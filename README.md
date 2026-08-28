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
- `docs/` chứa architecture, ADR, runbook, diagram và tài liệu hỗ trợ; không
  tạo thêm một hệ spec hành vi cạnh OpenSpec.
- `raw/` giữ research, evidence, audit history và handoff; không rewrite lịch
  sử chỉ để làm gọn.

## Bắt đầu một vòng làm việc

1. Chạy `./.agents/scripts/sync-agent-links.sh`.
2. Đọc `AGENTS.md` hoặc `CLAUDE.md`, rồi đọc shared rule phù hợp.
3. Xác định và sử dụng shared skill liên quan; load capability/OpenSpec-native
   integration của CLI nếu cần.
4. Đọc `raw/handoff_agent.md`, research note được dẫn link và OpenSpec active
   work.
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
raw/       handoff, research history, report và evidence
docker/    source hạ tầng dùng chung và observability/POC
AGENTS.md  contract cho Codex và agent tương thích
CLAUDE.md  hướng dẫn riêng cho Claude
```

`raw/` là audit history. Không rewrite hoặc xóa lịch sử chỉ để làm gọn repo;
không ghi credential/token/secret vào đó.

## Quant research loop

Claude Code hỗ trợ một vòng research bounded qua state runtime:

```text
/quant:codex-off
/loop 20m /quant-research
```

Khi muốn bật lại Codex, chạy:

```text
/quant:codex-on
```

Lệnh này không khởi động lại loop; vòng `/quant-research` kế tiếp tự đọc
`codex_available` từ `.ops/runtime/quant-research/state.json`. State được tạo
và cập nhật atomic bằng `.agents/scripts/quant-research-state.sh`, là runtime
transient và không được commit.

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

Operator có thể override qua `CODEX_IMPLEMENT_MODEL`, `CODEX_FIX_MODEL`,
`CODEX_FIX_FALLBACK_MODEL` và `CODEX_REASONING_EFFORT`. Launcher không phụ
thuộc model mặc định trong user config và không dùng `xhigh` mặc định. Codex
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
`global-quota-exhausted` tự chạy `quant-research-state.sh codex-off`; không thử
model khác và không đổi backend của transaction hiện tại. Generic 429 không tự
tắt Codex. Việc bật lại luôn thủ công bằng `/quant:codex-on`, và chỉ transaction
mới quan sát trạng thái mới.

`docker/infrastructure/` và `docker/observability/` là source canonical cho
stack dùng chung. Các repo application chỉ giữ compatibility copy trong giai
đoạn cutover; không coi bản copy đó là ownership lâu dài.
