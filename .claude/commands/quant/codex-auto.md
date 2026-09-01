---
description: "Tự phát hiện Codex availability cho mỗi vòng quant research"
---

Chạy tuần tự đúng một lần mỗi lệnh:

```bash
./.agents/scripts/quant-research-state.sh codex-auto
./.agents/scripts/detect-codex-availability.sh
```

Không bắt đầu research, không dừng hoặc khởi động lại `/loop`, và không retry
probe. Dù probe kết luận available, unavailable hay inconclusive,
`codex_mode=auto` vẫn được giữ để `/quant-research` tự probe lại ở đầu mỗi vòng.
Chỉ báo kết quả ngắn gọn bằng tiếng Việt; không in raw state JSON, probe log,
prompt, stderr hoặc thông tin xác thực.
