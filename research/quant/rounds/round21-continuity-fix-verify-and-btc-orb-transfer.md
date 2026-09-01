# Round 21 (2026-08-20) — Verify fix continuity round 2 + ORB/VWAP không transfer sang BTC

Status: research-only. 2 việc trong round này: (1) keep-check tiến độ Codex
trên item continuity đã log Round 18/20 (Rule 5), (2) test cross-instrument
cho candidate ORB 30m đầy hứa hẹn nhất (Round 18) — dùng lại đúng candidate
đã build, test thêm 1 instrument khác thay vì tạo mới.

## 1. Verify fix `cc49386` ("cover Exness DST rollover schedule")

Codex ship thêm 1 fix continuity nữa sau `e9f5287` (Round 20 đã verify).
`cc49386` mở rộng pattern daily-rollover để cover cả lệch giờ DST (21→22 UTC
mùa hè, 22→23 UTC mùa đông — trước chỉ hardcode đúng 21→22). Tự build, chạy
`cargo test daily_profit_gate` (11/11 pass), rồi re-run 2 gate case đã biết
fail continuity qua tunnel production:

| Candidate/combo | Violations trước (Round 18/15) | Violations sau `e9f5287`+`cc49386` | Giảm |
|---|---|---|---|
| `opening_range_breakout_london_30m`, Exness XAU 5m | 95 (sau `e9f5287` riêng, Round 20) | **32** | -66% |
| `mtf_candle_momentum_10bps_sma10_trend_filtered`, Exness XAU 4h/1d | 108 (Round 15, trước mọi fix) | **57** | -47% |

**Cả 2 fix đều có tác dụng thật, đo được bằng số cụ thể — không phải fix vô
ích.** Nhưng `holdout_interval_continuity` vẫn fail ở cả 2 combo — còn 32 và
57 violation thật chưa giải thích được. Đã thử tìm cách tự lấy raw kline
timestamp để tự root-cause pattern còn lại (finance-research `--json` không
lộ list nến, chỉ lộ count; port 8086 chỉ gRPC thuần, không có REST endpoint
song song) — không root-cause được thêm trong round này, cần cách khác (có
thể cần Codex thêm 1 flag debug xuất raw gap timestamps, hoặc audit trực
tiếp Timescale/Finance MW).

## 2. ORB 30m/60m + VWAP — KHÔNG transfer sang BTC (kết quả sạch, đúng hướng)

Test 4 candidate y hệt Round 18 (chưa đổi tham số) trên BTC/binance 5m, 5
năm — instrument hoàn toàn khác (XAU/exness → BTC/binance):

| Candidate | Train PF | Validation PF | Holdout PF |
|---|---|---|---|
| `session_vwap_reversion_london_14_1_5` | 0.815 | 0.818 | 0.697 |
| `session_vwap_reversion_london_14_2_0` | 0.842 | 0.791 | 0.743 |
| `opening_range_breakout_london_30m` | 0.879 | 0.669 | 0.744 |
| `opening_range_breakout_london_60m` | 0.740 | 0.619 | 0.737 |

**Cả 4 candidate đều PF<1 nhất quán CẢ 3 split trên BTC — không có ngoại lệ,
kể cả ORB 30m (candidate hứa hẹn nhất trên XAU).** Đây là kết quả sạch,
đúng hướng kỳ vọng về mặt cơ chế: ORB/VWAP session-anchored (London 08:00
UTC) dựa trên giả định có 1 "phiên giao dịch" thật với thanh khoản/biến động
đặc trưng lúc mở phiên — đúng với FX/vàng (Exness XAU giao dịch theo phiên,
đóng cửa cuối tuần) nhưng BTC giao dịch 24/7 liên tục, không có khái niệm
"mở phiên London" ảnh hưởng đặc biệt. Không cần test thêm BTC/exness (cùng
lý do cơ chế, không phải đặc thù riêng 1 broker).

**Kết luận:** giữ đúng nguyên tắc Rule 4 (không cần 1 setup chung cho mọi
token) — ORB/VWAP session-anchored chỉ nên xét cho XAU (và có thể các cặp
forex/CFD khác có phiên thật), không đề xuất cho BTC/crypto. Không cần
Codex làm gì thêm ở mục này, chỉ ghi nhận làm evidence cho quyết định
scope-theo-instrument.
