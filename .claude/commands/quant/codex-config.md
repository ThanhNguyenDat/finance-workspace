---
description: "Xem hoặc chỉnh Codex model/effort riêng cho từng phase"
argument-hint: "[probe|implement|fix|fix-fallback <model> <effort> | reset <role|all>]"
---

Xử lý `$ARGUMENTS` theo đúng một trong các dạng dưới đây. Không dùng `eval`,
không nội suy argument thành shell code và không chấp nhận role khác.

```text
/quant:codex-config
/quant:codex-config <probe|implement|fix|fix-fallback> <model> <effort>
/quant:codex-config reset <probe|implement|fix|fix-fallback|all>
```

- Không argument: gọi `./.agents/scripts/quant-research-state.sh profile-get`
  đúng một lần cho từng role `probe`, `implement`, `fix`, `fix-fallback`, rồi
  hiển thị model/effort bằng tiếng Việt. Không in raw state JSON.
- Update: gọi `./.agents/scripts/quant-research-state.sh profile-set <role>
  <model> <effort>` đúng một lần. Helper chịu trách nhiệm validate model và
  effort `none|minimal|low|medium|high|xhigh` trước atomic update.
- Reset một role: gọi `profile-reset <role>` đúng một lần.
- Reset all: gọi `profiles-reset` đúng một lần và chỉ hiển thị bốn default
  profile an toàn, không in raw JSON.

Các profile chỉ áp dụng cho Codex `probe`, `IMPLEMENT`, primary `FIX` và eligible
`FIX fallback`. `VERIFY` và `FINAL_VERIFY` luôn do Claude độc lập; không tạo
Codex review profile. Command này không thay đổi mode/availability, không bắt
đầu research, không chạy Codex, và không dừng hoặc khởi động lại `/loop`.
