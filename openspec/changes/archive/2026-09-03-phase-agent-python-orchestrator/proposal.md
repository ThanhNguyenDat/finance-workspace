## Why

The phase-agent state/lock/routing layer (`ops-runtime.sh`, `phase-agent-state.sh`,
`quant-research-state.sh` — roughly 1250 of the 1971 lines under
`.agents/scripts/`) is implemented in bash plus string-interpolated `jq`. This
session's lock-staleness fix (auto-release a change/repo lock when its owning
process has actually died) needed several iterations to get right — an initial
`$PPID`-based anchor was silently wrong and was only caught by hand-spawning
real subprocesses in ad-hoc shell scripts, because the logic has no
unit-testable seams. The JSON state manipulation, liveness/staleness
reasoning, and validation rules in this layer have outgrown what bash can
express safely and verify cheaply.

## What Changes

- Reimplement the logic currently in `ops-runtime.sh`, `phase-agent-state.sh`,
  and `quant-research-state.sh` as a Python package (dependency-managed with
  `uv`), exposed as CLI entrypoints that preserve each script's existing
  subcommands, arguments, and stdout/exit-code contract byte-for-byte, so
  every unmodified bash caller (`run-phase-agent.sh`,
  `run-phase-agent-command.sh`, etc.) invokes it exactly as it invokes the
  bash scripts today.
- Preserve, without behavior change, every semantic already specified in
  `openspec/specs/ops-backend-routing/spec.md` and this session's
  lock-staleness behavior: `$CLAUDE_PID`/`$CODEX_PID` anchor-pid liveness,
  same-host-only trust, the phase-attempt-lease dead-check, atomic JSON state
  writes, and all existing phase/transition/routing validation rules.
- Task-appropriate concurrency inside the new process: external CLI
  invocation (`claude`, `codex`) stays a real OS subprocess with the current
  timeout/kill-after/trap-equivalent supervision — threads cannot and must
  not replace that. In-process Python threads are used only for genuinely
  concurrent internal bookkeeping (for example, evaluating multiple
  repository-lock candidates), not as a subprocess substitute.
- **Non-goals for this change**: `run-claude-phase.sh`, `run-codex-phase.sh`,
  `run-phase-agent.sh`, `run-phase-agent-command.sh`,
  `classify-claude-result.sh`, `classify-codex-result.sh`,
  `detect-provider-availability.sh`, `detect-codex-availability.sh`,
  `configure-phase-agents.sh`, and `sync-agent-links.sh` stay bash and are not
  touched. They keep shelling out to the new Python CLI exactly as they shell
  out to the bash scripts today.
- Dependency management is `uv` (`pyproject.toml` + `uv.lock`); no other
  Python package manager is introduced.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none — the requirements in `openspec/specs/ops-backend-routing/spec.md` are
preserved unchanged; this is a re-implementation, not a behavior change, so
`skip_specs: true` is set on this change)

## Impact

- **Affected repository**: `finance-workspace` only. This is orchestration
  tooling under `.agents/scripts/`, not production runtime code, so
  `finance-mw`, `finance-web`, `finance-live-action`, `finance-broker`, and
  `mt5` are unaffected.
- **Affected files**: `.agents/scripts/ops-runtime.sh`,
  `phase-agent-state.sh`, `quant-research-state.sh` are replaced by Python CLI
  entrypoints (exact new source layout is a `design.md` decision). Their bash
  test suites (`test_ops_orchestration.sh`, `test_phase_agent_state.sh`,
  `test_quant_research_state.sh`, `test_phase_agent_routing.sh`,
  `test_quant_backend_routing.sh`, `test_quant_promotion_trace.sh`,
  `test_hermetic_agent_contracts.sh`) exercise the CLI surface end-to-end and
  must keep passing unmodified against the new Python CLI, since they are the
  existing behavioral contract.
- **New dependency**: this workspace is currently pure bash/jq/git tooling;
  this change adds a `uv`-managed Python runtime dependency and needs a
  documented bootstrap path for both interactive sessions and the
  non-interactive launcher scripts that invoke the new CLI.
- **Trading safety**: no direct trading-code impact (this is orchestration
  tooling, not live trading code). It is still safety-relevant to the OPS
  workflow itself: a lock/routing regression could let two concurrent OPS
  transactions corrupt the same `openspec/changes/<change>` artifacts or
  research state, so FINAL_VERIFY for this change must include a direct
  behavioral comparison against the current bash implementation, not only new
  unit tests.
- **Rollback**: the bash originals remain in git history; rollback is a
  straightforward revert of the cutover commit(s) because callers' contracts
  are unchanged either way.
