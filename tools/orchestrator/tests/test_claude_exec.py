import asyncio

from claude_agent_sdk import AssistantMessage, TextBlock

from orchestrator.cli import claude_exec

from .fakes import claude_query_fn, claude_result


def test_successful_run_prints_result_and_returns_zero(capsys) -> None:
    messages = [
        AssistantMessage(content=[TextBlock(text="thinking...")], model="claude"),
        claude_result(is_error=False, result="final answer"),
    ]
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
        )
    )
    assert exit_code == 0
    assert "final answer" in capsys.readouterr().out


def test_failed_turn_returns_nonzero_and_reports_error(capsys) -> None:
    messages = [claude_result(is_error=True, result="boom")]
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
        )
    )
    assert exit_code == 1
    assert "boom" in capsys.readouterr().err


def test_missing_result_message_returns_nonzero(capsys) -> None:
    messages = [
        AssistantMessage(content=[TextBlock(text="no result follows")], model="claude")
    ]
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
        )
    )
    assert exit_code == 1
    assert "without a result" in capsys.readouterr().err


class _HangingStream:
    """Duck-typed async stream whose `aclose()` call is directly observable.

    A bare async generator's teardown-on-cancellation timing is an asyncio
    implementation detail; wrapping it lets the test assert on the actual
    contract instead: BaseProvider must call interrupt() -> aclose() on
    timeout.
    """

    def __init__(self) -> None:
        self.aclose_called = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(10)
        raise StopAsyncIteration

    async def aclose(self) -> None:
        self.aclose_called = True


def test_timeout_closes_stream_and_returns_nonzero(capsys) -> None:
    stream = _HangingStream()

    def query_fn(*, prompt, options):
        return stream

    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing", cwd=None, timeout_seconds=0.05, query_fn=query_fn
        )
    )
    assert exit_code == 1
    assert "did not complete" in capsys.readouterr().err
    assert stream.aclose_called is True


def test_prompt_file_and_positional_prompt_reach_query_identically(tmp_path) -> None:
    seen_prompts: list[str] = []

    def capturing_query_fn(messages):
        async def query_fn(*, prompt, options):
            seen_prompts.append(prompt)
            for message in messages:
                yield message

        return query_fn

    result_messages = [claude_result(is_error=False, result="ok")]
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("hello world", encoding="utf-8")

    exit_code_positional = claude_exec.main(
        ["hello world"], query_fn=capturing_query_fn(result_messages)
    )
    exit_code_from_file = claude_exec.main(
        ["--prompt-file", str(prompt_file)],
        query_fn=capturing_query_fn(result_messages),
    )

    assert exit_code_positional == 0
    assert exit_code_from_file == 0
    assert seen_prompts == ["hello world", "hello world"]


def test_model_and_effort_flags_reach_claude_agent_options() -> None:
    seen_options = []

    def query_fn(*, prompt, options):
        seen_options.append(options)

        async def gen():
            yield claude_result(is_error=False, result="ok")

        return gen()

    exit_code = claude_exec.main(
        ["hello", "--model", "claude-opus-5", "--effort", "high"], query_fn=query_fn
    )
    assert exit_code == 0
    assert seen_options[0].model == "claude-opus-5"
    assert seen_options[0].effort == "high"
