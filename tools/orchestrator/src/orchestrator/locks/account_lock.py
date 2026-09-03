"""Provider account locks for phase-agent workers."""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import sys
from pathlib import Path
from typing import Any

from ..accounts.registry import normalize_account, resolve_account_dir
from ..core.io import atomic_write_json, die, json_text, utc_now
from .change_lock import _ReturnStatus, change_dir, owner_is_live, root_dir

PREFIX = "ops-runtime"


def account_locks_dir() -> Path:
    return root_dir() / ".ops/runtime/account-locks"


def account_lock_dir(provider: str, account: str) -> Path:
    normalized = normalize_account(account, PREFIX)
    if provider not in {"codex", "claude"}:
        die(PREFIX, f"unsupported provider: {provider}")
    return account_locks_dir() / f"{provider}-{normalized}"


def _read_json(path: Path, tolerate_failure: bool = False) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        if tolerate_failure:
            return None
        die(PREFIX, f"could not read JSON: {path}")
    raise AssertionError("unreachable")


def lock_account(provider: str, account: str, owner_pid: str, change: str = "", session_id: str = "") -> None:
    normalized, _ = resolve_account_dir(provider, account, PREFIX)
    if not re.fullmatch(r"[0-9]+", owner_pid):
        die(PREFIX, "account lock owner pid must be numeric")
    lock = account_lock_dir(provider, normalized)
    owner = lock / "owner.json"
    lock.parent.mkdir(parents=True, exist_ok=True)
    change_path = change_dir(change) if change else None
    try:
        lock.mkdir()
    except FileExistsError:
        if owner_is_live(owner, change_path):
            print(f"ops-runtime: account lock exists for {provider}/{normalized}", file=sys.stderr)
            value = _read_json(owner, tolerate_failure=True)
            if isinstance(value, dict):
                print(json_text({key: value.get(key) for key in ("provider", "account", "change", "session_id", "pid", "hostname", "started_at")}), file=sys.stderr)
            raise _ReturnStatus(1)
        print(f"ops-runtime: releasing stale account lock (owning process is dead): {lock}", file=sys.stderr)
        shutil.rmtree(lock, ignore_errors=True)
        try:
            lock.mkdir()
        except FileExistsError:
            print(f"ops-runtime: cannot acquire account lock after stale release: {lock}", file=sys.stderr)
            raise _ReturnStatus(1)
    atomic_write_json(owner, {"provider": provider, "account": normalized, "change": change or None, "session_id": session_id or None, "pid": owner_pid, "hostname": socket.gethostname(), "started_at": utc_now()})


def unlock_account(provider: str, account: str, owner_pid: str, change: str = "", session_id: str = "") -> None:
    normalized = normalize_account(account, PREFIX)
    lock = account_lock_dir(provider, normalized)
    owner = lock / "owner.json"
    if not owner.is_file():
        return
    value = _read_json(owner, tolerate_failure=True)
    if not isinstance(value, dict):
        return
    if value.get("provider") != provider or value.get("account") != normalized or value.get("pid") != owner_pid:
        return
    if change and value.get("change") != change:
        return
    if session_id and value.get("session_id") != session_id:
        return
    owner.unlink(missing_ok=True)
    try:
        lock.rmdir()
    except OSError:
        pass
