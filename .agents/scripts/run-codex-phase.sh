#!/usr/bin/env bash
set -Eeuo pipefail

# Bounded, non-interactive Codex worker used by /ops:run.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_ROOT="${OPS_WORKSPACE_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"
RUNTIME_ROOT="${OPS_ROOT:-$WORKSPACE_ROOT}"
RUNTIME="$SCRIPT_DIR/ops-runtime.sh"

usage() {
  printf 'usage: run-codex-phase.sh <change> <repository> <IMPLEMENT|FIX>\n' >&2
}
die() {
  printf 'run-codex-phase: %s\n' "$1" >&2
  exit 1
}

[ "$#" -eq 3 ] || { usage; exit 2; }
change="$1"
repository="$2"
phase="$3"
[[ "$change" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "invalid change name: $change"
case "$phase" in IMPLEMENT|FIX) ;; *) die "invalid worker phase: $phase" ;; esac
workspace_root="$(git -C "$WORKSPACE_ROOT" rev-parse --show-toplevel 2>/dev/null)" \
  || die "workspace is not a Git worktree: $WORKSPACE_ROOT"
repository_root="$(git -C "$repository" rev-parse --show-toplevel 2>/dev/null)" \
  || die "repository is not a Git worktree: $repository"
workspace_root="$(cd -- "$workspace_root" && pwd -P)"
repository_root="$(cd -- "$repository_root" && pwd -P)"
[ "$workspace_root" != "$repository_root" ] || die 'runtime repository must differ from finance-workspace'
command -v codex >/dev/null 2>&1 || die 'codex CLI is not installed or not on PATH'

timeout_seconds="${CODEX_TIMEOUT_SECONDS:-3600}"
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'CODEX_TIMEOUT_SECONDS must be a positive integer'
state_file="$RUNTIME_ROOT/.ops/changes/$change/runtime/state.json"
[ -f "$state_file" ] || die "runtime state not found: $state_file"
session_id="$(jq -r '.session_id // empty' "$state_file")"
[ -n "$session_id" ] || die 'runtime state has no session id'
"$RUNTIME" assert-repo-lock "$change" "$session_id" "$repository_root"
round="$(jq -r '.round' "$state_file")"
log_dir="$RUNTIME_ROOT/.ops/changes/$change/runtime/logs"
mkdir -p -- "$log_dir"
stdout_log="$log_dir/codex-${phase,,}-round-${round}.stdout.jsonl"
stderr_log="$log_dir/codex-${phase,,}-round-${round}.stderr.log"
last_message="$log_dir/codex-${phase,,}-round-${round}.last-message.md"
exit_code_file="$log_dir/codex-${phase,,}-round-${round}.exit"
prompt="$(cat <<EOF
Apply OpenSpec change $change.

The current working directory is the Finance orchestration workspace.
Implementation repository: $repository_root

Read AGENTS.md, applicable .agents/rules/, relevant skills, the active
OpenSpec change, and repository-local instructions. Use the Codex-native
OpenSpec apply workflow. Modify runtime production code only in the declared
implementation repository. Run local verification and create local commits
when required. Do not push before Claude final verification.
EOF
)"

set +e
timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" \
  codex exec --cd "$workspace_root" --add-dir "$repository_root" --ephemeral \
  --approve-for-me --json --output-last-message "$last_message" \
  - <<<"$prompt" >"$stdout_log" 2>"$stderr_log"
status=$?
set -e
printf '%s\n' "$status" >"$exit_code_file"
if [ "$status" -ne 0 ]; then
  printf 'Codex phase %s failed with exit %s; evidence: %s\n' "$phase" "$status" "$log_dir" >&2
  exit "$status"
fi
printf 'Codex phase %s completed; evidence: %s\n' "$phase" "$log_dir"
