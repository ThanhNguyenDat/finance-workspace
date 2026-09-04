"""Export coordinator attempt transcripts as normalized, chat-shaped JSON.

Reads Claude/Codex SDK stream events already recorded by the coordinator
(`events.event_type == 'provider.stream'`) and reduces each attempt to a
short list of chat bubbles: assistant text, tool calls, tool results, and
reasoning summaries. Every other provider notification (turn/hook lifecycle
noise, token-usage updates, duplicate "started" markers) is dropped. This is
read-only tooling for a local transcript viewer; it never mutates coordinator
state.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, NoReturn

from ..coordinator.db import CoordinatorDB
from ..core.io import CLIError, run_cli

PREFIX = "export-transcript"

MAX_TEXT_CHARS = 800
MAX_MESSAGES_PER_ATTEMPT = 100


def _truncate(text: str) -> str:
    text = text.strip()
    if len(text) <= MAX_TEXT_CHARS:
        return text
    return text[:MAX_TEXT_CHARS] + f"… [+{len(text) - MAX_TEXT_CHARS} chars]"


def _codex_item_text(item: dict[str, Any]) -> str | None:
    for key in ("text", "summary", "content"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, list) and value:
            parts = [part for part in value if isinstance(part, str) and part.strip()]
            if parts:
                return "\n".join(parts)
    return None


def _normalize_codex(payload: dict[str, Any]) -> dict[str, str] | None:
    method = payload.get("method", "")
    if method != "item/completed":
        return None
    item = payload.get("payload", {}).get("item")
    if not isinstance(item, dict):
        return None
    item_type = item.get("type", "unknown")
    if item_type == "userMessage":
        return None  # the injected prompt, echoed back on every attempt
    if item_type == "commandExecution":
        command = item.get("command", "")
        exit_code = item.get("exitCode")
        status = "ok" if exit_code == 0 else f"exit {exit_code}"
        output = (item.get("aggregatedOutput") or "").strip()
        text = f"$ {command}\n[{status}]"
        if output:
            text += f"\n{output}"
        return {"kind": "tool_call", "text": text}
    if item_type == "fileChange":
        changes = item.get("changes")
        if isinstance(changes, list) and changes:
            lines = [
                f"{change.get('kind', 'changed')}: {change.get('path', '?')}"
                for change in changes
                if isinstance(change, dict)
            ]
            return {"kind": "tool_call", "text": "\n".join(lines)}
        return None
    text = _codex_item_text(item)
    if item_type == "agentMessage":
        return {"kind": "message", "text": text or ""} if text else None
    if item_type == "reasoning":
        return {"kind": "reasoning", "text": text} if text else None
    if text:
        return {"kind": "tool_call", "text": f"[{item_type}] {text}"}
    # Unknown/opaque item shape: still surface it rather than drop it.
    compact = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
    return {"kind": "tool_call", "text": f"[{item_type}] {compact}"}


def _claude_block_text(block: dict[str, Any]) -> tuple[str, str] | None:
    if isinstance(block.get("text"), str) and block["text"].strip():
        return "message", block["text"]
    if block.get("type") == "tool_use":
        name = block.get("name", "tool")
        tool_input = json.dumps(block.get("input", {}), ensure_ascii=False)
        return "tool_call", f"{name}({tool_input})"
    if block.get("type") == "tool_result" or "tool_use_result" in block:
        content = block.get("content") or block.get("tool_use_result")
        return "tool_result", json.dumps(content, ensure_ascii=False)
    if isinstance(block.get("thinking"), str) and block["thinking"].strip():
        return "reasoning", block["thinking"]
    return None


def _normalize_claude(payload: dict[str, Any]) -> dict[str, str] | None:
    content = payload.get("content")
    if isinstance(content, list):
        parts: list[tuple[str, str]] = []
        for block in content:
            if isinstance(block, dict):
                found = _claude_block_text(block)
                if found:
                    parts.append(found)
        if not parts:
            return None
        kind = parts[0][0]
        text = "\n".join(text for _kind, text in parts)
        return {"kind": kind, "text": text}
    if "tool_use_result" in payload:
        return {
            "kind": "tool_result",
            "text": json.dumps(payload["tool_use_result"], ensure_ascii=False),
        }
    if payload.get("subtype") == "task_output" or {
        "output_file",
        "summary",
    } <= set(payload.keys()):
        summary = payload.get("summary")
        if isinstance(summary, str) and summary.strip():
            return {"kind": "tool_result", "text": summary}
    return None


def _normalize_final_result(payload: dict[str, Any]) -> dict[str, str] | None:
    """The attempt's one-shot final answer (event_type='provider.result').

    Every attempt carries this event regardless of provider or whether the
    fine-grained 'provider.stream' events exist (older attempts, recorded
    before Codex streaming was wired up, have only this). Claude's SDK
    result names the field 'result'; Codex's TurnResult names it
    'final_response'.
    """

    text = payload.get("final_response") or payload.get("result")
    if isinstance(text, str) and text.strip():
        return {"kind": "message", "text": text}
    return None


def _normalize(
    provider: str, event_type: str, payload: dict[str, Any]
) -> dict[str, str] | None:
    if event_type == "provider.result":
        entry = _normalize_final_result(payload)
    else:
        entry = (
            _normalize_codex(payload)
            if provider == "codex"
            else _normalize_claude(payload)
        )
    if entry is None or not entry.get("text"):
        return None
    return {"kind": entry["kind"], "text": _truncate(entry["text"])}


def _export(db: CoordinatorDB, selector: str) -> list[dict[str, Any]]:
    sessions = db.read(
        "SELECT * FROM sessions WHERE id = ? OR change_name = ? ORDER BY created_at",
        (selector, selector),
    )
    if not sessions:
        raise CLIError(f"{PREFIX}: no session or change found: {selector}")
    attempts_out: list[dict[str, Any]] = []
    for session in sessions:
        attempts = db.read(
            "SELECT * FROM attempts WHERE session_id = ? ORDER BY attempt_no",
            (session["id"],),
        )
        for attempt in attempts:
            rows = db.read(
                "SELECT event_type, safe_payload FROM events"
                " WHERE attempt_id = ? AND event_type IN ('provider.stream', 'provider.result')"
                " ORDER BY sequence",
                (attempt["id"],),
            )
            messages: list[dict[str, str]] = []
            for row in rows:
                try:
                    payload = json.loads(row["safe_payload"])
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                entry = _normalize(attempt["provider"], row["event_type"], payload)
                if entry is not None:
                    messages.append(entry)
            if len(messages) > MAX_MESSAGES_PER_ATTEMPT:
                messages = messages[-MAX_MESSAGES_PER_ATTEMPT:]
            attempts_out.append(
                {
                    "session_id": session["id"],
                    "change": session["change_name"],
                    "round": session["quant_iteration"] or session["round"],
                    "phase": attempt["phase"],
                    "attempt_no": attempt["attempt_no"],
                    "provider": attempt["provider"],
                    "account": attempt["account"],
                    "status": attempt["status"],
                    "result_class": attempt["result_class"],
                    "started_at": attempt["started_at"],
                    "completed_at": attempt["completed_at"],
                    "messages": messages,
                }
            )
    return attempts_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=PREFIX)
    parser.add_argument(
        "selector", help="a coordinator session id, or a change_name grouping many"
    )
    args = parser.parse_args(argv)
    db = CoordinatorDB()
    attempts = _export(db, args.selector)
    json.dump(attempts, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
