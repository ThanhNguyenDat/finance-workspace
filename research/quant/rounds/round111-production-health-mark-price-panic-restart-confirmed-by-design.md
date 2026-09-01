# Round 111 (2026-08-23) — Production verification: BTC/binance + XAU/binance worker panic-restart tại 03:08 UTC — xác nhận fail-closed đúng thiết kế, không phải bug

Status: production verification only, không có backtest mới, không đổi code.

## Bối cảnh

1 commit mới từ Codex (`7f70eb3`, CI, không thuộc trading). Round102
XAU/Exness follow-up còn chờ market mở cửa lại (22:00 UTC, còn ~17.5 giờ).
Kiểm tra checkpoint 4 route thấy container `live-action-binance-perpetual-
future-btc-usdt-*` và `live-action-binance-perpetual-future-xau-usdt-*` có
`RestartCount=1`, uptime chỉ ~1 giờ (khác 2 container Exness vẫn 12 giờ) —
điều tra thêm thay vì bỏ qua.

## Điều tra — panic thật, nhưng đúng thiết kế fail-closed

Đọc log container quanh 03:08 UTC:

```
03:08:09-03:08:12  WARN Authoritative mark-price dependency unavailable
                    (tcp connect error, retry, consecutive_failures 1→4)
03:08:42  ERROR Fatal authoritative mark-price refresh failure (transport error)
03:08:42  ERROR Shutting down after fatal worker data-contract failure
03:08:42  thread 'main' panicked at crates/finance-api/src/main.rs:1274:9
03:08:43  WARN Authoritative startup dependency unavailable; worker remains
                fail-closed and will retry (worker khởi động lại, vào retry loop)
```

Đọc đúng source line 1274 tại exact commit đang chạy production
(`56437f2d93c0c47f76e936b0a237ec72baa5a6b6`):

```rust
if let Some(error) = fatal_worker_status.borrow().clone() {
    panic!("fatal worker data-contract failure: {error}");
}
```

Đây là `panic!` **có chủ đích** — khi dependency mark-price authoritative
(cần cho risk sizing) thất bại vượt quá retry budget, worker chủ động crash
thay vì tiếp tục chạy với dữ liệu thiếu/cũ, để Docker restart policy khởi
động lại sạch. Không phải bug logic.

## Root cause đúng — trùng thời điểm MW redeploy

`finance-mw-1` cũng có uptime chỉ "58 phút" tại thời điểm kiểm tra — khớp
chính xác với 03:08-03:09 UTC, cùng lúc 2 worker binance panic. Kết luận:
1 trong các commit gần đây của Codex (`dfa4b82 fix(kline): serialize MW
history replay streams` hoặc `5aa24df feat(observability): capture bounded
MW memory evidence`) đã trigger redeploy MW, gây gián đoạn gRPC ngắn đúng
lúc 2 worker binance đang gọi authoritative mark-price — vượt retry budget,
kích hoạt đúng fail-closed panic. 2 worker Exness không bị ảnh hưởng (có
thể do khác timing gọi dependency, hoặc route khác không cùng path).

## Xác nhận không mất dữ liệu

Checkpoint Redis (`evaluation_count`) của cả 3 route đang hoạt động vẫn
tiến triển bình thường qua sự kiện này (không reset về 0, không gap bất
thường) — xác nhận state persistence qua Redis hoạt động đúng, restart
không gây mất tiến độ.

## Kết luận

Không phải bug, không cần action item mới. Đây là bằng chứng xác nhận đúng
thiết kế fail-closed của hệ thống hoạt động chính xác trong 1 sự kiện MW
redeploy thật (không phải test). Ghi nhận làm evidence, không log Todo cho
Codex.

## ⚠️ CẬP NHẬT Round 112 — kết luận "đúng thiết kế" cần làm rõ hơn: có thể là 1 khoảng hở thật trong error classification

Đào sâu hơn vào commit đã fix hành vi này (`af09209 fix: keep workers alive
during middleware outages`, đã nằm trong `56437f2` đang chạy production —
tức panic Round 111 xảy ra SAU KHI fix này đã deploy, không phải trước).
Đọc đúng `FundingSourceError::is_retryable()` (`crates/finance-api/src/
funding.rs`):

```rust
pub(crate) fn is_retryable(&self) -> bool {
    match self {
        Self::Transport(_) => true,
        Self::Status(status) => {
            matches!(status.code(), tonic::Code::Unavailable | tonic::Code::DeadlineExceeded)
                || (status.code() == tonic::Code::Cancelled && ...)
        }
        _ => false,
    }
}
```

Lỗi thật quan sát được ở Round 111 (`"status: Unknown, message: \"transport
error\""`) là `tonic::Status` với `code() == Unknown` — **KHÔNG nằm trong
danh sách retryable** (chỉ `Unavailable`/`DeadlineExceeded`/`Cancelled`+
timeout được retry). Vì vậy lỗi này đi thẳng vào nhánh Fatal → panic, dù
theo đúng doc comment của hàm ("True only for network/transport-layer
failures a retry can plausibly recover from — a DNS blip, a momentarily
unreachable peer") thì `Unknown`+"transport error" xảy ra đúng lúc MW đang
redeploy (peer tạm thời không reachable) **về mặt ngữ nghĩa khớp chính xác
tiêu chí đó**.

**Không tự kết luận đây chắc chắn là bug** — doc comment cũng cảnh báo rõ
"TRA-928 crash-looped a worker on a poison *data* error mà retry sẽ lặp lại
vô hạn", nên có khả năng `Code::Unknown` bị cố tình loại khỏi danh sách
retry vì đôi khi nó đại diện lỗi data/logic phía server (không nên retry
vô hạn), không chỉ transport. Đây là judgment call cần Codex xem lại code,
không phải điều Quant tự quyết được.

## Việc cho round sau

- **[trading][low]** Log Todo mới cho Codex xem xét: có nên mở rộng
  `is_retryable()` để chấp nhận `tonic::Code::Unknown` khi message khớp
  pattern "transport error" cụ thể (không phải mọi `Unknown`), để tránh
  panic-restart không cần thiết trong các lần MW redeploy tương lai — hay
  giữ nguyên vì lý do đã biết (TRA-928 lesson). Xem addendum này.
- Round sau (sau 22:00 UTC) tiếp tục theo dõi follow-up Round102 XAU/Exness
  weekend reopen như đã lên kế hoạch.
