"""SQLite connection and schema management for the local coordinator."""

from __future__ import annotations

import os
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 2
DEFAULT_BUSY_TIMEOUT_MS = 5_000


def repository_root() -> Path:
    return Path(os.environ.get("OPS_ROOT", Path(__file__).resolve().parents[5]))


def coordinator_path(root: Path | None = None) -> Path:
    base = root or repository_root()
    return base / ".ops" / "runtime" / "coordinator" / "coordinator.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    change_name TEXT NOT NULL CHECK (length(change_name) > 0),
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    round INTEGER NOT NULL CHECK (round >= 0),
    quant_iteration INTEGER CHECK (quant_iteration IS NULL OR quant_iteration >= 1),
    status TEXT NOT NULL CHECK (status IN ('QUEUED', 'RUNNING', 'PAUSED', 'BLOCKED', 'FAILED', 'COMPLETED', 'CANCELLED')),
    worktree TEXT,
    context_json TEXT NOT NULL CHECK (json_valid(context_json)),
    checkpoint TEXT NOT NULL CHECK (json_valid(checkpoint)),
    selected_provider TEXT,
    selected_account TEXT,
    lease_owner TEXT,
    lease_expires_at TEXT,
    fencing_token TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS sessions_quant_iteration
    ON sessions(quant_iteration)
    WHERE quant_iteration IS NOT NULL;

CREATE INDEX IF NOT EXISTS sessions_change_status
    ON sessions(change_name, status);

CREATE TABLE IF NOT EXISTS attempts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    round INTEGER NOT NULL CHECK (round >= 0),
    attempt_no INTEGER NOT NULL CHECK (attempt_no >= 1),
    provider TEXT NOT NULL CHECK (length(provider) > 0),
    account TEXT,
    model TEXT NOT NULL CHECK (length(model) > 0),
    effort TEXT NOT NULL CHECK (length(effort) > 0),
    continuation INTEGER NOT NULL CHECK (continuation IN (0, 1)),
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'INTERRUPTED', 'BLOCKED', 'FAILED')),
    result_class TEXT,
    evidence_path TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    UNIQUE(session_id, phase, attempt_no)
);

CREATE TABLE IF NOT EXISTS resource_leases (
    resource_type TEXT NOT NULL CHECK (length(resource_type) > 0),
    resource_key TEXT NOT NULL CHECK (length(resource_key) > 0),
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    owner_pid INTEGER NOT NULL CHECK (owner_pid > 0),
    owner_start_time TEXT NOT NULL,
    lease_expires_at TEXT NOT NULL,
    fencing_token TEXT NOT NULL,
    PRIMARY KEY(resource_type, resource_key)
);

CREATE INDEX IF NOT EXISTS resource_leases_session
    ON resource_leases(session_id);

CREATE TABLE IF NOT EXISTS admission_slots (
    slot_id INTEGER PRIMARY KEY CHECK (slot_id >= 0),
    session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    lease_expires_at TEXT NOT NULL,
    fencing_token TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL CHECK (sequence >= 1),
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    attempt_id TEXT REFERENCES attempts(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL CHECK (length(event_type) > 0),
    safe_payload TEXT NOT NULL CHECK (json_valid(safe_payload)),
    created_at TEXT NOT NULL,
    PRIMARY KEY(session_id, sequence)
);

CREATE TABLE IF NOT EXISTS operator_questions (
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'ANSWERED', 'EXPIRED', 'REJECTED')),
    safe_payload TEXT NOT NULL CHECK (json_valid(safe_payload)),
    response TEXT,
    expires_at TEXT NOT NULL,
    PRIMARY KEY(session_id, question_id)
);

CREATE TABLE IF NOT EXISTS coordinator_counters (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL CHECK (value >= 0)
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
"""

_MIGRATION_V2 = """
CREATE TABLE sessions_v2 (
    id TEXT PRIMARY KEY,
    change_name TEXT NOT NULL CHECK (length(change_name) > 0),
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    round INTEGER NOT NULL CHECK (round >= 0),
    quant_iteration INTEGER CHECK (quant_iteration IS NULL OR quant_iteration >= 1),
    status TEXT NOT NULL CHECK (status IN ('QUEUED', 'RUNNING', 'PAUSED', 'BLOCKED', 'FAILED', 'COMPLETED', 'CANCELLED')),
    worktree TEXT,
    context_json TEXT NOT NULL CHECK (json_valid(context_json)),
    checkpoint TEXT NOT NULL CHECK (json_valid(checkpoint)),
    selected_provider TEXT,
    selected_account TEXT,
    lease_owner TEXT,
    lease_expires_at TEXT,
    fencing_token TEXT,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
INSERT INTO sessions_v2 SELECT * FROM sessions;

CREATE TABLE attempts_v2 (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions_v2(id) ON DELETE CASCADE,
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    round INTEGER NOT NULL CHECK (round >= 0),
    attempt_no INTEGER NOT NULL CHECK (attempt_no >= 1),
    provider TEXT NOT NULL CHECK (length(provider) > 0),
    account TEXT,
    model TEXT NOT NULL CHECK (length(model) > 0),
    effort TEXT NOT NULL CHECK (length(effort) > 0),
    continuation INTEGER NOT NULL CHECK (continuation IN (0, 1)),
    status TEXT NOT NULL CHECK (status IN ('RUNNING', 'COMPLETED', 'INTERRUPTED', 'BLOCKED', 'FAILED')),
    result_class TEXT,
    evidence_path TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    UNIQUE(session_id, phase, attempt_no)
);
INSERT INTO attempts_v2 SELECT * FROM attempts;

CREATE TABLE events_v2 (
    session_id TEXT NOT NULL REFERENCES sessions_v2(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL CHECK (sequence >= 1),
    phase TEXT NOT NULL CHECK (phase IN ('PLAN', 'BRAINSTORM', 'IMPLEMENT', 'VERIFY', 'FIX', 'FINAL_VERIFY', 'ARCHIVE')),
    attempt_id TEXT REFERENCES attempts_v2(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL CHECK (length(event_type) > 0),
    safe_payload TEXT NOT NULL CHECK (json_valid(safe_payload)),
    created_at TEXT NOT NULL,
    PRIMARY KEY(session_id, sequence)
);
INSERT INTO events_v2 SELECT * FROM events;

DROP INDEX IF EXISTS sessions_quant_iteration;
DROP INDEX IF EXISTS sessions_change_status;
DROP TABLE events;
DROP TABLE attempts;
DROP TABLE sessions;
ALTER TABLE sessions_v2 RENAME TO sessions;
ALTER TABLE attempts_v2 RENAME TO attempts;
ALTER TABLE events_v2 RENAME TO events;
CREATE UNIQUE INDEX sessions_quant_iteration
    ON sessions(quant_iteration)
    WHERE quant_iteration IS NOT NULL;
CREATE INDEX sessions_change_status
    ON sessions(change_name, status);
"""


class CoordinatorDB:
    """Own a coordinator database and keep each transaction short-lived."""

    def __init__(
        self,
        root: Path | None = None,
        path: Path | None = None,
        busy_timeout_ms: int | None = None,
    ) -> None:
        self.path = path or coordinator_path(root)
        configured = (
            busy_timeout_ms
            if busy_timeout_ms is not None
            else int(
                os.environ.get(
                    "ORCHESTRATOR_DB_BUSY_TIMEOUT_MS", DEFAULT_BUSY_TIMEOUT_MS
                )
            )
        )
        if configured <= 0:
            raise ValueError("busy timeout must be positive")
        self.busy_timeout_ms = configured
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        return self._open_connection()

    def initialize(self) -> None:
        connection = self.connect_uninitialized()
        current_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        try:
            if current_version == 1:
                connection.execute("PRAGMA foreign_keys = OFF")
            connection.executescript(
                "BEGIN IMMEDIATE;\n"
                + SCHEMA
                + ("\n" + _MIGRATION_V2 if current_version == 1 else "")
                + "\nINSERT OR IGNORE INTO schema_migrations(version, applied_at) "
                + "VALUES ("
                + str(SCHEMA_VERSION)
                + ", datetime('now'));\n"
                + f"PRAGMA user_version = {SCHEMA_VERSION};\n"
                + "COMMIT;"
            )
        except BaseException:
            connection.rollback()
            raise
        finally:
            if current_version == 1:
                connection.execute("PRAGMA foreign_keys = ON")
            connection.close()

    def connect_uninitialized(self) -> sqlite3.Connection:
        return self._open_connection()

    def _open_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        deadline = time.monotonic() + self.busy_timeout_ms / 1000
        while True:
            try:
                journal_mode = connection.execute(
                    "PRAGMA journal_mode = WAL"
                ).fetchone()[0]
                if journal_mode.lower() != "wal":
                    raise RuntimeError(
                        f"coordinator requires WAL journal mode, got {journal_mode}"
                    )
                return connection
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower() or time.monotonic() >= deadline:
                    connection.close()
                    raise
                time.sleep(min(0.02, max(0.001, deadline - time.monotonic())))

    @contextmanager
    def transaction(self, *, immediate: bool = True) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def read(self, sql: str, parameters: tuple[object, ...] = ()) -> list[sqlite3.Row]:
        connection = self.connect()
        try:
            return list(connection.execute(sql, parameters).fetchall())
        finally:
            connection.close()
