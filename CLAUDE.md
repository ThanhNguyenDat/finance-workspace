# Claude workspace instructions

## Vai trò

Đây là workspace điều phối hệ sinh thái Finance, không phải checkout runtime.
Đọc `AGENTS.md`, rule/skill liên quan và `raw/handoff_agent.md` trước mỗi vòng.
Claude có thể research, review và xác nhận production độc lập; không tự coi
task đã `Done` chỉ vì Codex báo deploy thành công.

## Phân quyền repository

Khi task thay đổi code, chuyển sang checkout sở hữu code (`finance-mw`,
`finance-web`, `finance-live-action`, `finance-broker` hoặc `mt5`) và giữ một
owner/worktree rõ ràng. Không sửa cùng file/worktree với agent khác. Chỉ cập
nhật `docs/`, `raw/` hoặc `.agents/` trong workspace khi đó là artifact điều
phối, spec hoặc evidence tương ứng.

## Handoff và research

- Ghi tiến độ bằng Tiếng Việt, timezone UTC+7.
- Đọc `raw/researcher/SUMMARY-priority-backlog.md` trước các vòng quant và
  đọc file round được dẫn link trước khi kết luận.
- Backtest phải dùng tooling được quy định trong skill, có train/validation/
  holdout trung thực, Docker CPU cap và timeout cứng.
- Mọi finding mới ghi vào bộ ba `raw/handoff_agent.md`, research note và
  `raw/reports/optimize_loop_update_v2.csv`; không bịa metric còn thiếu.

## Production

Không ghi secret vào handoff hoặc log. Chỉ SSH host được ủy quyền khi skill yêu
cầu và không dump environment/process arguments rộng. Application code đi qua
CI/Coolify; hạ tầng live-first phải có inventory, backup/rollback, mutation có
guard và hậu kiểm trực tiếp.

Claude giữ task ở `Verify` cho tới khi có bằng chứng độc lập. Chỉ chuyển sang
`Done` khi SHA, runtime behavior, data/progress và observability đều khớp với
entry handoff.

## Attribution

Commit của Claude dùng conventional subject và thêm
`Co-Authored-By: Claude <noreply@anthropic.com>`.
