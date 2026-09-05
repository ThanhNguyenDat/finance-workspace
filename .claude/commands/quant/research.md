---
description: "Run one bounded automated quant research round"
---

Thực hiện một vòng quant-research bounded bằng tiếng Việt, timezone vận hành
`UTC+7 / Asia/Ho_Chi_Minh`. Đọc và áp dụng
[quant-research-domain](../../../.agents/domain/quant-research-domain.md), là
nguồn duy nhất cho hypothesis, backtest, evidence, classification và
promotion gate.

## Chạy một vòng

Mỗi lần chạy đúng một lệnh sau (không cần tham số bắt buộc):

```bash
uv run --project tools/orchestrator quant-research-exec
```

Có thể truyền một positional prompt hoặc `--prompt-file` làm guidance cho
Claude PLAN, cùng `--round`, `--timeout-seconds`, và các cặp flag model/effort
của Codex/Claude khi cần. Lệnh tự thực hiện toàn bộ flow:

```text
Claude PLAN -> Codex IMPLEMENT -> Claude VERIFY
  -> Codex trả lời QUESTION (tối đa một round-trip)
  -> Codex FIX / Claude re-VERIFY (tối đa 5 attempts, escalation từ attempt 3)
  -> Codex FINALIZE
```

PLAN chọn một hypothesis mở từ backlog, ưu tiên XAU, và tạo brief có
`PLAN_BRIEF:`. VERIFY dùng marker `VERIFY_RESULT:` và chỉ đánh giá evidence
và classification có đáng tin hay không. `PASS` cũng đúng với một kết quả âm
hưng được đo trung thực như `REJECTED`; không được diễn giải PASS là
hypothesis đã thành công. Nếu attempt thứ 5 vẫn là `DEFECT`, lệnh dừng
non-zero và không finalize.

Khi không truyền `--cwd`, lệnh tự sync default branch, chạy PLAN trước khi
tạo worktree, tạo `.agents/worktrees/quant-research-round-<N>` cho các bước còn
lại, rồi merge fast-forward và xóa worktree sau FINALIZE thành công. Nếu có
lỗi, worktree và branch được giữ lại để kiểm tra. Truyền `--cwd <dir>` để bỏ
toàn bộ lifecycle này và chạy trực tiếp trong directory đã được caller cô lập.

## Sau khi lệnh kết thúc

Đọc JSONL log tại
`tools/orchestrator/logs/quant-research-round-<N>/quant-research-exec.log` và
round/index/CSV mà Codex đã cập nhật. Kiểm tra các `stage` (`plan`,
`setup_worktree`, `implement`, `verify`, `ask`, `fix`, `finalize`, `merge`) và
đối chiếu evidence thật với domain rules, không chỉ dựa vào prose cuối turn.

Nếu classification là `PROMOTE`, dùng `/opsx:propose` trong phiên Claude
tương tác để tạo OpenSpec change tiếp theo; `quant-research-exec` chỉ finalize
commit của round, không tự tạo planning artifacts. Với classification nghiên
cứu khác, ghi nhận stable change name, file evidence, unseen-data evidence,
người thực hiện từng stage, và giới hạn thực tế trong handoff ngắn bằng tiếng
Việt.
