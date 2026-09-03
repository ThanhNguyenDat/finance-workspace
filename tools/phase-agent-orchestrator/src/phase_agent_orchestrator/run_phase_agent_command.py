"""Compatibility facade for the quant runner.

New code should import from :mod:`phase_agent_orchestrator.runners.quant`.
"""

from .runners.quant import *
from .runners.quant import _codex, main, run

__all__ = ["main", "run", "_codex"]
