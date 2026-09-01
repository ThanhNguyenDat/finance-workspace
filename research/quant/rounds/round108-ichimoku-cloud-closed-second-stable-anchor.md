# Round 108 (2026-08-23) — Ichimoku Cloud TK-cross + displaced cloud filter (mới hoàn toàn) — ĐÓNG, candidate ổn định thứ 2 sau `ema_crossover_12_26`@30m

Status: research, thêm `IchimokuCloudStrategy` (candidate mới hoàn toàn) vào
`finance-research/src/strategies.rs`. Chạy 4 route 5 năm thành 2 cặp song
song, `--cpus=2 --memory=4g --memory-swap=6g` (đúng Rule 9).

## Bối cảnh

2 commit mới từ Codex ở finance-mw (`5aa24df`, `dfa4b82` — observability/OOM
memory capture), không thuộc business `trading`, không cần review theo Rule
1. XAU/Exness vẫn đóng cửa. Sau khi cạn nhiều cơ chế wrapper-trên-candidate-
cũ (Round 103-107), Round 108 chuyển sang 1 hệ thống chỉ báo hoàn toàn khác:
**Ichimoku Kinko Hyo** — khác mọi candidate trước ở chỗ trend-filter (cloud)
là nội tại của hệ thống, không phải wrapper gắn thêm sau.

## Implementation

`IchimokuCloudStrategy`: Tenkan(9)/Kijun(26) là trung điểm cao-thấp rolling
(giống Donchian midpoint), Senkou Span A = (Tenkan+Kijun)/2, Senkou Span B =
trung điểm 52 nến. Cloud được "dịch chuyển" đúng chuẩn (hiển thị 26 nến
trước) bằng cách lưu deque các cặp (spanA, spanB) đã tính ở mỗi nến, và so
sánh giá hiện tại với cặp được tính từ **26 nến trước** (đọc index trước khi
push, không lookahead — cùng kỷ luật `DonchianBreakoutStrategy`). Tín hiệu
chỉ nổ đúng nến Tenkan cắt Kijun (không phải mọi nến còn giữ trạng thái cắt)
VÀ giá đóng cửa phải vượt/dưới cloud cùng hướng. Tham số chuẩn sách giáo
khoa 9/26/52/26. `cargo fmt` + `cargo build -p finance-research` sạch.

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật)

| Route | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|
| BTC/binance | 0.740 | 0.838 | 0.862 | 920 |
| BTC/exness | 0.779 | 0.814 | 0.881 | 904 |
| XAU/binance | 0.664 | 0.577 | 0.507 | 135 |
| XAU/exness | 0.519 | 0.510 | 0.764 | 651 |

## Nhận xét — ổn định, cross-broker nhất quán cho BTC, không có shape đáng ngờ

BTC ở cả 2 broker cho hình dạng **tăng dần đơn điệu** gần như y hệt nhau về
độ lớn (0.740→0.838→0.862 và 0.779→0.814→0.881) — không giật cục, không có
dấu hiệu overfit/false-positive nào (khác Round 106/107). **Không có ô nào
vượt 1.0** nên không cần cross-check 18 tháng (khác Round 106 — ở đây không
có "near-miss" nào để phải kiểm tra thêm). XAU yếu hơn rõ rệt và không nhất
quán hướng giữa 2 broker (binance giảm dần, exness tăng dần) — chưa đạt mức
đáng chú ý.

Đây là candidate **thứ 2 trong toàn chương trình** (sau `ema_crossover_12_26`
@30m, Round 78) cho thấy sự ổn định thật giữa các split mà không cần thêm
lever nào — đáng ghi làm điểm neo tham khảo, dù PF vẫn <1 mọi nơi.

## Kết luận — ĐÓNG

Không promote. Cả 12 ô PF<1. Ghi nhận làm điểm neo ổn định thứ 2 (cùng
nhóm `ema_crossover_12_26`@30m) — nếu tương lai muốn thử thêm lever (vd:
volume/ADX filter, tinh chỉnh tham số Kijun/Senkou), nên bắt đầu từ đây thay
vì các candidate giật cục đã đóng khác.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `IchimokuCloudStrategy` làm
  bản ghi closed-candidate (research-only), hoặc revert nếu không cần giữ.
