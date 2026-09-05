import asyncio

import pytest

from orchestrator.utils.timeout import ProviderTimeoutError, run_with_timeout


def test_completes_within_deadline() -> None:
    async def fast() -> None:
        await asyncio.sleep(0)

    asyncio.run(run_with_timeout(fast(), timeout_seconds=1))


def test_raises_and_calls_on_timeout_when_deadline_exceeded() -> None:
    cleaned_up = False

    async def slow() -> None:
        await asyncio.sleep(10)

    async def on_timeout() -> None:
        nonlocal cleaned_up
        cleaned_up = True

    async def scenario() -> None:
        await run_with_timeout(slow(), timeout_seconds=0.05, on_timeout=on_timeout)

    with pytest.raises(ProviderTimeoutError):
        asyncio.run(scenario())

    assert cleaned_up is True
