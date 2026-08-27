# Round 98 (2026-08-23) — Hoàn thiện ablation không chi phí cho XAU (Round 96 chỉ mới BTC), cùng hướng nhưng kém tin cậy hơn do chất lượng dữ liệu XAU đã biết

Status: research only. Nối tiếp trực tiếp Round 96 — comment permanent Codex
đã ghi rõ ablation trước "BTC-only", round này lấp nốt XAU cho đủ 4 route.

## Kết quả — XAU, `--fee-bps 0 --slippage-bps 0`, so với baseline có phí (Round 88/91/93)

| Candidate | Route | Có phí (holdout) | Không phí (holdout) |
|---|---|---|---|
| donchian_breakout_200 | XAU/binance | 0.76 | 1.03 |
| donchian_breakout_200 | XAU/exness | 0.92 | 1.36 |
| keltner_reversion_20_2_5 | XAU/binance | 0.42 | 1.08 |
| keltner_reversion_20_2_5 | XAU/exness | 0.69 | 0.80 |
| heikin_ashi_momentum_10 | XAU/binance | 0.33 | 0.74 |
| heikin_ashi_momentum_10 | XAU/exness | 0.72 | 1.10 |

## Phân tích — cùng hướng như BTC nhưng biến động mạnh hơn nhiều, không nên tin bằng BTC

Mọi ô đều tăng đáng kể khi bỏ chi phí (khớp hướng phát hiện Round 96), một
số ô còn vượt hẳn 1 (donchian XAU/exness 1.36, keltner XAU/binance 1.08,
heikin_ashi XAU/exness 1.10) — nhưng **KHÔNG nên diễn giải các con số >1 này
là "candidate profitable"**, vì 2 lý do đã biết rõ và nhắc lại nhiều lần
trong chương trình:

1. **XAU/binance mẫu quá mỏng** (chỉ ~85 ngày lịch sử, holdout 36-185 trade
   tuỳ candidate — dưới ngưỡng tin cậy ~20-30 trade cho vài ô, thừa cho vài
   ô khác nhưng vẫn là 1 window rất ngắn).
2. **XAU/exness có continuity gap chưa verify** (đã ghi trong permanent
   comment của Round 88/91/93) — số liệu có thể bị nhiễu bởi dữ liệu thiếu/
   sai lệch, không phải edge thật.

Biên độ dao động giữa 2 broker cũng lớn hơn nhiều so với BTC (vd
keltner_reversion: XAU/binance không-phí 1.08 nhưng XAU/exness chỉ 0.80 —
cách nhau 0.28, trong khi BTC 2 broker luôn khớp nhau trong khoảng 0.05) —
tự nó là bằng chứng cho thấy tín hiệu XAU nhiễu hơn, kém đáng tin hơn BTC,
đúng như pattern đã thấy xuyên suốt 98 round.

## Kết luận

**Không thay đổi kết luận CLOSED của Round 88/91/93/96** — hướng dữ liệu
XAU xác nhận cùng chiều (chi phí là nguyên nhân chính) nhưng không đủ tin
cậy để nâng bất kỳ candidate nào lên "promotable", đặc biệt vì bản thân dữ
liệu XAU có vấn đề chất lượng đã biết trước khi tính tới cost ablation.
Hoàn thiện bức tranh 4-route cho đầy đủ hồ sơ nghiên cứu, không có action
item mới.

## Việc cho Codex

- **[trading][low]** Không cấp bách. Có thể bổ sung số liệu XAU này vào
  permanent comment nếu muốn hồ sơ đầy đủ 4-route thay vì chỉ BTC, nhưng
  không bắt buộc vì kết luận không đổi.
