---
name: quant-research-loop
description: Run one bounded quant-research iteration for Finance Live Action BTC/XAU strategies, using honest unseen-data evidence and promoting only actionable results through one stable OpenSpec change. Use for manual terminal quant optimization work.
---

# Quant Research Loop

Run one rigorous iteration; a valid rejection, data issue, or clarified blocker
is useful progress. Never manufacture a candidate to keep the loop busy.

## Inputs and output

Input is the current research backlog, active OpenSpec/OPS state, available
market evidence, and one testable hypothesis. Output is exactly one classified
result (`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, or
`PROMOTE`) with reproducible evidence and updated research navigation.

## Core workflow

Each round is one unit of work that walks through all four provider roles
from `CLAUDE.md`'s Role/Working Model — **Claude plans, Codex implements,
Claude verifies, Codex fixes if needed — entirely within the same round**.
Never spend two round numbers on one hypothesis just to separate these
stages.

**Claude (PLAN), steps 1-2:**

1. Read the priority backlog and active OpenSpec work; legacy handoff is
   history only.
2. Choose one fresh or unresolved hypothesis, prioritizing XAU then BTC, and
   write a short plan: the hypothesis, why it is next, and the test design
   (route priority, train/validation/holdout or walk-forward split, cost/fill
   assumptions, and what evidence would classify PROMOTE vs. everything
   else). Hand this plan directly to Codex as the round's implementation
   brief — it does not need its own file or round number.

**Codex (IMPLEMENT), steps 3-5:**

3. Run bounded, containerized research against that plan, with pinned inputs
   and honest train/validation/holdout or walk-forward separation.
4. Check production only when the claim concerns live behavior.
5. Classify the result and draft the round file with raw evidence, metrics,
   assumptions, and invalidated conclusions — but do not commit yet.

**Claude (VERIFY), before commit:**

6. Independently check the draft against the non-negotiable invariants below
   (no fabricated/inferred/cherry-picked evidence, honest disjoint
   train/validation/holdout, no-lookahead, trading-safety and route-specific
   semantics preserved, the stated classification actually matches the
   numbers). Inspect the real evidence Codex produced, not just its written
   summary.

**Codex (FIX), only if Claude's verify found a problem:**

7. Correct the specific issue Claude raised — re-run the affected evidence,
   fix the classification, or fix the write-up — still inside this round, no
   new round number. Hand back to Claude for a quick re-check of the fix.

**Codex (finish), step 8:**

8. Commit the round file, clean up temporary containers/tunnels, and report
   limitations precisely.

**Claude (PLAN), step 9 — `PROMOTE` only:**

9. Create the OpenSpec change via `/opsx:propose` with research-origin
   references, then stop at planning — no automatic implementation lifecycle
   follows; implementation is a separate manual decision by the operator.
   Creating OpenSpec planning artifacts is Claude's job even here (`CLAUDE.md`
   "Claude owns: ... OpenSpec planning artifacts"), never Codex's.

Split one hypothesis across two round numbers only when execution genuinely
can't finish what was planned — e.g. Codex's implementation reveals the
planned test design is infeasible, the backlog turns out to be exhausted
mid-run, or Claude's verify finds a defect deep enough that redoing the test
design (not just fixing it) is the honest path. In that case, classify and
close the current round honestly (e.g. `NEEDS-MORE-RESEARCH` or
`DATA-ISSUE`) rather than silently reusing its round number for a different,
re-planned hypothesis; the re-plan becomes the next round. A confirmed
account/quota exhaustion for one provider is a fallback to the other under
the same role-boundary rule, not a reason to split the round.

There is no launcher or background orchestrator tracking iterations for this
loop anymore — the operator runs each round manually. **The round-file
sequence under `research/quant/rounds/` is the sole source of truth for the
next round number**: find the highest existing `round<N>-*.md` file (or the
latest `docs(research): round <N>` commit in `git log`) and use `N+1`.

When any stage of the round runs through `codex-exec`/`claude-exec`, pass
`--change quant-research-round-<N>` (the same `<N>` as the round file) so
every stage's log lands under `tools/orchestrator/logs/quant-research-round-<N>/`
instead of an unrelated `adhoc-<date>` bucket — this is what makes a round's
full Claude/Codex log trail findable as one unit later.

## Non-negotiable invariants

- Do not fabricate metrics, infer missing inputs, cherry-pick windows, or treat
  overlapping samples as independent evidence.
- Keep production reads non-secret and read-only unless separately authorized.
- Do not create OPS work for non-promoted outcomes.
- Preserve trading safety, no-lookahead, cost, fill, and route-specific
  semantics; a measurement defect is not a strategy improvement.
- A changed `--as-of` cutoff is not independent evidence by itself: compare the
  actual train/validation/holdout spans and label overlap with earlier runs.
  Call a window independent only when the relevant holdout is disjoint (or use
  walk-forward segments with non-overlapping evaluation periods); otherwise
  preserve the result as a shifted, overlapping confirmation.

## Detailed guidance

Use [references/playbook.md](references/playbook.md) as a searchable field
guide. Always read `Round structure`, `Backtest tooling`, `Promotion and
provider failover`, and `Research evidence and promotion`. Then read only the
topic-specific lessons relevant to the current hypothesis (for example cost
gates, live trade logs, continuity, strategy coverage, or holdout design).
