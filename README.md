# Finance workspace

Workspace trung tâm để Claude và Codex phối hợp trên hệ sinh thái Finance.
Repository này giữ contract agent, rule/skill, spec, runbook, sơ đồ, research
artifact và handoff. Nó không chứa code runtime của các service.

`/ops:run` là lifecycle orchestration cấp project: Claude plan/verify/orchestrate,
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

1. Chạy `./.agents/scripts/sync-agent-links.sh`.
2. Đọc `AGENTS.md` hoặc `CLAUDE.md`, rồi đọc shared rule phù hợp.
3. Xác định và sử dụng shared skill liên quan; load capability/OpenSpec-native
   integration của CLI nếu cần.
4. Đọc research note được dẫn link, `research/quant/index.md`
   và OpenSpec active work. `docs/archive/legacy-handoff-agent.md` chỉ đọc khi cần tra cứu
   lịch sử/index, không dùng làm engineering queue.
5. Kiểm tra branch/status và deployed revision của repository code trước khi sửa.
6. Thực hiện theo role: Claude plan/verify; Codex implement/test/fix.
7. Upsert reusable skill/rule nếu có kiến thức mới, rồi chạy lại sync và
   `./.agents/scripts/sync-agent-links.sh --check`.
8. Ghi SHA, CI, Coolify và verification vào handoff; không chuyển task sang
   `Done` nếu chưa có review độc lập.

## Cấu trúc

```text
.agents/   rule, skill và utility dùng chung
docs/      architecture, ADR, runbook, diagram, migration và supporting docs
research/  durable quant research, evidence, samples và reports
docker/    source hạ tầng dùng chung và observability/POC
AGENTS.md  contract cho Codex và agent tương thích
CLAUDE.md  hướng dẫn riêng cho Claude
```

Không tạo lại top-level `raw/`. Engineering request đi qua native `/opsx:*` và
OPS; quant evidence đi vào `research/quant/`; legacy-only content nằm dưới
`docs/archive/`. Không ghi credential/token/secret vào các artifact này.

## Quant research loop

Claude Code hỗ trợ auto-detection trước mỗi vòng research bounded:

```text
/quant:codex-auto
/loop 20m /quant-research
```

Có thể chuyển về manual override mà không restart loop:

```text
/quant:codex-on
/quant:codex-off
/quant:codex-manual
```

Các lệnh này không khởi động lại loop. Trong auto mode, vòng
`/quant-research` kế tiếp chạy một probe bounded rồi đọc resolved
`codex_available`; kết quả ambiguous giữ nguyên giá trị gần nhất. State schema
v2 lưu cả `codex_mode` và các model profile tại
`.ops/runtime/quant-research/state.json`, được cập nhật atomic bằng
`.agents/scripts/quant-research-state.sh`, là runtime transient và không commit.

Xem hoặc chỉnh model/effort độc lập theo role bằng
`/quant:codex-config`: `probe`, `implement`, `fix`, và `fix-fallback`. Không có
Codex review profile; VERIFY và FINAL_VERIFY vẫn do Claude độc lập.

Ở chế độ bình thường, quant research chỉ nghiên cứu, OOS/holdout-validate và
handoff cho Codex. Chỉ khi state tường minh tắt Codex, một candidate đã validate
mới được đi qua lifecycle `/ops:run` với Claude fallback; không có Claude CLI
lồng nhau và không có state machine thứ hai. Vì Claude Code `2.1.250` không
công bố cơ chế custom command gọi đệ quy trong `claude --help`,
`quant-research.md` tham chiếu trực tiếp command contract `/ops:run` bằng file
reference. Không truyền trạng thái availability như argument cố định của
`/loop`.

Backend được chốt một lần khi `/ops:run` khởi tạo transaction và lưu cùng
`verification_mode` trong runtime state. Việc bật lại Codex chỉ ảnh hưởng
transaction mới; transaction fallback đang chạy vẫn giữ route Claude và dùng
`claude-fallback-self-review` nếu cùng top-level session verify.

## Codex worker policy

`/ops:run` truyền model và reasoning effort tường minh cho từng worker attempt:

| Phase/attempt | Model mặc định | Effort |
| --- | --- | --- |
| IMPLEMENT | `gpt-5.6-luna` | `high` |
| FIX primary | `gpt-5.6-terra` | `high` |
| FIX fallback | `gpt-5.6-sol` | `high` |

Persisted profile có thể chỉnh bằng `/quant:codex-config`. Explicit environment
override vẫn có ưu tiên qua `CODEX_IMPLEMENT_MODEL`, `CODEX_FIX_MODEL`,
`CODEX_FIX_FALLBACK_MODEL`, `CODEX_IMPLEMENT_REASONING_EFFORT`,
`CODEX_FIX_REASONING_EFFORT`, `CODEX_FIX_FALLBACK_REASONING_EFFORT`, hoặc shared
`CODEX_REASONING_EFFORT`. Launcher không phụ thuộc model mặc định trong user
config và không dùng `xhigh` mặc định. Codex
CLI hiện tại không có literal `--yolo`; launcher dùng flag chính thức tương
đương `--dangerously-bypass-approvals-and-sandbox`. Workflow hiện không launch
Claude CLI lồng nhau; nếu sau này có một Claude CLI worker route được thiết kế
tường minh, invocation đó phải có `--dangerously-skip-permissions`.

FIX chỉ fallback Terra sang Sol khi classifier trả `model-unavailable` hoặc
`model-specific-limit`, và vẫn là attempt thứ hai trong cùng round. Trước mỗi
FIX, Claude phải ghi findings hiện tại vào
`.ops/changes/<change>/runtime/verification-findings-round-<round>.md`; launcher
không trộn findings giữa các round.

Mỗi attempt giữ stdout JSONL, stderr, last message, exit code và metadata
allowlist tại
`codex-<phase>-round-<round>-attempt-<n>.meta.json`. Classifier phân biệt global
quota với model-local limit và transient HTTP 429. Chỉ
`global-quota-exhausted` tự cập nhật resolved availability; không thử model
khác, không đổi auto/manual mode và không đổi backend của transaction hiện tại.
Generic 429 không tự tắt Codex. Auto mode có thể phát hiện quota hồi phục ở
iteration kế tiếp; chỉ transaction mới quan sát trạng thái mới.

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
canonical `/ops:run`. Một iteration research-only không tạo OPS transaction.

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
