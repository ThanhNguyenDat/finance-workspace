# Round 448 — REJECTED: Volume Profile không sống sót trên cutoff disjoint

Date: 2026-09-04. Operator iteration: **250**. Launcher đã ghi iteration một
lần; không gọi `begin-iteration` và không increment thêm. `quant-research-state`
hiển thị 249 tại lúc bắt đầu (bookkeeping lag); coordinator session đã tiếp
quản đúng iteration 250. Timezone vận hành: UTC+7 / Asia/Ho_Chi_Minh.

## Scope và giả thuyết

Vòng này thực hiện bước tiếp theo đã đăng ký ở Round 447 cho item 7 mục 0.5:
kiểm tra Volume Profile / Market Profile trên một cutoff **disjoint** với các
cửa sổ Round 446 và 447. Grid được cố định trước, không thêm biến thể sau khi
nhìn kết quả:

- `bin_count ∈ {12,24,48}`;
- `lookback ∈ {96,288}` nến 5m đóng;
- `{breakout,reversion}` quanh POC và Value Area 70%.

Chọn bằng train/validation trên `exness XAU/USD`, sau đó đọc transfer trên
`binance BTC/USDT`; holdout chỉ được đọc sau selection. Không có Portfolio
lever mở nào đủ điều kiện để test trong vòng này: `protective_kind` deployed
là `fractional`, nên `--portfolio-atr-periods` không phải lever áp dụng được.

## Method và dữ liệu

Hai route chạy bằng image `finance-research-local:latest` build từ
`finance-live-action` commit `efe5754`, mỗi route một container Docker detached
với `--cpus=2 --memory=4g --memory-swap=6g --network host`, qua SSH tunnel
read-only tới Finance MW `127.0.0.1:18086`. Output được thu bằng `docker logs
-f`, stdout JSON và stderr ECS log tách riêng. Cả hai container exit 0, đã xoá
sau khi đọc; tunnel đóng và không còn container research.

Cutoff cố định là `2025-04-01T00:00:00Z`, `days=500`, split
`train/validation/holdout=60/20/20`, fee 5 bps, slippage 2 bps, funding
fallback 1 bps, starting equity 10,000 USD. Cutoff này kết thúc hơn một năm
trước thời gian bắt đầu của holdout Round 447, nên là cửa sổ disjoint đối với
hai round Volume Profile trước; không gọi các split nội bộ là độc lập với nhau.

| route | candles | train / validation / holdout | holdout span | unverified gaps | verified session gaps |
|---|---:|---:|---|---:|---:|
| `exness XAU/USD` CFD | 96,234 | 57,740 / 19,247 / 19,247 | 102.2361 ngày, 2024-12-19 18:25 → 2025-04-01 00:04 UTC | 0 | 47,202 |
| `binance BTC/USDT` perpetual | 144,001 | 86,401 / 28,800 / 28,800 | 99.99999 ngày, 2024-12-22 00:05 → 2025-04-01 00:04 UTC | 0 | 0 |

## Kết quả Exness XAU/USD

Không có ô nào đạt PF > 1 đồng thời trên train, validation và holdout. Ô
validation tốt nhất trong breakout l288 là b12, nhưng train PF 0.7357 và
holdout PF 0.8078 đều thất bại. Các ô l96 âm rõ trên cả ba split; reversion
cũng âm trên cả ba split.

| strategy | PF train | PF validation | PF holdout | holdout trades | holdout PnL USD | trades/week |
|---|---:|---:|---:|---:|---:|---:|
| breakout b12 l96 | 0.5317 | 0.4869 | 0.3995 | 220 | -1.69023 | 15.06 |
| breakout b24 l96 | 0.5009 | 0.4718 | 0.3765 | 234 | -1.84868 | 16.02 |
| breakout b48 l96 | 0.5238 | 0.4528 | 0.3817 | 235 | -1.85909 | 16.09 |
| breakout b12 l288 | 0.7357 | 1.0374 | 0.8078 | 64 | -0.21520 | 4.38 |
| breakout b24 l288 | 0.7342 | 1.0122 | 0.7599 | 70 | -0.28832 | 4.79 |
| breakout b48 l288 | 0.7229 | 0.9646 | 0.7263 | 72 | -0.33615 | 4.93 |
| reversion b12 l96 | 0.2929 | 0.3378 | 0.3298 | 220 | -1.39144 | 15.06 |
| reversion b24 l96 | 0.3001 | 0.3296 | 0.3293 | 234 | -1.42900 | 16.02 |
| reversion b48 l96 | 0.2765 | 0.3332 | 0.3343 | 235 | -1.43261 | 16.09 |
| reversion b12 l288 | 0.4977 | 0.3702 | 0.3969 | 64 | -0.68216 | 4.38 |
| reversion b24 l288 | 0.4915 | 0.3649 | 0.4105 | 70 | -0.69304 | 4.79 |
| reversion b48 l288 | 0.4983 | 0.3700 | 0.4136 | 72 | -0.67320 | 4.93 |

## Transfer Binance BTC/USDT

Không có breakout cell nào vượt PF 1 trên bất kỳ split nào ở cutoff này.
Reversion b12/b24 l288 có holdout dương với PF 1.0510/1.0856, nhưng cả hai
đều âm và PF < 1 trên train/validation; vì vậy đây là holdout-only noise, không
được chọn. b48 l288 cũng không giữ được holdout (PF 0.9693).

| strategy | PF train | PF validation | PF holdout | holdout trades | holdout PnL USD | trades/week |
|---|---:|---:|---:|---:|---:|---:|
| breakout b12 l96 | 0.7689 | 0.7182 | 0.8513 | 322 | -1.34944 | 22.54 |
| breakout b24 l96 | 0.7675 | 0.7422 | 0.8512 | 330 | -1.36492 | 23.10 |
| breakout b48 l96 | 0.7796 | 0.7191 | 0.8360 | 342 | -1.53336 | 23.94 |
| breakout b12 l288 | 0.8282 | 1.1189 | 0.6668 | 119 | -1.87366 | 8.33 |
| breakout b24 l288 | 0.7987 | 1.0139 | 0.6447 | 125 | -2.11556 | 8.75 |
| breakout b48 l288 | 0.8175 | 0.9169 | 0.7165 | 125 | -1.59982 | 8.75 |
| reversion b12 l96 | 0.7044 | 0.7048 | 0.6563 | 322 | -3.15747 | 22.54 |
| reversion b24 l96 | 0.6987 | 0.6776 | 0.6514 | 330 | -3.25399 | 23.10 |
| reversion b48 l96 | 0.6883 | 0.7054 | 0.6533 | 342 | -3.25354 | 23.94 |
| reversion b12 l288 | 0.8437 | 0.5969 | 1.0510 | 119 | +0.20888 | 8.33 |
| reversion b24 l288 | 0.8729 | 0.6672 | 1.0856 | 125 | +0.36677 | 8.75 |
| reversion b48 l288 | 0.8542 | 0.7295 | 0.9693 | 125 | -0.14899 | 8.75 |

## Classification

**REJECTED.** Volume Profile breakout/reversion không tái lập trên cutoff
disjoint: XAU không có candidate nào sống qua cả ba split, và BTC không cho
transfer candidate được chọn từ XAU. Hai ô BTC reversion dương riêng holdout
không được dùng để cherry-pick vì selection đã thất bại trước đó.

Đây là rejection của cơ chế trong grid đã đăng ký, không phải tuyên bố rằng
mọi cách định nghĩa Volume Profile có thể có đều bất khả thi. Tuy nhiên item 7
đã có hai cutoff chồng lấn trước đó và một cutoff disjoint thất bại; không có
cơ sở để tiêu thêm backtest định kỳ vào cùng cơ chế. Item 7 được đóng; item 8
(ML classifier) vẫn là hướng mở, chưa implement trong vòng này.

Không chạy Portfolio gate, không tạo OpenSpec/OPS transaction, không thay đổi
production.

## Files

- `research/quant/reports/optimize_loop_update_v2.csv`: thêm 24 dòng Alpha cho
  12 cell trên mỗi route; metric extended để trống vì plain sweep không cung cấp.
- `research/quant/index.md`: đóng item 7 sau cutoff disjoint, giữ item 8 mở.
- File này: method, candle-count/continuity gate, toàn bộ 24 cell và kết luận.
