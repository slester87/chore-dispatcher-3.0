from __future__ import annotations

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus, next_status
from chore_dispatcher.workflow.errors import TransitionError
from chore_dispatcher.workflow.validator import PhaseValidator


class StateTransitionEngine:
    def __init__(self, validator: PhaseValidator | None = None) -> None:
        self._validator = validator or PhaseValidator()

    def validate_transition(self, from_status: ChoreStatus, to_status: ChoreStatus, chore: Chore) -> bool:
        expected = self._expected_next_status(chore)
        if expected != to_status:
            raise TransitionError(f"Invalid transition {from_status} -> {to_status}")
        return self._validator.validate_transition(from_status, to_status, chore)

    def execute_transition(self, chore: Chore, to_status: ChoreStatus) -> bool:
        self.validate_transition(chore.status, to_status, chore)
        chore.status = to_status
        return True

    def _expected_next_status(self, chore: Chore) -> ChoreStatus | None:
        if not chore.can_advance():
            return None
        return next_status(chore.status)
