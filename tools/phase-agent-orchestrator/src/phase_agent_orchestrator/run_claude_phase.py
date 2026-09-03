"""Compatibility imports for the Claude phase CLI."""

from .cli.run_claude_phase import PREFIX, cli, main

__all__ = ["PREFIX", "cli", "main"]


if __name__ == "__main__":
    cli()
