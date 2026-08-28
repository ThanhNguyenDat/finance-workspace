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
3. Đọc `raw/handoff_agent.md`,
   `raw/reports/optimize_loop_update_v2.csv`,
   `raw/researcher/SUMMARY-priority-backlog.md`, các file liên quan trong
   `raw/researcher/`, và evidence liên quan trong `raw/explain/`. Kiểm tra
   các mục `Dev-done`/`Verify` bằng diff và evidence authoritative; không đổi
   trạng thái chỉ vì handoff của worker tuyên bố đã xong.

## Nghiên cứu và xác minh

- Ưu tiên tài nguyên theo thứ tự `XAU`, rồi `BTC`; token/instrument khác chỉ
  là UI/backlog và không được tiêu tốn vòng backtest định kỳ.
- Tối ưu Portfolio Layer đồng thời theo profitability/không lỗ kéo dài,
  Make Decision rate và trade frequency; xem xét các metric phù hợp như PnL,
  PF, win rate, Sharpe/Sortino, drawdown, streak, SQN và decision rate, không
  tối ưu một metric đơn lẻ.
- Mọi candidate phải có train/validation và OOS, holdout hoặc walk-forward
  defensible trước khi gọi là improvement. Một kết quả rejection/no-change,
  bug dữ liệu có evidence, hoặc candidate cần nghiên cứu thêm đều là output
  hợp lệ; không cherry-pick, p-hack hoặc bịa metric.
- Backtest chỉ chạy bằng tooling Docker của repository theo resource gần
  production, tối đa 2 local strategy/service containers mỗi vòng, tối đa
  khoảng 2 CPU/4 GB RAM/2 GB swap. Chạy song song khi an toàn; không dùng
  production resources cho exploration. Nếu cần SSH, chỉ dùng evidence
  read-only có phạm vi hẹp và không dump env/credentials.

## Output và quyền implement

Sau research/backtest, cập nhật nhất quán:

- `raw/reports/optimize_loop_update_v2.csv` — một row cho mỗi
  instrument/broker/strategy touched, để trống metric không có evidence;
- `raw/researcher/<meaningful-name>.md` hoặc addendum đúng lịch sử;
- `raw/handoff_agent.md` — task mới ở đầu `## Todo`, prefix
  `[Business][Priority][Created at]`, quant thường là `[trading]`, không ghi
  credential/secret; đồng thời refresh
  `raw/researcher/SUMMARY-priority-backlog.md`.

Khi state có `codex_available=true`, chỉ được research → OOS validate → ghi
report → handoff Codex. Không sửa, commit, push hay deploy runtime code.

Khi state có `codex_available=false`, chỉ với candidate đã validate, scope rõ,
acceptance criteria đủ và risk hiểu được, mới được yêu cầu implement fallback.
Fallback phải dùng lifecycle hiện hữu trong
`@.claude/commands/ops/run.md` với context tường minh
`implementation_backend=claude-fallback` với context `quant-fallback`; không copy state machine và không
thực hiện chỉnh sửa runtime trực tiếp bên ngoài lifecycle. Fallback phải giữ
change/repository locks, OpenSpec, VERIFY/FIX/FINAL_VERIFY, RELEASE,
DEPLOY_VERIFY, ARCHIVE và DONE theo mức áp dụng. Nếu cùng top-level Claude
vừa implement vừa verify, ghi rõ `verification_mode=claude-fallback-self-review`
và không gọi một CLI Claude/session mới.

Mỗi iteration phải kết thúc bằng tóm tắt ngắn bằng tiếng Việt: state đã đọc,
iteration, instrument/scope, evidence OOS, kết quả (kể cả negative), report
đã cập nhật, handoff và các giới hạn/chặn thực tế. Không hỏi user trong lúc
research bình thường, không biến suy luận thành fact.
