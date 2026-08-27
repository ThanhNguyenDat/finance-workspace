# Finance workspace agent contract

## Phạm vi

`finance-workspace` là repository điều phối chung cho hệ sinh thái Finance:
spec, runbook, sơ đồ, skill, research artifact và kênh handoff giữa Claude và
Codex. Code chạy thật vẫn thuộc các repository chuyên trách:

- `finance-mw`: Go middleware/API, migrations và web gateway.
- `finance-web`: React/Vite browser application.
- `finance-live-action`: Rust strategy, Portfolio và live worker.
- `finance-broker`: broker adapters và execution.
- `mt5`: MT5 adapter.

Các checkout trên thường nằm cạnh workspace. Không sao chép code runtime vào
workspace và không sửa production trực tiếp từ workspace.

## Luồng làm việc

- Mỗi vòng bắt đầu bằng `raw/handoff_agent.md`, sau đó đọc research note mới
  nhất và các file spec/runbook liên quan.
- Giữ đúng các mục `Todo`, `Processing`, `Dev-done`, `Verify`, `Done`; Claude
  là người đóng `Done` sau khi review độc lập.
- Task code được thực hiện trong repository sở hữu code, với một worktree/owner
  riêng cho mỗi task độc lập. Workspace chỉ ghi nhận kế hoạch và bằng chứng.
- Không bỏ qua dependency giữa repository, replay contract, protobuf hoặc
  immutable revision. Khi code và tài liệu khác nhau, code/test/deployed state
  có bằng chứng trực tiếp được ưu tiên; cập nhật tài liệu sau đó.
- Giao tiếp với owner và ghi handoff bằng Tiếng Việt, múi giờ UTC+7. Không ghi
  credential, token, cookie, password hoặc payload nhạy cảm vào workspace.

## Delivery

- Code, configuration và deploy của các service đi theo commit → local check →
  GitHub Actions → immutable image → Coolify → production verification trong
  repository sở hữu.
- Hạ tầng dùng chung (Kafka, Grafana, Elasticsearch/OpenSearch, OTel/Tempo,
  Coolify resource) và audit/repair một lần dùng live-first lane có kiểm soát;
  không tạo workflow GitHub chỉ để thay cho thao tác hạ tầng.
- Khi owner yêu cầu giữ push gate, được commit local nhưng không push, CI,
  Coolify hoặc production mutate cho tới khi owner mở gate.
- Sau deploy phải xác nhận đúng SHA/image, hành vi thật, data/progress,
  observability, host safety và rollback readiness. Health 200 hoặc container
  xanh không tự chứng minh business behavior.
- Không dùng lệnh phá hủy trên workspace hoặc các checkout code nếu chưa xác
  định target và có sự cho phép phù hợp.

## Tài liệu và skill

`.agents/rules/` là quy tắc dùng chung; `.agents/skills/` là skill dùng trong
workspace và các checkout. Nếu skill trỏ sang file trong repository chuyên
trách, đọc bản đang deploy/đang sửa ở repository đó thay vì đoán từ tài liệu
cũ. `docs/` là spec/runbook/sơ đồ; `raw/` là handoff và research history, được
giữ lại để audit và không tự ý rewrite lịch sử.

## Attribution

Commit dùng conventional subject. Commit của Codex có
`Co-Authored-By: Codex <noreply@openai.com>`; commit của Claude có
`Co-Authored-By: Claude <noreply@anthropic.com>`.
