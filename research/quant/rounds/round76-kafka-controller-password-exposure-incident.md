# Round 76 (2026-08-21) — Sự cố bảo mật: lộ `KAFKA_CONTROLLER_PASSWORD` do lệnh quá rộng

Status: security incident + review. Round này định hoàn thành nốt việc
review hạng mục Kafka còn lại trong `Verify` (để lại từ Round 74), nhưng
phát hiện sự cố bảo mật khi đang kiểm tra.

## Việc đang làm

Kiểm tra hạng mục `Verify`: "Kafka research replay isolation and configured
historical engine are live and verified" (claim ACL `research-replay-ro`
deny-by-default, chỉ đọc prefix `market.kline.v2`). Bắt đầu bằng kiểm tra
port binding (an toàn, chỉ dùng `ss`/`docker port`, xác nhận `19092` chỉ
bind `127.0.0.1`, không lộ ra ngoài — khớp claim). Sau đó định tìm file
config admin client để chạy `kafka-acls.sh --list`, chạy `docker exec
finance-kafka-node1-... env` để tìm đường dẫn.

## Sự cố: lệnh `env` in ra TOÀN BỘ biến môi trường, bao gồm cả credential thật

Lệnh này không lọc gì — in ra mọi biến môi trường của container, trong đó có
`KAFKA_CONTROLLER_PASSWORD` (credential nội bộ dùng cho KRaft controller
quorum auth, cluster single-node: `CONTROLLER_QUORUM_VOTERS=0@finance-kafka-node1:9093`).
Giá trị này giờ nằm trong tool-output/transcript của tôi.

**Đã xử lý ngay theo đúng quy trình Round 20:**
1. Không lặp lại giá trị credential ở bất kỳ đâu (kể cả log này).
2. Báo ngay cho user trong cùng lượt hội thoại (transparency).
3. Dừng ngay việc dò thêm ACL/env theo cách rộng.
4. Log P0 vào `docs/archive/legacy-handoff-agent.md` (đã redact hoàn toàn).
5. **KHÔNG tự rotate** — khác với sửa code Rust có thể test/rollback dễ
   dàng, rotate credential controller của 1 cụm Kafka đang chạy là thao tác
   hạ tầng có rủi ro làm gãy quorum nếu sai — để lại cho follow-up cẩn thận
   hơn (hoặc Codex khi có quota trở lại).

## Bài học và cập nhật lâu dài

- **Cập nhật memory** (`feedback_no_broad_env_dumps.md`): không bao giờ chạy
  `docker exec <container> env` không lọc trên container production — luôn
  grep đúng biến cần, hoặc đọc file config.
- **Cập nhật skill `quant-research-loop`** (commit `16a0d7e`, finance-mw):
  thêm cảnh báo tương tự vào mục "Production verification" để các round sau
  không lặp lại.
- Đây là sự cố lộ credential **thứ 2** trên đúng container Kafka này (lần 1:
  Round 20, `KAFKA_CLIENT_PASSWORDS`, do lỗi redaction regex; lần 2: Round
  76, `KAFKA_CONTROLLER_PASSWORD`, do không lọc gì cả) — 2 credential khác
  nhau, cùng 1 nguyên nhân gốc (thao tác quá rộng trên hệ thống nhạy cảm).

## Chưa hoàn thành việc review Kafka ACL gốc

Hạng mục `Verify` gốc vẫn CHƯA được xác nhận lại đầy đủ (chỉ mới xác nhận
port binding an toàn) — để lại cho round sau, dùng phương pháp an toàn hơn
(grep đúng biến, không dump toàn bộ env).
