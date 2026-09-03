#!/usr/bin/env bash

# Contract suites may run from inside a phase-agent worker. Remove inherited
# orchestration context before each suite establishes its own isolated fixture.
while IFS= read -r variable; do
  case "$variable" in
    PHASE_AGENT_*|OPS_*|QUANT_RESEARCH_*|CODEX_TIMEOUT_SECONDS|CLAUDE_TIMEOUT_SECONDS|CODEX_RESULT_CLASSIFIER|CLAUDE_RESULT_CLASSIFIER|FAKE_*|TRACE)
      unset "$variable"
      ;;
  esac
done < <(compgen -A variable)

# Some compatibility suites copy a shim into an isolated fixture workspace.
# Keep the shim itself relocatable and provide its explicit project override
# from the test harness instead of making production code inspect process
# ancestry or depend on Linux /proc.
HERMETIC_ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export PHASE_AGENT_ORCHESTRATOR_PROJECT="$HERMETIC_ROOT_DIR/tools/orchestrator"
PHASE_AGENT_UV_BIN="$(command -v uv)"
orchestrator() {
  "$PHASE_AGENT_UV_BIN" run --project "$PHASE_AGENT_ORCHESTRATOR_PROJECT" "$@"
}
