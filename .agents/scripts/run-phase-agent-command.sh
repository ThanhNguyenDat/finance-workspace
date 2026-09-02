#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
RUNTIME="$SCRIPT_DIR/ops-runtime.sh"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
QUANT_STATE="${QUANT_RESEARCH_STATE_HELPER:-$SCRIPT_DIR/quant-research-state.sh}"
CODEX_CLASSIFIER="${CODEX_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
CLAUDE_CLASSIFIER="${CLAUDE_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-claude-result.sh}"
DETECTOR="${PHASE_AGENT_DETECTOR:-$SCRIPT_DIR/detect-provider-availability.sh}"
ambient_claude_config_dir="${CLAUDE_CONFIG_DIR-}"; ambient_codex_home="${CODEX_HOME-}"
ambient_claude_config_set="${CLAUDE_CONFIG_DIR+x}"; ambient_codex_home_set="${CODEX_HOME+x}"
die() { printf 'run-phase-agent-command: %s\n' "$1" >&2; exit 1; }
[[ $# -eq 1 && "$1" = quant-research ]] || die 'usage: run-phase-agent-command.sh quant-research'
for command in jq timeout git uv; do command -v "$command" >/dev/null 2>&1 || die "$command is required"; done
[[ -x "$STATE" && -x "$QUANT_STATE" ]] || die 'state helper unavailable'
prompt_file="$ROOT_DIR/.claude/commands/quant-research.md"; [[ -s "$prompt_file" ]] || die 'canonical quant prompt missing'
timeout_seconds="${PHASE_AGENT_QUANT_TIMEOUT_SECONDS:-3600}"; [[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'invalid timeout'
lease_dir="${PHASE_AGENT_QUANT_LEASE_DIR:-$ROOT_DIR/.ops/runtime/phase-agents/.quant-research-lock}"
release_lease() { if [[ -f "$lease_dir/pid" && "$(<"$lease_dir/pid")" = "$$" ]]; then rm -rf -- "$lease_dir"; fi; }
mkdir -p -- "$(dirname -- "$lease_dir")"
if ! mkdir -- "$lease_dir" 2>/dev/null; then
  owner=''; [[ ! -f "$lease_dir/pid" ]] || owner="$(<"$lease_dir/pid")"
  if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null; then die "quant research already runs as pid $owner"; fi
  rm -rf -- "$lease_dir"; mkdir -- "$lease_dir" 2>/dev/null || die 'cannot acquire quant research lease'
fi
printf '%s\n' "$$" >"$lease_dir/pid"
account_lock_provider=''; account_lock_name=''; account_lock_held=false
release_account_lock() {
  if [[ "$account_lock_held" = true ]]; then
    "$RUNTIME" unlock-account "$account_lock_provider" "$account_lock_name" "$$" "quant-research" >/dev/null 2>&1 || :
    account_lock_held=false
  fi
}
cleanup_locks() { release_account_lock; release_lease; }
trap cleanup_locks EXIT
agent_json="$($STATE state)"
if [[ -n "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}${PHASE_AGENT_QUANT_RESEARCH_MODEL:-}${PHASE_AGENT_QUANT_RESEARCH_EFFORT:-}${PHASE_AGENT_QUANT_RESEARCH_ACCOUNT:-}" ]]; then
  [[ -n "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}" && -n "${PHASE_AGENT_QUANT_RESEARCH_MODEL:-}" && -n "${PHASE_AGENT_QUANT_RESEARCH_EFFORT:-}" ]] || die 'quant provider/model/effort overrides must be supplied together'
  if [[ -n "${PHASE_AGENT_QUANT_RESEARCH_ACCOUNT:-}" ]]; then "$STATE" validate "$PHASE_AGENT_QUANT_RESEARCH_PROVIDER" "$PHASE_AGENT_QUANT_RESEARCH_MODEL" "$PHASE_AGENT_QUANT_RESEARCH_EFFORT" "$PHASE_AGENT_QUANT_RESEARCH_ACCOUNT"; else "$STATE" validate "$PHASE_AGENT_QUANT_RESEARCH_PROVIDER" "$PHASE_AGENT_QUANT_RESEARCH_MODEL" "$PHASE_AGENT_QUANT_RESEARCH_EFFORT"; fi
  candidates="$(jq -cn --arg p "$PHASE_AGENT_QUANT_RESEARCH_PROVIDER" --arg m "$PHASE_AGENT_QUANT_RESEARCH_MODEL" --arg e "$PHASE_AGENT_QUANT_RESEARCH_EFFORT" --arg a "${PHASE_AGENT_QUANT_RESEARCH_ACCOUNT:-}" '[{provider:$p,model:$m,effort:$e} + (if $a == "" then {} else {account:$a} end)]')"
else
  candidates="$(jq -c '.phases.quant_research.candidates' <<<"$agent_json")"
fi
count="$(jq 'length' <<<"$candidates")"
for ((index=0; index<count; index++)); do
  candidate="$(jq -c ".[$index]" <<<"$candidates")"
  candidate_provider="$(jq -r '.provider' <<<"$candidate")"; candidate_model="$(jq -r '.model' <<<"$candidate")"; candidate_effort="$(jq -r '.effort' <<<"$candidate")"; candidate_account="$(jq -r '.account // empty' <<<"$candidate")"
  if [[ -n "$candidate_account" ]]; then "$STATE" validate "$candidate_provider" "$candidate_model" "$candidate_effort" "$candidate_account"; else "$STATE" validate "$candidate_provider" "$candidate_model" "$candidate_effort"; fi
done
quant_json="$($QUANT_STATE begin-iteration)"; iteration="$(jq -r '.iteration' <<<"$quant_json")"; [[ "$iteration" =~ ^[1-9][0-9]*$ ]] || die 'invalid iteration'
canonical_prompt="$(<"$prompt_file")"
base_prompt="Quant iteration $iteration was already recorded mechanically by the terminal launcher. Do not call begin-iteration and do not increment it again. Execute exactly this iteration.\n\n$canonical_prompt"
run_dir="$ROOT_DIR/.ops/runtime/phase-agents/quant-runs/iteration-$iteration"; mkdir -p -- "$run_dir"
continuation=false; last_status=1; attempt=0
for ((index=0; index<count; index++)); do
  candidate="$(jq -c ".[$index]" <<<"$candidates")"; provider="$(jq -r '.provider' <<<"$candidate")"; model="$(jq -r '.model' <<<"$candidate")"; effort="$(jq -r '.effort' <<<"$candidate")"; account="$(jq -r '.account // empty' <<<"$candidate")"; account="${account,,}"
  agent_json="$($STATE state)"; mode="$(jq -r '.phases.quant_research.mode' <<<"$agent_json")"; pinned="$(jq -r '.phases.quant_research.pinned_provider//empty' <<<"$agent_json")"
  pinned_account="$(jq -r '.phases.quant_research.pinned_account // empty' <<<"$agent_json")"
  if [[ -z "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}" && "$mode" = manual && ( "$pinned" != "$provider" || ( -n "$pinned_account" && "$pinned_account" != "$account" ) ) ]]; then continue; fi
  if [[ -n "$account" ]]; then available="$(jq -r --arg provider "$provider" --arg account "$account" '.providers[$provider].accounts[$account].available // true' <<<"$agent_json")"; else available="$(jq -r --arg provider "$provider" '.providers[$provider].available' <<<"$agent_json")"; fi
  if [[ -z "$account" && "$available" != true && -x "$DETECTOR" ]] && "$STATE" probe-due "$provider" >/dev/null 2>&1; then "$DETECTOR" "$provider" >/dev/null 2>&1 || :; available="$("$STATE" state | jq -r --arg provider "$provider" '.providers[$provider].available')"; fi
  [[ "$available" = true ]] || continue
  attempt=$((attempt+1)); base="$run_dir/attempt-$attempt-$provider"; prompt="$base_prompt"
  if [[ "$continuation" = true ]]; then prompt="Continue quant iteration $iteration after provider quota interruption. Preserve existing research artifacts and do not restart, reschedule, or increment the iteration.\n\n$base_prompt"; fi
  release_account_lock
  if [[ -n "$account" ]]; then
    account_dir="$("$STATE" account-dir "$provider" "$account")"
    account_lock_provider="$provider"; account_lock_name="$account"
    "$RUNTIME" lock-account "$provider" "$account" "$$" "quant-research"
    account_lock_held=true
    if [[ "$provider" = claude ]]; then export CLAUDE_CONFIG_DIR="$account_dir"; else export CODEX_HOME="$account_dir"; fi
  else
    if [[ "$ambient_claude_config_set" = x ]]; then export CLAUDE_CONFIG_DIR="$ambient_claude_config_dir"; else unset CLAUDE_CONFIG_DIR; fi
    if [[ "$ambient_codex_home_set" = x ]]; then export CODEX_HOME="$ambient_codex_home"; else unset CODEX_HOME; fi
  fi
  set +e
  if [[ "$provider" = claude ]]; then
    (cd -- "$ROOT_DIR" && timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" claude --print --model "$model" --effort "$effort" --dangerously-skip-permissions --output-format stream-json --verbose --no-session-persistence <<<"$prompt") >"$base.stdout.jsonl" 2>"$base.stderr.log"
    status=$?; classifier="$CLAUDE_CLASSIFIER"
  else
    timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" codex exec --ignore-user-config --model "$model" --config "model_reasoning_effort=\"$effort\"" --cd "$ROOT_DIR" --ephemeral --dangerously-bypass-approvals-and-sandbox --json - <<<"$prompt" >"$base.stdout.jsonl" 2>"$base.stderr.log"
    status=$?; classifier="$CODEX_CLASSIFIER"
  fi
  set -e
  release_account_lock
  last_status="$status"; result="$($classifier "$status" "$base.stdout.jsonl" "$base.stderr.log")"; printf '%s\n' "$status" >"$base.exit"; printf '%s\n' "$result" >"$base.result-class"
  jq -n --argjson iteration "$iteration" --argjson attempt "$attempt" --arg provider "$provider" --arg model "$model" --arg effort "$effort" --arg account "$account" --argjson continuation "$continuation" --arg result "$result" \
    '{iteration:$iteration,attempt:$attempt,provider:$provider,model:$model,effort:$effort} + (if $account == "" then {} else {account:$account} end) + {continuation:$continuation,result_class:$result}' >"$base.meta.json"
  case "$result" in success) if [[ -n "$account" ]]; then "$STATE" provider-result "$provider" success "$account" >/dev/null; else "$STATE" provider-result "$provider" success >/dev/null; fi; printf 'Quant iteration %s completed with %s\n' "$iteration" "$provider"; exit 0 ;;
    global-quota-exhausted|auth-error) if [[ -n "$account" ]]; then "$STATE" provider-result "$provider" "$result" "$account" >/dev/null; else "$STATE" provider-result "$provider" "$result" >/dev/null; fi; continuation=true ;;
    model-unavailable|model-specific-limit) continuation=true ;;
    *) exit "$status" ;;
  esac
done
die "no eligible candidate completed quant iteration $iteration (last status $last_status)"
