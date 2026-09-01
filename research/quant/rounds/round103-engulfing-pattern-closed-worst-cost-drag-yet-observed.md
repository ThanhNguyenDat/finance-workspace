# Round 103 (2026-08-23) — Two-candle engulfing pattern (mới hoàn toàn, chưa từng test) — ĐÓNG, PF thấp nhất từng quan sát vì tần suất tín hiệu quá cao khuếch đại chi phí giao dịch

Status: research, thêm `EngulfingPatternStrategy` (candidate mới hoàn toàn,
chưa có trong file) vào `finance-research/src/strategies.rs` (research-only,
uncommitted, cùng lô chờ Codex review).

## Bối cảnh

Không có commit mới từ Codex kể từ Round 102 (vẫn `2840dcc`, Processing vẫn
đang xử lý loạt credential-exposure/OOM chờ XAU marker lane đóng). XAU/Exness
vẫn đóng cửa cuối tuần (kiểm tra lúc 02:34 UTC Chủ Nhật, còn cách giờ mở cửa
22:00 UTC gần 20 giờ) nên follow-up production đã đề xuất ở Round 102 chưa
thực hiện được. Toàn bộ 5 cơ chế Alpha mới trong phiên này (Donchian/Keltner/
Heikin-Ashi/MTF-filtered/strength-filtered) đều đã đóng, và bảng closed-
directions gần như phủ hết mọi cơ chế channel/band/oscillator hợp lý. Round
103 chọn hướng còn thật sự chưa test: **candlestick pattern 2 nến** (không
phải channel/band/oscillator) — mẫu hình engulfing kinh điển.

## Implementation

`EngulfingPatternStrategy`: state đơn giản (chỉ lưu open/close nến trước,
theo `instrument:timeframe`), không lookahead — chỉ đọc nến trước đã đóng.
Quy tắc: nến trước đỏ + nến hiện tại xanh + thân nến hiện tại bao trọn thân
nến trước (`open ≤ prev.close` và `close ≥ prev.open`) → Long; ngược lại →
Short. `strength = (current_body - previous_body) / current_body`, kẹp [0,1].
`cargo fmt --check` + `cargo build -p finance-research` sạch (Docker `--cpus=3`).

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật: fee 5bps + slippage 2bps)

| Route | train PF (trades) | validation PF (trades) | holdout PF (trades) | win% holdout |
|---|---|---|---|---|
| BTC/binance | 0.399 (34054) | 0.359 (11026) | **0.347** (11198) | 21.1% |
| XAU/binance | 0.249 (3854) | 0.218 (1388) | **0.159** (1445) | 12.6% |
| BTC/exness | 0.487 (20686) | 0.418 (9380) | **0.420** (6806) | 24.8% |
| XAU/exness | 0.148 (14261) | 0.192 (4581) | **0.344** (4647) | 22.0% |

**PF thấp nhất từng quan sát trong toàn bộ chương trình** — thấp hơn rõ rệt
mọi candidate khác từng test (kể cả những cái đã đóng như VWAP/Bollinger/ORB,
vốn thường ở khoảng 0.6-0.9). Nhất quán tuyệt đối cả 12 ô (3 split × 4 route)
đều <0.5 — không có shape "yếu train mạnh holdout" hay đảo chiều giữa broker,
nên **không cần cross-check cửa sổ 18 tháng độc lập** (khác các round trước
phải làm vậy vì kết quả có vẻ hứa hẹn/mâu thuẫn) — kết luận đã đủ rõ ràng
ngay từ 5 năm.

## Cost ablation — phân loại cost-limited, không phải edge-limited

Chạy lại BTC/binance với `--fee-bps 0 --slippage-bps 0`:

| Split | trades | win% | PF (no cost) |
|---|---|---|---|
| train | 34054 | 37.9% | 0.974 |
| validation | 11026 | 39.7% | 0.985 |
| holdout | 11198 | 39.6% | **0.994** |

Bỏ hết chi phí, PF gần chạm đúng 1.0 (0.974-0.994) — **cost-limited**, khớp
đúng "trần chi phí cấu trúc" đã xác nhận ở Round 96/98 cho Donchian/Keltner/
Heikin-Ashi. Nguyên nhân PF thấp bất thường khi CÓ chi phí không phải vì
raw edge âm nặng, mà vì **tần suất tín hiệu cực cao** (34,054 trade/route
trên train — gấp ~4-15 lần Donchian/Keltner/Heikin-Ashi cùng window) khiến
phí giao dịch bị nhân lên nhiều lần hơn hẳn mọi candidate khác từng test.
Mẫu hình 2 nến (engulfing) về bản chất trigger rất thường xuyên trên timeframe
5m vì chỉ cần 1 cặp nến liền kề thỏa điều kiện — khác các mẫu channel/band
cần tích lũy nhiều nến.

## Kết luận — ĐÓNG

Không promote. Cùng kết luận cấu trúc như Round 93/96/98/99/101 (raw edge
≈0, bị chi phí ăn hết), nhưng là ví dụ rõ nhất từ trước tới giờ cho thấy
**tần suất tín hiệu quá cao tự nó là một cách khác để chạm trần chi phí**,
không chỉ do edge âm. Không có động lực thử trend-filter cho mẫu hình này
(khác Donchian ở Round 94) vì PF quá xa 1.0 ngay cả không chi phí thật —
trend-filter thường chỉ giúp khi PF cost-real đã gần biên, không phải khi
cách xa 0.35-0.42 như đây.

## Cập nhật Round 105 — xác nhận độc lập bug fix của Codex, tác động không đáng kể

Codex (root review, commit `06f8bed` trên branch local `codex/round103-engulfing-record`)
phát hiện bug thật trong implementation gốc: `previous_bullish == current_bullish`
(với `bullish := close > open`) coi doji (`close == open`) là "không tăng",
nên 1 doji trước đó có thể vô tình được xem như nến giảm hợp lệ để kích hoạt
tín hiệu. Đã áp dụng đúng fix của Codex (strict `previous_bearish`/`current_bullish`
hoặc `previous_bullish`/`current_bearish`, loại hẳn doji khỏi cả 2 phía) vào
working copy, rebuild, chạy lại BTC/binance 5 năm để định lượng tác động:

| | trades (holdout) | PF (holdout) |
|---|---|---|
| Semantics cũ (buggy) | 11,197 | 0.347 |
| Semantics đúng (Round 105 fix) | 11,134 | 0.348 |

Chênh lệch không đáng kể (0.6% số lệnh, ΔPF=0.001) — khớp kỳ vọng vì doji
thật (`close` khớp chính xác `open`) rất hiếm trên dữ liệu 5m thực tế. **Kết
luận CLOSED của round này giữ nguyên, không cần sửa gì thêm.** Cảm ơn Codex
đã bắt được lỗi qua root review.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `EngulfingPatternStrategy`
  làm bản ghi closed-candidate (cùng lô với 5 candidate khác chờ review), hoặc
  revert nếu không cần giữ.
- Đóng hẳn hướng "candlestick pattern 2 nến thô, không lọc" — nếu muốn thử lại
  candlestick pattern trong tương lai, cần đi thẳng vào version có trend-filter
  hoặc lọc theo `strength`/context (không lặp lại phiên bản thô này).
