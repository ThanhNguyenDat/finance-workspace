#!/usr/bin/env bash
set -Eeuo pipefail

TEST_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

export PHASE_AGENT_PROVIDER=codex
export PHASE_AGENT_MODEL=inherited-model
export PHASE_AGENT_EFFORT=low
export PHASE_AGENT_FINAL_VERIFY_PROVIDER=codex
export PHASE_AGENT_FINAL_VERIFY_MODEL=inherited-final-model
export PHASE_AGENT_FINAL_VERIFY_EFFORT=low
export PHASE_AGENT_ATTEMPT_ID=inherited-attempt
export PHASE_AGENT_CONTINUATION=true
export PHASE_AGENT_EVIDENCE_BASE=/tmp/inherited-evidence-must-not-be-used
export OPS_ROOT=/tmp/inherited-ops-root-must-not-be-used

timeout --signal=TERM --kill-after=10s 3m "$TEST_DIR/test_ops_orchestration.sh" >/dev/null
timeout --signal=TERM --kill-after=10s 2m "$TEST_DIR/test_phase_agent_routing.sh" >/dev/null

printf '%s\n' 'test_hermetic_agent_contracts: all checks passed'
