import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.workflow.chain import activate_next_chore, handle_chain_completion, validate_chain_integrity


class TestChain(unittest.TestCase):
    def test_handle_chain_completion(self) -> None:
        a = Chore(id=1, name="A")
        b = Chore(id=2, name="B")
        a.set_next_chore(b)
        self.assertIsNone(handle_chain_completion(a))
        a.status = ChoreStatus.WORK_DONE
        self.assertIs(handle_chain_completion(a), b)

    def test_activate_next_chore(self) -> None:
        a = Chore(id=1, name="A")
        b = Chore(id=2, name="B")
        a.set_next_chore(b)
        self.assertFalse(activate_next_chore(a))
        a.status = ChoreStatus.WORK_DONE
        self.assertTrue(activate_next_chore(a))

    def test_validate_chain_integrity(self) -> None:
        a = Chore(id=1, name="A")
        b = Chore(id=2, name="B")
        c = Chore(id=3, name="C")
        a.set_next_chore(b)
        b.set_next_chore(c)
        c.set_next_chore(a)
        errors = validate_chain_integrity({1: a, 2: b, 3: c})
        self.assertEqual(len(errors), 1)
        self.assertIn("Circular chain detected", errors[0])


if __name__ == "__main__":
    unittest.main()
