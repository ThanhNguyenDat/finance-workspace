#!/usr/bin/env bash
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
BASE="${PROVIDER_RESULT_CLASSIFIER:-$SCRIPT_DIR/classify-codex-result.sh}"
[[ $# -eq 3 ]] || { printf 'usage: classify-claude-result.sh <status> <stdout-jsonl> <stderr-log>\n' >&2; exit 2; }
[[ -x "$BASE" ]] || { printf 'classify-claude-result: base classifier unavailable\n' >&2; exit 1; }
"$BASE" "$1" "$2" "$3"
