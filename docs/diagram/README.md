# Finance Workflow Diagrams

Tài liệu trong thư mục này mô tả luồng giao dịch hiện tại từ `finance-web`
đến `finance-mw`, `finance-live-action`, worker state và các datastore.

- [Bản review có Mermaid cho VS Code/Obsidian](finance-live-action-workflow.md)
- [Bản nhiều page cho Draw.io](finance-live-action-workflow.drawio)
- [Runbook vận hành market data](../runbooks/market-data-live-action.md)

Hai bản sơ đồ đều tách rõ interval universe của MW, realtime ingest intervals và
active `5m/15m/1h/4h` strategy bundle; không dùng bốn interval này để đại diện
cho toàn hệ thống.

## Cách mở

- Draw.io: mở trực tiếp `finance-live-action-workflow.drawio` bằng
  <https://app.diagrams.net/>, Draw.io Desktop hoặc extension Draw.io Integration
  trong VS Code.
- VS Code: preview file Markdown bằng `Markdown: Open Preview`; để render Mermaid
  cần VS Code/extension có hỗ trợ Mermaid.
- Obsidian: mở vault tại repository này rồi preview
  `finance-live-action-workflow.md`. Mermaid được render trực tiếp.

Các sơ đồ phân biệt rõ ba trạng thái:

- **WIRED**: đang nằm trên runtime path hiện tại.
- **IMPLEMENTED, NOT WIRED**: đã có domain contract/module nhưng worker chưa gọi.
- **TARGET**: hướng thiết kế, không được hiểu là production behavior.
