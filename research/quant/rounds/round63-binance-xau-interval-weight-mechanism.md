# Round 63 (2026-08-21) — Tìm ra CƠ CHẾ cụ thể của Target 2 stagnant: `interval_weights` Binance/XAU dồn hết vào 1d/12h/4h

> **⚠️ ĐÃ SỬA LẠI Ở ROUND 65:** giả thuyết "lịch sử ngắn → thiếu dữ liệu →
> weight zero" trong file này (và addendum Round 64) **SAI**. Nguyên nhân
> thật là bất đối xứng cấu hình subscribe strategy (Binance/XAU chỉ 2
> strategy, route khác có 3-5). Đọc `round65-CORRECTION-real-mechanism-is-strategy-subscription-asymmetry.md`
> trước — file đó có công thức đúng đã verify khớp 100% với production.
> Giữ file này nguyên vẹn làm lịch sử điều tra, không xoá/sửa nội dung gốc.

Status: verification/mechanism discovery, đọc trực tiếp `portfolio_evidence`
trong checkpoint production qua SSH (tiếp nối trực tiếp phát hiện Round 62
về `pending_history_backfill` kẹt 8 tháng).

## Bối cảnh

Round 62 phát hiện `trade_count` của Binance/XAU chỉ = 8, thấp hơn 100-140
lần so với 3 route còn lại đo trên cùng bộ đếm sau fix epoch-migration, và
tìm được 1 dấu hiệu tương quan (`pending_history_backfill` kẹt từ Dec 2025)
nhưng **chưa chứng minh được cơ chế nhân-quả**. Round này đào sâu thêm bằng
cách đọc `runtime_state.portfolio_evidence.policy` — nơi lưu trọng số thật
sự mà `MultiTimeframePortfolioPolicy::decide()` dùng để tính `entry_score`.

## Phát hiện: `interval_weights` của Binance/XAU zero-out gần hết các interval tần suất cao

**Binance/XAU** (`portfolio_evidence.policy.interval_weights`):
| Interval | Role | Weight |
|---|---|---|
| `1d` | trend | **0.521** |
| `12h` | trend | **0.338** |
| `4h` | trend | **0.141** |
| `2h` | trend | 0.0 |
| `1h` | trend | 0.0 |
| `30m` | entry | 0.0 |
| `15m` | entry | 0.0 |
| `5m` | entry | 0.0 |

**Exness/XAU cùng thời điểm, để so sánh:**
| Interval | Role | Weight |
|---|---|---|
| `1d` | trend | 0.223 |
| `12h` | trend | 0.199 |
| `4h` | trend | 0.116 |
| `2h` | trend | 0.116 |
| `1h` | trend | 0.116 |
| `30m` | entry | 0.116 |
| `15m` | entry | 0.116 |
| `5m` | entry | 0.0 |

**Khác biệt rõ rệt:** Exness/XAU chỉ có `5m` weight=0 (bình thường, theo
comment trong policy các round trước — 5m luôn bị loại vì noise), mọi
interval khác đều có trọng số đáng kể (0.116-0.223). Binance/XAU thì **cả 5
interval `15m/30m/1h/2h/5m` đều bị zero-out**, chỉ còn 3 interval trend dài
hạn nhất (`1d/12h/4h`) mang trọng số — và đặc biệt, **tất cả 2 interval vai
trò "entry" (`15m`, `30m`) đều = 0**.

## Vì sao điều này giải thích trực tiếp Target 2

Theo `required_intervals`, `entry_score` (điều kiện `gate_passed` trong
`signal_states`) được tính từ các interval vai trò "entry". Khi TẤT CẢ
interval entry của Binance/XAU đều weight=0, điểm entry chỉ có thể thay đổi
khi 1 trong 3 interval trend còn lại (1d/12h/4h) đóng nến — tức tối đa vài
lần/ngày, thay vì mỗi 5-30 phút như thiết kế ban đầu (và như Exness/XAU vẫn
đang hoạt động). **Đây là cơ chế trực tiếp (không chỉ tương quan) giải thích
vì sao `trade_count` Binance/XAU chỉ = 8** trong khi 3 route còn lại có
758-1126 (Round 62).

## Giả thuyết nguyên nhân gốc: `reweight_from_alpha_performance` + lịch sử ngắn

Trọng số này do `reweight_from_alpha_performance` tính (lifetime-cumulative
theo hiệu suất quá khứ, không phải rolling window — đã biết từ các round
trước khi đọc `trading_modes.rs`). Giả thuyết hợp lý nhất, khớp với bug Round
62 (Binance/XAU chỉ có lịch sử từ Dec 2025, ~8 tháng): **các strategy chạy
trên interval ngắn (5m/15m/30m) chưa tích luỹ đủ track record để được gán
trọng số dương**, trong khi Exness/XAU có lịch sử từ 2021 nên mọi interval
đều có đủ dữ liệu lịch sử để nhận trọng số khác 0. Đây KHÔNG nhất thiết là
"hiệu suất thật sự tệ" — có thể đơn giản là thuật toán reweight chưa đủ dữ
liệu để tính hiệu suất ổn định cho các interval đó trên 1 instrument mới
list.

**Giới hạn:** đây vẫn là bằng chứng đọc trực tiếp production state (không
phải code review) — chưa xác nhận 100% qua source code của
`reweight_from_alpha_performance` liệu có cơ chế floor/warm-up hay không.
Cần Codex xác nhận qua code review trước khi implement fix.

## Cập nhật Round 64 — xác nhận thêm bằng "thí nghiệm tự nhiên" 4 route

Đọc thêm `interval_weights` của 2 leg BTC (lịch sử dài từ 2021, cả 2 broker)
để đối chứng:

| Route | 5m | 15m | 30m | 1h | 2h | 4h | 12h | 1d |
|---|---|---|---|---|---|---|---|---|
| Binance/BTC | 0 | 0.136 | 0.136 | 0.136 | 0.136 | 0.136 | 0.154 | 0.167 |
| Exness/BTC | 0 | 0.134 | 0.134 | 0.134 | 0.134 | 0.145 | 0.153 | 0.167 |
| Exness/XAU | 0 | 0.116 | 0.116 | 0.116 | 0.116 | 0.116 | 0.199 | 0.223 |
| **Binance/XAU** | 0 | **0** | **0** | **0** | **0** | 0.141 | 0.338 | 0.521 |

**3/4 route có lịch sử dài (cả 2 leg BTC + Exness/XAU) đều trải đều trọng số
mọi interval (chỉ 5m=0, bình thường) — chỉ đúng 1/4 route có lịch sử ngắn
(Binance/XAU, list Dec 2025) bị zero-out hàng loạt.** Đây là bằng chứng dạng
thí nghiệm tự nhiên khá sạch (3 control routes đồng nhất, 1 treatment route
khác biệt rõ rệt) — nâng độ tin cậy giả thuyết "lịch sử ngắn → weight bị
zero-out" lên mức cao, không còn là suy luận từ 1 phép so sánh đơn lẻ nữa.
Không thay đổi kết luận/đề xuất, chỉ củng cố bằng chứng.

## Đề xuất cho Codex

Kiểm tra `reweight_from_alpha_performance` (trong `crates/finance-core/src/trading_modes.rs`)
xem có xử lý minimum-floor hoặc warm-up period cho instrument mới list hay
không. Nếu xác nhận đúng giả thuyết trên, đây chính là nguyên nhân gốc của
Target 2 cho XAU/binance — hướng fix khả dĩ: floor trọng số tối thiểu theo
%, hoặc warm-up period bỏ qua reweight cho tới khi đủ N ngày lịch sử. Nâng
độ ưu tiên item Round 62 từ P2 lên P1 trong `handoff_codex.md` (đã cập nhật)
vì giờ có cơ chế cụ thể, không chỉ tương quan.

## Không log candidate/backtest mới round này

Round này thuần đào sâu 1 bug/lead đã có, đọc production state trực tiếp —
không chạy `finance-research`. Đúng Rule 7 (cải tiến: nâng 1 lead mơ hồ từ
Round 62 thành 1 cơ chế cụ thể, có thể hành động được).
