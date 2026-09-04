# Round 430 — REJECTED: a third disjoint `bybit XAUT` holdout closes round429's own named open question — the round365/366 corner beats the deployed band on net PnL and Sharpe in 3 of 3 disjoint windows now tested, but the corner still never clears Target 3 frequency and only one of the three windows is gate-eligible

Research-state iteration at round start: launcher-recorded `231` per this
iteration's own prompt ("iteration 231 was already recorded... do not call
begin-iteration"); the `quant-research-state state` tool itself still read
`230` at round start. Per round422/424-429's documented precedent, the
launcher's `iteration` counter and this file's `round<N>` sequence number are
two independent counters that have never been 1:1 — this is `round430`,
continuing the sequence from round429.

## Why this round, not another status check

Round429 ran the disjoint-holdout robustness check it inherited from
round428 and found the corner's single strong reading (round428) reversed
sign on an adjacent, non-overlapping window. It then named its own next
step explicitly: *"The corner's better-than-deployed relative ordering on
both windows measured so far (round428 and this round) is itself a
candidate worth a dedicated round: does the corner beat the deployed band
on every window regardless of either arm's absolute sign? Two windows
agree; that is not yet the three-or-more the arc's own standard
(round391-392) requires before calling a pattern established."* This round
runs exactly that named, in-scope Portfolio-layer test — a third disjoint
`bybit XAUT` holdout, shifted back another ~65 days from round429's
holdout start — not a re-check of the three externally-blocked threads
(Target 2 product decision, forward-time ~30-day wait, Task 6.4 environment
access) that rounds 411-426 already exhausted and that this iteration's
prompt explicitly excludes from counting as round work.

## Method

Same mechanism as round429: `--as-of` shifts the replay cutoff to exactly
round429's own holdout start (`2026-03-05T17:00:00Z`), giving a third,
non-overlapping (to within one candle bucket, see below) holdout window.
Two Docker containers (`--cpus=1 --memory=2g --memory-swap=3g --network
host` each — 2 CPU / 4 GB RAM / 2 GB swap total, this iteration's resource
cap), one read-only SSH tunnel (`18086:localhost:8086`), both run against
`bybit spot XAUT/USDT 5m --days 500 --as-of 2026-03-05T17:00:00Z`:

1. **Corner**: `--daily-profit-gate --portfolio-minimum-hold-decisions 288
   --portfolio-protective-kind fractional --portfolio-stop-value 0.02
   --portfolio-take-value 0.04`
2. **Deployed-default control, same window**: `--daily-profit-gate
   --portfolio-minimum-hold-decisions 36 --portfolio-protective-kind
   fractional --portfolio-stop-value 0.01 --portfolio-take-value 0.02`

`finance-live-action` HEAD was unchanged at `ca23b05` (verified via
`git rev-parse HEAD` at round start, same as round427-429); the pre-built
`finance-research-local:latest` image from round428/429 was reused
(confirmed present via `docker images`, no source changes since). Containers
were launched `-d --rm` with `docker logs -f <name> > /tmp/r430/<name>.log`
started concurrently (not attached-and-waited), per round124-125's
documented `--rm` log-loss trap.

## Window identity — shorter partial window than round429, and a tiny overlap, both disclosed

Both runs report identical `candle_count: 94549`, `train_candle_count:
56729`, `validation_candle_count: 18910`, `holdout_candle_count: 18910`,
`holdout_start: 2025-12-30T01:15:00.000Z`, `holdout_end:
2026-03-05T17:04:59.999Z`, `observed_days: 67`, `holdout_calendar_days:
65.660` — confirmed from each run's own `research.backtest_candle_count`
log line and each run's `metrics` block, not assumed.

Two honesty notes, checked rather than assumed, per round360's "check
`candle_count`, don't assume" rule and round391's "verify no overlap, don't
assume it" standard:

- **Shorter partial window, as round429 anticipated.** `--days 500` at this
  `--as-of` yields only 94,549 candles (~328 days of train+validation+holdout
  combined) against round429's 118,185 and round428's 143,998 — history
  depth shrinks every time the cutoff moves earlier, exactly the constraint
  round429 flagged ("a third disjoint holdout of the same length may hit a
  shorter partial window still — check `candle_count` before trusting it").
  Consequence: this holdout (65.66 calendar days) is shorter than round429's
  (82.07) and round428's (99.997) — **only round428's window clears
  `minimum_holdout_days` (90)**; this round's and round429's both fail it
  structurally. Every number below is a relative-ranking measurement
  (round335's established distinction), not a gate pass/fail verdict.
- **Near-disjoint, not exactly disjoint.** This holdout's `holdout_end`
  (`2026-03-05T17:04:59.999Z`) is five minutes **after** round429's
  `holdout_start` (`2026-03-05T17:00:00Z`) — the single 5-minute candle
  bucket `17:00:00–17:04:59.999` is counted in both holdouts, the same
  1-candle-bucket artifact of `--as-of` boundary inclusivity round429 found
  at the round428/429 boundary. Negligible at this sample size (1 of 18,910
  holdout candles, 0.005%), reported exactly rather than rounded to zero.

## Results

| Config | trades | trades/week | net PnL | gross PnL (pre-cost) | Sharpe | Sortino | cost÷gross | positive_day_ratio | neg-day streak | checks passed | gate result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Corner (band 0.02/0.04, hold 288) | 27 | 2.878 | **+0.14145** | **+0.72581** | **+0.572** | **+1.001** | 0.805 | 0.507 | 8 | 6/12 | FAILED (`minimum_holdout_days`, `minimum_trades_per_week`, `positive_day_ratio`, `negative_day_streak`, `sharpe_ratio`, `cost_to_gross_pnl_ratio`) |
| Deployed (band 0.01/0.02, hold 36) | 68 | 7.249 | −0.14608 | +0.27362 | −0.528 | −0.794 | 1.534 | 0.478 | 4 | 6/12 | FAILED (`minimum_holdout_days`, `positive_day_ratio`, `median_daily_pnl`, `sortino_ratio`, `sharpe_ratio`, `cost_to_gross_pnl_ratio`) |

Both arms pass `holdout_interval_continuity`, `daily_drawdown`,
`total_drawdown`, `gross_pnl_positive` (identical four checks). Checks-passed
count is **tied 6-6** on this window (unlike round428, where the corner
passed 8/12 against deployed's 4/12) — but the two arms fail on different
axes: the corner passes `sortino_ratio` and `median_daily_pnl` where
deployed fails them; deployed passes `minimum_trades_per_week` and
`negative_day_streak` where the corner fails them. Deployed clears the
7.0/week bar on this window (7.249) — the first time in this three-window
series either arm has cleared Target 3 outright, and it is the deployed
control, not the corner.

## The named question, now answered: 3 of 3 windows agree on relative ordering

Collecting all three disjoint `bybit XAUT` holdouts measured for this exact
corner (round428, round429, this round) on **net PnL** and **Sharpe**, the
two metrics that most directly capture "did the extra hold/band buy
quality":

| Window (holdout start → end) | Calendar days | Corner net | Deployed net | Corner Sharpe | Deployed Sharpe | Corner better? |
|---|---|---|---|---|---|---|
| A (round428): 2026-05-26 → 2026-09-03 | 99.997 | +0.6246 | +0.1380 | +2.046 | +0.485 | **yes** |
| B (round429): 2026-03-05 → 2026-05-26 | 82.07 | −0.8057 | −0.8166 | −3.223 | −3.428 | **yes** (less negative) |
| C (round430, this round): 2025-12-30 → 2026-03-05 | 65.66 | +0.1415 | −0.1461 | +0.572 | −0.528 | **yes** |

**The corner beats the deployed band on both net PnL and Sharpe in 3 of 3
disjoint windows**, regardless of either arm's own absolute sign (window A
both positive, window B both negative, window C corner positive/deployed
negative). This meets the round391-392 "three or more disjoint windows"
standard round429 named as the bar for calling a pattern established, and
it closes round429's own explicitly flagged open question with a definite
answer: yes, the relative ordering holds. The same pattern extends to
Sortino (2.046>0.485, −3.223>−3.428, 1.001>−0.794 — all three) and
cost÷gross (0.056<0.727, 2.907<1.723 — **B breaks this one**, corner's
cost-ratio is worse than deployed's at 2.907 vs 1.723; 0.805<1.534 in C) —
so the ordering is not perfectly uniform across every secondary metric, only
on net PnL and Sharpe/Sortino across all three.

**This does not reopen the corner as promotable.** The mechanism replicating
is a relative quality edge, not an absolute-profitability or frequency
result: the corner's own frequency across the three windows is 1.61 / 2.815
/ 2.878 per week — never within 2x of the 7.0 bar, and in this window it is
the *deployed* control, not the corner, that clears Target 3. Extending
round366's "every profitable configuration this loop has ever measured
fails Target 3" pattern: window C is the first window in this specific
corner-vs-deployed series where a *net-positive* configuration (the corner,
+0.14145) coexists with a *Target-3-passing* configuration in the same
window (deployed, 7.249/week) — but they are different arms, and neither
single arm is both profitable and frequent enough at once. That
non-overlap — the frequency-clearing arm is never the profitable arm — has
now been observed on `bybit XAUT` specifically in addition to the fleet-wide
version of the same finding (round366-367 on `binance BTC`).

## Classification: REJECTED

Extends round428/429's REJECTED verdict for the round365/366 corner.
Positive finding: the corner's relative quality edge over the deployed band
(net PnL, Sharpe, Sortino) is now confirmed on 3 of 3 disjoint `bybit XAUT`
windows — a real, replicated mechanism, not a single-window artifact.
Negative finding, decisive for promotion: the corner's own frequency never
approaches Target 3 in any of the three windows (1.61-2.878/week against a
7.0 bar), only one of the three windows is gate-eligible on
`minimum_holdout_days`, and in the one window where a configuration does
clear Target 3 (this round, deployed at 7.249/week) that same configuration
is net-negative. No configuration on `bybit XAUT` has ever been shown
simultaneously profitable and frequency-eligible on a real holdout — this
round adds a third data point to that conclusion rather than changing it.
Promotion condition 2 ("an improvement đáng implement") is not met: a
relative quality edge that never produces a configuration clearing both
Target 1 and Target 3 together is not an implementable change to production
defaults.

## What would move this (not run this round — container budget spent)

- A fourth disjoint `bybit XAUT` holdout would extend the series further,
  but history depth is now the binding constraint at both ends: this
  round's window (94,549 candles) is already smaller than round429's
  (118,185), which was smaller than round428's (143,998) — each shift back
  loses train-window depth. Check total instrument history depth in
  Timescale before spending a container on a fourth window; it may no
  longer support a full three-way split.
- The cost÷gross reversal in window B (corner worse than deployed there,
  unlike A and C) is unexplained and untested — a dedicated look at what
  differs about that window (funding regime, trade count, entry timing)
  could clarify whether it is noise or a real interaction, but this round's
  container budget went to completing the three-window series first per
  round429's explicit priority.
- round428's still-open `--emit-trades` question (whether the round428
  holdout's 13-day negative streak was concentrated in one bad stretch)
  remains untested.

## Limits and what this does not change

- No production code, config, or deployment was touched. This is
  research-only evidence.
- Deployed production defaults (hold=36, band 0.01/0.02) are unchanged by
  this round; the control run is provided only for a valid same-window
  comparison.
- This window's gate verdict is not pass-eligible for either arm
  (`minimum_holdout_days` fails at 65.66 vs the 90-day threshold, same
  structural gap as round429) — read every number above as a
  relative-ranking measurement, per round335's established distinction
  between a route's raw scores and its gate eligibility, not as a pass/fail
  gate verdict in its own right.
- The 1-candle (0.005%) holdout overlap documented above does not
  materially affect any conclusion at this sample size but is disclosed for
  completeness rather than rounded to "no overlap."
- The three previously-identified blocked threads (Target 2 product
  decision, forward-time, Task 6.4 environment access — see round426) are
  unchanged by this round and were not re-checked; they remain outside the
  scope of a single bounded backtest round per this iteration's explicit
  instruction.

## Cleanup confirmation

Both containers were started `-d --rm`; `docker logs -f <name>` was run
concurrently to each container (not attached-and-waited), avoiding
round124-125's `--rm` log-loss trap. Both containers exited on their own
after completion; `docker ps -a --filter
"ancestor=finance-research-local:latest"` returned empty after both
finished. The SSH tunnel was closed with `pkill -f "ssh -f -N -L 18086"`;
`ss -tlnp | grep 18086` returned nothing afterward, confirming closure.
`git status --short` in both repositories is clean at the end of this round
save for the new/modified research-evidence files listed below.
