from __future__ import annotations

import copy
from pathlib import Path
from typing import Callable

from chore_dispatcher.config import Config
from chore_dispatcher.models.chore import Chore
from chore_dispatcher.repo.persistence import load_active_and_archive, resolve_store_paths, save_chores_atomic
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


class FileUnitOfWork:
    def __init__(self, config: Config, id_generator: Callable[[], int]) -> None:
        self._config = config
        self._id_generator = id_generator
        self._active_path, self._archive_path = resolve_store_paths(config)
        self._active: dict[int, Chore] | None = None
        self._archive: dict[int, Chore] | None = None

    def begin(self) -> None:
        active, archive = load_active_and_archive(self._active_path, self._archive_path)
        self._active = copy.deepcopy(active)
        self._archive = copy.deepcopy(archive)

    def repository(self) -> ChoreRepository:
        if self._active is None:
            raise RuntimeError("UnitOfWork has not been started")
        return ChoreRepository(self._active, self._id_generator)

    @property
    def archive_store(self) -> dict[int, Chore]:
        if self._archive is None:
            raise RuntimeError("UnitOfWork has not been started")
        return self._archive

    def commit(self) -> None:
        if self._active is None or self._archive is None:
            raise RuntimeError("UnitOfWork has not been started")
        save_chores_atomic(self._active_path, self._active.values())
        save_chores_atomic(self._archive_path, self._archive.values())
        self._active = None
        self._archive = None

    def rollback(self) -> None:
        if self._active is None or self._archive is None:
            raise RuntimeError("UnitOfWork has not been started")
        self._active = None
        self._archive = None
