"""Compatibility facade for the lifecycle runner.

New code should import from :mod:`phase_agent_orchestrator.runners.lifecycle`.
"""

from .runners.lifecycle import *
from .runners.lifecycle import _brainstorm_checkpoint, main, run

__all__ = ["main", "run", "_brainstorm_checkpoint"]
