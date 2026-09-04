# Round 447 — NEEDS-MORE-RESEARCH: Volume Profile breakout l288 lặp lại trên XAU nhưng không transfer sang BTC

Date: 2026-09-04. Operator iteration: **249**. Launcher đã ghi iteration một
lần; không gọi `begin-iteration` và không increment thêm. Research state còn
hiển thị iteration 248, được coi là bookkeeping lag theo contract. Timezone vận
hành: UTC+7 / Asia/Ho_Chi_Minh.

## Scope

Vòng này tiếp tục đúng item 7 mục 0.5 từ Round 446: Volume Profile / Market
Profile với histogram volume theo price, POC và Value Area 70%. Candidate đã có
trong research registry của `finance-live-action`, không đưa vào production
registry. Giữ nguyên grid đã đăng ký trước:

- `bin_count ∈ {12,24,48}`;
- `lookback ∈ {96,288}` closed 5m bars;
- hai giả thuyết đối lập `breakout` và `reversion`.

Để kiểm tra cutoff khác Round 446, cả hai route dùng cùng `--as-of
2026-08-20T00:00:00Z`, `--days 500`, `--train-ratio 0.6`,
`--validation-ratio 0.2`; Round 446 dùng cutoff `2026-09-04T14:15:11Z`.
Đây là cutoff khác nhưng hai cửa sổ 500 ngày vẫn chồng lấn phần lớn; vì vậy
không gọi đây là holdout độc lập hoàn toàn.

## Method và resource bounds

Đã rebuild `docker/Dockerfile-research` từ checkout sạch `finance-live-action`
commit `efe5754`. Mỗi route chạy một container detached qua SSH tunnel
read-only `127.0.0.1:18086`, giới hạn `--cpus=2 --memory=4g
--memory-swap=6g --network host`; tổng cộng đúng 2 research containers trong
vòng. Output lấy bằng `docker logs -f`, stdout JSON và stderr ECS log tách
riêng. Cả hai container exit 0 và sau khi chạy không còn container nào từ
`finance-research-local:latest`.

Stderr candle-count evidence:

| route | candles | train / validation / holdout | holdout span | unverified gaps | verified session gaps |
|---|---:|---:|---|---:|---:|
| `exness XAU/USD` CFD | 97,194 | 58,316 / 19,439 / 19,439 | 98.8923495 ngày, 2026-05-13 02:40 → 2026-08-20 00:04 UTC | 0 | 46,807 |
| `binance BTC/USDT` perpetual | 144,001 | 86,401 / 28,800 / 28,800 | 99.9999884 ngày, 2026-05-12 00:05 → 2026-08-20 00:04 UTC | 0 | 0 |

Chi phí mô phỏng là fee 5 bps, slippage 2 bps, funding fallback 1 bps và
starting equity 10,000 USD. Đây là plain Alpha sweep; công cụ không cung cấp
Sharpe/Sortino/decision-rate Portfolio cho các candidate này trong nhánh
plain sweep.

## Results — Exness XAU/USD

PF là `train / validation / holdout`; PnL và tần suất là holdout. Không ô nào
bị bỏ qua.

| strategy | PF train | PF val | PF holdout | trades | net PnL USD | trades/week |
|---|---:|---:|---:|---:|---:|---:|
| `breakout_b12_l96` | 0.8671 | 0.6675 | 0.7867 | 195 | -0.69966 | 13.80 |
| `breakout_b24_l96` | 0.8389 | 0.6681 | 0.7526 | 211 | -0.90330 | 14.94 |
| `breakout_b48_l96` | 0.8241 | 0.6733 | 0.7489 | 215 | -0.92178 | 15.22 |
| `breakout_b12_l288` | 1.0471 | 1.2251 | 1.3454 | 65 | +0.50334 | 4.60 |
| `breakout_b24_l288` | 1.0603 | 1.1289 | **1.3991** | 65 | **+0.57815** | 4.60 |
| `breakout_b48_l288` | 0.9317 | 1.2430 | 1.1630 | 69 | +0.26466 | 4.88 |
| `reversion_b12_l96` | 0.3349 | 0.6523 | 0.4447 | 195 | -2.02972 | 13.80 |
| `reversion_b24_l96` | 0.3325 | 0.6384 | 0.4634 | 211 | -2.05007 | 14.94 |
| `reversion_b48_l96` | 0.3358 | 0.6469 | 0.4586 | 215 | -2.08759 | 15.22 |
| `reversion_b12_l288` | 0.4789 | 0.5106 | 0.4084 | 65 | -1.41279 | 4.60 |
| `reversion_b24_l288` | 0.4601 | 0.5524 | 0.3971 | 65 | -1.48760 | 4.60 |
| `reversion_b48_l288` | 0.5396 | 0.4907 | 0.4783 | 69 | -1.23012 | 4.88 |

`breakout_b12_l288` và `breakout_b24_l288` đều dương ở train, validation và
holdout trên cutoff này. Đây là lần lặp lại thứ hai trên XAU, nhưng chưa phải
bằng chứng độc lập hoàn toàn do cửa sổ chồng lấn.

## Results — Binance BTC/USDT

| strategy | PF train | PF val | PF holdout | trades | net PnL USD | trades/week |
|---|---:|---:|---:|---:|---:|---:|
| `breakout_b12_l96` | 0.6962 | 0.7267 | 0.4717 | 347 | -4.53699 | 24.29 |
| `breakout_b24_l96` | 0.7167 | 0.7616 | 0.4697 | 353 | -4.46870 | 24.71 |
| `breakout_b48_l96` | 0.7183 | 0.7428 | 0.4757 | 361 | -4.50606 | 25.27 |
| `breakout_b12_l288` | 0.7634 | 0.9563 | 0.7301 | 119 | -1.15176 | 8.33 |
| `breakout_b24_l288` | 0.7972 | 0.9052 | 0.6474 | 127 | -1.70747 | 8.89 |
| `breakout_b48_l288` | 0.7798 | 0.8665 | 0.5914 | 133 | -2.07804 | 9.31 |
| `reversion_b12_l96` | 0.6417 | 0.7526 | 0.9395 | 347 | -0.32075 | 24.29 |
| `reversion_b24_l96` | 0.6158 | 0.7047 | 0.9121 | 353 | -0.47132 | 24.71 |
| `reversion_b48_l96` | 0.6003 | 0.7324 | 0.9016 | 361 | -0.54597 | 25.27 |
| `reversion_b12_l288` | 0.8132 | 0.7384 | 0.8598 | 119 | -0.51253 | 8.33 |
| `reversion_b24_l288` | 0.7806 | 0.7699 | 0.9807 | 127 | -0.06883 | 8.89 |
| `reversion_b48_l288` | 0.7887 | 0.7963 | **1.0614** | 133 | **+0.21775** | 9.31 |

Không có BTC candidate nào giữ PF > 1 qua train và validation. Ô
`reversion_b48_l288` chỉ dương ở holdout, nên không được chọn sau train/
validation và không được dùng để phủ nhận transfer failure.

## Portfolio layer

Không có hướng Portfolio-construction áp dụng được để test trong vòng này:
những lever production hiện tại đã đóng; mục còn ghi `--portfolio-atr-periods`
chỉ có ý nghĩa khi `protective_kind=atr`, trong khi policy deployed dùng
`fractional`. Hai container bounded đã được dùng cho Alpha XAU và transfer BTC;
không chạy thêm Portfolio container và không tạo metric Portfolio giả từ plain
sweep.

## Classification và giới hạn

**NEEDS-MORE-RESEARCH.** Volume Profile breakout lookback 288 tiếp tục có
evidence XAU tốt ở cutoff khác, nhưng chưa đạt promotion gate vì:

1. cutoff mới vẫn chồng lấn mạnh với Round 446, chưa phải disjoint holdout hoặc
   walk-forward thứ hai;
2. transfer BTC không sống qua train/validation/holdout; một holdout BTC dương
   đơn lẻ không đủ để chọn candidate;
3. plain sweep không đo extended Portfolio-faithful Sharpe/Sortino, drawdown,
   decision-rate hoặc cost-stress cho candidate;
4. XAU có 98.892 ngày lịch holdout và 0 unverified gaps, nhưng vẫn thiếu
   evidence promotion đầy đủ: transfer cross-route thất bại và không có các
   metric Portfolio-faithful/extended cùng cost-stress cần thiết.

Không cherry-pick `reversion_b48_l288` của BTC, không promote, không tạo
OpenSpec/OPS transaction và không thay đổi production. Item 7 giữ mở: bước
tiếp theo là một cutoff **disjoint** hoặc walk-forward được đăng ký trước trên
XAU, giữ nguyên candidate grid; chỉ cân nhắc Portfolio-faithful gate sau khi
Alpha selection sống sót. Item 8 ML vẫn thấp ưu tiên và chưa triển khai.

## Files

- `research/quant/reports/optimize_loop_update_v2.csv`: thêm 24 rows cho toàn
  bộ grid Alpha của XAU và BTC; metric extended để trống vì plain sweep không
  báo cáo.
- `research/quant/index.md`: thêm navigation Round 447 và giữ Volume Profile
  ở trạng thái mở.
- File này: methodology, candle-count/continuity evidence, toàn bộ 24 ô và
  classification.
