"""CLI boundary for the provider-backed command runner."""

from __future__ import annotations

from typing import NoReturn

from ..io import run_cli
from ..runners.quant import main

PREFIX = "run-phase-agent-command"


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
