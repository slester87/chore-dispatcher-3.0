from __future__ import annotations

import threading
import time

EPOCH_MS = 1704067200000  # Jan 1, 2024 UTC
NODE_ID_BITS = 10
SEQUENCE_BITS = 12

MAX_NODE_ID = (1 << NODE_ID_BITS) - 1
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

NODE_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_SHIFT = SEQUENCE_BITS + NODE_ID_BITS


class Snowflake:
    def __init__(self, node_id: int) -> None:
        if not (0 <= node_id <= MAX_NODE_ID):
            raise ValueError(f"node_id must be between 0 and {MAX_NODE_ID}")
        self._node_id = node_id
        self._lock = threading.Lock()
        self._last_ts = -1
        self._sequence = 0

    def next_id(self) -> int:
        with self._lock:
            ts = self._now_ms()
            if ts < self._last_ts:
                raise RuntimeError("Clock moved backwards")

            if ts == self._last_ts:
                self._sequence = (self._sequence + 1) & MAX_SEQUENCE
                if self._sequence == 0:
                    ts = self._wait_next_ms(ts)
            else:
                self._sequence = 0

            self._last_ts = ts
            return ((ts - EPOCH_MS) << TIMESTAMP_SHIFT) | (self._node_id << NODE_ID_SHIFT) | self._sequence

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, last_ts: int) -> int:
        ts = self._now_ms()
        while ts <= last_ts:
            time.sleep(0.0001)
            ts = self._now_ms()
        return ts
