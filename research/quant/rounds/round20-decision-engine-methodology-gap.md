# Round 20 (2026-08-20) — Phát hiện phương pháp luận quan trọng: `finance-research` không chạy đúng engine quyết định thật

Status: research-only, không code/deploy. Đây là phản hồi trực tiếp câu hỏi
của user: *"backtest là bạn nên chạy finance-live-action thật sự luôn chứ,
không chỉ finance-research"*. Đã đọc code để trả lời chính xác thay vì suy
đoán.

## Câu hỏi được trả lời bằng code, không phải giả định

Grep toàn bộ `crates/finance-research/src/*.rs` cho
`PortfolioDecisionPolicy`/`MultiTimeframePortfolioPolicy` (2 engine quyết
định thật, `finance-core/src/trading_modes.rs:267` và `:711` — chính là cái
mà production dùng, đã root-cause nhiều lần trong log trước, vd
"MultiTimeframePortfolioPolicy::decide() cần entry_score VÀ trend_score đều
vượt ngưỡng 0.10 và đồng dấu"):

- **Chỉ xuất hiện đúng 1 chỗ**: `lookahead_analysis.rs` — dùng cho 1 việc hẹp
  (kiểm tra lookahead correctness), KHÔNG phải path tạo ra bảng sweep/gate mà
  toàn bộ round 1-19 dựa vào.
- **`main.rs`'s `portfolio_execution`** (qua `portfolio_measurement.rs`) và
  **`daily_profit_gate.rs`** — cả 2 đường dẫn tạo ra MỌI số liệu tôi đã report
  từ round 1 tới giờ — đều tự map trực tiếp `signal_type != Hold` →
  `PortfolioDecision`, hoàn toàn bỏ qua việc tổng hợp evidence đa-interval,
  đa-strategy, trọng số theo `reweight_from_alpha_performance`, và ngưỡng
  đồng thuận entry/trend-score mà `decide()` thật yêu cầu.
- **Không phải bug, mà là scope mismatch có ghi chú rõ ràng trong chính code**
  (`portfolio_measurement.rs` dòng 1-8): *"Both paths consume the same
  strategy decision on the same candle... measures the execution footprint
  before and after the Portfolio boundary"* — tool này được thiết kế để so
  sánh **hành vi sizing/risk-gate** giữa 2 kiểu execution khi ĐÃ có sẵn 1
  quyết định, không phải để mô phỏng việc Portfolio có QUYẾT ĐỊNH hay không.

## Ý nghĩa thật sự — phải nói rõ, không giấu

**Mọi con số PF/Sharpe/Sortino/win-rate tôi đã report ở Round 1-19 (và cả
phần lớn log 62 dòng gốc `optimize_loop_update.csv` trước session `/loop`
này) trả lời đúng câu hỏi "tín hiệu này có lời không nếu Portfolio LUÔN LUÔN
làm theo nó" — KHÔNG trả lời được câu hỏi "nếu đưa tín hiệu này vào ensemble
thật, Portfolio's real decision engine có thực sự quyết định trade thường
xuyên hơn không (Target 2)".** Đây là khác biệt quan trọng vì:

- Target 2 của user (tăng tỉ lệ Make Decision) do chính `decide()` thật quyết
  định — phụ thuộc `interval_weights`, `alpha_performance_quality` trọng số
  theo hiệu suất, và yêu cầu đồng thuận entry+trend score qua NHIỀU interval
  cùng lúc — không phải thuộc tính của 1 signal đơn lẻ.
- Các kết luận "candidate X không đạt Target 3 (tần suất)" ở Round 17-19 vẫn
  đúng theo nghĩa hẹp (tần suất RAW của chính signal đó khi chạy solo) —
  nhưng KHÔNG chứng minh được rằng đưa signal đó vào ensemble thật (cộng dồn
  với các signal khác đang live) sẽ hay sẽ không cải thiện tần suất quyết
  định thật của Portfolio. Có thể signal yếu tự nó nhưng khi cộng dồn điểm số
  với 1-2 signal khác lại đủ vượt ngưỡng 0.10 thường xuyên hơn — điều này
  hoàn toàn không đo được bằng tool hiện tại.

## Đã cân nhắc và KHÔNG làm ngay: tự chạy `finance-api` (binary thật) local

Đã kiểm tra khả năng chạy đúng binary `finance-api` (chính là
`finance-live-action` production, dùng `decide()` thật) local để test —
đây chính xác là điều user đề xuất. Rào cản thật, không phải cái cớ:

1. `finance-api` import `finance_kafka::KafkaConsumer` trực tiếp trong
   `main.rs` — cần Kafka thật để khởi động, không có chế độ "replay-only,
   không cần Kafka" nào lộ ra qua CLI (không dùng `clap`, cấu hình hoàn toàn
   qua biến môi trường).
2. `docker/compose.dev.yaml`'s `live-action-dev` service dựa vào biến môi
   trường mặc định từ `docker/env/production.env` (duy nhất tồn tại,
   `KAFKA_BROKERS=finance-kafka-node1:9092` — hostname production thật) —
   không có sẵn 1 profile "local-isolated" nào override đủ để đảm bảo an
   toàn 100% không chạm production Redis/Kafka nếu tôi tự chạy vội.
3. Rủi ro thật nếu làm sai: nếu container tự lên và vô tình resolve/connect
   được production Kafka/Redis (network `finance: external: true` gợi ý nó
   mong đợi join đúng network production), có thể ghi đè checkpoint thật
   hoặc publish sai dữ liệu — đây là loại rủi ro "khó đảo ngược, ảnh hưởng hệ
   thống chung" cần cẩn trọng, không nên vội trong 1 vòng 15 phút.

**Quyết định: không tự dựng harness này vội vàng dưới áp lực thời gian —
thay vào đó log đề xuất cụ thể, phạm vi hẹp, rủi ro thấp hơn nhiều cho Codex
(xem `docs/archive/legacy-handoff-agent.md`).**

## Đề xuất cụ thể (đã log cho Codex, chưa tự làm)

Cách sửa rẻ và an toàn hơn nhiều so với dựng lại toàn bộ live server local:
**mở rộng `finance-research` để tự gọi đúng `PortfolioDecisionPolicy::decide()`/
`MultiTimeframePortfolioPolicy::decide()` thật** (thay vì tự map signal→
decision) khi build `portfolio_execution`/gate report — vẫn dùng lại đúng
lightweight CLI, đúng cách tôi đang chạy qua tunnel read-only, không cần
Kafka/Redis riêng, không rủi ro production. Đây là scope hẹp: đổi 1 hàm
mapping trong `portfolio_measurement.rs`/`daily_profit_gate.rs` để dùng
evidence book thật thay vì decision giả lập từ 1 signal — không phải viết
lại kiến trúc.

## Việc cần làm ở các round sau

Không rewrite lại toàn bộ 19 round trước (không có bằng chứng số cụ thể sai
— PF/Sharpe của từng signal solo vẫn đúng và hữu ích làm bước lọc sơ bộ Alpha
layer). Nhưng **từ giờ, mọi kết luận về Target 2 (Make Decision rate) phải
gắn caveat này** cho tới khi `finance-research` (hoặc 1 harness an toàn khác)
thực sự chạy qua `decide()` thật. Cột `target2_makedecision` trong CSV v2 đã
để `n/a` cho hầu hết dòng Alpha-layer từ trước — hoá ra đúng hướng thận trọng,
giờ có lý do rõ ràng để tiếp tục giữ vậy cho tới khi có harness đúng.
