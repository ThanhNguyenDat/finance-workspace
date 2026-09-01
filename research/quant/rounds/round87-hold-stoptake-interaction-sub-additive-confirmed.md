# Round 87 (2026-08-22) — Test tương tác 2 lever Portfolio-construction đã validate (hold-period × stop/take width): sub-additive, cấu hình hiện tại vẫn tối ưu

Status: research only, không commit. Đầu round đã verify độc lập + đóng 3 mục
Verify liên quan trading (Live Action outage, Round 85 `risk_fraction` fix,
risk-policy sync) sang Done trong `handoff_agent.md` — SSH `docker inspect` 4
container Live Action khớp đúng image Codex báo (`a417976330...`,
restart=0, uptime ổn định), và đọc lại checkpoint Redis 4 route độc lập xác
nhận `risk-2pct` trade count = `fixed-pct` = `compounding-10pct` (502=502=502
BTC Binance, 516=516=516 BTC Exness, 7=7=7 XAU Binance, 392=392=392 XAU
Exness) — Round 85's finding đã fix đúng và ổn định trên production thật.

## Câu hỏi (từ `SUMMARY-priority-backlog.md` mục ưu tiên Rule 1, chưa test)

Round 80 (`minimum_hold_decisions` 12→36) và Round 83 (`stop/take` tuyệt đối
0.005/0.010→0.01/0.02) đều validate ĐỘC LẬP, mỗi lever đo riêng lẻ trên nền
"mọi thứ khác giữ mặc định". Chưa ai test: khi cả 2 cùng áp dụng, lợi ích có
cộng dồn tuyến tính không, hay có tương tác?

## Phương pháp — factorial 2×2, `one_target`, `fixed_notional=5` mặc định, BTC cả 2 broker, 5 năm

| Cell | hold | stop/take | BTC/binance pnl (trades) | BTC/exness pnl (trades) |
|---|---|---|---|---|
| A (baseline gốc) | 12 | 0.005/0.010 | -$43.30 (5843) | -$43.18 (5829) |
| B (chỉ lever hold) | 36 | 0.005/0.010 | -$28.87 (3859) | -$28.29 (3869) |
| C (chỉ lever stop/take) | 12 | 0.01/0.02 | -$21.44 (2998) | -$21.61 (2935) |
| D (cả 2, = production hiện tại) | 36 | 0.01/0.02 | -$16.52 (2439) | -$19.00 (2417) |

## Phân tích — tương tác sub-additive, nhất quán 2 broker

Nếu 2 lever cộng dồn tuyến tính, cải thiện D so A phải bằng tổng cải thiện
B-so-A cộng C-so-A:

| Broker | Cải thiện B (%) | Cải thiện C (%) | Cộng dồn dự đoán | Cải thiện D thực tế | Đạt được |
|---|---|---|---|---|---|
| BTC/binance | 33.3% | 50.5% | 83.8% | **61.8%** | 73.7% dự đoán |
| BTC/exness | 34.5% | 49.9% | 84.4% | **56.0%** | 66.3% dự đoán |

Cả 2 broker đều cho thấy D chỉ đạt ~66-74% mức cải thiện mà phép cộng tuyến
tính dự đoán — tương tác **sub-additive nhất quán**, không phải nhiễu 1 phía.
Diễn giải hợp lý: 2 lever cùng lọc một phần overlapping của cùng 1 loại nhiễu
(cả hai đều làm giảm số lần bị "quét oan" bởi biến động ngắn hạn — hold dài
hơn giảm số lần đảo chiều SỚM, stop/take rộng hơn giảm số lần bị chạm sớm; 2
cơ chế này che phủ lẫn nhau một phần).

## Kết luận

**Không đổi gì** — D (cấu hình production hiện tại) vẫn là tổ hợp TỐT NHẤT
trong 4 tổ hợp test được, đúng như đang triển khai. Đây là xác nhận thêm
(không phải phát hiện cần action) rằng Round 80 + Round 83 stack đúng hướng.

**Bài học phương pháp luận quan trọng cho các round sau:** không được giả
định lever mới sẽ cộng dồn tuyến tính với lever đã có khi ước tính lợi ích kỳ
vọng — luôn phải đo lại TỔ HỢP ĐẦY ĐỦ (không chỉ marginal effect) trước khi
kết luận. Ghi vào `SUMMARY-priority-backlog.md` để áp dụng cho lever thứ 3
nếu tìm được trong tương lai.

## Việc cho round sau

Không có action item mới cho Codex. Cập nhật backlog: câu hỏi "hold×stop/take
có cộng dồn tuyến tính không" đã trả lời (KHÔNG, sub-additive nhưng vẫn cùng
chiều cải thiện) — đóng câu hỏi này trong mục ưu tiên Rule 1.
