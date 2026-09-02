"""Small adapters around the official Claude and Codex Python SDKs."""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .io import die


def executable(name: str, prefix: str) -> str:
    path = shutil.which(name)
    if path is None:
        die(prefix, f"missing-{name}")
    return path


def child_environment() -> dict[str, str]:
    """Return an isolated copy so SDK subprocesses inherit account routing."""

    return dict(os.environ)


def jsonable(value: Any) -> Any:
    """Convert SDK dataclasses/Pydantic models into safe JSON log values."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return jsonable(value.model_dump(mode="json", by_alias=True))
    if dataclasses.is_dataclass(value):
        return jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    return str(value)


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(jsonable(value), ensure_ascii=False, separators=(",", ":")) + "\n")


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def run_async(coro_factory: Callable[[], Any]) -> Any:
    """Run one Claude SDK coroutine without leaking an event loop."""

    import asyncio

    return asyncio.run(coro_factory())
