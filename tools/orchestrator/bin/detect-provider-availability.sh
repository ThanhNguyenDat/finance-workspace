#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="${PHASE_AGENT_ORCHESTRATOR_PROJECT:-$SCRIPT_DIR/..}"
PROJECT_DIR="$(cd -- "$PROJECT_DIR" 2>/dev/null && pwd -P || true)"
[[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]] || { printf 'detect-provider-availability: orchestrator project not found\n' >&2; exit 1; }
if UV_BIN="$(command -v uv 2>/dev/null)"; then exec "$UV_BIN" run --project "$PROJECT_DIR" detect-provider-availability "$@"; fi
if [[ -x "$PROJECT_DIR/.venv/bin/detect-provider-availability" ]]; then exec "$PROJECT_DIR/.venv/bin/detect-provider-availability" "$@"; fi
printf 'detect-provider-availability: uv is required (or bootstrap tools/orchestrator/.venv first)\n' >&2
exit 1
