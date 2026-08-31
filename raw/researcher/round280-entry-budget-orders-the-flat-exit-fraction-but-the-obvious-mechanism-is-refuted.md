# Round 280 — Entry weight budget orders the flat-exit fraction exactly across three routes — and the mechanism I reached for is refuted by the code

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection plus read-only
production evidence. **Zero containers.**

## Round 279's open question

Round 279 closed the flat-time mechanism and left one thing open: **what sets the
close-reason mix on same-volatility routes?** `binance BTC` has 14.0% flat exits and
`bybit BTC` 5.8%, at volatilities of 0.14371% and 0.14406% — a 2.4x difference the
protective band cannot explain.

## The correlation

| route | **entry weight budget** | minimum_role_score | stop_loss | take_profit | **target_flat** |
|---|---|---|---|---|---|
| binance BTC | **0.3114** | 0.1 | 59.0% | 27.1% | **14.0%** |
| exness BTC | **0.3063** | 0.1 | 60.5% | 24.3% | **15.2%** |
| **bybit BTC** | **0.1763** | 0.1 | 63.7% | 30.5% | **5.8%** |

The two routes with an entry budget near 0.31 sit at 14-15% flat exits; the route
with a budget **43% smaller** sits at **5.8%**. The ordering is exact, and
`minimum_role_score` is identical (0.1) on all three, so the *effective* entry
threshold is 32.1%, 32.6% and **56.7%** of each route's attainable maximum.

`strategy_weights` do **not** order this way — `exness BTC` is 0.353/0.647 while
`binance BTC` is 0.521/0.479, yet both land at 14-15%. So the composition of
strategies is not what separates them; the entry interval-weight budget is.

## The mechanism I reached for, and why it fails

The natural story: a small entry budget makes `entry_score` fail the 0.1 threshold
more often, so the Portfolio holds instead of acting, so positions run to the
protective band instead of being flattened.

**The code refutes it.** `hold()` (`trading_modes.rs:1100-1112`) returns
`exit: false`, and `construct()`'s non-passing branch returns
`self.current_target.clone()` — so a failed threshold **leaves an open position
open**. It cannot produce a `target_flat` close.

`target_flat` is emitted at `trading_modes.rs:1764` via `apply_target`, which closes
only when `target.position == Flat` while a position exists (`1991-1995`). The target
becomes Flat only through `decision.exit == true` or `force_flat()` — and
`force_flat` is documented in the source as a **safety gate**, i.e. the risk layer,
not the decision threshold.

**So the entry budget correlates with the flat-exit fraction through a path I have
not identified, and the obvious path is closed.** I checked before claiming, which is
the whole point.

## What is proven, and what is not

Proven:

- Entry weight budgets 0.3114 / 0.3063 / 0.1763 against flat-exit fractions 14.0% /
  15.2% / 5.8%, ordering exactly, with `minimum_role_score` identical at 0.1.
- `strategy_weights` do not order with the flat-exit fraction.
- `hold()` sets `exit: false`; the non-passing branch of `construct()` preserves the
  current target; `target_flat` requires the target to become Flat while a position
  is open.

Not proven, and deliberately not claimed:

- **Any causal link between entry budget and flat exits.** The ordering is exact but
  it is **three points**, and the mechanism that would explain it is refuted. Three
  points ordering correctly is weak evidence on its own — Rounds 252, 254, 261, 273
  and 275 are all cases where a tidy small-n pattern needed qualifying later.
- That the risk layer is responsible. `force_flat` is *a* path to a flat target and
  `risk_rejected_counts` exists in the `portfolio_execution` output, but I did **not**
  read those counts per route, and no evidence connects them to this correlation.
- Where `decision.exit == true` originates. I did not locate it; `hold()` is not it.
  That is the first concrete thing to find next.
- That entry budget matters for anything else. Rounds 269 and 270 both found
  entry-budget arguments failing against the samples; this is a third context and it
  is unresolved rather than supportive.
