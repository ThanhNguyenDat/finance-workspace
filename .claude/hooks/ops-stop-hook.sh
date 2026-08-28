#!/usr/bin/env bash
set -Eeuo pipefail

# Keep an active /ops:run session alive until its runtime state is terminal.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
RUNTIME="$SCRIPT_DIR/../../.agents/scripts/ops-runtime.sh"
payload="$(cat || true)"
cwd="$(jq -r '.cwd // empty' <<<"$payload" 2>/dev/null || true)"
session_id="$(jq -r '.session_id // empty' <<<"$payload" 2>/dev/null || true)"
session_id="${session_id:-${CLAUDE_SESSION_ID:-}}"
[ -n "$cwd" ] || cwd="$PWD"
[ -n "$session_id" ] || exit 0

active="$("$RUNTIME" active "$cwd" "$session_id" 2>/dev/null || true)"
[ -n "$active" ] || exit 0

line_count="$(printf '%s\n' "$active" | awk 'END { print NR }')"
if [ "$line_count" -ne 1 ]; then
  printf 'Stop blocked: multiple active /ops:run changes were found. Resume the owning workflow or terminate each change explicitly.\n%s\n' "$active" >&2
  exit 2
fi

IFS='|' read -r change phase round <<<"$active"
case "$phase" in
  DONE|BLOCKED|FAILED) exit 0 ;;
  *)
    printf 'Stop blocked: /ops:run change %s is in phase %s (round %s). Continue the workflow, record evidence, and move it to DONE, BLOCKED, or FAILED.\n' "$change" "$phase" "$round" >&2
    exit 2
    ;;
esac
