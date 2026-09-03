"""Compatibility facade for the provider availability library and CLI."""

from __future__ import annotations

from .cli import detect_provider_availability as _cli
from .providers.availability import probe
from .io import run_cli


PREFIX = "detect-provider-availability"


def main(argv: list[str] | None = None) -> int:
    _cli.probe = probe
    return _cli.main(argv)


def cli() -> None:
    run_cli(lambda: main(), PREFIX)


__all__ = ["PREFIX", "cli", "main", "probe"]


if __name__ == "__main__":
    cli()
