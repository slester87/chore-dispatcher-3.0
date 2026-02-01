from __future__ import annotations

import re
from typing import Iterable

from chore_dispatcher.models.chore import Chore
from chore_dispatcher.models.status import ChoreStatus
from chore_dispatcher.tmux.session import run_tmux


_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def slugify(name: str, max_len: int = 30) -> str:
    slug = name.strip().lower().replace(" ", "-")
    slug = _SLUG_RE.sub("-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = "chore"
    return slug[:max_len]


def window_name(chore: Chore) -> str:
    return f"chore-{chore.id}-{slugify(chore.name)}"


def create_window(session_name: str, chore: Chore, command: str | None = None) -> None:
    name = window_name(chore)
    args: list[str] = ["new-window", "-t", session_name, "-n", name]
    if command:
        args.append(command)
    run_tmux(args)


def split_review_panes(session_name: str, window: str, left_cmd: str, right_cmd: str) -> None:
    run_tmux(["split-window", "-t", f"{session_name}:{window}", "-h", left_cmd])
    run_tmux(["split-window", "-t", f"{session_name}:{window}", "-h", right_cmd])


def layout_for_status(status: ChoreStatus) -> str:
    if status in {ChoreStatus.PLAN_REVIEW, ChoreStatus.WORK_REVIEW}:
        return "review"
    return "single"
