---
description: "Chuyển Codex availability về chế độ điều khiển thủ công"
---

Chạy state helper sau đúng một lần:

```bash
uv run --project tools/phase-agent-orchestrator phase-agent-state provider-manual codex
```

Không thay đổi resolved availability, không chạy probe và không bắt đầu research.
Khi thành công, xác nhận ngắn gọn bằng
tiếng Việt rằng các vòng sau sẽ giữ resolved availability hiện tại cho tới khi
chạy `/quant:codex-on`, `/quant:codex-off` hoặc `/quant:codex-auto`. Không in raw
runtime JSON.
