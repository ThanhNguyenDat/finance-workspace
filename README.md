# Finance workspace

Workspace trung tâm để Claude và Codex phối hợp trên hệ sinh thái Finance.
Repository này giữ contract agent, rule/skill, spec, runbook, sơ đồ, research
artifact và handoff. Nó không chứa code runtime của các service.

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

`docker/infrastructure/` và `docker/observability/` là source canonical cho
stack dùng chung. Các repo application chỉ giữ compatibility copy trong giai
đoạn cutover; không coi bản copy đó là ownership lâu dài.
