"""Compatibility facade for the moved Codex availability CLI.

The small forwarding wrapper keeps monkeypatching and imports from the legacy
module path working for existing integrations while the implementation lives
under :mod:`phase_agent_orchestrator.cli`.
"""

from .cli import detect_codex_availability as _cli

PREFIX = _cli.PREFIX
probe = _cli.probe
quant_research = _cli.quant_research


def main(argv: list[str] | None = None) -> int:
    _cli.probe = probe
    return _cli.main(argv)


def cli() -> None:
    _cli.cli()


__all__ = ["PREFIX", "cli", "main", "probe", "quant_research"]


if __name__ == "__main__":
    cli()
