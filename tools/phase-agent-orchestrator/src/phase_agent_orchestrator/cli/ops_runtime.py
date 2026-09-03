"""Argument parsing and dispatch for ops-runtime.sh."""

from __future__ import annotations

import sys
from typing import NoReturn

from ..io import run_cli
from ..locks import account_lock, change_lock
from ..state import ops_transaction

PREFIX = ops_transaction.PREFIX
PHASES = ops_transaction.PHASES
TRANSITIONS = ops_transaction.TRANSITIONS


def usage() -> None:
    print(
        """usage:
  ops-runtime lock <change> <session-id>
  ops-runtime init <change> <session-id> [legacy-backend] [origin]
  ops-runtime unlock <change> <session-id>
  ops-runtime lock-repos <change> <session-id> <repository>...
  ops-runtime unlock-repos <change> <session-id>
  ops-runtime lock-account <provider> <account> <owner-pid> [change] [session-id]
  ops-runtime unlock-account <provider> <account> <owner-pid> [change] [session-id]
  ops-runtime cleanup <change> <session-id> <FAILED|BLOCKED>
  ops-runtime assert-repo-lock <change> <session-id> <repository>
  ops-runtime phase <change> <session-id> <next-phase>
  ops-runtime fix <change> <session-id>
  ops-runtime route <change> <session-id> <IMPLEMENT|FIX>
  ops-runtime record-attempt <change> <session-id> <attempt-json-file>
  ops-runtime trace-origin <change> <session-id> <research-iteration> <instrument> <research-artifact>...
  ops-runtime state <change>
  ops-runtime active <workspace-root> [session-id]
  ops-runtime complete <change> <session-id>""",
        file=sys.stderr,
    )
    raise SystemExit(2)


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    try:
        if command == "lock" and len(args) == 3:
            change_lock.lock_change(args[1], args[2])
        elif command == "init" and 3 <= len(args) <= 5:
            ops_transaction.init_change(args[1], args[2], args[3] if len(args) > 3 else None, args[4] if len(args) > 4 else None)
        elif command == "unlock" and len(args) == 3:
            ops_transaction.unlock_change(args[1], args[2])
        elif command == "lock-repos" and len(args) >= 4:
            ops_transaction.assert_active_owner(args[1], args[2])
            change_lock.lock_repositories(args[1], args[2], args[3:])
        elif command == "unlock-repos" and len(args) == 3:
            if not args[2]:
                ops_transaction.die(PREFIX, "session id is required")
            change_lock.release_repo_locks(args[1], args[2])
        elif command == "lock-account" and 4 <= len(args) <= 6:
            account_lock.lock_account(args[1], args[2], args[3], args[4] if len(args) >= 5 else "", args[5] if len(args) == 6 else "")
        elif command == "unlock-account" and 4 <= len(args) <= 6:
            account_lock.unlock_account(args[1], args[2], args[3], args[4] if len(args) >= 5 else "", args[5] if len(args) == 6 else "")
        elif command == "cleanup" and len(args) == 4:
            ops_transaction.cleanup(args[1], args[2], args[3])
        elif command == "assert-repo-lock" and len(args) == 4:
            ops_transaction.assert_active_owner(args[1], args[2])
            change_lock.assert_repo_lock(args[1], args[2], args[3])
        elif command == "phase" and len(args) == 4:
            ops_transaction.set_phase(args[1], args[2], args[3])
        elif command == "fix" and len(args) == 3:
            ops_transaction.enter_fix(args[1], args[2])
        elif command == "route" and len(args) == 4:
            ops_transaction.route(args[1], args[2], args[3])
        elif command == "record-attempt" and len(args) == 4:
            ops_transaction.record_attempt(args[1], args[2], args[3])
        elif command == "trace-origin" and len(args) >= 6:
            ops_transaction.trace_origin(args[1], args[2], args[3], args[4], args[5:])
        elif command == "state" and len(args) == 2:
            path = ops_transaction.state_path(args[1])
            try:
                print(path.read_text(encoding="utf-8"), end="")
            except OSError:
                ops_transaction.die(PREFIX, f"runtime state not found: {path}")
        elif command == "active" and 2 <= len(args) <= 3:
            ops_transaction.active_changes(args[1], args[2] if len(args) == 3 else "")
        elif command in {"complete", "archive"} and len(args) == 3:
            ops_transaction.complete(args[1], args[2])
        else:
            usage()
    except (change_lock._ReturnStatus, ops_transaction._ReturnStatus) as status:
        return status.status
    return 0


def cli() -> NoReturn:
    run_cli(main, PREFIX)


if __name__ == "__main__":
    cli()
