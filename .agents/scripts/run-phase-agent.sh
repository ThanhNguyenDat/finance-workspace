#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_ROOT="${OPS_WORKSPACE_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
RUNTIME_ROOT="${OPS_ROOT:-$WORKSPACE_ROOT}"
RUNTIME="$SCRIPT_DIR/ops-runtime.sh"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
DETECTOR="${PHASE_AGENT_DETECTOR:-$SCRIPT_DIR/detect-provider-availability.sh}"
die() { printf 'run-phase-agent: %s\n' "$1" >&2; exit 1; }
[[ $# -eq 3 ]] || die 'usage: run-phase-agent.sh <change> <repository> <PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY>'
change="$1"; repository="$2"; phase="$3"
[[ "$change" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die 'invalid change'
case "$phase" in PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY) ;; *) die 'unsupported phase' ;; esac
for command in jq git sha256sum; do command -v "$command" >/dev/null 2>&1 || die "$command is required"; done
[[ -x "$RUNTIME" && -x "$STATE" ]] || die 'runtime/state helper unavailable'
workspace_root="$(git -C "$WORKSPACE_ROOT" rev-parse --show-toplevel 2>/dev/null)" || die 'workspace is not a Git worktree'
repository_root="$(git -C "$repository" rev-parse --show-toplevel 2>/dev/null)" || die 'repository is not a Git worktree'
workspace_root="$(cd -- "$workspace_root" && pwd -P)"; repository_root="$(cd -- "$repository_root" && pwd -P)"
state_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/state.json"; [[ -f "$state_file" ]] || die 'OPS state missing'
session_id="$(jq -r '.session_id//empty' "$state_file")"; [[ -n "$session_id" ]] || die 'session id missing'
[[ "$(jq -r '.phase//empty' "$state_file")" = "$phase" ]] || die 'phase mismatch'
jq -e '.routing_policy_version==1' "$state_file" >/dev/null || die 'generic resolver requires routing policy version 1'
"$RUNTIME" assert-repo-lock "$change" "$session_id" "$repository_root"
round="$(jq -r '.round//0' "$state_file")"; [[ "$round" =~ ^[0-9]+$ ]] || die 'invalid round'
runtime_dir="$RUNTIME_ROOT/.ops/changes/$change/runtime"; log_dir="$runtime_dir/logs"; mkdir -p -- "$log_dir"
lease="$runtime_dir/.phase-attempt-lock"
release_lease() { if [[ -f "$lease/pid" && "$(<"$lease/pid")" = "$$" ]]; then rm -rf -- "$lease"; fi; }
if ! mkdir -- "$lease" 2>/dev/null; then
  owner=''; [[ ! -f "$lease/pid" ]] || owner="$(<"$lease/pid")"
  if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null; then die "phase attempt already runs as pid $owner"; fi
  rm -rf -- "$lease"; mkdir -- "$lease" || die 'cannot acquire phase lease'
fi
printf '%s\n' "$$" >"$lease/pid"; trap release_lease EXIT

fingerprint() {
  local root="$1" file
  { git -C "$root" status --porcelain=v1 -z; git -C "$root" diff --binary HEAD; while IFS= read -r -d '' file; do
      printf '%s\0' "$file"
      if [[ -L "$root/$file" ]]; then printf 'symlink:%s\0' "$(readlink -- "$root/$file")"; else sha256sum -- "$root/$file"; fi
    done < <(git -C "$root" ls-files --others --exclude-standard -z); } | sha256sum | awk '{print $1}'
}
phase_key="${phase,,}"
agent_json="$($STATE state)"
prefix="PHASE_AGENT_${phase}_"
provider_var="${prefix}PROVIDER"; model_var="${prefix}MODEL"; effort_var="${prefix}EFFORT"
override_provider="${!provider_var:-${PHASE_AGENT_PROVIDER:-}}"; override_model="${!model_var:-${PHASE_AGENT_MODEL:-}}"; override_effort="${!effort_var:-${PHASE_AGENT_EFFORT:-}}"
if [[ -n "$override_provider$override_model$override_effort" ]]; then
  [[ -n "$override_provider" && -n "$override_model" && -n "$override_effort" ]] || die 'provider/model/effort overrides must be supplied together'
  "$STATE" validate "$override_provider" "$override_model" "$override_effort"
  candidates="$(jq -cn --arg p "$override_provider" --arg m "$override_model" --arg e "$override_effort" '[{provider:$p,model:$m,effort:$e}]')"
else
  candidates="$(jq -c --arg phase "$phase_key" '.phases[$phase].candidates' <<<"$agent_json")"
fi
continuation=false; last_status=1; selected_any=false
count="$(jq 'length' <<<"$candidates")"
for ((index=0; index<count; index++)); do
  candidate="$(jq -c ".[$index]" <<<"$candidates")"
  provider="$(jq -r '.provider' <<<"$candidate")"; model="$(jq -r '.model' <<<"$candidate")"; effort="$(jq -r '.effort' <<<"$candidate")"
  "$STATE" validate "$provider" "$model" "$effort"
  agent_json="$($STATE state)"
  mode="$(jq -r --arg phase "$phase_key" '.phases[$phase].mode' <<<"$agent_json")"
  pinned="$(jq -r --arg phase "$phase_key" '.phases[$phase].pinned_provider//empty' <<<"$agent_json")"
  if [[ -z "$override_provider" && "$mode" = manual && "$pinned" != "$provider" ]]; then continue; fi
  available="$(jq -r --arg provider "$provider" '.providers[$provider].available' <<<"$agent_json")"
  if [[ "$available" != true ]]; then
    if [[ -x "$DETECTOR" ]] && "$STATE" probe-due "$provider" >/dev/null 2>&1; then "$DETECTOR" "$provider" >/dev/null 2>&1 || :; fi
    available="$("$STATE" state | jq -r --arg provider "$provider" '.providers[$provider].available')"
  fi
  [[ "$available" = true ]] || continue
  selected_any=true
  attempt="$(( $(jq '.attempts|length' "$state_file") + 1 ))"
  attempt_id="${phase,,}-r${round}-a${attempt}-$(date -u '+%Y%m%dT%H%M%S%NZ')"
  base="$log_dir/agent-$attempt_id"
  workspace_before="$(fingerprint "$workspace_root")"; repo_before="$(fingerprint "$repository_root")"; head_before="$(git -C "$repository_root" rev-parse HEAD)"; started="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  adapter="$SCRIPT_DIR/run-$provider-phase.sh"; [[ -x "$adapter" ]] || die "adapter unavailable: $adapter"
  set +e
  PHASE_AGENT_MODEL="$model" PHASE_AGENT_EFFORT="$effort" PHASE_AGENT_ATTEMPT_ID="$attempt_id" \
    PHASE_AGENT_CONTINUATION="$continuation" PHASE_AGENT_EVIDENCE_BASE="$base" \
    "$adapter" "$change" "$repository_root" "$phase"
  status=$?
  set -e
  last_status="$status"; [[ -s "$base.result-class" ]] || die 'adapter result class missing'
  result="$(<"$base.result-class")"; completed="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"; head_after="$(git -C "$repository_root" rev-parse HEAD)"
  objective_gates_passed=false
  if [[ "$phase" = FINAL_VERIFY && "$status" -eq 0 ]]; then
    if grep -Fqx 'FINAL_VERIFY_GATE: PASS' "$base.last-message.md" \
      && grep -Fqx 'P0_FINDINGS: 0' "$base.last-message.md" \
      && grep -Fqx 'P1_FINDINGS: 0' "$base.last-message.md" \
      && grep -Fqx 'OBJECTIVE_GATES: PASS' "$base.last-message.md"; then
      objective_gates_passed=true
    else
      printf '%s\n' 'FINAL_VERIFY did not provide a passing objective-gate attestation' >>"$base.stderr.log"
      status=1; last_status=1; result=implementation-error
      printf '%s\n' "$status" >"$base.exit"; printf '%s\n' "$result" >"$base.result-class"
    fi
  fi
  workspace_after="$(fingerprint "$workspace_root")"; repo_after="$(fingerprint "$repository_root")"; changed=false
  [[ "$workspace_before" = "$workspace_after" && "$repo_before" = "$repo_after" && "$head_before" = "$head_after" ]] || changed=true
  evidence_relative="${base#"$RUNTIME_ROOT/"}"
  record="$base.attempt.json"
  jq -n --argjson attempt "$attempt" --arg phase "$phase" --argjson round "$round" --arg provider "$provider" --arg model "$model" --arg effort "$effort" \
    --argjson continuation "$continuation" --arg result_class "$result" --argjson exit_status "$status" --argjson changed "$changed" --argjson process_id "$$" \
    --argjson objective_gates_passed "$objective_gates_passed" \
    --arg started_at "$started" --arg completed_at "$completed" --arg head_before "$head_before" --arg head_after "$head_after" --arg evidence_base "$evidence_relative" \
    '{attempt:$attempt,phase:$phase,round:$round,provider:$provider,model:$model,effort:$effort,continuation:$continuation,
      result_class:$result_class,exit_status:$exit_status,worktree_changed:$changed,process_id:$process_id,objective_gates_passed:$objective_gates_passed,
      started_at:$started_at,completed_at:$completed_at,head_before:$head_before,head_after:$head_after,evidence_base:$evidence_base}' >"$record"
  "$RUNTIME" record-attempt "$change" "$session_id" "$record"
  if [[ "$status" -eq 0 ]]; then printf 'Phase agent %s completed with %s\n' "$phase" "$provider"; exit 0; fi
  case "$result" in
    global-quota-exhausted|auth-error|model-unavailable|model-specific-limit)
      if [[ "$changed" = true && ( "$phase" = PLAN || "$phase" = IMPLEMENT || "$phase" = FIX ) ]]; then continuation=true; fi
      ;;
    *) exit "$status" ;;
  esac
done
[[ "$selected_any" = true ]] || die "no eligible candidate for $phase"
exit "$last_status"
