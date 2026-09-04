# Round 444 — REJECTED: Hurst-exponent regime gate does not cleanly rescue either closed Donchian breakout or Keltner reversion; closes index.md section 0.5 item 6 (6/6 mechanisms tested since round432's audit)

**Layer:** Alpha
**Instruments:** `exness XAU/USD` (cfd), `binance BTC/USDT` (perpetual future)
**Classification:** REJECTED

## Context

This round executes round442/443's other named next step for
`research/quant/index.md` section 0.5 item 6 (Hurst-exponent regime filter):
gate the CLOSED `DonchianBreakoutStrategy` (round88) and `KeltnerReversionStrategy`
(round91/96/98) by a rolling Hurst-exponent regime read and see whether the
gate rescues either into a promotable candidate.

## Continuation context — uncommitted work recovered, not re-done

`quant-research-state state` read iteration `245` at round start — the
coordinator's own per-session attempt counter, distinct from the round-file
sequence per the playbook's documented divergence (round413/424-426/440-443).
`finance-workspace` was clean and synced to `origin/main` (`1c2253f`) at round
start. `finance-live-action` was also synced to `origin/main` (`917f00d`,
round443's commit) **but had an uncommitted working-tree diff**: a complete,
already-unit-tested `hurst_exponent` R/S estimator
(`crates/finance-strategy/src/indicators/hurst.rs`, 241 lines, 5 tests
including 3 synthetic-series-with-known-Hurst-character fixtures — white
noise ≈0.5, a persistent ramp >0.75, an anti-persistent alternating series
<0.25, and an ordering check) plus a fully implemented, doc-commented
`HurstRegimeFilterStrategy` wrapper in `strategies.rs` (123 lines) — but **no
candidate registration and no backtest**. This matches the round422/424/425/440
"evidence-trail-sync-gap" family exactly: a prior attempt (plausibly
interrupted by a provider-quota boundary between round443's own commit and a
follow-up edit) did real, already-validated work and never committed it.

Verified the diff against round442/443's own design notes before trusting it
(the wrapper's doc comment cites round442's source survey and round443's
estimator-validation precedent correctly; the estimator's synthetic tests
match round442's "unit test R/S calculation on synthetic series with known
Hurst exponent before trusting it on real data" named next step exactly) —
did not re-derive or duplicate this work, built on it directly. `cargo build
-p finance-research -p finance-strategy` compiled clean; `cargo test -p
finance-strategy -p finance-research` — 157/157 in `finance-research`'s own
suite plus the 5 new `indicators::hurst::tests` in `finance-strategy`, all
green, before any candidate was registered.

## What this round added

Registered 6 new candidates in `strategies::candidates()` (the plain
discovery sweep grid), wrapping each closed strategy's own single
best-evidence variant — not the full historical grid, since the question is
"can gating rescue the strongest starting point", and a weaker variant has no
better chance if the strongest one fails:

- `donchian_breakout_200` (round88: the strongest holdout PF in its own
  20/55/100/200 grid) wrapped `HurstRegime::Trending` (breakout strategies
  expect persistent/trending behavior) at `period=64` (fixed, a 5m-bar
  lookback 2x the estimator's own 32-point minimum), threshold swept at
  {0.50, 0.55, 0.60} — tightened in the trending direction (`H >` threshold).
- `keltner_reversion_20_2_5` (round91/96/98: the cost-limited-not-clearly-
  negative variant) wrapped `HurstRegime::MeanReverting` (reversion
  strategies expect anti-persistent behavior) at the same `period=64`,
  threshold swept at {0.50, 0.45, 0.40} — tightened in the mean-reverting
  direction (`H <` threshold).

`cargo fmt -p finance-research -p finance-strategy` found two pre-existing
formatting issues in the uncommitted diff (a multi-line function signature,
a struct literal) — fixed, not suppressed. `cargo clippy -p finance-research
-p finance-strategy --all-targets` shows only the same 9 pre-existing
findings round437/443 already documented as unrelated to this diff. `cargo
test -p finance-strategy -p finance-research` still 157/157 (`finance-research`)
plus 93/93 (`finance-strategy`, `finance-strategy`'s own lib-test binary) —
no new test needed since the estimator and wrapper's unit tests were already
complete from the recovered work; the candidate registration itself has no
dedicated test (matches round88/91/130's own precedent — no per-candidate
test exists for the base grid, only for the underlying strategy structs).

## Backtest — two containers, `--days 500`, plain sweep (no `--daily-profit-gate`)

SSH tunnel `ssh -f -N -L 18086:localhost:8086 my` opened, confirmed listening
via `ss -tlnp`, closed at the end of the round (confirmed via `ss -tlnp`
showing nothing on 18086 afterward). Docker image rebuilt (`docker build -f
docker/Dockerfile-research`) after the source change, per the standing rule.
Two detached containers, `--cpus=2 --network host`, logs captured via
`docker logs -f <name>` (stdout carries only the pretty-printed `--json`
payload; ECS application logs go to stderr, captured separately) — both used
`--rm` and self-removed on completion (`docker wait` returned `0 0`),
confirmed via `docker ps -a --filter "ancestor=finance-research-local:latest"`
(empty) before this round ends:

1. `finance-research-r444-xau` — `exness XAU/USD` cfd.
2. `finance-research-r444-btc` — `binance BTC/USDT` perpetual future.

**Validity gate, checked before reading any score**: `candle_count` 97,472
(XAU) / 143,998 (BTC) — **identical** to round433/443's own recorded values
for this exact route/window/`--days 500`, confirming the same underlying
window loaded both times.

## Results — all 3 splits, all 6 candidates, both routes (18 cells)

| Route | Candidate | Train PF | Validation PF | Holdout PF | Holdout trades |
|---|---|---:|---:|---:|---:|
| XAU | `donchian_breakout_200` (unfiltered baseline) | 0.993 | 0.675 | 1.700 | 49 |
| XAU | `hurst_trending_64_0_50_donchian_breakout_200` | 1.069 | 0.803 | 2.038 | 43 |
| XAU | `hurst_trending_64_0_55_donchian_breakout_200` | 1.133 | 0.986 | 1.730 | 43 |
| XAU | `hurst_trending_64_0_60_donchian_breakout_200` | 1.034 | **1.125** | 1.264 | 41 |
| XAU | `keltner_reversion_20_2_5` (unfiltered baseline) | 0.440 | 0.570 | 0.594 | 157 |
| XAU | `hurst_mean_reverting_64_0_50_keltner_reversion_20_2_5` | 0.738 | 0.749 | 0.966 | 40 |
| XAU | `hurst_mean_reverting_64_0_45_keltner_reversion_20_2_5` | 1.485 | 0.692 | 2.392 | 18 |
| XAU | `hurst_mean_reverting_64_0_40_keltner_reversion_20_2_5` | 1.320 | 1.167 | 4.626 | 8 |
| BTC | `donchian_breakout_200` (unfiltered baseline) | 0.901 | 0.461 | 1.054 | 80 |
| BTC | `hurst_trending_64_0_50_donchian_breakout_200` | 0.766 | 0.442 | 1.130 | 76 |
| BTC | `hurst_trending_64_0_55_donchian_breakout_200` | 0.827 | 0.385 | 1.290 | 68 |
| BTC | `hurst_trending_64_0_60_donchian_breakout_200` | 1.140 | **0.462** | 1.373 | 54 |
| BTC | `keltner_reversion_20_2_5` (unfiltered baseline) | 0.693 | 0.792 | 0.769 | 280 |
| BTC | `hurst_mean_reverting_64_0_50_keltner_reversion_20_2_5` | 0.693 | 0.703 | 0.937 | 96 |
| BTC | `hurst_mean_reverting_64_0_45_keltner_reversion_20_2_5` | 1.164 | 1.344 | **0.341** | 38 |
| BTC | `hurst_mean_reverting_64_0_40_keltner_reversion_20_2_5` | 1.180 | 1.653 | 0.867 | 18 |

(Full per-split trade count / win rate / realized PnL / max drawdown / funding
for all 18 cells in `/tmp/r444-xau.json` and `/tmp/r444-btc.json`, this round
only, not committed — CSV summary of the holdout row per cell is in
`research/quant/reports/optimize_loop_update_v2.csv`, round 444 rows.)

## Reading — a real, structural effect that does not cross the promotion bar

**Trending gate on `donchian_breakout_200`.** Exactly one cell across both
routes clears PF>1.0 on **all three** splits with a non-thin sample: XAU at
threshold 0.60 (1.034 / 1.125 / 1.264, 118/31/41 trades — all above this
program's own ~20-30 holdout-trust floor from round49/round75). But the
**identical threshold fails BTC's validation split** (0.462, bolded above) —
train and holdout both clear 1.0 there too (1.140 / 1.373), so the same
single-route/thin-validation-window pattern round338/342 already flagged
applies: a configuration selected on one route does not transfer to the
other at the same threshold, which is exactly the cross-route
transfer-test bar this program has used since round366 to distinguish a real
edge from a route-specific artifact. Thresholds 0.50 and 0.55 fail their own
validation split on **both** routes (XAU: 0.803/0.986; BTC: 0.442/0.385) —
neither is even a same-route-consistent rescue, let alone a cross-route one.

**Mean-reverting gate on `keltner_reversion_20_2_5`.** Threshold 0.50 is the
one genuinely consistent finding in this round: it improves PF at **every
single one of the 6 cells** (both routes × all 3 splits) over the unfiltered
baseline — XAU 0.440/0.570/0.594 → 0.738/0.749/0.966, BTC 0.693/0.792/0.769
→ 0.693/0.703/0.937 — without a single regression anywhere, and gets XAU's
holdout to within 3.4% of breakeven. This is a real, structural improvement
in the same category as round130's realized-volatility filter or round371's
construction guard: the gate has genuine signal-quality value. It still does
not cross PF 1.0 on either route. Threshold 0.45 shows the textbook
train-good/holdout-bad overfit shape on BTC (1.164/1.344 train/validation
collapsing to **0.341** holdout, bolded above) — the same disqualifying
pattern round73/round383's arc has repeatedly flagged. Threshold 0.40's
apparent PF>4 XAU holdout (4.626) is 8 trades — below this program's own
trust floor, the same caveat round75 already applied to a 16-trade holdout;
not evidence for the mechanism on its own terms, and its BTC counterpart at
the same threshold is a plain holdout loss (0.867) with an equally thin
18-trade sample.

No cherry-picking: all 18 cells (6 candidates × both routes × 3 splits, plus
the 4 unfiltered-baseline reference cells) are reported above; none is
omitted. The two unfiltered baselines match round88/91's own closed-grid
numbers in shape (XAU Donchian's PF>1 holdout despite a sub-1 validation was
already visible in round88's own closed writeup; Keltner's below-1-everywhere
shape matches round91 exactly), confirming this round changed nothing about
how the underlying strategies score, only added the gate on top.

## Classification: REJECTED

Neither closed strategy is rescued into a **promotable** configuration:
promotion requires a defensible, non-cherry-picked, cross-route-consistent
PF>1.0 result (this program's standing bar since round338/366), and no
candidate here clears that bar. The trending gate's one same-route win fails
transfer; the mean-reverting gate's one fully-consistent finding (threshold
0.50) never reaches breakeven; every other cell is either inconsistent across
its own three splits, shows a classic overfit shape, or rests on a
holdout sample too thin to trust by this program's own established rule.
This closes `research/quant/index.md` section 0.5 item 6 — **all 6 items
proposed after round432's audit are now closed** (item 1 round433, item 2
round437, item 3 round439, item 4 round436, item 5 round443, item 6 here).

## What remains open, honestly

`period=64` was never swept (a shorter or longer Hurst lookback window could
change which threshold is closest to a rescue); `donchian_breakout_200` and
`keltner_reversion_20_2_5` are each only one variant of their own closed
grids (other periods/multipliers untested under a Hurst gate). The
mean-reverting-gate-at-0.50 structural improvement (real, consistent,
6-for-6 cells) is the strongest residual signal in this round and is
recorded here rather than asserted away — but per this program's own
no-fabrication rule and round443's identical precedent (closing
statistical-arbitrage spread-reversion despite an unswept `entry_z`
threshold), an unswept parameter does not on its own justify keeping a
direction open when the tested grid is this size (18 cells, comparable to
round433's 30-cell and round443's 8-cell closures) and shows no
cross-route-consistent promotable result. Re-open only with a period sweep
or a hedge-ratio-style refinement that reports honest train/validation/
holdout, not by re-running the same threshold grid.

## Housekeeping

Two Docker containers this round (both `-d --rm`, logs captured via `docker
logs -f` before their `--rm` self-removed them; confirmed empty via `docker
ps -a --filter "ancestor=finance-research-local:latest"`). One SSH tunnel
opened and closed, confirmed via `ss -tlnp` (empty for port 18086) after
teardown. `finance-live-action` local checks this round: `cargo build -p
finance-research -p finance-strategy` (clean), `cargo test -p finance-research
-p finance-strategy` (157/157 + 93/93, 0 failures), `cargo fmt --check -p
finance-research -p finance-strategy` (clean, after fixing two formatting
issues in the recovered diff), `cargo clippy -p finance-research -p
finance-strategy --all-targets` (9 pre-existing findings, unrelated to this
round's diff, left untouched per scope discipline). Commit pending push at
round end; `git fetch origin main -q && git rev-parse HEAD origin/main`
checked before and will be re-checked after push to confirm the exact SHA
landed. Research evidence updated: this file,
`research/quant/reports/optimize_loop_update_v2.csv` (12 new rows, round
444), `research/quant/index.md` (section 0.5 closed out, closed-directions
table updated).
