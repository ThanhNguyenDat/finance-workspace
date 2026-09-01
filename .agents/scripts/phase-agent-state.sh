#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
STATE_DIR="${PHASE_AGENT_STATE_DIR:-$ROOT_DIR/.ops/runtime/phase-agents}"
STATE_FILE="$STATE_DIR/state.json"
LOCK_DIR="$STATE_DIR/.lock"
LEGACY_QUANT_STATE="${PHASE_AGENT_LEGACY_QUANT_STATE:-$ROOT_DIR/.ops/runtime/quant-research/state.json}"
LEGACY_CLAUDE_STATE="${PHASE_AGENT_LEGACY_CLAUDE_STATE:-$ROOT_DIR/.ops/runtime/claude-workers/state.json}"

die() { printf 'phase-agent-state: %s\n' "$1" >&2; exit 1; }
usage() {
  cat >&2 <<'EOF'
Usage: phase-agent-state.sh <init|state|validate PROVIDER MODEL EFFORT|resolve PHASE|set PHASE PROVIDER MODEL EFFORT|candidate-set PHASE INDEX PROVIDER MODEL EFFORT|reset PHASE|reset-all|pin PHASE PROVIDER|auto PHASE|provider-on PROVIDER|provider-off PROVIDER [REASON]|provider-manual PROVIDER|provider-auto PROVIDER|provider-result PROVIDER RESULT [COOLDOWN_SECONDS]|probe-due PROVIDER>
EOF
  exit 2
}

command -v jq >/dev/null 2>&1 || die 'jq is required'

now() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
epoch_to_utc() { date -u -d "@$1" '+%Y-%m-%dT%H:%M:%SZ'; }
valid_phase() {
  case "$1" in quant_research|plan|implement|verify|fix|final_verify) return 0 ;; *) return 1 ;; esac
}
normalize_phase() {
  local value="${1//-/_}"
  valid_phase "$value" || die "unsupported phase agent: $1"
  printf '%s\n' "$value"
}
valid_provider() { case "$1" in codex|claude) return 0 ;; *) return 1 ;; esac; }
validate_candidate() {
  local provider="$1" model="$2" effort="$3"
  valid_provider "$provider" || die "unsupported provider: $provider"
  [[ "$model" =~ ^[A-Za-z0-9._:-]+$ ]] || die 'model contains unsafe characters'
  case "$provider:$effort" in
    codex:none|codex:minimal|codex:low|codex:medium|codex:high|codex:xhigh) ;;
    claude:low|claude:medium|claude:high|claude:xhigh|claude:max) ;;
    *) die "unsupported effort for $provider: $effort" ;;
  esac
  if [[ "$provider" = claude && "$model" =~ (^|[-.:])opus($|[-.:]) ]]; then
    case "$effort" in medium|high) ;; *) die 'Opus supports only medium or high by workspace policy' ;; esac
  fi
}

default_state() {
  jq -cn '{
    schema_version: 1,
    phases: {
      quant_research: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"claude",model:"sonnet",effort:"high"},
        {provider:"codex",model:"gpt-5.6-luna",effort:"high"}]},
      plan: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"claude",model:"opus",effort:"medium"},
        {provider:"codex",model:"gpt-5.6-terra",effort:"high"}]},
      implement: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"codex",model:"gpt-5.6-luna",effort:"high"},
        {provider:"claude",model:"sonnet",effort:"high"}]},
      verify: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"claude",model:"opus",effort:"medium"},
        {provider:"codex",model:"gpt-5.6-terra",effort:"high"}]},
      fix: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"codex",model:"gpt-5.6-terra",effort:"high"},
        {provider:"codex",model:"gpt-5.6-sol",effort:"high"},
        {provider:"claude",model:"opus",effort:"high"}]},
      final_verify: {mode:"auto", pinned_provider:null, candidates:[
        {provider:"claude",model:"opus",effort:"high"},
        {provider:"codex",model:"gpt-5.6-terra",effort:"high"}]}
    },
    providers: {
      codex:{mode:"auto",available:true,reason:null,observed_at:null,next_probe_at:null},
      claude:{mode:"auto",available:true,reason:null,observed_at:null,next_probe_at:null}
    },
    legacy_imported:false,
    updated_at:null
  }'
}

schema='type=="object" and .schema_version==1
  and (.phases|keys|sort)==["final_verify","fix","implement","plan","quant_research","verify"]
  and (.providers|keys|sort)==["claude","codex"]
  and all(.phases[]; . as $p |
    ($p.mode|IN("auto","manual")) and
    (($p.pinned_provider==null) or ($p.pinned_provider|IN("codex","claude"))) and
    ($p.candidates|type=="array" and length>0) and
    all($p.candidates[]; . as $c |
      ($c.provider|IN("codex","claude")) and
      ($c.model|type=="string" and test("^[A-Za-z0-9._:-]+$")) and
      (($c.provider=="codex" and ($c.effort|IN("none","minimal","low","medium","high","xhigh"))) or
       ($c.provider=="claude" and ($c.effort|IN("low","medium","high","xhigh","max")))) and
      (($c.provider!="claude" or ($c.model|test("(^|[-.:])opus($|[-.:])")|not)) or ($c.effort|IN("medium","high")))))
  and all(.providers[]; . as $p |
    ($p.mode|IN("auto","manual")) and ($p.available|type=="boolean") and
    (($p.reason==null) or ($p.reason|type=="string")) and
    (($p.observed_at==null) or ($p.observed_at|type=="string")) and
    (($p.next_probe_at==null) or ($p.next_probe_at|type=="string")))
  and (.legacy_imported|type=="boolean")
  and ((.updated_at==null) or (.updated_at|type=="string"))'

release_lock() {
  if [[ -f "$LOCK_DIR/pid" && "$(<"$LOCK_DIR/pid")" = "$$" ]]; then
    rm -rf -- "$LOCK_DIR"
  fi
}
acquire_lock() {
  mkdir -p -- "$STATE_DIR"
  if mkdir -- "$LOCK_DIR" 2>/dev/null; then
    printf '%s\n' "$$" >"$LOCK_DIR/pid"
    trap release_lock EXIT
    return
  fi
  local owner=''
  [[ ! -f "$LOCK_DIR/pid" ]] || owner="$(<"$LOCK_DIR/pid")"
  if [[ "$owner" =~ ^[0-9]+$ ]] && kill -0 "$owner" 2>/dev/null; then
    die "state mutation is locked by pid $owner"
  fi
  rm -rf -- "$LOCK_DIR"
  mkdir -- "$LOCK_DIR" 2>/dev/null || die 'could not acquire state lock'
  printf '%s\n' "$$" >"$LOCK_DIR/pid"
  trap release_lock EXIT
}
write_state() {
  local json="$1" tmp
  tmp="$(mktemp "$STATE_DIR/.state.XXXXXX")"
  if ! printf '%s\n' "$json" | jq -e "if ($schema) then . else error(\"invalid phase-agent state\") end" >"$tmp"; then
    rm -f -- "$tmp"
    die 'refusing invalid state'
  fi
  mv -f -- "$tmp" "$STATE_FILE"
}
import_legacy() {
  local state="$1"
  if [[ -f "$LEGACY_QUANT_STATE" ]] && jq -e '.codex_profiles|type=="object"' "$LEGACY_QUANT_STATE" >/dev/null 2>&1; then
    state="$(jq -c --slurpfile old "$LEGACY_QUANT_STATE" '
      .providers.codex.available=(if ($old[0]|has("codex_available")) then $old[0].codex_available else true end)
      | .phases.implement.candidates[0]=($old[0].codex_profiles.implement+{provider:"codex"})
      | .phases.fix.candidates[0]=($old[0].codex_profiles.fix+{provider:"codex"})
      | .phases.fix.candidates[1]=($old[0].codex_profiles.fix_fallback+{provider:"codex"})' <<<"$state")"
  fi
  if [[ -f "$LEGACY_CLAUDE_STATE" ]] && jq -e '.profiles|type=="object"' "$LEGACY_CLAUDE_STATE" >/dev/null 2>&1; then
    state="$(jq -c --slurpfile old "$LEGACY_CLAUDE_STATE" '
      .phases.quant_research.candidates[0]=($old[0].profiles.quant_research+{provider:"claude"})
      | .phases.plan.candidates[0]=($old[0].profiles.plan+{provider:"claude"})
      | .phases.implement.candidates[1]=($old[0].profiles.fallback_implement+{provider:"claude"})
      | .phases.verify.candidates[0]=($old[0].profiles.verify+{provider:"claude"})
      | .phases.fix.candidates[2]=($old[0].profiles.fallback_fix+{provider:"claude"})
      | .phases.final_verify.candidates[0]=($old[0].profiles.final_verify+{provider:"claude"})' <<<"$state")"
  fi
  jq -c '.legacy_imported=true' <<<"$state"
}
ensure_state() {
  if [[ ! -e "$STATE_FILE" ]]; then
    write_state "$(import_legacy "$(default_state)")"
    return
  fi
  [[ -f "$STATE_FILE" ]] || die "state is not a regular file: $STATE_FILE"
  jq -e "$schema" "$STATE_FILE" >/dev/null || die "state failed validation: $STATE_FILE"
}
with_state() { acquire_lock; ensure_state; }
mutate() {
  local filter="$1"; shift
  local updated
  updated="$(jq -c "$@" --arg now "$(now)" "$filter | .updated_at=\$now" "$STATE_FILE")"
  write_state "$updated"
}

case "${1:-}" in
  init|state)
    [[ $# -eq 1 ]] || usage; with_state; cat -- "$STATE_FILE" ;;
  validate)
    [[ $# -eq 4 ]] || usage; validate_candidate "$2" "$3" "$4" ;;
  resolve)
    [[ $# -eq 2 ]] || usage; phase="$(normalize_phase "$2")"; with_state
    jq -r --arg phase "$phase" '
      . as $root | .phases[$phase] as $p
      | [$p.candidates[] | select(.provider as $provider
          | ($p.mode!="manual" or $p.pinned_provider==$provider)
          and ($root.providers[$provider].available))][0]
      | if .==null then empty else [.provider,.model,.effort]|@tsv end' "$STATE_FILE" ;;
  set)
    [[ $# -eq 5 ]] || usage; phase="$(normalize_phase "$2")"; validate_candidate "$3" "$4" "$5"; with_state
    mutate '.phases[$phase].candidates = [{provider:$provider,model:$model,effort:$effort}] + [.phases[$phase].candidates[]|select(.provider!=$provider)]' \
      --arg phase "$phase" --arg provider "$3" --arg model "$4" --arg effort "$5" ;;
  candidate-set)
    [[ $# -eq 6 ]] || usage; phase="$(normalize_phase "$2")"; index="$3"; [[ "$index" =~ ^[0-9]+$ ]] || die 'candidate index must be non-negative'; validate_candidate "$4" "$5" "$6"; with_state
    jq -e --arg phase "$phase" --argjson index "$index" '.phases[$phase].candidates[$index]!=null' "$STATE_FILE" >/dev/null || die 'candidate index is out of range'
    mutate '.phases[$phase].candidates[$index]={provider:$provider,model:$model,effort:$effort}' --arg phase "$phase" --argjson index "$index" --arg provider "$4" --arg model "$5" --arg effort "$6" ;;
  reset)
    [[ $# -eq 2 ]] || usage; phase="$(normalize_phase "$2")"; with_state
    defaults="$(default_state)"; mutate '.phases[$phase]=$defaults.phases[$phase]' --arg phase "$phase" --argjson defaults "$defaults" ;;
  reset-all)
    [[ $# -eq 1 ]] || usage; with_state; write_state "$(jq -c '.legacy_imported=true' <<<"$(default_state)")" ;;
  pin)
    [[ $# -eq 3 ]] || usage; phase="$(normalize_phase "$2")"; valid_provider "$3" || die "unsupported provider: $3"; with_state
    jq -e --arg phase "$phase" --arg provider "$3" '.phases[$phase].candidates|any(.provider==$provider)' "$STATE_FILE" >/dev/null || die 'provider has no candidate for phase'
    mutate '.phases[$phase].mode="manual"|.phases[$phase].pinned_provider=$provider' --arg phase "$phase" --arg provider "$3" ;;
  auto)
    [[ $# -eq 2 ]] || usage; phase="$(normalize_phase "$2")"; with_state
    mutate '.phases[$phase].mode="auto"|.phases[$phase].pinned_provider=null' --arg phase "$phase" ;;
  provider-on|provider-off|provider-manual|provider-auto)
    case "$1" in provider-off) [[ $# -ge 2 && $# -le 3 ]] || usage ;; *) [[ $# -eq 2 ]] || usage ;; esac
    provider="$2"; valid_provider "$provider" || die "unsupported provider: $provider"; with_state
    case "$1" in
      provider-on) mutate '.providers[$provider]={mode:"manual",available:true,reason:null,observed_at:$now,next_probe_at:null}' --arg provider "$provider" ;;
      provider-off) reason="${3:-manual-off}"; [[ "$reason" =~ ^[A-Za-z0-9._:-]+$ ]] || die 'unsafe reason'; mutate '.providers[$provider]={mode:"manual",available:false,reason:$reason,observed_at:$now,next_probe_at:null}' --arg provider "$provider" --arg reason "$reason" ;;
      provider-manual) mutate '.providers[$provider].mode="manual"' --arg provider "$provider" ;;
      provider-auto) mutate '.providers[$provider].mode="auto"' --arg provider "$provider" ;;
    esac ;;
  provider-result)
    [[ $# -ge 3 && $# -le 4 ]] || usage; provider="$2"; result="$3"; valid_provider "$provider" || die "unsupported provider: $provider"; cooldown="${4:-3600}"; [[ "$cooldown" =~ ^[0-9]+$ ]] || die 'cooldown must be a non-negative integer'; with_state
    case "$result" in
      success) mutate '.providers[$provider].available=true|.providers[$provider].reason=null|.providers[$provider].observed_at=$now|.providers[$provider].next_probe_at=null' --arg provider "$provider" ;;
      global-quota-exhausted) next="$(epoch_to_utc "$(( $(date +%s) + cooldown ))")"; mutate '.providers[$provider].available=false|.providers[$provider].reason=$result|.providers[$provider].observed_at=$now|.providers[$provider].next_probe_at=$next' --arg provider "$provider" --arg result "$result" --arg next "$next" ;;
      auth-error) mutate '.providers[$provider].mode="manual"|.providers[$provider].available=false|.providers[$provider].reason=$result|.providers[$provider].observed_at=$now|.providers[$provider].next_probe_at=null' --arg provider "$provider" --arg result "$result" ;;
      probe-inconclusive) next="$(epoch_to_utc "$(( $(date +%s) + cooldown ))")"; mutate '.providers[$provider].observed_at=$now|.providers[$provider].next_probe_at=$next' --arg provider "$provider" --arg next "$next" ;;
      model-unavailable|model-specific-limit|transient-rate-limit|network-error|timeout|implementation-error|unknown-error) : ;;
      *) die "unsupported provider result: $result" ;;
    esac ;;
  probe-due)
    [[ $# -eq 2 ]] || usage; provider="$2"; valid_provider "$provider" || die "unsupported provider: $provider"; with_state
    jq -e --arg provider "$provider" --arg now "$(now)" '.providers[$provider] as $p|$p.mode=="auto" and ($p.available|not) and $p.next_probe_at!=null and $p.next_probe_at<=$now' "$STATE_FILE" >/dev/null ;;
  *) usage ;;
esac
