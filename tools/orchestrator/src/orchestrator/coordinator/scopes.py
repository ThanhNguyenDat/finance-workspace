"""Change/worktree scope helpers and isolated Git worktree allocation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from .db import CoordinatorDB, repository_root
from .leases import acquire_resource, release_resource
from .store import CoordinatorError, _id

GIT_TIMEOUT_SECONDS = 10
SAFE_ACCOUNT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def acquire_change_scope(
    session_id: str,
    change: str,
    *,
    db: CoordinatorDB | None = None,
    owner_pid: int | None = None,
    owner_start_time: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    return acquire_resource(
        _id(session_id),
        "change",
        f"change:{change}",
        db=db,
        owner_pid=owner_pid,
        owner_start_time=owner_start_time,
        lease_seconds=lease_seconds,
    )


def acquire_account_scope(
    session_id: str,
    provider: str,
    account: str,
    *,
    db: CoordinatorDB | None = None,
    owner_pid: int | None = None,
    owner_start_time: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Reserve one provider login while leaving other configured accounts free."""

    if (
        provider not in {"claude", "codex"}
        or not isinstance(account, str)
        or not SAFE_ACCOUNT.fullmatch(account)
    ):
        raise CoordinatorError("provider and account are required")
    lease = acquire_resource(
        _id(session_id),
        "account",
        f"account:{provider}/{account.lower()}",
        db=db,
        owner_pid=owner_pid,
        owner_start_time=owner_start_time,
        lease_seconds=lease_seconds,
    )
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET selected_provider = ?, selected_account = ?, version = version + 1, updated_at = datetime('now') WHERE id = ?",
            (provider, account.lower(), session_id),
        )
        if updated.rowcount != 1:
            release_resource(
                "account",
                f"account:{provider}/{account.lower()}",
                lease["fencing_token"],
                db=coordinator,
            )
            raise CoordinatorError(f"session not found: {session_id}")
    return {"provider": provider, "account": account.lower(), **lease}


def _canonical_repository(repository: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CoordinatorError(f"could not resolve Git worktree: {repository}") from exc
    if result.returncode != 0 or not result.stdout.strip():
        raise CoordinatorError(f"not a Git worktree: {repository}")
    return Path(result.stdout.strip()).resolve()


def allocate_worktree(
    session_id: str,
    repository: Path,
    *,
    db: CoordinatorDB | None = None,
    worktree_path: Path | None = None,
    base_ref: str = "HEAD",
    owner_pid: int | None = None,
    owner_start_time: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Create or reuse a session-owned detached worktree with a fenced scope."""

    session_id = _id(session_id)
    coordinator = db or CoordinatorDB()
    canonical = _canonical_repository(repository)
    current = coordinator.read(
        "SELECT worktree, version FROM sessions WHERE id = ?", (session_id,)
    )
    if not current:
        raise CoordinatorError(f"session not found: {session_id}")
    existing = current[0]["worktree"]
    if existing and Path(existing).is_dir():
        return {
            "session_id": session_id,
            "repository": str(canonical),
            "worktree": existing,
            "reused": True,
        }
    root = repository_root() / ".ops" / "runtime" / "coordinator" / "worktrees"
    target = (worktree_path or root / session_id / canonical.name).resolve()
    if target.exists():
        raise CoordinatorError(f"worktree path already exists: {target}")
    lease = acquire_resource(
        session_id,
        "worktree",
        f"worktree:{target}",
        db=coordinator,
        owner_pid=owner_pid,
        owner_start_time=owner_start_time,
        lease_seconds=lease_seconds,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(canonical),
                    "worktree",
                    "add",
                    "--detach",
                    str(target),
                    base_ref,
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CoordinatorError(
                f"Git worktree allocation timed out: {target}"
            ) from exc
        if result.returncode != 0:
            detail = result.stderr.strip() or "git worktree add failed"
            raise CoordinatorError(detail)
        with coordinator.transaction() as connection:
            updated = connection.execute(
                "UPDATE sessions SET worktree = ?, version = version + 1, updated_at = datetime('now') WHERE id = ? AND version = ?",
                (str(target), session_id, current[0]["version"]),
            )
            if updated.rowcount != 1:
                raise CoordinatorError("session changed while allocating worktree")
    except BaseException:
        release_resource(
            "worktree", f"worktree:{target}", lease["fencing_token"], db=coordinator
        )
        raise
    return {
        "session_id": session_id,
        "repository": str(canonical),
        "worktree": str(target),
        "fencing_token": lease["fencing_token"],
        "reused": False,
    }
