#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
CODEX_CLASSIFIER="${CODEX_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
CLAUDE_CLASSIFIER="${CLAUDE_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-claude-result.sh}"
TIMEOUT_SECONDS="${PHASE_AGENT_PROBE_TIMEOUT_SECONDS:-30}"
COOLDOWN_SECONDS="${PHASE_AGENT_PROBE_COOLDOWN_SECONDS:-3600}"
inconclusive() { printf 'inconclusive:%s\n' "$1"; exit 3; }
[[ $# -eq 1 ]] || inconclusive invalid-arguments
provider="$1"; case "$provider" in codex|claude) ;; *) inconclusive invalid-provider ;; esac
[[ "$TIMEOUT_SECONDS" =~ ^[1-9][0-9]*$ ]] || inconclusive invalid-timeout
[[ "$COOLDOWN_SECONDS" =~ ^[0-9]+$ ]] || inconclusive invalid-cooldown
for command in jq timeout "$provider"; do command -v "$command" >/dev/null 2>&1 || inconclusive "missing-$command"; done
[[ -x "$STATE" ]] || inconclusive missing-state
state_json="$($STATE state 2>/dev/null)" || inconclusive invalid-state
read -r model effort < <(jq -r --arg provider "$provider" '[.phases[].candidates[]|select(.provider==$provider)][0]|[.model,.effort]|@tsv' <<<"$state_json")
[[ -n "$model" && -n "$effort" ]] || inconclusive missing-candidate
model_var="PHASE_AGENT_${provider^^}_PROBE_MODEL"; effort_var="PHASE_AGENT_${provider^^}_PROBE_EFFORT"
model="${!model_var:-$model}"; effort="${!effort_var:-$effort}"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
stdout="$tmp/stdout.jsonl"; stderr="$tmp/stderr.log"
set +e
if [[ "$provider" = codex ]]; then
  timeout --signal=TERM --kill-after=5s "${TIMEOUT_SECONDS}s" codex exec --dangerously-bypass-approvals-and-sandbox --ignore-user-config --skip-git-repo-check --ephemeral --json --model "$model" --config "model_reasoning_effort=\"$effort\"" 'Reply with exactly OK.' >"$stdout" 2>"$stderr"
  status=$?; classifier="$CODEX_CLASSIFIER"
else
  timeout --signal=TERM --kill-after=5s "${TIMEOUT_SECONDS}s" claude --print --model "$model" --effort "$effort" --dangerously-skip-permissions --output-format stream-json --verbose --no-session-persistence 'Reply with exactly OK.' >"$stdout" 2>"$stderr"
  status=$?; classifier="$CLAUDE_CLASSIFIER"
fi
set -e
result="$($classifier "$status" "$stdout" "$stderr")" || inconclusive classifier
case "$result" in
  success) "$STATE" provider-result "$provider" success >/dev/null; printf '%s\n' available ;;
  global-quota-exhausted|auth-error) "$STATE" provider-result "$provider" "$result" >/dev/null; printf '%s\n' unavailable ;;
  *) "$STATE" provider-result "$provider" probe-inconclusive "$COOLDOWN_SECONDS" >/dev/null; inconclusive "$result" ;;
esac
