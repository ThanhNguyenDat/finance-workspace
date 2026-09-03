#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
STATE_HELPER="$ROOT_DIR/tools/phase-agent-orchestrator/bin/quant-research-state.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_quant_research_state: %s\n' "$1" >&2
  exit 1
}

expect_failure() {
  if "$@"; then
    fail "expected command to fail: $*"
  fi
}

state_dir="$tmp/state"
run_state() {
  QUANT_RESEARCH_STATE_DIR="$state_dir" "$STATE_HELPER" "$@"
}

test -x "$STATE_HELPER" || fail 'state helper is not executable'
bash -n "$STATE_HELPER" || fail 'state helper syntax is invalid'

initial="$(run_state init)"
printf '%s\n' "$initial" | jq -e '
  .schema_version == 2 and
  .codex_mode == "manual" and
  .codex_available == true and
  .codex_profiles == {
    probe: {model: "gpt-5.6-luna", effort: "high"},
    implement: {model: "gpt-5.6-luna", effort: "high"},
    fix: {model: "gpt-5.6-terra", effort: "high"},
    fix_fallback: {model: "gpt-5.6-sol", effort: "high"}
  } and
  .research_enabled == true and .iteration == 0 and
  .last_run_at == null and .updated_at == null
' >/dev/null || fail 'init did not create schema-v2 defaults'

run_state codex-auto | jq -e '.codex_mode == "auto" and .codex_available == true' >/dev/null \
  || fail 'codex-auto did not preserve resolved availability'
run_state codex-detected-off | jq -e '.codex_mode == "auto" and .codex_available == false' >/dev/null \
  || fail 'detected-off did not preserve auto mode'
run_state codex-manual | jq -e '.codex_mode == "manual" and .codex_available == false' >/dev/null \
  || fail 'codex-manual changed resolved availability'
expect_failure run_state codex-detected-on
run_state codex-on | jq -e '.codex_mode == "manual" and .codex_available == true' >/dev/null \
  || fail 'codex-on did not become a manual override'
run_state codex-auto >/dev/null
run_state codex-worker-off | jq -e '.codex_mode == "auto" and .codex_available == false' >/dev/null \
  || fail 'worker quota update did not preserve auto mode'
run_state codex-off | jq -e '.codex_mode == "manual" and .codex_available == false' >/dev/null \
  || fail 'codex-off did not become a manual override'

before_profiles="$(run_state state | jq -c '.codex_profiles')"
test "$(run_state profile-set implement custom-implement medium)" = $'custom-implement\tmedium' \
  || fail 'implement profile update output is incorrect'
run_state state | jq -e '
  .codex_profiles.implement == {model:"custom-implement", effort:"medium"} and
  .codex_profiles.fix == {model:"gpt-5.6-terra", effort:"high"} and
  .codex_mode == "manual" and .codex_available == false
' >/dev/null || fail 'profile update changed an unrelated field'
profile_state="$(run_state state)"
expect_failure run_state profile-set review forbidden high
expect_failure run_state profile-set fix 'bad model' high
expect_failure run_state profile-set fix safe-model extreme
test "$(run_state state)" = "$profile_state" || fail 'invalid profile input mutated state'
test "$(run_state profile-reset implement)" = $'gpt-5.6-luna\thigh' \
  || fail 'single profile reset did not restore its default'
run_state profile-set probe probe-model low >/dev/null
run_state profiles-reset | jq -e --argjson expected "$before_profiles" '.codex_profiles == $expected' >/dev/null \
  || fail 'reset-all did not restore every default profile'

run_state begin-iteration | jq -e '.iteration == 1 and (.last_run_at | type) == "string"' >/dev/null \
  || fail 'begin-iteration did not record exactly one iteration'
run_state begin-iteration | jq -e '.iteration == 2' >/dev/null \
  || fail 'second iteration did not increment once'

state_file="$state_dir/state.json"
printf '%s\n' '{"schema_version":1,"codex_available":false,"research_enabled":true,"iteration":7,"last_run_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-02T00:00:00Z"}' >"$state_file"
run_state state | jq -e '
  .schema_version == 2 and .codex_mode == "manual" and
  .codex_available == false and .iteration == 7 and
  .last_run_at == "2026-01-01T00:00:00Z" and
  .updated_at == "2026-01-02T00:00:00Z" and
  .codex_profiles.fix_fallback.model == "gpt-5.6-sol"
' >/dev/null || fail 'valid v1 state did not migrate atomically'

valid_state="$(cat -- "$state_file")"
printf '%s\n' '{"schema_version":2,"codex_available":"bad"}' >"$state_file"
before="$(sha256sum "$state_file" | awk '{print $1}')"
expect_failure run_state codex-off
after="$(sha256sum "$state_file" | awk '{print $1}')"
test "$before" = "$after" || fail 'malformed state was overwritten'
printf '%s\n' "$valid_state" >"$state_file"

mkdir -p "$state_dir/.lock"
printf '%s\n' "$$" >"$state_dir/.lock/pid"
expect_failure run_state codex-on
rm -rf -- "$state_dir/.lock"

mkdir -p "$state_dir/.lock"
printf '%s\n' '999999999' >"$state_dir/.lock/pid"
run_state init >/dev/null || fail 'stale state lock was not recovered'

printf '%s\n' 'test_quant_research_state: all checks passed'
