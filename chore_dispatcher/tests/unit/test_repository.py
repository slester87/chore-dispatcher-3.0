import unittest

from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.repo.repository import ChoreRepository


class _IdGen:
    def __init__(self) -> None:
        self._next = 1

    def __call__(self) -> int:
        value = self._next
        self._next += 1
        return value


class TestRepository(unittest.TestCase):
    def test_crud(self) -> None:
        store = {}
        repo = ChoreRepository(store, _IdGen())
        chore = repo.create("Test", "Desc")
        self.assertEqual(repo.read(chore.id), chore)

        updated = repo.update(chore.id, name="New")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "New")

        self.assertTrue(repo.delete(chore.id))
        self.assertIsNone(repo.read(chore.id))

    def test_find_by_status(self) -> None:
        store = {}
        repo = ChoreRepository(store, _IdGen())
        repo.create("A")
        chore_b = repo.create("B")
        repo.update(chore_b.id, status=ChoreStatus.WORK)
        matches = repo.find_by_status(ChoreStatus.WORK)
        self.assertEqual([chore_b], matches)

    def test_hierarchy_helpers(self) -> None:
        store = {}
        repo = ChoreRepository(store, _IdGen())
        parent = repo.create("Parent")
        child = repo.create_sub_chore(parent.id, "Child")
        self.assertIsNotNone(child)
        self.assertEqual(child.parent_chore_id, parent.id)
        self.assertEqual(repo.get_sub_chores(parent.id), [child])
        self.assertEqual(repo.get_parent_chore(child.id), parent)
        self.assertEqual(repo.find_root_chores(), [parent])


if __name__ == "__main__":
    unittest.main()
