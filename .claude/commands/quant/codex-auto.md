---
description: "Tự phát hiện Codex availability cho mỗi vòng quant research"
---

Chạy tuần tự đúng một lần mỗi lệnh:

```bash
uv run --project tools/orchestrator phase-agent-state provider-auto codex
uv run --project tools/orchestrator detect-provider-availability codex
```

Không bắt đầu research và không retry probe. Dù probe kết luận available,
unavailable hay inconclusive, provider mode vẫn là auto; resolver chỉ probe lại
khi cooldown cho phép.
Chỉ báo kết quả ngắn gọn bằng tiếng Việt; không in raw state JSON, probe log,
prompt, stderr hoặc thông tin xác thực.
