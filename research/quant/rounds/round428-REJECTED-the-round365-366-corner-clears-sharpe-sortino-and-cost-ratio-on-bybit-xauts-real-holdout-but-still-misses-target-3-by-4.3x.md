# Round 428 — REJECTED: the round365/366 "profitable corner" (band 0.02/0.04 + hold 288) clears Sharpe, Sortino, drawdown and cost-ratio on `bybit XAUT`'s real holdout — the strongest joint-objective reading this arc has ever measured for it — but still misses Target 3 by 4.3x and fails three day-distribution checks

Research-state iteration at round start: launcher-recorded `229` (per this
iteration's own prompt: "iteration 229 already recorded... do not call
begin-iteration"). Per round422/424-427's documented precedent, the
launcher's `iteration` counter and this file's `round<N>` sequence number
are two independent counters that have never been 1:1. This is `round428`,
continuing the sequence from round427.

## Why this round, not another status check

Round427 rejected the round365/366 "profitable corner" on `binance BTC`
using the now-unified `--daily-profit-gate` /
`--portfolio-minimum-hold-decisions` path (unblocked by round419's task 6.4
evidence), and named the remaining gap explicitly: *"`bybit XAUT` is
gate-eligible and untested this way, a candidate for a future round if
anyone wants the full three-route picture ... not expected to reverse
there"* (round427 also noted `exness XAU` is not gate-eligible at any window
measured so far, round335-336, so a holdout verdict there would not be
meaningful). This round runs exactly that named next step — a genuine open
Alpha/Portfolio-layer backtest question, not a re-check of the three
externally-blocked threads (Target 2 product decision, forward-time ~30-day
wait, Task 6.4 environment access) that rounds 411-426 already exhausted.

Priority order (`XAU` before `BTC`, per this iteration's standing
instruction): `bybit XAUT` is the gold-family route still open, so it took
priority this round over any further `BTC` work.

## Background: what round365/366/427 found

Round365 found that on `exness XAU` @300 days, combining a wider protective
band (0.02/0.04 vs deployed 0.01/0.02) with a longer hold (288 vs deployed
36 minimum-hold-decisions) produced the first positive full-window
`one_target` PnL at deployed costs in the whole arc, but flagged it as a
"searched corner, not a candidate" — no holdout score could exist for it at
the time because the hold flag conflicted with the gate flag at the CLI
level. Round366 found the same corner, applied unchanged, also turned
`binance BTC` and `bybit XAUT` positive or less-negative under the
guard-free `one_target` measure (full-window, not holdout). Round419 fixed
the CLI conflict (task 6.4). Round427 ran the first real holdout score for
this corner, on `binance BTC`: it failed cleanly, with `gross_pnl_before_costs`
negative even pre-cost. This round runs the same two-arm comparison on
`bybit XAUT`.

## Method

Two Docker containers (`--cpus=1 --memory=2g --memory-swap=3g --network
host` each — combined 2 CPU / 4 GB RAM / 2 GB swap, this iteration's
resource cap), one read-only SSH tunnel (`18086:localhost:8086`), both run
against `bybit spot XAUT/USDT 5m --days 500` (matching round338's route
identification for this instrument) so the result is directly comparable to
round427's binance-BTC test:

1. **Corner**: `--daily-profit-gate --portfolio-minimum-hold-decisions 288
   --portfolio-protective-kind fractional --portfolio-stop-value 0.02
   --portfolio-take-value 0.04`
2. **Deployed-default control, same window**: `--daily-profit-gate
   --portfolio-minimum-hold-decisions 36 --portfolio-protective-kind
   fractional --portfolio-stop-value 0.01 --portfolio-take-value 0.02`

`finance-live-action` HEAD was `ca23b05` (unchanged since round419-427; the
one intervening commit, `ca23b05` itself, only touches `scripts/`, not
`crates/finance-research` or its dependencies, so the pre-built
`finance-research-local:latest` image — built at `ca23b05`'s parent — was
reused rather than rebuilt, verified via `git show --stat`). Both runs
report `candle_count: 143998` and `holdout_candle_count: 28799` (holdout
`2026-05-26T18:40:00Z` → `2026-09-03T18:34:59.999Z`, 101 observed days,
`holdout_calendar_days: 99.997`) — confirmed identical from each run's own
`research.backtest_candle_count` log line, not assumed.

## Results

| Config | trades | trades/week | net PnL | gross PnL (pre-cost) | Sharpe | Sortino | cost÷gross | positive_day_ratio | neg-day streak | gate result |
|---|---|---|---|---|---|---|---|---|---|---|
| Corner (band 0.02/0.04, hold 288) | 23 | 1.61 | **+0.62458** | **+0.66144** | **2.046** | **3.826** | **0.056** | 0.455 | 13 | FAILED (4/12: `minimum_trades_per_week`, `positive_day_ratio`, `median_daily_pnl`, `negative_day_streak`) |
| Deployed (band 0.01/0.02, hold 36) | 59 | 4.13 | +0.13795 | +0.50480 | 0.485 | 0.764 | 0.727 | 0.426 | 9 | FAILED (8/12: `minimum_trades_per_week`, `positive_day_ratio`, `median_daily_pnl`, `negative_day_streak`, `sortino_ratio`, `sharpe_ratio`, `cost_to_gross_pnl_ratio`, and — unlike `binance BTC`'s deployed band in round427 — **also fails `minimum_trades_per_week`** at this window) |

Thresholds (from the gate's own `thresholds` block, unchanged from prior
rounds): `minimum_sharpe_ratio: 1.0`, `minimum_sortino_ratio: 1.0`,
`maximum_cost_to_gross_pnl_ratio: 0.5`, `minimum_trades_per_week: 7.0`,
`minimum_positive_day_ratio: 0.55`, `maximum_negative_day_streak: 5`.

**This is the strongest joint-objective reading this arc has measured for
the corner on any route, and the first time it clears Sharpe, Sortino,
drawdown and cost-ratio on a real gate holdout anywhere.** Both arms are
genuinely gross- and net-positive on this holdout (unlike `binance BTC` in
round427, where both arms were gross-negative) — `bybit XAUT`'s gross
positivity on this window is new evidence, not previously measured via the
gate for this exact corner. The corner clears 8 of 12 checks outright,
including both risk-adjusted-return checks (`sharpe_ratio`, `sortino_ratio`)
that the deployed band fails by a wide margin (2.046 vs 0.485; 3.826 vs
0.764) and the cost-ratio check by a factor of 13x (0.056 vs 0.727). Its
per-trade edge is also far higher: gross per trade is **+0.02876** (corner,
23 trades) against **+0.00856** (deployed, 59 trades) — a 3.4x improvement,
consistent with round364's "quality, not just cost" mechanism for this
hold+band combination.

**It still fails the same way every profitable configuration in this arc
has failed (round366's pattern, now extended to an eighth measured cell):**
`minimum_trades_per_week` at 1.61 against the 7.0 bar (a 4.3x miss, worse
than `binance BTC`'s 1.94x-equivalent corner in round365/366's original
reading and than round366's best-ever 4.57/week), and three
day-distribution checks — `positive_day_ratio` 0.455 (bar 0.55),
`median_daily_pnl` exactly 0.0 (most of the 101 days have zero closed
trades at only 23 trades total), and a 13-day `maximum_negative_day_streak`
(bar 5). The deployed control itself also fails `minimum_trades_per_week` on
this route/window (4.13/week) — unlike `binance BTC`'s deployed band in
round427, which still cleared 13.79/week — so on `bybit XAUT` at this window
neither arm clears the frequency bar, and the corner's frequency shortfall
relative to the deployed control (1.61 vs 4.13, a 61% reduction) is smaller
in absolute terms than the quality gain (Sharpe/Sortino/cost-ratio) it buys.

## Classification: REJECTED

Not promotable: the corner fails `minimum_trades_per_week` by 4.3x and three
day-distribution checks despite clearing every risk/return/cost check with
room to spare. This is not a marginal miss reachable by future tuning within
this arc's established levers — round363/365/366/427 have already shown the
hold/band levers trade frequency for quality monotonically, and extending
either further only worsens frequency. It also does not meet promotion
condition 1's spirit even though a holdout score now exists: per
round391-392, **a single holdout does not characterise a route** — this is
one data point, not the three-or-more disjoint holdouts the arc's own prior
rounds require before writing down a route's sign or quality as
established. What this round adds to the arc: `bybit XAUT` joins `exness
XAU` (round343) as a second route with gross-positive, reasonably stable
gate-holdout evidence for at least one configuration, and it is the first
route/configuration pair in the whole arc to clear both `sharpe_ratio` and
`sortino_ratio` on a real holdout. Round427's three-route picture is now
complete for the two gate-eligible routes (`binance BTC` fails pre-cost,
`bybit XAUT` fails frequency); `exness XAU` — where the corner
originated — remains structurally gate-ineligible at every window measured
so far (round335-336), so no meaningful holdout verdict is obtainable there.

## What would move this (not run this round — container budget spent)

- A second and third disjoint holdout on `bybit XAUT` (e.g. `--as-of`
  shifted back by ~100-day increments, per the disjoint-holdout technique
  round391 established) to see whether the Sharpe/Sortino/gross-positive
  reading survives outside this one window, per round391-392's own standard.
  Given every other profitable reading in this arc has alternated in sign or
  quality across windows (round339-341, round391-392), the prior from this
  arc's own evidence is that it likely will not hold uniformly — but that is
  an inference, not a measurement, and should not be reported as one.
- Whether the 13-day negative streak is concentrated in one dominant bad
  stretch (round341's single-day-dominance pattern) rather than spread —
  `--emit-trades` would answer this at zero additional containers next
  round, from a log already captured this round if retained, otherwise one
  more bounded run.

## Limits and what this does not change

- No production code, config, or deployment was touched. This is
  research-only evidence.
- Deployed production defaults (hold=36, band 0.01/0.02) are unchanged by
  this round; the control run above is provided only for a valid
  same-window comparison, not as a new finding about the deployed
  configuration on this route (its 4.13/week rate and general gate-fail
  profile were already implied by round337-343's characterization of `bybit
  XAUT`, though this is the first round to score it through the unified
  gate path specifically).
- `exness XAU` corner holdout score remains unobtainable at every window
  measured so far (round335-336 structural gate-ineligibility) —
  round427's three-route picture is complete only across the two
  gate-eligible routes.
- The three previously-identified blocked threads (Target 2 product
  decision, forward-time, Task 6.4 environment access — see round426) are
  unchanged by this round and were not re-checked; they remain outside the
  scope of a single bounded backtest round per this iteration's explicit
  instruction.

## Cleanup confirmation

Both containers were run in the foreground (not `-d`) with `--rm`, redirected
to log files under `/tmp/r428/`, and exited on their own after completion —
`docker ps -a --filter "ancestor=finance-research-local:latest"` returned
empty after both finished. The SSH tunnel was closed with `pkill -f "ssh -f
-N -L 18086"`; `ss -tlnp | grep 18086` returned nothing afterward, confirming
closure (not inferred from the wrapper's exit code). `git status --short` in
`finance-workspace` at the end of this round shows only the new/modified
research-evidence files listed below; `finance-live-action` was read-only
this round (source inspection + reuse of an existing Docker image, no
commits).
