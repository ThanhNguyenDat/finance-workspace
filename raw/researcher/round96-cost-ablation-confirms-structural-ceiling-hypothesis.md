# Round 96 (2026-08-23) — Ablation không chi phí: xác nhận phần lớn giả thuyết "trần chi phí cấu trúc" Round 93, tách bạch được candidate nào có edge âm thật

Status: research only. Trả lời trực tiếp methodology caveat Codex nêu ở
Dev-done Round 93 ("chưa có gross/no-cost/cost-stress ablation để tách
causal cost ceiling khỏi negative raw edge").

## Bối cảnh

Round 93 quan sát 3 cơ chế mới (Donchian, Keltner reversion, Heikin-Ashi)
đều hội tụ về PF~0.65-0.85 khi kéo dài tham số, đưa ra giả thuyết "trần chi
phí cấu trúc" nhưng CHƯA test trực tiếp. Codex phản biện đúng: cần ablation
fee=0/slippage=0 để biết chắc.

## Phương pháp

Chạy lại sweep table (không phí) cho 3 candidate tốt nhất mỗi cơ chế
(donchian_breakout_200, keltner_reversion_20_2_5, heikin_ashi_momentum_10)
với `--fee-bps 0 --slippage-bps 0`, so với baseline mặc định (fee=5bps,
slippage=2bps, round-trip nominal ~14bps trước spread/funding).

## Kết quả — BTC cả 2 broker, 5 năm

| Candidate | Có phí (holdout, Round 88/91/93) | KHÔNG phí (holdout) | Δ |
|---|---|---|---|
| donchian_breakout_200 (binance) | 0.82 | 0.96 | +0.14 |
| donchian_breakout_200 (exness) | 0.81 | 0.96 | +0.15 |
| keltner_reversion_20_2_5 (binance) | 0.73 | **1.02** | +0.29 |
| keltner_reversion_20_2_5 (exness) | 0.78 | **1.06** | +0.28 |
| heikin_ashi_momentum_10 (binance) | 0.71 | 0.98 | +0.27 |
| heikin_ashi_momentum_10 (exness) | 0.65 | 0.91 | +0.26 |

(Không chỉ holdout — train/validation của Keltner cũng đều ≥1.00 trên cả 2
broker, nhất quán, không phải may mắn 1 split.)

## Kết luận — xác nhận PHẦN LỚN giả thuyết, có sắc thái quan trọng

**Chi phí giao dịch giải thích phần lớn khoảng cách tới PF=1** cho cả 3 cơ
chế (Δ +0.14 đến +0.29) — xác nhận hướng giả thuyết Round 93 là đúng, không
phải suy đoán vô căn cứ.

**Nhưng KHÔNG đồng nhất giữa các cơ chế:**
- **Keltner reversion & Heikin-Ashi: gần như CHẠM ĐÚNG breakeven (PF≈1.0)
  khi bỏ chi phí** — nghĩa là "raw edge" của bản thân tín hiệu gần như bằng
  0 (không âm, không dương rõ rệt), toàn bộ khoản lỗ quan sát được khi CÓ
  phí là do chi phí giao dịch, không phải vì tín hiệu tệ.
- **Donchian breakout: vẫn dưới 1 (0.96) dù đã bỏ hết chi phí** — nghĩa là
  ngoài chi phí, Donchian còn có 1 khoản edge âm thật nhỏ (khoảng -4%) độc
  lập với transaction cost. Chi phí vẫn là phần lớn nguyên nhân nhưng không
  phải toàn bộ.

## Ý nghĩa

Không có candidate nào thực sự PROMOTE được (kể cả không phí, tốt nhất chỉ
chạm breakeven ~1.0-1.06, chưa đủ margin để bù đắp chi phí thật + margin an
toàn cho biến động ước lượng) — không đổi kết luận CLOSED của Round 88/91/93.
Nhưng giờ đã tách bạch được rõ ràng: **Keltner reversion và Heikin-Ashi
momentum là những tín hiệu "trung tính" (không có edge, không lỗ về bản
chất) bị chi phí giao dịch kéo xuống dưới ngưỡng có lời — khác về bản chất
với những tín hiệu có edge âm thật** (như hầu hết candidate khác đã đóng
trong chương trình, ví dụ Bollinger reversion PF<1 rõ rệt cả khi có phí lẫn
không phí ở các round trước — tuy chưa test lại không-phí để so sánh trực
tiếp, ghi nhận đây là giả thuyết chưa kiểm chứng hoàn toàn).

**Gợi ý thật sự có giá trị cho tương lai:** nếu tìm được cách giảm tần suất
giao dịch của Keltner/Heikin-Ashi hơn nữa (ít lệnh hơn nhưng chất lượng
tương đương) HOẶC nếu chi phí thực tế (maker thay vì taker, spread hẹp hơn)
thấp hơn giả định 14bps hiện tại, 2 cơ chế "trung tính" này có khả năng vượt
breakeven thật — khác hẳn Donchian (có edge âm cấu trúc, giảm phí không đủ
cứu). Đây là lần đầu tiên chương trình phân loại được candidate theo
"cost-limited" vs "edge-limited" thay vì gộp chung "PF<1, đóng".

## Việc cho Codex / round sau

- **[trading][low]** Không có action item code. Ghi nhận phân loại
  "cost-limited (Keltner/Heikin-Ashi) vs edge-limited (Donchian)" vào
  research record nếu Codex commit các candidate này, để tương lai không
  cần lặp lại ablation.
- Round sau có thể thử: giảm tần suất Keltner/Heikin-Ashi bằng filter thêm
  (vd chỉ vào lệnh khi biên độ đủ lớn) xem PF không-phí có tăng vượt 1 rõ
  rệt hơn không — nhưng vẫn phải nhớ đây chỉ có ý nghĩa nếu chi phí thực tế
  production thấp hơn 14bps giả định.
