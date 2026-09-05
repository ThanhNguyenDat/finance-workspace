import asyncio

from orchestrator.cli import codex_exec

from .fakes import FakeCodexClient, FakeThread, RaisingTurnHandle, codex_factory


def test_generic_exception_produces_clean_nonzero_exit_not_a_crash(capsys) -> None:
    handle = RaisingTurnHandle(RuntimeError("connection dropped"))
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
        )
    )
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "RuntimeError" in err
    assert "connection dropped" in err


def _sequenced_raising_factory(handles: list):
    """Like fakes.sequenced_codex_factory, but for a pre-built list of
    handles (mixing RaisingTurnHandle and FakeTurnHandle) instead of raw
    event sequences -- returns (factory, threads_created)."""

    threads: list[FakeThread] = []

    def factory(*, config=None):
        thread = FakeThread(handles[len(threads)])
        threads.append(thread)
        return FakeCodexClient(thread, config=config)

    return factory, threads


def test_generic_exception_does_not_trigger_failover_without_classification() -> None:
    handles = [
        RaisingTurnHandle(RuntimeError("connection dropped")),
        RaisingTurnHandle(RuntimeError("should never be reached")),
    ]
    factory, threads = _sequenced_raising_factory(handles)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    # Only the first account's thread was ever created -- no failover attempt.
    assert len(threads) == 1
    assert threads[0].seen_prompt == "do the thing"
