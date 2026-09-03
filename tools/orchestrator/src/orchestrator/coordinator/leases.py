"""Session admission and fenced resource leases."""

from __future__ import annotations

import os
import socket
import uuid
from pathlib import Path
from typing import Any

from ..core.io import utc_after, utc_now
from .db import CoordinatorDB
from .store import CoordinatorConflictError, CoordinatorError, StaleVersionError, _id, _json, _row

DEFAULT_MAX_SESSIONS = 2


def process_start_identity(pid: int) -> str | None:
    """Return a host-qualified Linux process start identity, when readable."""

    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
        return f"{socket.gethostname()}:{fields[21]}"
    except (OSError, IndexError, ValueError):
        return None


def max_sessions(value: int | None = None) -> int:
    configured = value if value is not None else int(os.environ.get("ORCHESTRATOR_MAX_SESSIONS", DEFAULT_MAX_SESSIONS))
    if not isinstance(configured, int) or isinstance(configured, bool) or configured < 1:
        raise CoordinatorError("ORCHESTRATOR_MAX_SESSIONS must be a positive integer")
    return configured


def admit_session(
    session_id: str,
    *,
    db: CoordinatorDB | None = None,
    capacity: int | None = None,
    owner_pid: int | None = None,
    owner_start_time: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Reserve a bounded slot, or persist a queued result without starting a worker."""

    session_id = _id(session_id)
    capacity = max_sessions(capacity)
    owner_pid = owner_pid or os.getpid()
    owner_start_time = owner_start_time or process_start_identity(owner_pid) or "unknown"
    if owner_pid <= 0 or not owner_start_time or lease_seconds <= 0:
        raise CoordinatorError("admission owner and lease values are invalid")
    coordinator = db or CoordinatorDB()
    now = utc_now()
    expires = utc_after(lease_seconds)
    with coordinator.transaction() as connection:
        session = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise CoordinatorError(f"session not found: {session_id}")
        existing = connection.execute("SELECT * FROM admission_slots WHERE session_id = ?", (session_id,)).fetchone()
        if existing is not None:
            if session["status"] == "QUEUED":
                connection.execute(
                    "UPDATE sessions SET status = 'RUNNING', version = version + 1, updated_at = ? WHERE id = ?",
                    (now, session_id),
                )
            updated = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            return {"admitted": True, "slot_id": existing["slot_id"], "fencing_token": existing["fencing_token"], "session": _row(updated)}
        occupied = {int(row["slot_id"]) for row in connection.execute("SELECT slot_id FROM admission_slots").fetchall()}
        slot_id = next((candidate for candidate in range(capacity) if candidate not in occupied), None)
        if slot_id is None:
            checkpoint = dict(_row(session)["checkpoint"])
            checkpoint["admission_reason"] = "capacity_exhausted"
            checkpoint_json = _json(checkpoint, "checkpoint")
            connection.execute(
                "UPDATE sessions SET status = 'QUEUED', checkpoint = ?, version = version + 1, updated_at = ? WHERE id = ?",
                (checkpoint_json, now, session_id),
            )
            updated = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            return {"admitted": False, "status": "QUEUED", "reason": "capacity_exhausted", "session": _row(updated)}
        token = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO admission_slots(slot_id, session_id, lease_expires_at, fencing_token) VALUES (?, ?, ?, ?)",
            (slot_id, session_id, expires, token),
        )
        connection.execute(
            "UPDATE sessions SET status = 'RUNNING', lease_owner = ?, lease_expires_at = ?, fencing_token = ?, version = version + 1, updated_at = ? WHERE id = ?",
            (f"{owner_pid}:{owner_start_time}", expires, token, now, session_id),
        )
        updated = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    return {"admitted": True, "slot_id": slot_id, "fencing_token": token, "session": _row(updated)}


def renew_admission(
    session_id: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    session_id = _id(session_id)
    if not fencing_token or lease_seconds <= 0:
        raise CoordinatorError("admission fencing token and lease are required")
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        slot = connection.execute(
            "SELECT * FROM admission_slots WHERE session_id = ? AND fencing_token = ?",
            (session_id, fencing_token),
        ).fetchone()
        if slot is None:
            raise StaleVersionError("admission fencing token is stale")
        expires = utc_after(lease_seconds)
        connection.execute(
            "UPDATE admission_slots SET lease_expires_at = ? WHERE session_id = ? AND fencing_token = ?",
            (expires, session_id, fencing_token),
        )
        connection.execute(
            "UPDATE sessions SET lease_expires_at = ?, updated_at = ? WHERE id = ? AND fencing_token = ?",
            (expires, utc_now(), session_id, fencing_token),
        )
        return {"session_id": session_id, "slot_id": slot["slot_id"], "fencing_token": fencing_token, "lease_expires_at": expires}


def heartbeat_session(
    session_id: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Renew the admission heartbeat without holding storage across provider work."""

    session_id = _id(session_id)
    if not fencing_token or lease_seconds <= 0:
        raise CoordinatorError("session fencing token and lease are required")
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        expires = utc_after(lease_seconds)
        updated = connection.execute(
            "UPDATE sessions SET lease_expires_at = ?, updated_at = ? WHERE id = ? AND fencing_token = ? AND status = 'RUNNING'",
            (expires, utc_now(), session_id, fencing_token),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("session heartbeat fencing token is stale")
        connection.execute(
            "UPDATE admission_slots SET lease_expires_at = ? WHERE session_id = ? AND fencing_token = ?",
            (expires, session_id, fencing_token),
        )
    return {"session_id": session_id, "fencing_token": fencing_token, "lease_expires_at": expires}


def release_admission(
    session_id: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
) -> None:
    session_id = _id(session_id)
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        deleted = connection.execute(
            "DELETE FROM admission_slots WHERE session_id = ? AND fencing_token = ?",
            (session_id, fencing_token),
        )
        if deleted.rowcount != 1:
            raise StaleVersionError("admission fencing token is stale")
        connection.execute(
            "UPDATE sessions SET lease_owner = NULL, lease_expires_at = NULL, fencing_token = NULL, updated_at = ? WHERE id = ? AND fencing_token = ?",
            (utc_now(), session_id, fencing_token),
        )


def acquire_resource(
    session_id: str,
    resource_type: str,
    resource_key: str,
    *,
    db: CoordinatorDB | None = None,
    owner_pid: int | None = None,
    owner_start_time: str | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    """Acquire one unique scope without deleting expired ownership."""

    session_id = _id(session_id)
    if not resource_type or not resource_key or lease_seconds <= 0:
        raise CoordinatorError("resource and lease values are required")
    owner_pid = owner_pid or os.getpid()
    owner_start_time = owner_start_time or process_start_identity(owner_pid) or "unknown"
    if owner_pid <= 0 or not owner_start_time:
        raise CoordinatorError("resource owner identity is required")
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        if connection.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone() is None:
            raise CoordinatorError(f"session not found: {session_id}")
        existing = connection.execute(
            "SELECT * FROM resource_leases WHERE resource_type = ? AND resource_key = ?",
            (resource_type, resource_key),
        ).fetchone()
        if existing is not None:
            if existing["session_id"] == session_id and existing["owner_pid"] == owner_pid and existing["owner_start_time"] == owner_start_time:
                return dict(existing)
            raise CoordinatorConflictError(
                f"resource is owned by session {existing['session_id']}; recovery must verify its owner"
            )
        token = str(uuid.uuid4())
        expires = utc_after(lease_seconds)
        connection.execute(
            "INSERT INTO resource_leases(resource_type, resource_key, session_id, owner_pid, owner_start_time, lease_expires_at, fencing_token) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (resource_type, resource_key, session_id, owner_pid, owner_start_time, expires, token),
        )
        row = connection.execute(
            "SELECT * FROM resource_leases WHERE resource_type = ? AND resource_key = ?",
            (resource_type, resource_key),
        ).fetchone()
    assert row is not None
    return dict(row)


def assert_resource_lease(
    resource_type: str,
    resource_key: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    coordinator = db or CoordinatorDB()
    rows = coordinator.read(
        "SELECT * FROM resource_leases WHERE resource_type = ? AND resource_key = ?",
        (resource_type, resource_key),
    )
    if not rows or rows[0]["fencing_token"] != fencing_token:
        raise StaleVersionError("resource fencing token is stale or missing")
    row = dict(rows[0])
    if row["lease_expires_at"] <= utc_now():
        raise StaleVersionError("resource lease is expired and requires recovery")
    return row


def renew_resource(
    resource_type: str,
    resource_key: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
    lease_seconds: int = 300,
) -> dict[str, Any]:
    if not fencing_token or lease_seconds <= 0:
        raise CoordinatorError("resource fencing token and lease are required")
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        expires = utc_after(lease_seconds)
        updated = connection.execute(
            "UPDATE resource_leases SET lease_expires_at = ? WHERE resource_type = ? AND resource_key = ? AND fencing_token = ?",
            (expires, resource_type, resource_key, fencing_token),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("resource fencing token is stale")
        row = connection.execute(
            "SELECT * FROM resource_leases WHERE resource_type = ? AND resource_key = ?",
            (resource_type, resource_key),
        ).fetchone()
    assert row is not None
    return dict(row)


def release_resource(
    resource_type: str,
    resource_key: str,
    fencing_token: str,
    *,
    db: CoordinatorDB | None = None,
) -> None:
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        deleted = connection.execute(
            "DELETE FROM resource_leases WHERE resource_type = ? AND resource_key = ? AND fencing_token = ?",
            (resource_type, resource_key, fencing_token),
        )
        if deleted.rowcount != 1:
            raise StaleVersionError("resource fencing token is stale")


def recovery_report(session_id: str, *, db: CoordinatorDB | None = None) -> dict[str, Any]:
    """Inspect ownership without reclaiming an expired or ambiguous lease."""

    session_id = _id(session_id)
    coordinator = db or CoordinatorDB()
    with coordinator.transaction(immediate=False) as connection:
        session = connection.execute("SELECT id, status, lease_owner, lease_expires_at, fencing_token, checkpoint FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if session is None:
            raise CoordinatorError(f"session not found: {session_id}")
        slots = connection.execute("SELECT * FROM admission_slots WHERE session_id = ?", (session_id,)).fetchall()
        resources = connection.execute("SELECT * FROM resource_leases WHERE session_id = ? ORDER BY resource_type, resource_key", (session_id,)).fetchall()
        latest_attempt = connection.execute("SELECT status FROM attempts WHERE session_id = ? ORDER BY started_at DESC, rowid DESC LIMIT 1", (session_id,)).fetchone()
    session_value = _row(session) or {}
    owner_parts = str(session_value["lease_owner"] or "").split(":", 1)
    admission_leases = [
        {
            **dict(item),
            "resource_type": "admission",
            "resource_key": str(item["slot_id"]),
            "owner_pid": int(owner_parts[0]) if owner_parts and owner_parts[0].isdigit() else 0,
            "owner_start_time": owner_parts[1] if len(owner_parts) == 2 else "",
        }
        for item in slots
    ]
    leases = admission_leases + [dict(item) for item in resources]
    expired = [item for item in leases if item["lease_expires_at"] <= utc_now()]
    indeterminate = []
    dead = []
    for item in expired:
        pid = item.get("owner_pid", 0)
        expected = item.get("owner_start_time", "")
        current = process_start_identity(pid) if isinstance(pid, int) and pid > 0 else None
        if current is None:
            dead.append(item)
        elif expected and current == expected:
            indeterminate.append(item)
        else:
            dead.append(item)
    state = "LIVE"
    reason = "leases_within_deadline"
    if indeterminate:
        state, reason = "INDETERMINATE", "owner_liveness_or_identity_ambiguous"
    elif expired:
        state, reason = "RECOVERABLE", "expired_owner_confirmed_dead"
    latest_status = latest_attempt["status"] if latest_attempt is not None else None
    if latest_status in {"RUNNING", "INTERRUPTED"} and session_value.get("checkpoint", {}).get("safe_boundary") is not True:
        state, reason = "INDETERMINATE", "attempt_side_effects_ambiguous"
    return {
        "session": session_value,
        "state": state,
        "reason": reason,
        "leases": leases,
        "latest_attempt_status": latest_status,
    }


def recover_session(session_id: str, *, db: CoordinatorDB | None = None) -> dict[str, Any]:
    """Requeue only a session whose expired owners were unambiguously dead."""

    report = recovery_report(session_id, db=db)
    if report["state"] != "RECOVERABLE":
        raise CoordinatorError(f"session recovery is {report['state'].lower()}: {report['reason']}")
    coordinator = db or CoordinatorDB()
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET status = 'QUEUED', lease_owner = NULL, lease_expires_at = NULL, fencing_token = NULL, version = version + 1, updated_at = datetime('now') WHERE id = ? AND status IN ('RUNNING', 'PAUSED')",
            (session_id,),
        )
        if updated.rowcount != 1:
            raise CoordinatorError("session is not recoverable in its current status")
        connection.execute("DELETE FROM admission_slots WHERE session_id = ?", (session_id,))
        connection.execute("DELETE FROM resource_leases WHERE session_id = ?", (session_id,))
        row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    assert row is not None
    return dict(row)
