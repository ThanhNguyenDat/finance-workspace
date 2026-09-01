# Round 107 (2026-08-23) — Volume filter cho `ema_crossover_12_26` @ 30m (điểm neo tốt nhất của Round 78) — ĐÓNG, kết quả không ổn định giữa 4 route

Status: research, thêm 1 candidate
(`ema_crossover_12_26_vol20_1_3`, tái dùng `VolumeFilterStrategy` đã có) vào
`finance-research/src/strategies.rs`. Chạy 4 route ở `--interval 30m`, 5
năm, 2 cặp song song (1 cặp Exness phải retry solo do transient tunnel
error, đã ghi nhận).

## Bối cảnh

Không có commit mới từ Codex. Round 78 (đã đóng) từng flag
`ema_crossover_12_26` @ base interval 30m là **candidate ổn định nhất từng
tìm được** trong toàn chương trình (PF 0.85-0.97, không giật cục), và gợi ý
rõ ràng "thử thêm 1 lever khác (vd: bộ lọc volatility)" — chưa ai làm việc
này. `VolumeFilterStrategy` đã có sẵn trong code (trước đó chỉ dùng kèm
stochastic MTF) nên đây là combo đầu tiên áp trực tiếp lên điểm neo.

## Kết quả — baseline (tái xác nhận Round 78) vs volume-filtered, 5 năm

| Route | | train | valid | holdout | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | baseline | 0.908 | 0.816 | 0.831 | 586 |
| BTC/binance | +volume filter | 1.051 | 0.651 | **1.393** | 154 |
| XAU/binance | baseline | 0.884 | 0.998 | 0.906 | 74 |
| XAU/binance | +volume filter | 1.092 | 0.981 | **0.359** | 16 |
| BTC/exness | baseline | 0.880 | 0.794 | 0.841 | 588 |
| BTC/exness | +volume filter | 1.330 | 0.462 | 1.025 | 91 |
| XAU/exness | baseline | 0.570 | 0.762 | 1.009 | 386 |
| XAU/exness | +volume filter | 0.580 | 1.028 | 0.784 | 66 |

Baseline khớp gần đúng số của Round 78 (chênh nhỏ do cửa sổ dữ liệu đã trôi
thêm từ khi đó) — xác nhận đúng candidate neo.

## Phân tích — không có shape chung, khác cả 4 route

Không giống Round 106 (2 broker BTC cho cùng 1 shape trước khi cross-check
làm lộ vấn đề), volume filter ở đây tạo ra **4 shape khác nhau hoàn toàn**
giữa 4 route: BTC/binance và BTC/exness đều zigzag lên-xuống-lên nhưng biên
độ khác hẳn nhau (BTC/exness dao động 1.330→0.462→1.025, biên độ lớn hơn
nhiều BTC/binance); XAU/binance đổ dốc tệ ở holdout (0.359); XAU/exness lại
hình dạng lên-xuống ngược. Số lệnh giảm rất mạnh (65-90%) và không đều —
dấu hiệu cổ điển của filter cắt xuống 1 tập con quá nhỏ, ngẫu nhiên may rủi
theo từng route, không phải 1 cơ chế lọc nhiễu thật.

**Không cần cross-check cửa sổ 18 tháng** — bằng chứng đã yếu ngay trong
cửa sổ 5 năm (không nhất quán giữa 4 route), yếu hơn cả Round 106 (vốn ít
nhất còn nhất quán 2 broker BTC trước khi bị 18 tháng bác bỏ).

## Kết luận — ĐÓNG

Volume filter không phải lever thật cho `ema_crossover_12_26` @ 30m. Đóng
hẳn hướng "thêm volatility/volume filter cho điểm neo Round 78" bằng
`VolumeFilterStrategy` với tham số 20/1.3 — nếu muốn thử lại trong tương
lai, nên đổi hẳn tham số (period/ratio khác) hoặc cơ chế lọc khác (ATR-based
thay vì volume-based), không lặp lại đúng combo này.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu candidate làm bản ghi
  closed-negative (research-only), hoặc revert nếu không cần giữ.
