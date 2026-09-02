"""CLI entry point for a Codex SDK-backed phase adapter."""

from __future__ import annotations

import sys

from .io import run_cli
from .phase_adapter import run

PREFIX = "run-codex-phase"


def main(argv: list[str] | None = None) -> int:
    return run("codex", list(argv if argv is not None else sys.argv[1:]))


if __name__ == "__main__":
    run_cli(lambda: main(), PREFIX)
