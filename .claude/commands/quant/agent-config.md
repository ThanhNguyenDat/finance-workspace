---
description: "Xem và cấu hình provider/model/effort cho agent roles"
argument-hint: "[show|set|candidate-set|reset|reset-all|pin|auto|provider-on|provider-off|provider-manual|provider-auto ...]"
---

Chuyển `$ARGUMENTS` sang đúng một invocation allowlisted của:

```text
uv run --project tools/orchestrator configure-agent-roles <operation> ...
```

Không dùng `eval`, không in raw state JSON, không khởi động research/model
worker và không thay đổi attempt đang chạy. Các role hợp lệ là
`quant-research`, `plan`, `implement`, `verify`, `fix`, `final-verify`; provider
hợp lệ là `codex|claude`. Opus chỉ nhận effort `medium|high`, với `high` dành
cho role rất khó.
