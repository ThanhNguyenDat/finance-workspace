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
