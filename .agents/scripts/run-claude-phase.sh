#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_ROOT="${OPS_WORKSPACE_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
RUNTIME_ROOT="${OPS_ROOT:-$WORKSPACE_ROOT}"
RUNTIME="$SCRIPT_DIR/ops-runtime.sh"
CLASSIFIER="${CLAUDE_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-claude-result.sh}"
AGENT_STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
die() { printf 'run-claude-phase: %s\n' "$1" >&2; exit 1; }
usage() { printf 'usage: run-claude-phase.sh <change> <repository> <PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY>\n' >&2; }
[[ $# -eq 3 ]] || { usage; exit 2; }
change="$1"; repository="$2"; phase="$3"
[[ "$change" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "invalid change: $change"
case "$phase" in PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY) ;; *) die "unsupported phase: $phase" ;; esac
for command in claude jq timeout git sha256sum; do command -v "$command" >/dev/null 2>&1 || die "$command is required"; done
[[ -x "$RUNTIME" && -x "$CLASSIFIER" ]] || die 'runtime/classifier unavailable'
workspace_root="$(git -C "$WORKSPACE_ROOT" rev-parse --show-toplevel 2>/dev/null)" || die 'workspace is not a Git worktree'
repository_root="$(git -C "$repository" rev-parse --show-toplevel 2>/dev/null)" || die 'repository is not a Git worktree'
workspace_root="$(cd -- "$workspace_root" && pwd -P)"; repository_root="$(cd -- "$repository_root" && pwd -P)"
repository_args=()
[[ "$workspace_root" = "$repository_root" ]] || repository_args=(--add-dir "$repository_root")
state_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/state.json"; [[ -f "$state_file" ]] || die 'runtime state missing'
session_id="$(jq -r '.session_id//empty' "$state_file")"; [[ -n "$session_id" ]] || die 'missing session id'
[[ "$(jq -r '.phase//empty' "$state_file")" = "$phase" ]] || die 'runtime phase mismatch'
if ! jq -e '.routing_policy_version==1' "$state_file" >/dev/null 2>&1; then
  backend="$(jq -r '.implementation_backend//"codex"' "$state_file")"
  case "$phase:$backend" in PLAN:*|VERIFY:*|FINAL_VERIFY:*|IMPLEMENT:claude-fallback|FIX:claude-fallback) ;; *) die 'legacy runtime does not select Claude for this phase' ;; esac
fi
"$RUNTIME" assert-repo-lock "$change" "$session_id" "$repository_root"
round="$(jq -r '.round//0' "$state_file")"; [[ "$round" =~ ^[0-9]+$ ]] || die 'invalid round'
model="${PHASE_AGENT_MODEL:-}"; effort="${PHASE_AGENT_EFFORT:-}"
if [[ -z "$model" || -z "$effort" ]]; then
  [[ -x "$AGENT_STATE" ]] || die 'phase-agent state unavailable'
  IFS=$'\t' read -r provider model effort account < <("$AGENT_STATE" resolve "${phase,,}")
  [[ "$provider" = claude ]] || die 'resolved candidate is not Claude'
fi
account="${PHASE_AGENT_ACCOUNT:-${account:-}}"
if [[ -n "$account" ]]; then
  account_dir="$("$AGENT_STATE" account-dir claude "$account")"
  "$RUNTIME" lock-account claude "$account" "$$" "$change" "$session_id"
  account_lock_held=true
  release_account_lock() {
    if [[ "$account_lock_held" = true ]]; then
      "$RUNTIME" unlock-account claude "$account" "$$" "$change" "$session_id" >/dev/null 2>&1 || :
      account_lock_held=false
    fi
  }
  trap release_account_lock EXIT
  export CLAUDE_CONFIG_DIR="$account_dir"
else
  account_lock_held=false
fi
[[ "$model" =~ ^[A-Za-z0-9._:-]+$ ]] || die 'unsafe model'
case "$effort" in low|medium|high|xhigh|max) ;; *) die 'unsupported Claude effort' ;; esac
if [[ "$model" =~ (^|[-.:])opus($|[-.:]) ]]; then case "$effort" in medium|high) ;; *) die 'Opus requires medium or high' ;; esac; fi
timeout_seconds="${CLAUDE_TIMEOUT_SECONDS:-3600}"; [[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'invalid timeout'
attempt_id="${PHASE_AGENT_ATTEMPT_ID:-direct-$(date -u '+%Y%m%dT%H%M%S%NZ')-$$}"; [[ "$attempt_id" =~ ^[A-Za-z0-9._:-]+$ ]] || die 'unsafe attempt id'
continuation="${PHASE_AGENT_CONTINUATION:-false}"; case "$continuation" in true|false) ;; *) die 'invalid continuation' ;; esac
findings=''
if [[ "$phase" = FIX ]]; then findings_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/verification-findings-round-$round.md"; [[ -s "$findings_file" ]] || die 'FIX findings missing'; findings="$(<"$findings_file")"; fi
prompt="Execute OPS phase $phase for OpenSpec change $change in $repository_root.
Read AGENTS.md, CLAUDE.md, applicable rules/skills, the active change, OPS state and repository-local instructions. Preserve locks, scope, tests, safety and secrets. Do not push or launch another model process."
case "$phase" in
  PLAN) prompt+=$'\nPlan/reconcile OpenSpec only; do not implement runtime code.' ;;
  IMPLEMENT) prompt+=$'\nImplement the approved scope, add tests and run bounded local checks.' ;;
  VERIFY|FINAL_VERIFY) prompt+=$'\nRead-only verification: do not edit, format, stage or commit. Report severity with exact evidence.' ;;
  FIX) prompt+=$'\nFix only the current-round findings and add regression coverage.\n--- FINDINGS ---\n'"$findings" ;;
esac
if [[ "$phase" = FINAL_VERIFY ]]; then
  prompt+=$'\nYou are the currently running FINAL_VERIFY attempt. This is the pre-push gate: do not report an unpushed local commit, unavailable GitHub Actions run, or the active change task that explicitly covers push/CI as a P0/P1 finding; these are evaluated only after this gate passes and the commit is pushed. The resolver appends this attempt and derives verification evidence only after your process exits, so do not fail solely because your own record is not yet present in runtime state. Evaluate the committed code, findings, and applicable local objective checks. Run only the smallest relevant bounded checks, sequentially; do not launch exploratory scans, duplicate checks, parallel shell calls, or retry loops. Do not issue shell commands containing rm, rm -f, git reset, or git checkout; do not create temporary artifacts that need cleanup. If a check fails, record the exact finding and continue to the final assessment. After the objective checks finish, stop using tools and immediately end the response with exactly these machine-readable lines, using PASS only after all applicable objective checks pass and no P0/P1 remains:\nFINAL_VERIFY_GATE: PASS|FAIL\nP0_FINDINGS: <count>\nP1_FINDINGS: <count>\nOBJECTIVE_GATES: PASS|FAIL'
fi
if [[ "$continuation" = true ]]; then prompt+=$'\nThis is a continuation after provider interruption. Inspect and preserve the current diff/commits and complete remaining work; do not restart or roll back.'; fi
fingerprint() {
  local root="$1" file
  { git -C "$root" status --porcelain=v1 -z; git -C "$root" diff --binary HEAD; while IFS= read -r -d '' file; do
      printf '%s\0' "$file"
      if [[ -L "$root/$file" ]]; then printf 'symlink:%s\0' "$(readlink -- "$root/$file")"; else sha256sum -- "$root/$file"; fi
    done < <(git -C "$root" ls-files --others --exclude-standard -z); } | sha256sum | awk '{print $1}'
}
workspace_before=''; repo_before=''
if [[ "$phase" = VERIFY || "$phase" = FINAL_VERIFY ]]; then workspace_before="$(fingerprint "$workspace_root")"; repo_before="$(fingerprint "$repository_root")"; fi
log_dir="$RUNTIME_ROOT/.ops/changes/$change/runtime/logs"; mkdir -p -- "$log_dir"
base="${PHASE_AGENT_EVIDENCE_BASE:-$log_dir/claude-${phase,,}-round-$round-$attempt_id}"
stdout="$base.stdout.jsonl"; stderr="$base.stderr.log"; last="$base.last-message.md"; exit_file="$base.exit"; result_file="$base.result-class"
set +e
(cd -- "$workspace_root" && timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" claude --print --model "$model" --effort "$effort" --dangerously-skip-permissions --output-format stream-json --verbose --no-session-persistence "${repository_args[@]}" <<<"$prompt") >"$stdout" 2>"$stderr"
status=$?
set -e
printf '%s\n' "$status" >"$exit_file"
jq -rs '[.[]|select(.type=="result")|.result//empty]|last//empty' "$stdout" 2>/dev/null >"$last" || :
result="$($CLASSIFIER "$status" "$stdout" "$stderr")"
if [[ "$phase" = VERIFY || "$phase" = FINAL_VERIFY ]]; then
  if [[ "$workspace_before" != "$(fingerprint "$workspace_root")" || "$repo_before" != "$(fingerprint "$repository_root")" ]]; then printf '%s\n' 'read-only verifier mutated a Git worktree' >>"$stderr"; status=1; result=implementation-error; printf '%s\n' "$status" >"$exit_file"; fi
fi
printf '%s\n' "$result" >"$result_file"
if [[ -x "$AGENT_STATE" && ( "$result" = global-quota-exhausted || "$result" = auth-error || "$result" = success ) ]]; then
  if [[ -n "$account" ]]; then "$AGENT_STATE" provider-result claude "$result" "$account" >/dev/null; else "$AGENT_STATE" provider-result claude "$result" >/dev/null; fi
fi
[[ "$status" -eq 0 ]] || { printf 'Claude phase %s failed: %s\n' "$phase" "$result" >&2; exit "$status"; }
printf 'Claude phase %s completed: %s\n' "$phase" "$base"
