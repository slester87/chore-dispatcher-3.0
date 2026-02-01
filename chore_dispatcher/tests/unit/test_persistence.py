import tempfile
import unittest
from pathlib import Path

from chore_dispatcher.config import Config
from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.repo.persistence import (
    load_active_and_archive,
    load_chores,
    resolve_store_paths,
    save_chores,
)


class TestPersistence(unittest.TestCase):
    def test_resolve_store_paths(self) -> None:
        config = Config(store_root="/tmp/chores", active_store_path="active.jsonl", archive_store_path="archive.jsonl")
        active, archive = resolve_store_paths(config)
        self.assertEqual(active, Path("/tmp/chores") / "active.jsonl")
        self.assertEqual(archive, Path("/tmp/chores") / "archive.jsonl")

    def test_round_trip_and_linking(self) -> None:
        parent = Chore(id=1, name="Parent")
        child = Chore(id=2, name="Child", status=ChoreStatus.WORK)
        parent.add_sub_chore(child)
        parent.set_next_chore(child)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "active.jsonl"
            save_chores(path, [parent, child])

            loaded = load_chores(path)
            self.assertIn(1, loaded)
            self.assertIn(2, loaded)

            loaded_parent = loaded[1]
            loaded_child = loaded[2]

            self.assertEqual(loaded_parent.name, "Parent")
            self.assertEqual(loaded_child.status, ChoreStatus.WORK)
            self.assertEqual(loaded_parent.get_sub_chores(), [loaded_child])
            self.assertIs(loaded_parent.get_next_chore(), loaded_child)
            self.assertEqual(loaded_child.parent_chore_id, loaded_parent.id)

    def test_active_archive_exclusivity(self) -> None:
        active = Chore(id=1, name="Active")
        archive = Chore(id=1, name="Archived", status=ChoreStatus.WORK_DONE)

        with tempfile.TemporaryDirectory() as tmpdir:
            active_path = Path(tmpdir) / "active.jsonl"
            archive_path = Path(tmpdir) / "archive.jsonl"
            save_chores(active_path, [active])
            save_chores(archive_path, [archive])

            loaded_active, loaded_archive = load_active_and_archive(active_path, archive_path)
            self.assertNotIn(1, loaded_active)
            self.assertIn(1, loaded_archive)


if __name__ == "__main__":
    unittest.main()
