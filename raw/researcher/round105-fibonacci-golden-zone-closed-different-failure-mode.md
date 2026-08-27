# Round 105 (2026-08-23) — Fibonacci Golden Zone retracement (hướng đã ghi backlog từ Round 22, chưa từng implement) — ĐÓNG, failure mode khác hẳn mọi candidate trước

Status: research, thêm `FibonacciGoldenZoneStrategy` (candidate mới hoàn
toàn) vào `finance-research/src/strategies.rs` (research-only, uncommitted,
cùng lô chờ Codex review). Chạy 4 route thành 2 cặp song song, mỗi container
`--cpus=2 --memory=4g --memory-swap=6g` (đúng Rule 9).

## Bối cảnh

Codex có commit mới (`70c5811`, kline marker-backfill trailing growth) nhưng
vẫn ở Processing, chưa tới Verify — không có gì để tôi verify độc lập lượt
này. XAU/exness vẫn đóng cửa (checkpoint frozen `updated_at` không đổi kể từ
2026-08-22T13:26:56Z, đã xác nhận qua Redis). `handoff_agent.md` mục 97-98
đã ghi từ lâu: "Fibonacci Golden Zone retracement entry chưa được
research/implement" — Round 105 thực hiện đúng hướng này lần đầu tiên.

## Implementation

`FibonacciGoldenZoneStrategy`: theo dõi cửa sổ `period` nến gần nhất
(high, low), xác định leg xu hướng gần nhất bằng cách so sánh index của đỉnh
cao nhất và đáy thấp nhất trong cửa sổ (đỉnh xảy ra sau đáy → up-leg, ngược
lại → down-leg). Vào lệnh khi giá pullback vào vùng 61.8%-65% retracement
của leg đó: Long trong up-leg, Short trong down-leg — continuation-on-pullback,
khác hẳn breakout/reversion/oscillator đã test trước đây. Đọc cửa sổ TRƯỚC
khi push nến hiện tại (giống `DonchianBreakoutStrategy`) nên không lookahead.
3 chu kỳ 20/50/100 (bracket ngắn/trung/dài, cùng convention Donchian).
`cargo fmt` + `cargo build -p finance-research` sạch.

## Kết quả — 5 năm, 3 split, cả 4 route, 3 chu kỳ (chi phí thật)

| Route | Period | train PF | valid PF | holdout PF | win% (holdout) |
|---|---|---|---|---|---|
| BTC/binance | 20 | 0.790 | 0.605 | 0.661 | 40.0% |
| BTC/binance | 50 | 0.781 | 0.574 | 0.653 | 44.3% |
| BTC/binance | 100 | 0.940 | 0.768 | 0.652 | 48.7% |
| XAU/binance | 20 | 0.786 | **1.068** | 0.378 | 24.2% |
| XAU/binance | 50 | 0.655 | 0.745 | 0.534 | 32.4% |
| XAU/binance | 100 | 0.617 | 0.696 | 0.805 | 36.1% |
| BTC/exness | 20 | 0.694 | 0.721 | 0.650 | 38.1% |
| BTC/exness | 50 | 0.801 | 0.549 | 0.706 | 46.3% |
| BTC/exness | 100 | 0.985 | 0.638 | 0.774 | 49.8% |
| XAU/exness | 20 | 0.427 | 0.534 | 0.666 | 37.2% |
| XAU/exness | 50 | 0.443 | 0.574 | **0.966** | 48.4% |
| XAU/exness | 100 | 0.539 | 0.399 | 0.737 | 48.7% |

## Phát hiện quan trọng: win rate cao bất thường nhưng PF vẫn <1 — failure mode khác

Win rate 24-54% trên toàn bộ 36 ô — **cao hơn rõ rệt** so với hầu hết
candidate đã đóng trước đây (thường <25%, có ô engulfing chỉ 12.6%). Đây là
mẫu hình pullback-continuation nên tự nhiên có tỷ lệ thắng khá hơn cơ chế
breakout/reversion thuần. Nhưng PF vẫn <1 mọi ô — nghĩa là vấn đề nằm ở
**R:R bất lợi** (thua nhiều hơn thắng mỗi khi sai), không phải win rate thấp
— khớp đúng kết luận đã đóng ở Round 86 (nới R:R không cứu được hệ thống
hiện tại) áp dụng sang 1 cơ chế hoàn toàn mới.

## 2 ô "gần breakeven" — cả 2 đều là false-positive shape đã biết, không tin

- **XAU/binance period 20, validation PF=1.068**: train 0.786, holdout chỉ
  0.378 — dạng "yếu train/holdout, mạnh 1 split giữa" kinh điển đã cảnh báo
  nhiều lần trong chương trình (ORB Round 34, mtf_donchian Round 94). Mẫu
  cũng rất mỏng (107-120 trade/split).
- **XAU/exness period 50, holdout PF=0.966**: train/validation chỉ 0.443/
  0.574 — cùng dạng "yếu 2 split đầu, mạnh 1 split cuối", không đáng tin dù
  con số holdout gần chạm 1.0.

Tham số ổn định nhất là **period 100** (ít giật cục nhất giữa các split cho
cả 2 route BTC: 0.940/0.768/0.652 và 0.985/0.638/0.774) nhưng **vẫn <1 mọi
split** — không đủ để promote.

## Kết luận — ĐÓNG

Không promote bất kỳ tham số/route nào. Đóng hẳn hướng Fibonacci Golden Zone
đã treo trong backlog từ Round 22. Ghi nhận đóng góp phương pháp luận: đây là
candidate đầu tiên cho thấy rõ ràng win-rate không phải nút thắt (win rate
tốt hơn hẳn candidate khác) — nút thắt luôn là R:R, củng cố thêm bằng chứng
cho kết luận đã đóng ở Round 86 từ 1 góc hoàn toàn khác (mẫu hình pullback
thay vì breakout/reversion).

## Sự cố hạ tầng nhỏ trong lúc chạy song song

2 lần chạy Exness (BTC + XAU) trong cặp thứ 2 gặp lỗi transient
`h2 protocol error`/`transport error` qua tunnel SSH khi chạy đồng thời với
tải khác — không phải bug logic. Đã restart tunnel và chạy lại solo, thành
công ngay lần đầu. Ghi nhận trung thực, không âm thầm bỏ qua.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `FibonacciGoldenZoneStrategy`
  làm bản ghi closed-candidate (cùng lô 7 candidate khác chờ review), hoặc
  revert nếu không cần giữ.
- Đóng hẳn hướng "Fibonacci Golden Zone thô, không trend filter" trong
  `SUMMARY-priority-backlog.md` mục 1 (gỡ khỏi danh sách "chưa research").
