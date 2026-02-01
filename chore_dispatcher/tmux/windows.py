from __future__ import annotations

import re

from chore_dispatcher.models.status import ChoreStatus
import subprocess

from chore_dispatcher.tmux.session import ensure_session, run_tmux, window_exists


_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def slugify(name: str, max_len: int = 30) -> str:
    slug = name.strip().lower().replace(" ", "-")
    slug = _SLUG_RE.sub("-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = "chore"
    return slug[:max_len]


def window_name(chore_id: int, role: str) -> str:
    return f"chore{chore_id}_{role}"


def create_window(session_name: str, chore_id: int, role: str, command: str | None = None) -> None:
    name = window_name(chore_id, role)
    args: list[str] = ["new-window", "-t", session_name, "-n", name]
    if command:
        args.append(command)
    try:
        run_tmux(args)
    except subprocess.CalledProcessError:
        ensure_session(session_name)
        run_tmux(args)


def create_named_window(session_name: str, name: str, command: str | None = None) -> None:
    if window_exists(session_name, name):
        return
    args: list[str] = ["new-window", "-t", session_name, "-n", name]
    if command:
        args.append(command)
    try:
        run_tmux(args)
    except subprocess.CalledProcessError:
        ensure_session(session_name)
        run_tmux(args)


def split_review_panes(session_name: str, window: str, right_cmd: str) -> None:
    run_tmux(["split-window", "-t", f"{session_name}:{window}", "-h", right_cmd])


def role_label(status: ChoreStatus) -> str:
    if status in {ChoreStatus.PLAN, ChoreStatus.PLAN_REVIEW, ChoreStatus.PLAN_READY}:
        return "Planner"
    return "Worker"
