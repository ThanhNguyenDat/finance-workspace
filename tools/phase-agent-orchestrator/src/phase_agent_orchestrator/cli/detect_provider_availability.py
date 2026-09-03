"""CLI boundary for provider availability probes."""

from __future__ import annotations

import argparse
import os
from typing import NoReturn

from ..io import CLIError
from ..io import run_cli
from ..providers.availability import probe
from ..state import candidates

PREFIX = "detect-provider-availability"


def _candidate(state: dict, provider: str) -> tuple[str, str]:
    for phase in state["phases"].values():
        for option in phase["candidates"]:
            if option["provider"] == provider:
                return option["model"], option["effort"]
    raise CLIError(f"{PREFIX}: missing-candidate")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=PREFIX)
    parser.add_argument("provider", choices=("codex", "claude"))
    args = parser.parse_args(argv)
    timeout_text = os.environ.get("PHASE_AGENT_PROBE_TIMEOUT_SECONDS", "30")
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise CLIError(f"{PREFIX}: invalid-timeout")
    current_lock, state = candidates.with_state()
    try:
        model, effort = _candidate(state, args.provider)
    finally:
        current_lock.release()
    model = os.environ.get(f"PHASE_AGENT_{args.provider.upper()}_PROBE_MODEL", model)
    effort = os.environ.get(f"PHASE_AGENT_{args.provider.upper()}_PROBE_EFFORT", effort)
    result = probe(args.provider, model, effort, int(timeout_text))
    if result == "success":
        candidates.mutate("provider-result", ["provider-result", args.provider, "success"])
        print("available")
        return 0
    if result in {"global-quota-exhausted", "auth-error"}:
        candidates.mutate("provider-result", ["provider-result", args.provider, result])
        print("unavailable")
        return 0
    cooldown = os.environ.get("PHASE_AGENT_PROBE_COOLDOWN_SECONDS", "3600")
    if not cooldown.isdigit():
        raise CLIError(f"{PREFIX}: invalid-cooldown")
    candidates.mutate("provider-result", ["provider-result", args.provider, "probe-inconclusive", cooldown])
    print(f"inconclusive:{result}")
    return 3


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
