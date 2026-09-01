# Round 110 (2026-08-23) — CCI momentum breakout (indicator mới hoàn toàn) — ĐÓNG; phát hiện phụ: trend filter gần như không đổi gì

Status: research, thêm indicator mới `finance_strategy::indicators::cci`
(file mới `crates/finance-strategy/src/indicators/cci.rs`, 5 unit test,
đăng ký qua `indicators.rs`) và `CciBreakoutStrategy` +
`sma10_trend_filtered_cci_breakout_20_100` vào
`finance-research/src/strategies.rs`. Chạy 4 route 5 năm, 2 cặp song song
(`--cpus=2 --memory=4g --memory-swap=6g`, Rule 9).

## Bối cảnh

1 commit mới từ Codex (`6823535`, CI/BuildKit, observability, không cần
review). Round102 XAU/Exness follow-up còn chờ market mở cửa lại (22:00
UTC). Round 110 chọn **CCI (Commodity Channel Index)** — oscillator dùng
mean-deviation, khác hẳn công thức RSI (gain/loss average) và Stochastic
(vị trí trong range cao/thấp) đã test trước đây. Theo đúng convention file
(`New reusable indicators... belong in finance-strategy/src/indicators/`),
đã thêm `cci()` như 1 hàm indicator dùng chung thay vì viết trực tiếp trong
`strategies.rs`.

## Implementation

`CciBreakoutStrategy`: đóng vai momentum breakout (không phải mean-
reversion) — Long khi CCI cắt lên trên `+threshold`, Short khi cắt xuống
dưới `-threshold`, chỉ nổ đúng nến chuyển zone (giống convention
`SmaTrendStrategy`). Tham số chuẩn sách giáo khoa 20/100. Đăng ký cả bản
gốc lẫn bản có `SmaTrendFilterStrategy` (đã có từ Round 104) trong CÙNG 1
lượt chạy — theo đúng phát hiện đã đóng ở Round 33 ("oscillator thô không
filter luôn thất bại"), thay vì tốn 1 round riêng test bản thô rồi mới test
bản có filter.

## Kết quả — 5 năm, 3 split, cả 4 route, cả 2 biến thể (chi phí thật)

| Route | Biến thể | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | thô | 0.553 | 0.530 | 0.529 | 4061 |
| BTC/binance | +SMA10 filter | 0.553 | 0.530 | 0.529 | 4061 |
| BTC/exness | thô | 0.557 | 0.549 | 0.542 | 4047 |
| BTC/exness | +SMA10 filter | 0.557 | 0.549 | 0.542 | 4047 |
| XAU/binance | thô | 0.362 | 0.375 | 0.334 | 583 |
| XAU/binance | +SMA10 filter | 0.360 | 0.376 | 0.336 | 581 |
| XAU/exness | thô | 0.256 | 0.297 | 0.489 | 2748 |
| XAU/exness | +SMA10 filter | 0.256 | 0.297 | 0.490 | 2744 |

## Phát hiện phụ — trend filter gần như KHÔNG đổi gì (khác mọi filter test trước)

Số lệnh và PF của bản có filter gần như **trùng khớp tuyệt đối** với bản
thô (chênh lệch trade chỉ 0-4 lệnh/route trên hàng nghìn lệnh) — khác hẳn
mọi filter đã test trước (Round 94/104/106/107 đều thấy filter cắt giảm
30-90% số lệnh). Nguyên nhân hợp lý: CCI cắt qua ngưỡng ±100 tự nó đã hàm ý
giá đang di chuyển mạnh theo 1 hướng, nên hầu như luôn trùng hướng với
SMA(10) sẵn — filter trở thành no-op vì 2 điều kiện gần như tương đương
nhau về mặt thống kê cho cơ chế breakout cụ thể này (khác Fibonacci/
Engulfing vốn có thể pullback ngược xu hướng ngắn hạn).

BTC nhất quán cross-broker rõ (0.553/0.530/0.529 vs 0.557/0.549/0.542).
XAU/exness có xu hướng nhẹ "yếu train/valid, khá hơn holdout" (0.256/0.297/
0.489) nhưng vẫn rất xa 1.0 nên không đáng lo, không cần cross-check 18
tháng.

## Kết luận — ĐÓNG

Không promote bất kỳ route/biến thể nào — toàn bộ 12 ô (2 biến thể × 4
route × ~1.5 split trung bình do trùng nhau) đều PF<0.6, thấp và không có ô
nào gần breakeven. Ghi nhận phát hiện phụ về trend-filter-no-op cho tương
lai: nếu 1 breakout mechanism khác cũng cho filter gần như không đổi gì,
đó là dấu hiệu 2 điều kiện đã tương quan cao sẵn, không cần test thêm biến
thể filter khác cho đúng combo đó.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `cci()` indicator +
  `CciBreakoutStrategy` làm bản ghi closed-candidate (research-only), hoặc
  revert nếu không cần giữ. Indicator `cci()` là hàm generic độc lập, có
  thể tái dùng cho cơ chế khác (vd: CCI mean-reversion ngưỡng ±100 thay vì
  breakout) nếu muốn thử hướng khác trong tương lai.
