import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.repo.integrity import (
    dedupe_chore_payloads,
    enforce_archive_exclusivity,
    find_chain_cycles,
    find_duplicate_ids,
    find_orphan_subchores,
)


class TestIntegrity(unittest.TestCase):
    def test_find_duplicate_ids(self) -> None:
        chores = [Chore(id=1, name="A"), Chore(id=1, name="B"), Chore(id=2, name="C")]
        self.assertEqual(find_duplicate_ids(chores), [1])

    def test_find_orphan_subchores(self) -> None:
        orphan = Chore(id=2, name="Orphan", parent_chore_id=999)
        self.assertEqual(find_orphan_subchores({2: orphan}), [orphan])

    def test_find_chain_cycles(self) -> None:
        a = Chore(id=1, name="A")
        b = Chore(id=2, name="B")
        c = Chore(id=3, name="C")
        a.set_next_chore(b)
        b.set_next_chore(c)
        c.set_next_chore(a)
        cycles = find_chain_cycles({1: a, 2: b, 3: c})
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {1, 2, 3})

    def test_dedupe_chore_payloads(self) -> None:
        payloads = [
            {"id": 1, "name": "A"},
            {"id": 1, "name": "B"},
            {"id": 2, "name": "C"},
        ]
        deduped, removed = dedupe_chore_payloads(payloads)
        self.assertEqual(removed, 1)
        self.assertEqual([payload["id"] for payload in deduped], [1, 2])

    def test_enforce_archive_exclusivity(self) -> None:
        active = {1: Chore(id=1, name="Active")}
        archive = {1: Chore(id=1, name="Archived")}
        removed = enforce_archive_exclusivity(active, archive)
        self.assertEqual(removed, [1])
        self.assertNotIn(1, active)


if __name__ == "__main__":
    unittest.main()
