#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
timeout --signal=TERM --kill-after=10s 2m "$ROOT_DIR/.agents/scripts/tests/test_phase_agent_quant_launcher.sh" >/dev/null
printf '%s\n' 'test_claude_quant_launcher: compatibility checks passed'
