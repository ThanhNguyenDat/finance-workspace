# THE STATED CONDITION HAS OCCURRED (Round 371)

This file called both Target 3 passes **window-robust** across 260d -> 360d
(`binance BTC` 9.42 -> 8.92, a +27.4% margin) and wrote its own stopping condition:
*"Either falling below 7 would mean no single-window verdict is trustworthy."*

At **900 days**, on the same deployed parameters, `binance BTC` scores **6.80
trades/week** - 874 trades over a window whose 259,198 candles are exactly 900.0 days,
so no denominator caveat applies. **It falls below 7.** The sequence across windows this
arc has actually run is 9.42 (260d) / 8.92 (360d) / 9.65 (500d) / **6.80 (900d)** -
non-monotone, with the crossing only at the deepest window.

This file's measurements and its route-specific-shift finding stand. What has occurred is
the condition it named for its own conclusion. See
`round371-NEEDS-MORE-RESEARCH-the-construction-guard-is-the-arcs-first-cross-route-cross-window-stable-effect-and-binance-btcs-target-3-pass-fails-at-900-days.md`.

---

# CORRECTION (Round 287)

This file's closing argument — that the three wide failures are safe because their
margins (−21% to −65%) exceed the observed 3-5% window effect — is **refuted**, and
this file flagged it as "an argument, not a measurement".

Measured (Round 287): `binance XAU` shifts **−43.2%** (3.63 → 2.06/week) and
`bybit XAUT` **+100.9%** (2.42 → 4.86/week). **The 3-5% figure was generalised from
the two highest-frequency routes and does not hold on quiet ones.**

What survives: this file's own finding that the **two passing routes** are
window-robust (9.80→9.35, 9.42→8.92, both ≥27% clear of the bar) — those measurements
stand. What does not: using that effect size to certify the failures. `bybit BTC`
(−21%, still one window) is now the least secure verdict in the table, not a safe one.
See `round287-CORRECTION-the-window-effect-is-3pct-on-busy-routes-and-up-to-101pct-on-quiet-ones.md`.

---

# Round 286 — The two Target 3 passes survive a 100-day window change; only `exness XAU` is genuinely on the threshold

Classification: **NO-CHANGE** — Round 285's fleet table stands, and its one ambiguous
row is now isolated. Two bounded Docker sweeps (exactly the 2-container budget).

## The question Round 285 raised and did not answer

Round 285 found `exness XAU`'s Target 3 verdict **flips** between windows (7.06/week
at 360 days, 6.84 at 260). That threatened the whole table: if every verdict moves
with the window, "2 of 6 pass" is not a fleet status.

Written to disk before either container launched (`precommit_r286.md`): test the two
**passing** routes on the second window. **Prediction: both stay inside 9.0-10.5/week
if the window effect is the ~3% seen on `exness XAU`. Either falling below 7 would
mean no single-window verdict is trustworthy.**

| route | 260d | 360d | shift | verdict 260d | verdict 360d |
|---|---|---|---|---|---|
| exness BTC/USD | 9.80 | **9.35** | **−4.6%** | PASS | **PASS** |
| binance BTC/USDT | 9.42 | **8.92** | **−5.3%** | PASS | **PASS** |

## The substance held; my band was slightly too tight

**Neither route came near the bar** — margins of +33.6% and +27.4% at 360 days. The
substantive prediction is confirmed and Round 285's passes are **window-robust**.

**But `binance BTC` landed at 8.92, just outside my 9.0-10.5 band.** I set that band
assuming a ~3% window effect; the actual effect is **4.6-5.3%**, about half again as
large. The prediction's *direction and consequence* were right, its *precision* was
not, and I am recording the miss rather than rounding 8.92 into "inside".

## The shift is route-specific, not a window bias

| route | 260d → 360d |
|---|---|
| exness BTC | −4.6% |
| binance BTC | −5.3% |
| **exness XAU** | **+3.2%** |

`exness XAU` moves **up** going to the longer window while both BTC routes move
**down**. So this is not a systematic artifact of window length — it is route-specific
variation of a few percent, which matters only where the margin is smaller than it.

## The fleet status, firmed up

| status | routes | margin vs 7/week |
|---|---|---|
| **passes robustly** (both windows) | exness BTC, binance BTC | +27% to +40% |
| **genuinely ambiguous** | exness XAU | ±3% — flips |
| **fails by a wide margin** | bybit BTC, binance XAU, bybit XAUT | −21%, −48%, −65% |

Only **one** row of Round 285's table is window-sensitive, and it is the one already
flagged. The other five verdicts are not close enough to the bar for a few percent to
matter.

## What is proven, and what is not

Proven:

- exness BTC 9.35/week and binance BTC 8.92/week at 360 days, against 9.80 and 9.42 at
  260 days.
- Window shifts of −4.6%, −5.3% (BTC routes) and +3.2% (`exness XAU`) — opposite
  directions.
- Both passing routes clear 7/week on both windows by ≥27%.

Not proven, and deliberately not claimed:

- **That any of this holds in production.** Every figure is a backtest under deployed
  parameters. Round 259's live interval remains uninformative and this round does not
  touch it.
- That two windows establish stability. **Two points per route.** They rule out a
  large window effect, not a moderate one, and a third window was not run.
- That the three wide failures are equally robust. They were measured on **one**
  window each; their margins (−21% to −65%) are far larger than the observed 3-5%
  effect, which is why I treat them as safe — that is an argument, not a measurement.
- Any change to Round 285's conclusions. This round adds robustness, not new status.
