# Round 84 (2026-08-22) — Bug thật: research CLI thiếu risk-policy widening cho equity_fraction/risk_fraction, khiến 2/3 rule Portfolio live không backtest được đúng

Status: research + candidate fix đã viết, build/test/fmt sạch, **CHƯA commit** — theo
yêu cầu user quay lại chế độ Codex-implement, code đang nằm ở working tree
finance-live-action (chưa `git add`/`commit`), sẵn sàng để Codex review/commit.

## Bối cảnh: thử explore sizing_value cho Portfolio theo Rule 1

User yêu cầu explore nhiều process song song (`--portfolio-sizing-mode`/
`--portfolio-sizing-value`, theo hướng ưu tiên đã note ở
`SUMMARY-priority-backlog.md`). Chạy song song 4 backtest qua 4 SSH tunnel
riêng biệt bị fail hết ("transport error") — server đọc chỉ hỗ trợ 1
connection lớn tại 1 thời điểm (kể cả 2 song song cũng fail); quay về chạy
tuần tự (ổn định, đã xác nhận).

## Phát hiện 1: `risk_fraction` sizing mode không được research CLI hỗ trợ

`crates/finance-research/src/execution_rules.rs::selected_rule` (hàm DUY
NHẤT research CLI dùng để dựng Portfolio execution rule cho backtest) chỉ
match `"fixed_notional"` và `"equity_fraction"`, mọi giá trị khác (kể cả
`"risk_fraction"`) rơi vào `UnsupportedValue` error. Trong khi đó, rule
**live** `"risk-2pct"` (`crates/finance-api/src/deployment_rules.rs:84-98`)
dùng chính xác `sizing_mode: "risk_fraction"`. Nghĩa là 1 trong 3 rule
Portfolio đang chạy production **chưa bao giờ backtest được** qua
`finance-research` — mọi kết luận trước đây (vd round 80, 83) chỉ áp dụng
cho rule mặc định `fixed_notional`.

**Đã fix**: thêm nhánh `"risk_fraction"` vào `selected_rule`, mirror y hệt
logic validate ở `finance-api/src/config.rs::PortfolioExecutionConfig::
from_values` (dòng 342-351) — value phải trong (0, 1].

## Phát hiện 2 (nghiêm trọng hơn): `one_target` tự nó cũng đo sai cho equity_fraction/risk_fraction

Đọc source `portfolio_measurement.rs` (2 nơi dựng `PortfolioRiskLayer`, dòng
~170 và ~344): cả hai đều gọi `PortfolioRiskPolicy::default()` trực tiếp.
`PortfolioRiskPolicy::default()` có cap rất hẹp — `max_order_notional:
1_000.0`, `max_order_equity_fraction: 0.10`, `max_leverage: 1.0` — vốn được
thiết kế cho `fixed_notional` nhỏ ($5).

Production (`finance-api/src/trading_api.rs::portfolio_risk_policy`) đã có
sẵn logic "widen" các cap này khi sizing phụ thuộc equity
(`EquityFraction`/`RiskFraction`), dựa theo `starting_equity * leverage` —
nhưng logic widen này **chỉ tồn tại ở finance-api, chưa bao giờ được
research measurement path gọi tới**. `finance-research` là crate riêng,
không phụ thuộc `finance-api` (chỉ phụ thuộc `finance-core`), nên 2 nơi này
đã âm thầm phân kỳ.

### Bằng chứng thực nghiệm (BTC/binance, 5 năm, hold=36, stop/take=0.01/0.02)

| sizing | `one_target` (TRƯỚC fix) | `risk_rejected_counts.risk` |
|---|---|---|
| `fixed_notional=5.0` (mặc định) | -$16.93, 2432 trade | 0 |
| `equity_fraction=0.05` | -$1519.58, 2432 trade | 0 (dưới cap cũ nên vô tình đúng) |
| `equity_fraction=0.10` **(= giá trị đang LIVE ở rule "compounding-10pct")** | **realized_pnl=$0, 0 trade** | **524,235 / 525,083 (99.8%)** |
| `equity_fraction=0.15` | $0, 0 trade | 524,506 / 525,083 (99.9%) |

Rule `"compounding-10pct"` — đang chạy thật trên production, không phải
candidate — nếu ai backtest lại nó qua `finance-research` sẽ thấy "gần như
không bao giờ trade", một kết luận SAI hoàn toàn (production thật vẫn trade
bình thường vì `trading_api.rs` có widen đúng).

### Sau khi fix (dùng chung 1 hàm `PortfolioRiskPolicy::widened_for_simulation`)

| sizing | `one_target` (SAU fix) | `risk_rejected_counts.risk` |
|---|---|---|
| `equity_fraction=0.10` (baseline live) | **-$2816.61, 2432 trade** | **0** |
| `equity_fraction=0.15` | -$3922.35, 2432 trade | 0 |

Số trade khớp với `fixed_notional` (2432) — đúng như kỳ vọng (cùng 1
decision stream, hold=36 không đổi). $ loss tăng đơn điệu theo sizing_value
(nhiều vốn hơn mỗi lệnh -> lỗ $ nhiều hơn trên 1 chiến lược đang lỗ ròng) —
**không phải một lever cải thiện risk-adjusted quality**, chỉ scale tuyến
tính rủi ro, giống hệt kết quả sweep `fixed_notional` (2.5 -> -$8.21, 10.0
-> -$32.85, gần đúng 0.5x/2x của baseline -$16.93). Không có candidate mới
để promote từ chính sweep sizing_value này.

## Root cause: `PortfolioRiskPolicy::widened_for_simulation` giờ sống ở
`finance-core` (dùng chung)

Đã refactor logic widen (nguyên bản nằm trong hàm private
`trading_api.rs::portfolio_risk_policy`) thành 1 method dùng chung:
`crates/finance-core/src/portfolio_risk.rs::PortfolioRiskPolicy::
widened_for_simulation(simulation: SimulationConfig) -> Self`. Cả
`finance-api::trading_api::portfolio_risk_policy` (production, giờ chỉ còn
1 dòng delegate) và `finance-research::portfolio_measurement` (2 nơi dựng
risk layer) đều gọi hàm này — đảm bảo 2 bên không thể phân kỳ lại trong
tương lai.

Thêm 1 regression test mới:
`portfolio_measurement::tests::equity_fraction_sizing_does_not_false_trip_the_risk_gate`
— dựng rule `equity_fraction=0.10` (khớp `compounding-10pct` thật) và assert
`risk_rejected_counts[&PortfolioRiskGate::Risk] == 0` + `one_target.trades >
0`. Test cũ (`one_target_removes_rule_fanout_...`) chỉ dùng `fixed_notional`
nên chưa bao giờ bắt được bug này.

## Verification đã chạy (local, chưa qua CI)

- `cargo build --workspace --exclude finance-redis`: sạch (chỉ warning
  dead-code có sẵn, không liên quan).
- `cargo test --workspace --exclude finance-redis`: tất cả pass (bao gồm
  test mới).
- `cargo fmt --check`: sạch.
- `cargo build --release -p finance-research -p finance-api`: cả 2 binary
  build thành công (1 lỗi permission denied vô hại khi ghi file `.d` cũ
  thuộc root từ build trước đó, không phải do code, đã kiểm chứng binary
  mới sinh ra đúng timestamp).
- Rebuild docker image `finance-research-local:latest`, chạy lại backtest
  thật qua tunnel SSH production (read-only) để xác nhận số liệu ở bảng
  trên — không phải số liệu giả định.

## Việc cho Codex

1. **Review diff hiện có trong working tree finance-live-action** (chưa
   commit): `crates/finance-core/src/portfolio_risk.rs`,
   `crates/finance-api/src/trading_api.rs`,
   `crates/finance-research/src/execution_rules.rs`,
   `crates/finance-research/src/portfolio_measurement.rs`. Nếu ổn, commit +
   push trực tiếp lên `main` theo quy ước solo-maintainer, theo dõi CI xanh,
   để Coolify deploy (đổi `finance-core`/`finance-api` nên chắc chắn trigger
   deploy thật — hành vi production **không đổi** vì đây là refactor giữ
   nguyên logic widen cũ, chỉ thêm chỗ gọi từ phía research, nhưng vẫn cần
   qua đúng quy trình verify production ở
   `.agents/rules/production-deployment-verification.md`).
2. Sau khi deploy, verify production không có gì thay đổi hành vi (đúng như
   kỳ vọng — logic `trading_api.rs::portfolio_risk_policy` behavior giữ
   nguyên 100%, chỉ đổi từ inline sang gọi hàm dùng chung).
3. Cân nhắc (không bắt buộc round này): giờ `risk_fraction` đã backtest
   được, có thể dùng để tái kiểm tra xem rule "risk-2pct" có hưởng lợi từ
   hold=36 + stop/take=0.01/0.02 giống 2 rule kia không (chưa test — nằm
   ngoài scope round này, log riêng nếu cần).
