# Chỉ mục tài liệu workspace

`finance-workspace` giữ tài liệu điều phối chung; mã nguồn nằm ở các checkout
chuyên trách được liệt kê trong [README](../README.md).

- `diagram/`: sơ đồ luồng giữa browser, middleware, worker và broker.
- `notes/`: ghi chú thiết kế và điều tra đã hoàn thành.
- `runbooks/`: quy trình vận hành, production verification và maintenance.
- `specs/`: contract/kiến trúc đích, bao gồm pipeline observability và
  analytics.
- `superpowers/`: kế hoạch/spec thay đổi sản phẩm cần đồng bộ nhiều repo.

Các đường dẫn tới file code trong tài liệu cũ có thể trỏ tới checkout sibling
(`../finance-mw`, `../finance-live-action`, `../finance-web`). Khi đọc trên
GitHub, mở repository tương ứng và giữ nguyên commit/SHA được ghi trong
evidence; không coi đường dẫn local là bằng chứng deployment.
