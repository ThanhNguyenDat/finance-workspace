from __future__ import annotations

import asyncio
import os
import stat
import time
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import Codex, CodexConfig

from orchestrator.subprocess_supervision import (
    supervise_claude_turn,
    supervise_codex_turn,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _wait_for_marker(path: Path) -> None:
    for _ in range(100):
        if path.exists():
            return
        time.sleep(0.01)
    raise AssertionError(f"fixture marker was not written: {path}")


class _CompletingClaude:
    def __init__(self) -> None:
        self.interrupt_calls = 0

    async def query(self, _prompt: str) -> None:
        return None

    async def receive_response(self):
        yield "completed"

    async def interrupt(self) -> None:
        self.interrupt_calls += 1


class _CompletingCodex:
    def __init__(self) -> None:
        self.interrupt_calls = 0

    def run(self) -> str:
        return "completed"

    def interrupt(self) -> None:
        self.interrupt_calls += 1


def test_claude_timer_is_cancelled_after_normal_completion() -> None:
    client = _CompletingClaude()
    outcome = asyncio.run(
        supervise_claude_turn(
            client,
            "prompt",
            timeout_seconds=1,
            kill_after_seconds=1,
        )
    )
    assert outcome.result == "completed"
    assert not outcome.timed_out
    assert not outcome.hard_killed
    assert client.interrupt_calls == 0


def test_codex_timer_is_cancelled_after_normal_completion() -> None:
    handle = _CompletingCodex()
    outcome = supervise_codex_turn(
        handle,
        timeout_seconds=1,
        kill_after_seconds=1,
    )
    assert outcome.result == "completed"
    assert not outcome.timed_out
    assert not outcome.hard_killed
    assert handle.interrupt_calls == 0


def test_claude_helper_hard_kills_after_ignored_interrupt(tmp_path: Path) -> None:
    cli = FIXTURES / "fake_claude_sdk_cli.py"
    _make_executable(cli)
    os.environ["CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK"] = "1"
    os.environ["FAKE_SDK_MODE"] = "hang"
    os.environ["FAKE_SDK_STARTED_MARKER"] = str(tmp_path / "started")
    os.environ["FAKE_SDK_INTERRUPT_MARKER"] = str(tmp_path / "interrupted")
    client = ClaudeSDKClient(
        ClaudeAgentOptions(cli_path=str(cli), permission_mode="bypassPermissions")
    )
    try:
        async def run() -> object:
            await client.connect()
            return await supervise_claude_turn(
                client,
                "prompt",
                timeout_seconds=0.05,
                kill_after_seconds=0.05,
            )

        outcome = asyncio.run(run())
        assert outcome.timed_out
        assert outcome.hard_killed
        _wait_for_marker(tmp_path / "interrupted")
    finally:
        asyncio.run(client.disconnect())
        for name in (
            "CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK",
            "FAKE_SDK_MODE",
            "FAKE_SDK_STARTED_MARKER",
            "FAKE_SDK_INTERRUPT_MARKER",
        ):
            os.environ.pop(name, None)


def test_codex_helper_hard_kills_after_ignored_interrupt(tmp_path: Path) -> None:
    cli = FIXTURES / "fake_codex_sdk_cli.py"
    _make_executable(cli)
    os.environ["FAKE_SDK_STARTED_MARKER"] = str(tmp_path / "started")
    os.environ["FAKE_SDK_INTERRUPT_MARKER"] = str(tmp_path / "interrupted")
    codex = Codex(CodexConfig(launch_args_override=(str(cli),)))
    try:
        handle = codex.thread_start().turn("prompt")
        _wait_for_marker(tmp_path / "started")
        outcome = supervise_codex_turn(
            handle,
            timeout_seconds=0.05,
            kill_after_seconds=0.05,
        )
        assert outcome.timed_out
        assert outcome.hard_killed
        _wait_for_marker(tmp_path / "interrupted")
    finally:
        codex.close()
        os.environ.pop("FAKE_SDK_STARTED_MARKER", None)
        os.environ.pop("FAKE_SDK_INTERRUPT_MARKER", None)
