"""CLI entry point: run exactly one bounded Claude Agent SDK turn."""

from __future__ import annotations

import functools
import sys
from pathlib import Path
from typing import NoReturn

from claude_agent_sdk import query as default_query

from ..providers.claude import ClaudeProvider, QueryFn
from ._shared import (
    build_arg_parser,
    emit_error,
    emit_event,
    emit_result,
    resolve_log_path,
    resolve_prompt,
    run_cli_main,
)

PROG = "claude-exec"


async def run_turn(
    prompt: str,
    *,
    cwd: str | None,
    timeout_seconds: float,
    query_fn: QueryFn = default_query,
    accounts: list[str | None] | None = None,
    model: str | None = None,
    effort: str | None = None,
    change: str | None = None,
    log_path: Path | None = None,
) -> int:
    """`log_path=None` means "resolve from `change`" (via `resolve_log_path`,
    read fresh here rather than bound as this parameter's own default) so
    tests can monkeypatch `_shared.LOGS_ROOT` and have it take effect."""

    resolved_log_path = (
        log_path if log_path is not None else resolve_log_path(PROG, change)
    )
    provider = ClaudeProvider(
        query_fn=query_fn, accounts=accounts, model=model, effort=effort
    )
    on_event = functools.partial(emit_event, log_path=resolved_log_path)
    result = await provider.run_turn(
        prompt, cwd=cwd, timeout_seconds=timeout_seconds, on_event=on_event
    )
    if not result.success:
        emit_error(result.error or "claude turn failed", log_path=resolved_log_path)
        return 1
    emit_result(result.text, log_path=resolved_log_path)
    return 0


def main(
    argv: list[str] | None = None,
    *,
    query_fn: QueryFn = default_query,
    accounts: list[str | None] | None = None,
    log_path: Path | None = None,
) -> int:
    parser = build_arg_parser(PROG, "Run exactly one bounded Claude Agent SDK turn.")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    prompt = resolve_prompt(args, parser=parser)
    resolved_log_path = (
        log_path if log_path is not None else resolve_log_path(PROG, args.change)
    )

    async def _main() -> int:
        return await run_turn(
            prompt,
            cwd=args.cwd,
            timeout_seconds=args.timeout_seconds,
            query_fn=query_fn,
            accounts=accounts,
            model=args.model,
            effort=args.effort,
            log_path=resolved_log_path,
        )

    return run_cli_main(_main, log_path=resolved_log_path)


def cli() -> NoReturn:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
