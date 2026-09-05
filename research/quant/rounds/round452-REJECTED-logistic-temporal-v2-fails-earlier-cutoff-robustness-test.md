# Round 452 - REJECTED: logistic temporal v2 fails the earlier-cutoff robustness test

## Scope and hypothesis

- Operating date: 2026-09-05, UTC+7 / Asia/Ho_Chi_Minh.
- Round number: 452. The authoritative round-file scan found round451 as the highest existing file before this run.
- Route priority: Exness XAU/USD CFD first, then Binance BTC/USDT perpetual.
- Pre-registered hypothesis: logistic_regression_temporal_v2 may have failed only at the Round-451 cutoff; on an earlier pinned cutoff the unchanged adapter might retain positive PnL/PF across train, validation, and holdout and transfer to BTC.

This is a robustness test of an unresolved ML direction, not a new threshold sweep and not a new candidate. Round 451 rejected v2 at its own cutoff but left the ML family open for different evidence. This round tests whether that failure was only cutoff/regime-specific. The two cutoffs are not pooled as independent evidence.

## Method and pinned inputs

Backtest used the unchanged finance-research binary in sibling repo ../finance-live-action at source commit 9eb515252b5c28ba851e3dd70e0eb3412e20a616 (Round 451). The image finance-research-local:latest was rebuilt from that checkout. Each route used a detached Docker container capped at 2 CPUs, 4 GiB RAM, and 6 GiB swap, with host networking and the read-only SSH tunnel at 127.0.0.1:18086.

Pinned command parameters for both routes:
- interval 5m
- days 150
- as-of 2024-12-18T00:00:00Z
- train/validation/holdout 60/20/20
- fee 5 bps, slippage 2 bps, fixed funding 1 bps
- starting equity 10,000 USD
- JSON output

Model protocol was unchanged from v2:
- causal features from closed candles: return_1, return_3, return_12, realized_vol_12, volume_surprise_24;
- 24-candle warm-up held;
- one fit on train, standardization from train only;
- threshold {0.50, 0.55, 0.60} selected on validation with a minimum of 20 validation trades;
- holdout read once, with no refit.

No daily-profit-gate was run: it cannot score an arbitrary Alpha candidate. Sharpe, Sortino, SQN, and Target 2 were left unavailable rather than inferred.

## Data validity

| route | candles | train / validation / holdout | holdout UTC | 5m unverified gaps | verified session gaps |
|---|---:|---:|---:|---:|---:|
| exness.cfd.XAU.USD | 29,349 | 17,609 / 5,870 / 5,870 | 2024-11-18 05:45 -> 2024-12-18 00:04:59 | 0 candles / 0 gaps | 13,587 / 109 |
| binance.perpetual_future.BTC.USDT | 43,201 | 25,921 / 8,640 / 8,640 | 2024-11-18 00:05 -> 2024-12-18 00:04:59 | 0 candles / 0 gaps | 0 / 0 |

The 5m continuity evidence is valid for this plain 5m Alpha run. XAU session gaps are recorded market-closure metadata, not missing candles. The holdout is about 29.76 days for XAU and 30.00 days for BTC, so it is thin evidence and not a Portfolio gate verdict.

## Results - Exness XAU/USD

Threshold 0.50 was selected: validation had 663 trades; 0.55 and 0.60 had only 1 and 0 validation trades and were excluded.

| threshold | train PnL / trades / PF | validation PnL / trades / PF | holdout PnL / trades / PF |
|---:|---:|---:|---:|
| 0.50 selected | -14.75285 / 2,238 / 0.0442 | -5.03048 / 663 / 0.0202 | -4.72074 / 666 / 0.0381 |
| 0.55 excluded | +0.32385 / 24 / 2.9311 | -0.31206 / 1 / 0.0000 | -0.24419 / 8 / 0.2228 |
| 0.60 excluded | +0.27179 / 2 / n/a | 0.00000 / 0 / n/a | 0.00000 / 0 / n/a |

Selected holdout win rate was 7.36% and estimated activity was about 156.6 trades/week. Activity does not rescue the negative PnL/PF.

## Results - Binance BTC/USDT

Threshold 0.55 was selected: among thresholds with at least 20 validation trades it had the highest validation PnL, although that PnL was negative. Threshold 0.60 had a positive one-trade holdout but only two validation trades and was excluded.

| threshold | train PnL / trades / PF | validation PnL / trades / PF | holdout PnL / trades / PF |
|---:|---:|---:|---:|
| 0.50 | -38.64539 / 5,822 / 0.1766 | -13.33238 / 1,840 / 0.1559 | -12.90529 / 1,896 / 0.1648 |
| 0.55 selected | -0.79344 / 82 / 0.8200 | -0.24224 / 31 / 0.8703 | -0.08188 / 27 / 0.9518 |
| 0.60 excluded | -2.11044 / 6 / 0.0675 | -0.30258 / 2 / 0.6728 | +0.35366 / 1 / n/a |

Selected holdout win rate was 62.96% and estimated activity was about 6.3 trades/week, below the 7/week reference. The one-trade positive at 0.60 is not an OOS result under the registered selection rule.

## Classification

**REJECTED** for the hypothesis that the temporal v2 result was only a cutoff artifact.

- The priority XAU route is negative on all three splits at the only eligible threshold; the earlier cutoff does not rescue the schema.
- The BTC transfer is negative on train, validation, and holdout at its only eligible selected threshold.
- The earlier cutoff is a bounded robustness reading, not a reason to pool thin or overlapping windows as independent evidence.
- Invalidated conclusions: do not claim temporal features are profitable on XAU, that high activity is an improvement, or that the BTC 0.60 one-trade holdout demonstrates transfer.

No OpenSpec/OPS change was created. No production read or mutation was needed.

## Reproducibility and cleanup

- Image build command: docker build -f docker/Dockerfile-research -t finance-research-local:latest .
- Both detached containers exited successfully.
- docker ps -a --filter ancestor=finance-research-local:latest was empty after cleanup.
- The SSH tunnel was closed and ss -tlnp confirmed port 18086 was absent.
- Temporary JSON/stderr files under /tmp were removed after extracting metrics.
- Source evidence: ../finance-live-action commit 9eb515252b5c28ba851e3dd70e0eb3412e20a616.

Artifacts updated:
- research/quant/reports/optimize_loop_update_v2.csv: two Alpha rows with selected-threshold metrics; unavailable extended metrics left blank.
- research/quant/index.md: item 8 navigation and Round 452 status.
