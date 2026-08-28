## Context

See `proposal.md`. Backend selection, pair validation, IMPLEMENT/FIX routing,
and atomic FIX transitions are already accepted and implemented. The remaining
contradiction is command-contract wording at FINAL_VERIFY/release, plus one
terminal smoke handoff stored under the active namespace.

## Goals / Non-Goals

**Goals:**

- Make final verification semantics branch only on persisted
  `verification_mode`.
- Describe a concrete enhanced fallback self-review without inventing or
  requiring inapplicable evidence.
- Preserve terminal FAILED smoke history in the conventional archive path.

**Non-Goals:**

- Add a verification-mode setter or re-read quant state mid-transaction.
- Change runtime transitions, FIX limits, backend routing, quant research
  policy, CI agent execution, or production behavior.

## Decisions

1. **Keep the mode decision in `/ops:run`.** FINAL_VERIFY reads the persisted
   mode already validated by `ops-runtime.sh`. The command explicitly branches
   `independent` versus `claude-fallback-self-review` and uses the same branch
   for release/completion language.
   - Alternative rejected: a new runtime setter or phase, because it would
     make an immutable transaction contract mutable.

2. **Define enhanced self-review as an applicability-filtered checklist.** A
   fallback re-reads the actual/committed diff, checks OpenSpec criteria one by
   one, and verifies applicable tests, static checks, build/schema, safety,
   CI, exact revisions, deployment, and production behavior. It explicitly
   reports that independent maker/checker verification is unavailable.
   - Alternative rejected: requiring every possible check for every repository,
     which would fabricate irrelevant gates.

3. **Extend the existing backend-routing test.** Static contract assertions
   protect wording semantics, while the existing temp runtime fixture advances
   a fallback transaction to FINAL_VERIFY and proves its verification pair is
   unchanged. No real agent or release is invoked.
   - Alternative rejected: a separate orchestration implementation, which
     would duplicate accepted state-machine logic.

4. **Move only the terminal smoke directory.** Preserve the tracked handoff
   under `.ops/archive/2026-08-28-finance-mw-dev-docs-smoke/`. Move ignored
   runtime evidence with it locally where safe, preserving FAILED rather than
   calling the successful completion path.
   - Alternative rejected: deleting history or using `complete`, either of
     which would lose or falsify terminal evidence.

## Risks / Trade-offs

- [Natural-language command contract regresses later] → Test both positive
  mode branches and reject the known unconditional independent-only phrases.
- [Archive move is mistaken for success] → Preserve explicit FAILED/timeout,
  lock-cleanup, and no-deployment statements and assert them in tests.
- [CI runner lacks optional tools] → Keep test search helpers compatible with
  both `rg` and `grep` and retain workflow/job timeouts.

## Migration Plan

Commit and push this workspace-only change through Agent Contracts. No runtime
deployment applies. Roll back with a follow-up Git revert if necessary.
