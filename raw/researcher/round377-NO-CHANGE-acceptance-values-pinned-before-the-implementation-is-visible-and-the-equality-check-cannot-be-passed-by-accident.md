# Round 377 — NO-CHANGE: acceptance values **pinned before the implementation is visible**, and the equality check is shown to be unpassable by accident.

Classification: **NO-CHANGE** — no research finding, no configuration verdict.
**Zero containers.** The active OPS transaction's IMPLEMENT phase is still
running; this round does the one useful thing available that cannot interfere
with it or be influenced by it.

## Why this, and why now

`portfolio-measurement-integrity` stands or falls on a single acceptance
criterion: after the gate and Portfolio replay paths are unified, a
`--daily-profit-gate` run must reproduce the `one_target` figures **exactly** at
the same window and configuration.

That check is only trustworthy if its expected values were fixed **before** the
implementation could be seen. Codex is mid-IMPLEMENT and has now modified seven
files (`daily_profit_gate.rs`, `main.rs`, `portfolio_decision_replay.rs`,
`portfolio_measurement.rs`, `split.rs`, `strategies.rs`, `sweep.rs`) with no
commit yet. Pinning the numbers now removes any possibility that the bar is
adjusted to what the implementation happens to produce — the failure mode this
arc has recorded five times in its own pre-registrations (r327, r330, r340,
r354, r373).

## The pinned baseline

Deployed configuration — band 0.01/0.02, hold 36, ATR 14, fee 5bps, slippage
2bps, funding 1bps, `--days 900` — read from logs captured in rounds 371–373,
before any of this change existed:

| route | candles | trades | `one_target` PnL | `legacy` control | ratio |
|---|---|---|---|---|---|
| `binance BTC` | 259,198 | 874 | **−4.81958** | −9.90557 | 2.06x |
| `bybit BTC` | 259,198 | 847 | **−3.76933** | −8.74651 | 2.32x |
| `exness BTC` | 259,084 | 676 | **−4.84586** | −6.79682 | 1.40x |
| `bybit XAUT` | 145,921 | 263 | **−2.03343** | −2.49876 | 1.23x |
| `binance XAU` | 75,672 | 134 | **−1.44149** | −1.09279 | **0.76x** |

Stored at `acceptance_baseline.json`; the check is scripted at
`verify_equality.py`, both written this round.

## Why the check cannot be passed by accident

The gate currently scores the `legacy` column. After unification it must score
the `one_target` column. Those columns are far apart on every route — and,
importantly, **they differ in opposite directions**: `legacy` is 2.32x *worse*
on `bybit BTC` and 0.76x, i.e. *better*, on `binance XAU`.

So an implementation that silently kept the old stream cannot land on the right
answer by luck, and cannot be wrong in a single consistent direction that might
be mistaken for a scaling issue. The check also fails if `legacy` and
`one_target` collapse to the same value, which would mean the control was lost
rather than the paths unified.

The replay is bit-for-bit deterministic (r351), so **exact** equality is the
correct bar; anything weaker is what permitted the original divergence.

## What is proven, and what is not

Proven:

- The five baseline rows above, read from logs captured in earlier rounds under
  the deployed configuration.
- `legacy / one_target` ratios spanning 0.76x to 2.32x — both directions.
- IMPLEMENT is still running and has modified seven files with no commit.

Not proven, and deliberately not claimed:

- **Nothing about the implementation.** No diff has been read, no test run, no
  verification performed. This round deliberately did not look at the work in
  progress beyond `git status`, so the pinned values stay independent of it.
- That these five routes are a sufficient acceptance set. `exness XAU` has no
  deployed-configuration @900 baseline in the held logs — its 900-day run used
  the corner configuration — so it is **absent** from the check and would need
  its own run.
- That passing this check means the change is correct. It proves the two paths
  produce the same numbers; the walk-forward, metric, audit-trail and
  refusal requirements are separate and unverified.
- That any result will improve. Unchanged from round 376: this makes measurement
  correct and does not predict the sign of what is measured.

## Named next step

VERIFY, once IMPLEMENT completes: read the diff, confirm `finance-core` changes
are additive only, run the pinned equality check on at least the two routes with
the widest ratios (`bybit BTC` 2.32x and `binance XAU` 0.76x, opposite
directions), then the remaining acceptance criteria. Nothing is committed or
pushed before that passes.
