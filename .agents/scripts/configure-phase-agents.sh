#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"
die() { printf 'configure-phase-agents: %s\n' "$1" >&2; exit 1; }
[[ -x "$STATE" ]] || die "state helper unavailable: $STATE"
usage() { printf 'usage: configure-phase-agents.sh <show|set PHASE PROVIDER MODEL EFFORT [ACCOUNT]|candidate-set PHASE INDEX PROVIDER MODEL EFFORT [ACCOUNT]|reset PHASE|reset-all|pin PHASE PROVIDER [ACCOUNT]|auto PHASE|provider-on PROVIDER [ACCOUNT]|provider-off PROVIDER [REASON] [ACCOUNT]|provider-manual PROVIDER|provider-auto PROVIDER>\n' >&2; exit 2; }
show() {
  local json
  json="$($STATE state)"
  printf '%-16s %-8s %-8s %-24s %-12s %s\n' PHASE MODE PROVIDER MODEL ACCOUNT EFFORT
  jq -r '.phases|to_entries[] as $p|$p.value.candidates[]|[$p.key,$p.value.mode,.provider,.model,(.account//"-"),.effort]|@tsv' <<<"$json" \
    | while IFS=$'\t' read -r phase mode provider model account effort; do printf '%-16s %-8s %-8s %-24s %-12s %s\n' "$phase" "$mode" "$provider" "$model" "$account" "$effort"; done
  printf '\n%-8s %-8s %-10s %s\n' PROVIDER MODE AVAILABLE REASON
  jq -r '.providers|to_entries[]|[.key,.value.mode,(.value.available|tostring),(.value.reason//"-")]|@tsv' <<<"$json" \
    | while IFS=$'\t' read -r provider mode available reason; do printf '%-8s %-8s %-10s %s\n' "$provider" "$mode" "$available" "$reason"; done
}
case "${1:-}" in
  show) [[ $# -eq 1 ]] || usage; show ;;
  set) [[ $# -eq 5 || $# -eq 6 ]] || usage; "$STATE" set "${@:2}" >/dev/null; show ;;
  candidate-set) [[ $# -eq 6 || $# -eq 7 ]] || usage; "$STATE" candidate-set "${@:2}" >/dev/null; show ;;
  reset) [[ $# -eq 2 ]] || usage; "$STATE" reset "$2" >/dev/null; show ;;
  reset-all) [[ $# -eq 1 ]] || usage; "$STATE" reset-all >/dev/null; show ;;
  pin) [[ $# -eq 3 || $# -eq 4 ]] || usage; "$STATE" pin "${@:2}" >/dev/null; show ;;
  auto) [[ $# -eq 2 ]] || usage; "$STATE" auto "$2" >/dev/null; show ;;
  provider-on) [[ $# -eq 2 || $# -eq 3 ]] || usage; "$STATE" provider-on "${@:2}" >/dev/null; show ;;
  provider-off) [[ $# -ge 2 && $# -le 4 ]] || usage; "$STATE" provider-off "${@:2}" >/dev/null; show ;;
  provider-manual|provider-auto) [[ $# -eq 2 ]] || usage; "$STATE" "$1" "${@:2}" >/dev/null; show ;;
  *) usage ;;
esac
