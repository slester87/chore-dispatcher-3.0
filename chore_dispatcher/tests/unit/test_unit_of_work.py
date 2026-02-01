import unittest

from chore_dispatcher.repo.unit_of_work import InMemoryUnitOfWork


class _IdGen:
    def __init__(self) -> None:
        self._next = 1

    def __call__(self) -> int:
        value = self._next
        self._next += 1
        return value


class TestUnitOfWork(unittest.TestCase):
    def test_commit_applies_changes(self) -> None:
        store = {}
        uow = InMemoryUnitOfWork(store, _IdGen())
        uow.begin()
        repo = uow.repository()
        chore = repo.create("Test")
        self.assertEqual(len(store), 0)
        uow.commit()
        self.assertIn(chore.id, store)

    def test_rollback_discards_changes(self) -> None:
        store = {}
        uow = InMemoryUnitOfWork(store, _IdGen())
        uow.begin()
        repo = uow.repository()
        repo.create("Test")
        uow.rollback()
        self.assertEqual(len(store), 0)

    def test_isolation_between_uows(self) -> None:
        store = {}
        uow1 = InMemoryUnitOfWork(store, _IdGen())
        uow1.begin()
        repo1 = uow1.repository()
        chore = repo1.create("Test")

        uow2 = InMemoryUnitOfWork(store, _IdGen())
        uow2.begin()
        repo2 = uow2.repository()
        self.assertIsNone(repo2.read(chore.id))

        uow1.commit()
        uow2.rollback()
        uow2.begin()
        repo2 = uow2.repository()
        self.assertIsNotNone(repo2.read(chore.id))


if __name__ == "__main__":
    unittest.main()
