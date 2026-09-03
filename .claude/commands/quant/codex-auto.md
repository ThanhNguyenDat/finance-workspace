---
description: "Tự phát hiện Codex availability cho mỗi vòng quant research"
---

Chạy tuần tự đúng một lần mỗi lệnh:

```bash
./.agents/scripts/phase-agent-state.py provider-auto codex
./.agents/scripts/detect-provider-availability.py codex
```

Không bắt đầu research và không retry probe. Dù probe kết luận available,
unavailable hay inconclusive, provider mode vẫn là auto; resolver chỉ probe lại
khi cooldown cho phép.
Chỉ báo kết quả ngắn gọn bằng tiếng Việt; không in raw state JSON, probe log,
prompt, stderr hoặc thông tin xác thực.
