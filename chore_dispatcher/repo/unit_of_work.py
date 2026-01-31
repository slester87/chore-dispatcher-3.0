from __future__ import annotations

import copy
from typing import Callable

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.repo.repository import ChoreRepository


class InMemoryUnitOfWork:
    def __init__(self, store: dict[int, Chore], id_generator: Callable[[], int]) -> None:
        self._store = store
        self._id_generator = id_generator
        self._working_copy: dict[int, Chore] | None = None

    def begin(self) -> None:
        self._working_copy = copy.deepcopy(self._store)

    def repository(self) -> ChoreRepository:
        if self._working_copy is None:
            raise RuntimeError("UnitOfWork has not been started")
        return ChoreRepository(self._working_copy, self._id_generator)

    def commit(self) -> None:
        if self._working_copy is None:
            raise RuntimeError("UnitOfWork has not been started")
        self._store.clear()
        self._store.update(self._working_copy)
        self._working_copy = None

    def rollback(self) -> None:
        if self._working_copy is None:
            raise RuntimeError("UnitOfWork has not been started")
        self._working_copy = None
