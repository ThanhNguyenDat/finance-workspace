# Round 42 (2026-08-20) — Xác nhận giả thuyết Funding Rate bằng dữ liệu công khai thật, không cần chờ hạ tầng nội bộ

Status: research thật, dùng dữ liệu bên ngoài (Binance public API, không
cần auth), không phải backtest qua `finance-research`. Round 22 đề xuất
Funding Rate Extreme Reversion nhưng chưa test được vì thiếu hạ tầng (wire
funding vào `Strategy` trait) — round này **tự validate giả thuyết trước
bằng dữ liệu độc lập bên ngoài**, để biết đáng đầu tư code mới hay không
trước khi Codex bắt tay implement.

## Phương pháp

Fetch trực tiếp `https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000`
(public endpoint, không cần API key) — trả về 500 bản ghi funding thật
(~5.5 tháng, 2026-03-05 → 2026-08-20, funding rate + mark price mỗi lần
settle). Chia funding rate thành percentile: **HIGH** (≥p90, ~10% cực trị
dương — long quá đông), **LOW** (≤p10, ~10% cực trị âm — short quá đông),
so sánh forward return giá sau K kỳ funding tiếp theo (K=1≈8h, 3≈24h,
9≈72h, 21≈168h/1 tuần) với baseline (toàn bộ mẫu).

## Kết quả — XÁC NHẬN rõ ràng, đúng hướng giả thuyết

| K (thời gian tới) | HIGH funding (long đông) forward return | LOW funding (short đông) forward return | Baseline (toàn mẫu) |
|---|---|---|---|
| 1 kỳ (~8h) | -0.109% | -0.108% | +0.020% |
| 3 kỳ (~24h) | **-0.456%** | -0.097% | +0.044% |
| 9 kỳ (~72h) | **-0.926%** | **+0.943%** | +0.038% |
| 21 kỳ (~168h, 1 tuần) | **-1.795%** | **+1.429%** | -0.166% |

**Đúng dấu, đúng hướng dự đoán, và độ lớn tăng dần theo thời gian (không
phải nhiễu ngẫu nhiên):** funding cực dương (long đông) → giá có xu hướng
GIẢM về sau (-1.8% sau 1 tuần); funding cực âm (short đông) → giá có xu
hướng TĂNG về sau (+1.4% sau 1 tuần). Cả 2 đều lệch rõ so với baseline gần
0. **Đây chính xác là chữ ký của mean-reversion, không phải trùng hợp với
xu hướng chung của thị trường** — nếu chỉ là market drift chung thì cả 2
nhóm (HIGH và LOW) sẽ cùng dấu, nhưng ở đây chúng lệch ngược nhau rõ rệt.

## Giới hạn trung thực (không giấu)

1. **Mẫu không lớn**: chỉ 44-51 quan sát mỗi nhóm cực trị (10% của 500 bản
   ghi) — đủ để thấy pattern nhất quán nhưng chưa đủ cho kết luận thống kê
   chặt chẽ (không tính p-value/confidence interval ở đây).
2. **Không phải methodology honest-holdout đầy đủ** của chương trình này
   (train/validation/holdout split, no-lookahead framework) — đây là 1 kiểm
   tra sơ bộ nhanh bằng dữ liệu ngoài, không thay thế cho backtest thật khi
   đã có code.
3. **Mark price tại thời điểm settle**, không phải giá đóng nến chính xác 1
   strategy thật sẽ dùng để entry/exit.
4. **Chỉ test BTC/binance** — chưa test XAU/binance (funding perpetual
   khác) vì API tương ứng cho XAUUSDT có thể khác cấu trúc, chưa verify.

## Ý nghĩa: NÂNG mức ưu tiên cho đề xuất Round 22

Trước round này, Funding Rate Extreme Reversion chỉ là "chưa bị phủ định vì
chưa test được" — mức độ tin cậy thấp, giống 1 ý tưởng chưa kiểm chứng. Sau
round này: **có bằng chứng thực nghiệm độc lập, đúng hướng, đúng độ lớn kỳ
vọng, tăng dần theo thời gian holding** — đáng để ưu tiên cao hơn hẳn so
với các đề xuất khác còn lại trong backlog (ensemble regime-switching vẫn
cần thiết kế thêm, ICT/FVG bị cảnh báo lookahead). Đây là hướng có khả năng
đáng đầu tư code nhất trong toàn bộ backlog hiện tại.

## Cập nhật SUMMARY-priority-backlog.md

Đã nâng mức ưu tiên mục 1 (Funding Rate) từ "chưa test được" thành "có bằng
chứng thực nghiệm bên ngoài ủng hộ, vẫn cần code để test honest đầy đủ
trong hệ thống".

## Cập nhật Round 43: test thêm XAU/binance — KHÔNG transfer, thậm chí NGƯỢC DẤU

Đúng giới hạn #4 đã nêu ở trên ("chỉ test BTC, chưa test XAU") — round 43
tự bổ sung. Fetch `fundingRate?symbol=XAUUSDT&limit=1000` (500 bản ghi thật,
funding mỗi 4h không phải 8h như BTC):

- **63.4% bản ghi funding = 0 chính xác**, và **chưa từng có funding ÂM
  trong toàn bộ mẫu** (min=0.0, max=0.00033369) — thị trường XAU perpetual
  mỏng, không đối xứng như BTC, không test được vế "short đông" (low
  funding) vì không tồn tại dữ liệu.
- **Vế "long đông" (top decile, HIGH funding) cho kết quả TRÁI NGƯỢC hoàn
  toàn với BTC:** forward return dương +1.886% sau ~84h (BTC: -1.795% sau
  168h) — funding cao ở XAU đi kèm giá TIẾP TỤC TĂNG, không đảo chiều.

**Kết luận: KHÔNG áp dụng logic funding-reversion của BTC cho XAU.** Có thể
là momentum/continuation thay vì reversion ở XAU, hoặc chỉ là artifact của
mẫu quá thưa (63% zero, thị trường mỏng) — chưa đủ tin cậy để kết luận theo
hướng nào, chỉ chắc chắn 1 điều: **không giống BTC, cần xử lý riêng theo
đúng Rule 4 (mỗi token 1 setup riêng)**. Đề xuất cho Codex: nếu implement,
CHỈ áp dụng cho BTC/binance ban đầu, KHÔNG mở rộng sang XAU/binance cho tới
khi có thêm dữ liệu/nghiên cứu riêng — đã sửa lại phạm vi đề xuất Round 22
(trước đó ghi "áp dụng BTC/binance + XAU/binance", giờ chỉ còn BTC).

## Cập nhật Round 44 — QUAN TRỌNG: out-of-sample test làm giảm độ tin cậy, không phủ định hoàn toàn

Đúng tinh thần honest-holdout của cả chương trình này (Round 13/34 đã
falsify candidate bằng cách test window khác) — tự lấy thêm 2 cửa sổ lịch
sử BTC độc lập hoàn toàn (2024 H1 và 2025 H1, cùng phương pháp, cùng
`fundingRate` API, dùng `startTime`/`endTime` để lấy dữ liệu cũ hơn):

| Cửa sổ | HIGH funding fwd ret (K=21≈1 tuần) | LOW funding fwd ret | Baseline (ALL) |
|---|---|---|---|
| 2026 H1-ish (Round 42 gốc) | -1.795% | +1.429% | -0.166% |
| 2024 H1 (mới) | +2.486% (SAI HƯỚNG) | +0.682% (yếu) | +1.615% (baseline chính nó đã tăng mạnh) |
| 2025 H1 (mới) | -1.619% | +1.174% | +0.510% |

2/3 cửa sổ xác nhận đúng hướng (2025 H1 khớp tốt với Round 42 gốc); 1/3 cửa
sổ (2024 H1) KHÔNG khớp, thậm chí sai hướng. Nhìn kỹ 2024 H1: đây là giai
đoạn BTC tăng giá rất mạnh (baseline toàn kỳ đã +1.615% ở K=21, gấp ~10 lần
baseline của 2 cửa sổ kia) — khả năng cao: hiệu ứng reversion bị lấn át bởi
1 xu hướng tăng mạnh kéo dài, đúng đặc điểm đã biết rộng rãi của mọi chiến
lược mean-reversion (yếu/thua khi gặp trend mạnh kéo dài) — không phải giả
thuyết sai hoàn toàn, mà là giả thuyết chỉ đúng khi không có trend áp đảo.

Kết luận đã điều chỉnh (không còn "ưu tiên implement ngay" như Round 42-43
nữa): giả thuyết funding-reversion vẫn có cơ sở thật (2/3 cửa sổ), nhưng
KHÔNG nên implement như 1 signal đứng độc lập — nên kết hợp với 1 regime/
trend filter (ví dụ: chỉ áp dụng funding-reversion khi KHÔNG đang trong
trend mạnh, đo bằng ADX hoặc tương tự) trước khi tin dùng thật. Đây là điểm
giao thoa thú vị với đề xuất ensemble/regime-switching Round 36-38 — có
thể coi 2 hướng này là 1 nhóm vấn đề chung (mọi signal đơn lẻ đều có điểm
mù theo regime), không phải 2 đề xuất tách biệt.

## Cập nhật Round 45 — tự test luôn đề xuất "trend filter" từ Round 44, kết quả HỖN HỢP

Trước khi đề xuất Codex thiết kế regime-filter, tự test ngay ý tưởng đơn
giản nhất: loại bỏ các thời điểm có |biến động giá 9 kỳ gần nhất| >= 3%
(proxy đơn giản cho "đang trong trend mạnh"), xem funding-reversion có nhất
quán hơn không, trên cả 3 cửa sổ đã có.

| Cửa sổ | HIGH không lọc | HIGH có lọc trend | LOW không lọc | LOW có lọc trend |
|---|---|---|---|---|
| 2024 H1 | +2.486% (sai) | +2.056% (vẫn sai) | +0.682% (đúng, yếu) | -0.439% (SAI, tệ hơn) |
| 2025 H1 | -1.619% (đúng) | -1.702% (đúng, tốt hơn chút) | +1.174% (đúng) | +1.910% (đúng, tốt hơn nhiều) |
| 2026 gần đây | -1.795% (đúng) | -0.765% (đúng nhưng YẾU ĐI) | +1.429% (đúng) | +2.111% (đúng, tốt hơn) |

**Kết luận trung thực: lọc trend theo biên độ (magnitude) đơn giản KHÔNG
giải quyết được vấn đề.** Cải thiện ở 2025 H1 và phần LOW của 2026, nhưng
**không cứu được 2024 H1 chút nào** (vẫn sai hướng cả 2 vế sau khi lọc) và
thậm chí làm YẾU ĐI vế HIGH của 2026. Gợi ý: vấn đề không đơn giản là "đang
biến động mạnh hay không" (magnitude), có thể cần xét **hướng trend so với
dấu funding** (funding dương nhưng trend đang tăng THUẬN theo funding thì
khác với funding dương nhưng trend đã đảo chiều) — phức tạp hơn 1 filter
biên độ đơn giản. Không đề xuất Codex implement filter kiểu "loại trừ biến
động mạnh" đơn giản — cần thiết kế regime-detector tinh vi hơn nếu muốn
theo đuổi tiếp, hoặc chấp nhận hướng ensemble/multi-signal (Round 36-38)
thay vì cố sửa 1 signal đơn lẻ.

## Cập nhật Round 46 — test thêm "hướng trend vs dấu funding", KHÔNG nhất quán, ĐÓNG hướng patch đơn giản

Theo đúng gợi ý cuối Round 45 ("có thể cần xét hướng trend so với dấu
funding") — chia funding cực trị thành 2 nhóm: **AGREE** (funding cùng
hướng trend đang diễn ra, "đang cưỡi theo trend") vs **DISAGREE** (funding
cực trị nhưng giá đã bắt đầu đảo hướng, "funding trễ so với giá").

| Cửa sổ | HIGH+AGREE | HIGH+DISAGREE | LOW+AGREE | LOW+DISAGREE |
|---|---|---|---|---|
| 2024 H1 | +2.184% (sai) | +2.837% (sai) | +0.664% | +0.698% |
| 2025 H1 | **-2.761%** (DISAGREE yếu hơn AGREE) | -0.364% | +2.129% | +0.566% |
| 2026 gần đây | +0.218% (gần 0) | **-3.472%** (DISAGREE mạnh hơn hẳn AGREE) | +1.890% | +1.002% |

**Không nhất quán giữa các cửa sổ — 2025 H1 và 2026 cho kết quả TRÁI NGƯỢC
nhau** (2025: AGREE mạnh hơn DISAGREE; 2026: DISAGREE mạnh hơn AGREE hẳn).
2024 H1 vẫn sai hướng ở cả 2 nhóm, không được cứu bởi cách chia này.

**Kết luận cuối cùng cho hướng patch bằng filter đơn giản: ĐÓNG.** Đã thử 2
cách filter khác nhau (biên độ trend Round 45, hướng trend Round 46) — cả 2
đều KHÔNG cho kết quả nhất quán đủ để tin cậy implement. Đề xuất cuối cùng:
**không tiếp tục patch signal funding-reversion bằng filter đơn giản nữa**
— nếu muốn dùng, nên đưa vào ensemble đa-signal (Round 36-38, để trọng số
tự điều chỉnh theo hiệu suất thay vì cố định 1 rule filter cứng), hoặc để
dành làm 1 trong nhiều input cho 1 model phức tạp hơn (không phải rule-based
đơn giản) nếu sau này có hướng ML. Không nên đầu tư thêm thời gian test
filter rule-based đơn giản cho signal này nữa.
