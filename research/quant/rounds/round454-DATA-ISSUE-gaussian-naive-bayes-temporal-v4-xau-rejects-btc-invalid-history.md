# Round 454 — DATA-ISSUE: Gaussian Naive Bayes temporal v4, XAU bị bác và BTC vẫn fail-closed vì invalid OHLCV

## Phạm vi và classification

- Ngày vận hành: **2026-09-05**, UTC+7 / `Asia/Ho_Chi_Minh`.
- Round: **454**.
- Module: Alpha, tiếp tục item 8 ML trong mục 0.5.
- Route: `exness/cfd/XAU/USD` trước, transfer `binance/perpetual_future/BTC/USDT`.
- Candidate: `gaussian_naive_bayes_temporal_v4`.
- Classification tổng thể: **DATA-ISSUE**.

GaussianNB đã chạy và có evidence hợp lệ trên XAU, nhưng mọi cell có đủ số lệnh đều lỗ/PF < 1. BTC không được chấm vì adapter fail-closed trong train trước khi fit do invalid OHLCV tại boundary `training candle 46853 has invalid OHLCV history`. Vì vậy đây không phải BTC model rejection và không đủ evidence cross-route để kết luận REJECTED cho identity.

## Giả thuyết và phương pháp

Round này thử một cơ chế generative/statistical khác với Round 450/451/452 logistic regression và Round 453 decision tree: Gaussian Naive Bayes, ước lượng Gaussian độc lập theo feature và class, với native `predict_proba` từ `linfa-bayes 0.8.1`. Feature schema giữ nguyên để so sánh:

| feature | định nghĩa causal |
|---|---|
| `return_1` | log-return close hiện tại so với 1 nến trước |
| `return_3` | log-return close hiện tại so với 3 nến trước |
| `return_12` | log-return close hiện tại so với 12 nến trước |
| `realized_vol_12` | độ lệch chuẩn 12 log-return gần nhất |
| `volume_surprise_24` | z-score log-volume hiện tại so với 24 nến trước |

Mọi feature chỉ đọc nến đã đóng và lịch sử trước thời điểm quyết định. 24 nến đầu giữ Hold. Label của hàng `t` là hướng close-to-close của nến `t+1`; model fit một lần trên train, freeze trước validation. Feature scaling dùng mean/std của train, không dùng validation/holdout. Threshold cố định `{0.50, 0.55, 0.60}`; chỉ threshold có ít nhất 20 lệnh validation được xét chọn theo validation realized PnL. Holdout đọc sau selection, không refit và không calibrate.

Cost cố định: interval `5m`, fee 5 bps, slippage 2 bps, funding 1 bps, starting equity 10,000 USD. Không chạy `--daily-profit-gate`; Sharpe/Sortino/SQN/decision-rate Portfolio-faithful để trống.

## Implementation và verification

- Thêm `linfa-bayes = 0.8.1` vào workspace và `finance-research`; Cargo khóa đúng `linfa 0.8.1` / `ndarray 0.16.1`.
- Adapter mới nằm trong `crates/finance-research`, chỉ được wiring vào research CLI JSON/human output; không thêm `StrategyKind`, deployment rule, Portfolio hay production path.
- Smoke compile disposable `rust:1.88-slim-bookworm` với source read-only và cap `--cpus=2 --memory=4g --memory-swap=10g`: exit 0, target đặt trong container ephemeral.
- `cargo fmt --all -- --check`: pass.
- `cargo test -p finance-research -- --test-threads=1`: **172 passed, 0 failed**, tăng từ baseline 169 của Round 453. Có test GaussianNB probability monotonic trên synthetic separated classes, warm-up 24 nến và label/future-feature boundary.
- `cargo clippy -p finance-research --all-targets`: exit 0 với 9 warning pre-existing ở `split.rs`, `daily_profit_gate.rs`, generated protobuf và `klines.rs`; không có warning mới từ adapter.
- Release Docker image `finance-research-round454:latest`: build exit 0 từ `docker/Dockerfile-research`, cap build theo tooling round.

## Validity gate và cửa sổ disjoint

Hai container chạy đồng thời qua SSH tunnel read-only `127.0.0.1:18086`, mỗi container `--cpus=2 --memory=4g --memory-swap=10g`.

| route | total | train / validation / holdout | holdout UTC thực tế | unverified gaps | session gaps |
|---|---:|---:|---|---:|---:|
| exness XAU/USD | 97,048 | 58,229 / 19,410 / 19,409 | 2025-06-24 07:30:00.000Z → 2025-10-01 00:04:59.999Z | 0 candles / 0 gaps | 46,688 candles / 359 |
| binance BTC/USDT | 144,001 | 86,401 / 28,800 / 28,800 | 2025-06-23 00:05:00.000Z → 2025-10-01 00:04:59.999Z | 0 candles / 0 gaps | 0 / 0 |

Requested cutoff là `2025-10-01T00:00:00Z`; các candle cuối có close-time sau cutoff đúng theo loader. Holdout mới bắt đầu sau toàn bộ holdout cũ: Round 452 kết thúc quanh 2024-12-18, Round 450/451 quanh 2025-04-01, còn Round 453 bắt đầu khoảng 2026-05-28. Do đó holdout Round 454 (2025-06-23/24 → 2025-10-01) không chồng lấp ba window holdout đã nêu.

XAU có 359 session gaps với 46,688 candle được metadata authority xác nhận; `unverified_gap_count=0`. BTC liên tục và `unverified_gap_count=0`.

## Kết quả XAU/Exness

Model có 58,204 training rows và label positive rate 0.5107724555. Threshold 0.55 được chọn vì validation PnL cao nhất trong các threshold đạt minimum 20 lệnh; threshold 0.60 bị loại trước selection vì chỉ có 8 validation trades.

| threshold | train PnL / trades / win rate / PF | validation PnL / trades / win rate / PF | holdout PnL / trades / win rate / PF |
|---:|---|---|---|
| 0.50 | -56.38483 / 8,346 / 6.3384% / 0.0335 | -28.13546 / 3,886 / 9.5986% / 0.0582 | -17.80953 / 2,528 / 5.5380% / 0.0236 |
| 0.55 **selected** | -2.27718 / 252 / 43.2540% / 0.4823 | -2.59322 / 246 / 43.4959% / 0.3978 | -1.11736 / 80 / 36.2500% / 0.2699 |
| 0.60 excluded | +0.25184 / 8 / 37.5000% / 0.5370 | -0.40387 / 8 / 12.5000% / 0.0038 | -0.43132 / 2 / 0.0000% / 0.0000 |

Selected holdout có 80 trades, 5.6743 trades/tuần, funding paid -0.1070 USD và max drawdown fraction 0.0001203. Tần suất không cứu được PnL/PF âm. XAU sub-result là **REJECTED** cho identity, không phải PROMOTE.

## BTC/Binance — DATA-ISSUE, không gán metric

Raw stderr ghi chính xác:

`ML temporal GaussianNB research candidate unavailable: training candle 46853 has invalid OHLCV history`.

Trên cửa sổ BTC 5m liên tục, boundary index 46853 tương ứng open-time `2024-10-28T16:25:00Z`, tính từ holdout anchor `2025-06-23T00:05:00Z` và khoảng cách 68,348 candle. Đây là timestamp của training boundary mà adapter báo; thông điệp `invalid OHLCV history` có thể chỉ một candle trong current/24-bar lookback, nên không khẳng định malformed candle nằm đúng index 46853. Cả logistic temporal và GaussianNB cùng fail tại boundary này; đây là evidence data/feature-validity blocker, không phải GaussianNB thua BTC.

Không ghi trades, win rate, PF, PnL hay frequency BTC vào CSV; các trường metric để trống.

## Kết luận, safety và giới hạn

Classification tổng thể là **DATA-ISSUE** vì transfer BTC bị chặn bởi invalid OHLCV mới trong train, trong khi XAU có kết quả âm hợp lệ. Không cherry-pick threshold 0.60; không hạ minimum 20 trades. Không tự interpolation/synthetic-fill candle lỗi. Không tạo OpenSpec/OPS, không đổi Portfolio/production.

XAU tiếp tục cho thấy cùng chữ ký bất lợi trên temporal schema dù classifier đã chuyển sang generative GaussianNB, nhưng chưa được gọi là “lần thứ ba cross-route thất bại” vì BTC chưa có metric trên cửa sổ này. Named next step là một data-quality investigation có scope riêng để xác định malformed BTC candle/lookback và chạy lại transfer trên cửa sổ hợp lệ; chỉ sau đó mới đánh giá có nên đóng ML family hay đổi hẳn label horizon/feature mechanism, không tự làm hướng đó trong Round 454.

## Evidence files

- `research/quant/reports/optimize_loop_update_v2.csv`: thêm 1 row XAU selected threshold 0.55 với metric thật và 1 row BTC để trống do DATA-ISSUE.
- `research/quant/index.md`: thêm navigation Round 454 dưới item 8.
- File này: `research/quant/rounds/round454-DATA-ISSUE-gaussian-naive-bayes-temporal-v4-xau-rejects-btc-invalid-history.md`.
- Raw backtest evidence đã trích từ `/tmp/round454-exness-xau.json`, `/tmp/round454-exness-xau.err`, `/tmp/round454-binance-btc.json`, `/tmp/round454-binance-btc.err`; các file tạm sẽ được dọn sau khi cập nhật evidence.
