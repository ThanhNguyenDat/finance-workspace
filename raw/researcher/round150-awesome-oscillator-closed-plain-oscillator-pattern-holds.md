# Round 150 — Awesome Oscillator: closed, falsified on 5-year honest BTC/binance backtest

## Context

Round 3 requires exploring new mechanisms via web research. Every plain
crossover/reversion oscillator already tried in this program (Stochastic,
CCI, MFI, OBV, Elder Ray, Vortex — see closed-directions table in
`raw/researcher/SUMMARY-priority-backlog.md`) fails without a trend filter
at 5m. This round tested whether a structurally different momentum
mechanism — the Awesome Oscillator (Bill Williams) — breaks that pattern.

## Mechanism

Awesome Oscillator (AO) is genuinely distinct from every crossover already
tried: it smooths the candle **midpoint** `(high+low)/2`, not the close
price, with two plain (non-exponential) SMAs at the standard textbook
periods 5 and 34 — a much wider slow window than any EMA pair tested so far
(max 26). Signal fires on the AO sign crossing zero. Implemented as
`AwesomeOscillatorStrategy` in `crates/finance-research/src/strategies.rs`
(reuses the existing `finance_strategy::indicators::sma` — no new indicator
module needed), registered as `awesome_oscillator_5_34`. Unit tests cover
window-warmup gating and the zero-line crossover firing rule; `cargo fmt
--check` clean, full workspace `cargo test --workspace --exclude
finance-redis` green (32/32 suites).

## Method

`finance-research`, Docker `--cpus=2`, `--broker binance --market-type
perpetual_future --base-asset BTC --quote-asset USDT --interval 5m --days
1825 --json` (5-year window, 525,599 candles: train 315,359 / validation
105,120 / holdout 105,120).

## Result

| split | trades | profit factor | win rate | realized PnL |
|---|---|---|---|---|
| train | 14,912 | 0.538 | 19.7% | -$107.68 |
| validation | 4,683 | 0.514 | 21.7% | -$32.35 |
| holdout | 4,840 | 0.494 | 20.3% | -$33.65 |

## Verdict: CLOSED, falsified

PF stays in a tight 0.49-0.54 band across all three splits — no "weak
train, strong later" false-positive shape, a consistently losing mechanism.
Using the midpoint instead of close, and a much wider slow SMA window, did
not break the established pattern: **every plain oscillator without a
trend/regime filter has failed in this program regardless of the specific
smoothing/reaction-speed mechanism.** This is now the 7th such mechanism
closed for the identical reason (Stochastic, CCI, MFI, OBV, Elder Ray,
Vortex, now AO) — strong convergent evidence that the ceiling is structural
(5m BTC/binance market microstructure), not a property of any one
indicator's math. Future rounds exploring a *new plain oscillator* should
weigh this prior heavily; the more promising unexplored direction per the
backlog is filter/regime combinations layered on an existing base signal,
or genuinely different timeframes/mechanisms (order flow, session
structure) rather than another zero-line-crossover oscillator.

Code stays in the working tree (unpromoted, per this program's convention).
No promotion, no further investigation planned for AO specifically.

## XAU cross-check

Per the loop's stated priority (XAU before BTC), a same-window XAU/binance
run followed. XAU/binance's live history is much shorter than BTC's (73,863
total candles vs 525,599 — train 44,318 / validation 14,773 / holdout
14,772, ~51 days holdout), consistent with XAU/binance starting live later
(see `[[project_active_instruments]]`-equivalent note in the backlog doc).

| split | trades | profit factor | win rate | realized PnL |
|---|---|---|---|---|
| train | 2,181 | 0.343 | 13.9% | -$16.08 |
| validation | 658 | 0.367 | 14.7% | -$4.22 |
| holdout | 635 | 0.300 | 15.0% | -$4.36 |

Same verdict, even weaker than BTC (PF 0.30-0.37 vs BTC's 0.49-0.54) — full
cross-instrument agreement, no divergence between BTC and XAU for this
mechanism. Strengthens the structural-ceiling conclusion above: this isn't
an instrument-specific artifact.
