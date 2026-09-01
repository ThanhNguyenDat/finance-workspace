## Context

OPS currently persists one implementation backend for a whole transaction.
Codex has role profiles and automatic global-quota detection; the in-progress
Claude worker work adds bounded external processes but keeps separate
Claude-specific state. This duplicates routing policy and cannot automatically
continue a phase when whichever provider is active exhausts quota.

## Goals / Non-Goals

**Goals:**

- Make phase ownership logical and provider-neutral.
- Automatically select an eligible Codex or Claude candidate at each attempt.
- Continue partially completed PLAN/IMPLEMENT/FIX work safely after confirmed
  quota exhaustion.
- Preserve exclusive locks, bounded execution, current FIX findings, auditable
  evidence, and honest verification separation.
- Keep provider-specific CLI options and validation inside adapters.

**Non-Goals:**

- Run multiple workers concurrently on one phase/repository.
- Treat timeout, generic 429, or implementation failure as proof of quota loss.
- Roll back partial work automatically.
- Add a scheduler, daemon, unbounded retry, or persistent model session.
- Delegate RELEASE, DEPLOY_VERIFY, or ARCHIVE decisions to a model worker.

## Decisions

### 1. A logical agent owns each model phase

The supported agents are `quant_research`, `plan`, `implement`, `verify`,
`fix`, and `final_verify`. Each stores an ordered candidate list. A candidate
contains `provider`, `model`, and provider-native effort; the provider adapter
validates its own vocabulary. Opus accepts only `medium` or `high`; `medium` is
normal and `high` is reserved for hard fixes/final verification.

The deterministic shell orchestrator owns phase transitions, locks, candidate
resolution, evidence, and release gates. It is not another model agent.

### 2. One atomic state owns profiles and provider health

Ignored `.ops/runtime/phase-agents/state.json` stores schema version, candidate
lists, provider mode (`auto|manual`), resolved availability, reason,
observation timestamp, cooldown/probe eligibility, and update timestamp.
Terminal commands expose safe show/set/reset/pin/auto/provider-on/provider-off
operations without printing raw JSON.

Environment overrides have emergency precedence over persisted profiles for
one invocation. Quant state keeps research enablement, iteration and timestamps;
Codex profile/availability fields migrate into phase-agent state once and are
then compatibility-read-only until removed by a later change.

### 3. A generic runner resolves and dispatches one attempt

`run-phase-agent.sh <change> <repository> <phase>` validates the OPS phase,
session and repository lock, current round, findings, and candidate policy. It
selects the first eligible candidate, creates an attempt id, persists the
selection, and invokes exactly one provider adapter. Direct provider CLI calls
from orchestration prompts remain prohibited.

Codex and Claude adapters receive the same phase context but retain native
flags, output parsing and effort validation. Claude always uses
`--dangerously-skip-permissions`; Codex uses its supported full-auto bypass.
VERIFY and FINAL_VERIFY remain read-only and fail on worktree mutation.

This replaces the previous Codex worker contract that limited Codex to
IMPLEMENT/FIX, embedded Terra-to-Sol fallback inside that adapter, and fixed
verification to Claude. Codex may now serve any configured model-owned phase;
candidate advancement and provider switching belong only to the resolver.

### 4. Provider health is a circuit breaker, not a guess

Result classification is provider-aware:

- explicit account/global quota opens that provider's circuit;
- model-specific unavailability advances to another model candidate, normally
  within the same provider first;
- authentication opens the provider circuit and records manual attention;
- timeout, network failure and generic 429 do not mark quota exhausted and get
  at most the configured bounded retry/failover policy;
- implementation/test failure never triggers provider substitution.

In auto mode, an unavailable provider becomes probe-eligible after a cooldown.
The resolver runs at most one bounded, side-effect-free probe before selecting
it. Success closes the circuit; confirmed quota extends cooldown; inconclusive
results preserve prior availability. Manual pin/off/on always wins until the
operator returns that scope to auto.

### 5. Quota interruption creates a continuation attempt

Only after the old process exits or is TERM/KILL bounded may the resolver
start another attempt. It records exit class, provider/model, timestamps,
commit HEAD, worktree fingerprint, whether files changed, and safe evidence
paths. Exactly one attempt owns the phase lease at a time.

If confirmed quota exhaustion occurs with no mutation, the next candidate may
start normally. If PLAN/IMPLEMENT/FIX changed files or created commits, the
next candidate runs in `continue` mode and must inspect current artifacts,
diff, commits, tests and prior safe evidence. It must not discard or restart
the work. The phase and FIX round stay unchanged. Ambiguous external side
effects or an unverifiable process state become BLOCKED rather than fail over.

### 6. Attempt history replaces transaction-wide backend immutability

New transactions persist a routing-policy version and append-only attempt
records, not one backend pair. A selected candidate is immutable for its live
attempt; later phases and failed-attempt continuations resolve again from
current health and overrides. Existing transactions containing the legacy
backend pair keep legacy routing until completion to avoid an in-place semantic
change.

### 7. Verification mode is derived from actual execution

The latest successful mutating attempt (IMPLEMENT or FIX) and each VERIFY or
FINAL_VERIFY attempt identify their provider and process id. Different
providers yield `provider-independent`; the same provider yields
`same-provider-process-separated`. No preselected mode can overstate evidence.
Release requires a fresh successful FINAL_VERIFY attempt and all objective
gates, regardless of the derived label.

### 8. Quant remains manually launched and bounded

The terminal launcher resolves the `quant_research` agent, feeds the canonical
quant prompt through stdin, and returns after one process. A quota interruption
may continue the same iteration through another candidate but must not call
`begin-iteration` again. No launcher schedules a loop, daemon or future run.

## Risks / Trade-offs

- [A second provider continues imperfect partial work] -> Preserve the actual
  diff/commits and use explicit continuation prompts rather than summaries.
- [A provider is disabled by a false quota match] -> Require provider-specific
  deterministic classification; generic 429/timeouts are inconclusive.
- [Failover starts while the old process still writes] -> Hold one phase lease
  and require confirmed exit before dispatch.
- [Repeated probes consume quota] -> Apply cooldown and one bounded probe per
  eligibility window.
- [Same-provider review is mistaken for independence] -> Derive and display the
  label from attempt evidence.
- [Legacy active state changes meaning] -> Keep a legacy routing path until
  those transactions terminate.

## Migration Plan

1. Add phase-agent state with migration/import from current Codex and Claude
   defaults while preserving quant iteration state.
2. Adapt current Codex/Claude runners behind one resolver and add provider-aware
   classifiers and probes.
3. Add append-only attempt/continuation evidence and phase lease enforcement.
4. Switch new OPS transactions and terminal quant to phase-agent routing;
   retain legacy runtime compatibility.
5. Update commands, specs, docs, shared skill and bounded fake-provider tests.

Rollback routes new work through the previous provider-specific commands and
leaves transient phase-agent state unused. Existing commits/diffs and legacy
transactions remain intact.
