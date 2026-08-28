# CI/CD chuẩn Finance

## Lane dùng chung

Service runtime mới nên bắt đầu từ
`.github/workflow-templates/finance-service-ci-cd.yml`. Template gọi reusable
workflow `reusable-finance-service-delivery.yml` và giữ một đường giao hàng
duy nhất:

```text
quality (test/lint/build)
        ↓
immutable Docker image (commit SHA)
        ↓
Coolify deploy
        ↓
production check (revision + behavior + observability)
```

Mọi command truyền vào template phải tự có kiểm tra phù hợp với service và
được bọc timeout cứng. Image luôn có tag theo commit (`<service>_sha-<SHA>`),
không deploy bằng tag trôi nổi. Pull request chỉ chạy quality; image/deploy/
production-check chỉ chạy trên push hoặc `workflow_dispatch`.

## Phân ranh workflow

- `*ci-cd*`: build, test, publish immutable image, deploy và kiểm tra production.
- `*rollback*`: thao tác rollback có kiểm tra ancestor, image retention và
  production verification.
- `*evidence*`, `*verification*`: thu thập bằng chứng/research hoặc xác nhận
  độc lập sau delivery; không build lại và không mutate hạ tầng.
- Hạ tầng dùng chung, runner và credential rotation: live-first qua runbook/
  SSH có guard; không tạo workflow GitHub để thay thao tác hạ tầng.

Các service hiện có vẫn giữ workflow chuyên biệt khi cần migration, replay,
multi-app deploy hoặc contract parity. Chúng phải tuân cùng thứ tự và timeout
ở trên; khi đơn giản hoá được thì chuyển sang caller của reusable workflow.
