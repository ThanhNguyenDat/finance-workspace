# Round 446 — NEEDS-MORE-RESEARCH: Volume Profile POC/Value Area có tín hiệu XAU nhưng không transfer ổn định sang BTC

Date: 2026-09-04. Operator iteration: **248**. Launcher đã ghi iteration một
lần; không gọi `begin-iteration`. Research state báo `iteration=247` (bookkeeping
có thể lag theo contract), nên không increment thêm. Timezone vận hành:
UTC+7 / Asia/Ho_Chi_Minh.

## Scope và giả thuyết

Round 445 đã mở item 7 trong mục 0.5: Volume Profile / Market Profile là cơ
chế mới, khác OBV/MFI/taker imbalance vì dựng phân phối volume theo price bin,
và khác Session VWAP vì đọc POC cùng vùng VAH/VAL bất đối xứng. Vòng này chỉ
test Alpha mechanism đó; không có hướng Portfolio-construction còn mở để tối
ưu có cơ sở. Không chạy Portfolio gate trong vòng này vì đã dùng đủ giới hạn
2 research containers.

Candidate mới được thêm vào registry research-only:

- rolling profile trên các nến đứng trước nến quyết định;
- volume mỗi nến phân bổ theo phần giao nhau với các bin trong `[low, high]`;
- POC là bin có volume lớn nhất, Value Area là vùng liên tiếp quanh POC đạt
  70% tổng volume;
- `bin_count ∈ {12,24,48}`, `lookback ∈ {96,288}`, và hai giả thuyết đối lập
  `{breakout,reversion}` — 12 cells mỗi route.

## Implementation và kiểm tra cục bộ

`finance-live-action/crates/finance-research/src/strategies.rs` có
`VolumeProfileStrategy`, state theo `instrument:timeframe`, eviction bounded,
metadata POC/VAL/VAH và replay semantics đầy đủ. Ba regression tests xác nhận
profile/VA, volume của bar bị eviction rời khỏi histogram, và breakout chỉ
đánh giá trên prior window. Registry không đưa candidate vào production
`StrategyKind` hay `deployment_rules`.

Evidence local:

- `cargo test -p finance-research`: **160 passed**;
- `cargo fmt --all -- --check`: passed;
- Docker image research build: passed;
- targeted strict Clippy vẫn **blocked bởi 9 lỗi pre-existing** ở
  `split::selectable`, `daily_profit_gate`, generated interval enum và
  `klines::LoadError`; lỗi `type_complexity` mới của state đã được sửa và không
  còn xuất hiện.

## Backtest thật

Hai arm chạy tuần tự trong Docker, `--cpus=2 --memory=4g --memory-swap=6g`,
qua SSH tunnel read-only `127.0.0.1:18086`, `--days 500`, `5m`, fee 5 bps,
slippage 2 bps, starting equity 10000, plain train/validation/holdout sweep,
cutoff `2026-09-04T14:15:11Z`. Cả hai log được thu bằng `docker logs -f`; sau
đó container được dọn và `docker ps -a --filter ancestor=finance-research-local:latest`
không còn container.

### Exness XAU/USD CFD — 97,472 candles

`verified_session_gap_candles=46,526`, `unverified_gap_candles=0`.

- Breakout lookback 96: b12/b24/b48 holdout lần lượt PF **0.9494 / 0.9125 /
  0.9248**, PnL **-0.15995 / -0.29718 / -0.24972**.
- Breakout lookback 288: b12/b24/b48 đều dương trên cả train, validation và
  holdout cho b12/b24; holdout PF **1.3366 / 1.3556 / 1.2604**, PnL
  **+0.54522 / +0.57509 / +0.44183**, 71/71/73 trades (~5.02/5.02/5.16
  trades/week). b48 có train PnL **-0.06227**, nên không phải cell selection
  sạch dù holdout dương.
- Reversion: cả 6 cells đều âm ở holdout, PF **0.3772–0.4469**.

### Binance BTC/USDT perpetual — 143,998 candles

`verified_session_gap_candles=0`, `unverified_gap_candles=0`.

- Breakout lookback 96: cả 3 cells âm ở cả ba split; holdout PF
  **0.5217–0.5412**.
- Breakout lookback 288: b12 có holdout **+0.16364**, PF **1.0452** trên 110
  trades (~7.70/week), nhưng train/validation vẫn âm (**-2.41311 / -0.66709**;
  PF **0.8057 / 0.8381**). b24 và b48 âm ở holdout, PF **0.9139 / 0.8350**.
- Reversion: cả 6 cells đều âm ở holdout, PF **0.6236–0.8584**.

## Kết luận

**NEEDS-MORE-RESEARCH.** Volume Profile breakout lookback 288 tạo được tín
hiệu đáng điều tra trên XAU và một holdout BTC dương, nhưng candidate được
chọn từ XAU không sống qua train/validation transfer trên BTC. Chưa có
walk-forward/disjoint holdout thứ hai, chưa có extended Sharpe/Sortino,
decision-rate Portfolio evidence, cost-stress hoặc promotion gate đầy đủ.
Không cherry-pick cell b12 BTC từ holdout; không promote và không tạo
OpenSpec/OPS transaction.

Item 7 vẫn mở cho vòng sau: kiểm tra một cutoff/window độc lập và giữ nguyên
grid/hypothesis đã đăng ký; chỉ xem xét promotion nếu selection + OOS + transfer
đạt đồng thời. Item 8 ML không được triển khai trong vòng này.

## Files

- `research/quant/reports/optimize_loop_update_v2.csv`: 24 rows cho 12 Alpha
  cells trên XAU và BTC; metric extended để trống vì plain sweep không cung cấp.
- `research/quant/index.md`: thêm navigation/evidence Round 446 và giữ item 7
  ở trạng thái mở.
- File này: full method, resource bounds, candle-count gate và kết quả.
