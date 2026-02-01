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


def ensure_window_index(session_name: str, name: str, index: int) -> None:
    result = subprocess.run(
        ["tmux", "list-windows", "-t", session_name, "-F", "#{window_index}:#{window_name}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return
    window_indices: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if ":" not in line:
            continue
        raw_index, raw_name = line.split(":", 1)
        if not raw_index.isdigit():
            continue
        window_indices[raw_name.strip()] = int(raw_index)
    current_index = window_indices.get(name)
    if current_index is None or current_index == index:
        return
    if index in window_indices.values():
        run_tmux(["swap-window", "-s", f"{session_name}:{name}", "-t", f"{session_name}:{index}"])
        return
    run_tmux(["move-window", "-s", f"{session_name}:{name}", "-t", f"{session_name}:{index}"])


def role_label(status: ChoreStatus) -> str:
    if status == ChoreStatus.PLAN:
        return "Planner"
    if status == ChoreStatus.PLAN_REVIEW:
        return "PlanReviewer"
    if status == ChoreStatus.WORK:
        return "Worker"
    if status == ChoreStatus.WORK_REVIEW:
        return "WorkReviewer"
    if status == ChoreStatus.PLAN_READY:
        return "Planner"
    return "Worker"
