import asyncio

from orchestrator.cli import codex_exec

from .fakes import completed_event, sequenced_codex_factory


def test_fails_over_to_second_account_on_usage_limit(capsys) -> None:
    factory, calls = sequenced_codex_factory(
        [
            [completed_event(status="failed", error_code="usage_limit_exceeded")],
            [completed_event(status="completed")],
        ]
    )
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 0
    assert calls == ["/accounts/one", "/accounts/two"]


def test_non_account_shaped_failure_does_not_retry() -> None:
    factory, calls = sequenced_codex_factory(
        [
            [completed_event(status="failed", error_message="bad prompt")],
            [completed_event(status="completed")],
        ]
    )
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert calls == ["/accounts/one"]


def test_all_accounts_exhausted_returns_final_error_and_stops(capsys) -> None:
    factory, calls = sequenced_codex_factory(
        [
            [
                completed_event(
                    status="failed", error_code="unauthorized", error_message="e1"
                )
            ],
            [
                completed_event(
                    status="failed", error_code="unauthorized", error_message="e2"
                )
            ],
        ]
    )
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    assert exit_code == 1
    assert "e2" in capsys.readouterr().err
    assert calls == ["/accounts/one", "/accounts/two"]


def test_no_accounts_configured_makes_exactly_one_attempt() -> None:
    factory, calls = sequenced_codex_factory([[completed_event(status="completed")]])
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "prompt",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=None,
        )
    )
    assert exit_code == 0
    assert calls == [None]


def test_failover_loop_creates_no_files_outside_cwd(tmp_path) -> None:
    before = set(tmp_path.iterdir())
    factory, _calls = sequenced_codex_factory(
        [
            [completed_event(status="failed", error_code="usage_limit_exceeded")],
            [completed_event(status="completed")],
        ]
    )
    asyncio.run(
        codex_exec.run_turn(
            "prompt",
            cwd=str(tmp_path),
            timeout_seconds=5,
            codex_client_factory=factory,
            accounts=["/accounts/one", "/accounts/two"],
        )
    )
    after = set(tmp_path.iterdir())
    assert after == before
