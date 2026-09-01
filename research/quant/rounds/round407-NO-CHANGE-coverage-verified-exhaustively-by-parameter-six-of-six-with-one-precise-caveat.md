# SCOPE NARROWED (Round 408)

This file's coverage claim describes `production_candidates` in `crates/finance-research` -
which is a **research-side mirror** called only from the research CLI (`main.rs:617`, `:678`).
**No live code calls it.** The live binary is `finance-api`, whose strategy set comes from
`deployment_rules::configured_alpha_strategies`.

**The two have drifted.** On `binance BTC` and `exness BTC` the live configuration carries a
**seventh** strategy the mirror does not: `mtf_stochastic_4h_1d_sma50` (k14, d3, 30/70, trend
50, base **4h** / higher **1d**). Confirmed in live trade payloads, whose
`contributing_strategies` list **six** names on both BTC routes against the mirror's five.

So "six of six, coverage complete" is true **of the mirror**. Production runs **seven**
distinct configurations, and the seventh has never been scored at its own intervals - every
MTF run in this arc used `5m`/`4h`. `exness XAU` is unaffected: both definitions give three.
See
`round408-DATA-ISSUE-the-research-mirror-has-drifted-from-the-live-configuration-production-runs-a-seventh-strategy-nobody-has-scored.md`.

---

# Round 407 — NO-CHANGE: coverage verified **exhaustively, by parameter** — six of six — closing the gap I named in round 406. One precise caveat.

Classification: **NO-CHANGE** — a verification that came back clean; no new
finding. **Zero containers**, pure code read.

## Why this round exists

Round 406 corrected two of my own rounds and then admitted its own limit:

> *"NOT claimed the sweep covers production on all six routes — I have not
> enumerated whether any route carries a candidate I have not looked for, which
> is exactly the failure mode of this round."*

Naming a gap and leaving it open is how rounds 394 and 395 went wrong. This
closes it the way it should have been closed the first time: **enumerate every
branch, then match by constructor arguments.**

## The complete enumeration

`production_candidates` contains **two unconditional** entries and **three
mutually exclusive branches**:

- always: `candle_momentum` (0.001), `rsi_mean_reversion` (14, 30, 70)
- `binance` perp `BTC/USDT` → `btc_trend_filtered_candidates(...)`
- `exness` cfd/forex `XAU/USD` → `mtf_stochastic` (9, 3, 35, 65, trend 5)
- `exness` cfd/forex `BTC/USD` → `btc_trend_filtered_candidates(...)`

`btc_trend_filtered_candidates` yields three: `mtf_stochastic` (9,3,35,65,t10),
`mtf_macd` (5,13,5,t10), `mtf_candle_momentum` (0.001,t10). The two BTC branches
pass **different id strings but identical parameters**, so they are the same
three configs.

`bybit BTC`, `bybit XAUT` and `binance XAU` match **no branch** and receive only
the two unconditional entries.

**Exactly six distinct configurations across the fleet. No branch missed.**

## Matched by constructor arguments, not by name

| production | params | sweep entry | sweep constructor |
|---|---|---|---|
| `candle_momentum` | 0.001 | `candle_momentum_10bps` | `CandleMomentumStrategy::new(0.001)` |
| `rsi_mean_reversion` | 14/30/70 | `rsi_mean_reversion_14_30_70` | `RsiMeanReversionStrategy::new(14, 30.0, 70.0)` |
| `mtf_stochastic_5m_4h_sma5` | 9,3,35,65,t5 | `mtf_stochastic_9_3_35_65_sma5_trend_filtered` | `StochasticStrategy::new(9,3,35.0,65.0)` + `5` |
| `mtf_stochastic_5m_4h_sma10` | 9,3,35,65,t10 | `mtf_stochastic_9_3_35_65_sma10_trend_filtered` | `StochasticStrategy::new(9,3,35.0,65.0)` + `10` |
| `mtf_macd_5m_4h_sma10` | 5,13,5,t10 | `mtf_macd_5_13_5_sma10_trend_filtered` | `MacdTrendStrategy::new(5,13,5)` + `10` |
| `mtf_candle_momentum_5m_4h_sma10` | 0.001,t10 | `mtf_candle_momentum_10bps_sma10_trend_filtered` | `CandleMomentumStrategy::new(0.001)` + `10` |

**Six of six.** Coverage is complete and now verified the correct way.

## The caveat that only appears when you read the constructors

The sweep's MTF entries take `base_interval` and `higher_interval` from **CLI
arguments**, not from the entry. They match production's `5m`/`4h` **only when
the run passes `--interval 5m --higher-timeframe-interval 4h`** — which the
rounds 395/396 runs did, so those results stand.

A run with a different higher-timeframe interval would produce entries with the
same names and the same core parameters that **do not correspond to anything
production runs**. The name would look right and the result would be about a
different strategy. That is the same failure mode as before, one level down.

## What is proven, and what is not

Proven:

- The complete branch structure of `production_candidates`; three branches,
  mutually exclusive, two unconditional entries.
- Six distinct production configurations fleet-wide.
- Each has an exact sweep counterpart, verified by constructor arguments.
- The MTF correspondence depends on the run's `--higher-timeframe-interval`.

Not proven, and deliberately not claimed:

- That the deployed binary matches this source. I read the repository at the
  current commit; whether production runs that revision is a deployment question
  I have not checked, and r402 already showed a stale-build trap in my own data.
- That the sweep entries and production strategies behave identically at
  runtime. Identical constructor arguments to the same types is strong, but I
  compared code, not outputs.
- Anything new about performance. Round 406's table stands: all six lose.

## Named next step

None. Coverage is closed, and the standing constraint is unchanged: what remains
is blocked on the release decision, on a definition for Target 2, or on forward
time.
