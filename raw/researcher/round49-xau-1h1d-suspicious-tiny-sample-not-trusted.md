# Round 49 (2026-08-20) — XAU 1h/1d candidate PF=13.8: KHÔNG tin, mẫu quá thưa

Status: research-only. Test combo MTF chưa từng thử cho XAU (1h base + 1d
higher-tf, tương tự BTC Round 24) — tìm được 1 candidate có số liệu top-line
ấn tượng nhưng đáng ngờ, đúng dạng pattern đã cảnh giác nhiều lần trong
chương trình này (Round 12/18/24: "chỉ thắng ở split cuối, mẫu quá nhỏ").

## Số liệu thô (nhìn hấp dẫn ở lần đầu)

`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, XAU/exness 1h/1d:
- Train: 59 trade, win 20.3%, PF 1.099, PnL $0.02 (gần như hoà vốn)
- Validation: 23 trade, win 17.4%, PF 1.284, PnL **-$0.047 (LỖ thực)**
- Holdout: **8 trade, win 75%, PF 13.835**, PnL $2.77

Full gate: Sharpe 1.19 (pass), Sortino 6.88 (pass rất cao), max streak 5
ngày (pass sát ngưỡng) — nhìn thoáng qua giống "candidate tốt".

## Vì sao KHÔNG tin — mẫu holdout chỉ có 8 trade

**Train gần hoà vốn, validation LỖ thực, chỉ holdout (đúng 8 trade) mới có
số liệu đẹp** — đây chính xác cùng shape đã bị falsify nhiều lần trước đây
(Round 12 candle_reversion, Round 18/34 ORB 30m). 8 trade là mẫu quá nhỏ để
tin PF=13.8 — chỉ cần 1-2 lệnh thắng lớn ngẫu nhiên là đủ tạo ra con số này,
không phản ánh edge ổn định. `positive_day_ratio` chỉ 31.2% (fail, cần
≥55%) — nghĩa là phần lớn NGÀY thực ra âm/flat, lợi nhuận dồn vào vài ngày
outlier hiếm hoi, không phải hiệu suất nhất quán hàng ngày.

## Thêm: vẫn fail `holdout_interval_continuity`

Cùng vấn đề data quality Exness XAU đã flag từ Round 15, Codex đã fix 1
phần (Round 20/21, giảm violation nhưng chưa về 0) — candidate này vẫn fail
check đó, thêm 1 điểm nữa để KHÔNG tin số liệu ở đây.

## Kết luận: KHÔNG phải candidate, không log task implement

Không đủ bằng chứng để coi đây là edge thật — đúng shape "may mắn ở mẫu
nhỏ" đã học được cách nhận diện qua nhiều round trước. Không cần test thêm
biến thể khác ở combo 1h/1d XAU trừ khi có candidate khác với mẫu holdout
đủ lớn hơn (>=20-30 trade tối thiểu, dựa theo kinh nghiệm các candidate
đáng tin trước đây trong chương trình này).
