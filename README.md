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

## Bắt đầu một vòng làm việc

1. Đọc `AGENTS.md` và skill/rule liên quan trong `.agents/`.
2. Đọc `raw/handoff_agent.md`, rồi đọc research note được dẫn link.
3. Kiểm tra branch/status và deployed revision của repository code trước khi sửa.
4. Implement/test/commit trong repository code; ghi SHA, CI, Coolify và verify
   vào handoff. Không chuyển task sang `Done` nếu chưa có review độc lập.

## Cấu trúc

```text
.agents/   rule và skill dùng chung
docs/      spec, runbook, sơ đồ và kế hoạch
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
