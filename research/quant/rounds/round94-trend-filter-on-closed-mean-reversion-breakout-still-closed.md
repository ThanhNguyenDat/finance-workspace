# Round 94 (2026-08-22) — Thử trend-filter (Round 33's edge nguồn) lên Keltner reversion + Donchian breakout đã đóng — ĐÓNG cả 2, Donchian suýt hứa hẹn nhưng đảo dấu trên cửa sổ độc lập

Status: research, thêm 2 candidate `mtf_*_trend_filtered` vào
`finance-research/src/strategies.rs` (cùng file uncommitted với Round 88/91/93,
tổng 4 candidate mới trong phiên chờ Codex review 1 lượt). Đầu round đã review
Dev-done item của Round 92 (Codex sửa comment khớp đúng số liệu, chưa push vì
chờ XAU marker lane — không cần hành động thêm từ tôi).

## Giả thuyết (từ gợi ý cuối Round 93)

Round 33 tìm ra: oscillator PLAIN (RSI/Stochastic không filter) đều thua lỗ
0/3 test, nhưng khi thêm trend-filter (chỉ vào lệnh khi khung lớn đồng thuận
hướng) thì mới có edge — "trend filter mới là nguồn edge", không phải bản thân
oscillator. Câu hỏi: liệu cơ chế này cũng áp dụng được cho 2 candidate mới
đóng trong phiên (Keltner reversion Round 91, Donchian breakout Round 88)?

## Implementation

Thêm `mtf_keltner_reversion_20_2_5_sma10_trend_filtered` và
`mtf_donchian_breakout_200_sma10_trend_filtered` vào `multi_timeframe_candidates()`,
dùng tham số tốt nhất mỗi candidate đã tìm được (Keltner multiplier=2.5,
Donchian period=200), trend-filter SMA10 khớp convention các candidate MTF
khác trong file. `--higher-timeframe-interval 4h` (base 5m), khớp combo chuẩn
đã dùng cho production (`mtf_stochastic_5m_4h_sma5`). `cargo build`/`fmt`
sạch.

## Kết quả 5 năm

| Candidate | BTC/binance holdout | BTC/exness holdout | XAU/binance holdout | XAU/exness holdout |
|---|---|---|---|---|
| mtf_keltner_reversion (2.5, sma10) | 0.77 | 0.83 | 0.87 (n=38, mỏng) | 0.69 |
| mtf_donchian_breakout (200, sma10) | **0.97** | **0.99** | 0.51 (n=26, mỏng) | 0.92 |

**Keltner reversion + trend-filter: ĐÓNG rõ ràng** — PF<1 mọi route/split,
không có gì hứa hẹn. Trend-filter không "giải cứu" được cơ chế reversion này
như đã làm với oscillator ở Round 33.

**Donchian breakout + trend-filter: gần hứa hẹn nhất — PF suýt chạm 1 rất
nhất quán trên validation+holdout của cả BTC 2 broker** (0.97-1.08), dù train
thấp hơn (0.80-0.83) — dạng "yếu train, mạnh sau" đúng cảnh báo trong quy
trình, bắt buộc cross-validate cửa sổ độc lập trước khi tin.

## Cross-check 18 tháng độc lập (bắt buộc) — ĐẢO NGƯỢC hoàn toàn, đóng

| | train | validation | holdout |
|---|---|---|---|
| BTC/binance | **1.30** | 0.70 | 0.88 |
| BTC/exness | **1.18** | 0.73 | 0.90 |

**Hình dạng đảo ngược hoàn toàn so với cửa sổ 5 năm**: 5 năm cho train THẤP,
validation/holdout CAO; 18 tháng cho train CAO, validation/holdout THẤP HƠN.
Đây chính xác là dạng false-positive kinh điển đã cảnh báo trong quy trình —
kết quả phụ thuộc cửa sổ lịch sử, không phải edge ổn định. Mẫu 18 tháng cũng
khá mỏng (48-51 trade/split). **ĐÓNG — không promote.**

## Kết luận

Giả thuyết "trend-filter cứu được mọi cơ chế đã đóng" (từ Round 33's kinh
nghiệm với oscillator) KHÔNG tổng quát hoá cho Keltner reversion hay Donchian
breakout. Đóng cả 2 hướng thử trong round này.

## Việc cho Codex

- **[trading][low]** Review gộp 4 candidate research-only trong cùng file
  (Donchian R88, Keltner R91, Heikin-Ashi R93, 2 biến thể MTF-filtered R94)
  — `cargo test -p finance-research` xanh, commit làm bản ghi hoặc revert.
  Không cấp bách.
