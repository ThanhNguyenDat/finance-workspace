# VictoriaMetrics query auth wiring — local delivery note

Ngày ghi nhận: 2026-08-27 (UTC+7)

## Phạm vi

Finance MW đã có client query VictoriaMetrics hỗ trợ Basic Auth qua
`VICTORIAMETRICS_QUERY_USERNAME` và `VICTORIAMETRICS_QUERY_PASSWORD` ở commit
`7ade99b`, nhưng deployment automation trước đó không giữ hai biến này trong
Coolify application env. Vì vậy endpoint `/api/v1/observability/kline-latency`
có thể trả 502 sau khi VictoriaMetrics bật auth.

## Thay đổi local

- `scripts/coolify-deploy.sh` chỉ xóa application env ngoài nhóm `SERVICE_FQDN_*`,
  `SERVICE_URL_*` và hai key VictoriaMetrics query; các key khác vẫn bị dọn như
  trước.
- `scripts/rotate-victoriametrics-http-auth.sh` xác nhận đúng application
  `finance-mw` (`ftj9mknbxl7rljmwtoielnnb`), upsert hai key production
  (`is_preview=false`), kiểm tra mỗi key có đúng một bản ghi và rollback cùng
  cặp giá trị khi rotation lỗi. Payload secret được tạo từ stdin của `jq`,
  không ghi credential vào log/argv.
- Thêm contract test `scripts/tests/test_victoriametrics_http_auth_rotation.sh`
  và mở rộng `test_coolify-deploy.sh`; quality workflow chạy cả hai với timeout.

Finance MW commit local: `aaab7a9`.

## Verification local

- `bash -n` cho rotation/deploy script: pass.
- `test_victoriametrics_http_auth_rotation.sh`: pass.
- `test_coolify-deploy.sh`: pass, durable query keys không bị DELETE.
- `go test -timeout=10m ./pkg/observability ./pkg/setting ./internal/interfaces/http`: pass.
- `go vet ./pkg/observability ./pkg/setting ./internal/interfaces/http`: pass.
- Workflow YAML parse: pass.

## Chưa thực hiện

Chưa push, CI, Coolify hoặc production mutation theo owner-held push gate. Bước
live còn lại cần owner thực hiện guarded reconciliation với credential
`finance-monitor`, redeploy Finance MW và kiểm tra từ trong container MW rằng
query trả HTTP 200 (credential cũ phải trả 401), sau đó ghi immutable image/SHA
và timestamp vào handoff. Không ghi credential hoặc giá trị masked vào tài liệu.
