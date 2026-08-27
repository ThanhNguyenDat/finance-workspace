# Chỉ mục tài liệu workspace

`finance-workspace` giữ tài liệu điều phối chung; mã nguồn nằm ở các checkout
chuyên trách được liệt kê trong [README](../README.md).

## Tài liệu đang dùng

- `diagram/`: sơ đồ luồng giữa browser, middleware, worker và broker.
- `runbooks/`: quy trình vận hành, production verification và maintenance.
- `specs/`: contract/kiến trúc đích, gồm observability và decision pipeline.
- `migration/`: các ghi nhận migration/cutover còn đang có hiệu lực.

## Lịch sử

Tài liệu nghiên cứu, kế hoạch triển khai và note đã supersede được giữ nguyên
trong [`archive/`](archive/README.md) để phục vụ audit, nhưng không phải
source-of-truth cho runtime mới.

Khi tài liệu dẫn tới code, ưu tiên repository chuyên trách và SHA/deployed
evidence được ghi trong handoff; đường dẫn checkout local chỉ là tiện ích cho
máy phát triển.
