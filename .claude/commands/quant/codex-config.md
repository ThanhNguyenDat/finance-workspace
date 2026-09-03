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

- Không argument: gọi `./.agents/scripts/configure-phase-agents.py show`.
- `implement`: gọi `configure-phase-agents.py set implement codex <model> <effort>`.
- `fix`: gọi `configure-phase-agents.py candidate-set fix 0 codex <model> <effort>`.
- `fix-fallback`: gọi `configure-phase-agents.py candidate-set fix 1 codex <model> <effort>`.
- Reset phase/all dùng `configure-phase-agents.py reset <phase>` hoặc `reset-all`.

Đây là alias migration; interface authoritative là
`configure-phase-agents.py`, hỗ trợ cả PLAN/VERIFY/FINAL_VERIFY và Claude.
Command không thay đổi provider health, không bắt đầu research và không chạy Codex.
