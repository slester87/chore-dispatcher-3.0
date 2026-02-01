from __future__ import annotations

import shutil
import subprocess
from typing import Iterable


class TmuxError(RuntimeError):
    pass


def ensure_tmux_available() -> None:
    if shutil.which("tmux") is None:
        raise TmuxError("tmux not found in PATH")


def session_exists(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ensure_session(session_name: str) -> None:
    if session_exists(session_name):
        return
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)


def run_tmux(args: Iterable[str]) -> None:
    subprocess.run(["tmux", *args], check=True)
