# Round 82 (2026-08-21) — Giải quyết dứt điểm lead ATR-stop từ Round 81: đo đúng phương pháp, fail cross-broker, đóng

Status: research + verification. Tiếp nối trực tiếp Round 81's câu hỏi mở
("cần đọc kỹ `portfolio_measurement.rs` để xác định `capital_reports` dùng
hold-period nào trước khi tin số liệu").

## Xác nhận nguyên nhân mơ hồ Round 81: đọc code trực tiếp

Đọc `compare_real_portfolio_with_funding` (`portfolio_measurement.rs:105-190`):
vòng lặp chính cho thấy rõ **`legacy_ledgers`/`legacy_selected_ledger` (nguồn
của `legacy_grid`/`legacy_selected_rule`/`capital_reports`) nhận thẳng
`timed.decision` KHÔNG qua `construction.construct()`** — tức hoàn toàn
KHÔNG áp dụng `minimum_holding_decisions`. Chỉ `construction.construct(timed.decision)`
(nguồn `one_target`) mới thực sự dùng guard này. Xác nhận bằng thực nghiệm
(window 200 ngày, so hold=12 vs hold=100): `legacy_grid`/`legacy_selected_rule`/
`capital_reports` **giống hệt nhau tuyệt đối**, chỉ `one_target` thay đổi
(603 trade → 247 trade). **Kết luận: `capital_reports` (nguồn ATR-stop
"improvement" ở Round 81) là 1 nhánh legacy hoàn toàn tách biệt khỏi cấu hình
hold-period hiện tại — không đáng tin cho quyết định production.**

## Đo lại đúng phương pháp: dùng `--portfolio-protective-kind` trên nhánh `one_target`

`finance-research` có `--portfolio-protective-kind atr_multiple
--portfolio-stop-value 2.0 --portfolio-take-value 4.0 --portfolio-atr-periods 14`
— áp dụng ATR-stop ngay trên nhánh `one_target` (nhánh ĐÚNG, tôn trọng
`--portfolio-minimum-hold-decisions`). So sánh tại đúng cấu hình production
hiện tại (hold=36):

**BTC/binance, 5 năm:**
| Protective kind | Trades | PnL |
|---|---|---|
| `fractional` (đang live) | 3830 | -$28.72 |
| `atr_multiple` (2.0/4.0/14) | 4363 | **-$26.51** (tốt hơn ~7.7%) |

**BTC/exness, 5 năm:**
| Protective kind | Trades | PnL |
|---|---|---|
| `fractional` (đang live) | 3859 | -$28.36 |
| `atr_multiple` (2.0/4.0/14) | 4297 | **-$30.52** (TỆ HƠN ~7.6%) |

## Kết luận: FAIL cross-broker rõ ràng — đóng lead ATR-stop

**Binance cho kết quả tốt hơn, Exness cho kết quả tệ hơn — gần như đối
xứng ngược nhau.** Đây chính xác là dạng thất bại cross-broker đã đóng nhiều
candidate khác trong chương trình (theo chuẩn Round 56). Kết luận: ATR-stop
2.0/4.0/14 KHÔNG phải cải thiện thật, chỉ là artifact riêng của 1 nguồn dữ
liệu. Đóng hẳn — không cần thử thêm tham số ATR khác trừ khi có lý do mới.

## Ý nghĩa: Round 80's kết luận (`minimum_hold_decisions`) không bị ảnh hưởng

Phát hiện quan trọng: Round 80 dùng đúng `one_target` (đã verify tôn trọng
hold-period) nên kết luận đó **vẫn đứng vững, không cần xem lại**. Chỉ có
Round 81's lead (dùng nhầm `capital_reports`) là sai và giờ đã đóng đúng
cách.

## Đã làm

- Đọc code xác nhận cơ chế 4 nhánh đo lường khác nhau trong
  `portfolio_measurement.rs`.
- Backtest thật qua `--portfolio-protective-kind` trên nhánh `one_target`
  đúng, cross-broker (Binance + Exness BTC), cùng cấu hình hold=36 hiện tại.
- Không có thay đổi code (kết luận là đóng, không implement).

## Bài học phương pháp luận quan trọng

`finance-research` có NHIỀU nhánh đo lường Portfolio song song
(`legacy_grid`, `legacy_selected_rule`, `one_target`, `capital_reports`) với
mức độ trung thực khác nhau — chỉ `one_target` (và `--daily-profit-gate`
riêng biệt) thực sự phản ánh cấu hình Portfolio hiện tại đầy đủ. Bất kỳ kết
luận nào dùng `legacy_*`/`capital_reports` cần được xác minh lại qua
`one_target` trước khi tin, đặc biệt sau khi có thay đổi cấu hình Portfolio
như Round 80.
