#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
printf '%s\n' 'run-claude-command: compatibility entrypoint; routing through phase agents' >&2
exec "$SCRIPT_DIR/run-phase-agent-command.sh" "$@"
