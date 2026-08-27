# Round 22 (2026-08-20) — Đề xuất signal mới: Funding Rate Extreme Reversion (chưa implement)

Status: research proposal, chưa test được bằng backtest vì thiếu 1 phần hạ
tầng (giải thích bên dưới) — không tự bịa số liệu backtest cho 1 signal
chưa tồn tại. Đây là kết quả của Rule 2 (tìm chiến thuật mới qua web/paper)
— lần đầu tiên trong cả 22 round dùng WebSearch thay vì chỉ backtest lại
candidate có sẵn.

## Nghiên cứu web (2026-08-20)

Tìm kiếm về funding rate làm tín hiệu giao dịch cho perpetual futures — đây
là 1 signal đặc thù crypto, khác hẳn mọi candidate đã test (momentum, mean-
reversion giá, MTF trend filter, VWAP, ORB — đều dựa trên OHLCV thuần).

**Phát hiện chính từ nghiên cứu:**
- Funding rate có autocorrelation ngắn hạn nhưng mean-revert dài hạn; funding
  cực trị (dương rất cao = long quá đông/leverage cao) thường đi trước 1 đợt
  đảo chiều giá thật — không phải vì funding "gây ra" đảo chiều, mà vì funding
  cực trị đánh dấu vị thế đông đúc, khi giá đi ngược lại đám đông đó thì
  unwind diễn ra nhanh.
- Ngưỡng cụ thể hay dùng: funding >0.10%/8h trên BTC perpetual lịch sử
  thường đi trước reversion. BTC/USDT funding cap ±0.3%, chuyển sang settle
  hàng giờ khi chạm cap (từ 5/2025).
- Cảnh báo quan trọng, không bỏ qua: funding cực trị có thể kéo dài NHIỀU
  TUẦN trong 1 trend mạnh trước khi đảo chiều — nên dùng funding như 1 input
  kết hợp cùng volume/open-interest/technical, không dùng đơn lẻ làm tín
  hiệu duy nhất.
- Chiến thuật funding-rate-arbitrage "thuần" (delta-neutral: long spot + short
  perp để harvest funding, không có rủi ro hướng giá) đạt Sharpe >3.0 với
  giới chuyên nghiệp — nhưng đây là kiến trúc HOÀN TOÀN khác (market-neutral,
  cần vị thế spot song song) so với hệ thống hiện tại (Alpha/Portfolio ra
  quyết định hướng long/short thuần dựa trên signal, không hedge spot) — nên
  KHÔNG đề xuất hướng arbitrage, chỉ đề xuất hướng "funding cực trị làm bias
  đảo chiều hướng" (directional reversion signal), phù hợp kiến trúc hiện có.

Nguồn: [Kraken - Funding rates as a trading signal](https://www.kraken.com/learn/futures-trading-funding-rate-strategy),
[ApeX - Perpetuals Trading Strategies](https://www.apex.exchange/blog/detail/Perpetuals-Trading-Strategies-Playbook),
[QuantJourney - Funding Rates in Crypto](https://quantjourney.substack.com/p/funding-rates-in-crypto-the-hidden),
[arXiv - Designing funding rates for perpetual futures](https://arxiv.org/pdf/2506.08573).

## Vì sao CHƯA backtest được — đã đọc code, không suy đoán

Đọc `Strategy` trait (`finance-strategy/src/engine.rs:14-31`):
`async fn evaluate(&self, kline: &Kline) -> Option<Signal>` — **chỉ nhận
`Kline`, không có funding rate nào truyền vào**. Đọc `Kline` struct
(`finance-core/src/kline.rs:9-23`) — 13 field (OHLCV, taker buy volume,
trades...), **không có field funding rate nào**.

**Nhưng data funding rate THẬT đã tồn tại sẵn trong hệ thống, chỉ chưa nối
vào tầng signal** — đúng pattern "machinery đã có, chưa wire vào" đã gặp
nhiều lần trong chương trình research này (vd
`reweight_from_alpha_performance` trước khi được wire vào
`survival_first_default`). Cụ thể: `FundingSettlement` struct
(`finance-core/src/broker_pnl.rs:103-113`) có sẵn `settled_at` (timestamp),
`rate_fraction` (funding rate ký hiệu, dương/âm), `mark_price` — và
`finance-research` đã có `--actual-funding-broker`/`--funding-schedule` để
fetch series funding rate CHÍNH XÁC thật (Binance qua venue adapter thật,
không phải giả lập) cho mục đích tính cost trong ledger. Data có thật, chỉ
chưa expose cho `Strategy::evaluate()` dùng làm tín hiệu.

## Đề xuất cụ thể cho Codex (chưa implement, cần code mới thật sự)

1. Thêm 1 cách để `Strategy` (hoặc 1 wrapper strategy mới, theo đúng pattern
   composition đã có của `MultiTimeframeTrendFilterStrategy`) nhận thêm
   `FundingSettlement` series song song với `Kline` stream — không cần đổi
   signature `evaluate()` của MỌI strategy hiện có, chỉ cần 1 wrapper mới
   kiểu `FundingRateExtremeReversionStrategy` tự giữ funding history nội bộ
   (giống cách `MultiTimeframeTrendFilterStrategy` tự giữ `higher_trend_sign`
   nội bộ qua 1 interval riêng).
2. Logic đề xuất (điểm khởi đầu, cần tune qua backtest thật sau khi có code):
   `rate_fraction > +0.0010` (0.10%/period) → bias `EnterShort`;
   `rate_fraction < -0.0010` → bias `EnterLong`; kết hợp làm **filter hướng**
   cho 1 entry signal có sẵn (giống cách `MultiTimeframeTrendFilterStrategy`
   filter theo trend, không phải tự làm entry đơn độc) — tránh lặp lại lỗi
   "chỉ dùng 1 filter đơn lẻ làm entry" đã thấy thất bại ở VWAP mean-reversion
   Round 18/21 (win rate cao nhưng R:R tệ khi dùng đơn độc).
3. **Chỉ áp dụng cho instrument có funding rate thật** (perpetual future —
   BTC/binance, XAU/binance) — **KHÔNG áp dụng Exness CFD** (dùng
   `SwapSettlement`/rollover khác cơ chế, không phải funding perpetual thật
   theo đúng định nghĩa nghiên cứu ở trên).
4. Test qua đúng methodology hiện tại (honest holdout train/validation/
   holdout, `--daily-profit-gate`) trước khi promote — và **quan trọng**:
   test cả tần suất extreme-funding thật xảy ra bao nhiêu lần/tuần trên data
   thật trước khi kỳ vọng nó giải quyết Target 3 (tần suất) — chưa có bằng
   chứng nó tần suất cao hơn các candidate hiện có, chỉ là 1 signal mới chưa
   test, không phải lời hứa.

## Vì sao đây là ưu tiên đáng cân nhắc (không phải chỉ thêm 1 ý tưởng ngẫu nhiên)

Khác hẳn cơ chế mọi candidate đã test (toàn bộ dựa trên hình dạng giá
OHLCV — momentum/mean-reversion/trend filter/session) — funding rate phản
ánh **vị thế/leverage thật của thị trường**, 1 loại thông tin hoàn toàn khác,
có khả năng ít tương quan với các signal hiện có (đúng nguyên tắc
diversification đã nêu ở `raw/proposal/portfolio-profitability-improvements.md`
mục "Cross-timeframe confirmation signal" — tín hiệu ít tương quan mới thực
sự giúp ensemble). Đây cũng là signal ĐẶC THÙ CRYPTO thật sự (không port lại
từ FX/equity như đa số candidate khác) — khớp yêu cầu Rule 2 của user tìm
chiến thuật mới qua nghiên cứu rộng hơn code có sẵn.
