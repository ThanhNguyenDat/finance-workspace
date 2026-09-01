# Round 40 (2026-08-20) — trade_count không phải counter ổn định qua restart, cần sửa cách track Target 2

Status: verification-only. Re-check checkpoint Portfolio sau ~13 round kể
từ lần đo dài hạn Round 23 để theo dõi Target 2, nhưng phát hiện 1 vấn đề
phương pháp luận quan trọng hơn bản thân số liệu.

## Quan sát: `trade_count` của BTC/binance GIẢM, không tăng

| Round | eval_count | trade_count (fixed-pct) | equity (fixed-pct) |
|---|---|---|---|
| 17-33 (ổn định nhiều round) | 2555→2594 | **1295** (không đổi) | ~9990.10 |
| 40 (round này) | **19 (reset)** | **1286** (giảm 9) | 9990.18 |

`eval_count=19` xác nhận worker BTC/binance vừa restart gần đây (khớp với
redeploy sau incident Postgres Round 26-32) — **đây chính là lý do
`trade_count` giảm, không phải mất dữ liệu/bug**. Đúng theo thiết kế đã biết
từ trước session `/loop` này (`continue_forward_from_replay`/
`SimulatedLedger::continue_from`): mỗi lần worker restart, ledger được
**tái tạo lại từ 1 lần backtest replay mới** thay vì tiếp tục nguyên trạng
— và vì "holdout"/backtest window dịch chuyển theo ngày hiện tại, số lệnh
tái tạo có thể khác đôi chút mỗi lần replay lại (1295 → 1286), không phải
monotonic counter thật.

## Ý nghĩa phương pháp luận cho việc track Target 2

**`trade_count` đọc từ Redis checkpoint KHÔNG phải là thước đo tin cậy để so
sánh "Make Decision rate có tăng qua thời gian" giữa 2 round cách nhau 1 lần
restart** — chênh lệch quan sát được có thể hoàn toàn do backtest reseed,
không phản ánh gì về hành vi forward thật. Toàn bộ log CSV v2 từ Round 11
tới giờ đã ngầm giả định trade_count là counter cộng dồn ổn định — giả định
này **chỉ đúng khi không có restart xen giữa 2 lần đo**. Round 17→33 (không
có restart) trade_count đúng là ổn định; Round 33→40 (có restart do
incident) thì không.

## Đề xuất cách track đúng hơn (không cần code mới, chỉ đổi cách Claude đo)

Từ các round sau: mỗi lần đọc checkpoint, **luôn kiểm tra `eval_count` trước
khi so sánh `trade_count` với round trước** — nếu `eval_count` nhỏ bất
thường (dấu hiệu restart gần đây), không so sánh trực tiếp trade_count với
số liệu round trước restart; thay vào đó chỉ track trade_count tăng dần
**trong cùng 1 giai đoạn không restart** (giống Round 17→33 đã làm đúng).
Không log task implement cho Codex — đây là sửa cách Claude tự đo, không
phải bug hệ thống.

## Trạng thái Target 2 hiện tại (baseline mới sau restart)

Baseline mới để track từ giờ: BTC/binance trade_count=1286 (eval_count=19),
BTC/exness=1312 (eval_count=4565, KHÔNG restart gần đây — worker này khác
chu kỳ), XAU/binance=8 (eval_count=19, restart), XAU/exness=735
(eval_count=188, có vẻ cũng mới restart nhưng đã eval nhiều hơn). Sẽ so
sánh round sau với các số baseline mới này, ghi rõ round nào có restart xen
giữa để không tái phạm lỗi so sánh sai.
