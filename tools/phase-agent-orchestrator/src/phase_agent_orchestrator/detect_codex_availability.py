"""Compatibility Codex availability probe for the quant-research state."""

from __future__ import annotations

import argparse
import contextlib
import os
import io
import shutil
import tempfile
from pathlib import Path

from .detect_provider_availability import probe
from .io import CLIError, run_cli
from .state import quant_research

PREFIX = "detect-codex-availability"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="detect-codex-availability.py")
    parser.parse_args(argv)
    if shutil.which("codex") is None:
        print("inconclusive:missing-codex")
        return 3
    timeout_text = os.environ.get("CODEX_PROBE_TIMEOUT_SECONDS", "30")
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise CLIError(f"{PREFIX}: invalid-timeout")
    current_lock, state = quant_research.with_state()
    try:
        profile = state["codex_profiles"]["probe"]
        model, effort = profile["model"], profile["effort"]
    finally:
        current_lock.release()
    result = probe("codex", model, effort, int(timeout_text))
    if result == "success":
        with contextlib.redirect_stdout(io.StringIO()):
            quant_research.update_mode("codex-detected-on")
        print("available")
        return 0
    if result == "global-quota-exhausted":
        with contextlib.redirect_stdout(io.StringIO()):
            quant_research.update_mode("codex-detected-off")
        print("unavailable")
        return 0
    print(f"inconclusive:{result}")
    return 3


if __name__ == "__main__":
    run_cli(lambda: main(), PREFIX)
