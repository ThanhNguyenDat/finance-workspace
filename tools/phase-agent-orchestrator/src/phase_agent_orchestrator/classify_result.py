"""Shared result-class mapping for provider SDK results and legacy log shims."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

RESULT_CLASSES = (
    "success",
    "timeout",
    "global-quota-exhausted",
    "model-unavailable",
    "model-specific-limit",
    "transient-rate-limit",
    "auth-error",
    "network-error",
    "implementation-error",
    "unknown-error",
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "value") and not isinstance(value, (str, bytes)):
        return _text(value.value)
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, BaseException):
        return str(value).lower()
    if isinstance(value, Iterable) and not isinstance(value, (bytes, dict)):
        return " ".join(_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items())
    if hasattr(value, "model_dump"):
        return _text(value.model_dump(mode="json", by_alias=True))
    if hasattr(value, "__dict__"):
        return _text(vars(value))
    return str(value).lower()


def _structured_fields(value: Any) -> str:
    fields: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"code", "type", "category", "error_type", "reason"}:
                fields.append(_text(item))
            fields.append(_structured_fields(item))
    elif isinstance(value, list):
        for item in value:
            fields.append(_structured_fields(item))
    return " ".join(fields)


def _message_fields(value: Any) -> str:
    fields: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"message", "detail", "type", "status"}:
                fields.append(_text(item))
            fields.append(_message_fields(item))
    elif isinstance(value, list):
        for item in value:
            fields.append(_message_fields(item))
    return " ".join(fields)


def _matches(value: str, pattern: str) -> bool:
    return re.search(pattern, value) is not None


def classify_fields(
    *,
    status: int | None = None,
    structured: str = "",
    messages: str = "",
    timed_out: bool = False,
) -> str:
    """Apply the existing classifier precedence to normalized SDK fields."""

    structured = structured.lower()
    messages = messages.lower()
    if timed_out or status == 124:
        return "timeout"
    if status == 0:
        return "success"
    if _matches(
        structured,
        r"(^|\s)(insufficient_quota|quota_exhausted|global_quota_exhausted|account_quota_exhausted|usage_limit_reached|credits_exhausted)(\s|$)",
    ):
        return "global-quota-exhausted"
    if _matches(
        structured,
        r"(^|\s)(model_not_found|model_unavailable|unsupported_model|model_routing_failure)(\s|$)",
    ):
        return "model-unavailable"
    if _matches(
        structured,
        r"(^|\s)(model_capacity_exceeded|model_limit_reached|model_rate_limit_exceeded|model_usage_limit)(\s|$)",
    ):
        return "model-specific-limit"
    if _matches(structured, r"(^|\s)(rate_limit_exceeded|too_many_requests|http_429)(\s|$)"):
        return "transient-rate-limit"
    if _matches(structured, r"(^|\s)(authentication_error|invalid_api_key|unauthorized|permission_denied)(\s|$)"):
        return "auth-error"
    if _matches(structured, r"(^|\s)(network_error|connection_error|dns_error|tls_error)(\s|$)"):
        return "network-error"
    if _matches(structured, r"(^|\s)(timeout|request_timeout|deadline_exceeded)(\s|$)"):
        return "timeout"
    if _matches(structured, r"(^|\s)(implementation_error|worker_failed|task_failed)(\s|$)"):
        return "implementation-error"
    if _matches(messages, r"(global|account(-wide)?)[\s_-]*(codex[\s_-]*)?quota[^.]{0,80}(exhausted|depleted|reached|exceeded)") or _matches(messages, r"(quota|usage[\s_-]*limit)[^.]*((exhausted|depleted)[^.]*(account|global)|exhausted)") or _matches(messages, r"usage[\s_-]*limit[^.]{0,80}(exhausted|depleted)") or _matches(messages, r"(account|session)[\s_-]*(usage[\s_-]*)?(cap|limit)[^.]{0,80}(reached|exceeded|exhausted)") or _matches(messages, r"no\s+remaining\s+(quota|credits)"):
        return "global-quota-exhausted"
    if _matches(messages, r"(selected[\s_-]*)?model[^.]{0,80}(not[\s_-]*found|unavailable|not[\s_-]*available|unsupported|routing[\s_-]*failure)"):
        return "model-unavailable"
    if _matches(messages, r"model[^.]{0,80}(capacity|specific[\s_-]*limit|usage[\s_-]*limit)[^.]{0,80}(exceeded|reached|unavailable|full)") or _matches(messages, r"(capacity|limit|quota)[^.]{0,80}for\s+(the\s+)?(selected\s+)?model"):
        return "model-specific-limit"
    if _matches(messages, r"(^|[^0-9])429([^0-9]|$)|too[\s_-]*many[\s_-]*requests|rate[\s_-]*limit"):
        return "transient-rate-limit"
    if _matches(messages, r"(^|[^0-9])(401|403)([^0-9]|$)|authentication|unauthorized|invalid[\s_-]*(api[\s_-]*)?key|permission[\s_-]*denied"):
        return "auth-error"
    if _matches(messages, r"network[\s_-]*error|connection[\s_-]*(failed|reset|refused)|dns|enotfound|tls[\s_-]*(error|failure)|could\s+not\s+resolve"):
        return "network-error"
    if _matches(messages, r"timed[\s_-]*out|timeout|deadline[\s_-]*exceeded"):
        return "timeout"
    if _matches(messages, r"implementation[\s_-]*error|worker[\s_-]*failed|task[\s_-]*failed|\"status\"\s*:\s*\"failed\""):
        return "implementation-error"
    return "unknown-error"


def classify_sdk_result(
    result: Any = None,
    *,
    provider: str,
    timed_out: bool = False,
    hard_killed: bool = False,
    error: BaseException | None = None,
) -> str:
    """Map a Claude ``ResultMessage`` or Codex ``TurnResult`` to the contract."""

    if timed_out or hard_killed:
        return "timeout"
    if error is not None:
        return classify_fields(messages=_text(error), structured=_text(error))
    if result is None:
        return "unknown-error"
    status = _text(getattr(result, "status", None))
    subtype = _text(getattr(result, "subtype", None))
    terminal_reason = _text(getattr(result, "terminal_reason", None))
    api_status = getattr(result, "api_error_status", None)
    if api_status in {401, 403}:
        return "auth-error"
    if api_status == 429:
        return "transient-rate-limit"
    structured = " ".join(
        part
        for part in (
            status,
            subtype,
            _text(getattr(result, "stop_reason", None)),
            _text(getattr(result, "error", None)),
            _text(getattr(result, "is_error", None)),
            terminal_reason,
            _text(getattr(result, "errors", None)),
            _text(getattr(getattr(result, "error", None), "codex_error_info", None)),
        )
        if part
    )
    messages = " ".join(
        part
        for part in (
            _text(getattr(result, "result", None)),
            _text(getattr(result, "final_response", None)),
            _text(getattr(result, "message", None)),
            _text(getattr(result, "error", None)),
            _text(getattr(result, "errors", None)),
        )
        if part
    )
    if provider == "claude" and subtype == "success" and not getattr(result, "is_error", False):
        return "success"
    if provider == "claude" and subtype == "error_max_budget_usd":
        return "global-quota-exhausted"
    if provider == "claude" and subtype == "error_max_turns":
        return "implementation-error"
    if provider == "codex" and status == "completed":
        return "success"
    if provider == "codex" and status == "interrupted":
        return "timeout"
    return classify_fields(structured=structured, messages=messages)


def _load_log(path: Path) -> list[Any]:
    values: list[Any] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError:
            values.append(line)
    return values


def classify_legacy_logs(status: int, stdout_log: Path, stderr_log: Path) -> str:
    """Compatibility entry point for existing shell fixtures and operators."""

    stdout_values = _load_log(stdout_log)
    stderr_values = _load_log(stderr_log)
    return classify_fields(
        status=status,
        structured=" ".join(_structured_fields(value) for value in stdout_values + stderr_values),
        messages=" ".join(_message_fields(value) for value in stdout_values + stderr_values)
        + " "
        + stderr_log.read_text(encoding="utf-8").lower(),
    )
