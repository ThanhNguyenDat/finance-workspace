# Round 382 — DATA-ISSUE: **every backtest in this arc used per-interval wall-clock cutoffs**, so no two runs ever covered the same bars. My P1 demanded an unreproducible value; the achievable criterion now passes.

Classification: **DATA-ISSUE** — the most consequential measurement defect this
arc has found, and it is **pre-existing**, not introduced by the change under
review. Two containers (the budget), cleaned up. OPS: FIX round 2 verified,
phase `VERIFY`.

## The mechanism, confirmed in code

`crates/finance-research/src/klines.rs:230` takes `let to_time = Utc::now();`
**inside `pub async fn load(...)`**, and `load` is called **once per interval**.
`PORTFOLIO_INTERVALS` has **eight** entries (`5m, 15m, 30m, 1h, 2h, 4h, 12h,
1d`), so a single run takes **eight different cutoffs**, one per interval load,
seconds to minutes apart. Across runs, the whole window rolls with wall-clock
time.

This is present in `14afa8e` (pre-unification), `59e2489` and `c07951a`
identically — **it predates this change and every round in this arc.**

## What that means for my own P1

I required `bybit BTC` @900 to reproduce `847` trades and
`−3.769332905847924`. **That value cannot be reproduced in principle**: the
baseline run's eight cutoffs were never recorded, and `--as-of` did not exist.
My findings demanded the impossible, and the fix rounds were chasing it.

The achievable criterion is **determinism under a pinned cutoff**, and Codex's
round-2 fix (`f158e04`) provides `--as-of <RFC3339>` plus a `data_as_of` field
in the output. Two runs, same cutoff:

| | run a | run b |
|---|---|---|
| `data_as_of` | 2026-08-31T00:00:00Z | 2026-08-31T00:00:00Z |
| `candle_count` | 259,201 | 259,201 |
| `one_target.trades` | 851 | 851 |
| `one_target.realized_pnl` | −4.083376695749315 | −4.083376695749315 |
| **full report sha256** | **identical** | **identical** |

**Bit-identical.** P1 is closed — not by restoring the old number, but by
establishing that the run is reproducible once the window is pinned, which is
the property that was actually missing.

Codex's stated reason for why its earlier synthetic regression passed while the
real run failed — the fixture operated on already-built in-memory decisions and
so could not exercise the loader's `Utc::now()` calls — is **correct**, and I
checked it against the code rather than accepting it.

## The consequence for the research record

Four runs of the *same route and nominal window*:

| run | `candle_count` | trades | `one_target` |
|---|---|---|---|
| r373 (pre-unification) | 259,198 | 847 | −3.769332905847924 |
| r380 (`59e2489`) | 259,198 | 847 | −3.618298890847919 |
| r381 (`c07951a`) | 259,198 | 846 | −3.713368400847926 |
| r382 (`--as-of` pinned) | 259,201 | 851 | −4.083376695749315 |

**A three-candle window shift moves PnL by 8.3% and the trade count by 4
trades.** Consistent with r345's finding that the replay is chaotic in its
inputs.

So the validity gate I have used since r361 — *"same `candle_count`, therefore
same window"* — is **wrong**. Equal length does not mean equal bars. Concretely:

- **Cross-round comparisons** in this arc compared different bar sets. This is
  the actual mechanism behind r360's cross-round drift, which I attributed to
  window *length*.
- **Within-round pairs** launched together are affected too, though far less:
  their loads are seconds apart, so they differ at the window edges.
- **Any effect smaller than roughly the jitter observed here cannot be
  distinguished from it** in a cross-run comparison. On this route that jitter
  was 8.3% of PnL from a three-bar shift.

I am not retracting specific earlier rounds on this basis — the jitter magnitude
is route- and window-dependent and I have measured it once. But every
cross-run PnL difference in this arc smaller than a few percent should now be
read as **not established**, and `--as-of` should be used from here on.

Large effects are unaffected: r368's +29.6% frequency change, r375's
2-to-5 input-count spread, r372's sign disagreements across routes, and the
guard advantage's ±20–70% range are all far outside this jitter.

## Verification status of the change

Resolved: **P1** (via the achievable criterion), **P2-1** (`"comparable": false`
on segment 1), **P2-2** (strategy-declared required inputs, verified additive —
no `evaluate()` body changed, so no production strategy behaviour moves).

Outstanding before FINAL_VERIFY: I have run `cargo test --workspace` on
`59e2489` (699 passed, 0 failed) but **not** on `f158e04`; and the cross-path
equality criterion — gate faithful against a holdout-restricted `one_target` —
is still not executed. With `--as-of` it is now actually possible.

## What is proven, and what is not

Proven:

- `Utc::now()` is inside `load()`, called once per interval, across all three
  builds; `PORTFOLIO_INTERVALS` has eight entries.
- Two runs with the same `--as-of` produce a byte-identical report (sha256).
- The four-run table above, and an 8.3% PnL swing from a three-candle shift.

Not proven, and deliberately not claimed:

- **That any specific earlier round is wrong.** The jitter is measured on one
  route, one window, once. This is a reason to re-check small effects, not a
  retraction of them.
- That the eight per-interval cutoffs within one run cause a *material*
  misalignment. They differ by the load duration; I have not measured that gap
  or its effect separately from the cross-run effect.
- That `--as-of` makes runs comparable across *machines* or data revisions.
  Binance kline revisions (r347) still move history under a fixed cutoff.
- That the change is ready to release. Two verification items remain.

## Named next step

Re-run `cargo test --workspace` on `f158e04`, then execute the cross-path
equality criterion using `--as-of` so both sides see identical bars — the test
that was impossible before this fix. Then FINAL_VERIFY.
