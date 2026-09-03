#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/bin"; export PATH="$tmp/bin:$PATH" CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1 AGENT_ROLE_STATE_DIR="$tmp/state" AGENT_ROLE_LEGACY_QUANT_STATE="$tmp/no-quant" AGENT_ROLE_LEGACY_CLAUDE_STATE="$tmp/no-claude"
fail() { printf 'test_provider_availability: %s\n' "$1" >&2; exit 1; }
make_fake() {
  local name="$1"
  cp "$ROOT_DIR/tools/orchestrator/tests/fixtures/fake_${name}_sdk_cli.py" "$tmp/bin/$name"
  chmod +x "$tmp/bin/$name"
}
make_fake codex; make_fake claude; orchestrator agent-role-state init >/dev/null
for provider in codex claude; do
  FAKE_RESULT=success orchestrator detect-provider-availability "$provider" | grep -Fqx available || fail "$provider success probe failed"
  if FAKE_RESULT=quota orchestrator detect-provider-availability "$provider" >/dev/null; then :; else [[ $? -eq 0 ]] || fail "$provider quota probe exit"; fi
  jq -e --arg p "$provider" '.providers[$p].available|not' "$AGENT_ROLE_STATE_DIR/state.json" >/dev/null || fail "$provider quota not persisted"
  orchestrator agent-role-state provider-result "$provider" global-quota-exhausted 0 >/dev/null
  orchestrator agent-role-state probe-due "$provider" || fail "$provider did not become probe due"
  before="$(jq -c --arg p "$provider" '.providers[$p]' "$AGENT_ROLE_STATE_DIR/state.json")"
  set +e; FAKE_RESULT=rate PHASE_AGENT_PROBE_COOLDOWN_SECONDS=60 orchestrator detect-provider-availability "$provider" >/dev/null; status=$?; set -e
  [[ "$status" -eq 3 ]] || fail "$provider generic rate was not inconclusive"
  jq -e --arg p "$provider" --argjson before "$before" '.providers[$p].available==$before.available and .providers[$p].reason==$before.reason and .providers[$p].mode==$before.mode and .providers[$p].next_probe_at>$before.next_probe_at' "$AGENT_ROLE_STATE_DIR/state.json" >/dev/null || fail "$provider inconclusive did not preserve health and advance cooldown"
  if orchestrator agent-role-state probe-due "$provider" >/dev/null 2>&1; then fail "$provider inconclusive probe remained immediately due"; fi
  orchestrator agent-role-state provider-on "$provider" >/dev/null
  FAKE_RESULT=auth orchestrator detect-provider-availability "$provider" >/dev/null
  jq -e --arg p "$provider" '.providers[$p].mode=="manual" and (.providers[$p].available|not) and .providers[$p].reason=="auth-error" and .providers[$p].next_probe_at==null' "$AGENT_ROLE_STATE_DIR/state.json" >/dev/null || fail "$provider auth did not require manual recovery"
  orchestrator agent-role-state provider-on "$provider" >/dev/null
done
printf '%s\n' 'test_provider_availability: all checks passed'
