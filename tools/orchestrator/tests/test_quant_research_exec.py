from pathlib import Path

import pytest

from orchestrator.cli import _shared, quant_research_exec


def _write_domain_rules(cwd: Path, content: str) -> None:
    path = cwd / ".agents" / "domain" / "quant-research-domain.md"
    path.parent.mkdir(parents=True)
    path.write_text(content, encoding="utf-8")


def test_read_domain_rules_returns_raw_content(tmp_path) -> None:
    _write_domain_rules(tmp_path, "## Rules\nbody\n")

    assert quant_research_exec.read_domain_rules(tmp_path) == "## Rules\nbody\n"


def test_read_domain_rules_reports_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="domain rules not found"):
        quant_research_exec.read_domain_rules(tmp_path)


def test_read_domain_rules_makes_file_read_only(tmp_path) -> None:
    _write_domain_rules(tmp_path, "## Rules\nbody\n")
    path = tmp_path / ".agents" / "domain" / "quant-research-domain.md"

    quant_research_exec.read_domain_rules(tmp_path)

    assert not (path.stat().st_mode & 0o222)


def test_highest_round_number_scans_round_files(tmp_path) -> None:
    rounds_dir = tmp_path / "research" / "quant" / "rounds"
    rounds_dir.mkdir(parents=True)
    for name in ("round12-first.md", "round452-second.md", "round7-old.md"):
        (rounds_dir / name).write_text("round", encoding="utf-8")
    (rounds_dir / "round-not-a-number.md").write_text("ignored", encoding="utf-8")
    (rounds_dir / "round999-second.txt").write_text("ignored", encoding="utf-8")

    assert quant_research_exec.highest_round_number(tmp_path) == 452


def test_highest_round_number_returns_zero_for_empty_directory(tmp_path) -> None:
    (tmp_path / "research" / "quant" / "rounds").mkdir(parents=True)

    assert quant_research_exec.highest_round_number(tmp_path) == 0


def test_highest_round_number_returns_zero_for_missing_directory(tmp_path) -> None:
    assert quant_research_exec.highest_round_number(tmp_path) == 0


def test_parser_has_only_quant_research_flags(capsys) -> None:
    with pytest.raises(SystemExit):
        quant_research_exec.build_arg_parser().parse_args(["--help"])

    help_text = capsys.readouterr().out
    for flag in (
        "--prompt-file",
        "--round",
        "--role",
        "--cwd",
        "--timeout-seconds",
        "--model",
        "--effort",
    ):
        assert flag in help_text
    assert "--change" not in help_text
    assert "{implement,fix}" in help_text


def test_resolve_round_number_uses_explicit_round_without_scanning(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        quant_research_exec,
        "highest_round_number",
        lambda _cwd: pytest.fail("explicit round must not scan"),
    )

    assert (
        quant_research_exec.resolve_round_number("implement", 453, cwd=tmp_path) == 453
    )


def test_resolve_round_number_auto_detects_next_round(tmp_path) -> None:
    rounds_dir = tmp_path / "research" / "quant" / "rounds"
    rounds_dir.mkdir(parents=True)
    (rounds_dir / "round452-plan.md").write_text("round", encoding="utf-8")

    assert (
        quant_research_exec.resolve_round_number("implement", None, cwd=tmp_path) == 453
    )


def test_fix_without_round_exits_before_provider_call(tmp_path, capsys) -> None:
    def fail_factory(**_kwargs):
        raise AssertionError("provider must not be called")

    with pytest.raises(SystemExit) as exc_info:
        quant_research_exec.main(
            ["--role", "fix", "issue", "--cwd", str(tmp_path)],
            codex_client_factory=fail_factory,
        )

    assert exc_info.value.code != 0
    assert "--round is required" in capsys.readouterr().err


def test_derived_round_change_scopes_log_path(tmp_path) -> None:
    _write_domain_rules(tmp_path, "DOMAIN")
    from .fakes import (
        FakeThread,
        FakeTurnHandle,
        codex_factory,
        completed_event,
    )

    thread = FakeThread(FakeTurnHandle([completed_event()]))
    exit_code = quant_research_exec.main(
        [
            "--role",
            "implement",
            "--round",
            "453",
            "--cwd",
            str(tmp_path),
            "brief",
        ],
        codex_client_factory=codex_factory(thread),
    )

    assert exit_code == 0
    assert (
        _shared.LOGS_ROOT / "quant-research-round-453" / "quant-research-exec.log"
    ).is_file()


def test_prompt_uses_domain_body_then_round_brief(tmp_path) -> None:
    _write_domain_rules(tmp_path, "DOMAIN RULES")
    from .fakes import (
        FakeThread,
        FakeTurnHandle,
        codex_factory,
        completed_event,
    )

    thread = FakeThread(FakeTurnHandle([completed_event()]))
    exit_code = quant_research_exec.main(
        [
            "--role",
            "implement",
            "--round",
            "7",
            "--cwd",
            str(tmp_path),
            "specific plan",
        ],
        codex_client_factory=codex_factory(thread),
    )

    assert exit_code == 0
    assert thread.seen_prompt == (
        "DOMAIN RULES\n\n## This round's brief\n\nspecific plan"
    )
