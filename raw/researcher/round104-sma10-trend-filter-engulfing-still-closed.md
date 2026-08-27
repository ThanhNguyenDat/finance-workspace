# Round 104 (2026-08-23) — Lọc xu hướng SMA(10) cho engulfing_pattern (Round 103) — cải thiện nhất quán nhưng vẫn ĐÓNG, còn cách xa breakeven

Status: research, thêm `SmaTrendFilterStrategy` (wrapper mới) + 1 candidate
vào `finance-research/src/strategies.rs` (research-only, uncommitted, cùng
lô chờ Codex review). Áp dụng đúng Rule 9 mới: 4 route chạy thành 2 cặp song
song (không tuần tự), mỗi container giới hạn `--cpus=2 --memory=4g
--memory-swap=6g` khớp cấu hình production (2 core/4GB RAM/2GB swap).

## Bối cảnh

Không có commit mới từ Codex kể từ Round 102 (vẫn `2840dcc`). XAU/Exness vẫn
đóng cửa cuối tuần (kiểm tra 02:47 UTC Chủ Nhật). Round 103 đóng
`engulfing_pattern` (mẫu hình nến engulfing 2 nến, chưa từng test trước đây)
với PF thấp nhất từng quan sát (0.16-0.42) nhưng xác nhận là cost-limited
(no-cost PF gần chạm 1.0) — nguyên nhân là tần suất tín hiệu quá cao. Theo
"trend filter là nguồn edge duy nhất từng cứu được 1 cơ chế channel/breakout"
(mục 3 SUMMARY, áp dụng cho Donchian Round 94), Round 104 test giả thuyết
tương tự cho engulfing.

## Implementation

`SmaTrendFilterStrategy`: bản song sinh cùng-timeframe của
`MultiTimeframeTrendFilterStrategy` — không cần `--higher-timeframe-interval`,
chỉ lọc theo hướng SMA(period) trên đúng timeframe base. Đăng ký
`sma10_trend_filtered_engulfing_pattern` (period=10, khớp convention
`sma10_trend_filtered` của Round 94). `cargo fmt` + `cargo build -p
finance-research` sạch (Docker `--cpus=3`).

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật), baseline (Round 103) vs trend-filtered

| Route | Split | PF baseline | PF filtered | Δ tuyệt đối | trades baseline→filtered |
|---|---|---|---|---|---|
| BTC/binance | holdout | 0.347 | 0.429 | +0.082 | 11197→6220 |
| XAU/binance | holdout | 0.159 | 0.211 | +0.052 | 1445→835 |
| BTC/exness | holdout | 0.420 | **0.506** | +0.086 | 6806→4066 |
| XAU/exness | holdout | 0.344 | 0.485 | +0.141 | 4647→2754 |

Cải thiện **nhất quán cả 12 ô** (3 split × 4 route), chiều dương ở mọi nơi
(+0.05 tới +0.14 tuyệt đối, ~15-40% tương đối), đi kèm giảm tần suất tín
hiệu ~35-50% (khớp giả thuyết: bớt tín hiệu ngược trend giúp giảm phần nào
gánh nặng chi phí). Ô tốt nhất (BTC/exness holdout) đạt PF 0.506 — vẫn cách
breakeven rất xa.

**Không cần cross-check cửa sổ 18 tháng độc lập** — hướng cải thiện đồng nhất
và cách xa 1.0 ở mọi ô, không phải trường hợp biên cần thêm bằng chứng (khác
Donchian Round 94 vốn có 1 ô chạm gần PF~1.0 trên 5 năm, buộc phải test tiếp).

## Kết luận — ĐÓNG

Trend-filter giúp thật (không phải nhiễu, hướng nhất quán 100%) nhưng
**không đủ để cứu candidate này** — khoảng cách còn lại (0.49-0.79 điểm PF)
lớn hơn nhiều mức trend-filter từng chứng minh có thể đóng góp (~0.05-0.14).
Khác Donchian (baseline đã gần 0.8-0.85, chỉ cần trend-filter đẩy nhẹ), gốc
`engulfing_pattern` xuất phát quá thấp (0.15-0.49) để 1 lever đơn lẻ bù đủ.
Không promote. Đóng hẳn hướng candlestick-pattern-2-nến-thô kể cả có
trend-filter.

## Cập nhật Round 105 — xác nhận bug fix doji (round103) không đổi kết luận round này

Cùng bug đã sửa ở round103 (doji trước đó bị coi sai là nến giảm) ảnh hưởng
gián tiếp `sma10_trend_filtered_engulfing_pattern` qua `inner`. Rerun
BTC/binance holdout dưới semantics đúng: PF 0.429→0.430, trades 6220→6200
(Δ<0.4%). Không đổi kết luận CLOSED.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `SmaTrendFilterStrategy` +
  `sma10_trend_filtered_engulfing_pattern` làm bản ghi closed-candidate
  (cùng lô 6 candidate khác chờ review), hoặc revert nếu không cần giữ.
- `SmaTrendFilterStrategy` là wrapper generic (nhận `inner: Box<dyn
  Strategy>` bất kỳ) — có thể tái dùng cho candidate khác trong tương lai mà
  không cần `--higher-timeframe-interval`, khác hẳn
  `MultiTimeframeTrendFilterStrategy` vốn cần 2 interval cùng lúc.
