from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import pytest

from phase_agent_orchestrator import common
from phase_agent_orchestrator import ops_runtime as ops
from phase_agent_orchestrator import phase_agent_state as phase_state


def test_atomic_json_write_never_exposes_partial_payload(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    common.atomic_write_json(target, {"version": 0, "payload": "old"})
    payload = "x" * 2_000_000
    stop = threading.Event()
    invalid: list[str] = []

    def reader() -> None:
        while not stop.is_set():
            try:
                value = json.loads(target.read_text())
                if value not in ({"version": 0, "payload": "old"}, {"version": 1, "payload": payload}):
                    invalid.append("unexpected payload")
                    return
            except (FileNotFoundError, json.JSONDecodeError):
                invalid.append("partial payload")
                return

    thread = threading.Thread(target=reader)
    thread.start()
    common.atomic_write_json(target, {"version": 1, "payload": payload})
    stop.set()
    thread.join(timeout=5)
    assert not invalid


@pytest.mark.parametrize("error", [ProcessLookupError(), PermissionError()])
def test_pid_is_alive_treats_lookup_and_permission_errors_as_dead(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    monkeypatch.setattr(common.socket, "gethostname", lambda: "host-a")

    def kill(_pid: int, _signal: int) -> None:
        raise error

    monkeypatch.setattr(common.os, "kill", kill)
    assert not common.pid_is_alive(123, "host-a")


def test_pid_is_alive_requires_exact_hostname_and_accepts_clean_kill(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(common.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(common.os, "kill", lambda _pid, _signal: None)
    assert common.pid_is_alive(123, "host-a")
    assert not common.pid_is_alive(123, "host-b")


def test_phase_attempt_lease_absent_is_not_dead(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    assert not ops.phase_attempt_lease_is_dead(tmp_path)


def test_phase_attempt_lease_dead_pid_is_stale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    lease = tmp_path / "runtime/.phase-attempt-lock"
    lease.mkdir(parents=True)
    (lease / "pid").write_text("456\n")
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(ops, "pid_is_alive", lambda _pid, _host: False)
    assert ops.phase_attempt_lease_is_dead(tmp_path)


@pytest.mark.parametrize("with_lease", [False, True])
@pytest.mark.parametrize("repo_owner", [False, True])
def test_change_and_repo_owner_staleness_scenarios(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, with_lease: bool, repo_owner: bool) -> None:
    owner = tmp_path / ("repo-owner.json" if repo_owner else "owner.json")
    owner.write_text(json.dumps({"pid": str(os.getpid()), "hostname": "host-a"}))
    if with_lease:
        lease = tmp_path / "runtime/.phase-attempt-lock"
        lease.mkdir(parents=True)
        (lease / "pid").write_text("999\n")
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(ops, "pid_is_alive", lambda pid, _host: pid != 999)
    expected_live = not with_lease
    assert ops.owner_is_live(owner, tmp_path) is expected_live


def test_unverifiable_owner_is_manual_release_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    owner = tmp_path / "owner.json"
    owner.write_text(json.dumps({"pid": "123", "hostname": "other-host"}))
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    assert ops.owner_is_live(owner, tmp_path)


@pytest.mark.parametrize("provider", ["claude", "codex"])
def test_account_registry_rejects_unset_and_missing_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, provider: str) -> None:
    _, variable = common.account_environment_name(provider, "work", "phase-agent-state")
    monkeypatch.delenv(variable, raising=False)
    with pytest.raises(common.CLIError, match=f"unregistered account 'work'.*{variable}"):
        common.resolve_account_dir(provider, "work", "phase-agent-state")

    missing = tmp_path / "missing-account"
    monkeypatch.setenv(variable, str(missing))
    with pytest.raises(common.CLIError, match="account 'work'.*directory does not exist"):
        common.resolve_account_dir(provider, "WORK", "phase-agent-state")


def test_account_lock_rejects_live_owner_and_reclaims_dead_owner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    account_dir = tmp_path / "claude-work"
    account_dir.mkdir()
    monkeypatch.setenv("PHASE_AGENT_CLAUDE_ACCOUNT_WORK_DIR", str(account_dir))
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(ops, "pid_is_alive", lambda _pid, _host: True)

    ops.lock_account("claude", "WORK", "123")
    with pytest.raises(ops._ReturnStatus):
        ops.lock_account("claude", "work", "456")

    monkeypatch.setattr(ops, "pid_is_alive", lambda _pid, _host: False)
    ops.lock_account("claude", "work", "456")
    owner = tmp_path / ".ops/runtime/account-locks/claude-work/owner.json"
    assert json.loads(owner.read_text())["pid"] == "456"


def test_account_lock_uses_recorded_owner_change_for_staleness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    account_dir = tmp_path / "claude-work"
    account_dir.mkdir()
    monkeypatch.setenv("PHASE_AGENT_CLAUDE_ACCOUNT_WORK_DIR", str(account_dir))
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    old_change = tmp_path / ".ops/changes/old-change/runtime/.phase-attempt-lock"
    new_change = tmp_path / ".ops/changes/new-change/runtime/.phase-attempt-lock"
    old_change.mkdir(parents=True)
    new_change.mkdir(parents=True)
    (old_change / "pid").write_text("222\n")
    (new_change / "pid").write_text("333\n")
    lock = tmp_path / ".ops/runtime/account-locks/claude-work"
    lock.mkdir(parents=True)
    (lock / "owner.json").write_text(json.dumps({
        "provider": "claude",
        "account": "work",
        "change": "old-change",
        "session_id": "old-session",
        "pid": "123",
        "hostname": "host-a",
    }))
    monkeypatch.setattr(ops.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(ops, "pid_is_alive", lambda pid, _host: pid not in {222, 999})

    ops.lock_account("claude", "work", "456", "new-change", "new-session")

    assert json.loads((lock / "owner.json").read_text())["session_id"] == "new-session"


def test_account_candidate_validation_pin_and_resolution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    work = tmp_path / "claude-work"
    personal = tmp_path / "claude-personal"
    work.mkdir()
    personal.mkdir()
    monkeypatch.setenv("PHASE_AGENT_CLAUDE_ACCOUNT_WORK_DIR", str(work))
    monkeypatch.setenv("PHASE_AGENT_CLAUDE_ACCOUNT_PERSONAL_DIR", str(personal))
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(tmp_path / "phase-state"))

    with pytest.raises(common.CLIError, match="unregistered account 'unknown'"):
        phase_state.validate_candidate("claude", "sonnet", "high", "unknown")

    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "set", "implement", "claude", "sonnet", "high", "work"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "set", "implement", "claude", "sonnet", "high", "unknown"])
    with pytest.raises(common.CLIError, match="unregistered account 'unknown'"):
        phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "candidate-set", "implement", "1", "claude", "sonnet", "high", "personal"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "candidate-set", "implement", "1", "claude", "sonnet", "high", "unknown"])
    with pytest.raises(common.CLIError, match="unregistered account 'unknown'"):
        phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "pin", "implement", "claude", "unknown"])
    with pytest.raises(common.CLIError, match="unregistered account 'unknown'"):
        phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "pin", "implement", "claude", "work"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "auto", "implement"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "provider-result", "claude", "global-quota-exhausted", "work", "0"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "resolve", "implement"])
    phase_state.main()
    assert capsys.readouterr().out.strip() == "claude\tsonnet\thigh\tpersonal"
    state = json.loads((tmp_path / "phase-state/state.json").read_text())
    assert state["providers"]["claude"]["available"] is True
    assert state["providers"]["claude"]["accounts"]["work"]["available"] is False
    assert state["providers"]["claude"].get("accounts", {}).get("personal", {}).get("available", True) is True


def test_account_provider_result_does_not_disable_provider_or_sibling(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    work = tmp_path / "codex-work"
    personal = tmp_path / "codex-personal"
    work.mkdir()
    personal.mkdir()
    monkeypatch.setenv("PHASE_AGENT_CODEX_ACCOUNT_WORK_DIR", str(work))
    monkeypatch.setenv("PHASE_AGENT_CODEX_ACCOUNT_PERSONAL_DIR", str(personal))
    monkeypatch.setenv("PHASE_AGENT_STATE_DIR", str(tmp_path / "phase-state"))

    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "init"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "provider-result", "codex", "success", "personal"])
    phase_state.main()
    monkeypatch.setattr(phase_state.sys, "argv", ["phase-agent-state", "provider-result", "codex", "global-quota-exhausted", "work", "0"])
    phase_state.main()
    state = json.loads((tmp_path / "phase-state/state.json").read_text())
    assert state["providers"]["codex"]["available"] is True
    assert state["providers"]["codex"]["accounts"]["work"]["available"] is False
    assert state["providers"]["codex"]["accounts"]["personal"]["available"] is True
