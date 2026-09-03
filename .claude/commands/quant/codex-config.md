---
description: "Compatibility command for agent-role Codex candidates"
argument-hint: "[implement|fix|fix-fallback <model> <effort> | reset <role|all>]"
---

Xử lý `$ARGUMENTS` theo đúng một trong các dạng dưới đây. Không dùng `eval`,
không nội suy argument thành shell code và không chấp nhận role khác.

```text
/quant:codex-config
/quant:codex-config <implement|fix|fix-fallback> <model> <effort>
/quant:codex-config reset <implement|fix|all>
```

- Không argument: gọi `uv run --project tools/orchestrator configure-agent-roles show`.
- `implement`: gọi `uv run --project tools/orchestrator configure-agent-roles set implement codex <model> <effort>`.
- `fix`: gọi `uv run --project tools/orchestrator configure-agent-roles candidate-set fix 0 codex <model> <effort>`.
- `fix-fallback`: gọi `uv run --project tools/orchestrator configure-agent-roles candidate-set fix 1 codex <model> <effort>`.
- Reset role/all dùng `uv run --project tools/orchestrator configure-agent-roles reset <role>` hoặc `reset-all`.

Đây là alias migration; interface authoritative là
`configure-agent-roles`, hỗ trợ cả PLAN/VERIFY/FINAL_VERIFY và Claude.
Command không thay đổi provider health, không bắt đầu research và không chạy Codex.
