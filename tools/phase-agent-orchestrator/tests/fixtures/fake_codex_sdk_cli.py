#!/usr/bin/env python3
"""Minimal Codex app-server fixture that ignores turn/interrupt."""

from __future__ import annotations

import json
import os
import sys
import threading
import time


THREAD_ID = "thread-fixture"
TURN_ID = "turn-fixture"


def emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


for raw_line in sys.stdin:
    message = json.loads(raw_line)
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        emit(
            {
                "id": request_id,
                "result": {
                    "userAgent": "fake-codex/0.1",
                    "serverInfo": {"name": "fake-codex", "version": "0.1"},
                },
            }
        )
    elif method == "thread/start":
        emit(
            {
                "id": request_id,
                "result": {
                    "approvalPolicy": "never",
                    "approvalsReviewer": "user",
                    "cwd": os.getcwd(),
                    "instructionSources": [],
                    "model": "fixture-model",
                    "modelProvider": "fixture-provider",
                    "reasoningEffort": "medium",
                    "sandbox": {"type": "dangerFullAccess"},
                    "thread": {
                        "id": THREAD_ID,
                        "cliVersion": "0.1",
                        "createdAt": 1,
                        "cwd": os.getcwd(),
                        "ephemeral": True,
                        "modelProvider": "fixture-provider",
                        "preview": "fixture prompt",
                        "sessionId": "session-fixture",
                        "status": {"type": "idle"},
                        "path": None,
                        "source": "appServer",
                        "turns": [],
                        "updatedAt": 1,
                    },
                },
            }
        )
    elif method == "turn/start":
        emit(
            {
                "id": request_id,
                "result": {
                    "turn": {
                        "id": TURN_ID,
                        "status": "inProgress",
                        "items": [],
                        "startedAt": 1,
                        "completedAt": None,
                        "durationMs": None,
                        "error": None,
                    }
                },
            }
        )
        marker = os.environ.get("FAKE_SDK_STARTED_MARKER")
        if marker:
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("turn-started\n")
        if os.environ.get("FAKE_SDK_MODE") == "complete":
            def complete_later() -> None:
                time.sleep(0.05)
                emit(
                    {
                        "method": "turn/completed",
                        "params": {
                            "threadId": THREAD_ID,
                            "turn": {
                                "id": TURN_ID,
                                "status": "completed",
                                "error": None,
                                "items": [],
                                "startedAt": 1,
                                "completedAt": 2,
                                "durationMs": 1,
                            },
                        },
                    }
                )

            threading.Thread(target=complete_later, daemon=True).start()
    elif method == "turn/interrupt":
        marker = os.environ.get("FAKE_SDK_INTERRUPT_MARKER")
        if marker:
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("interrupt-received\n")
        # Deliberately do not answer: this simulates an uncooperative server.
