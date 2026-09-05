"""Provider interface: run exactly one bounded, stateless SDK turn.

Includes optional account failover, shared by every subclass: when a
subclass is constructed with more than one account and `stream()` records a
failover-shaped error code in `self._last_error_code`, `run_turn` retries the
same prompt against the next account before giving up. A subclass that never
sets `_last_error_code` (or is constructed with a single account) behaves
exactly like a plain one-shot provider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any

from ..utils.timeout import ProviderTimeoutError, run_with_timeout


@dataclass(slots=True)
class ProviderResult:
    success: bool
    text: str | None
    error: str | None


class BaseProvider(ABC):
    """One-shot, stateless interface for a single bounded provider turn.

    A concrete provider (`CodexProvider`, `ClaudeProvider`, ...) implements
    `start_turn`/`stream`/`interrupt`/`collect_result` and sets
    `ACCOUNT_FAILOVER_ERRORS`. `run_turn` is the shared orchestration every
    subclass gets for free: try each configured account in order, forward
    each raw event to `on_event`, enforce `timeout_seconds` by calling
    `interrupt()` on expiry, always release resources via `aclose()`, and
    return a `ProviderResult(success, text, error)`.
    """

    name: str
    ACCOUNT_FAILOVER_ERRORS: frozenset[str] = frozenset()

    def __init__(self, *, accounts: list[str | None] | None = None) -> None:
        self._accounts: list[str | None] = accounts if accounts else [None]
        self._last_error_code: str | None = None

    @abstractmethod
    async def start_turn(
        self, prompt: str, *, cwd: str | None, account: str | None
    ) -> None:
        """Begin the turn on the given account. Must precede stream()/interrupt()."""

    @abstractmethod
    def stream(self) -> AsyncIterator[Any]:
        """Yield raw provider events for the turn started by start_turn().

        Implementations should set `self._last_error_code` to a failover
        code (from `ACCOUNT_FAILOVER_ERRORS`) when the stream carries one.
        """

    @abstractmethod
    async def interrupt(self) -> None:
        """Best-effort request to stop the in-flight turn."""

    @abstractmethod
    def collect_result(self) -> ProviderResult:
        """Return the final result. Only valid after stream() is exhausted."""

    async def aclose(self) -> None:  # noqa: B027 - intentionally optional to override
        """Release resources. Default no-op; override if a provider needs one."""

    async def _run_one_attempt(
        self,
        prompt: str,
        *,
        cwd: str | None,
        account: str | None,
        timeout_seconds: float,
        on_event: Callable[[Any], None],
    ) -> ProviderResult:
        self._last_error_code = None
        await self.start_turn(prompt, cwd=cwd, account=account)

        async def _consume() -> None:
            async for turn_event in self.stream():
                on_event(turn_event)

        try:
            try:
                await run_with_timeout(
                    _consume(),
                    timeout_seconds=timeout_seconds,
                    on_timeout=self.interrupt,
                )
            except ProviderTimeoutError as exc:
                return ProviderResult(success=False, text=None, error=str(exc))
        finally:
            await self.aclose()

        return self.collect_result()

    async def run_turn(
        self,
        prompt: str,
        *,
        cwd: str | None,
        timeout_seconds: float,
        on_event: Callable[[Any], None],
    ) -> ProviderResult:
        result: ProviderResult | None = None
        for index, account in enumerate(self._accounts):
            result = await self._run_one_attempt(
                prompt,
                cwd=cwd,
                account=account,
                timeout_seconds=timeout_seconds,
                on_event=on_event,
            )
            if result.success:
                return result
            has_more_accounts = index < len(self._accounts) - 1
            if not (
                has_more_accounts
                and self._last_error_code in self.ACCOUNT_FAILOVER_ERRORS
            ):
                return result
        assert result is not None  # self._accounts is always non-empty
        return result
