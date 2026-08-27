# Round 72 (2026-08-21) — Implement + backtest + đóng candidate mới: order-flow imbalance (taker buy/sell)

Status: dev + research, vai trò researcher+dev+reviewer (Codex vẫn hết
quota). Khai thác 1 chiều dữ liệu chưa từng được dùng trong toàn bộ hệ
thống.

## Phát hiện: dữ liệu order-flow thật đã có sẵn nhưng chưa ai dùng

`Kline` struct có sẵn `taker_buy_volume`/`taker_buy_quote_volume` (khối
lượng mua chủ động trong nến, so với tổng `volume`) — dữ liệu order-flow
thật từ Binance, đã có mặt trên MỌI nến mà toàn bộ chương trình từng nạp,
nhưng **grep xác nhận: không có strategy nào trong `finance-strategy` từng
đọc field này** — chỉ xuất hiện trong test fixture (dữ liệu giả để test).
Đây là 1 chiều tín hiệu genuinely khác (thành phần khối lượng trong nến, không
phải giá hay lịch sử giá) — khái niệm CVD (Cumulative Volume Delta) là kỹ
thuật order-flow phổ biến trong crypto futures, chưa từng thử trong chương
trình này.

## Implement

- `TakerImbalanceStrategy`: theo hướng lệch mua/bán (buy_ratio ≥ threshold →
  Long, ≤ 1-threshold → Short). 3 ngưỡng: 0.55/0.60/0.70.
- `TakerImbalanceFadeStrategy`: hướng ngược lại (fade — coi lệch 1 chiều
  cực đoan là dấu hiệu hấp thụ/kiệt sức sắp đảo chiều, không phải tiếp
  diễn). 2 ngưỡng: 0.55/0.60.
- Cả 2 đặt trong `finance-research/src/strategies.rs` (research-only, đúng
  convention), không đụng `StrategyKind`/production.

## Backtest (5 năm, BTC + XAU trên Binance)

| Strategy | Instrument | Trades (train) | Win rate | PF |
|---|---|---|---|---|
| `taker_imbalance_0_60` | BTC | 58,782 | 16.6-17.9% | 0.245-0.286 |
| `taker_imbalance_fade_0_60` | BTC | 58,782 | 20.0-24.5% | 0.196-0.27 |
| `taker_imbalance_0_60` | XAU | 10,274 | 7.6-8.3% | 0.091-0.096 |
| `taker_imbalance_fade_0_60` | XAU | 10,274 | 6.1-8.5% | 0.051-0.109 |

**Cả 2 hướng đều thua lỗ nặng, nhất quán mọi split, mọi ngưỡng, cả 2
instrument.** Điểm đáng chú ý: nếu đây chỉ đơn giản là "chọn sai hướng",
đảo ngược (fade) phải cho win rate ≈ 100% - win rate gốc (cùng 1 tập nến,
cùng entry point, chỉ khác hướng) — nhưng thực tế fade CŨNG có win rate thấp
tương tự (không bù trừ cho nhau). Điều này cho thấy: ở tần suất cực cao
(58k-102k trade/5 năm chỉ với 1 ngưỡng), tỷ lệ mua/bán trong nến chủ yếu là
NHIỄU, cả 2 hướng đều bị chi phí giao dịch bào mòn do whipsaw, không phải 1
edge một chiều thật sự.

## Kết luận: đóng candidate

Khớp đúng kết luận xuyên suốt chương trình (Round 33): tín hiệu thô không
có trend filter thì không có edge ở 5m. Chưa thử biến thể có trend filter
(kết hợp order-flow imbalance với higher-timeframe trend, giống kiến trúc
MTF đã validate) — đây là hướng tự nhiên nếu muốn quay lại chiều dữ liệu
này trong tương lai, nhưng round này dừng ở kết luận: **plain order-flow
imbalance không có edge, đóng candidate.**

## Đã làm (không chỉ đề xuất)

- Build + test qua Docker (`--cpus=3`): `cargo test --workspace --exclude
  finance-redis` 32/32 pass, `cargo fmt --check` sạch.
- Backtest thật qua `finance-research-local` Docker (`--cpus=2`), 5 năm, cả
  BTC lẫn XAU/binance.
- Cập nhật comment code phản ánh đúng kết quả đóng candidate.
- Commit `983ea1c`, push, CI đang chạy (research-tool-only, tương tự Round
  70 — có thể vẫn kích hoạt deploy vì thay đổi nằm trong crate được
  `finance-api` phụ thuộc).

## Không log task cho Codex

Kết quả phủ định tự đóng ngay trong round — không có action item.
