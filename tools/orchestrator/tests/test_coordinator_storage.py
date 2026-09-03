from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from orchestrator.coordinator import (
    CoordinatorConflictError,
    CoordinatorDB,
    CoordinatorError,
    IllegalTransitionError,
    StaleVersionError,
    acquire_account_scope,
    acquire_resource,
    admit_session,
    allocate_worktree,
    answer_question,
    append_event,
    archive_session,
    assert_resource_lease,
    create_quant_session,
    create_session,
    events_since,
    get_session,
    heartbeat_session,
    interrupt_session,
    process_start_identity,
    record_archive_attestation,
    record_attempt,
    record_question,
    record_verification_findings,
    recover_session,
    recovery_report,
    release_admission,
    release_resource,
    renew_resource,
    resume_session,
    session_status,
    transition_session,
    update_checkpoint,
)


def make_db(tmp_path: Path) -> CoordinatorDB:
    return CoordinatorDB(
        path=tmp_path / "coordinator" / "coordinator.db", busy_timeout_ms=2_000
    )


def test_database_uses_wal_foreign_keys_and_versioned_schema(tmp_path: Path):
    db = make_db(tmp_path)

    connection = db.connect()
    try:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert (
            connection.execute("SELECT version FROM schema_migrations").fetchone()[0]
            == 1
        )
    finally:
        connection.close()


def test_concurrent_quant_sessions_get_unique_iterations_and_namespaces(tmp_path: Path):
    db_path = tmp_path / "coordinator" / "coordinator.db"
    run_root = tmp_path / "quant-runs"

    def create(index: int) -> dict:
        db = CoordinatorDB(path=db_path, busy_timeout_ms=5_000)
        return create_quant_session(
            {"prompt": f"prompt-{index}"}, db=db, run_root=run_root
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        sessions = list(executor.map(create, range(8)))

    assert len({item["id"] for item in sessions}) == 8
    assert {item["quant_iteration"] for item in sessions} == set(range(1, 9))
    assert {item["worktree"] for item in sessions} == {
        str(run_root / item["id"]) for item in sessions
    }
    resumed = resume_session(
        sessions[0]["id"], db=CoordinatorDB(path=db_path, busy_timeout_ms=5_000)
    )
    assert resumed["id"] == sessions[0]["id"]
    assert resumed["quant_iteration"] == sessions[0]["quant_iteration"]


def test_records_are_atomic_and_enforce_session_scoped_uniqueness(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("change-a", {"request": "fix"}, db=db)
    session_id = session["id"]

    record_attempt(
        session_id,
        phase="PLAN",
        round=0,
        attempt_no=1,
        provider="claude",
        account="personal-02",
        model="opus",
        effort="medium",
        continuation=False,
        status="COMPLETED",
        result_class="success",
        db=db,
    )
    with pytest.raises(Exception, match="attempt already exists"):
        record_attempt(
            session_id,
            phase="PLAN",
            round=0,
            attempt_no=1,
            provider="claude",
            model="opus",
            effort="medium",
            continuation=True,
            status="COMPLETED",
            db=db,
        )
    with pytest.raises(CoordinatorError, match="invalid phase"):
        record_attempt(
            session_id,
            phase="NOT_A_PHASE",
            round=0,
            attempt_no=2,
            provider="claude",
            model="opus",
            effort="medium",
            continuation=False,
            status="COMPLETED",
            db=db,
        )

    assert db.read("SELECT COUNT(*) FROM attempts")[0][0] == 1

    with pytest.raises(CoordinatorError, match="event attempt does not belong"):
        append_event(
            session_id,
            phase="PLAN",
            event_type="tool",
            safe_payload={"ok": True},
            attempt_id="missing",
            db=db,
        )
    event = append_event(
        session_id,
        phase="PLAN",
        event_type="phase.started",
        safe_payload={"ok": True},
        db=db,
    )
    assert event["sequence"] == 1

    with pytest.raises(CoordinatorError, match="session not found"):
        record_question(
            "missing",
            question_id="q1",
            safe_payload={"prompt": "approve?"},
            expires_at="2099-01-01T00:00:00Z",
            db=db,
        )


def test_lifecycle_transitions_are_guarded_by_version(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("change-a", {"request": "plan"}, db=db)
    admitted = admit_session(session["id"], db=db)

    with pytest.raises(IllegalTransitionError):
        transition_session(
            session["id"],
            "VERIFY",
            expected_version=2,
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    assert get_session(session["id"], db=db)["phase"] == "PLAN"

    brainstorm = transition_session(
        session["id"],
        "BRAINSTORM",
        expected_version=2,
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    assert brainstorm["version"] == 3
    with pytest.raises(StaleVersionError):
        transition_session(
            session["id"],
            "IMPLEMENT",
            expected_version=2,
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    assert get_session(session["id"], db=db)["phase"] == "BRAINSTORM"

    implementation = transition_session(
        session["id"],
        "IMPLEMENT",
        expected_version=3,
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    transition_session(
        session["id"],
        "VERIFY",
        expected_version=implementation["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    verify = get_session(session["id"], db=db)
    assert verify["phase"] == "VERIFY"
    with pytest.raises(IllegalTransitionError, match="findings"):
        transition_session(
            session["id"],
            "FIX",
            expected_version=verify["version"],
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    with_findings = record_verification_findings(
        session["id"],
        [{"id": "F-1", "severity": "P1"}],
        expected_version=verify["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    with pytest.raises(IllegalTransitionError, match="blocked"):
        transition_session(
            session["id"],
            "ARCHIVE",
            expected_version=with_findings["version"],
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    fixed = transition_session(
        session["id"],
        "FIX",
        expected_version=with_findings["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    verified_again = transition_session(
        session["id"],
        "VERIFY",
        expected_version=fixed["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    with pytest.raises(IllegalTransitionError, match="findings"):
        transition_session(
            session["id"],
            "FIX",
            expected_version=verified_again["version"],
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    clean = record_verification_findings(
        session["id"],
        [],
        expected_version=verified_again["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    with pytest.raises(IllegalTransitionError, match="attestation"):
        transition_session(
            session["id"],
            "ARCHIVE",
            expected_version=clean["version"],
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    attested = record_archive_attestation(
        session["id"],
        {
            "verification_passed": True,
            "objective_gates_passed": True,
            "release_gates_passed": True,
        },
        expected_version=clean["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    with pytest.raises(IllegalTransitionError, match="leases"):
        transition_session(
            session["id"],
            "ARCHIVE",
            expected_version=attested["version"],
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    release_admission(session["id"], admitted["fencing_token"], db=db)
    archived = transition_session(
        session["id"], "ARCHIVE", expected_version=attested["version"], db=db
    )
    assert archived["phase"] == "ARCHIVE"
    assert archived["checkpoint"]["verification_findings"] == []
    assert (
        archived["checkpoint"]["archive_attestation"]["objective_gates_passed"] is True
    )
    completed = archive_session(session["id"], db=db)
    assert completed["status"] == "COMPLETED"
    assert (tmp_path / completed["checkpoint"]["archive_evidence"]).is_file()


def test_verification_findings_are_session_scoped_and_atomic(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("change-a", {"request": "verify"}, db=db)
    admitted = admit_session(session["id"], db=db)
    brainstorm = transition_session(
        session["id"],
        "BRAINSTORM",
        expected_version=2,
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    implementation = transition_session(
        session["id"],
        "IMPLEMENT",
        expected_version=brainstorm["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    verified = transition_session(
        session["id"],
        "VERIFY",
        expected_version=implementation["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )

    with pytest.raises(StaleVersionError):
        record_verification_findings(
            session["id"],
            [{"severity": "P0"}],
            expected_version=verified["version"] - 1,
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    assert get_session(session["id"], db=db)["checkpoint"] == {}

    recorded = record_verification_findings(
        session["id"],
        [{"severity": "P0", "message": "unsafe"}],
        expected_version=verified["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    assert recorded["checkpoint"]["verification_findings_round"] == 0
    assert recorded["checkpoint"]["blocking_findings"] is True
    assert [event["event_type"] for event in events_since(session["id"], db=db)] == [
        "verification.findings"
    ]


def test_checkpoint_write_rejects_stale_fencing_without_partial_update(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("change-a", {"request": "checkpoint"}, db=db)
    admitted = admit_session(
        session["id"], capacity=1, owner_pid=401, owner_start_time="boot", db=db
    )
    updated = update_checkpoint(
        session["id"],
        {"step": "started"},
        expected_version=2,
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    assert updated["checkpoint"] == {"step": "started"}
    with pytest.raises(StaleVersionError):
        update_checkpoint(
            session["id"],
            {"step": "stale"},
            expected_version=2,
            fencing_token=admitted["fencing_token"],
            db=db,
        )
    assert get_session(session["id"], db=db)["checkpoint"] == {"step": "started"}


def test_question_and_event_records_are_session_isolated(tmp_path: Path):
    db = make_db(tmp_path)
    first = create_session("one", {"request": "one"}, db=db)
    second = create_session("two", {"request": "two"}, db=db)
    question = record_question(
        first["id"],
        question_id="question-1",
        safe_payload={"kind": "approval", "command": "pytest"},
        expires_at="2099-01-01T00:00:00Z",
        db=db,
    )
    event = append_event(
        second["id"],
        phase="PLAN",
        event_type="log",
        safe_payload={"line": "safe"},
        db=db,
    )

    assert question["session_id"] == first["id"]
    assert event["session_id"] == second["id"]
    assert (
        db.read("SELECT COUNT(*) FROM events WHERE session_id = ?", (first["id"],))[0][
            0
        ]
        == 1
    )
    assert events_since(first["id"], db=db)[0]["event_type"] == "operator.question"
    assert (
        db.read(
            "SELECT COUNT(*) FROM operator_questions WHERE session_id = ?",
            (second["id"],),
        )[0][0]
        == 0
    )


def test_resume_preserves_context_manifest_and_attempt_references(tmp_path: Path):
    db = make_db(tmp_path)
    context = {
        "request": "repair the adapter",
        "openspec": "phase-agent-lifecycle-flow",
        "repositories": ["finance-workspace"],
        "findings": [{"id": "F-1", "severity": "P1"}],
    }
    session = create_session(
        "phase-agent-lifecycle-flow", context, checkpoint={"approved": True}, db=db
    )
    attempt = record_attempt(
        session["id"],
        phase="PLAN",
        round=0,
        attempt_no=1,
        provider="claude",
        model="opus",
        effort="medium",
        continuation=False,
        status="COMPLETED",
        result_class="success",
        evidence_path=".ops/runtime/evidence/plan.json",
        db=db,
    )

    resumed = resume_session(session["id"], db=db)
    status = session_status(session["id"], db=db)
    assert resumed["context_json"] == context
    assert resumed["checkpoint"] == {"approved": True}
    assert status["session"]["context_json"] == context
    assert status["session"]["checkpoint"] == {"approved": True}
    assert status["attempt_ids"] == [attempt["id"]]
    assert status["attempts"][0]["evidence_path"] == ".ops/runtime/evidence/plan.json"


def test_admission_persists_backpressure_and_uses_session_fencing(tmp_path: Path):
    db = make_db(tmp_path)
    sessions = [
        create_session(f"change-{index}", {"request": str(index)}, db=db)
        for index in range(3)
    ]
    first = admit_session(
        sessions[0]["id"], capacity=2, owner_pid=101, owner_start_time="start-a", db=db
    )
    second = admit_session(
        sessions[1]["id"], capacity=2, owner_pid=102, owner_start_time="start-b", db=db
    )
    queued = admit_session(
        sessions[2]["id"], capacity=2, owner_pid=103, owner_start_time="start-c", db=db
    )

    assert first["admitted"] is True
    assert second["admitted"] is True
    assert queued == {
        "admitted": False,
        "status": "QUEUED",
        "reason": "capacity_exhausted",
        "session": queued["session"],
    }
    assert queued["session"]["status"] == "QUEUED"
    assert db.read("SELECT COUNT(*) FROM admission_slots")[0][0] == 2
    heartbeat = heartbeat_session(
        sessions[0]["id"], first["fencing_token"], lease_seconds=600, db=db
    )
    assert heartbeat["lease_expires_at"] > first["session"]["lease_expires_at"]

    transitioned = transition_session(
        sessions[0]["id"],
        "BRAINSTORM",
        expected_version=2,
        fencing_token=first["fencing_token"],
        db=db,
    )
    assert transitioned["phase"] == "BRAINSTORM"
    with pytest.raises(StaleVersionError):
        transition_session(
            sessions[0]["id"],
            "IMPLEMENT",
            expected_version=transitioned["version"],
            fencing_token="stale-token",
            db=db,
        )
    release_admission(sessions[0]["id"], first["fencing_token"], db=db)
    retried = admit_session(
        sessions[2]["id"], capacity=2, owner_pid=103, owner_start_time="start-c", db=db
    )
    assert retried["admitted"] is True


def test_resource_leases_are_unique_fenced_and_fail_closed_after_expiry(tmp_path: Path):
    db = make_db(tmp_path)
    first = create_session("change-a", {"request": "a"}, db=db)
    second = create_session("change-b", {"request": "b"}, db=db)
    lease = acquire_resource(
        first["id"],
        "account",
        "claude/personal-02",
        owner_pid=201,
        owner_start_time="boot-a",
        db=db,
    )

    with pytest.raises(CoordinatorConflictError, match="owned by session"):
        acquire_resource(
            second["id"],
            "account",
            "claude/personal-02",
            owner_pid=202,
            owner_start_time="boot-b",
            db=db,
        )
    assert_resource_lease(
        "account", "claude/personal-02", lease["fencing_token"], db=db
    )
    with pytest.raises(StaleVersionError):
        renew_resource("account", "claude/personal-02", "stale-token", db=db)

    db_path = db.path
    connection = db.connect()
    try:
        connection.execute(
            "UPDATE resource_leases SET lease_expires_at = '2000-01-01T00:00:00Z'"
        )
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(StaleVersionError, match="expired"):
        assert_resource_lease(
            "account", "claude/personal-02", lease["fencing_token"], db=db
        )
    with pytest.raises(CoordinatorConflictError, match="recovery must verify"):
        acquire_resource(
            second["id"],
            "account",
            "claude/personal-02",
            owner_pid=202,
            owner_start_time="boot-b",
            db=db,
        )
    release_resource("account", "claude/personal-02", lease["fencing_token"], db=db)
    assert db_path.exists()


def test_mutable_sessions_get_disjoint_git_worktrees(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()

    def git(*args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=source, check=True, capture_output=True, timeout=10
        )

    git("init", "-q", "-b", "main")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Coordinator Test")
    (source / "README.md").write_text("fixture\n", encoding="utf-8")
    git("add", "README.md")
    git("commit", "-qm", "fixture")

    db = make_db(tmp_path)
    first = create_session("change-a", {"request": "a"}, db=db)
    second = create_session("change-b", {"request": "b"}, db=db)
    first_worktree = allocate_worktree(
        first["id"], source, db=db, worktree_path=tmp_path / "worktrees" / "first"
    )
    second_worktree = allocate_worktree(
        second["id"], source, db=db, worktree_path=tmp_path / "worktrees" / "second"
    )

    assert first_worktree["worktree"] != second_worktree["worktree"]
    assert Path(first_worktree["worktree"]).is_dir()
    assert Path(second_worktree["worktree"]).is_dir()
    assert allocate_worktree(first["id"], source, db=db)["reused"] is True


def test_provider_account_scopes_allow_two_accounts_but_not_one_account_twice(
    tmp_path: Path,
):
    db = make_db(tmp_path)
    first = create_session("change-a", {"request": "a"}, db=db)
    second = create_session("change-b", {"request": "b"}, db=db)
    third = create_session("change-c", {"request": "c"}, db=db)
    first_lease = acquire_account_scope(
        first["id"],
        "claude",
        "personal-02",
        owner_pid=301,
        owner_start_time="boot-a",
        db=db,
    )
    second_lease = acquire_account_scope(
        second["id"],
        "claude",
        "personal",
        owner_pid=302,
        owner_start_time="boot-b",
        db=db,
    )

    assert first_lease["account"] == "personal-02"
    assert second_lease["account"] == "personal"
    assert get_session(first["id"], db=db)["selected_account"] == "personal-02"
    assert get_session(second["id"], db=db)["selected_account"] == "personal"
    with pytest.raises(CoordinatorConflictError, match="owned by session"):
        acquire_account_scope(
            third["id"],
            "claude",
            "personal-02",
            owner_pid=303,
            owner_start_time="boot-c",
            db=db,
        )


def test_recovery_reclaims_only_confirmed_dead_owner(tmp_path: Path):
    db = make_db(tmp_path)
    dead = create_session("dead", {"request": "dead"}, db=db)
    acquire_resource(
        dead["id"],
        "change",
        "change:dead",
        owner_pid=99999999,
        owner_start_time="missing",
        db=db,
    )
    connection = db.connect()
    try:
        connection.execute(
            "UPDATE resource_leases SET lease_expires_at = '2000-01-01T00:00:00Z'"
        )
        connection.commit()
    finally:
        connection.close()
    assert recovery_report(dead["id"], db=db)["state"] == "RECOVERABLE"
    recovered = recover_session(dead["id"], db=db)
    assert recovered["status"] == "QUEUED"
    assert db.read("SELECT COUNT(*) FROM resource_leases")[0][0] == 0

    live = create_session("live", {"request": "live"}, db=db)
    current_pid = __import__("os").getpid()
    current_identity = process_start_identity(current_pid)
    assert current_identity is not None
    acquire_resource(
        live["id"],
        "change",
        "change:live",
        owner_pid=current_pid,
        owner_start_time=current_identity,
        db=db,
    )
    connection = db.connect()
    try:
        connection.execute(
            "UPDATE resource_leases SET lease_expires_at = '2000-01-01T00:00:00Z' WHERE resource_key = 'change:live'"
        )
        connection.commit()
    finally:
        connection.close()
    assert recovery_report(live["id"], db=db)["state"] == "INDETERMINATE"
    with pytest.raises(CoordinatorError, match="indeterminate"):
        recover_session(live["id"], db=db)
    assert (
        db.read(
            "SELECT COUNT(*) FROM resource_leases WHERE resource_key = 'change:live'"
        )[0][0]
        == 1
    )


def test_recovery_blocks_an_interrupted_attempt_without_safe_boundary(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("interrupted", {"request": "resume"}, db=db)
    lease = acquire_resource(
        session["id"],
        "change",
        "change:interrupted",
        owner_pid=99999999,
        owner_start_time="missing",
        db=db,
    )
    record_attempt(
        session["id"],
        phase="PLAN",
        round=0,
        attempt_no=1,
        provider="codex",
        model="model",
        effort="high",
        continuation=False,
        status="RUNNING",
        db=db,
    )
    connection = db.connect()
    try:
        connection.execute(
            "UPDATE resource_leases SET lease_expires_at = '2000-01-01T00:00:00Z' WHERE fencing_token = ?",
            (lease["fencing_token"],),
        )
        connection.commit()
    finally:
        connection.close()
    report = recovery_report(session["id"], db=db)
    assert report["state"] == "INDETERMINATE"
    assert report["reason"] == "attempt_side_effects_ambiguous"
    with pytest.raises(CoordinatorError, match="indeterminate"):
        recover_session(session["id"], db=db)
    assert (
        db.read(
            "SELECT COUNT(*) FROM resource_leases WHERE session_id = ?",
            (session["id"],),
        )[0][0]
        == 1
    )


def test_safe_interrupt_pauses_and_reopens_without_repeating_attempt(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("reopen", {"request": "reopen"}, db=db)
    admitted = admit_session(session["id"], db=db)
    lease = acquire_resource(
        session["id"],
        "change",
        "change:reopen",
        owner_pid=123,
        owner_start_time="worker",
        db=db,
    )
    completed_plan = record_attempt(
        session["id"],
        phase="PLAN",
        round=0,
        attempt_no=1,
        provider="codex",
        model="model",
        effort="high",
        continuation=False,
        status="COMPLETED",
        db=db,
    )
    transitioned = transition_session(
        session["id"],
        "BRAINSTORM",
        expected_version=admitted["session"]["version"],
        fencing_token=admitted["fencing_token"],
        db=db,
    )
    attempt = record_attempt(
        session["id"],
        phase="BRAINSTORM",
        round=0,
        attempt_no=1,
        provider="codex",
        model="model",
        effort="high",
        continuation=False,
        status="RUNNING",
        db=db,
    )
    interrupted = interrupt_session(
        session["id"],
        expected_version=transitioned["version"],
        fencing_token=admitted["fencing_token"],
        safe_boundary=True,
        reason="terminal reopened",
        db=db,
    )
    assert interrupted["status"] == "PAUSED"
    assert interrupted["checkpoint"]["safe_boundary"] is True
    assert (
        db.read("SELECT status FROM attempts WHERE id = ?", (attempt["id"],))[0][
            "status"
        ]
        == "INTERRUPTED"
    )
    assert db.read("SELECT COUNT(*) FROM admission_slots")[0][0] == 0
    assert db.read("SELECT COUNT(*) FROM resource_leases")[0][0] == 0
    assert recovery_report(session["id"], db=db)["reason"] == "safe_boundary_ready"
    reopened = recover_session(session["id"], db=db)
    assert reopened["status"] == "QUEUED"
    assert reopened["phase"] == "BRAINSTORM"
    assert (
        db.read("SELECT status FROM attempts WHERE id = ?", (completed_plan["id"],))[0][
            "status"
        ]
        == "COMPLETED"
    )
    assert [event["event_type"] for event in events_since(session["id"], db=db)] == [
        "provider.attempt.interrupted"
    ]
    assert lease["session_id"] == session["id"]


def test_unsafe_interrupt_blocks_replacement_and_preserves_lease(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("ambiguous", {"request": "ambiguous"}, db=db)
    admitted = admit_session(session["id"], db=db)
    acquire_resource(
        session["id"],
        "change",
        "change:ambiguous",
        owner_pid=123,
        owner_start_time="worker",
        db=db,
    )
    record_attempt(
        session["id"],
        phase="PLAN",
        round=0,
        attempt_no=1,
        provider="codex",
        model="model",
        effort="high",
        continuation=False,
        status="RUNNING",
        db=db,
    )
    interrupted = interrupt_session(
        session["id"],
        expected_version=admitted["session"]["version"],
        fencing_token=admitted["fencing_token"],
        safe_boundary=False,
        db=db,
    )
    assert interrupted["status"] == "BLOCKED"
    report = recovery_report(session["id"], db=db)
    assert report["state"] == "INDETERMINATE"
    with pytest.raises(CoordinatorError, match="indeterminate"):
        recover_session(session["id"], db=db)
    assert db.read("SELECT COUNT(*) FROM resource_leases")[0][0] == 1


def test_coordinator_redacts_secret_bearing_context_and_events(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session(
        "redacted",
        {"request": "token=do-not-persist", "api_key": "do-not-persist"},
        db=db,
    )
    event = append_event(
        session["id"],
        phase="PLAN",
        event_type="log",
        safe_payload={"message": "Authorization: Bearer do-not-persist"},
        db=db,
    )
    assert "do-not-persist" not in str(session["context_json"])
    assert event["safe_payload"]["message"] == "Authorization: <REDACTED>"


def test_operator_question_response_is_session_and_token_scoped(tmp_path: Path):
    db = make_db(tmp_path)
    first = create_session("first", {"request": "first"}, db=db)
    second = create_session("second", {"request": "second"}, db=db)
    first_admission = admit_session(first["id"], capacity=2, db=db)
    second_admission = admit_session(second["id"], capacity=2, db=db)
    record_question(
        first["id"],
        question_id="q1",
        safe_payload={"kind": "approval"},
        expires_at="2099-01-01T00:00:00Z",
        db=db,
    )

    with pytest.raises(StaleVersionError):
        answer_question(
            first["id"],
            "q1",
            "yes",
            fencing_token=second_admission["fencing_token"],
            db=db,
        )
    with pytest.raises(CoordinatorError, match="stale, missing"):
        answer_question(
            first["id"],
            "wrong-question",
            "yes",
            fencing_token=first_admission["fencing_token"],
            db=db,
        )
    assert (
        answer_question(
            first["id"],
            "q1",
            "yes",
            fencing_token=first_admission["fencing_token"],
            db=db,
        )["status"]
        == "ANSWERED"
    )
    assert [event["event_type"] for event in events_since(first["id"], db=db)] == [
        "operator.question",
        "operator.answer",
    ]


def test_operator_question_expiry_is_enforced_atomically(tmp_path: Path):
    db = make_db(tmp_path)
    session = create_session("expired-question", {"request": "expired"}, db=db)
    admission = admit_session(session["id"], db=db)
    record_question(
        session["id"],
        question_id="q1",
        safe_payload={"kind": "approval"},
        expires_at="2000-01-01T00:00:00Z",
        db=db,
    )

    with pytest.raises(CoordinatorError, match="expired"):
        answer_question(
            session["id"], "q1", "yes", fencing_token=admission["fencing_token"], db=db
        )
    question = db.read(
        "SELECT status, response FROM operator_questions WHERE session_id = ? AND question_id = ?",
        (session["id"], "q1"),
    )[0]
    assert question["status"] == "EXPIRED" and question["response"] is None
    assert [event["event_type"] for event in events_since(session["id"], db=db)] == [
        "operator.question",
        "operator.timeout",
    ]
