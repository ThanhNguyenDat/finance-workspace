# Round 19 (2026-08-20) — Vì sao đổi base interval không tăng tần suất họ MTF trend-filtered

Status: research-only. Test trực tiếp giả thuyết Round 17 đã đề xuất ("dùng
swing 1d trend làm bias/gate cho entry 5m tần suất cao") bằng data thật, thay
vì để đó chờ Codex viết code mới — dùng ngay cơ chế `--higher-timeframe-interval`
đã có sẵn trong CLI (không cần `StrategyKind` mới) để test naive version của ý
tưởng này trước.

## Test: BTC/binance, base=5m, higher-tf=1d, 5 năm (chưa ai test combo 5m+1d
trong cả chương trình này — mọi test MTF trước chỉ dùng 5m+4h hoặc 4h+1d)

Chỉ 2 candidate pass PF>1 nhất quán cả 3 split (so với 4 candidate ở
4h+1d Round 17-18):

| Candidate | Trades (train/val/holdout) | Win% (holdout) | PF (train/val/holdout) |
|---|---|---|---|
| `mtf_rsi_14_20_80_trend_filtered` (mới) | 126/36/45 | 33.3% | 1.091/1.156/1.445 |
| `mtf_stochastic_14_3_30_70_sma50_trend_filtered` | 51/24/29 | 13.8% | 1.687/1.537/1.488 |

So sánh trực tiếp candidate thứ 2 với chính nó ở base=4h (Round 17 baseline,
cùng higher-tf=1d, cùng tham số hệt):

| Metric | 4h/1d (Round 17) | 5m/1d (Round 19) | Thay đổi |
|---|---|---|---|
| Holdout trades | 18 | 29 | +61% (không phải +4800% như base interval 48x nhỏ hơn gợi ý) |
| Trades/week | 0.34 | 0.55 | vẫn cách target 7/tuần rất xa |
| Sharpe | 1.13 | 0.71 | XẤU ĐI |
| Sortino | 3.10 | 2.02 | XẤU ĐI |
| Max neg-day streak | 48 | 47 | không đổi, vẫn fail |
| Net PnL (holdout $) | 1.69 | 1.24 | XẤU ĐI |
| Cost ratio | -2.1% (có lợi) | 2.1% | XẤU ĐI (dù vẫn pass) |

Gate thật (`--daily-profit-gate`) trên bản 5m/1d: `passed=false`, fail
`positive_day_ratio`, `negative_day_streak`, `sharpe_ratio` (3 mục, nhiều hơn
bản 4h/1d chỉ fail 1 mục).

## Kết luận: giả thuyết Round 17 (naive version) bị bác bỏ bằng data thật

Đổi base interval từ 4h xuống 5m (nhỏ hơn 48 lần) chỉ tăng tần suất **1.6
lần** (0.34→0.55/tuần) — và đổi lại mọi metric chất lượng đều xấu đi rõ rệt.
Đọc code `MultiTimeframeTrendFilterStrategy::evaluate`
(`strategies.rs:1089-1130`) xác nhận cơ chế thật: entry **chỉ được forward
khi chính inner strategy (stochastic 14,3,30/70) tự phát tín hiệu trên nến
base-interval VÀ hướng đó khớp dấu SMA(50) của nến higher-tf gần nhất**. Higher-tf
filter chỉ là 1 cổng boolean (đồng ý/không đồng ý), không tự sinh thêm tín
hiệu nào. Vậy trần tần suất thật sự nằm ở tần suất raw của chính oscillator
stochastic trên khung base — và tần suất đó hoá ra KHÔNG scale tuyến tính
theo số nến (đổi 4h→5m không đổi bao nhiêu số lần giá thật sự cắt ngưỡng
30/70 trong 1 tuần lịch thật, vì đó là thuộc tính của biến động giá thật, không
phải của độ mịn nến) — cộng thêm base interval mịn hơn tạo nhiều tín hiệu
"giả" ngắn hạn hơn bị trend-filter loại bỏ nhiều hơn tương ứng (win rate
13.8% ở 5m/1d so với 50.0% ở 4h/1d — noise tăng thật).

**Ý nghĩa cho đề xuất kiến trúc Round 17 ("dùng swing bias gate cho entry
5m"):** phiên bản đơn giản nhất của ý tưởng này (chỉ gate boolean đồng ý/
không đồng ý hướng, dùng lại `MultiTimeframeTrendFilterStrategy` sẵn có) đã
tự test và KHÔNG hoạt động — không cần Codex code lại y hệt cơ chế này để
xác nhận thêm lần nữa. Ý tưởng ban đầu (dùng tín hiệu 5m *độc lập*
`candle_momentum`/`rsi_mean_reversion` đang live, không phải 1 oscillator
swing-scale mới, chỉ filter theo hướng 1d) vẫn chưa bị bác bỏ — đó là 1 inner
strategy có tần suất cao hoàn toàn khác (đã biết fire nhiều trên production),
khác hẳn dùng lại chính oscillator swing này. Giữ nguyên đề xuất P2 gốc,
nhưng làm rõ thêm: **phải dùng đúng 1 trong 2 strategy 5m tần suất cao đang
live làm inner, không phải 1 oscillator swing-tuned lại ở base interval
nhỏ hơn** — đây là phân biệt quan trọng mới rút ra từ round này, tránh Codex
implement nhầm hướng đã test thất bại.

## Không cần thêm hành động ngay

Không đề xuất candidate mới để deploy round này — đây là 1 phát hiện cơ chế
(mechanism finding) giúp thu hẹp đúng hướng implement cho đề xuất đã có, tránh
lãng phí 1 vòng code-review-revert nếu Codex triển khai nhầm version đã bị
bác bỏ.
