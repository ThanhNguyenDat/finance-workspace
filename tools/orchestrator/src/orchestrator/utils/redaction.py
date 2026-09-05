"""Redact credential-shaped values before anything reaches stdout/stderr."""

from __future__ import annotations

import re
from typing import Any

REDACTED = "<REDACTED>"

_SECRET_KEY = re.compile(
    r"(?:password|passwd|secret|token|api[_-]?key|authorization|cookie"
    r"|private[_-]?key|access[_-]?token)",
    re.IGNORECASE,
)
_SECRET_VALUE = re.compile(
    r"(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]+"
    r"|(?:api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)


def redact_text(text: str) -> str:
    """Replace credential-shaped substrings in free text with a placeholder."""

    return _SECRET_VALUE.sub(REDACTED, text)


def redact_value(value: Any, *, key: str = "") -> Any:
    """Recursively redact a JSON-shaped value, given the field name that held it."""

    if _SECRET_KEY.search(key):
        return REDACTED
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {
            str(name): redact_value(item, key=str(name)) for name, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [redact_value(item) for item in value]
    return value
