"""Persistent OPS transaction state and phase transitions."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..core.io import atomic_write_json, die, utc_now
from ..locks import change_lock

PREFIX = "ops-runtime"
SAFE_CHANGE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_ARTIFACT = re.compile(r"^[A-Za-z0-9._/-]+$")
PHASES = {
    "PLAN",
    "BRAINSTORM",
    "IMPLEMENT",
    "VERIFY",
    "FINAL_VERIFY",
    "FIX",
    "RELEASE",
    "DEPLOY_VERIFY",
    "ARCHIVE",
}
TRANSITIONS = {
    "PLAN:BRAINSTORM",
    "BRAINSTORM:IMPLEMENT",
    "PLAN:IMPLEMENT",
    "IMPLEMENT:VERIFY",
    "VERIFY:FINAL_VERIFY",
    "FIX:VERIFY",
    "FINAL_VERIFY:RELEASE",
    "FINAL_VERIFY:ARCHIVE",
    "RELEASE:DEPLOY_VERIFY",
    "RELEASE:ARCHIVE",
    "DEPLOY_VERIFY:ARCHIVE",
}


class _ReturnStatus(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


def root_dir() -> Path:
    return Path(os.environ.get("OPS_ROOT", Path(__file__).resolve().parents[5]))


def ops_dir() -> Path:
    return root_dir() / ".ops"


def changes_dir() -> Path:
    return ops_dir() / "changes"


def change_dir(change: str) -> Path:
    if not SAFE_CHANGE.fullmatch(change):
        die(PREFIX, f"invalid change name: {change}")
    return changes_dir() / change


def state_path(change: str) -> Path:
    return change_dir(change) / "runtime/state.json"


def valid_backend(value: str) -> bool:
    return value in {"codex", "claude-fallback"}


def read_json(path: Path, tolerate_failure: bool = False) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except OSError, json.JSONDecodeError, UnicodeDecodeError:
        if tolerate_failure:
            return None
        die(PREFIX, f"could not read JSON: {path}")
    raise AssertionError("unreachable")


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
        die(
            PREFIX, "Claude fallback requires current quant state codex_available=false"
        )


def init_change(
    change: str, session_id: str, backend: str | None, origin: str | None
) -> None:
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
        new_state: dict[str, Any] = {
            "change": change,
            "phase": "PLAN",
            "round": 0,
            "status": "running",
            "session_id": session_id,
            "routing_policy_version": 1,
            "attempts": [],
            "verification_evidence": None,
            "updated_at": utc_now(),
        }
    else:
        new_state = {
            "change": change,
            "phase": "PLAN",
            "round": 0,
            "status": "running",
            "session_id": session_id,
            "implementation_backend": backend,
            "verification_mode": verification_mode,
            "updated_at": utc_now(),
        }
    write_state(change, new_state)
    if not handoff.exists():
        handoff.write_text(
            f"# {change}\n\n- Claude: workflow initialized; planning pending.\n- Next: identify affected repositories and validate the OpenSpec artifacts.\n",
            encoding="utf-8",
        )


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
        if not isinstance(state.get("attempts"), list) or (
            state.get("verification_evidence") is not None
            and not isinstance(state.get("verification_evidence"), dict)
        ):
            die(PREFIX, "runtime state has invalid phase-agent fields")
    else:
        backend = state.get("implementation_backend", "codex")
        mode = state.get("verification_mode", "independent")
        if not valid_backend(backend):
            die(PREFIX, "runtime state has an invalid implementation backend")
        if f"{backend}:{mode}" not in {
            "codex:independent",
            "claude-fallback:claude-process-separated-review",
        }:
            die(
                PREFIX, "runtime state has an invalid verification mode for its backend"
            )
    return state


def set_phase(change: str, session_id: str, phase: str) -> None:
    if phase not in PHASES:
        die(PREFIX, f"invalid phase: {phase}")
    state = read_state(change)
    assert_active_owner(change, session_id)
    current = state.get("phase")
    if f"{current}:{phase}" not in TRANSITIONS:
        die(PREFIX, f"invalid phase transition: {current} -> {phase}")
    if (
        current == "FINAL_VERIFY"
        and phase in {"RELEASE", "ARCHIVE"}
        and state.get("routing_policy_version") == 1
    ):
        evidence = state.get("verification_evidence")
        if not (
            isinstance(evidence, dict)
            and evidence.get("final_result") == "success"
            and evidence.get("objective_gates_passed") is True
            and evidence.get("separation")
            in {"provider-independent", "same-provider-process-separated"}
        ):
            die(
                PREFIX,
                "release/archive requires successful derived FINAL_VERIFY evidence",
            )
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
    change_lock.release_repo_locks(change, session_id)
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
        change_lock.release_repo_locks(change, session_id)
        if (change_dir(change) / "runtime/lock").is_dir():
            unlock_change(change, session_id)
        print(
            f"ops-runtime: maximum fix rounds ({maximum}) reached; workflow blocked",
            file=sys.stderr,
        )
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
        die(
            PREFIX,
            f"runtime phase is {state.get('phase')}, requested route phase is {phase}",
        )
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
    required = {
        "attempt",
        "phase",
        "round",
        "provider",
        "model",
        "effort",
        "continuation",
        "result_class",
        "exit_status",
        "worktree_changed",
        "objective_gates_passed",
        "process_id",
        "evidence_base",
    }
    if (
        not isinstance(record, dict)
        or not required.issubset(record)
        or not (
            is_number(record.get("attempt"))
            and record["attempt"] >= 1
            and record.get("phase")
            in {"PLAN", "BRAINSTORM", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY"}
            and is_number(record.get("round"))
            and record.get("provider") in {"codex", "claude"}
            and isinstance(record.get("model"), str)
            and isinstance(record.get("effort"), str)
            and isinstance(record.get("continuation"), bool)
            and isinstance(record.get("result_class"), str)
            and is_number(record.get("exit_status"))
            and isinstance(record.get("worktree_changed"), bool)
            and isinstance(record.get("objective_gates_passed"), bool)
            and is_number(record.get("process_id"))
            and isinstance(record.get("evidence_base"), str)
        )
    ):
        die(PREFIX, "attempt record failed validation")
    attempts = state.get("attempts")
    if (
        state.get("routing_policy_version") != 1
        or not isinstance(attempts, list)
        or record.get("phase") != state.get("phase")
        or record.get("round") != state.get("round")
        or any(
            isinstance(item, dict) and item.get("attempt") == record.get("attempt")
            for item in attempts
        )
    ):
        die(PREFIX, "attempt does not match active state or already exists")
    attempts.append(record)
    if record["phase"] == "FINAL_VERIFY":
        mutators = [
            item
            for item in attempts
            if isinstance(item, dict)
            and item.get("phase") in {"IMPLEMENT", "FIX"}
            and item.get("result_class") == "success"
        ]
        mutator = mutators[-1] if mutators else None
        separation = (
            None
            if mutator is None
            else (
                "provider-independent"
                if mutator.get("provider") != record.get("provider")
                else (
                    "same-provider-process-separated"
                    if mutator.get("process_id") != record.get("process_id")
                    else None
                )
            )
        )
        state["verification_evidence"] = {
            "mutator_provider": mutator.get("provider") if mutator else None,
            "verifier_provider": record.get("provider"),
            "mutator_attempt": mutator.get("attempt") if mutator else None,
            "verifier_attempt": record.get("attempt"),
            "separation": separation,
            "final_result": record.get("result_class"),
            "objective_gates_passed": record.get("objective_gates_passed"),
        }
    state["updated_at"] = record.get("completed_at")
    write_state(change, state)


def trace_origin(
    change: str, session_id: str, iteration: str, instrument: str, artifacts: list[str]
) -> None:
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
    for name, label in (
        ("proposal.md", "proposal"),
        ("design.md", "design"),
        ("tasks.md", "tasks"),
    ):
        path = openspec_dir / name
        if not path.is_file() or not path.stat().st_size:
            die(PREFIX, f"promoted change {label} is missing")
    specs = openspec_dir / "specs"
    if not specs.is_dir() or not any(
        item.is_file() and item.suffix == ".md" for item in specs.rglob("*")
    ):
        die(PREFIX, "promoted change specs are missing")
    root_canonical = root_dir().resolve()
    approved = tuple(
        root_canonical / item
        for item in (
            "research/quant/rounds",
            "research/quant/studies",
            "research/quant/audits",
            "research/quant/samples",
            "research/quant/reports",
        )
    )
    for artifact in artifacts:
        if not SAFE_ARTIFACT.fullmatch(artifact):
            die(
                PREFIX, f"research artifact path contains unsafe characters: {artifact}"
            )
        wrapped = f"/{artifact}/"
        if "/../" in wrapped or "/./" in wrapped:
            die(PREFIX, f"research artifact path contains traversal: {artifact}")
        if not any(
            artifact.startswith(str(path.relative_to(root_canonical)) + "/")
            for path in approved
        ):
            die(
                PREFIX,
                f"research artifact is outside approved evidence roots: {artifact}",
            )
        candidate = root_canonical / artifact
        if not candidate.is_file():
            die(PREFIX, f"research artifact not found: {artifact}")
        resolved = candidate.resolve(strict=True)
        if not any(
            resolved.parent == path or path in resolved.parents for path in approved
        ):
            die(
                PREFIX,
                f"research artifact resolves outside approved evidence roots: {artifact}",
            )
    atomic_write_json(
        origin,
        {
            "change": change,
            "origin": "quant-research",
            "research_iteration": int(iteration),
            "instrument": instrument,
            "research_artifacts": artifacts,
        },
    )


def active_changes(workspace: str, session_id: str) -> None:
    directory = Path(workspace) / ".ops/changes"
    if not directory.is_dir():
        return
    for path in sorted(directory.glob("*/runtime/state.json")):
        state = read_json(path, tolerate_failure=True)
        if (
            isinstance(state, dict)
            and state.get("status") == "running"
            and state.get("phase") not in {"DONE", "BLOCKED", "FAILED"}
            and (not session_id or state.get("session_id") == session_id)
        ):
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
    destination = (
        ops_dir()
        / "archive"
        / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{change}"
    )
    if destination.exists():
        die(PREFIX, f"archive destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    change_lock.release_repo_locks(change, session_id)
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
