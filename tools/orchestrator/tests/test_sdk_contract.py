from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
from claude_agent_sdk import ResultMessage
from openai_codex import TurnResult
from openai_codex.generated.v2_all import TurnStatus
from orchestrator.cli import (
    configure_phase_agents,
    detect_codex_availability,
    detect_provider_availability,
)
from orchestrator.coordinator import CoordinatorDB, events_since
from orchestrator.core.fingerprint import fingerprint
from orchestrator.locks import change_lock
from orchestrator.providers.results import classify_sdk_result
from orchestrator.runners import lifecycle as run_phase_agent
from orchestrator.runners import quant as run_phase_agent_command
from orchestrator.runners.phase_adapter import (
    _coordinator_event,
    _operator_permission,
    _run_claude_sdk,
    build_prompt,
)
from orchestrator.runners.quant import _codex
from orchestrator.state import candidates, ops_transaction


def test_sdk_result_mapping_uses_structured_fields() -> None:
    success = ResultMessage("success", 1, 1, False, 1, "session", result="OK")
    budget = ResultMessage(
        "error_max_budget_usd", 1, 1, True, 1, "session", errors=["budget exhausted"]
    )
    rate = ResultMessage(
        "success", 1, 1, True, 1, "session", api_error_status=429, errors=["rate limit"]
    )
    completed = TurnResult(
        "turn", TurnStatus.completed, None, None, None, None, "OK", [], None
    )
    interrupted = TurnResult(
        "turn", TurnStatus.interrupted, None, None, None, None, None, [], None
    )
    assert classify_sdk_result(success, provider="claude") == "success"
    assert classify_sdk_result(budget, provider="claude") == "global-quota-exhausted"
    assert classify_sdk_result(rate, provider="claude") == "transient-rate-limit"
    assert classify_sdk_result(completed, provider="codex") == "success"
    assert classify_sdk_result(interrupted, provider="codex") == "timeout"


def test_prompt_construction_is_stable() -> None:
    prompt = build_prompt("change-name", Path("/tmp/repo"), "PLAN", False)
    assert prompt == (
        "Execute OPS phase PLAN for OpenSpec change change-name in /tmp/repo.\n"
        "Read AGENTS.md, applicable rules/skills, the active change, OPS state and repository-local instructions. Preserve locks, scope, tests, safety and secrets. Do not push or launch another model process.\n"
        "Plan/reconcile OpenSpec only; do not implement runtime code."
    )


def test_fingerprint_matches_legacy_byte_stream(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("new\n", encoding="utf-8")
    (repo / "target").mkdir()
    (repo / "link").symlink_to("target")
    status = subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z"]
    )
    diff = subprocess.check_output(["git", "-C", str(repo), "diff", "--binary", "HEAD"])
    paths = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard", "-z"]
    ).split(b"\0")
    stream = bytearray(status + diff)
    for raw in paths:
        if not raw:
            continue
        relative = raw.decode()
        stream.extend(raw + b"\0")
        path = repo / relative
        if path.is_symlink():
            stream.extend(f"symlink:{path.readlink()}\0".encode())
        else:
            stream.extend(
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}\n".encode()
            )
    assert fingerprint(repo) == hashlib.sha256(stream).hexdigest()


def test_claude_accounts_rotate_with_personal_02_first(
    tmp_path: Path, monkeypatch
) -> None:
    personal = tmp_path / "personal"
    personal_02 = tmp_path / "personal-02"
    personal.mkdir()
    personal_02.mkdir()
    registry = tmp_path / "accounts.yaml"
    registry.write_text(
        f"claude:\n  personal: {personal}\n  personal-02: {personal_02}\ncodex:\n  personal: {tmp_path}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(registry))
    current_lock, state = candidates.with_state()
    try:
        claude = [
            item
            for item in state["phases"]["quant_research"]["candidates"]
            if item["provider"] == "claude"
        ]
        assert [item["account"] for item in claude] == ["personal-02", "personal"]
    finally:
        current_lock.release()


def test_claude_sdk_reads_distinct_account_config_dirs(
    tmp_path: Path, monkeypatch
) -> None:
    cli = Path(__file__).parent / "fixtures/fake_claude_sdk_cli.py"
    cli.chmod(cli.stat().st_mode | stat.S_IXUSR)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cli = fake_bin / "claude"
    shutil.copy2(cli, fake_cli)
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    account_a = tmp_path / "personal-02"
    account_b = tmp_path / "personal"
    account_a.mkdir()
    account_b.mkdir()
    monkeypatch.setenv("CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK", "1")
    monkeypatch.setenv("FAKE_SDK_MODE", "complete")
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    captured: list[str] = []
    for directory in (account_a, account_b):
        stdout = tmp_path / f"{directory.name}.jsonl"
        status, result_class, result = asyncio.run(
            _run_claude_sdk(
                "prompt", "sonnet", "high", tmp_path, tmp_path, directory, stdout, 2
            )
        )
        assert status == 0
        assert result_class == "success"
        captured.append(result.result)
    assert captured == [str(account_a), str(account_b)]


@pytest.mark.parametrize(
    ("mode", "first_result"),
    [("quota-first", "global-quota-exhausted"), ("rate-first", "transient-rate-limit")],
)
def test_quant_claude_rotates_from_personal_02_to_personal(
    tmp_path: Path, monkeypatch, mode: str, first_result: str
) -> None:
    cli = Path(__file__).parent / "fixtures/fake_claude_sdk_cli.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cli = fake_bin / "claude"
    shutil.copy2(cli, fake_cli)
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    personal = tmp_path / "personal"
    personal_02 = tmp_path / "personal-02"
    personal.mkdir()
    personal_02.mkdir()
    registry = tmp_path / "accounts.yaml"
    registry.write_text(
        f"claude:\n  personal: {personal}\n  personal-02: {personal_02}\ncodex:\n  personal: {tmp_path}\n",
        encoding="utf-8",
    )
    root = tmp_path / "workspace"
    (root / ".claude/commands").mkdir(parents=True)
    (root / ".claude/commands/quant-research.md").write_text(
        "fixture quant prompt\n", encoding="utf-8"
    )
    state_dir = root / ".ops/runtime/phase-agents"
    quant_dir = root / ".ops/runtime/quant-research"
    monkeypatch.setenv("QUANT_RESEARCH_ROOT", str(root))
    monkeypatch.setenv("PHASE_AGENT_ROOT", str(root))
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(state_dir))
    monkeypatch.setenv("QUANT_RESEARCH_STATE_DIR", str(quant_dir))
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(registry))
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_SDK_MODE", mode)
    monkeypatch.setenv("CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK", "1")
    monkeypatch.setenv("PHASE_AGENT_QUANT_TIMEOUT_SECONDS", "2")
    candidates.ensure_state()
    assert run_phase_agent_command.run(["quant-research"]) == 0
    current_lock, state = candidates.with_state()
    try:
        expected_available = first_result != "global-quota-exhausted"
        account_state = (
            state["providers"]["claude"]
            .get("accounts", {})
            .get("personal-02", {"available": True})
        )
        assert account_state["available"] is expected_available
    finally:
        current_lock.release()
    run_namespaces = [
        path
        for path in (root / ".ops/runtime/phase-agents/quant-runs").iterdir()
        if path.is_dir()
    ]
    assert len(run_namespaces) == 1
    metas = sorted(run_namespaces[0].glob("*.meta.json"))
    assert [
        json.loads(path.read_text(encoding="utf-8"))["account"] for path in metas
    ] == ["personal-02", "personal"]
    assert (
        json.loads(metas[0].read_text(encoding="utf-8"))["result_class"] == first_result
    )
    db = CoordinatorDB(root=root)
    session_rows = db.read(
        "SELECT id FROM sessions WHERE change_name = 'quant-research'"
    )
    assert len(session_rows) == 1
    event_types = [
        event["event_type"] for event in events_since(session_rows[0]["id"], db=db)
    ]
    assert event_types[:3] == [
        "session.created",
        "session.admitted",
        "provider.attempt.started",
    ]
    assert "provider.stream" in event_types
    assert "provider.result" in event_types
    assert "provider.attempt.completed" in event_types
    assert event_types[-1] == "session.completed"
    status = __import__(
        "orchestrator.coordinator", fromlist=["session_status"]
    ).session_status(session_rows[0]["id"], db=db)
    assert [attempt["status"] for attempt in status["attempts"]] == [
        "FAILED",
        "COMPLETED",
    ]
    assert all(
        event["attempt_id"] is not None
        for event in events_since(session_rows[0]["id"], db=db)
        if event["event_type"].startswith("provider.")
    )
    assert run_phase_agent_command.run(["quant-research"]) == 0
    repeated_rows = db.read(
        "SELECT id, quant_iteration FROM sessions WHERE change_name = 'quant-research'"
    )
    assert len(repeated_rows) == 1
    repeated = __import__(
        "orchestrator.coordinator", fromlist=["session_status"]
    ).session_status(session_rows[0]["id"], db=db)
    assert repeated["session"]["quant_iteration"] == 2
    assert repeated["session"]["checkpoint"]["iteration_history"] == [1]
    assert "session.resumed" in [
        event["event_type"] for event in events_since(session_rows[0]["id"], db=db)
    ]


def test_codex_sdk_adapter_completes_with_protocol_fixture(
    tmp_path: Path, monkeypatch
) -> None:
    cli = Path(__file__).parent / "fixtures/fake_codex_sdk_cli.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cli = fake_bin / "codex"
    shutil.copy2(cli, fake_cli)
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_SDK_MODE", "complete")
    stdout = tmp_path / "codex.jsonl"
    status, result_class, result = _codex(
        "prompt", "gpt-test", "high", tmp_path, None, stdout, 2
    )
    assert status == 0, f"{result_class}: {getattr(result, 'error', result)}"
    assert result_class == "success"
    assert result.status.value == "completed"


def test_codex_fake_quota_preserves_partial_worktree_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    cli = Path(__file__).parent / "fixtures/fake_codex_sdk_cli.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cli = fake_bin / "codex"
    shutil.copy2(cli, fake_cli)
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_CODEX_MODE", "quota-mutate")
    monkeypatch.setenv("FAKE_REPO", str(repository))
    stdout = tmp_path / "codex-quota.jsonl"

    status, result_class, _ = _codex(
        "continue", "gpt-test", "high", repository, None, stdout, 2
    )

    assert status == 1
    assert result_class == "global-quota-exhausted"
    assert (repository / "partial.txt").read_text(encoding="utf-8") == "partial\n"


def test_configure_show_has_stable_table_fixture(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv(
        "PHASE_AGENT_ACCOUNTS_FILE", str(tmp_path / "missing-accounts.yaml")
    )
    candidates.ensure_state()
    configure_phase_agents.show()
    output = capsys.readouterr().out
    expected = """PHASE            MODE     PROVIDER MODEL                    ACCOUNT      EFFORT
quant_research   auto     claude   sonnet                   -            high
quant_research   auto     codex    gpt-5.6-luna             -            high
plan             auto     claude   opus                     -            medium
plan             auto     codex    gpt-5.6-terra            -            high
implement        auto     codex    gpt-5.6-luna             -            high
implement        auto     claude   sonnet                   -            high
verify           auto     claude   opus                     -            medium
verify           auto     codex    gpt-5.6-terra            -            high
fix              auto     codex    gpt-5.6-terra            -            high
fix              auto     codex    gpt-5.6-sol              -            high
fix              auto     claude   opus                     -            high
final_verify     auto     claude   opus                     -            high
final_verify     auto     codex    gpt-5.6-terra            -            high

PROVIDER MODE     AVAILABLE  REASON
codex    auto     true       -
claude   auto     true       -
"""
    assert output == expected


def test_provider_detectors_map_sdk_result_without_cli_parsing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(tmp_path / "phase-state"))
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(tmp_path / "missing.yaml"))
    candidates.ensure_state()
    monkeypatch.setattr(detect_provider_availability, "probe", lambda *args: "success")
    assert detect_provider_availability.main(["claude"]) == 0
    assert capsys.readouterr().out == "available\n"
    monkeypatch.setattr(
        detect_provider_availability, "probe", lambda *args: "global-quota-exhausted"
    )
    assert detect_provider_availability.main(["codex"]) == 0
    assert capsys.readouterr().out == "unavailable\n"


def test_legacy_codex_detector_uses_sdk_probe_result(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setenv("QUANT_RESEARCH_STATE_DIR", str(tmp_path / "quant-state"))
    monkeypatch.setattr(detect_codex_availability.shutil, "which", lambda _: "codex")
    quant_research = detect_codex_availability.quant_research
    quant_research.update_mode("codex-auto")
    capsys.readouterr()
    monkeypatch.setattr(
        detect_codex_availability, "probe", lambda *args: "global-quota-exhausted"
    )
    assert detect_codex_availability.main([]) == 0
    assert capsys.readouterr().out == "unavailable\n"


def test_generic_resolver_calls_claude_sdk_adapter_in_process(
    tmp_path: Path, monkeypatch
) -> None:
    cli = Path(__file__).parent / "fixtures/fake_claude_sdk_cli.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_cli = fake_bin / "claude"
    shutil.copy2(cli, fake_cli)
    fake_cli.chmod(fake_cli.stat().st_mode | stat.S_IXUSR)
    root = tmp_path / "workspace"
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "test@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
    (root / "README.md").write_text("root\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
    monkeypatch.setenv("OPS_ROOT", str(root))
    monkeypatch.setenv("OPS_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("PHASE_AGENT_ROOT", str(root))
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(root / ".ops/runtime/phase-agents"))
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(tmp_path / "missing.yaml"))
    monkeypatch.setenv("PATH", f"{fake_bin}:{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_SDK_MODE", "complete")
    candidates.ensure_state()
    change, session = "sdk-plan", "sdk-session"
    change_lock.lock_change(change, session)
    ops_transaction.init_change(change, session, None, None)
    change_lock.lock_repositories(change, session, [str(root)])
    assert run_phase_agent.run([change, str(root), "PLAN"]) == 0
    state = ops_transaction.read_state(change)
    assert state["attempts"][0]["provider"] == "claude"
    assert state["attempts"][0]["result_class"] == "success"
    coordinator = CoordinatorDB(root=root)
    events = events_since(session, db=coordinator)
    assert [event["event_type"] for event in events] == [
        "provider.attempt.started",
        "provider.stream",
        "provider.result",
        "provider.attempt.completed",
    ]
    assert {event["attempt_id"] for event in events} == {
        state["attempts"][0]["evidence_base"].split("/")[-1].removeprefix("agent-")
    }
    attempt_id = next(iter({event["attempt_id"] for event in events}))
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ROOT", str(root))
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_SESSION_ID", session)
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ATTEMPT_ID", attempt_id)
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_PHASE", "PLAN")
    _coordinator_event({"type": "tool_use", "command": "token=hidden"})
    tool_event = events_since(session, db=coordinator)[-1]
    assert tool_event["event_type"] == "provider.tool"
    assert tool_event["safe_payload"]["command"] == "<REDACTED>"


def test_claude_tool_permission_forwards_only_fenced_operator_answer(
    tmp_path: Path, monkeypatch
) -> None:
    from orchestrator.coordinator import admit_session, answer_question, create_session

    db = CoordinatorDB(root=tmp_path)
    session = create_session("interactive", {"request": "approval"}, db=db)
    admission = admit_session(session["id"], db=db)
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ROOT", str(tmp_path))
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_SESSION_ID", session["id"])
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ATTEMPT_ID", "attempt-1")
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_PHASE", "PLAN")
    monkeypatch.setenv(
        "PHASE_AGENT_COORDINATOR_FENCING_TOKEN", admission["fencing_token"]
    )
    monkeypatch.setenv("PHASE_AGENT_OPERATOR_TIMEOUT_SECONDS", "2")

    async def answer_pending_question() -> object:
        while True:
            pending = db.read(
                "SELECT question_id FROM operator_questions WHERE session_id = ? AND status = 'PENDING'",
                (session["id"],),
            )
            if pending:
                return answer_question(
                    session["id"],
                    pending[0]["question_id"],
                    "allow",
                    fencing_token=admission["fencing_token"],
                    db=db,
                )
            await asyncio.sleep(0.01)

    async def exercise() -> object:
        permission = asyncio.create_task(
            _operator_permission("Bash", {"command": "pytest"}, object())
        )
        await answer_pending_question()
        return await permission

    result = asyncio.run(exercise())
    assert result.behavior == "allow"


def test_claude_tool_permission_expires_without_operator_answer(
    tmp_path: Path, monkeypatch
) -> None:
    from orchestrator.coordinator import admit_session, create_session

    db = CoordinatorDB(root=tmp_path)
    session = create_session("interactive-timeout", {"request": "approval"}, db=db)
    admission = admit_session(session["id"], db=db)
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ROOT", str(tmp_path))
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_SESSION_ID", session["id"])
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_ATTEMPT_ID", "attempt-timeout")
    monkeypatch.setenv("PHASE_AGENT_COORDINATOR_PHASE", "PLAN")
    monkeypatch.setenv(
        "PHASE_AGENT_COORDINATOR_FENCING_TOKEN", admission["fencing_token"]
    )
    monkeypatch.setenv("PHASE_AGENT_OPERATOR_TIMEOUT_SECONDS", "1")

    result = asyncio.run(_operator_permission("Bash", {"command": "pytest"}, object()))

    assert result.behavior == "deny"
    question = db.read(
        "SELECT status, response FROM operator_questions WHERE session_id = ?",
        (session["id"],),
    )[0]
    assert question["status"] == "EXPIRED" and question["response"] is None
    assert [event["event_type"] for event in events_since(session["id"], db=db)] == [
        "operator.question",
        "operator.timeout",
    ]
