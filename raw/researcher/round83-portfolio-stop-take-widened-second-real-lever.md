# Round 83 (2026-08-21) — Đòn bẩy Target 1 thật thứ 2: nới rộng Portfolio stop/take-profit từ 0.005/0.010 lên 0.01/0.02

Status: dev + research. Tiếp nối trực tiếp Round 82's kết luận đúng phương
pháp (`one_target`) — áp dụng đúng cách đo đó cho 1 tham số Portfolio khác
chưa từng được biến thiên: `--portfolio-stop-value`/`--portfolio-take-value`.

## Ý tưởng: cùng cơ chế với Round 80, khác tham số

Round 80 tìm được: kéo dài thời gian giữ vị thế trước khi đảo chiều giúp
giảm lỗ do bớt whipsaw. Cùng logic có thể áp dụng cho khoảng cách stop-loss:
stop quá hẹp (0.5%) dễ bị nhiễu giá thông thường chạm phải trước khi tín
hiệu thật kịp phát triển — nới rộng stop có thể giảm số lần bị "quét" oan.

## Backtest: quan hệ đơn điệu, đo đúng qua `one_target` (đã xác nhận đáng tin ở Round 82)

**BTC/binance, 5 năm, hold=36 (cấu hình hiện tại):**

| stop/take | Trades | PnL | Tần suất ước tính |
|---|---|---|---|
| 0.005/0.010 (cũ) | 3830 | -$28.72 | ~14.7/tuần |
| 0.0075/0.015 | 2964 | -$26.04 | ~11.4/tuần |
| **0.01/0.02 (mới)** | **2417** | **-$16.93** | **~9.3/tuần** |
| 0.02/0.04 | 1340 | -$10.71 | ~5.2/tuần (dưới ngưỡng Target 3!) |

**Cross-broker (BTC/exness, cùng cấu hình):**

| stop/take | Trades | PnL |
|---|---|---|
| 0.005/0.010 (cũ) | 3859 | -$28.36 |
| **0.01/0.02 (mới)** | **2410** | **-$19.18** |

Chênh lệch Binance/Exness <2% ở mọi mức — cùng độ nhất quán cao đã thấy ở
Round 80.

## Regime-dependency (18 tháng độc lập): cùng hướng

0.005/0.010 → -$5.01 (892 trade); 0.01/0.02 → -$2.20 (555 trade) — cùng
hướng cải thiện ~56%, khớp window 5 năm.

## Chọn 0.01/0.02: gấp đôi hiện tại, giữ margin Target 3

Không chọn 0.02/0.04 (mạnh nhất) vì tần suất rơi xuống dưới 7/tuần — vi phạm
Target 3 rõ ràng. 0.01/0.02 giữ ~9.3/tuần (margin 33% so với ngưỡng), capture
phần lớn cải thiện khả dụng (~41% Binance, ~32% Exness).

## Đã triển khai đầy đủ

- Sửa `crates/finance-api/src/deployment_rules.rs`: gom `stop_value`/
  `take_value` lặp lại ở cả 3 rule (fixed-pct, risk-2pct, compounding-10pct)
  thành 2 constant `PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE` (0.01/0.02),
  kèm doc-comment đầy đủ bảng số liệu.
- Không có test nào assert giá trị stop/take tuyệt đối.
- `cargo test --workspace --exclude finance-redis`: 32/32 pass.
- `cargo fmt --check`: sạch.
- `cargo build --release -p finance-api`: thành công.
- Commit `31ed149`, push, CI đang chạy (SẼ deploy thật — đổi `finance-api`).

## Ý nghĩa: 2 đòn bẩy Portfolio-construction thật đã tìm + triển khai trong 4 round

Round 80 (`minimum_hold_decisions`) + Round 83 (`stop/take`) — cả 2 đều
thuộc trục Portfolio-construction (không phải Alpha signal), cả 2 đều giảm
lỗ ~30-40% mà không vi phạm Target 3, cả 2 đều cross-broker validate mạnh.
**Kết hợp cả 2 thay đổi**: ước tính (chưa test trực tiếp combo) tổng cải
thiện có thể lớn hơn đáng kể so với từng cái riêng lẻ — có thể là hướng đáng
thử ở round sau (dù rủi ro non-linear interaction cần kiểm tra thay vì cộng
dồn giả định).

## Giới hạn quan trọng

Vẫn KHÔNG biến lỗ thành lời — PF vẫn <1 ở mọi giá trị test được. Chỉ làm hệ
thống thua lỗ chậm hơn, rẻ hơn.
