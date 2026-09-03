from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path

from orchestrator.coordinator import (
    CoordinatorDB,
    acquire_resource,
    admit_session,
    append_event,
    archive_session,
    create_session,
    events_since,
    get_session,
    record_archive_attestation,
    record_attempt,
    record_verification_findings,
    release_admission,
    release_resource,
    transition_session,
    update_attempt,
)
from orchestrator.runners.quant import _codex


def test_read_only_lifecycle_smoke_records_fake_provider_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    fake_cli = tmp_path / "bin/codex"
    fake_cli.parent.mkdir()
    shutil.copy2(
        Path(__file__).parent / "fixtures/fake_codex_sdk_cli.py",
        fake_cli,
    )
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{fake_cli.parent}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_SDK_MODE", "complete")

    db = CoordinatorDB(root=tmp_path)
    session = create_session(
        "smoke-change",
        {"request": "read-only lifecycle smoke"},
        db=db,
    )
    session_id = session["id"]
    append_event(
        session_id,
        phase="PLAN",
        event_type="session.created",
        safe_payload={"entrypoint": "smoke"},
        db=db,
    )
    admission = admit_session(
        session_id,
        db=db,
        owner_pid=os.getpid(),
        owner_start_time="smoke",
    )
    admission_token = admission["fencing_token"]
    append_event(
        session_id,
        phase="PLAN",
        event_type="session.admitted",
        safe_payload={"slot_id": admission["slot_id"]},
        db=db,
    )
    change_lease = acquire_resource(
        session_id,
        "change",
        "change:smoke-change",
        owner_pid=os.getpid(),
        owner_start_time="smoke",
        db=db,
    )
    account_lease = acquire_resource(
        session_id,
        "account",
        "codex/personal",
        owner_pid=os.getpid(),
        owner_start_time="smoke",
        db=db,
    )

    for next_phase in ("BRAINSTORM", "IMPLEMENT"):
        current = get_session(session_id, db=db)
        assert current is not None
        transition_session(
            session_id,
            next_phase,
            expected_version=current["version"],
            fencing_token=admission_token,
            db=db,
        )
        append_event(
            session_id,
            phase=next_phase,
            event_type="phase.entered",
            safe_payload={"phase": next_phase},
            db=db,
        )

    attempt = record_attempt(
        session_id,
        phase="IMPLEMENT",
        round=0,
        attempt_no=1,
        provider="codex",
        account="personal",
        model="gpt-test",
        effort="high",
        continuation=False,
        status="RUNNING",
        db=db,
    )
    append_event(
        session_id,
        phase="IMPLEMENT",
        event_type="provider.attempt.started",
        attempt_id=attempt["id"],
        safe_payload={"provider": "codex", "model": "gpt-test"},
        db=db,
    )
    log_path = tmp_path / "evidence/codex.jsonl"
    status, result_class, result = _codex(
        "smoke prompt",
        "gpt-test",
        "high",
        tmp_path,
        None,
        log_path,
        5,
    )
    assert status == 0
    assert result_class == "success"
    assert getattr(result, "status", None).value == "completed"
    assert log_path.is_file()
    update_attempt(
        session_id,
        attempt["id"],
        status="COMPLETED",
        result_class=result_class,
        evidence_path=str(log_path),
        db=db,
    )
    append_event(
        session_id,
        phase="IMPLEMENT",
        event_type="provider.attempt.completed",
        attempt_id=attempt["id"],
        safe_payload={"result_class": result_class},
        db=db,
    )

    current = get_session(session_id, db=db)
    assert current is not None
    transition_session(
        session_id,
        "VERIFY",
        expected_version=current["version"],
        fencing_token=admission_token,
        db=db,
    )
    current = get_session(session_id, db=db)
    assert current is not None
    verified = record_verification_findings(
        session_id,
        [],
        expected_version=current["version"],
        fencing_token=admission_token,
        db=db,
    )
    attested = record_archive_attestation(
        session_id,
        {
            "verification_passed": True,
            "objective_gates_passed": True,
            "release_gates_passed": True,
        },
        expected_version=verified["version"],
        fencing_token=admission_token,
        db=db,
    )
    release_resource("account", "codex/personal", account_lease["fencing_token"], db=db)
    release_resource(
        "change", "change:smoke-change", change_lease["fencing_token"], db=db
    )
    release_admission(session_id, admission_token, db=db)

    current = get_session(session_id, db=db)
    assert current is not None
    archived_phase = transition_session(
        session_id,
        "ARCHIVE",
        expected_version=current["version"],
        db=db,
    )
    archived = archive_session(session_id, db=db)

    assert archived_phase["phase"] == "ARCHIVE"
    assert archived["status"] == "COMPLETED"
    assert (
        archived["checkpoint"]["archive_attestation"]
        == attested["checkpoint"]["archive_attestation"]
    )
    assert db.read("SELECT COUNT(*) FROM admission_slots")[0][0] == 0
    assert db.read("SELECT COUNT(*) FROM resource_leases")[0][0] == 0
    attempts = db.read(
        "SELECT status, result_class, evidence_path FROM attempts WHERE session_id = ?",
        (session_id,),
    )
    assert [dict(row) for row in attempts] == [
        {
            "status": "COMPLETED",
            "result_class": "success",
            "evidence_path": str(log_path),
        }
    ]
    events = events_since(session_id, db=db)
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    assert all(
        event["attempt_id"] == attempt["id"]
        for event in events
        if event["event_type"].startswith("provider.attempt.")
    )
    evidence_path = tmp_path / archived["checkpoint"]["archive_evidence"]
    assert evidence_path.is_file()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["session"]["phase"] == "ARCHIVE"
    assert evidence["session"]["status"] == "RUNNING"
    assert "fencing_token" not in evidence["session"]
    assert "lease_owner" not in evidence["session"]
