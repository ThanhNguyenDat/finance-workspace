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
run_runtime cleanup quant-fallback session-quant-fallback FAILED

run_quant codex-on >/dev/null
init_change normal-after-toggle
run_runtime state normal-after-toggle | jq -e '.implementation_backend == "codex"' >/dev/null \
  || fail 'new transaction did not observe the normal Codex default'
run_runtime cleanup normal-after-toggle session-normal-after-toggle FAILED

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

printf 'test_quant_backend_routing: all checks passed\n'
