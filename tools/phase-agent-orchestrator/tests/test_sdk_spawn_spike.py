from __future__ import annotations

import asyncio
import contextlib
import os
import stat
import threading
import time
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import Codex, CodexConfig


FIXTURES = Path(__file__).parent / "fixtures"


def _make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


async def _wait_for_marker(path: Path) -> None:
    for _ in range(100):
        if path.exists():
            return
        await asyncio.sleep(0.01)
    raise AssertionError(f"fixture marker was not written: {path}")


async def _kill_claude_after_ignored_interrupt(tmp_path: Path) -> None:
    cli = FIXTURES / "fake_claude_sdk_cli.py"
    _make_executable(cli)
    started = tmp_path / "claude-started"
    interrupted = tmp_path / "claude-interrupted"
    old_skip = os.environ.get("CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK")
    os.environ["CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK"] = "1"
    os.environ["FAKE_SDK_MODE"] = "hang"
    os.environ["FAKE_SDK_STARTED_MARKER"] = str(started)
    os.environ["FAKE_SDK_INTERRUPT_MARKER"] = str(interrupted)
    client = ClaudeSDKClient(
        ClaudeAgentOptions(cli_path=str(cli), permission_mode="bypassPermissions")
    )
    try:
        await client.connect()
        await client.query("fixture prompt")
        transport = client._transport
        assert transport is not None
        process = transport._process
        assert process is not None
        await _wait_for_marker(started)
        interrupt_task = asyncio.create_task(client.interrupt())
        await _wait_for_marker(interrupted)
        assert process.returncode is None
        process.kill()
        async with asyncio.timeout(2):
            await process.wait()
        assert process.returncode is not None
        interrupt_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await interrupt_task
    finally:
        await client.disconnect()
        for name in (
            "CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK",
            "FAKE_SDK_MODE",
            "FAKE_SDK_STARTED_MARKER",
            "FAKE_SDK_INTERRUPT_MARKER",
        ):
            os.environ.pop(name, None)
        if old_skip is not None:
            os.environ["CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK"] = old_skip


def test_claude_sdk_hard_kill_spike(tmp_path: Path) -> None:
    asyncio.run(_kill_claude_after_ignored_interrupt(tmp_path))


def test_codex_sdk_hard_kill_spike(tmp_path: Path) -> None:
    cli = FIXTURES / "fake_codex_sdk_cli.py"
    _make_executable(cli)
    started = tmp_path / "codex-started"
    interrupted = tmp_path / "codex-interrupted"
    old_started = os.environ.get("FAKE_SDK_STARTED_MARKER")
    old_interrupted = os.environ.get("FAKE_SDK_INTERRUPT_MARKER")
    os.environ["FAKE_SDK_STARTED_MARKER"] = str(started)
    os.environ["FAKE_SDK_INTERRUPT_MARKER"] = str(interrupted)
    codex = Codex(CodexConfig(launch_args_override=(str(cli),)))
    try:
        thread = codex.thread_start()
        handle = thread.turn("fixture prompt")
        for _ in range(100):
            if started.exists():
                break
            time.sleep(0.01)
        else:
            raise AssertionError(f"fixture marker was not written: {started}")
        client = codex._client
        process = client._proc
        assert process is not None
        interrupt_error: list[BaseException] = []

        def interrupt() -> None:
            try:
                handle.interrupt()
            except BaseException as error:  # the killed process unblocks this call
                interrupt_error.append(error)

        interrupt_thread = threading.Thread(target=interrupt)
        interrupt_thread.start()
        for _ in range(100):
            if interrupted.exists():
                break
            time.sleep(0.01)
        else:
            raise AssertionError(f"fixture marker was not written: {interrupted}")
        assert process.poll() is None
        process.kill()
        process.wait(timeout=2)
        assert process.poll() is not None
        interrupt_thread.join(timeout=2)
        assert not interrupt_thread.is_alive()
    finally:
        codex.close()
        if old_started is None:
            os.environ.pop("FAKE_SDK_STARTED_MARKER", None)
        else:
            os.environ["FAKE_SDK_STARTED_MARKER"] = old_started
        if old_interrupted is None:
            os.environ.pop("FAKE_SDK_INTERRUPT_MARKER", None)
        else:
            os.environ["FAKE_SDK_INTERRUPT_MARKER"] = old_interrupted
