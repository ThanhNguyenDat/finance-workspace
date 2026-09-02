"""PID liveness checks used by orchestration locks."""

from __future__ import annotations

import os
import socket
from pathlib import Path


def pid_is_alive(pid: int | str, hostname: str) -> bool:
    """Match the shell kill -0 contract, including EPERM as unconfirmed."""

    if hostname != socket.gethostname():
        return False
    try:
        numeric_pid = int(pid)
    except (TypeError, ValueError):
        return False
    try:
        os.kill(numeric_pid, 0)
    except (ProcessLookupError, PermissionError, ValueError):
        return False
    return True


def lock_pid_is_live(path: Path) -> bool:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return value.isdigit() and pid_is_alive(int(value), socket.gethostname())
