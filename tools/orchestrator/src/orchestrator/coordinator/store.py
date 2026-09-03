"""Atomic coordinator records and lifecycle transitions."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..core.io import atomic_write_json, utc_now
from ..core.redaction import redact_text, redact_value
from .db import CoordinatorDB, repository_root

PHASES = {"PLAN", "BRAINSTORM", "IMPLEMENT", "VERIFY", "FIX", "ARCHIVE"}
TRANSITIONS = {
    ("PLAN", "BRAINSTORM"),
    ("BRAINSTORM", "IMPLEMENT"),
    ("IMPLEMENT", "VERIFY"),
    ("VERIFY", "FIX"),
    ("FIX", "VERIFY"),
    ("VERIFY", "ARCHIVE"),
}
SAFE_CHANGE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
STATUSES = {
    "QUEUED",
    "RUNNING",
    "PAUSED",
    "BLOCKED",
    "FAILED",
    "COMPLETED",
    "CANCELLED",
}
ATTEMPT_STATUSES = {"RUNNING", "COMPLETED", "INTERRUPTED", "BLOCKED", "FAILED"}
QUESTION_STATUSES = {"PENDING", "ANSWERED", "EXPIRED", "REJECTED"}


class CoordinatorError(ValueError):
    """Base class for expected coordinator errors."""


class CoordinatorConflictError(CoordinatorError):
    """A unique coordinator record already exists."""


class StaleVersionError(CoordinatorError):
    """An optimistic version or fencing value no longer owns a session."""


class IllegalTransitionError(CoordinatorError):
    """A lifecycle transition is not allowed by the state machine."""


def _db(db: CoordinatorDB | None) -> CoordinatorDB:
    return db or CoordinatorDB()


def _json(value: Any, label: str) -> str:
    try:
        encoded = json.dumps(
            redact_value(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:
        raise CoordinatorError(f"{label} must be JSON serializable") from exc
    if not isinstance(value, (dict, list)):
        raise CoordinatorError(f"{label} must be a JSON object or array")
    return encoded


def _id(value: str | None = None) -> str:
    if value is None:
        return str(uuid.uuid4())
    if not isinstance(value, str) or not value or len(value) > 128:
        raise CoordinatorError(
            "identifier must be a non-empty string up to 128 characters"
        )
    return value


def _change(change: str) -> str:
    if (
        not isinstance(change, str)
        or not SAFE_CHANGE.fullmatch(change)
        or "/../" in f"/{change}/"
    ):
        raise CoordinatorError(f"invalid change name: {change}")
    return change


def _phase(phase: str) -> str:
    if phase not in PHASES:
        raise CoordinatorError(f"invalid phase: {phase}")
    return phase


def _row(row: Any) -> dict[str, Any] | None:
    if row is None:
        return None
    value = dict(row)
    for key in ("context_json", "checkpoint", "safe_payload"):
        if key in value and isinstance(value[key], str):
            value[key] = json.loads(value[key])
    return value


def create_session(
    change: str,
    context: dict[str, Any],
    *,
    db: CoordinatorDB | None = None,
    session_id: str | None = None,
    worktree: str | None = None,
    phase: str = "PLAN",
    status: str = "RUNNING",
    checkpoint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    coordinator = _db(db)
    session_id = _id(session_id)
    change = _change(change)
    phase = _phase(phase)
    if status not in STATUSES:
        raise CoordinatorError(f"invalid session status: {status}")
    context_json = _json(context, "context")
    checkpoint_json = _json(checkpoint or {}, "checkpoint")
    now = utc_now()
    try:
        with coordinator.transaction() as connection:
            connection.execute(
                """INSERT INTO sessions
                (id, change_name, phase, round, quant_iteration, status, worktree,
                 context_json, checkpoint, version, created_at, updated_at)
                VALUES (?, ?, ?, 0, NULL, ?, ?, ?, ?, 1, ?, ?)""",
                (
                    session_id,
                    change,
                    phase,
                    status,
                    worktree,
                    context_json,
                    checkpoint_json,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise CoordinatorConflictError(
                f"session already exists: {session_id}"
            ) from exc
        raise
    result = _row(row)
    assert result is not None
    return result


def create_quant_session(
    context: dict[str, Any],
    *,
    db: CoordinatorDB | None = None,
    change: str = "quant-research",
    session_id: str | None = None,
    worktree: str | None = None,
    run_root: Path | None = None,
) -> dict[str, Any]:
    """Create a quant session and allocate its iteration in one transaction."""

    coordinator = _db(db)
    session_id = _id(session_id)
    change = _change(change)
    context_json = _json(context, "context")
    checkpoint_json = _json({}, "checkpoint")
    now = utc_now()
    run_root = (
        run_root
        or repository_root() / ".ops" / "runtime" / "phase-agents" / "quant-runs"
    )
    try:
        with coordinator.transaction() as connection:
            counter = connection.execute(
                "SELECT value FROM coordinator_counters WHERE name = 'quant_iteration'"
            ).fetchone()
            iteration = (int(counter[0]) if counter else 0) + 1
            connection.execute(
                "INSERT INTO coordinator_counters(name, value) VALUES ('quant_iteration', ?) "
                "ON CONFLICT(name) DO UPDATE SET value = excluded.value",
                (iteration,),
            )
            connection.execute(
                """INSERT INTO sessions
                (id, change_name, phase, round, quant_iteration, status, worktree,
                 context_json, checkpoint, version, created_at, updated_at)
                VALUES (?, ?, 'PLAN', 0, ?, 'RUNNING', ?, ?, ?, 1, ?, ?)""",
                (
                    session_id,
                    change,
                    iteration,
                    worktree or str(run_root / session_id),
                    context_json,
                    checkpoint_json,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise CoordinatorConflictError(
                f"session already exists: {session_id}"
            ) from exc
        raise
    result = _row(row)
    assert result is not None
    return result


def seed_quant_iteration_floor(value: int, *, db: CoordinatorDB | None = None) -> int:
    """Migrate a legacy compatibility counter without decreasing coordinator state."""

    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CoordinatorError("quant iteration floor must be a non-negative integer")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        current = connection.execute(
            "SELECT value FROM coordinator_counters WHERE name = 'quant_iteration'"
        ).fetchone()
        existing = int(current[0]) if current else 0
        if value > existing:
            connection.execute(
                "INSERT INTO coordinator_counters(name, value) VALUES ('quant_iteration', ?) ON CONFLICT(name) DO UPDATE SET value = excluded.value",
                (value,),
            )
            existing = value
    return existing


def get_session(
    session_id: str, *, db: CoordinatorDB | None = None
) -> dict[str, Any] | None:
    session_id = _id(session_id)
    row = _db(db).read("SELECT * FROM sessions WHERE id = ?", (session_id,))
    return _row(row[0]) if row else None


def active_sessions(
    change: str, *, db: CoordinatorDB | None = None
) -> list[dict[str, Any]]:
    """Return resumable sessions for one change in creation order."""

    change = _change(change)
    rows = _db(db).read(
        "SELECT * FROM sessions WHERE change_name = ? AND status IN ('QUEUED', 'RUNNING', 'PAUSED') ORDER BY created_at, id",
        (change,),
    )
    return [_row(row) or {} for row in rows]


def resume_session(
    session_id: str, *, db: CoordinatorDB | None = None
) -> dict[str, Any]:
    """Read one durable session under a short transaction for safe re-entry."""

    session_id = _id(session_id)
    coordinator = _db(db)
    with coordinator.transaction(immediate=False) as connection:
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise CoordinatorError(f"session not found: {session_id}")
    return _row(row) or {}


def session_status(
    session_id: str, *, db: CoordinatorDB | None = None
) -> dict[str, Any]:
    """Return a read-only, session-scoped status view and evidence references."""

    session_id = _id(session_id)
    coordinator = _db(db)
    with coordinator.transaction(immediate=False) as connection:
        session = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if session is None:
            raise CoordinatorError(f"session not found: {session_id}")
        attempts = connection.execute(
            "SELECT id, phase, round, attempt_no, provider, account, model, effort, continuation, status, result_class, evidence_path, started_at, completed_at "
            "FROM attempts WHERE session_id = ? ORDER BY phase, round, attempt_no",
            (session_id,),
        ).fetchall()
        event_count = connection.execute(
            "SELECT COUNT(*) FROM events WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        pending_questions = connection.execute(
            "SELECT question_id, expires_at FROM operator_questions WHERE session_id = ? AND status = 'PENDING' ORDER BY question_id",
            (session_id,),
        ).fetchall()
    session_view = _row(session) or {}
    session_view.pop("fencing_token", None)
    session_view.pop("lease_owner", None)
    return {
        "session": session_view,
        "attempts": [dict(item) for item in attempts],
        "attempt_ids": [item["id"] for item in attempts],
        "event_count": int(event_count),
        "pending_questions": [dict(item) for item in pending_questions],
    }


def update_checkpoint(
    session_id: str,
    checkpoint: dict[str, Any],
    *,
    expected_version: int,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    """Persist a safe continuation checkpoint with optimistic fencing."""

    session_id = _id(session_id)
    checkpoint_json = _json(checkpoint, "checkpoint")
    if (
        not fencing_token
        or not isinstance(expected_version, int)
        or isinstance(expected_version, bool)
        or expected_version < 1
    ):
        raise CoordinatorError("checkpoint version and fencing token are required")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET checkpoint = ?, version = version + 1, updated_at = datetime('now') WHERE id = ? AND version = ? AND fencing_token = ?",
            (checkpoint_json, session_id, expected_version, fencing_token),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("checkpoint fencing token or version is stale")
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert row is not None
    return _row(row) or {}


def record_attempt(
    session_id: str,
    *,
    phase: str,
    round: int,
    attempt_no: int,
    provider: str,
    model: str,
    effort: str,
    continuation: bool,
    status: str,
    account: str | None = None,
    result_class: str | None = None,
    evidence_path: str | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    attempt_id: str | None = None,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    phase = _phase(phase)
    if not isinstance(round, int) or isinstance(round, bool) or round < 0:
        raise CoordinatorError("round must be a non-negative integer")
    if (
        not isinstance(attempt_no, int)
        or isinstance(attempt_no, bool)
        or attempt_no < 1
    ):
        raise CoordinatorError("attempt number must be a positive integer")
    if (
        not isinstance(provider, str)
        or not provider
        or not isinstance(model, str)
        or not model
        or not isinstance(effort, str)
        or not effort
    ):
        raise CoordinatorError("provider, model and effort are required")
    if not isinstance(continuation, bool) or status not in ATTEMPT_STATUSES:
        raise CoordinatorError("invalid attempt continuation or status")
    attempt_id = _id(attempt_id)
    started_at = started_at or utc_now()
    coordinator = _db(db)
    try:
        with coordinator.transaction() as connection:
            if (
                connection.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                is None
            ):
                raise CoordinatorError(f"session not found: {session_id}")
            connection.execute(
                """INSERT INTO attempts
                (id, session_id, phase, round, attempt_no, provider, account, model,
                 effort, continuation, status, result_class, evidence_path,
                 started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    attempt_id,
                    session_id,
                    phase,
                    round,
                    attempt_no,
                    provider,
                    account,
                    model,
                    effort,
                    int(continuation),
                    status,
                    result_class,
                    evidence_path,
                    started_at,
                    completed_at,
                ),
            )
            row = connection.execute(
                "SELECT * FROM attempts WHERE id = ?", (attempt_id,)
            ).fetchone()
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise CoordinatorConflictError(
                f"attempt already exists: {session_id}/{phase}/{attempt_no}"
            ) from exc
        raise
    assert row is not None
    return dict(row)


def update_attempt(
    session_id: str,
    attempt_id: str,
    *,
    status: str,
    result_class: str | None = None,
    evidence_path: str | None = None,
    completed_at: str | None = None,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    """Close a persisted provider attempt without holding a provider lease."""

    session_id = _id(session_id)
    attempt_id = _id(attempt_id)
    if status not in ATTEMPT_STATUSES:
        raise CoordinatorError(f"invalid attempt status: {status}")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE attempts SET status = ?, result_class = ?, evidence_path = COALESCE(?, evidence_path), completed_at = ? WHERE id = ? AND session_id = ? AND status = 'RUNNING'",
            (
                status,
                result_class,
                evidence_path,
                completed_at or utc_now(),
                attempt_id,
                session_id,
            ),
        )
        if updated.rowcount != 1:
            raise StaleVersionError(
                "attempt is missing, not session-scoped or already closed"
            )
        row = connection.execute(
            "SELECT * FROM attempts WHERE id = ? AND session_id = ?",
            (attempt_id, session_id),
        ).fetchone()
    assert row is not None
    return dict(row)


def append_event(
    session_id: str,
    *,
    phase: str,
    event_type: str,
    safe_payload: dict[str, Any],
    attempt_id: str | None = None,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    phase = _phase(phase)
    if not event_type:
        raise CoordinatorError("event type is required")
    payload_json = _json(safe_payload, "safe payload")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        if (
            connection.execute(
                "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            is None
        ):
            raise CoordinatorError(f"session not found: {session_id}")
        if (
            attempt_id is not None
            and connection.execute(
                "SELECT 1 FROM attempts WHERE id = ? AND session_id = ?",
                (attempt_id, session_id),
            ).fetchone()
            is None
        ):
            raise CoordinatorError("event attempt does not belong to session")
        latest = connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) FROM events WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
        sequence = int(latest) + 1
        now = utc_now()
        connection.execute(
            "INSERT INTO events(session_id, sequence, phase, attempt_id, event_type, safe_payload, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, sequence, phase, attempt_id, event_type, payload_json, now),
        )
        row = connection.execute(
            "SELECT * FROM events WHERE session_id = ? AND sequence = ?",
            (session_id, sequence),
        ).fetchone()
    assert row is not None
    return _row(row) or {}


def events_since(
    session_id: str, after_sequence: int = 0, *, db: CoordinatorDB | None = None
) -> list[dict[str, Any]]:
    session_id = _id(session_id)
    if (
        not isinstance(after_sequence, int)
        or isinstance(after_sequence, bool)
        or after_sequence < 0
    ):
        raise CoordinatorError("event offset must be a non-negative integer")
    rows = _db(db).read(
        "SELECT * FROM events WHERE session_id = ? AND sequence > ? ORDER BY sequence",
        (session_id, after_sequence),
    )
    return [_row(row) or {} for row in rows]


def record_question(
    session_id: str,
    *,
    question_id: str,
    safe_payload: dict[str, Any],
    expires_at: str,
    status: str = "PENDING",
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    question_id = _id(question_id)
    if status not in QUESTION_STATUSES:
        raise CoordinatorError(f"invalid question status: {status}")
    payload_json = _json(safe_payload, "safe payload")
    coordinator = _db(db)
    try:
        with coordinator.transaction() as connection:
            if (
                connection.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                is None
            ):
                raise CoordinatorError(f"session not found: {session_id}")
            connection.execute(
                "INSERT INTO operator_questions(session_id, question_id, status, safe_payload, response, expires_at) VALUES (?, ?, ?, ?, NULL, ?)",
                (session_id, question_id, status, payload_json, expires_at),
            )
            row = connection.execute(
                "SELECT * FROM operator_questions WHERE session_id = ? AND question_id = ?",
                (session_id, question_id),
            ).fetchone()
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise CoordinatorConflictError(
                f"question already exists: {session_id}/{question_id}"
            ) from exc
        raise
    assert row is not None
    return _row(row) or {}


def record_verification_findings(
    session_id: str,
    findings: list[dict[str, Any]],
    *,
    expected_version: int,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    """Persist the current VERIFY result before any FIX transition."""

    session_id = _id(session_id)
    if not isinstance(findings, list) or any(
        not isinstance(item, dict) for item in findings
    ):
        raise CoordinatorError("verification findings must be a list of JSON objects")
    if (
        not isinstance(expected_version, int)
        or isinstance(expected_version, bool)
        or expected_version < 1
        or not fencing_token
    ):
        raise CoordinatorError(
            "verification findings version and fencing token are required"
        )
    _json(findings, "verification findings")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        current = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if current is None:
            raise CoordinatorError(f"session not found: {session_id}")
        current_value = _row(current) or {}
        if current_value["phase"] != "VERIFY":
            raise IllegalTransitionError("verification findings require VERIFY phase")
        if current_value["version"] != expected_version:
            raise StaleVersionError(
                f"session version is {current_value['version']}, expected {expected_version}"
            )
        if current_value["fencing_token"] != fencing_token:
            raise StaleVersionError("verification findings fencing token is stale")
        checkpoint = dict(current_value["checkpoint"])
        blocking = any(item.get("severity") in {"P0", "P1"} for item in findings)
        checkpoint.update(
            {
                "verification_findings": findings,
                "verification_findings_round": current_value["round"],
                "blocking_findings": blocking,
                "fresh_verifier_required": False,
            }
        )
        now = utc_now()
        connection.execute(
            "UPDATE sessions SET checkpoint = ?, version = version + 1, updated_at = ? WHERE id = ? AND version = ? AND fencing_token = ?",
            (
                _json(checkpoint, "checkpoint"),
                now,
                session_id,
                expected_version,
                fencing_token,
            ),
        )
        latest = connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) FROM events WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO events(session_id, sequence, phase, event_type, safe_payload, created_at) VALUES (?, ?, 'VERIFY', 'verification.findings', ?, ?)",
            (
                session_id,
                int(latest) + 1,
                _json(
                    {
                        "round": current_value["round"],
                        "findings": findings,
                        "blocking": blocking,
                    },
                    "event payload",
                ),
                now,
            ),
        )
        updated = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert updated is not None
    return _row(updated) or {}


def record_archive_attestation(
    session_id: str,
    attestation: dict[str, Any],
    *,
    expected_version: int,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    """Persist the explicit evidence required before ARCHIVE."""

    session_id = _id(session_id)
    if not isinstance(attestation, dict):
        raise CoordinatorError("archive attestation must be a JSON object")
    required = ("verification_passed", "objective_gates_passed", "release_gates_passed")
    if any(attestation.get(key) is not True for key in required):
        raise CoordinatorError("archive attestation is incomplete")
    if (
        not isinstance(expected_version, int)
        or isinstance(expected_version, bool)
        or expected_version < 1
        or not fencing_token
    ):
        raise CoordinatorError(
            "archive attestation version and fencing token are required"
        )
    _json(attestation, "archive attestation")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        current = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if current is None:
            raise CoordinatorError(f"session not found: {session_id}")
        current_value = _row(current) or {}
        if current_value["phase"] != "VERIFY":
            raise IllegalTransitionError("archive attestation requires VERIFY phase")
        if current_value["version"] != expected_version:
            raise StaleVersionError(
                f"session version is {current_value['version']}, expected {expected_version}"
            )
        if current_value["fencing_token"] != fencing_token:
            raise StaleVersionError("archive attestation fencing token is stale")
        checkpoint = dict(current_value["checkpoint"])
        if (
            checkpoint.get("verification_findings_round") != current_value["round"]
            or checkpoint.get("blocking_findings") is not False
        ):
            raise IllegalTransitionError(
                "archive attestation requires clean current-round verification findings"
            )
        checkpoint["archive_attestation"] = attestation
        now = utc_now()
        connection.execute(
            "UPDATE sessions SET checkpoint = ?, version = version + 1, updated_at = ? WHERE id = ? AND version = ? AND fencing_token = ?",
            (
                _json(checkpoint, "checkpoint"),
                now,
                session_id,
                expected_version,
                fencing_token,
            ),
        )
        latest = connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) FROM events WHERE session_id = ?",
            (session_id,),
        ).fetchone()[0]
        connection.execute(
            "INSERT INTO events(session_id, sequence, phase, event_type, safe_payload, created_at) VALUES (?, ?, 'VERIFY', 'archive.attestation', ?, ?)",
            (session_id, int(latest) + 1, _json(attestation, "event payload"), now),
        )
        updated = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert updated is not None
    return _row(updated) or {}


def answer_question(
    session_id: str,
    question_id: str,
    response: str,
    *,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    question_id = _id(question_id)
    if not isinstance(response, str) or not response or not fencing_token:
        raise CoordinatorError(
            "question response and session fencing token are required"
        )
    response = redact_text(response)
    coordinator = _db(db)
    expiry_error: str | None = None
    with coordinator.transaction() as connection:
        session = connection.execute(
            "SELECT fencing_token FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if session is None:
            raise CoordinatorError(f"session not found: {session_id}")
        if session["fencing_token"] != fencing_token:
            raise StaleVersionError("question response fencing token is stale")
        question = connection.execute(
            "SELECT status, expires_at FROM operator_questions WHERE session_id = ? AND question_id = ?",
            (session_id, question_id),
        ).fetchone()
        if question is None or question["status"] != "PENDING":
            raise CoordinatorError("question is stale, missing or already answered")
        try:
            expires_at = datetime.fromisoformat(
                question["expires_at"].replace("Z", "+00:00")
            )
        except AttributeError, TypeError, ValueError:
            connection.execute(
                "UPDATE operator_questions SET status = 'EXPIRED' WHERE session_id = ? AND question_id = ? AND status = 'PENDING'",
                (session_id, question_id),
            )
            expiry_error = "question expiry is invalid"
        else:
            if expires_at <= datetime.now(timezone.utc):
                connection.execute(
                    "UPDATE operator_questions SET status = 'EXPIRED' WHERE session_id = ? AND question_id = ? AND status = 'PENDING'",
                    (session_id, question_id),
                )
                expiry_error = "question has expired"
            else:
                updated = connection.execute(
                    "UPDATE operator_questions SET status = 'ANSWERED', response = ? WHERE session_id = ? AND question_id = ? AND status = 'PENDING'",
                    (response, session_id, question_id),
                )
                if updated.rowcount != 1:
                    raise CoordinatorError(
                        "question is stale, missing or already answered"
                    )
                row = connection.execute(
                    "SELECT * FROM operator_questions WHERE session_id = ? AND question_id = ?",
                    (session_id, question_id),
                ).fetchone()
    if expiry_error is not None:
        raise CoordinatorError(expiry_error)
    assert row is not None
    return _row(row) or {}


def cancel_session(
    session_id: str,
    *,
    expected_version: int,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    if not fencing_token:
        raise CoordinatorError("session fencing token is required")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET status = 'CANCELLED', lease_owner = NULL, lease_expires_at = NULL, fencing_token = NULL, version = version + 1, updated_at = datetime('now') WHERE id = ? AND version = ? AND fencing_token = ? AND status IN ('QUEUED', 'RUNNING', 'PAUSED')",
            (session_id, expected_version, fencing_token),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("session version or fencing token is stale")
        connection.execute(
            "DELETE FROM admission_slots WHERE session_id = ? AND fencing_token = ?",
            (session_id, fencing_token),
        )
        connection.execute(
            "DELETE FROM resource_leases WHERE session_id = ?", (session_id,)
        )
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert row is not None
    return _row(row) or {}


def complete_session(
    session_id: str,
    *,
    expected_version: int,
    fencing_token: str,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET status = 'COMPLETED', lease_expires_at = NULL, version = version + 1, updated_at = datetime('now') WHERE id = ? AND version = ? AND fencing_token = ? AND status = 'RUNNING'",
            (session_id, expected_version, fencing_token),
        )
        if updated.rowcount != 1:
            raise StaleVersionError(
                "session completion fencing token or version is stale"
            )
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert row is not None
    return _row(row) or {}


def archive_session(
    session_id: str, *, db: CoordinatorDB | None = None
) -> dict[str, Any]:
    """Snapshot an ARCHIVE session and close it only after the snapshot exists."""

    session_id = _id(session_id)
    coordinator = _db(db)
    current = get_session(session_id, db=coordinator)
    if current is None:
        raise CoordinatorError(f"session not found: {session_id}")
    if current["phase"] != "ARCHIVE" or current["status"] != "RUNNING":
        raise IllegalTransitionError("archive requires an active ARCHIVE session")
    if current.get("checkpoint", {}).get("archive_attestation") is None:
        raise CoordinatorError("archive attestation is missing")
    if coordinator.read(
        "SELECT 1 FROM admission_slots WHERE session_id = ? LIMIT 1", (session_id,)
    ) or coordinator.read(
        "SELECT 1 FROM resource_leases WHERE session_id = ? LIMIT 1", (session_id,)
    ):
        raise CoordinatorError("archive requires cleared session leases")
    archive_root = (
        coordinator.path.parents[3]
        if len(coordinator.path.parents) > 3
        and coordinator.path.parents[2].name == ".ops"
        else coordinator.path.parent.parent
    )
    archive_name = current["change_name"].replace("/", "__")
    evidence_path = (
        archive_root
        / ".ops"
        / "archive"
        / f"{datetime.now(timezone.utc):%Y-%m-%d}-{archive_name}"
        / "coordinator"
        / f"{session_id}.json"
    )
    snapshot = session_status(session_id, db=coordinator)
    snapshot["session"].pop("fencing_token", None)
    snapshot["session"].pop("lease_owner", None)
    atomic_write_json(evidence_path, snapshot)
    checkpoint = dict(current["checkpoint"])
    checkpoint["archive_evidence"] = str(evidence_path.relative_to(archive_root))
    with coordinator.transaction() as connection:
        updated = connection.execute(
            "UPDATE sessions SET status = 'COMPLETED', checkpoint = ?, version = version + 1, updated_at = datetime('now') WHERE id = ? AND phase = 'ARCHIVE' AND status = 'RUNNING' AND version = ?",
            (_json(checkpoint, "checkpoint"), session_id, current["version"]),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("archive session changed during evidence snapshot")
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert row is not None
    return _row(row) or {}


def transition_session(
    session_id: str,
    next_phase: str,
    *,
    expected_version: int,
    fencing_token: str | None = None,
    db: CoordinatorDB | None = None,
) -> dict[str, Any]:
    session_id = _id(session_id)
    next_phase = _phase(next_phase)
    if (
        not isinstance(expected_version, int)
        or isinstance(expected_version, bool)
        or expected_version < 1
    ):
        raise CoordinatorError("expected version must be a positive integer")
    coordinator = _db(db)
    with coordinator.transaction() as connection:
        current = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if current is None:
            raise CoordinatorError(f"session not found: {session_id}")
        current_phase = current["phase"]
        if (current_phase, next_phase) not in TRANSITIONS:
            raise IllegalTransitionError(
                f"invalid phase transition: {current_phase} -> {next_phase}"
            )
        if current["version"] != expected_version:
            raise StaleVersionError(
                f"session version is {current['version']}, expected {expected_version}"
            )
        if fencing_token is not None and current["fencing_token"] != fencing_token:
            raise StaleVersionError("session fencing token is stale")
        checkpoint = dict(_row(current)["checkpoint"])
        if current_phase == "VERIFY" and next_phase == "FIX":
            if (
                checkpoint.get("verification_findings_round") != current["round"]
                or checkpoint.get("blocking_findings") is not True
            ):
                raise IllegalTransitionError(
                    "FIX requires current-round P0/P1 verification findings"
                )
        if (
            current_phase == "VERIFY"
            and next_phase == "ARCHIVE"
            and checkpoint.get("blocking_findings") is True
        ):
            raise IllegalTransitionError(
                "ARCHIVE is blocked by current-round P0/P1 findings"
            )
        if current_phase == "VERIFY" and next_phase == "ARCHIVE":
            if not isinstance(checkpoint.get("archive_attestation"), dict) or any(
                checkpoint["archive_attestation"].get(key) is not True
                for key in (
                    "verification_passed",
                    "objective_gates_passed",
                    "release_gates_passed",
                )
            ):
                raise IllegalTransitionError("ARCHIVE requires a complete attestation")
            if (
                connection.execute(
                    "SELECT 1 FROM admission_slots WHERE session_id = ? LIMIT 1",
                    (session_id,),
                ).fetchone()
                is not None
                or connection.execute(
                    "SELECT 1 FROM resource_leases WHERE session_id = ? LIMIT 1",
                    (session_id,),
                ).fetchone()
                is not None
            ):
                raise IllegalTransitionError("ARCHIVE requires cleared session leases")
        if current_phase == "FIX" and next_phase == "VERIFY":
            checkpoint.pop("verification_findings", None)
            checkpoint.pop("verification_findings_round", None)
            checkpoint.pop("blocking_findings", None)
            checkpoint["fresh_verifier_required"] = True
        now = utc_now()
        updated = connection.execute(
            "UPDATE sessions SET phase = ?, status = 'RUNNING', checkpoint = ?, version = version + 1, updated_at = ? WHERE id = ? AND version = ?",
            (
                next_phase,
                _json(checkpoint, "checkpoint"),
                now,
                session_id,
                expected_version,
            ),
        )
        if updated.rowcount != 1:
            raise StaleVersionError("session changed during transition")
        row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    assert row is not None
    return _row(row) or {}
