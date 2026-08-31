# UNRELIABLE — METHOD DEFECT (Round 300)

Every **Portfolio-layer slice rate** in this file comes from **nested differencing**
of `--days` runs, and Round 300 found that method invalid for Portfolio counters: the
Portfolio refits its interval and strategy weights **on every kline** from cumulative
Alpha performance (`portfolio_decision_replay.rs:317`), so two runs of different
length carry **different weights over every bar they share**. A difference between a
540-day and a 360-day run is therefore not "what happened in `[360,540]`".

The weight-free Alpha layer, which *is* cleanly nested (76 of 77 strategies strictly
monotone), shows **no** corresponding variation — 3,773.9 / 3,560.4 / 3,499.5 trades
per week across the same slices, a 4.5% spread against the Portfolio's 7-17x.

Treat this file's Portfolio slice rates as **unreliable pending re-derivation** — not
as disproved; a method defect removes evidence, it does not establish the opposite.
Coverage facts, single-window measurements and live production readings in this file
are unaffected. See
`round300-DATA-ISSUE-portfolio-weights-refit-every-kline-so-nested-differencing-does-not-isolate-a-calendar-period.md`.

---

# CORRECTION (Round 297)

This file's "trend versus swing" dichotomy places `bybit XAUT` on the wrong side of
itself. Its cited sequence **1.79 → 3.85 → 11.20 is strictly monotone** going back in
time — read forwards, that route's rate **fell** smoothly across all three slices. It
is not "non-monotone, swinging"; it is monotone with the **opposite sign** to the
majors. Three of six routes are monotone across every slice measured, not two.

The dichotomy conflated *shape* with *direction*. Everything else in this file —
the 2.10x/1.53x spreads, the 540d cumulative counts, and the point that the majors'
Target 3 passes sit on a rising trend — stands. See
`round297-REJECTED-the-deep-slice-collapse-is-not-a-method-artifact-and-bybit-xaut-was-misclassified-as-erratic.md`.

---

# RISK CLEARED (Round 295)

The AT RISK flag below is **withdrawn**. Round 295 refuted the warm-up confound
without needing the control run: a fixed warm-up predicts the average rate
`cum(N)/N = r·(1 − W/N)` to **rise** with window length, and both routes **fall
monotonically at every step** (10.31 / 9.80 / 9.35 / 7.87 / 6.36 and 9.61 / 9.42 /
8.92 / 8.04 / 6.12 per week). Warm-up works against the observed pattern, not for it.

This file's monotone-trend finding and its trend-versus-swing distinction stand. See
`round295-REJECTED-the-warm-up-confound-a-fixed-warm-up-predicts-the-opposite-curve.md`.

---

# AT RISK (Round 294)

This file's monotone-trend finding, and the "trend versus swing" distinction built on
it, rest on **nested differencing** — and Round 294 identified a probable confound in
that method.

Every `--days N` run *starts* N days ago, so its earliest stretch is that run's own
warm-up (`portfolio_evidence` needs all eight required intervals synchronized,
including 1d and 12h — Round 267). Differencing a longer run against a shorter one
deposits that suppressed period into the **new oldest slice** — exactly where the
trend appears. `binance BTC` gained **ten trades across 180 days** at `[540,720]`,
which is not a slow period but a route barely trading.

The finding is **not withdrawn** — Round 289's oldest slices are not uniformly
depressed, so warm-up cannot be the whole story. It is flagged as **at risk pending
the control run** named in Round 294: measure `[540,720]` from a 900-day window, where
it is no longer the warm-up region. See
`round294-DATA-ISSUE-the-trend-confirms-but-my-differencing-method-has-a-warm-up-confound.md`.

---

# Round 293 — REJECTED: `exness BTC`'s stability was a one-year artifact. But the majors **trend monotonically** where the others swing — a different kind of non-stationarity.

Classification: **REJECTED** — my pre-registered criterion fired. Two bounded Docker
sweeps (exactly the 2-container budget). Qualifies Round 292.

## Testing Round 292's own named limit

Round 292 closed with: *"three slices per route is **one year**; a route stable across
three quarters could still move across years."* Both BTC majors have five years of
data, so a 540-day run adds a `[360,540]` slice.

Registered before running: **both spreads stay under 2x; refuted if either reaches
2x.** I noted the pre-existing monotone decline going back in time made this a real
test cutting both ways, and that I was not predicting stability merely to chase Round
292's result.

| route | [0,180] | [180,260] | [260,360] | **[360,540]** | 1-year spread | **18-month spread** |
|---|---|---|---|---|---|---|
| **exness BTC** | 10.31 | 8.66 | 8.19 | **4.90** | 1.26x | **2.10x** |
| binance BTC | 9.61 | 9.01 | 7.63 | **6.26** | 1.26x | **1.53x** |

**`exness BTC` crosses the line at 2.10x. By the criterion I set, the finding is
refuted:** Round 292's "genuinely stable" was a one-year artifact on that route — the
same shape of error Round 291 found in Round 289, one level out, and now found in my
own work again.

`binance BTC` stays at 1.53x, so the refutation is one route of two, and `exness BTC`
clears the threshold only narrowly.

## The more useful finding: two different kinds of non-stationarity

Both majors decline **monotonically** going back in time — 10.31 → 8.66 → 8.19 → 4.90
and 9.61 → 9.01 → 7.63 → 6.26. Read forwards, **both routes' trade rates have roughly
doubled over eighteen months**, smoothly.

The four other routes do not do this. `bybit XAUT` runs 1.79 → 3.85 → 11.20;
`bybit BTC` runs 3.11 → 11.03 → 2.66 — **non-monotone**, swinging.

So "stable versus unstable" was the wrong dichotomy:

| kind | routes | signature |
|---|---|---|
| **smooth trend** | exness BTC, binance BTC | monotone, ~2x over 18 months, looks stable in any short window |
| **erratic swing** | the other four | non-monotone, 3.5-6.3x **within** one year |

`exness BTC`'s 2.10x and `bybit XAUT`'s 6.26x are both "non-stationary" and are not
the same phenomenon.

## What it means for Target 3

The two passing routes pass **on a rising trend**, not on a plateau. Their oldest
measured slice, `[360,540]`, sits at **4.90** and **6.26** per week — `exness BTC`
below the 7/week bar and `binance BTC` below it too. **Eighteen months ago, on this
configuration, neither major would have passed Target 3.**

That does not change today's verdict, which rests on recent data. It does mean the
passes are a property of the current period, and the confidence Round 286 attached to
them ("+27% to +40% clear of the bar") describes now, not the configuration.

## What is proven, and what is not

Proven:

- `exness BTC` 540d = 607 cumulative trades; `binance BTC` 540d = 620.
- `[360,540]` rates of 4.90 and 6.26 per week; 18-month spreads 2.10x and 1.53x.
- Both majors' four slices are monotone in time; two of the other routes' are not.

Not proven, and deliberately not claimed:

- **Any cause for the trend.** Unchanged since Round 289 — no cause has been
  established for any of the rate variation, and Round 290 eliminated the σ²
  candidate. I am not proposing one.
- That the trend continues before 540 days. One more slice; the routes have five
  years and I have measured eighteen months.
- That the two kinds are really distinct. Four monotone points on two routes against
  three non-monotone points on two others is a **description of six sequences**, not a
  test, and `binance XAU` and `exness XAU` have too few slices to classify.
- That `binance BTC` is stable. It is at 1.53x over 18 months and trending; it did
  not cross my threshold, which is not the same as being flat.
- That the slices are directly comparable. `[360,540]` is 180 days against 80-180 for
  the others — uneven widths I did not control for.
