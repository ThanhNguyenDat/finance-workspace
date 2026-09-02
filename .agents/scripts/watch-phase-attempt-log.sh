#!/usr/bin/env bash
set -Eeuo pipefail
# Stream real progress lines from the currently-running (or most recent)
# phase-agent attempt's stdout.jsonl log for a change, for both the Claude
# (`--output-format stream-json`) and Codex (`--json`) event schemas.
#
# Usage: watch-phase-attempt-log.sh <change>
# Intended to be wrapped in the Monitor tool, e.g.:
#   Monitor(command: ".agents/scripts/watch-phase-attempt-log.sh <change>")
# Each stdout line is one real agent progress event (tool call, file change,
# message, or result) -- not a heartbeat/timestamp line.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
die() { printf 'watch-phase-attempt-log: %s\n' "$1" >&2; exit 1; }
change="${1:-}"; [[ -n "$change" ]] || die 'usage: watch-phase-attempt-log.sh <change>'
log_dir="$ROOT_DIR/.ops/changes/$change/runtime/logs"

# Wait for at least one attempt log to exist (an attempt may not have
# started the moment this is launched), bounded so a typo'd change does
# not hang forever.
waited=0
while true; do
  latest="$(ls -t "$log_dir"/*.stdout.jsonl 2>/dev/null | head -1 || true)"
  [[ -n "$latest" ]] && break
  sleep 5; waited=$((waited + 5))
  [[ "$waited" -lt 3600 ]] || die "no attempt log found after ${waited}s under $log_dir"
done

printf 'watching: %s\n' "$latest"
tail -n0 -F "$latest" | jq -r --unbuffered '
  if .type == "item.completed" then
    (.item.type // "event") + ": " +
    ((.item.command // .item.path // .item.text // .item.aggregated_output // "") | tostring | .[0:220])
  elif .type == "error" then
    "error: " + ((.message // .error // .) | tostring | .[0:220])
  elif .type == "assistant" and (.message.content? != null) then
    ([.message.content[]? |
      if .type == "text" then "message: " + (.text // "")
      elif .type == "tool_use" then "tool_use: " + (.name // "") + " " + ((.input // {}) | tostring | .[0:150])
      else empty end
    ] | join(" | ")) as $line | if ($line | length) > 0 then $line[0:220] else empty end
  elif .type == "tool_result" or (.message.content[]?.type? == "tool_result") then
    "tool_result: " + (([.message.content[]? | select(.type=="tool_result") | (.content[]?.text // "")] | join(" ")) | tostring | .[0:220])
  elif .type == "result" then
    "result: " + ((.result // .subtype // "") | tostring | .[0:220])
  else
    empty
  end
' 2>/dev/null
