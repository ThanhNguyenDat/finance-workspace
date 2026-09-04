# Round 450 — REJECTED: logistic regression trên OHLCV không vượt qua selection gate hoặc chuyển giao XAU/BTC

## Phạm vi và trạng thái

- Operator iteration theo launcher: **252**. Không gọi `begin-iteration` và không tăng iteration lần nữa.
- Thời gian vận hành: 2026-09-04, UTC+7 / `Asia/Ho_Chi_Minh`.
- Mục tiêu: tiếp tục item 8 mục 0.5 bằng adapter Alpha research-only; không wiring production và không tạo OpenSpec/OPS.
- Route ưu tiên XAU: `exness/cfd/XAU/USD`, sau đó kiểm tra chuyển giao `binance/perpetual_future/BTC/USDT`.
- Input cố định: interval `5m`, `days=500`, `--as-of 2025-04-01T00:00:00Z`, train/validation/holdout = 60/20/20, fee 5 bps, slippage 2 bps, fixed funding 1 bps.

## Phương pháp

Adapter `logistic_regression_ohlcv_v1` chạy research-only trong `finance-research`. Model fit một lần trên train, dùng năm feature OHLCV đã chuẩn hoá bằng mean/std của train: `body_return`, `range_return`, `close_location`, `log_volume`, `log_trades`. Nhãn của nến hiện tại là hướng close-to-close của nến kế tiếp trong cùng train window; lúc phát tín hiệu chỉ đọc nến hiện tại đã đóng. Threshold cố định `{0.50, 0.55, 0.60}` được đánh giá trên validation; chỉ threshold có ít nhất 20 lệnh validation được phép thắng selection. Holdout được đọc sau selection, không refit.

Code/test evidence:

- `linfa 0.8.1`, `linfa-logistic 0.8.1`, `ndarray 0.16.1` được lock trong `finance-live-action`.
- `cargo fmt --all` sạch; `cargo test -p finance-research`: **163 passed**.
- Docker image `finance-research-local:latest` build release thành công.
- Hai container bounded tối đa 2 CPU / 4 GiB RAM / 6 GiB swap, chạy song song; exit code đều 0 và sau đó không còn container research.

## Kết quả unseen-data

### XAU/Exness

Validity gate: **96.234 candles**, train 57.740, validation 19.247, holdout 19.247; holdout 102,236 ngày lịch; `unverified_gap_count=0` và `unverified_gap_candles=0`.

| threshold | train pnl / trades / PF | validation pnl / trades / PF | holdout pnl / trades / PF |
|---:|---:|---:|---:|
| 0,50 | -158,5431 / 22.659 / 0,0099 | -59,3903 / 8.529 / 0,0057 | -60,7054 / 8.607 / 0,0035 |
| 0,55 | 0,0000 / 0 / — | 0,0000 / 0 / — | 0,0000 / 0 / — |
| 0,60 | 0,0000 / 0 / — | 0,0000 / 0 / — | 0,0000 / 0 / — |

Selection gate loại 0,55 và 0,60 vì không đạt 20 lệnh validation; threshold 0,50 được chọn nhưng lỗ nặng trên cả ba split. Win rate holdout là 0,953%.

### BTC/Binance

Validity gate: **144.001 candles**, train 86.401, validation 28.800, holdout 28.800; holdout xấp xỉ 100 ngày lịch; `unverified_gap_count=0` và `unverified_gap_candles=0`.

| threshold | train pnl / trades / PF | validation pnl / trades / PF | holdout pnl / trades / PF |
|---:|---:|---:|---:|
| 0,50 | -298,1583 / 43.115 / 0,1104 | -97,2519 / 13.857 / 0,1009 | -97,5944 / 13.812 / 0,1240 |
| 0,55 | -1,2939 / 305 / 0,9276 | **+1,0951 / 76 / 1,3957** | **+0,7839 / 133 / 1,1779** |
| 0,60 | -0,2118 / 20 / 1,0065 | 0,3893 / 4 / 1,5659 | -1,0690 / 11 / 0,3232 |

Threshold 0,55 được chọn từ validation sau khi áp minimum 20 lệnh, nhưng train vẫn âm; threshold 0,60 bị loại do validation chỉ 4 lệnh. Holdout dương của 0,55 chỉ là một kết quả route/window cụ thể, không đủ bù cho train âm, XAU thất bại và không có bằng chứng walk-forward thứ hai.

## Classification và giới hạn

**REJECTED** cho identity `logistic_regression_ohlcv_v1`. Không promote, không OpenSpec/OPS, không thay đổi production hay Portfolio configuration. Portfolio layer chỉ được chạy kèm theo command hiện hữu để giữ research context; các lever Portfolio cổ điển trong backlog đã đóng nên round này không lặp lại chúng.

ML item 8 vẫn mở ở mức family cho một cơ chế thực sự khác (ví dụ model/feature schema đã đăng ký mới); identity logistic với feature schema và threshold grid này không được test lại. Round này chưa đo Sharpe/Sortino/decision-rate Portfolio cho Alpha candidate vì plain Alpha sweep không cung cấp các metric đó; không suy diễn chúng từ PnL signal-only. Mọi số liệu trên là mô phỏng có cost trong Docker, không phải broker truth hay production performance.

Evidence source: `optimize_loop_update_v2.csv` rows `450`, cùng raw JSON/log được tạo từ hai command Docker trong round này.
