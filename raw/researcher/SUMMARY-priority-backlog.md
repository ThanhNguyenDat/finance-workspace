# Tổng hợp ưu tiên — chương trình Quant Research `/loop` (Round 1-55, tính tới 2026-08-21)

Status: tài liệu điều hướng, không phải phát hiện mới. Viết lần đầu ở Round
39, cập nhật lại toàn bộ ở Round 50 (mốc 50 vòng) và bổ sung Round 54-55
(THAY ĐỔI LỚN NHẤT từ trước tới giờ — xem mục 0). Cập nhật lại tài liệu này
thay vì tạo mới mỗi khi có thay đổi lớn về ưu tiên.

## 0. QUAN TRỌNG NHẤT — đọc mục này trước tiên (Round 54-55)

- **Round 54:** Codex fix xong gap phương pháp luận Round 20
  (`finance-research` giờ chạy qua `PortfolioDecisionPolicy` THẬT). Toàn bộ
  ensemble Round 36-38/51-54 bị **phủ định hoàn toàn** khi test qua engine
  thật (Sharpe -6.72 thay vì 1.8 backtest tay) — đóng hẳn hướng ensemble
  kiểu backtest-tay-cộng-dồn-PnL.
- **Round 55: `--gate-strategy` đã bị XOÁ khỏi CLI.** Không còn cách test
  extended metrics (Sharpe/Sortino/streak) cho 1 candidate tuỳ ý như Round
  17-53 đã làm suốt. `--daily-profit-gate` giờ chỉ đánh giá đúng Portfolio
  **production thật đang live** (không chọn candidate được nữa).
  `--weighted-ensemble-gate` hardcode đúng 1 tổ hợp (Round 54's). Sweep
  table PF/win-rate thường (không gate) vẫn hoạt động bình thường, số liệu
  Round 17-53's PF/win-rate table vẫn đáng tin.
- **Số liệu thẩm quyền nhất từ trước tới giờ (Round 55, qua engine đúng):**
  BTC/binance production Sharpe **-6.73**, Sortino -6.69, net PnL holdout
  -$13.39 (Target 1 KHÔNG đạt, rõ ràng). XAU/binance: observed_days chỉ
  51/366, positive_day_ratio 0% (Target 2 vẫn stagnant, khớp Round 23/40/48).
- File: `round54-CORRECTION-*.md`, `round55-real-production-gate-and-tool-overhaul.md`.
- **Round 80 (2026-08-21) — LẦN ĐẦU TIÊN sau 80 round tìm được lever THẬT cải
  thiện Target 1, ĐÃ TRIỂN KHAI production:** không phải signal mới — 1 tham
  số Portfolio-construction (`--portfolio-minimum-hold-decisions`, số chu kỳ
  quyết định phải chờ trước khi được đảo chiều vị thế). Backtest thật cho
  quan hệ đơn điệu rõ ràng: hold càng dài → ít trade hơn nhưng lỗ ít hơn (do
  Alpha hiện tại không đủ edge để đảo chiều thường xuyên sinh lời, mỗi lần
  đảo chỉ trả thêm phí). Cross-broker khớp gần như y hệt (<1% chênh lệch,
  mức nhất quán cao nhất từng thấy), confirm trên window 18 tháng độc lập
  cùng hướng. **Đã nâng `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS` từ 12 (1
  giờ) lên 36 (3 giờ)** — giảm ~34% lỗ đo được (-43.68→-28.71 tại BTC/binance
  5 năm). Con số tần suất ~15/tuần lúc đó chỉ đúng trước lever stop/take
  Round 83; cấu hình kết hợp production hiện đạt ~9.3/tuần trên 5 năm và
  ~7.2-7.3/tuần trên 18 tháng, nên margin Target 3 hiện mỏng (Round 92).
  Commit `efe7854`, đã build/test/deploy đầy đủ. **Lưu ý quan
  trọng: KHÔNG biến lỗ thành lời** — PF các strategy vẫn <1 mọi giá trị hold
  test được, chỉ làm hệ thống thua lỗ chậm hơn/rẻ hơn. File:
  `round80-portfolio-minimum-hold-decisions-raised-12-to-36.md`.
- **Round 81-82 (2026-08-21) — Lead ATR-stop tưởng là đòn bẩy thứ 2, hoá ra
  đo sai công cụ, đã đóng đúng cách:** `capital_reports` (nhánh đo cũ) không
  hề tôn trọng `minimum_hold_decisions` — verify bằng code + thực nghiệm.
  Đo lại đúng qua `one_target`: ATR-stop cải thiện trên Binance nhưng TỆ HƠN
  trên Exness (fail cross-broker rõ ràng). Đóng. Bài học: chỉ tin `one_target`
  cho mọi kết luận Portfolio-construction từ nay. File:
  `round81-*.md`, `round82-atr-stop-resolved-and-closed-cross-broker-fail.md`.
- **Round 83 (2026-08-21) — Đòn bẩy Target 1 thật THỨ 2, ĐÃ TRIỂN KHAI:** áp
  đúng phương pháp `one_target` (đã xác nhận đáng tin ở Round 82) cho
  `--portfolio-stop-value`/`--portfolio-take-value`. Cùng cơ chế Round 80:
  stop hẹp dễ bị nhiễu quét oan, nới rộng giảm lỗ. Cross-broker khớp <2%.
  **Đã nới `PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE` từ 0.005/0.010 lên
  0.01/0.02** — giảm ~41% lỗ (Binance) / ~32% (Exness), giữ ~9.3/tuần (trên
  ngưỡng Target 3). Commit `31ed149`, build/test/deploy đầy đủ. Vẫn KHÔNG
  biến lỗ thành lời. File:
  `round83-portfolio-stop-take-widened-second-real-lever.md`.
- **Round 67 (2026-08-21) — Codex hết quota lần 2 (không hẹn ngày), Claude
  chuyển sang researcher+dev+reviewer (tự implement/commit/push/deploy/verify,
  xem memory `feedback_deploy_ownership`).** Phát hiện lớn: **7 strategy MTF
  đang live** (`deployment_rules.rs`, 3 Binance/BTC + 2 Exness/BTC + 1
  Exness/XAU) đều được promote dựa trên backtest bị vô hiệu hoá bởi 1
  lookahead bug KHÁC (merge kline đa-timeframe, sort sai `open_time` thay vì
  `close_time`, fix commit `3c16745` lúc 2026-08-20T09:15Z — 1 thread nghiên
  cứu khác, trước cả chương trình Round 1-66 hiện tại, ghi trong
  `finance-mw/raw/portfolio-btc-optimization-log.md`). Re-validate cả 7: PF
  collapse từ 19.6-26.6 xuống 0.58-0.98 — tất cả thua lỗ/hoà vốn thật.
  `deployment_rules.rs` chưa hề được sửa từ sau bug fix. **Mô phỏng xoá cả 7
  cho thấy sẽ làm sụp `interval_weights` của CẢ 2 leg BTC** giống hệt
  Binance/XAU hiện tại (chúng vô tình giữ tần suất BTC nhờ cơ chế
  benefit-of-doubt của `reweight_from_alpha_performance`, dù bản thân đã
  ~0 weight thật). Quyết định KHÔNG xoá — chỉ sửa comment cho đúng sự thật
  (commit `fb9d955`), rút lại đề xuất Round 65-66 (subscribe thêm strategy
  cho Binance/XAU — chính nó cũng đã confirm thua lỗ). Vấn đề kiến trúc
  Target 1 vs Target 2 vẫn CHƯA giải quyết, cần floor có chủ đích hoặc
  strategy thật sự lời+tần suất cao. File:
  `round67-MAJOR-invalidated-mtf-strategy-promotions-plus-dev-mode-switch.md`.
- **Round 68 (2026-08-21) — ĐÓNG debate floor dứt điểm:** đọc doc-comment
  gốc trên `reweight_from_alpha_performance` — zero-out mature-losing
  strategy là THIẾT KẾ CÓ CHỦ Ý ("instead of diluting the demonstrated
  signal"), không phải thiếu sót. **Không nên thêm floor** — Target 2 của
  XAU/binance chỉ giải được bằng cách tìm strategy thật sự có edge, không
  phải kỹ thuật trọng số. Fix riêng 1 lỗ hổng robustness khác (không liên
  quan floor debate): `interval_weights` thiếu fallback uniform-khi-tổng-0
  mà `strategy_weights` đã có sẵn — nếu KHÔNG fix, khi tất cả interval của 1
  route đều "mature+confirm thua lỗ" cùng lúc, route đó đóng băng **vĩnh
  viễn** (Binance/XAU đã 5/8 interval trong trạng thái này). Đã fix + test +
  commit `cc0c8ac` + push, CI đang chạy. Không đổi hành vi hiện tại (chưa
  trigger). File: `round68-interval-weight-freeze-fix-plus-design-intent-confirmation.md`.

- **Round 85 (2026-08-22) — 2 phát hiện: Live Action production HOÀN TOÀN
  down (không phải suy giảm) + `risk_fraction` sizing vẫn bị Risk gate từ
  chối gần hết dù đã có fix Round 84:** verify độc lập xác nhận 0 container
  `live-action-*` trên host, Finance MW lỗi DNS `no such host` cho cả 4 route
  — đã log Processing (Codex đang tự fix, xem entry `[trading][risk]` phần
  Processing), KHÔNG cần round sau lặp lại việc này, chỉ cần verify kết quả.
  Test `risk_fraction=0.02` (rule `risk-2pct` LIVE) qua `one_target` đã fix
  Round 84: 3/4 route bị risk-gate từ chối 99.6-99.8% quyết định (chỉ 1-2
  trade/năm), khác hẳn `equity_fraction` (0% rejected, Round 84). XAU/binance
  là ngoại lệ 0%-rejected chưa giải thích được (cùng leverage 10x với
  BTC/binance nhưng kết quả trái ngược hoàn toàn). Root cause CHƯA xác định —
  cần đọc code risk-gate re-evaluation path, không suy đoán tiếp bằng tay.
  Nếu cơ chế này áp cho ledger thật, rule `risk-2pct` có thể gần như không
  bao giờ trade trên production — chưa verify được vì Live Action đang down.
  File: `round85-risk-fraction-still-rejected-plus-live-action-full-outage.md`.

- **Round 86 (2026-08-22) — R:R ratio (1:2→1:3) ĐÓNG, đảo dấu trên window độc
  lập:** Codex tự fix xong Round 85's `risk_fraction` bug (`6eebf76` — cap
  đóng băng ở starting equity + research mislabel leverage 1x cho perpetual,
  cả 2 đều đã fix) trước round này. Test tỉ lệ R:R (khác Round 80/83 vốn chỉ
  đổi ĐỘ RỘNG tuyệt đối, giữ tỉ lệ 1:2): 5 năm cho 1:3 thắng rõ cả 2 broker
  BTC (~-24-25%), nhưng 18 tháng độc lập ĐẢO NGƯỢC hoàn toàn cả 2 broker —
  đóng, giữ nguyên 1:2 hiện tại. File: `round86-rr-ratio-widening-reverses-on-independent-window-closed.md`.

- **Round 87 (2026-08-22) — Đóng câu hỏi mở "hold×stop/take có cộng dồn
  tuyến tính?":** factorial 2×2 trên BTC cả 2 broker (5 năm): tổ hợp cả 2
  lever (= production hiện tại) chỉ đạt 56-62% mức cải thiện mà phép cộng
  tuyến tính dự đoán (83-84%) — tương tác sub-additive nhất quán 2 broker,
  nhưng vẫn là tổ hợp tốt nhất trong 4 tổ hợp test được, KHÔNG đổi gì. Bài
  học phương pháp luận: lever mới trong tương lai phải test lại TỔ HỢP ĐẦY
  ĐỦ, không giả định cộng dồn tuyến tính với lever đã có. Đầu round cũng đã
  đóng 3 mục Verify trading sang Done (Live Action outage recovery,
  `risk_fraction` fix, risk-policy sync) sau khi verify độc lập qua SSH —
  `risk-2pct` giờ trade khớp `fixed-pct` trên cả 4 route production thật.
  File: `round87-hold-stoptake-interaction-sub-additive-confirmed.md`.

- **Round 88 (2026-08-22) — Donchian Channel breakout (Turtle Trading), cơ
  chế MỚI đầu tiên test sau nhiều round tập trung Rule 1 — ĐÓNG:** 4 period
  (20/55/100/200). BTC cả 2 broker: PF plateau <1 (đỉnh 0.81-0.82), cross-
  broker khớp nhau. XAU: có PF>1 ở vài split nhưng theo hướng NGƯỢC NHAU giữa
  2 broker (binance mạnh-train/yếu-holdout, exness yếu-train/mạnh-holdout) —
  dấu hiệu overfit kinh điển, không phải edge thật. Đóng, không promote. Code
  giữ lại `strategies.rs` (uncommitted, chờ Codex review/commit làm bản ghi).
  File: `round88-donchian-channel-breakout-new-mechanism-closed.md`.

- **Round 89 (2026-08-22) — `risk_fraction` sizing (rule `risk-2pct`) mất
  98-99.9% vốn mô phỏng do đòn bẩy hiệu dụng ẩn (`notional =
  equity×risk_fraction/stop = 2× equity`), lever stop/take Round 83 gần như
  vô dụng cho rule này (0.05-1.5% cải thiện thay vì 33-43% như
  `fixed_notional`):** không phải bug — hệ quả toán học của tỷ lệ
  `risk_fraction/stop=2` hiện tại trên Alpha có PF<1. Ledger mô phỏng
  (`simulated_child`, không phải vốn thật qua broker), không cấp bách,
  nhưng nên hạ `sizing_value` nếu muốn rule này so sánh được với
  `compounding-10pct` (đòn bẩy hiệu dụng chỉ ~0.1x). File:
  `round89-risk-fraction-effective-leverage-catastrophic-loss.md`.

- **Round 90 (2026-08-22) — xác nhận toán học `risk_fraction ≡ equity_fraction`
  tại cùng đòn bẩy (khớp tới cent), lỗ scale PHI TUYẾN (compounding hình
  học) theo đòn bẩy, và sửa lại 1 so sánh sai ở Round 85/88:** đòn bẩy 0.1x
  → lỗ -28%/-32% (không phải ~5% như dự đoán tuyến tính) — gấp ~5.6 lần.
  Con số "-663/-6.6%" của `compounding-10pct` trích dẫn trước đó là mẫu
  ledger production NGẮN (502 trade từ lúc restart), không phải kỳ vọng dài
  hạn — số 5 năm honest thực ra là -28-32%, gần bằng mức độ nghiêm trọng của
  `risk-2pct` (-99%), chỉ khác về MỨC ĐỘ đòn bẩy, không khác LOẠI rủi ro.
  Kết luận tổng quát: mọi sizing mode compounding-theo-equity đều nguy hiểm
  với Alpha PF<1 hiện tại; chỉ `fixed_notional` (rule `fixed-pct` đang
  "selected" thật) không compounding, giữ lỗ tuyến tính bounded (-0.03%).
  File: `round90-equity-compounding-sizing-geometric-decay-confirmed.md`.

- **Round 91 (2026-08-22) — Keltner Channel reversion, cơ chế MỚI thứ 2 (sau
  Donchian Round 88) — ĐÓNG:** 3 multiplier (1.5/2.0/2.5), toàn bộ 12 ô
  (3 tham số × 4 route) PF<1 cả 3 split, không đảo chiều/overfit — kết luận
  sạch, cùng hướng `bollinger_reversion` (đã đóng Round 24) dù đổi cả midline
  (EMA thay SMA) lẫn thước đo biến động (ATR thay std-dev). Code chung file
  uncommitted với Donchian, chờ Codex review 1 lần cho cả 2. File:
  `round91-keltner-channel-reversion-closed.md`.

- **Round 92 (2026-08-22) — ĐÓNG "kéo dài hold thêm", và SỬA LẠI tuyên bố
  "margin Target 3 lớn" của Round 80 (đã lỗi thời sau Round 83):** tự phát
  hiện + sửa 1 lỗi tính tần suất/tuần giữa round (chia sai số tuần cho cửa
  sổ 5 năm). Sau khi sửa: cấu hình production hiện tại (hold=36 +
  stop/take=0.01/0.02, CẢ 2 lever cộng dồn) chỉ đạt ~9.3/tuần (5 năm)
  /~7.2-7.3/tuần (18 tháng) — không phải "~15/tuần dư margin lớn" như Round
  80 ghi (số đó đo TRƯỚC Round 83). hold=72 đã DƯỚI ngưỡng 7/tuần trên cửa
  sổ 18 tháng gần đây; hold=100 dưới ngưỡng cả trên 5 năm. Không còn dư địa
  tăng hold — đóng hướng này, KHÔNG đổi `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS`.
  Đã thêm banner CẢNH BÁO vào file Round 80 gốc. **Bài học cho tương lai:
  margin Target 3 hiện đã mỏng, mọi lever mới làm giảm tần suất thêm phải
  kiểm tra kỹ trước khi triển khai.** File:
  `round92-hold-extension-closed-target3-margin-thinner-than-documented.md`.

- **Round 93 (2026-08-22) — Heikin-Ashi momentum (cơ chế mới thứ 3) ĐÓNG, và
  phát hiện "trần chi phí cấu trúc" nghi ngờ chung cho cả bộ chỉ báo kỹ
  thuật:** PF<1 toàn bộ 16 ô. **Quan trọng: cả 3 cơ chế mới thử trong phiên
  này (Donchian Round 88, Keltner Round 91, Heikin-Ashi Round 93) — hoàn
  toàn khác nhau về bản chất — đều hội tụ về cùng vùng PF ~0.65-0.85 trên BTC
  khi kéo dài tham số (giảm tần suất), không bao giờ vượt 1.** Giả thuyết
  hợp lý nhất: đây là trần chi phí cố định (fee+slippage+spread mỗi lệnh)
  chứ không phải điểm yếu riêng từng indicator — củng cố định lượng cho kết
  luận "không gian chỉ báo kỹ thuật chuẩn gần cạn ở 5m" đã ghi trước đây.
  **Gợi ý cho round sau:** nếu tiếp tục Rule 2/3, ưu tiên tìm cơ chế dùng
  nguồn thông tin THỰC SỰ khác OHLCV (đã thử volume/order-flow, đóng ở Round
  72-75) thay vì thêm biến thể breakout/reversion/momentum mới — khả năng
  vượt trần chỉ bằng công thức tín hiệu khác là thấp dựa trên bằng chứng
  này. File: `round93-heikin-ashi-momentum-closed-plus-plateau-ceiling-pattern.md`.

- **Round 94 (2026-08-22) — Thử trend-filter (giả thuyết Round 33) lên
  Keltner reversion + Donchian breakout đã đóng — ĐÓNG cả 2:** Keltner không
  được cứu (PF<1 mọi route). Donchian+trend-filter suýt hứa hẹn nhất chương
  trình gần đây — PF~1.0 rất nhất quán trên validation+holdout cả BTC 2
  broker ở window 5 năm — nhưng ĐẢO NGƯỢC HÌNH DẠNG HOÀN TOÀN trên cửa sổ 18
  tháng độc lập (train cao 1.18-1.30, validation/holdout thấp 0.70-0.90,
  ngược hẳn 5 năm) — false-positive kinh điển, đóng đúng quy trình bắt buộc
  cross-validate trước khi tin. File:
  `round94-trend-filter-on-closed-mean-reversion-breakout-still-closed.md`.

- **Round 95 (2026-08-23) — Vòng verify: đóng 6 mục Verify, xác nhận Codex
  sửa đúng 1 điểm trong Round 89, và fix 1 rủi ro git-divergence thật:**
  Codex đúng khi sửa lại mô tả đòn bẩy `risk_fraction` — chỉ Binance đạt
  đúng 2x (cap 10x không chạm), Exness CFD bị cap xuống 1x (stop-budget
  thực 1% không phải 2%) — accept correction, không đổi kết luận chính
  Round 89/90. **Quan trọng hơn:** phát hiện checkout local
  `finance-live-action` lệch 3 commit khỏi `origin/main` (Codex đã push
  Donchian/Keltner sạch trong lúc tôi vẫn giữ working tree cũ trùng lặp) —
  đã fix an toàn bằng backup+fast-forward+khôi phục, không mất dữ liệu, xác
  nhận lại 92/92 test xanh. **Bài học quy trình: phải `git fetch` + so sánh
  HEAD với origin/main mỗi đầu round, không chỉ occasionally — diff để lâu
  dễ trùng lặp/conflict với commit thật của Codex.** File:
  `round95-verification-round-and-git-divergence-fix.md`.

- **Round 96 (2026-08-23) — Ablation không chi phí xác nhận phần lớn giả
  thuyết "trần chi phí cấu trúc" Round 93, phân loại cost-limited vs
  edge-limited:** `--fee-bps 0 --slippage-bps 0` cho 3 candidate tốt nhất.
  `keltner_reversion_20_2_5`/`heikin_ashi_momentum_10` chạm gần đúng PF≈1.0
  (cost-limited, raw edge ≈0) — chi phí giao dịch là nguyên nhân chính khiến
  chúng <1 khi có phí. `donchian_breakout_200` vẫn <1 (0.96) dù bỏ hết chi
  phí (edge-limited, có edge âm thật nhỏ). Không candidate nào promote được
  nhưng lần đầu tách bạch được 2 loại nguyên nhân "PF<1" khác nhau. File:
  `round96-cost-ablation-confirms-structural-ceiling-hypothesis.md`.

- **Round 98 (2026-08-23) — Hoàn thiện ablation XAU (Round 96 chỉ BTC):**
  cùng hướng cost-driven, vài ô vượt 1 (donchian XAU/exness 1.36, keltner
  XAU/binance 1.08, heikin_ashi XAU/exness 1.10) nhưng KHÔNG đủ tin cậy để
  đổi kết luận CLOSED — XAU/binance mẫu mỏng (~85 ngày), XAU/exness có gap
  chưa verify, cả 2 lý do đã biết từ trước. File: `round98-cost-ablation-xau-completion.md`.

- **Round 99 (2026-08-23) — Lọc theo signal strength cho 2 candidate
  cost-limited — ĐÓNG, overfit mẫu mỏng:** Heikin-Ashi hứa hẹn rất lớn trên 5
  năm (holdout PF tới 1.90-2.98 ở strength≥0.7-0.9) nhưng SỤP ĐỔ trên 18
  tháng độc lập (holdout 0.22-0.28 dù validation vọt 3.38-4.56, n=9-25/split
  — quá mỏng). Đóng đúng kỷ luật false-positive-shape đã áp dụng xuyên suốt
  chương trình. Phát hiện phụ: strength field của Keltner vô dụng (luôn
  ≥0.9, filter không có tác dụng gì ở mọi ngưỡng). File:
  `round99-strength-filter-closed-thin-sample-overfit.md`.

- **Round 100 (2026-08-23) — Tự phát hiện + sửa lỗi trùng tên label
  (đụng regression test Codex):** đồng bộ working tree với `9c1fbb3`, phát
  hiện 6 label Round 99 trùng prefix với 2 test khoá grid Round 91/93 của
  Codex. Đổi tên (không đụng test Codex), 93/93 test xanh trở lại. Không có
  backtest mới.

- **Round 101 (2026-08-23) — `--alpha-stop-value`/`take-value` cho 3
  candidate mới — không tìm được lever, mở rộng kết luận đóng Round 25/59:**
  hiệu ứng nhỏ/trái chiều (Donchian cải thiện nhẹ, Keltner tệ hơn nhẹ,
  Heikin-Ashi trung tính), khác hẳn hiệu ứng mạnh nhất quán của stop/take ở
  Portfolio layer (Round 83). Xác nhận đòn bẩy stop/take thật chỉ nằm ở tầng
  Portfolio-construction, không phải Alpha riêng lẻ — đúng cho cả 5 cơ chế
  đã test (2 cũ + 3 mới). File:
  `round101-alpha-level-stop-take-no-lever-for-new-candidates.md`.

- **Round 102 (2026-08-23) — Kiểm tra sức khỏe production, false alarm
  XAU/Exness được điều tra và bác bỏ:** 3/4 route tiến triển bình thường
  (khớp đúng ~9.3/tuần đã xác nhận Round 92). XAU/exness's checkpoint đóng
  băng ban đầu nghi là bug (updated_at sớm hơn cả StartedAt container) nhưng
  điều tra ra đúng market-closed cuối tuần (2026-08-22 là thứ Bảy) — khớp
  semantics đã biết, không phải bug mới. File:
  `round102-production-health-check-xau-weekend-false-alarm-resolved.md`.

- **Round 120 (2026-08-23) — Bug production THẬT thứ 3 của chuỗi Bybit,
  đang OPEN, khác 2 bug trước (leverage + XAUT ingest cũ đều đã đóng):**
  leverage fix `41bde83` và web `.sort()` xác nhận deploy/chạy thật (CI +
  Production Trading/Web Verification xanh, code review trực tiếp). Nhưng
  đào sâu hơn "container healthy" bằng cách so `recent_klines` timestamp
  với wall clock: cả 2 route Bybit (`bybit.perpetual_future.btc.usdt.5m`,
  `bybit.spot.xaut.usdt.5m`) đứng yên ở bar `06:00-06:04:59Z` suốt 3 lần đọc
  trải ~4 phút trong khi `evaluation_count` vẫn tăng đều — worker "sống"
  nhưng không nhận dữ liệu `5m` mới (interval Portfolio dùng làm base) dù
  mọi health check bề mặt xanh. Root cause tìm trong `finance-kline-ingest-1`
  (producer riêng, không phải `finance-mw-1`): WS receiver Bybit crash-loop
  vì `normalizeBybitKlineEvent` (`internal/services/bybit_ws_service.go:285-288`)
  reject cứng bất kỳ push nào có `len(payload.Data) != 1`, trong khi Bybit
  không đảm bảo luôn gửi đúng 1 record/push — reject đó làm sập cả kết nối
  WS của TOÀN BỘ interval trên socket đó, không chỉ record lỗi. Config/wiring
  đã xác nhận đúng (không phải nguyên nhân). Task log ở đầu `## Todo` trong
  `raw/handoff_agent.md`, chi tiết đầy đủ →
  `raw/explain/bybit-5m-kline-ws-crash-loop.md`.

- **Round 121 (2026-08-23) — Codex hết quota giữa round, Claude tự
  implement/deploy fix cho bug Round 120 (Rule 0b):** `normalizeBybitKlineEvent`
  → `normalizeBybitKlineEvents`, xử lý mọi record thay vì reject cứng;
  `EventID` đổi key sang `item.Start` (per-record) tránh trùng ID. Local
  verify Docker CPU-capped (build/test/vet/fmt toàn workspace xanh), commit
  `60e16bab92ad42dfca1f2ac3cf6ea3f7b9325e27`, CI `32625351026` toàn bộ job
  xanh, SHA khớp production qua `/api/v1/system/version`. **Root cause xác
  nhận đã sửa** — `finance-kline-ingest-1` hết crash-loop hoàn toàn (>20
  phút quan sát, 0 lỗi, trước đó crash mỗi ~2s). Side-effect phát hiện thêm:
  MW deploy làm gRPC bị hủy giữa chừng → trigger fail-closed panic đã biết
  (`finance-api/src/main.rs:1274`, không phải bug mới) → Bybit BTC worker
  tự restart → đang chạy historical-replay backfill qua 8 interval, CHƯA
  chạm `5m` tại thời điểm kết thúc round (checkpoint vẫn đứng `06:00Z`).
  Không phải bug — khối lượng backfill lớn, không lỗi. **Chưa đóng hẳn
  task** — round sau re-check catch-up. File:
  `round121-bybit-kline-crash-loop-self-fixed.md`.

- **Round 122 (2026-08-23) — Vortex Indicator (candidate mới, code+test xong
  nhưng KHÔNG có backtest thật) + tìm ra nguyên nhân gốc backfill Bybit chậm:**
  thêm `VortexIndicatorStrategy` (VI+/VI- crossover, cơ chế trend-direction
  mới — đo lệch mỗi nến so với extremum đối diện nến trước, chuẩn hoá qua
  true range) và indicator `vortex` dùng chung, 5 unit test xanh, build/fmt
  Docker CPU-capped sạch. Thử chạy backtest 5 năm thật thì `finance-research`
  CLI treo `DeadlineExceeded` — điều tra bằng `grpcurl` trực tiếp (loại trừ
  network/tunnel) xác nhận **`kline.KlineService.Stream` giới hạn cứng
  `defaultMaxConcurrentHistoryStreams=1`** (cố ý, memory-safety cgroup
  512MiB, `kline_service_server.go:28-51,99,262`) — đúng RPC mà 2 route
  Bybit đang backfill (Round 120/121) cũng dùng, nên đang chiếm slot duy
  nhất liên tục. **Giải thích trọn vẹn cả 2 hiện tượng**: Bybit backfill
  chậm bất thường (đang xếp hàng qua 1 cổng, không phải hệ thống yếu) VÀ
  backtest tool bị chặn hoàn toàn cho tới khi có slot rảnh. Không phải bug
  — thiết kế cố ý, không tự sửa giới hạn. Candidate Vortex chưa commit
  (giữ local, chờ backtest thật khi slot rảnh). File:
  `round122-vortex-indicator-blocked-by-kline-stream-concurrency-gate.md`.

- **Round 123 (2026-08-23) — XÁC NHẬN QUA CODE root cause thứ 2 khiến
  backfill Bybit gần như không hội tụ (tiếp nối Round 122):** đọc trực
  tiếp `finance-live-action/crates/finance-api/src/historical_replay.rs`
  + `main.rs:750-772` xác nhận: `bootstrap_pending_intervals` mở đồng thời
  tối đa 8 stream (1/interval) qua đúng RPC bị giới hạn 1-slot (Round 122);
  merge loop dùng `?` nên **1 stream lỗi huỷ NGAY toàn bộ 8-interval
  batch**; vòng retry ngoài (`main.rs`) gọi lại từ `from_time` cố định
  (không phải watermark đã đạt), nên mỗi lần retry phải quét-bỏ-qua lại
  toàn bộ lịch sử cũ (dedup an toàn, không sai dữ liệu, nhưng tốn thời
  gian). Loại trừ hẳn giả thuyết "container restart" bằng `docker inspect`
  (XAUT `RestartCount=0`, chạy liên tục, vẫn thấy replay `5m` lùi ~3
  tháng). Dưới áp lực 2 instance Bybit × 8 interval tranh đúng 1 slot,
  retry xảy ra nhanh hơn tốc độ tiến bộ thật → gần-livelock. Không phải
  data-correctness bug, là inefficiency thật — cần Codex xem xét (đổi core
  replay logic ảnh hưởng mọi broker, cần cẩn trọng, không tự sửa vội).
  File: xem entry `[trading][medium][round 123]` đầu
  `raw/handoff_agent.md`.

- **Round 124 (2026-08-24) — Đóng phần theo dõi backfill Bybit (Round 120-123 saga), mở rộng bằng chứng gate 1-slot sang 4 route khác, loại trừ 1 giả thuyết nghi ngờ mới:** (1) Verify độc lập qua Redis: cả 2 route Bybit `recent_klines` chỉ trễ ~4.5 phút (bình thường cho 5m) và `pending_history_backfill` rỗng — backfill catch-up hoàn toàn, không cần round sau tiếp tục theo dõi mục này nữa. (2) Backtest Vortex Indicator (Round 121, vẫn chưa commit) thử lại vẫn bị chặn — nhưng giờ do 4 route Binance/Exness khác đang tự chạy historical-replay riêng (trùng đợt redeploy MW ~4h trước, `pending_history_backfill['5m']` có 508 candle trên Binance BTC, đứng yên tuyệt đối qua nhiều lần đọc) tranh đúng 1 slot `KlineService.Stream` — cùng root cause gate 1-slot đã biết (Round 122-123), không phải bug mới, chỉ mở rộng phạm vi biểu hiện; `recent_klines` live-tailing của cả 4 route này vẫn tươi bình thường, không phải data-staleness bug. Backtest Vortex tiếp tục dời sang round sau. (3) Điều tra phụ: WARN "Exchange revised a closed kline ... evaluation remains blocked" bắn ra ở MỌI lần đóng nến (100% quan sát được) ban đầu nghi là nguyên nhân thật của Target 2 stagnant — đọc code `trading_api.rs::record_closed_kline` xác nhận đây là thiết kế cố ý (chống lặp lại TRA-928 incident), evaluate vẫn xảy ra đúng 1 lần/candle ở lần đóng đầu tiên, KHÔNG phải nguyên nhân Target 2 — loại trừ, không cần round sau điều tra lại. Không có backtest mới/candidate mới round này (thời gian dồn hết vào điều tra production). File: xem entry Round 123/121 trong `raw/handoff_agent.md` (không tạo file round riêng vì không có kết quả backtest mới để báo cáo).

- **Round 125 (2026-08-24) — Tìm ra bug hạ tầng thật mới (gRPC stream gate leak), SỬA LẠI chẩn đoán sai của Round 124:** đọc metric `finance_mw_grpc_requests_in_flight` trực tiếp từ MW xác nhận gate 1-slot `kline.KlineService/Stream` đang bị kẹt bởi 3 kết nối "in-flight" dù không worker nào đang replay — root cause: `timeout ... docker run` (cách round trước dùng để bound backtest CLI) chỉ kill CLI wrapper chứ không kill container thật, để lại kết nối gRPC leak mỗi lần thử. Xác nhận bằng thực nghiệm (kill đúng container → in_flight giảm 3→2 ngay). **Sửa lại Round 124's chẩn đoán "4 route Binance/Exness chiếm slot" — SAI**, vì `pending_history_backfill` là buffer Kafka out-of-order nội bộ không liên quan gì gRPC stream gate (đọc code xác nhận). Log Todo mới cho Codex (`[observability][medium][round 125]`, đầu `raw/handoff_agent.md`) đề xuất thêm keepalive/idle-timeout cho gRPC server để tự giải phóng gate khi client chết. Đã sửa quy trình backtest tooling của skill cho các round sau (dùng `-d --name` + `rm -f`, không dựa vào `timeout` kill wrapper). Backtest Vortex Indicator (Round 121) vẫn dời tiếp — 2 slot leak cũ còn sót cần MW restart tự nhiên mới hết. Không có backtest/candidate mới round này (dồn thời gian điều tra hạ tầng, coi là "tìm ra bug mới" theo Rule 7).

- **Round 126 (2026-08-24) — Gate stream vẫn leak (không rush fix, cần cẩn trọng theo note Round 125), chuyển sang dọn dẹp `## Verify` backlog:** đã đóng 9 mục Verify tồn đọng sang Done qua verify độc lập thật (không chỉ đọc file): (1) follow-up Monday của Round102 XAU/Exness weekend false-alarm — PASS đầy đủ (checkpoint tươi ~4 phút, eval_count 795>689 baseline, container healthy 18h); (2) Bybit BTC risk-limit + full integration — re-confirm qua nhiều round liên tiếp đã ổn định; (3) OOM cgroup fix — re-check `restarts=0`, memory 104.9MiB/512MiB sau nhiều giờ backfill nặng; (4-9) batch 6 mục infra/credential-rotation 2026-08-22 (VictoriaMetrics/Redis/Trace panel/rename/Docker cleanup) — spot-check containers healthy 39h, không regression. `## Verify` giờ chỉ còn watcher note (standing, không phải task). Không có backtest/candidate mới round này (backtest tool vẫn bị block bởi gate leak, ưu tiên dọn backlog thay vì đợi vô thời hạn).

- **Round 127-129 (2026-08-24) — Implement + deploy fix keepalive cho gate leak (Round 125), xác nhận ĐÚNG nhưng KHÔNG đủ, tìm ra nguyên nhân thứ 2 thật sự đang chặn:** Round 127 implement `grpc.KeepaliveParams` (commit `1adff58`), full CI/deploy/verify production thành công (SHA khớp, PID fresh xác nhận qua `ps -o etimes`). Round 128-129 verify sau deploy phát hiện `in_flight` vẫn giữ ở 2 dù process hoàn toàn mới — loại trừ dead-client, điều tra sâu ra `GetOldestOpenTime` (dùng bởi `kline_sync_full`) mở stream KHÔNG giới hạn From/To chỉ để đọc 1 record, kết hợp `StartupTimeout=4h` của job đầu tiên sau restart worker — có thể giữ gate tới 4 giờ sau mỗi lần redeploy. Đã log Todo chi tiết + hướng fix, KHÔNG rush implement thêm (đã tốn 3 round liên tiếp cho vấn đề hạ tầng này, cần dừng lại). Backtest Vortex Indicator (Round 121) tiếp tục bị chặn tới khi có fix tiếp theo hoặc redeploy khác. Bài học quy trình: 1 finding hạ tầng có thể có NHIỀU nguyên nhân xếp chồng — đừng dừng điều tra chỉ vì tìm được 1 giải thích hợp lý, luôn verify bằng chứng thực nghiệm (fresh PID, in_flight thực tế) trước khi tuyên bố đã fix xong.

- **Round 130 (2026-08-24) — Quay lại research thực chất sau 3 round hạ tầng, cơ chế mới: realized-volatility expansion-regime filter (Rule 3, web research):** khác các filter đã thử (SMA/ADX trend, Bollinger/Keltner volatility-squeeze BREAKOUT) — đây là filter volatility layered lên entry đã có, không phải cơ chế entry mới. Implement `RealizedVolatilityRegimeFilterStrategy` (tái dùng `atr()` có sẵn), 2 composition wrap `candle_momentum`, 3 unit test mới xanh, full suite 126/126 xanh. Backtest thật vẫn bị chặn (gate Round 129 chưa tự giải phóng) — code giữ local uncommitted, chờ round sau khi gate rảnh. Cơ sở từ research ngoài: cùng nhóm "filter giảm drawdown không cần signal mới" như 2 lever Portfolio-construction thành công Round 80/83, lần này thử ở tầng Alpha.

- **Round 132-133 (2026-08-24) — Fix thứ 2 cho gate (timeout GetOldestOpenTime), verify thực nghiệm cho kết luận trung thực: fix đúng nhưng gate 1-slot vẫn là giới hạn dung lượng thật, không phải bug thuần túy:** implement/deploy/verify `context.WithTimeout(10s)` cho `GetOldestOpenTime` — bằng chứng: `requests_total` Stream leo lên 48 (trước đây tối đa 2, không bao giờ tăng), 1 request nhỏ (`--days 1`) chạy thành công 14s. Nhưng request lớn hơn (7/90/1825 ngày) vẫn bị treo do tranh chấp capacity=1 thật với traffic hợp lệ khác — không phải leak. Kết luận: 2 fix (Round 127 keepalive + Round 132 timeout) đã đóng đúng phần "leak", còn lại là giới hạn kiến trúc (1 slot) cần fix riêng nếu muốn backtest tool luôn dùng được ngay — không rush, cần review kỹ vì chạm memory-budget cgroup 512MiB. Bài học: đừng dừng lại ở "có vẻ đã fix" — luôn verify bằng request thật nhiều kích cỡ khác nhau trước khi tuyên bố xong.

- **Round 139-141 (2026-08-24) — TÌM RA ROOT CAUSE THẬT của gate saga (Round 122-138) qua goroutine dump thật, không còn suy đoán:** Round 139 wire up `net/http/pprof` (comment code cũ tự nhận đã làm nhưng thực ra chưa — xem Round 125). Round 141 dùng ngay: `debug/pprof/goroutine?debug=2` lộ ra 2 goroutine kẹt đúng 459 phút = khớp tuổi process (kẹt từ lúc boot). 1 goroutine giữ slot gate, kẹt ở HTTP/2 flow-control (`writeQuota.get`) vì client (rất có thể `live-action-bybit-perpetual-future-btc-usdt`, khớp thời điểm log 08:15:13Z) ngừng đọc stream — KHÔNG phải dead connection nên 2 fix trước (keepalive Round 127, timeout Round 132) đều đúng nhưng không bắt được loại lỗi này. Goroutine còn lại kẹt chờ ở `Acquire()` từ lúc boot — giải thích chính xác `in_flight=2` đứng yên suốt nhiều round. Phát hiện phụ: DB connection Postgres cũng bị giữ mở 459 phút theo. Chưa fix (cần sửa client-side finance-live-action hoặc thêm `MaxConnectionAge` phía MW, cả 2 đều cần round riêng cẩn trọng). Chi tiết đầy đủ → `raw/explain/kline-stream-gate-capacity-saga.md`. Bài học: pprof là công cụ đúng cho loại bug này ngay từ đầu — 15+ round trước đó đoán mò vì thiếu nó.

## 1. Hướng có cơ sở thật nhưng KHÔNG nên implement đứng độc lập

### Funding Rate Extreme Reversion (Round 22 → 46)
- **Trạng thái cuối cùng (Round 46):** có cơ sở thực nghiệm thật (2/3 cửa
  sổ lịch sử BTC độc lập khớp hướng dự đoán — funding cực dương → giá giảm,
  funding cực âm → giá tăng), nhưng **thất bại rõ trong giai đoạn trend
  mạnh kéo dài** (2024 H1). Đã tự test 2 cách patch bằng filter đơn giản
  (biên độ trend Round 45, hướng trend Round 46) — **cả 2 đều KHÔNG nhất
  quán, không cứu được vấn đề.**
- **Kết luận: KHÔNG implement như 1 signal đứng độc lập, KHÔNG patch bằng
  filter rule-based đơn giản.** Đề xuất cũ "đưa vào ensemble đa-signal" đã
  KHÔNG còn hợp lệ (mục 2 dưới đây đã đóng, thất bại khi test qua engine
  thật) — hiện KHÔNG có hướng nào rõ ràng để dùng candidate này tiếp.
- **Phạm vi nếu implement:** CHỈ BTC/binance — XAU/binance test riêng
  (Round 43) cho kết quả NGƯỢC DẤU hoàn toàn + dữ liệu quá mỏng/không đối
  xứng (63% funding=0, chưa từng âm).
- File: `round22-*.md`, `round42-funding-rate-hypothesis-validated-external-data.md`
  (có đủ 5 lần cập nhật Round 42/43/44/45/46 trong cùng 1 file).

## 2. Ensemble/regime-switching MTF 4h/1d — ĐÃ ĐÓNG, THẤT BẠI khi test qua engine thật (Round 54 correction)

### Ensemble/regime-switching giữa 3-4 biến thể MTF 4h/1d (Round 36-38, 51-54, ĐÓNG round 54)
- **[QUAN TRỌNG — đọc trước, đảo ngược mọi khuyến nghị "ưu tiên implement"
  trước đó]** Round 51-54 tự backtest ensemble bằng cách **lấy trung bình
  cộng `daily_results.return_fraction` của 4 candidate chạy ĐỘC LẬP** (mỗi
  candidate tự có ledger riêng) — tìm được kết quả có vẻ rất tốt (Sharpe
  tới 1.8, pass được `positive_day_ratio`).
- **Codex đã implement thật qua `PortfolioDecisionPolicy` thật** (commit
  `56a7f82` fix gap Round 20 + `339458f` dùng đúng trọng số grid-search
  Round 54: baseline=0.5/ADX=0.2/macd=0.1/candle_momentum=0.2) — **kết quả
  THẬT hoàn toàn khác: Sharpe -6.72, positive_day_ratio 25.14% (fail nặng),
  net PnL -5.92.**
- **Nguyên nhân: lỗi phương pháp luận của chính Claude.** Trung bình cộng
  PnL của 4 ledger ĐỘC LẬP (như 4 quỹ riêng biệt) hoàn toàn khác về hành vi
  với 1 Portfolio ensemble thật (tổng hợp entry/trend-score có trọng số
  thành 1 quyết định DUY NHẤT mỗi candle). 2 mô hình không tương đương.
  Thêm nữa: trọng số Round 54 bị grid-search TRÊN CHÍNH window dùng để báo
  cáo kết quả — data snooping/overfitting kinh điển.
- **KHÔNG còn là hướng có triển vọng.** Codex đã đúng khi đánh dấu
  `research_only=true`, `promotion_eligible=false`, không promote. **Đóng
  hẳn hướng ensemble/regime-switching kiểu này** — không log lại đề xuất
  tương tự trừ khi dùng đúng `--weighted-ensemble-gate` (qua engine thật)
  với holdout độc lập cho bước chọn trọng số, không backtest tay nữa.
- File: `round36-*.md`, `round51-*.md` (lịch sử điều tra, giữ nguyên để lộ
  quá trình), `round54-CORRECTION-real-decide-engine-invalidates-manual-backtest.md`
  (kết luận cuối cùng, đọc file này là đủ).

## 3. Đã ĐÓNG — không cần test lại, tránh lặp lại công sức

| Hướng | Round phủ định | Lý do |
|---|---|---|
| Donchian Channel breakout (Turtle Trading, period 20/55/100/200) | 88 | BTC plateau PF<1 cả 2 broker; XAU có PF>1 vài split nhưng hướng ngược nhau giữa 2 broker — overfit, không phải edge |
| Keltner Channel reversion (EMA+ATR band, multiplier 1.5/2.0/2.5) | 91 | PF<1 nhất quán cả 12 ô (3 tham số × 4 route), không đảo chiều/overfit — cùng kết luận `bollinger_reversion` (đã đóng Round 24) dù đổi cả midline (EMA) lẫn thước đo biến động (ATR) |
| Heikin-Ashi smoothed momentum (color-flip sau confirm_candles 1/3/5/10) | 93 | PF<1 toàn bộ 16 ô. Hội tụ về cùng trần ~0.65-0.85 như Donchian/Keltner khi kéo dài tham số — xem mục "trần chi phí cấu trúc" bên dưới |
| Trend-filter áp lên Keltner reversion/Donchian breakout đã đóng (giả thuyết Round 33) | 94 | Keltner: PF<1 mọi route, không được cứu. Donchian: PF~1.0 nhất quán 5 năm (2 broker BTC) nhưng ĐẢO NGƯỢC hình dạng hoàn toàn trên cửa sổ 18 tháng độc lập — false-positive kinh điển, đóng |
| VWAP mean-reversion (session-anchored) | 18, 21 | PF<1 nhất quán cả 3 split trên cả XAU lẫn BTC |
| ORB 30m/60m (London session breakout) | 18→34 | Thắng ở window 5 năm nhưng ĐẢO NGƯỢC hoàn toàn khi test window 18 tháng — regime artifact |
| Bollinger reversion + trend filter | 24 | Không nhất quán qua 3 split |
| Supertrend regime filter | 24 | Chỉ thắng holdout, dạng đáng ngờ |
| Oscillator PLAIN không trend filter (mọi base interval) | 33 | 0/3 test có candidate PF>1 — trend filter mới là nguồn edge |
| Đổi base interval (5m/1h) để tăng tần suất, giữ nguyên trend filter | 19, 24, 78, 118 | Không tăng tần suất tương ứng, MỌI metric chất lượng đều xấu đi. Round 78 quét thêm 15m/30m riêng cho XAU (chưa test kỹ trước đây): `ema_crossover_12_26` @ 30m là candidate ổn định nhất từng thấy cho cả BTC lẫn XAU (PF 0.77-0.97, không giật cục) nhưng vẫn <1 mọi split — điểm neo tham khảo, chưa đạt bar. Round 118 mở rộng sang 1h: BTC vẫn ổn định cross-broker (0.83-0.89), XAU near-miss (train/holdout >1) nhưng zigzag + mẫu mỏng, tự loại |
| `mtf_ema_crossover_12_26_sma10_trend_filtered` (trend-filter hoá Round 78's finding) | 79 | BTC: pattern đảo hoàn toàn giữa window 5 năm và 18 tháng (dạng lõm giữa → dạng yếu dần đều) — bất ổn định, giống dấu hiệu đã phủ định ORB Round 34. XAU: mẫu quá nhỏ (7-14 trade). Kết luận: gấp đôi trend-following (entry+filter cùng đo xu hướng) không tạo edge, khác hẳn khi filter áp lên oscillator/order-flow |
| `ema_crossover_12_26`@30m + volume filter (lever Round 78 gợi ý, lần đầu thử) | 107 | 4 route cho 4 shape khác nhau hoàn toàn (không nhất quán như Round 106's BTC), trades giảm 65-90% không đều — dấu hiệu nhiễu từ tập con quá nhỏ, không phải filter thật |
| Ichimoku Cloud TK-cross + displaced cloud filter (9/26/52/26, cơ chế index-system hoàn toàn mới) | 108 | PF 0.507-0.881 toàn bộ 12 ô, không ô nào vượt 1.0. BTC ổn định, tăng dần đơn điệu, nhất quán 2 broker gần như y hệt — **điểm neo ổn định thứ 2** sau `ema_crossover_12_26`@30m (Round 78), tham khảo cho lever tương lai |
| Parabolic SAR Wilder (0.02/0.02/0.2, cơ chế trailing-stop-and-reverse hoàn toàn mới) | 109 | PF 0.14-0.48 toàn bộ 12 ô — thấp, không ô nào gần 1.0. BTC cross-broker gần như y hệt (0.475/0.418/0.424 vs 0.472/0.434/0.423) nhưng vẫn xấu. AF mặc định phản ứng quá nhanh với nhiễu 5m gây whipsaw |
| CCI momentum breakout (20/100, indicator mean-deviation mới) + SMA(10) trend filter | 110 | PF 0.256-0.557 toàn bộ 12 ô, thấp và không gần 1.0. Phát hiện phụ: trend filter gần như no-op ở đây (trade count/PF trùng khớp bản thô trong sai số 0-4 lệnh) — CCI threshold crossing đã hàm ý trùng hướng SMA sẵn |
| On-Balance Volume signal-line crossover (period 20, cumulative signed total-volume — sửa lại Round 116: KHÔNG phải "volume-primary đầu tiên", Taker Imbalance Round 72-75 đã là volume-primary trước) | 113 | PF 0.092-0.365, win rate 6.7-15.5% — **thấp nhất toàn phiên** (mọi candidate khác ≥12.6% PF/thường 20-50% win rate). Tần suất tín hiệu cực cao (tới 53,878 lệnh) do OBV dao động quá thường xuyên quanh đường tín hiệu trên 5m. BTC cross-broker vẫn nhất quán hướng dù yếu |
| MFI mean reversion (14/20/80, oscillator bị chặn 0-100 có trọng số volume) bản thô | 114 | PF 0.387-0.958, win rate 33.8-58.2% — **oscillator thô (không filter) gần breakeven nhất chương trình** (BTC/exness validation 0.958, n=460). Vẫn <1 mọi ô. Bản ADX-filtered bị đóng riêng vì mẫu quá mỏng (12-41 trade) + zigzag validation-spike PF 1.5-3.6 — artifact kinh điển |
| Three White Soldiers/Black Crows (3-candle continuation, hình học khác Engulfing 2-candle) | 117 | PF 0.280-0.630 toàn bộ 12 ô, không ô nào gần 1.0. Cùng failure mode Engulfing — pattern nến thuần hình học (không volume/oscillator) đều thất bại trong chương trình này |
| Elder Ray Index (EMA(13)+high/low net power crossover) | 119 | PF 0.097-0.348, win rate 7.1-14.5% — cùng failure mode OBV Round 113 (tần suất cực cao tới 47,494 lệnh, cơ chế combined-multi-source-crossover thô quá nhạy trên 5m) |
| Vortex Indicator (VI+/VI- crossover, period 14) | 149 | PF 0.344-0.388, ổn định cả 3 split (5-year window) — không phải false-positive shape, chỉ là tín hiệu quá nhiễu ở 5m không kèm filter |
| Swing 4h/1d full sweep trên XAU (chưa từng chạy — Round 17 chỉ làm BTC) | 205 | Binance có 4 candidate vượt 1.0 cả 3 split (`engulfing_pattern` 1.44/1.58/1.73, `heikin_ashi_momentum_3`, 2 biến thể mtf_stochastic) nhưng **exness phủ định toàn bộ** (0.65/0.86/0.70 v.v.) với mẫu lớn hơn 4-5 lần. Nguyên nhân: binance XAU chỉ có 1,543 nến 4h (~257 ngày) vs exness 7,986 (~3.6 năm) → artifact mẫu nhỏ, cùng chữ ký đã falsify ATR breakout (r61)/Donchian (r88)/Fibonacci (r106). **Cảnh báo: đừng mở lại các cơ chế đã đóng ở 5m dựa trên kết quả 4h của riêng binance XAU.** Lead yếu duy nhất: `mtf_stochastic_14_3_30_70_sma10_trend_filtered` có train+holdout >1 ở CẢ 2 broker nhưng validation exness 0.70 và mẫu binance 18/7/9 — chưa đạt bar |
| Larry Connors RSI(2) 10/90 (cơ chế thật từ literature: RSI cực nhanh + ngưỡng cực đoan + trend filter dài hạn) | 204 | Bare: PF 0.024-0.111 cả 2 broker, 41,981 lệnh/train ở exness — over-trading thuần túy trên nhiễu 5m, **cơ chế oscillator thứ 8** thất bại đúng kiểu này (sau Stochastic/CCI/MFI/OBV/Elder Ray/Vortex/Awesome). Bản +SMA200 filter khá hơn NHIỀU (0.05→0.7, tái khẳng định filter mới là nơi có edge) nhưng vẫn <1 mọi ô (binance 0.707/0.905/0.750, exness 0.425/0.552/0.865) và 2 broker không đồng thuận split nào đỡ nhất → không có shape ổn định. Không cần cross-window 18 tháng vì không ô nào gần breakeven |
| Awesome Oscillator (Bill Williams, SMA(5)/SMA(34) của midpoint high+low, zero-line cross) | 150 | PF 0.494-0.538 ổn định cả 3 split — cơ chế thứ 7 (sau Stochastic/CCI/MFI/OBV/Elder Ray/Vortex) thất bại cùng lý do: oscillator thuần không kèm trend/regime filter luôn thua ở 5m, bất kể cơ chế smoothing cụ thể — bằng chứng hội tụ mạnh đây là trần cấu trúc, không phải đặc thù 1 indicator |
| Session time-of-day filter (UTC hour, London/NY overlap 12-16h và exclude-Asian 6-22h, áp lên candle_momentum/rsi_mean_reversion) | 164 | PF<1 nhất quán cross-instrument (BTC+XAU) mọi biến thể candle_momentum. 1 outlier XAU RSI holdout PF 0.971 (55 trade, train/validation thấp hơn nhiều) — dạng "chỉ holdout thắng" đã biết là false-positive, không promote |
| 5m entries gated bởi 1d SMA trend filter (`--interval 5m --higher-timeframe-interval 1d`, motivated bởi swing edge Round 172-180) trên XAU | 181 | ĐÓNG sạch — cả 7 biến thể (candle_momentum/rsi/bollinger/keltner) train PF>1 nhưng sập validation+holdout, dạng overfitting kinh điển |
| Funding rate contrarian threshold (nguồn thông tin THẬT SỰ khác OHLCV, dùng public Binance API do bearer token nội bộ bị chặn) | 168, 171 | Correlation sơ bộ có vẻ hứa hẹn (decile cực trị: funding dương cực đoan → return 8h kế tiếp -0.131%) nhưng ĐÓNG dứt điểm sau khi test đúng phương pháp 3-way split thời gian thật: train PF 1.30, validation PF 8.17 (n=10, artifact mẫu mỏng), **holdout PF 0.35** — dạng "chỉ train+validation đẹp, đảo trên holdout" kinh điển |
| Realized Volatility Regime Filter (áp lên `candle_momentum`/`rsi_mean_reversion`, threshold 1.1/1.3) | 149 | PF<1 mọi biến thể cả 3 split (0.47-0.83) dù giảm mạnh trade count (filter có tác dụng lọc nhưng không đổi dấu edge) — cùng kết luận nhóm filter khác (ADX/min-strength/volume) |
| Alpha-level stop/take tuning cho `candle_momentum`/`rsi_mean_reversion` | 25, 59 | Bất biến/xấu đi ở 4 tổ hợp instrument×strategy mặc định (25) VÀ ở các biến thể tham số rộng hơn tìm được sau (30bps/14_20_80, round 59) — đóng hoàn toàn, không phụ thuộc tham số (đã sweep nhiều tham số). Round 101 test THÊM 3 cơ chế mới (Donchian/Keltner/Heikin-Ashi) nhưng **chỉ đúng 1 cấu hình duy nhất** (stop=0.01/take=0.02, không sweep tham số) — hiệu ứng nhỏ/trái chiều, cùng hướng với 25/59 nhưng phạm vi bằng chứng hẹp hơn (1 config, chưa chứng minh bất biến qua tham số như 25/59). Codex root-review 2026-08-23 xác nhận scope hẹp này; không đổi kết luận CLOSED nhưng không nên diễn giải là "chứng minh vô dụng với mọi tham số" cho 3 cơ chế mới — nếu cần độ tin cậy ngang 25/59, phải sweep thêm tham số stop/take cho Donchian/Keltner/Heikin-Ashi trước |
| ICT liquidity-sweep/FVG | 27 (research) | Bằng chứng học thuật: edge biến mất ở granularity 1 phút thật (lookahead artifact) |
| Funding-reversion patch bằng filter đơn giản | 45-46 | 2 cách filter khác nhau đều không nhất quán qua các cửa sổ lịch sử |
| Day-of-week seasonality (BTC) | 47 | t-stat cao ở toàn kỳ nhưng biến mất khi split-test — data-mining artifact |
| XAU 1h/1d stochastic (PF=13.8 top-line) | 49 | Train/validation gần hoà vốn/lỗ, chỉ holdout 8 trade đẹp — mẫu quá thưa, cùng shape đã falsify nhiều lần |
| Open Interest / Long-Short Ratio qua public Binance API | 47-48 | Chỉ giữ 30 ngày lịch sử, không đủ test honest |
| Không gian "1 candidate đơn lẻ tại 5m production" | 60 | Sweep toàn bộ ~35 candidate plain, 0 đạt PF>1 nhất quán cả 3 split, cả BTC lẫn XAU — đã quét gần hết |
| Bollinger/Keltner volatility squeeze breakout | 70 | Cơ chế MỚI (regime chuyển đổi biến động, không phải threshold giá/oscillator) — implement + backtest thật, PF thua lỗ nhất quán cả 3 split, cả BTC lẫn XAU (0.68-0.76) — code giữ lại trong grid nghiên cứu (research-only, không đụng production) |
| "Tăng position size để cứu daily-bar signal" (đề xuất từ thread nghiên cứu trước) | 71 | SAI kỹ thuật — fee/slippage/funding đều tính theo % (bps), không phải USD cố định/trade, nên tăng size không đổi tỷ lệ cost/profit. Tín hiệu `stochastic_14_3_30_70`/`rsi_mean_reversion_9_30_70` khung 1d tự nó cũng đã yếu đi (PF 0.84-1.25, không còn rõ >1) khi test lại với dữ liệu mới |
| Order-flow imbalance (taker buy/sell ratio, cả 2 hướng follow lẫn fade) | 72-75 | Chiều dữ liệu MỚI — plain thua lỗ nặng (72). Trend filter 4h: PF cải thiện mạnh trên BTC (0.19-0.29→0.69-0.91) nhưng vẫn <1; XAU overfit ngược (73). Trend filter 1d: BTC PF>1 validation/holdout lặp lại ở 2 window độc lập nhưng mẫu quá mỏng (holdout 16-67 trade), XAU thất bại hoàn toàn — mẫu chỉ 15-18 trade/split (75). Đóng toàn bộ hướng này |
| `atr_breakout_14_3_0` (near-miss Round 60) | 61 | Giữ được PF>1 cả 3 split ở window 18 tháng trên BTC/binance, nhưng ĐẢO NGƯỢC khi test cross-broker (Exness BTC validation PF=0.729) và cross-instrument (XAU holdout PF=0.331) — artifact riêng Binance BTC, không phải signal thật |
| Two-candle engulfing pattern (candlestick body-containment reversal, không trend filter) | 103 | PF 0.16-0.42 toàn bộ 12 ô (3 split × 4 route) — THẤP NHẤT từng quan sát trong chương trình. Cost ablation xác nhận cost-limited (no-cost PF→0.97-0.99) nhưng tần suất tín hiệu cực cao (34k trade/route, 4-15× candidate khác) khuếch đại chi phí mạnh hơn hẳn mọi candidate trước |
| Engulfing pattern + SMA(10) same-timeframe trend filter | 104 | Cải thiện nhất quán 12/12 ô (+0.05 tới +0.14 PF tuyệt đối) nhưng baseline (103) xuất phát quá thấp — ô tốt nhất chỉ đạt PF 0.506 (BTC/exness holdout), còn cách breakeven rất xa. `SmaTrendFilterStrategy` (wrapper generic, cùng-timeframe, không cần `--higher-timeframe-interval`) giữ lại để tái dùng cho candidate khác |
| Fibonacci Golden Zone(100) + SMA(10) trend filter — **near-miss gần nhất phiên này** | 106 | 5 năm: PF>1 validation+holdout, nhất quán 2 broker BTC (binance 1.447/1.248, exness 1.141/1.026) — bằng chứng mạnh nhất trước cross-check. Cross-check 18 tháng bắt buộc: ĐẢO HÌNH DẠNG hoàn toàn cả 2 broker (train giờ >1, validation tụt <1), mẫu mỏng hơn — đóng. Ví dụ rõ nhất trong chương trình cho lý do cross-window check bắt buộc |

## 4. Gap hạ tầng/công cụ — chặn khả năng verify chính xác hơn

1. **`finance-research` không chạy qua engine quyết định thật**
   (`PortfolioDecisionPolicy`/`MultiTimeframePortfolioPolicy::decide()`) —
   mọi số liệu PF/Sharpe trong CSV chỉ trả lời "signal này có lời nếu chạy
   solo", KHÔNG trả lời "Portfolio thật có quyết định trade nhiều hơn
   không" (Target 2). Round 20, đề xuất sửa `portfolio_measurement.rs`/
   `daily_profit_gate.rs` gọi đúng `decide()`.
2. **Kafka read-only access cho harness backtest qua engine thật** — P0
   credential đã rotate xong (mục 5), giờ chỉ còn cần cấp quyền đọc riêng
   (Round 20, chưa làm).
3. **`1m` kline retention ~4.4 ngày** — chặn walk-forward honest cho bất kỳ
   strategy nào cần granularity phút (Round 15 gốc + Round 27 làm rõ thêm
   lý do FVG).
4. **`daily-profit-gate` thiếu threshold tần suất** và thiếu Information
   Ratio/Ulcer Index/SQN/skew/kurtosis native (Round 17) — hiện phải tự tính
   tay mỗi round.
5. **`holdout_interval_continuity` fail lặp lại cho Exness XAU** (mọi
   timeframe: 5m, 4h/1d, 1h/1d) — Codex đã fix 2 lần (Round 20/21, giảm
   violation nhưng chưa về 0) — vẫn còn gap thật chưa root-cause hết
   (Round 49 vẫn gặp lại). **ĐÃ ĐÓNG cho riêng interval `5m` (Round 115,
   2026-08-23):** broker-verified marker backfill hoàn tất và deploy exact
   `7f70eb3`, Claude verify độc lập qua `finance-research` continuity block
   (kênh khác hoàn toàn công cụ Codex dùng): `exness.cfd.XAU.USD/5m` giờ
   `unverified_gap_candles=0, unverified_gap_count=0` (trước đó
   `170654`/`1304` — xem Round 107). **8 interval còn lại (15m/30m/1h/2h/4h/
   12h/1d) vẫn còn unverified gap** — scope backfill chỉ giới hạn `5m`, chưa
   mở rộng. Chi tiết → `raw/explain/exness-gap-metadata-continuity.md`.

## 5. Bảo mật/hạ tầng

- Outage Postgres production (Round 26-32) — ĐÃ KHÔI PHỤC.
- Kafka `KAFKA_CLIENT_PASSWORDS` lộ do lỗi redact của Claude (Round 20) —
  Codex đã rotate cả Kafka lẫn Grafana admin (exposure khác tự phát hiện
  thêm), Claude verify độc lập, chuyển Done (Round 41).
- **CHƯA ĐÓNG — Round 76 (2026-08-21):** `KAFKA_CONTROLLER_PASSWORD` lộ do
  Claude chạy `docker exec ... env` không lọc trên cùng container Kafka
  (sự cố lộ credential thứ 2 trên container này, nguyên nhân gốc khác Round
  20 nhưng cùng dạng "thao tác quá rộng"). Không tự rotate (rủi ro gãy
  KRaft quorum nếu sai). **Cần Codex (hoặc round sau, cẩn thận) rotate
  credential này khi có điều kiện.** Đã cập nhật memory + skill
  `quant-research-loop` để tránh lặp lại. File:
  `round76-kafka-controller-password-exposure-incident.md`.

## 6. Target 2 (Make Decision rate) — stagnant xuyên suốt, đo lặp lại nhiều lần

Round 23/40/48: liên tục ghi nhận gần như **0 trade mới** across tất cả
scope Portfolio trong nhiều giờ, dù `evaluation_count` vẫn tăng bình thường
— hệ thống hoạt động đúng thiết kế, chỉ đơn giản tần suất signal quá thấp.
**Không có tiến triển tự nhiên nào** trong thời gian dài — nhưng **Round 65
tìm ra 1 hướng fix khả dĩ CHỈ CẦN THAY ĐỔI CONFIG** (subscribe thêm 1
strategy cho Binance/XAU), xem chi tiết cuối mục này — không còn chắc chắn
"cần code mới" nữa cho riêng leg Binance/XAU.

**Cảnh báo phương pháp luận (Round 40):** `trade_count` đọc từ checkpoint
KHÔNG phải counter ổn định qua worker restart — luôn kiểm tra `eval_count`
trước khi so sánh giữa 2 round. Baseline round 48 (trước epoch-fix, không
restart từ round 40): BTC/binance=1286, BTC/exness=1313, XAU/binance=8,
XAU/exness=735.

**Round 62 (2026-08-21):** Codex vá bug epoch-migration (`bfccc9a`, verify
độc lập xong, chuyển Done) — reset lại bộ đếm `trade_count` cho toàn bộ 4
route theo `epoch_version=1` mới. Baseline MỚI đo cùng 1 thời điểm sau fix:
BTC/binance=1126, BTC/exness=1117, XAU/exness=758, **XAU/binance=8 (y hệt
trước fix)** — xác nhận epoch fix chỉ sửa lỗi đếm sai, KHÔNG cải thiện tần
suất thật. **Phát hiện mới cùng round:** `pending_history_backfill` của
Binance/XAU kẹt từ Dec 2025 (~8 tháng, đúng đợt listing), trong khi 3 route
kia rotate bình thường (5 ngày - 1 tháng tuổi) — lead cụ thể đầu tiên khác
giả thuyết "chỉ do lịch sử ngắn" cũ, đã log Todo cho Codex điều tra, chưa
chứng minh nhân quả. Xem `round62-xau-binance-stuck-backfill-and-epoch-fix-verify.md`.

**Round 63 (2026-08-21) — NÂNG P2→P1, tìm ra cơ chế cụ thể:** đọc
`portfolio_evidence.policy.interval_weights` trực tiếp từ checkpoint.
Binance/XAU: `1d=0.521, 12h=0.338, 4h=0.141`, còn `15m/30m/1h/2h/5m` đều
**= 0.0** (toàn bộ interval "entry" bị zero-out). Exness/XAU cùng lúc: trọng
số trải đều mọi interval trừ 5m. Vì `entry_score` chỉ tính từ interval
"entry", khi tất cả = 0 thì điểm chỉ đổi được khi nến 1d/12h/4h đóng (vài
lần/ngày) thay vì mỗi 5-30 phút — **giải thích trực tiếp (không chỉ tương
quan) vì sao trade_count=8**. Giả thuyết: `reweight_from_alpha_performance`
(lifetime-cumulative) chưa đủ dữ liệu để gán trọng số dương cho interval
ngắn với instrument mới list ~8 tháng. Cần Codex code-review xác nhận. Xem
`round63-binance-xau-interval-weight-mechanism.md`.

**Round 65 (2026-08-21) — ⚠️ SỬA LẠI giả thuyết Round 63-64, tìm nguyên nhân
THẬT bằng cách đọc source code:** giả thuyết "lịch sử ngắn → thiếu dữ liệu
→ weight=0" ở Round 63-64 **SAI**. Đọc trực tiếp
`reweight_from_alpha_performance`/`alpha_performance_quality`
(`trading_modes.rs:464-537`) + tái tạo công thức bằng Python trên dữ liệu
production thật — khớp CHÍNH XÁC 100% với `interval_weights` quan sát được.
Code cho thấy `trade_count=0` (thiếu dữ liệu) → `quality=1.0` (TỐI ĐA,
"benefit of doubt"), không phải 0. **Nguyên nhân thật: bất đối xứng
subscription strategy** — Binance/XAU chỉ subscribe 2 strategy
(`candle_momentum`, `rsi_mean_reversion`, cả 2 đều thua lỗ xác nhận với đầy
đủ trade_count ở mọi interval ngắn), trong khi 3 route còn lại subscribe
3-5 strategy (có strategy MTF hiếm khi trigger, `trade_count≈0` ở hầu hết
interval → tự động quality=1.0, tạo "sàn" nâng đỡ toàn bộ interval_weights).
~~Đề xuất fix rủi ro thấp: subscribe thêm 1 strategy (vd. đúng
`mtf_stochastic_5m_4h_sma5` như Exness/XAU) cho Binance/XAU~~ — theo công
thức đã verify, sẽ ngay lập tức khôi phục trọng số dương cho các interval
entry, không cần sửa thuật toán reweight. Xem
`round65-CORRECTION-real-mechanism-is-strategy-subscription-asymmetry.md`.

> ⚠️ **RÚT LẠI ở Round 67 (2026-08-21) — mục này KHÔNG còn là đề xuất active,
> giữ nguyên văn để lộ lịch sử.** Round 67 phát hiện `mtf_stochastic_5m_4h_sma5`
> bản thân ĐÃ ĐƯỢC XÁC NHẬN THUA LỖ (validate cũ dùng tool có bug lookahead
> MTF kline merge, đã fix commit `3c16745`; PF thật 0.58-0.98, không phải
> 19.6-26.6 như comment cũ ghi). Subscribe thêm 1 strategy ĐÃ BIẾT thua lỗ
> chỉ để lợi dụng hiệu ứng "benefit of doubt" là đúng anti-pattern "zombie
> strategy" mà Round 67 tự phát hiện ở 7 strategy MTF của BTC (đang giữ
> `strategy_weight≈0` nhưng vẫn "hữu ích" tình cờ để giữ `interval_weights`
> BTC không sụp). Xem
> `round67-MAJOR-invalidated-mtf-strategy-promotions-plus-dev-mode-switch.md`
> mục "Không xoá đề xuất Round 65-66" — kết luận rõ: rút lại.
>
> **Round 165-167 (2026-08-25) — ĐÃ THIẾT KẾ, SIMULATE, IMPLEMENT, DEPLOY,
> VERIFY. ĐÓNG DỨT ĐIỂM.** Round 165 thiết kế + Round 166 simulate (dùng
> data Redis thật, tái tạo công thức Python, khớp 100% với production) đã
> giải quyết xong 2 câu hỏi thiết kế còn mở: floor chỉ áp `interval_quality`
> (không đụng `strategy_quality`, giữ nguyên "confirmed loser = 0" cho
> strategy), và chấp nhận floor hằng số phẳng `0.05` (không chuẩn hóa theo
> số strategy) làm lựa chọn đầu tiên hợp lý. Round 167 implement
> `MultiTimeframePortfolioPolicy::INTERVAL_QUALITY_FLOOR=0.05`
> (`trading_modes.rs`), thêm test, full suite xanh, commit `7fe0e13`, deploy,
> **verify production khớp CHÍNH XÁC dự đoán simulation tới 6+ chữ số** cả 4
> route (XAU/binance 0.0479, BTC/binance 0.0109, BTC/exness 0.0108,
> XAU/exness 0.0161 — trước đó cả 4 đều = 0.0000 đúng nghĩa đen). Đóng cả
> chuỗi điều tra Target 2 từ Round 63→167. Chi tiết đầy đủ →
> `raw/researcher/round165-target2-interval-weight-floor-proposal.md`. Theo
> dõi tiếp production 1-2 ngày sau để xem `trades_per_week` có dịch chuyển
> đo được không.

## Cách dùng tài liệu này

Mỗi round `/loop` mới: đọc file này trước để biết đang ở đâu, tránh lặp lại
test đã có kết luận rõ (mục 3), kiểm tra Codex đã pick up item nào ở mục 4
chưa. Cập nhật lại đúng phần tương ứng khi có kết quả mới, không cần đọc lại
toàn bộ file `round*.md` mỗi lần.

## Thứ tự ưu tiên giữa Rule 1 vs Rule 2/3 (quyết định 2026-08-21, sau Round 83)

Không thêm rule mới vào prompt `/loop` gốc — bộ Rule 0-7 hiện tại đã đủ
rộng. Thay vào đó, **ưu tiên nội bộ giữa 2 nhóm rule đã đổi dựa trên bằng
chứng thực tế qua 83 round**, user xác nhận đồng ý:

- **Rule 1 (tinh chỉnh sizing/position/Portfolio-construction): KHÔNG CÒN
  "ƯU TIÊN CAO" — không gian này đã gần cạn, tương tự Rule 2/3 (sửa lại
  2026-08-25 sau khi Round 151-162 lặp lại phần lớn Round 87-92).** Lịch sử
  đầy đủ:
  - Round 80 `minimum_hold_decisions` 12→36: ĐÃ TRIỂN KHAI, giảm ~34% lỗ.
  - Round 83 `stop/take` 0.005/0.010→0.01/0.02: ĐÃ TRIỂN KHAI, giảm 33-43%.
  - Round 81-82 ATR-stop: fail cross-broker, đóng.
  - **Round 87 (2026-08-22): đã test đúng câu hỏi "2 lever cộng dồn tuyến
    tính hay tương tác?"** — factorial 2×2 đầy đủ, kết luận sub-additive
    (đạt 56-74% mức cộng dồn tuyến tính dự đoán), production hiện tại (cả 2
    lever) vẫn là tổ hợp tốt nhất trong 4 tổ hợp. **Đã đóng dứt điểm — không
    cần test lại.** File: `round87-hold-stoptake-interaction-sub-additive-confirmed.md`.
  - **Round 89-90 (2026-08-22): đã test `risk_fraction`/`equity_fraction`
    sizing mode** — kết luận giống hệt Round 151/152 (lặp lại, xem dưới):
    `risk_fraction=0.02` mất 98-99.9% vốn mô phỏng, công thức
    `notional=equity×risk_fraction/stop` ẩn chứa đòn bẩy hiệu dụng 2x tại
    tham số hiện tại; `equity_fraction`/`risk_fraction` toán học tương
    đương ở cùng đòn bẩy, lỗ scale phi tuyến (compounding hình học) theo
    đòn bẩy; chỉ `fixed_notional` (rule `fixed-pct` đang live thật) không
    compounding, an toàn. **Cả 2 rule `risk-2pct`/`compounding-10pct` đã
    chạy CONCURRENT thật trong production dạng paper-ledger (không qua
    broker thật — xem `deployment_rules.rs:99-133` comment "does not submit
    broker orders") từ trước Round 87, chính là cách Round 89/90 lấy số
    liệu.** File: `round89-risk-fraction-effective-leverage-catastrophic-loss.md`,
    `round90-equity-compounding-sizing-geometric-decay-confirmed.md`.
  - Round 92: đóng hướng "kéo dài hold thêm" — margin Target 3 hiện đã
    mỏng (~9.3/tuần 5-năm, ~7.2-7.3/tuần 18-tháng), hold=72 đã dưới ngưỡng.
  - **Round 151-152/162 (2026-08-25) — RE-CONFIRM không phải phát hiện mới,
    xem là do chưa đọc kỹ mục này trước khi bắt đầu (bài học quy trình dưới
    đây):** lặp lại kết luận Round 89/90 cho `risk_fraction` với config
    stop/take đã sửa đúng + dữ liệu holdout-only tươi hơn (94.2% drawdown,
    khớp hướng Round 89's 99.94% — khác biệt do phạm vi đo: Round 151/152
    dùng `--daily-profit-gate` (chỉ holdout ~1 năm) còn Round 89 dùng
    `one_target` (cả cửa sổ 5 năm) — không phải mâu thuẫn, chỉ khác scope).
    Phần thật sự mới từ các round này: (1) phát hiện + tự sửa 1 lỗi
    phương pháp (env var `PORTFOLIO_STOP_VALUE` vestigial, không được code
    đọc — `deployment_rules.rs:58-59` mới là nguồn thật, hardcode Rust
    const đúng Round 83's giá trị); (2) phát hiện SSH tunnel nghiên cứu có
    thể chết ngầm gây `transport error` giả dạng gate-stuck (đã thêm rule 7
    vào `kline-stream-gate-capacity-saga.md`); (3) phát hiện tooling gotcha
    thật: `--daily-profit-gate` KHÔNG đọc `--portfolio-minimum-hold-decisions`
    (`config.rs:110` hardcode compile-in, Round 87 dùng đúng `one_target`
    nên không bị ảnh hưởng). Chi tiết →
    `raw/researcher/round151-risk-fraction-sizing-mode-catastrophic-under-negative-edge.md`.
  - `--portfolio-atr-periods` (chu kỳ ATR khi protective-kind=`atr`) vẫn
    chưa biến thiên — mục duy nhất còn thật sự mở trong Rule 1, ưu tiên
    thấp (protective-kind hiện tại là `fractional`, không phải `atr`, nên
    lever này không áp dụng cho production hiện tại trừ khi đổi protective
    kind trước).
  - **BÀI HỌC QUY TRÌNH QUAN TRỌNG (2026-08-25):** trước khi bắt đầu bất kỳ
    Rule 1 investigation nào, **grep `raw/researcher/round8[7-9]*.md` và
    `round9[0-2]*.md` trước** — mục "Thứ tự ưu tiên" này được viết ngay sau
    Round 83 và chưa từng cập nhật lại sau khi Round 87-92 đóng gần hết
    đúng những câu hỏi nó liệt kê "chưa khai thác", khiến Round 151-162 lặp
    lại ~3 round công sức. Toàn bộ không gian Rule 1 "cổ điển" (hold, stop/
    take, tương tác, sizing-mode) giờ ĐÃ ĐÓNG — tương tự tình trạng Rule 2/3
    đã ghi ở mục 93. Rule 1 KHÔNG còn nghiễm nhiên ưu tiên hơn Rule 2/3 nữa;
    coi cả 2 nhóm là "gần cạn, chỉ còn ý tưởng thực sự mới mới đáng thử".
- **Rule 2/3 (tìm signal/chiến thuật Alpha mới): ƯU TIÊN THẤP HƠN, không bỏ
  hẳn.** Tỷ lệ thành công 0/15+ cơ chế đã test (RSI divergence, Ichimoku,
  Bollinger/Keltner squeeze, order-flow imbalance × nhiều biến thể, ema
  crossover trend-filtered, sweep base interval khác, v.v. — xem mục 3).
  Không gian tìm kiếm bằng bộ chỉ báo kỹ thuật chuẩn đã gần cạn ở khung 5m.
  Vẫn nên thử nếu có ý tưởng THỰC SỰ mới (không phải biến thể tham số của
  cái đã đóng), nhưng đừng dành phần lớn thời gian mỗi round cho hướng này
  nữa khi Rule 1 còn nhiều lever chưa thử.
- **Luôn dùng đúng `one_target`** cho mọi kết luận liên quan cấu hình
  Portfolio hiện tại (bài học Round 82 — `legacy_grid`/`legacy_selected_rule`/
  `capital_reports` không đáng tin, xem chi tiết trong skill
  `quant-research-loop`).
- **Sau mỗi lần triển khai 1 lever Portfolio-construction mới, quay lại
  kiểm tra production 1-2 ngày sau** để xác nhận xu hướng PnL thật có khớp
  dự đoán backtest không — chưa từng làm bước này (mới verify ngay-sau-deploy,
  chưa verify xu-hướng-vài-ngày-sau).

**Lý do (bối cảnh cho ai đọc sau):** Target 1 (lợi nhuận ổn định) vẫn CHƯA
đạt sau 83 round — 2 lever Portfolio-construction đã triển khai chỉ làm hệ
thống "thua lỗ chậm hơn/rẻ hơn", không biến lỗ thành lời (PF Alpha vẫn <1
mọi nơi). User hỏi trực tiếp "có nên thêm rule mới không" (2026-08-21) sau
khi nghe tổng kết 83 round — quyết định: không thêm rule, chỉ đổi thứ tự ưu
tiên nội bộ dựa trên tỷ lệ thành công đo được.
