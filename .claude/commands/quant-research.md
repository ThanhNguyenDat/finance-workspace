---
description: "Run exactly one bounded, state-aware quant research iteration"
---

Thực hiện đúng một vòng nghiên cứu bounded bằng tiếng Việt, timezone vận hành
`UTC+7 / Asia/Ho_Chi_Minh`. Lệnh này được gọi bởi:

```text
/loop 20m /quant-research
```

Không tạo `/loop` khác, không sleep 20 phút, không tự gọi lại chính mình và
không khởi động một Claude CLI/session lồng nhau.

## Bắt đầu vòng

1. Đọc state bằng `./.agents/scripts/quant-research-state.sh state`; state
   authoritative là `.ops/runtime/quant-research/state.json`. Sau đó chạy
   `./.agents/scripts/quant-research-state.sh begin-iteration` đúng một lần và
   đọc lại state để lấy `codex_available`, `research_enabled`, `iteration` và
   timestamp hiện tại.
2. Nếu `research_enabled=false`, ghi nhận vòng đã bỏ qua và dừng trước mọi
   research/backtest tốn tài nguyên.
3. Đọc `raw/reports/optimize_loop_update_v2.csv`,
   `raw/researcher/SUMMARY-priority-backlog.md`, các file liên quan trong
   `raw/researcher/`, và evidence liên quan trong `raw/explain/`.
   `raw/handoff_agent.md` chỉ là lịch sử/index legacy, không phải engineering
   queue hoặc nguồn task/lifecycle status authoritative.

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

- `raw/reports/optimize_loop_update_v2.csv` — một row cho mỗi
  instrument/broker/strategy touched, để trống metric không có evidence;
- `raw/researcher/<meaningful-name>.md` hoặc addendum đúng lịch sử;
- `raw/researcher/SUMMARY-priority-backlog.md` — navigation cho hướng mở/đóng.

Không ghi task mới, không di chuyển `Todo`/`Processing`/`Dev-done`/`Verify`/
`Done`, và không dùng `raw/handoff_agent.md` để chờ Codex implementation.

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
research evidence dưới `raw/`. Không tạo OpenSpec change và không tạo OPS
transaction cho các kết quả này. Một `/loop 20m` không được biến thành một
OPS transaction mỗi 20 phút.

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
   `@.claude/commands/ops/run.md`. Không copy PLAN/IMPLEMENT/VERIFY/FIX/release/
   archive state machine vào command này và không launch CLI khác để gọi slash
   command.
4. Trong PLAN của OPS transaction, dùng cùng `<change>` tại
   `.ops/changes/<change>/` và attach origin references đúng một lần:

   ```text
   ./.agents/scripts/ops-runtime.sh trace-origin <change> <session-id> <iteration> <instrument> <research-artifact>...
   ```

   Chỉ truyền repository-relative paths dưới `raw/researcher/`, `raw/explain/`
   hoặc `raw/reports/`; không truyền nội dung report, environment hay secret.

Khi `codex_available=true`, promoted transaction dùng backend mặc định
`implementation_backend=codex`; Codex Luna/high IMPLEMENT và Terra/high FIX,
với Sol/high fallback chỉ theo worker policy hiện hữu. Khi
`codex_available=false`, promoted transaction chỉ được dùng fallback gate hiện
hữu với `implementation_backend=claude-fallback`, context `quant-fallback`, và
`verification_mode=claude-fallback-self-review`. Không sửa runtime code trực
tiếp ngoài OPS. Backend của transaction đã khởi tạo luôn immutable; quota
toggle chỉ ảnh hưởng transaction mới.

Claude verification findings vẫn là execution evidence theo round tại:

```text
.ops/changes/<change>/runtime/verification-findings-round-<round>.md
```

Không ghi FIX findings vào `raw/handoff_agent.md`.

Mỗi iteration kết thúc bằng tóm tắt ngắn bằng tiếng Việt: state, iteration,
instrument/scope, unseen-data evidence, classification, research files đã cập
nhật và giới hạn thực tế. Với `PROMOTE`, thêm stable change name, OpenSpec path,
OPS path và backend đã persist. Không hỏi user trong research bình thường và
không biến suy luận thành fact.
