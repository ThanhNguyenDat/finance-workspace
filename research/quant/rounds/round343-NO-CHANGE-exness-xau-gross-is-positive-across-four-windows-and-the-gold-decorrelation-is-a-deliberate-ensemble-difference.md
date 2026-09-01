# "SURVIVED WINDOW VARIATION" NEEDS DISCOUNTING (Round 352)

This file called `exness XAU`'s positive gross *"the first quantity in this entire arc that has
survived window variation"*. The measurement stands — and now extends to **six** windows
(+0.3391 / +0.6000 / +0.7820 / +0.7300 / **+0.9550** / +0.5550 at 300 / 500 / 900 / 1200 / 1500 /
1800 days) — but the phrase needs reading carefully.

**Every holdout in this arc is nested.** All of them end on the same day and each larger window's
holdout strictly contains the smaller ones (@300 2026-07-01→08-28 ⊂ @900 2026-03-04→08-28 ⊂ @1200
⊂ @1500 ⊂ @1800). Two `--days` values can never produce disjoint out-of-sample periods, because
the holdout is always the tail of a window ending at "now", and the CLI has no as-of flag.

So agreement across windows is **partly guaranteed** — the recent data is inside every sample.
Window-*fragility* results (a superset behaving differently) are unaffected; window-*replication*
language, including this file's, is weaker than it sounds. See `round352-NEEDS-MORE-RESEARCH-every-holdout-in-this-arc-is-nested-so-no-two-windows-are-independent-and-the-weekday-signal-is-half-replicated.md`.

---

# Round 343 — NO-CHANGE: `exness XAU`'s positive gross **survives four windows** (300, 500, 900, 1200 days) — the first quantity in this arc to do so. The gold decorrelation is a **deliberate ensemble difference** verified in production code. And a day's PnL is **not** a fixed quantity: it changes with the window.

Classification: **NO-CHANGE** — the pre-registered robustness test passed, the mechanism behind
Round 342 is identified in code, and nothing about the deployed configuration should change.
Two bounded Docker sweeps (exactly the 2-container budget) plus **zero-container** code
inspection and cross-window comparison of saved runs. **XAU-first.**

## Part 1 — the arc's load-bearing claim, tested

Every cost and band round since Round 313 rests on one fact: `exness XAU` earns a **positive
gross edge** and loses it to execution cost. Round 341 showed that on `bybit XAUT` the gross
*sign* flips with the window, so this needed a direct test.

**Pre-registered as a partition:** gross is positive at **both** `--days 300` and `--days 1200`
→ window-robust; **negative at either** → the fleet's "only positive gross" is window-scoped
like everything else.

| window | holdout | obs. days | trades | tr/wk | **gross** | cost | net | Sharpe | streak |
|---|---|---|---|---|---|---|---|---|---|
| **300** | 2026-07-01 → 08-28 | 51 | 42 | 5.05 | **+0.3391** | 0.3845 | **−0.0454** | −0.249 | **3** |
| 500 | 2026-05-22 → 08-28 | 84 | 126 | 8.95 | **+0.6000** | — | −0.2283 | −0.814 | 4 |
| 900 | 2026-03-04 → 08-28 | 151 | 174 | 6.85 | **+0.7820** | 1.1929 | −0.4110 | −0.860 | 5 |
| **1200** | 2026-01-02 → 08-28 | 202 | 190 | 5.59 | **+0.7300** | 1.1900 | −0.4600 | −0.763 | 5 |

**Positive at every window. The prediction holds.** Gross runs +0.34, +0.60, +0.78, +0.73
across a 4x span of window lengths and holdouts starting anywhere from January to July.

This is **the first quantity in this entire arc that has survived window variation** — set
against the optimal band (Round 331), the optimal frequency (Round 334), the gross trough
(Round 341) and `bybit XAUT`'s gross *sign* (Round 341), all of which moved. The premise the
cost work rests on is sound.

It is still a loss at every window (net −0.045 to −0.460, cost÷gross 1.13 to 1.63), and the
route remains gate-ineligible at all four — the seven interval-continuity checks fail at 300
and 1200 exactly as at 500 and 900.

Worth noting: **`--days 300` is the closest to break-even this route has ever measured on the
deployed band** — net −0.0454, cost÷gross 1.134, and a negative-day streak of **3**, the best
seen. That is one window, and Round 341's lesson applies to it as much as to anything else.

## Part 2 — why the two gold routes decorrelate (investigation only, nothing applied)

Round 342 measured price correlation **+0.996** and PnL correlation **+0.287** between
`exness XAU` and `bybit XAUT`, and listed three candidate mechanisms without testing any. One
of them is settled by reading the code:

**`finance-research/src/strategies.rs:24-78`** — `production_candidates` starts every route
with exactly two strategies (`candle_momentum`, `rsi_mean_reversion`) and adds extras to
**three routes only**:

| route | ensemble |
|---|---|
| `binance BTC/USDT` perp | base 2 + `btc_trend_filtered_candidates("mtf_stochastic_5m_4h_sma10")` |
| **`exness XAU/USD` cfd** | base 2 + **`mtf_stochastic_5m_4h_sma5`** |
| `exness BTC/USD` cfd | base 2 + `btc_trend_filtered_candidates("mtf_stochastic_5m_4h_35_65_sma10")` |
| `bybit XAUT`, `bybit BTC`, `binance XAU` | **base 2 only** |

**The two gold routes do not run the same strategies.** `exness XAU` runs a multi-timeframe
trend-filtered stochastic that `bybit XAUT` does not. Identical prices fed to different
ensembles produce different signals, different trades and different PnL — the decorrelation
needs no further explanation.

**And this mirrors production exactly, so it is not a measurement defect.**
`finance-api/src/deployment_rules.rs:616-642` gates the live ensemble with the same three
predicates (`is_binance_btc_perpetual`, `is_exness_xau_cfd`, `is_exness_btc_cfd`), and the
exclusions are deliberate and documented in place: `binance XAU` is excluded because *"the same
config regressed its holdout win rate below target there"* (`:624-627`), and the test at
`:747-780` asserts `binance XAU`, `bybit BTC` and `bybit XAUT` keep exactly
`["candle_momentum", "rsi_mean_reversion"]`, noting XAUT *"is tokenized Tether Gold spot, not
an XAU CFD or perpetual; it intentionally starts with only the base strategies."*

**Investigation only — nothing applied, no change proposed.**

But the ensemble does **not** order the whole correlation matrix. The identical-ensemble BTC
pair is highest (+0.856), yet `bybit XAUT` and `binance XAU` share the base-2 ensemble and
correlate at only **+0.423**, below the cross-ensemble `exness XAU`/`binance XAU` pair at
+0.589. Ensemble difference is a **sufficient** mechanism for the gold pair; it is not the only
driver.

## Part 3 — a day's PnL is not a fixed quantity

Round 341 reported `2026-08-12` as `exness XAU`'s worst day *"at both the 500- and 900-day
windows and at every band — band-independent **and** window-independent on that route."*
Adding two more windows at the deployed band refutes the second half:

| calendar day | @300 | @500 | @900 | @1200 |
|---|---|---|---|---|
| 2026-08-12 | −0.0545 | −0.1796 | −0.1796 | **+0.0015** |
| 2026-07-16 | −0.0575 | −0.0575 | −0.0575 | **−0.2186** |
| 2026-08-21 | **−0.1666** | **+0.0924** | 0.0000 | 0.0000 |

All four holdouts **contain** all three dates, and the band is identical. Yet the same session's
PnL changes, and twice it **changes sign**. The worst day is `2026-08-12` at 500 and 900,
`2026-08-21` at 300 and `2026-07-16` at 1200.

This is the per-kline weight refit (Round 300) showing up in the daily array: a longer replay
carries different interval and strategy weights over the bars it shares with a shorter one, so
it takes different trades on the same day. **Daily results may not be compared across windows**
— the same restriction Round 300 established for Portfolio counters, now extended to the daily
array. Round 341's cross-route day comparisons were all **within** one window each, so they
stand; its window-independence claim does not.

## What is proven, and what is not

Proven:

- `exness XAU` @300: 51 observed days, 42 trades, 5.053/week, gross **+0.33907**, cost 0.38445,
  net −0.04538, Sharpe −0.2488, Sortino −0.3744, streak 3, cost÷gross 1.1338, 7 continuity
  failures.
- `exness XAU` @1200: 202 observed days, 190 trades, 5.586/week, gross **+0.72998**, cost
  1.18997, net −0.45999, Sharpe −0.7632, Sortino −1.0794, streak 5, cost÷gross 1.6301, 7
  continuity failures.
- Gross is positive at 300, 500, 900 and 1200 days on this route.
- The code citations above, read directly, including that research mirrors production's gating.
- The three-date cross-window table, all four holdouts containing all three dates.

Not proven, and deliberately not claimed:

- **That the ensemble difference explains the correlation matrix.** It explains the gold pair.
  It does not order the rest — the base-2 `bybit XAUT`/`binance XAU` pair correlates lower than
  a cross-ensemble pair.
- **That the extra strategy is why `exness XAU` has positive gross.** `exness BTC` runs an
  enriched ensemble too and has the fleet's *worst* gross (−2.1476). There is no flag to run
  `exness XAU` without its extra strategy, so this is **untested** and I am not asserting it.
- That `--days 300`'s near-break-even net means anything beyond that window. One window, and
  the whole arc says windows move.
- That the daily-array window dependence is fully explained by the weight refit. That is the
  known mechanism that would produce it; I ran no controlled test isolating it.
- Any promotion. Every window of every route still fails, and this route cannot produce a
  gate verdict at all.
