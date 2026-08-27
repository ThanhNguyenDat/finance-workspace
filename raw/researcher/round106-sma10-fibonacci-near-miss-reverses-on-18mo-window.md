# Round 106 (2026-08-23) — SMA(10) trend filter cho Fibonacci Golden Zone(100) — PF>1 hấp dẫn trên 5 năm cả 2 broker BTC, nhưng ĐẢO HÌNH DẠNG hoàn toàn trên 18 tháng độc lập — ĐÓNG, near-miss gần nhất phiên này

Status: research, thêm 1 candidate (`sma10_trend_filtered_fibonacci_golden_zone_100`,
tái dùng `SmaTrendFilterStrategy` đã có từ Round 104) vào
`finance-research/src/strategies.rs`. Chạy 4 route thành 2 cặp song song
(`--cpus=2 --memory=4g --memory-swap=6g`, đúng Rule 9), sau đó thêm 2 lượt
18 tháng độc lập cho riêng BTC khi phát hiện dạng nghi ngờ.

## Bối cảnh

Không có commit mới từ Codex; XAU/Exness vẫn đóng cửa cuối tuần. Tiếp nối
Round 104 (rescue engulfing bằng trend filter, thất bại) và Round 105
(Fibonacci Golden Zone gốc, đóng), Round 106 áp đúng công thức tương tự cho
tham số ổn định nhất của Round 105 (`fibonacci_golden_zone_100`) — nhưng lần
này kết quả 5 năm ban đầu **rất khác** mọi round trước.

## Kết quả 5 năm — PF>1 ở validation VÀ holdout, nhất quán 2 broker BTC

| Route | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|
| BTC/binance | 0.929 | **1.447** | **1.248** | 172 |
| BTC/exness | 0.968 | **1.141** | **1.026** | 170 |
| XAU/binance | 0.580 | 1.823 | 1.805 | 18 (quá mỏng) |
| XAU/exness | 0.699 | 0.688 | 1.439 | 83 |

BTC ở CẢ 2 broker đều cho PF>1 ở validation và holdout — lần đầu tiên trong
phiên này 1 candidate vượt breakeven nhất quán qua 2 broker độc lập, đúng
tiêu chí "khớp cross-broker" mà chương trình coi là bằng chứng mạnh hơn 1
broker đơn lẻ. Đây là dạng "yếu train, mạnh validation+holdout" — theo quy
tắc đã ghi rõ trong skill, **bắt buộc phải cross-check trên cửa sổ độc lập**
trước khi tin, dù kết quả hấp dẫn tới đâu.

## Cross-check 18 tháng độc lập (bắt buộc) — ĐẢO HÌNH DẠNG hoàn toàn

| Route | Window | train PF | valid PF | holdout PF |
|---|---|---|---|---|
| BTC/binance | 5 năm | 0.929 | 1.447 | 1.248 |
| BTC/binance | **18 tháng** | **1.497** | **0.822** | **2.062** |
| BTC/exness | 5 năm | 0.968 | 1.141 | 1.026 |
| BTC/exness | **18 tháng** | **1.201** | **0.492** | **1.562** |

Trên cửa sổ 18 tháng, **train giờ >1** (đảo từ <1), **validation tụt xuống
<1** (đảo từ >1) — vị trí split "yếu/mạnh" hoán đổi hoàn toàn so với cửa sổ
5 năm, ở CẢ 2 broker cùng lúc. Đây chính xác là dạng "đảo hình dạng trên cửa
sổ độc lập" mà chương trình đã coi là bằng chứng dứt điểm của false-positive/
overfit trong nhiều round trước (ORB Round 34, mtf_donchian Round 94,
strength-filter Heikin-Ashi Round 99) — áp dụng nguyên tắc "regardless of how
good headline numbers look". Mẫu cũng rất mỏng trên 18 tháng (46-140 trade/
split so với 170-572 trên 5 năm) — càng làm giảm độ tin cậy.

## XAU: cả 2 broker đều thêm dấu hiệu không đáng tin

- XAU/binance: PF 1.8+ nhưng chỉ 18-24 trade/split — quá mỏng để kết luận
  theo bất kỳ chiều nào.
- XAU/exness: train/valid yếu (0.699/0.688), chỉ holdout >1 (1.439, 83
  trade) — dạng "chỉ holdout thắng" đã bị phủ định nhiều lần trong chương
  trình.

## Kết luận — ĐÓNG, nhưng là near-miss gần nhất phiên này

Không promote. Dù headline 5 năm rất hấp dẫn và nhất quán cross-broker —
đúng loại bằng chứng mạnh nhất từng thấy trước khi cross-check — cửa sổ 18
tháng độc lập đảo ngược hoàn toàn, nên phải đóng theo đúng kỷ luật đã áp
dụng nhất quán trong toàn chương trình. Đây là ví dụ rõ nhất từ trước tới
giờ cho thấy **vì sao bước cross-check bắt buộc, không phải thủ tục hình
thức** — nếu dừng lại ở 5 năm sẽ ra quyết định promote sai. Ghi nhận là
near-miss gần nhất (cùng nhóm với `atr_breakout_14_3_0` Round 61 — cũng
từng đẹp trên 1 cửa sổ/broker rồi thất bại khi cross-validate).

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu candidate làm bản ghi
  closed-near-miss (đã có sẵn cả 2 wrapper `SmaTrendFilterStrategy`/
  `FibonacciGoldenZoneStrategy`, chỉ cần đăng ký thêm 1 label), hoặc revert.
- Nếu muốn tiếp tục hướng Fibonacci+trend-filter trong tương lai, nên bắt
  đầu ngay từ việc test đa cửa sổ (không chỉ 5 năm) trước khi báo cáo số
  liệu đầu tiên — tránh lặp lại việc phải quay lại cross-check sau khi đã
  có kết quả "đẹp" ban đầu.
