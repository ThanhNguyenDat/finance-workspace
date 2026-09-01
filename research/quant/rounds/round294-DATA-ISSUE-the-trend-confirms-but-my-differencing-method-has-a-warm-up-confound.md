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

# RESOLVED (Round 295)

The DATA-ISSUE filed here is **resolved as refuted**. The control run proposed below
was not needed: a fixed warm-up implies `cum(N)/N = r·(1 − W/N)`, which must **rise**
with window length, while both routes' average rates **fall monotonically at every
step**. Warm-up predicts the opposite sign, and any non-zero `W` would *widen* the gap
to `[540,720]` rather than close it.

Filing it was still correct — the alternative was five rounds accumulating on a method
I had concrete reason to doubt. It cost one round to raise and one to clear. See
`round295-REJECTED-the-warm-up-confound-a-fixed-warm-up-predicts-the-opposite-curve.md`.

---

# Round 294 — DATA-ISSUE: the trend "confirms" on both routes, and the magnitude exposes a warm-up confound in the method I have used since Round 289

Classification: **DATA-ISSUE** — the measurement technique has a probable systematic
artifact. Two bounded Docker sweeps (exactly the 2-container budget).

## The registered test, and its result as measured

Round 293 left the substantive limit: *"NOT claimed the trend continues before 540
days."* A 720-day run adds `[540,720]` — a 180-day slice **exactly matching**
`[360,540]`'s width, which also addresses Round 293's uneven-width complaint.

Registered: **the trend continues if `[540,720]` lands below `[360,540]` on each
route.**

| route | [0,180] | [180,260] | [260,360] | [360,540] | **[540,720]** | monotone | **2-yr spread** |
|---|---|---|---|---|---|---|---|
| exness BTC | 10.31 | 8.66 | 8.19 | 4.90 | **1.83** | YES | **5.64x** |
| binance BTC | 9.61 | 9.01 | 7.63 | 6.26 | **0.39** | YES | **24.70x** |

Confirmed on both, monotone across five slices. **And that is where I stop trusting
it.**

## Why the result discredits the method

`binance BTC` gained **ten trades across 180 days** (620 → 630 cumulative). For a
route running ~9/week today, that is not a slow period — it is a route that was
barely trading at all.

**The confound:** every `--days N` run *starts* N days ago, so its earliest stretch is
that run's own warm-up — indicators filling and, more restrictively,
`portfolio_evidence` needing **all eight required intervals synchronized including 1d
and 12h** (Round 267). A longer run pushes its warm-up further back, so differencing a
longer run against a shorter one **deposits that suppressed period into the new oldest
slice** — precisely where I keep finding "the trend".

A monotone decline going back is exactly what this artifact would manufacture, on
every route, regardless of what the market did.

## How far the damage reaches — and where it does not

**It does not explain everything.** Round 289's oldest slices are not uniformly
depressed: `bybit XAUT`'s `[260,360]` is **11.20/week, its highest**, and
`exness XAU`'s is 7.63 against a 3.89 newest slice. So warm-up is not the whole story
and the erratic-swing routes are not obviously affected.

**But it threatens every oldest-slice number I have reported**, and hardest on the
180-day slices, where Rounds 293 and 294 found the "trend". Concretely at risk:

- Round 293's monotone-trend finding and its "two kinds of non-stationarity";
- this round's 5.64x and 24.70x;
- the oldest slice of every nested comparison since Round 289.

**Not at risk**: the fleet Target 3 table (Rounds 285-288), which uses whole-window
rates rather than differenced slices, and Round 289's core point that the *window
effect* exists.

## What would settle it

A run whose window **starts well before** the period of interest, so the period is not
that run's warm-up — for example measuring `[540,720]` from a 900-day run rather than
a 720-day one. If the rate rises, the trend is an artifact; if it stays at 0.39, it is
real. That is one container per route and it is the next round's job.

I am filing this rather than quietly continuing the series, because five rounds of
"the trend continues" would otherwise accumulate on a method I now have concrete
reason to doubt.

## What is proven, and what is not

Proven:

- `exness BTC` 720d = 654 cumulative trades; `binance BTC` = 630.
- Differenced `[540,720]` rates of 1.83 and 0.39 per week; both sequences monotone
  across five slices; 2-year spreads 5.64x and 24.70x **as measured by differencing**.
- `binance BTC` added 10 trades in 180 days.
- Round 289's oldest slices are not uniformly depressed.

Not proven, and deliberately not claimed:

- **That the trend is real.** The registered criterion passed, and I am declining to
  bank it because the confound would produce the same result.
- **That the trend is an artifact.** Equally unestablished — the non-uniform
  depression in Round 289 argues against a simple universal warm-up effect.
- The length of any warm-up. Not measured; Round 267 established which intervals must
  synchronize, not how long that takes.
- That earlier rounds' conclusions are wrong. They are **flagged as at risk**, which
  is not the same, and the fleet Target 3 table does not use this method.
