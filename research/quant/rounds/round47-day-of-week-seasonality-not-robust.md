# Round 47 (2026-08-20) — Day-of-week seasonality cho BTC: KHÔNG ổn định qua split-test, đóng hướng này

Status: research thật, dùng dữ liệu bên ngoài (Binance public kline API,
không cần auth) — ý tưởng hoàn toàn mới, chưa từng test trong 47 round.
Sau khi đóng hướng patch funding-reversion (Round 45-46), thử open interest
public API trước (chỉ giữ 30 ngày lịch sử, quá ngắn để test honest — bỏ
qua ngay), rồi chuyển sang ý tưởng day-of-week seasonality.

## Phương pháp

Fetch `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=1500`
(public, không cần auth) — 1500 nến ngày thật, 2022-07-13 → 2026-08-20
(~4.1 năm). Tính return trong ngày (`(close-open)/open`) theo từng thứ
trong tuần (UTC), so sánh mean/t-statistic trên toàn kỳ VÀ 2 nửa độc lập
(đúng tinh thần split-test đã dùng xuyên suốt chương trình).

## Kết quả: có pattern ở toàn kỳ, nhưng KHÔNG ổn định khi chia đôi

| Thứ | Toàn kỳ (4.1yr) mean/t | Nửa đầu (2022-2024) mean/t | Nửa sau (2024-2026) mean/t |
|---|---|---|---|
| Thứ 2 | +0.396%/**t=2.32** | +0.594%/**t=2.46** | +0.198%/t=0.82 |
| Thứ 3 | -0.040%/t=-0.23 | -0.046%/t=-0.19 | -0.033%/t=-0.14 |
| Thứ 4 | +0.407%/**t=2.39** | +0.362%/t=1.51 | +0.452%/t=1.87 |
| Thứ 5 | -0.199%/t=-1.17 | -0.061%/t=-0.25 | -0.335%/t=-1.39 |
| Thứ 6 | +0.118%/t=0.69 | +0.162%/t=0.67 | +0.073%/t=0.30 |
| Thứ 7 | +0.020%/t=0.12 | +0.076%/t=0.31 | -0.036%/t=-0.15 |
| CN | +0.134%/t=0.79 | +0.276%/t=1.14 | -0.008%/t=-0.03 |

**Thứ Hai** trông có vẻ đáng chú ý ở toàn kỳ (t=2.32, mượt sát ngưỡng "có ý
nghĩa") nhưng **gần như biến mất ở nửa sau** (t=0.82) — không ổn định.
**Thứ Tư** cũng vậy, giữ được hướng nhưng không đạt ngưỡng ý nghĩa ở cả 2
nửa riêng lẻ. Không có thứ nào đạt |t|>2 ở CẢ 2 nửa cùng lúc — đúng dấu
hiệu kinh điển của 1 pattern giả (data-mining artifact khi test 7 nhóm cùng
lúc), không phải seasonality thật.

## Kết luận: ĐÓNG, không đề xuất implement

Đúng tinh thần honest-holdout của chương trình này — 1 pattern chỉ đáng tin
khi ổn định qua split, không chỉ đẹp ở toàn kỳ. Day-of-week seasonality cho
BTC **không đạt ngưỡng này**. Không log task cho Codex, không tốn thêm thời
gian test biến thể khác của ý tưởng này (giờ trong ngày, tuần trong tháng)
trừ khi có lý do cụ thể khác để nghi ngờ 1 khung thời gian cụ thể nào đó.

## Ghi chú phụ: Open Interest public API không dùng được cho backtest

`futures/data/openInterestHist` (Binance public) chỉ giữ tối đa **30 ngày**
lịch sử bất kể `limit` yêu cầu — không đủ cho honest walk-forward, cùng
loại hạn chế đã gặp với `1m` kline retention nội bộ (Round 15/27). Không
theo đuổi hướng open interest qua API công khai này; nếu muốn dùng OI làm
signal, cần nguồn dữ liệu lịch sử dài hơn (có thể phải trả phí hoặc dùng
nguồn khác), không phải research item cho session này.
