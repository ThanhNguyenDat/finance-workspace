# Round 73 (2026-08-21) — Trend-filter order-flow imbalance: "gần đạt nhất" cho chiều dữ liệu này, vẫn chưa đủ

Status: dev + research. Tiếp nối tự nhiên Round 72 — áp đúng kiến trúc trend
filter (Round 33's phát hiện chính: nguồn edge DUY NHẤT tìm được trong toàn
bộ chương trình) lên tín hiệu order-flow vừa implement.

## Ý tưởng

Round 72 đóng order-flow imbalance vì plain (không filter) thua lỗ nặng cả 2
hướng. Nhưng MỌI candidate khác trong `multi_timeframe_candidates()` (grid
tìm kiếm chính của chương trình) đều được test qua đúng kiến trúc: gate tín
hiệu entry bằng xu hướng khung thời gian cao hơn. Chưa test order-flow theo
cách này — bước tiếp theo tự nhiên, không phải tìm cơ chế hoàn toàn mới.

## Implement

Thêm `mtf_taker_imbalance_0_60_sma10_trend_filtered` và
`mtf_taker_imbalance_fade_0_60_sma10_trend_filtered` vào
`multi_timeframe_candidates()` — bọc `TakerImbalanceStrategy`/
`TakerImbalanceFadeStrategy` (Round 72) trong `MultiTimeframeTrendFilterStrategy`
(SMA10, higher_interval=4h), đúng cấu trúc mọi candidate khác dùng.

## Backtest (5 năm, BTC + XAU/binance, base=5m, higher=4h)

**BTC:**
| Strategy | Split | Trades | Win rate | PF |
|---|---|---|---|---|
| `mtf_taker_imbalance_0_60...` | Train | 1209 | 23.0% | 0.777 |
| | Validation | 376 | 27.4% | 0.859 |
| | Holdout | 383 | 25.8% | 0.686 |
| `mtf_taker_imbalance_fade_0_60...` | Train | 1209 | 25.1% | 0.859 |
| | Validation | 376 | 26.1% | 0.905 |
| | Holdout | 383 | 25.6% | 0.691 |

**PF cải thiện RÕ RỆT nhờ trend filter: 0.19-0.29 (plain, Round 72) → 0.69-0.91
(có filter) — xác nhận filter cũng giúp được chiều dữ liệu order-flow này,
không chỉ oscillator/momentum như đã biết.** Nhưng vẫn dưới 1.0 nhất quán cả
3 split — chưa đủ để promote.

**XAU:**
| Strategy | Split | Trades | Win rate | PF |
|---|---|---|---|---|
| `mtf_taker_imbalance_0_60...` | Train | 138 | 29.0% | **1.799** |
| | Validation | 58 | 31.0% | 0.669 |
| | Holdout | 48 | 20.8% | 0.712 |
| `mtf_taker_imbalance_fade_0_60...` | Train | 140 | 29.3% | **1.476** |
| | Validation | 58 | 29.3% | 0.587 |
| | Holdout | 48 | 20.8% | 0.741 |

**XAU cho dạng đáng ngờ NGƯỢC LẠI với pattern đã cảnh giác trước đây:**
train PF cao (1.48-1.80) rồi SỤP xuống validation/holdout (0.59-0.74) — đây
là dạng overfitting kinh điển (train khớp nhiễu, không generalize), khác với
dạng "yếu train, mạnh dần" đã bị phủ định nhiều lần trước đó nhưng CŨNG đáng
ngờ tương đương — cả 2 dạng lệch giữa các split đều là dấu hiệu không đáng
tin, chỉ khác hướng.

## Kết luận: đóng — gần đạt nhất cho chiều dữ liệu này, nhưng chưa đủ

Đây là kết quả TỐT NHẤT từng đạt được cho order-flow imbalance (và một
trong những cải thiện tương đối lớn nhất khi thêm trend filter trong toàn
chương trình — gấp 3-4 lần PF gốc), nhưng vẫn KHÔNG đạt PF>1 nhất quán trên
cả 2 instrument. Đóng candidate, cập nhật comment code. Không log task
implement cho Codex — chưa đạt bar.

## Đã làm

- Build + test qua Docker: 32/32 pass, fmt sạch.
- Backtest thật (5 năm, BTC+XAU/binance, base=5m/higher=4h).
- Cập nhật comment code.
- Commit `8249bcd`, push, CI đang chạy (research-tool-only, chỉ đổi
  `finance-research` — kỳ vọng `deploy=false` giống Round 72).
