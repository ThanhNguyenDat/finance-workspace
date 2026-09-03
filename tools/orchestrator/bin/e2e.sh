#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="${PHASE_AGENT_ORCHESTRATOR_PROJECT:-$SCRIPT_DIR/..}"
PROJECT_DIR="$(cd -- "$PROJECT_DIR" 2>/dev/null && pwd -P || true)"
[[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]] || { printf 'e2e: orchestrator project not found\n' >&2; exit 1; }
if UV_BIN="$(command -v uv 2>/dev/null)"; then exec "$UV_BIN" run --project "$PROJECT_DIR" e2e "$@"; fi
if [[ -x "$PROJECT_DIR/.venv/bin/e2e" ]]; then exec "$PROJECT_DIR/.venv/bin/e2e" "$@"; fi
printf 'e2e: uv is required (or bootstrap tools/orchestrator/.venv first)\n' >&2
exit 1
