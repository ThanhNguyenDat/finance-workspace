# Kline continuity recovery

Task: `trading-24`

## The 15m/5m discrepancy, answered numerically

The original 365-day replay counts were not two views of one rolling-window
boundary:

- `15m`: 341 missing candles represented `341 × 15 = 5,115` minutes, or
  **85 hours 15 minutes**, behind the expected watermark.
- `5m`: 53–86 missing candles represented `265–430` minutes, or only
  **4 hours 25 minutes to 7 hours 10 minutes**, behind the expected watermark.

If a single wall-clock cutoff had shortened both series, the 15m series would
have lost about one third as many rows as the 5m series. Instead, it lost
`341 / 86 = 3.97` to `341 / 53 = 6.43` times as many rows, and its percentage
shortfall was about `0.97 / 0.07 = 13.86` times larger.

The cause was therefore interval-specific persistence state. The closed-kline
flusher required the next queued candle to be exactly contiguous with the
newest database candle. When the first queued candle was after that expected
slot, the route remained blocked at its own persisted watermark. The 15m route
had accumulated an 85h15 backlog while the observed 5m routes were only
4h25–7h10 behind. This explains both percentages without attributing them to a
shared 365-day boundary.

The gaps were collector/persistence omissions, not exchange halts and not
late-listing truncation. The repair path fetched the missing closed candles from
Binance and persisted them in order. No candle was interpolated or fabricated.

## Changes

### finance-mw

- `6ddd70b [trading-24] fix(kline): restore history continuity`
  validates candle quality at ingest, measures blocked ranges, repairs gaps from
  the exchange, exposes gap/invalid-candle metrics, and adds alerting.
- `b82ed6d [trading-24] test(kline): audit production continuity`
  adds a production audit for all 18 symbols and all four intervals.

### finance-broker

- `276a3dc fix: preserve closed historical klines`
- `0fb4840 [trading-24] chore(kline): link broker hotfix to Vikunja`

Historical REST rows are now marked closed from `close_at < now`, rather than
always marking the final returned row open. This prevents an already closed
historical candle from being stored with stale `is_kline_closed=false`
metadata.

### finance-live-action

- `5ad6df1 [trading-24] fix(kline): tolerate rounded duplicate metadata`
- `150bfd0 [trading-24] fix(kline): skip stale checkpoint overlap`

Kafka offsets and runtime checkpoints are durable but independent. On restart,
Kafka can replay an older exchange revision of a candle already restored from a
newer checkpoint. The runtime now records a per-interval restored watermark:
same-timestamp events at or before that boundary are idempotent and the
checkpoint revision wins, while conflicting duplicates after the boundary
still fail closed.

Production comparison confirmed this was real exchange revision drift, not just
floating-point rounding:

- XAUUSDT `5m` at `2026-07-29 14:35 UTC`: Kafka volume `1509.621`; the restored
  database row held corrected volume `1509.921`.
- 1000BONKUSDT `5m` at `2026-07-29 15:00 UTC`: Kafka volume `12,118,996`; the
  restored row held `13,102,261`.
- 1000PEPEUSDT `5m` at `2026-07-29 14:50 UTC`: Kafka close `0.0027256`; the
  restored row held the later one-tick correction `0.0027257`.

## Verification

Local `finance-live-action` verification:

- checkpoint-overlap regression tests: passed;
- later live-conflict fail-closed regression test: passed;
- `cargo fmt --all -- --check`: passed;
- `cargo test --workspace --no-fail-fast`: passed.

Independent code review passed for commit `150bfd0`.

CI/CD and production evidence:

- finance-broker CI/deploy
  [`30459708541`](https://github.com/ThanhNguyenDat/finance-broker/actions/runs/30459708541):
  passed.
- finance-live-action CI/deploy
  [`30465908563`](https://github.com/ThanhNguyenDat/finance-live-action/actions/runs/30465908563):
  passed, including all four bounded Coolify app deployments.
- finance-live-action immutable-image/checkpoint evidence
  [`30467360538`](https://github.com/ThanhNguyenDat/finance-live-action/actions/runs/30467360538):
  passed.
- finance-mw CI/CD
  [`30460959402`](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30460959402):
  the failed production-upstream gate was rerun after the live-action repair and
  the run concluded successfully; its freshness guard skipped redundant deploy
  steps because the production revision was already current.
- finance-mw continuity audit
  [`30466086943`](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30466086943):
  captured all routes successfully; its strict readiness job remained red only
  because of historical closed-state flags described below.

The fresh continuity artifact captured at `2026-07-29T15:29:52Z` reported:

- 72/72 routes audited and classified `continuous`;
- 0 gaps and 0 missing candles;
- 0 invalid candles;
- 0 duplicate open times;
- 129 historical `is_kline_closed=false` flags across 72 routes.

The 129 flags are legacy metadata already persisted before the broker close-time
fix; they are visible and intentionally not rewritten or hidden by this task.
They keep the strict audit red, but do not represent missing, invalid, duplicate,
or interpolated OHLCV rows.

The final worker artifact captured at `2026-07-29T15:53:00Z` reported:

- 18/18 expected workers and 18/18 checkpoints;
- all 18 workers healthy;
- all 18 checkpoint replays complete;
- one image only:
  `finance-live-action_sha-150bfd071f036127613a49cd3aecb4846587770f`;
- the latest worker start was `2026-07-29T15:43:29Z`, so even the newest
  container had remained stable for more than nine minutes at capture time.
