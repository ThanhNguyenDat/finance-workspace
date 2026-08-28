#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
STATE_HELPER="$ROOT_DIR/.agents/scripts/quant-research-state.sh"
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
  .schema_version == 1 and
  .codex_available == true and
  .research_enabled == true and
  .iteration == 0 and
  .last_run_at == null and
  .updated_at == null
' >/dev/null || fail 'init did not create the expected defaults'

run_state codex-off | jq -e '.codex_available == false and (.updated_at | type) == "string"' >/dev/null \
  || fail 'codex-off did not update availability atomically'
run_state codex-on | jq -e '.codex_available == true and (.updated_at | type) == "string"' >/dev/null \
  || fail 'codex-on did not update availability atomically'

run_state begin-iteration | jq -e '.iteration == 1 and (.last_run_at | type) == "string"' >/dev/null \
  || fail 'begin-iteration did not record exactly one iteration'
run_state begin-iteration | jq -e '.iteration == 2' >/dev/null \
  || fail 'second iteration did not increment once'

state_file="$state_dir/state.json"
valid_state="$(cat -- "$state_file")"
printf '%s\n' '{"schema_version":1,"codex_available":"bad"}' >"$state_file"
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
