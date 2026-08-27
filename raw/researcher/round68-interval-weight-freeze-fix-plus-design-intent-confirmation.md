# Round 68 (2026-08-21) — Xác nhận "zero weight cho loser" là THIẾT KẾ CÓ CHỦ Ý (đóng debate floor Round 65-67) + fix 1 lỗ hổng đóng băng vĩnh viễn thật sự

Status: dev + research + review. Code fix ĐÃ implement + test đầy đủ + commit
`cc0c8ac`, đã push, CI đang chạy.

## Phần 1: đọc doc-comment gốc — đóng hẳn debate "có nên thêm floor không"

Round 65-67 để ngỏ câu hỏi kiến trúc: có nên thêm 1 floor tối thiểu vào
`reweight_from_alpha_performance` để tránh Target 2 sụp hoàn toàn không? Đọc
kỹ doc-comment ngay phía trên hàm (dòng 452-463,
`crates/finance-core/src/trading_modes.rs`):

> "Strategy weights stay neutral until at least one strategy has a mature
> 20-trade profitable observation; after that, unobserved, sparse, and
> mature-losing strategies receive zero quality **instead of diluting the
> demonstrated signal**."

**Đây là thiết kế CÓ CHỦ Ý, không phải bug/thiếu sót.** Tác giả gốc đã cân
nhắc rõ ràng và chọn "không pha loãng tín hiệu tốt bằng tín hiệu đã xác nhận
xấu" làm nguyên tắc thiết kế. Kết luận: **KHÔNG nên thêm floor** — làm vậy
sẽ đi ngược chủ đích thiết kế đã ghi rõ, và bản chất vấn đề Target 2 của
XAU/binance không phải lỗi thuật toán mà là **thực tế**: 2 strategy cấu hình
cho route này thật sự không có edge ở khung ngắn (khớp đúng kết luận nhất
quán của toàn bộ 67 round nghiên cứu trước). Giải pháp DUY NHẤT bền vững
thật sự là tìm được 1 strategy CÓ edge thật + tần suất cao — không phải kỹ
thuật trọng số.

## Phần 2: nhưng phát hiện 1 lỗ hổng robustness THẬT — mất cân xứng giữa 2 nhánh chuẩn hoá

Đọc kỹ 2 hàm chuẩn hoá dùng trong `reweight_from_alpha_performance`:
- `strategy_weights` dùng `normalize_or_uniform_weights` — **CÓ** fallback:
  nếu tổng quality = 0 (mọi strategy đều chưa mature hoặc đã confirm thua
  lỗ), rơi về chia đều (uniform), không bao giờ kẹt ở 0 vĩnh viễn.
- `interval_weights` dùng `normalize_positive_weights` — **KHÔNG CÓ**
  fallback này: nếu tổng = 0, mọi interval_weight ở nguyên 0.0.

**Hệ quả nếu KHÔNG fix:** nếu 1 route có TẤT CẢ interval bắt buộc đều đạt
"mature + confirm thua lỗ" (≥20 trade mỗi interval-role, tất cả strategy),
`role_scores()` (tính `entry_score`/`trend_score` bằng tổng
`interval_weight * strategy_weight * score`) sẽ ra đúng **0.0 mãi mãi** ở cả
2 trục — `minimum_role_score` gate không bao giờ pass — Portfolio **đóng
băng vĩnh viễn**, kể cả khi sau này 1 strategy tình cờ cải thiện (vì
Portfolio bị treo thì không còn sinh trade mới để re-observe hiệu suất).

**Đây không phải giả thuyết — Binance/XAU ĐÃ ở 5/8 interval trong trạng
thái này** (15m/30m/1h/2h/5m, Round 63-67). Chỉ còn 3 interval nữa (1d/12h/
4h) rơi vào cùng trạng thái là route này đóng băng hoàn toàn, không chỉ tần
suất thấp như hiện tại.

## Fix: dùng lại đúng `normalize_or_uniform_weights` cho cả 2 trục

Đơn giản, an toàn, nhất quán — không thêm logic mới, chỉ tái sử dụng hàm đã
tồn tại + đã test cho `strategy_weights`, áp dụng luôn cho `interval_weights`.
Xoá `normalize_positive_weights` (không còn dùng). Thêm doc-comment giải
thích rõ ràng lý do và biên giới với thiết kế "không pha loãng" (fix này chỉ
xử lý trường hợp CỰC BIÊN "tất cả đều 0 cùng lúc", không làm yếu đi việc
zero-out từng loser riêng lẻ).

**Test mới:** `interval_weights_recover_to_uniform_instead_of_freezing_when_every_configured_strategy_is_a_confirmed_loser`
— mô phỏng đúng 2 strategy, cả 2 đều mature (200 trade) + thua lỗ, ở tất cả
8 interval bắt buộc → assert mọi `interval_weight` rơi về đúng `1/8` thay vì
0.

**Verification:**
- `cargo test -p finance-core --test trading_modes`: 53/53 pass (bao gồm 4
  test cũ liên quan reweight, không cái nào bị phá).
- `cargo test --workspace --exclude finance-redis`: 32/32 suite pass (loại
  trừ `finance-redis`'s docker-in-docker test cần Docker lồng Docker, môi
  trường hiện tại không hỗ trợ — không liên quan thay đổi này).
- `cargo fmt --check`: sạch (sau khi auto-fix 1 lần).
- `cargo build --release -p finance-api`: build production thành công.
- Commit `cc0c8ac`, push, CI đang chạy.

## Ý nghĩa cho Target 2

Fix này KHÔNG cải thiện tần suất hiện tại của Binance/XAU (chưa tới lúc
trigger, 3 interval còn lại vẫn >0) — đây thuần là phòng ngừa 1 nguy cơ
tương lai (đóng băng hoàn toàn), không phải fix tần suất thấp hiện tại. Kết
hợp với Phần 1 (xác nhận thiết kế có chủ ý), **Target 2 của XAU/binance
chính thức được xác nhận: không thể giải quyết bằng kỹ thuật trọng số/config
— chỉ có thể giải quyết bằng cách tìm được 1 strategy thật sự có edge ở
khung ngắn cho instrument này**, điều mà 68 round nghiên cứu (cả chương
trình này + thread trước đó `portfolio-btc-optimization-log.md`) chưa tìm
ra được cho bất kỳ instrument nào ở khung 5-15m.
