# Round 99 (2026-08-23) — Lọc theo signal strength cho 2 candidate "cost-limited" (Round 96/98) — ĐÓNG, kết quả hứa hẹn ban đầu sụp đổ trên cửa sổ độc lập; phát hiện phụ: Keltner's strength filter vô tác dụng

Status: research, thêm `MinStrengthFilterStrategy` (wrapper mới, chưa có
trong file) + 6 candidate vào `finance-research/src/strategies.rs`
(research-only, uncommitted, cùng lô với Donchian/Keltner/Heikin-Ashi/MTF
chờ Codex review).

## Giả thuyết

Round 96/98 phân loại `keltner_reversion_20_2_5` và `heikin_ashi_momentum_10`
là "cost-limited" (raw edge ≈0 khi bỏ chi phí, không âm). Nếu raw edge ~0
không đồng đều trên mọi tín hiệu mà tập trung ở subset độ tin cậy cao
(`strength` field, 0.0-1.0, đã có sẵn trong mọi `Signal`), lọc bỏ tín hiệu
yếu có thể nâng PF của phần còn lại vượt breakeven NGAY CẢ KHI có chi phí
thật — khác `donchian_breakout` (edge-limited, không có lý do kỳ vọng lọc
strength giúp được).

## Implementation

`MinStrengthFilterStrategy`: wrapper đơn giản nhất trong file — không cần
state ngoài field `strength` sẵn có của inner signal. 3 ngưỡng (0.5/0.7/0.9)
× 2 candidate = 6 biến thể. `cargo build`/`fmt --check` sạch.

## Phát hiện phụ: `keltner_reversion`'s strength filter KHÔNG có tác dụng gì

Cả 3 ngưỡng cho `keltner_reversion_20_2_5_strength_*` ra **CHÍNH XÁC** cùng
trade count/PF như bản không lọc (2532/936/974 trade, PF y hệt tới 2 chữ số
thập phân) trên cả 2 broker — nghĩa là `strength` của `KeltnerReversionStrategy`
gần như luôn ≥0.9 trong thực tế (công thức
`((close-middle).abs()/half_width).min(1.0)` bị chạm trần 1.0 rất thường
xuyên với dữ liệu BTC). Bug/hạn chế thiết kế, không phải phát hiện chiến
thuật — strength field này không phân biệt được tín hiệu mạnh/yếu cho cơ
chế reversion cụ thể này.

## Kết quả chính — Heikin-Ashi: hứa hẹn RẤT lớn trên 5 năm, SỤP ĐỔ trên 18 tháng

### Window 5 năm (with real cost)

| Ngưỡng | BTC/binance holdout | BTC/exness holdout |
|---|---|---|
| Không lọc | 0.71 (n=935) | 0.65 (n=965) |
| ≥0.5 | 0.60 (n=159) | 0.66 (n=137) |
| ≥0.7 | 0.99 (n=77) | **1.44 (n=63)** |
| ≥0.9 | **1.90 (n=36)** | **2.98 (n=26)** |

Nhìn rất hứa hẹn — PF tăng vọt, có vẻ đúng giả thuyết.

### Cross-check 18 tháng độc lập (bắt buộc) — SỤP ĐỔ hoàn toàn

| Ngưỡng | BTC/binance (train/val/holdout) | BTC/exness (train/val/holdout) |
|---|---|---|
| ≥0.7 | 0.98/1.09/**0.27** (n=74/24/23) | 1.50/**4.56**/**0.28** (n=53/16/25) |
| ≥0.9 | 1.27/**3.38**/**0.22** (n=28/10/13) | 1.51/2.49/2.08 (n=15/10/9) |

Validation cao bất thường (tới 4.56!) trong khi holdout sụp xuống 0.22-0.28
— mẫu cực mỏng (9-25 trade/split) chính là dấu hiệu nhiễu kinh điển, không
phải edge thật. Hoàn toàn không nhất quán với hình dạng 5 năm.

## Kết luận — ĐÓNG

Kết quả "hứa hẹn" trên 5 năm là **overfit mẫu mỏng**, không phải edge thật —
đúng loại false-positive chương trình đã cảnh báo nhiều lần (ORB Round 34,
mtf_donchian Round 94, v.v.). Không promote candidate nào. Giả thuyết
"strength filter cứu được cost-limited candidate" bị bác bỏ cho Heikin-Ashi
(mẫu quá mỏng để kết luận cả 2 chiều — có thể đúng nhưng cần data nhiều hơn
384 route hiện có để test tin cậy, không khả thi với lịch sử hiện tại). Với
Keltner, filter vô nghĩa vì bản thân strength field không phân biệt được gì.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `MinStrengthFilterStrategy`
  làm bản ghi closed-candidate (cùng lô với 4 candidate khác), hoặc revert
  nếu không cần giữ — không có giá trị thực tế nào được xác nhận.
- Đóng hẳn hướng "lọc theo strength field hiện có" cho 2 candidate này —
  không test lại trừ khi có công thức strength khác hẳn (công thức hiện tại
  của Keltner vô dụng, Heikin-Ashi thì mẫu luôn quá mỏng ở ngưỡng cao để tin
  cậy được với lượng dữ liệu 5m hiện có).

## Cập nhật Round 100 — sửa lỗi trùng tên label (tự phát hiện khi reconcile với commit Codex)

Đầu Round 100, đồng bộ lại working tree với commit `9c1fbb3` (Codex đã ghi
permanent comment cho ablation XAU Round 98) thì phát hiện: 6 label tôi đặt
ban đầu (`keltner_reversion_20_2_5_strength_0_X`,
`heikin_ashi_momentum_10_strength_0_X`) VÔ TÌNH trùng prefix với 2 regression
test Codex đã viết để khoá đúng grid Round 91/93
(`round91_registers_the_reviewed_keltner_multiplier_grid`,
`round93_registers_the_reviewed_heikin_ashi_confirmation_grid` — lọc theo
`name().starts_with("keltner_reversion_")`/`"heikin_ashi_momentum_"`), khiến
2 test đỏ khi build lại. Đã đổi tên 6 label sang tiền tố `min_strength_0_X_...`
(không đụng vào 2 file test của Codex), build/test lại 93/93 xanh. Số liệu
backtest trong file này không đổi (chỉ đổi tên hiển thị của candidate, không
chạy lại backtest) — nội dung phân tích ở trên vẫn đúng nguyên vẹn.
