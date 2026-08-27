#!/usr/bin/env bash
set -u

repo="${1:?usage: watch_gh_run.sh <owner/repo> <run-id> <absolute-output-log> [interval-seconds]}"
run_id="${2:?run id is required}"
output_log="${3:?absolute output log is required}"
interval_seconds="${4:-60}"

[[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || {
  printf 'invalid repository: %s\n' "$repo" >&2
  exit 2
}
[[ "$run_id" =~ ^[1-9][0-9]*$ ]] || {
  printf 'invalid run id: %s\n' "$run_id" >&2
  exit 2
}
[[ "$interval_seconds" =~ ^[1-9][0-9]*$ ]] || {
  printf 'invalid interval: %s\n' "$interval_seconds" >&2
  exit 2
}
[[ "$output_log" = /* ]] || {
  printf 'output log must be absolute: %s\n' "$output_log" >&2
  exit 2
}
[[ -d "$(dirname "$output_log")" ]] || {
  printf 'output directory does not exist: %s\n' "$(dirname "$output_log")" >&2
  exit 2
}

umask 077
: >"$output_log"
exec >>"$output_log" 2>&1

printf 'WATCH_START repository=%s run_id=%s interval_seconds=%s started_at=%s\n' \
  "$repo" "$run_id" "$interval_seconds" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

watch_status=1
while true; do
  gh run watch "$run_id" --repo "$repo" --interval "$interval_seconds" --exit-status
  watch_status=$?
  if ((watch_status == 0)); then
    break
  fi

  run_state="$({
    gh run view "$run_id" --repo "$repo" --json status,conclusion \
      --jq '[.status, (.conclusion // "")] | @tsv'
  } 2>/dev/null)" || {
    printf 'WATCH_RETRY reason=status_lookup_failed retry_at=%s\n' \
      "$(date -u -d "+${interval_seconds} seconds" +'%Y-%m-%dT%H:%M:%SZ')"
    sleep "$interval_seconds"
    continue
  }
  run_status="${run_state%%$'\t'*}"
  run_conclusion="${run_state#*$'\t'}"
  if [[ "$run_status" == "completed" ]]; then
    [[ "$run_conclusion" == "success" ]] && watch_status=0
    break
  fi

  printf 'WATCH_RETRY reason=watch_interrupted status=%s retry_at=%s\n' \
    "$run_status" "$(date -u -d "+${interval_seconds} seconds" +'%Y-%m-%dT%H:%M:%SZ')"
  sleep "$interval_seconds"
done

view_status=1
while ((view_status != 0)); do
  gh run view "$run_id" --repo "$repo" --json status,conclusion,jobs,url \
    --jq '{status,conclusion,url,jobs:[.jobs[]|{name,status,conclusion,databaseId}]}'
  view_status=$?
  if ((view_status != 0)); then
    printf 'VIEW_RETRY reason=terminal_snapshot_failed retry_at=%s\n' \
      "$(date -u -d "+${interval_seconds} seconds" +'%Y-%m-%dT%H:%M:%SZ')"
    sleep "$interval_seconds"
  fi
done

printf 'WATCH_COMPLETE watch_exit=%s view_exit=%s finished_at=%s\n' \
  "$watch_status" "$view_status" "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

if ((watch_status != 0 || view_status != 0)); then
  exit 1
fi
