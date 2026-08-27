# Round 101 (2026-08-23) — Thử `--alpha-stop-value`/`--alpha-take-value` cho 3 candidate mới (Donchian/Keltner/Heikin-Ashi) — không tìm được lever, mở rộng kết luận đã đóng Round 25/59

Status: research only, không đổi code (chỉ dùng flag CLI có sẵn).

## Bối cảnh

Toàn bộ candidate mới trong phiên này (Round 88/91/93 — Donchian, Keltner
reversion, Heikin-Ashi) được sweep test với "raw, signal-only-exit
semantics" MẶC ĐỊNH của `finance-research` — tức là KHÔNG có protective
stop/take ở tầng Alpha, chỉ thoát khi tín hiệu chính chiến lược đảo chiều.
Cờ `--alpha-stop-value`/`--alpha-take-value` từng test cho `candle_momentum`/
`rsi_mean_reversion` (Round 25, 59 — "bất biến/xấu đi", đóng) nhưng CHƯA
từng thử cho 3 candidate mới này. Với cơ chế khác hẳn (breakout/reversion/
smoothed-momentum, không phải momentum/mean-reversion thuần), có khả năng
protective stop giúp cắt lỗ sớm khác đi so với production strategies.

## Kết quả — BTC 2 broker, 5 năm, so với baseline không stop/take

| Candidate | Baseline holdout (binance/exness) | Với stop=0.01/take=0.02 holdout (binance/exness) |
|---|---|---|
| donchian_breakout_200 | 0.82 / 0.81 | **0.86 / 0.85** (cải thiện nhẹ) |
| keltner_reversion_20_2_5 | 0.73 / 0.78 | 0.70 / 0.75 (tệ hơn nhẹ) |
| heikin_ashi_momentum_10 | 0.71 / 0.65 | 0.67 / 0.67 (gần như trung tính, trái chiều nhẹ giữa 2 broker) |

Tần suất tăng mạnh khi có stop/take (Keltner: 2532→4605 trade train ở
binance) vì mỗi lệnh giờ thoát sớm qua stop/take thay vì chờ tín hiệu đảo
chiều — hợp lý, nhưng không đổi kết luận vì PF vẫn <1 mọi trường hợp.

## Kết luận

**Không tìm được lever nào có ý nghĩa** — hiệu ứng nhỏ, trái chiều giữa các
candidate, khác hẳn hiệu ứng mạnh và nhất quán của stop/take-width ở
PORTFOLIO layer (Round 83, giảm 32-41% lỗ). Điều này khớp và MỞ RỘNG kết
luận đã đóng ở Round 25/59 (Alpha-level stop/take cho candle_momentum/
rsi_mean_reversion cũng "bất biến/xấu đi") sang 3 cơ chế Alpha hoàn toàn
khác — củng cố thêm bằng chứng rằng đòn bẩy stop/take THẬT chỉ nằm ở tầng
Portfolio-construction (áp dụng sau khi đã tổng hợp nhiều Alpha), không phải
tầng Alpha riêng lẻ.

## Việc cho Codex / round sau

- **[trading][low]** Không có action item. Có thể cập nhật bảng đóng trong
  `SUMMARY-priority-backlog.md` để ghi rõ "Alpha-level stop/take tuning" giờ
  đã test cả 5 cơ chế (2 cũ + 3 mới), không chỉ 2 production strategies.
