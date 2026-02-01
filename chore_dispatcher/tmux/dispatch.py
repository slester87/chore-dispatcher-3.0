from __future__ import annotations

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.tmux.session import ensure_session, ensure_tmux_available
from chore_dispatcher.tmux.windows import create_window, layout_for_status, split_review_panes, window_name


def role_for_status(status: ChoreStatus) -> str:
    if status == ChoreStatus.PLAN:
        return "planner"
    if status == ChoreStatus.PLAN_REVIEW:
        return "plan_reviewer"
    if status == ChoreStatus.WORK:
        return "worker"
    if status == ChoreStatus.WORK_REVIEW:
        return "work_reviewer"
    return "worker"


def dispatch_chore_window(session_name: str, chore: Chore) -> None:
    ensure_tmux_available()
    ensure_session(session_name)

    role = role_for_status(chore.status)
    cmd = f"echo {role} for chore {chore.id}; exec $SHELL"
    create_window(session_name, chore, cmd)

    if layout_for_status(chore.status) == "review":
        window = window_name(chore)
        split_review_panes(session_name, window, cmd, cmd)
