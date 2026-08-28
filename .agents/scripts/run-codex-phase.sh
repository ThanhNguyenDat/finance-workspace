#!/usr/bin/env bash
set -Eeuo pipefail

# Bounded, non-interactive Codex worker used by /ops:run.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="${OPS_ROOT:-$(cd -- "$SCRIPT_DIR/../.." && pwd -P)}"

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
[ -d "$repository/.git" ] || die "repository is not a git worktree: $repository"
command -v codex >/dev/null 2>&1 || die 'codex CLI is not installed or not on PATH'

timeout_seconds="${CODEX_TIMEOUT_SECONDS:-3600}"
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'CODEX_TIMEOUT_SECONDS must be a positive integer'
state_file="$ROOT_DIR/.ops/changes/$change/runtime/state.json"
[ -f "$state_file" ] || die "runtime state not found: $state_file"
round="$(jq -r '.round' "$state_file")"
log_dir="$ROOT_DIR/.ops/changes/$change/runtime/logs"
mkdir -p -- "$log_dir"
stdout_log="$log_dir/codex-${phase,,}-round-${round}.stdout.jsonl"
stderr_log="$log_dir/codex-${phase,,}-round-${round}.stderr.log"
last_message="$log_dir/codex-${phase,,}-round-${round}.last-message.md"
exit_code_file="$log_dir/codex-${phase,,}-round-${round}.exit"
prompt="$(cat <<EOF
Apply OpenSpec change $change in the current repository.

Follow AGENTS.md and all applicable repository rules and skills. Use the
Codex-native OpenSpec workflow. Implement or fix all approved tasks and
verification criteria for phase $phase. Run bounded local checks and create
local commits as required. Read .ops/changes/$change/handoff.md when present.
Do not push; release remains blocked until Claude completes independent
verification.
EOF
)"

set +e
timeout --signal=TERM --kill-after=30s "${timeout_seconds}s" \
  codex exec --cd "$repository" --ephemeral --ask-for-approval never \
  --sandbox workspace-write --json --output-last-message "$last_message" \
  - <<<"$prompt" >"$stdout_log" 2>"$stderr_log"
status=$?
set -e
printf '%s\n' "$status" >"$exit_code_file"
if [ "$status" -ne 0 ]; then
  printf 'Codex phase %s failed with exit %s; evidence: %s\n' "$phase" "$status" "$log_dir" >&2
  exit "$status"
fi
printf 'Codex phase %s completed; evidence: %s\n' "$phase" "$log_dir"
