"""CLI entry point for one Codex stage of a quant-research round."""

from __future__ import annotations

import argparse
import functools
import re
import stat
import sys
from pathlib import Path
from typing import NoReturn

from openai_codex import AsyncCodex

from ..providers.codex import CodexClientFactory, CodexProvider
from ..utils.config import configured_scope
from ..utils.timeout import DEFAULT_TIMEOUT_SECONDS
from ._shared import (
    check_role_scope,
    emit_error,
    emit_event,
    emit_result,
    emit_warning,
    resolve_log_path,
    resolve_prompt,
    run_cli_main,
)

PROG = "quant-research-exec"
_ROUND_FILE_RE = re.compile(r"^round(\d+)-.*\.md$")
_ROLES = ("implement", "fix")


def read_domain_rules(cwd: Path) -> str:
    """Read the raw quant domain rules content.

    Deliberately outside `.agents/skills/`: that directory is scanned and
    synced as invocable agent skills, which risks an agent treating this
    reference content as something to revise. `.agents/domain/` holds plain
    reference material instead -- no frontmatter, no workflow references,
    just the domain rules text as-is."""

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
        pass  # best-effort: read-only protection, not the primary function

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
        description="Run exactly one bounded Codex quant-research stage.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Stage brief (omit when using --prompt-file)",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Read the stage brief from this file instead of the positional argument",
    )
    parser.add_argument(
        "--round",
        type=_positive_round,
        default=None,
        help="Round number (auto-detected for implement, required for fix)",
    )
    parser.add_argument(
        "--role",
        choices=_ROLES,
        required=True,
        help="Codex stage to run",
    )
    parser.add_argument(
        "--cwd",
        type=str,
        default=None,
        help="Working directory for the provider turn and round files",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Bound on turn duration in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the model for this turn (default: the SDK's own default)",
    )
    parser.add_argument(
        "--effort",
        type=str,
        default=None,
        help="Override the reasoning effort for this turn (default: the SDK's own default)",
    )
    return parser


def resolve_round_number(role: str, round_number: int | None, *, cwd: Path) -> int:
    if round_number is not None:
        return round_number
    if role == "fix":
        raise ValueError("--round is required when --role fix")
    return highest_round_number(cwd) + 1


def assemble_prompt(domain_body: str, brief: str) -> str:
    return f"{domain_body}\n\n## This round's brief\n\n{brief}"


async def run_turn(
    prompt: str,
    *,
    cwd: str | None,
    timeout_seconds: float,
    codex_client_factory: CodexClientFactory = AsyncCodex,
    accounts: list[str | None] | None = None,
    model: str | None = None,
    effort: str | None = None,
    change: str | None = None,
    role: str | None = None,
    log_path: Path | None = None,
) -> int:
    """Run one Codex turn with the quant-research command's log scope."""

    resolved_log_path = (
        log_path if log_path is not None else resolve_log_path(PROG, change)
    )
    warning = check_role_scope(role, configured_scope("codex"))
    if warning is not None:
        emit_warning(warning, log_path=resolved_log_path)
    provider = CodexProvider(
        codex_client_factory=codex_client_factory,
        accounts=accounts,
        model=model,
        effort=effort,
    )
    on_event = functools.partial(emit_event, log_path=resolved_log_path)
    result = await provider.run_turn(
        prompt, cwd=cwd, timeout_seconds=timeout_seconds, on_event=on_event
    )
    if not result.success:
        emit_error(result.error or "codex turn failed", log_path=resolved_log_path)
        return 1
    emit_result(result.text, log_path=resolved_log_path)
    return 0


def main(
    argv: list[str] | None = None,
    *,
    codex_client_factory: CodexClientFactory = AsyncCodex,
    accounts: list[str | None] | None = None,
    log_path: Path | None = None,
) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.role == "fix" and args.round is None:
        parser.error("--round is required when --role fix")
    prompt = resolve_prompt(args, parser=parser)
    cwd = Path(args.cwd) if args.cwd is not None else Path.cwd()
    round_number = resolve_round_number(args.role, args.round, cwd=cwd)
    change = f"quant-research-round-{round_number}"
    resolved_log_path = (
        log_path if log_path is not None else resolve_log_path(PROG, change)
    )

    async def _main() -> int:
        domain_body = read_domain_rules(cwd)
        return await run_turn(
            assemble_prompt(domain_body, prompt),
            cwd=args.cwd,
            timeout_seconds=args.timeout_seconds,
            codex_client_factory=codex_client_factory,
            accounts=accounts,
            model=args.model,
            effort=args.effort,
            change=change,
            role=args.role,
            log_path=resolved_log_path,
        )

    return run_cli_main(_main, log_path=resolved_log_path)


def cli() -> NoReturn:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
