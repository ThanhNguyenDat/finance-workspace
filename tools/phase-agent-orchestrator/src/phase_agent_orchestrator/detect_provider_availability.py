"""Probe provider availability through the official SDKs."""

from __future__ import annotations

import argparse
import asyncio
import os
import tempfile
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import ApprovalMode, CodexConfig, Sandbox

from .classify_result import classify_sdk_result
from .io import CLIError, run_cli
from .provider_sdk import child_environment, executable, start_codex
from .state import candidates
from .subprocess_supervision import hard_kill_claude_client, supervise_claude_turn, supervise_codex_turn

PREFIX = "detect-provider-availability"


async def _probe_claude(model: str, effort: str, timeout_seconds: float, cwd: Path) -> str:
    client = ClaudeSDKClient(
        ClaudeAgentOptions(
            cli_path=executable("claude", PREFIX),
            cwd=cwd,
            env=child_environment(),
            model=model,
            effort=effort,
            permission_mode="bypassPermissions",
        )
    )
    try:
        try:
            await asyncio.wait_for(client.connect(), timeout=max(1, timeout_seconds))
        except TimeoutError:
            hard_kill_claude_client(client)
            return "timeout"
        outcome = await supervise_claude_turn(
            client,
            "Reply with exactly OK.",
            timeout_seconds=timeout_seconds,
            kill_after_seconds=5,
        )
        return classify_sdk_result(
            outcome.result,
            provider="claude",
            timed_out=outcome.timed_out,
            hard_killed=outcome.hard_killed,
        )
    except BaseException as error:
        return classify_sdk_result(provider="claude", error=error)
    finally:
        try:
            await asyncio.wait_for(client.disconnect(), timeout=2)
        except (TimeoutError, asyncio.CancelledError):
            hard_kill_claude_client(client)


def _probe_codex(model: str, effort: str, timeout_seconds: float, cwd: Path) -> str:
    config = CodexConfig(
        codex_bin=executable("codex", PREFIX),
        cwd=str(cwd),
        env=child_environment(),
    )
    codex = None
    try:
        codex = start_codex(config, max(1, timeout_seconds))
        thread = codex.thread_start(
            approval_mode=ApprovalMode.deny_all,
            cwd=str(cwd),
            ephemeral=True,
            model=model,
            sandbox=Sandbox.full_access,
        )
        handle = thread.turn("Reply with exactly OK.", effort=effort, model=model, sandbox=Sandbox.full_access)
        outcome = supervise_codex_turn(
            handle,
            timeout_seconds=timeout_seconds,
            kill_after_seconds=5,
        )
        return classify_sdk_result(
            outcome.result,
            provider="codex",
            timed_out=outcome.timed_out,
            hard_killed=outcome.hard_killed,
        )
    except BaseException as error:
        return classify_sdk_result(provider="codex", error=error)
    finally:
        if codex is not None:
            codex.close()


def probe(provider: str, model: str, effort: str, timeout_seconds: float) -> str:
    with tempfile.TemporaryDirectory(prefix="phase-agent-probe-") as directory:
        cwd = Path(directory)
        if provider == "claude":
            return asyncio.run(_probe_claude(model, effort, timeout_seconds, cwd))
        if provider == "codex":
            return _probe_codex(model, effort, timeout_seconds, cwd)
    raise AssertionError("unreachable")


def _candidate(state: dict, provider: str) -> tuple[str, str]:
    for phase in state["phases"].values():
        for option in phase["candidates"]:
            if option["provider"] == provider:
                return option["model"], option["effort"]
    raise CLIError(f"{PREFIX}: missing-candidate")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="detect-provider-availability.sh")
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


if __name__ == "__main__":
    run_cli(lambda: main(), PREFIX)
