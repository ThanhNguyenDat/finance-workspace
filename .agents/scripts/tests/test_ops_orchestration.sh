#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"
RUNTIME="$ROOT_DIR/.agents/scripts/ops-runtime.sh"
RUNNER="$ROOT_DIR/.agents/scripts/run-codex-phase.sh"
HOOK="$ROOT_DIR/.claude/hooks/ops-stop-hook.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
export OPS_ROOT="$tmp"
repo="$ROOT_DIR"

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
grep -Fq '.ops/**/runtime/' "$ROOT_DIR/.gitignore" || fail 'runtime ignore rule missing'

"$RUNTIME" lock change-a session-a
expect_failure "$RUNTIME" lock change-a session-other
expect_failure "$RUNTIME" unlock change-a session-other
"$RUNTIME" init change-a session-a
"$RUNTIME" phase change-a IMPLEMENT 0
payload_a="$(jq -nc --arg cwd "$tmp" --arg sid session-a '{cwd: $cwd, session_id: $sid}')"
expect_hook_blocked "$payload_a"

"$RUNTIME" phase change-a DONE 0
printf '%s' "$payload_a" | "$HOOK" >/dev/null
"$RUNTIME" unlock change-a session-a

mock_bin="$tmp/mock-bin"
mkdir -p -- "$mock_bin"
cat >"$mock_bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -Eeuo pipefail
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
PATH="$mock_bin:$PATH" MOCK_CODEX_MODE=success CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$repo" IMPLEMENT
test "$(cat "$tmp/.ops/changes/change-runner/runtime/logs/codex-implement-round-0.exit")" = 0 || fail 'successful Codex phase was not recorded'

"$RUNTIME" round change-runner >/dev/null
"$RUNTIME" phase change-runner FIX 1
expect_failure env PATH="$mock_bin:$PATH" MOCK_CODEX_MODE=failure CODEX_TIMEOUT_SECONDS=2 \
  "$RUNNER" change-runner "$repo" FIX
test "$(cat "$tmp/.ops/changes/change-runner/runtime/logs/codex-fix-round-1.exit")" = 7 || fail 'Codex failure was not recorded'

"$RUNTIME" round change-runner >/dev/null
"$RUNTIME" phase change-runner FIX 2
expect_failure env PATH="$mock_bin:$PATH" MOCK_CODEX_MODE=timeout CODEX_TIMEOUT_SECONDS=1 \
  "$RUNNER" change-runner "$repo" FIX
test "$(cat "$tmp/.ops/changes/change-runner/runtime/logs/codex-fix-round-2.exit")" = 124 || fail 'Codex timeout was not bounded'

expect_failure env PATH="$tmp/no-codex:/usr/bin:/bin" "$RUNNER" change-runner "$repo" FIX
"$RUNTIME" phase change-runner BLOCKED 2
"$RUNTIME" unlock change-runner session-runner

"$RUNTIME" lock change-b session-b
"$RUNTIME" init change-b session-b
"$RUNTIME" phase change-b IMPLEMENT 0
"$RUNTIME" lock change-c session-c
"$RUNTIME" init change-c session-c
"$RUNTIME" phase change-c IMPLEMENT 0
payload_empty_session="$(jq -nc --arg cwd "$tmp" '{cwd: $cwd}')"
expect_hook_blocked "$payload_empty_session"
payload_other_session="$(jq -nc --arg cwd "$tmp" '{cwd: $cwd, session_id: "session-other"}')"
expect_hook_blocked "$payload_other_session"
"$RUNTIME" phase change-c BLOCKED 0
expect_hook_blocked "$payload_empty_session"
"$RUNTIME" phase change-b DONE 0
"$RUNTIME" unlock change-b session-b
"$RUNTIME" unlock change-c session-c
printf '%s' "$payload_empty_session" | "$HOOK" >/dev/null
archive_path="$("$RUNTIME" archive change-b)"
test -d "$archive_path" || fail 'archive destination was not created'
test ! -d "$tmp/.ops/changes/change-b" || fail 'change directory was not moved'
test "$(jq -r '.phase' "$archive_path/runtime/state.json")" = DONE || fail 'archived state was not finalized'

printf '%s\n' 'test_ops_orchestration: all checks passed'
