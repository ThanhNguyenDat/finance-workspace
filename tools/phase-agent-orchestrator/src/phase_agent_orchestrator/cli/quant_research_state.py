"""Argument parsing and dispatch for quant-research-state.py."""

from __future__ import annotations

import sys

from ..io import run_cli
from ..state import quant_research

PREFIX = quant_research.PREFIX


def usage() -> None:
    print(
        "Usage: quant-research-state.py <init|state|codex-auto|codex-manual|codex-off|codex-on|codex-worker-off|codex-detected-off|codex-detected-on|profile-get ROLE|profile-set ROLE MODEL EFFORT|profile-reset ROLE|profiles-reset|begin-iteration>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    if command in {"init", "state"}:
        if len(args) != 1:
            usage()
        current_lock, state = quant_research.with_state()
        try:
            quant_research.emit(state)
        finally:
            current_lock.release()
        return 0
    if command in {"codex-auto", "codex-manual", "codex-off", "codex-on", "codex-worker-off", "codex-detected-off", "codex-detected-on"}:
        if len(args) != 1:
            usage()
        quant_research.update_mode(command)
        return 0
    if command in {"profile-get", "profile-set", "profile-reset"}:
        if command in {"profile-get", "profile-reset"}:
            if len(args) != 2:
                usage()
        else:
            if len(args) != 4:
                usage()
        role = quant_research.normalize_role(args[1])
        if command == "profile-set":
            quant_research.validate_model(args[2])
            quant_research.validate_effort(args[3])
            quant_research.update_profile(command, role, args[2], args[3])
        else:
            quant_research.update_profile(command, role)
        return 0
    if command == "profiles-reset":
        if len(args) != 1:
            usage()
        quant_research.reset_profiles()
        return 0
    if command == "begin-iteration":
        if len(args) != 1:
            usage()
        quant_research.begin_iteration()
        return 0
    usage()
    return 2


if __name__ == "__main__":
    run_cli(main, PREFIX)
