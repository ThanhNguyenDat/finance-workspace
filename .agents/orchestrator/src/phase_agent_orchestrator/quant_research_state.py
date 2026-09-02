"""Implementation of .agents/scripts/quant-research-state.sh."""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from .common import PidDirectoryLock, atomic_write_json, die, json_text, run_cli, utc_after, utc_now

PREFIX = "quant-research-state"
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9._:-]+$")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}


def root_dir() -> Path:
    return Path(os.environ.get("QUANT_RESEARCH_ROOT", Path(__file__).resolve().parents[4]))


def state_dir() -> Path:
    return Path(os.environ.get("QUANT_RESEARCH_STATE_DIR", root_dir() / ".ops/runtime/quant-research"))


def state_path() -> Path:
    return state_dir() / "state.json"


def usage() -> None:
    print(
        "Usage: quant-research-state.sh <init|state|codex-auto|codex-manual|codex-off|codex-on|codex-worker-off|codex-detected-off|codex-detected-on|profile-get ROLE|profile-set ROLE MODEL EFFORT|profile-reset ROLE|profiles-reset|begin-iteration>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def default_profiles() -> dict[str, dict[str, str]]:
    return {
        "probe": {"model": "gpt-5.6-luna", "effort": "high"},
        "implement": {"model": "gpt-5.6-luna", "effort": "high"},
        "fix": {"model": "gpt-5.6-terra", "effort": "high"},
        "fix_fallback": {"model": "gpt-5.6-sol", "effort": "high"},
    }


def default_state() -> dict[str, Any]:
    return {
        "schema_version": 2,
        "codex_mode": "manual",
        "codex_available": True,
        "codex_profiles": default_profiles(),
        "research_enabled": True,
        "iteration": 0,
        "last_run_at": None,
        "updated_at": None,
    }


def profile_valid(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("model"), str) and bool(SAFE_IDENTIFIER.fullmatch(value["model"])) and value.get("effort") in EFFORTS


def common_valid(value: dict[str, Any]) -> bool:
    return isinstance(value.get("codex_available"), bool) and isinstance(value.get("research_enabled"), bool) and isinstance(value.get("iteration"), int) and not isinstance(value.get("iteration"), bool) and value["iteration"] >= 0 and (value.get("last_run_at") is None or isinstance(value["last_run_at"], str)) and (value.get("updated_at") is None or isinstance(value["updated_at"], str))


def state_valid(value: Any) -> bool:
    return isinstance(value, dict) and value.get("schema_version") == 2 and value.get("codex_mode") in {"auto", "manual"} and isinstance(value.get("codex_profiles"), dict) and set(value["codex_profiles"]) == {"probe", "implement", "fix", "fix_fallback"} and all(profile_valid(item) for item in value["codex_profiles"].values()) and common_valid(value)


def v1_valid(value: Any) -> bool:
    return isinstance(value, dict) and value.get("schema_version") == 1 and common_valid(value)


def load(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        die(PREFIX, f"state file failed schema validation: {path}")


def write(state: dict[str, Any]) -> None:
    if not state_valid(state):
        die(PREFIX, "refusing to write state that fails schema validation")
    atomic_write_json(state_path(), state)


def ensure_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        state = default_state()
        write(state)
        return state
    if not path.is_file():
        die(PREFIX, f"state file is not a regular file: {path}")
    state = load(path)
    if state_valid(state):
        return state
    if v1_valid(state):
        migrated = copy.deepcopy(default_state())
        migrated["codex_available"] = state["codex_available"]
        migrated["research_enabled"] = state["research_enabled"]
        migrated["iteration"] = state["iteration"]
        migrated["last_run_at"] = state["last_run_at"]
        migrated["updated_at"] = state["updated_at"]
        write(migrated)
        return migrated
    die(PREFIX, f"state file failed schema validation: {path}")
    raise AssertionError("unreachable")


def with_state() -> tuple[PidDirectoryLock, dict[str, Any]]:
    current_lock = PidDirectoryLock(state_dir() / ".lock", PREFIX)
    current_lock.acquire()
    try:
        return current_lock, ensure_state()
    except BaseException:
        current_lock.release()
        raise


def emit(state: dict[str, Any]) -> None:
    print(json_text(state))


def normalize_role(value: str) -> str:
    if value in {"probe", "implement", "fix"}:
        return value
    if value in {"fix-fallback", "fix_fallback"}:
        return "fix_fallback"
    die(PREFIX, f"unsupported Codex profile role: {value}")
    raise AssertionError("unreachable")


def validate_model(value: str) -> None:
    if not SAFE_IDENTIFIER.fullmatch(value):
        die(PREFIX, "model must contain only safe identifier characters")


def validate_effort(value: str) -> None:
    if value not in EFFORTS:
        die(PREFIX, f"unsupported reasoning effort: {value}")


def profile_line(state: dict[str, Any], role: str) -> None:
    item = state["codex_profiles"][role]
    print(f"{item['model']}\t{item['effort']}")


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    if command in {"init", "state"}:
        if len(args) != 1:
            usage()
        current_lock, state = with_state()
        try:
            emit(state)
        finally:
            current_lock.release()
        return 0
    if command in {"codex-auto", "codex-manual", "codex-off", "codex-on", "codex-worker-off", "codex-detected-off", "codex-detected-on"}:
        if len(args) != 1:
            usage()
        current_lock, state = with_state()
        try:
            now = utc_now()
            if command == "codex-auto":
                state["codex_mode"] = "auto"
            elif command == "codex-manual":
                state["codex_mode"] = "manual"
            elif command in {"codex-off", "codex-on"}:
                state["codex_mode"] = "manual"
                state["codex_available"] = command == "codex-on"
            else:
                if command.startswith("codex-detected") and state["codex_mode"] != "auto":
                    die(PREFIX, "automatic detection result is stale because manual mode is selected")
                state["codex_available"] = command.endswith("-on")
            state["updated_at"] = now
            write(state)
            emit(state)
        finally:
            current_lock.release()
        return 0
    if command in {"profile-get", "profile-set", "profile-reset"}:
        if command == "profile-get" or command == "profile-reset":
            if len(args) != 2:
                usage()
        else:
            if len(args) != 4:
                usage()
        role = normalize_role(args[1])
        if command == "profile-set":
            validate_model(args[2])
            validate_effort(args[3])
        current_lock, state = with_state()
        try:
            if command == "profile-set":
                state["codex_profiles"][role] = {"model": args[2], "effort": args[3]}
                state["updated_at"] = utc_now()
                write(state)
            elif command == "profile-reset":
                state["codex_profiles"][role] = copy.deepcopy(default_profiles()[role])
                state["updated_at"] = utc_now()
                write(state)
            profile_line(state, role)
        finally:
            current_lock.release()
        return 0
    if command == "profiles-reset":
        if len(args) != 1:
            usage()
        current_lock, state = with_state()
        try:
            state["codex_profiles"] = default_profiles()
            state["updated_at"] = utc_now()
            write(state)
            emit(state)
        finally:
            current_lock.release()
        return 0
    if command == "begin-iteration":
        if len(args) != 1:
            usage()
        current_lock, state = with_state()
        try:
            now = utc_now()
            state["iteration"] += 1
            state["last_run_at"] = now
            state["updated_at"] = now
            write(state)
            emit(state)
        finally:
            current_lock.release()
        return 0
    usage()
    return 2


if __name__ == "__main__":
    run_cli(main, PREFIX)
