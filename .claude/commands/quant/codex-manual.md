---
description: "Chuyển Codex availability về chế độ điều khiển thủ công"
---

Chạy state helper sau đúng một lần:

```bash
./.agents/scripts/quant-research-state.sh codex-manual
```

Không thay đổi `codex_available`, không chạy probe, không bắt đầu research và
không dừng hoặc khởi động lại `/loop`. Khi thành công, xác nhận ngắn gọn bằng
tiếng Việt rằng các vòng sau sẽ giữ resolved availability hiện tại cho tới khi
chạy `/quant:codex-on`, `/quant:codex-off` hoặc `/quant:codex-auto`. Không in raw
runtime JSON.
