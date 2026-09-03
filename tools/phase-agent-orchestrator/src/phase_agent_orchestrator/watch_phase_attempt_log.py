"""Compatibility imports for the phase-attempt log watcher CLI."""

from .cli.watch_phase_attempt_log import ROOT_DIR, cli, compact, latest_log, main, provider_tag, render

__all__ = ["ROOT_DIR", "cli", "compact", "latest_log", "main", "provider_tag", "render"]


if __name__ == "__main__":
    cli()
