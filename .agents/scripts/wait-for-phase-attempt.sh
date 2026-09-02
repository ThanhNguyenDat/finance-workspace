#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
die() { printf 'wait-for-phase-attempt: %s\n' "$1" >&2; exit 1; }
change="${1:-}"; [[ -n "$change" ]] || die 'usage: wait-for-phase-attempt.sh <change> [poll-seconds]'
poll="${2:-5}"; [[ "$poll" =~ ^[1-9][0-9]*$ ]] || die 'poll-seconds must be a positive integer'
lease="$ROOT_DIR/.ops/changes/$change/runtime/.phase-attempt-lock"

# Wait for the lease to exist first (the attempt may not have started the
# moment this script is launched), then wait for it to be released. Bound
# the pre-start wait so a typo'd change name does not hang forever.
waited=0
while [[ ! -d "$lease" && ! -f "$ROOT_DIR/.ops/changes/$change/runtime/state.json" ]]; do
  sleep "$poll"; waited=$((waited + poll))
  [[ "$waited" -lt 3600 ]] || die "change not found after ${waited}s: $change"
done
while [[ -d "$lease" ]]; do sleep "$poll"; done

printf 'phase attempt for %s finished\n' "$change"
"$ROOT_DIR/.agents/scripts/ops-runtime.sh" state "$change" 2>/dev/null || printf '(no active OPS state — change may have been archived/blocked)\n'
