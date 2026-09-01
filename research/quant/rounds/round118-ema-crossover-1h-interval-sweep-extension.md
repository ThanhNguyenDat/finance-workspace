# Round 118 (2026-08-23) — Mở rộng interval sweep cho `ema_crossover_12_26` (điểm neo Round 78) sang 1h — BTC ổn định thêm 1 mốc, XAU near-miss tự loại vì mẫu mỏng

Status: research thăm dò, không thêm code mới (chỉ chạy lại candidate có
sẵn `ema_crossover_12_26` ở base interval khác). Chạy 4 route 5 năm ở
`--interval 1h`, 2 cặp song song (`--cpus=2 --memory=4g --memory-swap=6g`,
Rule 9).

## Bối cảnh

Không có commit mới từ Codex, 2 bug Bybit vẫn chưa xử lý. Round 78 (đã
đóng) từng quét `ema_crossover_12_26` ở 15m/30m và tìm ra 30m là "candidate
ổn định nhất chương trình", nhưng chưa từng test 1h/2h/4h — Round 118 mở
rộng đúng dimension này (khác việc tune tham số candidate đã đóng nhiều
lần trước) để hoàn thiện interval sweep, không phải p-hacking lại candidate
cũ.

## Kết quả — 5 năm, 3 split, cả 4 route, `--interval 1h` (chi phí thật)

| Route | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|
| BTC/binance | 0.861 | 0.892 | 0.825 | 290 |
| BTC/exness | 0.853 | 0.874 | 0.851 | 288 |
| XAU/binance | **1.125** | 0.652 | **1.053** | 38 |
| XAU/exness | 0.673 | 0.914 | 0.858 | 191 |

## BTC ở 1h: ổn định, cross-broker gần như trùng khớp — thêm 1 mốc tham khảo

BTC/binance (0.861/0.892/0.825) và BTC/exness (0.853/0.874/0.851) gần như
trùng khớp nhau — cùng dạng ổn định, không giật cục đã thấy ở 30m (Round
78: BTC 0.907/0.819/0.774). 1h cho PF nhỉnh hơn 30m một chút nhưng cùng
kết luận: vẫn <1 mọi split, không promote. Ghi nhận thêm 1 mốc tham khảo
cho điểm neo `ema_crossover_12_26` (giờ có bằng chứng ổn định ở cả 30m và
1h cho BTC).

## XAU/binance: train+holdout >1 nhưng zigzag + mẫu quá mỏng — tự loại, không cần cross-check 18 tháng

XAU/binance 1h cho train=1.125 VÀ holdout=1.053 đều >1, nhưng validation
tụt xuống 0.652 ở giữa (mẫu 38-112 trade/split) — đúng dạng zigzag + thin-
sample đã tự loại nhiều lần trong chương trình (Round 107, 114's ADX-
filtered MFI). Không cross-broker nhất quán (XAU/exness cùng interval cho
shape hoàn toàn khác: 0.673/0.914/0.858). Theo đúng kỷ luật đã áp dụng
nhất quán: **không cần cross-check cửa sổ 18 tháng** vì bằng chứng đã tự
loại ngay trong window 5 năm (thiếu nhất quán nội tại + mẫu quá mỏng để
tin cậy).

## Kết luận

Không promote. Mở rộng thành công dimension interval cho điểm neo
`ema_crossover_12_26` — BTC xác nhận ổn định thêm ở 1h, XAU không cho thêm
bằng chứng đáng tin. Không cần thiết tiếp tục quét 2h/4h ngay — nếu muốn,
để round sau quyết định dựa trên độ ưu tiên khác.

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách, không có code mới cần review (chỉ
  research thăm dò trên candidate có sẵn).
