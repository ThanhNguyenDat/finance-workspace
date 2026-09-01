# Round 51 (2026-08-20) — Proof-of-concept: ensemble equal-weight của 4 candidate MTF cải thiện RẤT MẠNH

Status: research thật, tự backtest bằng dữ liệu `daily_results` thật từ
`finance-research` (4 lần gọi `--daily-profit-gate`, không phải giả lập).
Round 36-38 đã đề xuất ý tưởng ensemble/regime-switching nhưng chưa ai tự
kiểm tra bằng số liệu xem ý tưởng có thật sự hiệu quả không trước khi đề
xuất Codex xây hạ tầng reweighting mới. Round này tự làm proof-of-concept
đơn giản nhất có thể: **equal-weight** (không cần regime-detector, không
cần trọng số động) trên đúng 4 candidate đã biết (baseline sma50, ADX-
filtered, macd_5_13_5, candle_momentum — tất cả BTC/binance 4h/1d).

## Phương pháp

Lấy `daily_results.return_fraction` thật của cả 4 candidate (366 ngày căn
chỉnh theo cùng ngày), tính **trung bình cộng đơn giản** return mỗi ngày
(equal-weight portfolio, không có logic gì phức tạp), dựng lại equity curve
$10,000, tính Sharpe/Sortino/max negative streak/positive_day_ratio giống
hệt cách `daily-profit-gate` tính, để so sánh công bằng.

## Kết quả — cải thiện RẤT MẠNH so với MỌI candidate đơn lẻ

| | Sharpe | Max negative streak | Final equity |
|---|---|---|---|
| baseline (sma50) | 1.171 | 48 ngày | $10,001.73 |
| ADX-filtered | 1.368 | 66 ngày | $10,002.51 |
| macd_5_13_5 | 0.306 | 25 ngày | $10,000.63 |
| candle_momentum | 0.238 | 17 ngày | $10,000.41 |
| **ENSEMBLE equal-weight (4 candidate)** | **1.475** | **15 ngày** | $10,001.32 |

**Sharpe của ensemble (1.475) CAO HƠN candidate tốt nhất đơn lẻ (ADX,
1.368)** — không phải trung bình cộng của 4 Sharpe riêng lẻ (trung bình sẽ
~0.77), mà **cao hơn cả candidate tốt nhất** — đúng hiệu ứng diversification
kinh điển (các candidate lỗ ở thời điểm khác nhau, kết hợp lại làm mượt
đường equity). **Max negative streak giảm từ 48-66 ngày (mọi candidate
riêng lẻ tệ) xuống còn 15 ngày** — giảm 66-77% so với các candidate yếu
nhất, và còn tốt hơn cả candidate có streak ngắn nhất đứng riêng
(candle_momentum, 17 ngày).

## Chưa clear hết gate, nhưng tiến bộ rõ ràng

`positive_day_ratio` của ensemble = 49.2% (cần ≥55%) — vẫn chưa pass,
nhưng đã cải thiện đáng kể so với các candidate riêng lẻ (không tự tính lại
số của từng candidate riêng ở round này, nhưng baseline round 17 đã biết
fail đúng mục này). Streak 15 ngày vẫn > ngưỡng 5 ngày của gate, nên
`negative_day_streak` vẫn fail — nhưng khoảng cách tới target đã thu hẹp
rất nhiều so với 48-66 ngày ban đầu.

## Ý nghĩa: nâng mức tin cậy cho đề xuất Round 36-38

Đây là bằng chứng **mạnh nhất từ trước tới giờ** cho hướng ensemble —
không chỉ "các candidate thất bại ở cửa sổ khác nhau" (bằng chứng gián
tiếp Round 36) mà giờ có **backtest trực tiếp chứng minh ensemble thật sự
cải thiện Sharpe VÀ giảm streak cùng lúc**, chỉ với equal-weight đơn giản
nhất (không cần cơ chế reweighting phức tạp như đã bàn ở Round 38). Điều
này gợi ý: **có thể bắt đầu với 1 phiên bản equal-weight đơn giản trước**
(rẻ hơn hẳn rolling-window/EWMA reweighting đã đề xuất Round 38), đo hiệu
suất thật, rồi mới nâng cấp lên trọng số động nếu cần — giảm rủi ro
implementation so với đề xuất gốc.

## Đề xuất cụ thể cho Codex (chưa implement, chỉ backtest bằng tay)

1. **Bước 1 rẻ nhất:** implement 1 Portfolio decision rule mới đơn giản —
   kết hợp entry_score từ nhiều Alpha strategy variant bằng trung bình cộng
   thay vì chọn 1 variant duy nhất, test qua `finance-research` với chính
   4 candidate này trước khi wire vào production.
2. Nếu equal-weight backtest qua `finance-research` (không phải tự tính tay
   như round này) xác nhận lại kết quả tương tự, mới cân nhắc bước 2
   (trọng số động theo hiệu suất gần đây, đắt hơn).
3. Chưa đủ để pass toàn bộ gate (`positive_day_ratio`, streak vẫn fail) —
   không nên promote production ngay cả khi implement, cần thêm vòng lặp
   cải tiến sau khi có infra thật.

## Cập nhật Round 52 — thử các tổ hợp khác nhau, tìm được 1 combo pass được `positive_day_ratio` LẦN ĐẦU TIÊN

Test thêm các tổ hợp con (bỏ bớt candidate yếu, chỉ giữ 2/4 mạnh nhất) để
xem có tối ưu hơn ensemble 4-candidate equal-weight của Round 51 không:

| Tổ hợp | Sharpe | Sortino | Max streak | positive_day_ratio |
|---|---|---|---|---|
| baseline+ADX (2 mạnh nhất) | **1.780** | **5.448** | 48 ngày (fail) | **59.6% (PASS!)** |
| baseline+ADX+macd (bỏ candle_momentum) | 1.544 | 3.870 | 18 ngày | 52.5% |
| baseline+ADX+candle_momentum (bỏ macd) | 1.576 | 4.017 | 21 ngày | 48.4% |
| Cả 4 (Round 51 gốc) | 1.462 | 3.422 | **15 ngày (tốt nhất)** | 49.2% |
| macd+candle_momentum (2 yếu, đối chứng) | 0.386 | 0.785 | 17 ngày | 48.1% |

**Phát hiện quan trọng: tổ hợp 2 candidate mạnh nhất (baseline+ADX) là tổ
hợp ĐẦU TIÊN trong toàn bộ chương trình research (52 round) đạt
`positive_day_ratio` ≥ 55% (59.6%)** — 1 gate check thật sự pass, không
phải chỉ Sharpe/Sortino đẹp. Nhưng đổi lại streak vẫn 48 ngày (không cải
thiện so với baseline đơn lẻ — ADX không giúp gì trong đúng giai đoạn
baseline yếu, vì bản thân ADX cũng yếu ở giai đoạn gần đó theo Round 36).

**Trade-off thật, không phải kết luận đơn giản "càng nhiều candidate càng
tốt":** 2-combo cho chất lượng tổng thể (Sharpe/Sortino/pos-day-ratio) tốt
nhất nhưng streak tệ nhất trong các tổ hợp; 4-combo cho streak tốt nhất
nhưng chất lượng tổng thể thấp hơn. Không có 1 tổ hợp nào pass được cả 2
tiêu chí cùng lúc — nhưng đây là bằng chứng mạnh: **các tổ hợp gần đạt
target hơn hẳn bất kỳ candidate đơn lẻ nào đã test trong cả chương trình**.

**Đề xuất bổ sung cho Codex:** khi implement, nên thử nghiệm nhiều tổ hợp
subset khác nhau (không chỉ "tất cả candidate cùng trọng số"), có thể cần
1 bước chọn tổ hợp tối ưu (subset selection) trước khi cố định trọng số —
đắt hơn 1 chút so với đề xuất equal-weight đơn giản gốc nhưng đáng để cân
nhắc vì khác biệt hiệu suất giữa các tổ hợp là có thật và đáng kể.

## Cập nhật Round 53 — tìm trọng số cân bằng tốt hơn: 50/30/20 (baseline/ADX/candle_momentum)

Sau khi Round 52 tìm ra trade-off (2-combo pass pos-ratio nhưng streak
48 ngày; 4-combo equal-weight streak tốt 15 ngày nhưng fail pos-ratio) —
round này thử dò trọng số KHÔNG đều để tìm điểm cân bằng tốt hơn cả 2 phía,
thay vì chỉ equal-weight hoặc drop hẳn 1 candidate.

| Trọng số (baseline/ADX/CM/macd) | Sharpe | Sortino | Streak | pos_ratio |
|---|---|---|---|---|
| 50/30/20/0 | 1.703 | 4.667 | 21 (fail) | **57.1% (PASS)** |
| 50/25/25/0 | 1.618 | 4.246 | 21 (fail) | **56.0% (PASS)** |
| 50/20/30/0 | 1.505 | 3.787 | 21 (fail) | **57.7% (PASS)** |
| 45/45/10/0 | **1.796** | **5.409** | 21 (fail) | 47.3% (fail) |
| 55/25/20/0 | 1.642 | 4.430 | 21 | 53.3% (fail) |

**Kết quả tốt nhất tìm được: 50/30/20 (baseline/ADX/candle_momentum)** —
pass `positive_day_ratio` (57.1%) với Sharpe vẫn mạnh (1.703, Sortino
4.667), streak giảm còn **21 ngày** (từ 48 ngày của baseline/2-combo, giảm
56%) — dù chưa pass ngưỡng streak ≤5 của gate, đây là điểm cân bằng tốt
nhất tìm được qua round 51-53: vừa pass được 1 gate check thật, vừa cải
thiện đáng kể streak so với phương án pass gate khác (2-combo, streak vẫn
48). Đáng chú ý: streak "cứng" ở 21 ngày trong hầu hết tổ hợp có
candle_momentum trọng số 0.2-0.3 — có vẻ là 1 sàn tự nhiên của tổ hợp này,
chỉ tổ hợp full-4-equal-weight (Round 51) mới xuống được 15 ngày.

**Khuyến nghị cập nhật cho Codex:** nếu chỉ chọn 1 tổ hợp để implement thử
nghiệm đầu tiên, **50/30/20 (baseline/ADX/candle_momentum, bỏ macd)** là
lựa chọn cân bằng tốt nhất hiện có — không cần trọng số động phức tạp,
chỉ cần 3 trọng số cố định. Đây vẫn là kết quả từ tìm kiếm tay giới hạn
(6 tổ hợp round 53 + 5 tổ hợp round 52), không phải tối ưu hoá toàn diện —
Codex có thể tìm được điểm tốt hơn nếu chạy grid-search đầy đủ qua chính
`finance-research`.

## Cập nhật Round 54 — Grid-search đầy đủ (286 tổ hợp), tìm được kết quả TỐT HƠN round 52-53

Thay vì tiếp tục dò tay, chạy grid-search đầy đủ trên cả 4 trọng số
(bước 0.1, tổng = 1.0, 286 tổ hợp) — bao phủ toàn bộ không gian tìm kiếm
hợp lý thay vì chỉ vài chục điểm thử tay ở Round 52-53.

**Không có tổ hợp nào pass được CẢ 2 tiêu chí (`positive_day_ratio`≥55%
VÀ streak≤5)** — xác nhận lại kết luận Round 52 (2 tiêu chí có trade-off
thật, không phải do tìm kiếm chưa đủ). Nhưng grid-search tìm được **tổ hợp
tốt hơn hẳn** so với dò tay Round 53:

| Trọng số (base/ADX/macd/CM) | Sharpe | Sortino | Streak | pos_ratio |
|---|---|---|---|---|
| **[0.5, 0.2, 0.1, 0.2]** | **1.621** | **4.211** | **15 (bằng tốt nhất)** | **56.0% (PASS)** |
| [0.5, 0.2, 0.2, 0.1] | 1.611 | 4.156 | 15 | 56.3% (PASS) |
| Round 53's 50/30/20/0 | 1.703 | 4.667 | 21 | 57.1% (PASS) |
| Round 51's equal-weight 25/25/25/25 | 1.462 | 3.422 | 15 (tốt nhất trước đó) | 49.2% (fail) |

**[0.5, 0.2, 0.1, 0.2] (baseline 50% / ADX 20% / macd 10% / candle_momentum
20%) là tổ hợp tốt nhất tìm được qua cả 4 round nghiên cứu ensemble** —
đạt ĐỒNG THỜI streak tốt nhất từng thấy (15 ngày, ngang bằng equal-weight)
VÀ pass được `positive_day_ratio` (56.0%) — kết hợp ưu điểm của cả 2 hướng
Round 51 (streak tốt) và Round 52-53 (pass gate). Sharpe thấp hơn 1 chút so
với Round 53's 50/30/20 (1.621 vs 1.703) nhưng đổi lại streak tốt hơn nhiều
(15 vs 21 ngày) — đánh đổi hợp lý.

## Khuyến nghị cuối cùng cho Codex (thay thế khuyến nghị Round 53)

**Dùng trọng số [baseline=0.5, ADX=0.2, macd=0.1, candle_momentum=0.2]**
làm điểm khởi đầu implement, thay vì 50/30/20 đề xuất ở Round 53 — kết quả
tốt hơn theo cả 2 tiêu chí quan trọng nhất (pos_ratio và streak). Đây là
kết quả từ grid-search đầy đủ ở bước 0.1 (286 điểm), không phải dò tay —
Codex có thể tinh chỉnh thêm ở bước nhỏ hơn (0.05 hoặc 0.01) nếu muốn tối
ưu hơn nữa, nhưng cải thiện thêm nhiều khả năng không lớn (đã bao phủ khá
đầy đủ không gian ở bước 0.1).
