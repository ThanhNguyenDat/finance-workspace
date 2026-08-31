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

# QUALIFICATION (Round 292)

This file's suspicion — that the "stable" group was wholly a pooling artifact, since
"every route I have unpooled has turned out non-stationary" — was **too broad**.

Round 292 unpooled the last two: `exness BTC` **1.26x** (10.31 / 8.66 / 8.19) and
`binance BTC` **1.26x** (9.61 / 9.01 / 7.63). **Both are genuinely stable**, so Round
289's classification was correct for them and wrong only for `exness XAU`.

This file's own measurements stand — `exness XAU`'s 3.46x, `bybit XAUT`'s 6.26x, and
the corrected regression (slope +0.771) — as does its point that Round 290 overstated
its rejection. What needed narrowing is the inference from "four for four" to a
general artifact. See
`round292-REJECTED-my-prediction-the-two-btc-majors-are-genuinely-stable-and-the-fleet-splits-cleanly.md`.

---

# Round 291 — CORRECTION: `exness XAU` looked stable only because it was pooled. Every route I have unpooled is non-stationary.

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (exactly the
2-container budget). Corrects Round 289; refines Round 290.

## Cleaning the design Round 290 flagged

Round 290 rejected the σ² law for within-route time variation but named its own
weakness: *"four routes contribute only pooled [0,260] points, and pooling variances
across a regime change is itself lossy… **the design is not clean**."* Adding a
180-day run splits a pooled `[0,260]` into clean `[0,180]` and `[180,260]`. Two
containers, XAU-first.

| route | [0,180] | [180,260] | [260,360] | **spread** | Round 289 said |
|---|---|---|---|---|---|
| **exness XAU** | **3.89** | **13.47** | 7.63 | **3.46x** | **1.12x — "stable"** |
| **bybit XAUT** | 1.79 | 3.85 | 11.20 | **6.26x** | 4.62x |

**`exness XAU` was classified stable purely because its `[0,260]` was pooled.** Its
true sub-period rates run 3.89 → 13.47 → 7.63, a **3.46x** swing — squarely with the
routes Round 289 called unstable. `bybit XAUT` worsens from 4.62x to 6.26x.

## The consequence for Round 289's split

Round 289 divided the fleet into three stable routes (1.12-1.24x) and three unstable
ones (3.48-4.62x). **The stable group is now down to two — and neither has been
unpooled.**

| route | spread | slices |
|---|---|---|
| bybit XAUT | 6.26x | **unpooled** |
| bybit BTC | 4.14x | **unpooled** |
| binance XAU | 3.48x | **unpooled** |
| exness XAU | **3.46x** | **unpooled (this round)** |
| binance BTC | 1.24x | **still pooled** |
| exness BTC | 1.20x | **still pooled** |

**Every route I have unpooled has turned out non-stationary. The only two that still
look stable are the only two I have not unpooled.** That is not evidence they are
stable; it is the same artifact, un-tested.

## Round 290's rejection survives, but it was overstated

Re-running Round 290's regression on the cleaner slices:

| | slope | Pearson r |
|---|---|---|
| Round 290 (4 pooled points) | +0.415 | +0.191 |
| this round (2 pooled points) | **+0.771** | **+0.323** |

Still below the 1.0 floor I registered, so **the rejection survives** — exactly the
directional prediction made before running. But the slope nearly doubled once the
pooling was removed, so **Round 290's "refuted, and not narrowly" was too strong**.
At +0.771 against a theoretical +2, σ² carries *some* within-route signal — roughly a
third of what the law demands — rather than none.

I also note the method that produced this: I set a **directional** prediction, not a
band, after missing three bands in Rounds 286-288. It worked as a test.

## What is proven, and what is not

Proven:

- `exness XAU` 180d = 100 trades (3.89/week); `bybit XAUT` 180d = 46 (1.79/week).
- Unpooled sub-period rates and spreads as tabulated: `exness XAU` 3.46x,
  `bybit XAUT` 6.26x.
- The regression on 15 slices gives slope +0.771, r +0.323, against Round 290's
  +0.415 / +0.191.

Not proven, and deliberately not claimed:

- **That `exness BTC` and `binance BTC` are non-stationary.** They are untested. What
  is shown is that their apparent stability rests on the same pooling that produced a
  false stable reading for `exness XAU` — a reason to doubt, not a finding. Unpooling
  them is the next round's obvious job.
- That σ² has real within-route power. +0.771 with r = +0.323 on 15 slices, four of
  which are still pooled, is a weak positive at best and does not clear the floor I
  set.
- Any cause for the non-stationarity. Unchanged since Round 289; still unexplained.
- That Round 289's core finding fails. Its central point — the window effect **is**
  non-stationarity — is strengthened by this round, not weakened. What fails is its
  stable/unstable classification.
