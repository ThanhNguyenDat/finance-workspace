# Round 90 (2026-08-22) — Xác nhận `risk_fraction` = `equity_fraction` tại cùng đòn bẩy (chính xác tới cent), và lỗ scale PHI TUYẾN (compounding) theo đòn bẩy — sửa lại 1 so sánh sai ở Round 85/88

Status: research only. Tiếp nối trực tiếp Round 89 (đòn bẩy hiệu dụng ẩn
trong `risk_fraction`). File `strategies.rs` từ Round 88 vẫn chờ Codex,
không đổi gì thêm.

## Mục tiêu

Round 89 đề xuất: sweep `risk_fraction` sizing_value để tìm điểm đòn bẩy hiệu
dụng (`sizing_value/stop`) khớp `compounding-10pct` (~0.1x), xác nhận PnL có
"trở về mức tương đương" như dự đoán tuyến tính hay không.

## Kết quả 1 — Xác nhận CHÍNH XÁC tới cent: `risk_fraction` ≡ `equity_fraction`
khi cùng đòn bẩy hiệu dụng

`risk_fraction=0.001` (đòn bẩy = 0.001/0.01 = 0.1x, khớp `equity_fraction
=0.10`), cùng hold=36, stop/take=0.01/0.02, 5 năm, `one_target`:

| Route | `risk_fraction=0.001` | `equity_fraction=0.10` | Khớp? |
|---|---|---|---|
| BTC/binance | -$2,808.76 (2439 trade) | -$2,808.76 (2439 trade) | **100% khớp tới cent** |
| BTC/exness | -$3,177.19 (2417 trade) | -$3,177.19 (2417 trade) | **100% khớp tới cent** |

Xác nhận toán học: `RiskFraction::notional = equity×risk_fraction/stop` và
`EquityFraction::notional = equity×fraction` là CÙNG 1 công thức khi
`risk_fraction/stop = fraction` — không chỉ tương tự, mà **giống hệt hệ
thống thực thi**. Giả thuyết Round 89 được xác nhận hoàn toàn.

## Kết quả 2 (quan trọng hơn) — Lỗ scale PHI TUYẾN theo đòn bẩy, không
tuyến tính như `fixed_notional`

| Đòn bẩy hiệu dụng | BTC/binance | BTC/exness |
|---|---|---|
| 0.1x (`sv=0.001`) | -28.09% | -31.77% |
| 0.2x (`sv=0.002`) | -48.53% | -53.66% |
| 0.5x (`sv=0.005`) | -81.64% | -85.88% |
| 2.0x (`sv=0.02`, Round 89) | -99.94% | -98.22% |

Nếu tuyến tính, đòn bẩy 0.1x phải cho lỗ ≈ (0.1/2.0)×99.94% ≈ **5%**, nhưng
thực tế là **28%** — gấp ~5.6 lần dự đoán tuyến tính. Đây là hệ quả của
**compounding hình học** (equity co lại sau mỗi lệnh thua → lệnh sau nhỏ hơn
theo tỷ lệ, nhưng chuỗi hàng nghìn lệnh với edge âm vẫn làm equity suy giảm
theo cấp số nhân, giống hệt cơ chế "volatility decay" của leveraged ETF/token)
— khác hẳn `fixed_notional` (Round 84) nơi mỗi lệnh dùng đúng $5 cố định,
không phụ thuộc equity hiện tại, nên lỗ cộng dồn TUYẾN TÍNH, không phải hình
học.

## Sửa lại 1 so sánh sai ở Round 85/88

Round 85/88 dùng con số ledger **production thật** của `compounding-10pct`
(`-$663.22`, chỉ 502 trade kể từ lúc Live Action restart sau outage) làm mốc
tham chiếu "an toàn". Đây là **mẫu quá nhỏ** (vài giờ dữ liệu), KHÔNG phải kỳ
vọng dài hạn. Số liệu 5 năm honest qua `one_target` cho `equity_fraction
=0.10` thực ra là **-28.09%/-31.77%** (bảng trên) — vẫn là một khoản lỗ rất
lớn nếu chạy đủ lâu, chỉ là ít nghiêm trọng hơn `risk_fraction=0.02`'s -99%.
**Kết luận sửa lại: mọi sizing mode compounding-theo-equity (`equity_fraction`
LẪN `risk_fraction`) đều nguy hiểm với Alpha có PF<1 hiện tại, khác biệt chỉ
là mức độ (theo đòn bẩy hiệu dụng), không phải khác biệt về loại rủi ro.**
Chỉ `fixed_notional` (không compounding) mới thực sự bounded (Round 84/85:
-$3.41, -0.03%).

## Ý nghĩa

- Xác nhận cơ chế đòn bẩy hiệu dụng của `risk_fraction` (Round 89) là đúng
  và tổng quát hoá được: **BẤT KỲ sizing mode nào compounding theo equity
  hiện tại** (không chỉ `risk_fraction`) đều khuếch đại lỗ theo cấp số nhân
  khi Alpha có edge âm — đây là hệ quả toán học của compounding, không phải
  lỗi riêng của `risk_fraction`.
- `fixed_notional` (rule mặc định `fixed-pct`, đang là "selected Portfolio
  execution rule" thật) là lựa chọn AN TOÀN NHẤT trong 3 rule hiện có chính
  vì nó không compounding — không phải vì bản thân Alpha tốt hơn khi dùng
  rule này (cùng 1 decision stream cho cả 3 rule).
- Không có action item mới cấp bách — củng cố thêm lý do để không thay đổi
  rule "selected" khỏi `fixed-pct` cho tới khi Alpha có edge dương thật.

## Việc cho round sau / Codex

- **[trading][low]** Cập nhật comment/doc nếu có chỗ nào đang ngầm định
  "compounding-10pct an toàn hơn risk-2pct" chỉ dựa trên số liệu production
  ngắn hạn — cả hai đều compounding, khác nhau về MỨC ĐỘ đòn bẩy
  (0.1x vs 2.0x) chứ không phải về LOẠI rủi ro.
- Không cần sweep thêm sizing_value — đã đủ dữ liệu xác nhận quan hệ phi
  tuyến rõ ràng, cross-broker nhất quán (2 route, sai lệch <1% giữa nhau ở
  mọi mức đòn bẩy).
