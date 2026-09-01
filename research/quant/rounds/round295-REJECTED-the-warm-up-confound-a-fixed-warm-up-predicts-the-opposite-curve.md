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

# Round 295 — REJECTED: the warm-up confound. A fixed warm-up predicts a *rising* average-rate curve; both routes fall monotonically.

Classification: **REJECTED** — the confound I raised in Round 294 is refuted, and the
trend finding it endangered is restored. Derived from data already collected.
**Zero containers.**

## Settling Round 294 without the control run it proposed

Round 294 filed a DATA-ISSUE: every `--days N` run starts N days ago, so its earliest
stretch is that run's warm-up, and nested differencing deposits it into the newest
"oldest slice" — which would manufacture exactly the monotone trend I kept finding.
It proposed a control run at 900 days.

**The control run is unnecessary.** The hypothesis makes a prediction that the data
already contradicts.

If a fixed warm-up `W` consumes the oldest part of each run's window, then
`cum(N) = r·(N − W)`, so the **average** rate

```
cum(N)/N = r·(1 − W/N)
```

must **rise** as `N` grows — the fixed cost is amortised over a longer window.

| window | exness BTC avg /week | binance BTC avg /week |
|---|---|---|
| 180d | **10.31** | **9.61** |
| 260d | 9.80 | 9.42 |
| 360d | 9.35 | 8.92 |
| 540d | 7.87 | 8.04 |
| 720d | **6.36** | **6.12** |

**Both fall monotonically, at every step.** That is the opposite of what a fixed
warm-up produces. **A warm-up cannot generate this pattern; it works against it.**

## The second, independent check

Any non-zero `W` makes the *recent* rate **higher** than measured — 265 trades in
180 days becomes 265 in 120 days if `W` were 60 — which **widens** the gap to
`[540,720]`'s 0.39-1.83/week rather than closing it. So the confound, if it exists at
all, strengthens the trend rather than explaining it away.

## What this restores, and what it does not

**Restored**: Round 293's monotone-trend finding, its trend-versus-swing distinction,
and Round 294's 5.64x / 24.70x two-year spreads. The AT RISK flag on Round 293 is
cleared.

**Not restored to certainty**: the trend is now the best explanation of the data, not
a proven one. What is established is narrower and firmer — **a fixed warm-up is not
the explanation**, because it predicts the wrong sign.

Round 294 was right to file rather than bank the result, and the flag cost one round
to raise and one to clear. That is the correct trade against five rounds accumulating
on a method I had reason to doubt.

## What is proven, and what is not

Proven:

- Average rate by window: exness BTC 10.31 / 9.80 / 9.35 / 7.87 / 6.36 per week at
  180 / 260 / 360 / 540 / 720 days; binance BTC 9.61 / 9.42 / 8.92 / 8.04 / 6.12.
- Both sequences fall monotonically at every step.
- A fixed-warm-up model predicts a monotonically **rising** sequence.

Not proven, and deliberately not claimed:

- **That warm-up is zero.** What is shown is that it cannot produce the observed
  curve. A small `W` may well exist and would make the recent rates slightly higher
  than reported.
- That the argument covers a warm-up scaling with window length. It assumes a fixed
  duration, which is what indicator and evidence-synchronisation warm-up is; no
  mechanism for a scaling one is known to me, but I have not looked for one.
- Any cause for the trend itself. Unchanged since Round 289 — still unexplained, and
  Round 290 eliminated the σ² candidate.
- That the erratic-swing routes are unaffected by anything similar. This argument was
  run on the two majors only, because they are the two with five slices.
