## Why

**Sequencing**: land after `phase-agent-orchestrator-submodules` and
`phase-agent-account-registry-config`, so the new `adapters/`, `classify/`,
`detect/`, and `subprocess_supervision/` packages this change adds join an
already-clean layout instead of a set of flat files.

`phase-agent-python-orchestrator` ported the state/lock/routing layer
(`ops-runtime.sh`, `phase-agent-state.sh`, `quant-research-state.sh`) to
Python and deliberately left the remaining ~700 lines of bash — the
scripts that actually spawn `claude`/`codex` subprocesses and glue the
system together — untouched, reasoning that bash's `timeout` + `trap ...
EXIT` is already an idiomatic, sufficient way to supervise a child process
and that porting it would not obviously get *safer*, only different. The
operator has asked for the remaining bash converted to Python anyway, for
a different reason than safety: **maintaining one language across the
whole orchestration codebase** — no more shim indirection, one test
framework, one set of conventions, no context-switching between bash and
Python to read or change how a phase attempt runs end to end.

**Pivot to the official SDKs (2026-09-02)**: while planning this change,
the operator asked whether official SDKs exist for both providers instead
of hand-rolling subprocess supervision around the raw `claude`/`codex` CLI
binaries. Documentation fetched via `ctx7` confirmed both Anthropic
(`claude-agent-sdk`, Python) and OpenAI (`openai_codex`, Python) publish an
official Python SDK; both still spawn and own the underlying CLI as a
subprocess over stdio (not a persistent daemon, not a raw HTTP client), so
the "no daemon" non-goal is unaffected, but both expose structured results
(`ResultMessage`/`TurnResult` objects instead of text to parse) and a
native cancellation call (`ClaudeSDKClient.interrupt()`;
`TurnHandle.interrupt()` over Codex's `turn/interrupt` JSON-RPC) instead of
requiring this change to hand-write the SIGTERM/SIGKILL escalation timer
and text-based result classifier originally planned. The operator directed
this change to use the SDKs directly rather than the raw CLI, accepting
that this is a deliberate mechanism change (SDK-native cancellation
replacing OS signals) rather than the byte-for-byte "keep bash's exact
mechanism, just in Python" port originally scoped — see design.md for the
open verification items this pivot introduces.

## What Changes

- Port the remaining phase-agent bash scripts to Python, calling the
  official `claude-agent-sdk` and `openai_codex` Python SDKs instead of
  spawning the raw `claude`/`codex` CLI binaries directly, while preserving
  every *externally observable* behavior (same CLI invocation for the
  `tools/orchestrator/bin/*.sh` entry points, same effective model/effort/timeout/
  kill-after values, same lease/lock acquisition order, same log file
  layout under `.ops/changes/<change>/runtime/logs/`, same
  `result_class` vocabulary consumed by `phase_agent_state`):
  - `run-claude-phase.sh`, `run-codex-phase.sh` (spawn adapters, now SDK-backed)
  - `run-phase-agent.sh` (candidate resolution + adapter dispatch loop)
  - `run-phase-agent-command.sh` (quant-research launcher)
  - `classify-claude-result.sh`, `classify-codex-result.sh` (result
    classification, now sourced from SDK structured fields)
  - `detect-provider-availability.sh`, `detect-codex-availability.sh`
    (availability probes)
  - `configure-phase-agents.sh` (operator-facing config CLI)
- Add `claude-agent-sdk` and `openai_codex` (exact PyPI distribution names
  to be confirmed at implementation time — Task 3.0) as dependencies of
  `tools/orchestrator/pyproject.toml`, pinned in `uv.lock`.
- The three files ported by `phase-agent-python-orchestrator`
  (`ops-runtime.sh`, `phase-agent-state.sh`, `quant-research-state.sh`) are
  Python implementations exposed through clean `uv run` console commands;
  compatibility wrappers live in `tools/orchestrator/bin/`, while
  all Python code remains in `tools/orchestrator/`.
- Subprocess supervision (spawn `claude`/`codex` via its SDK, enforce a
  timeout via the SDK's native cancellation call, then a hard-kill fallback
  if the process is still alive after a grace period, always release the
  lease on exit) replaces the originally-scoped hand-rolled
  `subprocess.Popen` + signal-escalation timer (design.md must show the
  cancellation-then-hard-kill sequence preserves the same two guarantees
  the current bash `timeout --signal=TERM --kill-after=30s` provides: a
  grace period before forcible termination, and forcible termination
  eventually happening — this is still the one place a subtle behavior gap
  would be easy to introduce, now for a different reason: dependency on
  each SDK's own documented-but-not-fully-verified cancellation contract).
- Port the remaining operational helpers (`sync-agent-links.py`,
  `wait-for-phase-attempt.py`, and `watch-phase-attempt-log.py`) into
  `tools/orchestrator/`, exposing them through console commands and
  optional thin `bin/*.sh` wrappers. Shell contract tests remain shell because they exercise the
  public process/CLI contracts.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none — every requirement in `openspec/specs/ops-backend-routing/spec.md`
is preserved unchanged; the externally observable contract — result
classes, prompt content, lease/lock ordering — is what that spec describes,
and the SDK pivot changes internal mechanism only, so `skip_specs: true`
remains set)

## Impact

- **Affected repository**: `finance-workspace` only.
- **Affected files**: every bash script listed above is replaced by Python
modules under `tools/orchestrator/src/orchestrator/`, with
  each bash file's path either removed (once all callers are ported) or
  kept as a thin shim during a transition window (design.md must decide
  which); `tools/orchestrator/pyproject.toml` and `uv.lock` gain two new
  third-party dependencies.
- **Trading safety**: none directly (orchestration tooling). Safety-
  relevant to the OPS workflow the same way the rest of this system is:
  a regression in subprocess timeout/cancellation handling could leave a
  runaway `claude`/`codex` process unbounded, or a lease unreleased,
  blocking every future phase attempt for that change — the SDK pivot does
  not lower this risk relative to the original hand-rolled-Popen plan, it
  only changes which failure mode is most likely (a wedged SDK-internal
  process the SDK's own `interrupt()` cannot reach, vs. a bug in
  hand-written signal-escalation code).
- **Rollback**: bash originals remain in git history; per-script rollback
  is a straightforward revert, mirroring `phase-agent-python-orchestrator`'s
  migration plan. Reverting a script's cutover commit does not require
  removing the SDK dependencies (harmless to leave installed but unused).
