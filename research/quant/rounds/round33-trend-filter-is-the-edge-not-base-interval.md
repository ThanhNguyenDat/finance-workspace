# Round 33 (2026-08-20) — Xác nhận: trend filter (1d agreement) MỚI là nguồn edge thật, không phải base interval

Status: research-only, production đã khôi phục hoàn toàn sau incident P0
(round 26-32) — quay lại trọng tâm nghiên cứu chiến thuật. Không log thêm
gì mới về incident round này (đã đóng, xem `docs/archive/legacy-handoff-agent.md`).

## Test: candidate PLAIN (không MTF, không trend filter) ở đúng các base
interval đã biết có edge khi CÓ trend filter

Round 17 tìm ra: `mtf_stochastic_14_3_30_70_sma50_trend_filtered` (base 4h +
higher-tf 1d) là candidate tốt nhất chương trình. Round 19/24 test thêm base
5m/1h cùng trend filter — đều tệ hơn 4h nhưng vẫn CÓ trend filter. Round này
test câu hỏi chưa ai hỏi: **nếu bỏ hẳn trend filter, chỉ dùng plain
stochastic/momentum/rsi/macd/bollinger ở đúng base interval 1h hoặc 4h
(không MTF), có candidate nào PF>1 nhất quán cả 3 split không?**

| Instrument | Interval | Số candidate PF>1 nhất quán cả 3 split (plain, không MTF) |
|---|---|---|
| BTC/binance | 4h | **0** |
| BTC/binance | 1h | **0** |
| XAU/exness | 4h | **0** |

**Cả 3 test đều ZERO candidate.** So sánh trực tiếp: cùng base interval 4h,
BTC/binance có **4 candidate** PF>1 nhất quán khi CÓ trend filter (Round 17-
18: sma50-stochastic, candle_momentum-sma10, macd-sma10, adx-stochastic) —
nhưng **0 candidate** khi bỏ trend filter dù giữ nguyên mọi tham số khác của
inner strategy.

## Kết luận mechanistic rõ ràng

**Trend filter (đồng thuận hướng với SMA của nến higher-timeframe) không
phải phụ kiện giảm nhiễu — nó CHÍNH LÀ nguồn edge.** Bản thân oscillator
(stochastic/momentum/rsi/macd/bollinger) ở base interval 1h/4h/5m đều KHÔNG
có edge độc lập — chỉ khi kết hợp với điều kiện đồng thuận trend cao hơn thì
mới sinh ra PF>1 nhất quán. Điều này giải thích lại chính xác vì sao mọi nỗ
lực Round 19/24 "đổi base interval để tăng tần suất" đều thất bại: đổi base
interval không đổi được bản chất "trend filter cung cấp toàn bộ edge, oscillator
chỉ cung cấp thời điểm entry cụ thể trong lúc trend đã đồng thuận" — tần suất
bị giới hạn bởi tần suất thay đổi hướng trend 1d (tối đa vài lần/tháng thực
tế), không phải bởi base interval.

## Ý nghĩa thực dụng cho hướng tìm kiếm tiếp theo

Xác nhận thêm 1 lần nữa (không phải giả thuyết): **bất kỳ candidate mới nào
muốn có tần suất cao HƠN family MTF trend-filtered này, bắt buộc phải KHÔNG
dựa vào cơ chế "chờ trend 1d đồng thuận"** — đây chính là lý do đề xuất
Funding Rate (Round 22, dùng thông tin vị thế/leverage thay vì giá) và ORB
London-session (Round 18, dùng cấu trúc phiên thay vì trend dài hạn) vẫn là
2 hướng hợp lý nhất còn mở — cả 2 đều KHÔNG phụ thuộc cơ chế "chờ trend 1d"
đã chứng minh là trần tần suất cứng của mọi candidate momentum/oscillator
thuần tuý test được tới giờ.

## Không có action item mới cho Codex

Đây là củng cố hiểu biết (không phải bug, không phải candidate mới) — không
log thêm gì vào `docs/archive/legacy-handoff-agent.md` round này, chỉ lưu lại làm bằng chứng
tránh lặp lại hướng "thử oscillator plain ở base interval khác" trong tương
lai (đã đủ dữ liệu kết luận, không cần thử thêm interval khác cho hướng
plain-no-filter này).
