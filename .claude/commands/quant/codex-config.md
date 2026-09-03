---
description: "Compatibility command for phase-agent Codex candidates"
argument-hint: "[implement|fix|fix-fallback <model> <effort> | reset <phase|all>]"
---

Xử lý `$ARGUMENTS` theo đúng một trong các dạng dưới đây. Không dùng `eval`,
không nội suy argument thành shell code và không chấp nhận role khác.

```text
/quant:codex-config
/quant:codex-config <implement|fix|fix-fallback> <model> <effort>
/quant:codex-config reset <implement|fix|all>
```

- Không argument: gọi `uv run --project tools/orchestrator configure-phase-agents show`.
- `implement`: gọi `uv run --project tools/orchestrator configure-phase-agents set implement codex <model> <effort>`.
- `fix`: gọi `uv run --project tools/orchestrator configure-phase-agents candidate-set fix 0 codex <model> <effort>`.
- `fix-fallback`: gọi `uv run --project tools/orchestrator configure-phase-agents candidate-set fix 1 codex <model> <effort>`.
- Reset phase/all dùng `uv run --project tools/orchestrator configure-phase-agents reset <phase>` hoặc `reset-all`.

Đây là alias migration; interface authoritative là
`configure-phase-agents`, hỗ trợ cả PLAN/VERIFY/FINAL_VERIFY và Claude.
Command không thay đổi provider health, không bắt đầu research và không chạy Codex.
