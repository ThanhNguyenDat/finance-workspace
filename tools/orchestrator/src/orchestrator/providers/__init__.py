"""Provider abstraction for running one bounded SDK turn.

Each concrete provider (`CodexProvider`, `ClaudeProvider`, ...) wraps a
specific SDK behind `BaseProvider`. Adding a new provider later means adding
a subclass here, not touching the CLI entry points under `orchestrator.cli`.
"""

from .base import BaseProvider, ProviderResult
from .claude import ClaudeProvider
from .codex import CodexProvider

__all__ = ["BaseProvider", "ProviderResult", "ClaudeProvider", "CodexProvider"]
