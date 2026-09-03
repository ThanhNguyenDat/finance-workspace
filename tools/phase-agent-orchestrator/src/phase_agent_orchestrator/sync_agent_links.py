"""Compatibility imports for the agent-link synchronization CLI."""

from .cli.sync_agent_links import AGENTS_DIR, ROOT_DIR, TOOLS, cli, main, sync_entries

__all__ = ["AGENTS_DIR", "ROOT_DIR", "TOOLS", "cli", "main", "sync_entries"]


if __name__ == "__main__":
    cli()
