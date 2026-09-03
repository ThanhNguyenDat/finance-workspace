"""CLI boundary for the lifecycle phase runner."""

from __future__ import annotations

from typing import NoReturn

from ..io import run_cli
from ..runners.lifecycle import main

PREFIX = "run-phase-agent"


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
