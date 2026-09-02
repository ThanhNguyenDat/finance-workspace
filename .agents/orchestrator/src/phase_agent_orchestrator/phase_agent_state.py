"""Implementation of .agents/scripts/phase-agent-state.sh."""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from .common import CLIError, PidDirectoryLock, atomic_write_json, die, json_text, run_cli, utc_after, utc_now

PREFIX = "phase-agent-state"
PHASES = ("quant_research", "plan", "implement", "verify", "fix", "final_verify")
PROVIDERS = ("codex", "claude")
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9._:-]+$")


def root_dir() -> Path:
    return Path(os.environ.get("PHASE_AGENT_ROOT", Path(__file__).resolve().parents[4]))


def state_dir() -> Path:
    return Path(os.environ.get("PHASE_AGENT_STATE_DIR", root_dir() / ".ops/runtime/phase-agents"))


def state_path() -> Path:
    return state_dir() / "state.json"


def lock() -> PidDirectoryLock:
    return PidDirectoryLock(state_dir() / ".lock", PREFIX)


def usage() -> None:
    print(
        "Usage: phase-agent-state.sh <init|state|validate PROVIDER MODEL EFFORT|resolve PHASE|set PHASE PROVIDER MODEL EFFORT|candidate-set PHASE INDEX PROVIDER MODEL EFFORT|reset PHASE|reset-all|pin PHASE PROVIDER|auto PHASE|provider-on PROVIDER|provider-off PROVIDER [REASON]|provider-manual PROVIDER|provider-auto PROVIDER|provider-result PROVIDER RESULT [COOLDOWN_SECONDS]|probe-due PROVIDER>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def valid_phase(value: str) -> bool:
    return value in PHASES


def normalize_phase(value: str) -> str:
    normalized = value.replace("-", "_")
    if not valid_phase(normalized):
        die(PREFIX, f"unsupported phase agent: {value}")
    return normalized


def valid_provider(value: str) -> bool:
    return value in PROVIDERS


def validate_candidate(provider: str, model: str, effort: str) -> None:
    if not valid_provider(provider):
        die(PREFIX, f"unsupported provider: {provider}")
    if not SAFE_IDENTIFIER.fullmatch(model):
        die(PREFIX, "model contains unsafe characters")
    valid_efforts = {
        "codex": {"none", "minimal", "low", "medium", "high", "xhigh"},
        "claude": {"low", "medium", "high", "xhigh", "max"},
    }
    if effort not in valid_efforts[provider]:
        die(PREFIX, f"unsupported effort for {provider}: {effort}")
    if provider == "claude" and re.search(r"(^|[-.:])opus($|[-.:])", model) and effort not in {"medium", "high"}:
        die(PREFIX, "Opus supports only medium or high by workspace policy")


def candidate(provider: str, model: str, effort: str) -> dict[str, str]:
    return {"provider": provider, "model": model, "effort": effort}


def default_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phases": {
            "quant_research": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("claude", "sonnet", "high"), candidate("codex", "gpt-5.6-luna", "high")]},
            "plan": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("claude", "opus", "medium"), candidate("codex", "gpt-5.6-terra", "high")]},
            "implement": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("codex", "gpt-5.6-luna", "high"), candidate("claude", "sonnet", "high")]},
            "verify": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("claude", "opus", "medium"), candidate("codex", "gpt-5.6-terra", "high")]},
            "fix": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("codex", "gpt-5.6-terra", "high"), candidate("codex", "gpt-5.6-sol", "high"), candidate("claude", "opus", "high")]},
            "final_verify": {"mode": "auto", "pinned_provider": None, "candidates": [candidate("claude", "opus", "high"), candidate("codex", "gpt-5.6-terra", "high")]},
        },
        "providers": {
            "codex": {"mode": "auto", "available": True, "reason": None, "observed_at": None, "next_probe_at": None},
            "claude": {"mode": "auto", "available": True, "reason": None, "observed_at": None, "next_probe_at": None},
        },
        "legacy_imported": False,
        "updated_at": None,
    }


def is_string(value: Any) -> bool:
    return isinstance(value, str)


def state_valid(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        return False
    phases = value.get("phases")
    providers = value.get("providers")
    if not isinstance(phases, dict) or set(phases) != set(PHASES) or not isinstance(providers, dict) or set(providers) != set(PROVIDERS):
        return False
    for phase in PHASES:
        item = phases[phase]
        if not isinstance(item, dict) or item.get("mode") not in {"auto", "manual"}:
            return False
        if item.get("pinned_provider") is not None and item.get("pinned_provider") not in PROVIDERS:
            return False
        candidates = item.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return False
        for option in candidates:
            if not isinstance(option, dict) or not valid_provider(option.get("provider", "")):
                return False
            model, effort = option.get("model"), option.get("effort")
            if not is_string(model) or not SAFE_IDENTIFIER.fullmatch(model):
                return False
            if option["provider"] == "codex" and effort not in {"none", "minimal", "low", "medium", "high", "xhigh"}:
                return False
            if option["provider"] == "claude" and effort not in {"low", "medium", "high", "xhigh", "max"}:
                return False
            if option["provider"] == "claude" and re.search(r"(^|[-.:])opus($|[-.:])", model) and effort not in {"medium", "high"}:
                return False
    for provider in PROVIDERS:
        item = providers[provider]
        if not isinstance(item, dict) or item.get("mode") not in {"auto", "manual"} or not isinstance(item.get("available"), bool):
            return False
        for key in ("reason", "observed_at", "next_probe_at"):
            if item.get(key) is not None and not is_string(item[key]):
                return False
    return isinstance(value.get("legacy_imported"), bool) and (value.get("updated_at") is None or is_string(value.get("updated_at")))


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        die(PREFIX, f"state failed validation: {path}")


def import_legacy(state: dict[str, Any]) -> dict[str, Any]:
    quant = Path(os.environ.get("PHASE_AGENT_LEGACY_QUANT_STATE", root_dir() / ".ops/runtime/quant-research/state.json"))
    claude = Path(os.environ.get("PHASE_AGENT_LEGACY_CLAUDE_STATE", root_dir() / ".ops/runtime/claude-workers/state.json"))
    try:
        old = load_json(quant) if quant.is_file() else None
    except CLIError:
        old = None
    if isinstance(old, dict) and isinstance(old.get("codex_profiles"), dict):
        if "codex_available" in old:
            state["providers"]["codex"]["available"] = old["codex_available"]
        for phase, role in (("implement", "implement"), ("fix", "fix")):
            profile = old["codex_profiles"].get(role)
            if isinstance(profile, dict):
                state["phases"][phase]["candidates"][0] = {**profile, "provider": "codex"}
        profile = old["codex_profiles"].get("fix_fallback")
        if isinstance(profile, dict):
            state["phases"]["fix"]["candidates"][1] = {**profile, "provider": "codex"}
    try:
        old = load_json(claude) if claude.is_file() else None
    except CLIError:
        old = None
    if isinstance(old, dict) and isinstance(old.get("profiles"), dict):
        mappings = (("quant_research", "quant_research"), ("plan", "plan"), ("implement", "fallback_implement"), ("verify", "verify"), ("fix", "fallback_fix"), ("final_verify", "final_verify"))
        for phase, role in mappings:
            profile = old["profiles"].get(role)
            if isinstance(profile, dict):
                index = {"quant_research": 0, "plan": 0, "implement": 1, "verify": 0, "fix": 2, "final_verify": 0}[phase]
                state["phases"][phase]["candidates"][index] = {**profile, "provider": "claude"}
    state["legacy_imported"] = True
    return state


def ensure_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        state = import_legacy(default_state())
        if not state_valid(state):
            die(PREFIX, "refusing invalid state")
        atomic_write_json(path, state)
        return state
    if not path.is_file():
        die(PREFIX, f"state is not a regular file: {path}")
    state = load_json(path)
    if not state_valid(state):
        die(PREFIX, f"state failed validation: {path}")
    return state


def save(state: dict[str, Any]) -> None:
    if not state_valid(state):
        die(PREFIX, "refusing invalid state")
    atomic_write_json(state_path(), state)


def with_state() -> tuple[PidDirectoryLock, dict[str, Any]]:
    current_lock = lock()
    current_lock.acquire()
    try:
        return current_lock, ensure_state()
    except BaseException:
        current_lock.release()
        raise


def emit(state: dict[str, Any]) -> None:
    print(json_text(state))


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
    if command == "validate":
        if len(args) != 4:
            usage()
        validate_candidate(args[1], args[2], args[3])
        return 0
    if command == "resolve":
        if len(args) != 2:
            usage()
        phase = normalize_phase(args[1])
        current_lock, state = with_state()
        try:
            item = state["phases"][phase]
            for option in item["candidates"]:
                provider = option["provider"]
                if (item["mode"] != "manual" or item["pinned_provider"] == provider) and state["providers"][provider]["available"]:
                    print(f"{provider}\t{option['model']}\t{option['effort']}")
                    break
        finally:
            current_lock.release()
        return 0
    if command in {"set", "candidate-set"}:
        expected = 5 if command == "set" else 6
        if len(args) != expected:
            usage()
        phase = normalize_phase(args[1])
        if command == "set":
            provider, model, effort = args[2:5]
        else:
            index = args[2]
            if not index.isdigit():
                die(PREFIX, "candidate index must be non-negative")
            provider, model, effort = args[3:6]
        validate_candidate(provider, model, effort)
        current_lock, state = with_state()
        try:
            if command == "set":
                state["phases"][phase]["candidates"] = [candidate(provider, model, effort)] + [item for item in state["phases"][phase]["candidates"] if item["provider"] != provider]
            else:
                position = int(index)
                candidates = state["phases"][phase]["candidates"]
                if position >= len(candidates):
                    die(PREFIX, "candidate index is out of range")
                candidates[position] = candidate(provider, model, effort)
            state["updated_at"] = utc_now()
            save(state)
        finally:
            current_lock.release()
        return 0
    if command in {"reset", "reset-all", "pin", "auto", "provider-on", "provider-off", "provider-manual", "provider-auto", "provider-result"}:
        return mutate_command(command, args)
    if command == "probe-due":
        if len(args) != 2:
            usage()
        provider = args[1]
        if not valid_provider(provider):
            die(PREFIX, f"unsupported provider: {provider}")
        current_lock, state = with_state()
        try:
            item = state["providers"][provider]
            return int(not (item["mode"] == "auto" and not item["available"] and item["next_probe_at"] is not None and item["next_probe_at"] <= utc_now()))
        finally:
            current_lock.release()
    usage()
    return 2


def mutate_command(command: str, args: list[str]) -> int:
    if command == "reset":
        if len(args) != 2:
            usage()
        phase = normalize_phase(args[1])
    elif command == "reset-all":
        if len(args) != 1:
            usage()
    elif command == "pin":
        if len(args) != 3:
            usage()
        phase = normalize_phase(args[1])
        provider = args[2]
        if not valid_provider(provider):
            die(PREFIX, f"unsupported provider: {provider}")
    elif command == "auto":
        if len(args) != 2:
            usage()
        phase = normalize_phase(args[1])
    else:
        if command == "provider-off":
            if len(args) not in {2, 3}:
                usage()
        elif command in {"provider-on", "provider-manual", "provider-auto"} and len(args) != 2:
            usage()
        elif command == "provider-result" and len(args) not in {3, 4}:
            usage()
        if command != "provider-result":
            provider = args[1]
        else:
            provider, result = args[1:3]
        if not valid_provider(provider):
            die(PREFIX, f"unsupported provider: {provider}")

    current_lock, state = with_state()
    try:
        changed = True
        if command == "reset":
            state["phases"][phase] = copy.deepcopy(default_state()["phases"][phase])
        elif command == "reset-all":
            state = default_state()
            state["legacy_imported"] = True
        elif command == "pin":
            if not any(item["provider"] == provider for item in state["phases"][phase]["candidates"]):
                die(PREFIX, "provider has no candidate for phase")
            state["phases"][phase]["mode"] = "manual"
            state["phases"][phase]["pinned_provider"] = provider
        elif command == "auto":
            state["phases"][phase]["mode"] = "auto"
            state["phases"][phase]["pinned_provider"] = None
        elif command == "provider-on":
            state["providers"][provider] = {"mode": "manual", "available": True, "reason": None, "observed_at": utc_now(), "next_probe_at": None}
        elif command == "provider-off":
            reason = args[2] if len(args) == 3 else "manual-off"
            if not SAFE_IDENTIFIER.fullmatch(reason):
                die(PREFIX, "unsafe reason")
            state["providers"][provider] = {"mode": "manual", "available": False, "reason": reason, "observed_at": utc_now(), "next_probe_at": None}
        elif command == "provider-manual":
            state["providers"][provider]["mode"] = "manual"
        elif command == "provider-auto":
            state["providers"][provider]["mode"] = "auto"
        elif command == "provider-result":
            cooldown_text = args[3] if len(args) == 4 else "3600"
            if not cooldown_text.isdigit():
                die(PREFIX, "cooldown must be a non-negative integer")
            now = utc_now()
            changed = True
            if result == "success":
                state["providers"][provider].update(available=True, reason=None, observed_at=now, next_probe_at=None)
            elif result == "global-quota-exhausted":
                state["providers"][provider].update(available=False, reason=result, observed_at=now, next_probe_at=utc_after(int(cooldown_text)))
            elif result == "auth-error":
                state["providers"][provider].update(mode="manual", available=False, reason=result, observed_at=now, next_probe_at=None)
            elif result == "probe-inconclusive":
                state["providers"][provider].update(observed_at=now, next_probe_at=utc_after(int(cooldown_text)))
            elif result not in {"model-unavailable", "model-specific-limit", "transient-rate-limit", "network-error", "timeout", "implementation-error", "unknown-error"}:
                die(PREFIX, f"unsupported provider result: {result}")
            else:
                changed = False
        if command != "reset-all" and changed:
            state["updated_at"] = utc_now()
        if command != "reset-all" and not changed:
            current_lock.release()
            return 0
        save(state)
        if command in {"provider-on", "provider-off", "provider-manual", "provider-auto", "provider-result", "reset", "reset-all", "pin", "auto"}:
            return 0
    finally:
        current_lock.release()
    return 0


if __name__ == "__main__":
    run_cli(main, PREFIX)
