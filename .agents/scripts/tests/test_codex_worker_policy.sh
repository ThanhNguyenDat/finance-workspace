#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"; CLASSIFIER="$ROOT_DIR/.agents/scripts/classify-codex-result.sh"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
check() { local status="$1" body="$2" expected="$3"; printf '%s\n' "$body" >"$tmp/out"; : >"$tmp/err"; [[ "$($CLASSIFIER "$status" "$tmp/out" "$tmp/err")" = "$expected" ]] || { printf 'test_codex_worker_policy: expected %s\n' "$expected" >&2; exit 1; }; }
check 0 '{}' success
check 7 '{"error":{"code":"global_quota_exhausted"}}' global-quota-exhausted
check 7 '{"error":{"code":"model_unavailable"}}' model-unavailable
check 7 '{"error":{"code":"model_capacity_exceeded"}}' model-specific-limit
check 7 '{"error":{"code":"rate_limit_exceeded"}}' transient-rate-limit
check 7 '{"error":{"code":"implementation_error"}}' implementation-error
grep -Fq -- '--dangerously-bypass-approvals-and-sandbox' "$ROOT_DIR/.agents/scripts/run-codex-phase.sh" || { printf 'test_codex_worker_policy: bypass missing\n' >&2; exit 1; }
printf '%s\n' 'test_codex_worker_policy: all checks passed'
