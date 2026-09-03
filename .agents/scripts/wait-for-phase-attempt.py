#!/usr/bin/env python3
"""Wait for a phase attempt lease to appear and then be released."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent


def fail(message: str) -> int:
    print(f"wait-for-phase-attempt: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wait-for-phase-attempt.py")
    parser.add_argument("change")
    parser.add_argument("poll_seconds", nargs="?", type=int, default=5)
    args = parser.parse_args(argv)
    if args.poll_seconds < 1:
        return fail("poll-seconds must be a positive integer")

    runtime_dir = ROOT_DIR / ".ops/changes" / args.change / "runtime"
    lease = runtime_dir / ".phase-attempt-lock"
    waited = 0
    while not lease.is_dir() and not (runtime_dir / "state.json").is_file():
        time.sleep(args.poll_seconds)
        waited += args.poll_seconds
        if waited >= 3600:
            return fail(f"change not found after {waited}s: {args.change}")
    while lease.is_dir():
        time.sleep(args.poll_seconds)

    print(f"phase attempt for {args.change} finished")
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "ops-runtime.py"), "state", args.change],
        check=False,
        stderr=subprocess.DEVNULL,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
