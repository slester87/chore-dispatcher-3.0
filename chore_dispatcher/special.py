from __future__ import annotations

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus

SPECIAL_CHORE_ID = 0
SPECIAL_CHORE_NAME = "Chore Creation"

SPECIAL_CHORE_DESCRIPTION = (
    "This is the chore-creation chore. Its purpose is to help you frame a new chore.\n\n"
    "Start with the problem, not the solution. Before creating a new chore, answer these in order:\n"
    "1) What must never happen?\n"
    "2) What can go wrong?\n"
    "3) What conditions define correctness?\n\n"
    "Once you have enough detail to hand off, ask the user for permission to create the chore.\n"
    "Only after explicit approval should you call create().\n"
)


def special_chore() -> Chore:
    return Chore(
        id=SPECIAL_CHORE_ID,
        name=SPECIAL_CHORE_NAME,
        description=SPECIAL_CHORE_DESCRIPTION,
        status=ChoreStatus.PLAN,
    )
