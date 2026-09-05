# Quant Research Domain Rules

## Context

Bằng tiếng Việt. Đây là nội dung nghiên cứu và tiêu chí promote cho một
vòng quant-research của Finance Live Action (BTC/XAU) — mô tả cái gì một
vòng phải thoả mãn, không phải ai làm hay làm theo thứ tự nào.

## Goal

Một vòng chỉ tồn tại để phục vụ đúng 2 module — bằng backtest thật, có
train/validation/holdout hoặc walk-forward defensible. Không việc nào khác
được tính là công việc hợp lệ của vòng, kể cả khi có vẻ liên quan: không
quản lý vòng đời thay đổi kỹ thuật, không kiểm tra trạng thái
archive/handoff, không theo dõi CI/deploy, không đọc ADR, không status-check
các thread bị block bởi lý do bên ngoài (chờ thời gian lịch, chờ quyết định
sản phẩm, chờ hạ tầng không truy cập được).

### Module 1 — Alpha Layer

Tìm kiếm signal/candidate mới: chưa từng test, hoặc hướng thật chưa bị
đóng trong `research/quant/index.md` mục 3.

### Module 2 — Portfolio Layer

Tối ưu sizing, construction, risk, execution-rule tham số — đồng thời
theo profitability/không lỗ kéo dài, Make Decision rate, và trade
frequency.

## Rules

### Tìm hướng mới khi backlog cạn (Module 1)

**Khi backlog nội bộ (mục 3 + mục 0.5) không còn hướng nào mở**, trước khi
kết luận `NO-CHANGE`, tìm cơ chế mới qua nhiều nguồn — không chỉ web search
chung chung:

- academic paper (arxiv, SSRN...);
- quant blog/writeup (QuantInsti, Macrosynergy...);
- social/community thảo luận chiến lược (r/algotrading, quant Twitter/X,
  TradingView ý tưởng/script cộng đồng cho đúng instrument XAU/BTC nếu tìm
  được).

Tìm mechanism/kỹ thuật cụ thể chưa từng xuất hiện trong mục 3 (không phải
biến thể tham số của cái đã đóng) — ví dụ thống kê arbitrage,
machine-learning signal đơn giản, volume-profile/market-profile,
order-book microstructure, regime-detection, risk-parity/vol-targeting
variant khác mục 0.5 đã test.

Ghi rõ nguồn tìm được (link/tên bài/tên account nếu có) vào `index.md` mục
0.5 kèm lý do vì sao khác các mục 3 đã đóng, y hệt cách round442 đã ghi.
Không implement ngay trong cùng round tìm ra ý tưởng trừ khi đã đủ ngân
sách backtest của round (ưu tiên ghi ý tưởng lại cho round sau nếu không
chắc).

**Nếu đã tìm qua tất cả nguồn trên mà vẫn không ra cơ chế nào cụ thể và
khác biệt** (không phải chỉ 1 round — kiểm tra `index.md` xem có bao nhiêu
round liên tiếp gần nhất đã thử search mà không ra kết quả): ghi rõ vào
`index.md` có bao nhiêu round liên tiếp đã search không ra gì, và cân nhắc
chạy round tiếp theo bằng một model/session khác. Chỉ kết luận `NO-CHANGE`
khi tìm kiếm đa nguồn không ra cơ chế mới — không được bịa cơ chế chỉ để
có việc làm.

### Metric (Module 2)

Xem xét metric phù hợp — PnL, PF, win rate, Sharpe/Sortino, drawdown,
streak, SQN, decision rate — không tối ưu một metric đơn lẻ.

### Phương pháp nghiên cứu

- Ưu tiên tài nguyên theo thứ tự `XAU`, rồi `BTC`; token/instrument khác
  chỉ là UI/backlog và không được tiêu tốn vòng backtest định kỳ.
- Mọi candidate phải có train/validation và OOS, holdout hoặc walk-forward
  defensible trước khi gọi là improvement.
- Không cherry-pick, p-hack, hạ threshold để tạo engineering work, hoặc
  bịa metric.
- Backtest chỉ chạy bằng tooling Docker của repository theo resource gần
  production: tối đa 2 local strategy/service containers mỗi vòng, tối đa
  khoảng 2 CPU/4 GB RAM/2 GB swap. Chạy song song khi an toàn; không dùng
  production resources cho exploration.
- Nếu cần SSH, chỉ dùng evidence read-only có phạm vi hẹp và không dump
  env/credentials.

### Evidence bắt buộc cập nhật

Sau research/backtest, research truth phải nhất quán trên 3 file:

- `research/quant/reports/optimize_loop_update_v2.csv` — một row cho mỗi
  instrument/broker/strategy touched, để trống metric không có evidence;
- `research/quant/rounds/round<N>-<meaningful-name>.md` hoặc addendum
  đúng lịch sử;
- `research/quant/index.md` — navigation cho hướng mở/đóng.

### Promotion gate

Chỉ chọn classification `PROMOTE` khi mọi điều kiện dưới đây đều đạt;
thiếu một điều kiện thì giữ kết quả ở research-only classification phù
hợp:

1. có OOS, holdout hoặc walk-forward evidence defensible;
2. có improvement đáng implement hoặc concrete defect;
3. scope rõ và biết đầy đủ affected repositories;
4. expected behavior rõ;
5. acceptance criteria rõ;
6. risk và failure semantics đã hiểu;
7. trading-safety implications đã hiểu;
8. rollback approach đã hiểu khi áp dụng.

## Output

### Classification

Mỗi vòng phải chọn đúng một classification:

```text
REJECTED
NO-CHANGE
DATA-ISSUE
NEEDS-MORE-RESEARCH
PROMOTE
```

`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, và `NEEDS-MORE-RESEARCH` chỉ cập
nhật research evidence dưới `research/quant/`.

### Khi classification là PROMOTE

- Derive một tên thay đổi ổn định, có ý nghĩa, dạng kebab-case — không
  dùng tên kiểu `task-87`, `fix-stuff`, hoặc `research-test`.
- Tài liệu hoá bằng cách tham chiếu tới round nghiên cứu, instrument,
  research note, và file metrics CSV theo đường dẫn — không copy toàn bộ
  nội dung report vào nơi khác.

### Tóm tắt cuối vòng

Mỗi iteration kết thúc bằng tóm tắt ngắn bằng tiếng Việt, gồm:

- round number;
- instrument/scope;
- unseen-data evidence;
- classification;
- research files đã cập nhật;
- giới hạn thực tế.

Với `PROMOTE`, thêm stable change name. Không hỏi user trong research bình
thường và không biến suy luận thành fact.
