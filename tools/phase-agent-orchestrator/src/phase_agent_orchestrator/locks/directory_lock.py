"""PID directory lock used by the standalone state helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..io import die
from .pid_liveness import lock_pid_is_live


class PidDirectoryLock:
    """The mkdir/pid lock used by the two standalone state helpers."""

    def __init__(self, directory: Path, prefix: str) -> None:
        self.directory = directory
        self.pid_file = directory / "pid"
        self.prefix = prefix
        self.owned = False

    def acquire(self) -> None:
        self.directory.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.directory.mkdir()
        except FileExistsError:
            if lock_pid_is_live(self.pid_file):
                die(self.prefix, f"state mutation is already locked by pid {self._owner_pid()}")
            shutil.rmtree(self.directory, ignore_errors=True)
            try:
                self.directory.mkdir()
            except FileExistsError:
                die(self.prefix, "could not acquire state mutation lock")
        self.pid_file.write_text(f"{os.getpid()}\n", encoding="utf-8")
        self.owned = True

    def _owner_pid(self) -> str:
        try:
            return self.pid_file.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    def release(self) -> None:
        if not self.owned:
            return
        try:
            if self._owner_pid() == str(os.getpid()):
                shutil.rmtree(self.directory)
        except FileNotFoundError:
            pass
        self.owned = False

    def __enter__(self) -> "PidDirectoryLock":
        self.acquire()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.release()
