#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

ROOT_DIR="$HERMETIC_ROOT_DIR"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_codex_availability_detection: %s\n' "$1" >&2
  exit 1
}

state_dir="$tmp/state"
mock_bin="$tmp/bin"
trace_dir="$tmp/trace"
mkdir -p -- "$mock_bin" "$trace_dir"
cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_codex_sdk_cli.py" "$mock_bin/codex"
chmod +x "$mock_bin/codex"

run_state() {
  QUANT_RESEARCH_STATE_DIR="$state_dir" orchestrator quant-research-state "$@"
}
run_detector() {
  local scenario="${FAKE_SCENARIO:-success}" result="" mode=""
  case "$scenario" in
    success) result=success; mode=complete ;;
    global) result=quota ;;
    rate-limit) result=rate ;;
    model-limit) result=model-limit ;;
    auth) result=auth ;;
    network) result=network ;;
    timeout) mode=hang ;;
    *) result=unknown ;;
  esac
  PATH="$mock_bin:/usr/bin:/bin" FAKE_RESULT="$result" FAKE_SDK_MODE="$mode" \
    QUANT_RESEARCH_STATE_DIR="$state_dir" CODEX_PROBE_TIMEOUT_SECONDS="${PROBE_TIMEOUT:-2}" \
    orchestrator detect-codex-availability
}
expect_inconclusive() {
  local expected="$1" output status
  set +e
  output="$(FAKE_SCENARIO="$2" run_detector)"
  status=$?
  set -e
  [[ "$status" -eq 3 && "$output" = "inconclusive:$expected" ]] \
    || fail "expected inconclusive:$expected, got status=$status output=$output"
}

run_state codex-auto >/dev/null
run_state profile-set probe probe-model low >/dev/null

test "$(FAKE_SCENARIO=success run_detector)" = available || fail 'successful probe was not available'
run_state state | jq -e '.codex_mode == "auto" and .codex_available == true' >/dev/null \
  || fail 'successful probe did not enable Codex in auto mode'
test -f "$state_dir/state.json" || fail 'probe did not persist state through SDK path'

test "$(FAKE_SCENARIO=global run_detector)" = unavailable || fail 'global quota was not conclusive'
run_state state | jq -e '.codex_mode == "auto" and .codex_available == false' >/dev/null \
  || fail 'global quota did not disable Codex while preserving auto mode'

for case_name in rate-limit model-limit auth network unknown; do
  expected="$case_name"
  [[ "$case_name" != rate-limit ]] || expected=transient-rate-limit
  [[ "$case_name" != model-limit ]] || expected=model-specific-limit
  [[ "$case_name" != auth ]] || expected=auth-error
  [[ "$case_name" != network ]] || expected=network-error
  [[ "$case_name" != unknown ]] || expected=unknown-error
  expect_inconclusive "$expected" "$case_name"
  run_state state | jq -e '.codex_mode == "auto" and .codex_available == false' >/dev/null \
    || fail "$case_name probe changed the last resolved value"
done

PROBE_TIMEOUT=1 expect_inconclusive timeout timeout
run_state state | jq -e '.codex_available == false' >/dev/null \
  || fail 'timeout changed availability'

set +e
missing_output="$(PATH="/usr/bin:/bin" QUANT_RESEARCH_STATE_DIR="$state_dir" orchestrator detect-codex-availability)"
missing_status=$?
set -e
[[ "$missing_status" -eq 3 && "$missing_output" = inconclusive:missing-codex ]] \
  || fail 'missing Codex was not safely inconclusive'

printf '%s\n' 'test_codex_availability_detection: all checks passed'
