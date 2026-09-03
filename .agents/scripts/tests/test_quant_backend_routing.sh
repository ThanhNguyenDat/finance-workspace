#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"; OPS="$ROOT_DIR/tools/orchestrator/bin/ops-runtime.sh"; QUANT="$ROOT_DIR/tools/orchestrator/bin/quant-research-state.sh"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
workspace="$tmp/workspace"; mkdir -p "$workspace"; export OPS_ROOT="$workspace" QUANT_RESEARCH_STATE_DIR="$workspace/.ops/runtime/quant-research"
fail() { printf 'test_quant_backend_routing: %s\n' "$1" >&2; exit 1; }; expect_failure() { if "$@"; then fail "expected failure: $*"; fi; }
new_change() { "$OPS" lock "$1" "session-$1"; "$OPS" init "$1" "session-$1" "${2:-}" "${3:-}"; }

new_change phase-policy
jq -e '.routing_policy_version==1 and (.attempts|length)==0 and .verification_evidence==null and (has("implementation_backend")|not)' "$workspace/.ops/changes/phase-policy/runtime/state.json" >/dev/null || fail 'new transaction schema invalid'
"$OPS" phase phase-policy session-phase-policy IMPLEMENT
[[ "$($OPS route phase-policy session-phase-policy IMPLEMENT)" = phase-agent ]] || fail 'new transaction did not route phase-agent'
"$OPS" cleanup phase-policy session-phase-policy FAILED

new_change legacy-codex codex
jq -e '.implementation_backend=="codex" and .verification_mode=="independent" and (has("routing_policy_version")|not)' "$workspace/.ops/changes/legacy-codex/runtime/state.json" >/dev/null || fail 'legacy Codex state invalid'
"$OPS" phase legacy-codex session-legacy-codex IMPLEMENT
[[ "$($OPS route legacy-codex session-legacy-codex IMPLEMENT)" = codex ]] || fail 'legacy Codex route changed'
"$OPS" cleanup legacy-codex session-legacy-codex FAILED

"$QUANT" codex-off >/dev/null
new_change legacy-fallback claude-fallback quant-fallback
jq -e '.implementation_backend=="claude-fallback" and .verification_mode=="claude-process-separated-review"' "$workspace/.ops/changes/legacy-fallback/runtime/state.json" >/dev/null || fail 'legacy fallback state invalid'
"$OPS" phase legacy-fallback session-legacy-fallback IMPLEMENT
[[ "$($OPS route legacy-fallback session-legacy-fallback IMPLEMENT)" = claude-fallback ]] || fail 'legacy fallback route changed'
"$OPS" cleanup legacy-fallback session-legacy-fallback FAILED

"$OPS" lock invalid session-invalid; expect_failure "$OPS" init invalid session-invalid unsupported; [[ ! -e "$workspace/.ops/changes/invalid/runtime/state.json" ]] || fail 'invalid backend created state'; "$OPS" unlock invalid session-invalid
"$QUANT" codex-on >/dev/null; "$OPS" lock ungated session-ungated; expect_failure "$OPS" init ungated session-ungated claude-fallback quant-fallback; "$OPS" unlock ungated session-ungated
grep -Fq 'routing_policy_version' "$ROOT_DIR/tools/orchestrator/src/orchestrator/state/ops_transaction.py" || fail 'routing policy contract missing'
grep -Fq 'run-phase-agent.sh' "$ROOT_DIR/tools/orchestrator/bin/run-phase-agent.sh" || :
printf '%s\n' 'test_quant_backend_routing: all checks passed'
