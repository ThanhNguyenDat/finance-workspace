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
  ops-runtime.sh init <change> <session-id> [backend] [origin]
  ops-runtime.sh unlock <change> <session-id>
  ops-runtime.sh lock-repos <change> <session-id> <repository>...
  ops-runtime.sh unlock-repos <change> <session-id>
  ops-runtime.sh cleanup <change> <session-id> <FAILED|BLOCKED>
  ops-runtime.sh assert-repo-lock <change> <session-id> <repository>
  ops-runtime.sh phase <change> <session-id> <next-phase>
  ops-runtime.sh fix <change> <session-id>
  ops-runtime.sh route <change> <session-id> <IMPLEMENT|FIX>
  ops-runtime.sh trace-origin <change> <session-id> <research-iteration> <instrument> <research-artifact>...
  ops-runtime.sh state <change>
  ops-runtime.sh active <workspace-root> [session-id]
  ops-runtime.sh complete <change> <session-id>
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
    PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY|RELEASE|DEPLOY_VERIFY|ARCHIVE)
      return 0 ;;
    *) return 1 ;;
  esac
}

valid_transition() {
  case "$1:$2" in
    PLAN:IMPLEMENT|IMPLEMENT:VERIFY|VERIFY:FINAL_VERIFY|FIX:VERIFY|\
    FINAL_VERIFY:RELEASE|FINAL_VERIFY:ARCHIVE|RELEASE:DEPLOY_VERIFY|\
    RELEASE:ARCHIVE|DEPLOY_VERIFY:ARCHIVE)
      return 0 ;;
    *) return 1 ;;
  esac
}

now_utc() {
  date -u +'%Y-%m-%dT%H:%M:%SZ'
}

valid_backend() {
  case "$1" in
    codex|claude-fallback) return 0 ;;
    *) return 1 ;;
  esac
}

quant_state_file() {
  printf '%s/.ops/runtime/quant-research/state.json' "$ROOT_DIR"
}

fallback_is_allowed() {
  local quant_state
  quant_state="$(quant_state_file)"
  [ -f "$quant_state" ] || die "quant state not found: $quant_state"
  jq -e '.codex_available == false' "$quant_state" >/dev/null \
    || die 'Claude fallback requires current quant state codex_available=false'
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
  local backend="${3:-codex}"
  local origin="${4:-}"
  local dir state handoff verification_mode
  dir="$(change_dir "$change")"
  state="$dir/runtime/state.json"
  handoff="$dir/handoff.md"
  [ -n "$session_id" ] || die 'session id is required'
  valid_backend "$backend" || die "invalid implementation backend: $backend"
  case "$backend:$origin" in
    codex:)
      verification_mode='independent'
      ;;
    claude-fallback:quant-fallback)
      fallback_is_allowed
      verification_mode='claude-fallback-self-review'
      ;;
    claude-fallback:*)
      die 'Claude fallback requires explicit quant-fallback origin'
      ;;
    *)
      die 'backend origin is invalid'
      ;;
  esac
  [ -f "$dir/runtime/lock/owner.json" ] || die 'change must be locked before initialization'
  [ "$(jq -r '.session_id // empty' "$dir/runtime/lock/owner.json")" = "$session_id" ] \
    || die 'initialization lock is owned by another session'
  [ ! -e "$state" ] || die "runtime state already exists: $state"
  mkdir -p -- "$dir/runtime/logs"
  jq -n \
    --arg change "$change" \
    --arg session_id "$session_id" \
    --arg implementation_backend "$backend" \
    --arg verification_mode "$verification_mode" \
    --arg updated_at "$(now_utc)" \
    '{change: $change, phase: "PLAN", round: 0, status: "running", session_id: $session_id, implementation_backend: $implementation_backend, verification_mode: $verification_mode, updated_at: $updated_at}' \
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

assert_active_change_owner() {
  local change="$1"
  local session_id="$2"
  local dir state owner owner_session phase status backend verification_mode
  dir="$(change_dir "$change")"
  state="$dir/runtime/state.json"
  owner="$dir/runtime/lock/owner.json"
  [ -f "$state" ] || die "runtime state not found: $state"
  [ -f "$owner" ] || die "change lock owner metadata missing: $owner"
  owner_session="$(jq -r '.session_id // empty' "$owner")"
  [ "$owner_session" = "$session_id" ] || die 'change lock is owned by another session'
  phase="$(jq -r '.phase // empty' "$state")"
  status="$(jq -r '.status // empty' "$state")"
  [ "$status" = running ] || die "change is not active: $change"
  case "$phase" in BLOCKED|FAILED) die "change is terminal: $change" ;; esac
  [ "$(jq -r '.session_id // empty' "$state")" = "$session_id" ] \
    || die 'runtime state is owned by another session'
  backend="$(jq -r '.implementation_backend // "codex"' "$state")"
  verification_mode="$(jq -r '.verification_mode // "independent"' "$state")"
  valid_backend "$backend" || die 'runtime state has an invalid implementation backend'
  case "$backend:$verification_mode" in
    codex:independent|claude-fallback:claude-fallback-self-review) ;;
    *) die 'runtime state has an invalid verification mode for its backend' ;;
  esac
}

assert_repo_lock() {
  local change="$1"
  local session_id="$2"
  local repository="$3"
  local canonical owner
  assert_active_change_owner "$change" "$session_id"
  canonical="$(canonical_repo "$repository")"
  owner="$(repo_lock_dir "$canonical")/owner.json"
  [ -f "$owner" ] || die "repository lock not found: $canonical"
  jq -e \
    --arg change "$change" \
    --arg session_id "$session_id" \
    --arg repository "$canonical" \
    '(.change == $change) and (.session_id == $session_id) and (.repository == $repository)' \
    "$owner" >/dev/null \
    || die "repository lock is not owned by this change/session: $canonical"
}

lock_repositories() {
  local change="$1"
  local session_id="$2"
  shift 2
  local repository canonical lock owner
  local -a repositories=()
  [ "$#" -gt 0 ] || die 'at least one repository is required'
  [ -n "$session_id" ] || die 'session id is required'
  assert_active_change_owner "$change" "$session_id"
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
  local session_id="$2"
  local phase="$3"
  local state current
  state="$(state_file "$change")"
  valid_phase "$phase" || die "invalid phase: $phase"
  [ -f "$state" ] || die "runtime state not found: $state"
  assert_active_change_owner "$change" "$session_id"
  current="$(jq -r '.phase' "$state")"
  valid_transition "$current" "$phase" || die "invalid phase transition: $current -> $phase"
  jq \
    --arg phase "$phase" \
    --arg updated_at "$(now_utc)" \
    '.phase = $phase
    | .status = "running"
    | .updated_at = $updated_at' \
    "$state" | atomic_write_state "$state"
}

set_terminal_phase() {
  local change="$1"
  local session_id="$2"
  local phase="$3"
  local state
  case "$phase" in BLOCKED|FAILED) ;; *) die 'invalid terminal phase' ;; esac
  state="$(state_file "$change")"
  [ -f "$state" ] || die "runtime state not found: $state"
  assert_active_change_owner "$change" "$session_id"
  jq --arg phase "$phase" --arg updated_at "$(now_utc)" \
    '.phase = $phase | .status = "terminal" | .updated_at = $updated_at' \
    "$state" | atomic_write_state "$state"
}

cleanup_change() {
  local change="$1"
  local session_id="$2"
  local phase="$3"
  case "$phase" in BLOCKED|FAILED) ;; *) die 'cleanup accepts only BLOCKED or FAILED' ;; esac
  assert_active_change_owner "$change" "$session_id"
  set_terminal_phase "$change" "$session_id" "$phase"
  release_repo_locks "$change" "$session_id"
  if [ -d "$(change_dir "$change")/runtime/lock" ]; then
    unlock_change "$change" "$session_id"
  fi
}

enter_fix() {
  local change="$1"
  local session_id="$2"
  local state current_phase current_round max next_round
  state="$(state_file "$change")"
  [ -f "$state" ] || die "runtime state not found: $state"
  assert_active_change_owner "$change" "$session_id"
  current_phase="$(jq -r '.phase' "$state")"
  case "$current_phase" in
    VERIFY|RELEASE|DEPLOY_VERIFY) ;;
    *) die "FIX cannot start from phase: $current_phase" ;;
  esac
  max="$OPS_MAX_FIX_ROUNDS"
  [[ "$max" =~ ^[1-9][0-9]*$ ]] || die 'OPS_MAX_FIX_ROUNDS must be a positive integer'
  current_round="$(jq -r '.round // empty' "$state")"
  [[ "$current_round" =~ ^[0-9]+$ ]] || die 'runtime fix round is invalid'
  if [ "$current_round" -ge "$max" ]; then
    set_terminal_phase "$change" "$session_id" BLOCKED
    release_repo_locks "$change" "$session_id"
    if [ -d "$(change_dir "$change")/runtime/lock" ]; then
      unlock_change "$change" "$session_id"
    fi
    printf 'ops-runtime: maximum fix rounds (%s) reached; workflow blocked\n' "$max" >&2
    return 1
  fi
  next_round=$((current_round + 1))
  jq --arg updated_at "$(now_utc)" --argjson round "$next_round" \
    '.phase = "FIX"
    | .round = $round
    | .status = "running"
    | .updated_at = $updated_at' "$state" | atomic_write_state "$state"
}

route_phase() {
  local change="$1"
  local session_id="$2"
  local phase="$3"
  local state current_phase backend
  case "$phase" in IMPLEMENT|FIX) ;; *) die "invalid route phase: $phase" ;; esac
  state="$(state_file "$change")"
  [ -f "$state" ] || die "runtime state not found: $state"
  assert_active_change_owner "$change" "$session_id"
  current_phase="$(jq -r '.phase' "$state")"
  [ "$current_phase" = "$phase" ] || die "runtime phase is $current_phase, requested route phase is $phase"
  backend="$(jq -r '.implementation_backend // "codex"' "$state")"
  valid_backend "$backend" || die 'runtime state has an invalid implementation backend'
  printf '%s\n' "$backend"
}

trace_quant_origin() {
  local change="$1"
  local session_id="$2"
  local research_iteration="$3"
  local instrument="$4"
  shift 4
  local dir state origin_file artifact resolved root_canonical artifacts_json
  local -a artifacts=("$@")
  [ "${#artifacts[@]}" -gt 0 ] || die 'at least one research artifact is required'
  [[ "$research_iteration" =~ ^[1-9][0-9]*$ ]] \
    || die 'research iteration must be a positive integer'
  [[ "$instrument" =~ ^[A-Z][A-Z0-9_-]{0,15}$ ]] \
    || die 'instrument must be a safe uppercase identifier'

  assert_active_change_owner "$change" "$session_id"
  dir="$(change_dir "$change")"
  state="$dir/runtime/state.json"
  [ "$(jq -r '.phase // empty' "$state")" = PLAN ] \
    || die 'quant origin metadata may be attached only during PLAN'
  origin_file="$dir/runtime/origin.json"
  [ ! -e "$origin_file" ] || die "quant origin metadata already exists: $origin_file"

  [ -s "$ROOT_DIR/openspec/changes/$change/proposal.md" ] \
    || die 'promoted change proposal is missing'
  [ -s "$ROOT_DIR/openspec/changes/$change/design.md" ] \
    || die 'promoted change design is missing'
  [ -s "$ROOT_DIR/openspec/changes/$change/tasks.md" ] \
    || die 'promoted change tasks are missing'
  find "$ROOT_DIR/openspec/changes/$change/specs" -type f -name '*.md' -print -quit 2>/dev/null \
    | grep -q . || die 'promoted change specs are missing'

  root_canonical="$(cd -- "$ROOT_DIR" && pwd -P)"
  for artifact in "${artifacts[@]}"; do
    [[ "$artifact" =~ ^[A-Za-z0-9._/-]+$ ]] \
      || die "research artifact path contains unsafe characters: $artifact"
    case "/$artifact/" in
      *'/../'*|*'/./'*) die "research artifact path contains traversal: $artifact" ;;
    esac
    case "$artifact" in
      raw/researcher/*|raw/explain/*|raw/reports/*) ;;
      *) die "research artifact is outside approved evidence roots: $artifact" ;;
    esac
    [ -f "$ROOT_DIR/$artifact" ] || die "research artifact not found: $artifact"
    resolved="$(realpath -e -- "$ROOT_DIR/$artifact")" \
      || die "cannot resolve research artifact: $artifact"
    case "$resolved" in
      "$root_canonical"/raw/researcher/*|"$root_canonical"/raw/explain/*|"$root_canonical"/raw/reports/*) ;;
      *) die "research artifact resolves outside approved evidence roots: $artifact" ;;
    esac
  done

  artifacts_json="$(printf '%s\n' "${artifacts[@]}" | jq -Rsc 'split("\n")[:-1]')"
  jq -n \
    --arg change "$change" \
    --arg origin quant-research \
    --argjson research_iteration "$research_iteration" \
    --arg instrument "$instrument" \
    --argjson research_artifacts "$artifacts_json" \
    '{change: $change, origin: $origin, research_iteration: $research_iteration,
      instrument: $instrument, research_artifacts: $research_artifacts}' \
    | atomic_write_state "$origin_file"
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

complete_change() {
  local change="$1"
  local session_id="$2"
  local dir archive_root destination date archived_state lock owner
  dir="$(change_dir "$change")"
  [ -d "$dir" ] || die "change directory not found: $dir"
  [ -f "$dir/runtime/state.json" ] || die "runtime state not found: $dir/runtime/state.json"
  assert_active_change_owner "$change" "$session_id"
  [ "$(jq -r '.phase' "$dir/runtime/state.json")" = ARCHIVE ] \
    || die 'completion requires ARCHIVE phase'
  archive_root="$OPS_DIR/archive"
  date="$(date -u +%F)"
  destination="$archive_root/${date}-${change}"
  [ ! -e "$destination" ] || die "archive destination already exists: $destination"
  mkdir -p -- "$archive_root"
  release_repo_locks "$change" "$session_id"
  mv -- "$dir" "$destination"
  archived_state="$destination/runtime/state.json"
  jq --arg updated_at "$(now_utc)" \
    '.phase = "DONE" | .status = "terminal" | .updated_at = $updated_at' \
    "$archived_state" | atomic_write_state "$archived_state"
  lock="$destination/runtime/lock"
  owner="$lock/owner.json"
  [ -f "$owner" ] || die 'completion lock owner metadata missing after archive'
  [ "$(jq -r '.session_id // empty' "$owner")" = "$session_id" ] \
    || die 'completion lock ownership changed during archive'
  unlink -- "$owner"
  rmdir -- "$lock"
  printf '%s\n' "$destination"
}

command="${1-}"
case "$command" in
  lock)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    lock_change "$2" "$3"
    ;;
  init)
    [ "$#" -ge 3 ] && [ "$#" -le 5 ] || { usage; exit 2; }
    init_change "$2" "$3" "${4:-codex}" "${5:-}"
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
  assert-repo-lock)
    [ "$#" -eq 4 ] || { usage; exit 2; }
    assert_repo_lock "$2" "$3" "$4"
    ;;
  phase)
    [ "$#" -eq 4 ] || { usage; exit 2; }
    set_phase "$2" "$3" "$4"
    ;;
  fix)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    enter_fix "$2" "$3"
    ;;
  route)
    [ "$#" -eq 4 ] || { usage; exit 2; }
    route_phase "$2" "$3" "$4"
    ;;
  trace-origin)
    [ "$#" -ge 6 ] || { usage; exit 2; }
    trace_quant_origin "$2" "$3" "$4" "$5" "${@:6}"
    ;;
  state)
    [ "$#" -eq 2 ] || { usage; exit 2; }
    cat "$(state_file "$2")"
    ;;
  active)
    [ "$#" -ge 2 ] && [ "$#" -le 3 ] || { usage; exit 2; }
    active_changes "$2" "${3-}"
    ;;
  complete|archive)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    complete_change "$2" "$3"
    ;;
  *)
    usage
    exit 2
    ;;
esac
