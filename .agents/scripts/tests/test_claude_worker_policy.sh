#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
grep -Fq 'permission_mode="default"' "$ROOT_DIR/tools/orchestrator/src/orchestrator/runners/phase_adapter.py" || { printf 'test_claude_worker_policy: interactive permission mode missing\n' >&2; exit 1; }
grep -Fq '"bypassPermissions"' "$ROOT_DIR/tools/orchestrator/src/orchestrator/runners/phase_adapter.py" || { printf 'test_claude_worker_policy: SDK permission bypass missing\n' >&2; exit 1; }
grep -Fq 'can_use_tool=_operator_permission if coordinator_enabled else None' "$ROOT_DIR/tools/orchestrator/src/orchestrator/runners/phase_adapter.py" || { printf 'test_claude_worker_policy: coordinator permission callback missing\n' >&2; exit 1; }
grep -Fq 'Opus requires medium or high' "$ROOT_DIR/tools/orchestrator/src/orchestrator/runners/phase_adapter.py" || { printf 'test_claude_worker_policy: Opus policy missing\n' >&2; exit 1; }
timeout --signal=TERM --kill-after=10s 2m "$ROOT_DIR/.agents/scripts/tests/test_phase_agent_routing.sh" >/dev/null
printf '%s\n' 'test_claude_worker_policy: all checks passed'
