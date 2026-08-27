# Round 113 (2026-08-23) — On-Balance Volume signal-line crossover (candidate volume-là-tín-hiệu-chính đầu tiên trong chương trình) — ĐÓNG, PF/win-rate thấp nhất phiên này

Status: research, thêm `ObvTrendStrategy` (candidate mới hoàn toàn, state
cộng dồn toàn bộ stream chứ không phải rolling window như mọi candidate
khác) vào `finance-research/src/strategies.rs`. Chạy 4 route 5 năm, 2 cặp
song song (`--cpus=2 --memory=4g --memory-swap=6g`, Rule 9).

## Bối cảnh

Không có commit mới từ Codex. Round102 follow-up còn chờ market mở cửa lại
(22:00 UTC). Mọi candidate trước đây dùng volume chỉ như filter xác nhận
(`VolumeFilterStrategy`) trên 1 tín hiệu giá đã có sẵn — chưa candidate nào
dùng volume làm **nguồn tín hiệu chính**. Round 113 test OBV (On-Balance
Volume) — tổng cộng dồn volume theo dấu hiệu tăng/giảm giá, khác hẳn về bản
chất toán học (state phụ thuộc toàn bộ lịch sử từ lúc bắt đầu, không phải
cửa sổ rolling cố định như Donchian/RSI/CCI).

## Implementation

`ObvTrendStrategy`: OBV cộng dồn (+volume nếu close tăng, -volume nếu
giảm), tín hiệu nổ khi OBV cắt qua đường tín hiệu (SMA(20) của chính OBV) —
cùng convention crossover như `SmaTrendStrategy`. Vì OBV vốn cần state toàn
stream, state được giữ trực tiếp trong struct strategy (giống
`ParabolicSarStrategy`/`IchimokuCloudStrategy`), không phải hàm indicator
thuần trong `finance-strategy` (đã ghi rõ lý do trong doc comment).

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật)

| Route | train PF | valid PF | holdout PF | win% (holdout) | trades (holdout) |
|---|---|---|---|---|---|
| BTC/binance | 0.365 | 0.343 | 0.310 | 14.0% | 12,586 |
| BTC/exness | 0.321 | 0.304 | 0.290 | 13.5% | 16,022 |
| XAU/binance | 0.212 | 0.164 | 0.145 | 8.1% | 1,747 |
| XAU/exness | 0.092 | 0.120 | 0.225 | 11.7% | 11,052 |

## Nhận xét — PF/win-rate thấp nhất trong toàn phiên nghiên cứu này

Win rate 6.7-15.5% — **thấp nhất từng thấy** trong toàn bộ 8 candidate mới
test phiên này (mọi candidate khác đều ≥12.6%, đa số 20-50%). Tần suất tín
hiệu cực cao (tới 53,878 lệnh train BTC/exness) cho thấy tín hiệu cắt
đường trung bình của OBV rất nhạy/nhiễu trên 5m — bản chất cộng dồn volume
khiến OBV dao động rất thường xuyên quanh đường tín hiệu của chính nó. BTC
2 broker vẫn nhất quán hướng (0.365/0.343/0.310 vs 0.321/0.304/0.290) — xác
nhận đây là tín hiệu thật (không phải nhiễu ngẫu nhiên riêng 1 broker),
chỉ là tín hiệu quá yếu/nhiễu để dùng được.

Không có ô nào gần breakeven nên **không cần cross-check 18 tháng**.

## Kết luận — ĐÓNG

Không promote. OBV signal-line crossover ở tham số chuẩn (period 20) là
candidate yếu nhất phiên này. Không có động lực thử sweep tham số (period
dài hơn có thể giảm nhiễu nhưng khoảng cách tới breakeven quá xa để kỳ vọng
1 tham số cứu được). Đóng hẳn hướng "volume làm tín hiệu chính qua OBV cộng
dồn" ở dạng crossover thô.

## ⚠️ Cập nhật Round 116 — sửa claim không chính xác trong tiêu đề/nội dung

Codex root-review (khi absorb candidate vào commit `7d85cdb`) chỉ ra đúng:
claim "candidate volume-là-tín-hiệu-chính đầu tiên" **không chính xác** —
`TakerImbalanceStrategy`/`TakerImbalanceFadeStrategy` (Round 72-75, đã đóng
từ trước) đã dùng volume (taker buy/total ratio) làm tín hiệu chính rồi,
không phải chỉ làm filter như tôi hiểu nhầm lúc viết round này. Chính xác
hơn: OBV là candidate đầu tiên dùng **cumulative signed total-volume**
(tổng cộng dồn có dấu) làm tín hiệu — khác taker imbalance (tỷ lệ, không
cộng dồn qua thời gian) chứ không phải "volume-primary đầu tiên" nói chung.
Không đổi kết luận CLOSED hay số liệu PF/win-rate — chỉ sửa cách diễn đạt
nguồn gốc cơ chế cho chính xác. Cảm ơn Codex đã bắt lỗi này.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `ObvTrendStrategy` làm bản
  ghi closed-candidate (research-only), hoặc revert nếu không cần giữ.
