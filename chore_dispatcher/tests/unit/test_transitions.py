import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.workflow.errors import TransitionError
from chore_dispatcher.workflow.transitions import StateTransitionEngine


class TestTransitions(unittest.TestCase):
    def test_valid_transition(self) -> None:
        chore = Chore(id=1, name="Test")
        engine = StateTransitionEngine()
        self.assertTrue(engine.execute_transition(chore, ChoreStatus.PLAN_REVIEW))
        self.assertEqual(chore.status, ChoreStatus.PLAN_REVIEW)

    def test_invalid_transition(self) -> None:
        chore = Chore(id=1, name="Test")
        engine = StateTransitionEngine()
        with self.assertRaises(TransitionError):
            engine.execute_transition(chore, ChoreStatus.WORK)

    def test_blocked_by_subchores(self) -> None:
        parent = Chore(id=1, name="Parent")
        child = Chore(id=2, name="Child")
        parent.add_sub_chore(child)
        engine = StateTransitionEngine()
        with self.assertRaises(TransitionError):
            engine.execute_transition(parent, ChoreStatus.PLAN_REVIEW)


if __name__ == "__main__":
    unittest.main()
