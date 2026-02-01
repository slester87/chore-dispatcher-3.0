import tempfile
import unittest
from pathlib import Path

from chore_dispatcher.config import Config
from chore_dispatcher.repo.persistence import load_active_and_archive
from chore_dispatcher.repo.unit_of_work import FileUnitOfWork


class _IdGen:
    def __init__(self) -> None:
        self._next = 1

    def __call__(self) -> int:
        value = self._next
        self._next += 1
        return value


class TestFileUnitOfWork(unittest.TestCase):
    def test_commit_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(store_root=tmpdir, active_store_path="active.jsonl", archive_store_path="archive.jsonl")
            uow = FileUnitOfWork(config, _IdGen())
            uow.begin()
            repo = uow.repository()
            chore = repo.create("Test")
            uow.commit()

            active_path = Path(tmpdir) / "active.jsonl"
            archive_path = Path(tmpdir) / "archive.jsonl"
            active, archive = load_active_and_archive(active_path, archive_path)
            self.assertIn(chore.id, active)
            self.assertEqual(archive, {})

    def test_rollback_discards(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(store_root=tmpdir, active_store_path="active.jsonl", archive_store_path="archive.jsonl")
            uow = FileUnitOfWork(config, _IdGen())
            uow.begin()
            repo = uow.repository()
            repo.create("Test")
            uow.rollback()

            active_path = Path(tmpdir) / "active.jsonl"
            archive_path = Path(tmpdir) / "archive.jsonl"
            active, archive = load_active_and_archive(active_path, archive_path)
            self.assertEqual(active, {})
            self.assertEqual(archive, {})


if __name__ == "__main__":
    unittest.main()
