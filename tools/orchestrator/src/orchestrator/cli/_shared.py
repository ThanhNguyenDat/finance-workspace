"""Argument parsing and output plumbing shared by codex-exec and claude-exec.

Business logic (SDK invocation) stays out of this module - it only covers the
parts identical across both entry points: prompt resolution, event printing,
and mapping exceptions to a process exit code.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from ..utils.jsonable import jsonable
from ..utils.redaction import redact_text, redact_value
from ..utils.timeout import DEFAULT_TIMEOUT_SECONDS, ProviderTimeoutError

LOGS_ROOT = Path(__file__).resolve().parents[3] / "logs"
_CHANGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_ADHOC_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
ROLES = ("plan", "implement", "verify", "fix", "final_verify")


def _validate_change_name(value: str) -> str:
    if not _CHANGE_NAME_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(
            f"--change must be kebab-case (lowercase letters, digits, hyphens): {value!r}"
        )
    return value


def resolve_log_path(command: str, change: str | None) -> Path:
    """Resolve the log file for one invocation: `logs/<change>/<command>.log`.

    When `change` is omitted, falls back to `logs/adhoc-<YYYY-MM-DD>/<command>.log`
    using the Asia/Ho_Chi_Minh calendar date (the per-line `timestamp` field
    written into each log entry stays UTC regardless).
    """

    name = change if change else f"adhoc-{datetime.now(_ADHOC_TZ).date().isoformat()}"
    return LOGS_ROOT / name / f"{command}.log"


def build_arg_parser(prog: str, description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Prompt text (omit when using --prompt-file)",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Read the prompt from this file instead of the positional argument",
    )
    parser.add_argument(
        "--cwd", type=str, default=None, help="Working directory for the provider turn"
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
    parser.add_argument(
        "--change",
        type=_validate_change_name,
        default=None,
        help=(
            "OpenSpec change name to scope this invocation's log file under "
            "(logs/<change>/<command>.log); defaults to logs/adhoc-<YYYY-MM-DD>/"
            "<command>.log (Asia/Ho_Chi_Minh date) when omitted. Not checked "
            "against openspec/changes/ on disk."
        ),
    )
    parser.add_argument(
        "--role",
        choices=ROLES,
        default=None,
        help=(
            "Declare which lifecycle phase this invocation is for. If the "
            "provider's config.yaml `scope` list doesn't include it, prints "
            "an advisory warning -- never blocks or changes the exit code."
        ),
    )
    return parser


def resolve_prompt(args: argparse.Namespace, *, parser: argparse.ArgumentParser) -> str:
    if args.prompt is not None and args.prompt_file is not None:
        parser.error("pass either a prompt argument or --prompt-file, not both")
    if args.prompt is not None:
        return args.prompt
    if args.prompt_file is not None:
        return args.prompt_file.read_text(encoding="utf-8")
    parser.error("a prompt is required: pass it as an argument or via --prompt-file")
    raise AssertionError("unreachable")  # pragma: no cover


_file_loggers: dict[str, logging.Logger] = {}


def _file_logger(log_path: Path) -> logging.Logger:
    """Return a JSONL file logger for `log_path`, built once and cached.

    Caching by resolved path keeps this idempotent across the many
    `emit_event` calls in a single turn (each would otherwise attach a
    duplicate `FileHandler`, multiplying every line written).
    """

    key = str(log_path)
    logger = _file_loggers.get(key)
    if logger is not None:
        return logger

    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"orchestrator.exec_log.{key}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    _file_loggers[key] = logger
    return logger


def _log_line(log_path: Path, record: dict[str, Any]) -> None:
    line = {"timestamp": datetime.now(timezone.utc).isoformat(), **record}
    _file_logger(log_path).info(json.dumps(line, ensure_ascii=False))


def emit_event(payload: Any, *, log_path: Path | None = None) -> None:
    """Print one redacted JSON line for a streamed provider turn/tool event."""

    safe = redact_value(jsonable(payload))
    print(json.dumps(safe, ensure_ascii=False), file=sys.stdout, flush=True)
    if log_path is not None:
        _log_line(log_path, {"type": "event", "payload": safe})


def emit_result(text: str | None, *, log_path: Path | None = None) -> None:
    safe = redact_text(text) if text else ""
    print(safe, file=sys.stdout, flush=True)
    if log_path is not None:
        _log_line(log_path, {"type": "result", "text": safe})


def emit_error(message: str, *, log_path: Path | None = None) -> None:
    safe = redact_text(message)
    print(safe, file=sys.stderr, flush=True)
    if log_path is not None:
        _log_line(log_path, {"type": "error", "message": safe})


def emit_warning(message: str, *, log_path: Path | None = None) -> None:
    """Advisory-only: never affects the exit code. See `check_role_scope`."""

    safe = redact_text(message)
    print(f"warning: {safe}", file=sys.stderr, flush=True)
    if log_path is not None:
        _log_line(log_path, {"type": "warning", "message": safe})


def check_role_scope(role: str | None, scope: list[str]) -> str | None:
    """Return an advisory warning message, or `None` if there's no mismatch.

    No mismatch (returns `None`) when `role` is omitted, `scope` is empty,
    or `role` is already in `scope`.
    """

    if not role or not scope or role in scope:
        return None
    scope_text = ", ".join(scope)
    return f"{role} is outside the configured scope ({scope_text})"


def run_cli_main(
    main: Callable[[], Coroutine[Any, Any, int]], *, log_path: Path | None = None
) -> int:
    """Run `main`, mapping timeouts and unexpected errors to exit code 1."""

    import asyncio

    try:
        return asyncio.run(main())
    except ProviderTimeoutError as exc:
        emit_error(str(exc), log_path=log_path)
        return 1
    except KeyboardInterrupt:
        emit_error("interrupted", log_path=log_path)
        return 130
    except Exception as exc:  # noqa: BLE001 - top-level CLI error boundary
        emit_error(f"{type(exc).__name__}: {exc}", log_path=log_path)
        return 1
