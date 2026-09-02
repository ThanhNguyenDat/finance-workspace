"""Git worktree fingerprint compatible with the legacy phase-agent scripts."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def fingerprint(root: Path) -> str:
    """Hash the exact byte stream emitted by the bash fingerprint function."""

    digest = hashlib.sha256()
    digest.update(_git(root, "status", "--porcelain=v1", "-z"))
    digest.update(_git(root, "diff", "--binary", "HEAD"))
    paths = _git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    for raw_path in paths:
        if not raw_path:
            continue
        relative = os.fsdecode(raw_path)
        digest.update(raw_path + b"\0")
        path = root / relative
        if path.is_symlink():
            digest.update(f"symlink:{os.readlink(path)}\0".encode())
            continue
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        digest.update(f"{content_hash}  {relative}\n".encode())
    return digest.hexdigest()
