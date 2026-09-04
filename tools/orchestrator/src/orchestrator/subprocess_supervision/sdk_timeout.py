"""Bounded timeout handling for the Claude and Codex Python SDKs.

The SDK-native interrupt is always attempted first.  If the provider does not
finish within the kill-after grace period, this module uses the SDK-owned
process handle to force termination.  The private handle access is isolated
here so SDK upgrades have one small compatibility surface to re-check.
"""

from __future__ import annotations

import asyncio
import contextlib
import threading
from collections.abc import Callable
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Generic, TypeVar

ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class SupervisionOutcome(Generic[ResultT]):
    """The terminal observation from one provider turn."""

    result: ResultT | None
    timed_out: bool = False
    hard_killed: bool = False


def hard_kill_claude_client(client: Any) -> bool:
    """Kill the process owned by a connected ``ClaudeSDKClient``."""

    transport = getattr(client, "_transport", None)
    process = getattr(transport, "_process", None)
    if process is None or process.returncode is not None:
        return False
    with contextlib.suppress(ProcessLookupError):
        process.kill()
    return True


def hard_kill_codex_turn(turn_handle: Any) -> bool:
    """Kill the process owned by an ``openai_codex.TurnHandle``."""

    sdk_client = getattr(turn_handle, "_client", None)
    process = getattr(sdk_client, "_proc", None)
    if process is None or process.poll() is not None:
        return False
    with contextlib.suppress(ProcessLookupError):
        process.kill()
    return True


async def _collect_claude_turn(
    client: Any, prompt: str, on_message: Callable[[Any], None] | None = None
) -> Any:
    await client.query(prompt)
    result = None
    async for message in client.receive_response():
        if on_message is not None:
            on_message(message)
        result = message
    return result


async def supervise_claude_turn(
    client: Any,
    prompt: str,
    *,
    timeout_seconds: float,
    kill_after_seconds: float,
    on_message: Callable[[Any], None] | None = None,
) -> SupervisionOutcome[Any]:
    """Run one streaming Claude turn with interrupt then hard-kill escalation."""

    turn_task = asyncio.create_task(_collect_claude_turn(client, prompt, on_message))
    try:
        result = await asyncio.wait_for(asyncio.shield(turn_task), timeout_seconds)
        return SupervisionOutcome(result=result)
    except TimeoutError:
        interrupt_task = asyncio.create_task(client.interrupt())
        try:
            result = await asyncio.wait_for(
                asyncio.shield(turn_task), kill_after_seconds
            )
            return SupervisionOutcome(result=result, timed_out=True)
        except TimeoutError:
            hard_killed = hard_kill_claude_client(client)
            turn_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await turn_task
            return SupervisionOutcome(
                result=None, timed_out=True, hard_killed=hard_killed
            )
        finally:
            if not interrupt_task.done():
                interrupt_task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await interrupt_task


def _thread_result(target: Any) -> tuple[threading.Thread, Queue[tuple[str, Any]]]:
    result_queue: Queue[tuple[str, Any]] = Queue(maxsize=1)

    def run() -> None:
        try:
            result_queue.put(("result", target()))
        except BaseException as error:  # propagate provider failures to caller
            result_queue.put(("error", error))

    worker = threading.Thread(target=run, name="phase-agent-sdk-turn")
    worker.start()
    return worker, result_queue


def _get_thread_result(result_queue: Queue[tuple[str, Any]]) -> Any:
    kind, value = result_queue.get_nowait()
    if kind == "error":
        raise value
    return value


def _collect_codex_turn(
    turn_handle: Any, on_message: Callable[[Any], None] | None = None
) -> Any:
    from openai_codex._run import _collect_turn_result  # noqa: PLC0415

    stream = turn_handle.stream()
    try:

        def _tee() -> Any:
            for event in stream:
                if on_message is not None:
                    on_message(event)
                yield event

        return _collect_turn_result(_tee(), turn_id=turn_handle.id)
    finally:
        stream.close()


def supervise_codex_turn(
    turn_handle: Any,
    *,
    timeout_seconds: float,
    kill_after_seconds: float,
    on_message: Callable[[Any], None] | None = None,
) -> SupervisionOutcome[Any]:
    """Run one streaming Codex turn with interrupt then hard-kill escalation."""

    worker, result_queue = _thread_result(
        lambda: _collect_codex_turn(turn_handle, on_message)
    )
    worker.join(timeout_seconds)
    if worker.is_alive():
        interrupt_worker, interrupt_queue = _thread_result(turn_handle.interrupt)
        interrupt_worker.join(kill_after_seconds)
        if worker.is_alive():
            hard_killed = hard_kill_codex_turn(turn_handle)
            worker.join(timeout=2)
            return SupervisionOutcome(
                result=None, timed_out=True, hard_killed=hard_killed
            )
        with contextlib.suppress(Empty, Exception):
            _get_thread_result(interrupt_queue)
        if not result_queue.empty():
            return SupervisionOutcome(
                result=_get_thread_result(result_queue), timed_out=True
            )
        return SupervisionOutcome(result=None, timed_out=True)

    return SupervisionOutcome(result=_get_thread_result(result_queue))
