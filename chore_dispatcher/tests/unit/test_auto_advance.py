import time
import unittest

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.timers.auto_advance import AutoAdvanceConfig, AutoAdvanceTimer


class TestAutoAdvance(unittest.TestCase):
    def test_schedule_and_cancel(self) -> None:
        chore = Chore(id=1, name="Test", status=ChoreStatus.PLAN)
        config = AutoAdvanceConfig()
        config.delays = {ChoreStatus.PLAN: 0.01}
        timer = AutoAdvanceTimer(config)

        fired = []

        def callback(ch: Chore) -> None:
            fired.append(ch.id)

        timer.schedule(chore, callback)
        timer.cancel(chore.id)
        time.sleep(0.02)
        self.assertEqual(fired, [])

    def test_schedule_fires(self) -> None:
        chore = Chore(id=2, name="Test", status=ChoreStatus.WORK)
        config = AutoAdvanceConfig()
        config.delays = {ChoreStatus.WORK: 0.01}
        timer = AutoAdvanceTimer(config)

        fired = []

        def callback(ch: Chore) -> None:
            fired.append(ch.id)

        timer.schedule(chore, callback)
        time.sleep(0.02)
        self.assertEqual(fired, [2])


if __name__ == "__main__":
    unittest.main()
