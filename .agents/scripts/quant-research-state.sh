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
Usage: quant-research-state.sh <init|state|codex-off|codex-on|begin-iteration>
EOF
  exit 2
}

command -v jq >/dev/null 2>&1 || die 'jq is required'

state_schema=''
read -r -d '' state_schema <<'JQ' || true
  type == "object"
  and .schema_version == 1
  and (.codex_available | type) == "boolean"
  and (.research_enabled | type) == "boolean"
  and (.iteration | type) == "number"
  and (.iteration >= 0)
  and (.iteration | floor) == .iteration
  and ((.last_run_at == null) or ((.last_run_at | type) == "string"))
  and ((.updated_at == null) or ((.updated_at | type) == "string"))
JQ

timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

validate_file() {
  local file="$1"
  [[ -f "$file" ]] || die "state file is not a regular file: $file"
  jq -e "$state_schema" "$file" >/dev/null \
    || die "state file failed schema validation: $file"
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

default_state() {
  jq -cn '{
    schema_version: 1,
    codex_available: true,
    research_enabled: true,
    iteration: 0,
    last_run_at: null,
    updated_at: null
  }'
}

write_state() {
  local json="$1"
  local tmp
  tmp="$(mktemp "$STATE_DIR/.state.XXXXXX")"
  if ! printf '%s\n' "$json" | jq -e "if ($state_schema) then . else error(\"schema validation failed\") end" >"$tmp"; then
    rm -f -- "$tmp"
    die 'refusing to write state that fails schema validation'
  fi
  mv -f -- "$tmp" "$STATE_FILE"
}

ensure_state() {
  if [[ -e "$STATE_FILE" ]]; then
    validate_file "$STATE_FILE"
  else
    write_state "$(default_state)"
  fi
}

print_state() {
  cat -- "$STATE_FILE"
}

init_state() {
  acquire_lock
  ensure_state
  print_state
}

toggle_codex() {
  local value="$1"
  local now
  acquire_lock
  ensure_state
  now="$(timestamp)"
  write_state "$(jq -c --argjson available "$value" --arg now "$now" \
    '.codex_available = $available | .updated_at = $now' "$STATE_FILE")"
  print_state
}

begin_iteration() {
  local now
  acquire_lock
  ensure_state
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
  codex-off)
    [[ "$#" -eq 1 ]] || usage
    toggle_codex false
    ;;
  codex-on)
    [[ "$#" -eq 1 ]] || usage
    toggle_codex true
    ;;
  begin-iteration)
    [[ "$#" -eq 1 ]] || usage
    begin_iteration
    ;;
  *)
    usage
    ;;
esac
