#!/usr/bin/env bash
set -euo pipefail

readonly script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly test_root="$(mktemp -d)"
watcher_pid=""
cleanup() {
  if [[ -n "${watcher_pid}" ]]; then
    kill "${watcher_pid}" 2>/dev/null || true
    wait "${watcher_pid}" 2>/dev/null || true
  fi
  rm -rf "${test_root}"
}
trap cleanup EXIT

handoff_file="${test_root}/handoff.md"
output_log="${test_root}/watch.log"
printf '# initial\n' >"${handoff_file}"
"${script_dir}/watch_handoff.sh" "${handoff_file}" "${output_log}" 1 &
watcher_pid="$!"

for attempt in $(seq 1 20); do
  [[ -f "${output_log}" ]] && grep -q '^HANDOFF_WATCH_START ' "${output_log}" && break
  sleep 0.1
done
grep -q '^HANDOFF_WATCH_START ' "${output_log}"
printf '# changed\n' >"${handoff_file}"
for attempt in $(seq 1 30); do
  grep -q '^HANDOFF_CHANGED ' "${output_log}" && break
  sleep 0.1
done
grep -q '^HANDOFF_CHANGED ' "${output_log}"
if grep -q '# changed' "${output_log}"; then
  printf 'Watcher leaked handoff contents\n' >&2
  exit 1
fi
printf 'PASS: live handoff watcher records content-free change events\n'
