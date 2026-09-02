---
name: quant-research-loop
description: Run one bounded quant-research iteration for Finance Live Action BTC/XAU strategies, using honest unseen-data evidence and promoting only actionable results through one stable OpenSpec + OPS change. Use for manual terminal quant optimization work.
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

1. Read the priority backlog and active OpenSpec/OPS work; legacy handoff is
   history only.
2. Choose one fresh or unresolved hypothesis, prioritizing XAU then BTC.
3. Run bounded, containerized research with pinned inputs and honest train/
   validation/holdout or walk-forward separation.
4. Check production only when the claim concerns live behavior.
5. Classify the result and preserve raw evidence, metrics, assumptions, and
   invalidated conclusions.
6. For `PROMOTE` only, create/reuse one stable OpenSpec change and enter the
   canonical OPS lifecycle with research-origin references.
7. Clean up temporary containers/tunnels and report limitations precisely.

The terminal launcher records the iteration exactly once before invoking the
`quant_research` phase agent. Provider selection comes from atomic phase-agent
state; a confirmed quota interruption may continue through another candidate
without incrementing the iteration or discarding existing artifacts.

The launcher depends on the repository-local `uv` project at
`.agents/orchestrator/`; bootstrap it with `uv sync --project
.agents/orchestrator` before running the quant command in a new environment.

## Non-negotiable invariants

- Do not fabricate metrics, infer missing inputs, cherry-pick windows, or treat
  overlapping samples as independent evidence.
- Keep production reads non-secret and read-only unless separately authorized.
- Do not create OPS work for non-promoted outcomes.
- Preserve trading safety, no-lookahead, cost, fill, and route-specific
  semantics; a measurement defect is not a strategy improvement.

## Detailed guidance

Use [references/playbook.md](references/playbook.md) as a searchable field
guide. Always read `Round structure`, `Backtest tooling`, `Promotion and
provider failover`, and `Research evidence and promotion`. Then read only the
topic-specific lessons relevant to the current hypothesis (for example cost
gates, live trade logs, continuity, strategy coverage, or holdout design).
