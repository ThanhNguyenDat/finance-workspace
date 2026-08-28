#!/usr/bin/env bash
set -Eeuo pipefail

# Durable per-change state plus transient change/repository ownership locks.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="${OPS_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
OPS_DIR="$ROOT_DIR/.ops"
CHANGES_DIR="$OPS_DIR/changes"
REPO_LOCKS_DIR="$OPS_DIR/runtime/repo-locks"
OPS_MAX_FIX_ROUNDS="${OPS_MAX_FIX_ROUNDS:-3}"

usage() {
  cat >&2 <<'EOF'
usage:
  ops-runtime.sh lock <change> <session-id>
  ops-runtime.sh init <change> <session-id>
  ops-runtime.sh unlock <change> <session-id>
  ops-runtime.sh lock-repos <change> <session-id> <repository>...
  ops-runtime.sh unlock-repos <change> <session-id>
  ops-runtime.sh cleanup <change> <session-id> <FAILED|BLOCKED>
  ops-runtime.sh phase <change> <phase> [round]
  ops-runtime.sh round <change> <session-id>
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
      return 0 ;;
    *) return 1 ;;
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

canonical_repo() {
  local repository="$1"
  local inside top
  [ -n "$repository" ] || die 'repository path is required'
  inside="$(git -C "$repository" rev-parse --is-inside-work-tree 2>/dev/null)" \
    || die "not a Git worktree: $repository"
  [ "$inside" = true ] || die "not a Git worktree: $repository"
  top="$(git -C "$repository" rev-parse --show-toplevel 2>/dev/null)" \
    || die "cannot resolve Git worktree: $repository"
  (cd -- "$top" && pwd -P)
}

repo_lock_dir() {
  local repository="$1"
  local key
  key="$(printf '%s' "$repository" | sha256sum | awk '{print $1}')"
  printf '%s/%s' "$REPO_LOCKS_DIR" "$key"
}

release_repo_locks() {
  local change="$1"
  local session_id="$2"
  local owner lock owner_change owner_session
  [ -d "$REPO_LOCKS_DIR" ] || return 0
  while IFS= read -r -d '' owner; do
    lock="$(dirname -- "$owner")"
    owner_change="$(jq -r '.change // empty' "$owner" 2>/dev/null || true)"
    owner_session="$(jq -r '.session_id // empty' "$owner" 2>/dev/null || true)"
    if [ "$owner_change" = "$change" ] && [ "$owner_session" = "$session_id" ]; then
      unlink -- "$owner"
      rmdir -- "$lock"
    fi
  done < <(find "$REPO_LOCKS_DIR" -mindepth 2 -maxdepth 2 -type f -name owner.json -print0)
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
    [ ! -f "$owner" ] || jq -c '{change, session_id, pid, hostname, started_at}' "$owner" >&2 || true
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
- Next: identify affected repositories and validate the OpenSpec artifacts.
EOF
  fi
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

lock_repositories() {
  local change="$1"
  local session_id="$2"
  shift 2
  local repository canonical lock owner
  local -a repositories=()
  [ "$#" -gt 0 ] || die 'at least one repository is required'
  [ -n "$session_id" ] || die 'session id is required'
  for repository in "$@"; do
    canonical="$(canonical_repo "$repository")"
    repositories+=("$canonical")
  done
  mapfile -t repositories < <(printf '%s\n' "${repositories[@]}" | sort -u)
  for canonical in "${repositories[@]}"; do
    lock="$(repo_lock_dir "$canonical")"
    owner="$lock/owner.json"
    mkdir -p -- "$(dirname -- "$lock")"
    if ! mkdir -- "$lock" 2>/dev/null; then
      printf 'ops-runtime: repository lock exists for %s\n' "$canonical" >&2
      [ ! -f "$owner" ] || jq -c '{change, session_id, repository, pid, started_at}' "$owner" >&2 || true
      release_repo_locks "$change" "$session_id"
      return 1
    fi
    jq -n \
      --arg change "$change" \
      --arg session_id "$session_id" \
      --arg repository "$canonical" \
      --arg pid "$BASHPID" \
      --arg started_at "$(now_utc)" \
      '{change: $change, session_id: $session_id, repository: $repository, pid: $pid, started_at: $started_at}' \
      >"$owner"
  done
}

unlock_repositories() {
  local change="$1"
  local session_id="$2"
  [ -n "$session_id" ] || die 'session id is required'
  release_repo_locks "$change" "$session_id"
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
    '.phase = $phase
    | .round = $round
    | .status = (if ($phase == "DONE" or $phase == "BLOCKED" or $phase == "FAILED") then "terminal" else "running" end)
    | .updated_at = $updated_at' \
    "$state" | atomic_write_state "$state"
}

cleanup_change() {
  local change="$1"
  local session_id="$2"
  local phase="$3"
  valid_phase "$phase" || die "invalid cleanup phase: $phase"
  if [ -f "$(state_file "$change")" ]; then
    set_phase "$change" "$phase"
  fi
  release_repo_locks "$change" "$session_id"
  if [ -d "$(change_dir "$change")/runtime/lock" ]; then
    unlock_change "$change" "$session_id"
  fi
}

bump_round() {
  local change="$1"
  local session_id="$2"
  local state current max
  state="$(state_file "$change")"
  [ -f "$state" ] || die "runtime state not found: $state"
  max="$OPS_MAX_FIX_ROUNDS"
  [[ "$max" =~ ^[1-9][0-9]*$ ]] || die 'OPS_MAX_FIX_ROUNDS must be a positive integer'
  current="$(jq -r '.round' "$state")"
  if [ "$current" -ge "$max" ]; then
    set_phase "$change" BLOCKED "$current"
    release_repo_locks "$change" "$session_id"
    if [ -d "$(change_dir "$change")/runtime/lock" ]; then
      unlock_change "$change" "$session_id"
    fi
    printf 'ops-runtime: maximum fix rounds (%s) reached; workflow blocked\n' "$max" >&2
    return 1
  fi
  current=$((current + 1))
  jq --arg updated_at "$(now_utc)" --argjson round "$current" \
    '.round = $round | .updated_at = $updated_at' "$state" | atomic_write_state "$state"
  printf '%s\n' "$current"
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
  lock)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    lock_change "$2" "$3"
    ;;
  init)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    init_change "$2" "$3"
    ;;
  unlock)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    unlock_change "$2" "$3"
    ;;
  lock-repos)
    [ "$#" -ge 4 ] || { usage; exit 2; }
    lock_repositories "$2" "$3" "${@:4}"
    ;;
  unlock-repos)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    unlock_repositories "$2" "$3"
    ;;
  cleanup)
    [ "$#" -eq 4 ] || { usage; exit 2; }
    cleanup_change "$2" "$3" "$4"
    ;;
  phase)
    [ "$#" -ge 3 ] && [ "$#" -le 4 ] || { usage; exit 2; }
    set_phase "$2" "$3" "${4-}"
    ;;
  round)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    bump_round "$2" "$3"
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
