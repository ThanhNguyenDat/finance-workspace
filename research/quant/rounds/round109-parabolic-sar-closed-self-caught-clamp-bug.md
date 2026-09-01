# Round 109 (2026-08-23) — Parabolic SAR (mới hoàn toàn, cơ chế trailing-stop-and-reverse) — ĐÓNG, PF thấp nhất quán; tự bắt được bug clamp trong lúc implement

Status: research, thêm `ParabolicSarStrategy` (candidate mới hoàn toàn) vào
`finance-research/src/strategies.rs`. Chạy 4 route 5 năm, 2 cặp song song
(`--cpus=2 --memory=4g --memory-swap=6g`, đúng Rule 9).

## Bối cảnh

Đã xử lý 1 Verify item còn tồn (Round101 alpha-stop/take scope caveat —
Codex root-review đúng, đã sửa SUMMARY và chuyển Done, xem addendum trong
`handoff_agent.md`). Round102 XAU/Exness follow-up còn phải chờ market mở
cửa lại (22:00 UTC Chủ Nhật), chưa tới lúc. Sau khi cạn nhiều hướng
wrapper-trên-candidate-cũ, Round 109 chọn **Parabolic SAR (Wilder)** — cơ
chế trailing-stop-and-reverse, khác hẳn mọi channel/band/oscillator/cross
đã test (kể cả Ichimoku Round 108, vốn vẫn là dạng cross+filter).

## ⚠️ Tự bắt được bug trong lúc implement (trước khi backtest, không phải sau)

Bản đầu tiên clamp SAR dùng nhầm `kline.low`/`kline.high` của **chính nến
đang xét** trong công thức clamp (`candidate_sar.min(state.prev_low).min(kline.low)`),
khiến `sar_today` luôn ≤ `kline.low` (long) — điều kiện đảo chiều
`kline.low < sar_today` **không bao giờ đúng được về mặt toán học**. Backtest
đầu tiên trả 0 trade mọi split mọi route — phát hiện ngay từ số liệu bất
thường (0 trade suốt 5 năm là dấu hiệu rõ ràng của lỗi logic, không phải kết
quả thật), sửa lại clamp chỉ dùng `state.prev_low`/`state.prev_high` (dữ
liệu nến trước, không phải nến đang xét), build lại, backtest lại mới ra số
liệu thật. Ghi nhận minh bạch theo đúng kỷ luật chương trình (giống cách
Round 92 tự phát hiện lỗi tính tần suất).

## Kết quả — 5 năm, 3 split, cả 4 route (chi phí thật), tham số Wilder chuẩn (0.02/0.02/0.2)

| Route | train PF | valid PF | holdout PF | trades (holdout) |
|---|---|---|---|---|
| BTC/binance | 0.475 | 0.418 | 0.424 | 8991 |
| BTC/exness | 0.472 | 0.434 | 0.423 | 9204 |
| XAU/binance | 0.297 | 0.252 | 0.207 | 1232 |
| XAU/exness | 0.139 | 0.176 | 0.326 | 6528 |

**Toàn bộ 12 ô PF<0.5** — thấp và không có ô nào gần 1.0, nên **không cần
cross-check 18 tháng** (khác Round 106/108). BTC ở 2 broker cho số liệu gần
như trùng khớp (0.475/0.418/0.424 vs 0.472/0.434/0.423) — cross-broker nhất
quán rõ ràng dù kết quả xấu. Win rate thấp (12.7-24.8%) và tần suất tín hiệu
khá cao (SAR mặc định phản ứng nhanh với nhiễu trên 5m) — cùng failure mode
"win rate thấp" như phần lớn candidate breakout/momentum đã đóng trước đây
(khác Fibonacci Round 105 vốn có win rate cao nhưng R:R xấu).

## Kết luận — ĐÓNG

Không promote. Tham số Wilder mặc định (0.02/0.02/0.2) quá nhạy với nhiễu
5m, gây tần suất đảo chiều cao và PF thấp nhất quán mọi route. Không có
động lực thử sweep tham số AF khác (chậm hơn: af_start/increment nhỏ hơn)
trong round này — nếu muốn tiếp tục hướng SAR, nên bắt đầu bằng AF chậm hơn
đáng kể (vd 0.01/0.01/0.1) hoặc base interval dài hơn (giống cách
`ema_crossover_12_26` chỉ hoạt động tốt hơn ở 30m so với 5m).

## Việc cho Codex / round sau

- **[trading][low]** Không cấp bách. Có thể lưu `ParabolicSarStrategy` làm
  bản ghi closed-candidate (research-only), hoặc revert nếu không cần giữ.
