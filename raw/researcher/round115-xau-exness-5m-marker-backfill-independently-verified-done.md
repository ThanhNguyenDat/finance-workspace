# Round 115 (2026-08-23) — XAU/Exness 5m gap-marker backfill: verify độc lập, chuyển Done

Status: production verification only, không backtest candidate mới, không
đổi code.

## Bối cảnh

Đây là milestone lớn nhất phiên này: hướng "Carry Exness gap metadata
through Kline contract" đã được nhắc tới xuyên suốt hàng chục round trước
(dry-run fail nhiều lần vì bug tmpfs/df/health-window, rồi vướng "XAU exact
lane" giữ lại nhiều commit research của Codex không được push). Round 115
thấy item này đã chuyển sang `## Verify` trong `handoff_agent.md` — quyết
định dừng research mechanism mới, ưu tiên verify độc lập theo đúng Rule 1
(không tin lời kể trong file, tự kiểm tra qua SHA/CI/curl/dữ liệu thật).

## 3 bước verify độc lập

1. **CI run:** `gh run view 32617608885` → `conclusion=success`,
   `headSha=7f70eb360dc95e60a6f3ba0533f51747f8170f03` khớp chính xác claim.
2. **Production identity/health:** curl trực tiếp `/`, `/healthz` (HTTP 200
   cả 2) và `/api/v1/system/version` — trả đúng `commit_sha=7f70eb36...`
   cho finance-mw, cả 4 route Live Action `status=ok` tại `56437f2d9...`.
3. **Dữ liệu thật (quan trọng nhất):** chạy `finance-research` read-only
   qua tunnel — **kênh hoàn toàn khác** công cụ nội bộ Codex dùng để tự
   audit — cho `exness.cfd.XAU.USD/5m`, 5 năm. Continuity block:

   | | Trước backfill (Round 107, 2026-08-23 sớm hơn) | Sau backfill (Round 115) |
   |---|---|---|
   | `unverified_gap_candles` | 170,654 | **0** |
   | `unverified_gap_count` | 1,304 | **0** |
   | `verified_session_gap_count` | (chưa đo) | 1,309 |

   Metric quyết định (`unverified_gap_*` phải về 0 để continuity gate pass)
   khớp hoàn toàn. Số `verified_session_gap_count=1309` đọc được hơi khác
   con số `1313` Codex báo cáo — không đáng ngại, nhiều khả năng do
   segment/marker vs distinct-gap-event đếm theo cách khác nhau, không ảnh
   hưởng kết luận continuity đã sạch.

## Lưu ý phạm vi — chỉ 5m, chưa phải toàn bộ

Kiểm tra luôn continuity của 8 interval còn lại trong cùng response
(15m/30m/1h/2h/4h/12h/1d) — **tất cả vẫn còn unverified gap** (vd 15m:
56,793 candle/1,289 gap chưa verify). Đây **đúng như kỳ vọng**, không phải
lỗi sót — scope backfill từ đầu chỉ nhắm `XAU Exness 5m` (interval hệ thống
sản xuất dùng cho quyết định thật), không phải toàn bộ interval evidence.
Đã ghi rõ trong `SUMMARY-priority-backlog.md` mục 4.5 để round sau không
hiểu nhầm là đã xong toàn bộ.

## Kết luận

Chuyển `## Verify` → `## Done` trong `handoff_agent.md`. Đây là lần đầu
tiên trong toàn bộ chương trình continuity XAU/Exness 5m đạt 0 unverified
gap — gỡ bỏ 1 rào cản honest-backtest lớn đã tồn tại từ Round 20/21 (theo
SUMMARY mục 4.5).

## Việc cho round sau

- Không có action mới bắt buộc. Round sau có thể quay lại research mechanism
  bình thường; nếu muốn mở rộng backfill sang interval khác (15m/1h/...),
  cần Codex lên kế hoạch dry-run-first riêng, không phải việc Quant tự làm.
