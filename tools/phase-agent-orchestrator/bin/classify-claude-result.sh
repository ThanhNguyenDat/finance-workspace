#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="${PHASE_AGENT_ORCHESTRATOR_PROJECT:-$SCRIPT_DIR/..}"
PROJECT_DIR="$(cd -- "$PROJECT_DIR" 2>/dev/null && pwd -P || true)"
[[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]] || { printf 'classify-claude-result: orchestrator project not found\n' >&2; exit 1; }
if UV_BIN="$(command -v uv 2>/dev/null)"; then exec "$UV_BIN" run --project "$PROJECT_DIR" classify-claude-result "$@"; fi
if [[ -x "$PROJECT_DIR/.venv/bin/classify-claude-result" ]]; then exec "$PROJECT_DIR/.venv/bin/classify-claude-result" "$@"; fi
printf 'classify-claude-result: uv is required (or bootstrap tools/phase-agent-orchestrator/.venv first)\n' >&2
exit 1
