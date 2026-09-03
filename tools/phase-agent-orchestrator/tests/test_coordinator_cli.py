from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from phase_agent_orchestrator.cli import coordinator
from phase_agent_orchestrator.coordinator import CoordinatorDB, append_event, record_attempt, record_question


def invoke(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["coordinator", *args])
    return coordinator.main()


def test_coordinator_cli_submit_resume_status_and_attach(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    assert invoke(monkeypatch, ["submit", "change-a", '{"request":"fix"}']) == 0
    submitted = json.loads(capsys.readouterr().out)
    session = submitted["session"]
    assert submitted["admission"]["admitted"] is True

    assert invoke(monkeypatch, ["status", session["id"]]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["session"]["id"] == session["id"]

    assert invoke(monkeypatch, ["resume", session["id"]]) == 0
    resumed = json.loads(capsys.readouterr().out)
    assert resumed["id"] == session["id"]

    assert invoke(monkeypatch, ["attach", session["id"]]) == 0
    attached = json.loads(capsys.readouterr().out)
    assert attached["events"] == []


def test_coordinator_cli_answer_and_cancel_require_current_fencing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    assert invoke(monkeypatch, ["submit", "change-a"]) == 0
    submitted = json.loads(capsys.readouterr().out)
    session = submitted["admission"]["session"]
    token = submitted["admission"]["fencing_token"]
    record_question(session["id"], question_id="q1", safe_payload={"kind": "approval"}, expires_at="2099-01-01T00:00:00Z", db=CoordinatorDB(root=tmp_path))

    assert invoke(monkeypatch, ["answer", session["id"], "q1", token, "yes"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ANSWERED"

    assert invoke(monkeypatch, ["cancel", session["id"], str(session["version"]), token]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "CANCELLED"


def test_coordinator_cli_monitor_is_redacted_and_session_scoped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    db = CoordinatorDB(root=tmp_path)
    from phase_agent_orchestrator.coordinator import create_session, admit_session
    session = create_session("change-a", {"request": "monitor"}, db=db)
    admit_session(session["id"], db=db)
    attempt = record_attempt(session["id"], phase="PLAN", round=0, attempt_no=1, provider="claude", model="opus", effort="medium", continuation=False, status="RUNNING", db=db)
    append_event(session["id"], phase="PLAN", attempt_id=attempt["id"], event_type="provider.tool", safe_payload={"command": "pytest", "token": "hidden"}, db=db)

    assert invoke(monkeypatch, ["monitor", session["id"]]) == 0
    output = capsys.readouterr().out
    assert "phase=PLAN" in output and "provider=claude" in output and "model=opus" in output
    assert "hidden" not in output and "<REDACTED>" in output
