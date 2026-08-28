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

"$RUNTIME" lock change-a session-a
expect_failure "$RUNTIME" lock change-a session-other
expect_failure "$RUNTIME" unlock change-a session-other
"$RUNTIME" init change-a session-a
"$RUNTIME" phase change-a IMPLEMENT 0
payload_a="$(jq -nc --arg cwd "$workspace" --arg sid session-a '{cwd: $cwd, session_id: $sid}')"
expect_hook_blocked "$payload_a"
"$RUNTIME" cleanup change-a session-a BLOCKED
printf '%s' "$payload_a" | "$HOOK" >/dev/null

"$RUNTIME" lock change-a session-a
expect_failure "$RUNTIME" lock change-a session-other
"$RUNTIME" cleanup change-a session-a BLOCKED

"$RUNTIME" lock change-owner session-owner
"$RUNTIME" init change-owner session-owner
"$RUNTIME" lock-repos change-owner session-owner "$web_worktree"
expect_failure "$RUNTIME" lock-repos change-conflict session-conflict "$web_worktree"
"$RUNTIME" lock-repos change-independent session-independent "$mw"
"$RUNTIME" unlock-repos change-independent session-independent
"$RUNTIME" unlock-repos change-owner session-owner
"$RUNTIME" cleanup change-owner session-owner BLOCKED
"$RUNTIME" cleanup change-a session-a FAILED

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

"$RUNTIME" lock change-runner session-runner
"$RUNTIME" init change-runner session-runner
"$RUNTIME" phase change-runner IMPLEMENT 0
MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" \
  MOCK_CODEX_MODE=success CODEX_TIMEOUT_SECONDS=2 "$RUNNER" change-runner "$web_worktree" IMPLEMENT
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-implement-round-0.exit")" = 0 || fail 'successful Codex phase was not recorded'
grep -Fxq -- '--cd' "$tmp/mock-args" || fail 'Codex primary cwd flag missing'
grep -Fxq -- "$workspace" "$tmp/mock-args" || fail 'Codex primary cwd was not finance-workspace'
grep -Fxq -- '--add-dir' "$tmp/mock-args" || fail 'Codex additional directory flag missing'
grep -Fxq -- "$web_worktree" "$tmp/mock-args" || fail 'Codex writable repository was not passed'
grep -Fxq -- '--approve-for-me' "$tmp/mock-args" || fail 'Codex non-interactive approval flag missing'

"$RUNTIME" round change-runner session-runner >/dev/null
"$RUNTIME" phase change-runner FIX 1
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" MOCK_CODEX_MODE=failure CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-fix-round-1.exit")" = 7 || fail 'Codex failure was not recorded'

"$RUNTIME" round change-runner session-runner >/dev/null
"$RUNTIME" phase change-runner FIX 2
expect_failure env MOCK_PWD_FILE="$tmp/mock-pwd" MOCK_ARGS_FILE="$tmp/mock-args" PATH="$mock_bin:/usr/bin:/bin" MOCK_CODEX_MODE=timeout CODEX_TIMEOUT_SECONDS=1 \
  "$RUNNER" change-runner "$web_worktree" FIX
test "$(cat "$workspace/.ops/changes/change-runner/runtime/logs/codex-fix-round-2.exit")" = 124 || fail 'Codex timeout was not bounded'
expect_failure env PATH="$tmp/no-codex:/usr/bin:/bin" "$RUNNER" change-runner "$web_worktree" FIX
"$RUNTIME" cleanup change-runner session-runner FAILED

"$RUNTIME" lock change-fix-limit session-limit
"$RUNTIME" init change-fix-limit session-limit
"$RUNTIME" phase change-fix-limit FIX 0
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
"$RUNTIME" phase hook-a IMPLEMENT 0
"$RUNTIME" lock hook-b session-hook-b
"$RUNTIME" init hook-b session-hook-b
"$RUNTIME" phase hook-b IMPLEMENT 0
payload_empty_session="$(jq -nc --arg cwd "$workspace" '{cwd: $cwd}')"
expect_hook_blocked "$payload_empty_session"
"$RUNTIME" cleanup hook-a session-hook-a BLOCKED
"$RUNTIME" cleanup hook-b session-hook-b DONE
printf '%s' "$payload_empty_session" | "$HOOK" >/dev/null

"$RUNTIME" lock change-archive session-archive
"$RUNTIME" init change-archive session-archive
"$RUNTIME" phase change-archive ARCHIVE 0
"$RUNTIME" unlock change-archive session-archive
archive_path="$("$RUNTIME" archive change-archive)"
test "$(jq -r '.phase' "$archive_path/runtime/state.json")" = DONE || fail 'archive did not finalize state'

printf '%s\n' 'test_ops_orchestration: all checks passed'
