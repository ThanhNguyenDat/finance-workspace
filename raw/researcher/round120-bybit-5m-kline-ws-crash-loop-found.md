# Round 120 (2026-08-23) — Production verification: 2 bug cũ đã đóng đúng, tìm ra bug production THẬT thứ 3 trong chuỗi Bybit

Status: pure production verification, không backtest mới. Không thêm dòng
CSV (theo tiền lệ round102/111/112/115/116 — round verification-thuần
không tạo số liệu backtest).

## Bối cảnh

Đầu round: `git log` cho thấy Codex có commit mới ở cả 2 repo kể từ Round
119 — `41bde83` (leverage fix), `c222048` (Bybit live worker deploy) ở
finance-live-action. Theo Rule 1, round này review độc lập thay vì tự
implement.

## Phần 1 — 2 việc cũ: xác nhận CHẠY THẬT trên production

1. **Leverage fix `41bde83`:** `gh run list` xác nhận CI/CD `32622935894`
   thành công (20m4s), sau đó `Production Trading Verification` và
   `Production Web Verification` đều pass lúc 06:46:42Z. Đây là bằng chứng
   độc lập thứ 2 (không chỉ trust file handoff của Codex).
2. **Sidebar `.sort()`:** grep trực tiếp `web/src/app/components/Sidebar.tsx:36-37`
   xác nhận có `.sort((left, right) => left.localeCompare(right))` thật
   trong working tree hiện tại (đã pull tới `41bde83`). Đúng như correction
   đã ghi trước đó trong handoff_agent.md.
3. **2 container Bybit healthy đúng SHA:** `live-action-bybit-perpetual-future-btc-usdt-*`
   và `live-action-bybit-spot-xaut-usdt-*` đều `Up ~1h (healthy)`, image
   `finance-live-action_sha-7d85cdb5d1...` — khớp HEAD.

Tới đây, nếu chỉ dừng ở "container healthy + CI xanh" thì sẽ báo cáo Bybit
integration hoàn tất. Nhưng theo kỷ luật production-deployment-verification.md
("khai thác ít nhất 1 workflow read-only cho mỗi behavior thay đổi, không
chỉ transport success"), đào sâu thêm.

## Phần 2 — Đào sâu: `evaluation_count` tăng KHÔNG đồng nghĩa nhận dữ liệu mới

Lấy checkpoint Redis 2 route Bybit 3 lần, cách nhau ~4 phút:

| Route | eval_count (t0) | eval_count (t0+20s) | eval_count (t0+~3min) | last kline open_time (cả 3 lần) |
|---|---|---|---|---|
| bybit BTC 5m | 1235 | 1376 | 1909 | `2026-08-23T06:00:00Z` (đứng yên) |
| bybit XAUT 5m | 8670 | 8797 | (không đọc lại) | `2026-08-23T06:00:00Z` (đứng yên) |

Giờ thật lúc đọc: 06:51-06:53Z. Candle cuối cùng đóng lúc `06:04:59.999Z`
— lệch **>45 phút** và tiếp tục tăng theo thời gian trong lúc kiểm tra,
trong khi `evaluation_count` (chỉ đo vòng lặp worker chạy, không đo dữ liệu
mới) vẫn tăng đều đặn.

So sánh chéo với route Binance BTC cùng thời điểm: last kline
`06:45:00Z-06:49:59.999Z`, tức gần như real-time, `trades: 7221`.
Tất cả 200 kline buffer của Bybit BTC (và 1000 của XAUT) có `trades=0` và
`taker_buy_volume=0` toàn bộ — Binance thì có giá trị thật khác 0.

## Phần 3 — Root cause: WS crash-loop trong `finance-kline-ingest-1`

Kline ingestion là 1 container/binary RIÊNG (`cmd/kline-ingest`), không
phải `finance-mw-1` (API/gRPC). Log 15 phút gần nhất của
`finance-kline-ingest-1` filter theo "bybit":

```
[BybitWS] instrument=bybit.perpetual_future.BTC.USDT websocket connected     (x5)
[BybitWS] instrument=bybit.perpetual_future.BTC.USDT receiver exited retry=1
  retry_in=2.1s error=Bybit returned 2 kline records in one stream update    (x4)
```

Trace tới `internal/services/bybit_ws_service.go:285-288`:
`normalizeBybitKlineEvent` reject cứng bất kỳ WS push nào có
`len(payload.Data) != 1`, và `receiver()` coi lỗi này là fatal cho TOÀN
BỘ kết nối instrument đó (không chỉ record lỗi) — 1 subscription bao gồm
mọi interval (5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d) chung 1 socket
(`bybitKlineSubscription`). Bybit's kline WS topic không được đảm bảo luôn
gửi đúng 1 record/push — khi gửi 2, code hiện tại sập cả socket, reconnect
~2s, và lặp lại. So sánh log worker trong cùng cửa sổ 20 phút:
Binance BTC xử lý 8 event `5m`; Bybit BTC xử lý 0 event `5m` (chỉ có
46× `1h` + 14× `2h`) — giải thích tại sao interval cao hơn (ít cập nhật
hơn) "sống sót" qua các đợt reconnect trong khi `5m` (interval Portfolio
dùng làm base) không bao giờ kịp qua trước lần crash tiếp theo.

Loại trừ nguyên nhân config/wiring: `bybit_enabled: true` xác nhận cả
trong repo lẫn trong file config đã mount của container đang chạy
(`docker exec ... grep grpc.yaml`, không dump env rộng);
`TRADING_INSTRUMENT_IDENTITIES`/`INTERVALS` (`internal/interfaces/worker/consts.go`)
đúng đầy đủ.

## Kết luận

Bug production thật, đang mở, đã log `[trading][high][round 120]` ở đầu
`raw/handoff_agent.md`, chi tiết đầy đủ tại
`raw/explain/bybit-5m-kline-ws-crash-loop.md`. Đây là bug thứ 3 phát hiện
trong chuỗi Bybit — khác biệt hoàn toàn 2 bug trước (leverage tier lẻ,
XAUT kline-ingest chưa nối) — cả 2 đã đóng, bug này thì chưa. Không tự
implement (Codex còn quota, giữ narrowed-mode).
