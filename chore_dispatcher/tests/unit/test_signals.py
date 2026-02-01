import tempfile
import unittest
from pathlib import Path

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.signals.signals import SignalWatcher


class TestSignals(unittest.TestCase):
    def test_check_triggers_callbacks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            chore = Chore(id=1, name="Test")
            signal_dir = Path(tmpdir)
            watcher = SignalWatcher(str(signal_dir), poll_interval=0.01)

            complete_path = signal_dir / "chore_1_complete"
            exit_path = signal_dir / "chore_1_exit"
            complete_path.write_text("done")
            exit_path.write_text("done")

            events = []

            def on_complete(c: Chore) -> None:
                events.append("complete")

            def on_exit(c: Chore) -> None:
                events.append("exit")

            watcher.check(chore, on_complete, on_exit)

            self.assertEqual(set(events), {"complete", "exit"})
            self.assertFalse(complete_path.exists())
            self.assertFalse(exit_path.exists())


if __name__ == "__main__":
    unittest.main()
