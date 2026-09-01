# Round 122 (2026-08-23) — Vortex Indicator candidate (code+test xong, KHÔNG có backtest thật) + tìm ra nguyên nhân gốc backfill Bybit chậm

Status: candidate mới implement xong nhưng KHÔNG backtest được do phát hiện
giới hạn hạ tầng thật. Không thêm dòng CSV (không có số liệu PF/win-rate
thật để báo cáo — theo đúng kỷ luật "Leave a metric blank rather than
fabricating it").

## Bối cảnh

Không có commit mới từ Codex (vẫn hết quota, Rule 0b tiếp tục). Round này
dự định: research chiến thuật mới trong lúc chờ Bybit backfill (Round 121)
tự bắt kịp.

## Phần 1 — Vortex Indicator: cơ chế mới, implement + test xong

`finance_strategy::indicators::vortex` (mới): VI+ = tổng `|high[t] -
low[t-1]|` qua N nến, VI- = tổng `|low[t] - high[t-1]|` qua N nến, cả hai
chuẩn hoá bởi tổng true range cùng cửa sổ. Khác cấu trúc mọi crossover đã
test trong chương trình (EMA-cross đo 2 trung bình giá; Ichimoku đo
midpoint rolling high/low) — Vortex đo độ lệch trực tiếp của mỗi nến so
với **extremum đối diện của nến liền trước**.

`VortexIndicatorStrategy` (`crates/finance-research/src/strategies.rs`):
tín hiệu khi dấu `VI+ - VI-` đảo chiều, cùng convention single-sign-flip
như `EmaCrossoverStrategy`/`ElderRayStrategy`. Đăng ký `vortex_indicator_14`
(period textbook chuẩn) trong `candidates()`.

**Verify local (Docker `--cpus=3`):**
- `cargo test -p finance-strategy vortex`: 5/5 xanh (uptrend đọc VI+>VI-,
  downtrend ngược lại, flat series không chia-0, insufficient-data/zero-period
  trả None đúng).
- `cargo build -p finance-research`: xanh, không lỗi.
- `cargo fmt --check`: sạch sau 1 lần fix nhỏ (thiếu xuống dòng).

## Phần 2 — Backtest thật: KHÔNG chạy được, `finance-research` treo `DeadlineExceeded`

Chạy sweep 5 năm BTC/binance qua tunnel: CLI treo, không CPU, không network
I/O quan sát được qua `docker stats` (dù đây hoá ra là artifact đã biết của
`--network host` — không đáng tin). Nghi ban đầu: tunnel SSH cũ (mở từ
10:40 local, không phải của tôi) bị stale — kill + mở tunnel mới, TCP
connect xác nhận hoạt động, nhưng backtest vẫn treo y hệt kể cả với
`--days 7` (rất nhỏ).

**Điều tra sâu bằng `grpcurl` trực tiếp** (loại trừ hoàn toàn CLI/client
làm nghi phạm):
- `instrument.InstrumentService.Stream` → phản hồi tức thì, đầy đủ dữ liệu
  thật (danh sách instrument, bao gồm cả 2 Bybit mới).
- `kline.KlineService.Stream` (đúng RPC `finance-research` dùng để tải
  nến) → `DeadlineExceeded` sau 20s, ngay cả với cửa sổ 7 ngày rất nhỏ.

Đọc trực tiếp `internal/interfaces/grpc/servers/kline/kline_service_server.go`:
```go
const defaultMaxConcurrentHistoryStreams = 1
// One history stream at a time under Finance MW's 512 MiB cgroup. Production
// evidence showed two concurrent streams repeatedly crossing that limit.
```
`Stream()` handler gọi `s.streamGate.Acquire(ctx)` (dòng 262) trước khi xử
lý — một semaphore đúng 1 slot toàn cục. **2 route Bybit đang backfill
lịch sử (Round 120/121) × 8 interval/route đều phải đi qua đúng RPC này**,
nên chiếm slot liên tục.

## Kết luận — giải thích trọn vẹn 2 hiện tượng cùng lúc

1. **Tại sao Bybit backfill chậm bất thường** (Round 121 note): không phải
   hệ thống yếu hay lỗi — 16 tổ hợp interval×instrument đang phải serialize
   qua đúng 1 slot stream duy nhất, mỗi lượt giữ slot cho tới khi xong.
2. **Tại sao `finance-research` treo hoàn toàn**: cùng dùng đúng RPC bị
   giới hạn, nên mọi request research (kể cả 7 ngày) phải xếp hàng sau
   toàn bộ traffic backfill Bybit, quá thời hạn client trước khi tới lượt.

**Không phải bug — thiết kế cố ý** (giới hạn bộ nhớ cgroup, comment ghi rõ
lý do lịch sử). Không tự ý tăng giới hạn — code đã ghi chú "increasing it
requires a reviewed memory-budget change, not only an env edit".

## Việc cho round sau

- **[trading][medium][round 121]** Vortex Indicator: candidate sẵn sàng,
  chờ backtest thật khi slot stream rảnh (Bybit backfill xong hoặc tự
  retry). Chưa commit — giữ local đúng convention.
- Theo dõi Bybit backfill (Round 120/121) tiếp tục — khi xong sẽ tự giải
  phóng slot cho cả 2 việc.
