#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.py"
RUNNER="$ROOT_DIR/.agents/scripts/run-codex-phase.py"
HOOK="$ROOT_DIR/.claude/hooks/ops-stop-hook.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() {
  printf 'test_ops_orchestration: %s\n' "$1" >&2
  exit 1
}
expect_failure() {
  if "$@"; then
    fail "expected command to fail: $*"
  fi
}
expect_hook_logs_active() {
  # The Stop hook no longer blocks (2026-09-02, operator request): it always
  # exits 0 and quietly appends the active transaction to
  # <cwd>/.ops/runtime/last-active-transaction.log instead.
  local payload="$1"
  local log="$workspace/.ops/runtime/last-active-transaction.log"
  local before=0 after=0
  [ -f "$log" ] && before="$(wc -l <"$log")"
  printf '%s' "$payload" | "$HOOK" >/dev/null || fail 'Stop hook must always exit 0'
  [ -f "$log" ] || fail 'Stop hook did not create the active-transaction log'
  after="$(wc -l <"$log")"
  [ "$after" -gt "$before" ] || fail 'Stop hook did not log the active transaction'
}

jq -e . "$ROOT_DIR/.claude/settings.json" >/dev/null || fail 'invalid Claude settings JSON'
grep -Fq '/ops:run' "$ROOT_DIR/.claude/commands/ops/run.md" || fail 'run command missing namespace'
grep -Fq 'PLAN / VERIFY / FINAL_VERIFY = Claude first, Codex fallback' "$ROOT_DIR/AGENTS.md" || fail 'AGENTS phase-agent role contract missing'
grep -Fq '.ops/**/runtime/' "$ROOT_DIR/.gitignore" || fail 'runtime ignore rule missing'

# Archival is a separate explicit workflow; Agent Contracts must not reject a
# planning-complete change merely because the operator has not archived it yet.

while IFS= read -r state_file; do
  test "$(jq -r '.status' "$state_file")" != terminal \
    || fail "terminal OPS change remains active: $state_file"
done < <(find "$ROOT_DIR/.ops/changes" -mindepth 3 -maxdepth 3 \
  -type f -name state.json | sort)

test ! -e "$ROOT_DIR/openspec/changes/route-quant-promotions-through-ops" \
  || fail 'completed quant promotion OpenSpec remains active'
test ! -e "$ROOT_DIR/openspec/changes/codex-worker-model-routing" \
  || fail 'completed worker-routing OpenSpec remains active'
test -f "$ROOT_DIR/openspec/changes/archive/2026-08-29-route-quant-promotions-through-ops/tasks.md" \
  || fail 'quant promotion OpenSpec archive is missing'
test -f "$ROOT_DIR/openspec/changes/archive/2026-08-29-codex-worker-model-routing/tasks.md" \
  || fail 'worker-routing OpenSpec archive is missing'
test -f "$ROOT_DIR/.ops/archive/2026-08-29-route-quant-promotions-through-ops/handoff.md" \
  || fail 'quant promotion OPS archive is missing'
grep -Fq 'Status: DONE.' "$ROOT_DIR/.ops/archive/2026-08-29-route-quant-promotions-through-ops/handoff.md" \
  || fail 'quant promotion OPS archive lacks durable DONE evidence'
lock_line="$(awk '/lock-repos <change>/{print NR; exit}' "$ROOT_DIR/.claude/commands/ops/run.md")"
write_line="$(awk '/run-phase-agent.py <change> <repository> PLAN/{print NR; exit}' "$ROOT_DIR/.claude/commands/ops/run.md")"
test -n "$lock_line" && test -n "$write_line" && test "$lock_line" -lt "$write_line" \
  || fail 'planning writes appear before repository lock acquisition'

fixture="$tmp/fixture"
workspace="$fixture/finance-workspace"
web_source="$fixture/finance-web-source"
web_worktree="$fixture/finance-web"
mw="$fixture/finance-mw"
mkdir -p -- "$workspace/openspec/changes" "$web_source" "$mw"
for repository in "$workspace" "$web_source" "$mw"; do
  git -C "$repository" init -q
  git -C "$repository" config user.email test@example.invalid
  git -C "$repository" config user.name orchestration-test
  printf '%s\n' 'fixture' >"$repository/README.md"
  git -C "$repository" add README.md
  git -C "$repository" commit -qm fixture
done
git -C "$web_source" worktree add -q -b linked-fixture "$web_worktree" HEAD
test -f "$web_worktree/.git" || fail 'linked worktree fixture was not created'
test "$(git -C "$web_worktree" rev-parse --is-inside-work-tree)" = true || fail 'linked worktree was not recognized'

export OPS_ROOT="$workspace"
export OPS_WORKSPACE_ROOT="$workspace"

new_change() {
  local change="$1"
  local session="$2"
  "$RUNTIME" lock "$change" "$session"
  "$RUNTIME" init "$change" "$session" codex
}

new_change change-full session-full
"$RUNTIME" lock-repos change-full session-full "$web_worktree"
"$RUNTIME" phase change-full session-full IMPLEMENT
"$RUNTIME" phase change-full session-full VERIFY
"$RUNTIME" fix change-full session-full
"$RUNTIME" phase change-full session-full VERIFY
"$RUNTIME" phase change-full session-full FINAL_VERIFY
"$RUNTIME" phase change-full session-full RELEASE
"$RUNTIME" phase change-full session-full DEPLOY_VERIFY
"$RUNTIME" phase change-full session-full ARCHIVE
full_archive="$("$RUNTIME" complete change-full session-full)"
test "$(jq -r '.phase' "$full_archive/runtime/state.json")" = DONE || fail 'full transition flow did not complete'
test ! -d "$workspace/.ops/changes/change-full/runtime/lock" || fail 'full completion leaked change lock'

new_change change-dev session-dev
"$RUNTIME" lock-repos change-dev session-dev "$mw"
"$RUNTIME" phase change-dev session-dev IMPLEMENT
"$RUNTIME" phase change-dev session-dev VERIFY
"$RUNTIME" phase change-dev session-dev FINAL_VERIFY
"$RUNTIME" phase change-dev session-dev ARCHIVE
"$RUNTIME" complete change-dev session-dev >/dev/null

new_change change-release-recovery session-release-recovery
"$RUNTIME" phase change-release-recovery session-release-recovery IMPLEMENT
"$RUNTIME" phase change-release-recovery session-release-recovery VERIFY
"$RUNTIME" phase change-release-recovery session-release-recovery FINAL_VERIFY
"$RUNTIME" phase change-release-recovery session-release-recovery RELEASE
"$RUNTIME" fix change-release-recovery session-release-recovery
test "$(jq -r '.phase' "$workspace/.ops/changes/change-release-recovery/runtime/state.json")" = FIX \
  || fail 'release recovery did not enter FIX'
test "$(jq -r '.round' "$workspace/.ops/changes/change-release-recovery/runtime/state.json")" = 1 \
  || fail 'release recovery did not consume exactly one fix round'
"$RUNTIME" phase change-release-recovery session-release-recovery VERIFY
"$RUNTIME" phase change-release-recovery session-release-recovery FINAL_VERIFY
"$RUNTIME" phase change-release-recovery session-release-recovery RELEASE
"$RUNTIME" phase change-release-recovery session-release-recovery ARCHIVE
release_recovery_archive="$("$RUNTIME" complete change-release-recovery session-release-recovery)"
test "$(jq -r '.phase' "$release_recovery_archive/runtime/state.json")" = DONE \
  || fail 'release recovery flow did not complete'

new_change change-deploy-recovery session-deploy-recovery
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery IMPLEMENT
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery VERIFY
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery FINAL_VERIFY
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery RELEASE
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery DEPLOY_VERIFY
"$RUNTIME" fix change-deploy-recovery session-deploy-recovery
test "$(jq -r '.phase' "$workspace/.ops/changes/change-deploy-recovery/runtime/state.json")" = FIX \
  || fail 'deployment recovery did not enter FIX'
test "$(jq -r '.round' "$workspace/.ops/changes/change-deploy-recovery/runtime/state.json")" = 1 \
  || fail 'deployment recovery did not consume exactly one fix round'
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery VERIFY
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery FINAL_VERIFY
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery RELEASE
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery DEPLOY_VERIFY
"$RUNTIME" phase change-deploy-recovery session-deploy-recovery ARCHIVE
deploy_recovery_archive="$("$RUNTIME" complete change-deploy-recovery session-deploy-recovery)"
test "$(jq -r '.phase' "$deploy_recovery_archive/runtime/state.json")" = DONE \
  || fail 'deployment recovery flow did not complete'

new_change bad-release session-bad-release
"$RUNTIME" phase bad-release session-bad-release IMPLEMENT
"$RUNTIME" phase bad-release session-bad-release VERIFY
"$RUNTIME" phase bad-release session-bad-release FINAL_VERIFY
"$RUNTIME" phase bad-release session-bad-release RELEASE
expect_failure "$RUNTIME" phase bad-release session-bad-release FIX
expect_failure "$RUNTIME" phase bad-release session-bad-release IMPLEMENT
expect_failure "$RUNTIME" phase bad-release session-bad-release VERIFY
expect_failure "$RUNTIME" phase bad-release session-bad-release FINAL_VERIFY
expect_failure "$RUNTIME" phase bad-release session-bad-release PLAN
"$RUNTIME" cleanup bad-release session-bad-release BLOCKED

new_change bad-deploy-transition session-bad-deploy-transition
"$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition IMPLEMENT
"$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition VERIFY
"$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition FINAL_VERIFY
"$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition RELEASE
"$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition DEPLOY_VERIFY
expect_failure "$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition FIX
expect_failure "$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition IMPLEMENT
expect_failure "$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition VERIFY
expect_failure "$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition FINAL_VERIFY
expect_failure "$RUNTIME" phase bad-deploy-transition session-bad-deploy-transition RELEASE
"$RUNTIME" cleanup bad-deploy-transition session-bad-deploy-transition BLOCKED

new_change round-integrity session-round-integrity
"$RUNTIME" phase round-integrity session-round-integrity IMPLEMENT
"$RUNTIME" phase round-integrity session-round-integrity VERIFY
"$RUNTIME" fix round-integrity session-round-integrity
test "$(jq -r '.phase' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = FIX \
  || fail 'fix did not enter FIX'
test "$(jq -r '.round' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = 1 \
  || fail 'first fix did not increment the round exactly once'
"$RUNTIME" phase round-integrity session-round-integrity VERIFY
"$RUNTIME" fix round-integrity session-round-integrity
test "$(jq -r '.round' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = 2 \
  || fail 'second fix did not increment the round exactly once'
"$RUNTIME" phase round-integrity session-round-integrity VERIFY
"$RUNTIME" fix round-integrity session-round-integrity
test "$(jq -r '.round' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = 3 \
  || fail 'third fix did not increment the round exactly once'
"$RUNTIME" phase round-integrity session-round-integrity VERIFY
expect_failure "$RUNTIME" fix round-integrity session-round-integrity
test "$(jq -r '.round' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = 3 \
  || fail 'rejected fourth fix changed the round'
test "$(jq -r '.phase' "$workspace/.ops/changes/round-integrity/runtime/state.json")" = BLOCKED \
  || fail 'fourth fix did not block the workflow'
test ! -d "$workspace/.ops/changes/round-integrity/runtime/lock" \
  || fail 'fourth fix did not release the change lock'

new_change old-phase-syntax session-old-phase-syntax
expect_failure "$RUNTIME" phase old-phase-syntax session-old-phase-syntax VERIFY 0
expect_failure "$RUNTIME" round old-phase-syntax session-old-phase-syntax
"$RUNTIME" cleanup old-phase-syntax session-old-phase-syntax BLOCKED

new_change invalid-fix-plan session-invalid-fix-plan
expect_failure "$RUNTIME" fix invalid-fix-plan session-invalid-fix-plan
"$RUNTIME" cleanup invalid-fix-plan session-invalid-fix-plan BLOCKED

new_change invalid-fix-implement session-invalid-fix-implement
"$RUNTIME" phase invalid-fix-implement session-invalid-fix-implement IMPLEMENT
expect_failure "$RUNTIME" fix invalid-fix-implement session-invalid-fix-implement
"$RUNTIME" cleanup invalid-fix-implement session-invalid-fix-implement BLOCKED

new_change invalid-fix-final session-invalid-fix-final
"$RUNTIME" phase invalid-fix-final session-invalid-fix-final IMPLEMENT
"$RUNTIME" phase invalid-fix-final session-invalid-fix-final VERIFY
"$RUNTIME" phase invalid-fix-final session-invalid-fix-final FINAL_VERIFY
expect_failure "$RUNTIME" fix invalid-fix-final session-invalid-fix-final
"$RUNTIME" cleanup invalid-fix-final session-invalid-fix-final BLOCKED

new_change invalid-fix-archive session-invalid-fix-archive
"$RUNTIME" phase invalid-fix-archive session-invalid-fix-archive IMPLEMENT
"$RUNTIME" phase invalid-fix-archive session-invalid-fix-archive VERIFY
"$RUNTIME" phase invalid-fix-archive session-invalid-fix-archive FINAL_VERIFY
"$RUNTIME" phase invalid-fix-archive session-invalid-fix-archive ARCHIVE
expect_failure "$RUNTIME" fix invalid-fix-archive session-invalid-fix-archive
"$RUNTIME" cleanup invalid-fix-archive session-invalid-fix-archive BLOCKED

new_change invalid-fix-source session-invalid-fix-source
"$RUNTIME" phase invalid-fix-source session-invalid-fix-source IMPLEMENT
"$RUNTIME" phase invalid-fix-source session-invalid-fix-source VERIFY
"$RUNTIME" fix invalid-fix-source session-invalid-fix-source
expect_failure "$RUNTIME" fix invalid-fix-source session-invalid-fix-source
"$RUNTIME" cleanup invalid-fix-source session-invalid-fix-source BLOCKED

new_change fix-owner session-fix-owner
"$RUNTIME" phase fix-owner session-fix-owner IMPLEMENT
"$RUNTIME" phase fix-owner session-fix-owner VERIFY
expect_failure "$RUNTIME" fix fix-owner session-other
"$RUNTIME" unlock fix-owner session-fix-owner
expect_failure "$RUNTIME" fix fix-owner session-fix-owner
"$RUNTIME" lock fix-owner session-fix-owner
state_fix_owner="$workspace/.ops/changes/fix-owner/runtime/state.json"
jq '.session_id = "session-other"' "$state_fix_owner" >"$state_fix_owner.tmp"
mv -- "$state_fix_owner.tmp" "$state_fix_owner"
expect_failure "$RUNTIME" fix fix-owner session-fix-owner
jq '.session_id = "session-fix-owner"' "$state_fix_owner" >"$state_fix_owner.tmp"
mv -- "$state_fix_owner.tmp" "$state_fix_owner"
"$RUNTIME" cleanup fix-owner session-fix-owner BLOCKED

new_change bad-plan session-bad-plan
expect_failure "$RUNTIME" phase bad-plan session-bad-plan VERIFY
expect_failure "$RUNTIME" phase bad-plan session-bad-plan ARCHIVE
expect_failure "$RUNTIME" phase bad-plan session-bad-plan RELEASE
"$RUNTIME" cleanup bad-plan session-bad-plan BLOCKED

new_change bad-impl session-bad-impl
"$RUNTIME" phase bad-impl session-bad-impl IMPLEMENT
expect_failure "$RUNTIME" phase bad-impl session-bad-impl ARCHIVE
"$RUNTIME" cleanup bad-impl session-bad-impl BLOCKED

new_change bad-verify session-bad-verify
"$RUNTIME" phase bad-verify session-bad-verify IMPLEMENT
"$RUNTIME" phase bad-verify session-bad-verify VERIFY
expect_failure "$RUNTIME" phase bad-verify session-bad-verify FIX
expect_failure "$RUNTIME" phase bad-verify session-bad-verify RELEASE
"$RUNTIME" cleanup bad-verify session-bad-verify BLOCKED

new_change bad-fix session-bad-fix
"$RUNTIME" phase bad-fix session-bad-fix IMPLEMENT
"$RUNTIME" phase bad-fix session-bad-fix VERIFY
"$RUNTIME" fix bad-fix session-bad-fix
expect_failure "$RUNTIME" phase bad-fix session-bad-fix ARCHIVE
"$RUNTIME" cleanup bad-fix session-bad-fix BLOCKED

new_change bad-final session-bad-final
"$RUNTIME" phase bad-final session-bad-final IMPLEMENT
"$RUNTIME" phase bad-final session-bad-final VERIFY
"$RUNTIME" phase bad-final session-bad-final FINAL_VERIFY
expect_failure "$RUNTIME" phase bad-final session-bad-final IMPLEMENT
"$RUNTIME" cleanup bad-final session-bad-final BLOCKED

new_change bad-deploy session-bad-deploy
"$RUNTIME" phase bad-deploy session-bad-deploy IMPLEMENT
"$RUNTIME" phase bad-deploy session-bad-deploy VERIFY
"$RUNTIME" phase bad-deploy session-bad-deploy FINAL_VERIFY
"$RUNTIME" phase bad-deploy session-bad-deploy RELEASE
"$RUNTIME" phase bad-deploy session-bad-deploy DEPLOY_VERIFY
expect_failure "$RUNTIME" phase bad-deploy session-bad-deploy VERIFY
"$RUNTIME" cleanup bad-deploy session-bad-deploy BLOCKED

new_change bad-archive session-bad-archive
"$RUNTIME" phase bad-archive session-bad-archive IMPLEMENT
"$RUNTIME" phase bad-archive session-bad-archive VERIFY
"$RUNTIME" phase bad-archive session-bad-archive FINAL_VERIFY
"$RUNTIME" phase bad-archive session-bad-archive ARCHIVE
expect_failure "$RUNTIME" phase bad-archive session-bad-archive IMPLEMENT
"$RUNTIME" cleanup bad-archive session-bad-archive BLOCKED

new_change phase-owner session-phase-owner
expect_failure "$RUNTIME" phase phase-owner session-other IMPLEMENT
"$RUNTIME" unlock phase-owner session-phase-owner
expect_failure "$RUNTIME" phase phase-owner session-phase-owner IMPLEMENT
"$RUNTIME" lock phase-owner session-phase-owner
"$RUNTIME" cleanup phase-owner session-phase-owner BLOCKED

new_change phase-mismatch session-phase-mismatch
state_mismatch="$workspace/.ops/changes/phase-mismatch/runtime/state.json"
jq '.session_id = "session-other"' "$state_mismatch" >"$state_mismatch.tmp"
mv -- "$state_mismatch.tmp" "$state_mismatch"
expect_failure "$RUNTIME" phase phase-mismatch session-phase-mismatch IMPLEMENT
jq '.session_id = "session-phase-mismatch"' "$state_mismatch" >"$state_mismatch.tmp"
mv -- "$state_mismatch.tmp" "$state_mismatch"
"$RUNTIME" cleanup phase-mismatch session-phase-mismatch BLOCKED

"$RUNTIME" lock change-a session-a
expect_failure "$RUNTIME" lock change-a session-other
expect_failure "$RUNTIME" unlock change-a session-other
expect_failure "$RUNTIME" init change-a session-other codex
"$RUNTIME" init change-a session-a codex
"$RUNTIME" phase change-a session-a IMPLEMENT
payload_a="$(jq -nc --arg cwd "$workspace" --arg sid session-a '{cwd: $cwd, session_id: $sid}')"
expect_hook_logs_active "$payload_a"
"$RUNTIME" cleanup change-a session-a BLOCKED
printf '%s' "$payload_a" | "$HOOK" >/dev/null

"$RUNTIME" lock change-owner session-owner
"$RUNTIME" init change-owner session-owner codex
"$RUNTIME" lock-repos change-owner session-owner "$web_worktree"
"$RUNTIME" lock change-conflict session-conflict
"$RUNTIME" init change-conflict session-conflict codex
expect_failure "$RUNTIME" lock-repos change-conflict session-conflict "$web_worktree"
expect_failure "$RUNTIME" lock-repos random-change random-session "$mw"
"$RUNTIME" cleanup change-conflict session-conflict BLOCKED
"$RUNTIME" lock change-independent session-independent
"$RUNTIME" init change-independent session-independent codex
"$RUNTIME" lock-repos change-independent session-independent "$mw"
"$RUNTIME" unlock-repos change-independent session-independent
"$RUNTIME" cleanup change-independent session-independent BLOCKED
"$RUNTIME" unlock-repos change-owner session-owner
"$RUNTIME" cleanup change-owner session-owner BLOCKED

"$RUNTIME" lock change-holder session-holder
"$RUNTIME" init change-holder session-holder codex
"$RUNTIME" lock-repos change-holder session-holder "$web_worktree"
"$RUNTIME" lock change-partial session-partial
"$RUNTIME" init change-partial session-partial codex
expect_failure "$RUNTIME" lock-repos change-partial session-partial "$mw" "$web_worktree"
"$RUNTIME" lock-repos change-partial session-partial "$mw"
"$RUNTIME" unlock-repos change-partial session-partial
"$RUNTIME" cleanup change-partial session-partial BLOCKED
"$RUNTIME" cleanup change-holder session-holder BLOCKED

mock_bin="$tmp/mock-bin"
mkdir -p -- "$mock_bin"
cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_codex_sdk_cli.py" "$mock_bin/codex"
chmod +x "$mock_bin/codex"
export FAKE_SDK_TRACE="$tmp/sdk-trace" FAKE_SDK_RESULT_TEXT=$'OK\nFINAL_VERIFY_GATE: PASS\nP0_FINDINGS: 0\nP1_FINDINGS: 0\nOBJECTIVE_GATES: PASS'

"$RUNTIME" lock change-runner session-runner
"$RUNTIME" init change-runner session-runner codex
"$RUNTIME" phase change-runner session-runner IMPLEMENT
"$RUNTIME" lock-repos change-runner session-runner "$web_worktree"
PATH="$mock_bin:/usr/bin:/bin" FAKE_CODEX_MODE=complete CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$web_worktree" IMPLEMENT
test "$(cat "$(find "$workspace/.ops/changes/change-runner/runtime/logs" -name 'codex-implement-round-0-direct-*.exit' -print -quit)")" = 0 || fail 'successful Codex phase was not recorded'
grep -Fq '"method": "thread/start"' "$tmp/sdk-trace" || fail 'Codex SDK thread was not started'
grep -Fq '"method": "turn/start"' "$tmp/sdk-trace" || fail 'Codex SDK turn was not started'

"$RUNTIME" lock change-no-repo session-no-repo
"$RUNTIME" init change-no-repo session-no-repo codex
"$RUNTIME" phase change-no-repo session-no-repo IMPLEMENT
expect_failure env PATH="$mock_bin:/usr/bin:/bin" \
  "$RUNNER" change-no-repo "$web_worktree" IMPLEMENT
"$RUNTIME" cleanup change-no-repo session-no-repo BLOCKED

"$RUNTIME" lock change-repo-owner session-repo-owner
"$RUNTIME" init change-repo-owner session-repo-owner codex
"$RUNTIME" lock-repos change-repo-owner session-repo-owner "$mw"
"$RUNTIME" lock change-repo-denied session-repo-denied
"$RUNTIME" init change-repo-denied session-repo-denied codex
"$RUNTIME" phase change-repo-denied session-repo-denied IMPLEMENT
expect_failure env PATH="$mock_bin:/usr/bin:/bin" \
  "$RUNNER" change-repo-denied "$mw" IMPLEMENT
"$RUNTIME" cleanup change-repo-denied session-repo-denied BLOCKED
"$RUNTIME" cleanup change-repo-owner session-repo-owner BLOCKED

"$RUNTIME" phase change-runner session-runner VERIFY
"$RUNTIME" fix change-runner session-runner
printf '%s\n' 'Fix the regression from verification.' \
  >"$workspace/.ops/changes/change-runner/runtime/verification-findings-round-1.md"
expect_failure env PATH="$mock_bin:/usr/bin:/bin" FAKE_CODEX_RESULT=implementation CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$(find "$workspace/.ops/changes/change-runner/runtime/logs" -name 'codex-fix-round-1-direct-*.exit' -print -quit)")" = 1 || fail 'Codex failure was not recorded'
test "$(cat "$(find "$workspace/.ops/changes/change-runner/runtime/logs" -name 'codex-fix-round-1-direct-*.result-class' -print -quit)")" = implementation-error || { cat "$tmp/sdk-trace" >&2; fail 'Codex implementation failure class was not recorded'; }

"$RUNTIME" phase change-runner session-runner VERIFY
"$RUNTIME" fix change-runner session-runner
printf '%s\n' 'Fix the timeout finding from verification.' \
  >"$workspace/.ops/changes/change-runner/runtime/verification-findings-round-2.md"
expect_failure env PATH="$mock_bin:/usr/bin:/bin" FAKE_CODEX_MODE=delay FAKE_SDK_DELAY_SECONDS=2 CODEX_TIMEOUT_SECONDS=1 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$(find "$workspace/.ops/changes/change-runner/runtime/logs" -name 'codex-fix-round-2-direct-*.exit' -print -quit)")" = 1 || fail 'Codex timeout was not bounded'
test "$(cat "$(find "$workspace/.ops/changes/change-runner/runtime/logs" -name 'codex-fix-round-2-direct-*.result-class' -print -quit)")" = timeout || fail 'Codex timeout class was not recorded'
expect_failure env PATH="$tmp/no-codex:/usr/bin:/bin" "$RUNNER" change-runner "$web_worktree" FIX
"$RUNTIME" cleanup change-runner session-runner FAILED

"$RUNTIME" lock change-fix-limit session-limit
"$RUNTIME" init change-fix-limit session-limit codex
"$RUNTIME" phase change-fix-limit session-limit IMPLEMENT
"$RUNTIME" phase change-fix-limit session-limit VERIFY
"$RUNTIME" lock-repos change-fix-limit session-limit "$web_worktree"
"$RUNTIME" fix change-fix-limit session-limit
"$RUNTIME" phase change-fix-limit session-limit VERIFY
"$RUNTIME" fix change-fix-limit session-limit
"$RUNTIME" phase change-fix-limit session-limit VERIFY
"$RUNTIME" fix change-fix-limit session-limit
"$RUNTIME" phase change-fix-limit session-limit VERIFY
expect_failure "$RUNTIME" fix change-fix-limit session-limit
test "$(jq -r '.phase' "$workspace/.ops/changes/change-fix-limit/runtime/state.json")" = BLOCKED || fail 'fourth fix round did not block'
test ! -d "$workspace/.ops/changes/change-fix-limit/runtime/lock" || fail 'change lock survived max-round cleanup'
repo_owner_count="$(find "$workspace/.ops/runtime/repo-locks" -mindepth 2 -maxdepth 2 -type f -name owner.json -print0 \
  | xargs -0 -r jq -r --arg change change-fix-limit 'select(.change == $change) | .change' \
  | wc -l)"
test "$repo_owner_count" = 0 || fail 'fourth fix did not release repository locks'
active_after_limit="$("$RUNTIME" active "$workspace" || true)"
test -z "$active_after_limit" || fail "max-round cleanup left active workflow: $active_after_limit"

"$RUNTIME" lock hook-a session-hook-a
"$RUNTIME" init hook-a session-hook-a codex
"$RUNTIME" phase hook-a session-hook-a IMPLEMENT
"$RUNTIME" lock hook-b session-hook-b
"$RUNTIME" init hook-b session-hook-b codex
"$RUNTIME" phase hook-b session-hook-b IMPLEMENT
payload_a="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-hook-a"}')"
payload_b="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-hook-b"}')"
payload_unowned="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-unowned"}')"
expect_hook_logs_active "$payload_a"
expect_hook_logs_active "$payload_b"
"$RUNTIME" cleanup hook-a session-hook-a BLOCKED
expect_hook_logs_active "$payload_b"
"$RUNTIME" cleanup hook-b session-hook-b BLOCKED
printf '%s' "$payload_unowned" | "$HOOK" >/dev/null

"$RUNTIME" lock change-cleanup-done session-cleanup-done
"$RUNTIME" init change-cleanup-done session-cleanup-done codex
expect_failure "$RUNTIME" cleanup change-cleanup-done session-cleanup-done DONE
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done DONE
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done BLOCKED
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done FAILED
"$RUNTIME" cleanup change-cleanup-done session-cleanup-done BLOCKED

"$RUNTIME" lock change-plan session-plan
"$RUNTIME" init change-plan session-plan codex
expect_failure "$RUNTIME" archive change-plan session-plan
"$RUNTIME" cleanup change-plan session-plan BLOCKED

"$RUNTIME" lock change-verify session-verify
"$RUNTIME" init change-verify session-verify codex
"$RUNTIME" phase change-verify session-verify IMPLEMENT
"$RUNTIME" phase change-verify session-verify VERIFY
expect_failure "$RUNTIME" archive change-verify session-verify
"$RUNTIME" cleanup change-verify session-verify BLOCKED

"$RUNTIME" lock change-archive session-archive
"$RUNTIME" init change-archive session-archive codex
"$RUNTIME" lock-repos change-archive session-archive "$web_worktree"
"$RUNTIME" phase change-archive session-archive IMPLEMENT
"$RUNTIME" phase change-archive session-archive VERIFY
"$RUNTIME" phase change-archive session-archive FINAL_VERIFY
"$RUNTIME" phase change-archive session-archive ARCHIVE
archive_path="$("$RUNTIME" complete change-archive session-archive)"
test "$(jq -r '.phase' "$archive_path/runtime/state.json")" = DONE || fail 'archive did not finalize state'
test ! -d "$workspace/.ops/changes/change-archive/runtime/lock" || fail 'change lock survived completion'
"$RUNTIME" lock change-reuse session-reuse
"$RUNTIME" init change-reuse session-reuse codex
"$RUNTIME" lock-repos change-reuse session-reuse "$web_worktree"
"$RUNTIME" cleanup change-reuse session-reuse BLOCKED

printf '%s\n' 'test_ops_orchestration: all checks passed'
