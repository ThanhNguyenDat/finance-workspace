---
description: "Đánh dấu Codex tạm thời không khả dụng cho quant research"
---

Chạy lệnh state helper sau đúng một lần:

```bash
./.agents/scripts/quant-research-state.sh codex-off
```

Không bắt đầu research, không khởi động Codex, không dừng hoặc khởi động lại
`/loop`. Khi lệnh thành công, chỉ xác nhận bằng tiếng Việt rằng các vòng
`/quant-research` kế tiếp sẽ đọc `codex_mode=manual`,
`codex_available=false` và dùng chế độ Claude fallback khi cần implement. Không
in raw JSON runtime trừ khi người dùng yêu cầu debug.
