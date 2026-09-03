from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import pytest
import yaml
from orchestrator.accounts import registry
from orchestrator.cli import agent_role_state as role_cli
from orchestrator.core import io
from orchestrator.locks import account_lock, change_lock, pid_liveness
from orchestrator.state import candidates


def configure_accounts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    accounts: dict[str, dict[str, str]],
) -> Path:
    path = tmp_path / "accounts.yaml"
    path.write_text(yaml.safe_dump(accounts, sort_keys=True), encoding="utf-8")
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(path))
    return path


def test_atomic_json_write_never_exposes_partial_payload(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    io.atomic_write_json(target, {"version": 0, "payload": "old"})
    payload = "x" * 2_000_000
    stop = threading.Event()
    invalid: list[str] = []

    def reader() -> None:
        while not stop.is_set():
            try:
                value = json.loads(target.read_text())
                if value not in (
                    {"version": 0, "payload": "old"},
                    {"version": 1, "payload": payload},
                ):
                    invalid.append("unexpected payload")
                    return
            except FileNotFoundError, json.JSONDecodeError:
                invalid.append("partial payload")
                return

    thread = threading.Thread(target=reader)
    thread.start()
    io.atomic_write_json(target, {"version": 1, "payload": payload})
    stop.set()
    thread.join(timeout=5)
    assert not invalid


@pytest.mark.parametrize("error", [ProcessLookupError(), PermissionError()])
def test_pid_is_alive_treats_lookup_and_permission_errors_as_dead(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    monkeypatch.setattr(pid_liveness.socket, "gethostname", lambda: "host-a")

    def kill(_pid: int, _signal: int) -> None:
        raise error

    monkeypatch.setattr(pid_liveness.os, "kill", kill)
    assert not pid_liveness.pid_is_alive(123, "host-a")


def test_pid_is_alive_requires_exact_hostname_and_accepts_clean_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pid_liveness.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(pid_liveness.os, "kill", lambda _pid, _signal: None)
    assert pid_liveness.pid_is_alive(123, "host-a")
    assert not pid_liveness.pid_is_alive(123, "host-b")


def test_phase_attempt_lease_absent_is_not_dead(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    assert not change_lock.phase_attempt_lease_is_dead(tmp_path)


def test_phase_attempt_lease_dead_pid_is_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lease = tmp_path / "runtime/.phase-attempt-lock"
    lease.mkdir(parents=True)
    (lease / "pid").write_text("456\n")
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(change_lock, "pid_is_alive", lambda _pid, _host: False)
    assert change_lock.phase_attempt_lease_is_dead(tmp_path)


@pytest.mark.parametrize("with_lease", [False, True])
@pytest.mark.parametrize("repo_owner", [False, True])
def test_change_and_repo_owner_staleness_scenarios(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, with_lease: bool, repo_owner: bool
) -> None:
    owner = tmp_path / ("repo-owner.json" if repo_owner else "owner.json")
    owner.write_text(json.dumps({"pid": str(os.getpid()), "hostname": "host-a"}))
    if with_lease:
        lease = tmp_path / "runtime/.phase-attempt-lock"
        lease.mkdir(parents=True)
        (lease / "pid").write_text("999\n")
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(change_lock, "pid_is_alive", lambda pid, _host: pid != 999)
    expected_live = not with_lease
    assert change_lock.owner_is_live(owner, tmp_path) is expected_live


def test_unverifiable_owner_is_manual_release_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    owner = tmp_path / "owner.json"
    owner.write_text(json.dumps({"pid": "123", "hostname": "other-host"}))
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    assert change_lock.owner_is_live(owner, tmp_path)


@pytest.mark.parametrize("provider", ["claude", "codex"])
def test_account_registry_rejects_unset_and_missing_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, provider: str
) -> None:
    accounts_file = tmp_path / "accounts.yaml"
    monkeypatch.setenv("PHASE_AGENT_ACCOUNTS_FILE", str(accounts_file))
    with pytest.raises(io.CLIError, match="accounts registry file does not exist"):
        registry.resolve_account_dir(provider, "work", "agent-role-state")

    other_provider = "codex" if provider == "claude" else "claude"
    configure_accounts(tmp_path, monkeypatch, {other_provider: {"work": str(tmp_path)}})
    with pytest.raises(
        io.CLIError, match=f"no accounts configured for provider {provider}"
    ):
        registry.resolve_account_dir(provider, "work", "agent-role-state")

    account_dir = tmp_path / "account"
    account_dir.mkdir()
    configure_accounts(
        tmp_path, monkeypatch, {provider: {"personal": str(account_dir)}}
    )
    with pytest.raises(
        io.CLIError, match=f"account 'work' not found under provider {provider}"
    ):
        registry.resolve_account_dir(provider, "work", "agent-role-state")

    missing = tmp_path / "missing-account"
    configure_accounts(tmp_path, monkeypatch, {provider: {"work": str(missing)}})
    with pytest.raises(io.CLIError, match="account 'work'.*directory does not exist"):
        registry.resolve_account_dir(provider, "WORK", "agent-role-state")


def test_account_lock_rejects_live_owner_and_reclaims_dead_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    account_dir = tmp_path / "claude-work"
    account_dir.mkdir()
    configure_accounts(tmp_path, monkeypatch, {"claude": {"work": str(account_dir)}})
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(change_lock, "pid_is_alive", lambda _pid, _host: True)

    account_lock.lock_account("claude", "WORK", "123")
    with pytest.raises(account_lock._ReturnStatus):
        account_lock.lock_account("claude", "work", "456")

    monkeypatch.setattr(change_lock, "pid_is_alive", lambda _pid, _host: False)
    account_lock.lock_account("claude", "work", "456")
    owner = tmp_path / ".ops/runtime/account-locks/claude-work/owner.json"
    assert json.loads(owner.read_text())["pid"] == "456"


def test_account_lock_uses_recorded_owner_change_for_staleness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    account_dir = tmp_path / "claude-work"
    account_dir.mkdir()
    configure_accounts(tmp_path, monkeypatch, {"claude": {"work": str(account_dir)}})
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    old_change = tmp_path / ".ops/changes/old-change/runtime/.phase-attempt-lock"
    new_change = tmp_path / ".ops/changes/new-change/runtime/.phase-attempt-lock"
    old_change.mkdir(parents=True)
    new_change.mkdir(parents=True)
    (old_change / "pid").write_text("222\n")
    (new_change / "pid").write_text("333\n")
    lock = tmp_path / ".ops/runtime/account-locks/claude-work"
    lock.mkdir(parents=True)
    (lock / "owner.json").write_text(
        json.dumps(
            {
                "provider": "claude",
                "account": "work",
                "change": "old-change",
                "session_id": "old-session",
                "pid": "123",
                "hostname": "host-a",
            }
        )
    )
    monkeypatch.setattr(change_lock.socket, "gethostname", lambda: "host-a")
    monkeypatch.setattr(
        change_lock, "pid_is_alive", lambda pid, _host: pid not in {222, 999}
    )

    account_lock.lock_account("claude", "work", "456", "new-change", "new-session")

    assert json.loads((lock / "owner.json").read_text())["session_id"] == "new-session"


def test_account_candidate_validation_pin_and_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    work = tmp_path / "claude-work"
    personal = tmp_path / "claude-personal"
    work.mkdir()
    personal.mkdir()
    configure_accounts(
        tmp_path,
        monkeypatch,
        {"claude": {"work": str(work), "personal": str(personal)}},
    )
    monkeypatch.setenv("AGENT_ROLE_STATE_DIR", str(tmp_path / "role-state"))

    with pytest.raises(
        io.CLIError, match="account 'unknown' not found under provider claude"
    ):
        candidates.validate_candidate("claude", "sonnet", "high", "unknown")

    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        ["agent-role-state", "set", "implement", "claude", "sonnet", "high", "work"],
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        [
            "agent-role-state",
            "set",
            "implement",
            "claude",
            "sonnet",
            "high",
            "unknown",
        ],
    )
    with pytest.raises(
        io.CLIError, match="account 'unknown' not found under provider claude"
    ):
        role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        [
            "agent-role-state",
            "candidate-set",
            "implement",
            "1",
            "claude",
            "sonnet",
            "high",
            "personal",
        ],
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        [
            "agent-role-state",
            "candidate-set",
            "implement",
            "1",
            "claude",
            "sonnet",
            "high",
            "unknown",
        ],
    )
    with pytest.raises(
        io.CLIError, match="account 'unknown' not found under provider claude"
    ):
        role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        ["agent-role-state", "pin", "implement", "claude", "unknown"],
    )
    with pytest.raises(
        io.CLIError, match="account 'unknown' not found under provider claude"
    ):
        role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        ["agent-role-state", "pin", "implement", "claude", "work"],
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys, "argv", ["agent-role-state", "auto", "implement"]
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        [
            "agent-role-state",
            "provider-result",
            "claude",
            "global-quota-exhausted",
            "work",
            "0",
        ],
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys, "argv", ["agent-role-state", "resolve", "implement"]
    )
    role_cli.main()
    assert capsys.readouterr().out.strip() == "claude\tsonnet\thigh\tpersonal"
    state = json.loads((tmp_path / "role-state/state.json").read_text())
    assert state["providers"]["claude"]["available"] is True
    assert state["providers"]["claude"]["accounts"]["work"]["available"] is False
    assert (
        state["providers"]["claude"]
        .get("accounts", {})
        .get("personal", {})
        .get("available", True)
        is True
    )


def test_account_provider_result_does_not_disable_provider_or_sibling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = tmp_path / "codex-work"
    personal = tmp_path / "codex-personal"
    work.mkdir()
    personal.mkdir()
    configure_accounts(
        tmp_path, monkeypatch, {"codex": {"work": str(work), "personal": str(personal)}}
    )
    monkeypatch.setenv("AGENT_ROLE_STATE_DIR", str(tmp_path / "role-state"))

    monkeypatch.setattr(role_cli.sys, "argv", ["agent-role-state", "init"])
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        ["agent-role-state", "provider-result", "codex", "success", "personal"],
    )
    role_cli.main()
    monkeypatch.setattr(
        role_cli.sys,
        "argv",
        [
            "agent-role-state",
            "provider-result",
            "codex",
            "global-quota-exhausted",
            "work",
            "0",
        ],
    )
    role_cli.main()
    state = json.loads((tmp_path / "role-state/state.json").read_text())
    assert state["providers"]["codex"]["available"] is True
    assert state["providers"]["codex"]["accounts"]["work"]["available"] is False
    assert state["providers"]["codex"]["accounts"]["personal"]["available"] is True


def test_state_validation_tolerates_unresolvable_historical_account(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state_dir = tmp_path / "role-state"
    monkeypatch.setenv("AGENT_ROLE_STATE_DIR", str(state_dir))
    monkeypatch.delenv("PHASE_AGENT_ACCOUNTS_FILE", raising=False)

    monkeypatch.setattr(role_cli.sys, "argv", ["agent-role-state", "init"])
    role_cli.main()
    state_path = state_dir / "state.json"
    state = json.loads(state_path.read_text())
    state["providers"]["claude"]["accounts"] = {
        "stale": candidates.availability_record()
    }
    io.atomic_write_json(state_path, state)

    assert candidates.state_valid(json.loads(state_path.read_text()))
    for argv in (
        ["agent-role-state", "state"],
        ["agent-role-state", "auto", "plan"],
        ["agent-role-state", "set", "plan", "codex", "safe-model", "high"],
        ["agent-role-state", "pin", "plan", "codex"],
    ):
        monkeypatch.setattr(role_cli.sys, "argv", argv)
        assert role_cli.main() == 0

    assert (
        "stale" in json.loads(state_path.read_text())["providers"]["claude"]["accounts"]
    )
