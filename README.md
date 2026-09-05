# Finance workspace

Workspace trung tâm để Claude và Codex phối hợp trên hệ sinh thái Finance.
Repository này giữ contract agent, rule/skill, spec, runbook, sơ đồ, research
artifact và handoff. Nó không chứa code runtime của các service.

Claude plan/verify (Codex fallback khi hết quota); Codex implement/fix
(Claude fallback khi hết quota) — không có coordinator hay resolver tự động
route provider, đây là quyết định thủ công. `/opsx:*` là các primitive
OpenSpec-native cho planning; `/orchestrator:e2e` (`.claude/commands/orchestrator/e2e.md`)
là fast path cho việc nhanh/lặp lại, dùng trực tiếp `codex-exec`/`claude-exec`.
OpenSpec giữ requirements/design/tasks; `.ops/changes/<change>/handoff.md`
giữ handoff ngắn gọn khi có; `.ops` runtime là transient và được gitignore.

## Các repository chuyên trách

| Repository | Phạm vi |
| --- | --- |
| `finance-mw` | Go middleware/API, migration và gateway |
| `finance-web` | React/Vite browser application |
| `finance-live-action` | Rust strategy, Portfolio và live worker |
| `finance-broker` | Broker adapter và execution |
| `mt5` | MT5 adapter |

Các repo code nên được checkout cạnh thư mục workspace. Agent đọc task và
research từ workspace, sau đó sửa đúng repository sở hữu code.

## Nguồn sự thật

- `.agents/rules/` và `.agents/skills/` là source of truth cho rule, skill và
  operating procedure dùng chung của Finance.
- `.claude/` giữ OpenSpec-native commands/skills, adapter và metadata riêng
  của Claude Code; `tools/orchestrator sync-agent-links` mirror
  `.agents/skills/`/`.agents/rules/` vào `.claude/skills/`/`.claude/rules/`
  dưới dạng symlink, bỏ qua các mục `openspec*`.
- `openspec/specs/` và `openspec/changes/` là source of truth cho behavioral
  specs, active changes và task status.
- `research/quant/` chứa quant rounds, studies, audits, samples, reports và
  navigation index; research-only result không tạo engineering transaction.
- `docs/` chứa architecture, ADR, runbook, review, diagram và tài liệu lưu trữ;
  không tạo thêm một hệ spec hành vi cạnh OpenSpec.

## Bắt đầu một vòng làm việc

1. Chạy `uv run --project tools/orchestrator sync-agent-links`.
2. Đọc `AGENTS.md` hoặc `CLAUDE.md`, rồi đọc shared rule phù hợp.
3. Xác định và sử dụng shared skill liên quan; load capability/OpenSpec-native
   integration của CLI nếu cần.
4. Đọc research note được dẫn link, `research/quant/index.md`
   và OpenSpec active work. `docs/archive/legacy-handoff-agent.md` chỉ đọc khi cần tra cứu
   lịch sử/index, không dùng làm engineering queue.
5. Kiểm tra branch/status và deployed revision của repository code trước khi sửa.
6. Thực hiện theo role: Claude plan/verify; Codex implement/test/fix.
7. Upsert reusable skill/rule nếu có kiến thức mới, rồi chạy lại sync và
   `uv run --project tools/orchestrator sync-agent-links --check`.
8. Ghi SHA, CI, Coolify và verification vào handoff; không chuyển task sang
   `Done` nếu chưa có review độc lập.

## Cấu trúc

```text
.agents/   shared rules, skills và contract tests
tools/     Python orchestrator CLIs (codex-exec/claude-exec/sync-agent-links)
docs/      architecture, ADR, runbook, diagram, migration và supporting docs
research/  durable quant research, evidence, samples và reports
docker/    source hạ tầng dùng chung và observability/POC
AGENTS.md  contract cho Codex và agent tương thích
CLAUDE.md  hướng dẫn riêng cho Claude
```

Không tạo lại top-level `raw/`. Engineering request đi qua native `/opsx:*`
(planning) rồi implement theo role boundary ở trên (`/orchestrator:e2e` cho
việc nhanh/lặp lại); quant evidence đi vào `research/quant/`; legacy-only
content nằm dưới `docs/archive/`. Không ghi credential/token/secret vào các
artifact này.

## Quant research

Không có launcher, daemon, hay coordinator state nào track vòng research
nữa — operator chủ động chạy `/quant:research` (canonical tại
`.claude/commands/quant/research.md`) đúng một iteration mỗi lần.

**Round-file sequence dưới `research/quant/rounds/` là nguồn sự thật duy
nhất** cho số round tiếp theo: tìm file `round<N>-*.md` lớn nhất (hoặc commit
`docs(research): round <N>` mới nhất trong `git log`) rồi dùng `N+1`.

Provider cho vòng nghiên cứu (và cho PLAN/IMPLEMENT/VERIFY/FIX/FINAL_VERIFY
nói chung) theo đúng role boundary ở đầu file này — Claude PLAN/VERIFY
trước, Codex IMPLEMENT/FIX trước, fallback thủ công khi provider chính
confirmed hết quota. Không có state file hay CLI nào track candidate order
tự động nữa.

## Source of truth cho quant promotion

```text
Research = research evidence
OpenSpec = engineering truth
Git/CI   = delivery truth
```

Mỗi `/quant:research` chỉ là một iteration bounded. Kết quả có thể là
`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, hoặc `PROMOTE`.
Chỉ `PROMOTE` sau gate OOS/holdout/walk-forward defensible, improvement/defect
đáng implement, scope/repository/behavior/acceptance rõ, risk/trading safety
đã hiểu và rollback đã rõ khi áp dụng mới được tạo OpenSpec change qua
`/opsx:propose` rồi dừng lại ở planning — không có automatic lifecycle nào
tiếp theo, implementation là quyết định thủ công riêng của operator. Một
iteration research-only không tạo engineering transaction nào.

Promoted change dùng một tên stable `<change>` tại `openspec/changes/<change>/`
(và một `handoff.md` ngắn gọn tại `.ops/changes/<change>/` khi có); origin
metadata chỉ reference tới research iteration/instrument và các file dưới
`research/quant/`, không copy nội dung. Completed flow giữ trace từ research
artifact → OpenSpec → commit/CI/deploy → archive.

`docs/archive/legacy-handoff-agent.md` chỉ là archived human-readable history,
non-authoritative. Nó không sở hữu implementation queue hay trạng thái
`Todo`/`Processing`/`Dev-done`/`Verify`/`Done`; hãy đọc OpenSpec tasks và
archive để biết trạng thái thật.

`docker/infrastructure/` và `docker/observability/` là source canonical cho
stack dùng chung. Các repo application chỉ giữ compatibility copy trong giai
đoạn cutover; không coi bản copy đó là ownership lâu dài.
