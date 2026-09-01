#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
STATE_DIR="${QUANT_RESEARCH_STATE_DIR:-$ROOT_DIR/.ops/runtime/quant-research}"
STATE_FILE="$STATE_DIR/state.json"
LOCK_DIR="$STATE_DIR/.lock"

die() {
  printf 'quant-research-state: %s\n' "$1" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
Usage: quant-research-state.sh <init|state|codex-auto|codex-manual|codex-off|codex-on|codex-worker-off|codex-detected-off|codex-detected-on|profile-get ROLE|profile-set ROLE MODEL EFFORT|profile-reset ROLE|profiles-reset|begin-iteration>
EOF
  exit 2
}

command -v jq >/dev/null 2>&1 || die 'jq is required'

read -r -d '' common_schema <<'JQ' || true
  and (.codex_available | type) == "boolean"
  and (.research_enabled | type) == "boolean"
  and (.iteration | type) == "number"
  and (.iteration >= 0)
  and (.iteration | floor) == .iteration
  and ((.last_run_at == null) or ((.last_run_at | type) == "string"))
  and ((.updated_at == null) or ((.updated_at | type) == "string"))
JQ

read -r -d '' v1_schema <<JQ || true
  type == "object"
  and .schema_version == 1
  $common_schema
JQ

read -r -d '' profile_schema <<'JQ' || true
  type == "object"
  and (.model | type) == "string"
  and (.model | test("^[A-Za-z0-9._:-]+$"))
  and (.effort | IN("none", "minimal", "low", "medium", "high", "xhigh"))
JQ

read -r -d '' v2_schema <<JQ || true
  type == "object"
  and .schema_version == 2
  and (.codex_mode | IN("auto", "manual"))
  and (.codex_profiles | type) == "object"
  and (.codex_profiles | keys | sort) == ["fix", "fix_fallback", "implement", "probe"]
  and (.codex_profiles.probe | $profile_schema)
  and (.codex_profiles.implement | $profile_schema)
  and (.codex_profiles.fix | $profile_schema)
  and (.codex_profiles.fix_fallback | $profile_schema)
  $common_schema
JQ

timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

default_profiles() {
  jq -cn '{
    probe: {model: "gpt-5.6-luna", effort: "high"},
    implement: {model: "gpt-5.6-luna", effort: "high"},
    fix: {model: "gpt-5.6-terra", effort: "high"},
    fix_fallback: {model: "gpt-5.6-sol", effort: "high"}
  }'
}

default_state() {
  jq -cn --argjson profiles "$(default_profiles)" '{
    schema_version: 2,
    codex_mode: "manual",
    codex_available: true,
    codex_profiles: $profiles,
    research_enabled: true,
    iteration: 0,
    last_run_at: null,
    updated_at: null
  }'
}

release_lock() {
  if [[ -f "$LOCK_DIR/pid" ]] && [[ "$(cat -- "$LOCK_DIR/pid")" == "$$" ]]; then
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

  local owner_pid=''
  if [[ -f "$LOCK_DIR/pid" ]]; then
    owner_pid="$(cat -- "$LOCK_DIR/pid")"
  fi
  if [[ "$owner_pid" =~ ^[0-9]+$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
    die "state mutation is already locked by pid $owner_pid"
  fi

  rm -rf -- "$LOCK_DIR"
  mkdir -- "$LOCK_DIR" 2>/dev/null || die 'could not acquire state mutation lock'
  printf '%s\n' "$$" >"$LOCK_DIR/pid"
  trap release_lock EXIT
}

write_state() {
  local json="$1" tmp
  tmp="$(mktemp "$STATE_DIR/.state.XXXXXX")"
  if ! printf '%s\n' "$json" | jq -e "if ($v2_schema) then . else error(\"schema validation failed\") end" >"$tmp"; then
    rm -f -- "$tmp"
    die 'refusing to write state that fails schema validation'
  fi
  mv -f -- "$tmp" "$STATE_FILE"
}

ensure_state() {
  if [[ ! -e "$STATE_FILE" ]]; then
    write_state "$(default_state)"
    return
  fi
  [[ -f "$STATE_FILE" ]] || die "state file is not a regular file: $STATE_FILE"
  if jq -e "$v2_schema" "$STATE_FILE" >/dev/null 2>&1; then
    return
  fi
  if jq -e "$v1_schema" "$STATE_FILE" >/dev/null 2>&1; then
    write_state "$(jq -c --argjson profiles "$(default_profiles)" \
      '.schema_version = 2 | .codex_mode = "manual" | .codex_profiles = $profiles' "$STATE_FILE")"
    return
  fi
  die "state file failed schema validation: $STATE_FILE"
}

with_state() {
  acquire_lock
  ensure_state
}

print_state() {
  cat -- "$STATE_FILE"
}

init_state() {
  with_state
  print_state
}

set_mode() {
  local mode="$1" now
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --arg mode "$mode" --arg now "$now" \
    '.codex_mode = $mode | .updated_at = $now' "$STATE_FILE")"
  print_state
}

set_manual_availability() {
  local value="$1" now
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --argjson available "$value" --arg now "$now" \
    '.codex_mode = "manual" | .codex_available = $available | .updated_at = $now' "$STATE_FILE")"
  print_state
}

set_resolved_availability() {
  local value="$1" require_auto="$2" now
  with_state
  if [[ "$require_auto" = true ]] && [[ "$(jq -r '.codex_mode' "$STATE_FILE")" != auto ]]; then
    die 'automatic detection result is stale because manual mode is selected'
  fi
  now="$(timestamp)"
  write_state "$(jq -c --argjson available "$value" --arg now "$now" \
    '.codex_available = $available | .updated_at = $now' "$STATE_FILE")"
  print_state
}

normalize_role() {
  case "$1" in
    probe|implement|fix) printf '%s\n' "$1" ;;
    fix-fallback|fix_fallback) printf '%s\n' fix_fallback ;;
    *) die "unsupported Codex profile role: $1" ;;
  esac
}

validate_model() {
  [[ "$1" =~ ^[A-Za-z0-9._:-]+$ ]] || die 'model must contain only safe identifier characters'
}

validate_effort() {
  case "$1" in none|minimal|low|medium|high|xhigh) ;; *) die "unsupported reasoning effort: $1" ;; esac
}

profile_get() {
  local role
  role="$(normalize_role "$1")"
  with_state
  jq -r --arg role "$role" '.codex_profiles[$role] | [.model, .effort] | @tsv' "$STATE_FILE"
}

profile_set() {
  local role model="$2" effort="$3" now
  role="$(normalize_role "$1")"
  validate_model "$model"
  validate_effort "$effort"
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --arg role "$role" --arg model "$model" --arg effort "$effort" --arg now "$now" \
    '.codex_profiles[$role] = {model: $model, effort: $effort} | .updated_at = $now' "$STATE_FILE")"
  jq -r --arg role "$role" '.codex_profiles[$role] | [.model, .effort] | @tsv' "$STATE_FILE"
}

profile_reset() {
  local role now
  role="$(normalize_role "$1")"
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --arg role "$role" --argjson defaults "$(default_profiles)" --arg now "$now" \
    '.codex_profiles[$role] = $defaults[$role] | .updated_at = $now' "$STATE_FILE")"
  jq -r --arg role "$role" '.codex_profiles[$role] | [.model, .effort] | @tsv' "$STATE_FILE"
}

profiles_reset() {
  local now
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --argjson defaults "$(default_profiles)" --arg now "$now" \
    '.codex_profiles = $defaults | .updated_at = $now' "$STATE_FILE")"
  print_state
}

begin_iteration() {
  local now
  with_state
  now="$(timestamp)"
  write_state "$(jq -c --arg now "$now" \
    '.iteration += 1 | .last_run_at = $now | .updated_at = $now' "$STATE_FILE")"
  print_state
}

case "${1:-}" in
  init|state)
    [[ "$#" -eq 1 ]] || usage
    init_state
    ;;
  codex-auto)
    [[ "$#" -eq 1 ]] || usage
    set_mode auto
    ;;
  codex-manual)
    [[ "$#" -eq 1 ]] || usage
    set_mode manual
    ;;
  codex-off)
    [[ "$#" -eq 1 ]] || usage
    set_manual_availability false
    ;;
  codex-on)
    [[ "$#" -eq 1 ]] || usage
    set_manual_availability true
    ;;
  codex-worker-off)
    [[ "$#" -eq 1 ]] || usage
    set_resolved_availability false false
    ;;
  codex-detected-off)
    [[ "$#" -eq 1 ]] || usage
    set_resolved_availability false true
    ;;
  codex-detected-on)
    [[ "$#" -eq 1 ]] || usage
    set_resolved_availability true true
    ;;
  profile-get)
    [[ "$#" -eq 2 ]] || usage
    profile_get "$2"
    ;;
  profile-set)
    [[ "$#" -eq 4 ]] || usage
    profile_set "$2" "$3" "$4"
    ;;
  profile-reset)
    [[ "$#" -eq 2 ]] || usage
    profile_reset "$2"
    ;;
  profiles-reset)
    [[ "$#" -eq 1 ]] || usage
    profiles_reset
    ;;
  begin-iteration)
    [[ "$#" -eq 1 ]] || usage
    begin_iteration
    ;;
  *)
    usage
    ;;
esac
