---
description: "Run exactly one bounded, state-aware quant research iteration"
---

Thực hiện đúng một vòng nghiên cứu bounded bằng tiếng Việt, timezone vận hành
`UTC+7 / Asia/Ho_Chi_Minh`. Operator chạy thủ công từ terminal:

```text
uv run --project tools/orchestrator run-phase-agent-command quant-research
```

Launcher đã ghi iteration đúng một lần trước khi truyền prompt này. Không gọi
`begin-iteration` lần nữa. Không tạo `/loop`, daemon, scheduler, sleep, tự gọi
lại chính mình hoặc gọi trực tiếp provider CLI.

## Nhiệm vụ (chỉ đúng 2 việc)

Vòng này chỉ tồn tại để: **(1) tìm kiếm ra Alpha Layer mới** (signal/candidate
chưa từng test hoặc hướng thật chưa bị đóng trong `research/quant/index.md`
mục 3), và **(2) tối ưu Portfolio Layer** (sizing, construction, risk,
execution-rule tham số) — bằng backtest thật, có train/validation/holdout hoặc
walk-forward defensible. Không việc nào khác được tính là công việc hợp lệ của
vòng, kể cả khi có vẻ liên quan: không audit lifecycle OpenSpec/OPS, không
kiểm tra trạng thái archive/handoff, không theo dõi CI/deploy, không đọc ADR,
không status-check các thread bị block bởi lý do bên ngoài (chờ thời gian
lịch, chờ quyết định sản phẩm, chờ hạ tầng không truy cập được).

**Nếu backlog nội bộ (`research/quant/index.md` mục 3 + mục 0.5) không còn
hướng nào mở**, trước khi kết luận `NO-CHANGE`, dùng web search tìm cơ chế
Alpha hoặc Portfolio-construction mới — mechanism/kỹ thuật cụ thể chưa từng
xuất hiện trong mục 3 (không phải biến thể tham số của cái đã đóng), ví dụ
literature/kỹ thuật quant thực tế: thống kê arbitrage, machine-learning
signal đơn giản, volume-profile/market-profile, order-book microstructure,
regime-detection (Hurst exponent...), risk-parity/vol-targeting variant khác
mục 0.5 đã test. Ghi rõ nguồn tìm được vào `index.md` mục 0.5 kèm lý do vì
sao khác các mục 3 đã đóng, y hệt cách 4 hướng 2026-09-04 đã được ghi trước
khi implement. Chỉ kết luận `NO-CHANGE` khi web search cũng không tìm được
cơ chế nào đủ cụ thể và khác biệt để implement — không được bịa cơ chế chỉ
để có việc làm, và không implement ngay trong cùng round tìm ra ý tưởng trừ
khi đã đủ ngân sách backtest của round (ưu tiên ghi ý tưởng lại cho round
sau nếu không chắc).

## Bắt đầu vòng

1. Đọc research state bằng `uv run --project tools/orchestrator quant-research-state state`
   và agent-role state bằng `uv run --project tools/orchestrator agent-role-state state`.
   Iteration trong research state đã được launcher increment; dùng đúng giá trị
   đó cho mọi attempt tiếp quản. Provider health/probe/candidate selection do
   launcher xử lý, không tự chạy probe hoặc đổi provider trong prompt.
2. Nếu `research_enabled=false`, ghi nhận vòng đã bỏ qua và dừng trước mọi
   research/backtest tốn tài nguyên.
3. Đọc `research/quant/reports/optimize_loop_update_v2.csv`,
   `research/quant/index.md`, rồi chỉ các round, study, audit hoặc sample liên
   quan dưới `research/quant/`. `docs/reviews/` chứa supporting operational
   reviews. `docs/archive/legacy-handoff-agent.md` chỉ là lịch sử legacy, không
   phải engineering queue hoặc nguồn task/lifecycle status authoritative.

## Nghiên cứu và xác minh

- Ưu tiên tài nguyên theo thứ tự `XAU`, rồi `BTC`; token/instrument khác chỉ
  là UI/backlog và không được tiêu tốn vòng backtest định kỳ.
- Tối ưu Portfolio Layer đồng thời theo profitability/không lỗ kéo dài,
  Make Decision rate và trade frequency; xem xét metric phù hợp như PnL, PF,
  win rate, Sharpe/Sortino, drawdown, streak, SQN và decision rate, không tối
  ưu một metric đơn lẻ.
- Mọi candidate phải có train/validation và OOS, holdout hoặc walk-forward
  defensible trước khi gọi là improvement. Không cherry-pick, p-hack, hạ
  threshold để tạo engineering work, hoặc bịa metric.
- Backtest chỉ chạy bằng tooling Docker của repository theo resource gần
  production, tối đa 2 local strategy/service containers mỗi vòng, tối đa
  khoảng 2 CPU/4 GB RAM/2 GB swap. Chạy song song khi an toàn; không dùng
  production resources cho exploration. Nếu cần SSH, chỉ dùng evidence
  read-only có phạm vi hẹp và không dump env/credentials.

Sau research/backtest, cập nhật research truth nhất quán:

- `research/quant/reports/optimize_loop_update_v2.csv` — một row cho mỗi
  instrument/broker/strategy touched, để trống metric không có evidence;
- `research/quant/rounds/round<iteration>-<meaningful-name>.md` hoặc addendum
  đúng lịch sử;
- `research/quant/index.md` — navigation cho hướng mở/đóng.

## Phân loại kết quả

Mỗi vòng phải chọn đúng một classification:

```text
REJECTED
NO-CHANGE
DATA-ISSUE
NEEDS-MORE-RESEARCH
PROMOTE
```

`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, và `NEEDS-MORE-RESEARCH` chỉ cập nhật
research evidence dưới `research/quant/`. Không tạo OpenSpec change và không tạo OPS
transaction cho các kết quả này.

## Promotion gate

Chỉ chọn `PROMOTE` khi mọi điều kiện áp dụng đều đạt:

1. có OOS, holdout hoặc walk-forward evidence defensible;
2. có improvement đáng implement hoặc concrete defect;
3. scope rõ và biết đầy đủ affected repositories;
4. expected behavior rõ;
5. acceptance criteria rõ;
6. risk và failure semantics đã hiểu;
7. trading-safety implications đã hiểu;
8. rollback approach đã hiểu khi áp dụng.

Nếu thiếu một điều kiện, giữ kết quả ở research-only classification phù hợp.

## PROMOTE: OpenSpec rồi OPS

Với `PROMOTE`:

1. Derive một stable meaningful kebab-case `<change>`; không dùng tên kiểu
   `task-87`, `fix-stuff`, hoặc `research-test`.
2. Dùng native OpenSpec integration của session hiện tại để create hoặc update
   đầy đủ `openspec/changes/<change>/` trước implementation. Proposal/design/
   tasks/specs phải reference research iteration, instrument, research note và
   metrics CSV bằng path; không copy toàn bộ research report.
3. Sau khi OpenSpec sẵn sàng, thực hiện canonical lifecycle tại
   `@.claude/commands/ops/e2e.md`. Không copy PLAN/IMPLEMENT/VERIFY/FIX/release/
   archive state machine vào command này. Mọi model-owned phase chỉ chạy qua
   `uv run --project tools/orchestrator run-phase-agent`.
4. Trong PLAN của OPS transaction, dùng cùng `<change>` tại
   `.ops/changes/<change>/` và attach origin references đúng một lần:

   ```text
   uv run --project tools/orchestrator ops-runtime trace-origin <change> <session-id> <iteration> <instrument> <research-artifact>...
   ```

   Chỉ truyền repository-relative paths dưới `research/quant/rounds/`,
   `research/quant/studies/`, `research/quant/audits/`,
   `research/quant/samples/` hoặc `research/quant/reports/`; không truyền nội
   dung report, environment hay secret.

Promoted transaction dùng routing policy mới: PLAN, IMPLEMENT, VERIFY, FIX và
FINAL_VERIFY resolve ordered candidates riêng từ phase-agent state. Candidate
đang chạy immutable; nếu provider xác nhận hết quota, process cũ phải kết thúc
trước khi attempt mới tiếp quản cùng phase/round từ diff và commit hiện tại.
Không sửa runtime code trực tiếp ngoài OPS. Verification evidence ghi
`provider-independent` hoặc `same-provider-process-separated` từ provider thực
tế, không claim độc lập khi cùng provider.

Claude verification findings vẫn là execution evidence theo round tại:

```text
.ops/changes/<change>/runtime/verification-findings-round-<round>.md
```

Không ghi FIX findings vào `docs/archive/legacy-handoff-agent.md`.

Mỗi iteration kết thúc bằng tóm tắt ngắn bằng tiếng Việt: state, iteration,
instrument/scope, unseen-data evidence, classification, research files đã cập
nhật và giới hạn thực tế. Với `PROMOTE`, thêm stable change name, OpenSpec path,
OPS path và routing attempts đã persist. Không hỏi user trong research bình thường và
không biến suy luận thành fact.
