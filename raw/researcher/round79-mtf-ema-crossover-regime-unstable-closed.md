# Round 79 (2026-08-21) — Trend-filter `ema_crossover_12_26` (Round 78): pattern đảo hoàn toàn giữa 2 window, đóng

Status: research. Tiếp nối tự nhiên Round 78's phát hiện (`ema_crossover_12_26`
@ 30m — candidate ổn định nhất từng thấy) bằng cách thử trend filter, đúng
kỷ luật áp dụng cho mọi candidate khác trong chương trình.

## Implement

Thêm `mtf_ema_crossover_12_26_sma10_trend_filtered` vào
`multi_timeframe_candidates()` — bọc `EmaCrossoverStrategy` (đã là 1 cơ chế
trend-following) trong `MultiTimeframeTrendFilterStrategy` (SMA10). Câu hỏi
mở: gấp đôi trend-following (entry + filter cùng là xu hướng) có giúp
(double-confirm) hay hại (lọc quá tay, còn quá ít lệnh)?

## Backtest (30m base, 4h higher, 5 năm)

**BTC/binance:**
| Split | Trades | PF |
|---|---|---|
| Train | 250 | 1.193 |
| Validation | 86 | 0.896 |
| Holdout | 75 | **1.817** |

Dạng "lõm giữa" (thắng-thua-thắng), mẫu đủ lớn (≥75 mọi split).

**XAU/binance:**
| Split | Trades | PF |
|---|---|---|
| Train | 44 | 1.135 |
| Validation | 7 | 1.816 |
| Holdout | 14 | 0.534 |

Mẫu quá nhỏ (validation chỉ 7, holdout chỉ 14 — dưới ngưỡng tin cậy tối
thiểu ~20-30).

## Regime-dependency test (Round 34 methodology): BTC đảo pattern hoàn toàn

Test lại BTC trên window độc lập 18 tháng:

| Split | Trades | PF |
|---|---|---|
| Train | 73 | 1.780 |
| Validation | 25 | 1.178 |
| Holdout | 26 | **0.939** |

**Pattern hoàn toàn khác** window 5 năm: 18 tháng cho dạng "yếu dần đều"
(1.78→1.18→0.94), trong khi window 5 năm cho dạng "lõm giữa" (1.19→0.90→1.82).
**Cùng 1 instrument, 2 window khác nhau cho 2 hình dạng hoàn toàn khác nhau**
— đúng dấu hiệu bất ổn định/không phải edge thật đã dùng để phủ định ORB ở
Round 34.

## Kết luận: đóng — không instrument nào đứng vững

- BTC: pattern không ổn định qua 2 window độc lập.
- XAU: mẫu quá nhỏ để tin ở 2/3 split.

**Gấp đôi trend-following (entry EMA-crossover + filter SMA cùng hướng) không
tạo ra edge ổn định** — kết luận hợp lý: khi cả entry lẫn filter đều đo cùng
1 loại thông tin (xu hướng), việc lọc thêm chỉ làm giảm mẫu chứ không thêm
thông tin mới độc lập, khác với việc trend-filter giúp các mechanism KHÁC hẳn
(oscillator, order-flow) — những cái đó lọc thêm 1 chiều thông tin thực sự
mới.

## Đã làm

- Build + test qua Docker: 32/32 pass, fmt sạch.
- Backtest thật (5 năm + 18 tháng độc lập, BTC+XAU/binance).
- Cập nhật comment code.
- Commit `ddad3c8`, push, CI đang chạy.

## Bài học phương pháp luận

Củng cố thêm 1 nguyên tắc: trend filter không phải "luôn luôn tốt" một cách
vô điều kiện — nó giúp khi ENTRY và FILTER đo 2 loại thông tin độc lập (như
oscillator + xu hướng khung cao hơn), nhưng có thể vô ích hoặc hại khi cả 2
đều là cùng 1 loại tín hiệu (trend-following + trend filter).
