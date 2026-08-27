# Round 123 (2026-08-23) — Xác nhận qua code: historical-replay bootstrap huỷ cả batch 8-interval khi 1 stream lỗi, root cause thứ 2 của backfill Bybit gần-livelock

Status: code investigation, không backtest mới. Không thêm dòng CSV.

## Bối cảnh

Tiếp nối Round 122 (phát hiện `KLINE_MAX_CONCURRENT_HISTORY_STREAMS=1`
chặn cả backtest lẫn backfill Bybit). Đầu Round 123, kiểm tra lại tiến độ
2 route Bybit thì thấy hiện tượng lạ: vị trí replay `5m` của route XAUT
**nhảy LÙI thời gian** — nghi vấn cần điều tra thêm.

## Quan sát

Theo dõi log filter đúng `interval:5m` route XAUT qua nhiều lần đọc:

| Thời điểm | Vị trí replay `5m` |
|---|---|
| 08:06Z | 24/2/2026 |
| 08:11-08:17Z | tiến tới 26/5/2026 (tiến bộ thật, ~3 tháng/11 phút) |
| **08:53Z** | **27/2/2026 (LÙI ~3 tháng so với 08:17Z!)** |
| 08:54-08:55Z | tiến đều 15/2→16/2→17/2→19/2/2026 (~1 ngày/15s) |

`docker inspect` loại trừ hẳn giả thuyết "container crash/restart":
container XAUT `RestartCount=0`, `StartedAt=05:49:19Z`, chạy liên tục
xuyên suốt — hiện tượng nhảy lùi xảy ra TRONG CÙNG 1 process, không phải
do restart.

## Root cause — xác nhận qua code, không chỉ suy đoán

`finance-live-action/crates/finance-api/src/historical_replay.rs`:

- `bootstrap_pending_intervals` (dòng 160): mở đồng thời tối đa 8 stream
  (1 cho mỗi interval còn pending: 5m/15m/30m/1h/2h/4h/12h/1d), mỗi stream
  gọi `KlineService::Stream` — đúng RPC bị Round 122 phát hiện giới hạn
  `defaultMaxConcurrentHistoryStreams=1` phía MW.
- Vòng merge chính (dòng 271): `streams[stream_index].advance().await?`
  — dùng `?`, nghĩa là **BẤT KỲ 1 trong 8 stream lỗi sẽ huỷ ngay lập tức
  toàn bộ batch**, không chỉ riêng interval lỗi.
- `bootstrap_historical_replay` (dòng 30) bắt lỗi này, chỉ
  `tracing::warn!("Historical trading replay bootstrap unavailable")` rồi
  trả về — không phân biệt interval nào đã xong, interval nào chưa.

`finance-live-action/crates/finance-api/src/main.rs:750-772`: vòng lặp
ngoài gọi `bootstrap_historical_replay` lặp lại (backoff khởi đầu 5s) nếu
`pending_replay_intervals()` còn khác rỗng — **và `from_time = to_time -
replay_days` được tính lại mỗi lần gọi**, không dùng watermark đã đạt
được. Nghĩa là: interval `5m` đã tiến bộ thật tới 26/5/2026 trong lần thử
trước, nhưng vì batch đó bị huỷ do MỘT interval KHÁC lỗi (rất dễ xảy ra:
2 route Bybit × 8 interval = 16 stream tranh đúng 1 slot MW), lần retry
tiếp theo lại mở stream `5m` MỚI từ điểm bắt đầu lịch sử cũ.

## Tại sao không phải data-correctness bug

Log "Skipping duplicate or stale replay of closed kline" (đã thấy xuyên
suốt từ Round 120) chính là cơ chế dedup: candle cũ đã xử lý được nhận
diện và bỏ qua nhanh khi gặp lại, không xử lý lại/không sai dữ liệu. Cái
mất chỉ là THỜI GIAN — mỗi lần retry phải quét-bỏ-qua lại toàn bộ backlog
cũ trước khi chạm lại đúng điểm dừng thật.

## Kết luận

Dưới áp lực contention hiện tại (2 instance Bybit × 8 interval tranh đúng
1 slot MW — Round 122), stream lỗi xảy ra thường xuyên hơn tốc độ tích luỹ
tiến bộ thật, tạo hiệu ứng gần-livelock — giải thích tại sao backfill Bybit
đã chạy >70 phút mà `5m` (interval Portfolio dùng) vẫn chưa bắt kịp
real-time.

**Không tự sửa** — đây là core replay-bootstrap logic dùng chung cho MỌI
broker (không riêng Bybit), thay đổi cần cân nhắc kỹ (đúng tinh thần "core
decision-algorithm-adjacent" của skill guide, không phải instrument-scoped
fix đơn giản). Hướng gợi ý cho Codex (chưa quyết định):
- Retry đúng interval lỗi thay vì huỷ cả batch, hoặc
- Dùng watermark (điểm đã xử lý xong) làm `from_time` mới thay vì hằng số
  cố định mỗi lần retry.

## Việc cho round sau

- **[trading][medium][round 123]** Theo dõi Codex xử lý (nếu Codex có
  quota lại) hoặc tiếp tục quan sát backfill Bybit tự hội tụ (chậm nhưng
  không sai) — chi tiết đầy đủ → `raw/handoff_agent.md` entry
  `[trading][medium][round 123]`.
