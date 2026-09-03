"""Operator CLI for agent-role candidate and provider configuration."""

from __future__ import annotations

import sys
from typing import NoReturn

from ..core.io import CLIError, run_cli
from ..state import candidates

PREFIX = "configure-agent-roles"


def show() -> None:
    current_lock, state = candidates.with_state()
    try:
        print(
            f"{'ROLE':<16} {'MODE':<8} {'PROVIDER':<8} {'MODEL':<24} {'ACCOUNT':<12} EFFORT"
        )
        for role, item in state["roles"].items():
            for option in item["candidates"]:
                print(
                    f"{role:<16} {item['mode']:<8} {option['provider']:<8} "
                    f"{option['model']:<24} {option.get('account', '-'):<12} {option['effort']}"
                )
        print()
        print(f"{'PROVIDER':<8} {'MODE':<8} {'AVAILABLE':<10} REASON")
        for provider, item in state["providers"].items():
            print(
                f"{provider:<8} {item['mode']:<8} {str(item['available']).lower():<10} {item.get('reason') or '-'}"
            )
    finally:
        current_lock.release()


def usage() -> None:
    print(
        "usage: configure-agent-roles <show|set ROLE PROVIDER MODEL EFFORT [ACCOUNT]|candidate-set ROLE INDEX PROVIDER MODEL EFFORT [ACCOUNT]|reset ROLE|reset-all|pin ROLE PROVIDER [ACCOUNT]|auto ROLE|provider-on PROVIDER [ACCOUNT]|provider-off PROVIDER [REASON] [ACCOUNT]|provider-manual PROVIDER|provider-auto PROVIDER>",
        file=sys.stderr,
    )
    raise CLIError(f"{PREFIX}: invalid usage")


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        usage()
    command = args[0]
    if command == "show" and len(args) == 1:
        show()
        return 0
    if command == "set" and len(args) in {5, 6}:
        role = candidates.normalize_role(args[1])
        candidates.set_candidate(
            role, args[2], args[3], args[4], args[5] if len(args) == 6 else None
        )
        show()
        return 0
    if command == "candidate-set" and len(args) in {6, 7}:
        role = candidates.normalize_role(args[1])
        if not args[2].isdigit():
            raise CLIError(f"{PREFIX}: candidate index must be non-negative")
        candidates.set_candidate(
            role,
            args[3],
            args[4],
            args[5],
            args[6] if len(args) == 7 else None,
            int(args[2]),
        )
        show()
        return 0
    if command == "reset" and len(args) == 2:
        candidates.mutate(command, args)
        show()
        return 0
    if command == "reset-all" and len(args) == 1:
        candidates.mutate(command, args)
        show()
        return 0
    if command == "pin" and len(args) in {3, 4}:
        candidates.mutate(command, args)
        show()
        return 0
    if command == "auto" and len(args) == 2:
        candidates.mutate(command, args)
        show()
        return 0
    if command in {"provider-on", "provider-off"} and 2 <= len(args) <= 4:
        candidates.mutate(command, args)
        show()
        return 0
    if command in {"provider-manual", "provider-auto"} and len(args) == 2:
        candidates.mutate(command, args)
        show()
        return 0
    usage()
    return 2


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
