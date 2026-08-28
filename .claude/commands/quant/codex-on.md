---
description: "Bật lại Codex cho các vòng quant research kế tiếp"
---

Chạy lệnh state helper sau đúng một lần:

```bash
./.agents/scripts/quant-research-state.sh codex-on
```

Không bắt đầu research và không khởi động lại `/loop`. Khi lệnh thành công,
chỉ xác nhận bằng tiếng Việt rằng vòng `/quant-research` kế tiếp sẽ đọc
`codex_available=true` và trở về chế độ Codex bình thường. Không in raw JSON
runtime trừ khi người dùng yêu cầu debug.
