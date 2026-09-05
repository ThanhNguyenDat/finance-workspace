"""Bound a provider turn to a wall-clock deadline."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

DEFAULT_TIMEOUT_SECONDS = 300


class ProviderTimeoutError(Exception):
    """Raised when a provider turn does not complete within its deadline."""

    def __init__(self, timeout_seconds: float) -> None:
        super().__init__(f"provider turn did not complete within {timeout_seconds}s")
        self.timeout_seconds = timeout_seconds


async def run_with_timeout(
    coro: Awaitable[None],
    *,
    timeout_seconds: float,
    on_timeout: Callable[[], Awaitable[Any]] | None = None,
) -> None:
    """Await `coro`, cancelling it and raising `ProviderTimeoutError` on expiry.

    `on_timeout`, when given, is awaited after cancellation so the caller can
    ask the provider to interrupt its in-flight turn before the process exits.
    """

    try:
        await asyncio.wait_for(coro, timeout=timeout_seconds)
    except (asyncio.TimeoutError, TimeoutError) as exc:
        if on_timeout is not None:
            await on_timeout()
        raise ProviderTimeoutError(timeout_seconds) from exc
