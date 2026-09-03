#!/usr/bin/env bash
set -Eeuo pipefail

# Records the active /ops:run transaction quietly instead of blocking Stop.
#
# Previous behavior (disabled 2026-09-02 at the operator's explicit request):
# this hook returned exit 2 with a stderr message every time Stop fired while
# a transaction was non-terminal, which Claude Code's terminal UI surfaces as
# a visible "Stop hook feedback" block. There is no Claude Code setting to
# suppress that UI display while keeping the block (confirmed via the
# claude-code-guide agent, 2026-09-02), and it fired on every retry of a
# background job's idle-stop attempt -- often every few seconds -- which the
# operator found disruptive. The blocking behavior is preserved below as a
# commented reference in case a future session wants to restore it (e.g.
# behind an opt-in env var), but the active safety net is now the operator
# actively supervising each transaction via Monitor/uv run wait-for-phase-attempt
# per .claude/commands/ops/run.md, not this hook.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="$SCRIPT_DIR/../../tools/phase-agent-orchestrator"
payload="$(cat || true)"
cwd="$(jq -r '.cwd // empty' <<<"$payload" 2>/dev/null || true)"
session_id="$(jq -r '.session_id // empty' <<<"$payload" 2>/dev/null || true)"
session_id="${session_id:-${CLAUDE_SESSION_ID:-}}"
[ -n "$cwd" ] || cwd="$PWD"
[ -n "$session_id" ] || exit 0

active="$(uv run --project "$PROJECT_DIR" ops-runtime active "$cwd" "$session_id" 2>/dev/null || true)"
[ -n "$active" ] || exit 0

# Log under the target workspace's own .ops/runtime/, not the hook script's
# location, so this works correctly for any cwd (including a test fixture).
STATUS_FILE="$cwd/.ops/runtime/last-active-transaction.log"
mkdir -p -- "$(dirname -- "$STATUS_FILE")" 2>/dev/null || exit 0
printf '%s %s\n' "$(date -u +%FT%TZ)" "$active" >>"$STATUS_FILE" 2>/dev/null || true
exit 0

# --- restore point: the block below is the original blocking behavior ---
# line_count="$(printf '%s\n' "$active" | awk 'END { print NR }')"
# if [ "$line_count" -ne 1 ]; then
#   printf 'Stop blocked: multiple active /ops:run changes were found. Resume the owning workflow or terminate each change explicitly.\n%s\n' "$active" >&2
#   exit 2
# fi
# IFS='|' read -r change phase round <<<"$active"
# case "$phase" in
#   DONE|BLOCKED|FAILED) exit 0 ;;
#   *)
#     printf 'Stop blocked: /ops:run change %s is in phase %s (round %s). Continue to ARCHIVE/complete or record BLOCKED/FAILED before stopping.\n' "$change" "$phase" "$round" >&2
#     exit 2
#     ;;
# esac
