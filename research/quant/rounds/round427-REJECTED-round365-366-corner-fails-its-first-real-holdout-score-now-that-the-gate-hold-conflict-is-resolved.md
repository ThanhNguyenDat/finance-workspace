# Round 427 — REJECTED: the round365/366 "profitable corner" (band 0.02/0.04 + hold 288) fails its first real holdout score, now that `--daily-profit-gate` and `--portfolio-minimum-hold-decisions` no longer conflict

## Why this round, not another status check

Rounds 411-426 spent fifteen consecutive rounds re-checking the same three
externally-blocked threads (Target 2 product decision, forward-time ~30-day
wait, Task 6.4 Finance MW environment access) without new backtest evidence.
The prompt for this iteration explicitly forbids filling a round with that
kind of out-of-scope status check and requires either a genuine new
Alpha/Portfolio-layer test or a brief NO-CHANGE/NEEDS-MORE-RESEARCH
conclusion. Rather than re-read the same three blockers, this round looked
for a genuinely open, in-scope Portfolio-layer question and found one:
**round419 already demonstrated that `--daily-profit-gate` and
`--portfolio-minimum-hold-decisions` no longer conflict** (unified path
merged at `origin/main` `7d579cf`, unchanged through today's `ca23b05`). That
directly unblocks the promotion-condition-1 gap round365 identified for its
"profitable corner" candidate — until now, nobody had actually run it.

## Background: what round365/366 found and why it stalled

Round365 (2026-08-31) found that on `exness XAU` @300 days, combining a wider
protective band (0.02/0.04 vs deployed 0.01/0.02) with a longer hold
(288 vs deployed 36 minimum-hold-decisions) produced the **first positive
full-window `one_target` PnL at deployed costs** in the whole arc (+1.17395),
with the two levers composing super-additively rather than being the same
mechanism measured twice. Round365 immediately flagged it as "a searched
corner, not a candidate": trades 1.94/week (a 3.6x miss of the 7.0/week
Target 3 bar), from a ~16-cell search on one window (classic overfitting
shape), and — critically — **no holdout score could exist for it**, because
`--portfolio-minimum-hold-decisions` conflicted with `--daily-profit-gate` at
the CLI level. Round365 named the unblocking step explicitly: "a holdout
score for the combined configuration (needs a code change) ... or the same
corner surviving on a route or window it was not selected from."

Round366 tested the second half of that bar — transfer to routes the corner
was never selected from — and found it: applied unchanged, the corner turned
`binance BTC` @500 from -4.74869 to **+0.37527** (a fresh, unselected route,
positive), and `bybit XAUT` @500 from -1.57738 to -0.28493 (improved, still
negative). Round366 was explicit that transfer evidence is "not a holdout" —
promotion condition 1 was still unmet.

That was 61 rounds ago. Task 6.4 of `portfolio-measurement-integrity` (a
promoted OPS change, since archived) evidently unified the two flags into one
replay path along the way: `daily_profit_gate.rs`'s
`evaluate_real_portfolio_with_funding_and_continuity_and_hold` now takes both
the `selected_portfolio_rule.simulation` (which carries protective
kind/stop/take) *and* `--portfolio-minimum-hold-decisions` together
(`crates/finance-research/src/main.rs:654-666`, verified by reading the
source directly this round). Round419 confirmed this works for hold=72 alone.
This round is the first to run the actual round365/366 corner — band **and**
hold together — through that unified path.

## Method

Two Docker containers (`--cpus=2 --memory=4g --memory-swap=6g --network
host`, per the repository's backtest-tooling rule), one read-only SSH tunnel
(`18086:localhost:8086`), both run against `binance BTC perpetual_future 5m
--days 500` so the result is directly comparable to round366's binance-BTC
transfer test and round419's control:

1. **Corner**: `--daily-profit-gate --portfolio-minimum-hold-decisions 288
   --portfolio-protective-kind fractional --portfolio-stop-value 0.02
   --portfolio-take-value 0.04`
2. **Deployed-default control, same window**: `--daily-profit-gate
   --portfolio-minimum-hold-decisions 36 --portfolio-protective-kind
   fractional --portfolio-stop-value 0.01 --portfolio-take-value 0.02`
   (36/0.01/0.02 are the live production values —
   `finance-core/src/trading_modes.rs:113`
   `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS = 36`;
   `finance-api/src/deployment_rules.rs:58-59` `PORTFOLIO_STOP_VALUE = 0.01`,
   `PORTFOLIO_TAKE_VALUE = 0.02`)

Both runs report `candle_count: 143998` and `holdout_candle_count: 28799`
(holdout `2026-05-26T18:10:00Z` → `2026-09-03T18:04:59.999Z`, 101 observed
days) — confirmed identical, not assumed, per the playbook's own "check
`candle_count`" rule. Running both arms in the same round on the same window
avoids the round-361/365 drift-control trap.

## Results

| Config | trades | trades/week | net PnL | gross PnL (pre-cost) | Sharpe | Sortino | positive_day_ratio | gate result |
|---|---|---|---|---|---|---|---|---|
| Corner (band 0.02/0.04, hold 288) | 52 | 3.64 | -0.74235 | **-1.86562** | -2.0126 | -2.7837 | 0.4554 | FAILED (7/12: `minimum_trades_per_week`, `positive_day_ratio`, `median_daily_pnl`, `negative_day_streak`, `sortino_ratio`, `sharpe_ratio`, `gross_pnl_positive`) |
| Deployed (band 0.01/0.02, hold 36) | 197 | 13.79 | -2.62887 | -1.47495 | -6.4197 | -6.9318 | 0.3564 | FAILED (7/12: `positive_day_ratio`, `median_daily_pnl`, `negative_day_streak`, `sortino_ratio`, `sharpe_ratio`, `gross_pnl_positive`, `cost_to_gross_pnl_ratio`) |

The corner's full-window `one_target` positivity (round366: +0.37527 over the
whole 500-day window) **does not survive the honest 101-day out-of-sample
holdout**: `gross_pnl_before_costs` is -1.86562, negative even before any
cost is charged — the same failure mode round336-337 documented for the
deployed band on this exact route (`gross_pnl_positive` fails). The full
window's positive reading was carried by the train/validation portion, not
the holdout — precisely the risk round365 flagged when it called this "what
overfitting looks like" from a ~16-cell search.

The corner does buy a real reduction in *net* loss (-0.74 vs -2.63, 71.8%
smaller) and in Sharpe/Sortino severity, exactly the "trades less, loses
less" pattern round366's synthesis already established for every profitable
configuration in this arc — but it does so by cutting trade frequency 74%
(13.79 → 3.64/week), which **fails `minimum_trades_per_week` outright**
(3.64 vs the 7.0 bar) — a check the deployed config still passes at this
window. And its gross is 26.5% *worse* than deployed (-1.86562 vs -1.47495),
consistent with round367's finding that "wider is better per trade" does not
generalise to `binance BTC` (a widening that helped `exness XAU`'s per-trade
gross cost `binance BTC` per-trade gross there too).

## Classification: REJECTED

Promotion condition 1 (defensible OOS/holdout evidence) is no longer
structurally unmeetable for this configuration — that blocker is resolved.
But the holdout evidence itself is negative: gross is negative before costs,
net is still a loss, and the configuration fails Target 3's frequency floor
on the one route (`binance BTC`) that the deployed band still clears at this
window. This closes the round365/366 "corner" as a candidate on `binance
BTC` with real OOS evidence instead of the full-window `one_target` reading
that could only ever be suggestive. Not tested this round: `exness XAU`
(where the corner originated) or `bybit XAUT` through the unified holdout
path — `exness XAU` is not gate-eligible at any window measured so far
(round335-336, non-5m interval continuity failures), so a holdout verdict
there would not be meaningful; `bybit XAUT` is gate-eligible and untested
this way, a candidate for a future round if anyone wants the full three-route
picture, but the container/round budget was spent on the two-arm
route/window-matched comparison above and the direction (corner fails
pre-cost on holdout) already matches every other profitable-configuration
finding in this arc (round366's six-for-six pattern), so it is not expected
to reverse there.

## Limits and what this does not change

- No production code, config, or deployment was touched. This is
  research-only evidence.
- Deployed production defaults (hold=36, band 0.01/0.02) are unchanged by
  this round; the control run above is provided only for a valid same-window
  comparison, not as a new finding about the deployed configuration (its
  gate-fail profile matches round336-337/419's prior characterization of
  `binance BTC`).
- `exness XAU` and `bybit XAUT` corner holdout scores remain untested via the
  unified gate path — the corner is REJECTED specifically for `binance BTC`;
  extending to the other two routes would need its own round if the question
  is judged worth the container budget later.
- The three previously-identified blocked threads (Target 2 product
  decision, forward-time, Task 6.4 environment access — see round426) are
  unchanged by this round and were not re-checked; they remain outside the
  scope of a single bounded backtest round per this iteration's explicit
  instruction.

## Update — round428 (2026-09-04)

Round428 ran the `bybit XAUT` half of the three-route picture this round
left open. Result there is materially different from `binance BTC`: both
arms are gross-positive, and the corner clears `sharpe_ratio`,
`sortino_ratio` and `cost_to_gross_pnl_ratio` outright (Sharpe 2.046,
Sortino 3.826, cost÷gross 0.056) — the strongest joint-objective reading
this arc has measured for this corner anywhere. It still fails
`minimum_trades_per_week` by 4.3x and three day-distribution checks, so the
overall REJECTED verdict for the corner as a candidate is unchanged, and
this round's `binance BTC` failure mode (negative gross pre-cost) does not
generalise to the corner's failure mode on every route — see round428 for
the full comparison. `exness XAU` remains gate-ineligible at every window
measured (round335-336), so the three-route picture is complete only across
the two gate-eligible routes.

## Cleanup confirmation

Both containers were started `-d --rm` and exited on their own after
completion; `docker ps -a --filter "ancestor=finance-research-local:latest"`
returned empty before the round ended. The SSH tunnel was closed with `pkill
-f "ssh -f -N -L 18086"`; `ss -tlnp | grep 18086` returned nothing
afterward, confirming closure (not inferred from the wrapper's exit code, per
the playbook's own caution about that command's exit-code unreliability).
`git status --short` in `finance-workspace` at the end of this round shows
only the new/modified research-evidence files listed below; `finance-live-action`
was read-only this round (source inspection + Docker image build from
existing `HEAD`, no commits).
