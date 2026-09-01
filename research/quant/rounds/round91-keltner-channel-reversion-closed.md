# Round 91 (2026-08-22) — Keltner Channel mean-reversion (cơ chế mới, chưa từng test standalone) — ĐÓNG, PF<1 nhất quán, không dấu hiệu overfit

Status: research, code candidate mới thêm vào `finance-research/src/strategies.rs`
(research-only, chưa commit — cùng file với Round 88's `donchian_breakout`,
cả 2 đều chờ Codex review chung 1 lượt).

## Bối cảnh

Keltner Channel (EMA midline + ATR-based band) trước giờ CHỈ xuất hiện trong
`bollinger_keltner_squeeze` (Round 70, đã đóng) — dùng để so sánh độ rộng
với Bollinger Band, chưa từng đứng riêng làm tín hiệu mean-reversion độc
lập. Khác `BollingerReversionStrategy` (đã đóng, Round 24) trên 2 trục cùng
lúc: midline EMA (trọng số gần) thay vì SMA (trọng số đều), và độ rộng band
dùng ATR (bắt được gap/wick) thay vì độ lệch chuẩn giá đóng cửa.

## Implementation

`KeltnerReversionStrategy`: entry khi close chạm band trên/dưới (kỳ vọng hồi
về EMA giữa), cùng pattern với `BollingerReversionStrategy` — chỉ đổi nguồn
band. 3 biến thể multiplier (1.5/2.0/2.5) bracket hẹp/chuẩn/rộng, period=20
khớp tham số chuẩn `bollinger_reversion` để so sánh công bằng. `cargo build`/
`fmt --check` sạch trong Docker `--cpus=3`.

## Kết quả — sweep PF 3-split, 5 năm, cả 4 route

| Route | multiplier=1.5 (holdout) | multiplier=2.0 (holdout) | multiplier=2.5 (holdout) |
|---|---|---|---|
| BTC/binance | 0.58 | 0.74 | 0.73 |
| BTC/exness | 0.59 | 0.75 | 0.78 |
| XAU/binance | 0.24 | 0.38 | 0.42 |
| XAU/exness | 0.45 | 0.49 | 0.54 |

## Phân tích

**Toàn bộ 12 ô (3 tham số × 4 route) đều PF<1 cả 3 split (train/validation/
holdout), không có ô nào đảo chiều/không nhất quán** — khác hẳn Donchian
(Round 88, có vài ô PF>1 nhưng mâu thuẫn cross-broker). Đây là kết quả "thua
lỗ sạch", cùng dạng với `bollinger_reversion` gốc đã đóng ở Round 24 — thêm
bằng chứng cho kết luận tổng quát của chương trình: cơ chế mean-reversion về
band thống kê (dù dùng std-dev hay ATR) không có edge ở khung 5m cho cả BTC
lẫn XAU, bất kể midline là SMA hay EMA.

BTC vẫn tốt hơn XAU đáng kể ở mọi tham số (giống pattern đã thấy xuyên suốt
chương trình) — XAU/binance đặc biệt yếu (0.24-0.42), phù hợp với việc XAU
nhìn chung range/mean-revert kém trên khung 5m so với BTC.

## Kết luận — ĐÓNG

Không promote candidate nào. Giữ code trong `strategies.rs` làm bản ghi
(cùng lô với Donchian Round 88, chờ Codex review 1 lần).

## Việc cho Codex

- **[trading][low]** Review gộp cả `donchian_breakout` (Round 88) và
  `keltner_reversion` (Round 91) trong `finance-research/src/strategies.rs`
  — 1 file, `cargo test -p finance-research` xanh, commit làm bản ghi
  permanent-candidate-grid hoặc revert nếu không cần giữ. Không cấp bách.
