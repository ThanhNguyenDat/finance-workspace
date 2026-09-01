# Round 383 — NEEDS-MORE-RESEARCH: **short trades lose 40% less per trade than long**, the first side-split ever possible in this arc. Plus a P2: the gate report omits `data_as_of`.

Classification: **NEEDS-MORE-RESEARCH**. Two containers (the budget), cleaned
up. OPS transaction in `VERIFY`.

## A new direction, opened at the user's suggestion

The user asked whether long-only or short-only is worth exploring, as a separate
rule. It is, and it became answerable **this round** because the per-trade audit
trail verified in round 380 carries a `side` field — the first time in this arc
that a Portfolio result could be decomposed by direction at all.

`bybit.perpetual_future.BTC.USDT` @900, deployed configuration, from the 847
emitted trade records:

| side | trades | PnL | PnL/trade |
|---|---|---|---|
| **short** | 363 | −1.12027 | **−0.003086** |
| **long** | 484 | −2.49803 | **−0.005161** |

**Short loses 40.2% less per trade than long, and the Portfolio takes 33% more
long trades than short.** Both sides are negative, so neither is a candidate —
but the asymmetry is 1.67× per trade, far outside the window jitter measured in
round 382.

## The methodological caveat that matters most here

**Summing the long trades is not a long-only simulation.** Removing shorts
changes which longs happen: the minimum-hold guard gates *reversals*
specifically, a short that never opens changes what the next long does, and the
risk layer sees a different position sequence. A side-restricted result cannot
be inferred from this split; it has to be **run**.

There is no way to run it today: `grep` finds no `long_only`, `short_only`,
`allowed_side` or equivalent in `finance-research`'s CLI, in
`finance-core/src/portfolio_risk.rs`, or in `trading_modes.rs`. So the user is
right that this is **a separate rule** — it needs a code change, and it is the
natural next OpenSpec item after the current transaction closes.

## Verification progress this round

- **`cargo test --workspace` on `f158e04`, run by me: 702 passed, 0 failed, 37
  suites, no errors.** The final commit is now independently covered.
- **Gate and non-gate on one pinned window** (`--as-of 2026-08-31T00:00:00Z`,
  `exness XAU` @900, `candle_count` 174,254 in both):

| | trades | PnL |
|---|---|---|
| non-gate `one_target` (full) | 402 | −3.161420 |
| gate faithful (holdout) | 160 | −0.377343 |
| non-gate `legacy` (full) | 440 | −3.782369 |
| gate `legacy` (holdout) | 174 | −0.398118 |

Containment invariants hold on both paths (holdout ≤ full). The holdout carries
**39.8%** of trades on a **20.0%** window — the Portfolio trades about twice as
densely late as on average, consistent with the eight-interval warm-up (r267)
suppressing early activity.

- **Round 381's provisional −40.3% reading is superseded.** On this pinned
  window `exness XAU`'s guard advantage is **positive on both scopes**: +5.2% on
  holdout, +16.4% full-window. That reading came from an unpinned build and I
  declined to record it as a finding; this is why.

## P2-3 — the gate report omits `data_as_of`

The non-gate report records `data_as_of`; **the gate report does not** (`None`
in this run), although the gate accepts `--as-of` and honoured it — both runs
returned `candle_count` 174,254. So a gate verdict cannot be shown reproducible
from its own output, which is the whole purpose of the round-2 fix. Small,
mechanical, and worth closing before release.

## The cross-path equality criterion, resolved as unexecutable

Task 1.3's end-to-end form — gate faithful equal to a holdout-restricted
`one_target` — **cannot be executed with the current output surface**, because
no holdout-restricted `one_target` is emitted, and a `--days 180` run is not a
substitute: it starts the Portfolio cold, whereas the gate's holdout is reached
with the Portfolio already warm. I am recording that plainly rather than
deferring it a fourth time. What exists instead: the unit-level equality test
Codex added, the structural proof that both paths call one shared function, and
the containment invariants above.

## What is proven, and what is not

Proven:

- The side split above, from 847 emitted records on one route and window.
- 702 tests passing on `f158e04` in a run I executed.
- Gate and non-gate agree on `candle_count` under one `--as-of`; containment
  invariants hold; the gate omits `data_as_of`.
- No side-restriction flag exists in the research CLI or the shared crates.

Not proven, and deliberately not claimed:

- **That long-only or short-only would perform as the split suggests.** The
  split is descriptive. Restricting a side changes the position sequence, so the
  result must be measured, not summed.
- That the asymmetry generalises. **One route, one window, one configuration.**
  Every direction-shaped effect in this arc so far has failed to hold across
  routes; there is no reason to assume this one is different.
- Any mechanism for it. None offered.
- That the change is releasable. P2-3 is open, and FINAL_VERIFY has not run.

## Named next step

Close P2-3, then FINAL_VERIFY the current transaction. After it archives, the
side-restriction rule is the obvious next OpenSpec change — and the first
research question for it is whether the short-versus-long asymmetry survives on
a second route, using the audit trail on runs already held.
