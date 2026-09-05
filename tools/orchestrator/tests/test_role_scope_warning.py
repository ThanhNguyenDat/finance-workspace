import asyncio

from orchestrator.cli import claude_exec, codex_exec
from orchestrator.utils import config as config_module

from .fakes import (
    FakeThread,
    FakeTurnHandle,
    claude_query_fn,
    claude_result,
    codex_factory,
    completed_event,
)


def _write_scope(tmp_path, monkeypatch, provider: str, scope: list[str]) -> None:
    config_file = tmp_path / "config.yaml"
    scope_yaml = "\n".join(f"    - {role}" for role in scope)
    config_file.write_text(f"{provider}:\n  scope:\n{scope_yaml}\n", encoding="utf-8")
    monkeypatch.setattr(config_module, "CONFIG_PATH", config_file)


def test_codex_role_in_scope_prints_no_warning(tmp_path, monkeypatch, capsys) -> None:
    _write_scope(tmp_path, monkeypatch, "codex", ["implement", "fix"])
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            role="implement",
        )
    )
    assert exit_code == 0
    assert "warning" not in capsys.readouterr().err


def test_codex_role_outside_scope_warns_but_still_succeeds(
    tmp_path, monkeypatch, capsys
) -> None:
    _write_scope(tmp_path, monkeypatch, "codex", ["implement", "fix"])
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            role="plan",
        )
    )
    assert exit_code == 0
    err = capsys.readouterr().err
    assert "warning" in err
    assert "plan" in err
    assert "implement, fix" in err


def test_codex_role_outside_scope_warning_does_not_mask_a_real_failure(
    tmp_path, monkeypatch, capsys
) -> None:
    _write_scope(tmp_path, monkeypatch, "codex", ["implement", "fix"])
    handle = FakeTurnHandle([completed_event(status="failed", error_message="boom")])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            role="plan",
        )
    )
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "warning" in err
    assert "boom" in err


def test_codex_no_role_given_prints_no_warning_even_with_scope_configured(
    tmp_path, monkeypatch, capsys
) -> None:
    _write_scope(tmp_path, monkeypatch, "codex", ["implement"])
    handle = FakeTurnHandle([completed_event()])
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
    assert "warning" not in capsys.readouterr().err


def test_codex_role_given_but_no_scope_configured_prints_no_warning(capsys) -> None:
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = asyncio.run(
        codex_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            codex_client_factory=codex_factory(thread),
            role="plan",
        )
    )
    assert exit_code == 0
    assert "warning" not in capsys.readouterr().err


def test_role_flag_reaches_run_turn_via_main(tmp_path, monkeypatch, capsys) -> None:
    _write_scope(tmp_path, monkeypatch, "codex", ["implement"])
    handle = FakeTurnHandle([completed_event()])
    thread = FakeThread(handle)
    exit_code = codex_exec.main(
        ["hello", "--role", "plan"], codex_client_factory=codex_factory(thread)
    )
    assert exit_code == 0
    assert "plan" in capsys.readouterr().err


def test_claude_role_outside_scope_warns_but_still_succeeds(
    tmp_path, monkeypatch, capsys
) -> None:
    _write_scope(tmp_path, monkeypatch, "claude", ["plan", "verify", "final_verify"])
    messages = [claude_result(is_error=False, result="ok")]
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
            role="implement",
        )
    )
    assert exit_code == 0
    err = capsys.readouterr().err
    assert "warning" in err
    assert "implement" in err


def test_claude_role_in_scope_prints_no_warning(tmp_path, monkeypatch, capsys) -> None:
    _write_scope(tmp_path, monkeypatch, "claude", ["plan", "verify", "final_verify"])
    messages = [claude_result(is_error=False, result="ok")]
    exit_code = asyncio.run(
        claude_exec.run_turn(
            "do the thing",
            cwd=None,
            timeout_seconds=5,
            query_fn=claude_query_fn(messages),
            role="verify",
        )
    )
    assert exit_code == 0
    assert "warning" not in capsys.readouterr().err
