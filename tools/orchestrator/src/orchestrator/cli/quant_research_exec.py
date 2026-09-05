"""Run one complete, bounded quant-research round cycle."""

from __future__ import annotations

import argparse
import functools
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from claude_agent_sdk import query as default_query
from openai_codex import AsyncCodex

from ..providers.claude import ClaudeProvider, QueryFn
from ..providers.codex import CodexClientFactory, CodexProvider
from ._shared import (
    emit_error,
    emit_event,
    emit_result,
    resolve_log_path,
    run_cli_main,
)

PROG = "quant-research-exec"
DEFAULT_TIMEOUT_SECONDS = 3600.0
MAX_FIX_ATTEMPTS = 5
CODEX_HIGHEST_EFFORT = "xhigh"
CLAUDE_HIGHEST_EFFORT = "max"
_ROUND_FILE_RE = re.compile(r"^round(\d+)-.*\.md$")
_VERIFY_RESULT_RE = re.compile(
    r"(?m)^VERIFY_RESULT:[ \t]+(PASS|DEFECT|QUESTION)\b(?:[ \t]+([^\r\n]*))?[ \t]*$"
)


class CycleError(RuntimeError):
    """A bounded cycle failure that should be reported with its stage."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True, slots=True)
class VerifyVerdict:
    kind: str
    detail: str | None = None


def read_domain_rules(cwd: Path) -> str:
    """Read the raw quant domain rules content."""

    path = cwd / ".agents" / "domain" / "quant-research-domain.md"
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"quant research domain rules not found: {path}"
        ) from exc

    try:
        path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    except OSError:
        pass
    return content


def highest_round_number(cwd: Path) -> int:
    """Return the highest round number found under the round-file directory."""

    rounds_dir = cwd / "research" / "quant" / "rounds"
    if not rounds_dir.is_dir():
        return 0

    highest = 0
    for path in rounds_dir.glob("round*-*.md"):
        if not path.is_file():
            continue
        match = _ROUND_FILE_RE.fullmatch(path.name)
        if match is not None:
            highest = max(highest, int(match.group(1)))
    return highest


def _positive_round(value: str) -> int:
    try:
        round_number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--round must be a positive integer") from exc
    if round_number <= 0:
        raise argparse.ArgumentTypeError("--round must be a positive integer")
    return round_number


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Run one complete bounded quant-research round cycle.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Optional guidance for Claude PLAN",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Read optional PLAN guidance from this file",
    )
    parser.add_argument(
        "--round",
        type=_positive_round,
        default=None,
        help="Round number (auto-detected when omitted)",
    )
    parser.add_argument(
        "--cwd",
        type=str,
        default=None,
        help="Working directory; disables automatic worktree management",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Bound on each stage in seconds (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    for provider in ("codex", "claude"):
        parser.add_argument(
            f"--{provider}-model",
            type=str,
            default=None,
            help=f"Override the {provider} model",
        )
        parser.add_argument(
            f"--{provider}-effort",
            type=str,
            default=None,
            help=f"Override the {provider} reasoning effort",
        )
        parser.add_argument(
            f"--{provider}-escalated-model",
            type=str,
            default=None,
            help=f"Model for {provider} fix/re-verify attempts from attempt 3",
        )
    return parser


def resolve_guidance(
    args: argparse.Namespace, *, parser: argparse.ArgumentParser
) -> str | None:
    if args.prompt is not None and args.prompt_file is not None:
        parser.error("pass either a prompt argument or --prompt-file, not both")
    if args.prompt is not None:
        return args.prompt
    if args.prompt_file is not None:
        return args.prompt_file.read_text(encoding="utf-8")
    return None


def resolve_round_number(round_number: int | None, *, cwd: Path) -> int:
    return round_number if round_number is not None else highest_round_number(cwd) + 1


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )


def _default_branch(cwd: Path) -> str:
    try:
        ref = _git(
            cwd, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"
        ).stdout.strip()
        if ref.startswith("origin/"):
            return ref.removeprefix("origin/")
    except subprocess.CalledProcessError:
        pass
    branch = _git(cwd, "branch", "--show-current").stdout.strip()
    if not branch:
        raise RuntimeError("cannot determine the repository default branch")
    return branch


def sync_and_resolve_round(cwd: Path) -> int:
    """Sync the default branch to origin and resolve the next round number."""

    _git(cwd, "fetch", "origin")
    default_branch = _default_branch(cwd)
    _git(cwd, "merge", "--ff-only", f"origin/{default_branch}")
    return highest_round_number(cwd) + 1


def create_round_worktree(cwd: Path, round_number: int) -> Path:
    """Create the isolated worktree used after PLAN."""

    default_branch = _default_branch(cwd)
    branch = f"quant-research-round-{round_number}"
    worktree_path = cwd / ".agents" / "worktrees" / branch
    _git(
        cwd,
        "worktree",
        "add",
        str(worktree_path),
        "-b",
        branch,
        default_branch,
    )
    return worktree_path


def merge_and_cleanup_worktree(worktree_path: Path, branch: str, cwd: Path) -> None:
    """Merge a successful round branch and remove its worktree."""

    _git(cwd, "fetch", "origin")
    default_branch = _default_branch(cwd)
    _git(cwd, "merge", "--ff-only", f"origin/{default_branch}")
    try:
        _git(cwd, "merge", "--ff-only", branch)
    except subprocess.CalledProcessError:
        _git(worktree_path, "rebase", default_branch)
        _git(cwd, "merge", "--ff-only", branch)
    _git(cwd, "worktree", "remove", str(worktree_path))
    _git(cwd, "branch", "-d", branch)


def _round_sort_key(path: Path) -> int:
    match = _ROUND_FILE_RE.fullmatch(path.name)
    return int(match.group(1)) if match is not None else -1


def _backlog_paths(cwd: Path) -> list[Path]:
    paths = [
        cwd / "research" / "quant" / "index.md",
        cwd / "research" / "quant" / "reports" / "optimize_loop_update_v2.csv",
    ]
    rounds = sorted(
        (cwd / "research" / "quant" / "rounds").glob("round*-*.md"),
        key=_round_sort_key,
    )
    return paths + rounds[-5:]


def _backlog_description(cwd: Path) -> str:
    lines = [
        "Read these current backlog/evidence files before choosing the hypothesis:"
    ]
    for path in _backlog_paths(cwd):
        lines.append(f"- {path.relative_to(cwd)}")
    return "\n".join(lines)


def _plan_prompt(
    domain: str, cwd: Path, round_number: int, guidance: str | None
) -> str:
    optional = (
        guidance or "(No operator guidance was supplied; choose from the backlog.)"
    )
    return f"""{domain}

## PLAN for quant-research round {round_number}

You are Claude, the independent PLAN actor. {_backlog_description(cwd)}
Use the available read/search tools as needed. Prefer XAU before BTC, choose one
open hypothesis, and design a defensible train/validation/holdout or walk-forward
test that Codex can execute. Do not modify repository files in PLAN.

Optional operator guidance:
{optional}

End your response with a line containing exactly `PLAN_BRIEF:` and put the
complete implementation brief on the following lines. The brief is passed
verbatim to Codex IMPLEMENT.
"""


def _implement_prompt(domain: str, brief: str, round_number: int) -> str:
    return f"""{domain}

## IMPLEMENT quant-research round {round_number}

Execute the PLAN brief below with real repository tooling and the domain
invariants above. Draft the round markdown, CSV row(s), and index updates; do
not commit. Report the exact evidence paths and classification.

## PLAN_BRIEF

{brief}
"""


def _verify_prompt(domain: str, cwd: Path, round_number: int, produced_by: str) -> str:
    return f"""{domain}

## VERIFY quant-research round {round_number}

Independently inspect the evidence Codex {produced_by}. Read the round file(s),
`research/quant/reports/optimize_loop_update_v2.csv`, `research/quant/index.md`,
and the JSONL log under `tools/orchestrator/logs/quant-research-round-{round_number}/`.
Use the actual files under {cwd}. Judge only whether evidence and the stated
classification are trustworthy: no fabrication/cherry-picking, disjoint
holdout or defensible walk-forward, and classification matching the numbers.
An honestly measured negative outcome such as REJECTED is PASS; do not return
DEFECT merely because the hypothesis failed.

End with exactly one marker line:
VERIFY_RESULT: PASS
VERIFY_RESULT: DEFECT <one-line execution/evidence issue>
VERIFY_RESULT: QUESTION <one clarifying question>
"""


def _parse_plan_brief(text: str | None) -> str:
    if not text:
        raise CycleError("plan", "PLAN result did not contain a PLAN_BRIEF marker")
    matches = list(re.finditer(r"(?m)^PLAN_BRIEF:[ \t]*(.*)$", text))
    if not matches:
        raise CycleError("plan", "PLAN result did not contain a PLAN_BRIEF marker")
    marker = matches[-1]
    brief = marker.group(1).strip()
    if not brief:
        brief = text[marker.end() :].strip()
    if not brief:
        raise CycleError("plan", "PLAN_BRIEF marker was empty")
    return brief


def parse_verify_result(
    text: str | None, *, allow_question: bool = True
) -> VerifyVerdict:
    if not text:
        raise CycleError(
            "verify", "VERIFY result did not contain a VERIFY_RESULT marker"
        )
    matches = list(_VERIFY_RESULT_RE.finditer(text))
    if not matches:
        raise CycleError(
            "verify", "VERIFY result did not contain a VERIFY_RESULT marker"
        )
    match = matches[-1]
    kind = match.group(1)
    detail = (match.group(2) or "").strip() or None
    if kind in {"DEFECT", "QUESTION"} and detail is None:
        raise CycleError("verify", f"VERIFY_RESULT {kind} must include text")
    if kind == "QUESTION" and not allow_question:
        raise CycleError("verify", "a second VERIFY_RESULT QUESTION is not allowed")
    return VerifyVerdict(kind, detail)


async def _provider_turn(
    provider,
    prompt: str,
    *,
    stage: str,
    cwd: Path,
    timeout_seconds: float,
    log_path: Path,
    resume_id: str | None = None,
):
    on_event = functools.partial(emit_event, log_path=log_path, stage=stage)
    result = await provider.run_turn(
        prompt,
        cwd=str(cwd),
        timeout_seconds=timeout_seconds,
        on_event=on_event,
        resume_id=resume_id,
    )
    if not result.success:
        raise CycleError(stage, result.error or f"{stage} turn failed")
    emit_result(result.text, log_path=log_path, stage=stage)
    return result, provider.last_session_id


def _make_codex(
    *,
    factory: CodexClientFactory,
    accounts: list[str | None] | None,
    model: str | None,
    effort: str | None,
) -> CodexProvider:
    return CodexProvider(
        codex_client_factory=factory, accounts=accounts, model=model, effort=effort
    )


def _make_claude(
    *,
    query_fn: QueryFn,
    accounts: list[str | None] | None,
    model: str | None,
    effort: str | None,
) -> ClaudeProvider:
    return ClaudeProvider(
        query_fn=query_fn, accounts=accounts, model=model, effort=effort
    )


async def _verify_pass(
    *,
    domain: str,
    cwd: Path,
    round_number: int,
    timeout_seconds: float,
    log_path: Path,
    claude_query_fn: QueryFn,
    claude_accounts: list[str | None] | None,
    claude_model: str | None,
    claude_effort: str | None,
    claude_session_id: str | None,
    codex_client_factory: CodexClientFactory,
    codex_accounts: list[str | None] | None,
    codex_model: str | None,
    codex_effort: str | None,
    codex_session_id: str | None,
    produced_by: str,
) -> tuple[VerifyVerdict, str | None, str | None]:
    verify_provider = _make_claude(
        query_fn=claude_query_fn,
        accounts=claude_accounts,
        model=claude_model,
        effort=claude_effort,
    )
    result, claude_session_id = await _provider_turn(
        verify_provider,
        _verify_prompt(domain, cwd, round_number, produced_by),
        stage="verify",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
        resume_id=claude_session_id,
    )
    verdict = parse_verify_result(result.text)
    if verdict.kind != "QUESTION":
        return verdict, claude_session_id, codex_session_id

    ask_provider = _make_codex(
        factory=codex_client_factory,
        accounts=codex_accounts,
        model=codex_model,
        effort=codex_effort,
    )
    answer_result, codex_session_id = await _provider_turn(
        ask_provider,
        f"Answer this one Claude VERIFY question about the round you just implemented:\n\n{verdict.detail}",
        stage="ask",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
        resume_id=codex_session_id,
    )
    continuation = _make_claude(
        query_fn=claude_query_fn,
        accounts=claude_accounts,
        model=claude_model,
        effort=claude_effort,
    )
    continuation_result, claude_session_id = await _provider_turn(
        continuation,
        f"Codex answered your question:\n\n{answer_result.text or '(no answer text)'}\n\nRe-check the evidence now. No further question is accepted in this pass; end with exactly VERIFY_RESULT: PASS or VERIFY_RESULT: DEFECT <issue>.",
        stage="verify",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
        resume_id=claude_session_id,
    )
    return (
        parse_verify_result(continuation_result.text, allow_question=False),
        claude_session_id,
        codex_session_id,
    )


async def run_cycle(
    *,
    cwd: Path,
    round_number: int,
    guidance: str | None,
    managed_worktree: bool,
    timeout_seconds: float,
    codex_client_factory: CodexClientFactory,
    claude_query_fn: QueryFn,
    codex_accounts: list[str | None] | None,
    claude_accounts: list[str | None] | None,
    codex_model: str | None,
    codex_effort: str | None,
    codex_escalated_model: str | None,
    claude_model: str | None,
    claude_effort: str | None,
    claude_escalated_model: str | None,
    log_path: Path,
) -> None:
    domain = read_domain_rules(cwd)
    plan_provider = _make_claude(
        query_fn=claude_query_fn,
        accounts=claude_accounts,
        model=claude_model,
        effort=claude_effort,
    )
    plan_result, claude_session_id = await _provider_turn(
        plan_provider,
        _plan_prompt(domain, cwd, round_number, guidance),
        stage="plan",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
    )
    brief = _parse_plan_brief(plan_result.text)

    worktree_path = cwd
    branch: str | None = None
    if managed_worktree:
        worktree_path = create_round_worktree(cwd, round_number)
        branch = f"quant-research-round-{round_number}"
        emit_event(
            {"worktree": str(worktree_path), "branch": branch},
            log_path=log_path,
            stage="setup_worktree",
        )

    implement_provider = _make_codex(
        factory=codex_client_factory,
        accounts=codex_accounts,
        model=codex_model,
        effort=codex_effort,
    )
    _, codex_session_id = await _provider_turn(
        implement_provider,
        _implement_prompt(domain, brief, round_number),
        stage="implement",
        cwd=worktree_path,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
    )

    verdict, claude_session_id, codex_session_id = await _verify_pass(
        domain=domain,
        cwd=worktree_path,
        round_number=round_number,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
        claude_query_fn=claude_query_fn,
        claude_accounts=claude_accounts,
        claude_model=claude_model,
        claude_effort=claude_effort,
        claude_session_id=claude_session_id,
        codex_client_factory=codex_client_factory,
        codex_accounts=codex_accounts,
        codex_model=codex_model,
        codex_effort=codex_effort,
        codex_session_id=codex_session_id,
        produced_by="implemented/fixed the round",
    )

    attempt = 0
    while verdict.kind == "DEFECT":
        if attempt >= MAX_FIX_ATTEMPTS:
            raise CycleError(
                "verify",
                f"VERIFY still reports DEFECT after {MAX_FIX_ATTEMPTS} fix attempts",
            )
        attempt += 1
        escalated = attempt >= 3
        fix_provider = _make_codex(
            factory=codex_client_factory,
            accounts=codex_accounts,
            model=codex_escalated_model
            if escalated and codex_escalated_model
            else codex_model,
            effort=CODEX_HIGHEST_EFFORT if escalated else codex_effort,
        )
        _, codex_session_id = await _provider_turn(
            fix_provider,
            f"Fix this VERIFY defect in quant-research round {round_number}. Do not commit.\n\n{verdict.detail}",
            stage="fix",
            cwd=worktree_path,
            timeout_seconds=timeout_seconds,
            log_path=log_path,
            resume_id=codex_session_id,
        )
        verdict, claude_session_id, codex_session_id = await _verify_pass(
            domain=domain,
            cwd=worktree_path,
            round_number=round_number,
            timeout_seconds=timeout_seconds,
            log_path=log_path,
            claude_query_fn=claude_query_fn,
            claude_accounts=claude_accounts,
            claude_model=claude_escalated_model
            if escalated and claude_escalated_model
            else claude_model,
            claude_effort=CLAUDE_HIGHEST_EFFORT if escalated else claude_effort,
            claude_session_id=claude_session_id,
            codex_client_factory=codex_client_factory,
            codex_accounts=codex_accounts,
            codex_model=codex_model,
            codex_effort=codex_effort,
            codex_session_id=codex_session_id,
            produced_by=f"fixed the round (attempt {attempt})",
        )

    finalize_provider = _make_codex(
        factory=codex_client_factory,
        accounts=codex_accounts,
        model=codex_model,
        effort=codex_effort,
    )
    await _provider_turn(
        finalize_provider,
        f"Finalize quant-research round {round_number}: verify the draft evidence is saved, commit the round markdown/CSV/index changes on this branch, and report the commit. Do not alter unrelated files.",
        stage="finalize",
        cwd=worktree_path,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
        resume_id=codex_session_id,
    )
    if managed_worktree and branch is not None:
        emit_event(
            {"worktree": str(worktree_path), "branch": branch, "status": "merging"},
            log_path=log_path,
            stage="merge",
        )
        merge_and_cleanup_worktree(worktree_path, branch, cwd)
        emit_event(
            {"worktree": str(worktree_path), "branch": branch, "status": "complete"},
            log_path=log_path,
            stage="merge",
        )


def main(
    argv: list[str] | None = None,
    *,
    codex_client_factory: CodexClientFactory = AsyncCodex,
    claude_query_fn: QueryFn = default_query,
    codex_accounts: list[str | None] | None = None,
    claude_accounts: list[str | None] | None = None,
    log_path: Path | None = None,
) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    guidance = resolve_guidance(args, parser=parser)
    cwd = Path(args.cwd) if args.cwd is not None else Path.cwd()
    managed_worktree = args.cwd is None
    active_log_path = log_path

    async def _main() -> int:
        nonlocal active_log_path
        try:
            if managed_worktree:
                synced_round = sync_and_resolve_round(cwd)
                round_number = args.round or synced_round
            else:
                round_number = resolve_round_number(args.round, cwd=cwd)
            if active_log_path is None:
                change = f"quant-research-round-{round_number}"
                active_log_path = resolve_log_path(PROG, change)
            if managed_worktree:
                emit_event(
                    {"round": round_number},
                    log_path=active_log_path,
                    stage="sync",
                )
            await run_cycle(
                cwd=cwd,
                round_number=round_number,
                guidance=guidance,
                managed_worktree=managed_worktree,
                timeout_seconds=args.timeout_seconds,
                codex_client_factory=codex_client_factory,
                claude_query_fn=claude_query_fn,
                codex_accounts=codex_accounts,
                claude_accounts=claude_accounts,
                codex_model=args.codex_model,
                codex_effort=args.codex_effort,
                codex_escalated_model=args.codex_escalated_model,
                claude_model=args.claude_model,
                claude_effort=args.claude_effort,
                claude_escalated_model=args.claude_escalated_model,
                log_path=active_log_path,
            )
            return 0
        except CycleError as exc:
            emit_error(str(exc), log_path=active_log_path, stage=exc.stage)
            return 1
        except Exception as exc:  # noqa: BLE001 - CLI boundary
            emit_error(
                f"{type(exc).__name__}: {exc}",
                log_path=active_log_path,
                stage="setup" if managed_worktree else "plan",
            )
            return 1

    return run_cli_main(_main, log_path=active_log_path)


def cli() -> NoReturn:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
