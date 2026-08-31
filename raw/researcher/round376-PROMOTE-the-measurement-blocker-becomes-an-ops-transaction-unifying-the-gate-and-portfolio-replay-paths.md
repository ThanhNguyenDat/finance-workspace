# Round 376 — PROMOTE: the measurement blocker becomes an OPS transaction. The gate and Portfolio replay paths are being unified.

Classification: **PROMOTE**. First promotion in 171 iterations. **Zero research
containers** — the work of this round is planning and orchestration, not
backtesting.

## Why now

The user authorised an architecture change to remove blockers (2026-08-31),
subject to the rules and the promotion gate still holding and **correctness
first**. That removes the only thing that had kept rounds 356–375 at
research-only classifications: the blockers were real, but they were treated as
permanent constraints rather than as defects with an owner.

## The defect being promoted

`finance-research` has two Portfolio replay paths that diverged, and each holds
exactly what the other lacks:

| | gate path | Portfolio-faithful path |
|---|---|---|
| location | `daily_profit_gate.rs:376-412` | `portfolio_measurement.rs:184-208` |
| construction guard | **absent** | `construct(decision)` |
| risk layer | **absent** | `evaluate_historical` → `execution_target` |
| scorecard metrics | full | 4 fields |
| holdout restriction | yes | **none** |

Because the gate does not model the construction guard, `main.rs:264` declares
`portfolio_minimum_hold_decisions` as `conflicts_with = "daily_profit_gate"` —
so **no configuration carrying a minimum-hold value can ever obtain a holdout
score**. That is promotion condition 1, structurally unmeetable, and it is why
every hold-bearing result in this arc stopped short.

Round 371 measured the size of the discrepancy on
`binance.perpetual_future.BTC.USDT` @900: the gate scores a stream losing
**−9.90557** while the deployed path loses **−4.81958**.

Three further defects are in scope: nested-only out-of-sample (r352), the joint
objective being computable only on the wrong path, and rows the tool cannot
support — a strategy degraded rather than excluded when its input is absent
(r374) and a wrapper reported several times when its threshold provably cannot
bind (r375).

## Promotion gate — all eight conditions

1. **Defensible evidence** — this is a *defect*, so the evidence is measurement
   observation, not a trading-edge claim: file:line citations and reproducible
   numbers across r351, r352, r356, r371, r374, r375.
2. **Concrete defect** — four, enumerated above.
3. **Scope and repositories** — `finance-live-action` only; specific crates and
   files enumerated in `tasks.md`.
4. **Expected behavior** — five requirements with scenarios in the spec delta.
5. **Acceptance criteria** — per-task verify lines, headlined by the
   exact-equality gate below.
6. **Risk and failure semantics** — principal risk is a live-path regression;
   mitigation is additive-only in `finance-core` with the existing suite
   required to pass unchanged.
7. **Trading safety** — an explicit requirement that live trading behaviour is
   unchanged; no edit to the construction guard, risk layer, or execution
   semantics.
8. **Rollback** — Git revert; a research CLI with no persistent production
   state.

## The acceptance criterion this change stands or falls on

After unification, a gate run and a `one_target` run over the same window at the
deployed default hold must produce **identical** trade count and realized PnL.
The replay is bit-for-bit deterministic (r351), so **any difference is a defect,
not noise**. A test that only checked "close enough" is precisely what would
have permitted the original divergence.

## Transaction

- change: `portfolio-measurement-integrity`
- OpenSpec: `openspec/changes/portfolio-measurement-integrity/` — validated
  `--strict`
- OPS: `.ops/changes/portfolio-measurement-integrity/`
- backend persisted: `implementation_backend=codex`,
  `verification_mode=independent`
- origin attached once: iteration 171, `ALL_ROUTES`, six repository-relative
  artifacts under `raw/`
- repository lock: `finance-live-action`

Status at the close of this round: **IMPLEMENT in progress**. The Codex worker
has modified `daily_profit_gate.rs` and `portfolio_decision_replay.rs` and is
still running. VERIFY has not started.

## What is proven, and what is not

Proven:

- The two replay paths differ as tabulated, at the cited lines.
- `main.rs:264` forbids a minimum-hold value under the gate.
- The OpenSpec change validates `--strict`; the OPS transaction is initialized
  with the backend and verification mode above.

Not proven, and deliberately not claimed:

- **That the implementation is correct, or complete.** IMPLEMENT is still
  running and Claude has verified nothing. No Codex summary counts as
  verification.
- **That unifying the paths will improve any result.** This change makes the
  measurement correct; it does not predict the sign of what is then measured,
  and it must not be judged on that sign. The most likely outcome is that
  hold-bearing configurations finally receive a gate score **and fail it**.
- That past gate verdicts were wrong in a knowable direction. They described a
  different configuration; r371 measured the gap once, on one route and window.
- That the four defects are the only ones. They are the ones this arc found.

## Named next step

VERIFY: independently inspect the diff, and run the exact-equality check
between the gate and `one_target` paths before anything is committed or pushed.
Per `verification_mode=independent`, release requires Claude's own final
verification after Codex IMPLEMENT/FIX.
