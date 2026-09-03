"""Stream structured progress from the latest phase-agent JSONL log."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[4]


def compact(value: Any, limit: int = 220) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text[:limit]


def provider_tag(event: dict[str, Any]) -> str:
    if event.get("type") in {"item.completed", "item.started", "turn.completed", "error"}:
        return "Codex"
    if event.get("type") in {"assistant", "tool_result", "result", "system", "user"}:
        return "Claude"
    return "agent"


def render(event: dict[str, Any]) -> str | None:
    event_type = event.get("type")
    if event_type == "item.completed":
        item = event.get("item") or {}
        value = item.get("command") or item.get("path") or item.get("text") or item.get("aggregated_output") or ""
        return f"{item.get('type', 'event')}: {compact(value)}"
    if event_type == "error":
        return f"error: {compact(event.get('message') or event.get('error') or event)}"
    message = event.get("message")
    contents = message.get("content", []) if isinstance(message, dict) else []
    if event_type == "assistant":
        lines: list[str] = []
        for content in contents:
            if not isinstance(content, dict):
                continue
            if content.get("type") == "text":
                lines.append(f"message: {content.get('text', '')}")
            elif content.get("type") == "tool_use":
                lines.append(f"tool_use: {content.get('name', '')} {compact(content.get('input') or {}, 150)}")
        return compact(" | ".join(lines)) if lines else None
    if event_type == "tool_result" or any(
        isinstance(content, dict) and content.get("type") == "tool_result" for content in contents
    ):
        text = " ".join(
            str(part.get("text", ""))
            for content in contents
            if isinstance(content, dict) and content.get("type") == "tool_result"
            for part in content.get("content", [])
            if isinstance(part, dict)
        )
        return f"tool_result: {compact(text)}"
    if event_type == "result":
        return f"result: {compact(event.get('result') or event.get('subtype') or '')}"
    return None


def latest_log(log_dir: Path) -> Path | None:
    logs = list(log_dir.glob("*.stdout.jsonl")) if log_dir.is_dir() else []
    return max(logs, key=lambda path: path.stat().st_mtime_ns) if logs else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="watch-phase-attempt-log.sh")
    parser.add_argument("change")
    args = parser.parse_args(argv)
    log_dir = ROOT_DIR / ".ops/changes" / args.change / "runtime/logs"
    waited = 0
    path = latest_log(log_dir)
    while path is None:
        time.sleep(5)
        waited += 5
        if waited >= 3600:
            print(f"watch-phase-attempt-log: no attempt log found after {waited}s under {log_dir}", file=sys.stderr)
            return 1
        path = latest_log(log_dir)

    attempt_id = path.name.removesuffix(".stdout.jsonl")
    attempt_tag = attempt_id.removeprefix("agent-") or attempt_id
    print(f"[watch] watching {args.change} ({attempt_id})", flush=True)
    with path.open(encoding="utf-8") as handle:
        handle.seek(0, 2)
        while True:
            line = handle.readline()
            if not line:
                time.sleep(0.2)
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                message = render(event)
                if message:
                    print(f"[{provider_tag(event)}][{attempt_tag}] {message}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
