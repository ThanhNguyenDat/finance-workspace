# CROSS-ROUND COMPARISONS DRIFT — CHECK `candle_count` (Round 360)

A method rule that belongs with the audit findings: **two runs from different rounds are not
necessarily the same window.** Every run emits `candle_count` in its first ECS line
(`event.dataset: research.backtest_candle_count`); **two runs are comparable only if it matches.**

Measured: `exness XAU` @300 runs 3.5 hours apart gave **57,965** and **57,925** candles, while the
same-day `binance BTC` and `bybit XAUT` @500 runs all gave **143,998**. Session instruments drift;
24/7 crypto windows quantise. And when only Portfolio-construction parameters vary,
**`legacy_selected_rule` is a free drift control** — it bypasses the construction guard, so any
movement in it is drift, not treatment. In the voided comparison it moved **0.306**, the same size
as the 0.315 "effect". See `round360-DATA-ISSUE-cross-round-comparisons-drift-and-legacy-is-a-free-drift-control-the-hold-ladder-saturates-at-72.md`.

---

# THE OTHER END OF L4 (Round 357)

Audit item **L4** records that the backtest serialises no per-trade record. Production has now
been checked from the other side and has the mirror-image problem: the durable trade logs
(`trades:<route>`, zset, three entries per close, **no TTL**) hold **1 to 6 closed trades per
route** over a span that matches worker uptime — earliest entry 2026-08-27 14:39 UTC, all six
workers "Up 3 days". **`exness XAU` retains exactly one closed trade.**

So there is currently **no path from a backtest number to a live observation of the same
quantity**: aggregates only on one side, 1-6 closes reset on restart on the other. The three BTC
routes' live rates are consistent with their backtest rates, but with exact Poisson intervals of
**[5.63, 33.36]**, **[3.11, 29.26]** and **[2.63, 24.72]** per week — agreement by lack of power.
See `round357-DATA-ISSUE-the-live-trade-log-holds-1-to-6-closes-so-it-cannot-validate-any-backtest-rate.md`.

---

# L3 QUANTIFIED (Round 354)

The UTC+7 day-bucketing dilution recorded as **L3** is now measured on `exness XAU` @1800:
**49 Saturday buckets, 47 of them (95.9%) exactly zero**, and **88 of 306 rows (28.8%) zero
overall**. `positive_day_ratio` reads **0.37255** (114/306); excluding the Saturday buckets it is
**0.43580** (112/257) — **the Sat bucket alone depresses it by 0.06325**, about 17% of the
reported value, against a 0.55 threshold written for an instrument that trades every day.
See `round354-REJECTED-the-weekday-pattern-inverts-on-btc-routes-and-my-registered-criterion-was-vacuous.md`.

---

# CONFIRMED FROM PRODUCTION LOGS, AND TWO DIVERGENCES ADDED (observability audit)

This file's invariants were **code-verified only**. They are now **observed** in production ECS
logs and OpenTelemetry spans: on `exness XAU` 2026-08-28, **0 of 620** signal events were
emitted before their bar closed (min lag **+1.015 s**, median +2.133 s), Kafka offsets are
strictly increasing on all eight topics, and **245 distinct `market.event.id` were each
processed under exactly one trace** — no duplicate execution. Item **L4** (no per-trade audit
trail) is confirmed at runtime: the backtest CLI emits exactly one ECS event per run.

The logs also expose two things code reading could not: **Binance revises closed klines** (347/day
on BTC, 154/day on XAU, zero on Bybit and Exness) and live **blocks strategy evaluation** for the
revision while the replay reads the post-revision values; and **production enforces an
`execution_cost` gate at 10 bps** that the replay does not model. See `observability-trace-audit-production-logs-verify-causality-and-expose-two-backtest-live-divergences.md`.

---

# L1 QUANTIFIED AND DE-ESCALATED TO P3 (Round 346)

This file's **L1 (P2)** — protective fills execute at exactly the stop/take with no gap
modelling — is now measured on `exness XAU` 5m since 2024-09-01. Session-boundary gaps: n=118,
mean **0.2565%**, max **2.0030%**, and only **6 (5.08%)** reach the deployed 1% stop. Intraday:
**1 bar in 140,901** gaps past 1%, so within a session the exact-stop fill is essentially exact.
Worst case is about **2x** the modelled loss on roughly **6 events in two years**.

**L1 is de-escalated to P3.** The exposure is real, confined to session boundaries exactly as
this file predicted, and bounded. What remains blocked is the join: whether the Portfolio
actually held a position across any of those six boundaries is **not determinable** — that is
audit item **L4** (no per-trade audit trail), which is unchanged. See `round346-REJECTED-dropping-the-protective-band-is-profitable-at-300-days-and-worse-at-900-and-the-gap-fill-risk-is-quantified-small.md`.

---

# Backtest correctness audit — look-ahead, causal ordering, fill and accounting invariants

**Investigation only — nothing applied, no fix proposed.** Claude role note: inspect and
document with `file:line`, leave implementation to Codex. Method: code trace of the replay
pipeline, plus empirical checks on eight saved gate runs and one narrow read-only Timescale
query for independent confirmation.

## Verdict

**No look-ahead found.** Every point where future information could leak into a decision is
gated on bar close, and the fill convention is adverse-to-the-position. Two real limitations and
one tooling gap are recorded below; none of them is a look-ahead bug.

---

## PASS — causal ordering and no look-ahead

**1. Only closed bars enter the replay.**
`finance-research/src/klines.rs:246` — `if !item.is_kline_closed { continue; }`. A forming bar
can never contribute a signal.

**2. Event ordering is by close time, not open time.**
`finance-research/src/portfolio_decision_replay.rs:59-67` — `replay_order` sorts every interval's
klines by `close_time`, tie-broken by **ascending** interval length. A 4h bar therefore enters
the stream only once it has closed, and when a 5m and a 4h bar close at the same instant the
**5m is processed first** (5 < 240). The base interval never sees a higher-timeframe bar that
closed at the same moment — conservative, and it matches what a live worker would have.

**3. The multi-timeframe trend filter is causal.**
`finance-strategy/src/multi_timeframe_trend_filter.rs:77-116` — the higher-timeframe trend sign
is written **only** when a closed higher-interval kline arrives, and base-interval evaluations
read the last stored sign. Warm-up returns `None` — *"an absence of information, not agreement —
suppress rather than guess"* — so no signal is emitted before the SMA exists. This is the
classic MTF look-ahead trap and it is correctly avoided.

**4. The Portfolio decides only on evidence available at that instant.**
`portfolio_decision_replay.rs:340-347` — `evidence.decide(primary.close_time)` runs only when
`evidence.is_synchronized(primary.close_time)`; the evidence store has ingested exactly the
events whose `close_time` has already passed in the ordered stream.

**5. Weight refitting is online, not fitted on the whole window.**
`portfolio_decision_replay.rs:317` — `reweight_from_alpha_performance` is called inside the
per-kline loop, from **cumulative past** ledger performance. It is a source of path dependence
(Round 300) but it is not leakage: no future bar contributes.

**6. Entry fills are adverse, at the decision bar's close.**
`finance-core/src/trading_modes.rs:1919-1923` —
`Long => kline.close * (1.0 + slippage)`, `Short => kline.close * (1.0 - slippage)`. The fill
uses the close that produced the decision and moves **against** the position. No intrabar
favourable price (a low for a long) is ever used.

**7. A position cannot be stopped out by the bar that opened it.**
`trading_modes.rs:1745-1760` — per bar the order is `record_true_range` → `settle_funding` →
`try_close_at_protective_level` → `apply_target`. The protective check runs against the
**existing** position before the new target is applied, so a same-bar entry-and-exit round trip
is structurally impossible.

**8. Ambiguous bars resolve pessimistically.**
`trading_modes.rs:2153-2161` — when a bar's range contains both the stop and the take,
`(true, _) => stop` fires: the **loss** is taken. The optimistic branch does not exist.

---

## PASS — empirical checks on real runs

**9. Accounting integrity, 8 gate runs across all six routes.**
`ending_equity[i] == starting_equity + cumsum(realized_pnl)[i]` holds to a maximum absolute
error of **1.3e-11** on equity of 1e4 (relative ~1e-15, i.e. float noise), and
`sum(daily realized_pnl) == net_realized_pnl` exactly, on every run:

| run | days | Σ daily | `net_realized_pnl` | max equity drift |
|---|---|---|---|---|
| `exness XAU` @300 | 51 | −0.04538 | −0.04538 | 5.5e-12 |
| `exness XAU` @900 | 151 | −0.41099 | −0.41099 | 3.6e-12 |
| `exness XAU` @1200 | 202 | −0.45999 | −0.45999 | 7.3e-12 |
| `binance BTC` @500 | 101 | −3.94069 | −3.94069 | 1.3e-11 |
| `bybit BTC` @500 | 101 | −2.74173 | −2.74173 | 3.6e-12 |
| `exness BTC` @500 | 101 | −4.56244 | −4.56244 | 7.3e-12 |
| `bybit XAUT` @500 | 101 | −0.42039 | −0.42039 | 1.8e-12 |
| `binance XAU` @500 | 53 | −0.58934 | −0.58934 | 0.0 |

**10. A calendar alarm that resolved to correct behaviour.**
The gold CFD showed **non-zero PnL on Saturdays** — 2026-08-29, 2026-03-28, 2026-04-18,
2026-07-11, 2026-08-08, 2026-04-25, 2026-06-27, 2026-07-18, all verified as Saturdays. Gold is
closed all weekend, so this looked like a data or calendar defect.

A narrow read-only Timescale query settles it: `exness XAU` has **zero 5m bars on every one of
those Saturdays**, and Friday 2026-08-28 has 252 bars running **00:00 → 20:55 UTC** — the
session closing at 21:00 UTC as expected.

The explanation is in `finance-research/src/daily_profit_gate.rs:340` and `:402`:
`kline.close_time.with_timezone(&timezone).date_naive()` with `TRADING_TIMEZONE =
"Asia/Ho_Chi_Minh"` (UTC+7). Bars closing from 17:00 UTC onward fall on the **next** calendar
day in UTC+7, so the Friday-evening session is bucketed to Saturday. **Correct behaviour in the
declared operating timezone, not a defect** — and consistent: 2026-08-28 (+0.09557) and
2026-08-29 (+0.09407) are the two halves of one Friday session.

A cross-check confirms the calendar handling is instrument-driven rather than a blanket rule:
`exness BTC` is also a CFD but has PnL on **30 of 30** weekend days, matching Round 337's
finding that BTC/USD trades around the clock at that venue.

---

## Limitations found — real, and none of them look-ahead

**L1 (P2) — protective fills ignore gap risk.**
`trading_modes.rs:2143-2161` triggers on `kline.low <= stop` / `kline.high >= take` and then
fills at **exactly** the stop or take price. A bar that gaps straight through the level would
fill materially worse in reality. This bites hardest where gaps are structural — and
`exness XAU`, the one route with a positive gross edge, **closes every weekend**. Effect:
**tail loss is understated**, so measured drawdown and streak metrics are optimistic by an
unquantified amount.

**L2 (P3) — the holdout is not entry-clean at its boundary.**
Two of eight runs (`exness XAU` @900, `binance XAU` @500) book non-zero PnL on holdout **day 0**,
meaning a position opened during training closed inside the holdout. This is not look-ahead —
no future information was used — and it matches live behaviour at any boundary, but the first
day's PnL is not attributable to a holdout-only decision.

**L3 (P3) — UTC+7 bucketing splits a CFD session across two "days".**
Per L10 above, `exness XAU`'s Friday session lands in two daily buckets, one of them only a few
hours long. `observed_days`, `positive_day_ratio`, `median_daily_pnl` and
`maximum_negative_day_streak` are all computed over these buckets, so the gate applies per-day
thresholds to partial days. Consistent with the declared timezone; it still dilutes the
statistics it feeds.

**L4 (tooling gap) — there is no per-trade audit trail in the output.**
`finance-research/src/portfolio_measurement.rs:23-28` — `ExecutionFootprint` exposes only
`ledgers`, `trades`, `realized_pnl`, `funding_paid`. `SimulatedTrade`
(`trading_modes.rs:1548-1562`) carries `entry_at`, `exit_at`, `entry_price`, `exit_price`,
`close_reason` — and is **never serialized**. **Consequence: fills cannot be reconciled against
market data end-to-end without a code change.** Everything in sections 1-8 above is verified by
reading the code, not by auditing executed trades. This is the single largest limit on
independent verification of this pipeline.

**L5 — process-level selection bias, outside the code.**
The in-code train/validation/holdout split is clean, but the deployed band and parameters were
chosen across many rounds that reused overlapping holdouts. That is a property of the research
process, not of the replay, and no code change addresses it.

---

## Verification checklist (for whoever implements)

- [ ] Serialize `SimulatedTrade` records (behind a flag or capped by `max_retained_trades`) so
      fills can be reconciled against Timescale bars — closes L4 and makes 1-8 independently
      auditable.
- [ ] Reconcile a sample of entries: `entry_price / (1 ± slippage_bps/1e4)` must equal the 5m
      close at `entry_at` for that instrument.
- [ ] Assert no trade has `exit_at` in the same bar as `entry_at`.
- [ ] Decide explicitly whether gap-through fills should be modelled (L1) — at minimum record
      how often `kline.open` is already beyond the stop at the triggering bar.
- [ ] Consider reporting `observed_days` on session days rather than UTC+7 calendar days for
      session-based instruments (L3), or documenting the split in the gate output.
