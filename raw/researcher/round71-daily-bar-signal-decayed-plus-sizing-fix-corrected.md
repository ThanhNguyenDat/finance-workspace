# Round 71 (2026-08-21) — Sửa lại 1 "open lead" cũ (sizing không cứu được cost tỷ lệ) + tái xác nhận: tín hiệu daily-bar đã yếu đi

Status: research + review. Trước khi implement, phát hiện đề xuất tự đưa ra
đầu round SAI về mặt kỹ thuật — dừng lại kịp thời, không lãng phí công
implement.

## Bối cảnh: "open lead" từ thread nghiên cứu trước

`finance-mw/raw/portfolio-btc-optimization-log.md` (2026-08-20T09:15Z, thread
trước chương trình `/loop` Round 1-70 hiện tại) ghi nhận: `stochastic_14_3_30_70`
và `rsi_mean_reversion_9_30_70` trên khung `1d` có win rate nhất quán
(66.1%→69.6%→71.4% và 63.4%→60.0%→66.7%) qua 3 split — tín hiệu thật, không
phải may rủi. Nhưng `--daily-profit-gate` fail vì
`cost_to_gross_pnl_ratio=1.15` (chi phí giao dịch VƯỢT QUÁ tổng lợi nhuận
gross) — do tần suất quá thấp (~21 trade/năm ở $5 fixed notional) khiến chi
phí cố định ăn hết edge. Log kết luận: "cần size lớn hơn để pha loãng chi
phí cố định mỗi trade" — được ghi là "hướng mở đáng chú ý nhất cho tương
lai".

## Định implement: tăng position size để "pha loãng" chi phí — SAI, dừng lại kịp thời

Trước khi code, đọc lại kỹ cấu trúc chi phí trong `finance-research/src/main.rs`:
`fee_bps`, `slippage_bps`, `funding_rate_bps` — **toàn bộ đều tính theo basis
point (tỷ lệ %), không phải USD cố định mỗi trade.** `SIMULATION_FEE_BPS=5.0`
nghĩa là phí = 0.05% GIÁ TRỊ LỆNH, không phải $5 mỗi lệnh.

**Hệ quả: tăng position size KHÔNG giúp gì cho `cost_to_gross_pnl_ratio`.**
Tỷ lệ chi phí/lợi nhuận là scale-invariant khi cả 2 đều tỷ lệ thuận với kích
thước lệnh — nhân đôi size thì cả gross profit lẫn cost đều nhân đôi, tỷ lệ
giữa chúng giữ nguyên. Đây là chi phí TỶ LỆ (%), không phải chi phí CỐ ĐỊNH
(USD/trade) — chỉ chi phí cố định mới được "pha loãng" bằng size lớn hơn.
Đề xuất gốc của thread trước đã hiểu nhầm bản chất vấn đề. **Không có cách
sửa bằng sizing** — cần edge/trade (tính theo %) lớn hơn chi phí %, hoặc
giảm chi phí % (ngoài tầm kiểm soát, phản ánh phí sàn thật), không phải
"trade lớn hơn".

## Tái xác nhận tín hiệu daily-bar bằng dữ liệu mới — đã yếu đi, không còn PF>1 rõ ràng

Chạy lại đúng 2 candidate trên (BTC/binance, `--interval 1d --days 1825`,
qua Docker `--cpus=2`):

| Strategy | Split | Trades | Win rate | PF |
|---|---|---|---|---|
| `rsi_mean_reversion_9_30_70` | Train | 41 | 63.4% | **0.651** |
| | Validation | 15 | 60.0% | **0.412** |
| | Holdout | 21 | 66.7% | 1.249 |
| `stochastic_14_3_30_70` | Train | 62 | 66.1% | 0.840 |
| | Validation | 23 | 69.6% | 0.997 |
| | Holdout | 21 | 71.4% | 0.990 |

**Win rate khớp gần như y hệt log gốc** (66.1/69.6/71.4 cho stochastic —
xác nhận dữ liệu nhất quán, không phải lỗi đọc dữ liệu khác nguồn), nhưng
**PF giờ dao động quanh 0.84-1.25, không còn rõ ràng PF>1 nhất quán** như ấn
tượng ban đầu. `rsi_mean_reversion_9_30_70` còn có validation PF=0.412 (thua
lỗ rõ). Đây gần như breakeven ở mức tốt nhất, không phải "tín hiệu thật rõ
ràng, chỉ vướng chi phí" như log trước mô tả — có thể do regime thị trường
đã dịch chuyển kể từ lúc log gốc ghi nhận (2026-08-20), hoặc window 5 năm
trượt đã đổi thành phần dữ liệu đủ để lộ ra bản chất cận-biên của tín hiệu
này.

## Kết luận: đóng cả hướng "tăng size" lẫn hạ thấp độ tin cậy vào tín hiệu daily-bar

1. **Đóng hẳn hướng "tăng position size để cứu daily-bar signal"** — sai về
   bản chất kỹ thuật (chi phí tỷ lệ, không phải cố định), không đáng thử.
2. **Tín hiệu daily-bar tự nó cũng yếu hơn đánh giá trước** — PF cận biên
   (0.84-1.25), không đủ mạnh để ưu tiên đầu tư thêm công sức (ví dụ thử
   thêm bộ lọc, hay tăng độ chọn lọc entry) trừ khi có bằng chứng mới mạnh
   hơn. Hạ độ ưu tiên của hướng này trong backlog.

## Không log task mới cho Codex

Đây là 1 correction + tái xác nhận, không có action item cụ thể — chỉ giúp
tránh lãng phí công sức implement 1 hướng sai ở round sau.
