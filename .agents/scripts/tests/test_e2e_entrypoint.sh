#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp_dir="$(mktemp -d)"
first="$(OPS_ROOT="$tmp_dir" timeout --signal=TERM --kill-after=10s 60s "$ROOT_DIR/tools/orchestrator/bin/e2e.sh" change-a 'fix ABC')"
second="$(OPS_ROOT="$tmp_dir" timeout --signal=TERM --kill-after=10s 60s "$ROOT_DIR/tools/orchestrator/bin/e2e.sh" change-a reopen)"

test "$(jq -r '.action' <<<"$first")" = submitted
test "$(jq -r '.action' <<<"$second")" = resumed
test "$(jq -r '.session.id' <<<"$first")" = "$(jq -r '.session.id' <<<"$second")"
printf '%s\n' 'test_e2e_entrypoint: all checks passed'
