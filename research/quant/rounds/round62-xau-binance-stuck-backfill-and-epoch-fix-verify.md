# Round 62 (2026-08-21) — Verify fix epoch-migration của Codex + phát hiện bug mới: `pending_history_backfill` kẹt 8 tháng riêng Binance/XAU

Status: verification + bug discovery, đọc trực tiếp Redis production qua SSH
(không qua `finance-research`), theo đúng Rule 5 (check Codex đã implement gì)
và Rule 6 (log bug mới nếu phát hiện trong lúc verify).

## Bối cảnh

`docs/archive/legacy-handoff-agent.md` mục Verify có item **[Trading][P3] Migrate legacy
Portfolio decision epoch for Binance XAU checkpoint** (`bfccc9a`) — sửa bug
`evaluation_count=113` bị so sánh sai đơn vị với `decision counter=69,274`
cũ. Round này verify độc lập item đó, đồng thời nhân tiện kiểm tra ảnh hưởng
thật lên Target 2 (Make Decision rate) — vấn đề đã dai dẳng từ Round
13/23/40/48.

## Bước 1: verify fix epoch-migration — XÁC NHẬN ĐÚNG, chuyển Done

Đọc trực tiếp `{finance-live-action:checkpoints}:worker_checkpoint:*` của cả
4 route qua `docker exec redis-singleton-... redis-cli`:

| Route | `epoch_version` | `evaluation_count` | `updated_at` (fresh?) |
|---|---|---|---|
| Binance/BTC | 1 | 224 | 09:50:02Z — mới |
| Binance/XAU | 1 | 224 | 09:50:00Z — mới |
| Exness/BTC | 1 | 4,857 | 09:50:01Z — mới |
| Exness/XAU | 1 | 461 | 09:50:01Z — mới |

Cả 4 route đều `epoch_version=1` nhất quán, `evaluation_count` đang tăng
đều, không có quality/no-lookahead violation nào. **Fix đúng, đã deploy, đã
verify độc lập** — chuyển item này từ Verify sang Done trong
`handoff_codex.md` với addendum verify.

## Bước 2: đo lại Target 2 trên cùng 1 basis đếm mới (sau epoch reset) — bất cân đối RÕ RÀNG hơn bao giờ hết

`paper-fixed-pct` lifetime `trade_count` (cùng epoch version 1, đo cùng thời
điểm):

| Route | trade_count |
|---|---|
| Binance/BTC | 1,126 |
| Exness/BTC | 1,117 |
| Exness/XAU | 758 |
| **Binance/XAU** | **8** |

So với baseline Round 48 (BTC/binance=1286, BTC/exness=1313, XAU/binance=8,
XAU/exness=735) — các số BTC/binance, BTC/exness đổi vì bộ đếm đã reset theo
epoch mới (không so sánh trực tiếp được nữa), nhưng **XAU/binance vẫn y hệt
8** dù đo trên bộ đếm hoàn toàn mới. Đây là bằng chứng mạnh: XAU/binance
không phải "chậm hơn 1 chút" mà là **thấp hơn 100-140 lần** so với 3 route
kia trên cùng khung đo — mức chênh lệch không giải thích được chỉ bằng "lịch
sử ngắn hơn" (XAU/binance đã list từ Dec 2025, tức đã có ~8 tháng lịch sử —
đủ để tích luỹ hàng trăm nến 1d/4h).

## Bước 3: phát hiện mới — `pending_history_backfill` kẹt 8 tháng, chỉ riêng Binance/XAU

Trong lúc đọc checkpoint, phát hiện field `runtime_state.pending_history_backfill`
(hàng đợi nến chờ backfill lịch sử) có ở cả 4 route nhưng độ "cũ" khác biệt
rõ rệt:

| Route | Số entries (5m) | Khoảng thời gian | Tuổi |
|---|---|---|---|
| Exness/BTC | 1 | 2026-08-16 | ~5 ngày |
| Exness/XAU | 1,000 | 2026-08-07 → 08-12 | ~1-2 tuần |
| Binance/BTC | 508 | 2026-07-21 → 07-22 | ~1 tháng |
| **Binance/XAU** | **508** | **2025-12-23 → 12-25** | **~8 THÁNG** |

3 route kia có timestamp gần hiện tại — hàng đợi này rõ ràng đang xoay vòng
bình thường (nến mới vào, nến cũ được xử lý/xoá). Riêng Binance/XAU đông
cứng đúng tại đợt backfill lịch sử ban đầu lúc mới listing trên Binance, và
**chưa từng nhúc nhích kể từ đó tới nay** (8 tháng).

Kiểm tra thêm `recent_klines` (dữ liệu đang xử lý live) của route này: hoàn
toàn bình thường, mới nhất tới đúng `2026-08-21T09:45Z` (khớp thời điểm hiện
tại) — **worker KHÔNG bị treo/deadlock**, chỉ riêng cụm 508 nến backfill cũ
này bị bỏ quên trong checkpoint, tồn tại song song với hoạt động live bình
thường.

## Ý nghĩa và giới hạn của phát hiện

**Chưa chứng minh được quan hệ nhân-quả trực tiếp** giữa cụm dữ liệu kẹt này
và trade_count=8 bất thường — có thể đây chỉ là rác trạng thái (orphaned
state) vô hại, không ảnh hưởng quyết định thật. Nhưng đây là **manh mối cụ
thể đầu tiên khác hẳn giả thuyết cũ** ("chỉ do lịch sử ngắn", Round 13) —
đáng để Codex điều tra xem liệu cụm nến kẹt từ Dec 2025 có từng chặn một
phần warm-up của Portfolio decision policy cho khung thời gian cao hơn
(1d/4h cần nhiều lịch sử hơn 5m) ngay từ đầu, để lại hậu quả kéo dài (ví dụ
nếu SMA/trend-filter dài hạn không bao giờ "sẵn sàng" đúng cách) dù dữ liệu
live hiện tại vẫn chảy bình thường.

## Đã log cho Codex

- Chuyển **[Trading][P3] epoch-migration fix** từ Verify → Done (verify độc
  lập qua production Redis, không chỉ tin báo cáo).
- Log bug mới **[Data quality][P2] `pending_history_backfill` kẹt 8 tháng
  riêng Binance/XAU** vào đầu mục Todo — không gắn P0/P1 vì chưa xác nhận
  ảnh hưởng thật, nhưng đánh dấu là lead cụ thể nhất từ trước tới giờ cho
  vấn đề Target 2 dai dẳng của route này.

## Không cần test backtest mới round này

Round này thuần verify + audit production state qua SSH, không chạy
`finance-research` — đúng tinh thần Rule 6 ("cần thêm dữ liệu có thể ssh vào
server"). Không thay đổi code, `git status --short` xác nhận sạch ở cả 2
repo sau khi xong.
