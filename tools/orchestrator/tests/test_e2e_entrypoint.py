from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from orchestrator.cli import e2e
from orchestrator.core.io import CLIError


def invoke(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["e2e", *args])
    return e2e.main()


def test_e2e_submits_then_resumes_one_change_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    assert invoke(monkeypatch, ["change-a", "fix", "ABC"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["action"] == "submitted"
    session_id = first["session"]["id"]
    assert first["session"]["phase"] == "PLAN"
    assert first["session"]["context_json"]["entrypoint"] == "e2e"

    assert invoke(monkeypatch, ["change-a", "different prompt"]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["action"] == "resumed"
    assert second["session"]["id"] == session_id


def test_e2e_explicit_session_must_match_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    assert invoke(monkeypatch, ["change-a"]) == 0
    session_id = json.loads(capsys.readouterr().out)["session"]["id"]

    with pytest.raises(CLIError, match="another change"):
        invoke(monkeypatch, ["change-b", "--session", session_id])
