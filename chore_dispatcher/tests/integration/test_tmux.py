import unittest

from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.tmux.windows import role_label, slugify, window_name


class TestTmuxHelpers(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(slugify("Hello World"), "hello-world")
        self.assertEqual(slugify("***"), "chore")

    def test_window_name(self) -> None:
        self.assertEqual(window_name(42, "Planner"), "chore42_Planner")

    def test_role_label(self) -> None:
        self.assertEqual(role_label(ChoreStatus.PLAN), "Planner")
        self.assertEqual(role_label(ChoreStatus.PLAN_REVIEW), "PlanReviewer")
        self.assertEqual(role_label(ChoreStatus.WORK), "Worker")
        self.assertEqual(role_label(ChoreStatus.WORK_REVIEW), "WorkReviewer")


if __name__ == "__main__":
    unittest.main()
