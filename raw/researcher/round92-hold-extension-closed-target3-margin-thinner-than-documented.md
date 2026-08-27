# Round 92 (2026-08-22) — Thử kéo dài `minimum_hold_decisions` vượt 36 để khai thác thêm — ĐÓNG: không còn dư địa, và phát hiện margin Target 3 hiện tại mỏng hơn tài liệu ghi nhận nhiều

Status: research only. Tự phát hiện và sửa 1 lỗi tính toán của chính mình
giữa round — ghi lại minh bạch thay vì im lặng sửa.

## Bối cảnh

Round 80 chọn `minimum_hold_decisions=36` một cách THẬN TRỌNG dù hold=60 đã
cho thấy cải thiện PnL thêm ~22% — lý do nêu rõ trong file: "giữ margin an
toàn rộng cho Target 3" và "công cụ đo chỉ dùng 5m, production dùng đầy đủ 8
interval". Round 92 kiểm tra: có thực sự còn dư địa để đẩy hold cao hơn (khai
thác thêm cải thiện PnL) mà vẫn an toàn cho Target 3 (≥7/tuần) không?

## ⚠️ Tự phát hiện lỗi giữa round: sai đơn vị tính tần suất/tuần

Lần chạy đầu, tôi tính `tần suất/tuần = trades / (365/7)` — ĐÚNG cho cửa sổ
1 năm nhưng SAI cho cửa sổ **5 năm** (`--days 1825`) đang dùng. Kết quả ban
đầu cho ra tần suất gấp **~5 lần** giá trị thật (vd hiển thị "~41/tuần" thay
vì đúng phải là ~8.2/tuần), khiến tôi tưởng còn rất nhiều margin. Đã tự phát
hiện khi đối chiếu với số liệu Round 87 (hold=36, 2439 trade/5 năm — quy đổi
đúng phải ra ~9.36/tuần, không phải giá trị lớn hơn nhiều lần tôi tính nhầm
ban đầu). Sửa lại: chia đúng cho `1825/7 = 260.71` tuần. Toàn bộ bảng dưới
đây dùng số ĐÃ SỬA.

## Kết quả (5 năm, `one_target`, stop/take=0.01/0.02 hiện tại)

| hold | BTC/binance pnl | tần suất/tuần | BTC/exness pnl | tần suất/tuần |
|---|---|---|---|---|
| 36 (hiện tại, từ Round 87) | -$16.52 | **9.36** | -$19.00 | **9.27** |
| 48 | -$17.66 | 8.19 | -$15.65 | 8.17 |
| 60 | -$15.00 | 7.64 | -$14.30 | 7.53 |
| 72 | -$10.08 | 7.12 | -$12.84 | 7.11 |
| 100 | -$13.02 | 6.27 (**dưới ngưỡng**) | -$12.62 | 6.23 (**dưới ngưỡng**) |

## Cross-check cửa sổ 18 tháng độc lập (bắt buộc theo quy trình) — xác nhận margin còn MỎNG hơn nữa

| hold | BTC/binance tần suất/tuần (18m) | BTC/exness tần suất/tuần (18m) |
|---|---|---|
| 36 | **7.2** (sát ngưỡng 7/tuần) | **7.3** (sát ngưỡng) |
| 72 | **5.7 (DƯỚI ngưỡng)** | **5.7 (DƯỚI ngưỡng)** |

## Phát hiện quan trọng — margin Target 3 hiện tại MỎNG HƠN NHIỀU so với tài liệu

Round 80's tài liệu ghi "hold=36 giữ tần suất ~15/tuần, dư margin lớn so với
ngưỡng 7/tuần" — con số đó đo TRƯỚC KHI Round 83 nới `stop/take` từ
0.005/0.010 lên 0.01/0.02. **Sau khi CẢ 2 lever cùng áp dụng (cấu hình
production thật hiện tại), tần suất 5 năm thực chỉ ~9.3/tuần — margin chỉ
còn ~33% trên ngưỡng, không phải "margin lớn" nữa.** Trên cửa sổ 18 tháng
(gần thực tế hơn), hold=36 hiện tại chỉ ~7.2-7.3/tuần — **gần như CHẠM
ngưỡng Target 3**, không còn margin an toàn thực sự.

## Kết luận — ĐÓNG hướng "kéo dài hold thêm"

**Không còn dư địa để tăng hold vượt 36** — bất kỳ giá trị nào cao hơn (48+)
đều tiếp tục ăn vào margin Target 3 vốn đã mỏng, và hold=72 đã THỰC SỰ dưới
ngưỡng trên cửa sổ 18 tháng gần đây. Không đề xuất thay đổi
`DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS` (giữ nguyên 36).

**Cảnh báo cần theo dõi:** vì margin hiện tại đã mỏng (~7.2-9.3/tuần tuỳ cửa
sổ, sát ngưỡng 7/tuần), sản phẩm phụ của việc 2 lever Round 80+83 cộng dồn
(dù sub-additive về PnL — Round 87 — nhưng CỘNG DỒN về việc giảm tần suất)
khiến hệ thống mất phần lớn khoảng đệm an toàn ban đầu. Nếu có lever mới nào
trong tương lai tiếp tục giảm tần suất (hold dài hơn, stop/take rộng hơn
nữa, hay bất kỳ filter mới nào), PHẢI kiểm tra kỹ tần suất thực trước khi
triển khai — không còn margin lớn để "miễn phí" như trước.

## Việc cho Codex / round sau

- **[trading][medium]** Cập nhật `SUMMARY-priority-backlog.md`/comment liên
  quan tới `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS`: sửa lại tuyên bố
  "margin lớn ~15/tuần" (chỉ đúng dưới stop/take CŨ) thành con số thật sau
  khi cả 2 lever cộng dồn (~9.3/tuần trên 5 năm, ~7.2/tuần trên 18 tháng gần
  đây) — tránh hiểu lầm còn nhiều margin cho các quyết định tương lai.
- Không cần action code — chỉ là làm rõ tài liệu và đóng hướng nghiên cứu
  này (không tăng hold nữa).
