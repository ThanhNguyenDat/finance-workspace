# Round 384 — NEEDS-MORE-RESEARCH: the side asymmetry **inverts by instrument**, and on `exness XAU` the **long side alone is positive**.

Classification: **NEEDS-MORE-RESEARCH**. Two containers (the budget), cleaned
up, both on a pinned window (`--as-of 2026-08-31T00:00:00Z`). OPS transaction in
FIX round 3 — the last one `OPS_MAX_FIX_ROUNDS` allows — for P2-3.

## The cross-route test round 383 named

| route | trades | short (n, /trade) | long (n, /trade) | short/long |
|---|---|---|---|---|
| `bybit BTC` | 847 | 363, −0.003086 | 484, −0.005161 | **1.67×** |
| `binance BTC` | 891 | 424, −0.004341 | 467, −0.007777 | **1.79×** |
| **`exness XAU`** | 402 | 255, −0.014957 | **147, +0.004440** | **−0.30×** |

Ratio > 1 means short loses less per trade.

**The two BTC routes agree closely — short is 1.67× and 1.79× better per trade.**
That is unusual for this arc: almost every effect tested has disagreed across
routes, and these two agree.

**On `exness XAU` the sign inverts.** The long side is **positive**: 147 trades,
**+0.65265 total**, +0.004440 per trade — while shorts lose −3.81407 across 255
trades. **The entire loss on that route sits on the short side**, and gold is
also the route that trades short most often (63.4% of trades).

This is the first time in the arc that any decomposition of a Portfolio result
has produced a positive component.

## What this does not mean

**Summing the long trades is not a long-only simulation.** Removing shorts
changes which longs happen: the minimum-hold guard gates reversals, a short that
never opens changes the next long's timing and entry, and the risk layer sees a
different position sequence. **+0.65265 is not a prediction of long-only
performance on this route.** It has to be run, and no flag exists to run it
(r383).

**And the obvious explanation is one this arc has already caught itself on.**
Gold rose over this window; a long-biased result on a rising asset may be drift,
not edge. Rounds 254–257 went through exactly this: r255 found the favourable
window "neither unique nor predictable, and drift does explain it", and r257
found the control population confirmed a tautology. A positive long side on gold
must be compared against the drift available to any long exposure over the same
bars before it means anything.

That comparison has not been made and is the first thing to do, ahead of any
side-restriction implementation.

## Verification status of the transaction

FIX round 3 is running for **P2-3** (the gate report omits `data_as_of`). Round
3's findings also record, for the OpenSpec design rather than for the worker,
that task 1.3's end-to-end equality form **cannot be executed** with the current
output surface, and instruct that **no new report be added to satisfy it** — the
unit-level equality test, the single shared replay function, and the containment
invariants are accepted as sufficient.

Everything else is closed: P1, P2-1, P2-2, task 4.2's reconciliation, 702 tests
passing in my own run on `f158e04`, `finance-core` untouched.

## What is proven, and what is not

Proven:

- The three-route side split above; `bybit BTC` from a rolling-window export,
  the two pinned routes from `--as-of 2026-08-31T00:00:00Z`.
- `exness XAU`'s long side totals **+0.65265** over 147 trades in that run.
- The two BTC routes agree in direction and closely in magnitude.

Not proven, and deliberately not claimed:

- **That long-only would be profitable on `exness XAU`.** The split is
  descriptive; the position sequence changes when a side is removed.
- **That gold's positive long side is edge rather than drift.** Untested, and
  the arc has already found this exact shape to be a tautology risk (r255,
  r257). I am treating it as unexplained until the drift comparison is run.
- That the BTC agreement generalises. Two routes of the same instrument, whose
  prices track each other closely (r276 measured their volatility identical to
  three decimals), are close to one observation, not two.
- That the split is stable across windows. One window each; r382 showed a
  three-candle shift moves route PnL by 8.3%, and these are per-side
  subaggregates of similar runs.

## Named next step

Before anything is implemented: compare `exness XAU`'s long-side result against
the passive drift over the same bars — if a long exposure earns the same or more
without the strategy, the positive component is drift and the direction closes.
That is a data question answerable from the emitted records plus the kline
series, at **zero containers**.
