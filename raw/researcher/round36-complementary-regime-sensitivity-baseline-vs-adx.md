# Round 36 (2026-08-20) — sma50 baseline và ADX-filtered "bù trừ" nhau ở 2 regime khác nhau

Status: research-only, phân tích số liệu `daily_results` thật, không
backtest candidate mới, không implement. Trực tiếp follow-up gợi ý Round 35:
kiểm tra candidate ADX-filtered (Round 17/24) có tránh được đúng chuỗi lỗ
48 ngày (2026-04-12→05-29) của candidate baseline hay không.

## Phát hiện: 2 candidate thất bại ở 2 CỬA SỔ THỜI GIAN KHÁC NHAU HOÀN TOÀN

| Candidate | Cửa sổ 2026-04-12→05-29 (baseline's bad window) | Cửa sổ 2025-09-05→11-09 (ADX's bad window) |
|---|---|---|
| `mtf_stochastic_14_3_30_70_sma50_trend_filtered` (baseline) | **48/48 ngày âm** (streak tệ nhất chính nó) | 10 âm / 22 dương / 34 flat, PnL -0.29 (chịu được, không phải streak tệ nhất) |
| `mtf_stochastic_14_3_35_65_adx14_20_sma10_trend_filtered` (ADX) | 6 âm / 42 dương, PnL -0.43 (không phải streak tệ nhất, dù PnL tổng vẫn hơi âm) | **66/66 ngày, streak tệ nhất chính nó** |

**Không phải 1 candidate strictly tốt hơn candidate kia** — mỗi candidate có
đúng 1 "điểm mù" thời gian riêng, và candidate còn lại xử lý tốt hơn hẳn
đúng lúc đó. Baseline thất bại thảm ở Apr-May 2026 nhưng ADX filter tránh
được rõ ràng (42 ngày dương so với 48 ngày âm cùng cửa sổ). Ngược lại ADX
filter thất bại thảm ở Sep-Nov 2025 nhưng baseline chịu được tốt hơn nhiều
(chỉ 10/66 ngày âm, phần lớn flat hoặc dương).

## Ý nghĩa: đây là bằng chứng cụ thể ủng hộ hướng ensemble/regime-switching,
không phải suy đoán chung chung

Toàn bộ chương trình research (Round 17-24) đã kết luận không có 1 filter
đơn lẻ nào giải quyết được cả streak lẫn tần suất cùng lúc. Phát hiện round
này đi xa hơn: **2 filter cụ thể đã test THẤT BẠI Ở 2 REGIME KHÁC NHAU**,
không trùng nhau — đây chính xác là điều kiện lý tưởng để 1 cơ chế
ensemble/switching có giá trị thật (nếu 2 filter cùng fail ở cùng lúc thì
kết hợp chúng không giúp gì, nhưng ở đây chúng KHÔNG trùng thời điểm fail).

**Đề xuất cụ thể (chưa implement, cần thiết kế + code mới):** 1 cơ chế
Portfolio-level chọn/trọng số động giữa 2 (hoặc nhiều) biến thể filter dựa
trên tín hiệu regime nào đó (có thể chính là `reweight_from_alpha_performance`
đã có sẵn — nếu 2 biến thể MTF này được đăng ký làm 2 Alpha strategy riêng
biệt, cơ chế trọng số hiện có theo hiệu suất gần đây CÓ THỂ tự động chuyển
trọng số sang biến thể đang hoạt động tốt hơn mà không cần code logic
switching mới — đáng thử nghiệm ý này trước khi thiết kế cơ chế phức tạp
hơn). Đây là hướng khác hẳn "tìm 1 filter tốt nhất" mà cả chương trình đã
theo đuổi tới giờ — chuyển sang "kết hợp nhiều filter yếu bù trừ nhau".

## Cập nhật cùng round: đã tự kiểm tra thêm 1 candidate thứ 3, giả thuyết MẠNH HƠN hẳn

Test thêm `mtf_macd_5_13_5_sma10_trend_filtered` (Round 17) ở đúng 2 cửa sổ
trên, cộng thêm tìm streak tệ nhất của chính nó:

| Candidate | Apr-May 2026 (baseline's bad window) | Sep-Nov 2025 (ADX's bad window) | Streak tệ nhất của chính nó |
|---|---|---|---|
| baseline (sma50) | **48/48 âm** | 10 âm/22 dương, PnL -0.29 | Apr-May 2026 (48 ngày) |
| ADX-filtered | 6 âm/42 dương, PnL -0.43 | **66/66, streak tệ nhất** | Sep-Nov 2025 (66 ngày) |
| macd_5_13_5_sma10 | 27 âm/21 dương, **PnL +0.28 (dương!)** | 40 âm/26 dương, PnL -0.19 | **Jul 2026 (chỉ 25 ngày, cửa sổ thứ 3 hoàn toàn khác)** |

**3 candidate, 3 cửa sổ streak tệ nhất HOÀN TOÀN KHÔNG TRÙNG NHAU** (Apr-May
2026 / Sep-Nov 2025 / Jul 2026) — không phải trùng hợp ngẫu nhiên với mẫu 2
nữa, đây là mẫu 3/3 độc lập đều xác nhận cùng 1 pattern. macd còn dương hẳn
ở đúng cửa sổ baseline thất bại nặng nhất — bằng chứng mạnh nhất cho tới giờ
rằng các filter khác nhau thực sự nhạy với các regime thị trường khác nhau,
không phải chỉ 1 filter "tốt hơn" các filter khác 1 cách tổng quát.

## Cập nhật Round 37: hoàn thiện candidate thứ 4, kết quả TỔNG THỂ vẫn ủng hộ nhưng có 1 điểm trung thực cần nêu

Test nốt `mtf_candle_momentum_10bps_sma10_trend_filtered` (candidate cuối
của Round 17) qua cả 3 cửa sổ đã biết:

| Cửa sổ | candle_momentum_10bps_sma10 |
|---|---|
| Apr-May 2026 (baseline bad) | +0.71 (dương, tốt) |
| Sep-Nov 2025 (ADX bad) | +0.15 (dương, tốt) |
| Jul 2026 (macd bad) | -0.10 (âm nhẹ) |
| **Streak tệ nhất của chính nó** | **2025-09-03→09-19 (17 ngày — NGẮN NHẤT trong 4 candidate)** |

Bảng tổng hợp cuối cùng, 4/4 candidate:

| Candidate | Streak tệ nhất | Độ dài |
|---|---|---|
| baseline (sma50) | 2026-04-12→05-29 | 48 ngày |
| ADX-filtered | 2025-09-05→11-09 | 66 ngày |
| candle_momentum_10bps_sma10 | 2025-09-03→09-19 | **17 ngày (ngắn nhất)** |
| macd_5_13_5_sma10 | 2026-07 | 25 ngày |

**1 điểm cần nêu trung thực:** streak của `candle_momentum` (Sep 3-19, 2025)
**trùng lấp một phần** với streak của ADX (Sep 5 - Nov 9, 2025) — không phải
4 cửa sổ hoàn toàn tách biệt như claim ban đầu (3/3), mà là **3 cửa sổ chính
tách biệt rõ (Apr-May 2026, Jul 2026, và cụm Sep-Nov 2025)**, trong đó cụm
Sep-Nov 2025 có 2 candidate (`candle_momentum` và ADX) cùng gặp khó nhưng ở
mức độ khác hẳn (17 ngày ngắn/nhẹ vs 66 ngày dài/nặng) — cụm này giống 1
giai đoạn thị trường khó chung, không phải hoàn toàn độc lập. Kết luận tổng
thể (mỗi filter có "điểm mù" khác nhau, kết hợp có thể giảm rủi ro tệ nhất)
**vẫn đứng vững** — `candle_momentum` chịu đựng cụm Sep-Nov tốt hơn hẳn ADX
(17 ngày so với 66 ngày) — nhưng độ độc lập giữa các cửa sổ không hoàn hảo
100% như bản nháp đầu, cần nói rõ để không phóng đại bằng chứng.

## Giới hạn còn lại

Đã test đủ 4/4 candidate Round 17. Đề xuất tiếp theo: thử ngay hướng "để
`reweight_from_alpha_performance` tự chọn" (đã có sẵn trong hệ thống, không
cần code switching mới) trước khi thiết kế cơ chế phức tạp hơn — đây vẫn là
con đường rẻ nhất để tận dụng phát hiện này.
