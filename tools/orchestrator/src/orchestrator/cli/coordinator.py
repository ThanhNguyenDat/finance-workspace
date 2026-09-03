"""CLI for the provider-neutral local coordinator."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, NoReturn

from ..coordinator import (
    CoordinatorDB,
    CoordinatorError,
    admit_session,
    answer_question,
    archive_session,
    archive_terminal_history,
    cancel_session,
    create_session,
    events_since,
    interrupt_session,
    record_verification_findings,
    recover_session,
    resume_session,
    session_status,
)
from ..core.io import CLIError, json_text, run_cli

PREFIX = "coordinator"


def usage() -> NoReturn:
    print(
        "Usage: coordinator <submit CHANGE [CONTEXT_JSON]|resume SESSION|status SESSION|recover SESSION|cancel SESSION VERSION FENCING_TOKEN|interrupt SESSION VERSION FENCING_TOKEN SAFE_BOUNDARY [REASON]|attach SESSION [OFFSET]|monitor SESSION [OFFSET]|follow SESSION [OFFSET] [SECONDS]|findings SESSION VERSION FENCING_TOKEN FINDINGS_JSON|archive SESSION|archive-history SESSION|answer SESSION QUESTION_ID FENCING_TOKEN RESPONSE>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def _context(value: str | None) -> dict[str, Any]:
    if value is None:
        return {"request": ""}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise CLIError(f"{PREFIX}: context must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise CLIError(f"{PREFIX}: context must be a JSON object")
    return parsed


def _findings(value: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise CLIError(f"{PREFIX}: findings must be valid JSON") from exc
    if not isinstance(parsed, list) or any(
        not isinstance(item, dict) for item in parsed
    ):
        raise CLIError(f"{PREFIX}: findings must be a JSON array of objects")
    return parsed


def _elapsed_seconds(started_at: str) -> int:
    try:
        started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        return max(0, int((datetime.now(timezone.utc) - started).total_seconds()))
    except TypeError, ValueError:
        return 0


def main() -> int:
    args = sys.argv[1:]
    command = args[0] if args else ""
    db = CoordinatorDB()
    try:
        if command == "submit" and 2 <= len(args) <= 3:
            session = create_session(
                args[1], _context(args[2] if len(args) == 3 else None), db=db
            )
            admission = admit_session(session["id"], db=db)
            print(json_text({"session": session, "admission": admission}))
            return 0 if admission["admitted"] else 2
        if command == "resume" and len(args) == 2:
            print(json_text(resume_session(args[1], db=db)))
            return 0
        if command == "status" and len(args) == 2:
            print(json_text(session_status(args[1], db=db)))
            return 0
        if command == "recover" and len(args) == 2:
            print(json_text(recover_session(args[1], db=db)))
            return 0
        if command == "cancel" and len(args) == 4:
            print(
                json_text(
                    cancel_session(
                        args[1],
                        expected_version=int(args[2]),
                        fencing_token=args[3],
                        db=db,
                    )
                )
            )
            return 0
        if command == "interrupt" and 5 <= len(args) <= 6:
            boundary = args[4].lower()
            if boundary not in {"true", "false"}:
                raise CLIError(f"{PREFIX}: safe boundary must be true or false")
            print(
                json_text(
                    interrupt_session(
                        args[1],
                        expected_version=int(args[2]),
                        fencing_token=args[3],
                        safe_boundary=boundary == "true",
                        reason=args[5] if len(args) == 6 else "operator-interrupt",
                        db=db,
                    )
                )
            )
            return 0
        if command == "attach" and 2 <= len(args) <= 3:
            print(
                json_text(
                    {
                        "session": session_status(args[1], db=db),
                        "events": events_since(
                            args[1], int(args[2]) if len(args) == 3 else 0, db=db
                        ),
                    }
                )
            )
            return 0
        if command == "findings" and len(args) == 5:
            print(
                json_text(
                    record_verification_findings(
                        args[1],
                        _findings(args[4]),
                        expected_version=int(args[2]),
                        fencing_token=args[3],
                        db=db,
                    )
                )
            )
            return 0
        if command == "archive" and len(args) == 2:
            print(json_text(archive_session(args[1], db=db)))
            return 0
        if command == "archive-history" and len(args) == 2:
            print(json_text(archive_terminal_history(args[1], db=db)))
            return 0
        if command == "monitor" and 2 <= len(args) <= 3:
            status = session_status(args[1], db=db)
            attempts = status["attempts"]
            latest = attempts[-1] if attempts else {}
            events = events_since(args[1], int(args[2]) if len(args) == 3 else 0, db=db)
            latest_event = events[-1] if events else {}
            latest_payload = latest_event.get("safe_payload", {})
            if not isinstance(latest_payload, dict):
                latest_payload = {}
            quota_result = (
                latest.get("result_class")
                if latest.get("result_class")
                in {
                    "global-quota-exhausted",
                    "auth-error",
                    "model-unavailable",
                    "model-specific-limit",
                    "transient-rate-limit",
                }
                else "-"
            )
            tests = latest_payload.get(
                "tests", status["session"].get("checkpoint", {}).get("tests", "-")
            )
            started_at = latest.get("started_at") or status["session"]["created_at"]
            print(
                f"session={status['session']['id']} phase={status['session']['phase']} "
                f"status={status['session']['status']} version={status['session']['version']} "
                f"provider={latest.get('provider', status['session'].get('selected_provider') or '-')} "
                f"model={latest.get('model', '-')} account={latest.get('account', status['session'].get('selected_account') or '-')} "
                f"elapsed_seconds={_elapsed_seconds(started_at)} last_result={latest.get('result_class', '-')} "
                f"current_action={latest_event.get('event_type', '-')} quota_failover={quota_result} "
                f"tests={tests} updated_at={status['session']['updated_at']} events={status['event_count']} "
                f"terminal={status['session']['status']}"
            )
            for event in events:
                payload = json_text(event["safe_payload"])
                print(
                    f"[{event['sequence']}] {event['event_type']} phase={event['phase']} payload={payload}"
                )
            return 0
        if command == "follow" and 2 <= len(args) <= 4:
            offset = int(args[2]) if len(args) >= 3 else 0
            seconds = int(args[3]) if len(args) == 4 else 60
            if offset < 0 or seconds < 1 or seconds > 3600:
                raise CLIError(f"{PREFIX}: follow offset/seconds are out of bounds")
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                events = events_since(args[1], offset, db=db)
                for event in events:
                    print(
                        f"[{event['sequence']}] {event['event_type']} phase={event['phase']} payload={json_text(event['safe_payload'])}",
                        flush=True,
                    )
                    offset = event["sequence"]
                if (
                    session_status(args[1], db=db)["session"]["status"]
                    in {"COMPLETED", "FAILED", "BLOCKED", "CANCELLED"}
                    and not events
                ):
                    break
                time.sleep(0.2)
            return 0
        if command == "answer" and len(args) == 5:
            print(
                json_text(
                    answer_question(
                        args[1], args[2], args[4], fencing_token=args[3], db=db
                    )
                )
            )
            return 0
    except (ValueError, CoordinatorError) as exc:
        raise CLIError(f"{PREFIX}: {exc}") from exc
    usage()


def cli() -> NoReturn:
    run_cli(main, PREFIX)


if __name__ == "__main__":
    cli()
