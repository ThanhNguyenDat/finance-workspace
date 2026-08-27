# Tách workspace điều phối khỏi repository code

Ngày: 2026-08-27 (UTC+7)

## Mục tiêu

Đưa contract agent, rules, skills, specs, runbooks, diagrams, research history
và handoff ra `ThanhNguyenDat/finance-workspace`, để Claude/Codex được action từ
một workspace chung. Các repository code vẫn giữ lịch sử và ownership riêng.

## Nguồn và phạm vi seed

Seed đầu tiên được lấy từ local `finance-mw` tại commit chứa các tài liệu hiện
hành. Đã chuyển:

- `AGENTS.md`, `CLAUDE.md` (đã viết lại để mô tả workspace, không giả là repo
  code).
- Toàn bộ `.agents/` rules, skills, helper scripts và agent metadata.
- Toàn bộ `docs/` bao gồm spec observability mới nhất.
- Toàn bộ `raw/` gồm handoff, research notes, reports và archive để giữ audit
  history.

Không chuyển code Go/Rust/TypeScript, `node_modules`, `dist`, credential file,
Docker runtime state hoặc production checkout. `finance-web` là repository code
riêng, không nằm trong workspace.

Evidence local hiện tại:

- Workspace seed commit: `1b0ac09` (`chore(workspace): centralize finance docs
  and agent contracts`).
- `finance-mw` compatibility-pointer commit: `f1a22a6`.
- Cả hai commit mới chỉ tồn tại local theo owner-held push gate; chưa có CI,
  GitHub hoặc Coolify deployment.

## Quy tắc sau migration

1. Task/research/handoff bắt đầu tại `raw/handoff_agent.md` trong workspace.
2. Agent sửa code tại repository sở hữu; workspace chỉ nhận spec/evidence và
   không trở thành nơi build/deploy application.
3. Trong giai đoạn cutover, giữ bản copy tài liệu cũ ở các repo code để CI và
   agent đang chạy không bị gãy. Chỉ xóa hoặc thay bằng pointer sau khi
   `finance-workspace` đã được push, checkout độc lập và kiểm tra link.
4. Mọi task đang Processing phải ghi rõ workspace path mới khi cập nhật handoff.
5. Không chuyển trạng thái Verify/Done chỉ vì seed repository đã tạo; code và
   production evidence vẫn theo pipeline của repository sở hữu.

## Cổng cutover tài liệu

- [ ] Repo workspace có commit đầu tiên và remote SHA đã xác nhận.
- [ ] Claude/Codex đọc được `AGENTS.md`, `CLAUDE.md`, `.agents/` và handoff từ
      workspace checkout mới.
- [ ] Các link quan trọng tới repo code được kiểm tra trên cả local sibling và
      GitHub.
- [ ] CI/workflow của từng repo code không còn phụ thuộc bản copy cũ, hoặc đã
      có compatibility pointer được review.
- [ ] Sau khi đạt các cổng trên mới xóa tài liệu duplicate khỏi `finance-mw`.
