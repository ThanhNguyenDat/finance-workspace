import asyncio

from claude_agent_sdk import AssistantMessage, ResultError

from orchestrator.cli import claude_exec

from .fakes import claude_result


def _raising_query_fn(sequences_then_raise):
    """Build a query_fn(prompt=..., options=...) fake per call, yielding the
    next sequence's messages then raising its exception (or succeeding if
    the sequence has no exception)."""

    calls = {"count": 0}

    def query_fn(*, prompt, options):
        index = calls["count"]
        calls["count"] += 1
        messages, exc = sequences_then_raise[index]

        async def gen():
            for message in messages:
                yield message
            if exc is not None:
                raise exc

        return gen()

    return query_fn, calls


def test_result_error_with_mapped_status_triggers_failover(capsys) -> None:
    query_fn, calls = _raising_query_fn(
        [
            ([], ResultError("boom", data={"api_error_status": 429})),
            ([claude_result(is_error=False, result="ok")], None),
        ]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 0
    assert calls["count"] == 2
    assert "ok" in capsys.readouterr().out


def test_result_error_with_unmapped_status_does_not_trigger_failover(capsys) -> None:
    query_fn, calls = _raising_query_fn(
        [
            ([], ResultError("server exploded", data={"api_error_status": 500})),
            ([claude_result(is_error=False, result="unreachable")], None),
        ]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert calls["count"] == 1
    assert "ResultError" in capsys.readouterr().err


def test_preceding_event_classification_takes_precedence_over_exception(capsys) -> None:
    # AssistantMessage.error is a non-failover code; the ResultError's own
    # status (429 -> rate_limit) must NOT override it, so no failover here
    # even though 429 alone would normally trigger one.
    query_fn, calls = _raising_query_fn(
        [
            (
                [AssistantMessage(content=[], model="claude", error="invalid_request")],
                ResultError("boom", data={"api_error_status": 429}),
            ),
            ([claude_result(is_error=False, result="unreachable")], None),
        ]
    )
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=query_fn,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert calls["count"] == 1
