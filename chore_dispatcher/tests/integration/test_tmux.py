import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.tmux.windows import layout_for_status, slugify, window_name


class TestTmuxHelpers(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(slugify("Hello World"), "hello-world")
        self.assertEqual(slugify("***"), "chore")

    def test_window_name(self) -> None:
        chore = Chore(id=42, name="Test Name")
        self.assertTrue(window_name(chore).startswith("chore-42-"))

    def test_layout_for_status(self) -> None:
        self.assertEqual(layout_for_status(ChoreStatus.PLAN), "single")
        self.assertEqual(layout_for_status(ChoreStatus.WORK_REVIEW), "review")


if __name__ == "__main__":
    unittest.main()
