#!/usr/bin/env bash
set -euo pipefail

if (( $# < 2 || $# > 3 )); then
  printf 'Usage: %s <handoff-file> <output-log> [interval-seconds]\n' "$0" >&2
  exit 64
fi

readonly handoff_file="$1"
readonly output_log="$2"
readonly interval_seconds="${3:-2}"

if [[ ! "${interval_seconds}" =~ ^[1-9][0-9]*$ ]]; then
  printf 'Interval must be a positive integer\n' >&2
  exit 64
fi

handoff_state() {
  if [[ -f "${handoff_file}" ]]; then
    sha256sum "${handoff_file}" | awk '{print $1}'
  else
    printf 'missing\n'
  fi
}

previous_state="$(handoff_state)"
printf 'HANDOFF_WATCH_START file=%s state=%s started_at=%s\n' \
  "${handoff_file}" "${previous_state}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >>"${output_log}"
while true; do
  sleep "${interval_seconds}"
  current_state="$(handoff_state)"
  if [[ "${current_state}" != "${previous_state}" ]]; then
    printf 'HANDOFF_CHANGED file=%s previous=%s current=%s observed_at=%s\n' \
      "${handoff_file}" "${previous_state}" "${current_state}" \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"${output_log}"
    previous_state="${current_state}"
  fi
done
