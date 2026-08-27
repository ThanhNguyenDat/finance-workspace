> ⚠️ **CẬP NHẬT Round 92 (2026-08-22):** con số "~15/tuần, dư margin lớn" bên
> dưới đo TRƯỚC KHI Round 83 nới `stop/take`. Sau khi CẢ 2 lever (hold=36 +
> stop/take=0.01/0.02) cùng áp dụng như production hiện tại, tần suất thật
> chỉ ~9.3/tuần (5 năm) / ~7.2-7.3/tuần (18 tháng) — margin còn lại MỎNG,
> không phải "lớn". Xem `round92-hold-extension-closed-target3-margin-thinner-than-documented.md`.

# Round 80 (2026-08-21) — Tìm và triển khai lever THẬT ĐẦU TIÊN cải thiện Target 1: nâng `minimum_hold_decisions` từ 12 lên 36

Status: dev + research. Sau 80 round, đây là lần đầu tiên tìm được 1 đòn
bẩy cải thiện Target 1 (lợi nhuận) rõ ràng, đã cross-validate mạnh, và đã
triển khai vào production — không phải 1 signal mới, mà là 1 tham số
Portfolio-construction (Rule 1: "tinh chỉnh Model về sizing, position...").

## Phát hiện: `--portfolio-minimum-hold-decisions` là đòn bẩy chưa từng khám phá

`finance-research` có flag `--portfolio-minimum-hold-decisions <N>` (mirror
đúng `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS` production, mặc định 12 =
1 giờ ở khung 5m) — kiểm soát số chu kỳ quyết định Portfolio phải chờ trước
khi được phép ĐẢO CHIỀU vị thế đang mở (không chặn lệnh mở đầu tiên từ flat,
chỉ chặn đảo chiều). Cờ này CHỈ dùng cho báo cáo "Portfolio-construction-comparison"
(`compare_real_portfolio_with_funding`, dùng đúng `production_candidates()`
qua `decision_policy=multi_timeframe_portfolio`) — chưa từng được biến thiên
trong 79 round trước.

## Backtest: quan hệ đơn điệu rõ ràng giữa hold period và PnL

BTC/binance, 5 năm dữ liệu thật:

| hold_decisions | Trades | PnL | Tần suất ước tính |
|---|---|---|---|
| 12 (hiện tại) | 5794 | -$43.68 | ~22/tuần |
| 24 | 4466 | -$34.11 | ~17/tuần |
| **36 (mới)** | **3832** | **-$28.71** | **~15/tuần** |
| 40 | 3634 | -$26.19 | ~14/tuần |
| 60 | 2862 | -$22.37 | ~11/tuần |
| 144 | 1787 | -$12.32 | ~6.9/tuần (dưới ngưỡng Target 3!) |

**Quan hệ đơn điệu, nhất quán**: hold càng dài, trade càng ít, PnL càng bớt
âm. Cơ chế hợp lý: tín hiệu Alpha hiện tại không có đủ edge để đảo chiều
thường xuyên sinh lời — mỗi lần đảo chiều chỉ trả thêm phí giao dịch mà
không có đủ lợi thế bù lại (khớp đúng phát hiện Round 71 về chi phí tỷ lệ).

## Cross-broker: gần như y hệt — xác nhận cơ chế thật, không phải nhiễu 1 nguồn dữ liệu

| hold | Binance | Exness |
|---|---|---|
| 12 | 5794 / -$43.68 | 5813 / -$43.06 |
| 40 | 3634 / -$26.19 | 3663 / -$26.14 |
| 60 | 2862 / -$22.37 | 2872 / -$23.26 |

Chênh lệch <1% giữa 2 broker ở mọi mức — mức nhất quán cao nhất từng thấy
trong toàn chương trình cho bất kỳ phát hiện nào.

## Regime-dependency test (18 tháng độc lập): cùng hướng

hold=12 → hold=60 trên window 18 tháng: 1237 trade/-$8.60 → 702 trade/-$5.58
(giảm ~35%, cùng hướng với window 5 năm's ~49% giảm). Không đảo chiều, không
lật pattern — khác hẳn các candidate bị falsify trước đây (ORB, ema_crossover
trend-filtered).

## Chọn giá trị: 36 (3 giờ) — trung dung, giữ margin an toàn cho Target 3

Không chọn giá trị tích cực nhất (60 hoặc cao hơn) vì: (1) muốn giữ margin
an toàn rộng cho ngưỡng Target 3 (≥7/tuần) — số liệu đo được từ công cụ này
KHÔNG hoàn toàn khớp 1:1 với production thật (production dùng đầy đủ 8
interval đồng bộ + trọng số reweight động, công cụ đo chỉ dùng 5m); (2) 36 =
3 giờ giữ đúng quy ước "bội số giờ tròn" mà comment gốc code đã dùng (12 = 1
giờ); (3) hold=36 đã capture phần lớn cải thiện PnL khả dụng (-43.68→-28.71,
~34% giảm lỗ) mà vẫn giữ tần suất ~15/tuần, dư địa lớn so với ngưỡng 7/tuần.

## Đã triển khai đầy đủ

- Sửa `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS` (12→36) +
  doc-comment giải thích đầy đủ trong `crates/finance-core/src/trading_modes.rs`.
- Xác nhận không có test nào hardcode giá trị 12 tuyệt đối (chỉ dùng
  `DEFAULT+1` tương đối, vẫn đúng với giá trị mới).
- `cargo test --workspace --exclude finance-redis`: 32/32 pass.
- `cargo fmt --check`: sạch.
- `cargo build --release -p finance-api`: thành công.
- Commit `efe7854`, push, CI đang chạy (SẼ deploy thật vì đổi `finance-core`
  — dùng chung production, khác các round research-only trước).

## Giới hạn quan trọng cần nói rõ

Đây **KHÔNG** phải fix hoàn chỉnh cho Target 1 — PF của các Alpha strategy
hiện tại vẫn <1 ở MỌI giá trị hold test được (tín hiệu vẫn không có edge
thật). Thay đổi này chỉ làm hệ thống **THUA LỖ CHẬM HƠN, RẺ HƠN** (giảm ~34%
lỗ đo được), không biến lỗ thành lời. Vẫn cần tìm được 1 signal thật sự có
edge (chưa tìm ra sau 80 round) để đạt Target 1 hoàn toàn ("lợi nhuận ổn
định"). Đây là cải thiện thật, đo lường được, và là bước tiến cụ thể đầu
tiên hướng "ít nhất không lỗ" của Target 1.
