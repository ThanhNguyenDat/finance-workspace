## 1. Phase-agent state and controls

- [x] 1.1 In `finance-workspace`, add atomic ignored phase-agent state for six
  phases, ordered provider candidates, provider modes/health/cooldown and
  provider-native validation; verify defaults, migration, role isolation,
  malformed-state preservation and lock safety with bounded shell tests.
- [x] 1.2 Add safe terminal show/set/reset/pin/auto/provider-on/provider-off
  controls and environment precedence; verify every public operation against a
  temporary state directory without exposing raw JSON.

## 2. Provider adapters and availability

- [x] 2.1 Reconcile the existing Codex and in-progress Claude runners as
  provider adapters for every supported model-owned phase, preserving native
  flags, Opus medium/high policy, current-round findings, no-push prompts and
  read-only verification guards; verify both adapters using fake executables.
- [x] 2.2 Add provider-specific result classification and bounded recovery
  probes so only explicit global quota/auth evidence opens a circuit and
  generic 429/network/timeout stays inconclusive; verify classification,
  cooldown and recovery without contacting model services.

## 3. Generic resolver and interrupted continuation

- [x] 3.1 Add the generic phase-agent resolver with ordered candidates, manual
  pin precedence, active phase/session/repository lock validation and exactly
  one immutable live attempt; verify PLAN/IMPLEMENT/VERIFY/FIX/FINAL_VERIFY
  routing for both providers offline.
- [x] 3.2 Add append-only attempt evidence containing safe provider/model,
  phase/round, process, exit class, Git fingerprint and continuation metadata;
  verify prior attempts cannot be overwritten and no secrets/raw environment
  are serialized.
- [x] 3.3 Implement confirmed-quota continuation after the old process exits:
  unchanged work starts another same-phase attempt, changed PLAN/IMPLEMENT/FIX
  work enters continue mode, FIX round remains stable, and an unkillable or
  externally ambiguous attempt blocks; verify all branches with fake workers.
- [x] 3.4 Derive verification separation from the latest mutator and fresh
  verifier providers, enforce read-only verifier process separation, and gate
  release on objective FINAL_VERIFY evidence; verify independent and
  same-provider labels cannot be overstated.

## 4. Quant and OPS migration

- [x] 4.1 Route the one-shot terminal quant launcher through the
  `quant_research` agent while preserving canonical stdin prompt, exactly-one
  iteration across continuation, hard timeout and no loop/daemon/retry
  scheduling; verify argv, stdin, exit and interrupted iteration behavior.
- [x] 4.2 Migrate new OPS transactions from transaction-wide backend pairs to
  routing-policy/attempt history while retaining legacy active transaction
  behavior; verify phase re-resolution, lock ownership, FIX limits and terminal
  cleanup for both schemas.

## 5. Documentation and bounded verification

- [x] 5.1 Update current Claude/Codex worker specs, README, Claude quant/OPS command guidance and
  the shared quant-research skill for phase agents, manual overrides,
  interruption continuation and honest verification labels; verify shared
  links synchronize without changing platform-native OpenSpec integrations.
- [x] 5.2 Add all new scripts/tests to bounded Agent Contracts, run shell syntax
  checks, every orchestration suite, strict OpenSpec validation, agent-link
  check and `git diff --check`; verify every command exits successfully before
  implementation is handed to the apply workflow.
