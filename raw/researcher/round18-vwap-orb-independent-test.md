# Round 18 (2026-08-20) — Độc lập backtest 4 candidate VWAP/ORB Codex mới ship

Status: research-only, không implement/deploy. Đây là "keep check lại chiến
thuật đã setup nếu codex đã implement" theo Rule 5 — Codex đã commit
`e7fb55b` ("feat(research): add session VWAP and ORB candidates") lên
`finance-live-action main` trước round này, session `/loop` round 18 tự build
lại và chạy honest backtest thật (không tin lời commit message, tự verify
bằng số liệu).

## Setup

`finance-research` build từ `e7fb55b` (rebuild local, không đổi code), chạy
qua SSH tunnel production (`root@160.22.122.55:8086` → `127.0.0.1:18086`,
credentials không log ra process args). Instrument: **Exness XAU/USD, CFD,
5m base interval, 1825 ngày (5 năm)** — đúng combo Codex's commit message ghi
là mục tiêu ("ưu tiên Exness XAU"). `holdout_candles=70784`,
`holdout_calendar_days≈365`, nhưng `observed_days=310` sau gate (CFD đóng cửa
cuối tuần là hành vi thị trường thật, đã biết từ trước).

## Kết quả sweep table (train/validation/holdout PF)

| Candidate | Train (trades/win%/PF) | Validation | Holdout |
|---|---|---|---|
| `session_vwap_reversion_london_14_1_5` | 1316/55.5%/**0.513** | 441/58.5%/**0.547** | 470/63.6%/**0.598** |
| `session_vwap_reversion_london_14_2_0` | 996/54.1%/**0.591** | 327/57.8%/**0.654** | 322/57.1%/**0.503** |
| `opening_range_breakout_london_30m` | 360/44.2%/0.868 | 123/44.7%/1.023 | 123/48.0%/**1.275** |
| `opening_range_breakout_london_60m` | 386/46.4%/0.872 | 123/46.3%/1.111 | 112/42.0%/0.947 |

## 1. VWAP mean-reversion — PHỦ ĐỊNH, không phải candidate nữa

Cả 2 biến thể band-width (1.5σ và 2.0σ) đều PF<1 **nhất quán cả 3 split**,
mặc dù win rate khá cao (54-64%). Đây không phải nhiễu ngắn hạn — nhất quán
đủ để kết luận: mỗi lần thua trung bình lớn hơn nhiều mỗi lần thắng (R:R
tệ), y hệt cơ chế đã falsify VWAP/ORB breakout families ở
`raw/proposal/portfolio-profitability-improvements.md` Round 2 cho BTC.
Không cần backtest thêm biến thể band-width khác trên combo instrument/
interval này — hướng VWAP mean-reversion (ít nhất theo state/RSI-confirmation
design hiện tại) không có edge ở Exness XAU 5m.

## 2. ORB 60m — không nhất quán, không phải candidate

PF 0.872/1.111/0.947 — dao động quanh 1.0 không theo hướng nào rõ, khác hẳn
pattern nhất quán cần có để tin tưởng.

## 3. ORB 30m — candidate thật nhưng CHƯA validate, kèm 1 phát hiện data quality

Full `--daily-profit-gate --gate-strategy opening_range_breakout_london_30m`:

```
passed: false
failed_checks: [holdout_interval_continuity, positive_day_ratio, median_daily_pnl, sharpe_ratio]
sortino_ratio: 1.854 (pass, ≥1.0)
sharpe_ratio: 0.944 (fail, sát ngưỡng 1.0)
maximum_negative_day_streak: 4 (pass, ≤5 — TỐT NHẤT toàn chương trình)
net_realized_pnl: 1.35 (dương)
cost_to_gross_pnl_ratio: 0.391 (pass, ≤0.5)
holdout_interval_continuity: FALSE (data quality, không phải signal quality)
```

Extended metrics tự tính từ `daily_results` thật (công thức giống Round 17,
xem `raw/researcher/round17-swing-4h1d-regime-filter-family.md`):
`ulcer_index=0.0042`, `max_drawdown_duration_days=121`,
`max_consecutive_losing_days=7`, `skew_daily_ret=3.78`,
`excess_kurtosis_daily_ret=30.43`, `sqn_daily_approx=0.870`.

**Vì sao chưa gọi là validated (không lặp lại sai lầm Round 12):**

1. **Pattern PF tăng dần qua 3 split (0.868 → 1.023 → 1.275)** — thua ở
   train, hoà ở validation, thắng ở holdout. Đây đúng hình dạng
   `candle_reversion` XAU Round 12 đã có (thua train/validation, thắng
   holdout mạnh) — và candidate đó sau bị **phủ định hoàn toàn** ở Round 13
   khi test trên dataset dài hơn (Exness, không phải Binance mẫu ngắn).
   Không tự động kết luận ORB 30m cũng sẽ bị phủ định — nhưng pattern giống
   hệt là lý do đủ để KHÔNG tin ngay, cần thêm dữ liệu hoặc walk-forward dài
   hơn để phân biệt "edge thật đang mạnh dần lên gần đây" khỏi "regime ngắn
   hạn trùng hợp trong đúng khoảng holdout này".
2. **`holdout_interval_continuity` fail thật** — đây là lỗi dữ liệu, không
   phải lỗi chiến lược. Round 15 (mục Alpha, `mtf_candle_momentum_10bps_
   sma10_trend_filtered` ở 4h/1d) đã fail đúng check này cho **cùng
   instrument Exness XAU/USD**, khác timeframe hoàn toàn (4h/1d vs 5m ở đây)
   — cùng 1 instrument fail cùng 1 check ở 2 timeframe độc lập là bằng chứng
   khá mạnh đây là vấn đề hệ thống (data gap/session-handling) của riêng
   Exness XAU, không phải trùng hợp ngẫu nhiên theo từng combo riêng lẻ. Đã
   gộp thành 1 Todo item duy nhất trong `raw/handoff_codex.md` thay vì để 2
   ghi chú rời rạc như trước.

**Vẫn đáng ghi nhận vì sao đây là kết quả tốt nhất về streak/frequency-tradeoff
tìm được tới giờ:** max negative-day streak chỉ 4 ngày — thấp hơn HẲN mọi
candidate swing 4h/1d ở Round 17 (17-66 ngày), đồng thời tần suất holdout
123 trade/366 ngày ≈ **2.37 lần/tuần** — cao hơn hẳn cả họ swing đó (0.21-
1.24/tuần). Sortino đã pass thật. Đây là ứng viên gần target nhất về mặt
"đồng thời đạt cả streak lẫn frequency tốt", dù Sharpe còn thiếu (0.94 vs
1.0) và 2 lý do thận trọng ở trên chưa cho phép coi là validated.

## Việc đề xuất tiếp theo (không tự làm, log cho Codex/round sau)

1. Điều tra gộp `holdout_interval_continuity` cho Exness XAU (5m và 4h/1d) —
   xem đây là data gap thật hay false-positive từ session-closure hợp lệ đã
   biết.
2. Nếu muốn tiếp tục theo đuổi ORB 30m: chạy lại trên window ngắn hơn gần đây
   (12-18 tháng, giống cách Round 13 test candle_reversion) để phân biệt
   regime-artifact khỏi edge thật, thay vì đợi observed_days tự nhiên tăng.
3. Không port thêm biến thể VWAP mean-reversion khác cho instrument/interval
   này — đã đủ bằng chứng phủ định.
