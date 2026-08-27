# Round 88 (2026-08-22) — Donchian Channel breakout (Turtle Trading), cơ chế MỚI chưa từng test trong chương trình — ĐÓNG, PF<1 nhất quán BTC, XAU không ổn định cross-broker

Status: research, code candidate mới thêm vào `finance-research/src/strategies.rs`
(research-only, chưa commit — theo narrowed rule hiện tại, log Todo cho Codex
review). Đầu round đã đóng 4 mục Verify trading khác sang Done (Exness
`last_event` timestamp fix, finance-broker C++ cleanup, kline-ingest gap,
Exness backfill/sync) sau khi verify độc lập qua `gh run view` + `git
merge-base --is-ancestor` + `docker inspect` trực tiếp.

## Bối cảnh

Ưu tiên Rule 1 (Portfolio-construction) đã khá bão hòa sau round 84-87
(sizing mode, R:R ratio, factorial interaction đều đã test). Theo hướng dẫn
"ưu tiên nội bộ" trong `SUMMARY-priority-backlog.md`, quay lại Rule 2/3 (tìm
cơ chế Alpha mới) khi có ý tưởng thực sự mới — Donchian Channel breakout
(luật entry gốc của hệ thống Turtle Trading, 1 trong những chiến thuật trend-
following cơ học lâu đời nhất) chưa từng xuất hiện trong bảng "Đã ĐÓNG" của
chương trình này, khác cơ chế với `atr_breakout` (đo *độ lớn move* so với ATR)
và `opening_range_breakout` (kênh session cố định theo giờ) — đây là kênh
rolling liên tục theo giá thuần tuý, không dùng thống kê biến động.

## Implementation

Thêm `DonchianBreakoutStrategy` vào `finance-research/src/strategies.rs`:
entry khi close vượt highest-high/thấp hơn lowest-low của `period` nến TRƯỚC
đó (không tính nến hiện tại — tránh lookahead, theo đúng pattern
`AtrBreakoutStrategy` đã dùng: đọc window trước, push sau). 4 biến thể period
(20/55/100/200) bracket từ ngắn tới dài, 20 = tham số chuẩn "System 1" gốc
Turtle. `cargo build`/`cargo fmt --check` sạch trong Docker `--cpus=3`.

## Kết quả — sweep PF/win-rate 3-split, 5 năm, cả 4 route

| Route | period=20 | period=55 | period=100 | period=200 |
|---|---|---|---|---|
| BTC/binance (holdout) | 0.55 | 0.65 | 0.76 | 0.82 |
| BTC/exness (holdout) | 0.57 | 0.66 | 0.77 | 0.81 |
| XAU/binance (train/val/holdout) | 0.44/0.43/0.41 | 0.82/0.93/0.80 | **1.05/1.17/0.92** | **1.26/1.11/0.76** |
| XAU/exness (train/val/holdout) | 0.33/0.38/0.60 | 0.48/0.57/0.87 | 0.56/0.76/0.93 | 0.72/0.87/**1.09** |

## Phân tích

**BTC (cả 2 broker): PF tăng đơn điệu theo period nhưng luôn <1 (đỉnh 0.81-0.82
tại period=200), cross-broker khớp gần như y hệt.** Cùng dạng "anchor point"
đã thấy với `ema_crossover_12_26_sma10` tại 30m (round 78) — không có edge
thật, chỉ là chiến thuật ít lỗ nhất tìm được, không đạt bar.

**XAU: có vài ô PF>1 nhưng KHÔNG nhất quán — đúng dạng false-positive đã biết.**
- XAU/binance period=200: train=1.26, validation=1.11 (đều >1) nhưng
  **holdout sụt xuống 0.76** (tệ hơn cả period=100's holdout 0.92) — dạng
  "đẹp early, tệ late", mẫu holdout chỉ 36 trade (quá mỏng).
- XAU/exness period=200: train=0.72, validation=0.87, **holdout=1.09** (duy
  nhất >1) — dạng "yếu train, mạnh holdout", đúng chính xác pattern skill đã
  cảnh báo ("weak train, strong later splits... known false-positive shape").
- Hai broker cho kết quả PF>1 ở **2 split đối lập nhau** (binance mạnh
  đầu/yếu cuối, exness yếu đầu/mạnh cuối) — nếu là edge thật, kỳ vọng nhất
  quán hướng cross-broker như BTC đã thể hiện. Sự đối lập này tự nó là bằng
  chứng mạnh cho nhiễu/overfit, không phải tín hiệu thật.

## Kết luận — ĐÓNG

Donchian Channel breakout không có edge thật ở khung 5m cho cả BTC lẫn XAU,
mọi period test được. Không promote candidate nào. Giữ code trong
`strategies.rs` làm bản ghi vĩnh viễn (theo đúng convention các candidate đã
đóng khác như `BollingerKeltnerSqueezeStrategy`/`AtrBreakoutStrategy`), không
đụng `finance-strategy`/production.

## Việc cho Codex

- **[trading][low]** Review 4 file thay đổi (chỉ `finance-research/src/strategies.rs`,
  không chạm production): xác nhận `cargo test -p finance-research` xanh rồi
  commit làm bản ghi permanent-candidate-grid (giống các candidate đã đóng
  khác), hoặc revert nếu không cần giữ lại. Không cấp bách — đây không phải
  bug hay lever cải thiện Target 1/2, chỉ là kết quả nghiên cứu đã đóng.
