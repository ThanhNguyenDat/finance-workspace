"""Small, dependency-free helpers shared by the orchestration CLIs."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, NoReturn


class CLIError(Exception):
    """An expected CLI error whose message belongs on stderr."""


def die(prefix: str, message: str) -> NoReturn:
    raise CLIError(f"{prefix}: {message}")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_after(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def json_text(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def read_json(path: Path, prefix: str, message: str | None = None) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        die(prefix, message or f"could not read JSON: {path}")
    raise AssertionError("unreachable")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.tmp.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json_text(value) + "\n")


def run_cli(main: Callable[[], int], prefix: str) -> NoReturn:
    import sys

    try:
        status = main()
    except CLIError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None
    raise SystemExit(status)
