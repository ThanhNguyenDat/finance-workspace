# Round 351 — DATA-ISSUE: `--interval` does **not** change the Portfolio's decision interval — it is hardcoded to `"5m"`. The `--interval 30m` run reproduced an earlier 5m baseline **bit-for-bit**, which is both the proof and a free determinism check.

Classification: **DATA-ISSUE** — a flag that reads like a lever is inert on this measurement
path, and a researcher could easily believe they had tested a longer decision horizon. Two
bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## The lever I intended to test

Cost is the binding constraint on `exness XAU` (Rounds 313-350) and every construction lever has
been closed. One axis had never been touched: **every run in this arc has used a 5m decision
interval**. A longer decision horizon would mean fewer, larger decisions — fewer trades for the
same edge, which is exactly what a cost-bound strategy needs.

**Pre-registered as a partition:** let **K** = `cost_to_gross_pnl_ratio` for `exness XAU` @300
with `--interval 15m`, deployed band and costs.
- **K < 1.1338** (the 5m value at the same window) → the longer decision interval improves the
  binding constraint;
- **K ≥ 1.1338** → it does not.

## Result — the treatment was never applied

| run | holdout candles | trades | tr/wk | gross | cost | net | **cost÷gross** |
|---|---|---|---|---|---|---|---|
| 5m (r343 baseline) | 11,598 | 42 | 5.0526 | 0.339074407112835**5**4 | 0.38445248744791927 | −0.04537808033508374 | **1.1338** |
| **30m** | **11,598** | **42** | **5.0526** | **0.33907440711283554** | **0.38445248744791927** | **−0.04537808033508374** | **1.1338** |
| 15m | 11,595 | 42 | 5.0535 | 0.33543718157929480 | 0.38445576196952630 | −0.04901858039023151 | 1.1461 |

**The `--interval 30m` run is identical to the 5m baseline in all 20 metric fields, in the entire
`daily_results` array, and in the holdout window.** Two runs launched in different rounds at
different wall-clock times, agreeing to seventeen significant digits, is not a coincidence — it
is the same computation.

The code says why. `finance-research/src/main.rs` passes the **literal `"5m"`** into the
Portfolio path — `replay_portfolio_decisions(..., "5m", ...)` at `:577`, the gate at `:612`, the
gate klines at `:599`, and `compare_real_portfolio_with_funding(..., "5m", ...)` at `:634` —
never `args.interval`. And `portfolio_decision_replay.rs:246-250` hard-errors on anything else:

```rust
if primary_interval != "5m" {
    return Err(format!("production Portfolio decision interval is 5m, got {primary_interval}"));
}
```

`--interval` (default `5m`, `main.rs:185`) reaches only the **Alpha sweep table**, a separate
candidate-scoring surface. **The Portfolio decision interval is not configurable from the CLI.**

**So my pre-registered branch technically fired — K(15m) = 1.1461 ≥ 1.1338 — and it is void.**
The 15m run did not test a 15m decision interval either; its 3-candle-shorter holdout (11,595
against 11,598) is a window-alignment side effect that perturbs the same 5m replay. I did not
chase where that shift originates, and I am not reporting 1.1461 as a decision-interval result.

## The by-product is worth more than the intended test

Two runs, **different rounds, different wall-clock times, identical data window** → **identical
output to seventeen digits across every field and all 51 daily rows.**

**The replay is bit-for-bit deterministic given the same input window.** That matters for how
this arc reads its own numbers: every difference observed between configurations in Rounds
330-350 is a **real response to a real input change**, never run-to-run jitter. There is no
"configuration noise" floor from non-determinism — Round 339's ±0.28 noise talk and Round 345's
"chaotic sensitivity" are about **sensitivity to inputs**, not randomness, and this run separates
those two ideas cleanly for the first time.

It also means a repeat measurement of an identical configuration is worthless — the only way to
probe stability is to change an input, which is what makes Round 345's threshold finding the
right frame.

## What is proven, and what is not

Proven:

- `main.rs:577, 599, 612, 634` pass the literal `"5m"`; `portfolio_decision_replay.rs:246-250`
  rejects any other primary interval; `--interval` defaults to `5m` at `main.rs:185`.
- `--interval 30m` reproduced the r343 5m baseline in **20/20 metric fields**, the full
  `daily_results` array, and the holdout window.
- `--interval 15m` produced an 11,595-candle holdout against 11,598, with 13 of 20 metric fields
  differing and 42 trades in both.

Not proven, and deliberately not claimed:

- **Anything about a longer Portfolio decision interval.** It was not tested and **cannot be**
  from the CLI; the guard hard-errors, so it needs a code change. The registered K comparison is
  void.
- **Why `--interval 15m` shifts the holdout by 3 candles.** It does not change the decision
  interval, so something upstream in window selection or alignment uses the flag. **I did not
  investigate.**
- That determinism extends across code or image versions. Both runs used the same
  `finance-research-local:latest` build; a rebuild is untested.
- That determinism means the numbers are *accurate*. It means they are **reproducible** — a
  different property, and the fidelity limits recorded in the audits are untouched.
- Any promotion. No configuration changed and nothing was improved.
