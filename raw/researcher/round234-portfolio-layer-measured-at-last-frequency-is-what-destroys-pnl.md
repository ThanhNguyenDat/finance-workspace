# Round 234 — The first Portfolio-layer measurement of the session: both routes earn positive gross edge and lose everything to friction, and BTC's 8x higher frequency costs it 15x more

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The gap this closes

Twenty-nine iterations analysed **Alpha-layer** candidates. The program's actual
objective is **Portfolio-layer** profitability, and `--daily-profit-gate`
evaluates the *real currently-deployed* decision policy — not an arbitrary
candidate — on holdout. It had not been run once this session.

Both routes, 5m, 1,800-day request, holdout ~360 days:

| metric | **exness XAU/USD** | **binance BTC/USDT** | threshold |
|---|---|---|---|
| closed trades | 232 | **1,877** | — |
| trades / week | **4.52** | **36.50** | >= 7.0 |
| observed days | 306 | 361 | — |
| positive day ratio | 0.281 | 0.382 | >= 0.55 |
| Sharpe | −1.96 | **−6.68** | >= 1.0 |
| Sortino | −2.54 | −6.63 | >= 1.0 |
| **gross PnL before costs** | **+0.475** | **+0.281** | — |
| **total cost drag** | **1.527** | **13.526** | — |
| **net realized PnL** | **−1.052** | **−13.246** | — |
| **cost / gross ratio** | **3.22** | **48.20** | <= 0.5 |
| implied edge/friction | 0.311 | **0.021** | — |
| max total drawdown | 0.013% | 0.135% | <= 10% |

Both fail. Both fail for the same reason, and the reason is now measured on the
deployed policy rather than inferred from candidate sweeps:

> **Gross edge is positive on both routes. Friction is 3.2x that edge on XAU and
> 48x on BTC.**

## The finding: frequency is what destroys Portfolio PnL

BTC trades **8.1x more often** than XAU (36.50 vs 4.52 per week), produces
**less** gross profit (+0.281 vs +0.475), and pays **8.9x more cost** (13.53 vs
1.53). Its distance from break-even is **15x worse**.

This is the Portfolio-layer version of Rounds 213-217, and it is far more
authoritative: those measured arbitrary Alpha candidates, this measures what
production actually runs, over ~360 days of holdout.

It also shows the Portfolio construction layer **is** adding value. Round 217
measured Alpha-layer edge/friction on XAU 5m at a median of **0.035** and a best
family of **0.12**. The deployed Portfolio policy on the same instrument and
interval reaches **0.311** — roughly 3-9x better than the signals it aggregates.
The gating, hold period and stop/take rules do work. They are still 3x short.

## The conflict this exposes, stated precisely

The `minimum_trades_per_week >= 7.0` threshold and profitability are **in direct
opposition on measured production data**:

- **BTC satisfies the frequency target spectacularly** — 36.50/week, 5x the floor
  — and is **48x from break-even**.
- **XAU violates it** — 4.52/week — and is **3.2x from break-even**, fifteen
  times closer.

Round 92 closed the "extend hold" direction because further frequency reduction
would breach the >= 7/week floor, citing ~7.2-9.3/week from `one_target`
backtests. This round measures the deployed policy at **4.52/week on XAU** — the
floor is already breached there, and the route closest to profitability is the
one breaching it.

**The decision this needs is not a research question.** Whether Target 3 should
remain a floor, become a ceiling, or be scoped per instrument is a product call
about what the system is for. Research can say what it costs: at current friction,
every additional trade per week is a net loss on both routes.

## What is proven, and what is not

Proven:

- Deployed Portfolio policy, holdout ~360 days: XAU 232 trades, gross +0.475,
  cost 1.527, net −1.052, cost/gross 3.22; BTC 1,877 trades, gross +0.281, cost
  13.526, net −13.246, cost/gross 48.20.
- Both routes fail `minimum_trades_per_week` in opposite directions relative to
  profitability: BTC at 36.50/week is furthest from break-even.
- The deployed Portfolio policy on XAU 5m reaches edge/friction 0.311 against
  Round 217's Alpha-layer median of 0.035 on the same instrument and interval.

Not proven, and deliberately not claimed:

- That reducing BTC's frequency would make it profitable. Round 92 measured the
  hold lever as sub-additive with stop/take and Rounds 213-215 measured cost
  levers as worth approximately nothing; 48x is not closable by frequency alone.
- Anything from the absolute PnL figures. Sizing is `fixed_notional 5.0` against
  10,000 equity, so total drawdown is 0.013-0.135% and the dollar amounts are
  meaningless in isolation. The **ratios** carry the content.
- That one holdout window settles it. Rounds 219 and 232 measured window and
  configuration sensitivity; this is one window per route.

## One flag raised, not interpreted

The XAU report lists `input_continuity_failed` for all seven non-5m intervals —
e.g. 15m shows **1,266 unverified gaps across 55,917 candles**, 30m shows 1,263 —
while `holdout_interval_continuity` passes and `interval_continuity_violations`
is 0. The two signals disagree and I do not know which governs. Recorded for a
`kline-data-quality` pass rather than guessed at here.
