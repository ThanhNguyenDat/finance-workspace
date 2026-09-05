---
description: "Run exactly one bounded, state-aware quant research iteration"
---

Thực hiện đúng một vòng nghiên cứu bounded bằng tiếng Việt, timezone vận hành
`UTC+7 / Asia/Ho_Chi_Minh`. Operator chạy lệnh này thủ công (không có launcher
hay orchestrator riêng nào chạy nền cho vòng này nữa). Không tạo `/loop`,
daemon, scheduler, sleep, hay tự gọi lại chính mình.

**Trước khi bắt đầu**: đọc và áp dụng
[quant-research-domain](../../../.agents/domain/quant-research-domain.md)
— đó là nguồn duy nhất cho nhiệm vụ của vòng, ràng buộc backtest, tiêu chí
phân loại kết quả, và promotion gate. File này (`research.md`) chỉ định
nghĩa **flow** điều phối Claude/Codex bên dưới; không lặp lại nội dung của
skill đó ở đây.

## Vai trò trong vòng

Phiên Claude hiện tại tự làm PLAN (chọn hypothesis, thiết kế test) và VERIFY
(kiểm tra độc lập evidence trước khi commit); phần IMPLEMENT (chạy backtest
thật) và FIX (sửa khi verify phát hiện vấn đề) giao cho Codex qua
`tools/orchestrator` — đúng `CLAUDE.md`'s Role/Working Model (`PLAN/VERIFY =
Claude first`, `IMPLEMENT/FIX = Codex first`). Cả 4 giai đoạn nằm trong CÙNG
một round number, không tách thành 2 vòng trừ khi thực thi thật sự không
hoàn thành được đúng plan ban đầu (xem
[quant-research-loop](../../../.agents/skills/quant-research-loop/SKILL.md)
"Core workflow" để biết chi tiết điều kiện tách vòng — đây cũng là skill mô
tả chính xác 4 bước dưới đây, bằng tiếng Anh, cho bất kỳ agent nào khác cần
đọc).

## Bước 1-2 — Claude (PLAN)

1. Xác định số round tiếp theo: tìm file `round<N>-*.md` lớn nhất trong
   `research/quant/rounds/` (hoặc `git log --oneline -- research/quant/rounds/`)
   rồi dùng `N+1`. Không có launcher hay state CLI nào track iteration nữa —
   round-file sequence là nguồn sự thật duy nhất.
2. Đọc `research/quant/reports/optimize_loop_update_v2.csv`,
   `research/quant/index.md`, rồi chỉ các round, study, audit hoặc sample liên
   quan dưới `research/quant/`. `docs/reviews/` chứa supporting operational
   reviews. `docs/archive/legacy-handoff-agent.md` chỉ là lịch sử legacy, không
   phải engineering queue hoặc nguồn task/lifecycle status authoritative. Chọn
   một hypothesis còn mở theo đúng quy tắc của `quant-research-domain` (ưu
   tiên `XAU` rồi `BTC`), rồi viết một plan ngắn: hypothesis, vì sao chọn nó
   tiếp theo, thiết kế test (route ưu tiên, split train/validation/holdout
   hoặc walk-forward, giả định cost/fill, và bằng chứng nào sẽ tính là
   `PROMOTE` so với các classification còn lại). Ghi plan này ra một file
   tạm (ví dụ trong scratchpad session) để làm prompt cho Codex — plan không
   cần round number hay file riêng dưới `research/quant/`.

## Bước 3-5 — Codex (IMPLEMENT)

Giao plan ở trên cho Codex chạy backtest thật, qua `tools/orchestrator`:

```bash
uv run --project tools/orchestrator quant-research-exec \
  --prompt-file <đường dẫn file plan> \
  --role implement \
  --round <N> \
  --timeout-seconds 3600
```

`quant-research-exec` tự suy ra `change=quant-research-round-<N>` (cùng `<N>` ở
bước 1) để log của Codex trong vòng này nằm trong một thư mục
`tools/orchestrator/logs/quant-research-round-<N>/` thay vì rơi vào bucket
`adhoc-<ngày>` không liên quan. Yêu cầu Codex trong plan: chạy đúng ràng buộc
domain skill nêu trên, phân loại kết quả, và **viết draft** round file + cập
nhật CSV/index nhưng **chưa commit** — Claude cần verify trước.

## Bước 6 — Claude (VERIFY)

Đọc trực tiếp evidence Codex tạo ra (CSV, log JSONL, draft round file) — không
chỉ tin vào tóm tắt cuối turn của Codex. Kiểm tra độc lập theo
`quant-research-loop/SKILL.md`'s "Non-negotiable invariants": không
fabricate/cherry-pick, train/validation/holdout thực sự disjoint, không
lookahead, classification khớp đúng số liệu theo tiêu chí của
`quant-research-domain`. Nếu ổn, chuyển sang bước 8. Nếu có vấn đề, sang
bước 7.

## Bước 7 — Codex (FIX), chỉ khi bước 6 phát hiện vấn đề

```bash
uv run --project tools/orchestrator quant-research-exec \
  --prompt-file <đường dẫn file mô tả vấn đề cụ thể> \
  --role fix \
  --round <N> \
  --timeout-seconds 1800
```

Mô tả đúng vấn đề Claude phát hiện (không lặp lại toàn bộ plan). Sau khi
Codex sửa, quay lại bước 6 để Claude re-check nhanh phần vừa sửa. Chỉ chạy
bước này **tối đa 1 lần** cho mỗi round; nếu re-check sau đó vẫn phát hiện
vấn đề, đóng round lại trung thực với classification `NEEDS-MORE-RESEARCH`
hoặc `DATA-ISSUE` thay vì tiếp tục fix.

## Bước 8 — Codex (hoàn tất)

Khi verify đạt, để Codex (trong cùng turn implement/fix cuối, hoặc 1 turn
ngắn tiếp theo với `--role implement`) commit round file + mọi cập nhật CSV/
index, dọn container/tunnel tạm, báo giới hạn thực tế.

## PROMOTE

Nếu classification là `PROMOTE`, xem
[quant-research-domain](../../../.agents/domain/quant-research-domain.md)
"Khi kết quả là PROMOTE" — đây là bước Claude PLAN kế tiếp (dùng
`/opsx:propose`, xem `.claude/commands/opsx/propose.md`), không giao cho
Codex.

Mỗi iteration kết thúc bằng tóm tắt ngắn bằng tiếng Việt: round number,
instrument/scope, unseen-data evidence, classification, research files đã cập
nhật, ai (Claude/Codex) làm phần nào, và giới hạn thực tế. Với `PROMOTE`, thêm
stable change name và đường dẫn OpenSpec change đã tạo. Không hỏi user trong
research bình thường và không biến suy luận thành fact.
