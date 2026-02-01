from __future__ import annotations

from chore_dispatcher.models.chore import Chore


def validate_chain_integrity(chores: dict[int, Chore]) -> list[str]:
    errors: list[str] = []
    visited: set[int] = set()

    for chore in chores.values():
        if chore.id in visited:
            continue

        path: dict[int, int] = {}
        current = chore
        step = 0
        while current is not None:
            if current.id in path:
                cycle = list(path.keys())[path[current.id]:]
                errors.append(f"Circular chain detected: {cycle}")
                break
            if current.id in visited:
                break
            path[current.id] = step
            step += 1
            current = current.next_chore

        visited.update(path.keys())

    return errors


def handle_chain_completion(completed_chore: Chore) -> Chore | None:
    if not completed_chore.is_complete():
        return None
    return completed_chore.get_next_chore()


def activate_next_chore(completed_chore: Chore) -> bool:
    return handle_chain_completion(completed_chore) is not None
