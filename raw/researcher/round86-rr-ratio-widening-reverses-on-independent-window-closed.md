# Round 86 (2026-08-22) — Test R:R ratio (không phải độ rộng tuyệt đối) theo yêu cầu owner ("tỉ lệ R hơi thấp") — ĐÓNG, đảo dấu trên cửa sổ độc lập

Status: research only, không commit gì. Trước round này, Codex đã tự commit 3
fix lớn (`6eebf76` fix đúng finding Round 85 — root cause là cap đóng băng ở
starting equity + leverage research bị mislabel 1x cho perpetual; `54cf66a`,
`af09209` — dependency breaker cho Live Action outage). Đã rebuild
`finance-research-local` với code mới trước khi test round này.

## Bối cảnh

Owner nhận xét "tỉ lệ R tôi thấy hơi thấp" — hiểu là R:R (risk:reward) của
stop/take hiện tại = 1:2 (`PORTFOLIO_STOP_VALUE=0.01`,
`PORTFOLIO_TAKE_VALUE=0.02`, giữ nguyên tỉ lệ này xuyên suốt Round 80→83, chỉ
đổi ĐỘ RỘNG tuyệt đối chứ chưa từng đổi TỈ LỆ). Test giả thuyết: giữ nguyên
stop=0.01 (đã validate ở Round 83), chỉ nới take để tăng R:R lên 1:2.5/1:3/1:4.

## Bước 1 — Sweep trên window 5 năm (giống phương pháp Round 80/83)

`--portfolio-stop-value 0.01`, sizing mặc định `fixed_notional=5`, hold=36,
`one_target`, `--days 1825`:

| take_value | R:R | BTC/binance pnl | BTC/binance trades | BTC/exness pnl | BTC/exness trades |
|---|---|---|---|---|---|
| 0.02 (hiện tại) | 1:2 | -$16.52 | 2439 | -$19.00 | 2417 |
| 0.025 | 1:2.5 | -$14.50 | 2322 | -$15.42 | 2309 |
| **0.03** | **1:3** | **-$12.56** | 2244 | **-$14.18** | 2215 |
| 0.04 | 1:4 | -$13.42 | 2078 | -$14.14 | 2057 |

1:3 nhìn tốt nhất trên CẢ 2 broker (giảm lỗ ~24-25% so với 1:2 hiện tại),
1:4 tệ hơn 1:3 (không đơn điệu, có đỉnh). Cross-instrument XAU cùng hướng
nhưng biên độ nhỏ hơn nhiều: XAU/exness -$4.39→-$4.31 (~2%), XAU/binance quá
ít trade (8) để có ý nghĩa.

## Bước 2 — Cross-validate trên window 18 tháng độc lập (bắt buộc theo bài học
Round 34/79) → ĐẢO DẤU hoàn toàn

| take_value | R:R | BTC/binance pnl (18m) | BTC/exness pnl (18m) |
|---|---|---|---|
| 0.02 (hiện tại) | 1:2 | **-$0.77** | **-$1.27** |
| 0.03 | 1:3 | -$1.00 (TỆ HƠN) | -$1.43 (TỆ HƠN) |

Trên cửa sổ 5 năm, 1:3 thắng rõ trên cả 2 broker. Trên cửa sổ 18 tháng độc
lập, 1:3 THUA trên CẢ 2 broker (cùng hướng đảo ngược, không phải nhiễu ngẫu
nhiên 1 phía). Đây đúng khuôn mẫu false-positive đã biết (ORB Round 18→34,
`mtf_ema_crossover` Round 79) — "chỉ thắng ở 1 cửa sổ, đảo ngược ở cửa sổ
khác" → đóng, không promote.

## So sánh với 2 lever ĐÃ validate thành công (Round 80, 83)

Khác biệt quan trọng: Round 80 (`minimum_hold_decisions` 12→36) và Round 83
(độ rộng stop/take tuyệt đối 0.005/0.010→0.01/0.02) đều đã **tự confirm khớp
hướng trên CẢ window 5 năm lẫn 18 tháng** trước khi triển khai (ghi rõ trong
`SUMMARY-priority-backlog.md` mục ưu tiên). Lever tỉ lệ R:R lần này KHÔNG đạt
được điều đó — chỉ thắng ở 1 trong 2 cửa sổ.

## Kết luận

**KHÔNG đề xuất đổi R:R ratio.** Giữ nguyên `PORTFOLIO_STOP_VALUE=0.01` /
`PORTFOLIO_TAKE_VALUE=0.02` (1:2) như hiện tại — đây vẫn là cấu hình tốt nhất
đã validate được qua 2 cửa sổ độc lập. Trả lời trực tiếp nhận xét của owner:
tỉ lệ 1:2 hiện tại "thấp" hơn các con số phổ biến trong tài liệu trading
(1:3 hay hơn) nhưng dữ liệu thật của hệ thống này KHÔNG ủng hộ nới rộng thêm
— nới ra chỉ thắng trên 1 cửa sổ lịch sử cụ thể, đảo ngược ở cửa sổ khác,
đúng dạng overfit đã phủ định nhiều lần trước đây trong chương trình này.

## Việc cho round sau

Không có action item mới cho Codex (kết luận là "giữ nguyên", không phải
"đổi"). Đóng hướng "đổi tỉ lệ R:R" — không cần test lại trừ khi có cơ chế mới
khác hẳn (vd R:R thay đổi theo regime/ATR thay vì hằng số cố định).
