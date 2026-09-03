#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.py"
QUANT_COMMAND="$ROOT_DIR/.claude/commands/quant-research.md"
OPS_COMMAND="$ROOT_DIR/.claude/commands/ops/run.md"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_quant_promotion_trace: %s\n' "$1" >&2
  exit 1
}
expect_failure() {
  if "$@"; then
    fail "expected command to fail: $*"
  fi
}

workspace="$tmp/workspace"
outside="$tmp/outside.md"
mkdir -p -- "$workspace/.ops/changes" "$workspace/openspec/changes" \
  "$workspace/research/quant/rounds" "$workspace/research/quant/studies" \
  "$workspace/research/quant/audits" "$workspace/research/quant/samples" \
  "$workspace/research/quant/reports" "$workspace/raw/researcher"
git -C "$workspace" init -q
git -C "$workspace" config user.email test@example.invalid
git -C "$workspace" config user.name promotion-test
printf '%s\n' fixture >"$workspace/README.md"
printf '%s\n' evidence >"$workspace/research/quant/rounds/candidate.md"
printf '%s\n' 'round,metric' >"$workspace/research/quant/reports/metrics.csv"
printf '%s\n' legacy >"$workspace/raw/researcher/legacy.md"
printf '%s\n' outside >"$outside"
ln -s -- "$outside" "$workspace/research/quant/rounds/escaped.md"
git -C "$workspace" add .
git -C "$workspace" commit -qm fixture

export OPS_ROOT="$workspace"
run_runtime() {
  "$RUNTIME" "$@"
}
prepare_change() {
  local change="$1" session="session-$1"
  mkdir -p -- "$workspace/openspec/changes/$change/specs/capability"
  printf '%s\n' proposal >"$workspace/openspec/changes/$change/proposal.md"
  printf '%s\n' design >"$workspace/openspec/changes/$change/design.md"
  printf '%s\n' tasks >"$workspace/openspec/changes/$change/tasks.md"
  printf '%s\n' spec >"$workspace/openspec/changes/$change/specs/capability/spec.md"
  run_runtime lock "$change" "$session"
  run_runtime init "$change" "$session"
}
cleanup_change() {
  run_runtime cleanup "$1" "session-$1" BLOCKED
}

prepare_change promoted-candidate
run_runtime trace-origin promoted-candidate session-promoted-candidate 87 XAU \
  research/quant/rounds/candidate.md research/quant/reports/metrics.csv
origin="$workspace/.ops/changes/promoted-candidate/runtime/origin.json"
jq -e '
  .change == "promoted-candidate" and
  .origin == "quant-research" and
  .research_iteration == 87 and
  .instrument == "XAU" and
  .research_artifacts == ["research/quant/rounds/candidate.md", "research/quant/reports/metrics.csv"]
' "$origin" >/dev/null || fail 'valid origin metadata is incorrect'
if grep -Fq -- evidence "$origin" || grep -Fq -- 'round,metric' "$origin"; then
  fail 'origin metadata duplicated research content'
fi
origin_hash="$(sha256sum "$origin" | awk '{print $1}')"
expect_failure run_runtime trace-origin promoted-candidate session-promoted-candidate 88 XAU research/quant/rounds/candidate.md
test "$(sha256sum "$origin" | awk '{print $1}')" = "$origin_hash" \
  || fail 'origin overwrite changed existing metadata'
jq -e '.routing_policy_version == 1 and (.attempts|length) == 0 and .phase == "PLAN"' \
  "$workspace/.ops/changes/promoted-candidate/runtime/state.json" >/dev/null \
  || fail 'trace-origin changed routing history or phase'
cleanup_change promoted-candidate

for invalid in bad-iteration bad-instrument bad-traversal bad-missing bad-outside bad-old-root bad-symlink-escape; do
  prepare_change "$invalid"
  case "$invalid" in
    bad-iteration) args=(0 XAU research/quant/rounds/candidate.md) ;;
    bad-instrument) args=(87 'xau gold' research/quant/rounds/candidate.md) ;;
    bad-traversal) args=(87 XAU research/quant/rounds/../candidate.md) ;;
    bad-missing) args=(87 XAU research/quant/rounds/missing.md) ;;
    bad-outside) args=(87 XAU README.md) ;;
    bad-old-root) args=(87 XAU raw/researcher/legacy.md) ;;
    bad-symlink-escape) args=(87 XAU research/quant/rounds/escaped.md) ;;
  esac
  expect_failure run_runtime trace-origin "$invalid" "session-$invalid" "${args[@]}"
  test ! -e "$workspace/.ops/changes/$invalid/runtime/origin.json" \
    || fail "$invalid created origin metadata"
  cleanup_change "$invalid"
done

prepare_change wrong-owner
expect_failure run_runtime trace-origin wrong-owner another-session 87 XAU research/quant/rounds/candidate.md
cleanup_change wrong-owner

prepare_change wrong-phase
run_runtime phase wrong-phase session-wrong-phase IMPLEMENT
expect_failure run_runtime trace-origin wrong-phase session-wrong-phase 87 XAU research/quant/rounds/candidate.md
cleanup_change wrong-phase

grep -Fq 'REJECTED' "$QUANT_COMMAND" || fail 'REJECTED classification missing'
grep -Fq 'NO-CHANGE' "$QUANT_COMMAND" || fail 'NO-CHANGE classification missing'
grep -Fq 'DATA-ISSUE' "$QUANT_COMMAND" || fail 'DATA-ISSUE classification missing'
grep -Fq 'NEEDS-MORE-RESEARCH' "$QUANT_COMMAND" || fail 'NEEDS-MORE-RESEARCH classification missing'
grep -Fq 'PROMOTE' "$QUANT_COMMAND" || fail 'PROMOTE classification missing'
grep -Fq 'defensible' "$QUANT_COMMAND" || fail 'promotion evidence gate missing'
grep -Fq 'scope rõ' "$QUANT_COMMAND" || fail 'promotion scope gate missing'
grep -Fq 'trace-origin' "$QUANT_COMMAND" || fail 'OPS origin trace missing'
grep -Fq '@.claude/commands/ops/run.md' "$QUANT_COMMAND" || fail 'canonical OPS reference missing'
grep -Fq 'dùng cùng `<change>`' "$QUANT_COMMAND" || fail 'same change identity contract missing'
grep -Fq 'docs/archive/legacy-handoff-agent.md' "$QUANT_COMMAND" \
  && grep -Fq 'authoritative' "$QUANT_COMMAND" \
  || fail 'quant command does not demote legacy handoff lifecycle'
if rg -n 'codex exec|claude -p|claude exec' "$QUANT_COMMAND" >/dev/null \
  || grep -Fq '/loop 20m /quant-research "' "$QUANT_COMMAND" \
  || grep -Fq "/loop 20m /quant-research '" "$QUANT_COMMAND"; then
  fail 'quant command contains a real nested loop or worker invocation'
fi
grep -Fq 'trace-origin <change> <session-id> <research-iteration>' "$OPS_COMMAND" \
  || fail 'OPS command does not define promotion origin attachment'

printf 'test_quant_promotion_trace: all checks passed\n'
