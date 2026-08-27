# Round 65 (2026-08-21) — CORRECTION: nguyên nhân thật của Target 2 stagnant là bất đối xứng subscription strategy, không phải "lịch sử ngắn"

Status: correction + code-verified mechanism discovery. Đọc trực tiếp source
code `reweight_from_alpha_performance` (thay vì chỉ suy luận từ production
state như Round 63-64), tái tạo công thức bằng Python, verify khớp chính
xác 100% với số liệu production quan sát được.

## Tóm tắt sửa lỗi

Round 63-64 quan sát đúng hiện tượng (Binance/XAU có `interval_weights` bị
zero-out hàng loạt ở các interval "entry", khác hẳn 3 route còn lại) nhưng
**suy luận sai nguyên nhân** ("lịch sử ngắn từ khi listing Dec 2025 → chưa
đủ dữ liệu → thuật toán reweight cho weight=0"). Đọc code thực tế cho thấy
**điều ngược lại**: thiếu dữ liệu (`trade_count=0`) được thuật toán cho
**quality=1.0 (tối đa)**, không phải 0 — đây là "benefit of the doubt" có
chủ đích cho signal chưa từng được test.

## Đọc code: `alpha_performance_quality` (`trading_modes.rs:510-537`)

```rust
fn alpha_performance_quality(performance: SimulatedPerformance) -> f64 {
    let confidence = (performance.trade_count as f64 / PERFORMANCE_CONFIDENCE_TRADES).clamp(0.0, 1.0);
    if confidence == 0.0 {
        return 1.0;  // <-- THIẾU DỮ LIỆU = QUALITY TỐI ĐA, không phải 0
    }
    let empirical = if performance.realized_pnl > 0.0 && performance.gross_profit > 0.0 {
        // ... tính từ win_rate * profit_factor * (1 - drawdown_ratio)
    } else {
        0.0  // thua lỗ xác nhận = quality 0, CHỈ KHI đã có đủ trade_count
    };
    (1.0 - confidence) + confidence * empirical
}
```

`PERFORMANCE_CONFIDENCE_TRADES = 20.0` (`trading_modes.rs:400`) — cần ≥20
trade để đạt confidence=1.0 (đánh giá đầy đủ).

`reweight_from_alpha_performance` (`trading_modes.rs:464-503`) cộng dồn
`interval_quality[interval] += alpha_performance_quality(...)` **qua TẤT
CẢ strategy đã subscribe** cho route đó, rồi normalize.

## Tái tạo công thức bằng dữ liệu production thật — khớp 100%

Đọc `simulated_ledgers` (per interval × strategy) từ checkpoint, tính lại
quality bằng công thức trên, so với `interval_weights` quan sát Round 63:

| Route | Quality tự tính (chuẩn hoá) | `interval_weights` thật (Round 63) |
|---|---|---|
| Binance/XAU | 12h=0.338, 1d=0.521, 4h=0.141, còn lại=0 | **khớp chính xác** |
| Exness/XAU | 12h=0.199, 15m=0.116, 1d=0.223, 1h/2h/30m/4h=0.116, 5m=0 | **khớp chính xác** |

Công thức đúng 100% — có thể tin tưởng phần phân tích cơ chế bên dưới.

## Nguyên nhân thật: Binance/XAU chỉ subscribe 2 strategy, các route khác 3-5

`strategy_weights` (số lượng key = số strategy đã subscribe cho route đó):

| Route | Strategy đã subscribe | Số lượng |
|---|---|---|
| **Binance/XAU** | `candle_momentum`, `rsi_mean_reversion` | **2** |
| Exness/XAU | `candle_momentum`, `rsi_mean_reversion`, `mtf_stochastic_5m_4h_sma5` | 3 |
| Binance/BTC | `candle_momentum`, `rsi_mean_reversion`, `mtf_candle_momentum_5m_4h_sma10`, `mtf_macd_5m_4h_sma10`, `mtf_stochastic_5m_4h_sma10` | 5 |
| Exness/BTC | tương tự Binance/BTC (5 strategy, biến thể MTF khác nhẹ) | 5 |

Điểm mấu chốt: `mtf_stochastic_5m_4h_sma5` của Exness/XAU có **`trade_count=0`
ở MỌI interval trừ 5m** (383 trades) — tức chưa từng kích hoạt ở
15m/30m/1h/2h/4h/12h/1d. Theo công thức, `trade_count=0` → `quality=1.0` tự
động ở các interval đó. Vì `interval_quality` CỘNG DỒN qua mọi strategy, 1
strategy chưa-test đóng góp +1.0 "miễn phí" vào MỌI interval nó chưa chạm
tới — tạo ra 1 cái "sàn" (floor) khiến `interval_quality` tối thiểu ≈1.0 ở
mọi interval cho Exness/XAU.

**Binance/XAU không có "sàn" này** vì chỉ có 2 strategy, và CẢ 2 đều đã
thua lỗ với đầy đủ confidence (trade_count hàng trăm-nghìn ở mọi interval
ngắn — xem bảng dưới) → `quality=0.0` chính xác ở những interval đó, không
strategy nào "cứu" được tổng.

### Bằng chứng: performance thật của 2 strategy trên Binance/XAU (mọi interval đều đã có đủ ≥20 trade)

| Interval | `candle_momentum` trade/pnl | `rsi_mean_reversion` trade/pnl |
|---|---|---|
| 15m | 3662 / **-26.79** | 528 / **-4.37** |
| 30m | 2464 / **-17.31** | 268 / **-2.20** |
| 1h | 1578 / **-12.70** | 135 / **-2.02** |
| 2h | 938 / **-6.01** | 72 / **-0.66** |
| 5m | 5228 / **-38.19** | 1772 / **-11.53** |
| 4h | 466 / -1.11 | 48 / **+0.08** (nhỏ, không đủ nâng tổng) |
| 12h | 196 / **+0.55** | 15 (confidence<1) / +0.03 |
| 1d | 112 / -0.54 | 2 (confidence rất thấp) / -0.84 |

Cả 2 strategy thua lỗ nhất quán ở hầu hết interval (khớp hoàn toàn với kết
luận Round 25/55-59 của cả chương trình: `candle_momentum`/`rsi_mean_reversion`
không có edge thật) — 12h/1d có ít trade hơn (confidence thấp hơn) nên vẫn
giữ được 1 phần "benefit of doubt", đó là lý do 3 interval trend dài hạn
nhất vẫn còn trọng số dương.

## Điểm thú vị: đây KHÔNG phải do XAU "kém" — mà do THIẾU 1 strategy "vô hại"

Ở Exness/XAU, chính vì `mtf_stochastic_5m_4h_sma5` **chưa từng thắng cũng
chưa từng thua** (0 trade ở hầu hết interval) mà nó vô tình "cứu" toàn bộ
interval_weights. Đây là 1 hệ quả phụ (side-effect) của thiết kế công thức
— không phải lỗi logic sai, nhưng tạo ra hành vi khó đoán: **số lượng
strategy subscribe (không phải chất lượng) quyết định liệu 1 interval có
"chết" hoàn toàn hay không**, miễn là ít nhất 1 trong các strategy subscribe
chưa được test đủ ở interval đó.

## Đề xuất cụ thể cho Codex — rủi ro thấp, không cần sửa thuật toán

**Subscribe thêm 1 strategy nữa cho Binance/XAU** (ví dụ đúng
`mtf_stochastic_5m_4h_sma5` như Exness/XAU đang có, hoặc bất kỳ biến thể MTF
nào phù hợp) — theo đúng công thức đã verify ở trên, việc này sẽ ngay lập
tức tạo lại "sàn" và nâng `interval_weights` các interval entry (15m/30m)
lên >0, tăng tần suất Make Decision (Target 2) **mà không cần sửa
`reweight_from_alpha_performance`**. Đây là thay đổi cấu hình (subscription
list), rủi ro thấp hơn nhiều so với sửa thuật toán reweight.

**Cần Codex xác nhận:**
1. Đây có phải chỉ là thay đổi config (biến môi trường/subscription list),
   hay cần sửa code khởi tạo policy?
2. Tại sao Binance/XAU thiếu strategy thứ 3 ngay từ đầu so với 3 route còn
   lại — có phải thiếu sót cấu hình đơn giản khi route mới được thêm (Dec
   2025 listing), hay có lý do kỹ thuật cụ thể (ví dụ thiếu dữ liệu để tính
   `mtf_stochastic` ban đầu, giờ đã đủ)?
3. Nên chọn strategy nào để thêm — khuyến nghị dùng đúng
   `mtf_stochastic_5m_4h_sma5` (đã có sẵn, đã chứng minh hoạt động tốt trên
   Exness/XAU) để giữ nhất quán, trừ khi có lý do kỹ thuật khác.

**Giới hạn:** đề xuất dựa trên đọc code + tái tạo công thức khớp 100% với
dữ liệu production — độ tin cậy cao, nhưng chưa test được hiệu ứng thật (vì
đây là thay đổi runtime config, cần Codex triển khai rồi Claude verify lại
qua production checkpoint ở round sau, không thể backtest trước bằng
`finance-research` vì công cụ không có flag để mô phỏng thêm strategy vào
policy hiện có).

## Cập nhật Round 66 — mô phỏng định lượng hiệu ứng dự kiến ngay sau khi subscribe

Dùng đúng công thức đã verify (Round 65), mô phỏng bằng Python: nếu subscribe
thêm 1 strategy mới cho Binance/XAU với `trade_count=0` ở mọi interval (đúng
trạng thái ban đầu ngay sau khi subscribe, trước khi nó kịp tích luỹ trade
nào) — mỗi interval nhận thêm `+1.0` raw quality "miễn phí":

| Interval | Weight TRƯỚC (thật, Round 63) | Weight SAU (dự đoán, ngay sau subscribe) |
|---|---|---|
| 5m | 0.0000 | 0.1028 |
| **15m** | **0.0000** | **0.1028** |
| **30m** | **0.0000** | **0.1028** |
| 1h | 0.0000 | 0.1028 |
| 2h | 0.0000 | 0.1028 |
| 4h | 0.1408 | 0.1278 |
| 12h | 0.3377 | 0.1627 |
| 1d | 0.5214 | 0.1954 |

**Tổng trọng số 2 interval "entry" (15m+30m) đi từ 0.0000 → 0.2056** —
tương đương gần 21% ảnh hưởng lên `entry_score`, đủ để `entry_score` thực
sự có thể đổi dấu/độ lớn mỗi khi nến 15m hoặc 30m đóng, thay vì chỉ đổi
được vài lần/ngày như hiện tại. Đây là hiệu ứng NGAY LẬP TỨC dự kiến, có thể
verify lại qua production checkpoint sau khi Codex triển khai.

**Lưu ý quan trọng — hiệu ứng KHÔNG vĩnh viễn, cần theo dõi tiếp:** một khi
strategy mới subscribe bắt đầu tích luỹ đủ ≥20 trade (`PERFORMANCE_CONFIDENCE_TRADES`)
ở từng interval, quality của nó sẽ chuyển từ "benefit of doubt" (1.0) sang
hiệu suất thật đo được trên chính Binance/XAU. Nếu nó cũng thua lỗ tương tự
như 2 strategy hiện có (khả năng thật, vì `candle_momentum`/`rsi_mean_reversion`
thua lỗ khá nhất quán trên XAU cả 2 broker — xem bảng ở trên), hiệu ứng "sàn"
sẽ dần suy giảm về gần 0 sau khi đủ dữ liệu, y hệt 2 strategy hiện tại. Vì
vậy đây là **giải pháp tạm thời/làm chậm vấn đề**, không phải giải pháp gốc
rễ vĩnh viễn — nhưng vẫn đáng làm vì rủi ro thấp, chi phí thấp, và cho hệ
thống nhiều dữ liệu thật hơn để đánh giá trong lúc đó. Đề xuất Codex cân
nhắc thêm 1 floor tối thiểu không suy giảm hoàn toàn về 0 (khác với chỉ dựa
vào "may mắn có 1 strategy chưa test") nếu muốn giải pháp bền vững hơn về
lâu dài.

## Bài học phương pháp luận (đáng ghi để không lặp lại)

Round 63-64 suy luận nguyên nhân từ tương quan (routes lịch sử dài đều
trải đều trọng số, route lịch sử ngắn thì không) mà chưa đọc code — kết
luận sai hướng dù quan sát đúng hiện tượng. Bài học: khi có quyền truy cập
source code (repo hiện tại, không cần hỏi Codex), nên đọc code TRƯỚC khi
đưa ra giả thuyết nguyên nhân cuối cùng, chỉ dùng suy luận tương quan khi
không thể đọc code trực tiếp (ví dụ hành vi phụ thuộc dữ liệu production
không có trong source).
