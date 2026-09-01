# Round 58 (2026-08-21) — `rsi_mean_reversion_14_20_80` tốt hơn bản đang live, xác nhận cross-instrument

Status: research, dùng sweep table thường (vẫn hoạt động đầy đủ sau thay
đổi tool Round 55). Tiếp nối Round 57 (test tham số thay thế cho
`candle_momentum`) — round này làm tương tự cho `rsi_mean_reversion`,
strategy Alpha thứ 2 đang live (config hiện tại: `14_30_70`).

## Kết quả: `14_20_80` (biên rộng hơn) tốt hơn `14_30_70` đang live, NHẤT QUÁN cả 3 split VÀ cả 2 instrument

### BTC/binance 5m
| Config | Train PF | Validation PF | Holdout PF |
|---|---|---|---|
| `14_30_70` (đang live) | 0.677 | 0.660 | 0.625 |
| **`14_20_80`** | **0.717** | **0.789** | **0.816** |

### XAU/binance 5m
| Config | Train PF | Validation PF | Holdout PF |
|---|---|---|---|
| `14_30_70` (đang live) | 0.522 | 0.336 | 0.271 |
| **`14_20_80`** | **0.680** | **0.595** | **0.515** |

**`14_20_80` thắng ở CẢ 3 split, CẢ 2 instrument — 6/6 phép so sánh đều
cùng hướng.** Đặc biệt ở BTC: PF của `14_20_80` còn TĂNG DẦN qua các split
(0.717→0.789→0.816) — hướng ngược lại hoàn toàn với dạng "chỉ thắng
holdout" đáng ngờ đã cảnh giác nhiều lần (train/validation cũng thắng, đây
KHÔNG phải artifact mẫu nhỏ).

## Vẫn chưa fix được Target 1 — vẫn PF<1

Cần nói rõ: `14_20_80` **vẫn thua lỗ** (PF<1 mọi trường hợp) — đây là cải
thiện tương đối thật, không phải lời giải hoàn chỉnh cho Target 1. Đánh
đổi: tần suất giảm mạnh (BTC holdout 875 trade so với 2487 của bản live,
-65%; XAU 152 so với 371, -59%) — cùng dạng trade-off tần suất/chất lượng
đã thấy xuyên suốt chương trình này (Round 19/24/33).

## So sánh với Round 57's `candle_momentum_30bps`

| | Cải thiện PF | Nhất quán 3-split | Cross-instrument | Tần suất giảm |
|---|---|---|---|---|
| `candle_momentum_30bps` (Round 57) | 0.347→0.756 (holdout) | chỉ test BTC | chưa test XAU | -87% |
| `rsi_mean_reversion_14_20_80` (round này) | 0.625→0.816 (BTC holdout) | ✓ cả 3 split | ✓ đã xác nhận | -59% đến -65% |

**`14_20_80` là bằng chứng mạnh hơn** (đã xác nhận cross-instrument + nhất
quán 3-split, không chỉ 1 instrument như candle_momentum_30bps).

## Đề xuất cho Codex

Không log task "implement/deploy ngay" (vẫn PF<1, chưa đạt Target 1) —
nhưng đây là **2 tham số riêng biệt (candle_momentum bps, rsi band) đều
cùng hướng cải thiện khi mở rộng ngưỡng/biên**, cùng đánh đổi tần suất. Gợi
ý: nếu Codex muốn thử tune production, `rsi_mean_reversion_14_20_80` là
ứng viên đáng cân nhắc nhất trong 2 (bằng chứng mạnh hơn, tần suất giảm ít
hơn) — nhưng vẫn cần kết hợp thêm đòn bẩy khác (signal mới, không chỉ
tuning tham số) để thực sự đạt Target 1, đúng kết luận nhất quán của toàn
bộ chương trình research này.
