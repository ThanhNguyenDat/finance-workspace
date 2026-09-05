# Round 453 — DATA-ISSUE: decision-tree temporal v3 bị bác trên XAU, BTC không chấm được do OHLCV lỗi

## Phạm vi và classification

- Ngày vận hành: **2026-09-05**, UTC+7 / `Asia/Ho_Chi_Minh`.
- Round: **453**.
- Module: Alpha, tiếp tục item 8 ML trong mục 0.5.
- Route ưu tiên: `exness/cfd/XAU/USD`, sau đó transfer `binance/perpetual_future/BTC/USDT`.
- Candidate: `decision_tree_temporal_v3`, một model mechanism khác với logistic
  regression của Round 450/451/452 nhưng dùng đúng temporal feature schema Round 451.
- Classification tổng thể: **DATA-ISSUE**.

XAU có kết quả research hợp lệ nhưng bị bác ở cả ba split tại candidate được
chọn. BTC không được gán metric vì adapter fail closed trước khi fit do một
đoạn lịch sử OHLCV không hợp lệ. Do đó round này không đủ evidence để gọi là
cross-route transfer, nhưng cũng không được biến lỗi dữ liệu thành một BTC
rejection giả.

## Giả thuyết và phương pháp

Logistic regression là classifier tuyến tính và đã bị bác ở hai schema trước.
Round này thử decision tree nông để bắt threshold/interactions phi tuyến mà
không đưa xgboost/lightgbm hoặc FFI vào research container.

Feature schema giữ nguyên Round 451, tất cả chỉ đọc closed candles:

| feature | định nghĩa causal |
|---|---|
| `return_1` | log-return close hiện tại so với 1 nến trước |
| `return_3` | log-return close hiện tại so với 3 nến trước |
| `return_12` | log-return close hiện tại so với 12 nến trước |
| `realized_vol_12` | độ lệch chuẩn 12 log-return gần nhất |
| `volume_surprise_24` | z-score log-volume hiện tại so với 24 nến trước |

24 nến đầu được giữ Hold để warm-up. Label của hàng `t` là hướng close-to-close
của nến `t+1`; không dùng label trong feature. Model được fit một lần trên
train cho mỗi depth đã đăng ký `{3,4,5}`, dùng `SplitQuality::Gini`, rồi không
refit ở validation/holdout.

`linfa-trees` không cung cấp leaf probability, chỉ trả hard class. Để threshold
vẫn có semantics đo được, adapter tính xác suất dương hiệu chuẩn theo class dự
đoán trên **train duy nhất**: với mỗi class mà tree dự đoán, lấy tỷ lệ label dương
trong các train row rơi vào class đó; threshold `{0.50,0.55,0.60}` được chọn
trên validation theo realized PnL, chỉ nhận cell có ít nhất 20 lệnh validation.
Holdout chỉ được đọc sau selection, không refit và không dùng để calibrate.

Cost và split giữ nguyên để so sánh: interval `5m`, `days=500`, cutoff
`2026-09-05T00:00:00Z`, train/validation/holdout `60/20/20`, fee `5 bps`,
slippage `2 bps`, fixed funding `1 bps`, starting equity `10,000 USD`.

## Build và resource evidence

- Dependency `linfa-trees 0.8.1` được thêm vào workspace cùng family `linfa`
  `0.8.1` đã dùng ở Round 449.
- Smoke compile `cargo check -p finance-research` trong
  `rust:1.88-slim-bookworm` chạy với cap thực tế `2,000,000,000 NanoCPUs`,
  `4 GiB` memory, `6 GiB` memory+swap; exit **0**, `Finished dev profile`.
- Release image `finance-research-round453:latest` build thành công từ
  `docker/Dockerfile-research`; image chứa `linfa-trees 0.8.1`.
- `cargo fmt --all -- --check` sạch; `cargo test -p finance-research`:
  **169 passed, 0 failed**.
- Hai backtest container chạy song song, mỗi container cap 2 CPU / 4 GiB RAM /
  6 GiB swap, qua SSH tunnel read-only `127.0.0.1:18086`; cả hai exit **0**.

## Kiểm tra cửa sổ và data validity

Các round ML trước dùng cutoff `2025-04-01T00:00:00Z` (Round 450/451) hoặc
`2024-12-18T00:00:00Z` (Round 452). Holdout Round 453 thực tế nằm trong
`2026-05-28` đến `2026-09-05`, nên không chồng lấn các holdout trước. Với
`days=500`, requested calendar lower bound của Round 453 cũng sau cutoff
`2025-04-01`; không dùng các cutoff cũ như confirmation.

| route | total candles | train / validation / holdout | holdout UTC | unverified gaps | session gaps |
|---|---:|---:|---|---:|---:|
| exness XAU/USD | 97,450 | 58,470 / 19,490 / 19,490 | 2026-05-28 22:50 -> 2026-09-04 20:59:59.999 | 0 candles / 0 gaps | 46,514 candles / 358 |
| binance BTC/USDT | 144,001 | 86,401 / 28,800 / 28,800 | 2026-05-28 00:05 -> 2026-09-05 00:04:59.999 | 0 candles / 0 gaps | 0 / 0 |

Session gaps của XAU là metadata đóng cửa có authority, không phải unverified
missing candles. Tuy vậy, BTC adapter gặp `training candle 36940 has invalid
OHLCV history`; continuity metadata không đủ để che lấp lỗi này, nên không có
BTC train/validation/holdout metric.

## Kết quả XAU/Exness

Depth 3 / threshold 0.50 được chọn: validation có 910 lệnh và PnL cao nhất
trong các cell đủ minimum trade count. Threshold 0.55 và 0.60 không có lệnh
ở các split nên bị loại khỏi selection. PF `—` nghĩa là không có trade, không
phải PF bằng 0.

| depth | threshold | train PnL / trades / PF | validation PnL / trades / PF | holdout PnL / trades / PF |
|---:|---:|---:|---:|---:|
| 3 | 0.50 | -8.28310 / 1,645 / 0.5335 | -7.66372 / 910 / 0.3352 | -4.15145 / 534 / 0.3665 |
| 3 | 0.55 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |
| 3 | 0.60 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |
| 4 | 0.50 | -8.35648 / 1,733 / 0.5385 | -7.94194 / 952 / 0.3316 | -4.40617 / 570 / 0.3580 |
| 4 | 0.55 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |
| 4 | 0.60 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |
| 5 | 0.50 | -11.34086 / 2,215 / 0.4879 | -9.89421 / 1,241 / 0.3092 | -6.88330 / 902 / 0.3214 |
| 5 | 0.55 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |
| 5 | 0.60 | 0 / 0 / — | 0 / 0 / — | 0 / 0 / — |

Selected holdout: 534 trades, win rate `32.9588%`, funding paid `0.1430 USD`,
max drawdown fraction `0.0004220`, estimated `37.7867 trades/week` using the
98.9236-day holdout span. Tần suất vượt mốc 7/tuần nhưng PnL và PF âm; không
được dùng tần suất để cứu candidate.

## BTC/ Binance — không chấm được

Raw backtest output ghi `ml_decision_tree_temporal: null` và stderr ghi đúng
lỗi `training candle 36940 has invalid OHLCV history`. Adapter temporal logistic
cũng fail tại cùng boundary, cho thấy đây là data/feature-validity blocker
của cửa sổ hiện tại, không phải bằng chứng decision tree thua BTC. Không có
selected depth, threshold, PnL, PF, win rate hay frequency được ghi cho BTC.

## Kết luận, safety và giới hạn

XAU đã đủ evidence để bác candidate temporal decision-tree v3 trên route ưu
tiên: không depth nào có PF > 1 qua train, validation và holdout ở cell có
trade; cell threshold cao hơn chỉ tạo zero-trade. BTC transfer chưa hoàn tất
vì lỗi OHLCV, nên classification tổng thể giữ `DATA-ISSUE`.

Không chạy `--daily-profit-gate`: plain Alpha candidate không có Portfolio-
faithful decision-rate/Sharpe/Sortino/SQN từ command này. Các metric đó để
trống, không suy diễn từ signal-only PnL. Không wiring production, không đổi
Portfolio, không tạo OpenSpec/OPS và không promote.

Giới hạn thực tế: BTC cần một lần data-quality investigation hoặc cửa sổ hợp
lệ khác trước khi có thể nói về cross-route transfer; Round 453 không tự sửa
schema dữ liệu trong cùng round. Calibration theo predicted class là cơ chế
phụ trợ cần được review độc lập trước khi tái sử dụng, dù toàn bộ calibration
chỉ dùng train và không làm thay đổi kết luận XAU.

## Evidence files

- `research/quant/reports/optimize_loop_update_v2.csv`: thêm một row XAU có
  metric selected holdout và một row BTC để trống metric do DATA-ISSUE.
- `research/quant/index.md`: cập nhật item 8, ghi XAU rejection và BTC data
  blocker; ML family chỉ còn mở cho cơ chế/model khác hoặc data repair có scope
  riêng.
- File này: writeup đầy đủ Round 453.
- Raw `/tmp/round453-exness-xau.json`, `/tmp/round453-exness-xau.err`,
  `/tmp/round453-binance-btc.json`, `/tmp/round453-binance-btc.err` được dùng
  để trích evidence; sẽ dọn sau khi kiểm tra độc lập.

Không commit trong Round 453 theo brief; source adapter và dependency đang ở
worktree tạm `finance-live-action-round453` để independent verify kiểm tra.
