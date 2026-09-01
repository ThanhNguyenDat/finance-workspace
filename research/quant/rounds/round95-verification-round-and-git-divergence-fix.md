# Round 95 (2026-08-23) — Vòng verify: đóng 6 mục Verify, xác nhận 1 correction đúng từ Codex, và fix 1 rủi ro git-divergence thật trước khi nó gây conflict

Status: verification + git hygiene, không có backtest số liệu mới (không cập
nhật CSV round này — không có instrument/strategy result mới để log).

## 1. Review Dev-done: Round93 Heikin-Ashi + Round92 docs correction

Codex đã tự implement 2 việc tôi log ở Round 92/93 thành commit sạch riêng
(`a5317ac2`/`b599a43` cho Heikin-Ashi, `a089ad2` cho docs Round92) — cả 2
build/test/fmt xanh trong Docker, giữ Dev-done chờ push tới khi XAU marker
lane đóng để tránh làm stale pin đang chạy. Không cần hành động thêm.

## 2. Verify: Codex sửa đúng 1 điểm chưa chính xác trong Round 89 của tôi

Codex correction (commit `56437f2`, đã deploy production, verify độc lập
bằng `docker inspect` khớp đúng SHA): Round 89 tôi mô tả `risk_fraction=0.02`
tạo đòn bẩy hiệu dụng "~2x equity" cho CẢ 2 broker — thực ra **chỉ đúng cho
Binance perpetual (leverage cap 10x, không chạm cap)**. Trên **Exness CFD
(leverage cap 1x)**, `executable_notional = min(desired=2×equity,
equity×leverage=1×equity) = 1×equity` — bị cap xuống 1x, tức stop-budget
thực chỉ 1% chứ không phải nhãn 2% ghi trên rule. Đã đọc trực tiếp code
`executable_notional()` trong `trading_modes.rs` xác nhận đúng công thức
cap này, và Codex đã thêm regression test
`risk_fraction_exposure_uses_the_configured_venue_leverage_cap` cụ thể hoá
quan hệ này (Binance 2.0x/2% stop-budget, Exness 1.0x/1% stop-budget).

**Không làm sai lệch kết luận chính của Round 89/90** (cả 2 sizing mode vẫn
compounding lỗ hình học trên Alpha PF<1) — chỉ là mô tả cơ chế "vì sao
Exness lỗ ít hơn Binance chút" (98.22% vs 99.94%) lẽ ra phải nêu rõ nguyên
nhân là cap đòn bẩy khác nhau giữa 2 venue, không phải cùng 2x cho cả hai.
Cảm ơn Codex đã bắt lỗi này — accept correction.

## 3. Phát hiện + fix: local checkout `finance-live-action` bị lệch khỏi `origin/main`, có rủi ro conflict thật

Trong lúc review, phát hiện `origin/main` đã tiến 3 commit
(`b65c367`→Donchian, `56437f2`→risk_fraction docs, `2840dcc`→Keltner) trong
khi checkout local của tôi (dùng để research suốt Round 88-94) vẫn ở
`082437b` — working tree của tôi có 396+ dòng uncommitted TRÙNG LẶP với
những gì Codex đã commit sạch (Donchian, Keltner) cộng thêm phần thật sự
mới (Heikin-Ashi Round 93, MTF-filtered Round 94).

**Đã fix an toàn** (không dùng lệnh phá huỷ): backup file hiện tại ra ngoài
→ `git checkout --` để trả file về trạng thái HEAD cũ → `git merge --ff-only
origin/main` (fast-forward sạch, đúng quy tắc "giữ local main = origin/main"
trong `coding-and-verification.md`) → khôi phục lại nội dung backup → xác
nhận diff giờ CHỈ còn đúng phần thật sự mới (Heikin-Ashi + 2 candidate MTF
Round 94, 264 dòng, không trùng lặp Donchian/Keltner nữa) → build/test/fmt
lại toàn bộ, 92/92 test xanh bao gồm cả 3 regression test
`round88_registers_.../round91_registers_.../round93_registers_...` xác
nhận đúng grid mỗi round.

**Bài học quy trình cho các round sau:** vì Codex hoạt động song song và có
thể commit/push bất kỳ lúc nào giữa các round, bắt buộc `git fetch origin
main` + so sánh `HEAD` với `origin/main` mỗi đầu round (không chỉ mỗi 5-10
round) trước khi dùng lại working tree cũ có uncommitted diff nhiều round
liên tiếp — diff càng để lâu càng dễ trùng lặp/conflict với commit thật của
Codex.

## Kết luận Verify → Done (6 mục)

Đã chuyển 6 mục `[trading][evidence]` sang Done sau verify độc lập (CI/SHA/
production image, không tin lời kể): Round 87 factorial, Round 86 R:R,
Round 89/90 risk_fraction exposure (+ correction đã xác nhận đúng), Round
88/91 Donchian+Keltner permanent record, ICT/FVG queue-cleanup, priority
backlog summary read-confirmation.

## Việc cho round sau

Không có action item mới. Tiếp tục theo dõi khi nào Codex push
Heikin-Ashi/docs-Round92 (đang chờ XAU marker lane đóng) và cân nhắc round
sau có nên tiếp tục Rule 2/3 hay quay lại kiểm tra production trend PnL
1-2 ngày sau deploy Round 80/83 (chưa từng làm bước này, giờ đã đủ thời gian
kể từ Round 80/83's deploy 2026-08-21).
