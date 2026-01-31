from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from chore_dispatcher.models.status import ChoreStatus, next_status


@dataclass
class Chore:
    id: int
    name: str
    description: str = ""
    status: ChoreStatus = ChoreStatus.PLAN
    next_chore: Optional["Chore"] = None
    progress_info: Optional[str] = None
    review_info: Optional[str] = None
    parent_chore_id: Optional[int] = None
    sub_chores: list["Chore"] = field(default_factory=list)

    def can_advance(self) -> bool:
        return all(chore.is_complete() for chore in self.sub_chores)

    def advance_status(self) -> bool:
        if not self.can_advance():
            return False

        next_state = next_status(self.status)
        if next_state is None:
            return False

        self.status = next_state
        return True

    def is_complete(self) -> bool:
        return self.status == ChoreStatus.WORK_DONE

    def set_next_chore(self, chore: "Chore") -> None:
        self.next_chore = chore

    def get_next_chore(self) -> Optional["Chore"]:
        if not self.is_complete():
            return None
        return self.next_chore

    def add_sub_chore(self, chore: "Chore") -> None:
        chore.parent_chore_id = self.id
        self.sub_chores.append(chore)

    def get_sub_chores(self) -> list["Chore"]:
        return list(self.sub_chores)
