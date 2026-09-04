# Round 431 — REJECTED: a fourth disjoint `bybit XAUT` holdout reverses — the round365/366 corner beats the deployed band on only 3 of 4 disjoint windows now measured, not "3 of 3" as round430 concluded, and instrument history depth is now exhausted for this series

Research-state iteration at round start: launcher-recorded `232` per this
iteration's own prompt ("iteration 232 was already recorded... do not call
begin-iteration"); the `quant-research-state state` tool itself still read
`231` at round start. Per round422/424-430's documented precedent, the
launcher's `iteration` counter and this file's `round<N>` sequence number
are two independent counters that have never been 1:1 — this is `round431`,
continuing the sequence from round430.

## Why this round, not another status check

This iteration's prompt explicitly excludes the three externally-blocked
threads (Target 2 product decision, forward-time ~30-day wait, Task 6.4
environment access) from counting as round work, and round430 itself named
the concrete next step in scope: *"A fourth disjoint `bybit XAUT` holdout
would extend the series further, but history depth is now the binding
constraint at both ends... Check total instrument history depth in
Timescale before spending a container on a fourth window; it may no longer
support a full three-way split."* This round runs exactly that named,
in-scope Portfolio-layer test.

## Method

Same mechanism as round429/430: `--as-of` shifts the replay cutoff to
exactly round430's own holdout start (`2025-12-30T01:15:00.000Z`), giving a
fourth, near-disjoint `bybit XAUT` holdout window. Two Docker containers
(`--network host --cpus=1 --memory=2g --memory-swap=3g` each — 2 CPU / 4 GB
RAM / 2 GB swap total, this iteration's resource cap), one read-only SSH
tunnel (`18086:localhost:8086`), both run against `bybit spot XAUT/USDT 5m
--days 500 --as-of 2025-12-30T01:15:00.000Z --daily-profit-gate`:

1. **Corner**: `--portfolio-minimum-hold-decisions 288
   --portfolio-protective-kind fractional --portfolio-stop-value 0.02
   --portfolio-take-value 0.04`
2. **Deployed-default control, same window**: `--portfolio-minimum-hold-decisions 36
   --portfolio-protective-kind fractional --portfolio-stop-value 0.01
   --portfolio-take-value 0.02`

`finance-live-action` HEAD was unchanged at `ca23b05` (verified via `git
rev-parse HEAD` at round start, same as round427-430); the pre-built
`finance-research-local:latest` image from round428-430 was reused
(confirmed present via `docker images`, no source changes since). Containers
were launched `-d --rm` with `docker logs -f <name> > /tmp/r431/<name>.log`
started concurrently (not attached-and-waited), per round124-125's
documented `--rm` log-loss trap.

## Window identity — smaller again, as round430 anticipated

Both runs report identical `candle_count: 75640`, `train_candle_count:
45384`, `validation_candle_count: 15128`, `holdout_candle_count: 15128`,
`holdout_start: 2025-11-07T12:40:00.000Z`, `holdout_end:
2025-12-30T01:19:59.999Z`, `observed_days: 54`, `holdout_calendar_days:
52.528` — confirmed from each run's own `research.backtest_candle_count`
log line and each run's `metrics` block.

History depth across all four windows, each shifted ~65 days earlier than
the last: round428 (A) 143,998 candles → round429 (B) 118,185 → round430 (C)
94,549 → this round (D) 75,640. Each shift loses roughly 19,000-24,000
candles of train+validation+holdout depth. At `--days 500` and this `--as-of`,
75,640 candles at 5m resolution is ~262.6 days of total history reachable —
meaning `bybit XAUT`'s usable history for this instrument now reaches back
only to roughly 2025-04, consistent with the arc's repeated observation
(round62, round335 and others) that several instruments were listed
relatively recently. **A fifth window would be shorter still and is not
worth spending a container on** — this closes the disjoint-window
extension question round430 raised, with a concrete number instead of a
guess.

Near-disjoint, not exactly disjoint, following the same pattern round429/430
already disclosed: this holdout's `holdout_end` (`2025-12-30T01:19:59.999Z`)
is 5 minutes after round430's `holdout_start` (`2025-12-30T01:15:00Z`) — the
same single 5-minute candle-bucket overlap artifact of `--as-of` boundary
inclusivity, negligible at this sample size (1 of 15,128 holdout candles).

## Results

| Config | trades | trades/week | net PnL | gross PnL (pre-cost) | Sharpe | Sortino | cost÷gross | positive_day_ratio | neg-day streak | checks passed | gate result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Corner (band 0.02/0.04, hold 288) | 8 | 1.066 | **-0.01071** | -0.04555 | **-0.0887** | **-0.1321** | -0.765 | 0.741 | 4 | 7/12 | FAILED (`minimum_holdout_days`, `minimum_trades_per_week`, `sortino_ratio`, `sharpe_ratio`, `gross_pnl_positive`) |
| Deployed (band 0.01/0.02, hold 36) | 20 | 2.665 | **+0.01911** | +0.09041 | **+0.1536** | **+0.2724** | 0.789 | 0.685 | 3 | 7/12 | FAILED (`minimum_holdout_days`, `minimum_trades_per_week`, `sortino_ratio`, `sharpe_ratio`, `cost_to_gross_pnl_ratio`) |

Both arms pass `holdout_interval_continuity`, `positive_day_ratio`,
`median_daily_pnl`, `negative_day_streak`, `daily_drawdown`,
`total_drawdown` (six identical checks). **Deployed beats the corner on net
PnL, gross PnL, Sharpe, and Sortino in this window** — the opposite ordering
from all three prior windows. Neither arm clears `minimum_trades_per_week`
here (corner 1.07/week, deployed 2.67/week — both far under the 7.0 bar,
unlike round430's window C where deployed cleared it outright at 7.249).
The corner's trade count (8, over 52.5 days) is the thinnest sample measured
anywhere in this four-window series.

## The "3 of 3" claim in round430 does not hold at n=4 — corrected to 3 of 4

Extending round430's own net-PnL/Sharpe table with this window:

| Window (holdout start → end) | Calendar days | Corner net | Deployed net | Corner Sharpe | Deployed Sharpe | Corner better? |
|---|---|---|---|---|---|---|
| A (round428): 2026-05-26 → 2026-09-03 | 99.997 | +0.6246 | +0.1380 | +2.046 | +0.485 | yes |
| B (round429): 2026-03-05 → 2026-05-26 | 82.07 | -0.8057 | -0.8166 | -3.223 | -3.428 | yes (less negative) |
| C (round430): 2025-12-30 → 2026-03-05 | 65.66 | +0.1415 | -0.1461 | +0.572 | -0.528 | yes |
| D (round431, this round): 2025-11-07 → 2025-12-30 | 52.53 | -0.0107 | **+0.0191** | -0.0887 | **+0.1536** | **no** |

Round430 wrote: *"Corner thắng deployed ở CẢ 3 cửa sổ... đạt chuẩn 'ba cửa
sổ trở lên' Round391-392 đã đặt ra"* (the corner beats the deployed band on
all 3 windows, meeting the round391-392 "three or more" bar for calling a
pattern established). Adding a fourth disjoint window breaks that: the
corner now wins 3 of 4, not 4 of 4 (nor was it ever meant to be read as 3 of
3 = 100% once a fourth window existed to test). This is exactly the failure
mode the arc has hit repeatedly before (round340's smooth trough that
looked robust until round391 broke it disjointly, round352's nested-window
warning, round391-392 themselves reversing round371's cross-route gross
edge) — a pattern that clears a round-specific "N of N" bar is not the same
claim as a pattern that holds under an out-of-sample extension, and round430
should have been read as "3 of 3 measured so far," not as a closed,
permanent 100% result. This round's correction does not itself establish a
new number to trust either (3 of 4 is still a small sample) — it demonstrates
the earlier framing overstated confidence, which is the substantive,
recordable finding here.

## Classification: REJECTED (unchanged bottom line, corrected supporting claim)

The corner (round365/366: band 0.02/0.04, hold 288) remains not promotable
on `bybit XAUT`, same as round427-430: frequency across all four disjoint
windows measured is 1.066 / 1.61 / 2.815 / 2.878 per week, never within 2.5x
of the 7.0/week Target 3 bar regardless of which window's relative ordering
is examined. Promotion condition 2 is still not met. What changes is a
supporting claim, not the verdict: round430's "beats deployed at every
disjoint window" statement is corrected to "beats deployed at 3 of the 4
disjoint windows measured, with the losing window also the thinnest sample
(8 trades)." No production code, config, or deployment was touched.

## History-depth conclusion: close the disjoint-window extension question

Candle depth at this `--as-of` (75,640 candles, ~262.6 days of total
train+validation+holdout) confirms round430's concern was correct: `bybit
XAUT` cannot support a meaningfully-sized fifth disjoint window at this
`--days 500` request without falling well under any of the three prior
windows' size, let alone the 90-day `minimum_holdout_days` gate threshold
(only window A ever cleared it). This closes the "how many disjoint windows
can this corner still be tested against on this route" question round430
opened — the answer is four, and this round used the last one worth
running.

## Data-issue found and fixed in passing: round430's CSV rows were missing their trailing columns

While preparing this round's CSV rows, `research/quant/reports/optimize_loop_update_v2.csv`
was inspected for round430's two rows and found truncated: both stopped
after the `kurtosis` column (25 of 29 fields), missing
`target1_profitable`, `target2_makedecision`, `target3_freq_ge1day_or_7week`
and `notes` entirely (no trailing comma, no quoted notes field — not an
empty-field issue, an actually-missing-fields issue). This is a genuine gap
in the evidence trail, the same class of issue rounds 422/424/425 caught
(never a strategy or measurement conclusion problem, always a mechanical
recording gap). Cross-checked against round430.md's own prose (already
final, not re-derived) to backfill the two rows correctly this round:
corner net_pnl +0.14145 (positive) → `target1_profitable=yes`,
`target3_freq` fails at 2.878/week; deployed net_pnl -0.14608 (negative) →
`target1_profitable=no`, `target3_freq` **passes** at 7.249/week (round430's
own text: "the first time in this three-window series either arm has
cleared Target 3 outright, and it is the deployed control, not the
corner"). `target2_makedecision=n/a` on both, matching every other Portfolio
row since round401 (no metric exists in the tool). Fixed by appending the
four missing fields to both existing rows — no other field on those two
rows was touched, and no round430 conclusion changed.

## What would move this (not run this round — container budget spent)

- The disjoint-window series for this specific corner on `bybit XAUT` is
  now closed (history-depth exhausted, see above). Any future Portfolio-layer
  round on this thread should test a genuinely new question, not a fifth
  window.
- round429's still-open cost÷gross reversal in window B (corner worse than
  deployed there, unlike A, C, and now D where the ratio's sign relationship
  varies again) remains unexplained and untested — a dedicated trade-level
  look (`--emit-trades`, though note this flag is only reachable via the
  non-gate `one_target` code path in `main.rs`, since `--daily-profit-gate`
  returns early before the `--emit-trades` block runs — untested this round,
  a genuine tooling constraint worth recording for whoever picks this up
  next) could clarify whether it is noise or a real interaction.
- With this route's disjoint-window budget exhausted for this corner, the
  next Portfolio-layer round should either test a different lever entirely
  (index.md section "Thứ tự ưu tiên" already flags `--portfolio-atr-periods`
  as the one genuinely-untested Rule 1 parameter, though it does not apply
  to the current `fractional` protective-kind in production) or return to
  Rule 2/3 (new Alpha signal search), both explicitly lower-priority but not
  closed per the existing guidance.

## Limits and what this does not change

- No production code, config, or deployment was touched. This is
  research-only evidence.
- Deployed production defaults (hold=36, band 0.01/0.02) are unchanged by
  this round; the control run is provided only for a valid same-window
  comparison.
- This window's gate verdict is not pass-eligible for either arm
  (`minimum_holdout_days` fails at 52.53 vs the 90-day threshold, same
  structural gap as round429/430) — every number above is a
  relative-ranking measurement, per round335's established distinction, not
  a pass/fail gate verdict in its own right.
- The 1-candle (0.007%) holdout overlap documented above does not
  materially affect any conclusion at this sample size but is disclosed for
  completeness.
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
`git status --short` in `finance-live-action` is clean (HEAD unchanged,
no source edits). Only `research/quant/*` files were modified in
`finance-workspace` this round.
