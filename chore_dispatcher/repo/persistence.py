from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from chore_dispatcher.config import Config
from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus


def resolve_store_paths(config: Config) -> tuple[Path, Path]:
    root = Path(config.store_root)
    active = root / config.active_store_path
    archive = root / config.archive_store_path
    return active, archive


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

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
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


def save_chores(path: Path, chores: Iterable[Chore]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for chore in chores:
            fh.write(json.dumps(serialize_chore(chore)) + "\n")
