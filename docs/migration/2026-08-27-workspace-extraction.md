# Tách workspace điều phối khỏi repository code

Ngày: 2026-08-27 (UTC+7)

## Mục tiêu

Đưa contract agent, rules, skills, specs, runbooks, diagrams, research history
và handoff ra `ThanhNguyenDat/finance-workspace`, để Claude/Codex được action từ
một workspace chung. Các repository code vẫn giữ lịch sử và ownership riêng.

## Nguồn và phạm vi seed

Seed đầu tiên được lấy từ local `finance-mw` tại commit chứa các tài liệu hiện
hành. Đã chuyển:

- `AGENTS.md`, `CLAUDE.md` (đã viết lại để mô tả workspace, không giả là repo
  code).
- Toàn bộ `.agents/` rules, skills, helper scripts và agent metadata.
- Toàn bộ `docs/` bao gồm spec observability mới nhất.
- Toàn bộ `raw/` gồm handoff, research notes, reports và archive để giữ audit
  history.

Không chuyển code Go/Rust/TypeScript, `node_modules`, `dist`, credential file,
Docker runtime state hoặc production checkout. `finance-web` là repository code
riêng, không nằm trong workspace.

Evidence local hiện tại:

- Workspace seed commit: `1b0ac09` (`chore(workspace): centralize finance docs
  and agent contracts`).
- `finance-mw` compatibility-pointer commit: `f1a22a6`.
- Cả hai commit mới chỉ tồn tại local theo owner-held push gate; chưa có CI,
  GitHub hoặc Coolify deployment.

## Finance Web cutover (local)

Finance Web đã được seed sang repository riêng và kiểm tra local:

- Commit source ban đầu: `6eaf2b7` (`chore(web): seed standalone finance-web repository`).
- Commit chuẩn hóa Makefile/README: `7fd7dc1` (`chore(web): make standalone repository commands self-contained`).
- `npm run test`: 50 test files, 328 tests pass.
- `npm run lint`: pass, chỉ còn một warning hook đã tồn tại trong source.
- `npm run build`: pass.

Chưa xóa `finance-mw/web` vì workflow hiện tại vẫn build/verify trực tiếp
`web/`, `docker/compose.web.yaml`, Makefile và các script production-web. Cần
tách job CI/CD và chuyển các script sở hữu web trước; nếu xóa source trước bước
đó, pipeline Finance MW sẽ fail-closed do thiếu path.

Đã hoàn tất cutover local ngày 2026-08-27 UTC+7: `finance-mw` commits
`ad43acd` + `d450876` xoá `web/`, `docker/compose.web.yaml`, các verifier/detector web,
workflow `verify-web.yml`, và các job publish/deploy web khỏi pipeline MW.
Makefile, Docker builder, runtime-env/Compose contracts và tài liệu đã được cập
nhật; Go test/vet/build, shell contracts và workflow YAML parse đều xanh. Repo
`finance-web` giữ workflow/image/deploy riêng. Commit chưa push nên chưa có CI,
Coolify hay production verification.

## Shared Docker ownership cutover (local)

Đã seed bản canonical local sang `docker/infrastructure/` (20 file) và
`docker/observability/` (41 file), gồm cả POC Kafka/ClickHouse/S3 mới. Không
copy `elasticsearch/.env` hoặc `.env.poc` vì đây là credential/runtime state.

Chưa xóa bản trong `finance-mw`: Makefile, Coolify resource scripts, workflow
path filters và nhiều contract tests vẫn đọc trực tiếp `docker/infrastructure/*`
hoặc `docker/observability/*`. Cần chuyển các consumer này sang workspace hoặc
repo hạ tầng riêng, sau đó mới xoá compatibility copy trong một commit độc lập.

Đã chuyển một phần consumer local trong Finance MW bằng các commit `cc4e65a`,
`0fadc9e`, `ab4864c` và `c9078f0`:
Makefile và các script Grafana (`deploy_grafana_dashboards.py`,
`deploy_grafana_alerts.py`, `validate-grafana-dashboards.py`), validator tracing,
Kibana rotation và hai contract test ưu tiên `FINANCE_WORKSPACE_ROOT` khi sibling
workspace có đủ manifest, nhưng vẫn fallback về compatibility copy để checkout
CI đơn repo không bị gãy. Đây chưa phải consumer cutover hoàn chỉnh; Coolify
scripts còn lại, contract tests và workflow filters vẫn cần chuyển có kiểm soát
trước khi xóa bản copy.

## Quy tắc sau migration

1. Task/research/handoff bắt đầu tại `raw/handoff_agent.md` trong workspace.
2. Agent sửa code tại repository sở hữu; workspace chỉ nhận spec/evidence và
   không trở thành nơi build/deploy application.
3. Trong giai đoạn cutover, giữ bản copy tài liệu cũ ở các repo code để CI và
   agent đang chạy không bị gãy. Chỉ xóa hoặc thay bằng pointer sau khi
   `finance-workspace` đã được push, checkout độc lập và kiểm tra link.
4. Mọi task đang Processing phải ghi rõ workspace path mới khi cập nhật handoff.
5. Không chuyển trạng thái Verify/Done chỉ vì seed repository đã tạo; code và
   production evidence vẫn theo pipeline của repository sở hữu.

## Cổng cutover tài liệu

- [ ] Repo workspace có commit đầu tiên và remote SHA đã xác nhận.
- [ ] Claude/Codex đọc được `AGENTS.md`, `CLAUDE.md`, `.agents/` và handoff từ
      workspace checkout mới.
- [ ] Các link quan trọng tới repo code được kiểm tra trên cả local sibling và
      GitHub.
- [ ] CI/workflow của từng repo code không còn phụ thuộc bản copy cũ, hoặc đã
      có compatibility pointer được review.
- [ ] Sau khi đạt các cổng trên mới xóa tài liệu duplicate khỏi `finance-mw`.
- [x] Finance Web CI/CD độc lập đã được seed local và `finance-mw` không còn
      build/verify hoặc include `web/` trong commit `ad43acd` (CI/Coolify chờ
      owner mở push gate).
- [x] Đã xóa `web/` và web-owned compose/script khỏi `finance-mw` bằng commit
      `ad43acd` sau khi workflow standalone local pass.
- [ ] Các consumer hạ tầng (Make/script/test/workflow/Coolify raw Compose) đã
      dùng source workspace; sau đó xoá `docker/infrastructure/` và
      `docker/observability/` khỏi `finance-mw`.

Các asset Elasticsearch mà `coolify-resources.sh` cài đặt cũng đã dùng resolver
chung ở `ab4864c`. Fallback vẫn giữ nguyên để các workflow checkout riêng
không fail trước khi CI được chuyển sang checkout workspace.

Bốn contract test Compose/Filebeat/Elasticsearch/Kline-maintenance dùng cùng
resolver ở `c9078f0`; local đã chạy trên manifest workspace và giữ fallback cho
CI checkout đơn repo. Các test và workflow còn lại là cổng cutover tiếp theo.

Contract healthcheck hạ tầng cũng đã chuyển sang resolver ở `5e05a73`; local
đã xác nhận toàn bộ service trên manifest workspace có healthcheck bounded.

Bốn Python contract test memory/process/Prometheus/retired-metrics đã chuyển
sang resolver ở `bde66e7`; local 19/19 test pass khi đọc manifest workspace.
