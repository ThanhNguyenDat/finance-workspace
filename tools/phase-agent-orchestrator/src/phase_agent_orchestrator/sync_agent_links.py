"""Synchronize shared rules and skills into agent-native directories."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn


PROJECT_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = PROJECT_DIR.parents[1]
AGENTS_DIR = ROOT_DIR / ".agents"
TOOLS = (".claude", ".kimi-code", ".opencode")


def sync_entries(source_dir: Path, target_dir: Path, link_prefix: str, check_only: bool) -> int:
    status = 0
    if not target_dir.is_dir():
        if check_only:
            print(f"missing target directory: {target_dir}", file=sys.stderr)
            return 1
        target_dir.mkdir(parents=True, exist_ok=True)

    for target in target_dir.iterdir():
        if not target.is_symlink():
            continue
        raw = os.readlink(target)
        if raw.startswith(f"{link_prefix}/") and not target.exists():
            if check_only:
                print(f"stale link: {target} -> {raw}", file=sys.stderr)
                status = 1
            else:
                target.unlink()
                print(f"removed stale link: {target}")

    relative_source = source_dir.relative_to(AGENTS_DIR)
    for source in source_dir.iterdir():
        if not source.exists():
            continue
        name = source.name
        if name == ".openspec-target" or name.startswith("openspec"):
            continue
        target = target_dir / name
        expected = f"../../.agents/{relative_source}/{name}"

        if target.exists() or target.is_symlink():
            if target.is_symlink():
                raw = os.readlink(target)
                if raw != expected:
                    print(f"incorrect link: {target} -> {raw} (expected {expected})", file=sys.stderr)
                    status = 1
            else:
                print(f"real local entry blocks shared link: {target}", file=sys.stderr)
                status = 1
            continue

        if check_only:
            print(f"missing link: {target} (expected -> {expected})", file=sys.stderr)
            status = 1
        else:
            target.symlink_to(expected)
            print(f"linked {target} -> {expected}")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sync-agent-links")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    status = 0
    for tool in TOOLS:
        status |= sync_entries(AGENTS_DIR / "skills", ROOT_DIR / tool / "skills", "../../.agents/skills", args.check)
        status |= sync_entries(AGENTS_DIR / "rules", ROOT_DIR / tool / "rules", "../../.agents/rules", args.check)
    if status:
        message = "Agent skill/rule links need synchronization." if args.check else "Agent skill/rule synchronization failed."
        print(message, file=sys.stderr)
        return status
    print("Agent skill/rule links are synchronized." if args.check else "Agent skill/rule links are up to date.")
    return 0


def cli() -> NoReturn:
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
