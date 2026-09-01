#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
die() { printf 'configure-phase-agents: %s\n' "$1" >&2; exit 1; }
[[ -x "$STATE" ]] || die "state helper unavailable: $STATE"
usage() { printf 'usage: configure-phase-agents.sh <show|set PHASE PROVIDER MODEL EFFORT|candidate-set PHASE INDEX PROVIDER MODEL EFFORT|reset PHASE|reset-all|pin PHASE PROVIDER|auto PHASE|provider-on PROVIDER|provider-off PROVIDER|provider-manual PROVIDER|provider-auto PROVIDER>\n' >&2; exit 2; }
show() {
  local json
  json="$($STATE state)"
  printf '%-16s %-8s %-8s %-24s %s\n' PHASE MODE PROVIDER MODEL EFFORT
  jq -r '.phases|to_entries[] as $p|$p.value.candidates[]|[$p.key,$p.value.mode,.provider,.model,.effort]|@tsv' <<<"$json" \
    | while IFS=$'\t' read -r phase mode provider model effort; do printf '%-16s %-8s %-8s %-24s %s\n' "$phase" "$mode" "$provider" "$model" "$effort"; done
  printf '\n%-8s %-8s %-10s %s\n' PROVIDER MODE AVAILABLE REASON
  jq -r '.providers|to_entries[]|[.key,.value.mode,(.value.available|tostring),(.value.reason//"-")]|@tsv' <<<"$json" \
    | while IFS=$'\t' read -r provider mode available reason; do printf '%-8s %-8s %-10s %s\n' "$provider" "$mode" "$available" "$reason"; done
}
case "${1:-}" in
  show) [[ $# -eq 1 ]] || usage; show ;;
  set) [[ $# -eq 5 ]] || usage; "$STATE" set "$2" "$3" "$4" "$5" >/dev/null; show ;;
  candidate-set) [[ $# -eq 6 ]] || usage; "$STATE" candidate-set "$2" "$3" "$4" "$5" "$6" >/dev/null; show ;;
  reset) [[ $# -eq 2 ]] || usage; "$STATE" reset "$2" >/dev/null; show ;;
  reset-all) [[ $# -eq 1 ]] || usage; "$STATE" reset-all >/dev/null; show ;;
  pin) [[ $# -eq 3 ]] || usage; "$STATE" pin "$2" "$3" >/dev/null; show ;;
  auto) [[ $# -eq 2 ]] || usage; "$STATE" auto "$2" >/dev/null; show ;;
  provider-on|provider-off|provider-manual|provider-auto) [[ $# -eq 2 ]] || usage; "$STATE" "$1" "$2" >/dev/null; show ;;
  *) usage ;;
esac
