# Round 89 (2026-08-22) — `risk_fraction` sizing: lever stop/take Round 83 gần như không tác dụng, và tự nó gây lỗ 98-99.9% vốn mô phỏng do đòn bẩy hiệu dụng ẩn trong công thức

Status: research only, không sửa code round này (chỉ chạy backtest qua binary
đã build). File `strategies.rs` từ Round 88 vẫn đang chờ Codex review, chưa
đổi thêm gì.

## Bối cảnh

Round 85 phát hiện + Codex đã fix (commit `6eebf76`) bug risk-gate từ chối
gần hết quyết định cho `risk_fraction` sizing. Round 89 tiếp tục hướng đó:
kiểm tra xem lever stop/take-width (Round 83, đã chứng minh hiệu quả cho
`fixed_notional`) có tác dụng tương tự cho `risk_fraction` không — trực tiếp
liên quan rule `risk-2pct` đang chạy thật (mô phỏng) trên production.

## Kết quả 1 — Lever stop/take gần như KHÔNG có tác dụng cho `risk_fraction`

`one_target`, `risk_fraction=0.02`, hold=36, BTC cả 2 broker, 5 năm:

| Broker | stop/take 0.005/0.010 (cũ) | stop/take 0.01/0.02 (hiện tại) | Cải thiện |
|---|---|---|---|
| BTC/binance | -$9,999.75 (1510 trade) | -$9,994.33 (2439 trade) | **0.05%** |
| BTC/exness | -$9,968.56 (3870 trade) | -$9,822.08 (2417 trade) | **1.5%** |

So sánh: cùng lever này cho `fixed_notional` (Round 87) cải thiện **33-43%**.
Sự khác biệt cực lớn — lever Round 83 gần như vô nghĩa cho rule `risk-2pct`.

## Kết quả 2 (nghiêm trọng hơn nhiều) — `risk_fraction=0.02` tự nó gây lỗ
gần hết vốn mô phỏng $10,000, bất kể stop/take

| Route | PnL (stop/take hiện tại 0.01/0.02) | % vốn mất |
|---|---|---|
| BTC/binance | -$9,994.33 | **99.94%** |
| BTC/exness | -$9,822.08 | **98.22%** |
| XAU/binance | +$89.07 (8 trade, mẫu quá mỏng) | outlier như mọi round trước |
| XAU/exness | -$5,991.96 | **59.9%** |

So sánh cùng thời điểm, cùng decision stream, sizing khác (từ checkpoint
production thật, Round 88 đã đọc): `fixed-pct` (sizing `fixed_notional=5`)
chỉ lỗ **-$3.41** (0.03%), `compounding-10pct` (sizing `equity_fraction=0.10`)
lỗ **-$663.22** (6.6%) trên cùng route BTC/binance. `risk-2pct` lỗ **gấp
~1.500 lần** `compounding-10pct` dù cùng chạy trên cùng 1 decision stream.

## Nguyên nhân gốc — công thức `risk_fraction` ẩn chứa đòn bẩy hiệu dụng lớn

`PositionSizing::RiskFraction::notional = (equity × risk_fraction) / stop`
(`trading_modes.rs:1287-1295`). Với `risk_fraction=0.02`, `stop=0.01`:
`notional = equity × 0.02 / 0.01 = equity × 2` — **mỗi lệnh dùng notional
gấp 2 lần equity hiện tại** (leverage-hiệu-dụng 2x), so với `equity_fraction
=0.10` chỉ dùng 0.1× equity (không đòn bẩy). Công thức này đúng về mặt thiết
kế ("rủi ro đúng 2% equity nếu chạm stop") nhưng vì `stop` hiện tại rất hẹp
(1%) so với `risk_fraction` (2%), tỷ lệ `risk_fraction/stop = 2` tạo ra đòn
bẩy hiệu dụng gấp đôi vốn mỗi lệnh — trên 1 Alpha có PF<1 xuyên suốt chương
trình 89 round, đòn bẩy này khuếch đại lỗ theo cấp số nhân qua ~2000-4000
lệnh trong 5 năm, dẫn tới gần như mất trắng.

**Vì sao lever Round 83 (nới stop/take) không giúp được:** nới stop giúp
giảm số lần bị "quét oan" (đúng cơ chế đã xác nhận cho `fixed_notional`),
nhưng với `risk_fraction`, nới `stop` từ 0.005→0.01 đồng thời làm GIẢM
notional mỗi lệnh (vì `notional ∝ 1/stop`: risk_fraction/stop giảm từ 4→2),
tức là 2 hiệu ứng đối lập triệt tiêu lẫn nhau — ít bị quét oan hơn (tốt) NHƯNG
mỗi lệnh còn lại vẫn đủ đòn bẩy lớn để tiếp tục ăn mòn vốn nhanh (xấu),
net effect gần như hoà, khác hẳn `fixed_notional` nơi 2 hiệu ứng không tương
tác (notional cố định, không phụ thuộc stop).

## Ý nghĩa — CẢNH BÁO nghiêm túc, không phải bug code

Đây **không phải bug reject** như Round 85 (bug đó đã fix đúng, risk-gate
0 rejection). Đây là hệ quả TOÁN HỌC của chính công thức `risk_fraction` khi
áp lên 1 Alpha có edge âm với `risk_fraction=0.02`/`stop=0.01` hiện tại — số
liệu hoàn toàn hợp lý, không phải lỗi đo. Rule `risk-2pct` đang chạy mô
phỏng song song thật trên production (ledger `paper-risk-2pct-scope-*`,
KHÔNG phải risking vốn thật qua broker thật — xác nhận qua code
`trading_api.rs:756-780`: mọi rule Portfolio đều dùng `context.simulated_child`,
đây là hệ thống demo/paper simulation chạy trên dữ liệu thị trường thật, không
kết nối lệnh thật ra broker). Vẫn cần lưu ý nếu ledger này có vai trò trong
bất kỳ cơ chế trọng số/so sánh/promotion nào trong tương lai, hoặc nếu
dashboard tổng hợp Target 1 có gộp cả 3 rule lại — con số -99% của riêng
`risk-2pct` sẽ làm méo bức tranh tổng.

## Việc cho Codex / round sau

- **[trading][medium]** Cân nhắc giảm `sizing_value` của rule `risk-2pct` từ
  0.02 xuống mức nhỏ hơn nhiều (vd 0.005 hoặc thấp hơn) để đòn bẩy hiệu dụng
  (`risk_fraction/stop`) về mức tương đương `compounding-10pct` (~0.1-0.2)
  thay vì 2.0 hiện tại — hoặc chấp nhận rule này chỉ mang tính minh hoạ công
  thức, không kỳ vọng cạnh tranh performance với 2 rule kia cho tới khi
  Alpha có edge dương thật.
- Không cấp bách/không phải bug cần fix gấp — chỉ cần owner/Codex biết để
  không hiểu lầm số liệu `risk-2pct` khi xem dashboard hoặc dùng nó trong so
  sánh sizing mode sau này.
- Round sau nếu tiếp tục hướng sizing: có thể sweep `risk_fraction` sizing_value
  (0.005/0.01/0.02/0.03) để tìm điểm đòn bẩy hiệu dụng ≈ `compounding-10pct`,
  xác nhận PnL trở về mức tương đương (dự đoán tuyến tính theo tỷ lệ đòn bẩy).
