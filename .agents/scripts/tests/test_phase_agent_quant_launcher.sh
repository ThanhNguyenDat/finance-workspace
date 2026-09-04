#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
RUNNER="$ROOT_DIR/tools/orchestrator/bin/run-phase-agent-command.sh"; STATE="$ROOT_DIR/tools/orchestrator/bin/agent-role-state.sh"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
workspace="$tmp/workspace"; bin="$tmp/bin"; trace="$tmp/trace"; mkdir -p "$workspace/.agents/scripts" "$workspace/.claude/commands" "$bin" "$trace"
cp "$ROOT_DIR/tools/orchestrator/bin/run-phase-agent-command.sh" "$workspace/.agents/scripts/run-phase-agent-command.sh"; cp "$ROOT_DIR/tools/orchestrator/bin/quant-research-state.sh" "$workspace/.agents/scripts/quant-research-state.sh"; cp "$ROOT_DIR/tools/orchestrator/bin/agent-role-state.sh" "$workspace/.agents/scripts/agent-role-state.sh"; cp "$ROOT_DIR/tools/orchestrator/bin/classify-codex-result.sh" "$workspace/.agents/scripts/classify-codex-result.sh"; cp "$ROOT_DIR/tools/orchestrator/bin/classify-claude-result.sh" "$workspace/.agents/scripts/classify-claude-result.sh"
chmod +x "$workspace/.agents/scripts/"*.sh
printf '%s\n' 'CANONICAL QUANT PROMPT' >"$workspace/.claude/commands/quant-research.md"
git -C "$workspace" init -q; git -C "$workspace" config user.email test@example.invalid; git -C "$workspace" config user.name Test; git -C "$workspace" add .; git -C "$workspace" commit -qm init
cp "$ROOT_DIR/tools/orchestrator/tests/fixtures/fake_claude_sdk_cli.py" "$bin/claude"
cp "$ROOT_DIR/tools/orchestrator/tests/fixtures/fake_codex_sdk_cli.py" "$bin/codex"
chmod +x "$bin/claude" "$bin/codex"
export PATH="$bin:$PATH" TRACE="$trace" FAKE_SDK_TRACE="$trace/sdk.jsonl" CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1 FAKE_CLAUDE_MODE=complete FAKE_CODEX_MODE=complete FAKE_CODEX_RESULT=quota FAKE_SDK_RESULT_TEXT=$'OK\nFINAL_VERIFY_GATE: PASS\nP0_FINDINGS: 0\nP1_FINDINGS: 0\nOBJECTIVE_GATES: PASS' AGENT_ROLE_ROOT="$workspace" QUANT_RESEARCH_ROOT="$workspace" OPS_ROOT="$workspace" OPS_WORKSPACE_ROOT="$workspace" PHASE_AGENT_ACCOUNTS_FILE="$tmp/missing-accounts.yaml" AGENT_ROLE_STATE_DIR="$workspace/.ops/runtime/agent-roles" QUANT_RESEARCH_STATE_DIR="$workspace/.ops/runtime/quant-research" AGENT_ROLE_LEGACY_QUANT_STATE="$tmp/no-quant" AGENT_ROLE_LEGACY_CLAUDE_STATE="$tmp/no-claude"
fail() { printf 'test_phase_agent_quant_launcher: %s\n' "$1" >&2; exit 1; }
# quant_research now resolves codex first (matching implement/fix); codex
# hits quota and claude continues, the reverse of the previous default order.
(cd "$workspace" && ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null
jq -e '.iteration==1' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'iteration incremented more than once'
grep -Fq 'Quant iteration 1 was already recorded' "$trace/sdk.jsonl" || fail 'Codex iteration context missing'
grep -Fq 'Continue quant iteration 1' "$trace/sdk.jsonl" || fail 'Claude continuation context missing'
grep -Fq 'CANONICAL QUANT PROMPT' "$trace/sdk.jsonl" || fail 'canonical prompt missing'
grep -Fq '"type": "user"' "$trace/sdk.jsonl" || fail 'Claude SDK turn missing'
grep -Fq '"method": "turn/start"' "$trace/sdk.jsonl" || fail 'Codex SDK turn missing'
find "$workspace/.ops/runtime/phase-agents/quant-runs" -mindepth 2 -maxdepth 2 -name '*.meta.json' | wc -l | grep -Fqx 2 || { find "$workspace/.ops" -type f -print >&2; fail 'quant attempt evidence missing'; }

set +e; (cd "$workspace" && PHASE_AGENT_QUANT_RESEARCH_PROVIDER=claude PHASE_AGENT_QUANT_RESEARCH_MODEL=opus PHASE_AGENT_QUANT_RESEARCH_EFFORT=low ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; invalid_status=$?; set -e
[[ "$invalid_status" -ne 0 ]] || fail 'invalid quant override was accepted'
jq -e '.iteration==1' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'invalid override changed iteration state'

"$STATE" provider-on claude >/dev/null; "$STATE" provider-off codex >/dev/null
started_marker="$tmp/first-attempt-started"
# The coordinator's admission pool has no per-change exclusivity — it is a
# global capacity gate (DEFAULT_MAX_SESSIONS=2), and each of these two
# concurrent launches creates its OWN new session (the bound session from
# step 1 stays RUNNING forever, never COMPLETED, so it is never resumed).
# With the default capacity of 2 both launches admit successfully and this
# step no longer demonstrates contention. Force capacity to 1 so the second
# launch deterministically finds no free slot, matching what this step
# actually verifies (a launcher respects admission capacity), rather than
# relying on incidental timing that made it merely likely to contend before.
export ORCHESTRATOR_MAX_SESSIONS=1
set +e
(cd "$workspace" && FAKE_CLAUDE_MODE=quota-delay FAKE_SDK_STARTED_MARKER="$started_marker" PHASE_AGENT_QUANT_TIMEOUT_SECONDS=10 ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1 & first_pid=$!
set -e
# Wait for the fake SDK to actually report its turn started (proof the
# first launch's session is admitted and holds the sole slot) instead of
# merely polling for coordinator.db to exist.
for _ in $(seq 1 100); do [[ -f "$started_marker" ]] && break; sleep 0.1; done
[[ -f "$started_marker" ]] || fail 'first attempt never reported its turn started'
set +e; (cd "$workspace" && ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; concurrent_status=$?; wait "$first_pid"; first_status=$?; set -e
unset ORCHESTRATOR_MAX_SESSIONS
[[ "$concurrent_status" -ne 0 ]] || fail 'quota-only concurrent quant launcher unexpectedly completed'
[[ "$first_status" -ne 0 ]] || fail 'quota-only fixture unexpectedly completed'
[[ ! -e "$workspace/.ops/runtime/phase-agents/.quant-research-lock" ]] || fail 'legacy global quant lease remains'
jq -e '.iteration==2' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'concurrent launches changed iteration count'
namespace_count="$(find "$workspace/.ops/runtime/phase-agents/quant-runs" -mindepth 1 -maxdepth 1 -type d | wc -l)"
[[ "$namespace_count" -eq 3 ]] || { find "$workspace/.ops/runtime/phase-agents/quant-runs" -mindepth 1 -maxdepth 1 -type d >&2; fail 'concurrent sessions did not get isolated namespaces'; }

"$STATE" provider-on claude >/dev/null
set +e; (cd "$workspace" && FAKE_CLAUDE_MODE=delay FAKE_SDK_DELAY_SECONDS=2 PHASE_AGENT_QUANT_TIMEOUT_SECONDS=1 ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; status=$?; set -e
[[ "$status" -ne 0 ]] || fail 'SDK timeout did not propagate'
jq -e '.iteration==3' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'timed out iteration count invalid'
printf '%s\n' 'test_phase_agent_quant_launcher: all checks passed'
