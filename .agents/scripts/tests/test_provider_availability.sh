#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
DETECT="$ROOT_DIR/.agents/scripts/detect-provider-availability.py"
STATE="$ROOT_DIR/.agents/scripts/phase-agent-state.py"
tmp="$(mktemp -d)"; trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/bin"; export PATH="$tmp/bin:$PATH" CLAUDE_AGENT_SDK_SKIP_VERSION_CHECK=1 PHASE_AGENT_STATE_DIR="$tmp/state" PHASE_AGENT_LEGACY_QUANT_STATE="$tmp/no-quant" PHASE_AGENT_LEGACY_CLAUDE_STATE="$tmp/no-claude"
fail() { printf 'test_provider_availability: %s\n' "$1" >&2; exit 1; }
make_fake() {
  local name="$1"
  cp "$ROOT_DIR/tools/phase-agent-orchestrator/tests/fixtures/fake_${name}_sdk_cli.py" "$tmp/bin/$name"
  chmod +x "$tmp/bin/$name"
}
make_fake codex; make_fake claude; "$STATE" init >/dev/null
for provider in codex claude; do
  FAKE_RESULT=success "$DETECT" "$provider" | grep -Fqx available || fail "$provider success probe failed"
  if FAKE_RESULT=quota "$DETECT" "$provider" >/dev/null; then :; else [[ $? -eq 0 ]] || fail "$provider quota probe exit"; fi
  jq -e --arg p "$provider" '.providers[$p].available|not' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail "$provider quota not persisted"
  "$STATE" provider-result "$provider" global-quota-exhausted 0 >/dev/null
  "$STATE" probe-due "$provider" || fail "$provider did not become probe due"
  before="$(jq -c --arg p "$provider" '.providers[$p]' "$PHASE_AGENT_STATE_DIR/state.json")"
  set +e; FAKE_RESULT=rate PHASE_AGENT_PROBE_COOLDOWN_SECONDS=60 "$DETECT" "$provider" >/dev/null; status=$?; set -e
  [[ "$status" -eq 3 ]] || fail "$provider generic rate was not inconclusive"
  jq -e --arg p "$provider" --argjson before "$before" '.providers[$p].available==$before.available and .providers[$p].reason==$before.reason and .providers[$p].mode==$before.mode and .providers[$p].next_probe_at>$before.next_probe_at' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail "$provider inconclusive did not preserve health and advance cooldown"
  if "$STATE" probe-due "$provider" >/dev/null 2>&1; then fail "$provider inconclusive probe remained immediately due"; fi
  "$STATE" provider-on "$provider" >/dev/null
  FAKE_RESULT=auth "$DETECT" "$provider" >/dev/null
  jq -e --arg p "$provider" '.providers[$p].mode=="manual" and (.providers[$p].available|not) and .providers[$p].reason=="auth-error" and .providers[$p].next_probe_at==null' "$PHASE_AGENT_STATE_DIR/state.json" >/dev/null || fail "$provider auth did not require manual recovery"
  "$STATE" provider-on "$provider" >/dev/null
done
printf '%s\n' 'test_provider_availability: all checks passed'
