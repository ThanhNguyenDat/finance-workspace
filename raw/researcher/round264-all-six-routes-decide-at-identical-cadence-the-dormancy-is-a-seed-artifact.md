# Round 264 — All six routes construct Portfolio decisions at an identical cadence. The "dormancy" is a seed artifact, and my P2 de-escalates.

Classification: **NO-CHANGE**. Read-only production `/metrics` plus local code
inspection. **Zero containers.** The finding raised in Round 262 is **de-escalated,
not closed** — details below.

## The step Round 263 named

Round 263 ended with: *"Whether they are retained in a countable form in the
checkpoint or only logged was **not** determined this round — that is the first
thing the next round should check."*

**They are not countable.** `finance_live_action_portfolio_decisions_total` is the
only decision metric and it carries **no reason label** (`metrics.rs:1173-1175`); no
`reason` label exists anywhere in that file. So the three-way hold-reason test
Round 263 designed cannot be run from metrics.

But the counter is still decisive for a different split, because of **where** it
increments (`trading_api.rs:1708`):

```rust
let decision = pending.evidence.decide(close_time);
let scores  = pending.evidence.role_scores();
let target  = inner.portfolio_construction.construct(decision.clone());
inner.portfolio_decisions_total = inner.portfolio_decisions_total.saturating_add(1);
```

It increments **once per synchronized Portfolio primary, hold or trade alike** —
and only after the `is_synchronized` guard at `trading_api.rs:1694-1700`. So it
separates "the decision loop is not running / not synchronizing" from "the loop
runs and resolves to hold".

## The measurement

Scraped read-only from each worker's own `:8002/metrics`:

| route | evidence intervals complete / required | **decisions_total** |
|---|---|---|
| exness XAU | **8 / 8** | 342 |
| **binance XAU** (8 lifetime trades) | **8 / 8** | **571** |
| **bybit XAUT** (3 lifetime trades) | **8 / 8** | **571** |
| binance BTC | 8 / 8 | 571 |
| exness BTC | 8 / 8 | 571 |
| bybit BTC | 8 / 8 | 571 |

**Five routes sit at exactly 571 — including both "dormant" ones.** `exness XAU`'s
342 is lower for the expected reason: gold CFD is closed for the weekend, so fewer
5m primaries closed.

**Evidence synchronization is 8/8 on every route**, the two dormant ones included.

## What this settles

The two routes are **not dormant in live operation**. They construct Portfolio
decisions at exactly the cadence of the healthy BTC routes, with fully synchronized
evidence. Over that same live window they produced 1 close each against the BTC
routes' 3-4 — a ratio consistent with the long-run 7.60 vs 9.14/week that Round 261
measured, and well inside the noise Round 261 established.

So Round 263's three-way test resolves without needing hold reasons: **the replay
path is not costing live decisions, and synchronization is not either.** The loss
that produced 8 and 3 *lifetime* trades is confined to the **historical seed**,
which Round 262 measured at 14 days and 2 days against a configured 365.

## My P2 de-escalates — stated plainly, because I raised it

Round 262 filed this as **P2, possibly P1 "if it affects live decisions, which is
not established"**. It is now established that it **does not** affect live decision
construction or synchronization. The correct severity is **P3**: a historical
seeding inconsistency that leaves two routes with a near-empty backtest ledger and a
stale backfill cluster, with no demonstrated live impact.

**It is de-escalated, not closed**, for one specific reason: the seed feeds the
reweighting formula, and the two affected routes carry blended
`candle_momentum`/`rsi_mean_reversion` weights where the healthy route carries a
single mechanism at 1.0 (Round 263). That is a real propagation path from seed to
live behaviour. What this round shows is that **no harm is visible in the decision
cadence** — not that no harm exists.

## What is proven, and what is not

Proven:

- No `reason` label exists on any metric in `crates/finance-api/src/metrics.rs`;
  `portfolio_decisions_total` is the only decision counter (`metrics.rs:1173-1175`).
- It increments once per synchronized primary regardless of outcome
  (`trading_api.rs:1708`), behind the `is_synchronized` guard at 1694-1700.
- Live counters: 571 on five routes including both "dormant" ones, 342 on
  `exness XAU`; `evidence_intervals_complete == required == 8` on all six.

Not proven, and deliberately not claimed:

- **Which hold gate fires, or in what proportion.** The metric has no reason label,
  so Round 263's designed test remains unrun. The remaining route to it is the
  application logs, which were not read this round.
- That the blended weights are harmless. They are shown not to suppress decision
  *construction*; their effect on decision *outcomes* is unmeasured.
- That `exness XAU`'s 342 is fully explained by the weekend. It is consistent with
  it and with that route's 63.7% bar coverage (Round 260), but 342/571 = 0.60
  against a 0.637 coverage figure is an approximate match, not a verified one.
- Any cause for the short seed spans or the stalled backfill. Round 262's
  observation and Round 263's four eliminations both stand; the cause is still
  unknown and still belongs to Codex.
- Anything about PnL. Not examined.
