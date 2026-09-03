# Finance workspace

Workspace trung tâm để Claude và Codex phối hợp trên hệ sinh thái Finance.
Repository này giữ contract agent, rule/skill, spec, runbook, sơ đồ, research
artifact và handoff. Nó không chứa code runtime của các service.

`/ops:e2e` là lifecycle orchestration cấp project: Claude plan/verify/orchestrate,
Codex implement/test/fix. `/opsx:*` là các primitive OpenSpec-native. OpenSpec
giữ requirements/design/tasks; `.ops/changes/<change>/handoff.md` giữ handoff
ngắn gọn; `.ops` runtime là transient và được gitignore.

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
- `.claude/`, `.kimi-code/`, `.opencode/` giữ OpenSpec-native commands/skills,
  adapter và metadata riêng của từng CLI. Shared sync không quản lý các mục
  `openspec*`.
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
tools/     Python phase-agent orchestrator và operational entrypoints
docs/      architecture, ADR, runbook, diagram, migration và supporting docs
research/  durable quant research, evidence, samples và reports
docker/    source hạ tầng dùng chung và observability/POC
AGENTS.md  contract cho Codex và agent tương thích
CLAUDE.md  hướng dẫn riêng cho Claude
```

Không tạo lại top-level `raw/`. Engineering request đi qua native `/opsx:*` và
OPS; quant evidence đi vào `research/quant/`; legacy-only content nằm dưới
`docs/archive/`. Không ghi credential/token/secret vào các artifact này.

## Quant research và phase agents

Operator chủ động chạy đúng một iteration, không có loop/daemon tự động:

```text
uv run --project tools/orchestrator run-phase-agent-command quant-research
```

Launcher increment iteration một lần, đọc canonical
`.claude/commands/quant-research.md`, rồi resolve logical agent
`quant_research`. Nếu provider hết quota giữa vòng, candidate kế tiếp tiếp tục
cùng iteration và artifacts hiện tại.

PLAN, IMPLEMENT, VERIFY, FIX và FINAL_VERIFY cũng là logical phase agents, và
`quant_research` là một role riêng biệt (không phải một OPS phase). Mỗi role
có ordered Codex/Claude candidates riêng tại ignored atomic state
`.ops/runtime/agent-roles/state.json`. Xem và điều chỉnh an toàn:

```text
uv run --project tools/orchestrator configure-agent-roles show
uv run --project tools/orchestrator configure-agent-roles set implement codex gpt-5.6-luna high
uv run --project tools/orchestrator configure-agent-roles pin verify claude
uv run --project tools/orchestrator configure-agent-roles auto verify
uv run --project tools/orchestrator configure-agent-roles provider-off codex
uv run --project tools/orchestrator configure-agent-roles provider-auto codex
```

Mặc định ưu tiên Claude Opus `medium` cho PLAN/VERIFY, Codex cho
IMPLEMENT/FIX, và Opus `high` chỉ cho fallback FIX/FINAL_VERIFY khó. Workspace
chỉ chấp nhận Opus `medium|high`.

Mỗi attempt dùng model/effort tường minh và hard timeout. Claude luôn có
`--dangerously-skip-permissions`; Codex dùng
`--dangerously-bypass-approvals-and-sandbox`. Confirmed global quota/auth mở
provider circuit; model-local limit chuyển candidate; generic 429, timeout,
network và implementation failure không bị gắn nhãn global quota.

Khi quota hết trong PLAN/IMPLEMENT/FIX, process cũ phải thoát hoàn toàn trước
attempt mới. Diff/commit được giữ nguyên và candidate mới chạy continuation
trong cùng phase/FIX round. Attempt history không bị overwrite. VERIFY và
FINAL_VERIFY read-only; kết quả ghi `provider-independent` nếu provider khác,
hoặc `same-provider-process-separated` nếu cùng provider.

Các alias `/quant:codex-*` cũ vẫn tồn tại trong giai đoạn migration, nhưng
phase-agent controls là interface authoritative cho routing mới.

## Source of truth cho quant promotion

```text
Research = research evidence
OpenSpec = engineering truth
OPS      = execution/tracing truth
Git/CI   = delivery truth
```

Mỗi `/quant-research` chỉ là một iteration bounded. Kết quả có thể là
`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, hoặc `PROMOTE`.
Chỉ `PROMOTE` sau gate OOS/holdout/walk-forward defensible, improvement/defect
đáng implement, scope/repository/behavior/acceptance rõ, risk/trading safety
đã hiểu và rollback đã rõ khi áp dụng mới được tạo OpenSpec rồi enter
canonical `/ops:e2e`. Một iteration research-only không tạo OPS transaction.

Promoted change dùng cùng tên stable `<change>` tại
`openspec/changes/<change>/` và `.ops/changes/<change>/`; origin metadata chỉ
reference tới research iteration/instrument và các file dưới
`research/quant/`, không copy nội dung. Completed flow giữ trace từ research
artifact → OpenSpec → OPS →
commit/CI/deploy → archive.

`docs/archive/legacy-handoff-agent.md` chỉ là archived human-readable history,
non-authoritative. Nó không sở hữu implementation queue hay trạng thái
`Todo`/`Processing`/`Dev-done`/`Verify`/`Done`; hãy đọc OpenSpec tasks và OPS
runtime/archive để biết trạng thái thật.

`docker/infrastructure/` và `docker/observability/` là source canonical cho
stack dùng chung. Các repo application chỉ giữ compatibility copy trong giai
đoạn cutover; không coi bản copy đó là ownership lâu dài.
