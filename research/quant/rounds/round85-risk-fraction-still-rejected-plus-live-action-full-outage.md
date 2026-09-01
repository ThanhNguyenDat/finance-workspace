# Round 85 (2026-08-22) — 2 phát hiện lớn: `risk_fraction` vẫn bị Risk gate từ chối gần hết dù đã có fix Round 84, và Live Action production đang HOÀN TOÀN down (không phải chỉ suy giảm)

Status: research + production read-only verify. Không implement/commit gì (đang ở
chế độ narrowed rule — Codex có quota, xem `feedback_deploy_ownership`). Đồng
thời phát hiện bằng chứng writer xung đột (mục 0) — đã dừng tự bắt đầu việc
implement mới theo Rule 0b, chỉ tiếp tục research/verify.

## 0. Bằng chứng writer xung đột (đã xác nhận độc lập, không phải do phiên này gây ra)

Codex tự log trong `handoff_agent.md` Processing: lúc 17:38:14 UTC+7, trong khi
Codex đang xử lý queue từ HEAD `8b9b344`, có commit `ee7621deb6502952fda846a07e28a34ea6f87841`
push thẳng lên `main` (finance-mw). Đã verify độc lập qua `git show`:
- Author: `thanhnd13 <thanhnd13@vng.com.vn>` (chính git identity của owner).
- Message: "refactor: Implement shared-driver architecture for historical
  portfolio replay" — nhắc tới `HistoricalPortfolioDriver`, bump contract
  version lên 19.
- Diff thực tế: CHỈ đổi `.gitignore` (+`raw/`) và xoá 7.750 dòng tài liệu cũ
  dưới `raw/` (`portfolio-btc-optimization-log.md`,
  `portfolio-btc-target-tracking.md`, `portfolio-multi-entry-per-candle.md`,
  `refactor.md`, `todo.md`, 3 ảnh). KHÔNG có dòng code Rust nào trong diff.
- Đối chiếu: `HistoricalPortfolioDriver`/`HistoricalPortfolioRuleReplay` đã tồn
  tại sẵn trong `finance-live-action/crates/finance-api/src/trading_api.rs` từ
  trước (contract version hiện tại = 26, không phải 19) — message hoàn toàn
  không khớp với repo/diff nào cả. Nội dung xoá `raw/` thì HỢP LÝ (đã verify:
  các file bị xoá đều có bản sao ở `raw/researcher/`/`docs/reviews/`, không mất
  dữ liệu) — vấn đề chỉ là message sai lệch nghiêm trọng, dấu hiệu có agent
  khác đang thao tác song song và nhầm lẫn phạm vi commit.

**Hành động:** không tự sửa/revert commit này (nội dung diff vô hại), không tự
bắt đầu việc implement mới cho tới khi owner xác nhận trạng thái thực (đúng
ngoại lệ Rule 0b). Tiếp tục phần research/backtest/verify (vẫn được phép).

## 1. PHÁT HIỆN NGHIÊM TRỌNG HƠN: Live Action production HOÀN TOÀN down, không có container nào

`docker ps -a` trên host `my` (160.22.122.55) lúc kiểm tra (~17:47 UTC+7,
2026-08-22): **0 container tên `live-action-*`** — không phải crash-loop, mà
hoàn toàn không tồn tại (không có cả bản đã dừng). `finance-mw-1` log liên tục
lỗi DNS cho cả 4 route:

```
lookup live-action-binance-perpetual-future-btc-usdt on 127.0.0.11:53: no such host
lookup live-action-binance-perpetual-future-xau-usdt on 127.0.0.11:53: no such host
lookup live-action-exness-cfd-btc-usd on 127.0.0.11:53: no such host
lookup live-action-exness-cfd-xau-usd on 127.0.0.11:53: no such host
```

Nghiêm trọng hơn item đang "Processing" trong `handoff_agent.md`
("cascading into Live Action transport failures... WRONGPASS restart loops
now being fixed forward") — item đó mô tả suy giảm/restart-loop, thực tế hiện
tại là **mất hẳn container, kể cả Docker DNS record cũng không còn** — tức là
Coolify đã gỡ hẳn service này (có thể là bước giữa của quy trình redeploy do
Codex đang fix-forward Redis-credential/OOM incident).

**Trạng thái khắc phục đang diễn ra:** `gh run view 32503588264`
(finance-live-action, "Build and Deploy") đang `in_progress`, "Triggered via
push about 3 minutes ago" tại thời điểm kiểm tra — tái trigger cho commit
`31ed149` (round 83, không đổi nội dung). Nhiều khả năng đây là bước Codex
đang chủ động redeploy để khôi phục. Round sau (15 phút tới) cần verify lại
xem 4 container đã quay lại chưa và checkpoint có tiếp tục advance không —
**KHÔNG coi CI xanh hay Coolify "deployed" là bằng chứng đủ**, phải thấy lại
`docker ps` có đủ 4 container + `evaluation_count` tiếp tục tăng.

**Tác động tới Target 1/2/3:** trong lúc down, Make Decision rate = 0 tuyệt
đối cho cả 4 route — không phải "tần suất thấp", mà là hoàn toàn không hoạt
động. Đây là ưu tiên cao nhất hiện tại, trên cả 2 phát hiện research bên dưới.

## 2. `risk_fraction` sizing (rule `risk-2pct`, đang chạy thật production) vẫn bị Risk gate từ chối ~99.8% dù đã áp fix Round 84

### Bối cảnh

Round 84 đã fix + đã test kỹ `equity_fraction` (rule `compounding-10pct`):
sau fix, `risk_rejected_counts.risk == 0`, có regression test riêng xác nhận.
Round 84 để lại 1 việc "cân nhắc, không bắt buộc": test tiếp `risk_fraction`
(rule `risk-2pct`) — round này làm đúng việc đó, dùng chính docker image đã
build với fix Round 84 (vẫn đang UNCOMMITTED trong working tree
finance-live-action, xem mục 0/round84 — không commit thêm gì).

### Cấu hình test (khớp chính xác rule `risk-2pct` live, `deployment_rules.rs:84-98`)

`--portfolio-sizing-mode risk_fraction --portfolio-sizing-value 0.02
--portfolio-protective-kind fractional --portfolio-stop-value 0.01
--portfolio-take-value 0.02 --portfolio-atr-periods 14
--portfolio-minimum-hold-decisions 36 --fee-bps 5 --slippage-bps 2`
(hold=36, stop/take=0.01/0.02 là default hiện tại của CLI, khớp production).
`--days 1825`, holdout ~365 ngày mỗi route (trừ XAU/binance chỉ có ~85 ngày
lịch sử).

### Kết quả (qua `one_target`, đã dùng đúng fix widening)

| Route | leverage | decision_count | `one_target.trades` | risk-rejected | % rejected |
|---|---|---|---|---|---|
| BTC/binance | 10x | 525,152 | 2 | 524,297 | 99.8% |
| BTC/exness | 1x | 524,839 | 1 | 523,993 | 99.8% |
| XAU/binance | 10x | 72,993 | 8 | 0 | 0% |
| XAU/exness | 1x | 337,314 | 1 | 335,816 | 99.6% |

3/4 route gần như KHÔNG bao giờ trade được — `one_target.trades` chỉ 1-2 lệnh
trong CẢ NĂM holdout (so sánh: `fixed_notional`/`equity_fraction` cùng
decision stream cho ra 2432 trade ở BTC/binance theo Round 84). XAU/binance là
ngoại lệ duy nhất (0% rejected, 8 trade) — chưa rõ nguyên nhân khác biệt,
leverage giống hệt BTC/binance (10x) nên không phải do leverage đơn thuần.

### Đánh giá trung thực — CHƯA xác định được root cause chính xác

Đã thử tính tay công thức `RiskFraction::notional = (equity * risk_fraction)
/ stop` (`trading_modes.rs:1287-1295`) và đối chiếu với
`widened_for_simulation`'s one-time snapshot cap (`portfolio_risk.rs:249-301|
259-301`) — công thức tay cho thấy lệnh ĐẦU TIÊN lẽ ra phải lọt qua cap (cap
được set đúng bằng `initial_notional`/`initial_equity_fraction`), nhưng thực
nghiệm cho thấy ngay cả sau vài lệnh đã bị từ chối gần như tuyệt đối. Giả
thuyết khả dĩ nhất (CHƯA verify bằng code/debug): risk gate re-evaluate
notional mỗi chu kỳ quyết định (kể cả khi giữ nguyên vị thế, mark-to-market),
và cap widen chỉ tính 1 lần từ equity BAN ĐẦU nên không theo kịp biến động
giá/equity qua hàng trăm nghìn chu kỳ trong 1 năm — nhưng chưa đủ bằng chứng
để khẳng định, và không giải thích được vì sao XAU/binance lại 0%. Cần Codex
đọc code risk-gate path (`PortfolioRiskGate`/nơi gọi `evaluate` mỗi decision
cycle) hoặc thêm log debug thay vì suy đoán tiếp bằng tay.

### Ý nghĩa cho production

Rule `risk-2pct` đang chạy song song thật trên cả 4 route production (không
phải candidate nghiên cứu — `configured_portfolio_rules()` luôn include cả 3
rule `fixed-pct`/`risk-2pct`/`compounding-10pct`). Nếu cơ chế risk-gate y hệt
đang áp dụng cho ledger thật trên production (rule `trading_api.rs` dùng
CHUNG code path này, xác nhận ở Round 84), **`risk-2pct` có thể gần như không
bao giờ trade thật trên 3/4 route** — cần verify trực tiếp qua
`simulated_ledgers.paper-risk-2pct-scope-*` trong checkpoint Redis (**chưa
làm được round này** vì Live Action đang down hoàn toàn — mục 1 — không đọc
được checkpoint mới; sẽ verify ngay khi service quay lại).

## Việc cho round sau / Codex

1. **Ưu tiên tuyệt đối:** verify Live Action đã có đủ 4 container trở lại
   chưa, `evaluation_count` có tiếp tục tăng không (mục 1).
2. Sau khi Live Action sống lại: đọc `simulated_ledgers.paper-risk-2pct-scope-*`
   cho cả 4 route, so `trade_count`/`realized_pnl` với `paper-fixed-pct-scope-*`
   cùng route — xác nhận (hoặc bác bỏ) giả thuyết "risk-2pct gần như không
   trade thật trên production" ở mục 2.
3. Nếu xác nhận đúng: đây là bug thật ảnh hưởng trực tiếp Target 2 cho 1/3
   rule Portfolio đang chạy — cần Codex đọc source risk-gate re-evaluation
   path để tìm root cause chính xác (không đoán), rồi mới quyết định fix.
4. Không commit gì thêm vào diff Round 84 hiện có cho tới khi Codex tự
   review/commit (round này chỉ CHẠY THỬ bằng docker image đã build sẵn từ
   diff đó, không sửa thêm dòng code nào).
