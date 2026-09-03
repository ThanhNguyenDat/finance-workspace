"""Compatibility imports for the Codex phase CLI."""

from .cli.run_codex_phase import PREFIX, cli, main

__all__ = ["PREFIX", "cli", "main"]


if __name__ == "__main__":
    cli()
