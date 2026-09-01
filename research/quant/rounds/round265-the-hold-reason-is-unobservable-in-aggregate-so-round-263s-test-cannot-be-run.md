# Round 265 — The hold reason is unobservable in aggregate, so Round 263's decisive test cannot be run at all; and holding is the normal state on every route

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence plus local
code inspection. **Zero containers.**

## The last route to Round 263's test, and it is closed

Round 264 established the reason is not in metrics and left one path open: *"the
remaining route to it is the application logs, which were not read this round."*

**The reasons never reach the logs.** Over six hours of `binance XAU` worker output:

```
grep -c 'entry_trend_conflict|entry_score_below_threshold|trend_score_below_threshold'  ->  0
grep -c 'gate_reason'                                                                   ->  0
```

The only place the reason exists is `inner.signal_states`
(`trading_api.rs:1803-1821`), which stores `gate_reason`, `gate_passed`,
`entry_score` and `trend_score` for the **latest evaluation only**, inside the
Redis checkpoint.

So Round 263's designed three-way test — *count hold reasons per route and compare* —
**cannot be run from any production surface**. Not from `/metrics` (no `reason`
label anywhere in `metrics.rs`), not from logs (never emitted), and not from the
checkpoint (one evaluation, not a count). **This is an observability gap, not a
shortage of effort.**

## And sampling the snapshot does not substitute for it

I read the checkpoint twice, minutes apart, intending two independent samples. The
second read returned **byte-identical** `entry_score`/`trend_score`/`gate_reason`
for all three overlapping routes — the checkpoint had not been rewritten in between.

**So this round has n = 1 per route, not n = 2.** I am recording that because I
set out to double the sample and did not.

## What the single snapshot does show — and it points away from Round 263

| route | health | gate_reason | entry | trend |
|---|---|---|---|---|
| binance BTC | healthy | `entry_trend_conflict` | −0.1707 | +0.1759 |
| exness BTC | healthy | `entry_score_below_threshold` | −0.0405 | −0.0693 |
| binance XAU | "dormant" | `entry_score_below_threshold` | +0.0722 | −0.3476 |
| bybit XAUT | "dormant" | `entry_trend_conflict` | +0.1038 | −0.5023 |

**All four are holding, and both gate types fire on healthy and "dormant" routes
alike.** Opposite-signed entry and trend appear on 3 of 4 routes including a healthy
one. There is **no signature separating the two groups** in this observation.

## Holding is the normal state everywhere, so "they hold a lot" was never diagnostic

Combining Round 264's decision counters with the live closes:

| route | closes / 571 decisions | gate pass | **hold rate** |
|---|---|---|---|
| binance BTC | 4 | 0.70% | **99.30%** |
| exness BTC | 3 | 0.53% | **99.47%** |
| bybit BTC | 3 | 0.53% | **99.47%** |
| binance XAU | 1 | 0.18% | **99.82%** |
| bybit XAUT | 1 | 0.18% | **99.82%** |

The healthy routes hold **99.3–99.5%** of the time. The difference between groups
is 3-4 events against 1 — Poisson noise, consistent with Rounds 261 and 264.

## Consequence for the Round 263 hypothesis

Round 263 proposed that blended `candle_momentum`/`rsi_mean_reversion` weights drive
role scores into cancellation or sign conflict on the two affected routes, and
explicitly declined to call it the cause. **The only obtainable evidence gives it no
support**: the healthy `binance BTC` route shows the same opposite-sign signature at
the same instant, and both hold gates fire on both groups.

The hypothesis is **not refuted** — one observation cannot refute it any more than
it could confirm it. It is **untestable with current instrumentation**, which is a
different and more useful thing to know.

## What would unblock it — named, not implemented

A counter labelled by reason, e.g.
`finance_live_action_portfolio_holds_total{reason="entry_trend_conflict"}`, or
emitting the reason on the existing decision path so it can be counted from logs.
Either makes Round 263's test a single scrape. **Not proposed as work and not
implemented** — recorded so the next round does not re-derive the same dead end.

This is **P3**, alongside Round 262's de-escalated seeding item.

## What is proven, and what is not

Proven:

- Zero occurrences of the three reason strings and of `gate_reason` in six hours of
  worker logs.
- The reason exists only in `signal_states` (`trading_api.rs:1803-1821`), latest
  evaluation only.
- Two checkpoint reads minutes apart returned identical values, so repeated
  sampling within a round does not yield independent observations.
- The four-route snapshot above.
- Hold rates of 99.30–99.82% across all five 24/7 routes, from Round 264's counters.

Not proven, and deliberately not claimed:

- **Anything about the distribution of hold reasons.** n = 1 per route. The table
  above is one instant and is not evidence about typical behaviour.
- That Round 263's weight hypothesis is wrong. It is unsupported by this
  observation and untestable with current instrumentation; those are not the same
  as refuted.
- That the checkpoint never refreshes fast enough to sample. Two reads in one round
  were identical; a longer-spaced series was not attempted and might work.
- Any cause for the short seed spans or the stalled backfill. Rounds 262 and 263
  stand unchanged.
- Anything about PnL or Target 3.
