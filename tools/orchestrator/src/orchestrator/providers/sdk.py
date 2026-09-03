"""Small adapters around the official Claude and Codex Python SDKs."""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import threading
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from ..core.io import die
from ..core.redaction import redact_value


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
        handle.write(json.dumps(redact_value(jsonable(value)), ensure_ascii=False, separators=(",", ":")) + "\n")


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def run_async(coro_factory: Callable[[], Any]) -> Any:
    """Run one Claude SDK coroutine without leaking an event loop."""

    import asyncio

    return asyncio.run(coro_factory())


def start_codex(config: Any, timeout_seconds: float) -> Any:
    """Create the public Codex facade with a bounded app-server handshake."""

    from openai_codex import Codex
    from openai_codex.client import CodexClient

    client = CodexClient(config)
    outcome: list[Any] = []

    def initialize() -> None:
        try:
            client.start()
            outcome.append(("result", client.initialize()))
        except BaseException as error:
            outcome.append(("error", error))

    worker = threading.Thread(target=initialize, name="phase-agent-codex-connect")
    worker.daemon = True
    worker.start()
    worker.join(timeout_seconds)
    if worker.is_alive():
        process = getattr(client, "_proc", None)
        if process is not None and process.poll() is None:
            process.kill()
        worker.join(2)
        client.close()
        raise TimeoutError("Codex SDK app-server handshake timed out")
    if not outcome:
        client.close()
        raise RuntimeError("Codex SDK app-server handshake returned no result")
    kind, value = outcome[0]
    if kind == "error":
        client.close()
        raise value
    facade = Codex.__new__(Codex)
    facade._client = client
    facade._init = value
    return facade
