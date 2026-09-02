from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import pytest

from phase_agent_orchestrator import common
from phase_agent_orchestrator import ops_runtime as ops


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
