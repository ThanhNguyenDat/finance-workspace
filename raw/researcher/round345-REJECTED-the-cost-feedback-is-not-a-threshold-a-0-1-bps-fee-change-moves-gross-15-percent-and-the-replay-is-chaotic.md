# SENSITIVITY, NOT RANDOMNESS (Round 351)

This file's "chaotically sensitive" framing can now be sharpened: **the replay is bit-for-bit
deterministic**. An `--interval 30m` run (inert on the Portfolio path — see the reference)
reproduced round 343's 5m baseline in **20/20 metric fields and every one of the 51 daily rows**,
across different rounds and wall-clock times.

So there is **no run-to-run jitter**: every difference this arc has measured between
configurations is a real response to a real input change. "Chaotic" here means **sensitivity to
inputs**, never randomness — which is exactly why round 348's threshold explanation fits, and why
repeating an identical configuration proves nothing. See `round351-DATA-ISSUE-the-interval-flag-does-not-change-the-portfolio-decision-interval-and-the-replay-is-bit-for-bit-deterministic.md`.

---

# NOT CHAOS — A THRESHOLD AT 10 BPS (Round 348)

This file called the replay *"chaotically sensitive"* because the fee ladder's net was
non-monotone. The large jumps are a **discrete gate crossing**, not chaos. Projected execution
cost is `(fee + slippage) × 2` for a reversal against a **10 bps** ceiling
(`portfolio_risk.rs:210`, strict `>` at `execution_cost.rs:243`), so: fee 5.0 → 14.0 **blocked**;
fee 4.9 → 13.8 **blocked**; **fee 3.0 → exactly 10.0 → reversals UNLOCKED**; fee 0 → 4.0 unlocked.
The two runs that land on exactly 10.0 bps by different routes (`--fee-bps 3.0` and round 344's
`--slippage-bps 0`) both give **38 trades** and nets of **+0.1442** and **+0.1315**.

What survives from this file: fee 4.9 and fee 5.0 are **both** above the ceiling yet still differ
by one trade and 14.8% of gross. That residual sensitivity is real and remains unexplained. See
`round348-DATA-ISSUE-the-cost-flags-move-reversals-across-a-10bps-gate-which-explains-rounds-344-345-and-346.md`.

---

# Round 345 — REJECTED: the cost feedback is **not** a sign-flip threshold. Cutting the fee by **0.1 bps** — 1.4% of the round trip — adds a trade, moves gross **+14.8%**, raises total cost, and makes net **worse**. The replay is chaotically sensitive to its cost parameter.

Classification: **REJECTED** — my pre-registered mechanism failed, and what replaces it is a
harder constraint on every measurement in this loop. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**, on the closest-to-break-even window.

## The mechanism Round 344 could not isolate

Round 344 showed `--fee-bps` and `--slippage-bps` change the decision stream and named the
likely path without testing it: `alpha_performance_quality`
(`finance-core/src/trading_modes.rs:589-616`). Reading it gives a sharp, testable structure —
`empirical` is **exactly 0.0** unless `realized_pnl > 0.0 && gross_profit > 0.0`, and only above
that gate does it vary continuously (win rate × clamped PF/3 × (1 − drawdown ratio)). With every
strategy a confirmed loser at deployed cost, quality collapses to `1 − confidence`, a pure
trade-count function — and a cost change should then do **nothing** until it flips some
strategy's realized PnL positive.

**Pre-registered as a partition:** `--fee-bps 4.9` — a 2% fee cut, **1.4%** of the 7 bps round
trip, far too small to flip a sign —
- gives **identical** trade count **and** identical gross → the feedback is threshold-driven and
  the `realized_pnl > 0` gate is the path;
- differs in trade count **or** gross → the feedback is continuous, and the sign gate is not the
  path.

## Result — refuted, and worse than refuted

`exness XAU`, `--days 300`, deployed band, identical holdout (2026-07-01 → 2026-08-28):

| `--fee-bps` | trades | **gross** | cost drag | **net** | Sharpe |
|---|---|---|---|---|---|
| 5.0 (deployed) | 42 | 0.33907 | 0.38445 | −0.04538 | −0.2488 |
| **4.9** | **43** | **0.38909** | **0.43965** | **−0.05056** | −0.2850 |
| 3.0 | 38 | 0.33666 | 0.19244 | **+0.14423** | **+0.9307** |
| 0.0 | 42 | 0.07177 | 0.10812 | −0.03635 | −0.2595 |

**A 0.1 bps fee cut adds a trade (+2.4%), moves gross by +14.8%, raises total cost by +14.4%
despite a lower rate, and leaves net 11.4% worse.** The prediction is refuted: the feedback is
not gated on a sign flip.

And the map from cost to outcome is **not even monotone**. Net across the fee ladder runs
**−0.04538 → −0.05056 → +0.14423 → −0.03635** at 5.0, 4.9, 3.0 and 0.0 bps. **Making execution
cheaper does not make the result better**, and the profitable point sits in the middle of the
ladder with both endpoints negative.

## What this costs the rest of the loop

The replay amplifies a **1.4%** input perturbation into a **14.8%** change in gross. That is
chaotic sensitivity, and it sets a floor on what any single-configuration measurement can mean:

- **Round 344's "zero slippage is profitable" is weaker than it looked.** So is fee 3.0 — and
  fee 0.0, a *larger* cost cut, is **not** profitable. A profitable point on a cost ladder is
  not evidence that reducing cost helps.
- **Differences of this magnitude between configurations are not interpretable.** Round 334's
  refined 500-day band grid separated its best two points by **0.018 in net**, and Round 340's
  trough shoulders by similar amounts — well inside a perturbation that a 1.4% parameter nudge
  can produce here. Round 334 already flagged that its fine ordering was not established; this
  round supplies a reason.
- It is a **cost-axis** measurement. I have not shown the same amplification on the band axis or
  the `--days` axis, so this is an indication that small differences deserve suspicion, **not**
  a proven noise bound for those axes. Round 300's `--days N` versus `N+1` probe is the
  equivalent on that axis and found the same character of problem.

The one clean, unchanged statement: **`exness XAU`'s gross is positive at every cost setting and
every window measured** (Round 343). Its *magnitude* is not stable to 15%; its *sign* has never
moved.

## What is proven, and what is not

Proven:

- `exness XAU` @300, identical holdout, deployed band: `--fee-bps 4.9` → 43 trades, gross
  0.38909, cost 0.43965, net −0.05056, Sharpe −0.2850; `--fee-bps 3.0` → 38 trades, gross
  0.33666, cost 0.19244, net **+0.14423**, Sharpe **+0.9307**.
- Against deployed: +1 trade, gross +0.050019 (+14.8%), cost +0.055200 (+14.4%) at a *lower*
  fee rate.
- Net across the fee ladder is non-monotone: −0.04538, −0.05056, +0.14423, −0.03635.
- `alpha_performance_quality` returns `empirical = 0.0` unless
  `realized_pnl > 0.0 && gross_profit > 0.0` (`trading_modes.rs:597-612`), read directly.

Not proven, and deliberately not claimed:

- **The actual feedback path.** The sign-gate hypothesis is refuted; I have **not** established
  what replaces it. Continuous variation in `confidence` through changed trade counts,
  equity-path effects on position sizing, and ordinary path dependence in the replay are all
  candidates, and **I inspected no per-strategy weights or performance records**.
- That the amplification is uniform. **One route, one window, one axis, four points.** Nothing
  here says a 1.4% nudge always produces 15%, or that it does so on other axes.
- That any of the profitable points on this ladder mean the system can be made profitable.
  Reduced cost is not achievable in these amounts, the runs are not comparable to each other for
  the reason this round establishes, and the route is gate-ineligible at every window.
- That earlier rounds' conclusions are void. Their measurements stand and their *sign-level* and
  large-magnitude conclusions are unaffected; what this round undermines is fine ranking between
  near configurations.
- Any promotion. Nothing achievable is profitable, and the measurement precision needed to claim
  a small improvement is not available.
