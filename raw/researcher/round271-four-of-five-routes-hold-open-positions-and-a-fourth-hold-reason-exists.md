# Round 271 — No outcome counters exist, but the ledger position does: 4 of 5 routes are holding open positions, and there is a fourth hold reason my earlier framing missed

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence.
**Zero containers.**

## Round 270's question, and what is actually countable

Round 270 ended on: *"how much is lost at the gate versus after it is unmeasured."*
Rather than guess, I enumerated every metric a worker exposes. The complete
portfolio-related set:

```
finance_live_action_portfolio_decisions_total                    599
finance_live_action_portfolio_evidence_intervals_complete          8
finance_live_action_portfolio_evidence_intervals_required          8
finance_live_action_portfolio_last_primary_close_timestamp_seconds
finance_live_action_portfolio_pending_boundaries                   0
finance_live_action_portfolio_replay_scopes_completed / _expected  3/3
finance_live_action_layer_evaluations_total                      599
```

**There is no counter for gate passes, positions opened, or trades.** So the
gate-versus-downstream split cannot be measured from metrics either — the same class
of gap Round 265 recorded for hold reasons.

(`decisions_total` has advanced 571 → 599 since Round 264, about 12/hour, matching
the 5m decision interval. The loop is running normally.)

## What *is* observable: the ledger's position

The deployed `paper-fixed-pct` ledger carries a `position` field. Sampled now:

| route | position | side | lifetime trades | gate_passed | reason |
|---|---|---|---|---|---|
| binance BTC | **OPEN** | long | 479 | false | `entry_score_below_threshold` |
| **binance XAU** | **OPEN** | **short** | **8** | **true** | `multi_timeframe_gate_passed` |
| bybit XAUT | flat | — | 3 | false | `entry_trend_conflict` |
| exness BTC | **OPEN** | short | 485 | true | `multi_timeframe_gate_passed` |
| exness XAU | **OPEN** | short | 395 | false | **`stale_timeframe_evidence:15m`** |

**Four of five routes are holding open positions right now — including `binance XAU`,
the route with 8 lifetime trades.** It is short, and its gate passed in the same
observation.

This reframes the whole "dormant" reading. A ~99.5% hold rate does **not** mean the
system sits out of the market; it means it is **holding positions it already has**.
Closes are rare because positions are held — the `minimum_hold_decisions` guard is 36
(≈3h) and exits require the stop/take band or a flat signal. `binance XAU` is
currently participating in the market with an open short.

That further supports Round 264's de-escalation to **P3**: the route is not idle.

## A fourth hold reason, which my earlier framing missed

`exness XAU` shows **`stale_timeframe_evidence:15m`** — a reason that is **not one of
the three gates** in `decide()` (`trading_modes.rs:851/854/857`). It comes from the
`synchronization_failure()` check that runs *before* them.

Round 265 designed a "three-way hold-reason test" and Rounds 265-270 all reasoned as
though there were exactly three hold paths. **There are at least four**, and the
synchronization path is the first one evaluated. For `exness XAU` it is also the
expected one: gold CFD is closed for the weekend, so its 15m evidence is stale — the
same weekend closure Round 259 verified is not a defect.

A new append-only log records position state per round:
**`raw/researcher/position-state-samples.csv`**.

## What is proven, and what is not

Proven:

- The complete portfolio metric set above; no outcome counters exist.
- `decisions_total` 599, advancing ~12/hour, consistent with the 5m interval.
- Position state and gate state for all five 24/7-plus-CFD routes as tabulated;
  4 of 5 open.
- `stale_timeframe_evidence:15m` exists as a hold reason distinct from the three
  `decide()` gates.

Not proven, and deliberately not claimed:

- **The gate-versus-downstream split.** Still unmeasured; this round shows metrics
  cannot provide it and that position state is a partial substitute, not the answer.
- That `binance XAU`'s open short is representative. **One observation.** It shows
  the route is not idle; it says nothing about what fraction of time it holds
  exposure.
- That holding positions explains the low close count. It is consistent with it and
  is the obvious reading, but position *duration* per route was not measured.
- How many distinct hold reasons exist in total. Four are now observed; I am not
  claiming that is all of them, having just been wrong that there were three.
- Anything about PnL or Target 3.
