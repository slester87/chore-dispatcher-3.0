from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Iterable

from chore_dispatcher.config import Config
from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.repo.integrity import dedupe_chore_payloads, enforce_archive_exclusivity

MANIFEST_NAME = "store_manifest.json"


def resolve_store_paths(config: Config) -> tuple[Path, Path]:
    root = Path(config.store_root)
    active = root / config.active_store_path
    archive = root / config.archive_store_path
    return active, archive


def _manifest_path(root: Path) -> Path:
    return root / MANIFEST_NAME


def serialize_chore(chore: Chore) -> dict:
    return {
        "id": chore.id,
        "name": chore.name,
        "description": chore.description,
        "status": chore.status.value,
        "next_chore_id": chore.next_chore.id if chore.next_chore else None,
        "progress_info": chore.progress_info,
        "review_info": chore.review_info,
        "parent_chore_id": chore.parent_chore_id,
        "sub_chore_ids": [sub.id for sub in chore.sub_chores],
    }


def deserialize_chore(payload: dict) -> Chore:
    return Chore(
        id=payload["id"],
        name=payload["name"],
        description=payload.get("description", ""),
        status=ChoreStatus(payload.get("status", ChoreStatus.PLAN.value)),
        next_chore=None,
        progress_info=payload.get("progress_info"),
        review_info=payload.get("review_info"),
        parent_chore_id=payload.get("parent_chore_id"),
        sub_chores=[],
    )


def load_chores(path: Path) -> dict[int, Chore]:
    if not path.exists():
        return {}

    chores: dict[int, Chore] = {}
    pending_links: dict[int, dict] = {}

    payloads: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            payloads.append(json.loads(line))

    payloads, _ = dedupe_chore_payloads(payloads)

    for payload in payloads:
        chore = deserialize_chore(payload)
        chores[chore.id] = chore
        pending_links[chore.id] = payload

    for chore_id, payload in pending_links.items():
        chore = chores[chore_id]

        next_id = payload.get("next_chore_id")
        if next_id is not None:
            chore.next_chore = chores.get(next_id)

        sub_ids = payload.get("sub_chore_ids") or []
        chore.sub_chores = [chores[sub_id] for sub_id in sub_ids if sub_id in chores]

    return chores


def _read_manifest(root: Path) -> dict | None:
    path = _manifest_path(root)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_manifest_paths(root: Path, manifest: dict) -> tuple[Path, Path]:
    active_rel = manifest.get("active")
    archive_rel = manifest.get("archive")
    if not active_rel or not archive_rel:
        raise ValueError("Manifest missing active/archive paths")
    return root / active_rel, root / archive_rel


def load_active_and_archive(active_path: Path, archive_path: Path) -> tuple[dict[int, Chore], dict[int, Chore]]:
    root = active_path.parent
    manifest = _read_manifest(root)
    if manifest is not None:
        try:
            active_path, archive_path = _resolve_manifest_paths(root, manifest)
        except ValueError:
            pass

    active = load_chores(active_path)
    archive = load_chores(archive_path)
    enforce_archive_exclusivity(active, archive)
    return active, archive


def _fsync_file(handle) -> None:
    handle.flush()
    os.fsync(handle.fileno())


def _write_jsonl(path: Path, chores: Iterable[Chore]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for chore in chores:
            fh.write(json.dumps(serialize_chore(chore)) + "\n")
        _fsync_file(fh)


def save_chores(path: Path, chores: Iterable[Chore]) -> None:
    _write_jsonl(path, chores)


def _next_version(manifest: dict | None) -> int:
    if manifest and isinstance(manifest.get("version"), int):
        return manifest["version"] + 1
    return int(time.time() * 1000)


def save_active_and_archive_atomic(active_path: Path, archive_path: Path, active: Iterable[Chore], archive: Iterable[Chore]) -> None:
    root = active_path.parent
    manifest = _read_manifest(root)
    version = _next_version(manifest)

    active_version = active_path.with_name(f"{active_path.stem}.v{version}{active_path.suffix}")
    archive_version = archive_path.with_name(f"{archive_path.stem}.v{version}{archive_path.suffix}")

    active_tmp = active_version.with_suffix(active_version.suffix + ".tmp")
    archive_tmp = archive_version.with_suffix(archive_version.suffix + ".tmp")

    _write_jsonl(active_tmp, active)
    _write_jsonl(archive_tmp, archive)

    active_tmp.replace(active_version)
    archive_tmp.replace(archive_version)

    manifest_payload = {
        "version": version,
        "active": str(active_version.relative_to(root)),
        "archive": str(archive_version.relative_to(root)),
    }

    manifest_path = _manifest_path(root)
    manifest_tmp = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_tmp.open("w", encoding="utf-8") as fh:
        json.dump(manifest_payload, fh)
        _fsync_file(fh)
    manifest_tmp.replace(manifest_path)
