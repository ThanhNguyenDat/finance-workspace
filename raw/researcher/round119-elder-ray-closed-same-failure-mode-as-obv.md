# Round 119 (2026-08-23) — Elder Ray Index (EMA + high/low, mới hoàn toàn) — ĐÓNG, cùng failure mode OBV Round 113

Status: research, thêm `ElderRayStrategy` (candidate mới hoàn toàn) vào
`finance-research/src/strategies.rs`. Chạy 4 route 5 năm, 2 cặp song song
(`--cpus=2 --memory=4g --memory-swap=6g`, Rule 9).

## Bối cảnh

Không có commit mới từ Codex ở finance-live-action. Trong lúc chạy round
này phát hiện Codex đang sửa live `internal/services/leverage_constraints.go`
(đúng bug tôi tìm ở Round 116) và `web/src/shared/config/compositions.ts`
— không đụng vào, tiếp tục round research bình thường. Round 119 test
**Elder Ray Index** — kết hợp EMA baseline với CẢ high lẫn low (`bull_power
= high - ema`, `bear_power = low - ema`), khác cấu trúc thuần MA-cross (1
điểm giá) hay oscillator bị chặn.

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật)

| Route | train PF | valid PF | holdout PF | win% (holdout) | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | 0.335 | 0.296 | 0.284 | 13.3% | 15,470 |
| BTC/exness | 0.348 | 0.323 | 0.295 | 13.7% | 15,183 |
| XAU/binance | 0.182 | 0.174 | 0.142 | 7.3% | 2,059 |
| XAU/exness | 0.097 | 0.124 | 0.243 | 12.3% | 10,061 |

## Nhận xét — cùng failure mode với OBV (Round 113)

Win rate rất thấp (7.1-14.5%) và tần suất tín hiệu cực cao (tới 47,494
lệnh train BTC/binance) — tín hiệu "net power cắt qua 0" quá nhạy trên 5m
vì high/low thường xuyên straddle quanh EMA baseline mỗi vài nến. Cùng dấu
hiệu overfitting-to-noise đã thấy ở OBV signal-line crossover. BTC nhất
quán cross-broker (0.335/0.296/0.284 vs 0.348/0.323/0.295) — xác nhận đây
là tín hiệu thật nhưng quá yếu/nhiễu để dùng.

Không ô nào gần breakeven nên không cần cross-check 18 tháng.

## Kết luận — ĐÓNG

Không promote. Cùng nhóm với OBV (Round 113) — 2 candidate duy nhất trong
chương trình có win rate <15% VÀ tần suất tín hiệu >10,000 lệnh/route trên
5 năm — dấu hiệu rõ ràng cho thấy các cơ chế "combined multi-source
crossover thô" (EMA+high/low, hoặc cumulative volume) không phù hợp trực
tiếp trên 5m mà không có bước làm mượt/lọc tần suất bổ sung.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `ElderRayStrategy` làm bản
  ghi closed-candidate (research-only), hoặc revert nếu không cần giữ.
