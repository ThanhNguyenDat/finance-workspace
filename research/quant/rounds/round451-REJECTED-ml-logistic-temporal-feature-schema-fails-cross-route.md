# Round 451 — REJECTED: logistic temporal feature schema không giữ được OOS/cross-route

## Phạm vi và trạng thái

- Ngày vận hành: **2026-09-05**, UTC+7 / `Asia/Ho_Chi_Minh`.
- Operator iteration theo launcher: **253**. Launcher đã ghi iteration; không
  gọi `begin-iteration` và không tăng iteration lần nữa.
- Round research liên tục kế tiếp theo round-file/git history: **451**.
- Mục tiêu: tiếp tục item 8 ML ở mục 0.5 bằng một feature schema khác với
  `logistic_regression_ohlcv_v1` của Round 450; không wiring production.
- Ưu tiên route: `exness/cfd/XAU/USD`, sau đó transfer sang
  `binance/perpetual_future/BTC/USDT`.

## Hypothesis và phương pháp

Candidate mới: `logistic_regression_temporal_v2`. Khác v1 ở chỗ model nhận
feature temporal đa khung thay vì OHLCV của một nến hiện tại:

| feature | định nghĩa causal |
|---|---|
| `return_1` | log-return close hiện tại so với 1 nến trước |
| `return_3` | log-return close hiện tại so với 3 nến trước |
| `return_12` | log-return close hiện tại so với 12 nến trước |
| `realized_vol_12` | độ lệch chuẩn 12 log-return gần nhất |
| `volume_surprise_24` | z-score log-volume hiện tại so với 24 nến trước |

Mỗi feature chỉ đọc nến đã đóng và lịch sử trước thời điểm quyết định. 24
nến đầu mỗi split được giữ Hold cho warm-up; label của hàng `t` là hướng
close-to-close của nến `t+1`. Logistic model được fit một lần trên train,
mean/std của feature cũng chỉ lấy từ train. Threshold cố định
`{0.50, 0.55, 0.60}` được chọn trên validation theo realized PnL, chỉ nhận
threshold có ít nhất 20 lệnh validation; holdout được đọc sau selection và
không refit.

Cost-aware simulator dùng đúng engine nghiên cứu hiện tại: fee 5 bps,
slippage 2 bps, fixed funding 1 bps, starting equity 10.000 USD, split
60/20/20, interval 5m, `days=500`, cutoff
`2025-04-01T00:00:00Z`. Hai route chạy song song trong Docker image rebuilt
từ source hiện tại, mỗi container giới hạn 2 CPU, 4 GiB RAM, 6 GiB swap,
qua SSH tunnel read-only tới Finance MW.

## Kiểm tra code và dữ liệu

- Adapter là module research-only trong `finance-research`; không thêm vào
  `StrategyKind`, deployment rules hay worker production.
- Unit tests causal/warm-up/label boundary: **3 passed**.
- Full `cargo test -p finance-research`: **166 passed**, fmt check sạch.
- Docker release build `finance-research-local:latest`: exit 0.
- XAU candle-count: **96.234**, holdout 19.247, calendar span 102,236 ngày;
  5m `unverified_gap_count=0`, session gaps 357 / 47.202 candles.
- BTC candle-count: **144.001**, holdout 28.800, calendar span 100,000 ngày;
  5m `unverified_gap_count=0`.
- Hai container exit 0; sau run không còn container research Round 253.

## Kết quả train/validation/holdout

### XAU/Exness — route ưu tiên

Threshold được chọn: **0,50**. Threshold 0,55 có 19 validation trades và
threshold 0,60 có 1, nên cả hai bị loại bởi minimum 20.

| threshold | train PnL / trades / PF | validation PnL / trades / PF | holdout PnL / trades / PF |
|---:|---:|---:|---:|
| 0,50 | -62,0698 / 8.967 / 0,0229 | -22,8990 / 3.241 / 0,0119 | -22,4909 / 3.231 / 0,0097 |
| 0,55 | -0,7823 / 127 / 0,7725 | -0,9357 / 19 / 0,2215 | +0,0204 / 16 / 1,1586 |
| 0,60 | +0,4529 / 16 / 1,2244 | -0,2450 / 1 / 0,0000 | -0,0624 / 1 / 0,0000 |

Selected holdout: 3.231 trades, win rate **3,22%**, max drawdown fraction
0,002249, funding paid 0,1225 USD, estimated **221,22 trades/week**.
The small positive 0,55 holdout is not eligible for selection and is not
evidence of improvement.

### BTC/Binance — transfer route

Threshold được chọn: **0,60** vì validation có 24 trades và realized PnL cao
hơn hai threshold đủ điều kiện còn lại. Tuy nhiên dấu dương không sống qua
validation/holdout.

| threshold | train PnL / trades / PF | validation PnL / trades / PF | holdout PnL / trades / PF |
|---:|---:|---:|---:|
| 0,50 | -147,2077 / 21.318 / 0,1390 | -47,6086 / 6.915 / 0,1392 | -48,2157 / 6.917 / 0,1631 |
| 0,55 | -5,4456 / 621 / 0,7744 | -2,9699 / 175 / 0,5987 | -2,2307 / 242 / 0,7484 |
| 0,60 | +0,7637 / 114 / 1,1102 | -0,9706 / 24 / 0,6642 | -0,2172 / 45 / 0,9455 |

Selected holdout: 45 trades, win rate **62,22%**, max drawdown fraction
0,000221, funding paid 0,0130 USD, estimated **484,19 trades/week**. Đây là
train-positive nhưng validation và holdout đều âm; không phải OOS improvement.

## Phân loại và giới hạn

**REJECTED** cho identity `logistic_regression_temporal_v2`.

- XAU/Exness là route ưu tiên nhưng lỗ mạnh trên cả ba split.
- BTC/Binance không giữ được dấu dương của train ở validation hoặc holdout.
- Kết quả có trade count rất cao ở threshold 0,50, nhưng tần suất không được
  dùng để biến PnL âm thành tín hiệu tốt.
- Đây là một cutoff holdout disjoint so với các cửa sổ trước trong arc
  nghiên cứu, nhưng không phải bằng chứng độc lập thứ hai cho riêng schema
  v2; không có lý do để promote một candidate đã fail route ưu tiên.
- Plain Alpha output không có Sharpe/Sortino hay Portfolio-faithful decision
  rate; các trường đó để trống trong CSV, không suy diễn từ PnL signal-only.

Không tạo OpenSpec/OPS, không pin provider, không đổi Portfolio configuration
hay production. Portfolio layer không còn lever mở trong backlog đã đăng ký;
vòng này không lặp lại các knob đã đóng. ML family vẫn mở cho một model hoặc
feature mechanism khác, nhưng không test lại v1/v2 như biến thể threshold.

## Artifacts

- `research/quant/reports/optimize_loop_update_v2.csv`: hai row Alpha cho
  XAU/Exness và BTC/Binance, metric holdout selected threshold; metric không
  có trong tool để trống.
- `research/quant/index.md`: cập nhật điều hướng item 8 và Round 451.
- Raw JSON/stderr của hai container được lưu tạm trong `/tmp` trong phiên;
  stderr chứa candle-count/gap records dùng để đối soát ở trên.
