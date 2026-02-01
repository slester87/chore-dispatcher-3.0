from __future__ import annotations

from typing import Callable, Optional

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus


class ChoreRepository:
    def __init__(self, store: dict[int, Chore], id_generator: Callable[[], int]) -> None:
        self._store = store
        self._id_generator = id_generator

    def create(self, name: str, description: str = "") -> Chore:
        chore_id = self._id_generator()
        chore = Chore(id=chore_id, name=name, description=description)
        self._store[chore_id] = chore
        return chore

    def read(self, chore_id: int) -> Optional[Chore]:
        return self._store.get(chore_id)

    def update(self, chore_id: int, **kwargs) -> Optional[Chore]:
        chore = self._store.get(chore_id)
        if chore is None:
            return None

        for key, value in kwargs.items():
            if not hasattr(chore, key):
                raise ValueError(f"Unknown field: {key}")
            if key == "status" and isinstance(value, str):
                value = ChoreStatus(value)
            setattr(chore, key, value)
        return chore

    def delete(self, chore_id: int) -> bool:
        return self._store.pop(chore_id, None) is not None

    def list_all(self) -> list[Chore]:
        return list(self._store.values())

    def find_by_status(self, status: ChoreStatus) -> list[Chore]:
        return [chore for chore in self._store.values() if chore.status == status]

    def create_sub_chore(self, parent_id: int, name: str, description: str = "") -> Optional[Chore]:
        parent = self._store.get(parent_id)
        if parent is None:
            return None

        chore_id = self._id_generator()
        child = Chore(id=chore_id, name=name, description=description)
        parent.add_sub_chore(child)
        self._store[chore_id] = child
        return child

    def get_sub_chores(self, parent_id: int) -> list[Chore]:
        parent = self._store.get(parent_id)
        if parent is None:
            return []
        return parent.get_sub_chores()

    def get_parent_chore(self, chore_id: int) -> Optional[Chore]:
        chore = self._store.get(chore_id)
        if chore is None or chore.parent_chore_id is None:
            return None
        return self._store.get(chore.parent_chore_id)

    def find_root_chores(self) -> list[Chore]:
        return [chore for chore in self._store.values() if chore.parent_chore_id is None]
