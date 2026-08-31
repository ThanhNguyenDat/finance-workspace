# SATURATION IS ROUTE-SPECIFIC (Round 362)

The saturation this file measured on `binance BTC` — 72 → 144 buying only **3.5%** — **does not
hold on `exness XAU`**. The same step there, on a validity-gated same-window pair (57,933 candles,
`legacy` identical at 345 / −1.633800), gains **+30.3%** (−1.00705 → −0.70183), for **+55.4%**
cumulatively from hold 36.

So saturation is a property of the **route**, not of the lever. On XAU it costs frequency the
route cannot spare: 5.34 → **3.83 per week** on a route already failing Target 3 at every hold.
See `round362-NEEDS-MORE-RESEARCH-the-hold-ladder-saturates-on-btc-but-not-on-xau-where-144-still-gains-30-percent.md`.

---

# THE VOIDED TEST, REDONE AND VALID (Round 361)

This file's prescription — run both arms in the same round — was followed and **the validity gate
passed on both criteria**: identical `candle_count` (**57,929**) and a **byte-identical** `legacy`
control (345 trades, **−1.633800**), exactly as the theory requires of a guard-free ledger. The
drift this file diagnosed vanishes when the window is held fixed.

Result: `exness XAU` @300 hold 36 → 72 gives **−1.57256 → −1.00705, +36.0%** — **it does
respond**, contrary to the expectation carried from round 358. And this file's warning now has a
number: two hold-36 runs four hours apart differ by **36 candles** and **0.25040 of PnL — 18.9% of
the scale**. See `round361-NEEDS-MORE-RESEARCH-the-hold-lever-transfers-to-exness-xau-at-36-percent-on-a-validity-gated-same-window-test.md`.

---

# Round 360 — DATA-ISSUE: two runs from different rounds are **not the same window**, and the `legacy` ledger is a **free drift control** that says so. It voids my transfer test — while the same-window BTC ladder shows the hold lever **saturates at 72** and breaks Target 3 at 144.

Classification: **DATA-ISSUE** — a comparison-design flaw found in my own work, with a cheap
reusable guard, plus one clean result from the arm that survived. Two bounded Docker sweeps
(exactly the 2-container budget), **XAU-first**.

## Two pre-registered questions

Round 359 named both:

- **H1 (transfer)** — on `exness XAU`, hold 36 → 72 changes `one_target` PnL by **< 10%**
  relative → the lever is route-dependent and tied to where the guard bites (Round 358 measured
  0.4% there); **≥ 10%** → the route responds after all.
- **H2 (monotonicity)** — `binance BTC` hold 144 improves on hold 72's −2.74744 → the ladder
  continues; otherwise it turns, as the band lever did in Rounds 330-335.

## H2 — clean, and it answers the more useful question

All three `binance BTC` runs report **143,998 candles**, so the window is identical:

| hold | trades | trades/week | `one_target` PnL | step gain | `execution_cost` rejections |
|---|---|---|---|---|---|
| 36 (deployed) | 689 | 9.65 | −4.74869 | — | 189 |
| **72** | 517 | **7.24** | **−2.74744** | **+2.00126 (42.1%)** | 111 |
| 144 | 368 | **5.15** | −2.65041 | **+0.09702 (3.5%)** | 46 |

**The ladder continues but saturates hard.** The second doubling buys **3.5%** where the first
bought **42.1%**, and it costs the frequency target: **5.15 trades/week fails the 7.0 bar** that
hold 72 still cleared.

**So among tested values, hold 72 is the joint-objective point** — nearly all the available PnL
improvement, with Target 3 intact. Pushing to 144 is close to free in PnL and expensive in
frequency.

(The `execution_cost` rejections falling 189 → 111 → 46 is consistent: a longer hold blocks
reversals before the risk gate ever sees them.)

## H1 — void, and the reason is the finding

`exness XAU` @300, hold 36 (from Round 349) against hold 72 (this round):

| hold | `one_target` trades | `one_target` PnL | `legacy` trades | **`legacy` PnL** | candles |
|---|---|---|---|---|---|
| 36 | 280 | −1.32216 | 355 | **−1.32799** | **57,965** |
| 72 | 229 | −1.00705 | 345 | **−1.63380** | **57,925** |

The measured "effect" is **+0.31511 (+23.8%)**, which would fire the "responds after all" branch.

**It is not usable.** The two runs are **40 candles apart** — different windows, three and a half
hours of wall-clock between them — and `legacy_selected_rule` **bypasses the construction guard
entirely**, so it must be invariant to the hold parameter. It moved by **0.30581**.

**The drift on the control is the same size as the effect on the treatment** (0.306 against
0.315). H1 is void. Whether `exness XAU` responds to the hold lever is **unknown**, and the
correct experiment is both arms in one round.

## The reusable guard, and it is already emitted

Every run's first ECS line carries `candle_count`, `train_candle_count`,
`validation_candle_count`, `holdout_candle_count`
(`event.dataset: research.backtest_candle_count`). **Two runs are comparable only if
`candle_count` matches.** Checked across this round's work:

- `binance BTC` 36/72/144 — 143,998 / 143,998 / 143,998 → **same window**, H2 stands.
- `bybit XAUT` 36/72 (Rounds 358/359) — 143,998 / 143,998 → **same window**, Round 359's XAUT arm
  stands.
- `exness XAU` 36/72 — 57,965 / 57,925 → **different**, H1 void.

Crypto routes trade 24/7 and their windows quantise to the same bar count over tens of minutes;
`exness XAU` is a session instrument and its window moves. **The drift is route-specific, which is
exactly why it must be checked rather than assumed.**

And when only Portfolio-construction parameters vary, **`legacy_selected_rule` is a free control**:
it is guard-free, so any movement in it is drift, not treatment.

## What is proven, and what is not

Proven:

- The `binance BTC` three-point table, on a verified-identical 143,998-candle window.
- `exness XAU` hold 36 vs 72 measured on windows of 57,965 and 57,925 candles, with `legacy`
  moving −1.32799 → −1.63380 despite being invariant to the hold.
- `bybit XAUT`'s Round 358/359 pair shares a window (143,998 both).
- `candle_count` is emitted on every run in the first ECS log line.

Not proven, and deliberately not claimed:

- **Whether `exness XAU` responds to the hold lever.** The test is void; I am not reporting the
  +23.8% as an effect, and Round 358's 0.4% figure is about the guard's *presence*, not the
  parameter's leverage.
- That hold 72 is optimal. It is the best of **three tested values on one route at one window**,
  and the curve between 72 and 144 is unsampled.
- That saturation transfers. `bybit XAUT` was not extended past 72 this round.
- **That any of this is promotable.** Unchanged from Round 359: `--portfolio-minimum-hold-decisions`
  conflicts with `--daily-profit-gate`, so no holdout score exists for this parameter and
  promotion condition 1 cannot be met. `binance BTC` also has negative gross at this window
  (Round 342) — a smaller loss there is not a path to profit.
- That earlier cross-round comparisons are all safe. The three checked above are; **others in this
  arc were not verified this way and should be re-checked against `candle_count` before being
  relied on.**
