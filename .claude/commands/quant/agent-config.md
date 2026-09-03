---
description: "Xem và cấu hình provider/model/effort cho phase agents"
argument-hint: "[show|set|candidate-set|reset|reset-all|pin|auto|provider-on|provider-off|provider-manual|provider-auto ...]"
---

Chuyển `$ARGUMENTS` sang đúng một invocation allowlisted của:

```text
uv run --project tools/orchestrator configure-phase-agents <operation> ...
```

Không dùng `eval`, không in raw state JSON, không khởi động research/model
worker và không thay đổi attempt đang chạy. Các phase hợp lệ là
`quant-research`, `plan`, `implement`, `verify`, `fix`, `final-verify`; provider
hợp lệ là `codex|claude`. Opus chỉ nhận effort `medium|high`, với `high` dành
cho phase rất khó.
