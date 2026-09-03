# Round 419 — NO-CHANGE: first real holdout-scored hold-bearing Portfolio configuration (OpenSpec task 6.4); still a loss, ~3x not ~2x understatement

Classification: **NO-CHANGE**. One container (finance-research, capped `--cpus=2
--memory=4g --memory-swap=6g`), one read-only SSH tunnel, both cleaned up.

## Why this round deviated from r411-r418's pure status checks

r411-r418 re-verified the same three (later two) threads without running new
compute, because each was recorded as genuinely blocked: Target 2's metric
definition needs a product/human decision, and the forward-time re-read needs
~30 calendar days. Neither of those changed this round. But this session also
has working `docker` and a working `ssh my` to the production host — and
`openspec/changes/portfolio-measurement-integrity/tasks.md` task 6.4 is
unchecked with a recorded blocker: *"no Finance MW/research runtime is
available in the current local environment ... a networked holdout rerun must
be performed after Claude verification on a host with the production data
route."* That blocker is about environment access, not about a product/human
decision or calendar time, so it was worth re-testing directly rather than
assuming it still holds.

## What was checked

1. `docker build -f docker/Dockerfile-research -t finance-research-local:latest .`
   in `finance-live-action` succeeded against the exact code at `origin/main`
   `7d579cf` (verified clean `git status --short` before and after).
2. `ssh -f -N -L 18086:localhost:8086 my` established the tunnel;
   `ss -tlnp | grep 18086` confirmed it was listening.
3. Ran, detached and without `--rm` (so output could be captured before
   cleanup — a first attempt with `--rm` lost its own output when the
   container exited before `docker logs` was called; documented here so a
   future round doesn't repeat it):
   ```
   docker run -d --name finance-research-hold72b --cpus=2 --memory=4g \
     --memory-swap=6g --network host finance-research-local:latest \
     --endpoint http://127.0.0.1:18086 --broker binance \
     --market-type perpetual_future --base-asset BTC --quote-asset USDT \
     --interval 5m --days 500 --daily-profit-gate \
     --portfolio-minimum-hold-decisions 72 --json
   ```
4. `docker wait` then `docker logs > /tmp/hold72_gate_output.jsonl` captured
   the full output; container removed and tunnel killed afterward
   (`ss -tlnp | grep 18086` empty at end).

This is exactly what task 6.4 asked for: `--daily-profit-gate` and
`--portfolio-minimum-hold-decisions` no longer conflict (task 1.2, merged in
the same push r416 recorded), so this is the **first daily-profit-gate run
ever executed at a hold-bearing configuration through the unified replay
path** (`portfolio_construct_evaluate_execute_target`, not the old
`legacy_selected_rule_on_kline_control`).

## Result (candle_count 143,998 — same as r359/r360's binance BTC @500 window,
confirming no drift for this route)

`holdout_start` 2026-05-25 → `holdout_end` 2026-09-02, 28,799 holdout candles,
99.997 days.

- **Gate: FAILED.** 7 of 12 checks fail: `positive_day_ratio`,
  `median_daily_pnl`, `negative_day_streak`, `sortino_ratio`, `sharpe_ratio`,
  `gross_pnl_positive`, `cost_to_gross_pnl_ratio`.
- **`portfolio_faithful`** (real Portfolio-construction path, hold=72): 173
  trades, `realized_pnl` **-1.450971**, funding -0.0195.
- **`legacy_selected_rule`** (hold-guard bypassed control): 515 trades,
  `realized_pnl` **-4.307464**.
- `gross_pnl_before_costs` **-0.248754** (negative even before costs),
  `total_cost_drag` 1.202217, `cost_to_gross_pnl_ratio` **4.833** (costs are
  ~4.8x gross).
- `trades_per_week` 12.11 — clears Target 3 (>=7/week).
- `sharpe_ratio` -5.7992, `sortino_ratio` -6.7236, `max_drawdown_duration_days`
  98 (near the full 100-day window).

## What this confirms and what it changes

**Confirms the direction** of r371's "gate verdicts understate the deployed
(hold-guarded) configuration by roughly 2x, in the pessimistic direction"
claim — the guarded path (-1.451) does lose materially less than the
unguarded control (-4.307).

**Refines the magnitude**: r371's ~2x figure came from an indirect comparison
(gate vs a separate `one_target` sweep, not the same unified code path,
because at the time `--daily-profit-gate` could not even accept a hold value).
This round is the first time both numbers come from one run of the actual
unified path. The real ratio is **4.307 / 1.451 = 2.97x**, closer to 3x than
2x.

**Does not change any prior strategy conclusion.** `gross_pnl_before_costs`
is negative — the underlying signal loses independent of the hold guard or
execution costs. This matches every prior round's finding that PF(Alpha) < 1
on this route family; the hold guard reduces the size of the loss, it does
not create profit. No promotion condition is met (no improvement, still
fails Target 1 and the gate outright).

## OpenSpec task 6.4 — evidence recorded, checkbox left untouched

Per r416's explicit scope note, this loop does not own the decision to check
off `openspec/changes/portfolio-measurement-integrity/tasks.md` 6.4 or to
archive that change — that OPS transaction is already archived
(`.ops/archive/2026-09-01-portfolio-measurement-integrity/`) and reopening or
closing the OpenSpec artifact is a lifecycle decision outside a NO-CHANGE
research round. What this round adds is the evidence 6.4 asked for: **the run
completed, reported a gate verdict, and the round 371 understatement is now
quantified against the unified path (2.97x, not the earlier ~2x estimate)**.
Whoever owns that lifecycle can check 6.4 and decide whether to archive with
this evidence or fold it into a fresh change.

## Named next step

Both of r418's remaining threads (Target 2 metric definition, ~30-day
forward-time re-read) are unaffected by this round and stay blocked on a
product/human decision and calendar time respectively — nothing here shortens
either wait. Task 6.4's environment blocker is resolved with evidence; no new
backtest direction opens from this result since it reconfirms rather than
contradicts the existing "loses everywhere, hold guard only shrinks the
loss" conclusion.
