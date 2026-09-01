# Bybit broker integration — research findings + implementation anchors

Requested directly by user (2026-08-23, ngoài vòng lặp `/quant-research-loop`):
"tích hợp thêm Bybit vào" + "sort theo ABC trên web cho dễ nhìn". User đã
chọn rõ 2 điều qua `AskUserQuestion`:
1. **Ai implement:** Codex (giữ narrowed-mode — Claude chỉ research/log, không
   tự commit vào production).
2. **Phạm vi:** **Full integration ngay** — không chỉ research candidate, mà
   broker thứ 3 đầy đủ (kline ingest, worker live, Portfolio routing, web UI,
   deploy) tương đương quy mô Binance/Exness hiện tại.

## Đã có sẵn trong code — không phải bắt đầu từ 0

Domain model **đã có `Broker::Bybit`** từ trước (`finance-core/src/market_event.rs:18-22`,
enum `Broker { Binance, Bybit, Mt5, Exness }`) và **đã dùng thật** ở 2 chỗ trong
`finance-mw`:

- `internal/services/leverage_constraints.go` — `getBybitLeverage`/
  `getBybitMarkPrice` gọi public API `https://api.bybit.com/v5/market/
  instruments-info`, `/v5/market/risk-limit`, `/v5/market/tickers` với
  `category=linear` (không cần credentials) để lấy leverage constraints/mark
  price cho tính risk sizing.
- `internal/interfaces/grpc/servers/funding/funding_service_server.go` —
  `listBybit` gọi `/v5/market/funding/history?category=linear` (không cần
  credentials) để lấy funding rate history, dùng cho
  `--actual-funding-broker` trong `finance-research`.
- `finance-api/src/config.rs` đã parse `broker` từ env var generic
  (`"binance, bybit, mt5, exness"` là danh sách hợp lệ), có test
  `assert_eq!(broker, Broker::Bybit)` — config layer đã broker-agnostic.

Kết luận: **credentials/auth KHÔNG cần thiết** cho phần market-data/leverage/
funding — mọi endpoint Bybit đã dùng trong code đều là public, không key.
Điều này khớp với việc hệ thống hiện đang chạy **paper/simulated** (xem
`finance-broker/app/services/binance.py`: `open_position`/`close_position`
là stub chưa implement; web có disclaimer "Simulated Alpha/Portfolio values
are not Binance, Bybit or MT5/Exness statement truth" tại
`TradingBusinessTargetsPanel.tsx:224`) — nên Bybit cũng chỉ cần market-data
đọc, không cần order-execution credentials để đạt "full integration" đúng
nghĩa tương đương Binance/Exness hiện tại.

## Xác nhận thực nghiệm — API Bybit đã test trực tiếp (read-only, không auth)

```
curl "https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=5&limit=2"
→ OK, trả candle 5m chuẩn [startTime, open, high, low, close, volume, turnover]

curl "https://api.bybit.com/v5/market/kline?category=spot&symbol=XAUTUSDT&interval=5&limit=3"
→ OK, trả candle 5m cho XAUT (Tether Gold, token hoá vàng thật, giá bám sát
   giá vàng giao ngay)
```

**Lưu ý quan trọng về XAU trên Bybit:** `category=linear` (nơi BTC hoạt
động, giống Binance) **KHÔNG có XAUUSD** — đã test `symbol=XAUUSD` trả
`retCode:10001 params error: symbol invalid`. Sản phẩm "XAUUSD+"/TradFi
Perpetual/TradFi CFD (được quảng cáo trên web Bybit, xem câu hỏi trước của
user) **không nằm trong REST `/v5/market/*` public chuẩn** — có vẻ thuộc 1
namespace API riêng (TradFi), chưa xác minh được endpoint/auth requirement
cụ thể trong lượt research này. Sản phẩm gold **duy nhất xác nhận hoạt động
qua API chuẩn, không cần auth** là **XAUTUSDT** (`category=spot`) — token
hoá vàng (Tether Gold), khác về bản chất microstructure với XAU/USDT
perpetual tổng hợp của Binance hay XAU/USD CFD MT5 thật của Exness (thanh
khoản crypto-spot, không phải FX/CFD).

**Khuyến nghị quyết định kiến trúc cho Codex:** dùng `XAUTUSDT` (category
spot) làm nguồn XAU cho Bybit trong lần tích hợp đầu, ghi rõ trong code
comment/doc rằng đây là token hoá vàng chứ không phải hợp đồng gold CFD/
perpetual thật — nhất quán với cách chương trình research đã luôn phân biệt
rõ instrument semantics (vd: XAU/binance vốn cũng đã là 1 cặp
tổng hợp XAU/USDT, không phải spot gold thật). Nếu sau này Codex tìm ra
endpoint TradFi thật có XAUUSD+ không cần MT5-style riêng, đó sẽ là lựa chọn
tốt hơn — nhưng không nên block việc tích hợp Bybit BTC + Bybit XAU(T) vào
chờ điều đó.

## Kiến trúc cần đụng tới — theo đúng pattern 2 broker hiện tại

### 1. Kline ingestion (finance-mw, Go)
Mirror `internal/services/binance_ws_service.go` (`BinanceWSSerivce`,
415 dòng) — WebSocket client, heartbeat, reconnect backoff, normalize event,
push Kafka. Bybit WS public endpoint:
`wss://stream.bybit.com/v5/public/{linear|spot}/kline.{interval}.{symbol}`
(xác nhận có tồn tại qua doc chính thức:
https://bybit-exchange.github.io/docs/v5/websocket/public/kline — chưa tự
test WS trong lượt research này, chỉ REST). Wiring worker mới vào
`internal/initialize/kline_ingest.go` (hiện chỉ thấy 1 worker
`"binance_websocket"` — cần thêm `"bybit_websocket"` tương tự, và xác nhận
có cần 1 worker riêng cho Exness/MT5 bridge để tham khảo pattern đa-broker).

### 2. Portfolio decision worker (finance-live-action, Rust)
- `crates/finance-core/src/market_event.rs` — `Broker::Bybit` đã có, không
  cần sửa.
- `crates/finance-api/src/deployment_rules.rs` — thêm subscription
  `Broker::Bybit` cho BTC/USDT (linear) và XAU/USDT (spot, dùng XAUT) vào
  `configured_portfolio_rules()`/danh sách production subscriptions (xem
  dòng ~693-696 nơi 4 subscription hiện tại được liệt kê), cùng
  `production_candidates()` cho instrument mới.
- `crates/finance-data/src/binance.rs` — có `BinanceClient` làm reference
  pattern cho 1 client mới (`bybit.rs`) nếu Rust-side cũng cần gọi trực tiếp
  Bybit REST (kiểm tra xem worker Rust có tự fetch kline hay chỉ tiêu thụ
  Kafka đã ingest sẵn từ Go service — dựa trên kiến trúc hiện tại, khả năng
  cao là chỉ tiêu thụ Kafka nên có thể KHÔNG cần client Rust riêng, chỉ cần
  Go-side ingestion).

### 3. Broker/statement service (finance-broker, Python)
Mirror `app/services/binance.py` (`BinanceService`, 102 dòng: `get_klines`,
`get_exchange_info`, `get_price`, `open_position`/`close_position` stub) →
tạo `app/services/bybit.py` + `app/dto/bybit.py` cùng pattern. Vì hệ thống
đang paper-only, `open_position`/`close_position` có thể giữ nguyên dạng
stub như Binance hiện tại.

### 4. Deploy (finance-live-action Docker Compose)
`docker/compose.commodity.yaml` là ví dụ rõ nhất: mỗi route là 1 service
block riêng dùng chung `BROKER: ${BROKER:-binance}` env override (xem dòng
93-128, `live-action-binance-perpetual-future-xau-usdt` /
`live-action-exness-cfd-xau-usd` / `live-action-exness-cfd-btc-usd`). Thêm
`live-action-bybit-linear-btc-usdt` + `live-action-bybit-spot-xaut-usdt`
theo đúng pattern (image tag, hostname, `APP_NAME`, `BROKER: bybit`).
Repo cũng có sẵn `compose.large-cap.yaml`/`compose.altcoin.yaml`/
`compose.memecoin.yaml` — cấu trúc scale-theo-category đã tồn tại sẵn cho
tương lai, không cần thiết kế mới.

### 5. Web UI (finance-mw, React/TS) — bao gồm yêu cầu "sort ABC"
- `web/src/shared/config/compositions.ts` — thêm 2 (hoặc nhiều hơn) entry
  Bybit vào mảng `COMPOSITIONS`, theo đúng shape hiện có (`key`, `baseAsset`,
  `quoteAsset`, `broker: 'Bybit'`, `marketType`, `group`). **Đặt entry Bybit
  giữa Binance và Exness trong mảng** (B-i-nance < B-y-bit < Exness theo thứ
  tự chữ cái) để khớp yêu cầu sort ABC ngay tại nguồn.
- `web/src/app/components/Sidebar.tsx:36` — **đây là chỗ quyết định thứ tự
  hiển thị broker thật sự trên UI**: `const brokers = [...new
  Set(compositions.map(composition => composition.broker))];` hiện lấy thứ
  tự theo insertion-order của mảng `COMPOSITIONS`, KHÔNG sort tường minh.
  Cần sửa thành `.sort()` (vd: `[...new Set(...)].sort((a, b) =>
  a.localeCompare(b))`) để đảm bảo ABC thật sự bất kể thứ tự khai báo trong
  `compositions.ts` sau này — đây là fix bền vững hơn là chỉ dựa vào việc
  chèn đúng vị trí trong mảng.
- Kiểm tra thêm `web/src/features/trading/utils/klineChart.ts` và
  `web/src/features/trading/constants/layerCatalog.ts` (đã thấy có nhắc
  "binance"/"exness") xem có logic nào khác cần biết về broker mới.

## Rủi ro / lưu ý khi Codex implement

- **XAU trên Bybit là token hoá (XAUT spot), không phải CFD/perpetual gold
  thật** — phải ghi rõ trong code comment + doc để tránh hiểu nhầm khi so
  sánh cross-broker trong tương lai (research loop đã rất kỷ luật về việc
  phân biệt rõ semantics từng nguồn dữ liệu).
- Instrument mới (Bybit BTC/XAU) sẽ **không có lịch sử 5 năm** như
  Binance/Exness hiện tại — cần lưu ý continuity/backfill từ ngày bắt đầu
  ingest, tương tự cách XAU/binance từng bị đánh giá "thin sample" trong
  research vì list ngắn.
- Theo đúng `coding-and-verification.md`/`production-deployment-verification.md`:
  chạy full local verification, commit/push, theo dõi CI, deploy qua
  Coolify, rồi verify production (container mới healthy, checkpoint tiến
  triển, không phá vỡ 4 route hiện tại) trước khi coi là Done.
- Đây là thay đổi lớn nhiều repo (finance-mw + finance-live-action +
  finance-broker) — nên cân nhắc chia nhỏ theo lớp (ingestion → worker →
  web UI → deploy) thay vì 1 commit khổng lồ, theo đúng nguyên tắc "Keep
  changes small, focused, reviewable".
