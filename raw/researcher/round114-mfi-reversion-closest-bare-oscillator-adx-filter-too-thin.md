# Round 114 (2026-08-23) — MFI (Money Flow Index) mean reversion — ĐÓNG; bản thô là oscillator gần breakeven nhất từng thấy, bản ADX-filtered bị loại vì mẫu quá mỏng/zigzag

Status: research, thêm indicator mới `finance_strategy::indicators::mfi`
(file mới `crates/finance-strategy/src/indicators/mfi.rs`, 4 unit test,
đăng ký qua `indicators.rs`) và `MfiReversionStrategy` +
`adx_filtered_mfi_reversion_14_20_80` vào `finance-research/src/strategies.rs`.
Chạy 4 route 5 năm, 2 cặp song song (`--cpus=2 --memory=4g --memory-swap=6g`,
Rule 9).

## Bối cảnh

Không có commit mới từ Codex. Round102 follow-up còn chờ market mở cửa lại
(22:00 UTC). Sau Round 113 (OBV — volume cộng dồn không giới hạn, thất
bại nặng), Round 114 test **MFI** — oscillator bị chặn 0-100 giống RSI
nhưng có trọng số volume, khác cấu trúc cả OBV (không chặn) lẫn RSI thuần
giá. Dùng đúng `AdxRangeFilterStrategy` (filter phù hợp cho mean-reversion,
không phải `SmaTrendFilterStrategy` vốn dành cho trend-following) để test
song song bản thô và bản có filter.

## Kết quả — bản thô (5 năm, chi phí thật)

| Route | train PF | valid PF | holdout PF | win% (holdout) | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | 0.753 | 0.744 | 0.675 | 54.4% | 1,306 |
| BTC/exness | 0.765 | **0.958** | 0.771 | 58.2% | 698 |
| XAU/binance | 0.561 | 0.419 | 0.387 | 33.8% | 195 |
| XAU/exness | 0.481 | 0.612 | 0.791 | 54.9% | 546 |

**Win rate cao bất thường (33.8-58.2%)** so với hầu hết candidate khác đã
test phiên này (đa số momentum/breakout chỉ 12-25%) — MFI reversion có cơ
chế cân bằng tốt hơn hẳn. BTC/exness validation đạt PF **0.958** (gần chạm
breakeven, mẫu đủ lớn 460 trade) — **oscillator thô (không filter) gần
breakeven nhất từng quan sát trong toàn chương trình** (mọi oscillator
khác đã đóng — RSI/Stochastic/CCI/Bollinger reversion — đều PF thấp hơn rõ
rệt ở dạng thô). Vẫn <1 mọi ô nên không promote.

## Kết quả — bản ADX-filtered — ĐÓNG vì zigzag + mẫu quá mỏng, không cần cross-check 18 tháng

| Route | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|
| BTC/binance | 1.151 | 0.771 | 1.012 | 126 |
| BTC/exness | 0.623 | **3.640** | 1.083 | 41 |
| XAU/binance | 0.668 | **1.475** | 0.313 | 15 |
| XAU/exness | 0.594 | **2.754** | 0.468 | 36 |

Filter ADX giảm mẫu rất mạnh (còn 12-269 trade so với 195-1306 bản thô) và
tạo ra **zigzag không nhất quán** — validation nhảy vọt lên PF 1.475-3.640
(mẫu chỉ 12-41 trade, artifact kinh điển) rồi rơi lại ở holdout (0.313-1.083),
không có shape chung giữa 4 route. **Không cần cross-check cửa sổ 18 tháng**
— bằng chứng đã tự loại ngay trong window 5 năm do thiếu nhất quán nội tại
(giống phương pháp đã áp dụng ở Round 107, khác Round 106 vốn cần cross-check
vì có nhất quán cross-broker trước khi bị 18 tháng bác bỏ).

## Kết luận — ĐÓNG cả 2 biến thể

Không promote. Bản thô là tài liệu tham khảo tốt (oscillator gần breakeven
nhất, win rate cao, không giật cục) nhưng vẫn <1 mọi nơi. Bản ADX-filtered
không đáng tin vì mẫu quá mỏng và không nhất quán.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `mfi()` indicator +
  `MfiReversionStrategy` làm bản ghi closed-candidate (research-only, ghi
  rõ bản thô là "closest bare oscillator" tham khảo), hoặc revert nếu không
  cần giữ.
- Nếu muốn tiếp tục hướng MFI trong tương lai, nên thử threshold khác
  (vd 25/75 thay vì 20/80, để tăng tần suất mà không dùng ADX filter làm
  mẫu quá mỏng) thay vì lặp lại đúng combo ADX đã đóng ở đây.
