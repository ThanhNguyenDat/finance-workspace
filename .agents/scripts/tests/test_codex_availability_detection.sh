#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
DETECTOR="$ROOT_DIR/.agents/scripts/detect-codex-availability.sh"
STATE_HELPER="$ROOT_DIR/.agents/scripts/quant-research-state.sh"
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

cat >"$mock_bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p -- "$FAKE_TRACE_DIR"
count_file="$FAKE_TRACE_DIR/count"
count=0
[[ ! -f "$count_file" ]] || count="$(<"$count_file")"
count="$((count + 1))"
printf '%s\n' "$count" >"$count_file"
printf '%s\n' "$@" >"$FAKE_TRACE_DIR/args-$count"
pwd -P >"$FAKE_TRACE_DIR/cwd-$count"
case "${FAKE_SCENARIO:-success}" in
  success) printf '%s\n' '{"type":"result","status":"completed"}' ;;
  global) printf '%s\n' '{"error":{"code":"insufficient_quota"}}'; exit 7 ;;
  rate-limit) printf '%s\n' '{"error":{"code":"rate_limit_exceeded"}}'; exit 7 ;;
  model-limit) printf '%s\n' '{"error":{"code":"model_capacity_exceeded"}}'; exit 7 ;;
  auth) printf '%s\n' '{"error":{"code":"authentication_error"}}'; exit 7 ;;
  network) printf '%s\n' '{"error":{"code":"network_error"}}'; exit 7 ;;
  timeout) sleep 5 ;;
  *) printf '%s\n' unexpected >&2; exit 7 ;;
esac
MOCK
chmod +x "$mock_bin/codex"

run_state() {
  QUANT_RESEARCH_STATE_DIR="$state_dir" "$STATE_HELPER" "$@"
}
run_detector() {
  PATH="$mock_bin:/usr/bin:/bin" FAKE_TRACE_DIR="$trace_dir" \
    QUANT_RESEARCH_STATE_DIR="$state_dir" CODEX_PROBE_TIMEOUT_SECONDS="${PROBE_TIMEOUT:-2}" \
    "$DETECTOR"
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

test -x "$DETECTOR" || fail 'detector is not executable'
bash -n "$DETECTOR" || fail 'detector syntax is invalid'
run_state codex-auto >/dev/null
run_state profile-set probe probe-model low >/dev/null

test "$(FAKE_SCENARIO=success run_detector)" = available || fail 'successful probe was not available'
run_state state | jq -e '.codex_mode == "auto" and .codex_available == true' >/dev/null \
  || fail 'successful probe did not enable Codex in auto mode'
grep -Fqx -- --dangerously-bypass-approvals-and-sandbox "$trace_dir/args-1" \
  || fail 'probe did not use the supported yolo-equivalent flag'
grep -Fqx -- --skip-git-repo-check "$trace_dir/args-1" \
  || fail 'isolated probe did not bypass the temporary directory Git check'
grep -Fqx -- probe-model "$trace_dir/args-1" || fail 'probe ignored probe model profile'
grep -Fqx -- 'model_reasoning_effort="low"' "$trace_dir/args-1" || fail 'probe ignored probe effort profile'
test "$(cat -- "$trace_dir/cwd-1")" != "$ROOT_DIR" || fail 'probe ran inside the repository'

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
missing_output="$(PATH="/usr/bin:/bin" QUANT_RESEARCH_STATE_DIR="$state_dir" "$DETECTOR")"
missing_status=$?
set -e
[[ "$missing_status" -eq 3 && "$missing_output" = inconclusive:missing-codex ]] \
  || fail 'missing Codex was not safely inconclusive'

printf '%s\n' 'test_codex_availability_detection: all checks passed'
