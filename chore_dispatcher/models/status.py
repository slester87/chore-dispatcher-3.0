from __future__ import annotations

from enum import Enum


class ChoreStatus(str, Enum):
    PLAN = "PLAN"
    PLAN_REVIEW = "PLAN_REVIEW"
    PLAN_READY = "PLAN_READY"
    WORK = "WORK"
    WORK_REVIEW = "WORK_REVIEW"
    WORK_DONE = "WORK_DONE"


ORDERED_STATUSES = [
    ChoreStatus.PLAN,
    ChoreStatus.PLAN_REVIEW,
    ChoreStatus.PLAN_READY,
    ChoreStatus.WORK,
    ChoreStatus.WORK_REVIEW,
    ChoreStatus.WORK_DONE,
]


def next_status(status: ChoreStatus) -> ChoreStatus | None:
    try:
        idx = ORDERED_STATUSES.index(status)
    except ValueError:
        return None
    if idx + 1 >= len(ORDERED_STATUSES):
        return None
    return ORDERED_STATUSES[idx + 1]
