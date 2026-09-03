"""Coordinator-backed compatibility entrypoint for prompt submission."""

from __future__ import annotations

import sys
from typing import NoReturn

from ..coordinator import CoordinatorDB, active_sessions, admit_session, create_session, resume_session
from ..core.io import CLIError, json_text, run_cli

PREFIX = "e2e"


def usage() -> NoReturn:
    print("Usage: e2e <change> [prompt ...] [--session SESSION]", file=sys.stderr)
    raise SystemExit(2)


def _arguments(args: list[str]) -> tuple[str, str, str | None]:
    if not args:
        usage()
    session_id: str | None = None
    remaining: list[str] = []
    index = 0
    while index < len(args):
        if args[index] == "--session":
            if session_id is not None or index + 1 >= len(args):
                raise CLIError(f"{PREFIX}: --session requires one value")
            session_id = args[index + 1]
            index += 2
            continue
        remaining.append(args[index])
        index += 1
    if not remaining:
        usage()
    change = remaining[0]
    prompt = " ".join(remaining[1:]).strip()
    return change, prompt, session_id


def main(argv: list[str] | None = None) -> int:
    change, prompt, requested_session = _arguments(list(argv if argv is not None else sys.argv[1:]))
    db = CoordinatorDB()
    if requested_session:
        session = resume_session(requested_session, db=db)
        if session.get("change_name") != change:
            raise CLIError(f"{PREFIX}: session belongs to another change")
        print(json_text({"session": session, "action": "resumed"}))
        return 0

    candidates = active_sessions(change, db=db)
    if len(candidates) > 1:
        raise CLIError(f"{PREFIX}: multiple active sessions exist for change {change}")
    if candidates:
        print(json_text({"session": candidates[0], "action": "resumed"}))
        return 0

    context = {"request": prompt or change, "entrypoint": "e2e"}
    session = create_session(change, context, db=db)
    admission = admit_session(session["id"], db=db)
    print(json_text({"session": session, "admission": admission, "action": "submitted"}))
    return 0 if admission["admitted"] else 2


def cli() -> NoReturn:
    run_cli(main, PREFIX)


if __name__ == "__main__":
    cli()
