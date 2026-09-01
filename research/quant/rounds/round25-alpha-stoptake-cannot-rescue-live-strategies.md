# Round 25 (2026-08-20) — Alpha-level stop/take không cứu được 2 strategy đang live (BTC + XAU)

Status: research-only. Round 9/47 trước đây đã chứng minh R:R/sizing không
cứu được `candle_momentum` cho **XAU** (Portfolio-layer). Round này mở rộng
đầy đủ hơn: test **alpha-level** stop/take (`--alpha-stop-value`/
`--alpha-take-value`, khác biệt với Portfolio-layer protective config đã
test trước) cho **cả 2 strategy đang thật sự live** (`candle_momentum`,
`rsi_mean_reversion`) trên **cả 2 instrument perpetual đang live**
(BTC/binance, XAU/binance) — 4 tổ hợp, chưa ai test đủ trước đây.

## Baseline (raw, signal-only-exit, không stop/take) — khớp đúng số liệu production

| Instrument | Strategy | Holdout trades | Win% | PF |
|---|---|---|---|---|
| BTC/binance | candle_momentum_10bps | 15591 | 22.7 | 0.346 |
| BTC/binance | rsi_mean_reversion_14_30_70 | 2485 | 54.4 | 0.625 |
| XAU/binance | candle_momentum_10bps | 688 | 23.0 | 0.356 |
| XAU/binance | rsi_mean_reversion_14_30_70 | 364 | 29.7 | 0.256 |

Khớp đúng số liệu production thật đã ghi nhận đầu chương trình research này
(candle_momentum PnL -113.18/22.7% win, rsi_mean_reversion -14.73 trên
BTC/binance real ledger) — xác nhận backtest và production đồng nhất cho 2
strategy này (câu hỏi user đặt ra trước đây về backtest-vs-production).

## Test 3 mức stop/take khác nhau

| Config | candle_momentum PF (holdout) | rsi_mean_reversion PF (holdout) |
|---|---|---|
| Baseline (không stop/take) | BTC 0.346 / XAU 0.356 | BTC 0.625 / XAU 0.256 |
| stop=0.005/take=0.01 (giống Portfolio default) | BTC 0.346 / XAU 0.344 | BTC 0.602 / XAU 0.281 |
| stop=0.02/take=0.04 (rộng gấp 4x) | BTC 0.346 (không đổi) | BTC 0.633 (gần baseline) |

## Kết luận rõ ràng, nhất quán cả 4 tổ hợp

1. **`candle_momentum` hoàn toàn bất biến với stop/take** ở cả BTC lẫn XAU
   (PF không đổi quá 0.01 dù thay đổi mạnh stop/take) — xác nhận lại đúng cơ
   chế Round 9/47 đã tìm ra cho XAU: phần lớn lệnh đóng bởi **tín hiệu đối
   lập** trước khi chạm stop/take, không phải bởi protective level. Giờ có
   bằng chứng y hệt trên BTC — không phải đặc thù riêng XAU.
2. **`rsi_mean_reversion` bị stop/take chặt LÀM XẤU ĐI** (số lệnh tăng gấp
   đôi vì exit sớm hơn, win rate giảm, PF không cải thiện hoặc xấu đi nhẹ) —
   ở cả BTC lẫn XAU. Stop/take rộng thì gần như không có tác dụng (quay lại
   baseline) — không có điểm cân bằng nào tốt hơn baseline được tìm thấy.
3. **Không có mức stop/take nào (chặt, giống default, hay rộng) đưa PF của
   1 trong 4 tổ hợp lên trên 1.0.** Đây là kết luận đóng, không phải giả
   thuyết — đã test đủ range.

## Ý nghĩa cho Target 1

**Sizing/R:R/protective-level tuning KHÔNG thể là lời giải cho Target 1 (có
lời/không lỗ) đối với 2 strategy đang live** — đã chứng minh đủ 4/4 tổ hợp
instrument×strategy. Đòn bẩy duy nhất còn lại thật sự là **thay signal**
(khớp đúng kết luận xuyên suốt cả chương trình research: momentum/RSI đơn
giản ở 5m không có edge thật; các candidate MTF swing 4h/1d Round 17 có edge
nhưng tần suất quá thấp; ORB 30m Round 18 có tần suất khá hơn nhưng chưa
validate). Không đề xuất Codex làm gì thêm ở mục sizing/protective cho 2
strategy hiện tại — hướng này đã đóng, đừng lặp lại.
