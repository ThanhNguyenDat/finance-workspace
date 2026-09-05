import json
import subprocess
from pathlib import Path

import pytest

from orchestrator.cli import _shared, quant_research_exec
from .fakes import (
    FakeCodexClient,
    FakeThread,
    FakeTurnHandle,
    claude_result,
    completed_event,
    wrapped_item_event,
)


def _run(*args, **kwargs):
    kwargs.setdefault("timeout", 10)
    return subprocess.run(*args, **kwargs)


def _write_repo_files(cwd: Path, *, domain: str = "DOMAIN") -> None:
    (cwd / ".agents" / "domain").mkdir(parents=True)
    (cwd / ".agents" / "domain" / "quant-research-domain.md").write_text(
        domain, encoding="utf-8"
    )
    (cwd / "research" / "quant" / "reports").mkdir(parents=True)
    (cwd / "research" / "quant" / "rounds").mkdir(parents=True)
    (cwd / "research" / "quant" / "index.md").write_text("INDEX", encoding="utf-8")
    (cwd / "research" / "quant" / "reports" / "optimize_loop_update_v2.csv").write_text(
        "CSV", encoding="utf-8"
    )


def _codex_factory(texts, calls):
    def factory(*, config=None):
        index = len(calls)
        calls.append({"resume": None, "config": config})
        handle = FakeTurnHandle([wrapped_item_event(texts[index]), completed_event()])

        class RecordingThread(FakeThread):
            async def turn(self, prompt, *, cwd=None, model=None, effort=None):
                calls[index].update(
                    {
                        "prompt": prompt,
                        "cwd": cwd,
                        "model": model,
                        "effort": effort,
                    }
                )
                return await super().turn(prompt, cwd=cwd, model=model, effort=effort)

        thread = RecordingThread(handle, thread_id=f"codex-{index}")

        class Client(FakeCodexClient):
            async def thread_start(self, **kwargs):
                calls[index]["start"] = True
                return thread

            async def thread_resume(self, thread_id, **kwargs):
                calls[index]["resume"] = thread_id
                return thread

        return Client(thread, config=config)

    return factory


def _claude_query(results, calls):
    def query_fn(*, prompt, options):
        index = len(calls)
        calls.append({"prompt": prompt, "options": options})
        result = results[index]

        async def stream():
            yield claude_result(is_error=False, result=result)

        return stream()

    return query_fn


def test_read_domain_rules_returns_raw_content(tmp_path):
    _write_repo_files(tmp_path, domain="## Rules\nbody\n")
    assert quant_research_exec.read_domain_rules(tmp_path) == "## Rules\nbody\n"


def test_read_domain_rules_reports_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="domain rules not found"):
        quant_research_exec.read_domain_rules(tmp_path)


def test_read_domain_rules_makes_file_read_only(tmp_path):
    _write_repo_files(tmp_path)
    path = tmp_path / ".agents" / "domain" / "quant-research-domain.md"
    quant_research_exec.read_domain_rules(tmp_path)
    assert not (path.stat().st_mode & 0o222)


def test_highest_round_number_scans_round_files(tmp_path):
    rounds = tmp_path / "research" / "quant" / "rounds"
    rounds.mkdir(parents=True)
    for name in ("round12-first.md", "round452-second.md", "round7-old.md"):
        (rounds / name).write_text("round", encoding="utf-8")
    (rounds / "round-not-a-number.md").write_text("ignored", encoding="utf-8")
    assert quant_research_exec.highest_round_number(tmp_path) == 452


def test_parser_has_new_zero_argument_surface(capsys):
    with pytest.raises(SystemExit):
        quant_research_exec.build_arg_parser().parse_args(["--help"])
    help_text = capsys.readouterr().out
    for flag in (
        "--prompt-file",
        "--round",
        "--cwd",
        "--timeout-seconds",
        "--codex-model",
        "--codex-effort",
        "--codex-escalated-model",
        "--claude-model",
        "--claude-effort",
        "--claude-escalated-model",
    ):
        assert flag in help_text
    for flag in ("--role", "--model", "--effort"):
        assert flag not in help_text
    assert quant_research_exec.build_arg_parser().parse_args([]).prompt is None


def test_resolve_round_number_uses_explicit_round_without_scanning(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        quant_research_exec,
        "highest_round_number",
        lambda _cwd: pytest.fail("explicit round must not scan"),
    )
    assert quant_research_exec.resolve_round_number(453, cwd=tmp_path) == 453


def test_resolve_round_number_auto_detects_next_round(tmp_path):
    rounds = tmp_path / "research" / "quant" / "rounds"
    rounds.mkdir(parents=True)
    (rounds / "round452-plan.md").write_text("round", encoding="utf-8")
    assert quant_research_exec.resolve_round_number(None, cwd=tmp_path) == 453


def test_plan_marker_is_required_before_codex(tmp_path):
    _write_repo_files(tmp_path)
    codex_calls = []
    claude_calls = []
    code = quant_research_exec.main(
        ["--cwd", str(tmp_path)],
        codex_client_factory=_codex_factory(["unexpected"], codex_calls),
        claude_query_fn=_claude_query(["no marker"], claude_calls),
        codex_accounts=[],
        claude_accounts=[],
        log_path=tmp_path / "cycle.log",
    )
    assert code == 1
    assert codex_calls == []


def test_verify_markers_parse_last_and_question_guard():
    assert (
        quant_research_exec.parse_verify_result(
            "old\nVERIFY_RESULT: DEFECT bad\nVERIFY_RESULT: PASS"
        ).kind
        == "PASS"
    )
    assert quant_research_exec.parse_verify_result(
        "VERIFY_RESULT: DEFECT wrong split"
    ) == quant_research_exec.VerifyVerdict("DEFECT", "wrong split")
    assert quant_research_exec.parse_verify_result(
        "VERIFY_RESULT: QUESTION why?"
    ) == quant_research_exec.VerifyVerdict("QUESTION", "why?")
    with pytest.raises(quant_research_exec.CycleError, match="second"):
        quant_research_exec.parse_verify_result(
            "VERIFY_RESULT: QUESTION again?", allow_question=False
        )
    with pytest.raises(quant_research_exec.CycleError, match="did not contain"):
        quant_research_exec.parse_verify_result("plain prose")


def test_question_round_trip_resumes_both_sessions_and_logs_stages(
    tmp_path, monkeypatch
):
    _write_repo_files(tmp_path)
    codex_calls = []
    claude_calls = []
    log = tmp_path / "cycle.log"
    monkeypatch.setattr(_shared, "LOGS_ROOT", tmp_path / "logs")
    code = quant_research_exec.main(
        ["--cwd", str(tmp_path), "consider XAU"],
        codex_client_factory=_codex_factory(
            ["implemented", "answer", "finalized"], codex_calls
        ),
        claude_query_fn=_claude_query(
            [
                "plan\nPLAN_BRIEF:\nrun test",
                "VERIFY_RESULT: QUESTION what cutoff?",
                "VERIFY_RESULT: PASS",
            ],
            claude_calls,
        ),
        codex_accounts=[],
        claude_accounts=[],
        log_path=log,
    )
    assert code == 0
    assert [call["resume"] for call in codex_calls] == [None, "codex-0", "codex-1"]
    assert [call["options"].resume for call in claude_calls] == [None, "s1", "s1"]
    stages = [json.loads(line)["stage"] for line in log.read_text().splitlines()]
    assert set(stages) >= {"plan", "implement", "verify", "ask", "finalize"}
    assert all("stage" in json.loads(line) for line in log.read_text().splitlines())


def test_fix_loop_escalates_on_attempt_three_and_stops_after_five(tmp_path):
    _write_repo_files(tmp_path)
    codex_calls = []
    claude_calls = []
    claude_results = [
        "PLAN_BRIEF:\nrun test",
        "VERIFY_RESULT: DEFECT missing holdout",
        "VERIFY_RESULT: DEFECT still missing holdout",
        "VERIFY_RESULT: DEFECT still missing holdout",
        "VERIFY_RESULT: DEFECT still missing holdout",
        "VERIFY_RESULT: DEFECT still missing holdout",
        "VERIFY_RESULT: DEFECT still missing holdout",
    ]
    code = quant_research_exec.main(
        [
            "--cwd",
            str(tmp_path),
            "--codex-model",
            "codex-base",
            "--codex-effort",
            "low",
            "--codex-escalated-model",
            "codex-escalated",
            "--claude-model",
            "claude-base",
            "--claude-effort",
            "medium",
            "--claude-escalated-model",
            "claude-escalated",
        ],
        codex_client_factory=_codex_factory(
            ["implemented"] + ["fixed"] * 5, codex_calls
        ),
        claude_query_fn=_claude_query(claude_results, claude_calls),
        codex_accounts=[],
        claude_accounts=[],
        log_path=tmp_path / "cycle.log",
    )
    assert code == 1
    assert len(codex_calls) == 6
    assert len(claude_calls) == 7
    assert [call["effort"] for call in codex_calls] == [
        "low",
        "low",
        "low",
        "xhigh",
        "xhigh",
        "xhigh",
    ]
    assert [call["model"] for call in codex_calls] == [
        "codex-base",
        "codex-base",
        "codex-base",
        "codex-escalated",
        "codex-escalated",
        "codex-escalated",
    ]
    assert [call["options"].effort for call in claude_calls] == [
        "medium",
        "medium",
        "medium",
        "medium",
        "max",
        "max",
        "max",
    ]
    assert [call["options"].model for call in claude_calls] == [
        "claude-base",
        "claude-base",
        "claude-base",
        "claude-base",
        "claude-escalated",
        "claude-escalated",
        "claude-escalated",
    ]


def test_worktree_helpers_use_real_throwaway_git_repo(tmp_path):
    origin = tmp_path / "origin.git"
    seed = tmp_path / "seed"
    _run(["git", "init", "--bare", str(origin)], check=True, capture_output=True)
    _run(["git", "init", "-b", "main", str(seed)], check=True, capture_output=True)
    _run(
        ["git", "-C", str(seed), "config", "user.email", "test@example.com"], check=True
    )
    _run(["git", "-C", str(seed), "config", "user.name", "Test"], check=True)
    (seed / "research" / "quant" / "rounds").mkdir(parents=True)
    (seed / "research" / "quant" / "rounds" / "round2-old.md").write_text("old")
    _run(["git", "-C", str(seed), "add", "."], check=True)
    _run(
        ["git", "-C", str(seed), "commit", "-m", "initial"],
        check=True,
        capture_output=True,
    )
    _run(["git", "-C", str(seed), "remote", "add", "origin", str(origin)], check=True)
    _run(
        ["git", "-C", str(seed), "push", "-u", "origin", "main"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "--git-dir", str(origin), "symbolic-ref", "HEAD", "refs/heads/main"],
        check=True,
    )
    repo = tmp_path / "repo"
    _run(["git", "clone", str(origin), str(repo)], check=True, capture_output=True)

    peer = tmp_path / "peer"
    _run(["git", "clone", str(origin), str(peer)], check=True, capture_output=True)
    _run(
        ["git", "-C", str(peer), "config", "user.email", "test@example.com"], check=True
    )
    _run(["git", "-C", str(peer), "config", "user.name", "Test"], check=True)
    (peer / "research" / "quant" / "rounds" / "round3-remote.md").write_text("remote")
    _run(["git", "-C", str(peer), "add", "."], check=True)
    _run(
        ["git", "-C", str(peer), "commit", "-m", "remote"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(peer), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )

    assert quant_research_exec.sync_and_resolve_round(repo) == 4
    worktree = quant_research_exec.create_round_worktree(repo, 4)
    branch = "quant-research-round-4"
    assert worktree.is_dir()
    assert (
        _run(
            ["git", "-C", str(worktree), "branch", "--show-current"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        == branch
    )
    (worktree / "round-output.txt").write_text("result")
    _run(["git", "-C", str(worktree), "add", "round-output.txt"], check=True)
    _run(
        ["git", "-C", str(worktree), "commit", "-m", "round"],
        check=True,
        capture_output=True,
    )
    quant_research_exec.merge_and_cleanup_worktree(worktree, branch, repo)
    assert not worktree.exists()
    assert not _run(
        ["git", "-C", str(repo), "branch", "--list", branch],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    assert (repo / "round-output.txt").read_text() == "result"

    # Advance origin after the round branch is created: merge must rebase the
    # stale round branch before the fast-forward merge.
    _run(
        ["git", "-C", str(repo), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )
    worktree = quant_research_exec.create_round_worktree(repo, 5)
    branch = "quant-research-round-5"
    (worktree / "round-output-5.txt").write_text("result-5")
    _run(["git", "-C", str(worktree), "add", "round-output-5.txt"], check=True)
    _run(
        ["git", "-C", str(worktree), "commit", "-m", "round 5"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(peer), "pull", "--ff-only", "origin", "main"],
        check=True,
        capture_output=True,
    )
    (peer / "remote-2.txt").write_text("remote-2")
    _run(["git", "-C", str(peer), "add", "remote-2.txt"], check=True)
    _run(
        ["git", "-C", str(peer), "commit", "-m", "remote 2"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(peer), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )
    quant_research_exec.merge_and_cleanup_worktree(worktree, branch, repo)
    assert not worktree.exists()
    assert (repo / "round-output-5.txt").read_text() == "result-5"
    assert (repo / "remote-2.txt").read_text() == "remote-2"

    # A rebase conflict is a hard failure: neither the worktree nor branch is
    # deleted, leaving the round available for inspection.
    _run(
        ["git", "-C", str(repo), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )
    (repo / "conflict.txt").write_text("base")
    _run(["git", "-C", str(repo), "add", "conflict.txt"], check=True)
    _run(
        ["git", "-C", str(repo), "commit", "-m", "conflict base"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(repo), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )
    worktree = quant_research_exec.create_round_worktree(repo, 6)
    branch = "quant-research-round-6"
    (worktree / "conflict.txt").write_text("round")
    _run(["git", "-C", str(worktree), "add", "conflict.txt"], check=True)
    _run(
        ["git", "-C", str(worktree), "commit", "-m", "round 6"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(peer), "pull", "--ff-only", "origin", "main"],
        check=True,
        capture_output=True,
    )
    (peer / "conflict.txt").write_text("remote")
    _run(["git", "-C", str(peer), "add", "conflict.txt"], check=True)
    _run(
        ["git", "-C", str(peer), "commit", "-m", "remote conflict"],
        check=True,
        capture_output=True,
    )
    _run(
        ["git", "-C", str(peer), "push", "origin", "main"],
        check=True,
        capture_output=True,
    )
    with pytest.raises(subprocess.CalledProcessError):
        quant_research_exec.merge_and_cleanup_worktree(worktree, branch, repo)
    assert worktree.exists()
    assert _run(
        ["git", "-C", str(repo), "branch", "--list", branch],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def test_automatic_worktree_cycle_orders_sync_plan_setup_and_merge(
    tmp_path, monkeypatch
):
    _write_repo_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    order = []

    def sync(cwd):
        order.append("sync")
        assert cwd == tmp_path
        return 9

    def create(cwd, round_number):
        order.append("setup_worktree")
        assert cwd == tmp_path
        assert round_number == 9
        return tmp_path

    def merge(worktree, branch, cwd):
        order.append("merge")
        assert worktree == tmp_path
        assert branch == "quant-research-round-9"
        assert cwd == tmp_path

    monkeypatch.setattr(quant_research_exec, "sync_and_resolve_round", sync)
    monkeypatch.setattr(quant_research_exec, "create_round_worktree", create)
    monkeypatch.setattr(quant_research_exec, "merge_and_cleanup_worktree", merge)
    claude_calls = []
    codex_calls = []

    def query_fn(*, prompt, options):
        index = len(claude_calls)
        claude_calls.append(options)
        order.append("plan" if index == 0 else "verify")

        async def stream():
            yield claude_result(
                is_error=False,
                result="PLAN_BRIEF:\nbrief" if index == 0 else "VERIFY_RESULT: PASS",
            )

        return stream()

    def factory(*, config=None):
        index = len(codex_calls)
        codex_calls.append(index)
        order.append("implement" if index == 0 else "finalize")
        thread = FakeThread(
            FakeTurnHandle([wrapped_item_event("ok"), completed_event()]),
            thread_id=f"thread-{index}",
        )
        return FakeCodexClient(thread, config=config)

    assert (
        quant_research_exec.main(
            [],
            codex_client_factory=factory,
            claude_query_fn=query_fn,
            codex_accounts=[],
            claude_accounts=[],
            log_path=tmp_path / "cycle.log",
        )
        == 0
    )
    assert order[:4] == ["sync", "plan", "setup_worktree", "implement"]
    assert order[-2:] == ["finalize", "merge"]


def test_automatic_worktree_exhaustion_does_not_merge(tmp_path, monkeypatch):
    _write_repo_files(tmp_path)
    monkeypatch.chdir(tmp_path)
    order = []
    monkeypatch.setattr(
        quant_research_exec,
        "sync_and_resolve_round",
        lambda _cwd: order.append("sync") or 3,
    )
    monkeypatch.setattr(
        quant_research_exec,
        "create_round_worktree",
        lambda *_: order.append("setup") or tmp_path,
    )
    monkeypatch.setattr(
        quant_research_exec,
        "merge_and_cleanup_worktree",
        lambda *_: order.append("merge"),
    )
    claude_results = ["PLAN_BRIEF:\nbrief", "VERIFY_RESULT: DEFECT bad"] * 6
    codex_calls = []
    assert (
        quant_research_exec.main(
            [],
            codex_client_factory=_codex_factory(["ok"] * 6, codex_calls),
            claude_query_fn=_claude_query(claude_results, []),
            codex_accounts=[],
            claude_accounts=[],
            log_path=tmp_path / "cycle.log",
        )
        == 1
    )
    assert "merge" not in order


def test_explicit_cwd_skips_worktree_helpers(tmp_path, monkeypatch):
    _write_repo_files(tmp_path)
    monkeypatch.setattr(
        quant_research_exec,
        "sync_and_resolve_round",
        lambda _cwd: pytest.fail("sync called"),
    )
    monkeypatch.setattr(
        quant_research_exec,
        "create_round_worktree",
        lambda *_: pytest.fail("create called"),
    )
    monkeypatch.setattr(
        quant_research_exec,
        "merge_and_cleanup_worktree",
        lambda *_: pytest.fail("merge called"),
    )
    code = quant_research_exec.main(
        ["--cwd", str(tmp_path)],
        codex_client_factory=_codex_factory(["implemented", "finalized"], []),
        claude_query_fn=_claude_query(
            ["PLAN_BRIEF:\nbrief", "VERIFY_RESULT: PASS"], []
        ),
        codex_accounts=[],
        claude_accounts=[],
        log_path=tmp_path / "cycle.log",
    )
    assert code == 0
