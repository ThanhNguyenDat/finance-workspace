# Kế hoạch loại bỏ downtime khi deploy Finance Web

Ngày: 2026-08-27 (UTC+7)

## Hiện trạng đã chứng minh

Finance Web production đang chạy dưới một Coolify Docker Compose resource với
một replica duy nhất. Khi Coolify recreate container, probe production đã ghi
nhận `/` và `/healthz` trả `502/503` khoảng 46–54 giây; deployment vẫn xanh sau
khi container mới healthy. Vì vậy healthcheck hiện tại chỉ bảo đảm container
mới sẵn sàng, chưa bảo đảm zero-downtime cho người dùng.

## Mục tiêu nghiệm thu

- Trong rollout bình thường, `/` và `/healthz` không có khoảng trống phục vụ;
  mọi response phải là `2xx` hoặc một lỗi ứng dụng có chủ đích được ghi nhận.
- Container mới chỉ nhận traffic sau khi healthcheck và smoke test (HTML,
  JS/CSS, `/api/v1/system/version`) pass.
- Có thể rollback về immutable image/source SHA trước đó mà không sửa trực tiếp
  repository-owned file trên host.
- Runtime không dùng host port cố định hoặc `container_name` riêng; traffic đi
  qua proxy/load balancer và external Docker network `finance` theo runbook.

## Phương án

### A — Khuyến nghị: resource Dockerfile/build-pack với rolling replicas

Tách Finance Web khỏi Compose single-replica, build image từ repository
`finance-web`, expose cổng nội bộ 80 và khai báo healthcheck `/healthz`. Chạy tối
thiểu hai replica sau proxy/load balancer; rollout giữ replica cũ phục vụ cho tới
khi replica mới healthy rồi mới drain/retire.

Ưu điểm: loại bỏ điểm đơn gây downtime, rollback nhanh theo image SHA, ownership
khớp repository web standalone. Cần owner duyệt resource migration, routing và
chi phí thêm replica trước khi áp dụng.

### B — Tách load balancer khỏi resource hiện tại

Giữ Compose resource nhưng chạy nhiều service/replica phía sau một LB được quản
lý riêng. Phương án này chỉ đạt mục tiêu nếu LB có health-aware draining và
Compose không recreate toàn bộ backend cùng lúc; phức tạp vận hành cao hơn A.

### C — Giữ nguyên một replica

Không đáp ứng mục tiêu zero-downtime; chỉ nên dùng tạm thời trong khi chuẩn bị A
hoặc B. Verifier tránh false negative xuyên rollout nhưng không thể che giấu
outage thực tế.

## Trình tự triển khai sau khi owner phê duyệt

1. Tạo resource mới song song, không dừng resource hiện tại; pin source/image
   SHA bất biến và kiểm tra network, healthcheck, resource limits.
2. Chạy smoke/contract test và probe liên tục trên URL tạm; xác nhận ít nhất
   hai replica healthy và proxy chỉ route tới backend healthy.
3. Chuyển traffic bằng cơ chế reversible của proxy/LB; theo dõi `/`, `/healthz`,
   latency, 5xx và restart trong một cửa sổ đủ dài.
4. Chỉ sau khi đạt mục tiêu mới retire resource Compose cũ qua Coolify; giữ
   image/manifest rollback đã xác nhận.
5. Ghi lại deployment ID, immutable image digest, probe window và rollback test
   vào `raw/handoff_agent.md`; chuyển task sang `Verify` để Claude kiểm tra độc
   lập.

## Cổng quyết định còn mở

- Owner chọn A hay B và xác nhận ngân sách/replica count.
- Owner xác nhận DNS/proxy/LB resource đích và cửa sổ chuyển traffic.
- Chưa được mutate production, xoá Compose resource hoặc tuyên bố zero-downtime
  trước khi ba cổng trên được duyệt.
