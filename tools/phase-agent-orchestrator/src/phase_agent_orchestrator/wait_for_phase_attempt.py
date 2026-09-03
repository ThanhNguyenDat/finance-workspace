"""Compatibility imports for the phase-attempt wait CLI."""

from .cli.wait_for_phase_attempt import ROOT_DIR, cli, fail, main

__all__ = ["ROOT_DIR", "cli", "fail", "main"]


if __name__ == "__main__":
    cli()
