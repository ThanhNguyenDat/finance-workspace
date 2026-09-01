#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.sh"
RUNNER="$ROOT_DIR/.agents/scripts/run-codex-phase.sh"
CLASSIFIER="$ROOT_DIR/.agents/scripts/classify-codex-result.sh"
QUANT="$ROOT_DIR/.agents/scripts/quant-research-state.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_codex_worker_policy: %s\n' "$1" >&2
  exit 1
}
expect_failure() {
  if "$@"; then
    fail "expected command to fail: $*"
  fi
}
assert_file_contains() {
  grep -Fq -- "$2" "$1" || fail "$3"
}
assert_no_second_attempt() {
  test ! -e "$1/call-2.args" || fail "$2"
}

classifier_case() {
  local name="$1" status="$2" json="$3" stderr="$4" expected="$5"
  local out="$tmp/classifier-$name.stdout" err="$tmp/classifier-$name.stderr"
  printf '%s\n' "$json" >"$out"
  printf '%s\n' "$stderr" >"$err"
  test "$("$CLASSIFIER" "$status" "$out" "$err")" = "$expected" \
    || fail "classifier case $name did not return $expected"
}

classifier_case success 0 '{}' '' success
classifier_case global 7 '{"error":{"code":"insufficient_quota","message":"429 rate limit"}}' '' global-quota-exhausted
classifier_case global-type 7 '{"error":{"type":"quota_exhausted","message":"429 rate limit"}}' '' global-quota-exhausted
classifier_case global-stderr-json 7 '{}' '{"error":{"category":"usage_limit_reached"}}' global-quota-exhausted
classifier_case model-unavailable 7 '{"error":{"code":"model_unavailable"}}' '' model-unavailable
classifier_case model-limit 7 '{"error":{"category":"model_capacity_exceeded"}}' '' model-specific-limit
classifier_case rate-limit 7 '{"error":{"code":"rate_limit_exceeded","message":"HTTP 429"}}' '' transient-rate-limit
classifier_case auth 7 '{"error":{"code":"authentication_error"}}' '' auth-error
classifier_case network 7 '{"error":{"code":"network_error"}}' '' network-error
classifier_case timeout 124 '{}' '' timeout
classifier_case implementation 7 '{"error":{"code":"implementation_error"}}' '' implementation-error
classifier_case unknown 7 '{}' 'unexpected provider failure' unknown-error
classifier_case explicit-quota-text 7 '{}' 'Account-wide Codex quota is exhausted.' global-quota-exhausted
classifier_case usage-limit-text 7 '{}' 'Usage limit exhausted for this account.' global-quota-exhausted
classifier_case session-cap-text 7 '{}' 'Session usage cap reached.' global-quota-exhausted

fixture="$tmp/fixture"
workspace="$fixture/finance-workspace"
repository="$fixture/finance-web"
mock_bin="$tmp/mock-bin"
mkdir -p -- "$workspace" "$repository" "$mock_bin"
for repo in "$workspace" "$repository"; do
  git -C "$repo" init -q
  git -C "$repo" config user.email test@example.invalid
  git -C "$repo" config user.name worker-policy-test
  printf '%s\n' fixture >"$repo/README.md"
  git -C "$repo" add README.md
  git -C "$repo" commit -qm fixture
done

cat >"$mock_bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p -- "$FAKE_TRACE_DIR"
counter="$FAKE_TRACE_DIR/counter"
if [ -f "$counter" ]; then
  call="$(( $(<"$counter") + 1 ))"
else
  call=1
fi
printf '%s\n' "$call" >"$counter"
printf '%s\n' "$@" >"$FAKE_TRACE_DIR/call-$call.args"
prompt="$(cat)"
printf '%s\n' "$prompt" >"$FAKE_TRACE_DIR/call-$call.prompt"
model=''
last_message=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    --model) model="$2"; shift 2 ;;
    --output-last-message) last_message="$2"; shift 2 ;;
    *) shift ;;
  esac
done
printf '%s\n' "$model" >"$FAKE_TRACE_DIR/call-$call.model"

emit_error() {
  printf '{"type":"error","error":{"code":"%s"}}\n' "$1"
  exit "${2:-7}"
}
case "${FAKE_SCENARIO:-success}:$model" in
  implement-unavailable:gpt-5.6-luna) emit_error model_unavailable 10 ;;
  terra-unavailable:gpt-5.6-terra) emit_error model_unavailable 10 ;;
  implementation-failure:gpt-5.6-terra) emit_error implementation_error 11 ;;
  global-terra:gpt-5.6-terra) emit_error insufficient_quota 12 ;;
  global-sol:gpt-5.6-terra) emit_error model_unavailable 10 ;;
  global-sol:gpt-5.6-sol) emit_error insufficient_quota 12 ;;
  both-unavailable:gpt-5.6-terra|both-unavailable:gpt-5.6-sol) emit_error model_unavailable 10 ;;
  generic-429:gpt-5.6-terra) emit_error rate_limit_exceeded 13 ;;
  profile-fallback:state-fix) emit_error model_unavailable 10 ;;
  explicit-quota:*)
    printf '%s\n' 'Account-wide Codex quota is exhausted.' >&2
    exit 12
    ;;
esac
printf '%s\n' '{"type":"result","status":"completed"}'
if [ -n "$last_message" ]; then
  printf '%s\n' completed >"$last_message"
fi
MOCK
chmod +x "$mock_bin/codex"

export OPS_ROOT="$workspace"
export OPS_WORKSPACE_ROOT="$workspace"
export QUANT_RESEARCH_STATE_DIR="$workspace/.ops/runtime/quant-research"
export PATH="$mock_bin:/usr/bin:/bin"
export CODEX_TIMEOUT_SECONDS=2

new_change() {
  local change="$1" session="session-$1"
  "$RUNTIME" lock "$change" "$session"
  "$RUNTIME" init "$change" "$session"
  "$RUNTIME" lock-repos "$change" "$session" "$repository"
}
enter_implement() {
  "$RUNTIME" phase "$1" "session-$1" IMPLEMENT
}
enter_fix() {
  local change="$1" finding="$2"
  enter_implement "$change"
  "$RUNTIME" phase "$change" "session-$change" VERIFY
  "$RUNTIME" fix "$change" "session-$change"
  round="$(jq -r '.round' "$workspace/.ops/changes/$change/runtime/state.json")"
  printf '%s\n' "$finding" >"$workspace/.ops/changes/$change/runtime/verification-findings-round-$round.md"
}
run_worker() {
  local scenario="$1" trace="$2" change="$3" phase="$4"
  local status
  set +e
  FAKE_SCENARIO="$scenario" FAKE_TRACE_DIR="$trace" \
    "$RUNNER" "$change" "$repository" "$phase"
  status=$?
  set -e
  "$RUNTIME" unlock-repos "$change" "session-$change"
  return "$status"
}

"$QUANT" codex-on >/dev/null

new_change implement-policy
enter_implement implement-policy
trace="$tmp/trace-implement"
run_worker success "$trace" implement-policy IMPLEMENT
assert_file_contains "$trace/call-1.args" gpt-5.6-luna 'IMPLEMENT did not select Luna'
assert_file_contains "$trace/call-1.args" 'model_reasoning_effort="high"' 'IMPLEMENT did not select high reasoning'
assert_file_contains "$trace/call-1.args" --dangerously-bypass-approvals-and-sandbox 'Codex yolo-equivalent flag is missing'
if grep -Fq -- xhigh "$trace/call-1.args"; then fail 'xhigh was passed'; fi
meta="$workspace/.ops/changes/implement-policy/runtime/logs/codex-implement-round-0-attempt-1.meta.json"
jq -e 'keys == ["attempt","fallback_from","model","phase","reasoning_effort","result_class","round","worker"]
  and .worker == "codex" and .phase == "IMPLEMENT" and .round == 0 and .attempt == 1
  and .model == "gpt-5.6-luna" and .reasoning_effort == "high"
  and .fallback_from == null and .result_class == "success"' "$meta" >/dev/null \
  || fail 'IMPLEMENT metadata is incomplete or unsafe'

new_change implement-unavailable
enter_implement implement-unavailable
trace="$tmp/trace-implement-unavailable"
expect_failure run_worker implement-unavailable "$trace" implement-unavailable IMPLEMENT
assert_no_second_attempt "$trace" 'IMPLEMENT model failure incorrectly tried another model'
test "$("$QUANT" state | jq -r '.codex_available')" = true \
  || fail 'IMPLEMENT model-local failure disabled Codex'

new_change operator-overrides
enter_implement operator-overrides
trace="$tmp/trace-overrides"
CODEX_IMPLEMENT_MODEL=operator-model CODEX_REASONING_EFFORT=medium \
  run_worker success "$trace" operator-overrides IMPLEMENT
assert_file_contains "$trace/call-1.args" operator-model 'IMPLEMENT model override was ignored'
assert_file_contains "$trace/call-1.args" 'model_reasoning_effort="medium"' 'reasoning override was ignored'

"$QUANT" profile-set implement state-implement low >/dev/null
"$QUANT" profile-set fix state-fix medium >/dev/null
"$QUANT" profile-set fix-fallback state-fallback xhigh >/dev/null
new_change state-implement-profile
enter_implement state-implement-profile
trace="$tmp/trace-state-implement"
run_worker success "$trace" state-implement-profile IMPLEMENT
assert_file_contains "$trace/call-1.args" state-implement 'IMPLEMENT ignored its persisted model profile'
assert_file_contains "$trace/call-1.args" 'model_reasoning_effort="low"' 'IMPLEMENT ignored its persisted effort profile'
new_change state-fix-profiles
enter_fix state-fix-profiles 'profile routing finding'
trace="$tmp/trace-state-fix"
run_worker profile-fallback "$trace" state-fix-profiles FIX
assert_file_contains "$trace/call-1.args" state-fix 'primary FIX ignored its persisted model profile'
assert_file_contains "$trace/call-1.args" 'model_reasoning_effort="medium"' 'primary FIX ignored its persisted effort profile'
assert_file_contains "$trace/call-2.args" state-fallback 'FIX fallback ignored its persisted model profile'
assert_file_contains "$trace/call-2.args" 'model_reasoning_effort="xhigh"' 'FIX fallback ignored its persisted effort profile'
jq -e '.model == "state-fallback" and .reasoning_effort == "xhigh"' \
  "$workspace/.ops/changes/state-fix-profiles/runtime/logs/codex-fix-round-1-attempt-2.meta.json" >/dev/null \
  || fail 'fallback metadata did not record its effective profile'
"$QUANT" profiles-reset >/dev/null

new_change fix-fallback
enter_fix fix-fallback 'ROUND ONE UNIQUE FINDING'
trace="$tmp/trace-fallback"
run_worker terra-unavailable "$trace" fix-fallback FIX
assert_file_contains "$trace/call-1.args" gpt-5.6-terra 'FIX primary did not select Terra'
assert_file_contains "$trace/call-2.args" gpt-5.6-sol 'FIX fallback did not select Sol'
assert_file_contains "$trace/call-1.prompt" 'ROUND ONE UNIQUE FINDING' 'primary FIX prompt omitted findings'
assert_file_contains "$trace/call-2.prompt" 'ROUND ONE UNIQUE FINDING' 'fallback FIX prompt omitted findings'
test "$(jq -r '.round' "$workspace/.ops/changes/fix-fallback/runtime/state.json")" = 1 \
  || fail 'model fallback consumed another FIX round'
jq -e '.attempt == 2 and .fallback_from == "gpt-5.6-terra" and .result_class == "success"' \
  "$workspace/.ops/changes/fix-fallback/runtime/logs/codex-fix-round-1-attempt-2.meta.json" >/dev/null \
  || fail 'fallback metadata is incorrect'

new_change normal-failure
enter_fix normal-failure 'normal failure finding'
trace="$tmp/trace-normal-failure"
expect_failure run_worker implementation-failure "$trace" normal-failure FIX
assert_no_second_attempt "$trace" 'implementation failure incorrectly used Sol'

new_change global-primary
enter_fix global-primary 'global quota finding'
trace="$tmp/trace-global-primary"
expect_failure run_worker global-terra "$trace" global-primary FIX
assert_no_second_attempt "$trace" 'global quota incorrectly used Sol'
test "$("$QUANT" state | jq -r '.codex_available')" = false || fail 'global quota did not disable Codex'
jq -e '.implementation_backend == "codex"' "$workspace/.ops/changes/global-primary/runtime/state.json" >/dev/null \
  || fail 'global quota mutated the active backend'

"$RUNTIME" lock future-fallback session-future-fallback
"$RUNTIME" init future-fallback session-future-fallback claude-fallback quant-fallback
jq -e '.implementation_backend == "claude-fallback"' \
  "$workspace/.ops/changes/future-fallback/runtime/state.json" >/dev/null \
  || fail 'new quant transaction could not observe automatic disable'
"$RUNTIME" cleanup future-fallback session-future-fallback BLOCKED
"$QUANT" codex-on >/dev/null

new_change global-fallback
enter_fix global-fallback 'fallback quota finding'
trace="$tmp/trace-global-fallback"
expect_failure run_worker global-sol "$trace" global-fallback FIX
test -f "$trace/call-2.args" || fail 'Sol was not attempted after Terra unavailable'
test "$("$QUANT" state | jq -r '.codex_available')" = false || fail 'Sol global quota did not disable Codex'
"$QUANT" codex-on >/dev/null

new_change unavailable-both
enter_fix unavailable-both 'both unavailable finding'
trace="$tmp/trace-both"
expect_failure run_worker both-unavailable "$trace" unavailable-both FIX
test "$("$QUANT" state | jq -r '.codex_available')" = true || fail 'model-local failures disabled Codex'

new_change generic-rate-limit
enter_fix generic-rate-limit 'generic 429 finding'
trace="$tmp/trace-429"
expect_failure run_worker generic-429 "$trace" generic-rate-limit FIX
assert_no_second_attempt "$trace" 'generic 429 incorrectly used Sol'
test "$("$QUANT" state | jq -r '.codex_available')" = true || fail 'generic 429 disabled Codex'

new_change explicit-quota
enter_implement explicit-quota
trace="$tmp/trace-explicit-quota"
expect_failure run_worker explicit-quota "$trace" explicit-quota IMPLEMENT
test "$("$QUANT" state | jq -r '.codex_available')" = false || fail 'explicit quota text did not disable Codex'
"$QUANT" codex-on >/dev/null

new_change findings-required
enter_fix findings-required 'temporary finding'
rm -f -- "$workspace/.ops/changes/findings-required/runtime/verification-findings-round-1.md"
trace="$tmp/trace-findings-required"
expect_failure run_worker success "$trace" findings-required FIX
test ! -e "$trace/call-1.args" || fail 'FIX ran without its findings artifact'

new_change findings-isolation
enter_fix findings-isolation 'ROUND ONE MUST NOT LEAK'
trace="$tmp/trace-round-one"
expect_failure run_worker implementation-failure "$trace" findings-isolation FIX
"$RUNTIME" phase findings-isolation session-findings-isolation VERIFY
"$RUNTIME" fix findings-isolation session-findings-isolation
"$RUNTIME" lock-repos findings-isolation session-findings-isolation "$repository"
printf '%s\n' 'ROUND TWO ONLY' \
  >"$workspace/.ops/changes/findings-isolation/runtime/verification-findings-round-2.md"
trace="$tmp/trace-round-two"
expect_failure run_worker implementation-failure "$trace" findings-isolation FIX
assert_file_contains "$trace/call-1.prompt" 'ROUND TWO ONLY' 'round-two findings were omitted'
if grep -Fq -- 'ROUND ONE MUST NOT LEAK' "$trace/call-1.prompt"; then fail 'round-one findings leaked'; fi

assert_file_contains "$ROOT_DIR/.claude/commands/ops/run.md" 'ops-runtime.sh fix <change> <session-id>' 'atomic FIX contract is missing'
assert_file_contains "$ROOT_DIR/.claude/commands/ops/run.md" 'Do not invoke `claude`, `claude -p`,' 'Claude fallback guard is missing'
assert_file_contains "$ROOT_DIR/.claude/commands/ops/run.md" '--dangerously-skip-permissions' 'conditional Claude CLI permission contract is missing'

printf 'test_codex_worker_policy: all checks passed\n'
