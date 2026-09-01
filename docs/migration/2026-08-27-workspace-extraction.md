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

Chưa xóa bản compatibility trong `finance-mw`: các consumer code hiện ưu tiên
`FINANCE_WORKSPACE_ROOT` và chỉ fallback về bản copy khi checkout CI đơn repo
không có sibling workspace. Audit hiện tại không còn Coolify script nào đọc trực
tiếp source cũ; các chuỗi `docker/infrastructure/*` và `docker/observability/*`
còn lại chỉ là nhãn tương đối trong contract test, tài liệu hoặc fallback có chủ
đích.

Consumer local đã chuyển qua resolver bằng các commit `cc4e65a`, `0fadc9e`,
`ab4864c`, `c9078f0`, `5e05a73`, `bde66e7`, `474b337`, `943d2de`, `db1b76e`,
`d8ca6a4` và `2ed7c18`: Makefile, script Grafana, validator tracing, Kibana
rotation, Coolify asset installer, toàn bộ contract test hạ tầng/observability,
path filters và Compose validation đều đã chạy local trên manifest canonical.
Consumer cutover chưa thể đóng vì workflow GitHub chưa checkout workspace ở SHA
bất biến; remote `finance-workspace` hiện vẫn rỗng (`isEmpty=true`). Sau khi owner
publish `main` và xác nhận SHA, mới thêm checkout/pin workflow rồi xóa
compatibility copy trong một commit độc lập.

## Quy tắc sau migration

1. Engineering work starts in OpenSpec and OPS; quant evidence lives under
   `research/quant/`, and coordination lives in `.ops/changes/<change>/handoff.md`.
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
- [ ] Các workflow đã checkout/pin source workspace ở SHA bất biến; sau đó xoá
      `docker/infrastructure/` và `docker/observability/` compatibility copy khỏi
      `finance-mw`.

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

Commit `474b337` bổ sung resolver vào path filters monitor/deployment để các
thay đổi consumer Docker không bị CI bỏ qua. Workflow chưa tự checkout workspace
canonical vì cần owner xác nhận remote SHA trước khi pin dependency.

Layout contract `943d2de` cũng kiểm tra thư mục canonical trong workspace (và
fallback khi CI chỉ có một repo), nên không còn false-fail bởi thư mục
`finance-mw/docker/monitor` root-owned cũ.

Quality workflow không còn hard-code ba compose hạ tầng; `db1b76e` thêm target
`make validate-infrastructure-compose` dùng cùng resolver. Local validation
với biến môi trường contract đã pass và workflow YAML parse pass.

## Recheck local 16:12 UTC+7

- Finance Web standalone đã recheck tại commit `49d6777`: test 50/50 file,
  328/328 test pass; lint 0 error (chỉ còn một warning hook có sẵn);
  production build TypeScript/Vite pass.
- Finance MW baseline tại HEAD `22f2e7a`: `go test -timeout=10m ./...`,
  `go vet ./...` và `go build ./...` đều pass; các contract hạ tầng/observability
  tiếp tục pass với resolver canonical sibling workspace.
- `git ls-remote origin refs/heads/main` của workspace và web không trả SHA;
  GitHub API cũng xác nhận cả hai repository còn `isEmpty=true` và chưa có
  default branch. Vì vậy các workflow chưa được checkout/pin workspace và bản
  compatibility Docker trong `finance-mw` vẫn phải giữ nguyên.
