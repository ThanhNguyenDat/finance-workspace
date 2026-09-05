import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from orchestrator.providers.base import BaseProvider, ProviderResult


class _FakeProvider(BaseProvider):
    """Minimal BaseProvider subclass exercising only the shared orchestration."""

    name = "fake"

    def __init__(self, *, events, hang: bool = False, accounts=None) -> None:
        super().__init__(accounts=accounts)
        self._events = events
        self._hang = hang
        self.interrupted = False
        self.closed = False
        self.started_with: tuple[str, str | None, str | None] | None = None

    async def start_turn(
        self, prompt: str, *, cwd: str | None, account: str | None
    ) -> None:
        self.started_with = (prompt, cwd, account)

    async def stream(self) -> AsyncIterator[Any]:
        if self._hang:
            await asyncio.sleep(10)
            return
        for event in self._events:
            yield event

    async def interrupt(self) -> None:
        self.interrupted = True

    async def aclose(self) -> None:
        self.closed = True

    def collect_result(self) -> ProviderResult:
        return ProviderResult(success=True, text="done", error=None)


class _FailoverProvider(BaseProvider):
    """Fake provider whose attempts fail until `succeed_on_attempt`, exercising
    the generic account-failover loop in BaseProvider.run_turn."""

    name = "fake-failover"
    ACCOUNT_FAILOVER_ERRORS = frozenset({"exhausted"})

    def __init__(
        self, *, accounts, succeed_on_attempt: int, error_code: str = "exhausted"
    ) -> None:
        super().__init__(accounts=accounts)
        self._succeed_on_attempt = succeed_on_attempt
        self._error_code = error_code
        self._attempt = -1
        self.started_accounts: list[str | None] = []

    async def start_turn(
        self, prompt: str, *, cwd: str | None, account: str | None
    ) -> None:
        self._attempt += 1
        self.started_accounts.append(account)

    async def stream(self) -> AsyncIterator[Any]:
        if self._attempt != self._succeed_on_attempt:
            self._last_error_code = self._error_code
        yield f"attempt-{self._attempt}"

    async def interrupt(self) -> None:
        pass

    def collect_result(self) -> ProviderResult:
        if self._attempt == self._succeed_on_attempt:
            return ProviderResult(success=True, text=f"ok-{self._attempt}", error=None)
        return ProviderResult(success=False, text=None, error=f"failed-{self._attempt}")


class _RaisingProvider(BaseProvider):
    """Fake provider whose stream() raises, exercising the generic exception
    safety net in `_run_one_attempt` (rather than a graceful failed result)."""

    name = "fake-raising"
    ACCOUNT_FAILOVER_ERRORS = frozenset({"exhausted"})

    def __init__(
        self,
        *,
        accounts=None,
        exc_factory=lambda: Exception("boom"),
        pre_set_error_code: str | None = None,
        classify_result: str | None = None,
        succeed_on_attempt: int | None = None,
    ) -> None:
        super().__init__(accounts=accounts)
        self._exc_factory = exc_factory
        self._pre_set_error_code = pre_set_error_code
        self._classify_result = classify_result
        self._succeed_on_attempt = succeed_on_attempt
        self._attempt = -1
        self.started_accounts: list[str | None] = []

    async def start_turn(
        self, prompt: str, *, cwd: str | None, account: str | None
    ) -> None:
        self._attempt += 1
        self.started_accounts.append(account)

    async def stream(self) -> AsyncIterator[Any]:
        if self._attempt == self._succeed_on_attempt:
            yield "ok"
            return
        if self._pre_set_error_code is not None:
            self._last_error_code = self._pre_set_error_code
            yield "pre-event"
        raise self._exc_factory()

    async def interrupt(self) -> None:
        pass

    def _classify_exception(self, exc: Exception) -> str | None:
        return self._classify_result

    def collect_result(self) -> ProviderResult:
        return ProviderResult(success=True, text=f"ok-{self._attempt}", error=None)


def test_exception_with_preset_error_code_triggers_failover() -> None:
    provider = _RaisingProvider(
        accounts=["one", "two"], pre_set_error_code="exhausted", succeed_on_attempt=1
    )
    result = asyncio.run(
        provider.run_turn("p", cwd=None, timeout_seconds=5, on_event=lambda _e: None)
    )
    assert result == ProviderResult(success=True, text="ok-1", error=None)
    assert provider.started_accounts == ["one", "two"]


def test_exception_without_classification_does_not_trigger_failover() -> None:
    provider = _RaisingProvider(accounts=["one", "two"], classify_result=None)
    result = asyncio.run(
        provider.run_turn("p", cwd=None, timeout_seconds=5, on_event=lambda _e: None)
    )
    assert result.success is False
    assert "boom" in (result.error or "")
    assert provider.started_accounts == ["one"]


def test_exception_classified_by_hook_triggers_failover() -> None:
    provider = _RaisingProvider(
        accounts=["one", "two"], classify_result="exhausted", succeed_on_attempt=1
    )
    result = asyncio.run(
        provider.run_turn("p", cwd=None, timeout_seconds=5, on_event=lambda _e: None)
    )
    assert result == ProviderResult(success=True, text="ok-1", error=None)
    assert provider.started_accounts == ["one", "two"]


def test_keyboard_interrupt_is_not_caught_by_the_exception_safety_net() -> None:
    provider = _RaisingProvider(accounts=["one"], exc_factory=KeyboardInterrupt)
    with pytest.raises(KeyboardInterrupt):
        asyncio.run(
            provider.run_turn(
                "p", cwd=None, timeout_seconds=5, on_event=lambda _e: None
            )
        )


def test_run_turn_forwards_events_and_returns_collected_result() -> None:
    seen: list[Any] = []
    provider = _FakeProvider(events=["a", "b"])

    result = asyncio.run(
        provider.run_turn("prompt", cwd="/tmp", timeout_seconds=5, on_event=seen.append)
    )

    assert seen == ["a", "b"]
    assert provider.started_with == ("prompt", "/tmp", None)
    assert result == ProviderResult(success=True, text="done", error=None)
    assert provider.closed is True


def test_run_turn_interrupts_and_closes_on_timeout() -> None:
    provider = _FakeProvider(events=[], hang=True)

    result = asyncio.run(
        provider.run_turn(
            "prompt", cwd=None, timeout_seconds=0.05, on_event=lambda _e: None
        )
    )

    assert result.success is False
    assert "did not complete" in (result.error or "")
    assert provider.interrupted is True
    assert provider.closed is True


def test_base_provider_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        BaseProvider()  # type: ignore[abstract]


def test_run_turn_defaults_to_single_ambient_account() -> None:
    provider = _FakeProvider(events=[])
    asyncio.run(
        provider.run_turn(
            "prompt", cwd=None, timeout_seconds=5, on_event=lambda _e: None
        )
    )
    assert provider.started_with == ("prompt", None, None)


def test_account_failover_advances_on_matching_error_code() -> None:
    provider = _FailoverProvider(accounts=["one", "two"], succeed_on_attempt=1)
    result = asyncio.run(
        provider.run_turn(
            "prompt", cwd=None, timeout_seconds=5, on_event=lambda _e: None
        )
    )
    assert result == ProviderResult(success=True, text="ok-1", error=None)
    assert provider.started_accounts == ["one", "two"]


def test_account_failover_stops_on_non_matching_error_code() -> None:
    provider = _FailoverProvider(
        accounts=["one", "two"], succeed_on_attempt=1, error_code="something-else"
    )
    result = asyncio.run(
        provider.run_turn(
            "prompt", cwd=None, timeout_seconds=5, on_event=lambda _e: None
        )
    )
    assert result == ProviderResult(success=False, text=None, error="failed-0")
    assert provider.started_accounts == ["one"]


def test_account_failover_exhausts_all_accounts() -> None:
    provider = _FailoverProvider(accounts=["one", "two"], succeed_on_attempt=99)
    result = asyncio.run(
        provider.run_turn(
            "prompt", cwd=None, timeout_seconds=5, on_event=lambda _e: None
        )
    )
    assert result == ProviderResult(success=False, text=None, error="failed-1")
    assert provider.started_accounts == ["one", "two"]
