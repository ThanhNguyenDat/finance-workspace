# Round 263 — Eliminated: replay window, data depth, data continuity. What is left is a feedback loop I cannot untangle from a snapshot

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection plus read-only
production queries. **Zero containers.** Investigation only — nothing applied.

Round 262 deferred the code investigation to Codex. That was the wrong split: under
the Claude role note in `.agents/rules/coding-and-verification.md`, **investigation
is my lane and only implementation is Codex's.** This round does the investigation
Round 262 should have done.

## Four candidate causes eliminated

**1. The replay window is uniform and correct.**
`crates/finance-api/src/historical_replay.rs:177` computes it as

```rust
let from_time = to_time - chrono::Duration::days(days.max(1));
```

with `days = cfg.historical_replay_days` (`main.rs:854`), and
`HISTORICAL_DEMO_REPLAY_DAYS=365` was read narrowly from both workers in Round 262.
Same window, same code path, every route.

**2. The replay reported complete on all three routes.**
`historical_replay_completed_scopes` is 19/19, 19/19 and 27/27; no interval stayed
pending. The retry loop at `main.rs:862-905` exits only when
`pending_replay_intervals()` is empty.

**3. Data depth is sufficient.** `binance XAU` has 75 232 5m bars from 2025-12-11
(~254 days inside the replay window); `bybit XAUT` has 145 481 from 2025-04-11
(the full 365 days).

**4. Data continuity is clean — and cleaner on the dormant routes than the healthy
one.** Gap markers on 5m since 2025-12-11:

| route | bars | gap-marked | gap candles |
|---|---|---|---|
| binance XAU | 75 236 | **0** | **0** |
| bybit XAUT | 75 333 | **0** | **0** |
| exness XAU | 50 530 | 185 | 24 602 |

The route that seeds correctly is the one **with** gap markers (weekend closures,
correctly recorded); the two that seed almost nothing have perfectly continuous
data. Continuity is not the cause, and this also disposes of the idea that the
stalled `pending_history_backfill` cluster on `binance XAU` reflects missing bars —
those bars are present and unmarked in Timescale.

## What the code says about deciding, and where suspicion now points

`PortfolioConstructionState::decide` (`crates/finance-core/src/trading_modes.rs:842-857`)
holds on **three** conditions:

```rust
if entry_score.abs() < self.policy.minimum_role_score { return self.hold("entry_score_below_threshold", …) }
if trend_score.abs() < self.policy.minimum_role_score { return self.hold("trend_score_below_threshold", …) }
if entry_score.is_sign_positive() != trend_score.is_sign_positive() { return self.hold("entry_trend_conflict", …) }
```

`minimum_role_score = 0.1` on all three routes. The deployed `strategy_weights`
differ sharply:

| route | strategy_weights | trades |
|---|---|---|
| exness XAU | `candle_momentum 1.000` (single non-zero) | 395 |
| binance XAU | `candle_momentum 0.373`, **`rsi_mean_reversion 0.627`** | 8 |
| bybit XAUT | `candle_momentum 0.164`, **`rsi_mean_reversion 0.836`** | 3 |

Round 257 established, against a pre-committed control, that `candle_momentum` and
`rsi_mean_reversion` respond to trend magnitude in **opposite directions**. Blending
them at comparable weights is exactly the configuration that drives the weighted
role scores toward zero and their signs into disagreement — tripping the first,
second or third hold gate. The mature route runs a **single** mechanism at 1.0 and
has no such cancellation. Round 207's production payload shows the shape directly:
`candle_momentum +0.381` alongside `rsi_mean_reversion −0.045` on one real trade.

## Why I am not calling this the cause

`strategy_weights` are **outputs** of the reweighting formula, fed by the simulated
ledgers. Those ledgers hold 7 and 1 seed trades on the two dormant routes. So the
blended weights may be a **symptom** of the empty seed rather than its cause:

```
short seed → almost no ledger evidence → blended/degenerate weights
   → role scores cancel or conflict → few decisions → almost no ledger evidence
```

**A snapshot cannot establish the direction of that loop**, and I am not going to
present a mechanism that fits as though it were measured. Round 252, Round 254 and
Round 261 were each cases where I read a fitting story as a result; this is the same
shape and it gets the same treatment.

## The decisive test, named precisely

Count the **hold reasons** actually emitted per route over a fixed window —
`entry_score_below_threshold`, `trend_score_below_threshold`,
`entry_trend_conflict` — and compare the dormant routes against `exness XAU`.

- If `entry_trend_conflict` dominates on the dormant routes, the opposing-weights
  mechanism is confirmed and the fix is about weight composition.
- If the threshold gates dominate instead, it is score magnitude, not sign conflict.
- If hold reasons look similar across all three routes, the gate is **not** where the
  decisions are lost and the replay path itself is at fault.

These strings are emitted at `trading_modes.rs:851/854/856`. Whether they are
retained in a countable form in the checkpoint or only logged was **not** determined
this round — that is the first thing the next round should check.

## Finding status for Codex — unchanged from Round 262, better scoped

Still **P2**, still **not applied**. Round 262's observation stands; this round
removes four candidate causes and localises the remaining suspicion to the
interaction between replay seeding and weight reweighting. **No fix direction is
recommended yet**, because a fix aimed at the weights would be wrong if the seed is
the cause, and vice versa.

## What is proven, and what is not

Proven:

- The replay window computation and its single configuration source, cited above.
- Replay completion on all three routes; no pending intervals.
- Bar counts and zero gap markers on both dormant routes; 185 markers / 24 602 gap
  candles on `exness XAU`.
- The three hold conditions and `minimum_role_score = 0.1`, cited to line.
- The deployed `strategy_weights` per route.

Not proven, and deliberately not claimed:

- **That opposing strategy weights cause the low decision rate.** It fits, it is
  code-grounded, and it is untested. The confound above is real.
- The direction of the seed ↔ weights loop. Not determinable from a snapshot.
- That the replay path is exonerated. Eliminating window, completion, depth and
  continuity does not exonerate what happens **inside** the replay.
- Any cause for the stalled `pending_history_backfill` on `binance XAU`. Round 262
  recorded it; this round only shows it is not explained by missing or ungapped
  bars.
- Anything about PnL or Target 3 on these routes.
