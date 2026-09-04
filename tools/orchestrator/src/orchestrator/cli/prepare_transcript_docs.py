"""Split an export-transcript result into per-attempt Artifact db documents.

`export-transcript` reduces a coordinator session (or change) to a chat-shaped
JSON array, one entry per attempt. The Artifact `write_db` batch tool takes a
`file_path` per write, and each such file must hold exactly one JSON document
object — not an array. This CLI does that split: one file per attempt, named
by the same document id convention the "Agent Transcripts" artifact expects
(`<session_id>-<phase lowercased>-a<attempt_no>`), so the files can be handed
straight to `write_db` without hand-crafting them.

This is read-only with respect to coordinator state: it only reads through
`export_transcript._export` and writes plain JSON files under an output
directory (default `.ops/runtime/transcript-docs/<selector>/`, matching the
project's convention for transient runtime evidence).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, NoReturn

from ..coordinator.db import CoordinatorDB
from ..core.io import CLIError, run_cli
from .export_transcript import _export

PREFIX = "prepare-transcript-docs"

DEFAULT_OUT_ROOT = Path(".ops/runtime/transcript-docs")


def doc_id(attempt: dict[str, Any]) -> str:
    phase = str(attempt.get("phase") or "unknown").lower()
    return f"{attempt['session_id']}-{phase}-a{attempt['attempt_no']}"


def write_docs(attempts: list[dict[str, Any]], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for attempt in attempts:
        path = out_dir / f"{doc_id(attempt)}.json"
        path.write_text(
            json.dumps(attempt, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=PREFIX)
    parser.add_argument(
        "selector", help="a coordinator session id, or a change_name grouping many"
    )
    parser.add_argument(
        "--out-dir",
        help="directory to write one JSON file per attempt into "
        "(default: .ops/runtime/transcript-docs/<selector>/)",
    )
    args = parser.parse_args(argv)
    db = CoordinatorDB()
    attempts = _export(db, args.selector)
    if not attempts:
        raise CLIError(f"{PREFIX}: no attempts found for: {args.selector}")
    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUT_ROOT / args.selector
    written = write_docs(attempts, out_dir)
    print(json.dumps({"out_dir": str(out_dir), "count": len(written)}))
    return 0


def cli() -> NoReturn:
    run_cli(lambda: main(), PREFIX)


if __name__ == "__main__":
    cli()
