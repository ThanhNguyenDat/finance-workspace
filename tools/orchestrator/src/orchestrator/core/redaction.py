"""Small recursive redaction boundary for coordinator evidence and views."""

from __future__ import annotations

import re
from typing import Any

REDACTED = "<REDACTED>"
SECRET_KEY = re.compile(
    r"(?:password|passwd|secret|token|api[_-]?key|authorization|cookie|private[_-]?key|access[_-]?token)",
    re.IGNORECASE,
)
SECRET_VALUE = re.compile(
    r"(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]+|(?:api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)


def redact_text(value: str) -> str:
    return SECRET_VALUE.sub(REDACTED, value)


def redact_value(value: Any, *, key: str = "") -> Any:
    if SECRET_KEY.search(key):
        return REDACTED
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {
            str(name): redact_value(item, key=str(name)) for name, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item) for item in value]
    return value
