#!/usr/bin/env bash
set -Eeuo pipefail

# Bounded, non-interactive Codex worker used by /ops:run.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_ROOT="${OPS_WORKSPACE_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
RUNTIME_ROOT="${OPS_ROOT:-$WORKSPACE_ROOT}"
RUNTIME="$SCRIPT_DIR/ops-runtime.sh"
CLASSIFIER="${CODEX_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
QUANT_STATE_HELPER="${QUANT_RESEARCH_STATE_HELPER:-$SCRIPT_DIR/quant-research-state.sh}"

usage() {
  printf 'usage: run-codex-phase.sh <change> <repository> <IMPLEMENT|FIX>\n' >&2
}
die() {
  printf 'run-codex-phase: %s\n' "$1" >&2
  exit 1
}
valid_setting() {
  [[ "$1" =~ ^[A-Za-z0-9._:-]+$ ]]
}

[ "$#" -eq 3 ] || { usage; exit 2; }
change="$1"
repository="$2"
phase="$3"
[[ "$change" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "invalid change name: $change"
case "$phase" in IMPLEMENT|FIX) ;; *) die "invalid worker phase: $phase" ;; esac
workspace_root="$(git -C "$WORKSPACE_ROOT" rev-parse --show-toplevel 2>/dev/null)" \
  || die "workspace is not a Git worktree: $WORKSPACE_ROOT"
repository_root="$(git -C "$repository" rev-parse --show-toplevel 2>/dev/null)" \
  || die "repository is not a Git worktree: $repository"
workspace_root="$(cd -- "$workspace_root" && pwd -P)"
repository_root="$(cd -- "$repository_root" && pwd -P)"
[ "$workspace_root" != "$repository_root" ] || die 'runtime repository must differ from finance-workspace'
command -v codex >/dev/null 2>&1 || die 'codex CLI is not installed or not on PATH'
command -v jq >/dev/null 2>&1 || die 'jq is required'
[ -x "$CLASSIFIER" ] || die "Codex result classifier is unavailable: $CLASSIFIER"
[ -x "$QUANT_STATE_HELPER" ] || die "quant research state helper is unavailable: $QUANT_STATE_HELPER"

timeout_seconds="${CODEX_TIMEOUT_SECONDS:-3600}"
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'CODEX_TIMEOUT_SECONDS must be a positive integer'
implement_model="${CODEX_IMPLEMENT_MODEL:-gpt-5.6-luna}"
fix_model="${CODEX_FIX_MODEL:-gpt-5.6-terra}"
fix_fallback_model="${CODEX_FIX_FALLBACK_MODEL:-gpt-5.6-sol}"
reasoning_effort="${CODEX_REASONING_EFFORT:-high}"
for setting in "$implement_model" "$fix_model" "$fix_fallback_model" "$reasoning_effort"; do
  valid_setting "$setting" || die 'model and reasoning overrides must contain only safe identifier characters'
done

state_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/state.json"
[ -f "$state_file" ] || die "runtime state not found: $state_file"
session_id="$(jq -r '.session_id // empty' "$state_file")"
[ -n "$session_id" ] || die 'runtime state has no session id'
current_phase="$(jq -r '.phase // empty' "$state_file")"
[ "$current_phase" = "$phase" ] || die "runtime phase is $current_phase, requested worker phase is $phase"
implementation_backend="$(jq -r '.implementation_backend // "codex"' "$state_file")"
[ "$implementation_backend" = codex ] || die "Codex worker is not selected for backend: $implementation_backend"
"$RUNTIME" assert-repo-lock "$change" "$session_id" "$repository_root"
round="$(jq -r '.round' "$state_file")"
[[ "$round" =~ ^[0-9]+$ ]] || die 'runtime round is invalid'

findings=''
if [ "$phase" = FIX ]; then
  findings_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/verification-findings-round-$round.md"
  [ -s "$findings_file" ] || die "FIX findings are missing or empty: $findings_file"
  findings="$(<"$findings_file")"
fi

log_dir="$RUNTIME_ROOT/.ops/changes/$change/runtime/logs"
mkdir -p -- "$log_dir"
prompt="$(cat <<EOF
Apply OpenSpec change $change.

The current working directory is the Finance orchestration workspace.
Implementation repository: $repository_root

Read AGENTS.md, applicable .agents/rules/, relevant skills, the active
OpenSpec change, and repository-local instructions. Use the Codex-native
OpenSpec apply workflow. Modify only files required by the approved OpenSpec
change and within the declared implementation repository. Respect scope,
trading invariants, secret handling, and repository ownership. Run relevant
local verification and create local commits when required. Do not push before
Claude final verification.
EOF
)"
if [ "$phase" = FIX ]; then
  prompt+="$(cat <<EOF


Claude verification findings for FIX round $round follow. Address these exact
findings; do not use findings from another round.

--- BEGIN VERIFICATION FINDINGS ROUND $round ---
$findings
--- END VERIFICATION FINDINGS ROUND $round ---
EOF
)"
fi

attempt_status=1
attempt_result=unknown-error

run_attempt() {
  local model="$1"
  local attempt="$2"
  local fallback_from="$3"
  local base stdout_log stderr_log last_message exit_code_file meta_file meta_tmp status
  base="$log_dir/codex-${phase,,}-round-${round}-attempt-${attempt}"
  stdout_log="$base.stdout.jsonl"
  stderr_log="$base.stderr.log"
  last_message="$base.last-message.md"
  exit_code_file="$base.exit"
  meta_file="$base.meta.json"
  : >"$last_message"

  set +e
  timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" \
    codex exec --ignore-user-config --model "$model" \
    --config "model_reasoning_effort=\"$reasoning_effort\"" \
    --cd "$workspace_root" --add-dir "$repository_root" --ephemeral \
    --dangerously-bypass-approvals-and-sandbox --json \
    --output-last-message "$last_message" - \
    <<<"$prompt" >"$stdout_log" 2>"$stderr_log"
  status=$?
  set -e
  printf '%s\n' "$status" >"$exit_code_file"
  attempt_result="$("$CLASSIFIER" "$status" "$stdout_log" "$stderr_log")"
  attempt_status="$status"

  meta_tmp="$(mktemp "$log_dir/.codex-meta.XXXXXX")"
  jq -n \
    --arg worker codex \
    --arg phase "$phase" \
    --argjson round "$round" \
    --argjson attempt "$attempt" \
    --arg model "$model" \
    --arg reasoning_effort "$reasoning_effort" \
    --arg fallback_from "$fallback_from" \
    --arg result_class "$attempt_result" \
    '{worker: $worker, phase: $phase, round: $round, attempt: $attempt,
      model: $model, reasoning_effort: $reasoning_effort,
      fallback_from: (if $fallback_from == "" then null else $fallback_from end),
      result_class: $result_class}' >"$meta_tmp"
  mv -f -- "$meta_tmp" "$meta_file"

  if [ "$attempt_result" = global-quota-exhausted ]; then
    QUANT_RESEARCH_STATE_DIR="${QUANT_RESEARCH_STATE_DIR:-$RUNTIME_ROOT/.ops/runtime/quant-research}" \
      "$QUANT_STATE_HELPER" codex-off >/dev/null \
      || die 'global quota was detected but Codex availability could not be disabled'
  fi

  [ "$status" -eq 0 ]
}

if [ "$phase" = IMPLEMENT ]; then
  primary_model="$implement_model"
else
  primary_model="$fix_model"
fi

if run_attempt "$primary_model" 1 ''; then
  printf 'Codex phase %s completed; evidence: %s\n' "$phase" "$log_dir"
  exit 0
fi
primary_status="$attempt_status"
primary_result="$attempt_result"

if [ "$phase" = FIX ] && { [ "$primary_result" = model-unavailable ] || [ "$primary_result" = model-specific-limit ]; }; then
  if run_attempt "$fix_fallback_model" 2 "$primary_model"; then
    printf 'Codex phase %s completed via fallback; evidence: %s\n' "$phase" "$log_dir"
    exit 0
  fi
  primary_status="$attempt_status"
  primary_result="$attempt_result"
fi

printf 'Codex phase %s failed with class %s and exit %s; evidence: %s\n' \
  "$phase" "$primary_result" "$primary_status" "$log_dir" >&2
exit "$primary_status"
