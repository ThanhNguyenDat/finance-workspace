"""Change and repository locks for OPS transactions."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ..core.io import CLIError, atomic_write_json, die, json_text, utc_now
from .pid_liveness import pid_is_alive

PREFIX = "ops-runtime"
SAFE_CHANGE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class _ReturnStatus(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


def root_dir() -> Path:
    return Path(os.environ.get("OPS_ROOT", Path(__file__).resolve().parents[5]))


def ops_dir() -> Path:
    return root_dir() / ".ops"


def changes_dir() -> Path:
    return ops_dir() / "changes"


def change_dir(change: str) -> Path:
    if not SAFE_CHANGE.fullmatch(change):
        die(PREFIX, f"invalid change name: {change}")
    return changes_dir() / change


def repo_locks_dir() -> Path:
    return ops_dir() / "runtime/repo-locks"


def _read_json(path: Path, tolerate_failure: bool = False) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except OSError, json.JSONDecodeError, UnicodeDecodeError:
        if tolerate_failure:
            return None
        die(PREFIX, f"could not read JSON: {path}")
    raise AssertionError("unreachable")


def canonical_repo(repository: str) -> str:
    if not repository:
        die(PREFIX, "repository path is required")
    result = subprocess.run(
        ["git", "-C", repository, "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        die(PREFIX, f"not a Git worktree: {repository}")
    result = subprocess.run(
        ["git", "-C", repository, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        die(PREFIX, f"cannot resolve Git worktree: {repository}")
    return str(Path(result.stdout.strip()).resolve())


def repo_lock_dir(repository: str) -> Path:
    key = hashlib.sha256(repository.encode()).hexdigest()
    return repo_locks_dir() / key


def lock_anchor_pid() -> str:
    return os.environ.get("CLAUDE_PID") or os.environ.get("CODEX_PID") or ""


def phase_attempt_lease_is_dead(change_path: Path) -> bool:
    pid_file = change_path / "runtime/.phase-attempt-lock/pid"
    if not pid_file.is_file():
        return False
    try:
        value = pid_file.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return value.isdigit() and not pid_is_alive(int(value), socket.gethostname())


def owner_is_live(owner: Path, change_path: Path | None = None) -> bool:
    if not owner.is_file():
        return False
    value = _read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict):
        return True
    pid, hostname = value.get("pid"), value.get("hostname")
    if isinstance(pid, str) and pid.isdigit() and hostname == socket.gethostname():
        if not pid_is_alive(int(pid), hostname):
            return False
        recorded_change = value.get("change")
        if isinstance(recorded_change, str) and recorded_change:
            try:
                change_path = change_dir(recorded_change)
            except CLIError:
                # An unverifiable owner must remain live so lock recovery fails closed.
                change_path = None
        if change_path is not None and phase_attempt_lease_is_dead(change_path):
            return False
        return True
    return True


def release_repo_locks(change: str, session_id: str) -> None:
    if not repo_locks_dir().is_dir():
        return
    for owner in list(repo_locks_dir().glob("*/owner.json")):
        value = _read_json(owner, tolerate_failure=True)
        if (
            isinstance(value, dict)
            and value.get("change") == change
            and value.get("session_id") == session_id
        ):
            lock = owner.parent
            owner.unlink(missing_ok=True)
            try:
                lock.rmdir()
            except OSError:
                pass


def lock_change(change: str, session_id: str) -> None:
    directory = change_dir(change)
    if not session_id:
        die(PREFIX, "session id is required")
    lock = directory / "runtime/lock"
    owner = lock / "owner.json"
    (directory / "runtime/logs").mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        if owner_is_live(owner, directory):
            print(f"ops-runtime: active lock exists: {lock}", file=sys.stderr)
            value = _read_json(owner, tolerate_failure=True)
            if isinstance(value, dict):
                print(
                    json_text(
                        {
                            key: value.get(key)
                            for key in (
                                "change",
                                "session_id",
                                "pid",
                                "hostname",
                                "started_at",
                            )
                        }
                    ),
                    file=sys.stderr,
                )
            raise _ReturnStatus(1) from None
        print(
            f"ops-runtime: releasing stale lock (owning process is dead): {lock}",
            file=sys.stderr,
        )
        shutil.rmtree(lock, ignore_errors=True)
        try:
            lock.mkdir()
        except FileExistsError:
            print(
                f"ops-runtime: cannot acquire lock after stale release: {lock}",
                file=sys.stderr,
            )
            raise _ReturnStatus(1) from None
    atomic_write_json(
        owner,
        {
            "change": change,
            "session_id": session_id,
            "pid": lock_anchor_pid(),
            "hostname": socket.gethostname(),
            "started_at": utc_now(),
        },
    )


def lock_repositories(change: str, session_id: str, repositories: list[str]) -> None:
    if not repositories:
        die(PREFIX, "at least one repository is required")
    if not session_id:
        die(PREFIX, "session id is required")
    # Imported lazily to keep lock -> state dependencies one-way. The owner
    # assertion is supplied by the CLI/state transaction layer at dispatch.
    canonical_repositories = sorted({canonical_repo(item) for item in repositories})
    directory = change_dir(change)

    def existing_status(repository: str) -> bool:
        return repo_lock_dir(repository).exists()

    with ThreadPoolExecutor(
        max_workers=max(1, min(8, len(canonical_repositories)))
    ) as pool:
        # This is only an existence pre-check. The result is deliberately not
        # used as a liveness verdict because the lock can change before the
        # sequential acquisition loop reaches it.
        for _ in pool.map(existing_status, canonical_repositories):
            pass
    for canonical in canonical_repositories:
        lock = repo_lock_dir(canonical)
        owner = lock / "owner.json"
        lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock.mkdir()
        except FileExistsError:
            if owner_is_live(owner, directory):
                print(
                    f"ops-runtime: repository lock exists for {canonical}",
                    file=sys.stderr,
                )
                value = _read_json(owner, tolerate_failure=True)
                if isinstance(value, dict):
                    print(
                        json_text(
                            {
                                key: value.get(key)
                                for key in (
                                    "change",
                                    "session_id",
                                    "repository",
                                    "pid",
                                    "started_at",
                                )
                            }
                        ),
                        file=sys.stderr,
                    )
                release_repo_locks(change, session_id)
                raise _ReturnStatus(1) from None
            print(
                f"ops-runtime: releasing stale repository lock (owning process is dead): {canonical}",
                file=sys.stderr,
            )
            shutil.rmtree(lock, ignore_errors=True)
            try:
                lock.mkdir()
            except FileExistsError:
                print(
                    f"ops-runtime: cannot acquire repository lock after stale release: {canonical}",
                    file=sys.stderr,
                )
                release_repo_locks(change, session_id)
                raise _ReturnStatus(1) from None
        atomic_write_json(
            owner,
            {
                "change": change,
                "session_id": session_id,
                "repository": canonical,
                "pid": lock_anchor_pid(),
                "hostname": socket.gethostname(),
                "started_at": utc_now(),
            },
        )


def assert_repo_lock(change: str, session_id: str, repository: str) -> None:
    canonical = canonical_repo(repository)
    owner = repo_lock_dir(canonical) / "owner.json"
    if not owner.is_file():
        die(PREFIX, f"repository lock not found: {canonical}")
    value = _read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or not (
        value.get("change") == change
        and value.get("session_id") == session_id
        and value.get("repository") == canonical
    ):
        die(PREFIX, f"repository lock is not owned by this change/session: {canonical}")
