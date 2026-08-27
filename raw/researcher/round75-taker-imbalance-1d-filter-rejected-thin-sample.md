# Round 75 (2026-08-21) — Thử higher_interval=1d cho order-flow imbalance: pattern đáng ngờ lặp lại, nhưng mẫu quá mỏng để tin

Status: research. Tiếp tục thread order-flow (Round 72-73), thử 1 tham số
chưa từng biến thiên trong toàn chương trình: higher_interval của trend
filter (luôn cố định 4h từ Round 17 tới giờ).

## Ý tưởng

`--higher-timeframe-interval` là CLI flag, đổi được mà không cần sửa code.
Chưa ai từng thử `1d` thay vì `4h` mặc định cho bất kỳ candidate MTF nào
trong 74 round trước. Test lại đúng `mtf_taker_imbalance_0_60/fade`
(Round 73) với `--higher-timeframe-interval 1d`.

## Kết quả: BTC lộ pattern "yếu train, mạnh dần" — ĐÃ CẢNH GIÁC TRƯỚC ĐÂY

**BTC/binance, 5 năm:**
| Split | Trades | PF |
|---|---|---|
| Train | 206 | 0.874 |
| Validation | 59 | **1.082** |
| Holdout | 67 | **1.021** |

Test lại trên window độc lập 18 tháng (đúng phương pháp Round 34):

**BTC/binance, 18 tháng:**
| Split | Trades | PF |
|---|---|---|
| Train | 53 | 0.922 |
| Validation | 24 | **1.035** |
| Holdout | 16 | **1.325** |

**Pattern "yếu train, mạnh dần" lặp lại y hệt trên CẢ 2 window độc lập** —
nhưng mẫu quá mỏng để tin: holdout window 18 tháng chỉ có **16 trade**, dưới
ngưỡng tối thiểu ~20-30 đã thiết lập từ Round 49. Window 5 năm khá hơn
(67 trade holdout) nhưng vẫn nhỏ.

## XAU: thất bại hoàn toàn, cả về mẫu lẫn hướng

**XAU/binance, 5 năm:**
| Split | Trades | PF |
|---|---|---|
| Train | 18 | 1.273 |
| Validation | 7 | 0.564 |
| Holdout | 15 | 0.528 |

Tổng cộng chỉ 40 trade trong CẢ 5 NĂM (do nến 1d đổi xu hướng quá hiếm,
filter quá chặt ở base interval 5m) — hoàn toàn không đủ để đánh giá. Và
pattern lại NGƯỢC (mạnh train, yếu dần) — kiểu overfitting kinh điển khác.

## Kết luận: đóng, không đủ tin cậy

Dù pattern "yếu train mạnh dần" lặp lại nhất quán trên BTC ở 2 window độc
lập (có thể gợi ý đây không hoàn toàn là nhiễu ngẫu nhiên), **mẫu quá mỏng
để kết luận** (16 trade holdout ở window ngắn), và **thất bại rõ ràng trên
XAU** (mẫu còn mỏng hơn, hướng pattern ngược lại). Theo đúng kỷ luật đã áp
dụng xuyên suốt chương trình (Round 56: cần cross-instrument mới tin), đóng
candidate này.

## Đã làm

- Backtest qua Docker (không cần build lại — chỉ đổi CLI flag).
- Cập nhật comment code ghi lại kết quả tránh lặp lại thử nghiệm này.
- Commit `e19fddf` (comment-only), push, CI đang chạy.

## Không log task cho Codex

Kết quả phủ định, tự đóng trong round — không cần action item.
