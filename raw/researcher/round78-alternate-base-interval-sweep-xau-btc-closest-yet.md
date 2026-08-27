# Round 78 (2026-08-21) — Sweep XAU/BTC ở base interval 15m/30m: `ema_crossover_12_26` là kết quả gần hoà vốn nhất từng tìm được, nhưng vẫn chưa đủ

Status: research. Round 19/24 (rất sớm trong chương trình) từng kết luận
"đổi base interval không giúp gì" nhưng chủ yếu test trên BTC với trend
filter — round này quét lại có hệ thống hơn cho XAU cụ thể (chưa từng được
test kỹ ở base interval khác 5m) và xác nhận chéo trên BTC.

## Sweep XAU ở 15m: không có gì đáng tin

Top candidate theo min-PF (đã lọc nhiễu): `bollinger_breakout_20_2` chỉ đạt
0.709 — vẫn thua lỗ rõ. Phát hiện 1 outlier giả: `candle_reversion_60bps`
holdout PF=17.48 nhưng **chỉ có 2 trade** trong holdout — artifact mẫu quá
nhỏ kinh điển (giống case Round 49 XAU 8-trade), không phải tín hiệu thật.

## Sweep XAU ở 30m (lọc ≥20 trade/split): `ema_crossover_12_26` gần hoà vốn nhất

| Candidate | Train | Validation | Holdout | Trades (T/V/H) |
|---|---|---|---|---|
| `ema_crossover_12_26` | 0.892 | 0.973 | **0.846** | 256/72/73 |
| `bollinger_keltner_squeeze_10_2_0_1_5` | 1.037 | 0.83 | 0.786 | 247/89/86 |
| `candle_momentum_30bps` | 0.729 | 0.814 | 0.776 | 423/96/74 |

`ema_crossover_12_26` có PF ổn định trong khoảng 0.85-0.97 (không giật cục
giữa các split — khác hẳn dạng overfit đáng ngờ đã gặp nhiều lần), tuy vẫn
<1 nhất quán.

## Xác nhận chéo trên BTC ở 30m: cùng dạng ổn định, cùng mức thua lỗ nhẹ

| Split | Trades | Win rate | PF |
|---|---|---|---|
| Train | 1927 | 24.0% | 0.907 |
| Validation | 596 | 26.3% | 0.819 |
| Holdout | 588 | 26.4% | 0.774 |

**`ema_crossover_12_26` ở 30m là candidate ổn định nhất (PF gần 1 nhất, dao
động ít nhất giữa các split) từng tìm được cho CẢ 2 instrument** trong toàn
bộ 78 round. Vẫn thua lỗ (PF<1 mọi split, mọi instrument) nên KHÔNG đạt bar
promote, nhưng là baseline tốt nhất nếu ai muốn thử thêm 1 đòn bẩy khác (ví
dụ: bộ lọc volatility, hay tinh chỉnh chu kỳ EMA) trong tương lai.

## Kết luận

Xác nhận rộng hơn phát hiện cũ (Round 19/24): đổi base interval không tự nó
tạo ra edge cho cả BTC lẫn XAU, dù đã quét kỹ hơn (15m/30m, có lọc nhiễu mẫu
nhỏ). Không log task implement (chưa đạt bar). Ghi nhận `ema_crossover_12_26`
làm điểm neo tham khảo cho backlog.

## Không thay đổi code

Round này thuần backtest thăm dò (không thêm candidate mới vào code) —
không có gì cần commit.
