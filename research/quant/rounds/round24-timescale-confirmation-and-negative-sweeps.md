# Round 24 (2026-08-20) — Củng cố phát hiện Round 19 qua timescale thứ 3 + 2 sweep phủ định

Status: research-only. 3 việc: (1) test thêm 1h/1d (timescale MTF thứ 3,
chưa ai thử) cho đúng candidate baseline Round 17, (2) quét Bollinger/
Supertrend regime-filter chưa test ở 4h/1d, (3) quét toàn bộ XAU/exness
4h/1d tìm candidate PF>1 nhất quán (chưa ai làm full sweep này, chỉ test
từng candidate riêng lẻ trước đây).

## 1. Xác nhận Round 19 bằng timescale thứ 3 (1h/1d) — không còn là 1 data point đơn lẻ

Round 19 đã chứng minh: đổi base interval 4h→5m (cùng higher-tf=1d, cùng
candidate `mtf_stochastic_14_3_30_70_sma50_trend_filtered`) làm MỌI metric
chất lượng xấu đi trong khi tần suất chỉ tăng nhẹ. Round này test thêm
timescale thứ 3 (**1h**, giữa 4h và 5m) cho đúng candidate đó — cùng
phương pháp, không đổi gì khác:

| Base interval | Sharpe | Sortino | Max neg-day streak | Net PnL holdout | Trades/week holdout |
|---|---|---|---|---|---|
| 4h (Round 17, tốt nhất) | **1.13** | **3.10** | 48 | 1.69 | 0.34 |
| 1h (Round 24, mới) | 0.57 | 1.48 | 46 | 1.01 | 0.55 |
| 5m (Round 19) | 0.71 | 2.02 | 47 | 1.24 | 0.55 |

**Không đơn điệu theo hướng "càng mịn càng nhiều trade" — 1h và 5m cho tần
suất gần bằng nhau (0.55/tuần cả 2) nhưng 1h lại có Sharpe/Sortino TỆ HƠN
CẢ 5m** (0.57 vs 0.71, 1.48 vs 2.02). Điều này củng cố thêm giả thuyết Round
19 (trần tần suất do chính oscillator/trend-filter quyết định, không phải
hàm đơn điệu của độ mịn nến) và cho thấy quan hệ này còn phức tạp hơn "nhỏ
hơn = nhiều nhiễu hơn theo tỉ lệ" — 4h vẫn là điểm tối ưu rõ ràng, không
phải điểm biên của 1 trend đơn điệu. Kết luận thực dụng: **không cần thử
thêm base interval nào khác cho đúng candidate này** — đã có 3 điểm dữ liệu
đồng thuận, đủ để khẳng định 4h là lựa chọn tốt nhất trong nhóm 5m/1h/4h.

Test thêm 1 candidate MACD mới ở 1h/1d (`mtf_macd_19_39_9_sma10_trend_filtered`,
PF 1.14/1.27/1.35 tăng dần nhất quán ở bảng sweep) qua full gate: Sharpe
0.49, Sortino 1.10 (pass sát nút), streak 25 ngày, net PnL $0.99 — vẫn fail
gate (`positive_day_ratio`, `negative_day_streak`, `sharpe_ratio`), không
tốt hơn các candidate đã biết.

## 2. Bollinger + Supertrend regime filter ở 4h/1d BTC — không có candidate mới

- `mtf_bollinger_reversion_20_2_sma10_trend_filtered`: PF 1.2/0.858/0.769 —
  thắng train, thua validation+holdout. Không nhất quán.
- `mtf_stochastic_14_3_35_65_supertrend10_3_filtered`: PF 0.748/0.77/1.146 —
  thua train+validation, chỉ thắng holdout — cùng dạng "chỉ thắng split
  cuối" đã cảnh giác nhiều lần (candle_reversion Round 12, ORB 30m Round 18).
  Không tin được, không phải candidate.

## 3. XAU/exness 4h/1d — quét toàn bộ, ZERO candidate PF>1 nhất quán

Chạy lại đúng sweep đầy đủ (51 candidate) cho XAU/exness ở khung 4h/1d —
**không có bất kỳ candidate nào PF>1 nhất quán cả 3 split** (khác hẳn BTC,
nơi có 4 candidate ở round 17-18). Xác nhận bằng số liệu: họ swing 4h/1d
trend-filtered hoạt động tốt cho BTC nhưng KHÔNG có edge tương tự cho XAU ở
cùng timescale — đúng nguyên tắc Rule 4 (mỗi token cần setup riêng, không
suy diễn từ 1 token sang token khác). Không cần Codex làm gì — chỉ là bằng
chứng ranh giới áp dụng của họ candidate này.

## Tổng kết round

Không tìm được candidate mới nào đạt target. Giá trị chính của round này là
**thu hẹp không gian tìm kiếm bằng bằng chứng phủ định có hệ thống** — giờ
đã biết chắc: (a) trong họ MTF stochastic/macd trend-filtered, 4h/1d là
timescale tốt nhất cho BTC (đã test đủ 5m/1h/4h), không cần thử thêm biến
thể base interval nào khác; (b) Bollinger/Supertrend regime filter không
thêm giá trị ở đây; (c) XAU cần hướng khác hẳn BTC ở swing timescale (đã
biết ORB 30m London-session là hướng XAU-specific duy nhất còn mở, xem
Round 18/21).
