"""Implementation of .agents/scripts/ops-runtime.sh."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .common import atomic_write_json, die, json_text, pid_is_alive, run_cli, utc_now

PREFIX = "ops-runtime"
SAFE_CHANGE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_ARTIFACT = re.compile(r"^[A-Za-z0-9._/-]+$")


def root_dir() -> Path:
    return Path(os.environ.get("OPS_ROOT", Path(__file__).resolve().parents[4]))


def ops_dir() -> Path:
    return root_dir() / ".ops"


def changes_dir() -> Path:
    return ops_dir() / "changes"


def repo_locks_dir() -> Path:
    return ops_dir() / "runtime/repo-locks"


def usage() -> None:
    print(
        """usage:
  ops-runtime.sh lock <change> <session-id>
  ops-runtime.sh init <change> <session-id> [legacy-backend] [origin]
  ops-runtime.sh unlock <change> <session-id>
  ops-runtime.sh lock-repos <change> <session-id> <repository>...
  ops-runtime.sh unlock-repos <change> <session-id>
  ops-runtime.sh cleanup <change> <session-id> <FAILED|BLOCKED>
  ops-runtime.sh assert-repo-lock <change> <session-id> <repository>
  ops-runtime.sh phase <change> <session-id> <next-phase>
  ops-runtime.sh fix <change> <session-id>
  ops-runtime.sh route <change> <session-id> <IMPLEMENT|FIX>
  ops-runtime.sh record-attempt <change> <session-id> <attempt-json-file>
  ops-runtime.sh trace-origin <change> <session-id> <research-iteration> <instrument> <research-artifact>...
  ops-runtime.sh state <change>
  ops-runtime.sh active <workspace-root> [session-id]
  ops-runtime.sh complete <change> <session-id>""",
        file=sys.stderr,
    )
    raise SystemExit(2)


def valid_change(value: str) -> bool:
    return bool(SAFE_CHANGE.fullmatch(value))


def change_dir(change: str) -> Path:
    if not valid_change(change):
        die(PREFIX, f"invalid change name: {change}")
    return changes_dir() / change


def state_path(change: str) -> Path:
    return change_dir(change) / "runtime/state.json"


PHASES = {"PLAN", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY", "RELEASE", "DEPLOY_VERIFY", "ARCHIVE"}
TRANSITIONS = {"PLAN:IMPLEMENT", "IMPLEMENT:VERIFY", "VERIFY:FINAL_VERIFY", "FIX:VERIFY", "FINAL_VERIFY:RELEASE", "FINAL_VERIFY:ARCHIVE", "RELEASE:DEPLOY_VERIFY", "RELEASE:ARCHIVE", "DEPLOY_VERIFY:ARCHIVE"}


def valid_backend(value: str) -> bool:
    return value in {"codex", "claude-fallback"}


def read_json(path: Path, tolerate_failure: bool = False) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        if tolerate_failure:
            return None
        die(PREFIX, f"could not read JSON: {path}")


def read_state(change: str) -> dict[str, Any]:
    path = state_path(change)
    if not path.is_file():
        die(PREFIX, f"runtime state not found: {path}")
    value = read_json(path)
    if not isinstance(value, dict):
        die(PREFIX, f"runtime state is invalid: {path}")
    return value


def write_state(change: str, state: dict[str, Any]) -> None:
    atomic_write_json(state_path(change), state)


def quant_state_file() -> Path:
    return root_dir() / ".ops/runtime/quant-research/state.json"


def fallback_is_allowed() -> None:
    path = quant_state_file()
    if not path.is_file():
        die(PREFIX, f"quant state not found: {path}")
    state = read_json(path, tolerate_failure=True)
    if not isinstance(state, dict) or state.get("codex_available") is not False:
        die(PREFIX, "Claude fallback requires current quant state codex_available=false")


def canonical_repo(repository: str) -> str:
    if not repository:
        die(PREFIX, "repository path is required")
    result = subprocess.run(["git", "-C", repository, "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if result.returncode != 0 or result.stdout.strip() != "true":
        die(PREFIX, f"not a Git worktree: {repository}")
    result = subprocess.run(["git", "-C", repository, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if result.returncode != 0:
        die(PREFIX, f"cannot resolve Git worktree: {repository}")
    return str(Path(result.stdout.strip()).resolve())


def repo_lock_dir(repository: str) -> Path:
    key = hashlib.sha256(repository.encode()).hexdigest()
    return repo_locks_dir() / key


def lock_anchor_pid() -> str:
    return os.environ.get("CLAUDE_PID") or os.environ.get("CODEX_PID") or ""


def phase_attempt_lease_is_dead(change_path: Path) -> bool:
    pid_file = change_path / "runtime/.phase-attempt-lock/pid"
    if not pid_file.is_file():
        return False
    try:
        value = pid_file.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return value.isdigit() and not pid_is_alive(int(value), socket.gethostname())


def owner_is_live(owner: Path, change_path: Path | None) -> bool:
    if not owner.is_file():
        return False
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict):
        return True
    pid, hostname = value.get("pid"), value.get("hostname")
    if isinstance(pid, str) and pid.isdigit() and hostname == socket.gethostname():
        if not pid_is_alive(int(pid), hostname):
            return False
        if change_path is not None and phase_attempt_lease_is_dead(change_path):
            return False
        return True
    return True


def release_repo_locks(change: str, session_id: str) -> None:
    if not repo_locks_dir().is_dir():
        return
    for owner in list(repo_locks_dir().glob("*/owner.json")):
        value = read_json(owner, tolerate_failure=True)
        if isinstance(value, dict) and value.get("change") == change and value.get("session_id") == session_id:
            lock = owner.parent
            owner.unlink(missing_ok=True)
            try:
                lock.rmdir()
            except OSError:
                pass


def lock_change(change: str, session_id: str) -> None:
    directory = change_dir(change)
    if not session_id:
        die(PREFIX, "session id is required")
    lock = directory / "runtime/lock"
    owner = lock / "owner.json"
    (directory / "runtime/logs").mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        if owner_is_live(owner, directory):
            print(f"ops-runtime: active lock exists: {lock}", file=sys.stderr)
            value = read_json(owner, tolerate_failure=True)
            if isinstance(value, dict):
                print(json_text({key: value.get(key) for key in ("change", "session_id", "pid", "hostname", "started_at")}), file=sys.stderr)
            return_code = 1
            raise _ReturnStatus(return_code)
        print(f"ops-runtime: releasing stale lock (owning process is dead): {lock}", file=sys.stderr)
        shutil.rmtree(lock, ignore_errors=True)
        try:
            lock.mkdir()
        except FileExistsError:
            print(f"ops-runtime: cannot acquire lock after stale release: {lock}", file=sys.stderr)
            raise _ReturnStatus(1)
    atomic_write_json(owner, {"change": change, "session_id": session_id, "pid": lock_anchor_pid(), "hostname": socket.gethostname(), "started_at": utc_now()})


class _ReturnStatus(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


def init_change(change: str, session_id: str, backend: str | None, origin: str | None) -> None:
    directory = change_dir(change)
    state = directory / "runtime/state.json"
    handoff = directory / "handoff.md"
    if not session_id:
        die(PREFIX, "session id is required")
    backend = backend or ""
    origin = origin or ""
    verification_mode = ""
    if backend:
        if not valid_backend(backend):
            die(PREFIX, f"invalid implementation backend: {backend}")
        if backend == "codex" and origin:
            die(PREFIX, "backend origin is invalid")
        if backend == "codex":
            verification_mode = "independent"
        elif origin == "quant-fallback":
            fallback_is_allowed()
            verification_mode = "claude-process-separated-review"
        else:
            die(PREFIX, "Claude fallback requires explicit quant-fallback origin")
    elif origin:
        die(PREFIX, "backend origin is invalid")
    owner = directory / "runtime/lock/owner.json"
    if not owner.is_file():
        die(PREFIX, "change must be locked before initialization")
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or value.get("session_id") != session_id:
        die(PREFIX, "initialization lock is owned by another session")
    if state.exists():
        die(PREFIX, f"runtime state already exists: {state}")
    (directory / "runtime/logs").mkdir(parents=True, exist_ok=True)
    if not backend:
        new_state: dict[str, Any] = {"change": change, "phase": "PLAN", "round": 0, "status": "running", "session_id": session_id, "routing_policy_version": 1, "attempts": [], "verification_evidence": None, "updated_at": utc_now()}
    else:
        new_state = {"change": change, "phase": "PLAN", "round": 0, "status": "running", "session_id": session_id, "implementation_backend": backend, "verification_mode": verification_mode, "updated_at": utc_now()}
    write_state(change, new_state)
    if not handoff.exists():
        handoff.write_text(f"# {change}\n\n- Claude: workflow initialized; planning pending.\n- Next: identify affected repositories and validate the OpenSpec artifacts.\n", encoding="utf-8")


def unlock_change(change: str, session_id: str) -> None:
    lock = change_dir(change) / "runtime/lock"
    owner = lock / "owner.json"
    if not lock.is_dir():
        die(PREFIX, f"lock not found: {lock}")
    if not owner.is_file():
        die(PREFIX, f"lock owner metadata missing: {owner}")
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or value.get("session_id") != session_id:
        die(PREFIX, "lock is owned by another session")
    owner.unlink()
    lock.rmdir()


def assert_active_owner(change: str, session_id: str) -> dict[str, Any]:
    directory = change_dir(change)
    state = read_state(change)
    owner = directory / "runtime/lock/owner.json"
    if not owner.is_file():
        die(PREFIX, "change lock owner metadata missing: " + str(owner))
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or value.get("session_id") != session_id:
        die(PREFIX, "change lock is owned by another session")
    if state.get("status") != "running":
        die(PREFIX, f"change is not active: {change}")
    if state.get("phase") in {"BLOCKED", "FAILED"}:
        die(PREFIX, f"change is terminal: {change}")
    if state.get("session_id") != session_id:
        die(PREFIX, "runtime state is owned by another session")
    if state.get("routing_policy_version") == 1:
        if not isinstance(state.get("attempts"), list) or (state.get("verification_evidence") is not None and not isinstance(state.get("verification_evidence"), dict)):
            die(PREFIX, "runtime state has invalid phase-agent fields")
    else:
        backend = state.get("implementation_backend", "codex")
        mode = state.get("verification_mode", "independent")
        if not valid_backend(backend):
            die(PREFIX, "runtime state has an invalid implementation backend")
        if f"{backend}:{mode}" not in {"codex:independent", "claude-fallback:claude-process-separated-review"}:
            die(PREFIX, "runtime state has an invalid verification mode for its backend")
    return state


def assert_repo_lock(change: str, session_id: str, repository: str) -> None:
    assert_active_owner(change, session_id)
    canonical = canonical_repo(repository)
    owner = repo_lock_dir(canonical) / "owner.json"
    if not owner.is_file():
        die(PREFIX, f"repository lock not found: {canonical}")
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or not (value.get("change") == change and value.get("session_id") == session_id and value.get("repository") == canonical):
        die(PREFIX, f"repository lock is not owned by this change/session: {canonical}")


def lock_repositories(change: str, session_id: str, repositories: list[str]) -> None:
    if not repositories:
        die(PREFIX, "at least one repository is required")
    if not session_id:
        die(PREFIX, "session id is required")
    assert_active_owner(change, session_id)
    canonical_repositories = sorted({canonical_repo(item) for item in repositories})
    directory = change_dir(change)

    def existing_status(repository: str) -> bool:
        return repo_lock_dir(repository).exists()

    with ThreadPoolExecutor(max_workers=max(1, min(8, len(canonical_repositories)))) as pool:
        # This is only an existence pre-check.  The result is deliberately
        # not used as a liveness verdict because the lock can change before
        # the sequential acquisition loop reaches it.
        for _ in pool.map(existing_status, canonical_repositories):
            pass
    for canonical in canonical_repositories:
        lock = repo_lock_dir(canonical)
        owner = lock / "owner.json"
        lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock.mkdir()
        except FileExistsError:
            # The existence snapshot is only an I/O optimization. Another
            # session may have reclaimed and re-acquired the lock since it
            # completed, so liveness must always be evaluated at the steal
            # decision point.
            if owner_is_live(owner, directory):
                print(f"ops-runtime: repository lock exists for {canonical}", file=sys.stderr)
                value = read_json(owner, tolerate_failure=True)
                if isinstance(value, dict):
                    print(json_text({key: value.get(key) for key in ("change", "session_id", "repository", "pid", "started_at")}), file=sys.stderr)
                release_repo_locks(change, session_id)
                raise _ReturnStatus(1)
            print(f"ops-runtime: releasing stale repository lock (owning process is dead): {canonical}", file=sys.stderr)
            shutil.rmtree(lock, ignore_errors=True)
            try:
                lock.mkdir()
            except FileExistsError:
                print(f"ops-runtime: cannot acquire repository lock after stale release: {canonical}", file=sys.stderr)
                release_repo_locks(change, session_id)
                raise _ReturnStatus(1)
        atomic_write_json(owner, {"change": change, "session_id": session_id, "repository": canonical, "pid": lock_anchor_pid(), "hostname": socket.gethostname(), "started_at": utc_now()})


def set_phase(change: str, session_id: str, phase: str) -> None:
    if phase not in PHASES:
        die(PREFIX, f"invalid phase: {phase}")
    state = read_state(change)
    assert_active_owner(change, session_id)
    current = state.get("phase")
    if f"{current}:{phase}" not in TRANSITIONS:
        die(PREFIX, f"invalid phase transition: {current} -> {phase}")
    if current == "FINAL_VERIFY" and phase in {"RELEASE", "ARCHIVE"} and state.get("routing_policy_version") == 1:
        evidence = state.get("verification_evidence")
        if not (isinstance(evidence, dict) and evidence.get("final_result") == "success" and evidence.get("objective_gates_passed") is True and evidence.get("separation") in {"provider-independent", "same-provider-process-separated"}):
            die(PREFIX, "release/archive requires successful derived FINAL_VERIFY evidence")
    state["phase"] = phase
    state["status"] = "running"
    state["updated_at"] = utc_now()
    write_state(change, state)


def set_terminal(change: str, session_id: str, phase: str) -> None:
    if phase not in {"BLOCKED", "FAILED"}:
        die(PREFIX, "invalid terminal phase")
    state = read_state(change)
    assert_active_owner(change, session_id)
    state.update(phase=phase, status="terminal", updated_at=utc_now())
    write_state(change, state)


def cleanup(change: str, session_id: str, phase: str) -> None:
    if phase not in {"BLOCKED", "FAILED"}:
        die(PREFIX, "cleanup accepts only BLOCKED or FAILED")
    assert_active_owner(change, session_id)
    set_terminal(change, session_id, phase)
    release_repo_locks(change, session_id)
    if (change_dir(change) / "runtime/lock").is_dir():
        unlock_change(change, session_id)


def enter_fix(change: str, session_id: str) -> None:
    state = read_state(change)
    assert_active_owner(change, session_id)
    if state.get("phase") not in {"VERIFY", "RELEASE", "DEPLOY_VERIFY"}:
        die(PREFIX, f"FIX cannot start from phase: {state.get('phase')}")
    maximum_text = os.environ.get("OPS_MAX_FIX_ROUNDS", "3")
    if not re.fullmatch(r"[1-9][0-9]*", maximum_text):
        die(PREFIX, "OPS_MAX_FIX_ROUNDS must be a positive integer")
    current = state.get("round")
    if not isinstance(current, int) or isinstance(current, bool) or current < 0:
        die(PREFIX, "runtime fix round is invalid")
    maximum = int(maximum_text)
    if current >= maximum:
        set_terminal(change, session_id, "BLOCKED")
        release_repo_locks(change, session_id)
        if (change_dir(change) / "runtime/lock").is_dir():
            unlock_change(change, session_id)
        print(f"ops-runtime: maximum fix rounds ({maximum}) reached; workflow blocked", file=sys.stderr)
        raise _ReturnStatus(1)
    state["phase"] = "FIX"
    state["round"] = current + 1
    state["status"] = "running"
    state["updated_at"] = utc_now()
    write_state(change, state)


def route(change: str, session_id: str, phase: str) -> None:
    if phase not in {"PLAN", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY"}:
        die(PREFIX, f"invalid route phase: {phase}")
    state = read_state(change)
    assert_active_owner(change, session_id)
    if state.get("phase") != phase:
        die(PREFIX, f"runtime phase is {state.get('phase')}, requested route phase is {phase}")
    if state.get("routing_policy_version") == 1:
        print("phase-agent")
    else:
        if phase not in {"IMPLEMENT", "FIX"}:
            die(PREFIX, "legacy runtime routes only IMPLEMENT/FIX")
        backend = state.get("implementation_backend", "codex")
        if not valid_backend(backend):
            die(PREFIX, "runtime state has an invalid implementation backend")
        print(backend)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def record_attempt(change: str, session_id: str, attempt_file: str) -> None:
    state = read_state(change)
    path = Path(attempt_file)
    if not path.is_file():
        die(PREFIX, f"attempt record not found: {attempt_file}")
    record = read_json(path)
    required = {"attempt", "phase", "round", "provider", "model", "effort", "continuation", "result_class", "exit_status", "worktree_changed", "objective_gates_passed", "process_id", "evidence_base"}
    if not isinstance(record, dict) or not required.issubset(record) or not (is_number(record.get("attempt")) and record["attempt"] >= 1 and record.get("phase") in {"PLAN", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY"} and is_number(record.get("round")) and record.get("provider") in {"codex", "claude"} and isinstance(record.get("model"), str) and isinstance(record.get("effort"), str) and isinstance(record.get("continuation"), bool) and isinstance(record.get("result_class"), str) and is_number(record.get("exit_status")) and isinstance(record.get("worktree_changed"), bool) and isinstance(record.get("objective_gates_passed"), bool) and is_number(record.get("process_id")) and isinstance(record.get("evidence_base"), str)):
        die(PREFIX, "attempt record failed validation")
    attempts = state.get("attempts")
    if state.get("routing_policy_version") != 1 or not isinstance(attempts, list) or record.get("phase") != state.get("phase") or record.get("round") != state.get("round") or any(isinstance(item, dict) and item.get("attempt") == record.get("attempt") for item in attempts):
        die(PREFIX, "attempt does not match active state or already exists")
    attempts.append(record)
    if record["phase"] == "FINAL_VERIFY":
        mutators = [item for item in attempts if isinstance(item, dict) and item.get("phase") in {"IMPLEMENT", "FIX"} and item.get("result_class") == "success"]
        mutator = mutators[-1] if mutators else None
        separation = None if mutator is None else ("provider-independent" if mutator.get("provider") != record.get("provider") else ("same-provider-process-separated" if mutator.get("process_id") != record.get("process_id") else None))
        state["verification_evidence"] = {"mutator_provider": mutator.get("provider") if mutator else None, "verifier_provider": record.get("provider"), "mutator_attempt": mutator.get("attempt") if mutator else None, "verifier_attempt": record.get("attempt"), "separation": separation, "final_result": record.get("result_class"), "objective_gates_passed": record.get("objective_gates_passed")}
    state["updated_at"] = record.get("completed_at")
    write_state(change, state)


def trace_origin(change: str, session_id: str, iteration: str, instrument: str, artifacts: list[str]) -> None:
    if not artifacts:
        die(PREFIX, "at least one research artifact is required")
    if not re.fullmatch(r"[1-9][0-9]*", iteration):
        die(PREFIX, "research iteration must be a positive integer")
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,15}", instrument):
        die(PREFIX, "instrument must be a safe uppercase identifier")
    state = assert_active_owner(change, session_id)
    directory = change_dir(change)
    if state.get("phase") != "PLAN":
        die(PREFIX, "quant origin metadata may be attached only during PLAN")
    origin = directory / "runtime/origin.json"
    if origin.exists():
        die(PREFIX, f"quant origin metadata already exists: {origin}")
    openspec_dir = root_dir() / "openspec/changes" / change
    if not (openspec_dir / "proposal.md").is_file() or not (openspec_dir / "proposal.md").stat().st_size:
        die(PREFIX, "promoted change proposal is missing")
    if not (openspec_dir / "design.md").is_file() or not (openspec_dir / "design.md").stat().st_size:
        die(PREFIX, "promoted change design is missing")
    if not (openspec_dir / "tasks.md").is_file() or not (openspec_dir / "tasks.md").stat().st_size:
        die(PREFIX, "promoted change tasks are missing")
    specs = openspec_dir / "specs"
    if not specs.is_dir() or not any(item.is_file() and item.suffix == ".md" for item in specs.rglob("*")):
        die(PREFIX, "promoted change specs are missing")
    root_canonical = root_dir().resolve()
    approved = (root_canonical / "research/quant/rounds", root_canonical / "research/quant/studies", root_canonical / "research/quant/audits", root_canonical / "research/quant/samples", root_canonical / "research/quant/reports")
    for artifact in artifacts:
        if not SAFE_ARTIFACT.fullmatch(artifact):
            die(PREFIX, f"research artifact path contains unsafe characters: {artifact}")
        wrapped = f"/{artifact}/"
        if "/../" in wrapped or "/./" in wrapped:
            die(PREFIX, f"research artifact path contains traversal: {artifact}")
        if not any(artifact.startswith(str(path.relative_to(root_canonical)) + "/") for path in approved):
            die(PREFIX, f"research artifact is outside approved evidence roots: {artifact}")
        candidate = root_canonical / artifact
        if not candidate.is_file():
            die(PREFIX, f"research artifact not found: {artifact}")
        resolved = candidate.resolve(strict=True)
        if not any(resolved.parent == path or path in resolved.parents for path in approved):
            die(PREFIX, f"research artifact resolves outside approved evidence roots: {artifact}")
    atomic_write_json(origin, {"change": change, "origin": "quant-research", "research_iteration": int(iteration), "instrument": instrument, "research_artifacts": artifacts})


def active_changes(workspace: str, session_id: str) -> None:
    root = Path(workspace)
    directory = root / ".ops/changes"
    if not directory.is_dir():
        return
    for path in sorted(directory.glob("*/runtime/state.json")):
        state = read_json(path, tolerate_failure=True)
        if isinstance(state, dict) and state.get("status") == "running" and state.get("phase") not in {"DONE", "BLOCKED", "FAILED"} and (not session_id or state.get("session_id") == session_id):
            print(f"{state.get('change')}|{state.get('phase')}|{state.get('round')}")


def complete(change: str, session_id: str) -> None:
    directory = change_dir(change)
    state_path_value = directory / "runtime/state.json"
    if not directory.is_dir():
        die(PREFIX, f"change directory not found: {directory}")
    if not state_path_value.is_file():
        die(PREFIX, f"runtime state not found: {state_path_value}")
    state = assert_active_owner(change, session_id)
    if state.get("phase") != "ARCHIVE":
        die(PREFIX, "completion requires ARCHIVE phase")
    destination = ops_dir() / "archive" / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{change}"
    if destination.exists():
        die(PREFIX, f"archive destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    release_repo_locks(change, session_id)
    shutil.move(str(directory), str(destination))
    archived_state = destination / "runtime/state.json"
    archived = read_json(archived_state)
    archived.update(phase="DONE", status="terminal", updated_at=utc_now())
    atomic_write_json(archived_state, archived)
    owner = destination / "runtime/lock/owner.json"
    if not owner.is_file():
        die(PREFIX, "completion lock owner metadata missing after archive")
    value = read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict) or value.get("session_id") != session_id:
        die(PREFIX, "completion lock ownership changed during archive")
    owner.unlink()
    (destination / "runtime/lock").rmdir()
    print(destination)


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    try:
        if command == "lock" and len(args) == 3:
            lock_change(args[1], args[2])
        elif command == "init" and 3 <= len(args) <= 5:
            init_change(args[1], args[2], args[3] if len(args) > 3 else None, args[4] if len(args) > 4 else None)
        elif command == "unlock" and len(args) == 3:
            unlock_change(args[1], args[2])
        elif command == "lock-repos" and len(args) >= 4:
            lock_repositories(args[1], args[2], args[3:])
        elif command == "unlock-repos" and len(args) == 3:
            if not args[2]:
                die(PREFIX, "session id is required")
            release_repo_locks(args[1], args[2])
        elif command == "cleanup" and len(args) == 4:
            cleanup(args[1], args[2], args[3])
        elif command == "assert-repo-lock" and len(args) == 4:
            assert_repo_lock(args[1], args[2], args[3])
        elif command == "phase" and len(args) == 4:
            set_phase(args[1], args[2], args[3])
        elif command == "fix" and len(args) == 3:
            enter_fix(args[1], args[2])
        elif command == "route" and len(args) == 4:
            route(args[1], args[2], args[3])
        elif command == "record-attempt" and len(args) == 4:
            record_attempt(args[1], args[2], args[3])
        elif command == "trace-origin" and len(args) >= 6:
            trace_origin(args[1], args[2], args[3], args[4], args[5:])
        elif command == "state" and len(args) == 2:
            path = state_path(args[1])
            try:
                print(path.read_text(encoding="utf-8"), end="")
            except OSError:
                die(PREFIX, f"runtime state not found: {path}")
        elif command == "active" and 2 <= len(args) <= 3:
            active_changes(args[1], args[2] if len(args) == 3 else "")
        elif command in {"complete", "archive"} and len(args) == 3:
            complete(args[1], args[2])
        else:
            usage()
    except _ReturnStatus as status:
        return status.status
    return 0


if __name__ == "__main__":
    run_cli(main, PREFIX)
