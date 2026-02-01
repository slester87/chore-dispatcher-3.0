from __future__ import annotations

from collections import Counter
from typing import Iterable

from chore_dispatcher.models.chore import Chore


def find_duplicate_ids(chores: Iterable[Chore]) -> list[int]:
    ids = [chore.id for chore in chores]
    return [chore_id for chore_id, count in Counter(ids).items() if count > 1]


def find_orphan_subchores(chores: dict[int, Chore]) -> list[Chore]:
    orphans = []
    for chore in chores.values():
        if chore.parent_chore_id is not None and chore.parent_chore_id not in chores:
            orphans.append(chore)
    return orphans


def find_chain_cycles(chores: dict[int, Chore]) -> list[list[int]]:
    cycles: list[list[int]] = []
    visited: set[int] = set()

    for chore in chores.values():
        if chore.id in visited:
            continue

        path: dict[int, int] = {}
        current = chore
        step = 0
        while current is not None:
            if current.id in path:
                cycle_start = path[current.id]
                cycle_ids = list(path.keys())[cycle_start:]
                cycles.append(cycle_ids)
                break
            if current.id in visited:
                break

            path[current.id] = step
            step += 1
            current = current.next_chore

        visited.update(path.keys())

    return cycles


def dedupe_chore_payloads(payloads: list[dict]) -> tuple[list[dict], int]:
    seen: set[int] = set()
    deduped: list[dict] = []
    removed = 0

    for payload in payloads:
        chore_id = payload.get("id")
        if chore_id in seen:
            removed += 1
            continue
        seen.add(chore_id)
        deduped.append(payload)

    return deduped, removed


def enforce_archive_exclusivity(active: dict[int, Chore], archive: dict[int, Chore]) -> list[int]:
    overlapping = sorted(set(active.keys()) & set(archive.keys()))
    for chore_id in overlapping:
        active.pop(chore_id, None)
    return overlapping
