# CORRECTION (Round 261)

This file's "BTC point estimate above the bar, XAU below" pattern was built on a
**pooled XAU rate that mixed one mature route with two near-dormant ones** —
`exness XAU` has 395 lifetime trades, `binance XAU` has 8 and `bybit XAUT` has 3.
That pooling was mine and it was wrong; it produced an apparent ~3x XAU/BTC gap
that does not exist.

Over their own ~1-year histories the mature routes run **7.60 closes/week
(exness XAU)** against **9.14 (binance BTC)** — a ratio of **1.20x**, and the live
counts in this file are ordinary draws from those rates (p = 0.38 and 0.23). Both
mature routes are **above** the 7/week Target 3 bar, the opposite of what this
file's XAU point estimate suggested.

This file's *measurements* stand — the durable-log completeness verification, the
un-frozen `binance XAU` route, the confirmed stop/take levers, the correctly
dismissed stale checkpoint, and its refusal to issue a Target 3 verdict, which was
right for an even stronger reason than the confidence intervals it gave. What does
not stand is the BTC-vs-XAU pooled comparison. See
`round261-CORRECTION-there-was-no-xau-btc-frequency-gap-my-pooling-created-it.md`.

---

# Round 259 — Target 3, second live reading: point estimates split BTC from XAU, but every route is still statistically undetermined — and the durable log is now verified *complete*, not just atomic

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence only.
**Zero containers.** First round off the Rounds 242-258 thread, which closed last
round.

## Why this round, and what Round 207 asked for

Round 207 built the live Target 3 measurement path from the durable Portfolio trade
log and closed with an explicit instruction: *"Re-read the same keys after roughly
seven days and the numbers become comparable to Round 92's backtest figures for the
first time."* It also stated plainly that its own 25.2-hour window, with one to
three closes per route, **could not support a frequency claim**.

The window is now **46.1 hours** — worker start (all six containers `Up 46 hours`)
to now. That is not the seven days Round 207 asked for, but it is double its
window, and Target 3 is one of the three objectives this loop optimises.

## Part 1 — Target 3: the split is real in the point estimates and absent in the statistics

Closes are `entries / 3` (three capital rules per close), the structure Round 207
established and this round re-confirmed: every route's ZSET holds exactly three
entries per distinct `exit_at`.

| route | closes | point /week | 95% Poisson CI (/week) | verdict vs 7/week |
|---|---|---|---|---|
| binance BTC/USDT | 4 | 14.6 | [3.97, 37.32] | **undetermined** |
| exness BTC/USD | 3 | 10.9 | [2.25, 31.95] | **undetermined** |
| bybit BTC/USDT | 3 | 10.9 | [2.25, 31.95] | **undetermined** |
| binance XAU/USDT | 1 | 3.6 | [0.09, 20.30] | **undetermined** |
| exness XAU/USD | 1 | 3.6 | [0.09, 20.30] | **undetermined** |
| bybit XAUT/USDT | 1 | 3.6 | [0.09, 20.30] | **undetermined** |
| **BTC pooled** | 10 | 12.1 | **[5.83, 22.34]** | **undetermined** |
| **XAU pooled** | 3 | 3.6 | **[0.75, 10.65]** | **undetermined** |

**Not one route, and neither pool, clears or fails Target 3 at 95% confidence.**
Pooled BTC's lower bound is 5.83/week — below the bar — and pooled XAU's upper
bound is 10.65/week — above it.

Round 207's directional hint (BTC above the bar, XAU near or below) survives a
doubled window and is now supported by 10 closes rather than 5. **It is still a
hint.** Doubling the window doubled the counts and barely moved the confidence
bounds, which is what Poisson counting does and is exactly why Round 207 refused
to call it.

Against Round 92's backtest (~7.2-7.3/week at 18 months, ~9.3/week at 5 years):
BTC's live point estimate of 12.1/week sits above both, XAU's 3.6/week below both.
Neither comparison is significant.

**What would settle it**, if the current point estimates are the true rates:

- BTC pooled clears 7/week at 95% after **17 closes ≈ 3.3 more days** of all three
  routes;
- XAU pooled fails 7/week at 95% after **9 closes ≈ 5.8 more days**.

That is the concrete re-read date, and it replaces Round 207's "roughly seven days"
with a number derived from the observed rate.

## Part 2 — the durable log is complete, which Round 207 did not establish

The two independent counters disagreed at first sight. Live Portfolio ledger
`trade_count` minus its `paper-backtest-*` seed gives 6/1/5/2/4/3 = **21**; the
durable log gives 4/1/3/1/3/1 = **13**.

Round 207 verified the log's **atomicity** invariant (index cardinality equals
payload cardinality — still exact on all six routes). It did **not** verify
**completeness** against an independent counter. This round does, because the live
ledger retains its most recent trade records with timestamps:

| route | ledger retained `exit_at` | in durable log? |
|---|---|---|
| binance BTC | 08-25 18:59, 08-27 08:14 | no — **both predate deployment** |
| binance BTC | 08-27 19:59, 08-27 22:59, 08-28 03:59, 08-28 16:04 | **yes, all four** |
| exness XAU | 08-25 02:09, 08-25 23:59 | no — **both predate deployment** |
| exness XAU | 08-28 14:09 | **yes** |

**Every close after the durable log's deployment (worker start, 2026-08-27T14:35Z)
is present, with exit timestamps matching exactly; every ledger trade absent from
the log predates it.** The discrepancy is entirely the different window start —
suspected at first sight, and now verified rather than assumed.

## Part 3 — two smaller production facts

**`binance.perpetual_future.xau.usdt` has un-frozen.** Round 207 recorded the key
as absent and Round 206 confirmed that route's ledger stuck at 7 trades since
2025-12-26. It now holds 3 entries — one close at 2026-08-28T16:19Z — and its
ledger reads 8 trades. The route is trading again.

**The Round 80 / Round 83 levers are confirmed live from real closed trades**, not
from configuration: observed `take_profit` +0.09407 against
`5.0 × PORTFOLIO_TAKE_VALUE(0.02) − 0.007 = +0.093`, and observed `stop_loss`
−0.05596 against `−5.0 × PORTFOLIO_STOP_VALUE(0.01) − 0.007 = −0.057`, at notional
5.0 net of ~14 bps round-trip friction. The deployed protective values behave as
Round 83 set them.

## Part 4 — a stale checkpoint that is not a defect

`exness.cfd.xau.usd.5m`'s checkpoint last advanced at **2026-08-29T00:00:04Z,
12.7 hours ago**, while the other five advanced within the last 10 minutes and its
container reports `Up 46 hours (healthy)`. That is the shape of the
"healthy container with no progress" failure the production-deployment rule warns
about.

It is **not** that failure here. Today is **Saturday**, and `exness.cfd.xau.usd` is
a *gold CFD*, which does not trade weekends — so no new candles arrive and the
checkpoint correctly has nothing to advance. Two pieces of evidence rather than the
assumption: `exness.cfd.btc.usd` is also an Exness CFD and *did* advance at
12:30Z, because crypto CFDs trade continuously; and over the identical five-year
span XAU holds 8011 4h bars against BTC's 10977, a ratio of 0.73 ≈ 5/7 — the
weekend closure, visible in the data itself.

This is recorded so a future round does not re-raise it as an incident.

## What is proven, and what is not

Proven:

- Six routes' durable log cardinalities (12/3/9/3/9/3 entries), index equal to
  payload on every route, three entries per distinct `exit_at`.
- The Target 3 table above, including the Poisson intervals and the
  3.3-day / 5.8-day resolution estimates conditional on the current point rates.
- Durable log completeness on the two routes checked, by exit-timestamp match
  against retained ledger records.
- `binance.perpetual_future.xau.usdt` traded once on 2026-08-28 after being frozen
  since 2025-12-26.
- Deployed stop/take behaviour matches `PORTFOLIO_STOP_VALUE=0.01` /
  `PORTFOLIO_TAKE_VALUE=0.02` in real closed trades.

Not proven, and deliberately not claimed:

- **Any Target 3 verdict.** Every route and both pools are undetermined at 95%.
  The BTC/XAU split is a point-estimate pattern across two readings, not a result.
- That the durable log is complete on the other four routes. **Two of six were
  checked** — the two where retained ledger records made the comparison possible
  without a deeper dig.
- That `binance XAU` has resumed normal operation. One close is one close; the
  route may go quiet again.
- Anything about PnL. The deployed `fixed-pct` ledgers remain net negative on every
  route except `binance XAU` (+0.047 over 8 trades), and none of these samples can
  support a profitability statement.
- That the 46.1-hour window is representative. It contains one weekend boundary,
  which suppresses the XAU CFD routes specifically — a bias against XAU that the
  seven-day re-read would carry too, and that the point estimates above do **not**
  correct for.
