import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus


class TestChore(unittest.TestCase):
    def test_advances_linearly(self) -> None:
        chore = Chore(id=1, name="Test")
        self.assertEqual(chore.status, ChoreStatus.PLAN)
        self.assertTrue(chore.advance_status())
        self.assertEqual(chore.status, ChoreStatus.PLAN_REVIEW)

    def test_terminal_state(self) -> None:
        chore = Chore(id=1, name="Test", status=ChoreStatus.WORK_DONE)
        self.assertFalse(chore.advance_status())
        self.assertTrue(chore.is_complete())

    def test_sub_chores_block_advancement(self) -> None:
        parent = Chore(id=1, name="Parent")
        child = Chore(id=2, name="Child")
        parent.add_sub_chore(child)
        self.assertFalse(parent.advance_status())
        child.status = ChoreStatus.WORK_DONE
        self.assertTrue(parent.advance_status())

    def test_next_chore_only_when_complete(self) -> None:
        a = Chore(id=1, name="A")
        b = Chore(id=2, name="B")
        a.set_next_chore(b)
        self.assertIsNone(a.get_next_chore())
        a.status = ChoreStatus.WORK_DONE
        self.assertIs(a.get_next_chore(), b)


if __name__ == "__main__":
    unittest.main()
