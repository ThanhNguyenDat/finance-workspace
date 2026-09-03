"""Reusable provider availability probes backed by the official SDKs."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import ApprovalMode, CodexConfig, Sandbox

from .results import classify_sdk_result
from .sdk import child_environment, executable, start_codex
from ..subprocess_supervision import hard_kill_claude_client, supervise_claude_turn, supervise_codex_turn

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
    """Run a bounded provider probe in an isolated temporary working tree."""

    with tempfile.TemporaryDirectory(prefix="phase-agent-probe-") as directory:
        cwd = Path(directory)
        if provider == "claude":
            return asyncio.run(_probe_claude(model, effort, timeout_seconds, cwd))
        if provider == "codex":
            return _probe_codex(model, effort, timeout_seconds, cwd)
    raise AssertionError("unreachable")
