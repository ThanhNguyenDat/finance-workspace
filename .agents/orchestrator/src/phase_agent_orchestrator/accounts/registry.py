"""Provider account registration and resolution."""

from __future__ import annotations

import os
import re
from pathlib import Path

from ..io import die

ACCOUNT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def normalize_account(account: str, prefix: str) -> str:
    if not isinstance(account, str) or not ACCOUNT_NAME.fullmatch(account):
        die(prefix, "account must contain only letters, numbers, underscores, or hyphens")
    return account.lower()


def account_environment_name(provider: str, account: str, prefix: str) -> tuple[str, str]:
    normalized = normalize_account(account, prefix)
    if provider not in {"codex", "claude"}:
        die(prefix, f"unsupported provider: {provider}")
    return normalized, f"PHASE_AGENT_{provider.upper()}_ACCOUNT_{normalized.upper()}_DIR"


def resolve_account_dir(provider: str, account: str, prefix: str) -> tuple[str, Path]:
    normalized, variable = account_environment_name(provider, account, prefix)
    configured = os.environ.get(variable, "")
    if not configured:
        die(prefix, f"unregistered account '{normalized}' for {provider}; set {variable}")
    directory = Path(configured).expanduser()
    if not directory.is_dir():
        die(prefix, f"account '{normalized}' for {provider} directory does not exist: {directory}")
    return normalized, directory.resolve()
