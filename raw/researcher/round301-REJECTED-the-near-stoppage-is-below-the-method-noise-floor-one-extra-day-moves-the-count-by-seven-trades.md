# QUALIFIED (Round 302)

The blanket unreliability above is **route-dependent in magnitude**. On `binance BTC`
the defect is small: a one-day perturbation moves the Target 3 rate by **+1.04%**, and
Round 292's recorded slices imply a 260-day cumulative of 350.1 against an independent
**350** measured in Round 302 — an exact reproduction. On `exness XAU` it is severe: a
**negative** one-day response, a 5.5% perturbation spread, and a **1.87x** swing in the
single-window rate between 180 and 360 days.

The mechanism is instrument-independent; its magnitude is not. Differenced slices stay
unestablished everywhere, but `binance BTC`'s single-window numbers are corroborated
rather than merely unreliable. See
`round302-NEEDS-MORE-RESEARCH-the-defect-is-route-dependent-binance-btc-is-robust-and-exness-xau-is-not.md`.

---

# Round 301 — REJECTED: the `exness XAU` near-stoppage is **below the method's own noise floor**. Adding **one day** to the window changes the Portfolio trade count by **−7**.

Classification: **REJECTED** — the near-stoppage as a real effect is rejected; it is
smaller than the noise the measurement generates. Two bounded Docker sweeps (exactly
the 2-container budget), XAU-first. Quantifies the defect Round 300 filed and could
not measure.

## The gap Round 300 left

Round 300 found in code that the Portfolio refits its weights on **every kline** from
cumulative Alpha performance, so nested runs are not comparable — and closed with the
honest limit: *"I have shown the weights are path-dependent … I have **not** measured
how much the weight trajectories actually diverge, and I have no way to with the
current tool."*

There is a way, and it does not need an as-of flag: **perturb the window start by one
day.** A `--days 361` run is a `--days 360` run plus one extra day at the deep end.
At the local slice rate (0.74/week) that day is worth **0.106 trades**; five days are
worth **0.529**. Any larger movement — and above all any *negative* movement — is
confound, measured directly.

**Registered before running:** if the confound is negligible for `one_target`, then
`|trades(361) − 374| ≤ 1` and `|trades(365) − 374| ≤ 2`, and both differences are
non-negative.

## The result

| `--days` | candles | **`one_target`** | legacy | grid | cost rej | decisions | Alpha 5m |
|---|---|---|---|---|---|---|---|
| 360 | 69,741 | **374** | 462 | 5,092 | 181 | 66,079 | 197,670 |
| **361** | 70,005 | **367** | 455 | 4,928 | 176 | 66,332 | 198,335 |
| **365** | 70,578 | **392** | 481 | 5,262 | 198 | 67,347 | 199,805 |
| 540 | 104,639 | 393 | 471 | 4,860 | 160 | 99,751 | 289,224 |

**One extra day moves `one_target` by −7 trades.** A strictly larger window returned
**seven fewer** Portfolio trades — nesting monotonicity violated, on the one counter I
had believed to be safe. Five extra days move it **+18**. The prediction fails on both
sign and magnitude, at roughly **70x** the expected content of the added data.

`legacy_selected_rule` moves in lockstep (−7, +19), so this is not the hold guard.
`legacy_grid` (−164, +170) and `execution_cost` (−5, +17) do the same, as Round 300
predicted.

## The Alpha control behaves exactly as a clean counter should

| perturbation | extra candles | extra Alpha trades | **Alpha per candle** | **`one_target` per candle** |
|---|---|---|---|---|
| +1 day | 264 | +665 | **2.519** | **−0.0265** |
| +5 days | 837 | +2,135 | **2.551** | **+0.0215** |

The weight-free Alpha layer scales with added data at a **constant 2.52-2.55 trades
per candle — consistent to 1.2%**, and never negative. The Portfolio measure over the
identical added data produces **opposite signs**. The added days are ordinary; the
Portfolio measure's response to them is not.

(The per-day candle counts differ — 264 for the first day, 167/day averaged over five —
because gold CFD closes at weekends. Normalising per candle removes it, which is why
the Alpha ratio is so stable.)

## The noise floor, and what it swallows

Across three window lengths differing by at most five days, `one_target` returns
**367 / 374 / 392** — a spread of **25 trades**, **6.7%** of the cumulative count.

The `[360,540]` slice that Rounds 297-299 pursued is **19 trades**. Recomputing it
against each of the three equally-valid bases:

| base | slice | rate |
|---|---|---|
| 393 − 374 (360d) | **19 trades** | 0.74/week |
| 393 − 367 (361d) | **26 trades** | 1.01/week |
| 393 − 392 (365d) | **1 trade** | 0.04/week |

**The entire anomaly moves from 26 trades to 1 depending on which day I choose as the
window start.** It is not a small effect measured imprecisely; it is **wholly inside
the noise the method generates**, and I spent Rounds 297, 298 and 299 explaining it.

**The near-stoppage is rejected.** Round 298's headline — *"the near-stoppage is real
and bigger"* — was wrong, and the "bigger" came from the same noise that now makes it
vanish.

## What this implies for the rest of the ladder, stated conservatively

Every differenced Portfolio slice smaller than roughly 25 trades on a comparable
window is not established. Two examples from Round 293/296 fall under that line:
`binance BTC`'s `[540,720]` slice is **10 trades**, `exness BTC`'s about **47**.

I measured the floor on `exness XAU` and I am **not** transferring the number to BTC —
the majors have a different bar density, a different candidate set and roughly 1.6x
the trade rate, and the same one-day perturbation on those routes has not been run.
What transfers is the **mechanism**, which is instrument-independent: the weights refit
on every kline in every run.

## What is proven, and what is not

Proven:

- `exness XAU` at the deployed config, same day, same endpoint: `one_target` = 374 at
  360 days, **367 at 361 days**, 392 at 365 days.
- `legacy_selected_rule` 462 / 455 / 481; `legacy_grid` 5,092 / 4,928 / 5,262;
  `execution_cost` 181 / 176 / 198 — all non-monotone in the same direction.
- Alpha 5m cumulative 197,670 / 198,335 / 199,805, giving 2.519 and 2.551 trades per
  added candle; `one_target` gives −0.0265 and +0.0215 over the same added candles.
- The `[360,540]` slice evaluates to 19, 26 or 1 trades depending on which of the
  three bases is used.

Not proven, and deliberately not claimed:

- **A noise floor for any route other than `exness XAU`.** One route, one perturbation
  pair. The BTC figures above are quoted for comparison, not as a verdict on them.
- That the confound is bounded by 25 trades. Three points at ≤5 days of separation
  bound nothing; a 180-day separation could be far worse, and I did not measure it.
- That Portfolio-layer *single-window* measurements are affected. A single run is
  internally consistent; what is broken is **comparing runs of different length**.
  Target 3 verdicts from single windows and from live Redis trade logs are untouched.
- Any cause for the variation the ladder appeared to show. There may be nothing to
  explain.
- That the Alpha layer measures anything about Target 3. It does not, and it must
  never be quoted against it.
