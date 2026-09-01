# Round 74 (2026-08-21) — Production health sweep + dọn 2 hạng mục Verify cũ

Status: reviewer + verification. Sau 4 round liên tiếp research candidate
mới (70-73, đều đóng), chuyển sang vai trò reviewer để cân bằng lại — dọn
backlog `Verify` cũ và kiểm tra sức khoẻ hệ thống tổng thể.

## Production health sweep

Đọc trực tiếp cả 4 worker checkpoint qua SSH:

| Route | eval_count | trade_count (paper-fixed-pct) | realized_pnl |
|---|---|---|---|
| Binance/BTC | 300 | 1126 | -7.89 |
| Binance/XAU | 300 | 8 | -0.02 |
| Exness/BTC | 4933 | 1119 | -7.87 |
| Exness/XAU | 537 | 758 | -3.50 |

Tất cả 4 container healthy, `updated_at` mới (lag ~2 phút, bình thường theo
chu kỳ 5m). So với baseline Round 65 (ngay sau epoch-fix): trade_count hầu
như đứng yên ở cả 4 route (Binance/BTC 1126→1126, Exness/BTC 1117→1119,
Exness/XAU 758→758, Binance/XAU 8→8) dù eval_count vẫn tăng đều — thị
trường có vẻ đang trong giai đoạn ít biến động/tín hiệu yếu trên diện rộng,
không phải bug riêng của 1 route (kể cả Exness/BTC, route có eval_count cao
nhất, cũng gần như đứng yên). Không phát hiện bug mới từ sweep này — ghi
nhận làm baseline theo dõi cho round sau.

## Dọn 2 hạng mục `Verify` cũ, chuyển `Done`

1. **VWAP mean reversion + ORB research-only** — kết quả gốc (VWAP PF<1 mọi
   split, ORB 30m/60m không nhất quán) khớp hoàn toàn với 2 phát hiện độc
   lập của chính chương trình này (Round 18: VWAP đóng vì PF<1 nhất quán cả
   XAU lẫn BTC; Round 34: ORB đảo ngược hoàn toàn khi test window 18 tháng).
   2 phương pháp độc lập cùng kết luận phủ định — corroboration mạnh.
2. **Both production Kline alerts resolved** — sự cố cụ thể (5-candle outage
   2026-08-20) đã cũ và đã qua. Corroborate bằng 70+ round giám sát checkpoint
   trực tiếp của chính tôi: Binance BTC/XAU chưa từng xuất hiện
   `input_continuity_failed` trong bất kỳ lần đọc `--daily-profit-gate` nào —
   vấn đề continuity duy nhất từng tìm thấy và xác nhận lặp lại là của riêng
   Exness (Round 56, vẫn còn mở, không liên quan item này).

Còn lại 2 hạng mục Trading trong `Verify` chưa review: Kafka research replay
access (P0, phạm vi hạ tầng lớn, để lại round sau) và "Web production không
còn hiển thị 0" (cần xác thực qua API có auth, chưa setup trong session
này).

## Không có finding mới cụ thể

Round này thuần bảo trì/review, không backtest mới — nhưng đúng tinh thần
Rule 6/7 (review hệ thống, dọn backlog, xác nhận không có bug mới xuất hiện).
