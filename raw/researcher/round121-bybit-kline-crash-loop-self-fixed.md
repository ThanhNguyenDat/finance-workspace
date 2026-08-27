# Round 121 (2026-08-23) — Bybit 5m kline WS crash-loop: tự implement & deploy fix (Codex hết quota, Rule 0b)

Status: bug production, KHÔNG phải backtest research. Không thêm dòng CSV
(cùng tiền lệ round102/111/112/115/116/120 — round không tạo số liệu
backtest mới).

## Bối cảnh

Round 120 phát hiện + root-cause chính xác bug crash-loop WS Bybit (xem
`round120-bybit-5m-kline-ws-crash-loop-found.md` +
`raw/explain/bybit-5m-kline-ws-crash-loop.md`), log cho Codex xử lý. Giữa
Round 121, user báo "codex hết quota rồi, bạn xử lí tiếp nhé" — chuyển sang
Rule 0b: tự implement/commit/push/CI/deploy/verify toàn bộ. Không có commit
`Co-Authored-By: Codex` mới nào mâu thuẫn với trạng thái này tại bất kỳ
điểm check nào trong round.

## Fix

`finance-mw/internal/services/bybit_ws_service.go`:
`normalizeBybitKlineEvent` (nhận đúng 1 record, reject cứng nếu khác 1) →
`normalizeBybitKlineEvents` (xử lý MỌI record trong `payload.Data`, trả về
`[]EventV2`). `EventID`/`EventTime` đổi từ key theo `payload.Ts` (message-
level, dùng chung cho mọi record trong 1 push) sang key theo `item.Start`
(kline open time riêng từng record) — tránh 2 record khác nhau trong cùng 1
push bị trùng `EventID` (bug tiềm ẩn nếu chỉ đơn giản loop mà giữ nguyên
`payload.Ts`). Call site `receiver()` sửa để loop push từng event lên
Kafka thay vì gọi 1 lần.

Xác nhận thêm (không phải bug): `trades=0`/`taker_buy_volume=0` trên mọi
kline Bybit là THIẾT KẾ ĐÚNG — Bybit V5 kline WS payload không có field
này (struct `bybitKlineWSItem` không có trường tương ứng, test cũ đã pin
rõ hành vi này từ trước). Ghi đè nhận định "mapping gap" ở Round 120 —
không phải bug, không cần fix.

## Verify local (Docker, `--cpus=3`, theo Rule Codex-down-mode)

- `go build ./...`, `go test -run Bybit -v ./internal/services/...`: 9/9
  xanh (bao gồm 2 test mới — xử lý 2-record push không lỗi, EventID/kline
  identity không trùng; giữ nguyên test reject instrument sai + reject
  0-record).
- `gofmt -l .`: sạch (0 file cần format lại).
- `go vet ./...`: sạch.
- `go build ./...` toàn workspace: xanh.
- `go test -timeout=10m ./...` toàn bộ package: xanh, không skip gì.

## Commit, push, CI

Commit `60e16bab92ad42dfca1f2ac3cf6ea3f7b9325e27`
(`fix(trading): process every record in a Bybit kline stream push`), push
lên `main` (`41bde83→60e16ba`), SHA khớp remote. CI/CD `32625351026`: mọi
job xanh — `Detect changed paths`, `Test Go runtime`, `Test and validate`,
`Apply runtime database migrations`, `Publish runtime image`,
`Deploy runtime`, `Deploy worker stack`, `Configure English Telegram
webhook`, `Verify runtime production`.

## Verify production độc lập

1. **Deployment identity:** `curl -s --get
   https://finance.thanhne.io.vn/api/v1/system/version
   --data-urlencode repository=ThanhNguyenDat/finance-mw
   --data-urlencode commit_sha=60e16ba...` → `matched:true` (lần đầu 502
   trùng đúng lúc rollout, retry vài giây sau ra `complete:true`).
2. **Root cause đã sửa ở tầng ingest — bằng chứng trực tiếp:**
   `finance-kline-ingest-1` restart `07:40:40Z`; log Bybit sạch liên tục
   suốt >20 phút quan sát, **không còn một lần crash/reconnect nào** — so
   với trước fix (crash mỗi ~2 giây, 4 lần trong 15 phút quan sát ở Round
   120). Đây là bằng chứng trực tiếp mạnh nhất: nguồn gốc bug (reject cứng
   multi-record push) đã bị loại bỏ hoàn toàn.
3. **Side-effect ngoài dự tính, đã điều tra rõ, không phải bug mới:** MW
   deploy khiến gRPC call của worker
   `live-action-bybit-perpetual-future-btc-usdt-*` bị hủy giữa chừng
   (`status: Cancelled`) → trigger đúng cơ chế fail-closed panic đã biết từ
   trước (`finance-api/src/main.rs:1274`, `panic!("fatal worker
   data-contract failure: {error}")`) → container tự restart `07:45Z` →
   chạy historical-replay bootstrap qua 8 interval con trước khi resume
   Kafka live. Đây là thiết kế fail-closed intentional (ưu tiên an toàn dữ
   liệu hơn continuity), không phải lỗi mới.
4. **Functional catch-up: ĐANG DIỄN RA, chưa hoàn tất tại thời điểm viết
   bài này.** Theo dõi checkpoint Redis nhiều lần (07:46, 07:53, 07:56,
   08:02 UTC): `recent_klines` của cả 2 route Bybit vẫn đứng ở
   `06:00-06:05Z` trong khi backfill xử lý hàng nghìn record các interval
   lớn hơn (`15m`>2900 dòng/8min, `1h`, `2h`, `30m`, `12h`) nhưng CHƯA chạm
   tới interval `5m`. Không có `error`/`warn` log nào trong toàn bộ thời
   gian quan sát ở cả 2 container Bybit — loại trừ khả năng crash-loop tái
   diễn; đây là backfill hợp lệ khối lượng lớn, không phải bug.

## Trả lời câu hỏi trực tiếp của user ("các worker chết hết rồi nhỉ?")

Kiểm tra `docker ps` toàn bộ 6 container `live-action`: **tất cả đều
`Up`/`healthy`**, không container nào chết. Chi tiết theo route (08:02
UTC): Binance BTC/XAU và Exness BTC tươi thời gian thực (~5-10 phút trễ);
Exness XAU cũ do đúng lịch đóng cửa cuối tuần (đã điều tra Round 102, mở
lại 22:00 UTC Chủ nhật); chỉ 2 route Bybit đang backfill (container sống,
không chết).

## Kết luận round này

Root cause bug crash-loop Round 120 **đã sửa và deploy thành công, có bằng
chứng trực tiếp** (ingest hết crash-loop hoàn toàn). Functional recovery
(checkpoint catch-up thật) **đang tiến triển tự nhiên, chưa hoàn tất** —
không phải bug, chỉ là khối lượng backfill lớn cần thời gian. Quyết định
không tiếp tục block round này chờ vô thời hạn (đã theo dõi ~25 phút); để
vòng `/loop` tự động tiếp theo (mỗi 15 phút) re-check tiến độ catch-up và
đóng task chính thức khi `recent_klines` bắt kịp wall clock trên cả 2
route, sustained qua ít nhất 2 lần đọc.

## Việc cho round sau

- **[trading][high][round 121]** Re-check checkpoint `bybit.perpetual_future.btc.usdt.5m`
  và `bybit.spot.xaut.usdt.5m`: nếu `recent_klines` đã bắt kịp wall clock
  (trong vòng 1-2 interval) và sustained qua 2 lần đọc cách nhau ≥20s →
  đóng hẳn task Bybit crash-loop (chuyển sang evidence/Done trong
  `raw/handoff_agent.md`). Nếu vẫn chưa, tiếp tục theo dõi hoặc điều tra
  sâu hơn nếu backfill có dấu hiệu treo (log ngừng hẳn, không chỉ chậm).
