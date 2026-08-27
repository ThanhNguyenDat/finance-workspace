# Round 55 (2026-08-21) — Tool đã đổi cấu trúc lớn + số liệu THẬT đầu tiên của Portfolio production qua engine đúng

Status: research + verify, dùng đúng `finance-research` mới nhất (build lại
từ `origin/main` sau khi pull các commit Round 54 + `b3f6687`). Phát hiện 2
việc quan trọng: (1) tool đã đổi cấu trúc lớn, cách tôi test candidate suốt
54 round không còn dùng được nguyên dạng; (2) lần đầu tiên có số liệu Sharpe/
Sortino/streak THẬT của chính Portfolio production (không phải backtest tay
hay signal-only-exit giả lập).

## 1. Thay đổi cấu trúc tool — QUAN TRỌNG, ảnh hưởng toàn bộ workflow từ giờ

- **`--gate-strategy` đã bị XOÁ HOÀN TOÀN khỏi CLI.** Chạy lệnh cũ
  (`--daily-profit-gate --gate-strategy X`) giờ báo lỗi
  `unexpected argument '--gate-strategy'`. Đây là cách tôi đã dùng ở TOÀN
  BỘ Round 17-53 để test extended metrics (Sharpe/Sortino/streak/
  positive_day_ratio) cho từng candidate cụ thể — **không còn dùng được**.
- **`--daily-profit-gate` giờ nghĩa khác hẳn:** theo `--help` mới, nó
  *"Evaluate the synchronized production Portfolio decision engine on
  holdout only"* — tức đánh giá đúng cấu hình Portfolio ĐANG LIVE (2
  strategy `candle_momentum`+`rsi_mean_reversion`, trọng số thật), không
  còn nhận tham số chọn candidate nào khác.
- **`--weighted-ensemble-gate` (mới, từ Round 54) bị hardcode** đúng 1
  ensemble cụ thể ("the exact BTC 4h/1d Round 54 fixed-weight Alpha
  ensemble") — không phải công cụ tổng quát để test ensemble tuỳ ý.
- **Tin tốt: sweep table thường (không có gate flag) vẫn hoạt động y hệt
  cũ** — tự verify lại candidate Round 17 baseline
  (`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, BTC 4h/1d) cho ĐÚNG
  số liệu cũ (39/19/18 trade, PF 1.658/2.040/1.650) — bảng PF/win-rate Alpha
  layer từ Round 17-53 **vẫn đáng tin**, chỉ có phần Sharpe/Sortino/streak/
  positive_day_ratio riêng cho từng candidate là không re-verify được nữa
  bằng công cụ hiện tại.
- **Phát hiện thêm:** `--daily-profit-gate` giờ có
  `minimum_trades_per_week` trong `failed_checks` — đúng đề xuất tool-gap
  tôi log ở Round 17! Codex đã fix cả gap này cùng đợt.

## 2. Số liệu THẬT ĐẦU TIÊN của chính Portfolio production (qua engine đúng)

### BTC/binance (5m, đúng interval production)
`passed=false`, fail 6/9 check: `positive_day_ratio` 37.7%, streak 10 ngày,
**Sortino -6.69, Sharpe -6.73**, net PnL holdout **-$13.39**.

### XAU/binance (5m)
`passed=false`, fail 8/9 check kể cả `minimum_trades_per_week` MỚI:
`observed_days=51` (rất ngắn), `positive_day_ratio=0%`, net PnL=$0.00,
Sharpe/Sortino=None (không đủ variance để tính) — **khớp hoàn toàn** với
mọi lần tôi đọc checkpoint thấy XAU Portfolio gần như không ra quyết định
mới (Round 23/40/48).

## Ý nghĩa

Đây là bằng chứng THẬT, THẨM QUYỀN NHẤT từ trước tới giờ rằng: **Target 1
(có lời/không lỗ ổn định) hiện KHÔNG đạt cho BTC** (Sharpe -6.73 là con số
rất tệ, không phải biên độ nhỏ) và **Target 2 (Make Decision rate) vẫn
stagnant cho XAU** (observed_days chỉ 51/366, quá ít quyết định thật). Khác
hẳn mọi số liệu trước đây của tôi (vốn dựa trên simplified signal-mapper
hoặc backtest tay tự tính) — đây là số liệu qua đúng
`PortfolioDecisionPolicy` thật đang chạy production.

## Đề xuất cho Codex (không phải bug, đề xuất tăng khả năng research)

`--weighted-ensemble-gate` hiện hardcode đúng 1 tổ hợp — nếu muốn tiếp tục
research ensemble/candidate mới với extended metrics (Sharpe/Sortino/
streak) qua engine thật, cần 1 cách tổng quát hơn (vd nhận JSON config chỉ
định danh sách strategy + trọng số qua CLI, thay vì hardcode) — không phải
việc khẩn cấp, chỉ ghi nhận để khi cần research tiếp có sẵn hướng đề xuất.
