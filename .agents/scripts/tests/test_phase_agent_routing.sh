#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
RUNNER="$ROOT_DIR/.agents/scripts/run-phase-agent.py"; OPS="$ROOT_DIR/.agents/scripts/ops-runtime.py"; STATE="$ROOT_DIR/.agents/scripts/phase-agent-state.py"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
workspace="$tmp/workspace"; repo="$tmp/repo"; bin="$tmp/bin"; trace="$tmp/trace"; mkdir -p "$workspace/.agents/scripts" "$repo" "$bin" "$trace"
cp "$ROOT_DIR/.agents/scripts/"*.py "$workspace/.agents/scripts/"
git -C "$workspace" init -q; git -C "$workspace" config user.email test@example.invalid; git -C "$workspace" config user.name Test
printf '%s\n' '.ops/**/runtime/' >"$workspace/.gitignore"; printf '%s\n' root >"$workspace/README.md"; git -C "$workspace" add .; git -C "$workspace" commit -qm init
git -C "$repo" init -q; git -C "$repo" config user.email test@example.invalid; git -C "$repo" config user.name Test; printf '%s\n' app >"$repo/app.txt"; git -C "$repo" add .; git -C "$repo" commit -qm init
mkdir "$repo/untracked-target"; ln -s untracked-target "$repo/untracked-directory-link"
cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_codex_sdk_cli.py" "$bin/codex"
cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_claude_sdk_cli.py" "$bin/claude"
chmod +x "$bin/codex" "$bin/claude" "$workspace/.agents/scripts/"*.py
export PATH="$bin:$PATH" OPS_ROOT="$workspace" OPS_WORKSPACE_ROOT="$workspace" PHASE_AGENT_STATE_DIR="$workspace/.ops/runtime/phase-agents" PHASE_AGENT_LEGACY_QUANT_STATE="$tmp/no-quant" PHASE_AGENT_LEGACY_CLAUDE_STATE="$tmp/no-claude" FAKE_SDK_TRACE="$trace/sdk.jsonl" FAKE_REPO="$repo" CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1 FAKE_SDK_MODE=complete FAKE_SDK_RESULT_TEXT=$'OK\nFINAL_VERIFY_GATE: PASS\nP0_FINDINGS: 0\nP1_FINDINGS: 0\nOBJECTIVE_GATES: PASS' CODEX_TIMEOUT_SECONDS=5 CLAUDE_TIMEOUT_SECONDS=5
fail() { printf 'test_phase_agent_routing: %s\n' "$1" >&2; exit 1; }
session=session-test; change=agent-route
"$STATE" init >/dev/null; "$OPS" lock "$change" "$session"; "$OPS" init "$change" "$session"; "$OPS" lock-repos "$change" "$session" "$repo"
"$RUNNER" "$change" "$repo" PLAN >/dev/null
jq -e '.attempts|length==1 and .[0].provider=="claude" and .[0].phase=="PLAN"' "$workspace/.ops/changes/$change/runtime/state.json" >/dev/null || fail 'PLAN did not route to Claude'
grep -Fq '"type": "user"' "$trace/sdk.jsonl" || fail 'Claude SDK did not receive a user turn'

"$OPS" phase "$change" "$session" IMPLEMENT
FAKE_SDK_MODE=quota-mutate "$RUNNER" "$change" "$repo" IMPLEMENT >/dev/null
state_file="$workspace/.ops/changes/$change/runtime/state.json"
jq -e '.round==0 and (.attempts|length)==3 and .attempts[1].provider=="codex" and .attempts[1].result_class=="global-quota-exhausted" and .attempts[1].worktree_changed and .attempts[2].provider=="claude" and .attempts[2].continuation and .attempts[2].result_class=="success"' "$state_file" >/dev/null || fail 'quota continuation history invalid'
grep -Fq 'continuation after provider interruption' "$trace/sdk.jsonl" || fail 'continuation prompt missing'
grep -Fq '"method": "turn/start"' "$trace/sdk.jsonl" || fail 'Codex SDK did not receive a turn'

"$OPS" phase "$change" "$session" VERIFY
mkdir "$workspace/.ops/changes/$change/runtime/.phase-attempt-lock"; printf '%s\n' "$$" >"$workspace/.ops/changes/$change/runtime/.phase-attempt-lock/pid"
if "$RUNNER" "$change" "$repo" VERIFY >/dev/null 2>&1; then fail 'concurrent phase lease was ignored'; fi
rm -rf -- "$workspace/.ops/changes/$change/runtime/.phase-attempt-lock"
set +e; FAKE_SDK_MODE=mutate "$RUNNER" "$change" "$repo" VERIFY >/dev/null 2>&1; mutation_status=$?; set -e
[[ "$mutation_status" -ne 0 ]] || fail 'verifier mutation passed'
rm -f -- "$repo/verify-mutation.txt"
"$RUNNER" "$change" "$repo" VERIFY >/dev/null
"$OPS" phase "$change" "$session" FINAL_VERIFY; "$STATE" provider-on codex >/dev/null; "$STATE" set final_verify codex gpt-5.6-terra high >/dev/null
if FAKE_SDK_MODE=no-gate "$RUNNER" "$change" "$repo" FINAL_VERIFY >/dev/null 2>&1; then fail 'FINAL_VERIFY passed without objective-gate attestation'; fi
if "$OPS" phase "$change" "$session" RELEASE >/dev/null 2>&1; then fail 'release accepted failed objective gates'; fi
"$RUNNER" "$change" "$repo" FINAL_VERIFY >/dev/null
grep -Fq 'resolver appends this attempt' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY current-attempt guidance missing'
grep -Fq 'Do not issue shell commands containing rm, rm -f, git reset, or git checkout' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY destructive-command guard missing'
grep -Fq 'sequentially; do not launch exploratory scans' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY bounded-check guidance missing'
grep -Fq 'This is the pre-push gate' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY pre-push gate guidance missing'
grep -Fq 'active change task that explicitly covers push/CI' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY pending push task guidance missing'
grep -Fq 'do not run unscoped `git diff --check HEAD`' "$trace/sdk.jsonl" || fail 'FINAL_VERIFY dirty-tree scope guidance missing'
jq -e '.verification_evidence.separation=="provider-independent" and .verification_evidence.mutator_provider=="claude" and .verification_evidence.verifier_provider=="codex" and .verification_evidence.final_result=="success" and .verification_evidence.objective_gates_passed' "$state_file" >/dev/null || fail 'verification derivation invalid'
"$OPS" phase "$change" "$session" RELEASE

attempt_count="$(jq '.attempts|length' "$state_file")"; [[ "$attempt_count" -eq 7 ]] || fail 'attempt history length changed unexpectedly'
find "$workspace/.ops/changes/$change/runtime/logs" -name '*.attempt.json' | wc -l | grep -Fqx '7' || fail 'attempt evidence missing'
if jq -e '..|objects|has("environment") or has("prompt")' "$state_file" >/dev/null; then fail 'unsafe attempt fields serialized'; fi
"$OPS" unlock-repos agent-route session-test

change=same-provider; session=session-same
"$STATE" set implement claude sonnet high >/dev/null; "$STATE" set fix claude opus high >/dev/null; "$STATE" set final_verify claude opus high >/dev/null
"$OPS" lock "$change" "$session"; "$OPS" init "$change" "$session"; "$OPS" lock-repos "$change" "$session" "$repo"
"$RUNNER" "$change" "$repo" PLAN >/dev/null; "$OPS" phase "$change" "$session" IMPLEMENT; "$RUNNER" "$change" "$repo" IMPLEMENT >/dev/null
"$OPS" phase "$change" "$session" VERIFY; "$RUNNER" "$change" "$repo" VERIFY >/dev/null
"$OPS" fix "$change" "$session"; printf '%s\n' 'P1 current round only' >"$workspace/.ops/changes/$change/runtime/verification-findings-round-1.md"; "$RUNNER" "$change" "$repo" FIX >/dev/null
grep -Fq 'P1 current round only' "$trace/sdk.jsonl" || fail 'FIX current findings missing'
"$OPS" phase "$change" "$session" VERIFY; "$RUNNER" "$change" "$repo" VERIFY >/dev/null; "$OPS" phase "$change" "$session" FINAL_VERIFY; "$RUNNER" "$change" "$repo" FINAL_VERIFY >/dev/null
same_state="$workspace/.ops/changes/$change/runtime/state.json"
jq -e '.round==1 and .verification_evidence.separation=="same-provider-process-separated" and .verification_evidence.mutator_provider=="claude" and .verification_evidence.verifier_provider=="claude"' "$same_state" >/dev/null || fail 'same-provider verification label invalid'
"$OPS" phase "$change" "$session" RELEASE
"$OPS" unlock-repos "$change" "$session"

change=env-override; session=session-env
"$STATE" provider-on codex >/dev/null; "$OPS" lock "$change" "$session"; "$OPS" init "$change" "$session"; "$OPS" lock-repos "$change" "$session" "$repo"
PHASE_AGENT_PLAN_PROVIDER=codex PHASE_AGENT_PLAN_MODEL=override-model PHASE_AGENT_PLAN_EFFORT=medium "$RUNNER" "$change" "$repo" PLAN >/dev/null
jq -e '.attempts[0].provider=="codex" and .attempts[0].model=="override-model" and .attempts[0].effort=="medium"' "$workspace/.ops/changes/$change/runtime/state.json" >/dev/null || fail 'environment override precedence failed'
if PHASE_AGENT_PLAN_PROVIDER=claude PHASE_AGENT_PLAN_MODEL=opus PHASE_AGENT_PLAN_EFFORT=low "$RUNNER" "$change" "$repo" PLAN >/dev/null 2>&1; then fail 'invalid environment override was accepted'; fi

change=workspace-only; session=session-workspace
"$OPS" lock "$change" "$session"; "$OPS" init "$change" "$session"; "$OPS" lock-repos "$change" "$session" "$workspace"
"$RUNNER" "$change" "$workspace" PLAN >/dev/null
jq -e '.attempts|length==1 and .[0].provider=="claude" and .[0].phase=="PLAN"' "$workspace/.ops/changes/$change/runtime/state.json" >/dev/null || fail 'workspace-only phase did not run'
grep -Fq '"type": "user"' "$trace/sdk.jsonl" || fail 'workspace-only Claude SDK turn missing'
"$OPS" unlock-repos "$change" "$session"
printf '%s\n' 'test_phase_agent_routing: all checks passed'
