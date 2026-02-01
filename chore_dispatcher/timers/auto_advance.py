from __future__ import annotations

import threading
from collections.abc import Callable

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus


class AutoAdvanceConfig:
    def __init__(self) -> None:
        self.delays = {
            ChoreStatus.PLAN: 5,
            ChoreStatus.PLAN_REVIEW: 3,
            ChoreStatus.WORK: 10,
            ChoreStatus.WORK_REVIEW: 5,
        }


class AutoAdvanceTimer:
    def __init__(self, config: AutoAdvanceConfig | None = None) -> None:
        self._config = config or AutoAdvanceConfig()
        self._lock = threading.RLock()
        self._timers: dict[int, threading.Timer] = {}

    def schedule(self, chore: Chore, callback: Callable[[Chore], None]) -> None:
        delay = self._config.delays.get(chore.status)
        if delay is None:
            return

        with self._lock:
            self.cancel(chore.id)
            timer = threading.Timer(delay, self._fire, args=(chore, callback))
            self._timers[chore.id] = timer
            timer.start()

    def cancel(self, chore_id: int) -> None:
        with self._lock:
            timer = self._timers.pop(chore_id, None)
            if timer is not None:
                timer.cancel()

    def _fire(self, chore: Chore, callback: Callable[[Chore], None]) -> None:
        with self._lock:
            self._timers.pop(chore.id, None)
        callback(chore)
