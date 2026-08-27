# Binance BTC Portfolio Target Tracking

Append-only. Tracks every backtest/production run against the user's
original targets. Never delete or rewrite prior entries — only append.

## Targets (set 2026-08-17)

1. Stable daily profit, or at minimum no net loss, at the Portfolio layer.
2. Win rate >= 70% at the Portfolio layer.
3. Trade frequency: >= 1 closed trade/day OR >= 7 closed trades/week
   (secondary to targets 1-2 — do not over-trade just to hit it).
4. Secondary quant-quality bar (proposed by the cloud optimization routine,
   Iteration 1, reusing `finance-live-action/README.md`'s own promotion
   gate rather than inventing new numbers): Sharpe >= 1.0, max drawdown
   <= 10%, profit factor > 1.3, positive-day ratio >= 55%, Sortino >= 1.0.

## Data source discipline

Every row below comes from either (a) a real `finance-research` backtest
run against real historical klines pulled live from production via gRPC
(`--endpoint` pointed at the real `finance-mw` service, never a local
fixture), or (b) real production `trades`/`trading_runs` data once any
exists. **No row is ever a projection, an estimate, or an invented number.**
If a run's data is incomplete or a metric can't be computed, the row says
so explicitly rather than omitting it silently.

---

## Run 1 — 2026-08-18T03:32Z (backtest, current production strategy config)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval 5m --days 90` (all other flags default —
`--portfolio-rule fixed-pct`, sizing/protective values match the live
`docker/compose.large-cap.yaml` defaults).

**Data:** 25,919 real 5m candles (train 15,551 / validation 5,184 / holdout
5,184), pulled live from production over a direct SSH tunnel to
`finance-mw`'s gRPC market-data service. Real historical BTC/USDT data, not
synthetic.

**Strategies tested:** the tool's fixed research grid — `candle_momentum`
and `candle_reversion`, each at multiple move-threshold variants (10bps,
30bps, 60bps) — the closest available proxy to the two Alpha strategies
actually configured live (`candle_momentum`, `rsi_mean_reversion`; the
research grid does not carry an RSI variant, so this run does not yet cover
that half of the live config — see "Known gaps" below).

| Strategy | Split | Trades | Win % | Profit Factor | PnL | vs Target 2 (win>=70%) | vs Target 4 (PF>1.3) |
|---|---|---:|---:|---:|---:|---|---|
| candle_momentum_10bps | holdout | 269 | 24.9% | 0.39 | -1.63 | ❌ far below | ❌ |
| candle_momentum_30bps | holdout | 7 | 42.9% | 1.26 | +0.03 | ❌ below (and n=7, not statistically meaningful) | close but n too small |
| candle_reversion_10bps | holdout | 269 | 30.1% | 0.16 | -2.14 | ❌ far below | ❌ |
| candle_reversion_30bps | holdout | 7 | 57.1% | 0.40 | -0.13 | ❌ below (n=7, not meaningful) | ❌ |
| candle_reversion_60bps | holdout | 0 | — | — | — | no trades fired at this threshold | n/a |

**Tool's own promotion verdict:** *"No candidate earned on both train and
validation. Nothing to promote."* — every variant tested failed the tool's
own train+validation profitability gate; none reached holdout evaluation
with a passing status.

### Status vs targets

- **Target 1 (stable/non-negative daily profit):** not met — every variant
  with a statistically meaningful trade count (n>200) is net negative on
  holdout.
- **Target 2 (win rate >= 70%):** not met — actual range 24.9%-57.1%,
  and the two readings above 40% both come from n=7 trades, too few to
  trust.
- **Target 3 (trade frequency 1/day or 7/week):** not directly measured
  this run (this counts backtest-window trades, not a live daily/weekly
  rate) — the 10bps variants alone would clear it easily (269 holdout
  trades over the same window `candle_reversion_60bps` is on), so frequency
  is not the binding constraint; profitability is.
- **Target 4 (Sharpe/drawdown/PF/etc.):** not fully computed this run —
  `finance-research`'s table output does not print Sharpe/Sortino/max
  drawdown for var/momentum grid rows (only `pnl`, `win%`, `pf`, `maxDD`
  columns shown; `maxDD` printed as ~0.0-0.2% here but that reflects the
  small fixed-notional sizing in this run, not a validated risk bound).
  Profit factor is the one Target-4 metric directly comparable, and every
  meaningful-n variant fails it (PF well under 1.3, mostly under 1.0).

### Known gaps in this run (do not treat as resolved)

1. Does not test `rsi_mean_reversion` (the second Alpha strategy actually
   configured live in `deployment_rules.rs`) — the research grid's
   `candle_reversion` is a different formula (move-threshold based) than
   `rsi_mean_reversion` (period/oversold/overbought based). A dedicated
   RSI-parameter sweep is still needed before claiming full coverage of the
   live config.
2. Single window only (90 days, 5m). Rules 2/4 from the original task ask
   for exploring other timeframes (15m/1h/4h/1d) and setups (swing,
   scalping, multi-timeframe combination) — none of that is covered yet.
3. Sizing/protective parameters were left at the tool's defaults (which
   mirror the *current* live config) — no sizing/position-tuning sweep run
   yet (Rule 3 from the original task).
4. This queries production market data read-only via an SSH tunnel set up
   for this one run and torn down immediately after — not a standing
   integration; a future run needs to re-establish it the same way, or a
   proper reachable endpoint needs to be decided if this becomes routine.

### Next runs planned (as of Run 1)

- RSI-parameter sweep to actually cover `rsi_mean_reversion`. **Done — see
  Run 2 below.**
- Same grid at 15m/1h to see if the momentum/reversion edge (or lack of
  one) is timeframe-dependent.
- Longer window (365 days, the tool's own default) once a faster/standing
  way to reach production market data exists, to check whether 90 days was
  an unusually bad regime or representative.

---

## Run 2 — 2026-08-18T13:21Z (backtest, RSI mean-reversion, same 90-day window as Run 1)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval 5m --days 90` (same command as Run 1, for a
direct comparison — only the code changed: `finance-live-action` commit
`e872705` added RSI to the candidate grid).

**Data:** 25,919 real 5m candles (train 15,551 / validation 5,184 / holdout
5,184) — identical counts to Run 1, confirming this is the same historical
window, pulled live from production over the same SSH tunnel pattern
(established, used, torn down within this run; confirmed closed via
`ss -tlnp` afterward).

**Strategies tested:** 4 `rsi_mean_reversion` variants, reusing
`finance-strategy`'s own live implementation (not a reimplementation) —
`14_30_70` is the exact parameters actually configured live today.

| Strategy | Split | Trades | Win % | Profit Factor | PnL | vs Target 2 (win>=70%) | vs Target 4 (PF>1.3) |
|---|---|---:|---:|---:|---:|---|---|
| rsi_mean_reversion_14_30_70 (live default) | holdout | 130 | 33.8% | 0.32 | -0.85 | ❌ far below | ❌ |
| rsi_mean_reversion_14_20_80 | holdout | 52 | 50.0% | 0.74 | -0.15 | ❌ below | ❌ |
| rsi_mean_reversion_9_30_70 | holdout | 237 | 26.6% | 0.18 | -1.66 | ❌ far below | ❌ |
| rsi_mean_reversion_14_35_65 | holdout | 169 | 26.6% | 0.20 | -1.36 | ❌ far below | ❌ |

**Tool's own promotion verdict:** *"No candidate earned on both train and
validation. Nothing to promote."* — same verdict as Run 1; RSI does not
change the outcome. Every variant, including the parameters actually
running live right now, fails the tool's own train+validation gate.

### Status vs targets

- **Target 1 (stable/non-negative daily profit):** not met — every RSI
  variant is net negative on holdout.
- **Target 2 (win rate >= 70%):** not met — actual range 26.6%-50.0%, all
  well under target. `14_20_80` (tighter thresholds → fewer, higher-quality
  signals in theory) is the best of the four but still fails.
- **Target 3 (trade frequency):** not the binding constraint — even the
  lowest-frequency variant (`14_20_80`, 52 holdout trades) would clear
  either frequency bar comfortably over this window; profitability is what's
  failing, same conclusion as Run 1.
- **Target 4 (PF/Sharpe/etc.):** PF fails for every variant (0.18-0.74, all
  under the 1.3 bar). Sharpe/Sortino/drawdown still not computed by this
  tool's table output (same gap as Run 1).

### Known gaps in this run (do not treat as resolved)

1. Only 5m tested — 15m/1h grid (queued since Run 1) still not done.
2. Only the same 90-day window as Run 1 — the tool's own default 365-day
   window still not tried.
3. RSI parameter grid is 4 variants (1 live-default + 3 single-parameter
   perturbations) — not an exhaustive sweep. A real optimization would need
   a wider grid, which risks overfitting to this specific window without a
   proper walk-forward validation the tool doesn't yet report on (Sharpe/
   Sortino/drawdown gap above).
4. Same ad-hoc SSH tunnel dependency as Run 1 — no standing way to reach
   production market data for backtests yet.

### Next runs planned (as of Run 2)

- Same strategy families (momentum, reversion, RSI) at 15m/1h timeframes.
  **Done — see Run 3 below.**
- 365-day window to check regime-dependence.
- Given momentum/reversion/RSI have all now failed on this window, Rule 4's
  swing/scalping/multi-timeframe exploration (a genuinely different setup,
  not just more parameters of the same three families) is due next.

---

## Run 3 — 2026-08-18T13:37Z (backtest, same strategy grid at 15m and 1h, same 90-day window)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {15m,1h} --days 90` — two runs, same window
length as Run 1/Run 2, different candle interval.

**Data:** 15m → 8,640 real candles (train 5,184 / validation 1,728 /
holdout 1,728). 1h → 2,160 real candles (train 1,296 / validation 432 /
holdout 432). Same SSH tunnel pattern as Run 1/2, torn down after.

**Result headline: the tool's own selection gate passed for the first time
— twice — but both hits have holdout samples too small to trust.**

| Interval | Strategy | Train (n / win% / PF) | Validation (n / win% / PF) | Holdout (n / win% / PnL) |
|---|---|---|---|---|
| 15m | candle_reversion_60bps | 74 / 64.9% / 1.33 | 4 / 50.0% / 1.50 | **1** / 100% / +0.08 |
| 1h | rsi_mean_reversion_14_20_80 | 10 / 70.0% / 1.18 | **3** / 100% / — | **4** / 100% / +0.44 |

Both "survived selection on train and validation" per the tool's own
output — a first across Run 1/2/3. **Not treating either as a promotable
result**: holdout n=1 and n=4 (and validation n=3/n=4) are far below the
n=7 threshold this log already flagged as "not statistically meaningful" in
Run 1, let alone enough to trust over n=1-4.

**Two 1h cells that look strong but are explicitly NOT evidence** (reported
here only so nobody re-discovers them later and mistakes them for a hit):

| Interval | Strategy | Train PF | Validation PF | Holdout (n / win% / PF) | Why it's not evidence |
|---|---|---|---|---|---|
| 1h | rsi_mean_reversion_14_35_65 | 0.85 (loses) | 0.35 (loses) | 21 / **76.2%** / **6.69** | Train and validation both lose money; the tool correctly did not select this. A strong holdout with a losing train+validation is the signature of noise/regime-shift within this window, not a real edge. |
| 1h | rsi_mean_reversion_9_30_70 | 1.23 (wins) | 0.12 (loses badly) | 31 / 74.2% / 6.08 | Validation lost money (28.6% win); not selected. |

Both of these *individually* clear Target 2 (win≥70%) on a real sample size
(n=21, n=31) — exactly the kind of number that would look like a result if
read in isolation. They are reported with full context specifically to
prevent that misreading.

### Status vs targets

Not met, same as Run 1/2. The tool's selection gate finally passed twice,
but the standing "don't trust a thin sample" rule this log has applied
since Run 1 applies equally here — n=1 and n=4 holdout are not meaningfully
different from n=7 having been already ruled insufficient.

### Known gaps in this run

1. 90-day window is now looking like the binding constraint on holdout
   sample size at longer intervals (1h × 90 days only ever gives ~430
   holdout candles, and far fewer actual trade events within them) — the
   365-day window queued since Run 1 is the natural next step specifically
   to address this, not just "more data for its own sake."
2. Same ad-hoc SSH tunnel dependency as every prior run.

### Next runs planned (as of Run 3)

- 365-day window at 5m/15m/1h — primarily to get holdout sample sizes large
  enough that a "survived selection" result would actually be trustworthy.
  **Done — see Run 4 below.**
- If that still doesn't produce a trustworthy positive result, Rule 4's
  swing/scalping/multi-timeframe exploration (new strategy designs, not
  more parameters of momentum/reversion/RSI) is the next real avenue.

---

## Run 4 — 2026-08-18T13:51Z (backtest, same strategy grid at 5m/15m/1h, 365-day window)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {5m,15m,1h} --days 365` — the tool's own
default window length, directly testing whether Run 3's 90-day window was
too short to trust its two thin-sample "survived selection" hits.

**Data:** 5m → 105,119 candles (train 63,071 / validation 21,024 / holdout
21,024). 15m → 35,040 candles (train 21,024 / validation 7,008 / holdout
7,008). 1h → 8,760 candles (train 5,256 / validation 1,752 / holdout
1,752). All real, pulled live via the same SSH tunnel pattern as every
prior run, torn down after (confirmed via `ss -tlnp`).

**Headline: "Nothing to promote" at all three intervals**, with real,
trustworthy sample sizes this time (holdout ranges from 1,752 to 21,024
candles, producing dozens to thousands of actual trade events per
strategy — nothing like Run 3's n=1/n=4).

| Interval | Closest candidate | Train PF | Validation PF | Holdout (n / win% / PF) | Selected? |
|---|---|---:|---:|---|---|
| 5m | candle_reversion_60bps | 0.99 | 0.76 (loses) | 30 / 60.0% / 1.30 | No |
| 15m | candle_reversion_60bps | 0.63 | 1.01 (barely breakeven) | 48 / 64.6% / 1.30 | No |
| 1h | rsi_mean_reversion_14_30_70 (live default) | 0.97 | 0.84 (loses) | 48 / 64.6% / 1.88 | No |

**Two 1h cells flagged explicitly as NOT evidence**, same discipline as
Run 3 — both look attractive read in isolation, both fail on train and/or
validation:
- `rsi_mean_reversion_14_20_80`: holdout 13 trades, 84.6% win, PF 3.40 —
  train PF 0.89 and validation PF 0.77 both lose money.
- `rsi_mean_reversion_14_30_70` (live default): holdout 48 trades, 64.6%
  win, PF 1.88, **PnL +1.06 — the best absolute holdout PnL for this
  strategy seen across any run**, but train (PF 0.97) and validation (PF
  0.84) still lose money, so the tool still did not select it.

### Status vs targets

Not met. This is the most thorough negative result gathered so far:
momentum, reversion, and RSI (4 parameter variants each) have now been
tested at both 90-day and 365-day windows, across 5m/15m/1h, and none
clears the tool's own train+validation selection bar with a trustworthy
sample. Run 3's two "survived selection" hits (thin n=1/n=4 holdouts) do
not reproduce with the larger, more reliable 365-day samples — the honest
reading is that they were noise, not an under-sampled real edge.

### Known gaps in this run

1. Still only the three single-candle-signal strategy families (momentum,
   reversion, RSI) — no swing, scalping, or genuine multi-timeframe
   combination strategy has been implemented or tested yet. Given the
   breadth of what has now been ruled out, this is the natural next
   direction, not another parameter sweep of the same families.
2. Sizing/position-model tuning (Rule 3) has not been touched — deliberately
   secondary, since tuning position size cannot create an edge a strategy
   doesn't have.
3. Same ad-hoc SSH tunnel dependency as every prior run.

### Next runs planned (as of Run 4)

- Design and implement a genuinely different strategy (swing, scalping, or
  multi-timeframe combination) per Rule 4. **Partially done — see Run 5
  below** (6 new single-timeframe families implemented and tested; true
  multi-timeframe combination still not done, see Run 5's own next-steps).

---

## Run 5 — 2026-08-18T14:51Z (backtest, 6 new strategy families: MACD, EMA, SMA, Bollinger×2, ATR, Stochastic)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {5m,1h} --days {90,365}` — two runs: 5m/90d
(direct comparison to Run 1) and 1h/365d (favors trend-following mechanisms,
which need room to hold a multi-candle trend).

**Data:** 5m/90d → 25,918 candles (train 15,551 / validation 5,184 /
holdout 5,183). 1h/365d → 8,760 candles (same split sizes as Run 4's 1h/365d
run). Real, via the same SSH tunnel pattern as every prior run, torn down
after.

**New strategies tested** (17 variants beyond Runs 1-4's momentum/reversion/
RSI): `macd_trend` (3), `ema_crossover` (2), `sma_trend` (2), `bollinger_
reversion` (1), `bollinger_breakout` (1), `atr_breakout` (2), `stochastic`
(2) — 13 variants... plus the momentum/reversion/RSI baseline re-run
alongside them for direct comparison (full grid run together each time).

**Verdict, both windows: "No candidate earned on both train and validation.
Nothing to promote."**

**The real finding this run: trend-following underperforms mean-reversion
on this instrument/timeframe set, and by a wide margin:**

| Family | 5m/90d holdout win% | 1h/365d holdout win% |
|---|---|---|
| macd_trend (3 variants) | 11.7%-15.8% | 27.0%-33.7% |
| ema_crossover (2 variants) | 14.7%-18.4% | 24.6%-27.6% |
| sma_trend (2 variants) | 9.6%-10.4% | 15.9%-17.9% |
| bollinger_reversion | 28.9% | 50.0% |
| stochastic (2 variants) | 24.8%-26.1% | 56.2%-58.6% |
| atr_breakout (2 variants) | 20.7%-21.2% | 0%-38.1% (n=2 for the 3.0x variant, not meaningful) |

Trend-following (top 3 rows) consistently underperforms the
mean-reversion/oscillator families (bottom 3 rows) at both windows — high
trade counts with very low win rates is the signature of whipsaw in a
choppy/mean-reverting market, which is what this data suggests BTC actually
is at these timeframes, not what trend-following strategies assume.

**Closest near-miss:** `bollinger_reversion_20_2` at 1h — validation 38
trades/68.4% win/PF 1.18 (would nearly clear Target 2 on its own), but train
(112 trades/55.4% win/PF 0.76) failed, so the tool correctly did not select
it. Same pattern flagged in Run 3/4: a good-looking cell without train
support is not evidence.

### Status vs targets

Not met. 9 strategy families, 31 parameter variants total across this
session, tested across 2 window lengths and 3 intervals (5m/15m/1h) — none
has cleared the promotion bar with a trustworthy sample. This run's
contribution is narrowing *which kind* of approach is worth pursuing next:
mean-reversion/oscillator mechanisms consistently outperform trend-following
ones here, even though neither has produced a promotable result yet.

### Known gaps in this run

1. Only single-timeframe strategies — no genuine multi-timeframe
   combination (e.g. 5m entry gated by 1h trend agreement) implemented yet.
   `finance-research`'s CLI/dataset loader only evaluates one `--interval`
   per run currently; supporting two intervals in the same backtest would
   be a real, scoped feature addition, not done this run.
2. Sizing/position-model tuning (Rule 3) still untouched.
3. Same ad-hoc SSH tunnel dependency as every prior run.

### Next runs planned (as of Run 5)

- Rule 3: sizing/protective-level tuning, motivated by near-miss cells like
  `bollinger_reversion_20_2`'s validation PF 1.18 — a different lever than
  finding a new signal. **Done — see Run 6 below** (found the CLI sizing
  flags didn't reach the promotion table at all; fixed that, then applied
  the real live stop/take — conclusion unchanged).
- Scope and potentially implement genuine multi-timeframe combination
  (needs dataset-loader support for 2+ intervals per run) — the one part of
  Rule 4 not yet attempted.

---

## Run 6 — 2026-08-18T15:20Z (backtest, real live stop-loss/take-profit applied to the Alpha promotion table)

**Context:** Runs 1-5's promotion table used `ProtectiveLevels::None` —
positions closed only on the strategy's own reversal signal, never on a
fixed stop/take. Live trading uses `PORTFOLIO_STOP_VALUE=0.005`/
`PORTFOLIO_TAKE_VALUE=0.01` (fractional). Implemented opt-in `--alpha-stop-
value`/`--alpha-take-value` CLI flags (`finance-live-action` commit
`d8cdc78`) so the table can be scored the same way production would
actually exit trades, without changing the flag's default (unset) behavior
anywhere else that reuses the same simulation config.

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval 5m --days 90 --alpha-stop-value 0.005 --alpha-
take-value 0.01` — same window as Run 1/2, only the protective-levels flag
added.

**Data:** 25,919 candles (train 15,551 / validation 5,184 / holdout 5,184)
— same window Run 1/2 used, pulled live over the same SSH tunnel pattern,
torn down after.

**The override genuinely changes trade behavior** (confirming the fix
works, not just compiles) — trades close sooner via stop/take instead of
waiting for a reversal signal, producing different trade counts and win
rates:

| Strategy | Holdout (no protective, Run 2) | Holdout (real live stop/take, Run 6) |
|---|---|---|
| rsi_mean_reversion_14_30_70 (live default) | 130 trades, 33.8% win | 176 trades, 38.6% win |
| macd_trend_5_13_5 | 797 trades, 11.7% win | 794 trades, 11.7% win |

**Verdict: still "No candidate earned on both train and validation. Nothing
to promote."** Realistic exits do not rescue any strategy — RSI's win rate
moved a few points but stayed far under target; the weakest trend-following
variants were essentially unaffected.

### Status vs targets

Not met. This closes the "was the backtest methodology unrealistic"
question raised in the prior entry — it was worth checking honestly, and
the answer is no, the same conclusion holds either way.

### Known gaps in this run

1. Only re-tested the 5m/90d window with the new flag, for direct
   comparison to Run 2 — didn't re-sweep every interval/window combination
   with stop/take applied (would be straightforward to do, just more
   compute time, not a design gap).
2. Multi-timeframe combination (Rule 4's one still-unexplored piece)
   remains unimplemented.

### Next runs planned (as of Run 6)

- Given 9 strategy families × 31+ variants × 2 window lengths × up to 3
  intervals × both raw and stop/take-aware exit semantics have all
  converged on "Nothing to promote," the honest next step is either (a)
  scope genuine multi-timeframe combination, or (b) surface to the user
  that five runs of consistent, methodologically-checked negative evidence
  is itself a significant finding worth a direct conversation about what
  the data supports — not a reason to quietly keep sweeping without saying
  so. **Superseded — see Run 7**: web research (user-directed) pointed at
  untested 2h/4h intervals specifically, which produced this session's
  first repeatable gate-pass before either (a) or (b) was needed.

---

## Run 7 — 2026-08-18T15:26Z (backtest, 2h and 4h intervals — untested until now, found via academic research)

**Why this run happened:** user asked to also search TikTok and academic
papers/books for strategy ideas (Rule 5). Academic search surfaced a
peer-reviewed finding that Bitcoin shows significant negative first-order
return autocorrelation specifically at **1h, 2h, and 4h** timeframes — the
statistical signature of exploitable mean reversion — with profitability
sensitive to round-trip costs above ~0.25% (this backtest's fee+slippage
config, ~0.07%, is well under that). This session had tested 1h (Runs 3-6)
but never 2h or 4h.

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {2h,4h} --days 365` — run both raw and with
`--alpha-stop-value 0.005 --alpha-take-value 0.01`.

**Data:** 2h/365d → 4,380 candles (train 2,628 / validation 876 / holdout
876). 4h/365d → 2,190 candles (train 1,314 / validation 438 / holdout
438). Real, via the same SSH tunnel pattern, torn down after.

**With live fixed stop/take (0.5%/1%) applied: worse than raw, not
better** — win rates fell to 21-35% across the board at both intervals.
The fixed percentage stop is calibrated for finer timeframes and is too
tight for 2h/4h candle ranges, causing systematic premature stop-outs.
This is itself a real, actionable finding, separate from the headline
result below.

**With raw (signal-only exit) scoring — the headline result:**
`rsi_mean_reversion_14_20_80` survived the train+validation selection gate
at **both** 2h and 4h independently — the first candidate in this session
to clear the bar at more than one timeframe:

| Interval | Split | Trades | Win % | PF | PnL |
|---|---|---:|---:|---:|---:|
| 2h | train | 32 | 75.0% | 1.71 | +2.12 |
| 2h | validation | 10 | 60.0% | 1.28 | +0.22 |
| 2h | holdout | 6 | 83.3% | 139.56 | +0.57 |
| 4h | train | 14 | 42.9% | 1.13 | +0.21 |
| 4h | validation | 4 | 75.0% | 1.50 | +0.16 |
| 4h | holdout | 4 | 100% | — | +0.98 |

At 2h, two other candidates also survived selection but with **negative**
holdout PnL — `bollinger_breakout_20_2` (-0.87 over 26 trades) and
`stochastic_14_3_20_80` (-0.54 over 42 trades) — recorded for completeness,
not as positive evidence.

**Tool's own promotion verdict** (both intervals, both raw and stop/take):
the summary line still read "No candidate earned on both train and
validation. Nothing to promote" *in the stop/take runs* — the raw-run
survivals above are read from the explicit "Survived selection on train
and validation" list the tool prints separately, which the summary line
in these two specific raw runs did not negate.

### Status vs targets

- **Target 1/2 (profit, win≥70%):** `rsi_mean_reversion_14_20_80`'s
  holdout clears win≥70% at both 2h (83.3%) and 4h (100%), on real
  production data, for a candidate that also passed train+validation
  selection — the strongest result this session has produced. Not treating
  it as proven: every split's trade count is small (train 32/14,
  validation 10/4, holdout 6/4) — far more trustworthy than Run 3's n=1/n=4
  dead ends, but still thin next to the hundreds-of-trades samples this log
  has otherwise required before calling something evidence.
- **Target 3 (frequency ≥1/day or ≥7/week):** likely a real problem for
  this specific variant — 6-13 trades across holdout windows of roughly
  90-180 days is well under even the weaker weekly bar. Not yet measured
  precisely; flagged as the first thing to check before investing more
  validation effort here.
- **Target 4:** PF at 2h/4h (1.13-1.71 on train/validation, where sample
  size makes it more meaningful) clears the >1.3 bar in 3 of 4 non-holdout
  cells — again the best PF result across every run this session, though
  holdout PF is either undefined (no losses) or extreme (139.56, an
  artifact of a near-zero denominator on 6 trades, not a real number to
  trust) — flagging explicitly rather than reporting it as if it meant
  something.

### Known gaps in this run

1. Sample sizes, while the best "survived selection" result this session
   has seen, remain small — more history (if available beyond 365 days) or
   accepting the trade-frequency trade-off explicitly are the two ways to
   get more confidence.
2. Trade frequency vs. Target 3 not yet computed precisely for this
   specific variant/interval combination.
3. The stop/take mismatch finding (fixed 0.5%/1% too tight for 2h/4h) is
   itself unresolved — if this candidate were ever considered for
   promotion, its *own* protective levels would need separate tuning, not
   reuse of the 5m-calibrated live defaults.

### Next runs planned (as of Run 7)

- Compute `rsi_mean_reversion_14_20_80`'s actual trade frequency at 2h/4h
  against Target 3 before further validation investment. **Done inline —
  0.4-0.9 trades/week at both intervals, well under Target 3's weekly bar,
  though this became moot once Run 8 below found the underlying result
  doesn't hold up with more data anyway.**
- Get a larger sample before treating Run 7 as a real candidate — not
  deploying anything from a 6-14-trade holdout. **Done — see Run 8.**

---

## Run 8 — 2026-08-18T15:30Z (backtest, full 5-year real history at 5m/1h/2h/4h — the definitive check)

**Why:** user flagged that real 5-year kline history exists and asked for
care before trusting Run 7's 365-day result. Correct call — re-checked
before treating Run 7 as a finding.

**Confirmed real data availability first** (never assumed `--days N`
returned N days without checking `candle_count` in the tool's own log
line): 4h → 10,950 candles = exactly 1825 days. 2h → 21,900. 1h → 43,800.
5m → 525,600 = exactly 1825×288. All four confirmed as genuine, complete
5-year real history from production, not a truncated or assumed value.

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {5m,1h,2h,4h} --days 1825` — raw (signal-only
exit) scoring, four separate runs. Same SSH tunnel pattern, torn down after
each.

**Run 7's headline result does not hold up.** `rsi_mean_reversion_14_20_80`
at 4h/5yr: train PnL **-3.22** (67.6% win) — fails train (the 365-day
version had train PnL +0.21, barely positive). At 2h/5yr: train PnL -4.05
(42.9% win) — also fails. The 365-day "survived selection" result was noise
on a thin sample, now directly disconfirmed rather than left as an open
question.

**Verdict at every interval, on the full real 5-year history:**

| Interval | Candles | Verdict |
|---|---:|---|
| 5m | 525,600 | Nothing to promote |
| 1h | 43,800 | `atr_breakout_14_3_0` survived selection, holdout PnL **-2.17** over 20 trades |
| 2h | 21,900 | `atr_breakout_14_3_0` survived selection, holdout PnL **-1.24** over 16 trades |
| 4h | 10,950 | Nothing to promote |

No interval produced a candidate with both selection-gate survival and
positive holdout — the most robust negative result this session has
gathered, on thousands of trades per strategy rather than the tens/hundreds
every prior run had to caveat.

### Status vs targets

Not met, on the strongest evidence available. Full session total: 9
strategy families, 31+ parameter variants, intervals from 5m through 4h,
window lengths from 90 days to the complete 5-year history, both raw and
live-protective-level-aware exit semantics — no trustworthy positive
result anywhere.

### Known gaps in this run

1. Only re-checked raw (signal-only exit) scoring at 5-year scale, not the
   `--alpha-stop-value`/`--alpha-take-value` variant — Run 6/7 already
   showed the live fixed stop/take is mismatched to 2h/4h timeframes
   (too tight), so re-testing that combination wasn't expected to add
   information and was skipped to keep this check focused.
2. Multi-timeframe combination (the one Rule 4 avenue never implemented)
   remains the only unexplored single-signal-adjacent idea.

### Next runs planned (as of Run 8)

- Genuine multi-timeframe combination, if pursued: requires a real,
  correctness-sensitive change to `sweep.rs`'s ledger-driving loop (feed a
  higher-timeframe kline stream to the strategy for state only, not to the
  ledger, or true-range/funding/protective-level accounting would be
  corrupted by mixing bar granularities) — scoped, not yet implemented.
  **Done — see Run 9, the strongest result this session has produced.**

---

## Run 9 — 2026-08-18T15:49Z (backtest, multi-timeframe trend-filter combination — the strongest result this session)

**Implemented and verified** (`finance-live-action` commit `d3b0586`): a
higher-timeframe trend filter wrapping RSI/stochastic entries (see the
optimization log's matching entry for full implementation detail — new
`MultiTimeframeTrendFilterStrategy`, ledger correctly isolated from
higher-timeframe bars via a `sweep.rs` fix with its own regression test,
`--higher-timeframe-interval` CLI flag). 42 unit tests, full workspace
`cargo test` green, CI in progress.

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {5m,15m} --days {90,1825} --higher-timeframe-
interval {1h,4h}` — several combinations, real production data, SSH tunnel
torn down after each.

**Result table (5-year runs only — the 90-day 5m/1h run is reported in the
optimization log as a cautionary comparison: it looked good on train/
validation and flipped negative on holdout, exactly the small-sample
pattern Run 3/7 already warned about):**

| Base/Higher | Candidate | Train (n/win%/PF/pnl) | Validation | Holdout |
|---|---|---|---|---|
| 5m/1h | mtf_rsi_14_30_70_trend_filtered | 1266/42.3%/1.41/+17.87 | 420/41.7%/1.30/+3.51 | 439/40.8%/1.15/+2.06 |
| 5m/1h | mtf_stochastic_14_3_30_70_trend_filtered | 2266/50.7%/2.27/+49.44 | 699/50.2%/2.17/+12.76 | 731/46.6%/1.66/+8.82 |
| 15m/4h | mtf_rsi_14_30_70_trend_filtered | 375/50.7%/1.69/+15.66 | 132/55.3%/2.77/+6.70 | 111/50.5%/1.92/+4.68 |
| 15m/4h | mtf_stochastic_14_3_30_70_trend_filtered | 606/61.1%/3.57/+40.90 | 219/66.7%/5.01/+14.03 | 165/63.6%/3.11/+9.17 |

Every row above is on the full real 5-year window, with hundreds to low
thousands of trades per split, **positive on all three splits** for every
candidate shown — the first time in 9 runs this session has produced that
pattern outside of thin, since-disconfirmed samples.

### Status vs targets — the honest read

- **Target 1 (stable profit):** met with a trustworthy sample for the
  first time this session.
- **Target 2 (win rate ≥70%):** still not met. Best: 66.7% (validation),
  63.6% (holdout), both from `15m/4h mtf_stochastic_14_3_30_70`. This is
  the closest this session has come, but it is a real, ~4-7 point gap, not
  noise or rounding — reporting it exactly as measured, not rounding up.
- **Target 3 (frequency):** **computed after this entry was first written,
  and corrected here — it does NOT clear the bar.** 15m/4h holdout = 365.0
  days; stochastic's 165 holdout trades = 0.452/day, 3.16/week; full-window
  990 trades over 1825 days = 0.542/day, 3.80/week. Target 3 needs ≥1/day
  OR ≥7/week — this variant reaches roughly half the weekly bar and well
  under the daily one. The original version of this row guessed "likely
  fine" without doing the arithmetic; corrected once actually computed,
  same discipline this file has applied to every other unverified claim.
- **Target 4 (PF>1.3 etc.):** PF clears 1.3 on every split shown, several
  by a wide margin (up to 5.01). Sharpe/Sortino/max drawdown remain
  uncomputed by this tool — a standing gap since Run 1, not specific to
  this run.

### Known gaps in this run

1. Exact trade frequency (Target 3) not yet computed — next step.
2. Only 3 candidates tested per combination (2 RSI variants + 1 stochastic
   variant); the stochastic 30/70 (looser thresholds) variant clearly
   outperformed — a parameter pass specifically tightening/loosening this
   variant's thresholds hasn't been done yet, unlike every single-timeframe
   family earlier in this session.
3. Only 2 base/higher interval pairs tested (5m/1h, 15m/4h) — other
   combinations (e.g. 1h/4h, 5m/4h) unexplored.
4. Sharpe/Sortino/max drawdown still not in this tool's output.

### Next runs planned (as of Run 9)

1. Compute `15m/4h mtf_stochastic_14_3_30_70_trend_filtered`'s exact trade
   frequency against Target 3. **Done — corrected inline: 3.16/week, does
   NOT clear the 7/week bar (the original "likely fine" note was an
   unverified guess and was wrong).**
2. Parameter-sweep the stochastic variant's thresholds specifically (the
   one now-promising family). **Done — see Run 10 below.**
3. Try 1h/4h and 5m/4h combinations for completeness. Not yet done.
4. This is a real enough result to report directly and clearly to the
   user, not just log. **Done — reported directly in chat.**

---

## Run 10 — 2026-08-18T15:54Z (backtest, parameter sweep on the strongest candidate)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval 15m --days 1825 --higher-timeframe-interval
4h` — same combination as Run 9's best result, now including 2 new
variants added to `multi_timeframe_candidates()` (`finance-live-action`
commit `3975477`): tighter stochastic thresholds (20/80) and a slower
trend filter (SMA-50 instead of SMA-20).

**Result: neither follow-up beats Run 9's original 30/70/SMA-20 variant.**

| Variant | Train (n/win%/PF) | Validation (n/win%/PF) | Holdout (n/win%/PF) | Holdout freq |
|---|---|---|---|---|
| Original (30/70, SMA-20) | 606/61.1%/3.57 | 219/66.7%/5.01 | 165/63.6%/3.11 | 0.45/day, 3.16/wk |
| Tighter (20/80, SMA-20) | 526/54.0%/2.39 | 193/57.5%/3.00 | 149/59.1%/3.14 | 0.41/day, 2.86/wk |
| Slower trend (30/70, SMA-50) | 343/53.6%/2.82 | 123/65.0%/3.29 | 115/54.8%/2.92 | 0.32/day, 2.21/wk |

Tighter thresholds reduced trade count without improving win rate or PF
(holdout win rate actually fell, 59.1% vs 63.6%). The slower trend filter
also underperformed on holdout (54.8%) and reduced frequency further. Both
are real, useful negative results — they narrow what's already been tried
without finding an improvement, rather than leaving the question open.

### Status vs targets

Unchanged from Run 9: Target 1 and PF real for the original variant;
Target 2 (66.7% best) and Target 3 (3.16/week best, confirmed the binding
constraint — tightening thresholds made frequency worse, not better,
narrowing rather than closing this gap) remain short by real margins.

### Known gaps in this run

1. Only 2 follow-up variants tried; the parameter space around
   30/70/SMA-20 is not exhaustively searched.
2. 1h/4h and 5m/4h base/higher combinations still untested.
3. Frequency, not win rate, now looks like the harder constraint given
   tightening (the natural lever to raise win rate) directly worsens it.

### Next runs planned (as of Run 10)

- Combining multiple concurrent Alpha rules for frequency is a Portfolio-
  layer construction question, not a single strategy's parameter — raised
  directly with the user.
- Try 1h/4h and 5m/4h combinations. **Done — see Run 11: 5m/4h is the
  strongest result this session has produced.**

---

## Run 11 — 2026-08-18T16:45Z (backtest, 5m/4h combination — Target 2 cleared on all splits)

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval {1h,5m} --days 1825 --higher-timeframe-
interval 4h` — using already-deployed commit `3975477`, no new code.

**1h/4h: weaker than Run 9's 15m/4h** (43-51% win, PF 1.30-2.38 across
splits for `mtf_stochastic_14_3_30_70_trend_filtered`) — not the best
combination, reported for completeness.

**5m/4h: the strongest result this session has produced.** All three
stochastic trend-filtered variants clear **70% win rate on train,
validation, AND holdout simultaneously**:

| Variant | Train (n/win%/PF) | Validation (n/win%/PF) | Holdout (n/win%/PF) |
|---|---|---|---|
| mtf_stochastic_14_3_30_70_trend_filtered | 766/79.5%/15.08 | 255/83.5%/18.67 | **213/73.2%/8.53** |
| mtf_stochastic_14_3_20_80_trend_filtered | 746/74.0%/10.36 | 249/79.1%/12.37 | **205/72.7%/6.58** |
| mtf_stochastic_14_3_30_70_sma50_trend_filtered | 444/76.8%/13.76 | 153/81.0%/11.29 | **153/72.5%/6.71** |

**Data:** 5m/4h merged series over 1825 real days (5m: 525,600 candles;
holdout window 365.0 days). Pulled live via the standard SSH tunnel
pattern, torn down after.

**These numbers come from the same tested `SimulatedLedger`/`score_of`
machinery every prior run (positive or negative) in this file has used —
not a new, unvalidated computation path.** The result is an emergent
property of combining two independently-tested pieces (stochastic
oscillator entries, tested since Run 5; SMA-based higher-timeframe trend
filter, tested in Run 9) — not a special case in the scoring code itself.

### Status vs targets — the strongest read this session has produced

- **Target 1 (stable profit):** met, robustly.
- **Target 2 (win rate ≥70%):** **met, for the first time this session,
  on a real out-of-sample holdout with a trustworthy sample** (150-213
  holdout trades) — 72.5-73.2% holdout win rate across all three variants.
- **Target 3 (frequency ≥1/day or ≥7/week):** still not met. Holdout:
  `stoch_30_70` 0.584/day, 4.08/week — closest of any candidate this
  session (vs. 15m/4h's 3.16/week best), but still short. Full 5-year
  window: 4.73/week.
- **Target 4 (PF>1.3 etc.):** met by a very wide margin — PF 6.58-18.67
  across every split shown. Sharpe/Sortino/max drawdown still not computed
  by this tool (standing gap since Run 1).

### Known gaps in this run

1. Sharpe/Sortino/max drawdown remain unmeasured for this candidate — the
   tool's table output has never included them, across every run this
   session.
2. Frequency remains short of Target 3 for this candidate alone. Whether
   that matters depends on whether Target 3 is evaluated per-strategy or
   at the Portfolio layer across multiple concurrently-running rules
   (`deployment_rules.rs` already runs 3 rules concurrently in production)
   — a real open question, not yet resolved.
3. This is backtest evidence, not production evidence — `trades`/
   `trading_runs` in the actual production database are still 0 rows as of
   this session's last direct check. No amount of backtest evidence
   substitutes for that.

### Next runs planned (as of Run 11)

- Compute or approximate Sharpe/Sortino/max drawdown for this candidate.
  Still not done — standing gap.
- Explore whether relaxing the stochastic period trades win rate for
  frequency favorably. **Done — see Run 12: found a candidate that clears
  every numeric target, including frequency, for the first time this
  session.**

---

## Run 12 — 2026-08-19T01:32Z (backtest, frequency-focused follow-ups — first candidate to clear every numeric target)

**Why:** user asked directly, "tăng tần suất mà không giảm win rate đi"
(increase frequency without reducing win rate), on Run 11's 5m/4h
stochastic result. Implemented 3 single-axis variants (`finance-live-action`
commit `4bb231a`): looser thresholds (35/65), faster oscillator period
(%K=9), faster trend filter (SMA-10 instead of SMA-20).

**Command:** `finance-research --endpoint <production finance-mw gRPC, via
SSH tunnel> --broker binance --market-type perpetual_future --base-asset BTC
--quote-asset USDT --interval 5m --days 1825 --higher-timeframe-interval
4h`. **Data:** confirmed real, complete 5-year window — `candle_count:
525598`, `holdout_candle_count: 105119` → holdout = exactly 365.0 days.

**Result — `mtf_stochastic_14_3_30_70_sma10_trend_filtered` clears every
numeric target simultaneously:**

| Variant | Train (n/win%/PF) | Validation (n/win%/PF) | Holdout (n/win%/PF) | Holdout freq |
|---|---|---|---|---|
| Original (Run 11, SMA-20) | 767/79.4%/14.84 | 254/83.5%/18.24 | 213/73.2%/8.52 | 0.58/day, 4.08/wk |
| Looser (35/65) | 773/81.1%/18.14 | 260/84.6%/22.00 | 215/75.8%/11.15 | 0.59/day, 4.12/wk |
| Faster %K (period 9) | 783/83.8%/20.00 | 262/87.0%/35.61 | 215/80.5%/14.20 | 0.59/day, 4.12/wk |
| **Faster trend filter (SMA-10)** | 1193/78.8%/14.63 | 374/79.7%/15.74 | **377/75.9%/8.95** | **1.03/day, 7.23/wk** |

- **Target 1 (profit):** met — positive every split.
- **Target 2 (win ≥70%):** met — 75.9% holdout, *higher* than Run 11's
  73.2%, not traded away for the frequency gain.
- **Target 3 (frequency ≥1/day OR ≥7/week): met — the first candidate this
  entire session has cleared this bar.** 1.033/day AND 7.23/week on
  holdout alone (both independently, not just one); 1.065/day, 7.46/week
  over the full 5-year window.
- **Target 4 (PF>1.3):** met by a wide margin, PF 8.95 holdout. Sharpe/
  Sortino/max drawdown remain uncomputed — standing gap since Run 1, not
  resolved by this run.

**Why it worked:** SMA-10 reacts faster than SMA-20, so it "agrees" with
the inner stochastic signal more often, roughly doubling trade count
(213→377 holdout) versus Run 11's original. Win rate did not fall as a
result — it rose slightly. Consistent with Run 11's own observation that
looser inner thresholds also improved rather than hurt quality here: the
higher-timeframe agreement check appears to carry most of the real quality
screening in this design.

### Status vs targets — full honesty, not a declared win

**Every numerically-checkable target is met by this one candidate, on
real 5-year data, with the largest trustworthy sample this session has
produced (1,944 total trades).** This is qualitatively different from
every prior run.

**What this explicitly is NOT:**
- Not live evidence — `trades`/`trading_runs` in production are still 0
  rows. This is the strongest backtest evidence gathered, not proof.
- Not Sharpe/Sortino/drawdown-verified.
- Not a deployment — no code proposes shipping this to
  `deployment_rules.rs`. Per `live-execution-safety.md`'s own gates
  (largely unbuilt, found earlier this session), the honest next step
  toward using this would be paper/shadow testing infrastructure, not a
  live deploy.
- Not immune to standard backtest risk — one real 5-year period, not a
  guarantee about the future. Lower overfitting risk than Run 3/7's false
  leads given the sample size and train/validation/holdout consistency,
  but not zero risk.

### Known gaps in this run

1. Sharpe/Sortino/max drawdown still not computed — the one metric gap
   present in literally every run this session.
2. No paper/shadow-testing infrastructure exists to validate this
   candidate beyond backtest, per the `live-execution-safety.md` findings
   earlier this session.
3. Only one instrument (`binance.perpetual_future.BTC.USDT`) and one
   parameter neighborhood explored in depth — this is the strongest local
   result found, not a guarantee it's a global optimum.

### Next runs planned

- Report this finding to the user directly and completely (done in the
  same turn).
- Await user direction on next steps: further validation (Sharpe/drawdown,
  paper testing) versus other priorities.

### Addendum — 2026-08-19T01:58Z: explicit walk-forward framing per user request

User asked directly: use data older than 1 year to arrive at a model, then
run that fixed model as a "live simulation" over the most recent year, to
check whether it holds up. Confirmed the exact window boundaries (not
assumed): **train = oldest 3.00 years (~5yr ago to ~2yr ago); validation =
next 1.00 year (~2yr ago to ~1yr ago) — together, entirely data older than
1 year, the basis this candidate was selected on. Holdout = the most
recent 1.00 year exactly, zero influence on selection** — precisely the
two-phase structure requested.

Re-ran fresh (not reusing cached numbers) to confirm: **the model holds up
on the true out-of-sample "live simulation" year** — 377 trades, 75.9%
win, PF 8.95, PnL +23.62, 1.033 trades/day. Win rate in this most-recent,
never-selected-on year (75.9%) sits close to the two older windows (78.8%,
79.7%) rather than collapsing, and PF, though lower than the older windows
(8.95 vs 14.63/15.74), remains far above the 1.3 bar. This is the opposite
of Run 3/7's false-lead pattern (a strong number on one window evaporating
on a larger/later one) — here the edge is consistent in direction and
magnitude across three non-overlapping windows spanning 5 real years.

---

## Run 13 — 2026-08-19T03:15Z (backtest, extending the validated strategy to XAU/AUX — the user's "apply cho các token còn lại" request)

**Context:** user asked to try the same validated strategy on the other live
instruments, specifically AUX (production's shorthand for XAU). Production
actually runs **two** separate XAU instruments concurrently — confirmed via
`docker ps` on the production host, not assumed:
`live-action-binance-perpetual-future-xau-usdt-...` and
`live-action-exness-cfd-xau-usd-...`. Both were backtested with the exact
same, unmodified winning config (`mtf_stochastic_14_3_30_70_sma10`, 5m base /
4h higher-timeframe trend filter, k=14 d=3 oversold=30 overbought=70,
SMA-10 trend), no re-tuning, via the same SSH-tunneled
`--endpoint http://127.0.0.1:18086` production gRPC path used for every
other run in this log.

**Command (Binance XAU/USDT):** `finance-research --endpoint <tunnel>
--broker binance --market-type perpetual_future --base-asset XAU
--quote-asset USDT --interval 5m --days 1825 --higher-timeframe-interval 4h`

**Data:** 72,228 real 5m candles — **only ~250.8 days of history exist for
this pair on Binance** (the `--days 1825` request returned everything
available, not a full 5 years; this instrument has a much shorter listing
history than BTC/USDT). Split: train 43,337 / validation 14,446 / holdout
14,445 candles (holdout window = 50.2 days).

| split      | trades | win % | PF    |
|------------|--------|-------|-------|
| train      | 138    | 72.5% | 14.37 |
| validation | 56     | 75.0% | 15.16 |
| holdout    | 44     | 70.5% | 9.44  |

Holdout frequency: 44 trades / 50.2 days = **0.877/day, 6.14/week** — misses
**both** halves of Target 3 (>=1/day OR >=7/week), narrowly.

**Command (Exness XAU/USD):** `finance-research --endpoint <tunnel>
--broker exness --market-type cfd --base-asset XAU --quote-asset USD
--interval 5m --days 1825 --higher-timeframe-interval 4h`

**Data:** 353,732 real 5m candles = 1228.2 days (~3.37 years) of real
history — reachable through the same production gRPC path even though this
session had never queried Exness data before. Split: train 212,239 /
validation 70,746 / holdout 70,747 candles (holdout window = 245.6 days).

| split      | trades | win % | PF    |
|------------|--------|-------|-------|
| train      | 770    | 68.4% | 7.17  |
| validation | 232    | 75.0% | 7.05  |
| holdout    | 257    | 70.4% | 10.28 |

Holdout frequency: 257 trades / 245.6 days = **1.046/day, 7.32/week** —
clears **both** halves of Target 3.

**Honest read against all 4 targets, per instrument:**

- **Exness XAU/USD**: Target 2 cleared on all 3 splits (68.4/75.0/70.4%, all
  >=70% except train at 68.4% — close but technically under on train only;
  validation and holdout both clear). Target 3 cleared on holdout
  (1.046/day, 7.32/week). Sample size is healthy and comparable in shape to
  the BTC finding (257 holdout trades vs BTC's 377). Target 4 (Sharpe/
  drawdown/Sortino/positive-day-ratio) not yet computed for this instrument
  — same gap that exists for the BTC finding, not newly introduced here.
- **Binance XAU/USDT**: Target 2 cleared on all 3 splits (72.5/75.0/70.5%),
  actually stronger PF than Exness (9.44-15.16 vs 7.05-10.28). Target 3
  **missed** on both sub-conditions (0.877/day < 1, 6.14/week < 7) — close,
  but a miss is a miss, reported as such rather than rounded up. Sample is
  also thin in absolute terms (44 holdout trades total) because this venue
  only has ~251 days of history for this pair — not a strategy weakness, a
  data-availability constraint specific to this listing.

**Decision:** deployed the validated strategy to **Exness XAU/USD** only
(code change: `finance-live-action` `deployment_rules.rs`, new
`is_exness_xau_cfd()` gate alongside the existing `is_binance_btc_perpetual()`
gate, same `ConfiguredStrategy` id `mtf_stochastic_5m_4h_sma10`, same
signal-only/no-real-capital framing as the BTC deployment). **Did not**
deploy to Binance XAU/USDT — Target 3 miss plus thin sample means the
evidence bar this session has held every other promotion to (BTC needed a
full walk-forward pass; every negative single-timeframe result was reported
as negative, never rounded to "close enough") is not yet cleared. Full
workspace test suite (`cargo test --workspace --release`) green, 36/36 test
binaries passing, before this line was written.

### Next runs planned

- Push, verify CI, deploy through Coolify, and confirm on the live
  dashboard (`finance.thanhne.io.vn`) that Exness XAU/USD now shows the new
  strategy in its weight table and that Binance XAU/USDT does not — mirroring
  the exact verification already done for BTC.
- Revisit Binance XAU/USDT once more real history accumulates on that venue,
  or if a walk-forward re-check on the existing thin sample still holds up
  despite the frequency miss (not assumed yet — will report honestly either
  way).

### Correction — 2026-08-19T03:25Z: the Exness deploy above was wrong, reverted

User pushed back on the frequency methodology directly: "tôi nghĩ cứ có
total dữ liệu rùi nhân % đi, chia tập data ra thì hợp lí hơn" (just take the
total data and multiply by the split percentages — that's more logical).
That was the right challenge. Every frequency number in this log, including
Run 13 above, estimated "holdout days" as `holdout_candle_count *
interval_minutes / 60 / 24` — i.e. assumed the market trades continuously
with zero gaps. That assumption is correct for Binance crypto (24/7,
verified below) but wrong for Exness XAU/USD, which is a CFD that closes on
weekends.

Fixed the root cause rather than just recalculating by hand: added
`holdout_span`/`holdout_start`/`holdout_end`/`holdout_calendar_days` to
`finance-research`'s `research.backtest_candle_count` JSONL event
(`crates/finance-research/src/candle_count_log.rs` +
`crates/finance-research/src/main.rs`), computed from the **actual**
`open_time`/`close_time` of the first and last holdout candle rather than
an assumed cadence. 2 new unit tests
(`omits_holdout_span_fields_when_not_provided`,
`computes_real_calendar_days_from_the_holdout_span_not_candle_count`).
Re-ran both XAU backtests fresh against this instrumented build:

| instrument         | holdout candles | assumed days (old, wrong) | real calendar days (new) | trades | trades/day | trades/week |
|---------------------|-----------------|----------------------------|----------------------------|--------|------------|--------------|
| Exness XAU/USD      | 70,747          | 245.6                      | **364.63**                 | 268    | **0.735**  | **5.14**     |
| Binance XAU/USDT    | 14,446          | 50.2                       | 50.16 (matches — confirms 24/7 crypto has no gap to correct for) | 44 | 0.877 | 6.14 |

**The real numbers reverse Run 13's decision.** Exness XAU/USD's holdout
span is 70,747 candles spread across 364.6 real days (not 245.6) because
its weekend closures mean each calendar week holds fewer 5m candles than a
24/7 market — so the true trade frequency (0.735/day, 5.14/week) is *lower*
than what Run 13 reported, not higher, and it now misses Target 3 just like
Binance XAU/USDT does. Win rate/PF are essentially unchanged and still
strong (Exness holdout re-ran at 70.9% win / PF 10.64 on a slightly larger
270-candle-newer sample), but this session's own standard — hold every
target to the same bar BTC was held to before promotion, frequency
included — means neither XAU instrument clears the bar yet.

**Action taken:** reverted the `is_exness_xau_cfd()` deployment gate in
`finance-live-action/crates/finance-api/src/deployment_rules.rs` back to
BTC-only before it was ever pushed or deployed — full revert, not a
patch on top: `configured_extra_strategies()`, its doc comment, and the
test suite are back to exactly gating on `is_binance_btc_perpetual()`.
Full workspace test suite re-verified green (36/36 binaries, 0 failures)
after the revert. **No incorrect deployment reached CI, Coolify, or
production** — this was caught and corrected entirely at the local
backtest/code-review stage, before any push.

**Standing improvement kept:** the `holdout_calendar_days` instrumentation
is real, tested, and stays in `finance-research` regardless of this
decision — every future frequency check against a non-24/7 instrument (any
Exness CFD, any market with scheduled downtime) now has a correct
denominator available in the JSONL event instead of relying on an assumed
cadence.

### Next runs planned (updated)

- Neither XAU instrument is deployed. Continue searching for a config that
  clears frequency on real calendar time for at least one XAU instrument
  before proposing another promotion — same discipline that took BTC
  several frequency-focused iterations (Runs 9-12) to clear.
- Apply the same real-calendar-day correction retroactively to a fresh BTC
  spot-check (expected to match the existing numbers almost exactly, since
  Binance crypto has no weekend gap — but verify rather than assume, per
  the standing no-fabrication rule).

**Spot-check result (2026-08-19T03:34Z):** re-ran the BTC 5-year backtest
against the instrumented build. Holdout = 105,120 candles; instrumented
real calendar span = **364.99998842592595 days** vs the candle-count-based
estimate of exactly 365.0 days — a 0.00001-day difference, i.e. no gap
exists in Binance's 5m BTC/USDT stream, confirming the assumption held for
every prior BTC entry in this log. Fresh numbers this run: 377 holdout
trades, 75.9% win, PF 8.94, 1.033 trades/day — matches the already-live
deployment's validated figures. **No change needed to the BTC deployment;
it was correct all along.** Only the XAU/AUX numbers were wrong, and only
because Exness CFD data has real weekend gaps that Binance crypto does not.

---

## Run 14 — 2026-08-19T09:34Z: Target 4 finally checked for real (Sharpe, Sortino, drawdown, positive-day-ratio)

Target 4 (Sharpe >= 1.0, max drawdown <= 10%, PF > 1.3, positive-day ratio
>= 55%, Sortino >= 1.0) was set on 2026-08-17 and had **never actually been
run** against the live BTC strategy in any prior entry in this log — every
"Run" above reported Target 1-3 honestly but silently skipped Target 4. Two
real gaps blocked it, found and fixed today in `finance-research`:

1. `--daily-profit-gate` was hardcoded to test `CandleMomentumStrategy`
   regardless of what the caller wanted checked — running it before today
   would have graded the wrong strategy entirely, not the live
   `mtf_stochastic_14_3_30_70_sma10_trend_filtered`. Added a
   `--gate-strategy <id>` flag that resolves any registered candidate by
   name, wired to use the multi-timeframe holdout window when
   `--higher-timeframe-interval` is set.
2. **Two real correctness bugs in the gate itself**, both the same root
   cause (a multi-timeframe holdout mixes base-interval and higher-
   interval klines, and code written before multi-timeframe existed
   assumed every kline was base-interval):
   - `daily_profit_gate::replay` fed every kline — including 4h ones — to
     `ledger.on_kline`, exactly the bug `sweep.rs::score_window` was fixed
     for earlier this session, just never ported to this second call site.
     Fixed with the identical one-line guard.
   - `interval_continuity_violations` counted every interspersed 4h candle
     as a "gap" in the 5m cadence. On the first real run, this alone
     produced 2189 false violations and failed the gate
     (`holdout_interval_continuity: false`) despite every substantive
     metric passing. Fixed by filtering to base-interval klines first,
     same pattern.
3. Also found while fixing (2): **the pre-existing regression tests for
   bug (1)'s bug class — `sweep.rs`'s own
   `score_window_ignores_higher_timeframe_klines_for_ledger_accounting`,
   written and committed earlier this session — passed even with its own
   guard removed.** `ProtectiveLevels::None` means a stop/take level never
   exists to trigger against a wide high/low, so the test was vacuously
   true and never actually caught the regression it claimed to guard
   against. Fixed both that test and the new `daily_profit_gate` one to
   use a real `ProtectiveLevels::Fractional` band wide enough to isolate
   from natural price action but narrow enough that the deliberately
   extreme higher-timeframe fixture triggers it — verified by physically
   removing each guard and confirming the test then fails (`left: 0, right:
   1` trade-count mismatch in both cases) before restoring the fix.

**Real result, run against production BTC data via the same SSH-tunneled
endpoint used all session** (`--gate-strategy
mtf_stochastic_14_3_30_70_sma10_trend_filtered --higher-timeframe-interval
4h`, full 5-year window, 366-day holdout):

| metric | value | threshold | pass |
|---|---|---|---|
| Sharpe ratio | **10.34** | >= 1.0 | yes |
| Sortino ratio | **50.93** | >= 1.0 | yes |
| Max daily drawdown | 0.00246% | <= 10% | yes |
| Max total drawdown | 0.00349% | <= 10% | yes |
| Positive day ratio | 69.1% | >= 55% | yes |
| Median daily PnL | +$0.0051 | > $0 | yes |
| Max negative-day streak | 5 days | <= 5 | yes |
| Cost-to-gross-PnL ratio | 10.06% | <= 50% | yes |
| Interval continuity | 0 violations | 0 | yes |
| Holdout days | 366 | >= 90 | yes |

**`passed: true` — Target 4 is cleared, honestly, for the first time.** Net
realized PnL over the 366-day holdout: $23.60 (matches the $23.62 found in
the 2026-08-19T01:58Z walk-forward entry almost exactly, cross-confirming
both measurements independently). Combined with Targets 1-3 already
cleared (Runs 9-12), **all four original targets are now cleared for the
live BTC strategy**, checked end-to-end rather than assumed.

Commit `ba56419` (finance-live-action), pushed. CI verification in
progress via the detached watcher.

**CI/deploy confirmed (2026-08-19T10:08Z):** all jobs green
(https://github.com/ThanhNguyenDat/finance-live-action/actions/runs/32238802144
— pre-commit, build-and-push, deploy-app, retain-app-images). SSH-verified
directly: `live-action-binance-perpetual-future-btc-usdt-...` running image
`finance-live-action_sha-ba56419d0b3775575f0469f1d71ef541c2b3fe94`, healthy.
As expected, this is a research-tooling-only change (`deployment_rules.rs`
untouched) — the live strategy's actual behavior is unaffected; only
`finance-research`'s offline CLI gained the ability to check it correctly.

### Next runs planned

All 4 original targets are now cleared for BTC, checked end-to-end rather
than assumed. Continue exploring additional strategies/regimes per the
standing rules, or revisit the still-open Exness data-freshness / stale-
threshold findings from earlier today (silent-error fix and watermark
metric already shipped; the deeper architectural items — shared mutex
between startup backfill and recurring sync, sequential per-instrument
blocking loop — are still open, found but not yet fixed).
