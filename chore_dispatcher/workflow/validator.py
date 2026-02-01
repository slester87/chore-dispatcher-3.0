from __future__ import annotations

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.workflow.errors import ValidationError


class PhaseValidator:
    def validate_transition(self, from_status: ChoreStatus, to_status: ChoreStatus, chore: Chore) -> bool:
        if not self._validate_progress_info(chore.progress_info):
            raise ValidationError("Invalid progress_info")
        if not self._validate_review_info(chore.review_info):
            raise ValidationError("Invalid review_info")
        if to_status == ChoreStatus.WORK_DONE and not self._validate_work_quality(chore):
            raise ValidationError("Work quality requirements not met")
        return True

    def _validate_progress_info(self, progress_info: str | None) -> bool:
        if progress_info is None:
            return True
        length = len(progress_info.strip())
        return 2 <= length <= 200

    def _validate_review_info(self, review_info: str | None) -> bool:
        if review_info is None:
            return True
        length = len(review_info.strip())
        return 2 <= length <= 200

    def _validate_work_quality(self, chore: Chore) -> bool:
        # Placeholder: in later steps, wire actual compile/lint/test checks.
        return True
