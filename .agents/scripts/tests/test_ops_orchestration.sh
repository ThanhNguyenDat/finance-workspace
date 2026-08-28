#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.sh"
RUNNER="$ROOT_DIR/.agents/scripts/run-codex-phase.sh"
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
expect_hook_blocked() {
  local payload="$1"
  if printf '%s' "$payload" | "$HOOK" >/dev/null 2>&1; then
    fail 'expected Stop hook to block an active workflow'
  fi
}

jq -e . "$ROOT_DIR/.claude/settings.json" >/dev/null || fail 'invalid Claude settings JSON'
grep -Fq '/ops:run' "$ROOT_DIR/.claude/commands/ops/run.md" || fail 'run command missing namespace'
grep -Fq 'Claude = PLAN + VERIFY + ORCHESTRATE' "$ROOT_DIR/AGENTS.md" || fail 'AGENTS role contract missing'
grep -Fq '.ops/**/runtime/' "$ROOT_DIR/.gitignore" || fail 'runtime ignore rule missing'
lock_line="$(awk '/lock-repos <change>/{print NR; exit}' "$ROOT_DIR/.claude/commands/ops/run.md")"
write_line="$(awk '/create or revise/{print NR; exit}' "$ROOT_DIR/.claude/commands/ops/run.md")"
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
  "$RUNTIME" init "$change" "$session"
}

new_change change-full session-full
"$RUNTIME" lock-repos change-full session-full "$web_worktree"
"$RUNTIME" phase change-full session-full IMPLEMENT
"$RUNTIME" phase change-full session-full VERIFY
"$RUNTIME" phase change-full session-full FIX
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
expect_failure "$RUNTIME" phase bad-verify session-bad-verify RELEASE
"$RUNTIME" cleanup bad-verify session-bad-verify BLOCKED

new_change bad-fix session-bad-fix
"$RUNTIME" phase bad-fix session-bad-fix IMPLEMENT
"$RUNTIME" phase bad-fix session-bad-fix VERIFY
"$RUNTIME" phase bad-fix session-bad-fix FIX
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
expect_failure "$RUNTIME" init change-a session-other
"$RUNTIME" init change-a session-a
"$RUNTIME" phase change-a session-a IMPLEMENT
payload_a="$(jq -nc --arg cwd "$workspace" --arg sid session-a '{cwd: $cwd, session_id: $sid}')"
expect_hook_blocked "$payload_a"
"$RUNTIME" cleanup change-a session-a BLOCKED
printf '%s' "$payload_a" | "$HOOK" >/dev/null

"$RUNTIME" lock change-owner session-owner
"$RUNTIME" init change-owner session-owner
"$RUNTIME" lock-repos change-owner session-owner "$web_worktree"
"$RUNTIME" lock change-conflict session-conflict
"$RUNTIME" init change-conflict session-conflict
expect_failure "$RUNTIME" lock-repos change-conflict session-conflict "$web_worktree"
expect_failure "$RUNTIME" lock-repos random-change random-session "$mw"
"$RUNTIME" cleanup change-conflict session-conflict BLOCKED
"$RUNTIME" lock change-independent session-independent
"$RUNTIME" init change-independent session-independent
"$RUNTIME" lock-repos change-independent session-independent "$mw"
"$RUNTIME" unlock-repos change-independent session-independent
"$RUNTIME" cleanup change-independent session-independent BLOCKED
"$RUNTIME" unlock-repos change-owner session-owner
"$RUNTIME" cleanup change-owner session-owner BLOCKED

"$RUNTIME" lock change-holder session-holder
"$RUNTIME" init change-holder session-holder
"$RUNTIME" lock-repos change-holder session-holder "$web_worktree"
"$RUNTIME" lock change-partial session-partial
"$RUNTIME" init change-partial session-partial
expect_failure "$RUNTIME" lock-repos change-partial session-partial "$mw" "$web_worktree"
"$RUNTIME" lock-repos change-partial session-partial "$mw"
"$RUNTIME" unlock-repos change-partial session-partial
"$RUNTIME" cleanup change-partial session-partial BLOCKED
"$RUNTIME" cleanup change-holder session-holder BLOCKED

mock_bin="$tmp/mock-bin"
mkdir -p -- "$mock_bin"
cat >"$mock_bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
printf '%s\n' "$PWD" >"$MOCK_PWD_FILE"
printf '%s\n' "$@" >"$MOCK_ARGS_FILE"
case "${MOCK_CODEX_MODE:-success}" in
  success) printf '%s\n' '{"type":"result","status":"completed"}' ;;
  failure) printf '%s\n' '{"type":"result","status":"failed"}' >&2; exit 7 ;;
  timeout) sleep 5 ;;
  *) exit 9 ;;
esac
MOCK
chmod +x "$mock_bin/codex"

if command -v codex >/dev/null 2>&1; then
  timeout --signal=TERM --kill-after=10s 15s codex exec --cd "$workspace" \
    --add-dir "$web_worktree" --ephemeral --approve-for-me --help >/dev/null \
    || fail 'selected Codex invocation was rejected by the real CLI parser'
else
  printf '%s\n' 'real Codex parser check skipped: codex is unavailable'
fi

"$RUNTIME" lock change-runner session-runner
"$RUNTIME" init change-runner session-runner
"$RUNTIME" phase change-runner session-runner IMPLEMENT
"$RUNTIME" lock-repos change-runner session-runner "$web_worktree"
MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" \
  MOCK_CODEX_MODE=success CODEX_TIMEOUT_SECONDS=2 "$RUNNER" change-runner "$web_worktree" IMPLEMENT
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-implement-round-0.exit")" = 0 || fail 'successful Codex phase was not recorded'
grep -Fxq -- '--cd' "$tmp/mock-args" || fail 'Codex primary cwd flag missing'
grep -Fxq -- "$workspace" "$tmp/mock-args" || fail 'Codex primary cwd was not finance-workspace'
grep -Fxq -- '--add-dir' "$tmp/mock-args" || fail 'Codex additional directory flag missing'
grep -Fxq -- "$web_worktree" "$tmp/mock-args" || fail 'Codex writable repository was not passed'
grep -Fxq -- '--approve-for-me' "$tmp/mock-args" || fail 'Codex non-interactive approval flag missing'
test "$(grep -Fc -- '--sandbox' "$tmp/mock-args" || true)" = 0 || fail 'conflicting sandbox flag was passed'

"$RUNTIME" lock change-no-repo session-no-repo
"$RUNTIME" init change-no-repo session-no-repo
"$RUNTIME" phase change-no-repo session-no-repo IMPLEMENT
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" \
  "$RUNNER" change-no-repo "$web_worktree" IMPLEMENT
"$RUNTIME" cleanup change-no-repo session-no-repo BLOCKED

"$RUNTIME" lock change-repo-owner session-repo-owner
"$RUNTIME" init change-repo-owner session-repo-owner
"$RUNTIME" lock-repos change-repo-owner session-repo-owner "$mw"
"$RUNTIME" lock change-repo-denied session-repo-denied
"$RUNTIME" init change-repo-denied session-repo-denied
"$RUNTIME" phase change-repo-denied session-repo-denied IMPLEMENT
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" \
  "$RUNNER" change-repo-denied "$mw" IMPLEMENT
"$RUNTIME" cleanup change-repo-denied session-repo-denied BLOCKED
"$RUNTIME" cleanup change-repo-owner session-repo-owner BLOCKED

"$RUNTIME" round change-runner session-runner >/dev/null
"$RUNTIME" phase change-runner session-runner VERIFY
"$RUNTIME" phase change-runner session-runner FIX
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" MOCK_CODEX_MODE=failure CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-fix-round-1.exit")" = 7 || fail 'Codex failure was not recorded'

"$RUNTIME" round change-runner session-runner >/dev/null
"$RUNTIME" phase change-runner session-runner VERIFY
"$RUNTIME" phase change-runner session-runner FIX
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" MOCK_CODEX_MODE=timeout CODEX_TIMEOUT_SECONDS=1 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-fix-round-2.exit")" = 124 || fail 'Codex timeout was not bounded'
expect_failure env PATH="$tmp/no-codex:/usr/bin:/bin" "$RUNNER" change-runner "$web_worktree" FIX
"$RUNTIME" cleanup change-runner session-runner FAILED

"$RUNTIME" lock change-fix-limit session-limit
"$RUNTIME" init change-fix-limit session-limit
"$RUNTIME" phase change-fix-limit session-limit IMPLEMENT
"$RUNTIME" phase change-fix-limit session-limit VERIFY
"$RUNTIME" phase change-fix-limit session-limit FIX
"$RUNTIME" lock-repos change-fix-limit session-limit "$web_worktree"
"$RUNTIME" round change-fix-limit session-limit >/dev/null
"$RUNTIME" round change-fix-limit session-limit >/dev/null
"$RUNTIME" round change-fix-limit session-limit >/dev/null
expect_failure "$RUNTIME" round change-fix-limit session-limit
test "$(jq -r '.phase' "$workspace/.ops/changes/change-fix-limit/runtime/state.json")" = BLOCKED || fail 'fourth fix round did not block'
test ! -d "$workspace/.ops/changes/change-fix-limit/runtime/lock" || fail 'change lock survived max-round cleanup'
active_after_limit="$("$RUNTIME" active "$workspace" || true)"
test -z "$active_after_limit" || fail "max-round cleanup left active workflow: $active_after_limit"

"$RUNTIME" lock hook-a session-hook-a
"$RUNTIME" init hook-a session-hook-a
"$RUNTIME" phase hook-a session-hook-a IMPLEMENT
"$RUNTIME" lock hook-b session-hook-b
"$RUNTIME" init hook-b session-hook-b
"$RUNTIME" phase hook-b session-hook-b IMPLEMENT
payload_a="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-hook-a"}')"
payload_b="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-hook-b"}')"
payload_unowned="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd, session_id: "session-unowned"}')"
expect_hook_blocked "$payload_a"
expect_hook_blocked "$payload_b"
"$RUNTIME" cleanup hook-a session-hook-a BLOCKED
expect_hook_blocked "$payload_b"
"$RUNTIME" cleanup hook-b session-hook-b BLOCKED
printf '%s' "$payload_unowned" | "$HOOK" >/dev/null

"$RUNTIME" lock change-cleanup-done session-cleanup-done
"$RUNTIME" init change-cleanup-done session-cleanup-done
expect_failure "$RUNTIME" cleanup change-cleanup-done session-cleanup-done DONE
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done DONE
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done BLOCKED
expect_failure "$RUNTIME" phase change-cleanup-done session-cleanup-done FAILED
"$RUNTIME" cleanup change-cleanup-done session-cleanup-done BLOCKED

"$RUNTIME" lock change-plan session-plan
"$RUNTIME" init change-plan session-plan
expect_failure "$RUNTIME" archive change-plan session-plan
"$RUNTIME" cleanup change-plan session-plan BLOCKED

"$RUNTIME" lock change-verify session-verify
"$RUNTIME" init change-verify session-verify
"$RUNTIME" phase change-verify session-verify IMPLEMENT
"$RUNTIME" phase change-verify session-verify VERIFY
expect_failure "$RUNTIME" archive change-verify session-verify
"$RUNTIME" cleanup change-verify session-verify BLOCKED

"$RUNTIME" lock change-archive session-archive
"$RUNTIME" init change-archive session-archive
"$RUNTIME" lock-repos change-archive session-archive "$web_worktree"
"$RUNTIME" phase change-archive session-archive IMPLEMENT
"$RUNTIME" phase change-archive session-archive VERIFY
"$RUNTIME" phase change-archive session-archive FINAL_VERIFY
"$RUNTIME" phase change-archive session-archive ARCHIVE
archive_path="$("$RUNTIME" complete change-archive session-archive)"
test "$(jq -r '.phase' "$archive_path/runtime/state.json")" = DONE || fail 'archive did not finalize state'
test ! -d "$workspace/.ops/changes/change-archive/runtime/lock" || fail 'change lock survived completion'
"$RUNTIME" lock change-reuse session-reuse
"$RUNTIME" init change-reuse session-reuse
"$RUNTIME" lock-repos change-reuse session-reuse "$web_worktree"
"$RUNTIME" cleanup change-reuse session-reuse BLOCKED

printf '%s\n' 'test_ops_orchestration: all checks passed'
