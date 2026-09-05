"""CLI entry point: run exactly one bounded Codex SDK turn."""

from __future__ import annotations

import functools
import sys
from pathlib import Path
from typing import NoReturn

from openai_codex import AsyncCodex

from ..providers.codex import CodexClientFactory, CodexProvider
from ._shared import (
    build_arg_parser,
    emit_error,
    emit_event,
    emit_result,
    resolve_prompt,
    run_cli_main,
)

PROG = "codex-exec"

DEFAULT_LOG_PATH = Path(__file__).resolve().parents[3] / "logs" / "codex-exec.log"


async def run_turn(
    prompt: str,
    *,
    cwd: str | None,
    timeout_seconds: float,
    codex_client_factory: CodexClientFactory = AsyncCodex,
    accounts: list[str | None] | None = None,
    model: str | None = None,
    effort: str | None = None,
    log_path: Path | None = None,
) -> int:
    """`log_path=None` means "use DEFAULT_LOG_PATH", read fresh here (not
    bound as this parameter's own default) so tests can monkeypatch the
    module-level `DEFAULT_LOG_PATH` and have it take effect."""

    resolved_log_path = log_path if log_path is not None else DEFAULT_LOG_PATH
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
    parser = build_arg_parser(PROG, "Run exactly one bounded Codex SDK turn.")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    prompt = resolve_prompt(args, parser=parser)
    resolved_log_path = log_path if log_path is not None else DEFAULT_LOG_PATH

    async def _main() -> int:
        return await run_turn(
            prompt,
            cwd=args.cwd,
            timeout_seconds=args.timeout_seconds,
            codex_client_factory=codex_client_factory,
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
