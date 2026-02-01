from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from chore_dispatcher.models.chore import Chore


class SignalWatcher:
    def __init__(self, signal_dir: str, poll_interval: float = 1.0) -> None:
        self._signal_dir = Path(signal_dir)
        self._poll_interval = poll_interval

    def _signal_path(self, chore_id: int, signal_type: str) -> Path:
        return self._signal_dir / f"chore_{chore_id}_{signal_type}"

    def check(self, chore: Chore, on_complete: Callable[[Chore], None], on_exit: Callable[[Chore], None]) -> None:
        complete_path = self._signal_path(chore.id, "complete")
        exit_path = self._signal_path(chore.id, "exit")

        if complete_path.exists():
            complete_path.unlink(missing_ok=True)
            on_complete(chore)

        if exit_path.exists():
            exit_path.unlink(missing_ok=True)
            on_exit(chore)

    def watch(self, chore: Chore, on_complete: Callable[[Chore], None], on_exit: Callable[[Chore], None]) -> None:
        while True:
            self.check(chore, on_complete, on_exit)
            time.sleep(self._poll_interval)
