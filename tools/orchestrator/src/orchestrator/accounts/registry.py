"""Provider account registration and resolution."""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

from ..core.io import CLIError, die

ACCOUNT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
PROVIDERS = {"codex", "claude"}
ACCOUNTS_FILE_ENV = "PHASE_AGENT_ACCOUNTS_FILE"


def normalize_account(account: str, prefix: str) -> str:
    if not isinstance(account, str) or not ACCOUNT_NAME.fullmatch(account):
        die(
            prefix,
            "account must contain only letters, numbers, underscores, or hyphens",
        )
    return account.lower()


def account_environment_name(
    provider: str, account: str, prefix: str
) -> tuple[str, Path]:
    normalized = normalize_account(account, prefix)
    if provider not in PROVIDERS:
        die(prefix, f"unsupported provider: {provider}")
    configured = os.environ.get(ACCOUNTS_FILE_ENV)
    accounts_file = (
        Path(configured).expanduser()
        if configured
        else Path(__file__).resolve().parents[3] / "accounts.yaml"
    )
    return normalized, accounts_file


def resolve_account_dir(provider: str, account: str, prefix: str) -> tuple[str, Path]:
    normalized, accounts_file = account_environment_name(provider, account, prefix)
    if not accounts_file.is_file():
        die(prefix, f"accounts registry file does not exist: {accounts_file}")
    try:
        with accounts_file.open(encoding="utf-8") as handle:
            registry = yaml.safe_load(handle)
    except OSError, UnicodeDecodeError, yaml.YAMLError:
        die(prefix, f"could not read accounts registry file: {accounts_file}")
    if not isinstance(registry, dict):
        die(
            prefix, f"accounts registry must map providers to accounts: {accounts_file}"
        )
    provider_accounts = registry.get(provider)
    if not isinstance(provider_accounts, dict) or not provider_accounts:
        die(
            prefix, f"no accounts configured for provider {provider} in {accounts_file}"
        )
    configured = provider_accounts.get(normalized)
    if not isinstance(configured, str) or not configured:
        die(
            prefix,
            f"account '{normalized}' not found under provider {provider} in {accounts_file}",
        )
    directory = Path(configured).expanduser()
    if not directory.is_dir():
        die(
            prefix,
            f"account '{normalized}' for {provider} directory does not exist: {directory}",
        )
    return normalized, directory.resolve()


def configured_accounts(provider: str) -> list[str]:
    """Return usable account names in the local registry, in YAML order."""

    if provider not in PROVIDERS:
        return []
    configured = os.environ.get(ACCOUNTS_FILE_ENV)
    accounts_file = (
        Path(configured).expanduser()
        if configured
        else Path(__file__).resolve().parents[3] / "accounts.yaml"
    )
    try:
        with accounts_file.open(encoding="utf-8") as handle:
            registry = yaml.safe_load(handle)
    except OSError, UnicodeDecodeError, yaml.YAMLError:
        return []
    values = registry.get(provider) if isinstance(registry, dict) else None
    if not isinstance(values, dict):
        return []
    result: list[str] = []
    for name, directory in values.items():
        if not isinstance(name, str) or not isinstance(directory, str):
            continue
        try:
            normalized = normalize_account(name, "phase-agent-state")
        except CLIError:
            continue
        if Path(directory).expanduser().is_dir():
            result.append(normalized)
    return result
