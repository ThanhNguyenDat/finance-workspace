# Round 117 (2026-08-23) — Three White Soldiers / Three Black Crows (pattern 3 nến liên tiếp, mới hoàn toàn) — ĐÓNG

Status: research, thêm `ThreeCandleContinuationStrategy` (candidate mới,
không tham số) vào `finance-research/src/strategies.rs`. Chạy 4 route 5
năm, 2 cặp song song (`--cpus=2 --memory=4g --memory-swap=6g`, Rule 9).

## Bối cảnh

Không có commit mới từ Codex, 2 bug Bybit (Round 116) vẫn chưa được xử lý
(chưa có Processing/Dev-done mới). Round102 follow-up còn chờ market mở
cửa lại. Round 117 test **Three White Soldiers/Black Crows** — pattern 3
nến liên tiếp cùng màu, mỗi nến mở trong thân nến trước, close tăng/giảm
dần — khác hẳn Engulfing 2 nến (Round 103) về hình học (containment 1 lần
vs continuation 3 lần).

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật)

| Route | train PF | valid PF | holdout PF | win% (holdout) | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | 0.526 | 0.444 | 0.466 | 25.7% | 4,966 |
| BTC/exness | 0.630 | 0.513 | 0.605 | 31.3% | 2,240 |
| XAU/binance | 0.367 | 0.298 | 0.280 | 18.1% | 647 |
| XAU/exness | 0.336 | 0.420 | 0.451 | 29.5% | 1,611 |

BTC/exness là ô tốt nhất (0.605-0.630) nhưng vẫn cách xa breakeven. Không
ô nào gần 1.0 nên không cần cross-check 18 tháng.

## Kết luận — ĐÓNG

Không promote. Pattern continuation 3 nến thô không đủ edge, cùng nhóm kết
quả với Engulfing 2 nến (Round 103) — cả 2 dạng pattern nến thuần hình học
(không có yếu tố volume/oscillator) đều thất bại trong chương trình này.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu
  `ThreeCandleContinuationStrategy` làm bản ghi closed-candidate
  (research-only), hoặc revert nếu không cần giữ.
