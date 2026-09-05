"""Load the optional orchestrator YAML config file.

The file always lives at `tools/orchestrator/config.yaml` (its location is
fixed, not configurable) and is entirely optional and machine-specific --
it typically names local account directories -- so it is gitignored; see
the README for its shape.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.yaml"


def load_config() -> dict[str, Any]:
    """Return the parsed YAML config, or `{}` if no config file is present."""

    if not CONFIG_PATH.is_file():
        return {}
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def _parse_account_list(raw: list[Any]) -> list[str]:
    return [os.path.expanduser(str(item).strip()) for item in raw if str(item).strip()]


def resolve_account_list(env_var: str, config_section: str) -> list[str | None]:
    """Resolve an ordered account-config-dir list for one provider.

    Precedence: `env_var` (comma-separated, for a quick one-off override) >
    `<config_section>.accounts` in the YAML config file > a single `[None]`
    attempt using whatever the ambient environment already provides -- no
    rotation, unchanged from before either source is configured.
    """

    raw_env = os.environ.get(env_var, "").strip()
    resolved = _parse_account_list(raw_env.split(",")) if raw_env else []

    if not resolved:
        section = load_config().get(config_section)
        raw_accounts = section.get("accounts") if isinstance(section, dict) else None
        if isinstance(raw_accounts, list):
            resolved = _parse_account_list(raw_accounts)

    if not resolved:
        return [None]

    accounts: list[str | None] = list(resolved)
    return accounts


def configured_scope(config_section: str) -> list[str]:
    """Return `<config_section>.scope` from the YAML config, or `[]`.

    This is advisory metadata only (see `orchestrator-exec-cli` spec's
    "Optional advisory role/scope mismatch warning" requirement) -- unlike
    accounts, it has no environment-variable override; it is a standing
    per-machine policy declaration, not something that needs a quick
    one-off override.
    """

    section = load_config().get(config_section)
    raw_scope = section.get("scope") if isinstance(section, dict) else None
    if not isinstance(raw_scope, list):
        return []
    return [str(item).strip() for item in raw_scope if str(item).strip()]
