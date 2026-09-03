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


def trace(payload: dict[str, object]) -> None:
    path = os.environ.get("FAKE_SDK_TRACE")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")


for raw_line in sys.stdin:
    message = json.loads(raw_line)
    trace(message)
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
        mode = os.environ.get("FAKE_CODEX_MODE", os.environ.get("FAKE_SDK_MODE"))
        fake_result = os.environ.get(
            "FAKE_CODEX_RESULT", os.environ.get("FAKE_RESULT", "")
        )
        if mode == "quota-mutate":
            target = os.environ.get("FAKE_REPO")
            if target:
                with open(
                    os.path.join(target, "partial.txt"), "w", encoding="utf-8"
                ) as handle:
                    handle.write("partial\n")
        if mode in {"complete", "quota-mutate", "no-gate", "delay"} or fake_result in {
            "success",
            "quota",
            "rate",
            "model-limit",
            "auth",
            "network",
            "unknown",
            "implementation",
        }:
            fake_result = (
                "quota" if mode == "quota-mutate" else (fake_result or "success")
            )
            if fake_result == "success":
                status = "completed"
                error = None
            else:
                status = "failed"
                error = {
                    "message": {
                        "quota": "global_quota_exhausted",
                        "rate": "rate_limit_exceeded",
                        "model-limit": "model_capacity_exceeded",
                        "auth": "authentication_error",
                        "network": "network_error",
                        "unknown": "unexpected",
                        "implementation": "implementation_error",
                    }[fake_result]
                }

            def complete_later(
                mode: str | None = mode,
                status: str = status,
                error: dict[str, str] | None = error,
            ) -> None:
                time.sleep(
                    float(os.environ.get("FAKE_SDK_DELAY_SECONDS", "0.05"))
                    if mode == "delay"
                    else 0.05
                )
                message_text = os.environ.get(
                    "FAKE_SDK_RESULT_TEXT",
                    "OK\nFINAL_VERIFY_GATE: PASS\nP0_FINDINGS: 0\nP1_FINDINGS: 0\nOBJECTIVE_GATES: PASS",
                )
                if mode == "no-gate":
                    message_text = "OK"
                if status == "completed":
                    emit(
                        {
                            "method": "item/completed",
                            "params": {
                                "threadId": THREAD_ID,
                                "turnId": TURN_ID,
                                "completedAtMs": 2,
                                "item": {
                                    "id": "item-fixture",
                                    "type": "agentMessage",
                                    "text": message_text,
                                },
                            },
                        }
                    )
                emit(
                    {
                        "method": "turn/completed",
                        "params": {
                            "threadId": THREAD_ID,
                            "turn": {
                                "id": TURN_ID,
                                "status": status,
                                "error": error,
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
