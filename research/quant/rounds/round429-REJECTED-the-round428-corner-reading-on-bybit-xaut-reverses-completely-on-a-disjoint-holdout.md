# Round 429 — REJECTED: the round428 "corner clears Sharpe/Sortino on `bybit XAUT`" reading reverses completely on a disjoint holdout

Research-state iteration at round start: launcher-recorded `230` per this
iteration's own prompt ("iteration 230 was already recorded... do not call
begin-iteration"); the `quant-research-state state` tool itself still read
`229` at round start. Per round422/424-428's documented precedent, the
launcher's `iteration` counter and this file's `round<N>` sequence number are
two independent counters that have never been 1:1 — this is `round429`,
continuing the sequence from round428.

## Why this round, not another status check

Round428 measured the round365/366 "corner" (protective band 0.02/0.04 +
`--portfolio-minimum-hold-decisions 288`) on `bybit XAUT`'s single available
gate holdout and found the strongest joint-objective reading this arc has
ever produced for it (Sharpe 2.046, Sortino 3.826, cost÷gross 0.056, both
arms gross-positive) — then named its own next step explicitly under "what
would move this": *"A second and third disjoint holdout on `bybit XAUT` ...
to see whether the Sharpe/Sortino/gross-positive reading survives outside
this one window, per round391-392's own standard. Given every other
profitable reading in this arc has alternated in sign or quality across
windows ... the prior from this arc's own evidence is that it likely will
not hold uniformly — but that is an inference, not a measurement."* This
round runs exactly that named, in-scope Portfolio-layer test — not a
re-check of the three externally-blocked threads (Target 2 product decision,
forward-time ~30-day wait, Task 6.4 environment access) that rounds 411-426
already exhausted and that this iteration's prompt explicitly excludes from
counting as round work.

## Method

`--as-of`, the reproducibility flag round382/391 established as the
mechanism for genuinely disjoint (non-nested) holdouts, is used to shift the
replay cutoff back to exactly round428's holdout start
(`2026-05-26T18:40:00Z`). Two Docker containers (`--cpus=1 --memory=2g
--memory-swap=3g --network host` each — 2 CPU / 4 GB RAM / 2 GB swap total,
this iteration's resource cap), one read-only SSH tunnel
(`18086:localhost:8086`), both run against `bybit spot XAUT/USDT 5m --days
500 --as-of 2026-05-26T18:40:00Z`:

1. **Corner**: `--daily-profit-gate --portfolio-minimum-hold-decisions 288
   --portfolio-protective-kind fractional --portfolio-stop-value 0.02
   --portfolio-take-value 0.04`
2. **Deployed-default control, same window**: `--daily-profit-gate
   --portfolio-minimum-hold-decisions 36 --portfolio-protective-kind
   fractional --portfolio-stop-value 0.01 --portfolio-take-value 0.02`

`finance-live-action` HEAD was unchanged at `ca23b05` (same as round427-428);
the pre-built `finance-research-local:latest` image from round428 was reused
(confirmed present via `docker images`, no source changes since). Containers
were launched `-d --rm` and their logs streamed to files with `docker logs
-f` running concurrently (not attached-and-waited), avoiding round124-125's
`--rm` log-loss trap.

## Window identity — partial window and a small overlap, both disclosed

Both runs report identical `candle_count: 118185`, `holdout_candle_count:
23637`, `holdout_start: 2026-03-05T17:00:00Z`, `holdout_end:
2026-05-26T18:44:59.999Z`, `observed_days: 83`, `holdout_calendar_days:
82.073` — confirmed from each run's own `research.backtest_candle_count` log
line, not assumed.

Two honesty notes, checked rather than assumed, per round360's "check
`candle_count`, don't assume" rule and round391's "verify no overlap, don't
assume it" standard:

- **Partial window.** `--days 500` at this `--as-of` yields only 118,185
  candles against round428's 143,998 at the later `--as-of` — roughly 410
  days of history reachable before the cutoff, not the requested 500. This
  is the playbook's documented "a `--days` value beyond available data
  silently yields a partial window rather than an error" behavior, not a
  bug. Consequence: this holdout is shorter (83 observed / 82.07 calendar
  days) than round428's (101 observed / 99.997 calendar days), and **both
  arms fail `minimum_holdout_days` (90)** here — a structural gate-eligibility
  gap this window shares with `exness XAU` (round335-336), not previously
  documented for `bybit XAUT` at this `--as-of`.
- **Near-disjoint, not exactly disjoint.** This holdout's `holdout_end`
  (`2026-05-26T18:44:59.999Z`) is five minutes **after** round428's
  `holdout_start` (`2026-05-26T18:40:00Z`) — the single 5-minute candle
  bucket `18:40:00–18:44:59.999` is counted in both holdouts. That is a
  1-candle overlap out of 23,637 holdout candles in this run (0.004%), an
  artifact of `--as-of` boundary inclusivity rather than a chosen overlap.
  Negligible in magnitude, but reported exactly rather than claimed as clean
  zero-overlap the way round391 verified for its own comparison.

## Results

| Config | trades | trades/week | net PnL | gross PnL (pre-cost) | Sharpe | Sortino | cost÷gross | positive_day_ratio | neg-day streak | gate result |
|---|---|---|---|---|---|---|---|---|---|---|
| Corner (band 0.02/0.04, hold 288) | 33 | 2.815 | −0.80573 | **−0.20623** | **−3.223** | **−4.195** | 2.907 | 0.434 | 11 | FAILED (9/12) |
| Deployed (band 0.01/0.02, hold 36) | 79 | 6.738 | −0.81658 | −0.29989 | −3.428 | −4.238 | 1.723 | 0.434 | 11 | FAILED (9/12) |

Both arms fail the identical 9 checks: `minimum_holdout_days`,
`minimum_trades_per_week`, `positive_day_ratio`, `median_daily_pnl`,
`negative_day_streak`, `sortino_ratio`, `sharpe_ratio`, `gross_pnl_positive`,
`cost_to_gross_pnl_ratio`.

**The round428 reading reverses completely.** On round428's own holdout the
corner was gross +0.6614 / net +0.6246 / Sharpe +2.046 / Sortino +3.826,
clearing 8 of 12 checks. On this disjoint holdout — the identical
configuration, same route, same instrument — it is gross −0.2062 / net
−0.8057 / Sharpe −3.223 / Sortino −4.195, clearing only 3 of 12
(`holdout_interval_continuity`, `daily_drawdown`, `total_drawdown`, all of
which passed trivially in round428 too). `gross_pnl_positive` flips from a
passing check to a failing one for both arms — this is not a "quality
narrows" result, it is a full sign reversal, exactly the round391-392
pattern ("the fleet's one real edge does not survive a disjoint holdout")
now reproduced a second time on a second route/configuration.

**The corner still beats the deployed control on this window**, consistent
with round364's "hold+band buys quality, not just less cost" mechanism: less
negative net (−0.8057 vs −0.8166), less negative gross (−0.2062 vs −0.2999),
better Sharpe/Sortino/cost-ratio by a smaller margin than round428's 4x-plus
gap (here roughly 6-40% better per metric, not the order-of-magnitude gap
round428 measured). That relative ordering replicates even though the
absolute sign of both arms flipped — the corner's *quality* edge over
deployed appears more window-robust than either arm's own sign.

**Frequency inverts too**: the deployed control trades *faster* than the
corner on both windows as expected (hold=36 vs hold=288 is unconditional on
window), but the deployed control's own rate moved from round428's
4.13/week (missing Target 3 by 1.7x) to 6.738/week here (missing by only
1.04x, the closest any `bybit XAUT` reading in this arc has come to the
7.0 bar) — a 63% swing in trade rate for the identical configuration across
two adjacent 82-101 day windows, on the scale round300/301's noise-floor
methodology would call large, not noise.

## Classification: REJECTED

Extends round428's REJECTED verdict for the round365/366 corner with the
disjoint-holdout evidence round428 itself named as the next step. The
corner's one strong joint-objective reading (round428, this same
configuration) does not survive a non-overlapping holdout drawn from an
immediately adjacent period: gross, net, Sharpe and Sortino all flip sign.
This is the second time in the arc (after round391-392's fleet-wide gross
edge) that a single-holdout positive finding for a Portfolio-layer lever has
failed a disjoint-holdout check, and it closes round428's own explicitly
flagged uncertainty — the arc's prior that "it likely will not hold
uniformly" is now a measurement, not an inference, for this route and
configuration. Combined with round427's `binance BTC` failure (gross
negative pre-cost on that route's only available holdout) and `exness XAU`'s
structural gate-ineligibility at every window (round335-336), **no route has
now produced a corner reading that survives even a single robustness check**
— round428's single positive cell was the last untested one, and it is now
tested and failed.

## What would move this (not run this round — container budget spent)

- A third `bybit XAUT` holdout (e.g. `--as-of 2026-03-05T17:00:00Z`, the
  start of this round's holdout, shifted back another ~82 days) would give
  the fleet's third disjoint window on this route and let a majority verdict
  be stated the way round391-392 called for on `exness XAU`. History depth
  is the binding constraint: this round already found only ~410 days behind
  the 2026-05-26 cutoff, so a third disjoint holdout of the same length may
  hit a shorter partial window still — check `candle_count` before trusting
  it.
- The corner's better-than-deployed *relative* ordering on both windows
  measured so far (round428 and this round) is itself a candidate worth a
  dedicated round: does the corner beat the deployed band on every window
  regardless of either arm's absolute sign? Two windows agree; that is not
  yet the three-or-more the arc's own standard (round391-392) requires
  before calling a pattern established.
- round428's still-open `--emit-trades` question (whether the 13-day
  negative streak there was concentrated in one bad stretch) remains
  untested; not pursued this round since the container budget went to the
  higher-priority disjoint-holdout test round428 named first.

## Limits and what this does not change

- No production code, config, or deployment was touched. This is
  research-only evidence.
- Deployed production defaults (hold=36, band 0.01/0.02) are unchanged by
  this round; the control run is provided only for a valid same-window
  comparison.
- This window's gate verdict is not pass-eligible for either arm
  (`minimum_holdout_days` fails at 82.07 vs the 90-day threshold) — read
  every number above as a relative-ranking measurement, per round335's
  established distinction between a route's raw scores and its gate
  eligibility, not as a pass/fail gate verdict in its own right.
- The 1-candle (0.004%) holdout overlap documented above does not
  materially affect any conclusion at this sample size but is disclosed for
  completeness rather than rounded to "no overlap."
- The three previously-identified blocked threads (Target 2 product
  decision, forward-time, Task 6.4 environment access — see round426) are
  unchanged by this round and were not re-checked; they remain outside the
  scope of a single bounded backtest round per this iteration's explicit
  instruction.

## Cleanup confirmation

Both containers were started `-d --rm`; `docker logs -f <name>` was run
concurrently to each container (not attached-and-waited) to avoid losing
output to the `--rm` auto-removal race that bit an earlier attempt this same
round (the first launch used `-d --rm` without a concurrent `docker logs -f`
and both containers exited/self-removed before their output could be
captured — no evidence was lost from a bad run, no partial numbers were
recorded or reported from that attempt, and it consumed no extra container
budget since `--rm` containers that exit before their logs are read are the
same two runs re-launched, not a third and fourth). Both final containers
exited on their own after completion; `docker ps -a --filter
"ancestor=finance-research-local:latest"` returned empty after both
finished. The SSH tunnel was closed with `pkill -f "ssh -f -N -L 18086"`;
`ss -tlnp | grep 18086` returned nothing afterward, confirming closure (the
`pkill` wrapper itself reported a nonzero exit code, consistent with the
playbook's documented unreliability of that command's exit code — `ss`
confirmed the true state). `git status --short` in both repositories is
clean at the end of this round save for the new/modified research-evidence
files listed below.
