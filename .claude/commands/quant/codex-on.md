---
description: "Bật lại Codex cho các vòng quant research kế tiếp"
---

Chạy lệnh state helper sau đúng một lần:

```bash
uv run --project tools/orchestrator agent-role-state provider-on codex
```

Không bắt đầu research. Khi lệnh thành công, chỉ xác nhận bằng tiếng Việt rằng
Codex ở manual available và các attempt kế tiếp có thể chọn Codex.
Không in raw JSON runtime trừ khi người dùng yêu cầu debug.
