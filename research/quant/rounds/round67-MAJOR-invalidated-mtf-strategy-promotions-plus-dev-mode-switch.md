# Round 67 (2026-08-21) — Codex hết quota lần 2, Claude chuyển sang researcher+dev+reviewer; phát hiện LỚN: 7 strategy MTF đang live được promote dựa trên backtest ĐÃ BỊ VÔ HIỆU HOÁ

Status: dev + research + review (vai trò mới, xem bối cảnh bên dưới). Code
change ĐÃ deploy (commit `fb9d955`, comment-only, không đổi runtime
behavior) + investigation đầy đủ cho quyết định KHÔNG xoá 7 strategy dù đã
xác nhận chúng thua lỗ.

## Bối cảnh: Codex hết quota lần 2, Claude nhận toàn bộ 3 vai trò

User xác nhận (2026-08-21): "codex lại hết quota rồi, bạn xử lí tiếp hết
nhé, giờ bạn vừa researcher vừa dev vừa review luôn nhé, 3 agent khác nhau".
Từ round này, Claude KHÔNG còn chỉ log task cho Codex — tự implement, test,
commit, push, theo dõi CI, deploy, verify production, cho tới khi Codex có
quota trở lại (không có ngày hẹn trước lần này, khác lần outage đầu
2026-08-15→20).

## Phát hiện: đọc `deployment_rules.rs` trước khi implement fix Round 65-66 — lộ ra vấn đề lớn hơn nhiều

Định implement đề xuất Round 65-66 (subscribe thêm 1 strategy cho
Binance/XAU, ví dụ `mtf_stochastic_5m_4h_sma5` giống Exness/XAU). Trước khi
sửa, đọc `crates/finance-api/src/deployment_rules.rs` để hiểu cách wiring
subscription — phát hiện:

1. File có 7 "extra" strategy MTF được promote (3 cho Binance/BTC, 2 cho
   Exness/BTC, 1 cho Exness/XAU — Binance/XAU KHÔNG có extra nào, khớp
   Round 65's phát hiện).
2. Comment trong code claim các số liệu cực tốt: PF 19.6-26.6, win rate
   80-85%, Sharpe 11-12, Sortino 60-196 — HOÀN TOÀN trái ngược với mọi số
   liệu mà chương trình research này (Round 1-66) tìm được (Sharpe -6.73
   production thật, PF<1 mọi nơi).
3. Lý do: `finance-mw/research/quant/studies/portfolio-btc-optimization-log.md` (file đã bị
   sửa từ đầu session, "M" trong git status) ghi lại 1 phiên nghiên cứu
   TRƯỚC (2026-08-19/20, khác thread với chương trình Round 1-66 hiện tại)
   đã tìm ra và fix 1 **lookahead bug nghiêm trọng khác** trong
   `finance-research`: merge klines đa-timeframe sort theo `open_time` thay
   vì `close_time`, khiến nến higher-timeframe "biết trước" outcome vài
   giờ tới 1 ngày trước khi thực tế đóng nến — root-cause tại commit
   `d3b0586`, fix tại commit `3c16745` (2026-08-20T09:15Z UTC).

## Bảng re-validation gốc (đã có sẵn trong log, không phải tôi tự làm)

| Strategy | Instrument | Win (buggy→fixed) | PF (buggy→fixed) |
|---|---|---|---|
| stochastic (k=9) | Binance BTC | 85.2%→27.3% | 19.59→0.68 |
| MACD (5/13/5) | Binance BTC | 82.6%→27.8% | 20.02→0.64 |
| candle_momentum | Binance BTC | 81.1%→29.8% | 26.56→0.75 |
| stochastic (k=9) | Exness BTC | 84.5%→26.5% | 19.95→0.67 |
| MACD (5/13/5) | Exness BTC | 83.8%→27.0% | 21.14→0.65 |
| candle_momentum | Exness BTC | 81.7%→29.9% | 24.67→0.74 |

## Phần tôi tự làm: re-validate strategy thứ 7 (Exness XAU) còn thiếu trong bảng trên

`git log` xác nhận `deployment_rules.rs` KHÔNG được sửa từ sau commit
`f143c44` (2026-08-20 00:30 UTC) — TRƯỚC cả thời điểm fix bug lookahead
(09:15Z cùng ngày). Nghĩa là **không ai quay lại re-validate hay sửa file
này sau khi bug được fix** — cả 7 strategy vẫn live dựa trên promotion đã
bị vô hiệu hoá.

Chạy lại đúng candidate khớp production (`mtf_stochastic_9_3_35_65_sma5_trend_filtered`,
k=9/d=3/oversold=35/overbought=65/sma5 — khớp chính xác
`mtf_stochastic_5m_4h_sma5` đang live) qua Docker (`finance-research-local`,
`--cpus=2`), window 5 năm, Exness XAU/USD 5m:

| Split | Trades | Win rate | PF |
|---|---|---|---|
| Train | 1247 | 24.9% | **0.584** |
| Validation | 404 | 26.5% | **0.643** |
| Holdout | 385 | 30.4% | **0.98** |

So với comment code claim "holdout 394 trades, 79.4% win, PF 13.06, Sharpe
11.09, Sortino 97.89" — hoàn toàn khác biệt, khớp đúng pattern collapse của
bảng trên. **Xác nhận đủ cả 7/7 strategy: tất cả đều thua lỗ hoặc hoà vốn
dưới validation trung thực, không phải edge mạnh như comment claim.**

## Cân nhắc xoá 7 strategy này — mô phỏng trước khi hành động, PHÁT HIỆN RỦI RO LỚN

Định xoá cả 7 (đúng logic: strategy thua lỗ xác nhận thì không nên giữ).
Trước khi sửa code, mô phỏng ảnh hưởng lên `interval_weights` (dùng đúng
công thức đã verify Round 65) bằng cách loại bỏ toàn bộ strategy `mtf_*`
khỏi dữ liệu performance thật của Binance/BTC và Exness/BTC:

| Route | Còn cả 5 strategy (hiện tại) | Chỉ còn 2 strategy base (mô phỏng xoá) |
|---|---|---|
| Binance/BTC | mọi interval (trừ 5m) đều >0 | **15m/1h/2h/30m/4h/5m → 0, chỉ 12h/1d còn >0** |
| Exness/BTC | mọi interval (trừ 5m) đều >0 | **15m/1h/2h/30m/5m → 0, chỉ 12h/1d/4h còn >0** |

**Xoá 7 strategy này sẽ làm CẢ 2 leg BTC sụp đổ `interval_weights` giống
hệt Binance/XAU hiện tại** — vì cơ chế "benefit of doubt" (Round 65:
`trade_count=0` tại 1 role-interval → quality=1.0) đang được 3 strategy MTF
này (dù đã bị confirm thua lỗ, `strategy_weight` thực tế đã ~0.0 trong
production) vô tình "gánh" nhờ CHƯA tích luỹ đủ 20 evaluation ở nhiều
role-interval slot. Data thật (checkpoint production, đọc trực tiếp) xác
nhận: `strategy_weights` của Binance/BTC hiện tại đã có
`mtf_stochastic_5m_4h_sma10: 0.0, mtf_macd_5m_4h_sma10: 0.0,
mtf_candle_momentum_5m_4h_sma10: 0.0` — hệ thống ĐÃ tự nhận ra 3 strategy
này vô dụng qua đúng cơ chế reweight, nhưng chúng vẫn "hữu ích" 1 cách tình
cờ cho việc giữ interval_weights không sụp đổ.

## Quyết định: KHÔNG xoá — chỉ sửa comment, giữ nguyên runtime behavior

Đánh đổi ở đây rõ ràng: xoá 7 strategy sẽ fix "nợ kỹ thuật" (comment sai sự
thật) nhưng phá vỡ Target 2 của BTC (instrument quan trọng nhất) để đổi lấy
Target 1 code-cleanliness — **không phải trade-off an toàn**, đặc biệt khi
Target 1 (lợi nhuận) được liệt kê ưu tiên số 1 trong đề bài nhưng bản thân
việc xoá 7 strategy này KHÔNG cải thiện Target 1 (chúng đã ở strategy_weight
≈0, gần như không ảnh hưởng quyết định thật) — chỉ có RỦI RO làm xấu đi
Target 2. Đây là quyết định "không hành động" có cân nhắc, không phải bỏ
qua.

**Đã làm:** thêm 1 comment correction dài, rõ ràng, có dẫn chứng đầy đủ
ngay phía trên `configured_extra_strategies()` trong
`crates/finance-api/src/deployment_rules.rs` — giải thích rõ 7 comment bên
dưới đã lỗi thời/vô hiệu, dẫn chứng số liệu thật, và giải thích TẠI SAO cố
tình chưa xoá (rủi ro Target 2 cho BTC). Không đổi behavior runtime nào —
build + `cargo test -p finance-api deployment_rules` (8/8 pass) +
`cargo fmt --check` đều sạch trước khi commit.

**Commit:** `fb9d955` "docs(deployment): flag invalidated MTF strategy
promotion rationale" — pushed lên `main`, CI đang chạy (workflow
`32476493251`).

## Ý nghĩa lớn hơn: kiến trúc hiện tại có mâu thuẫn Target 1 vs Target 2 chưa giải quyết

Đây không phải bug đơn giản mà là 1 căng thẳng kiến trúc thật: cơ chế
`reweight_from_alpha_performance` đang "vô tình" giữ tần suất quyết định
của BTC ổn nhờ có NHIỀU strategy configured (kể cả loser đã confirm), trong
khi Binance/XAU chỉ có 2 strategy (cũng loser) nên sụp hẳn. Giải pháp bền
vững thật sự cần 1 trong 2:
1. Tìm được strategy THẬT SỰ có lời + tần suất cao (mục tiêu cả chương
   trình 66 round trước chưa đạt được) để thay thế zombie strategies.
2. Sửa `reweight_from_alpha_performance`/`alpha_performance_quality` để có
   floor tối thiểu CÓ CHỦ ĐÍCH (không phụ thuộc số lượng strategy configured
   tình cờ), cân nhắc kỹ đánh đổi Target 1 vs Target 2 khi thiết kế floor
   (floor cao quá sẽ để tín hiệu đã confirm thua lỗ tiếp tục ảnh hưởng
   quyết định, ngược lại mục đích ban đầu của công thức).

Không implement hướng 2 ngay round này — cần thiết kế cẩn thận hơn (mức
floor bao nhiêu, áp dụng cho tất cả interval hay chỉ role "entry", v.v.)
trước khi động vào core decision algorithm dùng chung cho toàn bộ 4 route
production. Ghi lại làm ưu tiên cao cho round sau.

## Không xoá đề xuất Round 65-66 (subscribe thêm strategy cho Binance/XAU)

Đề xuất cũ (subscribe `mtf_stochastic_5m_4h_sma5` cho Binance/XAU) giờ cần
đánh giá lại dưới ánh sáng phát hiện này: bản thân `mtf_stochastic_5m_4h_sma5`
ĐÃ ĐƯỢC XÁC NHẬN THUA LỖ (bảng trên) — subscribe thêm 1 strategy ĐÃ BIẾT THUA
LỖ chỉ để lợi dụng hiệu ứng "benefit of doubt" tạm thời là cùng 1 kiểu vá
"zombie strategy" y hệt vấn đề vừa phát hiện ở BTC, không phải giải pháp
sạch. **Rút lại đề xuất này** — không nên áp dụng, dù rủi ro thấp về mặt kỹ
thuật, vì nó lặp lại đúng anti-pattern vừa phát hiện và ghi rõ trong comment
correction ở trên ("do not add more zombie strategies to XAU").
