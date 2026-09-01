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

Where this file says "the four erratic routes", read **three**. `bybit XAUT`'s slices
are monotone (falling forward), not erratic; the misclassification originates in
Round 293 and was inherited here. This file's own measurements and its rejection of
volatility are unaffected. Round 297 also tested, and rejected, the rival worry that
the deep-slice collapse used throughout this series is an artifact of window depth.
See `round297-REJECTED-the-deep-slice-collapse-is-not-a-method-artifact-and-bybit-xaut-was-misclassified-as-erratic.md`.

---

# Round 296 — The differencing basis is verified in code, and on clean within-route slices volatility is *inverted*: the most volatile period is the least active one

Classification: **REJECTED** — volatility as the cause of the two-year trend, on the
cleanest data available. Local code inspection plus one read-only query.
**Zero containers.**

## First: verifying the basis I have used for eleven rounds

Every result since Round 285 assumes `one_target` counts trades over the **whole**
`--days` window. If it instead reported only a split — say the 20% holdout — then
cumulative differencing would be meaningless and Rounds 285-295 with it. **I had never
checked.**

`main.rs:555-562` loads `portfolio_series` via `load_portfolio_series(…, args.days, …)`
and `main.rs:631-641` passes that whole series to
`compare_real_portfolio_with_funding`, which replays it end to end
(`portfolio_measurement.rs:105-125`). **No split is applied — `one_target` covers the
full window.** The basis is sound; recording it because it was assumed, not verified.

## Second: volatility on clean within-route slices

Round 290 rejected σ² for within-route variation on 13 slices, four of them pooled;
Round 291 softened that to "slope +0.771 — some signal". The two majors now have
**five clean, unpooled slices each over two years** — the best data this question has
had.

| slice | binance BTC rate | vol | exness BTC rate | vol |
|---|---|---|---|---|
| [0,180] | 9.61 | 0.12773 | 10.31 | 0.12622 |
| [180,260] | 9.01 | 0.16308 | 8.66 | 0.16149 |
| [260,360] | 7.63 | 0.14734 | 8.19 | 0.14264 |
| [360,540] | 6.26 | 0.12123 | 4.90 | 0.12005 |
| **[540,720]** | **0.39** | **0.16480** | **1.83** | **0.16342** |

**On both routes the oldest slice has the highest volatility of the five and the
lowest rate.** σ² requires the opposite. Spearman(rate, vol) = **−0.300** on each
(p = 0.68).

And the shapes differ fundamentally: **rate is strictly monotone on both routes;
volatility is not monotone on either** — it runs 0.128 / 0.163 / 0.147 / 0.121 / 0.165,
swinging while the rate falls steadily.

**Volatility is not the driver of the two-year trend.** Round 290's rejection is
confirmed on data with none of the weaknesses Round 291 identified, and the softening
Round 291 applied does not survive on the majors: this is not "weak positive signal",
it is a negative rank correlation with an inverted extreme.

## Where the cause question stands

Eliminated so far, for the two-year trend on the majors: **warm-up** (Round 295, wrong
sign), **volatility** (this round, inverted), and **data gaps** — both routes carry
526 913 five-minute bars over 1 829 days, exactly 288/day, complete coverage.

Still unexplained. I am not proposing a fourth candidate; Rounds 279-284 are the
standing reason.

## What is proven, and what is not

Proven:

- `one_target` measures the full `--days` window (`main.rs:555-562`, `631-641`;
  `portfolio_measurement.rs:105-125`), so the differencing basis of Rounds 285-295 is
  valid.
- Five-slice rate and volatility sequences for both majors, tabulated.
- Rate strictly monotone on both; volatility non-monotone on both;
  Spearman −0.300 each; oldest slice highest-volatility and lowest-rate on both.
- 5m kline coverage of 526 913 bars / 1 829 days = 288.1/day on both routes.

Not proven, and deliberately not claimed:

- **Significance.** Five slices give a minimum two-sided p of 0.0167; −0.300 sits at
  p = 0.68. What carries weight here is the **inverted extreme and the shape
  mismatch**, not the coefficient.
- That volatility is irrelevant cross-sectionally. Rounds 273/275/285 stand; this
  concerns within-route time variation only, as Round 290 already scoped it.
- Any cause for the trend. Three candidates eliminated, none offered.
- That the majors' pattern generalises to the four erratic routes. They have two or
  three slices each and were not part of this test.
