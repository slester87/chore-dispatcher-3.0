from __future__ import annotations

from chore_dispatcher.models.chore import Chore
import shlex

from chore_dispatcher.prompts import build_role_prompt
from chore_dispatcher.tmux.session import attach_session, ensure_session, ensure_tmux_available, run_tmux, session_exists
from chore_dispatcher.tmux.windows import create_named_window, create_window, ensure_window_index, role_label, window_name
from chore_dispatcher.special import special_chore


def _role_env_value(role: str) -> str:
    if role.endswith("Reviewer"):
        return role.replace("Reviewer", "_REVIEWER").upper()
    return role.upper()


def _command_for_role(role: str, chore: Chore, kiro_command: str) -> str:
    prompt = build_role_prompt(chore)
    env_parts = [
        f"CHORE_ID={shlex.quote(str(chore.id))}",
        f"CHORE_NAME={shlex.quote(chore.name)}",
        f"CHORE_DESCRIPTION={shlex.quote(chore.description)}",
        f"CHORE_STATUS={shlex.quote(chore.status.value)}",
        f"CHORE_ROLE={shlex.quote(_role_env_value(role))}",
    ]
    return f"{' '.join(env_parts)} {kiro_command} {shlex.quote(prompt)}"


def dispatch_chore_window(session_name: str, chore: Chore, kiro_command: str) -> None:
    ensure_tmux_available()
    ensure_session(session_name)

    role = role_label(chore.status)
    cmd = _command_for_role(role, chore, kiro_command)
    create_window(session_name, chore.id, role, cmd)


def dispatch_bootstrap_planner(session_name: str, kiro_command: str) -> None:
    ensure_tmux_available()
    chore = special_chore()
    cmd = _command_for_role("Planner", chore, kiro_command)
    if session_exists(session_name):
        create_named_window(session_name, "planner", cmd)
    else:
        run_tmux(["new-session", "-d", "-s", session_name, "-n", "planner", cmd])
    ensure_window_index(session_name, "planner", 0)
    attach_session(session_name)


def dispatch_review_window(session_name: str, chore: Chore, kiro_command: str) -> None:
    ensure_tmux_available()
    ensure_session(session_name)
    role = role_label(chore.status)
    cmd = _command_for_role(role, chore, kiro_command)
    create_window(session_name, chore.id, role, cmd)


def teardown_window(session_name: str, chore: Chore) -> None:
    ensure_tmux_available()
    ensure_session(session_name)
    run_tmux(["kill-window", "-t", f"{session_name}:{window_name(chore.id, role_label(chore.status))}"])


def teardown_windows(session_name: str, chore: Chore, roles: list[str]) -> None:
    ensure_tmux_available()
    ensure_session(session_name)
    for role in roles:
        run_tmux(["kill-window", "-t", f"{session_name}:{window_name(chore.id, role)}"])
