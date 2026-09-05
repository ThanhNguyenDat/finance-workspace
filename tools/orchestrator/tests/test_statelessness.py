import asyncio
import re
from pathlib import Path

from orchestrator.cli import claude_exec, codex_exec

from .fakes import (
    FakeThread,
    FakeTurnHandle,
    claude_query_fn,
    claude_result,
    codex_factory,
    completed_event,
)

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "orchestrator"
FORBIDDEN_TERMS = (
    "coordinator",
    "lease",
    "account_lock",
    "account_rotation",
    "operator_permission",
    "fencing",
)
CHECKED_FILES = (
    SRC_ROOT / "cli" / "codex_exec.py",
    SRC_ROOT / "cli" / "claude_exec.py",
    SRC_ROOT / "providers" / "codex.py",
    SRC_ROOT / "providers" / "claude.py",
    SRC_ROOT / "providers" / "base.py",
)


def test_no_coordinator_lease_or_account_registry_references() -> None:
    offenders = []
    for path in CHECKED_FILES:
        text = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", text):
                offenders.append((path.name, term))
    assert offenders == []


def test_codex_exec_creates_no_files_outside_cwd(tmp_path) -> None:
    before = set(tmp_path.iterdir())
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    asyncio.run(
        codex_exec.run_turn(
            "hello",
            cwd=str(tmp_path),
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
        )
    )
    after = set(tmp_path.iterdir())
    assert after == before


def test_claude_exec_creates_no_files_outside_cwd(tmp_path) -> None:
    before = set(tmp_path.iterdir())
    messages = [claude_result(is_error=False, result="ok")]
    asyncio.run(
        claude_exec.run_turn(
            "hello",
            cwd=str(tmp_path),
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
        )
    )
    after = set(tmp_path.iterdir())
    assert after == before
