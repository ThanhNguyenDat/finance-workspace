# Round 269 — Round 268 verified at the production 5m interval; and the route with the tightest entry budget is the only one observed to pass its gate

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (exactly the
2-container budget) plus read-only sampling.

## Part 1 — Round 268's conclusion holds at 5m

Round 268 measured at 4h and flagged its own limit: *"Not claimed the 4h result
carries to the production 5m interval. The ratio ought to, but that was not
measured."* Same comparison, same 260-day window, at **5m** — the interval
production actually decides on:

| | binance XAU/USDT | exness XAU/USD |
|---|---|---|
| candles / 260 d | 74 878 (288/day) | 50 063 (192.6/day) |
| median trades per mechanism | **3255.5** | 1901.5 |
| p25 / p75 | 1714 / 8200 | 457 / 5073 |
| **per candle** | **0.04348** | 0.03798 |
| **per week** | **87.65** | 51.19 |

| ratio binance / exness | per candle | per week |
|---|---|---|
| **5m (this round)** | **1.14x** | **1.71x** |
| 4h (Round 268) | 1.33x | 1.83x |

**Same direction, similar magnitude.** Round 268's conclusion — that `binance XAU`'s
data supports *more* candidate trading than the healthy route's, so the shortfall is
policy-side rather than data-side — **carries to the production interval.** The
per-candle ratio is smaller at 5m (1.14x against 1.33x); the per-week ratio is nearly
unchanged.

One structural difference worth recording: at 5m `binance XAU`'s busiest mechanisms
are `taker_imbalance`/`taker_imbalance_fade`, which do not appear in `exness XAU`'s
top five — taker-volume fields exist for the perpetual future and not for the CFD.
That affects the tails, not the median used above.

## Part 2 — the sampling log, and a counter-example I did not expect

Fourth sample appended; `raw/researcher/signal-state-samples.csv` now holds **16
observations** across rounds 265, 266, 267, 269, spanning **14:35Z → 15:55Z (~80
minutes)**.

**`trend_score` is unchanged to four decimals on all four routes across all four
samples** — +0.1759, −0.3476, −0.5023, −0.0693 throughout 80 minutes. Round 267's
structural reading (TREND = 1h/2h/4h/12h/1d, with 84-89% of the budget in 4h/12h/1d)
continues to hold, now over four times the original window.

And then:

| route | gate_passed | reason | entry | trend |
|---|---|---|---|---|
| **binance XAU** | **true** | **`multi_timeframe_gate_passed`** | **−0.1079** | −0.3476 |
| binance BTC | false | `entry_trend_conflict` | −0.1278 | +0.1759 |
| bybit XAUT | false | `entry_trend_conflict` | +0.1038 | −0.5023 |
| exness BTC | false | `trend_score_below_threshold` | −0.1839 | −0.0693 |

**`binance XAU` — the route with 8 lifetime trades and the tightest entry budget —
is the only route observed to pass a gate in the entire 16-sample log.** Its
`entry_score` reached −0.1079, i.e. **75.1% of its 0.1437 entry budget**, clearing
the 0.1 threshold Round 267 computed requires 69.6%; and its sign matched its pinned
negative trend, so all three gates cleared at once.

This is a **concrete counter-example** to the direction Rounds 263 and 267 were
leaning. A tight entry budget makes passing harder; it demonstrably does not make it
impossible, and in this small sample the constrained route passed while the three
others did not.

## What is proven, and what is not

Proven:

- The 5m comparison above, on a matched 260-day window: `binance XAU` 1.14x per
  candle and 1.71x per week against `exness XAU`, same direction as 4h.
- `trend_score` unchanged to four decimals on four routes across four samples over
  ~80 minutes.
- `binance XAU` recorded `gate_passed=true` with entry −0.1079 and trend −0.3476;
  it is the only pass in 16 samples.

Not proven, and deliberately not claimed:

- **That `binance XAU` passes its gate more often than the others.** One pass in
  four samples against zero in four is not a rate comparison — it is a
  counter-example to "structurally blocked" and nothing more. Round 261 and Round
  264 both established the live differences are inside noise.
- That the tight entry budget is irrelevant. It is shown to be surmountable, not
  harmless; whether it depresses the pass rate over many samples is exactly what the
  log is for.
- That `trend_score` never moves. Eighty minutes, four routes, and Round 267 shows it
  cannot move faster than an hourly close by configuration.
- Which of seed or weights is the cause. Unchanged since Round 263.
- Anything about PnL, Target 3, the seed spans, or the stalled backfill.
