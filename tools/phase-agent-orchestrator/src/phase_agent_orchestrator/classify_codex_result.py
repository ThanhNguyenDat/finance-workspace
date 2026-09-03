"""Compatibility imports for the Codex result CLI."""

from .cli.classify_codex_result import cli, main
from .providers.results import classify_sdk_result

__all__ = ["cli", "classify_sdk_result", "main"]


if __name__ == "__main__":
    cli()
