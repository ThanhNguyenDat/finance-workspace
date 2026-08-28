#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.sh"
QUANT_STATE="$ROOT_DIR/.agents/scripts/quant-research-state.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_quant_backend_routing: %s\n' "$1" >&2
  exit 1
}

expect_failure() {
  if "$@"; then
    fail "expected command to fail: $*"
  fi
}

contains() {
  local pattern="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -q "$pattern" "$file"
  else
    grep -Eq "$pattern" "$file"
  fi
}

contains_i() {
  local pattern="$1"
  local file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -qi "$pattern" "$file"
  else
    grep -Eqi "$pattern" "$file"
  fi
}

contains_normalized_i() {
  local pattern="$1"
  local file="$2"
  tr '\n' ' ' <"$file" | grep -Eqi "$pattern"
}

workspace="$tmp/workspace"
state_dir="$workspace/.ops/runtime/quant-research"
mkdir -p -- "$workspace/.ops/changes" "$state_dir"

run_runtime() {
  OPS_ROOT="$workspace" "$RUNTIME" "$@"
}

run_quant() {
  QUANT_RESEARCH_STATE_DIR="$state_dir" "$QUANT_STATE" "$@"
}

init_change() {
  local change="$1"
  run_runtime lock "$change" "session-$change"
  run_runtime init "$change" "session-$change" "${@:2}"
}

lock_change() {
  local change="$1"
  run_runtime lock "$change" "session-$change"
}

init_change normal-default
run_runtime state normal-default | jq -e '
  .implementation_backend == "codex" and
  .verification_mode == "independent"
' >/dev/null || fail 'normal transaction did not persist Codex defaults'
run_runtime phase normal-default session-normal-default IMPLEMENT
test "$(run_runtime route normal-default session-normal-default IMPLEMENT)" = codex \
  || fail 'normal IMPLEMENT did not route to Codex'
run_runtime cleanup normal-default session-normal-default FAILED

run_quant init >/dev/null
run_quant codex-off >/dev/null
init_change quant-fallback claude-fallback quant-fallback
run_runtime state quant-fallback | jq -e '
  .implementation_backend == "claude-fallback" and
  .verification_mode == "claude-fallback-self-review"
' >/dev/null || fail 'fallback transaction did not persist fallback fields'
run_runtime phase quant-fallback session-quant-fallback IMPLEMENT
test "$(run_runtime route quant-fallback session-quant-fallback IMPLEMENT)" = claude-fallback \
  || fail 'fallback IMPLEMENT did not route to the current Claude session'
run_runtime phase quant-fallback session-quant-fallback VERIFY
run_quant codex-on >/dev/null
run_runtime fix quant-fallback session-quant-fallback
test "$(run_runtime route quant-fallback session-quant-fallback FIX)" = claude-fallback \
  || fail 'fallback FIX changed after Codex was re-enabled'
run_runtime phase quant-fallback session-quant-fallback VERIFY
run_runtime phase quant-fallback session-quant-fallback FINAL_VERIFY
run_runtime state quant-fallback | jq -e '
  .phase == "FINAL_VERIFY" and
  .implementation_backend == "claude-fallback" and
  .verification_mode == "claude-fallback-self-review"
' >/dev/null || fail 'fallback verification pair changed before FINAL_VERIFY'
run_runtime cleanup quant-fallback session-quant-fallback FAILED

run_quant codex-on >/dev/null
init_change normal-after-toggle
run_runtime state normal-after-toggle | jq -e '.implementation_backend == "codex"' >/dev/null \
  || fail 'new transaction did not observe the normal Codex default'
run_runtime cleanup normal-after-toggle session-normal-after-toggle FAILED

init_change invalid-pair
pair_state="$workspace/.ops/changes/invalid-pair/runtime/state.json"
jq '.verification_mode = "claude-fallback-self-review"' "$pair_state" >"$pair_state.tmp"
mv -- "$pair_state.tmp" "$pair_state"
expect_failure run_runtime phase invalid-pair session-invalid-pair IMPLEMENT
jq '.verification_mode = "independent"' "$pair_state" >"$pair_state.tmp"
mv -- "$pair_state.tmp" "$pair_state"
run_runtime cleanup invalid-pair session-invalid-pair FAILED

lock_change invalid-backend
expect_failure run_runtime init invalid-backend session-invalid-backend unsupported
test ! -e "$workspace/.ops/changes/invalid-backend/runtime/state.json" \
  || fail 'invalid backend created runtime state'
run_runtime unlock invalid-backend session-invalid-backend

lock_change ungated-fallback
expect_failure run_runtime init ungated-fallback session-ungated-fallback claude-fallback
test ! -e "$workspace/.ops/changes/ungated-fallback/runtime/state.json" \
  || fail 'ungated fallback created runtime state'
run_runtime unlock ungated-fallback session-ungated-fallback

run_quant codex-on >/dev/null
lock_change unavailable-fallback
expect_failure run_runtime init unavailable-fallback session-unavailable-fallback claude-fallback quant-fallback
test ! -e "$workspace/.ops/changes/unavailable-fallback/runtime/state.json" \
  || fail 'fallback was accepted while Codex was available'
run_runtime unlock unavailable-fallback session-unavailable-fallback

runner="$ROOT_DIR/.agents/scripts/run-codex-phase.sh"
run_command="$ROOT_DIR/.claude/commands/ops/run.md"
contains 'implementation_backend="\$\(jq -r' "$runner" \
  || fail 'Codex runner does not read persisted backend'
contains 'Codex worker is not selected' "$runner" \
  || fail 'Codex runner has no backend guard'
contains 'Modify only files required by the approved OpenSpec' "$runner" \
  || fail 'Codex runner prompt is not generic'
if contains_i 'documentation-only|developer documentation file|finance-mw|smoke test' "$runner"; then
  fail 'Codex runner still contains smoke-specific wording'
fi
contains 'ops-runtime.sh route <change> <session-id> IMPLEMENT' "$run_command" \
  || fail 'ops run does not route IMPLEMENT from persisted state'
contains 'ops-runtime.sh route <change> <session-id> FIX' "$run_command" \
  || fail 'ops run does not route FIX from persisted state'
contains 'never use a later setter or re-read quant state' "$run_command" \
  || fail 'ops run does not document backend immutability'
contains 'Do not invoke `claude`, `claude -p`,' "$run_command" \
  || fail 'fallback route does not prohibit nested Claude'
contains 'For `verification_mode=independent`' "$run_command" \
  || fail 'Codex final verification mode is not explicit'
contains 'Release is allowed only after this independent final' "$run_command" \
  || fail 'Codex path no longer requires independent final verification'
contains 'For `verification_mode=claude-fallback-self-review`' "$run_command" \
  || fail 'fallback final verification mode is not explicit'
contains 'performs enhanced final self-review' "$run_command" \
  || fail 'fallback path does not require enhanced final self-review'
contains 'applicable objective evidence passes' "$run_command" \
  || fail 'fallback path has no objective evidence release gate'
contains 'independent maker/checker verification: NOT AVAILABLE' "$run_command" \
  || fail 'fallback path does not disclose unavailable independent review'
if contains_normalized_i 'Never push or deploy before[[:space:]]+independent final verification' "$run_command"; then
  fail 'ops run restored the unconditional independent-only push gate'
fi
if contains_normalized_i 'Do not claim completion unless.{0,240}independent verification' "$run_command"; then
  fail 'ops run restored the unconditional independent-only completion gate'
fi

active_smoke="$ROOT_DIR/.ops/changes/finance-mw-dev-docs-smoke/handoff.md"
archived_smoke="$ROOT_DIR/.ops/archive/2026-08-28-finance-mw-dev-docs-smoke/handoff.md"
test ! -e "$active_smoke" || fail 'terminal smoke handoff remains active'
test -f "$archived_smoke" || fail 'terminal smoke handoff was not archived'
contains 'Smoke result: FAILED' "$archived_smoke" \
  || fail 'archived smoke handoff lost FAILED status'
contains 'exited 124 after the bounded 900-second worker timeout' "$archived_smoke" \
  || fail 'archived smoke handoff lost timeout evidence'
contains 'change and finance-mw repository locks are absent' "$archived_smoke" \
  || fail 'archived smoke handoff lost lock-cleanup evidence'
contains 'Production deployment: not performed' "$archived_smoke" \
  || fail 'archived smoke handoff lost deployment evidence'

printf 'test_quant_backend_routing: all checks passed\n'
