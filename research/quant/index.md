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
  `finance-mw/research/quant/studies/portfolio-btc-optimization-log.md`). Re-validate cả 7: PF
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
  `docs/archive/legacy-handoff-agent.md`, chi tiết đầy đủ →
  `docs/reviews/bybit-5m-kline-ws-crash-loop.md`.

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
  `docs/archive/legacy-handoff-agent.md`.

- **Round 124 (2026-08-24) — Đóng phần theo dõi backfill Bybit (Round 120-123 saga), mở rộng bằng chứng gate 1-slot sang 4 route khác, loại trừ 1 giả thuyết nghi ngờ mới:** (1) Verify độc lập qua Redis: cả 2 route Bybit `recent_klines` chỉ trễ ~4.5 phút (bình thường cho 5m) và `pending_history_backfill` rỗng — backfill catch-up hoàn toàn, không cần round sau tiếp tục theo dõi mục này nữa. (2) Backtest Vortex Indicator (Round 121, vẫn chưa commit) thử lại vẫn bị chặn — nhưng giờ do 4 route Binance/Exness khác đang tự chạy historical-replay riêng (trùng đợt redeploy MW ~4h trước, `pending_history_backfill['5m']` có 508 candle trên Binance BTC, đứng yên tuyệt đối qua nhiều lần đọc) tranh đúng 1 slot `KlineService.Stream` — cùng root cause gate 1-slot đã biết (Round 122-123), không phải bug mới, chỉ mở rộng phạm vi biểu hiện; `recent_klines` live-tailing của cả 4 route này vẫn tươi bình thường, không phải data-staleness bug. Backtest Vortex tiếp tục dời sang round sau. (3) Điều tra phụ: WARN "Exchange revised a closed kline ... evaluation remains blocked" bắn ra ở MỌI lần đóng nến (100% quan sát được) ban đầu nghi là nguyên nhân thật của Target 2 stagnant — đọc code `trading_api.rs::record_closed_kline` xác nhận đây là thiết kế cố ý (chống lặp lại TRA-928 incident), evaluate vẫn xảy ra đúng 1 lần/candle ở lần đóng đầu tiên, KHÔNG phải nguyên nhân Target 2 — loại trừ, không cần round sau điều tra lại. Không có backtest mới/candidate mới round này (thời gian dồn hết vào điều tra production). File: xem entry Round 123/121 trong `docs/archive/legacy-handoff-agent.md` (không tạo file round riêng vì không có kết quả backtest mới để báo cáo).

- **Round 125 (2026-08-24) — Tìm ra bug hạ tầng thật mới (gRPC stream gate leak), SỬA LẠI chẩn đoán sai của Round 124:** đọc metric `finance_mw_grpc_requests_in_flight` trực tiếp từ MW xác nhận gate 1-slot `kline.KlineService/Stream` đang bị kẹt bởi 3 kết nối "in-flight" dù không worker nào đang replay — root cause: `timeout ... docker run` (cách round trước dùng để bound backtest CLI) chỉ kill CLI wrapper chứ không kill container thật, để lại kết nối gRPC leak mỗi lần thử. Xác nhận bằng thực nghiệm (kill đúng container → in_flight giảm 3→2 ngay). **Sửa lại Round 124's chẩn đoán "4 route Binance/Exness chiếm slot" — SAI**, vì `pending_history_backfill` là buffer Kafka out-of-order nội bộ không liên quan gì gRPC stream gate (đọc code xác nhận). Log Todo mới cho Codex (`[observability][medium][round 125]`, đầu `docs/archive/legacy-handoff-agent.md`) đề xuất thêm keepalive/idle-timeout cho gRPC server để tự giải phóng gate khi client chết. Đã sửa quy trình backtest tooling của skill cho các round sau (dùng `-d --name` + `rm -f`, không dựa vào `timeout` kill wrapper). Backtest Vortex Indicator (Round 121) vẫn dời tiếp — 2 slot leak cũ còn sót cần MW restart tự nhiên mới hết. Không có backtest/candidate mới round này (dồn thời gian điều tra hạ tầng, coi là "tìm ra bug mới" theo Rule 7).

- **Round 126 (2026-08-24) — Gate stream vẫn leak (không rush fix, cần cẩn trọng theo note Round 125), chuyển sang dọn dẹp `## Verify` backlog:** đã đóng 9 mục Verify tồn đọng sang Done qua verify độc lập thật (không chỉ đọc file): (1) follow-up Monday của Round102 XAU/Exness weekend false-alarm — PASS đầy đủ (checkpoint tươi ~4 phút, eval_count 795>689 baseline, container healthy 18h); (2) Bybit BTC risk-limit + full integration — re-confirm qua nhiều round liên tiếp đã ổn định; (3) OOM cgroup fix — re-check `restarts=0`, memory 104.9MiB/512MiB sau nhiều giờ backfill nặng; (4-9) batch 6 mục infra/credential-rotation 2026-08-22 (VictoriaMetrics/Redis/Trace panel/rename/Docker cleanup) — spot-check containers healthy 39h, không regression. `## Verify` giờ chỉ còn watcher note (standing, không phải task). Không có backtest/candidate mới round này (backtest tool vẫn bị block bởi gate leak, ưu tiên dọn backlog thay vì đợi vô thời hạn).

- **Round 127-129 (2026-08-24) — Implement + deploy fix keepalive cho gate leak (Round 125), xác nhận ĐÚNG nhưng KHÔNG đủ, tìm ra nguyên nhân thứ 2 thật sự đang chặn:** Round 127 implement `grpc.KeepaliveParams` (commit `1adff58`), full CI/deploy/verify production thành công (SHA khớp, PID fresh xác nhận qua `ps -o etimes`). Round 128-129 verify sau deploy phát hiện `in_flight` vẫn giữ ở 2 dù process hoàn toàn mới — loại trừ dead-client, điều tra sâu ra `GetOldestOpenTime` (dùng bởi `kline_sync_full`) mở stream KHÔNG giới hạn From/To chỉ để đọc 1 record, kết hợp `StartupTimeout=4h` của job đầu tiên sau restart worker — có thể giữ gate tới 4 giờ sau mỗi lần redeploy. Đã log Todo chi tiết + hướng fix, KHÔNG rush implement thêm (đã tốn 3 round liên tiếp cho vấn đề hạ tầng này, cần dừng lại). Backtest Vortex Indicator (Round 121) tiếp tục bị chặn tới khi có fix tiếp theo hoặc redeploy khác. Bài học quy trình: 1 finding hạ tầng có thể có NHIỀU nguyên nhân xếp chồng — đừng dừng điều tra chỉ vì tìm được 1 giải thích hợp lý, luôn verify bằng chứng thực nghiệm (fresh PID, in_flight thực tế) trước khi tuyên bố đã fix xong.

- **Round 130 (2026-08-24) — Quay lại research thực chất sau 3 round hạ tầng, cơ chế mới: realized-volatility expansion-regime filter (Rule 3, web research):** khác các filter đã thử (SMA/ADX trend, Bollinger/Keltner volatility-squeeze BREAKOUT) — đây là filter volatility layered lên entry đã có, không phải cơ chế entry mới. Implement `RealizedVolatilityRegimeFilterStrategy` (tái dùng `atr()` có sẵn), 2 composition wrap `candle_momentum`, 3 unit test mới xanh, full suite 126/126 xanh. Backtest thật vẫn bị chặn (gate Round 129 chưa tự giải phóng) — code giữ local uncommitted, chờ round sau khi gate rảnh. Cơ sở từ research ngoài: cùng nhóm "filter giảm drawdown không cần signal mới" như 2 lever Portfolio-construction thành công Round 80/83, lần này thử ở tầng Alpha.

- **Round 132-133 (2026-08-24) — Fix thứ 2 cho gate (timeout GetOldestOpenTime), verify thực nghiệm cho kết luận trung thực: fix đúng nhưng gate 1-slot vẫn là giới hạn dung lượng thật, không phải bug thuần túy:** implement/deploy/verify `context.WithTimeout(10s)` cho `GetOldestOpenTime` — bằng chứng: `requests_total` Stream leo lên 48 (trước đây tối đa 2, không bao giờ tăng), 1 request nhỏ (`--days 1`) chạy thành công 14s. Nhưng request lớn hơn (7/90/1825 ngày) vẫn bị treo do tranh chấp capacity=1 thật với traffic hợp lệ khác — không phải leak. Kết luận: 2 fix (Round 127 keepalive + Round 132 timeout) đã đóng đúng phần "leak", còn lại là giới hạn kiến trúc (1 slot) cần fix riêng nếu muốn backtest tool luôn dùng được ngay — không rush, cần review kỹ vì chạm memory-budget cgroup 512MiB. Bài học: đừng dừng lại ở "có vẻ đã fix" — luôn verify bằng request thật nhiều kích cỡ khác nhau trước khi tuyên bố xong.

- **Round 139-141 (2026-08-24) — TÌM RA ROOT CAUSE THẬT của gate saga (Round 122-138) qua goroutine dump thật, không còn suy đoán:** Round 139 wire up `net/http/pprof` (comment code cũ tự nhận đã làm nhưng thực ra chưa — xem Round 125). Round 141 dùng ngay: `debug/pprof/goroutine?debug=2` lộ ra 2 goroutine kẹt đúng 459 phút = khớp tuổi process (kẹt từ lúc boot). 1 goroutine giữ slot gate, kẹt ở HTTP/2 flow-control (`writeQuota.get`) vì client (rất có thể `live-action-bybit-perpetual-future-btc-usdt`, khớp thời điểm log 08:15:13Z) ngừng đọc stream — KHÔNG phải dead connection nên 2 fix trước (keepalive Round 127, timeout Round 132) đều đúng nhưng không bắt được loại lỗi này. Goroutine còn lại kẹt chờ ở `Acquire()` từ lúc boot — giải thích chính xác `in_flight=2` đứng yên suốt nhiều round. Phát hiện phụ: DB connection Postgres cũng bị giữ mở 459 phút theo. Chưa fix (cần sửa client-side finance-live-action hoặc thêm `MaxConnectionAge` phía MW, cả 2 đều cần round riêng cẩn trọng). Chi tiết đầy đủ → `docs/reviews/kline-stream-gate-capacity-saga.md`. Bài học: pprof là công cụ đúng cho loại bug này ngay từ đầu — 15+ round trước đó đoán mò vì thiếu nó.

- **Round 206 (2026-08-28) — LỖI ĐO LƯỜNG THẬT trong ledger, tìm bằng bằng
  chứng production thuần (không chạy backtest): liquidation chỉ được đánh giá
  trên mark-price feed LIVE (`trading_modes.rs:1835-1872`, doc comment nói rõ
  candle close bị cố tình từ chối làm input). Vị thế mở trong historical replay
  không hề được kiểm tra liquidation; mark đầu tiên sau khoảng trống đóng nó
  tại giá lúc đó và `close_position` không cap lỗ ở margin. Đo được trên
  binance BTC: **5 liquidation, toàn short, đóng tại đúng 2 mốc wall-clock**,
  vượt ngưỡng `isolated_liquidation_price` **+3.9% đến +17.1%**, lỗ
  **1.16x-2.58x margin**. Đối chứng binance XAU có 1 liquidation ngoài mốc
  restart đóng đúng **+0.0%** so với ngưỡng ⇒ công thức đúng, lỗi nằm ở khoảng
  trống feed. **Tác động nghiêm trọng nhất: cái ngày 2026-08-25 rơi trúng
  `mtf_stochastic_4h_1d_sma50`** (deployment Round 189, cơ chế DUY NHẤT từng
  được validate là có edge thật) — gross_profit ledger live y hệt ledger replay
  (2.6785), toàn bộ chênh lệch là đúng khoản −1.2898 đó, kéo PF live
  **3.28 → 1.27**, và đây đồng thời là ledger đếm maturity. Hai phát hiện phụ:
  (1) `PERFORMANCE_CONFIDENCE_TRADES=20` không phân biệt tần suất — đo được
  **~0.28 trade/tuần** (12 trade trải 43.4 tuần, so với ước lượng ~0.35 của
  Round 189) ⇒ strategy này còn **~25-28 tuần** nữa mới có `strategy_weight`
  khác 0, tức edge duy nhất đóng góp **đúng bằng 0** tới khoảng 03/2027 trong
  khi 2 strategy PF 0.35-0.94 giữ 100% trọng số; (2) demo ledger exness chạy
  `leverage=1`/`mmr=0.0` nên **không bao giờ liquidate được** — quy tắc validate
  cross-broker của cả chương trình đang so ledger 10x có liquidation với ledger
  1x không có. Chưa implement (Codex available). File:
  `round206-replay-gap-liquidations-overshoot-margin.md`.

- **Round 207 (2026-08-28) — durable Portfolio trade log đã VERIFY được trên
  production, và lần đầu tiên có đường đo Target 3 KHÔNG qua backtest:** commit
  `e452083` đã push và đã nằm trong image đang chạy `7a15b76`; probe của Codex
  hôm 27/08 còn thấy `ZCARD=0` nên entry bị giữ lại — nay đã có dữ liệu thật.
  5/6 route có key `trades:<broker>.<market>.<base>.<quote>` + `:payloads` với
  **cardinality khớp tuyệt đối** (9/9, 6/6, 3/3, 6/6, 3/3), payload đủ schema,
  `event_id` SHA-256 deterministic ⇒ replay idempotent, không chứa credential.
  binance XAU vắng key là **đúng kỳ vọng** (route frozen, khớp Round 206).
  **Đường đo Target 3 mới:** mỗi Portfolio close ghi đúng 1 record/capital rule
  (3 rule) ⇒ `closes = ZCARD/3`. Baseline cửa sổ 25.2h
  (2026-08-27T14:39Z → 2026-08-28T15:50Z): binance BTC 3 close (~20/tuần),
  exness BTC 2 (~13.3), bybit BTC 2 (~13.3), exness XAU 1 (~6.7), bybit XAUT 1
  (~6.7), binance XAU 0. **Là baseline chứ KHÔNG phải kết luận** — 1-3 sự kiện
  mỗi route; con số /tuần chỉ là phép chia hiển thị. Việc cần làm: đọc lại đúng
  6 key đó sau ~7 ngày rồi mới so được với Round 92 (~9.3/tuần 5 năm,
  ~7.2-7.3/tuần 18 tháng). Phát hiện phụ (low): `trade_log.rs` không có trim/TTL
  trên `trades:*` — fact table tài chính append-only nằm vĩnh viễn trong RAM
  Redis, ~10-15 MB/năm cho cả 6 route, chưa gấp nhưng nên là quyết định có chủ
  đích. **Ghi chú phương pháp:** hai vòng liên tiếp (206, 207) kết luận từ bằng
  chứng production mà không chạy backtest container — đều chính đáng, nhưng vòng
  sau nên quay lại một thí nghiệm backtest có giới hạn để thread nghiên cứu
  không trôi thành công việc verification thuần. File:
  `round207-durable-trade-log-verified-first-live-target3-measurement.md`.

- **Round 208 (2026-08-28) — ĐÓNG HẲN câu hỏi "có nên backfill XAU/binance
  không": lịch sử ngắn là TRẦN DỮ LIỆU CỦA SÀN, không phải lỗ hổng của ta.**
  XAU/binance bắt đầu `2025-12-11` trên **cả 8 interval** giống hệt nhau (260
  ngày); exness XAU 1.829 ngày; bybit XAUT 504 ngày. Bằng chứng quyết định:
  binance BTC và binance XAU đăng ký **cùng transaction, khớp tới micro giây**
  (`2026-08-11 04:14:30.840671+00`), cùng pipeline backfill — BTC lấy đủ 5 năm,
  XAU dừng ở 260 ngày. Dấu hiệu lặp lại độc lập trên bybit (BTC 1.829 vs XAUT
  504). `2021-08-26` chỉ là mốc retention 5 năm dùng chung, không phải giới hạn
  availability. **Hệ quả:** trần XAU/binance là cấu trúc, tới ~12/2028 mới có 3
  năm dữ liệu 4h; kết luận "không có strategy validate được cho XAU/binance"
  (Round 203/205) là vĩnh viễn chứ không tạm thời; **cấm dùng binance XAU làm
  bằng chứng chính cho candidate vàng**. Đề xuất chưa validate: thay bằng
  **bybit XAUT** (3.026 nến 4h, gần gấp đôi binance XAU, chưa vòng nào dùng) làm
  cross-check vàng thứ hai — nhưng nó là spot Tether Gold, cần kiểm tra có bám
  XAU đủ sát không, **đó là thí nghiệm backtest vòng sau**. Cross-validate được
  Round 205 từ nguồn độc lập (1.562 vs 1.543 sau 3 ngày = đúng mức tích luỹ dự
  kiến). File: `round208-xau-binance-history-is-a-venue-horizon-not-a-backfill-gap.md`.

- **Round 209 (2026-08-28) — bybit XAUT CHẤP NHẬN CÓ ĐIỀU KIỆN làm cross-check
  vàng thứ hai, kèm tự sửa con số của Round 208.** Log-return 4h trên bar đã
  căn khớp: `bybit XAUT vs exness XAU` Pearson **0.9915**, Spearman 0.9867, TE
  0.0850%/bar, direction agreement **95.06%** (n=2.132) — so với cặp chương
  trình đã chấp nhận `binance XAU vs exness` 0.9954/0.9916/0.0724%/97.63%. Cùng
  đẳng cấp ⇒ qua bài test đầu. **Hai điều kiện:** (1) 819/3.026 bar bybit
  (27,1%, chủ yếu T7+CN) không có đối ứng exness và có volume ~1/3, biên độ
  ~1/4 ⇒ **phải loại khi falsify cross-broker**; (2) basis trôi ~0,4%/15 tháng
  ⇒ ngưỡng theo LEVEL không so được, return/range thì vô hại. **Sửa Round 208:**
  lợi thế mẫu dùng được là **+41% (2.207 vs 1.562)**, không phải ~94% như số thô
  vòng đó ghi; cái thật sự giá trị là **8 tháng lịch sử vươn xa hơn**. Stack
  vàng từ đây: exness (authoritative) × bybit XAUT (cross-check) × binance XAU
  (chỉ confirmation). **Chưa chứng minh:** tương quan return là điều kiện cần
  chứ không đủ — vòng sau phải sweep candidate ĐÃ ĐÓNG (Donchian r88, Keltner
  r91, Connors RSI(2) r204) trên bybit weekday-only để xem nó có tái tạo được
  falsification đã biết không. **Blocker cần nêu tên để hết trôi:** image
  `finance-research-local:latest` chưa tồn tại trên máy này, phải
  `docker build -f docker/Dockerfile-research` — đó là hành động đầu tiên của
  vòng sau. File: `round209-bybit-xaut-tracks-spot-gold-conditionally-accepted.md`.

- **Round 210 (2026-08-28) — bybit XAUT QUA bài calibration (0 false promotion),
  và chính lần chạy đó cho thấy PF theo từng split ở 4h bị NHIỄU chi phối.**
  Hai sweep Docker cùng engine/interval/cửa sổ 500 ngày, chỉ khác nguồn giá:
  bybit XAUT 2.999 nến (1.799/600/600) vs exness XAU 2.191 nến (1.315/438/438),
  chênh 808 nến đúng bằng phiên cuối tuần. **Kết quả 1 — calibration ĐẠT:** 9/9
  candidate thuộc 3 hướng đã đóng (Donchian r88, Keltner r91, Heikin-Ashi r93)
  vẫn đóng; **không candidate nào vượt PF>1 cả ba split trên bất kỳ nguồn nào**;
  0 promotion sai ⇒ bybit XAUT dùng được làm falsifier. **Kết quả 2 — nhưng con
  số sau các verdict thì lệch nhau lớn:** câu hỏi nhị phân "PF>1?" **lệch ở
  11/24 ô (45,8%)**; khoảng lệch PF tương đối trung bình **45,0%**, giảm còn
  **18,3%** ở ô có **≥30 trade cả hai nguồn** và tăng lên **53,8%** ở ô dưới 30
  trade; ô tệ nhất `keltner_reversion_20_2_0` validation **1,83 vs 0,22** trên
  13 và 5 trade. Hai chuỗi tương quan 0.9915 (Round 209) mà PF từng split lệch
  tới 8 lần, và khoảng lệch co lại theo số trade ⇒ dấu hiệu của nhiễu, không
  phải của nguồn giá. **ĐỔI THỰC HÀNH (chỉ research, không implement): PF của
  một split có dưới ~30 trade không mang thông tin dùng được — không ghi thành
  lead, không xếp hạng candidate theo nó, không gọi là "near-miss".** Điều này
  vô hiệu hoá các lead kiểu Round 205 (18/7/9 trade) và Round 114. Rào
  "cả-ba-split-cả-hai-broker" vẫn đứng vững vì nó là phép hội của nhiều test yếu.
  **Kết quả 3 — weekend drag đã định lượng:** T7+CN = 28,6% số bar nhưng chỉ
  12,3% tổng biên độ (0,43x); CLI **không có** bộ lọc weekday nên điều kiện của
  Round 209 chưa thể đáp ứng ⇒ quy tắc diễn giải: **fail** trên bybit full-series
  **không phải** falsification sạch, còn **pass** thì mạnh hơn exness tương ứng.
  Vòng này quy tắc đó chưa cắn: PF bybit không thấp hơn exness một cách hệ thống.
  **Chưa chứng minh:** calibration mới chỉ test negative — chưa chứng minh bybit
  chấp nhận đúng một winner, vì chương trình chưa có positive nào ở 4h XAU để
  đối chiếu. File: `round210-bybit-calibration-passes-but-per-split-pf-is-noise.md`.

- **Round 211 (2026-08-29) — chỉ đổi CỬA SỔ đã làm PF ở ô mẫu lớn dịch ~30%:
  rào hội (conjunction) thì ổn định, từng thành phần của nó thì không.** Cùng
  nguồn/engine/interval (exness XAU 4h), chỉ đổi `--days` 500 → 1800 (2.191 →
  7.880 nến). **Khoảng dịch PF tương đối trung bình 47,6%** trên 23 ô; **29,9%**
  nếu chỉ xét ô có **≥100 trade ở CẢ HAI** cửa sổ; **11/23 ô (48%) đảo luôn câu
  trả lời nhị phân "PF>1?"**. Bốn ô mẫu lớn: `heikin_ashi_momentum_1` train
  0,88→0,58 (316→1.137 trade, lệch 34,1%), holdout 0,58→0,86 (32,6%);
  `heikin_ashi_momentum_3` train 1,17→0,64 (132→466 trade, 45,3%) — **3/4 ô mẫu
  lớn tệ đi** trên cửa sổ 5 năm. **Đây là cơ chế KHÁC với Round 210:** ở đó
  khoảng lệch co lại khi số trade tăng (đúng kiểu nhiễu lấy mẫu); ở đây ô có
  300-1.100 trade vẫn dịch 30-45% khi đổi cửa sổ ⇒ **phụ thuộc regime, tăng mẫu
  không chữa được**. Ghép hai vòng: ở cùng cỡ mẫu, **đổi cửa sổ (29,9%) làm PF
  dịch mạnh hơn đổi nguồn giá (18,3%)**. **Thứ vẫn đứng yên:** trên cửa sổ 1.800
  ngày vẫn **không candidate nào vượt PF>1 cả ba split** — giống hệt cả run
  500 ngày lẫn run bybit của Round 210. Qua 2 nguồn giá và 2 cửa sổ chênh 3,6
  lần dữ liệu, rào cả-ba-split cho **cùng một verdict mọi lần**, trong khi từng
  thành phần đảo ở gần một nửa số ô. **Hệ quả thực hành (chỉ research):** (1)
  không bao giờ trích một PF-một-split như thuộc tính của strategy — nó là thuộc
  tính của strategy × cửa sổ × cách chia; Round 210 đã chốt điều này cho mẫu <30
  trade, vòng này mở rộng lên mẫu 100+; (2) ưu tiên cửa sổ dài **vì độ phủ
  regime, không phải vì chính xác hơn** — kết quả 500 ngày đẹp có thể chỉ là
  regime thuận; (3) **giữ nguyên rào cả-ba-split-cả-hai-nguồn**, đây là thước đo
  duy nhất đã sống sót qua cả đổi nguồn lẫn đổi cửa sổ mà không đổi verdict.
  **Giới hạn:** hai cửa sổ lồng nhau nên đây là sensitivity chứ không phải
  replication độc lập; nhóm 30-99 trade chỉ có 2 ô nên không có trọng số; chưa
  phân tích regime để giải thích vì sao dữ liệu cũ tệ hơn. File:
  `round211-pf-is-not-portable-across-windows-even-at-large-samples.md`.

- **Round 212 (2026-08-29) — LỖI ĐO LƯỜNG: `profit_factor` KHÔNG tính funding
  trong khi PnL có tính, 8,1% số ô "PF>1" thật ra đang lỗ.** Phát hiện khi truy
  một mâu thuẫn trong chính output của vòng: `ema_crossover_12_26` ở cửa sổ
  1.800 ngày đọc ra **PF 1,01 nhưng PnL −0,10**. Đọc code: `profit_factor =
  gross_profit/gross_loss` (`finance-research/src/sweep.rs:58-59`), hai bộ đếm
  đó chỉ được ghi trong `close_position` theo dấu PnL của trade đã đóng; còn
  funding settle ở đường khác (`finance-core/src/trading_modes.rs:2131-2135`)
  làm `realized_pnl -= paid` và `funding_paid += paid` mà **không hề chạm**
  `gross_profit`/`gross_loss`. Tức bảng sweep in **PnL có funding cạnh PF không
  có funding**. Đo trên 924 ô candidate×split×window của 4 cửa sổ: 270 ô báo
  PF>1, trong đó **22 ô (8,1%) có PnL âm**; 17 ô ngược lại. **Thiên lệch có
  hướng:** funding tích theo thời gian giữ lệnh ⇒ metric ưu ái đúng loại
  candidate giữ lệnh lâu — cũng chính là hướng Round 80/83/92 đẩy production
  (hold dài hơn, stop rộng hơn). **KHÔNG kết luận Round 80/83/92 sai** — các
  vòng đó dùng `one_target` và số PnL chứ không dùng cột PF này; nhưng nên
  kiểm lại các lever đó bằng thước đo có tính funding trước khi nới thêm.
  **Cũng có thể đây là quy ước cố ý** (profit factor cổ điển định nghĩa trên
  kết quả trade, tách riêng carry) — chính vì vậy ghi nhận là DATA-ISSUE để
  quyết định có chủ đích, không tự promote một bản sửa. **Sản phẩm phụ — profile
  ổn định 4 cửa sổ (500/900/1.350/1.800 ngày) trên nguồn vàng authoritative:**
  trong 77 candidate, **68 không qua rào cả-ba-split ở cửa sổ nào**, 4 qua 1 cửa
  sổ, 3 qua 2, 2 qua 3, và **không candidate nào qua cả 4**. Hai ứng viên 3/4:
  `ichimoku_cloud_9_26_52_26` (min-trade 3/4/7/10 — dưới sàn 30 trade của Round
  210, là nhiễu) và `ema_crossover_12_26` (**bị bác bởi chính lỗi nó phơi ra**:
  qua rào PF ở 3/4 cửa sổ nhưng chỉ qua rào PnL>0 ở 1/4). Cửa sổ lồng nhau nên
  đây là sensitivity chứ không phải replication. File:
  `round212-profit-factor-excludes-funding-8pct-of-passing-cells-lose-money.md`.

- **Round 213 (2026-08-29) — ĐO TRỰC TIẾP funding (và SỬA khẳng định sai của
  Round 212), và: CHI PHÍ mới là ràng buộc quyết định ở vàng 4h, không phải
  chọn indicator.** Chạy lại đúng sweep với `--funding-rate-bps 0` rồi lấy hiệu:
  **222/231 ô đổi PnL, KHÔNG ô nào đổi PF** (mọi delta đúng bằng 0,00) — xác
  nhận sạch sẽ nhất có thể cho phần đọc code của Round 212. Mức độ nghiêm trọng:
  |funding| chiếm **trung vị 16,4%** của |PnL| báo cáo, p90 100%, max 600%;
  **vượt** cả |PnL| ở 22 ô (9,9%) và **đảo dấu** PnL ở 25 ô (11,3%).
  **⚠️ SỬA ROUND 212:** vòng đó viết "thiên lệch có hướng, ưu ái candidate giữ
  lệnh lâu" — **SAI**. Funding có dấu theo chiều lệnh, short được NHẬN, nên nó
  là **credit ở 114 ô và cost ở 108 ô**: không hề có thiên lệch lạc quan hệ
  thống. Cách mô tả đúng còn khó chịu hơn: PF và PnL lệch nhau một lượng **lớn,
  hai chiều và không tương quan với tín hiệu**. **Không lật lại kết luận cũ nào**
  — không candidate nào đổi verdict cả-ba-split khi bỏ funding, vì rào đọc PF mà
  PF chưa từng thấy funding. Lỗi phụ tìm được trong cùng phép hiệu:
  `taker_imbalance_*` báo **0 trade nhưng PnL ±1,62**, về đúng 0,00 khi funding=0
  — đó là carry trên vị thế mở chưa đóng, bị ghi vào `realized_pnl`.
  **PHẦN 2 — xác nhận định lượng giả thuyết "trần chi phí" của Round 93 trên
  vàng:** cùng sweep với `--fee-bps 0 --slippage-bps 0 --funding-rate-bps 0`,
  số candidate qua rào cả-ba-split đi từ **2/77 (chi phí thật) lên 14/77 (không
  chi phí)** — **12 candidate lật fail→pass chỉ nhờ bỏ 7bps round-trip**, nhiều
  cái mẫu lớn: `heikin_ashi_momentum_1` 0,58/0,95/0,86 → 1,03/1,61/1,18 (1.137
  trade train), `candle_momentum_10bps` (1.540), `macd_trend_5_13_5` (705),
  `elder_ray_13` (608). **Thành tích 0/15+ cơ chế mới không phải 15 ý tưởng tồi
  — mà là MỘT ràng buộc chi phí gặp lại 15 lần.** **Không có gì promotable**
  (backtest miễn phí chi phí thì không giao dịch được). **Hướng mới, chưa test
  bao giờ:** (1) **maker thay vì taker** — ledger đã model sẵn `maker_fee_bps`
  2,0 vs `fee_bps` 5,0 và `liquidity_role`, hơn nửa chi phí round-trip là phần
  bù taker, chưa vòng nào so; (2) ít lệnh hơn/lệnh to hơn — chi phí scale theo
  số lệnh còn edge thì không; (3) đưa **break-even cost** thành màn sàng lọc bậc
  một (sweep ở 0/2/5/7bps) thay vì một pass/fail ở đúng mức chi phí production.
  File: `round213-funding-measured-and-cost-is-the-binding-constraint-on-gold.md`.

- **Round 214 (2026-08-29) — MAKER KHÔNG PHẢI đòn bẩy; SLIPPAGE mới là thứ chi
  phối, không phải phí.** Round 213 đề xuất chuyển taker→maker vì "hơn nửa chi
  phí round-trip là phần bù taker". Test bằng cách chỉ đổi `--fee-bps`, giữ
  nguyên slippage 2bps và funding 1bps: số candidate qua rào cả-ba-split đi
  **2 → 3 → 4** ở mức phí **5 → 2 → 0 bps**. Bỏ **toàn bộ** phí (10bps
  round-trip, tính cả hai đầu lệnh) chỉ được thêm 2 candidate; bước taker→maker
  được **đúng 1** candidate (`sma200_trend_filtered_rsi_2_10_90`, nhích train
  0,99 → 1,05 trên 48 trade) — chạm ngưỡng chứ không phải được mở khoá.
  **⚠️ Rút lại đề xuất maker của Round 213** (đã thêm banner correction).
  **Phân rã chi phí qua 4 run:** production (5/2/1) = 2 pass; bỏ phí (0/2/1) = 4;
  bỏ funding (5/2/0) = 2 (Round 213, không đổi verdict nào); bỏ hết (0/0/0) = 14.
  ⇒ **funding đáng 0 candidate, phí đáng +2 cho 10bps, còn SLIPPAGE đáng ~+10
  chỉ với 4bps round-trip.** Số hạng chi phí nhỏ nhất gánh gần như toàn bộ hiệu
  ứng. **Cơ chế khả dĩ (CHƯA kiểm chứng):** phí là phép trừ thuần, còn slippage
  dịch chính GIÁ khớp nên dời luôn mức kích hoạt stop/target — phụ thuộc đường
  đi, không chỉ bào mòn kết quả. **Hệ quả quan trọng nhất:** mọi kết luận của
  chương trình từ trước tới nay đều dựa trên default `--slippage-bps 2` mà chưa
  ai đối chiếu với fill thật, trong khi pass count nhạy với nó **gấp ~5 lần mỗi
  bps** so với phí — một con số hợp đồng đã biết chắc. **Hướng đúng từ đây:**
  (1) đo slippage thật trên các instrument này ở size thật; (2) giảm phơi nhiễm
  slippage (ít lệnh hơn/lệnh to hơn, entry ít hung hăng, lệnh chờ) thay vì đàm
  phán bậc phí; (3) báo cáo **break-even cost** cho từng candidate thay vì một
  pass/fail duy nhất. File:
  `round214-maker-is-not-the-lever-slippage-dominates-not-fees.md`.

- **Round 215 (2026-08-29) — FACTORIAL 2x2: không có đòn bẩy chi phí nào cả;
  hiệu ứng là SIÊU CỘNG TÍNH (+12 đo được vs +3 nếu cộng tuyến tính) ⇒ ĐÓNG
  hướng giảm chi phí.** Round 87 đã ghi bài học "lever phải test factorial đầy
  đủ, không giả định cộng tính"; Round 214 đã không áp dụng, vòng này áp dụng.
  Chạy nốt 2 ô còn thiếu, funding giữ cố định 1,0bps — số candidate qua rào
  cả-ba-split: **(phí 5/slip 2) = 2** (production), **(5/0) = 3**, **(0/2) = 4**,
  **(0/0) = 14**. Tách hiệu ứng chính từ góc production: **bỏ phí +2, bỏ slippage
  +1, bỏ cả hai +12**, trong khi cộng tuyến tính chỉ dự đoán +3 — khuếch đại 4
  lần. Bỏ thêm funding ở góc (0,0) được **+0**, khớp Round 213.
  **⚠️ SỬA ROUND 214:** khẳng định "slippage gánh gần như toàn bộ, ~+10 cho
  4bps" là **SAI** — slippage một mình chỉ đáng **+1**, phí đáng +2 (thứ tự cũng
  ngược lại). Round 214 lấy hiệu giữa các run **không trực giao** rồi gán phần dư
  cho slippage; phần dư đó chính là **số hạng tương tác** mà nó tự nói là chưa
  đo. Kết luận còn lại của Round 214 (maker không phải đòn bẩy) vẫn đứng.
  **Vì sao siêu cộng tính:** rào là phép HỘI của 3 split; bỏ một số hạng chi phí
  đưa nhiều candidate qua được 1-2 split nhưng gần như không candidate nào qua
  đủ 3 — bỏ cả hai mới đẩy hàng loạt qua cùng lúc. Đây không phải tính chất của
  slippage hay phí mà là tính chất của việc đo bằng phép hội quanh ngưỡng — cùng
  cấu trúc đã làm rào này bền vững ở Round 210/211. Đối chiếu Round 87 (hold ×
  stop/take **dưới** cộng tính, 56-62% mức tuyến tính): cùng hệ thống, dấu ngược
  nhau, trục khác ⇒ **không được giả định chiều nào cả**.
  **Hệ quả vận hành (lý do REJECTED):** ép phí về **0** (bất khả) được +2; triệt
  tiêu slippage (bất khả) được +1; chỉ khi bỏ **gần như toàn bộ** ma sát mới lên
  14 — thế giới đó không tồn tại. Kịch bản thực tế tốt nhất (phí maker, slippage
  giảm nửa) nằm giữa hai góc +1 và +2, tức **xấp xỉ không thêm candidate nào**.
  Thứ còn sống từ Round 213 là phần **chẩn đoán** (các cơ chế có gross edge
  dương nhưng nhỏ hơn tổng ma sát), không phải phần **kê đơn**. Câu hỏi mở duy
  nhất còn đáng theo: **slippage thật là bao nhiêu** trên các instrument này ở
  size thật — vì cả cái factorial này là một MÔ HÌNH chi phí, không phải phép đo
  chi phí. File: `round215-cost-effect-is-super-additive-no-single-lever-exists.md`.

- **Round 216 (2026-08-29) — ở interval production 5m: 31% candidate có gross
  edge dương, và ma sát giết 96% trong số đó.** Mô hình chi phí của Round
  213-215 dựng hoàn toàn ở 4h, nên nó cho một dự đoán kiểm chứng được ở **5m**
  (interval production thật, sweep chưa từng chạy): số trade mỗi candidate gấp
  ~5 lần ⇒ pass ở chi phí production phải **giảm** còn pass ở chi phí 0 thì
  không ⇒ **khoảng cách phải giãn ra**. Nếu khoảng cách giữ nguyên hoặc thu hẹp
  thì câu chuyện chi phí là thiếu. **Đo được (exness XAU 5m, 365 ngày, 70.852
  nến):** pass ở chi phí production **1/77**, ở chi phí 0 **24/77** ⇒ khoảng
  cách **23**, so với **12** ở 4h (2/77 và 14/77). Dự đoán đúng chiều. Nói cách
  quan trọng nhất: **24/77 (31%) có gross edge dương cả ba split, đúng 1 sống
  sót qua ma sát — ma sát giết 96% tập gross-positive.** 5m không thiếu tín
  hiệu; nó thiếu tín hiệu sống nổi qua chi phí thu hoạch. **Candidate sống sót
  duy nhất xác nhận đúng cơ chế và bị chính luật của chương trình loại:**
  `sma10_trend_filtered_fibonacci_golden_zone_100` sống vì nó gần như không trả
  phí — 47/18/16 trade so với **trung vị 1.531 trade train** của tập
  gross-positive; nhưng validation (18) và holdout (16) **đều dưới sàn 30 trade
  của Round 210**, và nó là biến thể của hướng Fibonacci Golden Zone đã đóng ở
  Round 105-106, xuất hiện lại ở interval khác trên mẫu mỏng — đúng hình dạng
  false-positive mà Round 205 cảnh báo. Ghi nhận nó như **kẻ sống sót của bài
  test chi phí** nhưng **từ chối nó như một candidate**; cả hai đều đúng.
  **Giới hạn:** hai run khác cửa sổ lịch (1.800 ngày ở 4h vs 365 ngày ở 5m) nên
  **không** phải so sánh interval có kiểm soát — đại lượng được kiểm soát là
  khoảng cách production-vs-zero-cost **trong từng** interval, mỗi cái đo trên
  cùng một bộ dữ liệu. Và giới hạn Round 215 vẫn nguyên: `fee_bps 5.0 /
  slippage_bps 2.0` là **mô hình**, không phải phép đo — `deployment_rules.rs`
  cho thấy production dùng đúng cặp mô hình đó, nên PnL production cũng đứng
  trên cùng giả định chưa kiểm chứng. **Không mở hướng mới:** suy luận hiển
  nhiên "chạy interval chậm hơn để trả ít ma sát hơn" đã bị Round 92 đóng vì
  biên Target 3 (≥7 lệnh/tuần) quá mỏng. File:
  `round216-at-5m-friction-kills-96-percent-of-gross-positive-candidates.md`.

- **Round 217 (2026-08-29) — ĐO ĐỘ HỤT, không chỉ đo đỗ/trượt: tín hiệu vàng 5m
  CÓ edge dương ngoài mẫu, nhưng nhỏ hơn ma sát khoảng MỘT BẬC ĐỘ LỚN (~8x).**
  Suốt 200+ vòng chương trình chỉ hỏi "candidate này có qua không", chưa vòng nào
  hỏi **"trượt bao xa"** — mà hụt 20% thì đáng đánh tiếp, hụt 800% thì không.
  Tính được từ 2 run đã lưu của Round 216, **không cần giả định sizing/notional**
  vì ma sát đo bằng phép hiệu: `ma sát/lệnh = (PnL chi phí 0 − PnL production)/số
  lệnh`. Trên 193 ô có **≥30 trade**: **ma sát/lệnh là một khoản thuế gần như
  hằng số — trung vị 0,00701, khoảng p10-p90 chỉ chênh 4%** (lần đầu được *đo*
  chứ không phải giả định). **Tỉ lệ edge/ma sát: trung vị 0,035** — candidate
  điển hình kiếm được **3,5%** số ma sát nó trả; p90 mới 0,674; chỉ 14/193 ô
  vượt 1; và **không candidate nào vượt 1 trên cả ba split** (duy nhất
  `donchian_breakout_200` được 2/3). **Ngoài mẫu (holdout, ≥30 trade), theo họ cơ
  chế:** breakout +0,00086 (82% ô dương, n=11), trend/momentum +0,00043 (83%,
  n=23), reversion +0,00037 (61%, n=18), other +0,00009 — so với ma sát 0,00701.
  **Hai điều cùng đúng:** (1) **tín hiệu là THẬT** — 82-83% ô breakout và
  trend/momentum dương *ngoài mẫu*, sau ngần ấy vòng "không cái nào chạy" thì
  điều này đáng nói thẳng: các cơ chế không phải nhiễu; (2) **nó nhỏ hơn ma sát
  ~8 lần** (họ tốt nhất đạt tỉ lệ 0,12). **Khoảng hụt 8x không thể lấp** bằng
  tinh chỉnh execution (Round 215 đã đo: cải thiện chi phí thực tế đáng ~0
  candidate), bằng dò tham số, hay bằng indicator tốt hơn (0/15+). Chương trình
  đang dùng công cụ 1,1x để lấp khe 8x. **Một "phát hiện" tôi suýt ghi rồi bỏ:**
  bảng xếp hạng theo tỉ lệ nhìn như một câu chuyện họ-cơ-chế sạch sẽ (breakout
  đứng đầu, reversion đội sổ) — nhưng **6/8 ô đầu bảng là `train`**; tính lại
  chỉ trên holdout thì câu chuyện tan: reversion có trung vị **dương** và nằm
  trong khoảng 2x của trend/momentum. Ghi lại để vòng sau không suy ra lại từ
  cùng cái bảng đó. **Giới hạn:** chỉ đo exness XAU 5m/365 ngày (4h ít bị chi
  phí trói hơn, chưa tính); trung vị theo họ là trung vị trên 10-23 ô, không có
  kiểm định; và ma sát 0,00701 là **của mô hình** (`fee 5 / slip 2 / funding 1`)
  chứ chưa từng đối chiếu fill thật — nhưng kể cả ma sát thật chỉ bằng nửa mô
  hình thì khe vẫn 4x, vẫn không lấp được, nên kết luận sống sót qua bất định đó.
  File: `round217-the-gap-is-8x-not-marginal-edge-per-trade-vs-friction-per-trade.md`.

- **Round 218 (2026-08-29) — KHE HỤT PHỤ THUỘC INTERVAL: 8x ở 5m, ~3x ở 1h,
  ~1,5x ở 4h. Con số "8x" của Round 217 là số của RIÊNG 5m.** Ma sát là thuế
  theo lệnh, còn biên độ một nến 4h lớn hơn nến 5m nhiều — nếu edge/lệnh tăng
  theo độ dài nến mà ma sát thì không, tỉ lệ phải cải thiện theo interval.
  **Đo được (cùng cửa sổ 365 ngày, holdout, ≥30 trade):** ma sát/lệnh
  **0,00701 / 0,00702 / 0,00703** ở 5m / 1h / 4h — **giống nhau tới 3 chữ số
  thập phân**, tức đúng là thuế theo lệnh, độc lập thời gian giữ (giờ đã *đo*
  trên ba interval chứ không còn giả định). Edge/lệnh thì không phẳng:
  **+0,00040 (5m) → +0,00232 (1h)**, gấp **5,8 lần** trên cùng lịch ⇒ tỉ lệ
  **0,057 → 0,331**. **Số 4h/365 ngày đọc ra −0,179 nhưng đó là hiện tượng cửa
  sổ ngắn — đã kiểm chứng chứ không báo cáo bừa:** chỉ 12 ô, trung vị 68 trade
  (đúng bẫy mẫu nhỏ Round 210-211); tính lại trên cửa sổ **1.800 ngày** (40 ô,
  trung vị 110 trade) cho **edge/lệnh +0,00470, tỉ lệ +0,659, 70% ô dương** —
  **tỉ lệ tốt nhất đo được ở bất cứ đâu**. **Bức tranh sửa lại:** 5m tỉ lệ 0,057
  (hụt ~18x), 1h 0,331 (~3x), 4h **0,659 (~1,5x)**. 1,5x là loại bài toán khác
  hẳn 8x — nằm trong tầm những thứ chương trình đã chứng minh là dịch được
  (Round 80 giảm ~34% lỗ bằng một tham số hold, Round 83 thêm ~41% bằng độ rộng
  stop/take). **Và nó giải thích được điều chương trình quan sát mà chưa lý giải
  nổi: cơ chế DUY NHẤT từng validate được — swing 4h/1d MTF stochastic (r17/172/
  189) — nằm ở 4h.** Đó không phải may mắn mà là chỗ cấu trúc cho phép edge sống
  qua ma sát. **Hệ quả:** nên rời 5m — các vòng 88-93, 103-123, 149-151, 204-205
  dồn phần lớn công sức vào 5m, nơi khe hụt ~18x, trong khi cùng cơ chế ở 4h chỉ
  đối mặt ~1,5x. **KHÔNG khẳng định chuyển sang 4h là giải quyết được gì:** (1)
  biên **Target 3** (Round 92: ~9,3/tuần 5 năm, ~7,2-7,3/tuần 18 tháng so với
  sàn ≥7/tuần) — ít lệnh hơn/chậm hơn chính là thứ cải thiện tỉ lệ và cũng chính
  là thứ phá sàn đó; (2) **hiện chưa có gì qua rào** ở 4h (2/77 ở chi phí
  production, và Round 212 không tìm được candidate nào sống qua cả 4 cửa sổ).
  Tỉ lệ tốt hơn không phải là một candidate. **Giới hạn:** phần có kiểm soát chỉ
  là 5m-vs-1h trên cùng cửa sổ; số 4h lấy từ cửa sổ dài hơn nên **trộn interval
  với cửa sổ** — không được đọc đường cong này như đơn điệu đã chứng minh. File:
  `round218-the-gap-closes-with-interval-1.5x-at-4h-not-8x.md`.

- **Round 219 (2026-08-29) — matched window GIỮ được thứ tự interval nhưng LÀM
  VỠ con số "1,5x": đó là số của riêng holdout, còn train thì ngược dấu.**
  Round 218 tự nêu điểm yếu của mình (4h lấy từ cửa sổ 1.800 ngày còn 5m/1h từ
  365 ngày ⇒ trộn interval với cửa sổ); vòng này chạy **1h trên đúng cửa sổ
  1.800 ngày**. **Thứ tự sống sót:** holdout, ≥30 trade — 1h tỉ lệ **+0,206**
  (61 ô, trung vị 195 trade) so với 4h **+0,659** (40 ô); 4h vẫn hơn ~3 lần trên
  dữ liệu khớp cửa sổ. **Nhưng độ lớn thì không:** tách theo split thay vì chỉ
  trích holdout — 4h đọc ra **−0,029 (train) / +0,158 (validation) / +0,659
  (holdout)**, tức **train ÂM**; 1h cùng hình dạng (+0,035 / +0,000 / +0,206).
  Trên **cả hai** interval, 20% cuối cửa sổ đơn giản là regime dễ thở hơn. Con
  số 4h trung thực là **một KHOẢNG từ −0,03 tới +0,66, trung vị các split
  ~0,16** ⇒ khe hụt **3-6x**, không phải 1,5x như Round 218 giật tít. Round
  217/218 trích holdout — hợp lệ vì là out-of-sample, nhưng chỉ báo cáo split
  đẹp nhất mà không show hai cái kia đã biến một regime thuận thành "tính chất
  của interval"; đúng cái bẫy Round 211 đã đo, mà tôi không áp dụng cho chính
  headline của mình. **Bằng chứng thứ ba về window-sensitivity** (r211/r212, nay
  trên metric edge/friction chứ không phải PF): tỉ lệ holdout của 1h là **0,331
  ở 365 ngày** và **0,206 ở 1.800 ngày** — cùng interval/nguồn/engine/metric,
  thấp hơn 38% trên cửa sổ dài. Ghi thêm: **1h/1800d qua rào 0/77** ở chi phí
  production so với 2 của 4h — interval có nhiều ô hơn và nhiều trade mỗi ô hơn
  lại không qua cái nào. **Vòng sau phải làm:** thay lát cắt 60/20/20 duy nhất
  bằng **walk-forward** (CLI có `--train-ratio`/`--validation-ratio`), chạy
  nhiều partition so le trên cùng 1.800 ngày rồi lấy **phân phối** của tỉ lệ;
  và từ nay báo cáo tỉ lệ như một **khoảng**, không bao giờ như một con số. File:
  `round219-matched-window-keeps-the-ordering-but-breaks-the-1.5x-number.md`.

- **Round 220 (2026-08-29) — lợi thế của giai đoạn gần đây CƯỠI trên biến động
  tăng 2,07 lần trong khi ma sát mô hình đứng yên: đây là hình hài cụ thể của
  cảnh báo Round 215.** **Ghi nhận giới hạn công cụ trước:** walk-forward thật
  **không diễn đạt được** bằng flag hiện có — `--train-ratio`/`--validation-ratio`
  dời được ranh giới nhưng holdout **luôn là phần đuôi**, còn `--days` chỉ dời
  điểm bắt đầu, nên không có cách nào đặt holdout vào giữa lịch sử. Thay vào đó
  đổi **độ dài** holdout. **Kết quả 1 — gradient theo thời gian, không phải vách
  đứng:** 4h/1.800 ngày, holdout 20% cho tỉ lệ **+0,659** (70% ô dương) còn
  holdout 40% cho **+0,452** (55%); train và validation gần như không đổi khi
  chia lại (−0,029/−0,061 và +0,158/+0,151) — chỉ holdout nhạy. Đọc theo trục
  thời gian: **dữ liệu cũ −0,03…−0,06, giữa +0,15, gần đây +0,45…+0,66**.
  **Kết quả 2 — và phần lớn gradient đó là biến động đối đầu một khoản thuế cố
  định:** biến động thực (trung vị |log return| 4h, 7.880 nến, 2021-09-24 →
  2026-08-28) là **0,1521% (train) / 0,1820% (validation) / 0,3143% (holdout
  20%) = 2,07 lần train** / 0,2377% (holdout 40%), trong khi **ma sát mô hình
  chỉ nhích 0,00693 → 0,00713, tức +3%**. Edge/lệnh scale theo độ lớn con sóng;
  ma sát bps cố định thì không scale theo gì cả ⇒ biến động gấp đôi **tự động**
  nâng tỉ lệ mà tín hiệu không hề tốt lên. Chuẩn hoá theo biến động vẫn còn phần
  dư, nhưng **chiều của sai số mô hình là một chiều**: spread/slippage thật nới
  rộng khi biến động tăng, nên mô hình bps cố định **đánh giá THẤP ma sát đúng
  ở đoạn biến động cao gần đây** — chính đoạn đang gánh kết quả đẹp. Hiệu chỉnh
  chỉ có thể **thu hẹp** lợi thế gần đây, không thể nới ra. **Ảnh hưởng tới
  Round 217-219:** **thứ tự interval KHÔNG bị ảnh hưởng** (5m/1h/4h đo trên cùng
  cửa sổ, cùng hồ sơ biến động, nên so sánh giữa chúng vẫn nhất quán); thứ bị
  ảnh hưởng là **mọi khẳng định tuyệt đối về việc 4h gần điểm hoà vốn tới đâu**.
  Suốt 5 vòng "ma sát là mô hình chứ không phải phép đo" chỉ là câu miễn trừ
  trừu tượng; giờ nó có **độ lớn đo được (2,07x) và dấu đã biết**. File:
  `round220-the-recent-advantage-rides-on-doubled-volatility-and-flat-modelled-friction.md`.

- **Round 221 (2026-08-29) — tính đúng ma sát theo biến động thì lợi thế gần đây
  GIẢM MỘT NỬA nhưng KHÔNG biến mất: tỉ lệ 4h là ~0,32, không phải 0,66.**
  Round 220 đo được chênh lệch biến động 2,07 lần và từ chối quy trách vì phép
  chuẩn hoá trên nền train âm không đáng tin. Vòng này quy trách bằng cách tránh
  hẳn phép chia tỉ-lệ-của-tỉ-lệ: **tính cho đoạn gần đây đúng mức ma sát mà biến
  động của nó hàm ý, rồi so với thời kỳ cũ tính ở mức của nó**. Một run với ma
  sát nhân 2,07 (`--fee-bps 10.35 --slippage-bps 4.14 --funding-rate-bps 2.07`);
  kiểm tra vệ sinh đạt: ma sát/lệnh đo được đi từ 0,00713 → **0,01476, đúng
  2,07x**, edge/lệnh không đổi. **Cặp so sánh:** train @1x (thời kỳ biến động
  thấp, tính đúng phí của nó) = **−0,029** so với holdout @2,07x (thời kỳ biến
  động cao, đã điều chỉnh) = **+0,318**; còn headline cũ của Round 218/219 ở ma
  sát phẳng là +0,659. ⇒ **Gradient theo thời gian là khoảng NỬA ARTIFACT, NỬA
  THẬT.** Round 218-219 thổi lên khoảng 2 lần; nghi ngờ "toàn bộ là artifact"
  của Round 220 cũng sai. Ghi thêm: ở ma sát gấp đôi, số candidate qua rào chỉ
  giảm 2/77 → **1/77** — vẫn còn một cái sống. **Con số sau bốn lần sửa:** r218
  ~1,5x (0,659, chỉ holdout, thổi phồng) → r219 khoảng −0,03…+0,66 (đúng nhưng
  rộng) → r220 nghi toàn artifact (quá bi quan) → **r221 ~0,32 dưới giả định ma
  sát scale tuyến tính, tức khe ~3x**. **Dạng trung thực là một KHOẢNG chứ không
  phải một điểm:** tỉ lệ thật nằm giữa **0,32** (ma sát scale tuyến tính theo
  biến động) và **0,659** (ma sát không scale) — cả hai đều là giả định về
  microstructure, và đầu bảo thủ mới là đầu để lập kế hoạch. Cả hai đầu đều
  **chưa chạm hoà vốn**. **Giới hạn đứng nguyên:** hệ thống chưa từng sinh một
  fill thật (production chạy ledger `paper-*` mô phỏng), nên mọi con số ma sát ở
  đây vẫn là mô hình; đo spread thật theo regime biến động sẽ chốt được khoảng
  này và **không làm được từ bên trong hệ thống này**. File:
  `round221-half-artifact-half-real-volatility-adjusted-4h-ratio-is-0.32.md`.

- **Round 222 (2026-08-29) — áp TOÀN BỘ bộ lọc tích luỹ vào 4h thì còn KHÔNG
  candidate nào, và kẻ sống sót cuối cùng chết vì ba lý do độc lập.** Round 221
  đếm được 1/77 sống qua ma sát điều chỉnh nhưng chưa gọi tên; đó là
  **`ichimoku_cloud_9_26_52_26`**. **Phễu (mỗi bộ lọc đều đến từ một phát hiện
  đo được ở r210-r221, không phải từ ý muốn loại bỏ):** 77 candidate → **2** qua
  rào PF cả ba split ở ma sát 1x → **1** sống qua ma sát điều chỉnh 2,07x → **0**
  đạt sàn 30 trade cả ba split (r210) → **0** có PnL dương cả ba split (r212).
  **Bộ lọc không nhận cái nào.** Chỗ chết cụ thể: `ema_crossover_12_26` gãy khi
  ma sát điều chỉnh (train PF 1,01 → 0,82) và âm PnL ở 2/3 split;
  `ichimoku_cloud_9_26_52_26` có **10 trade ở validation và 10 ở holdout** —
  dưới sàn 30 trade ở 2/3 split nên PF 1,97/4,15 của nó không mang thông tin —
  cộng thêm **PF 1,78 mà PnL −0,07** ở validation (đúng lỗi r212 hiện hình ngay
  trong kẻ tưởng như sống sót), và nó vốn đã đóng từ Round 108. **Không tiêu
  container nào:** bước tiếp theo hiển nhiên là cross-check bybit XAUT (r210 đã
  hiệu chuẩn sẵn) nhưng một candidate có 10 trade ở hai split thì đã bị loại
  trước khi sự đồng thuận cross-broker có ý nghĩa — ghi lại để phần bỏ qua này
  được đọc là quyết định chứ không phải sơ suất. **KHOẢNG TRỐNG HIỆU CHUẨN, nói
  thẳng:** một bộ lọc không nhận gì chỉ có ý nghĩa nếu nó *sẽ* nhận thứ có thật —
  và bộ này **chưa từng được test với một positive đã biết**. `grep '^mtf_'` trên
  mọi run của chuỗi này trả về **0**, vì candidate MTF cần
  `--higher-timeframe-interval` mà chưa run nào truyền. Mà cơ chế **duy nhất**
  chương trình từng validate (swing 4h/1d MTF stochastic, r17/172/189) **chính
  là** một candidate MTF. ⇒ **"không còn candidate nào" phải đọc là "không còn
  candidate ĐƠN-KHUNG-THỜI-GIAN nào", không phải "4h không có gì chạy được"** —
  yếu hơn hẳn cái phễu gợi ý, và đó là cách đọc trung thực. **Vòng sau:** chạy
  bộ lọc trên họ swing 4h/1d với `--higher-timeframe-interval` để kiểm chứng
  hiệu chuẩn. File:
  `round222-the-accumulated-rule-stack-admits-zero-candidates-at-4h.md`.

- **Round 223 (2026-08-29) — bộ lọc CÓ nhận candidate (2/107 trên BTC 4h+1d),
  nhưng nó KHÔNG ĐỦ SỨC đánh giá chính chiến thuật swing đang deploy — và cả hai
  điều đều quan trọng.** Đây là vòng BTC vì bắt buộc: câu hỏi hiệu chuẩn xoay
  quanh cơ chế duy nhất chương trình từng validate, mà cơ chế đó nằm ở BTC. Chạy
  exness BTC/USD 4h với `--higher-timeframe-interval 1d`, 1.800 ngày — **107
  candidate, 30 cái MTF, 17 biến thể stochastic**, có cả cái đang deploy.
  **Kết quả 1 — bộ lọc không phải bất khả bác bỏ:** 107 → **7** qua rào PF cả ba
  split → **2** qua toàn bộ stack (≥30 trade mọi split + PnL dương mọi split).
  `mtf_candle_momentum_10bps_sma10_trend_filtered`: trade **193/58/62**, PF
  1,07/1,14/1,08, PnL đều dương, **tỉ lệ edge/ma sát 2,04/2,23/2,00** — ổn định
  qua cả ba split trong vòng 12%, đúng chữ ký hiếm mà r210-211 chỉ ra là có ý
  nghĩa; `candle_momentum_rv_regime_filter_10_50_1.3`: trade 376/152/115, tỉ lệ
  1,23/3,55/1,19. Trung vị holdout của cả quần thể cùng run chỉ **0,087** (n=61)
  ⇒ hai cái này cao hơn đồng loại một tới hai bậc. **Đây là candidate đầu tiên
  của cả phiên qua được MỌI bộ lọc đã tích luỹ.** **Kết quả 2 — nhưng chiến thuật
  swing đang deploy thì bộ lọc không phán được:**
  `mtf_stochastic_14_3_30_70_sma50_trend_filtered` (r17/172, deploy r189) đọc ra
  train 1,37 / validation 2,40 / **holdout 0,90 (PnL −0,17)** trên **41/18/19**
  trade ⇒ *trượt* rào, nhưng 18 và 19 trade **dưới chính sàn 30 trade của r210**,
  nên hai split đó không mang thông tin theo bất kỳ chiều nào. Đọc đúng không
  phải "chiến thuật này bị bác bỏ" mà là **"phép test này không có power để
  phán"**. **CĂNG THẲNG CẤU TRÚC, là số học chứ không phải quan điểm:** rào cần
  ≥30 trade × 3 split = **90+ trade**; r207 đo tần suất live của chiến thuật này
  là **~0,28 trade/tuần**; 90 trade cần **~6 năm**; retention exness là **5 năm**.
  ⇒ **Rào đánh giá của chương trình về nguyên tắc không thể đánh giá đúng lớp cơ
  chế tần suất thấp mà r218-221 kết luận là nơi edge sống được qua ma sát.** Ghi
  thêm: cả hai kẻ sống sót đều **tần suất cao** (376/152/115 và 193/58/62) — bộ
  lọc hiện chỉ nhận được đúng loại mà r216-217 chỉ ra là phơi nhiễm chi phí nhất.
  Bộ lọc và vật lý đang chỉ ngược hướng nhau. **CHƯA PROMOTE:** cả hai mới chỉ
  một broker, một instrument, một cửa sổ, một partition — cần cross-broker
  binance BTC + bybit BTC (r205/r210), cửa sổ thứ hai (r219: lệch 38%) và
  partition thứ hai (r211: 48% ô đảo verdict). Promote lúc này là lặp lại đúng
  sai lầm "zombie strategy" của Round 67. File:
  `round223-stack-calibration-passes-two-real-candidates-and-a-structural-tension.md`.

- **Round 224 (2026-08-29) — CROSS-BROKER: một candidate sống qua TOÀN BỘ stack
  trên CẢ BA broker, cái còn lại bị bác bỏ. Kết quả mạnh nhất chương trình từng
  ghi được.** Chạy lại hai kẻ sống sót của Round 223 trên **binance BTC/USDT** và
  **bybit BTC/USDT**, 4h + bộ lọc 1d, 1.800 ngày, chi phí production.
  **`mtf_candle_momentum_10bps_sma10_trend_filtered` — đứng vững ở mọi nơi:**
  exness trade 193/58/62 PF 1,07/1,14/1,08; binance 187/58/62 PF 1,10/1,17/1,12;
  bybit 187/58/64 PF 1,13/1,16/1,11 — **chín ô broker×split, PF đều nằm trong dải
  1,07-1,17**, mọi split trên sàn 30 trade, mọi PnL dương, số trade gần như y hệt
  nhau giữa các broker (đúng hình dạng của cùng một tín hiệu bắn trên cùng những
  cây nến). Để so sánh: trung vị edge/ma sát holdout của cả quần thể là 0,087,
  còn candidate này 2,00-2,23 (r223). **`candle_momentum_rv_regime_filter_10_50_1.3`
  — BỊ BÁC BỎ:** qua ở exness (1,02/1,39/1,05) nhưng **đảo chiều** ở binance
  (train PF 0,86, PnL −3,79) và bybit (0,79/1,20/0,99, PnL −6,23/−0,21) — đúng
  chữ ký Round 205. Ghi thêm: `three_candle_continuation` chỉ qua ở **riêng
  binance**, thêm một artifact một-broker. Luật cross-broker đã loại 2 trong 3
  candidate được đưa cho nó. **VÌ SAO CHƯA PROMOTE (nói thẳng, không vòng vo):**
  còn thiếu đúng hai trục mà chính chương trình đã ĐO là nguồn false-positive
  chính — **partition** (r211: 48% ô đảo verdict khi dời partition) và **cửa sổ**
  (r219: cùng metric lệch 38% giữa 365 và 1.800 ngày). Candidate này mới có một
  cut 60/20/20 và một cửa sổ. Mỗi trục là một container, đúng việc của vòng sau.
  Promote lúc này = phạm sai lầm zombie-strategy Round 67 trong khi biết rõ.
  Hai điểm tiết chế thêm: **edge mỏng** (train PF 1,07-1,13, PnL ròng +0,40…+2,54
  trên vốn 10.000) và **deploy cũng chưa tác dụng sớm** — theo r207/r223 strategy
  mới có `strategy_weight = 0` cho tới khi đủ 20 trade, mà cái này chỉ ~62 trade
  mỗi holdout 360 ngày. **Sự cố đã xử lý:** lần gọi đầu timeout ở 2 phút khi
  container bybit còn chạy — đúng kiểu hỏng mà skill cảnh báo (foreground
  `docker run` bị kill để lại container giữ slot kline gate). Đã kiểm tra ngay,
  thấy còn chạy, để nó chạy nốt 75 giây và `--rm` tự dọn. Không rò rỉ, không
  tranh chấp gate — ghi lại vì chính việc kiểm tra mới quan trọng: nếu bỏ mặc,
  các vòng sau sẽ bị chẩn đoán nhầm thành tranh chấp production đúng như
  Round 124-125. File:
  `round224-one-candidate-survives-the-full-stack-on-all-three-brokers.md`.

- **Round 225 (2026-08-29) — candidate mạnh nhất QUA được test partition nhưng
  TRƯỢT test cửa sổ: edge của nó nằm ở phần lịch sử cũ và ÂM trong 2,5 năm gần
  đây ⇒ KHÔNG promote.** Chạy đúng hai trục Round 224 đã nêu, trên binance
  BTC/USDT (route production). **Partition — QUA, và còn mạnh hơn:** với
  40/20/40, trade 132/55/121, PF 1,09/1,13/1,16, PnL đều dương — holdout tăng gấp
  đôi lên **121 trade** mà vẫn qua hết, đối chiếu tỉ lệ đảo 48% mà r211 đo được
  thì đây là kết quả thật. **Cửa sổ — TRƯỢT, và không phải vì kỹ thuật:** cửa sổ
  900 ngày cho trade 88/36/25, PF **0,91/0,79**/2,12, PnL **−0,76/−0,59**/+1,24 —
  train và validation đều **dưới 1 và PnL âm** trên 88 và 36 trade (trên/gần sàn
  30 nên không thể đổ cho mẫu nhỏ); chỉ holdout 25 trade là mạnh, mà 25 thì dưới
  sàn. **MÂU THUẪN QUYẾT ĐỊNH:** hai run cho verdict ngược nhau về **cùng một
  khoảng lịch** — validation của run 1.800 ngày phủ ~720→360 ngày trước với PF
  **1,17**, trong khi run 900 ngày đọc 900→540 trước là **0,91** và 540→360 trước
  là **0,79**. Ledger phụ thuộc đường đi (equity state, vị thế đang mở, warmup của
  bộ lọc 1d đều khác nhau tuỳ điểm bắt đầu), nên sức mạnh trên 1.800 ngày một
  phần là tính chất của **lịch sử được nạp vào**, không phải của riêng tín hiệu.
  Ghép các đoạn lại: ~360 ngày gần nhất tốt, ~540 ngày trước đó xấu, ~900 ngày cũ
  hơn tốt ⇒ **phụ thuộc regime, không phải edge ổn định**. **Phán quyết:** không
  promote. Đồng thuận cross-broker ba nguồn (r224) là thật và vẫn là kết quả mạnh
  nhất chương trình ghi được, partition còn củng cố thêm — nhưng một candidate mà
  edge biến mất và chuyển âm trong 2,5 năm gần nhất thì trượt câu hỏi duy nhất có
  ý nghĩa cho deploy: "ngày mai tôi có dám trade cái này không". Giữ lại trong hồ
  sơ như candidate tốt nhất từng tìm được, kèm chế độ thất bại chính xác, thay vì
  deploy rồi phát hiện trên production. **Quan sát phụ:** **số lượng kẻ sống sót
  cũng phụ thuộc partition** — 40/20/40 nhận **5** candidate qua full stack so với
  **2** ở 60/20/20 trên **cùng dữ liệu** (r211 ở mức quần thể chứ không còn ở mức
  từng ô); và cửa sổ 900 ngày nhận **0/107**, khớp mọi cửa sổ ngắn khác trong
  chuỗi này. File:
  `round225-the-strongest-candidate-fails-the-window-test-not-promotable.md`.

- **Round 226 (2026-08-29) — KHÔNG có path dependence: giữ nguyên kỳ holdout mà
  đổi độ dài lịch sử thì kết quả giống hệt nhau. Cả cơ chế lẫn số học ranh giới
  của Round 225 đều SAI, và cả hai đều là lỗi của tôi.** Round 225 giải thích
  thất bại test cửa sổ bằng "ledger phụ thuộc đường đi" — một khẳng định mạnh về
  engine, đưa ra từ suy luận chứ không từ phép đo. Kiểm chứng trực tiếp: **giữ
  cố định kỳ đánh giá** (holdout = ~360 ngày cuối, 2.159-2.160 nến) và chỉ đổi
  lượng lịch sử phía trước — 1.800 / 1.200 / 900 ngày, bằng cách chỉnh ratio
  tương ứng (60/20/20, 50/20/30, 40/20/40). **Kết quả: giống hệt.** Candidate cho
  **62 trade, PF 1,12, PnL +0,53 ở cả ba run**; trung vị quần thể cũng y hệt
  (PF 0,890, PnL −0,81, 63 ô); **0/63 candidate lệch PF holdout quá 10%**, 59/63
  giữ nguyên số trade (4 cái lệch là chỉ báo nhạy warmup). ⇒ **Mỗi split được
  đánh giá trên ledger riêng, độc lập với lượng lịch sử phía trước. Cơ chế của
  Round 225 bị bác bỏ.** **Và "mâu thuẫn quyết định" kia là lỗi số học của tôi:**
  60% của 900 ngày là 540 ngày, nên train của run 900 ngày là **900→360 trước**
  và validation là **360→180** — không phải 900→540 và 540→360 như tôi viết. Hai
  run có validation phủ **hai kỳ khác nhau**; chưa từng có mâu thuẫn cùng-kỳ nào
  để mà phải giải thích. **Phán quyết vẫn giữ nguyên** (không promote) nhưng trên
  cơ sở đúng: tính theo ranh giới chuẩn, candidate đọc ra 1800→720 PF 1,10 tốt;
  720→360 PF 1,17 tốt; **900→360 PF 0,91 PnL −0,76 xấu**; **360→180 PF 0,79 PnL
  −0,59 xấu**; 360→0 PF 1,12 tốt. Một đoạn yếu nấp trong một tổng hợp dài mạnh
  hơn là chuyện bình thường của phép tổng hợp, không phải mâu thuẫn — nhưng nó là
  **phụ thuộc regime** (đo được), không phải **phụ thuộc đường đi** (đã bị bác
  bỏ). **Sự thật phương pháp luận hữu ích rút ra:** **so sánh cửa sổ là chuyện
  KỲ LỊCH nào được đưa vào, không bao giờ là chuyện cơ chế chạy** — khi hai cửa
  sổ bất đồng, lời giải nằm trong dữ liệu chứ không nằm trong engine. Điều này
  loại hẳn một lớp suy đoán khỏi các vòng sau, kể cả suy đoán tôi đã công bố ở
  vòng trước. File:
  `round226-no-path-dependence-round-225-boundary-arithmetic-was-wrong.md`.

- **Round 227 (2026-08-29) — WALK-FORWARD THẬT ĐẦU TIÊN trên XAU, và đúng một
  segment làm sụp lời giải thích "do biến động".** Round 219 đòi walk-forward,
  Round 220 kết luận không diễn đạt được (holdout luôn là đuôi). Round 226 gỡ
  được rào đó mà không cần đổi công cụ: nó chứng minh **mỗi split được đánh giá
  độc lập với lịch sử phía trước**, nên **train và validation chính là các
  segment nội vùng hợp lệ** — đặt `--train-ratio k*0.2 --validation-ratio 0.2` là
  đọc thẳng segment thứ k. **Năm segment ~360 ngày không chồng lấn của exness XAU
  4h (ô ≥30 trade), từ cũ tới mới:** tỉ lệ **−0,114 → −0,264 → +0,151 → +0,158 →
  +0,659**; %ô có edge dương 45/41/59/56/70; số ô PF>1 là 6/5/11/11/14. Ma sát
  **phẳng 0,00701-0,00722 suốt 5 năm** (lần xác nhận thứ sáu rằng nó là thuế cố
  định theo lệnh). Xu hướng là một **bậc thang chứ không phải trôi dần**: hai
  segment âm rõ rồi ba segment dương. Thay thế suy luận từ cửa sổ lồng nhau của
  Round 220 bằng phép đo trực tiếp từng đoạn. **SEGMENT LÀM SỤP LỜI GIẢI THÍCH
  BIẾN ĐỘNG:** biến động thực từng segment (trung vị |ret 4h|) là 0,1549 /
  0,1520 / **0,1471** / 0,1820 / 0,3143 % ⇒ 1,00 / 0,98 / **0,95** / 1,17 /
  2,03 lần S1. **S3 có biến động THẤP NHẤT trong cả năm segment nhưng tỉ lệ
  DƯƠNG rõ (+0,151), trong khi S1 và S2 biến động cao hơn lại âm.** Nếu biến
  động chi phối tỉ lệ thì S3 phải là segment tệ nhất, chứ không phải hạng ba.
  Concordance 8/10 cặp, và đúng hai cặp lệch đều dính S3. ⇒ **Tách được vị trí
  của từng nửa trong kết luận "nửa artifact nửa thật" của Round 221:** S4→S5
  (0,158→0,659 khi biến động 1,17x→2,03x) phần lớn **là** hiệu ứng biến động;
  còn **S2→S3 (−0,264→+0,151 khi biến động GIẢM còn 0,95x) KHÔNG giải thích được
  bằng biến động** — có gì đó đã đổi trong độ "giao dịch được" của vàng 4h quanh
  mốc ~1.080 ngày trước. **KHÔNG khẳng định:** ý nghĩa thống kê (5 segment, trung
  vị trên ~40 ô, không có kiểm định — con số concordance chỉ là mô tả); *cái gì*
  đã đổi; hay bất kỳ segment nào giao dịch được — cái tốt nhất là 0,659, mà
  Round 221 đã cho thấy nó rơi về ~0,32 khi tính ma sát theo biến động, nên
  **không segment nào trong 5 năm chạm hoà vốn**. File:
  `round227-first-real-walk-forward-and-volatility-does-not-explain-the-mid-history-turn.md`.

- **Round 228 (2026-08-29) — sáu thống kê thị trường đối chiếu với dãy tỉ lệ:
  giả thuyết "thị trường trending hơn" BỊ BÁC BỎ, và hai bước chuyển có chữ ký
  KHÁC NHAU.** Round 227 để ngỏ câu hỏi "cái gì đã đổi quanh mốc 1.080 ngày
  trước". Tính sáu thống kê từ cùng bộ OHLC cho từng segment.
  **Kết quả 1 — trendiness bị bác bỏ chứ không phải chỉ thiếu bằng chứng:**
  **tự tương quan lag-1 gần như bằng 0 ở mọi segment** (+0,017…+0,032) và thứ tự
  của nó chạy **ngược** dãy tỉ lệ (2/10 cặp đồng thuận); body/range 3/10. Cái đã
  đổi **không phải** là chuyện nến vàng 4h bắt đầu nối tiếp nhau. **Kết quả 2 —
  hai bước chuyển làm dịch chuyển những thống kê NGƯỢC nhau:** **S2→S3** (tỉ lệ
  −0,264 → +0,151, đúng bước mà biến động không giải thích được): Kaufman
  efficiency 0,0366 → **0,0753** và drift +13,9% → **+26,9%** đều **gấp đôi**,
  trong khi biến động **giảm** (0,1520 → 0,1471%) và biên độ phẳng (+2,7%);
  **S4→S5** (+0,158 → +0,659): biến động **1,73x** và biên độ 1,69x trong khi
  efficiency **sụp còn một phần ba** (0,0805 → 0,0278) và drift giảm. ⇒ S2→S3 là
  **tính định hướng ở biến động phẳng**; S4→S5 là **biến động ở lúc tính định
  hướng sụp đổ**. Không thống kê đơn lẻ nào bám được cả hai — khớp với kết luận
  của Round 227 rằng hai nửa gradient có nguyên nhân khác nhau. **CẢNH BÁO ĐẶT
  TRƯỚC KHI AI DỰA VÀO BẢNG NÀY:** chỉ có **năm segment** — đếm concordance trên
  10 cặp ở n=5 không phân biệt nổi 9/10 với 6/10, không có kiểm định nào được
  thực hiện vì không kiểm định nào đáng tin, và **thứ hạng sáu thống kê không
  được đọc như một thứ hạng**. Thứ sống sót qua mẫu nhỏ là bằng chứng về **dấu**:
  tự tương quan gần 0 khắp nơi và đi sai chiều; và riêng ở S2→S3, biến động cùng
  biên độ phẳng trong khi efficiency và drift gấp đôi. **Một câu chuyện khớp với
  năm điểm dữ liệu là một câu chuyện, không phải một phát hiện** — ghi nhận đúng
  như vậy. File:
  `round228-no-single-market-statistic-explains-the-turn-and-trendiness-is-contradicted.md`.

- **Round 229 (2026-08-29) — cuối cùng cũng chạy sweep MTF trên XAU: KHÔNG
  candidate nào sống sót, nhưng họ MTF lại cho TỈ LỆ EDGE/MA SÁT CAO NHẤT
  chương trình từng đo.** Round 223 là run đầu tiên trong cả chuỗi truyền
  `--higher-timeframe-interval`, và nó chạy trên BTC — thí nghiệm đó **chưa bao
  giờ** chạy trên XAU, instrument ưu tiên. Nay chạy: exness XAU 4h + bộ lọc 1d,
  1.800 ngày, **107 candidate (30 cái MTF)**. **Phễu rỗng:** 107 → **2** qua rào
  PF → **1** qua sàn 30 trade → **0** qua PnL dương. **Không một candidate MTF
  nào qua nổi cả rào PF**; hai cái qua rào PF chính là cặp đơn-khung mà Round 222
  đã loại, và loại lại vì đúng lý do cũ (`ema_crossover_12_26` PF 1,01/1,05/1,42
  nhưng PnL **−0,10/−0,05**/+0,79 — lỗi r212, bị đúng bộ lọc PnL bắt được).
  Thêm 30 candidate MTF vào sweep XAU làm thay đổi số kẻ sống sót đúng **bằng 0**.
  **NHƯNG:** tách quần thể holdout của cùng run đó (ô ≥30 trade) — **MTF: 11 ô,
  trung vị 40 trade, edge/lệnh +0,02895, tỉ lệ +4,571, 82% ô dương**; đơn-khung:
  40 ô, trung vị 110 trade, edge/lệnh +0,00470, tỉ lệ +0,659, 70%. Tức **gấp 6,9
  lần edge mỗi lệnh ở một phần ba số lệnh**, và là **tỉ lệ cao nhất chương trình
  từng đo ở bất cứ đâu**; kể cả bị Round 221 hiệu chỉnh biến động cho giảm nửa
  thì vẫn ~2,3 — trên hoà vốn, trong khi mọi quần thể trước đó đều dưới 1. Bộ lọc
  xu hướng làm đúng điều mô hình chi phí dự đoán: ít lệnh hơn, tốt hơn, đối đầu
  một khoản thuế cố định. **Vì sao vẫn không cái nào qua — HAI vấn đề KHÁC NHAU,
  không được gộp:** (1) **cỡ mẫu** — chỉ 12/30 đạt sàn trade ở validation và
  11/30 ở holdout, nên một phép hội ba split không thể chứng nhận một họ chỉ giao
  dịch ~40 lần mỗi đoạn 360 ngày (đúng căng thẳng cấu trúc r223 đo được cho
  chiến thuật swing đang deploy trên BTC); (2) **các đoạn cũ thật sự tệ** —
  18/30 qua PF ở holdout so với **7/30** ở train, khớp walk-forward r227 nơi
  S1/S2 âm cho cả instrument. Vấn đề 1 là giới hạn đo lường, vấn đề 2 là điểm yếu
  thật. **Vị thế trung thực về XAU chuyển từ "không gì chạy được" sang:** *trên
  XAU 4h, cơ chế MTF lọc xu hướng kiếm được ~4,6 lần ma sát của nó trong 360 ngày
  gần nhất và không thể được chứng nhận bởi một rào đòi 30 trade trên mỗi trong
  ba split; lịch sử xa của chúng thì kém, và đoạn thuận lợi kia chính là đoạn
  biến động cao vốn tâng bốc mọi thứ.* Đây **không phải** edge đã validate và
  không được đối xử như vậy — nó là quần thể chưa validate hứa hẹn nhất tìm được
  trên instrument ưu tiên, và **không validate được bằng rào hiện tại**. File:
  `round229-mtf-family-on-xau-best-ratio-ever-measured-but-cannot-clear-a-trade-count-bar.md`.

- **Round 230 (2026-08-29) — "lợi thế MTF" KHÔNG tổng quát sang BTC và ÂM ở hai
  trong ba split của XAU: đó là PHƯƠNG SAI, không phải edge. Rút lại headline
  của Round 229.** Round 229 trích tỉ lệ holdout **+4,571** của họ MTF trên XAU
  và gọi đó là "cao nhất từng đo" — nhưng nó chỉ trích **một split**, không kiểm
  hai split còn lại lẫn instrument còn lại. Kiểm cả hai (từ dữ liệu đã lưu, không
  tốn container): **XAU MTF = +0,371 / −1,954 / +4,571** — validation **âm sâu**
  ngay ở split liền kề; **BTC MTF = +1,458 / −1,086 / −1,563** — **âm ở CẢ HAI
  split ngoài mẫu**, chỉ dương ở train. **Cơ chế là số học chứ không phải cấu
  trúc thị trường:** biên độ dao động tỉ lệ giữa các split của MTF rộng gấp
  **9,5 lần** (XAU) và **4,3 lần** (BTC) so với đơn-khung (6,525 và 3,021 so với
  0,690 và 0,705), trên số trade mỗi ô **ít hơn 2,3-2,8 lần** (trung vị 39-51 so
  với 88-278). Đó đúng là thứ mẫu nhỏ gây ra cho một thống kê tính theo lệnh.
  Con số +4,571 là ô tốt nhất trong ba ô của quần thể ồn nhất trong run.
  **Thứ còn sống từ Round 229:** phễu rỗng (không candidate MTF nào qua rào PF
  trên XAU) vẫn đúng; và sự bất tương thích với sàn 30 trade vẫn đúng — nhưng
  giờ sàn đó là **toàn bộ câu chuyện** chứ không phải một nửa: **không có edge
  nào bị giấu sau sàn cả.** **LỖI LẶP LẠI, nói thẳng — đây là lần thứ BA trong
  phiên này tôi trích một split thuận lợi như thể nó là thuộc tính:** r218 trích
  holdout 4h 0,659 thành "khe ~1,5x" (r219 sửa khi train đọc ra −0,029); r225
  dựng cơ chế path-dependence trên một lỗi số học ranh giới (r226 sửa); r229
  trích holdout MTF 4,571 (r230 sửa khi validation đọc ra −1,954). Cùng một
  khuôn: **một split từ quần thể mẫu nhỏ, đọc mà không đọc kèm biên độ dao
  động** — dù chính r210, r211 và r219 đều đã đo tại sao làm vậy là sai. **Sửa
  bằng cơ chế chứ không bằng thái độ: từ nay báo cáo CẢ BA split KÈM biên độ,
  hoặc không báo cáo gì.** File:
  `round230-the-mtf-advantage-does-not-generalise-it-is-variance.md`.

- **Round 231 (2026-08-29) — RÀO BA-SPLIT chỉ cho nhiều kẻ sống sót hơn NGẪU
  NHIÊN khoảng 1,38 lần, và ở hai run còn ÍT HƠN ngẫu nhiên.** Câu hỏi hiển
  nhiên mà 230 vòng chưa ai đặt: **bao nhiêu candidate qua rào "PF>1 cả ba
  split" hoàn toàn do may?** Lấy tỉ lệ qua từng split nhân lại, trên bảy sweep
  đã lưu: exness XAU 4h 1800d kỳ vọng 1,30 – quan sát 2 (1,54x); XAU 4h+1d kỳ
  vọng 2,33 – quan sát 2 (**0,86x**); exness BTC 4h+1d kỳ vọng 3,33 – quan sát 7
  (**2,10x**, giá trị hợp lệ cao nhất, và đúng là run sinh ra candidate qua được
  cross-broker); binance BTC 1800d 1,25x; bybit 1,65x; binance BTC 900d kỳ vọng
  2,67 – quan sát 1 (**0,37x**). XAU 5m hiện 20,17x nhưng đó là **một** kẻ sống
  sót trên kỳ vọng 0,05 — không có độ phân giải, đã loại. **Tổng: kỳ vọng 16,73,
  quan sát 23, tỉ số 1,38x** (1,32x nếu bỏ dòng 5m). **Diễn giải, và giả định
  độc lập cắt về một phía:** các split của cùng chuỗi dưới cùng một chiến thuật
  **không** độc lập — một chiến thuật có edge bền sẽ qua cả ba **vì** edge bền,
  tạo phụ thuộc dương đẩy quan sát vượt kỳ vọng. Nên obs/exp chính là thước đo
  mức "bền" mà quần thể mang theo, và **1,38x là TOÀN BỘ tín hiệu bền trên bảy
  sweep và ~700 lượt đánh giá candidate**. Một quần thể có nhiều chiến thuật bền
  thật sẽ cho 5-10x. ⇒ **Kết luận KHÔNG phải "rào bị hỏng"** — rào đang làm đúng
  việc của một phép hội. Kết luận là: **quần thể candidate gần như toàn những
  chiến thuật có kết quả từng split gần như độc lập nhau, tức đúng hình hài của
  một quần thể KHÔNG có edge bền; phép hội gần như không có gì để tìm.**
  **Điều này giải thích cả phiên:** candidate của r224 qua exness rồi đảo chiều
  ở hai broker; kẻ sống sót của r225 qua ba broker và một repartition rồi trượt
  cửa sổ 900 ngày; họ MTF của r229 đẹp nhất-từ-trước-tới-nay ở một split và
  −1,954 ở split liền kề. **Ở mức lift 1,38x thì đó là hành vi ĐƯỢC DỰ ĐOÁN của
  kẻ qua rào, không phải xui xẻo.** **KHÔNG được lấy cớ này để hạ rào:** một bộ
  lọc đang cho lọt kẻ sống sót ngẫu nhiên sẽ **tệ hơn** nếu nới lỏng — phản ứng
  đúng là **thêm test độc lập**, đúng như r224-226 đã làm và đã loại đúng
  candidate. File: `round231-the-three-split-bar-beats-chance-by-only-1.4x.md`.

- **Round 232 (2026-08-29) — áp luật của Round 230 lên chính thống kê của Round
  231: lift GỘP là THẬT (z=3,22) nhưng KHÔNG cấu hình nào xếp hạng được.**
  Round 230 kết bằng một luật cơ chế: *báo cáo cả ba split kèm biên độ, hoặc
  không báo cáo gì.* Round 231 ngay sau đó báo cáo một giá trị obs/exp mỗi run
  rồi chỉ đích danh một cái ("exness BTC 4h+1d 2,10x — nơi tín hiệu nằm") **mà
  không kèm biên độ**. Vòng này chạy đúng phép kiểm mà luật đó đòi. **Biên độ
  của chính thống kê đó — cùng một cấu hình BTC 4h+1d, chỉ đổi broker/cửa sổ/
  partition:** 2,10 (exness 1800d) / 1,25 (binance) / 1,64 (bybit) / 2,24
  (binance 40-20-40) / 1,67 (binance 1200d) / **2,73** (binance 900d 40-20-40) /
  **0,37** (binance 900d 60-20-20) ⇒ **dải 0,37–2,73, rộng 7,3 lần cho về cơ bản
  một cấu hình**. XAU 4h trải 0,00–1,54 (trung vị 0,86), có hai cấu hình **0 kẻ
  sống sót** trên kỳ vọng ~1. Con số 2,10 của Round 231 chỉ là một lượt rút bình
  thường (z=2,01); còn z cao nhất bảng (**3,47**) lại thuộc về binance 900d
  40/20/40 — **đúng cửa sổ mà Round 225 đo được candidate tốt nhất sụp đổ**. Độ
  bền cao ở mức quần thể trong một cửa sổ **không nói gì** về bất kỳ candidate
  nào trong đó. ⇒ **Rút lại phần xếp hạng của Round 231.** **NHƯNG gộp lại thì
  củng cố phần còn lại theo chiều ngược:** coi số đếm là Poisson trên mười hai
  cấu hình — 3/12 vượt |z|=2, 1/12 vượt |z|=3; **gộp: kỳ vọng 34,19, quan sát 53,
  tỉ số 1,55, z=3,22**. Tức lift **không** phải "không phân biệt được với ngẫu
  nhiên" — quần thể **có** một tín hiệu bền thật, chỉ là nhỏ. **VỊ THẾ CUỐI:**
  *quần thể candidate mang một tín hiệu bền có thật nhưng nhỏ — khoảng 1,5 lần
  tỉ lệ ngẫu nhiên trên ~700 lượt đánh giá — quá nhỏ để nhận diện được bất kỳ
  cấu hình, cửa sổ, broker hay candidate cụ thể nào, và đó chính là lý do mọi
  candidate qua rào ở r222-230 đều trượt bài test độc lập kế tiếp.* **Giới hạn:**
  mười hai run chồng lấn nặng về candidate lẫn dữ liệu nên không phải mẫu độc
  lập, z gộp là lạc quan. **Ghi chú về tỉ lệ sai của chính tôi:** đây là lần tự
  sửa thứ **tư** trong phiên (r219, r226, r230, r232), và **ba trong bốn là cùng
  một lỗi** — trích một con số thuận lợi mà không kèm biên độ. Luật không phải
  vấn đề; nhớ áp nó cho các thống kê **mới** mới là vấn đề. **Yêu cầu biên độ áp
  dụng cho MỌI thống kê chương trình báo cáo, kể cả thống kê được nghĩ ra để đánh
  giá thống kê khác.** File:
  `round232-the-persistence-signal-is-small-but-real-and-cannot-rank-configurations.md`.

- **Round 233 (2026-08-29) — production đã đóng 12 lệnh durable, và điều đó CHƯA
  nói lên gì; nhưng route XAU/binance bị đóng băng ĐÃ MỞ.** Rounds 231-232 kết
  luận quần thể chỉ mang tín hiệu bền nhỏ (~1,55x); production là dữ liệu **thực
  sự chưa từng thấy** duy nhất, nên đọc durable trade log (r207 dựng ra chính để
  làm việc này). **Đã đóng:** binance BTC 4 lệnh (PF 1,74), exness BTC 3 (0,84),
  bybit BTC 2 (1,68), và **đúng 1 lệnh** ở mỗi route vàng. Tổng 12 lệnh, 9 thắng,
  PnL dương ở mọi rule. **VÀ NÓ KHÔNG NÓI LÊN GÌ, theo đúng luật của chính phiên
  này:** (1) **cỡ mẫu** — r210 đã lập rằng PF dưới ~30 trade không mang thông tin
  dùng được, đây là **1-4 trade/route**; trích "binance BTC PF 1,74" sẽ đúng là
  lỗi đã bị sửa ở r219, r229/230 và r231/232 (ba trong bốn lần tự sửa của tôi
  chính là lỗi này); (2) **tính độc lập** — ba route vàng mỗi cái đóng **đúng
  một** lệnh take_profit thắng, mà r209 đo được các nguồn vàng tương quan
  **0,9915** trên return 4h ⇒ ba sàn bắt cùng một con sóng vàng là **một** quan
  sát chứ không phải ba; số sự kiện độc lập thực tế khoảng **4-5, không phải 12**.
  Chín thắng trên mười hai lệnh tương quan trong hai ngày là thứ một đồng xu
  cũng làm được ở cỡ mẫu này. **Không đưa ra khẳng định hiệu quả nào, theo bất kỳ
  chiều nào.** **PHÁT HIỆN THỰC CHẤT: XAU/binance đã mở băng.** Route đóng băng
  từ 2025-12-26 (chẩn đoán r203, xác nhận còn băng ở r205 và r206) nay:
  **trade 7 → 8**, `paper-fixed-pct` PnL **−0,0478 → +0,0466**, một lệnh
  take_profit thắng. **Quan trọng: `strategy_weights` GIỐNG HỆT r206** (rsi
  0,6267 / candle 0,3733) ⇒ `reweight_from_alpha_performance` **không** dịch
  chuyển; băng vỡ do **điều kiện thị trường** vượt qua gate của r203, không phải
  do đổi trọng số. **Một lệnh thắng không validate gì:** backtest r203 cho hành
  vi unfrozen của route này là **−1,54**, tổng 8 trade vẫn xa mọi sàn thông tin,
  và cú lật PnL chỉ là một lệnh đẩy một con số vốn luôn quanh 0. Nhưng cách mô tả
  "frozen by choice" của r205 **nay đã lỗi thời** với route đang chạy. **Ghi chú
  quy trình đáng giữ:** truy vấn checkpoint đầu tiên trả `(nil)` — trông y hệt
  mất checkpoint production — nhưng đó là **tôi sai key** (thiếu hậu tố route
  `.5m`); scan `*worker_checkpoint*` cho thấy đủ cả sáu key khoẻ mạnh. Ghi lại vì
  chế độ hỏng này **bất đối xứng**: báo "mất checkpoint production" sẽ kích hoạt
  một cuộc điều tra sự cố chỉ vì một lỗi gõ. **Scan trước khi kết luận là thiếu.**
  File: `round233-production-has-traded-twelve-times-and-that-says-nothing-yet.md`.

- **Round 234 (2026-08-29) — PHÉP ĐO PORTFOLIO-LAYER ĐẦU TIÊN của cả phiên: cả
  hai route đều CÓ gross edge dương và mất sạch vào ma sát; BTC giao dịch nhiều
  gấp 8 lần và vì thế xa hoà vốn gấp 15 lần.** Hai mươi chín vòng phân tích
  candidate **Alpha-layer**, trong khi mục tiêu của chương trình là lợi nhuận
  **Portfolio-layer** — và `--daily-profit-gate` đánh giá đúng **policy đang
  deploy thật**, không phải candidate tuỳ ý. Nó chưa từng được chạy lần nào
  trong phiên. **Kết quả (5m, holdout ~360 ngày):** exness XAU — 232 lệnh,
  **4,52 lệnh/tuần**, gross **+0,475**, cost drag **1,527**, net **−1,052**,
  **cost/gross 3,22** ⇒ edge/ma sát **0,311**, Sharpe −1,96; binance BTC —
  **1.877 lệnh**, **36,50 lệnh/tuần**, gross **+0,281**, cost drag **13,526**,
  net **−13,246**, **cost/gross 48,20** ⇒ edge/ma sát **0,021**, Sharpe −6,68.
  Cả hai đều trượt. **Cả hai trượt vì cùng một lý do, nay đo được trên policy
  đang chạy chứ không phải suy ra từ sweep candidate: gross edge dương, còn ma
  sát gấp 3,2 lần edge ở XAU và 48 lần ở BTC.** **PHÁT HIỆN — TẦN SUẤT LÀ THỨ
  PHÁ HUỶ PnL:** BTC giao dịch nhiều hơn **8,1 lần**, tạo ra **ÍT** gross profit
  hơn (+0,281 so với +0,475), trả chi phí nhiều hơn **8,9 lần**, và xa hoà vốn
  **gấp 15 lần**. **Tầng Portfolio CÓ tạo giá trị:** r217 đo edge/ma sát
  Alpha-layer trên XAU 5m là trung vị 0,035 và họ tốt nhất 0,12; policy deploy
  trên **cùng instrument, cùng interval** đạt **0,311** — tốt hơn 3-9 lần so với
  chính các tín hiệu nó tổng hợp. Gate, hold, stop/take đều có tác dụng. Vẫn
  thiếu 3 lần. **XUNG ĐỘT ĐƯỢC PHƠI BÀY VÀ ĐỊNH LƯỢNG:** ngưỡng
  `minimum_trades_per_week >= 7` **đối nghịch** với lợi nhuận trên dữ liệu
  production đo được — **BTC ĐẠT** chỉ tiêu tần suất rực rỡ (36,50/tuần, gấp 5
  lần sàn) và **cách hoà vốn 48 lần**; **XAU VI PHẠM** (4,52/tuần) và chỉ **cách
  3,2 lần**, gần hơn mười lăm lần. Round 92 đóng hướng "kéo dài hold" vì sợ phá
  sàn ≥7/tuần, dẫn ~7,2-9,3/tuần từ backtest `one_target` — vòng này đo policy
  **đang deploy** ở **4,52/tuần trên XAU**, tức sàn đã bị phá sẵn, và route gần
  lợi nhuận nhất chính là route đang phá nó. **Quyết định này không phải câu hỏi
  nghiên cứu:** Target 3 nên là sàn, thành trần, hay tách theo instrument — đó là
  quyết định sản phẩm. Nghiên cứu chỉ nói được cái giá: ở mức ma sát hiện tại,
  **mỗi lệnh thêm mỗi tuần là một khoản lỗ ròng trên cả hai route**. **KHÔNG
  khẳng định** giảm tần suất BTC sẽ có lãi — r92 đo hold là dưới-cộng-tính với
  stop/take và r213-215 đo các lever chi phí đáng ~0; 48 lần không lấp được chỉ
  bằng tần suất. Số PnL tuyệt đối vô nghĩa khi đứng riêng (sizing `fixed_notional
  5.0` trên vốn 10.000, drawdown tổng chỉ 0,013-0,135%) — **tỉ lệ mới mang nội
  dung**. Một cửa sổ holdout mỗi route; r219/r232 đã đo độ nhạy cửa sổ.
  **MỘT CỜ ĐƯỢC GIƯƠNG, KHÔNG DIỄN GIẢI:** báo cáo XAU liệt kê
  `input_continuity_failed` cho cả bảy interval khác 5m (15m có **1.266 gap chưa
  verify trên 55.917 nến**, 30m 1.263) trong khi `holdout_interval_continuity`
  lại **pass** và `interval_continuity_violations` = 0. Hai tín hiệu mâu thuẫn và
  tôi không biết cái nào chi phối — ghi lại để một pass `kline-data-quality` xử
  lý, không đoán ở đây. File:
  `round234-portfolio-layer-measured-at-last-frequency-is-what-destroys-pnl.md`.

- **Round 235 (2026-08-29) — giải quyết cờ của Round 234: MỌI gap chưa đánh dấu
  đều bắt đầu đúng ranh giới phiên hằng ngày. Đây là THIẾU METADATA, không phải
  THIẾU DỮ LIỆU.** Round 234 báo cáo gate XAU liệt kê 13 check trượt, bảy trong
  đó là `input_continuity_failed` trên mọi interval khác 5m, trong khi
  `holdout_interval_continuity` lại **pass** và `interval_continuity_violations`
  = **0** — hai tín hiệu mâu thuẫn, cố ý để lại chưa diễn giải. **Phân loại
  toàn bộ chuỗi exness XAU 15m (118.363 nến, 2021-08-26 → 2026-08-28):** 1.297
  điểm gián đoạn, 57.209 slot thiếu, **chỉ 10 cái có `gap_before_reason`** (đều
  là `broker_session_or_no_tick`) ⇒ 1.287 cái không đánh dấu, **độ phủ marker
  0,8%**. **Mọi gap không đánh dấu đều bắt đầu ở ranh giới phiên:** 987/992 gap
  nhỏ (≤2h) bắt đầu lúc **20:00 hoặc 21:00 UTC** (655 và 332), trung vị 4 slot =
  đúng một giờ, một lần mỗi ngày giao dịch (Thu 258 / Fri 255 / Mon 255 /
  Tue 260 / Wed 258 trên ~260 tuần); và 244/253 gap lớn bắt đầu **thứ Sáu 20:00
  hoặc 21:00 UTC**, cỡ 150-292 slot. ⇒ **1.283/1.287 gap không đánh dấu chính là
  phiên đóng cửa hằng ngày hoặc cuối tuần của một CFD chạy ngày thường**, chỉ 4
  cái nằm ngoài khuôn. **PHÁN QUYẾT: dữ liệu ĐẦY ĐỦ, marker mới là thứ thiếu.**
  `interval_continuity_violations=0` là đúng; `input_continuity_failed` kích hoạt
  theo `unverified_gap_count>0`, tức theo điểm gián đoạn **thiếu marker**, bất kể
  nó có phải phiên đóng cửa thật hay không. Hai check hỏi hai câu khác nhau.
  **Tác động, giới hạn trung thực: KHÔNG làm mất hiệu lực backtest nào** trong
  phiên này hay trước đó — chuỗi kline đầy đủ theo đúng lịch giao dịch thật của
  instrument, mà đó chính là thứ chiến thuật tiêu thụ. **Nhưng nó làm báo cáo
  gate khó đọc:** 13 check trượt thì **7 là nhiễu metadata, 6 mới là thật**
  (trades/tuần, positive_day_ratio, median_daily_pnl, sortino, sharpe,
  cost_to_gross). Đọc báo cáo mà không có phân tích này thì hoặc đếm thừa lỗi,
  hoặc tệ hơn là bắt đầu nghi ngờ chính dữ liệu bên dưới — lỗi đắt hơn, vì sáu
  cái trượt thật của r234 mới là kết quả thực chất. **Cách sửa** là backfill
  marker cho phiên đóng cửa bằng tooling sẵn có (`kline-gap-marker-backfill`,
  mutation có kiểm soát theo `docs/runbooks/kline-maintenance-tools.md`);
  **không thực hiện ở đây** vì đó là mutation production có kiểm soát còn vòng
  này là research. **Chưa xác định:** bốn gap bất thường (bắt đầu 08:00/11:00/
  13:00/23:00 UTC) là gì — 4 trên 1.287 đủ nhỏ để không đổi kết luận và đủ đáng
  để gọi tên thay vì làm tròn bỏ đi; và mới phân loại 15m, sáu interval bị gắn
  cờ còn lại chưa kiểm. File:
  `round235-the-continuity-flags-are-missing-markers-not-missing-data.md`.

- **Round 236 (2026-08-29) — kiểm chứng khẳng định CHƯA TEST của Round 234: nhân
  bốn hold thì lỗ giảm 57% nhưng lỗ MỖI LỆNH gần như không đổi. Giảm tần suất là
  đòn bẩy GIẢM LỖ có đáy bằng 0, không phải đường tới lợi nhuận.** Round 234 đo
  BTC ở cost/gross 48,20 rồi **khẳng định mà không test** rằng "48 lần không lấp
  được chỉ bằng tần suất" — đúng loại khẳng định mà phiên này đã phải rút lại
  nhiều lần, nên đem đo. Dùng `one_target` (đường đo Portfolio duy nhất skill tin
  cho mọi kết luận liên quan hold, bài học r82), binance BTC 5m, 1.800 ngày, chỉ
  đổi `--portfolio-minimum-hold-decisions`: **hold=36 (mặc định production)** →
  3.825 lệnh, 14,87/tuần, PnL **−28,183**, lỗ/lệnh **−0,00737**; **hold=144** →
  1.793 lệnh, **6,97/tuần**, PnL **−12,204**, lỗ/lệnh **−0,00681**. **HÌNH DẠNG
  CHÍNH LÀ CÂU TRẢ LỜI:** lệnh giảm **53,1%**, lỗ giảm **56,7%**, còn **lỗ mỗi
  lệnh chỉ cải thiện 7,6%**. Giảm lỗ đến gần như hoàn toàn từ **giao dịch ÍT
  hơn**, không phải **giao dịch TỐT hơn** — lỗ ≈ số lệnh × một hằng số, tức mô
  hình thuế-cố-định-mỗi-lệnh của r217/r227/r234 nay được xác nhận **ở tầng
  Portfolio trên policy đang deploy**, không còn là suy ra từ sweep Alpha.
  ⇒ Khẳng định của r234 **đứng vững, và phát biểu được mạnh hơn**: giảm tần suất
  hội tụ về **"đừng giao dịch"**, không bao giờ về "giao dịch có lãi". Nhất quán
  và độc lập với r213-215 (lever chi phí đáng ~0) và r231-232 (độ bền quần thể
  ~1,5x ngẫu nhiên) — **ba đường đo khác nhau, cùng một kết luận**. **HAI RÀNG
  BUỘC GẶP NHAU TẠI hold=144:** mức đó cho **6,97 lệnh/tuần** so với sàn Target 3
  là **≥7,0** — gần như đúng ranh giới. Đây là câu trả lời định lượng cho câu hỏi
  mà Round 92 đóng bằng phán đoán ("kéo hold được tới đâu trước khi phá Target
  3?"): với BTC trên cửa sổ này là **hold ≈ 144 (12 giờ), và lỗ ở đó vẫn là
  −12,2**. Quyết định sản phẩm mà r234 nêu nay đã có **cả hai con số**: giữ
  Target 3 làm sàn ⇒ hold trần ~144 ⇒ lỗ ~−12,2 thay vì −28,2; coi Target 3 là
  thương lượng được ⇒ lỗ tiếp tục giảm về 0 khi ngừng giao dịch. **Không nhánh
  nào chạm tới lợi nhuận.** Nghiên cứu không chọn thay được; nó chỉ nói được rằng
  lựa chọn ở đây là giữa **lỗ ít hơn** và **lỗ ít nhất**, không phải giữa lỗ và
  lãi. **KHÔNG khẳng định** hình dạng giữa/ngoài hai điểm — **hai phép đo không
  định nghĩa một đường cong**, và sau bài học r230 tôi không khớp đường cong;
  không khẳng định XAU cũng vậy (nó đã ở 4,52 lệnh/tuần nên dư địa hold ít hơn
  nhiều, chưa chạy); và hold=144 **không phải khuyến nghị** — r87 đã đo hold ×
  stop/take là dưới-cộng-tính nên không được ghép lever bằng giả định. File:
  `round236-frequency-reduction-converges-to-not-trading-not-to-profit.md`.

- **Round 237 (2026-08-29) — đòn bẩy hold trên XAU gần như VÔ TÁC DỤNG, và LỖ
  MỖI LỆNH hoá ra là cùng một hằng số trên cả hai instrument với mọi hold từ 12
  tới 144.** Round 236 đã nêu rõ chưa chạy XAU; vòng này chạy, theo đúng chiều có
  ý nghĩa với XAU là **rút ngắn** hold (kéo dài chỉ phá sàn Target 3 sâu thêm).
  exness XAU 5m, 1.800 ngày, `one_target`: **hold=12** → 907 lệnh, 3,53/tuần, PnL
  **−6,121**, lỗ/lệnh −0,00675; **hold=36 (production)** → 830 lệnh, 3,23/tuần,
  PnL **−5,262**, lỗ/lệnh −0,00634. **Kết quả 1 — trên XAU lever hold gần như
  trơ:** gấp ba hold chỉ đổi số lệnh **−8,5%**, so với BTC gấp bốn hold đổi
  **−53,1%**. Nhìn thấy ngay ở `trade_reduction_fraction`: **0,07-0,15 trên XAU
  so với 0,61-0,82 trên BTC** — ràng buộc hold hiếm khi chạm tới vì tín hiệu vốn
  đã bắn thưa. **Không có lever tần suất đáng kể trên XAU theo bất kỳ chiều nào.**
  **Kết quả 2 — LỖ MỖI LỆNH LÀ MỘT HẰNG SỐ:** gộp bốn phép đo Portfolio của r236
  và r237 — BTC hold36 (3.825 lệnh, −28,183, **−0,00737**/lệnh), BTC hold144
  (1.793, −12,204, **−0,00681**), XAU hold12 (907, −6,121, **−0,00675**), XAU
  hold36 (830, −5,262, **−0,00634**). **Số lệnh biến thiên 4,6 lần, tổng PnL biến
  thiên 5,4 lần, còn lỗ mỗi lệnh chỉ biến thiên 14%** — dải −0,00737…−0,00634
  quanh trung bình **−0,0068**. Hai instrument, hai broker, hold từ 12 tới 144, và
  lỗ mỗi lệnh thực chất là **một con số**: **tổng lỗ = số lệnh × một hằng số, và
  không thứ gì chương trình từng chỉnh làm dịch chuyển hằng số đó.** r217/r227 đo
  ma sát phẳng theo lệnh **trong** một instrument; đây cho thấy kết quả **ròng**
  mỗi lệnh phẳng **xuyên qua** instrument lẫn cấu hình. **Kết quả 3 — giá của
  việc thoả Target 3 trên XAU.** Đo được: rút hold 36→12 mua thêm **+0,30
  lệnh/tuần** với giá **−0,859 PnL** (tệ đi 16%). **Phóng chiếu (ghi rõ là phóng
  chiếu):** để đạt sàn **7,0/tuần** từ 3,23 cần **2,17 lần** số lệnh; ở hằng số
  −0,0068/lệnh thì PnL rơi về khoảng **−11,4**, tức **gần gấp đôi mức lỗ hiện
  tại**; và **không cấu hình nào được tìm thấy thực sự tạo ra 7 lệnh/tuần trên
  XAU**. ⇒ Hai instrument nay trả lời câu hỏi Target 3 **giống nhau từ hai phía
  ngược nhau**: BTC trả giá cho việc thoả sàn bằng cost/gross 48 lần, XAU trả giá
  bằng lỗ gấp đôi. **Sàn đó đắt ở bất cứ đâu nó chạm tới.** **Ghi chú lệch số
  đo:** gate của r234 báo XAU 4,52 lệnh/tuần, `one_target` ở đây báo 3,23 — khác
  đường đo và khác khoảng thời gian (gate chỉ holdout ~360 ngày, one_target cả
  1.800 ngày); cả hai đều xa dưới 7,0 nên kết luận không đổi, **nhưng không được
  trích lẫn lộn hai con số**. **KHÔNG khẳng định** −0,0068 đúng ngoài dải đã đo —
  bốn điểm, một interval, mỗi cái một cửa sổ; tính hằng số là **quan sát trong
  dải đo được, không phải một định luật**. File:
  `round237-loss-per-trade-is-a-universal-constant-across-instruments-and-hold.md`.

- **Round 238 (2026-08-29) — stop/take CÓ dịch chuyển được hằng số mỗi-lệnh mà
  hold không dịch nổi, và nó dịch SAI CHIỀU: ít hơn 67% số lệnh, mỗi lệnh tệ hơn
  65%.** Round 237 đo lỗ mỗi lệnh là hằng số (−0,0068 ±14%) qua hai instrument và
  hold 12→144. Hold chỉ chặn **bao nhiêu** lệnh xảy ra, không chạm vào chuyện gì
  diễn ra **bên trong** một lệnh — **stop/take thì có**. exness XAU 5m, 1.800
  ngày, `one_target`, hold giữ ở mặc định 36: **0,005/0,010** → 831 lệnh, PnL
  −5,293, lỗ/lệnh −0,00637; **0,010/0,020 (production)** → 830 lệnh, −5,262,
  −0,00634; **0,020/0,040** → **275 lệnh**, **−2,876**, **−0,01046**.
  **Kết quả 1 — hạ một nửa mức production KHÔNG đổi gì trên XAU:** 831 vs 830
  lệnh, −5,293 vs −5,262, hai cấu hình không phân biệt được. Round 83 đo đúng
  bước nới này là **giảm lỗ 32-41%** — nhưng trên **BTC**. Trên XAU ở cửa sổ này
  nó là **null**. Không mâu thuẫn r83 (vòng đó chưa từng nói XAU); ghi lại như
  một null **theo instrument** để không giả định lever này chuyển giao được.
  **Kết quả 2 — nhân đôi tiếp thì hằng số ĐỘNG, và động xuống:** 0,010/0,020 →
  0,020/0,040 làm số lệnh giảm **66,9%**, tổng lỗ giảm **45,3%**, nhưng **lỗ mỗi
  lệnh tệ đi 65%**. Stop rộng hơn để mỗi lệnh thua chạy xa hơn trước khi bị cắt;
  tổng lỗ giảm **chỉ vì số lệnh giảm nhanh hơn mức lỗ mỗi lệnh tăng**.
  **BỨC TRANH LEVER PORTFOLIO NAY ĐÃ ĐỦ:** *hold* (r236-237) — giảm mạnh số lệnh,
  lỗ mỗi lệnh **không đổi** ⇒ lỗ tỉ lệ thuận số lệnh; *nới stop/take* (r238) —
  giảm số lệnh mạnh hơn nữa, lỗ mỗi lệnh **tệ đi 65%** ⇒ lỗ giảm nhưng từng lệnh
  xấu đi. **Không lever Portfolio-construction nào trong tay chương trình cải
  thiện được kinh tế mỗi lệnh; chúng chỉ giảm lỗ bằng cách giảm phơi nhiễm, và
  một cái còn làm xấu đi từng lệnh còn lại.** Nhất quán và độc lập với r213-215
  (lever chi phí đáng ~0), r231-232 (độ bền quần thể ~1,5x ngẫu nhiên) và r236
  (giảm tần suất hội tụ về ngừng giao dịch) — **bốn đường đo, một kết luận: tầng
  Portfolio thu nhỏ được khoản lỗ nhưng không đổi được dấu của nó.**
  **Cũng phân rã luôn Round 83**, vòng đó ghi nới stop/take là "giảm lỗ ~41%/32%"
  mà không tách hai hiệu ứng: trên XAU cùng chiều thay đổi đó nay nhìn rõ là
  **67% ít lệnh hơn, mỗi lệnh tệ hơn 65%** — cái "cải thiện" ở tiêu đề là giảm
  **phơi nhiễm**, không phải cải thiện **thực thi**. **KHÔNG khẳng định**
  0,020/0,040 là tốt hơn (route rơi xuống **1,07 lệnh/tuần** trên 275 lệnh, xa
  dưới mọi mục tiêu tần suất và mẫu mỏng hơn nhiều); không khẳng định BTC cũng
  vậy (bước null ở đây lại có hiệu ứng thật ở r83, vòng này không chạy lại BTC);
  và **không khớp đường cong** — ba điểm, một instrument, một cửa sổ, và r87 đã
  đo hold × stop/take là dưới-cộng-tính nên không ghép lever bằng giả định. File:
  `round238-stop-take-moves-the-per-trade-constant-and-makes-it-worse.md`.

- **Round 239 (2026-08-29) — protective theo ATR: nhiều hơn 73% số lệnh ở đúng
  mức lỗ mỗi lệnh cũ, và LỆNH BIÊN có giá bằng LỆNH TRUNG BÌNH.** Round 238 cho
  thấy nới stop **fractional** làm kinh tế mỗi lệnh tệ đi 65% vì stop cố định
  rộng hơn để mọi lệnh thua chạy xa hơn; stop **theo ATR** đúng là cơ chế lẽ ra
  tránh được điều đó vì nó chỉ nới khi biến động cho phép. Đây cũng là mục Rule 1
  duy nhất SUMMARY còn ghi là chưa khai thác, và r82 đóng ATR trên **BTC**
  cross-broker chứ chưa từng thử trên XAU. exness XAU 5m, 1.800 ngày,
  `one_target`, hold 36: **atr_multiple 2,0/4,0 (periods 14)** → **1.433 lệnh**
  (nhiều hơn production 73%), **5,57/tuần**, PnL **−9,459** (lỗ nhiều hơn 80%),
  nhưng **lỗ/lệnh −0,00660 so với −0,00634** — chỉ lệch **4%**, nằm gọn trong dải
  14% mà r237 đo cho hằng số. ⇒ **ATR đổi SỐ LƯỢNG chứ không đổi HẰNG SỐ**: nó
  hành xử như lever hold, không như nới fractional, và là **lever đầu tiên đo
  được làm số lệnh TĂNG**. Bảng lever nay: *hold* giảm mạnh số lệnh / hằng số
  không đổi; *nới fractional* giảm số lệnh / hằng số **tệ đi 65%**; *atr_multiple*
  **tăng 73%** số lệnh / hằng số không đổi. **DẠNG SẮC NÉT NHẤT CỦA MÔ HÌNH:**
  vì ATR **thêm** lệnh chứ không bớt, kinh tế **biên** tính được trực tiếp —
  thêm **603 lệnh**, thêm **−4,197** lỗ ⇒ **lỗ biên mỗi lệnh −0,00696** so với
  trung bình production −0,00634, **lệch trong vòng 10%**. **Lệnh biên có giá
  bằng lệnh trung bình.** Không tồn tại tập con lệnh nào tốt hơn: thêm 603 lệnh
  thì thêm lỗ đúng bằng tốc độ 830 lệnh cũ đang lỗ. ⇒ **trung bình và biên bằng
  nhau, nên không phép chọn lọc hay tiết chế lệnh nào đổi được kết quả trên mỗi
  đơn vị giao dịch** — đóng vòng r236-238: giao dịch ít thì lỗ ít, giao dịch
  nhiều thì lỗ nhiều, và không gì trong tay đổi được **tốc độ**. Ghi thêm: ATR
  đẩy tần suất lên **5,57/tuần**, gần sàn Target 3 (7,0) hơn hẳn mức 3,23 của
  production — và cái giá là lỗ nhiều hơn 80%; đúng đánh đổi r234/r237, đo trên
  lever thứ ba, ở cùng một tốc độ hằng số. **KHÔNG khẳng định** các multiple/
  periods ATR khác cũng vậy (mới chạy 2,0/4,0 ở periods 14; **biến thiên
  `--portfolio-atr-periods` vẫn còn mở**), cũng không khẳng định ATR tệ trên BTC
  (r82 đã đóng ở đó, vòng này không chạy lại). **Ngân sách:** ba lần khởi container,
  hai cái hoàn tất — cái đầu bị argument validation từ chối trong 45 giây vì tôi
  truyền `--portfolio-protective-kind atr` trong khi giá trị hợp lệ là
  `atr_multiple` (`execution_rules.rs:157`); không tốn công backtest nào nhưng vẫn
  là một lần khởi container trên hạn mức hai, nên ghi lại thay vì bỏ qua. File:
  `round239-atr-protective-adds-trades-at-the-same-per-trade-loss.md`.

- **Round 240 (2026-08-29) — `--portfolio-atr-periods` cuối cùng cũng được biến
  thiên và hoá ra TRƠ, đóng nốt mục Rule 1 còn mở; và hằng số mỗi-lệnh nay đứng
  vững qua CHÍN cấu hình.** Backlog mang mục này suốt nhiều vòng như "mục duy
  nhất còn thật sự mở trong Rule 1", ưu tiên thấp vì production dùng
  `fractional`; r239 mới chạy ATR ở periods 14 và để ngỏ chính cái period.
  exness XAU 5m, 1.800 ngày, `one_target`, hold 36, `atr_multiple` 2,0/4,0:
  **periods 7** → 1.443 lệnh / −9,743 / **−0,00675**/lệnh; **14** → 1.433 /
  −9,459 / **−0,00660**; **28** → 1.409 / −8,917 / **−0,00633**. **Tham số này
  TRƠ trên cả hai trục:** số lệnh đổi **1,02 lần** khi period đổi 4 lần; lỗ mỗi
  lệnh đổi **6,3%**, nằm trong dải 14%. **Ghi chú trung thực về sức nặng của phép
  test:** mô hình dự đoán "số lượng đổi, hằng số không đổi" — hằng số quả thực
  không đổi, **nhưng số lượng cũng gần như không đổi**, nên đây là xác nhận
  **yếu** chứ không mạnh; phép test mạnh vẫn là r237 (hold) và r239 (ATR làm
  tăng số lệnh). Cái nó chốt được là **mục backlog: `atr_periods` không phải một
  lever, có thể ngừng liệt kê là đang mở.** **HẰNG SỐ MỖI-LỆNH ĐẦY ĐỦ, chín cấu
  hình r236-240:** BTC hold36 −0,00737; BTC hold144 −0,00681; XAU hold12
  −0,00675; XAU hold36 (prod) −0,00634; XAU frac 0,005/0,010 −0,00637; **XAU frac
  0,020/0,040 −0,01046**; XAU atr p7 −0,00675; atr p14 −0,00660; atr p28
  −0,00633. **Số lệnh trải từ 275 tới 3.825 = 13,9 lần.** Cả chín trải 39,5%;
  **loại đúng một cấu hình đã dịch được hằng số** (stop cố định rộng của r238)
  thì **tám cái còn lại nằm trong dải 14,1%**, trung bình **−0,00666**, độ lệch
  chuẩn **0,00032**. **Hai instrument, hai broker, hold 12-144, ba cơ chế
  protective, ATR periods 7-28, biên độ số lệnh 13,9 lần — và lỗ mỗi lệnh là
  −0,0067 ± 5% ở tám trên chín trường hợp. Một lever trên năm dịch được nó, và
  cái đó làm nó TỆ ĐI 65%.** **CHỐT:** không gian tìm kiếm Portfolio-construction
  **đã cạn** với bộ lever chương trình có; tổng lỗ bám theo số lệnh gần như máy
  móc, và kết quả biên-bằng-trung-bình của r239 giải thích vì sao — **không tồn
  tại tập con hay cấu hình lệnh nào có kinh tế khác đi**. Lối ra còn lại nằm
  **ngoài tầng này**: một tín hiệu Alpha có edge dương thật trên mỗi lệnh
  (r231-232 đo độ bền quần thể chỉ ~1,5x ngẫu nhiên), hoặc ma sát thật thấp hơn
  (r213-215 đo các lever chi phí khả dụng đáng ~0). **Không cái nào là một tham số
  Portfolio.** File:
  `round240-atr-periods-is-inert-and-the-per-trade-constant-holds-across-nine-configurations.md`.

- **Round 241 (2026-08-29) — đo gross edge tầng Portfolio trên TOÀN BỘ 5 năm: XAU
  chỉ bằng ~5% ma sát, còn BTC ÂM NGAY CẢ KHI KHÔNG MẤT PHÍ.** Chuỗi r213-217 và
  r234 dựng nên luận điểm "gross edge dương, bị ma sát giết"; nhưng tất cả các
  phép đo đó hoặc ở tầng Alpha, hoặc (r234) là gate chỉ chạy **holdout ~360
  ngày**. Gross edge tầng Portfolio trên **toàn cửa sổ 1.800 ngày** chưa từng
  được đo. `one_target`, 5m, hold 36, zero cost: **exness XAU** 1.787 lệnh,
  **+0,683**, gross **+0,00038**/lệnh — so với ma sát ~0,0070 thì chỉ bằng **~5%
  ma sát**; **binance BTC** 3.312 lệnh, **−2,658**, gross **−0,00080**/lệnh.
  **BTC lỗ ngay cả khi phí = 0, slippage = 0, funding = 0.** Không phải "edge nhỏ
  hơn ma sát" — trên 5 năm **không có edge nào để mà nhỏ hơn**. **BẪY ĐÃ TRÁNH VÀ
  GHI LẠI:** run có phí và run không phí cho **số lệnh khác nhau** (830 vs 1.787
  ở XAU, chênh 2,2 lần) vì chi phí dịch giá khớp nên đổi luôn việc lệnh nào chạm
  protective; **lấy hiệu gross−net giữa hai run là SAI**, đúng lỗi không-trực-giao
  của r214 — nên mỗi run chỉ được tính chỉ số theo số lệnh của chính nó, không
  trừ gì cả. (Ghi chú phương pháp: cấu hình chi phí **đổi đáng kể số lệnh** ở tầng
  Portfolio, khác với độ dài lịch sử mà r226 đã chứng minh là sạch.)
  **QUALIFY LUẬN ĐIỂM TRUNG TÂM CỦA CẢ PHIÊN:** r234 báo **cả hai** route có
  gross dương (+0,475 XAU, +0,281 BTC) nhưng gate đó chỉ chạy holdout ⇒ **"gross
  edge dương bị ma sát giết" là tính chất của CỬA SỔ GẦN ĐÂY** — đúng với XAU ở
  cả hai span, đúng với BTC **chỉ** ở span gần. Nhất quán với walk-forward r227
  (hai segment XAU cũ nhất đều âm) và r225 (candidate BTC tốt nhất yếu ở đoạn
  900→180 ngày trước): hệ thống trông càng đẹp khi cửa sổ càng gần, và hiệu ứng
  đó đủ mạnh để **đảo dấu** gross edge của BTC. **Ảnh hưởng tới mô hình:** "lỗ =
  số lệnh × hằng số, không lever Portfolio nào dịch được hằng số" của r236-240
  **vẫn đứng** (đo trên run có phí, vòng này không đụng tới). Cái thay đổi là
  **lý do** hằng số ấy âm: với XAU là ma sát lấn át một edge thật nhưng nhỏ; với
  BTC trên toàn cửa sổ **không phải ma sát gì cả** — tín hiệu vốn đã âm, ma sát
  chỉ đào sâu thêm. **Hai route, hai căn bệnh khác nhau, trước giờ bị mô tả như
  một.** **KHÔNG khẳng định** tách được sạch gross/ma sát cho route nào (số lệnh
  lệch nên không tách được); không nói gate r234 sai (nó đo span khác, và **chính
  sự bất đồng đó mới là phát hiện**); và **không khẳng định +0,00038 của XAU là
  dương có ý nghĩa** — nó bằng 5% ma sát trên một cửa sổ, mà r230-232 đã cho thấy
  số ở cỡ này không phân biệt được với nhiễu nếu thiếu biên độ, thứ vòng này chưa
  tính. File:
  `round241-portfolio-gross-edge-is-a-recent-window-property-and-btc-is-negative-over-five-years.md`.

- **Round 242 (2026-08-29) — gross edge của XAU BỀN VỀ DẤU qua ba cửa sổ, và phân
  rã theo dải cho thấy 900 ngày CŨ NHẤT là ÂM.** Round 241 đo gross Portfolio của
  XAU là **+0,00038**/lệnh trên 1.800 ngày rồi tự gắn cờ: *"bằng 5% ma sát trên
  một cửa sổ, mà r230-232 đã cho thấy số ở cỡ này không phân biệt được với nhiễu
  nếu thiếu biên độ — thứ vòng này chưa tính"*. Vòng này tính biên độ đó.
  exness XAU 5m, `one_target`, hold 36, **toàn bộ chi phí = 0**: **450 ngày** →
  693 lệnh, +0,741, **+0,00107**/lệnh; **900 ngày** → 1.034 lệnh, +2,505,
  **+0,00242**; **1.800 ngày** → 1.787 lệnh, +0,683, **+0,00038**. **Dấu dương ở
  cả ba** ⇒ edge **không** phải hiện tượng một-cửa-sổ. Độ lớn trải **6,3 lần** và
  **không đơn điệu** — 900 ngày tốt nhất, toàn lịch sử tệ nhất. **PHÂN RÃ THEO
  DẢI LỊCH RỜI NHAU** (phép trừ được **r226 cho phép**, vì vòng đó chứng minh mỗi
  nến được đánh giá độc lập với lịch sử phía trước — ghi rõ đây là **suy luận**,
  vì r226 chứng minh cho holdout cố định dưới lịch sử biến thiên, một thiết lập
  gần chứ không đồng nhất): **900-1800 ngày trước** → 753 lệnh, **−1,822**,
  **−0,00242**/lệnh = **−35% ma sát**; **450-900** → 341 lệnh, +1,764, **+0,00517**
  = **74% ma sát**; **0-450** → 693 lệnh, +0,741, **+0,00107** = **15% ma sát**.
  ⇒ Con số toàn-lịch-sử nhỏ **là vì 900 ngày cũ nhất âm**, không phải vì edge
  nhỏ đều — xác nhận walk-forward tầng Alpha của r227 **ở tầng Portfolio**, qua
  một đường độc lập. **CHỐT ĐƯỢC:** edge không phải nhiễu. **KHÔNG chốt được:**
  nó có đủ lớn để có ý nghĩa không — dải tốt nhất mới đạt **74% ma sát**, còn
  **450 ngày gần nhất chỉ 15%**; nghĩa là **ngay cả dải tốt nhất cũng không tự
  trả nổi chi phí**, và dải gần nhất — dải có ý nghĩa cho việc deploy — lại là
  cái yếu hơn trong hai dải dương. Headline của r241 vẫn đứng nhưng phải đổi trọng
  tâm: con số đó **có thật và không đủ**, và nó đang **teo lại** ở dải gần nhất so
  với dải trước đó. **Đây là đường thứ TƯ độc lập dẫn tới cùng một hình dạng**
  (r227 Alpha walk-forward, r234 gate holdout, r241 Portfolio toàn cửa sổ, r242
  phân rã dải) — cả bốn đồng thuận và **không cái nào chạm hoà vốn**; sự nhất
  quán đó đáng giá hơn bất kỳ con số đơn lẻ nào. **KHÔNG khẳng định** ba dải phân
  biệt được với nhau về mặt thống kê (341-753 lệnh, không có khoảng tin cậy —
  cái được khẳng định là **mẫu dấu**, không phải thứ tự độ lớn); và chưa phân rã
  dải cho BTC (r241 đo gross toàn cửa sổ của nó là **âm**). File:
  `round242-xau-gross-edge-is-sign-robust-but-the-oldest-band-is-negative.md`.

- **Round 243 (2026-08-29) — dải gần nhất của BTC cũng DƯƠNG: khẳng định "hai căn
  bệnh khác nhau" của chính tôi ở Round 241 BỊ BÁC BỎ.** Round 241 đo gross toàn
  cửa sổ của BTC là −0,00080/lệnh rồi kết luận *"XAU là ma sát lấn át một edge
  thật; BTC thì tín hiệu vốn đã âm — hai route, hai căn bệnh"*. Round 242 sau đó
  phân rã XAU và cho thấy con số toàn-cửa-sổ nhỏ **là vì dải cũ nhất âm**, đồng
  thời ghi rõ **chưa phân rã BTC**. Vòng này phân rã BTC. **Kết quả (zero cost,
  binance BTC 5m, hold 36):** cửa sổ 450 ngày → 716 lệnh, **+0,558**; 900 ngày →
  1.708 lệnh, −0,387; 1.800 ngày → 3.312 lệnh, −2,658. **Dải:** 900-1800 ngày
  trước **−0,00142**/lệnh (−20% ma sát), 450-900 **−0,00095** (−14%), và
  **0-450 = +0,00078 (+11%)**. ⇒ **450 ngày gần nhất của BTC là DƯƠNG**; số âm
  toàn cửa sổ đến hoàn toàn từ hai dải cũ. **So sánh cạnh nhau với XAU (r242):**
  dải 900-1800 −0,00242 (XAU) vs −0,00142 (BTC); 450-900 **+0,00517** vs
  **−0,00095**; **0-450 +0,00107 (15%) vs +0,00078 (11%)**. **Hai route CÙNG MỘT
  HÌNH DẠNG** — dải cũ nhất âm, dải gần nhất dương, và hai con số gần nhất **hội
  tụ trong khoảng 37%**; chúng chỉ khác ở dải giữa. **Khẳng định "hai căn bệnh"
  rút lại:** nó là artifact của việc đem bức tranh **đã phân rã** của XAU so với
  **tổng gộp chưa phân rã** của BTC — đúng lỗi tổng-gộp mà r242 vừa sửa cho XAU,
  lặp lại một vòng sau trên instrument kia. **PHÁT BIỂU THAY THẾ, phủ cả hai
  route:** *tầng Portfolio có một gross edge dương nhỏ **chỉ giới hạn trong ~450
  ngày gần nhất**, đáng **11-15% ma sát**; mọi thứ cũ hơn đều âm; và cả hai route
  cần **khoảng 7-9 lần** gross edge mỗi lệnh nữa mới hoà vốn.* Khớp với r227
  (walk-forward tầng Alpha), r234 (gate holdout), r242 (dải XAU) — **năm đường đo,
  một hình dạng**. **KHÔNG khẳng định** ý nghĩa thống kê của hai dải dương gần
  nhất (716 và 693 lệnh, không khoảng tin cậy, và biên độ ở đây là qua **cửa sổ
  lồng nhau** chứ không phải mẫu độc lập); cũng không khẳng định chênh lệch ở dải
  giữa (XAU +74% vs BTC −14%) có ý nghĩa gì. File:
  `round243-btc-recent-band-is-positive-too-the-two-diseases-claim-was-wrong.md`.

- **Round 244 (2026-08-29) — bổ dải gần nhất của XAU thành ba: DẤU thì rộng khắp
  (3/3 dương) nhưng ĐỘ LỚN đang teo, và 150 ngày mới nhất coi như BẰNG KHÔNG.**
  Round 243 tự gắn cờ: *"chưa khẳng định ý nghĩa thống kê của hai dải dương gần
  nhất… biên độ ở đây là qua cửa sổ lồng nhau chứ không phải mẫu độc lập"*. Thứ
  thay thế được cho một kiểm định là **bổ dải gần nhất thành các đoạn RỜI NHAU**
  rồi hỏi: edge trải rộng hay do một đoạn gánh? exness XAU 5m, `one_target`,
  hold 36, zero cost — cửa sổ 150 ngày → 175 lệnh, +0,015; 300 ngày → 473 lệnh,
  +0,557; 450 ngày → 693 lệnh, +0,741. **Ba đoạn rời nhau:** **300-450 ngày
  trước** +0,00084/lệnh (**12,0%** ma sát); **150-300** **+0,00182** (**26,0%**);
  **0-150** **+0,00008** (**1,2%**). **HAI CÁCH ĐỌC, cả hai đều quan trọng:**
  (1) **Dấu trải rộng** — cả ba đoạn rời nhau đều dương, **3/3**; edge gần đây
  **không** phải sản phẩm của một quãng may mắn, và đây là phát biểu mạnh nhất có
  thể đưa ra khi không có kiểm định thật. (2) **Độ lớn đang teo và đoạn mới nhất
  coi như bằng 0**: đi theo thời gian là **12,0% → 26,0% → 1,2%**; 150 ngày gần
  nhất tạo ra **+0,015 tổng gross trên 175 lệnh** — dương về dấu nhưng **không
  phân biệt được với 0** về thực chất. **Ảnh hưởng tới câu chuyện "edge gần đây":**
  r242-243 chốt *"gross edge dương nhỏ, chỉ trong ~450 ngày gần nhất, đáng 11-15%
  ma sát, trên cả hai instrument"* — với XAU thì phát biểu đó nay **quá hào
  phóng**: con số 15% là trung bình của một giai đoạn mà **một phần ba mới nhất
  chỉ đóng góp ~1%**. **Phát biểu lại cho XAU:** *gross edge dương là thật về dấu
  trên ba đoạn rời nhau, nhưng nó tập trung ở khoảng 150-450 ngày trước và đã teo
  về xấp xỉ 0 trong 150 ngày gần nhất.* Điều này quan trọng hơn con số tổng, vì
  **đoạn mới nhất mới là đoạn dự báo thứ mà việc deploy sẽ gặp ngay bây giờ**.
  **KHÔNG khẳng định** đây là xu hướng thay vì ba lượt rút (ba đoạn, 175-298 lệnh,
  không khoảng tin cậy — bài học r230 áp cho **thứ tự độ lớn**, dù mẫu dấu 3/3
  mới là thứ được khẳng định); không nói đoạn mới nhất đã **âm** (nó dương, chỉ
  là không đáng kể — phát biểu là "không phân biệt được với 0", không phải "đã
  đảo chiều"); và **chưa bổ dải cho BTC** — đó là vòng kế tiếp hiển nhiên, vì dải
  0-450 của nó đọc ra +0,00078 ở r243 mà chưa biết một phần ba mới nhất có cũng
  gần 0 hay không. File:
  `round244-the-recent-edge-is-broad-in-sign-but-decaying-and-the-newest-150-days-are-zero.md`.

- **Round 245 (2026-08-29) — bổ dải BTC thành ba: 2/3 dương, và CẢ HAI instrument
  đều đạt đỉnh ở CÙNG MỘT KHUNG LỊCH.** Đúng phép test r244 đã nêu. binance BTC
  5m zero-cost: cửa sổ 150 ngày → 233 lệnh, +0,130; 300 → 569 lệnh, +0,817;
  450 → 716 lệnh, +0,558. **Ba đoạn rời nhau:** 300-450 ngày trước **−0,00176**
  (−25,1% ma sát), 150-300 **+0,00204** (+29,2%), 0-150 **+0,00056** (+8,0%) ⇒
  **BTC 2/3 dương**, không phải 3/3 như XAU — đoạn cũ nhất của nó âm.
  **NỘI DUNG THẬT SỰ CỦA VÒNG NÀY:** so cạnh nhau — 0-150: XAU +0,00008 (1,2%)
  vs BTC +0,00056 (8,0%); **150-300: XAU +0,00182 (26,0%) vs BTC +0,00204
  (29,2%)**; 300-450: XAU +0,00084 (12,0%) vs BTC −0,00176 (−25,1%). **Đoạn
  150-300 ngày là đoạn mạnh nhất trên CẢ HAI instrument, và hai giá trị lệch nhau
  trong vòng 12%** — dù là hai tài sản khác nhau trên hai broker khác nhau.
  **Sự trùng khớp đó chỉ về một hướng khó chịu:** *một edge của CHIẾN THUẬT lẽ ra
  phải mang tính riêng theo instrument và phải bền; còn một edge xuất hiện ở
  **cùng một khung lịch trên các instrument không liên quan** rồi tắt sau đó thì
  giống một **REGIME THỊ TRƯỜNG** hơn là một thuộc tính chiến thuật.* Và 150 ngày
  mới nhất của cả hai đều chỉ dương yếu (1,2% và 8,0%) — khung mạnh dùng chung
  **đã đi qua**. Nhất quán với r220 (biến động gần đây tăng ~2 lần) và r228
  (không thống kê giá đơn lẻ nào giải thích được các bước chuyển). Nó **định
  khung lại** "edge dương nhỏ gần đây" của r242-244: có thể đó chỉ là **một giai
  đoạn thị trường thuận lợi**, nhìn qua bất kỳ chiến thuật nào đang chĩa vào nó.
  **ĐỘ MẠNH BẰNG CHỨNG, nói thẳng:** với ba đoạn, việc hai instrument cùng đạt
  đỉnh ở một đoạn xảy ra **1 lần trong 3** hoàn toàn do may; thứ nâng nó lên là
  **độ lớn đỉnh cũng khớp trong 12%** — nhưng hai con số khớp nhau thì vẫn chỉ là
  hai con số. **GỢI Ý, CHƯA XÁC LẬP** — tôi phát biểu đúng như vậy vì r230 và
  r232 đều đã bắt được tôi trình bày một khuôn mẫu ở đúng mức bằng chứng này như
  thể là một phát hiện. **PHÉP TEST PHÂN BIỆT CHO VÒNG SAU:** chạy **instrument
  thứ ba** (bybit BTC hoặc bybit XAUT, cả hai đã được r210 hiệu chuẩn làm nguồn
  độc lập) — nếu là regime thì nó cũng phải đạt đỉnh ở 150-300, đưa xác suất trùng
  hợp từ 1-trên-3 xuống 1-trên-9; chưa phải chứng minh, nhưng là một cập nhật
  thật. File:
  `round245-both-instruments-peak-in-the-same-calendar-band-which-looks-like-regime-not-edge.md`.

- **Round 246 (2026-08-29) — instrument THỨ BA cũng đạt đỉnh ở cùng khung lịch
  (3/3), đoạn mới nhất của nó ÂM RÕ — nhưng POLICY DÙNG CHUNG là confound tôi
  chưa tách được.** Đúng phép test r245 nêu, chọn **bybit XAUT/USDT**: là vàng
  (instrument ưu tiên), venue và tài sản thật sự khác (spot Tether Gold chứ không
  phải CFD), đã được r210 hiệu chuẩn làm nguồn độc lập. Zero cost, 5m, hold 36:
  cửa sổ 150 ngày → 150 lệnh, **−0,325**; 300 ngày → 398 lệnh, **+1,371**.
  **Hai đoạn:** **0-150** = **−0,00217**/lệnh (**−31,0%** ma sát, ÂM);
  **150-300** = **+0,00684** (**+97,7%** ma sát — gần hoà vốn nhất trong mọi phép
  đo của cả phiên). **3/3:** exness XAU +0,00008 vs +0,00182; binance BTC
  +0,00056 vs +0,00204; bybit XAUT −0,00217 vs +0,00684 — **cả ba đều mạnh hơn ở
  150-300**, trên ba instrument không liên quan thuộc ba broker. **Xác suất null,
  nói chính xác thay vì làm tròn có lợi cho mình:** đây là so sánh **hai đoạn**
  cho mỗi instrument, nên 3/3 cùng chiều là **1 trên 8 (12,5%)** dưới giả thuyết
  tung đồng xu; còn trên hai instrument có đủ ba đoạn thì cùng đạt đỉnh ở một
  trong ba là **1 trên 9**. r245 hứa "1-trên-9" nhưng phép test tôi thực sự chạy
  trên instrument thứ ba là dạng hai đoạn — nên phát biểu trung thực là **cả hai
  con số đó**, không phải một con số mạnh hơn. **CONFOUND TÔI CHƯA TÁCH ĐƯỢC, và
  nó quan trọng:** cả ba instrument chạy **cùng một registry chiến thuật và cùng
  một Portfolio decision policy** — các instrument thì độc lập, **policy thì
  không**. Hai lời giải vẫn tương đương về mặt quan sát: (1) **regime thị
  trường** — khung 150-300 thuận lợi xuyên tài sản, chiến thuật hợp lý nào cũng
  thấy; (2) **policy dùng chung** — chính policy này hợp giai đoạn đó, và nó sẽ
  trông y hệt trên mọi instrument vì **nó là cùng một policy**. r228 (không thống
  kê giá đơn lẻ nào bám được các bước chuyển) làm yếu bớt nhánh regime thuần nhưng
  không chốt được. **PHÉP TEST TÁCH BẠCH cần một họ chiến thuật khác về mặt cơ
  chế**, đánh giá trên cùng các đoạn: nếu policy khác cũng đạt đỉnh ở 150-300 thì
  là regime; nếu đỉnh rơi chỗ khác thì chính policy dùng chung đang tạo ra hiệu
  ứng. **Chưa chạy.** Tới lúc đó phát biểu dừng ở: *hiệu ứng có dùng chung giữa
  các instrument, và nguồn gốc chưa được xác định.* **Đọc theo góc deploy** thì
  không đổi và hơi xấu đi: 150 ngày gần nhất đọc ra **+1,2%** (XAU), **+8,0%**
  (BTC), **−31,0%** (bybit XAUT) ma sát — hai cái gần 0, một cái âm rõ. File:
  `round246-third-instrument-confirms-the-shared-window-but-policy-is-the-confound.md`.

- **Round 247 (2026-08-29) — phép test tách bạch: ba họ cơ chế KHÔNG liên quan
  cũng đạt đỉnh ở 150-300, nhưng REVERSION đi NGƯỢC lại. Khung đó mang tính ĐỊNH
  HƯỚNG, không phải "dễ ăn đều".** Round 246 để lại confound: ba instrument đều
  chạy **cùng một Portfolio policy**, nên "regime thị trường" và "policy hợp giai
  đoạn" tương đương về quan sát; phép tách bạch nó nêu là **một họ chiến thuật
  khác về cơ chế trên cùng các đoạn**. Alpha sweep cung cấp đúng thứ đó — 68
  candidate thuộc những họ mà policy đang deploy hầu như không dùng. exness XAU
  5m, zero cost, candidate có ≥30 lệnh ở cả hai đoạn, gộp theo họ:
  **breakout (15)** +0,00082 → **+0,00294** (gấp 3,6 lần, mức tăng lớn nhất);
  **trend/momentum (24)** +0,00020 → +0,00031; **other (11)** +0,00008 → +0,00013;
  **reversion (18)** **−0,00048 → −0,00124** (ngoại lệ — âm ở cả hai đoạn và **tệ
  hơn** ở 150-300). **3/4 họ đạt đỉnh ở 150-300.** **BẰNG CHỨNG CHỐNG LẠI nhánh
  "chỉ do policy dùng chung":** breakout là họ mà policy gần như **không** dùng
  (trọng số production do `candle_momentum` và `rsi_mean_reversion` chi phối, theo
  checkpoint r206/r233) — vậy mà nó thể hiện hiệu ứng **mạnh nhất**. **NHƯNG
  reversion đi ngược**, nên khung đó **không** thuận lợi đồng đều. Mô tả đúng là:
  **khung 150-300 ngày ƯU ÁI cơ chế định hướng (breakout, momentum) và TRỪNG PHẠT
  mean-reversion.** Đây **không phải giả thuyết bịa ra cho khớp bảng**: r228 đã
  **đo độc lập** đúng bước chuyển đó — Kaufman efficiency tăng gấp đôi (0,0366 →
  0,0753) và drift tăng gấp đôi (+13,9% → +26,9%) **trong khi biến động GIẢM**.
  Tính định hướng tăng, reversion bị phạt — **hai đường độc lập, cùng một kết
  luận**. **Vị thế câu hỏi của r246:** nhánh "chỉ do policy" **yếu đi** (họ policy
  không dùng lại thể hiện mạnh nhất); nhánh "regime đồng đều" **yếu đi**
  (reversion ngược chiều); **"regime định hướng"** nhất quán với cả vòng này lẫn
  r228. Chưa chốt, nhưng **không còn là hai cách đọc ngang nhau**. Khoảng trống
  còn lại: "regime định hướng" là một **mô tả, không phải nguyên nhân** — r228 đã
  cho thấy không thống kê giá đơn lẻ nào bám được **tất cả** các bước chuyển, và
  vòng này không đổi điều đó. **KHÔNG khẳng định** cách chia họ là chuẩn (đó là
  heuristic khớp chuỗi của riêng tôi, đúng cái dùng ở r217, không phải taxonomy
  đọc từ code); không khẳng định các số gộp theo họ không bị vài candidate nhiều
  lệnh chi phối; và đây là tầng **Alpha**, không phải Portfolio. File:
  `round247-the-shared-window-favoured-direction-and-punished-reversion.md`.

- **Round 248 (2026-08-29) — kiểm theo TỪNG CANDIDATE: kết quả breakout SỐNG SÓT,
  còn cách đếm "3/4 họ" thì KHÔNG.** Round 247 tự ghi giới hạn: *"chưa khẳng định
  các số gộp theo họ không bị vài candidate nhiều lệnh chi phối"*. Đó là con số
  chịu lực của cả vòng nên phải kiểm, theo đúng luật r230 (báo cáo biên độ, không
  báo cáo một số gộp). exness XAU 5m, zero cost, candidate ≥30 lệnh ở cả hai đoạn
  — **gộp vs TRUNG VỊ vs số candidate cải thiện:** **breakout (15)** gộp
  +0,00083→+0,00294, **trung vị +0,00056→+0,00278**, **9/15** cải thiện;
  **trend/momentum (24)** gộp +0,00020→+0,00031 **nhưng trung vị +0,00030→+0,00028
  (đi NGƯỢC lại)**, 15/24 (gần tung đồng xu); **other (11)** 6/11 trên độ lớn gần
  0; **reversion (18)** gộp −0,00049→−0,00123, **trung vị −0,00034→−0,00241** (tệ
  đi 7 lần), chỉ **6/18** cải thiện. **BREAKOUT SỐNG SÓT và được hậu thuẫn tốt hơn
  cả ở r247** — mức tăng trải trên **bảy cơ chế khác nhau về cấu trúc**
  (`opening_range_breakout_london_30m/60m`, `donchian_breakout_100/200`,
  `fibonacci_golden_zone_50`, `atr_breakout_14_3_0`, `bollinger_breakout_20_2`),
  không phải artifact của một vài outlier. **TREND/MOMENTUM KHÔNG SỐNG SÓT** —
  việc r247 xếp nó vào "3/4 họ" là **artifact của phép gộp**. **Cách đếm đã sửa:
  MỘT họ tăng rõ (breakout), MỘT họ giảm rõ (reversion), HAI họ không phân biệt
  được với nhiễu.** Và cách đếm này làm câu chuyện **sạch hơn chứ không yếu đi**,
  vì nó khớp với thống kê giá của r228 theo cách bản "3/4" không khớp được: r228
  đo cùng bước chuyển đó thấy **Kaufman efficiency gấp đôi** (0,0366→0,0753) và
  **drift gấp đôi** (+13,9%→+26,9%) trong khi **tự tương quan lag-1 phẳng/giảm**
  (+0,0315→+0,0276). **Momentum bám vào tự tương quan — thứ KHÔNG cải thiện;
  breakout bám vào efficiency và drift — cả hai đều gấp đôi.** Họ lẽ ra phải phản
  ứng thì đã phản ứng, họ lẽ ra không thì đã không. **Hai đường đo độc lập khớp
  nhau ở mức chi tiết này là sự nhất quán mạnh nhất mà mạch nghiên cứu này tạo
  ra.** Lập luận chịu lực của r247 (breakout — họ mà policy gần như không dùng —
  thể hiện hiệu ứng mạnh nhất, phản bác nhánh "chỉ do policy dùng chung") **không
  bị ảnh hưởng và còn được hậu thuẫn tốt hơn**. **KHÔNG khẳng định** ý nghĩa thống
  kê (11-24 candidate mỗi họ, không khoảng tin cậy; 9/15 là gợi ý, 15/24 thì
  không), taxonomy họ vẫn là heuristic của riêng tôi, và **quan hệ nhân quả giữa
  thống kê r228 với phản ứng của các họ chưa được test bằng cấu trúc** (mới chỉ
  là nhất quán). File:
  `round248-per-candidate-check-breakout-survives-momentum-does-not.md`.

- **Round 249 (2026-08-29) — ở 4h, 13/14 candidate trend/momentum cải thiện ở dải
  150-300; nhưng p-value danh nghĩa BỊ THỔI PHỒNG NẶNG vì các candidate là biến
  thể của nhau.** Ghép hai phát hiện tốt nhất của phiên mà chưa từng ghép: r218
  (4h ít bị chi phí trói hơn 5m nhiều) và r248 (các họ định hướng mới là họ phản
  ứng với khung 150-300) — r247-248 chỉ chạy ở 5m. exness XAU **4h**, zero cost,
  candidate ≥30 lệnh ở cả hai dải: breakout **n=2** (−0,01585→+0,02714, 2/2);
  **trend/momentum n=14, trung vị −0,00007 → +0,01183, 13/14 cải thiện, bằng
  169,0% ma sát**; other n=5 (2/5); reversion n=3 (0/3). Chỉ trend/momentum có
  quần thể dùng được — breakout tụt xuống n=2 ở 4h vì phần lớn candidate rơi dưới
  sàn trade, nên **không so sánh họ được** như r248 làm ở 5m. Số lệnh thì thoải
  mái vượt sàn: trung vị 68 và 76 mỗi dải, thấp nhất 32. **CẢNH BÁO PHẢI ĐẶT
  TRƯỚC:** sign test một phía trên 13/14 cho **p = 0,0009**, và **con số đó bị
  thổi phồng nặng, không được trích**. 14 candidate **không độc lập** — năm cái là
  biến thể của `candle_momentum` (10bps, 30bps, session_london_ny_overlap,
  session_exclude_asian, rv_regime_filter), hai cái `sma_trend` (20/50), hai cái
  `macd_trend`, hai cái `heikin_ashi_momentum`, còn lại `parabolic_sar`,
  `ema_crossover_5_20`, `obv_trend_20`. Tức khoảng **5-6 cơ chế thật sự khác
  nhau**, không phải 14 lượt rút; ở n=6 thì 5/6 hay 6/6 cho p ≈ 0,1 hoặc 0,016 —
  gợi ý, xa 0,0009 cả một bậc. **Nói thẳng: 13/14 trông mạnh hơn thực tế, và tôi
  không trình bày nó như mức ý nghĩa.** r230, r232 và r248 đều đã bắt được tôi
  trình bày một con số ở đúng mức bằng chứng này như một phát hiện. **THỨ SỐNG SÓT
  sau khi trừ hao:** (1) **mức cải thiện trung vị lớn — +0,01183/lệnh = 169% ma
  sát**, con số cấp-họ đầu tiên của cả phiên **vượt ma sát**, trên quần thể mà mọi
  số lệnh đều qua sàn; (2) **chiều nhất quán với bằng chứng độc lập** — r228 đo
  efficiency và drift gấp đôi ở đúng bước chuyển này, r218 đo edge/lệnh tăng theo
  interval, nên một regime định hướng hiện rõ hơn ở 4h so với 5m là điều **cả hai
  đều dự đoán**. **XUNG ĐỘT với r248:** ở **5m** cùng họ đó **không** sống sót
  (15/24, trung vị phẳng); ở **4h** là 13/14 với trung vị lớn — hoặc hiệu ứng thật
  sự **phụ thuộc interval** (hợp lý theo r218), hoặc một trong hai là nhiễu. Vòng
  này **không giải quyết được**, và đó là câu hỏi mở rõ ràng nhất của mạch này.
  **Việc cần làm tiếp:** (1) **khử trùng lặp về các cơ chế phân biệt** (một đại
  diện mỗi họ biến thể) rồi chạy lại sign test ở **cả hai** interval — đó mới là
  bản trung thực của phép test tôi vừa chạy; (2) lặp trên **BTC 4h**. File:
  `round249-at-4h-momentum-improves-13-of-14-but-the-candidates-are-not-independent.md`.

- **Round 250 (2026-08-29) — BTC 4h KHÔNG tái lập được kết quả của Round 249:
  sign test sau khử trùng lặp p=0,23 và độ lớn hụt 4,4 lần.** Chạy cả hai việc
  r249 tự nêu — **khử trùng lặp về cơ chế phân biệt** và **lặp trên BTC 4h** —
  trên instrument độc lập. **Luật khử trùng lặp được cố định TRƯỚC khi nhìn kết
  quả:** gộp mọi candidate về gốc cơ chế rồi giữ biến thể **nhiều lệnh nhất**;
  luật này không thể chọn lọc thiên vị vì số lệnh độc lập với phép so hai dải.
  binance BTC 4h, zero cost, ≥30 lệnh mỗi dải: **36 candidate gộp còn 16 cơ chế
  phân biệt**. **Nhóm định hướng:** obv_trend −0,00556→+0,00730; candle_momentum
  −0,00348→+0,00517; macd_trend −0,00294→+0,00346; parabolic_sar
  −0,00462→+0,00268; heikin_ashi −0,00109→−0,00106; **sma_trend +0,00675→−0,00211**;
  **ema_crossover +0,02905→−0,00902**. ⇒ **5/7 cải thiện, p = 0,2266, trung vị
  150-300 = +0,00268 = 38,2% ma sát**. Trên **cả 16** cơ chế: **9/16** — đúng tung
  đồng xu. **DẠNG MẠNH CỦA r249 BỊ BÁC BỎ:** XAU 4h cho 13/14 (≈5-6 cơ chế) với
  trung vị **169,0%** ma sát; BTC 4h cho 5/7 với **p=0,23** và trung vị **38,2%**
  — **hụt 4,4 lần** và không có ý nghĩa thống kê. Một kết quả xuất hiện ở
  instrument này mà không ở instrument kia chính là thứ r205 và r224 đã dạy chương
  trình phải loại. **Dạng yếu thì sống nhưng không đáng kể:** số cơ chế định hướng
  cải thiện nhiều hơn không cải thiện (5/7) — đúng điều mô tả "regime định hướng"
  của r228/r247-248 vốn đã dự đoán. **HAI CHI TIẾT ĐÁNG GHI:** (1)
  `heikin_ashi_momentum_1` được tính là "cải thiện" với −0,00109 → −0,00106 —
  chênh ở chữ số thập phân thứ năm, **cả hai đều âm**: **sign test tính hoà gần
  như thắng**, làm phồng các con số kiểu 13/14 và 5/7, và 13/14 của r249 gần như
  chắc chắn có những ca như vậy; (2) hai cơ chế **đảo chiều** lại đúng là hai cơ
  chế có giá trị dải 0-150 **dương lớn nhất** — đó là hình dạng của **hồi quy về
  trung bình trong chính các ước lượng**, không phải một câu chuyện cơ chế.
  **VỊ TRÍ CỦA MẠCH NGHIÊN CỨU:** khung thuận lợi dùng chung (150-300 ngày) của
  r242-248 **vẫn đứng**, được hậu thuẫn từ nhiều hướng độc lập; nhưng việc r249
  nâng nó lên thành "ở 4h cơ chế định hướng vượt ma sát" **không sống sót qua
  instrument thứ hai**. Vị thế trung thực quay về đúng r242-246: **một hiệu ứng
  cửa sổ có thật nhưng nhỏ, dùng chung giữa các instrument, và không đủ lớn ở bất
  cứ đâu để trang trải ma sát.** File:
  `round250-btc-4h-fails-to-replicate-the-momentum-result-magnitude-off-by-4x.md`.

- **Round 251 (2026-08-29) — cuối cùng cũng so ĐÚNG CƠ SỞ: XAU 4h là 7/7 sau khử
  trùng lặp (p=0,0078), BTC 5/7 (p=0,23). Và bảy cơ chế trên một cửa sổ KHÔNG
  phải bảy phép thử độc lập.** Round 250 so **BTC đã khử trùng lặp (5/7)** với
  **XAU thô (13/14)** — không cùng cơ sở, đúng lỗi tổng-gộp đã gây ra sai lầm
  r241/r243, và chính nó đã tự gắn cờ. Vòng này chạy lại XAU 4h với **đúng luật
  khử trùng lặp không đổi**: 24 candidate ≥30 lệnh/dải gộp còn **13 cơ chế phân
  biệt**, 7 cái định hướng — `parabolic_sar` +0,00400→+0,03667; `ema_crossover`
  −0,00395→+0,02812; `macd_trend` +0,01056→+0,01646; `heikin_ashi`
  −0,00261→+0,00874; `obv_trend` +0,00099→+0,00848; `candle_momentum`
  +0,00170→+0,00669; `sma_trend` +0,00040→+0,00616. ⇒ **7/7 cải thiện, KHÔNG có
  ca hoà sát**, p=0,0078, trung vị **+0,00874 = 124,9% ma sát**, toàn bộ cơ chế
  10/13. **SỬA MỘT PHẦN r250:** vòng đó ngụ ý 13/14 của XAU bị phồng do đếm biến
  thể — nhưng sau khử trùng lặp nó là **7/7 không hoà sát**, tức **MẠNH HƠN** trên
  mỗi cơ chế chứ không yếu đi. Việc r250 bác **dạng mạnh** vẫn đứng nhờ con số
  38,2% của BTC; nhưng ngụ ý "XAU sẽ xẹp" thì sai. **KHỬ HAO SÂU HƠN, áp cho CẢ
  HAI:** vấn đề trùng lặp biến thể đã xử lý, **vấn đề ĐỘC LẬP thì chưa**. Bảy cơ
  chế phân biệt giao dịch **cùng một instrument trên cùng 150 ngày** không phải
  bảy phép thử độc lập — chúng là **bảy góc nhìn vào MỘT đường giá**. Một cửa sổ
  tưởng thưởng giao dịch định hướng sẽ đẩy cả bảy cùng chiều, nên 7/7 gần như là
  một quan sát lặp lại bảy lần, và **p=0,0078 vẫn bị thổi phồng nặng** — vì lý do
  khác r249 nhưng vẫn là thổi phồng. **Đó chính là lý do BTC mới là phép test có
  thông tin:** nó là một lượt rút **thật sự độc lập** của cùng kỳ lịch, và cho
  **5/7, p=0,23, 38,2% ma sát** — cùng chiều, bằng một phần ba, không có ý nghĩa
  thống kê. **Cấu trúc bằng chứng:** một instrument trông mạnh, một bản lặp độc
  lập yếu, và một thống kê nội-instrument không tin được ở cả hai. **Trạng thái
  từng dạng khẳng định:** "cơ chế định hướng phản ứng với khung 150-300" **được
  hậu thuẫn** (7/7 và 5/7, cộng r228/r247/r248); "phản ứng đó vượt ma sát" **chỉ
  ở XAU** (124,9% vs 38,2%), **không tái lập**; "p-value nội-instrument nói đúng
  điều nó nói" **không**. Không đổi so với r242-246: **một hiệu ứng cửa sổ có thật
  nhưng nhỏ, đủ để thấy ở một instrument và không thấy ở cái kia, chưa xác lập là
  giao dịch được.** File:
  `round251-like-for-like-xau-is-7-of-7-but-seven-mechanisms-on-one-window-are-not-seven-trials.md`.

- **Round 252 (2026-08-29) — vì sao XAU phản ứng mạnh gấp 3,3 lần BTC: lời giải
  thích hiển nhiên nhất BỊ BÁC BỎ, và bác theo chiều NGƯỢC LẠI.** Round 251 đo
  like-for-like rằng cơ chế định hướng đạt **124,9% ma sát ở XAU 4h** nhưng chỉ
  **38,2% ở BTC 4h** trong cùng khung 150-300, và đóng lại với *"chưa điều tra vì
  sao hai instrument khác nhau"*. Giả thuyết hiển nhiên theo r228/r247-248: **thị
  trường XAU trở nên định hướng hơn BTC** trong khung đó. Đo trực tiếp (4h, cùng
  các dải): exness XAU 0-150 eff 0,0242 drift −6,43% → 150-300 eff **0,0447**
  drift **+16,89%**; binance BTC 0-150 eff 0,0259 drift +12,21% → 150-300 eff
  **0,0805** drift **−48,18%**. **Tỉ lệ 150-300 / 0-150: efficiency XAU 1,85x vs
  BTC 3,11x; |drift| XAU 2,63x vs BTC 3,95x.** ⇒ **Thị trường BTC trở nên định
  hướng hơn XAU ĐÁNG KỂ, mà chiến thuật của nó lại phản ứng YẾU HƠN 3,3 lần.**
  Nếu tính định hướng chi phối phản ứng thì BTC phải phản ứng **mạnh hơn**. Lời
  giải thích không chỉ thiếu bằng chứng — **nó chỉ sai chiều**. **Thứ sống sót:**
  **mẫu hình theo thời gian trong từng instrument vẫn đứng** — cả hai thị trường
  đều định hướng hơn ở dải 150-300 (efficiency tăng ở cả hai), đúng như r228/
  r247/r248 mô tả và đúng chiều phản ứng của cả hai. **Thứ mất đi:** câu chuyện
  "regime định hướng" giải thích được **KHI NÀO** phản ứng xảy ra, nhưng **không**
  giải thích được **ĐỘ LỚN** trên từng instrument — và cơ chế hiển nhiên duy nhất
  cho việc đó vừa bị bác. **MỘT QUAN SÁT, GHI RÕ LÀ CHƯA KIỂM CHỨNG:** hai dải
  mạnh có hướng **ngược nhau** — drift XAU **+16,89%** (xu hướng tăng) còn BTC
  **−48,18%** (xu hướng giảm mạnh). Một quần thể chiến thuật xử lý xu hướng tăng
  tốt hơn xu hướng giảm sẽ tạo ra **đúng mẫu hình quan sát được**. **Đây là giả
  thuyết, không phải phát hiện** — chưa test, và sau r228, r230, r249 thì tôi
  không trình bày một câu chuyện khớp với hai điểm dữ liệu như bất cứ thứ gì
  khác. Phép test cụ thể: đo hiệu quả của quần thể candidate trong các đoạn xu
  hướng **tăng** so với **giảm**, xem bất đối xứng đó có tồn tại không. File:
  `round252-directionality-does-not-explain-the-instrument-gap-it-points-the-wrong-way.md`.

- **Round 253 (2026-08-29) — giả thuyết bất đối xứng long/short bị BÁC trên
  instrument độc lập; hướng xu hướng không giải thích thêm gì so với dải thời
  gian:** test đúng phép test r252 đặt ra, **không cần backtest mới** — r250/r251
  đã lưu edge từng cơ chế cho **cả hai dải trên cả hai instrument** dưới cùng một
  quy tắc dedup cam kết trước, r252 đã đo drift từng dải. Việc chưa từng làm là
  **nhóm lại cùng 14 số đó theo hướng xu hướng thay vì theo dải lịch**. Bốn ô:
  XAU 0-150 (giảm −6,43%) edge trung vị **+0,00099**, XAU 150-300 (tăng +16,89%)
  **+0,00874**, BTC 0-150 (**tăng** +12,21%) **−0,00294**, BTC 150-300 (giảm
  −48,18%) **+0,00268**. **Dải TĂNG của BTC là ô ÂM DUY NHẤT trong bốn ô và tệ
  hơn chính dải GIẢM của nó.** **Cùng 14 số, hai cách gán nhãn:** theo **dải
  lịch** → XAU 7/7, BTC 5/7, hai instrument **đồng thuận 2/2**, gộp 12/14
  p=0,0129; theo **hướng xu hướng** → XAU 7/7, BTC **2/7**, hai instrument
  **mâu thuẫn 1/2**, gộp 9/14 p=0,4240. Hướng xu hướng **không giải thích thêm
  gì** so với dải lịch và **phá vỡ** tính nhất quán cross-instrument mà dải lịch
  có. **Vì sao đây là bằng chứng duy nhất có được, và nó yếu tới đâu:** trong
  cùng một instrument, dải lịch và hướng xu hướng **đồng biến hoàn toàn** (mỗi
  instrument có đúng hai dải, một tăng một giảm), nên **không** so sánh
  within-instrument nào phân biệt được — XAU 7/7 ủng hộ **cả hai** câu chuyện như
  nhau. Bằng chứng phân biệt duy nhất là tính nhất quán cross-instrument, và đó
  là **n = 2**: một draw đồng thuận, một draw mâu thuẫn. Không phải "bác bỏ bất
  đối xứng long/short ở mọi nơi". Cả hai p-value vẫn mang nguyên deflation r251
  (7 cơ chế trên một đường giá không phải 7 phép thử độc lập) nên **đều bị thổi
  phồng**; chỉ **phép so sánh giữa hai dòng** được dùng. **MẠCH:** r252 bác
  *độ lớn tính định hướng*, r253 bác *bất đối xứng long/short* — cửa sổ lịch
  chung r242-248 đứng vững hơn, nhưng **chênh lệch ĐỘ LỚN cross-instrument vẫn
  chưa có lời giải**. **NGÂN SÁCH — 2 container, 0 kết quả:** hai sweep định thêm
  dải thứ ba **300-450 ngày** (`--days 450`, chia ba, 4h, zero cost) — thứ sẽ phá
  được đồng biến dải/hướng một cách đúng đắn — cùng chạy `docker run -d --rm`,
  **thoát sau ~24s trước khi stdout được ghi lại** và bị `--rm` xoá. Lỗi gọi lệnh
  của tôi, không phải lỗi tool; ngân sách 2 container tiêu hết không thu được gì
  nên **không chạy thêm container nào**. Không rò rỉ, tunnel đã đóng và verify
  bằng `ss`. Lần sau: bỏ `--rm` rồi đọc `docker logs` sau khi thoát, hoặc chạy
  attached và pipe stdout ra file. File:
  `round253-trend-direction-does-not-explain-what-calendar-band-already-explains.md`.

- **Round 254 (2026-08-29) — DẢI THỨ BA 300-450 NGÀY: một PHÉP ĐỐI CHỨNG TỰ
  NHIÊN — drift giữ nguyên mà edge vẫn chênh 3,25 lần:** chạy đúng thí nghiệm
  r253 đặt ra (`--days 450`, chia ba theo index, 4h, zero cost); cách gọi lệnh đã
  sửa và hoạt động. Lần đầu tiên **cả hai instrument phủ CÙNG một cửa sổ lịch với
  ranh giới khớp nhau** (2025-06-05 / 2025-10-31 / 2026-04-01 / 2026-08-28) —
  điều r249-253 chưa từng có. Dải: XAU train(450-300n) drift **+19,62%** eff
  0,1005; validation(300-150n) drift **+19,63%** eff 0,0560; holdout(150-0n)
  drift −6,90% eff 0,0248. BTC: train +6,37% eff 0,0143; validation −38,22% eff
  0,0589; holdout +12,99% eff 0,0261. **PHÉP ĐỐI CHỨNG TỰ NHIÊN:** drift của
  train và validation XAU **cách nhau 0,01 điểm phần trăm** (+19,62% vs +19,63%)
  — hai xu hướng tăng cùng cỡ, mỗi dải năm tháng, cùng instrument — và dải **cũ
  hơn** còn **hiệu quả hơn 1,79 lần**. Edge trung vị của cơ chế định hướng vẫn
  là **+0,00304 so với +0,00987 = validation cao gấp 3,25 lần**. **Drift giữ
  nguyên, efficiency chỉ ngược chiều, mà dải lịch vẫn dịch edge 3,25 lần** — đây
  là **so sánh có đối chứng thật**, không phải lập luận gán nhãn lại như r253, và
  là bằng chứng đơn lẻ mạnh nhất của cả mạch này. **MẪU HÌNH DẢI TÁI LẬP TRÊN
  CÁCH CHIA MỚI:** validation>train 6/6 (XAU) và 6/7 (BTC), hai instrument
  **đồng thuận 2/2**, gộp 12/13 p=0,0034; validation>holdout 6/6 và 5/7, **2/2**,
  11/13 p=0,0225; holdout>train 3/6 và 2/7 — **dải giữa là đỉnh trên cả hai
  instrument, hai dải ngoài không phân biệt được với nhau**. Trung vị so với hằng
  số ma sát 0,0070: XAU 43,4% / **141,0%** / −2,5% (n=6); BTC −0,0% / **80,6%** /
  −29,3% (n=7) — **zero cost, gộp trước phí, KHÔNG phải claim giao dịch được**.
  **CẢ HAI LỜI GIẢI THÍCH ĐỐI THỦ LẠI THẤT BẠI TRÊN DỮ LIỆU MỚI:** *hướng xu
  hướng* — dải TĂNG của XAU thắng dải GIẢM nhưng dải TĂNG của BTC **thua** dải
  GIẢM, **1/2**, đúng mâu thuẫn r253 tìm ra, nay trên một dải độc lập bổ sung;
  *efficiency/độ lớn định hướng* — dải **hiệu quả nhất** của XAU lại là dải
  edge **tệ nhất** trong hai dải tăng, còn BTC thì efficiency có bám theo,
  **1/2** lần nữa, đúng như r252. **Dải lịch 2/2 ở cả hai phép so sánh.**
  **TÁI LẬP ĐỘC LẬP r250/r251** (cách chia khác): dấu được giữ ở **11/13** cơ chế
  ở dải holdout và **11/13** ở validation, độ lớn sát nhau ở các giá trị lớn;
  **cả bốn lần đổi dấu đều rơi vào ước lượng gần 0** — edge lớn theo dải tái lập
  tốt, **edge gần 0 KHÔNG ổn định trước một dịch chuyển ranh giới vài ngày** và
  không được tính là "win" trong sign test. **CẶP GƯƠNG:** `candle_reversion` là
  phủ định chính xác của `candle_momentum`, `taker_imbalance_fade` của
  `taker_imbalance`; mỗi cặp góp đúng một win và một loss theo cấu tạo. Tôi **đã
  kỳ vọng** điều này giải thích được "9/16 coin flip" của r250 và **NÓ KHÔNG** —
  loại cặp gương chỉ đổi 9/13 thành 8/11 và 11/21 thành 9/17, có thật nhưng quá
  nhỏ để đổi cách đọc; ghi lại như **caveat đếm, KHÔNG phải correction cho r250**.
  **GIỚI HẠN:** p-value gộp vẫn mang nguyên deflation r251 (6-7 cơ chế trên một
  đường giá là các góc nhìn của một đường giá), **n độc lập trung thực là 2
  INSTRUMENT** chứ không phải 13 cơ chế; mọi con số đều trước phí. **CÂU HỎI MỞ
  đã sắc hơn:** nếu hiệu ứng khoá theo lịch và không do drift hay efficiency, thì
  **tính chất nào của đúng cửa sổ đó đang làm việc** — và nó có **nhận biết được
  TRƯỚC** hay chỉ thấy được khi nhìn lại? Một cửa sổ chỉ nhận ra sau khi đã qua
  thì **vô giá trị về vận hành**, và đó vẫn là lý do mạch này chưa từng promote.
  File: `round254-a-natural-control-the-band-moves-the-edge-with-drift-held-constant.md`.

- **Round 255 (2026-08-29) — CORRECTION + ĐÓNG HƯỚNG r242-254: cửa sổ KHÔNG duy
  nhất, KHÔNG dự đoán được, và drift THỰC SỰ giải thích được thứ tự:** CLI
  **không có** cờ as-of/end-date — mọi cửa sổ đều kết thúc ở "bây giờ" — nhưng
  train/validation có thể **đặt ở bất kỳ đâu** qua `--days` cộng ratio, nên hai
  run (`--days 1050` tại 1/7, `--days 750` tại 0,2) cho thêm bốn dải 150 ngày lùi
  về quá khứ. Cộng ba dải của r254 thành **BẢY DẢI 150 NGÀY LIÊN TIẾP phủ
  2023-10-15 → 2026-08-28**, ranh giới khớp trong vòng một ngày. XAU 4h zero
  cost, edge trung vị định hướng: B1 (1050-900n) drift +12,81% edge +0,00032; B2
  +11,92% / +0,00148; B3 +9,03% / +0,00177; **B4 (600-450n) +26,72% / +0,01134**;
  B5 +19,62% / +0,00304; **B6 (300-150n) +19,63% / +0,00987**; B7 −6,90% /
  −0,00018.
  **PHÁT HIỆN 1 — "CỬA SỔ THUẬN LỢI" KHÔNG DUY NHẤT:** **B4 (+0,01134) CAO HƠN
  B6 (+0,00987)**; B6 chỉ **hạng #2 trên 7**. Mười ba vòng (r242-254) đã mô tả
  dải tốt **thứ nhì** trong mẫu vì phân tích chưa bao giờ nhìn lùi quá 450 ngày.
  **PHÁT HIỆN 2 — SỬA LẠI CHÍNH KẾT LUẬN CỦA TÔI Ở r252/r253/r254:** tôi đã bác
  drift **ba lần** trên 2-3 dải. Với **bảy** dải, quan hệ **gần như đơn điệu**:
  hạng \|drift\| 4,3,2,7,5,6,1 so với hạng edge 2,3,4,7,5,6,1 — chỉ B1/B3 hoán
  vị — **Spearman +0,857, permutation chính xác p=0,0238** (đủ 5040 hoán vị);
  efficiency yếu hơn nhiều (+0,500, p=0,267). **"Phép đối chứng tự nhiên" của
  r254 đã bị tôi đọc quá tay** và tôi còn gọi nó là "bằng chứng đơn lẻ mạnh nhất
  của cả mạch": theo quan hệ hạng thì cặp B5/B6 được sắp **đúng** (19,62 < 19,63
  và +0,00304 < +0,00987); cái bất thường là **độ lớn**, không phải chiều. Phát
  biểu trung thực và hẹp hơn: **độ lớn drift sắp hạng các dải rất tốt và KHÔNG
  xác định được mức edge**. Đây là **đúng failure mode r230 nâng lên một cấp** —
  tôi tuân thủ "báo cáo cả ba split và biên độ" cho *split* nhưng lại vi phạm nó
  cho *dải*. **MỞ RỘNG QUY TẮC: trước khi tuyên bố một biến là không liên quan,
  hãy đo nó trên MỌI dải mà tooling với tới được, không phải trên các dải mà lần
  gọi lệnh hiện tại tình cờ sinh ra.**
  **PHÁT HIỆN 3 — QUYẾT ĐỊNH: tất cả đều là ĐỒNG THỜI, không có gì biết trước.**
  Dự báo edge của dải **kế tiếp**: edge(t) Spearman +0,086 p=0,919; \|drift\|(t)
  −0,371 p=0,497; drift(t) −0,371 p=0,497; efficiency(t) +0,314 p=0,564 —
  **không gì dự đoán được dải kế tiếp** (đối chiếu đồng thời +0,857). Hai dải tốt
  nhất đều bị sụp ngay sau đó (B4 +0,01134 → B5 +0,00304; B6 +0,00987 → B7
  −0,00018). Luật walk-forward thô: chỉ trade dải sau một dải \|drift\| cao →
  mean **+0,00424**; ngược lại → mean **+0,00486** — **luật còn TỆ HƠN không dùng
  luật** (3 quan sát mỗi nhánh, không đủ power cho lợi ích nhỏ). r254 đã nêu đúng
  câu hỏi quyết định mạch này có đáng đi tiếp không; **câu trả lời là CHỈ NHẬN RA
  ĐƯỢC KHI NHÌN LẠI**, nên **hướng r242-254 ĐÓNG về mặt vận hành**.
  **GIỚI HẠN:** **một instrument** — BTC không chạy lại, ngân sách dồn cho việc
  kéo dài lịch sử XAU theo thứ tự ưu tiên XAU-trước; **sáu trên bảy dải có drift
  dương** nên drift và \|drift\| gần như cùng một biến ở đây và **không tách
  được**; theo cách đọc \|drift\|, ba dải BTC của r254 cho Spearman +0,5 — cùng
  chiều, trên 3 điểm, **không có power** — ghi lại như **quan sát, không phải
  claim**, và đó là phép test hiển nhiên kế tiếp; mọi con số **zero cost, trước
  phí**; bốn predictor trên sáu chuyển tiếp là phép tìm yếu, loại được hiệu ứng
  **mạnh** chứ không loại được hiệu ứng tinh vi. File:
  `round255-CORRECTION-the-window-is-neither-unique-nor-predictable-and-drift-does-explain-it.md`.

- **Round 256 (2026-08-29) — BTC TÁI LẬP ĐÚNG ρ=+0,857: là ĐỘ LỚN xu hướng, KHÔNG
  phải HƯỚNG; và vẫn chỉ nhận ra được khi nhìn lại. Hướng r242-255 nay ĐÓNG trên
  CẢ HAI instrument:** chạy đúng phép test r255 nêu. r255 tìm ra `|drift|→edge`
  Spearman +0,857 trên XAU nhưng **không tách được** signed drift khỏi độ lớn xu
  hướng (sáu trên bảy dải XAU có drift dương). BTC tile y hệt cho **bảy dải 150
  ngày liên tiếp trên CÙNG ranh giới lịch với XAU** và — quyết định — **hai dải
  giảm thật**: B1 (1050-900n) drift **+167,75%** edge +0,00493; B2 **−15,90%** /
  +0,00407; B3 +65,96% / +0,00630; B4 +5,60% / **−0,00969**; B5 +6,37% /
  −0,00000; B6 **−38,22%** / +0,00564; B7 +12,99% / −0,00205.
  **PHÁT HIỆN 1 — TÁI LẬP CHÍNH XÁC:** `|drift|→edge` Spearman **+0,857**, perm
  chính xác **p=0,0238** trên BTC — **trùng XAU tới ba chữ số thập phân**; Fisher
  trên hai phép test instrument độc lập cho χ²=14,95, df=4, **p gộp = 0,0048**.
  **PHÁT HIỆN 2 — ĐỘ LỚN, KHÔNG PHẢI HƯỚNG:** trên BTC — instrument **tách được**
  hai biến — `|drift|→edge` **+0,857** (p=0,024) so với **signed drift→edge
  +0,143** (p=0,78, **không gì cả**). Trên XAU cả hai đều đọc +0,857 **chỉ vì**
  XAU có đúng một dải drift âm khiến hai biến gần như trùng nhau ở đó. **Trên
  instrument duy nhất trả lời được câu hỏi, HƯỚNG không mang thông tin nào và ĐỘ
  LỚN mang toàn bộ** — đóng câu hỏi long/short r252/r253 từ góc thứ ba, và giải
  thích vì sao các vòng đó cứ thấy hai instrument mâu thuẫn về hướng: **họ đang
  test SAI BIẾN**. **CẢNH GIÁC MỘT CÁCH ĐỌC SAI TÔI SUÝT GHI:** phép đếm ngây thơ
  "cả hai instrument cùng dấu" cũng cho 2/2 cho signed drift vì +0,143 là dương —
  **phép đếm đó vô nghĩa ở mức đó** và **không** phải bằng chứng cho hướng.
  **PHÁT HIỆN 3 — QUAN HỆ THỨ BẬC TRONG một instrument, KHÔNG phải thang đo CHUNG
  giữa hai instrument:** cùng dải lịch B6 — XAU \|drift\| 19,63% edge +0,00987 so
  với BTC \|drift\| 38,22% edge +0,00564: **BTC trend mạnh hơn 1,95 lần mà chỉ
  kiếm được 57% edge mỗi trade của XAU**. Điều này **giải quyết câu hỏi mở r252**
  ("vì sao XAU phản ứng mạnh gấp 3,3 lần BTC") bằng cách chỉ ra **đó là CÂU HỎI
  SAI** — không có thang đo chung, nên "khoảng cách" đó là **artifact** của việc
  đối xử một quan hệ thứ bậc nội-instrument như một quan hệ định lượng
  liên-instrument.
  **PHÁT HIỆN 4 — NULL EX-ANTE TÁI LẬP:** predictor cho edge dải kế tiếp trên BTC
  — edge(t) Spearman **−0,600** p=0,242; \|drift\|(t) −0,314; drift(t) −0,086;
  efficiency(t) −0,314. **Cả bốn không có ý nghĩa và cả bốn đều ÂM**, như trên
  XAU. Đồng thời +0,857 trên cả hai; **dự báo thì không gì cả trên cả hai**; BTC
  còn gợi ý **phản-persistence**.
  **CÁCH ĐỌC TRUNG THỰC — GẦN NHƯ MỘT TAUTOLOGY:** "cơ chế theo xu hướng kiếm
  được nhiều hơn trong giai đoạn thị trường xu hướng nhiều hơn" gần như là một
  **định nghĩa** — và đó chính là điểm mấu chốt: mẫu hình dải mà r242-255 dành
  **mười bốn vòng** để mô tả **phần lớn chỉ là phát biểu lại thị trường đã đi một
  chiều bao nhiêu trong dải đó**. Nó giải thích mẫu hình **và** giải thích vì sao
  mẫu hình **vô giá trị**: độ lớn xu hướng của dải chỉ biết được **sau khi dải đã
  kết thúc**. r255 đóng hướng này trên một instrument; **nay đóng trên hai**, có
  cơ chế, có null ex-ante tái lập.
  **GIỚI HẠN:** `|drift|` và efficiency **KHÔNG phải hai bằng chứng riêng** —
  efficiency = \|drift\| chia tổng độ dài đường đi, **chung tử số theo cấu tạo**,
  nên **không được cộng dồn** hai hệ số tương quan; bảy dải từ một đường giá
  không phải bảy phép thử độc lập (không chồng lấn thì tốt hơn tình huống r251,
  nhưng dải kề nhau vẫn có thể chung regime) — **đơn vị độc lập trung thực là 2
  INSTRUMENT**; mọi con số **zero cost, trước phí**; bốn predictor trên sáu
  chuyển tiếp mỗi instrument loại được hiệu ứng **mạnh**, không loại được hiệu
  ứng tinh vi; cách đọc tautology **khớp và đơn giản nhất nhưng CHƯA** được test
  độc lập với một quần thể đối chứng không-theo-xu-hướng. File:
  `round256-btc-replicates-it-is-trend-magnitude-not-direction-and-still-hindsight-only.md`.

- **Round 257 (2026-08-29) — QUẦN THỂ ĐỐI CHỨNG XÁC NHẬN TAUTOLOGY (+1,000 so với
  −0,900), và REGIME SWITCHING KHÔNG CÓ GÌ ĐỂ CHUYỂN:** đóng nốt khoảng trống r256
  nêu ("cách đọc tautology **chưa** được test độc lập với quần thể đối chứng
  không-theo-xu-hướng"). Dự đoán **sắc và bác bỏ được**: nhóm trend có
  `|drift|→edge` dương (đã xác lập +0,857 trên cả hai instrument) thì nhóm
  **counter-trend BẮT BUỘC phải ÂM**; nếu nhóm counter-trend cũng dương thì phát
  hiện là **về các dải**, không phải về trend-following, và cách đọc đó **sai**.
  **PHÂN NHÓM VÀ DỰ ĐOÁN ĐÃ GHI RA ĐĨA TRƯỚC KHI CHẠY BẤT KỲ SWEEP NÀO của vòng
  này** (`precommit_groups.json`, iteration 52) để việc gán nhóm **không thể** được
  chỉnh theo kết quả. Hai cơ chế bị loại ngay tại đó vì là **gương số học** —
  `candle_reversion` là phủ định chính xác của `candle_momentum`,
  `taker_imbalance_fade` của `taker_imbalance` — tương quan của chúng **bị ép theo
  cấu tạo** và **không phải bằng chứng**. XAU 4h, **năm dải 150 ngày liên tiếp
  B3-B7**, zero cost, ≥30 trade ở **cả năm** dải; \|drift\| theo dải:
  9,03/26,72/19,62/19,63/6,90%.
  **KẾT QUẢ — HAI QUẦN THỂ ĐI NGƯỢC CHIỀU NHAU:** trend-following (n=6) edge
  +0,00115/+0,01134/+0,00304/+0,00987/−0,00017 → **ρ=+1,000** (**đơn điệu hoàn
  hảo**, mức tối đa đạt được trên năm điểm) perm **p=0,0167**; counter-trend thật
  (n=3: `rsi`, `stochastic`, `engulfing_pattern`) edge
  −0,00014/−0,01246/−0,01124/−0,00394/+0,00419 → **ρ=−0,900** perm p=0,0833; nhóm
  "khác" (không đặt dự đoán) +0,700 p=0,2333. Edge counter-trend **âm ở BỐN trên
  NĂM dải**, và dải dương duy nhất là **B7 — dải \|drift\| THẤP NHẤT**: cơ chế
  đảo chiều **lỗ trong dải xu hướng và chỉ kiếm được trong dải yên tĩnh**, đúng
  ảnh gương của câu chuyện trend, từ một quần thể **không phải** phủ định số học
  của nó. Drift các dải **tái lập chính xác** giá trị r255 từ hai run độc lập.
  **Dự đoán cam kết trước đã được xác nhận** — mẫu hình dải **là** phát biểu lại
  độ lớn xu hướng, và cuộc săn "cửa sổ thuận lợi" suốt mười bốn vòng r242-255 chỉ
  đang bám theo đúng thứ đó.
  **HỆ QUẢ HIỂN NHIÊN, VÀ VÌ SAO NÓ CHẾT NGAY:** hai quần thể bổ sung nhau — một
  kiếm trong dải xu hướng, một trong dải yên tĩnh — gợi ra Portfolio
  **chuyển regime** (chạy trend khi thị trường xu hướng, chạy reversion khi
  không). Điều đó đòi hỏi biết **độ lớn xu hướng của dải KẾ TIẾP**. **Nó không
  bền:** `|drift|(t)→|drift|(t+1)` XAU Spearman **−0,314** (p=0,564), BTC
  **−0,143** (p=0,803) — **không có ý nghĩa và đều ÂM trên cả hai instrument**.
  Một bộ chuyển regime ở horizon này **không có gì để chuyển**: nó sẽ chọn quần
  thể dựa trên một biến **không mang thông tin nào** về giai đoạn nó sắp giao
  dịch. Đúng bức tường r255/r256 đã đụng từ phía bên kia — quan hệ **mạnh, tái
  lập, có cơ chế, và HOÀN TOÀN ĐỒNG THỜI**.
  **GIỚI HẠN:** counter-trend **p=0,0833 KHÔNG có ý nghĩa**, và với năm dải thì
  sàn là 0,0167 — kết quả nằm ở **dấu và độ lớn của ρ**, không phải ở p-value;
  hai nhóm **KHÔNG phải hai phép test độc lập** (cùng năm dải, một đường giá, và
  quần thể counter-trend đại khái là phần bù của quần thể trend ngay cả khi không
  phải phủ định số học) nên đây là **phép kiểm tra nhất quán với một dự đoán cam
  kết trước**, không phải xác nhận độc lập thứ hai; chỉ **ba** cơ chế counter-trend
  qua được bộ lọc ≥30 trade (`rsi_mean_reversion` không qua) nên đây **không phải**
  đối chứng đại diện; regime switching mới test ở **horizon dải 150 ngày**, horizon
  regime ngắn hơn **chưa bị loại trừ** dù không có gì trong r249-257 gợi ý nó khác;
  **một instrument** — BTC không chạy lại cho phép test đối chứng, ngân sách dồn
  cho năm dải XAU liên tiếp thay vì ba dải mỗi bên; mọi con số zero-cost, trước
  phí. File:
  `round257-the-control-population-confirms-the-tautology-and-regime-switching-has-nothing-to-switch-on.md`.

- **Round 258 (2026-08-29) — PHẦN DỰ ĐOÁN ĐƯỢC CỦA THỊ TRƯỜNG LÀ PHẦN SAI: `|drift|`
  KHÔNG bền ở BẤT KỲ horizon nào (5-150 ngày), volatility LUÔN bền, và chỉ
  `|drift|` mới dẫn dắt edge. ĐÓNG HOÀN TOÀN mạch r242-258. KHÔNG DÙNG CONTAINER
  NÀO.** Đóng nốt điều duy nhất r257 để mở ("regime switching mới test ở horizon
  dải 150 ngày; horizon ngắn hơn **chưa** bị loại trừ"). Một bộ chuyển regime cần
  đúng một thứ: **độ lớn xu hướng của giai đoạn KẾ TIẾP** — đây là câu hỏi thuần
  dữ liệu giá, quét được qua nhiều horizon **không cần backtest**, và ở horizon
  ngắn thì có power thật (**364 cửa sổ ở 5 ngày** so với **7** mà r255-257 có).
  **KHÔNG GIẢ ĐỊNH PHƯƠNG PHÁP ĐÚNG:** volatility được đưa vào làm **ĐỐI CHỨNG
  DƯƠNG** vì volatility clustering là stylized fact sách giáo khoa — nếu phương
  pháp không tìm lại được nó trên **cùng các cửa sổ đó** thì phương pháp hỏng và
  mọi kết quả null đều vô nghĩa. Toàn bộ lịch sử 4h hai instrument (XAU 8011 bar,
  BTC 10977 bar, 2021-08-26 → 2026-08-28/29); Spearman lag-1 trên cửa sổ **không
  chồng lấn** lát từ hiện tại lùi về, permutation 20 000 lần, seed cố định.
  **KẾT QUẢ — ĐỐI CHỨNG NỔ, BIẾN QUAN TÂM THÌ KHÔNG:** `|drift|` **không có ý
  nghĩa ở 0 trên 16 ô** instrument×horizon (XAU +0,044/−0,020/+0,031/+0,081/
  +0,135/−0,216/−0,392/+0,045; BTC +0,027/+0,062/−0,099/−0,213/−0,106/−0,145/
  −0,154/−0,564), trong khi **đối chứng volatility có ý nghĩa ở 12 trên 16 ô**,
  phần lớn **p<0,0001** (XAU +0,506/+0,606/+0,518/+0,539/+0,403…; BTC +0,532/
  +0,504/+0,570/+0,535/+0,500/+0,598…). **Phương pháp rõ ràng phát hiện được
  persistence khi persistence tồn tại.** Efficiency đạt p<0,05 danh nghĩa ở **2
  trên 16** ô (XAU 100d −0,498; BTC 150d −0,609) — với 16 test thì kỳ vọng ngẫu
  nhiên ~0,8 ô, và **cả hai đều ÂM**, tức **sai dấu** cho một bộ chuyển regime
  ngay cả khi có thật; **không** được coi là phát hiện.
  **LẬP LUẬN KẾT THÚC — BIẾN DỰ ĐOÁN ĐƯỢC LÀ BIẾN SAI:** volatility bền rất mạnh
  — vậy nó có dẫn dắt edge không? Tính lại trên **đúng bảy dải 150 ngày** của
  r255/r256, từ một lần pull dữ liệu **độc lập**: **edge vs `|drift|` (KHÔNG dự
  đoán được) Spearman +0,857 p=0,0238 trên CẢ HAI instrument**; **edge vs
  volatility (dự đoán được) +0,357 p=0,444 (XAU) và +0,107 p=0,840 (BTC)**.
  **BIẾN DẪN DẮT EDGE THÌ KHÔNG BỀN; BIẾN BỀN THÌ KHÔNG DẪN DẮT EDGE.** Regime
  switching vì thế thất bại **về mặt CẤU TRÚC**, không phải vì thiếu horizon tốt
  hơn hay tín hiệu khéo hơn: thị trường cho ta dự báo **giá sẽ DAO ĐỘNG bao
  nhiêu** và **không** cho dự báo **giá sẽ ĐI ĐƯỢC BAO XA**, còn edge chỉ phụ
  thuộc vào vế thứ hai. **ROBUSTNESS:** các giá trị `|drift|` ở đây lát từ chuỗi
  5 năm đầy đủ chứ không từ lần pull 1050 ngày của r255/r256 nên số theo dải lệch
  chút (XAU B1 15,8% ở đây so với 12,81% ở đó) — mà **Spearman vẫn là +0,857 trên
  cả hai instrument theo cả hai cách**, không đổi tới ba chữ số.
  **GIỚI HẠN:** tự tương quan lag-1 trên **một** biến là **phép tìm hẹp** — chưa
  test predictor đa biến hay ngoại sinh, nên điều này loại trừ **persistence đơn
  giản**, không phải mọi khả năng dự đoán; hai ô efficiency có ý nghĩa danh nghĩa
  **nhất quán với nhiễu** khi có 16 test và sai dấu, nhưng **không** chứng minh
  được chúng là giả; **không** kết luận volatility vô dụng với Portfolio nói
  chung — position sizing và risk control là câu hỏi riêng **chưa** xem xét;
  không claim gì **dưới 5 ngày hoặc trên 150 ngày**; mọi edge vẫn là số zero-cost
  trước phí của r254-257. File:
  `round258-the-forecastable-regime-variable-is-the-wrong-one-across-every-horizon.md`.

- **Round 259 (2026-08-29) — ĐO TARGET 3 LẦN HAI TRÊN PRODUCTION: point estimate
  tách BTC khỏi XAU nhưng MỌI route vẫn CHƯA KẾT LUẬN ĐƯỢC; và durable log nay đã
  verify ĐẦY ĐỦ chứ không chỉ nguyên tử. Vòng đầu tiên rời mạch r242-258 (đã đóng).
  Chỉ evidence production read-only, KHÔNG CONTAINER.** Đây đúng là việc r207 yêu
  cầu ("đọc lại các key đó sau khoảng bảy ngày"). Cửa sổ nay là **46,1 giờ** (cả
  sáu worker `Up 46 hours`) = **gấp đôi** 25,2h của r207, dù chưa phải bảy ngày.
  Closes = entries/3 (ba capital rule mỗi close), cấu trúc r207 lập đã xác nhận
  lại: mỗi route có **đúng ba** entry cho mỗi `exit_at` phân biệt; cardinality
  12/3/9/3/9/3, index = payload trên mọi route.
  **TARGET 3 (ngưỡng 7/tuần), closes và KTC Poisson 95% (/tuần):** binance BTC 4 →
  **14,6** [3,97; 37,32]; exness BTC 3 → 10,9 [2,25; 31,95]; bybit BTC 3 → 10,9
  [2,25; 31,95]; binance XAU 1 → **3,6** [0,09; 20,30]; exness XAU 1 → 3,6; bybit
  XAUT 1 → 3,6. **GỘP:** BTC 10 closes → **12,1/tuần [5,83; 22,34]**; XAU 3 →
  **3,6/tuần [0,75; 10,65]**. **KHÔNG route nào và KHÔNG pool nào đạt hay trượt
  Target 3 ở mức 95%** — cận dưới của BTC gộp là **5,83 < 7**, cận trên của XAU gộp
  là **10,65 > 7**. Gợi ý định hướng của r207 (BTC trên vạch, XAU quanh/dưới) sống
  sót qua cửa sổ gấp đôi với 10 closes thay vì 5 — **nhưng vẫn chỉ là gợi ý**: gấp
  đôi cửa sổ thì gấp đôi số đếm mà cận tin cậy gần như không nhúc nhích, đúng bản
  chất đếm Poisson và đúng lý do r207 từ chối kết luận. So với backtest r92
  (~7,2-7,3/tuần 18 tháng, ~9,3/tuần 5 năm): BTC 12,1 nằm trên cả hai, XAU 3,6 nằm
  dưới cả hai, **không cái nào có ý nghĩa**. **THỨ SẼ GIẢI QUYẾT** (nếu point
  estimate hiện tại là rate thật): BTC gộp đạt ở **17 closes ≈ 3,3 ngày nữa**; XAU
  gộp trượt ở **9 closes ≈ 5,8 ngày nữa** — ngày đọc lại **suy ra từ rate quan
  sát**, thay cho "khoảng bảy ngày" của r207.
  **DURABLE LOG ĐÃ VERIFY ĐẦY ĐỦ — r207 CHƯA làm điều này.** Hai bộ đếm độc lập
  thoạt nhìn mâu thuẫn: ledger `trade_count` trừ seed `paper-backtest-*` cho
  6/1/5/2/4/3 = **21** closes, durable log cho 4/1/3/1/3/1 = **13**. r207 verify
  **tính nguyên tử** (index cardinality = payload cardinality, vẫn khớp chính xác
  trên cả sáu route) nhưng **chưa bao giờ** verify **tính đầy đủ** với một bộ đếm
  độc lập. Ledger `paper-*` **giữ lại các bản ghi trade gần nhất KÈM timestamp**,
  nên kiểm được: binance BTC giữ exit 08-25 18:59 và 08-27 08:14 — **vắng trong
  log và ĐỀU TRƯỚC deployment**; còn 08-27 19:59 / 08-27 22:59 / 08-28 03:59 /
  08-28 16:04 — **CÓ ĐỦ CẢ BỐN**; exness XAU giữ 08-25 02:09 và 08-25 23:59 (vắng,
  trước deployment) và 08-28 14:09 (**có**). **MỌI close sau khi log deploy
  (worker start 2026-08-27T14:35Z) đều có mặt, exit timestamp khớp chính xác; mọi
  trade ledger vắng trong log đều xảy ra TRƯỚC đó.** Chênh lệch hoàn toàn do khác
  điểm bắt đầu cửa sổ — nghi từ đầu, nay **đã verify** chứ không phải giả định.
  **BINANCE XAU/USDT ĐÃ "TAN BĂNG":** r207 ghi key **vắng mặt** và r206 xác nhận
  ledger route đó đứng ở 7 trade từ 2025-12-26; nay có 3 entry (một close
  2026-08-28T16:19Z) và ledger đọc 8 trade.
  **ĐÒN BẨY r80/r83 ĐƯỢC XÁC NHẬN LIVE TỪ TRADE ĐÓNG THẬT**, không phải từ config:
  `take_profit` quan sát **+0,09407** so với `5,0×TAKE(0,02)−0,007 = +0,093`;
  `stop_loss` **−0,05596** so với `−5,0×STOP(0,01)−0,007 = −0,057`, notional 5,0
  trừ ~14bps khứ hồi.
  **MỘT CHECKPOINT CŨ NHƯNG KHÔNG PHẢI LỖI:** `exness.cfd.xau.usd.5m` cập nhật lần
  cuối 2026-08-29T00:00:04Z, **12,7 giờ trước**, trong khi năm route kia cập nhật
  trong vòng 10 phút và container báo `Up 46 hours (healthy)` — **đúng hình dạng**
  lỗi "container healthy mà không tiến triển" mà rule cảnh báo. **Nó không phải
  lỗi đó:** hôm nay là **THỨ BẢY** và route đó là **CFD vàng**, không giao dịch
  cuối tuần. Hai bằng chứng thay cho giả định: `exness.cfd.btc.usd` **cũng** là
  CFD Exness và **có** cập nhật lúc 12:30Z vì CFD crypto chạy liên tục; và trên
  cùng khoảng 5 năm, XAU có **8011** bar 4h so với BTC **10977** — tỉ lệ 0,73 ≈
  5/7, đúng phần đóng cửa cuối tuần, **nhìn thấy trong chính dữ liệu**. Ghi lại để
  vòng sau **không** dựng lại thành incident.
  **GIỚI HẠN:** **KHÔNG có verdict Target 3** — tất cả chưa kết luận được ở 95%,
  tách BTC/XAU chỉ là mẫu hình point-estimate qua hai lần đọc, không phải kết quả;
  completeness mới kiểm **hai trên sáu** route (hai route mà bản ghi ledger giữ lại
  cho phép kiểm mà không cần đào sâu); một close **không** có nghĩa binance XAU đã
  trở lại bình thường; ledger `fixed-pct` triển khai vẫn **âm ròng** trên mọi route
  trừ binance XAU (+0,047 trên 8 trade) và **không** mẫu nào ở đây đủ để phát biểu
  về lợi nhuận; cửa sổ 46,1h **chứa một ranh giới cuối tuần**, thứ **triệt tiêu
  riêng** các route CFD XAU — một thiên lệch **chống lại XAU** mà lần đọc bảy ngày
  cũng sẽ mang theo và các point estimate trên **KHÔNG** hiệu chỉnh. File:
  `round259-target3-second-live-reading-undetermined-and-durable-log-completeness-verified.md`.

- **Round 260 (2026-08-29) — DURABLE LOG VERIFY ĐẦY ĐỦ TRÊN CẢ 6/6 ROUTE, và thiên
  lệch cuối tuần r259 tự nêu chỉ giải thích 5,9% khoảng cách XAU/BTC. KHÔNG
  CONTAINER.** r259 đã chỉ ra Target 3 cần khoảng **3,3 ngày nữa** mới kết luận
  được; mới trôi qua hai mươi phút nên **đọc lại số đếm sẽ không thêm gì** và
  không được thử. Thứ **làm được ngay** là hai giới hạn r259 tự viết ra chống lại
  chính kết quả của nó.
  **GIỚI HẠN 1 — ĐÓNG: log đầy đủ trên cả sáu route, không phải hai.** r259 verify
  **tính đầy đủ** (không chỉ invariant nguyên tử r207 kiểm) trên **hai trên sáu**
  route và nói rõ như vậy. Chạy đúng phép kiểm đó cho bốn route còn lại: bybit BTC
  (ledger 316, giữ 5, log 3 closes) — 2 trước-deploy vắng, **3 sau-deploy CÓ ĐỦ**;
  bybit XAUT (3/2/1) — 1 trước-deploy vắng, 1 sau-deploy có; exness BTC (485/4/3) —
  1 trước-deploy vắng, **3 sau-deploy CÓ ĐỦ**; binance XAU (8/1/1) — 1 sau-deploy
  có. **KHÔNG MISMATCH TRÊN BẤT KỲ ROUTE NÀO**: mọi trade ledger giữ lại có
  `exit_at` từ mốc deployment (worker start 2026-08-27T14:35Z) trở đi đều xuất hiện
  trong log với timestamp khớp; mọi trade trước mốc đó đều vắng, đúng như phải
  vậy. Cộng với hai route của r259, durable Portfolio trade log nay **verify ĐẦY
  ĐỦ trên 6/6 route** — đúng thứ r207 nói rõ là chưa lập được.
  **GIỚI HẠN 2 — ĐÓNG VÀ ĐỊNH LƯỢNG: thiên lệch cuối tuần có thật và NHỎ.** Phép
  hiệu chỉnh cần **exposure giao dịch được** từng route, đếm trực tiếp bằng số bar
  5m đã đóng trong cửa sổ: **năm** route có **554 bar** (100%), **chỉ**
  `exness.cfd.XAU.USD` có **353** (63,7%). **CHỈ MỘT TRONG BA ROUTE XAU đóng cửa
  cuối tuần** — `binance XAU/USDT` là perpetual future và `bybit XAUT/USDT` là spot
  Tether Gold; **cả hai chạy 24/7 với 554 bar, exposure GIỐNG HỆT mọi route BTC, và
  mỗi route đóng đúng MỘT lệnh**. Pool có trọng số exposure: **BTC 10 closes/1662
  bar → 12,13/tuần** KTC [5,82; 22,31] **chưa kết luận**; **XAU 3/1461 → 4,14/tuần**
  [0,85; 12,10] **chưa kết luận**. Ở đúng exposure của BTC, các route XAU sẽ tạo ra
  **3,41 closes so với 10 của BTC**, nên **phần đóng cửa chỉ chiếm 0,41 trên khoảng
  cách 7,00 closes = 5,9%**. **Thiên lệch có thật, nó nâng rate XAU gộp từ 3,6 lên
  4,14/tuần, và nó KHÔNG đổi gì**: XAU vẫn dưới vạch 7/tuần theo point estimate,
  vẫn chưa kết luận được ở 95%, và khoảng cách XAU/BTC **sống sót gần như nguyên
  vẹn**. r259 đúng khi nêu nó và đúng khi không dựa vào nó.
  **MỘT ĐÍNH CHÍNH ĐÁNG GHI:** `binance.perpetual_future.XAU.USDT` có **554 bar
  trong cửa sổ và đủ 2016 bar tuần đầy đủ vừa rồi** — **kline coverage 24/7 hoàn
  chỉnh**. Mô tả route đó là "đóng băng từ 2025-12-26" ở r206 nói về **Portfolio
  ledger không giao dịch**, **không phải** thiếu market data; vòng sau **không**
  được đọc "route đóng băng" thành lỗ hổng dữ liệu.
  **GIỚI HẠN:** **KHÔNG có verdict Target 3** — cả hai pool vẫn chưa kết luận được
  ở 95% **sau** hiệu chỉnh, y như trước; vòng này **không** dịch chuyển câu hỏi đó
  và **không thể**, nó bị chặn bởi **thời gian trôi qua**, không phải bởi phân
  tích. **CHƯA lập được** rằng exposure tính bằng bar đã đóng là mẫu số đúng cho
  Target 3 — nó đúng cho câu "chiến thuật có bắn đủ thường xuyên so với số cơ hội
  nó có không", nhưng nếu yêu cầu vận hành là **số quyết định theo LỊCH mỗi tuần
  bất kể giờ giao dịch** thì cột **chưa hiệu chỉnh** mới là cột tính và exness XAU
  đọc **3,6/tuần chứ không phải 5,7**; cả hai được trình bày vì **mẫu số mà target
  hàm ý không phải thứ vòng này giải quyết được**. Khoảng cách XAU/BTC nay **đã
  biết KHÔNG phải do giờ giao dịch**; **không** có gì ở đây nói nó là do cái gì.
  PnL không xem xét vòng này. File:
  `round260-log-complete-on-all-six-routes-and-the-weekend-bias-explains-6pct-of-the-gap.md`.

- **Round 261 (2026-08-29) — CORRECTION: KHÔNG HỀ CÓ khoảng cách tần suất XAU/BTC.
  Chính cách gộp route của TÔI ở r259-260 đã tạo ra nó. KHÔNG CONTAINER.** Trả lời
  câu hỏi r260 để mở ("khoảng cách XAU/BTC đã biết **không** do giờ giao dịch;
  không có gì ở đây nói nó do cái gì"). **GIẢ THUYẾT VÀ DỰ ĐOÁN ĐÃ GHI RA ĐĨA
  TRƯỚC KHI KÉO BẤT KỲ LỊCH SỬ TRADE NÀO** (`precommit_r261.md`, iteration 56):
  band bảo vệ triển khai là **fractional** và giống hệt trên mọi route (STOP 0,01 /
  TAKE 0,02, xác nhận live ở r259), trong khi BTC biến động mỗi bar **~2,4 lần**
  XAU — nên một band cố định theo **tỉ lệ giá** sẽ mất nhiều thời gian hơn để chạm
  trên XAU. **P1** hold trung vị XAU > BTC theo tỉ lệ nghịch biến động (~2,4x);
  **P2** XAU có tỉ lệ close **không** chạm stop/take cao hơn; **P3** nếu P1 và P2
  đúng thì khoảng cách tần suất là hệ quả của band một-cỡ. Bằng chứng: ledger
  `paper-backtest-fixed-pct` mang **lịch sử trade ĐẦY ĐỦ kèm timestamp vào/ra** —
  **392** trade exness XAU và **473** binance BTC, mỗi bên ~361 ngày.
  **P1 — XÁC NHẬN MỘT PHẦN, YẾU HƠN DỰ ĐOÁN:** hold trung vị **8,46h so với
  6,17h = 1,37x** (mean 1,75x, p75 1,61x) so với **2,39x** dự đoán từ vol 4h trung
  vị 0,433% vs 1,036% — **đúng chiều, độ lớn rõ ràng THIẾU**, tôi không làm tròn
  lên. **P2 — XÁC NHẬN MẠNH:** close reason XAU stop_loss 32,1% / take_profit
  20,4% / **target_flat 47,4%** so với BTC 59,0% / 27,1% / **14,0%** — **gần một
  nửa** trade XAU **không bao giờ chạm** band bảo vệ, so với **một trên bảy** ở
  BTC; band fractional cố định **ràng buộc yếu hơn nhiều** trên instrument êm hơn.
  Đây là phần duy nhất của giả thuyết **sống sót sạch sẽ**.
  **P3 — BỊ BÁC VÌ TIỀN ĐỀ SAI:** dài hạn trên chính khoảng ~1 năm của mỗi ledger:
  **exness XAU 7,60 close/tuần; binance BTC 9,14/tuần — TỈ LỆ 1,20x**, KHÔNG phải
  khoảng cách ~3x mà r259 và r260 dành hai vòng để mô tả. Và số đếm live là **rút
  thăm bình thường** từ các rate đó: exness XAU kỳ vọng 2,09 quan sát 1
  (P(X≤1)=0,38); BTC gộp kỳ vọng 7,52 quan sát 10 (P(X≥10)=0,23). **Không hề có
  khoảng cách nào để giải thích**; P3 rút lại cùng với câu hỏi nó trả lời.
  **KHOẢNG CÁCH GIẢ ĐẾN TỪ ĐÂU — TỪ CHÍNH CÁCH GỘP CỦA TÔI:** `trade_count` trọn
  đời từng route: exness BTC 485, binance BTC 479, **exness XAU 395**, bybit BTC
  316, **binance XAU 8**, **bybit XAUT 3**. r259/r260 gộp ba route XAU chọi ba
  route BTC — nhưng "pool XAU" trộn **MỘT route trưởng thành** (395 trade trọn
  đời, ngang mọi route BTC) với **HAI route gần như ngủ đông** (8 và 3 trade trọn
  đời). Gộp như vậy cho ra một trung bình thấp **không mô tả gì cả**. **CÁCH GỘP
  ĐÓ LÀ CỦA TÔI, ở CẢ HAI VÒNG, VÀ NÓ SAI.** r260 còn tính hiệu chỉnh exposure rồi
  báo rằng khoảng cách "sống sót gần như nguyên vẹn" — **đúng về số học và trật
  trọng tâm**, vì khoảng cách là do **thành phần**, không phải do exposure; sửa mẫu
  số **không bao giờ** phát hiện được điều đó, chỉ nhìn từng route riêng mới thấy.
  **QUY TẮC RÚT RA: trước khi gộp route, kiểm tra chúng có tương đương về HOẠT
  ĐỘNG TRỌN ĐỜI không, chứ không chỉ về exposure — thời gian quan sát bằng nhau
  KHÔNG làm cho một route ngủ đông và một route trưởng thành gộp được với nhau.**
  **HỆ QUẢ CHO TARGET 3:** dài hạn, **cả hai route trưởng thành đều TRÊN vạch
  7/tuần** — exness XAU **7,60** (biên **+8,6%**), binance BTC **9,14** (+30,6%) —
  **ngược hẳn** với gợi ý từ point estimate live của XAU; và 7,60 của XAU **trùng
  khít** con số backtest ~7,2-7,3/tuần (18 tháng) của r92, một sự đồng thuận độc
  lập từ đường dữ liệu khác. r259/r260 **đúng** khi từ chối ra verdict Target 3 —
  vì lý do còn mạnh hơn khoảng tin cậy của chúng: **rate XAU gộp mà chúng từ chối
  kết luận vốn không đo đúng thứ mà nhãn của nó nói.**
  **GIỚI HẠN:** đây là ledger **seed `paper-backtest-*`** — cùng strategy và config,
  trọn một năm, nhưng là **BACKTEST**; cửa sổ live vẫn 46h và vẫn **không** giải
  quyết được Target 3. **VÌ SAO `binance XAU` (8) và `bybit XAUT` (3) GẦN NHƯ NGỦ
  ĐÔNG THÌ CHƯA GIẢI THÍCH ĐƯỢC** — đó là hiện tượng **khác** với "giao dịch thưa
  hơn", và nay là **câu hỏi được đặt tốt hơn** thay cho câu r260 để mở. Khác biệt
  cấu trúc ở P2 **chưa** được chứng minh ảnh hưởng tới **rate** (hai rate chỉ cách
  nhau 1,20x). 7,60 của XAU là số **backtest** với biên **mỏng 8,6%**, khớp với
  việc r92 gọi biên này là mỏng. PnL không xem xét. File:
  `round261-CORRECTION-there-was-no-xau-btc-frequency-gap-my-pooling-created-it.md`.

- **Round 262 (2026-08-29) — DATA-ISSUE: hai route "ngủ đông" KHÔNG hề ngủ đông —
  chúng replay đúng 14 ngày và 2 ngày trong một cửa sổ cấu hình 365 ngày, và một
  route có backfill lịch sử KẸT từ 2025-12-25. KHÔNG CONTAINER. Chỉ điều tra,
  KHÔNG áp dụng gì** (theo Claude role note trong
  `.agents/rules/coding-and-verification.md`). Trả lời câu hỏi r261 bàn giao.
  **KHÔNG PHẢI DO DỮ LIỆU, CŨNG KHÔNG PHẢI DO TẦN SUẤT QUYẾT ĐỊNH:** coverage 5m
  trong Timescale là **binance XAU 75 232 bar từ 2025-12-11** và **bybit XAUT
  145 481 bar từ 2025-04-11** (8 và 16 tháng liên tục), và
  `last_portfolio_primary_close_time` của **cả hai** là **bar hiện tại**
  2026-08-29T13:29:59Z.
  **NGUYÊN NHÂN: REPLAY CHỈ SEED MỘT MẨU CỦA CỬA SỔ ĐƯỢC CẤU HÌNH.** Cửa sổ đọc
  hẹp từ chính container đang chạy (`env | grep -E '^HISTORICAL_[A-Z_]*REPLAY_DAYS='`,
  **một biến duy nhất, KHÔNG dump**): **`HISTORICAL_DEMO_REPLAY_DAYS=365`** trên cả
  hai worker kiểm tra. Cả ba replay **hoàn tất cách nhau chưa tới 17 giờ**
  (2026-08-22T13:26/13:27Z và 2026-08-23T06:11Z). Span trade được seed:
  **exness XAU 361 NGÀY** (2025-08-25..2026-08-21, 392 trade) — **đúng y như cấu
  hình**; **binance XAU 14 NGÀY** (2025-12-12..2025-12-26, 7 trade) so với **~254
  ngày có sẵn** trong cửa sổ; **bybit XAUT 2 NGÀY** (2026-08-19..21, 1 trade) so
  với **365 ngày có sẵn**. binance XAU bỏ lại ~240 ngày dữ liệu trong cửa sổ chưa
  replay; bybit XAUT bỏ lại ~363 ngày và **chỉ seed đúng hai ngày CUỐI** cửa sổ của
  chính nó. **Số trade trọn đời thấp KHÔNG phải tần suất quyết định thấp** — nó là
  hệ quả số học của một seed phủ gần như không gì trong khoảng nó được cấu hình để
  phủ.
  **TÍN HIỆU HỖ TRỢ:** `runtime_state.pending_history_backfill` — **binance XAU giữ
  508 bar 5m KẸT ở 2025-12-23T11:05Z..2025-12-25T05:20Z = ~8 THÁNG CŨ**; exness XAU
  giữ 1000 bar ở 2026-08-07..08-12 (~17 ngày); bybit XAUT **không có key này**.
  SKILL `quant-research-loop` nói rõ trường này "phải xoay vòng với timestamp gần
  hiện tại; một cụm cũ, không tiến triển là **bug thật**, không bình thường".
  **Cụm của binance XAU kẹt ở 2025-12-23…25 còn span seed của nó KẾT THÚC
  2025-12-26** — hai ranh giới trùng nhau trong vòng một ngày, và 2025-12-26 đúng
  là ngày r206 ghi route đó đóng băng. **Ba quan sát độc lập rơi vào cùng một ngày**
  là phần mạnh nhất của vòng này. bybit XAUT có **hình dạng khác** — không có cụm
  pending nào và seed gói gọn trong hai ngày cuối — nên **không cùng một lỗi**, chỉ
  cùng một lớp.
  **MỘT KHÁC BIỆT LÀ BÌNH THƯỜNG, ghi lại để không bị nhầm thành nguyên nhân:**
  `historical_replay_completed_scopes` là **27** ở exness XAU và **19** ở hai route
  kia — suy ra từ số strategy (3 strategy × 8 interval + 3 paper rule = 27; 2×8+3 =
  19), `strategy_weights` xác nhận. Đây là khác biệt **cấu hình**, không phải lỗi,
  và **không** giải thích span seed.
  **FINDING CHO CODEX — CHƯA ÁP DỤNG, CHỈ ĐIỀU TRA. P2** (nâng lên P1 nếu ảnh hưởng
  quyết định live, **chưa xác lập**): replay seed span khác nhau cực lớn dưới cùng
  một `HISTORICAL_DEMO_REPLAY_DAYS=365`, và một route mang cụm backfill đứng im tám
  tháng đúng tại ranh giới ledger của nó dừng. **EXPECTED:** replay mỗi route seed
  `min(365 ngày, lịch sử có sẵn)` và hàng đợi backfill tiến về hiện tại.
  **VERIFY SAU KHI FIX:** span seed mỗi route khớp `min(365d, available)`;
  `pending_history_backfill` tiến về hiện tại trên **mọi** route; `trade_count`
  trọn đời hai route tăng lên mức so sánh được với 7,60/tuần của exness XAU.
  **GIỚI HẠN:** **NGUYÊN NHÂN CHƯA XÁC LẬP** — không điều tra mức code, cố ý để lại
  cho Codex. **CHƯA CHỨNG MINH quan hệ nhân quả** giữa backfill kẹt và seed ngắn:
  ngày trùng nhau ở binance XAU **nhưng bybit XAUT có seed ngắn mà KHÔNG có cụm
  kẹt nào**, nên backfill kẹt **không thể** là cơ chế chung. Chưa chứng minh điều
  này ảnh hưởng giao dịch **live** chứ không chỉ seed — cả hai route hiện **đang**
  đóng lệnh và binance XAU tạo một lệnh ngày 2026-08-28. Chưa chứng minh hai route
  sẽ đạt 7,60/tuần nếu seed đầy đủ — đó là **giả thuyết mà một bản fix sẽ kiểm**.
  Không phát biểu gì về PnL: 8 và 3 trade trọn đời không đỡ nổi một phát biểu như
  vậy. File:
  `round262-two-routes-replayed-a-sliver-of-their-configured-window-and-one-has-a-backfill-stuck-8-months.md`.

- **Round 263 (2026-08-29) — LOẠI TRỪ ĐƯỢC BỐN NGUYÊN NHÂN: cửa sổ replay, độ sâu
  dữ liệu, tính liên tục dữ liệu, và replay hoàn tất. Nghi ngờ còn lại là một VÒNG
  LẶP PHẢN HỒI mà một snapshot KHÔNG tách được chiều nhân quả. KHÔNG CONTAINER,
  chỉ điều tra, không áp dụng gì.** r262 đẩy phần điều tra code sang Codex — **đó
  là chia việc SAI**: theo Claude role note trong
  `.agents/rules/coding-and-verification.md`, **ĐIỀU TRA là việc của Claude**, chỉ
  **triển khai** mới là của Codex. Vòng này làm phần điều tra đó.
  **BỐN NGUYÊN NHÂN ỨNG VIÊN BỊ LOẠI:** (1) **cửa sổ replay đồng nhất và đúng** —
  `historical_replay.rs:177` tính `from_time = to_time - Duration::days(days.max(1))`
  với `days = cfg.historical_replay_days` (`main.rs:854`), và
  `HISTORICAL_DEMO_REPLAY_DAYS=365` đã đọc hẹp ở r262: **cùng cửa sổ, cùng code
  path, mọi route**. (2) **replay báo HOÀN TẤT cả ba route** —
  `historical_replay_completed_scopes` 19/19, 19/19, 27/27, **không interval nào
  còn pending**; vòng retry `main.rs:862-905` chỉ thoát khi
  `pending_replay_intervals()` rỗng. (3) **độ sâu dữ liệu đủ** — binance XAU 75 232
  bar 5m từ 2025-12-11 (~254 ngày trong cửa sổ), bybit XAUT 145 481 từ 2025-04-11
  (đủ 365). (4) **tính liên tục SẠCH — và còn sạch hơn ở route "hỏng" so với route
  khoẻ**: gap marker 5m từ 2025-12-11 là binance XAU **75 236 bar / 0 marker / 0
  gap candle**; bybit XAUT **75 333 / 0 / 0**; exness XAU 50 530 / **185** / 24 602.
  **Route seed ĐÚNG lại là route CÓ gap marker** (đóng cửa cuối tuần, ghi nhận
  đúng), còn hai route seed gần như không gì **có dữ liệu liên tục hoàn hảo**. Điều
  này cũng gạt bỏ giả thiết cụm `pending_history_backfill` kẹt ở binance XAU (r262)
  phản ánh bar thiếu — **những bar đó có mặt và không bị đánh dấu gap** trong
  Timescale.
  **NGHI NGỜ CHUYỂN VỀ ĐÂU:** `PortfolioConstructionState::decide`
  (`finance-core/src/trading_modes.rs:842-857`) hold theo **ba** điều kiện:
  `entry_score.abs() < minimum_role_score` (**dòng 851**);
  `trend_score.abs() < minimum_role_score` (**854**); và
  `entry_score.is_sign_positive() != trend_score.is_sign_positive()` → hold
  **`entry_trend_conflict`** (**856**). `minimum_role_score = 0.1` ở cả ba route.
  `strategy_weights` triển khai khác hẳn nhau: **exness XAU `candle_momentum
  1.000`** (chỉ MỘT non-zero, 395 trade); **binance XAU 0.373 + `rsi_mean_reversion`
  0.627** (8 trade); **bybit XAUT 0.164 + `rsi_mean_reversion` 0.836** (3 trade).
  r257 đã lập, đối chiếu một control **cam kết trước**, rằng `candle_momentum` và
  `rsi_mean_reversion` phản ứng với độ lớn xu hướng theo **hai chiều NGƯỢC NHAU** —
  nên trộn chúng ở trọng số tương đương chính là cấu hình đẩy role score về 0 và
  đẩy dấu của chúng vào bất đồng, kích hoạt một trong ba gate hold; route trưởng
  thành chạy **một** cơ chế duy nhất ở 1.0, không có triệt tiêu. Payload production
  r207 cho thấy đúng hình dạng đó (`candle_momentum +0.381` cạnh
  `rsi_mean_reversion −0.045`).
  **VÌ SAO TÔI KHÔNG GỌI ĐÓ LÀ NGUYÊN NHÂN:** `strategy_weights` là **ĐẦU RA** của
  công thức reweight, được nuôi bởi chính các simulated ledger — mà ledger hai route
  đó chỉ có **7 và 1** trade seed. Nên trọng số bị trộn có thể là **TRIỆU CHỨNG**
  của seed rỗng chứ không phải nguyên nhân. Vòng lặp: `seed ngắn → gần như không có
  bằng chứng ledger → trọng số trộn/suy biến → role score triệt tiêu hoặc xung đột
  dấu → rất ít quyết định → gần như không có bằng chứng ledger`. **Một snapshot
  KHÔNG xác định được chiều của vòng lặp đó**, và tôi **không** trình bày một cơ
  chế vừa khớp như thể nó đã được đo — r252, r254 và r261 đều là những lần tôi đọc
  một câu chuyện vừa khớp thành kết quả, và đây đúng hình dạng đó.
  **PHÉP TEST QUYẾT ĐỊNH, ĐẶT CHÍNH XÁC:** đếm **hold reason** thực sự phát ra theo
  route trong một cửa sổ cố định (`entry_score_below_threshold`,
  `trend_score_below_threshold`, `entry_trend_conflict` — phát tại
  `trading_modes.rs:851/854/856`) và so hai route hỏng với exness XAU. Nếu
  `entry_trend_conflict` **áp đảo** ở hai route hỏng → cơ chế trọng số đối nghịch
  được xác nhận và bản fix là về **thành phần trọng số**; nếu hai gate ngưỡng áp đảo
  → là **độ lớn score**, không phải xung đột dấu; nếu hold reason **giống nhau** ở
  cả ba route → gate **không phải** nơi quyết định bị mất và **chính đường replay**
  có lỗi. **Việc các chuỗi đó có được lưu đếm được trong checkpoint hay chỉ được
  log thì vòng này CHƯA xác định** — đó là thứ **đầu tiên** vòng sau nên kiểm.
  **TRẠNG THÁI FINDING CHO CODEX:** vẫn **P2**, vẫn **CHƯA áp dụng**; quan sát r262
  đứng vững, vòng này loại bốn nguyên nhân và khu trú nghi ngờ vào tương tác
  **seed-replay ↔ reweight trọng số**. **CHƯA khuyến nghị hướng fix** vì một bản fix
  nhắm vào trọng số sẽ sai nếu nguyên nhân là seed, và ngược lại.
  **GIỚI HẠN:** loại được cửa sổ/hoàn tất/độ sâu/liên tục **KHÔNG** miễn tội cho
  những gì xảy ra **BÊN TRONG** replay; chưa có nguyên nhân nào cho cụm backfill
  kẹt, chỉ biết nó **không** do bar thiếu hay bị đánh dấu gap; không nói gì về PnL
  hay Target 3 trên hai route này. File:
  `round263-the-replay-window-and-data-are-clean-the-suspicion-moves-to-a-self-reinforcing-weight-loop.md`.

- **Round 264 (2026-08-29) — CẢ SÁU ROUTE RA QUYẾT ĐỊNH VỚI CÙNG MỘT NHỊP. "Ngủ
  đông" chỉ là ARTIFACT CỦA SEED, và P2 của tôi HẠ CẤP xuống P3. KHÔNG CONTAINER.**
  Chạy đúng bước r263 nêu. **Hold reason KHÔNG đếm được:**
  `finance_live_action_portfolio_decisions_total` là metric quyết định **duy nhất**
  và **không có label `reason`** (`metrics.rs:1173-1175`); không có label `reason`
  nào trong cả file — nên **phép test ba nhánh r263 thiết kế KHÔNG chạy được từ
  metrics**. **Nhưng** counter đó vẫn quyết định cho một phép tách khác, nhờ **vị
  trí** nó tăng (`trading_api.rs:1708`): **một lần cho mỗi Portfolio primary đã
  đồng bộ, HOLD hay TRADE đều tính**, và chỉ sau guard `is_synchronized`
  (`trading_api.rs:1694-1700`) — nên nó tách được "vòng quyết định không chạy /
  không đồng bộ" khỏi "vòng chạy và ra hold".
  **ĐO ĐƯỢC** (scrape read-only từ `:8002/metrics` của chính mỗi worker):
  `evidence_intervals_complete/required` = **8/8 TRÊN CẢ SÁU ROUTE**, gồm cả hai
  route "ngủ đông"; `portfolio_decisions_total` = exness XAU **342**, binance XAU
  **571**, bybit XAUT **571**, binance BTC **571**, exness BTC **571**, bybit BTC
  **571**. **NĂM ROUTE ĐÚNG 571, GỒM CẢ HAI ROUTE "NGỦ ĐÔNG"**; 342 của exness XAU
  thấp hơn vì lý do đã biết (CFD vàng đóng cửa cuối tuần).
  **ĐIỀU NÀY GIẢI QUYẾT:** hai route **KHÔNG ngủ đông trong vận hành live** — chúng
  dựng quyết định đúng nhịp các route BTC khoẻ, evidence đồng bộ đầy đủ, và trong
  cùng cửa sổ live tạo 1 close mỗi route so với 3-4 của BTC — tỉ lệ **nhất quán**
  với dài hạn 7,60 vs 9,14/tuần của r261 và **nằm gọn trong nhiễu** r261 đã lập.
  Phép test ba nhánh của r263 vì thế **giải quyết được mà không cần hold reason**:
  **đường replay KHÔNG làm mất quyết định live, và đồng bộ hoá cũng không**. Phần
  mất tạo ra 8 và 3 trade **TRỌN ĐỜI** chỉ giới hạn trong **seed lịch sử**, thứ
  r262 đo là 14 ngày và 2 ngày so với 365 được cấu hình.
  **P2 CỦA TÔI HẠ CẤP — nói thẳng, vì chính tôi nêu nó.** r262 xếp P2, có thể P1
  "nếu ảnh hưởng quyết định live, **chưa xác lập**". Nay **đã xác lập là KHÔNG**:
  không ảnh hưởng dựng quyết định, không ảnh hưởng đồng bộ. Mức đúng là **P3** —
  một bất nhất khi seed lịch sử để lại hai route với ledger backtest gần rỗng và
  một cụm backfill cũ, **không có tác động live nào được chứng minh**. **HẠ CẤP,
  KHÔNG PHẢI ĐÓNG**, vì đúng một lý do: seed nuôi công thức reweight, và hai route
  đó mang trọng số trộn `candle_momentum`/`rsi_mean_reversion` trong khi route khoẻ
  mang một cơ chế duy nhất ở 1.0 (r263) — **đó là một đường lan truyền THẬT từ seed
  sang hành vi live**. Vòng này chỉ cho thấy **không thấy tổn hại trong nhịp quyết
  định**, chứ **không** phải không có tổn hại.
  **GIỚI HẠN:** **gate hold nào kích hoạt và theo tỉ lệ nào thì vẫn CHƯA BIẾT** —
  metric không có label reason nên phép test r263 thiết kế **vẫn chưa chạy**; đường
  còn lại là **application log**, **chưa đọc** vòng này. Chưa chứng minh trọng số
  trộn là vô hại — chỉ cho thấy chúng **không** chặn việc **DỰNG** quyết định, còn
  ảnh hưởng lên **KẾT QUẢ** quyết định thì **chưa đo**. 342 của exness XAU **nhất
  quán** với cuối tuần và với coverage 63,7% (r260) nhưng 342/571 = 0,60 so với
  0,637 là **khớp xấp xỉ, không phải đã kiểm chứng**. **Chưa có nguyên nhân** cho
  seed ngắn hay backfill kẹt — quan sát r262 và bốn phép loại trừ r263 đều đứng
  vững, nguyên nhân vẫn chưa biết và vẫn thuộc về Codex. PnL không xem xét. File:
  `round264-all-six-routes-decide-at-identical-cadence-the-dormancy-is-a-seed-artifact.md`.

- **Round 265 (2026-08-29) — HOLD REASON KHÔNG QUAN SÁT ĐƯỢC Ở MỨC TỔNG HỢP, nên
  phép test quyết định của r263 KHÔNG THỂ CHẠY; và HOLD LÀ TRẠNG THÁI BÌNH THƯỜNG
  trên MỌI route. KHÔNG CONTAINER.** Đóng nốt đường cuối r264 để mở ("đường còn lại
  là application log, chưa đọc vòng này"). **REASON KHÔNG BAO GIỜ VÀO LOG:** trong
  sáu giờ output của worker binance XAU, `grep -c` cho
  `entry_trend_conflict|entry_score_below_threshold|trend_score_below_threshold`
  trả **0**, và `grep -c gate_reason` trả **0**. Nơi duy nhất reason tồn tại là
  `inner.signal_states` (`trading_api.rs:1803-1821`), lưu `gate_reason`,
  `gate_passed`, `entry_score`, `trend_score` cho **DUY NHẤT lần đánh giá mới
  nhất**, bên trong checkpoint Redis. Vậy phép test ba nhánh r263 thiết kế —
  *đếm hold reason theo route rồi so sánh* — **KHÔNG CHẠY ĐƯỢC TỪ BẤT KỲ BỀ MẶT
  PRODUCTION NÀO**: không từ `/metrics` (không có label `reason`, r264 đã lập),
  không từ log (không bao giờ phát ra), không từ checkpoint (một lần đánh giá, không
  phải một phép đếm). **ĐÂY LÀ KHOẢNG TRỐNG OBSERVABILITY, KHÔNG PHẢI THIẾU CÔNG
  SỨC.** **LẤY MẪU KHÔNG THAY THẾ ĐƯỢC:** tôi đọc checkpoint **hai lần** cách nhau
  vài phút với ý định có hai mẫu độc lập, và lần đọc thứ hai trả về giá trị **GIỐNG
  HỆT TỪNG BYTE** cho cả ba route trùng nhau — checkpoint chưa được ghi lại trong
  khoảng đó — **nên vòng này có n = 1 mỗi route, KHÔNG phải n = 2**; tôi ghi lại vì
  tôi đã định nhân đôi mẫu và đã **không** làm được.
  **ẢNH CHỤP DUY NHẤT CHO THẤY GÌ — VÀ NÓ CHỈ NGƯỢC HƯỚNG r263:** bốn route tại
  cùng một thời điểm — binance BTC (**khoẻ**) `entry_trend_conflict` entry −0,1707
  trend +0,1759; exness BTC (**khoẻ**) `entry_score_below_threshold` entry −0,0405
  trend −0,0693; binance XAU (**"hỏng"**) `entry_score_below_threshold` entry
  +0,0722 trend −0,3476; bybit XAUT (**"hỏng"**) `entry_trend_conflict` entry
  +0,1038 trend −0,5023. **CẢ BỐN ĐỀU ĐANG HOLD, và CẢ HAI loại gate đều kích hoạt
  ở route khoẻ lẫn route "hỏng"**; entry và trend ngược dấu xuất hiện ở **3 trên 4**
  route, **kể cả một route khoẻ**. **KHÔNG có dấu hiệu nào tách được hai nhóm.**
  **HOLD LÀ TRẠNG THÁI BÌNH THƯỜNG Ở MỌI NƠI, nên "chúng hold nhiều" chưa bao giờ
  là dấu hiệu chẩn đoán:** ghép counter r264 với số close live — binance BTC 4/571 =
  **0,70%** pass (**hold 99,30%**), exness BTC 3/571 = 0,53% (99,47%), bybit BTC
  3/571 = 0,53% (99,47%), binance XAU 1/571 = **0,18%** (99,82%), bybit XAUT 1/571 =
  0,18% (99,82%). **Các route KHOẺ hold 99,3-99,5% thời gian**, và chênh lệch giữa
  hai nhóm là 3-4 sự kiện so với 1 — **nhiễu Poisson**, nhất quán với r261 và r264.
  **HỆ QUẢ CHO GIẢ THUYẾT r263:** r263 nêu rằng trọng số trộn
  `candle_momentum`/`rsi_mean_reversion` đẩy role score vào triệt tiêu hoặc xung đột
  dấu ở hai route đó, và **đã tự từ chối gọi nó là nguyên nhân**. **Bằng chứng duy
  nhất lấy được KHÔNG ủng hộ nó**: route **khoẻ** binance BTC cho **cùng** dấu hiệu
  ngược dấu tại cùng thời điểm, và cả hai gate đều kích hoạt ở cả hai nhóm. Giả
  thuyết **KHÔNG bị bác** — một quan sát không bác được cũng như không xác nhận
  được — nó **KHÔNG TEST ĐƯỢC VỚI INSTRUMENTATION HIỆN TẠI**, đó là điều **khác** và
  hữu ích hơn.
  **THỨ SẼ GỠ TẮC — NÊU TÊN, KHÔNG TRIỂN KHAI:** một counter có label reason, ví dụ
  `finance_live_action_portfolio_holds_total{reason="entry_trend_conflict"}`, hoặc
  phát reason trên đường quyết định hiện có để đếm được từ log; cách nào cũng biến
  phép test r263 thành **một lần scrape**. **KHÔNG đề xuất thành việc và KHÔNG triển
  khai** — ghi lại để vòng sau **không** phải đi lại đúng ngõ cụt này. Mức **P3**,
  cùng hạng với item seeding đã hạ cấp của r262.
  **GIỚI HẠN:** **KHÔNG** claim gì về **phân bố** hold reason — n = 1 mỗi route,
  bảng trên là **một thời điểm**, không phải bằng chứng về hành vi điển hình; **không**
  claim checkpoint không bao giờ refresh đủ nhanh để lấy mẫu — hai lần đọc trong một
  vòng thì giống nhau, nhưng **chưa thử** chuỗi cách xa hơn và nó có thể được; chưa
  có nguyên nhân cho seed ngắn hay backfill kẹt, r262 và r263 đứng nguyên; không nói
  gì về PnL hay Target 3. File:
  `round265-the-hold-reason-is-unobservable-in-aggregate-so-round-263s-test-cannot-be-run.md`.

- **Round 266 (2026-08-29) — LẤY MẪU XUYÊN VÒNG HOẠT ĐỘNG (nên chính `/loop` có thể
  tích luỹ được phân bố mà r265 không đọc trực tiếp được), và `trend_score` KHÔNG
  NHÚC NHÍCH trong 20 phút. KHÔNG CONTAINER.** Test đúng một thứ r265 để lại chưa
  thử ("chưa claim rằng checkpoint không bao giờ refresh đủ nhanh để lấy mẫu — hai
  lần đọc trong một vòng thì giống nhau, nhưng **chưa thử** chuỗi cách xa hơn").
  Hai mươi phút cách lần đọc của r265 = **4+ lần đóng nến 5m**.
  **NÓ HOẠT ĐỘNG — với `entry_score`:** binance BTC −0,1707 → **−0,1278** (đổi);
  binance XAU +0,0722 → +0,0722 (không); bybit XAUT +0,1038 → **+0,1969** (đổi);
  exness BTC −0,0405 → **−0,0119** (đổi). **`entry_score` đổi ở 3/4 route.** Vậy
  `/loop` **làm được vai trò sampler**: mỗi vòng một quan sát mỗi route, tích luỹ
  dần thành phân bố. **Đây là ĐƯỜNG VÒNG cho khoảng trống observability, KHÔNG phải
  bản vá** — khoảng trống r265 ghi nhận **vẫn còn nguyên**. Đã tạo log append-only
  tại **`research/quant/samples/signal-state-samples.csv`**, seed sẵn 4 mẫu của r265 và 4
  mẫu vòng này (8 dòng); **vòng sau nên append một dòng mỗi route** thay vì dựng
  lại từ đầu.
  **MỘT ĐÍNH CHÍNH NGAY TRONG VÒNG:** lần chạy đầu tôi báo **4/4 route đổi** —
  **SAI**: nó so float đầy đủ độ chính xác của live với chính bản chép 4 chữ số thập
  phân của tôi từ r265, nên giá trị **không đổi** của binance XAU bị tính thành đổi.
  Chạy lại đúng độ chính xác đã ghi thì là **3/4**.
  **PHÁT HIỆN CÓ SỨC NẶNG HƠN — `trend_score` ĐỨNG YÊN:** `trend_score` **giống hệt
  tới 4 chữ số trên CẢ BỐN route** suốt hai mươi phút, trong khi `entry_score` đổi ở
  ba route (**0/4 so với 3/4**). Hai score rõ ràng chạy trên **hai đồng hồ khác
  nhau** — `entry_score` theo interval quyết định 5m, `trend_score` neo vào bằng
  chứng khung thời gian cao hơn chưa đóng trong khoảng đó. **ĐIỀU NÀY QUAN TRỌNG**
  vì `entry_trend_conflict` (`trading_modes.rs:857`) là phép so **DẤU**: nếu dấu của
  `trend_score` bị **ghim** giữa hai lần đóng khung cao hơn, thì route nào có
  `entry_score` dao động quanh 0 ở **phía ngược lại** sẽ nằm trong xung đột **suốt
  những quãng dài** — **không phải ngẫu nhiên từng lần đánh giá mà mang tính CẤU
  TRÚC**, cho tới khi khung cao hơn đóng. Hai route có số trade trọn đời nhỏ nhất
  mang **`trend_score` độ lớn LỚN NHẤT trong nhóm**, đều âm và đều ổn định qua hai
  quan sát: binance XAU **−0,3476** và bybit XAUT **−0,5023**, so với route khoẻ
  +0,1759 và −0,0693; còn `entry_score` của chúng thì **dương** (+0,0722; +0,1038 →
  +0,1969), tức **ở phía ngược lại**. **ĐÂY LÀ HAI THỜI ĐIỂM CÁCH NHAU HAI MƯƠI
  PHÚT — MỘT LEAD, KHÔNG PHẢI KẾT QUẢ.** Sau r252, r254, r261 và r263 tôi **không**
  trình bày một mẫu hình hai quan sát như một cơ chế, và **đính chính ngay trên đây
  là lời nhắc rằng tôi làm sai những chuyện này khi vội**.
  **TÍCH LUỸ SẼ GIẢI QUYẾT ĐƯỢC GÌ** (một mẫu mỗi route mỗi vòng, vài chục vòng):
  phân bố hold reason theo route (**đúng phép test gốc của r263**); `trend_score`
  thực sự đổi bao lâu một lần, và do đó cách đọc "dấu bị ghim" có sống sót không;
  `trend_score` của hai route kia là **lớn-và-âm dai dẳng** hay chỉ tình cờ như vậy
  hôm 2026-08-29. **Không cần đổi instrumentation — chỉ cần số vòng.**
  **GIỚI HẠN:** **KHÔNG** claim `trend_score` "đứng yên" nói chung — nó không đổi
  trong **một** cửa sổ 20 phút trên bốn route, điều này nhất quán với việc neo khung
  cao hơn **và với vài giải thích khác**. **KHÔNG** claim `trend_score` âm lớn giải
  thích số trade trọn đời thấp — hai quan sát, và r264 đã cho thấy các route đó ra
  quyết định **cùng nhịp** còn r261 cho thấy chênh lệch rate live là **nhiễu**. Chưa
  có phân bố hold reason nào, vẫn n = 2 mỗi route là nhiều nhất. **KHÔNG** claim
  việc tích luỹ mẫu sẽ chạy được — nó phụ thuộc vào việc `trend_score` có đổi hay
  không qua quãng dài hơn, đúng thứ **chưa đo**. Không nói gì về PnL, Target 3, seed
  span hay backfill kẹt; r261-r265 đứng nguyên. File:
  `round266-cross-round-sampling-works-for-entry-score-and-trend-score-is-frozen.md`.

- **Round 267 (2026-08-29) — `trend_score` KHÔNG THỂ đổi nhanh hơn 1h **do CẤU
  HÌNH**, và `minimum_role_score` đòi tới **70% TOÀN BỘ ngân sách entry** của một
  route. KHÔNG CONTAINER.** Trả lời đại lượng r266 để ngỏ ("phụ thuộc vào
  `trend_score` có đổi hay không qua quãng dài hơn, đúng thứ **chưa đo**") — **bằng
  phân tích, không phải bằng chờ hàng chục vòng**. `role_scores()`
  (`trading_modes.rs:1042-1069`) chia bằng chứng theo `policy.required_intervals`,
  ánh xạ mỗi interval sang `Entry` hoặc `Trend`; đọc từ checkpoint live, map đó
  **GIỐNG HỆT trên cả bốn route**: **ENTRY = 5m/15m/30m; TREND = 1h/2h/4h/12h/1d**.
  Vậy **`trend_score` KHÔNG THỂ cập nhật nhanh hơn một lần đóng nến 1h**, và theo
  `interval_weights` thì **84-89% ngân sách trend nằm ở 4h/12h/1d** — thứ không thể
  đổi trong nhiều giờ tới một ngày: binance XAU ngân sách entry **0,1437** / trend
  0,8564 / phần chậm **88,8%**; bybit XAUT 0,2933 / 0,7068 / 84,2%; exness XAU
  0,2523 / 0,7475 / 68,4%. Điều đó **giải thích trọn vẹn** quan sát r266 **mà không
  cần tích luỹ**, và mẫu thứ ba xác nhận: `trend_score` **không đổi tới 4 chữ số
  trên cả bốn route qua cả ba mẫu, trải 37 phút**. Log mẫu
  `research/quant/samples/signal-state-samples.csv` nay có **12 quan sát** (vòng 265/266/267).
  **MỨC KHẮC NGHIỆT CỦA GATE ENTRY, ĐỊNH LƯỢNG:** `entry_score` là tổng có trọng số
  **chỉ trên các interval ENTRY**, nên **độ lớn TỐI ĐA của nó ĐÚNG BẰNG ngân sách
  trọng số entry**, trong khi `minimum_role_score` = 0,1 ở mọi route. Gate vì thế
  đòi: **binance XAU 0,1/0,1437 = 69,6%** của mức tối đa lý thuyết; exness XAU
  (khoẻ) **39,6%**; bybit XAUT **34,1%**. **binance XAU phải đạt ~70% mức tối đa lý
  thuyết mới qua được gate 1**, gần **gấp đôi** route khoẻ exness XAU; ba giá trị
  `entry_score` quan sát được của nó là +0,0722 / +0,0722 / +0,0121 và gate reason
  là `entry_score_below_threshold` **cả ba lần**.
  **HAI ROUTE ÍT TRADE HỎNG THEO HAI KIỂU KHÁC NHAU — KHÔNG PHẢI MỘT CƠ CHẾ MÀ
  HAI:** binance XAU trượt ở **ngưỡng** (below/below/below, trend ghim −0,3476);
  bybit XAUT **vượt ngưỡng thoải mái** (+0,1038/+0,1969/+0,1969) và trượt ở **xung
  đột dấu** với trend ghim lớn nhất nhóm (−0,5023, conflict/conflict/conflict). Đáng
  chú ý bybit XAUT có ràng buộc entry **LỎNG NHẤT** trong ba (34,1%), nên câu chuyện
  ngưỡng **không thể** là thứ giới hạn nó.
  **VÌ SAO ĐÂY VẪN CHƯA PHẢI KẾT QUẢ:** các route **khoẻ** kích hoạt **cùng những
  gate đó** trong cùng các mẫu — binance BTC: conflict/conflict/below; exness BTC:
  below/below/trend_below. **Cả bốn route đều hold, vì một hỗn hợp lý do**, nhất
  quán với tỉ lệ hold 99,3-99,8% mà r265 đo trên mọi route. Và `interval_weights`
  mang **đúng confound r263 đã nêu** cho `strategy_weights`: chúng là **ĐẦU RA** của
  công thức reweight, nuôi bởi ledger chỉ có 7 và 1 trade seed — nên trọng số tập
  trung bất thường của binance XAU (1d = 0,4311, ngân sách entry 0,1437) **có thể là
  TRIỆU CHỨNG** của seed gần rỗng chứ không phải nguyên nhân độc lập. **Một snapshot
  vẫn không giải được chiều đó.**
  **GIỚI HẠN:** chưa chứng minh cơ chế nào **GÂY RA** số trade trọn đời thấp — ba
  mẫu mỗi route, và các route khoẻ kích hoạt cùng gate; r264 đã cho thấy cả sáu
  route ra quyết định **cùng nhịp**, r261 cho thấy chênh lệch rate live là **nhiễu**.
  Chưa chứng minh trọng số tập trung là nguyên nhân chứ không phải triệu chứng.
  **KHÔNG** claim `trend_score` không bao giờ đổi — nó **không thể** đổi nhanh hơn 1h
  **do cấu hình**, còn thực tế nó đổi bao lâu một lần qua nhiều giờ/ngày thì **vẫn
  chưa đo**, và log mẫu là cách để biết. Không nói gì về PnL, Target 3, seed span hay
  backfill kẹt; r261-r266 đứng nguyên. File:
  `round267-the-role-split-is-configuration-and-the-entry-threshold-is-severe.md`.

- **Round 268 (2026-08-29) — DỮ LIỆU của `binance XAU` CHO PHÉP GIAO DỊCH NHIỀU HƠN
  route khoẻ, KHÔNG PHẢI ít hơn: thiếu hụt nằm ở PHÍA POLICY, không phải phía dữ
  liệu. Hai container (đúng hạn mức).** Giải quyết đúng cái chân của confound
  r263-r267 mà **backtest LÀM ĐƯỢC** và chưa ai hỏi: **hoạt động thấp của
  `binance XAU` là tính chất của DỮ LIỆU THỊ TRƯỜNG hay của POLICY/SEED đang triển
  khai?** Alpha sweep là công cụ đúng vì nó **ĐỘC LẬP VỚI POLICY** — nó chấm từng
  candidate trên ledger riêng, **không** dùng `interval_weights`, `strategy_weights`,
  `minimum_role_score` hay gate dấu — nên nó đo **thứ chuỗi giá có thể nuôi được**,
  với lớp Portfolio **bị gỡ bỏ hoàn toàn**. Cửa sổ khớp nhau **260 ngày** (giới hạn
  bởi lịch sử binance XAU từ 2025-12-11), cùng interval, cùng bộ candidate, chi phí
  production.
  **KẾT QUẢ — DỮ LIỆU CỦA ROUTE "NGỦ ĐÔNG" LẠI LÀ BÊN NĂNG ĐỘNG HƠN:** binance XAU
  1559 nến (6,00/ngày, 24/7), 36 cơ chế, **trung vị 71,5 trade mỗi cơ chế**, p25/p75
  32/146, cao nhất `candle_momentum` 474, **1,92 trade/tuần**, **0,0459 trade MỖI
  NẾN**; exness XAU 1130 nến (4,35/ngày, đóng cuối tuần), 36 cơ chế, trung vị
  **39,0**, p25/p75 11/92, cao nhất 444, 1,05/tuần, **0,0345 mỗi nến**. **Tính theo
  mỗi nến, binance XAU NĂNG ĐỘNG HƠN 1,33 lần**, theo tuần **1,83 lần**; và thứ hạng
  candidate **gần như y hệt** trên cả hai (`candle_momentum` → `heikin_ashi_momentum`
  → `rsi` → `macd_trend` → `elder_ray`), tức cùng những cơ chế đó tìm thấy **cùng
  loại chất liệu** trên cả hai instrument.
  **ĐIỀU NÀY GIẢI QUYẾT: INSTRUMENT KHÔNG HỀ "ÍT SÓNG", VÀ DỮ LIỆU KHÔNG PHẢI
  NGUYÊN NHÂN.** Gỡ lớp Portfolio ra, chuỗi giá của chính binance XAU nuôi được
  **NHIỀU** hoạt động candidate hơn route đã tạo 395 trade live so với 8 của nó.
  r262-r267 đã **loại** cửa sổ replay, replay hoàn tất, độ sâu dữ liệu, tính liên
  tục, đồng bộ hoá và nhịp quyết định; **vòng này là vòng ĐẦU TIÊN LOẠI VÀO** —
  thiếu hụt nằm ở **PHÍA POLICY/SEED** (trọng số, gate, hoặc seed gần rỗng nuôi
  chúng), **không** ở dữ liệu thị trường. Nó **không** chọn giữa seed và trọng số;
  nó **gỡ nốt lựa chọn ngoài-policy cuối cùng**.
  **MỨC ĐỘ GIỮ NGUYÊN:** r264 hạ xuống **P3** vì chưa chứng minh được tác động live
  — cả sáu route dựng quyết định cùng nhịp, và chênh lệch close-rate live (1 so với
  3-4) nằm trong nhiễu Poisson. **Điều đó vẫn đúng** — vòng này **không** cho thấy
  tổn hại, nó cho thấy **khoảng trống tiềm năng (headroom) là có thật**. Nếu có
  thiếu hụt thì nó ở phía policy; còn **có thiếu hụt hay không thì vẫn chưa xác
  lập**.
  **GIỚI HẠN:** **KHÔNG** claim lớp Portfolio **NÊN** giao dịch nhiều hơn trên
  binance XAU — sweep đo **candidate Alpha riêng lẻ**, không phải quyết định
  Portfolio đã qua gate, và một gate khoẻ mạnh **có quyền chính đáng** loại bỏ phần
  lớn hoạt động candidate (hold 99,3-99,8% trên **MỌI** route, r265). Không claim
  kết quả 4h chuyển được sang interval production 5m — tỉ lệ **đáng lẽ** chuyển
  được nhưng **chưa đo**. Seed hay trọng số là nguyên nhân thì **không đổi** so với
  r263. **KHÔNG** claim binance XAU thiếu hụt Target 3 — một close live trong 46 giờ
  cho khoảng 95% là [0,09; 20,30]/tuần (r259), **không giải quyết được gì**. PnL
  không xem xét. File:
  `round268-binance-xau-data-is-more-active-not-less-so-the-shortfall-is-policy-side.md`.

- **Round 269 (2026-08-29) — XÁC MINH r268 Ở INTERVAL PRODUCTION 5m; và route có
  ngân sách entry CHẶT NHẤT lại là route DUY NHẤT quan sát được QUA GATE. Hai
  container (đúng hạn mức).** Xác minh đúng điều r268 tự nêu ("chưa claim kết quả
  4h chuyển được sang interval production 5m; tỉ lệ **đáng lẽ** chuyển được nhưng
  **chưa đo**"). Cùng phép so, cùng cửa sổ 260 ngày, **ở 5m** — interval mà
  production thực sự ra quyết định. binance XAU: **74 878 nến** (288/ngày), trung vị
  **3255,5** trade mỗi cơ chế, p25/p75 1714/8200, **0,04348 mỗi nến**, **87,65/tuần**;
  exness XAU: 50 063 nến (192,6/ngày), trung vị **1901,5**, p25/p75 457/5073,
  **0,03798 mỗi nến**, 51,19/tuần. **TỈ LỆ binance/exness ở 5m: 1,14x mỗi nến,
  1,71x mỗi tuần**; ở 4h (r268): 1,33x và 1,83x. **CÙNG CHIỀU, ĐỘ LỚN TƯƠNG TỰ** —
  kết luận r268 (dữ liệu binance XAU nuôi được **NHIỀU** hoạt động candidate hơn
  route khoẻ, nên thiếu hụt ở **phía policy** chứ không phải phía dữ liệu) **CHUYỂN
  ĐƯỢC sang interval production**. Một khác biệt cấu trúc ghi lại: ở 5m các cơ chế
  bận nhất của binance XAU là `taker_imbalance`/`taker_imbalance_fade`, **không**
  xuất hiện trong top 5 của exness XAU vì trường taker-volume có ở perpetual future
  mà không có ở CFD — ảnh hưởng phần đuôi, **không** ảnh hưởng trung vị dùng ở trên.
  **LOG LẤY MẪU VÀ MỘT PHẢN VÍ DỤ TÔI KHÔNG NGỜ TỚI:** mẫu thứ tư đã append;
  `research/quant/samples/signal-state-samples.csv` nay có **16 quan sát** (vòng
  265/266/267/269), trải **14:35Z → 15:55Z (~80 phút)**. `trend_score` **không đổi
  tới 4 chữ số trên cả bốn route qua cả bốn mẫu** (+0,1759 / −0,3476 / −0,5023 /
  −0,0693 suốt), nên cách đọc cấu trúc của r267 (TREND = 1h/2h/4h/12h/1d, 84-89%
  ngân sách nằm ở 4h/12h/1d) **tiếp tục đứng vững** trên cửa sổ gấp bốn lần ban đầu.
  **VÀ RỒI:** binance XAU ghi nhận **`gate_passed=TRUE`**, reason
  **`multi_timeframe_gate_passed`**, entry **−0,1079**, trend −0,3476 — trong khi
  binance BTC (`entry_trend_conflict`), bybit XAUT (`entry_trend_conflict`) và
  exness BTC (`trend_score_below_threshold`) đều hold. **BINANCE XAU — ROUTE CÓ 8
  TRADE TRỌN ĐỜI VÀ NGÂN SÁCH ENTRY CHẶT NHẤT — LÀ ROUTE DUY NHẤT QUAN SÁT ĐƯỢC QUA
  GATE TRONG TOÀN BỘ LOG 16 MẪU.** `entry_score` của nó đạt **−0,1079 = 75,1% ngân
  sách 0,1437**, vượt ngưỡng 0,1 mà r267 tính là cần **69,6%**, và **dấu khớp** với
  trend âm bị ghim của nó, nên **cả ba gate thông cùng lúc**. **ĐÂY LÀ PHẢN VÍ DỤ CỤ
  THỂ** với hướng mà r263 và r267 đang nghiêng về: ngân sách entry chặt làm việc qua
  gate **khó hơn**, nó **rõ ràng KHÔNG** làm việc đó **bất khả thi**, và trong mẫu
  nhỏ này **route bị ràng buộc nhất lại qua được còn ba route kia thì không**.
  **GIỚI HẠN:** **KHÔNG** claim binance XAU qua gate **thường xuyên hơn** các route
  khác — một lần qua trên bốn mẫu so với không lần nào trên bốn **KHÔNG phải** một
  phép so tỉ lệ; nó là **phản ví dụ** cho "bị chặn về cấu trúc", **không hơn**;
  r261 và r264 đều đã lập rằng chênh lệch live nằm **trong nhiễu**. **KHÔNG** claim
  ngân sách entry chặt là vô can — nó được chứng minh là **VƯỢT QUA ĐƯỢC**, không
  phải vô hại, còn việc nó có kéo tỉ lệ pass xuống qua nhiều mẫu hay không thì đúng
  là **thứ log này sinh ra để trả lời**. **KHÔNG** claim `trend_score` không bao giờ
  đổi — tám mươi phút, bốn route, và r267 cho thấy nó **không thể** đổi nhanh hơn
  một lần đóng nến 1h **do cấu hình**. Seed hay trọng số là nguyên nhân thì **không
  đổi** từ r263. Không nói gì về PnL, Target 3, seed span hay backfill kẹt. File:
  `round269-5m-confirms-268-and-the-tightest-route-is-the-only-one-observed-to-pass.md`.

- **Round 270 (2026-08-29) — BẤT ĐỐI XỨNG CỦA GATE là THẬT về THIẾT KẾ nhưng KHÔNG
  ràng buộc trong thực tế; và `gate_passed` KHÔNG PHẢI một trade — điều này đẩy nghi
  ngờ XUỐNG HẠ NGUỒN. KHÔNG CONTAINER.**
  **BẤT ĐỐI XỨNG, lần đầu được phát biểu cho đúng:** r267 tính mức khắc nghiệt của
  ngưỡng entry từng route nhưng **chưa bao giờ gọi tên nguyên nhân**:
  `minimum_role_score` là **MỘT SỐ TUYỆT ĐỐI DUY NHẤT** so với **CẢ HAI** role,
  trong khi hai role có **ngân sách trọng số RẤT KHÔNG BẰNG NHAU** — `entry_score`
  không bao giờ vượt được ngân sách entry, `trend_score` không vượt được ngân sách
  trend. binance XAU: entry 0,1437 (ngưỡng = **69,6%**) so với trend 0,8564
  (**11,7%**) → **6,0x**; bybit XAUT 0,2933 (34,1%) vs 0,7068 (14,1%) → 2,4x;
  exness XAU 0,2523 (39,6%) vs 0,7475 (13,4%) → 3,0x. **CÙNG MỘT NGƯỠNG NHƯNG KHẮC
  NGHIỆT VỚI ENTRY GẤP 2,4-6 LẦN SO VỚI TREND, DO CẤU TẠO.**
  **NHƯNG NÓ KHÔNG RÀNG BUỘC THEO CÁCH ĐÓ:** trên toàn bộ **20 mẫu** hiện có trong
  `research/quant/samples/signal-state-samples.csv` (vòng 265/266/267/269/270),
  **|entry| dưới ngưỡng ở 6/20 = 30%** mẫu còn **|trend| dưới ngưỡng ở 5/20 = 25%**
  — **gần như bằng nhau**, bất chấp bất đối xứng thiết kế 2,4-6x. `entry_score` rõ
  ràng dùng **phần lớn** ngân sách nhỏ của nó một cách thường xuyên, còn
  `trend_score` chỉ dùng **một phần nhỏ** ngân sách lớn của nó, và hai bên rơi vào
  **cùng cỡ độ lớn tuyệt đối**. **BẤT ĐỐI XỨNG THIẾT KẾ LÀ THẬT; BẤT ĐỐI XỨNG RÀNG
  BUỘC MÀ NÓ TIÊN ĐOÁN THÌ KHÔNG QUAN SÁT ĐƯỢC** — đây là **lần thứ hai trong ba
  vòng** (r269 là lần đầu) một lập luận cấu trúc về ngân sách entry **không sống sót
  khi chạm vào dữ liệu mẫu**.
  **ĐÍNH CHÍNH QUAN TRỌNG: `gate_passed` KHÔNG PHẢI MỘT TRADE.** binance XAU nay có
  **2 lần pass trên 5 mẫu** — **tỉ lệ quan sát cao nhất trong log** — trong khi chỉ
  tạo **1 close trên 571 quyết định (0,18%)** ở cửa sổ live (r264/r265). Hai con số
  đó **không thể** cùng mô tả một đại lượng, và chúng **không** phải: `gate_passed`
  đánh dấu **một quyết định có lập trường hướng**, còn một **close** đòi
  `portfolio_construction.construct()` phải hành động, chịu ràng buộc
  `minimum_hold_decisions` (36 ≈ 3h) và **vị thế đang mở**, rồi mới thoát qua
  stop/take/flat. Nên một lần pass khi **đã có vị thế cùng chiều** tạo ra **KHÔNG
  trade mới** và không close. **TỈ LỆ PASS VÀ TỈ LỆ CLOSE LÀ HAI ĐẠI LƯỢNG KHÁC
  NHAU, VÀ TÔI ĐÃ ĐỐI XỬ VỚI CHÚNG NHƯ SO SÁNH ĐƯỢC SUỐT r265-r269.** Hệ quả là một
  bước **thu hẹp thật**: gate của binance XAU **CÓ** pass, ít nhất là đôi khi — nên
  số close thấp của nó nằm **HẠ NGUỒN SO VỚI GATE** (ở dựng vị thế, hold guard, hoặc
  điều kiện thoát), **không** phải tại chính gate. **Đây là lần đầu tiên** mạch này
  định vị được phần mất mát ở **hạ nguồn** thay vì tại hoặc trước `decide()`.
  Đếm theo route (n=5 mỗi route): binance BTC 1 entry-dưới / 1 trend-dưới / 0 pass;
  binance XAU 3/0/**2**; bybit XAUT 0/0/0; exness BTC 2/4/1.
  **GIỚI HẠN:** **KHÔNG** claim binance XAU pass thường xuyên hơn các route khác —
  2/5 so với 0/5 là **chênh nhau bốn mẫu**, và r261/r264 đã lập rằng chênh lệch live
  nằm **trong nhiễu**; không có gì ở đây lật lại điều đó. **KHÔNG** claim bất đối
  xứng thiết kế là vô hại — nó chỉ được chứng minh là **không tạo ra** bất đối xứng
  ràng buộc quan sát được **trong 20 mẫu**, một mẫu nhỏ và trong **một ngày**.
  **KHÔNG** claim phần mất mát chắc chắn ở hạ nguồn — thứ được xác lập là gate
  **không phải một rào chặn TOÀN PHẦN**; mất bao nhiêu tại gate so với sau gate thì
  **chưa đo**. Seed hay trọng số là nguyên nhân thì **không đổi** từ r263. Không nói
  gì về PnL hay Target 3. File:
  `round270-the-gate-asymmetry-is-real-in-design-but-does-not-bind-and-passes-are-not-trades.md`.

- **Round 271 (2026-08-29) — KHÔNG có counter kết quả nào tồn tại, nhưng `position`
  của ledger thì có: **4/5 route ĐANG GIỮ VỊ THẾ MỞ**, và có một **hold reason THỨ
  TƯ** mà cách khung của tôi trước đó đã bỏ sót. KHÔNG CONTAINER.**
  Trả lời câu hỏi kết của r270 ("mất bao nhiêu tại gate so với sau gate thì **chưa
  đo**") bằng cách **liệt kê trước xem thứ gì thực sự đếm được**. **TOÀN BỘ tập
  metric portfolio** trên một worker live: `portfolio_decisions_total` **599**,
  `evidence_intervals_complete/required` 8/8,
  `portfolio_last_primary_close_timestamp_seconds`, `portfolio_pending_boundaries` 0,
  `portfolio_replay_scopes_completed/expected` 3/3, `layer_evaluations_total` 599.
  **KHÔNG có counter nào cho gate pass, vị thế mở ra, hay trade** — nên phép tách
  gate/hạ-nguồn **cũng KHÔNG đo được từ metrics**, đúng cùng loại khoảng trống r265
  ghi cho hold reason. (`decisions_total` đã tăng 571 → 599 kể từ r264, khoảng
  **12/giờ**, khớp interval quyết định 5m — vòng lặp chạy bình thường.)
  **THỨ QUAN SÁT ĐƯỢC: trường `position` của ledger `paper-fixed-pct` đang triển
  khai.** Lấy mẫu ngay bây giờ: binance BTC **MỞ long** (479 trọn đời, gate false
  `entry_score_below_threshold`); **BINANCE XAU MỞ SHORT** (**8** trọn đời, gate
  **TRUE** `multi_timeframe_gate_passed`); bybit XAUT **flat** (3, gate false
  `entry_trend_conflict`); exness BTC **MỞ short** (485, gate true); exness XAU **MỞ
  short** (395, gate false **`stale_timeframe_evidence:15m`**).
  **BỐN TRÊN NĂM ROUTE ĐANG GIỮ VỊ THẾ MỞ NGAY LÚC NÀY, KỂ CẢ BINANCE XAU** — route
  có 8 trade trọn đời; nó đang **short**, và gate của nó **pass** trong cùng quan
  sát. **ĐIỀU NÀY ĐẶT LẠI KHUNG cho toàn bộ cách đọc "ngủ đông":** tỉ lệ hold ~99,5%
  **KHÔNG** có nghĩa hệ thống **đứng ngoài thị trường**, mà nghĩa là nó **ĐANG GIỮ
  những vị thế đã có**; close hiếm vì **vị thế được giữ** (`minimum_hold_decisions`
  = 36 ≈ 3h, thoát cần chạm dải stop/take hoặc tín hiệu flat). binance XAU **đang
  tham gia thị trường** với một lệnh short mở — điều này **củng cố thêm** việc r264
  hạ cấp xuống **P3**: route **không hề nhàn rỗi**.
  **MỘT HOLD REASON THỨ TƯ, MÀ KHUNG TRƯỚC CỦA TÔI ĐÃ BỎ SÓT:** exness XAU hiện
  **`stale_timeframe_evidence:15m`** — một reason **KHÔNG thuộc ba gate** trong
  `decide()` (`trading_modes.rs:851/854/857`); nó đến từ kiểm tra
  `synchronization_failure()` chạy **TRƯỚC** chúng. r265 thiết kế "phép test ba
  nhánh" và r265-r270 đều lập luận như thể **chỉ có ba** đường hold. **CÓ ÍT NHẤT
  BỐN**, và đường đồng bộ hoá là đường **được đánh giá đầu tiên**. Với exness XAU nó
  cũng là đường **đúng như dự kiến**: CFD vàng đóng cửa cuối tuần nên bằng chứng 15m
  cũ — chính là phần đóng cửa cuối tuần r259 đã verify **không phải lỗi**. Log
  append-only mới: **`research/quant/samples/position-state-samples.csv`**.
  **GIỚI HẠN:** phép tách **gate so với hạ nguồn VẪN CHƯA ĐO ĐƯỢC** — vòng này chỉ
  cho thấy metrics **không** cung cấp được nó và position state là **thay thế MỘT
  PHẦN**, không phải câu trả lời. **KHÔNG** claim lệnh short của binance XAU là đại
  diện — **MỘT quan sát**; nó cho thấy route không nhàn rỗi và **không** nói gì về
  tỉ lệ thời gian nó giữ trạng thái mở. **KHÔNG** claim việc giữ vị thế **GIẢI
  THÍCH** số close thấp — nó **nhất quán** với điều đó và là cách đọc hiển nhiên,
  nhưng **thời lượng** vị thế theo route **chưa đo**. **KHÔNG** claim bốn là tổng số
  hold reason, vì tôi **vừa mới sai** khi cho rằng có ba. Không nói gì về PnL hay
  Target 3. File:
  `round271-four-of-five-routes-hold-open-positions-and-a-fourth-hold-reason-exists.md`.

- **Round 272 (2026-08-29) — OCCUPANCY KHÔNG PHẢI VẤN ĐỀ: `binance XAU` ở trong thị
  trường NHIỀU HƠN route khoẻ nhất. Toàn bộ khác biệt nằm ở THỜI LƯỢNG GIỮ LỆNH.
  KHÔNG CONTAINER.** Đóng khoảng trống r271 nêu ("thời lượng vị thế theo route
  **chưa đo**") — đại lượng quyết định một tỉ lệ close thấp nghĩa là hệ thống **nhàn
  rỗi** hay chỉ đang **giữ lệnh**. Nó phân rã **chính xác**:
  `closes/tuần = occupancy × 168h / mean_hold_hours`. Tính từ lịch sử trade
  `paper-backtest-fixed-pct` giữ lại của từng route, **đẳng thức tái tạo đúng tỉ lệ
  quan sát tới hai chữ số thập phân trên CẢ BỐN ROUTE** — tức phân rã này được
  **kiểm chứng**, không phải giả định.
  | route | n | span | **occupancy** | **mean hold** | closes/tuần |
  |---|---|---|---|---|---|
  | binance BTC | 473 | 362n | **59,6%** | **10,96h** | 9,14 |
  | **binance XAU** | **7** | **14n** | **63,5%** | **29,98h** | **3,56** |
  | bybit XAUT | **1** | **1n** | 100% | 32,92h | 5,10 |
  | exness XAU | 392 | 361n | 86,7% | 19,17h | 7,60 |
  **OCCUPANCY BỊ LOẠI:** `binance XAU` giữ vị thế **63,5%** thời gian — **NHIỀU HƠN**
  `binance BTC` (59,6%), route **khoẻ nhất** đội. Nó **không** nhàn rỗi, **không**
  đứng ngoài thị trường, và số trade trọn đời thấp của nó **KHÔNG** phải vấn đề về
  mức tham gia. Cộng với ảnh chụp r271 (4/5 route đang giữ vị thế mở, có binance
  XAU), cách đọc "route ngủ đông" nay **bị phản bác từ HAI hướng độc lập**.
  **TOÀN BỘ KHÁC BIỆT NẰM Ở THỜI LƯỢNG GIỮ:** mean hold của binance XAU là **29,98h
  so với 10,96h** của binance BTC = **dài gấp 2,74 lần**, **CÙNG broker**, **CÙNG**
  dải bảo vệ. Thoát lệnh là stop (1%), take (2%) hoặc flat — nên giữ lâu hơn nghĩa
  là giá **mất nhiều thời gian hơn để đi cùng một quãng TỈ LỆ**. Đó chính là cơ chế
  P1 của r261, thứ ở đó mới chỉ "xác nhận một phần, yếu hơn dự đoán" (1,37x so với
  dự đoán 2,39x); **ở đây nó khớp TỐT HƠN NHIỀU** — vàng so với BTC là tương phản
  biến động khoảng **2,4x** (vol dải r258 ~0,43% vs ~1,0% mỗi 4h) so với tỉ lệ hold
  **2,74x** quan sát được; và phép so của r261 bị nhiễu bởi việc exness XAU đóng cửa
  cuối tuần, còn phép so này **nằm trong CÙNG MỘT BROKER**. Vậy hiệu ứng đã được
  định vị: **HẠ NGUỒN SO VỚI GATE, ở THỜI ĐIỂM THOÁT LỆNH** — đúng nơi r270 nghi ngờ
  nhưng chưa xác nhận được.
  **CẢNH BÁO VỀ CỠ MẪU, ở đây KHÔNG phải một dòng chú thích:** số liệu binance XAU
  đến từ **BẢY trade trong MƯỜI BỐN ngày** và bybit XAUT từ **MỘT trade** trong một
  ngày; đó chính là hai route mà **toàn bộ câu hỏi này nói về**, và chúng **gần như
  không có trọng số thống kê nào**. Các con số occupancy và hold ở trên là **sự thật
  số học về 7 và 1 trade đó**, **không phải** ước lượng hành vi của route. Phép so
  **duy nhất có mẫu tử tế** là binance BTC (473) so với exness XAU (392): occupancy
  59,6% vs 86,7%, hold 10,96h vs 19,17h — **cả hai đòn bẩy đều dịch chuyển và chúng
  bù trừ một phần**, cho ra 9,14 so với 7,60 close/tuần.
  **GIỚI HẠN:** **KHÔNG** claim binance XAU **thường** giữ 63,5% thời gian hay 29,98h
  mỗi trade — điều này loại occupancy như lời giải **CHO BẢY TRADE ĐÓ**, không phải
  một mô tả về route; **không** claim gì về bybit XAUT trên một trade; **KHÔNG**
  claim biến động giải thích tỉ lệ hold — 2,74x so với tương phản ~2,4x là **gợi ý**
  và **chưa được test**, và r261 đã làm đúng kiểu so sánh này rồi thấy nó yếu hơn dự
  đoán; **KHÔNG** claim giữ lệnh lâu là một lỗi — một instrument ít biến động hơn
  chạm dải tỉ lệ cố định chậm hơn là hành vi **đúng như mong đợi**, còn việc dải
  **có nên** co giãn theo biến động hay không là câu hỏi riêng mà r81-r82 đã đóng
  trên cơ sở cross-broker **cho PnL, chưa bao giờ cho tần suất**. Không nói gì về PnL
  hay Target 3. File:
  `round272-occupancy-is-fine-the-whole-difference-is-hold-duration.md`.

- **Round 273 (2026-08-30) — THỜI LƯỢNG GIỮ LỆNH TỈ LỆ VỚI 1/σ², ĐÚNG như một dải
  tỉ lệ cố định tiên đoán. ĐIỀU NÀY ĐÓNG câu hỏi "route ngủ đông". KHÔNG CONTAINER.**
  Test đúng điều r272 để ngỏ, áp dụng **chính quy tắc r255**: đo một biến trên **MỌI
  đơn vị có được**, không phải trên hai đơn vị mà phép so hiện tại tình cờ sinh ra.
  **DỰ ĐOÁN KHÔNG PHẢI `hold ~ 1/σ`:** thoát lệnh là dải **TỈ LỆ CỐ ĐỊNH** (stop 1%,
  take 2%), và thời gian chạm biên lần đầu của một bước ngẫu nhiên tỉ lệ với
  `(d/σ)²` — nên dự đoán là **`hold ~ 1/σ²`**, tức **độ dốc −2** trong log-log (nếu
  drift chi phối thì −1). Vol log-return 5m từng route từ 2026-02-01 so với mean hold:
  | route | n | mean hold | vol 5m | **hold × σ²** |
  |---|---|---|---|---|
  | exness BTC | 481 | 10,89h | 0,14218% | **0,2201** |
  | binance BTC | 473 | 10,96h | 0,14371% | **0,2263** |
  | exness XAU | 392 | 19,17h | 0,11212% | **0,2410** |
  | bybit BTC | 311 | 12,14h | 0,14406% | **0,2520** |
  | binance XAU | **7** | 29,98h | 0,09058% | **0,2459** |
  | bybit XAUT | **1** | 32,92h | 0,08812% | **0,2556** |
  **KẾT QUẢ:** trên **bốn route có mẫu tử tế** (n=311-481), `log(hold)` so với
  `log(σ)` cho **Pearson r = −0,9756** và **độ dốc −2,130** so với lý thuyết **−2**.
  Và **`hold × σ²` gần như HẰNG SỐ trên cả sáu route**: 0,2201 → 0,2556 — biên độ
  **16%** qua **hai lớp tài sản, ba broker, và số trade từ 1 tới 481** — trong khi
  `hold × σ` trải **87%** trên cùng tập, nên **luỹ thừa BÌNH PHƯƠNG mới là đúng**.
  Hai route mẫu cực nhỏ rơi **BÊN TRONG** cùng dải hẹp đó.
  **ĐIỀU NÀY ĐÓNG:** câu hỏi "route ngủ đông" chạy từ r261 **đã có lời giải** —
  binance XAU và bybit XAUT giao dịch thưa hơn vì chúng là **hai instrument ÍT BIẾN
  ĐỘNG NHẤT đội** (0,091% và 0,088% so với ~0,143% của BTC), và một dải thoát tỉ lệ
  cố định mất **~2,5 lần lâu hơn** để chạm ở mức biến động **~0,63 lần**. **KHÔNG
  CẦN bất kỳ lỗi nào để giải thích.** Cộng với r271 (4/5 route đang giữ vị thế mở) và
  r272 (occupancy 63,5%, **CAO HƠN** route khoẻ nhất), bức tranh đã đủ: **các route
  đó THAM GIA ĐẦY ĐỦ, chỉ là thoát lệnh lâu hơn — hệ quả cơ học của việc dải được cố
  định theo TỈ LỆ GIÁ.** Điều này cũng **rút lui confound seed↔trọng số VỚI TƯ CÁCH
  lời giải cho tần suất giao dịch**; nó **KHÔNG** rút lui quan sát seeding của r262,
  thứ vẫn là một **P3 riêng**.
  **MỘT HỆ QUẢ ĐÁNG NÊU, KHÔNG PHẢI ĐỀ XUẤT:** nếu Target 3 (≥7/tuần) áp **theo từng
  route** thì dưới một dải tỉ lệ cố định, tần suất của route **phần lớn do biến động
  của nó quyết định** — nên instrument ít biến động sẽ **hụt về mặt cấu trúc**.
  r81-r82 đã test dải bảo vệ co giãn theo ATR và **bác bỏ trên cơ sở PnL
  cross-broker**; **bác bỏ đó VẪN ĐỨNG và không được mở lại ở đây** — nhưng cùng đòn
  bẩy đó xét như một câu hỏi **TẦN SUẤT** thì **chưa bao giờ được xem xét**. Chỉ nêu.
  **GIỚI HẠN:** **MỘT ĐỊNH LUẬT TỪ BỐN ĐIỂM** — hồi quy dựa trên bốn route có mẫu
  tử tế, **ba trong số đó là BTC** và cụm chặt về biến động, nên **exness XAU gánh
  phần lớn đòn bẩy**; bốn điểm với một quan sát ảnh hưởng lớn **KHÔNG phải** một
  scaling law đã kiểm chứng. binance XAU và bybit XAUT **KHÔNG** xác nhận nó (n=7 và
  n=1) — chúng chỉ **nhất quán với** dải đó, dạng ủng hộ **yếu nhất**. Cửa sổ đo biến
  động (từ 2026-02-01) **không trùng** khoảng trade của từng ledger và **chưa** chạy
  kiểm tra độ nhạy. Mô hình bước ngẫu nhiên **chưa được xác lập**: −2,13 gần −2 nhưng
  lợi suất thật **không** driftless cũng **không** độc lập, và **chưa** đối chiếu với
  mô hình thay thế. Không nói gì về PnL, hay việc dải ATR có giúp tần suất hay không.
  File:
  `round273-hold-duration-scales-as-one-over-volatility-squared-which-closes-the-dormant-route-question.md`.

- **Round 274 (2026-08-30) — DẢI ATR CÓ nâng được tần suất (2,43x), và mua nó bằng
  2,27x mức lỗ vì kinh tế mỗi trade KHÔNG ĐỔI. BÁC BỎ. Hai container (đúng hạn
  mức).** Trả lời câu hỏi r273 nêu: r273 đóng mạch "route ngủ đông" bằng định luật
  `hold ~ 1/σ²` và ghi rằng dưới dải **tỉ lệ cố định**, tần suất của route phần lớn
  do biến động quyết định, nên instrument ít biến động **hụt về cấu trúc** với
  Target 3; r81-r82 bác dải ATR **trên cơ sở PnL cross-broker**, còn cùng đòn bẩy
  xét như câu hỏi **TẦN SUẤT** thì chưa từng được xem xét. **A/B có đối chứng** trên
  `exness XAU/USD`, 5m, 360 ngày, `minimum_hold_decisions=36`, **giống hệt nhau ở
  mọi mặt trừ dải bảo vệ**, đọc từ **`one_target`** — phép đo Portfolio trung thực
  duy nhất (r82).
  | dải | trades | **/tuần** | realized_pnl | **pnl/trade** |
  |---|---|---|---|---|
  | fractional 0,01/0,02 (đang triển khai) | 363 | **7,06** | −2,5832 | **−0,00712** |
  | ATR 1,5x/3,0x, 14 chu kỳ | 883 | **17,17** | −5,8573 | **−0,00663** |
  **KẾT QUẢ — NÓ CHẠY ĐƯỢC, VÀ CHÍNH VÌ THẾ NÓ VÔ DỤNG:** tần suất **2,43x** (7,06 →
  17,17/tuần, vượt xa vạch 7/tuần); lỗ **2,27x** (−2,58 → −5,86); **mỗi trade 0,93x
  — về cơ bản KHÔNG ĐỔI** (−0,00712 → −0,00663). **Dải ATR nâng tần suất CHỈ bằng
  cách nhận thêm nhiều hơn CHÍNH những trade thua đó.** Hằng số mỗi trade nằm ở
  −0,0071 và −0,0066, **kẹp lấy** con số −0,0068 lâu đời mà r234 và r96 đã lập, và
  tổng lỗ **bám sát số trade gần như chính xác** (2,43x trade, 2,27x lỗ). Đây là kết
  quả đứng lâu nay được **tái hiện dưới dạng một THÍ NGHIỆM CÓ ĐỐI CHỨNG**: **lỗ ≈
  số trade × một hằng số gần cố định, và KHÔNG đòn bẩy Portfolio-construction nào
  dịch chuyển được hằng số đó.** r80 và r83 cải thiện Target 1 **chính vì chúng GIẢM
  số trade**; đòn bẩy này làm điều ngược lại và **trả giá tương ứng**. Câu hỏi r273
  nêu vì thế **đã trả lời và ĐÓNG**: ATR là một đòn bẩy tần suất **có tác dụng** và
  là **một thương vụ lỗ**, đồng thời **củng cố** bác bỏ r81-r82 **từ một hướng độc
  lập**.
  **MỘT CON SỐ VẬN HÀNH ĐÁNG GHI:** cấu hình fractional đang triển khai cho **7,06
  trade/tuần** trên exness XAU qua 360 ngày từ `one_target`. Vạch Target 3 là
  7/tuần. **BIÊN CHỈ 0,9%** — **mỏng hơn** ước lượng ~7,2-7,3/tuần của r92, và đây là
  phép đo **có thẩm quyền hơn** (`one_target`, 360 ngày, tham số đang triển khai).
  **GIỚI HẠN:** đây **KHÔNG** phải phép so ATR với fractional ở **BỀ RỘNG DẢI KHỚP
  NHAU** — 1,5x/3,0x ATR rõ ràng là dải **HẸP HƠN** 1%/2% trên instrument này, và đó
  chính là lý do tần suất tăng; một hệ số lớn hơn sẽ về gần mức fractional. Thứ
  **sống sót qua mọi cách hiệu chỉnh** là hằng số mỗi trade, tức **tần suất mua bằng
  cách nới hay thu dải đều được trả giá TƯƠNG ỨNG** — và đó mới là phát hiện.
  **KHÔNG** claim ATR hành xử như vậy trên route khác — **MỘT instrument**, và
  r81-r82 từng thấy tác dụng PnL của ATR **ĐẢO CHIỀU** giữa Binance và Exness nên
  hành vi cross-broker **đặc biệt không được giả định**. **KHÔNG** claim 7,06/tuần là
  rate **live** — đó là backtest 360 ngày dưới tham số triển khai, còn cửa sổ live
  r259 vẫn chưa giải quyết được Target 3. Hệ số/chu kỳ ATR được chọn để **giữ nguyên
  tỉ lệ stop/take 1:2** đang triển khai, **không phải đã tinh chỉnh** — và tinh chỉnh
  chúng để tối đa tần suất **chỉ làm lỗ to hơn**. File:
  `round274-atr-band-buys-frequency-at-exactly-proportional-loss-so-it-is-rejected.md`.

- **Round 275 (2026-08-30) — TARGET 3 TRƯỢT VỀ MẶT CẤU TRÚC trên route ít biến động
  nhất (3,63/tuần), và định luật σ² của r273 được XÁC NHẬN bằng một dự đoán ĐĂNG KÝ
  TRƯỚC, sai số 2,8%. Hai container (đúng hạn mức).**
  **DỰ ĐOÁN ĐĂNG KÝ TRƯỚC KHI CHẠY:** định luật σ² của r273 dựa trên bốn điểm và tôi
  đã nói rõ điều đó; vòng này test nó **đúng cách** — **dự đoán được ghi ra đĩa
  TRƯỚC khi khởi động bất kỳ container nào** (`precommit_r275.md`): tần suất ~ σ²,
  vol 5m đo được là binance BTC 0,14371% và binance XAU 0,09058%, nên tần suất
  `one_target` của binance XAU phải vào khoảng **(0,09058/0,14371)² = 0,397 lần**
  của binance BTC; **bác bỏ nếu tỉ lệ nằm ngoài 0,25-0,60**. Cửa sổ khớp 260 ngày,
  tham số đang triển khai (fractional 0,01/0,02, hold 36), đọc từ `one_target`.
  | route | trades | **/tuần** | realized_pnl | pnl/trade | **Target 3** |
  |---|---|---|---|---|---|
  | **binance XAU/USDT** | 135 | **3,63** | −1,4331 | −0,01062 | **TRƯỢT** |
  | binance BTC/USDT | 350 | **9,42** | −3,3986 | −0,00971 | ĐẠT |
  **DỰ ĐOÁN 0,397; QUAN SÁT 0,386 — sai số 2,8%.** Đây là **xác nhận ngoài mẫu** cho
  định luật σ² trên **một phép đo ĐỘC LẬP** (tần suất `one_target` mức Portfolio,
  không phải thời lượng hold của ledger mà định luật được khớp lên); điểm yếu chính
  của r273 ("một định luật từ bốn điểm") **được trả lời phần lớn**.
  **PHÁT HIỆN VẬN HÀNH: HAI TARGET XUNG ĐỘT VỀ MẶT CƠ HỌC.** Tần suất `one_target`
  có thẩm quyền dưới tham số triển khai: binance BTC **9,42/tuần** đạt thoải mái;
  exness XAU **7,06/tuần** (r274) đạt với biên **0,9%**; **binance XAU 3,63/tuần
  TRƯỢT 48%**. Và **lối thoát đã bị đóng**: r274 cho thấy thu hẹp dải nâng tần suất
  **2,43x** trong khi nhân lỗ lên **2,27x**, vì chi phí mỗi trade **không đổi** —
  nên trên binance XAU, đạt 7/tuần nghĩa là **gấp đôi số trade và gấp đôi mức lỗ**.
  **TARGET 1 (lợi nhuận / không lỗ kéo dài) VÀ TARGET 3 (≥7 trade/tuần) ĐỐI NGHỊCH
  TRỰC TIẾP trên instrument ít biến động**, và sự đối nghịch mang tính **CƠ HỌC**:
  tần suất tỉ lệ với σ², chi phí mỗi trade **không** tỉ lệ với gì cả, nên tần suất
  **chỉ mua được bằng lỗ tương ứng**. Trên binance XAU, **bộ target NHƯ ĐANG ĐẶC TẢ
  là KHÔNG THOẢ MÃN ĐỒNG THỜI ĐƯỢC**. Đây **không** phải lỗi cần sửa — đây là **XUNG
  ĐỘT ĐẶC TẢ**, nay **có đo đạc làm nền** thay vì chỉ lập luận.
  **MỘT ĐÍNH CHÍNH CHO "HẰNG SỐ GẦN CỐ ĐỊNH":** chi phí mỗi trade qua bốn phép đo
  `one_target` hiện có là −0,00663, −0,00712 (exness XAU, r274), −0,00971 (binance
  BTC), −0,01062 (binance XAU) — **biên độ 1,6 lần**, **rộng hơn** con số "±14%" các
  vòng trước báo cáo. Những con số trước đó là **TRONG MỘT INSTRUMENT qua nhiều cấu
  hình**; **qua nhiều instrument thì hằng số này KÉM cố định hơn rõ rệt**, và **tôi
  đã trích dẫn con số chặt hơn trong những ngữ cảnh trải qua nhiều instrument**. Kết
  quả định tính **không đổi** (chi phí mỗi trade **không giảm** khi tần suất tăng)
  nhưng "hằng số gần cố định −0,0068" nên đọc là **"−0,0066 tới −0,0106 tuỳ route"**.
  **GIỚI HẠN:** **KHÔNG** claim binance XAU trượt Target 3 **trong production** —
  đây là backtest 260 ngày, còn cửa sổ live r259 cho [0,09; 20,30]/tuần và **không
  giải quyết được gì**. **KHÔNG** claim định luật σ² đúng tổng quát — một dự đoán
  đăng ký trước trên **một cặp**, cộng bốn điểm khớp của r273, và **cặp này được
  chọn CỐ Ý cách xa nhau về biến động** nên đây là **phép test thuận lợi**. **KHÔNG**
  claim không đòn bẩy nào khác nâng được tần suất mà không mất lỗ tương ứng — mới
  chỉ test **dải bảo vệ** (r274) và **chỉ trên một instrument**. **KHÔNG** claim bộ
  target nên thay đổi — **đó là quyết định của user**, không phải đầu ra nghiên cứu,
  và **không** khuyến nghị nào được đưa ra ở đây. Chưa đo `bybit XAUT`, `exness BTC`
  hay `bybit BTC` dưới `one_target`. File:
  `round275-target3-fails-structurally-on-the-least-volatile-route-and-the-sigma-squared-law-is-confirmed-out-of-sample.md`.

- **Round 276 (2026-08-30) — QUALIFICATION: σ² chi phối THỜI LƯỢNG GIỮ, KHÔNG chi
  phối TẦN SUẤT Portfolio. `bybit BTC` chạy 5,55/tuần ở biến động Y HỆT và cũng
  TRƯỢT Target 3. Hai container (đúng hạn mức). Tiêu chí bác bỏ đăng ký trước ĐÃ KÍCH
  HOẠT.** r275 xác nhận định luật σ² nhưng **tự thừa nhận** phép test của nó
  **THUẬN LỢI** — cặp được chọn cách xa nhau về biến động nên σ² có tín hiệu lớn để
  dự đoán. Phiên bản **khắt khe** thì ngược lại, và đã ghi ra đĩa **trước khi khởi
  động container nào** (`precommit_r276.md`): vol 5m ba route BTC là 0,14218% /
  0,14371% / 0,14406% — **biên độ 1,3%**, nên σ² dự đoán tần suất chúng **nằm trong
  ~2,7% của nhau**; binance BTC đã đo 9,42/tuần; **DỰ ĐOÁN: cả hai route mới nằm
  trong 8,9-10,0/tuần**; **BÁC BỎ/GIỚI HẠN nếu route nào rơi ngoài 8,0-11,0**.
  | route | vol 5m | trades | **/tuần** | pnl/trade | Target 3 |
  |---|---|---|---|---|---|
  | exness BTC/USD | 0,14218% | 364 | **9,80** | −0,00996 | ĐẠT |
  | binance BTC/USDT | 0,14371% | 350 | 9,42 | −0,00971 | ĐẠT |
  | **bybit BTC/USDT** | 0,14406% | 206 | **5,55** | −0,01149 | **TRƯỢT** |
  **exness BTC rơi TRONG dải. bybit BTC rơi ở 5,55 — XA BÊN NGOÀI.** Biên độ tần
  suất **1,77 lần** so với biên độ biến động 1,013 lần (σ² dự đoán 1,027 lần).
  **TIÊU CHÍ TÔI ĐẶT RA ĐÃ KÍCH HOẠT. ĐỊNH LUẬT BỊ GIỚI HẠN: σ² KHÔNG phải toàn bộ
  câu chuyện cho tần suất Portfolio.**
  **HOÀ GIẢI — VÀ NÓ ĐÃ CÓ SẴN TRONG r272:** r272 lập đẳng thức
  `tần suất = occupancy × 168 / hold`. r273 rồi cho thấy σ² chi phối **HOLD**
  (hold × σ² hằng số tới 16% qua sáu route), và **r273/r275 đã LẶNG LẼ coi đó là chi
  phối TẦN SUẤT**. Nó **không** — vì **occupancy là số hạng thứ hai, ĐỘC LẬP**, và
  r272 đo nó dao động từ **59,6% tới 86,7%, biên độ 1,45 lần**. Nên bybit BTC có thể
  ở biến động y hệt, giữ lệnh đúng thời lượng σ² dự đoán, mà **vẫn giao dịch thưa
  hơn nhiều** nếu nó ở trong vị thế ít thời gian hơn. **Cú trúng 2,8% sạch sẽ của
  r275 một phần là MAY MẮN:** binance XAU (63,5%) và binance BTC (59,6%) **tình cờ có
  occupancy tương tự** nên số hạng occupancy gần như triệt tiêu. Nhất quán với điều
  này, bybit BTC **vốn đã là điểm khớp TỆ NHẤT** trong bảng r273 (hold × σ² = 0,2520
  so với 0,2263 của binance BTC, lệch 11%) **nhưng tần suất Portfolio của nó lệch tới
  77%** — nên yếu tố phụ tác động ở **TẦNG PORTFOLIO**, không phải ở thời điểm thoát
  lệnh. **TÔI CHƯA ĐO occupancy của bybit BTC**; hoà giải trên **bị ép về mặt số học**
  bởi đẳng thức nhưng số hạng cụ thể **CHƯA ĐƯỢC KIỂM CHỨNG**, và sau r252/r254/r261/
  r263 tôi **không** trình bày một lời giải vừa khớp như thể đã đo.
  **BỨC TRANH VẬN HÀNH CẬP NHẬT** (`one_target`, tham số triển khai, 260 ngày trừ khi
  ghi khác): exness BTC **9,80** đạt; binance BTC **9,42** đạt; exness XAU **7,06**
  (360n) đạt với biên **0,9%**; **bybit BTC 5,55 TRƯỢT**; **binance XAU 3,63 TRƯỢT**;
  bybit XAUT **chưa đo**. **HAI TRÊN NĂM route đã đo TRƯỢT Target 3, và một route
  nữa đạt với biên dưới 1%.** Điều này **phá vỡ cách đọc gọn gàng của r275** — thất
  bại **KHÔNG** giới hạn ở instrument ít biến động; **bybit BTC biến động ngang hai
  route BTC đạt chuẩn mà vẫn trượt**.
  **GIỚI HẠN:** **KHÔNG** claim occupancy giải thích bybit BTC — nó là số hạng tự do
  **duy nhất** trong một đẳng thức buộc phải cân, nhưng **CHƯA ĐO trên route đó**, và
  đó là **việc đầu tiên của vòng sau**. **Không** claim σ² sai về **thời lượng giữ**
  — bằng chứng r273 **vẫn đứng**; thứ bị giới hạn là **BƯỚC NHẢY TỪ HOLD SANG TẦN
  SUẤT** mà r273 và r275 đã thực hiện **mà không biện minh**. Không claim bybit BTC
  trượt Target 3 **trong production** (backtest 260 ngày). Chưa điều tra nguyên nhân
  nào cho khác biệt occupancy theo route. bybit XAUT vẫn chưa đo dưới `one_target`.
  File:
  `round276-QUALIFICATION-sigma-squared-governs-hold-not-frequency-and-bybit-btc-also-fails-target3.md`.

- **Round 277 (2026-08-30) — ĐÃ ĐO: occupancy của `bybit BTC` là 43,3%, THẤP NHẤT
  đội. TARGET 3 CÓ HAI NGUYÊN NHÂN KHÁC NHAU, không phải một. KHÔNG CONTAINER.**
  Làm đúng **việc đầu tiên r276 nêu tên** ("occupancy **chưa được đo** trên route đó;
  đó là việc đầu tiên của vòng sau"). Bảng occupancy của r272 chỉ phủ bốn route; hai
  route nó chưa từng đo lại **chính là hai route cần thiết**.
  | route | n | **occupancy** | mean hold | ledger /tuần |
  |---|---|---|---|---|
  | bybit XAUT | **1** | 100,0% | 32,92h | — |
  | exness XAU | 392 | 86,7% | 19,17h | 7,60 |
  | binance XAU | **7** | 63,5% | 29,98h | 3,56 |
  | exness BTC | 481 | **60,3%** | 10,89h | 9,30 |
  | binance BTC | 473 | **59,6%** | 10,96h | 9,14 |
  | **bybit BTC** | 311 | **43,3%** | 12,14h | 5,99 |
  **HOÀ GIẢI ĐƯỢC XÁC NHẬN:** ba route BTC có biến động gần y hệt và — **ĐÚNG NHƯ σ²
  ĐÒI HỎI** — có **thời lượng giữ gần y hệt: 10,89h / 10,96h / 12,14h**. Định luật
  σ² đang **làm đúng việc của nó** trên đại lượng nó thực sự chi phối. **THỨ KHÁC
  NHAU LÀ OCCUPANCY: 60,3%, 59,6%, và 43,3%** — bybit BTC nằm **flat** nhiều hơn hẳn.
  Kiểm lập luận r276 bằng đẳng thức `tần suất = occupancy × 168 / hold`: dự đoán tỉ
  lệ bybit/binance = (43,3/59,6) × (10,96/12,14) = **0,656** so với tỉ lệ `one_target`
  quan sát 5,55/9,42 = **0,589** — **lệch trong 10%**. r276 suy ra điều này từ đẳng
  thức và **ghi rõ là CHƯA ĐO**; nay **đã đo và nó đứng vững**. Hai phương pháp cũng
  **tự khớp độc lập**: bybit BTC 5,99 vs 5,55; exness BTC 9,30 vs 9,80; binance BTC
  9,14 vs 9,42 — **đều trong ~8%**, từ **hai cửa sổ và hai đường đo khác nhau**.
  **TARGET 3 CÓ HAI NGUYÊN NHÂN KHÁC NHAU:** `binance XAU` **3,63/tuần** trượt vì
  **GIỮ LỆNH LÂU** (biến động thấp nhất đội, cơ chế σ² của r273); `bybit BTC`
  **5,55/tuần** trượt vì **OCCUPANCY THẤP** (43,3% so với ~60% của hai route BTC anh
  em) **trong khi giữ lệnh với thời lượng hoàn toàn bình thường**. **ĐÂY LÀ HAI THẤT
  BẠI KHÁC NHAU** — r273-r275 đọc thiếu hụt Target 3 như **một câu chuyện biến động
  DUY NHẤT**, và **nó không phải vậy**. Hệ quả: kết luận r274/r275 rằng tần suất
  **chỉ mua được bằng lỗ tương ứng** mới chỉ được chứng minh **CHO ĐÒN BẨY THỜI
  LƯỢNG GIỮ** (dải bảo vệ); việc nâng **OCCUPANCY** có mang cùng cái giá tương ứng
  hay không thì **CHƯA ĐƯỢC TEST**, và đó là **một đòn bẩy KHÁC**.
  **GIỚI HẠN:** **KHÔNG BIẾT cái gì điều khiển occupancy** — nó dao động 43,3%-86,7%
  qua các route và **không** được biến động giải thích; vòng này **không** điều tra
  nguyên nhân và **không** đoán mò. **KHÔNG** claim nâng occupancy sẽ cải thiện
  Target 3 mà không trả giá PnL tương ứng — **chưa test**, và **vì chi phí mỗi trade
  không đổi trước mọi đòn bẩy đã thử, prior nên là BI QUAN**. **Không** claim gì từ
  hai dòng yếu: bybit XAUT (n=1) và binance XAU (n=7) có trong bảng **cho đủ**, con
  số occupancy của chúng **không có trọng số**. Không claim bybit BTC trượt Target 3
  **trong production** — chỉ có bằng chứng backtest và seed-ledger. File:
  `round277-occupancy-measured-bybit-btc-sits-flat-and-target3-has-two-distinct-causes.md`.

- **Round 278 (2026-08-30) — THỜI GIAN FLAT BỊ GHIM ĐÚNG TẠI HOLD GUARD ở hơn một
  nửa số lần vào lại; OCCUPANCY do ĐUÔI vượt qua ngưỡng đó quyết định. KHÔNG
  CONTAINER.** Phân rã câu hỏi mở của r277 ("**không biết** cái gì điều khiển
  occupancy") thêm một tầng. Occupancy **không phải đại lượng nguyên thuỷ**: vị thế
  chỉ có mở hoặc flat, nên `occupancy = hold / (hold + flat)`. `hold` **đã** được σ²
  giải thích (r273), nên đại lượng tự do là **THỜI GIAN FLAT** — và nó đo được **ĐỘC
  LẬP**, từ khoảng cách giữa `exit_at` của một trade và `entry_at` của trade kế tiếp,
  **không** phải bằng cách biến đổi đại số từ occupancy.
  | route | n | mean hold | mean flat | **occ TỪ flat** | **occ ĐO ĐƯỢC** | chồng lấn |
  |---|---|---|---|---|---|---|
  | binance BTC | 473 | 10,96h | 7,43h | **59,6%** | **59,6%** | 0 |
  | bybit BTC | 311 | 12,14h | **15,94h** | **43,2%** | **43,3%** | 0 |
  | exness BTC | 481 | 10,89h | 7,19h | **60,2%** | **60,3%** | 0 |
  | exness XAU | 392 | 19,17h | **2,96h** | **86,6%** | **86,7%** | 0 |
  Phép tính độc lập **tái tạo occupancy đo được sai lệch dưới 0,1 điểm phần trăm trên
  cả bốn route**, và **không vị thế nào chồng lấn** — phân rã được **kiểm chứng**,
  không phải giả định.
  **PHÁT HIỆN: THỜI GIAN FLAT CÓ MỘT SÀN CỨNG ĐÚNG TẠI HOLD GUARD.**
  `minimum_hold_decisions = 36` ở interval quyết định 5m là **36 × 5 = 180 phút =
  3,00h**. Trung vị flat:
  | route | **trung vị flat** | mean flat | **vào lại ĐÚNG SÀN (≤3,05h)** | **flat > 12h** | occupancy |
  |---|---|---|---|---|---|
  | exness XAU | **3,00h** | 2,96h | **64,7%** | **2,0%** | 86,7% |
  | binance BTC | **3,00h** | 7,43h | 52,5% | 15,5% | 59,6% |
  | exness BTC | **3,04h** | 7,19h | 50,0% | 13,5% | 60,3% |
  | **bybit BTC** | **4,29h** | 15,94h | **26,8%** | **27,7%** | 43,3% |
  **Trung vị flat là 3,00h trên hai route và 3,04h trên route thứ ba — ĐÚNG BẰNG hold
  guard.** Từ **một nửa tới hai phần ba** số lần vào lại xảy ra **đúng thời điểm sớm
  nhất mà guard cho phép**. Guard **không** phải một giới hạn an toàn hiếm khi chạm
  tới; nó là **ràng buộc CHÍNH của phần lớn các lần vào lại**. **Occupancy khi đó gần
  như hoàn toàn do ĐUÔI vượt sàn quyết định:** xếp các route theo "tỉ lệ đúng sàn"
  (64,7 / 52,5 / 50,0 / 26,8) hoặc nghịch theo "tỉ lệ chờ trên 12 giờ" (2,0 / 15,5 /
  13,5 / 27,7) thì **ra đúng thứ tự occupancy** (86,7 / 59,6 / 60,3 / 43,3). bybit BTC
  vào lại ngay **chỉ bằng một nửa** tần suất của hai route BTC anh em và **chờ trên
  12 giờ nhiều gấp đôi**.
  **MỘT XÁC NHẬN TÌNH CỜ CHO r80:** r80 nâng `minimum_hold_decisions` từ 12 lên 36 và
  đo được giảm lỗ ~34%; vòng này cho thấy **VÌ SAO** hiệu ứng lớn đến vậy — guard đặt
  ra một **sàn cứng mà hơn một nửa số lần vào lại nằm ĐÚNG trên đó**, nên dịch nó từ
  1h lên 3h **trực tiếp trì hoãn đa số các lần vào lại**. Cơ chế đó ở r80 là **suy
  luận**; nay nó **nhìn thấy được trong chính timing của các trade**.
  **GIỚI HẠN:** **KHÔNG BIẾT cái gì tạo ra ĐUÔI DÀI** — vòng này chuyển câu hỏi từ
  "vì sao occupancy khác nhau" thành "vì sao vài route chờ vượt xa guard", **hẹp hơn
  nhưng vẫn mở**. r267 tìm thấy `trend_score` không thể đổi nhanh hơn một lần đóng
  nến 1h với 84-89% trọng số nằm ở 4h/12h/1d, nên một trend bị ghim ngược chiều sẽ
  **chặn vào lệnh nhiều giờ** — **NHẤT QUÁN** với đuôi 27,7% trên 12h và **HOÀN TOÀN
  CHƯA ĐƯỢC TEST**; tôi **nêu** mối liên hệ, **không khẳng định**. **Chưa chứng minh**
  guard **GÂY RA** sàn đó chứ không phải trùng hợp: khớp chính xác trên ba route là
  bằng chứng mạnh, nhưng **chưa lần theo đường code nào** để xác nhận guard chặn cả
  **vào lại** chứ không chỉ **đảo chiều**. **Không** claim hạ guard sẽ nâng occupancy
  một cách hữu ích — nó sẽ **tăng số trade**, mà r274/r275 đã cho thấy chi phí mỗi
  trade **không** cải thiện khi tần suất tăng; **r80 dịch đòn bẩy này theo chiều
  NGƯỢC LẠI đúng vì lý do đó**. Không claim gì cho binance XAU (n=7) hay bybit XAUT
  (n=1), đã loại khỏi vòng này. File:
  `round278-flat-time-is-pinned-at-the-hold-guard-and-occupancy-is-set-by-the-long-tail.md`.

- **Round 279 (2026-08-30) — CORRECTION: hold guard CHỈ chặn lần vào lại SAU MỘT
  PROTECTIVE EXIT. Dải 0,2-2,9h RỖNG trên mọi route. KHÔNG CONTAINER.**
  Lần theo đúng đường code r278 nói là **chưa lần theo** ("chưa lần theo đường code
  nào để xác nhận guard chặn cả vào lại chứ không chỉ đảo chiều"). **NÓ KHÔNG CHẶN**,
  và code nói điều **sắc hơn** (`trading_modes.rs:238-264`):
  `starts_initial_position = current.position == Flat && !waiting_after_protective_exit`
  — nếu điều này đúng thì vị thế mở **NGAY LẬP TỨC, bỏ qua** kiểm tra holding-period.
  `observe_execution(ProtectiveExit)` đặt `waiting_after_protective_exit = true`, còn
  `decision.exit` thường đặt nó **FALSE**. Vậy: sau một **flat exit** → lần gate pass
  kế tiếp **mở vị thế NGAY, bỏ qua guard**; chỉ sau một **protective exit**
  (stop/take) thì vào lại mới phải chờ đủ **36 quyết định = 3h**.
  **DỰ ĐOÁN: khoảng cách phải LƯỠNG ĐỈNH** — một đỉnh gần 0 và một đỉnh đúng 3h, với
  tỉ lệ gần 0 **BẰNG** tỉ lệ flat exit. **XÁC NHẬN chính xác gần như tối đa mà dữ
  liệu cho phép:**
  | route | gaps | **≤0,2h** | **0,2-2,9h** | **2,9-3,1h** | >3,1h | **flat exits** |
  |---|---|---|---|---|---|---|
  | binance BTC | 472 | **14,0%** | **0,0%** | 40,5% | 45,6% | **14,0%** |
  | bybit BTC | 310 | **5,8%** | **0,0%** | 24,5% | 69,7% | **5,8%** |
  | exness XAU | 391 | **47,6%** | **0,0%** | 17,6% | 34,8% | **47,6%** |
  **Tỉ lệ ≤0,2h BẰNG ĐÚNG tỉ lệ flat exit trên cả ba route**, và **dải 0,2-2,9h RỖNG
  trên cả ba** (0 gap trên 472, 310 và 391). **Không có gì nằm giữa "ngay lập tức" và
  "ba giờ".**
  **ĐIỀU NÀY SỬA GÌ Ở r278:** r278 viết "từ một nửa tới hai phần ba số lần vào lại
  xảy ra đúng thời điểm sớm nhất guard cho phép" và coi rổ `≤3,05h` là **MỘT** quần
  thể. **NÓ LÀ HAI QUẦN THỂ**, và guard chỉ chạm vào một: exness XAU 64,7% = **47,6%
  ngay lập tức (guard KHÔNG dính dáng)** + 17,6% tại guard; binance BTC 52,5% = 14,0%
  + 40,5%; bybit BTC 26,8% = 5,8% + 24,5%. Vậy trên exness XAU **guard chỉ dính dáng
  tới 17,6% số lần vào lại, KHÔNG PHẢI 64,7%** — thống kê của r278 **gộp một cơ chế
  với cơ chế ngược lại của nó**.
  **CHUỖI NAY ĐÃ ĐẦY ĐỦ, VÀ OCCUPANCY ĐI THEO TỈ LỆ CLOSE-REASON:** tỉ lệ flat exit
  47,6% > 14,0% > 5,8% xếp các route **đúng y như occupancy** 86,7% > 59,6% > 43,3%.
  Chuỗi nhân quả: `tỉ lệ close-reason → tỉ lệ exit là "flat" → vào lại ngay hay chờ
  3h → occupancy → (cùng hold, do σ² chi phối) → tần suất`. r277 tách hold và
  occupancy thành "hai nguyên nhân khác biệt"; **chúng KHÔNG khác biệt đến thế** —
  cả hai đều truy về việc **dải TỈ LỆ CỐ ĐỊNH** tương tác với instrument: dải đặt ra
  thời lượng giữ (σ², r273) **và** quyết định giá chạm nó **trước** hay **sau** khi
  tín hiệu chuyển flat, tức đặt ra tỉ lệ close-reason. **NHƯNG ĐÓ CŨNG CHƯA PHẢI TOÀN
  BỘ:** bybit BTC và binance BTC có biến động gần y hệt mà tỉ lệ flat exit là **5,8%
  so với 14,0%** — chênh 2,4 lần, **dải KHÔNG giải thích được**.
  **GIỚI HẠN:** **KHÔNG BIẾT cái gì đặt ra tỉ lệ close-reason trên các route cùng
  biến động** — phần dư bybit/binance **không có gì ở đây giải thích**. **Không**
  claim cách đọc hợp nhất này thay thế r277: **đo đạc** của r277 **vẫn đứng**, thứ
  được sửa là việc gọi hold và occupancy là hai nguyên nhân **hoàn toàn độc lập**, vì
  cả hai đều phản ứng với cùng một dải — và phần dư bybit BTC **chính là phần KHÔNG
  hợp nhất được**. **Không** claim flat exit **luôn luôn** kéo theo vào lại ngay lập
  tức **về nguyên tắc** — thứ được chứng minh là **nó đã xảy ra như vậy trên MỌI gap
  của ba route**; gate về nguyên tắc **có thể** không pass ngay, và rõ ràng gần như
  không bao giờ như vậy. Không claim gì cho binance XAU (n=7) hay bybit XAUT (n=1).
  File:
  `round279-CORRECTION-the-guard-gates-only-post-protective-re-entries-and-the-gap-band-is-empty.md`.

- **Round 280 (2026-08-30) — NGÂN SÁCH ENTRY xếp ĐÚNG thứ tự tỉ lệ flat exit trên ba
  route — và cơ chế hiển nhiên mà tôi nghĩ tới ĐÃ BỊ CODE BÁC BỎ. KHÔNG CONTAINER.**
  Tấn công câu hỏi mở r279 (cái gì đặt ra tỉ lệ close-reason trên các route **cùng
  biến động**: binance BTC 14,0% flat exit so với bybit BTC 5,8%, ở vol 0,14371% và
  0,14406%).
  **TƯƠNG QUAN:**
  | route | **ngân sách entry** | min_role_score | stop_loss | take_profit | **target_flat** |
  |---|---|---|---|---|---|
  | binance BTC | **0,3114** | 0,1 | 59,0% | 27,1% | **14,0%** |
  | exness BTC | **0,3063** | 0,1 | 60,5% | 24,3% | **15,2%** |
  | **bybit BTC** | **0,1763** | 0,1 | 63,7% | 30,5% | **5,8%** |
  Hai route có ngân sách entry ~0,31 nằm ở 14-15% flat exit; route có ngân sách **nhỏ
  hơn 43%** nằm ở **5,8%**. **Thứ tự khớp chính xác**, và `minimum_role_score` **giống
  hệt nhau (0,1)** trên cả ba, nên **ngưỡng entry HIỆU DỤNG** là 32,1%, 32,6% và
  **56,7%** mức tối đa khả dĩ của từng route. **`strategy_weights` KHÔNG xếp theo thứ
  tự này** — exness BTC là 0,353/0,647 còn binance BTC là 0,521/0,479 mà cả hai đều ở
  14-15%; nên **thành phần strategy KHÔNG phải thứ phân tách chúng**, mà là ngân sách
  trọng số interval của entry.
  **CƠ CHẾ TÔI NGHĨ TỚI, VÀ VÌ SAO NÓ HỎNG:** câu chuyện tự nhiên là ngân sách entry
  nhỏ khiến `entry_score` trượt ngưỡng 0,1 thường xuyên hơn, nên Portfolio **hold**
  thay vì hành động, nên vị thế chạy tới dải bảo vệ thay vì bị flat. **CODE BÁC BỎ
  ĐIỀU ĐÓ:** `hold()` (`trading_modes.rs:1100-1112`) trả `exit: FALSE`, và nhánh
  không-pass của `construct()` trả `self.current_target.clone()` — nên **một lần
  trượt ngưỡng để NGUYÊN vị thế đang mở** và **KHÔNG THỂ** tạo ra một close
  `target_flat`. `target_flat` phát ra tại `trading_modes.rs:1764` qua `apply_target`,
  thứ chỉ đóng khi `target.position == Flat` trong lúc đang có vị thế (`1991-1995`);
  target chỉ trở thành Flat qua `decision.exit == true` hoặc `force_flat()`, mà
  `force_flat` được chính source mô tả là **một safety gate**, tức **tầng risk**,
  không phải ngưỡng quyết định. **VẬY NGÂN SÁCH ENTRY TƯƠNG QUAN VỚI TỈ LỆ FLAT EXIT
  QUA MỘT ĐƯỜNG TÔI CHƯA XÁC ĐỊNH ĐƯỢC, VÀ ĐƯỜNG HIỂN NHIÊN ĐÃ BỊ ĐÓNG.** Tôi **kiểm
  tra TRƯỚC khi tuyên bố** — đó chính là điểm mấu chốt.
  **GIỚI HẠN:** **KHÔNG** claim quan hệ nhân quả nào giữa ngân sách entry và flat exit
  — thứ tự khớp chính xác nhưng đây là **BA ĐIỂM**, và cơ chế lẽ ra giải thích được nó
  **đã bị bác**; ba điểm xếp đúng thứ tự **tự nó là bằng chứng yếu**, và r252, r254,
  r261, r273, r275 **đều** là những lần một mẫu hình n-nhỏ gọn gàng về sau phải bị
  giới hạn lại. **KHÔNG** claim tầng risk chịu trách nhiệm — `force_flat` là **MỘT**
  đường tới target Flat và `risk_rejected_counts` **có tồn tại** trong output
  `portfolio_execution`, nhưng tôi **KHÔNG** đọc các counter đó theo route và **không**
  bằng chứng nào nối chúng với tương quan này. **CHƯA XÁC ĐỊNH ĐƯỢC** `decision.exit
  == true` phát sinh từ đâu; `hold()` **không phải** chỗ đó, và **đó là thứ cụ thể
  đầu tiên cần tìm tiếp**. **Không** claim ngân sách entry quan trọng ở chỗ khác —
  r269 và r270 **đều** thấy lập luận về ngân sách entry **thất bại** khi đối chiếu mẫu,
  và đây là ngữ cảnh thứ ba, **chưa ngã ngũ** chứ không phải ủng hộ. File:
  `round280-entry-budget-orders-the-flat-exit-fraction-but-the-obvious-mechanism-is-refuted.md`.

- **Round 281 (2026-08-30) — `target_flat` KHÔNG PHẢI một strategy exit. Nó là cổng
  execution-cost TỪ CHỐI MỘT LỆNH ĐẢO CHIỀU ở 14bps so với hạn mức 10bps. Hai
  container (đúng hạn mức).** Theo đúng bước r280 nêu tên ("chưa xác định
  `decision.exit == true` phát sinh từ đâu; `hold()` không phải chỗ đó; **đó là thứ
  cụ thể đầu tiên cần tìm tiếp**"). **NÓ KHÔNG PHÁT SINH Ở BẤT KỲ ĐÂU TRÊN ĐƯỜNG
  PORTFOLIO:** cả **hai** nhánh của `PortfolioConstructionState::decide()` đều đặt
  `exit: false` — nhánh pass (`trading_modes.rs:864`) và `hold()` (`1103`); nơi duy
  nhất đặt nó từ evidence là `alpha_decision()` (`trading_api.rs:3372`), thứ dựng
  quyết định **MỘT-STRATEGY** cho các ledger `demo-*`, **không phải** Portfolio. Vậy
  trên đường Portfolio, target chỉ có thể thành Flat qua `force_flat()`, và hàm đó có
  **ĐÚNG MỘT NƠI GỌI**: `portfolio_risk.rs:533` →
  `.force_flat(format!("risk_{}_emergency_close", rejection.gate.as_str()))`.
  **MỌI close `target_flat` trên ledger Portfolio ĐỀU LÀ MỘT EMERGENCY CLOSE CỦA
  TẦNG RISK.**
  **KIỂM CHỨNG BẰNG CHÍNH COUNTER RISK, KHÔNG để nguyên như suy luận:** exness XAU
  256 trade `one_target` với `execution_cost` = **98** (mọi gate khác **BẰNG 0**) so
  với tỉ lệ `target_flat` trên ledger **47,6%**; bybit BTC 206 trade với
  `execution_cost` = **11** (mọi gate khác **BẰNG 0**) so với **5,8%**. **Tỉ lệ từ
  chối 98/11 = 8,9 lần so với tỉ lệ `target_flat` 47,6/5,8 = 8,2 lần.** Mọi gate khác
  — `execution_freshness`, `execution_halt`, `performance_halt`,
  `position_reconciliation`, `risk` — **đều bằng 0 trên cả hai route**; gate duy nhất
  từng kích hoạt là **`execution_cost`**.
  **VÀ SOURCE NÓI CHÍNH XÁC VÌ SAO** (`portfolio_risk.rs:205-211`):
  `max_total_cost_bps: 10.0` kèm comment *"One simulated market fill costs 5bps fee +
  2bps slippage by default. **A reversal prices both legs and is rejected at
  14bps.**"* Một lệnh khớp đơn là 7bps và **qua**; **một lệnh ĐẢO CHIỀU tính cả hai
  chân thành 14bps và BỊ TỪ CHỐI**, nên Portfolio **KHÔNG THỂ lật vị thế trực tiếp**
  — gate ép nó **flat** thay vào đó. Đây là **CỐ Ý** và comment nói rõ như vậy.
  **ĐIỀU NÀY SỬA GÌ:** r261, r277, r279 và r280 **đều** đọc `target_flat` là "tín
  hiệu chuyển flat", một strategy exit lành tính. **NÓ LÀ MỘT LỆNH ĐẢO CHIỀU BỊ TỪ
  CHỐI.** Tỉ lệ close-reason **không** cho biết chiến thuật quyết định đứng ngoài bao
  nhiêu lần; nó cho biết **Portfolio ĐỊNH ĐẢO CHIỀU bao nhiêu lần và bị từ chối vì
  chi phí**. Nó cũng cung cấp **đúng cơ chế r280 đi tìm mà không thấy**, theo **CHIỀU
  NGƯỢC LẠI** với chiều r280 đã bác: ngân sách entry **LỚN HƠN** vượt ngưỡng 0,1
  thường xuyên hơn → nhiều quyết định có hướng xác định hơn → **nhiều lần định đảo
  chiều hơn** → nhiều lần bị cost gate từ chối hơn → nhiều `target_flat` hơn; ngân
  sách 0,3114 / 0,3063 / 0,1763 so với tỉ lệ flat 14,0% / 15,2% / 5,8% **chạy đúng
  chiều** cho chuỗi đó.
  **GIỚI HẠN:** **LIÊN KẾT ngân sách entry → số lần định đảo chiều CHƯA ĐƯỢC ĐO** —
  chuỗi đã kiểm chứng chạy từ `force_flat` tới cost gate tới đảo chiều; việc ngân sách
  lớn hơn tạo ra nhiều lần định đảo chiều hơn **chỉ là phần hoàn thiện HỢP LÝ**, và
  r280 **đã** có một câu chuyện ngân sách entry bị bác rồi, đây là câu chuyện thứ hai
  **dựng trên ba điểm**. **KHÔNG** claim đây là lỗi — comment cho thấy việc từ chối ở
  14bps là **CÓ CHỦ Ý**, còn việc một Portfolio **không bao giờ đảo chiều trực tiếp
  được** có phải hành vi **mong muốn** hay không là **câu hỏi thiết kế**, không phải
  phát hiện nghiên cứu, và tôi **không** nêu nó như một lỗi. **Không** claim con số
  counter và con số ledger phải khớp chính xác (98/256 = 38,3% so với 47,6% của
  ledger — khác cửa sổ, khác mẫu); **TỈ LỆ GIỮA CÁC ROUTE** mới là bằng chứng, không
  phải mức tuyệt đối. Không claim gì về các route ngoài hai route đã đo. File:
  `round281-target-flat-is-the-cost-gate-rejecting-reversals-not-a-strategy-exit.md`.

- **Round 282 (2026-08-30) — CORRECTION: `target_flat` KHÔNG PHẢI `force_flat`. Phép
  test PAIRWISE mà r279 chưa từng chạy BÁC BỎ cơ chế của r281. KHÔNG CONTAINER.**
  **MÂU THUẪN GIỮA HAI VÒNG CỦA CHÍNH TÔI:** r281 kết luận mọi close `target_flat` là
  emergency close của tầng risk qua `force_flat()`; nhưng `force_flat` đặt
  `waiting_after_protective_exit = TRUE` (`trading_modes.rs:285`), mà theo đúng cơ
  chế của r279 thì vào lại **phải chờ guard 3h**. r279 kết luận **NGƯỢC LẠI** — flat
  exit kéo theo vào lại **NGAY LẬP TỨC** — và đạt tới đó bằng cách khớp **TỈ LỆ TỔNG
  HỢP, CHƯA BAO GIỜ pairwise**. Phép test pairwise phân xử:
  | route | sau `stop_loss` | sau `take_profit` | sau **`target_flat`** |
  |---|---|---|---|
  | binance BTC | n=279, TV **3,00h**, ≤0,2h **0,0%** | n=127, TV 10,42h, **0,0%** | n=66, TV **0,08h**, ≤0,2h **100,0%** |
  | bybit BTC | n=198, TV 3,67h, **0,0%** | n=94, TV 12,50h, **0,0%** | n=18, TV **0,08h**, **100,0%** |
  | exness XAU | n=126, TV 4,00h, **0,0%** | n=79, TV 3,42h, **0,0%** | n=186, TV **0,08h**, **100,0%** |
  **Sau `target_flat`, vào lại là NGAY LẬP TỨC 100% số lần trên cả ba route** (trung
  vị 0,08h ≈ một quyết định 5m); sau một close bảo vệ thì **KHÔNG BAO GIỜ** ngay lập
  tức.
  **HAI HỆ QUẢ, THEO HAI CHIỀU NGƯỢC NHAU. r279 ĐƯỢC XÁC NHẬN và mạnh thêm** — suy
  luận theo tỉ lệ tổng hợp của nó **đúng**, và phép test pairwise nó **chưa từng
  chạy** nay xác nhận trực tiếp, ở mức 100%/0% trên **370** gap `target_flat` và
  **903** gap bảo vệ. **CƠ CHẾ CỦA r281 BỊ BÁC** — nếu `target_flat` đến từ
  `force_flat` thì cờ đã được đặt và vào lại phải chờ 3h; **nó ngay lập tức, luôn
  luôn**. Vậy `target_flat` do nhánh **`decision.exit == TRUE`** của `construct()`
  sinh ra — đúng nhánh **đặt cờ đó thành FALSE** — **chứ không** phải tầng risk.
  **TƯƠNG QUAN của r281 vẫn sống**: `execution_cost` 98 so với 11 đối lại tỉ lệ
  `target_flat` 47,6% so với 5,8% (8,9x so với 8,2x) vẫn là **sự thật quan sát được**.
  **ĐƯỜNG NHÂN QUẢ tôi khẳng định từ nó thì SAI** — tôi đọc **một** nơi gọi
  `force_flat`, thấy một tỉ lệ khớp, và kết luận cơ chế **mà KHÔNG kiểm tra dự đoán
  mà nó đưa ra**.
  **ĐIỀU NÀY ĐẨY CÂU HỎI r280 VỀ ĐÂU: MỞ LẠI.** r280 hỏi `decision.exit == true` phát
  sinh từ đâu; r281 trả lời "không đâu cả — là `force_flat`", và câu trả lời đó nay
  **CHẾT**. Dữ liệu nói `decision.exit` **CÓ** là true cho các close này, nên cách đọc
  của tôi rằng cả hai nhánh `decide()` đặt `exit: false` **phải là KHÔNG ĐẦY ĐỦ** —
  **có một constructor `PortfolioDecision` tôi chưa tìm ra**.
  **MỘT QUAN SÁT TÌNH CỜ:** sau `take_profit`, trung vị gap là **10,42h / 12,50h**
  trên hai route BTC, so với **3,00h / 3,67h** sau `stop_loss` — take kéo theo chờ
  **lâu hơn hẳn** stop, dù cả hai đều vượt guard. **Chưa điều tra.**
  **GIỚI HẠN:** **VẪN CHƯA ĐỊNH VỊ ĐƯỢC** `decision.exit == true` đến từ đâu, và câu
  trả lời trước của tôi **sai**; bước tiếp theo là tìm **MỌI** constructor
  `PortfolioDecision` đi tới `construct()` trên đường paper-ledger, **không phải đoán
  lần nữa**. **KHÔNG** claim tương quan `execution_cost` là giả — nó **CHƯA ĐƯỢC GIẢI
  THÍCH**, khác hẳn; 8,9x so với 8,2x qua hai route **không phải không có gì**, và
  gate **có** kích hoạt; thứ bị bác là **ĐƯỜNG ĐI**, không phải mối liên hệ. Không
  claim gì về vì sao take kéo theo chờ lâu hơn stop. **Không** claim các phát hiện
  khác của r281 hỏng — các phép đo counter và comment policy (`max_total_cost_bps`
  10,0; đảo chiều tính 14bps) **vẫn đứng như đã đọc**; chỉ **mối nối tới `target_flat`
  bị rút lại**. File:
  `round282-CORRECTION-target-flat-is-not-force-flat-the-pairwise-test-refutes-round-281.md`.

- **Round 283 (2026-08-30) — LIỆT KÊ XONG: CẢ HAI đường ứng viên cho `target_flat`
  đều BỊ LOẠI, và hành vi quan sát được KHÔNG khớp đường nào. KHÔNG CONTAINER.**
  Làm **đúng theo chữ** chỉ dẫn r282 ("tìm **MỌI** constructor `PortfolioDecision` đi
  tới `construct()` trên đường paper-ledger, **không đoán lần nữa**") — làm **có hệ
  thống** thay vì grep theo triệu chứng.
  **MỌI constructor `PortfolioDecision` nuôi đường Portfolio/paper đều đặt
  `exit: false`, HARD-CODED:** `trading_modes.rs:862` (nhánh pass của `decide()`),
  `trading_modes.rs:1101` (`decide()` → `hold()`), `trading_api.rs:2458`
  (`record_market_without_decision`). Cả **hai** nơi gọi `construct()` lúc runtime
  nuôi paper ledger đều lấy decision từ `…evidence.decide(…)`:
  `trading_api.rs:1707` (realtime) và `2260` (driver historical replay); các
  constructor còn lại nằm trong `finance-research` (binary riêng) và `alpha_decision`
  (ledger `demo-*` một-strategy). **VẬY `decision.exit` KHÔNG BAO GIỜ true trên
  đường này — và suy luận của r282 rằng nó phải true ĐƯỢC RÚT LẠI.**
  **`apply_target` có ĐÚNG HAI nơi gọi:** `1734` (`"strategy_exit"`,
  `"opposite_decision"` — một-strategy) và `1764` (`"target_flat"`,
  `"target_changed"` — Portfolio). Nên `target_flat` **chắc chắn** là **nhánh FLAT
  của đường Portfolio**, và nó đòi `target.position == Flat`.
  **MỘT SỰ THẬT MỚI — ĐẢO CHIỀU KHÔNG BAO GIỜ XẢY RA:** `target_changed`, nhãn đảo
  chiều **tại cùng nơi gọi đó**, **KHÔNG xuất hiện lần nào** trong bất kỳ phân bố
  close-reason nào đã thu thập qua **ba route và 1176 trade** (r261, r280, r282 đều
  chỉ có `stop_loss`, `take_profit`, `target_flat`). Nhánh đảo chiều **đóng và mở lại
  TRONG CÙNG MỘT LẦN GỌI** (`trading_modes.rs:1997-2008`, *"A reversal is one
  action"*), nên một lệnh đảo chiều sẽ tạo close `target_changed` với gap ~0; **không
  có cái nào**. **Đảo chiều trực tiếp KHÔNG BAO GIỜ xảy ra** — nhất quán với cách đọc
  cost-gate của r281, dù r282 đã bác mối nối của cách đọc đó tới `target_flat`.
  **CẢ HAI CƠ CHẾ ỨNG VIÊN NAY ĐỀU BỊ LOẠI:** để có close `target_flat`,
  `current_target` phải **đã** Flat, mà trên đường Portfolio chỉ tới được qua
  `force_flat()` (đặt `waiting_after_protective_exit = true` → lần vào kế tiếp cần
  guard 3h) hoặc `observe_execution(ProtectiveExit)` (**cùng cờ, cùng hệ quả**). r282
  đo được vào lại sau `target_flat` là **100% ≤0,2h trên cả ba route** (n=66/18/186,
  trung vị 0,08h). **KHÔNG đường nào cho phép điều đó**, và khả năng thứ ba
  (`decision.exit == true`) **đã bị loại ở trên**. **VẬY HÀNH VI QUAN SÁT ĐƯỢC KHÔNG
  ĐƯỢC GIẢI THÍCH BỞI CODE NHƯ TÔI ĐÃ ĐỌC.** Tôi **nói thẳng điều đó** thay vì đề
  xuất một cơ chế thứ ba, **sau khi đã có hai cơ chế bị bác trong hai vòng liên
  tiếp**.
  **CHỖ TÔI CÓ KHẢ NĂNG SAI NHẤT:** đây là ledger `paper-**backtest**-*` — **seed của
  historical replay** — và tôi **giả định** chúng được đổ qua `trading_api.rs:2260`
  dựa trên bằng chứng `historical_replay_completed_scopes` của r262. Nếu thực ra
  chúng được seed qua một đường tôi **chưa lần theo**, thì **mọi** suy luận ở trên về
  close-reason **của chúng** đang dựng trên **sai call graph**. **XÁC MINH ĐƯỜNG CODE
  NÀO THỰC SỰ GHI CÁC LEDGER NÀY LÀ BƯỚC KẾ TIẾP**, trước mọi tuyên bố cơ chế nào
  nữa.
  **GIỚI HẠN:** **KHÔNG** claim cơ chế nào cho `target_flat` — **ba** ứng viên đã bị
  loại (`force_flat` ở r282, `decision.exit` ở vòng này, và cả hai đường protective)
  và tôi **không** đưa ra ứng viên thứ tư. Không claim liệt kê là vét cạn ngoài các
  crate đã tìm (`finance-core`, `finance-api`, `finance-research`,
  `finance-strategy`, trừ test). Tương quan cost-gate của r281 vẫn là **liên hệ chưa
  giải thích**, nay có thêm việc **vắng mặt `target_changed`** — ít nhất **nhất quán**
  với việc đảo chiều bị chặn. **KHÔNG** claim các ledger được ghi bởi đường tôi giả
  định — **đó chính là thứ cần kiểm tiếp theo**, và nó **có thể làm VÔ HIỆU cách đóng
  khung của vòng này** chứ không phải mở rộng nó. File:
  `round283-enumeration-complete-both-candidate-paths-excluded-and-the-behaviour-is-unexplained.md`.

- **Round 284 (2026-08-30) — CALL GRAPH ĐƯỢC XÁC NHẬN, nên MÂU THUẪN CODE↔DỮ LIỆU LÀ
  CÓ THẬT. Nộp thành P3, chỉ điều tra. KHÔNG CONTAINER.** Làm đúng phép kiểm r283 nêu
  tên ("xác minh đường code nào thực sự ghi các ledger này là bước kế tiếp, **trước**
  mọi tuyên bố cơ chế nào nữa"). **GIẢ ĐỊNH ĐÚNG** (`trading_api.rs:831-866`):
  `paper-{rule_id}` dựng qua `context.simulated_child(..., WeightedEnsemble)` và
  `paper-backtest-{rule_id}` qua
  `simulated_child_with_workflow(..., WorkflowKind::Backtest, ..., WeightedEnsemble)`,
  và **CẢ HAI lane mang CÙNG `PortfolioReplaySemantics`** — cùng
  `minimum_holding_decisions`, cùng `decision_policy`, cùng `risk_policy`. Vậy ledger
  backtest **đúng là** do bộ máy Portfolio ghi với policy đang triển khai, và call
  graph của r283 **đúng**.
  **TRẠNG THÁI `portfolio_construction` ĐỌC TRỰC TIẾP** trên ba route: binance BTC
  `current_target` **long**, reason `multi_timeframe_gate_passed`,
  `waiting_after_protective_exit` **false**, `decisions_since_target_change` **250**,
  `minimum_holding_decisions` **36**; bybit BTC short / cùng reason / false / 238 /
  36; exness XAU short / cùng reason / false / 39 / 36. Cờ đó **tạm thời** đúng như
  dự đoán (một lần gate pass đổi vị thế sẽ reset nó), và
  **`minimum_holding_decisions` = 36 được xác nhận TRONG TRẠNG THÁI ĐÃ PERSIST**, chứ
  không chỉ trong cấu hình.
  **MÂU THUẪN, NAY VỮNG CHẮC:** truy `construct()` vét cạn — nhánh gate-pass **luôn**
  cho Long hoặc Short (`side != Hold`), nhánh không-pass **clone** target hiện tại, và
  `decision.exit` **không bao giờ** true trên đường này (r283). **Vậy `current_target`
  chỉ có thể thành Flat qua `force_flat()` hoặc `observe_execution(ProtectiveExit)` —
  và CẢ HAI đặt `waiting_after_protective_exit = true`**, thứ buộc lần vào kế tiếp
  phải chờ 36 quyết định. r282 đo được vào lại sau `target_flat` là **100% ≤0,2h trên
  cả ba route** (n=66/18/186, trung vị 0,08h ≈ một nến 5m). **MỌI ĐƯỜNG ỨNG VIÊN ĐÃ BỊ
  LOẠI, CALL GRAPH ĐÃ ĐƯỢC XÁC MINH, VÀ HAI BÊN VẪN MÂU THUẪN.** Tôi **không** đề xuất
  cơ chế thứ tư.
  **ĐÂY LÀ GÌ, NÓI THẲNG:** hoặc tôi **đọc sai một chuyển trạng thái** trong
  `PortfolioConstructionState`, hoặc **nhãn `close_reason` của ledger KHÔNG tương ứng**
  với đường code tôi đã truy. **Cả hai đều đáng để người có khả năng instrument hệ
  thống đang chạy kiểm tra** — **một dòng log duy nhất** mang `current_target.reason`
  và `waiting_after_protective_exit` tại mỗi lần `apply_target` đóng flat sẽ **giải
  quyết ngay**, và r265 **đã ghi nhận** rằng observability tương đương **không tồn
  tại** cho hold reason. **Nộp thành P3, chỉ điều tra, KHÔNG áp dụng** — nó không giải
  thích PnL nào và không chặn target nào; nó là **mâu thuẫn giữa cơ chế được tài liệu
  hoá và hành vi được ghi nhận**.
  **MỘT GHI CHÚ TRUNG THỰC VỀ MẠCH NÀY:** r279-r284 đã tiêu **SÁU VÒNG** cho cơ chế
  `target_flat`. Chuỗi **ĐO ĐẠC** thì vững và tái dùng được (hold ~ σ², occupancy từ
  thời gian flat, sàn chính xác của guard, bảng close-reason pairwise, việc vắng mặt
  `target_changed`). Chuỗi **TUYÊN BỐ CƠ CHẾ** thì đã sinh ra **BA lần bác bỏ chính
  công việc của tôi** (r279, r282, r283). **Đo đạc là phần bền; lẽ ra tôi nên NGỪNG đề
  xuất cơ chế sau lần bác thứ hai và nộp mâu thuẫn này ngay lúc đó.**
  **GIỚI HẠN:** **không phân biệt được BÊN NÀO của mâu thuẫn là sai** từ việc đọc tĩnh
  cộng ảnh chụp; **không** đề xuất cơ chế thứ tư; **KHÔNG** claim điều này ảnh hưởng
  kết quả giao dịch — nó ảnh hưởng **CÁCH TÔI MÔ TẢ** chúng, còn các phép đo PnL/tần
  suất của r272-r278 **không** phụ thuộc vào việc cơ chế nào tạo ra close đó; không
  claim gì về các route ngoài ba route đã đọc. File:
  `round284-the-call-graph-is-confirmed-so-the-code-data-discrepancy-is-real.md`.

- **Round 285 (2026-08-30) — BẢNG TARGET 3 ĐẦY ĐỦ CẢ ĐỘI trên MỘT cửa sổ khớp nhau:
  CHỈ 2/6 ROUTE ĐẠT, và verdict của `exness XAU` LẬT theo cửa sổ. Hai container (đúng
  hạn mức). SỬA r274.** r274-r276 dựng bức tranh Target 3 **chắp vá** (exness XAU ở
  360 ngày, bốn route ở 260 ngày, **bybit XAUT chưa từng đo**). Vòng này đo route
  còn thiếu và **đo lại exness XAU trên cửa sổ khớp**, để cả đội nằm trên **MỘT nền
  so sánh** — `one_target`, tham số triển khai, 260 ngày.
  | route | vol 5m | trades | **/tuần** | pnl | pnl/trade | **Target 3** |
  |---|---|---|---|---|---|---|
  | exness BTC/USD | 0,14218% | 364 | **9,80** | −3,6254 | −0,00996 | **ĐẠT** |
  | binance BTC/USDT | 0,14371% | 350 | **9,42** | −3,3986 | −0,00971 | **ĐẠT** |
  | exness XAU/USD | 0,11212% | 254 | **6,84** | −1,0919 | −0,00430 | **TRƯỢT** |
  | bybit BTC/USDT | 0,14406% | 206 | **5,55** | −2,3669 | −0,01149 | **TRƯỢT** |
  | binance XAU/USDT | 0,09058% | 135 | **3,63** | −1,4331 | −0,01062 | **TRƯỢT** |
  | bybit XAUT/USDT | 0,08812% | 90 | **2,42** | −0,2234 | −0,00248 | **TRƯỢT** |
  **HAI TRÊN SÁU ROUTE ĐẠT TARGET 3. BỐN KHÔNG. CẢ SÁU ĐỀU LỖ.**
  **SỬA r274:** r274 ghi exness XAU **7,06/tuần — "đạt với biên 0,9%"** trên cửa sổ
  360 ngày. Trên cửa sổ **khớp 260 ngày** nó là **6,84/tuần — TRƯỢT 2,3%**.
  **VERDICT LẬT THEO CỬA SỔ QUAN SÁT.** r274 đã nêu biên là cực mỏng; **nó mỏng tới
  mức "đạt" KHÔNG phải một tính chất ổn định của route**. **Không con số nào sai** —
  phát biểu đúng là exness XAU **nằm NGAY TRÊN NGƯỠNG**, và **một phép đo đơn lẻ
  không nên được trích như một verdict** theo bất kỳ chiều nào. Phần còn lại của r274
  **vẫn đứng**: A/B ATR (tần suất 2,43x, lỗ 2,27x, mỗi trade 0,93x) chạy trên **một**
  cửa sổ với **chỉ dải thay đổi**, phép so đó **không bị ảnh hưởng**.
  **SỬA BIÊN ĐỘ pnl/trade CỦA r275:** r275 ghi chi phí mỗi trade trải **1,6 lần** qua
  bốn phép đo và cảnh báo "hằng số gần cố định −0,0068" lỏng hơn các vòng trước tuyên
  bố. **Cả đội là −0,00248 tới −0,01149, biên độ 4,6 LẦN.** Kết quả định tính không
  đổi (mọi route đều lỗ mỗi trade) nhưng **hằng số đó KHÔNG NÊN được trích như một
  con số duy nhất** khi so sánh giữa các route.
  **BIẾN ĐỘNG vs TẦN SUẤT CẢ ĐỘI:** Spearman **+0,600** (perm p=0,242) trên cả sáu;
  **loại bybit BTC** — outlier r276 đã biết, mà occupancy 43,3% (r277) kéo nó từ mức
  kỳ vọng ~9,5/tuần xuống 5,55 — thì **+0,900** (p=0,083).
  **GIỚI HẠN:** **KHÔNG** claim bốn route trượt Target 3 **trong production** — đây là
  backtest 260 ngày; cửa sổ live (r259) vẫn cho khoảng như [0,09; 20,30]/tuần và
  **không giải quyết được gì**, còn exness XAU cho thấy verdict **nhạy tới mức nào**
  với cửa sổ. **KHÔNG** claim việc loại bybit BTC là suy luận hợp lệ — **NÓ KHÔNG
  PHẢI**; dòng +0,900 chỉ để **làm outlier của r276 nhìn thấy được**, và **loại một
  điểm vì nó bất đồng chính là thứ tôi KHÔNG được coi là bằng chứng**. Không claim
  nguyên nhân nào ngoài những gì r273-r278 đã lập. **KHÔNG** khuyến nghị xem lại
  Target 3 — r275 đã lập rằng Target 1 và 3 **đối nghịch về mặt cơ học**, và việc làm
  gì với một target mà **bốn trên sáu route không đạt** là **quyết định của user**;
  tôi **không** đưa khuyến nghị nào. File:
  `round285-the-complete-fleet-target3-table-two-of-six-pass-and-exness-xau-flips.md`.

- **Round 286 (2026-08-30) — HAI ROUTE ĐẠT TARGET 3 SỐNG SÓT qua thay đổi cửa sổ 100
  ngày; CHỈ `exness XAU` là thực sự nằm trên ngưỡng. Hai container (đúng hạn mức).**
  Trả lời câu hỏi r285 nêu ra mà **chưa** trả lời: r285 thấy verdict của exness XAU
  **lật** giữa hai cửa sổ (7,06/tuần ở 360n, 6,84 ở 260n), điều đó **đe doạ cả bảng**
  — nếu **mọi** verdict đều dịch theo cửa sổ thì "2/6 đạt" **không phải** một trạng
  thái đội. **DỰ ĐOÁN GHI RA ĐĨA TRƯỚC KHI KHỞI ĐỘNG CONTAINER NÀO**
  (`precommit_r286.md`): test **hai route ĐẠT** trên cửa sổ thứ hai; cả hai **nằm
  trong 9,0-10,5/tuần** nếu hiệu ứng cửa sổ đúng cỡ ~3% thấy ở exness XAU; **route nào
  rơi xuống dưới 7 thì KHÔNG verdict một-cửa-sổ nào đáng tin**.
  | route | 260n | 360n | dịch chuyển | verdict 260n | verdict 360n |
  |---|---|---|---|---|---|
  | exness BTC/USD | 9,80 | **9,35** | **−4,6%** | ĐẠT | **ĐẠT** |
  | binance BTC/USDT | 9,42 | **8,92** | **−5,3%** | ĐẠT | **ĐẠT** |
  **KHÔNG route nào tới gần vạch** — biên **+33,6%** và **+27,4%** ở 360 ngày — nên
  các route đạt của r285 là **BỀN VỚI CỬA SỔ**.
  **PHẦN NỘI DUNG ĐÚNG; DẢI DỰ ĐOÁN CỦA TÔI HƠI CHẶT QUÁ:** binance BTC rơi vào
  **8,92**, **NGAY NGOÀI** dải 9,0-10,5 tôi đặt, vì tôi đặt dải đó khi giả định hiệu
  ứng cửa sổ ~3% trong khi hiệu ứng thật là **4,6-5,3%**, lớn hơn khoảng một nửa nữa.
  **Chiều và hệ quả** của dự đoán **đúng**, **độ chính xác** thì **không**, và tôi
  **ghi nhận cú trượt** thay vì làm tròn 8,92 thành "nằm trong".
  **DỊCH CHUYỂN LÀ THEO TỪNG ROUTE, KHÔNG PHẢI THIÊN LỆCH CỬA SỔ:** đi từ 260n →
  360n, exness BTC dịch **−4,6%** và binance BTC **−5,3%** (**XUỐNG**) trong khi
  exness XAU dịch **+3,2%** (**LÊN**). Vậy đây **KHÔNG** phải artifact hệ thống của độ
  dài cửa sổ — nó là **biến thiên theo route** cỡ vài phần trăm, thứ **chỉ quan trọng
  ở nơi biên nhỏ hơn nó**.
  **TRẠNG THÁI ĐỘI ĐƯỢC LÀM CHẮC:** **đạt bền vững** (cả hai cửa sổ) — exness BTC,
  binance BTC, biên **+27% tới +40%**; **thực sự mập mờ** — exness XAU, **±3%, lật**;
  **trượt với biên rộng** — bybit BTC **−21%**, binance XAU **−48%**, bybit XAUT
  **−65%**. **CHỈ MỘT dòng** trong bảng r285 nhạy với cửa sổ, và **đó đúng là dòng đã
  được gắn cờ**; năm verdict còn lại **không đủ gần vạch** để vài phần trăm làm thay
  đổi.
  **GIỚI HẠN:** **KHÔNG** claim bất cứ điều gì ở đây đúng **trong production** — mọi
  con số là backtest dưới tham số triển khai; khoảng live của r259 vẫn vô định và vòng
  này **không** đụng tới nó. **KHÔNG** claim hai cửa sổ là đủ để lập tính bền — **HAI
  ĐIỂM mỗi route**; chúng loại được hiệu ứng cửa sổ **LỚN**, không loại được hiệu ứng
  vừa, và **cửa sổ thứ ba chưa chạy**. **KHÔNG** claim ba route trượt rộng cũng bền
  như vậy — chúng mới đo trên **MỘT** cửa sổ mỗi route, và việc biên của chúng
  (−21% tới −65%) lớn hơn nhiều hiệu ứng 3-5% quan sát được là lý do tôi coi chúng an
  toàn, **đó là một LẬP LUẬN, không phải một PHÉP ĐO**. Không thay đổi kết luận nào
  của r285: vòng này **thêm tính bền, không thêm trạng thái mới**. File:
  `round286-the-two-passes-are-window-robust-only-exness-xau-is-genuinely-ambiguous.md`.

- **Round 287 (2026-08-30) — CORRECTION: hiệu ứng cửa sổ chỉ 3-5% trên các route BẬN
  NHẤT; trên route THƯA nó là 43% và 101%. Hai container (đúng hạn mức).** Đo đúng
  thứ r286 **tự thừa nhận là mới chỉ lập luận**: r286 thừa nhận ba route trượt rộng
  mới đo trên **MỘT cửa sổ mỗi route**, và việc gọi chúng an toàn vì biên vượt hiệu
  ứng cửa sổ 3-5% là **"một LẬP LUẬN, không phải một PHÉP ĐO"**. Vòng này **đo** hai
  route XAU trượt (ưu tiên XAU-trước), dự đoán và tiêu chí **ghi ra đĩa trước khi
  chạy** (`precommit_r287.md`): binance XAU trong **3,2-4,1**/tuần, bybit XAUT trong
  **2,2-2,7**/tuần.
  | route | 260n | cửa sổ 2 | kết quả | **dịch chuyển** | trong dải? | Target 3 |
  |---|---|---|---|---|---|---|
  | binance XAU/USDT | 3,63 | 180n¹ | **2,06** | **−43,2%** | **KHÔNG** | TRƯỢT |
  | bybit XAUT/USDT | 2,42 | 360n | **4,86** | **+100,9%** | **KHÔNG** | TRƯỢT |
  ¹ kline của binance XAU bắt đầu 2025-12-11 (~262 ngày) nên cửa sổ **DÀI hơn không
  tồn tại** — cửa sổ thứ hai buộc phải **ngắn hơn**. **Giới hạn dữ liệu, không phải
  lựa chọn.**
  **CẢ HAI DỰ ĐOÁN ĐỀU TRẬT, VÀ TRẬT NẶNG:** bybit XAUT **TĂNG GẤP ĐÔI**; binance XAU
  **giảm gần một nửa**. Dải của tôi giả định hiệu ứng 3-5% mà r286 đo; hiệu ứng thật
  trên các route này là **43% và 101%**.
  | route | trade (cửa sổ nhỏ hơn) | hiệu ứng cửa sổ |
  |---|---|---|
  | exness BTC | 481 | −4,6% |
  | binance BTC | 459 | −5,3% |
  | exness XAU | 254 | +3,2% |
  | **binance XAU** | **53** | **−43,2%** |
  | **bybit XAUT** | 250 | **+100,9%** |
  **Con số 3-5% của r286 được TỔNG QUÁT HOÁ từ hai route tần suất CAO NHẤT và KHÔNG
  đúng trên route thưa.** **Tôi** đã tổng quát hoá như vậy và **dùng nó để lập luận
  ba route được phân loại an toàn; lập luận đó BỊ BÁC.**
  **THỨ SỐNG SÓT VÀ THỨ KHÔNG. VERDICT "TRƯỢT" SỐNG SÓT:** không route nào tới gần
  7/tuần trên bất kỳ cửa sổ nào (2,06-3,63 và 2,42-4,86), và pre-registration của tôi
  đã nêu "chạm 7/tuần" là kết cục làm đổi bức tranh — **nó đã không xảy ra**. **CÁC
  BIÊN THÌ KHÔNG SỐNG SÓT:** bảng r285 ghi bybit XAUT ở **−65%** dưới vạch; trên cửa
  sổ 360 ngày nó là **−31%**. Chia pass/fail giữ nguyên cho hai route này nhưng
  **KHOẢNG CÁCH** ghi kèm **không đáng tin trên route tần suất thấp** và **không nên
  đọc như thước đo độ tin cậy**. **LẬP LUẬN AN TOÀN CỦA r286 ĐƯỢC RÚT LẠI:**
  `bybit BTC` — route trượt **hẹp nhất** ở −21%, và **VẪN CHỈ MỘT CỬA SỔ** vì hai
  container không phủ nổi ba route — nay là **verdict KÉM CHẮC CHẮN NHẤT** trong
  bảng, **không phải** một verdict an toàn; một cú dịch cỡ +101% sẽ **vượt vạch**.
  **GIỚI HẠN:** **KHÔNG** claim bybit BTC sẽ sống sót qua cửa sổ thứ hai — nó **chưa
  được test** và nay là verdict tôi **ít tin nhất**, mục tiêu hiển nhiên của vòng sau.
  **KHÔNG** claim hiệu ứng này **do** số trade thấp gây ra — tương quan với số trade
  sạch qua năm route **NHƯNG bybit XAUT có 250 trade**, ngang với 254 của exness XAU
  vốn chỉ dịch 3,2%, nên **số trade một mình KHÔNG giải thích được**. **KHÔNG** claim
  rate thật của route nào là một trong các con số này — hai cửa sổ mỗi route **kẹp
  khoảng** 2,06-3,63 và 2,42-4,86, và **đó mới là KHOẢNG trung thực, không phải một
  ước lượng điểm**. **Không** claim chia pass/fail của r285 sai — nó **không** bị
  thách thức ở đây, chỉ **các biên** bên cạnh nó, và **chỉ trên route thưa**. File:
  `round287-CORRECTION-the-window-effect-is-3pct-on-busy-routes-and-up-to-101pct-on-quiet-ones.md`.

- **Round 288 (2026-08-30) — `bybit BTC` TRƯỢT Target 3 trên CẢ BA cửa sổ; và dự đoán
  dải của tôi ĐÃ TRẬT BA VÒNG LIÊN TIẾP. Hai container (đúng hạn mức).**
  Đo đúng mục tiêu r287 nêu tên: bybit BTC là **"verdict tôi ít tin nhất"** — route
  trượt **hẹp nhất** (−21%) và là route **duy nhất còn ở một cửa sổ**. Cả hai
  container dồn vào nó, cho **BA cửa sổ trên đúng cái verdict quan trọng nhất**.
  | cửa sổ | trades | **/tuần** | dịch vs 260n | pnl/trade | Target 3 |
  |---|---|---|---|---|---|
  | 180n | 80 | **3,11** | **−43,9%** | −0,01914 | **TRƯỢT** |
  | 260n | 206 | **5,55** | — | −0,01149 | **TRƯỢT** |
  | 360n | 244 | **4,74** | **−14,5%** | −0,00702 | **TRƯỢT** |
  **Cả ba đều trượt.** Khoảng 3,11-5,55/tuần (trải **1,78 lần**), với **giá trị cao
  nhất vẫn thấp hơn vạch 21%**. Theo đúng tiêu chí tôi đăng ký trước khi chạy ("cả ba
  cửa sổ dưới 7 → verdict TRƯỢT vững chắc tới mức ba cửa sổ có thể làm được"), **đó
  là kết cục**. Vậy **"2/6 đạt" của r285 ĐỨNG VỮNG**, và **dòng kém chắc nhất của nó
  nay là dòng có bằng chứng tốt nhất**.
  **DẢI CỦA TÔI LẠI TRẬT — VÒNG THỨ BA LIÊN TIẾP.** Tôi dự đoán 4,0-7,5/tuần; cửa sổ
  180 ngày ra **3,11**, **dưới sàn**. Bảng thành tích: r286 dải 9,0-10,5 vs thực tế
  **8,92** (trật thấp); r287 dải 3,2-4,1 và 2,2-2,7 vs **2,06** và **4,86** (trật cả
  hai, **nặng**); r288 dải 4,0-7,5 vs **3,11** (trật thấp). **MỌI TIÊU CHÍ NỘI DUNG
  TÔI ĐẶT ĐỀU ĐÚNG; MỌI DẢI SỐ TÔI ĐẶT ĐỀU SAI.** Bảy hiệu ứng cửa sổ đã đo: −4,6%,
  −5,3%, +3,2%, −43,2%, +100,9%, −43,9%, −14,5%. **Tôi liên tục giả định một sự ổn
  định mà đại lượng này KHÔNG có.** **Lập trường trung thực: rate Target 3 một-cửa-sổ
  dao động tới 2 lần trên một route, và tôi KHÔNG dự báo được chiều lẫn độ lớn; tôi
  nên NGỪNG đưa ra dải hẹp cho nó — chúng không thêm thông tin và đã sai ba lần.**
  **CHI PHÍ MỖI TRADE CŨNG KHÔNG HẰNG SỐ NGAY TRONG MỘT ROUTE:** riêng bybit BTC là
  −0,01914 (180n), −0,01149 (260n), −0,00702 (360n) — **biên độ 2,7 lần trên MỘT
  route chỉ do chọn cửa sổ**. r275 nới "hằng số gần cố định −0,0068" thành biên độ
  1,6 lần giữa các route, r285 thành 4,6 lần, và vòng này cho thấy nó còn dịch **2,7
  lần NGAY TRONG một route**; **nó KHÔNG phải hằng số theo bất kỳ nghĩa hữu ích nào
  và không nên được trích như vậy.** Kết quả **định tính** thì không đổi và chưa bao
  giờ lung lay: **mọi route, mọi cửa sổ, mọi cấu hình đều LỖ mỗi trade.**
  **GIỚI HẠN:** **KHÔNG** claim ba cửa sổ là dứt điểm — ba điểm kẹp 3,11-5,55 và điểm
  thứ tư **có thể rơi ngoài**; thứ chúng lập được là **không cửa sổ nào ĐÃ ĐO tới gần
  vạch trong 21%**, chứ không phải **không thể**. Backtest suốt; khoảng live r259 vẫn
  vô định. **Không** nguyên nhân nào cho độ nhạy cửa sổ được đưa ra (r287 đã cho thấy
  số trade **không** dự báo được nó). Tính tới vòng này **cả sáu route đều có ít nhất
  hai cửa sổ** — exness BTC 260/360, binance BTC 260/360, exness XAU 260/360, binance
  XAU 180/260, bybit XAUT 260/360, bybit BTC 180/260/360 — **nhưng r287 đã cho thấy
  hai cửa sổ có thể kẹp một khoảng 2 lần, nên "đo hai lần" là SÀN, không phải bảo
  đảm**. File:
  `round288-bybit-btc-fails-on-three-windows-and-my-band-predictions-keep-missing.md`.

- **Round 289 (2026-08-30) — HIỆU ỨNG CỬA SỔ CHÍNH LÀ TÍNH KHÔNG DỪNG (non-stationarity),
  và trong các LÁT BẬN của mình, các route "trượt" VƯỢT HẲN vạch Target 3. KHÔNG
  CONTAINER — suy ra từ dữ liệu đã thu.** Thay vì tiếp tục **dự báo** đại lượng đã
  đánh trượt tôi ba vòng (r286-r288), vòng này **GIẢI THÍCH** nó — và không cần chạy
  gì mới: **mọi cửa sổ `--days N` đều LỒNG NHAU và cùng kết thúc ở "bây giờ"**, nên
  **lấy hiệu các số trade tích luỹ liên tiếp sẽ cho rate BÊN TRONG từng lát**.
  | route | lát (ngày trước) | trades | ngày | **/tuần** |
  |---|---|---|---|---|
  | exness BTC | [0,260] / [260,360] | 364 / 117 | 260 / 100 | 9,80 / 8,19 |
  | binance BTC | [0,260] / [260,360] | 350 / 109 | 260 / 100 | 9,42 / 7,63 |
  | exness XAU | [0,260] / [260,360] | 254 / 109 | 260 / 100 | 6,84 / 7,63 |
  | **bybit BTC** | [0,180]/[180,260]/[260,360] | 80/126/38 | 180/80/100 | **3,11 / 11,03 / 2,66** |
  | **binance XAU** | [0,180] / [180,260] | 53 / 82 | 180 / 80 | **2,06 / 7,17** |
  | **bybit XAUT** | [0,260] / [260,360] | 90 / 160 | 260 / 100 | **2,42 / 11,20** |
  **Biên độ giữa các lát:** exness XAU **1,12x**, exness BTC **1,20x**, binance BTC
  **1,24x** — so với **binance XAU 3,48x, bybit BTC 4,14x, bybit XAUT 4,62x**.
  **BA ROUTE CÓ VERDICT DỊCH THEO CỬA SỔ CHÍNH LÀ BA ROUTE CÓ RATE KHÔNG DỪNG.** Hiệu
  ứng cửa sổ **không** phải nhiễu đo và **không** phải artifact công cụ — nó là **rate
  giao dịch THẬT SỰ thay đổi 3,5-4,6 lần giữa các quãng 80-100 ngày liên tiếp**, trong
  khi ba route ổn định chỉ dịch 1,1-1,2 lần và verdict của chúng **giữ nguyên**.
  **KHÔNG phải nhiễu Poisson**: lát nhỏ nhất có 38 trade (±16% ở 1σ), lát lớn nhất 160
  (±8%), so với các cú dao động **250-360%** quan sát được.
  **PHẦN SỬA LẠI CHÍNH CÁCH ĐÓNG KHUNG CỦA TÔI: TRONG CÁC LÁT BẬN, CÁC ROUTE "TRƯỢT"
  VƯỢT HẲN TARGET 3** — binance XAU **7,17/tuần**, bybit BTC **11,03/tuần**, bybit
  XAUT **11,20/tuần**, đều **ở hoặc trên vạch 7**, và **11,03 của bybit BTC là lát bận
  nhất đo được trên BẤT KỲ route nào** trong cả session. Vậy với ba route đó, **"trượt
  Target 3" là tính chất của CỬA SỔ TRUNG BÌNH HOÁ, không phải của route.** r285-r288
  trình bày bảng đội **như trạng thái route**; với **một nửa đội** cách đọc đó **SAI**.
  Phát biểu trung thực: chúng **LUÂN PHIÊN** giữa các quãng gần-ngủ-đông (2,1-3,1/tuần)
  và các quãng bận (7,2-11,2/tuần), còn một cửa sổ đơn lẻ **báo cáo bất kỳ hỗn hợp nào
  nó tình cờ trải qua**. Hai route đạt và exness XAU **không bị ảnh hưởng** — các lát
  của chúng ổn định, và các lát của exness XAU **kẹp lấy vạch** (6,84 và 7,63), đúng
  cách đọc "nằm trên ngưỡng" mà r285 đã cho.
  **GIỚI HẠN:** **KHÔNG** claim các route thưa **sẽ ĐẠT** Target 3 trên horizon dài —
  rate **GỘP** của chúng trên mọi cửa sổ đã đo vẫn **dưới 7**; thứ được chứng minh là
  thiếu hụt **có tính NGẮT QUÃNG, không phải thường trực**, đó là claim **khác và yếu
  hơn**. **KHÔNG** nguyên nhân nào được đưa ra cho tính không dừng — r273-r279 giải
  thích **MỨC** rate của một route (biến động, occupancy, guard) nhưng **không gì ở
  đây** giải thích vì sao rate một route đổi 4 lần giữa các quý, và **tôi không đoán**
  sau r279-r284. Phép lấy hiệu **không chính xác tuyệt đối**: các cửa sổ chạy cách nhau
  vài giờ (**không đáng kể** so với lát 80-100 ngày) nhưng số đếm mỗi lát là **HIỆU CỦA
  HAI PHÉP ĐO** và **thừa hưởng sai số của cả hai**. **KHÔNG** claim bảng r285 phải bị
  rút — **các con số của nó đứng vững**; thứ cần thêm chú giải là việc **đọc một rate
  theo cửa sổ như một tính chất của route** trên ba route không ổn định. File:
  `round289-the-window-effect-is-non-stationarity-and-the-quiet-routes-clear-the-bar-in-their-busy-slices.md`.

- **Round 290 (2026-08-30) — BỊ BÁC: định luật σ² CHỈ đúng theo CHIỀU NGANG (giữa các
  route), nó KHÔNG giải thích rate của chính một route thay đổi theo thời gian. KHÔNG
  CONTAINER.** Test ứng viên hiển nhiên cho câu hỏi mở của r289. r289 giải thích hiệu
  ứng cửa sổ là **tính không dừng** của rate nhưng **từ chối nói vì sao**; ứng viên đã
  sẵn có trong chính session này: **r273/r275** tần suất ~ σ² (đã xác nhận bằng dự
  đoán **liên-route** đăng ký trước, sai số 2,8%), và **r258** biến động **không dừng
  và có CỤM** (tự tương quan lag-1 +0,50 → +0,61 ở p<0,0001 — đó là **đối chứng dương**
  của r258). Nếu cả hai đúng thì rate của một route phải bám theo **biến động CỦA CHÍNH
  NÓ**, từng lát một. **ĐĂNG KÝ TRƯỚC KHI TRUY VẤN BẤT KỲ SỐ BIẾN ĐỘNG NÀO**
  (`precommit_r290.md`): độ dốc `log(rate)` trên `log(σ)` gần **+2**, xác nhận nếu nằm
  trong **1,0-3,0** với tương quan dương rõ ràng; **dải đặt CỐ Ý RỘNG** vì r286-r288
  đã thấy ba dải hẹp trượt.
  **KẾT QUẢ — BỊ BÁC, VÀ KHÔNG SÁT SAO:** n=13 lát, **độ dốc +0,415**, **Pearson
  +0,191**, so với lý thuyết +2 và sàn đăng ký +1,0. Hai phản ví dụ cụ thể:
  | | biến động | rate |
  |---|---|---|
  | bybit BTC [0,180] | 0,12807 | 3,11/tuần |
  | bybit BTC [260,360] | **0,14853 (CAO hơn)** | **2,66/tuần (THẤP hơn)** |
  | bybit XAUT [260,360] | **0,06769 — THẤP NHẤT bảng** | **11,20/tuần — CAO NHẤT đo được** |
  **Lát bận nhất của bybit XAUT lại là thị trường yên ắng nhất của nó.**
  **GIỚI HẠN PHẠM VI ĐƯỢC XÁC LẬP: σ² giải thích khác biệt GIỮA các route, KHÔNG giải
  thích thay đổi BÊN TRONG một route theo thời gian.** Định luật được khớp theo
  **chiều ngang** (sáu route của r273, cặp đăng ký trước của r275, +0,600/+0,900 của
  r285) và **ở đó nó đứng vững**; tôi đã **cách một bước** khỏi việc mở rộng nó sang
  chiều **thời gian**, và dữ liệu **nói không**. Đó là một **ranh giới đáng được ghi
  lại**, và nó có nghĩa **tính không dừng của r289 VẪN CHƯA ĐƯỢC GIẢI THÍCH** — với
  ứng viên hiển nhiên nhất nay **bị LOẠI chứ không phải được giả định**.
  **MỘT QUAN SÁT TÌNH CỜ LÀM SẮC THÊM CÂU ĐỐ:** lát `[180,260]` là **lát biến động
  CAO NHẤT trên CẢ SÁU route** — regime biến động **dùng chung toàn thị trường**, đúng
  hiện tượng cụm r258 đo được. **NHƯNG đỉnh trade-rate thì KHÔNG dùng chung:** bybit
  BTC và binance XAU đạt đỉnh ở `[180,260]` **cùng** biến động, còn bybit XAUT đạt
  đỉnh ở `[260,360]` **ngược** với nó. **BIẾN ĐỘNG DỊCH CHUYỂN CÙNG NHAU GIỮA CÁC
  ROUTE; TRADE RATE THÌ KHÔNG.** Vậy thứ điều khiển tính không dừng của rate **ít nhất
  một phần là ĐẶC THÙ TỪNG ROUTE**, không phải một regime toàn thị trường.
  **GIỚI HẠN:** **KHÔNG** claim σ² sai theo chiều ngang — **không gì ở đây đụng tới**
  r273/r275/r285; thứ bị bác là việc **MỞ RỘNG** định luật sang biến thiên thời gian
  nội-route. **KHÔNG** đưa ra nguyên nhân thay thế nào cho tính không dừng — r279-r284
  là lời nhắc thường trực về chuyện gì xảy ra khi tôi đề xuất cơ chế **nhanh hơn tốc
  độ tôi kiểm được chúng**. **KHÔNG** claim 13 lát là phép test mạnh: bốn route chỉ
  đóng góp điểm gộp `[0,260]`, và gộp phương sai xuyên qua một lần đổi regime **tự nó
  đã hao tổn**; độ dốc +0,415 với r=+0,191 **yếu tới mức một thiết kế sạch hơn cũng
  không cứu được**, nhưng **thiết kế này KHÔNG sạch**. Tính đặc thù route **CHƯA được
  xác lập** — đỉnh biến động dùng chung đối lại đỉnh rate không dùng chung là **MỘT
  quan sát trên sáu route, không phải một phép phân rã**. File:
  `round290-REJECTED-the-sigma-squared-law-is-cross-sectional-only-it-does-not-explain-within-route-time-variation.md`.

- **Round 291 (2026-08-30) — CORRECTION: `exness XAU` trông "ổn định" CHỈ VÌ nó bị
  GỘP. Mọi route tôi đã tách gộp đều hoá ra KHÔNG DỪNG. Hai container (đúng hạn
  mức). Sửa r289; tinh chỉnh r290.** Làm sạch đúng thiết kế r290 tự gắn cờ ("bốn route
  chỉ đóng góp điểm gộp `[0,260]`, và gộp phương sai xuyên qua một lần đổi regime tự
  nó đã hao tổn… **thiết kế này KHÔNG sạch**"). Thêm một run 180 ngày sẽ **tách** một
  `[0,260]` gộp thành `[0,180]` và `[180,260]` sạch. Hai container, **XAU trước**.
  | route | [0,180] | [180,260] | [260,360] | **biên độ** | r289 nói |
  |---|---|---|---|---|---|
  | **exness XAU** | **3,89** | **13,47** | 7,63 | **3,46x** | **1,12x — "ổn định"** |
  | **bybit XAUT** | 1,79 | 3,85 | 11,20 | **6,26x** | 4,62x |
  **`exness XAU` được xếp là ổn định thuần tuý vì `[0,260]` của nó bị GỘP.** Rate thật
  theo lát của nó chạy 3,89 → 13,47 → 7,63, **biên độ 3,46 lần** — nằm **hẳn** trong
  nhóm mà r289 gọi là không ổn định. bybit XAUT còn **tệ hơn**, từ 4,62x lên **6,26x**.
  **HỆ QUẢ CHO PHÉP CHIA CỦA r289:** nhóm "ổn định" nay **chỉ còn HAI** — binance BTC
  1,24x và exness BTC 1,20x — **và CẢ HAI đều CHƯA được tách gộp**.
  | route | biên độ | lát |
  |---|---|---|
  | bybit XAUT | 6,26x | **đã tách** |
  | bybit BTC | 4,14x | **đã tách** |
  | binance XAU | 3,48x | **đã tách** |
  | exness XAU | **3,46x** | **đã tách (vòng này)** |
  | binance BTC | 1,24x | **VẪN GỘP** |
  | exness BTC | 1,20x | **VẪN GỘP** |
  **MỌI ROUTE TÔI ĐÃ TÁCH GỘP ĐỀU HOÁ RA KHÔNG DỪNG. HAI ROUTE DUY NHẤT CÒN TRÔNG ỔN
  ĐỊNH ĐÚNG LÀ HAI ROUTE DUY NHẤT TÔI CHƯA TÁCH.** Đó **không** phải bằng chứng chúng
  ổn định; đó là **cùng một artifact, chưa được kiểm**.
  **PHÉP BÁC CỦA r290 SỐNG SÓT, NHƯNG NÓ ĐÃ BỊ NÓI QUÁ.** Chạy lại hồi quy của r290
  trên các lát sạch hơn: r290 (4 điểm gộp) độ dốc **+0,415**, Pearson **+0,191**; vòng
  này (2 điểm gộp) độ dốc **+0,771**, Pearson **+0,323**. Vẫn **dưới sàn 1,0** tôi
  đăng ký nên **phép bác sống sót** — đúng dự đoán **định hướng** đưa ra trước khi
  chạy — **NHƯNG độ dốc gần như gấp đôi** khi bỏ gộp, nên **"bị bác, và không sát sao"
  của r290 LÀ QUÁ MẠNH**. Ở +0,771 so với lý thuyết +2, σ² mang **MỘT PHẦN** tín hiệu
  nội-route — khoảng **một phần ba** thứ định luật đòi hỏi — **chứ không phải không
  có gì**. **Ghi chú phương pháp:** tôi đặt dự đoán **ĐỊNH HƯỚNG**, không phải một
  dải, sau khi trượt ba dải ở r286-r288; **nó hoạt động như một phép test**.
  **GIỚI HẠN:** **KHÔNG** claim exness BTC và binance BTC không dừng — **chúng CHƯA
  ĐƯỢC TEST**; thứ được chỉ ra là **tính ổn định biểu kiến của chúng dựa trên ĐÚNG
  cách gộp đã tạo ra kết quả "ổn định" GIẢ cho exness XAU**, đó là **lý do để nghi
  ngờ, không phải một phát hiện**, và tách gộp chúng là **việc hiển nhiên của vòng
  sau**. **KHÔNG** claim σ² có sức giải thích nội-route thật: +0,771 với r=+0,323 trên
  15 lát, **bốn trong số đó VẪN GỘP**, là **dương yếu, cùng lắm**, và **không vượt
  được sàn tôi đặt**. **KHÔNG** nguyên nhân nào cho tính không dừng — không đổi từ
  r289, **vẫn chưa giải thích được**. **KHÔNG** claim phát hiện lõi của r289 hỏng —
  điểm trung tâm của nó (hiệu ứng cửa sổ **CHÍNH LÀ** tính không dừng, và các route
  thưa vượt vạch trong lát bận của chúng) được vòng này **CỦNG CỐ**; thứ hỏng là
  **PHÉP PHÂN LOẠI ổn định/không ổn định** của nó. File:
  `round291-CORRECTION-exness-xau-was-stable-only-because-it-was-pooled.md`.

- **Round 292 (2026-08-30) — BỊ BÁC (dự đoán CỦA TÔI): hai route BTC lớn THỰC SỰ ổn
  định. Đội đã tách gộp đầy đủ chia làm HAI NHÓM RÕ RỆT, và KHÔNG theo instrument
  cũng KHÔNG theo biến động. Hai container (đúng hạn mức).** Làm đúng việc r291 nêu
  tên: exness BTC và binance BTC là hai route duy nhất còn `[0,260]` bị gộp và là hai
  route duy nhất còn lại trong nhóm "ổn định" của r289. **Tôi đã dự đoán, theo hướng,
  rằng CẢ HAI sẽ hoá ra KHÔNG DỪNG (biên độ > 2x)** vì cả bốn route đã tách trước đó
  đều vậy (3,46x; 3,48x; 4,14x; 6,26x).
  | route | [0,180] | [180,260] | [260,360] | **biên độ** | r289 nói |
  |---|---|---|---|---|---|
  | exness BTC | 10,31 | 8,66 | 8,19 | **1,26x** | 1,20x |
  | binance BTC | 9,61 | 9,01 | 7,63 | **1,26x** | 1,24x |
  **CẢ HAI THỰC SỰ ỔN ĐỊNH. Dự đoán của tôi bị bác**, và phân loại của r289 **ĐÚNG**
  với hai route này — nó chỉ **sai với exness XAU**. Nghi ngờ của r291 rằng **toàn bộ**
  nhóm ổn định là artifact gộp **là QUÁ RỘNG**, và tôi ghi nhận điều đó **chống lại
  chính lập luận của mình**, không chỉ chống lại dự đoán.
  **BỨC TRANH ĐỘI HOÀN CHỈNH — CHIA HAI NHÓM RÕ RỆT** (cả sáu route nay đã tách gộp):
  | route | biên độ | Target 3 |
  |---|---|---|
  | bybit XAUT | 6,26x | trượt |
  | bybit BTC | 4,14x | trượt |
  | binance XAU | 3,48x | trượt |
  | exness XAU | 3,46x | trượt/ngưỡng |
  | **binance BTC** | **1,26x** | **ĐẠT** |
  | **exness BTC** | **1,26x** | **ĐẠT** |
  **Hai route ở 1,26x, bốn route ở 3,46-6,26x, và KHÔNG có gì ở giữa.** Phép chia
  **sắc nét**, và **cặp ổn định ĐÚNG LÀ cặp đạt Target 3**.
  **PHÉP CHIA NÀY KHÔNG PHẢI DO ĐÂU: KHÔNG phải instrument** — BTC xuất hiện ở **cả
  hai phía** (binance BTC và exness BTC ở 1,26x, còn bybit BTC ở 4,14x); **KHÔNG phải
  biến động** — r276 đo ba route BTC ở 0,14371%, 0,14218% và 0,14406%, **giống nhau
  tới ba chữ số thập phân**, mà hai ổn định một không. Vậy tính ổn định ở đây là một
  tính chất **cấp VENUE**, không phải tính chất của instrument hay thị trường — nhất
  quán với điều bất thường cấp venue khác của r277 **trên chính route đó**: occupancy
  của bybit BTC là **43,3%** so với ~60% của hai route BTC kia.
  **GIỚI HẠN:** **KHÔNG** claim tính ổn định **gây ra** việc đạt Target 3 hay ngược
  lại — sự trùng khớp 2/2 và 4/4 là trên **SÁU route** và **cả hai đại lượng đều tính
  từ CÙNG bộ số trade**, nên chúng **KHÔNG phải hai phép đo độc lập**; đó là **mẫu
  hình đáng ghi nhận, KHÔNG phải một kết quả**. **KHÔNG** claim phép chia là do venue
  — thứ được chỉ ra là instrument và biến động **KHÔNG** giải thích được nó, còn
  "venue" là **thứ CÒN LẠI sau khi loại hai ứng viên trên sáu route**, yếu hơn nhiều
  so với một nguyên nhân đã được chứng minh. **KHÔNG** nguyên nhân nào cho chính tính
  không dừng — không đổi từ r289; r290 đã loại ứng viên σ² và **chưa có gì thay thế**.
  **KHÔNG** claim ba lát là đủ để kết luận tính ổn định: `[0,180]`, `[180,260]` và
  `[260,360]` là **MỘT NĂM**, và một route ổn định qua ba quý **vẫn có thể dịch chuyển
  qua nhiều năm**. File:
  `round292-REJECTED-my-prediction-the-two-btc-majors-are-genuinely-stable-and-the-fleet-splits-cleanly.md`.

- **Round 293 (2026-08-30) — BỊ BÁC: tính ổn định của `exness BTC` là ARTIFACT MỘT
  NĂM. Nhưng hai route lớn ĐI THEO XU HƯỚNG ĐƠN ĐIỆU trong khi bốn route kia DAO
  ĐỘNG — hai loại không dừng KHÁC NHAU. Hai container (đúng hạn mức). Tinh chỉnh
  r292.** Test đúng giới hạn r292 **tự nêu** ("ba lát mỗi route là **MỘT NĂM**; một
  route ổn định qua ba quý **vẫn có thể dịch chuyển qua nhiều năm**). **Đăng ký trước
  khi chạy:** cả hai biên độ **dưới 2x**; **bác nếu route nào chạm 2x** — và tôi ghi
  rõ rằng đà giảm đơn điệu sẵn có khiến đây là **phép test thật, cắt về cả hai phía**,
  và tôi **không** dự đoán "ổn định" chỉ để chạy theo kết quả r292.
  | route | [0,180] | [180,260] | [260,360] | **[360,540]** | biên 1 năm | **biên 18 tháng** |
  |---|---|---|---|---|---|---|
  | **exness BTC** | 10,31 | 8,66 | 8,19 | **4,90** | 1,26x | **2,10x** |
  | binance BTC | 9,61 | 9,01 | 7,63 | **6,26** | 1,26x | **1,53x** |
  **`exness BTC` vượt vạch ở 2,10x. Theo tiêu chí tôi đặt, phát hiện BỊ BÁC:** "thực
  sự ổn định" của r292 là **artifact một năm** trên route đó — **đúng hình dạng lỗi
  r291 tìm thấy ở r289, lùi ra một tầng, và nay tìm thấy TRONG CHÍNH CÔNG VIỆC CỦA
  TÔI lần nữa**. binance BTC dừng ở 1,53x nên phép bác là **một trên hai route**, và
  exness BTC **chỉ vượt ngưỡng sát sao**.
  **PHÁT HIỆN HỮU ÍCH HƠN — HAI LOẠI KHÔNG DỪNG KHÁC NHAU:** cả hai route lớn giảm
  **ĐƠN ĐIỆU** khi lùi về quá khứ (10,31 → 8,66 → 8,19 → 4,90 và 9,61 → 9,01 → 7,63 →
  6,26), tức **đọc xuôi thì rate giao dịch của CẢ HAI đã TĂNG GẤP ĐÔI trong mười tám
  tháng, một cách MƯỢT**. Bốn route kia **KHÔNG** như vậy: bybit XAUT chạy 1,79 →
  3,85 → 11,20 và bybit BTC chạy 3,11 → 11,03 → 2,66 — **KHÔNG đơn điệu, dao động**.
  Vậy "ổn định / không ổn định" là **phép lưỡng phân SAI**:
  | loại | route | dấu hiệu |
  |---|---|---|
  | **xu hướng mượt** | exness BTC, binance BTC | đơn điệu, ~2x qua 18 tháng, **trông ổn định trong mọi cửa sổ ngắn** |
  | **dao động thất thường** | bốn route kia | không đơn điệu, 3,5-6,3x **NGAY TRONG** một năm |
  2,10x của exness BTC và 6,26x của bybit XAUT **đều là "không dừng"** và **KHÔNG phải
  cùng một hiện tượng**.
  **Ý NGHĨA CHO TARGET 3:** hai route đạt đang đạt **TRÊN MỘT XU HƯỚNG ĐANG LÊN**,
  không phải trên một mặt bằng. Lát cũ nhất đo được `[360,540]` của chúng là **4,90**
  và **6,26**/tuần — **cả hai DƯỚI vạch 7** — nên **mười tám tháng trước, với cấu hình
  này, KHÔNG route lớn nào đạt Target 3**. Điều đó **không** đổi verdict hôm nay (vốn
  dựa trên dữ liệu gần đây), nhưng nó có nghĩa các lần đạt là **tính chất của GIAI
  ĐOẠN HIỆN TẠI**, và biên "+27% tới +40%" của r286 **mô tả BÂY GIỜ, không phải cấu
  hình**.
  **GIỚI HẠN:** **KHÔNG** nguyên nhân nào cho xu hướng — không đổi từ r289; r290 đã
  loại ứng viên σ² và **tôi không đề xuất cái nào**. Không claim xu hướng tiếp tục
  trước mốc 540 ngày: **một lát nữa thôi**, các route có **năm năm** dữ liệu còn tôi
  mới đo **mười tám tháng**. **KHÔNG** claim hai loại thực sự khác biệt — bốn điểm đơn
  điệu trên hai route đối lại ba điểm không đơn điệu trên hai route khác là **MÔ TẢ
  SÁU CHUỖI, không phải một phép test**, và binance XAU với exness XAU **quá ít lát để
  phân loại**. **KHÔNG** claim binance BTC ổn định — nó ở 1,53x qua 18 tháng **và đang
  theo xu hướng**; **không vượt ngưỡng của tôi KHÔNG đồng nghĩa với phẳng**. Các lát
  **KHÔNG so sánh trực tiếp được**: `[360,540]` là 180 ngày so với 80-180 của các lát
  khác — **độ rộng lệch nhau mà tôi chưa kiểm soát**. File:
  `round293-REJECTED-stability-was-a-one-year-artifact-but-the-majors-trend-rather-than-swing.md`.

- **Round 294 (2026-08-30) — DATA-ISSUE: xu hướng "xác nhận" trên cả hai route, và
  chính ĐỘ LỚN của nó phơi bày một CONFOUND WARM-UP trong phương pháp tôi dùng từ
  r289. Hai container (đúng hạn mức).** Test giới hạn thực chất r293 để lại ("chưa
  claim xu hướng tiếp tục trước mốc 540 ngày"). Run 720 ngày thêm lát `[540,720]` —
  **rộng 180 ngày, KHỚP CHÍNH XÁC** `[360,540]`, đồng thời xử lý luôn phàn nàn về độ
  rộng lệch của r293. **Đăng ký:** xu hướng tiếp tục nếu `[540,720]` **thấp hơn**
  `[360,540]` trên mỗi route.
  | route | [0,180] | [180,260] | [260,360] | [360,540] | **[540,720]** | đơn điệu | **biên 2 năm** |
  |---|---|---|---|---|---|---|---|
  | exness BTC | 10,31 | 8,66 | 8,19 | 4,90 | **1,83** | CÓ | **5,64x** |
  | binance BTC | 9,61 | 9,01 | 7,63 | 6,26 | **0,39** | CÓ | **24,70x** |
  **Xác nhận trên cả hai, đơn điệu qua năm lát. VÀ ĐÓ CHÍNH LÀ CHỖ TÔI NGỪNG TIN NÓ.**
  **VÌ SAO KẾT QUẢ NÀY LÀM MẤT UY TÍN PHƯƠNG PHÁP:** binance BTC **thêm MƯỜI trade
  qua 180 ngày** (620 → 630 tích luỹ). Với một route đang chạy ~9/tuần hôm nay, đó
  **không phải một giai đoạn chậm** — đó là một route **gần như không giao dịch**.
  **CONFOUND:** mọi run `--days N` **KHỞI ĐỘNG từ N ngày trước**, nên quãng sớm nhất
  của nó **chính là warm-up của run đó** — indicator nạp đầy và, ràng buộc hơn,
  `portfolio_evidence` cần **cả TÁM required interval đồng bộ, KỂ CẢ 1d và 12h**
  (r267). Một run dài hơn **đẩy warm-up của nó lùi xa hơn**, nên lấy hiệu run dài trừ
  run ngắn **đổ đúng quãng bị triệt tiêu đó vào LÁT CŨ NHẤT MỚI** — **chính xác chỗ
  tôi liên tục tìm thấy "xu hướng"**. Một đà giảm đơn điệu khi lùi về quá khứ **đúng
  là thứ artifact này sẽ chế tạo ra**, trên mọi route, **bất kể thị trường làm gì**.
  **THIỆT HẠI LAN TỚI ĐÂU — VÀ KHÔNG TỚI ĐÂU:** nó **KHÔNG** giải thích được mọi thứ
  — các lát cũ nhất của r289 **không bị triệt tiêu đồng loạt**: `[260,360]` của bybit
  XAUT là **11,20/tuần, CAO NHẤT của nó**, và của exness XAU là 7,63 so với lát mới
  nhất 3,89. Nên warm-up **không phải toàn bộ câu chuyện** và các route dao động thất
  thường **không rõ là bị ảnh hưởng**. **NHƯNG nó đe doạ MỌI con số lát-cũ-nhất tôi đã
  báo cáo**, nặng nhất ở các lát 180 ngày nơi r293 và r294 tìm ra "xu hướng". **CÓ RỦI
  RO:** phát hiện xu hướng đơn điệu của r293 và phân biệt "xu hướng vs dao động" của
  nó; 5,64x và 24,70x của vòng này; **lát cũ nhất của MỌI phép so lồng nhau từ r289**.
  **KHÔNG rủi ro:** bảng Target 3 của đội (r285-r288), vốn dùng **rate TOÀN CỬA SỔ**
  chứ không phải lát lấy hiệu, và luận điểm lõi của r289 rằng **hiệu ứng cửa sổ có tồn
  tại**.
  **THỨ SẼ PHÂN XỬ:** một run có cửa sổ **BẮT ĐẦU TRƯỚC HẲN** giai đoạn quan tâm, để
  giai đoạn đó **không còn là warm-up của run** — ví dụ đo `[540,720]` từ cửa sổ **900
  ngày** thay vì 720. Nếu rate **tăng lên** thì xu hướng là artifact; nếu vẫn 0,39 thì
  nó thật. Một container mỗi route, **việc của vòng sau**. Tôi **NỘP** cái này thay vì
  lặng lẽ chạy tiếp, vì **năm vòng "xu hướng tiếp tục" sẽ tích luỹ trên một phương
  pháp mà tôi nay có lý do cụ thể để nghi ngờ**.
  **GIỚI HẠN:** **KHÔNG** claim xu hướng là thật — tiêu chí đăng ký **đã đạt**, và tôi
  **từ chối ghi nhận nó** vì confound sẽ tạo ra **đúng cùng kết quả**. **KHÔNG** claim
  xu hướng là artifact — **cũng chưa xác lập**; việc triệt tiêu **không đồng loạt** ở
  r289 phản bác một hiệu ứng warm-up phổ quát đơn giản. **Độ dài warm-up CHƯA đo** —
  r267 lập được **interval nào** phải đồng bộ, **không phải mất bao lâu**. Các vòng
  trước được **GẮN CỜ CÓ RỦI RO**, **không đồng nghĩa với sai**. File:
  `round294-DATA-ISSUE-the-trend-confirms-but-my-differencing-method-has-a-warm-up-confound.md`.

- **Round 295 (2026-08-30) — BỊ BÁC: confound warm-up. Một warm-up cố định TIÊN ĐOÁN
  ĐƯỜNG CONG NGƯỢC LẠI; cả hai route đều GIẢM đơn điệu. KHÔNG CONTAINER — suy ra từ
  dữ liệu đã thu.** Giải quyết DATA-ISSUE của r294 **mà KHÔNG cần** control run nó đề
  xuất. r294 nộp rằng mọi run `--days N` khởi động từ N ngày trước nên quãng sớm nhất
  là warm-up của chính run đó, và phép lấy hiệu lồng nhau đổ nó vào "lát cũ nhất" mới,
  **chế tạo ra** xu hướng đơn điệu. **CONTROL RUN LÀ KHÔNG CẦN THIẾT:** giả thuyết đó
  đưa ra một **tiên đoán mà dữ liệu ĐÃ CÓ bác bỏ**.
  Nếu warm-up cố định `W` ăn mất phần cũ nhất mỗi cửa sổ thì `cum(N) = r·(N − W)`, nên
  **rate TRUNG BÌNH** `cum(N)/N = r·(1 − W/N)` **PHẢI TĂNG** khi `N` lớn lên (chi phí
  cố định được khấu hao trên cửa sổ dài hơn).
  | cửa sổ | exness BTC (tb /tuần) | binance BTC (tb /tuần) |
  |---|---|---|
  | 180n | **10,31** | **9,61** |
  | 260n | 9,80 | 9,42 |
  | 360n | 9,35 | 8,92 |
  | 540n | 7,87 | 8,04 |
  | 720n | **6,36** | **6,12** |
  **CẢ HAI GIẢM ĐƠN ĐIỆU, Ở MỌI BƯỚC** — **ngược hẳn** thứ một warm-up cố định tạo
  ra. **Warm-up KHÔNG THỂ sinh ra mẫu hình này; nó tác động NGƯỢC CHIỀU.**
  **KIỂM TRA THỨ HAI, ĐỘC LẬP:** bất kỳ `W` khác 0 nào cũng làm rate **GẦN ĐÂY CAO
  HƠN** con số đo được (265 trade trong 180 ngày thành 265 trong 120 ngày nếu W=60),
  tức **NỚI RỘNG** khoảng cách tới 0,39-1,83/tuần của `[540,720]` **chứ không thu hẹp
  nó**. Vậy confound này, nếu có tồn tại, **CỦNG CỐ** xu hướng chứ không giải thích nó
  đi.
  **PHỤC HỒI:** phát hiện xu hướng đơn điệu của r293, phân biệt "xu hướng vs dao động"
  của nó, và các biên hai năm 5,64x / 24,70x của r294. **Cờ AT RISK trên r293 được
  GỠ** và **DATA-ISSUE của r294 được GIẢI QUYẾT LÀ BỊ BÁC**. **KHÔNG phục hồi tới mức
  chắc chắn:** xu hướng nay là **lời giải TỐT NHẤT** cho dữ liệu, **không phải đã được
  chứng minh**; thứ được xác lập **hẹp hơn và chắc hơn** — **một warm-up cố định KHÔNG
  phải lời giải, vì nó tiên đoán SAI DẤU**.
  **r294 ĐÃ ĐÚNG khi nộp thay vì ghi nhận kết quả**, và cái cờ đó tốn **một vòng để
  dựng và một vòng để gỡ** — **đúng là cái giá phải trả**, so với năm vòng tích luỹ
  trên một phương pháp mà tôi có lý do cụ thể để nghi ngờ.
  **GIỚI HẠN:** **KHÔNG** claim warm-up bằng 0 — thứ được chỉ ra là **nó không thể tạo
  ra đường cong quan sát được**; một `W` nhỏ **có thể tồn tại** và sẽ làm các rate gần
  đây **cao hơn một chút** so với báo cáo. Lập luận **giả định warm-up có ĐỘ DÀI CỐ
  ĐỊNH** — đúng bản chất của warm-up indicator và đồng bộ evidence; **tôi không biết**
  cơ chế nào cho một warm-up **co giãn theo độ dài cửa sổ**, **nhưng tôi cũng chưa đi
  tìm**. **KHÔNG** nguyên nhân nào cho chính xu hướng — không đổi từ r289, **vẫn chưa
  giải thích được**, r290 đã loại ứng viên σ². **KHÔNG** claim các route dao động thất
  thường không bị ảnh hưởng bởi thứ gì tương tự — lập luận này chỉ chạy trên **HAI
  ROUTE LỚN**, vì đó là hai route có **năm lát**. File:
  `round295-REJECTED-the-warm-up-confound-a-fixed-warm-up-predicts-the-opposite-curve.md`.

- **Round 296 (2026-08-30) — NỀN ĐO ĐƯỢC XÁC MINH TRONG CODE, và trên các lát
  nội-route SẠCH thì biến động bị ĐẢO NGƯỢC: giai đoạn BIẾN ĐỘNG NHẤT lại là giai đoạn
  ÍT HOẠT ĐỘNG NHẤT. KHÔNG CONTAINER.**
  **TRƯỚC HẾT — XÁC MINH CÁI NỀN TÔI ĐÃ DÙNG SUỐT MƯỜI MỘT VÒNG:** mọi kết quả từ
  r285 **giả định** `one_target` đếm trade trên **TOÀN BỘ** cửa sổ `--days`. Nếu nó
  chỉ báo cáo **một split** (ví dụ 20% holdout) thì phép lấy hiệu tích luỹ **vô
  nghĩa**, và r285-r295 cùng đổ theo. **TÔI CHƯA TỪNG KIỂM.** `main.rs:555-562` nạp
  `portfolio_series` qua `load_portfolio_series(…, args.days, …)` và `main.rs:631-641`
  truyền **toàn bộ** series đó cho `compare_real_portfolio_with_funding`, hàm này
  replay **từ đầu tới cuối** (`portfolio_measurement.rs:105-125`). **KHÔNG split nào
  được áp — `one_target` phủ TOÀN CỬA SỔ.** Nền vững; **tôi ghi lại vì nó từng là GIẢ
  ĐỊNH, không phải điều đã xác minh.** Đồng thời xác nhận: coverage kline 5m là
  **526 913 bar / 1 829 ngày = 288,1/ngày** trên cả hai route lớn — **đầy đủ**, nên
  **lỗ hổng dữ liệu cũng bị loại** khỏi danh sách ứng viên.
  **THỨ HAI — BIẾN ĐỘNG TRÊN CÁC LÁT NỘI-ROUTE SẠCH:** r290 bác σ² cho biến thiên
  nội-route trên 13 lát, **bốn trong đó bị gộp**; r291 làm nhẹ đi thành "độ dốc +0,771
  — có chút tín hiệu". Hai route lớn nay có **NĂM LÁT SẠCH, KHÔNG GỘP, mỗi route, trải
  hai năm** — **dữ liệu tốt nhất câu hỏi này từng có**.
  | lát | binance BTC rate | vol | exness BTC rate | vol |
  |---|---|---|---|---|
  | [0,180] | 9,61 | 0,12773 | 10,31 | 0,12622 |
  | [180,260] | 9,01 | 0,16308 | 8,66 | 0,16149 |
  | [260,360] | 7,63 | 0,14734 | 8,19 | 0,14264 |
  | [360,540] | 6,26 | 0,12123 | 4,90 | 0,12005 |
  | **[540,720]** | **0,39** | **0,16480** | **1,83** | **0,16342** |
  **Trên CẢ HAI route, lát cũ nhất có biến động CAO NHẤT trong năm lát và rate THẤP
  NHẤT.** σ² đòi hỏi **điều ngược lại**. Spearman(rate, vol) = **−0,300** ở mỗi route
  (p=0,68). Và hình dạng **khác nhau về bản chất**: **rate ĐƠN ĐIỆU CHẶT trên cả hai
  route, biến động KHÔNG đơn điệu trên route nào** — nó chạy 0,128 / 0,163 / 0,147 /
  0,121 / 0,165, **dao động** trong khi rate **giảm đều**.
  **BIẾN ĐỘNG KHÔNG PHẢI THỨ ĐIỀU KHIỂN xu hướng hai năm.** Phép bác của r290 **được
  xác nhận trên dữ liệu KHÔNG còn điểm yếu nào r291 đã chỉ ra**, và **phần làm nhẹ của
  r291 KHÔNG sống sót** trên hai route lớn: đây **không** phải "tín hiệu dương yếu",
  đây là **tương quan hạng ÂM với cực trị BỊ ĐẢO**.
  **CÂU HỎI NGUYÊN NHÂN ĐANG Ở ĐÂU:** đã loại, cho xu hướng hai năm trên hai route
  lớn — **warm-up** (r295, sai dấu), **biến động** (vòng này, đảo ngược), và **lỗ hổng
  dữ liệu** (coverage đầy đủ). **Vẫn chưa giải thích được.** Tôi **không** đề xuất ứng
  viên thứ tư; **r279-r284 là lý do thường trực**.
  **GIỚI HẠN:** **Ý NGHĨA THỐNG KÊ** — năm lát cho p hai phía tối thiểu 0,0167, còn
  −0,300 nằm ở **p=0,68**; thứ có trọng lượng ở đây là **CỰC TRỊ BỊ ĐẢO và SỰ LỆCH
  HÌNH DẠNG**, **không phải hệ số**. **KHÔNG** claim biến động vô can theo chiều ngang
  — r273/r275/r285 **vẫn đứng**; đây chỉ nói về **biến thiên thời gian nội-route**,
  đúng phạm vi r290 đã đặt. **KHÔNG** đưa ra nguyên nhân nào. **KHÔNG** claim mẫu hình
  của hai route lớn **tổng quát** sang bốn route dao động — chúng chỉ có **hai hoặc ba
  lát** mỗi route và **không tham gia** phép test này. File:
  `round296-the-measurement-basis-is-verified-and-volatility-is-inverted-on-clean-within-route-slices.md`.

- **Round 297 (2026-08-30) — SỰ SỤP ĐỔ Ở LÁT SÂU NHẤT **KHÔNG** LÀ ARTIFACT CỦA
  PHƯƠNG PHÁP, và `bybit XAUT` bị xếp nhầm là "dao động" trong khi dãy của nó
  ĐƠN ĐIỆU. 2 container (đúng budget), XAU trước.**
  **PHẦN 1 — SỬA r293 BẰNG SỐ ĐÃ CÓ SẴN, KHÔNG CẦN CHẠY GÌ.** r293 dựng lưỡng phân
  "smooth trend vs erratic swing" và nêu thành viên rõ ràng: *"bybit XAUT chạy
  1,79 → 3,85 → 11,20 … **không đơn điệu, dao động**"*. **Dãy của `bybit XAUT` LÀ ĐƠN
  ĐIỆU**: đọc ngược thời gian nó **tăng chặt ở từng bước**; đọc xuôi thời gian, rate
  của route đó **GIẢM** 11,20 → 3,85 → 1,79 một cách trơn tru. Ví dụ này bị đặt vào
  **đúng phía sai** của chính lưỡng phân mà nó được đưa ra để minh hoạ.
  Phân loại lại theo **hình dạng**: exness BTC (10,31/8,66/8,19/4,90) và binance BTC
  (9,61/9,01/7,63/6,26) **đơn điệu — TĂNG xuôi thời gian**; **`bybit XAUT`
  (1,79/3,85/11,20) đơn điệu — GIẢM xuôi thời gian**; binance XAU (2,06/7,17) đơn
  điệu nhưng chỉ hai điểm; exness XAU (3,89/13,47/7,63) và bybit BTC
  (3,11/11,03/2,66) **không đơn điệu**. **BA TRONG SÁU ROUTE ĐƠN ĐIỆU trên mọi lát đã
  đo, không phải hai** — và **một trong ba đi NGƯỢC CHIỀU**. r293 đã **lẫn HÌNH DẠNG
  với CHIỀU**, đọc "đơn điệu" như dấu hiệu của hai route pass Target 3, trong khi một
  route **fail** có cùng hình dạng và **đảo dấu**; cụm "bốn route dao động" của r296
  thừa hưởng lỗi này và phải đọc là **ba**. **KHÔNG** claim điều này khôi phục nhãn
  "ổn định" cho ai, **KHÔNG** claim `bybit XAUT` giống hai route lớn (giảm 6,26x không
  phải tăng 1,5x), và **ba điểm là phép test hình dạng yếu** — xác suất đơn điệu ngẫu
  nhiên từ ba giá trị là 1/3. Ghi lại vì **r293 đã phát biểu ngược với chính số của
  nó**.
  **PHẦN 2 — HAI ROUTE KHÔNG THỂ ĐO ĐẾN ĐỘ SÂU MÀ CÂU HỎI NÀY CẦN.** Truy vấn
  Timescale read-only, coverage 5m: `binance XAU` 75 372 bar, **262 ngày**;
  **`bybit XAUT` 145 621 bar, 506 NGÀY** (bar đầu 2025-04-11); `exness XAU` 354 814
  bar, 1 828 ngày ở 194,1 bar/ngày. **`bybit XAUT` chỉ có 506 ngày lịch sử 5m**: lát
  `[360,540]` **không tồn tại** với nó và `[540,720]` **hoàn toàn ngoài dữ liệu**, nên
  **độ sâu hai năm mà hai route lớn có là BẤT KHẢ THI về mặt cấu trúc** — cách đọc
  "đơn điệu giảm" ở Phần 1 **không bao giờ** mở rộng được tới độ sâu nơi xu hướng của
  hai route lớn được thiết lập. `binance XAU` còn tệ hơn ở 262 ngày và vốn là route
  đóng băng (r207). **PHÂN LOẠI CẢ SÁU ROUTE Ở CÙNG ĐỘ SÂU LÀ BẤT KHẢ THI với dữ liệu
  đang tồn tại.** 194,1 bar/ngày của `exness XAU` so với ~288 của crypto là **đóng cửa
  cuối tuần và phiên của gold CFD**, hiệu ứng r260 đã lượng hoá; tool báo nó là
  `verified_session_gap_candles` (50 004 trên cửa sổ 540 ngày,
  `authoritative_gap_metadata: true`, `unverified_gap_count: 0`) — **đóng cửa thị
  trường đã ghi nhận, KHÔNG phải dữ liệu thiếu**.
  **PHẦN 3 — PHÉP TEST ĐĂNG KÝ TRƯỚC, VÀ NÓ GIẾT CÁI GÌ.** r289-r296 đều dựa trên
  nested differencing, và **lát SÂU NHẤT của hai route lớn là thứ gánh cả câu chuyện**:
  `[540,720]` trả về **0,39/tuần** (binance BTC) và **1,83/tuần** (exness BTC) —
  gần-không, trên **cả hai** route, ở **cùng một độ sâu**. r294 nêu warm-up, r295 bác
  nó bằng hình dạng đường rate trung bình; nhưng một lo ngại **sắc hơn chưa từng được
  test**: **thứ làm suy giảm lát sâu nhất có thể là thuộc tính của CHÍNH ĐỘ SÂU CỬA
  SỔ**, và khi đó **mọi số liệu sâu trong loạt này là artifact** và câu chuyện xu hướng
  đổ theo. `exness XAU` là control đúng: khác instrument, khác broker, khác lịch thị
  trường, năm năm dữ liệu, và dãy chưa bao giờ giống hai route lớn.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** sự sụp đổ **KHÔNG** tái hiện — `[540,720]` của
  `exness XAU` về ở **≥ 4,0/tuần**; **bác bỏ nếu < 2,0/tuần**, khi đó phụ-thuộc-độ-sâu
  thành lời giải dẫn đầu và r289-r296 lâm nguy.
  Hai run chạy cùng lúc, chia sẻ endpoint chính xác (`holdout_end`
  2026-08-28T20:59:59.999Z ở cả hai), config deployed (fractional 0,01/0,02, hold 36,
  fee 5bps, slippage 2bps): **540d = 393 trade tích luỹ, 720d = 526**.
  | lát | trade | span | **rate/tuần** |
  |---|---|---|---|
  | [0,180] | 100 | 180d | 3,89 |
  | [180,260] | 154 | 80d | 13,47 |
  | [260,360] | 109 | 100d | 7,63 |
  | **[360,540]** | **30** | 180d | **1,17** |
  | **[540,720]** | **133** | 180d | **5,17** |
  **`[540,720]` = 5,17/tuần — DỰ ĐOÁN ĐÚNG và GIẢ THUYẾT ARTIFACT BỊ BÁC BỎ**: ở
  **cùng độ sâu**, `exness XAU` giao dịch **13x** rate của binance BTC và **2,8x** của
  exness BTC. **MẠNH HƠN CON SỐ ĐƠN LẺ**: **lát sâu nhất của `exness XAU` KHÔNG phải
  lát thấp nhất của nó** — `[540,720]` gấp **4,4x** `[360,540]`. Một cơ chế làm suy
  giảm phần xa nhất của cửa sổ hẳn sẽ đặt cực tiểu **ở** phần xa nhất; nó đặt cực tiểu
  **cách đó một lát**. **HAI CONTROL từ cùng run:** coverage **đồng đều theo độ sâu**
  (104 639 candle/540d và 139 646/720d = 193,8 và 193,9 bar/ngày — cửa sổ sâu **không**
  mỏng dữ liệu hơn); và **dòng decision dày đặc suốt** (decisions/candles 0,9533 và
  0,9493; riêng `[540,720]` chứa **32 818 DECISION** sinh ra 133 trade, trong khi
  `[360,540]` trải gần đúng cùng số candle và sinh ra **30**) — **CÙNG KHỐI LƯỢNG
  DECISION, SẢN LƯỢNG TRADE KHÁC 4,4x**, khớp r264 và **định vị biến thiên ở PHÍA SAU
  decision, không phải trong decision**.
  **PHẦN 4 — ĐIỀU BẤT NGỜ TÔI KHÔNG DỰ ĐOÁN.** `[360,540]` ở **1,17/tuần** là **lát
  THẤP NHẤT đo được trên bất kỳ route nào** trong loạt này, và nó nằm **GIỮA** hai lát
  bình thường (7,63 trước, 5,17 sau); `exness XAU` nay trải **11,5x** trên năm lát so
  với 3,46x khi có ba lát. **TÔI KHÔNG CÓ LỜI GIẢI**, **không dự đoán trước**, và ghi
  rõ rằng một đoạn 180 ngày sinh 30 trade trên route trung bình ~7/tuần **đúng là loại
  quan sát đã hai lần trong session này hoá ra là LỖI ĐO CỦA CHÍNH TÔI**. Nó dựa trên
  **một** phép hiệu với con số 360d đo ở vòng trước; endpoint drift nhỏ so với lát 180
  ngày nhưng **không bằng không**, và tôi **không** tiêu container thứ ba để đo lại
  360d hôm nay.
  **CÂU HỎI NGUYÊN NHÂN:** đã loại cho xu hướng hai năm của hai route lớn — **warm-up**
  (r295), **biến động** (r296), **lỗ hổng dữ liệu** (r296), và nay **phụ thuộc độ sâu
  của phương pháp differencing** (vòng này). **Vẫn chưa giải thích được**; không đề
  xuất ứng viên thứ năm, **r279-r284 là lý do thường trực**. File:
  `round297-REJECTED-the-deep-slice-collapse-is-not-a-method-artifact-and-bybit-xaut-was-misclassified-as-erratic.md`.

- **Round 298 (2026-08-30) — KHOẢNG NGƯNG 180 NGÀY CỦA `exness XAU` SỐNG SÓT QUA PHÉP
  ĐO LẠI CÙNG NGÀY, và nó **LỚN HƠN** r297 báo cáo; **BIẾN ĐỘNG KHÔNG GIẢI THÍCH ĐƯỢC
  NÓ**. 2 container (đúng budget) + 1 truy vấn Timescale read-only. XAU trước.**
  **ĐÓNG ĐÚNG LỖ HỔNG r297 TỰ NÊU RA VỚI CHÍNH MÌNH:** *"`[360,540]` dựa trên **một**
  phép hiệu với con số 360d đo ở vòng trước… tôi **không** tiêu container thứ ba để đo
  lại 360d hôm nay."* Đáng làm vì **differencing KHUẾCH ĐẠI** drift giữa các vòng: sai
  số nhỏ trong con số tích luỹ trở thành sai số lớn ở lát trừ nó, tệ nhất với lát nhỏ
  nhất — và `[360,540]` chỉ có 30 trade.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** `260d` và `360d` cùng ngày tái hiện 254 và 363 **trong
  ±10%**; bác bỏ nếu lệch >10%, khi đó **mọi lát trong r289-r297 dựng từ số liệu trộn
  vòng phải suy lại**. **KẾT QUẢ: `260d` = 254 hôm nay vs 254 đã ghi — CHÍNH XÁC
  0,00%; `360d` = 374 hôm nay vs 363 — +3,03%. DỰ ĐOÁN ĐÚNG**, cross-round differencing
  vững ở mức độ lớn này. Run cách r297 **18 phút**, nên `360d/540d` nay là **cặp cùng
  ngày**.
  **NHƯNG KHUẾCH ĐẠI LÀ THẬT VÀ NÓ CẮT VÀO CHÍNH SỐ CỦA r297:** dịch chuyển **11
  trade** ở con số tích luỹ 360d đã đẩy `[360,540]` từ 30 trade xuống **19** — **thay
  đổi 37% ở lát từ thay đổi 3% ở đầu vào**. **KHOẢNG NGƯNG KHÔNG PHẢI ARTIFACT CỦA
  DRIFT GIỮA CÁC VÒNG; SỬA DRIFT LÀM NÓ TỆ HƠN.**
  | lát | trade | span | **rate/tuần** | r297 nói |
  |---|---|---|---|---|
  | [0,180] | 100 | 180d | 3,89 | 3,89 |
  | [180,260] | 154 | 80d | 13,47 | 13,47 |
  | [260,360] | 120 | 100d | **8,40** | 7,63 |
  | **[360,540]** | **19** | 180d | **0,74** | **1,17** |
  | [540,720] | 133 | 180d | 5,17 | 5,17 |
  Trải năm lát: **18,2x** (so với 3,46x khi có ba lát, r291). **`[260,360]` = 8,40**
  xuất hiện trong bảng fleet của r289-r297 dưới dạng 7,63 và **từ nay phải đọc là
  8,40**.
  **KHÔNG PHẢI HIỆU ỨNG DỮ LIỆU, COVERAGE HAY NHỊP DECISION:** `[360,540]` có **34 898
  candle / 33 672 decision / 19 trade** so với `[540,720]` **35 007 / 32 818 / 133** —
  **ĐẦU VÀO KHỚP NHAU, SẢN LƯỢNG TRADE KHÁC 7,0x**, hiệu suất trên mỗi decision khác
  **7,2x** (1 trade / 1 772 decision so với 1 / 247). Engine chạy bình thường suốt,
  khớp nhịp decision đồng nhất của r264 ⇒ **sự suy giảm nằm PHÍA SAU decision**.
  **KIỂM CHÉO:** research tool và Timescale **khớp candle count CHÍNH XÁC** (19 751 và
  34 898 trùng khít; 35 007 vs 35 002 ở ranh giới) — tool đọc đúng dữ liệu database
  đang giữ.
  **PHÉP TEST σ² ĐĂNG KÝ TRƯỚC, VÀ NÓ THẤT BẠI.** r273 lập `hold ∝ 1/σ²` theo chiều
  ngang: σ² thấp ⇒ hold dài ⇒ ít close — ứng viên hiển nhiên cho 180 ngày ra 19 trade,
  và nó cho dự đoán **sắc**. **ĐĂNG KÝ TRƯỚC KHI TRUY VẤN:** nếu σ² giải thích được,
  `[360,540]` phải là **lát BIẾN ĐỘNG THẤP NHẤT trong năm lát**.
  | lát | bar | **vol%/5m** | path% | drift% | efficiency | **rate/tuần** |
  |---|---|---|---|---|---|---|
  | [0,180] | 35 166 | 0,10297 | 2 309,4 | −17,07 | 0,00739 | 3,89 |
  | [180,260] | 14 824 | **0,13764** | 1 173,2 | +24,92 | 0,02124 | 13,47 |
  | [260,360] | 19 751 | 0,08080 | 1 069,5 | +21,36 | 0,01997 | 8,40 |
  | **[360,540]** | 34 898 | **0,06538** | 1 512,1 | +21,82 | **0,01443** | **0,74** |
  | **[540,720]** | 35 002 | **0,04940** | 1 192,2 | +16,54 | **0,01387** | **5,17** |
  **`[360,540]` KHÔNG phải lát biến động thấp nhất — `[540,720]` mới là, 0,04940 so
  với 0,06538, VÀ NÓ GIAO DỊCH GẤP 7 LẦN.** Dự đoán thất bại và **σ² BỊ BÁC BỎ** như
  lời giải cho bất thường này. Hai ứng viên nữa rơi ra miễn phí từ cùng bảng và
  **không cái nào tách được hai lát**: **độ lớn xu hướng** (+21,82% vs +16,54% drift —
  tương đương, và drift **lớn hơn** thuộc về lát **bị ngưng**) và **hiệu suất xu
  hướng** (|drift|/path, thước đo r252: **0,01443 vs 0,01387 — lệch dưới 4%**, gần như
  cùng một hình dạng thị trường). Trên cả năm lát Spearman(rate, vol) = **+0,500**,
  **p hai phía chính xác = 0,45**, n=5: đúng dấu σ² dự đoán, **không có ý nghĩa thống
  kê**, và **bị mâu thuẫn ngay tại cực trị** — nơi bất thường sinh sống. r296 đo
  **−0,300** trên hai route lớn BTC; gộp lại: **chưa thiết lập được quan hệ
  rate/biến-động nội-route đáng tin theo bất kỳ chiều nào**, và không hệ số nào được
  đọc như một quan hệ.
  **ĐÃ LOẠI cho khoảng ngưng này:** drift đo giữa các vòng (sửa nó làm bất thường
  **lớn hơn**), coverage dữ liệu (candle khớp, kiểm chéo Timescale), nhịp decision
  (khối lượng decision khớp), biến động (lát σ² thấp nhất giao dịch gấp 7 lần), độ lớn
  xu hướng và hiệu suất xu hướng (đều khớp). **MỌI ĐẠI LƯỢNG QUAN SÁT ĐƯỢC tôi có thể
  tính từ giá hoặc từ counter của chính tool đều KHỚP NHAU giữa một lát 19 trade và
  một lát 133 trade.** **KHÔNG có lời giải và KHÔNG đề xuất lời giải nào**; r279-r284
  là lý do thường trực, và ở đây nó áp dụng **mạnh hơn**, không yếu hơn, chính vì danh
  sách loại trừ nay đã đủ dài để gây cám dỗ. **KHÔNG** claim σ² vô can — luật chiều
  ngang của r273 **nguyên vẹn**; thứ bị bác là σ² như lời giải cho **lát này**, theo
  tiêu chí đăng ký **trước** khi truy vấn. **KHÔNG** claim `[180,260]` 13,47 đã được
  xác minh cùng ngày (đầu vào 180d = 100 trade vẫn là số của vòng trước). **KHÔNG**
  thay đổi verdict Target 3 nào — đây là lát lịch sử. File:
  `round298-REJECTED-the-xau-near-stoppage-is-real-and-bigger-and-volatility-does-not-explain-it.md`.

- **Round 299 (2026-08-30) — HOLD GUARD **KHÔNG** PHẢI NGUYÊN NHÂN. Bỏ guard đi thì
  sụp đổ là **17,3x**, không phải 7,0x. **KHÔNG CONTAINER, KHÔNG SSH** — mọi con số
  lấy từ bốn JSON report r297/r298 đã tạo, cộng một lần đọc code local.**
  r298 để lại khoảng ngưng **đã xác nhận nhưng chưa giải thích**: `[360,540]` cho **19
  trade từ 33 672 decision** trong khi `[540,720]` liền kề cho **133 từ 32 818** —
  đầu vào khớp, sản lượng khác 7,0x. **ỨNG VIÊN HIỂN NHIÊN CÒN LẠI** là đòn bẩy duy
  nhất nằm giữa một decision và một trade: **guard `minimum_hold_decisions = 36`
  (3,00h)** trong `PortfolioConstructionState::construct`. r82 đã lập rằng
  `legacy_selected_rule` chạy **cùng rule trên cùng decision stream với guard bị bỏ
  qua**, nên đóng góp của guard **đo trực tiếp được**.
  **ĐĂNG KÝ TRƯỚC KHI XEM `legacy_selected_rule`:** **H1 (guard là nguyên nhân)** —
  thước đo không-guard **KHÔNG** sụp: rate `[360,540]` của nó nằm trong **hệ số 2** so
  với `[540,720]`; **H2 (thượng nguồn)** — thước đo không-guard **cũng sụp** với hệ số
  tương đương (≥4x), **loại trừ** guard. Tôi dự đoán **H2**, vì guard chặn reversal
  theo ngưỡng **cố định** 36 decision và **không thể** tạo ra dao động 7x giữa hai giai
  đoạn 180 ngày có nhịp decision khớp nhau.
  **THƯỚC ĐO ĐÚNG NHƯ r82 NÓI:** `trade_reduction_fraction` tái tạo
  `1 − one_target/legacy_selected_rule` **chính xác ở cả bốn cửa sổ** (260d 254/328 =
  0,2256; 360d 374/462 = 0,1905; 540d 393/471 = 0,1656; 720d 526/627 = 0,1611) — hai
  thước đo khác nhau **đúng bằng guard và không gì khác**.
  | lát | `one_target` /tuần | **không-guard /tuần** |
  |---|---|---|
  | [260,360] | 8,40 | 9,38 |
  | **[360,540]** | **0,74** (19 trade) | **0,35** (**9 trade**) |
  | [540,720] | 5,17 | 6,07 |
  | **tỉ lệ [540,720]/[360,540]** | **7,0x** | **17,3x** |
  **CHÍN TRADE TRONG 180 NGÀY KHI TẮT GUARD. H1 THẤT BẠI, H2 ĐÚNG, GUARD BỊ LOẠI** —
  bỏ nó đi làm sụp đổ **sâu hơn gấp đôi**. Vậy sự suy giảm nằm **THƯỢNG NGUỒN CỦA
  PORTFOLIO CONSTRUCTION**, trong **dòng target** mà các strategy sinh ra. Đây là một
  thu hẹp thật: r289-r298 đã loại dữ liệu, coverage, nhịp decision, σ², độ lớn xu
  hướng, hiệu suất xu hướng và drift đo — **đều là ĐẦU VÀO**; đây là **phép loại trừ
  đầu tiên BÊN TRONG pipeline**. Ghi thêm: **sức cắn của guard GIẢM đơn điệu** theo độ
  dài cửa sổ (0,2256 → 0,1905 → 0,1656 → 0,1611) — một cơ chế đang **mờ dần** không
  thể là thứ tạo ra bất thường ở cửa sổ sâu.
  **HAI SỰ THẬT VỀ PHƯƠNG PHÁP, cả hai đều bị r289-r298 GIẢ ĐỊNH và chưa từng kiểm.**
  **(1) DÒNG DECISION KHÔNG PHỤ THUỘC ĐỘ DÀI CỬA SỔ.** `main.rs` dựng tập candidate
  bằng `strategies::production_candidates(&instrument)`, **tham số duy nhất là
  instrument identity**: danh sách strategy và mọi ngưỡng (`candle_momentum`
  minimum_move 0,001; `rsi_mean_reversion` 14/30/70; các bổ sung MTF theo instrument)
  đều **HARD-CODE, KHÔNG fit trên train split**. Một run 540 ngày **không phải model
  fit lại**, nó là **cùng một model** trên chuỗi dài hơn. **NẾU candidate được train
  theo từng cửa sổ thì MỌI phép hiệu tích luỹ trong loạt này đã là so sánh HAI MODEL
  KHÁC NHAU** và toàn bộ phương pháp sụp đổ. Nó không sụp.
  **(2) `legacy_grid` TUYỆT ĐỐI KHÔNG ĐƯỢC LẤY HIỆU — và vòng này tôi suýt làm.** Số
  trade tích luỹ của nó **GIẢM** theo độ dài cửa sổ: 3 250 → 5 092 → **4 860** → 6 880.
  Một counter tích luỹ trên các cửa sổ **lồng nhau KHÔNG THỂ giảm**, nên đại lượng này
  **không tích luỹ** theo nghĩa cần thiết. Lý do hiện ngay trong report: `legacy_grid`
  mang **`ledgers: 4`** và tập capital rule `fixed-pct, compounding-pct, fixed-atr,
  compounding-atr` — **không đổi qua cả bốn cửa sổ** nên **không phải** tập rule thay
  đổi, nhưng **hai trong bốn rule COMPOUND EQUITY**. Cửa sổ dài hơn bắt đầu sớm hơn ⇒
  đường equity compound khác ⇒ kích thước và tính khả thi của trade về sau khác theo
  (geometric decay của r90). `risk_rejected_counts.execution_cost` thừa hưởng đúng
  tính không đơn điệu đó: 93 → 181 → **160** → 248. `one_target` và
  `legacy_selected_rule` đều mang `ledgers: 1` dưới sizing `fixed_notional`, **độc lập
  với đường equity**, và **đơn điệu qua cả bốn cửa sổ**: **hai thước đo đó lấy hiệu
  được; grid và các counter risk-rejection thì KHÔNG.**
  **MỘT CẢNH BÁO VÒNG NÀY TỰ TẠO RA CHỐNG LẠI CHÍNH MÌNH:** hold guard **có trạng
  thái** — `decisions_since_target_change` mang theo — nên một run 540 ngày bước vào
  360 ngày cuối với **trạng thái guard khác** một run 360 ngày mới tinh. Lấy hiệu
  `one_target` vì thế mang **confound trạng thái mang-theo** mà thước đo không-guard
  không có; **lần đầu tôi gọi tên nó**. Nó **không** làm yếu kết quả: sụp đổ **lớn
  hơn** trên `legacy_selected_rule` vốn **không có trạng thái guard nào**, nên nếu có
  gì thì carryover đang **che bớt** bất thường.
  **KHÔNG claim:** bất kỳ **nguyên nhân** nào — guard bị loại, **không có gì được lập
  ra thay thế**, và **không đề xuất cơ chế nào**; r279-r284 là lý do thường trực và
  vòng này **đúng là dạng bằng chứng khiến việc suy đoán trở nên cám dỗ**. **KHÔNG**
  claim "thượng nguồn của Portfolio construction" đã **định danh một component** — dòng
  target, các gate role-score, cost gate và bản thân các strategy **đều còn nằm trong
  vùng sống sót và chưa cái nào được test**. **KHÔNG** claim guard vô can nói chung
  (nó cắt 16-23% trade ở mọi cửa sổ; thứ bị bác là guard như lời giải cho **lát này**).
  **KHÔNG** claim phép lấy hiệu `one_target` sạch confound — cảnh báo carryover ở trên
  **vẫn đứng và chưa được lượng hoá**. File:
  `round299-REJECTED-the-hold-guard-is-not-the-cause-and-the-collapse-is-worse-without-it.md`.

- **Round 300 (2026-08-30) — DATA-ISSUE: PORTFOLIO REFIT TRỌNG SỐ **TRÊN MỖI KLINE** TỪ
  HIỆU NĂNG TÍCH LUỸ, NÊN NESTED DIFFERENCING **KHÔNG** CÔ LẬP ĐƯỢC MỘT GIAI ĐOẠN LỊCH.
  TẦNG ALPHA NÓI THỊ TRƯỜNG BÌNH THƯỜNG. KHÔNG CONTAINER, KHÔNG SSH.**
  **Vòng này RÚT LẠI một claim tôi đưa ra ĐÚNG MỘT VÒNG TRƯỚC và làm lung lay một
  phương pháp tôi đã chạy MƯỜI MỘT VÒNG.** r299 kết luận, như một "sự thật về phương
  pháp", rằng **dòng decision không phụ thuộc độ dài cửa sổ**, lập luận từ
  `strategies::production_candidates(&instrument)` chỉ nhận instrument identity.
  **Tập candidate ĐÚNG là tĩnh. TRỌNG SỐ TRÊN NÓ THÌ KHÔNG.**
  `crates/finance-research/src/portfolio_decision_replay.rs:317`, **bên trong vòng lặp
  replay theo từng kline**: `evidence.reweight_from_alpha_performance(&alpha_performance(&ledgers))`.
  Nó chạy **trên MỌI kline**, và `alpha_performance(&ledgers)` là hiệu năng **TÍCH
  LUỸ** của các Alpha ledger **kể từ đầu cửa sổ**;
  `TradingPolicy::reweight_from_alpha_performance` (`trading_modes.rs:517-556`) tính
  lại **cả `interval_weights` lẫn `strategy_weights`** từ đó. Vậy trọng số của
  Portfolio tại **bất kỳ bar lịch nào** là hàm của **mọi thứ xảy ra trước nó trong
  run đó**, và một run 540 ngày với một run 360 ngày mang **trọng số KHÁC NHAU ở MỌI
  BAR CHÚNG DÙNG CHUNG**. Phép tổng quát hoá của r299 từ "candidate tĩnh" sang "dòng
  decision độc lập cửa sổ" **SAI, và tôi rút lại nó**. Đây chính là **vòng lặp trọng
  số tự củng cố** mà **r263** nghi ngờ nhưng chưa định vị — **nay đã định vị**.
  **SỐ LIỆU ĐÃ NÓI ĐIỀU ĐÓ TỪ TRƯỚC VÀ TÔI GIẢI THÍCH SAI:** dưới một dòng decision
  độc-lập-đường-đi, **mọi counter tích luỹ trên cửa sổ lồng nhau phải không giảm** —
  và **hai counter thì giảm**: `legacy_grid.trades` 3 250 / 5 092 / **4 860** / 6 880
  và `risk_rejected_counts.execution_cost` 93 / 181 / **160** / 248. r299 quy cái giảm
  của grid cho hai capital rule **compound equity**; **giải thích đó KHÔNG bao được
  dòng thứ hai**, vì `execution_cost` là **đếm gate, hoàn toàn không có equity sizing**.
  Phụ-thuộc-đường-trọng-số bao được cả hai; **tôi sửa lại quy kết của chính mình**.
  **CONTROL QUYẾT ĐỊNH — TẦNG ALPHA KHÔNG CÓ TRỌNG SỐ.** `strategy_scores` báo cáo
  ledger riêng của từng Alpha strategy, mô phỏng **độc lập với trọng số Portfolio**,
  nên tổng `splits[*].trades` cho một **counter tích luỹ KHÔNG TRỌNG SỐ** trên đúng
  những cửa sổ đó. Nó hành xử **đúng như một counter lồng nhau phải hành xử**: **76/77**
  strategy 5m **đơn điệu chặt**; ngoại lệ duy nhất (`candle_reversion_60bps`,
  76/81/86/**84**) mất **2 trade trên 379 212**; tổng 143 757 / 197 670 / 289 224 /
  379 212, **đơn điệu chặt**. Và nó nói **thị trường hoàn toàn bình thường**:
  | lát | **Alpha /tuần (không trọng số)** | Portfolio `one_target` /tuần | không-guard /tuần |
  |---|---|---|---|
  | [260,360] | **3 773,9** | 8,40 | 9,38 |
  | **[360,540]** | **3 560,4** | **0,74** | **0,35** |
  | [540,720] | **3 499,5** | 5,17 | 6,07 |
  **Rate Alpha lệch tối đa 4,5% quanh trung bình. Rate Portfolio trên ĐÚNG những lát
  đó lệch 7x, và 17x khi bỏ hold guard.** Bảy mươi bảy strategy sinh ra lượng hoạt động
  **hoàn toàn bình thường** trong `[360,540]`. **Khoảng ngưng, dù là gì, KHÔNG PHẢI
  THỊ TRƯỜNG IM LẶNG**, và nó **chỉ xuất hiện trong thước đo phụ thuộc đường đi** —
  đó là **chữ ký của một ARTIFACT ĐO ĐẠC**, không phải hiện tượng thị trường.
  **CÁI GIÁ:** **nested differencing KHÔNG hợp lệ cho counter tầng Portfolio.** Coi là
  **KHÔNG ĐÁNG TIN, CHỜ SUY LẠI** mọi Portfolio slice rate trong **r289-r299** và mọi
  thứ dựng trên chúng: khung "window effect là non-stationarity", phân loại "trend vs
  swing", xu hướng hai năm của hai route lớn, các spread fleet, và chính khoảng ngưng
  của `exness XAU`. Các vòng **bác bỏ** lời giải cho những con số đó — warm-up (r295),
  biến động (r296), phụ thuộc độ sâu (r297), σ² (r298) — đang test **một đại lượng có
  thể không đo một giai đoạn lịch**; các phép bác **không vì thế mà SAI**, nhưng chúng
  nhắm vào một mục tiêu **tôi không còn bảo chứng được**.
  **CÁI CÒN SỐNG:** **kết quả chính của r299** (nó so `one_target` với
  `legacy_selected_rule` **TRONG CÙNG MỘT RUN**, nơi reduction fraction là 16-23% ở mọi
  cửa sổ — guard **không thể** tạo hiệu ứng 7x hay 17x bất kể differencing ra sao);
  **xác minh của r296** rằng `one_target` đo toàn bộ cửa sổ `--days` (một run, không
  ảnh hưởng); **đo lường production LIVE** (r207, r259-r260 — trade đóng thật trong
  Redis, không replay, không trọng số, không differencing); **kết quả tầng Alpha**; và
  mọi **dữ kiện coverage**.
  **GIỚI HẠN CÔNG CỤ LỘ RA:** **không có cách nào** lấy được số trade Portfolio theo
  từng giai đoạn mà so sánh được giữa các giai đoạn — lấy hiệu các run lồng nhau thì
  **không hợp lệ**, còn chạy các cửa sổ **cùng độ dài với ngày kết thúc khác nhau** thì
  được, nhưng **CLI KHÔNG CÓ cờ as-of/end-date**, mọi cửa sổ đều kết thúc ở "now". So
  sánh thời gian nội-route ở tầng Portfolio **hiện KHÔNG ĐO ĐƯỢC** bằng công cụ này —
  **ghi nhận như một giới hạn, không phải việc để lên lịch**.
  **KHÔNG claim: ĐỘ LỚN của confound.** Tôi đã chỉ ra trọng số phụ thuộc đường đi và
  hai counter vi phạm tính lồng nhau; tôi **CHƯA** đo được các quỹ đạo trọng số phân kỳ
  bao nhiêu, và **không có cách nào** với công cụ hiện tại. **Có thể** confound nhỏ với
  riêng `one_target` và khoảng ngưng có phần thật. **Tôi không biết**, và đó chính là
  lý do các con số bị đánh dấu **KHÔNG ĐÁNG TIN** chứ không phải **RÚT BỎ**. **KHÔNG**
  claim các phát hiện slice Portfolio là **SAI** — chúng **chưa được xác minh**; một
  khuyết tật phương pháp **lấy đi bằng chứng, nó không lập ra điều ngược lại**. **KHÔNG**
  claim nguyên nhân nào cho khoảng ngưng — **ít hơn bao giờ hết**, vì chính **sự tồn
  tại** của nó nay đang bị nghi ngờ. **KHÔNG** claim tầng Alpha là thước đo thay thế
  cho Target 3: nó đếm trade của 77 Alpha strategy, **không liên quan** tới tần suất
  trade Portfolio, và **tuyệt đối không được trích dẫn như vậy**. Banner
  "UNRELIABLE — METHOD DEFECT (Round 300)" đã gắn lên r289 và r291-r299. File:
  `round300-DATA-ISSUE-portfolio-weights-refit-every-kline-so-nested-differencing-does-not-isolate-a-calendar-period.md`.

- **Round 301 (2026-08-30) — KHOẢNG NGƯNG CỦA `exness XAU` NẰM **DƯỚI SÀN NHIỄU CỦA
  CHÍNH PHƯƠNG PHÁP**. Thêm **MỘT NGÀY** vào cửa sổ làm số trade Portfolio đổi **−7**.
  2 container (đúng budget), XAU trước.**
  **LỖ HỔNG r300 ĐỂ LẠI:** r300 tìm ra trong code rằng Portfolio refit trọng số trên
  **mỗi kline**, rồi khép lại bằng giới hạn thành thật: *"tôi **chưa** đo được các quỹ
  đạo trọng số phân kỳ bao nhiêu, và **không có cách nào** với công cụ hiện tại."*
  **CÓ MỘT CÁCH, và nó không cần cờ as-of: NHIỄU LOẠN ĐIỂM BẮT ĐẦU CỬA SỔ MỘT NGÀY.**
  Một run `--days 361` chính là run `--days 360` cộng **một ngày** ở đầu sâu; theo rate
  cục bộ (0,74/tuần) ngày đó đáng **0,106 trade**, năm ngày đáng **0,529**. Mọi dịch
  chuyển lớn hơn — và trên hết là **dịch chuyển ÂM** — là confound **đo trực tiếp**.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** nếu confound không đáng kể với `one_target` thì
  `|trades(361) − 374| ≤ 1` và `|trades(365) − 374| ≤ 2`, cả hai **không âm**.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | decision | Alpha 5m |
  |---|---|---|---|---|---|---|---|
  | 360 | 69 741 | **374** | 462 | 5 092 | 181 | 66 079 | 197 670 |
  | **361** | 70 005 | **367** | 455 | 4 928 | 176 | 66 332 | 198 335 |
  | **365** | 70 578 | **392** | 481 | 5 262 | 198 | 67 347 | 199 805 |
  | 540 | 104 639 | 393 | 471 | 4 860 | 160 | 99 751 | 289 224 |
  **MỘT NGÀY THÊM VÀO LÀM `one_target` ĐỔI −7 TRADE**: một cửa sổ **lớn hơn hẳn** trả
  về **BẢY TRADE ÍT HƠN** — vi phạm tính đơn điệu lồng nhau, **trên đúng counter tôi
  từng tin là an toàn**. Năm ngày thêm vào làm nó đổi **+18**. **Dự đoán thất bại cả
  về DẤU lẫn ĐỘ LỚN**, ở khoảng **70x** nội dung kỳ vọng của dữ liệu thêm vào.
  `legacy_selected_rule` dịch **đồng bộ** (−7, +19) nên đây **không phải** hold guard;
  `legacy_grid` (−164, +170) và `execution_cost` (−5, +17) cũng vậy, **đúng như r300
  dự đoán**.
  **CONTROL ALPHA HÀNH XỬ ĐÚNG NHƯ MỘT COUNTER SẠCH PHẢI HÀNH XỬ:**
  | nhiễu loạn | candle thêm | Alpha trade thêm | **Alpha/candle** | **`one_target`/candle** |
  |---|---|---|---|---|
  | +1 ngày | 264 | +665 | **2,519** | **−0,0265** |
  | +5 ngày | 837 | +2 135 | **2,551** | **+0,0215** |
  Tầng Alpha không-trọng-số **giãn nở theo dữ liệu thêm ở tốc độ hằng 2,519-2,551
  trade/candle — nhất quán tới 1,2% — và không bao giờ âm**. Thước đo Portfolio trên
  **đúng cùng dữ liệu thêm đó** cho **dấu ngược nhau**. Vậy **những ngày thêm vào là
  bình thường; PHẢN ỨNG của thước đo Portfolio với chúng thì không** — loại bỏ cách
  đọc thay thế rằng bản thân dữ liệu thêm vào là bất thường. (Số candle mỗi ngày khác
  nhau — 264 cho ngày đầu so với 167/ngày trung bình trên năm ngày — vì gold CFD đóng
  cửa cuối tuần; chuẩn hoá theo candle khử được nó, **đó là lý do tỉ số Alpha ổn định
  đến vậy**.)
  **SÀN NHIỄU, VÀ NÓ NUỐT CÁI GÌ:** trên ba độ dài cửa sổ chênh nhau **tối đa năm
  ngày**, `one_target` trả về **367 / 374 / 392** — trải **25 TRADE**, **6,7%** số tích
  luỹ. Lát `[360,540]` mà r297-r299 theo đuổi là **19 trade**; tính lại theo từng base
  **đều hợp lệ như nhau**: 393−367 = **26 trade** (1,01/tuần), 393−374 = **19** (0,74),
  393−392 = **1 TRADE** (0,04). **TOÀN BỘ BẤT THƯỜNG DI CHUYỂN TỪ 26 TRADE XUỐNG 1 TUỲ
  THEO TÔI CHỌN NGÀY NÀO LÀM ĐIỂM BẮT ĐẦU CỬA SỔ.** Nó không phải hiệu ứng nhỏ đo thiếu
  chính xác — nó **nằm trọn trong nhiễu do chính phương pháp sinh ra**, và **tôi đã tiêu
  r297, r298, r299 để giải thích nó**.
  **KHOẢNG NGƯNG BỊ BÁC BỎ.** Tiêu đề của r298 — *"khoảng ngưng là thật và lớn hơn"* —
  **SAI**, và chữ "lớn hơn" đến từ **chính cái nhiễu nay làm nó biến mất**; banner
  **WITHDRAWN** đã gắn lên file đó.
  **HỆ QUẢ CHO PHẦN CÒN LẠI CỦA LADDER, PHÁT BIỂU DÈ DẶT:** mọi lát Portfolio lấy hiệu
  **nhỏ hơn khoảng 25 trade** trên cửa sổ tương đương là **chưa được thiết lập** —
  `binance BTC` `[540,720]` là **10 trade**, `exness BTC` khoảng **47**. Tôi đo sàn
  trên `exness XAU` và **KHÔNG** chuyển con số sang BTC (mật độ bar khác, tập candidate
  khác, rate gấp ~1,6x, và **chưa chạy** cùng phép nhiễu loạn ở đó); **thứ chuyển được
  là CƠ CHẾ**, vốn độc lập instrument — trọng số refit trên mỗi kline trong mọi run.
  **KHÔNG claim:** sàn nhiễu cho bất kỳ route nào khác `exness XAU` (một route, một cặp
  nhiễu loạn); rằng confound **bị chặn** bởi 25 trade — **ba điểm cách nhau ≤5 ngày
  không chặn được gì**, khoảng cách 180 ngày có thể tệ hơn nhiều và tôi **không đo**;
  rằng đo lường **một-cửa-sổ** ở tầng Portfolio bị ảnh hưởng — **một run là nhất quán
  nội tại**, thứ hỏng là **so sánh các run KHÁC ĐỘ DÀI**, nên verdict Target 3 từ cửa
  sổ đơn và từ trade log Redis live **nguyên vẹn**; bất kỳ nguyên nhân nào cho biến
  thiên mà ladder tưởng như cho thấy — **có thể chẳng có gì để giải thích**. Tầng Alpha
  **không** đo gì về Target 3 và **không được trích dẫn** như vậy — ở đây nó chỉ là
  control chứng minh dữ liệu thêm vào là bình thường. File:
  `round301-REJECTED-the-near-stoppage-is-below-the-method-noise-floor-one-extra-day-moves-the-count-by-seven-trades.md`.

- **Round 302 (2026-08-30) — KHUYẾT TẬT ĐO **PHỤ THUỘC ROUTE**: `binance BTC` VỮNG và
  ladder của nó **TÁI HIỆN CHÍNH XÁC**, còn Target 3 của `exness XAU` **KHÔNG VỮNG**
  trước lựa chọn cửa sổ. 2 container (đúng budget).**
  **CHẠY ĐÚNG GIỚI HẠN r301 TỰ NÊU:** *"tôi đo sàn trên `exness XAU` và **KHÔNG**
  chuyển con số sang BTC… **chưa chạy** cùng phép nhiễu loạn ở đó."*
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** nếu pass Target 3 của hai route lớn là vững, rate của
  `binance BTC` ở `--days 260` và `261` chênh **< 2%**; bác bỏ ở **≥ 5%**.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | decision | Alpha 5m |
  |---|---|---|---|---|---|---|---|
  | 260 | 74 878 | **350** | 502 | 4 584 | 52 | 74 338 | 315 121 |
  | **261** | 75 166 | **355** | 503 | 4 578 | 53 | 74 626 | 316 454 |
  Một ngày thêm: **+288 candle, +288 decision, `one_target` +5**. Nội dung thật của một
  ngày ở ~9,6/tuần là **1,37 trade**, nên confound đóng góp khoảng **+3,6** — so với
  **−7** của `exness XAU` trên một ngày chỉ đáng **0,11 trade**.
  **RATE TARGET 3: 9,423/tuần ở 260 ngày và 9,521 ở 261 — chênh +1,04%. DỰ ĐOÁN ĐÚNG.**
  Cả hai vượt vạch 7/tuần **+34,6%** và **+36,0%** — biên **lớn hơn một bậc độ lớn** so
  với độ nhạy nhiễu loạn. Vi phạm lồng nhau **vẫn hiện diện** (`legacy_grid` 4 584 →
  **4 578**) nên cơ chế r300 có ở đây, **chỉ là NHỎ**.
  **VÀ LADDER ĐÃ GHI TÁI HIỆN CHÍNH XÁC:** r292 ghi `binance BTC` `[0,180]` = 9,61/tuần
  và `[180,260]` = 9,01/tuần, hàm ý tích luỹ 260 ngày là **350,1 trade**; run độc lập
  hôm nay trả về **350**. So với `exness XAU` có số 360 ngày dịch 363 → 374 (+3,03%)
  giữa các vòng, **đây là một CHẤT LƯỢNG ĐO KHÁC HẲN**.
  **TARGET 3 CỦA `exness XAU` KHÔNG VỮNG TRƯỚC LỰA CHỌN CỬA SỔ** (từ ba run của r301,
  không container mới): 360d → **7,272/tuần** (biên **+3,9%**), 361d → **7,116**
  (**+1,7%**), 365d → **7,518** (**+7,4%**). Route **pass cả ba** — nhưng **trải do
  lựa chọn cửa sổ là 5,5%, LỚN HƠN biên nhỏ nhất (+1,7%)**. Một `--days` tuỳ ý khác đi
  một chút **có thể đẩy route xuống dưới vạch**.
  **Tệ hơn, phụ thuộc ĐỘ DÀI cửa sổ lớn hơn nhiễu nhiễu-loạn rất nhiều:**
  | route | cửa sổ ngắn | cửa sổ dài hơn | tỉ lệ |
  |---|---|---|---|
  | **`exness XAU`** | 180d → **3,89/tuần** | 360d → **7,27/tuần** | **1,87x** |
  | `binance BTC` | 180d → 9,61/tuần | 260d → 9,42/tuần | **0,98x** |
  **`exness XAU` báo cáo gần GẤP ĐÔI rate tuỳ theo bạn hỏi cửa sổ dài bao nhiêu;
  `binance BTC` báo cáo cùng một rate tới 2%.** Với `exness XAU` **KHÔNG TỒN TẠI rate
  Target 3 backtest độc lập cửa sổ**, và trích dẫn một con số mà không kèm `--days` là
  **vô nghĩa**; với `binance BTC` rate **ổn định trên mọi độ dài cửa sổ đã đo**.
  **ĐIỀU NÀY LÀM GÌ VỚI BANNER CỦA r300:** r300 đánh dấu **mọi** lát Portfolio lấy hiệu
  trong r289-r299 là không đáng tin, **đồng loạt**. Đó là quyết định đúng với bằng
  chứng khi đó và **tôi không rút lại** — nhưng nay nó **quá rộng ở một phía**: trên
  **`binance BTC`** khuyết tật hiện diện nhưng **nhỏ** (~1% độ nhạy rate, tái hiện
  ladder chính xác, biên Target 3 gấp 30 lần nhiễu), nên số của nó **tốt hơn mức "không
  đáng tin"** — chúng **được chứng thực ở mức cửa-sổ-đơn**. Trên **`exness XAU`**
  khuyết tật **nghiêm trọng** (phản ứng một ngày **ÂM**, trải 5,5%, swing 1,87x), nên
  mọi thứ lấy hiệu ở route đó **vẫn không đáng tin**, và pass Target 3 sát vạch của nó
  phải đọc là **CHƯA XÁC ĐỊNH**, không phải pass. **Cơ chế độc lập instrument — trọng
  số refit trên mỗi kline trong mọi run — nhưng ĐỘ LỚN của nó thì rõ ràng KHÔNG**, và
  r300 không có cách nào biết điều đó từ một route.
  **KHÔNG claim:** **TẠI SAO** khuyết tật nhỏ ở route này và lớn ở route kia (BTC có
  288 bar/ngày so với 194 của XAU, nhiều trade hơn, tập candidate khác — tôi **không
  test cái nào** và **không đề xuất cơ chế**); rằng **lát sâu lấy hiệu** của
  `binance BTC` nay đáng tin (một phép nhiễu loạn ở 260/261 ngày **không nói gì** về
  khoảng cách 180 ngày ở 540-720 — lát `[540,720]` 10 trade của r293 **vẫn chưa được
  thiết lập**); bất cứ điều gì về `exness BTC`, `bybit BTC`, `bybit XAUT`, `binance XAU`
  (**bốn trên sáu route chưa hề chạy phép nhiễu loạn nào**); rằng `exness XAU` **FAIL**
  Target 3 — nó **pass cả ba cửa sổ đã đo**, điều được claim là **biên nhỏ hơn độ nhạy
  cửa sổ của chính phép đo**, nên pass **chưa được thiết lập**, chứ không phải bị bác;
  rằng route nào có lãi (`binance BTC` cho realized_pnl −3,40 và −3,56). File:
  `round302-NEEDS-MORE-RESEARCH-the-defect-is-route-dependent-binance-btc-is-robust-and-exness-xau-is-not.md`.

- **Round 303 (2026-08-30) — MẬT ĐỘ BAR **KHÔNG** GIẢI THÍCH ĐƯỢC KHUYẾT TẬT.
  `bybit XAUT` chạy 24/7 như BTC mà vẫn dịch **+8,57%** chỉ vì một ngày. Confound là
  một nhiễu loạn **TUYỆT ĐỐI GẦN NHƯ CỐ ĐỊNH**. 2 container (đúng budget), XAU trước.**
  **CÂU HỎI r302 ĐỂ NGỎ:** r302 thấy khuyết tật **nhỏ** trên `binance BTC` (+1,04%) và
  **lớn** trên `exness XAU` (phản ứng **âm**, trải 5,5%), và nói thẳng *"tôi không test
  cái nào và không đề xuất cơ chế"* — hai route khác nhau ở **bốn** thứ bị trộn lẫn:
  instrument, mật độ bar (288 vs 194/ngày), số trade, tập candidate. **`bybit XAUT`
  tách được hai trong số đó**: nó là **XAU** như Exness nhưng giao dịch **24/7 ở 288,0
  bar/ngày** như BTC, **không có session gap**.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** nếu mật độ bar và tính liên tục phiên điều khiển độ lớn
  khuyết tật, `bybit XAUT` sẽ hành xử như `binance BTC` — nhiễu loạn một ngày làm rate
  Target 3 đổi **< 2%** và `one_target` đổi **không âm**; **bác bỏ ở ≥ 5%**. Tôi **dự
  đoán kết cục khuyết-tật-nhỏ**, lập luận rằng 385 session gap của `exness XAU` liên
  tục làm mất đồng bộ các required interval khiến hiệu năng Alpha tích luỹ — thứ điều
  khiển trọng số — nhiễu hơn.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | decision | Alpha 5m |
  |---|---|---|---|---|---|---|---|
  | 260 | 74 878 | **89** | 104 | 1 688 | 28 | 74 342 | 216 999 |
  | **261** | 75 166 | **97** | 113 | **2 262** | 35 | 74 630 | 217 823 |
  **KẾT QUẢ — BỊ BÁC BỎ:** một ngày thêm cho **`one_target` +8** so với nội dung kỳ
  vọng **0,34 trade** — **vượt 23 lần** — và **rate Target 3 đổi +8,57%**, **trên ngưỡng
  bác bỏ của tôi**. `legacy_grid` dịch 1 688 → **2 262**, **+34% chỉ từ một ngày**.
  **MẬT ĐỘ BAR VÀ TÍNH LIÊN TỤC PHIÊN BỊ BÁC** như lời giải: một route XAU 24/7 với
  288,0 bar/ngày và **không session gap nào** lại có khuyết tật **tương đối LỚN HƠN**
  route 194 bar/ngày đầy gap.
  **BA ROUTE CHO THẤY ĐIỀU GÌ:**
  | route | instrument | bar/ngày | trade | **Δ 1 ngày** | kỳ vọng | **Δ rate** | **tác động tương đối** |
  |---|---|---|---|---|---|---|---|
  | `binance BTC` | BTC | 288,0 | 350 | **+5** | 1,37 | +1,04% | **1,4%** |
  | `exness XAU` | XAU | 193,8 | 374 | **−7** | 0,11 | −2,14% | **1,9%** |
  | **`bybit XAUT`** | **XAU** | **288,0** | **89** | **+8** | 0,34 | **+8,57%** | **9,0%** |
  **Nhiễu loạn TUYỆT ĐỐI gần như giống nhau trên cả ba route — 5, 7 và 8 trade — trải
  qua khoảng 4x số trade, 1,5x mật độ bar, hai instrument và cả hai market type.** Thứ
  khác nhau là **cái mà nhúm trade cố định đó là một phần CỦA**. Vậy khuyết tật đọc như
  một **nhiễu tuyệt đối gần cố định vài trade**, mà **thiệt hại TỈ LỆ NGHỊCH với số
  trade route đó tạo ra** — đây là **MÔ TẢ BA ROUTE, KHÔNG PHẢI ĐỊNH LUẬT** (ba điểm,
  không sai số, mỗi route một phép nhiễu loạn) — nhưng nó giải thích được tương phản
  của r302 **mà không cần mật độ bar**, và nó khiến **route ít trade nhất là route KHÓ
  ĐO NHẤT**.
  **QUY TẮC THỰC DỤNG CHO TARGET 3:** một verdict Target 3 đáng tin **đúng khi biên
  vượt vạch LỚN HƠN độ nhạy nhiễu loạn của route đó**:
  | route | rate | biên trên 7/tuần | độ nhạy | verdict |
  |---|---|---|---|---|
  | `binance BTC` | 9,42/tuần | **+34,6%** | 1,04% | **pass — AN TOÀN** |
  | **`bybit XAUT`** | **2,40/tuần** | **−65,8%** | 8,57% | **fail — AN TOÀN** |
  | `exness XAU` | 7,12-7,52/tuần | **+1,7% … +7,4%** | 5,5% | **CHƯA XÁC ĐỊNH** |
  Khuyết tật **tương đối lớn** tự nó **không** vô hiệu hoá một verdict: độ nhạy 8,57%
  của `bybit XAUT` **không thể bắc qua khoảng cách 65,8%**, nên **fail của nó AN TOÀN
  NGANG pass của `binance BTC`**. **Chỉ route sát vạch mới nguy hiểm** — hiện tại là
  `exness XAU` **một mình**. Và `exness XAU` **còn tệ hơn r302 ghi nhận**: số 260 ngày
  (254, r289) cho **6,84/tuần — DƯỚI vạch** — trong khi số 360 ngày cho **7,27/tuần,
  TRÊN vạch**. **Cùng một route pass hay fail chỉ tuỳ theo hỏi cửa sổ dài bao nhiêu**;
  "chưa xác định" nếu có gì thì là **rộng lượng**.
  **KHÔNG claim:** rằng confound là đại lượng tuyệt đối **CỐ ĐỊNH** (5-8 trên ba route;
  route thứ tư có thể phá vỡ, và tôi **chưa** test nó co giãn theo **ĐỘ LỚN** của nhiễu
  loạn ra sao); **BẤT KỲ CƠ CHẾ nào** cho độ lớn (mật độ bar và liên tục phiên nay bị
  loại; số trade **phù hợp** với dữ liệu nhưng **chưa được test như một nguyên nhân**;
  khác biệt tập candidate **hoàn toàn chưa xem xét**); rằng fail Target 3 của
  `bybit XAUT` là mới (r289-r292 đã có — cái **mới** là fail đó **VỮNG TRƯỚC KHUYẾT
  TẬT**); bất cứ điều gì về `exness BTC`, `bybit BTC`, `binance XAU` — **ba trên sáu
  route vẫn chưa có phép nhiễu loạn nào**; rằng lát sâu lấy hiệu nào được cứu (không
  đổi so với r300-r302); rằng `exness XAU` **FAIL** Target 3 — verdict là **CHƯA XÁC
  ĐỊNH**, không phải pass cũng không phải bác. `bybit XAUT` realized_pnl −0,2506 và
  −0,3081 — **vẫn lỗ, như mọi route**. File:
  `round303-REJECTED-bar-density-does-not-explain-the-defect-and-a-target3-verdict-is-safe-only-when-margin-exceeds-sensitivity.md`.

- **Round 304 (2026-08-30) — CONFOUND **KHÔNG** PHẢI "VÀI TRADE CỐ ĐỊNH": NÓ ĐẠT
  **−20**, và VERDICT TARGET 3 CỦA `exness XAU` **LẬT** trên sáu cửa sổ cùng ngày.
  2 container (đúng budget), XAU trước.**
  **GIỚI HẠN r303 TỰ NÊU:** r303 mô tả khuyết tật là *"một nhiễu **tuyệt đối gần cố
  định** vài trade"* (5-8 trên ba route) và nói rõ khoảng trống: *"tôi **chưa** test nó
  co giãn theo **ĐỘ LỚN** của nhiễu loạn ra sao."*
  **PHÉP TEST SẠCH KHÔNG CẦN ƯỚC LƯỢNG RATE THẬT** — thứ đang bị tranh cãi: **một
  counter tích luỹ lồng nhau BẮT BUỘC phải không giảm theo `--days`, bất kể thị trường
  đã làm gì**. Vậy: kéo dài ladder và **đếm vi phạm**. **ĐĂNG KÝ TRƯỚC KHI CHẠY:** nếu
  confound là dai dẳng chứ không phải một lần ở 361 ngày, **ít nhất một lần giảm nữa sẽ
  xuất hiện** trong ladder 360/361/365/370/380.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | Alpha 5m |
  |---|---|---|---|---|---|---|
  | 360 | 69 741 | **374** | 462 | 5 092 | 181 | 197 670 |
  | 361 | 70 005 | **367** | 455 | 4 928 | 176 | 198 335 |
  | 365 | 70 578 | **392** | 481 | 5 262 | 198 | 199 805 |
  | **370** | 71 891 | **391** | 490 | 5 382 | 192 | 203 017 |
  | **380** | 73 545 | **371** | 462 | 5 160 | 173 | 207 381 |
  | counter | dãy | vi phạm |
  |---|---|---|
  | **`one_target`** | 374 / 367 / 392 / 391 / 371 | **3** — `−7`, `−1`, **`−20`** |
  | `legacy_selected_rule` | 462 / 455 / 481 / 490 / 462 | 2 — `−7`, `−28` |
  | `legacy_grid` | 5 092 / 4 928 / 5 262 / 5 382 / 5 160 | 2 — `−164`, `−222` |
  | **Alpha 5m** | 197 670 → 207 381 | **0** |
  | candle | 69 741 → 73 545 | **0** |
  **BA TRÊN BỐN BƯỚC VI PHẠM TÍNH LỒNG NHAU trên `one_target`, và vi phạm lớn nhất là
  −20 TRADE, ở bước lớn nhất.** Counter Alpha không-trọng-số và candle count **đơn điệu
  chặt** trên cả năm — **đúng như bắt buộc**.
  **"VÀI TRADE CỐ ĐỊNH" CỦA r303 BỊ BÁC BỎ:** thang ~7 trade tôi dùng từ r301 là **SÀN
  QUAN SÁT ĐƯỢC Ở NHIỄU LOẠN NHỎ**, không phải kích thước của confound; trên cửa sổ 380
  ngày, −20 trade là **5,4% số đếm**, và **mọi độ nhạy theo route ghi nhận cho tới nay
  đều là CẬN DƯỚI**. Tôi **KHÔNG** claim một định luật co giãn: vi phạm chạy −7 ở +1
  ngày, −1 ở +5 ngày, −20 ở +10 ngày — **không đơn điệu theo kích thước bước**. Thứ
  **được** thiết lập: nhiễu **ít nhất 20 trade**, và cái lớn nhất tìm được đến từ bước
  lớn nhất, nên **coi nó bị chặn bởi một nhúm là SAI**.
  **HỆ QUẢ QUAN TRỌNG — VERDICT TARGET 3 LẬT.** Sáu phép đo **cùng ngày**, **cùng
  route**, **cùng config**, chỉ khác một `--days` tuỳ ý:
  | `--days` | trade | **rate/tuần** | biên trên 7,0 | verdict |
  |---|---|---|---|---|
  | 260 | 254 | 6,838 | **−2,3%** | **FAIL** |
  | 360 | 374 | 7,272 | +3,9% | pass |
  | 361 | 367 | 7,116 | +1,7% | pass |
  | 365 | 392 | 7,518 | +7,4% | pass |
  | 370 | 391 | 7,397 | +5,7% | pass |
  | **380** | **371** | **6,834** | **−2,4%** | **FAIL** |
  **Bốn pass, hai fail. Rate trải 6,834 → 7,518 — 9,5% của trung bình — và vạch 7/tuần
  NẰM BÊN TRONG khoảng đó.** Đây **không còn là một cảnh báo về biên mỏng**; đây là
  **chứng minh** rằng verdict Target 3 của `exness XAU` **do độ dài cửa sổ mà người
  phân tích tình cờ chọn quyết định**. r302 và r303 ghi route này là **CHƯA XÁC ĐỊNH**;
  phân loại đó **đúng** và nay **dựa trên bằng chứng trực tiếp** thay vì suy ra từ độ
  nhạy.
  **CÁI KHÔNG ĐỔI:** quy tắc biên-so-với-độ-nhạy của r303 **sống sót**, với độ nhạy của
  `exness XAU` **sửa từ 5,5% lên 9,5%**: `binance BTC` +34,6% so với 1,04% (pass — an
  toàn, biên vẫn gấp **33 lần** độ nhạy); `bybit XAUT` −65,8% so với 8,57% (fail — an
  toàn); `exness XAU` −2,4%…+7,4% so với **9,5%** (**chưa xác định — đã chứng minh**).
  **Không route nào khác được đo lại với nhiễu loạn lớn hơn**, và cả hai nên được **giả
  định lớn hơn** con số một-ngày của chúng, đúng như `exness XAU` đã cho thấy.
  **KHÔNG claim:** một **định luật co giãn** (năm điểm không lập được dạng hàm — chỉ
  **cận dưới 20 trade** là được thiết lập); rằng **20 là cực đại** (chưa thử nhiễu loạn
  lớn hơn, và **khoảng cách 180 ngày — đúng thang mà r289-r299 thực sự dùng — VẪN CHƯA
  ĐƯỢC ĐO**); rằng `binance BTC` hay `bybit XAUT` sẽ hành xử như vậy dưới nhiễu loạn
  +10 ngày (**không route nào được chạy lại**; độ nhạy của chúng là con số **một ngày**
  nên là **cận dưới**, không phải trường hợp xấu nhất); rằng `exness XAU` **FAIL**
  Target 3 — nó **pass 4/6 và fail 2/6**, verdict là **CHƯA XÁC ĐỊNH** và nay **được
  chứng minh chứ không phải suy ra**; rằng lát lấy hiệu lịch sử nào được cứu hay bị kết
  án thêm ngoài r300-r303. File:
  `round304-REJECTED-the-confound-is-not-a-fixed-few-trades-it-reaches-20-and-the-xau-target3-verdict-flips-with-window-choice.md`.

- **Round 305 (2026-08-30) — ĐỘ NHẠY CỦA `binance BTC` GẤP **15 LẦN** CON SỐ MỘT-NGÀY.
  Pass Target 3 sống sót mọi cửa sổ đã đo, nhưng **"biên an toàn 33x" ĐÃ BIẾN MẤT**.
  2 container (đúng budget).**
  *Phạm vi BTC: `exness XAU` nay đã đo ở sáu độ dài cửa sổ và verdict đã chốt là **chưa
  xác định**, còn `binance BTC` mang **pass an toàn duy nhất còn lại của fleet** — nên
  budget đi về đó.*
  **GIỚI HẠN r304 ĐÃ NÊU:** *"`binance BTC` và `bybit XAUT` không được chạy lại với
  nhiễu loạn +10 ngày; độ nhạy của chúng là **con số một ngày nên là CẬN DƯỚI**, không
  phải trường hợp xấu nhất."* r302 đo route này ở **+1,04%** một ngày và r303 dựng quy
  tắc fleet trên đó: biên **+34,6%** so với độ nhạy 1,04% — **đệm 33x**, *"pass — an
  toàn"*. Nếu 1,04% là sàn thì cái đệm đó **chưa biết**.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** pass là vững — **mọi** cửa sổ trong ladder 260/261/270/280
  ở **trên 7/tuần**, **và** trải rate **dưới 10%** trung bình. Bác bỏ nếu **có** cửa sổ
  dưới 7/tuần **hoặc** trải vượt **15%**.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | Alpha 5m | **rate/tuần** | biên |
  |---|---|---|---|---|---|---|---|---|
  | 260 | 74 878 | 350 | 502 | 4 584 | 52 | 315 121 | 9,423 | +34,6% |
  | 261 | 75 166 | 355 | 503 | 4 578 | 53 | 316 454 | 9,521 | +36,0% |
  | **270** | 77 758 | **313** | 439 | 4 086 | 22 | 327 558 | **8,115** | **+15,9%** |
  | **280** | 80 638 | **334** | 475 | 4 438 | 28 | 339 918 | 8,350 | +19,3% |
  | counter | dãy | vi phạm |
  |---|---|---|
  | **`one_target`** | 350 / 355 / **313** / 334 | 1 — **`−42`** ở 261→270 |
  | `legacy_selected_rule` | 502 / 503 / 439 / 475 | 1 — `−64` |
  | `legacy_grid` | 4 584 / 4 578 / 4 086 / 4 438 | 2 — `−6`, `−492` |
  | **Alpha 5m** | 315 121 → 339 918 | **0** |
  | candle | 74 878 → 80 638 | **0** |
  **PHẢI BÁO CÁO CẢ HAI NỬA CỦA DỰ ĐOÁN:** **pass GIỮ ĐƯỢC — 4/4 cửa sổ vượt vạch**,
  yếu nhất 8,115/tuần; **NHƯNG trải là 15,9% trung bình, TRÊN ngưỡng bác bỏ 15%** của
  tôi, nên **dự đoán BỊ BÁC**, và độ nhạy **gấp 15,3 lần** con số một-ngày 1,04%.
  Một bước **+9 ngày** làm số đếm **rơi 42 trade** trong khi nội dung thật của chín ngày
  là khoảng **+12**; từ 260→280 ngày nội dung thật là **+26,9 trade** còn thước đo trả
  về **−16** — **chênh 43 trade**, trên đúng route mà r302 gọi là "hành xử tốt". Control
  Alpha và candle count **vẫn đơn điệu chặt, không vi phạm nào**, như mọi vòng trong
  loạt này.
  **ĐIỀU NÀY LÀM GÌ VỚI QUY TẮC FLEET:** quy tắc của r303 (verdict đáng tin khi biên >
  độ nhạy) **sống sót**; thứ thay đổi là **con số đưa vào nó**:
  | route | biên trên vạch | **độ nhạy (biết rõ nhất)** | biên ÷ độ nhạy | verdict |
  |---|---|---|---|---|
  | `binance BTC` | +15,9%…+36,0% | **15,9%** (4 cửa sổ, span ≤20 ngày) | **1,0x** *(từng là 33x)* | **pass — không còn thoải mái** |
  | `bybit XAUT` | −65,8% | ≥8,57% (**chỉ một ngày**) | ≤7,7x | fail — an toàn **dựa trên một cái sàn** |
  | `exness XAU` | −2,4%…+7,4% | 9,5% (6 cửa sổ, ≤20 ngày) | 0,8x | chưa xác định — đã chứng minh |
  **Biên nhỏ nhất và độ nhạy của `binance BTC` nay LÀ CÙNG MỘT CON SỐ.** Pass **không
  bị bác** — mọi cửa sổ đã đo đều vượt vạch — nhưng nó **không còn được che bởi một cái
  đệm rộng**, và một độ dài cửa sổ tôi chưa thử **có thể** đưa nó về sát vạch.
  **"Fail an toàn" của `bybit XAUT` nay dựa trên ĐÚNG loại sàn một-ngày vừa tỏ ra nhỏ
  hơn 15 lần trên BTC.** Tôi **không** claim fail của nó đang bị nghi ngờ — khoảng cách
  65,8% là rộng — **chỉ** rằng cái đệm 7,7x được tính trên một con số **thuộc loại đã
  thất bại một lần**. **Hệ số tăng trưởng KHÔNG dự đoán được** từ những gì tôi có:
  `binance BTC` tăng **15,3x** từ một ngày lên span 20 ngày, trong khi `exness XAU` chỉ
  tăng **1,7x** qua cùng phần mở rộng — **hai điểm, không mô hình**.
  **KHÔNG claim:** rằng `binance BTC` **fail** Target 3 hay sắp fail — **4/4 cửa sổ
  pass**; điều được claim là **biên an toàn r302-r303 báo cáo được tính từ một con số
  nhỏ hơn 15 lần**, không phải verdict đã đổi. **Không** claim 15,9% là độ nhạy **thật**
  của route (trải trên bốn cửa sổ span 20 ngày; span rộng hơn chưa thử, và r304 đã cho
  thấy các con số này **chỉ tăng**). **Không** claim **định luật co giãn** nào cho hệ số
  tăng trưởng. **Không** claim fail của `bybit XAUT` bị nghi ngờ — **nó chưa được test**;
  cảnh báo là về **xuất xứ** của cái đệm, không phải verdict. **Ba trên sáu route**
  (`exness BTC`, `bybit BTC`, `binance XAU`) **vẫn chưa có phép nhiễu loạn nào.**
  realized_pnl −3,399 / −3,562 / −1,764 / −1,852 — **âm ở mọi cửa sổ**; PnL "cải thiện"
  ở cửa sổ dài **không có nghĩa gì**, đó đúng là phép so sánh chéo-cửa-sổ không đáng tin
  mà cả loạt này nói về. File:
  `round305-REJECTED-binance-btc-sensitivity-is-15x-the-one-day-figure-and-its-safe-margin-is-gone.md`.

- **Round 306 (2026-08-30) — TRADE LOG LIVE LÀ THƯỚC ĐO TARGET 3 **DUY NHẤT** MÀ
  r300-r305 KHÔNG CHẠM TỚI ĐƯỢC. Nó nói fleet **KHÔNG ĐÓNG MỘT TRADE NÀO TRONG 27-38
  GIỜ**, và **worker HOÀN TOÀN KHOẺ**. KHÔNG CONTAINER; chỉ evidence production
  read-only phạm vi hẹp.**
  **TẠI SAO ĐI HƯỚNG NÀY:** r300-r305 đã lập rằng **mọi** con số Target 3 từ backtest
  phụ thuộc một `--days` tuỳ ý (`exness XAU` pass 4 cửa sổ, fail 2; đệm của
  `binance BTC` sập từ 33x xuống 1,0x khi mở rộng nhiễu loạn). r301 đã gọi tên thước đo
  **miễn nhiễm** với tất cả: **durable Redis trade log** — vị thế đóng thật, không
  replay, không trọng số thích nghi, **không lựa chọn cửa sổ** (r207, r259-r260).
  **PHẦN 1 — PHÉP ĐO LIVE.** Cửa sổ log **2026-08-27T14:39:59Z → 2026-08-30T04:10:39Z
  = 61,5 h (2,56 ngày)**. **Cardinality index và payload KHỚP CHÍNH XÁC** trên cả sáu
  route (12/12, 9/9, 9/9, 3/3, 3/3, 3/3) ⇒ **invariant append r207 kiểm vẫn giữ**.
  | route | close | **live /tuần** | giờ từ close cuối | tuổi checkpoint |
  |---|---|---|---|---|
  | `binance BTC/USDT` | 4 | **10,93** | 36,1 | 0,01 h |
  | `exness BTC/USD` | 3 | **8,19** | 36,1 | 0,01 h |
  | `bybit BTC/USDT` | 3 | **8,19** | 27,2 | 0,01 h |
  | `binance XAU/USDT` | 1 | 2,73 | 35,8 | 0,01 h |
  | `exness XAU/USD` | 1 | 2,73 | 38,0 | **28,18 h** |
  | `bybit XAUT/USDT` | 1 | 2,73 | 38,0 | 0,01 h |
  **`binance XAU` đã tạo close durable ĐẦU TIÊN**: r207 thấy key này **vắng mặt** và
  route đóng băng từ 2025-12-26; nay nó có 3 entry, `exit_at` 2026-08-28T16:19:59Z,
  trong khi `recent_klines` của checkpoint **vẫn kết thúc ở tháng 12/2025**. **Cặp đôi
  này được GHI NHẬN, KHÔNG được giải thích.**
  **PHẦN 2 — FLEET ĐÃ NGỪNG ĐÓNG, VÀ ĐÓ **KHÔNG** PHẢI OUTAGE.** Close cuối của mọi
  route rơi vào **dải hai giờ ngày 2026-08-28, 14:09-16:19Z**, trừ `bybit BTC` kéo tới
  2026-08-29T00:59Z. Từ đó: **27 đến 38 giờ không một close nào**. Tính đồng thời qua
  ba broker, hai instrument và cả hai market type là **dáng dấp một sự kiện mức hệ
  thống**, nên việc đầu tiên phải kiểm là worker còn sống không. **Chúng còn sống:
  NĂM TRÊN SÁU checkpoint được ghi TRONG VÒNG 40 GIÂY trước lúc đọc** (`updated_at`
  2026-08-30T04:10:00-04:10:03Z). Cái thứ sáu, `exness XAU`, **cũ 28,18 giờ** — và đó
  là **đóng cửa cuối tuần của CFD, KHÔNG phải lỗi**: Kafka offset cuối của nó nằm trên
  topic `market.kline.v2.exness.cfd.xau.usd.**1d**` lúc 2026-08-29T00:00:04Z, **đúng
  điều một worker gold CFD làm khi thị trường đóng** — r102 đã ghi đúng chữ ký này là
  **false alarm**. **VẬY SỰ NGƯNG TRỆ KHÔNG PHẢI OUTAGE WORKER**: thứ đang giữ fleet
  nằm im nằm ở **đường decision-to-target của Portfolio**, trên một hệ thống có **data
  plane khoẻ mạnh**.
  **PHẦN 3 — LIVE SO VỚI BACKTEST** *(kỳ vọng hình thành trước khi đọc nhưng phát biểu
  LỎNG, không phải một ngưỡng đăng-ký-trước như các vòng khác, nên ghi là **kỳ vọng,
  không phải phép test**)*:
  | route | **live** | backtest | tỉ lệ |
  |---|---|---|---|
  | `binance BTC/USDT` | 10,93/tuần | 8,12-9,52 | **1,15x-1,35x** |
  | `bybit XAUT/USDT` | 2,73/tuần | 2,40-2,60 | **1,05x-1,14x** |
  | `exness XAU/USD` | 2,73/tuần | 6,83-7,52 | **0,36x-0,40x** |
  **Hai trên ba khớp sát.** `exness XAU` lệch — nhưng cửa sổ live của nó **chứa một cuối
  tuần** và route chỉ giao dịch **67,4%** thời gian lịch (194,1/288 bar/ngày); điều chỉnh
  theo giờ mở cửa cho **4,05/tuần**, tỉ lệ **0,54x-0,59x** — vẫn thấp, **nay trong hệ số
  hai**. Đáng nói cẩn thận: **route nhạy-cửa-sổ nhất của backtest cũng là route mà
  backtest khớp với live TỆ NHẤT** — một cuối tuần và một close **không** là bằng chứng
  cho một khoảng lệch hệ thống, nhưng nó **đúng chiều** mà công việc về window-sensitivity
  dự đoán.
  **CÁI NÀY KHÔNG CHỐT ĐƯỢC TARGET 3.** **Mười ba close trên sáu route** là đúng phản
  đối r207 nêu khi có chín, và cơn hạn 27-38 giờ nghĩa là các rate trên **vẫn đang
  GIẢM** theo từng giờ chứ chưa hội tụ. **Cái nó LẬP ĐƯỢC** là **thước đo này lành
  lặn** — cardinality khớp, close đếm được, worker sống rõ ràng, checkpoint cũ duy nhất
  có lời giải lành tính — nên **mọi phát biểu Target 3 về sau nên đến từ ĐÂY**, không
  phải từ một cửa sổ `--days`.
  **KHÔNG claim:** verdict Target 3 nào (**1-4 close mỗi route**, một **baseline** đúng
  như r207 nói khi có chín); rằng cơn hạn 27-38 giờ là **bất thường** — với rate của
  chính `binance BTC` thì khoảng trống 36 giờ **không hiếm** riêng lẻ; thứ **bất thường**
  là **năm route dừng trong vòng hai giờ của nhau**, và tôi **chưa** test điều đó với một
  null model. **KHÔNG** claim **nguyên nhân** nào cho cơn hạn — worker còn sống chỉ
  **loại trừ outage và không gì khác**; vị thế có đang mở không, target có đơn giản là
  chưa đổi không, hay một gate đang bắn — **đều chưa được kiểm vòng này**. **KHÔNG**
  claim `binance XAU` đã hết đóng băng. **KHÔNG** claim gì về các đuôi `recent_klines`
  tôi trích bằng grep — **phương pháp đó lấy lần xuất hiện CUỐI theo thứ tự
  serialization, không phải bar MỚI NHẤT qua các interval**, nên các đuôi có vẻ cũ trên
  vài route là **KHÔNG DIỄN GIẢI ĐƯỢC** từ evidence này và **không kết luận nào được
  rút ra**. File:
  `round306-NEEDS-MORE-RESEARCH-the-live-log-is-the-window-free-target3-measure-and-the-fleet-has-not-closed-a-trade-in-27-38-hours.md`.

- **Round 307 (2026-08-30) — NO-CHANGE: CƠN HẠN TOÀN FLEET LÀ **SÁU VỊ THẾ ĐANG MỞ VÀ
  NĂM GATE ĐANG CHẶN**. Mọi lý do gate **tái tạo được từ code**. **KHÔNG có defect.**
  KHÔNG CONTAINER; chỉ evidence production read-only phạm vi hẹp.**
  **CÂU HỎI r306 ĐỂ NGỎ:** *"vị thế có đang mở không, target có đơn giản là chưa đổi
  không, hay một gate đang bắn — **đều chưa được kiểm** vòng này."*
  **ĐĂNG KÝ TRƯỚC KHI ĐỌC:** cơn hạn là **vị thế đang được GIỮ**, không phải entry bị
  chặn ⇒ các route hiện **position KHÔNG flat**. Tôi dự đoán vậy vì close đến từ target
  change, và một gate chặn cả sáu route qua ba broker cùng lúc sẽ là **một loại sự kiện
  khác hẳn**.
  | route | position | `decisions_since_target_change` | đã giữ | giờ từ close cuối | **khoảng flat** | gate |
  |---|---|---|---|---|---|---|
  | `binance BTC/USDT` | **long** | 342 | 28,5 h | 36,1 | 7,6 h | BLOCK `trend_score_below_threshold` |
  | `exness BTC/USD` | **short** | 330 | 27,5 h | 36,1 | 8,6 h | **PASS** `multi_timeframe_gate_passed` |
  | `bybit BTC/USDT` | **short** | 330 | 27,5 h | 27,2 | ~0 | BLOCK `entry_trend_conflict` |
  | `binance XAU/USDT` | **short** | 156 | 13,0 h | 35,8 | 22,8 h | BLOCK `entry_trend_conflict` |
  | `exness XAU/USD` | **short** | 39 | 3,2 h | 38,0 | — | BLOCK `stale_timeframe_evidence:15m` |
  | `bybit XAUT/USDT` | **short** | 102 | 8,5 h | 38,0 | 29,5 h | BLOCK `entry_score_below_threshold` |
  **CẢ SÁU ROUTE ĐANG GIỮ MỘT VỊ THẾ MỞ** — một long, năm short, mọi `reason` đều là
  `multi_timeframe_gate_passed`. **Fleet KHÔNG nhàn rỗi, nó ĐANG ĐẦU TƯ TOÀN PHẦN**;
  dự đoán đúng.
  **(1) HOLD GUARD KHÔNG DÍNH DÁNG GÌ:** `minimum_holding_decisions` = 36 ở mọi route,
  **counter nhỏ nhất là 39**, lớn nhất 342 — mọi route **đã qua guard** và tự do đổi
  target; `waiting_after_protective_exit` = `false` khắp nơi.
  **(2) NĂM TRÊN SÁU GATE ĐANG CHẶN, MỖI CÁI MỘT LÝ DO KHÁC NHAU** — và **mọi lý do tái
  tạo CHÍNH XÁC** từ `trading_modes.rs:842-857` với `minimum_role_score = 0.1`:
  | route | \|entry\| | \|trend\| | dấu | lý do báo cáo | tái tạo? |
  |---|---|---|---|---|---|
  | `binance BTC` | 0,12782 ✓ | **0,01048 ✗** | ngược | `trend_score_below_threshold` | **có** |
  | `exness BTC` | 0,12863 ✓ | 0,13263 ✓ | cùng | `multi_timeframe_gate_passed` | **có** |
  | `bybit BTC` | 0,11464 ✓ | 0,27510 ✓ | **ngược** | `entry_trend_conflict` | **có** |
  | `binance XAU` | 0,10674 ✓ | 0,28236 ✓ | **ngược** | `entry_trend_conflict` | **có** |
  | `exness XAU` | **0,01611 ✗** | 0,74762 ✓ | cùng | `stale_timeframe_evidence:15m` | staleness thắng |
  | `bybit XAUT` | **0,00899 ✗** | 0,42172 ✓ | cùng | `entry_score_below_threshold` | **có** |
  Cái thứ sáu là **guard staleness cuối tuần** trên gold CFD — đúng chữ ký lành tính
  r306 truy tới offset Kafka `.1d` lúc thị trường đóng. **LOGIC GATE LIVE KHỚP CODE
  CHÍNH XÁC.**
  **(3) VẬY CƠN HẠN CÓ MỘT LỜI GIẢI ĐẦY ĐỦ VÀ TẺ NHẠT:** close cần một target mới,
  target mới cần gate pass, **năm gate đang từ chối**, vị thế cứ mở và không trade nào
  đóng. **KHÔNG CÓ GÌ HỎNG.**
  **MỘT QUAN SÁT LIVE LÀM NHẸ MỘT VÒNG TRƯỚC:** r284 ghi rằng flat exit được theo sau
  bởi **tái vào lệnh NGAY LẬP TỨC, 100% số lần**. Khoảng flat live ở đây là **7,6 h**
  (`binance BTC`), **8,6 h** (`exness BTC`) và **29,5 h** (`bybit XAUT`); chỉ `bybit
  BTC` vào lại ngay tại close. **Đó KHÔNG phải "ngay lập tức".** Phát hiện của r284 đến
  từ **replay**, và r300 đã lập rằng so sánh replay chéo cửa sổ là không vững; đây là
  bằng chứng **live** chỉ theo chiều ngược lại. **Ghi như một quan sát trên BA route,
  KHÔNG phải một phép bác**: khoảng flat suy ra từ `decisions_since_target_change × 5
  phút`, **giả định decision 5 phút không gián đoạn** — giả định đó **KHÔNG hợp lệ** cho
  `exness XAU` (đóng cửa cuối tuần, worker cũ 28 h) và `binance XAU` (dữ liệu checkpoint
  kết thúc 2025-12-25), nên **hai dòng đó bị loại khỏi claim**.
  **KHÔNG claim:** rằng cơn hạn là **bình thường hay bất thường** — nó **được GIẢI
  THÍCH**, không đồng nghĩa với **được KỲ VỌNG**, và **không null model nào được chạy**;
  nguyên nhân nào cho việc năm close **dồn vào dải hai giờ** ngày 2026-08-28 (một cú
  chuyển động thị trường chung qua vàng và BTC là **hợp lý nhưng CHƯA ĐƯỢC TEST**); rằng
  khoảng flat **bác bỏ** r284 — ba route, **một snapshot**, và khoảng flat tính từ **một
  counter decision** chứ không phải timestamp; verdict Target 3 nào — **không đổi so với
  r306**, 13 close là baseline; rằng các gate được **hiệu chỉnh đúng** — thứ được xác
  minh là chúng **hành xử ĐÚNG NHƯ ĐƯỢC VIẾT**; `minimum_role_score = 0.1` có phải
  ngưỡng đúng hay không là **câu hỏi khác** và **không được xem xét**. Sample đã thêm
  vào `research/quant/samples/position-state-samples.csv` và
  `research/quant/samples/signal-state-samples.csv`. File:
  `round307-NO-CHANGE-the-drought-is-six-open-positions-and-five-blocked-gates-not-a-defect.md`.

- **Round 308 (2026-08-30) — `minimum_role_score` LÀ MỘT ĐÒN BẨY YẾU: **giảm 30%
  KHÔNG mở khoá được gì**, đưa về **0** cũng chỉ mở dưới một phần tư. **Ba phần tư số
  block là XUNG ĐỘT DẤU.** KHÔNG CONTAINER, KHÔNG SSH.**
  **CÂU HỎI r307 HOÃN LẠI:** *"`minimum_role_score = 0.1` có phải ngưỡng đúng hay không
  là câu hỏi khác và **không được xem xét**."* Đây là **đòn bẩy tần suất hiển nhiên** —
  năm trên sáu route bị gate chặn ở lần đọc cuối — **NHƯNG gate có BA điều kiện**
  (`trading_modes.rs:850-857`) và **ngưỡng chỉ chạm được HAI**:
  | điều kiện | dòng | nhạy ngưỡng? |
  |---|---|---|
  | `entry_score.abs() < minimum_role_score` | 850 | **có** |
  | `trend_score.abs() < minimum_role_score` | 853 | **có** |
  | `entry_score` và `trend_score` **ngược dấu** | 857 | **KHÔNG** |
  Một block do **ngược dấu** **không thể** sửa ở **bất kỳ ngưỡng nào** — nên **trần của
  đòn bẩy đo được mà KHÔNG cần chạy gì**.
  **ĐĂNG KÝ TRƯỚC KHI TÍNH:** ngưỡng là **đòn bẩy YẾU** — **dưới một nửa** số block đã
  ghi sẽ pass **ngay cả ở `minimum_role_score = 0`**.
  **PHÉP ĐO** trên 26 sample tích luỹ (r265-r270, r307): **4 pass, 22 BLOCK** —
  `entry_trend_conflict` **10**, `entry_score_below_threshold` 7,
  `trend_score_below_threshold` 4, staleness 1. Bỏ staleness còn **21 block**; ở ngưỡng
  0 hai phép kiểm độ lớn **biến mất** và một block **chỉ** clear **khi hai score CÙNG
  DẤU**:
  | ngưỡng | block được mở | tỉ lệ |
  |---|---|---|
  | **0,100** (đang deploy) | 0 | — |
  | 0,090 | **0** | 0,0% |
  | **0,070** (giảm 30%) | **0** | **0,0%** |
  | 0,050 (giảm một nửa) | 2 | 9,5% |
  | 0,040 | 3 | 14,3% |
  | 0,010 (giảm 10 lần) | 4 | 19,0% |
  | **0,000** (bỏ hẳn gate) | **5** | **23,8%** |
  **Giảm 30% KHÔNG thay đổi GÌ CẢ. Giảm 10 lần mở được bốn trên hai mươi mốt. Xoá hẳn
  phép kiểm mở được năm.** Dự đoán đúng, và đúng với biên rộng: **16 trên 22 block
  (72,7%) là XUNG ĐỘT DẤU, MIỄN NHIỄM với ngưỡng.**
  **CÁI BẪY TRONG NHÃN:** hai nhãn `*_below_threshold` chiếm **11 trên 22** block, đọc
  lên như *"một nửa số block sửa được bằng ngưỡng"*. **KHÔNG PHẢI.** Ba điều kiện được
  **đánh giá theo THỨ TỰ**, nên một thất bại độ lớn **bắn TRƯỚC** và **che** một xung
  đột dấu bên dưới: **6 trên 11 block gắn nhãn độ lớn (55%) CŨNG ngược dấu**. **Đếm
  theo nhãn gate OVERSTATE đòn bẩy hơn 2 LẦN** — 50% tưởng vậy so với **22,7% thật**.
  Ví dụ live rõ nhất là `binance BTC` ở r307: `|trend_score|` = 0,01048, báo cáo là
  `trend_score_below_threshold`; **hạ ngưỡng xuống dưới 0,01 nó VẪN KHÔNG pass**, vì
  `entry_score` = −0,1278 so với `trend_score` = +0,0105 ⇒ **rơi ngay vào**
  `entry_trend_conflict`. Năm block mở được cũng **tập trung**: **bốn là `exness BTC`,
  một là `bybit XAUT`**, cần ngưỡng 0,0693 / 0,0693 / 0,0405 / 0,0119 / 0,0090.
  **KHOẢNG TRỐNG CÔNG CỤ, GHI NHẬN VÀ KHÔNG HÀNH ĐỘNG:** kể cả nếu tầm với tốt hơn thì
  **mục tiêu đồng thời vẫn không đánh giá được — `minimum_role_score` KHÔNG được research
  CLI phơi ra.** Nó là field của `TradingPolicy`
  (`crates/finance-core/src/trading_modes.rs:427`, set và clamp ở `:459`, `:465`, đọc ở
  `:850` và `:853`) còn `crates/finance-research/src/main.rs` **không có argument tương
  ứng** — khác với `--portfolio-stop-value`, `--portfolio-take-value`,
  `--portfolio-atr-periods`, `--portfolio-minimum-hold-decisions` vốn đều mirror setting
  runtime. Vậy PnL, PF, Sharpe/Sortino, drawdown, streak ở một ngưỡng khác **hôm nay
  KHÔNG đo được**. Cùng loại khoảng trống r84 đã ghi cho protective band; ghi ở đây là
  **investigation only — không áp dụng**, implement không phải việc của Claude. Lưu ý:
  **A/B ở một `--days` CỐ ĐỊNH sẽ sạch về phương pháp** kể cả sau r300-r305, vì chúng chỉ
  vô hiệu hoá so sánh **CHÉO** độ dài cửa sổ — nên **cờ CLI thiếu mới là ràng buộc**,
  không phải confound.
  **KHÔNG claim:** bất cứ điều gì về **lợi nhuận** ở ngưỡng khác (**không đo được** với
  công cụ hiện tại — không claim PnL/PF/Sharpe/drawdown theo chiều nào); rằng hạ ngưỡng
  sẽ **có hại** — nó bị bác **như một ĐÒN BẨY TẦN SUẤT** vì **tầm với quá ngắn**, còn
  các trade nó sẽ nạp vào tốt hay xấu thì **chưa test**; rằng `entry_trend_conflict`
  được hiệu chỉnh đúng — **nó CHIẾM ĐA SỐ block**, điều đó khiến nó là tham số **đáng
  quan tâm hơn**, và nó **không có ngưỡng nào cả** nên là **một loại câu hỏi khác hẳn**,
  **chưa xem xét**. **GIỚI HẠN MẪU:** 21 block nhưng **chỉ 16 trạng thái
  (route, entry_score, trend_score) PHÂN BIỆT** trên **5 route** và **6 thời điểm quan
  sát** — vài route lấy mẫu cách nhau vài phút mang **cùng một** `trend_score`, nên mẫu
  hữu hiệu **nhỏ hơn 21 rất nhiều**; tính trên trạng thái phân biệt, tỉ lệ ở ngưỡng 0 là
  **5/16 = 31,2%** thay vì 23,8% — **kết luận sống sót cả hai cách, con số thì đổi**.
  File:
  `round308-REJECTED-minimum-role-score-is-a-weak-lever-a-30pct-cut-unblocks-nothing-and-zero-unblocks-a-quarter.md`.

- **Round 309 (2026-08-30) — MỘT NGƯỠNG, HAI THANG ĐO KHÁC NHAU: `entry_score` cộng
  **3** interval còn `trend_score` cộng **5**, nên `minimum_role_score = 0.10` là một
  **nhát cắt xác suất 50/50** ở một role và một **bộ lọc nhẹ** ở role kia.
  KHÔNG CONTAINER, KHÔNG SSH.**
  **CÂU HỎI r308 CHUYỂN TIẾP:** *"`entry_trend_conflict` chiếm đa số block, khiến nó là
  tham số **đáng quan tâm hơn** — và nó **không có ngưỡng nào cả** nên là một loại câu
  hỏi khác hẳn. **Chưa xem xét.**"*
  **ĐĂNG KÝ TRƯỚC KHI TÍNH:** tỉ lệ xung đột **không phân biệt được với 50%** — dấu của
  hai role score hành xử như **hai đồng xu độc lập**.
  **HAI ROLE THỰC SỰ ĐƯỢC DỰNG THẾ NÀO:** `role_scores()` (`trading_modes.rs:1042-1069`)
  phân hoạch **THEO INTERVAL**, không theo strategy — mỗi required interval mang tag
  `Entry` hoặc `Trend`, và **CÙNG một tập strategy** đóng góp vào role mà interval của
  nó thuộc về. Map production (`trading_modes.rs:477-496`):
  | role | interval | số lượng | trọng số mỗi cái |
  |---|---|---|---|
  | **Entry** | `5m`, `15m`, `30m` | **3** | 1/8 |
  | **Trend** | `1h`, `2h`, `4h`, `12h`, `1d` | **5** | 1/8 |
  `minimum_role_score` = **0.10** (`:501`), so với **CẢ HAI tổng, KHÔNG đổi** (`:850`,
  `:853`). **Hai tổng KHÔNG cùng thang**: với trọng số đều 1/8, một trend role **hoàn
  toàn đồng thuận** có thể đạt **5/3 = 1,67x** mức tối đa của entry role ⇒ **một ngưỡng
  vô hướng NHẤT THIẾT mang hai ý nghĩa khác nhau**.
  **TỈ LỆ XUNG ĐỘT:** 16/26 sample xung đột (**61,5%**); trên **21 trạng thái PHÂN
  BIỆT**, 11/21 (**52,4%**). Binomial hai phía chính xác so với 50%: **p = 0,327** trên
  toàn mẫu, **p = 1,000** trên trạng thái phân biệt. **DỰ ĐOÁN ĐÚNG — điều kiện chặn
  chủ đạo bắn ở tỉ lệ KHÔNG PHÂN BIỆT ĐƯỢC VỚI MỘT LẦN TUNG ĐỒNG XU.** Đó **không**
  phải bằng chứng bộ lọc vô dụng: nó nói **dấu** của hai score **không mang thông tin
  tương hỗ phát hiện được** trong mẫu này, và **với 21 trạng thái thì không phát hiện
  được nhiều**.
  **THANG ĐO — bất đối xứng LỚN HƠN cả những gì số interval dự đoán:**
  | | trung bình | min | max |
  |---|---|---|---|
  | `\|entry_score\|` | **0,1067** | 0,0090 | 0,2125 |
  | `\|trend_score\|` | **0,2767** | 0,0105 | 0,7476 |
  **Tỉ số trung bình 2,59x**, so với trần cấu trúc **1,67x**, và `|trend| > |entry|` ở
  **21/26** sample — trend aggregate lớn hơn **vừa vì nhiều interval hơn vừa vì tín hiệu
  của nó TRIỆT TIÊU NHAU ÍT HƠN** (strategy khung dài đồng thuận với nhau nhiều hơn
  khung ngắn).
  **VẬY NGƯỠNG CẮT BẤT ĐỐI XỨNG, VÀ CẮT MẠNH MỘT PHÍA:** trung bình `|entry_score|` là
  **0,1067 — gần như NẰM ĐÚNG TRÊN ngưỡng 0,10**, nên **khoảng một nửa** entry score
  trượt **do cấu trúc**; trung bình `|trend_score|` **cao gấp 2,6 lần** ngưỡng. Đếm trực
  tiếp: **8/26** sample dưới ngưỡng ở phía entry so với **6/26** ở phía trend, và nhãn
  block phía entry nhiều hơn phía trend **7 so với 4**.
  **Tỉ lệ xung đột theo route rất không đều** (mỗi route sáu sample, tự tương quan
  mạnh): `exness BTC` **0/6**, `exness XAU` 0/1, `binance XAU` 4/6, `bybit XAUT` 5/6,
  `binance BTC` **6/6**, `bybit BTC` 1/1. Route **không bao giờ xung đột** (`exness
  BTC`) cũng là route được quan sát **pass gate nhiều nhất** — với mẫu này đó là **một
  trùng hợp đáng ghi, KHÔNG phải một kết quả**.
  **QUAN SÁT THIẾT KẾ, GHI NHẬN VÀ KHÔNG HÀNH ĐỘNG:** một **role score CHUẨN HOÁ** —
  chia tổng của mỗi role cho số interval trong role đó, hoặc cho tổng trọng số interval
  của nó — sẽ khiến `minimum_role_score` **mang cùng một ý nghĩa cho cả hai role**. Hôm
  nay nó không, và **phía entry hấp thụ gần như toàn bộ nhát cắt**. **INVESTIGATION
  ONLY — KHÔNG ÁP DỤNG**: đây là code change trong `finance-live-action`, **không phải
  việc của Claude**, và **không thể đánh giá trước** (r308 đã lập rằng
  `minimum_role_score` không có cờ research CLI, còn chuẩn hoá **thậm chí không phải một
  tham số**). **KHÔNG PROMOTE:** điều kiện đầu tiên của gate — evidence OOS/holdout/
  walk-forward defensible — **không thể đạt cho một thay đổi không mô phỏng được**.
  **KHÔNG claim:** rằng `entry_trend_conflict` **vô dụng** — phép test nói hai **dấu**
  không phân biệt được với độc lập trên **21 trạng thái**, **đó là power thấp**, và độc
  lập về dấu **không nói gì** về việc các trade nó chặn có lời hay không; câu hỏi đó cần
  một mô phỏng **tôi không chạy được**. **KHÔNG** claim chuẩn hoá sẽ **cải thiện** gì —
  nó làm ngưỡng **nhất quán**; nhất quán có giúp PnL/PF/drawdown/tần suất hay không thì
  **chưa test và không test được**. **KHÔNG** claim phân tách xung đột theo route là
  thật — sáu sample mỗi route, **cách nhau vài phút**, `trend_score` lặp lại y hệt; đây
  là mô tả **một buổi chiều**. **KHÔNG** claim khoảng cách thang 2,59x là **ổn định** —
  nó là trung bình của 26 sample tự tương quan trên năm route, và **reweighting thích
  nghi của r300 liên tục kéo `interval_weights` rời khỏi 1/8 đều**, nên trần cấu trúc
  1,67x áp cho policy **KHỞI TẠO**, không nhất thiết cho policy **live**. File:
  `round309-NEEDS-MORE-RESEARCH-one-threshold-two-different-scales-entry-sums-3-intervals-and-trend-sums-5.md`.

- **Round 310 (2026-08-30) — TRỌNG SỐ LIVE ĐẨY `5m` XUỐNG **THẤP HƠN UNIFORM 2,1-7,8
  LẦN** trên **mọi** route, và **KHUẾCH ĐẠI** bất đối xứng entry/trend của r309 từ
  1,67x lên **2,21x-5,96x**. Cơ chế **đã được document sẵn**; **độ lớn thì chưa**.
  KHÔNG CONTAINER; evidence production read-only + hai lần đọc code.**
  **CAVEAT r309 ĐỂ LẠI:** *"reweighting thích nghi của r300 liên tục kéo
  `interval_weights` rời khỏi 1/8 đều, nên trần cấu trúc 1,67x áp cho policy **KHỞI
  TẠO**, không nhất thiết cho policy **live**."*
  **ĐĂNG KÝ TRƯỚC KHI ĐỌC:** trọng số live **đã trôi đáng kể** — ít nhất một interval
  nằm ngoài [0,10 ; 0,15], tức lệch hơn 20% khỏi 0,125. **Nếu tất cả vẫn ≈0,125 thì
  reweighting là VÔ HIỆU trong thực tế**, và confound weight-path của r300 sẽ **nhẹ hơn
  nhiều** so với cách tôi đang xử lý.
  | route | `5m` | so uniform | `1d` | so uniform | tổng entry | tổng trend | **tỉ lệ** |
  |---|---|---|---|---|---|---|---|
  | `binance BTC/USDT` | 0,0412 | **thấp 3,0x** | 0,1549 | 1,24x | 0,3114 | 0,6886 | **2,21x** |
  | `exness BTC/USD` | 0,0408 | **thấp 3,1x** | 0,1550 | 1,24x | 0,3083 | 0,6917 | **2,24x** |
  | `bybit BTC/USDT` | 0,0588 | thấp 2,1x | **0,4145** | **3,32x** | 0,1763 | 0,8237 | **4,67x** |
  | `binance XAU/USDT` | 0,0479 | thấp 2,6x | **0,4311** | **3,45x** | 0,1437 | 0,8563 | **5,96x** |
  | `exness XAU/USD` | **0,0161** | **thấp 7,8x** | 0,2081 | 1,66x | 0,2524 | 0,7476 | **2,96x** |
  | `bybit XAUT/USDT` | 0,0571 | thấp 2,2x | 0,3030 | 2,42x | 0,2755 | 0,7245 | **2,63x** |
  **DỰ ĐOÁN ĐÚNG TRÊN MỌI ROUTE:** không gì gần uniform — `5m` **bị hạ trên cả sáu**,
  `1d` **được nâng trên cả sáu**, và trên `binance XAU` **một interval duy nhất gánh
  43% toàn bộ trọng số**. **Bất đối xứng của r309 BỊ KHUẾCH ĐẠI, KHÔNG bị chặn**: con
  số cấu trúc là 5/3 = 1,67x từ trọng số đều; tỉ lệ entry:trend **live** chạy **2,21x
  tới 5,96x**, trung bình **3,45x**. r309 quan sát tỉ số mẫu 2,59x và **không giải
  thích được** vì sao nó vượt 1,67x — **trọng số live cung cấp chiều và bậc độ lớn**
  (chúng **không** tái tạo 2,59x chính xác và **không nên**: tỉ số score còn phụ thuộc
  strategy nào có evidence không-Hold ở từng thời điểm).
  **MỘT HỆ QUẢ CẢ HAI VÒNG ĐỀU CHƯA CÓ:** với `minimum_role_score = 0.10`, **KHÔNG
  route nào có `5m` tự mình vượt được ngưỡng** — đóng góp tối đa chạy 0,0161 tới 0,0588.
  **Interval quyết định chính KHÔNG CÒN tự mình lay chuyển được entry gate ở bất kỳ đâu
  trong fleet**; role entry nay **phụ thuộc vào `15m`/`30m`** có evidence không-Hold.
  **XÁC NHẬN SỐ HỌC CHÍNH XÁC:** r307 ghi `entry_score` của `exness XAU` là
  **−0,016109519172610748**, còn trọng số interval `5m` live của nó là
  **0,016109519172610748** — **giống nhau tới mười sáu chữ số thập phân**. Điều đó ghim
  chính xác phép tính (`candle_momentum` trọng số **1.0** đóng góp một tín hiệu đủ mạnh
  ở `5m`; `15m` và `30m` **không đóng góp gì**) và xác nhận `role_scores()` hành xử
  **đúng như đã đọc** ở r309.
  **TRỌNG SỐ STRATEGY CŨNG ĐÃ SỤP:** `binance BTC` 0,521/0,479 với **cả bốn `mtf_*`
  đúng bằng 0,0**; `exness BTC` 0,515/0,485, bốn `mtf_*` = 0,0; `bybit BTC` 0,525/0,475;
  `binance XAU` 0,386/0,614; **`exness XAU` `candle_momentum` = 1.0 và mọi strategy
  khác = 0,0**; `bybit XAUT` 0,826/0,174. **Quyết định Portfolio của `exness XAU` do
  MỘT strategy gánh**, và mọi `mtf_*` đúng bằng 0,0 — **tái xác nhận độc lập r206-r207
  từ policy state live**.
  **CƠ CHẾ ĐÃ ĐƯỢC BIẾT VÀ CỐ Ý GIỮ NGUYÊN — TÔI KHÔNG TRÌNH BÀY ĐÂY NHƯ MỘT PHÁT
  HIỆN.** `deployment_rules.rs:218-240` đã document: `alpha_performance_quality` trả về
  **1.0 khi `trade_count == 0`** (`trading_modes.rs:593-595`), luật "benefit of the
  doubt" — nên **interval KHÔNG có lịch sử giao dịch Alpha nhận chất lượng TỐI ĐA**,
  trong khi interval **thực sự giao dịch** bị chấm theo hiệu năng **thua lỗ thật** và
  rơi về `INTERVAL_QUALITY_FLOOR = 0.05` (`:453`). Ghi chú đó gọi tên "pathological
  all-entry-intervals-zeroed pattern", ghi rằng các zombie `mtf_*` đang **chống đỡ tần
  suất decision** "bằng cách chưa tích luỹ đủ 20 role-interval evaluation", và nêu hướng
  sửa: *"một interval-weight floor RÕ RÀNG, CÓ CHỦ ĐÍCH trong
  `reweight_from_alpha_performance`"*. **Cái vòng này THÊM VÀO** là **độ lớn hiện tại
  trên cả sáu route** và **tương tác của nó với `minimum_role_score`**, thứ ghi chú kia
  **không phủ**. Lưu ý: ý tưởng **chuẩn hoá role** của r309 là **ĐÒN BẨY KHÁC** với
  **interval-weight floor** nói trên — một cái sửa **thang entry/trend**, cái kia sửa
  **interval nào được trọng số**. **Cả hai vẫn là INVESTIGATION ONLY, KHÔNG ÁP DỤNG.**
  **KHÔNG claim:** rằng cách gán trọng số này **SAI** — nó được document như một đánh
  đổi **đã biết và cố ý chấp nhận**; tôi **đo độ lớn hiện tại**, **không** đánh giá liệu
  một cách gán khác có giao dịch tốt hơn, và r308 đã lập rằng **công cụ không cho phép**.
  **Không** claim việc `5m` không tự vượt ngưỡng là **có hại** — đó là **sự thật cấu
  trúc** của cấu hình hiện tại; entry gate **có nên** lay chuyển được bởi interval chính
  hay không là **câu hỏi thiết kế, chưa test**. **Không** claim trọng số **ổn định** —
  **một snapshot**, reweighting chạy trên **mỗi kline**. **Không** diễn giải trọng số
  của `binance XAU`: dữ liệu thị trường của nó **đóng băng từ 2025-12-25** (r207, r306)
  nên 0,4311 ở `1d` **có thể phản ánh một ledger đứng yên** chứ không phải hiệu năng
  live — **ghi nhận, không diễn giải**. File:
  `round310-NEEDS-MORE-RESEARCH-live-weights-put-5m-2x-to-8x-below-uniform-and-amplify-the-entry-trend-asymmetry-to-6x.md`.

- **Round 311 (2026-08-30) — MỌI STRATEGY ĐỀU LỖ, NÊN `alpha_performance_quality` RÚT
  GỌN THÀNH **`1 − trades/20`**. Trọng số là một **HÀM THUẦN TUÝ CỦA SỐ TRADE** — và
  **đó chính là CƠ CHẾ của confound r300**. KHÔNG CONTAINER, KHÔNG SSH.**
  **HÀM QUALITY THỰC SỰ TÍNH GÌ** (`trading_modes.rs:589-617`, với
  `PERFORMANCE_CONFIDENCE_TRADES = 20.0` ở `:431`):
  `confidence = clamp(trade_count/20, 0, 1)`; **nếu `confidence == 0` → trả về 1.0**;
  `empirical = 0.0` **trừ khi** `realized_pnl > 0 && gross_profit > 0`; trả về
  `(1 − confidence) + confidence × empirical`.
  **MỌI strategy trên MỌI route đều là kẻ thua đã xác nhận** — điều này giữ suốt cả
  session, `realized_pnl` âm ở cả bốn cửa sổ r305 và cả sáu route r306-r307 — nên
  `empirical` **đúng bằng 0.0 ở khắp nơi**, và toàn bộ hàm **sụp xuống thành**:
  **`quality = 1 − min(trade_count/20, 1)`**, sàn `INTERVAL_QUALITY_FLOOR = 0.05`
  (`:453`).
  **HIỆU NĂNG KHÔNG HỀ THAM GIA VÀO VIỆC GÁN TRỌNG SỐ:** trọng số của một interval được
  quyết định **CHỈ bởi số trade Alpha nó đã sinh ra**, và **giảm đơn điệu** theo con số
  đó — 0 trade nhận **tối đa 1.0**, từ 20 trade trở lên nhận **đúng 0.0** (bị sàn về
  0,05).
  **TRỌNG SỐ LIVE TÁI DỰNG CHÍNH XÁC:** r310 đọc trọng số production mà **không giải
  thích được**; trên ba route mang **đúng hai strategy**, cả vector **nghịch đảo được
  sạch sẽ** (các interval bị sàn ghim hằng số chuẩn hoá), và mỗi interval còn lại cho ra
  **một SỐ TRADE SUY RA**:
  | route | `1d` | `12h` | cao kế tiếp | còn lại |
  |---|---|---|---|---|
  | `bybit BTC/USDT` | **12,9 trade** | 16,0 | — | ≥ 20 (trưởng thành) |
  | `binance XAU/USDT` | **11,0 trade** | 16,0 | `4h` 17,1 | ≥ 20 |
  | `bybit XAUT/USDT` | **14,7 trade** | 15,6 | `15m` 17,2 | ≥ 20 |
  Mỗi phép tái dựng **khớp đúng hằng số chuẩn hoá của chính nó**. **MỌI interval được
  NÂNG trọng số đều được nâng vì MỘT LÝ DO: nó CHƯA làm đủ 20 trade.** `1d` ở mức
  **11-15 trade** trên cả ba và gánh **30-43% tổng trọng số** — **không cái nào giành
  được nó bằng hiệu năng**, vì **hiệu năng đóng góp bằng KHÔNG do cấu trúc**.
  **TẠI SAO ĐÂY LÀ CONFOUND r300:** r300-r305 lập rằng đổi `--days` làm đổi dòng
  decision, đo được tới **−42 trade** từ nhiễu loạn **chín ngày**, và **chưa bao giờ
  giải thích ĐƯỢC VÌ SAO**. **Đây là vì sao.** Trong replay các Alpha ledger **bắt đầu
  RỖNG**, nên **độ trưởng thành** của một interval là hàm của **số bar cửa sổ cấp cho
  nó**:
  | interval | bar trong cửa sổ 180 ngày 24/7 | cửa sổ tối thiểu để **có thể** đạt 20 trade |
  |---|---|---|
  | `5m` | 51 840 | vài giờ |
  | `1h` | 4 320 | — |
  | `12h` | 360 | **10 ngày bar**, thực tế lâu hơn nhiều |
  | `1d` | **180** | **20 ngày bar**, thực tế lâu hơn nhiều |
  `5m` **bão hoà confidence gần như ngay lập tức** ở mọi cửa sổ và rơi xuống sàn; `1d`
  **có thể không bao giờ đạt 20 trade** — ở 11-15 trade trong production sau **nhiều
  tháng**, rõ ràng nó chưa.
  **VẬY CỬA SỔ CÀNG NGẮN → INTERVAL DÀI CÀNG ÍT TRƯỞNG THÀNH → TRỌNG SỐ CỦA CHÚNG CÀNG
  CAO → DÒNG DECISION CÀNG BỊ TREND CHI PHỐI.** **Vector trọng số là hàm của độ dài cửa
  sổ DO CẤU TRÚC**, và nó dịch chuyển **theo một chiều DỰ ĐOÁN ĐƯỢC**. Nó cũng giải
  thích vì sao r310 thấy tỉ lệ entry:trend live 2,21x-5,96x so với 1,67x uniform: **các
  interval dài chính là các interval CHƯA TRƯỞNG THÀNH về mặt cấu trúc**.
  **ĐIỀU NÀY KHÔNG THAY ĐỔI GÌ:** hành vi **đã được document như một lựa chọn CÓ CHỦ
  ĐÍCH** — `deployment_rules.rs:218-240` gọi tên luật `trade_count == 0 → quality = 1.0`,
  **gọi kết quả là "pathological"**, và ghi rằng zombie `mtf_*` chống đỡ tần suất
  decision "bằng cách chưa tích luỹ đủ 20 role-interval evaluation". r310 trích ghi chú
  đó cho **trọng số STRATEGY**; **vòng này cho thấy CÙNG một phép số học điều khiển
  trọng số INTERVAL**, và **tái dựng nó bằng SỐ**. Ghi chú `normalize_or_uniform_weights`
  (`:630-645`) cũng giải thích **vì sao cần sàn**: không có nó, một route mà mọi strategy
  đã trưởng thành thành kẻ thua sẽ có **mọi trọng số bằng 0**, `role_scores()` trả về
  0.0, **gate không bao giờ clear được và route không bao giờ decide lại được** — **sàn
  là một DEADLOCK GUARD CÓ CHỦ ĐÍCH, không phải tai nạn**.
  **KHÔNG PROMOTE:** ở đây **không có defect nào để sửa** — đó là một đánh đổi đã
  document — và r308 đã lập rằng **các tham số dù sao cũng không mô phỏng được**.
  **KHÔNG claim:** rằng các **số trade suy ra là CHÍNH XÁC** — chúng được **nghịch đảo**
  từ ba vector trọng số đã chuẩn hoá, dưới giả định các interval bị sàn nằm **đúng** ở
  sàn và **mọi** strategy trên route đều lỗ; cả hai đều có cơ sở tốt nhưng con số là
  **SUY RA, KHÔNG PHẢI ĐỌC ĐƯỢC**. **Không** claim điều này giải thích **ĐỘ LỚN** của
  confound r300 — nó giải thích **CHIỀU** và **CƠ CHẾ**, **không** dự đoán được −42
  trade ở chín ngày, và tôi **không** thử dựng mô hình định lượng. **Không** claim cách
  gán trọng số là **sai** hay **nên đổi**. **Không** claim gì về hai route sáu-strategy
  (`binance BTC`, `exness BTC`) — vector của chúng **không được nghịch đảo** ở đây, nhiều
  tham số tự do hơn, và tôi **không muốn FIT thay vì GIẢI**. **Không** claim số của
  `binance XAU` nói lên điều gì về hành vi **live** — dữ liệu của nó **đóng băng từ
  2025-12-25**, ledger count **cũ do cấu trúc**; đưa vào vì **phép số học khớp**, không
  phải như bằng chứng live. File:
  `round311-NEEDS-MORE-RESEARCH-the-weights-are-a-pure-trade-count-function-and-that-is-the-mechanism-of-the-round-300-confound.md`.

- **Round 312 (2026-08-30) — CONFOUND **TỆ HƠN** THEO ĐỘ SÂU, KHÔNG NHẸ ĐI: một ngày
  làm dịch **+50 TRADE** ở 900 ngày so với **+5** ở 260 — và verdict Target 3 của
  `binance BTC` **NẰM VẮT NGANG VẠCH**. 2 container (đúng budget).**
  **DỰ ĐOÁN, VÀ VÌ SAO TÔI ĐƯA RA NÓ:** r311 khép lại bằng việc gọi tên thứ nó **chưa**
  làm: *"nó giải thích CHIỀU và CƠ CHẾ; nó **không** dự đoán được −42 trade ở chín
  ngày."* Cơ chế đó **cho một hệ quả TEST ĐƯỢC**: quality là `1 − min(trades/20, 1)` cho
  kẻ thua, sàn 0,05 — nên **cửa sổ càng dài thì MỌI interval rốt cuộc đều vượt 20 trade**,
  mọi quality chạm sàn, và `normalize_or_uniform_weights` **đưa chúng về UNIFORM 1/8** ⇒
  **còn ít quỹ đạo trọng số để nhiễu loạn hơn**.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** ở 900/901 ngày, nhiễu loạn một ngày làm `one_target` dịch
  **DƯỚI 5 trade** về độ lớn — **nhỏ hơn** +5 đo ở 260/261 (r302). Bác bỏ ở **≥5** hoặc
  nếu **âm**.
  | `--days` | candle | **`one_target`** | legacy | grid | cost | Alpha 5m | **rate/tuần** | biên |
  |---|---|---|---|---|---|---|---|---|
  | 900 | 259 198 | **862** | 1 178 | 12 414 | 62 | 1 110 899 | **6,704** | **−4,2%** |
  | 901 | 259 486 | **912** | 1 251 | 13 370 | 68 | 1 112 168 | **7,085** | **+1,2%** |
  **Một ngày thêm làm `one_target` dịch +50 TRADE.** Nội dung thật của ngày đó theo
  chính rate 900 ngày của route là **0,96 trade** — **vượt 52 LẦN**.
  `legacy_selected_rule` dịch **+73**, `legacy_grid` **+956 (+7,7%)** từ **cùng một
  ngày**.
  **DỰ ĐOÁN BỊ BÁC BỎ VỚI HỆ SỐ MƯỜI:** 260→261 cho **+5** trade (+1,04% rate);
  **900→901 cho +50 trade (+5,68% rate)** — **CONFOUND LỚN GẤP 10 LẦN Ở CỬA SỔ SÂU
  HƠN**. Lập luận trưởng-thành của r311 **dự đoán điều NGƯỢC LẠI**, nên cơ chế đó **ít
  nhất là KHÔNG ĐẦY ĐỦ**: nó giải thích vì sao cửa sổ ngắn nâng trọng số interval dài,
  nhưng **không** giải thích vì sao **độ nhạy TĂNG theo độ sâu**. **Tôi KHÔNG đề xuất
  một cơ chế thứ hai** — r279-r284 là lý do thường trực, và **tôi vừa chứng kiến một cơ
  chế của chính mình đưa ra một dự đoán sai**. Control Alpha vẫn như mọi khi: **4,406
  trade/candle thêm** so với 4,628 cùng route ở r302 — nhất quán, dương, đơn điệu.
  **`binance BTC` KHÔNG CÒN MỘT PASS SẠCH.** Mọi cửa sổ đo hôm nay trên route này:
  | `--days` | trade | rate/tuần | biên | verdict |
  |---|---|---|---|---|
  | 260 | 350 | 9,423 | +34,6% | pass |
  | 261 | 355 | 9,521 | +36,0% | pass |
  | 270 | 313 | 8,115 | +15,9% | pass |
  | 280 | 334 | 8,350 | +19,3% | pass |
  | **900** | **862** | **6,704** | **−4,2%** | **FAIL** |
  | **901** | **912** | **7,085** | **+1,2%** | pass |
  **Năm pass, một fail, và vạch NẰM GIỮA HAI CỬA SỔ CÁCH NHAU MỘT NGÀY**; trải trên sáu
  cửa sổ là **34,3% trung bình**. **HAI THỨ PHẢI TÁCH RA**, điều r302/r305 chưa cần làm:
  **(1) MỨC ĐỘ** ở 900 ngày (6,7/tuần so với 9,4 ở 260) **CÓ THỂ LÀ LỊCH SỬ THẬT** —
  r293 đã đo các lát sâu của route này thấp hơn (6,26/tuần ở `[360,540]`), nên một cửa
  sổ dài lấy trung bình cả những năm trầm lắng là **ĐIỀU DỰ KIẾN, KHÔNG PHẢI DEFECT**;
  **(2) CÚ VẮT NGANG VẠCH THÌ KHÔNG THẬT** — 6,704 và 7,085 đến từ hai cửa sổ **cách
  nhau MỘT NGÀY**, và vạch rơi vào giữa **thuần tuý do nhiễu đo**. Vậy pass của
  `binance BTC` là **thuộc tính của cửa sổ GẦN**: r302/r305 ghi nó là pass với đệm đang
  co lại; **nay phải đọc là PASS TRÊN CỬA SỔ 260-280 NGÀY, CHƯA XÁC ĐỊNH Ở ĐỘ SÂU** —
  **cùng trạng thái `exness XAU` đạt tới ở r304, đến từ hướng ngược lại**. Banner
  QUALIFIED đã gắn lên r302 và r305; banner CORRECTED lên r311.
  **KHÔNG claim:** **bất kỳ cơ chế nào** cho việc độ nhạy tăng theo độ sâu — lập luận
  của r311 dự đoán ngược lại và **vừa trượt một phép test**; tôi **không thay nó bằng
  một phỏng đoán**. **Không** claim `binance BTC` **FAIL** Target 3 — nó **pass 5/6 cửa
  sổ**, và mức 900 ngày **có thể phản ánh những giai đoạn lịch sử trầm lắng thật** (r293);
  điều được claim là **verdict KHÔNG ĐỘC LẬP VỚI CỬA SỔ**, một phát biểu **khác và YẾU
  HƠN**. **Không** claim mức 900 ngày đáng tin **như một MỨC** — nó là **một cửa sổ**, và
  r300-r305 áp cho nó y như mọi cửa sổ khác. **Không** claim +50 là **trường hợp xấu
  nhất** — một phép nhiễu loạn, một cặp độ sâu, và r304 đã cho thấy các con số này **chỉ
  tăng** khi đầu dò mở rộng. **Ba trên sáu route vẫn chưa có phép nhiễu loạn nào.**
  realized_pnl −5,10 và −3,79 — **âm cả hai**. File:
  `round312-REJECTED-the-confound-grows-with-depth-one-day-moves-50-trades-at-900d-and-binance-btc-straddles-the-bar.md`.

- **Round 313 (2026-08-30) — TẦNG PORTFOLIO **CÓ EDGE GỘP DƯƠNG**. Khoản lỗ là **DO
  CHI PHÍ**, không phải do tín hiệu — nhưng edge chỉ bằng **30% chi phí khứ hồi**, và
  cấu hình đang deploy nằm ở **70% trần cứng của cost gate**. 2 container (đúng
  budget), XAU trước.**
  **VÌ SAO LÀ VIỆC NÀY, VÀ VÌ SAO LÚC NÀY:** **mười ba vòng** đã dành cho đo tần suất
  trade, trong khi **Target 1 — lợi nhuận — là ưu tiên ĐƯỢC LIỆT KÊ ĐẦU TIÊN**, và cả
  mạch này **chưa bao giờ hỏi câu hỏi trung tâm của nó: LỖ LÀ DO CHI PHÍ HAY DO TÍN
  HIỆU?** r96 từng chạy cost ablation nhưng trên **bảng sweep tầng ALPHA** (PF từng
  candidate, BTC, 5 năm); **tầng PORTFOLIO — `one_target`, thước đo Portfolio-faithful
  duy nhất (r82) — CHƯA BAO GIỜ được cost-ablate**. Và r308 đã lập rằng **A/B ở một
  `--days` CỐ ĐỊNH vẫn sạch** sau toàn bộ confound r300-r312, vì confound đó chỉ phá
  so sánh **CHÉO** độ dài cửa sổ.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** `one_target.realized_pnl` **vẫn ÂM** ở chi phí bằng 0 —
  lỗ do tín hiệu, khớp cách đọc "trần cấu trúc" của r93 và phát hiện r274 rằng lỗ mỗi
  trade **gần như không đổi** khi tần suất đổi 2,4x. **Bác bỏ nếu nó về ≥ 0.**
  | fee/slippage (bps) | trade `one_target` | **realized_pnl** | pnl/trade | pnl không-guard | trade không-guard |
  |---|---|---|---|---|---|
  | **0 / 0** | 391 | **+1,0997** | **+0,00281** | **+1,5993** | 472 |
  | 5 / 2 (đang deploy) | 374 | −2,4441 | −0,00654 | −1,9787 | 462 |
  | 10 / 4 | **0** | — | — | −4,9873 | 443 |
  **Ở CHI PHÍ THỰC THI BẰNG KHÔNG, TẦNG PORTFOLIO CÓ LÃI** — **cả hai thước đo đều đổi
  dấu**. **Dự đoán bị bác**, và cách đọc "trần cấu trúc" **KHÔNG đúng ở tầng
  Portfolio**: **lỗ là DO CHI PHÍ.**
  **NHƯNG EDGE NHỎ SO VỚI CHI PHÍ NÓ PHẢI VƯỢT:** edge gộp mỗi trade **+0,00281** so
  với chi phí khứ hồi **0,00935** = **30,1%**. **Hai ước lượng ĐỘC LẬP** cho mức cần
  cắt: **`one_target`** (2 điểm) cần chi phí khứ hồi xuống **4,2 bps — cắt 70%**;
  **không-guard** (3 điểm, gần tuyến tính, độ dốc −0,2556 và −0,2149 per bps, lệch 17%)
  cắt trục 0 ở **6,3-6,8 bps — cắt ~51%**. Vậy phát biểu trung thực **không phải** "các
  strategy hoạt động được, chi phí cản đường", mà là: **CÓ MỘT EDGE GỘP THẬT NHƯNG NHỎ,
  đáng khoảng MỘT PHẦN BA ĐẾN MỘT NỬA chi phí thực thi hiện tại**. Khép khoảng đó là
  câu hỏi **venue/spread/phí**, **không phải** câu hỏi tinh chỉnh tham số.
  **MỘT GIỚI HẠN CỨNG DO NHÁNH 2x PHÁT HIỆN:** nhánh `10/4` **suy biến, và CHÍNH ĐÓ là
  phát hiện**: `one_target` trả về **KHÔNG TRADE NÀO** với **66 025** lần từ chối
  `execution_cost`. `CostGatePolicy` chặn tổng chi phí ở **`max_total_cost_bps = 10.0`**,
  và 10 + 4 = 14 bps một chiều **vượt nó ở MỌI fill**. **Vậy mức 7 bps một chiều đang
  deploy nằm ở 70% một TRẦN CỨNG khiến route DỪNG HẲN.** Một broker hoặc điều kiện thị
  trường làm xấu thực thi thêm ~43% sẽ **âm thầm đưa một route về KHÔNG TRADE**, chứ
  không phải về PnL tệ hơn. Số lần từ chối `execution_cost` qua ba mức: **0 / 181 /
  66 025**. Lưu ý `legacy_selected_rule` vẫn tạo 443 trade ở 10/4, nên cost gate **ràng
  buộc ở mức dựng target của Portfolio**, không ràng buộc thước đo đó — **đó là lý do
  đường cong chi phí ba điểm không-guard dùng được trong khi điểm thứ ba của
  `one_target` suy biến**. **Ghi nhận như quan sát về headroom — INVESTIGATION ONLY,
  KHÔNG ÁP DỤNG**, và **không đề xuất promotion** (điều kiện đầu tiên của gate — evidence
  OOS/holdout/walk-forward defensible cho một cải tiến — **không** được thoả bởi một
  quan sát về headroom).
  **KHÔNG claim:** rằng điều này **TỔNG QUÁT HOÁ** — một route, một cửa sổ, một
  instrument; **năm route còn lại chưa test**, và kết quả tầng Alpha của r96 là trên
  **BTC**. **Không** claim đây là ablation **SẠCH** — chi phí **cũng làm đổi dòng
  decision** (391 trade so với 374) vì cost gate từ chối khác đi; đây đo "hệ thống làm
  gì ở chi phí 0" so với "ở chi phí deploy", **đúng câu hỏi nhưng KHÔNG phải phản-thực
  thuần trên một tập trade cố định**. **KHÔNG claim gì về Ý NGHĨA KINH TẾ**: các con số
  tuyệt đối ở đơn vị notional của simulator dưới sizing `fixed_notional`; **`starting_equity`
  = 10 000 KHÔNG phải mẫu số đúng** và tôi **không** trích một tỉ suất trên nó — thứ được
  thiết lập là **DẤU** và **TỈ LỆ VỚI CHI PHÍ**, không phải một độ lớn ai đó nên dùng để
  size vị thế. **Không** claim gì về PF, win rate, Sharpe, Sortino, drawdown, streak hay
  SQN ở chi phí 0 — `one_target` chỉ báo trades/realized_pnl/funding/ledgers (giới hạn
  thường trực từ r84). **Không** claim mức cắt 51-70% là **khả thi**. **Không** claim r96
  bị mâu thuẫn — nó đo PF tầng Alpha trên BTC và thấy chi phí giải thích phần lớn khoảng
  cách tới PF=1, **cùng chiều**; vòng này **mở rộng sang tầng Portfolio trên XAU và đặt
  một CON SỐ lên phần còn thiếu**. File:
  `round313-REJECTED-the-portfolio-layer-has-positive-gross-edge-the-loss-is-cost-driven-but-the-edge-is-only-30pct-of-costs.md`.

- **Round 314 (2026-08-30) — CHẨN ĐOÁN "DO CHI PHÍ" **KHÔNG TỔNG QUÁT HOÁ**:
  `binance BTC` **vẫn lỗ ở chi phí BẰNG KHÔNG** — edge thô của nó **ÂM**. 2 container
  (đúng budget), cùng thiết kế `--days` cố định.**
  **GIỚI HẠN r313 ĐÃ NÊU:** *"rằng điều này **tổng quát hoá** — một route, một cửa sổ,
  một instrument; `binance BTC`, `exness BTC`, `bybit BTC`, `bybit XAUT` và
  `binance XAU` **chưa test**."* `binance BTC` là instrument **flagship** và route
  **bận nhất** nên nó đi trước.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** `binance BTC` **cũng** có edge gộp dương —
  `one_target.realized_pnl > 0` ở 0/0 bps — với edge chiếm tỉ lệ tương tự trên chi phí
  khứ hồi (khoảng 15-60%). **Bác bỏ nếu PnL ở chi phí 0 là ÂM.** Tôi ghi rõ **trước khi
  chạy** rằng r96 thấy các candidate Alpha BTC chỉ đạt **PF 0,91-1,06** ở chi phí 0 —
  **vắt ngang điểm hoà** — nên đây là **một phép test thật**, không phải thủ tục.
  | fee/slippage | trade | **realized_pnl** | pnl/trade | không-guard | trade k-guard | cost rej |
  |---|---|---|---|---|---|---|
  | **0 / 0** | 479 | **−0,4432** | **−0,00093** | −2,0053 | 616 | 0 |
  | 5 / 2 (deploy) | 460 | −3,6776 | −0,00799 | −6,8053 | 659 | 85 |
  **Ở CHI PHÍ THỰC THI BẰNG KHÔNG, `binance BTC` VẪN LỖ** — cả hai thước đo **đều âm**.
  Edge gộp mỗi trade **−0,00093**: **tín hiệu thô đã KHÔNG có lãi TRƯỚC MỌI MA SÁT**, nên
  **không phép giảm chi phí nào làm route này có lãi được** — hoà vốn cần **cắt 113%**,
  một thứ không tồn tại.
  **HAI ROUTE MÂU THUẪN NHAU, VÀ CẢ HAI DỰ ĐOÁN CỦA TÔI ĐỀU SAI:**
  | route | pnl chi-phí-0 | pnl deploy | gộp/trade | edge ÷ chi phí | phần dư ở chi phí 0 |
  |---|---|---|---|---|---|
  | `exness XAU/USD` | **+1,0997** | −2,4441 | **+0,00281** | **+30,1%** | **DƯƠNG** |
  | `binance BTC/USDT` | **−0,4432** | −3,6776 | **−0,00093** | **−13,1%** | **ÂM** |
  r313 dự đoán XAU **vẫn âm** → nó thành **DƯƠNG**; r314 dự đoán BTC **thành dương** →
  nó **vẫn ÂM**. **Cả hai đăng ký trước đều thất bại, THEO HAI CHIỀU NGƯỢC NHAU** —
  đáng ghi lại như **một cảnh báo về CHÍNH TIÊN NGHIỆM CỦA TÔI** trên câu hỏi này, chứ
  không phải hai lần đoán xui.
  **KHÔNG CÓ MỘT CHẨN ĐOÁN CHUNG CHO CẢ FLEET:** cách đọc "trần cấu trúc" của **r93
  ĐÚNG trên BTC và SAI trên XAU**; cách đọc "do chi phí" của **r313 ĐÚNG trên XAU và
  SAI trên BTC**.
  **ĐIỀU HAI ROUTE CÙNG CHIA SẺ:** **chi phí chiếm phần lớn khoản lỗ trên CẢ HAI** —
  `exness XAU` chi phí phá **3,5438** = **145%** khoản lỗ deploy (nên bỏ nó đi thì
  **đổi dấu**); `binance BTC` chi phí phá **3,2344** = **88%** khoản lỗ, để lại phần dư
  **−0,4432 ở phía sai của số 0**. Vậy **"chi phí là số hạng chi phối" là ĐÚNG trên cả
  hai**; thứ **khác nhau** chỉ là **phần dư bên dưới có dương hay không** — và **chính
  sự phân biệt đó mới là câu hỏi thực tiễn**: trên XAU một mức cắt chi phí đủ lớn **đạt
  được điểm hoà** (cần cắt 51-70% theo r313), **trên BTC KHÔNG GÌ ĐẠT ĐƯỢC**. Banner
  **QUALIFIED** đã gắn lên r313.
  **KHÔNG claim:** bất cứ điều gì về **bốn route còn lại** — `exness BTC`, `bybit BTC`,
  `bybit XAUT`, `binance XAU` **chưa có cost ablation nào**; **hai route mâu thuẫn là lý
  do để KỲ VỌNG SỰ KHÔNG ĐỒNG NHẤT, không phải cơ sở để dự đoán route thứ ba**. **Không**
  claim `binance BTC` **không thể** có lãi — thứ được chứng minh là **RIÊNG việc giảm chi
  phí** không làm được, trên cấu hình và cửa sổ này; một tín hiệu/band/tập candidate khác
  **chưa được test ở đây**. **Không** claim phân tách là theo **instrument** thay vì theo
  **broker** hay route — XAU-trên-Exness so với BTC-trên-Binance khác nhau ở **cả hai**,
  và **`exness BTC` sẽ tách được chúng nhưng chưa chạy**. **Không** claim độ lớn nào —
  như r313, các con số ở đơn vị notional của simulator, `starting_equity` **không phải
  mẫu số đúng**; chỉ **DẤU** và **TỈ LỆ VỚI CHI PHÍ** được khẳng định. **Không** có
  PF/win rate/Sharpe/Sortino/drawdown/streak — `one_target` không báo (r84), nên đây là
  so sánh **CHỈ PnL** và **KHÔNG PHẢI** đánh giá đa mục tiêu mà loop yêu cầu. **Không**
  claim kết quả nào **độc lập cửa sổ** — cả hai là một cửa sổ `--days 360` duy nhất;
  r300-r312 **không** chạm vào A/B này nhưng chúng có nghĩa là **không MỨC nào** nên được
  trích như edge thật của route. File:
  `round314-REJECTED-the-cost-driven-diagnosis-does-not-generalise-binance-btc-still-loses-at-zero-cost.md`.

- **Round 315 (2026-08-30) — PHÂN TÁCH **KHÔNG** THEO INSTRUMENT: `exness BTC` cũng
  DƯƠNG — nhưng **dấu của nó ĐỔI GIỮA HAI THƯỚC ĐO**, và broker **bị trộn hoàn toàn**
  với market type. 2 container (đúng budget).**
  **Ô r314 ĐÃ NÊU:** *"rằng phân tách là theo **instrument** thay vì **broker** hay
  route — XAU-trên-Exness so với BTC-trên-Binance khác nhau ở **cả hai**, và
  **`exness BTC` sẽ tách được chúng** nhưng chưa chạy."* Đó là **ô duy nhất** hoàn tất
  cả hai so sánh: giữ **broker** cố định so với `exness XAU`, và giữ **instrument** cố
  định so với `binance BTC`.
  **ĐĂNG KÝ TRƯỚC KHI CHẠY:** PnL chi-phí-0 của `exness BTC` **ÂM** như `binance BTC` —
  phân tách theo **instrument**. **Bác bỏ nếu dương.** **Cơ sở** là r96, vốn thấy các
  candidate Alpha BTC ở chi phí 0 cho kết quả **gần như y hệt giữa hai broker**
  (donchian 0,96/0,96; keltner 1,02/1,06; heikin 0,98/0,91 binance/exness) — **giống
  nhau theo broker trên BTC**, tức chỉ về phía instrument.
  | fee/slippage | trade | **realized_pnl** | pnl/trade | không-guard | trade k-guard | cost rej |
  |---|---|---|---|---|---|---|
  | **0 / 0** | 508 | **+0,5634** | **+0,00111** | **−0,4548** | 636 | 0 |
  | 5 / 2 (deploy) | 488 | −4,3201 | −0,00885 | −6,2155 | 669 | 95 |
  **`exness BTC` DƯƠNG ở chi phí 0 trên `one_target`** — dự đoán thất bại, và **phân
  tách KHÔNG theo instrument**.
  **NHƯNG CŨNG KHÔNG SẠCH SẼ THEO BROKER**, vì hai lý do:
  | route | broker | market | `one_target` 0-cost | gộp/trade | edge÷cp | không-guard 0-cost | cùng dấu? |
  |---|---|---|---|---|---|---|---|
  | `exness XAU/USD` | exness | cfd | +1,0997 | **+0,00281** | +30,1% | +1,5993 | có |
  | **`exness BTC/USD`** | exness | cfd | **+0,5634** | **+0,00111** | +11,1% | **−0,4548** | **KHÔNG** |
  | `binance BTC/USDT` | binance | perp | −0,4432 | **−0,00093** | −13,1% | −2,0053 | có |
  **(1) Dấu của `exness BTC` PHỤ THUỘC THƯỚC ĐO** — nó là **route DUY NHẤT** mà
  `one_target` (+0,5634) và không-guard (−0,4548) **ngược dấu nhau**; hai route kia đều
  đồng dấu. **Ô quyết định câu hỏi lại chính là ô mà câu trả lời KHÔNG VỮNG.**
  **(2) Broker và market type BỊ TRỘN HOÀN TOÀN:** mọi route dương đều là
  **exness + cfd**, route âm duy nhất là **binance + perpetual_future** — **không gì
  trong mẫu này tách được "Exness" khỏi "CFD"**. `bybit BTC` (perp) hoặc `bybit XAUT`
  (spot) **sẽ tách được**; **không cái nào được chạy**.
  Và đây là **một GRADIENT, không phải nhị phân**: +0,00281 → +0,00111 → −0,00093 mỗi
  trade; **ngay cả ô tốt nhất cũng chỉ chuyển hoá 30% chi phí khứ hồi**.
  **BA DỰ ĐOÁN, BA LẦN THẤT BẠI:** r313 dự đoán XAU **vẫn âm** → **dương**; r314 dự đoán
  BTC **thành dương** → **vẫn âm**; r315 dự đoán `exness BTC` **vẫn âm** → **dương**.
  **Ba đăng ký trước liên tiếp trên cùng một trục, đều sai, hai lần theo hai chiều ngược
  nhau.** Tôi ghi lại đây như **một phát hiện MINH THỊ về CHÍNH TIÊN NGHIỆM CỦA TÔI**:
  **tôi không có mô hình hoạt động nào về việc edge thô nằm ở đâu trong fleet này**, và
  **nên NGỪNG đưa ra dự đoán có hướng trên trục đó** cho tới khi có thứ gì khác ngoài
  trực giác cung cấp một mô hình.
  **KHÔNG claim:** rằng phân tách **theo BROKER** (nó khớp trên `one_target`, nhưng ô
  quyết định **mơ hồ về dấu** và broker **bị trộn** với market type); rằng nó **theo
  MARKET TYPE** (cùng một confound đọc theo chiều kia); bất cứ điều gì về `bybit BTC`,
  `bybit XAUT`, `binance XAU` — **ba trên sáu route vẫn chưa có cost ablation**, và
  **hai route phá được confound broker/market-type nằm trong số đó**; rằng `exness BTC`
  có edge **DÙNG ĐƯỢC** — +0,00111/trade là **11,1%** chi phí khứ hồi, cần cắt **~89%**,
  **tệ hơn** mức 51-70% của `exness XAU`, và **dấu của nó không sống sót khi đổi thước
  đo**. Không có PF/win rate/Sharpe/Sortino/drawdown/streak; không claim độ lớn nào;
  tất cả đều là **một cửa sổ `--days 360` duy nhất**. File:
  `round315-REJECTED-the-split-is-not-by-instrument-exness-btc-is-positive-too-but-its-sign-is-measure-dependent.md`.

- **Round 316 (2026-08-30) — **BROKER BỊ LOẠI**: cả hai route perpetual-future đều lỗ ở
  chi phí bằng không, trên **hai broker KHÁC NHAU**, chỉ cách nhau **20%** mỗi trade.
  Market type sống sót — nhưng **mới phá được MỘT NỬA confound**. 2 container (đúng
  budget).**
  **VÒNG NÀY KHÔNG ĐƯA DỰ ĐOÁN CÓ HƯỚNG, MỘT CÁCH CÓ CHỦ Ý.** r315 đã ghi như một phát
  hiện về chính tiên nghiệm của tôi: *"tôi không có mô hình hoạt động nào về việc edge
  thô nằm ở đâu, và **nên NGỪNG đưa ra dự đoán có hướng**"* — ba đăng ký trước liên tiếp
  đã thất bại. Nên vòng này **đăng ký trước CÁCH DIỄN GIẢI** thay vì kết quả:
  | kết quả `bybit BTC` ở chi phí 0 | kết luận |
  |---|---|
  | **âm**, hai thước đo đồng dấu | **market type** quyết định dấu, không phải broker |
  | **dương**, hai thước đo đồng dấu | **riêng binance** là ngoại lệ; broker quyết định dấu |
  | hai thước đo **ngược dấu** | mơ hồ — không kết luận |
  `bybit BTC` là **ô sắc bén** vì nó giữ `market_type = perpetual_future` **cố định**
  trong khi đổi broker khỏi Binance. Nó là BTC chứ không phải XAU, và đó là **một sai
  lệch CÓ CHỦ Ý** khỏi thứ tự XAU-trước thường lệ: `bybit XAUT` là **spot**, nên nó sẽ
  thêm một hạng mục thứ ba **mà không tách được hai giả thuyết đang có trên bàn**.
  | fee/slippage | trade | **realized_pnl** | pnl/trade | không-guard | trade k-guard | cost rej |
  |---|---|---|---|---|---|---|
  | **0 / 0** | 320 | **−0,3654** | **−0,00114** | **−1,0816** | 411 | 0 |
  | 5 / 2 (deploy) | 260 | −2,0694 | −0,00796 | −3,4393 | 339 | 23 |
  **ÂM, và hai thước đo ĐỒNG DẤU.** Quy tắc kích hoạt: **market type quyết định dấu.**
  **BỐN Ô:**
  | route | broker | market | `one_target` 0-cost | gộp/trade | không-guard 0-cost | đồng dấu |
  |---|---|---|---|---|---|---|
  | `exness XAU/USD` | exness | cfd | +1,0997 | **+0,00281** | +1,5993 | có |
  | `exness BTC/USD` | exness | cfd | +0,5634 | **+0,00111** | −0,4548 | **KHÔNG** |
  | **`bybit BTC/USDT`** | **bybit** | **perp** | **−0,3654** | **−0,00114** | **−1,0816** | **có** |
  | `binance BTC/USDT` | binance | perp | −0,4432 | **−0,00093** | −2,0053 | có |
  **BROKER BỊ LOẠI Ở PHÍA ÂM:** Binance và Bybit là **hai sàn khác nhau**, và trên cùng
  market type chúng cho **−0,00093** và **−0,00114** mỗi trade — **cách nhau 20%**, cùng
  dấu, **cả hai thước đo đồng dấu trên cả hai route**. Cách đọc "khớp theo broker" của
  r315 **không sống sót**. Để đối chiếu, hai route Exness CFD cách nhau **87%** — nên
  **cặp perpetual mới là cụm CHẶT HƠN**.
  **CÁI VẪN CÒN BỊ TRỘN:** **mọi route CFD đều là Exness.** Nên ở **phía dương**, "cfd"
  và "exness" **vẫn tangled y như cũ** — vòng này chỉ phá được confound **ở nơi hai
  broker chia sẻ một market type**. **Phát biểu sống sót rất hẹp:** *hai broker khác
  nhau, cùng trên perpetual futures, đều có edge thô ÂM; hai route có edge thô DƯƠNG
  trên `one_target` đều là Exness CFD, và MỘT TRONG HAI mơ hồ về dấu giữa các thước đo.*
  **`bybit XAUT` là spot trên một broker ĐÃ CÓ MẶT ở đây**, nên nó thêm **market type
  thứ ba mà không phải dùng lại Binance** — **ô kế tiếp tự nhiên, vẫn chưa chạy**.
  **KHÔNG claim:** rằng market type **GÂY RA** dấu — nó chỉ là ứng viên **duy nhất còn
  đứng TRONG HAI cái đã test**, trên bốn route; **"cfd" vẫn bị trộn hoàn toàn với
  "exness"**, và **chưa có cơ chế nào được thiết lập** — market type là **một CÁI NHÃN
  trên một BÓ khác biệt** (pricing, spread, funding, vi cấu trúc sàn) mà **thiết kế này
  không tách được**. **Không** claim `exness BTC` thuộc phía dương — hai thước đo của nó
  **ngược dấu**, nên **một trong bốn ô KHÔNG vững**. **Hai trên sáu route vẫn chưa có
  cost ablation.** **Không** claim funding giải thích — funding để mặc định 1,0 bps ở mọi
  run và đóng góp **tối đa ~0,11** so với PnL 0,4-4,3, quá nhỏ để quyết định dấu, **nhưng
  chưa được ablate riêng**. Không có PF/win rate/Sharpe/Sortino/drawdown/streak; không
  claim độ lớn; **cả bốn ô đều là một cửa sổ `--days 360` duy nhất**. File:
  `round316-NEEDS-MORE-RESEARCH-broker-is-ruled-out-both-perpetual-routes-lose-at-zero-cost-on-two-different-brokers.md`.

- **Round 317 (2026-08-30) — **"RIÊNG EXNESS" BỊ LOẠI**: `bybit XAUT` spot **cũng
  dương**, với **tỉ lệ edge/chi-phí CAO NHẤT fleet**. Market type và instrument **vẫn
  hoà** — và ô có thể phân định **không chạy được ở cửa sổ này**. 2 container (đúng
  budget), **XAU trước**.**
  **Ô r316 ĐÃ NÊU:** *"`bybit XAUT` là spot trên một broker **đã có mặt**, nên nó thêm
  **market type thứ ba mà không phải dùng lại Binance** — ô kế tiếp tự nhiên, vẫn chưa
  chạy."* Theo r315-r316, **không dự đoán có hướng**; **đăng ký trước CÁCH DIỄN GIẢI**:
  dương+đồng dấu ⇒ **"riêng Exness" bị loại**; âm+đồng dấu ⇒ edge **đặc thù venue Exness
  CFD**; ngược dấu ⇒ mơ hồ.
  | fee/slippage | trade | **realized_pnl** | pnl/trade | không-guard | trade k-guard | cost rej |
  |---|---|---|---|---|---|---|
  | **0 / 0** | 278 | **+0,3427** | **+0,00123** | **+0,0936** | 315 | 0 |
  | 5 / 2 (deploy) | 251 | −0,6070 | −0,00242 | −0,2463 | 311 | 86 |
  **Dương, hai thước đo đồng dấu.** Quy tắc kích hoạt: **"riêng Exness" bị loại** — một
  **market type thứ ba**, trên **một broker khác**, cũng có edge thô dương. **Tỉ lệ
  edge/chi-phí của nó là 33,8% — CAO NHẤT trong mọi route đo được**, vượt 30,1% của
  `exness XAU`; nó cũng có khoản lỗ deploy nhỏ nhất (−0,6070) **đơn giản vì nó giao dịch
  ít nhất**.
  **NĂM Ô:**
  | route | broker | market | asset | 0-cost | gộp/trade | không-guard | đồng dấu |
  |---|---|---|---|---|---|---|---|
  | `exness XAU/USD` | exness | cfd | XAU | +1,0997 | **+0,00281** | +1,5993 | có |
  | `exness BTC/USD` | exness | cfd | BTC | +0,5634 | **+0,00111** | −0,4548 | **KHÔNG** |
  | **`bybit XAUT/USDT`** | **bybit** | **spot** | **XAU** | **+0,3427** | **+0,00123** | **+0,0936** | **có** |
  | `bybit BTC/USDT` | bybit | perp | BTC | −0,3654 | **−0,00114** | −1,0816 | có |
  | `binance BTC/USDT` | binance | perp | BTC | −0,4432 | **−0,00093** | −2,0053 | có |
  **Nhóm theo MARKET TYPE, năm ô tách SẠCH** (cfd 2 + spot 1 **dương**; perpetual 2
  **âm**). **Nhóm theo ASSET thì KHÔNG** (XAU 2 dương; BTC 3 **hỗn hợp**).
  **VÌ SAO VẪN CHƯA PHÂN ĐỊNH ĐƯỢC:** hai ứng viên còn lại **bị trộn bởi CHÍNH việc ô
  nào tồn tại**. **Tương phản NỘI-INSTRUMENT duy nhất** là BTC qua các market type:
  **+0,00111** trên cfd so với **−0,00114** và **−0,00093** trên perp — **thiên về
  MARKET TYPE**, nhưng **dựa hoàn toàn vào `exness BTC`, ô duy nhất mà hai thước đo
  ngược dấu** (r315). Và **không có tương phản NỘI-MARKET-TYPE nào thiên về instrument**:
  cfd có cả XAU lẫn BTC và **cả hai đều dương** (không đổi dấu); perp **chỉ có BTC**
  (không có XAU để so).
  **Ô có thể phân định là `binance XAU/USDT` — XAU trên PERPETUAL FUTURE**: **âm** ⇒
  market type thắng dứt điểm; **dương** ⇒ instrument thắng. **VÀ NÓ KHÔNG CHẠY ĐƯỢC Ở
  CỬA SỔ NÀY**: `binance XAU` chỉ có **262 ngày** lịch sử 5m (bar đầu 2025-12-11, r297)
  và **đóng băng từ 2025-12-26** (r207), nên `--days 360` là **bất khả thi**, còn cửa sổ
  ngắn hơn **phá tính so sánh được** với năm ô này. **Đó là giới hạn cứng của dữ liệu —
  ghi nhận chứ không lách.**
  **KHÔNG claim:** rằng market type **GÂY RA** dấu — nó sống sót **hai** lần loại trừ
  (broker ở r316, "riêng Exness" ở đây) và khớp **5/5** ô, **nhưng** giả thuyết instrument
  **cũng khớp** một khi gạt `exness BTC` sang bên, và market type vẫn là **một cái nhãn
  trên một bó** khác biệt venue mà thiết kế này **không phân rã được**. **Không** claim
  `exness BTC` thuộc phía dương — hai thước đo vẫn ngược dấu, và **lập luận thiên về
  market type dựa đúng vào ô đó**. **Không** claim 33,8% của `bybit XAUT` là cơ hội tốt
  nhất — nó có **ít trade nhất** (278 so với 391-508) nên con số mỗi-trade **nhiễu nhất**,
  và 33,8% vẫn nghĩa là cần **cắt ~66% chi phí** để hoà vốn. Không có PF/win rate/Sharpe/
  Sortino/drawdown/streak (r84); **cả năm ô đều là một cửa sổ `--days 360` duy nhất**.
  File:
  `round317-NEEDS-MORE-RESEARCH-exness-specific-is-ruled-out-bybit-xaut-spot-is-positive-too-market-type-and-instrument-still-tied.md`.

- **Round 318 (2026-08-30) — DATA-ISSUE: **CONTROL THẤT BẠI**. Sự đồng dấu giữa hai
  thước đo **không sống sót** qua thay đổi cửa sổ 110 ngày, nên kết luận cost-ablation
  **KHÔNG chuyển được giữa các cửa sổ**. 2 container (đúng budget), **XAU trước**.**
  **THIẾT KẾ VÀ VÌ SAO CHỌN NÓ:** r317 xác định ô sẽ phân định market-type vs instrument
  — **`binance XAU`, XAU trên perpetual future** — và blocker của nó: chỉ **262 ngày**
  lịch sử 5m nên **không chạy được ở `--days 360`**. Thay vì lách, vòng này **dời TOÀN BỘ
  so sánh** sang một cửa sổ `binance XAU` chịu được, và dùng container thứ hai làm
  **CONTROL**: `bybit XAUT`, vốn **đã biết dương trên cả hai thước đo** ở 360 ngày. Cả hai
  chạy `--days 250`, chi phí 0, cùng ngày.
  **ĐĂNG KÝ TRƯỚC:** control **đổi dấu** ở 250d ⇒ cửa sổ không so sánh được, **VÔ KẾT
  LUẬN**; control giữ + `binance XAU` **âm** và hai thước đo đồng dấu ⇒ **market type
  thắng**; control giữ + `binance XAU` **dương** đồng dấu ⇒ **instrument thắng**;
  `binance XAU` hai thước đo ngược dấu ⇒ mơ hồ.
  | cửa sổ | route | market | asset | `one_target` | không-guard | trade | đồng dấu |
  |---|---|---|---|---|---|---|---|
  | 360d | `exness XAU/USD` | cfd | XAU | +1,0997 | +1,5993 | 391 | có |
  | 360d | `exness BTC/USD` | cfd | BTC | +0,5634 | −0,4548 | 508 | **KHÔNG** |
  | 360d | `bybit XAUT/USDT` | spot | XAU | **+0,3427** | **+0,0936** | 278 | **có** |
  | 360d | `bybit BTC/USDT` | perp | BTC | −0,3654 | −1,0816 | 320 | có |
  | 360d | `binance BTC/USDT` | perp | BTC | −0,4432 | −2,0053 | 479 | có |
  | **250d** | **`binance XAU/USDT`** | **perp** | **XAU** | **−0,4474** | **−0,4543** | 174 | **có** |
  | **250d** | **`bybit XAUT/USDT`** | **spot** | **XAU** | **+0,6346** | **−0,1791** | 192 | **KHÔNG** |
  **`bybit XAUT` đồng dấu DƯƠNG ở 360 ngày và NGƯỢC DẤU ở 250 ngày.** Control **thất
  bại**, và **theo đúng quy tắc của chính tôi, câu hỏi chính là VÔ KẾT LUẬN**.
  **PHÁT HIỆN VỀ PHƯƠNG PHÁP MỚI LÀ KẾT QUẢ THẬT:** r308 lập rằng **A/B ở `--days` cố
  định** là phép so sánh **duy nhất** confound r300 để lại sạch, và r313-r317 dựa vào đó.
  **Điều đó VẪN ĐÚNG — TRONG MỘT CỬA SỔ.** Thứ vòng này cho thấy là phần tôi **giả định
  mà không test**: **KẾT LUẬN KHÔNG CHUYỂN ĐƯỢC GIỮA CÁC CỬA SỔ.** Dấu edge thô của một
  route, và cả việc hai thước đo có **đồng dấu** về nó hay không, **KHÔNG phải thuộc tính
  độc lập cửa sổ** — tôi đã thiết kế vòng này trên giả định ngầm rằng nó là.
  **Vậy bảng năm ô của r313-r317 MÔ TẢ CỬA SỔ 360 NGÀY, KHÔNG PHẢI "FLEET"**: mọi phát
  biểu trong đó (market type tách sạch, asset thì không, "riêng Exness" bị loại) **đều
  bị giới hạn vào cửa sổ đó** và **chưa từng được chứng minh là đúng ở cửa sổ khác**.
  Banner **"SCOPED TO 360 DAYS"** đã gắn lên **r313, r314, r315, r316, r317**.
  **CÁI VẪN NÓI ĐƯỢC:** **`binance XAU` ở 250 ngày ÂM trên CẢ HAI thước đo** (−0,4474 /
  −0,4543; **−0,00257/trade**) — **một ô vững**, và nằm đúng khoảng hai route perpetual
  kia chiếm ở 360 ngày. **Nó CHỈ VỀ PHÍA market type.** Nhưng tương phản mà nó **định**
  nuôi — XAU-trên-perp so với XAU-trên-spot **ở cùng cửa sổ** — **dựa vào `bybit XAUT` ở
  250 ngày, vốn MƠ HỒ**. Đó **đúng là khuyết tật** đã ngăn `exness BTC` phân định câu hỏi
  ở 360 ngày: **phép so sánh quyết định cứ rơi trúng một ô có dấu không vững**.
  **Một quan sát nhỏ, nêu như GIẢ THUYẾT chứ không phải phát hiện:** cả hai ô ngược dấu
  (`exness BTC` @360d, `bybit XAUT` @250d) đều có **|PnL| nhỏ trên cả hai thước đo**,
  khớp với một edge **không phân biệt được với 0**. **Nhưng** `binance XAU` @250d cũng có
  giá trị nhỏ tương tự (−0,45 cả hai) mà **vẫn đồng dấu**, nên **độ lớn một mình không
  giải thích được**, và **số trade cũng không** (508 là cao nhất đo được, 192 thấp nhất).
  **KHÔNG claim:** **bất kỳ câu trả lời nào** cho market type vs instrument — quy tắc
  đăng ký trước trả về **vô kết luận** và tôi **tôn trọng nó** thay vì đọc riêng ô
  `binance XAU`. **Không** claim bức tranh 360 ngày là **sai** — nó **bị giới hạn phạm
  vi**, và không gì trong vòng này mâu thuẫn với nó **ở đó**. **Không** claim
  `binance XAU` âm **nói chung** — một cửa sổ, trên một route mà **checkpoint live có dữ
  liệu thị trường kết thúc 2025-12-25** (r207, r306) **dù** Timescale giữ kline đầy đủ
  tới 2026-08-30 — cặp đôi r306 **ghi nhận và không giải thích**, và **tôi cũng chưa giải
  quyết**. Không có PF/win rate/Sharpe/Sortino/drawdown/streak (r84). File:
  `round318-DATA-ISSUE-the-control-fails-raw-edge-sign-does-not-transfer-across-windows.md`.

- **Round 319 (2026-08-30) — TRÊN Ô MẠNH NHẤT, **DẤU LÀ VỮNG QUA CÁC CỬA SỔ** (dương ở
  250, 360, 500 ngày trên **cả hai** thước đo). **ĐỘ LỚN thì KHÔNG**: edge mỗi trade dao
  động **1,97 lần**, kéo theo cả tỉ lệ edge/chi-phí. 2 container (đúng budget), **XAU
  trước**.**
  **VÌ SAO TEST NÀY:** r318 thấy hai thước đo của `bybit XAUT` **đồng dấu dương ở 360
  ngày và ngược dấu ở 250**, kết luận dấu edge thô **không** độc lập cửa sổ, và **giới
  hạn phạm vi** mọi kết luận r313-r317 vào cửa sổ 360 ngày. **Cảnh báo đó chỉ hữu ích
  nếu tôi biết nó RỘNG ĐẾN ĐÂU**: nếu ngay cả ô mạnh nhất cũng lật, cả mạch cost-ablation
  mô tả **cửa sổ** chứ không phải **route**; nếu chỉ các ô sát-không dịch chuyển, claim
  chính của mạch **sống sót**. `exness XAU` là phép test: ô dương lớn nhất, hai thước đo
  đồng dấu, và là route ưu tiên XAU.
  | `--days` | candle | trade | **`one_target`** | pnl/trade | không-guard | trade k-guard | đồng dấu |
  |---|---|---|---|---|---|---|---|
  | **250** | 48 220 | 304 | **+1,4354** | **+0,00472** | +1,5226 | 380 | **có** |
  | 360 | 69 681 | 391 | **+1,0997** | **+0,00281** | +1,5993 | 472 | **có** |
  | **500** | 96 794 | 549 | **+3,0359** | **+0,00553** | +4,1558 | 668 | **có** |
  **Dương trên cả hai thước đo ở cả ba cửa sổ.** Quy tắc kích hoạt: trên route này
  **dấu VỮNG qua khoảng 250-500 ngày**.
  **BẤT ỔN THỰC SỰ NẰM Ở ĐÂU:** trên **cả chín** ô chi-phí-0 đã đo, **0/3** ô có
  `|one_target| ≥ 1,0` ngược dấu, so với **2/6** ô dưới 1,0 (`exness BTC` @360,
  `bybit XAUT` @250). Vậy **độ lớn lớn LUÔN đi kèm đồng dấu**, còn độ lớn nhỏ là **tung
  đồng xu** (bốn trên sáu ô nhỏ đồng dấu, hai không). Điều này **tinh chỉnh, chứ không
  cứu**, giả thuyết r318 nêu rồi tự mâu thuẫn: độ lớn có vẻ **ĐỦ** cho ổn định, **không
  CẦN**. Với chỉ **ba ô** trên ngưỡng thì **đây là quan sát yếu** và tôi ghi đúng như vậy.
  **Vậy phạm vi hoá của r318 ĐÚNG cho các ô sát-không và QUÁ RỘNG cho ô này**: edge thô
  dương của `exness XAU` — **claim mạnh nhất của r313-r317** — **KHÔNG phải artifact
  360 ngày**. Banner **"PARTIALLY UN-SCOPED"** đã gắn lên r318.
  **NHƯNG ĐỘ LỚN DỊCH CHUYỂN RẤT NHIỀU, VÀ ĐIỀU ĐÓ QUAN TRỌNG:** edge/trade là
  **+0,00472 / +0,00281 / +0,00553** ở 250/360/500 ngày — **dải 1,97 lần** — và **360
  ngày tình cờ là THẤP NHẤT trong ba**. Tiêu đề r313 là edge đáng **30,1%** chi phí khứ
  hồi, cần **cắt 70%**. Suy lại ở từng cửa sổ, dùng chi-phí-mỗi-trade 0,00935 của 360
  ngày (**ước lượng** ở nơi khác — nhánh deploy **không** chạy lại ở 250/500):
  | cửa sổ | edge ÷ chi phí | mức cần cắt |
  |---|---|---|
  | 250d | **50,5%** | 50% |
  | 360d | **30,1%** | 70% |
  | 500d | **59,1%** | 41% |
  **Con số r313 trích là BI QUAN NHẤT trong ba**, và dải trung thực là khoảng **30-60%**,
  cần cắt **41-70%**. Đó là **bức tranh khác về chất** so với một con số đơn lẻ, và nó
  **đổi giọng kết luận mà không đổi chiều**: **edge vẫn KHÔNG bù nổi chi phí ở BẤT KỲ
  cửa sổ nào đã đo**. Banner **"RANGE CORRECTED"** đã gắn lên r313.
  **KHÔNG claim:** rằng ổn định dấu **tổng quát hoá** sang route khác — **một route, ba
  cửa sổ**; các route thực sự đã lật (`bybit XAUT`) và ngược dấu (`exness BTC`) **không
  được test lại ở đây** và cảnh báo r318 **vẫn đứng** cho chúng. **Không** claim độ lớn
  **GÂY RA** đồng dấu — ba ô trên ngưỡng, **đều cùng một route**, là mẫu hình trong mẫu
  nhỏ **chứ không phải quy tắc**. **Không** claim dấu vững **ngoài** 250-500 ngày — r304
  và r312 cho thấy confound cửa sổ **tăng theo độ sâu** và **900 ngày không được test ở
  đây**. **Không** claim dải 30-60% là **đo được** — chỉ điểm 360 ngày có chi-phí-mỗi-
  trade **của chính nó**, hai điểm kia **tái dùng** nó, nên **các tỉ lệ đó là ước lượng**.
  **Không** đổi kết luận về lợi nhuận — thứ dịch chuyển chỉ là **mức cắt chi phí cần
  thiết**. Không có PF/win rate/Sharpe/Sortino/drawdown/streak (r84). File:
  `round319-NEEDS-MORE-RESEARCH-the-sign-is-window-robust-on-the-strongest-cell-but-the-magnitude-swings-2x.md`.

- **Round 320 (2026-08-30) — EDGE THÔ CỦA `binance BTC` **ĐỔI DẤU** ở 500 ngày. Quy tắc
  "perpetual thì âm" là **ARTIFACT 360 NGÀY**, và **đồng dấu giữa hai thước đo KHÔNG
  mua được ổn định qua cửa sổ**. 2 container (đúng budget).**
  **THỨ ĐANG ĐƯỢC TEST:** r319 chỉ ra dấu dương của `exness XAU` vững qua 250-500 ngày
  và **gỡ một phần** phạm vi hoá của r318 dựa trên đó — đồng thời nêu giới hạn: *"rằng
  ổn định dấu **tổng quát hoá** sang route khác. Một route, ba cửa sổ. Các route thực sự
  đã lật (`bybit XAUT`) và ngược dấu (`exness BTC`) **chưa được test lại**."* Vòng này
  dùng một container cho **`bybit XAUT` @500** (hoàn tất ba cửa sổ trên route hay lật) và
  một cho **`binance BTC` @500** — **ô âm chủ lực mà cả kết luận r314 dựa vào**.
  | route | `--days` | trade | **`one_target`** | gộp/trade | không-guard | đồng dấu |
  |---|---|---|---|---|---|---|
  | `exness XAU/USD` | 250 | 304 | +1,4354 | +0,00472 | +1,5226 | có |
  | `exness XAU/USD` | 360 | 391 | +1,0997 | +0,00281 | +1,5993 | có |
  | `exness XAU/USD` | 500 | 549 | +3,0359 | +0,00553 | +4,1558 | có |
  | `bybit XAUT/USDT` | 250 | 192 | +0,6346 | +0,00331 | **−0,1791** | **KHÔNG** |
  | `bybit XAUT/USDT` | 360 | 278 | +0,3427 | +0,00123 | +0,0936 | có |
  | **`bybit XAUT/USDT`** | **500** | 349 | +0,5945 | +0,00170 | **−0,2936** | **KHÔNG** |
  | `binance BTC/USDT` | 360 | 479 | **−0,4432** | **−0,00093** | −2,0053 | có |
  | **`binance BTC/USDT`** | **500** | 515 | **+1,7176** | **+0,00334** | +0,3089 | **có** |
  **`binance BTC` LẬT DẤU: −0,4432 ở 360 ngày và +1,7176 ở 500 ngày — và HAI THƯỚC ĐO
  ĐỒNG DẤU Ở CẢ HAI CỬA SỔ.** Edge gộp/trade đi từ **−0,00093** lên **+0,00334**, ở 500
  ngày **vượt cả +0,00281 của `exness XAU` ở 360 ngày**. **Claim trung tâm của r314 —
  "tín hiệu thô của `binance BTC` không có lãi trước mọi ma sát nên không phép giảm chi
  phí nào cứu được" — ĐÚNG ở 360 ngày và SAI ở 500.**
  Và nó **chốt một điều r319 để ngầm**: **đồng dấu giữa hai thước đo và ổn định qua cửa
  sổ là HAI THUỘC TÍNH ĐỘC LẬP** — `binance BTC` **đồng dấu ở cả hai cửa sổ mà vẫn lật**.
  **`bybit XAUT` BẤT ỔN KINH NIÊN:** `one_target` dương ở cả ba cửa sổ nhưng không-guard
  chạy **−0,1791 / +0,0936 / −0,2936** — **ngược dấu ở 2/3 cửa sổ**. Theo quy tắc đăng ký
  trước, **claim dựa trên route đó là KHÔNG DÙNG ĐƯỢC** — đáng chú ý vì **r317 dùng nó để
  loại "riêng Exness"** và **r318 dùng nó làm CONTROL**.
  **ĐIỀU NÀY LÀM GÌ VỚI r314-r317:** bảng năm ô đo **toàn bộ ở 360 ngày**, và trong ba
  route nay đã test ổn định cửa sổ **chỉ MỘT dùng được**: `exness XAU` (dấu dương 3/3,
  đồng dấu 3/3 — **dùng được**); `bybit XAUT` (dấu `one_target` ổn nhưng **ngược dấu
  2/3** — **không dùng được**); `binance BTC` (**dấu LẬT**, đồng dấu 2/2 — **giới hạn
  cửa sổ**). Vậy: **r314 "cost-driven không tổng quát hoá" TỰ NÓ bị giới hạn cửa sổ**;
  **r316 "broker bị loại, cả hai perpetual đều âm" LÀ ĐẶC THÙ 360 NGÀY** vì **một trong
  hai perpetual đó DƯƠNG ở 500 ngày**; **r317 phân tách market-type sạch cũng vậy**; và
  **phần gỡ phạm vi của r319 dựa trên đúng cái route hoá ra là NGOẠI LỆ** — **cảnh báo
  gốc của r318 gần đúng hơn r319 cho phép**. Banner đã gắn lên **r314, r316, r317,
  r319**. **Claim duy nhất còn nguyên không điều kiện là edge thô dương của
  `exness XAU`**, ổn định cả dấu lẫn thước đo qua 250-500 ngày.
  **KHÔNG claim:** rằng `binance BTC` **CÓ** edge thô dương — nó có ở 500 ngày và không
  ở 360; thứ được thiết lập là **DẤU PHỤ THUỘC CỬA SỔ**, một phát biểu **yếu hơn và tổn
  hại hơn** cả hai cách đọc đơn lẻ. **Không** claim kết luận market-type/instrument nào —
  r316-r317 nay dựa trên một cửa sổ mà **một ô của chúng có dấu ngược lại**, và tôi
  **không** đề xuất quy tắc thay thế. **Không** claim `exness XAU` sẽ vững **ngoài**
  250-500 ngày (r304/r312: confound tăng theo độ sâu; **900 ngày chưa test** trên thước
  đo này). **Không** claim cửa sổ nào là "đúng" — **không cửa sổ nào được đặc quyền**,
  mạch này **không có cách chọn**, và **đó là trạng thái trung thực**. Không có PF/win
  rate/Sharpe/Sortino/drawdown/streak (r84). File:
  `round320-REJECTED-binance-btc-raw-edge-flips-sign-at-500-days-so-the-perpetual-negative-rule-is-a-360-day-artifact.md`.

- **Round 321 (2026-08-30) — **CLAIM DUY NHẤT CÒN SỐNG ĐỨNG VỮNG QUA 250-900 NGÀY**:
  mười trên mười giá trị đều dương. Nhưng **hai cửa sổ SÂU NHẤT cho hai tỉ lệ edge/chi-phí
  THẤP NHẤT**. 2 container (đúng budget), **XAU trước**.**
  **GIỚI HẠN r320 ĐÃ NÊU:** r320 phá phần lớn mạch cost-ablation (`binance BTC` **lật
  dấu** giữa 360 và 500 ngày ⇒ quy tắc "perpetual thì âm" là **artifact 360 ngày**;
  `bybit XAUT` ngược dấu ở 2/3 cửa sổ) và khép lại bằng: *"rằng `exness XAU` sẽ vững
  **ngoài** 250-500 ngày. r304 và r312 cho thấy confound cửa sổ **tăng theo độ sâu** và
  **900 ngày chưa được test**."* **Đó là toàn bộ câu hỏi còn lại**: `exness XAU` là ô
  **DUY NHẤT** còn dùng được, và nếu nó hỏng ở độ sâu thì **không gì trong mạch sống sót**
  như một claim mức-route. 900 ngày **đúng là nơi** r312 đo confound nhiễu loạn ở **10
  lần** kích thước 260-ngày trên `binance BTC` — nên **đây là phép test khó, không phải
  thủ tục**.
  | `--days` | candle | trade | **`one_target`** | gộp/trade | **không-guard** | trade k-guard | đồng dấu |
  |---|---|---|---|---|---|---|---|
  | 250 | 48 220 | 304 | **+1,4354** | +0,00472 | **+1,5226** | 380 | có |
  | 360 | 69 681 | 391 | **+1,0997** | +0,00281 | **+1,5993** | 472 | có |
  | 500 | 96 794 | 549 | **+3,0359** | +0,00553 | **+4,1558** | 668 | có |
  | **700** | 135 548 | 645 | **+1,7832** | +0,00276 | **+2,8799** | 759 | **có** |
  | **900** | 174 394 | 715 | **+1,7386** | +0,00243 | **+2,6777** | 830 | **có** |
  **Mười trên mười giá trị dương; hai thước đo đồng dấu ở cả năm cửa sổ.** Quy tắc kích
  hoạt: edge thô dương của `exness XAU` **vững qua 250-900 ngày** — dải **3,6 lần** độ
  dài cửa sổ, **bao gồm cả độ sâu nơi confound tệ nhất**. Sau khi r320 gỡ bỏ câu chuyện
  market-type, quy tắc perpetual-âm và ô `bybit XAUT`, **đây là thứ còn lại của mạch** —
  và nó nay **được test rộng hơn hẳn mọi thứ khác trong mạch**.
  **ĐỘ LỚN VẪN KHÔNG VỮNG, VÀ ĐẦU SÂU LÀ ĐẦU BI QUAN:**
  | `--days` | trade/tuần | gộp/trade | edge ÷ chi phí* |
  |---|---|---|---|
  | 250 | 8,51 | +0,00472 | **50,5%** |
  | 360 | 7,60 | +0,00281 | 30,1% |
  | 500 | 7,69 | +0,00553 | **59,1%** |
  | 700 | 6,45 | +0,00276 | 29,6% |
  | **900** | 5,56 | **+0,00243** | **26,0%** |
  *\* dùng chi-phí-mỗi-trade 0,00935 của 360 ngày; là **ước lượng** ở bốn cửa sổ kia vì
  nhánh deploy chỉ chạy ở 360.*
  Edge/trade trải **2,27 lần** (0,00243-0,00553), **rộng hơn** 1,97x mà r319 thấy trên ba
  cửa sổ. Dải "30-60%" của r319 **nay phải đọc là 26-59%**, cần cắt **41-74%**.
  **Hai cửa sổ sâu nhất cho hai tỉ lệ thấp nhất** (29,6% và 26,0%). **Không có xu hướng
  đơn điệu** trên cả năm (50,5 / 30,1 / 59,1 / 29,6 / 26,0) nên tôi **không** claim tỉ lệ
  giảm theo độ sâu; điều công bằng để nói là **đầu lạc quan của dải đến từ các cửa sổ
  NÔNG, còn đầu sâu thì bi quan đồng loạt**. Trade rate cũng giảm theo độ sâu (8,51 →
  5,56/tuần), khớp các lát sâu thấp hơn của r293 — **không phải phát hiện mới**, và
  r300-r312 áp cho các rate đó y như mọi rate khác.
  **KHÔNG claim:** rằng **bất kỳ route nào khác** có dấu edge thô ổn định — **một route**;
  r320 cho thấy `binance BTC` **lật** và `bybit XAUT` **ngược dấu 2/3**, còn `exness BTC`,
  `bybit BTC`, `binance XAU` **mỗi cái chỉ một cửa sổ**; **điều này KHÔNG tổng quát hoá**.
  **Không** claim tỉ lệ **giảm theo độ sâu** — dãy không đơn điệu, "hai cửa sổ sâu thấp
  nhất" là **quan sát trên năm điểm, không phải xu hướng**. **Không** claim dải 26-59% là
  **đo được** — chỉ điểm 360 ngày có chi-phí-mỗi-trade của chính nó. **Không** đổi kết
  luận lợi nhuận — **edge KHÔNG bù nổi chi phí ở BẤT KỲ cửa sổ nào đã đo**. **Không** có
  lời giải vì sao `exness XAU` là route ổn định — r315 đã ghi tôi **không có mô hình nào**
  và vòng này **không cung cấp**. Không có PF/win rate/Sharpe/Sortino/drawdown/streak/SQN
  — đây vẫn là kết quả **chỉ PnL** và **không phải** đánh giá đa mục tiêu loop yêu cầu.
  File:
  `round321-NEEDS-MORE-RESEARCH-the-one-surviving-claim-holds-across-250-to-900-days-but-the-deep-windows-are-the-pessimistic-end.md`.

- **Round 322 (2026-08-30) — DATA-ISSUE: `edge ÷ chi phí` **KHÔNG PHẢI** tỉ lệ chi-phí-
  mỗi-trade. Mẫu số của nó **bị nhiễm bởi thay đổi LỰA CHỌN TRADE**, tăng từ **4% lên
  43%** theo độ sâu cửa sổ. 2 container (đúng budget), **XAU trước**.**
  **GIỚI HẠN r321 ĐÃ NÊU:** *"rằng dải 26-59% là **đo được**. Chỉ điểm 360 ngày có
  chi-phí-mỗi-trade của chính nó; bốn điểm kia **tái dùng** nó nên **là ước lượng**."*
  Rẻ để sửa **ở đúng đầu quan trọng**: các cửa sổ **sâu** cho tỉ lệ bi quan nhất, và
  **26,0% ở 900 ngày** là con số dẫn tới "cần cắt 74% chi phí". Vòng này chạy **nhánh
  chi-phí-deploy** ở 700 và 900 ngày để **đo** thay vì suy.
  **ĐĂNG KÝ TRƯỚC:** edge/chi-phí **đo được** ở 900 ngày nằm trong **±25%** của ước lượng
  26,0% — tức **19,5%-32,5%**; bác bỏ nếu ngoài, khi đó chi-phí-mỗi-trade thay đổi theo
  cửa sổ và **cả dải ước lượng không đáng tin**.
  | `--days` | trade 0-cost | pnl 0-cost | trade deploy | pnl deploy | gộp/tr | net/tr | **cp/tr** | **edge÷cp** | cần cắt |
  |---|---|---|---|---|---|---|---|---|---|
  | 360 | 391 | +1,0997 | 374 | −2,4441 | +0,00281 | −0,00654 | **0,00935** | **30,1%** | 70% |
  | **700** | 645 | +1,7832 | **509** | −1,8103 | +0,00276 | −0,00356 | **0,00632** | **43,7%** | 56% |
  | **900** | 715 | +1,7386 | **404** | −3,0651 | +0,00243 | −0,00759 | **0,01002** | **24,3%** | 76% |
  **900 ngày đo được 24,3% so với ước lượng 26,0% — ĐĂNG KÝ TRƯỚC ĐÚNG** (sai 7,0%).
  **Nhưng 700 ngày đo được 43,7% so với ước lượng 29,6% — SAI 32%**: giả định chi-phí
  hằng số phía sau r319 và r321 **sai về chất** ở cửa sổ đó, dù cả hai vòng đều đã đánh
  dấu các con số đó là **ước lượng**.
  **VÌ SAO MẪU SỐ DỊCH CHUYỂN, VÀ VÌ SAO CÁI TÊN SAI:** dưới sizing `fixed_notional`,
  chi phí mỗi fill **lẽ ra hằng số**, nhưng `cost/trade` **dịch 1,58 lần** (0,00632 →
  0,01002). Lý do: `cost/trade` như tôi tính là `gộp/trade − net/trade` — **hiệu của HAI
  TRUNG BÌNH TRÊN HAI QUẦN THỂ TRADE KHÁC NHAU**:
  | `--days` | trade ở 0-cost | trade deploy | **giảm** |
  |---|---|---|---|
  | 360 | 391 | 374 | **−4,3%** |
  | 700 | 645 | 509 | **−21,1%** |
  | 900 | 715 | 404 | **−43,5%** |
  **Nhánh deploy mất trade ngày càng nhiều khi cửa sổ sâu hơn** — tới 900 ngày nó giao
  dịch **ít hơn 43,5%**. Vậy đại lượng tôi vẫn gọi là "chi phí mỗi trade" **hấp thụ một
  THAY ĐỔI LỰA CHỌN, không chỉ một CHI PHÍ**, và `edge ÷ chi phí` **không phải** thứ mà
  cái tên gợi ra.
  Lưu ý: **số lần từ chối `execution_cost` KHÔNG tự giải thích được mẫu hình** — **181,
  236, 120** ở 360/700/900, **không đơn điệu** trong khi mức giảm trade **thì đơn điệu**.
  Vậy trade bị mất qua **nhiều hơn** những lần từ chối tường minh của cost gate, và **tôi
  chưa xác định được phần còn lại của con đường đó**.
  **ĐIỀU NÀY LÀM GÌ VỚI DẢI ĐÃ CÔNG BỐ:** r319/r321 trích **26-59%** (cắt 41-74%) từ
  **một điểm đo và bốn ước lượng**. **Ba điểm ĐO ĐƯỢC là 30,1%, 43,7% và 24,3%**, cần cắt
  **56-76%**. Con số **59,1% ở 500 ngày vẫn là ước lượng** và — vì sai số 700 ngày lệch
  về phía **lạc quan** — nên coi là **chưa xác minh**, không phải đỉnh của một dải.
  **Chiều không đổi: edge KHÔNG bù nổi chi phí ở bất kỳ cửa sổ nào đã đo.** Banner
  **"RATIO RECOMPUTED FROM MEASURED ARMS"** đã gắn lên r319 và r321.
  **KHÔNG claim:** **bất kỳ cơ chế nào** cho việc mất trade tăng dần — số từ chối của
  cost gate **không khớp**, nên có thứ khác đang loại trade ở độ sâu và **tôi chưa tìm
  ra**; **tôi không đề xuất ứng viên** (r279-r284 là lý do thường trực, và r312 đã cho
  thấy một cơ chế của chính tôi dự đoán sai). **Không** claim tỉ lệ đúng là 24-44% — ba
  điểm đo trên **một route**, và r300-r312 nghĩa là **không điểm nào độc lập cửa sổ**.
  **Không** claim 500 ngày là 59,1% — điểm đó **kém tin cậy nhất trong năm**. **Không**
  đổi kết luận lợi nhuận, và **không** có PF/win rate/Sharpe/Sortino/drawdown/streak/SQN.
  **Không** claim kết quả **DẤU** của `exness XAU` bị ảnh hưởng: **mười-trên-mười giá trị
  0-cost dương của r321 KHÔNG bị đụng tới** — **khuyết tật nằm ở TỈ LỆ, không ở phép đo
  0-cost**. File:
  `round322-DATA-ISSUE-the-edge-to-cost-ratio-is-contaminated-by-trade-selection-that-grows-with-depth.md`.

- **Round 323 (2026-08-30) — "CON ĐƯỜNG CHƯA XÁC ĐỊNH" HOÁ RA **CHÍNH LÀ COST GATE**.
  Thứ thay đổi không phải *đường nào* mà là **SỐ TRADE MẤT TRÊN MỖI LẦN TỪ CHỐI — 0,055
  lên 3,24, dao động 59 LẦN theo độ sâu**. KHÔNG CONTAINER, KHÔNG SSH.**
  **GIỚI HẠN r322 ĐÃ NÊU:** nhánh deploy giao dịch ít hơn **4,3% / 21,1% / 43,5%** ở
  360/700/900 ngày trong khi từ chối `execution_cost` chạy **181 / 236 / 120** — *không
  đơn điệu* — và kết luận: *"trade bị mất qua **nhiều hơn** những lần từ chối tường minh
  của cost gate, và **tôi chưa xác định được phần còn lại**."* **Sáu report đã nằm sẵn
  trên đĩa với đầy đủ counter**; vòng này **lấy hiệu tất cả**.
  | | 360d | 700d | 900d |
  |---|---|---|---|
  | `decision_count` 0-cost vs deploy | 66 079 / **66 079** | 128 896 / **128 896** | 165 687 / **165 687** |
  | Δ `one_target` | −17 | −136 | **−311** |
  | Δ không-guard | −10 | −150 | **−389** |
  | từ chối `execution_cost` | 181 | 236 | **120** |
  | bucket risk khác ≠ 0 | không | không | không |
  **(1) DÒNG DECISION ĐỘC LẬP VỚI CHI PHÍ** — `decision_count` **y hệt** ở cả ba cửa sổ.
  **(2) MẤT MÁT NẰM THƯỢNG NGUỒN HOLD GUARD** — thước đo không-guard mất **NHIỀU HƠN**
  `one_target` ở 700 và 900 ngày. **(3) `execution_cost` là counter DUY NHẤT khác nhau**
  — mọi bucket risk khác **bằng 0 ở cả hai nhánh, mọi cửa sổ**.
  **VẬY CON ĐƯỜNG CHƯA BAO GIỜ THIẾU — KHUNG NHÌN CỦA TÔI SAI.** Chi phí đi vào mô phỏng
  **đúng hai chỗ**: số học PnL (trừ phí mỗi fill — **không thể** đổi *số đếm* trade) và
  **cost gate**. Dưới sizing `fixed_notional`, kích thước vị thế **không** phụ thuộc PnL
  đã thực hiện, và band bảo vệ fractional đặt theo giá vào — **cả hai đều không nhạy chi
  phí**. **BẰNG PHÉP LOẠI TRỪ, với `one_target` và `legacy_selected_rule`, COST GATE LÀ
  CƠ CHẾ DUY NHẤT** qua đó chi phí đổi được số trade. **"Phần còn lại của con đường" mà
  r322 nói KHÔNG TỒN TẠI.**
  Thứ tôi thực sự tìm thấy — và mô tả sai:
  | `--days` | trade không-guard mất | từ chối | **trade mất / lần từ chối** |
  |---|---|---|---|
  | 360 | 10 | 181 | **0,055** |
  | 700 | 150 | 236 | **0,636** |
  | 900 | 389 | 120 | **3,242** |
  **Tỉ lệ chuyển hoá tăng ĐƠN ĐIỆU theo độ sâu — dao động 59 LẦN** — trong khi số từ chối
  thô **thì không**. Một lần từ chối ở 360 ngày gần như không tốn gì; một lần ở 900 ngày
  tốn khoảng **ba trade**. Điều đó **khớp về số học** với việc một lần từ chối **HOÃN**
  một target change chứ không **huỷ** nó — nhưng **tôi KHÔNG xác minh được từ các counter
  này**: cần trace theo từng decision, và **tôi không đề xuất nó như đã lập** (r312 đã cho
  thấy một cơ chế của chính tôi dự đoán sai).
  **QUAN SÁT PHỤ VỀ HOLD GUARD:** `trade_reduction_fraction` đi 0,1716 → 0,1905 ở 360d và
  0,1502 → 0,1642 ở 700d (**guard cắn MẠNH HƠN** dưới chi phí), nhưng ở 900d là
  **0,1386 → 0,0839** — **cắn NHẸ HƠN**. Cách đọc hợp lý: ở độ sâu, **cost gate đã loại
  sẵn những reversal mà guard lẽ ra chặn**. **Ghi như quan sát; tương tác chưa được test
  trực tiếp.** Còn `legacy_grid` hành xử bất nhất đúng như dự kiến (**+388** trade *có*
  chi phí ở 360d so với −1 520 và −1 572 ở 700/900) — **đúng phụ thuộc đường equity mà
  r299 đã ghi**, **không phải phát hiện mới**, và nay còn chứng minh quy tắc "không bao
  giờ lấy hiệu `legacy_grid`" **ngay trong một cửa sổ** qua một thay đổi chi phí.
  Banner **"PATH IDENTIFIED"** đã gắn lên r322.
  **KHÔNG claim:** **cơ chế cascade** — "một lần từ chối HOÃN chứ không HUỶ" khớp số học
  nhưng **chưa được xác minh**, và **không trace theo decision nào được xem xét**.
  **Không** claim **VÌ SAO** tỉ lệ chuyển hoá tăng theo độ sâu — ba điểm, một route,
  **không ứng viên nào được đưa ra** (r279-r284 là lý do thường trực). **Không** claim
  tương tác guard/cost-gate ở 900 ngày là **nhân quả** — một cửa sổ, một quan sát.
  **Không** đổi kết luận lợi nhuận hay tỉ lệ nào — các điểm edge/chi-phí **đo được** của
  r322 (30,1% / 43,7% / 24,3%) **đứng nguyên**; vòng này giải thích **NGUỒN** của thay đổi
  lựa-chọn-trade trong mẫu số, **không phải giá trị của nó**. **Không** claim gì về route
  khác — **cả sáu report đều là `exness XAU`**. File:
  `round323-NEEDS-MORE-RESEARCH-the-missing-path-is-the-cost-gate-what-varies-is-59x-in-trades-lost-per-rejection.md`.

- **Round 324 (2026-08-30) — **ĐÁNH GIÁ ĐA MỤC TIÊU ĐẦU TIÊN** của session. Sharpe
  **−2,33 và −0,86**, tỉ lệ ngày dương **0,40-0,42**, gate **fail SÁU check ở cả hai cửa
  sổ** — đồng thời **xác nhận độc lập GROSS PnL DƯƠNG trước chi phí**. 2 container (đúng
  budget), **XAU trước**.**
  **ĐÓNG MỘT LỖ HỔNG MƯỜI MỘT VÒNG:** mọi vòng từ r313 đều khép lại bằng *"`one_target`
  chỉ báo PnL (r84), nên đây là kết quả **CHỈ PnL** và **KHÔNG PHẢI** đánh giá đa mục
  tiêu mà loop yêu cầu."* Brief thường trực nói rõ: tối ưu **ĐỒNG THỜI** theo lợi nhuận,
  decision rate và tần suất trade, xét PnL, PF, win rate, Sharpe/Sortino, drawdown,
  streak, **SQN** và decision rate, **không bao giờ một metric đơn lẻ**.
  `--daily-profit-gate` **chính là** công cụ đó: đánh giá policy Portfolio **đang deploy**
  trên **holdout**, phát ra scorecard có version. Nó **xung đột** với
  `--portfolio-minimum-hold-decisions` nên cờ đó đã được bỏ.
  | metric | ngưỡng | 360d | | 900d | |
  |---|---|---|---|---|---|
  | ngày holdout | ≥ 90 | 60,0 | **FAIL** | 151,0 | PASS |
  | trade/tuần | ≥ 7,0 | 8,51 | PASS | **6,85** | **FAIL** |
  | tỉ lệ ngày dương | ≥ 0,55 | **0,417** | **FAIL** | **0,404** | **FAIL** |
  | median PnL ngày | ≥ 0,0 | −0,0021 | **FAIL** | 0,0000 | PASS |
  | chuỗi ngày âm dài nhất | ≤ 5 | 4 | PASS | 5 | PASS |
  | drawdown tổng tối đa | ≤ 0,1 | 0,0001 | PASS | 0,0001 | PASS |
  | **Sortino** | ≥ 1,0 | **−3,104** | **FAIL** | **−1,179** | **FAIL** |
  | **Sharpe** | ≥ 1,0 | **−2,329** | **FAIL** | **−0,861** | **FAIL** |
  | **chi phí ÷ gross PnL** | ≤ 0,5 | **9,886** | **FAIL** | **1,527** | **FAIL** |
  **Sáu lỗi ở mỗi cửa sổ.** Holdout 2026-06-19→2026-08-28 (86 trade đóng) và
  2026-03-04→2026-08-28 (174 trade đóng).
  **(1) HIỆU NĂNG ĐIỀU CHỈNH RỦI RO ÂM DỨT KHOÁT Ở CẢ HAI CỬA SỔ** — Sharpe −2,33 và
  −0,86, Sortino −3,10 và −1,18 so với yêu cầu +1,0. Đây là **lần đầu trong session**
  policy đang deploy được phán xét bằng thứ khác ngoài PnL thô, và câu trả lời **rõ
  ràng**; **DẤU của nó ỔN ĐỊNH qua hai cửa sổ**, khác hẳn phần lớn mạch này.
  **(2) GATE XÁC NHẬN ĐỘC LẬP EDGE GỘP DƯƠNG:** `gross_pnl_before_costs` = **+0,053459**
  ở 360 ngày và **+0,781175** ở 900 — **dương ở cả hai**, tính **chỉ trên holdout**, qua
  **một đường code khác và một cách tổng hợp khác** (lợi suất theo ngày) so với cost
  ablation `one_target` của r313-r321. **HAI CÔNG CỤ ĐỘC LẬP NAY ĐỒNG Ý** rằng edge thô
  của `exness XAU` **dương** còn kết quả ròng thì **không**.
  **(3) DRAWDOWN PASS MỘT CÁCH TẦM THƯỜNG VÀ KHÔNG NÓI GÌ** — 0,0001 (0,01%) vì sizing
  `fixed_notional` triển khai ~5 đơn vị trên equity 10 000; **chỉ các check tỉ lệ, chất
  lượng-ngày và chi phí là có tính phân biệt**.
  **(4) TARGET 3 LẬT THÊM LẦN NỮA:** 8,51 trade/tuần ở holdout 360 ngày, **6,85** ở
  holdout 900 ngày.
  **(5) SQN KHÔNG TÍNH ĐƯỢC BẰNG CÔNG CỤ NÀY.** Khối `unavailable_metrics` nêu **ba**:
  `system_quality_number` (*"cần phân phối R-multiple theo từng trade"*),
  `information_ratio` (cần chuỗi benchmark) và `maximum_consecutive_losing_trades`
  (*"cần giữ lại kết quả PnL ròng theo thứ tự từng trade"*). **Brief thường trực có liệt
  kê SQN; hôm nay nó KHÔNG ĐO ĐƯỢC.** Ghi nhận như giới hạn công cụ — **investigation
  only, không áp dụng**.
  **MỘT QUAN SÁT VỀ CHẤT LƯỢNG DỮ LIỆU, KHÔNG PHẢI PHÁT HIỆN:** gate báo
  `input_continuity_failed` trên **7/8 interval**, với số gap **chưa xác minh** lớn ở các
  khung cao (`15m` 245 gap / 10 767 candle; `30m` 243 / 5 381; `1h` 243 / 2 688) trong
  khi **`5m` có `unverified_gap_count: 0`**. **Cách đọc khả dĩ nhất là của r235 — đây là
  THIẾU NHÃN, KHÔNG PHẢI THIẾU DỮ LIỆU**: một lần đóng cửa cuối tuần được gắn nhãn
  verified ở 5m có thể **không** được gắn ở interval tổng hợp; `interval_continuity_
  violations` **bằng 0** trong khối metrics, nhất quán với cách đọc đó. **Tôi ghi nhận
  quan sát và KHÔNG coi nó là defect**; phân biệt hai khả năng cần soi bộ sinh
  gap-metadata, **việc chưa làm**.
  **KHÔNG claim:** rằng `cost/gross` của gate (nghịch đảo thành 10,1% và 65,5%) và
  `edge/cost` mỗi-trade của r322 (24,3-43,7%) **đo cùng một thứ** — **chúng không**
  (khác cách tổng hợp, khác nhịp thời gian) và **không đưa ra phép đối chiếu nào**.
  **Không** claim gì về **năm route còn lại** — gate **chưa chạy** trên chúng. **Không**
  claim các metric này độc lập cửa sổ — **dấu** Sharpe ổn định nhưng **độ lớn khác 2,7
  lần**. **Không** đề xuất **cải tiến ứng viên** nào — vòng này **đo** policy đang deploy,
  **không đề xuất gì**, và **không promotion nào là chính đáng**: verdict của gate là
  **FAIL**, tức **bằng chứng về một vấn đề, KHÔNG PHẢI một thay đổi đã được xác thực**.
  File:
  `round324-NEEDS-MORE-RESEARCH-the-first-joint-objective-evaluation-sharpe-is-negative-at-both-windows-and-sqn-is-untestable.md`.

- **Round 325 (2026-08-30) — **SHARPE VÀ SORTINO ÂM TRÊN BỐN TRÊN BỐN route-window** —
  phát biểu **mức fleet đầu tiên KHÔNG cần differencing**. Và **edge GỘP trước chi phí ÂM
  trên cả hai holdout crypto**. 2 container (đúng budget), **XAU trước** trong số route
  với tới được cửa sổ.**
  **GIỚI HẠN r324 ĐÃ NÊU:** đánh giá đa mục tiêu mới chỉ trên **một route**. Vòng này
  thêm **`bybit XAUT`** (route XAU còn lại với tới được cửa sổ sâu — `binance XAU` chỉ có
  262 ngày) và **`binance BTC`** (flagship), **cả hai ở `--days 500`** để **holdout khớp
  chính xác** (2026-05-22 → 2026-08-30, 101 ngày quan sát).
  **ĐĂNG KÝ TRƯỚC (đăng ký CÁCH DIỄN GIẢI, theo lối r315-r317):** nếu Sharpe âm trên
  **mọi** route đo được thì đó là **thuộc tính mức FLEET không phụ thuộc phép so sánh cửa
  sổ nào** — phát biểu đầu tiên loại đó mà mạch này đưa ra được; nếu route nào Sharpe
  dương thì fleet **không đồng nhất** cả trên mục tiêu đa chiều.
  | route/cửa sổ | holdout | ngày | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | **GỘP** | ròng |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | `exness XAU` @360 | 06-19→08-28 | 60 | 86 | 8,51 | 0,417 | 4 | −3,104 | −2,329 | 9,89 | **+0,0535** | −0,4750 |
  | `exness XAU` @900 | 03-04→08-28 | 151 | 174 | 6,85 | 0,404 | 5 | −1,179 | −0,861 | 1,53 | **+0,7812** | −0,4118 |
  | **`bybit XAUT` @500** | **05-22→08-30** | 101 | 64 | **4,48** | 0,366 | **14** | −1,972 | −1,402 | **30,35** | **−0,0135** | −0,4219 |
  | **`binance BTC` @500** | **05-22→08-30** | 101 | 312 | **21,84** | 0,416 | **7** | **−6,817** | **−6,753** | 1,20 | **−1,7909** | −3,9406 |
  **ĐĂNG KÝ TRƯỚC ĐƯỢC THOẢ — BỐN TRÊN BỐN route-window fail CÙNG BỐN check, không có
  differencing ở bất kỳ đâu trong dẫn xuất:** Sharpe âm 4/4 (−2,33; −0,86; −1,40;
  **−6,75**); Sortino âm 4/4; tỉ lệ ngày dương dưới 0,55 ở 4/4; chi phí÷gộp trên 0,5 ở
  4/4. **Sau một mạch mà gần như MỌI claim mức-route hoá ra bị giới hạn cửa sổ, CÁI NÀY
  THÌ KHÔNG** — mỗi scorecard tính **độc lập trên holdout của chính nó**.
  **EDGE GỘP TRƯỚC CHI PHÍ ÂM TRÊN CẢ HAI HOLDOUT CRYPTO:** `gross_pnl_before_costs` =
  **−0,0135** (`bybit XAUT`) và **−1,7909** (`binance BTC`); check `gross_pnl_positive`
  **fail cả hai** và **pass trên `exness XAU` ở cả hai cửa sổ**. **ĐÂY KHÔNG PHẢI MÂU
  THUẪN VỚI r320**: vòng đó đo `one_target` **chi phí 0 trên TOÀN cửa sổ 500 ngày** (+0,5945
  và +1,7176), còn **gate đo CHỈ ~101 NGÀY CUỐI**. Dương trên 500 ngày và âm trên 101 ngày
  gần nhất là **nhất quán về số học** — đây là khác biệt **GIAI ĐOẠN**, **không phải** bất
  đồng phép đo, và tôi **không** coi nó như vậy. Điều nó **nói** là: trên **giai đoạn gần
  nhất** — cái mà hệ thống deploy đang thực sự sống trong đó — **hai route crypto có edge
  ÂM TRƯỚC MỌI CHI PHÍ**. **`exness XAU` vẫn là route DUY NHẤT dương trước chi phí trên
  MỌI phép đo đã lấy.**
  **HAI QUAN SÁT KHÁC:** **`binance BTC` giao dịch 21,84/tuần trên holdout gần đây** —
  vượt xa vạch 7/tuần và **vượt xa** 8,1-9,5/tuần mà r305 đo trên cửa sổ đầy đủ; **trên
  giai đoạn gần, Target 3 KHÔNG phải vấn đề của route này**. Và **"không lỗ kéo dài" FAIL
  trên cả hai route mới**: chuỗi ngày âm dài nhất **14** (`bybit XAUT`) và **7**
  (`binance BTC`) so với giới hạn 5 (`exness XAU` là 4 và 5) — mục tiêu này **được nêu
  minh thị trong brief** và **đây là lần đầu nó được ĐO**.
  **KHÔNG claim:** rằng các route crypto có edge thô âm **nói chung** — holdout của gate
  là **giai đoạn khác** với cửa sổ đầy đủ của r320, **cả hai cách đọc đều có thể đúng**,
  **không đối chiếu nào được đưa ra và không cần**. **Không** claim kết quả Sharpe 4/4 phủ
  **cả fleet** — ba route, bốn route-window; **`exness BTC`, `bybit BTC`, `binance XAU`
  chưa chạy gate lần nào**. **Không** claim holdout **so sánh được giữa các route**: hai
  run mới **chia sẻ holdout chính xác**, nhưng hai run của `exness XAU` là **giai đoạn
  khác nhau**, nên so sánh dấu gộp giữa các route **KHÔNG khớp** — chạy `exness XAU` ở 500
  ngày sẽ sửa được và **chưa làm**. **Không** đề xuất cải tiến hay promotion nào — gate
  fail khắp nơi, đó là **bằng chứng về một vấn đề, không phải một thay đổi đã xác thực**.
  SQN, information ratio và max consecutive losing trades **vẫn không đo được** (r324).
  File:
  `round325-NEEDS-MORE-RESEARCH-sharpe-is-negative-on-four-of-four-route-windows-and-gross-edge-is-negative-on-both-crypto-holdouts.md`.

- **Round 326 (2026-08-30) — TRÊN **HOLDOUT KHỚP NHAU**, `exness XAU` **VẪN LÀ ROUTE DUY
  NHẤT DƯƠNG TRƯỚC CHI PHÍ**. Và hai route **BẬN NHẤT có Sharpe TỆ NHẤT** — một căng
  thẳng với Target 3, trên bốn điểm. 2 container (đúng budget), **XAU trước**.**
  **GIỚI HẠN r325 ĐÃ NÊU:** *"hai holdout của `exness XAU` là **giai đoạn khác nhau** nên
  so sánh dấu gộp giữa route **KHÔNG khớp** — chạy `exness XAU` ở 500 ngày sẽ sửa và
  **chưa làm**."* Đó là **điểm yếu chịu lực** trong claim dương duy nhất của fleet. Vòng
  này chạy **`exness XAU` @500** để khớp, và dùng container thứ hai cho **`exness BTC`**
  — ô mơ hồ về dấu từ r315, **chưa từng được gate**.
  **ĐĂNG KÝ TRƯỚC:** nếu `exness XAU` **vẫn** là route **duy nhất** có
  `gross_pnl_before_costs` dương khi holdout đã khớp thì claim **sống sót**; nếu nó âm
  thì "route duy nhất dương trước chi phí" là **artifact giai đoạn** và **sụp**.
  | route | kết thúc | ngày | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | **GỘP** | ròng |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | **`exness XAU/USD`** | 08-28 | 84 | 126 | 8,95 | 0,429 | 4 | −1,152 | **−0,814** | 1,38 | **+0,6000** | −0,2283 |
  | `bybit XAUT/USDT` | 08-30 | 101 | 64 | 4,48 | 0,366 | **14** | −1,972 | −1,402 | **30,35** | −0,0135 | −0,4219 |
  | `binance BTC/USDT` | 08-30 | 101 | 312 | 21,84 | 0,416 | 7 | −6,817 | −6,753 | 1,20 | −1,7909 | −3,9406 |
  | **`exness BTC/USD`** | 08-30 | 101 | 351 | **24,58** | 0,406 | 6 | **−7,514** | **−7,558** | 1,12 | **−2,1633** | **−4,5772** |
  **`exness XAU` VẪN LÀ ROUTE DUY NHẤT có gross PnL dương trước chi phí (+0,6000)** —
  **đăng ký trước ĐÚNG, claim KHÔNG phải artifact giai đoạn**; ba route kia đều fail
  `gross_pnl_positive`.
  **KHỚP HOLDOUT, NÓI THẲNG:** ngày bắt đầu **giống hệt**; `exness XAU` kết thúc
  2026-08-28 (**84** ngày quan sát) còn ba route kia 2026-08-30 (**101**) — đó là **đóng
  cửa cuối tuần của gold CFD**, và `exness BTC` **cũng là Exness CFD** nhưng **có** giao
  dịch cuối tuần, nên khác biệt là **lịch thị trường của instrument**, không phải lỗi
  thiết kế. **Khớp tốt hơn r325 nhiều, KHÔNG chính xác tuyệt đối, và KHÔNG sửa được.**
  **SHARPE NAY ÂM TRÊN SÁU TRÊN SÁU route-window:** `exness XAU` −2,329 / −0,814 / −0,861
  (360/500/900), `exness BTC` **−7,558**, `bybit XAUT` −1,402, `binance BTC` −6,753 —
  cộng với ngày-dương < 0,55 và chi phí÷gộp > 0,5 trên **cả sáu**, **không có differencing
  nào**. `exness BTC` là **route TỆ NHẤT fleet** trên holdout này và còn fail
  `holdout_interval_continuity` (ba route kia thì không).
  **QUAN SÁT ĐÁNG GẮN CỜ — BẬN HƠN THÌ TỆ HƠN:** sắp theo tần suất — `bybit XAUT` 4,48
  (Sharpe −1,402), `exness XAU` 8,95 (−0,814), `binance BTC` 21,84 (−6,753), `exness BTC`
  24,58 (−7,558). **Hai route trên 20 trade/tuần có Sharpe gần −7; hai route dưới 9 có
  Sharpe gần −1.** Spearman(trade/tuần, Sharpe) = **−0,80**, **p hai phía chính xác =
  0,333** trên n=4 — **KHÔNG có ý nghĩa thống kê**, và tôi ghi **chỉ như một quan sát**.
  **Nó quan trọng** vì chỉ **ngược chiều Target 3**, vốn đẩy tần suất **LÊN**: nếu chiều
  này là thật, tăng tần suất sẽ đẩy các route **về phía góc `exness BTC`**. Bốn điểm
  **không lập được** điều đó, và **r274 đã tìm thấy một đòn bẩy tần suất mua 2,43x trade
  với 2,27x lỗ** — **cùng chiều, phương pháp độc lập**. **Tôi KHÔNG claim quan hệ nhân
  quả**: bốn điểm, p = 0,33, và các route khác nhau về **instrument, broker và market
  type** chứ không chỉ tần suất.
  **KHÔNG claim:** rằng gross dương của `exness XAU` **có ý nghĩa kinh tế** — +0,6000 ở
  đơn vị notional simulator trên 84 ngày, route có **ròng −0,2283** và cp÷gộp **1,38**;
  nó vẫn cần cắt chi phí **~28%** chỉ để hoà vốn **trên holdout này**, còn gate yêu cầu
  cp÷gộp **≤ 0,5**. **Không** claim gì về `bybit BTC` hay `binance XAU` — **hai trên sáu
  route vẫn chưa chạy gate**, và `binance XAU` **không với tới `--days 500`** (262 ngày
  lịch sử). **Không** đề xuất cải tiến hay promotion — **mọi route đều fail gate**. File:
  `round326-NEEDS-MORE-RESEARCH-on-a-matched-holdout-exness-xau-is-still-the-only-route-positive-before-costs-and-the-busiest-routes-have-the-worst-sharpe.md`.

- **Round 327 (2026-08-30) — FLEET **HOÀN TẤT**. `exness XAU` **vẫn dương duy nhất trước
  chi phí** trên **năm route khớp**, quan hệ tần-suất/Sharpe mạnh lên **ρ = −0,900** — và
  **ngưỡng ý nghĩa tôi đăng ký trước BỊ ĐẶC TẢ SAI**. 2 container (đúng budget).**
  **CÁC GIỚI HẠN r326 ĐÃ NÊU:** *"bất cứ điều gì về `bybit BTC` hay `binance XAU` — **hai
  trên sáu route vẫn chưa chạy gate**; `binance XAU` **không với tới `--days 500`**"*, và
  quan sát tần-suất/Sharpe **thiếu lực** ở n=4. Vòng này chạy **`bybit BTC` @500** — ô thứ
  năm của tập khớp — và **`binance XAU` @250**, độ sâu duy nhất nó với tới, **báo cáo
  riêng**.
  **ĐĂNG KÝ TRƯỚC (1):** `exness XAU` vẫn là route khớp **duy nhất** có
  `gross_pnl_before_costs` dương; **bác bỏ nếu `bybit BTC` cũng dương**. **(2):** với n=5,
  nếu **|ρ| ≥ 0,9** thì p hai phía chính xác đạt **0,0167** ⇒ quan hệ có ý nghĩa ở 5%.
  | route | ngày | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | **GỘP** | ròng |
  |---|---|---|---|---|---|---|---|---|---|---|
  | **`exness XAU/USD`** | 84 | 126 | 8,95 | 0,429 | 4 | −1,152 | **−0,814** | 1,38 | **+0,6000** | −0,2283 |
  | `bybit XAUT/USDT` | 101 | 64 | 4,48 | 0,366 | **14** | −1,972 | −1,402 | **30,35** | −0,0135 | −0,4219 |
  | **`bybit BTC/USDT`** | 101 | 172 | **12,04** | 0,386 | 8 | −5,447 | **−4,955** | 1,12 | **−1,2653** | −2,6862 |
  | `binance BTC/USDT` | 101 | 312 | 21,84 | 0,416 | 7 | −6,817 | −6,753 | 1,20 | −1,7909 | −3,9406 |
  | `exness BTC/USD` | 101 | 351 | **24,58** | 0,406 | 6 | −7,514 | **−7,558** | 1,12 | −2,1633 | −4,5772 |
  **ĐĂNG KÝ TRƯỚC (1) ĐÚNG:** `exness XAU` là route khớp **duy nhất** dương trước chi phí;
  `bybit BTC` về **−1,2653** và fail `gross_pnl_positive`. **Sharpe âm trên cả năm route
  khớp** và trên **cả bảy route-window** đã gate.
  **`binance XAU` BÁO CÁO RIÊNG** (không với tới 500 ngày): ở `--days 250`, holdout **51
  ngày — DƯỚI mức tối thiểu 90 ngày của chính gate**, 29 trade, 4,06/tuần, Sharpe −0,879,
  và **GỘP +0,0797 — DƯƠNG**. **Điều đó ảnh hưởng cách phát biểu claim fleet**: "route duy
  nhất dương trước chi phí" **đúng TRÊN TẬP KHỚP**; trên **cả sáu** route ở độ sâu mỗi
  route với tới được thì **HAI route dương** — `exness XAU` (holdout khớp 84 ngày) và
  `binance XAU` (holdout dưới-chuẩn 51 ngày). **Tôi phát biểu cả hai thay vì giữ câu gọn
  gàng hơn.**
  **QUAN HỆ TẦN SUẤT, VÀ NGƯỠNG TÔI ĐẶC TẢ SAI:** sắp theo tần suất — 4,48 (−1,402);
  **8,95 (−0,814)**; 12,04 (−4,955); 21,84 (−6,753); 24,58 (−7,558). **Spearman = −0,900**,
  tăng từ −0,800 ở n=4; thứ tự **chỉ cách hoàn hảo MỘT phép hoán vị kề**.
  **NHƯNG NGƯỠNG ĐĂNG KÝ TRƯỚC CỦA TÔI SAI.** Tôi đăng ký "|ρ| ≥ 0,9 sẽ đạt p = 0,0167 ở
  n=5". **Không đúng.** Tính phân phối hoán vị chính xác ở n=5: **|ρ| ≥ 1,0 → p = 0,0167**;
  **|ρ| ≥ 0,9 → p = 0,0833**; |ρ| ≥ 0,8 → 0,1333; |ρ| ≥ 0,7 → 0,2333. **Chỉ ρ = ±1,0 HOÀN
  HẢO mới đạt 0,0167 ở cỡ mẫu này.** Giá trị quan sát −0,900 cho **p = 0,0833** — gần hơn
  0,3333 của n=4, **vẫn KHÔNG có ý nghĩa ở 5%**, và **vẫn là một quan sát**. **Tôi đã đăng
  ký một tiêu chí mà tôi chưa tính, và tôi ghi lại điều đó** thay vì lặng lẽ báo con số đã
  sửa.
  **KHÔNG claim:** rằng tần suất **GÂY RA** hiệu năng điều-chỉnh-rủi-ro tệ hơn — ρ = −0,900
  với **p = 0,083** trên năm route khác nhau cả về **instrument, broker và market type**;
  r274 cùng chiều bằng phương pháp độc lập, **cả hai đều không phải bằng chứng nhân quả**.
  **Không** claim gross dương của `binance XAU` **so sánh được** với `exness XAU` —
  holdout **dưới mức tối thiểu của chính gate**, trên route có checkpoint live kết thúc
  2025-12-25; **được báo cáo, không được cân đo**. Holdout khớp **không cùng độ dài** (84
  so với 101 ngày, đóng cửa cuối tuần gold CFD). **Cả sáu route đều FAIL gate**, mỗi route
  trên Sharpe, Sortino, ngày-dương và chi phí÷gộp. SQN/information ratio/max consecutive
  losing trades **vẫn không đo được** (r324). File:
  `round327-NEEDS-MORE-RESEARCH-fleet-complete-exness-xau-still-uniquely-positive-on-the-matched-set-and-my-significance-threshold-was-mis-specified.md`.

- **Round 328 (2026-08-30) — TĂNG TẦN SUẤT **KHÔNG TẠO RA EDGE — NÓ NHÂN CHI PHÍ LÊN**.
  Gross PnL **gần như không đổi** qua dải tần suất **7,3 lần** trong khi **lỗ ròng tăng
  142 lần**. Một phép test **có kiểm soát, NỘI-ROUTE**. 2 container (đúng budget), **XAU
  trước**.**
  **BIẾN MỘT TƯƠNG QUAN THÀNH MỘT PHÉP TEST CÓ KIỂM SOÁT:** r326-r327 thấy **giữa các
  route** rằng route bận nhất có Sharpe tệ nhất (ρ = −0,900; p = 0,083) — nhưng đó là
  tương quan trên **đơn vị bị trộn**. Bản sạch là **NỘI MỘT ROUTE**: chỉ đổi đòn bẩy tần
  suất, giữ nguyên route/cửa sổ/holdout, chấm bằng mục tiêu đa chiều.
  **ĐĂNG KÝ TRƯỚC:** nếu căng thẳng là thật trong một route, Sharpe **sắp NGƯỢC** với
  trade/tuần — rộng > deploy > ATR về Sharpe, và rộng < deploy < ATR về tần suất.
  | band | trade | tr/tuần | ngày-dương | chuỗi | Sortino | **Sharpe** | cp÷gộp | **GỘP** | ròng |
  |---|---|---|---|---|---|---|---|---|---|
  | **fractional RỘNG 0,02/0,04** | 96 | **6,82** | 0,417 | 5 | −0,155 | **−0,096** | **1,05** | **+0,6067** | **−0,0301** |
  | fractional deploy 0,01/0,02 | 126 | 8,95 | 0,429 | 4 | −1,152 | −0,814 | 1,38 | +0,6000 | −0,2283 |
  | **ATR 1,5/3,0** | 703 | **49,94** | **0,095** | **16** | −14,802 | **−23,225** | **7,25** | **+0,6839** | **−4,2751** |
  **Cả hai thứ tự đều đúng — dự đoán được xác nhận.**
  **CƠ CHẾ, NÓI THẲNG:** từ rộng sang ATR, **tần suất tăng 7,32 lần** (6,82 → 49,94/tuần)
  trong khi **gross PnL trước chi phí chỉ đổi 1,13 lần** (+0,6067 → +0,6839, tức
  **+12,7%**), **cp÷gộp tăng 6,90 lần** (1,05 → 7,25) và **lỗ ròng tăng 142 LẦN**
  (−0,0301 → −4,2751). **EDGE GỘP GẦN NHƯ PHẲNG QUA DẢI TẦN SUẤT 7,3 LẦN**: đòn bẩy này
  **không tìm ra cơ hội có lãi hơn**, nó tìm ra **nhiều TRADE hơn**, mỗi cái mang cùng chi
  phí khứ hồi — **chi phí co giãn theo số đếm, gross thì không**. Điều này **giải thích**
  phát hiện r274 (2,43x tần suất đổi 2,27x lỗ, PnL mỗi trade gần như không đổi) và **biến
  tương quan chéo-route của r326-r327 thành một kết quả NỘI-ROUTE, MỘT HOLDOUT, MỘT BIẾN**.
  **TARGET 1 VÀ TARGET 3 XUNG ĐỘT TRỰC TIẾP TRÊN ROUTE NÀY**, cùng holdout: band **rộng**
  6,82 trade/tuần **trượt vạch 7/tuần 2,6%** với ròng −0,0301 và Sharpe −0,096; band
  **deploy** 8,95 trade/tuần **đạt vạch** với ròng −0,2283 và Sharpe −0,814. **Cấu hình
  GẦN HOÀ VỐN NHẤT lại là cấu hình FAIL Target 3**: đạt vạch tốn **7,6 lần lỗ ròng** và
  **8,5 lần Sharpe**. Đó không phải cách diễn đạt — đó là **điều hai cấu hình đo được**.
  **VÌ SAO ĐÂY KHÔNG PHẢI PROMOTION:** band rộng **hấp dẫn** (gần hoà vốn, tốt hơn ở mọi
  metric rủi ro) và **KHÔNG** phải candidate promote được: **(1) nó VẪN FAIL GATE** —
  Sharpe −0,096 so với yêu cầu +1,0, ngày-dương 0,417 so với 0,55, cp÷gộp 1,05 so với
  0,5; **nó LỖ ÍT HƠN, nó KHÔNG PASS**. **(2) Một route, một cửa sổ, một holdout** —
  r318-r321 đã lập rằng kết quả mức-route **nhạy cửa sổ**, và **chưa đo lại ở cửa sổ
  khác**. **(3) Nó HY SINH một mục tiêu đã nêu** — chấp nhận nó là đánh đổi Target 3 lấy
  lỗ Target 1 nhỏ hơn, **một quyết định về ƯU TIÊN, không phải một phát hiện nghiên cứu**.
  Điều kiện **đầu tiên** của promotion gate — bằng chứng defensible về một **CẢI TIẾN** —
  **không được thoả** bởi một cấu hình chỉ **lỗ ít hơn** trong khi **fail mọi ngưỡng**.
  **Giữ ở research-only, đúng như gate yêu cầu.**
  **KHÔNG claim:** rằng điều này **tổng quát hoá** sang route khác — **một route**, năm
  route kia **chưa được ladder**, và r320-r321 cho thấy kết quả mức-route **dịch theo cửa
  sổ**. **Không** claim band rộng **trụ được ở cửa sổ khác** — chỉ đo ở `--days 500`, và
  r322 cho thấy hành vi nhánh deploy **đổi đáng kể theo độ sâu**. **Không** claim band
  rộng là **một cải tiến**. **Không** claim gross edge **chính xác hằng số** — nó dịch
  **12,7%** qua dải, nhỏ so với 7,32 lần tần suất nhưng **không phải 0**, và tôi **chưa
  test** 12,7% đó có ý nghĩa không. **Không** đọc ρ = −0,900 chéo-route như **nhân quả**.
  **Cả ba cấu hình đều FAIL gate.** File:
  `round328-REJECTED-raising-trade-frequency-does-not-create-edge-it-multiplies-cost-a-within-route-controlled-test.md`.

- **Round 329 (2026-08-30) — KẾT QUẢ "TẦN SUẤT = BỘ NHÂN CHI PHÍ" **TÁI HIỆN TRÊN
  `binance BTC`** — cả hai thứ tự đều đúng, gross **gần như phẳng** qua dải tần suất
  **5,4 lần**. **ĐỘ LỚN thì khác hẳn**: lỗ ròng xấu đi **2,7 lần** ở đây so với **142
  lần** trên XAU. 2 container (đúng budget).**
  **GIỚI HẠN r328 TỰ NÊU ĐẦU TIÊN:** *"rằng điều này **tổng quát hoá** sang route khác.
  **MỘT ROUTE.** Năm route kia **chưa được ladder**."* Vòng này lặp **ladder y hệt** trên
  **`binance BTC`** — flagship, đã có baseline gate 500 ngày. Là BTC chứ không phải XAU
  **có chủ đích**: route XAU đã ladder vòng trước, và **một phép tái hiện BẮT BUỘC phải
  trên một route KHÁC**.
  **ĐĂNG KÝ TRƯỚC:** Sharpe sắp **ngược** với trade/tuần, và `gross_pnl_before_costs`
  **gần như phẳng** trong khi cp÷gộp tăng; bác bỏ nếu thứ tự Sharpe bị vi phạm hoặc gross
  đổi **tỉ lệ thuận** với tần suất.
  | band | trade | tr/tuần | ngày-dương | chuỗi | Sortino | **Sharpe** | cp÷gộp | gross | ròng |
  |---|---|---|---|---|---|---|---|---|---|
  | rộng 0,02/0,04 | 218 | **15,26** | **0,475** | 10 | −5,984 | **−5,730** | 0,76 | −1,9515 | −3,4406 |
  | deploy 0,01/0,02 | 312 | 21,84 | 0,416 | 7 | −6,817 | −6,753 | 1,20 | −1,7909 | −3,9406 |
  | ATR 1,5/3,0 | 1 176 | **82,32** | **0,139** | **27** | −13,481 | **−18,871** | 6,46 | −1,2520 | **−9,3378** |
  **Cả hai thứ tự đều đúng — dự đoán được xác nhận trên route thứ hai.**
  **CHIỀU TÁI HIỆN, ĐỘ LỚN THÌ KHÔNG:** dải tần suất 7,32x (XAU) vs **5,39x** (BTC); đổi
  gross +12,7% vs **+35,8%**; cp÷gộp 1,05→7,25 vs 0,76→6,46; **lỗ ròng 142x vs 2,7x**;
  Sharpe −0,096→−23,225 vs −5,730→−18,871. **Cơ chế giống nhau trên cả hai: gross gần như
  không nhúc nhích trong khi chi phí co giãn theo SỐ ĐẾM trade** — tăng tần suất 5-7 lần
  chỉ đổi gross 13-36%, **xa tỉ lệ thuận**, nên trade thêm **mang chi phí mà không mang
  edge**. **Bội số lỗ ròng chênh ~50 lần giữa hai route** vì **điểm xuất phát khác nhau**:
  band rộng của XAU **gần hoà vốn** (−0,0301) nên mọi chi phí thêm là một sự tệ đi **tương
  đối** khổng lồ, còn `binance BTC` **đã lỗ sâu** (−3,4406) nên cùng cơ chế dịch nó ít hơn
  nhiều theo tỉ lệ. **Tỉ số gây hiểu nhầm; thứ TÁI HIỆN là CHIỀU và CƠ CHẾ GROSS-PHẲNG.**
  **HAI CẢNH BÁO TRUNG THỰC TỪ RUN NÀY:** **(1) `cp÷gộp` KHÔNG diễn giải được trên
  `binance BTC`** — **cả ba band đều có gross ÂM**, nên "chi phí gấp X lần lợi nhuận gộp"
  **vô nghĩa**; chỉ **CHIỀU** của tỉ số được dùng, còn **mức thì không so sánh được** với
  XAU (nơi gross dương). Check thực sự quan trọng ở route này là `gross_pnl_positive`,
  **cả ba band đều fail**. **(2) Chuỗi ngày âm KHÔNG đi theo tần suất trên route nào**:
  XAU 5/4/16 và BTC 10/7/27 — **cả hai lần, band DEPLOY có chuỗi NGẮN NHẤT**, không phải
  band rộng. **Streak không thuộc mẫu hình và tôi không gộp nó vào.** Cũng đáng ghi:
  band rộng của `binance BTC` có ngày-dương **0,475** — **cao nhất trong mọi cấu hình đo
  được trên cả hai route** — và **vẫn fail** ngưỡng 0,55.
  **KHÔNG claim:** cơ chế đúng trên **bốn route còn lại** — **hai trên sáu** đã ladder.
  **Không** claim bội số lỗ ròng **so sánh được** giữa các route — 142x so với 2,7x phản
  ánh **khoảng cách tới hoà vốn của từng route**, không phải khác biệt cơ chế. **Không**
  claim mức `cp÷gộp` trên `binance BTC` có ý nghĩa. **Không** claim gross **không bị ảnh
  hưởng** bởi tần suất — nó dịch 12,7% và 35,8%, nhỏ so với 5-7 lần nhưng **không phải 0**.
  **Không** claim band rộng **đáng chọn** trên `binance BTC`: nó có Sharpe và ngày-dương
  tốt hơn nhưng **gross TỆ HƠN** (−1,9515 so với −1,7909) và **vẫn fail mọi check**.
  **Không promotion.** **Không** claim độc lập cửa sổ — cả hai ladder chỉ ở `--days 500`.
  File:
  `round329-NEEDS-MORE-RESEARCH-the-frequency-cost-multiplier-replicates-on-a-second-route-in-direction-not-in-magnitude.md`.

- **Round 330 (2026-08-30) — NỚI BAND **RỘNG THÊM NỮA LẠI TỆ ĐI**. Có **CỰC TRỊ TRONG
  MIỀN ở 0,02/0,04**, đòn bẩy **BÃO HOÀ** dưới 0,04, và **KHÔNG cấu hình nào trong dải
  tần suất 8,2 lần đạt hoà vốn**. 2 container (đúng budget), **XAU trước**.**
  **CÂU HỎI r328-r329 MỞ RA:** hai vòng đó cho thấy tăng tần suất nhân chi phí mà không
  tạo edge; bước tiếp theo hiển nhiên là **chạy đòn bẩy theo CHIỀU NGƯỢC LẠI** — band rộng
  0,02/0,04 của `exness XAU` đã về net **−0,0301**, Sharpe **−0,096**, **rất gần hoà vốn**.
  Nới nữa thì tới đâu? **ĐĂNG KÝ TRƯỚC:** nếu chi phí là thứ **duy nhất** tần suất nhân
  lên, nới thêm sẽ **tiếp tục cải thiện net về phía — và có thể vượt — 0**, gross gần như
  phẳng; **bị chặn/bác bỏ nếu gross rơi quá 30% dưới mức +0,60**.
  | band | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | gross | **net** |
  |---|---|---|---|---|---|---|---|---|---|
  | **0,08 / 0,16** | 86 | **6,11** | 0,429 | 5 | −0,725 | −0,445 | 1,31 | **+0,4460** | −0,1396 |
  | **0,04 / 0,08** | 86 | **6,11** | 0,429 | 5 | −0,725 | −0,445 | 1,31 | **+0,4460** | −0,1396 |
  | **0,02 / 0,04** | 96 | 6,82 | 0,417 | 5 | −0,155 | **−0,096** | **1,05** | +0,6067 | **−0,0301** |
  | 0,01 / 0,02 (deploy) | 126 | 8,95 | 0,429 | 4 | −1,152 | −0,814 | 1,38 | +0,6000 | −0,2283 |
  | ATR 1,5 / 3,0 | 703 | 49,94 | 0,095 | 16 | −14,802 | −23,225 | 7,25 | +0,6839 | −4,2751 |
  **(1) ĐÒN BẨY BÃO HOÀ:** `0,04/0,08` và `0,08/0,16` **giống hệt nhau ở MỌI trường**, tới
  chữ số cuối. Ở mức stop ≤ 0,04, **band bảo vệ NGỪNG RÀNG BUỘC hoàn toàn** — mọi close
  đến từ target change. Vậy đòn bẩy có **SÀN ở 6,11 trade/tuần**, và nới quá 0,04 **không
  làm gì cả**.
  **(2) CÓ CỰC TRỊ TRONG MIỀN, VÀ ĐÓ LÀ 0,02/0,04.** Vượt qua nó, nới thêm **LÀM HẠI**:
  gross rơi **+0,6067 → +0,4460 (−26,5%)** trong khi tần suất chỉ giảm 6,82 → 6,11
  (**−10,4%**), nên **net xấu đi 4,6 lần**. **Đó là kỳ vọng đăng ký trước THẤT BẠI**: dưới
  cực trị, band **không còn chỉ cắt chi phí — nó ĐÁNH ĐỔI NHIỀU GROSS HƠN PHẦN NÓ TIẾT
  KIỆM**. Cách đọc hợp lý là take-profit ở 0,04 vẫn bắt được winner còn ở 0,08 thì không
  bao giờ kích hoạt; **tôi KHÔNG có dữ liệu close-reason theo từng trade và KHÔNG khẳng
  định điều đó**.
  **(3) KHÔNG GÌ ĐẠT HOÀ VỐN:** trên **toàn bộ** đòn bẩy — dải tần suất **8,2 lần**, từ
  6,11 tới 49,94 trade/tuần — **net tốt nhất là −0,0301**. **Không cấu hình nào có lãi.**
  Đòn bẩy protective-band, **đẩy tới CẢ HAI giới hạn**, **không thể làm route này có lãi**.
  **(4) VÀ CỰC TRỊ VẪN FAIL MỌI THỨ:** ở 0,02/0,04 route giao dịch **6,82/tuần — DƯỚI vạch
  7/tuần** — và vẫn fail gate ở Sharpe (−0,096 vs +1,0), ngày-dương (0,417 vs 0,55) và
  cp÷gộp (1,05 vs 0,5). **Điểm tốt nhất trên đòn bẩy KHÔNG đạt Target 1 lẫn Target 3.**
  **MỘT SỬA LỖI VỀ CHÍNH TIÊU CHÍ CỦA TÔI:** tôi đăng ký "bị chặn nếu **gross** rơi quá
  30% dưới +0,60". **Gross rơi 25,7% — vừa dưới ngưỡng** — nên **theo đúng chữ nghĩa quy
  tắc của chính tôi** thì run này "không bị chặn", **trong khi net rõ ràng xấu đi** và
  hướng **rõ ràng bị bác**. **TIÊU CHÍ NHẮM SAI CHỖ: tôi đặt ngưỡng lên GROSS trong khi
  đại lượng quyết định là NET.** Đây là **khuyết tật đăng-ký-trước thứ hai trong bốn
  vòng** (r327 đăng ký một ngưỡng ý nghĩa **chưa tính**, sai 5 lần; r330 đăng ký ngưỡng
  **lên sai biến**). Cả hai đều được bắt và ghi ngay trong vòng sinh ra chúng, nhưng mẫu
  hình đáng gọi tên: **khi đăng ký trước, hãy đặt tiêu chí lên ĐÚNG đại lượng mà kết luận
  sẽ xoay quanh, và TÍNH mọi ngưỡng TRƯỚC khi cam kết**.
  **KHÔNG claim:** **vì sao** gross rơi ở band rộng hơn (cần close-reason theo trade, tool
  **không báo**); rằng 0,02/0,04 là **THE** optimum — tốt nhất trong **năm điểm trên lưới
  thô**, **chưa test gì giữa 0,01 và 0,04**; rằng điều này đúng ở route/cửa sổ khác — **một
  route, chỉ `--days 500`**; rằng cực trị **promote được** — nó fail Target 3 **và** ba
  check của gate, **lỗ ít hơn không được gate chấp nhận là cải tiến**. **Mọi route vẫn fail
  gate**, và protective band nay **được chứng minh là không sửa được điều đó** trên route
  duy nhất đã đẩy tới cả hai giới hạn. File:
  `round330-REJECTED-widening-the-band-further-makes-it-worse-there-is-an-interior-optimum-and-it-does-not-reach-break-even.md`.

- **Round 331 (2026-08-30) — **CỰC TRỊ CỦA BAND DI CHUYỂN THEO CỬA SỔ**. Ở 900 ngày,
  band **ĐANG DEPLOY** mới là tốt nhất, không phải 0,02/0,04 đã thắng ở 500. **Tinh chỉnh
  tham số trên một cửa sổ KHÔNG chuyển được sang cửa sổ khác.** 2 container (đúng budget),
  **XAU trước**.**
  **GIỚI HẠN r330 ĐÃ NÊU:** *"rằng điều này đúng ở route/cửa sổ khác. **Một route, chỉ
  `--days 500`**."* Vì r318-r322 đã thấy gần như mọi kết quả mức-route **mong manh theo
  cửa sổ**, câu hỏi là **một CỰC TRỊ THAM SỐ có vững hơn không**. Vòng này chạy lại hai
  band quyết định ở **`--days 900`**, nơi holdout là **151 ngày** và **vượt mức tối thiểu
  90 ngày của chính gate** — **tốt hơn về phương pháp** so với 500 ngày (chỉ cho XAU 84
  ngày).
  **ĐĂNG KÝ TRƯỚC:** nếu hình dạng đòn bẩy **vững theo cửa sổ**, thì ở 900 ngày band
  0,02/0,04 **thắng CẢ** deploy 0,01/0,02 **lẫn** 0,04/0,08 về net, và **không cấu hình
  nào dương**; bác bỏ nếu thứ tự đổi hoặc có net dương.
  | band | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | gross | **net** |
  |---|---|---|---|---|---|---|---|---|---|
  | 0,04 / 0,08 | 109 | 4,29 | 0,391 | 5 | −1,793 | −1,384 | 37,27 | **−0,0207** | **−0,7931** |
  | 0,02 / 0,04 | 128 | 5,04 | 0,397 | 5 | −1,134 | −0,788 | 1,95 | +0,4933 | −0,4695 |
  | **0,01 / 0,02 (deploy)** | 174 | 6,85 | 0,404 | 5 | −1,179 | −0,861 | 1,53 | **+0,7812** | **−0,4118** |
  **THỨ TỰ ĐỔI: band ĐANG DEPLOY có net tốt nhất ở 900 ngày** (−0,4118), vượt 0,02/0,04
  (−0,4695). **Dự đoán bị bác.**
  | band | tr/tuần@500 | net@500 | gross@500 | tr/tuần@900 | net@900 | gross@900 |
  |---|---|---|---|---|---|---|
  | 0,04/0,08 | 6,11 | −0,1396 | +0,4460 | 4,29 | **−0,7931** | **−0,0207** |
  | 0,02/0,04 | 6,82 | **−0,0301** | +0,6067 | 5,04 | −0,4695 | +0,4933 |
  | 0,01/0,02 (deploy) | 8,95 | −0,2283 | +0,6000 | 6,85 | **−0,4118** | +0,7812 |
  **Tốt nhất ở 500 ngày: 0,02/0,04. Tốt nhất ở 900 ngày: band đang deploy.** "Cực trị
  trong miền ở 0,02/0,04" của r330 là **đặc thù 500 ngày**, và **hình dạng cũng khác** —
  cực trị trong miền ở 500 ngày, **đơn điệu-cải-thiện-theo-tần-suất** trên đúng ba điểm
  đó ở 900 ngày. Đây là **một bước leo thang có ý nghĩa của vấn đề trung tâm mạch này**:
  r318-r322 cho thấy **DẤU** mức-route mong manh theo cửa sổ; vòng này cho thấy **CẢ CẤU
  HÌNH THAM SỐ TỐI ƯU CŨNG MONG MANH THEO CỬA SỔ**. **Tinh chỉnh một tham số trên một
  cửa sổ không chuyển sang cửa sổ khác, ngay cả trên cùng một route.** Banner **"500-DAY
  SPECIFIC"** đã gắn lên r330.
  **CÁI CÓ TÁI HIỆN — ba điều đúng ở CẢ HAI cửa sổ:** **(1) không cấu hình nào có lãi** —
  sáu cấu hình qua hai cửa sổ, **mọi net đều âm**; đòn bẩy **không đạt hoà vốn ở cả hai**.
  **(2) band rộng nhất được test là TỆ NHẤT ở cả hai.** **(3) Nới band phá gross, và tệ
  hơn ở độ sâu**: với 0,04/0,08, gross là **+0,4460** ở 500 ngày và **−0,0207** ở 900 —
  **nó thành ÂM**, tức ở cửa sổ đó band rộng **không chỉ đánh đổi edge, nó KHÔNG CÒN edge
  nào trước chi phí**.
  **KHÔNG claim:** rằng band deploy là **tối ưu** ở 900 ngày — nó tốt nhất trong **ba cái
  đã test**, **chưa chạy gì chặt hơn 0,01/0,02** ở cửa sổ đó nên cực trị **có thể nằm bên
  dưới**. **Không** claim **bão hoà** xảy ra ở 900 ngày — **0,08/0,16 KHÔNG được chạy** ở
  cửa sổ này, nên phát hiện bão hoà của r330 **chưa được test ở đây** và tôi **không mang
  nó sang**. **Không** kết luận gì về route khác — chỉ `exness XAU`; ladder `binance BTC`
  **chưa bao giờ được mở rộng xuống** ở bất kỳ cửa sổ nào. **Không** claim cơ chế
  tần-suất-nhân-chi-phí (r328-r329) **bị ảnh hưởng**: cơ chế đó đo trên dải tần suất 5-8
  lần **bao gồm cả band ATR**, còn vòng này so **ba điểm trong một dải tần suất THẤP và
  HẸP** nơi bức tranh rõ ràng khác — **hai điều KHÔNG mâu thuẫn** và tôi **không** coi
  đây là bằng chứng chống lại nó. **Mọi cấu hình ở cả hai cửa sổ đều FAIL gate.** File:
  `round331-REJECTED-the-band-optimum-moves-with-the-window-so-parameter-tuning-on-one-window-does-not-transfer.md`.

- **Round 332 (2026-08-30) — NO-CHANGE: ở 900 ngày **BAND ĐANG DEPLOY LÀ CỰC TRỊ** trong
  năm cấu hình. Và **tần suất tối ưu là ~6,8 trade/tuần ở CẢ HAI cửa sổ** — thứ dịch
  chuyển là **ánh xạ band→tần suất**, không phải cực trị. 2 container (đúng budget),
  **XAU trước**.**
  **LỖ HỔNG r331 ĐÃ GẮN CỜ:** *"nó tốt nhất trong **ba cái đã test**; **chưa chạy gì chặt
  hơn 0,01/0,02** ở cửa sổ đó nên **cực trị có thể nằm bên dưới**."* Ở 900 ngày net cải
  thiện **đơn điệu** theo tần suất qua 4,29 → 5,04 → 6,85, nên **siết chặt thêm** là hướng
  còn mở. **ĐĂNG KÝ TRƯỚC, HAI CHIỀU:** **(A)** nếu xu hướng đơn điệu tiếp diễn, band chặt
  hơn **thắng** net −0,4118; **(B)** nếu có **cực trị trong miền** tại/gần band deploy,
  band chặt hơn **tệ hơn**.
  | band | trade | tr/tuần | ngày-dương | chuỗi | Sortino | Sharpe | cp÷gộp | gross | **net** |
  |---|---|---|---|---|---|---|---|---|---|
  | 0,04 / 0,08 | 109 | 4,29 | 0,391 | 5 | −1,793 | −1,384 | 37,27 | −0,0207 | −0,7931 |
  | 0,02 / 0,04 | 128 | 5,04 | 0,397 | 5 | −1,134 | **−0,788** | 1,95 | +0,4933 | −0,4695 |
  | **0,01 / 0,02 (deploy)** | 174 | **6,85** | 0,404 | 5 | −1,179 | −0,861 | **1,53** | **+0,7812** | **−0,4118** |
  | 0,0075 / 0,015 | 240 | 9,45 | 0,351 | 5 | −3,205 | −2,504 | 2,69 | +0,6660 | −1,1279 |
  | 0,005 / 0,01 | 350 | 13,78 | 0,351 | 6 | −4,758 | −3,969 | 2,85 | +0,8681 | −1,6051 |
  **NHÁNH B KÍCH HOẠT:** siết quá band deploy làm **tệ đi rõ rệt** (−0,4118 → −1,1279 →
  −1,6051). Đường cong **ĐƠN ĐỈNH với đỉnh ĐÚNG TẠI cấu hình đang deploy**, và **band bảo
  vệ đang deploy là CỰC TRỊ trong năm cấu hình đã test ở cửa sổ này**. **Đáng nói thẳng
  sau nhiều vòng toàn tìm ra thứ sai: trên đòn bẩy này, ở cửa sổ này, CẤU HÌNH PRODUCTION
  KHÔNG BỊ CẤU HÌNH SAI.**
  **QUAN SÁT LÀM ĐỔI CÁCH ĐỌC r331:** r331 kết luận "cực trị **di chuyển** theo cửa sổ".
  Với ladder **đã hoàn tất ở cả hai cửa sổ**, cách đọc tốt hơn xuất hiện: **500 ngày** →
  band tối ưu 0,02/0,04 → **6,82 trade/tuần**; **900 ngày** → band tối ưu 0,01/0,02
  (deploy) → **6,85 trade/tuần**. **Band khác nhau; TẦN SUẤT kết quả là 6,82 so với 6,85 —
  lệch dưới 0,4%.** Vậy thứ dịch chuyển giữa hai cửa sổ là **ÁNH XẠ BAND→TẦN SUẤT**,
  **không phải tần suất tối ưu**. Lý do khả dĩ là biến động thị trường hai giai đoạn khác
  nhau nên cùng một band phân số cho tỉ lệ trade khác — **tôi CHƯA test và KHÔNG khẳng
  định**. **Hai điểm là hai điểm**, tôi gắn cờ đây là **một trùng hợp đáng kiểm tra, không
  phải một định luật**. Và **~6,8/tuần nằm NGAY DƯỚI vạch 7/tuần ở CẢ HAI cửa sổ** (−2,6%
  ở 500 ngày, −2,1% ở 900) ⇒ **xung đột Target 1 / Target 3 của r328 nay đúng ở CẢ HAI cửa
  sổ**, không chỉ một.
  **HAI CHI TIẾT TRUNG THỰC:** **(1) Net và Sharpe KHÔNG chọn cùng một cấu hình ở 900
  ngày** — net đỉnh ở 6,85/tuần (−0,4118) còn **Sharpe đỉnh ở 5,04/tuần** (−0,788 so với
  −0,861); trên một mục tiêu **đa chiều**, điều đó quan trọng: hai metric **bất đồng một
  nấc ladder** (ở 500 ngày chúng đồng thuận). **(2) Không gì có lãi** — trên **chín** cấu
  hình phân biệt đã đo ở route này qua hai cửa sổ, net tốt nhất là **−0,0301** và **không
  cái nào dương**.
  **KHÔNG claim:** rằng ~6,8/tuần là tần suất tối ưu **theo nghĩa tổng quát** — hai cửa
  sổ, một route, **lưới thô**: đỉnh thật có thể nằm **bất kỳ đâu giữa 5,04 và 9,45** ở 900
  ngày. **Không** claim **vì sao** ánh xạ band→tần suất dịch chuyển — giải thích theo
  regime biến động **khớp** nhưng **chưa test**, và **không đo biến động theo cửa sổ ở
  đây**. **Không** claim band deploy tối ưu **nói chung** — nó tốt nhất trong năm ở 900
  ngày và **thứ nhì trong bốn** ở 500 ngày; "không bị cấu hình sai" **giới hạn** ở đòn bẩy
  này, route này, cửa sổ này. **Không** claim vòng này cho phép **thay đổi gì** — **nó cho
  phép KHÔNG thay đổi gì, đó chính là phát hiện**. **Không** nói gì về route khác — ladder
  `binance BTC` **chưa bao giờ được mở rộng xuống dưới band deploy** ở bất kỳ cửa sổ nào.
  File:
  `round332-NO-CHANGE-the-deployed-band-is-the-900-day-optimum-and-the-optimal-frequency-is-6-8-per-week-at-both-windows.md`.

- **Round 333 (2026-08-30) — LỜI GIẢI THEO BIẾN ĐỘNG **ĐƯỢC XÁC NHẬN**: đoạn 500-900 ngày
  **êm hơn 42%**, và tỉ số tần suất của cùng một band (1,307x) **khớp** tỉ số biến động
  (1,190x) **trong 10%**. KHÔNG CONTAINER; một truy vấn Timescale read-only. **XAU
  trước**.**
  **GIỚI HẠN r332 ĐÃ NÊU:** *"Lý do khả dĩ là biến động thị trường hai giai đoạn khác nhau
  nên cùng một band phân số cho tỉ lệ trade khác — **tôi CHƯA test và KHÔNG khẳng định**."*
  Điều đó **test được, không cần container**: một band phân số cố định **kích hoạt ÍT hơn
  trong thị trường êm hơn**, nên để đạt cùng tỉ lệ trade trên cửa sổ êm hơn cần band **CHẶT
  hơn** — **đúng chiều đã quan sát** (0,02 ở 500 ngày, 0,01 ở 900).
  **ĐĂNG KÝ TRƯỚC:** ngày 500-900 trước có **biến động 5m THẤP HƠN** ngày 0-500 trước;
  bác bỏ nếu cao hơn hoặc bằng.
  | đoạn | bar | **vol %/5m** | mean \|ret\| % |
  |---|---|---|---|
  | gần 0-500 ngày | 96 738 | **0,09597** | 0,05885 |
  | **cũ 500-900 ngày** | 77 607 | **0,05590** | 0,03710 |
  | toàn 0-900 ngày | 174 345 | 0,08063 | 0,04917 |
  **Đoạn cũ êm hơn 42% — dự đoán ĐƯỢC XÁC NHẬN.** Và vì cửa sổ 900 ngày **chứa** cửa sổ
  500 ngày cộng đoạn êm đó, biến động pha trộn của nó **thấp hơn 16%**.
  **KIỂM TRA ĐỊNH LƯỢNG** — band **deploy** 0,01/0,02 đã chạy ở **cả hai** cửa sổ nên cho
  một so sánh có kiểm soát: tần suất **8,95/tuần (500d) vs 6,85/tuần (900d) = 1,307x**;
  biến động **0,09597 vs 0,08063 = 1,190x**. **Hai tỉ số khớp nhau trong 9,8%**: cùng một
  band, chạy trên cửa sổ êm hơn 16%, cho **ít hơn 31% số trade** — **chiều VÀ độ lớn xấp
  xỉ đều khớp** một cách đọc first-passage (rào phân số cố định bị chạm ít hơn khi biên độ
  nhỏ hơn). Đó chính là cơ chế r332 phỏng đoán, **nay được ĐO trên một nguồn dữ liệu độc
  lập** (giá Timescale) thay vì suy ra từ chính output của backtest.
  **CÁI NÓ KHÔNG GIẢI THÍCH:** tỉ số **band tối ưu** là 0,02/0,01 = **2,00x** so với tỉ số
  biến động **1,19x** — **không khớp**. **Nhưng lưới thô** (0,005 / 0,0075 / 0,01 / 0,02 /
  0,04, hai điểm kề nhau cách nhau **gấp 2** ở đầu trên), nên **2,00x là CẬN TRÊN DO ĐỘ
  PHÂN GIẢI LƯỚI, không phải một dịch chuyển đo được**: **chưa chạy gì giữa 0,01 và 0,02**
  ở cửa sổ nào, và hai cực trị thật có thể **gần nhau hơn nhiều**. Tôi **không** coi đây là
  mâu thuẫn và **không** claim band **co giãn theo** biến động.
  **CÁI NÓ HỖ TRỢ, MỘT CÁCH CẨN THẬN:** nó cho một cách đọc mạch lạc về trùng hợp của
  r332 — nếu **tần suất tối ưu** là thuộc tính của route và band chỉ là **cái núm** để đạt
  tới đó, thì **band PHẢI dịch theo biến động trong khi tần suất đứng yên**. Đó đúng là
  điều cả hai cửa sổ cho thấy. **Hai cửa sổ vẫn là hai cửa sổ**: một route, hai giai đoạn,
  một dự đoán **có hướng** được xác nhận — **một cơ chế CÓ BẰNG CHỨNG HỖ TRỢ, KHÔNG PHẢI
  một định luật đã lập**. Và lưu ý **r296 VÀ r298 đều đã TỪNG BÁC biến động** như lời giải
  cho **những đại lượng KHÁC** trên **cùng route này** (biến thiên rate nội-route, và
  khoảng ngưng `[360,540]`), nên **đây là một thắng lợi HẸP cho biến động, không phải một
  thắng lợi tổng quát**.
  **KHÔNG claim:** rằng band **co giãn theo** biến động (tỉ số 2,00x là **artifact lưới**);
  rằng ~6,8 trade/tuần là tần suất tối ưu **theo nghĩa tổng quát** (không đổi so với r332);
  rằng biến động giải thích **bất cứ thứ gì khác** trên route này; **bất kỳ MÔ HÌNH
  first-passage nào** — sự khớp 1,31x/1,19x **nhất quán với** một mô hình như vậy, tôi
  **không fit gì và không test dạng hàm nào**; và **không** đụng tới kết luận lợi nhuận —
  **không cấu hình nào đo được trên route này ở cửa sổ nào có lãi**. File:
  `round333-NEEDS-MORE-RESEARCH-the-volatility-explanation-is-confirmed-the-older-segment-is-42pct-calmer.md`.

## Round 346 — REJECTED: bỏ protective band **có lãi ở 300 ngày** (Sharpe +3,05) nhưng **tệ hơn deployed 87% ở 900 ngày** — bị bác bỏ ngay trong chính vòng nêu ra nó. Và rủi ro gap-fill của audit đã được **định lượng: 5,08% biên phiên, chặn trên ~2 lần stop**

**Phần 1 — định lượng L1 của audit.** Audit ghi **L1 (P2)**: `try_close_at_protective_level` (`trading_modes.rs:2143-2161`) fill **đúng bằng** giá stop/take, **không mô hình hoá gap**, và `exness XAU` — route duy nhất có gross dương — **đóng cửa mỗi cuối tuần**. **Đăng ký trước dạng phân hoạch**: **G** = tỷ lệ gap tại **biên phiên** vượt stop 1% deployed; **G ≥ 10%** → L1 giữ **P2**; **G < 10%** → **hạ xuống P3**.

Truy vấn Timescale read-only, `exness XAU` 5m từ 2024-09-01, gap = `|open_t − close_{t−1}|/close_{t−1}`, tách theo khoảng cách nến > 2 giờ:

| loại | n | trung bình | max | ≥0,5% | **≥1,0% (stop)** | ≥2,0% (take) |
|---|---|---|---|---|---|---|
| **biên phiên** | 118 | 0,2565% | **2,0030%** | 17 (14,4%) | **6 (5,08%)** | 1 (0,85%) |
| trong phiên | 140.901 | 0,0016% | 1,2958% | 5 (0,004%) | **1 (0,0007%)** | 0 |

**G = 6/118 = 5,08% — dưới mốc. L1 hạ xuống P3.** Hai dữ kiện làm việc hạ cấp này **có căn cứ chứ không phải tiện tay**: (a) **trong phiên, fill đúng giá stop gần như chính xác tuyệt đối** — 1 nến trên 140.901 vượt 1%, tức sai lệch chỉ tập trung ở biên phiên **đúng như audit dự đoán**; (b) **biên độ bị chặn** — gap biên phiên lớn nhất hai năm là **2,0030%** so với stop 1%, **tối đa ~2 lần** khoản lỗ mô hình hoá, trên **khoảng 6 sự kiện trong hai năm**.

**Nhưng phép nối không có sẵn**: tôi đo phân phối gap **của thị trường**, **không** phải việc Portfolio có thật sự giữ vị thế qua sáu biên đó hay không. Mục **L4** của audit (không serialize audit trail theo lệnh) khiến phép nối này **bất khả thi nếu không sửa code**. Phát biểu trung thực: **phơi nhiễm phía thị trường là nhỏ và bị chặn; việc có lệnh nào đã đo bị ảnh hưởng hay không thì công cụ hiện tại không xác định được.**

**Phần 2 — ứng viên nảy sinh, và sự bác bỏ.** `protective: none` bỏ hẳn đường stop/take nên **sai lệch gap-fill vắng mặt theo cấu trúc**:

| cửa sổ | protective | lệnh | /tuần | gross | cost | **net** | Sharpe | Sortino | streak |
|---|---|---|---|---|---|---|---|---|---|
| 300 | fractional 0,01/0,02 | 42 | 5,05 | +0,3391 | 0,3845 | −0,0454 | −0,249 | −0,374 | **3** |
| **300** | **none** | 12 | **1,44** | **+0,5001** | **0,0932** | **+0,4069** | **+3,046** | **+10,18** | 5 |
| 900 | fractional 0,01/0,02 | 174 | 6,85 | +0,7820 | 1,1929 | −0,4110 | −0,860 | −1,177 | 5 |
| **900** | **none** | 104 | 4,10 | **−0,0287** | 0,7389 | **−0,7675** | **−1,361** | −1,661 | 5 |

Ở **300 ngày**, bỏ band **lãi rõ rệt** — và **khác** với phản-thực-tế slippage-0 của Round 344, đây là **cấu hình khả thi**. Ở **900 ngày**, cùng thay đổi đó làm gross **âm** và net **−0,7675 so với −0,4110 của deployed — tệ hơn 87%**. **Ứng viên bị bác bỏ ngay trong vòng nêu ra nó** — đúng kiểu window-fragility của r331/r334/r341 nhưng trên một lever **lớn hơn nhiều**, và phát hiện r345 (nhiễu đầu vào 1,4% → đầu ra 15%) áp dụng **mạnh hơn nhiều** cho một nhiễu cỡ này.

**Và nó trượt joint objective ngay cả ở nơi nó thắng**: 1,44 lệnh/tuần — **hụt 4,9 lần** mốc Target 3, tệ hơn mọi band từng thử — streak **xấu hơn** deployed (5 so với 3), ngày dương 0,451 so với yêu cầu 0,55. **Đọc riêng Target 1 sẽ gọi đây là thắng lớn; đọc cả ba thì nó không phải ứng viên.** Route cũng **vẫn không gate-eligible** ở cả hai cửa sổ.

**Giới hạn**: **không** khẳng định các run no-band **cô lập** được sai lệch gap-fill — chúng bỏ hẳn đường stop, tức đổi **chiến lược** chứ không chỉ mô hình fill, và **không** cho ước lượng nào về mức thổi phồng của các run có band. **Không** khẳng định lệnh nào đã đo bị ảnh hưởng bởi gap-through. **Không** khẳng định phân phối gap hai năm chuyển sang route/giai đoạn khác — chỉ `exness XAU`; route crypto **không có biên phiên**. **Không promote.**

Chi tiết: `research/quant/rounds/round346-REJECTED-dropping-the-protective-band-is-profitable-at-300-days-and-worse-at-900-and-the-gap-fill-risk-is-quantified-small.md`.

## Round 432 — NO-CHANGE: audit toàn bộ `index.md` (mục 0/1/2/3/4/6 và round330-431) không tìm thấy hướng Alpha/Portfolio nào còn mở và chưa test

Zero container, zero SSH tunnel, zero backtest compute. Nhiệm vụ vòng này là
tìm Alpha mới hoặc tối ưu Portfolio bằng backtest thật — trước khi tiêu ngân
sách container, vòng này làm đúng phần tiền đề mà prompt cũng yêu cầu: đọc
lại toàn bộ `index.md` để xác định hướng nào **thật sự** còn mở, tránh chạy
lại đúng câu hỏi corpus đã có kết luận.

**(1) Hướng hoạt động gần nhất — "góc" band 0,02/0,04 + hold 288 (Round
365/366) — đã đóng dứt điểm ở Round 431**, trên cả ba route test được:
`binance BTC` thua trước cả chi phí (Round427); `bybit XAUT` thắng deployed
3/4 cửa sổ rời nhưng không bao giờ gần Target 3 và độ sâu lịch sử đã cạn
(Round428-431, Round431 tự đóng nhánh này); `exness XAU` (nơi góc xuất phát)
chưa từng gate-eligible ở bất kỳ cửa sổ nào (Round335-336).

**(2) Rule 1 (sizing/band/hold Portfolio-construction) đã đóng như một
không gian**, theo đúng mục "Thứ tự ưu tiên" (dòng ~10195-10266): hold
(Round80, đã deploy), stop/take (Round83, đã deploy), tương tác hai lever
sub-additive và production hiện tại là tổ hợp tốt nhất trong 4 (Round87),
sizing mode đã đóng (Round89-90/151-152, chỉ `fixed-pct` tránh được sụp đổ
compounding hình học). Câu hỏi band-optimum được Round330-332 trả lời trực
tiếp: ở `--days 900` trên `exness XAU`, **band đang deploy chính là cực trị
trong miền** trong năm cấu hình đã test — "production KHÔNG BỊ cấu hình
sai". Mục còn ghi "mở" duy nhất (`--portfolio-atr-periods`) không áp dụng
cho production (protective-kind hiện là `fractional`, không phải `atr`), và
nhánh ATR đã xuất hiện như hàng so sánh ở Round329/330 với kết quả tệ hơn
fractional rất nhiều (Sharpe −18,9 tới −23,2 so với −0,1 tới −0,9) — sweep
thêm tham số ATR mà chưa mở lại câu hỏi `protective-kind` (đã đóng, bất lợi)
sẽ không phải cách dùng ngân sách vòng này hợp lý.

**(3) Rule 2/3 (tìm signal Alpha) đã đóng như một không gian ở 5m** theo
mục 3: ~40 cơ chế đã test, 0 cơ chế đạt PF>1 nhất quán qua split/broker/cửa
sổ. Ensemble/regime-switching đã đóng hai lần độc lập (Round54 qua engine
thật; Round67/394-396 cho chính các strategy MTF đang live).

**(4) Các nhánh phụ chiều/guard/cấu trúc chi phí đều đã đóng**: bất đối
xứng long/short là drift chứ không phải edge (Round385-386); guard không
tổng quát hoá (Round371-372); hiệu ứng theo thứ trong tuần trượt permutation
test đăng ký trước (p=0,60, Round354-355); gross gộp qua 9 holdout rời của
cả hạm đội chứa 0 trong khoảng tin cậy, và chính Round400 đã tự đánh giá
thêm điểm holdout nữa "sẽ không đổi câu trả lời", chỉ đáng làm như xác
nhận chứ không phải câu hỏi còn sống (Round398-400).

**(5) Ba hướng còn ghi "mở" trong `index.md`** (quyết định release, định
nghĩa metric Target 2, chờ đủ forward-time) đều bị chặn bởi yếu tố ngoài
phạm vi vòng này theo đúng chỉ dẫn của prompt (quyết định sản phẩm, thời
gian lịch, hạ tầng không truy cập) — không audit lại ngoài việc xác nhận
chúng chưa đổi.

**Kết luận**: không tìm được candidate Alpha mới, không tìm được lever
Portfolio-construction nào còn áp dụng được và chưa test. Không promote,
không implement, không đổi production. File:
`round432-NO-CHANGE-search-space-audit-finds-no-open-untested-alpha-or-portfolio-direction-left-in-431-rounds-of-history.md`.

## Round 431 — REJECTED: holdout tách rời thứ TƯ trên `bybit XAUT` **đảo lại** — corner chỉ thắng deployed **3/4 cửa sổ**, không phải 3/3 như Round430 kết luận, và độ sâu lịch sử đã cạn cho route này

Round430 tự đặt câu hỏi liệu độ sâu lịch sử `bybit XAUT` có còn đủ cho cửa
sổ tách rời thứ tư không. Vòng này chạy đúng cửa sổ đó (`--as-of
2025-12-30T01:15:00.000Z`, lùi thêm ~65 ngày từ điểm bắt đầu holdout
Round430), cùng corner (band 0,02/0,04, hold 288) so với deployed control
(band 0,01/0,02, hold 36) qua `--daily-profit-gate`.

**Cửa sổ D (2025-11-07 → 2025-12-30, 52,53 ngày, candle_count 75640 — nhỏ
hơn cả C's 94549, xác nhận độ sâu lịch sử tiếp tục co lại đúng lo ngại của
Round430; ở `--days 500` nghĩa là lịch sử `bybit XAUT` dùng được chỉ còn tới
khoảng 2025-04):** corner net **−0,01071**/Sharpe **−0,0887** (8 lệnh,
1,066/tuần — mẫu mỏng nhất trong cả chuỗi 4 cửa sổ); deployed net
**+0,01911**/Sharpe **+0,1536** (20 lệnh, 2,665/tuần). **Deployed thắng
corner** ở cửa sổ này — đảo ngược thứ tự đã thấy ở cả 3 cửa sổ trước (A, B,
C).

**Sửa lại tuyên bố "3/3" của Round430:** gộp cả 4 cửa sổ (A=R428, B=R429,
C=R430, D=vòng này), corner chỉ thắng deployed trên net PnL/Sharpe ở **3/4
cửa sổ**, không phải "MỌI cửa sổ" như Round430 khẳng định. Một pattern đạt
chuẩn "3 cửa sổ trở lên" ở đúng lúc đo được 3 cửa sổ không đồng nghĩa nó
sống sót cửa sổ thứ tư — đúng dạng thất bại đã thấy nhiều lần trong arc
(Round340 → Round391, Round371 → Round372). **Không đổi kết luận REJECTED**:
tần suất corner cả 4 cửa sổ (1,066/1,61/2,815/2,878 mỗi tuần) không bao giờ
gần Target 3 (7,0).

**Đóng nhánh disjoint-window cho corner này trên `bybit XAUT`:** candle_count
giảm dần 143998→118185→94549→75640 qua 4 cửa sổ — một cửa sổ thứ năm sẽ còn
ngắn hơn nữa, dưới ngưỡng có ý nghĩa. Không chạy thêm cửa sổ nào cho corner
này trên route này.

**Sửa dữ liệu phụ:** 2 dòng CSV của Round430 (`optimize_loop_update_v2.csv`)
bị thiếu 4 cột cuối (`target1_profitable`/`target2_makedecision`/
`target3_freq_ge1day_or_7week`/`notes`) — lỗi ghi thiếu, đã bổ sung đúng
theo nội dung round430.md trong vòng này (DATA-ISSUE phụ, không phải phát
hiện mới, không đổi kết luận Round430). File: `round431-*.md`.

## Round 430 — REJECTED: holdout tách rời thứ BA trên `bybit XAUT` — corner thắng deployed band về net PnL/Sharpe ở **3/3 cửa sổ**, nhưng tần suất vẫn không bao giờ đạt Target 3

Trả lời dứt điểm câu hỏi Round429 tự nêu: "corner có thắng deployed band ở
MỌI cửa sổ, bất kể dấu tuyệt đối của từng arm không?" Chạy holdout tách rời
thứ ba (`--as-of 2026-03-05T17:00:00Z`, lùi thêm ~65 ngày từ điểm bắt đầu
holdout Round429), cùng corner (band 0.02/0.04, hold 288) so với deployed
control (band 0.01/0.02, hold 36) qua `--daily-profit-gate`.

**Kết quả 3 cửa sổ (net PnL / Sharpe, corner vs deployed):** A (Round428,
99.997 ngày): +0.6246/+0.1380, +2.046/+0.485 → corner thắng. B (Round429,
82.07 ngày): −0.8057/−0.8166, −3.223/−3.428 → corner thắng (ít âm hơn). C
(Round430, 65.66 ngày, cửa sổ này): **+0.1415/−0.1461, +0.572/−0.528** →
corner thắng rõ ràng (đảo dấu hoàn toàn). **Corner thắng deployed ở CẢ 3
cửa sổ** trên net PnL và Sharpe/Sortino — đạt chuẩn "3 cửa sổ trở lên"
Round391-392 đã đặt ra, và Round429 tự nêu là điều kiện cần trước khi gọi
pattern này "established". cost÷gross KHÔNG nhất quán tuyệt đối (B corner
tệ hơn deployed: 2.907 vs 1.723) — chỉ net PnL/Sharpe/Sortino nhất quán cả
3/3.

**KHÔNG mở lại hướng promote.** Tần suất corner cả 3 cửa sổ: 1.61 / 2.815 /
2.878 mỗi tuần — không bao giờ gần ngưỡng Target 3 (7.0). Ở cửa sổ này lần
đầu tiên **deployed** (không phải corner) đạt Target 3 (7.249/tuần) nhưng
lại net-âm — chưa cấu hình nào trên `bybit XAUT` từng vừa có lãi vừa đủ tần
suất trong cùng 1 arm. Chỉ 1/3 cửa sổ (A) đủ điều kiện gate
(`minimum_holdout_days≥90`); B và C đều là cửa sổ partial (lịch sử càng lùi
càng ngắn — 143,998→118,185→94,549 candle) nên là relative-ranking, không
phải gate verdict. Đóng theo đúng kết luận Round366: "mọi cấu hình có lãi
trong arc này đều fail Target 3" — nay có thêm bằng chứng thứ ba trên
`bybit XAUT`. File: `round430-*.md`.

## Round 429 — REJECTED: đọc số Round428 cho `bybit XAUT` **đảo ngược hoàn toàn** trên một holdout tách rời (disjoint)

Round428 tự nêu bước tiếp theo trong mục "what would move this": chạy thêm
holdout tách rời (disjoint) thứ hai/ba trên `bybit XAUT` để xem đọc số
Sharpe/Sortino/gross-dương có sống sót ngoài đúng một cửa sổ hay không, theo
đúng chuẩn Round391-392. Vòng này chạy đúng bước đó bằng `--as-of` dịch về
đúng mốc bắt đầu holdout của Round428 (`2026-05-26T18:40:00Z`), tạo ra
holdout `2026-03-05` → `2026-05-26` (83 ngày quan sát) — không trùng lặp
holdout Round428 (`2026-05-26` → `2026-09-03`) ngoại trừ đúng 1 nến 5 phút
tại ranh giới (0,004% trong 23.637 nến holdout của vòng này, công bố rõ chứ
không làm tròn thành "không trùng"). Cửa sổ cũng là **cửa sổ bộ phận** (chỉ
118.185 nến so với 143.998 của Round428 — lịch sử chỉ chạm tới ~410 ngày
trước mốc as-of này, không đủ 500 ngày yêu cầu), khiến cả hai nhánh đều trượt
`minimum_holdout_days` (82,07 so với ngưỡng 90) — đọc mọi số dưới đây như
xếp hạng tương đối, không phải verdict gate.

**Kết quả đảo ngược hoàn toàn**: corner (band 0,02/0,04, hold 288) đi từ
gross +0,6614/net +0,6246/Sharpe +2,046/Sortino +3,826 (Round428) sang gross
**−0,20623**/net **−0,80573**/Sharpe **−3,223**/Sortino **−4,195** trên
holdout tách rời này — 9/12 check trượt (kể cả `gross_pnl_positive`, vốn đã
ĐẠT ở Round428) so với 4/12 trượt ở Round428. Nhánh deployed control cùng
cửa sổ cũng đảo dấu tương tự (gross +0,5048 → −0,29989, net +0,1379 →
−0,81658) — xác nhận đây là thuộc tính của **cửa sổ**, không riêng cấu hình
corner. Đây là lần đảo-ngược-trên-holdout-tách-rời thứ hai trong toàn bộ arc
(sau phát hiện gross toàn hạm đội của Round391-392), lần này trên
route/cấu hình khác.

**Một điểm sống sót**: xếp hạng tương đối corner > deployed vẫn lặp lại trên
cả hai cửa sổ (mọi metric của corner tốt hơn deployed, dù cả hai đã đổi
dấu) — nhưng 2 cửa sổ đồng thuận về THỨ TỰ chưa đạt chuẩn ≥3 holdout độc lập
mà Round391-392 đặt ra để coi là đã xác lập. Tần suất giao dịch của nhánh
deployed cũng dao động mạnh giữa hai cửa sổ liền kề (4,13/tuần → 6,738/tuần,
+63%, gần Target 3 nhất từng đo trên route này).

**REJECTED**: khép lại đúng câu hỏi Round428 tự đặt ra — đọc số mạnh nhất
toàn arc cho corner này không sống sót qua kiểm tra holdout tách rời đầu
tiên. Cộng với Round427 (`binance BTC` thua trước phí) và tình trạng
không-gate-eligible cấu trúc của `exness XAU` (Round335-336), **không còn
route nào cho ra đọc số corner sống sót dù chỉ một kiểm tra độ vững** — ô
dương duy nhất còn lại (Round428) nay đã được kiểm tra và trượt. Không đổi
production, không implement gì. Hai container đã dọn sạch (`docker ps -a`
rỗng — sau khi lần chạy đầu bị mất log do đua với `--rm`, đã chạy lại đúng 2
container với `docker logs -f` chạy đồng thời, không tốn thêm ngân sách
container vì lần đầu bị mất log trước khi đọc được số nào), tunnel đã đóng
(`ss -tlnp` xác nhận). File:
`round429-REJECTED-the-round428-corner-reading-on-bybit-xaut-reverses-completely-on-a-disjoint-holdout.md`.

## Round 428 — REJECTED: cùng "góc có lãi" Round 365/366 (band 0,02/0,04 + hold 288), lần này trên `bybit XAUT` — đạt Sharpe/Sortino/cost-ratio holdout thật MẠNH NHẤT từ trước tới giờ cho corner này, nhưng vẫn hụt Target 3 tới 4,3 lần

Hoàn tất đúng việc Round427 để mở: "`bybit XAUT` gate-eligible và chưa test
qua unified path". Theo đúng thứ tự ưu tiên XAU trước BTC của prompt vòng
này, chọn `bybit XAUT` (route vàng gate-eligible duy nhất còn lại — `exness
XAU` không gate-eligible ở bất kỳ cửa sổ nào, r335-336) thay vì lặp lại
BTC. Hai container Docker (`--cpus=1 --memory=2g --memory-swap=3g` mỗi
container — tổng 2 CPU/4GB RAM/2GB swap đúng giới hạn vòng này), một SSH
tunnel read-only, cùng route/cửa sổ `bybit spot XAUT/USDT 5m --days 500`:
corner (hold=288, band 0,02/0,04) và control cùng cửa sổ (hold=36, band
0,01/0,02). Cả hai xác nhận `candle_count=143998`,
`holdout_candle_count=28799` (holdout 2026-05-26→2026-09-03, 101 ngày quan
sát) — khớp chính xác với holdout Round427 đo trên `binance BTC`, cùng cửa
sổ lịch.

**Kết quả — khác hẳn `binance BTC`:** cả hai nhánh đều **dương thật** trên
route này (không như BTC gross âm cả hai nhánh). Corner: net **+0,62458**,
gross **+0,66144**, Sharpe **2,046** (ngưỡng 1,0), Sortino **3,826** (ngưỡng
1,0), cost÷gross **0,056** (ngưỡng ≤0,5) — **lần đầu tiên corner này vượt cả
Sharpe lẫn Sortino lẫn cost-ratio trên một holdout thật ở bất kỳ route nào**.
Vẫn trượt gate 4/12 check: `minimum_trades_per_week` (1,61 so với ngưỡng
7,0 — hụt 4,3 lần), `positive_day_ratio` (0,455 so với 0,55),
`median_daily_pnl` (đúng bằng 0,0 — phần lớn 101 ngày không có lệnh đóng nào
trong tổng 23 lệnh), `negative_day_streak` (13 ngày so với ngưỡng 5). Control
deployed cùng cửa sổ cũng dương (+0,13795) nhưng yếu hơn corner mọi chiều
(Sharpe 0,485, Sortino 0,764, cost÷gross 0,727 — trượt cả 3) và **cũng trượt
tần suất** ở route này (4,13/tuần, khác `binance BTC`'s deployed vẫn đạt
13,79/tuần ở Round427) — 8/12 check fail.

**REJECTED**: corner không promote được — hụt tần suất 4,3 lần và 3 check
phân phối ngày, đúng mẫu hình Round366 "mọi cấu hình có lãi đều trượt Target
3" (nay là ô thứ 8 khớp mẫu này). Cũng chưa đủ điều kiện promotion theo
chuẩn chính arc này đặt ra (Round391-392: một holdout không đủ đặc trưng cho
một route — cần ≥3 holdout độc lập). Đóng góp mới của vòng: `bybit XAUT`
gia nhập `exness XAU` (Round343) là route thứ hai có bằng chứng gross dương
tương đối ổn định qua gate; bức tranh 3-route Round427 đặt ra nay hoàn tất
cho 2 route gate-eligible (`binance BTC` thua trước phí, `bybit XAUT` thua
tần suất); `exness XAU` (nơi corner xuất phát) vẫn không thể có verdict gate
ở bất kỳ cửa sổ nào. Không đổi production, không implement gì. Hai container
đã dọn sạch (`docker ps -a` rỗng), tunnel đã đóng (`ss -tlnp` xác nhận). File:
`round428-REJECTED-the-round365-366-corner-clears-sharpe-sortino-and-cost-ratio-on-bybit-xauts-real-holdout-but-still-misses-target-3-by-4.3x.md`.

## Round 427 — REJECTED: "góc có lãi" Round 365/366 (band 0,02/0,04 + hold 288) nhận điểm holdout thật đầu tiên, sau khi xung đột `--daily-profit-gate`/`--portfolio-minimum-hold-decisions` đã được gỡ — và nó **thua ngay trước cả chi phí**

Không lặp lại status-check 15 round liên tiếp (r411-r426) về ba hướng bị
chặn ngoài phạm vi (quyết định sản phẩm Target 2, chờ lịch forward-time, môi
trường Task 6.4) — prompt vòng này yêu cầu rõ không lấp đầy vòng bằng việc
đó. Thay vào đó tìm đúng một câu hỏi Portfolio-layer còn thật sự mở:
Round419 (2026-09-02) đã xác nhận `--daily-profit-gate` và
`--portfolio-minimum-hold-decisions` **không còn xung đột** (unified path,
`origin/main` `7d579cf`, vẫn đúng ở `ca23b05` hiện tại) — đây chính là
"bước gỡ chặn cụ thể: sửa code" mà Round365 đã nêu tên cho "góc có lãi"
(band 0,02/0,04 + hold 288, `exness XAU` +1,17395 full-window `one_target`,
Round366 transfer sang `binance BTC` +0,37527) nhưng **chưa ai thật sự chạy
qua gate**. Round này chạy nó lần đầu.

Hai container Docker (`--cpus=2 --memory=4g --memory-swap=6g`), một SSH
tunnel read-only, cùng route/cửa sổ `binance BTC perpetual_future 5m --days
500` để so trực tiếp với transfer test Round366: **corner** (hold=288, band
0,02/0,04) và **control cùng cửa sổ** (hold=36, band 0,01/0,02 — đúng giá trị
production `trading_modes.rs:113`/`deployment_rules.rs:58-59`). Cả hai xác
nhận `candle_count=143998`, `holdout_candle_count=28799` (holdout
2026-05-26→2026-09-03, 101 ngày quan sát) — cùng cửa sổ, không suy đoán.

**Kết quả — corner thua holdout thật**: `gross_pnl_before_costs` **−1,86562**
(âm ngay cả trước phí, cùng kiểu thất bại r336-337 đã ghi cho band deployed
trên chính route này), net −0,74235, 3,64 lệnh/tuần — **trượt luôn cả
`minimum_trades_per_week`** (deployed ở cùng cửa sổ vẫn đạt 13,79/tuần). Gate
FAILED 7/12 check. Điểm dương full-window Round366 (+0,37527) **không sống
sót** qua 101 ngày holdout thật — đúng rủi ro overfitting mà Round365 tự nêu
("~16-cell search trên một cửa sổ"). Corner vẫn giảm net loss 71,8% so với
deployed (đúng mẫu hình "lãi bằng cách giao dịch ít hơn" Round366 đã tổng kết
cho toàn bộ 6 cấu hình có lãi của arc) nhưng gross lại **tệ hơn** deployed
26,5% (−1,86562 so với −1,47495) — "wider is better per trade" không tổng
quát hoá sang `binance BTC` (r367 đã ghi).

**REJECTED** cho `binance BTC`: điều kiện promotion 1 (holdout defensible)
giờ đo được thật, và bằng chứng là âm. Chưa test `exness XAU` (nơi corner
xuất phát, nhưng không gate-eligible ở bất kỳ cửa sổ nào — r335-336) hay
`bybit XAUT` qua unified path — để dành cho vòng sau nếu cần bức tranh đầy đủ
ba route; hướng đo được (corner thua trước chi phí) khớp mẫu hình 6/6 đã có
của Round366 nên không kỳ vọng đảo chiều. Không đổi production, không
implement gì. Hai container đã dọn sạch (`docker ps -a` rỗng), tunnel đã đóng
(`ss -tlnp` xác nhận). File:
`round427-REJECTED-round365-366-corner-fails-its-first-real-holdout-score-now-that-the-gate-hold-conflict-is-resolved.md`.

## Round 426 — NO-CHANGE: kiểm tra trạng thái 1 ngày sau Round 425, cả ba hướng vẫn bị chặn không đổi — phía OPS của `portfolio-measurement-integrity` đã được archive (nội dung không đổi), phía OpenSpec vẫn vắng mặt

Zero container, zero SSH nghiên cứu, zero backtest compute — chỉ một probe
health-endpoint local read-only. Iteration research-state đọc lại đầu round:
`226` (`quant-research-state state`, `last_run_at` 2026-09-03T17:44:00Z);
chính prompt của phiên này nói launcher đã ghi cơ học iteration `227` trước
khi bàn giao. Theo đúng tiền lệ round424/425, counter `iteration` của
launcher (bookkeeping cho provider/account) và số thứ tự file `round<N>` là
hai counter độc lập, chưa từng khớp 1:1 — round này không gọi lại
`begin-iteration`, không tăng lại gì, và không coi lệch số là phát hiện mới.
Đây là `round426`, tiếp nối đúng thứ tự từ round425.

`git status --short` đầu phiên: sạch. `git fetch origin main -q && git
rev-parse HEAD origin/main`: cả hai đều `fab1af1` — thay đổi so với điểm
kết thúc của round425 (`511a23f`): một phiên ngoài loop này (`fab1af1`,
"chore(orchestrator): remove stale accounts.yaml.example, document format in
README", 2026-09-04T00:31:03+07) đã đóng đúng mục round424/425 từng để lại
"out of scope" (drift `accounts.yaml.example`) — ghi làm bối cảnh, không
phải phát hiện của round này. `finance-live-action` `HEAD` vẫn `ca23b05` =
`origin/main`, cùng CI run cũ r421-r425, không có commit mới.
`openspec/changes/` rỗng trừ `archive/`, vẫn không có mục
`portfolio-measurement-integrity` dù live hay archived.

`.ops/changes/` giờ **rỗng hoàn toàn** (không transaction active nào).
`find .ops -iname '*portfolio-measurement*'` trả về hai mục:
`.ops/archive/2026-09-01-portfolio-measurement-integrity/` (đã biết) và một
mục **mới** `.ops/archive/2026-09-03-portfolio-measurement-integrity/` — đây
là thay đổi trạng thái kể từ round425: lúc round425 đọc, `handoff.md` của
transaction này vẫn còn ở `.ops/changes/portfolio-measurement-integrity/`;
giữa round425 và round này nó đã được chuyển vào `.ops/archive/` với mốc
ngày `2026-09-03`, bởi cùng phiên ngoài-loop suy ra ở trên (hoặc một phiên
khác) — không phải bởi loop này. So sánh hai bản archive: nội dung
`2026-09-03` giống hệt text "BLOCKED evidence (2026-09-03)" mà r419/
r422-r425 đã trích từ bản `.ops/changes/` trước khi archive — **chỉ đổi vị
trí (active → archived), không đổi nội dung.** Bất nhất mà round424 nêu đầu
tiên vẫn còn: phía OPS giờ có bản ghi archived, phía OpenSpec thì không có
gì (cả live lẫn archived) cho cùng change — vẫn ngoài phạm vi sở hữu của
loop nghiên cứu này, ghi lại chỉ để liền mạch.

Target 2: `docs/adr/` vẫn không tồn tại, không commit liên quan từ
2026-09-01 — vẫn không có metric trong tool (r401, không đổi). Forward-time:
hôm nay 2026-09-04, tức **5 ngày** kể từ baseline 2026-08-30 của r403 (nhiều
hơn round425 một ngày) — còn **~25 ngày** nữa mới tới ngưỡng ~30 ngày. Một
probe read-only trực tiếp kiểm lại blocker Task 6.4: `curl --max-time 3
localhost:8086/health` thất bại và `finance-mw` không resolve trong môi
trường này — xác nhận blocker mà bản archive 2026-09-03 ghi vẫn còn đúng.

Không đổi kết luận chiến lược/đo lường/lifecycle nào. Cả ba hướng bị chặn
(quyết định sản phẩm cho Target 2, thời gian lịch cho forward-time, môi
trường có route Finance MW cho Task 6.4) đều nằm ngoài khả năng một round
backtest bounded có thể giải quyết. File:
`round426-NO-CHANGE-status-check-one-day-after-round425-all-three-threads-still-blocked-ops-side-now-archived.md`.

## Round 425 — DATA-ISSUE: commit của chính Round 424 chưa được push, local `main` vượt trước `origin/main` đúng 1 commit — đã push

Zero container, zero SSH, zero backtest compute — cùng nhóm phát hiện với
round422 và round424, ba round liên tiếp cùng loại evidence-trail hygiene.
Iteration research-state đọc lại đầu round: `225` (`quant-research-state
state`, `last_run_at` 2026-09-03T15:34:49Z). Theo đúng tiền lệ round424 đã
ghi lại, counter iteration của launcher và số thứ tự file round là hai
counter độc lập; round này không gọi lại `begin-iteration` và không coi
lệch số là phát hiện mới, chỉ nhắc lại ghi chú của round424 để liền mạch.

`git status`, `git log --oneline -3`, và `git fetch origin main -q && git
rev-parse HEAD origin/main` đầu phiên cho thấy local `main` ở `511a23f`
(đúng commit của round424: "docs(research): round 424 — DATA-ISSUE, restore
9 committed round files + index.md entries missing from working tree") nhưng
`origin/main` vẫn ở `3b1315b` — "Your branch is ahead of 'origin/main' by 1
commit". Commit của round424 đã tồn tại local nhưng chưa từng được push, khả
năng do gián đoạn provider-quota (mà iteration này đang tiếp quản) rơi đúng
giữa bước commit local và bước push của round424. `git show --stat 511a23f`
xác nhận nội dung chỉ gồm tài liệu (`index.md`, CSV, file round424 `.md`),
không đụng application/runtime code, nên đã push trực tiếp theo đúng chính
sách solo-maintainer direct-to-main. `git push origin main` thành công
(`3b1315b..511a23f main -> main`); xác minh lại `HEAD` và `origin/main` cùng
về `511a23f`, working tree sạch trừ đúng `accounts.yaml.example` không liên
quan đã ghi nhận từ round424.

Rà lại 3 hướng như round422/423/424, cùng ngày 2026-09-03, không đổi:
`finance-live-action` `HEAD` vẫn `ca23b05` = `origin/main`, cùng CI run cũ;
Target 2 vẫn không có metric trong tool (r401, vẫn không có `docs/adr/`);
forward-time vẫn ~4 ngày kể từ baseline 2026-08-30, ~26 ngày nữa mới tới
ngưỡng ~30 ngày — không có thời gian lịch mới trôi qua kể từ round424; bất
nhất lifecycle OpenSpec/OPS của `portfolio-measurement-integrity` (context
only, ngoài phạm vi sở hữu loop này) vẫn y nguyên round424 đã ghi.

Không đổi kết luận chiến lược nào — nội dung commit được push (các phát hiện
của round424) vốn đã đúng, chỉ thay đổi khả năng nhìn thấy trên remote.
Đóng lần thứ ba trong 4 round một lỗ hổng evidence-trail cùng họ (round422:
local-vs-committed; round424: committed-vs-working-tree; round425:
committed-vs-pushed) — mỗi round bắt đúng một dạng lệch khác nhau, gợi ý
bước đóng round nên diff tường minh với `origin/main` chứ không chỉ `git
status --short` với working tree local; ghi làm ứng viên skill-upsert, chưa
hành động thêm ngoài việc push commit đã tìm thấy. File:
`round425-DATA-ISSUE-round424s-own-commit-sat-unpushed-local-ahead-of-origin-main.md`.

## Round 424 — DATA-ISSUE: 9 round đã commit (412-415, 417-418, 420-421, 423) cùng mục lục `index.md` của chúng biến mất khỏi working tree, chưa commit — khôi phục từ HEAD

Zero container, zero SSH, zero backtest compute — cùng nhóm phát hiện với
round422, ba round trước. Iteration research-state đầu round: 226 (launcher
ghi máy móc; không gọi lại `begin-iteration`).

`git status --short` đầu phiên cho thấy `index.md` mất 135 dòng (đúng các
mục `## Round 423` → `## Round 412`, trừ round416/419/422) và 9 file round
biến mất khỏi đĩa dù vẫn còn trong tree của `HEAD` (`git cat-file -e` xác
nhận cả 9). Kiểu xoá có chọn lọc — chỉ đúng các round "status-check thuần,
không đổi gì" biến mất, mọi round có phát hiện thật (411, 416, 419, 422) vẫn
còn — nên đã kiểm tra khả năng đây là một lượt biên tập chủ ý trước khi coi
là mất dữ liệu: mtime của `index.md` chỉ ~5 phút sau commit `3b1315b`
(refactor orchestrator, không đụng `research/quant/*`); CSV không có diff nào
(mọi dòng của 9 round vẫn nguyên); tìm khắp repo (`prune`/`consolidat`/
`redundant`/`dedup`) không thấy lý do nào được ghi lại ở bất kỳ đâu; và cùng
cửa sổ ~5 phút đó có một phiên orchestrator-relocation không liên quan lớn
(`815f5bf`, `58a5466`, `0caa758`, ...), với đúng 1 file khác cũng bị xoá
ngoài `research/quant/` (`tools/orchestrator/accounts.yaml.example`) — thuộc
về phiên đó, không phải quant-research. Kết luận: không có bằng chứng đây là
biên tập chủ ý; theo đúng tiền lệ round422 (bảo toàn evidence trail), khôi
phục từ `HEAD` bằng `git checkout --` theo đúng 10 đường dẫn cụ thể (không
phải `git checkout -- .`). Xác minh lại: cả 9 file round đã có lại trên đĩa,
`index.md` có lại đủ mục `## Round 423`/`## Round 412`, chỉ còn đúng
`accounts.yaml.example` (không liên quan, không đụng tới, ghi chú riêng cho
phiên orchestrator sở hữu nó).

Rà lại 3 hướng như round422/423, cùng ngày 2026-09-03, không đổi:
`finance-live-action` `HEAD` vẫn `ca23b05` = `origin/main`, hai CI run cũ
không đổi; Target 2 vẫn không có metric trong tool (r401, không có
`docs/adr/` trong checkout này); forward-time vẫn ~4 ngày kể từ baseline
2026-08-30, ~26 ngày nữa mới tới ngưỡng ~30 ngày; `finance-workspace` và
`origin/main` giờ cùng ở `3b1315b`, đồng bộ hoàn toàn.

Quan sát ngoài phạm vi (chỉ ghi làm bối cảnh): `openspec/changes/portfolio-measurement-integrity/`
đã bị xoá hẳn bởi `3b1315b` (không nằm trong `openspec/changes/archive/`),
trong khi `.ops/changes/portfolio-measurement-integrity/` (OPS runtime state)
vẫn còn với `handoff.md` **cũ**, vẫn ghi `BLOCKED` bằng đúng văn bản blocker
trước round419 — chưa được cập nhật theo bằng chứng round419 đã tạo ra. Đây
là bất nhất lifecycle OpenSpec/OPS, ngoài phạm vi sở hữu của research loop
này theo đúng ranh giới round416/419 đã lập, không hành động thêm.

Không đổi kết luận chiến lược nào — các file mất chỉ là bằng chứng của các
phát hiện đã có từ trước. Đóng lần thứ hai trong 3 round một lỗ hổng cùng
loại (evidence có trên đĩa/trong git nhưng chưa được xác minh đầu-cuối trước
khi một round khác hoặc một task không liên quan chạm vào working tree) —
gợi ý bước 8 của round structure ("git status --short sạch trước khi kết
thúc round") chỉ bắt được sai lệch do chính loop này gây ra, không bắt được
sai lệch do phiên khác gây ra giữa các round. File:
`round424-DATA-ISSUE-nine-already-committed-round-files-plus-their-index-entries-were-missing-from-the-working-tree-restored-from-head.md`.

## Round 423 — NO-CHANGE: kiểm tra trạng thái ~9h sau Round 422 — cả ba hướng vẫn bị chặn không đổi, repo giờ đã đồng bộ hoàn toàn với `origin/main`

Zero container, zero backtest compute, zero SSH tunnel research (chỉ 1 probe
SSH liveness read-only `echo ssh-ok`, không mở port-forward). Kiểm lại: `git
status --short` ở `finance-workspace` sạch đầu phiên, `HEAD` == `origin/main`
tại `1c9531a` — khác round422's end-state (local lead 17 commit chưa push);
giữa round422 và round này, một phiên khác đã push cả commit `3f40f88`/
`b98746c` của round422 lẫn phase-agent-orchestrator work không liên quan —
ghi nhận làm bối cảnh, không phải phát hiện của round này.
`finance-live-action` `HEAD` vẫn `ca23b05` = `origin/main`, hai CI run cũ
không đổi. `openspec/changes/portfolio-measurement-integrity/tasks.md` 6.4
vẫn chưa tick (lifecycle decision ngoài phạm vi, bằng chứng đã có từ r419).
`.ops/changes/` chỉ có phase-agent-orchestrator work không liên quan. Target
2 vẫn không có metric trong tool (r401, không có ADR mới, không có commit
liên quan kể từ 2026-09-01). Forward-time vẫn ~4 ngày kể từ baseline
2026-08-30 (round422 chạy cùng ngày, sớm hơn ~9 giờ) — ~26 ngày nữa mới tới
ngưỡng ~30 ngày. Rà lại mục 4/6 của tài liệu này: không có hạng mục nào chưa
nằm trong 1 trong 3 hướng đang theo dõi hoặc trong các round đã đóng
(330-401, 165-167) — không có hướng backtest mới nào đủ căn cứ để mở trong
ngân sách round này mà không lặp lại một hướng đã đóng. File:
`round423-NO-CHANGE-status-check-9h-after-round422-all-three-threads-still-blocked-repo-now-fully-synced.md`.

## Round 422 — DATA-ISSUE: 11 round nghiên cứu (411-421) nằm chưa commit, và CSV metric đã trôi sang CRLF

Zero compute, zero container, zero SSH. Kiểm lại trạng thái y hệt r421 trước
(finance-live-action `HEAD` vẫn `ca23b05` = `origin/main`, hai CI run cũ
không đổi, `openspec/changes/portfolio-measurement-integrity/tasks.md` 6.4
vẫn chưa tick, `.ops/changes/` chỉ có phase-agent-orchestrator work không
liên quan, forward-time mới 4 ngày kể từ baseline 2026-08-30 (~26 ngày nữa),
Target 2 vẫn không có metric — tất cả khớp y hệt r421, bản thân sẽ chỉ là
NO-CHANGE thuần.

**Phát hiện thật của round này**: `git status --short` đầu phiên cho thấy
`research/quant/index.md` và CSV metric đã sửa đổi, cộng round411-421's
`.md` **chưa từng track** — 11 round viết ra đĩa nhưng chưa bao giờ commit kể
từ `29bc7f7` (2026-09-01). Riêng CSV đã trôi sang **line-ending hỗn hợp**
(755/759 terminator là CRLF, ~5 dòng cũ vẫn LF) — khả năng cao do một tool
Python `csv.writer` mặc định `\r\n` khi rewrite toàn file ở một round nào đó
giữa 411-421, khiến diff tương lai luôn nhiễu toàn file (750 xoá/947 thêm chỉ
cho ~10 dòng nội dung thật). Đã chuẩn hoá CSV về LF thuần (0 CRLF còn lại,
diff còn lại đúng 10 dòng thêm sạch), commit backlog trong 1 commit phạm vi
hẹp chỉ đụng `research/quant/*` (`3f40f88`, local `main`, **chưa push** —
local đang lead `origin/main` 17 commit, 16 commit trong đó là
phase-agent-orchestrator work không liên quan và không thuộc phạm vi round
này để verify/push thay). Không đụng phần openspec/.ops archive/deletion
không liên quan khác đang nằm dirty trong working tree — ghi nhận nhưng để
nguyên, thuộc task khác. Không đổi kết luận chiến lược nào; chỉ đóng lỗ hổng
tính toàn vẹn evidence trail. File:
`round422-DATA-ISSUE-eleven-rounds-of-research-evidence-sat-uncommitted-and-the-metrics-csv-had-drifted-to-crlf.md`.

## Round 421 — NO-CHANGE: commit mới duy nhất kể từ Round 420 là tooling SSH-tunnel không liên quan — cả hai hướng còn lại vẫn bị chặn không đổi

Zero compute, zero container, zero SSH mở bởi round này. `git fetch origin
main` trên `finance-live-action` — `HEAD` tiến lên `ca23b05`, một commit sau
`7d579cf` của r420: `chore(scripts): add reusable SSH tunnel to production
Finance MW` — chỉ thêm `scripts/tunnel-production-mw.sh` (38 dòng), không
đụng code strategy/Portfolio/gate. `gh run list` cho thấy hai run mới tương
ứng (`Build and Deploy` và `Production Live Action Verification`, đều
success) nhưng không ảnh hưởng kết luận chiến lược nào vì không có code
chiến lược thay đổi. `openspec/changes/portfolio-measurement-integrity/tasks.md`
6.4 vẫn chưa tick, đúng ranh giới lifecycle đã ghi ở r419/r420.
`.ops/changes/` giờ có `phase-agent-multi-account-routing/` — một OPS
transaction phase-agent-orchestrator không liên quan quant-research, không
có OPS transaction quant-research nào đang chạy. Hai hướng còn lại không đổi:
Target 2 vẫn thiếu metric trong tool (r401), forward-time vẫn baseline
2026-08-30 (~27 ngày nữa mới tới ngưỡng ~30 ngày). Không có hướng backtest
mới nào mở ra từ round này. File:
`round421-NO-CHANGE-only-new-commit-is-an-unrelated-ssh-tunnel-tooling-script-both-blocked-threads-unchanged.md`.

## Round 420 — NO-CHANGE: kiểm tra trạng thái ngay sau bằng chứng task 6.4 của Round 419 — cả hai hướng còn lại vẫn bị chặn không đổi

Zero compute, zero container, zero SSH. Round419 vừa chạy compute thật
(hold=72 gate run) ngay trước đó; chạy lại compute lần nữa ngay sau sẽ chỉ
lặp lại đúng bằng chứng cũ, nên round này quay về kiểm tra trạng thái thuần
như r411-r418: `git fetch origin main` trên `finance-live-action` — `HEAD`
vẫn `7d579cf`, khớp không đổi so với r416-r419; `gh run list` cùng hai run
gần nhất đã ghi, không có gì mới; `openspec/changes/portfolio-measurement-integrity/tasks.md`
6.4 vẫn chưa tick (đúng như r419 để lại — quyết định tick/archive là lifecycle
call ngoài phạm vi round nghiên cứu); `.ops/changes/` rỗng, không có OPS
transaction đang chạy. Hai hướng còn lại không đổi: Target 2 vẫn thiếu metric
trong tool (r401), forward-time mới ~3 ngày kể từ baseline 2026-08-30 của
r403 (~27 ngày nữa mới tới ngưỡng ~30 ngày). Không có hướng backtest mới nào
mở ra từ round này. File:
`round420-NO-CHANGE-status-check-after-round419-task-6-4-evidence-both-remaining-threads-still-blocked.md`.

## Round 419 — NO-CHANGE: lần đầu có holdout score thật cho task 6.4 (hold=72, unified path) — vẫn lỗ, hệ số understatement 2,97x chứ không phải ~2x

Một container (`finance-research`, `--cpus=2 --memory=4g --memory-swap=6g`),
một SSH tunnel read-only, cả hai đã dọn sạch. Khác với r411-r418 (chỉ kiểm tra
trạng thái, zero compute), round này thử lại trực tiếp lý do chặn của
`openspec/changes/portfolio-measurement-integrity/tasks.md` task 6.4 ("no
Finance MW/research runtime available in the current local environment") vì
session hiện tại có `docker` và `ssh my` hoạt động — build image từ đúng
`origin/main` `7d579cf`, mở tunnel `18086:localhost:8086`, chạy
`--daily-profit-gate --portfolio-minimum-hold-decisions 72` trên
`binance BTC perpetual_future 5m --days 500` (143.998 candle, khớp cửa sổ
r359/r360). Đây là lần đầu tiên `--daily-profit-gate` chạy với hold value qua
unified path (`portfolio_construct_evaluate_execute_target`) kể từ khi task
1.2 gỡ conflict giữa hai cờ.

**Kết quả**: gate **FAILED** (7/12 check: positive_day_ratio, median_daily_pnl,
negative_day_streak, sortino_ratio, sharpe_ratio, gross_pnl_positive,
cost_to_gross_pnl_ratio). `portfolio_faithful` (đường Portfolio thật, hold=72):
173 lệnh, `realized_pnl` **−1,450971**. `legacy_selected_rule` (control bỏ qua
hold guard): 515 lệnh, `realized_pnl` **−4,307464**. `gross_pnl_before_costs`
**−0,248754** (âm ngay cả trước phí) — tín hiệu gốc lỗ độc lập với hold guard.
`trades_per_week` 12,11 (đạt Target 3).

**Xác nhận hướng** của r371 ("gate hiểu sai theo hướng bi quan ~2x") nhưng
**tinh chỉnh độ lớn**: r371 so gián tiếp hai đường khác code path; lần này
cùng một run cho cả hai số, tỷ lệ thật là **4,307/1,451 = 2,97x**, gần 3x hơn
là 2x. **Không đổi kết luận chiến lược nào** — gross âm trước phí nên hold
guard chỉ giảm lỗ, không tạo lời; không đạt điều kiện promote. Task 6.4's
checkbox và quyết định archive change **không** thuộc phạm vi round nghiên
cứu này (theo đúng ranh giới r416 đã ghi) — chỉ ghi lại bằng chứng để người
sở hữu lifecycle OpenSpec/OPS quyết định. Hai hướng còn lại của r418 (Target 2
metric, forward-time ~30 ngày) không đổi. File:
`round419-NO-CHANGE-first-real-holdout-score-for-task-6-4-confirms-loss-with-2-97x-not-2x-understatement.md`.

## Round 418 — NO-CHANGE: ~3h10 kể từ Round 417 — cả hai hướng còn lại vẫn bị chặn không đổi

Zero container/SSH. Kiểm lại vì khoảng cách 3h10 đủ lớn để có thể có fix-up
push, CI run mới, hoặc thay đổi task OpenSpec. `git fetch origin main` trên
`finance-live-action` — `HEAD` vẫn bằng `origin/main` = `7d579cf`, đúng commit
r416/r417 đã ghi. `gh run list --limit 5` cho thấy đúng hai run gần nhất đã
ghi, không có gì mới hơn. `openspec/changes/portfolio-measurement-integrity/tasks.md`
vẫn giữ nguyên: 6.1-6.3 đã tick, 6.4 vẫn chưa, cùng đúng nguyên văn lý do bị
chặn (truy cập network/môi trường), change chưa archive. Hướng Target 2 (r401,
không có metric trong tool) và hướng forward-time (~3 ngày kể từ mốc r403
2026-08-30, so ngưỡng ~30 ngày, còn ~27 ngày nữa) đều không có thông tin mới —
đọc lại sẽ chỉ lặp lại đúng kết luận cũ trên cùng một mẫu chưa đổi. File:
`round418-NO-CHANGE-3h10m-since-round417-both-remaining-threads-still-blocked.md`.

## Round 417 — NO-CHANGE: 71 phút kể từ Round 416 — cả hai hướng còn lại vẫn bị chặn không đổi

Zero container/SSH. Kiểm lại thay vì mặc định giữ nguyên: hướng release-decision
vừa đổi ở r416 nên được re-check chứ không chỉ mang sang. `git fetch origin
main` trên `finance-live-action` — `HEAD` vẫn bằng `origin/main` = `7d579cf`,
đúng commit r416 đã ghi. `gh run list --limit 5` cho thấy đúng hai run gần nhất
r416 đã ghi, không có gì mới hơn. `openspec/changes/portfolio-measurement-integrity/tasks.md`
vẫn giữ nguyên: 6.1-6.3 đã tick, 6.4 vẫn chưa, cùng đúng nguyên văn lý do bị
chặn (truy cập network/môi trường), change chưa archive. Hướng Target 2 (r401,
không có metric trong tool) và hướng forward-time (~3 ngày kể từ mốc r403
2026-08-30, so ngưỡng ~30 ngày) đều không có thông tin mới — đọc lại sẽ chỉ
lặp lại đúng kết luận cũ trên cùng một mẫu chưa đổi. File:
`round417-NO-CHANGE-71-minutes-since-round416-both-remaining-threads-still-blocked.md`.

## Round 416 — NO-CHANGE: hướng "quyết định release" đã di chuyển — finance-live-action đã push và deploy; 2 hướng còn lại vẫn bị chặn

Zero container/SSH. Kiểm lại cả ba hướng r411-r415: **hướng 1 (quyết định
release) đã đổi.** `git fetch origin main` trên `finance-live-action` rồi so
`origin/main..HEAD` và `HEAD..origin/main` — **cả hai đều rỗng**, `HEAD` =
`origin/main` = `7d579cf`. Bốn commit trước đây local-only (`59e2489`,
`c07951a`, `f158e04`, `ae6a1fd` — `portfolio-measurement-integrity` task
1.1-6.3) giờ đã ở `origin/main`, cộng thêm 1 commit lint-fix `7d579cf`
(2026-09-02, đồng tác giả Claude Sonnet 5, cơ học/không đổi hành vi theo
chính message của nó). `gh run list` xác nhận `Build and Deploy` thành công
(12m8s) rồi `Production Live Action Verification` thành công (45s) cho lần
push này. `openspec/changes/portfolio-measurement-integrity/` vẫn còn
(chưa archive), task 6.4 vẫn chưa tick — vẫn bị chặn bởi truy cập
network/môi trường tới production data route, **không liên quan** tới việc
commit đã merge hay chưa nên push này không tự động mở khoá 6.4. **Không**
khẳng định push này đổi bất kỳ kết luận chiến thuật nào đã ghi (r396-r410
vẫn đứng — đây là hạ tầng đo lường/replay, không phải backtest mới).
**Không** khẳng định PnL/hành vi production thay đổi (không chạy kiểm tra
dữ liệu production vòng này, ngoài phạm vi vòng bounded này). Hai hướng còn
lại (định nghĩa Target 2, forward time ~3 ngày kể từ mốc r403 so ngưỡng
~30 ngày) vẫn bị chặn không đổi. Quyết định về task 6.4 và việc archive
change thuộc về người sở hữu vòng đời OpenSpec/OPS đó, không phải vòng
research-only này. File:
`round416-NO-CHANGE-release-decision-thread-resolved-finance-live-action-pushed-and-deployed-two-threads-still-blocked.md`.

## Round 415 — NO-CHANGE: 18 phút kể từ Round 414 — cả ba hướng bị chặn không đổi

Zero container/SSH. Kiểm lại cả ba mục r411-r414: `portfolio-measurement-integrity`
vẫn chỉ ở `.ops/archive/...`, vẫn BLOCKED, `.ops/changes/` vẫn rỗng; 4 commit
`finance-live-action` vẫn local-only (xác nhận lại bằng `git fetch`); forward
time vẫn ~3 ngày kể từ mốc r403 (2026-08-30), còn xa ngưỡng ~30 ngày. Không có
quan sát mới nào phát sinh vòng này. Bước tiếp theo không đổi: hướng nào trong
ba hướng bị chặn di chuyển trước (quyết định release, định nghĩa Target 2,
hoặc thêm thời gian cho live trade log). File:
`round415-NO-CHANGE-18-minutes-since-round414-all-three-blocked-threads-unchanged.md`.

## Round 414 — NO-CHANGE: 27 phút kể từ Round 413 — cả ba hướng bị chặn không đổi

Zero container/SSH. Kiểm lại cả ba mục r411/r412/r413: `portfolio-measurement-integrity`
vẫn chỉ ở `.ops/archive/...`, vẫn BLOCKED, `.ops/changes/` vẫn rỗng; 4 commit
`finance-live-action` vẫn local-only (xác nhận lại bằng `git fetch`); forward
time vẫn ~3 ngày kể từ mốc r403 (2026-08-30), còn xa ngưỡng ~30 ngày. Không có
quan sát mới nào phát sinh vòng này — câu hỏi về iteration counter mà r412 nêu
và r413 làm rõ một phần không được kiểm lại, vì thêm một điểm dữ liệu ở
khoảng cách 27 phút sẽ không thêm thông tin nào ngoài những gì r413 đã ghi.
Bước tiếp theo không đổi: hướng nào trong ba hướng bị chặn di chuyển trước
(quyết định release, định nghĩa Target 2, hoặc thêm thời gian cho live trade
log). File:
`round414-NO-CHANGE-27-minutes-since-round413-all-three-blocked-threads-unchanged.md`.

## Round 413 — NO-CHANGE: vẫn chưa đầy một ngày kể từ Round 412 — cả ba hướng bị chặn không đổi, iteration counter đã tăng lên 207

Zero container/SSH. Kiểm lại cả ba mục r411/r412: `portfolio-measurement-integrity`
vẫn chỉ ở `.ops/archive/...`, vẫn BLOCKED; 4 commit `finance-live-action` vẫn
local-only (xác nhận lại bằng `git fetch`); forward time vẫn ~3 ngày kể từ mốc
r403 (2026-08-30), còn xa ngưỡng ~30 ngày. Một quan sát mới: iteration counter
mà r412 nêu là "không tăng" giữa hai lần gọi liên tiếp (đều đọc 206) giờ đã
tăng lên **207** ở vòng này — làm yếu bớt (không giải quyết dứt điểm) lo ngại
r412 nêu, không có điều tra thêm vì đây là cơ chế launcher tooling, không phải
câu hỏi nghiên cứu. File:
`round413-NO-CHANGE-still-under-a-day-since-round412-all-three-blocked-threads-unchanged-iteration-counter-now-advanced-to-207.md`.

## Round 412 — NO-CHANGE: kiểm lại ngay sau Round 411 (cùng `iteration` báo là 206) — không có gì đổi trong chưa đầy một ngày

Zero container/SSH. Kiểm lại cả ba mục r411 đã đóng thay vì giả định còn
đúng: `portfolio-measurement-integrity` vẫn chỉ ở `.ops/archive/...`, vẫn
BLOCKED; 4 commit `finance-live-action` vẫn local-only (xác nhận lại bằng
`git fetch`); UTC hiện tại `2026-09-01T18:32:37Z`, chưa đầy 1 ngày sau r411,
còn xa ngưỡng ~30 ngày của forward time. Một quan sát mới thật sự: giá trị
`iteration` trong `quant-research-state.sh state` **không tăng** giữa hai lần
gọi `run-phase-agent-command.sh quant-research` liên tiếp — ghi nhận như một
fact về tooling launcher, không phải bug đã chẩn đoán, không ảnh hưởng kết
luận nghiên cứu nào. File:
`round412-NO-CHANGE-re-verified-immediately-after-round411-nothing-changed-in-under-a-day.md`.

## Round 411 — NO-CHANGE: cả ba hướng còn lại (release decision, định nghĩa Target 2, forward time) vẫn thật sự bị chặn — không có gì mới để chạy vòng này

Không chạy container/SSH nào. Kiểm tra lại cả ba hướng r409/r410 để lại:
`portfolio-measurement-integrity` đã chuyển sang `.ops/archive/2026-09-01-...`
với status **BLOCKED** (đóng vì worker process chết, có user authorization —
không phải released); 4 commit trên `finance-live-action` vẫn chỉ nằm local,
xác nhận lại bằng `git fetch origin main`. Target 2 vẫn `n/a`. Forward time:
mới 3 ngày kể từ mốc r403 (2026-08-30), ngưỡng cần ~30 ngày — chạy lại live
log bây giờ sẽ lặp đúng số liệu r403/r405 trên mẫu lớn hơn không đáng kể,
đúng kiểu "busywork" r405 đã cảnh báo. Ghi nhận workspace đã đổi cấu trúc
(`raw/` → `research/quant/`, thêm `run-phase-agent-command.sh`/
`phase-agent-state.sh`) giữa r410 và vòng này — lịch sử nghiên cứu cũ còn
nguyên vẹn qua migration. File:
`round411-NO-CHANGE-all-three-remaining-threads-are-still-genuinely-blocked-nothing-new-to-run.md`.

## Round 409 — REJECTED: strategy production **thứ bảy** cũng lỗ trên holdout — và mang đúng hình dạng **train mạnh, sau đó sụp** mà chính comment trong codebase gọi là **disqualifying**

`round409-REJECTED-the-seventh-production-strategy-loses-on-holdout-too-and-shows-the-overfitting-shape-the-codebase-itself-calls-disqualifying.md`

`mtf_stochastic_14_3_30_70_sma50_trend_filtered` — tức `mtf_stochastic_4h_1d_sma50` của
production, deploy trên cả hai route BTC và **vắng mặt khỏi bản sao research** (r408) — chạy
**lần đầu tiên ở đúng interval của nó** (`--interval 4h --higher-timeframe-interval 1d`), cửa
sổ ghim, 5.401 nến:

| route | holdout | lệnh | train | validation | **holdout** |
|---|---|---|---|---|---|
| `binance BTC` | 2026-03-04 → 2026-08-31 | 11 | +1,06746 | −0,11951 | **−1,12232** |
| `exness BTC` | 2026-03-04 → 2026-08-31 | 11 | +1,09441 | −0,11826 | **−1,15979** |

**Đáp án đã đăng ký: không cái nào dương. Cả BẢY cấu hình production nay đều lỗ trên holdout.**

**Hình dạng:** train **dương**, validation **âm**, holdout **âm hơn** — trên cả hai route, gần
như giống hệt. Đó đúng là mẫu hình mà **chính documentation trong `strategies.rs`** nêu ra và
bác bỏ: *"...strong-train-weak-later là mặt ngược của, và cũng disqualifying ngang, mẫu hình
weak-train-strong-later mà chương trình này đã nhiều lần gắn cờ và bác bỏ."* **Comment đó được
viết về một candidate ĐÃ BỊ ĐÓNG vì có hình dạng này; cùng hình dạng nay xuất hiện trên một
strategy ĐANG ĐƯỢC DEPLOY.**

**Và nó gần như không giao dịch:** **11 lệnh holdout trên 180 ngày = 0,43/tuần.** Dù nó đóng góp
gì cho ensemble sáu-strategy của BTC, **đó không phải tần suất**.

**Bức tranh production đầy đủ** — bảy cấu hình, tất cả đã đo trên holdout: −21,08 · −6,56 ·
−2,13/−0,05 · −1,32/−0,92 · −1,56/−1,50 · −0,97/−0,54 · **−1,16/−1,12**. **Mọi cái đều lỗ. Con
số tốt nhất ở bất kỳ đâu là −0,05.**

**Giới hạn:** **không** khẳng định hình dạng overfitting đã được **xác lập** — ba split trên
**mười một lệnh holdout** là **một hình dạng, không phải một phép kiểm định**; comment trong
codebase mô tả cùng mẫu hình với profit factor trên mẫu **lớn hơn**, còn tôi có **một chuỗi dấu
trên mẫu mỏng, hai lần, trên hai thị trường gần trùng lặp**. **Không** khẳng định nên **loại bỏ**
strategy này — việc nó đóng góp cho ensemble **qua đa dạng hoá** thay vì PnL độc lập **không
phải thứ một điểm số per-strategy trả lời được**, và **replay Portfolio không tiêu thụ nó** (nó
dùng bản sao research, r408). **Không** khẳng định bảy con số so sánh được với nhau — chúng đến
từ run ở **interval khác nhau** với số lệnh **từ 11 đến 3.262**.

**Bước tiếp theo: KHÔNG có cái nào không bị chặn.** Câu hỏi backtest chạy được cuối cùng đã được
trả lời, **và nó trả lời giống sáu cái kia**. Phần còn lại là **quyết định release, một định
nghĩa cho Target 2, và thời gian phía trước**.

## Round 408 — DATA-ISSUE: bản sao research đã **trôi** khỏi cấu hình live. Production chạy một strategy **thứ bảy** không có ở đâu trong đó — **xác nhận bằng payload production**

`round408-DATA-ISSUE-the-research-mirror-has-drifted-from-the-live-configuration-production-runs-a-seventh-strategy-nobody-has-scored.md`

**Zero container.** r407 đóng lại với caveat rằng nó **chưa kiểm binary đang deploy có khớp
source hay không**. Kiểm điều đó cho ra hai sự thật, rồi một sự thật thứ ba quan trọng hơn.

**Định danh triển khai:** cả sáu container live-action chạy image
`finance-live-action_sha-7a15b76`. `origin/main` là `14afa8e`, **đi trước một commit**, và
commit đó là *"ci: remove runner bootstrap"* — **chỉ hạ tầng**, nên production đi sau một commit
là **đúng, không phải cũ**. Cả `production_candidates` lẫn `configured_extra_strategies` đều
**giống hệt từng byte** giữa `7a15b76` và HEAD của tôi → **không có artifact deploy-lag nào**.

**Sự trôi:** `production_candidates` **chỉ được gọi từ research CLI** (`main.rs:617`, `:678`)
— **không code live nào gọi nó**. Binary live là `finance-api`, và tập strategy của nó đến từ
`deployment_rules::configured_alpha_strategies`.

| nhóm route | live (`finance-api`) | bản sao research | |
|---|---|---|---|
| `exness XAU` | 3 | 3 | khớp |
| `binance BTC`, `exness BTC` | **6** | **5** | **khác** |

Strategy chỉ-có-ở-live là **`mtf_stochastic_4h_1d_sma50`** — k14, d3, 30/70, trend 50, base
**4h** / higher **1d**. Nó xuất hiện **0 lần** trong bản sao research. **Xác nhận bằng dữ liệu
production, không chỉ code**: `contributing_strategies` trong payload live liệt kê **sáu** tên
trên cả hai route BTC, gồm cả nó.

**Điều này thu hẹp phạm vi:** số Alpha input của r375 **sai với BTC** (thực tế **6/6/3/2/2/2**,
không phải 5/5/3/2/2/2) — giả thuyết đó **dù sao cũng đã bị bác bỏ**, nhưng **trên con số sai
nó chưa bao giờ test đúng thứ nó tưởng**. "Độ phủ đầy đủ, sáu trên sáu" của r406/r407 **mô tả
bản sao**; **production chạy BẢY cấu hình riêng biệt và cái thứ bảy chưa từng được chấm**.
r394 dùng `exness XAU` — nơi hai định nghĩa **khớp** — nên **không bị ảnh hưởng**.

**Cái thứ bảy chấm được nhưng chưa từng được chấm:** tham số lõi của nó khớp entry
`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, thứ đã cho **+0,19411** trên gold ở bảng
r406 — **nhưng ở SAI interval**. Mọi run MTF của arc đều dùng `5m`/`4h`; **production chạy cái
này ở 4h/1d**. **Tên và tham số lõi khớp trong khi strategy thì không.** **r407 đã dự đoán đúng
kiểu thất bại này một vòng trước đó**, trong chính caveat của nó — rồi **không kiểm xem có
strategy triển khai nào dùng interval khác không**.

**Giới hạn:** **không** khẳng định sự trôi này đổi bất kỳ kết luận **hiệu năng** nào — cái thứ
bảy **chưa được đo ở interval thật** và có thể là bất cứ gì; **không gì trong r394–r407 bị thu
hồi về mặt hiệu năng, cái bị thu hẹp là PHẠM VI**. **Không** khẳng định bản sao **sai** thay vì
**cố ý rút gọn** — có thể có lý do một sweep 5m bỏ qua strategy 4h/1d; tôi **không tìm thấy lý
do trong comment và cũng không giả định theo chiều nào**. **Không** so sánh mọi thứ khác giữa
hai định nghĩa — chỉ **tập strategy**; thứ tự, trọng số và tham số triển khai khác **chưa so**.

**Bước tiếp theo:** chấm `mtf_stochastic_4h_1d_sma50` **ở đúng interval của nó**
(`--interval 4h --higher-timeframe-interval 1d`) trên `binance BTC` và `exness BTC`. Đó là
**strategy production duy nhất chưa từng được đo**, **chạy được ngay hôm nay**, và là **câu hỏi
backtest duy nhất còn lại không bị chặn** bởi quyết định release, định nghĩa Target 2, hay thời
gian phía trước.

## Round 407 — NO-CHANGE: độ phủ đã kiểm **vét cạn, bằng tham số** — **sáu trên sáu** — đóng khoảng trống tôi tự nêu ở r406. Kèm một caveat chính xác

`round407-NO-CHANGE-coverage-verified-exhaustively-by-parameter-six-of-six-with-one-precise-caveat.md`

**Zero container**, đọc code thuần. r406 sửa hai vòng của chính tôi rồi **tự thừa nhận giới
hạn của nó**: *"chưa liệt kê xem có route nào mang candidate tôi chưa đi tìm — đúng kiểu thất
bại của chính vòng này."* **Nêu một khoảng trống rồi để đó chính là cách r394 và r395 đi sai.**

**Liệt kê đầy đủ:** `production_candidates` có **hai entry vô điều kiện** (`candle_momentum`
0,001; `rsi_mean_reversion` 14/30/70) và **ba nhánh loại trừ lẫn nhau** — `binance` perp
BTC/USDT, `exness` cfd|forex XAU/USD, `exness` cfd|forex BTC/USD.
`btc_trend_filtered_candidates` cho **ba** cấu hình; hai nhánh BTC truyền **id khác nhau nhưng
tham số giống hệt**. `bybit BTC`, `bybit XAUT`, `binance XAU` **không khớp nhánh nào** và chỉ
nhận hai entry vô điều kiện. → **Đúng sáu cấu hình riêng biệt toàn fleet, không bỏ sót nhánh nào.**

**Khớp bằng tham số constructor, không bằng tên — sáu trên sáu:**
`CandleMomentumStrategy::new(0.001)`; `RsiMeanReversionStrategy::new(14, 30.0, 70.0)`;
`StochasticStrategy::new(9,3,35.0,65.0)` + `5`; cùng core + `10`;
`MacdTrendStrategy::new(5,13,5)` + `10`; `CandleMomentumStrategy::new(0.001)` + `10`.

**Caveat chỉ lộ ra khi đọc constructor:** các entry MTF của sweep lấy `base_interval` và
`higher_interval` **từ đối số CLI**, không phải từ entry. Chúng khớp `5m`/`4h` của production
**chỉ khi run truyền `--interval 5m --higher-timeframe-interval 4h`** — các run r395/r396 **có
truyền**, nên kết quả đó **đứng vững**. Một run với higher-timeframe khác sẽ cho ra entry
**cùng tên, cùng tham số lõi, nhưng không tương ứng với bất kỳ thứ gì production chạy**: **tên
trông đúng còn kết quả nói về một strategy khác.** **Cùng kiểu thất bại, thấp hơn một tầng.**

**Giới hạn:** **không** khẳng định **binary đang deploy** khớp với source này — tôi đọc
repository ở commit hiện tại; production có chạy revision đó không là **câu hỏi triển khai tôi
chưa kiểm**, và r402 đã cho thấy bẫy build-cũ ngay trong dữ liệu của tôi. **Không** khẳng định
entry sweep và strategy production hành xử **giống nhau lúc chạy** — cùng tham số constructor
vào cùng kiểu là mạnh, nhưng tôi **so code, không so output**. **Không có gì mới** về hiệu năng:
bảng r406 đứng nguyên, **cả sáu đều lỗ**.

**Bước tiếp theo: KHÔNG.** Độ phủ đã đóng, và ràng buộc thường trực không đổi — phần còn lại
**bị chặn bởi quyết định release, bởi một định nghĩa cho Target 2, hoặc bởi thời gian phía trước**.

## Round 406 — DATA-ISSUE: **lỗ hổng độ phủ bằng KHÔNG**. Tôi đã lặp lại, ở r395, đúng sai lầm mà chính tôi đã ghi vào skill ở r394

`round406-DATA-ISSUE-the-coverage-gap-is-zero-i-repeated-a-mistake-i-had-already-written-into-the-skill.md`

**Zero container.** `mtf_stochastic_9_3_35_65_sma5_trend_filtered` **có trong sweep**
(`strategies.rs:4230-4238`), dựng bằng `StochasticStrategy::new(9, 3, 35.0, 65.0)` với trend
period `5` — **trùng khớp** cấu hình gold của production. **Comment ngay trên nó ghi "further
on the already-deployed SMA5 config"** — nó được thêm vào **chính xác để phủ cấu hình này**.

**Lỗ hổng độ phủ bằng KHÔNG. Không có gì để implement.** Thay đổi r394 đề xuất và "một biến
thể thiếu" của r395 **đều bị thu hồi**.

**Tệ hơn cả kết luận sai:** sau r394 tôi đã ghi vào skill *"Khớp strategy production với entry
sweep bằng THAM SỐ, không bằng id."* **Ở r395 tôi lại khớp bằng tên**, không thấy
`mtf_stochastic_5m_4h_sma5`, và kết luận có lỗ hổng. **Tôi ghi bài học rồi lặp lại sai lầm ngay
vòng kế tiếp.**

**Cả sáu candidate production, đo trên holdout 2026-03-04 → 2026-08-31:**

| cấu hình production | `exness XAU` | `binance BTC` |
|---|---|---|
| `candle_momentum` (10bps) | −21,08420 / 3262 | — |
| `rsi_mean_reversion` (14/30/70) | −6,56068 / 819 | — |
| **`mtf_stochastic` sma5** *(gold prod)* | **−0,05076 / 189** | −2,12836 / 300 |
| `mtf_stochastic` sma10 *(BTC prod)* | −1,32247 / 140 | **−0,92104 / 192** |
| `mtf_macd` 5/13/5 sma10 | −1,56472 / 140 | −1,50073 / 192 |
| `mtf_candle_momentum` sma10 | −0,96677 / 122 | −0,53536 / 180 |

**Mọi ô đo được đều ÂM.** Độ phủ production bởi sweep nghiên cứu **đã đầy đủ**, và **không gì
production đang chạy có lãi trên holdout này**.

**Lựa chọn production đầu tiên arc này thấy là ĐÚNG:** production dùng **trend-5 cho gold** và
**trend-10 cho BTC**. Trên holdout này, **lựa chọn theo route của production là cái tốt hơn
trong hai — trên CẢ HAI route** (gấp 26× trên gold, 2,3× trên BTC). Trend period cũng là **đòn
bẩy lớn**: các biến thể chỉ khác trend period trải **1,27–1,51** về PnL holdout.

Dưới đồng xu, đúng cả hai route là **p = 0,25 — không có ý nghĩa thống kê**, và là **một
holdout**. Nhưng đó là **quyết định cấu hình đầu tiên trong arc này được kiểm chứng là đúng
thay vì thất bại**.

**Giới hạn:** **không** khẳng định cấu hình production là tốt — **candidate của nó đều lỗ**;
lựa chọn trend chỉ là **cái tốt hơn trong hai phương án đều lỗ**. **Không** khẳng định kết quả
trend khái quát hoá — một holdout, hai route, hai giá trị của một tham số. **Không** khẳng định
sweep phủ production trên cả sáu route — tôi **chưa liệt kê** xem có route nào mang candidate
mà tôi **chưa đi tìm** hay không, **đúng kiểu thất bại của chính vòng này**.

**Bước tiếp theo: KHÔNG có từ luồng này** — độ phủ đã đầy đủ và câu trả lời đồng nhất. Ràng
buộc thường trực giữ nguyên: mọi việc khả thi đều **bị chặn bởi quyết định release, bởi một
định nghĩa cho Target 2, hoặc bởi thời gian phía trước**.

## Round 405 — NO-CHANGE: cấu trúc ba scope là **phổ quát trên cả sáu route**, và **KHÔNG route nào** — chứ không phải bốn — có nhịp live cao hơn backtest

`round405-NO-CHANGE-the-three-scope-structure-is-universal-and-zero-routes-not-four-show-a-live-rate-above-the-backtest.md`

**Zero container.** r404 xác lập defect gộp-ba-scope trên **hai** route; claim bị thu hồi của
r403 phủ **cả sáu**, nên phải kiểm ở mọi nơi.

| route | thô | scope | **riêng biệt** | live /tuần (95% CI) | backtest | |
|---|---|---|---|---|---|---|
| `exness XAU` | 9 | 3 | **3** | 1,1 – 15,7 | 6,232 | chồng lấn |
| `binance XAU` | 3 | 3 | **1** | 0,0 – 10,0 | 4,797 | chồng lấn |
| `bybit XAUT` | 3 | 3 | **1** | 0,0 – 10,0 | 3,454 | chồng lấn |
| `binance BTC` | 18 | 3 | **6** | 3,9 – 23,4 | 7,661 | chồng lấn |
| `bybit BTC` | 12 | 3 | **4** | 1,9 – 18,3 | 8,517 | chồng lấn |
| `exness BTC` | 15 | 3 | **5** | 2,9 – 20,9 | 5,794 | chồng lấn |

**Mọi route đều có đúng ba scope**, và **thô = 3 × riêng biệt** ở mọi route, ba scope **đồng ý**
về số riêng biệt. **Hệ số gộp là đúng 3 ở mọi nơi, không phải xấp xỉ.**

**Không route nào có nhịp live cao hơn nhịp holdout của backtest. r403 báo bốn. Đáp án đúng
trên cả sáu là KHÔNG CÓ.**

**Mẫu live thực chất là gì:** **hai mươi lệnh riêng biệt trên toàn fleet trong 3,91 ngày**,
không phải sáu mươi. **Hai route chỉ có một lệnh.** Vậy lập trường trung thực **không phải**
"chúng khớp nhau" — mà là **log live hiện chưa hỗ trợ kết luận nào theo bất kỳ chiều nào**: mọi
khoảng đều chồng lấn **vì mọi khoảng đều rộng**, và **hai khoảng bắt đầu từ 0**.

**Giới hạn:** **không** khẳng định nhịp live và backtest khớp nhau — **khoảng rộng chồng lấn là
sự VẮNG MẶT bằng chứng, không phải bằng chứng về sự khớp** — và vòng này làm điều đó **yếu hơn**
r404 gợi ý, vì **bốn trên sáu route có dưới năm lệnh riêng biệt**. **Không** khẳng định ba scope
luôn dùng chung một luồng quyết định — kiểm **từng bộ** trên hai route (r404); bốn route còn lại
chỉ cho thấy **số đếm khớp**, nhất quán nhưng **không phải bằng chứng**. **Không** kết luận gì
về PnL live.

**Bước tiếp theo — nay định lượng chính xác:** log live cho **~5 lệnh riêng biệt mỗi route mỗi
3,9 ngày ở mức tốt nhất, và 1 ở mức tệ nhất**; một tháng cho khoảng **8–46** lệnh đóng riêng
biệt mỗi route. **Cho tới lúc đó không còn gì để đọc từ nó, và luồng này không nên được mở lại
mỗi vòng chỉ để có việc mà chạy.**

## Round 404 — DATA-ISSUE: nhịp live của r403 bị **thổi lên đúng 3×** do gộp **ba cấu hình sizing paper** của **một** luồng quyết định

`round404-DATA-ISSUE-round-403s-live-rate-was-inflated-exactly-3x-by-pooling-three-paper-sizing-scopes-of-one-decision-stream.md`

**Zero container**; đọc production read-only phạm vi hẹp.

**Điều r403 bỏ sót:** nó đếm số lần đóng trong `trades:<route>` và kết luận production nhanh
hơn 2–4×. **Nó không đọc payload.** Payload mang `scope_id`, và **có ba trên mỗi route**:
`paper-fixed-pct-scope`, `paper-compounding-10pct-scope`, `paper-risk-2pct-scope`.
**Production chạy ba cấu hình sizing paper song song**, và log **gộp cả ba dưới một key**.

**Chúng dùng chung MỘT luồng quyết định:** mọi bộ `(entry_at, exit_at, side, close_reason)`
**giống hệt nhau** qua ba scope — **3/3** trên `exness XAU`, **6/6** trên `binance BTC`. **Mỗi
lệnh là cùng một lệnh**, mở và đóng cùng thời điểm, cùng chiều, cùng lý do. Chúng **chỉ khác
kích thước vị thế**: 0,001105 / 0,213332 / 1,516232 — **chênh 1.372×**, và **không khác gì về
quyết định**.

Vậy số lệnh **riêng biệt** là **3 và 6**, không phải 9 và 18.

| route | scope | đóng | live /tuần (95% CI) | backtest | |
|---|---|---|---|---|---|
| `exness XAU` | mỗi scope | 3 | 1,1 – 15,7 | 6,232 | **chồng lấn** |
| `exness XAU` | *gộp (r403)* | *9* | *7,4 – 30,6* | *6,232* | *live cao hơn* |
| `binance BTC` | mỗi scope | 6 | 3,9 – 23,4 | 7,661 | **chồng lấn** |
| `binance BTC` | *gộp (r403)* | *18* | *19,1 – 50,9* | *7,661* | *live cao hơn* |

**Headline của r403 bị thu hồi.** Khoảng cách 2–4× **chính xác là hệ số gộp 3×**. Lời giải
thích thay thế của r403 (xu hướng tần suất tăng) **không được xác nhận và cũng không cần** —
**không còn chênh lệch nào để giải thích**.

**Giới hạn:** **không** khẳng định production và backtest **đồng thuận** về tần suất — "chồng
lấn" với 3 và 6 sự kiện trong 3,9 ngày là **yếu**: khoảng trải **một bậc độ lớn** và sẽ chồng
lấn gần như mọi nhịp hợp lý. **Điều này gỡ bằng chứng bất đồng, KHÔNG cung cấp bằng chứng đồng
thuận.** **Không** khẳng định ba scope tồn tại trên cả sáu route — **kiểm trên hai**. **Không**
khẳng định `paper-fixed-pct` đúng là cấu hình backtest — tên và kích thước nhỏ **nhất quán**,
nhưng tôi **không xác minh tham số** vì việc đó đồng nghĩa đọc cấu hình worker. **Không** kết
luận gì về PnL live — kích thước vị thế chênh **ba bậc độ lớn** giữa các scope.

**Bài học đáng giữ:** r403 đã kiểm log có bị trim không, neo cửa sổ cẩn thận, tính **khoảng
Poisson chính xác**, và test độ nhạy theo cửa sổ — **mà vẫn ra đáp án sai**, vì nó **không bao
giờ nhìn xem các bản ghi LÀ GÌ**. **Sự chặt chẽ về thống kê không bù được việc không đọc dữ liệu.**

**Bước tiếp theo:** phép so live cần **lệnh riêng biệt**, và chỉ có 3–6 mỗi route sau khi khử
trùng lặp. "Chờ 30+ ngày" của r403 vẫn đứng, **kèm đính chính**: số dùng được là **một phần ba**
kích thước key thô — một tháng cho khoảng **20–45** lệnh đóng riêng biệt mỗi route, **không phải
60–135**.

## Round 403 — NEEDS-MORE-RESEARCH: production giao dịch **nhanh hơn 2–4×** so với nhịp holdout của backtest trên **cả ba route BTC** — phép so live-vs-backtest đầu tiên arc đủ dữ liệu để làm

`round403-NEEDS-MORE-RESEARCH-production-trades-2-to-4x-faster-than-the-backtest-holdout-rate-on-all-three-btc-routes.md`

**Zero container**; đọc production read-only phạm vi hẹp + một lần kiểm code.

**Vì sao nay làm được:** r306 và r357 đã thử và thất bại — log giao dịch live chỉ có **1–6 lần
đóng lệnh**. Nay nó có **60 lần đóng trên sáu route**. Log **an toàn để đếm**:
`crates/finance-redis/src/trade_log.rs` **chỉ có `ZADD`** — **không trim, không expire, không
delete**.

Cửa sổ quan sát neo vào **lần đóng sớm nhất trên cả sáu route** (neo độc lập với route):
**3,91 ngày**. Khoảng Poisson 95% cho nhịp live:

| route | đóng | live /tuần (95% CI) | backtest holdout /tuần | |
|---|---|---|---|---|
| `exness XAU` | 9 | 7,4 – 30,6 | 6,232 | live cao hơn |
| `binance XAU` | 3 | 1,1 – 15,7 | 4,797 | chồng lấn |
| `bybit XAUT` | 3 | 1,1 – 15,7 | 3,454 | chồng lấn |
| **`binance BTC`** | 18 | **19,1 – 50,9** | 7,661 | **live cao hơn** |
| **`bybit BTC`** | 12 | **11,1 – 37,5** | 8,517 | **live cao hơn** |
| **`exness BTC`** | 15 | **15,0 – 44,3** | 5,794 | **live cao hơn** |

Neo này **điều kiện hoá trên sự kiện** — đúng bias r357/r358 đã bắt — nên cửa sổ là **chặn
dưới** và mọi nhịp live là **chặn trên**. Chạy lại với cửa sổ **dài hơn một ngày**: **ba route
vẫn giữ** — `binance BTC` (15,2–40,6), `bybit BTC` (8,8–29,9), `exness BTC` (12,0–35,3).
**Cả ba route BTC, dưới cả hai giả định.** Ba route vàng **chồng lấn** khi nới cửa sổ.

**Cách giải thích thay thế — mà chính phát hiện của arc này ủng hộ, và tôi nêu nó là cách giải
thích DẪN ĐẦU chứ không phải một caveat:** **tần suất tăng về phía hiện tại.** r392 đo
1,963 → 6,232 lệnh/tuần qua bốn holdout rời (3,17×); r397 thấy cùng hướng trên `binance BTC`.

**Cửa sổ của production là 3,9 ngày gần nhất; holdout của backtest là 180 ngày gần nhất, kết
thúc cùng ngày.** Nếu nhịp đang tăng, cửa sổ 4 ngày nằm **ở đỉnh** xu hướng còn trung bình 180
ngày nằm **dưới** — **điều đó có thể giải thích TOÀN BỘ chênh lệch mà backtest không sai ở đâu
cả.** Kết luận "backtest đánh giá thấp production" **đòi hỏi so sánh cùng loại**, và hai cửa sổ
này **chênh nhau 46 lần về độ dài** trên một đại lượng arc **đã chứng minh là đang trend**.

**Giới hạn:** **không** khẳng định backtest đánh giá thấp production. **Không** khẳng định
production và backtest chạy cùng cấu hình hiệu dụng — **chưa xác minh**, và **khác cấu hình sẽ
tạo ra đúng dấu hiệu này**. **Không** khẳng định gì về hai route 3-lệnh — ba sự kiện **không
phân biệt được gì**, khoảng của chúng trải **một bậc độ lớn**. **Không** khẳng định 3,91 ngày
là cửa sổ thật — nó là **chặn dưới neo vào một sự kiện**; tôi **không đọc uptime worker để
tránh mở rộng một phép đọc hẹp**. **Không** rút ra hàm ý nào cho Target 3 — nhịp live trên mốc
trong **bốn ngày** không phải một lần đạt Target 3.

**Bước tiếp theo:** phép thử sạch là **cùng loại**, nhưng một run backtest cửa sổ ngắn sẽ có
warm-up và độ dài holdout **không đủ điều kiện** — nên phiên bản trung thực là **hướng ngược
lại: CHỜ, rồi đếm lại log live khi nó trải 30+ ngày**. Đó là **luồng thời-gian-phía-trước** mà
arc đã nhiều lần nêu tên, và **nay nó đang thực sự thu thập dữ liệu**.

## Round 402 — NO-CHANGE: hai dòng fleet-table cũ **vô hại**. Riêng biệt: `binance XAU` **không bao giờ tạo được holdout đủ điều kiện** ở bất kỳ độ dài cửa sổ nào

`round402-NO-CHANGE-the-stale-fleet-rows-were-harmless-and-binance-xau-can-never-produce-a-qualifying-holdout.md`

**Vì sao cần kiểm:** r401 phát hiện một log `binance XAU` có trước thay đổi đo lường. Audit
xuất xứ bảng fleet của r390 cho thấy **hai trên năm dòng** đến từ commit `59e2489`, đường đo
của nó **bị sửa hai lần sau đó**, và **không dòng nào được ghim cửa sổ**. r381 đã cho thấy các
bản fix **làm dịch số lệnh và PnL**.

| route | build | gross | net | lệnh/tuần | holdout ngày |
|---|---|---|---|---|---|
| `binance XAU` | cũ | −0,39816 | −0,62329 | 4,794 | 52,6 |
| `binance XAU` | **final** | **−0,42093** | −0,64607 | 4,797 | 52,5 |
| `bybit BTC` | cũ | −0,89289 | −2,45576 | 8,517 | 180,0 |
| `bybit BTC` | **final** | **−0,89289** | −2,45576 | 8,517 | 180,0 |

**Đáp án đã đăng ký: không dấu gross nào đổi.** Các dòng cũ **vô hại**; bảng r390 đứng vững
như đã được r397 sửa.

Hai chi tiết đáng giữ: **`bybit BTC` giống hệt từng byte qua hai build** — các bản fix **không
đổi gì** trên route này, trong khi r381 đo chúng làm `binance BTC` dịch một lệnh và 4% PnL →
**hiệu ứng của bản fix phụ thuộc route và có thể bằng 0**. `binance XAU` **dịch 5,7%**, nhất
quán với r382 về việc run không ghim thì trôi.

**Sự thật cấu trúc lộ ra:** `binance XAU` ở `--days 900` nạp **75.672 nến = 262,8 bar-days**,
holdout là 20% đuôi = **52,5 ngày**. Ngưỡng `minimum_holdout_days` là **90**. Để đạt, route cần
**450 bar-days**; nó có **263**. **Không giá trị `--days` nào tạo được holdout đủ điều kiện trên
route này**, vì nó **đã nạp toàn bộ lịch sử venue** (r208). Thiếu hụt: **187 bar-days ≈ 6,2
tháng thời gian phía trước**.

**Vậy trong sáu route production:** `binance XAU` **không thể qualify gate** cho tới khi có thêm
~6 tháng lịch sử; `bybit XAUT` chỉ qualify ở cutoff mới nhất (101,3 ngày), mọi cutoff sớm hơn
**bị loại vì độ dài** (r400); bốn route còn lại qualify ở 180 ngày. **Hai trên sáu route không
thể đánh giá qua nhiều holdout ở độ dài đủ điều kiện — điều đó chặn mọi phát biểu cấp fleet mà
arc này đưa ra được, kể cả khoảng tin cậy gộp.**

**Giới hạn:** **không** khẳng định vấn đề build cũ vô hại ở mọi nơi — **hai dòng được kiểm**,
bảng có năm, và các vòng cũ dùng build đó **rộng rãi mà không kiểm lại**. **Không** khẳng định
tính giống-hệt của `bybit BTC` nghĩa là bản fix là no-op: nó là no-op **trên route và cửa sổ
này**. **Không** khẳng định sáu tháng sẽ làm `binance XAU` đánh giá được — nó sẽ vượt **ngưỡng
độ dài**; bảy check interval-continuity và các ngưỡng hiệu năng là **riêng biệt**. **Không** đổi
ước lượng gộp — route này **chưa bao giờ nằm trong** chuỗi chín holdout.

**Bước tiếp theo:** không còn gì trong bảng fleet cần chạy lại. Ràng buộc cho mọi phát biểu
fleet tiếp theo là **cấu trúc, không phải quy trình** — hai route không cung cấp được holdout
đủ điều kiện, bốn route còn lại đã đo xong. **Đó là kết thúc trung thực của luồng đo fleet.**

## Round 401 — DATA-ISSUE: **Target 2 không có metric nào trong công cụ**. Cái mang tên `decision_rate` đo **tỉ lệ chuyển đổi lệnh**, và nó **vắng mặt hoàn toàn khỏi report holdout**

`round401-DATA-ISSUE-target-2-has-no-metric-in-the-tool-and-the-one-named-decision-rate-measures-trade-conversion-instead.md`

**Zero container.** Mục tiêu thường trực nêu **ba** thứ cần tối ưu đồng thời — lợi nhuận,
**Make Decision rate**, tần suất giao dịch — và tôi đã ghi `target2_makedecision: n/a` trong
**khoảng sáu mươi vòng CSV mà chưa bao giờ xác lập vì sao.** Vòng này xác lập.

**Kiểm chứng chính xác trên mọi run build hiện tại: `decision_rate` = `trades` ÷ `decision_count`.**

| run | nến | decision | lệnh | `decision_rate` | decision/nến |
|---|---|---|---|---|---|
| `exness XAU` @08-31 | 174.254 | 165.689 | 402 | 0,002426 | 0,951 |
| `exness XAU` @03-04 | 173.939 | 165.885 | 279 | 0,001682 | 0,954 |
| `exness XAU` @09-04 | 174.498 | 166.162 | 215 | 0,001294 | 0,952 |
| `binance BTC` @08-31 | 259.201 | 258.914 | 891 | 0,003441 | 0,999 |
| `bybit BTC` @08-31 | 259.201 | 258.914 | 851 | 0,003287 | 0,999 |

Đó là **tỉ lệ chuyển đổi lệnh** — bao nhiêu phần chu kỳ quyết định kết thúc bằng một lệnh —
**không phải sản lượng quyết định**: **~95% nến gold và ~99,9% nến BTC đã sinh ra một bản ghi
decision**, tuyệt đại đa số là Hold. **Vậy đại lượng mà mục tiêu gọi là "Make Decision rate"
KHÔNG phải thứ mà trường tên `decision_rate` báo cáo.**

**Và nó vắng mặt khỏi report holdout:** `decision_rate` chỉ có trên block `one_target`
**non-gate**; block `metrics` của gate **không chứa nó** và nó **không xuất hiện ở đâu khác
trong report gate**. **Vậy proxy gần nhất cho Target 2 hoàn toàn không có đường đo trên
holdout.** Target 1 và 3 đều đo được trên holdout; **Target 2 thì không, kể cả bằng proxy.**

**Điều các con số cho thấy:** BTC chuyển đổi ~**1,4×** tỉ lệ của gold, và tỉ lệ của gold
**giảm một nửa khi lùi về quá khứ** (0,002426 → 0,001682 → 0,001294 qua ba cửa sổ rời) — cùng
xu hướng tần suất r392 đo bằng lệnh/tuần, **biểu diễn dưới dạng tỉ số nên không giải thích được
bằng độ dài cửa sổ**.

**Một lỗi của tôi, bị chính assertion bắt:** lần chạy đầu tôi gắn cờ `binance XAU` báo
`decision_rate: None` dù có 134 lệnh và 75.482 decision — **đó sẽ là một defect thật**. Nó
không phải: log đó từ **vòng 372**, **trước** thay đổi đo lường, và `one_target` của nó chỉ có
bốn trường gốc. **Khoá VẮNG MẶT, không phải null.** Ghi lại thay vì lặng lẽ bỏ dòng đó đi.

**Giới hạn:** **không** khẳng định "Make Decision rate" **nên** nghĩa là gì — r265–r270 đo
`gate_passed` từ log production, một định nghĩa hợp lý, nhưng **chọn định nghĩa không phải việc
của tôi**: chọn một cái rồi báo cáo theo nó là **bịa ra mục tiêu** chứ không phải đo nó.
**Không** khẳng định việc gate thiếu metric này là defect chứ không phải bỏ qua có chủ ý — gate
chấm những gì ngưỡng của nó phủ, và **không có ngưỡng Target 2 nào** trong `thresholds`; thêm
metric **mà không có tiêu chí** sẽ không làm mục tiêu đo được theo nghĩa quan trọng.

**Bước tiếp theo: Target 2 cần một ĐỊNH NGHĨA trước khi cần một metric**, và đó là quyết định
của người đặt ra mục tiêu, **không phải thứ một vòng nghiên cứu nên tự chốt**. Cho tới lúc đó,
bản ghi trung thực là `n/a` **kèm lý do này**, thay vì `n/a` không giải thích như sáu mươi vòng
vừa qua.

## Round 400 — REJECTED: thành công joint-objective duy nhất của arc là **artifact mẫu ngắn**. Các cửa sổ lân cận, **chồng lấn mạnh, đều âm**

`round400-REJECTED-the-arcs-only-joint-objective-success-was-a-short-sample-artifact-and-neighbouring-overlapping-windows-are-both-negative.md`

**Một ràng buộc phải nêu trước khi test:** r399 nêu "chạy ở cutoff cho holdout ≥ 90 ngày" —
**điều đó KHÔNG lấy được** cho holdout kết thúc 2026-03-04: lịch sử route không lùi đủ xa, và
độ dài holdout là 20% của phần nạp được. Nên bài test trở thành: **kết quả dương có sống sót
khi cửa sổ TRƯỢT không?**

| cutoff | holdout | ngày | gross | **net** | lệnh/tuần | ≥90d |
|---|---|---|---|---|---|---|
| 2026-01-15 | 2025-11-20 → 2026-01-15 | 55,7 | −0,18472 | **−0,25888** | 2,513 | không |
| **2026-03-04** | **2025-12-28 → 2026-03-04** | **65,3** | +0,46972 | **+0,06359** | **7,073** | không |
| 2026-04-15 | 2026-01-31 → 2026-04-15 | 73,7 | +0,14300 | **−0,45686** | 9,021 | không |
| 2026-08-31 | 2026-05-21 → 2026-08-31 | 101,3 | +0,01363 | **−0,31114** | 3,454 | **có** |

**Cả hai lân cận đều âm** — và chúng **không phải phép thử ở xa**: cửa sổ 2026-04-15 **chồng
lấn cửa sổ dương khoảng 33 ngày** mà vẫn ra **−0,45686**.

**Đáp án đã đăng ký: +0,06359 là đặc thù cửa sổ.** Đúng hiệu ứng mẫu ngắn mà ngưỡng 90 ngày
sinh ra để bắt — và **r399 đã đúng khi từ chối tính nó**.

**Bất ổn bên dưới:** lệnh/tuần qua bốn cửa sổ là **2,513 · 7,073 · 9,021 · 3,454** — **trên
những cửa sổ chồng lấn nhau đáng kể**. **Verdict Target 3 của route này lật giữa trượt rõ
(2,51) và đạt rõ (9,02) chỉ với một dịch cutoff vài tuần.** Và **chỉ một trong bốn holdout đạt
mức tối thiểu 90 ngày**: trên route này gate thực tế **chỉ chấm được cutoff mới nhất**.

**KHÔNG gộp vào chuỗi:** hai số mới **không** được thêm vào chuỗi chín holdout của r399 — chúng
là **cửa sổ chồng lấn trên một route đã có mặt**, gộp vào sẽ **thổi phồng n bằng dữ liệu tương
quan**, đúng lỗi r398 đã cảnh báo. Ước lượng gộp **giữ nguyên**: n = 9, mean +0,19085,
95% [−0,16974; +0,55144], **chứa 0**.

**Giới hạn:** **không** khẳng định `bybit XAUT` không thể có lãi — bốn cửa sổ ngắn trên một
route nói rằng **kết quả dương đó không sống sót một lần trượt cửa sổ**, **không** xác lập một
thuộc tính âm của route. **Không** khẳng định bất ổn tần suất là đặc thù route này — `exness
XAU` và `binance BTC` cũng dao động 3× qua các holdout; route này là **cực đoan nhất đã đo,
trên các cửa sổ ngắn nhất**.

**Bước tiếp theo:** luồng `bybit XAUT` **đã đóng**. Danh sách trung thực các câu hỏi backtest
arc còn trả lời được nay **rất ngắn**: hai-ba điểm holdout rời nữa trên `exness BTC` và
`bybit BTC`, đưa chuỗi lên n ≈ 12 và thu hẹp khoảng thêm khoảng một phần sáu. **Trên ước lượng
hiện tại điều đó sẽ không đổi câu trả lời**, nên chỉ đáng làm **như xác nhận, không phải như
truy vấn**.

## Round 399 — NEEDS-MORE-RESEARCH: **holdout đầu tiên của cả arc vừa net-dương vừa đạt tần suất Target 3** — và nó **quá ngắn để đủ điều kiện**

`round399-NEEDS-MORE-RESEARCH-the-first-net-positive-at-frequency-holdout-in-the-arc-and-it-is-too-short-to-qualify.md`

**Câu hỏi đăng ký — trả lời: ổn định.**

| | mean | se | khoảng 95% | |
|---|---|---|---|---|
| n = 7 (r398) | +0,08923 | 0,22360 | [−0,34903; +0,52749] | chứa 0 |
| **n = 9** | **+0,19085** | 0,18398 | **[−0,16974; +0,55144]** | **chứa 0** |

Khoảng **hẹp lại 18%**, trung bình **gần gấp đôi**, nhưng **0 vẫn nằm trong**. Gross nay dương
ở **6/9** holdout — khác với ấn tượng "dao động quanh 0" trước đây — **nhưng trung bình vẫn
không tách được khỏi 0** vì độ phân tán lớn, và **6/9 tự nó không bất thường**.

**Hai điểm mới, và cái đáng chú ý:**

| route | holdout | ngày | gross | **net** | lệnh/tuần |
|---|---|---|---|---|---|
| `bybit XAUT` | 2025-12-28 → 2026-03-04 | **65,3** | +0,46972 | **+0,06359** | **7,073** |
| `exness BTC` | 2025-09-05 → 2026-03-04 | 180,0 | +0,62328 | −0,04486 | 4,162 |

**`bybit XAUT` net dương (+0,06359) ở 7,073 lệnh/tuần** — vượt mốc Target 3 **và** có lãi.
**Holdout đầu tiên trong 194 iteration làm được cả hai cùng lúc.**

**Và nó KHÔNG đủ điều kiện.** Holdout chỉ **65,3 ngày lịch** so với ngưỡng `minimum_holdout_days`
là **90**. Gate **từ chối vì quá ngắn**, và nó ngắn vì lịch sử của `bybit XAUT` hết. **Vậy
thành công joint-objective đầu tiên của arc nằm trên một mẫu mà chính gate tuyên bố là không
đủ.** Đây **không phải tiểu tiết để lách** — 65 ngày **chính là chỗ một kết quả dương dễ xuất
hiện do ngẫu nhiên nhất**, và đó **chính xác là lý do ngưỡng tồn tại**.

**Sửa ước lượng của r398:** r398 nói bốn route chưa test sẽ cho "sáu-bảy điểm nữa trong hai
vòng". **Chân trời dữ liệu khiến điều đó lạc quan** — lịch sử mọi route dừng quanh 2024-03-14
nên cutoff sớm hơn nạp được ít dần; holdout `bybit XAUT` vòng này ra **65 ngày thay vì 180**.
Số điểm dùng được **gần hai-ba hơn là sáu-bảy**.

**Giới hạn:** **không** khẳng định `bybit XAUT` có cấu hình có lãi — **một holdout, 65 ngày,
dưới mức tối thiểu**, và r397 đã xác lập số đo một-holdout **không mô tả được route**. **Không**
khẳng định gross edge dương — 6/9 với trung bình +0,19 và khoảng [−0,17; +0,55] **không phải kết
quả dương**, mà là **ước lượng rộng hơn mức hữu ích tình cờ nằm trên 0**. **Không** tin khoảng
này ở giá trị bề mặt — chín holdout đến từ **bốn route với lịch sử fit chồng lấn**, nên sai số
chuẩn **giả định nhiều độc lập hơn thực tế và do đó lạc quan**. **Không** coi +0,06359 là lớn —
nó là 0,06 so với các dao động ±1,8 khác trong chuỗi.

**Bước tiếp theo:** chạy lại `bybit XAUT` ở cutoff cho holdout **≥ 90 ngày** (H1 của nó là 180
ngày, nên một cutoff ở giữa sẽ cho độ dài đủ điều kiện). **Nếu net vẫn dương ở độ dài đủ điều
kiện VÀ ở tần suất, đó là kết quả đầu tiên của arc đáng đưa ra thảo luận promote**; nếu không,
số đo 65 ngày **chính là hiệu ứng mẫu ngắn mà ngưỡng sinh ra để bắt**.

## Round 398 — NEEDS-MORE-RESEARCH: gross gộp qua **bảy holdout rời** **không phân biệt được với 0**. Đánh đổi tần suất có mặt về hướng nhưng ở **p = 0,13** — và tôi đã tự chọn ngưỡng biết trước null là 13%

`round398-NEEDS-MORE-RESEARCH-pooled-gross-across-seven-disjoint-holdouts-is-not-distinguishable-from-zero-and-my-threshold-had-a-13-percent-null.md`

**Zero container.** Bảy số gross holdout rời (bốn `exness XAU`, ba `binance BTC`):
`+0,66471, −0,72458, +0,29154, −0,11094, −0,58685, +0,82128, +0,26947`.

**Trung bình +0,08923; sd 0,59160; se 0,22360; khoảng 95% xấp xỉ [−0,34903; +0,52749] —
CHỨA SỐ 0.** Mọi phát biểu trước đây về điều này đều **định tính** ("hình dạng của nhiễu").
**Đây là con số**: gross edge gộp qua bảy kỳ thực sự ngoài mẫu **không phân biệt được với
không có gì**. Khoảng này **cũng đủ rộng để chứa một edge ±0,5**, nên **cũng không xác lập là
KHÔNG có**.

**Bài test đánh đổi — và ngưỡng lẽ ra tôi không nên chấp nhận.** Tuyên bố lặp nhiều nhất của
arc (r363, r367) được lập **hoàn toàn trên sweep tham số toàn-cửa-sổ, in-sample**, nơi tần suất
bị dịch **có chủ đích**. Bảy holdout này để tần suất **biến thiên tự nhiên** ở cấu hình **cố
định** — phép thử khác và mạnh hơn.

| holdout | lệnh/tuần | net |
|---|---|---|
| `exness XAU` H4 | 1,963 | −0,37140 |
| `exness XAU` H3 | 2,176 | **+0,00095** |
| `exness XAU` H2 | 3,020 | −1,20812 |
| `binance BTC` H2 | 4,200 | **+0,00025** |
| `binance BTC` H3 | 4,900 | −0,15914 |
| `exness XAU` H1 | 6,232 | −0,37734 |
| `binance BTC` H1 | 7,661 | −1,77712 |

**Spearman ρ = −0,5000**, rơi **đúng** vào ngưỡng đã đăng ký. **p hoán vị chính xác (5.040
hoán vị) = 0,1333.**

**Tôi đã tính null đó TRƯỚC khi chạy và vẫn đăng ký ngưỡng ấy**, vì ở n = 7 các lựa chọn khác
còn tệ hơn (ρ ≤ −0,714 cho p = 0,044 nhưng mất phần lớn power). **Chọn một tiêu chí có tỉ lệ
dương-giả 13% rồi báo "tiêu chí đã đạt" sẽ là gây hiểu nhầm, nên tôi không báo cáo như vậy.**
**Đánh đổi có mặt về hướng và chưa được xác lập** — một hoán vị trong bảy cho ra kết quả này
hoặc mạnh hơn.

**Điều bảng cho thấy mà không cần test nào:** hai kết quả **ít âm nhất** (+0,00095 và +0,00025)
nằm ở 2,176 và 4,200 lệnh/tuần; hai kết quả **tệ nhất** (−1,20812; −1,77712) ở 3,020 và 7,661.
**Kết quả tệ nhất là holdout bận nhất; hai kết quả tốt nhất không phải hai cái yên nhất.**

**Giới hạn:** **không** khẳng định không có gross edge — khoảng chứa **cả 0 lẫn ±0,5**, và bảy
quan sát **không tách được hai điều đó**. **Không** coi bảy holdout là độc lập — hai route, và
trong mỗi route lịch sử fit tới mỗi cutoff **chồng lấn**, nên **cả khoảng tin cậy lẫn phép hoán
vị đều giả định nhiều độc lập hơn dữ liệu thực có và do đó đều lạc quan**. **Không** khẳng định
đánh đổi in-sample của r363/r367 là sai — vòng này **không xác nhận được nó ngoài mẫu**, không
phải bác bỏ nó.

**Bước tiếp theo:** **n = 7 là ràng buộc chặn mọi câu hỏi còn lại**, và chỉ lớn lên bằng cách
chạy holdout rời trên bốn route chưa test — khoảng hai vòng cho sáu-bảy điểm nữa, thu hẹp khoảng
tin cậy khoảng một phần ba và đưa phép hoán vị về dải p dùng được. **Đó là công việc backtest
duy nhất còn lại có thể thay đổi điều gì nói được.**

## Round 397 — DATA-ISSUE: tôi chỉ đem **kết quả dương** đi test holdout rời. Các kết quả **âm cũng bất ổn y hệt** — `binance BTC` dương gross ở **hai trên ba** holdout

`round397-DATA-ISSUE-i-tested-only-the-positive-result-on-disjoint-holdouts-the-negative-ones-are-just-as-unstable.md`

**Bất đối xứng trong chính phương pháp của tôi:** r391/r392 đem kết quả **dương** của
`exness XAU` qua bốn holdout và thấy nó đảo dấu; r390 ghi **ba route gross âm** và một dương —
**mỗi route một holdout** — rồi tôi dựng một mô tả fleet trên đó **mà không test các số âm theo
cùng cách**. **Chỉ test kết quả nổi bật là bất đối xứng chọn lọc, bất kể nó chỉ theo hướng nào.**

`binance BTC`, ba holdout rời, cửa sổ ghim:

| run | holdout | **gross** | net | cost/gross | lệnh/tuần |
|---|---|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | **−0,58685** | −1,77712 | 2,0282 | 7,661 |
| H2 | 2025-09-05 → 2026-03-04 | **+0,82128** | **+0,00025** | 0,9997 | 4,200 |
| H3 | 2025-03-08 → 2025-09-04 | **+0,26947** | −0,15914 | 1,5906 | 4,900 |

**Hai trên ba dương.** r390 chỉ đo H1 và ghi route này là **gross âm**.

| route | gross qua các holdout | dương |
|---|---|---|
| `exness XAU` | +0,66471, −0,72458, +0,29154, −0,11094 | 2/4 |
| `binance BTC` | −0,58685, +0,82128, +0,26947 | **2/3** |

**Cả hai route đều đảo dấu. Không route nào được mô tả đúng bởi số đo một-holdout.**

**Cái bị vô hiệu hoá:** bảng fleet của r390 **với tư cách mô tả các ROUTE** — nó mô tả **một
cửa sổ mỗi route**. **Cái KHÔNG bị vô hiệu hoá:** kết luận cốt lõi của r391/r392 rằng **số dương
không tái lập** — nó **sống sót**, vì số của `binance BTC` **cũng không tái lập**; nếu có thì
điều này **củng cố** nó: **bất ổn dấu là mẫu hình chung**, không phải thuộc tính của một route.

**Cũng không đổi: không gì có lãi.** Net tốt nhất của `binance BTC` qua ba holdout là
**+0,00025** — hoà vốn, ở 4,200 lệnh/tuần. Đây là net **không-âm thứ hai** của cả arc (sau
+0,00095 của `exness XAU`), và **cả hai đều ở tần suất joint objective bác bỏ**.

**Route thứ hai cho câu hỏi tần suất:** 4,900 → 4,200 → **7,661** — holdout mới nhất **rõ ràng
bận nhất** như trên gold (r392), **nhưng không đơn điệu** (H3 cũ hơn lại cao hơn H2). Xu hướng
"tăng về hiện tại" có **ủng hộ về hướng** trên route thứ hai và **không phải** chuỗi đơn điệu
sạch như gold.

**Giới hạn:** **không** khẳng định `binance BTC` có edge — 2/3 dương với trung bình gần 0 là
**cùng hình dạng** với `exness XAU`: **bất ổn, không phải edge**. **Không** khẳng định bốn route
kia cũng đảo — **chưa test**, và đó nay là **khoảng trống đã biết**, đúng khoảng trống tôi vừa
phê phán. **Kết luận fleet trước của tôi không sai về HƯỚNG — nó sai về ĐỘ TIN CẬY.**

**Bước tiếp theo:** mọi phát biểu tương lai về dấu gross của một route cần **ít nhất ba holdout
rời** trước khi được viết ra. Bốn route chưa test mất hai vòng; **có đáng làm hay không phụ thuộc
vào việc câu trả lời sẽ thay đổi điều gì** — và trên bằng chứng hiện tại **nó sẽ không thay đổi
gì**: mọi route đo hơn một lần đều **dao động quanh 0**.

## Round 396 — REJECTED: thư viện MTF **cũng không tái lập gì**, và base rate cao hơn của nó là **artifact của đúng một cửa sổ**

`round396-REJECTED-the-mtf-library-replicates-nothing-either-and-its-higher-base-rate-is-one-windows-artifact.md`

**Đăng ký trước với cả null VÀ power được mô phỏng trước** (bài học r393/r394): ngưỡng **≥ 2**
strategy dương trên cả ba holdout rời; **P(null) = 0,0014**; **power 0,573** (5 strategy ở
p=0,70) và **0,682** (10 ở p=0,60).

| run | holdout | chấm | dương |
|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 98 | 8 |
| H2 | 2025-09-04 → 2026-03-04 | 98 | **31** |
| H3 | 2025-03-07 → 2025-09-04 | 98 | 9 |

**Dương trên cả ba: 0.** Kỳ vọng null 0,232; P(≥1) = 0,212 → **zero là bình thường**. **Cùng
kết luận r393 cho thư viện thường. Không thư viện nào tái lập.**

**Ấn tượng về base rate tan ra khi tách:** toàn bộ ô cho MTF **16,3%** (48/294) so với **7,6%**
của thư viện thường. **Bỏ H2 ra thì còn 17/196 = 8,7% — không phân biệt được với 7,6%.**
**Toàn bộ phần "cải thiện" là đúng một cửa sổ**: riêng H2 là 31/98 = **31,6%**, gần **gấp bốn**
hai holdout kia. Báo cáo 16,3% mà không tách như vậy **sẽ là đúng lỗi diễn giải của r390**.

**Một quan sát tôi KHÔNG gọi là finding:** H2 là cửa sổ mà **thư viện Alpha làm tốt nhất**
(31,6% dương) và cũng là cửa sổ mà **gross của chính Portfolio tệ nhất** (−0,72458, r391 — âm
nhất trong bốn holdout). **Trong kỳ mà nhiều strategy hoạt động nhất, phần chọn lọc của
Portfolio cho kết quả tệ nhất.** Một cửa sổ, hai đại lượng đo trên cùng dữ liệu — **ghi lại để
kiểm lại, không phải vì đã xác lập được tương quan nghịch giữa chọn-lọc và sẵn-có.**

**Giới hạn:** **không** khẳng định thư viện MTF không có edge — **power 0,57–0,68**, tốt hơn
r393 nhưng **vẫn không cao**; hiệu ứng yếu **rất có thể bị bỏ sót**. **Không** khẳng định 8,7%
và 7,6% là cùng một tỉ lệ — quần thể khác, run khác, **không có phép kiểm định nào** trên chênh
lệch. **Không** điều tra nguyên nhân H2 là ngoại lệ.

**Bước tiếp theo:** cả hai thư viện nay đã được test **cùng một cách** và **không cái nào tái
lập**. Câu hỏi đo được còn lại trên route này là **một cấu hình production chưa chấm**
(`mtf_stochastic` trend-5, r395) — thay đổi một dòng, **hoãn tới khi OPS transaction hiện tại
được release**. **Ngoài ra, arc này đã hết câu hỏi backtest mà một vòng nữa có thể trả lời —
thứ còn lại là thời gian phía trước.**

## Round 395 — REJECTED: candidate MTF của production **cũng lỗ trên holdout**. Và thay đổi code tôi đề xuất vòng trước **phần lớn là không cần thiết**

`round395-REJECTED-productions-mtf-candidates-lose-on-holdout-too-and-the-code-change-i-proposed-is-largely-unnecessary.md`

**Điều tôi đã sai vòng trước:** r394 kết luận `mtf_stochastic_5m_4h_sma5` "không có analogue
trong thư viện nghiên cứu" và đề xuất thêm cấu hình MTF của production vào `candidates()`, gọi
đó là "thay đổi đầu tiên arc xác định được mà giá trị không phụ thuộc việc tìm edge".

**`multi_timeframe_candidates()` đã tồn tại**, gọi được qua `--higher-timeframe-interval`, và
chứa **105 strategy** gồm **khớp chính xác** cho các extras MTF của production:
`mtf_stochastic_9_3_35_65_sma10_trend_filtered`, `mtf_macd_5_13_5_sma10_trend_filtered`,
`mtf_candle_momentum_10bps_sma10_trend_filtered`. **Chỉ** `mtf_stochastic_5m_4h_sma5`
(trend 5) là **không có khớp chính xác**.

**Lỗ hổng nằm ở CÁCH arc chạy công cụ, không phải ở công cụ:** **không vòng nào trong 190
iteration truyền `--higher-timeframe-interval`**, nên mọi `strategy_scores` tôi từng đọc đều
**loại trừ toàn bộ thư viện MTF**. **Đề xuất của tôi thu lại còn MỘT biến thể tham số thiếu**,
không phải một loại điểm mù.

**Phép đo, khi cờ đã được dùng** (holdout 2026-03-04 → 2026-08-31, ghim, cấu hình deploy):

| candidate production | `exness XAU` | `binance BTC` |
|---|---|---|
| `mtf_stochastic` (9,3,35/65,t10) | −1,32247 / 140 | −0,92104 / 192 |
| `mtf_candle_momentum` (10bps,t10) | −0,96677 / 122 | −0,53536 / 180 |

**Cả hai âm trên cả hai route.** Cộng với r394 (`candle_momentum` và `rsi_mean_reversion` 0/6
dương trên ba holdout rời): **bốn trên năm candidate riêng biệt của production nay đã đo trên
holdout, và cả bốn đều lỗ.** Cái thứ năm (stochastic trend-5 của gold) **vẫn chưa đo**.

**Thư viện MTF có cùng base rate với thư viện thường:** **8/98 (8,2%)** và **9/105 (8,6%)**
dương, so với **7,6%** (r393) và **8,4%** toàn fleet (r373). **Thêm 105 strategy đa-khung thời
gian làm base rate dịch chưa tới một điểm phần trăm.** Bộ bọc MTF — thứ production tìm đến khi
muốn edge đặc thù route — **cho ra một thư viện thất bại ngoài mẫu ở đúng tỉ lệ như thư viện
không có nó.**

**Giới hạn:** **không** khẳng định candidate MTF của production không có edge — **mỗi cái một
holdout**; cặp generic của r394 được test trên **ba** holdout rời, hai cái này **thì không**.
**Không** khẳng định hai base rate so sánh được có ý nghĩa — sweep MTF là **quần thể khác và
lớn hơn**, chạy với cờ **làm đổi dữ liệu được nạp**; 8,2% so 7,6% **không phải phép so có kiểm
soát** và tôi **không** coi chênh lệch đó là thông tin theo bất kỳ chiều nào. **Không** khẳng
định stochastic trend-5 của gold sẽ hành xử như biến thể trend-10 — nó là **cấu hình deploy duy
nhất hoàn toàn không có độ phủ nghiên cứu**, và trend period **đúng là tham số** r375 thấy
ensemble khác nhau theo route.

**Bước tiếp theo:** việc còn lại trung thực là **một strategy** — chấm `mtf_stochastic
9/3/35-65/trend-5` trên `exness XAU`, một **dòng thêm** vào `multi_timeframe_candidates()`,
**không** phải loại thay đổi r394 đề xuất. Nên làm **khi OPS transaction hiện tại được release,
không phải trước** — chồng một implementation thứ hai lên một cái chưa release chính là điều
quy tắc branch-discipline cảnh báo.

## Round 394 — REJECTED: candidate gold **của chính production** lỗ trên **mọi** holdout rời nhau. Và lớp Portfolio **gỡ đi 98,6%** khoản lỗ đó — **nó không phải chỗ có vấn đề**

`round394-REJECTED-productions-own-gold-candidates-lose-on-every-disjoint-holdout-and-the-portfolio-removes-98-6-percent-of-that-loss.md`

**Một lỗi tra cứu của tôi, bắt được và sửa giữa vòng:** lần đầu tôi báo **không** candidate
nào của production có trong sweep 75 — và suýt kết luận hai tập **rời nhau**. **Sai**: tôi tra
bằng `id` của production trong khi **sweep dùng nhãn có tham số**. Kiểm trong `strategies.rs`:
`candle_momentum` (0,001) == `candle_momentum_10bps` **khớp chính xác**; `rsi_mean_reversion`
(14/30/70) == `rsi_mean_reversion_14_30_70` **khớp chính xác**; `mtf_stochastic_5m_4h_sma5`
**vắng mặt — sweep không có entry `mtf_` nào**. **Tôi đã không báo cáo kết quả rỗng "0 trên 0"
mà lỗi tra cứu tạo ra.**

**Đăng ký lại cho sáu ô thực sự có (2 candidate × 3 holdout), TRƯỚC khi đọc kết quả** — chỉ số
lượng ô thay đổi: **≥ 3/6** thắng base rate; null (p = 0,076) = **0,0074**; **power** với hiệu
ứng đồng-xu = **0,656**.

| candidate production | H1 | H2 | H3 |
|---|---|---|---|
| `candle_momentum` (0,001) | −21,08420 / 3262 | −23,23038 / 3184 | −11,27030 / 1561 |
| `rsi_mean_reversion` (14/30/70) | −6,56068 / 819 | −5,35702 / 784 | −6,13148 / 809 |

**0 trên 6 dương.** Kỳ vọng theo base rate: 0,46 → **nhất quán với nó**. Candidate của
production **không tốt hơn** một thành viên ngẫu nhiên của thư viện, và **cũng không đo được
là tệ hơn**.

**Con số định hình lại cả arc:** trên holdout H1, hai candidate Alpha của production **lỗ
−27,64488 trên 4.081 lệnh**. Portfolio, **được nuôi bởi chúng**, lỗ **−0,377343 trên 160 lệnh**.

| | input Alpha | output Portfolio | thay đổi |
|---|---|---|---|
| tổng lỗ | −27,64488 | −0,37734 | **−98,6%** |
| lệnh | 4.081 | 160 | −96,1% |
| **mỗi lệnh** | −0,006774 | −0,002358 | **−65,2%** |

**Portfolio gỡ 98,6% khoản lỗ được trao, và cải thiện kinh tế học mỗi lệnh 65% — không chỉ nhờ
giao dịch ít đi. Cả hai trục.**

**Vậy kết luận mà 60 vòng dò knob Portfolio vòng quanh là NGƯỢC LẠI với giả định của chính cuộc
tìm kiếm đó: lớp Portfolio KHÔNG PHẢI chỗ có vấn đề.** Nó đang làm việc thật, đo được. Nó bắt
đầu từ **input lỗ trên mọi kỳ ngoài mẫu đã test**, và **điều tốt nhất một bộ chọn có thể làm với
input như vậy là lỗ ít hơn.**

**Giới hạn:** **không** khẳng định candidate production **tệ hơn** thư viện — 0/6 so với kỳ vọng
0,46 là **nhất quán**, không phải thấp hơn. **Không** khẳng định lớp Portfolio "hoạt động tốt":
nó **giảm lỗ**, **không tạo lãi**, và r391/r392 cho thấy gross edge của chính nó **không tái
lập** — **"không phải chỗ có vấn đề" không phải "lời giải"**. **Không** khẳng định 98,6% khái
quát hoá — một route, một holdout, **hai trên ba input**, và **cái thứ ba không test được cũng
đang nuôi Portfolio** nên phép so **thiếu một phần thứ nó thực sự tiêu thụ**.

**Bước tiếp theo:** `mtf_stochastic_5m_4h_sma5` **đang chạy trên gold và không có bất kỳ độ phủ
nghiên cứu nào trong cả arc**. Thêm ba cấu hình MTF của production vào `candidates()` là **thay
đổi nhỏ, phạm vi rõ**, cho phép sweep chấm **đúng thứ đang chạy** — và là **thay đổi đầu tiên
arc này xác định được mà giá trị của nó KHÔNG phụ thuộc vào việc tìm ra edge.**

## Round 393 — REJECTED: **không strategy Alpha nào** dương trên cả ba holdout rời nhau. Và **92,4%** ô strategy-holdout đều lỗ — thư viện **không phải** không gian tìm kiếm có người thắng hiếm, nó **lỗ đồng loạt**

`round393-REJECTED-zero-alpha-strategies-replicate-across-three-disjoint-holdouts-and-92-percent-of-the-library-loses-every-time.md`

`exness XAU`, ba cutoff cách nhau đúng một độ dài holdout → holdout của Alpha sweep **rời nhau**:

| run | holdout | nến | dương / 75 |
|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 174.254 | **4** |
| H2 | 2025-09-04 → 2026-03-04 | 173.939 | **9** |
| H3 | 2025-03-07 → 2025-09-04 | 174.498 | **4** |

(75 chứ không 77: năm entry `taker_imbalance` **nay bị loại đúng** trên route này — defect r374,
**đã sửa và đang hoạt động**.)

**Dương trên cả ba: 0.** Kỳ vọng dưới ngẫu nhiên: **0,025** → **zero đúng là điều ngẫu nhiên
dự đoán**.

**Ngưỡng tôi đăng ký lại đặt sai — lần thứ tám** (r327, r330, r340, r354, r373, r378, r387,
r393). Tôi đăng ký *"≥ 3 tái lập"* trong khi **tối đa đạt được là 4** (chỉ bốn strategy dương
trên H1). Đối với null 0,025 thì ngưỡng 3 **nghe có vẻ ngặt**; về **power** thì **gần như không
thể đạt**. **Bài test này không phân biệt được "không có hiệu ứng" với "hiệu ứng yếu" — nó chỉ
loại trừ hiệu ứng mạnh.** Mẫu hình nhất quán: tôi cứ chọn ngưỡng theo **cái nghe có vẻ khắt
khe** thay vì **mô phỏng xem bài test phát hiện được gì**.

**Phát hiện không phụ thuộc vào ngưỡng của tôi:** ô dương là **17 trên 225 = 7,6%** (mỗi
holdout: 5,3%, 12,0%, 5,3%). **Nếu các strategy là đồng xu, khoảng 50% sẽ dương trên bất kỳ
holdout nào. Chúng dương 7,6%.**

**Vậy thư viện Alpha không phải không gian tìm kiếm chứa người thắng hiếm giữa các ứng viên
trung tính — nó là tập 75 strategy LỖ NGOÀI MẪU khoảng 92% THỜI GIAN**, ở chi phí deploy. Nhất
quán với 8,4% toàn fleet của r373, **nay xác nhận trên các kỳ thực sự rời nhau**.

r216/r217 nói friction giết gần như mọi thứ. **Đây là cùng sự thật được đo đúng: những cái sống
sót không bị friction giết từ một nền dương — CHÍNH CÁI NỀN ĐÃ ÂM.**

**Giới hạn:** **không** khẳng định không strategy nào có edge — **bài test quá ít power để nói
vậy**, và tôi nói ra điều đó thay vì **khoác cho một kết quả rỗng cái áo phát hiện**. **Không**
khẳng định 7,6% là base rate đúng. **Không** coi ba holdout là ba quan sát độc lập — chúng **rời
nhau về dữ liệu** nhưng mỗi strategy vẫn là **cùng strategy** và thành phần sweep **cố định**:
đây là **ba lần nhìn vào một thư viện, không phải ba phép thử**.

**Bước tiếp theo:** **ngừng test thư viện này để tìm edge.** Hai việc còn đáng một vòng, **không
cái nào là dò tham số**: (a) xu hướng **tần suất** (r392, tăng 3,17× về hiện tại) có tiếp tục
**về phía trước theo thời gian thực** không; (b) **ensemble ba candidate đang deploy trên gold**
có khác base rate của thư viện 75 không — vì nếu chính candidate của production cũng lỗ 92% ngoài
mẫu, **câu hỏi thôi không còn là chọn strategy nào**.

## Round 392 — REJECTED: gross **đảo dấu liên tục** qua bốn holdout. Riêng biệt: tần suất giao dịch **tăng 3,17× về phía hiện tại** — tái lập một phát hiện cũ bằng phương pháp **thực sự hợp lệ**

`round392-REJECTED-gross-alternates-sign-across-four-holdouts-and-trade-frequency-rises-3-2x-toward-the-present.md`

| holdout | cửa sổ | ngày | **gross** | net | lệnh/tuần |
|---|---|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 179,7 | **+0,66471** | −0,37734 | 6,232 |
| H2 | 2025-09-04 → 2026-03-04 | 180,8 | **−0,72458** | −1,20812 | 3,020 |
| H3 | 2025-03-07 → 2025-09-04 | 180,2 | **+0,29154** | **+0,00095** | 2,176 |
| H4 | 2024-11-05 → 2025-05-06 | 181,9 | **−0,11094** | −0,37140 | 1,963 |

**Hai trên bốn dương → KHÔNG TÁI LẬP.** Gross chạy **+ − + −**. Trung bình **+0,03018** (bốn)
và **+0,07722** (ba cái xếp khít), so với **biên độ 1,38929**. **Một đại lượng tập trung quanh
0 với độ phân tán lớn — hình dạng của nhiễu, không phải của edge.** H1/H2/H3 **xếp khít chính
xác**; H4 **chồng lấn** H3 khoảng hai tháng vì lịch sử `exness XAU` bắt đầu 2024-03-14.

**Hai điều bất ngờ trong bảng:**

**H3 có NET = +0,00095 — net không-âm DUY NHẤT trên bất kỳ holdout nào trong cả arc.** Đó là
**hoà vốn, không phải lãi**, và nó xảy ra ở **2,176 lệnh/tuần — một phần ba mốc Target 3**.
Nhất quán với mọi thứ arc đã tìm được: cấu hình chỉ tiệm cận hoà vốn **ở nơi nó hầu như không
giao dịch**.

**Tần suất tăng đơn điệu về phía hiện tại**: 1,963 → 2,176 → 3,020 → **6,232**, **tăng 3,17×**.
Điều này quan trọng vượt ra ngoài vòng này: r289 và r293 tìm thấy tỉ lệ giao dịch "tăng gấp đôi
sau mười tám tháng" **bằng nested differencing**, thứ mà **r300 đã vô hiệu hoá**. Phát hiện đó
**nay tái lập trên holdout thực sự rời nhau** — phương pháp **không có khiếm khuyết đó**. **Một
kết quả từng bị vô hiệu hoá hoá ra đã đúng, được xác nhận bằng phương pháp hợp lệ**, và độ lớn
**còn lớn hơn** ước lượng ban đầu.

**Điều này khép lại:** **việc tìm edge ở lớp Portfolio đã kết thúc** trên bằng chứng hiện có.
Sáu route đo trên holdout: **ba gross âm, hai không phân biệt được với 0, và cái duy nhất có
số dương thật thì đảo dấu qua bốn holdout.**

**Giới hạn:** **không** khẳng định **không có** edge — bốn holdout trên một route là **bốn quan
sát**, và ba trong số đó chỉ **rời nhau về cấu tạo, không độc lập**: chúng **chia sẻ cùng lịch
sử fit** tới mỗi cutoff. **Không** khẳng định xu hướng tần suất có nguyên nhân. **Không** coi
+0,00095 của H3 có ý nghĩa — nó bằng **0,03%** độ lớn gross của H1 và ở tần suất mà joint
objective **bác bỏ**.

**Bước tiếp theo:** **không nên tiêu thêm vòng nào để tìm edge ở lớp Portfolio.** Hai câu hỏi
đáng một vòng: (a) xu hướng **tần suất** có tiếp tục về phía trước không — **chạy lại sau vài
tuần, không phải backtest**; (b) **Alpha ensemble** có sinh ra gì trên **holdout rời nhau**
không — cùng bài test, một lớp cao hơn, nơi r373–r374 để lại một scan **không sống sót bài test
bảo thủ nào** nhưng **chưa từng chạy trên dữ liệu thực sự chưa thấy**.

## Round 391 — REJECTED: edge gross duy nhất của fleet **không sống sót holdout RỜI NHAU** — bài test đầu tiên thuộc loại này mà arc từng chạy được

`round391-REJECTED-the-fleets-one-real-edge-does-not-survive-a-disjoint-holdout-the-first-such-test-the-arc-has-ever-run.md`

**Bài test mà r352 tuyên bố là bất khả.** r352 xác lập **mọi holdout đều lồng nhau** (holdout
là 20% đuôi của `--days`) — rào cản đó đứng vững **39 vòng**. `--as-of`, thêm vào bởi
transaction đo lường **vì một lý do khác** (tái tạo được, r382), **hoá giải nó**: dịch cutoff
lùi đúng **một độ dài holdout** cho ra holdout **không giao nhau chút nào**.

| | holdout | gross | net | cost/gross | lệnh/tuần |
|---|---|---|---|---|---|
| gốc | 2026-03-04 → 2026-08-31 | **+0,66471** | −0,37734 | 1,5677 | 6,232 |
| **rời nhau** | **2025-09-04 → 2026-03-04** | **−0,72458** | −1,20812 | 0,6673 | 3,020 |

**Không giao nhau** — holdout thứ hai **kết thúc đúng chỗ** holdout thứ nhất bắt đầu.

**Đáp án đã đăng ký: gross = −0,72458. KHÔNG DƯƠNG. Nó ĐẢO DẤU.** Con số +0,66471 là **thuộc
tính của sáu tháng đó, không phải của cấu hình**.

**Tần suất cũng không ổn định**: 6,232/tuần ở holdout này, **3,020** ở holdout liền kề — đúng
kiểu giảm một nửa mà r382 cảnh báo, **trên chính đại lượng Target 3 dùng để chấm**.

**Nói thẳng: sau 186 iteration, với phép đo cuối cùng đã đúng** — replay Portfolio-faithful,
giới hạn holdout, cửa sổ ghim, cấu hình có hold, scorecard joint-objective đầy đủ — **không có
gross edge nào được chứng minh ở bất kỳ đâu trong fleet trên dữ liệu thực sự chưa thấy.**

**Fleet đầy đủ** (gross trên holdout): `exness XAU` +0,66471 (**đảo thành −0,72458**);
`exness BTC` +0,09272; `bybit XAUT` +0,01363; `binance XAU` −0,39816; `binance BTC` −0,58685;
`bybit BTC` −0,89289. **Ba âm, hai không phân biệt được với 0, và con số dương duy nhất không
tái lập.**

**Về transaction đã làm điều này khả thi:** thay đổi đo lường được **minh oan theo cách quan
trọng nhất** — toàn bộ mục đích của nó là làm cho một **phán quyết out-of-sample defensible**
trở nên khả thi, và **phán quyết đầu tiên nó cho phép là ÂM**. Đó là **kết cục đúng của việc
đo lường cho tử tế**, và nó đáng giá hơn 60 vòng dò tham số trước đó.

**Giới hạn:** **không** khẳng định cấu hình **không có** edge — hai holdout trên một route là
**hai quan sát**; điều khẳng định là **kết quả dương duy nhất không tái lập**. **Không** khẳng
định năm route kia cũng sẽ đảo — chưa test trên holdout rời, và ba trong số đó **đã âm sẵn**.
**Không** khẳng định holdout rời nhau nay rẻ và tổng quát: mỗi cái tốn **một run đầy đủ** và
**ăn vào lịch sử** — cửa sổ 900 ngày cho khoảng **bốn** holdout 180 ngày rời nhau, **ít hơn**
trên `binance XAU` (r208). **Không** quy nguyên nhân cho việc đảo dấu.

**Bước tiếp theo:** chạy **hai holdout rời còn lại** trên `exness XAU`. **Nếu gross âm ở ba
trên bốn**, con số dương duy nhất của route là **nhiễu**, và **việc tìm edge ở lớp Portfolio
kết thúc**. Hai vòng công việc, và nó **giải quyết câu hỏi arc đã vòng quanh từ r313**.

## Round 390 — REJECTED: chỉ **một** route có gross edge thật. **Ba route lỗ TRƯỚC mọi chi phí.** Tỉ số chi phí **gộp lẫn hai tình huống hoàn toàn khác nhau**

`round390-REJECTED-only-one-route-has-real-gross-edge-three-lose-before-any-cost-and-the-cost-ratio-conflates-two-different-situations.md`

r389 nêu giả thuyết: *"nếu tỉ số trên 1,0 ở mọi nơi, fleet có edge thật nhưng đồng loạt quá
nhỏ để trả nổi friction."* Năm route, holdout, đường Portfolio-faithful, cửa sổ ghim:

| route | **gross** | cost drag | net | cost/gross | sharpe | lệnh/tuần |
|---|---|---|---|---|---|---|
| **`exness XAU`** | **+0,66471** | 1,04205 | −0,37734 | 1,5677 | −0,810 | 6,232 |
| `bybit XAUT` | **+0,01363** | 0,32477 | −0,31114 | 23,8348 | −1,163 | 3,454 |
| `binance XAU` | **−0,39816** | 0,22512 | −0,62329 | 0,5654 | −4,561 | 4,794 |
| `binance BTC` | **−0,58685** | 1,19027 | −1,77712 | 2,0282 | −2,482 | **7,661** |
| `bybit BTC` | **−0,89289** | 1,56287 | −2,45576 | 1,7503 | −3,234 | **8,517** |

**Tỉ số trên 1,0 ở bốn trên năm — và giả thuyết vẫn SAI**, vì **ba trong số đó không có edge
nào để mà "quá nhỏ"**. Chúng **lỗ trước một điểm cơ bản chi phí nào được áp**.

**Cái bẫy diễn giải tôi đã bước vào:** `cost_to_gross_pnl_ratio` **chỉ có nghĩa khi gross > 0**.
Với mẫu số âm nó vẫn cho ra con số **trông hợp lý** — 0,5654 của `binance XAU` sẽ **ĐẠT** dải
ngưỡng trên một route có gross **−0,398** — còn 23,83 của `bybit XAUT` là **số học trên gross
+0,0136**, thứ **không phân biệt được với 0**, chứ không phải "edge bị nhấn chìm 24×".

Tỉ số > 1,0 **gộp lẫn**: (1) **edge thật bị chi phí nhấn chìm** — `exness XAU`, **và chỉ nó**;
(2) **không có edge nào cả** — ba route còn lại. **Gate không có lỗi**: nó có
`gross_pnl_positive` là **check riêng** — đúng cái chốt mà diễn giải của tôi cần và **đã không
dùng**.

**Bức tranh sắc hơn — tần suất và edge nằm ở hai route ngược nhau:** hai route **ĐẠT Target 3
trên holdout** (`bybit BTC` 8,517; `binance BTC` 7,661) — **cả hai gross ÂM**. Route duy nhất
có gross edge đáng kể, `exness XAU`, chạy **6,232/tuần và TRƯỢT**. **Route giao dịch đủ thì
không có edge; route có edge thì không giao dịch đủ.** Đó là joint objective **hỏng ở cả hai
trục cùng lúc, lần đầu được đo đúng.**

**Giới hạn:** **không** khẳng định `exness BTC` thuộc nhóm nào — route thứ sáu, **chưa đo**.
**Không** khẳng định gross edge ổn định — mỗi route một holdout, và r382 cho thấy thay đổi cửa
sổ nhỏ làm PnL dịch cỡ phần trăm trong khi các con số gross này **nhỏ**. **Không** coi +0,01363
của `bybit XAUT` là edge — nó gần 0 hơn gần `exness XAU` **49 lần**. **Không** điều tra nguyên
nhân ba route gross âm.

**Bước tiếp theo:** đo `exness BTC` cho đủ fleet, **rồi dừng đo**. Nếu năm trên sáu route không
có gross edge trên holdout, câu hỏi **không còn là xoay knob nào của Portfolio** mà là **Alpha
ensemble có sinh ra edge trên route nào khác `exness XAU` không** — và r373/r374 đã cho thấy
scan holdout của chính lớp Alpha **không sống sót bài test bảo thủ nào**.

## Round 389 — NEEDS-MORE-RESEARCH: **scorecard holdout đo đúng đầu tiên sau 184 iteration**. Edge là **thật** — và chi phí bằng **157% của nó**

`round389-NEEDS-MORE-RESEARCH-the-first-correctly-measured-holdout-scorecard-the-edge-is-real-and-costs-are-157-percent-of-it.md`

**Zero container**, đọc từ run đã có. **Đây là phép đo cả arc không thực hiện được.**

`exness XAU` @900, **cấu hình deploy kèm `minimum_hold_decisions` 36**, **chỉ holdout**, cửa
sổ **ghim**, chấm qua replay **Portfolio-faithful**. **Từng mệnh đề trong đó đều bất khả
trước transaction này**: gate **từ chối thẳng** giá trị hold (`conflicts_with`, r356), nó chấm
**luồng không guard**, và **không cửa sổ nào ghim được** (r382). Holdout: 2026-03-04 →
2026-08-31, 34.851 nến, **179,7 ngày lịch, 152 ngày quan sát**.

| metric | giá trị | ngưỡng | |
|---|---|---|---|
| **`gross_pnl_before_costs`** | **+0,664709** | > 0 | **ĐẠT** |
| **`total_cost_drag`** | **1,042052** | — | |
| **`net_realized_pnl`** | **−0,377343** | — | |
| **`cost_to_gross_pnl_ratio`** | **1,567682** | ≤ 0,5 | **TRƯỢT, vượt 3,1×** |
| `sharpe_ratio` | −0,810499 | ≥ 1,0 | trượt |
| `sortino_ratio` | −1,150073 | ≥ 1,0 | trượt |
| `positive_day_ratio` | 0,401316 | ≥ 0,55 | trượt |
| `median_daily_pnl` | 0,0 | > 0 | trượt |
| `trades_per_week` | 6,232 | ≥ 7,0 | trượt **11%** |
| `minimum_holdout_days` | 179,7 | ≥ 90 | **ĐẠT** |

**Con số duy nhất quan trọng: Portfolio CÓ gross edge dương trên holdout — và chi phí bằng
157% của nó.** Đó là **ràng buộc ràng buộc**, vượt **3,1×**, và **mọi thất bại khác đều suy ra
từ nó**: một chiến lược có chi phí vượt gross edge **không thể** có Sharpe dương, ngày trung
vị dương, hay tỉ lệ ngày dương trên một nửa.

r216/r217 **nghi ngờ** điều này ("friction giết 96% candidate gross-dương", "khoảng cách là
8×") từ phép đo **toàn-cửa-sổ, in-sample, sai đường**. **Nay nó được đo trên holdout, trên cấu
hình deploy, qua replay thực sự mô hình hoá Portfolio.** Nghi ngờ **đúng**, và độ lớn là
**1,57×, không phải 8×**.

**Hai rào cản cấu trúc, kiểm lại:** `minimum_holdout_days` **NAY ĐẠT** — r335/r336 kết luận
route này "không bao giờ qua được gate ở bất kỳ cửa sổ nào" một phần vì 500 ngày cho 84 ngày
quan sát; **900 ngày cho 152**. Nửa đó của rào cản **được gỡ bằng độ sâu cửa sổ, không bằng
thay đổi code**. Nhưng **bảy `input_continuity_failed` vẫn còn** (mọi interval trừ 5m) — lịch
giao dịch CFD (r337), **cấu trúc**. Vậy r335/r336 **đúng rằng route không qua được** và **sai
về phần nào là vĩnh viễn**.

**Ba metric được khai báo KHÔNG KHẢ DỤNG kèm lý do** thay vì phát số 0 — đúng refusal
semantics mà thay đổi này đặc tả, **đang hoạt động**.

**Giới hạn:** **không** khẳng định điều này khái quát hoá — một route, một cửa sổ, một cấu
hình. **Không** khẳng định giảm chi phí 1,57× sẽ làm cấu hình có lãi — tỉ số được **đo**,
**không phải** phản thực; r344/r345 cho thấy thay đổi chi phí **làm dịch luồng quyết định**.
**Không** diễn giải các con số drawdown: max total drawdown 7,3e−05 trên tài khoản lỗ 0,377 là
con số **tôi chưa hiểu**.

**Bước tiếp theo:** đo `cost_to_gross_pnl_ratio` trên **năm route còn lại** qua cùng gate, ghim
cửa sổ. Nếu tỉ số **trên 1,0 ở mọi nơi**, fleet **có edge thật nhưng đồng loạt quá nhỏ để trả
nổi friction**, và mục tiêu trở thành **chi phí mỗi lệnh** chứ không phải bất kỳ knob nào của
Portfolio — kết luận mà 184 iteration đã vòng quanh **mà không đo được**.

## Round 388 — NEEDS-MORE-RESEARCH: thiên lệch short của gold là hiệu ứng **số lần vào lệnh**. Thời gian giữ hành xử **giống hệt nhau trên mọi route** → guard và risk layer **bị loại**

`round388-NEEDS-MORE-RESEARCH-golds-short-bias-is-an-entry-count-effect-duration-behaves-identically-on-every-route.md`

**Zero container.** OPS không đổi, vẫn ở `FINAL_VERIFY`.

**Trước hết, sửa chính bước tiếp theo tôi đã nêu:** r387 nói bước kế là đọc phân bố tín hiệu
long/short của từng production candidate "từ Alpha sweep đã có sẵn trong `strategy_scores`".
**Dữ liệu đó không tồn tại** — entry của `strategy_scores` chỉ có `interval`, `strategy` và
theo split: `trades`, `realized_pnl`, `profit_factor`, `win_rate`, `max_drawdown`,
`funding_paid` — **không có trường side nào**. **Tôi đã đề xuất một phép thử mà không kiểm tra
input có sẵn hay không.**

**Phép tách thực sự có sẵn — và nó định vị được thiên lệch.** Exposure skew tách **chính xác**
thành số-lần-vào × thời-gian-giữ-trung-bình:

| route | vào lệnh L / S | giữ TB h L / S | **entry skew** | **duration skew** | exposure skew |
|---|---|---|---|---|---|
| **`exness XAU`** | 147 / 255 | 36,7 / 42,9 | **1,735×** | 1,171× | 2,032× |
| `binance BTC` | 467 / 424 | 10,1 / 14,0 | **0,908×** | 1,388× | 1,260× |
| `bybit BTC` | 491 / 360 | 10,3 / 13,6 | **0,733×** | 1,318× | 0,966× |

(Kiểm định danh: 1,735×1,171 = 2,032; 0,908×1,388 = 1,260; 0,733×1,318 = 0,966 — **khớp
chính xác** exposure skew quan sát được.)

**Duration skew nhất quán ở mọi nơi**: short được giữ lâu hơn 17–39% trên **cả ba route** →
đó là **thuộc tính chung của bộ máy**, **không thể giải thích một thiên lệch đặc thù route**.

**Entry skew mới là chỗ gold tách hẳn ra:** cả hai route BTC vào **long** nhiều hơn (0,908×;
0,733×), còn **gold vào short nhiều hơn long 1,735×**. **Gold không phải "lệch mạnh hơn cùng
chiều" — nó lệch NGƯỢC CHIỀU.**

**Vậy thiên lệch bắt nguồn ở khâu VÀO LỆNH, không phải ở thời gian giữ.** **Guard min-hold —
thứ chặn reversal và do đó tác động lên duration — bị LOẠI khỏi danh sách nguyên nhân**, cùng
mọi thứ hạ nguồn chỉ kéo dài vị thế.

**Một quan sát nữa, KHÔNG quy kết được:** `risk_rejected_counts` chỉ bắn ở đúng một gate mọi
nơi — `execution_cost` — **118 trên gold**, 63 `binance BTC`, 39 `bybit BTC`. Gold gấp **3×**
`bybit BTC`. Các số này **không tách theo chiều** nên **không quy kết được**; ghi lại vì gold
là cực trị ở cả hai chỉ số, không phải vì nó giải thích điều gì.

**Giới hạn:** **không** khẳng định cái gì sinh ra entry skew — phép tách nói **ở đâu**, không
nói **vì sao**. Ứng viên ensemble-composition của r387 **vẫn chỉ được nêu tên, chưa test**.
**Không** khẳng định guard không liên quan đến kết quả — nó bị loại với tư cách **nguồn của
thiên lệch chiều**, còn hiệu ứng PnL lớn đo ở r371–r375 vẫn nguyên.

**Bước tiếp theo, lần này đã kiểm là có tồn tại:** chiều của decision stream chỉ quan sát được
trong record đã xuất **sau khi** guard và risk layer tác động. Muốn thấy phân bố **trước
guard**, control `legacy_selected_rule` cần **bản export riêng** — `--emit-trades` hiện chỉ
xuất **đường có guard**. Xác nhận điều đó là **câu hỏi đọc code trước**: nếu luồng legacy
**cũng** lệch short 1,7× trên gold → thiên lệch nằm **thượng nguồn ở Alpha ensemble**; nếu nó
**cân bằng** → **khâu tổng hợp của Portfolio tạo ra nó**.

## Round 387 — REJECTED: thiên lệch short của gold là **cấu trúc, không do xu hướng**. Tiêu chí đăng ký của tôi **đặt sai lần thứ bảy**

`round387-REJECTED-golds-short-bias-is-structural-not-trend-driven-and-my-registered-criterion-was-mis-specified-for-the-seventh-time.md`

**Zero container.** Giả thuyết dẫn đầu là **thiên hướng mean-reversion bán vào sức mạnh** —
hai trong ba production candidate của gold là chiến lược reversion — dự đoán **tỉ trọng short
phải tăng ở nơi giá đã tăng**.

**Quan sát: Spearman ρ = +0,006 trên mười decile thời gian. Đó là số 0.**

**Tiêu chí tôi đăng ký đặt sai lần thứ bảy** (r327, r330, r340, r354, r373, r378, r387): tôi
viết *"dương → nhất quán với bán vào sức mạnh"*, mà +0,006 **là** dương — **đúng như viết thì
test sẽ trả lời CÓ**. **Một phép thử theo dấu, không có ngưỡng độ lớn, biến mọi nhiễu thành
xác nhận.** Tôi đọc **con số, không đọc tiêu chí**: **không có tương quan, giả thuyết theo xu
hướng bị bác bỏ.**

**Decile cho thấy gì:** short share **trên 50% ở tám trên mười decile** bất kể giá ở đâu.
Decile 8 và 9 ở **gần như cùng một mức giá** (4878 và 4714) nhưng **90,7% và 37,1% short** —
**biến động rộng nhất bảng, trên thay đổi giá nhỏ nhất**. **Thiên lệch là dai dẳng và độc lập
với giá.**

**Phát hiện thay thế — thiên lệch này đặc thù cho gold:**

| route | long h | short h | **short share** |
|---|---|---|---|
| **`exness XAU`** | 5.390 | 10.951 | **67,0%** |
| `binance BTC` | 4.696 | 5.920 | 55,8% |
| `bybit BTC` | 5.070 | 4.898 | 49,1% |

`bybit BTC` **cân bằng**, `binance BTC` lệch nhẹ, và **gold dành hai trên ba giờ phơi nhiễm
để short — trên đúng route đã tăng 105%.**

**Một cơ chế ứng viên, nêu tên và KHÔNG test:** gold nhận **ba** production candidate so với
**năm** của BTC (r375), và cái riêng của nó là `mtf_stochastic_5m_4h_sma5` — một **oscillator**
— trong khi extras của BTC gồm stochastic, MACD **và** một biến thể candle-momentum, tức
**BTC có trọng số momentum mà gold không có**. **Hợp lý không phải là đã đo**: thành tích của
arc này với các cơ chế "nghe hợp lý" **rất tệ** — câu chuyện whipsaw-tần suất của r372 và
câu chuyện số-input của r375 **đều bị bác bỏ bởi chính dữ liệu gợi ra chúng**.

**Giới hạn:** **không** khẳng định nguyên nhân nào cho thiên lệch short của gold. **Không**
khẳng định thiên lệch tự nó có hại — nó tốn kém **trên cửa sổ này** vì gold tăng; trên cửa sổ
giảm nó sẽ **có lợi**, và r386 đã xác lập kết cục theo chiều ở đây là **drift alignment**.
**Không** khẳng định ba route lập thành một mẫu hình — hai route BTC cùng instrument gần như
**một quan sát** (r276). **Không** khẳng định proxy giá theo decile là chính xác.

**Bước tiếp theo:** so **phân bố tín hiệu long/short của từng production candidate** trên gold,
dùng Alpha sweep đã có sẵn trong `strategy_scores` của mọi run. Nếu các candidate oscillator
lệch short trên instrument đang tăng còn momentum thì không → **định vị được cơ chế**; nếu cả
ba đều cân bằng → **thiên lệch nằm ở khâu tổng hợp của Portfolio chứ không ở input**, một chỗ
khác và **nghiêm trọng hơn** để soi.

## Round 386 — REJECTED: bất đối xứng chiều là **drift alignment trên cả ba route** — hướng này **đóng**. P2-3 đã xong, transaction vào **FINAL_VERIFY**

`round386-REJECTED-the-side-asymmetry-is-drift-alignment-on-all-three-routes-and-the-last-verification-finding-is-closed.md`

| route | move/h khi long | khi short | tỉ số | net long | net short | chiều tốt hơn |
|---|---|---|---|---|---|---|
| `exness XAU` | +5,152e−05 | +5,274e−05 | 1,024 | **+0,65265** | −3,81407 | **long** |
| `binance BTC` | −5,525e−05 | −6,697e−06 | 0,121 | −3,63186 | **−1,84068** | **short** |
| `bybit BTC` | −8,798e−06 | −1,688e−05 | 1,918 | −2,67790 | **−1,40548** | **short** |

**Drift của gold dương ở cả hai trạng thái; cả hai route BTC âm ở cả hai.** Gold tăng, BTC giảm.

**Chiều tốt hơn, trên MỌI route, đơn giản là chiều đứng cùng drift của instrument.** Long
thắng trên tài sản tăng, short thắng trên tài sản giảm. Đây đúng là lời giải thích r385 đã
lập cho gold, và **nay nó phủ cả ba route — kể cả hai route mà bất đối xứng chỉ theo hướng
NGƯỢC LẠI**, thứ từng khiến chúng trông như một hiện tượng riêng. **Không có timing theo chiều
ở bất kỳ đâu trong bảng này.**

**Phần dư là route-local và không khái quát hoá:** trên `binance BTC` thị trường giảm **nhanh
gấp 8,3× khi đang long** — **anti-timed thật sự**; trên `bybit BTC` giảm nhanh gấp 1,9× khi
đang short — well-timed nhẹ. **Cùng instrument, cùng cửa sổ ghim, cùng cấu hình, dấu timing
ngược nhau.** Khớp với r345 và độ nhạy cửa sổ r382. Một hiệu ứng route-local nữa, **không xây
tiếp lên nó**.

**Tiêu chí để lại:** nếu side rule được implement, yêu cầu của r385 nay có **ba route** đứng
sau thay vì một — **tiêu chí phải là "thắng exposure thụ động trên cùng đoạn bar", không bao
giờ là "PnL dương"**, vì trên mọi route đã test, **chiều có lãi là chiều thị trường trao cho nó**.

**Verify — finding cuối đã đóng.** **P2-3 RESOLVED**: commit `ae6a1fd`; kiểm bằng cách chạy —
report của gate nay có `data_as_of = 2026-08-31T00:00:00Z`. **Tất cả finding đã đóng** (P1,
P2-1, P2-2, P2-3); task 4.2 khớp tới 1,8e−15; **702 test pass trong run của tôi**;
`finance-core` không chạm, `finance-strategy` thuần additive. **Transaction ở FINAL_VERIFY.**

**Giới hạn:** **không** khẳng định drift alignment là toàn bộ câu chuyện — nó giải thích
**chiều nào thắng**, còn dấu timing phần dư vẫn khác nhau giữa hai thị trường gần như giống
hệt và **điều đó chưa giải thích được**. **Không** khẳng định rule long-only sẽ thất bại: trên
gold nó có thể lãi **như beta**, trên BTC cửa sổ này nó sẽ **lỗ** vì BTC giảm — **cả hai kết
cục đều không chứng minh được kỹ năng**. **Không** khẳng định BTC giảm bao nhiêu — **suy ra**
từ bốn drift đều âm, không phải từ truy vấn giá. **Chưa push gì**, và **push là hành động
hướng ra ngoài tôi sẽ không tự làm.**

**Câu hỏi nghiên cứu mở từ r385 vẫn đứng và KHÔNG phải câu hỏi về chiều:** vì sao Portfolio
short 51% thời gian trên route tăng 105%, và long đúng vào những nhịp giảm nhanh nhất trên
`binance BTC`? Cả hai chỉ về **thành phần Alpha ensemble** (ba production candidate trên gold,
r375), **không** về bất kỳ knob nào của Portfolio.

## Round 385 — REJECTED: chiều long dương của gold là **drift, không phải edge**. Strategy **không có timing theo chiều** — và **ngược drift 75% thời gian**

`round385-REJECTED-golds-positive-long-side-is-drift-not-edge-the-strategy-has-zero-directional-timing-and-is-wrong-sided-75-percent-of-the-time.md`

**Zero container**: record audit đã xuất + **một** truy vấn giá read-only hẹp.

`exness XAU`, cửa sổ ghim, 174.253 nến = 14.521 giờ (605,0 ngày nến — lịch giao dịch, r370).
Gold **2174,827 → 4458,240 = +105,0%**.

| | phơi nhiễm (h) | tổng raw move | **move mỗi giờ** |
|---|---|---|---|
| khi **long** | 5.389,8 | +0,27767 | **5,152e−05** |
| khi **short** | 10.950,7 | +0,57752 | **5,274e−05** |
| toàn cửa sổ (thụ động) | 14.521,1 | +1,04993 | 4,943e−05 |

**Drift khi short ÷ drift khi long = 1,024.** Thị trường tăng **cùng một tốc độ** ở cả hai
chiều — thậm chí **nhanh hơn chút khi strategy đang short**. Cả hai đều trong khoảng 7% của
drift thụ động. **Đó là không có timing theo chiều.**

**Con số thực sự quan trọng: strategy short 75,4% thời gian và long 37,1%** — nó dành **gấp
2,0 lần thời gian đứng NGƯỢC drift chủ đạo** trên một route tăng **+105%**. Vậy "thành phần
dương đầu tiên của arc" (r384) **không phải phát hiện về chiều long** — nó là **nửa nhìn thấy
được của một strategy bị lệch chiều một cách hệ thống trên route này**.

**Ý nghĩa cho rule long-only:** trên cửa sổ này nó **rất có thể có lãi** — và đó sẽ là **beta,
không phải alpha**: một vị thế định hướng trong tài sản đã tăng gấp đôi, gánh nguyên drawdown
của vị thế đó, **không có bằng chứng về timing**. Gọi đó là cải thiện Portfolio-layer chính là
**tautology mà r255 và r257 đã bắt được chương trình này mắc phải**.

**Không phải lý lẽ chống lại việc implement side restriction** — mà là: **nếu implement, tiêu
chí nghiệm thu phải là "thắng được exposure thụ động trên cùng đoạn bar", không phải "PnL
dương"** — nếu không, **mọi rule long-only trên tài sản đang tăng đều pass một cách tầm thường.**

**Câu hỏi đáng mang tiếp thay vào đó:** *vì sao Portfolio short 75% thời gian trên một route
tăng 105%?* Đây **không** phải câu hỏi beta và **không** được trả lời bằng việc hạn chế chiều.
Ứng viên **chưa test**: thành phần Alpha ensemble trên route đó (chỉ ba production candidate —
r375), thiên hướng mean-reversion của `rsi_mean_reversion` và `candle_reversion` trong thị
trường trending, hoặc tính đối xứng của entry threshold.

**Giới hạn:** **không** khẳng định rule long-only sẽ **lỗ** — nó có thể có lãi; điều khẳng định
là **làm vậy chẳng chứng minh được gì**. **Không** khẳng định strategy lệch chiều trên route
khác: **một route, một cửa sổ**, và bất đối xứng short-tốt-hơn của BTC (r384) chỉ theo **hướng
ngược lại** trong khi BTC **cũng tăng** — nên cùng logic drift **không hiển nhiên chuyển sang
được** và tôi **chưa chạy**. **Không** khẳng định drift là hằng số trong cửa sổ — đo theo
**trung bình**.

**Bước tiếp theo:** chạy đúng phép tách drift này trên **hai route BTC** từ record **đã có** —
**zero container**. Nếu bất đối xứng của BTC cũng sụp thành drift, **toàn bộ hướng side đóng**;
nếu không, **BTC mới là nơi một side rule thực sự test được**.

## Round 384 — NEEDS-MORE-RESEARCH: bất đối xứng chiều **đảo dấu theo instrument**, và trên `exness XAU` **riêng chiều long là DƯƠNG**

`round384-NEEDS-MORE-RESEARCH-the-side-asymmetry-inverts-by-instrument-and-golds-long-side-alone-is-positive.md`

| route | lệnh | short (n, /lệnh) | long (n, /lệnh) | short/long |
|---|---|---|---|---|
| `bybit BTC` | 847 | 363, −0,003086 | 484, −0,005161 | **1,67×** |
| `binance BTC` | 891 | 424, −0,004341 | 467, −0,007777 | **1,79×** |
| **`exness XAU`** | 402 | 255, −0,014957 | **147, +0,004440** | **−0,30×** |

**Hai route BTC đồng thuận chặt** — short tốt hơn 1,67× và 1,79× mỗi lệnh. **Hiếm** với arc
này, nơi gần như mọi hiệu ứng đều bất đồng qua route.

**Trên `exness XAU` dấu đảo và chiều long DƯƠNG**: 147 lệnh, **+0,65265 tổng**, +0,004440
mỗi lệnh, trong khi short lỗ −3,81407 trên 255 lệnh. **Toàn bộ khoản lỗ của route nằm ở
chiều short**, và gold cũng là route short nhiều nhất (63,4% số lệnh). **Lần đầu tiên trong
arc một phép tách kết quả Portfolio cho ra thành phần dương.**

**Điều này KHÔNG có nghĩa gì:** **cộng các lệnh long không phải mô phỏng long-only** — bỏ
short làm đổi chính những long nào xảy ra. **+0,65265 không phải dự báo hiệu năng long-only**,
và **chưa có flag để chạy** (r383).

**Và lời giải thích hiển nhiên là thứ arc này đã từng tự vấp:** gold tăng trong cửa sổ này,
nên kết quả thiên long trên tài sản đang lên **có thể là drift, không phải edge**. Vòng
254–257 đã đi qua đúng chỗ này — r255: *"cửa sổ thuận lợi không độc nhất cũng không dự báo
được, và drift giải thích được nó"*; r257: control population xác nhận **tautology**. **Chiều
long dương trên gold phải được so với drift mà bất kỳ exposure long nào cũng có trên cùng
đoạn bar, trước khi nó có ý nghĩa gì.** So sánh đó **chưa làm** và là việc **đầu tiên**, **trước**
mọi implementation side-restriction.

**Giới hạn:** **không** khẳng định long-only sẽ có lãi trên `exness XAU`. **Không** khẳng định
chiều long dương của gold là edge chứ không phải drift — **chưa giải thích** cho tới khi chạy
so sánh drift. **Không** khẳng định đồng thuận BTC khái quát hoá: hai route **cùng một
instrument** với giá bám sát nhau (r276: volatility giống tới ba chữ số) **gần như là một quan
sát, không phải hai**. **Không** khẳng định lát cắt ổn định qua cửa sổ — mỗi route một cửa sổ,
và r382 cho thấy dịch ba nến làm PnL đổi 8,3%.

**Transaction:** FIX round 3 đang chạy cho **P2-3** (report của gate thiếu `data_as_of`) —
**round cuối cùng `OPS_MAX_FIX_ROUNDS` cho phép**. Findings round 3 cũng ghi, cho design chứ
không cho worker, rằng dạng end-to-end của task 1.3 **không thực thi được** và **không được
thêm report mới** để thoả nó. Mọi thứ khác đã đóng.

## Round 383 — NEEDS-MORE-RESEARCH: **lệnh short lỗ ít hơn 40% mỗi lệnh so với long** — lát cắt theo chiều đầu tiên của arc. Kèm P2: report của gate **thiếu `data_as_of`**

`round383-NEEDS-MORE-RESEARCH-short-trades-lose-40-percent-less-per-trade-than-long-and-the-gate-report-omits-data-as-of.md`

**Hướng mới, theo gợi ý của user** (long-only / short-only như một rule riêng) — và nó
**trả lời được ngay vòng này** vì audit trail từng-lệnh verify ở r380 **mang trường `side`**:
lần đầu tiên trong arc một kết quả Portfolio có thể **tách theo chiều**.

`bybit BTC` @900, cấu hình deploy, từ 847 record:

| chiều | lệnh | PnL | PnL/lệnh |
|---|---|---|---|
| **short** | 363 | −1,12027 | **−0,003086** |
| **long** | 484 | −2,49803 | **−0,005161** |

**Short lỗ ít hơn 40,2% mỗi lệnh**, và Portfolio vào long **nhiều hơn 33%**. **Cả hai chiều
đều âm** nên **không chiều nào là candidate** — nhưng bất đối xứng **1,67×/lệnh**, **xa ngoài**
jitter cửa sổ đo ở r382.

**Cảnh báo phương pháp quan trọng nhất: cộng các lệnh long KHÔNG phải là mô phỏng long-only.**
Bỏ short **làm đổi chính những long nào xảy ra** — guard min-hold chặn **reversal**, một short
không mở ra sẽ đổi long kế tiếp, và risk layer thấy chuỗi vị thế khác. **Kết quả side-restricted
phải được CHẠY, không suy ra được từ lát cắt này.**

**Hôm nay chưa chạy được**: `grep` không tìm thấy `long_only`/`short_only`/`allowed_side` trong
CLI, trong `portfolio_risk.rs` hay `trading_modes.rs`. **User đúng: đây là một rule riêng**, cần
thay đổi code, và là **OpenSpec item tiếp theo tự nhiên** sau khi transaction hiện tại đóng.

**Tiến độ verify:** `cargo test --workspace` trên `f158e04` **do tôi chạy: 702 passed, 0 failed,
37 suite**. Gate và non-gate **trên một cửa sổ ghim** (`exness XAU` @900, `candle_count` 174.254
ở cả hai): **invariant bao hàm đạt** trên cả hai đường; holdout mang **39,8%** số lệnh trên cửa
sổ **20,0%** — Portfolio giao dịch dày gấp đôi ở đoạn cuối, khớp với warm-up tám interval (r267).

**Chỉ số tạm −40,3% của r381 bị thay thế**: trên cửa sổ ghim, advantage của `exness XAU`
**dương ở cả hai phạm vi** (+5,2% holdout, +16,4% toàn cửa sổ). Nó đến từ build chưa ghim và
tôi **đã từ chối ghi nó thành finding** — đây chính là lý do.

**P2-3 — report của gate thiếu `data_as_of`.** Non-gate có ghi, **gate thì không**, dù gate
**nhận và tôn trọng** `--as-of`. Vậy **một verdict gate không tự chứng minh được là tái tạo
được từ chính output của nó** — đúng mục đích của fix round 2. Nhỏ, cơ học, nên đóng trước release.

**Tiêu chí đẳng thức cross-path: kết luận là KHÔNG THỰC THI ĐƯỢC** với bề mặt output hiện tại —
không có `one_target` giới hạn holdout, và run `--days 180` **không thay thế được** vì nó khởi
động Portfolio **nguội**, trong khi holdout của gate đạt tới khi Portfolio **đã ấm**. **Ghi thẳng
thay vì hoãn lần thứ tư.**

**Giới hạn:** **không** khẳng định long-only/short-only sẽ cho kết quả như lát cắt gợi ý — lát
cắt là **mô tả**. **Không** khẳng định bất đối xứng khái quát hoá được: **một route, một cửa sổ,
một cấu hình**, và **mọi hiệu ứng dạng-chiều trong arc đến nay đều trượt bài test qua route**.
Không cơ chế. **Chưa push gì.**

## Round 382 — DATA-ISSUE: **mọi backtest trong arc này dùng cutoff wall-clock theo từng interval**, nên **không hai run nào từng phủ cùng một tập bar**. P1 của tôi đòi một giá trị không tái tạo được; tiêu chí khả thi nay **đạt**

`round382-DATA-ISSUE-every-backtest-in-this-arc-used-per-interval-wall-clock-cutoffs-so-no-two-runs-ever-shared-the-same-bars.md`

**Cơ chế, xác nhận trong code:** `klines.rs:230` lấy `Utc::now()` **bên trong
`pub async fn load(...)`**, và `load` được gọi **một lần mỗi interval**;
`PORTFOLIO_INTERVALS` có **tám** phần tử → **một run lấy tám cutoff khác nhau**, cách nhau
vài giây đến vài phút; và **qua các run, cả cửa sổ trôi theo đồng hồ**. Giống hệt ở
`14afa8e`, `59e2489`, `c07951a` → **có trước thay đổi này và trước mọi vòng trong arc.**

**P1 của tôi đòi một giá trị không thể tái tạo**: baseline chưa từng ghi lại tám cutoff của
nó và `--as-of` khi đó chưa tồn tại. **Cả hai vòng FIX đã đuổi theo một con số bất khả.**

**Tiêu chí khả thi là tất định dưới cutoff ghim** — fix round 2 (`f158e04`) thêm `--as-of`
và trường `data_as_of`. Hai run cùng cutoff: `candle_count` 259.201, 851 lệnh,
−4,083376695749315 — **và sha256 của toàn báo cáo giống hệt nhau**. **P1 đóng** — không phải
bằng cách khôi phục số cũ, mà bằng cách xác lập **run tái tạo được khi cửa sổ được ghim**,
đúng thuộc tính thực sự thiếu.

**Hệ quả cho bản ghi nghiên cứu:** bốn run cùng route, cùng cửa sổ danh nghĩa cho
259.198/847/−3,7693 · 259.198/847/−3,6183 · 259.198/846/−3,7134 · 259.201/851/−4,0834.
**Dịch ba nến làm PnL đổi 8,3% và số lệnh đổi 4** — khớp với r345 ("replay hỗn loạn theo
input"). Vậy **cổng validity tôi dùng từ r361 — "cùng `candle_count` nên cùng cửa sổ" — là
SAI. Cùng độ dài không có nghĩa cùng bar.**

**Không retract vòng cũ nào** — jitter phụ thuộc route/cửa sổ và tôi mới đo **một lần** —
nhưng **mọi chênh lệch PnL cross-run trong arc nhỏ hơn vài phần trăm nay phải đọc là CHƯA
XÁC LẬP**, và từ đây dùng `--as-of`. **Hiệu ứng lớn không bị ảnh hưởng**: +29,6% tần suất
(r368), spread 2–5 input (r375), bất đồng dấu qua route (r372), biên ±20–70% của guard
advantage — đều **xa ngoài** jitter này.

**Trạng thái verify:** P1, P2-1, P2-2 **đều đã giải quyết** (P2-2 kiểm là **thuần additive**).
**Còn nợ trước FINAL_VERIFY:** tôi mới chạy `cargo test --workspace` trên `59e2489` (699
passed), **chưa** trên `f158e04`; và **tiêu chí đẳng thức cross-path vẫn chưa chạy** — nhưng
**với `--as-of` thì nay đã khả thi**.

**Giới hạn:** **không** khẳng định vòng cũ nào sai. **Không** khẳng định tám cutoff trong
**một** run gây lệch **đáng kể** — tôi chưa đo riêng khoảng cách đó. **Không** khẳng định
`--as-of` làm run so sánh được qua máy khác hay qua data revision: Binance vẫn sửa kline
(r347) dưới cùng một cutoff. **Chưa push gì.**

## Round 381 — DATA-ISSUE: bản fix cho ra **giá trị thứ ba** và **đổi cả số lệnh**, nên `run_id` chỉ là **một phần** nguyên nhân

`round381-DATA-ISSUE-the-fix-produced-a-third-value-and-changed-the-trade-count-so-run-id-was-only-part-of-the-cause.md`

**FIX round 1**: Codex `gpt-5.6-terra`/high, exit 0, `result_class: success`, commit
`c07951a`. Nguyên nhân gốc nó nêu **hợp lý**: replay hợp nhất đã đổi `DecisionScope.run_id`
từ `"portfolio-construction-comparison"` sang `"portfolio-measurement-integrity"`, và scope
của risk layer rõ ràng nuôi một thứ tất định → **đổi chuỗi làm dịch quyết định risk và do đó
dịch fill**. Nó khôi phục giá trị cũ và thêm regression test. **Codex không chạy được** kiểm
tra 900 ngày (môi trường của nó không có endpoint) — **phép kiểm tra đó là của tôi và là toàn
bộ vấn đề.**

| build | nến | lệnh | `one_target.realized_pnl` |
|---|---|---|---|
| trước hợp nhất (**yêu cầu**) | 259.198 | **847** | **−3,769332905847924** |
| `59e2489` | 259.198 | 847 | −3,618298890847919 |
| **`c07951a`** | 259.198 | **846** | **−3,713368400847926** |

Khôi phục `run_id` **kéo PnL về gần** giá trị yêu cầu nhưng **không tới**, **và tạo ra chênh
lệch số lệnh chưa từng có**: `59e2489` khớp đúng 847, `c07951a` cho 846. Vậy `run_id` **nhiều
nhất là một phần** nguyên nhân, và bản fix nay còn làm nhiễu **cả luồng quyết định**. **Ba
build, ba kết quả.**

**Điểm phương pháp mang vào findings round 2:** regression test mới của Codex **pass** trong
khi run 900 ngày thật **fail** → fixture tổng hợp không chạm được thứ đang khác là **cần
nhưng không đủ**; round 2 hỏi **thẳng vì sao fixture bỏ sót**, thay vì đòi thêm fixture.

**Đã giải quyết và đã verify:** **P2-1** segment 1 nay mang `"comparable": false`. **P2-2**
required input nay **do strategy khai báo** trong `crates/finance-strategy` (enum,
`required_inputs()` **mặc định rỗng**, wrapper forward) và loại trừ không còn khớp theo tên.
**Đã kiểm là thuần additive: không `evaluate()` nào đổi** → **không ảnh hưởng hành vi strategy
production** — kiểm có chủ ý vì `finance-strategy` là crate **live worker đang dùng**.

**Một quan sát tạm, đánh dấu là tạm và KHÔNG ghi thành finding:** gate run `exness XAU` @900
trên `c07951a`, holdout 179,7 ngày: faithful 161 lệnh/−0,39768 so với control 169/−0,28338 →
**advantage −0,11430 (−40,3%)**. Toàn-cửa-sổ trên build trước, route này **+68,7%** (r372).
**Trên holdout nó âm.** Nếu sống sót, đây là **đảo dấu giữa toàn-cửa-sổ và holdout trên cùng
một route**. Nhưng nó đến từ **build mà đường đo đang bất ổn qua ba commit — đúng defect đang
sửa** — nên nó được ghi để **kiểm lại khi P1 đóng, không phải để trích dẫn**.

**Giới hạn:** **không** khẳng định nguyên nhân phần chênh còn lại — findings round 2 liệt kê
**nơi cần so sánh** và nói rõ **đó không phải chẩn đoán**. **Không** khẳng định `run_id` vô
can. **Chưa** thử tiêu chí đẳng thức cross-path: đường đo đang bất ổn nên so sánh với nó
**chỉ đo được chính sự bất ổn đó**. `OPS_MAX_FIX_ROUNDS` = 3 → **còn đúng một round** sau
round này. **Chưa push gì.**

## Round 380 — DATA-ISSUE: xác minh độc lập phát hiện **đường đo dịch 4% trên cửa sổ y hệt**; **audit trail đối chiếu chính xác**

`round380-DATA-ISSUE-independent-verification-finds-the-measurement-path-moved-4-percent-on-an-identical-window-and-the-audit-trail-reconciles-exactly.md`

**Phát hiện P1** — `bybit BTC` @900, cấu hình deploy, **không cờ gate** (đúng lệnh mà task
3.4 yêu cầu **không được đổi**):

| trường | build cũ | commit `59e2489` | lệch |
|---|---|---|---|
| `candle_count` | 259.198 | 259.198 | y hệt |
| `one_target.trades` | **847** | **847** | y hệt |
| `one_target.realized_pnl` | **−3,769332905847924** | **−3,618298890847919** | **+0,151034 (+4,0%)** |
| `funding_paid` | 0,017 | 0,016 | −0,001 |

**Luồng quyết định không đổi — 847 lệnh đóng ở cả hai — nên độ lệch nằm ở mức fill/chi phí,
không phải ở điều Portfolio quyết định.** Funding chỉ giải thích 0,001 trong 0,151 →
**khoảng 99% chưa giải thích được**. Ứng viên hiển nhiên đã loại: `execute_target` chỉ uỷ
quyền cho `execute_target_with_closed_trade`, nên hoán đổi hai hàm **không** phải nguyên
nhân; `finance-core` không đổi nên nguyên nhân nằm trong `crates/finance-research`.

**Có thể giá trị mới mới là đúng và giá trị cũ sai — đó sẽ là kết quả tốt** — nhưng một cú
dịch 4% **chưa giải thích được** ở đúng đường mà thay đổi này **bắt buộc phải để yên** chính
là loại defect mà thay đổi này sinh ra để loại bỏ. **Phải được giải thích, không được hấp
thụ.** OPS: `VERIFY` → **`FIX` round 1**, findings đã ghi, Codex FIX worker đã chạy. **Không
đoán cơ chế** trong findings — yêu cầu là "tái tạo giá trị cũ, hoặc nêu tên code path và biện
minh cho giá trị mới".

**Phần đạt:** **Task 4.2 đối chiếu chính xác** — `--emit-trades` cho **847 record** đúng bằng
847 lệnh báo cáo, `sum(realized_pnl)` khớp tới **1,8e−15**. **Lần đầu tiên trong arc một số
tổng có thể kiểm chứng được với từng fill — audit L4 đóng.** `cargo test --workspace` **do
tôi chạy**: **699 passed, 0 failed, 37 suite** → claim của Codex nay được **xác nhận độc lập**.

**Quan sát phạm vi:** walk-forward áp cho **Alpha sweep**, **không** cho đường Portfolio, và
**dựng lại `candidates()` mỗi segment** để strategy có state không mang quan sát sang segment
sau — lựa chọn chống rò rỉ có chủ ý. Vậy blocker r352 **đóng cho lớp Alpha**; lớp Portfolio
vẫn chỉ có **một holdout đuôi**, vẫn lồng nhau theo `--days`. **Không vi phạm spec** (yêu cầu
không nêu lớp) nhưng OOS của Portfolio được cải thiện nhờ **gate trở nên trung thành**, **không
phải** nhờ walk-forward — bản ghi không được nhập nhèm hai điều đó.

**Giới hạn:** **không** khẳng định nguyên nhân cú dịch 4% — một ứng viên đã loại, **chưa xác
định cơ chế**. **Không** khẳng định giá trị mới sai. **Không** khẳng định tiêu chí đẳng thức
cross-path đã chạy — **vẫn còn nợ**, và walk-forward hoá ra **không** cung cấp figure Portfolio
giới hạn holdout nên đường đó **đã đóng**, cần cách khác. **Chưa push gì.**

## Round 379 — NO-CHANGE: task 2–5 đã verify trong code, **hai finding P2**, và phép kiểm tra đẳng thức cross-path **vẫn còn nợ**

`round379-NO-CHANGE-tasks-2-to-5-verified-in-code-two-p2-findings-and-the-cross-path-equality-check-still-outstanding.md`

**Zero container.** OPS vẫn ở `VERIFY`.

**Đã verify bằng đọc code đã commit:** **Task 3** walk-forward — `split.rs:50` cho
`training = klines[..start]`, `evaluation = klines[start..end]` → **phân hoạch đúng một
lần**, rời nhau, training **hoàn toàn sớm hơn**; test `split.rs:191` khẳng định liên tục,
tổng rời nhau, tính neo, và **ranh giới no-look-ahead**. **Task 2** — `ExecutionFootprint`
nay có đủ chín metric, **tất cả là `Option`** (vắng mặt chứ không phải 0, đúng yêu cầu), và
implementation **import từ module gate** chứ không nhân bản. **Task 4** — `--emit-trades`.
**Task 5** — `excluded: Option<String>`, `exclusion_reason`, dòng excluded **trượt**
`survives_selection`, và `sweep.rs:60` trả `realized_pnl = 0` khi `trade_count == 0` —
**đúng defect r374, đã đóng.**

**P2-1 — segment 1 của walk-forward được chấm với training RỖNG.** `split.rs` cho segment 1
`training = klines[..0]` và test **tự khẳng định** `segments[0].training.is_empty()`. Yêu
cầu được thoả **theo nghĩa đen** (không có bar nào sớm hơn), nhưng r267 đã xác lập Portfolio
**không quyết định** cho tới khi đủ tám interval đồng bộ → **số của segment 1 bị warm-up chi
phối và không so sánh được với các segment sau.**

**P2-2 — luật loại trừ bị hardcode theo tên một strategy.** `exclusion_reason` trả `None`
trừ khi tên chứa `taker_imbalance`. Yêu cầu trong spec là **tổng quát**. Audit r375 cho thấy
family taker là cái **duy nhất hiện đang** bị ảnh hưởng nên output hôm nay đúng — **nhưng
một strategy mới, hoặc một strategy cũ trên route thiếu cột khác, sẽ lại bị thoái hoá âm
thầm**, đúng thứ yêu cầu này sinh ra để chặn.

**Cả hai đều không phải P0/P1** nên không tự chúng chặn release.

**Phép kiểm tra đẳng thức vẫn còn nợ:** test hiện có so gate với hàm dùng chung **trên cùng
tập decision**; nó **không** chứng minh gate và `portfolio_measurement` **đưa cùng input**
vào hàm đó — đúng chỗ hai đường vẫn có thể lệch. Bằng chứng mạnh nhất hiện có là **gián
tiếp**: dấu faithful-so-với-control của gate **khớp dấu toàn-cửa-sổ đã biết độc lập trên cả
hai route** (dương `bybit BTC`, âm `binance XAU`) — khớp trên hai route **ngược dấu** sẽ là
trùng hợp nếu input sai. **Đó là lập luận, không phải phép kiểm tra đã ghim.**

**Test suite:** tôi **tự chạy** `cargo test --workspace` với hard timeout 25 phút. Khi đóng
vòng nó **vẫn đang chạy, chưa thấy failure nào** — **chưa xong nên tôi không khẳng định gì**.
Báo cáo "đã pass" của Codex vẫn là **claim của worker**; `verification_mode=independent`
nghĩa là **không tính** cho tới khi run của tôi kết thúc. **Chưa thấy failure ≠ đã pass.**

**Bước tiếp theo:** đọc kết quả test khi xong; chạy tiêu chí đẳng thức trên **cơ sở giới hạn
holdout**; chạy `--emit-trades` một lần và **đối chiếu record với số tổng** — đó là acceptance
check của chính task 4.2 và là cách duy nhất xác nhận audit trail có thật. **Chỉ sau đó** mới
FINAL_VERIFY.

## Round 378 — NEEDS-MORE-RESEARCH: VERIFY **đạt về cấu trúc**, **phép kiểm tra đẳng thức của chính tôi đặt sai cơ sở**, và guard advantage được đo **trên holdout lần đầu tiên**

`round378-NEEDS-MORE-RESEARCH-verify-passes-structurally-my-own-equality-check-was-mis-specified-and-the-guard-advantage-is-measured-on-holdout-for-the-first-time.md`

**IMPLEMENT xong**: Codex `gpt-5.6-luna`/high, attempt 1, exit 0, `result_class: success`,
commit local **`59e2489`**, 8 file, +916/−183, **chưa push**. OPS: `IMPLEMENT` → **`VERIFY`**.

**Xác minh độc lập — phần đạt** (kiểm bằng code và run thật, **không** bằng tóm tắt worker):
`finance-core` **không bị chạm** → yêu cầu an toàn giao dịch đạt ở mức diff. **Một hàm
replay dùng chung** (`portfolio_decision_replay.rs:50`) áp dụng đủ `construct` →
`evaluate_historical` → `execution_target` → `execute_target` và được gọi bởi **cả**
`daily_profit_gate.rs:414` **và** `portfolio_measurement.rs:356`. **Xung đột CLI đã hết** —
cả hai run thật **chấp nhận `--daily-profit-gate` cùng `--portfolio-minimum-hold-decisions 36`**;
`conflicts_with` còn lại ở `main.rs:237` thuộc **`weighted_ensemble_gate`**, một flag khác —
**đã kiểm, không phỏng đoán**. Control được giữ và khác biệt; gate giới hạn holdout đúng
**20,0%**.

**Khiếm khuyết nằm ở phép kiểm tra của chính tôi.** r377 ghim giá trị `one_target`
**toàn-cửa-sổ** làm mốc đẳng thức, nhưng **gate giới hạn holdout theo thiết kế** — đó chính
là mục đích của nó. So một số holdout với baseline toàn-cửa-sổ **không thể đạt và không kiểm
tra được gì**: `bybit BTC` gate faithful 219 lệnh / −2,45576 so với ghim 847 / −3,76933;
219/847 = 25,9% trên holdout chiếm 20,0% cửa sổ — **nhất quán với một implementation đúng**.

**Đây là pre-registration đặt sai thứ sáu của arc (r327, r330, r340, r354, r373, r378) và
là cái đầu tiên nằm ở khâu verification chứ không phải research.** `binance XAU` còn trả
75.696 nến so với 75.672 đã ghim — 24 bar mới tới ở venue horizon từ r372: **baseline ghim
trên route đang lớn thì hết hạn**.

**Kết quả nghiên cứu mới — guard advantage trên holdout, lần đầu:**

| route | holdout | faithful | control `legacy` | advantage |
|---|---|---|---|---|
| `bybit BTC` | 180,0 ngày | 219 lệnh, −2,45576 | 286 lệnh, −3,11011 | **+0,65435 (+21,0%)** |
| `binance XAU` | 52,6 ngày | 36 lệnh, −0,62329 | 38 lệnh, −0,41645 | **−0,20684 (−49,7%)** |

**Cả hai dấu tái lập ngoài mẫu**: dương trên `bybit BTC` (+56,9% toàn-cửa-sổ, r375) và âm
trên `binance XAU` (−31,9%, r372). **Route duy nhất mà guard gây hại vẫn gây hại trên dữ
liệu chưa từng dùng để tìm ra nó.**

**Trạng thái verify: không có finding P0/P1 với implementation. VERIFY chưa xong, không phải
fail** — tiêu chí đẳng thức hành vi, **đúng cái thay đổi này được nói là sống chết theo**,
**chưa được chạy trên cơ sở hợp lệ**. Task 2–5 chưa verify. **Chưa push gì.**

**Giới hạn:** **không** khẳng định hai đường cho số giống nhau — **đồng nhất về cấu trúc lời
gọi không phải đẳng thức hành vi**, và đó chính là lý do phép kiểm tra ghim tồn tại.
**Không** khẳng định `cargo test --workspace` đã pass — đó là **claim của worker**, và
`verification_mode=independent` nghĩa là nó **không được tính** cho tới khi tôi tự chạy.

**Bước tiếp theo:** chạy `one_target` **giới hạn holdout** đối chiếu figure faithful của gate
để thực hiện tiêu chí đẳng thức cho đúng, tự chạy test suite, soi task 2–5. **Chỉ sau đó**
mới FINAL_VERIFY, và **chỉ sau đó** mới push.

## Round 377 — NO-CHANGE: **ghim giá trị nghiệm thu trước khi nhìn thấy implementation**, và chứng minh phép kiểm tra đẳng thức **không thể đạt do may mắn**

`round377-NO-CHANGE-acceptance-values-pinned-before-the-implementation-is-visible-and-the-equality-check-cannot-be-passed-by-accident.md`

**Zero container.** IMPLEMENT của OPS transaction **vẫn đang chạy** (bảy file đã sửa, chưa
commit), nên vòng này làm đúng một việc hữu ích **không can thiệp vào nó và không bị nó ảnh
hưởng**.

`portfolio-measurement-integrity` sống chết theo **một** tiêu chí: sau hợp nhất, run
`--daily-profit-gate` phải tái tạo **chính xác** số liệu `one_target` ở cùng cửa sổ và cấu
hình. Phép kiểm tra đó **chỉ đáng tin nếu giá trị kỳ vọng được cố định TRƯỚC khi nhìn thấy
implementation**. Arc này đã tự ghi nhận **năm** pre-registration lỗi (r327, r330, r340,
r354, r373); ghim ngay bây giờ loại bỏ mọi khả năng hạ/chỉnh mốc theo thứ implementation
tình cờ tạo ra.

**Baseline đã ghim** (cấu hình deploy, `--days 900`, đọc từ log vòng 371–373 — có trước khi
thay đổi này tồn tại):

| route | nến | lệnh | `one_target` | `legacy` | tỉ số |
|---|---|---|---|---|---|
| `binance BTC` | 259.198 | 874 | **−4,81958** | −9,90557 | 2,06× |
| `bybit BTC` | 259.198 | 847 | **−3,76933** | −8,74651 | **2,32×** |
| `exness BTC` | 259.084 | 676 | **−4,84586** | −6,79682 | 1,40× |
| `bybit XAUT` | 145.921 | 263 | **−2,03343** | −2,49876 | 1,23× |
| `binance XAU` | 75.672 | 134 | **−1,44149** | −1,09279 | **0,76×** |

**Vì sao không thể đạt do may mắn:** gate hiện chấm cột `legacy`, sau hợp nhất phải chấm
cột `one_target`. Hai cột cách xa nhau trên mọi route **và lệch theo hai chiều ngược nhau**
— `legacy` **tệ hơn 2,32×** trên `bybit BTC` nhưng **tốt hơn** (0,76×) trên `binance XAU`.
Một implementation âm thầm giữ luồng cũ **không thể trúng đáp án do may**, và **không thể
sai theo một chiều nhất quán** có thể bị nhầm là lỗi tỉ lệ. Phép kiểm tra **cũng fail** nếu
`legacy` và `one_target` trùng nhau — nghĩa là control bị mất chứ không phải hai đường được
hợp nhất. Replay **tất định từng byte** (r351) nên **đẳng thức chính xác** là mốc đúng.

**Giới hạn:** **không** khẳng định gì về implementation — **chưa đọc diff, chưa chạy test,
chưa verify**; vòng này **cố ý không nhìn** công việc đang dở ngoài `git status` để giá trị
ghim giữ được tính độc lập. **Không** khẳng định năm route là bộ nghiệm thu đủ: `exness XAU`
**không có** baseline cấu hình-deploy @900 trong log đã giữ (run 900 ngày của nó dùng cấu
hình góc) nên **vắng mặt** khỏi phép kiểm tra và cần run riêng. **Không** khẳng định đạt
phép kiểm tra này nghĩa là thay đổi đúng — nó chỉ chứng minh **hai đường cho cùng số**;
walk-forward, metrics, audit trail và yêu cầu từ-chối-điểm là **riêng biệt và chưa verify**.

**Bước tiếp theo:** VERIFY khi IMPLEMENT xong — đọc diff, xác nhận thay đổi `finance-core`
**chỉ additive**, chạy phép kiểm tra đã ghim trên ít nhất hai route tỉ số rộng nhất
(`bybit BTC` 2,32× và `binance XAU` 0,76× — **ngược chiều nhau**), rồi các tiêu chí còn lại.
**Không commit, không push trước khi đạt.**

## Round 376 — PROMOTE: rào cản đo lường trở thành **OPS transaction**. Hai đường replay gate và Portfolio đang được hợp nhất

`round376-PROMOTE-the-measurement-blocker-becomes-an-ops-transaction-unifying-the-gate-and-portfolio-replay-paths.md`

**Promotion đầu tiên sau 171 iteration.** Zero research container — công việc vòng này là
lập kế hoạch và điều phối, không phải backtest.

**Vì sao bây giờ:** user cho phép đổi kiến trúc để gỡ rào cản, với điều kiện giữ nguyên
rules + promotion gate và **tính đúng đắn trước tiên**. Điều đó gỡ đúng thứ đã giữ r356–r375
ở research-only: **các rào cản là thật, nhưng đang bị coi như ràng buộc vĩnh viễn thay vì
defect có chủ sở hữu.**

**Defect:** hai đường replay phân kỳ, mỗi đường giữ đúng thứ đường kia thiếu.
`daily_profit_gate.rs:376-412` **không** guard, **không** risk layer, nhưng **có** giới hạn
holdout và **có** scorecard đầy đủ; `portfolio_measurement.rs:184-208` áp dụng **cả hai**
nhưng **không** holdout và chỉ **4** trường metric. Vì gate không mô hình hoá guard,
`main.rs:264` khai `conflicts_with = "daily_profit_gate"` → **không cấu hình nào có
minimum-hold từng có thể lấy điểm holdout** = điều kiện promote 1, **bất khả thi về cấu
trúc**. r371 đo độ lệch: **−9,90557** so với **−4,81958**.

**Điều kiện nghiệm thu mà thay đổi sống chết theo:** sau hợp nhất, gate và `one_target` phải
cho **trade count và PnL giống hệt nhau** ở cùng cấu hình. Replay **tất định từng byte**
(r351) → **mọi khác biệt là defect, không phải nhiễu**.

**Transaction:** `portfolio-measurement-integrity` ·
`openspec/changes/portfolio-measurement-integrity/` (validated `--strict`) ·
`.ops/changes/portfolio-measurement-integrity/` · `implementation_backend=codex`,
`verification_mode=independent` · origin gắn một lần: iteration 171, `ALL_ROUTES`, sáu
artifact repo-relative dưới `research/quant/` · repo lock: `finance-live-action`.

**Trạng thái khi đóng vòng: IMPLEMENT đang chạy.** Codex đã sửa `daily_profit_gate.rs` và
`portfolio_decision_replay.rs`, worker **vẫn đang chạy**. **VERIFY chưa bắt đầu và Claude
chưa xác minh gì** — không tóm tắt nào của Codex được tính là verification.

**Giới hạn:** **không** khẳng định implementation đúng hay đủ. **Không** khẳng định hợp nhất
hai đường sẽ **cải thiện** bất cứ kết quả nào — thay đổi này làm **phép đo** đúng, **không**
dự đoán dấu của thứ đo được và **không được đánh giá theo dấu đó**; **khả năng cao nhất là
các cấu hình có hold cuối cùng nhận được điểm gate và trượt nó.** **Không** khẳng định bốn
defect này là tất cả.

**Bước tiếp theo:** VERIFY — tự đọc diff và chạy kiểm tra đẳng thức chính xác giữa gate và
`one_target` **trước khi** commit hoặc push bất cứ thứ gì.

## Chốt hướng — rào cản đo lường đã được lập kế hoạch, không còn là ràng buộc vĩnh viễn

**2026-08-31, user cho phép đổi kiến trúc để gỡ rào cản**, với điều kiện vẫn giữ nguyên
rules và promotion gate, và **tính đúng đắn đặt lên hàng đầu**; được phép bổ sung metrics
đo lường còn thiếu.

OpenSpec change đã tạo và validate (`--strict`): **`openspec/changes/portfolio-measurement-integrity/`**

Nó nhắm đúng bốn rào cản mà r351–r375 đã lập hồ sơ:

1. **Gate chấm điểm cấu hình khác với cấu hình nó báo cáo** — `daily_profit_gate.rs:408`
   replay bằng `ledger.on_kline` (không guard, không risk layer) trong khi đường trung thành
   với Portfolio ở `portfolio_measurement.rs:184-208` áp dụng cả hai; vì thế `main.rs:264`
   khai báo `conflicts_with = "daily_profit_gate"` → **mọi cấu hình có minimum-hold vĩnh
   viễn không có điểm holdout**. r371 đo được độ lệch: −9,90557 so với −4,81958.
2. **Không kỳ OOS nào độc lập** (r352) → thêm walk-forward neo, các đoạn **rời nhau**.
3. **Không đánh giá được joint objective trên đường Portfolio** — `ExecutionFootprint` chỉ
   lộ 4 trường; PF/win rate/Sharpe/Sortino/drawdown/streak/SQN/decision rate/cost-to-gross
   chỉ tồn tại **bên trong gate**, tức đúng đường **không** mô hình hoá Portfolio.
4. **Hai loại dòng sai âm thầm** (r374, r375) → thiếu input thì **loại**, không hạ cấp;
   `trades == 0` thì `realized_pnl = 0`.

**Điều kiện nghiệm thu then chốt về tính đúng đắn:** sau khi hợp nhất, gate và `one_target`
phải cho **trade count và PnL giống hệt nhau** ở cùng cấu hình — replay là tất định (r351)
nên **mọi khác biệt đều là defect**. Test "gần đúng" chính là thứ đã cho phép hai đường
phân kỳ ngay từ đầu.

**Ràng buộc an toàn giao dịch:** không sửa `PortfolioConstructionState`,
`PortfolioRiskLayer`, hay ngữ nghĩa thực thi của `trading_modes`; chỉ thêm call site và
`Serialize`. Repo ảnh hưởng: **`finance-live-action` duy nhất**.

**Trạng thái:** PLAN xong, chờ OPS transaction để Codex implement. Các vòng sau **không cần
suy diễn lại rào cản này** — nó đã có kế hoạch.

## Round 375 — REJECTED: **số lượng Alpha input không giải thích được guard advantage**. Bản ghi fleet-complete là **5/6 route dương**, và breadth thực của sweep là **71–74, không phải 77**

`round375-REJECTED-alpha-input-count-does-not-explain-the-guard-advantage-and-the-fleet-complete-record-is-five-of-six-routes-positive.md`

**Zero container** — đọc code cộng log đã có. Thực hiện audit mà r374 đã nêu tên.

**Câu hỏi đăng ký 1 — failure mode của r374 có bị chặn không?** Audit toàn bộ 77 strategy
trên cả sáu route: **đúng năm strategy** có zero trade ở mọi split, **đúng family taker**,
**đúng bốn route không-Binance**; **không gì khác có zero trade ở bất kỳ đâu**. → **Phạm vi
r374 đã đầy đủ.** (live: 77/77/72/72/72/72)

**Rủi ro nhiễm bẩn không tồn tại.** `main.rs:629-630` dựng `candidates()` cho
`strategy_scores` và `production_candidates(&instrument)` cho Portfolio; `:573` cũng dùng
`production_candidates` cho replay — **hai đường tách rời**. **Các strategy chết không bao
giờ tới Portfolio** → **mọi phép đo Portfolio của arc không bị ảnh hưởng**. Đây là rủi ro
thật (năm tín hiệu short vĩnh viễn nuôi Portfolio trên bốn route sẽ làm nhiễm bốn mươi
vòng) và nó bị **loại trừ bằng call site**, không phải bằng giả định.

**Degeneracy thứ hai, chứng minh được từ code:** `min_strength_0_5/0_7/0_9_keltner_reversion_20_2_5`
**giống hệt nhau từng byte trên cả sáu route**, kể cả Binance → **không phải lỗ hổng dữ
liệu**. `strategies.rs:1152-1165` chỉ phát tín hiệu khi `close <= lower` hoặc
`close >= upper`, rồi đặt `strength = (|close − middle| / half_width).min(1.0)`. **Phá band
ép `|close − middle| ≥ half_width` nên `strength ≡ 1,0` với mọi tín hiệu**, và
`MinStrengthFilterStrategy` (`:3561`) chỉ loại tín hiệu **dưới** ngưỡng → với mọi ngưỡng
≤ 1,0 nó **không loại gì cả**. **Ba entry của sweep là một hành vi, theo cấu tạo.** Wrapper
**không** hỏng nói chung: trên `heikin_ashi_momentum` cùng ba ngưỡng cho ba hành vi khác
nhau (88/38/21 lệnh holdout).

**Breadth thực** (số chữ ký split phân biệt trên 77 id): **74** trên hai route Binance,
**71** trên bốn route còn lại. Phép gộp 62 family của r373 **bảo thủ hơn cả hai** → **kết
luận KHÔNG CÓ của r373 không đổi**, không kết quả nào được phục hồi.

**Câu hỏi đăng ký 2 — số Alpha input có giải thích guard advantage không?**
`production_candidates` cho Portfolio **số input phụ thuộc route**: **5 / 5 / 3 / 2 / 2 / 2**
(spread 2,5×). Route âm duy nhất là route 2-input, advantage lớn nhất ở route 5-input → đó
là **giả thuyết**, nên tôi đăng ký trên năm route đã đo và test trên **`bybit BTC`, route
chưa từng được tính advantage**: nếu đúng, nó phải nằm **dưới** +68,7 / +51,3 / +28,7%.

**Quan sát: `bybit BTC` +56,9% — trên hai trong ba. BÁC BỎ.** Hai nhóm chồng lấn nặng:
2-input trải **−31,9% → +56,9%**; 3-và-5-input trải **+28,7% → +68,7%**.

**Guard advantage fleet-complete** (deploy config, một cửa sổ mỗi route):

| route | input | advantage | % lỗ |
|---|---|---|---|
| `exness XAU` | 3 | +1,55149 | **+68,7%** |
| **`bybit BTC`** | 2 | +4,97718 | **+56,9%** |
| `binance BTC` | 5 | +5,08599 | **+51,3%** |
| **`exness BTC`** | 5 | +1,95096 | **+28,7%** |
| `bybit XAUT` | 2 | +0,46533 | **+18,6%** |
| `binance XAU` | 2 | −0,34870 | **−31,9%** |

**Năm trên sáu route dương, một âm** — phiên bản chốt của r371/r372. `exness BTC` và
`bybit BTC` đo lần đầu ở đây.

**Giới hạn:** **không** khẳng định số input là vô nghĩa — bị bác bỏ với tư cách **lời giải
thích chính**, trên sáu route, một cửa sổ, một cấu hình mỗi route; đóng góp yếu hơn **không
bị loại trừ** và thiết kế này không test nó. **Không** có cơ chế nào được đưa ra — **hai ứng
viên nay đã bị loại** (tần suất giao dịch ở r372, ρ = +0,143; số input ở vòng này).
**Không** khẳng định 5/6 dương nghĩa là guard có lợi nói chung: một cửa sổ mỗi route,
in-sample, `legacy` là **control** chứ không phải phương án triển khai, và route âm là route
ít dữ liệu nhất. **Chưa** audit các cặp wrapper/strategy khác cho lỗi saturating-strength.

**Bước tiếp theo đã nêu tên:** audit các cặp wrapper/strategy còn lại — với mỗi strategy
được bọc, kiểm tra xem điều kiện vào lệnh của nó có **ép cứng** chính metric mà wrapper lọc
theo hay không. Vòng đọc code, **zero container**.

## Round 374 — DATA-ISSUE: tín hiệu sống sót duy nhất của r373 là **bóng ma**. `taker_base_vol` **vắng mặt trên bốn trên sáu route**, và strategy **thoái hoá âm thầm thành lệnh short vĩnh viễn không bao giờ đóng**

`round374-DATA-ISSUE-round-373s-only-surviving-signal-is-a-phantom-taker-volume-is-absent-on-four-routes-and-the-strategy-degrades-into-a-permanent-short.md`

**Zero container** — giải quyết hoàn toàn bằng đọc code, log đã có, và **một** truy vấn
production read-only phạm vi hẹp. **Thu hồi headline của r373.**

**Bốn ô "dương" của `taker_imbalance` có `trades = 0` ở MỌI split.** r373 vẫn đếm
`realized_pnl` của chúng như kết quả holdout dương.

**Dữ liệu production, 30 ngày nến 5m:** `taker_base_vol` phủ **100,00%** trên **cả hai**
route Binance và **0,00%** trên **cả bốn** route bybit/exness, trong khi `volume` được
populate ở khắp nơi.

**Cơ chế** (`strategies.rs:246-256`): `buy_ratio = taker_buy_volume / volume` **đồng nhất
bằng 0** trên bốn route đó, mà `0 ≤ 1 − threshold` đúng với **mọi** threshold ≥ 0,5 → phát
**EnterShort trên mọi bar, mãi mãi, giống hệt nhau cho cả ba threshold**; biến thể fade
phản chiếu thành EnterLong. **Side không bao giờ đổi nên không gì được đóng**: `trade_count`
đứng ở 0 trong khi một vị thế mở tích luỹ funding suốt kỳ. Xác minh trên **cả 12** ô
zero-trade: `realized_pnl == −funding_paid` **chính xác**, tỉ lệ theo split
**0,8100 / 0,2700 / 0,2700 = 3 : 1 : 1** = đúng split 60/20/20.

**→ "PnL holdout dương" là funding nhận được trên một lệnh short bóng ma.**

**r373 tính lại với yêu cầu `trades > 0`:**

| | r373 | đã sửa |
|---|---|---|
| ô holdout dương | 39/462 | **27/462** |
| family ở ≥ 4/6 route | 6 | 5 |
| **dương trên cả hai instrument** | **`taker_imbalance`** | **KHÔNG CÓ** |

**Đáp án đúng cho test bảo thủ của r373 là KHÔNG CÓ**, và p = 0,0115 của nó **không mô tả
gì cả**.

**Codebase đã có sẵn gate đúng và tôi đã đi vòng qua nó.** `sweep.rs:43-46`
`survives_selection()` **đã** yêu cầu `trades > 0 && realized_pnl > 0` trên train **và**
validation, kèm doc comment *"Holdout is deliberately not consulted here"* — **đúng cả hai
lỗi r373 mắc phải**. Tôi tự viết tay phần chọn lọc trên mảng `strategy_scores` thô và
**không tái tạo gate nào**. Đây là ghi nhận tôi thấy khó chịu nhất và cũng hữu ích nhất.

**Defect cụ thể — không áp dụng, chỉ điều tra.** (1) **Thoái hoá âm thầm**: strategy thiếu
input bắt buộc phải bị **loại**, không phải biến thành tín hiệu một-chiều cố định. (2)
**Dòng zero-trade mang `realized_pnl` khác 0** với `win_rate`/`profit_factor` null — mời gọi
đúng lỗi r373. **Không có phơi nhiễm production**: `taker_imbalance` **không** có trong
`production_candidates` (`strategies.rs:24-78`) lẫn `deployment_rules.rs` → **defect đo
lường của research sweep, không phải vấn đề trading-safety.**

**Giới hạn:** **không** khẳng định 27 ô còn lại có ý nghĩa — chúng vẫn được **chọn trên
chính holdout dùng để chấm** (blocker r373, không đổi), và **không family nào sống sót test
bảo thủ**. **Vòng này gỡ một dương-giả, không tạo ra một dương-thật.** **Không** khẳng định
bybit/exness *có thể* cung cấp taker volume — truy vấn đo cái **đang lưu**, không đo cái
venue **có phát**. **Chưa** audit 72 strategy còn lại cho cùng kiểu thoái hoá.

**Bước tiếp theo đã nêu tên:** audit toàn bộ strategy còn lại theo cùng failure mode — đếm
strategy có `trades == 0` ở mọi split trên từng route rồi đối chiếu input trong
`public.klines`. Vòng log-và-query như vòng này, **zero container**, và nó chặn được **bao
nhiêu phần của sweep 77 strategy thực sự sống trên mỗi route**.

## Round 373 — NEEDS-MORE-RESEARCH: **lớp Alpha đã sẵn có cấu trúc holdout mà lớp Portfolio không thể cung cấp**. Một tín hiệu cross-route trông áp đảo **co lại còn đúng một family biên**

`round373-NEEDS-MORE-RESEARCH-the-alpha-layer-has-the-holdout-structure-the-portfolio-lacks-and-an-overwhelming-cross-route-signal-collapses-to-one-marginal-family.md`

**Vòng đầu tiên của arc chạm tới lớp Alpha.** Hai container hoàn tất fleet; bốn route còn
lại đọc từ log đã có.

**Phát hiện khiến vòng này rẻ:** mọi run đều đã chứa `strategy_scores` — **77 strategy ×
ba split (`train`/`validation`/`holdout`)** kèm `realized_pnl`, `trades`, `profit_factor`,
`win_rate`, `max_drawdown`, `funding_paid`, **ở đúng chi phí deploy**. Đã xác minh
**sha256 giống hệt** giữa cấu hình góc và cấu hình deploy trên cùng route/cửa sổ → **Alpha
độc lập với band/hold của Portfolio**, và **mọi log cũ đều đã mang nó**. Split là 20% đuôi
sạch: `binance BTC` @900 = 155.519 + 51.840 + **51.839** = 259.198 = `candle_count`,
holdout **180,0 ngày lịch**. → **Lớp Alpha có đúng cấu trúc OOS mà lớp Portfolio không thể
có (r356), và nó nằm sẵn trong mọi run arc từng chạy.**

| route | nến | dương/77 | holdout tốt nhất |
|---|---|---|---|
| `binance BTC` | 259.198 | 5 | +1,4373 |
| `exness BTC` | 259.084 | 9 | +1,8836 |
| `bybit BTC` | 259.198 | 6 | +1,3527 |
| `binance XAU` | 75.672 | 3 | +0,4690 |
| `bybit XAUT` | 145.921 | 9 | +0,6074 |
| `exness XAU` | 174.251 | 7 | +1,5199 |

**39/462 ô dương (8,4%).**

**Tiêu chí đăng ký của tôi gần như vô hiệu — khiếm khuyết thứ năm** (r327, r330, r340,
r354, r373). Tôi đăng ký "có strategy nào dương ở ≥ 2 trên sáu route?" — **dưới ngẫu nhiên
thuần với đúng các số đếm đó, P = 0,9999**. Nó gần như **không thể sai**. Ghi trước khi
báo kết quả, không phải sau.

**Thống kê phân biệt được:** số strategy đạt ≥ 4/6 — quan sát **6**, null mean 0,045,
**P < 1e−5**. Nhưng **null đó sai theo hướng thổi phồng**: r276 đo ba route BTC có
volatility **giống nhau tới ba chữ số**; r342 đo hai route vàng tương quan **0,996** về
giá. Ba route BTC và ba route vàng gần với **hai** đơn vị độc lập hơn.

**Test bảo thủ** (gộp 77 id thành **62 mechanism family**, yêu cầu ≥ 2/3 route của mỗi
instrument): BTC được `atr_breakout`, `orb_london`, `taker_imbalance`; vàng được
`bk_squeeze`, `heikin_ashi_mom`, `sma10_fib`, `taker_imbalance`. **Dương trên CẢ HAI
instrument: đúng một family — `taker_imbalance`, P = 0,0115.**

Mọi hit khác là **hiệu ứng của một instrument tràn sang đúng một route của instrument kia**
(`atr_breakout` = cả ba BTC + `exness XAU`; `sma10_fib` = cả ba vàng + `binance BTC`;
`bk_squeeze` = cả ba vàng + `exness BTC`). Đó **vừa là dáng của hiệu ứng thật một-instrument,
vừa là dáng của dữ liệu gần trùng lặp** — phép đo này **không phân biệt được**.

**Người sống sót duy nhất có degeneracy:** `taker_imbalance` có **năm** biến thể, cho **năm
chữ ký split khác nhau trên cả hai route Binance nhưng chỉ hai trên bốn route còn lại** —
threshold **vô hiệu trên 4/6 route**, phụ thuộc route, khác với `--interval` vô hiệu phổ
quát của r351.

**Rào cản đi theo sang lớp Alpha:** sáu strategy này được **chọn bằng cách nhìn vào holdout**
→ holdout bị **tiêu thụ** làm tập chọn. Và **không có holdout mới**: holdout là 20% đuôi
nên **mọi giá trị `--days` đều cho holdout lồng trong hoặc chứa cái này** — blocker r352 nay
**áp dụng cả cho lớp Alpha**. Cả sáu route đã tiêu thụ hết.

**Giới hạn:** **không** khẳng định strategy nào có edge — p = 0,0115 trên một family, sau
khi thu gọn một hiệu ứng lớn hơn nhiều, là **giả thuyết**. **Không** khẳng định 0,0115 là
p-value đúng: nó giả định family khả hoán và hai instrument là hai đơn vị độc lập, **cả hai
đều xấp xỉ**. **Không** khẳng định các holdout PnL này sống sót qua construction guard và
risk layer — đó là số của **Alpha ledger**, không chạy qua `one_target`.

**Bước tiếp theo đã nêu tên:** **dữ liệu chưa thấy duy nhất là thời gian phía trước** —
chạy lại đúng scan sáu route sau khi 20% đuôi chứa bar mà không strategy nào được chọn
trên đó. **Không xác nhận được hôm nay.**

## Round 372 — REJECTED: **guard advantage cũng không tổng quát**. Trên `binance XAU`, guard + risk layer **tệ hơn 31,9%** so với luồng không guard

`round372-REJECTED-the-guard-advantage-is-not-general-either-binance-xau-is-31-9-percent-worse-with-the-guard-than-without-it.md`

**Tiêu chí đăng ký trước đã bắn ngược lại giả thuyết.** Đăng ký: **cả hai** route XAU còn
lại dương → hiệu ứng Portfolio-layer tổng quát đầu tiên của arc; **bất kỳ** cái nào ≤ 0 →
nó nhập hội với mọi kết quả route-local khác.

**Quan sát: `bybit XAUT` +0,46533 (dương), `binance XAU` −0,34870 (ÂM).** Claim "hiệu ứng
tổng quát đầu tiên" của r371 bị **thu hồi**.

| đo | lệnh/tuần | `legacy` | advantage | % lỗ |
|---|---|---|---|---|
| **`binance XAU` @900 deploy** | 1,04 | −1,09279 | **−0,34870** | **−31,9%** |
| `exness XAU` @900 góc | 1,27 | −2,25984 | +1,55149 | +68,7% |
| `exness XAU` @500 góc | 1,93 | −1,44608 | +2,24338 | +155,1% |
| `bybit XAUT` @900 deploy | 2,05 | −2,49876 | +0,46533 | +18,6% |
| `binance BTC` @900 góc | 2,45 | −4,81544 | +1,86003 | +38,6% |
| `binance BTC` @900 deploy | 6,80 | −9,90557 | +5,08599 | +51,3% |

**Năm trên sáu dương, ba trên bốn route dương, một route âm.** Vẫn là **thành tích tái lập
tốt nhất** mà bất cứ thứ gì trong arc đạt được — nhưng **không phải thứ đã đăng ký**.
Chuẩn hoá, biên độ trải **−31,9% đến +155,1%**: r371 đã cảnh báo "dấu tái lập, độ lớn thì
không"; nay **dấu cũng không tái lập hoàn toàn**.

**Ghi chú validity khiến bài test này rẻ:** advantage tính **bên trong mỗi run**
(`one_target` so với `legacy_selected_rule` trên **cùng** luồng quyết định), nên khác với
mọi so sánh cross-configuration của arc, **cửa sổ các route không cần khớp nhau**.

**Route thất bại không thể cho thêm dữ liệu:** `binance XAU` @900 trả về **75.672 nến =
262,8 bar-days** — **toàn bộ lịch sử khả dụng** (r208: venue horizon, không phải backfill
gap). Kết quả âm **không giải quyết được bằng cửa sổ sâu hơn**. Đây cũng là evidence mỏng
nhất bảng (134 lệnh, route ít hoạt động nhất). **Ghi nhận như giới hạn, không phải lý do
để gạt bỏ một tiêu chí đã đăng ký và đã bắn.**

**Một cơ chế tôi tự đề xuất và chính dữ liệu của tôi bác bỏ:** giả thuyết "guard chặn
whipsaw nên trên route ít giao dịch nó chỉ loại mất lệnh có thể thắng" dự đoán advantage
**tăng theo tần suất**. Xếp theo tần suất, advantage chuẩn hoá chạy **−31,9 / +68,7 /
+155,1 / +18,6 / +38,6 / +51,3**; **Spearman ρ = +0,143**. Giữa bảng lộn xộn, tương quan
không đáng kể → **cơ chế bị bác bỏ**, ghi lại thay vì để nó tồn tại như lời giải thích
nghe hợp lý. (ρ **chỉ mô tả** — sáu điểm và **không độc lập**.)

**Giới hạn:** **không** khẳng định guard gây hại trên `binance XAU` nói chung (một cửa sổ
= toàn bộ lịch sử route đó, một cấu hình, 134 lệnh) — cái đổ là claim **tổng quát**.
**Không** khẳng định guard vô dụng: nó dương trên **ba trên bốn route** và trên **hai route
mang nhiều lệnh nhất**. `bybit BTC` và `exness BTC` **chưa test**.

**Trạng thái arc:** **mọi hiệu ứng đo được ở Portfolio layer nay đều route-local**, kể cả
thứ vừa trông có vẻ tổng quát. Rào cản cấu trúc không đổi (r356, r352); phân tách
guard-vs-risk-layer vẫn **cần thay đổi code**, không chạy được.

## Round 371 — NEEDS-MORE-RESEARCH: **construction guard + risk layer** là **hiệu ứng đầu tiên của arc dương trên cả hai route ở cả hai độ sâu cửa sổ**. Riêng biệt: Target 3 của `binance BTC` **trượt ở 900 ngày**

`round371-NEEDS-MORE-RESEARCH-the-construction-guard-is-the-arcs-first-cross-route-cross-window-stable-effect-and-binance-btcs-target-3-pass-fails-at-900-days.md`

**Hai đăng ký trước, trả lời ngược chiều nhau.** Cả hai arm `candle_count` 259.198 (cùng cửa sổ).

**Phần 1 — dấu của góc trên `binance BTC` @900 = −2,95541, ÂM.** Góc là artifact cửa sổ
gần đây **trên cả hai route**; câu hỏi r370 để mở nay **đóng**.

**Phần 2 — advantage so với control `legacy` = +1,86003, DƯƠNG.** Và đây mới là nửa đáng quan tâm.

| route | cửa sổ | cấu hình | `one_target` | `legacy` | advantage | cắt lỗ |
|---|---|---|---|---|---|---|
| exness XAU | 500 | góc | +0,79730 | −1,44608 | **+2,24338** | đảo dấu |
| exness XAU | 900 | góc | −0,70835 | −2,25984 | **+1,55149** | **68,7%** |
| binance BTC | 900 | góc | −2,95541 | −4,81544 | **+1,86003** | **38,6%** |
| binance BTC | 900 | **deploy** | −4,81958 | −9,90557 | **+5,08599** | **51,3%** |

**Bốn đo, hai route, hai độ sâu, tất cả dương.** Chưa gì khác trong arc làm được điều đó —
mọi gradient band, quy tắc per-trade, mẫu hình theo thứ, hố lõm và góc có lãi đều trượt
một trong hai bài test.

**Advantage lớn nhất thuộc về cấu hình ĐANG DEPLOY, không phải góc** → hiệu ứng là **chính
bộ máy** (`PortfolioConstructionState::construct` + `PortfolioRiskLayer`), không phải tham
số tìm được. Và đó **đúng thứ mà `--daily-profit-gate` bỏ qua** (r356) — hệ quả nay được
**định lượng**: gate chấm luồng lỗ −9,90557 trong khi thứ thực chạy lỗ −4,81958 →
**verdict gate hạ thấp cấu hình deploy khoảng 2×, theo hướng bi quan.**

**Target 3 của `binance BTC` phụ thuộc cửa sổ**: cùng tham số deploy, **9,65/tuần @500
(r367) → 6,80/tuần @900** — dịch −29,5% và **vượt qua mốc**. Route này là perpetual 24/7,
259.198 nến đúng bằng 900,0 ngày nên mẫu số lịch và nến trùng nhau — **không vướng caveat
phủ lịch của r370**. r286 từng gọi hai pass là "window-robust" và tự viết điều kiện dừng:
*"rơi xuống dưới 7 nghĩa là không verdict một-cửa-sổ nào đáng tin"* — **điều kiện đó nay
đã xảy ra**. Banner đã thêm vào `round286-…md` và `round370-…md`.

**Giới hạn:** **không** khẳng định advantage ổn định về **độ lớn** (38,6%–68,7%; bốn điểm
không phải một phân phối) — **dấu** mới là thứ tái lập. **Không** khẳng định verdict gate
sai 2× nói chung: một route, một cửa sổ, đo **một lần**. **Không** promotable: hiệu ứng là
"lỗ ít hơn một nửa", **không phải** "có lãi". `legacy` là **control**, không phải lựa chọn
triển khai được.

**Bước tiếp theo đã nêu tên:** tách **guard so với risk layer** — cái nào mang 38,6–68,7%.
**Không chạm được bằng flag hiện có**, nên đây là **câu hỏi cần thay đổi code**, xếp cùng
r356 và audit L4, không phải một vòng chạy được.

## Round 370 — REJECTED: **cấu hình có lãi duy nhất của toàn arc đảo dấu ở 900 ngày**. Góc đó là thuộc tính của **cửa sổ gần đây**, không phải của cấu hình

`round370-REJECTED-the-arcs-only-profitable-configuration-flips-sign-at-900-days-so-the-corner-is-a-recent-window-property-not-a-configuration-property.md`

**Tiêu chí đăng ký trước đã bắn ngược lại chính kết quả dương mạnh nhất của arc.**
Góc (band 0,02/0,04, `minimum_hold_decisions` 288) là **cấu hình duy nhất trong 60+ vòng
có PnL dương ở chi phí deploy** (+1,17395 @300 — r365; chuyển được sang `binance BTC`
@500 ở +0,37527 — r366) và **chưa bao giờ được test trên cửa sổ mà nó không được chọn ra**.

Đăng ký: dương ở **cả** 500 và 900 → bền theo cửa sổ; âm ở **bất kỳ** cái nào → artifact.

| cửa sổ | nến | bar-days | phủ | lệnh/tuần (lịch) | `one_target` PnL | control `legacy` |
|---|---|---|---|---|---|---|
| 300 (r365) | 57.934 | 201,2 | 67,1% | 1,94 | **+1,17395** | — |
| **500** | 96.686 | 335,7 | 67,1% | 1,93 | **+0,79730** | −1,44608 |
| **900** | 174.251 | 605,0 | 67,2% | 1,27 | **−0,70835** | −2,25984 |

**Dấu sống qua 300 → 500 và chết ở 900.** Nhất quán với r241 ("gross edge của Portfolio
là thuộc tính cửa sổ gần đây") và r244 — nay áp dụng cho đúng cấu hình từng thoát khỏi
kết luận đó.

**Sắc thái trung thực — bền *tương đối*, không bền *tuyệt đối*:** so với control
`legacy_selected_rule` (không guard, không risk layer), góc **tốt hơn ở mọi cửa sổ**, kể
cả cửa sổ nó lỗ (+2,24338 @500; +1,55149 @900). Cấu hình **có làm gì đó thật**. Cái không
sống sót là thứ duy nhất khiến nó đáng quan tâm: **vượt qua mốc 0**.

**Vấn đề định nghĩa lộ ra:** gold CFD của `exness` chỉ phủ **67,1% thời gian lịch** ở cả
ba cửa sổ (lịch giao dịch — r337, không phải lỗi dữ liệu). Quy ước lệnh/tuần của arc chia
theo **tuần lịch** → trên route này **thấp hơn 1,49×** so với thời gian theo nến (1,94 so
với 2,89 @300). **Không đổi verdict nào trong vòng này**, nhưng việc `exness XAU` có vượt
mốc 7/tuần hay không **phụ thuộc một định nghĩa chưa ai chốt** — hệ số 1,49× trên chính
route mà Target 3 mơ hồ nhất (r285/r286/r304). **Ghi nhận như câu hỏi định nghĩa đang mở,
không phải chấm điểm lại kết quả cũ.**

**Giới hạn:** **không** tính đóng góp của đoạn cũ — cửa sổ lồng nhau (r352) và r300 đã
chứng minh **nested differencing không hợp lệ với counter của Portfolio**; không con số
nào như vậy xuất hiện. **Không** khẳng định góc cũng hỏng trên `binance BTC` (chưa test ở
cửa sổ khác; r369 cho thấy hai route bất đồng về cấu trúc trục band). Không có cơ chế.
Banner đã thêm vào `round365-…md` và `round366-…md`.

**Trạng thái arc:** mọi kết quả Portfolio-layer dương đến nay **hoặc** không khái quát hoá
được qua route (r364/r367/r369) **hoặc** không giữ được dấu qua cửa sổ (vòng này). Hai rào
cản cấu trúc không đổi: cấu hình có hold **không có điểm gate** (r356 → điều kiện 1) và
mọi holdout đều **lồng nhau** (r352).

## Round 369 — REJECTED: **bất đối xứng band đảo chiều giữa các route**. Siết band **rẻ hơn 52 lần** trên `exness XAU` và **đắt hơn 1,9 lần** trên `binance BTC`

`round369-REJECTED-the-band-asymmetry-inverts-between-routes-tightening-is-52x-cheaper-on-exness-xau-and-1-9x-more-expensive-on-binance-btc.md`

**Tiêu chí đăng ký trước đã bắn ngược lại giả thuyết.** Ngưỡng được tính từ dữ liệu
r367 **trước khi chạy**: cost ratio `|ΔPnL%| / |Δtần suất%|` của hướng **nới** trên
`binance BTC` là **0,561**. Đăng ký: siết `< 0,561` → tái lập; `≥ 0,561` → đặc thù route.

**Quan sát: 1,052 → không tái lập.** Trên `binance BTC` siết band tốn **+19,16% tần
suất đổi lấy −20,15% PnL** — gần một-đổi-một, và **đắt gần gấp đôi hướng nới**, đúng
thứ tự **ngược lại** với `exness XAU`.

| route | siết | nới | hướng rẻ |
|---|---|---|---|
| `exness XAU` (r368) | 0,046 | 2,385 | **siết, rẻ hơn 52×** |
| `binance BTC` (r369) | **1,052** | **0,561** | **nới, rẻ hơn 1,9×** |

**Gradient PnL/lệnh cũng đảo dấu**: `binance BTC` tốt nhất ở **band hẹp nhất**
(−0,006630), `exness XAU` tốt nhất ở **band rộng nhất** (−0,002181). Cả hai đường cong
đều không đơn điệu và **hai đầu "tốt" nằm ngược nhau**.

**Khái quát hoá thứ ba về band sụp trong ba vòng**: r364 phản bác "PnL/lệnh là hằng số",
r367 phản bác "rộng hơn thì tốt hơn mỗi lệnh", r369 phản bác "siết là hướng rẻ".
**Chưa có hiệu ứng Portfolio-layer nào trong arc giữ được dấu qua các route.**

Tần suất **có sẵn** trên route này và chỉ đơn giản là **đắt**: band hẹp nhất đạt
**14,55 lệnh/tuần — hơn gấp đôi mốc Target 3 — tại −6,88814, PnL tệ nhất toàn lưới.**
Tám ô đều `candle_count` 143.998 (cùng cửa sổ).

**Giới hạn:** mỗi route một cửa sổ, `one_target` toàn-cửa-sổ → **in-sample**. **Không**
khẳng định "route" là biến giải thích — venue, instrument, market type và lịch giao dịch
khác nhau cùng lúc; chỉ chứng minh hiệu ứng **không khái quát hoá được**. Không có cơ chế.
Banner đã thêm vào `round368-…md`.

**Ghi chú quy trình:** lần đánh giá đầu dùng **baseline gán nhãn sai** (log 0,02/0,04 cũ
bị đọc như ô đang deploy) cho ra 0,632 — **cùng kết luận nhưng nhờ may mắn**; đã bắt được
trước khi ghi bất cứ artifact nào. Log cũ phải nhận diện **bằng tham số nó báo cáo**,
không bằng tên file vòng trước đặt.

## Round 368 — NEEDS-MORE-RESEARCH: `exness XAU` **có** đạt Target 3 khi siết band — nhưng chỉ khi lỗ. **Đường cong band bất đối xứng mạnh quanh điểm đang deploy**: siết band cho **+29,6% tần suất với thay đổi PnL chỉ 1,36%**

`round368-NEEDS-MORE-RESEARCH-exness-xau-does-reach-target-3-once-the-band-is-tightened-but-only-at-a-loss-and-the-band-curve-is-sharply-asymmetric-around-the-deployed-point.md`

**Đăng ký trước — trả lời CÓ.** r368 sửa một tiền đề của r367: r367 gọi `binance BTC`
là *"route có điều kiện tốt nhất để phá vỡ"* vì *"route duy nhất từng vượt 7 lệnh/tuần"* —
điều đó đúng với **các thiết lập đã test**, không đúng với route. `exness XAU` chưa bao
giờ chạy band hẹp hơn 0,01/0,02 đang deploy. Ở band **0,005/0,01** hold 36 nó đạt
**10,43 lệnh/tuần**; ở **0,0075/0,015** đạt **8,17**. **Cả hai đều lỗ** (−2,71794 và −1,59396).

**Kết luận của r367 không bị ảnh hưởng và nay được củng cố trên route thứ hai.**
Break-even trên `exness XAU` bị chặn trong **(1,94; 3,83) lệnh/tuần → nhiều nhất 3,83,
thấp hơn mốc 45,3%** — khoảng cách còn **rộng hơn** mức 5,24 (25%) của `binance BTC`.

**Phát hiện đáng mang tiếp — bất đối xứng:** siết 0,01/0,02 → 0,0075/0,015 cho
**+29,6% lệnh/tuần** (6,30 → 8,17) với **thay đổi tổng PnL 1,36%** (−1,57256 → −1,59396);
nới 0,01/0,02 → 0,02/0,04 cho −31,1% tần suất đổi lấy +74,2% PnL. Chênh lệch 0,02140
tương đương **4,7 lệnh** theo PnL/lệnh của chính ô đó trên 350 lệnh, và **PnL/lệnh còn
tốt hơn 21,8%**. Đây là **ô đầu tiên trong toàn bộ arc mà tần suất tăng đáng kể còn PnL
không dịch chuyển đáng kể** — đúng hình dạng mà 60+ vòng tìm kiếm. **Không phải candidate:
ô đó vẫn lỗ**, nên không có gì để promote.

`PnL/lệnh` **không đơn điệu theo band** (−0,006080 / −0,004554 / −0,005824 / −0,002181
cho 0,005 / 0,0075 / 0,01 / 0,02) → phản bác "rộng hơn thì tốt hơn mỗi lệnh" của r367
vẫn đứng nhưng **còn nhẹ hơn thực tế**.

**Giới hạn:** một ô, một route, một cửa sổ, `one_target` toàn-cửa-sổ → **in-sample**;
"không phân biệt được" là **lập luận về độ lớn, không phải kiểm định ý nghĩa**. Không
khẳng định break-even là hằng số route. Banner sửa đã thêm vào `round367-…md`.

**Bước tiếp theo đã nêu tên:** chạy **hướng siết band trên `binance BTC`** — chưa test ở
đó, và route đó **ngược dấu** với `exness XAU` ở hướng nới.

## Round 367 — REJECTED: trên route **có điều kiện tốt nhất để phá vỡ nó**, **không thiết lập (band, hold) nào vừa có lãi vừa đạt Target 3**. Hai ô vượt mốc 7,0/tuần lỗ **−4,75** và **−2,75**; ô duy nhất có lãi giao dịch **2,80/tuần**. **Tần suất hoà vốn cao nhất là 5,24/tuần — thấp hơn mốc 25%**

**Câu hỏi Round 366 buộc phải hỏi.** r366 tìm được sáu cấu hình có lãi và sáu lần trượt Target 3; quy tắc trong skill trở thành: *trước khi tốn thêm một vòng cho knob tầng Portfolio, hãy kiểm xem nó có thể tăng PnL mà KHÔNG cắt tần suất hay không*. `binance BTC` là route **có điều kiện tốt nhất**: **route duy nhất trong arc từng vượt 7,0/tuần** (9,65 ở deployed), và r366 cho thấy góc kéo nó thành dương ở 2,80/tuần — nên **biên giới giữa hai điểm đó** là nơi có câu trả lời.

**Đăng ký trước phân hoạch**: có cấu hình nào trên `binance BTC` @500 **vừa** PnL dương **vừa** ≥ 7,0 lệnh/tuần không? **Có** → phá vỡ tính không-tương-thích; **Không** → nó đứng vững trên route thuận lợi nhất.

**Kết quả — KHÔNG.** Cả sáu ô ở `candle_count` **143.998**:

| band | hold | lệnh | **lệnh/tuần** | `one_target` PnL | PnL/lệnh |
|---|---|---|---|---|---|
| 0,01/0,02 | 36 (deployed) | 689 | **9,65** ✓ | −4,74869 | −0,006892 |
| 0,01/0,02 | 72 | 517 | **7,24** ✓ | −2,74744 | −0,005314 |
| **0,02/0,04** | **36** | 481 | 6,73 | **−3,94375** | **−0,008199** |
| **0,02/0,04** | **72** | 374 | 5,24 | **−1,95771** | −0,005235 |
| 0,01/0,02 | 144 | 368 | 5,15 | −2,65041 | −0,007202 |
| 0,02/0,04 | 288 | 200 | 2,80 | **+0,37527** | +0,001876 |

**Hai ô vượt mốc, cả hai lỗ nặng. Một ô có lãi, nó chạy 2,80 lệnh/tuần.**

**Dạng sắc hơn — điểm hoà vốn nằm ở đâu**: ô âm tốt nhất là **−1,95771 tại 5,24/tuần**; ô dương duy nhất **+0,37527 tại 2,80/tuần** → **điểm cắt 0 nằm trong (2,80; 5,24) lệnh/tuần — nhiều nhất là 5,24, tức thấp hơn mốc 7,0 tới 25%.** Mạnh hơn hẳn bảng thống kê của r366: **không phải chỉ là "các cấu hình có lãi tìm được đều chậm"**, mà **trên route này chính tần suất hoà vốn đã nằm dưới mục tiêu** — nên không thiết lập nào trên biên giới này thoả mãn được cả hai.

**Một đảo chiều đặc thù route đáng ghi**: nới band ở hold 36 làm `binance BTC` **tệ hơn mỗi lệnh** (−0,006892 → **−0,008199**, −19,0%), trong khi **đúng thay đổi đó trên `exness XAU`** (r364) **cải thiện +62,5%**. → **Hiệu ứng per-trade của band không phổ quát về dấu.** r364 bác bỏ quy tắc "per-trade hằng số"; vòng này bác bỏ **cái thay thế hấp dẫn** ("rộng hơn thì tốt hơn mỗi lệnh"). **Không khái quát hoá nào sống sót.** Biên giới cũng **không đơn điệu theo tần suất** (6,73 tệ hơn 7,24; 5,15 tệ hơn 5,24).

**Giới hạn**: **không** khẳng định **không thiết lập nào ở bất cứ đâu** thoả mãn cả hai — **sáu ô, một route, một cửa sổ**, toàn-cửa-sổ `one_target`; còn vùng chưa lấy mẫu (hold giữa 72–288, band giữa 0,02–0,04, và mọi tổ hợp trên năm route còn lại). **Không** khẳng định tần suất hoà vốn là hằng số của route — chỉ chặn được **trên cửa sổ này**, mà r331/r334/r341 đều cho thấy các ranh giới như vậy **dịch theo cửa sổ**. **Không** khẳng định tính không đơn điệu là cấu trúc — replay tất định (r351) nên đây là **độ nhạy đầu vào**, không phải nhiễu, và **không có cơ chế nào được đưa ra**. Hành vi holdout không đổi: cấu hình có hold **không có điểm gate**, **điều kiện 1 vẫn bất khả thi**. **Không promote.**

Chi tiết: `research/quant/rounds/round367-REJECTED-no-band-hold-setting-is-both-profitable-and-at-target-3-the-break-even-frequency-is-25-percent-below-the-bar.md`.

## Round 366 — NEEDS-MORE-RESEARCH: góc có lãi **chuyển giao được** — áp lên `binance BTC`, route **chưa từng dùng để chọn nó**, cho **+0,37527**. Và mẫu hình toàn arc đã rõ: **mọi cấu hình có lãi từng đo được đều trượt Target 3**, cái tốt nhất chỉ **4,57 lệnh/tuần** so với mốc 7,0

**Phép test r365 yêu cầu.** r365 nêu rõ điều gì sẽ làm kết quả của nó có sức nặng: *"cùng góc đó sống sót trên route hoặc cửa sổ mà nó không được chọn từ đó"*. Góc — **band 0,02/0,04 với hold 288** — sinh ra **chỉ từ `exness XAU`**, nên áp nguyên trạng lên hai route khác là **test thật sự mới**.

**Đăng ký trước phân hoạch**: góc làm PnL **dương ở ít nhất một** trong `bybit XAUT` và `binance BTC` @500 → hướng sống sót; **âm ở cả hai** → không chuyển giao, nhất quán với overfitting. **Validity**: cả bốn run `candle_count` **143.998**.

| route | config | lệnh | /tuần | `one_target` PnL | PnL/lệnh |
|---|---|---|---|---|---|
| `bybit XAUT` @500 | deployed | 247 | 3,46 | −1,57738 | −0,006386 |
| `bybit XAUT` @500 | **góc** | 108 | 1,51 | **−0,28493** | −0,002638 |
| `binance BTC` @500 | deployed | 689 | 9,65 | −4,74869 | −0,006892 |
| `binance BTC` @500 | **góc** | 200 | **2,80** | **+0,37527** | **+0,001876** |

**`binance BTC` chuyển dương → nhánh đã đăng ký xảy ra.** Và góc **cải thiện cả ba route**: `exness XAU` **+174,7%**, `bybit XAUT` +81,9%, `binance BTC` **+107,9%**. Đây là **bằng chứng thật** chống lại cách đọc "chỉ là artifact cửa sổ của `exness XAU`".

**Nhưng hãy nhìn cái nó làm với `binance BTC`**: đó là **route DUY NHẤT trong cả arc vượt mốc tần suất** (9,65/tuần), và góc kéo nó xuống **2,80** — **nó mua lợi nhuận bằng cách phá đúng thứ route đó đang có**.

**Mẫu hình quyết định cả arc** — mọi cấu hình có lãi từng đo được, kèm tần suất:

| cấu hình | lệnh/tuần | PnL | Target 3 |
|---|---|---|---|
| `exness XAU` @300 góc (r365) | **1,94** | +1,17395 | TRƯỢT |
| `exness XAU` @300 `protective: none` (r346) | **1,44** | +0,40691 | TRƯỢT |
| `binance BTC` @500 góc (vòng này) | **2,80** | +0,37527 | TRƯỢT |
| `exness XAU` @1500 deployed, gate holdout (r352) | **2,81** | +0,22720 | TRƯỢT |
| `exness XAU` @300 `--fee-bps 3.0` (r345, phản-thực-tế) | 4,57 | +0,14423 | TRƯỢT |
| `exness XAU` @300 `--slippage-bps 0` (r344, phản-thực-tế) | 4,57 | +0,13146 | TRƯỢT |

**Sáu cấu hình có lãi, sáu lần trượt Target 3.** Tần suất cao nhất trong nhóm là **4,57/tuần** so với mốc **7,0**, và **hai cái lãi nhất giao dịch dưới 2 lệnh/tuần**.

Đây **không còn là trùng hợp** giữa các lever — **đó là hình dạng của kết quả: ở mức chất lượng quyết định hiện tại của Portfolio, lợi nhuận và mục tiêu tần suất là không tương thích ở mọi nơi arc đã tìm.** Mọi lever cải thiện PnL đều làm vậy **bằng cách giao dịch ít đi**, và vùng có lãi **luôn** nằm dưới mốc.

Đó là phát biểu về **luồng quyết định**, không phải về tham số nào: **quyết định không đủ tốt để chịu được việc bị lấy thường xuyên**. Cải thiện chúng là **bài toán tầng Alpha**, không phải Portfolio-construction — và **không knob nào của tầng Portfolio trong 60+ vòng dịch được nó**.

**Giới hạn**: **không** khẳng định góc không bị overfit — nó qua **một** test dương trên **hai**, và **không phải holdout** (thứ promotion gate đòi và không thể tạo ra cho cấu hình có hold). **Không** khẳng định `one_target` dương của `binance BTC` mâu thuẫn với gross âm ở r342 — con số đó là đo **trên gate**, **band deployed**, luồng **guard-free**; góc là cấu hình khác và **không có phép đo gross cho nó**. **Không** khẳng định tính không-tương-thích là **quy luật** — sáu cấu hình, bốn lever, ba route, đều toàn-cửa-sổ hoặc holdout lồng nhau: **mẫu hình mạnh, không phải chứng minh**, và **không có cơ chế nào được đưa ra**. **Không** khẳng định tầng Alpha là lời giải — đó là nơi lập luận **chỉ tới**, không có gì ở đây test nó. **Không promote.**

Chi tiết: `research/quant/rounds/round366-NEEDS-MORE-RESEARCH-the-profitable-corner-transfers-to-binance-btc-and-every-profitable-configuration-ever-found-fails-target-3.md`.

## Round 365 — NEEDS-MORE-RESEARCH: band và hold là **hai lever khác nhau và cộng hưởng siêu-cộng-tính**. Kết hợp — band 0,02/0,04 với hold 288 — `exness XAU` **dương: +1,17395** ở chi phí deployed, lần đầu tiên trong arc. Nó cũng chỉ giao dịch **1,94 lệnh/tuần** (**hụt Target 3 3,6 lần**) và **không thể kiểm chứng trên holdout**

**Câu hỏi.** Cả hai lever đều hoạt động bằng cách **giữ vị thế sống lâu hơn** — band rộng đẩy rào thoát ra xa, hold dài cấm đảo chiều sớm. **Có thể chúng là cùng một cơ chế đo theo hai cách.**

**Đăng ký trước phân hoạch**: hiệu ứng của band lên **PnL mỗi lệnh**, đo **tại hold 288**; **≥ 30%** (ít nhất một nửa mức 62,5% ở hold 36) → hai lever **khác nhau** và cộng hưởng; **< 30%** → **cùng một cơ chế**.

**Validity**: cả năm cấu hình đều `candle_count` **57.934** — **một cửa sổ**; và điểm hold-288 của r363 **tái lập chính xác** (108 lệnh, −0,32723) khi chạy lại vòng này.

| band | hold | lệnh | /tuần | `one_target` PnL | **PnL/lệnh** | funding/lệnh |
|---|---|---|---|---|---|---|
| 0,01/0,02 | 36 | 270 | 6,30 | −1,57256 | −0,005824 | −0,000354 |
| 0,02/0,04 | 36 | 186 | 4,34 | −0,40571 | −0,002181 | −0,000522 |
| 0,01/0,02 | 288 | 108 | 2,52 | −0,32723 | −0,003030 | −0,000542 |
| **0,02/0,04** | **288** | **83** | **1,94** | **+1,17395** | **+0,014144** | −0,000620 |

Hiệu ứng band lên PnL/lệnh: **+62,5%** ở hold 36 → **+566,8%** ở hold 288 → **nhánh "khác nhau" xảy ra, hai lever cộng hưởng siêu-cộng-tính** (đọc chiều kia: hold cho +48,0% ở band hẹp, **+748,5%** ở band rộng).

**Và góc đó có lãi**: **+1,17395** trên 300 ngày, **+0,014144/lệnh**, với **funding mỗi lệnh tệ hơn** (−0,000620) → **không phải do cắt chi phí**. Mô tả mạch lạc: **giữ tối thiểu ~24 giờ (288 × 5m), thoát ở −2%/+4%** — cấu hình **swing** thay vì **scalp** như deployed; win rate ngụ ý ~57% cho payoff 4%/2%, không phi lý.

**Vì sao đây KHÔNG phải ứng viên — nói thẳng:**
1. **Target 3 hụt 3,6 lần**: 1,94 lệnh/tuần so với mốc 7,0; Target 3 cần **~300 lệnh** trên cửa sổ này, cấu hình chỉ có **83**. **Góc lãi nhất cũng là góc ít hoạt động nhất** — đúng đánh đổi arc gặp ở mọi lever.
2. **Không có bằng chứng holdout và không thể có**: flag hold xung đột với gate → **điều kiện 1 không thể đáp ứng cho bất kỳ cấu hình nào dùng hold**.
3. **Tham số được chọn SAU khi nhìn cửa sổ**: qua r359–r365 tôi đã đi khoảng **bốn giá trị hold × bốn band** trên route này; **một góc dương trong lưới ~16 ô trên một cửa sổ đúng là hình dạng của overfitting** — tôi không giả vờ ngược lại.
4. **Một cửa sổ, một route** — r331/r334/r341 đều từng có cấu hình "trông đã ổn" rồi dịch theo cửa sổ; r352 cho thấy **mọi holdout đều lồng nhau** nên kiểm "cửa sổ thứ hai" cũng yếu hơn vẻ ngoài.
5. **83 lệnh là mẫu nhỏ** cho trung bình mỗi lệnh, và output không có khoảng tin cậy.

**Điều gì sẽ đổi bức tranh**: một **điểm holdout** cho cấu hình kết hợp (**cần sửa code**), và **cùng góc đó sống sót trên route/cửa sổ mà nó không được chọn từ đó**.

**Giới hạn**: **không** khẳng định cấu hình này có lãi **ngoài mẫu**. **Không** khẳng định nó không phải overfitting — lưới ~16 ô tìm được một góc dương, **đó chính là giả thuyết null và không gì ở đây bác bỏ nó**. **Không** khẳng định tính siêu-cộng-tính là **cơ chế** — tương tác được **đo**, không được **giải thích**. Win rate ~57% là **số học từ tỷ lệ payoff**, không phải đo được. **Chưa test** trên `binance BTC`, `bybit XAUT`, hay cửa sổ khác. **Không promote.**

Chi tiết: `research/quant/rounds/round365-NEEDS-MORE-RESEARCH-band-and-hold-compose-super-additively-into-the-first-positive-pnl-at-deployed-costs.md`.

## Round 364 — REJECTED: quy tắc lâu năm *"lỗ ≈ số lệnh × một hằng số gần cố định"* **bị bác bỏ** với band fractional. Nới 0,01/0,02 → 0,02/0,04 làm **mỗi lệnh tốt hơn 62,5%**, trong khi **funding mỗi lệnh tăng 47%** — phần lợi là **chất lượng, không phải số lượng**

**Áp công cụ của Round 363 vào một hướng đã đóng.** r363 tạo ra kỹ thuật: khi không quan sát được tách gross/cost, dùng **PnL ròng mỗi lệnh + `funding_paid` mỗi lệnh** để tách "ít lệnh hơn" khỏi "lệnh tốt hơn" — vì funding là thành phần chi phí **duy nhất chứng minh được biến theo thời gian giữ**; nếu nó **đi ngược** chiều cải thiện thì cải thiện **không phải** do cắt chi phí. Quy tắc kinh tế đứng từ r96 và nhắc lại ở r274 là **per-trade gần như hằng số qua các mức band** — chưa từng được test bằng công cụ này trên đường `one_target`.

**Đăng ký trước phân hoạch**: **|ΔQ|/|Q_deployed| ≥ 5%** → band đổi **chất lượng** lệnh, quy tắc hằng số **thất bại**; **< 5%** → quy tắc đứng.

**Validity**: `candle_count` **57.934** ở cả hai — cùng cửa sổ. **Lưu ý control khác r363**: `legacy_selected_rule` **không bất biến** ở đây (345 → 214 lệnh; −1,633800 → −0,845140) vì **band ảnh hưởng cả ledger ngoài guard** → **phép so band không có control trôi miễn phí**, chỉ dựa vào `candle_count`.

| band | lệnh | /tuần | `one_target` PnL | **PnL/lệnh** | funding/lệnh |
|---|---|---|---|---|---|
| 0,01/0,02 (deployed) | 270 | 6,30 | −1,57256 | **−0,005824** | −0,000354 |
| **0,02/0,04** | 186 | 4,34 | **−0,40571** | **−0,002181** | **−0,000522** |

**Q đổi 62,5% → nhánh đã đăng ký xảy ra, quy tắc hằng số bị bác bỏ.** Phân rã mức cải thiện PnL **74,2%**: lệnh **−31,1%**, **PnL/lệnh +62,5%**, **funding/lệnh −47,4% (tệ đi)** → chi phí mỗi lệnh **tăng** ⇒ **gross mỗi lệnh cải thiện còn nhiều hơn net**. **Phần lớn là chất lượng, không phải số lượng.**

**Tương phản với ladder hold** (cùng route/cửa sổ, cắt lệnh gần bằng nhau):

| lever | Δ lệnh | Δ PnL/lệnh | bị chi phối bởi |
|---|---|---|---|
| hold 72 → 144 (r363) | −28,4% | **+2,7%** | số lượng |
| **band 0,01 → 0,02 (vòng này)** | −31,1% | **+62,6%** | **chất lượng** |

**Hai lever cắt lệnh gần như bằng nhau nhưng làm hai chuyện hoàn toàn khác với những lệnh còn lại.**

**Mở lại gì và không mở lại gì**: **phép đo của r274 vẫn đứng** (band **ATR**, cửa sổ khác, 0,93×); cái thất bại là **khái quát hoá** "mọi hiệu chỉnh đều giữ hằng số per-trade" — với band fractional ở đây tỷ số là **0,37×**. **Không mở lại band như một ứng viên**: vẫn lỗ; **Target 3 còn tệ hơn** (6,30 → 4,34/tuần); đây là **toàn cửa sổ `one_target`, không phải điểm holdout**, mà r330–r341 đóng band bằng **gate run trên holdout**; và **hướng thì trùng khớp** với gate run (r335 @500 cũng cải thiện khi nới) → đây là **cách đọc sắc hơn của cùng một hướng, không phải mâu thuẫn**.

**Giới hạn**: **không** khẳng định chất lượng cải thiện **vô hạn** theo độ rộng — **hai điểm**, và r330–r341 tìm thấy **cực trị trong** cùng một **rãnh** trên đường gate. Lập luận "edge" là **định hướng, không phải phân rã** (funding là chi phí duy nhất chứng minh được biến; fee/slippage mỗi lệnh không quan sát riêng được). **Không promote**: không có bằng chứng holdout và joint objective đi sai hướng.

Chi tiết: `research/quant/rounds/round364-REJECTED-per-trade-economics-are-not-constant-across-band-settings-the-wide-band-trades-62-percent-better.md`.

## Round 363 — REJECTED (như một ứng viên): lever hold cải thiện **cả chất lượng lệnh** (**+48%** mỗi lệnh) **lẫn số lệnh** (**−60%**), thu nhỏ khoản lỗ **79%** từ hold 36 lên 288 — và quỹ đạo của nó dẫn tới **không giao dịch, không phải lợi nhuận**. Target 3 bị phá ở mọi bước: **6,30 → 2,52 lệnh/tuần**

**Đăng ký trước dạng phân hoạch** cho phần phân rã: gọi Q = PnL ròng **mỗi lệnh**; nếu phần lợi là **thuần cắt lệnh** ở chất lượng không đổi thì Q **phẳng**. **|ΔQ|/|Q₃₆| ≥ 5%** giữa hold 36 và 144 → lệnh còn lại **khác về chất lượng**; **< 5%** → nhất quán với cắt lệnh thuần.

**Validity gate đạt**: `candle_count` **57.934** ở cả hai nhánh; `legacy` **345 lệnh / −1,633800** ở cả hai.

| hold | lệnh | lệnh/tuần | `one_target` PnL | **PnL/lệnh** | Δ lệnh | Δ PnL/lệnh |
|---|---|---|---|---|---|---|
| 36 (deployed) | 270 | 6,30 | −1,57256 | **−0,005824** | — | — |
| 72 | 229 | 5,34 | −1,00705 | −0,004398 | −15,2% | **+24,5%** |
| 144 | 164 | 3,83 | −0,70183 | −0,004279 | −28,4% | +2,7% |
| **288** | **108** | **2,52** | **−0,32723** | **−0,003030** | −34,1% | **+29,2%** |

**Q(36) → Q(144) là +26,5%, vượt xa mốc 5% → nhánh đã đăng ký xảy ra: lệnh còn lại thật sự tốt hơn, không chỉ ít hơn.**

**Bằng chứng funding làm sắc thêm**: chi phí funding **mỗi lệnh tăng** theo hold (−0,000354 ở 36 so với **−0,000409** ở 144, **tệ hơn 15,5%**) — đúng như hold dài phải thế. Vậy **chi phí mỗi lệnh tăng trong khi net mỗi lệnh cải thiện 26,5%** → **gross mỗi lệnh cải thiện còn nhiều hơn**. **Đây là cơ chế đầu tiên trong arc chạm được vào EDGE chứ không phải chi phí.**

**Và cách đọc giữa vòng của tôi đã sai**: sau khi thấy 72 → 144 chỉ đổi chất lượng **+2,7%**, tôi dự đoán mọi thứ sau 72 là cắt lệnh thuần. **Điểm 288 bác bỏ** điều đó với **+29,2%** nữa → chuỗi per-trade **lồi lõm, không đơn điệu theo bước** — ghi nhận ngược lại suy luận của chính tôi.

**Vì sao vẫn không phải ứng viên.** Cộng dồn 36 → 288: PnL cải thiện **79,2%**, lệnh giảm **60,0%**, tần suất **6,30 → 2,52/tuần**.
1. **Không bao giờ dương** — lỗ mỗi lệnh còn **−0,003030** ở điểm sâu nhất, **không dấu hiệu cắt 0**; khoản lỗ nhỏ đi **chủ yếu vì ít lệnh hơn** (biên độ mỗi lệnh giảm 48% trong khi số lệnh giảm 60%).
2. **Target 3 bị phá** — đã trượt ở hold 36 (6,30 < 7,0); ở 288 là **2,52/tuần, hụt 2,8 lần**.
3. **Điểm cuối là không giao dịch** — kéo hold vô hạn đưa số lệnh về 0 và PnL về 0 **từ phía dưới**; đó là **số học, không phải chiến lược**.
4. **`binance BTC` — route duy nhất giữ Target 3 ở hold 72 — thì bão hoà** (r360: 3,5% cùng bước). Vậy **không route nào có đường đi**: XAU cải thiện tiếp nhưng không giao dịch nổi, BTC giao dịch được nhưng hết cải thiện và **gross âm** (r342).
5. **Vẫn không promote được**: flag xung đột với gate → **không có điểm holdout**, **điều kiện 1** không đáp ứng.

**Hướng này đóng lại như một ứng viên.** Cái còn lại là **cơ chế**: guard cải thiện **chất lượng lệnh** — đáng nhớ cho lần sau khi có thứ trông như một núm chỉnh tần suất thuần tuý.

**Giới hạn**: **không** khẳng định lỗ mỗi lệnh **không bao giờ** cắt 0 — bốn điểm, **không khớp xu hướng**; cái xác lập được là **không gì trong dải đã thử gợi ý điều đó**. **Không** khẳng định phần cải thiện là **edge** thay vì một thành phần chi phí khác — funding là chi phí **duy nhất** chứng minh được biến theo hold và nó **đi ngược** chiều cải thiện, nên lập luận là **định hướng, không phải phân rã**. **Không** khẳng định tính lồi lõm là cấu trúc — ba bước, một route, một cửa sổ.

Chi tiết: `research/quant/rounds/round363-REJECTED-the-hold-lever-shrinks-the-loss-by-trading-less-and-its-endpoint-is-no-activity-not-profit.md`.

## Round 362 — NEEDS-MORE-RESEARCH: ladder hold **bão hoà trên `binance BTC` nhưng KHÔNG trên `exness XAU`** — bước 72 → 144 mua được **3,5%** ở bên kia và **+30,3%** ở đây. Cộng dồn 36 → 144 là **+55,4%** trên XAU, đổi bằng **39% ít lệnh hơn** trên một route vốn đã trượt Target 3

**Câu hỏi.** Round 360 thấy ladder **bão hoà** trên `binance BTC` (72 → 144 chỉ mua 3,5% và phá Target 3), nhưng đó là tính chất của **lever** hay của **route** thì chưa test.

**Đăng ký trước, validity gate đi đầu**: `candle_count` giống hệt **và** `legacy_selected_rule` giống hệt, hai nhánh chạy cùng lúc. **Nếu hợp lệ**: hold 144 cải thiện so với 72 **≥ 10%** → ladder XAU tiếp tục, khác BTC; **< 10%** → cũng bão hoà ở 72.

**Validity gate — đạt**: `candle_count` **57.933 = 57.933**; `legacy` **345 lệnh, −1,633800** ở cả hai.

**Kết quả — ladder XAU tiếp tục**

| hold | lệnh | lệnh/tuần | `one_target` PnL | mức tăng bước | `ec_rej` |
|---|---|---|---|---|---|
| 36 (deployed)\* | 270 | 6,30 | −1,57256 | — | 97 |
| 72 | 229 | 5,34 | −1,00705 | +36,0% | 71 |
| **144** | **164** | **3,83** | **−0,70183** | **+30,3%** | 30 |

\* dòng 36 lấy từ Round 361 ở 57.929 nến — xem ghi chú bên dưới.

**Delta +0,30523, tương đối +30,3% → nhánh "tiếp tục"**, so với **3,5%** của `binance BTC` **ở cùng bước**. → **Bão hoà là tính chất của ROUTE, không phải của lever.** Cộng dồn **36 → 144 là +55,4%** trên route này.

**Cái giá**: tần suất rơi **6,30 → 3,83 lệnh/tuần (−39%)** trên route **vốn đã trượt Target 3 ở mọi mức hold** — ladder XAU mua PnL bằng tần suất route **không dư**, cùng dạng với `bybit XAUT`, khác `binance BTC` (route duy nhất mà hold 72 giữ được mốc).

**Không phân rã được**: đường plain `--json` chỉ báo `realized_pnl` (**net**), và đưa chi phí về 0 để lộ gross sẽ kéo chi phí đảo chiều xuống dưới gate 10 bps và **đổi không gian hành động** (r348) — đúng rào cản đã chặn câu hỏi gross-theo-thứ ở r354. Lệnh giảm 39% trong khi PnL cải thiện 55% là **nhất quán với** nhiều hơn thuần cắt chi phí, **nhưng tôi không tách được và không khẳng định**.

**Tinh chỉnh quy tắc trôi**: r361 đo dịch **36 nến** làm PnL đổi **0,25040**. Vòng này nhánh hold-72 ở **57.933** nến so với **57.929** của r361 — dịch **4 nến** — và **tái lập chính xác −1,00705 với 229 lệnh**. → **Độ trôi KHÔNG tỉ lệ với mức dịch**: 4 nến đổi **0**, 36 nến đổi 18,9% thang đo. **Điều đó không cho phép so sánh xuyên vòng** — nó cho thấy kiểm `candle_count` là guard **đúng** chính vì hiệu ứng **không đoán trước được**. Phép so **72 → 144 đã đăng ký thì hoàn toàn trong-vòng**.

**Giới hạn**: **không** khẳng định phần cải thiện là **edge** hay **cắt chi phí** — không phân rã được. **Không** khẳng định ladder không bão hoà **quá 144** trên XAU — chưa test, và `binance BTC` từng trông đơn điệu ở 72 rồi gần như phẳng ở 144, nên ngoại suy đúng là sai lầm cần tránh. **Không** khẳng định điều này giúp joint objective — tần suất **−39%** trên route đã trượt Target 3 rất xa ở mọi mức hold. **Không promote**: vẫn không có điểm holdout cho tham số này (**điều kiện 1**).

Chi tiết: `research/quant/rounds/round362-NEEDS-MORE-RESEARCH-the-hold-ladder-saturates-on-btc-but-not-on-xau-where-144-still-gains-30-percent.md`.

## Round 361 — NEEDS-MORE-RESEARCH: chạy đúng cách, `exness XAU` **có** phản ứng với lever hold — **+36,0%** — và validity gate **đạt đúng như thiết kế**: `candle_count` giống hệt và control `legacy` **trùng khít từng chữ số**. Lever nay có bằng chứng cùng-cửa-sổ trên **ba route**, và chỉ `binance BTC` giữ được Target 3

**Làm lại phép test mà Round 360 vô hiệu hoá.** r360 so một run hold-72 mới với run hold-36 **từ vòng trước**, cửa sổ lệch 40 nến — control `legacy` dịch 0,306 so với "hiệu ứng" 0,315, nên phép so chết. Đơn thuốc của nó rất rõ: **chạy cả hai nhánh trong cùng một vòng.**

**Đăng ký trước, validity gate đi đầu**: hai run phải có **`candle_count` giống hệt** **và** `legacy_selected_rule` **giống hệt** (số lệnh + PnL) — `legacy` bỏ qua construction guard nên **bắt buộc bất biến** với hold; lệch một trong hai → **vô hiệu**. **Nếu hợp lệ**: hold 36 → 72 đổi `one_target` PnL **≥ 10%** → `exness XAU` phản ứng; **< 10%** → lever chỉ giới hạn ở route mà guard cắn mạnh.

**Validity gate — đạt cả hai tiêu chí**

| kiểm tra | hold 36 | hold 72 | kết luận |
|---|---|---|---|
| `candle_count` | **57.929** | **57.929** | cùng cửa sổ |
| `legacy_selected_rule` | 345 lệnh, **−1,633800** | 345 lệnh, **−1,633800** | **trùng khít** |

Control hành xử **đúng như lý thuyết đòi hỏi** ở một ledger guard-free — và đó cũng là xác nhận trực tiếp chẩn đoán của r360: **giữ cố định cửa sổ thì độ trôi biến mất hoàn toàn.**

**Kết quả — có phản ứng, và mạnh**

| hold | lệnh | lệnh/tuần | `one_target` PnL | giảm lệnh | `ec_rej` |
|---|---|---|---|---|---|
| 36 (deployed) | 270 | 6,30 | −1,57256 | 0,2174 | 97 |
| **72** | 229 | **5,34** | **−1,00705** | 0,3362 | 71 |

**Delta +0,56550, tương đối +36,0% → nhánh "có phản ứng".**

**Điều này đính chính cách tôi đọc Round 358**: ở đó tôi đo guard-tại-36 so với guard-free trên `exness XAU` được **0,44%** và hiểu thành "guard gần như không quan trọng ở route này". **Đó là hai đại lượng khác nhau**: **36 quyết định hold đầu tiên** gần như vô giá trị ở đây, **36 quyết định tiếp theo** đáng **36%**. **Thiếu hiệu ứng mức không nói gì về đòn bẩy biên của tham số** — tôi không nên tổng quát hoá từ đó.

**Bức tranh ba route, đều đã xác minh cùng cửa sổ**

| route | PnL 36 → 72 | cải thiện | lệnh/tuần | Target 3 |
|---|---|---|---|---|
| `exness XAU` @300 | −1,57256 → −1,00705 | **+36,0%** | 6,30 → 5,34 | trượt → trượt |
| `bybit XAUT` @500 | −1,57738 → −1,24701 | +20,9% | 3,46 → 3,01 | trượt → trượt |
| `binance BTC` @500 | −4,74869 → −2,74744 | **+42,1%** | 9,65 → **7,24** | **đạt → đạt** |

**Lever hoạt động trên mọi route đã thử — 21% đến 42% — nhưng ở hai trong ba, nó mua PnL bằng tần suất mà route vốn không dư.** Chỉ `binance BTC` còn vượt mốc 7,0 sau bước đó, mà **gross của nó âm** (r342) → lỗ nhỏ hơn **không phải** con đường tới lãi.

**Một con số cụ thể cho quy tắc của r360**: hai run `exness XAU` @300 hold-36 cách nhau 4 giờ — r349 (18:30) 57.965 nến, PnL −1,32216; r361 (22:30) **57.929** nến, **−1,57256**. **Dịch 36 nến (3 giờ) làm PnL đổi 0,25040 — 18,9% thang đo.**

**Giới hạn**: **không** khẳng định hold 72 tốt hơn **ngoài mẫu** — vẫn là rào cản cấu trúc: **không có điểm holdout** cho tham số này, **điều kiện 1 không đáp ứng được**; ba route cải thiện toàn-cửa-sổ **không phải** bằng chứng OOS. **Không** khẳng định lever giúp joint objective — hai trong ba route **mất** tần suất vốn đã thiếu, route còn lại **gross âm**. **Một cửa sổ** cho con số 36%. Số đo độ trôi **không tổng quát hoá** (route 24/7 trôi **bằng 0** qua khoảng cách tương tự). **Không promote.**

Chi tiết: `research/quant/rounds/round361-NEEDS-MORE-RESEARCH-the-hold-lever-transfers-to-exness-xau-at-36-percent-on-a-validity-gated-same-window-test.md`.

## Round 360 — DATA-ISSUE: hai run từ **hai vòng khác nhau không cùng cửa sổ**, và ledger `legacy` là **control trôi cửa sổ miễn phí** cho biết điều đó. Nó **vô hiệu hoá** phép test chuyển giao của tôi — trong khi ladder BTC **cùng cửa sổ** cho thấy lever hold **bão hoà ở 72**, và 144 thì **phá Target 3**

**Hai câu hỏi đã đăng ký** (Round 359 nêu tên cả hai): **H1 (chuyển giao)** — trên `exness XAU`, hold 36 → 72 đổi `one_target` PnL **< 10%** → lever phụ thuộc route, gắn với nơi guard cắn; **≥ 10%** → route **có** phản ứng. **H2 (đơn điệu)** — `binance BTC` hold 144 cải thiện so với −2,74744 của hold 72 → ladder tiếp tục; ngược lại → nó quay đầu như band lever ở r330–r335.

**H2 — sạch, và trả lời câu hỏi hữu ích hơn.** Cả ba run báo **143.998 nến** → cửa sổ **giống hệt** (đã kiểm chứng, không giả định):

| hold | lệnh | lệnh/tuần | `one_target` PnL | mức tăng bước | từ chối `execution_cost` |
|---|---|---|---|---|---|
| 36 (deployed) | 689 | 9,65 | −4,74869 | — | 189 |
| **72** | 517 | **7,24** | **−2,74744** | **+2,00126 (42,1%)** | 111 |
| 144 | 368 | **5,15** | −2,65041 | **+0,09702 (3,5%)** | 46 |

**Ladder tiếp tục nhưng bão hoà mạnh**: lần gấp đôi thứ hai chỉ mua được **3,5%** trong khi lần đầu mua **42,1%**, **và** nó **phá mục tiêu tần suất** — **5,15 lệnh/tuần trượt mốc 7,0** mà hold 72 còn vượt. → **Trong các giá trị đã thử, hold 72 là điểm joint-objective**: gần như toàn bộ phần PnL cải thiện được, Target 3 còn nguyên. Từ chối `execution_cost` giảm 189 → 111 → 46 là nhất quán: hold dài chặn lệnh đảo chiều **trước khi** risk gate nhìn thấy.

**H1 — vô hiệu, và lý do chính là phát hiện của vòng.**

| hold | `one_T` lệnh | `one_T` PnL | `legacy` lệnh | **`legacy` PnL** | nến |
|---|---|---|---|---|---|
| 36 | 280 | −1,32216 | 355 | **−1,32799** | **57.965** |
| 72 | 229 | −1,00705 | 345 | **−1,63380** | **57.925** |

"Hiệu ứng" đo được là **+0,31511 (+23,8%)** — đủ để bắn nhánh "có phản ứng". **Nhưng không dùng được**: hai run **cách nhau 40 nến** (khác cửa sổ, cách nhau 3,5 giờ), và `legacy_selected_rule` **bỏ qua hoàn toàn construction guard** nên **phải bất biến** với tham số hold — vậy mà nó dịch **0,30581**. **Độ trôi trên control bằng đúng cỡ hiệu ứng trên treatment** (0,306 vs 0,315). **H1 vô hiệu**; việc `exness XAU` có phản ứng với lever hold hay không là **chưa biết**, và thí nghiệm đúng là **chạy cả hai nhánh trong cùng một vòng**.

**Guard tái dùng được, và nó đã được phát ra sẵn**: mỗi run có `candle_count` ở dòng ECS đầu tiên (`event.dataset: research.backtest_candle_count`). **Hai run chỉ so sánh được nếu `candle_count` khớp.** Kiểm chứng vòng này: `binance BTC` 36/72/144 = 143.998 ×3 → **cùng cửa sổ**, H2 đứng vững; `bybit XAUT` 36/72 (r358/r359) = 143.998 ×2 → **cùng cửa sổ**, nhánh XAUT của r359 đứng vững; `exness XAU` 36/72 = 57.965 / 57.925 → **khác**, H1 vô hiệu. **Route crypto 24/7 lượng tử hoá về cùng số nến qua vài chục phút; `exness XAU` theo phiên nên cửa sổ dịch — độ trôi phụ thuộc route, đó chính là lý do phải kiểm tra chứ không được giả định.** Và khi chỉ thay tham số Portfolio-construction, **`legacy_selected_rule` là control miễn phí**: nó guard-free nên mọi chuyển động của nó là **trôi, không phải hiệu ứng**.

**Giới hạn**: **không** kết luận `exness XAU` có phản ứng với lever hold — test vô hiệu, và **tôi không báo +23,8% như một hiệu ứng**. **Không** khẳng định hold 72 tối ưu (ba giá trị, một route, một cửa sổ; khoảng 72–144 chưa lấy mẫu). **Không** khẳng định bão hoà chuyển sang route khác. **Vẫn không promote** (r359): không có điểm holdout cho tham số này; `binance BTC` còn có **gross âm**. **Không** khẳng định mọi so sánh cross-round trước đây đều an toàn — ba cái kiểm ở trên thì có, **các cái khác chưa được kiểm theo `candle_count` và cần rà lại**.

Chi tiết: `research/quant/rounds/round360-DATA-ISSUE-cross-round-comparisons-drift-and-legacy-is-a-free-drift-control-the-hold-ladder-saturates-at-72.md`.

## Round 359 — NEEDS-MORE-RESEARCH: tăng minimum-hold từ **36 lên 72** cắt **42%** khoản lỗ của `binance BTC` và **21%** của `bybit XAUT`, mà `binance BTC` **vẫn đạt Target 3** ở **7,24 lệnh/tuần**. Đây là cải thiện đáng kể **đầu tiên** của cả arc — và nó **không thể kiểm chứng trên holdout**, do cấu trúc công cụ

**Vì sao lever này, và vì sao lúc này.** Round 358 cho thấy minimum-hold guard là hiệu ứng **bậc nhất** ở nơi nó cắn (41% trên `binance BTC`, 19,8% trên `bybit XAUT` so với luồng không-guard). **Mọi lever arc từng tinh chỉnh đều là protective band**; `--portfolio-minimum-hold-decisions` là **tham số production đã deploy, chỉnh được** (đang là 36) mà **chưa bao giờ được dịch**.

**Đăng ký trước phân hoạch**: hold 72 cải thiện `one_target` PnL trên **cả hai** route so với hold 36 → lever hữu ích ở nơi guard cắn, đáng làm ladder; **một trong hai** tệ hơn → không đáng tin.

| route | cấu hình | lệnh | lệnh/tuần | `one_target` PnL | so với guard-free |
|---|---|---|---|---|---|
| `bybit XAUT` | guard-free | 309 | 4,33 | −1,96680 | — |
| `bybit XAUT` | **hold 36 (deployed)** | 247 | 3,46 | −1,57738 | +19,8% |
| `bybit XAUT` | **hold 72** | 215 | 3,01 | **−1,24701** | **+36,6%** |
| `binance BTC` | guard-free | 990 | 13,86 | −8,07260 | — |
| `binance BTC` | **hold 36 (deployed)** | 689 | 9,65 | −4,74869 | +41,2% |
| `binance BTC` | **hold 72** | 517 | **7,24** | **−2,74744** | **+66,0%** |

**Cả hai đều cải thiện — nhánh đã đăng ký xảy ra.** Bước 36 → 72 đáng **+20,9%** (XAUT) và **+42,1%** (BTC), **đơn điệu** qua cả ba điểm trên mỗi route. **Và trên `binance BTC` joint objective sống sót qua bước đó**: 7,24 lệnh/tuần **vẫn vượt mốc 7,0** — **lần đầu tiên trong arc một lever cải thiện PnL đáng kể mà không lập tức phá mục tiêu tần suất**. `bybit XAUT` **trượt Target 3 ở mọi mức hold**, nên cải thiện ở đó không phải ứng viên. **Cả hai route vẫn lỗ** — đó là **lỗ nhỏ hơn, không phải lãi**.

**Rào cản, và nó mang tính cấu trúc**: `--portfolio-minimum-hold-decisions` **xung đột** với `--daily-profit-gate` (`main.rs:255-263`) **chính vì gate không mô hình hoá construction guard** (r356). → **Lever này không chấm được trên holdout với CLI hiện tại.** Mọi con số vòng này là **`one_target` toàn cửa sổ**, **không phải** bằng chứng OOS mà **điều kiện 1** của promotion gate đòi hỏi. **Đó không phải lý do để nới gate** — đó là lý do kết quả này dừng ở NEEDS-MORE-RESEARCH **dù là cải thiện lớn nhất arc từng tạo ra**. Bước gỡ chặn cụ thể là **sửa code**: cho gate nhận giá trị hold và mô hình hoá guard, hoặc phơi ra `one_target` giới hạn theo holdout.

**Giới hạn**: **không** khẳng định hold 72 tốt hơn **ngoài mẫu** — không đo được trên holdout, và cải thiện toàn-cửa-sổ từ một tham số chọn **sau khi** nhìn cửa sổ đúng là loại kết quả loop này nghi ngờ. **Không** khẳng định đơn điệu **quá 72** — ba điểm một chiều, và r330–r335 từng có lever trông đơn điệu **rồi quay đầu**. **Không** khẳng định chuyển sang `exness XAU` (guard chỉ đổi 0,4% ở đó — **chưa test**, là run hiển nhiên tiếp theo). **Không** khẳng định route nào trở nên khả thi: cả hai vẫn lỗ, `bybit XAUT` hụt Target 3 **2,3 lần**, và **gross của `binance BTC` vốn âm** ở cửa sổ này (r342) — **lỗ nhỏ hơn trên gross âm không phải con đường tới lãi**. **Không promote**: điều kiện 1 **không thể đáp ứng** cho tham số này, bất kể độ lớn hiệu ứng.

Chi tiết: `research/quant/rounds/round359-NEEDS-MORE-RESEARCH-the-minimum-hold-lever-cuts-losses-42-percent-and-cannot-be-validated-on-holdout.md`.

## Round 358 — REJECTED: kết luận *"guard không đáng kể về độ lớn"* của Round 356 **chỉ đúng cho `exness XAU`**. Trên `binance BTC`, guard **cắt 41% khoản lỗ**. Và phép so tần suất live của Round 357 dùng **mẫu số thiên lệch** — sửa lại thì **đảo chiều**

**Phần 1 — tác động của guard không tổng quát hoá.** r356 đo `|one_target − legacy| / |legacy|` trên `exness XAU` được 0,44% / 3,83% / 1,94% qua ba cửa sổ và kết luận **"không đáng kể"** — nhưng đó là **ba cửa sổ trên MỘT route**. **Đăng ký trước phân hoạch**: D = giá trị lớn nhất của tỷ số đó trên **hai route chưa từng test**; **D ≥ 0,20** → guard đổi kết quả đáng kể ở nơi khác, kết luận r356 **không tổng quát**; **D < 0,20** → mở rộng được.

| route @500 | `one_target` | `legacy` | giảm lệnh | `one_T` PnL | `legacy` PnL | **chênh** |
|---|---|---|---|---|---|---|
| **`binance BTC`** | 689 | 990 | **0,3040** | **−4,74869** | **−8,07260** | **0,4118** |
| **`bybit XAUT`** | 247 | 309 | 0,2006 | −1,57738 | −1,96680 | **0,1980** |
| `exness XAU` @300 (r356) | 280 | 355 | 0,2113 | −1,32216 | −1,32799 | 0,0044 |

**D = 0,4118 → ĐÁNG KỂ.** Trên `binance BTC`, guard bỏ 30% số lệnh và **cắt 41% khoản lỗ**. → **Gate — vốn chấm luồng không-guard (r356) — bi quan có hệ thống trên những route mà guard cắn**; verdict BTC của gate **lệch nhiều**. Kết luận "không đáng kể" của r356 **rút lại ở dạng tổng quát**, giữ lại như một quan sát riêng của `exness XAU`.

**Phần 2 — mẫu số của Round 357 bị thiên lệch.** r357 tính tần suất live bằng *số lệnh ÷ (entry cuối − entry đầu)*. **Mẫu số đó điều kiện hoá trên chính các sự kiện** → **thổi phồng** tần suất; mẫu số đúng là **cửa sổ quan sát**. Hai điều r357 ghi là "chưa đọc" nay đã kiểm chứng: **writer chỉ append** (`trade_log.rs` chỉ có `ZADD`, **không** trim/expire/delete → follow-up "chờ rồi đọc lại" **hợp lệ**), và **ba entry đúng là một lệnh** ghi dưới **ba paper scope** (`paper-risk-2pct`, `paper-compounding-10pct`, `paper-fixed-pct`) → **số đếm của r357 đúng**.

Redis khởi động **2026-08-22 05:26 UTC**. Sửa mẫu số:

| cửa sổ | `exness XAU` | `binance BTC` | `bybit BTC` | `exness BTC` |
|---|---|---|---|---|
| **8,67 ngày** (Redis) — live/tuần | 0,81 | 4,84 | 3,23 | 3,23 |
| CI 95% | [0,02; 4,50] | [1,78; 10,54] | [0,88; 8,27] | [0,88; 8,27] |
| backtest/tuần | 5,05 **NGOÀI** | 21,84 **NGOÀI** | 12,11 **NGOÀI** | 24,58 **NGOÀI** |
| **3,40 ngày** (worker) — live/tuần | 2,06 | 12,35 | 8,24 | 8,24 |
| backtest | 5,05 trong | 21,84 trong | 12,11 trong | 24,58 **NGOÀI** |

Với **cửa sổ Redis đầy đủ**, **năm trên sáu route có tần suất backtest nằm NGOÀI khoảng tin cậy live**, đều theo hướng **backtest dự báo nhiều hơn thực tế 4,5–7,6 lần**. **Cửa sổ nào đúng thì dữ liệu lưu giữ không phân xử được**: entry đầu tiên xuất hiện 2026-08-27/28 khớp lúc deploy worker, nhưng lệnh `exness XAU` duy nhất có `entry_at` **2026-08-26** — **trước** deploy — chỉ chứng minh vị thế **sống sót qua restart**, **không** nói gì về lúc logging bắt đầu. **Verdict thực sự chưa xác định**, và tôi **không** báo cáo phân kỳ live-vs-backtest như một finding — nhưng "không phát hiện bất nhất" của r357 đạt được **bằng mẫu số sai**.

**Một xác nhận miễn phí từ payload live**: lệnh `exness XAU` duy nhất mang `contributing_strategies: [candle_momentum −0,6296, mtf_stochastic_5m_4h_sma5 **0,0**, rsi_mean_reversion **0,0**]`. **Hai trong ba strategy deployed mang trọng số đúng bằng 0 trên một lệnh thật.** Đây là **bằng chứng trực tiếp đầu tiên ngoài replay** cho hiện tượng sụp trọng số mà arc suy ra từ `alpha_performance_quality`. Lệnh giữ 2,6 ngày, đóng `take_profit`, `return_fraction` **+1,88%**.

**Giới hạn**: **không** khẳng định guard sẽ cải thiện verdict BTC của gate **đúng 41%** — con số đó là **toàn cửa sổ** `one_target` vs `legacy`, **không phải** metric holdout của gate; **hướng** thì đã xác lập, **độ lớn** cho cửa sổ của gate thì chưa. **Không** khẳng định mức cắn của guard là thuộc tính route. **Không** khẳng định hai-trên-ba trọng số 0 là điển hình — **một lệnh**. **Không promote.**

Chi tiết: `research/quant/rounds/round358-REJECTED-the-guard-is-immaterial-only-on-exness-xau-it-moves-binance-btc-by-41-percent.md`.

## Round 357 — DATA-ISSUE: trade log production giữ **1 đến 6 lệnh đã đóng mỗi route** trên khoảng 3 ngày trùng với uptime worker. Phép kiểm live-vs-backtest mà arc chưa từng chạy **vẫn không chạy được** — và tôi ghi lại **vì sao**, kèm số

**Phép kiểm dự định.** Round 356 xác lập gate chấm luồng **không-guard** còn `one_target` là luồng **có guard**, và ở @300 chúng chênh **26,8%** về số lệnh (280 vs 355 ⇒ 6,53 vs 8,28/tuần). **Tần suất giao dịch live có thể phân xử điều đó.** **Đăng ký trước phân hoạch**: tần suất live trên `exness.cfd.xau.usd` gần **6,53/tuần** → hệ deployed **có guard**, `one_target` là tham chiếu đúng; gần **8,28/tuần** → cấu trúc của gate mới là trung thực.

**Vì sao không chạy được.** Redis production, cả sáu trade log (`trades:<route>`, **zset**, **ba entry mỗi lệnh đóng**, **không TTL** — `TTL` = −1):

| route | entry | **lệnh đóng** | span | lệnh đóng/tuần |
|---|---|---|---|---|
| `exness XAU` | 3 | **1** | **một timestamp duy nhất** | **n/a** |
| `bybit XAUT` | 3 | **1** | một timestamp | n/a |
| `binance XAU` | 3 | **1** | một timestamp | n/a |
| `binance BTC` | 18 | 6 | 2,74 ngày | 15,33 |
| `bybit BTC` | 12 | 4 | 2,45 ngày | 11,43 |
| `exness BTC` | 12 | 4 | 2,90 ngày | 9,66 |

Entry sớm nhất trên mọi route là **2026-08-27 14:39 UTC** và **cả sáu worker báo "Up 3 days"** → log **bắt đầu từ lúc worker khởi động**, không phải biên retention; key **không có TTL** nên đây là **cắt cụt do restart, không phải hết hạn**.

**`exness XAU` — đúng route mà cả arc xoay quanh — chỉ giữ MỘT lệnh đóng**, ba entry ở cùng một timestamp. **Không tính được tần suất** → **phân hoạch đã đăng ký không có đầu vào**. Với một quan sát, khoảng tin cậy Poisson 95% trải khoảng **0,03× đến 5,6×** giá trị điểm; phân biệt chênh lệch **26,8%** là **không thể**.

**Ba route BTC nói được gì, và ít đến mức nào**

| route | lệnh đóng | live/tuần | **CI 95%** | backtest/tuần | nhất quán? |
|---|---|---|---|---|---|
| `binance BTC` | 6 | 15,33 | **[5,63; 33,36]** | 21,84 | có |
| `bybit BTC` | 4 | 11,43 | **[3,11; 29,26]** | 12,11 | có |
| `exness BTC` | 4 | 9,66 | **[2,63; 24,72]** | 24,58 | có |

**Không phát hiện bất nhất trên route nào — và khoảng tin cậy rộng đến mức đây là "đồng thuận do thiếu năng lực phát hiện", không phải bằng chứng đã hiệu chuẩn.** Đây là **so sánh live-vs-backtest đầu tiên** của arc; tóm tắt trung thực: **replay chưa bao giờ được kiểm chứng với hành vi production, và với dữ liệu production lưu giữ thì vẫn chưa.**

Đây là **mặt kia của L4**: backtest **không serialize** bản ghi theo lệnh (`portfolio_measurement.rs:23-28`), production **giữ quá ít** (1–6 lệnh, reset khi restart) → **hiện không có đường nào từ một con số backtest tới một quan sát live của cùng đại lượng**. Số liệu của arc **nhất quán nội bộ và chưa được kiểm chứng từ bên ngoài**.

**Follow-up rẻ duy nhất**: log **lớn dần khi worker chạy liên tục**, nên **đọc lại sáu key này sau một đợt chạy dài hơn là miễn phí**. `exness XAU` cần khoảng **30–40 lệnh đóng** — chừng **6–8 tuần** ở tần suất backtest — trước khi chênh 27% tách được ở mức 95%.

**Giới hạn**: **không** khẳng định live và backtest **đồng thuận** — ba khoảng 3–33/tuần chứa gần như mọi giá trị hợp lý; đây là **không phát hiện được**, không phải đồng thuận. **Không** kết luận production có guard hay không — phân hoạch **không đánh giá được**. **Không** khẳng định log bị giới hạn theo thiết kế — **chưa đọc writer**. **Không** khẳng định 3 ngày là retention bình thường. **Không promote.**

Chi tiết: `research/quant/rounds/round357-DATA-ISSUE-the-live-trade-log-holds-1-to-6-closes-so-it-cannot-validate-any-backtest-rate.md`.

## Round 356 — DATA-ISSUE: scorecard `--daily-profit-gate` **không mô hình hoá cấu trúc Portfolio deployed**. Nó replay quyết định thẳng vào ledger — **không có hold guard, không có risk layer, và do đó không có gate chi phí 10 bps**. Ảnh hưởng PnL nhỏ (≤3,8%), ảnh hưởng **số lệnh thì không** (**21,1%** ở @300)

**Gate thực sự làm gì.** `daily_profit_gate.rs:376-412` dựng **một** `SimulatedLedger` và gọi **`ledger.on_kline(&timed.kline, &timed.decision)`** cho mỗi quyết định — **chỉ vậy**. Nó **không** gọi `PortfolioConstructionState::construct`, **không** áp `minimum_hold_decisions`, **không** chạy `PortfolioRiskLayer`. Đường `one_target` (`portfolio_measurement.rs:184-208`) làm **cả ba**. Theo định nghĩa r82, ledger được nuôi bằng `on_kline` trực tiếp **chính là** cấu trúc `legacy_selected_rule` → **gate chấm điểm luồng không-guard, không phải luồng Portfolio-faithful**.

Code nói thẳng ở `main.rs:255-263`: *"The daily-profit gate **does not model this construction comparison**…"* — đó là **lý do** `--portfolio-minimum-hold-decisions` **xung đột** với `--daily-profit-gate`. **Công cụ đã trung thực; tôi đọc xung đột đó như một điểm lạ của CLI chứ không phải một tuyên bố về thứ gate đo.**

**Đăng ký trước phân hoạch**: `|one_target − legacy| / |legacy|` trên realized PnL **≥ 0,20** → guard đổi kết quả đáng kể, metric gate không tin cậy; **< 0,20** → bỏ sót không đáng kể về độ lớn.

| cửa sổ | `one_target` lệnh | `legacy` lệnh | giảm lệnh | `one_target` PnL | `legacy` PnL | **chênh tương đối** | từ chối `execution_cost` |
|---|---|---|---|---|---|---|---|
| @300 | 280 | 355 | **0,2113** | −1,32216 | −1,32799 | **0,0044** | 102 |
| @1500 | 398 | 410 | 0,0293 | −3,82660 | −3,68554 | **0,0383** | 55 |
| @1800 | 488 | 504 | 0,0317 | −4,34249 | −4,25993 | **0,0194** | 73 |

**Cả ba ≤ 0,038 → nhánh "không đáng kể về độ lớn".** Nhưng **số lệnh là chuyện khác**: guard cắt **21,1%** lệnh ở @300 (~3% ở cửa sổ sâu) — và `trades_per_week` **là một ngưỡng của gate** (Target 3, 7,0/tuần). Gate báo tần suất của một luồng giao dịch **nhiều hơn** luồng deployed → tần suất thật **thấp hơn**, làm Target 3 **khó hơn**, không phải dễ hơn. **Mọi con số lệnh/tuần trích từ gate run kể từ r328 là một cận trên của tần suất deployed.** Cột `execution_cost` cho thấy tương phản trực tiếp: đường plain ghi **102/55/73** lần từ chối; đường gate **không ghi lần nào** vì không có risk layer.

**Đính chính bắt buộc với Round 348.** r348 giải thích bước nhảy thang phí của r344/r345 bằng **gate 10 bps**. Nhưng **r344 và r345 là gate run**, mà đường gate **không có risk layer** → **gate đó không thể nổ trong chúng**. **Rút lại quy kết đó.** **r349 và r350 vẫn đứng** (dùng plain `--json`, nơi risk layer **có** hoạt động; r349 đo trực tiếp 102 → 3). Điều này làm arc **mạch lạc hơn**: r350 kết luận **độ dốc chi phí** giải thích chuyển động (Δ = −0,13), và r349 cô lập **đường phản hồi không-qua-gate** trên chính ledger `legacy_selected_rule` — **đường gate chính là ledger đó**.

**Giới hạn**: **không** khẳng định kết luận gate là **sai** — ảnh hưởng PnL ≤3,8% nên kết luận **mức dấu** và **biên độ lớn** không đổi; cái đổi là **chúng mô tả cấu hình nào**, và `trades_per_week` từ gate **thổi phồng** tần suất deployed. **Không** khẳng định mức giảm 21,1% ở @300 chuyển sang cửa sổ khác (ở hai cửa sổ sâu chỉ ~3%; tôi có **ba điểm**). **Không** khẳng định cấu hình deployed sẽ chấm điểm tốt hay xấu **trên gate** — **không chấm được**, hai flag xung đột theo thiết kế, cần sửa code. **Không promote.**

Chi tiết: `research/quant/rounds/round356-DATA-ISSUE-the-daily-profit-gate-omits-the-construction-guard-and-the-risk-layer-so-it-scores-a-different-configuration.md`.

## Round 355 — REJECTED: hướng "theo thứ" **đóng lại**. Permutation test cho *"có thứ nào đó âm ở cả ba phần ba rời nhau"* ra **p = 0,60** — chuyện đó xảy ra ngẫu nhiên **sáu lần trên mười**. Wednesday ra **p = 0,0532**, **trượt** ngưỡng tôi đã đăng ký; Friday **p = 0,20**

**Áp đúng bài học của chính loop trước khi đăng ký.** Quy tắc từ r327: **tính phân phối hoán vị trước khi chốt ngưỡng, và tính luôn multiplicity vào**. Bằng chứng của r353 có hai phần, nên cả hai được biến thành thống kê **đã tính giá của việc chọn lựa**:
- **S1** — **giá trị nhỏ nhất** trong năm mean theo thứ (dùng "min", **không** gọi tên Wednesday, để tính vào việc Wednesday **được chọn** là tệ nhất trong năm);
- **S2** — *"có thứ nào đó âm ở cả ba phần ba rời nhau"*, đúng thứ r353 đã báo cáo.

Hoán vị: xáo nhãn thứ trên 257 dòng ngày giao dịch của `exness XAU` @1800, giữ nguyên số ngày mỗi thứ, **N = 20.000**. **Đăng ký trước phân hoạch**: **p < 0,05** → không phải ngẫu nhiên; **p ≥ 0,05** → là ngẫu nhiên, **hướng đóng lại**.

Mean quan sát: Mon −0,00062 · Tue −0,00473 · **Wed −0,01603** · Thu +0,00474 · **Fri +0,01043**.

| thống kê | quan sát | **p** |
|---|---|---|
| min mean theo thứ ≤ Wednesday | −0,01603 | **0,0532** |
| max mean theo thứ ≥ Friday | +0,01043 | **0,1996** |
| **có thứ âm ở cả ba phần ba** | đúng | **0,6013** |

**S2 vô giá trị.** Headline của r353 — Wednesday âm ở cả ba phần ba rời nhau, biên độ ổn định — **xuất hiện ở 60% các lần xáo ngẫu nhiên**. Số học dễ hiểu khi nói ra: mean ngày tổng thể hơi âm nên mỗi thứ âm trong một phần ba với xác suất hơn ½ → ≈0,5³ mỗi thứ, và ≈1 − (1−0,125)⁵ ≈ 0,5 trên năm thứ. **Cấu trúc "ba giai đoạn rời nhau cùng đồng thuận" — thứ làm phát hiện có vẻ chắc — hầu như không mang thông tin.**

**S1 trượt ngưỡng đã đăng ký**: p = 0,0532 ≥ 0,05. Tôi đã đăng ký 0,05 và **nó không đạt** — "sát ngưỡng" **không phải kết quả**.

**Multiplicity đã tốn đúng bao nhiêu**: test Wednesday **theo tên**, bỏ qua việc nó được chọn là tệ nhất trong năm, cho **p = 0,0112** — trông "có ý nghĩa" rõ ràng. Con số trung thực có hiệu chỉnh là **0,0532**. **Bỏ qua multiplicity sẽ làm p nhỏ đi 4,8 lần và lật ngược phán quyết.**

**Hướng này đóng lại.** Ba tuyến độc lập cùng chỉ một chiều: (1) r354 — mẫu hình **đảo ngược** trên hai route BTC; (2) vòng này — bằng chứng cấu trúc **vô giá trị**, bằng chứng biên độ **trượt ngưỡng**; (3) ngay cả nếu đạt cũng **chưa bao giờ khả thi** — CLI **không có bộ lọc theo thứ**, **gross theo thứ không lấy được** (r354), và route **gate-ineligible** ở mọi cửa sổ. Số liệu của r352–r353 **vẫn đứng như phép đo**; **diễn giải** thì không sống sót qua một test có tính giá của cách chọn giả thuyết.

**Giới hạn**: **không** khẳng định **không có** hiệu ứng theo thứ — p = 0,0532 là **không bác bỏ được**, không phải bằng chứng vắng mặt, và 257 dòng là mẫu nhỏ; cái xác lập được là **bằng chứng này không đủ đỡ cho khẳng định đó**. **Không** khẳng định null hoán vị là chính xác tuyệt đối — xáo nhãn giả định PnL ngày **khả hoán** giữa các thứ; tự tương quan chuỗi sẽ làm p **lớn hơn**, không nhỏ hơn, nên xấp xỉ đó **không cứu** được kết quả. **Không promote.**

Chi tiết: `research/quant/rounds/round355-REJECTED-the-weekday-lead-closes-a-permutation-test-puts-negative-in-all-three-thirds-at-p-0-60.md`.

## Round 354 — REJECTED: mẫu hình theo thứ **đảo ngược** trên hai route BTC — Wednesday từ **tệ nhất** thành **tốt nhất**, Friday từ **tốt nhất** thành **tệ nhất**. Tiêu chí tôi đăng ký **bắn trúng nhưng vô nghĩa**. Riêng phần Wednesday: có vẻ do **edge**, không phải chi phí

**Phần 1 — câu hỏi Round 353 nói là quyết định.** `daily_results` mang `realized_pnl` là **net**, nên Wednesday **âm edge** hay chỉ **đắt hơn**? Đưa chi phí về 0 sẽ cho gross theo ngày, **nhưng** Round 348 đã xác lập `(fee + slippage) × 2 > 10` chính là thứ chặn lệnh đảo chiều → **mọi mức chi phí đủ thấp để cô lập gross đều làm đổi không gian hành động**. **Gross theo thứ với luồng quyết định deployed là không lấy được** — tôi ghi nhận rào cản đó thay vì lách ẩu.

Thứ **lấy được** là proxy hoạt động (ngày có `realized_pnl == 0` là ngày không đóng lệnh nào). **Đăng ký trước phân hoạch**: `A_wed ≥ A_other × 1,15` → chi phí còn là lời giải; `<` → **nghiêng về âm edge**.

| thứ | n | active | tỷ lệ | mean \|PnL\| ngày active | thắng | thua |
|---|---|---|---|---|---|---|
| Mon | 51 | 44 | 0,863 | 0,04243 | 22 | 22 |
| **Wed** | 51 | 42 | **0,824** | **0,04699** | **18** | **24** |
| Thu | 52 | 44 | 0,846 | 0,02397 | 27 | 17 |
| Fri | 52 | 44 | 0,846 | 0,05074 | 24 | 20 |

**A_wed = 0,8235 < 0,9714 → nhánh "âm edge" xảy ra.** Wednesday **ít hoạt động hơn** trung bình, win rate theo ngày **0,429 so với 0,540**, biên độ **lớn hơn 1,20 lần**. **Ít thắng, biên độ lớn, hoạt động như nhau** — câu chuyện hướng, không phải chi phí.

**Phần 2 — test cross-route thật sự "mới", và vì sao tiêu chí của tôi vô giá trị.** Giả thuyết Wednesday sinh ra **chỉ từ `exness XAU`**, nên áp lên route chưa từng dùng để hình thành nó **là** test mới — đúng thứ Round 353 nói còn thiếu.

| route | Mon | Tue | Wed | Thu | Fri | tốt nhất | tệ nhất |
|---|---|---|---|---|---|---|---|
| `exness XAU` | −0,00062 | −0,00473 | **−0,01603** | +0,00474 | **+0,01043** | **Fri** | **Wed** |
| `exness BTC` | −0,02337 | −0,01260 | **−0,01196** | −0,02867 | **−0,04116** | **Wed** | **Fri** |
| `binance BTC` | −0,01653 | −0,01026 | **−0,01148** | −0,03125 | **−0,04547** | Tue | **Fri** |

Wednesday âm ở cả hai route BTC → **tiêu chí đăng ký bắn "systematic"**. **Nhưng nó vô nghĩa**: **mọi** thứ đều âm ở cả hai route BTC — chúng lỗ toàn cục (net −6,6188 và −6,4102, trên **gross âm** −2,2161 và −1,9930). **Một tiêu chí mà bất kỳ route toàn-âm nào cũng đạt thì không phân biệt được gì.** Tôi **đã đăng ký một test không thể trượt ở nơi nó được áp dụng** — **lỗi pre-registration thứ tư** của loop (sau r327 p-value chưa tính, r330 sai biến, r340 hở khoảng).

**So sánh có khả năng phân biệt thì bác bỏ tính chuyển giao**: xếp hạng trong từng route, Wednesday **tệ nhất** trên `exness XAU` nhưng **tốt nhất/nhì** trên cả hai route BTC; Friday **tốt nhất** trên `exness XAU` nhưng **tệ nhất** trên cả hai BTC. **Mẫu hình không chuyển giao — nó đảo ngược.** Vậy cấu trúc theo thứ của `exness XAU` **không phải** artifact hệ thống của Portfolio; nó **đặc thù route, hoặc là nhiễu**.

**Phần 3 — L3 của audit đã định lượng.** `exness XAU` @1800: **49 bucket thứ Bảy, 47 (95,9%) đúng bằng 0**; toàn bộ **88/306 dòng (28,8%) bằng 0**. `positive_day_ratio` = **0,37255** (114/306); **bỏ bucket thứ Bảy** → **0,43580** (112/257) → **riêng bucket Sat kéo tụt chỉ số 0,06325**, khoảng **17%** giá trị báo cáo, so với ngưỡng 0,55. Ngưỡng được viết cho instrument giao dịch mọi ngày; với instrument theo phiên, nó áp lên mẫu số **độn thêm các bucket rỗng có cấu trúc**.

**Giới hạn**: **không** khẳng định Wednesday là âm edge — proxy **thô** (ngày non-zero có thể 1 hay 5 lệnh) và win rate là **theo ngày, không theo lệnh**; **gross theo thứ vẫn không lấy được** nên câu hỏi Round 353 gọi là quyết định **vẫn mở**. **Không** khẳng định hai route BTC **bác bỏ** hiệu ứng theo thứ trên `exness XAU` — chúng chỉ cho thấy **không chuyển giao**, mà "đặc thù route" và "nhiễu" **đều** dự đoán điều đó. **Không promote.**

Chi tiết: `research/quant/rounds/round354-REJECTED-the-weekday-pattern-inverts-on-btc-routes-and-my-registered-criterion-was-vacuous.md`.

## Round 353 — NEEDS-MORE-RESEARCH: **Wednesday âm ở cả ba phần ba rời nhau** của một holdout 306 ngày, ổn định ở −0,019 / −0,015 / −0,014 mỗi ngày — **20,3 lần** mức trung bình. Cả hai giả thuyết đăng ký trước đều tái lập. Nhưng **không giả thuyết nào là "mới"**, và đó là trần của phát hiện này

**Lấy được giai đoạn rời nhau sau khi Round 352 nói là bất khả thi.** Round 352 đúng **giữa các run** — mọi holdout kết thúc ở "now" nên không hai giá trị `--days` nào cho giai đoạn OOS rời nhau. **Nhưng trong MỘT run thì có**: mảng `daily_results` của một replay duy nhất chia được thành các đoạn rời nhau, và vì là **cùng một replay** nên các giá trị **nhất quán nội bộ** — điều mà Round 343 đã chứng minh là **không** đúng giữa các run. `exness XAU` @1800 cho holdout 306 ngày → **ba phần ba rời nhau, mỗi phần 102 ngày**, từ một phép tính nhất quán.

**Đăng ký trước hai phân hoạch**, đều **nghiêm ngặt, đơn giả thuyết** (tiêu chí tổng hợp của r352 đã **che mất** một lần đổi dấu, nên lần này **không tổng hợp**): **H1** — thứ có mean PnL **cao nhất** ở phần ba 1 phải **dương** ở **cả** phần ba 2 **và** 3. **H2** — **Wednesday** phải **âm** ở **cả** phần ba 2 và 3.

| thứ | phần ba 1 | phần ba 2 | phần ba 3 | ổn định? |
|---|---|---|---|---|
| Mon | −0,00734 | **+0,01795** | −0,01246 | không — đổi dấu hai lần |
| Tue | −0,01350 | +0,00053 | −0,00121 | không |
| **Wed** | **−0,01895** | **−0,01486** | **−0,01428** | **có — âm cả ba** |
| Thu | −0,00901 | +0,00884 | +0,01413 | không — đổi dấu |
| **Fri** | **+0,00057** | **+0,00829** | **+0,02176** | **có — dương cả ba** |
| Sat\* | +0,00055 | +0,00316 | 0,00000 | — |

\* đuôi UTC+7 của phiên thứ Sáu (audit L3), không phải ngày giao dịch.

**H1 tái lập** (Friday, dương ở cả hai phần ba sau). **H2 tái lập** — và Wednesday còn âm ở cả phần ba 1, nên **cả ba giai đoạn rời nhau đều đồng thuận với biên độ ổn định đáng kể**. **Chỉ Wednesday và Friday ổn định**; Monday và Thursday đều đổi dấu.

**Độ lớn**: Wednesday chiếm 51/306 ngày (16,7%) nhưng gánh **−0,81767** trong một holdout có **net tổng −0,24159**; mean ngày **−0,016033** so với tổng thể **−0,000790** → **tệ hơn 20,3 lần**. Về số học, holdout bỏ Wednesday cộng lại là **+0,57608**. **Đó là phép tính kế toán, KHÔNG phải backtest** — đúng lý do Round 340 đã nêu. Khác với r340 ở chỗ **tập con được nêu tên TRƯỚC và kiểm chứng trên hai giai đoạn rời nhau nữa**.

**Trần của phát hiện — không giả thuyết nào "mới"**:

| giai đoạn | Round 352 đã nhìn chưa? |
|---|---|
| phần ba 1 (2025-09-04 → 2025-12-31) | **một phần** — chỉ 2025-09-04 → 2025-11-02 nằm ngoài holdout @1500 |
| phần ba 2 (2026-01-01 → 2026-04-30) | **rồi** — nằm trong @1200/@1500/@1800 |
| phần ba 3 (2026-05-01 → 2026-08-29) | **rồi** — nằm trong tất cả |

**H2 tồn tại vì Round 352 quan sát Wednesday tệ nhất — trên chính các bảng đã phủ phần ba 2 và 3.** Nên **thiết kế đúng, nhưng dữ liệu không out-of-sample so với giả thuyết**. Test sạch cần giả thuyết cố định **trước khi** nhìn ngày kiểm chứng — **không dựng lại được hồi tố, chỉ làm được tiến cứu trên những ngày chưa tồn tại**.

Và ngay cả kết quả sạch cũng **không promote được từ đây**: **CLI không có bộ lọc theo thứ** nên ứng viên **không chạy được đầu-cuối nếu không sửa code**, và `exness XAU` **vẫn gate-ineligible** ở mọi cửa sổ.

**Giới hạn**: **không** khẳng định đây là kết quả out-of-sample. **Không** khẳng định bỏ Wednesday sẽ cho +0,57608 — bỏ một ngày là bỏ các lệnh của nó, làm đổi trạng thái Portfolio về sau (r349: chặn một hành động **không** đơn giản là trừ nó đi). **Không** khẳng định gì về **gross theo thứ**: `daily_results` mang `realized_pnl` là **net**, nên **không xác định được** Wednesday là **âm edge** hay chỉ **đắt hơn** — **và chính phân biệt đó quyết định bộ lọc có ích hay không**. **Không** có nguyên nhân nào được kiểm tra. **Không promote.**

Chi tiết: `research/quant/rounds/round353-NEEDS-MORE-RESEARCH-wednesday-is-negative-in-three-disjoint-periods-but-the-hypothesis-was-not-fresh.md`.

## Round 352 — NEEDS-MORE-RESEARCH: **mọi holdout của cả arc đều lồng nhau** — tất cả kết thúc cùng một ngày và cửa sổ lớn hơn **chứa trọn** cửa sổ nhỏ hơn. Nên "tái lập qua nhiều cửa sổ" chưa bao giờ là bằng chứng độc lập. Phép chia theo thứ **đạt** tiêu chí đã đăng ký, nhưng **chỉ một nửa** tái lập

**Câu hỏi.** Ràng buộc quyết định trên `exness XAU` là gross chỉ bằng 60–88% chi phí. Nếu edge **tập trung** ở một số phiên nhất định thì một bộ lọc thời gian sẽ **cắt lệnh — và cắt chi phí — mà vẫn giữ phần lớn gross**. Đó là dạng lever duy nhất arc chưa thử, và đúng dạng có thể lấp khoảng 13%. Chọn thứ trong tuần từ chính dữ liệu đo là p-hacking, nên thiết kế được cố định trước.

**Đăng ký trước dạng phân hoạch** trên `exness XAU` @1200 (holdout 202 ngày): **phát hiện** ở nửa đầu những thứ có mean PnL dương; rồi ở **nửa sau**, mean PnL của tập đã chọn **> 0** → tái lập; **≤ 0** → nhiễu.

| thứ | n | sum A | mean A | **sum B** | mean B |
|---|---|---|---|---|---|
| Mon | 17 | +0,15138 | **+0,00890** | **−0,20063** | −0,01180 |
| Tue | 17 | −0,09391 | −0,00552 | +0,03464 | +0,00204 |
| Wed | 17 | −0,34699 | −0,02041 | −0,14885 | −0,00876 |
| Thu | 17 | −0,04285 | −0,00252 | −0,03404 | −0,00200 |
| Fri | 17 | +0,07437 | **+0,00437** | **+0,26986** | +0,01587 |
| Sat\* | 16 | −0,06658 | −0,00416 | −0,05640 | −0,00353 |

\* là **đuôi UTC+7 của phiên thứ Sáu** (audit L3), không phải ngày giao dịch.

Nửa A chọn **{Mon, Fri}**; ở nửa B tập đó cho n=34, sum **+0,06924**, mean **+0,002036 > 0** → **tiêu chí đã đăng ký ĐẠT**. **Nhưng đạt trên tổng hợp trong khi một nửa thành viên thất bại**: Friday +0,07437 → **+0,26986**, còn **Monday +0,15138 → −0,20063, đổi dấu**. Tập tái lập vì **Friday lấn át Monday**, không phải vì mẫu hình giữ được. Và bước phát hiện **không có ý nghĩa thống kê**: với 6 ô và n=17, **khoảng ba ô dương là kỳ vọng dưới giả thuyết null**.

**Cái sống sót, và cái giết nó.** Friday dương ở **cả bốn** lát, Wednesday âm ở **cả bốn** (và Wednesday nhất quán hơn — luôn là thứ tệ nhất). **Nhưng đây không phải bốn mẫu.**

| cửa sổ | holdout |
|---|---|
| @300 | 2026-07-01 → 2026-08-28 |
| @900 | 2026-03-04 → 2026-08-28 |
| @1200 | 2026-01-02 → 2026-08-28 |
| @1500 | 2025-11-03 → 2026-08-28 |
| @1800 | 2025-09-03 → 2026-08-28 |

**Mọi holdout kết thúc cùng ngày, và cửa sổ lớn hơn chứa trọn mọi cửa sổ nhỏ hơn — lồng nhau hoàn toàn.** Hai giá trị `--days` **không bao giờ** cho hai giai đoạn out-of-sample rời nhau, vì holdout luôn là phần đuôi của cửa sổ kết thúc ở "now", và CLI **không có flag as-of/end-date**.

**Hệ quả cho cả arc**: mọi khẳng định xuyên cửa sổ ở r331–r351 đều dựa trên **mẫu lồng nhau**. Kết luận về **tính mong manh theo cửa sổ vẫn đứng** (một tập cha hành xử khác **là** thông tin thật). Nhưng ngôn ngữ về **tái lập** thì **yếu hơn vẻ ngoài** — dữ liệu gần đây nằm trong **mọi** mẫu nên sự đồng thuận **một phần là tất yếu**. Chính headline r343 của tôi cần đọc lại theo nghĩa đó; đã prepend banner.

**Một kết quả phụ không được đọc quá lên**: `exness XAU` **@1500 có net dương ở chi phí deployed** — gross +0,95498, cost 0,72778, **net +0,22720**, cost÷gross **0,7621**, Sharpe +0,3424, Sortino +0,5401 — **run gate đầu tiên có lãi ở chi phí deployed trong cả arc**. Nhưng: **một trên sáu cửa sổ**, holdout **chứa** mọi cửa sổ nhỏ hơn, và **vẫn trượt sáu check**: `minimum_trades_per_week` (**2,814** so với 7,0 — hụt 2,5 lần), ngày dương 0,373, median 0,0, Sortino 0,540, Sharpe 0,342, cost÷gross 0,762 so với 0,5 — cộng bảy check continuity khiến route **vốn không gate-eligible**. Cửa sổ sâu kề bên **@1800 là net −0,24159**, cost÷gross 1,4353.

Gross vẫn **dương ở cả sáu** cửa sổ (+0,3391 / +0,6000 / +0,7820 / +0,7300 / **+0,9550** / +0,5550) — đó là phát biểu bền, nay kèm cảnh báo lồng mẫu.

**Giới hạn**: **không** khẳng định lọc theo Friday hay loại Wednesday sẽ có ích — Friday đo trên mẫu lồng nhau, **không hiệu chỉnh** cho việc đã chọn từ 6 ô, và **Wednesday chưa bao giờ được đăng ký trước**. **Không** khẳng định bốn cửa sổ chứng thực lẫn nhau. **Không** khẳng định @1500 có ý nghĩa ngoài cửa sổ đó. Các bucket không phải ngày giao dịch (UTC+7 cắt phiên thứ Sáu). **Không promote.**

Chi tiết: `research/quant/rounds/round352-NEEDS-MORE-RESEARCH-every-holdout-in-this-arc-is-nested-so-no-two-windows-are-independent-and-the-weekday-signal-is-half-replicated.md`.

## Round 351 — DATA-ISSUE: `--interval` **không** đổi decision interval của Portfolio — nó **hardcode `"5m"`**. Run `--interval 30m` tái lập baseline 5m **bit-for-bit**, vừa là bằng chứng vừa là một kiểm tra **tính tất định** miễn phí

**Lever tôi định thử.** Chi phí là ràng buộc quyết định trên `exness XAU` và mọi lever cấu trúc đã đóng; **một trục chưa từng chạm**: cả arc đều chạy decision interval 5m. Horizon dài hơn nghĩa là **ít quyết định hơn, mỗi quyết định lớn hơn** — đúng thứ một chiến lược bị chi phí bó cần.

**Đăng ký trước dạng phân hoạch**: **K** = `cost_to_gross_pnl_ratio` ở `--interval 15m`; **K < 1,1338** (giá trị 5m cùng cửa sổ) → cải thiện ràng buộc; **K ≥ 1,1338** → không.

**Kết quả — can thiệp chưa từng được áp dụng.**

| run | nến holdout | lệnh | gross | cost | net | **cost÷gross** |
|---|---|---|---|---|---|---|
| 5m (baseline r343) | 11.598 | 42 | 0,33907440711283554 | 0,38445248744791927 | −0,04537808033508374 | **1,1338** |
| **30m** | **11.598** | **42** | **0,33907440711283554** | **0,38445248744791927** | **−0,04537808033508374** | **1,1338** |
| 15m | 11.595 | 42 | 0,33543718157929480 | 0,38445576196952630 | −0,04901858039023151 | 1,1461 |

**Run `--interval 30m` trùng baseline 5m ở cả 20 trường metric, toàn bộ mảng `daily_results`, và cửa sổ holdout.** Hai run chạy ở **hai vòng khác nhau, thời điểm khác nhau**, khớp tới **17 chữ số có nghĩa** — không phải trùng hợp, mà **là cùng một phép tính**.

**Code nói vì sao**: `main.rs` truyền **chuỗi literal `"5m"`** vào đường Portfolio — `replay_portfolio_decisions(..., "5m", ...)` `:577`, gate `:612`, gate klines `:599`, `compare_real_portfolio_with_funding(..., "5m", ...)` `:634` — **không bao giờ** `args.interval`; và `portfolio_decision_replay.rs:246-250` **hard-error** với mọi giá trị khác. `--interval` (mặc định `5m`, `main.rs:185`) **chỉ** tới bảng sweep Alpha. **Decision interval của Portfolio không cấu hình được từ CLI.**

→ Nhánh đăng ký trước **về hình thức có xảy ra** (K(15m) = 1,1461 ≥ 1,1338) **và nó vô hiệu**: run 15m cũng không test 15m; holdout ngắn hơn 3 nến là **hiệu ứng lề của việc chọn cửa sổ** làm nhiễu **chính cái replay 5m** đó. Tôi **không** truy nguồn gốc dịch chuyển đó và **không** báo 1,1461 như một kết quả về decision interval.

**Sản phẩm phụ đáng giá hơn phép thử ban đầu.** Hai run, khác vòng, khác thời điểm, **cùng cửa sổ dữ liệu** → **output trùng tới 17 chữ số ở mọi trường và cả 51 dòng daily**. **Replay tất định bit-for-bit với cùng cửa sổ đầu vào.**

Điều đó đổi cách arc đọc chính số liệu của mình: **mọi khác biệt giữa các cấu hình ở r330–r350 đều là phản ứng thật với thay đổi đầu vào thật, không phải nhiễu giữa các lần chạy.** **Không có sàn "nhiễu cấu hình" do phi tất định** — cách nói ±0,28 ở r339 và "nhạy hỗn loạn" ở r345 là về **độ nhạy với đầu vào**, **không** phải ngẫu nhiên; đây là lần đầu hai khái niệm đó tách bạch. Hệ quả: **đo lặp một cấu hình y hệt là vô ích** — muốn dò tính ổn định thì phải đổi đầu vào, đúng như khung mà r348 dùng.

**Giới hạn**: **không** khẳng định gì về decision interval dài hơn — **chưa test và không test được từ CLI**, guard hard-error nên cần sửa code. **Không** biết vì sao `--interval 15m` dịch holdout 3 nến — **chưa điều tra**. **Không** khẳng định tính tất định giữ qua các phiên bản code/image (cùng một build `finance-research-local:latest`, **rebuild chưa test**). **Không** khẳng định tất định nghĩa là **chính xác** — nó nghĩa là **tái lập được**, và các giới hạn fidelity trong hai audit **không đổi**. **Không promote.**

Chi tiết: `research/quant/rounds/round351-DATA-ISSUE-the-interval-flag-does-not-change-the-portfolio-decision-interval-and-the-replay-is-bit-for-bit-deterministic.md`.

## Round 350 — REJECTED: mở khoá lệnh đảo chiều **không** giải thích mức tăng 31% của Round 349. Thang chi phí trên **nhánh bị chặn** cho thấy mức tăng là **độ dốc chi phí**, còn việc vượt gate — nếu có tác dụng gì — thì làm **tệ đi** khoảng 0,13–0,18. Nhưng thiết kế **không phân giải nổi** hiệu ứng nhỏ như vậy

Round 349 không tách được "rẻ hơn" khỏi "được phép đảo chiều" vì `--slippage-bps 0` đổi cả hai, và CLI không có flag `max_total_cost_bps`. **Có cách vòng qua mà không cần sửa code**: gate từ chối khi `(fee + slippage) × 2 > 10`, nên giữ `--fee-bps 5` thì chi phí đảo chiều **chỉ vượt trần giữa slippage 0,5 và 0**. Ba điểm còn lại do đó đo **độ dốc chi phí thuần với không gian hành động giữ nguyên**.

**Đăng ký trước dạng phân hoạch**: Δ = (PnL unlocked thực tế) − (ngoại suy tuyến tính từ nhánh bị chặn tới 5,0 bps); **|Δ| ≥ 0,15** → vượt gate là bước nhảy **đáng kể**; **|Δ| < 0,15** → **độ dốc chi phí đủ giải thích**.

| slippage | tổng bps | gate | từ chối | lệnh | **`one_target` PnL** | legacy (**ngoài gate**) |
|---|---|---|---|---|---|---|
| 2,0 | 7,0 | chặn | 102 | 280 | −1,32216 | −1,32799 |
| 1,0 | 6,0 | chặn | 96 | 273 | −1,08032 | −0,75172 |
| 0,5 | 5,5 | chặn | 97 | 272 | −0,90624 | −0,72084 |
| **0,0** | **5,0** | **mở** | **3** | 277 | **−0,91662** | −0,83321 |

Số lần từ chối **xác nhận thiết kế**: 102/96/97 khi chặn, **3** khi mở.

Khớp tuyến tính nhánh chặn (đúng phương pháp đã đăng ký): độ dốc **−0,27222 PnL mỗi +1 bps**, dự báo **−0,78532** tại 5,0 bps. Thực tế **−0,91662** → **Δ = −0,13130 < 0,15** → nhánh *"độ dốc chi phí đủ giải thích"*.

**Và dấu mới là kết quả thật**: điểm unlocked **tệ hơn** xu hướng chặn dự báo. Mức tăng 31% từ slippage 2 → 0 của Round 349 là **hiệu ứng chi phí**; cho phép đảo chiều **trừ đi** khoảng 0,13 chứ không cộng thêm. Cách đọc từng gợi ra ở Round 349 — *"gate của production làm mất PnL"* — **bị bác bỏ về dấu**; theo bằng chứng này gate **hơi có tính bảo vệ**.

**Cảnh báo trung thực: kết quả này không phân giải được.**

| cách ngoại suy | dự báo tại 5,0 | Δ | phán quyết |
|---|---|---|---|
| khớp 3 điểm **(đã đăng ký)** | −0,78532 | **−0,13130** | dưới 0,15 |
| độ dốc cặp gần nhất (6,0 → 5,5) | −0,73216 | **−0,18446** | **bằng/trên** 0,15 |

Độ dốc từng cặp của chính nhánh chặn lệch nhau **44%** (−0,24184 với −0,34816 mỗi bps), nên ngoại suy 0,5 bps mang **sai số lớn hơn ngưỡng 0,15** tôi đã chọn. Tệ hơn: **ledger ngoài gate** dịch **−0,11237** qua đúng bước 0,5 → 0,0 và bản thân nó **không đơn điệu**. **Một hiệu ứng ~0,13 không tách được khỏi dao động phản hồi chi phí ~0,11 trên một ledger không hề có gate.**

**Vậy cái đứng vững là một cận**: vượt gate đáng khoảng **−0,13 đến −0,18**, **nhỏ** so với tổng dịch chuyển 0,4056 từ slippage 2 xuống 0, và **dấu không có lợi cho việc mở khoá**. Con số chính xác **vượt khả năng phân giải của thiết kế**, và run sạch vẫn cần flag `max_total_cost_bps` chưa tồn tại.

**Giới hạn**: **không** khẳng định vượt gate đáng **đúng** −0,13 — hai cách ngoại suy hợp lệ **kẹp hai bên** ngưỡng đã đăng ký, phát biểu trung thực là **một khoảng**. **Không** khẳng định cho phép đảo chiều là **có hại** — dấu âm ở cả hai cách nhưng biên độ nằm trong dao động của chính ledger ngoài gate; **"không có lợi" yếu hơn "có hại"**. **Không** khẳng định độ dốc chi phí là tuyến tính (lệch 44% qua 1,5 bps, ba điểm không xác lập được dạng hàm). Toàn bộ là `one_target` **toàn cửa sổ**, một route, một cửa sổ. **Không promote.**

Chi tiết: `research/quant/rounds/round350-REJECTED-unlocking-reversals-does-not-explain-the-gain-the-cost-slope-does-and-the-gate-if-anything-hurts.md`.

## Round 349 — NEEDS-MORE-RESEARCH: counter của chính replay cho thấy **102 lần từ chối `execution_cost` ở chi phí deployed, còn 3 khi lệnh đảo chiều vượt qua trần** — giảm 34 lần, xác nhận trực tiếp Round 348. Mở khoá gần như **không đổi số lệnh** nhưng cải thiện realized PnL **31%**, và **tôi không tách được** gate khỏi chi phí

Round 348 đóng lại với: *"replay sẽ nhận bao nhiêu lệnh đảo chiều nếu mở khoá… cần audit trail theo lệnh, tức L4, chưa serialize."* **Quá bi quan.** Output `--json` thường (không có gate) **có sẵn `risk_rejected_counts`** — bảng đếm từ chối theo từng gate lấy thẳng từ risk layer (`portfolio_measurement.rs:255`). **Không cần** per-trade trail để đếm từ chối.

**Đăng ký trước dạng phân hoạch**: **R** = số lần từ chối `execution_cost` replay ghi nhận trên `exness XAU` @300 ở chi phí deployed; **R ≥ 10** → lệnh đảo chiều là phần **đáng kể** và gate là yếu tố định hình bậc nhất; **R < 10** → hiếm, và chênh lệch PnL lớn ở r344–r345 phải đến từ thứ khác.

**R = 102 — nhánh "đáng kể" xảy ra.** `exness XAU` @300, band deployed, hold 36, **55.045 quyết định**, cùng cửa sổ, chỉ khác `--slippage-bps`:

| | deployed 5+2 bps<br>(đảo chiều **14,0** → chặn) | `--slippage-bps 0` → 5+0<br>(đảo chiều **10,0** → cho phép) |
|---|---|---|
| **từ chối `execution_cost`** | **102** | **3** |
| trên tổng quyết định | 0,19% | 0,01% |
| **trên số lệnh đã khớp** | **36%** | 1% |
| `one_target` lệnh | 280 | 277 |
| `one_target` realized PnL | **−1,3222** | **−0,9166** |
| `legacy_selected_rule` lệnh (**không qua gate**) | 355 | 338 |
| các gate khác | **0** | **0** |

**99/102 lần từ chối biến mất** khi chi phí đảo chiều rơi từ 14,0 xuống đúng 10,0 bps — cơ chế r348 **được xác nhận bằng chính counter của replay**. `execution_cost` là **gate duy nhất** từng nổ ở đây. Mẫu số đúng là **số lệnh, không phải số quyết định**: **một lệnh đảo chiều bị chặn cho mỗi ~3 lệnh khớp**.

**Hai điều thay đổi cách đọc cả arc**

1. **Gate là lever chất-lượng-hành-động, không phải lever tần suất**: mở khoá làm số lệnh đổi **chỉ −1,1%** (280 → 277) trong khi realized PnL cải thiện **31%**. Chặn một lệnh đảo chiều **không** loại bỏ một lệnh — Portfolio đơn giản **không hành động** ở quyết định đó. **Mọi kết quả về band và tần suất trong arc đều được đọc như thể số lệnh là lever**; ở đây số lệnh gần như đứng yên còn kết quả đổi một phần ba.
2. **Có một đường phản hồi chi phí thứ hai, không qua gate, và giờ đo được**: `legacy_selected_rule` chạy **ngoài** risk layer, vậy mà số lệnh vẫn đổi **355 → 338 (−4,8%)**. **Đó không thể là gate.** Đây chính là độ nhạy dư mà r345 tìm ra và r348 chưa giải thích — nay **cô lập được vào một ledger gate không hề chạm tới**.

**Điều tôi KHÔNG kết luận được, và đó mới là phần quan trọng**: nhánh mở khoá đổi **hai thứ cùng lúc** — slippage từ 2 bps xuống 0 (**rẻ hơn**) **và** lệnh đảo chiều được phép (**không gian hành động khác**). **Không thể quy 31% cải thiện PnL cho bên nào từ cặp run này.** Muốn tách phải có run **giữ chi phí ở mức deployed và nâng trần** — CLI có `--fee-bps`, `--slippage-bps` nhưng **không có flag cho `max_total_cost_bps`**, nên **thí nghiệm sạch không chạy được nếu không sửa code**. Đó là follow-up cụ thể. **Tôi đặc biệt KHÔNG khẳng định** gate `execution_cost` của production làm mất 31% PnL — cách đọc đó có sẵn trong bảng và **không được chứng minh**.

**Giới hạn**: **không** khẳng định 102 là số lệnh đảo chiều **được thử** — đó là số **lần từ chối được ghi**, và việc một quyết định có thể bị từ chối lặp lại qua nhiều nến liên tiếp thì **chưa test**; nếu có thì 102 **đếm thừa**. **Không** điều tra 3 lần từ chối còn lại ở `--slippage-bps 0` (đảo chiều ở đó đúng 10,0 bps, qua được phép so sánh chặt) — hiệu ứng precision/sizing là hợp lý nhưng **tôi không đoán**. **Không** so sánh con số toàn cửa sổ này với các vòng gate: `one_target` phủ trọn 300 ngày (280 lệnh) còn `--daily-profit-gate` phủ holdout 51 ngày (42 lệnh). **Không promote.**

Chi tiết: `research/quant/rounds/round349-NEEDS-MORE-RESEARCH-the-replay-blocks-102-reversals-at-deployed-costs-and-3-when-unlocked.md`.

## Round 348 — DATA-ISSUE: cờ chi phí không chỉ đổi chi phí, chúng **đẩy lệnh đảo chiều qua một gate 10 bps**. Một ngưỡng duy nhất giải thích Round 344, 345 và 346 — và **"Phân kỳ 2" của tôi là SAI**: replay **có** mô hình hoá gate này

**Trước hết, đính chính chính mình.** Audit observability ghi Phân kỳ 2: *"production áp gate `execution_cost` 10 bps… **replay không có gate này**."* **Sai.** `portfolio_measurement.rs:170-181` dựng `PortfolioRiskLayer` với `PortfolioRiskPolicy::widened_for_simulation(...)`, và hàm đó (`portfolio_risk.rs:272-307`) **chỉ** nới giới hạn notional/leverage — giữ nguyên `execution_cost.max_total_cost_bps = 10.0` (`:210`). `evaluate_historical` (`:411-417`) gọi `evaluate_execution_cost(&input, is_reversal)` mỗi khi target mở rủi ro mới (`:446-452`), và `execution_target(...)` trả `None` khi bị từ chối nên **không có gì được thực thi**. **Replay áp đúng trần 10 bps như production. Phân kỳ 2 bị rút lại.**

**Gate đó thực chất là gì.** Với `spread_cost_bps`/`market_impact_bps`/`latency_cost_bps` mặc định **= 0** (`:248-250`), chi phí dự phóng rút gọn thành `(fee_bps + slippage_bps) × leg_multiplier`, với **`leg_multiplier = 2` cho lệnh đảo chiều** (`:624, 643-648`), từ chối theo phép so sánh **chặt** `>` (`execution_cost.rs:243`). Chính comment trong policy nói thẳng: *"A reversal prices both legs and **is rejected at 14bps**"* (`:206-209`). Ở chi phí deployed: một chân = 7 bps → **qua**; **đảo chiều = 14 bps → bị từ chối**.

**Quan sát production xác nhận đây là hành vi *duy nhất* của gate** — trên mọi file `warn` còn lưu của cả sáu worker:

| route | file warn | **từ chối `execution_cost`** | chi phí dự phóng |
|---|---|---|---|
| `bybit BTC` | 7 | **213** | 14 bps |
| `binance BTC` | 8 | 87 | 14 bps |
| `exness BTC` | 2 | 66 | 14 bps |
| **`exness XAU`** | 6 | **3** | 14 bps |
| `bybit XAUT` | 2 | 0 | — |
| `binance XAU` | 8 | 0 | — |

**369 lần từ chối, tất cả đều đúng 14 bps** (biến thể 13,999999999999998 / 14,000000000000002 là nhiễu float của 2×7) — **không một lần nào ở giá trị khác**. Trên thực tế gate này là một luật **"không đảo chiều trực tiếp"**. Câu hỏi đăng ký trước — *`exness XAU` có bị từ chối `execution_cost` không?* — trả lời **có** (3 lần/6 ngày, so với nhịp giao dịch backtest ~0,7/ngày là **cùng bậc**) — nhưng vì replay cũng mô hình hoá gate, **phân kỳ mà câu hỏi đó kiểm tra không tồn tại.**

**Phần thưởng: một ngưỡng giải thích Round 344, 345 và 346.** Chi phí dự phóng tính từ `fee_bps`/`slippage_bps` — **đúng những cờ CLI phơi ra** — nên đổi chúng là **đẩy chi phí đảo chiều qua trần 10 bps**:

| run | fee + slip | **chi phí đảo chiều** | `> 10`? | đảo chiều | kết quả đo |
|---|---|---|---|---|---|
| deployed (r343) | 7 | **14,0** | có | **chặn** | 42 lệnh, net −0,0454 |
| r345 `--fee-bps 4.9` | 6,9 | 13,8 | có | chặn | 43 lệnh, net −0,0506 |
| **r345 `--fee-bps 3.0`** | 5 | **10,0** | **không** (`>` chặt) | **mở** | **38 lệnh, net +0,1442, Sharpe +0,93** |
| **r344 `--slippage-bps 0`** | 5 | **10,0** | **không** | **mở** | **38 lệnh, net +0,1315, Sharpe +0,91** |
| r344 `--fee-bps 0` | 2 | 4,0 | không | mở | 42 lệnh, gross +0,0718 |

**Hai run rơi đúng 10,0 bps — đi tới bằng hai cờ hoàn toàn khác nhau — cho cùng số lệnh (38) và net gần như trùng (+0,1442 và +0,1315)**; hai run trên trần thì giống nhau (42 và 43 lệnh, net −0,045 và −0,051). **Thang này không hỗn loạn, nó là hàm bậc thang với ngưỡng tại 10 bps.**

Điều này **đính chính Round 345**, vốn gọi replay là *"nhạy hỗn loạn"* dựa trên thang phí không đơn điệu: các bước nhảy lớn là **vượt ngưỡng rời rạc**, không phải hỗn loạn. Cái **còn lại** từ r345: fee 4,9 và fee 5,0 **đều** trên trần mà vẫn lệch một lệnh và 14,8% gross — **độ nhạy dư đó là thật và vẫn chưa giải thích được**.

Nó cũng **đọc lại** Round 344: *"slippage = 0 có lãi"* thực ra là *"slippage = 0 kéo chi phí đảo chiều xuống đúng trần, **mở khoá một chiến lược mà production không chạy được ở chi phí deployed**"*. (Ngoại lệ: `protective: none` +0,4069 của Round 346 chạy ở **chi phí deployed**, nên **không** do gate này; nó vẫn bị bác bỏ bằng cửa sổ 900 ngày.) **Ở chi phí deployed, chưa cấu hình nào từng có lãi trên bất kỳ route nào** — không đổi, và giờ hiểu rõ hơn.

**Giới hạn**: **không** khẳng định gate là cơ chế **duy nhất** — fee 4,9 và 5,0 đều trên trần mà vẫn khác, nên còn thứ khác, và việc r345 bác bỏ giả thuyết cổng dấu `alpha_performance_quality` **vẫn đứng**. **Không** khẳng định gate **chỉ có thể** từ chối lệnh đảo chiều — với spread/impact/latency khác 0 thì một chân cũng có thể vượt 10 bps; mọi lần từ chối **quan sát được** đều ở 14 bps nhưng đó là quan sát về **cấu hình hiện tại**, không phải chứng minh về gate. **Không** biết replay sẽ nhận bao nhiêu lệnh đảo chiều nếu mở khoá — cần audit trail theo lệnh, tức **L4**, chưa serialize. **Không promote.**

Chi tiết: `research/quant/rounds/round348-DATA-ISSUE-the-cost-flags-move-reversals-across-a-10bps-gate-which-explains-rounds-344-345-and-346.md`.

## Round 347 — NO-CHANGE: Binance sửa **74% nến 5m đã đóng**, nhưng mức thay đổi giá là **median 0,0000 bps**, tệ nhất **2,90 bps**. Phân kỳ 1 hạ cấp — và route mà cả arc dựa vào **không có lần sửa nào**

Audit observability để mở: *"biên độ chưa xác định — log không mang giá trước/sau"*. **Đăng ký trước dạng phân hoạch**: **D** = median `|Δclose|` (bps) giữa giá **live strategy đã dùng** và giá **Timescale lưu**, trên nến 5m `binance BTC`; **D ≥ 1 bps** → đáng kể so với 7 bps khứ hồi → **leo thang**; **D < 1 bps** → chỉ là hình thức → **hạ cấp**.

**Cách lấy biên độ mà không cần Kafka**: console consumer của broker bị từ chối trên cổng mà phiên read-only tiếp cận được, và đi sâu hơn sẽ thành **săn credential — ngoài phạm vi**. Nguồn sạch hơn đã có sẵn: worker live ghi event `Signal evaluated` mang **`price` strategy thực sự dùng**, và span cùng message mang `market.event.id` định danh nến. Join với `close_price` Timescale của đúng nến đó **chính là** delta trước/sau khi sửa. **Tự kiểm**: nếu căn nến lệch một nến thì delta sẽ ở mức **hàng chục bps** (một nhịp 5m của BTC); thực tế là **phần trăm của bps** → căn đúng.

**Kết quả** — 125 nến `binance BTC` 5m, 2026-08-30 00:00–17:30 UTC:

| thống kê | giá trị |
|---|---|
| **giống hệt (0 bps)** | **64 (51,2%)** |
| khác | 61 (48,8%) |
| **median \|Δ\|** | **0,0000 bps** |
| mean / p95 / **max** | 0,1806 / 1,4211 / **2,8955 bps** |
| ≥1,0 bps | 8 (6,4%) |
| ≥2,0 bps | 4 (3,2%) |
| **≥7,0 bps (chi phí khứ hồi)** | **0 (0,0%)** |

**D = 0,0000 bps → Phân kỳ 1 hạ xuống P3.**

**Đuôi không phải bằng không, và tôi không giả vờ ngược lại**: 6,4% nến lệch ≥1 bps và 3,2% lệch ≥2 bps — **cùng bậc với dòng slippage 2 bps deployed** — và Round 345 cho thấy replay biến nhiễu chi phí 1,4% thành thay đổi gross 15%, nên một nhiễu đầu vào **có hệ thống** cỡ này trên **khoảng một nửa** số nến Binance **không hiển nhiên là bỏ qua được**. Cái được xác lập là **một cận trên nằm dưới hẳn chi phí khứ hồi**, **không phải** sự vô hại.

**Tỷ lệ sửa theo interval (binance BTC, 2026-08-29)**: 5m **213/288 = 74,0%**; 15m 68,8%; 30m 68,8%; 1h 83,3%; 2h 75,0%; 4h 83,3%; 12h 50%; 1d 0%. Mỗi nến bị sửa **đúng một lần**. Toàn ngày: binance BTC **347**, binance XAU **154**, **0** ở bybit BTC / bybit XAUT / exness BTC / exness XAU.

**Vì sao điều này gần như không chạm tới arc**: **`exness XAU` — route duy nhất có gross dương và là chủ thể của Round 313–346 — không có lần sửa nào.** Phân kỳ chỉ giới hạn ở hai route Binance, mà **cả hai vốn đã trượt vì gross âm** (−1,7909 và −0,3442 ở band deployed, r342). **Không kết luận nào của arc dựa vào chúng.**

**Phân kỳ 2 vẫn nguyên và vẫn mở**: production áp gate `execution_cost` **10 bps** mà replay **không** mô hình hoá → production giao dịch tập target nhỏ hơn, rẻ hơn — và cái này **có** ảnh hưởng tới `exness XAU`.

**Giới hạn**: **không** khẳng định 48,8% là tỷ lệ sửa — mẫu của tôi là **nến có signal nổ**, không phải mọi nến; tỷ lệ từ log trên cùng route là **74,0%** ở 5m, **hai tổng thể khác nhau, không đánh đồng**. **Không** khẳng định live **luôn** dùng giá trước sửa — message nói evaluation bị chặn cho bản sửa, nhưng tôi chỉ đọc code path đủ để trích, **chưa xác minh** thứ tự bản sửa tới so với lúc phát signal theo từng nến. **Không** khẳng định gì về interval khác 5m, route khác `binance BTC`, hay ngày khác 2026-08-30 **về biên độ**. **Không promote.**

Chi tiết: `research/quant/rounds/round347-NO-CHANGE-binance-kline-revisions-are-real-but-median-zero-bps-with-a-2-9-bps-tail.md`.

## Audit tracing bằng observability — **log/metrics quan sát được xác nhận tính nhân quả**, và lộ ra **hai phân kỳ backtest-vs-live** mà đọc code không thấy

Theo yêu cầu người dùng: không chỉ trace bằng code mà dùng **log/metrics quan sát thật**. **Investigation only — không áp dụng gì.** Nguồn: ECS JSONL + OpenTelemetry span của **sáu worker route live**, cộng ECS event mà chính CLI backtest phát ra. Read-only toàn bộ, **không đọc/không in credential**. Đồng hồ host production lúc thu thập: **2026-08-30 17:48 UTC**.

**ĐẠT 1 — không look-ahead, đo từ trace production.** `exness XAU`, trọn ngày giao dịch 2026-08-28, **620 signal event** đủ **cả tám interval** (5m 348, 15m 126, 30m 70, 1h 40, 2h 22, 4h 10, 12h 2, 1d 2), nơi `market.event.id` **căn đúng mốc nến** (ms lệch trong interval = 0 cho cả 620):

| đại lượng | giá trị |
|---|---|
| signal phát **trước khi** nến đóng | **0 / 620** |
| lag (`@timestamp` − nến đóng), min | **+1,015 s** |
| median / p95 / max | +2,133 s / +5,012 s / +8,083 s |

**ĐẠT 2 — không thực thi trùng, không xử lý lại**: Kafka offset **tăng nghiêm ngặt trên cả tám topic** (0 bước không tăng); **245 `market.event.id` khác nhau, 0 cái nằm dưới hơn một `trace.id`**. Đây là **lần đầu** invariant an toàn giao dịch này được kiểm chứng **trên production** thay vì lập luận từ code.

**ĐẠT 3 — W3C trace context đúng chuẩn**: 620/620 `trace.id` đúng 32 ký tự, `span.id` đúng 16.

**ĐẠT 4 — lịch phiên đúng ở live**: `application.jsonl` của `exness XAU` **0 byte** từ 2026-08-29 00:00; thứ Bảy đó gold worker phát **0 event** trong khi năm route 24/7 phát 933–1893.

**ĐẠT 5 — toàn vẹn split, từ chính event backtest phát ra**: qua **24 run** đã lưu (r335–r346, đủ sáu route, cửa sổ 300–1200 ngày), **`train + validation + holdout == candle_count` chính xác ở cả 24** — phân hoạch 60/20/20, không chồng lấn, không rơi nến. Trước đây đây là giả định; giờ là quan sát. Và **L4 được xác nhận ở runtime**: CLI backtest phát **đúng một** ECS event mỗi run, **không** có event theo quyết định hay theo lệnh.

**PHÂN KỲ 1 — Binance sửa nến đã đóng; live chặn, backtest thì đọc bản đã sửa.** Warn event nguyên văn: *"Exchange revised a closed kline; matching history entry replaced and **strategy evaluation remains blocked for this revision**"*. Trọn ngày 2026-08-29, sáu route:

| route | app lines | **sửa nến** | risk reject |
|---|---|---|---|
| `binance BTC/USDT` perp | 1893 | **347** | 0 |
| `binance XAU/USDT` perp | 1009 | **154** | 0 |
| `bybit BTC/USDT` perp | 1031 | 0 | 3 |
| `bybit XAUT/USDT` spot | 933 | 0 | 0 |
| `exness BTC/USD` cfd | 1064 | 0 | 0 |
| `exness XAU/USD` cfd | 0 (đóng phiên) | 0 | 0 |

**Chỉ route Binance bị sửa nến** — Bybit và Exness bằng 0. **Live** thay entry lịch sử nhưng **chặn đánh giá strategy** cho bản sửa → strategy live hành động trên nến **trước khi sửa**; **replay** đọc Timescale, tức giá trị **sau khi sửa**. → **Backtest đánh giá trên những nến mà live cố tình từ chối đánh giá lại.** Giá đóng đã sửa mang thông tin đến **sau** khi nến đóng, nên đây là **look-ahead nhẹ trong backtest** — thứ đọc code không bao giờ thấy vì **code đúng, dữ liệu mới khác**. **Biên độ chưa xác định** (log không mang giá trước/sau). Đáng chú ý: **`exness XAU` — route duy nhất có gross dương — có 0 lần sửa.**

**PHÂN KỲ 2 — production có gate chi phí thực thi 10 bps mà replay không mô hình hoá.** Warn event nguyên văn: `gate=execution_cost`, `reason="projected execution cost is 14bps; maximum is 10bps"`, `rejected_count=73`. **Replay không có gate này** — nó tính phí/slippage/funding cho mọi lệnh nhưng **không bao giờ từ chối** một target vì quá đắt. → **Production giao dịch một tập target nhỏ hơn hẳn backtest, và những cái bị loại đúng là những cái đắt.** Điều này nặng hơn bình thường vì r313–r346 kết luận **chi phí là ràng buộc quyết định** trên route duy nhất có edge: backtest nhận đúng những lệnh đắt mà production từ chối → **thiên lệch theo hướng dễ dãi trên đúng trục mà nghiên cứu đang tối ưu**.

**DATA-ISSUE — `market.event.id` không cùng ngữ nghĩa giữa các broker.** Exness: suffix là **thời điểm mở nến**, căn **chính xác** (ms lệch = 0 cho cả 620). Binance: suffix hành xử như **timestamp phía đóng có jitter**, ms lệch **0–1444 ms** (mẫu `…BTC.USDT.4h.1788076800219`, lệch 219 ms). Đọc dữ liệu Binance theo quy ước Exness cho ra 518/528 event "trước khi nến đóng" với median −299,93 s — **artefact của quy ước sai, không phải look-ahead**; đọc theo quy ước của chính nó thì tệ nhất là **−0,43 s**, nằm trong jitter. **Tôi suýt báo một cảnh báo look-ahead sai vì đúng điều này** và ghi nhận lại: mọi phân tích nhân quả dựa trên trace **phải xác lập quy ước `market.event.id` theo từng broker** trước khi trừ timestamp.

**Giới hạn**: **không** có bằng chứng từ **metrics series** — VictoriaMetrics HTTP API có xác thực, tôi **không** tìm cách lấy credential, nên kiểm chứng decision-rate/counter qua `/metrics` **vẫn còn mở**. **Không** khẳng định kết quả backtest nào sai vì hai phân kỳ — chúng có hệ thống và có hướng nhưng **biên độ chưa đo**, và tôi **không điều chỉnh** kết quả cũ nào. **Không** khẳng định `rejected_count=73` là số theo ngày — nó đọc như counter tích lũy, cửa sổ không ghi trong event.

Chi tiết: `research/quant/audits/observability-trace-audit-production-logs-verify-causality-and-expose-two-backtest-live-divergences.md`.

## Audit tính đúng đắn backtest — **không tìm thấy look-ahead**; ba giới hạn thật, trong đó lớn nhất là **không có audit trail theo từng lệnh**

Theo yêu cầu người dùng: truy vết bằng tracing để kiểm chứng các rule (no look-ahead, …). **Investigation only — không áp dụng gì, không đề xuất fix.** Phương pháp: trace code toàn pipeline replay + kiểm chứng thực nghiệm trên tám gate run đã lưu + một truy vấn Timescale read-only phạm vi hẹp để xác nhận độc lập. **0 container.**

**ĐẠT — thứ tự nhân quả, không look-ahead**
1. `klines.rs:246` — chỉ nến `is_kline_closed` vào replay; nến đang hình thành không bao giờ sinh tín hiệu.
2. `portfolio_decision_replay.rs:59-67` — `replay_order` sắp theo **`close_time`** (không phải `open_time`), tie-break theo interval **tăng dần** → nến 4h chỉ vào luồng khi đã đóng, và khi 5m với 4h đóng cùng lúc thì **5m xử lý trước**. Base interval không bao giờ thấy nến khung lớn đóng cùng thời điểm — bảo thủ, đúng như worker live.
3. `multi_timeframe_trend_filter.rs:77-116` — dấu trend khung lớn chỉ được ghi khi một nến khung lớn **đã đóng** tới; nến base đọc **dấu đã lưu gần nhất**; giai đoạn warm-up trả `None` (*"absence of information, not agreement — suppress rather than guess"*). **Đúng cái bẫy look-ahead kinh điển của MTF và nó đã tránh được.**
4. `portfolio_decision_replay.rs:340-347` — `evidence.decide(primary.close_time)` chỉ chạy khi `evidence.is_synchronized(primary.close_time)`.
5. `portfolio_decision_replay.rs:317` — refit trọng số là **online từ hiệu năng quá khứ tích lũy**: phụ thuộc đường đi (r300), **không phải leakage**.
6. `trading_modes.rs:1919-1923` — **giá vào lệnh bất lợi, tại close của nến ra quyết định**: `Long => close × (1 + slippage)`, `Short => close × (1 − slippage)`. **Không bao giờ** dùng giá thuận lợi trong nến.
7. `trading_modes.rs:1745-1760` — thứ tự mỗi nến: `record_true_range` → `settle_funding` → `try_close_at_protective_level` → `apply_target`, nên check bảo vệ chạy trên vị thế **đang có** **trước** target mới → **vào-và-ra trong cùng một nến là bất khả thi về mặt cấu trúc**.
8. `trading_modes.rs:2153-2161` — nến chứa **cả** stop lẫn take thì `(true,_) => stop` kích hoạt: **lấy khoản lỗ**; nhánh lạc quan không tồn tại.

**ĐẠT — kiểm chứng thực nghiệm**
9. **Toàn vẹn kế toán trên 8 run, đủ sáu route**: `ending_equity[i] == starting_equity + cumsum(realized_pnl)[i]` với sai số tuyệt đối tối đa **1,3e-11** trên equity 1e4 (tương đối ~1e-15 — nhiễu float), và `Σ daily == net_realized_pnl` **chính xác** ở mọi run.
10. **Một cảnh báo đã được giải quyết bằng dữ liệu độc lập.** Gold CFD hiện PnL khác 0 vào **thứ Bảy** (2026-08-29, 2026-03-28, 2026-04-18, 2026-07-11, 2026-08-08, 2026-04-25, 2026-06-27, 2026-07-18 — đều là thứ Bảy), trong khi vàng đóng cửa cả cuối tuần. Truy vấn Timescale read-only: `exness XAU` có **0 nến 5m** vào **mọi** thứ Bảy đó, và thứ Sáu 2026-08-28 có **252 nến chạy 00:00 → 20:55 UTC**. Nguyên nhân ở `daily_profit_gate.rs:340,402`: gom ngày bằng `close_time.with_timezone(Asia/Ho_Chi_Minh)` (**UTC+7**) → nến đóng từ 17:00 UTC rơi sang ngày kế trong UTC+7. **Đúng hành vi theo timezone vận hành đã khai báo, không phải lỗi** — và nhất quán: 2026-08-28 (+0,09557) với 2026-08-29 (+0,09407) là hai nửa của **cùng một phiên thứ Sáu**. Đối chứng: `exness BTC` cũng là CFD nhưng có PnL ở **30/30** ngày cuối tuần, khớp phát hiện r337 rằng BTC/USD chạy 24/7 ở venue đó.

**Giới hạn tìm được — không cái nào là look-ahead**
- **L1 (P2) — fill bảo vệ bỏ qua rủi ro gap.** `trading_modes.rs:2143-2161` kích hoạt theo `low <= stop` / `high >= take` rồi fill **đúng bằng** giá stop/take. Nến **nhảy xuyên qua** mức đó thực tế sẽ fill tệ hơn nhiều. Đau nhất ở nơi gap mang tính cấu trúc — và `exness XAU`, **route duy nhất có gross dương**, **đóng cửa mỗi cuối tuần**. **Hệ quả: tail loss bị đánh giá thấp**, nên drawdown/streak đo được lạc quan một lượng **chưa định lượng**.
- **L2 (P3) — biên holdout không sạch về điểm vào.** 2/8 run (`exness XAU` @900, `binance XAU` @500) có PnL khác 0 ở **ngày 0** của holdout → vị thế mở trong giai đoạn train đóng bên trong holdout. **Không phải look-ahead**, nhưng PnL ngày đầu không quy về một quyết định thuần holdout.
- **L3 (P3) — gom ngày UTC+7 cắt phiên thứ Sáu của CFD thành hai "ngày"**, một trong đó chỉ vài giờ; `observed_days`, `positive_day_ratio`, `median_daily_pnl`, streak đều tính trên các bucket này → **gate áp ngưỡng theo ngày lên những ngày một phần**.
- **L4 (lỗ hổng công cụ — giới hạn lớn nhất cho kiểm chứng độc lập): output không có audit trail theo từng lệnh.** `portfolio_measurement.rs:23-28` chỉ phơi `ledgers/trades/realized_pnl/funding_paid`; `SimulatedTrade` (`trading_modes.rs:1548-1562`) có `entry_at`/`exit_at`/giá/`close_reason` nhưng **không bao giờ được serialize**. **Hệ quả: không thể đối soát fill với dữ liệu thị trường đầu-cuối nếu không sửa code** — toàn bộ mục 1–8 ở trên được kiểm chứng **bằng đọc code**, không phải bằng audit lệnh đã khớp.
- **L5 — selection bias ở mức quy trình**, nằm ngoài code: tham số deployed được chọn qua nhiều vòng dùng lại holdout chồng lấn. Không thay đổi code nào xử lý được điều này.

Checklist kiểm chứng cho người implement nằm trong báo cáo: `research/quant/audits/backtest-correctness-audit-look-ahead-and-fill-invariants.md`.

## Round 345 — REJECTED: phản hồi chi phí **không** phải ngưỡng đổi dấu. Cắt phí **0,1 bps** — 1,4% vòng khứ hồi — thêm một lệnh, đẩy gross **+14,8%**, làm **tăng** tổng chi phí, và net **xấu đi**. Replay **nhạy hỗn loạn** với tham số chi phí

Round 344 nêu đường phản hồi khả dĩ mà chưa test. Đọc `alpha_performance_quality` (`finance-core/src/trading_modes.rs:589-616`) cho một cấu trúc sắc nét: `empirical` **đúng bằng 0,0** trừ khi `realized_pnl > 0 && gross_profit > 0`, và chỉ **trên** cổng đó nó mới biến thiên liên tục. Vì mọi strategy đều đang lỗ ở chi phí deployed, quality thu về `1 − confidence` — hàm **thuần theo số lệnh** — nên một thay đổi chi phí **lẽ ra không làm gì** cho tới khi nó lật dấu realized PnL của một strategy nào đó.

**Đăng ký trước dạng phân hoạch**: `--fee-bps 4.9` (cắt 2% phí, **1,4%** của 7 bps, quá nhỏ để lật dấu) cho số lệnh **giống hệt** và gross **giống hệt** → phản hồi theo ngưỡng, cổng dấu là đường đi; **khác** ở số lệnh **hoặc** gross → phản hồi liên tục, cổng dấu không phải đường đi.

**Bác bỏ, và tệ hơn cả bác bỏ.** `exness XAU` `--days 300`, cùng holdout (2026-07-01 → 2026-08-28), band deployed:

| `--fee-bps` | lệnh | **gross** | cost | **net** | Sharpe |
|---|---|---|---|---|---|
| 5,0 (deployed) | 42 | 0,33907 | 0,38445 | −0,04538 | −0,2488 |
| **4,9** | **43** | **0,38909** | **0,43965** | **−0,05056** | −0,2850 |
| 3,0 | 38 | 0,33666 | 0,19244 | **+0,14423** | **+0,9307** |
| 0,0 | 42 | 0,07177 | 0,10812 | −0,03635 | −0,2595 |

Cắt phí **0,1 bps** thêm một lệnh (+2,4%), đẩy gross **+14,8%**, làm **tăng** tổng chi phí **+14,4%** dù đơn giá **thấp hơn**, và net **xấu đi 11,4%**. Và ánh xạ chi phí → kết quả **không đơn điệu**: net chạy **−0,04538 → −0,05056 → +0,14423 → −0,03635** ở 5,0 / 4,9 / 3,0 / 0,0 bps. **Thực thi rẻ hơn không làm kết quả tốt hơn**, và điểm có lãi nằm **giữa** thang với **cả hai đầu đều âm**.

**Cái giá cho phần còn lại của loop.** Replay khuếch đại nhiễu đầu vào **1,4%** thành **14,8%** thay đổi gross:
- **"Slippage bằng 0 thì có lãi" của Round 344 yếu hơn vẻ ngoài** — fee 3,0 cũng có lãi, còn fee 0,0 (**cắt chi phí nhiều hơn**) thì **không**. Một điểm có lãi trên thang chi phí **không** phải bằng chứng rằng giảm chi phí là hữu ích.
- **Chênh lệch cỡ này giữa các cấu hình không diễn giải được**: grid band tinh 500 ngày của Round 334 tách hai điểm tốt nhất bằng **0,018 net**, vai rãnh của Round 340 cũng tương tự — nằm gọn trong biên độ mà một nhiễu 1,4% tạo ra được. Round 334 **đã tự nêu** thứ tự tinh chưa xác lập; vòng này cấp **lý do**.
- Đây là đo **trên trục chi phí**. Tôi **chưa** chứng minh khuếch đại tương tự trên trục band hay trục `--days` → đây là **chỉ dấu để nghi ngờ chênh lệch nhỏ**, **không** phải cận nhiễu đã chứng minh cho các trục đó.

**Phát biểu duy nhất còn sạch và không đổi**: **gross của `exness XAU` dương ở mọi thiết lập chi phí và mọi cửa sổ đã đo** (Round 343). **Độ lớn** không ổn định tới 15%; **dấu** thì chưa bao giờ đổi.

**Giới hạn**: **không** khẳng định đường phản hồi thực sự — giả thuyết cổng dấu bị bác bỏ và tôi **chưa** xác lập cái thay thế; biến thiên liên tục của `confidence` qua số lệnh, hiệu ứng đường equity lên position sizing, và phụ thuộc đường đi thông thường đều là ứng viên; **chưa kiểm tra trọng số hay bản ghi performance từng strategy**. **Không** khẳng định mức khuếch đại là đồng nhất: **một route, một cửa sổ, một trục, bốn điểm**. **Không** khẳng định kết luận các vòng trước vô hiệu — phép đo vẫn đứng, kết luận **mức dấu** và **biên độ lớn** không bị ảnh hưởng; cái bị lung lay là **xếp hạng tinh giữa các cấu hình gần nhau**. **Không promote.**

Chi tiết: `research/quant/rounds/round345-REJECTED-the-cost-feedback-is-not-a-threshold-a-0-1-bps-fee-change-moves-gross-15-percent-and-the-replay-is-chaotic.md`.

## Round 344 — DATA-ISSUE: `--fee-bps` và `--slippage-bps` **thay đổi luồng quyết định**, nên **không** quy được chi phí về từng thành phần. Bằng chứng: bỏ phí giữ nguyên số lệnh 42 mà **gross — đại lượng đo TRƯỚC chi phí — giảm 79%**

Round 343 đo `exness XAU` @300 ở gross **+0,3391** với cost **0,3845** — chi phí bằng 113% gross, khoảng cách nhỏ nhất từng ghi nhận. Chi phí deployed: phí 5 bps, slippage 2 bps, funding 1 bps → slippage chiếm **28,6% số bps**. **Đăng ký trước dạng phân hoạch**: `--slippage-bps 0` cắt `total_cost_drag` **≥ 50%** → slippage chi phối; **< 50%** → không.

| run | lệnh | /tuần | **gross** | cost | **net** | Sharpe | Sortino | cost÷gross |
|---|---|---|---|---|---|---|---|---|
| deployed (5/2/1 bps) | 42 | 5,05 | +0,33907 | 0,38445 | −0,04538 | −0,249 | −0,374 | 1,134 |
| **`--slippage-bps 0`** | **38** | 4,57 | +0,33666 | **0,20521** | **+0,13146** | **+0,913** | **+1,592** | **0,610** |
| **`--fee-bps 0`** | 42 | 5,05 | **+0,07177** | 0,10812 | −0,03635 | −0,259 | −0,438 | 1,507 |

**Bỏ slippage cắt chi phí 46,6% — dưới mốc 50%, dự đoán bị bác bỏ** (dù vẫn cao hơn hẳn tỷ trọng 28,6% bps, nên slippage **đắt bất tương xứng**, chỉ là không vượt ngưỡng đã đăng ký).

**Nhưng không nhánh nào là phân rã sạch, và nhánh phí chứng minh điều đó.** Bỏ phí giữ số lệnh **đúng 42** mà `gross_pnl_before_costs` rơi từ **+0,33907 xuống +0,07177 — giảm 79% ở một đại lượng đo TRƯỚC khi tính chi phí**. Một tham số chi phí **không thể** làm đổi gross tiền-chi-phí trên cùng một tập lệnh → **đó không phải cùng những lệnh đó**: cùng số lượng, khác điểm vào/ra. Nhánh slippage còn rõ hơn: số lệnh dịch **42 → 38**.

**Cơ chế (r300)**: Portfolio refit trọng số interval và strategy **trên từng kline** từ Alpha performance tích lũy, và `alpha_performance_quality` xét `realized_pnl > 0 && gross_profit > 0` → **thực thi rẻ hơn làm nhiều strategy có lãi hơn → đổi trọng số → đổi lệnh Portfolio vào**. **Chi phí không phải tham số ngoại sinh trong replay này.**

**Hệ quả: không được quy delta `total_cost_drag` cho thành phần chi phí đã đổi.** Mọi so sánh `--fee-bps`/`--slippage-bps` trong loop — Round 213, 214, 215 và vòng này — đo một thay đổi **kép** của chi phí **và** quyết định. Kết luận "siêu cộng tính, không có lever đơn lẻ" của Round 215 là **đúng**; vòng này cung cấp **cơ chế** và cho thấy tính không cộng tính là **thuộc tính cấu trúc của replay**. Đã prepend banner vào round213/214/215.

**Con số dễ bị trích sai**: ở slippage bằng 0, Portfolio này **có lãi** — net **+0,1315**, Sharpe **+0,913**, Sortino **+1,592** (vượt mốc Sortino 1,0 của gate), cost÷gross **0,610**. **Đây là net dương đầu tiên đo được trong cả arc.** **Không được đọc là "chiến lược chạy được nếu sửa execution"**: (1) slippage bằng 0 **không khả thi**, đó là phản-thực tế; (2) run **bị nhiễu confound** — 38 lệnh so với 42, luồng quyết định khác; (3) **vẫn trượt gate** (Sharpe 0,913 < 1,0; cost÷gross 0,610 > 0,5; ngày dương 0,353 < 0,55) và route **không gate-eligible ở mọi cửa sổ**; (4) **một cửa sổ**, và đúng là cửa sổ vốn đã ưu ái route này.

Điều nó **thật sự** xác lập, cẩn trọng: ở cửa sổ này **toàn bộ khoản thiếu hụt cùng bậc độ lớn với dòng slippage**. Việc có thu hồi được phần nào hay không là **câu hỏi chất lượng thực thi** trong `finance-broker`/`mt5`, **không phải** câu hỏi của tầng Portfolio, và **không có gì ở đây nói là thu hồi được**.

**Giới hạn**: **không** đưa ra bất kỳ quy kết chi phí theo thành phần nào — đó chính là thứ vòng này chứng minh công cụ **không** cung cấp được; các con số 46,6% và 71,9% là hiệu ứng **kép** và phải trích dẫn như vậy. **Không** khẳng định phản hồi chỉ chạy qua `alpha_performance_quality` — đó là đường đã biết (`trading_modes.rs:589-617`) nhưng **chưa chạy test cô lập** và **chưa kiểm tra trọng số từng strategy**. **Không** khẳng định kết luận Round 213–215 sai — **phép đo** của chúng vẫn đứng; cái bị gỡ là khả năng đọc chúng như phân rã sạch theo thành phần. **Không promote.**

Chi tiết: `research/quant/rounds/round344-DATA-ISSUE-the-cost-flags-change-the-decision-stream-so-cost-component-attribution-is-not-identified.md`.

## Round 343 — NO-CHANGE: gross dương của `exness XAU` **sống sót qua bốn cửa sổ** (300, 500, 900, 1200 ngày) — đại lượng **đầu tiên** của cả arc làm được. Phi tương quan giữa hai route vàng là **khác biệt ensemble có chủ ý**, đã xác minh trong code production. Và PnL của một ngày **không** phải đại lượng cố định

**Phần 1 — kiểm tra khẳng định chịu lực của cả arc.** Mọi vòng về chi phí và band từ Round 313 đều dựa trên một sự kiện: `exness XAU` **có gross dương** và mất nó vào chi phí thực thi. Round 341 cho thấy trên `bybit XAUT` **dấu** của gross đảo theo cửa sổ, nên điều này cần test trực tiếp. **Đăng ký trước dạng phân hoạch**: gross dương ở **cả** `--days 300` và `--days 1200` → bền theo cửa sổ; **âm ở một trong hai** → "route duy nhất gross dương" cũng chỉ giới hạn cửa sổ.

| cửa sổ | holdout | ngày quan sát | lệnh | /tuần | **gross** | cost | net | Sharpe | streak |
|---|---|---|---|---|---|---|---|---|---|
| **300** | 2026-07-01 → 08-28 | 51 | 42 | 5,05 | **+0,3391** | 0,3845 | **−0,0454** | −0,249 | **3** |
| 500 | 2026-05-22 → 08-28 | 84 | 126 | 8,95 | **+0,6000** | — | −0,2283 | −0,814 | 4 |
| 900 | 2026-03-04 → 08-28 | 151 | 174 | 6,85 | **+0,7820** | 1,1929 | −0,4110 | −0,860 | 5 |
| **1200** | 2026-01-02 → 08-28 | 202 | 190 | 5,59 | **+0,7300** | 1,1900 | −0,4600 | −0,763 | 5 |

**Dương ở mọi cửa sổ — dự đoán đúng.** Gross chạy +0,34 · +0,60 · +0,78 · +0,73 qua dải độ dài cửa sổ gấp 4 lần, holdout bắt đầu từ tháng 1 tới tháng 7. **Đây là đại lượng đầu tiên trong cả arc sống sót qua thay đổi cửa sổ** — đối lập với band tối ưu (r331), tần suất tối ưu (r334), rãnh gross (r341) và **dấu** gross của `bybit XAUT` (r341), tất cả đều dịch. **Tiền đề mà toàn bộ công việc về chi phí dựa vào là vững.** Vẫn lỗ ở mọi cửa sổ (net −0,045 → −0,460; cost÷gross 1,13 → 1,63) và route **vẫn không gate-eligible** ở cả bốn. Ghi nhận: `--days 300` là **gần break-even nhất từng đo** trên band deployed (net −0,0454, streak 3) — **một cửa sổ**, và bài học r341 áp dụng cho nó y như mọi thứ khác.

**Phần 2 — vì sao hai route vàng phi tương quan (inspection, không áp dụng gì).** `finance-research/src/strategies.rs:24-78`: mọi route bắt đầu với đúng hai strategy (`candle_momentum`, `rsi_mean_reversion`) và **chỉ ba route** được thêm: `binance BTC/USDT` perp, **`exness XAU/USD` cfd** (thêm `mtf_stochastic_5m_4h_sma5`), `exness BTC/USD` cfd. **`bybit XAUT`, `bybit BTC`, `binance XAU` chỉ có 2 strategy nền.** → **Hai route vàng không chạy cùng strategy**; giá giống hệt đưa vào hai ensemble khác nhau thì cho tín hiệu, lệnh và PnL khác nhau.

**Và điều này phản chiếu production chính xác nên không phải lỗi đo lường**: `finance-api/src/deployment_rules.rs:616-642` gate ensemble live bằng đúng ba predicate đó; các loại trừ là **có chủ ý và ghi rõ tại chỗ** — `binance XAU` bị loại vì *"cùng cấu hình đó làm win rate holdout của nó tụt dưới mục tiêu"* (`:624-627`), và test tại `:747-780` khẳng định ba route kia giữ đúng `["candle_momentum","rsi_mean_reversion"]`, ghi chú XAUT *"là Tether Gold spot token, không phải XAU CFD hay perpetual; nó cố ý chỉ khởi đầu với các strategy nền."* **Investigation only — không áp dụng gì, không đề xuất thay đổi.**

Nhưng ensemble **không** sắp xếp được toàn bộ ma trận tương quan: cặp BTC cùng ensemble cao nhất (+0,856), nhưng `bybit XAUT` và `binance XAU` **cùng** ensemble base-2 lại chỉ +0,423 — **thấp hơn** cặp khác ensemble `exness XAU`/`binance XAU` (+0,589). Khác biệt ensemble là cơ chế **đủ** cho cặp vàng, **không phải** yếu tố duy nhất.

**Phần 3 — PnL của một ngày không cố định.** Round 341 nói 2026-08-12 là ngày tệ nhất của `exness XAU` *"độc lập cả band lẫn cửa sổ"*. Thêm hai cửa sổ ở band deployed **bác bỏ nửa sau**:

| ngày | @300 | @500 | @900 | @1200 |
|---|---|---|---|---|
| 2026-08-12 | −0,0545 | −0,1796 | −0,1796 | **+0,0015** |
| 2026-07-16 | −0,0575 | −0,0575 | −0,0575 | **−0,2186** |
| 2026-08-21 | **−0,1666** | **+0,0924** | 0,0000 | 0,0000 |

Cả bốn holdout **đều chứa** cả ba ngày và band giống hệt, vậy mà PnL cùng phiên đổi khác, **hai lần đổi dấu**. Đây là refit trọng số theo từng kline (r300) hiện lên trong mảng daily: replay dài hơn mang trọng số khác trên các nến nó chia sẻ với replay ngắn hơn. **Không được so sánh daily results giữa các cửa sổ** — đúng ràng buộc r300 đã đặt cho Portfolio counter, nay mở rộng sang mảng daily. Các so sánh **cross-route theo ngày** của Round 341 đều nằm **trong cùng một cửa sổ** nên **vẫn đúng**; khẳng định độc lập cửa sổ thì không.

**Giới hạn**: **không** khẳng định ensemble giải thích được ma trận tương quan — nó giải thích cặp vàng, không sắp xếp phần còn lại. **Không** khẳng định strategy thứ ba là **lý do** `exness XAU` có gross dương: `exness BTC` cũng có ensemble mở rộng nhưng gross **tệ nhất fleet** (−2,1476), và **không có flag** để chạy `exness XAU` bỏ strategy đó → **chưa test**. **Không** khẳng định net gần break-even ở @300 có ý nghĩa ngoài cửa sổ đó. **Không** khẳng định phụ thuộc cửa sổ của mảng daily được giải thích **hoàn toàn** bởi refit trọng số — chưa chạy test cô lập. **Không promote.**

Chi tiết: `research/quant/rounds/round343-NO-CHANGE-exness-xau-gross-is-positive-across-four-windows-and-the-gold-decorrelation-is-a-deliberate-ensemble-difference.md`.

## Round 342 — NEEDS-MORE-RESEARCH: hai route vàng khớp nhau **+0,996 về giá** và chỉ **+0,287 về PnL của Portfolio**. Phân kỳ mà Round 341 tìm ra là do **tầng Portfolio tạo ra**, không phải do instrument. Fleet đã đủ **sáu trên sáu**, và **`exness XAU` là route duy nhất có gross dương ở band deployed**

Round 341 để mở: *"phân kỳ giữa XAUT token và CFD XAU/USD, vị thế Portfolio ngược chiều, và phạm vi phiên khác nhau **đều** nhất quán với quan sát — tôi **không truy vấn dữ liệu thị trường và không kiểm tra vị thế**."*

**Đăng ký trước dạng phân hoạch**: **ρ_gold < ρ_BTC − 0,20** → hai route vàng không đồng biến như hai route BTC; **ρ_gold ≥ ρ_BTC − 0,20** → chúng đồng biến tương đương và 2026-06-10 chỉ là dị thường một ngày.

**Kết quả — dự đoán đúng, nhưng cách diễn giải hiển nhiên thì sai.** Tương quan PnL ngày trong nhóm, trên fleet đủ sáu route: **BTC +0,734** (binance/exness +0,856; binance/bybit +0,715; exness/bybit +0,631); **vàng +0,433** (exness XAU/bybit XAUT **+0,287**; exness XAU/binance XAU +0,589; bybit XAUT/binance XAU +0,423). ρ_gold − ρ_BTC = **−0,301** → **xác nhận**.

Cách giải thích hiển nhiên — hai route vàng theo dõi hai thứ khác nhau — **bị dữ liệu giá bác bỏ.** Một truy vấn **read-only phạm vi hẹp** lấy giá đóng cửa 5m theo ngày (2026-05-20 → 2026-08-30), tương quan log-return ngày:

| cặp | r giá | n |
|---|---|---|
| **`bybit XAUT` vs `exness XAU`** | **+0,996** | 86 |
| `binance BTC` vs `bybit XAUT` | +0,609 | 102 |
| `binance BTC` vs `exness XAU` | +0,595 | 86 |

**Hai instrument vàng thực chất là một instrument.** Và ngày 2026-06-10 **cả hai cùng giảm**: `XAUT` **−4,00%**, `XAU` **−4,23%** — trong khi PnL Portfolio là **−0,1694** trên route spot và **+0,2197** trên route CFD.

**Vậy sự đảo dấu do chính quyết định theo từng route của tầng Portfolio tạo ra, không phải do khác biệt nào ở tài sản cơ sở.** Phát hiện: **tương quan giá +0,996, tương quan PnL +0,287** — tầng quyết định **vứt bỏ khoảng 70%** mức đồng biến có sẵn trong dữ liệu nó nhận. Tôi đăng ký đúng phân hoạch và **lẽ ra đã kết luận sai** nếu không có dữ liệu giá: **một dự đoán được xác nhận không phải là một giải thích được xác nhận.**

**Fleet đã đủ — sáu trên sáu** (band deployed):

| route | gate-eligible | lệnh/tuần | **gross** | net | Sharpe |
|---|---|---|---|---|---|
| `exness XAU` @900 | không (7 interval) | 6,85 | **+0,7820** | −0,4110 | −0,860 |
| `bybit XAUT` @500 | có | 4,48 | −0,0135 | −0,4204 | −1,397 |
| **`binance XAU` @500** | **không** (53 ngày quan sát) | 5,07 | **−0,3442** | −0,5893 | −4,280 |
| **`bybit BTC` @500** | **có** | 12,11 | **−1,3153** | −2,7417 | −5,057 |
| `binance BTC` @500 | có | 21,84 | −1,7909 | −3,9407 | −6,753 |
| `exness BTC` @500 | không (4 interval) | 24,58 | −2,1476 | −4,5624 | −7,510 |

**Cả sáu đều trượt. Ở band deployed, `exness XAU` là route duy nhất có gross dương** — phiên bản chính xác của khẳng định mà Round 337 nói quá và Round 338 đính chính bằng **các band khác** trên `bybit XAUT`.

`bybit BTC` **gate-eligible đầy đủ** (không gap unverified ở bất kỳ interval nào, 101 ngày quan sát) và trượt vì performance, gồm cả `gross_pnl_positive` — **route gate-eligible thứ ba, gross âm thứ ba**. `binance XAU` continuity sạch nhưng `--days 500` **âm thầm trả về cửa sổ một phần**: holdout 2026-07-09 → 2026-08-30, 15.111 nến, **53 ngày quan sát**; dữ liệu chạy tới 2026-08-30 nên route **hiện hành, chỉ là nông** — đúng cái bẫy `--days` vượt độ sâu đã ghi trong skill.

**Giới hạn**: **không** khẳng định giá giữa các venue BTC ít tương quan hơn giữa các venue vàng — tôi chỉ truy vấn `binance BTC` trong nhóm BTC, nên tương quan **giá** nội bộ BTC **chưa đo**. **Không** biết **vì sao** Portfolio phân kỳ trên đầu vào giống hệt nhau — trọng số interval theo Alpha performance riêng từng route, thời điểm vào lệnh, và chiều vị thế đều nhất quán; tôi **không kiểm tra vị thế và trọng số**. **Không** khẳng định tương quan PnL ổn định: **mỗi route một cửa sổ**. **Không** khẳng định tương quan PnL thấp là **lỗi** — một hệ **đa dạng hóa** cũng trông như vậy, nhưng ở đây mọi route đều lỗ nên phi tương quan đang **rải lỗ**, không phải rải rủi ro. Sáu trên sáu trượt gate → **không promote**.

Chi tiết: `research/quant/rounds/round342-NEEDS-MORE-RESEARCH-the-two-gold-routes-track-each-other-at-0-996-in-price-and-0-287-in-portfolio-pnl.md`.

## Round 341 — REJECTED: rãnh **không tái lập** ở cửa sổ khác — khoảng cách gross 0,33 co lại còn 0,05. Và hiện tượng một-ngày-chi-phối là **phổ biến ở mọi route**, với 2026-06-10 là ngày **tệ nhất** trên `bybit XAUT` nhưng **tốt nhất** trên `exness XAU`

**Đăng ký trước dạng phân hoạch** (áp dụng đúng bài học của Round 340): gross(0,0125) **thấp hơn ít nhất 0,10** so với gross(0,02) → rãnh tồn tại; khoảng cách **dưới 0,10** → không. Ở 500 ngày khoảng cách đó là **0,3272** (−0,0682 với +0,2590).

**Bác bỏ — rãnh không tồn tại.** `bybit XAUT` `--days 300`, holdout 2026-07-01 → 2026-08-30, 61 ngày quan sát, **2026-06-10 đã được xác nhận không nằm trong holdout**, không trượt continuity:

| band | lệnh | /tuần | **gross** | cost | net | Sharpe | streak |
|---|---|---|---|---|---|---|---|
| 0,0125/0,025 | 45 | 5,25 | **−0,1757** | 0,2892 | −0,4650 | −2,746 | 5 |
| 0,02/0,04 | 31 | 3,62 | **−0,1282** | 0,2038 | −0,3319 | −1,734 | 6 |

Khoảng cách là **0,0476** — dưới hẳn mốc 0,10, **co lại 7 lần**. Và **mức** cũng dịch: ở 500 ngày hai band này đo được −0,0682 và **+0,2590**; ở 300 ngày **cả hai đều âm**.

**Cái giá phải trả cho Round 338–340.** Round 340 kết luận *"đặc trưng này mang tính cấu trúc, và band deployed nằm ngay đáy"* — cần thu hẹp: hình dạng đơn đỉnh trơn **có** chứng minh rãnh **không phải nhiễu cấu hình trong cửa sổ đó** (lập luận này vẫn đứng), nhưng **không** chứng minh nó là thuộc tính **ổn định của route**. Phải đọc là "cấu trúc **trong cửa sổ này**". Round 338 đính chính Round 337 bằng +0,2662 và +0,2590 trên `bybit XAUT` — ở 300 ngày **cả hai band đều âm**, nên **dấu của gross trên route này phụ thuộc cửa sổ**, và **cả** khẳng định của Round 337 **lẫn** đính chính của Round 338 đều không phải phát biểu ổn định. **Đây là bài học Round 331 lặp lại lần thứ ba**: một hình dạng đo trên một cửa sổ là phát biểu về cửa sổ đó — đã học lại cho band tối ưu (r331), tần suất tối ưu (r334), và rãnh (lần này).

**Giới hạn thiết kế tôi không thể biện hộ**: holdout 300 ngày **vừa** loại 2026-06-10 **vừa** là giai đoạn ngắn hơn, muộn hơn, điều kiện khác (61 ngày so với 101). Thiết kế **trộn lẫn** hai yếu tố; nó trả lời đúng câu hỏi tính tái lập đã đăng ký nhưng **không** quy được nguyên nhân cho ngày bị loại.

**Kết quả 0 container — một-ngày-chi-phối là phổ biến, và vàng đảo dấu giữa hai venue.** Đọc `daily_results` từ sáu gate run đã lưu ở Round 335–337:

| run | ngày | net | **ngày tệ nhất** | PnL | tỷ lệ | **ngày tốt nhất** | PnL |
|---|---|---|---|---|---|---|---|
| `exness XAU` @500 b=0,011 | 84 | −0,0541 | **2026-08-12** | −0,1530 | 282,8% | **2026-06-10** | **+0,2097** |
| `exness XAU` @500 b=0,0115 | 84 | −0,0122 | **2026-08-12** | −0,1205 | 983,4% | **2026-06-10** | **+0,2197** |
| `exness XAU` @900 deployed | 151 | −0,4110 | **2026-08-12** | −0,1796 | 43,7% | 2026-04-01 | +0,1869 |
| `binance BTC` @500 | 101 | −3,9407 | **2026-06-05** | −0,4667 | 11,8% | **2026-06-15** | +0,1685 |
| `exness BTC` @500 | 101 | −4,5624 | **2026-06-05** | −0,4108 | 9,0% | **2026-06-15** | +0,1697 |
| `bybit XAUT` @500 | 101 | −0,4204 | **2026-06-10** | −0,1694 | 40,3% | 2026-08-05 | +0,1874 |

1. **Mọi route đều có một ngày chi phối** → phát hiện của Round 340 **không** đặc thù `bybit XAUT`. Trên `exness XAU` đó là **2026-08-12**, tệ nhất ở **cả** cửa sổ 500 **và** 900 ngày và ở mọi band — **độc lập cả band lẫn cửa sổ**.
2. **Hai venue BTC đồng thuận**: 2026-06-05 tệ nhất và 2026-06-15 tốt nhất trên **cả** binance lẫn exness.
3. **Hai route vàng đảo dấu**: 2026-06-10 **tệ nhất** trên `bybit XAUT` nhưng **tốt nhất** trên `exness XAU`. Cùng underlying, cùng phiên, ngược dấu.

Mức tập trung rất đồng đều: **năm ngày lớn nhất chiếm 14,4%–19,7%** tổng |PnL ngày| ở cả năm run, qua ba instrument và hai độ dài cửa sổ.

**Giới hạn**: **không** khẳng định việc loại 2026-06-10 **gây ra** việc rãnh biến mất. **Không** biết **vì sao** vàng đảo dấu giữa hai venue — phân kỳ XAUT token với CFD XAU/USD, vị thế Portfolio ngược chiều, và phạm vi phiên khác nhau **đều** nhất quán với quan sát; tôi **không truy vấn dữ liệu thị trường và không kiểm tra vị thế**. **Không** khẳng định `bybit XAUT` không có gross edge — cả hai cách đọc đều **giới hạn theo cửa sổ**, và đó chính là điểm mấu chốt. **Không** khẳng định mức tập trung đồng đều có ý nghĩa nhân quả. Mọi cấu hình vòng này đều lỗ → **không promote**.

Chi tiết: `research/quant/rounds/round341-REJECTED-the-trough-does-not-replicate-on-a-different-window-and-single-day-dominance-is-general-with-gold-inverting-between-venues.md`.

## Round 340 — NEEDS-MORE-RESEARCH: "cái hố" thực ra là **rãnh trơn đơn đỉnh** qua bảy band, khó bác bỏ hơn hẳn. Và **một ngày duy nhất, 2026-06-10, là ngày tệ nhất ở mọi band**, bằng 3,6 lần toàn bộ khoản lỗ ròng của cấu hình tốt nhất

**Đăng ký trước, và một lỗi trong chính nó**: hố hẹp → 0,009 cho gross **≥ +0,15** và 0,015 cho gross **≥ +0,15**; bác bỏ nếu một trong hai **≤ +0,1**. **Đăng ký này có lỗi và tôi ghi nhận đúng như vậy**: khoảng `(+0,1; +0,15)` **không** thuộc nhánh nào, và 0,015 rơi đúng vào đó ở **+0,1414**. Đây là **lỗi pre-registration thứ ba** của loop — Round 327 đăng ký p-value chưa tính, Round 330 đăng ký ngưỡng trên **sai biến**, lần này để **hở khoảng** giữa vùng xác nhận và vùng bác bỏ. Cách sửa vẫn thế: phát biểu tiêu chí như một **phân hoạch**, không phải hai bất đẳng thức rời.

**Bức tranh bảy band** (`bybit XAUT` `--days 500`, cùng holdout, 101 ngày quan sát, không run nào trượt continuity):

| band | lệnh | /tuần | **gross** | cost | cost/lệnh | net | Sharpe |
|---|---|---|---|---|---|---|---|
| 0,005 | 148 | 10,36 | +0,2662 | 1,0998 | 0,00743 | −0,8336 | −3,074 |
| 0,008 | 84 | 5,88 | +0,2518 | 0,7047 | 0,00839 | −0,4529 | −1,655 |
| **0,009** | 70 | 4,90 | **+0,1561** | 0,7139 | 0,01020 | −0,5578 | −1,893 |
| 0,01 **(deployed)** | 64 | 4,48 | **−0,0135** | 0,4069 | 0,00636 | −0,4204 | −1,397 |
| 0,0125 | 48 | 3,36 | **−0,0682** | 0,3162 | 0,00659 | −0,3843 | −1,279 |
| **0,015** | 41 | 2,87 | **+0,1414** | 0,2719 | 0,00663 | −0,1305 | −0,397 |
| 0,02 | 28 | 1,96 | +0,2590 | 0,3185 | 0,01137 | −0,0595 | −0,171 |

Dãy gross **đơn đỉnh hoàn hảo**: 0,2662 > 0,2518 > 0,1561 > −0,0135 > −0,0682 < +0,1414 < +0,2590 — một cực tiểu duy nhất tại 0,0125 với **hai vai đơn điệu**. "Hố hẹp" của Round 339 được **tinh chỉnh thành rãnh trơn**, và điều đó **củng cố** kết luận: nhiễu cấu hình **không** tạo ra dốc xuống đơn điệu qua ba điểm rồi dốc lên đơn điệu qua ba điểm nữa. Đặc trưng này mang tính cấu trúc, và band deployed nằm ngay đáy.

**Một xấp xỉ chuẩn bị vỡ ở độ phân giải này**: từ Round 274 tôi vẫn dùng "chi phí tỉ lệ với số lệnh". **Chi phí mỗi lệnh qua bảy band chạy 0,00636 → 0,01137 — chênh 1,8 lần** — và **không** đơn điệu theo độ rộng band. Đó là **xấp xỉ hữu ích, không phải đẳng thức**; kết luận nào phụ thuộc chênh lệch chi phí/lệnh nhỏ hơn ~2 lần thì không được dựa vào nó. Không ảnh hưởng các kết luận cũ vốn dựa trên thay đổi tần suất 2–5 lần.

**Kết quả 0 container 1 — bất biến 37/101 là trùng hợp, không phải cùng ngày.** Tập ngày **khác nhau**: 0,008 và 0,0125 chỉ chung **29** trong 37 ngày dương (Jaccard 0,644); Jaccard từng cặp qua bốn band là 0,481–0,689; 23 ngày dương ở cả bốn, 35 ngày âm ở cả bốn. Câu hỏi mở của Round 339 **đóng lại** ở khả năng ít thú vị hơn.

**Kết quả 0 container 2 — một ngày chi phối mọi cấu hình.** **`2026-06-10` là ngày tệ nhất ở cả sáu band đã đo** (−0,2184; −0,1854; −0,2054; −0,2069; −0,1634; −0,2134), bất kể độ rộng band, số lệnh hay tần suất.

| band | net | PnL ngày tệ nhất | net **không tính** ngày đó | tỷ lệ trên khoản lỗ ròng |
|---|---|---|---|---|
| 0,005 | −0,8336 | −0,2184 | −0,6152 | 26,2% |
| 0,008 | −0,4529 | −0,1854 | −0,2675 | 40,9% |
| 0,0125 | −0,3843 | −0,2069 | −0,1774 | 53,8% |
| 0,02 | −0,0595 | −0,2134 | **+0,1539** | **358,6%** |

**Đây là phát biểu về mức tập trung, không phải về khả năng sinh lời.** Một cấu hình **không** sinh lời chỉ vì có thể bỏ ngày tệ nhất — ngày đó nằm trong mẫu, khoản lỗ là thật, và route nào có kết quả treo vào một phiên trên 101 phiên thì đang mang tail risk mà Sharpe/Sortino của gate **phạt đúng**. Điều nó nói được: verdict holdout của route này **bị một phiên duy nhất chi phối**, và protective band — vốn sinh ra để chặn lỗ mỗi vị thế — **không chặn được nó ở bất kỳ độ rộng nào đã thử**.

**Giới hạn**: **không có cơ chế** giải thích rãnh; bảy điểm mô tả **hình dạng**, và "hình dạng trơn" là bằng chứng nó **có thật**, **không** phải bằng chứng về nguyên nhân. **Không** khẳng định bỏ 2026-06-10 làm cấu hình nào sinh lời — ngày đó đã xảy ra; dòng đó là đo mức tập trung, **không được trích như kết quả PnL**. **Không** biết chuyện gì xảy ra ngày 2026-06-10: tôi **không** truy vấn dữ liệu thị trường phiên đó. **Một route, một cửa sổ.** Mọi band trên route này đều lỗ → **không promote**.

Chi tiết: `research/quant/rounds/round340-NEEDS-MORE-RESEARCH-the-hole-is-a-smooth-unimodal-trough-across-seven-bands-and-one-day-dominates-every-configuration.md`.

## Round 339 — NEEDS-MORE-RESEARCH: hõm gross tại band deployed là **thật, không phải nhiễu** — nó lan sang band kế trên. Trên `bybit XAUT`, band production nằm **bên trong một hố hẹp 0,01–0,0125** nơi gross sụp từ +0,25 xuống 0. Khôi phục gross **không** khôi phục net

Round 338 tự nêu: *"không khẳng định −0,0135 tại band deployed là nhiễu; nó **nhất quán** với nhiễu cỡ ±0,28, nhưng **tôi không chạy đo lặp**."* **Đăng ký trước hai chiều**: **(A) nhiễu** — cả hai band kề trả về gross trong **[+0,1; +0,4]**, để lại deployed là outlier đơn lẻ; **(B) hõm thật** — ít nhất một band kề cũng trả về gross trong **[−0,15; +0,1]**.

**Nhánh B xảy ra.** `bybit XAUT` `--days 500`, cùng holdout (28.799 nến, 101 ngày quan sát), không run nào trượt continuity:

| band | lệnh | /tuần | **gross** | cost | net | Sharpe | ngày dương | streak |
|---|---|---|---|---|---|---|---|---|
| 0,005/0,01 | 148 | 10,36 | **+0,2662** | 1,0998 | −0,8336 | −3,074 | 0,386 | 5 |
| **0,008/0,016** | 84 | 5,88 | **+0,2518** | 0,7047 | −0,4529 | −1,655 | 0,366 | 13 |
| 0,01/0,02 **(deployed)** | 64 | 4,48 | **−0,0135** | 0,4069 | −0,4204 | −1,397 | 0,366 | 13 |
| **0,0125/0,025** | 48 | 3,36 | **−0,0682** | 0,3162 | −0,3843 | −1,279 | 0,366 | 13 |
| 0,02/0,04 | 28 | 1,96 | **+0,2590** | 0,3185 | −0,0595 | −0,171 | 0,406 | 21 |

**Hai band kề nhau (0,01 và 0,0125) đều ở mức gross gần 0**, kẹp giữa +0,25 đến +0,27 ở cả hai phía. Nhiễu **không** tạo ra hai giá trị thấp liền kề nằm giữa ba giá trị cao → cách đọc "nhiễu ±0,28" của Round 338 **bị rút lại**. `bybit XAUT` có **hố hẹp 0,01–0,0125** nơi gross edge sụp về không, **và band production nằm bên trong đó**.

**Vì sao đây không phải cải thiện khả thi**: rời khỏi hố khôi phục gross nhưng **không** khôi phục net — siết về 0,008 lấy lại **+0,265 gross** nhưng thêm **+0,298 cost** (tần suất 4,48 → 5,88/tuần), nên net **xấu đi 0,032**. Đúng kết quả chuẩn từ Round 274 trở đi: **tần suất mua bằng cách dịch band luôn phải trả theo tỷ lệ**. Nới lên 0,02 có net tốt hơn (−0,0595) nhưng Round 338 đã cho thấy giá phải trả trên joint objective: 1,96 lệnh/tuần và streak **21 ngày**.

**Một bất biến tôi chưa giải thích được**: ba trong năm band — 0,008, 0,01 và 0,0125, ở **84, 64 và 48 lệnh** — trả về **cùng** tỷ lệ ngày dương (0,36634 = đúng 37/101 ngày) và **cùng** streak ngày âm (13). Hai band còn lại khác (39/101 và 41/101; streak 5 và 21). **Tôi chưa kiểm tra mảng daily results**, nên không biết đó là cùng những ngày sinh lời hay chỉ trùng số học.

**Giới hạn**: **không** khẳng định bất kỳ **nguyên nhân** nào cho cái hố — năm điểm grid chỉ xác lập nó tồn tại và nằm khoảng nào; tôi **không có cơ chế** và không đề xuất. Biên của hố là **nơi grid dừng** (chưa chạy gì giữa 0,008–0,01 và 0,0125–0,02). **Một route, một cửa sổ** — không khẳng định có ở route khác hay ổn định theo thời gian. **Không** khẳng định việc band deployed nằm trong hố nghĩa là **production cấu hình sai**: net ở 0,008 **tệ hơn** deployed, và band duy nhất có net tốt hơn thì trượt nặng cả tần suất lẫn streak. **Không có khuyến nghị đổi cấu hình deployed. Không promote.**

Chi tiết: `research/quant/rounds/round339-NEEDS-MORE-RESEARCH-the-gross-dip-at-the-deployed-band-is-real-not-noise-and-production-sits-inside-a-narrow-hole.md`.

## Round 338 — REJECTED: mẫu "gross giảm theo tần suất" cross-route **không sống sót** qua ladder trong cùng route trên một route gate-eligible. Gross **phẳng ở +0,26 qua dải tần suất 5,3 lần** — và `bybit XAUT` **có** gross edge, điều Round 337 nói sai vì chỉ đo một band

Round 337 ghi mẫu cross-route rồi tự đánh dấu là lead, kèm nhận xét *"muốn test nó cần thiết kế trong cùng route trên một route gate-eligible, chưa vòng nào chạy"*. `bybit XAUT` chính là route đó: gate-eligible (0 gap trên cả tám interval) và có exposure vàng. **Đăng ký trước**: gross ở **cả** 0,005/0,01 và 0,02/0,04 nằm trong **[−0,3; +0,3]** (tức phẳng, theo Round 328); bác bỏ nếu gross dịch theo tần suất vượt dải đó.

**Xác nhận — phẳng.** Ladder ba band, cùng holdout (2026-05-22 → 2026-08-30, 28.799 nến, 101 ngày quan sát), **không run nào trượt continuity**:

| band | lệnh | /tuần | **gross** | cost | net | Sharpe | ngày dương | **streak** | cost÷gross |
|---|---|---|---|---|---|---|---|---|---|
| 0,005/0,01 | 148 | **10,36** | **+0,2662** | 1,0998 | −0,8336 | −3,074 | 0,386 | **5** | 4,131 |
| 0,01/0,02 (deployed) | 64 | 4,48 | −0,0135 | 0,4069 | −0,4204 | −1,397 | 0,366 | 13 | 30,24 |
| 0,02/0,04 | 28 | **1,96** | **+0,2590** | 0,3185 | **−0,0595** | −0,171 | 0,406 | **21** | 1,230 |

**Gross là +0,2662 ở 10,36/tuần và +0,2590 ở 1,96/tuần — chênh 2,8% qua dải tần suất 5,3 lần.** Mẫu cross-route của Round 337 **không có** hậu thuẫn trong cùng route; kết luận gross phẳng của Round 328 được tái xác nhận trên **route thứ hai**, lần này là route gate-eligible. Phần dao động còn lại là **một hõm tại band deployed** (−0,0135), không đơn điệu và nằm giữa hai giá trị gần như bằng nhau — đúng hình dạng **nhiễu mức cấu hình cỡ ±0,28**, không phải một quy luật tần suất.

**Đính chính bắt buộc với Round 337.** Round 337 kết luận *"`exness XAU` là route **duy nhất** có gross dương"* — đo ở **một band mỗi route**. Trên route này **hai trong ba band** cho gross **+0,26**; chỉ band deployed cho ≈ 0. **`bybit XAUT` có gross edge và chữ "duy nhất" của Round 337 là sai — tôi rút lại nó.** Điểm cấu trúc vẫn sống ở dạng yếu hơn: mọi route gate-eligible đã đo **vẫn trượt gate**, và gross dương lớn nhất tìm được ở đâu đó vẫn là +0,78 của `exness XAU` — nhưng "route duy nhất có edge" là artifact của việc lấy mẫu một band.

**Phát hiện joint-objective đáng giá hơn cả hai điều trên**: đọc đồng thời ba chiều của gate, các band **xung đột trực tiếp** — **net tốt nhất ở 0,02/0,04** (−0,0595, cost÷gross 1,23, Sharpe −0,171), cấu hình duy nhất trên route này ở gần break-even; **cũng chính band đó tệ nhất về tần suất** (1,96/tuần, hụt mốc 7,0 tới 3,6 lần) **và tệ nhất về streak** (**21 ngày âm liên tiếp** so với ngưỡng 5); và streak xấu đi **đơn điệu khi tần suất giảm**: 5 → 13 → 21. **Trên route này cấu hình net-tốt-nhất đồng thời là frequency-tệ-nhất và streak-tệ-nhất**, và không có thiết lập nào của lever này cải thiện một chiều mà không phá hai chiều còn lại — phát biểu sạch hơn xung đột joint-objective của Round 328 (vốn chỉ là Target 1 với Target 3).

**Giới hạn**: không khẳng định gross độc lập với tần suất **như một quy luật** — hai route, mỗi route một cửa sổ; điều được xác lập là mẫu cross-route **không có hậu thuẫn trong cùng route ở nơi có thể test**. Không khẳng định −0,0135 ở band deployed là nhiễu: nó **nhất quán** với nhiễu, nhưng tôi **không** chạy đo lặp nên không tách được nhiễu khỏi một hõm cục bộ thật. Không khẳng định +0,26 của `bybit XAUT` ổn định: **một cửa sổ**. Không khẳng định tính đơn điệu của streak là **nhân quả** — tôi không kiểm tra cách phân loại ngày. **Không promote**: net tốt nhất trên route là −0,0595 ở 1,96 lệnh/tuần với streak 21 ngày — **tệ hơn** thiết lập deployed trên joint objective, không phải tốt hơn.

Chi tiết: `research/quant/rounds/round338-REJECTED-the-cross-route-frequency-gross-pattern-does-not-survive-a-within-route-ladder-and-bybit-xaut-does-have-gross-edge.md`.

## Round 337 — REJECTED (giả thuyết của tôi): lỗi continuity đi theo **lịch giao dịch của instrument**, không phải theo venue. Và trên bốn route đã đo bằng gate, **route duy nhất có gross dương lại chính là route không thể có verdict gate**

Hai dự đoán đăng ký trước: **(A)** lỗi là thuộc tính **venue** của bề mặt CFD Exness → `exness BTC`, một CFD trên cùng venue, trượt đúng bảy interval đó; bác bỏ nếu nó sạch. **(B)** `bybit XAUT` — vàng trên venue crypto 24/7 — không có gap trên cả tám interval nên gate-eligible; bác bỏ nếu trượt continuity.

**(A) bị bác bỏ — là lịch giao dịch, không phải venue.** `exness BTC/USD` `--days 500` chỉ trượt **bốn** interval, với số gap **nhỏ hơn ba bậc độ lớn** so với `exness XAU` (5m: 15 gap unverified / 54 nến; 15m 3/9; 30m 2/4; 1h 1/1) và **2h/4h/12h/1d hoàn toàn sạch**. `exness BTC/USD` giao dịch gần như 24/7; `exness XAU/USD` theo lịch phiên hàng tuần của thị trường vàng và đóng cửa mỗi cuối tuần. **Hàng trăm gap unverified bám theo lịch giao dịch của instrument, venue chỉ là ngẫu nhiên — giả thuyết của tôi gọi sai biến.** Hai điều mới: `input_continuity_failed:5m` có xuất hiện ở route này (bề mặt 5m **tự nó** trượt, trong khi 5m của `exness XAU` luôn được đánh dấu đầy đủ), và một check riêng biệt **`holdout_interval_continuity`** cũng nằm trong danh sách trượt → độ phủ marker **không** đơn giản là "5m xong, phần còn lại chưa", mà **khác nhau theo route**.

**(B) được xác nhận — và nó không mua được gì.** `bybit XAUT/USDT` spot `--days 500`: **0 gap verified và 0 unverified trên cả tám interval**, 101 ngày quan sát, **gate-eligible**. Và nó trượt performance rất nặng: 64 lệnh, **4,48/tuần**, gross **−0,01346**, cost 0,4069, net −0,4204, Sharpe −1,397, Sortino −1,965, **streak ngày âm 13** — streak tệ nhất từng đo trong arc này.

**Bức tranh trên bốn route đã đo bằng gate:**

| route | gate-eligible | lệnh/tuần | **gross trước phí** | net | Sharpe |
|---|---|---|---|---|---|
| `exness XAU` @900 | **không** (7 interval) | 6,85 | **+0,7820** | −0,4110 | −0,860 |
| `bybit XAUT` @500 | **có** | 4,48 | −0,0135 | −0,4204 | −1,397 |
| `binance BTC` @500 | **có** | 21,84 | −1,7909 | −3,9407 | −6,753 |
| `exness BTC` @500 | không (4 interval) | 24,58 | −2,1476 | −4,5624 | −7,510 |

**`exness XAU` là route duy nhất có gross dương, và đó đúng là route không thể có verdict gate.** Mọi route gate-eligible đã đo đều có gross ≤ 0 — nghĩa là **không lever chi phí hay tần suất nào chạm tới lợi nhuận được trên chúng**, vì không có gì để giữ lại. Đọc thẳng thắn: arc chi phí (Round 313–335) **hoàn toàn** về `exness XAU` — route duy nhất mà nỗ lực đó có ý nghĩa, **và** cũng là route có verdict gate không thể đạt được về mặt cấu trúc.

**Một quan sát, dứt khoát không phải kết luận**: xếp theo tần suất, bốn con số gross là +0,7820 (6,85/tuần) · −0,0135 (4,48) · −1,7909 (21,84) · −2,1476 (24,58) — hai route tần suất thấp ở mức ≥ 0, hai route tần suất cao âm sâu. Nếu đúng thì các quyết định thêm của Portfolio **tệ hơn một cách hệ thống**, chứ không chỉ đắt hơn — mạnh hơn hẳn Round 328. **Nhưng bốn route khác instrument/venue/độ sâu/cửa sổ không phải test có kiểm soát**, thứ tự **không đơn điệu** theo tần suất (4,48/tuần thấp hơn 6,85/tuần về gross), và các ladder **trong cùng route** ở Round 328 giữ gross **gần như phẳng** qua thay đổi tần suất 5–7 lần, tức **mâu thuẫn** với mẫu cross-route. **Ghi nhận như một lead, không phải finding.**

**Giới hạn**: không khẳng định lịch giao dịch là nguyên nhân **đã xác nhận** — cái được chứng minh là giả thuyết **venue** sai; tôi **chưa** đối chiếu lịch phiên hay đường ghi marker theo từng route. Không khẳng định vàng không có edge: `bybit XAUT` khác instrument/venue/độ sâu/thanh khoản so với `exness XAU`, **không** phải so sánh có kiểm soát, và hai route **trái dấu** về gross. Không khẳng định gross âm là vĩnh viễn: **mỗi route một cửa sổ**. Chưa đo `bybit BTC` và `binance XAU` bằng gate.

Chi tiết: `research/quant/rounds/round337-REJECTED-continuity-follows-the-instruments-trading-calendar-not-the-venue-and-every-gate-eligible-route-has-negative-gross.md`.

## Round 336 — DATA-ISSUE: `exness XAU` trượt input continuity **ở cả 900 ngày**, nên **không** verdict gate nào trên route đó ở **bất kỳ cửa sổ nào** là pass-eligible. `binance BTC` sạch trên cả tám interval — đo lường gate-eligible **đầu tiên** của cả arc, và nó trượt vì **gross âm**

Round 335 để mở: *"chưa test bảy check continuity có trượt ở 900 ngày không — nếu có thì không verdict gate nào trên route này mang ý nghĩa như vẻ ngoài."* Đăng ký trước: `binance BTC` — perpetual 24/7 không có phiên đóng cửa — qua **cả** `minimum_holdout_days` **và** cả tám check `input_continuity` ở 500 ngày, tức lỗi continuity là **đặc thù route CFD** chứ không phổ quát; bác bỏ nếu nó trượt một trong hai.

**Kết quả 1 — caveat đóng lại theo hướng bất lợi cho arc exness.** `exness XAU` `--days 900` (holdout 2026-03-04 → 2026-08-28, 34.867 nến, **151 ngày quan sát**): `minimum_holdout_days` **qua** (đúng như Round 331 nói) nhưng **cả bảy** interval khác 5m **vẫn trượt** `input_continuity`, và nặng hơn ở 500 ngày — 15m 628 gap unverified / 27.659 nến, 30m 626 / 13.821, 1h 625 / 6.901; 5m lại là 645 gap **đã verify**, 0 unverified. → **Cửa sổ 900 ngày không hề gate-eligible hơn cửa sổ 500 ngày.** Mọi verdict gate trong arc `exness XAU` (Round 328, 330, 331, 332, 334, 335) là **xếp hạng tương đối trên cùng cửa sổ**, không bao giờ là verdict pass-eligible. Đã prepend banner vào cả bốn file. Số liệu performance tái lập: 174 lệnh, 6,853/tuần, gross **+0,7820**, cost 1,1929, net −0,41099 so với −0,4118 của Round 331 (lệch 0,2%, do cửa sổ kết thúc ở "now" muộn hơn).

**Kết quả 2 — dự đoán đúng.** `binance BTC` `--days 500` (holdout 2026-05-22 → 2026-08-30, 28.799 nến, **101 ngày quan sát**): **0 gap verified và 0 gap unverified trên cả tám interval**, `minimum_holdout_days` qua, **không có** `input_continuity_failed` trong danh sách trượt. **Lỗi continuity là đặc thù cấu trúc phiên của CFD, không phải thuộc tính phổ quát của gate — verdict gate trên route crypto là verdict performance thật.**

**Kết quả 3 — và route gate-eligible đầu tiên trượt dứt khoát, theo một kiểu khác.**

| | `exness XAU` @900 | `binance BTC` @500 |
|---|---|---|
| lệnh / mỗi tuần | 174 / 6,85 | 312 / **21,84** |
| **gross trước phí** | **+0,7820** | **−1,7909** |
| cost drag | 1,1929 | 2,1498 |
| net | −0,41099 | **−3,9407** |
| Sharpe / Sortino | −0,860 / −1,177 | **−6,753 / −6,817** |
| streak ngày âm | 5 | 7 |
| Target 3 | trượt (6,85) | **đạt (21,84)** |
| gate-eligible | **không** | **có** |

**Hai route trượt vì lý do khác nhau về cấu trúc**: `exness XAU` **có gross dương** và mất nó vào chi phí thực thi (cost÷gross 1,53) — **vấn đề chi phí**. `binance BTC` **gross âm**: nó lỗ **trước khi** tính bất kỳ chi phí nào, và `gross_pnl_positive` nằm trong danh sách trượt. **Không cách giảm chi phí nào cứu được gross âm.** Đây là lần đầu phân biệt này được đo trên chính holdout của gate với một route mà **tính eligible không còn là câu hỏi**. Và **lever tần suất không phải nút thắt** trên `binance BTC` — nó chạy 3,2 lần mốc Target 3 mà vẫn lỗ.

**Marker thiếu đến từ đâu (inspection read-only, không áp dụng gì).** Gap chỉ được tính "verified" khi kline mang `gap_before_reason`/`gap_before_candles` — `finance-live-action/crates/finance-research/src/klines.rs:314-329`. **Cả hai đầu contract đều hỗ trợ đủ tám interval trong code**: `finance-mw/cmd/ops/kline-gap-marker-backfill/main.go:334-354` (`activeIntervalDuration` nhận 5m…1d, tool chạy **theo từng route từng interval**) và `finance-mw/internal/interfaces/worker/kline_flusher.go:331-337` (đường repair live đặt marker từ `step` suy ra từ interval của chính route, interval-agnostic). **Vậy thiếu hụt nằm ở độ phủ dữ liệu đã lưu, không phải ở code path không diễn đạt được.** **Investigation only — không áp dụng gì, không đề xuất fix ở đây.**

**Giới hạn**: không khẳng định **vì sao** marker vắng trên bảy interval — backfill chưa chạy và lỗ hổng đường live **đều** nhất quán với dữ liệu; tôi **không** kiểm tra bản ghi backfill hay production state. Không khẳng định gap khung lớn là dữ liệu sai. **Không** khẳng định xếp hạng `exness XAU` mất hiệu lực — một check cấu trúc trượt **giống hệt nhau** ở mọi cấu hình thì không thể đảo thứ tự chúng. Không khẳng định gross âm của `binance BTC` là thuộc tính route hay cửa sổ: **một cửa sổ, một route, một band**.

Chi tiết: `research/quant/rounds/round336-DATA-ISSUE-exness-xau-can-never-pass-the-gate-at-any-window-and-binance-btc-is-the-first-gate-eligible-route-measured.md`.

## Round 335 — DATA-ISSUE: **không** run nào của `exness XAU` tại `--days 500` có thể qua gate, vì hai lý do không liên quan performance. Và band tối ưu là một **vùng phẳng**, không phải một điểm

Round 334 để mở: *"chỉ hai điểm trung gian được thử và **điểm thấp hơn thắng**"* và *"thứ hạng chính xác của ba điểm giữa thì **chưa** xác lập"*. Đăng ký trước: net tại 0,011/0,022 và 0,0115/0,023 nằm **hẳn giữa** −0,2283 (0,01) và −0,0121 (0,0125) — tức đoạn dốc lên từ 0,01 tới 0,0125 là trơn và đơn điệu; bác bỏ nếu một trong hai rơi ra ngoài khoảng đó.

**Phát hiện chính — danh sách check trượt dài hơn những gì tôi vẫn báo cáo.** Hai check trượt **không phải** vì performance:

1. **`minimum_holdout_days`** — holdout dài 98,5 ngày lịch nhưng chỉ **84 ngày quan sát** so với ngưỡng 90. `exness XAU` là CFD, cuối tuần đóng cửa, nên cửa sổ 500 ngày **về mặt cấu trúc không thể** cung cấp 90 ngày holdout. Tại `--days 900` holdout đạt 151 ngày quan sát (Round 331) và check này qua.
2. **`input_continuity_failed` trên cả bảy interval khác 5m** — metadata gap: 5m có **356 session gap đã verify, 0 unverified**, còn mọi khung lớn hơn đều mang hàng trăm gap **unverified** (15m: 344 gap / 15.154 nến; 1h: 342 / 3.782; 30m: 342 / 7.572).

**Hệ quả: không cấu hình nào có thể qua gate trên route này ở 500 ngày.** Round 330 và Round 334 đều nói cấu hình tốt nhất "vẫn trượt gate" và quy cho Sharpe, tỷ lệ ngày dương và cost÷gross — **quy kết đó thiếu**, hai check cấu trúc đang trượt bên dưới mà tôi không báo cáo. Các so sánh performance trong hai vòng đó **vẫn đúng như xếp hạng tương đối trên cùng một cửa sổ**; **verdict gate thì không mang ý nghĩa tôi ngụ ý**. Đã prepend banner đính chính vào cả hai file.

**Kết quả test đã đăng ký — khoảng dự đoán đúng, và đỉnh là một mặt phẳng.** Grid 500 ngày bảy điểm (band | lệnh | /tuần | gross | net | Sharpe | cost÷gross): 0,01/0,02 126 8,95 +0,6000 −0,2283 −0,814 1,38 · **0,011/0,022 115 8,17 +0,7559 −0,0541 −0,193 1,072** · **0,0115/0,023 110 7,82 +0,7201 −0,01225 −0,045 1,017** · 0,0125/0,025 108 7,67 +0,7121 −0,0121 −0,041 1,02 · 0,015/0,03 107 7,60 +0,6499 −0,0724 −0,230 1,11 · 0,02/0,04 96 6,82 +0,6067 −0,0301 −0,096 1,05 · 0,04/0,08 86 6,11 +0,4460 −0,1396 −0,445 1,31.

- **Đoạn dốc lên là tín hiệu thật, không phải nhiễu**: net leo −0,2283 → −0,0541 → −0,0122, bước nhảy 0,174 rồi 0,042 — lớn hơn một đến hai bậc so với khoảng cách cỡ 0,01 mà Round 334 lo là nhiễu.
- **Đỉnh là mặt phẳng**: 0,0115 (−0,01225) và 0,0125 (−0,0121) giống nhau trong 1,2%, cùng Sharpe, cùng tỷ lệ ngày dương 0,405, cùng streak 4, cùng cost÷gross. **Dự đoán 0,0119 từ volatility nằm bên trong mặt phẳng này** — mạnh hơn phát biểu "định vị được vùng" của Round 334.
- **Tần suất đơn điệu tuyệt đối theo độ rộng band** (8,95/8,17/7,82/7,67/7,60/6,82/6,11, không ngoại lệ) — đọc lever này theo lệnh/tuần, không theo giá trị band.
- **Gross và net đạt đỉnh ở hai band khác nhau**: gross cao nhất tại 0,011 (+0,7559), cost drag giảm đơn điệu theo số lệnh (0,8100 → 0,7324), nên net đạt đỉnh **rộng hơn** gross — tối ưu do **giao điểm** giữa hai đường, không do cực đại của gross.
- **Vẫn lỗ**: cost÷gross > 1,0 ở cả bảy band.

**Giới hạn**: không khẳng định gap khung lớn là **lỗi dữ liệu** — "unverified" nghĩa là gap chưa được xác nhận là session gap, không phải thiếu dữ liệu, và tôi **không** điều tra classifier. Không khẳng định các run 900 ngày sạch lỗi continuity — **chưa test**. Không khẳng định 0,0115–0,0125 chứa tối ưu thật: biên của mặt phẳng là **nơi grid dừng**, không phải nơi đường cong quay đầu. Đoạn dốc xuống (0,015 tệ hơn cả hai lân cận) **chưa động tới**.

Chi tiết: `research/quant/rounds/round335-DATA-ISSUE-no-500-day-exness-xau-run-can-pass-the-gate-and-the-band-optimum-is-a-plateau-not-a-point.md`.

## Round 334 — REJECTED: "~6,8 lệnh/tuần ở cả hai cửa sổ" tan biến khi làm mịn grid; band tối ưu 500 ngày là **0,0125**, đúng vùng mà lập luận volatility dự đoán

Round 333 tự nêu giới hạn: *"tỷ lệ band tối ưu 2,0x là một **grid artifact** — chưa chạy gì giữa 0,01 và 0,02"* và *"tôi **không** khẳng định band scale theo volatility."* Nếu nó thật sự scale thì số học rõ ràng: band tối ưu 900 ngày là 0,01, cửa sổ 500 ngày biến động hơn **1,190x**, nên band tối ưu 500 ngày phải nằm quanh **0,01 × 1,190 = 0,0119** — không phải 0,02 như Round 330 báo cáo.

Đăng ký trước hai chiều: (A) một band quanh 0,0119–0,015 tốt hơn net −0,0301 của 0,02/0,04; (B) cả hai điểm trung gian đều tệ hơn → tối ưu 500 ngày thật sự ở 0,02 và volatility không dự đoán được vị trí band.

**Nhánh A xảy ra.** Grid 500 ngày sau khi làm mịn (`exness XAU`, chi phí deployed, cùng holdout):

| band | lệnh | /tuần | Sharpe | cost÷gross | gross | **net** |
|---|---|---|---|---|---|---|
| 0,01/0,02 (deployed) | 126 | 8,95 | −0,814 | 1,38 | +0,6000 | −0,2283 |
| **0,0125/0,025** | 108 | **7,67** | **−0,041** | **1,02** | **+0,7121** | **−0,0121** |
| 0,015/0,03 | 107 | 7,60 | −0,230 | 1,11 | +0,6499 | −0,0724 |
| 0,02/0,04 | 96 | 6,82 | −0,096 | 1,05 | +0,6067 | −0,0301 |
| 0,04/0,08 | 86 | 6,11 | −0,445 | 1,31 | +0,4460 | −0,1396 |

Ba hệ quả:

1. **Lập luận volatility dự đoán được cả vị trí band, không chỉ hướng** — dự đoán 0,0119, điểm tốt nhất đo được là 0,0125, sai lệch **5%**. Nhưng chỉ hai điểm trung gian được thử và **điểm thấp hơn thắng**, nên tối ưu thật có thể nằm tại hoặc dưới 0,0119: dự đoán định vị được **vùng**, không phải một điểm.
2. **"Interior optimum tại 0,02/0,04" của Round 330 là artifact của grid thô** — net tốt nhất sau khi làm mịn là −0,0121 tại 0,0125, tốt hơn 2,5 lần so với −0,0301.
3. **"~6,8 lệnh/tuần ở cả hai cửa sổ" của Round 332 bị bác bỏ và tôi rút lại nó** — tối ưu 900 ngày 6,85/tuần, tối ưu 500 ngày sau khi làm mịn là **7,67/tuần**, không phải 6,82.

**Target 3 hết xung đột ở cửa sổ này**: Round 328 kết luận cấu hình gần break-even nhất **trượt** mốc 7/tuần; trên grid mịn, cấu hình net tốt nhất chạy **7,67/tuần — nó đạt Target 3**, đồng thời có Sharpe tốt nhất (−0,041), gross tốt nhất (+0,7121) và cost÷gross thấp nhất (1,02) trong mọi cấu hình từng đo trên route này. Xung đột Target 1 / Target 3 vì vậy đúng ở **900 ngày** (tối ưu 6,85/tuần, trượt) và **không** đúng ở 500 ngày khi grid đủ mịn.

**Vẫn trượt gate**: Sharpe −0,041 so với +1,0, tỷ lệ ngày dương 0,405 so với 0,55, cost÷gross 1,02 so với 0,5, net vẫn âm. **Không promote.**

**Giới hạn quan trọng — thứ tự chi tiết chưa được xác lập**: 0,015/0,03 (−0,0724) tệ hơn **cả hai** điểm lân cận, đường net không đơn điệu ở đó, và với biên độ 0,01–0,07 các khoảng cách này có thể là nhiễu giữa cấu hình. Phát biểu vững chắc là: **tối ưu nằm giữa 0,01 và 0,02, không phải tại 0,02**; thứ hạng chính xác của ba điểm giữa thì **chưa**.

Chi tiết: `research/quant/rounds/round334-REJECTED-the-6-8-per-week-coincidence-dissolves-on-a-refined-grid-and-the-volatility-prediction-locates-the-band.md`.

## 0.5. Hướng mới đề xuất sau Round 432 (chưa test) — bar để mở lại research compute

Round 432 audit kết luận không còn cơ chế Alpha/Portfolio nào mở trong ~90
candidate hiện có (mục 3). Hai hướng **thật sự mới**, chưa từng xuất hiện
trong danh sách candidate hay mục 3, do user đề xuất trực tiếp
(2026-09-04), chưa test:

1. **Short-term k-bar return reversal** (autocorrelation reversal cổ điển —
   sau N nến cùng chiều liên tiếp, kỳ vọng đảo chiều). Khác cơ chế RSI
   (oscillator có ngưỡng cố định) và Bollinger (band biến động) — dựa trực
   tiếp vào chuỗi return gần nhất, không cần indicator trung gian.
   **Buildable ngay** trong kiến trúc hiện tại (`trait Strategy::evaluate`
   nhận 1 kline/lần) — implement như 1 `Strategy` mới trong
   `crates/finance-research/src/strategies.rs`, wrap bằng
   `SmaTrendFilterStrategy`/session-filter đã có sẵn để test 2-3 biến thể
   trong 1 lần setup (base + trend filter + session filter — không phải
   ensemble hand-average, đúng pattern wrapper đã dùng cho mọi filter khác
   trong chương trình).
2. **Cross-instrument lead-lag** (return của 1 instrument dự đoán
   instrument khác, vd BTC dẫn XAU). **KHÔNG buildable ngay**: đọc
   `crates/finance-strategy/src/engine.rs:30` xác nhận
   `trait Strategy::evaluate(&self, kline: &Kline)` chỉ nhận đúng 1
   candle của 1 instrument mỗi lần — không có đường nạp dữ liệu instrument
   thứ hai. MTF filter hiện có (`--higher-timeframe-interval`) chỉ nạp thêm
   1 interval khác của CÙNG instrument, không phải instrument khác. Cần
   thay đổi kiến trúc nạp dữ liệu trước khi test được — việc lớn hơn hẳn
   mục 1, nên tách riêng thành 1 round khảo sát thiết kế trước khi backtest.

Ưu tiên: implement + backtest thật mục 1 trước (base signal + factorial
2-3 filter combo, train/validation/holdout đầy đủ). Nếu PF>1 nhất quán
xuất hiện, đó là lý do hợp lệ để mở lại research compute theo bar round432
đã đặt ra. Không cherry-pick tham số riêng lẻ để tạo dáng promotable —
sweep đủ range như mọi mechanism khác trong mục 3 trước khi kết luận.

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
   mở rộng. Chi tiết → `docs/reviews/exness-gap-metadata-continuity.md`.

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
> `research/quant/rounds/round165-target2-interval-weight-floor-proposal.md`. Theo
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
    `research/quant/rounds/round151-risk-fraction-sizing-mode-catastrophic-under-negative-edge.md`.
  - `--portfolio-atr-periods` (chu kỳ ATR khi protective-kind=`atr`) vẫn
    chưa biến thiên — mục duy nhất còn thật sự mở trong Rule 1, ưu tiên
    thấp (protective-kind hiện tại là `fractional`, không phải `atr`, nên
    lever này không áp dụng cho production hiện tại trừ khi đổi protective
    kind trước).
  - **BÀI HỌC QUY TRÌNH QUAN TRỌNG (2026-08-25):** trước khi bắt đầu bất kỳ
    Rule 1 investigation nào, **grep `research/quant/rounds/round8[7-9]*.md` và
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
