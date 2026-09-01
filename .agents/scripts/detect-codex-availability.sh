#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
STATE_HELPER="${QUANT_RESEARCH_STATE_HELPER:-$SCRIPT_DIR/quant-research-state.sh}"
CLASSIFIER="${CODEX_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
TIMEOUT_SECONDS="${CODEX_PROBE_TIMEOUT_SECONDS:-30}"

inconclusive() {
  printf 'inconclusive:%s\n' "$1"
  exit 3
}

[[ "$TIMEOUT_SECONDS" =~ ^[1-9][0-9]*$ ]] || inconclusive invalid-timeout
command -v jq >/dev/null 2>&1 || inconclusive missing-jq
command -v timeout >/dev/null 2>&1 || inconclusive missing-timeout
command -v codex >/dev/null 2>&1 || inconclusive missing-codex
[[ -x "$STATE_HELPER" ]] || inconclusive missing-state-helper
[[ -x "$CLASSIFIER" ]] || inconclusive missing-classifier

profile="$($STATE_HELPER profile-get probe 2>/dev/null)" || inconclusive invalid-state
IFS=$'\t' read -r model effort <<<"$profile"
[[ -n "$model" && -n "$effort" ]] || inconclusive invalid-profile

probe_dir="$(mktemp -d)" || inconclusive tempdir-failure
cleanup() {
  rm -rf -- "$probe_dir"
}
trap cleanup EXIT
stdout_log="$probe_dir/stdout.jsonl"
stderr_log="$probe_dir/stderr.log"

set +e
(
  cd -- "$probe_dir"
  timeout --signal=TERM --kill-after=5s "${TIMEOUT_SECONDS}s" \
    codex exec --dangerously-bypass-approvals-and-sandbox \
    --ignore-user-config --skip-git-repo-check --ephemeral --json \
    --model "$model" --config "model_reasoning_effort=\"$effort\"" \
    'Reply with exactly OK.'
) >"$stdout_log" 2>"$stderr_log"
status=$?
set -e

result="$($CLASSIFIER "$status" "$stdout_log" "$stderr_log")" \
  || inconclusive classifier-failure
case "$result" in
  success)
    "$STATE_HELPER" codex-detected-on >/dev/null || inconclusive stale-mode
    printf '%s\n' available
    ;;
  global-quota-exhausted)
    "$STATE_HELPER" codex-detected-off >/dev/null || inconclusive stale-mode
    printf '%s\n' unavailable
    ;;
  *)
    inconclusive "$result"
    ;;
esac
