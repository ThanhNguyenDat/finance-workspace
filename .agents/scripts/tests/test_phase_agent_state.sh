#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
STATE="$ROOT_DIR/tools/phase-agent-orchestrator/bin/phase-agent-state.sh"
CONFIG="$ROOT_DIR/tools/phase-agent-orchestrator/bin/configure-phase-agents.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
export PHASE_AGENT_STATE_DIR="$tmp/state"
export PHASE_AGENT_LEGACY_QUANT_STATE="$tmp/quant.json"
export PHASE_AGENT_LEGACY_CLAUDE_STATE="$tmp/claude.json"
export PHASE_AGENT_ACCOUNTS_FILE="$tmp/missing-accounts.yaml"
fail() { printf 'test_phase_agent_state: %s\n' "$1" >&2; exit 1; }

printf '%s\n' '{"schema_version":2,"codex_available":false,"codex_profiles":{"implement":{"model":"codex-i","effort":"high"},"fix":{"model":"codex-f","effort":"high"},"fix_fallback":{"model":"codex-ff","effort":"medium"}}}' >"$PHASE_AGENT_LEGACY_QUANT_STATE"
printf '%s\n' '{"profiles":{"quant_research":{"model":"sonnet","effort":"high"},"plan":{"model":"opus","effort":"medium"},"fallback_implement":{"model":"sonnet","effort":"high"},"verify":{"model":"opus","effort":"medium"},"fallback_fix":{"model":"opus","effort":"high"},"final_verify":{"model":"opus","effort":"high"}}}' >"$PHASE_AGENT_LEGACY_CLAUDE_STATE"

initial="$(orchestrator phase-agent-state init)"
jq -e '.legacy_imported and (.providers.codex.available|not) and .phases.implement.candidates[0].model=="codex-i" and .phases.plan.candidates[0].effort=="medium"' <<<"$initial" >/dev/null || fail 'legacy/default migration failed'
before_verify="$(jq -c '.phases.verify' <<<"$initial")"
orchestrator phase-agent-state set implement claude sonnet medium >/dev/null
after="$(orchestrator phase-agent-state state)"
[[ "$(jq -c '.phases.verify' <<<"$after")" = "$before_verify" ]] || fail 'phase isolation failed'
[[ "$(orchestrator phase-agent-state resolve implement)" == $'claude\tsonnet\tmedium' ]] || fail 'set/resolve failed'

cp "$PHASE_AGENT_STATE_DIR/state.json" "$tmp/good.json"
if $STATE set plan claude opus low >/dev/null 2>&1; then fail 'invalid Opus effort accepted'; fi
cmp -s "$tmp/good.json" "$PHASE_AGENT_STATE_DIR/state.json" || fail 'invalid input changed state'

$STATE provider-on codex >/dev/null
$STATE pin implement codex >/dev/null
[[ "$($STATE resolve implement)" == $'codex\tcodex-i\thigh' ]] || fail 'manual pin failed'
$STATE provider-off codex quota >/dev/null
[[ -z "$($STATE resolve implement)" ]] || fail 'disabled pinned provider resolved'
$STATE auto implement >/dev/null
[[ "$($STATE resolve implement)" == $'claude\tsonnet\tmedium' ]] || fail 'phase auto failed'
$STATE provider-auto codex >/dev/null
$STATE provider-result codex global-quota-exhausted 0 >/dev/null
$STATE probe-due codex || fail 'quota cooldown did not become probe eligible'
$STATE provider-result codex success >/dev/null
jq -e '.providers.codex.available and .providers.codex.reason==null' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'provider recovery failed'

output="$(PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" show)"
grep -Fq 'quant_research' <<<"$output" || fail 'safe show lacks phases'
if grep -Fq 'schema_version' <<<"$output"; then fail 'safe show exposed raw JSON'; fi
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" set verify codex configured-model high >/dev/null
jq -e '.phases.verify.candidates[0].provider=="codex" and .phases.verify.candidates[0].model=="configured-model"' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'config set failed'
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" candidate-set fix 1 codex backup-model medium >/dev/null
jq -e '.phases.fix.candidates[1].model=="backup-model"' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'config candidate-set failed'
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" pin verify codex >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" auto verify >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" provider-off claude >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" provider-on claude >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" provider-manual claude >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" provider-auto claude >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" reset verify >/dev/null
PHASE_AGENT_STATE_HELPER="$STATE" "$CONFIG" reset-all >/dev/null
jq -e '.legacy_imported and .providers.codex.available and .phases.implement.candidates[0].model=="gpt-5.6-luna"' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'reset-all re-imported legacy state'
if $STATE validate claude opus low >/dev/null 2>&1; then fail 'public validation accepted invalid Opus effort'; fi
$STATE validate codex safe-model high >/dev/null || fail 'public validation rejected a valid candidate'

printf '%s\n' '{bad json' >"$PHASE_AGENT_STATE_DIR/state.json"
if $STATE state >/dev/null 2>&1; then fail 'malformed state accepted'; fi
grep -Fq '{bad json' "$PHASE_AGENT_STATE_DIR/state.json" || fail 'malformed state overwritten'
cp "$tmp/good.json" "$PHASE_AGENT_STATE_DIR/state.json"

mkdir "$PHASE_AGENT_STATE_DIR/.lock"
printf '%s\n' "$$" >"$PHASE_AGENT_STATE_DIR/.lock/pid"
if $STATE reset plan >/dev/null 2>&1; then fail 'live lock ignored'; fi
rm -rf -- "$PHASE_AGENT_STATE_DIR/.lock"
$STATE reset plan >/dev/null
[[ "$($STATE resolve plan)" == $'claude\topus\tmedium' ]] || fail 'phase reset failed'
$STATE reset-all >/dev/null
jq -e '.legacy_imported and (.phases|length==6)' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'reset-all failed'

printf '%s\n' 'test_phase_agent_state: all checks passed'
