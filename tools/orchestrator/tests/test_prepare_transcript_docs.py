from __future__ import annotations

import json
from pathlib import Path

from orchestrator.cli import prepare_transcript_docs as cli


def make_attempt(**overrides: object) -> dict:
    base = {
        "session_id": "sess-1",
        "change": "quant-research",
        "round": 250,
        "phase": "PLAN",
        "attempt_no": 1,
        "provider": "claude",
        "account": "personal-02",
        "status": "COMPLETED",
        "result_class": "success",
        "started_at": "2026-09-04T12:58:14Z",
        "completed_at": "2026-09-04T13:09:37Z",
        "messages": [{"kind": "message", "text": "hi"}],
    }
    base.update(overrides)
    return base


def test_doc_id_matches_artifact_convention():
    attempt = make_attempt(phase="PLAN", attempt_no=3)
    assert cli.doc_id(attempt) == "sess-1-plan-a3"


def test_doc_id_lowercases_phase_and_defaults_missing_phase():
    attempt = make_attempt(phase=None)
    assert cli.doc_id(attempt) == "sess-1-unknown-a1"


def test_write_docs_creates_one_file_per_attempt_holding_a_single_object(
    tmp_path: Path,
):
    attempts = [
        make_attempt(attempt_no=1, phase="PLAN"),
        make_attempt(attempt_no=2, phase="VERIFY"),
    ]
    out_dir = tmp_path / "docs"

    written = cli.write_docs(attempts, out_dir)

    assert {p.name for p in written} == {
        "sess-1-plan-a1.json",
        "sess-1-verify-a2.json",
    }
    for path in written:
        body = json.loads(path.read_text())
        assert isinstance(body, dict)
        assert body["session_id"] == "sess-1"
