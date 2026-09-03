"""Compatibility imports for the operator configuration CLI.

The command implementation lives in :mod:`phase_agent_orchestrator.cli`.
"""

from .cli.configure_phase_agents import PREFIX, cli, main, show, usage

__all__ = ["PREFIX", "cli", "main", "show", "usage"]


if __name__ == "__main__":
    cli()
