#!/usr/bin/env python3
"""Minimal Claude stream-json fixture that ignores interrupt requests."""

from __future__ import annotations

import json
import os
import sys


def emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


for raw_line in sys.stdin:
    message = json.loads(raw_line)
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
        if os.environ.get("FAKE_SDK_MODE") in {"complete", "quota-first"}:
            quota = os.environ.get("FAKE_SDK_MODE") == "quota-first" and os.environ.get("CLAUDE_CONFIG_DIR", "").endswith("personal-02")
            emit(
                {
                    "type": "result",
                    "subtype": "success",
                    "duration_ms": 1,
                    "duration_api_ms": 1,
                    "is_error": quota,
                    "num_turns": 1,
                    "session_id": "fixture-session",
                    "result": os.environ.get("CLAUDE_CONFIG_DIR", ""),
                    "errors": ["global_quota_exhausted"] if quota else None,
                    "terminal_reason": "completed",
                }
            )
        else:
            # Deliberately keep the session open.
            pass
