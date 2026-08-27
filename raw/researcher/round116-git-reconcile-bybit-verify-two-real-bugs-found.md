# Round 116 (2026-08-23) — Reconcile git divergence lớn, verify fix funding-retry (Round 112) + deploy Bybit, phát hiện 2 bug thật đang chặn cả 2 route Bybit

Status: production verification + git reconciliation, không backtest candidate
mới. Reconcile `finance-live-action` local dirty tree với 17 commit mới từ
Codex (bao gồm Round103-114 research absorption + fix funding retry + full
Bybit deploy).

## Bối cảnh

Đầu round phát hiện `origin/main` (finance-live-action) đã vượt xa
local HEAD (`2840dcc` → `7d85cdb`, 17 commit) — Codex đã absorb toàn bộ
candidate research của tôi (Ichimoku/SAR/CCI/OBV/Fibonacci/Engulfing/
Heikin-Ashi...) thành commit sạch, fix đúng finding Round 112
(`is_retryable()` classification gap), VÀ triển khai xong task Bybit đã log
ở phiên trước ("`Add Bybit as a third live broker`").

## 1. Reconcile git — theo đúng pattern đã dùng nhiều lần trước

Backup 4 file dirty (`strategies.rs`, `indicators.rs`, `cci.rs`, `mfi.rs`) →
`git checkout --` 2 file đã absorb + xóa `cci.rs` trùng → `git merge
--ff-only origin/main` (fast-forward sạch, không conflict) → thêm lại module
`mfi` (chưa được Codex absorb, work mới nhất Round 114) vào đúng vị trí
logic (giữa CCI và OBV trong `strategies.rs`, cùng nhóm oscillator) →
rebuild + test toàn workspace. Kết quả: `cargo test --workspace --exclude
finance-redis` **0 lỗi mọi crate** (211+123+82+... pass), `cargo fmt --check`
sạch. `git status --short` giờ chỉ còn đúng phần MFI local (đang chờ Codex
review như quy trình cũ).

## 2. Verify fix funding-retry (Round 112 finding) — xuất sắc, đúng lo ngại TRA-928

Đọc commit `8a20cb0` (`fix(funding): retry local tonic transport status`):
Codex KHÔNG chỉ đơn giản thêm `Code::Unknown` vào danh sách retryable (rủi
ro tái diễn TRA-928 như tôi đã cảnh báo), mà thêm điều kiện chính xác hơn —
chỉ coi `Unknown`+"transport error" là retryable **khi `status.source()` là
đúng kiểu `tonic::transport::Error`** (phân biệt transport thật khỏi lỗi
data/logic phía server giả dạng cùng message). Có regression test riêng
tên `unknown_tonic_transport_status_is_retryable_but_poison_unknown_is_fatal`
chứng minh cả 2 case đều đúng. Toàn bộ workspace test xanh xác nhận không
phá gì. Đây là ví dụ tốt về việc để đúng người ra quyết định (tôi đã chủ
động ghi rõ "cần Codex judgment, không phải Quant-side decision" ở Round
112 — kết quả đúng như kỳ vọng).

## 3. Verify deploy Bybit — production thật, 2 route mới, nhưng cả 2 đều đang bị chặn

`curl /api/v1/system/version` xác nhận 4 route cũ đã lên `7d85cdb5...`.
`ssh docker ps` xác nhận thêm 2 container mới:
`live-action-bybit-perpetual-future-btc-usdt-*` và
`live-action-bybit-spot-xaut-usdt-*`, cả 2 `healthy`, đúng exact SHA.

**Nhưng health ≠ ready** — kiểm tra log/checkpoint kỹ hơn phát hiện cả 2
route đều chưa hoạt động thật:

### Bug 1 — BTC linear: `normalizeBybitRiskLimits` từ chối tier `maxLeverage` phân số

Log lặp lại mỗi 20s: `"leverage constraints unavailable: invalid Bybit risk
limit"` (attempt 22+ và tăng liên tục). Đã tự root-cause chính xác: fetch
trực tiếp `GET /v5/market/risk-limit?category=linear&symbol=BTCUSDT` (35
tier) rồi replay lại đúng validation logic Go (`leverage_constraints.go:
445-472`) bằng Python cho từng row — tier `id=34` (bracket notional cao
nhất, `riskLimitValue=800000000`) có `"maxLeverage": "1.43"` — **giá trị
phân số thật**. Check `maxLeverage != math.Trunc(maxLeverage)` (viết theo
kiểu Binance leverage nguyên) từ chối đúng row này, và vì loop return lỗi
ngay khi gặp row xấu, **toàn bộ 35 tier bị "đầu độc"** — worker không bao
giờ load được leverage constraints, retry vô hạn, không bao giờ ready.
Checkpoint Redis `bybit.perpetual_future.btc.usdt.5m` chưa hề tồn tại.

### Bug 2 (khác nguyên nhân) — XAUT spot: MW chưa ingest instrument này

Log: `"instrument not found in finance-mw instrument stream:
bybit.spot.XAUT.USDT"` lặp mỗi 60s, `pending_intervals` liệt kê đủ 8
interval. Đây là do phía kline-ingest (Go, MW) chưa được wire cho Bybit —
đúng thứ tự xây dựng đã ghi trong task doc gốc (ingestion → worker → web UI)
nhưng bị deploy lệch thứ tự (worker đã lên trước ingestion). Checkpoint
Redis tồn tại nhưng `evaluation_count=0`, không tiến triển.

Đã log đầy đủ 2 phát hiện này thành 1 Todo `[trading][high]` chi tiết trong
`handoff_agent.md`, chỉ nêu bằng chứng + root cause, để nguyên quyết định
cách sửa cho Codex (không tự đề xuất giải pháp Go code cụ thể).

## 4. Tự sửa 1 claim sai của chính mình (Round 113)

Codex audit đúng: tiêu đề Round 113 gọi OBV là "candidate volume-là-tín-hiệu-
chính đầu tiên" — sai, vì `TakerImbalanceStrategy` (Round 72-75, đã đóng từ
trước) đã dùng volume làm tín hiệu chính rồi. Đã sửa lại minh bạch (addendum,
không xóa lịch sử) trong file round113 và SUMMARY — OBV chỉ là candidate đầu
tiên dùng **cumulative signed total-volume**, không phải "volume-primary" nói
chung. Không đổi số liệu/kết luận CLOSED.

## Kết luận

Round giá trị cao dù không có backtest mới: reconcile sạch, verify 1 fix
chất lượng cao của Codex, và **phát hiện 2 bug thật** đang chặn hoàn toàn
tính năng Bybit vừa deploy (nếu không kiểm tra kỹ, health=healthy sẽ dễ bị
hiểu nhầm là đã hoạt động).

## Việc cho round sau

- Theo dõi Codex xử lý 2 bug Bybit; verify lại sau khi fix (checkpoint phải
  bắt đầu tiến triển ở cả 2 route).
- Round102 XAU/Exness weekend-reopen follow-up vẫn chờ 22:00 UTC.
