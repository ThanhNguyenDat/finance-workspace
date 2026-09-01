# Round 34 (2026-08-20) — ORB 30m BỊ PHỦ ĐỊNH bằng regime-dependency test đã hứa từ Round 18/21

Status: research-only. Thực hiện đúng việc Round 18/21 đã đề xuất nhưng
chưa làm: *"chạy lại walk-forward chỉ dùng 12-18 tháng gần nhất làm train/
validation... không cần chờ observed_days tự nhiên tăng"* — dùng đúng
phương pháp đã falsify `candle_reversion` ở Round 13 (đổi `--days` để thay
đổi window train/validation/holdout, không đổi gì khác).

## Test: `--days 545` (~18 tháng) thay vì `--days 1825` (5 năm), cùng
instrument/interval (Exness XAU 5m)

| Candidate | Window | Train PF | Validation PF | Holdout PF |
|---|---|---|---|---|
| `opening_range_breakout_london_30m` | 5 năm (Round 18/21) | 0.868 | 1.023 | **1.275 (thắng)** |
| `opening_range_breakout_london_30m` | **18 tháng (round này)** | 1.009 | **2.014 (thắng mạnh)** | **0.683 (thua)** |
| `opening_range_breakout_london_60m` | 5 năm | 0.740 | 0.619 | 0.737 |
| `opening_range_breakout_london_60m` | 18 tháng | 1.065 | 1.325 | **0.466 (thua mạnh)** |

## Kết luận: PHỦ ĐỊNH, đúng cách Round 13 đã falsify candle_reversion

**Pattern đảo ngược hoàn toàn khi đổi window** — ở cửa sổ 5 năm, ORB 30m
"thắng" đúng ở holdout (split cuối cùng theo thời gian); ở cửa sổ 18 tháng,
holdout lại là split THUA nặng nhất (0.683, và ORB 60m còn tệ hơn: 0.466).
Đây không phải nhiễu ngẫu nhiên nhỏ — đây là bằng chứng trực tiếp rằng kết
quả "thắng" trước đó phụ thuộc hoàn toàn vào việc chọn đúng lát cắt thời
gian nào làm holdout, không phải 1 edge ổn định xuyên suốt các cách chia dữ
liệu khác nhau. **Cùng chính xác cơ chế đã falsify `candle_reversion` XAU ở
Round 13** (thắng ở 1 window cụ thể, thua khi test trên window khác).

Kết hợp với 2 lý do thận trọng đã có sẵn (Round 18: pattern PF tăng dần qua
split ở window gốc; Round 20/21: fail `holdout_interval_continuity` chưa
giải thích hết) — giờ có đủ 3 bằng chứng độc lập để **đóng hẳn ORB 30m/60m,
không còn là candidate treo "chưa validate" nữa mà là candidate ĐÃ PHỦ
ĐỊNH**, giống `candle_reversion` trước đó.

## Cập nhật quan trọng cho tổng kết chương trình research

Sau phát hiện này, **danh sách "hướng còn mở, chưa bị phủ định" của cả
chương trình research thu hẹp còn lại đúng 1: Funding Rate Extreme
Reversion (Round 22)** — vẫn chưa test được vì thiếu hạ tầng (Strategy
trait chưa nhận funding data), nhưng là hướng DUY NHẤT còn lại chưa có bằng
chứng phủ định trực tiếp nào (vì chưa test được, không phải vì đã test và
qua). Swing MTF trend-filtered family (Round 17 baseline) vẫn là candidate
CÓ edge thật (Sharpe/Sortino dương, cross-broker validated Round 16) nhưng
bị chặn cứng bởi tần suất — không phải bị phủ định, chỉ là không đạt Target
3.

## Hành động

Cập nhật `docs/archive/legacy-handoff-agent.md`: đóng khuyến nghị "không promote ORB 30m"
thành "đã phủ định, không còn là candidate" — tránh Codex hoặc round sau
nhầm tưởng đây vẫn là hướng đang mở.
