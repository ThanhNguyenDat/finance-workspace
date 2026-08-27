# Round 27 (2026-08-20) — Nghiên cứu ICT liquidity-sweep/FVG: KHÔNG đề xuất implement lúc này

Status: research (WebSearch), không backtest được round này vì pipeline
production đang bị chặn bởi sự cố Postgres P0 (xem mục cùng ngày trong
`raw/handoff_codex.md` — `finance-research` tự test fail đúng lỗi
`pq: password authentication failed`, không load được nến nào). Dùng thời
gian này tra cứu sâu hơn 1 ý tưởng đã flag từ đầu chương trình research
(handoff Todo cũ: "ICT-style liquidity-sweep + FVG entry... cần code mới
thật sự để test") nhưng chưa ai backtest hay research kỹ.

## Phát hiện quan trọng nhất: bằng chứng học thuật thật về lookahead bias

Tìm được 1 nghiên cứu thực nghiệm nghiêm túc (backtest FVG trên 4 thị
trường futures, khung 5m/15m/1h, so sánh reaction rate với random baseline):
kết luận "the reaction is real; the tradeable edge is not". Chi tiết quan
trọng nhất:

> **Khi trade được resolve bằng data 1 phút (đúng thứ tự trader thật sự
> trải nghiệm), win rate giảm từ ~73% xuống ~50% — TOÀN BỘ edge có vẻ tồn
> tại hoá ra là do intrabar lookahead bias** (backtest trên nến thô 5m/15m
> "nhìn thấy" cả nến đóng trước khi biết giá thật sự di chuyển ra sao bên
> trong nến đó, tạo ảo giác về entry/exit hoàn hảo mà trader thật không thể
> đạt được).

**Đây CHÍNH XÁC cùng loại lỗi đã tìm thấy và fix trong chương trình research
này** (lookahead bug trong MTF kline merge, khiến win rate báo sai 69-97%
trước khi corrected xuống 27-30% thật — xem CSV log dòng 4-9). Không phải
trùng hợp — FVG/ICT theo bản chất dễ mắc loại lỗi này hơn hẳn các strategy
khác đã test (momentum/RSI/stochastic) vì cơ chế của nó phụ thuộc trực tiếp
vào "khoảng trống giá" hình thành TRONG 1 nến — backtest ở granularity thô
hơn granularity thật trader trải nghiệm gần như chắc chắn lộ thông tin
tương lai.

Nguồn: [FVG Strategies and Backtesting - forextester](https://forextester.com/blog/fair-value-gap/),
[Advanced FVG Strategy - Medium/FMZQuant](https://medium.com/@FMZQuant/advanced-fair-value-gap-strategy-quantitative-algorithm-for-micro-imbalance-capture-3a82e0c3332c),
[Liquidity Sweep ICT Guide - phidiaspropfirm](https://phidiaspropfirm.com/education/liquidity-sweep),
[ICT Trading 2026 - forextester](https://forextester.com/blog/ict-trading/).

## Kết nối với 1 hạn chế hạ tầng đã biết — không phải phát hiện mới, nhưng giờ có lý do cụ thể hơn hẳn

Round 15 (session trước `/loop` này) đã phát hiện: `1m` kline chỉ lưu ~4.4
ngày thật (đủ cho chart, không đủ cho backtest walk-forward), logged là P3
"cần quyết định có mở rộng retention hay không". Lúc đó lý do là 1 ý tưởng
scalping RSI 1 phút chung chung. **Giờ có lý do cụ thể và mạnh hơn nhiều:**
nếu muốn test ICT/FVG đúng cách (theo đúng khuyến nghị của chính nghiên cứu
vừa tìm được — phải resolve ở granularity 1 phút mới biết edge có thật hay
chỉ là lookahead artifact), **bắt buộc cần retention 1m dài hơn hẳn 4.4
ngày** — không thể validate honest được nếu thiếu điều kiện hạ tầng này.

## Khuyến nghị: KHÔNG đề xuất Codex implement ICT/FVG lúc này

Khác với đề xuất Funding Rate (Round 22, vẫn khuyến nghị theo đuổi) — với
ICT/FVG, bằng chứng research cho thấy **rủi ro cao rằng bất kỳ kết quả nào
build được cũng sẽ mắc đúng loại lookahead-bias đã từng gây sai lệch nghiêm
trọng trong chương trình này**, trừ khi giải quyết được 2 điều kiện tiên
quyết: (1) mở rộng `1m` retention đủ dài để test honest walk-forward, (2)
implement rất cẩn thận theo đúng `NoLookaheadObservation` contract đã có
(`trading_modes.rs:564-566`) — resolve FVG timing dựa đúng closed-candle
tại granularity thật, không "nhìn" high/low của nến base interval thô hơn.
Không log task implement mới cho Codex — chỉ cập nhật lại đánh giá rủi ro
của ý tưởng cũ (đã có sẵn trong Todo lịch sử) để không ai vội implement mà
không biết rủi ro lookahead cụ thể này.

## Việc cần làm nếu ai muốn theo đuổi (không phải action item bắt buộc)

Nếu quyết định mở rộng `1m` retention vì lý do khác (round 15's P3 vẫn mở),
thì lúc đó backtest ICT/FVG mới có ý nghĩa — nên gộp 2 quyết định lại làm 1,
không mở rộng retention chỉ vì FVG khi chưa có nhu cầu khác cụ thể hơn.
