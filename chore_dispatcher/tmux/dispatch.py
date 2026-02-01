from __future__ import annotations

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.tmux.session import ensure_session, ensure_tmux_available, run_tmux
from chore_dispatcher.tmux.windows import create_window, role_label, split_review_panes, window_name


def _command_for_role(role: str, chore: Chore) -> str:
    return f"echo {role} for chore {chore.id}; exec $SHELL"


def dispatch_chore_window(session_name: str, chore: Chore) -> None:
    ensure_tmux_available()
    ensure_session(session_name)

    role = role_label(chore.status)
    cmd = _command_for_role(role, chore)
    create_window(session_name, chore.id, role, cmd)


def add_review_pane(session_name: str, chore: Chore) -> None:
    ensure_tmux_available()
    ensure_session(session_name)
    window = window_name(chore.id, role_label(chore.status))
    reviewer_cmd = _command_for_role(role_label(chore.status), chore)
    split_review_panes(session_name, window, reviewer_cmd)


def teardown_window(session_name: str, chore: Chore) -> None:
    ensure_tmux_available()
    ensure_session(session_name)
    run_tmux(["kill-window", "-t", f"{session_name}:{window_name(chore.id, role_label(chore.status))}"])
