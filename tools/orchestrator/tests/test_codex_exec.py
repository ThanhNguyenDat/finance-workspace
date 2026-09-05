import asyncio
import json

from orchestrator.cli import codex_exec

from .fakes import (
    FakeThread,
    FakeTurnHandle,
    HangingTurnHandle,
    codex_factory,
    completed_event,
    item_event,
)


def test_successful_run_prints_result_and_returns_zero(capsys) -> None:
    handle = FakeTurnHandle([item_event("final answer"), completed_event()])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
        )
    )
    assert exit_code == 0
    assert "final answer" in capsys.readouterr().out


def test_failed_turn_returns_nonzero_and_reports_error(capsys) -> None:
    handle = FakeTurnHandle([completed_event(status="failed", error_message="boom")])
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
    assert "boom" in capsys.readouterr().err


def test_missing_completion_event_returns_nonzero(capsys) -> None:
    handle = FakeTurnHandle([item_event("partial, never completes")])
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
    assert "without a completion" in capsys.readouterr().err


def test_timeout_interrupts_turn_and_returns_nonzero(capsys) -> None:
    handle = HangingTurnHandle()
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=0.05,
            codex_client_factory=codex_factory(thread),
        )
    )
    assert exit_code == 1
    assert "did not complete" in capsys.readouterr().err
    assert handle.interrupted is True


def test_prompt_file_and_positional_prompt_reach_thread_identically(tmp_path) -> None:
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("hello world", encoding="utf-8")

    handle_positional = FakeTurnHandle([completed_event()])
    thread_positional = FakeThread(handle_positional)
    exit_code_positional = codex_exec.main(
        ["hello world"], codex_client_factory=codex_factory(thread_positional)
    )

    handle_from_file = FakeTurnHandle([completed_event()])
    thread_from_file = FakeThread(handle_from_file)
    exit_code_from_file = codex_exec.main(
        ["--prompt-file", str(prompt_file)],
        codex_client_factory=codex_factory(thread_from_file),
    )

    assert exit_code_positional == 0
    assert exit_code_from_file == 0
    assert thread_positional.seen_prompt == "hello world"
    assert thread_from_file.seen_prompt == "hello world"


def test_model_and_effort_flags_reach_the_thread_turn_call() -> None:
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = codex_exec.main(
        ["hello", "--model", "gpt-5.2-codex", "--effort", "high"],
        codex_client_factory=codex_factory(thread),
    )
    assert exit_code == 0
    assert thread.seen_model == "gpt-5.2-codex"
    assert thread.seen_effort == "high"


def test_writes_a_jsonl_log_file_alongside_stdout(tmp_path, capsys) -> None:
    log_path = tmp_path / "codex-exec.log"
    handle = FakeTurnHandle([item_event("final answer"), completed_event()])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            log_path=log_path,
        )
    )
    assert exit_code == 0
    lines = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    types = [line["type"] for line in lines]
    assert types == ["event", "event", "result"]
    assert all("timestamp" in line for line in lines)
    assert lines[-1]["text"] == "final answer"


def test_log_file_records_errors_too(tmp_path) -> None:
    log_path = tmp_path / "codex-exec.log"
    handle = FakeTurnHandle([completed_event(status="failed", error_message="boom")])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            log_path=log_path,
        )
    )
    assert exit_code == 1
    lines = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    assert lines[-1] == {
        "type": "error",
        "message": "boom",
        "timestamp": lines[-1]["timestamp"],
    }


def test_no_log_path_given_writes_to_the_default_log_path() -> None:
    # conftest.py's autouse fixture points codex_exec.DEFAULT_LOG_PATH at an
    # isolated tmp directory for every test.
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = codex_exec.main(["hello"], codex_client_factory=codex_factory(thread))
    assert exit_code == 0
    assert codex_exec.DEFAULT_LOG_PATH.is_file()
