# Round 93 (2026-08-22) — Heikin-Ashi smoothed momentum (cơ chế mới thứ 3 trong phiên) — ĐÓNG, và tổng hợp 1 pattern quan trọng: cả 3 cơ chế mới đều hội tụ về cùng 1 "trần" PF ~0.7-0.85

Status: research, code candidate thêm vào `finance-research/src/strategies.rs`
(cùng file uncommitted với Donchian Round 88 và Keltner Round 91, cả 3 chờ
Codex review 1 lượt).

## Bối cảnh

Sau Donchian (Round 88, breakout thuần giá) và Keltner reversion (Round 91,
mean-reversion ATR-band), thử cơ chế thứ 3 hoàn toàn khác dạng: **biến đổi
chính chuỗi OHLC trước khi đánh giá tín hiệu** — Heikin-Ashi (nến trung bình
trượt: `ha_close=(o+h+l+c)/4`, `ha_open=(prev_ha_open+prev_ha_close)/2`) lọc
nhiễu 1 nến đơn lẻ, phổ biến trong nội dung TikTok/YouTube trading (Rule 3),
chưa từng xuất hiện trong chương trình.

## Implementation

`HeikinAshiMomentumStrategy`: vào lệnh đúng nến mà màu HA đảo chiều (bear→bull
hoặc ngược lại) SAU KHI đã có `confirm_candles` nến HA liên tiếp cùng màu cũ
— đòi hỏi đảo chiều thật sau consolidation, không phản ứng với 1 wick đơn lẻ.
4 biến thể `confirm_candles` (1/3/5/10). `cargo build`/`fmt --check` sạch.

## Kết quả — sweep PF 3-split, 5 năm, cả 4 route

| confirm_candles | BTC/binance (holdout) | BTC/exness (holdout) | XAU/binance (holdout) | XAU/exness (holdout) |
|---|---|---|---|---|
| 1 | 0.22 | 0.23 | 0.09 | 0.17 |
| 3 | 0.30 | 0.30 | 0.12 | 0.23 |
| 5 | 0.42 | 0.41 | 0.18 | 0.30 |
| 10 | 0.71 | 0.65 | 0.33 (train/val: 0.55/0.82, không đơn điệu, n mỏng) | 0.72 |

Đơn điệu tăng theo `confirm_candles` trên hầu hết route (trừ XAU/binance có
1 điểm dao động, mẫu nhỏ n=148-149 — cùng dạng nhiễu-mẫu-mỏng đã thấy xuyên
suốt chương trình cho route này). Tại `confirm_candles=1` (không cần
consolidation trước), tần suất RẤT cao (n=26,000-80,000 trade/5 năm!) —
gần như trade mỗi lần màu HA đổi, PF cực thấp (0.06-0.29) do phí/slippage ăn
mòn từ giao dịch quá dày. Kéo dài `confirm_candles` giảm tần suất mạnh
(80,486→934 trade ở BTC/binance) và tăng PF đáng kể nhưng KHÔNG vượt 1.

## Đóng — không promote

Toàn bộ 16 ô (4 tham số × 4 route) đều PF<1. Không có candidate.

## Phát hiện tổng hợp quan trọng — "trần" PF hội tụ chung cho cả 3 cơ chế mới thử trong phiên này

| Cơ chế | Tham số dài nhất test | PF trần đạt được (BTC, holdout) |
|---|---|---|
| Donchian breakout (Round 88) | period=200 | 0.76-0.82 |
| Keltner reversion (Round 91) | multiplier=2.5 | 0.73-0.78 |
| Heikin-Ashi momentum (Round 93) | confirm=10 | 0.65-0.71 |

**Cả 3 cơ chế HOÀN TOÀN khác nhau về bản chất** (breakout kênh giá thuần túy,
mean-reversion theo ATR-band, và biến đổi OHLC lọc nhiễu) nhưng đều hội tụ về
cùng vùng PF **~0.65-0.82** khi kéo dài tham số (giảm tần suất/tăng "bộ nhớ"
tín hiệu) trên BTC, KHÔNG BAO GIỜ vượt 1 dù có xu hướng monotonic rõ ràng
tiến gần 1. Diễn giải hợp lý nhất: trần này phản ánh cấu trúc chi phí cố định
của hệ thống (phí + slippage + spread mỗi lệnh, khoảng 7bps/lệnh theo cấu
hình `fee_bps=5, slippage_bps=2`) áp lên MỌI cơ chế kỹ thuật ở khung 5m, chứ
không phải điểm yếu riêng của từng indicator cụ thể — khớp với ghi nhận tổng
quát đã có trong `SUMMARY-priority-backlog.md` ("không gian tìm kiếm bằng bộ
chỉ báo kỹ thuật chuẩn đã gần cạn ở khung 5m") nhưng giờ có bằng chứng định
lượng cụ thể hơn: 3 cơ chế độc lập, hội tụ về cùng độ lớn trần.

## Ý nghĩa cho các round sau

Nếu giả thuyết "trần chi phí cấu trúc" đúng, tiếp tục tìm thêm cơ chế kỹ
thuật MỚI (biến thể khác của breakout/reversion/momentum) khó có khả năng
vượt qua trần ~0.8 chỉ bằng cách đổi công thức tín hiệu — cần 1 trong 2
hướng khác hẳn: (1) giảm tần suất trade xuống rất thấp (kiểu swing 4h/1d đã
thử, đổi lại tần suất quá thấp không đạt Target 3), hoặc (2) giảm chi phí
mỗi lệnh (fee/slippage thực tế, ngoài tầm kiểm soát research), hoặc (3) tìm
được nguồn thông tin thực sự mới (không phải biến đổi của giá/volume đã thử
— dữ liệu vĩ mô, on-chain, sentiment, v.v., ngoài phạm vi dữ liệu OHLCV hiện
có trong `finance-research`).

## Việc cho Codex

- **[trading][low]** Review gộp 3 candidate cùng file (Donchian Round 88,
  Keltner Round 91, Heikin-Ashi Round 93) trong `finance-research/src/strategies.rs`
  — `cargo test -p finance-research` xanh, commit làm bản ghi hoặc revert.
  Không cấp bách.
