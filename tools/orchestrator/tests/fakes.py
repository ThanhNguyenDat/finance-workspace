"""Fake Codex/Claude SDK backends shared across orchestrator CLI tests."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from claude_agent_sdk import ResultMessage


# --- Codex fakes -----------------------------------------------------------


def event(method: str, payload) -> SimpleNamespace:
    return SimpleNamespace(method=method, payload=payload)


def item_event(text: str) -> SimpleNamespace:
    return event("item/completed", SimpleNamespace(item=SimpleNamespace(text=text)))


def completed_event(
    *,
    status: str = "completed",
    error_message: str | None = None,
    error_code: str | None = None,
):
    error = None
    if error_message or error_code:
        codex_error_info = SimpleNamespace(value=error_code) if error_code else None
        error = SimpleNamespace(
            message=error_message, codex_error_info=codex_error_info
        )
    turn = SimpleNamespace(status=SimpleNamespace(value=status), error=error)
    return event("turn/completed", SimpleNamespace(turn=turn))


class FakeTurnHandle:
    def __init__(self, events):
        self._events = events
        self.interrupted = False

    async def stream(self):
        for turn_event in self._events:
            yield turn_event

    async def interrupt(self):
        self.interrupted = True


class HangingTurnHandle:
    def __init__(self):
        self.interrupted = False

    async def stream(self):
        await asyncio.sleep(10)
        if False:  # pragma: no cover - keeps this an async generator
            yield None

    async def interrupt(self):
        self.interrupted = True


class FakeThread:
    def __init__(self, handle):
        self._handle = handle
        self.seen_prompt: str | None = None
        self.seen_model: str | None = None
        self.seen_effort: str | None = None

    async def turn(self, prompt, *, cwd=None, model=None, effort=None):
        self.seen_prompt = prompt
        self.seen_model = model
        self.seen_effort = effort
        return self._handle


class FakeCodexClient:
    def __init__(self, thread, *, config=None):
        self._thread = thread

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def thread_start(self, **kwargs):
        return self._thread


def codex_factory(thread: FakeThread):
    def factory(*, config=None):
        return FakeCodexClient(thread, config=config)

    return factory


def sequenced_codex_factory(event_sequences: list[list]):
    """Return (factory, calls). Each call consumes the next events sequence
    and records the CODEX_HOME override its CodexConfig was given."""

    calls: list[str | None] = []

    def factory(*, config=None):
        index = len(calls)
        calls.append(config.env.get("CODEX_HOME") if config and config.env else None)
        handle = FakeTurnHandle(event_sequences[index])
        thread = FakeThread(handle)
        return FakeCodexClient(thread, config=config)

    return factory, calls


# --- Claude fakes ------------------------------------------------------------


def claude_result(
    *, is_error: bool, result: str | None = "final answer"
) -> ResultMessage:
    return ResultMessage(
        subtype="success" if not is_error else "error",
        duration_ms=1,
        duration_api_ms=1,
        is_error=is_error,
        num_turns=1,
        session_id="s1",
        result=result,
    )


def claude_query_fn(messages):
    """Build a query_fn(prompt=..., options=...) fake yielding fixed messages."""

    async def query_fn(*, prompt, options):
        for message in messages:
            yield message

    return query_fn
