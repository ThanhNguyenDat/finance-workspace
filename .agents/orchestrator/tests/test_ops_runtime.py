from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from phase_agent_orchestrator.common import CLIError
from phase_agent_orchestrator import ops_runtime as ops


def test_transition_matrix_preserves_all_allowed_and_rejected_edges() -> None:
    accepted = {"PLAN:IMPLEMENT", "IMPLEMENT:VERIFY", "VERIFY:FINAL_VERIFY", "FIX:VERIFY", "FINAL_VERIFY:RELEASE", "FINAL_VERIFY:ARCHIVE", "RELEASE:DEPLOY_VERIFY", "RELEASE:ARCHIVE", "DEPLOY_VERIFY:ARCHIVE"}
    assert ops.TRANSITIONS == accepted
    all_phases = sorted(ops.PHASES)
    for source in all_phases:
        for target in all_phases:
            assert (f"{source}:{target}" in ops.TRANSITIONS) == (f"{source}:{target}" in accepted)


def prepare_origin_change(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    monkeypatch.setenv("OPS_ROOT", str(tmp_path))
    change = "origin-test"
    session = "session-origin"
    change_dir = tmp_path / ".ops/changes" / change
    (change_dir / "runtime/lock").mkdir(parents=True)
    (tmp_path / "openspec/changes" / change / "specs/capability").mkdir(parents=True)
    for name in ("proposal.md", "design.md", "tasks.md"):
        (tmp_path / "openspec/changes" / change / name).write_text(name)
    (tmp_path / "openspec/changes" / change / "specs/capability/spec.md").write_text("spec")
    (change_dir / "runtime/lock/owner.json").write_text(json.dumps({"session_id": session}))
    (change_dir / "runtime/state.json").write_text(json.dumps({"change": change, "phase": "PLAN", "round": 0, "status": "running", "session_id": session, "routing_policy_version": 1, "attempts": [], "verification_evidence": None}))
    (tmp_path / "research/quant/rounds").mkdir(parents=True)
    (tmp_path / "research/quant/rounds/evidence.md").write_text("evidence")
    return change, session


@pytest.mark.parametrize("artifact", ["research/quant/rounds/../evidence.md", "README.md"])
def test_trace_origin_rejects_traversal_and_outside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, artifact: str) -> None:
    change, session = prepare_origin_change(tmp_path, monkeypatch)
    with pytest.raises(CLIError):
        ops.trace_origin(change, session, "1", "XAU", [artifact])
    assert not (tmp_path / ".ops/changes" / change / "runtime/origin.json").exists()


def test_repo_lock_rechecks_owner_after_existence_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    change_dir = tmp_path / "change"
    (change_dir / "runtime").mkdir(parents=True)
    repositories = [str(tmp_path / "repo-a"), str(tmp_path / "repo-b")]
    locks = {repository: tmp_path / f"lock-{index}" for index, repository in enumerate(repositories)}
    locks[repositories[0]].mkdir()
    monkeypatch.setattr(ops, "change_dir", lambda _change: change_dir)
    monkeypatch.setattr(ops, "assert_active_owner", lambda _change, _session: {})
    monkeypatch.setattr(ops, "canonical_repo", lambda repository: repository)
    monkeypatch.setattr(ops, "repo_lock_dir", lambda repository: locks[repository])
    monkeypatch.setattr(ops, "release_repo_locks", lambda _change, _session: None)

    class SnapshotExecutor:
        def __enter__(self) -> "SnapshotExecutor":
            return self

        def map(self, function: object, values: list[str]) -> list[tuple[str, bool]]:
            return [(value, function(value)) for value in values]  # type: ignore[operator]

        def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
            (locks[repositories[0]] / "owner.json").write_text(json.dumps({"pid": str(os.getpid()), "hostname": ops.socket.gethostname()}))

    monkeypatch.setattr(ops, "ThreadPoolExecutor", lambda **_kwargs: SnapshotExecutor())
    with pytest.raises(ops._ReturnStatus) as error:
        ops.lock_repositories("change", "session", repositories)
    assert error.value.status == 1
    assert "repository lock exists" in capsys.readouterr().err
    assert json.loads((locks[repositories[0]] / "owner.json").read_text())["pid"] == str(os.getpid())
