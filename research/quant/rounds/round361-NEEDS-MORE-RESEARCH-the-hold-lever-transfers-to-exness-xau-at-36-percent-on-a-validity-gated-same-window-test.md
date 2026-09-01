# DRIFT IS NOT PROPORTIONAL TO THE SHIFT (Round 362)

This file measured a **36-candle** shift moving `exness XAU` PnL by **0.25040**. A **4-candle**
shift moved **nothing**: round 362's hold-72 arm at 57,933 candles reproduced this file's
−1.00705 with 229 trades **exactly**.

So drift is **unpredictable rather than proportional** — a small shift can be inert if the extra
bars produce no decisions. That is an argument for the `candle_count` guard, **not** a licence to
compare across rounds. See `round362-NEEDS-MORE-RESEARCH-the-hold-ladder-saturates-on-btc-but-not-on-xau-where-144-still-gains-30-percent.md`.

---

# Round 361 — NEEDS-MORE-RESEARCH: run properly, `exness XAU` **does** respond to the hold lever — **+36.0%** — and the validity gate passed exactly as designed: identical `candle_count` and a **byte-identical** `legacy` control. The lever now has same-window evidence on **three routes**, and only `binance BTC` keeps Target 3.

Classification: **NEEDS-MORE-RESEARCH** — the largest, broadest effect this arc has found, still
unpromotable for a structural reason. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## Redoing the test Round 360 voided

Round 360's transfer test compared a fresh hold-72 run against a hold-36 run from an earlier
round, and the windows differed by 40 candles — the `legacy` control moved 0.306 against a
treatment "effect" of 0.315, so the comparison died. Its prescription was explicit: **run both
arms in the same round.**

**Pre-registered, validity gate first:** the two runs must report **identical `candle_count`** and
an **identical `legacy_selected_rule`** (trades and PnL) — `legacy` bypasses the construction
guard, so it *must* be invariant to the hold. If either differs, the comparison is void.
**Given validity:** hold 36 → 72 changes `one_target` PnL by **≥ 10%** relative → `exness XAU`
responds; **< 10%** → the lever is confined to routes where the guard bites hard.

## Validity gate — passed on both criteria

| check | hold 36 | hold 72 | verdict |
|---|---|---|---|
| `candle_count` | **57,929** | **57,929** | same window |
| `legacy_selected_rule` | 345 trades, **−1.633800** | 345 trades, **−1.633800** | **byte-identical** |

The control behaved exactly as the theory requires: guard-free, so untouched by the hold. That is
also a direct confirmation of Round 360's diagnosis — when the window is held fixed, the drift it
blamed disappears entirely.

## Result — it responds, and strongly

| hold | `one_target` trades | trades/week | `one_target` PnL | trade reduction | `execution_cost` rejections |
|---|---|---|---|---|---|
| 36 (deployed) | 270 | 6.30 | −1.57256 | 0.2174 | 97 |
| **72** | 229 | **5.34** | **−1.00705** | 0.3362 | 71 |

**Delta +0.56550, relative +36.0% — the "responds" branch fires.**

**This corrects how I read Round 358.** There I measured guard-at-36 against guard-free on
`exness XAU` at **0.44%** and treated that as "the guard barely matters on this route". Those are
different quantities: the **first** 36 decisions of hold are worth roughly nothing here, the
**next** 36 are worth **36%**. Absence of a level effect said nothing about the parameter's
marginal leverage, and I should not have generalised from it.

## The three-route picture, all same-window

| route | PnL 36 → 72 | improvement | trades/week | Target 3 |
|---|---|---|---|---|
| `exness XAU` @300 | −1.57256 → −1.00705 | **+36.0%** | 6.30 → 5.34 | fail → fail |
| `bybit XAUT` @500 | −1.57738 → −1.24701 | +20.9% | 3.46 → 3.01 | fail → fail |
| `binance BTC` @500 | −4.74869 → −2.74744 | **+42.1%** | 9.65 → **7.24** | **pass → pass** |

**The lever works on every route tested — 21% to 42% — and on two of three it buys the PnL with
frequency the route could not spare.** Only `binance BTC` still clears the 7.0/week bar after the
step, and its gross is **negative** at that window (Round 342), so a smaller loss there is not a
route to profit.

## A concrete number for Round 360's rule

Two `exness XAU` @300 hold-36 runs, four hours apart:

| run | candles | `one_target` PnL |
|---|---|---|
| Round 349, 18:30 | 57,965 | −1.32216 |
| Round 361, 22:30 | **57,929** | **−1.57256** |

**A 36-candle window shift (three hours) moved PnL by 0.25040 — 18.9% of the scale.** That is the
size of the drift Round 360 warned about, measured directly. Any cross-round comparison on a
session instrument at this window size is unusable without matching `candle_count`.

## What is proven, and what is not

Proven:

- The validity gate: identical `candle_count` (57,929) and byte-identical `legacy` (345 trades,
  −1.633800) across the two arms.
- `exness XAU` @300: hold 36 → 270 trades / −1.57256; hold 72 → 229 trades / −1.00705; +36.0%.
- The three-route table above, each pair verified same-window.
- The drift measurement: 36 candles ↔ 0.25040 of PnL on this route and window.

Not proven, and deliberately not claimed:

- **That hold 72 is better out of sample.** Unchanged and structural:
  `--portfolio-minimum-hold-decisions` conflicts with `--daily-profit-gate`, so **no holdout score
  exists for this parameter** and promotion condition 1 cannot be met. Three routes of
  full-window improvement is not OOS evidence.
- That the lever helps the joint objective. On two of three routes it **costs** frequency a route
  already failing, and on the third the gross is negative.
- That 36% is the effect size at another window on this route. **One window**, and Round 352's
  nesting caveat applies to any follow-up.
- That the drift figure generalises. It is one route, one window size, one three-hour gap;
  24/7 routes showed **zero** drift over similar gaps.
- Any promotion. The blocker is unchanged and is a tooling gap, not a research one.
