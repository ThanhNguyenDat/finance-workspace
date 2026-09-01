#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
QUANT_STATE="${QUANT_RESEARCH_STATE_HELPER:-$SCRIPT_DIR/quant-research-state.sh}"
CODEX_CLASSIFIER="${CODEX_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
CLAUDE_CLASSIFIER="${CLAUDE_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-claude-result.sh}"
DETECTOR="${PHASE_AGENT_DETECTOR:-$SCRIPT_DIR/detect-provider-availability.sh}"
die() { printf 'run-phase-agent-command: %s\n' "$1" >&2; exit 1; }
[[ $# -eq 1 && "$1" = quant-research ]] || die 'usage: run-phase-agent-command.sh quant-research'
for command in jq timeout git; do command -v "$command" >/dev/null 2>&1 || die "$command is required"; done
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
printf '%s\n' "$$" >"$lease_dir/pid"; trap release_lease EXIT
agent_json="$($STATE state)"
if [[ -n "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}${PHASE_AGENT_QUANT_RESEARCH_MODEL:-}${PHASE_AGENT_QUANT_RESEARCH_EFFORT:-}" ]]; then
  [[ -n "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}" && -n "${PHASE_AGENT_QUANT_RESEARCH_MODEL:-}" && -n "${PHASE_AGENT_QUANT_RESEARCH_EFFORT:-}" ]] || die 'quant provider/model/effort overrides must be supplied together'
  "$STATE" validate "$PHASE_AGENT_QUANT_RESEARCH_PROVIDER" "$PHASE_AGENT_QUANT_RESEARCH_MODEL" "$PHASE_AGENT_QUANT_RESEARCH_EFFORT"
  candidates="$(jq -cn --arg p "$PHASE_AGENT_QUANT_RESEARCH_PROVIDER" --arg m "$PHASE_AGENT_QUANT_RESEARCH_MODEL" --arg e "$PHASE_AGENT_QUANT_RESEARCH_EFFORT" '[{provider:$p,model:$m,effort:$e}]')"
else
  candidates="$(jq -c '.phases.quant_research.candidates' <<<"$agent_json")"
fi
count="$(jq 'length' <<<"$candidates")"
for ((index=0; index<count; index++)); do
  candidate="$(jq -c ".[$index]" <<<"$candidates")"
  "$STATE" validate "$(jq -r '.provider' <<<"$candidate")" "$(jq -r '.model' <<<"$candidate")" "$(jq -r '.effort' <<<"$candidate")"
done
quant_json="$($QUANT_STATE begin-iteration)"; iteration="$(jq -r '.iteration' <<<"$quant_json")"; [[ "$iteration" =~ ^[1-9][0-9]*$ ]] || die 'invalid iteration'
canonical_prompt="$(<"$prompt_file")"
base_prompt="Quant iteration $iteration was already recorded mechanically by the terminal launcher. Do not call begin-iteration and do not increment it again. Execute exactly this iteration.\n\n$canonical_prompt"
run_dir="$ROOT_DIR/.ops/runtime/phase-agents/quant-runs/iteration-$iteration"; mkdir -p -- "$run_dir"
continuation=false; last_status=1; attempt=0
for ((index=0; index<count; index++)); do
  candidate="$(jq -c ".[$index]" <<<"$candidates")"; provider="$(jq -r '.provider' <<<"$candidate")"; model="$(jq -r '.model' <<<"$candidate")"; effort="$(jq -r '.effort' <<<"$candidate")"
  agent_json="$($STATE state)"; mode="$(jq -r '.phases.quant_research.mode' <<<"$agent_json")"; pinned="$(jq -r '.phases.quant_research.pinned_provider//empty' <<<"$agent_json")"
  if [[ -z "${PHASE_AGENT_QUANT_RESEARCH_PROVIDER:-}" && "$mode" = manual && "$pinned" != "$provider" ]]; then continue; fi
  available="$(jq -r --arg provider "$provider" '.providers[$provider].available' <<<"$agent_json")"
  if [[ "$available" != true && -x "$DETECTOR" ]] && "$STATE" probe-due "$provider" >/dev/null 2>&1; then "$DETECTOR" "$provider" >/dev/null 2>&1 || :; available="$("$STATE" state | jq -r --arg provider "$provider" '.providers[$provider].available')"; fi
  [[ "$available" = true ]] || continue
  attempt=$((attempt+1)); base="$run_dir/attempt-$attempt-$provider"; prompt="$base_prompt"
  if [[ "$continuation" = true ]]; then prompt="Continue quant iteration $iteration after provider quota interruption. Preserve existing research artifacts and do not restart, reschedule, or increment the iteration.\n\n$base_prompt"; fi
  set +e
  if [[ "$provider" = claude ]]; then
    (cd -- "$ROOT_DIR" && timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" claude --print --model "$model" --effort "$effort" --dangerously-skip-permissions --output-format stream-json --verbose --no-session-persistence <<<"$prompt") >"$base.stdout.jsonl" 2>"$base.stderr.log"
    status=$?; classifier="$CLAUDE_CLASSIFIER"
  else
    timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" codex exec --ignore-user-config --model "$model" --config "model_reasoning_effort=\"$effort\"" --cd "$ROOT_DIR" --ephemeral --dangerously-bypass-approvals-and-sandbox --json - <<<"$prompt" >"$base.stdout.jsonl" 2>"$base.stderr.log"
    status=$?; classifier="$CODEX_CLASSIFIER"
  fi
  set -e
  last_status="$status"; result="$($classifier "$status" "$base.stdout.jsonl" "$base.stderr.log")"; printf '%s\n' "$status" >"$base.exit"; printf '%s\n' "$result" >"$base.result-class"
  jq -n --argjson iteration "$iteration" --argjson attempt "$attempt" --arg provider "$provider" --arg model "$model" --arg effort "$effort" --argjson continuation "$continuation" --arg result "$result" \
    '{iteration:$iteration,attempt:$attempt,provider:$provider,model:$model,effort:$effort,continuation:$continuation,result_class:$result}' >"$base.meta.json"
  case "$result" in success) "$STATE" provider-result "$provider" success >/dev/null; printf 'Quant iteration %s completed with %s\n' "$iteration" "$provider"; exit 0 ;;
    global-quota-exhausted|auth-error) "$STATE" provider-result "$provider" "$result" >/dev/null; continuation=true ;;
    model-unavailable|model-specific-limit) continuation=true ;;
    *) exit "$status" ;;
  esac
done
die "no eligible candidate completed quant iteration $iteration (last status $last_status)"
