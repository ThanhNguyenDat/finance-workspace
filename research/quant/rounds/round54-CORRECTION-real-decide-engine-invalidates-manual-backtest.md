# Round 54 correction (2026-08-21) — Codex đã implement ensemble qua engine THẬT, kết quả khác hẳn backtest tay của tôi — bài học phương pháp luận quan trọng

Status: đính chính trung thực, không phải phát hiện chiến thuật mới. Đây là
điều cần làm ngay khi phát hiện: Codex đã pick up đề xuất ensemble
(Round 36-38, 51-54) và implement thật, kết quả THẬT khác hẳn số liệu tôi tự
tính tay ở Round 51-54.

## Những gì Codex đã làm (đọc trực tiếp code + docs, không suy đoán)

3 commit liên tiếp trong `finance-live-action`:
1. **`56a7f82` "fix: replay real portfolio decisions in research"** — thêm
   `crates/finance-research/src/portfolio_decision_replay.rs` (305 dòng
   mới) — **chính xác là fix cho gap phương pháp luận tôi tìm ra ở Round 20**
   (`finance-research` trước đây không chạy qua `PortfolioDecisionPolicy`
   thật). Giờ đã có.
2. **`339458f` "feat(research): gate fixed-weight alpha ensemble"** — thêm
   `--weighted-ensemble-gate`, dùng **CHÍNH XÁC trọng số grid-search Round
   54 của tôi**: `baseline=0.5, ADX=0.2, macd=0.1, candle_momentum=0.2`.
   Có kèm doc `docs/notes/2026-08-21-fixed-weight-alpha-ensemble.md`.
3. **`b6f664c` "harden profitability evidence"** — deploy production, chạy
   replay thật.

Cả 3 đã CI xanh, deploy production verified (workflow `32443360685` +
nhiều verification run sau đó đều success), production hiện `/healthz`=200.

## Kết quả THẬT (qua `PortfolioDecisionPolicy` thật) — KHÁC HẲN backtest tay của tôi

| Metric | Backtest tay Round 51-54 (trung bình cộng PnL 4 stream độc lập) | Replay thật qua `decide()` (Codex) |
|---|---|---|
| Sharpe | 1.621 (tổ hợp tốt nhất) | **-6.72** |
| positive_day_ratio | 56.0% (PASS) | **25.14% (fail nặng)** |
| Max negative streak | 15 ngày | 8 ngày (nhưng net PnL âm nặng) |
| Net PnL | dương nhẹ (~$0-3) | **-5.92** |

## Vì sao khác nhau HOÀN TOÀN — đây là lỗi phương pháp luận của chính tôi, không phải Codex sai

Đọc kỹ doc Codex viết, cộng với việc tự nhận ra: **cách tôi tính ensemble ở
Round 51-54 KHÔNG PHẢI cách 1 Portfolio ensemble thật hoạt động.**

- **Cách tôi làm (SAI về khái niệm):** lấy `daily_results.return_fraction`
  của 4 candidate ĐÃ CHẠY ĐỘC LẬP (mỗi candidate tự có ledger riêng, tự vào
  lệnh riêng theo tín hiệu riêng của nó), rồi **lấy trung bình cộng return
  hàng ngày của 4 ledger độc lập đó** — giống như chia vốn cho 4 quỹ độc
  lập, mỗi quỹ tự giao dịch theo tín hiệu riêng.
- **Cách Portfolio ensemble thật hoạt động:** CHỈ CÓ 1 ledger, 1 vị thế tại
  1 thời điểm. `PortfolioDecisionPolicy` tổng hợp **entry_score/trend_score
  có trọng số** từ cả 4 strategy để ra **1 quyết định duy nhất** (long/
  short/flat) mỗi candle — không phải 4 vị thế song song rồi cộng PnL.

**2 mô hình này KHÔNG tương đương về mặt toán học lẫn hành vi thị trường**
— trung bình cộng 4 PnL stream độc lập làm mượt được rủi ro theo kiểu
"diversification" cổ điển (đúng như tôi quan sát: Sharpe cao hơn candidate
đơn lẻ) — nhưng đó là diversification giữa **4 VỊ THẾ THẬT chạy song
song**, không phải giữa 4 tín hiệu được gộp thành 1 vị thế duy nhất theo
trọng số. Khi gộp thành 1 quyết định duy nhất, weighted-score có thể rơi
đúng vào vùng "gần ngưỡng, sai hướng liên tục" mà không candidate riêng lẻ
nào gặp phải — cơ chế thất bại hoàn toàn khác.

## Thêm 1 lý do quan trọng khác Codex đã nêu rõ, tôi cần thừa nhận

Doc của Codex ghi rõ: **"Round 54's weights were grid-searched on the same
evaluation window reported by this command... selected research evidence,
not an untouched holdout."** Tôi grid-search 286 tổ hợp trọng số TRÊN CHÍNH
window mà sau đó dùng để "chứng minh" tổ hợp đó tốt — đây là **overfitting/
data snooping kinh điển**, đúng loại lỗi mà cả chương trình research này đã
liên tục cảnh giác với các candidate khác (Round 12, 18, 34) nhưng tôi lại
mắc phải chính lỗi đó ở Round 54 khi tự tin đề xuất "kết quả tốt nhất qua
grid-search" mà không có holdout độc lập cho chính bước chọn trọng số.

## Đánh giá lại: đề xuất ensemble KHÔNG còn là hướng đầy hứa hẹn nữa

**Rút lại hoàn toàn** mọi khuyến nghị "ưu tiên implement ensemble" từ Round
36-38, 51-54. Bằng chứng thật (qua engine thật, không phải backtest tay)
cho thấy **kết quả TỆ HƠN** bất kỳ candidate đơn lẻ nào đã test trong toàn
bộ chương trình (Sharpe -6.72, positive_day_ratio 25.14%). Codex đã làm
đúng: đánh dấu `research_only=true`, `promotion_eligible=false`, tool luôn
exit code 2 cho tới khi có walk-forward/untouched-future gate thật, KHÔNG
promote lên production. Đây là quyết định đúng, không cần Claude can thiệp
thêm ở khía cạnh đó.

## Cảm ơn Codex vì đã tự làm đúng cả 2 việc quan trọng

1. Fix đúng gap phương pháp luận Round 20 TRƯỚC khi test ensemble (không
   test ensemble qua backtest giả như tôi đã làm) — nhờ vậy phát hiện ra
   vấn đề thật thay vì promote nhầm 1 con số ảo.
2. Tự flag rõ selection bias của chính weights tôi đề xuất, không lặng lẽ
   tin theo — đúng kỷ luật honest-holdout mà cả chương trình này đề cao.

## Bài học phương pháp luận cho các round sau

**Từ giờ, MỌI phép tính "ensemble/kết hợp nhiều signal" bằng tay (cộng dồn
`daily_results.return_fraction` từ các gate run riêng lẻ) đều KHÔNG đáng
tin làm bằng chứng cho hiệu suất 1 Portfolio ensemble thật** — chỉ có thể
dùng lệnh `--weighted-ensemble-gate` (hoặc tương đương chạy qua
`PortfolioDecisionPolicy` thật) mới cho kết quả đáng tin. Nếu muốn tìm
trọng số tốt hơn, phải grid-search bằng chính `--weighted-ensemble-gate`
(không phải backtest tay), và BẮT BUỘC giữ 1 phần dữ liệu untouched làm
holdout riêng cho bước chọn trọng số — không dùng lại đúng window đã tối
ưu để tự báo cáo kết quả tốt.
