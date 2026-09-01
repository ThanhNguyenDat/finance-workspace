# Round 23 (2026-08-20) — Target 2 (Make Decision rate) đứng yên xuyên suốt session, đo bằng số thật

Status: verification-only, đọc production Redis checkpoint read-only qua SSH.
Không phải backtest — đây là số liệu thật của hệ thống đang chạy.

## Số liệu longitudinal (so sánh Round 11/17 → Round 23, ~vài giờ thật)

| Leg | Trades Round 11/17 | Trades Round 23 | Thay đổi | evaluation_count Round 17→23 |
|---|---|---|---|---|
| BTC/binance fixed-pct | 1295 (392W/903L) | **1295 (392W/903L)** | **0 trade mới** | 2555→2580 (+25) |
| BTC/exness risk-2pct | 1 (1W/0L) | **1 (1W/0L)** | **0 trade mới** | 4456→4480 (+24) |
| BTC/exness fixed-pct | 1310 (405W/905L) | **1310 (405W/905L)** | **0 trade mới** | (không log riêng round 17) |
| XAU/binance all-3-rules | 8 (3W/5L) | **8 (3W/5L)** | **0 trade mới** | 2558→2582 (+24) |
| XAU/exness fixed-pct | 734 (251W/483L) | **734 (251W/483L)** | **0 trade mới** | (không log riêng round 17) |

**Cả 5 scope đều 0 trade mới trong khoảng thời gian đo được** (~1h20m giữa
round 17→23, và với BTC/binance + XAU/exness là 0 trade mới kể từ tận Round
11/Round 10 — tức nhiều giờ thật). Trong khi đó `evaluation_count` mỗi
checkpoint vẫn tăng đều (~24-25 lần đánh giá mỗi ~1h20m, tương ứng đúng nhịp
nến 5m/~16 nến mỗi giờ với 1 vài scope khác intervals cộng dồn) — hệ thống
vẫn đang chạy, đánh giá bình thường, không bị treo. Chỉ đơn giản là **không
đưa ra quyết định mới nào** trong khoảng thời gian này.

## Ý nghĩa

Đây KHÔNG phải bug mới — khớp hoàn toàn với mọi phát hiện Alpha-layer từ
Round 17-22: mọi candidate có edge thật tìm được (swing 4h/1d, ORB 30m) đều
có tần suất raw rất thấp (0.21-2.37 lần/tuần), tức việc Portfolio's real
decision engine không ra quyết định mới trong 1-vài giờ là hoàn toàn phù hợp
với tần suất signal thật, không phải dấu hiệu treo/lỗi. Nhưng nó cũng nói
rõ: **Target 2 (tăng tỉ lệ Make Decision) hiện chưa có tiến triển thật nào
đo được trong suốt session `/loop` này** — không phải do thiếu candidate,
mà đúng như Round 20 đã chỉ ra, cần công cụ đo đúng qua `decide()` thật để
biết thêm 1 signal mới (vd funding rate Round 22) có thực sự tăng tần suất
quyết định của ensemble hay không, trước khi có thể claim tiến bộ thật cho
Target 2.

## Refinement nhỏ cho anomaly Round 17/20

`decisions_since_target_change` của Binance XAU (đã flag bất thường lớn hơn
`evaluation_count` ~27 lần) tăng từ 69102→69117 (+15) cùng lúc
`evaluation_count` tăng 2558→2582 (+24) — **counter này không bị đóng băng**,
chỉ khởi điểm rất lớn từ trước session. Củng cố giả thuyết "counter không
reset theo redeploy giống `evaluation_count`" hơn là 1 lỗi tính sai đơn vị —
vẫn cần Codex xác nhận qua code, không tự đóng item.

## Không cần hành động ngay

Đây là bằng chứng track theo thời gian, không phải phát hiện cần fix gấp.
Giá trị chính: xác nhận bằng số liệu thật rằng target 2 hiện KHÔNG cải thiện
tự nhiên chỉ nhờ thời gian trôi qua hay các fix continuity/bug đã ship — cần
1 thay đổi thật (signal mới có tần suất cao hơn, hoặc điều chỉnh
interval_weights/threshold ở decision engine) mới có thể dịch chuyển số này,
đúng hướng đề xuất đã log ở round 17-22.
