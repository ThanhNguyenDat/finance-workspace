#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test_dir="$(mktemp -d)"
trap 'rm -rf "$test_dir"' EXIT

mkdir -p "$test_dir/bin"
cat >"$test_dir/bin/gh" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail

if [[ "$1 $2" == "run watch" ]]; then
  count=0
  [[ ! -f "$WATCH_COUNT_FILE" ]] || count="$(<"$WATCH_COUNT_FILE")"
  count=$((count + 1))
  printf '%s\n' "$count" >"$WATCH_COUNT_FILE"
  ((count > 1))
  exit
fi

if [[ "$1 $2" == "run view" && " $* " == *" --json status,conclusion --jq "* ]]; then
  printf 'in_progress\t\n'
  exit 0
fi

if [[ "$1 $2" == "run view" ]]; then
  count=0
  [[ ! -f "$VIEW_COUNT_FILE" ]] || count="$(<"$VIEW_COUNT_FILE")"
  count=$((count + 1))
  printf '%s\n' "$count" >"$VIEW_COUNT_FILE"
  if ((count == 1)); then
    exit 1
  fi
  printf '{"status":"completed","conclusion":"success","jobs":[],"url":"fixture"}\n'
  exit 0
fi

exit 2
MOCK
chmod +x "$test_dir/bin/gh"

export WATCH_COUNT_FILE="$test_dir/watch-count"
export VIEW_COUNT_FILE="$test_dir/view-count"
PATH="$test_dir/bin:$PATH" \
  "$script_dir/watch_gh_run.sh" owner/repository 123 "$test_dir/output.log" 1

[[ "$(<"$WATCH_COUNT_FILE")" == "2" ]]
[[ "$(<"$VIEW_COUNT_FILE")" == "2" ]]
grep -Fq 'WATCH_RETRY reason=watch_interrupted status=in_progress' "$test_dir/output.log"
grep -Fq 'VIEW_RETRY reason=terminal_snapshot_failed' "$test_dir/output.log"
grep -Fq 'WATCH_COMPLETE watch_exit=0 view_exit=0' "$test_dir/output.log"

printf 'PASS: workflow watcher retries transient interruptions until terminal state\n'
