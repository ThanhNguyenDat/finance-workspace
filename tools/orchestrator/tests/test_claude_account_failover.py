import asyncio

from claude_agent_sdk import AssistantMessage

from orchestrator.cli import claude_exec

from .fakes import claude_result


def _sequenced_query_fn(sequences):
    """Return (query_fn, calls). Each call to query_fn consumes the next
    sequence and records the CLAUDE_CONFIG_DIR override it was given."""

    calls: list[str | None] = []

    def query_fn(*, prompt, options):
        index = len(calls)
        calls.append(options.env.get("CLAUDE_CONFIG_DIR"))
        messages = sequences[index]

        async def gen():
            for message in messages:
                yield message

        return gen()

    return query_fn, calls


def _rate_limited_turn() -> list:
    return [AssistantMessage(content=[], model="claude", error="rate_limit")]


def _invalid_request_turn() -> list:
    return [AssistantMessage(content=[], model="claude", error="invalid_request")]


def test_fails_over_to_second_account_on_rate_limit(capsys) -> None:
    query_fn, calls = _sequenced_query_fn(
        [
            _rate_limited_turn(),
            [claude_result(is_error=False, result="second account ok")],
        ]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 0
    assert "second account ok" in capsys.readouterr().out
    assert calls == ["/accounts/one", "/accounts/two"]


def test_non_account_shaped_failure_does_not_retry(capsys) -> None:
    query_fn, calls = _sequenced_query_fn(
        [_invalid_request_turn(), [claude_result(is_error=False, result="unreachable")]]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert calls == ["/accounts/one"]


def test_all_accounts_exhausted_returns_final_error_and_stops(capsys) -> None:
    query_fn, calls = _sequenced_query_fn([_rate_limited_turn(), _rate_limited_turn()])
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert "without a result" in capsys.readouterr().err
    assert calls == ["/accounts/one", "/accounts/two"]


def test_no_accounts_configured_makes_exactly_one_attempt(capsys) -> None:
    query_fn, calls = _sequenced_query_fn(
        [[claude_result(is_error=False, result="ok")]]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "prompt", cwd=None, timeout_seconds=5, query_fn=query_fn, accounts=None
        )
    )
    assert exit_code == 0
    assert calls == [None]


def test_failover_loop_creates_no_files_outside_cwd(tmp_path) -> None:
    before = set(tmp_path.iterdir())
    query_fn, _calls = _sequenced_query_fn(
        [_rate_limited_turn(), [claude_result(is_error=False, result="ok")]]
    )
    asyncio.run(
        claude_exec.run_turn(
            "prompt",
            cwd=str(tmp_path),
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    after = set(tmp_path.iterdir())
    assert after == before
