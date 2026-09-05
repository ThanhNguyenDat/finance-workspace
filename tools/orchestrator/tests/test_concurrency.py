import asyncio

from orchestrator.cli import claude_exec, codex_exec

from .fakes import (
    FakeThread,
    FakeTurnHandle,
    claude_query_fn,
    claude_result,
    codex_factory,
    completed_event,
    item_event,
)


def test_codex_exec_and_claude_exec_run_concurrently_without_interacting(
    capsys,
) -> None:
    codex_handle = FakeTurnHandle([item_event("codex answer"), completed_event()])
    codex_thread = FakeThread(codex_handle)
    claude_messages = [claude_result(is_error=False, result="claude answer")]

    async def scenario() -> tuple[int, int]:
        return await asyncio.gather(
            codex_exec.run_turn(
                "codex prompt",
                cwd=None,
                timeout_seconds=5,
                codex_client_factory=codex_factory(codex_thread),
            ),
            claude_exec.run_turn(
                "claude prompt",
                cwd=None,
                timeout_seconds=5,
                query_fn=claude_query_fn(claude_messages),
            ),
        )

    codex_exit, claude_exit = asyncio.run(scenario())

    assert codex_exit == 0
    assert claude_exit == 0
    assert codex_thread.seen_prompt == "codex prompt"
    output = capsys.readouterr().out
    assert "codex answer" in output
    assert "claude answer" in output
