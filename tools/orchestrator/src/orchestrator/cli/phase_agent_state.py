"""Argument parsing and dispatch for the phase-agent-state console command."""

from __future__ import annotations

import sys
from typing import NoReturn

from ..core.io import run_cli
from ..state import candidates

PREFIX = candidates.PREFIX


def usage() -> None:
    print(
        "Usage: phase-agent-state <init|state|account-dir PROVIDER ACCOUNT|validate PROVIDER MODEL EFFORT [ACCOUNT]|resolve PHASE|set PHASE PROVIDER MODEL EFFORT [ACCOUNT]|candidate-set PHASE INDEX PROVIDER MODEL EFFORT [ACCOUNT]|reset PHASE|reset-all|pin PHASE PROVIDER [ACCOUNT]|auto PHASE|provider-on PROVIDER [ACCOUNT]|provider-off PROVIDER [REASON] [ACCOUNT]|provider-manual PROVIDER|provider-auto PROVIDER|provider-result PROVIDER RESULT [COOLDOWN_SECONDS] [ACCOUNT]|probe-due PROVIDER [ACCOUNT]>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def mutate_command(command: str, args: list[str]) -> int:
    if command == "reset":
        if len(args) != 2:
            usage()
    elif command == "reset-all":
        if len(args) != 1:
            usage()
    elif command == "pin":
        if len(args) not in {3, 4}:
            usage()
        provider = args[2]
        if not candidates.valid_provider(provider):
            candidates.die(PREFIX, f"unsupported provider: {provider}")
    elif command == "auto":
        if len(args) != 2:
            usage()
    else:
        if command == "provider-off":
            if len(args) not in {2, 3, 4}:
                usage()
        elif command in {"provider-on", "provider-manual", "provider-auto"} and len(args) not in {2, 3}:
            usage()
        elif command == "provider-result" and len(args) not in {3, 4, 5}:
            usage()
        provider = args[1]
        if not candidates.valid_provider(provider):
            candidates.die(PREFIX, f"unsupported provider: {provider}")
    return candidates.mutate(command, args)


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    if command in {"init", "state"}:
        if len(args) != 1:
            usage()
        current_lock, state = candidates.with_state()
        try:
            candidates.emit(state)
        finally:
            current_lock.release()
        return 0
    if command == "account-dir":
        if len(args) != 3:
            usage()
        _, directory = candidates.resolve_account_dir(args[1], args[2], PREFIX)
        print(directory)
        return 0
    if command == "validate":
        if len(args) not in {4, 5}:
            usage()
        candidates.validate_candidate(args[1], args[2], args[3], args[4] if len(args) == 5 else None)
        return 0
    if command == "resolve":
        if len(args) != 2:
            usage()
        phase = candidates.normalize_phase(args[1])
        current_lock, state = candidates.with_state()
        try:
            candidates.resolve(phase, state)
        finally:
            current_lock.release()
        return 0
    if command in {"set", "candidate-set"}:
        expected = {"set": {5, 6}, "candidate-set": {6, 7}}[command]
        if len(args) not in expected:
            usage()
        phase = candidates.normalize_phase(args[1])
        if command == "set":
            provider, model, effort = args[2:5]
            account = args[5] if len(args) == 6 else None
            candidates.set_candidate(phase, provider, model, effort, account)
        else:
            index = args[2]
            if not index.isdigit():
                candidates.die(PREFIX, "candidate index must be non-negative")
            provider, model, effort = args[3:6]
            account = args[6] if len(args) == 7 else None
            candidates.set_candidate(phase, provider, model, effort, account, int(index))
        return 0
    if command in {"reset", "reset-all", "pin", "auto", "provider-on", "provider-off", "provider-manual", "provider-auto", "provider-result"}:
        return mutate_command(command, args)
    if command == "probe-due":
        if len(args) not in {2, 3}:
            usage()
        provider = args[1]
        if not candidates.valid_provider(provider):
            candidates.die(PREFIX, f"unsupported provider: {provider}")
        account = args[2] if len(args) == 3 else None
        if account is not None:
            account, _ = candidates.resolve_account_dir(provider, account, PREFIX)
        return candidates.probe_due(provider, account)
    usage()
    return 2


def cli() -> NoReturn:
    run_cli(main, PREFIX)


if __name__ == "__main__":
    cli()
