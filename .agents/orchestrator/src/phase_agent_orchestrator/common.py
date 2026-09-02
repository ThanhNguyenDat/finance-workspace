"""Small, dependency-free helpers shared by the orchestration CLIs."""

from __future__ import annotations

import json
import os
import shutil
import socket
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, NoReturn


class CLIError(Exception):
    """An expected CLI error whose message belongs on stderr."""


def die(prefix: str, message: str) -> NoReturn:
    raise CLIError(f"{prefix}: {message}")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_after(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def json_text(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def read_json(path: Path, prefix: str, message: str | None = None) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        die(prefix, message or f"could not read JSON: {path}")
    raise AssertionError("unreachable")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.tmp.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json_text(value) + "\n")


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


def run_cli(main: Callable[[], int], prefix: str) -> NoReturn:
    import sys

    try:
        status = main()
    except CLIError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None
    raise SystemExit(status)
