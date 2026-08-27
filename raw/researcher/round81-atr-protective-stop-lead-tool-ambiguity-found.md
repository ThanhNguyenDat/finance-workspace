# Round 81 (2026-08-21) — Đào sâu thêm đòn bẩy Portfolio-construction: phát hiện lead ATR-stop nhưng gặp mơ hồ trong công cụ đo, dừng lại trước khi implement sai

Status: research + verification. Tiếp nối hướng thành công Round 80
(Portfolio-construction level, không phải Alpha signal) — nhưng lần này phát
hiện 1 sự mơ hồ trong công cụ đo cần làm rõ trước khi tin bất kỳ số liệu nào.

## Ý tưởng: so sánh protective stop cơ chế % cố định vs ATR-adaptive

`finance-research`'s `portfolio_execution.capital_reports` so sánh song song
4 rule: `fixed-pct`/`compounding-pct` (stop % cố định 0.5%/1%) vs
`fixed-atr`/`compounding-atr` (stop theo ATR 2x/4x, period 14). Số liệu ban
đầu (BTC/binance, `--portfolio-minimum-hold-decisions 36`):

| Rule | PnL | ROI trên vốn triển khai |
|---|---|---|
| `fixed-pct` (đang live) | -$78.69 | -0.001535 |
| `fixed-atr` | -$65.67 | **-0.001480** |
| `compounding-pct` | -$7932.97 | -0.001593 |
| `compounding-atr` | -$7320.01 | **-0.001543** |

`fixed-atr` và `compounding-atr` đều tốt hơn phiên bản % cố định tương ứng
(~15-17% ít lỗ hơn) — trông giống 1 đòn bẩy thứ 2 tiềm năng.

## Phát hiện mơ hồ: `capital_reports` KHÔNG phản ánh `--portfolio-minimum-hold-decisions`

Chạy lại với `--portfolio-minimum-hold-decisions 12` (giá trị cũ) — số liệu
`capital_reports` **giống hệt** kết quả ở `--portfolio-minimum-hold-decisions
36`. Đọc code xác nhận: `replay_portfolio_decisions` (nguồn decision stream
dùng chung cho mọi rule so sánh) **không hề nhận tham số
`minimum_holding_decisions`** — chỉ nhánh `legacy_selected_rule`/`one_target`
(dùng trong Round 80's kết luận) mới thực sự áp dụng guard này. `capital_reports`
rất có thể đang dùng 1 giả định hold-period mặc định/khác, không phải giá trị
36 mới deploy.

## Quyết định: KHÔNG implement ATR-stop round này

Không đủ tin cậy để kết luận "ATR-stop sẽ giúp dưới chế độ hold=36 hiện tại"
từ dữ liệu này — cần hiểu rõ `capital_reports` đang thực sự đo gì (hold-period
nào) trước khi tin số liệu 15-17% cải thiện có ý nghĩa dưới cấu hình production
THẬT hiện tại hay không. Dừng lại đúng lúc, không lặp lại sai lầm suýt xảy ra ở
Round 76/77 (Round 76 là lộ credential; đây là mơ hồ phương pháp luận) —
tránh implement dựa trên hiểu nhầm công cụ.

## Việc đã làm

- Đọc code `execution_rules.rs`/`portfolio_decision_replay.rs` để xác nhận
  gap giữa các nhánh đo lường.
- Kiểm tra nhanh production sau deploy Round 80 (chưa đủ thời gian để thấy xu
  hướng PnL thật rõ ràng — cần theo dõi thêm vài ngày).

## Để lại cho round sau

Cần: (1) đọc kỹ hơn `portfolio_measurement.rs`'s `compare_real_portfolio_with_funding`
để xác định chính xác `capital_reports` dùng hold-period nào (có thể cần đọc
`replay_portfolio_decisions`'s internal logic sâu hơn, hoặc grep xem có tham
số hold-period nào truyền vào legacy grid không); (2) nếu xác nhận được
`capital_reports` cũng đáng tin dưới cấu hình mới, backtest lại ATR-stop kỹ
hơn (cross-broker, regime-dependency) trước khi cân nhắc implement.
