# Round 56 (2026-08-21) — Bức tranh đầy đủ 4 leg qua engine thật + continuity issue rộng hơn tưởng

Status: verification, hoàn thiện Round 55 (mới chỉ check Binance) bằng cách
chạy `--daily-profit-gate` (đánh giá đúng Portfolio production thật) cho cả
2 leg Exness còn lại.

## Bức tranh đầy đủ 4 leg (production thật, qua `PortfolioDecisionPolicy`)

| Leg | Sharpe | Sortino | Net PnL holdout | positive_day_ratio | observed_days |
|---|---|---|---|---|---|
| BTC/binance | -6.73 | -6.69 | -$13.39 | 37.7% | 366 |
| **BTC/exness** | **-6.93** | **-6.88** | **-$13.73** | 35.5% | 366 |
| XAU/binance | None | None | $0.00 | 0% | 51 |
| **XAU/exness** | **-1.58** | **-2.06** | **-$0.79** | 25.1% | 311 |

**BTC 2 broker gần như giống hệt nhau** (Sharpe -6.73 vs -6.93, net PnL
-13.39 vs -13.73) — xác nhận cross-broker đây là vấn đề signal thật (Alpha
strategy đang live thua lỗ nhất quán), không phải artifact riêng 1 nguồn
giá, khớp đúng phương pháp cross-validation đã dùng nhiều lần trong chương
trình này.

## Phát hiện mới: continuity issue rộng hơn nhiều so với hiểu biết trước đây

Tool mới lộ ra breakdown chi tiết `input_continuity_failed:<interval>` cho
từng khung riêng biệt — **Exness BTC fail continuity ở 5m/15m/1h/2h/30m**
(5 interval!), **Exness XAU fail ở 5m/12h/15m/1d/1h/2h/30m/4h** (8 interval,
gần như TẤT CẢ). Trước đây (Round 15/18/20/21/49) tôi chỉ phát hiện lẻ tẻ
từng combo cụ thể bị fail — giờ thấy rõ đây là vấn đề **hệ thống của
Exness** ảnh hưởng gần như mọi interval, không phải vài trường hợp cá biệt.
Binance (cả BTC lẫn XAU) KHÔNG có `input_continuity_failed` nào trong
`failed_checks` — xác nhận đây là vấn đề riêng của nguồn dữ liệu Exness.

## Ý nghĩa

1. **Target 1 (BTC) fail nặng, xác nhận cross-broker** — không phải may
   rủi 1 nguồn giá, signal đang live thật sự thua lỗ nhất quán.
2. **Target 2 (XAU) yếu ở cả 2 broker** nhưng theo cách khác nhau: Binance
   gần như không ra quyết định (observed_days=51, có thể do listing mới,
   ít lịch sử — đã biết từ Round 13), Exness có nhiều quyết định hơn
   (observed_days=311) nhưng vẫn thua lỗ + vẫn fail tần suất.
3. **Continuity issue Exness cần điều tra ở mức hệ thống**, không phải
   từng interval riêng lẻ — đề xuất Codex audit tổng thể pipeline dữ liệu
   Exness (không chỉ tiếp tục vá từng interval một như 2 lần fix trước).

## Đề xuất cho Codex

Nâng độ ưu tiên điều tra continuity Exness — giờ có bằng chứng rõ ràng đây
không phải vài case lẻ tẻ mà là pattern hệ thống ảnh hưởng hầu hết interval.
Không log lại y hệt các item cũ (đã có ở Round 15/18/20/21/49) — chỉ bổ
sung bằng chứng mới (breakdown per-interval) để tăng độ ưu tiên điều tra.
