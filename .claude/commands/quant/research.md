---
description: "Run exactly one bounded, state-aware quant research iteration"
---

Thực hiện đúng một vòng nghiên cứu bounded bằng tiếng Việt, timezone vận hành
`UTC+7 / Asia/Ho_Chi_Minh`. Operator chạy lệnh này thủ công (không có launcher
hay orchestrator riêng nào chạy nền cho vòng này nữa — phiên hiện tại tự thực
hiện toàn bộ vòng). Không tạo `/loop`, daemon, scheduler, sleep, hay tự gọi
lại chính mình.

## Nhiệm vụ (chỉ đúng 2 việc)

Vòng này chỉ tồn tại để: **(1) tìm kiếm ra Alpha Layer mới** (signal/candidate
chưa từng test hoặc hướng thật chưa bị đóng trong `research/quant/index.md`
mục 3), và **(2) tối ưu Portfolio Layer** (sizing, construction, risk,
execution-rule tham số) — bằng backtest thật, có train/validation/holdout hoặc
walk-forward defensible. Không việc nào khác được tính là công việc hợp lệ của
vòng, kể cả khi có vẻ liên quan: không audit lifecycle OpenSpec, không kiểm
tra trạng thái archive/handoff, không theo dõi CI/deploy, không đọc ADR,
không status-check các thread bị block bởi lý do bên ngoài (chờ thời gian
lịch, chờ quyết định sản phẩm, chờ hạ tầng không truy cập được).

**Nếu backlog nội bộ (`research/quant/index.md` mục 3 + mục 0.5) không còn
hướng nào mở**, trước khi kết luận `NO-CHANGE`, tìm cơ chế Alpha hoặc
Portfolio-construction mới qua nhiều nguồn — không chỉ web search chung
chung: academic paper (arxiv, SSRN...), quant blog/writeup (QuantInsti,
Macrosynergy...), social/community thảo luận chiến lược (r/algotrading,
quant Twitter/X, TradingView ý tưởng/script cộng đồng cho đúng instrument
XAU/BTC nếu tìm được). Tìm mechanism/kỹ thuật cụ thể chưa từng xuất hiện
trong mục 3 (không phải biến thể tham số của cái đã đóng) — ví dụ thống kê
arbitrage, machine-learning signal đơn giản, volume-profile/market-profile,
order-book microstructure, regime-detection, risk-parity/vol-targeting
variant khác mục 0.5 đã test. Ghi rõ nguồn tìm được (link/tên bài/tên
account nếu có) vào `index.md` mục 0.5 kèm lý do vì sao khác các mục 3 đã
đóng, y hệt cách round442 đã ghi. Không implement ngay trong cùng round tìm
ra ý tưởng trừ khi đã đủ ngân sách backtest của round (ưu tiên ghi ý tưởng
lại cho round sau nếu không chắc).

**Nếu đã tìm qua tất cả nguồn trên mà vẫn không ra cơ chế nào cụ thể và khác
biệt** (không phải chỉ 1 round — kiểm tra `index.md` xem có bao nhiêu round
liên tiếp gần nhất đã thử search mà không ra kết quả), ghi rõ vào `index.md`
có bao nhiêu round liên tiếp đã search không ra gì, và đề xuất operator cân
nhắc chạy round tiếp theo bằng một model/session khác (không có cơ chế pin
provider tự động nữa — đây là quyết định thủ công của operator). Chỉ kết
luận `NO-CHANGE` khi tìm kiếm đa nguồn không ra cơ chế mới — không được bịa
cơ chế chỉ để có việc làm.

## Bắt đầu vòng

1. Xác định số round tiếp theo: tìm file `round<N>-*.md` lớn nhất trong
   `research/quant/rounds/` (hoặc `git log --oneline -- research/quant/rounds/`)
   rồi dùng `N+1`. Không có launcher hay state CLI nào track iteration nữa —
   round-file sequence là nguồn sự thật duy nhất.
2. Đọc `research/quant/reports/optimize_loop_update_v2.csv`,
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
- `research/quant/rounds/round<N>-<meaningful-name>.md` hoặc addendum
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
research evidence dưới `research/quant/`. Không tạo OpenSpec change cho các
kết quả này.

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

## PROMOTE: OpenSpec, dừng ở planning

Với `PROMOTE`, chỉ làm tới bước tạo OpenSpec planning artifact rồi dừng —
không có cơ chế tự động implement/verify nào để giao việc tiếp:

1. Derive một stable meaningful kebab-case `<change>`; không dùng tên kiểu
   `task-87`, `fix-stuff`, hoặc `research-test`.
2. Dùng `/opsx:propose` (native OpenSpec integration của session hiện tại,
   xem `.claude/commands/opsx/propose.md`) để tạo đầy đủ
   `openspec/changes/<change>/`. Proposal/design/tasks/specs phải reference
   research round, instrument, research note và metrics CSV bằng path;
   không copy toàn bộ research report.
3. Dừng lại sau khi OpenSpec change sẵn sàng. Không tự implement, không tự
   gọi lifecycle nào khác. Báo cho operator: stable change name, đường dẫn
   OpenSpec, và rằng implementation cần được operator quyết định thủ công
   (tự làm, hoặc chờ orchestrator mới được dựng lại).

Mỗi iteration kết thúc bằng tóm tắt ngắn bằng tiếng Việt: round number,
instrument/scope, unseen-data evidence, classification, research files đã cập
nhật và giới hạn thực tế. Với `PROMOTE`, thêm stable change name và đường dẫn
OpenSpec change đã tạo. Không hỏi user trong research bình thường và không
biến suy luận thành fact.
