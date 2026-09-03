#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
RUNNER="$ROOT_DIR/tools/phase-agent-orchestrator/bin/run-claude-phase.sh"
OPS="$ROOT_DIR/tools/phase-agent-orchestrator/bin/ops-runtime.sh"
STATE="$ROOT_DIR/tools/phase-agent-orchestrator/bin/phase-agent-state.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
workspace="$tmp/workspace"; repo="$tmp/repo"; bin="$tmp/bin"; trace="$tmp/trace"
mkdir -p "$workspace" "$repo" "$bin" "$trace" "$tmp/claude-work" "$workspace/.agents/scripts"
for helper in ops-runtime.sh phase-agent-state.sh quant-research-state.sh run-phase-agent-command.sh classify-claude-result.sh classify-codex-result.sh; do
  cp "$ROOT_DIR/tools/phase-agent-orchestrator/bin/$helper" "$workspace/.agents/scripts/$helper"
done
chmod +x "$workspace/.agents/scripts/"*.sh

git -C "$workspace" init -q
git -C "$workspace" config user.email test@example.invalid
git -C "$workspace" config user.name Test
printf '%s\n' root >"$workspace/README.md"
git -C "$workspace" add README.md
git -C "$workspace" commit -qm init
git -C "$repo" init -q
git -C "$repo" config user.email test@example.invalid
git -C "$repo" config user.name Test
printf '%s\n' app >"$repo/app.txt"
git -C "$repo" add app.txt
git -C "$repo" commit -qm init

cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_claude_sdk_cli.py" "$bin/claude"
chmod +x "$bin/claude"

export PATH="$bin:$PATH" CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1 FAKE_SDK_ACCOUNT_TRACE="$trace/claude.config-dir" FAKE_SDK_RESULT_TEXT="OK"
export OPS_ROOT="$workspace" OPS_WORKSPACE_ROOT="$workspace"
export QUANT_RESEARCH_ROOT="$workspace"
export PHASE_AGENT_STATE_DIR="$workspace/.ops/runtime/phase-agents"
export PHASE_AGENT_LEGACY_QUANT_STATE="$tmp/no-quant"
export PHASE_AGENT_LEGACY_CLAUDE_STATE="$tmp/no-claude"
export PHASE_AGENT_ACCOUNTS_FILE="$tmp/accounts.yaml"
mkdir -p "$tmp/claude-personal"
cat >"$PHASE_AGENT_ACCOUNTS_FILE" <<EOF
claude:
  work: $tmp/claude-work
  personal: $tmp/claude-personal
EOF
export FAKE_TRACE="$trace"
export CLAUDE_TIMEOUT_SECONDS=10

fail() { printf 'test_multi_account_routing: %s\n' "$1" >&2; exit 1; }

"$STATE" init >/dev/null
"$STATE" set plan claude sonnet high work >/dev/null
"$OPS" lock account-lock-test session-test
"$OPS" init account-lock-test session-test
"$OPS" lock-repos account-lock-test session-test "$repo"

set +e
FAKE_SDK_MODE=delay "$RUNNER" account-lock-test "$repo" PLAN >"$trace/first.out" 2>"$trace/first.err" & first_pid=$!
set -e
lock_owner="$workspace/.ops/runtime/account-locks/claude-work/owner.json"
for _ in $(seq 1 50); do [[ -f "$lock_owner" ]] && break; sleep 0.1; done
[[ -f "$lock_owner" ]] || { cat "$trace/first.err" >&2; fail 'account lock was not acquired before the subprocess ran'; }

set +e
"$RUNNER" account-lock-test "$repo" PLAN >/dev/null 2>&1
second_status=$?
wait "$first_pid"
first_status=$?
set -e
[[ "$second_status" -ne 0 ]] || fail 'second same-account attempt was accepted while the first was running'
[[ "$first_status" -eq 0 ]] || fail 'first account attempt did not complete successfully'
[[ ! -e "$lock_owner" ]] || fail 'account lock was not released after subprocess exit'
grep -Fqx -- "$tmp/claude-work" "$trace/claude.config-dir" || fail 'selected Claude account directory was not exported'

"$OPS" unlock-repos account-lock-test session-test
"$OPS" unlock account-lock-test session-test
mkdir -p "$workspace/.claude/commands"
printf '%s\n' 'CANONICAL QUANT PROMPT' >"$workspace/.claude/commands/quant-research.md"
"$STATE" set quant_research claude sonnet high work >/dev/null
"$STATE" candidate-set quant_research 1 claude sonnet high personal >/dev/null
export QUANT_RESEARCH_STATE_DIR="$workspace/.ops/runtime/quant-research"
export FAKE_SDK_MODE=quota-work FAKE_CLAUDE_QUOTA_DIR="$tmp/claude-work"
(cd "$workspace" && ./.agents/scripts/run-phase-agent-command.sh quant-research) >/dev/null

quant_state="$QUANT_RESEARCH_STATE_DIR/state.json"
jq -e '.iteration == 1' "$quant_state" >/dev/null || fail 'quant iteration was not incremented exactly once'
jq -e '.providers.claude.available == true and .providers.claude.accounts.work.available == false' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail 'account-specific quota state was not isolated'
grep -Fqx -- "$tmp/claude-work" "$trace/claude.config-dir" || fail 'work account was not attempted'
grep -Fqx -- "$tmp/claude-personal" "$trace/claude.config-dir" || fail 'personal account was not used for continuation'
find "$workspace/.ops/runtime/phase-agents/quant-runs" -mindepth 2 -maxdepth 2 -name '*.meta.json' -print0 | sort -z -V | xargs -0 jq -s -e 'length == 2 and .[0].account == "work" and .[0].result_class == "global-quota-exhausted" and .[1].account == "personal" and .[1].result_class == "success"' >/dev/null || fail 'same-provider account failover evidence is invalid'

printf '%s\n' 'test_multi_account_routing: all checks passed'
