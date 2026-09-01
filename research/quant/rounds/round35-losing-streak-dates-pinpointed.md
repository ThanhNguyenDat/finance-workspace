# Round 35 (2026-08-20) — Xác định chính xác ngày tháng của chuỗi lỗ 48 ngày chặn candidate tốt nhất

Status: research-only, phân tích số liệu thật từ `daily_results`, không
backtest candidate mới. Mục tiêu: biến "candidate tốt nhất (Round 17) có
streak 48 ngày, vượt ngưỡng 5" từ 1 con số trừu tượng thành 1 case study cụ
thể có ngày tháng thật, để bất kỳ ai thiết kế regime-filter sau này có dữ
liệu cụ thể để test thay vì đoán mò.

## Phát hiện: chuỗi lỗ 48 ngày là **2026-04-12 → 2026-05-29**

Trích xuất trực tiếp từ mảng `daily_results` thật của gate
`mtf_stochastic_14_3_30_70_sma50_trend_filtered` (BTC/binance, 4h/1d).
**Xác nhận cross-broker** (đúng phương pháp Round 16): chạy lại đúng
candidate trên **Exness BTC/USD** (nguồn giá độc lập hoàn toàn) cho đúng
cửa sổ ngày này — **48/48 ngày cũng âm, PnL tổng -0.41**, khớp chính xác
với Binance. Đây là bằng chứng mạnh: chuỗi lỗ này là 1 sự kiện thị trường
BTC thật (giá đi ngang/nhiễu kéo dài khiến trend filter liên tục sai hướng),
không phải artifact riêng của 1 nguồn dữ liệu.

## Vì sao đáng lưu lại

Round 17-19 đã biết "streak 48 ngày là vấn đề chặn Target 3", nhưng chưa ai
biết CHÍNH XÁC khi nào streak đó xảy ra để điều tra sâu hơn cơ chế (BTC lúc
đó có đang sideway mạnh? Volatility có giảm bất thường không? ADX lúc đó có
thấp không — nếu có thì đây chính là bằng chứng cụ thể ủng hộ hướng regime-
filter mà Round 24 đã test (ADX-filtered variant) nhưng KHÔNG dùng đúng cửa
sổ này để kiểm chứng trực tiếp). Có ngày tháng cụ thể giúp:

1. Nếu sau này implement bất kỳ regime-filter mới nào (ADX, volatility,
   choppiness index...), có thể kiểm tra CỤ THỂ filter đó có tránh được
   đúng 48 ngày này hay không, thay vì chỉ nhìn tổng thể "streak giảm hay
   không".
2. Round 24 đã test ADX-filtered variant NHƯNG trên toàn bộ 5 năm, không
   biết riêng cửa sổ 2026-04-12→05-29 có bị filter loại bỏ hay không — có
   thể tự tra cứu lại kết quả round 24 hoặc chạy lại có kiểm tra riêng cửa
   sổ này ở round sau nếu cần.

## Không phải action item mới, chỉ là dữ liệu tham chiếu

Không log task mới cho Codex — đây là dữ liệu bổ sung cho hồ sơ đã có (Round
17-19 P2 item về swing candidate). Nếu Codex/round sau quay lại thiết kế
regime-filter cho candidate này, nên tham chiếu case study cụ thể này thay
vì test mù trên toàn bộ lịch sử.
