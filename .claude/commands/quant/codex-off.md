---
description: "Đánh dấu Codex tạm thời không khả dụng cho quant research"
---

Chạy lệnh state helper sau đúng một lần:

```bash
./.agents/scripts/phase-agent-state.sh provider-off codex
```

Không bắt đầu research, không khởi động Codex, không dừng hoặc khởi động lại
research. Khi lệnh thành công, chỉ xác nhận bằng tiếng Việt rằng các attempt
phase-agent kế tiếp sẽ bỏ qua Codex và chọn candidate khả dụng tiếp theo. Không
in raw JSON runtime trừ khi người dùng yêu cầu debug.
