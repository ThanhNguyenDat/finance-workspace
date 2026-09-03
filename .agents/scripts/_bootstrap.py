"""Bootstrap the workspace's Python orchestration package for script entrypoints."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent


def project_dir() -> Path:
    configured = os.environ.get("PHASE_AGENT_ORCHESTRATOR_PROJECT")
    return Path(configured).expanduser().resolve() if configured else ROOT_DIR / "tools/phase-agent-orchestrator"


def bootstrap() -> Path:
    project = project_dir()
    if not project.is_dir():
        raise SystemExit(f"{Path(sys.argv[0]).name}: orchestrator project not found: {project}")

    venv_python = project / ".venv/bin/python"
    if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    source_dir = project / "src"
    if not source_dir.is_dir():
        raise SystemExit(f"{Path(sys.argv[0]).name}: orchestrator source not found: {source_dir}")
    sys.path.insert(0, str(source_dir))
    return project
