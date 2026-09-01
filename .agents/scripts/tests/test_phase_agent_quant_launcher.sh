#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
RUNNER="$ROOT_DIR/.agents/scripts/run-phase-agent-command.sh"; STATE="$ROOT_DIR/.agents/scripts/phase-agent-state.sh"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
workspace="$tmp/workspace"; bin="$tmp/bin"; trace="$tmp/trace"; mkdir -p "$workspace/.agents/scripts" "$workspace/.claude/commands" "$bin" "$trace"
cp "$RUNNER" "$workspace/.agents/scripts/run-phase-agent-command.sh"; cp "$ROOT_DIR/.agents/scripts/quant-research-state.sh" "$workspace/.agents/scripts/quant-research-state.sh"; cp "$ROOT_DIR/.agents/scripts/phase-agent-state.sh" "$workspace/.agents/scripts/phase-agent-state.sh"; cp "$ROOT_DIR/.agents/scripts/classify-codex-result.sh" "$workspace/.agents/scripts/classify-codex-result.sh"; cp "$ROOT_DIR/.agents/scripts/classify-claude-result.sh" "$workspace/.agents/scripts/classify-claude-result.sh"
chmod +x "$workspace/.agents/scripts/"*.sh
printf '%s\n' 'CANONICAL QUANT PROMPT' >"$workspace/.claude/commands/quant-research.md"
git -C "$workspace" init -q; git -C "$workspace" config user.email test@example.invalid; git -C "$workspace" config user.name Test; git -C "$workspace" add .; git -C "$workspace" commit -qm init
printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" "$@" >"$TRACE/claude.args"; cat >"$TRACE/claude.prompt"' 'if [[ "${FAKE_CLAUDE_MODE:-quota}" = sleep ]]; then sleep 5; fi' 'printf "%s\n" '\''{"error":{"code":"global_quota_exhausted"}}'\'' >&2; exit 1' >"$bin/claude"
printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" "$@" >"$TRACE/codex.args"; cat >"$TRACE/codex.prompt"; printf "%s\n" '\''{"type":"result","result":"OK"}'\''' >"$bin/codex"
chmod +x "$bin/claude" "$bin/codex"
export PATH="$bin:$PATH" TRACE="$trace" PHASE_AGENT_STATE_DIR="$workspace/.ops/runtime/phase-agents" QUANT_RESEARCH_STATE_DIR="$workspace/.ops/runtime/quant-research" PHASE_AGENT_LEGACY_QUANT_STATE="$tmp/no-quant" PHASE_AGENT_LEGACY_CLAUDE_STATE="$tmp/no-claude"
fail() { printf 'test_phase_agent_quant_launcher: %s\n' "$1" >&2; exit 1; }
(cd "$workspace" && ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null
jq -e '.iteration==1' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'iteration incremented more than once'
grep -Fq 'Quant iteration 1 was already recorded' "$trace/claude.prompt" || fail 'Claude iteration context missing'
grep -Fq 'Continue quant iteration 1' "$trace/codex.prompt" || fail 'Codex continuation context missing'
grep -Fq 'CANONICAL QUANT PROMPT' "$trace/codex.prompt" || fail 'canonical prompt missing'
grep -Fqx -- --dangerously-skip-permissions "$trace/claude.args" || fail 'Claude bypass missing'
grep -Fqx -- --verbose "$trace/claude.args" || fail 'Claude stream-json verbose flag missing'
grep -Fqx -- --dangerously-bypass-approvals-and-sandbox "$trace/codex.args" || fail 'Codex bypass missing'
find "$workspace/.ops/runtime/phase-agents/quant-runs/iteration-1" -name '*.meta.json' | wc -l | grep -Fqx 2 || fail 'quant attempt evidence missing'

set +e; (cd "$workspace" && PHASE_AGENT_QUANT_RESEARCH_PROVIDER=claude PHASE_AGENT_QUANT_RESEARCH_MODEL=opus PHASE_AGENT_QUANT_RESEARCH_EFFORT=low ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; invalid_status=$?; set -e
[[ "$invalid_status" -ne 0 ]] || fail 'invalid quant override was accepted'
jq -e '.iteration==1' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'invalid override changed iteration state'

"$STATE" provider-on claude >/dev/null; "$STATE" provider-off codex >/dev/null
set +e
(cd "$workspace" && FAKE_CLAUDE_MODE=sleep PHASE_AGENT_QUANT_TIMEOUT_SECONDS=10 ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1 & first_pid=$!
set -e
for _ in $(seq 1 50); do [[ -f "$workspace/.ops/runtime/phase-agents/.quant-research-lock/pid" ]] && break; sleep 0.1; done
[[ -f "$workspace/.ops/runtime/phase-agents/.quant-research-lock/pid" ]] || fail 'quant lease was not acquired'
set +e; (cd "$workspace" && ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; concurrent_status=$?; wait "$first_pid"; first_status=$?; set -e
[[ "$concurrent_status" -ne 0 ]] || fail 'concurrent quant launcher was accepted'
[[ "$first_status" -ne 0 ]] || fail 'quota-only fixture unexpectedly completed'
jq -e '.iteration==2' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'concurrent launch changed iteration count'

"$STATE" provider-on claude >/dev/null
set +e; (cd "$workspace" && FAKE_CLAUDE_MODE=sleep PHASE_AGENT_QUANT_TIMEOUT_SECONDS=1 ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null 2>&1; status=$?; set -e
[[ "$status" -eq 124 ]] || fail 'quant hard timeout did not propagate'
jq -e '.iteration==3' "$QUANT_RESEARCH_STATE_DIR/state.json" >/dev/null || fail 'timed out iteration count invalid'
printf '%s\n' 'test_phase_agent_quant_launcher: all checks passed'
