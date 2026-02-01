from __future__ import annotations

import shutil
import subprocess
from typing import Iterable
import os


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


def is_inside_tmux() -> bool:
    return bool(os.environ.get("TMUX"))


def attach_session(session_name: str) -> None:
    if is_inside_tmux():
        return
    subprocess.Popen(["tmux", "attach-session", "-t", session_name])


def window_exists(session_name: str, window_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "list-windows", "-t", session_name, "-F", "#{window_name}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return window_name in names
