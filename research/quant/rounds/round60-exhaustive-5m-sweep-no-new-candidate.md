# Round 60 (2026-08-21) — Sweep toàn diện tại đúng interval production (5m): không có candidate mới, đóng không gian tìm kiếm này

Status: research, sweep table thường (không MTF) cho toàn bộ ~35 candidate
plain tại đúng base interval production (5m), cả BTC lẫn XAU/binance — sau
khi đã đóng các hướng patch tham số (Round 57-59), kiểm tra xem còn candidate
nào ở đúng khung thời gian production chưa từng nổi bật hay không.

## Kết quả: 0 candidate đạt PF>1 nhất quán cả 3 split (cả 2 instrument)

Xếp hạng theo MIN(PF 3 split) — "gần đạt nhất":

**BTC/binance 5m:**
| Candidate | Train | Validation | Holdout |
|---|---|---|---|
| `candle_reversion_60bps` | 0.820 | 0.946 | 0.854 |
| `atr_breakout_14_3_0` | 0.819 | **1.124** | **1.253** |
| `rsi_mean_reversion_14_20_80` (đã biết, Round 58) | 0.716 | 0.789 | 0.816 |

**XAU/binance 5m:**
| Candidate | Train | Validation | Holdout |
|---|---|---|---|
| `candle_reversion_30bps` | 0.613 | 0.551 | 1.528 |
| `rsi_mean_reversion_14_20_80` (đã biết) | 0.680 | 0.595 | 0.548 |

## Đáng chú ý nhưng KHÔNG đủ tin: `atr_breakout_14_3_0` (BTC)

2/3 split PF>1 (validation 1.124, holdout 1.253) nhưng train chỉ 0.819 —
cùng dạng "yếu ở train, mạnh dần lên" đã cảnh giác nhiều lần (Round 12, 18,
34 đều falsify pattern này khi test thêm window). Chưa đủ bằng chứng để
coi là candidate thật — cần test thêm window độc lập (như Round 34 đã làm
cho ORB) trước khi tin, nhưng đây là ưu tiên thấp vì chỉ 2/3 split, không
mạnh bằng các pattern đã bị phủ định trước đây từng có.

## Kết luận: đóng không gian tìm kiếm "candidate đơn lẻ tại 5m production"

Sau Round 33 (plain oscillator không trend-filter thì không có edge ở bất
kỳ base interval nào), Round 57-59 (đã tune hết tham số rộng nhất có sẵn
cho 2 strategy live), và round này (sweep toàn bộ ~35 candidate còn lại tại
đúng 5m, XAU lẫn BTC) — **không gian tìm kiếm "1 candidate đơn lẻ, chạy
solo tại 5m" đã được quét gần hết, không còn ứng viên rõ ràng nào**. Kết
luận nhất quán với toàn bộ chương trình: cần signal MỚI HẲN VỀ CƠ CHẾ (như
funding rate — đã đóng vì không nhất quán qua regime) hoặc kiến trúc khác
(swing 4h/1d + gate cho entry tần suất cao — vẫn là hướng lý thuyết mở duy
nhất còn lại, xem `docs/archive/legacy-handoff-agent.md` mục Round 19/36-38 correction),
không phải tiếp tục sweep tham số các candidate hiện có.

## Không log task mới cho Codex

Đây là kết quả phủ định/xác nhận không gian đã đóng — không có action item
cụ thể, chỉ ghi nhận để tránh lặp lại sweep tương tự trong tương lai.
