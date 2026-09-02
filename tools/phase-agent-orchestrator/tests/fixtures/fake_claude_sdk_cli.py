#!/usr/bin/env python3
"""Minimal Claude stream-json fixture that ignores interrupt requests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time


def emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def trace(payload: dict[str, object]) -> None:
    path = os.environ.get("FAKE_SDK_TRACE")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")


for raw_line in sys.stdin:
    message = json.loads(raw_line)
    trace(message)
    if message.get("type") == "control_request":
        request = message.get("request", {})
        subtype = request.get("subtype")
        if subtype == "initialize":
            emit(
                {
                    "type": "control_response",
                    "response": {
                        "request_id": message["request_id"],
                        "subtype": "success",
                        "response": {"commands": []},
                    },
                }
            )
        elif subtype == "interrupt":
            marker = os.environ.get("FAKE_SDK_INTERRUPT_MARKER")
            if marker:
                with open(marker, "w", encoding="utf-8") as handle:
                    handle.write("interrupt-received\n")
            # Deliberately do not answer: this simulates an uncooperative CLI.
    elif message.get("type") == "user":
        marker = os.environ.get("FAKE_SDK_STARTED_MARKER")
        if marker:
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("prompt-received\n")
        mode = os.environ.get("FAKE_CLAUDE_MODE", os.environ.get("FAKE_SDK_MODE"))
        fake_result = os.environ.get("FAKE_RESULT", "success")
        account_trace = os.environ.get("FAKE_SDK_ACCOUNT_TRACE")
        if account_trace:
            with open(account_trace, "a", encoding="utf-8") as handle:
                handle.write(os.environ.get("CLAUDE_CONFIG_DIR", "") + "\n")
        if mode in {"delay", "quota-delay"}:
            time.sleep(float(os.environ.get("FAKE_SDK_DELAY_SECONDS", "2")))
        if mode == "mutate":
            target = os.environ.get("FAKE_REPO")
            if target:
                Path(target, "verify-mutation.txt").write_text("bad\n", encoding="utf-8")
        if mode != "hang" and (mode in {"complete", "quota-first", "quota-always"} or fake_result in {"success", "quota", "rate", "auth"}):
            quota = (mode == "quota-first" and os.environ.get("CLAUDE_CONFIG_DIR", "").endswith("personal-02")) or mode == "quota-always" or mode == "quota-delay" or (mode == "quota-work" and os.environ.get("CLAUDE_CONFIG_DIR", "") == os.environ.get("FAKE_CLAUDE_QUOTA_DIR", "")) or fake_result == "quota"
            error_code = {"rate": "rate_limit_exceeded", "auth": "authentication_error"}.get(fake_result)
            result_text = os.environ.get("FAKE_SDK_RESULT_TEXT", os.environ.get("CLAUDE_CONFIG_DIR", ""))
            emit(
                {
                    "type": "result",
                    "subtype": "success",
                    "duration_ms": 1,
                    "duration_api_ms": 1,
                    "is_error": quota,
                    "num_turns": 1,
                    "session_id": "fixture-session",
                    "result": result_text,
                    "errors": ["global_quota_exhausted"] if quota else ([error_code] if error_code else None),
                    "api_error_status": 401 if fake_result == "auth" else (429 if fake_result == "rate" else None),
                    "terminal_reason": "completed",
                }
            )
        else:
            # Deliberately keep the session open.
            pass
