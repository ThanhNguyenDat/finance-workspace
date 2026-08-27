# Round 61 (2026-08-21) — `atr_breakout_14_3_0`: giữ được ở window 18 tháng Binance BTC, nhưng ĐẢO NGƯỢC khi test cross-broker/cross-instrument — đóng candidate

Status: research, tiếp nối phương pháp regime-dependency testing (Round 34)
cho candidate near-miss của Round 60 (`atr_breakout_14_3_0`, BTC/binance 5m,
window 5 năm: train=0.819, validation=1.124, holdout=1.253 — dạng "yếu train,
mạnh dần" bị cảnh giác).

## Bước 1: test lại đúng leg gốc (BTC/binance) ở window 18 tháng (545 ngày)

| Split | Trades | Win rate | PF | Net PnL |
|---|---|---|---|---|
| Train | 201 | 41.3% | **1.152** | +1.12 |
| Validation | 86 | 37.2% | **1.121** | +0.41 |
| Holdout | 94 | 34.0% | **1.194** | +0.60 |

**Khác hẳn ORB (Round 34, bị đảo ngược hoàn toàn ở window 18 tháng)** — ở
đây cả 3 split đều PF>1, thậm chí nhất quán hơn window 5 năm gốc (vốn có
train<1). Số trade (201/86/94) đủ lớn để tin theo ngưỡng đã dùng ở Round 49
(≥20-30 tối thiểu). Tần suất holdout: 94 trade / ~109 ngày ≈ 0.86/ngày ≈
**6.0/tuần** — gần đạt Target 3 nếu signal này thật.

→ Tại bước này, kết quả trông like candidate mạnh nhất chương trình từng
gặp. Nhưng theo đúng chuẩn Round 56 (cross-broker validation bắt buộc trước
khi tin bất kỳ candidate nào), tiếp tục test thêm 2 leg độc lập trước khi kết
luận.

## Bước 2: test cross-broker (Exness BTC) và cross-instrument (XAU/binance), cùng window 18 tháng

**Exness/BTC 5m:**
| Split | Trades | Win rate | PF | Net PnL |
|---|---|---|---|---|
| Train | 130 | 47.7% | 1.482 | +2.38 |
| Validation | 76 | 38.2% | **0.729** | -1.08 |
| Holdout | 58 | 32.8% | 1.206 | +0.60 |

**XAU/binance 5m:**
| Split | Trades | Win rate | PF | Net PnL |
|---|---|---|---|---|
| Train | 334 | 17.1% | 0.731 | -1.47 |
| Validation | 60 | 21.7% | 1.057 | +0.07 |
| Holdout | 99 | 18.2% | **0.331** | -1.04 |

**Cả 2 leg độc lập đều KHÔNG nhất quán:**
- Exness/BTC: validation PF=0.729 (<1) — fail giữa 2 split thắng, đúng dạng
  "thắng-thua-thắng" đáng ngờ đã cảnh giác nhiều lần (Round 12/18/34).
- XAU/binance: fail nặng — win rate rất thấp (17-22%), holdout PF=0.331 —
  hoàn toàn không giống pattern ở BTC/binance.

## Kết luận: đóng candidate — đây là artifact riêng của Binance BTC, không phải signal robust

Áp đúng chuẩn Round 56 (BTC 2 broker phải giống nhau mới coi là signal thật,
không phải artifact 1 nguồn giá): ở đây BTC/binance và BTC/exness **khác
nhau rõ rệt** (binance nhất quán 3/3, exness chỉ 2/3 với validation fail) —
ngược với leg thua lỗ đang live (Round 56) từng khớp gần như y hệt giữa 2
broker. Kết hợp XAU falsify hoàn toàn, kết luận: `atr_breakout_14_3_0` chỉ
"đẹp" trên đúng 1 tổ hợp instrument×broker×window đã dùng để tìm ra nó ở
Round 60 — dấu hiệu artifact/data-mining, không phải edge thật.

**Đóng hẳn candidate này, bổ sung vào danh sách đã đóng ở
`SUMMARY-priority-backlog.md` mục 3.** Không log task implement cho Codex —
không đủ bằng chứng, đúng tinh thần Rule 7 (round này có cải tiến: đã kiểm
định và đóng dứt điểm 1 candidate gần-đạt còn treo lơ lửng từ Round 60, tránh
việc các round sau lặp lại điều tra candidate này).

## Giới hạn công cụ (nhắc lại từ Round 55)

Không thể lấy Sharpe/Sortino/streak cho candidate tuỳ ý (`--gate-strategy`
đã bị xoá) — chỉ dùng được PF/win-rate/trades từ sweep thường. Đủ để phủ
định ở bước cross-validation này (PF<1 rõ ràng ở 2/6 split ngoài broker
gốc), không cần thêm metrics khác.
