"""Codex result classifier CLI and SDK entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .classify_result import classify_legacy_logs, classify_sdk_result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="classify-codex-result.sh")
    parser.add_argument("status", type=int)
    parser.add_argument("stdout_log", type=Path)
    parser.add_argument("stderr_log", type=Path)
    args = parser.parse_args(argv)
    print(classify_legacy_logs(args.status, args.stdout_log, args.stderr_log))
    return 0


__all__ = ["classify_sdk_result", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
