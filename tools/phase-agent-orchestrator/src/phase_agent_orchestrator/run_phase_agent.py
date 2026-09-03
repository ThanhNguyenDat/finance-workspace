"""Generic phase resolver with direct Python calls between orchestration layers."""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path
from typing import Iterator

from .classify_result import RESULT_CLASSES
from .detect_provider_availability import probe
from .fingerprint import fingerprint
from .io import CLIError, atomic_write_json, run_cli, utc_now
from .locks.directory_lock import PidDirectoryLock
from .state import candidates, ops_transaction

PREFIX = "run-phase-agent"
PHASES = {"PLAN", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY"}
RETRYABLE = {"global-quota-exhausted", "auth-error", "model-unavailable", "model-specific-limit", "transient-rate-limit"}


@contextlib.contextmanager
def _environment(values: dict[str, str]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in values}
    present = {key: key in os.environ for key in values}
    try:
        for key, value in values.items():
            if value:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
        yield
    finally:
        for key in values:
            if present[key]:
                os.environ[key] = previous[key] or ""
            else:
                os.environ.pop(key, None)


def _state_and_candidates(phase: str) -> tuple[dict, list[dict]]:
    current_lock, state = candidates.with_state()
    try:
        phase_state = state["phases"][phase.lower()]
        return state, list(phase_state["candidates"])
    finally:
        current_lock.release()


def _override_candidates(phase: str) -> list[dict] | None:
    prefix = f"PHASE_AGENT_{phase}_"
    provider = os.environ.get(prefix + "PROVIDER", os.environ.get("PHASE_AGENT_PROVIDER", ""))
    model = os.environ.get(prefix + "MODEL", os.environ.get("PHASE_AGENT_MODEL", ""))
    effort = os.environ.get(prefix + "EFFORT", os.environ.get("PHASE_AGENT_EFFORT", ""))
    account = os.environ.get(prefix + "ACCOUNT", os.environ.get("PHASE_AGENT_ACCOUNT", ""))
    if not any((provider, model, effort, account)):
        return None
    if not all((provider, model, effort)):
        raise CLIError(f"{PREFIX}: provider/model/effort overrides must be supplied together")
    candidates.validate_candidate(provider, model, effort, account or None)
    item = {"provider": provider, "model": model, "effort": effort}
    if account:
        item["account"] = account.lower()
    return [item]


def _available(state: dict, item: dict) -> bool:
    provider = item["provider"]
    account = item.get("account")
    if account:
        return state["providers"][provider].get("accounts", {}).get(account, {}).get("available", True)
    return state["providers"][provider].get("available", False)


def _probe_if_due(provider: str, state: dict) -> None:
    if not candidates.probe_due(provider, None):
        return
    options = next((item for phase in state["phases"].values() for item in phase["candidates"] if item["provider"] == provider), None)
    if options is None:
        return
    try:
        result = probe(provider, options["model"], options["effort"], int(os.environ.get("PHASE_AGENT_PROBE_TIMEOUT_SECONDS", "30")))
    except BaseException:
        result = "unknown-error"
    if result in {"success", "global-quota-exhausted", "auth-error"}:
        candidates.mutate("provider-result", ["provider-result", provider, result])
    else:
        candidates.mutate("provider-result", ["provider-result", provider, "probe-inconclusive", os.environ.get("PHASE_AGENT_PROBE_COOLDOWN_SECONDS", "3600")])


def _objective_gate(path: Path) -> bool:
    required = {"FINAL_VERIFY_GATE: PASS", "P0_FINDINGS: 0", "P1_FINDINGS: 0", "OBJECTIVE_GATES: PASS"}
    try:
        return required.issubset(set(path.read_text(encoding="utf-8").splitlines()))
    except OSError:
        return False


def _run_attempt(change: str, repository: str, phase: str, item: dict, continuation: bool, state: dict, state_file: Path, runtime_dir: Path, workspace: Path) -> tuple[int, str, bool]:
    attempt = len(state.get("attempts", [])) + 1
    round_value = state.get("round", 0)
    attempt_id = f"{phase.lower()}-r{round_value}-a{attempt}-{os.getpid()}"
    base = runtime_dir / "logs" / f"agent-{attempt_id}"
    repository_root = Path(_git_root(repository))
    before = (fingerprint(workspace), fingerprint(repository_root))
    head_before = _git_head(repository_root)
    started_at = utc_now()
    env = {
        "PHASE_AGENT_MODEL": item["model"],
        "PHASE_AGENT_EFFORT": item["effort"],
        "PHASE_AGENT_ACCOUNT": item.get("account", ""),
        "PHASE_AGENT_ATTEMPT_ID": attempt_id,
        "PHASE_AGENT_CONTINUATION": "true" if continuation else "false",
        "PHASE_AGENT_EVIDENCE_BASE": str(base),
    }
    with _environment(env):
        if item["provider"] == "claude":
            from .run_claude_phase import main as adapter_main
        else:
            from .run_codex_phase import main as adapter_main
        status = adapter_main([change, repository, phase])
    result_file = base.with_suffix(".result-class")
    result = result_file.read_text(encoding="utf-8").strip() if result_file.is_file() else "unknown-error"
    last_file = base.with_suffix(".last-message.md")
    if phase == "FINAL_VERIFY" and status == 0 and not _objective_gate(last_file):
        status, result = 1, "implementation-error"
        base.with_suffix(".stderr.log").open("a", encoding="utf-8").write("FINAL_VERIFY did not provide a passing objective-gate attestation\n")
        base.with_suffix(".exit").write_text("1\n", encoding="utf-8")
        result_file.write_text("implementation-error\n", encoding="utf-8")
    after = (fingerprint(workspace), fingerprint(repository_root))
    head_after = _git_head(repository_root)
    changed = before != after or head_before != head_after
    record = {
        "attempt": attempt,
        "phase": phase,
        "round": round_value,
        "provider": item["provider"],
        "model": item["model"],
        "effort": item["effort"],
        **({"account": item["account"]} if item.get("account") else {}),
        "continuation": continuation,
        "result_class": result,
        "exit_status": status,
        "worktree_changed": changed,
        "process_id": os.getpid(),
        "objective_gates_passed": phase == "FINAL_VERIFY" and status == 0,
        "started_at": started_at,
        "completed_at": utc_now(),
        "head_before": head_before,
        "head_after": head_after,
        "evidence_base": str(base.relative_to(Path(os.environ.get("OPS_ROOT", workspace)))) if base.is_relative_to(Path(os.environ.get("OPS_ROOT", workspace))) else str(base),
    }
    attempt_path = base.with_suffix(".attempt.json")
    atomic_write_json(attempt_path, record)
    ops_transaction.record_attempt(change, state["session_id"], str(attempt_path))
    return status, result, changed


def _git_head(repository: Path) -> str:
    import subprocess

    return subprocess.check_output(["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip()


def run(argv: list[str]) -> int:
    if len(argv) != 3:
        raise CLIError(f"{PREFIX}: usage: run-phase-agent.sh <change> <repository> <PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY>")
    change, repository, phase = argv
    if phase not in PHASES:
        raise CLIError(f"{PREFIX}: unsupported phase")
    runtime_state, state_file, session_id, round_value, workspace, runtime_dir = _read_runtime(change, repository)
    lease = PidDirectoryLock(runtime_dir / ".phase-attempt-lock", PREFIX)
    lease.acquire()
    try:
        override = _override_candidates(phase)
        _, options = _state_and_candidates(phase.lower())
        options = override or options
        continuation = False
        selected = False
        last_status = 1
        for item in options:
            candidates.validate_candidate(item["provider"], item["model"], item["effort"], item.get("account"))
            current_state, _ = _state_and_candidates(phase.lower())
            phase_state = current_state["phases"][phase.lower()]
            if override is None and phase_state["mode"] == "manual" and phase_state.get("pinned_provider") != item["provider"]:
                continue
            if not _available(current_state, item) and not item.get("account"):
                _probe_if_due(item["provider"], current_state)
                current_state, _ = _state_and_candidates(phase.lower())
            if not _available(current_state, item):
                continue
            selected = True
            status, result, changed = _run_attempt(change, repository, phase, item, continuation, runtime_state, state_file, runtime_dir, workspace)
            runtime_state = ops_transaction.read_state(change)
            last_status = status
            if status == 0:
                print(f"Phase agent {phase} completed with {item['provider']}")
                return 0
            if result not in RETRYABLE:
                return status
            if changed and phase in {"PLAN", "IMPLEMENT", "FIX"}:
                continuation = True
        if not selected:
            raise CLIError(f"{PREFIX}: no eligible candidate for {phase}")
        return last_status
    finally:
        lease.release()


def _read_runtime(change: str, repository: str) -> tuple[dict, Path, str, int, Path, Path]:
    state_file = ops_transaction.state_path(change)
    state = ops_transaction.assert_active_owner(change, _read_session(state_file))
    if state.get("phase") not in PHASES:
        raise CLIError(f"{PREFIX}: phase mismatch")
    workspace = Path(os.environ.get("OPS_WORKSPACE_ROOT", ops_transaction.root_dir())).resolve()
    repository_root = Path(_git_root(repository))
    change_lock = __import__("phase_agent_orchestrator.locks.change_lock", fromlist=["assert_repo_lock"])
    change_lock.assert_repo_lock(change, state["session_id"], str(repository_root))
    runtime_dir = state_file.parent
    runtime_dir.joinpath("logs").mkdir(parents=True, exist_ok=True)
    return state, state_file, state["session_id"], state.get("round", 0), workspace, runtime_dir


def _read_session(state_file: Path) -> str:
    import json

    try:
        return str(json.loads(state_file.read_text(encoding="utf-8"))["session_id"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise CLIError(f"{PREFIX}: missing session id") from error


def _git_root(repository: str) -> str:
    import subprocess

    return subprocess.check_output(["git", "-C", repository, "rev-parse", "--show-toplevel"], text=True).strip()


def main(argv: list[str] | None = None) -> int:
    return run(list(argv if argv is not None else sys.argv[1:]))


if __name__ == "__main__":
    run_cli(lambda: main(), PREFIX)
