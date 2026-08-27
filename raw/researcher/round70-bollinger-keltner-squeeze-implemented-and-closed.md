# Round 70 (2026-08-21) — Implement + backtest + đóng candidate mới: Bollinger/Keltner volatility squeeze

Status: dev + research, vai trò researcher+dev+reviewer (Codex vẫn hết
quota). Lần đầu tiên trong chương trình này TỰ implement 1 cơ chế strategy
hoàn toàn mới (không chỉ tune tham số cái cũ), backtest, và đóng candidate
trong cùng 1 round.

## Ý tưởng: web research (Rule 2)

Search "Bollinger Band squeeze Keltner Channel volatility breakout crypto
backtest" — tìm được 1 cơ chế genuinely khác mọi thứ đã thử trong chương
trình (oscillator mean-reversion, MACD/momentum trend continuation, ATR
threshold breakout đơn giản): **volatility squeeze breakout** — vào lệnh khi
Bollinger Band co lại BÊN TRONG Keltner Channel (cả biến động thống kê lẫn
biến động thực đều nén cùng lúc) rồi "giải phóng" (band mở rộng ra ngoài
Keltner). Nguồn ngoài báo cáo Sharpe>1.0 trên BTC/USDT, nhưng khuyến nghị
khung thời gian 30m-1D, không phải 5m production của hệ thống này.

## Implement

- Thêm indicator `Keltner Channel` mới (`crates/finance-strategy/src/indicators/keltner.rs`,
  EMA midline ± multiplier×ATR) — dùng chung, tương tự cách Bollinger/ATR/EMA
  đã có sẵn.
- Thêm `BollingerKeltnerSqueezeStrategy` — theo đúng convention của file
  `finance-research/src/strategies.rs`: candidate CHƯA validate sống LOCAL
  trong file này (không đưa vào `finance-strategy` — crate đó chỉ chứa
  strategy đã được promote), không đụng `StrategyKind`/`deployment_rules.rs`.
- Ban đầu định nghĩa nhầm trong `finance-strategy` (crate dùng chung
  production) — nhận ra sai convention giữa chừng, sửa lại đúng chỗ trước
  khi commit (giữ Keltner Channel indicator ở finance-strategy vì đó là
  utility dùng chung, nhưng chuyển strategy struct về finance-research).
- 3 biến thể tham số: `20_2_0_1_5` (chuẩn textbook), `20_2_0_1_0` (Keltner
  nhạy hơn), `10_2_0_1_5` (period ngắn hơn, nhanh hơn nhưng nhiễu hơn).
- 9 unit test mới (indicator + strategy: không fire giữa squeeze, fire đúng
  1 lần tại candle giải phóng, đúng hướng theo thân nến, không chia sẻ state
  giữa các interval khác nhau).

## Backtest (5 năm, BTC + XAU trên Binance)

| Strategy | Instrument | Train PF | Validation PF | Holdout PF |
|---|---|---|---|---|
| `bollinger_keltner_squeeze_20_2_0_1_5` | BTC | 0.686 | 0.760 | 0.693 |
| `bollinger_keltner_squeeze_20_2_0_1_5` | XAU | 0.703 | 0.741 | 0.675 |
| `bollinger_keltner_squeeze_20_2_0_1_0` | BTC | 0.688 | 1.726 (39 trade) | 0.528 |
| `bollinger_keltner_squeeze_10_2_0_1_5` | BTC | 0.562 | 0.529 | 0.527 |

**Biến thể chuẩn (`20_2_0_1_5`) thua lỗ NHẤT QUÁN cả 3 split, cả 2
instrument** (0.68-0.76) — không phải dạng "yếu 1 split" đáng ngờ, mà thua
lỗ đều đặn. 2 biến thể còn lại nhiễu hơn (số trade nhỏ hoặc PF còn tệ hơn).
**Kết luận: đóng candidate, không có edge ở 5m** — khớp hoàn toàn kết luận
xuyên suốt chương trình (bộ công cụ kỹ thuật chuẩn không có edge ở khung
5-15m khi validate trung thực).

## Đã làm (không chỉ đề xuất)

- Build + test local qua Docker (`--cpus=3`): `cargo test --workspace
  --exclude finance-redis` 32/32 pass, `cargo fmt --check` sạch.
- Backtest thật qua `finance-research-local` Docker image (`--cpus=2`) đấu
  qua SSH tunnel vào production data thật.
- Cập nhật lại doc-comment trong code phản ánh đúng kết quả (đóng candidate,
  không phải "chưa test" như comment ban đầu).
- Commit `3544c84`, push, CI đang chạy — vì đây là thay đổi
  research-tool-only (không đụng `StrategyKind`/`deployment_rules.rs`), kỳ
  vọng workflow phân loại đúng là không cần rebuild/deploy runtime service
  (giống pattern Round 54/55's docs/research-only path).

## Không log task cho Codex

Đây là kết quả phủ định tự đóng ngay trong round, không có action item nào
cần Codex — code đã ở trạng thái sạch (test pass, comment đúng sự thật),
sẵn sàng cho round sau nếu ai đó muốn tái sử dụng Keltner Channel indicator
cho hướng khác.
