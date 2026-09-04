# Round 449 — NEEDS-MORE-RESEARCH: ML logistic dependency spike builds under the research cap

Date: 2026-09-04. Operator iteration: **251**. The launcher recorded the
iteration before this prompt; `begin-iteration` was not called. Timezone vận
hành: UTC+7 / Asia/Ho_Chi_Minh. Coordinator session:
`529d401a-77d9-4d8f-8dde-789ffef0b431`.

## Scope

Round 448 closed Volume Profile on a disjoint cutoff. The only remaining
direction in `index.md` mục 0.5 is item 8: a learned Alpha signal, starting
with a simple logistic classifier on causal OHLCV-derived features. Portfolio
search has no open lever: Round 240 already tested `--portfolio-atr-periods`
at 7/14/28 and found it inert; the stale navigation sentence claiming that it
was still open is corrected by this round.

This round performs the registered prerequisite only: determine whether a
minimal pure-Rust logistic-regression dependency can build under the existing
research resource contract. It does not claim a market candidate and does not
run a backtest.

## Buildability evidence

The workspace still has no existing `linfa`, `smartcore`, `ndarray`, XGBoost,
LightGBM, or equivalent ML dependency in its Cargo manifests. `cargo search`
resolved `linfa-logistic` **0.8.1**. Its dependency metadata identifies the
pure-Rust `linfa` 0.8.1 / `ndarray` 0.16 family and the optimizer stack; no GPU
or BLAS dependency was selected for this spike.

A disposable crate was compiled in `rust:1.88-slim-bookworm`, the same builder
base used by `docker/Dockerfile-research`, with the exact research cap:

| cap / result | evidence |
|---|---|
| CPU | 2 vCPU (`NanoCpus=2000000000`) |
| memory | 4 GiB, swap ceiling 6 GiB |
| dependency graph | 64 locked packages; `linfa-logistic 0.8.1`, `linfa 0.8.1`, `ndarray 0.16.1` |
| API smoke compile | `Dataset::new` → `LogisticRegression::default().fit(...)` compiled |
| build | exit 0, `Finished dev profile` in 10.15 s |

The first invocation used `bash -lc` and failed with `cargo: command not found`
(`exit 127`) because the Rust image's Cargo path was not loaded by that login
shell. Re-running with `bash -c`, matching the repository's Docker guidance,
passed. No research service or market-data container remained running after
cleanup.

## What this proves and does not prove

The dependency is technically buildable under the CPU/RAM/swap cap, and the
minimal fitting API is usable. This is not evidence of predictive edge,
Portfolio compatibility, decision frequency, transaction-cost behavior, or
trading safety. No instrument, broker, candle stream, train/validation/
holdout split, trade count, or performance metric was touched; therefore no
metric is fabricated in the CSV.

The next bounded step is a research-only classifier adapter with a fixed,
causal feature schema and an explicit temporal protocol: fit on train only,
freeze the model before validation, choose any probability threshold on
validation only, then evaluate once on a disjoint holdout or registered
walk-forward segments. The adapter must expose signal decisions through the
existing cost-aware research engine before any Alpha improvement claim.

## Classification

**NEEDS-MORE-RESEARCH.** The open ML direction advanced from an unmeasured
dependency risk to a successful capped build/API smoke compile, but it has no
backtest evidence and cannot be promoted. No OpenSpec, OPS transaction,
production change, or provider pin was created.

## Files

- `research/quant/reports/optimize_loop_update_v2.csv`: one research-only row
  with all performance fields blank and no instrument metrics.
- `research/quant/index.md`: records the successful dependency spike, keeps
  ML open for causal temporal backtest, and reconciles Portfolio closure with
  Round 240.
- This file: bounded build evidence and limitations.
