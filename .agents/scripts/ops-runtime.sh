#!/usr/bin/env bash
set -Eeuo pipefail

# Runtime state for the per-change /ops:run orchestration.
# The state directory is intentionally outside Git's tracked source model.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="${OPS_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
OPS_DIR="$ROOT_DIR/.ops"
CHANGES_DIR="$OPS_DIR/changes"

usage() {
  cat >&2 <<'EOF'
usage:
  ops-runtime.sh init <change> <session-id>
  ops-runtime.sh lock <change> <session-id>
  ops-runtime.sh unlock <change> <session-id>
  ops-runtime.sh phase <change> <phase> [round]
  ops-runtime.sh round <change>
  ops-runtime.sh state <change>
  ops-runtime.sh active <workspace-root> [session-id]
  ops-runtime.sh archive <change>
EOF
}

die() {
  printf 'ops-runtime: %s\n' "$1" >&2
  exit 1
}

valid_change() {
  [[ "$1" =~ ^[a-z0-9][a-z0-9-]*$ ]]
}

change_dir() {
  local change="$1"
  valid_change "$change" || die "invalid change name: $change"
  printf '%s/%s' "$CHANGES_DIR" "$change"
}

state_file() {
  printf '%s/runtime/state.json' "$(change_dir "$1")"
}

valid_phase() {
  case "$1" in
    PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY|RELEASE|DEPLOY_VERIFY|ARCHIVE|DONE|BLOCKED|FAILED)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

now_utc() {
  date -u +'%Y-%m-%dT%H:%M:%SZ'
}

atomic_write_state() {
  local file="$1"
  local tmp
  tmp="$(mktemp "${file}.tmp.XXXXXX")"
  cat >"$tmp"
  mv -- "$tmp" "$file"
}

init_change() {
  local change="$1"
  local session_id="$2"
  local dir state handoff
  dir="$(change_dir "$change")"
  state="$dir/runtime/state.json"
  handoff="$dir/handoff.md"
  [ -n "$session_id" ] || die 'session id is required'
  [ -f "$dir/runtime/lock/owner.json" ] || die 'change must be locked before initialization'
  [ "$(jq -r '.session_id // empty' "$dir/runtime/lock/owner.json")" = "$session_id" ] \
    || die 'initialization lock is owned by another session'
  [ ! -e "$state" ] || die "runtime state already exists: $state"

  mkdir -p -- "$dir/runtime/logs"
  jq -n \
    --arg change "$change" \
    --arg session_id "$session_id" \
    --arg updated_at "$(now_utc)" \
    '{change: $change, phase: "PLAN", round: 0, status: "running", session_id: $session_id, updated_at: $updated_at}' \
    | atomic_write_state "$state"

  if [ ! -e "$handoff" ]; then
    cat >"$handoff" <<EOF
# $change

- Claude: workflow initialized; planning pending.
- Next: create and validate the OpenSpec artifacts.
EOF
  fi
}

lock_change() {
  local change="$1"
  local session_id="$2"
  local dir lock owner
  dir="$(change_dir "$change")"
  lock="$dir/runtime/lock"
  owner="$lock/owner.json"
  [ -n "$session_id" ] || die 'session id is required'

  mkdir -p -- "$dir/runtime/logs"

  if ! mkdir -- "$lock" 2>/dev/null; then
    printf 'ops-runtime: active lock exists: %s\n' "$lock" >&2
    if [ -f "$owner" ]; then
      jq -c '{change, session_id, pid, hostname, started_at}' "$owner" >&2 || true
    fi
    return 1
  fi

  jq -n \
    --arg change "$change" \
    --arg session_id "$session_id" \
    --arg pid "$BASHPID" \
    --arg hostname "$(hostname)" \
    --arg started_at "$(now_utc)" \
    '{change: $change, session_id: $session_id, pid: $pid, hostname: $hostname, started_at: $started_at}' \
    >"$owner"
}

unlock_change() {
  local change="$1"
  local session_id="$2"
  local dir lock owner owner_session
  dir="$(change_dir "$change")"
  lock="$dir/runtime/lock"
  owner="$lock/owner.json"
  [ -d "$lock" ] || die "lock not found: $lock"
  [ -f "$owner" ] || die "lock owner metadata missing: $owner"
  owner_session="$(jq -r '.session_id // empty' "$owner")"
  [ "$owner_session" = "$session_id" ] || die 'lock is owned by another session'
  unlink -- "$owner"
  rmdir -- "$lock"
}

set_phase() {
  local change="$1"
  local phase="$2"
  local requested_round="${3-}"
  local state
  state="$(state_file "$change")"
  valid_phase "$phase" || die "invalid phase: $phase"
  [ -f "$state" ] || die "runtime state not found: $state"

  jq \
    --arg phase "$phase" \
    --arg updated_at "$(now_utc)" \
    --argjson round "${requested_round:-$(jq -r '.round' "$state")}" \
    ' .phase = $phase
    | .round = $round
    | .status = (if ($phase == "DONE" or $phase == "BLOCKED" or $phase == "FAILED") then "terminal" else "running" end)
    | .updated_at = $updated_at' \
    "$state" | atomic_write_state "$state"
}

bump_round() {
  local change="$1"
  local state
  state="$(state_file "$change")"
  [ -f "$state" ] || die "runtime state not found: $state"
  jq --arg updated_at "$(now_utc)" '.round += 1 | .updated_at = $updated_at' "$state" \
    | atomic_write_state "$state"
  jq -r '.round' "$state"
}

active_changes() {
  local root="$1"
  local session_id="${2-}"
  local file change phase round
  [ -d "$root/.ops/changes" ] || return 0
  while IFS= read -r -d '' file; do
    if jq -e --arg session_id "$session_id" '
      (.status == "running")
      and (.phase != "DONE" and .phase != "BLOCKED" and .phase != "FAILED")
      and ($session_id == "" or .session_id == $session_id)
    ' "$file" >/dev/null; then
      change="$(jq -r '.change' "$file")"
      phase="$(jq -r '.phase' "$file")"
      round="$(jq -r '.round' "$file")"
      printf '%s|%s|%s\n' "$change" "$phase" "$round"
    fi
  done < <(find "$root/.ops/changes" -mindepth 3 -maxdepth 3 -type f -name state.json -print0)
}

archive_change() {
  local change="$1"
  local dir archive_root destination date archived_state
  dir="$(change_dir "$change")"
  [ -d "$dir" ] || die "change directory not found: $dir"
  [ -f "$dir/runtime/state.json" ] || die "runtime state not found: $dir/runtime/state.json"
  [ ! -d "$dir/runtime/lock" ] || die 'cannot archive a locked change'
  archive_root="$OPS_DIR/archive"
  date="$(date -u +%F)"
  destination="$archive_root/${date}-${change}"
  [ ! -e "$destination" ] || die "archive destination already exists: $destination"
  mkdir -p -- "$archive_root"
  mv -- "$dir" "$destination"
  archived_state="$destination/runtime/state.json"
  jq --arg updated_at "$(now_utc)" \
    '.phase = "DONE" | .status = "terminal" | .updated_at = $updated_at' \
    "$archived_state" | atomic_write_state "$archived_state"
  printf '%s\n' "$destination"
}

command="${1-}"
case "$command" in
  init)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    init_change "$2" "$3"
    ;;
  lock)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    lock_change "$2" "$3"
    ;;
  unlock)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    unlock_change "$2" "$3"
    ;;
  phase)
    [ "$#" -ge 3 ] && [ "$#" -le 4 ] || { usage; exit 2; }
    set_phase "$2" "$3" "${4-}"
    ;;
  round)
    [ "$#" -eq 2 ] || { usage; exit 2; }
    bump_round "$2"
    ;;
  state)
    [ "$#" -eq 2 ] || { usage; exit 2; }
    cat "$(state_file "$2")"
    ;;
  active)
    [ "$#" -ge 2 ] && [ "$#" -le 3 ] || { usage; exit 2; }
    active_changes "$2" "${3-}"
    ;;
  archive)
    [ "$#" -eq 2 ] || { usage; exit 2; }
    archive_change "$2"
    ;;
  *)
    usage
    exit 2
    ;;
esac
