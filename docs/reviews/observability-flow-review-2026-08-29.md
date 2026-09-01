# Review luồng observability (metrics / logs / tracing) — 2026-08-29

Phạm vi: đối chiếu `.agents/rules/observability-logging.md` với code trong git và
trạng thái production read-only. **Chỉ inspect — không implement.** Mọi hướng sửa
bên dưới đều đánh dấu "chưa áp dụng".

## Tóm tắt

| Trụ cột | Trạng thái |
|---|---|
| Logging (ECS JSONL) | **Đạt** ở cả 5 repo, kể cả nginx |
| Tracing (OTel/W3C) | **Đạt** — bật thật trên cả 4 backend |
| Metrics (`/metrics` → vmagent) | **Có lỗ hổng nghiêm trọng** — xem P1 |
| Alerting | **Không có định nghĩa nào trong version control** — xem P3 |
| Hạ tầng observability | **Khoẻ** — 8/8 container healthy |

## P1 — Config vmagent đã deploy LỆCH khỏi git: 6 service đang chạy không được giám sát

Đây là phát hiện nghiêm trọng nhất và nó đang có hiệu lực ngay lúc này.

**Đo được (vmagent API, `/api/v1/targets`):** 16 active target, 15 up, 1 down.

**Ba bất khớp:**

1. **4 worker hoàn toàn không được scrape.** Production đang chạy
   `finance-trading-worker-1`, `finance-english-worker-1`, `finance-social-worker-1`,
   `finance-tvl-worker-1` (đều healthy, up 41 giờ). Git đã có đúng 4 job cho chúng
   tại `docker/observability/vmagent/scrape.yml:80-119`. **Config đã deploy không
   có job nào trong 4 cái đó.**

2. **1 target ma vĩnh viễn DOWN.** vmagent đã deploy đang scrape
   `finance-job-worker:8002` — tên này không khớp container nào đang chạy. Đây là
   tên **trước** khi tách worker (việc tách được ghi trong
   `.agents/rules/coding-and-verification.md` mục "Native automation" như trạng
   thái hiện hành). Một target DOWN thường trực chính là thứ che mất một sự cố
   thật.

3. **2 worker live-action bybit không được scrape.** Git liệt kê 6 target
   (`scrape.yml:146-157`) gồm `live-action-bybit-perpetual-future-btc-usdt` và
   `live-action-bybit-spot-xaut-usdt`; production chạy **6** container live-action
   nhưng vmagent chỉ scrape **4**. Hai route bybit (instrument tạo 2026-08-23, xem
   `research/quant/rounds/round208-*.md`) đang giao dịch mà không có metrics.

**Tổng: 6 service production đang chạy mà không có metrics, cộng một cảnh báo DOWN giả.**

Điều này vi phạm trực tiếp `.agents/rules/production-deployment-verification.md`
mục "Observability": *"verify all expected current scrape targets with `up == 1`"* —
số target "expected" hiện đang được lấy từ config cũ, nên check đó tự pass mà
không phát hiện gì.

**Hướng sửa (CHƯA ÁP DỤNG — chỉ là investigation):** redeploy vmagent với
`docker/observability/vmagent/scrape.yml` trong git; sau đó đối chiếu số target
với số container đang chạy chứ không đối chiếu với chính config.

## P2 — `finance-web` thiếu contract `setup-log.sh` / `setup-agent.sh`

`.agents/rules/observability-logging.md` mục "Verification and delivery":
*"Every ecosystem repository must provide executable `scripts/setup-log.sh` and
`scripts/setup-agent.sh`, include both in its runtime image, call them from its
entrypoint, and guard that contract with a bounded test."*

| repo | setup-log.sh | setup-agent.sh |
|---|---|---|
| finance-mw | exec | exec |
| finance-live-action | exec | exec |
| finance-broker | exec | exec |
| mt5 | exec | exec |
| **finance-web** | **thiếu** | **thiếu** |

Đây gần như chắc chắn là hệ quả của việc tách `finance-web` khỏi `finance-mw`
(2026-08-27) — repo mới chưa mang theo hai script này.

**Cần nói rõ để không phóng đại:** phần *logging* của finance-web thì **đúng
chuẩn**. `nginx.conf.template` có `log_format finance_json escape=json` (dòng 12),
ghi `access.jsonl` ra cả file lẫn stdout (dòng 42-43), `error_log` ra file lẫn
stderr (dòng 44-45) — đúng ngoại lệ mà rule cho phép với native server error log,
và tắt access log cho health probe (dòng 53, 59). `logrotate.conf` có sẵn. Cái
thiếu là **contract script**, không phải luồng log.

`finance-web` cũng **không có job scrape nào** — nginx không expose `/metrics`,
nên không có metrics tầng web (request rate, 4xx/5xx, latency). Đáng lưu ý vì
`docs/archive/legacy-handoff-agent.md` có ghi một sự cố `502/503` kéo dài ~54 giây mỗi lần deploy
web mà không có metrics tầng đó để đo.

## P3 — Không có định nghĩa alert nào trong version control

Không tìm thấy `vmalert`, `alertmanager`, hay bất kỳ file rule nào trong
`docker/observability/`; production cũng **không chạy container vmalert hoặc
alertmanager** (đếm = 0).

`.agents/rules/production-deployment-verification.md` yêu cầu *"verify affected
alert rules evaluate without new unexpected failures or firing states"*, và
`docs/archive/legacy-handoff-agent.md` từng ghi bằng chứng "32/32 rules healthy" — nên rule nhiều
khả năng nằm **trong database của Grafana**, không phải trong git.

**Chưa kiểm chứng:** tôi không truy vấn Grafana API (cần credential, và rule cấm
in secret). Nên phát biểu chính xác là: **không có alert nào trong version
control**; việc Grafana có giữ rule nội bộ hay không thì vòng này không xác minh.

Hệ quả nếu đúng: alert không được review qua code, không rollback được theo commit,
và mất cùng lúc với Grafana volume.

## Những phần đang ĐẠT

- **Logging:** cả 5 repo (kể cả finance-web qua nginx) phát JSONL đúng chuẩn.
- **Tracing bật thật trên production**, không chỉ khai báo: `OTEL_TRACES_ENABLED=true`
  xác nhận trong `finance-mw-1`, `live-action-*`, `finance-broker-*`, `mt5-*`
  (kiểm bằng `env | grep -c`, không in giá trị nào).
- **W3C propagation qua Kafka có thật ở cả hai runtime**: Go tại
  `finance-mw/pkg/kafka/tracing.go:48,55` (inject/extract, có test khẳng định
  header không đụng payload, `tracing_test.go:34`), Rust tại
  `finance-live-action/crates/finance-kafka/src/consumer.rs:343-351` và
  `crates/finance-api/src/observability.rs:95-96,244-245`.
- **Hạ tầng khoẻ:** elasticsearch, filebeat, kibana, grafana, victoriametrics,
  vmagent, otel-collector, tempo — 8/8 healthy (uptime 3-6 ngày).

## Checklist xác minh (cho người sửa P1)

1. `docker exec <vmagent> wget -qO- http://127.0.0.1:8429/api/v1/targets` — đếm
   `activeTargets`, phải khớp **số container đang chạy**, không khớp config.
2. Không còn target nào `health != up`; đặc biệt `finance-job-worker` phải biến mất.
3. Có đủ 4 job worker và đủ **6** instance live-action.
4. Trên Grafana, panel của 4 worker và 2 route bybit phải có dữ liệu hiện tại
   (dùng instant query, không dùng series lịch sử).

## Giới hạn của review này

- Không xác minh độ tươi của document ECS trong Elasticsearch (cần credential).
- Không xác minh rule alert bên trong Grafana (cần credential).
- Chỉ đọc production read-only; không sửa gì, không deploy gì.
- Không kiểm `/metrics` của từng service một cách độc lập ngoài đường vmagent.
