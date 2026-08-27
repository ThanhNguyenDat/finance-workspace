# Hạ tầng Docker dùng chung

Thư mục này là source-of-truth cho hạ tầng dùng chung của hệ sinh thái Finance:

- `infrastructure/`: Kafka, PostgreSQL/TimescaleDB, Redis, RabbitMQ và image
  maintenance cho dữ liệu.
- `observability/`: OpenTelemetry, Tempo, VictoriaMetrics agent, Grafana,
  Elasticsearch/Filebeat/Kibana và POC Kafka → ClickHouse/S3.

Các file này không thuộc ownership của Finance MW runtime. Giai đoạn cutover
hiện vẫn giữ bản compatibility trong `finance-mw/docker/`; chỉ xoá bản đó sau
khi mọi Make target, script, test, workflow và Coolify raw Compose đã chuyển
sang workspace hoặc owner hạ tầng tương ứng.

Không commit credential runtime (`.env`, password, token, key). Bản seed lần
này đã loại `docker/observability/elasticsearch/.env` và local `.env.poc`; dùng
file example/secret manager theo runbook khi chạy thật.

POC ClickHouse trong `observability/poc/` chỉ dùng local validation, không tự
động deploy production.
