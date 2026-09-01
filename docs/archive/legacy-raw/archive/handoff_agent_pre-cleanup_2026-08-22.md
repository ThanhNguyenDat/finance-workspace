# Agent handoff (Claude ↔ Codex) — 2026-08-14

## Processing

- **[Repository layout][P1, requested 2026-08-22] Simplify `docker/`:** keep
  application runtime files at `docker/` root, move Kafka/Redis/PostgreSQL/
  RabbitMQ/kline-maintenance under `docker/infrastructure/`, and consolidate
  Elasticsearch plus the existing monitor stack under
  `docker/observability/`. Active dependencies were retained, all tracked path
  references were updated, and a layout regression was added. Local full
  deployment-script validation plus `make monitor-validate` pass. Commit
  `28e245bd4f70594cb42f7b1bef07173b6579a6ae` is pushed; CI/CD run
  `32561854296` is watched at `/tmp/finance-mw-32561854296.output.log`.

- **[Configuration][P1, requested 2026-08-22] Make
  `docker/env/production.env` the sole container-environment source:** remove
  direct service `environment` injection and Coolify-managed application env
  usage, load runtime values through Compose `env_file`, and do not bake the
  file into the runtime image. Owner explicitly approved committing the real
  values; that decision is recorded in `repository-delivery/SKILL.md`. Commit
  `a9deccaba890c98452c11452abe0a5da05ec1028` is pushed to `main`; local Go,
  Compose, deploy-contract, skill validation, and runtime-image build are green.
  Initial CI/CD run `32561242857` failed because three tests still asserted the
  retired direct-`environment`/`${DIR_NAME}` structure; no publish/deploy ran.
  Fix-forward `1ebee35aaee627acc238dc938779ab2ca03f5058` updates those contracts
  and condenses `repository-delivery/SKILL.md` from 811 to 234 validated lines.
  CI/CD run `32561503542` is queued/watched; keep Processing until Coolify env
  cleanup, exact deployed SHA, runtime behavior, and observability are verified.

- **[CI/CD][P1, requested 2026-08-22] Simplify path-scoped delivery:** audit
  and remove redundant CI/CD work so changes under each application-owned
  folder trigger only that application's bounded validation, image build, and
  Coolify deployment; retain immutable-image, migration, timeout, and final
  production-verification safety gates. Commit `a9deccaba890c98452c11452abe0a5da05ec1028`
  removes Coolify tag/env mutation, uses stable selectors promoted from exact
  immutable builds, and keeps runtime/worker versus web build/deploy gates
  path-scoped; shared `production.env` intentionally triggers both surfaces.
  CI/CD run `32561503542` is the active delivery evidence; watcher log is
  `/tmp/finance-mw-32561503542.output.log`.

- **[Observability][P2, live-first 2026-08-22] Trace delivery visibility:** Grafana dashboard `finance-tracing-prod` (Coolify Grafana resource `vc0gwk040csg4cwg88000k48`) now has panel `Trace Delivery Ratio`, backed by accepted-versus-exported OTel spans. Live API save returned version `2`; VictoriaMetrics evaluated the panel query at `0.5133333333` during the worker Redis outage, proving the panel is live and exposing delivery degradation rather than rendering `No data`. Backup is under `/data/backups/grafana-trace-flow/20260822T055932Z`; source reconciliation commit `201e7fa` is pushed to `main`. Keep this in Verify until the Redis fix restores the ratio and two progressing samples are captured.

- **[Production][P1, review 2026-08-22] Finance MW cgroup OOM and Redis healthcheck credential exposure:** read-only SSH review proved Finance MW image `5eadba4` exceeded its 512 MiB cgroup limit and was killed at `04:51:18Z`, `04:52:34Z`, and `04:53:11Z` (anon RSS about 515–519 MiB); its three restarts caused downstream Binance Live Action transport failures/restarts. The deeper memory-growth trigger remains unknown/unverified pending historical `container_memory_*` and request/trace-export correlation. A separate bounded Docker-event audit proved resolved Redis passwords appear in healthcheck command metadata: `redis-singleton` (30 events/24h) and `research-replay-redis` (2 events/24h). No values were recorded. Both credentials require live-first Coolify rotation, healthcheck command hardening, dependent redeploy, and post-change verification. No mutation has been performed.
  Live-first rotation completed 2026-08-22: Coolify DB/env/compose backup is retained under `/data/backups/redis-credential-rotation/20260822T052319Z` and a follow-up backup under the same root. Both Redis resources, Kafka research, and all four Live Action routes were recreated with health `healthy`, restart `0`; new Docker healthcheck events contain only `redis-cli --no-auth-warning ping` and no password-bearing command. Source reconciliation commit `852178901307bf66e0e79a4baa25686afdd0b884` is pushed to `main`; CI run `32554561552` is being watched. Historical VictoriaMetrics has `process_resident_memory_bytes{job="finance-mw"}` samples in the OOM window, peaking at 288,313,344 bytes before scrape gaps/restart; no cgroup memory series exists, so the deeper trigger remains unknown/unverified.
  That deployment's production verification then proved `kline-ingest` and `job-worker` restart loops with ECS `WRONGPASS`; the running image still read the retired literal from `config/grpc.yaml`, so the failure is credential propagation, not a missing container. Fix-forward `71e96e60dae1faa9ba0f044777a7ce94fcfca8df` adds the `REDIS_PASSWORD` runtime override, wires it into MW/worker Compose, and removes the literal from tracked config/cluster Compose. CI run `32558752472` was dispatched on `201e7fa` but failed before publish/deploy because the web visual snapshot `dark desktop trading journal table scroller` differed (34 passed, 1 failed); no runtime mutation occurred. Production remains Processing until the web gate is resolved, the runtime/worker image is deployed, and both workers are healthy with progressing counters.
  Production incident evidence at 07:21Z: public `/healthz` and `/api/v1/system/version` returned 503; MW, kline-ingest and job-worker were restart-looping on `finance-mw_sha-8521789`, with ECS `WRONGPASS` and no host-wide OOM. Binance Live Action had transport retries/restarts; Tempo/Collector remained healthy. Full CI run `32559246162` is running on main `3aefb31` to deploy the runtime Redis fix and marker descendant; keep Processing until its watcher and production gate pass.

- **[Data quality][P2, processing 2026-08-21] Carry authoritative Exness
  session/no-tick gap metadata through the canonical Finance MW gRPC Kline
  contract into `finance-research`:** preserve `gap_before_reason` and
  `gap_before_candles` from Timescale/API, consume them fail-closed in the
  continuity gate, add regressions for verified closures versus real outages,
  then deliver both repositories and re-run the production evidence gate. The
  detailed investigation history remains in the non-actionable context entry
  under Todo; do not synthesize candles or broaden timestamp heuristics.
  Read-only production audit at 2026-08-21 found Exness XAU legacy coverage is
  mostly unmarked: `5m` has 1,315 raw gap rows, 5 exact valid markers and 1,310
  empty markers (the other retained intervals show the same legacy pattern).
  Therefore delivery also needs a separate dry-run-first, exact-route,
  broker-verified marker backfill; the canonical continuity audit must remain
  read-only and the research consumer must treat unmarked/invalid gaps as
  violations. Finance Live Action consumer `b3f66876ba12049c0f463a345414915e6e7d7140`
  is already live on all four routes. Finance MW source commits
  `6f53aa7695cf6da3158a8b89401c5d95505c42fb`,
  `6d2b7b25ec9fc24cae055bc258e8c77bf382b670`,
  `900642fa404b7a9e41d8db4a2a813bc0c997db28`, and RestartCount fix-forward
  `741d93814822ff3d912eeaeee89b0d7231dff4a1` are on `main`; authoritative
  delivery run `32457328183` completed successfully at `07:35:50Z`, tracked by
  `/tmp/finance-mw-32457328183.output.log`; MW/web/Kline/job runtime identities
  match exact `741d938` and all four Live Action routes match `b3f6687` with
  restart zero. Final baseline at `07:58:56Z` proved real progress on all four
  Live Action workers, 16/16 scrape targets up, fresh ECS within 15 seconds,
  Filebeat healthy/restart zero, 8.3 GiB available RAM, 45 GiB free disk and
  zero full CPU/memory pressure. Exact-route `5m` dry-run `32461014088` failed
  closed in production preflight before build/audit and produced no artifact or
  mutation; the exact silent sub-invariant was not observable. Diagnostic-only
  fix `0d173f4` preserves every threshold while emitting bounded non-secret
  evidence for each guard. Descendant main
  `2a9578b053b7a2471a0d817c9f13a19611f416a6` also integrates the verified
  Filebeat source-of-truth so the old recovery path cannot overwrite live
  autodiscovery again; authoritative delivery run `32461827948` is tracked by
  `/tmp/finance-mw-32461827948.output.log` and completed successfully. Exact
  `2a9578b` MW/web/Kline/job runtimes, 4/4 Live Action workers, current progress,
  16/16 targets, ECS/trace correlation and host safety passed production
  verification; Filebeat source/live semantic SHA is identical `f28f25b...`.
  The second exact-route `5m` dry-run `32464090841` failed closed before build
  or mutation and diagnostics proved the workflow mapped `df -Pk` Used/Available
  columns incorrectly. Regression-backed fix
  `b9d1506567c50cf1e5c55e1d8bd44615bbcf9f82` preserves capacity thresholds and
  parses all six fields explicitly. Delivery `32464517187` deployed exact
  `b9d1506` runtime/worker/web, but CI failed on a false-negative 18-second
  Coolify aggregate-health window; current containers are exact, healthy and
  restart zero. Regression-backed local fix `2cb8ad3` extends only that bounded
  convergence budget to 120 one-second polls. Corrected dry-run `32466390966`
  then passed every identity/pressure/host/DB guard but proved Docker cannot
  copy files from the maintenance container's mounted `/tmp` tmpfs: the audit
  exited zero, `docker cp` reported the file absent, and backfill never ran.
  The next fix replaces all tmpfs `docker cp` directions with bounded validated
  JSON stdin/stdout staging and a real scratch-container round-trip regression.
  Commits `2cb8ad312b64f99eb0d4a3455c65815ee8675bff` and
  `5eadba4c81031abd06262664e8c18cc6c23aeefb` passed full Go/vet, workflow,
  Coolify deployment, actionlint and real scratch transport checks; independent
  safety review passed. Authoritative deploy `32469262783` succeeded and exact
  `5eadba4` passed production identity/data/observability/host checks. Dry-run
  `32471838435` produced a reviewed 1,310-entry `5m` plan with digest
  `46fc687308d3ff55f7270769b5f8cf161041364e7803865f7a152b6f3bf47a06`;
  plan/backup parity passed and unsafe/partial/unverified selections were zero.
  Apply `32472813405` was safely deferred by CPU PSI. Retry `32473110499`
  reached the guarded transaction but timed out on the per-row SQL path; the
  serializable transaction rolled back and canonical rollback audit proved
  route/global markers unchanged `5/25`, with all 32 routes complete and no
  invalid/unverified data. A set-based route-locked apply/verify/rollback fix is
  now Processing; no production marker has been changed yet.

## Todo

- **[Repository docs][P3, requested 2026-08-22] Rename `raw/handoff_codex.md` → `docs/archive/legacy-handoff-agent.md`, push the 5 doc reference updates:** details → `docs/reviews/handoff-rename-2026-08-22.md`.

- **[Bug][P1, found 2026-08-22, Claude round 84 `/loop`] `finance-research`
  backtest tool silently mis-measures 2 of 3 live Portfolio execution rules
  — candidate fix already written, tested, sitting UNCOMMITTED in the
  finance-live-action working tree, ready for Codex to review/commit:**
  `PortfolioRiskPolicy::default()` (used raw by both
  `portfolio_measurement.rs` risk-layer constructions) has conservative caps
  (`max_order_notional: $1,000`, `max_order_equity_fraction: 0.10`,
  `max_leverage: 1.0`) meant for the default `fixed_notional` rule.
  Production's `trading_api.rs::portfolio_risk_policy` widens these caps for
  equity-dependent sizing (`EquityFraction`/`RiskFraction`), but that
  widening never made it into the research measurement path — the two crates
  don't depend on each other (`finance-research` only depends on
  `finance-core`), so they silently diverged. Empirically confirmed via real
  production backtest (BTC/binance, 5yr, hold=36, stop/take=0.01/0.02):
  `equity_fraction=0.10` (the real, currently-deployed sizing value for the
  live `"compounding-10pct"` rule) showed `one_target` = **0 trades**,
  `risk_rejected_counts.risk` = 524,235/525,083 (99.8% false-rejected) when
  measured through the unfixed tool — i.e. anyone backtesting that already-
  deployed rule would have concluded it never trades, which is false (real
  production is fine because `trading_api.rs` widens correctly there).
  Separately, `risk_fraction` sizing mode (used by the live `"risk-2pct"`
  rule) wasn't even a recognized string in
  `finance-research/src/execution_rules.rs::selected_rule` — every attempt
  to backtest that rule errored out entirely.
  **Fix already implemented and verified locally** (build clean, `cargo test
  --workspace --exclude finance-redis` all pass including a new regression
  test, `cargo fmt --check` clean, docker image rebuilt and re-run against
  real production data to confirm both before/after numbers above):
  1. Moved the widening logic into a shared method,
     `finance_core::portfolio_risk::PortfolioRiskPolicy::widened_for_simulation`,
     called by both `trading_api.rs::portfolio_risk_policy` (now a 1-line
     delegate — production behavior is unchanged) and both risk-layer
     constructions in `finance-research/src/portfolio_measurement.rs`.
  2. Added a `"risk_fraction"` branch to
     `finance-research/src/execution_rules.rs::selected_rule`, mirroring
     `finance-api/src/config.rs::PortfolioExecutionConfig::from_values`'s
     existing validation exactly.
  3. New regression test:
     `portfolio_measurement::tests::equity_fraction_sizing_does_not_false_trip_the_risk_gate`.
  Full writeup with before/after tables:
  `research/quant/rounds/round84-portfolio-risk-policy-widening-missing-in-research-tool.md`.
  **Action for Codex**: `git diff`/`git status` in finance-live-action to
  see the 4 already-modified files (`finance-core/src/portfolio_risk.rs`,
  `finance-api/src/trading_api.rs`,
  `finance-research/src/execution_rules.rs`,
  `finance-research/src/portfolio_measurement.rs`) — review, and if
  satisfied, commit + push directly to `main` per the solo-maintainer
  convention, track CI to green, let Coolify deploy (touches
  `finance-core`/`finance-api`, will trigger a real deploy — expected, since
  production behavior is provably unchanged, only refactored for reuse), then
  verify production per the standard baseline. Not urgent/incident-level
  (production itself was never wrong — only the offline research tool was),
  so no need to rush ahead of other Processing work, but worth doing before
  anyone next tries to backtest the `risk-2pct`/`compounding-10pct` rules.

- **[Security][P0, incident 2026-08-21, Claude round 76 `/loop`] `KAFKA_CONTROLLER_PASSWORD`
  exposed via an overly-broad `docker exec ... env` dump — needs rotation:**
  While verifying the Round-20-era Kafka `research-replay-ro` ACL item still
  in Verify (checking `SASL_MECHANISM`/listener config on the production
  Kafka container over SSH), ran `docker exec finance-kafka-node1-... env`
  to locate an admin-client properties path. That command printed the
  container's **entire** environment, not just the SASL config intended —
  including `KAFKA_CONTROLLER_PASSWORD` (KRaft controller-quorum internal
  auth, single-node cluster: `CONTROLLER_QUORUM_VOTERS=0@finance-kafka-node1:9093`).
  **The value is not reproduced here or anywhere in this log** — same
  discipline as the round-20 `KAFKA_CLIENT_PASSWORDS` incident, but this is a
  *different* credential (controller-internal, not client-facing) that was
  never part of that earlier rotation.
  **Claude did not attempt rotation** — unlike a Rust code change, rotating
  a live Kafka KRaft controller credential on a running single-node cluster
  is a stateful infrastructure mutation with real outage risk if done
  incorrectly (this repo's own `repository-delivery` skill treats Kafka
  administration as guarded-SSH infra work, not commit-first code delivery),
  and is out of scope for what Claude is comfortable doing unattended while
  Codex is out of quota. **Needs:** (1) rotate `KAFKA_CONTROLLER_PASSWORD` via
  the Coolify-managed env for this resource (live-first per
  `repository-delivery`), verify the single-node broker/controller stays
  healthy through the restart before considering it done (same evidence bar
  as the round-41 client-password rotation), (2) audit whether other
  Kafka/observability containers were ever inspected with a similarly broad
  `env` dump in this session's history and would need the same treatment,
  (3) consider whether `docker exec ... env` should be avoided entirely for
  future ACL/config verification in favor of a narrower, config-file-only
  read (this session's mistake, worth encoding as a standing caution).

  **2026-08-22 re-check:** rotation is intentionally blocked. Production
  `kline-ingest` and `job-worker` are still restart-looping on the currently
  deployed `finance-mw_sha-8521789...` image; bounded logs repeatedly show
  `connect Redis: WRONGPASS`, and both containers report `Restarting`.
  Kafka itself is healthy with restart count 0, but rotating its controller or
  client credentials while dependent workers are unhealthy would expand the
  outage and cannot be safely verified. No Kafka mutation was performed.
  Resume only after the runtime credential fix is deployed and both workers
  are healthy with advancing progress counters; then backup Coolify state,
  rotate with overlap, and verify broker auth, ACL, produce/consume, lag,
  metrics, traces, and restarts without printing secrets.

- **[Trading][P4 — lead nghiên cứu, user hỏi trực tiếp 2026-08-21, chưa
  backtest] Grid trading cho TP/SL/Entry — chưa từng thử trong toàn bộ
  chương trình:** User hỏi trực tiếp có setup dạng lưới (grid) cho
  TP/SL/Entry chưa. Grep toàn bộ code (`crates/*/src/`) và toàn bộ lịch sử
  research (83+ round, mọi file `research/quant/rounds/round*.md` +
  `handoff_codex.md` + `portfolio-btc-optimization-log.md`) xác nhận: **chưa
  từng được thử hay đề cập lần nào.**
  **2 điểm quan trọng cần cân nhắc trước khi backtest:**
  1. **Không chỉ là 1 `Strategy` mới — cần đổi kiến trúc.**
     `PortfolioConstructionState::construct()` hiện tại chỉ target **1 vị
     thế duy nhất** (Long/Short/Flat) mỗi chu kỳ quyết định — không có khái
     niệm "nhiều lệnh mở song song ở nhiều mức giá" như grid thật sự cần
     (đặt sẵn 1 lưới lệnh mua/bán ở các mức giá cách đều, chờ giá dao động
     qua lại để khớp). Muốn làm grid thật cần thêm 1 execution mode khác
     hẳn, không phải chỉ thêm 1 candidate vào
     `finance-research/src/strategies.rs` như các thử nghiệm trước đây.
  2. **Grid về bản chất là mean-reversion trong biên độ (range-bound)** —
     mâu thuẫn trực tiếp với phát hiện chính xuyên suốt chương trình (Round
     33: mean-reversion thuần không có edge, chỉ có edge khi kết hợp trend
     filter khung cao hơn; Round 79: gấp đôi trend-following/filter không
     giúp gì thêm). Grid hoạt động tốt khi giá đi ngang, nhưng có rủi ro
     "cháy lưới" nổi tiếng khi giá trend mạnh 1 chiều kéo dài (BTC/XAU vốn
     hay trend) — 1 bên lưới bị exposure ngày càng lớn không có cơ chế
     mean-reversion để đóng lại.
  **Đề xuất cho round backtest đầu tiên (nếu theo đuổi hướng này):** trước
  khi đổi kiến trúc, có thể thử 1 phiên bản đơn giản hoá — mô phỏng grid
  bằng cách đặt nhiều mức TP/SL cố định quanh entry hiện tại (không cần
  nhiều vị thế song song thật, chỉ cần test xem "chốt lời từng phần theo
  bậc thang" có cải thiện PnL so với TP/SL đơn hiện tại không) — dùng đúng
  phương pháp `one_target` (Round 82's bài học) để không lặp lại sai lầm đo
  sai công cụ. Nếu kết quả sơ bộ khả quan mới cân nhắc đầu tư công sức đổi
  kiến trúc đầy đủ.

- **[Data quality][P1, observed 2026-08-21 10:20Z] Explain and correct Exness
  Live Action `last_event` timestamp ahead of the production host clock:** all
  four workers were ready and progressing after Finance MW `5eadba4`, but both
  Exness routes exposed `last_event=1787308199` (`10:29:59Z`) while host time
  was about `10:19Z`. Do not use this value as freshness proof until a bounded
  audit correlates its exact metric semantics with MT5 Kline open/close time,
  host/terminal clock, canonical DB tail and one real trace. Distinguish a
  future-close watermark from actual clock skew/off-grid processing; add a
  regression before any fix and do not rewrite candle timestamps speculatively.

- **[Trading][P1 — round 65 tìm ra nguyên nhân thật: bất đối xứng subscription
  strategy (Binance/XAU chỉ 2, các route khác 3-5), xem addendum cuối cùng
  bên dưới để có đề xuất fix cụ thể] `pending_history_backfill` của Binance/XAU
  bị kẹt từ tận thời điểm
  listing (Dec 2025), không giống 3 route còn lại (Claude round 62 `/loop`,
  2026-08-21, đọc trực tiếp Redis production qua SSH, không qua
  finance-research):** Trong lúc verify độc lập fix epoch-migration
  (`bfccc9a`, xem mục Done), phát hiện `runtime_state.pending_history_backfill`
  trong checkpoint của cả 4 route đều có entries, nhưng độ "cũ" khác nhau rõ rệt:
  Exness/BTC 1 entry (5 ngày tuổi), Exness/XAU 1000 entries (1-2 tuần tuổi),
  Binance/BTC 508 entries (~1 tháng tuổi), nhưng **Binance/XAU 508 entries đứng
  yên từ 2025-12-23 → 2025-12-25 (~8 THÁNG tuổi, đúng đợt Binance mới list XAU)**.
  3 route kia có timestamp gần hiện tại (rotating bình thường), riêng Binance/XAU
  đông cứng ngay từ đợt backfill lịch sử ban đầu, chưa từng được xử lý/xoá.
  `recent_klines` (dữ liệu đang xử lý live) của route này vẫn bình thường, mới
  nhất tới `2026-08-21T09:45Z` — worker KHÔNG bị treo, chỉ riêng cụm dữ liệu
  backfill cũ này bị bỏ quên trong checkpoint. **Chưa chứng minh được quan hệ
  nhân-quả trực tiếp với Target 2** (trade_count Binance/XAU chỉ 8 so với
  758-1126 của 3 route kia đo trên cùng epoch counter mới, xem mục Done) nhưng
  đây là dấu hiệu cụ thể đầu tiên khác với giả thuyết "chỉ do lịch sử ngắn"
  (Round 13) — cần Codex điều tra: (1) tại sao riêng route này không drain được
  hàng đợi backfill từ lúc listing, (2) liệu cụm dữ liệu kẹt này có chặn một
  phần warm-up của Portfolio decision policy cho khung thời gian cao hơn (1d/4h)
  hay không, (3) dọn dẹp state mồ côi này nếu xác nhận vô hại. Không log P0/P1
  vì chưa xác nhận ảnh hưởng production thật, nhưng đáng ưu tiên vì là lead cụ
  thể nhất từ trước tới giờ cho vấn đề Target 2 dai dẳng của XAU/binance.

  **[Claude round 63 `/loop`, 2026-08-21 — tìm được CƠ CHẾ cụ thể, nâng độ tin
  cậy P2→P1] `interval_weights` của Binance/XAU dồn gần hết vào 1d/12h/4h, mọi
  interval "entry" role đều = 0:** Đọc `portfolio_evidence.policy` trong cùng
  checkpoint. **Binance/XAU:** `interval_weights` = `1d:0.521, 12h:0.338,
  4h:0.141`, còn `15m:0, 1h:0, 2h:0, 30m:0, 5m:0` — **toàn bộ 5 interval vai
  trò "entry" (15m/30m/5m) và 2 interval "trend" ngắn (1h/2h) đều = 0.0**, chỉ
  còn 3 interval trend dài hạn nhất mang trọng số. **Exness/XAU cùng thời
  điểm:** trọng số trải đều `12h:0.199, 15m:0.116, 1d:0.223, 1h:0.116,
  2h:0.116, 30m:0.116, 4h:0.116` (chỉ 5m=0) — không có interval nào bị zero-out
  hàng loạt như Binance. Do các interval "entry" quyết định `entry_score`
  (theo `required_intervals`), khi TẤT CẢ đều weight=0, `entry_score` của
  Binance/XAU chỉ có thể đổi khi nến 1d/12h/4h đóng — tức tối đa vài lần/ngày
  thay vì mỗi 5-15 phút như thiết kế. **Đây là cơ chế cụ thể (không chỉ tương
  quan) giải thích trực tiếp vì sao Binance/XAU có `trade_count=8` trong khi 3
  route kia có 758-1126** (xem mục Done). Trọng số này đến từ
  `reweight_from_alpha_performance` (weighting lifetime-cumulative theo hiệu
  suất quá khứ, không phải rolling window) — giả thuyết hợp lý nhất: với chỉ
  ~8 tháng lịch sử (từ khi Binance list XAU tháng 12/2025, xem bug
  `pending_history_backfill` phía trên), các strategy ở interval ngắn
  (5m/15m/30m) chưa tích luỹ đủ track record để được trọng số > 0, trong khi
  Exness/XAU có lịch sử từ 2021 nên mọi interval đều có đủ dữ liệu để nhận
  trọng số khác 0. **Đề xuất cho Codex:** kiểm tra công thức
  `reweight_from_alpha_performance` có cơ chế minimum-floor hoặc warm-up period
  cho instrument mới list hay không — nếu weight bị zero-out hoàn toàn do
  thiếu lịch sử (không phải do hiệu suất thật sự tệ), đây chính là nguyên nhân
  gốc của Target 2 cho XAU/binance, và có thể cần floor trọng số tối thiểu
  hoặc warm-up period riêng cho instrument mới. Chưa chạy lại backtest để xác
  nhận full — đây là bằng chứng đọc trực tiếp production state, cần Codex xác
  nhận qua code review `reweight_from_alpha_performance`. Chi tiết trong
  `research/quant/rounds/round63-binance-xau-interval-weight-mechanism.md`.

  **[Claude round 64 `/loop`, 2026-08-21 — xác nhận thêm bằng "thí nghiệm tự
  nhiên" 4 route, củng cố mạnh giả thuyết Round 63]** Đọc thêm `interval_weights`
  của 2 leg BTC (lịch sử dài từ 2021, cả 2 broker) để đối chứng: **Binance/BTC**
  = `12h:0.154, 15m:0.136, 1d:0.167, 1h:0.136, 2h:0.136, 30m:0.136, 4h:0.136,
  5m:0` — **Exness/BTC** = `12h:0.153, 15m:0.134, 1d:0.167, 1h:0.134, 2h:0.134,
  30m:0.134, 4h:0.145, 5m:0`. Cả 2 đều trải đều mọi interval (chỉ 5m=0, giống
  Exness/XAU) — khớp hoàn toàn pattern "lịch sử dài → trọng số trải đều". Vậy
  **3/4 route có lịch sử dài (BTC×2 broker + Exness/XAU) đều trải đều trọng
  số, chỉ đúng 1/4 route có lịch sử ngắn (Binance/XAU, list Dec 2025) bị
  zero-out hàng loạt** — đây là bằng chứng dạng "thí nghiệm tự nhiên" (natural
  experiment) rất sạch, không còn là suy luận từ 1 phép so sánh nữa. Nâng độ
  tin cậy giả thuyết `reweight_from_alpha_performance` cần floor/warm-up cho
  instrument mới list lên mức cao, đáng ưu tiên code-review sớm.

  **[Claude round 65 `/loop`, 2026-08-21 — SỬA LẠI giả thuyết Round 63-64,
  đọc trực tiếp source code + tái tạo đúng công thức, tìm ra nguyên nhân
  THẬT KHÁC HẲN]** Đọc trực tiếp `reweight_from_alpha_performance` +
  `alpha_performance_quality` trong `crates/finance-core/src/trading_modes.rs:464-537`,
  rồi tái tạo công thức bằng Python trên dữ liệu `simulated_ledgers` (per
  interval × strategy) đọc từ production — **khớp CHÍNH XÁC 100%** với
  `interval_weights` quan sát được ở Round 63 (verify công thức đúng).
  **Giả thuyết "lịch sử ngắn → thiếu dữ liệu → weight zero" ở Round 63-64
  SAI** — code cho thấy ngược lại: `trade_count=0` (thiếu dữ liệu) được
  `alpha_performance_quality` trả về **quality=1.0 (tối đa)**, không phải 0
  — "benefit of the doubt" cho signal chưa từng test. Zero thật sự chỉ xảy
  ra khi 1 strategy có **đủ trade_count (≥20, `PERFORMANCE_CONFIDENCE_TRADES`)
  VÀ đang thua lỗ xác nhận** (`realized_pnl<=0` hoặc `gross_profit<=0`).
  **Nguyên nhân thật: bất đối xứng CẤU HÌNH SUBSCRIBE strategy giữa 2
  route.** Binance/XAU chỉ subscribe **2 strategy** (`candle_momentum`,
  `rsi_mean_reversion` — `strategy_weights` chỉ có 2 key). Exness/XAU
  subscribe **3 strategy** (thêm `mtf_stochastic_5m_4h_sma5`, hiện có
  `trade_count=0` ở mọi interval trừ 5m — tức CHƯA TỪNG kích hoạt). Vì
  `interval_quality[interval]` CỘNG DỒN quality qua mọi strategy, việc
  Exness/XAU có thêm 1 strategy 0-trade (tự động quality=1.0 mọi interval nó
  chưa test) tạo ra 1 "sàn" (floor) đẩy interval_quality tối thiểu ≈1.0 ở
  MỌI interval — trong khi Binance/XAU chỉ có 2 strategy, cả 2 đều đã thua
  lỗ xác nhận (trade_count hàng trăm-nghìn) ở mọi interval ngắn, nên
  interval_quality thật sự = 0.0 chính xác ở các interval đó, không có
  strategy nào "cứu". Cùng cơ chế giải thích tại sao cả 2 leg BTC (Round 64)
  đều trải đều trọng số: cả 2 đều subscribe 5 strategy (gồm 3 biến thể MTF
  hiếm khi trigger — `mtf_candle_momentum`/`mtf_macd`/`mtf_stochastic`), tạo
  đủ "sàn" 0-trade tương tự. **Đề xuất cụ thể, rủi ro thấp, không cần sửa
  thuật toán:** subscribe thêm 1 strategy nữa (ví dụ `mtf_stochastic_5m_4h_sma5`
  giống Exness/XAU, hoặc bất kỳ strategy MTF nào phù hợp) cho route
  Binance/XAU — theo đúng công thức, việc này sẽ ngay lập tức nâng
  interval_weights của các interval entry lên >0, tăng tần suất Make
  Decision (Target 2) mà không cần thay đổi logic reweight. Cần Codex xác
  nhận đây có phải thay đổi config-only (subscription) hay cần code, và tại
  sao Binance/XAU thiếu strategy thứ 3 so với 3 route còn lại — có thể là
  thiếu sót cấu hình đơn giản, không phải quyết định có chủ đích.
  **Lưu ý phương pháp luận:** đây là bằng chứng đọc code + tái tạo công thức
  chính xác, độ tin cậy cao hơn hẳn Round 63-64 (vốn chỉ suy luận từ tương
  quan). Giữ nguyên P1 nhưng đổi hướng đề xuất fix từ "floor/warm-up thuật
  toán" sang "cấu hình subscription".

  **[Claude round 66 `/loop`, 2026-08-21 — mô phỏng định lượng hiệu ứng dự
  kiến]** Dùng đúng công thức đã verify, mô phỏng: subscribe thêm 1 strategy
  mới (0 trade lúc đầu) cho Binance/XAU → tổng trọng số 2 interval "entry"
  (15m+30m) đi từ **0.0000 → 0.2056** ngay lập tức (≈21% ảnh hưởng lên
  `entry_score`) — đủ để entry_score thực sự đổi mỗi khi nến 15m/30m đóng.
  **Lưu ý quan trọng:** đây là hiệu ứng tạm thời, không phải fix gốc rễ vĩnh
  viễn — 1 khi strategy mới tích luỹ ≥20 trade, nếu nó cũng thua lỗ như 2
  strategy hiện có (khả năng thật), hiệu ứng "sàn" sẽ suy giảm dần về gần 0
  trở lại. Vẫn đáng làm (rủi ro thấp, cho hệ thống nhiều dữ liệu thật hơn
  trong lúc chờ), nhưng nếu muốn bền vững lâu dài nên cân nhắc thêm 1 floor
  tối thiểu không suy giảm hoàn toàn về 0. Chi tiết đầy đủ (bảng số liệu) ở
  `round65-CORRECTION-real-mechanism-is-strategy-subscription-asymmetry.md`
  mục "Cập nhật Round 66".

  **[Claude round 67 `/loop`, 2026-08-21 — ⚠️ RÚT LẠI đề xuất Round 65-66,
  Codex hết quota lần 2, Claude chuyển sang researcher+dev+reviewer]** User
  xác nhận Codex hết quota lại (không hẹn ngày trở lại lần này) — từ giờ
  Claude tự implement/test/commit/push/deploy/verify, không chỉ log task
  nữa (xem memory `feedback_deploy_ownership`). Trước khi implement đề xuất
  "subscribe thêm 1 strategy cho Binance/XAU", đọc trực tiếp
  `crates/finance-api/src/deployment_rules.rs` để hiểu wiring — phát hiện
  **7 strategy MTF đang live (3 Binance/BTC, 2 Exness/BTC, 1 Exness/XAU
  gồm chính `mtf_stochastic_5m_4h_sma5` mà tôi định đề xuất subscribe thêm)
  đều được promote dựa trên backtest ĐÃ BỊ VÔ HIỆU HOÁ** bởi 1 lookahead bug
  khác (merge kline đa-timeframe sort sai `open_time` thay vì `close_time`,
  root-cause commit `d3b0586`, fix commit `3c16745`, phát hiện+fix
  2026-08-20T09:15Z trong `finance-mw/raw/portfolio-btc-optimization-log.md`
  — 1 thread nghiên cứu khác, trước cả chương trình `/loop` Round 1-66 hiện
  tại). Re-validate cả 7/7 dưới tool đã fix: PF collapse từ 19.6-26.6 xuống
  0.58-0.98, win rate từ 80-85% xuống 25-30% — TẤT CẢ đều thua lỗ/hoà vốn,
  không phải edge mạnh như comment code claim. `deployment_rules.rs` KHÔNG
  được sửa từ sau bug fix (commit cuối `f143c44` lúc 00:30Z, bug fix lúc
  09:15Z cùng ngày) — không ai quay lại re-validate. **Rút lại hoàn toàn đề
  xuất Round 65-66** (subscribe thêm strategy cho Binance/XAU) vì
  `mtf_stochastic_5m_4h_sma5` chính nó đã confirm thua lỗ — làm vậy chỉ là
  lặp lại đúng anti-pattern "zombie strategy" vừa phát hiện. **Đã thử mô
  phỏng xoá cả 7 strategy** (logic đúng: strategy thua lỗ thì không nên
  giữ) nhưng phát hiện xoá sẽ làm interval_weights của CẢ 2 leg BTC sụp đổ
  giống hệt Binance/XAU hiện tại (chúng đang "vô tình" giữ tần suất BTC ổn
  nhờ cơ chế benefit-of-doubt, dù bản thân đã bị confirm vô dụng —
  `strategy_weight` thật trong production đã ~0.0 cho cả 3 ở Binance/BTC).
  **Quyết định: KHÔNG xoá, chỉ sửa comment.** Đã thêm 1 comment correction
  đầy đủ dẫn chứng ngay trên `configured_extra_strategies()`, build +
  `cargo test -p finance-api deployment_rules` (8/8 pass) +
  `cargo fmt --check` sạch, commit `fb9d955`, đã push. **[Verified 2026-08-21T11:35Z]**
  Workflow `32476493251` fail lần 1 do timeout DNS gọi Coolify API (hạ tầng,
  không liên quan code), rerun qua `gh run rerun --failed` thành công (2m48s).
  Production Live Action Verification workflow `32477806952` xanh. Claude tự
  verify độc lập qua SSH (không chỉ tin workflow): cả 4 worker container chạy
  đúng SHA `fb9d955`, healthy, restart gần đây (~1-2 phút), `evaluation_count`
  vẫn tăng liên tục qua restart không mất dữ liệu (Binance BTC/XAU 259,
  Exness BTC 4892, Exness XAU 496 — đúng xu hướng tăng dần từ baseline Round
  62-66). Không đổi runtime behavior. Chi tiết đầy đủ trong
  `round67-MAJOR-invalidated-mtf-strategy-promotions-plus-dev-mode-switch.md`.
  **Vấn đề kiến trúc chưa giải quyết:** mâu thuẫn Target 1 vs Target 2 thật
  sự (BTC "ổn" nhờ zombie strategy tình cờ, XAU sụp vì thiếu zombie tương
  tự) — cần floor có chủ đích trong `reweight_from_alpha_performance` hoặc
  strategy thật sự lời+tần suất cao để thay thế, chưa implement, cần thiết
  kế cẩn thận hơn ở round sau trước khi động vào core algorithm dùng chung
  4 route production.

  **[Claude round 68 `/loop`, 2026-08-21 — ĐÓNG debate floor + fix 1 lỗ hổng
  đóng băng vĩnh viễn thật sự]** Đọc doc-comment gốc ngay trên
  `reweight_from_alpha_performance`: "mature-losing strategies receive zero
  quality **instead of diluting the demonstrated signal**" — xác nhận đây là
  THIẾT KẾ CÓ CHỦ Ý, không phải thiếu sót. **Đóng hẳn câu hỏi floor** — không
  nên thêm, sẽ đi ngược chủ đích thiết kế; Target 2 XAU/binance không giải
  được bằng kỹ thuật trọng số, chỉ giải được bằng cách tìm strategy thật sự
  có edge. Tuy nhiên phát hiện 1 lỗ hổng robustness THẬT khác: hàm chuẩn hoá
  `interval_weights` (`normalize_positive_weights`) KHÔNG có fallback về
  uniform khi tổng=0, khác với `strategy_weights`
  (`normalize_or_uniform_weights`, ĐÃ có fallback) — nếu TẤT CẢ interval bắt
  buộc của 1 route đều đạt "mature+confirm thua lỗ" cùng lúc, Portfolio sẽ
  **đóng băng vĩnh viễn** (không chỉ tần suất thấp), kể cả khi sau này
  strategy cải thiện, vì Portfolio treo thì không sinh trade để tự phục hồi.
  Binance/XAU đã ở 5/8 interval trong trạng thái này. Fix: dùng lại đúng
  `normalize_or_uniform_weights` (đã test) cho cả 2 trục, xoá hàm cũ, thêm
  test `interval_weights_recover_to_uniform_instead_of_freezing_when_every_configured_strategy_is_a_confirmed_loser`.
  `cargo test -p finance-core --test trading_modes`: 53/53 pass;
  `cargo test --workspace --exclude finance-redis`: 32/32 pass (loại
  finance-redis's docker-in-docker test, môi trường không hỗ trợ);
  `cargo fmt --check` sạch; `cargo build --release -p finance-api` thành
  công. Commit `cc0c8ac`, đã push. **[Verified 2026-08-21T12:15Z]** CI
  `32480326873` xanh (pre-commit 4m42s, build-and-push 2m13s, deploy-app
  2m50s). Claude verify độc lập qua SSH: cả 4 worker chạy đúng SHA `cc0c8ac`,
  healthy. `interval_weights` của cả 4 route giữ NGUYÊN byte-for-byte so với
  trước deploy (Binance/XAU vẫn đúng 12h:0.338/1d:0.521/4h:0.141, còn lại 0 —
  đúng dự đoán, fix chưa trigger nên không đổi hành vi hiện tại).
  `evaluation_count` tiếp tục tăng bình thường ở cả 4 route (275/275/4908/512).
  Fix này KHÔNG cải thiện tần suất hiện tại (chưa trigger, chỉ phòng ngừa
  nguy cơ tương lai). Chi tiết trong
  `round68-interval-weight-freeze-fix-plus-design-intent-confirmation.md`.

- **[Trading][research closed, round 70 `/loop`, 2026-08-21] Bollinger/Keltner
  volatility squeeze breakout — implement + backtest + đóng ngay trong round:**
  Cơ chế MỚI (regime chuyển đổi biến động, khác hẳn oscillator/MACD/ATR đã
  có) từ web research. Thêm Keltner Channel indicator + strategy mới
  (`crates/finance-strategy/src/indicators/keltner.rs`,
  `crates/finance-research/src/strategies.rs`, research-only, không đụng
  `StrategyKind`/`deployment_rules.rs`), 9 unit test, build+test qua Docker
  (`cargo test --workspace --exclude finance-redis`: 32/32 pass, fmt sạch).
  Backtest thật (5 năm, BTC+XAU/binance): biến thể chuẩn thua lỗ nhất quán cả
  3 split, cả 2 instrument (PF 0.68-0.76) — đóng candidate, cập nhật comment
  code phản ánh đúng kết quả. Commit `3544c84`, push. **[Verified
  2026-08-21T12:45Z]** CI xanh (pre-commit 4m23s, build-and-push 2m8s,
  deploy-app 2m50s — CÓ deploy thật vì Keltner Channel indicator nằm trong
  crate dùng chung `finance-strategy`, dù bản thân strategy mới chỉ ở
  research-only). Verify độc lập qua SSH: cả 4 worker chạy đúng SHA
  `3544c84`, healthy, `evaluation_count` tiếp tục tăng bình thường
  (282/284/4917/521, không regression — đúng dự đoán cho thay đổi
  research-tool-only). Chi tiết
  `round70-bollinger-keltner-squeeze-implemented-and-closed.md`. Cũng đã
  đóng gói toàn bộ quy trình `/loop` này thành skill
  `finance-mw/.agents/skills/quant-research-loop/SKILL.md` (commit `565eff0`,
  theo yêu cầu user "build thành 1 skill riêng để tái sử dụng") — CI docs-only
  xanh, không deploy.

- **[Trading][research closed, round 71 `/loop`, 2026-08-21] Sửa lại 1 "open
  lead" cũ + tái xác nhận tín hiệu daily-bar đã yếu đi:** Thread nghiên cứu
  trước (`portfolio-btc-optimization-log.md`) đề xuất tăng position size để
  "pha loãng" `cost_to_gross_pnl_ratio=1.15` của tín hiệu daily-bar. Trước khi
  implement, đọc code xác nhận `fee_bps`/`slippage_bps`/`funding_rate_bps` đều
  tính theo % (tỷ lệ), không phải USD cố định/trade — tăng size KHÔNG đổi tỷ
  lệ cost/profit, đề xuất gốc sai kỹ thuật. Test lại 2 candidate daily-bar với
  dữ liệu mới: win rate khớp gần y hệt log gốc nhưng PF giờ chỉ 0.84-1.25
  (marginal, không còn rõ ràng >1 như trước). Đóng cả 2 hướng, không implement
  gì (dừng lại trước khi lãng phí công sức). Chi tiết
  `round71-daily-bar-signal-decayed-plus-sizing-fix-corrected.md`.

  Cũng review thêm 2 hạng mục Verify cũ: chuyển "BTC Portfolio initial_flat/
  weight dilution" sang Done (xác nhận độc lập qua nhiều round tích luỹ —
  Round 64/68 đã đọc `strategy_weights` thật nhiều lần, khớp claim gốc).

- **[Trading][research closed, round 72 `/loop`, 2026-08-21] Order-flow
  imbalance (taker buy/sell ratio) — chiều dữ liệu mới, implement + backtest
  + đóng ngay trong round:** `Kline.taker_buy_volume` có sẵn trên mọi nến
  nhưng chưa strategy nào từng đọc (verify bằng grep). Thêm
  `TakerImbalanceStrategy` (theo hướng lệch mua/bán) +
  `TakerImbalanceFadeStrategy` (ngược lại, coi lệch cực đoan là kiệt sức sắp
  đảo chiều) vào `finance-research/src/strategies.rs` (research-only), build
  + test qua Docker (32/32 pass, fmt sạch). Backtest thật (5 năm, BTC+XAU/
  binance): **cả 2 hướng đều thua lỗ nặng nhất quán** (BTC win 14.6-24.5%,
  XAU chỉ 6.1-8.5%) — đáng chú ý là 2 hướng KHÔNG bù trừ cho nhau (nếu chỉ
  "chọn sai hướng" thì đảo lại phải ~100% win), nghĩa là nhiễu chi phối ở
  5m, không phải edge 1 chiều thật. Đóng candidate, cập nhật comment code.
  Commit `983ea1c`, push. **[Verified 2026-08-21T13:18Z]** CI xanh, workflow
  tự phân loại đúng `deploy=false` (chỉ đổi `finance-research`, không đụng
  `finance-strategy`/`finance-api`) — không deploy, production không đổi,
  không cần verify SSH. Chi tiết
  `round72-taker-order-flow-imbalance-implemented-and-closed.md`.

- **[Trading][research closed, round 73 `/loop`, 2026-08-21] Trend-filter
  order-flow imbalance — gần đạt nhất cho chiều dữ liệu này, vẫn chưa đủ:**
  Bọc `TakerImbalanceStrategy`/`TakerImbalanceFadeStrategy` (Round 72) trong
  đúng `MultiTimeframeTrendFilterStrategy` mọi candidate khác dùng
  (SMA10, higher=4h). PF cải thiện MẠNH trên BTC nhờ filter (0.19-0.29 plain
  → 0.69-0.91 có filter, cả 3 split) — xác nhận trend filter cũng giúp được
  chiều order-flow, nhưng vẫn <1 nhất quán. XAU cho dạng overfit ngược
  (train PF 1.48-1.80 sụp xuống 0.59-0.74 validation/holdout) — đáng ngờ
  tương đương pattern "yếu train mạnh dần" đã phủ định trước đây, chỉ khác
  hướng. Đóng candidate, cập nhật comment code, không log task implement
  (chưa đạt bar). Commit `8249bcd`, push. **[Verified 2026-08-21T13:31Z]** CI
  xanh, `build-and-push`/`deploy-app` skip đúng như dự đoán (research-only,
  không đụng `finance-strategy`) — production không đổi, không cần verify
  SSH. Chi tiết `round73-mtf-taker-imbalance-closest-miss-not-promotable.md`.

- **[Trading][review, round 74 `/loop`, 2026-08-21] Production health sweep +
  dọn 2 hạng mục Verify cũ:** Sau 4 round research liên tiếp (70-73), chuyển
  vai trò reviewer. Đọc cả 4 checkpoint: tất cả healthy, `eval_count` tăng
  bình thường, nhưng `trade_count` gần như đứng yên ở cả 4 route so với
  baseline Round 65 (kể cả Exness/BTC, route eval_count cao nhất) — có vẻ thị
  trường đang ít tín hiệu trên diện rộng, không phải bug 1 route riêng lẻ.
  Không phát hiện bug mới. Chuyển 2 hạng mục Verify cũ (VWAP/ORB
  research-only, Kline alerts resolved) sang Done — cả 2 đều được corroborate
  bởi kết quả độc lập của chính chương trình `/loop` này (Round 18/34 cho
  VWAP/ORB; 70+ round giám sát checkpoint chưa từng thấy
  `input_continuity_failed` cho Binance cho item kia). Còn 2 hạng mục Trading
  chưa review (Kafka access — phạm vi hạ tầng lớn; Web zero-values — cần API
  auth chưa setup), để lại round sau. Chi tiết
  `round74-production-health-sweep-plus-verify-cleanup.md`.

- **[Trading][research closed, round 75 `/loop`, 2026-08-21] Order-flow MTF
  với higher_interval=1d — pattern đáng ngờ lặp lại nhưng mẫu quá mỏng:**
  Thử `--higher-timeframe-interval 1d` (chưa từng biến thiên trong 74 round
  trước, luôn cố định 4h) cho candidate Round 73. BTC: PF>1 ở
  validation/holdout, lặp lại nhất quán trên CẢ 2 window độc lập (5 năm và
  18 tháng) — nhưng holdout window 18 tháng chỉ 16 trade, dưới ngưỡng tin
  cậy tối thiểu. XAU thất bại hoàn toàn (chỉ 15-18 trade/split cả 5 năm,
  filter 1d quá chặt ở base 5m). Đóng — mẫu quá mỏng để tin dù pattern lặp
  lại, và fail cross-instrument rõ ràng. Commit `e19fddf` (comment-only),
  push. **[Verified 2026-08-21T14:00Z]** CI xanh, `build-and-push`/`deploy-app`
  skip đúng dự đoán (research-only) — production không đổi. Chi tiết
  `round75-taker-imbalance-1d-filter-rejected-thin-sample.md`.

- **[Trading][research, round 77-78 `/loop`, 2026-08-21] Kafka ACL re-verify
  an toàn (round 77) + sweep base interval 15m/30m cho XAU (round 78):**
  Round 77 xác nhận lại 2 thuộc tính bảo mật quan trọng nhất của Kafka
  `research-replay-ro` bằng phương pháp an toàn (không dump env) sau sự cố
  Round 76 — port chỉ bind localhost, `research-replay-ro` không phải
  super-user. Round 78 quét XAU ở base interval 15m/30m (chưa từng test kỹ
  trước đây, khác BTC-focused Round 19/24): `ema_crossover_12_26` @ 30m là
  candidate ổn định nhất từng thấy cho CẢ BTC lẫn XAU (PF 0.77-0.97, không
  giật cục giữa các split) nhưng vẫn <1 mọi nơi — ghi nhận làm điểm neo, chưa
  đạt bar promote. Không log task implement. Chi tiết
  `round78-alternate-base-interval-sweep-xau-btc-closest-yet.md`.

- **[Trading][research closed, round 79 `/loop`, 2026-08-21] Trend-filter
  hoá Round 78's `ema_crossover_12_26` — pattern đảo hoàn toàn giữa 2 window,
  đóng:** Bọc candidate ổn định nhất từng tìm (Round 78) trong trend filter
  chuẩn. BTC 5yr: PF dạng lõm giữa (1.19/0.90/1.82, mẫu đủ lớn). Test lại
  window độc lập 18 tháng (đúng phương pháp Round 34): pattern đảo HOÀN TOÀN
  thành dạng yếu dần đều (1.78/1.18/0.94) — cùng dấu hiệu bất ổn định đã
  phủ định ORB. XAU: mẫu quá nhỏ (7-14 trade). Đóng cả 2 instrument. Kết
  luận phương pháp luận: gấp đôi trend-following (entry EMA-crossover +
  filter cùng đo xu hướng) không tạo edge, khác hẳn khi filter áp lên
  oscillator/order-flow (2 loại thông tin độc lập). Commit `ddad3c8`, push.
  **[Verified 2026-08-21T15:02Z]** CI xanh, `build-and-push`/`deploy-app`
  skip đúng dự đoán (research-only) — production không đổi. Chi tiết
  `round79-mtf-ema-crossover-regime-unstable-closed.md`.

- **[Trading][P1 — LẦN ĐẦU TIÊN sau 80 round tìm được lever thật, đã triển
  khai production, round 80 `/loop`, 2026-08-21] Nâng
  `DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS` từ 12 lên 36:** Phát hiện quan
  hệ đơn điệu, cross-broker khớp gần y hệt (<1% chênh lệch), confirm qua
  window 18 tháng độc lập: hold càng dài (chờ lâu hơn trước khi đảo chiều vị
  thế) → ít trade nhưng lỗ ít hơn (chi phí đảo chiều không được bù bởi edge
  thật). BTC/binance 5 năm: hold=12 → 5794 trade/-$43.68; hold=36 (mới) →
  3832 trade/-$28.71 (~34% giảm lỗ, ~15/tuần, dư margin so với ngưỡng Target
  3 7/tuần). Đã sửa `crates/finance-core/src/trading_modes.rs` +
  doc-comment giải thích đầy đủ, `cargo test --workspace --exclude
  finance-redis` 32/32 pass, `cargo fmt --check` sạch, `cargo build
  --release -p finance-api` thành công. Commit `efe7854`, push. **[Verified
  2026-08-21T15:40Z]** CI xanh (build-and-push + deploy-app đều chạy thật,
  đúng dự đoán vì đổi `finance-core`). Verify độc lập qua SSH: cả 4 worker
  chạy đúng SHA `efe7854`, healthy. Phát hiện thêm khi verify: hệ thống tự
  động kích hoạt **historical replay lại từ đầu** cho cả 4 route ngay sau
  deploy (đúng thiết kế `continue_forward_from_replay` — khi luật Portfolio
  construction đổi, ledger tính lại từ lịch sử thay vì tiếp tục trạng thái
  cũ dưới luật cũ). Binance BTC/XAU replay xong ngay; Exness BTC/XAU
  `awaiting_replay=True` tạm thời (~10 phút) rồi cũng xong. Kết quả cuối
  cùng sau khi cả 4 route replay xong: **Binance/BTC 750 trade, Exness/BTC
  757 trade — gần khớp nhau (đúng pattern cross-broker đã thấy trong
  backtest)**; Binance/XAU 7 trade (gần như không đổi, đúng dự đoán — hold
  chỉ ảnh hưởng đảo chiều, XAU/binance hiếm khi vào lệnh); Exness/XAU 592
  trade (giảm từ baseline 758 trước deploy, đúng hướng "hold dài hơn → ít
  trade hơn"). Toàn bộ khớp đúng dự đoán từ backtest. **Lưu ý quan trọng:
  đây KHÔNG phải fix hoàn chỉnh** — PF vẫn <1 mọi giá trị hold test được,
  chỉ làm hệ thống thua lỗ chậm hơn/rẻ hơn, chưa biến lỗ thành lời. Theo dõi
  thêm vài ngày tới để xác nhận PnL thực tế cải thiện đúng như backtest dự
  đoán. Chi tiết đầy đủ (bảng số liệu, lý do chọn 36) trong
  `round80-portfolio-minimum-hold-decisions-raised-12-to-36.md`.

- **[Trading][P2 — lead cần làm rõ trước khi implement, round 81 `/loop`,
  2026-08-21] Đòn bẩy tiềm năng thứ 2 (ATR protective stop) — dừng lại vì
  công cụ đo mơ hồ:** `capital_reports` cho thấy `fixed-atr`/`compounding-atr`
  ít lỗ hơn ~15-17% so với `fixed-pct`/`compounding-pct` đang live. Nhưng
  verify phát hiện: nhánh so sánh này **không phản ánh
  `--portfolio-minimum-hold-decisions`** (số liệu giống hệt ở hold=12 và
  hold=36 — đọc code xác nhận `replay_portfolio_decisions` không nhận tham
  số này, chỉ nhánh `one_target`/`legacy_selected_rule` dùng cho kết luận
  Round 80 mới thực sự áp dụng). **Chủ động KHÔNG implement** vì chưa rõ
  `capital_reports` đang đo dưới giả định hold-period nào — tránh lặp lại
  kiểu sai lầm phương pháp luận. Cần Codex hoặc round sau đọc kỹ
  `portfolio_measurement.rs`/`replay_portfolio_decisions` để làm rõ trước
  khi cân nhắc ATR-stop. Chi tiết
  `round81-atr-protective-stop-lead-tool-ambiguity-found.md`.

  **[Claude round 82 `/loop`, 2026-08-21 — giải quyết dứt điểm, đóng]** Đọc
  code xác nhận `legacy_grid`/`legacy_selected_rule`/`capital_reports` hoàn
  toàn KHÔNG dùng `construction.construct()` (bỏ qua `minimum_holding_decisions`
  hoàn toàn) — verify thực nghiệm (hold=12 vs hold=100 trên window 200 ngày):
  3 field đó y hệt nhau, chỉ `one_target` đổi. Đo lại đúng phương pháp qua
  `--portfolio-protective-kind atr_multiple` trên nhánh `one_target` (tôn
  trọng hold=36 hiện tại): BTC/binance cải thiện (~7.7%) nhưng **BTC/exness
  TỆ HƠN (~7.6%)** — fail cross-broker rõ ràng, gần đối xứng ngược. Đóng hẳn
  ATR-stop, xác nhận Round 80's kết luận (dùng đúng `one_target` từ đầu)
  không bị ảnh hưởng. Chi tiết
  `round82-atr-stop-resolved-and-closed-cross-broker-fail.md`.

- **[Trading][P1 — đòn bẩy Target 1 thật THỨ 2, đã triển khai production,
  round 83 `/loop`, 2026-08-21] Nới `PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE`
  từ 0.005/0.010 lên 0.01/0.02:** Áp đúng phương pháp `one_target` (đã xác
  nhận đáng tin ở Round 82) cho tham số Portfolio thứ 2. Cùng cơ chế Round
  80: stop hẹp dễ bị nhiễu quét oan trước khi tín hiệu thật kịp phát triển.
  BTC/binance 5 năm: 0.005/0.010 → -$28.72 (3830 trade); 0.01/0.02 (mới) →
  **-$16.93** (2417 trade, ~41% giảm lỗ, ~9.3/tuần). Cross-broker Exness khớp
  <2% (-$28.36→-$19.18). Confirm window 18 tháng độc lập cùng hướng
  (~56% giảm). Đã sửa `crates/finance-api/src/deployment_rules.rs` (gom
  thành constant `PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE`, dùng chung
  cả 3 rule fixed-pct/risk-2pct/compounding-10pct), `cargo test --workspace
  --exclude finance-redis` 32/32 pass, `cargo fmt --check` sạch, `cargo
  build --release -p finance-api` thành công. Commit `31ed149`, push.
  **[Verified 2026-08-22T04:25Z]** CI xanh, deploy thành công, cả 4 worker
  chạy đúng SHA `31ed149`, healthy 12+ giờ, historical replay đã tự kích
  hoạt lại và hoàn tất trên cả 4 route (đúng thiết kế như Round 80). Kết
  quả post-deploy: Binance/BTC 496 trade, Exness/BTC 506 trade — gần khớp
  nhau như dự đoán. **Lưu ý: vẫn KHÔNG biến lỗ thành lời** — chỉ làm hệ
  thống thua lỗ chậm hơn/rẻ hơn. Kết hợp với Round 80, đây là 2 đòn bẩy
  Portfolio-construction thật đã tìm+triển khai trong 4 round. Chi tiết
  `round83-portfolio-stop-take-widened-second-real-lever.md`.

- **[Trading][P3 — cải thiện tương đối, chưa đủ để fix Target 1, ghi nhận
  làm tham khảo] `candle_momentum_30bps` tốt hơn hẳn `10bps` đang live
  nhưng vẫn thua lỗ (Claude round 57 `/loop`, 2026-08-21):** Sanity-check
  trước: đối chiếu Sharpe -6.73/-6.93 (Round 55-56) với checkpoint thật —
  win rate 350/1126=31.1%, xác nhận con số cực đoan đó là THẬT (thua lỗ nhỏ
  nhưng rất đều đặn mỗi ngày → Sharpe rất âm dù tổng lỗ không lớn), không
  phải bug tính toán. Sau đó test `candle_momentum_30bps` (chưa từng thử,
  bps rộng hơn 10bps đang live) trên BTC/binance 5m: **PF cải thiện rõ rệt
  (0.756 vs 0.347 holdout, win rate 33.7% vs 22.7%)** nhưng vẫn PF<1 cả 3
  split — chưa đủ fix Target 1, nhưng là đòn bẩy cải thiện tương đối thật.
  Đánh đổi: tần suất giảm 87% (1969 vs 15613 trade holdout) — sẽ ảnh hưởng
  Target 3 nếu áp dụng đơn lẻ. Không log task implement (chưa đủ tốt để
  promote) — chỉ ghi nhận làm tham khảo nếu sau này cần tune bps.

  **[Claude round 58 /loop, 2026-08-21 — bằng chứng mạnh hơn cho strategy
  thứ 2 đang live]** Test tương tự cho `rsi_mean_reversion` (config live:
  `14_30_70`): `rsi_mean_reversion_14_20_80` (biên rộng hơn) cho PF tốt hơn
  **NHẤT QUÁN cả 3 split VÀ cả 2 instrument** (BTC: 0.677/0.660/0.625 →
  0.717/0.789/**0.816**, PF còn TĂNG DẦN qua split — không phải artifact
  mẫu nhỏ; XAU: 0.522/0.336/0.271 → 0.680/0.595/0.515) — 6/6 phép so sánh
  cùng hướng, bằng chứng mạnh hơn hẳn `candle_momentum_30bps` ở trên (chỉ
  test 1 instrument). Vẫn PF<1 mọi trường hợp — chưa fix Target 1, tần suất
  giảm 59-65%. **Nếu Codex cân nhắc tune tham số production, đây là ứng
  viên đáng xem xét nhất trong 2** (bằng chứng cross-instrument + nhất quán
  3-split, tần suất giảm ít hơn candle_momentum_30bps) — vẫn cần thêm đòn
  bẩy khác để đạt Target 1 thật sự, không chỉ tuning tham số. Chi tiết
  trong `research/quant/rounds/round58-rsi_14_20_80-consistent-improvement-cross-instrument.md`.

- **[Trading][P1 — số liệu THẬT đầu tiên qua engine đúng, không phải task
  bug, ghi nhận quan trọng] Round 55: Portfolio production BTC/binance
  Sharpe -6.73 thật, XAU/binance gần như không ra quyết định (Claude round
  55 `/loop`, 2026-08-21, tự build lại `finance-research` sau các fix Round
  54 và verify):** Sau khi Codex xoá `--gate-strategy` và đổi
  `--daily-profit-gate` thành đánh giá đúng Portfolio production hiện tại
  (không phải candidate tuỳ ý), Claude chạy lại lệnh mới cho cả BTC lẫn XAU
  binance (5m, đúng interval production). **BTC: fail 6/9 check, Sharpe
  -6.73, Sortino -6.69, net PnL holdout -$13.39, positive_day_ratio 37.7%.
  XAU: fail 8/9 check kể cả `minimum_trades_per_week` mới, observed_days
  chỉ 51/366, positive_day_ratio 0%.** Đây là số liệu thẩm quyền nhất từ
  trước tới giờ (qua đúng `PortfolioDecisionPolicy` thật, không phải
  backtest tay/simplified mapper) xác nhận Target 1 (BTC) và Target 2 (XAU)
  đều chưa đạt rõ ràng. Không phải bug — đúng bản chất production hiện tại.
  Cũng xác nhận Codex đã thêm `minimum_trades_per_week` vào gate (đúng đề
  xuất tool-gap Round 17). Chi tiết đầy đủ trong
  `research/quant/rounds/round55-real-production-gate-and-tool-overhaul.md`.
  **Lưu ý cho ai research tiếp:** `--gate-strategy` không còn tồn tại,
  `--weighted-ensemble-gate` hardcode 1 tổ hợp cụ thể — muốn test extended
  metrics (Sharpe/Sortino/streak) cho candidate/ensemble MỚI qua engine
  thật cần công cụ tổng quát hơn (đề xuất nhỏ, không khẩn).

- **[Trading][meta, không phải task riêng] Tổng hợp ưu tiên chương trình
  Quant Research `/loop` (Claude round 39, cập nhật toàn diện round 50,
  2026-08-20):** `research/quant/index.md` — đọc file
  này trước nếu muốn bắt đầu implement bất kỳ item Trading nào ở dưới,
  tránh phải đọc lại toàn bộ 50 file rải rác. Liệt kê: hướng có triển vọng
  nhất hiện tại (ensemble regime-switching — Funding Rate đã tự đóng vòng
  patch, chỉ còn hợp lệ nếu gộp chung), danh sách đã đóng/phủ định (11 mục,
  tránh test lại), gap hạ tầng đang chặn verify chính xác hơn, và trạng
  thái Target 2 (vẫn stagnant qua mọi lần đo).

  **[Research context for the active ensemble task — đề xuất mới, có bằng chứng số liệu 3/3 mẫu độc lập, chưa
  implement] 3 candidate swing 4h/1d (baseline sma50, ADX-filtered,
  macd_5_13_5) thất bại ở 3 cửa sổ thời gian HOÀN TOÀN KHÁC NHAU — bằng
  chứng ủng hộ hướng ensemble/regime-switching thay vì tìm 1 filter tốt
  nhất (Claude round 36 `/loop`, 2026-08-20, phân tích `daily_results` thật,
  không backtest candidate mới):** streak tệ nhất của mỗi candidate:
  baseline (sma50) → 2026-04-12→05-29 (48 ngày); ADX-filtered →
  2025-09-05→11-09 (66 ngày); macd_5_13_5_sma10 → 2026-07 (chỉ 25 ngày) — 3
  cửa sổ không trùng nhau. Đáng chú ý nhất: **macd_5_13_5_sma10 có PnL DƯƠNG
  (+0.28) đúng ở cửa sổ mà baseline lỗ nặng nhất (48/48 ngày âm)**. Đây là
  mẫu 3/3 độc lập, không phải trùng hợp thống kê với mẫu quá nhỏ.

  **Đề xuất rẻ nhất, không cần code switching mới:** đăng ký 2-3 biến thể
  MTF này (baseline/ADX-filtered/macd) làm các Alpha strategy riêng biệt
  trong hệ thống hiện có, để `reweight_from_alpha_performance` (đã live,
  `trading_modes.rs:455-491`) tự động dịch trọng số theo hiệu suất gần đây
  — cơ chế này ĐÃ TỒN TẠI, không cần thiết kế regime-detector mới. Nếu cách
  này không đủ nhạy (vì cơ chế reweight hiện dùng cửa sổ dài, có thể phản
  ứng chậm với đổi regime), mới cần tính tới thiết kế switching chuyên biệt
  hơn. Chi tiết đầy đủ trong
  `research/quant/rounds/round36-complementary-regime-sensitivity-baseline-vs-adx.md`.
  Còn thiếu 1 candidate Round 17 chưa test đủ (`candle_momentum_10bps_sma10`)
  — nên hoàn thiện trước khi quyết định implement.

  **[Claude round 37 /loop, 2026-08-20 — đã hoàn thiện candidate thứ 4, kết
  luận vẫn đứng vững nhưng cần điều chỉnh trung thực]** Test nốt
  `candle_momentum_10bps_sma10`: streak tệ nhất của chính nó là
  2025-09-03→09-19 (17 ngày, NGẮN NHẤT trong 4 candidate) — nhưng **trùng
  lấp một phần** với cửa sổ tệ nhất của ADX-filtered (2025-09-05→11-09).
  Không còn là "3/3 cửa sổ hoàn toàn tách biệt" như bản nháp round 36, mà là
  **3 cửa sổ chính tách biệt rõ (Apr-May 2026 / Jul 2026 / cụm Sep-Nov
  2025)**, trong đó cụm Sep-Nov có 2 candidate cùng khó nhưng mức độ khác
  hẳn (17 ngày nhẹ vs 66 ngày nặng). Kết luận tổng thể (mỗi filter có điểm
  mù riêng, kết hợp giảm rủi ro tệ nhất) vẫn đứng vững, nhưng độ độc lập
  giữa các cửa sổ không hoàn hảo 100% — đã cập nhật lại
  `research/quant/rounds/round36-complementary-regime-sensitivity-baseline-vs-adx.md`
  để không phóng đại bằng chứng. Đề xuất "thử `reweight_from_alpha_performance`
  tự chọn trước" ở trên vẫn giữ nguyên.

  **[Claude round 38 /loop, 2026-08-20 — SỬA LẠI đề xuất "rẻ nhất" ở trên,
  đã tự kiểm tra code trước khi đề xuất tiếp]** Đọc kỹ
  `reweight_from_alpha_performance` (`trading_modes.rs:458-497`) và
  `SimulatedPerformance` struct (`trading_modes.rs:1436-1451`): **toàn bộ
  field dùng để tính quality score (`realized_pnl`, `gross_profit`,
  `gross_loss`, `trade_count`, `win_count`, `max_drawdown`...) đều là bộ đếm
  CỘNG DỒN TOÀN THỜI GIAN kể từ khi ledger bắt đầu, không có field
  windowing/decay/rolling-recent nào cả** (chỉ có `consecutive_losses` là
  streak hiện tại, nhưng không dùng trong `alpha_performance_quality`).
  **Nghĩa là đề xuất "rẻ nhất" ở trên (chỉ đăng ký làm Alpha strategy riêng,
  để reweight tự chọn) RẤT CÓ THỂ KHÔNG hoạt động như kỳ vọng** — 1 strategy
  có lịch sử tốt nhiều năm sẽ gần như không bị giảm trọng số dù vừa trải qua
  1 giai đoạn tệ vài tháng (điểm quality bị pha loãng bởi lịch sử dài), tức
  cơ chế này được thiết kế để thưởng sự nhất quán dài hạn, KHÔNG phải để
  phản ứng nhanh theo regime tháng — ngược hoàn toàn với nhu cầu của đề xuất
  Round 36-37 (cần phản ứng theo tháng, không phải theo năm). **Rút lại
  khuyến nghị "thử cái này trước"** — nếu muốn theo đuổi ý tưởng ensemble/
  regime-switching, cần 1 cơ chế reweighting MỚI có cửa sổ gần đây (rolling
  window hoặc EWMA decay) thay vì dùng lại `reweight_from_alpha_performance`
  nguyên bản. Đây là code mới thật sự, không phải config/registration đơn
  giản như đã tưởng.

  **[NÂNG MỨC TIN CẬY MẠNH — Claude round 51 /loop, 2026-08-20, proof-of-
  concept backtest thật, không chỉ suy luận nữa]** Tự dựng equal-weight
  ensemble (trung bình cộng đơn giản `return_fraction` mỗi ngày của cả 4
  candidate, KHÔNG cần trọng số động/regime-detector) từ `daily_results`
  thật của `finance-research`. **Kết quả: Sharpe ensemble = 1.475, CAO HƠN
  candidate tốt nhất đứng riêng (ADX, 1.368)** — không phải trung bình cộng
  của 4 Sharpe (~0.77), mà cao hơn cả từng candidate. **Max negative streak
  giảm từ 48-66 ngày (candidate riêng lẻ) xuống còn 15 ngày** (-66% đến
  -77%). Chưa clear hết gate (`positive_day_ratio` 49.2% < 55%, streak 15 >
  ngưỡng 5) nhưng tiến bộ rõ ràng, đo được bằng số cụ thể. **Đề xuất bước 1
  rẻ hơn hẳn bản gốc:** implement 1 Portfolio decision rule mới kết hợp
  entry_score nhiều Alpha variant bằng **trung bình cộng đơn giản trước**
  (không cần rolling-window/EWMA reweighting phức tạp đã đề xuất ở trên),
  test qua `finance-research` xác nhận lại kết quả tương tự trước khi nâng
  cấp lên trọng số động. Chi tiết đầy đủ trong
  `research/quant/rounds/round51-ensemble-proof-of-concept-major-improvement.md`.

  **[Claude round 52 /loop, 2026-08-20 — tìm được tổ hợp ĐẦU TIÊN pass được
  1 gate check thật]** Test thêm các tổ hợp subset (không chỉ cả 4 cùng
  trọng số). **Tổ hợp 2 candidate mạnh nhất (baseline sma50 + ADX-filtered)
  đạt `positive_day_ratio` = 59.6% — PASS ngưỡng 55%, lần đầu tiên trong
  toàn bộ 52 round có bất kỳ tổ hợp/candidate nào pass được check này.**
  Sharpe 1.780, Sortino 5.448 — cao hơn cả ensemble 4-candidate. Đổi lại
  streak vẫn 48 ngày (không cải thiện). **Trade-off thật giữa các tổ hợp**:
  2-combo tốt nhất về Sharpe/Sortino/pos-day-ratio nhưng tệ nhất về streak;
  4-combo (Round 51) tốt nhất về streak (15 ngày) nhưng chất lượng tổng
  thể thấp hơn. Không có tổ hợp nào pass cả 2 tiêu chí cùng lúc, nhưng đều
  gần target hơn hẳn candidate đơn lẻ. Đề xuất bổ sung: khi implement, nên
  thử nghiệm nhiều tổ hợp subset (không cố định "tất cả candidate cùng
  trọng số"), có thể cần 1 bước chọn tổ hợp tối ưu trước khi cố định trọng
  số. Chi tiết trong file trên, mục "Cập nhật Round 52".

  **[Claude round 53 /loop, 2026-08-20 — tìm trọng số cân bằng tốt hơn]**
  Dò thêm trọng số không đều (không chỉ equal-weight hay drop hẳn 1
  candidate). **Kết quả tốt nhất: 50/30/20 (baseline/ADX/candle_momentum,
  bỏ macd)** — pass `positive_day_ratio` (57.1%), Sharpe 1.703, Sortino
  4.667, streak giảm còn **21 ngày** (từ 48 ngày, -56%) dù chưa pass ngưỡng
  gate (≤5). Đây là điểm cân bằng tốt nhất tìm được: vừa pass 1 gate check
  thật vừa cải thiện streak đáng kể hơn hẳn phương án 2-combo thuần (streak
  vẫn 48). **Khuyến nghị: nếu chọn 1 tổ hợp để implement thử nghiệm đầu
  tiên, dùng 50/30/20 (3 trọng số cố định, không cần trọng số động).** Đây
  vẫn là tìm kiếm tay giới hạn (11 tổ hợp tổng cộng round 52-53) — Codex có
  thể tìm điểm tốt hơn nếu chạy grid-search đầy đủ qua `finance-research`.

- **[Trading][P2 — đề xuất signal mới từ web research, chưa implement, cần
  code mới thật sự] Funding Rate Extreme Reversion — signal đặc thù crypto
  chưa từng thử trong chương trình research này (Claude round 22 `/loop`,
  2026-08-20, theo Rule 2 dùng WebSearch tìm chiến thuật mới):** Nghiên cứu
  web xác nhận funding rate cực trị (BTC >0.10%/8h) thường đi trước 1 đợt
  đảo chiều giá thật (vị thế đông đúc/leverage cao, không phải nhân quả trực
  tiếp) — signal hoàn toàn khác cơ chế mọi candidate đã test (momentum/mean-
  reversion/trend-filter/session, toàn bộ dựa OHLCV). Đọc code xác nhận:
  `Strategy::evaluate()` (`finance-strategy/src/engine.rs:16`) chỉ nhận
  `Kline`, không có funding rate; nhưng `FundingSettlement`
  (`finance-core/src/broker_pnl.rs:103-113`, có `rate_fraction` ký hiệu thật)
  và `--actual-funding-broker` (fetch funding thật qua venue adapter, không
  giả lập) đã tồn tại sẵn cho mục đích tính cost — **chưa wire vào tầng
  signal**, đúng pattern "machinery có sẵn, chưa nối" đã gặp nhiều lần trong
  chương trình này. Đề xuất: 1 wrapper strategy mới (theo đúng pattern
  composition của `MultiTimeframeTrendFilterStrategy`) dùng funding cực trị
  làm **filter hướng** cho 1 entry signal có sẵn (không tự làm entry đơn độc
  — tránh lặp lại lỗi VWAP Round 18/21: win rate cao nhưng R:R tệ khi dùng
  đơn độc), chỉ áp dụng instrument có funding perpetual thật (BTC/binance,
  XAU/binance — KHÔNG Exness CFD, dùng `SwapSettlement` khác cơ chế). Chi
  tiết đầy đủ + nguồn trích dẫn trong
  `research/quant/rounds/round22-funding-rate-extreme-reversion-proposal.md`. Chưa
  có số liệu backtest vì signal chưa tồn tại trong code — không tự bịa số.

  **[NÂNG ƯU TIÊN — Claude round 42 /loop, 2026-08-20, đã tự validate giả
  thuyết bằng dữ liệu bên ngoài THẬT trước khi đề xuất Codex code]** Không
  chờ hạ tầng nội bộ — tự fetch trực tiếp public API
  `https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000`
  (không cần auth, 500 bản ghi thật, ~5.5 tháng), tính forward return giá
  sau funding cực trị (percentile 10/90). **Kết quả xác nhận đúng hướng giả
  thuyết:** funding cực dương (long đông) → giá giảm trung bình **-1.8%**
  sau 1 tuần; funding cực âm (short đông) → giá tăng **+1.4%** sau 1 tuần —
  lệch ngược dấu rõ rệt so với baseline gần 0%, đúng chữ ký mean-reversion
  (không phải market drift chung, vì 2 nhóm lệch ngược nhau chứ không cùng
  dấu). Mẫu 44-51 quan sát/nhóm — chưa phải thống kê chặt chẽ nhưng pattern
  nhất quán, tăng dần theo thời gian holding (K=1→21 kỳ). **Đây là hướng có
  bằng chứng thực nghiệm mạnh nhất trong toàn bộ backlog hiện tại — khuyến
  nghị ưu tiên implement trước các đề xuất khác (ensemble regime-switching
  vẫn cần thiết kế thêm).** Chi tiết đầy đủ + giới hạn trung thực trong
  `research/quant/rounds/round42-funding-rate-hypothesis-validated-external-data.md`.

  **[SỬA LẠI PHẠM VI — Claude round 43 /loop, 2026-08-20, đã test thêm
  XAU/binance như đã hứa]** Fetch thêm `fundingRate?symbol=XAUUSDT&limit=1000`
  (public, 500 bản ghi thật): **KHÔNG transfer sang XAU, thậm chí NGƯỢC DẤU
  hoàn toàn với BTC** — funding cực dương ở XAU đi kèm giá TIẾP TỤC TĂNG
  (+1.9% sau ~84h), trái ngược BTC (giá giảm -1.8% sau 168h). Thêm nữa,
  63.4% bản ghi funding XAU = 0 chính xác và chưa từng có funding ÂM trong
  toàn mẫu — thị trường quá mỏng/không đối xứng để tin cậy theo bất kỳ
  hướng nào. **Sửa lại phạm vi đề xuất: CHỈ áp dụng cho BTC/binance, KHÔNG
  mở rộng sang XAU/binance** như bản gốc Round 22 từng ghi — đúng Rule 4
  của user (mỗi token cần setup riêng, không suy diễn từ token này sang
  token khác).

  **[HẠ MỨC ƯU TIÊN LẠI — Claude round 44 /loop, 2026-08-20, out-of-sample
  test theo đúng tinh thần honest-holdout đã dùng xuyên suốt chương trình
  này]** Test thêm 2 cửa sổ lịch sử BTC độc lập (2024 H1, 2025 H1, cùng
  `fundingRate` API, dùng `startTime`/`endTime`). **Chỉ 2/3 cửa sổ khớp
  hướng dự đoán** — 2025 H1 khớp tốt (HIGH funding → -1.6%/tuần, LOW → +1.2%
  /tuần, đúng hướng Round 42), nhưng **2024 H1 SAI HƯỚNG hoàn toàn** (HIGH
  funding → +2.5%/tuần). Nhìn kỹ: 2024 H1 là giai đoạn BTC trend tăng rất
  mạnh (baseline toàn kỳ đã +1.6%/tuần, gấp ~10 lần 2 cửa sổ kia) — dấu hiệu
  điển hình "mean-reversion bị lấn át bởi trend mạnh kéo dài", KHÔNG phải
  giả thuyết sai hoàn toàn. **Rút lại khuyến nghị "ưu tiên implement ngay"
  ở round 42-43** — đề xuất mới: nếu implement, PHẢI kết hợp với 1 regime/
  trend filter (chỉ áp dụng funding-reversion khi không có trend mạnh áp
  đảo), không nên dùng như 1 signal đứng độc lập. Đây thực chất là cùng 1
  nhóm vấn đề với đề xuất ensemble/regime-switching Round 36-38 (mọi signal
  đơn lẻ đều có điểm mù theo regime) — nên cân nhắc thiết kế chung 1 cơ chế
  regime-detection cho cả 2 đề xuất thay vì làm riêng lẻ. Chi tiết đầy đủ
  trong `research/quant/rounds/round42-funding-rate-hypothesis-validated-external-data.md`
  mục "Cập nhật Round 44".

  **[Claude round 45 /loop, 2026-08-20 — đã tự test luôn ý tưởng "trend
  filter" trước khi đề xuất Codex làm]** Test filter đơn giản nhất: loại
  bỏ thời điểm |biến động giá 9 kỳ gần nhất| >= 3%. **Kết quả HỖN HỢP, không
  giải quyết được vấn đề:** cải thiện ở 2025 H1 và 1 vế của 2026, nhưng
  **KHÔNG cứu được 2024 H1** (vẫn sai hướng cả 2 vế) và làm YẾU ĐI vế HIGH
  của 2026. Kết luận: lọc theo biên độ trend đơn giản không đủ — vấn đề có
  thể liên quan hướng trend so với dấu funding (phức tạp hơn), không phải
  chỉ "đang biến động mạnh hay không". **Không đề xuất Codex implement
  filter biên độ đơn giản kiểu này** — nếu muốn tiếp tục hướng funding-
  reversion, cần regime-detector tinh vi hơn, hoặc ưu tiên hướng ensemble
  đa-signal (Round 36-38) thay vì cố sửa 1 signal đơn lẻ.

  **[ĐÓNG hướng patch filter đơn giản — Claude round 46 /loop, 2026-08-20]**
  Test thêm cách chia thứ 2: funding cực trị + hướng trend AGREE (cùng
  hướng, "cưỡi trend") vs DISAGREE (funding trễ, giá đã đảo hướng). Kết quả
  **KHÔNG nhất quán giữa các cửa sổ** — 2025 H1 cho AGREE phản ứng mạnh hơn
  DISAGREE, nhưng 2026 lại cho ngược lại hoàn toàn (DISAGREE mạnh hơn hẳn);
  2024 H1 vẫn sai hướng ở cả 2 nhóm. Đã thử 2 cách filter khác nhau (biên
  độ Round 45, hướng Round 46) — cả 2 đều không nhất quán đủ để tin cậy.
  **Kết luận cuối: đóng hướng patch filter rule-based đơn giản cho signal
  này** — không đề xuất Codex tốn thêm thời gian test filter kiểu này nữa.
  Nếu muốn dùng funding-reversion, nên đưa vào ensemble đa-signal (Round
  36-38, để trọng số tự điều chỉnh) thay vì cố tìm 1 rule filter cứng.

- **[Trading][P2 — đề xuất kiến trúc mới, chưa implement, số liệu thật kèm
  theo] Swing 4h/1d family: đã quét thêm 3 candidate regime-filter/entry
  khác nhau (Claude research 2026-08-20, round 17 `/loop`, dùng backtest
  thật qua `finance-research --daily-profit-gate` với extended metrics tự
  tính từ `daily_results` thật — không tự implement, đúng scope session này
  chỉ explore/optimize):** cùng khung 4h base + 1d higher-tf như candidate
  Round 14/16 (`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, Sharpe 1.13/
  Sortino 3.10 dương thật nhưng streak 48 ngày + tần suất 0.35 lần/tuần chặn
  target), test thêm 3 candidate khác cùng timescale (chưa ai test ở 4h/1d
  trước round này): `mtf_candle_momentum_10bps_sma10_trend_filtered` (momentum
  entry, sma10 filter nhanh hơn), `mtf_macd_5_13_5_sma10_trend_filtered`
  (MACD crossover entry), `mtf_stochastic_14_3_35_65_adx14_20_sma10_trend_filtered`
  (ADX(14)<20 ranging-regime gate chồng lên stochastic core). Đầy đủ bảng số
  liệu (trades/win%/PF/Sharpe/Sortino/Ulcer Index/skew/kurtosis/max losing-day
  streak/max drawdown duration/tần suất) trong
  `research/quant/rounds/round17-swing-4h1d-regime-filter-family.md` và
  `research/quant/reports/optimize_loop_update_v2.csv`.

  **Kết luận định lượng, không phải giả thuyết:** cả 4 candidate (từ "giao
  dịch nhiều nhất, edge yếu nhất" tới "giao dịch ít nhất, edge mạnh nhất")
  đều KHÔNG đạt đồng thời cả chất lượng lẫn tần suất — đây là trade-off cấu
  trúc thật (filter trend càng lỏng, tần suất tăng nhưng Sharpe/Ulcer/PF đều
  xấu đi rõ rệt; filter càng chặt/ADX-gated thì Sharpe/Sortino/Ulcer tốt nhất
  cả chương trình (1.37/4.61/0.0022) nhưng tần suất còn thấp hơn cả baseline
  (0.21 lần/tuần) và streak dài hơn (66 ngày). Không phải 1 tham số chỉnh sai
  — 4 cơ chế entry/filter khác hẳn nhau cùng hội tụ về 1 trần tần suất giống
  nhau ở khung 4h/1d.

  **Đề xuất kiến trúc (chưa implement, cần code mới thật sự, không phải sweep
  tham số):** dùng hướng đi swing 4h/1d làm **bias/gate hướng** cho tín hiệu
  5m tần suất cao đang live (`candle_momentum`, `rsi_mean_reversion`) thay vì
  để swing tự làm entry signal riêng — chỉ cho phép entry 5m khi cùng hướng
  với trend 1d, để tầng 5m cung cấp số lần trade còn tầng swing cung cấp chất
  lượng hướng. Đây là `StrategyKind`/decision-policy mới, không phải chỉnh
  tham số — cần Codex tự thiết kế nếu muốn theo đuổi. Hướng thay thế đơn giản
  hơn (không cần code mới): chấp nhận swing là 1 frequency-bucket riêng với
  target tần suất thấp hơn (như Round 14 đã đề xuất), tách khỏi target chung
  7 lần/tuần.

  **[Claude làm rõ round 19 `/loop`, 2026-08-20 — QUAN TRỌNG, tránh implement
  nhầm hướng]** Đã tự test naive version của đề xuất trên bằng cơ chế
  `--higher-timeframe-interval` có sẵn (không cần code mới): base=5m,
  higher-tf=1d, BTC/binance, dùng lại chính oscillator swing
  `mtf_stochastic_14_3_30_70_sma50_trend_filtered` ở base interval nhỏ hơn.
  **Kết quả: đổi base 4h→5m (nhỏ hơn 48 lần) chỉ tăng tần suất 0.34→0.55
  lần/tuần (+61%, không tuyến tính) trong khi MỌI metric chất lượng xấu đi**
  (Sharpe 1.13→0.71, Sortino 3.10→2.02, win rate 50.0%→13.8%). Đọc code
  `MultiTimeframeTrendFilterStrategy::evaluate` (`strategies.rs:1089-1130`)
  xác nhận: higher-tf filter chỉ là cổng boolean, trần tần suất nằm ở tần
  suất raw của chính inner oscillator — không scale theo độ mịn nến base
  interval như kỳ vọng ban đầu. Chi tiết đầy đủ trong
  `research/quant/rounds/round19-mtf-frequency-bottleneck-mechanism.md`.

  **Ý nghĩa: nếu triển khai đề xuất trên, inner strategy PHẢI là
  `candle_momentum`/`rsi_mean_reversion` đang live thật (2 strategy tần suất
  cao đã biết fire nhiều trên production), KHÔNG được dùng lại 1 oscillator
  swing-scale (stochastic/MACD/RSI kiểu đã test ở Round 17-19) chỉ vì đổi
  base interval nhỏ hơn — hướng đó đã tự test và bị bác bỏ bằng data thật,
  không cần code lại để xác nhận thêm lần nữa.**

  **[Claude round 35 /loop, 2026-08-20 — case study cụ thể cho streak 48
  ngày]** Xác định chính xác chuỗi lỗ 48 ngày của candidate baseline
  (`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, BTC 4h/1d) là
  **2026-04-12 → 2026-05-29**, xác nhận cross-broker (Exness BTC/USD cùng
  cửa sổ cũng 48/48 ngày âm) — sự kiện thị trường BTC thật, không phải
  artifact dữ liệu. Nếu sau này thiết kế regime-filter mới cho candidate
  này, nên test cụ thể filter đó có tránh được đúng 48 ngày này không, thay
  vì chỉ nhìn tổng thể streak toàn kỳ. Chi tiết trong
  `research/quant/rounds/round35-losing-streak-dates-pinpointed.md`.

- **[Observability][P3] `1m` kline chỉ lưu ~4.4 ngày — không đủ backtest
  walk-forward, cần quyết định có mở rộng retention hay không (Claude phát
  hiện 2026-08-20T19:xx ICT, trong lúc research theo Rule 5 — web/reddit/
  tiktok/paper, không tự implement):** Test ý tưởng "gold RSI scalping 1
  phút" (retail strategy phổ biến, RSI 14/30/70, TP/SL cố định ~1:2 R:R,
  báo cáo win rate 55-65%) — candidate đã có sẵn code
  (`rsi_mean_reversion_14_30_70`), chỉ cần `--interval 1m`. Nhưng
  `finance-research --interval 1m` trả về đúng **6,353 nến (~4.4 ngày
  thật)** bất kể `--days` yêu cầu 30 hay 365 — xác nhận giống hệt cho cả
  XAU lẫn BTC. Holdout window chưa tới 1 ngày — không đủ để backtest
  walk-forward đáng tin, không tự bịa số liệu từ mẫu quá nhỏ. Khớp với
  thực tế đã biết: `1m` không nằm trong `EVALUATED_INTERVALS` của live
  evaluation — có vẻ retention 1m vốn thiết kế ngắn (đủ cho chart, không
  đủ cho backtest). **Nếu muốn theo đuổi hướng scalping 1 phút thật sự,
  cần quyết định có mở rộng retention `1m` hay không trước** — đây là

  **[Claude round 27 /loop, 2026-08-20 — lý do mới, mạnh hơn hẳn để giải
  quyết prerequisite này]** Research sâu ý tưởng ICT liquidity-sweep/FVG
  (mục Todo khác cùng file) tìm được bằng chứng học thuật thật: backtest FVG
  ở granularity 5m/15m/1h cho win rate ảo ~73%, nhưng khi resolve đúng ở
  granularity 1 phút (thứ tự trader thật trải nghiệm) thì rơi xuống ~50% —
  toàn bộ edge là lookahead artifact, cùng loại lỗi đã tìm thấy trong chính
  MTF kline merge của hệ thống này (win rate ảo 69-97% → thật 27-30%). Ý
  nghĩa: retention `1m` ngắn không chỉ chặn ý tưởng scalping RSI cũ, mà còn
  chặn khả năng test honest bất kỳ strategy nào phụ thuộc cấu trúc giá
  intrabar (FVG, order block, liquidity sweep...) — nếu Codex/owner sau này
  cân nhắc mở rộng retention `1m`, đây là lý do cụ thể hơn hẳn "có thể hữu
  ích" — không mở rộng thì không thể validate honest cả họ strategy này, chỉ
  có thể suy đoán từ literature như round này đã làm.
  prerequisite hạ tầng, research không tự giải quyết được.

- **[Trading][P3] 2 candidate alpha signal mới từ research rộng hơn
  (YouTube/TikTok/Reddit/paper theo yêu cầu user) — chưa implement:**
  (1) **ICT-style liquidity-sweep + FVG entry**: xác nhận sweep ở 15m, rồi
  chuyển xuống 1m tìm market-structure-shift, entry tại FVG/order-block
  hình thành — khác các MTF candidate hiện có (chain 2 timeframe theo thứ
  tự cụ thể, không phải dạng base+higher-filter đơn giản `finance-research`
  đang hỗ trợ, cần code mới thật sự để test). (2) **Fibonacci retracement
  "Golden Zone" (0.236-0.786) entry**, kết hợp EMA(9/50) cross + ATR stop —
  phần EMA/ATR đã có sẵn, nhưng logic Fibonacci retracement-zone hoàn toàn
  chưa tồn tại trong codebase (đã grep xác nhận, giống cách check VWAP/ORB
  trước đây) — tín hiệu thật sự mới, cơ chế khác (support/resistance từ tỉ
  lệ swing high/low). Chi tiết trong
  `raw/portfolio-btc-optimization-log.md` mục cùng ngày.

- **[Trading][P2 — CANDIDATE MỚI, TÍCH CỰC HƠN MỌI THỨ TÌM ĐƯỢC TRONG SESSION
  NHƯNG CHƯA CLEAR TARGET] Swing 4h/1d MTF stochastic — Sharpe/Sortino
  dương thật, nhưng có 2 điểm chặn cụ thể (Claude research
  2026-08-20T18:52 ICT, dùng backtest thật, chưa implement — scope
  `/loop` chỉ explore/optimize):** Test tổ hợp timescale swing (4h base +
  1d higher-timeframe) — chưa ai test trong session này (mọi MTF test
  trước đều dùng 5m base + 4h higher). Candidate
  `mtf_stochastic_14_3_30_70_sma50_trend_filtered` trên BTC/binance 5 năm:
  PF **1.66/2.04/1.65** nhất quán cả train/validation/holdout (39/19/18
  trade) — khác hẳn mọi candidate trước (toàn âm hoặc chỉ thắng holdout do
  mẫu ngắn). Full `--daily-profit-gate`: **Sharpe 1.13 (pass), Sortino
  3.10 (pass), positive_day_ratio 55.7% (pass sát ngưỡng), net PnL dương,
  cost_to_gross_pnl_ratio ÂM (-2.1% — funding carry có lợi)** — candidate
  ĐẦU TIÊN trong cả session có Sharpe VÀ Sortino dương VÀ PF>1 nhất quán cả
  3 split.

  **2 điểm chặn thật, không giấu:** (1) `failed_checks:
  ["negative_day_streak"]` — **48 ngày lỗ liên tiếp** trong năm holdout,
  vượt xa ngưỡng tối đa 5 ngày — filter trend SMA50 có vẻ vô dụng trong
  giai đoạn sideway kéo dài, cứ lỗ nhỏ liên tục; (2) **tần suất chỉ 18
  trade/năm ≈ 0.35 lần/tuần**, cách rất xa target 7 lần/tuần của user —
  cùng dạng vấn đề với tín hiệu daily-bar đã flag trước đây.

  **Không claim đây clear được target của user — KHÔNG, riêng tần suất đã
  fail.** Nhưng đây là phát hiện thật, có số liệu, dương thực sự — khác
  hẳn dạng "không tìm thấy edge" của mọi round trước. Nếu ai muốn theo
  đuổi: cần (a) giải pháp cho streak risk (regime filter tạm dừng khi
  sideway, hoặc giảm size khi streak dài), (b) chấp nhận tần suất thấp như
  1 bucket target riêng (swing, không phải scalping) thay vì ép đạt 7
  lần/tuần chung. Chi tiết đầy đủ trong
  `raw/portfolio-btc-optimization-log.md` mục cùng ngày.

  **[CROSS-BROKER VALIDATION, 2026-08-20T19:07 ICT]** Chạy cùng gate trên
  **Exness BTC/USD** (chưa test broker này) — số liệu gần như y hệt: Sharpe
  1.12 (Binance 1.13), Sortino 3.02 (3.10), positive_day_ratio 55.9%
  (55.7%), net PnL $1.66 ($1.69), **đúng 48 ngày lỗ liên tiếp giống hệt**,
  cùng cost ratio âm có lợi. Đây là bằng chứng mạnh hơn hẳn 1 broker đơn lẻ
  — cùng 1 signal cho hiệu suất gần như giống hệt trên 2 nguồn giá độc lập
  → khả năng cao đây là tính chất thật của giá BTC ở khung thời gian này,
  không phải artifact riêng của 1 nguồn data. **2 điểm chặn (streak 48
  ngày, tần suất 0.35 lần/tuần) vẫn y nguyên** — cross-validation không tự
  fix 2 vấn đề đó, chỉ tăng độ tin cậy của phần signal thật. (Ghi chú nhỏ:
  Exness lần này chỉ có 1 continuity violation, không đáng kể so với 108
  của XAU 4h/1d — không cần điều tra thêm.)

- **[Trading][ĐÃ ĐÓNG — PHỦ ĐỊNH BẰNG DATA THẬT, KHÔNG PHẢI CANDIDATE NỮA]
  `candle_reversion` mean-reversion trên XAU/USDT binance 1d — số liệu
  holdout rất mạnh nhưng thiếu ngày dữ liệu để pass gate chính thức
  (Claude research 2026-08-20T18:37 ICT, theo yêu cầu mới của user: mỗi
  vòng `/loop` phải tự backtest và tìm candidate cụ thể, không chỉ dừng ở
  phát hiện bug):** Test `--interval 1d --days 1825` cho XAU/binance (chưa
  ai test XAU ở 1d trước đây, chỉ có BTC). 3 biến thể bps liên quan đều có
  cùng pattern lạ — thua ở train/validation, thắng mạnh ở holdout:

  | Strategy | Train | Validation | Holdout |
  |---|---|---|---|
  | candle_reversion_10bps | 62 trade/59.7%/PF0.56 | 21/42.9%/0.68 | 28/**71.4%**/**1.85** |
  | candle_reversion_30bps | 52/57.7%/0.63 | 17/52.9%/0.53 | 26/**80.8%**/**2.24** |
  | candle_reversion_60bps | 42/66.7%/0.92 | 17/58.8%/0.68 | 18/**72.2%**/**3.41** |

  Chạy full `--daily-profit-gate --gate-strategy candle_reversion_60bps`:
  **positive_day_ratio 70% (≥55%), Sharpe 3.99 (≥1.0), Sortino 8.02
  (≥1.0), cost_to_gross_pnl_ratio 14.6% (≤50%), drawdown ~0.002%** — mọi
  ngưỡng chất lượng/rủi ro đều pass thoải mái. **`passed: false` chỉ vì
  đúng 1 lý do: `minimum_holdout_days` (cần 90, hiện có `holdout_candles:
  50` — window `2026-07-01`→`2026-08-19`, là ngày lịch thật gần nhất có
  cho XAU/binance 1d, không đổi được bằng cách chỉnh `--days`.**

  **Vì sao CHƯA gọi đây là "đã validate" (trung thực, không chỉ báo cáo
  con số đẹp):** pattern thua-train/thắng-holdout giống hệt nhau trên cả 3
  biến thể bps — không phải nhiễu ngẫu nhiên (nhiễu thật không tương quan
  chặt vậy giữa 3 tham số liên quan), nhưng cũng KHÔNG phải dạng "ổn định
  cả 3 split" đáng tin như tín hiệu daily stochastic của BTC trước đây
  (66.1%→69.6%→71.4%, tăng dần và ổn định). Khả năng cao nhất: 2 tháng gần
  đây của XAU thật sự đang ở 1 regime ủng hộ mean-reversion (có thể liên
  quan biến động giá vàng mùa hè này), trong khi các năm training trước đó
  thì không — có thể là edge thật đang hoạt động, hoặc có thể đảo ngược
  khi regime đổi.

  **Việc cần làm:** KHÔNG deploy vội. Theo dõi tự nhiên — mỗi ngày thật
  trôi qua `observed_days` sẽ tăng, nếu sau vài tuần vẫn giữ số liệu tương
  tự khi đủ 90 ngày holdout thì đó là validation mạnh hơn hẳn mọi thứ tìm
  được trong session này. Muốn nhanh hơn: chạy lại walk-forward chỉ dùng
  12-18 tháng gần nhất làm train/validation (thay vì full 5 năm) để test
  trực tiếp xem có phải regime-specific hay không, không cần chờ.

  **[CẬP NHẬT — ĐÃ TỰ TEST VÀ PHỦ ĐỊNH, 2026-08-20T18:41 ICT]** Tự làm
  đúng việc đã đề xuất ở trên thay vì để đó. Phát hiện: XAU/binance chỉ có
  đúng **253 nến 1d thật** (`candle_count` từ chính log tool, không phụ
  thuộc `--days` yêu cầu) — Binance mới list XAU/USDT perpetual ~8 tháng,
  không phải 5 năm như Claude nhầm tưởng ở round trước (tự đính chính).
  Vì không có lịch sử dài hơn thật để test trên Binance, chuyển sang test
  **Exness XAU/USD (cùng tài sản vàng, nhưng có 1,555 nến thật, ~4.3 năm)**
  — kết quả: `candle_reversion` cho **PF < 1 ở CẢ 3 split, nhất quán**
  (10bps: 0.84/0.62/0.57; 30bps: 0.92/0.93/0.62; 60bps: 0.93/0.83/0.72) —
  ngược hẳn pattern thắng-holdout thấy trên Binance. **Kết luận: candidate
  này đã bị phủ định bằng data thật, không phải edge bền vững, chỉ là
  artifact của mẫu quá ngắn (253 nến) trên Binance.** Quét lại toàn bộ
  candidate khác trên dataset Exness dài này (yêu cầu PF>1 nhất quán cả 3
  split, ≥10/5/5 trade) — **0 candidate nào pass**, khớp đúng kết luận
  chung "chưa tìm được edge robust" của cả chương trình research. Đóng
  item này, không phải candidate nữa — không cần Codex làm gì.

- **[Trading][P1 — ROOT CAUSE ĐÃ XÁC NHẬN, KHÔNG CÓ BURST 100+ LỆNH/NẾN]
  BTC Portfolio từng bị hiểu nhầm là ra quyết định dồn dập trong 2 khung quá độ
  deploy liên tiếp, `risk-2pct` gần mất trắng (Claude phát hiện
  2026-08-20T~14:52 ICT, dao động sai/đúng liên tục 14:55→15:07→15:22 ICT,
  chưa tự sửa code — scope session `/loop` chỉ explore/optimize):** **Correction
  authoritative 2026-08-20T16:10 ICT:** đọc trực tiếp checkpoint production và
  đối chiếu `continue_forward_from_replay`/`SimulatedLedger::continue_from` xác
  nhận 1,293 trade xuất hiện sau restart là lịch sử Backtest một năm được seed
  có chủ đích vào accumulator của Realtime để tạo continuous series; forward
  chỉ thêm đúng 1 trade (1,294), không phải 347/1,300 quyết định mới trên vài
  nến. Backtest `risk-2pct` equity $2.305 và Realtime $2.249 khác nhau đúng một
  trade forward; checkpoint vẫn tiến đều, target hiện
  `protective_exit_waiting_for_fresh_insight`. Vì OTel commit không đổi replay
  contract/fingerprint (vẫn v25), restart không rerun replay. Không rollback và
  không sửa decision throttle theo giả thuyết cũ. Việc còn lại là product
  decision riêng: giữ semantics continuous Backtest→Realtime hiện có, hay tách
  account/PnL Realtime khởi tạo lại $10k; không tự đổi vì đây là thay đổi nghĩa
  dữ liệu chứ không phải bug kỹ thuật đã chứng minh. Tóm tắt lịch sử điều tra
  đúng theo thứ tự thời gian sau khi đã xác nhận chắc chắn (đừng tin các
  kết luận tạm thời ở dưới, chỉ tin dòng này):
  - 13:52 ICT: fix evidence (`3d1ad44`) deploy, BTC bắt đầu ra quyết định
    lần đầu tiên trong lịch sử — nhưng kèm burst ~100+ trade/nến.
  - 14:29 ICT: fix weight-dilution (`cf35652`) deploy — Claude check lúc
    14:50/14:55 thấy số liệu đứng yên, kết luận nhầm "đã dừng".
  - 14:53 ICT: fix float-epsilon (`044e2b9`, xem mục Verify phía dưới,
    Claude đã review + xác nhận đúng) deploy — mỗi lần deploy/restart lại
    trigger 1 đợt burst mới (15:07 ICT: risk-2pct tiếp tục rơi từ $26.94
    xuống $2.31, +347 trade trong 12 phút).
  - **15:22 ICT, bằng chứng chắc chắn:** không có deploy mới nào từ 14:53
    tới giờ (`/api/v1/system/version` vẫn `044e2b9`); checkpoint 15 phút
    liên tục (08:05Z→08:20Z) chỉ **+1 trade** (392/901 → 392/902), equity
    risk-2pct gần như đứng yên ($2.31 → $2.25). **Xác nhận thật: burst chỉ
    xảy ra trong khung quá độ ngay sau mỗi deploy/restart, KHÔNG PHẢI lỗi
    chảy máu liên tục ở steady-state.** Giả thuyết "mỗi redeploy trigger
    lại burst" từ update trước được xác nhận đúng bằng dữ liệu thật.

  **Claude tiếp nhận correction của Codex (2026-08-20T16:52 ICT):** cảm ơn
  Codex đã tự điều tra sâu hơn và tìm ra giải thích đúng — Claude đã hiểu
  sai bản chất `1,293 trade` là burst lỗi thật; thực ra đó là 1 năm lịch sử
  Backtest được seed có chủ đích vào Realtime accumulator (thiết kế
  continuous series), forward path chỉ thêm đúng 1 trade thật. Equity
  `$10,000 → ~$2.25` phản ánh **hiệu suất thật của rule/strategy này qua 1
  năm backtest** (khớp hoàn toàn với toàn bộ phát hiện "không tìm thấy edge
  robust" của cả chương trình research này — không phải điều bất ngờ, mà là
  bằng chứng thêm cho đúng kết luận đó), không phải bug runaway destroy
  equity trong 1 giờ như Claude từng lo. Không cần rollback, không cần tìm
  "cơ chế gây burst" nữa (không có burst). Việc còn lại đúng như Codex nói:
  chỉ là product decision (giữ continuous series hay tách Realtime khởi
  tạo lại $10k) — không phải bug kỹ thuật, để user/Codex quyết định.
  Pull checkpoint lần 3 lúc **15:07 ICT** (12 phút sau lần đọc "đã dừng"
  lúc 14:55): **Binance BTC `risk-2pct` equity tiếp tục giảm từ $26.94 →
  $2.31** (thêm 347 trade mới trong 12 phút: win/loss từ 293/653 lên
  392/901). `fixed-pct` cũng tăng đúng y hệt 392/901 (từ 393/914 — gần như
  y hệt số trade với risk-2pct, chỉ khác sizing) — xác nhận cả 3 rule vẫn
  đang chia sẻ đúng 1 luồng quyết định over-firing chung, không phải vấn đề
  riêng của rule nào. **~12 phút chỉ có tối đa 2-3 nến 5m, mà có 347 trade
  mới — vẫn ~140 trade/nến, cùng độ lớn bất thường như lần đầu phát hiện.**
  Deploy `cf35652` (14:29 ICT) KHÔNG fix được vấn đề over-firing này — chỉ
  vô tình trùng với 1 khoảng lặng ngẫu nhiên giữa 2 lần Claude check (14:50/
  14:55), khiến Claude kết luận nhầm là đã dừng. **Đây vẫn là sự cố đang
  diễn ra thật sự, mức khẩn cấp cao nhất.**

  **Chi tiết quan trọng phát hiện thêm (15:09 ICT):** production đã deploy
  1 commit MỚI HƠN nữa, `044e2b948f`, build lúc **14:53:38 ICT** — tức sau
  cả `cf35652` (14:29) lẫn lần check "đã dừng" sai (14:50-14:55, vẫn đang
  chạy `cf35652`, chưa lên `044e2b9`). Điều này gợi ý mạnh: **burst 100+
  trade/nến rất có thể bị TRIGGER LẠI bởi MỖI LẦN redeploy/restart worker**
  (khả năng nằm ở đường historical-replay/evidence-resync lúc khởi động,
  không phải steady-state `decide()` loop khi đã chạy ổn định) — không
  phải 1 lỗi liên tục chảy máu vô hạn. Check checkpoint 2 phút sau (15:07 →
  15:09 ICT): `updated_at` KHÔNG đổi (giống hệt tới micro-giây), risk-2pct
  vẫn giữ nguyên `equity=2.31, win=392, loss=901`. **Nhưng chưa rõ chu kỳ
  checkpoint save là bao lâu** — không đủ bằng chứng để khẳng định lại
  "đã dừng" lần nữa (đã sai 1 lần rồi, không lặp lại sai lầm đó) — cần đợi
  ít nhất 15-20 phút không có deploy mới nào để có bằng chứng chắc chắn.
  **Khuyến nghị mạnh cho Codex:** nếu giả thuyết "mỗi redeploy trigger lại
  burst" đúng, thì MỖI lần Codex deploy tiếp theo cho tới khi fix xong sẽ
  tiếp tục gây thiệt hại equity mới — cân nhắc dừng redeploy liên tục vào
  khu vực này cho tới khi xác định chắc chắn root cause của chính cái burst
  lúc khởi động, không chỉ fix từng triệu chứng (weight-dilution,
  float-epsilon) riêng lẻ. Sau khi fix
  evidence-wiping (`3d1ad44`, xem task đã Dev-done phía dưới) deploy lên
  production (~13:52 ICT), BTC Portfolio đã chuyển từ "chưa từng ra quyết
  định" sang **ra quyết định liên tục bất thường**. Đọc trực tiếp Redis
  checkpoint production (~1 giờ sau deploy):
  - **Binance BTC `risk-2pct`: equity $10,000 → $26.94 (mất 99.7%)**, 293
    win / 653 loss (946 trade), net PnL -$9,973.06.
  - Binance BTC `compounding-10pct`: equity $10,000 → $8,196.65 (-18.0%),
    394 win / 913 loss (1307 trade), PnL -$1,803.35.
  - Binance BTC `fixed-pct`: equity $10,000 → $9,990.03 (-0.1%, size nhỏ
    nên ít thiệt hại hơn), 393 win / 914 loss (1307 trade), PnL -$9.97.
  - Exness BTC `compounding-10pct`: equity → $8,263.71 (-17.4%), 404
    win / 903 loss (1307 trade), PnL -$1,736.29.
  - Exness BTC `fixed-pct`: equity → $9,990.38, 403 win / 905 loss (1308
    trade), PnL -$9.62.
  - Win rate mọi rule đều ~30% (293-404 win trên 946-1308 trade).

  **Bằng chứng đây là bug, không phải "cuối cùng đã trade nhưng gặp thị
  trường xấu":** BTC base interval là **5m** — 1 giờ chỉ có tối đa ~12 nến
  đóng. 1307 trade trong ~1 giờ nghĩa là **~100+ trade MỖI NẾN 5 PHÚT** —
  không thể là hành vi "1 quyết định/nến" đúng thiết kế. Rất có thể fix
  `3d1ad44` (bỏ `inner.signal_states.clear();
  inner.portfolio_evidence.clear_interval(&interval);` khi có revision) đã
  vô tình bỏ luôn một cơ chế throttle/gate ngầm nào đó từng ngăn Portfolio
  ra quyết định lặp lại nhiều lần cho cùng 1 nến — cần đọc lại thật kỹ toàn
  bộ code path gọi `MultiTimeframePortfolioPolicy::decide()` để tìm chỗ
  nào trước đây phụ thuộc (trực tiếp hay gián tiếp) vào việc evidence bị
  clear để không bị gọi lặp lại.

  **XAU không bị ảnh hưởng theo cùng cách nghiêm trọng** (chưa kiểm tra kỹ
  trong entry này, cần verify riêng) — nhưng vì cùng chung code path
  `decide()`, cần kiểm tra cả XAU trước khi kết luận đây chỉ là vấn đề của
  BTC.

  **[ĐOẠN DƯỚI ĐÂY SAI — ĐÃ SỬA LẠI Ở ĐẦU MỤC NÀY, giữ nguyên để lộ rõ quá
  trình điều tra, đừng tin kết luận "đã dừng" ở đây]** Cập nhật lúc đó
  (cùng lúc phát hiện, +5 phút sau): tưởng đã dừng chảy
  máu, không phải incident đang diễn ra. Kiểm tra lại `handoff_codex.md`
  thì thấy Codex đã tự root-cause ĐÚNG bug này (mục Processing "BTC
  Portfolio luôn initial_flat" — quality tối đa 1.0 cho strategy chưa có
  trade, y hệt phát hiện của Claude từ round trước) và đã deploy fix
  `cf35652b7c8c95dc88fa3f3591600b32e875a48c` lúc **14:29:26 ICT** (xác nhận
  qua `/api/v1/system/version` production, cả 4 worker đều đúng SHA này).
  Pull lại checkpoint 5 phút sau lần đọc đầu (14:50 → 14:55 ICT):
  **equity/win/loss của cả `risk-2pct` và `fixed-pct` KHÔNG đổi** — nghĩa
  là thiệt hại 99.7% đã xảy ra trong đúng khung ~37 phút quá độ (13:52 lúc
  `3d1ad44` cho BTC bắt đầu ra quyết định, tới 14:29 lúc `cf35652` fix
  trọng số) — **KHÔNG phải đang tiếp diễn dưới code hiện tại**. Không cần
  rollback khẩn cấp nữa. Hạ mức từ "khẩn cấp đang diễn ra" xuống: (1) số
  liệu thiệt hại 99.7%/risk-2pct là thật, cần quyết định có reset lại các
  ledger simulated này về $10,000 hay giữ nguyên làm bằng chứng lịch sử;
  (2) cơ chế chính xác gây ra ~100+ trade/nến trong khung quá độ đó vẫn
  chưa được giải thích đầy đủ — đáng để hiểu rõ phòng khi 1 lần deploy
  tương lai tạo ra khung quá độ tương tự (evidence đã sync nhưng
  weight/threshold vẫn còn sai trong 1 khoảng ngắn). Không còn P0-CRITICAL
  khẩn nữa, hạ về P1 theo dõi. **[Đoạn này đã lỗi thời — xem correction của
Codex ở đầu mục này: không có burst, đây là backtest history seed đúng
thiết kế. Giữ nguyên để lộ quá trình điều tra.]**

- **[Trading][P2] R:R hiện tại (2:1) không thể hòa vốn với win rate thực
  tế đang quan sát được — Rule 3 (Claude tính toán 2026-08-20T16:52 ICT,
  dùng số liệu production thật đã thu thập trong session này, chưa tự đổi
  config — scope session `/loop` chỉ explore/optimize):** protective
  config của mọi Portfolio rule (đọc từ checkpoint thật) đều là
  `stop=0.005, take=0.01` — tỉ lệ R:R cố định 2:1 cho mọi rule, cả BTC lẫn
  XAU, cả 2 broker. Với R:R 2.0, win rate hòa vốn (chưa tính phí) là
  `1/(1+2)=33.3%`. Win rate thật quan sát được trong session này:
  XAU/binance ~30% (3W/7L) đã **dưới** ngưỡng hòa vốn; XAU/exness ~6.7%
  (1W/14L) thì cách rất xa. Nghĩa là **cấu hình R:R hiện tại đảm bảo lỗ về
  mặt toán học** ở mọi win rate thực tế đã quan sát, kể cả trước khi trừ
  phí/slippage/funding — đây là vấn đề hiệu chỉnh sizing riêng biệt, không
  chỉ là vấn đề chất lượng signal. (Lưu ý: số liệu BTC risk-2pct dùng để
  ước tính win rate ~30% trước đó hoá ra là backtest-seeded, xem correction
  phía trên — nhưng XAU/binance và XAU/exness's win rate là số liệu
  Realtime thật, không bị ảnh hưởng bởi correction đó.)

  **2 hệ quả cần tách bạch rõ:** (a) **Target 1 (có lãi/không lỗ)** có thể
  đạt được chỉ bằng cách hiệu chỉnh lại R:R theo đúng win rate thực tế
  (VD win rate 30% cần R ≈ 3-4 mới đủ margin sống sót qua phí thật) — đòn
  bẩy này CHƯA từng được thử trong toàn bộ chương trình research này; (b)
  **Target 2 (win rate ≥ 70%)** KHÔNG thể đạt được bằng cách chỉnh R:R —
  win rate là thuộc tính của tín hiệu entry/exit, không phải khoảng cách
  stop/take. Cần signal tốt hơn thật sự cho mục tiêu này, không liên quan
  gì tới sizing.

  **Việc cần làm nếu ai pick up:** thử nghiệm qua `finance-research` CLI
  (`--portfolio-stop-value`/`--portfolio-take-value`, đã có sẵn flag) với
  vài giá trị R lớn hơn (3-5), backtest honest theo đúng methodology hiện
  tại, so sánh net PnL trước khi đổi config production — không đổi trực
  tiếp `PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE` mà chưa backtest.
  Chi tiết trong `raw/portfolio-btc-optimization-log.md` mục Rule 3 cùng
  ngày.

  **[ĐÃ TỰ TEST, KẾT QUẢ PHỦ ĐỊNH giả thuyết trên — 2026-08-20T17:22 ICT]**
  Không để giả thuyết ở trên là lý thuyết chưa kiểm chứng — tự chạy
  `finance-research` local qua tunnel production thật
  (`--broker binance --base-asset XAU --quote-asset USDT --interval 5m
  --days 180`), so sánh `portfolio_execution` (`candle_momentum_10bps`/
  `fixed-pct`) ở 3 cấu hình: baseline (stop=0.005/take=0.01, R=2, PnL
  **-$22.42**), take rộng hơn (stop=0.005/take=0.02, R=4, PnL **-$21.57**),
  stop hẹp hơn (stop=0.002/take=0.01, R=5, PnL **-$21.61**). **Cả 3 gần như
  giống hệt nhau** (chênh nhau chưa tới $1, ROI chênh <0.003 điểm %), số
  trade cũng gần như không đổi (3374→3319→3283) dù đã đổi khoảng cách
  stop/take rất nhiều. **Giả thuyết R:R ở trên SAI — đã tự phủ định bằng
  số liệu thật, đừng implement.** Đọc mechanistic: PnL gần như bất biến
  dù đổi mạnh stop/take gợi ý phần lớn lệnh đóng bởi **tín hiệu đối lập**
  (Portfolio tự đảo hướng quyết định) trước khi chạm stop/take, không phải
  đóng bởi protective level — nghĩa là sizing/R:R KHÔNG fix được cả Target
  1 (không chỉ Target 2 như viết ở trên). Đòn bẩy duy nhất còn lại thật sự
  là chất lượng signal, khớp đúng kết luận chung của toàn bộ chương trình
  research này. Hạ độ ưu tiên xuống — không còn actionable, chỉ giữ lại
  làm bằng chứng đã thử và không hiệu quả.

- **[Trading][P2 — phần cleanup đã chuyển Dev-done, chỉ còn research tùy chọn]
  `finance-broker` từng có thư viện 16 strategy C++ chưa từng
  được wire vào runtime; đã deprecate/xóa ở commit `3895176`, phần còn lại
  chỉ là quyết định có port từng thuật toán sang `finance-research` hay không
  (Claude phát
  hiện 2026-08-20, trong lúc chạy `/loop` explore/optimize — không tự làm gì
  cả, đúng scope session này chỉ explore & optimize + log bug/finding):**
  đọc production Redis read-only (`root@160.22.122.55`,
  `redis-singleton-wkwwogos0css0g0owwoc0sos`, chỉ để tìm ledger data cho
  Portfolio layer) tình cờ lộ ra ~25k key `engine_cache:*` cho hàng chục cặp
  (BTCUSDT, ETHUSDT, XRPUSDT, altcoin...) gắn tên strategy hoàn toàn không
  tồn tại trong code Rust hiện tại của `finance-live-action`: `ADX_TREND`,
  `ICHIMOKU`, `HULL_MA`, `SUPERTREND`, `KELTNER`, `PIVOT_BOUNCE`,
  `STOCH_RSI`, `VOLUME_SPIKE`, `VWAP_ABS`, `WILLIAMS_R`, `AG_OCC`,
  `EMA_CROSS`, `MACD_TREND`, `RSI`, `SCALP`. Truy ra nguồn:
  `finance-broker/packages/finance_strategies_cpp/` — 16 strategy C++ (qua
  pybind11) chia 3 nhóm `trend/` (Adx/HullMa/Ichimoku/Supertrend), `entry/`
  (AtrZScoreMeanReversion/Keltner/PivotBounce/StochRsi/VolumeSpike/
  VWAPAbsorption/WilliamsR), `compose/` (AntigravityOcc/EmaCross/MacdTrend/
  Rsi/Scalp).

  **Xác nhận đây KHÔNG phải hệ thống đang chạy live, mà là code đã build
  nhưng bị bỏ quên** (kiểm chứng trước khi báo, không suy đoán):
  `docker/Dockerfile:27` vẫn build package này vào image production, nhưng
  grep toàn bộ `app/` (code Python thật sự chạy) chỉ thấy import
  `Kline`/`Side` (type dùng chung) — **không có bất kỳ chỗ nào trong `app/`
  gọi tới 16 class strategy đó hay factory `create_strategies`** của
  package. Redis `engine_cache:snapshot_ts` của BTCUSDT/5m đọc được
  `ts_ms` cũ hơn thời điểm query khoảng **104 ngày** — không được refresh
  nữa. `git log` riêng thư mục package dừng lại ở 2026-03-28 dù cả repo
  `finance-broker` vẫn commit đều tới 2026-08-14 — tức có một giai đoạn
  phát triển thật rồi dừng lại, không phải code chết từ đầu. Không có
  workflow/cron nào reference `engine_cache` hay `finance_strategies_cpp`.

  **Cập nhật (cùng ngày, vòng `/loop` kế tiếp): đã tìm ra commit xoá gốc —
  bớt mơ hồ hơn nhiều.** `finance-broker` commit `278a54d` ("clear code",
  2026-06-06, ~2.5 tháng trước) xoá chủ đích toàn bộ
  `app/services/trading/` (calibration engine: `live_ranking_worker.py`,
  `optimizer.py` có class `PortfolioWeights`, `scalping_scorer.py`,
  `selector.py`) và `app/interfaces/live/` (HTTP server riêng, có
  `routers/trades.py`) — tức bên tiêu thụ `finance_strategies_cpp` đã bị
  xoá hẳn. Các commit ngay sau đó refactor `finance-broker` đúng theo
  README hiện tại (chỉ market-data/broker integration qua gRPC, không tự
  quyết định trade) — khớp hoàn toàn với kiến trúc hiện tại đã biết
  (`finance-live-action` là nơi duy nhất ra quyết định). Kết luận: nhiều
  khả năng đây là **dọn dẹp kiến trúc có chủ đích**, không phải hệ thống bị
  bỏ quên giữa chừng.

  **Việc cần làm (rõ ràng hơn, không còn là câu hỏi mở):**
  1. Dọn xác chết còn sót lại: `docker/Dockerfile:27` vẫn build
     `finance_strategies_cpp` vào image production dù không ai gọi (tốn
     build time vô ích); 2 file test
     (`tests/services/trading/engine/test_decision.py`,
     `tests/services/trading/calibration/test_live_ranking_worker.py`)
     import từ `app.services.trading.*` — module đã không còn tồn tại từ
     commit `278a54d`. **Đã tự confirm thật (không chỉ suy đoán):** chạy
     `python -m pytest tests/services/trading/ --collect-only -q` local →
     `ModuleNotFoundError: No module named 'app.services.trading'`, collect
     fail ngay, không phải fail assertion. Lý do chưa ai phát hiện: CI
     (`ci-cd.yml:149-151`) chỉ chạy đúng 2 file cụ thể
     (`test_grpc_server.py`, `test_log_rotation.py`), không bao giờ chạy
     full `pytest` discovery qua `testpaths = ["tests"]`
     (`pyproject.toml:84`) — nên bug collect này vô hình với CI suốt 2.5
     tháng qua, chỉ lộ ra khi chạy `pytest` không tham số local. Cần xoá
     cả build step (`docker/Dockerfile:27`) lẫn 2 file test orphan này.
  2. Việc riêng, không bắt buộc: 16 thuật toán indicator (Adx/Ichimoku/
     HullMa/Supertrend/Keltner/...) tách biệt được khỏi phần Flow1/Flow2
     execution logic đã xoá — nếu muốn, có thể cân nhắc port riêng thuật
     toán (không phải nguyên hệ thống cũ) vào sweep `finance-research` như
     candidate signal mới, nhưng đây là ý tưởng khám phá riêng, không phải
     phần của việc dọn dẹp #1.
  Chi tiết đầy đủ + evidence trong `raw/portfolio-btc-optimization-log.md`,
  mục "found a whole second, unused 16-strategy library" + follow-up cùng
  ngày (2026-08-20).

- **[Observability][historical record — superseded, not actionable] Goal setup
  OpenTelemetry ban đầu:** toàn bộ timeline bên dưới ghi lại quá trình trước
  cutover và không còn mô tả current state. Acceptance đã được đáp ứng bởi
  unified Coolify stack/commit `08620d2` trong Verify; local Tempo backend 7-day
  hiện là quyết định production single-host đã kiểm chứng, không còn bị chặn bởi
  các biến `TEMPO_S3_*` hay resource `finance-tracing` cũ. Owner duyệt goal ngày
  2026-08-20; implementation đã bắt đầu ở
  Finance MW với OTel SDK, W3C propagation HTTP/gRPC/Kafka, ECS trace/span
  correlation và POC upstream Collector → Tempo. Kiến trúc chốt là **trace-only
  trước**: service OTel SDK -> OTLP -> upstream OTel Collector gateway (memory
  limiter + tail sampling + batch) -> Tempo; giữ `/metrics` -> vmagent/
  VictoriaMetrics và ECS JSONL -> Filebeat -> Elasticsearch/Kibana như hiện tại.
  ECS log phải có `trace.id`, `span.id`, `service.name`, `service.version` để
  correlate trace với log. Instrument các causal path thật: Finance MW -> Live
  Action và Finance MW -> Broker/MT5; producer -> Kafka -> consumer là một trace
  riêng, không nối giả các luồng không có quan hệ nhân quả. Giữ 100% error/slow
  trace và sample 5-10% trace bình thường; chỉ rollout rộng khi đo được overhead,
  trace continuity, storage/day và rollback. Production Tempo dùng S3-compatible
  object storage; local filesystem chỉ dùng cho POC/dev. Acceptance: propagate
  W3C trace context qua HTTP, gRPC và Kafka; Grafana xem được trace Tempo và link
  sang ECS `trace.id`/`span.id` trong Kibana; Collector/Tempo có `/metrics`,
  dashboard/alert, resource caps, retention và rollback; không ghi credential/
  payload nhạy cảm vào span. Verify bằng một lỗi test kiểm soát được: từ request/
  market event tìm được full trace, đúng service/version và log liên quan, đồng
  thời `/metrics`/VictoriaMetrics và Filebeat/ES hiện tại không bị duplicate hay
  regression. Production rollout còn phải cấp S3-compatible bucket/credentials;
  không được thay bằng local disk rồi mark verify.
  **Progress 2026-08-20:** Finance MW đã có SDK/exporter opt-in, AlwaysSample
  head policy, bounded batch shutdown, W3C HTTP/gRPC/Kafka propagation, Kafka
  consumer span bao trùm commit và poison event vẫn được đánh ERROR để tail
  sampler giữ lại; HTTP/gRPC/Kafka ECS access/error log dùng trace/span ID thật
  và request ID độc lập. Pinned local stack Collector `0.159.0` + Tempo `3.0.2`
  đã validate exact config; controlled error integration test query lại đúng
  trace ID/service/version từ Tempo sau 10.65s. Đã thêm S3-only production
  config, bounded local override, vmagent scrapes, Grafana tracing dashboard,
  4 alert rules, Tempo datasource provisioning, runbook và static contracts.
  Finance MW foundation commit `38d0177` đã push `main`; full `go test ./...`,
  `go vet ./...`, 94 monitor tests và controlled-error Tempo integration xanh.
  CI/deploy run `32348469746` được theo dõi qua detached watcher
  `/tmp/finance-mw-38d0177.output.log` (watcher cũ đã chết trước completion và
  phải được thay bằng watcher file-backed mới sau khi lấy trạng thái run đúng
  một lần). Live Action commit `4f55c72` đã push thẳng `main`: đã có
  OTLP SDK opt-in, bounded batch/shutdown, service version từ immutable build
  SHA, W3C HTTP/gRPC/Kafka extraction/injection, server/client/error spans,
  ECS trace/span correlation, Kafka span đi qua strategy + durable checkpoint,
  và Compose env mặc định tắt. Regression hiện xanh: Finance API 187/187,
  Kafka 7/7, full Rust workspace, targeted Clippy (chỉ còn debt ngoài diff),
  và Compose config active stacks. Broker commit `b0c1a50` đã push `main`: OTel
  Python SDK opt-in, gRPC async client/server instrumentation, ECS trace/span ID
  thật và regression in-process chứng minh client/server cùng W3C trace (10 test
  observability xanh). MT5 commit `8ce5b95` đã push `main`: OTel SDK tương thích
  Python 3.9+, gRPC server instrumentation, ECS correlation và in-process W3C
  propagation test (32 test xanh). MT5 run `32351817616` bắt được CI image test
  chỉ cài dependency cũ nên thiếu package OTel; fix-forward `cbc36f6` thêm exact
  tracing dependencies và workflow contract, reproduction đúng Python 3.12
  container 32/32 xanh; run `32352088507`, watcher
  `/tmp/mt5-cbc36f6.output.log`. Cả ba repo service được push cùng một batch;
  tracing vẫn fail-safe mặc định tắt cho tới khi production backend sẵn sàng.
  Còn thiếu live S3-compatible credentials/backend, bật live Collector/Tempo,
  Grafana datasource thực tế và production controlled-error end-to-end gate.
  Production web verification của `38d0177` còn phát hiện false gate: thay đổi
  backend CI bị coi là web delivery nên đòi image web không được build; regression
  đã thêm và fix-forward `5a67ac3` push `main`, run `32352372121`, watcher
  `/tmp/finance-mw-5a67ac3.output.log`. MT5 test fix-forward run đã xanh unit
  nhưng build gặp Docker Hub TLS timeout; rerun cùng `32352088507` được theo dõi
  tại `/tmp/mt5-cbc36f6-attempt2.output.log`.
  **Production delivery path 16:45–16:50 ICT:** commit `4a71604` push `main`
  thêm workflow mode `deploy-tracing` và `scripts/deploy-tracing.sh`. Script
  fail-closed trước mọi mutation nếu thiếu secret; dựng candidate Tempo/
  Collector pinned + capped, dùng release/WAL riêng theo SHA/run/attempt, gửi
  controlled ERROR OTLP JSON rồi query exact trace/service/version từ Tempo,
  atomic promote với container rollback, lặp lại controlled trace sau promote,
  provision + health-check Grafana Tempo datasource. 110 observability tests,
  bash syntax, workflow contract và no-secret gate xanh. CI run `32355877695`,
  watcher `/tmp/finance-mw-4a71604.output.log`. Audit chỉ tên GitHub secrets xác
  nhận production environment đã có Grafana credentials nhưng **chưa có** năm
  secret `TEMPO_S3_ENDPOINT`, `TEMPO_S3_BUCKET`, `TEMPO_S3_ACCESS_KEY`,
  `TEMPO_S3_SECRET_KEY`, `TEMPO_S3_INSECURE`; vì host còn 85% disk và contract
  cấm local backend, không dispatch production tracing và không chuyển Verify.
  **Parallel hardening 2026-08-20 18:18 ICT:** Finance MW commit `e64d3e1`
  loại S3/Grafana credentials khỏi Docker/curl process arguments bằng env/auth
  files mode 0600 + cleanup, reject newline injection, thêm pinned Tempo/
  Collector config validation và CI path contracts; run `32363183833` được
  theo dõi file-backed. Audit service xác nhận Live Action và MT5 wiring hiện
  tại đã đủ, test bounded xanh và exporter vẫn mặc định tắt. Finance Broker có
  một gap: `service.version` ưu tiên mutable tag hơn immutable build SHA; commit
  `f7a3f18` sửa precedence và thêm disabled-exporter regression. CI/deploy run
  `32362890724` xanh (build/test/publish 7m21s, deploy 1m08s), production exact
  image `f7a3f18`, health pass; canonical production gRPC BTC/USDT futures 5m
  sau deploy trả 3 closed candles thật, open timestamps cách đúng 300000ms.
  Tracing chưa bật vì Collector/Tempo S3 chưa tồn tại; không coi health/image
  deployment là causal-trace success.
  Finance MW hardening tiếp tục ở `458af95` (validator dùng `docker cp` để tránh
  Docker-outside-of-Docker bind path) và `c9cf272` (bounded cold pull như trên);
  cả hai là ancestor/current của run authoritative `32364497291`. Không dispatch
  `deploy-tracing` khi năm secret S3 còn thiếu.
  Owner cần cấu hình các environment secrets này từ một S3-compatible provider
  (không gửi giá trị qua chat); sau đó dispatch mode `deploy-tracing`, bật SDK
  từng service và chạy causal HTTP/gRPC/Kafka error trace gate.
  **Coolify ownership 2026-08-20 22:10 ICT:** đã tạo resource inactive
  `finance-tracing` UUID `eqoery9uo2wq9801lnssxaql` trong production project,
  đủ năm slot env `TEMPO_S3_*`, không có container tracing chạy và không có
  native durable owner. Tempo/Collector config đã cài read-only trên host,
  WAL owner `10001:10001`, hash khớp repository. Source Coolify Compose không
  `container_name`/profile, resource-capped, commit `0b2e35b`; tests OTel,
  Coolify workflow và 40-service resource-limit contract đều xanh. Resource
  phải giữ `exited` cho đến khi owner điền credential S3 thật; đây chưa phải
  production trace success và chưa được chuyển Verify cho goal OTel end-to-end.

- **[Data quality][historical context for active Processing task, not a separate Todo]
  Root-cause `holdout_interval_continuity` của Exness
  XAU trên research gate:** implementation/backtest VWAP + ORB đã hoàn tất
  research-only, không wire vào
  live workers. Đã thêm London-session anchored VWAP (volume-weighted variance
  band + RSI confirmation) và ORB first-close breakout, mỗi family có hai
  parameter variants; state tách theo instrument/timeframe, reset theo session,
  chỉ dùng closed candle và ORB chỉ fire một lần/session. Regression reset,
  no-repeat, band/RSI và unique candidate names xanh; full finance-research
  55/55 xanh. Backtest Candle Evidence workflow được tổng quát hoá theo canonical
  broker/market/base/quote/interval để chạy honest 5-year Exness XAU sau push.
  Commit research `e7fb55b` đã push `main` cùng batch deploy run
  `32374812800`; local logging/workflow/research/API/full workspace/fmt/diff
  đều pass. Chưa promote production trước khi workflow evidence 5 năm
  và train/validation/holdout được kiểm tra trung thực.

  Root cause code đã xác nhận: `daily_profit_gate` coi mọi delta khác
  chính xác một interval là violation, không xét broker/market/session trong khi
  Finance MW đã persist authoritative `gap_before_reason=broker_session_or_no_tick`
  và continuity audit production trước đó chứng minh các gap Exness XAU là
  daily rollover/weekend closure thật. Commits `e9f5287` + `cc49386` port
  heuristic fail-closed đã được production chart kiểm chứng, bao gồm cả
  DST 21→22 và 22→23 UTC; weekday outage và cùng gap trên Binance vẫn
  fail. Full workspace/research/fmt/diff pass; research-only CI runs
  `32377310284` và `32378404175` success, runtime deploy được skip đúng.
  Exact image evidence runs `32377810035` + `32378874591` success.

  Production daily gate ORB 30m giảm continuity violation `95 → 32` nhưng
  chưa về 0. Read-only Timescale liệt kê 32 gap còn lại là weekend
  reopen +5 phút, holiday/early-close và no-tick ngắn; các row lịch sử cũ
  chưa có marker dù canonical broker audit đã phân loại broker-native.
  Không mở rộng heuristic vì sẽ che outage thật. Fix triệt để còn lại:
  truyền authoritative `gap_before_reason/gap_before_candles` từ Finance MW
  qua canonical gRPC Kline sang research, hoặc backfill marker chỉ sau broker
  verification. Task giữ `Processing`; không synthesize candle/không mark Verify.

  **[Claude independent backtest, round 18 `/loop`, 2026-08-20]** Tự build
  `e7fb55b` và chạy honest sweep + `--daily-profit-gate` thật trên Exness
  XAU/USD 5m (5 năm, qua tunnel production) cho cả 4 candidate mới. Kết quả
  đầy đủ trong `research/quant/rounds/round18-vwap-orb-independent-test.md` và
  `research/quant/reports/optimize_loop_update_v2.csv`:

  - **`session_vwap_reversion_london_14_1_5` và `..._14_2_0` — GIẢ THUYẾT BỊ
    PHỦ ĐỊNH bằng data thật, không phải candidate nữa.** Cả 2 biến thể đều
    PF<1 nhất quán ở CẢ 3 split (0.51/0.55/0.60 và 0.59/0.65/0.50) dù win
    rate khá cao (54-64%) — R:R quá tệ nên vẫn lỗ. Không cần backtest thêm,
    không đề xuất tiếp tục hướng VWAP mean-reversion cho instrument/timeframe
    này.
  - **`opening_range_breakout_london_60m`** — PF không nhất quán (0.87/1.11/
    0.95), không phải candidate.
  - **`opening_range_breakout_london_30m` — candidate đáng chú ý nhất, CHƯA
    gọi là validated (cùng lý do thận trọng như candle_reversion Round 12 đã
    từng bị phủ định sau đó):** full gate thật: Sortino **1.85 (pass)**,
    Sharpe **0.94 (sát ngưỡng 1.0, fail nhẹ)**, max negative-day streak
    **chỉ 4 ngày (pass, ≤5)** — tốt nhất toàn chương trình research này, mọi
    candidate 4h/1d swing trước đó đều fail streak nặng (17-66 ngày). Tần
    suất holdout 123 trade/366 ngày ≈ **2.37 lần/tuần** — thấp hơn target 7
    nhưng cao hơn hẳn cả họ swing 4h/1d (0.21-1.24/tuần, xem round 17). Net
    PnL dương $1.35 (holdout). **Nhưng 2 lý do CHƯA tin được:** (1) pattern
    PF tăng dần qua 3 split (train 0.868 thua → validation 1.023 hoà →
    holdout 1.275 thắng) — giống hệt hình dạng candle_reversion XAU Round 12
    đã bị phủ định sau đó bằng dataset dài hơn, không phải dạng ổn định cả 3
    split đáng tin; (2) **fail `holdout_interval_continuity`** — vấn đề chất
    lượng dữ liệu thật, không phải chất lượng signal, cùng loại lỗi đã flag ở
    Round 15 cho Exness XAU 4h/1d (`interval_continuity_violations=108`) —
    giờ xuất hiện lại ở Exness XAU **5m** cũng của instrument này, gợi ý đây
    có thể là vấn đề hệ thống của riêng Exness XAU (data gap/session-closure
    handling), không phải ngẫu nhiên riêng lẻ từng combo. Đề xuất: (a) không
    promote ORB 30m production trước khi có thêm dữ liệu dài hơn xác nhận
    pattern không phải regime-artifact ngắn hạn; (b) điều tra gộp
    `holdout_interval_continuity` cho Exness XAU ở cả 2 timeframe (5m và
    4h/1d) như 1 root cause chung thay vì 2 vấn đề riêng lẻ.

  **[Claude re-verify round 20 /loop, 2026-08-20, sau fix e9f5287]** Đã tự
  build e9f5287 ("fix(research): exempt verified Exness session closures"),
  chạy `cargo test daily_profit_gate` local (11/11 pass, đúng claim), rồi
  chạy lại chính xác gate `opening_range_breakout_london_30m` trên Exness
  XAU 5m qua tunnel production. Fix có tác dụng thật cho đúng 2 pattern nó
  target (weekend Friday->Sunday, daily 21:00->22:00 UTC rollover -- có test
  riêng, cả 2 pass) nhưng vẫn còn `interval_continuity_violations=95`, check
  vẫn fail -- nghĩa là còn gap thật khác weekend/rollover ở Exness XAU 5m
  chưa được fix này cover. Không so sánh được số violation trước/sau chính
  xác (round 18 không log số violation cụ thể, chỉ log fail/pass) -- nhưng
  kết luận rõ: fix đúng hướng, đúng những gì nó tự nhận làm, nhưng CHƯA đóng
  hẳn item này -- vẫn cần điều tra tiếp 95 violation còn lại là gap thật hay
  1 pattern session-closure khác chưa được nhận diện.

  **[Claude re-verify round 21 /loop, 2026-08-20, sau fix cc49386 "cover
  Exness DST rollover"]** Tự build, `cargo test daily_profit_gate` 11/11
  pass, re-run đúng 2 case đã biết fail: `opening_range_breakout_london_30m`
  Exness XAU 5m giảm từ **95 → 32 violation** (-66%); và re-check luôn case
  gốc Round 15 (`mtf_candle_momentum_10bps_sma10_trend_filtered` Exness XAU
  4h/1d) giảm từ **108 → 57 violation** (-47%). Cả 2 fix đều có tác dụng
  thật, đo được bằng số cụ thể, không phải fix vô ích -- nhưng
  `holdout_interval_continuity` vẫn fail cả 2 combo, còn 32 và 57 violation
  chưa giải thích được. **Đã thử tự root-cause thêm nhưng không đủ công cụ:**
  `finance-research --json` chỉ lộ `candle_count` (số), không lộ list
  timestamp thật của nến; port `8086` Finance MW chỉ có gRPC thuần, không có
  REST endpoint song song để tôi tự pull raw kline timestamps qua `curl` mà
  phân tích gap. Đề xuất: nếu muốn tiếp tục thu hẹp, cần 1 trong 2: (a) thêm
  1 debug flag vào `finance-research` xuất list các cặp nến vi phạm continuity
  kèm timestamp (giúp cả Claude và Codex tự phân tích được không cần đọc lại
  toàn bộ code phát hiện pattern mới), hoặc (b) Codex tự audit trực tiếp
  Timescale/Finance MW cho đúng instrument+interval này.

  **[NÂNG ĐỘ ƯU TIÊN — Claude round 56 /loop, 2026-08-21, bằng chứng mới:
  đây là vấn đề HỆ THỐNG, không phải case lẻ tẻ]** Tool mới (sau Round 54
  fix) lộ ra breakdown `input_continuity_failed:<interval>` chi tiết. Chạy
  `--daily-profit-gate` (Portfolio production thật) cho cả 2 leg Exness:
  **Exness BTC fail continuity ở 5 interval (5m/15m/1h/2h/30m); Exness XAU
  fail ở 8 interval (5m/12h/15m/1d/1h/2h/30m/4h) — gần như TẤT CẢ.** Binance
  (cả BTC lẫn XAU) KHÔNG có `input_continuity_failed` nào. Đây là vấn đề hệ
  thống của riêng nguồn dữ liệu Exness, không phải vài case cá biệt như 2
  lần fix trước (`e9f5287`/`cc49386`) đã xử lý. Đề xuất: audit tổng thể
  pipeline dữ liệu Exness thay vì tiếp tục vá từng interval riêng lẻ. Chi
  tiết trong `research/quant/rounds/round56-full-4leg-production-gate-picture.md`.

  **[Claude cross-instrument test round 21 /loop, 2026-08-20]** Test đúng 4
  candidate này (không đổi tham số) trên BTC/binance 5m, 5 năm — kết quả
  SẠCH, đúng hướng: cả 4 (VWAP 2 biến thể + ORB 30m/60m) đều PF<1 nhất quán
  CẢ 3 split trên BTC, không có ngoại lệ, kể cả ORB 30m (candidate hứa hẹn
  nhất trên XAU). Đúng cơ chế kỳ vọng: ORB/VWAP session-anchored (London
  08:00 UTC) giả định có 1 phiên giao dịch thật với thanh khoản đặc trưng
  lúc mở phiên — đúng với FX/vàng nhưng BTC giao dịch 24/7 không có khái
  niệm mở phiên. Xác nhận: ORB/VWAP nên giữ scope riêng cho XAU (theo đúng
  Rule 4 của user — không cần 1 setup chung cho mọi token), không đề xuất
  cho BTC. Chi tiết đầy đủ trong
  `research/quant/rounds/round21-continuity-fix-verify-and-btc-orb-transfer.md`.

  **[ĐÃ PHỦ ĐỊNH — Claude round 34 /loop, 2026-08-20, đúng regime-dependency
  test đã hứa ở round 18/21]** Chạy lại `opening_range_breakout_london_30m`
  và `_60m` trên Exness XAU 5m với window 18 tháng (`--days 545`) thay vì 5
  năm, đúng phương pháp đã falsify `candle_reversion` ở Round 13. Kết quả:
  **pattern đảo ngược hoàn toàn** — ORB 30m: train 1.009/validation
  **2.014**/holdout **0.683 (thua)**; ORB 60m: train 1.065/validation
  1.325/holdout **0.466 (thua nặng)**. Ở window 5 năm trước đó, holdout lại
  là split THẮNG. Kết luận: candidate "thắng" trước đây phụ thuộc hoàn toàn
  vào việc chọn đúng lát cắt thời gian nào làm holdout — không phải edge ổn
  định. **Đóng hẳn ORB 30m/60m, không còn là candidate treo nữa.** Chi tiết
  trong `research/quant/rounds/round34-orb-30m-falsified-regime-dependency-test.md`.
  Sau phát hiện này, hướng duy nhất còn mở chưa bị phủ định trong toàn bộ
  chương trình research là Funding Rate Extreme Reversion (mục Todo khác) —
  vẫn chưa test được vì thiếu hạ tầng, không phải vì đã test và pass.

- **Portfolio profitability practices (Claude system review):** Round 2 đã
  reconcile proposal với code/production hiện tại: attribution (`33f95b1`),
  per-rule risk caps (`8d31ac1` và descendants) và realtime/replay adaptive
  reweight (`40fdfa3`, `cf35652`) đều đã live, nên không implement lại các bước
  cũ. Baseline scoped BTC fixed-notional vẫn âm: 1,295 trades, PnL
  `-9.9046439016`, PF `0.6327140786`; breakout families cũ cũng đã được sweep,
  không phải candidate chưa thử. Round 2 đã append vào
  `docs/archive/legacy-raw/proposal/portfolio-profitability-improvements.md`; vòng actionable hiện
  tại là research-only VWAP/ORB ở item phía trên, chỉ promote khi honest gate
  chứng minh được edge.

- **P0 — Watcher handoff Codex:** theo dõi thay đổi của
  `raw/handoff_codex.md`, ghi event bất biến vào file log và dùng nội dung mới
  làm task intake để triển khai; không tự commit operator-state file.

## Dev-done

## Verify

- **[Observability][P3, verify 2026-08-21 — no code/infra change required]
  Full-stack metrics/tracing/logging audit against
  `.agents/rules/observability-logging.md`, plus explicit Tempo storage
  durability check requested mid-task:** read-only SSH audit of
  `root@160.22.122.55` (all commands filtered per credential-safety rule —
  no `docker exec ... env` dumps; the standing `KAFKA_CONTROLLER_PASSWORD`
  P0 exposure incident under Todo was left untouched, not rotated, per that
  item's own guidance). Findings: (1) **Metrics** — all 8 unified
  observability containers healthy 7-8h uptime; canonical `/metrics` on
  port `8002` returns real Prometheus text with correct families on
  finance-mw, kline-ingest, job-worker path, finance-broker, mt5, and all 4
  Live Action workers (binance BTC/XAU, exness BTC/XAU); finance-mw's own
  port `8086` is the app port, not metrics, matching README's documented
  `:8002` contract — no `/actuator/prometheus`-style alias found anywhere.
  (2) **Tracing / Tempo storage** — user asked mid-task whether Tempo has
  centralized durable storage like VictoriaMetrics rather than ephemeral
  container disk. Confirmed it already does: production
  `tempo-vc0gwk040csg4cwg88000k48` bind-mounts host path
  `/data/monitor/tempo:/var/tempo` (matches source of truth
  `docker/monitor/coolify-observability.yaml:339-341` and
  `docker/monitor/tempo/tempo-production.yaml`, `backend: local`,
  `block_retention: 168h` = the required 7-day retention). Durability
  proof: container `State.StartedAt` is `2026-08-21T07:00:00Z` but the
  oldest block file under `/data/monitor/tempo/blocks` has mtime
  `01:00:49Z` the same day — six hours *before* the current container
  started, proving the volume survived the most recent redeploy/recreation
  instead of being wiped. Current usage 1.9G, host disk 43G free headroom.
  This is architecturally the same durability pattern VictoriaMetrics uses
  (VM: named Docker volume `u0s884skc4cgwoss8s0c8o0s_victoriametricsdata`;
  Tempo: host bind mount) — both survive container recreation, neither is
  the container's ephemeral writable layer. No object-storage (S3/MinIO)
  backend exists in the stack and none was added: local-disk-with-durable-
  mount already satisfies the retention/durability requirement for this
  single-node (`-target=all`) Tempo monolith, and adding MinIO would be new
  infrastructure scope, not a gap fix. **Conclusion: no Tempo storage
  change applied — verified already durable.** (3) **Logging** — all 4
  repos (`finance-mw`, `finance-broker`, `finance-live-action`, `mt5`)
  already have `scripts/setup-log.sh` and `scripts/setup-agent.sh`, both
  copied into their Docker images and sourced from `docker/entrypoint.sh`,
  each guarded by an existing bounded test
  (`test_observability_bootstrap.sh` / `test_log_rotation.sh` /
  `test-logging.sh`). Production `/data/log/<service>/access.jsonl.*`
  rotation on finance-mw and finance-broker holds exactly 7 dated archives
  (`2026-08-14` through `2026-08-20`) plus the live current-day file — the
  7-day retention rule is enforced correctly, no stale archives. (4)
  **Credential/PII audit** — grepped `password|authorization|cookie|api_key
  |secret|token|credential` across active services' `application.jsonl`/
  `error.jsonl` (`finance-mw`, `finance-broker`, `finance-kline-ingest`,
  `finance-job-worker`), with every matching line piped through a
  long-string redaction filter before leaving the remote shell so no
  candidate secret value could reach this session. All matches were benign:
  the Postgres driver's standard `pq: password authentication failed for
  user "postgres"` string (no value) and a CoinGecko coin id literally named
  `fxn-token` — zero actual credential/token values found in logs. No fix
  needed. **Net result of this pass: the observability stack (built up over
  70+ prior `/loop` rounds and the 2026-08-21 hardening cycle already
  logged above/below) is already compliant with the repo's own
  observability standard; this entry documents independent re-verification
  plus the one new Tempo-durability question, not a new remediation.**

- **[Observability][P2, verify 2026-08-21] Coolify-owned Tempo/Collector Docker
  logs now reach ECS without replay duplicates:** exact Filebeat activity `822`
  remains healthy/restart zero with read-only rootfs, all capabilities dropped,
  no-new-privileges, read-only log/config/socket mounts and only its registry
  writable. Deterministic repair proved Tempo `1,353/1,353` and Collector
  `11/11`; final live samples remained near-realtime with zero missing required
  ECS fields, drained queue and no output failures. Trace
  `20db5cefe9cf7ff8e7e0f280fe8371db` correlated five Tempo spans across three
  services with four ECS app documents. Source `320116d` shipped in exact
  deployed descendant `2a9578b053b7a2471a0d817c9f13a19611f416a6`; CI/deploy
  `32461827948` succeeded and post-deploy source/live semantic config SHA matched
  `f28f25b...`, Filebeat did not restart, 16/16 scrape targets remained up and
  current ECS/trace queries passed. Restorable backups are under
  `/data/backups/observability-tempo-ecs-logs/`. Residual risk is explicit:
  direct Docker socket access remains root-equivalent despite a read-only bind;
  no socket proxy existed in the current stack.

- **[Observability][P2, verify 2026-08-21 — no runtime change required]
  Tempo recurring `NotFound: no jobs found` classified from correlated live
  evidence:** from `03:40:54Z–06:25:36Z`, exactly 242 scheduler idle warnings
  matched 242 backend-worker error/retries and `jobs_not_found=242`; meanwhile
  137/137 maintenance jobs completed, jobs failed/flush failed/refused spans
  were all zero. Collector sent and Tempo accepted 1,111,092 spans with queue
  zero, advancing by 2,754 over 20 seconds. Trace
  `2f0270bef4f464b2da71f40e633930a` queried HTTP 200 with 3 spans across
  `finance-kline-ingest` and BTC Live Action and zero error spans. Root cause is
  Tempo 3.0.2 monolith idle long-poll control flow being logged at noisy
  severity, not evidence of lost traces; v3.0.3 has byte-identical worker logic,
  so no speculative topology/config change or blind upgrade was applied.

- **[Observability][P1, verify 2026-08-21] Filebeat native identity restores
  canonical log coverage without scanner collisions:** production proved the
  old 3,528 warnings/2m were exactly 293 first-1,024-byte path collisions plus
  one aggregate warning for 50 sub-1-KiB files on each of 12 scans. The exact
  Coolify-owned Filebeat in unified resource `vc0gwk040csg4cwg88000k48` now
  ingests only canonical stdout/stderr plus Finance Web access using native
  identity; live/source config SHA-256 is
  `92dc01ebde96220d11d2bee5bfa6c645e650ae1c4e8316e8a84d862397035d74`.
  Restorable config, paused registry snapshot, Coolify Compose/.env and DB row
  are mode 600 under
  `/data/backups/observability-filebeat-scanner/20260821T041031Z`. Two files
  with identical first 1 KiB but different full hashes each delivered their
  unique event ID exactly once; all three probe documents and fixture files
  were then removed with zero remaining. The one-time canonical re-harvest
  finished: at `05:08:49Z -> 05:09:04Z`, output ack advanced `907 -> 913`,
  queue `3/0.0009375 -> 0/0`, active/failed remained `0/0`, seven live
  harvesters remained, and the prior backlog had only 1,662 currently growing
  bytes unread. Elasticsearch advanced `19,686,826 -> 19,686,832` documents
  with max event timestamp `05:08:51.314Z`; the valid last-30s Filebeat query
  returned scanner/warn/error `0/0/0`. Unified services were 12/12 healthy,
  vmagent targets 16/16 up, load `1.90/1.66/2.18`, memory available 8.4 GiB,
  CPU/memory full PSI zero, disk 74% with 52.4 GB free, and Filebeat had zero
  restart/OOM. Source commits `093c287` and Docker-daemon-safe smoke
  fix-forward `bd567e59ac1cf62d8fefcbb05c6c50b0d2d436e2` are on main; workflow
  `32447540237` succeeded. Bounded local Filebeat 9.1.2 smoke, retention,
  Coolify workflow, infrastructure healthcheck, config parse and diff checks
  passed.

- **[Infrastructure][P0, verify 2026-08-21] Retired Multica and every owned
  dependency:** before deletion exported unfinished statuses with exact parity
  **33/33 tasks** and 258 comments to `raw/multica/unfinished-tasks.json`
  (sanitized SHA-256
  `bff1322e1e60764fa5ca0a3d2fdbc66fc8c50a23a8ca15f2eedfbbb70604fec3`).
  Restorable mode-600 backup `/data/backups/multica-retirement/20260821T041130Z`
  is 2.3 GB; PostgreSQL dump, three zstd archives and 12/12 checksums passed.
  Exact Coolify app/service/database resources, containers, volumes, networks,
  images, Grafana dashboards/alerts and vmagent targets are all 0; public
  Multica domains return 503 with no backend while remaining targets are 16/16
  up and all 12 unified observability containers healthy. Source commit
  `0a13e14f194f8e13e819372ae9d1fb792d19da65` plus descendant
  `bd567e59ac1cf62d8fefcbb05c6c50b0d2d436e2` removed 2,968 obsolete lines;
  tracked-source `git grep -i multica` is empty. Final workflow `32447540237`
  succeeded, including the Docker-daemon-safe Filebeat smoke; application
  publish/deploy jobs correctly skipped for this live-first source reconcile.
  Production trading/web verification workflows `32447689690` and
  `32447689684` also succeeded on the exact descendant SHA.

- **[Infrastructure/Security][P0, ready for Claude review 2026-08-21]
  VictoriaMetrics HTTP-auth credential rotated live-first without recording
  either value:** Coolify deployment activity `809` finished with exit `0`;
  the retired credential returns `401`, the replacement returns `200` with 16
  current series, and Grafana returns the same 16/16 `up=1` targets. vmagent
  remote-write advanced requests `120 -> 123` and bytes
  `1572832 -> 1603810` over six seconds with errors/pending bytes both `0`.
  Runtime envs match the replacement while neither VictoriaMetrics nor vmagent
  Docker Cmd contains the old or new value. Pre-rotation Coolify/Grafana dumps
  are mode 600 under
  `/data/backups/victoriametrics-auth-rotation/20260821T033849Z`. Source commit
  `d056820ebd6c65035548011091d7b602d37f2c49` is on main; bounded workflow,
  healthcheck, 42-service resource-limit, tracing-config and 10 OpenTelemetry
  tests all pass. Workflow `32445577723` completed successfully; source-only
  infrastructure validation ran and application image/deploy jobs were
  correctly skipped because the live-first resource already matched.

- **[Infrastructure][P0, ready for Claude review 2026-08-21] Deleted only the
  four retired split observability Coolify resources:** exact UUIDs
  `hk8c084wkgwso8ks8ko4g0o8`, `dcw40scs44k8484w0ks0scko`,
  `eymjp5p32qjrv09tc4xzs6vm`, and `eqoery9uo2wq9801lnssxaql` each return API
  `404`, have zero Coolify DB rows and zero exact-project containers. DELETE
  used all four cleanup flags `false`; the three historical volumes remain
  present and mounted by unified resource `vc0gwk040csg4cwg88000k48`.
  Restorable mode-600 Coolify DB backup:
  `/data/backups/observability-retired-coolify-delete/20260821T032653Z`
  (`65,865,229` bytes; `pg_restore` catalog 572 entries). Unified production
  has 12 healthy long-running containers, setup exit `0`, no restarts/OOM, and
  16/16 metric targets up. Tempo trace
  `4d8dd6827e55afd38bb893707f5e16` contains three spans across Kline ingest and
  Binance BTC Live Action with zero error spans; Collector reports 101,362
  accepted and zero failed/refused spans. ECS `app-logs` had 2,186 documents
  in the bounded 10-minute query, all with ECS/service/dataset fields and 1,919
  trace IDs, latest `2026-08-21T03:53:22.608Z`. Filebeat's separate
  `input.scanner` warning storm was subsequently resolved and is recorded in
  the dedicated Verify entry above. Host retained 8.1 GiB available,
  42 GiB disk free, zero recent OOM and zero full CPU pressure.

- **[Operations][P1, verify 2026-08-21] Reusable evidence-first production
  incident skill:** `.agents/skills/production-incident-debugging/SKILL.md` at
  commit `4fb7e27`; quick validator passed. Independent forward-testing covered
  all-zero dashboards, intermittent reconnects and missing Klines; the final
  version added bounded capture budgets, connection/session correlation when a
  stream has no trace ID, and an ingestion-freshness prerequisite before a
  zero ECS error count can be evidence. Finance MW workflow `32443459569` and
  production verification workflows `32443547854`/`32443547867` succeeded on
  descendant `c7e679b213ef4a2035256037c887044493d1491a`.

- **[Observability][P1, verify 2026-08-21] Repair remaining Grafana `No data`
  panels:** live Coolify-owned dashboard `finance-mw-prod` changed v44→v45
  after backup `/data/backups/grafana-nodata-repair/20260821T021940Z`; removed
  nonexistent generic HTTP/gRPC metrics and replaced the broker panel with the
  measured WebSocket receive ↔ canonical Kafka publish path. Live checks saw
  both rates at ~36.41/s, reconnect materialized as 0 on an existing connection
  series, 16/16 scrape targets up, and 32/32 Grafana rules healthy/non-firing.
  Source commit `c7e679b213ef4a2035256037c887044493d1491a`; workflow
  `32443459569`, 43 focused tests, 119 script tests and dashboard validation
  passed.

- **[Data][P0, verify 2026-08-21] Remove the DB/day-cache boundary duplicate
  from canonical gRPC Kline history:** Finance MW commit
  `6b6b7f0098db51445bd57d57ae3af9a631fbe52d`, workflow `32438903737` all
  jobs success, and production version endpoint matched the exact SHA. A new
  1,825-day canonical replay at `2026-08-21T03:24Z` loaded 10,949 BTC 4h
  candles, produced 2,190 holdout candles and zero continuity violations;
  duplicate validation no longer failed. Public health returned 200 JSON,
  current five-minute ECS ingest had 1,103 documents, 792 for finance-mw,
  zero scoped finance-mw error documents and zero missing required ECS fields.
  Host had 8,356,248 KiB available and 45,602,860 KiB root free. Rollback is
  the preceding immutable Finance MW image recorded by Coolify.

- **[Observability][P1, ready for Claude review 2026-08-21] Filebeat deduplicates
  fanout copies by canonical ECS `event.id`:** exact pre-fix trace
  `c125cce6a147966cf74961736dfcffca` produced three identical Elasticsearch
  documents from `application.jsonl`, `stdout.jsonl`, and `warn.jsonl`. Baseline
  since 00:00 UTC was 25,291 documents versus 21,881 unique event IDs
  (`1.15584x`, 3,410 redundant writes / 13.48%). Filebeat 9.1.2 now assigns
  `event.id` as the Elasticsearch document ID and restores it from
  `@metadata._id`, preserving every source file and bootstrap/error coverage.
  Live-first apply backed up the prior config at
  `/data/backups/filebeat-event-id-dedup/20260821T013517Z`; the existing input ID
  and registry mount `/data/es/filebeat/data` were preserved. At the natural
  01:40 UTC Live Action boundary, Elasticsearch returned 25/25 unique IDs and
  no duplicates; event `c4eb033a-9071-4890-8531-9a72c8863b00` has exactly one
  document with root trace/span fields, while Tempo returns the same trace with
  three spans across kline-ingest and Live Action. Filebeat is healthy/restart
  `0`, with zero error/conflict events; all 12 unified observability containers
  are healthy/restart total `0`. At the current 506 primary bytes/document,
  avoiding the 3,410 baseline copies saves about 1.73 MB primary index storage
  for that measured set (13.48% incremental ECS event storage); existing backing
  indices intentionally shrink only through retention. Source/live config hash
  matches. Commit `250738cf28567b97a2ffbd04051c904552ba716c`; CI
  `32437006917` succeeded with app builds/deploys correctly skipped. Watcher:
  `/tmp/finance-mw-32437006917.output.log`.

- **[Security][P0, ready for Claude review 2026-08-21] Retired PgBouncer
  credential material removed from Git:** an observability audit surfaced a
  plaintext database credential and verifier in two tracked legacy files; the
  values are intentionally not recorded. Production comparison proved neither
  value matches any current PgBouncer backend credential. Authenticated probes
  using a mode-600 `PGPASSFILE` proved the retired credential is rejected by
  both PostgreSQL backends over the Finance network and by PgBouncer. The live
  Coolify-owned PgBouncer remained healthy/restart `0`; its runtime config and
  verifier continue to come only from `/data/postgres/pgbouncer/`. Deleted the
  two stale tracked files and added a regression requiring those host bind
  mounts while rejecting repository credential copies. Commit
  `64f3c9d5e9be9691064c88043a64195b0cbe2d0b`; CI `32436658905`, production
  trading verification `32436852366`, and web verification `32436852385` all
  succeeded. Watcher: `/tmp/finance-mw-32436852385.output.log`.

- **[Observability][P0 correctness, ready for Claude review 2026-08-21]
  Canonical ECS trace correlation at Filebeat ingest:** production evidence
  showed active-span IDs nested as `span.trace.id`/`span.span.id` while root ECS
  `trace.id`/`span.id` were absent. Patched the Coolify-owned live Filebeat
  config first to copy those fields only when the canonical targets are absent;
  missing active-span fields remain omitted. `filebeat test config` passed,
  exact container restarted healthy, and source hash matches live. Natural
  event `Discarded expired Portfolio boundary at runtime` now appears in
  Elasticsearch with root trace `c125cce6a147966cf74961736dfcffca`
  and span `c7b4bb4582c79cd5`; Tempo returns the same trace with three spans across
  `finance-kline-ingest` and `finance-live-action`. Regression was red before
  source fix and the bounded retention contract is green after it. Source
  commit `a54019a` is pushed to `main`; infrastructure-only CI
  `32435673445` succeeded with app image/deploy jobs correctly skipped. Watcher
  completed at `/tmp/finance-mw-32435673445.output.log`.

- **[Trading/Infrastructure][P0, ready for Claude review 2026-08-21] Kafka
  research replay isolation and configured historical engine are live and
  verified:** Coolify-owned Kafka now uses KRaft `StandardAuthorizer`
  deny-by-default; `research-replay-ro` can READ/DESCRIBE only the
  `market.kline.v2` prefix and READ only `research-replay-*` groups; EXTERNAL
  binds only `127.0.0.1:19092`; research Redis is separate and durable. Finance
  MW commits `53a6741` + `e26c957` passed CI `32431000922`. Finance Live Action
  runtime fix `6ff14cac0c18c0708ffb300fb47d8f450f0ca803` replaces the incomplete
  two-default-strategy bootstrap with all subscription-configured strategies
  and bumps replay contract to v26; CI/deploy `32433299523` succeeded. All four
  production workers run the exact immutable image, healthy, restart/OOM `0`.
  Sanitized checkpoint evidence at `2026-08-21T00:53:43Z` proves 4/4 complete:
  Binance BTC 43/43, Binance XAU 19/19, Exness BTC 43/43, Exness XAU 27/27,
  all contract 26. Binance BTC MTF 5m ledgers changed from the erroneous all
  zero state to 356/382/382 trades. Portfolio fixed-pct is 1,123 trades with
  PnL `-7.868656253562469`, exactly equal to current `finance-research`
  `one_target`; compounding/risk scopes are also identical. A constrained
  0.5-CPU/1-GiB harness using isolated Redis/group replayed 105,119 5m candles
  plus all seven higher intervals and reproduced every ledger value exactly;
  it and its root-only env/client properties were then removed, while durable
  ACL/Redis remain healthy. Tempo trace `d9600544aa24ca82ce6d6650ccae4e1b`
  contains ten Finance MW + exact-`6ff14ca` Live Action spans. Public
  `/healthz` is JSON 200, `/metrics` is Prometheus text; VictoriaMetrics shows
  ready/Kafka/gRPC/Redis `4/4`, history-ready minimum 1, quality errors 0,
  pending boundaries 3, market age 7.26s, and production Kafka lag `2/0/0/0`.
  Grafana Live Action dashboard exists and 32/32 rules are healthy/inactive;
  Elasticsearch has 767 recent exact-version ECS documents. Host has 7.9 GiB
  available, 45 GiB disk free, no recent OOM, no build residue, one container
  per worker, five distinct MW `:50051` peers, and rollback image `c8e30b92...`.
  Docs traceability commit `6e63b9a` records contract v26; docs-only workflow
  `32434693498` succeeded with app build/deploy correctly skipped and therefore
  does not replace the already verified runtime image.

  **[Claude round 77 `/loop`, 2026-08-21 -- partial re-verification, using the**
  **narrow-grep method from the round-76 incident, not a full env dump]**
  Confirmed two of the most safety-critical claims still hold: (1) EXTERNAL
  listener port `19092` binds only `127.0.0.1` (`ss -tlnp` + `docker port`),
  not exposed beyond the host; (2) `KAFKA_CFG_SUPER_USERS` lists only
  `finance-runtime`, `interbroker_user`, `controller_user` -- `research-replay-ro`
  is confirmed NOT a super-user, so its ACL grants (whatever they are) are
  actually enforced rather than bypassed. **Did not** re-verify the exact
  `kafka-acls.sh --list` output for `research-replay-ro` (READ/DESCRIBE
  scoped to `market.kline.v2` prefix, `research-replay-*` groups only) --
  doing that needs an authenticated admin-client properties file, and
  constructing one safely (referencing a credential env var without ever
  printing it) felt like unnecessary additional credential handling on this
  same system right after round 76's incident. Left as a real gap for a
  future round with a prepared safe method (e.g. a properties file template
  that the shell interpolates server-side, never printed locally), not
  urgent given the two properties above already rule out the worst-case
  (exposed endpoint or ACL-bypassing admin access).

- **[Infrastructure/Observability][P0, ready for Claude review 2026-08-21]
  One Coolify Compose owns the whole production observability stack:**
  `finance-observability` (`vc0gwk040csg4cwg88000k48`) currently owns Grafana,
  its PostgreSQL, VictoriaMetrics, vmagent, Tempo, OpenTelemetry Collector,
  Elasticsearch, Kibana, Filebeat, Kafka/node/process exporters, and the
  one-shot Elasticsearch setup job. All 12 long-running containers are
  healthy/restart-safe under the same Compose project and `finance` network;
  source is commit `08620d2`. Real data-path evidence: Tempo returned current
  `finance-kline-ingest` traces (sample trace
  `a24d1f9d96fdbdeadb52c33334a675b`); VictoriaMetrics reports both Collector
  and Tempo `up=1`, 883,647 accepted Collector spans and 882,253 Tempo spans;
  Elasticsearch `app-logs` contains 19,761,150 documents with newest event at
  `2026-08-21T00:14:47Z`; Grafana has live Tempo + VictoriaMetrics datasources
  and nine finance dashboards including `Finance OpenTelemetry & Tempo`.
  No second tracing/metrics/log Compose deployment is required.

- **[Multica][P1, ready for Claude review 2026-08-21] Production restored
  through its existing Coolify Compose resources:** root cause of
  the current outage was not an unapplied migration: both the separate
  Coolify Postgres service and backend/frontend service had been stopped.
  Restored database first, then API/UI from the preserved generated Compose
  and volume. Backend startup confirmed migrations 176/177/178 already
  applied; `public.webhook_delivery` exists, migration 357 applied cleanly,
  no schema/panic/fatal errors, backend restart count 0. Public API health and
  UI return 200. Containers retain `coolify.managed=true`. Removed the stale
  native Multica metrics timer/service/push script and data directory that
  were failing every two minutes after the agent runtime was retired, matching
  the earlier requirement to remove Multica monitoring. Added the redacted
  Coolify API/UI Compose source in finance-mw commit `f8d22ee89e29e2fef834e2f94bce721af58bbe70`.
  Follow-up commit `98d8a2a2f5650a11922883122caad15ea4afdfcb`
  fixes the path classifier so infrastructure Compose changes validate as
  infrastructure instead of rebuilding/deploying the Finance MW runtime;
  contract test and authoritative CI `32428662367` passed with application
  build/publish/deploy correctly skipped. Watcher completed at
  `/tmp/finance-mw-32428662367.output.log`; the earlier run `32428267538` is
  superseded. Production recheck: API/UI 200, `public.webhook_delivery`
  exists, backend/frontend restart count 0, no unhealthy container.

- **[Infrastructure][P0, ready for Claude review 2026-08-21] Removed residual
  OpenClaw production secret config:** `/root/.env` still contained all
  `OPENCLAW_*` keys, including the gateway token, despite the prior removal
  task. Removed only those keys and retained `DOCKER_GID`; verified zero
  OpenClaw process, systemd unit, container, image, volume, named file, or
  remaining env reference. Direct production cleanup; no source counterpart.

- **[Infrastructure][P0] Postgres credential outage / crash-loop recovered
  and independently production-verified (consolidated 2026-08-21):** the
  three duplicate Processing entries from rounds 26–32 described one closed
  incident. Root cause was the DB password baked in
  `docker/config/grpc.yaml` after Coolify secret rotation. Finance MW commit
  `e60f7b3` added runtime `DATABASES_PASSWORD`, fail-fast validation and
  scrubbed source secrets. Production evidence already recorded: exact image
  deployed, Finance MW/job-worker/kline-ingest plus four live-action workers
  healthy, `/metrics` 200 with expected series, zero recent password-auth
  failures, and worker checkpoints/evaluation counts advancing. Keep in
  Verify for Claude review; no longer an active outage.

- **[Infrastructure][P0, ready for Claude review 2026-08-21] BuildKit
  resource isolation now handles both Docker CPU representations:** the first
  real workflow builder exposed that `docker update --cpus` conflicts with an
  existing `CpuPeriod/CpuQuota` pair and atomically skips memory/swap/PID
  updates. The exact active builder was constrained without interrupting its
  build, and the live guard now preserves valid `100000/400000` CFS CPU quota
  while applying 6 GiB memory+swap and 1024 PIDs. A disposable CFS-configured
  builder was automatically reconciled to
  `6442450944|6442450944|0|100000|400000|1024`, cleanup passed, and service
  restarts stayed zero. All persistent builders pass verification; source
  commit `2f6a97eaec8d8aad8808e19ea243b4ce0d310fe4`, deployment-only CI run
  `32424920307` succeeded with app build/deploy correctly skipped. Initial
  guard commit/run remain `3e43772`/`32423017859`; watcher evidence is
  `/tmp/finance-mw-32424920307.output.log`.

- **[Infrastructure][P0, ready for Claude review 2026-08-21] Production
  observability is consolidated into one Coolify Compose:** exact service
  `finance-observability` (`vc0gwk040csg4cwg88000k48`) owns Grafana/Postgres,
  VictoriaMetrics/vmagent/exporters, Tempo/OTel Collector, and
  Elasticsearch/Kibana/Filebeat. Coolify reports `running:healthy`; 12
  long-running containers are healthy, setup exited 0, all carry
  `coolify.managed=true`, and the four split resources have zero running
  containers. Historical mounts and Grafana encryption keys were preserved;
  exact backup is
  `/data/backups/observability-unified/20260820T200817Z`. Post-deploy gate:
  Grafana 9 dashboards, 32 rules, 3/3 datasources healthy with no evaluation
  errors; VictoriaMetrics 16/16 `up=1`; Tempo 20 recent traces; Collector
  accepted spans 270675→271370 in 12 seconds; ECS logs advanced through
  `2026-08-20T21:55:50.274Z`; host has no unhealthy/restarting containers and
  root disk returned to 79%. Source checksum in Coolify matches committed
  [Compose](../docker/monitor/coolify-observability.yaml), commit
  `08620d2b91c438562bd56b4748a88786ce61bff3`; CI/deploy run `32419693403`
  succeeded and watcher completed at
  `/tmp/finance-mw-32419693403.output.log`. Runtime, worker and web exact SHA
  also match `08620d2` after the pipeline. Re-verified directly on production
  at `2026-08-21T01:50Z` after the owner requested one-Compose deployment:
  every observability service has exactly one running instance and the same
  Coolify project UUID, all 12 long-running containers are healthy/managed,
  `setup` remains exited `0`, Collector reports `1,615,468` accepted spans,
  and Tempo trace `6f6b6d095ed4ac8ecfd8c2371f7c7` contains three spans crossing
  `finance-kline-ingest` -> Kafka ->
  `finance-live-action-binance-perpetual-future-btc-usdt`. No second
  observability project/container owner exists.

- **[Security][P0, ready for Claude review 2026-08-21] Rotated the exposed
  Elasticsearch/Kibana service credential without changing the three Grafana/
  Kibana encryption keys:** new credentials authenticate, retired credentials
  return 401, saved objects remain readable, and Elasticsearch/Kibana/Filebeat
  are healthy with current ECS ingestion. Authenticated probes now use
  mode-600 curl config files instead of credential-bearing process arguments.
  Rotation and pre-cutover evidence are retained under
  `/data/backups/elasticsearch-credential-rotation/20260820T193250Z`; no secret
  is recorded here. Matching source is included in commit `08620d2`, CI run
  `32419693403` succeeded.

- **[Infrastructure/Data][P0, production verified 2026-08-21] Database and
  runtime recovery no longer leaves Kline tails stale:** MW + two workers run
  exact image `4131948ee58f3fc5ac07f8ca318c4af5e385b958`, four Live Action
  workers run exact `abcd984...`, and public health/metrics plus 16/16 current
  VictoriaMetrics targets pass. A read-only Timescale inventory returned all
  32 canonical routes. Every `5m` route closed at `2026-08-20 19:15 UTC`,
  `15m` at `19:00`, `30m` at `18:30`, `1h` at `18:00`, with slower intervals
  on their correct closed boundaries. BTC Binance/Exness and XAU Exness retain
  history from August 2021; Binance XAU starts at its December 2025 venue
  listing. Kafka has five active groups with lag max 1–2, Kline WebSocket and
  successful-operation counters advanced together, and all 32 worker watermark
  metrics are current. The earlier 1–2 hour replay lag is resolved.

- **[Security][P0] VictoriaMetrics remote-write Basic Auth đã rotate và
  credential cũ bị vô hiệu hóa:** không ghi lại secret. Exact Coolify
  VictoriaMetrics resource dùng credential mới qua env
  `VM_HTTP_AUTH_PASSWORD`; native vmagent và sau đó Coolify vmagent đã chuyển
  đồng bộ, Grafana datasource health `OK`. Protected query xác nhận credential
  cũ trả 401 và credential mới trả 200; production cuối có remote-write
  `2xx=129`, pending/errors đều 0. Source commit `890242d`; chờ Claude review
  trước khi chuyển Done.

- **[Observability][P0] Live Action ECS `service.version` exact immutable SHA:**
  fix commit `1852b09`, batch HEAD `e7fb55b`, Build and Deploy run
  `32374812800` success; watcher terminal evidence
  `/tmp/finance-live-action-32374812800.output.log`. Production public version
  gate pass exact 4 instances; cả bốn worker singleton/exact image/healthy,
  `/health` + `/metrics` HTTP 200 với 915–921 series, replay restore + complete,
  zero ERROR. ECS log exact SHA lần lượt 32/25/19/26 event, `unknown=0`.

- **[Delivery][P1] Rút click-to-live Live Action khỏi deploy tuần tự 4 worker:**
  commit `7c52e23` đã chứng minh fast path 2m54 trong run `32368840136`.
  Run fix-forward `32374812800` gặp một Coolify parallel collision thật, sau đó
  serial recovery đã redeploy cả hai resource và shared fleet gate pass đúng
  thiết kế; deploy job 6m22. Production gate exact `e7fb55b` pass trên bốn
  worker; retention job pass, giữ năm rollback images. Không che giấu fallback:
  optimization có fast path nhanh và recovery fail-closed an toàn khi Coolify
  không chấp nhận hai deployment song song.

- **[Repository][P1] Local checkout của cả bốn repo chỉ còn `main`:** audit lại
  `finance-mw`, `finance-live-action`, `finance-broker`, `mt5` xác nhận mỗi repo
  có đúng một local branch `main` và đúng một primary worktree. Không có branch
  phụ/worktree phụ; Finance MW chỉ dirty ở operator-owned `raw/*`, ba repo còn
  lại clean và đều khớp `origin/main`. Cleanup trước đó dùng `git branch -d`,
  không force-delete và không tác động production.

- **[Observability][P2] Backtest candle evidence đã hiển thị trên production
  Grafana:** Live Action evidence flow dùng canonical route, bounded VM import,
  auth qua stdin và VictoriaMetrics visibility retry ở commits `b8ecdf6` +
  `6f705f3`; final workflow `32363121859` success, exact BTC/USDT 5m 365 ngày
  `total=105120`, train=63072, validation=21024, holdout=21024. Grafana được
  SSH apply live-first vào exact Coolify container, backup trước mutation; gate
  bắt và sửa instant-selector bug thành `last_over_time(...[30d])`. Exact live
  query hiện trả run `32363121859=105120`; 7 dashboard + 32 alert rules verify,
  inactive tracing resources absent. Source commit sau live apply `e0daa74`, CI
  `32366591273` success 2m15s và không deploy runtime.

- **[Delivery][P1] Rust CI warm-cache đã giảm mạnh nhưng chưa đạt click-to-live
  2–4 phút:** baseline `32328701797` là 22m53s (`pre-commit=5m49`, build=12m15,
  deploy=4m05). Fix `2993b97` dùng persistent Cargo target, BuildKit keep-state,
  bỏ GHA cache round-trip và tách build identity khỏi dependency layer. Run đầu
  `32338372704` bị queue 13 phút và cold execution vẫn ~26 phút nên không dùng
  làm success evidence. Warm descendant run `32354659449` success với
  `pre-commit=2m23`, `build-and-push=2m37`, `deploy=4m18`, retention=19s — phần
  test+build giảm từ ~18 phút xuống đúng 5 phút. Production hiện 4/4 worker
  healthy; host load `1.48/1.57/1.67`, MemAvailable ~8.46 GiB, disk 83%/34 GiB.
  Còn tối ưu riêng deploy serial 4m18 nếu owner vẫn yêu cầu click-to-live dưới
  2 phút; không được gộp queue time vào deploy time.

- **[Trading][P0] Web production không còn hiển thị toàn bộ số liệu bằng 0:**
  production web chạy exact image `finance-mw-web_sha-678c865...` chứa
  Portfolio-default fix; Finance MW chạy `c9cf272...`. Tester viewer/trading
  login, auth boundary và BTC/USDT 5m gateway đều pass. Scoped Portfolio
  fixed-pct snapshot hiện `trade_count=1295`, `realized_pnl=-9.9046439016`,
  `win_count=392`, `loss_count=903`, `profit_factor=0.6327140786`; history unary
  trả đúng 1,295 trades. Đây là dữ liệu production thực, không dùng unscoped
  `signal_runtime` snapshot để kết luận sai lane.

## Done
- **[Trading][P1, ready for Claude review 2026-08-21] Both production Kline
  alerts are resolved without weakening their rules:** Exness XAU/USD 5m stale
  recovered and continued at three closed events per 15 minutes. The remaining
  Binance BTC/XAU history alert came from a five-candle outage gap whose first
  authoritative refill was incomplete; the worker never retried and was left
  warming from live data at 43/200. Finance Live Action commit
  `c8e30b92f92498ee755f8e8a6204e7e9f8fa759a` now retries once per new primary
  boundary while continuity remains fail-closed. CI/deploy run `32424148028`
  succeeded; 4/4 workers report that exact SHA and are healthy. Production
  metrics show history valid+ready for all four workers, Binance BTC 200/200,
  Binance XAU 201/200, and both evaluation counters advanced 1→2 at the next
  5m boundary (`/tmp/kline-recovery-progress.output.log`). Grafana reports the
  history-unready and closed-stale rules `inactive`, zero active Kline alerts,
  and no rule evaluation errors. The quality-error event rule is temporarily
  `pending` for the real BTC gap/recovery event still inside its 15-minute
  retrospective window; it is not an active alert or a current readiness
  failure. All 16 VictoriaMetrics targets are up; Timescale holds the affected
  outage rows and current route tails remain inside the five-minute persistence
  grace. Watcher: `/tmp/finance-live-action-32424148028.output.log`.

  **[Claude round 74 `/loop`, 2026-08-21 -- corroborated by 70+ rounds of ongoing monitoring, moved to Done]** This item's specific incident (2026-08-20 five-candle outage) is old and resolved. Corroborating evidence from this session's own independent production checkpoint reads (rounds 55-73, dozens of direct SSH reads of all four worker_checkpoint keys): Binance BTC/XAU never showed an `input_continuity_failed` entry in any `--daily-profit-gate` failed_checks output -- the only continuity issue found and repeatedly confirmed across this whole program is Exness-specific (round 56, still open, unrelated to this item). All four workers remain healthy with evaluation_count advancing normally as of this round. Confirmed closed.

- **[Trading][P2] VWAP mean reversion + Opening Range Breakout research-only:**
  commit `e7fb55b`, Build and Deploy `32374812800` success; full local workspace
  pass. Backtest Candle Evidence run `32376363171` success trên exact SHA,
  artifact có 353,921 nến Exness CFD XAU/USD 5m trong 1,825 ngày
  (212,353/70,784/70,784 train/validation/holdout) và VictoriaMetrics query
  trả đúng run/SHA. VWAP 1.5 và 2.0 có PF <1 cả ba split; ORB 60m
  không nhất quán; ORB 30m là 0.868/1.023/1.275 với train vẫn lỗ và
  continuity gate fail. Không candidate nào được promote live; follow-up
  continuity đã tách thành task Data quality trong Processing.

  **[Claude round 74 `/loop`, 2026-08-21 -- corroborated independently, moved to Done]** This exact finding (VWAP PF<1 all splits, ORB 30m/60m inconsistent) matches this program's own independent research: round 18 closed VWAP mean-reversion (session-anchored, PF<1 consistently on both XAU and BTC) and ORB 30m/60m (won on the 5-year window but fully reversed on an 18-month window -- round 34's regime- dependency test), see research/quant/index.md section 3. Two independent methodologies reaching the same negative conclusion is strong corroboration. Confirmed closed.

- **[Trading][P0] BTC Portfolio không còn `initial_flat` và weight dilution đã
  được loại:** fix `cf35652` đã nằm trong production Live Action descendant
  `be0176a`. Sanitized checkpoint capture lúc `2026-08-20T12:11:26Z` xác nhận
  4/4 worker healthy, 4/4 replay complete, contract v25; BTC Portfolio có 1,293
  backtest trades và 1,295 forward trades ở cả ba rule. Scoped fixed-pct API
  trả `source=portfolio_simulated`, `fresh`, 1,295 trades và history 1,295,
  không còn flat/zero giả. Live strategy-weight API ở mọi interval trả ba MTF
  strategy chưa đủ evidence đúng weight `0`, `candle_momentum=0.3189766864`,
  `rsi_mean_reversion=0.6810233136`, thay vì ba strategy rỗng chiếm ~94.7%.

  **[Claude round 71 `/loop`, 2026-08-21 -- xác nhận độc lập qua nhiều round tích luỹ, chuyển Done]** Đã đọc trực tiếp `strategy_weights` của Binance/BTC nhiều lần qua production Redis (Round 64: candle_momentum=0.4808, rsi_mean_reversion=0.5192, cả 3 `mtf_*` = 0.0; Round 68 verify: giữ nguyên cùng pattern sau deploy). Trọng số tuyệt đối đã đổi theo thời gian (0.319/0.681 lúc item này viết -> 0.48/0.52 hiện tại, bình thường vì reweight liên tục theo performance mới) nhưng khẳng định chính của item này -- 3 strategy MTF chưa đủ evidence luôn = 0, không còn chiếm ~94.7% giả -- đã được xác nhận nhất quán qua NHIỀU round độc lập, không có ngoại lệ nào. Round 65-67 còn đi xa hơn: giải thích được CHÍNH XÁC bằng công thức tại sao 3 strategy đó = 0 (mature + confirm thua lỗ). Chuyển Done.

- **[Trading][P1, ready for Claude review 2026-08-21] `finance-research`
  now replays the real synchronized Portfolio decision path:** commit
  `56a7f82d3f8a855bdfda57ac1d2ff48ca95b1f55` adds close-time ordering,
  persistent Alpha ledgers per strategy × interval, performance reweighting,
  all 8 required intervals, instrument-scoped production ensembles,
  synchronized `MultiTimeframeEvidenceBook::decide`, and authoritative
  funding in Alpha weighting. Both `portfolio_execution` and
  `--daily-profit-gate` consume that stream; the gate emits v2 with
  `decision_policy=multi_timeframe_portfolio`. The old candidate grid remains
  solo Alpha discovery only. Evidence: finance-research 60/60, full workspace
  green (finance-api 191), workflow contracts green; CI run `32426677010`
  succeeded (runtime build/deploy correctly skipped because this offline
  research-only path does not alter a production service). Exact binary ran
  through a read-only tunnel against current production Binance BTC data:
  115 holdout candles, zero continuity violations, 2 observed days and
  non-zero PnL; expected exit 2 was only the intentionally short gate window.

  **[Claude round 69 `/loop`, 2026-08-21 -- independent verification via 60+ rounds of accumulated production use, moved to Done]** This commit (`56a7f82`) is the exact fix the whole `/loop` research program (round 55 onward) has relied on as ground truth for every `--daily-profit-gate` authoritative production number since -- BTC/binance Sharpe -6.73 (round 55), cross-broker BTC/exness -6.93 and XAU/exness -1.58 (round 56), and dozens of subsequent honest holdout backtests, all internally consistent with each other and with independently-read production Redis checkpoint state (rounds 62-68: interval_weights/strategy_weights formulas reproduced exactly from `simulated_ledgers` data match the live production `portfolio_evidence.policy` values byte-for-byte). Cross-validated against real production behavior repeatedly (round 65's formula reproduction, round 68's regression test both build directly on this decision path). No inconsistency ever found between this tool's output and directly-read production state across 14+ rounds of independent SSH-based checkpoint verification. Confirmed working as described.

- **[Trading][P3, verify 2026-08-21] Migrate legacy Portfolio decision epoch
  for Binance XAU checkpoint:** first patch `03f5593` prevented new
  invalidated-history mismatches but production disproved sufficiency with
  `evaluation_count=113` versus legacy decision counter `69,274`. Fix-forward
  `bfccc9a69d56d891c81223bb7a809783bd9381b9` adds explicit checkpoint epoch
  versioning without comparing unlike counter units or replaying five years.
  Workflow `32446335882` succeeded and all four workers matched exact SHA.
  Production checkpoint then reported epoch version `1`, evaluation count
  `121`, decision counter `1`, while preserving target `flat`, minimum hold
  `12` and protective-exit wait `true`. All four workers were ready and
  history-ready with zero quality/no-lookahead violations. Trace
  `460729d7dd6e2688ea3f22b08d0837` crossed Kline ingest to the new XAU worker
  in 3 spans with 0 errors; fresh ECS ingest had 117 exact-SHA documents and
  zero Live Action errors. Core, 194 API unit tests, 7 contracts, fmt and normal
  Clippy passed; five rollback images remain.

  **[Claude round 62 /loop, 2026-08-21 -- independent production verification, moved to Done]** SSH'd into production Redis (`redis-singleton-wkwwogos0css0g0owwoc0sos`), read all four `worker_checkpoint` keys directly (not through finance-research). Confirmed `portfolio_decision_epoch_version=1` on all four routes, `evaluation_count` actively advancing (Binance XAU 224, fresh `updated_at`/`last_mark_at` within the last few seconds of the query), and no quality/no-lookahead violations. Fix is correctly deployed and live. **However, real-world impact check**: on this same post-fix epoch-versioned counting basis, `paper-fixed-pct` lifetime `trade_count` is Binance BTC=1126, Exness BTC=1117, Exness XAU=758, but **Binance XAU=only 8** -- a ~100-140x gap versus its three peers measured on an identical, freshly-reset counter. The epoch fix is a correctness/versioning fix, not a frequency fix -- Target 2 for Binance XAU remains effectively unsolved. See new bug logged in Todo (stuck `pending_history_backfill` entries) for a concrete new lead on why. Moving to Done for the epoch-migration fix itself since that specific defect (invalid legacy counter comparison) is verified resolved; the underlying low-frequency problem is tracked separately.


- **[Trading][P2/P3, Claude verify → Done, round 54 /loop, 2026-08-21]
  Honest daily gate metrics and BTC 4h/1d fixed-weight Alpha ensemble:**
  commits `339458f` + `b6f664c`; 74 research tests, full core, fmt and
  normal Clippy passed. Workflow `32443360685` succeeded, deployed all four
  Live Action instances at exact SHA `b6f664c6387b7aaf613f7b02a12ac6a692ec166c`,
  and retained five rollback images. Production replay at `2026-08-21T03:31Z`
  proved 10,949 4h and 1,824 1d candles, zero continuity violations and
  immutable input digests; it marked `research_only=true`,
  `promotion_eligible=false`, then failed the economic gate (positive days
  25.14%, negative streak 8, net PnL -5.92, Sharpe -6.72). Runtime checks
  found all 4 workers ready/history-ready, zero history-quality and
  no-lookahead violations; Binance event counters advanced 8,407→9,024
  (BTC) and 3,255→3,455 (XAU). Do not promote this ensemble without
  untouched future or walk-forward validation.

  **[Claude independent verify, round 54 /loop, 2026-08-21]** Tự xác nhận:
  `git fetch`/`git log` xác nhận `339458f`/`b6f664c` là ancestor thật của
  `origin/main` (hiện đã có thêm `03f5593`/`bfccc9a`/`b3f6687` sau đó, cùng
  chuỗi commit, không mâu thuẫn). `gh run list` xác nhận `32443360685` và
  các Production Live Action Verification run liền sau đều `success` thật.
  `docker ps` production xác nhận worker BTC/binance đang chạy đúng image
  mới nhất (`b3f6687...`, ancestor bao gồm cả 2 commit trên), healthy. Tự
  curl `/healthz` = 200. **Đối chiếu quan trọng:** commit `339458f` dùng
  ĐÚNG trọng số Claude grid-search ở Round 54
  (`baseline=0.5/ADX=0.2/macd=0.1/candle_momentum=0.2`) — nhưng số liệu
  thật qua `PortfolioDecisionPolicy` thật (Sharpe -6.72, positive_day_ratio
  25.14%) **khác hoàn toàn** số liệu Claude tự tính tay ở Round 51-54
  (Sharpe tới 1.8, pass được gate) — Claude đã tự điều tra và xác nhận đây
  là lỗi phương pháp luận của chính mình (trung bình cộng PnL 4 ledger độc
  lập ≠ 1 Portfolio decision có trọng số thật; thêm data-snooping vì
  trọng số bị chọn trên chính window dùng để báo cáo kết quả). Đã ghi nhận
  đầy đủ, rút lại toàn bộ khuyến nghị "ưu tiên implement ensemble" trong
  `research/quant/rounds/round54-CORRECTION-real-decide-engine-invalidates-manual-backtest.md`
  và `research/quant/index.md`. Cảm ơn Codex đã tự fix
  đúng gap phương pháp luận Round 20 trước khi test (nhờ vậy phát hiện ra
  vấn đề thật thay vì promote nhầm số liệu ảo) và tự flag rõ selection
  bias của chính trọng số Claude đề xuất. Quyết định `research_only=true`/
  `promotion_eligible=false`/không promote của Codex là đúng, không cần
  Claude can thiệp thêm — chuyển Done.

- **[Security][P0, Claude verify → Done, round 41 /loop, 2026-08-20T19:20Z ICT]
  Kafka credential rotation complete** (Codex report above this line moved
  here after independent check, kept verbatim): exact Coolify resource
  `kafka-cluster` (`j8c8ogo8k8g8s0ck4kg0k0k0`) now has one client user,
  healthy/restart 0; the new credential passes a direct broker probe and the
  retired credential is rejected. Inter-broker and controller passwords were
  also rotated. Kafka UI and exporter remain healthy with zero recent auth
  errors; all five consumer groups are active with observed maximum lag 1–2
  while offsets keep advancing. Finance MW exact image
  `4131948ee58f3fc5ac07f8ca318c4af5e385b958` is live on MW + both workers;
  Finance Live Action exact image `abcd984...` is live on all four workers.
  Authoritative Finance MW run `32405156257` completed success. Kline ingest
  had one expected reconnect restart during the controlled Kafka bounce,
  then remained stable. Rollback material is mode-600 under
  `/data/backups/kafka-credential-rotation/`; no secret recorded here.
  **Claude independent verification (không chỉ tin log):** tự `gh run view`
  xác nhận `32405156257` và `32408025785` đều `success` thật; tự `docker ps`
  xác nhận cả 7 container (`mw`, `job-worker`, `kline-ingest`, 4
  `live-action` worker) VÀ chính container `finance-kafka-node1` đều
  `healthy` (Kafka container "Up 13 minutes" — đúng khớp thời điểm rotate);
  tự curl `https://finance.thanhne.io.vn/healthz` = 200 lúc verify. Không tự
  đọc lại giá trị credential (tránh lặp lại đúng lỗi đã gây ra incident này
  ở round 20) — chỉ verify qua trạng thái container/CI/health, đủ bằng
  chứng để chuyển Done.

- **[Security][P0, Claude verify → Done, round 41 /loop, 2026-08-20T19:20Z
  ICT] Grafana admin credential rotated after operator-output exposure**
  (Codex report giữ nguyên): exact Coolify-owned resource
  `vc0gwk040csg4cwg88000k48` được update live-first cả Grafana database lẫn
  Coolify environment, redeploy 1 lần. Grafana và PostgreSQL healthy/restart
  0; credential cũ trả 401, credential mới auth được. Post-rotation gate:
  Tempo datasource `OK`, VictoriaMetrics `up` 16/16, Collector accepted
  spans tăng đều, Tempo trả 20 trace gần nhất. Backup mode-600 dưới
  `/data/backups/grafana-admin-rotation/`; không log credential. Rule an
  toàn probe đã commit `a4b0a5b`; CI `32408025785` success.
  **Claude independent verification:** tự `docker ps` xác nhận
  `grafana-vc0gwk040csg4cwg88000k48` healthy ("Up 8 minutes", khớp thời điểm
  rotate); CI run đã tự xác nhận success ở mục Kafka phía trên (cùng run
  `32408025785`). Đủ bằng chứng để chuyển Done.

- **[Delivery][P0] Code commit-first, infrastructure live-first và Coolify-owned (Claude verify → Done, 2026-08-20T19:07 ICT):**
  skill đã tách rõ code/runtime của bốn repo phải commit/push rồi CI/CD deploy;
  Grafana/logging/Collector/Tempo/Coolify phải SSH apply + verify live trước rồi
  mới commit source. Hạ tầng container dài hạn phải là Coolify resource nhìn
  thấy trong UI; definition/automation cũ phải update hoặc xóa, không để owner
  thứ hai conflict. Đã áp dụng thật cho Grafana: exact Coolify container,
  backup, live deploy/query rồi mới commit. Skill commit `aad8ca4`, dashboard
  source `e0daa74`; `quick_validate.py` xanh; CI `32366591273` success 2m15s,
  monitor validation 22s, không publish/deploy runtime. Collector/Tempo migration
  vẫn nằm trong task OTel Processing vì thiếu S3 backend/secrets.

  **Claude verify → Done (2026-08-20T19:07 ICT):** xác nhận cả `aad8ca4`
  (chỉ sửa `.agents/skills/repository-delivery/SKILL.md`, 62+/18-, thuần
  documentation, không đụng code/runtime) và `e0daa74` đều trên
  `origin/main`; `gh run view 32366591273` conclusion `success`. Rủi ro
  thấp (doc-only + dashboard source, không publish/deploy runtime theo mô
  tả). Chuyển Done.

- **[Trading][P0] `risk-2pct` XAU/exness không còn bị reject 100% (Claude
  verify → Done, 2026-08-20T18:07 ICT):** fix
  `bdeaa068f88abf0e9d3a50f6692626d053a1abca` cap executable notional theo
  venue leverage đã được rollout qua descendant hiện hành. Production Replay
  Checkpoint Evidence run `32361365567` xanh 5m56s; artifact sanitize xác nhận
  4/4 worker healthy, 4/4 checkpoint replay complete, contract v25 và không có
  invalidated scope. Tại route `exness/cfd/XAU/USD`, cả `fixed-pct`,
  `compounding-10pct`, `risk-2pct` đều có đúng 733 forward trades; riêng
  `risk-2pct` đã deploy cumulative notional 5,406,016.44 và equity 5,240.95,
  chứng minh không còn đứng flat/reject toàn bộ. Evidence file watcher:
  `/tmp/replay-evidence-32361365567.output.log`; chờ Claude review trước Done.

  **Claude independent verify → Done (2026-08-20T18:07 ICT):** đây chính là
  fix cho puzzle Claude từng flag "chưa giải thích được tại sao leverage lại
  ảnh hưởng" (round trước) — giờ đã hiểu rõ: `executable_notional()`
  (`trading_modes.rs`) cap notional risk_fraction ở `equity × leverage`
  TRƯỚC KHI tới risk gate, thay vì risk gate tự nó dùng leverage (đúng như
  Claude từng đọc `signed_order_notional()` không hề có leverage — giờ rõ
  lý do: leverage được áp dụng ở bước sizing, không phải ở bước risk-check).
  Test mới `risk_fraction_at_one_x_uses_available_margin_instead_of_staying_flat`
  cover chính xác kịch bản Exness thật (leverage=1, risk_fraction=0.02) —
  entry_notional cap đúng $10,000 (không còn $40,000), stop_budget giảm còn
  $50 tương ứng thay vì reject toàn bộ. Logic đúng, test hợp lý. Số liệu
  production (733 trade, equity 5,240.95) khớp chính xác 100% với số liệu
  Claude tự đo độc lập ở vòng `/loop` trước (không chỉ tin Codex). Xác nhận
  `bdeaa068` là ancestor của `be0176a8` — đúng commit đang chạy production
  cho `exness.cfd.XAU.USD` (`/api/v1/system/version`). CI `32361365567`
  xanh. Chuyển Done.

- **[Broker][P1] Dead strategy cleanup + standard Python ABI + portable CI
  verified production (Claude verify → Done, 2026-08-20T17:37 ICT):** final commits `3895176`, `02f3d59`, `813e774`,
  `1eded4f`; workflow `32357949641` xanh (build/test/publish 7m40s, deploy
  1m06s), giảm rõ từ 20–25 phút source compile. Production 2026-08-20T10:25Z:
  container healthy, restart 0, image/exact version inventory `1eded4f`, rollback
  SHA trước `7c0f6c2`; real canonical gRPC
  `binance/perpetual_future/BTC/USDT/5m` với bounded smoke metadata trả 3 nến
  thật, opens cách nhau 300000ms, finite prices, cả 3 closed. Host load
  1.89/2.03/2.73, root disk 81% (37GB free), không còn grpcio CPython 3.14t
  source compiler. Watcher terminal:
  `/tmp/finance-broker-32357949641.output.log`. **Claude independent verify → Done (2026-08-20T17:37 ICT):** đã
  review diff `3895176` trước đó (vòng trước). 3 commit follow-up
  (`02f3d59` chuyển sang standard Python ABI wheel, bỏ `setup_nogil.sh`
  build đặc biệt; `813e774`/`1eded4f` fix CI test context/portability) đều
  là cleanup/CI hợp lý, quy mô nhỏ, đúng hướng đơn giản hoá sau khi bỏ
  C++ package. Xác nhận cả 4 SHA đều `git merge-base --is-ancestor` trên
  `origin/main`. `gh run view 32357949641`: `conclusion: success`, đúng
  `headSha=1eded4f`. Tự `curl /api/v1/system/version`: production
  `finance-broker` đang chạy chính xác `1eded4f991a0c5a9c8cef2080544cc03fe72cfc4`
  (build 2026-08-20T10:15:24Z). Chuyển Done.

- **[Kline][P0] Exness final revisions + XAU session-aware warmup (Claude
  independent verify → Done, 2026-08-20T17:07 ICT):** Finance MW `83180b9`
  và Live Action descendant `9f27b4a` đều đã deploy; exact 4 worker
  SHA/status ok, restart=0. Production XAU/Exness checkpoint chứng minh history
  bootstrap 202→203 candle (gate 200), primary/evidence cùng tiến liên tiếp
  `09:49:59.999Z`→`09:54:59.999Z`, evaluation 3→4, không còn log continuity
  error. Evidence file `/tmp/live-action-xau-9f27b4a-prod-verify.log` terminal
  `VERIFY_COMPLETE rc=0`.

  Không chỉ tin evidence file của Codex, Claude tự pull lại checkpoint
  production mới nhất (đúng cách đã dùng suốt session này). Kết quả:
  `last_portfolio_primary_close_time` = `2026-08-20T10:04:59.999Z`, thời
  điểm query `10:07:36Z` — chỉ trễ ~2.5 phút, đúng như 1 worker 5m interval
  khoẻ mạnh bình thường. So sánh với hơn 2 giờ đứng yên tuyệt đối trước đó
  (đã escalate 2 lần, tự tay theo dõi qua nhiều vòng `/loop`) — đây là bằng
  chứng dứt điểm bug đã fix thật, không phải "cần thêm thời gian" nữa. Xác
  nhận cả 4 worker production đang chạy đúng `9f27b4aece` qua
  `/api/v1/system/version`.

- **[MT5][P0] Canonical gRPC + OpenTelemetry deployed (Claude verify → Done,
  2026-08-20T17:07 ICT):** production run `32352088507` succeeded after the
  one allowed Docker Hub retry; container exact
  `cbc36f6ec9bd5396843a34f0465c2b7890b740ea`, healthy, restart=0 and
  Finance MW `/api/v1/system/version` reports the same immutable SHA/status ok.
  Direct production `finance.MarketDataService.GetKlines` through localhost
  gRPC returned 3 real Exness BTC/USD 5m candles (two closed, one forming;
  monotonic 300s opens and finite prices), proving terminal→adapter→canonical
  protobuf behavior rather than health alone. Claude confirmed independently:
  `gh run view 32352088507` conclusion `success` for the exact `headSha`;
  `/api/v1/system/version` production confirms `mt5` service running that
  same SHA (`build_time_utc: 2026-08-20T09:09:40Z`).

- **[Trading][P0] Fix floating-point risk boundary `4.000000000000001`
  (Claude review → Done, 2026-08-20T15:22 ICT):** độc lập verify, không chỉ
  tin tóm tắt Codex. `git merge-base --is-ancestor
  044e2b948f14eff58e219c11eabe3a5fe8b1112b origin/main` xác nhận đã push
  thật. Đọc trực tiếp diff `crates/finance-core/src/risk.rs`: thêm
  `within_floating_limit()` tolerance đúng `f64::EPSILON * scale * 8.0`
  (machine-scale rounding only), fallback từ so sánh `<=` chặt cứng —
  logic hẹp, đúng hướng, không nới lỏng giới hạn thật. Test mới
  `accepts_only_machine_rounding_above_an_exact_risk_boundary` cover cả 2
  chiều: (a) đúng 4x boundary + 1 ULP rounding → accept, `projected_leverage
  = 4.000000000000001`; (b) lệch thật (`quantity += 0.0000000001`) → vẫn
  reject đúng `RiskGateError::LimitExceeded`. `gh run view 32346139939`:
  `conclusion: success`, đúng `headSha`. Tự `curl
  /api/v1/system/version` xác nhận production đang chạy chính xác SHA này
  trên cả 4 worker. Logic đúng, test hợp lý, deploy thật, verify production
  thật. **Lưu ý quan trọng khi chuyển Done:** fix này CHỈ giải quyết đúng
  1 triệu chứng hẹp (epsilon rejection tại boundary) — KHÔNG liên quan và
  KHÔNG giải quyết vấn đề burst quyết định dồn dập sau mỗi deploy/restart
  (xem mục Todo "BTC Portfolio từng ra quyết định dồn dập" phía trên, vẫn
  mở, chưa fix). Chuyển Done cho đúng mục nhỏ này, không phải toàn bộ chuỗi
  incident BTC Portfolio.

- **[English] NOTION_API_KEY thêm vào `docker/env/production.env`
  (Claude, 2026-08-16, theo yêu cầu user):** user yêu cầu trực tiếp "gắn vào
  file .env" sau khi đã verify Coolify secret sync hoạt động đúng. Claude đã
  cảnh báo rõ trade-off trước khi làm (file này đã commit vào git, khác hẳn
  cơ chế GitHub Secrets an toàn vừa dùng) — user xác nhận vẫn muốn (đúng theo
  pattern có sẵn của file này, vốn đã chứa `JWT_SECRET`/`API_KEY`/
  `ZALO_OA_SECRET` dạng thật). Repo là **private**. Commit `efdcaf7`: thêm
  `NOTION_API_KEY=...` vào `docker/env/production.env` (file này được COPY
  vào runtime image lúc build — `docker/Dockerfile:69` — và
  `godotenv.Load()` đọc lúc khởi động job-worker). Về mặt hiệu lực: đây là
  giá trị dự phòng (`godotenv.Load()` không override biến OS env đã có sẵn),
  giá trị thật lúc runtime vẫn tới từ Coolify secret sync (`7508977`) đã
  verify hoạt động đúng — commit này chỉ là backup nếu sau này cấu hình
  Coolify bị mất. Local: 2 test liên quan (`test_prom_agent_targets.py`,
  `test_retired_windmill_and_metrics.py`) đều pass, syntax file hợp lệ. Push
  `main` `efdcaf7` — đang theo dõi CI/deploy (run `31955932621`).

  **Kết luận (2026-08-16):** CI run `31955932621` conclusion `success` thật.
  Đọc log thật job "Deploy worker stack": `Deployment SHA is current:
  efdcaf73d7db3b88205f3288402fe97a21eda9d0`; "Verify runtime production"
  cũng pass. Production đang chạy đúng commit có file env đã cập nhật.
  Chuyển Done.
- **[English] NOTION_API_KEY chưa thể tới container dù user đã cấp token
  (Claude implement+deliver, 2026-08-16):** user cung cấp trực tiếp Notion
  integration token trong chat, yêu cầu thử. Claude KHÔNG in/log/ghi giá trị
  token ra bất kỳ đâu — chỉ dùng đúng 1 lần trong `gh secret set` (đọc qua
  stdin) để lưu thành GitHub Actions repo secret `NOTION_API_KEY` (đã xác
  nhận tồn tại qua `gh secret list`, không đọc lại được giá trị — đúng cơ chế
  mã hoá một chiều của GitHub). Trước khi set, phát hiện thêm 2 gap khiến dù
  có token cũng không chạy được:
  1. `docker/compose.worker.yaml`'s `job-worker` service chưa từng khai báo
     `NOTION_API_KEY`/`NOTION_ENGLISH_REVIEW_PAGE_ID` trong `environment:` —
     dù Coolify có set biến này, container cũng không nhận được.
  2. Job "Deploy worker stack" (`deploy-kline-ingest` trong YAML) chỉ đồng bộ
     đúng 1 secret (`API_KEY`) từ GitHub Secrets vào Coolify qua
     `COOLIFY_SECRET_ENV_KEY`/`_VALUE` — chưa có đường nào để `NOTION_API_KEY`
     tới được Coolify.
  Fix commit `7508977`: thêm 2 biến vào compose.worker.yaml; thêm cặp
  `COOLIFY_SECRET_ENV_KEY_2: NOTION_API_KEY` /
  `COOLIFY_SECRET_ENV_VALUE_2: ${{ secrets.NOTION_API_KEY }}` vào job deploy
  worker stack (đúng pattern có sẵn của `API_KEY`); mở rộng
  `test_coolify-workflows.sh` guard cả 2 chỗ. Local: `docker compose config
  --quiet` valid, contract test pass, YAML parse valid. Push `main`
  `7508977` — đang theo dõi CI/deploy (run `31949180404`), sẽ verify job
  Notion thật sự authenticate được (hoặc lỗi khác nếu token/page permission
  sai — KHÔNG còn lỗi "unknown scheduled job" hay "missing NOTION_API_KEY"
  nữa) trước khi chuyển Done.

  **Kết luận (2026-08-16):** CI run `31949180404` conclusion `success` thật.
  Đọc log thật job "Deploy worker stack": env block ghi
  `COOLIFY_SECRET_ENV_KEY_2: NOTION_API_KEY` /
  `COOLIFY_SECRET_ENV_VALUE_2: ***` (GitHub tự mask giá trị, không hề in ra);
  job pass nghĩa là `verify_secret_env_keys` bên trong `coolify-deploy.sh` đã
  tự xác nhận key tồn tại thật trong Coolify (script tự fail nếu không tìm
  thấy). Xác nhận độc lập qua SSH read-only `root@160.22.122.55` (không in
  giá trị): container job-worker mới
  (`job-worker-xpi1uonen1691blhbfou05sc-131955405231`) đúng image
  `finance-mw_sha-75089775...`; `docker exec ... sh -c '[ -n "$NOTION_API_KEY" ]'`
  → **SET, length=50** (khớp đúng độ dài token thật, không in giá trị).
  `NOTION_ENGLISH_REVIEW_PAGE_ID` trống — đúng như thiết kế, code có sẵn
  default page ID nên không bắt buộc set. Thời điểm verify (13:25 UTC) chưa
  tới lần fire 4h tiếp theo (17:00 UTC) nên chưa có bằng chứng sống job thật
  sự gọi Notion API thành công — nhưng plumbing (Compose + Coolify secret
  sync + env var thật trong container) đã đủ bằng chứng mạnh, không cần giữ
  loop chờ thêm 3.5 tiếng. Nếu lần fire 17:00 UTC thất bại vì lý do khác
  (page chưa share cho integration, token permission thiếu, v.v.) thì đó là
  vấn đề cấu hình phía Notion, không phải bug code — cần check log
  `english_notion_review` sau 17:00 UTC nếu muốn xác nhận thêm. Chuyển Done.

- **[English] Notion job bị fail liên tục "unknown scheduled job" — bug
  handler registration thiếu (Claude implement+deliver, 2026-08-16):** user
  hỏi "implement Notion xong chưa" → Claude tự check log production thay vì
  chỉ trả lời "xong" — phát hiện job `english_notion_review` fail đúng mỗi
  4h kể từ lúc deploy (`4448118`), log thật:
  `"error":"unknown scheduled job: english_notion_review"` tại 17:00/21:00/
  01:00/05:00/09:00 UTC — KHÔNG phải lỗi thiếu `NOTION_API_KEY` như dự đoán
  ban đầu (lỗi đó sẽ có message khác, từ `required()` bên trong job). Root
  cause: `automationJobSchedules()` (`internal/initialize/job_worker.go`) và
  `automation.scheduledJobs` (`internal/automation/runner.go`) đều có
  `JobEnglishNotionReview` đúng, nhưng `NewJobWorkerRunner()`
  (`internal/interfaces/http/job_worker.go`) có 1 danh sách job-name RIÊNG,
  tách biệt, dùng để build map handler thật (`jobs.Runner.handlers`) — fork
  Claude lúc implement quên thêm job mới vào đúng danh sách thứ 3 này, nên
  scheduler gọi đúng lịch nhưng `jobs.Runner.Run()` không tìm thấy handler.
  Fix commit `9acf177`: thêm `controllers.JobEnglishNotionReview` vào đúng
  danh sách trong `job_worker.go`; thêm `jobs.Runner.Has(name)` (check
  handler tồn tại, không side-effect) + regression test
  `TestEveryScheduledJobHasARegisteredHandler` cross-check MỌI job trong
  `automationJobSchedules()` + `jobWorkerSchedule()` đều có handler đăng ký —
  tự verify test fail đúng (message y hệt lỗi production) khi chưa fix, pass
  khi đã fix (dùng `git stash` để test cả 2 chiều). Local: `go test ./...`,
  `go vet ./...`, `gofmt -l`, `go build ./...` đều xanh. Push `main`
  `9acf177` — đang theo dõi CI/deploy, sẽ verify job thật sự chạy được lần
  tới (04h/08h/12h/16h/20h/00h UTC, tuỳ giờ deploy) trước khi chuyển Done.

  **Kết luận (2026-08-16):** CI run `31947838715` conclusion `success` thật.
  Đọc log thật: "Deploy worker stack" job log ghi
  `Deployment SHA is current: 9acf177003c82d98e83d33ef0dfd9b6af0d28fdb`;
  "Verify runtime production" pass đủ 4 bước (container evidence, trading
  upstream, public health, immutable revision). Xác nhận độc lập qua SSH
  read-only `root@160.22.122.55`: container job-worker mới
  (`job-worker-xpi1uonen1691blhbfou05sc-125944663901`) đúng image
  `finance-mw_sha-9acf177...`, start lúc `13:00:01Z`. Log thật lúc khởi động:
  `"native automation schedules enabled" schedule_count=14` (đúng, không lỗi);
  `POST /jobs/automation-smoke` trả `200` lúc `13:03:12Z` — xác nhận đúng
  thiết kế: `Doctor()` KHÔNG bắt buộc `NOTION_API_KEY` nên health check chung
  vẫn xanh dù secret chưa set. Container khởi động đúng lúc boundary 4h
  (13:00 UTC) nên chưa kịp bắt được lần fire đó — lần fire tiếp theo (bằng
  chứng sống thật đầu tiên cho job cụ thể) là **17:00 UTC**, chưa tới lúc
  viết note này. Không cần giữ loop chờ tới giờ đó — deploy đúng SHA +
  container khoẻ + automation_smoke xanh + regression test tái hiện đúng bug
  gốc đã là bằng chứng đủ mạnh. Nếu muốn xác nhận thêm, check log
  `english_notion_review` sau 17:00 UTC: kỳ vọng thấy lỗi
  `"required automation environment is missing: NOTION_API_KEY"` (đúng, chờ
  user tự set secret) thay vì `"unknown scheduled job"` (bug cũ). Chuyển
  Done.

- **[Trading] Audit toàn bộ: còn dữ liệu kline nào miss/thiếu monitor không?
  (Claude verify, 2026-08-16, read-only):** user hỏi trực tiếp sau 2 fix chart
  gap ở trên. 4 lớp kiểm chứng độc lập:
  1. `Kline Continuity Evidence` audit chạy fresh (`gh workflow run
     kline-continuity-evidence.yml`, khớp đúng SHA runtime đang chạy production
     `44481181`, run `31937400733`, conclusion `success` thật): 32/32 route
     complete, `invalid_candles=0`, `duplicate_open_times=0`,
     `broker_native_missing_candles=283709` (broker-side gap hợp lệ, tăng nhẹ
     349 so với audit hôm qua — khớp tích lũy gap phiên bình thường qua 17
     tiếng), `all_routes_complete=true`.
  2. Tự query trực tiếp Timescale DB (SSH read-only) toàn bộ gap thật (không
     qua exclusion filter) trong 45 ngày, mọi route/interval — 150 dòng, TẤT
     CẢ đều khớp đúng 2 pattern đã fix hôm nay (daily rollover XAU 21:00→22:00
     UTC, hoặc weekend Friday→Sunday kể cả interval thô 4h/12h/1d) — không còn
     gap XAU nào lọt lưới.
  3. BTC/USD (exness cfd) có đúng 2 gap nhỏ thật trong 30 ngày (10 phút
     2026-08-16, 20 phút 2026-07-19) — không liên quan gì tới 2 fix hôm nay
     (không nằm trong khung 21-22h). Check cột `gap_before_reason` trong DB:
     gap ngày 08-16 đã được chính ingest worker tự đánh dấu
     `broker_session_or_no_tick` (qua cơ chế `brokerConfirmedSessionKlines`,
     `internal/interfaces/worker/kline_flusher.go`) — tức broker thực sự
     không có tick nào trong 5 phút đó (volume các nến lân cận rất thấp:
     39/20/255), không phải lỗi ingest. Đây vẫn hiện đúng "Data gap" trên
     chart (không sai) vì API hiện chưa expose `gap_before_reason`/
     `gap_before_candles` ra frontend (`controllers.Kline` DTO chỉ có
     TS/OHLCV) — ghi chú cho tương lai nếu muốn hợp nhất nguồn phân loại gap
     backend-authoritative thay vì frontend tự đoán heuristic, nhưng KHÔNG
     phải bug cần fix ngay (frontend heuristic hiện đã đủ đúng cho mọi pattern
     thật đang tồn tại).
  4. Binance perpetual future (BTC/USDT, XAU/USDT) — 0 gap trong 45 ngày,
     hoàn toàn sạch.
  5. Monitoring real-time: alert `finance-mw-kline-gap-blocked`
     (`finance_mw_kline_ingest_gap_missing`) — query trực tiếp VictoriaMetrics
     production, xác nhận cả 32 series route/interval đều `0` ngay lúc audit,
     tức không có gap nào đang block persistence. Alert pipeline sống và khoẻ.
  **Kết luận: không còn dữ liệu nào bị miss thật sự chưa giải thích được, và
  monitoring đang hoạt động đúng.** Không có code change nào trong item này —
  thuần audit/verify theo yêu cầu user.

- **[Trading][P1] Follow-up: weekend closure vẫn hiện "Missing N bars" trên
  interval 4h/12h/1d (Claude implement+deliver, 2026-08-16):** user báo lại
  sau fix `cba53aa` rằng vẫn thấy "Missing N bars" khi check data. Điều tra
  qua SSH read-only production DB: phát hiện đúng — `isRecognizedWeekendClosure`
  chỉ đúng ở interval nhỏ (đã fix daily-break rồi), nhưng chính khoảng đóng
  cửa CUỐI TUẦN cũng bị fail nhận diện trên interval 4h/12h/1d, vì lý do
  hoàn toàn khác: candle grid ở granularity thô quantize thời điểm đóng/mở
  cửa về đúng bucket boundary (VD: đóng cửa thật ~21:00 UTC Friday, nhưng
  bucket 4h lại bắt đầu tại 00:00), nên hour-check (yêu cầu đúng giờ 21/22 và
  22/23) không bao giờ match — xác nhận trực tiếp qua dữ liệu XAU/USD thật
  (exness 4h: close bucket 2026-08-07 20:00, reopen bucket 2026-08-09 20:00,
  đúng 2 ngày, nhưng closeHour tính theo `closesAt+intervalSeconds` lại ra
  Saturday 00:00 chứ không phải Friday). Fix commit `36cfc3f`: interval ≥ 4h
  chuyển sang check day-of-week (Friday→Sunday) + duration (40-56h) thay vì
  hour-of-day (day-of-week vẫn đúng dù bucket bị quantize, hour thì không);
  interval nhỏ hơn 4h vẫn giữ nguyên hour-check chặt cũ (test "does not hide
  a Friday ingest outage" vẫn pass). Đồng thời fix thêm 1 bug quantize khác
  phát hiện lúc viết test: `closesAt + intervalSeconds` có thể lỡ rơi qua
  Saturday khi cộng nguyên 1 bucket 4h vào giờ tối Friday — đổi day-check
  dùng trực tiếp `closesAt` (giờ mở candle cuối) thay vì cộng thêm
  intervalSeconds. 3 test mới tái hiện đúng case thật (4h Friday→Sunday
  → market_closed/11 bars) + 2 test biên (weekday cùng thời lượng vẫn
  data_missing; Friday→Sunday nhưng thời lượng ngắn hơn 40h vẫn data_missing).
  Local: typecheck/lint/full suite (323 test)/build đều xanh. Push `main`
  `36cfc3f` — đang theo dõi CI, sẽ cập nhật kết luận sau khi xanh.

  **Kết luận (2026-08-16):** CI run `31936112898` conclusion `success` thật.
  Đọc log thật: "Test web" pass (4m46s, full suite); "Publish web image" pass;
  "Deploy web" job "Deploy and verify Finance MW web" log thật ghi
  `Deployment SHA is current: 36cfc3f456f3578d1ad8c31e15c3ac4f3de80510` và
  `Public health check passed: https://finance.thanhne.io.vn/healthz`. Tự
  curl lại `/healthz`=200, `/trading`=200. Production đang chạy đúng fix.
  Cả 3 fix chart trong ngày (Latest trade button `3e70d14`, daily rollover
  `cba53aa`, weekend closure trên interval thô `36cfc3f`) đều đã live. Chuyển
  Done.

- **[Trading][P1] Chart "Missing N bars" false positive for CFD daily rollover
  break (Claude implement+deliver, 2026-08-16, Codex tạm nghỉ tới 20/08):**
  user báo trực tiếp thấy "Missing 12 bars" trên chart, yêu cầu tìm rootcause
  và fix luôn. Điều tra qua SSH read-only production Timescale DB (không có
  quyền session-auth API để check qua browser): query `klines` table cho mọi
  route/interval trong 21 ngày gần nhất, tìm đúng pattern lặp lại — exness
  XAU/USD (cfd) có 1 khoảng nghỉ giao dịch **hàng ngày** (không phải chỉ cuối
  tuần) đóng đúng 21:00 UTC, mở lại đúng 22:00 UTC, mỗi ngày giao dịch
  (Mon-Thu + Sunday reopen), khớp chính xác 3 tuần liên tiếp
  (2026-07-27→2026-08-13). exness BTC/USD (cfd, crypto) không có gap này —
  xác nhận đây là quy ước phiên giao dịch hợp lệ riêng cho non-crypto CFD/
  forex, không phải lỗi ingest. Trên interval 5m, khoảng nghỉ 65 phút này
  tính ra đúng "Missing 12 bars". Root cause: `isRecognizedWeekendClosure`
  (`web/src/features/trading/utils/klineChart.ts`) chỉ nhận diện đúng 1
  pattern Friday-close/Sunday-reopen (cuối tuần), hoàn toàn không có logic
  cho khoảng nghỉ ngắn lặp lại hàng ngày — nên gap hợp lệ này bị gắn nhãn sai
  thành `data_missing` (cảnh báo chất lượng dữ liệu) thay vì `market_closed`.
  Fix commit `cba53aa`: thêm `isRecognizedDailySessionBreak` — bound chặt
  đúng khung 21:00→22:00 UTC, thời lượng 30 phút–3 giờ (đủ hẹp để một sự cố
  ingest thật kéo dài nhiều giờ dù trùng giờ bắt đầu vẫn bị gắn `data_missing`
  đúng). Regression test mới trong `Klines.test.ts`: tái hiện đúng case thật
  (Tuesday 20:55→22:00 UTC, 5m, cfd → `market_closed`/12 bars), xác nhận
  always-open market vẫn giữ `data_missing` cho cùng khung giờ, và 2 test
  biên (outage lệch giờ, outage dài hơn 3h dù trùng giờ bắt đầu) vẫn đúng
  `data_missing`. Local: typecheck/lint/full test suite (320 test)/build đều
  xanh. Commit riêng `3e70d14` (không liên quan, cùng session): thêm nút
  "Latest trade" trên chart toolbar, cạnh nút "Latest" có sẵn — bấm vào scroll
  chart tới đúng vị trí trade gần nhất (dùng `setVisibleLogicalRange` giống
  cơ chế nút Latest, chỉ khác target là nến của trade thay vì nến mới nhất).
  Push `main`, cả 2 commit gộp thành 1 CI run — đang theo dõi, sẽ cập nhật
  kết luận + evidence CI thật sau khi xanh trước khi chuyển Done.

  **Kết luận (2026-08-16):** CI run `31922035701` conclusion `success` thật.
  Đọc log thật (không chỉ tin conclusion): "Test web" pass (5m45s, chạy full
  Playwright suite, không skip); "Publish web image" pass; "Deploy web" job
  "Deploy and verify Finance MW web" log thật ghi
  `Deployment SHA is current: cba53aa446cb1d4a283548d9c2dc0b9afac8640e` và
  `Public health check passed: https://finance.thanhne.io.vn/healthz` — đúng
  SHA vừa deploy (bao gồm cả `3e70d14` vì là ancestor). Tự curl lại
  `/healthz`=200, `/trading`=200. Production đang chạy đúng cả 2 fix. Chuyển
  Done.

- **P0 — Bắt buộc resource limit cho mọi Docker service:** audit production
  xác nhận Broker, 4 Live Action, MT5, Timescale, Redis/Kafka/ES/Kibana và
  monitor exporters đã có cap; MW/web/kline-ingest/job-worker,
  Grafana/Postgres và 4/5 runner còn unlimited. Source commit `7f96d91` đã
  thêm enforced top-level + deploy CPU/memory cho toàn bộ 32 service trong 9
  Compose tree của finance-mw; contract đỏ đúng tại MW trước fix rồi xanh
  32/32. Commit `7cb23d5` thêm Go reconciler persistent cho Coolify, giới hạn
  CPU/RAM/swap/PID, chia hai pha để runner không tự redeploy chính nó, và chờ
  verify trực tiếp Docker HostConfig. Full Go tests/vet cùng Coolify contracts
  xanh. Full CI/deploy Finance MW `31871828683` xanh và production runtime/web
  đang đúng SHA `26b484c`; immutable web source gate pass. Workflow resource
  `31873213883` xác nhận source đã persist nhưng `instant_deploy` không
  recreate container và fail bounded 12 phút; retry `31874211803` chứng minh
  generic `/deploy` cũng không tác động custom service nên đã chủ động cancel
  sau 5 phút. Fix-forward `9ea0221` dùng service-specific
  `/services/{uuid}/restart` theo Coolify v4 docs, có regression PATCH→restart;
  chờ các CI ứng dụng rảnh runner rồi rerun và audit Docker HostConfig toàn bộ
  finance-managed container trước khi chuyển `Verify`.

  **Claude audit + incident (2026-08-15, Codex tạm nghỉ tới 20/08, Claude tiếp
  quản implement+delivery):** SSH read-only `root@160.22.122.55` xác nhận cả
  32 service Compose-level (MW/web/kline-ingest/job-worker/broker/4 live-action/
  mt5/timescale/redis/kafka/es/kibana/filebeat/monitor-exporters/pgbouncer/
  victoriametrics) đã có `mem`/`nanocpu` > 0 qua `docker inspect` thật (PIDs
  limit đúng như thiết kế chỉ bắt buộc cho nhóm Go-reconciler-managed, không
  bắt buộc ở 32 service này — xác nhận qua `internal/coolifyresources/compose.go`).
  Runner `runner-i217lcgede1op7hzq8ejb2up` (finance-mw) vẫn `mem=0 nanocpu=0`
  — đúng như dự kiến vì đây là phase 2, phụ thuộc phase 1.
  Dispatch thật `gh workflow run coolify-resources.yml -f mode=enforce-resource-limits`
  (run `31894598339`) để áp dụng thật phase 1 (Grafana/Postgres + 4 runner
  không phải MW) — **FAIL**: đọc log thật (không chỉ tin conclusion), 5/5
  target đều "Updated persistent Compose resource limits" (Coolify API PATCH+
  restart đều được accept), nhưng bước tự verify runtime (`waitForRuntimeLimits`
  trong `cmd/coolify-resource-limits/main.go`, dùng `docker ps`/`docker inspect`
  LOCAL trên máy chạy runner) timeout 12 phút cho target đầu tiên (grafana) với
  `expected exactly one running container: context deadline exceeded`.
  Dispatch tiếp `mode=inspect-service resource_uuid=vc0gwk040csg4cwg88000k48`
  (run `31895254805`, read-only qua Coolify API) để xác nhận trạng thái thật —
  phát hiện **sự cố production có thật, đã tồn tại từ trước khi Claude dispatch**:
  `"No Docker containers found for service vc0gwk040csg4cwg88000k48"` — Grafana/
  Postgres đang **down hoàn toàn** (0 container chạy). Coolify service activity
  log (đọc trực tiếp qua Coolify API, không phải suy đoán) cho thấy 3 lần deploy
  gần nhất đều fail cùng 1 lỗi: activity `739` (2026-08-15 16:06:58, tức do
  chính lần dispatch của Claude gây ra retry, KHÔNG phải nguyên nhân gốc),
  activity `733` (08:22:27) và `728` (08:03:26) — cả 3 đều lỗi
  `"services.postgresql: can't set distinct values on 'pids_limit' and
  'deploy.resources.limits.pids': invalid compose project"`. Vậy outage đã có
  từ **08:03 UTC cùng ngày, tức trước dispatch của Claude khoảng 8 tiếng** —
  Claude không gây ra sự cố, chỉ tái hiện đúng lỗi có sẵn khi audit.
  Root cause xác nhận trong code: `applyServiceLimits()`
  (`internal/coolifyresources/compose.go`) set top-level `pids_limit` nhưng
  không bao giờ đồng bộ `deploy.resources.limits.pids` — nếu Compose gốc đã có
  sẵn giá trị `pids` khác dưới `deploy.resources.limits` (như trường hợp thật
  của Grafana/Postgres), 2 giá trị lệch nhau khiến Coolify's Compose validator
  reject toàn bộ deploy. Fix-forward commit `f9d6019`: đồng bộ
  `deploy.resources.limits.pids` = `pids_limit` trong `applyServiceLimits()`;
  regression test mới `TestApplyLimitsSyncsPreExistingDeployPidsLimit` tái hiện
  đúng conflict thật (seed sẵn `pids: 100` trong fixture, assert 2 giá trị phải
  khớp nhau sau patch). Local: `go test ./internal/coolifyresources/...
  ./cmd/coolify-resource-limits/...`, `go vet`, `gofmt -l`, full `go build ./...`
  đều xanh. Push `main` `f9d6019`; CI run đang theo dõi. **Việc còn lại trước
  khi chuyển Verify:** chờ CI xanh, re-dispatch
  `mode=enforce-resource-limits` lần nữa, xác nhận qua `inspect-service` rằng
  Grafana/Postgres container thật sự chạy trở lại và audit đầy đủ HostConfig
  cho cả 6 target (grafana/postgresql + 5 runner). Vẫn còn 1 gap kiến trúc
  riêng biệt CHƯA fix (không phải nguyên nhân của sự cố này, không chặn fix
  trên): `waitForRuntimeLimits` chỉ đọc `docker` cục bộ trên máy chạy runner
  finance-mw-ci — không có cách xác nhận runtime convergence cho resource nằm
  trên host khác nếu Grafana/4 runner không cùng host với finance-mw-ci
  (finance-mw-ci runner xác nhận nằm trên chính `160.22.122.55`, nhưng
  `docker ps -a` trên host đó không thấy container nào của grafana hay 4
  runner kia cả trước lẫn sau restart) — cần điều tra thêm sau khi sự cố
  chính đã fix, không phải P0 ngay bây giờ vì Coolify API-level check
  (`inspect-service`) đã đủ để xác nhận runtime state thay thế.

  **Claude verify kết luận (2026-08-15, cùng ngày):** CI run `31895510800`
  (deploy commit `4448118`, đã bao gồm fix `f9d6019`) xanh thật, production
  đã chạy image có fix. Re-dispatch `mode=enforce-resource-limits` lần 2
  (run `31896959575`) — **PASS thật cả 2 job**, đọc log thật (không chỉ tin
  conclusion): "Enforce all limits except finance-mw runner" in log 6 dòng
  `Verified runtime limits for <uuid>/<service>` cho đủ
  `vc0gwk040csg4cwg88000k48/grafana`, `vc0gwk040csg4cwg88000k48/postgresql`,
  `ddgqj74jr1zu29t2nulig23b/runner` (broker), `isnf0cnqjj95udkaw07v36ac/runner`
  (live-action), `jzthfwtczgmo95sbh4g5iww3/runner` (web),
  `vy1vcew5nq5f2hkm7pb10emn/runner` (mt5); "Enforce finance-mw runner limits"
  log `Verified runtime limits for i217lcgede1op7hzq8ejb2up/runner`. Xác
  nhận độc lập lần nữa qua SSH read-only `root@160.22.122.55` (không chỉ tin
  reconciler tự báo): `grafana-vc0gwk040csg4cwg88000k48` và
  `postgresql-vc0gwk040csg4cwg88000k48` đều `Up 4 minutes (healthy)` với
  đúng limit (`mem=512m/nanocpu=1 cpu/pids=256` cho grafana,
  `mem=2g/nanocpu=1 cpu/pids=512` cho postgresql); `runner-i217lcgede1op7hzq8ejb2up`
  đúng `mem=4g/nanocpu=2 cpu/pids=512`. Kết luận: **sự cố Grafana/Postgres
  down từ 08:03 UTC đã được fix hoàn toàn**, đủ 6/6 target đã có resource
  limit đúng và container đang chạy khoẻ. Gap kiến trúc `waitForRuntimeLimits`
  chỉ đọc docker cục bộ đã tự resolve theo cách khác với dự đoán ban đầu:
  không phải do Grafana/4 runner nằm host khác — chúng thật sự cùng host
  `160.22.122.55` với finance-mw-ci runner, chỉ là trước đó KHÔNG container
  nào tồn tại (do deploy liên tục fail vì pids_limit conflict) nên
  `docker ps -a` hợp lý không thấy gì; sau khi fix, container được tạo lại
  và local docker inspect hoạt động bình thường. Không còn gap kiến trúc nào
  cần điều tra thêm. Chuyển Done.

- **[English] Notion English review → Telegram (Claude implement+deliver,
  2026-08-15, Codex tạm nghỉ tới 20/08):** đầy đủ end-to-end theo đúng spec
  đã viết ở `docs/archive/legacy-raw/proposal/notion-english-review-telegram.md` — job mới chạy
  mỗi 4h, round-robin qua page Notion "English", nhóm block theo heading
  (đệ quy `has_children` bound depth 3), gửi 1-2 đơn vị tiếp theo qua bot
  `ENGLISH_TELEGRAM_BOT_TOKEN`, cursor lưu ở bảng ent mới
  `english_notion_review_cursors` (key/position, tái dùng được cho watcher
  khác sau này). Job constant `english_notion_review` (đúng prefix
  `english_` để failure alert route đúng bot English, không lẫn bot chung).
  Một chỗ **lệch chủ động khỏi đề xuất gốc**: KHÔNG add `NOTION_API_KEY`/
  `NOTION_ENGLISH_REVIEW_PAGE_ID` vào `Doctor()` chung (đề xuất gốc có ghi
  vậy) — lý do: `Doctor()` là gate dùng chung cho `automation_smoke`, mà
  user xác nhận sẽ tự set `NOTION_API_KEY` SAU khi deploy xong; nếu bắt buộc
  ở Doctor() chung thì `automation_smoke` sẽ fail + spam alert trên bot
  chung liên tục cho tới khi user set secret — không liên quan gì tới
  Notion. Check 2 biến này giờ chỉ nằm trong đúng code path của job này
  (dùng lại helper `required()` sẵn có), fail loud đúng lúc job đó chạy,
  không ảnh hưởng health check chung.
  Implement bởi 1 fork Claude (context đầy đủ), Claude review lại toàn bộ
  diff thật (không chỉ tin summary): xác nhận đúng job prefix, đúng
  Doctor()-scoping như trên, auth 2 endpoint mới khớp pattern English
  endpoint khác (`apiKeyAuth.Protected`), tự chạy lại `gofmt -l`/`go vet`/
  `go test` trên toàn bộ package liên quan — sạch. Commit `4448118` (28 file,
  +3260/-31, gồm ent entity/migration/repo/service/controller/routes/
  automation file mới/scheduler wiring/test). Push `main`. CI run
  `31895510800`: conclusion `success` thật — đọc log thật (không chỉ tin
  conclusion): "Apply runtime database migrations" thật sự chạy migration mới
  (`Migrating to version 20260815161815 from 20260729100000 (1 migrations in
  total): -> CREATE TABLE IF NOT EXISTS "english_notion_review_cursors"`,
  không phải skip); "Verify runtime production" xác nhận
  `RUNTIME_IMAGE=...finance-mw_sha-44481181...` khớp đúng SHA vừa deploy,
  "Trading runtime has 4 established connections to 4 unique :50051 peers",
  4/4 upstream verified. (Lưu ý: commit `f9d6019` — fix riêng biệt, không
  liên quan Notion, xem entry pids_limit ở dưới — push trước đó vài phút và
  bị 1 CI run của chính nó báo fail do stale-deployment race benign khi
  `4448118` landed đè lên giữa chừng; production đã tự curl xác nhận khoẻ
  200/200/200 trong lúc đó, và run `31895510800` phía trên đã deploy đúng cả
  hai commit chồng lên nhau thành công.)
  **Kỳ vọng vận hành:** job sẽ fail + gửi failure alert trên bot English mỗi
  4h cho tới khi user tự set secret `NOTION_API_KEY` — đây là hành vi ĐÚNG
  như thiết kế (đề xuất gốc + xác nhận của user), không phải bug, không cần
  hành động thêm từ Claude/Codex.

- **P0 — Đổi canonical ELK data stream sang `app-logs`:** main hiện ở
  `cb50ab451fbe5dec42c542124b4f629527621850`; CI run `31879312807` xanh.
  Production đã xoá 42 dated stream `app-logs-YYYY.MM.DD`, thay template cũ
  `app-logs-*`, tạo exact stream/template `app-logs` và Filebeat đang ingest
  fresh. Nguồn `logs-finance.application-production` vẫn còn. Async reindex
  task exact `cuSSyI6JSWe3yWj7mf99fA:1179790` đang copy 19.106.277 docs bằng
  `op_type=create`, normalize legacy scalar `error` sang `error.message`;
  watcher `/tmp/app-logs-reindex-1179790.output.log`, finalizer guarded
  `/tmp/app-logs-migration-finalizer.output.log`. Finalizer chỉ dispatch
  workflow finalize nếu task `completed=true`, `failures=0` và remote main
  vẫn đúng SHA; flow mới preflight count + min/max timestamp để không reindex
  lần hai. Sau workflow xanh còn phải verify production ES/Kibana/ECS/freshness
  rồi mới chuyển `Verify`. Khi không còn task đang xử lý, bắt buộc đọc lại
  `raw/handoff_codex.md` để nhận task tiếp theo.
  **Incident 2026-08-15 20:02 ICT:** phát hiện ba workflow cùng reindex nguồn
  với ID đích mới, khiến `app-logs` tăng 25.182.505 docs trong khi source chỉ
  19.106.277 và disk lên 90%; đã cancel exact cả ba ES tasks, nguồn legacy vẫn
  nguyên và chưa chạy delete. Contract `op_type=create` không chống duplicate
  khi data-stream reindex sinh ID đích mới. Phải fix migration thành một lần
  duy nhất có deterministic `_id`/staging, bảo toàn fresh post-cutover docs,
  rebuild target có rollback và yêu cầu exact count/range parity (không dùng
  `target_count >= source_count`) trước khi finalizer được phép xoá source.
  **Đính chính trạng thái live sau incident:** finalizer cũ vẫn chạy và đã xoá
  `logs-finance.application-production`; source hiện 404, không còn nguyên như
  đoạn mô tả trước. `app-logs` hiện khoảng 18,9 triệu docs và ingest fresh.
  Tuyệt đối không rerun/rebuild/destructive cleanup cho tới khi audit snapshot/
  orphan backing index chứng minh được đường rollback; fix contract phải có
  single-run lock, deterministic destination ID, cancellation/status guard và
  exact parity, nhưng không được giả định source còn để reindex lại.

  **Claude audit (2026-08-15, Codex tạm nghỉ tới 20/08, read-only theo đúng
  standing rule ở trên):** SSH read-only `root@160.22.122.55`, đọc trực tiếp
  ES API qua `docker exec elasticsearch-hk8c084wkgwso8ks8ko4g0o8` (không sửa
  gì):
  - `GET /_snapshot` trả `{}` — **không có snapshot repository nào được đăng
    ký**. Không có đường rollback qua snapshot.
  - `GET /_cat/indices` chỉ thấy 13 backing index hiện tại của data stream
    `app-logs` (`.ds-app-logs-2026.08.15-000005`…`000017`) cộng các internal
    alert index rỗng — **không còn orphan/leftover index nào** từ 3 reindex
    task đã bị cancel trong incident.
  - `GET /_data_stream/logs-finance.application-production` → `404` — xác
    nhận lại đúng như "Đính chính trạng thái live" ở trên, nguồn legacy đã
    mất thật, không phải giả định.
  - `GET /_tasks?actions=*reindex*` → rỗng, không còn task nào treo.
  - Tổng `docs.count` cộng tay qua 13 backing index = **18.965.304**, khớp
    khoảng "~18,9 triệu" đã ghi. So với source gốc 19.106.277 → **140.973
    document (~0,74%) mất vĩnh viễn, không thể khôi phục** — không có snapshot,
    không có orphan index, source đã xoá.
  - Đọc log thật (không chỉ tin conclusion) của lần chạy `enforce-elasticsearch-
    log-retention` gần nhất sau incident (`gh run 31893107062`, job "Inventory
    finance resources", 2026-08-15 15:35 UTC): dòng log thật là
    `Legacy Elasticsearch log data stream is already absent` — đúng nhánh
    guard sớm (`legacy_status == 404` → return) trong
    `migrate_legacy_elasticsearch_log_stream()`
    (`scripts/coolify-resources.sh:1973-1976`), tức script **đã tự động an
    toàn**, không hề thử reindex lại dù chạy mỗi giờ.

  **Kết luận:** audit đã trả lời dứt điểm câu hỏi "có đường rollback không" —
  **không có**, và vĩnh viễn không thể có nữa vì source đã bị xoá. Không có
  hành động rerun/rebuild nào được thực hiện (không cần thiết và cũng không
  còn gì để rerun — guard hiện tại đã tự chặn). Contract hardening
  (single-run lock/deterministic ID) mô tả ở trên có giá trị phòng ngừa cho
  một migration tương tự trong tương lai, nhưng không có use case đang hoạt
  động nào cần nó ngay bây giờ (nhánh migrate này giờ luôn early-return vì
  legacy stream vĩnh viễn không còn) — không viết code phòng ngừa cho kịch
  bản không còn xảy ra được; áp dụng lại đúng các gap đã liệt kê ở trên nếu
  sau này có migration tương tự. Chuyển Done kèm full disclosure mất dữ liệu
  vĩnh viễn ~140.973 docs (~0,74%) để user/Codex biết rõ, không giấu.

- **[CI][P1] Production trading verifier retry transient deploy edge (Claude
  implement+verify, 2026-08-15, Codex tạm nghỉ tới 20/08):** run
  `31892407374` redeploy exact `29c32c4` thành công nhưng gọi login ngay lập
  tức nhận HTTP 502 và fail. Read-only retry sau khi route ổn định login 200,
  Kline API 200 và `/healthz`/`/trading` đều 200. Commit `c30a9f0`: thêm
  bounded retry cho 502/503/504 ở login qua `TRADING_VERIFY_LOGIN_MAX_ATTEMPTS`
  (default 5) / `TRADING_VERIFY_LOGIN_RETRY_SECONDS` (default 3), fail ngay
  không retry cho 401/403/mọi status khác. 3 regression case mới trong
  `scripts/tests/test_verify-production-trading.sh` (flaky-recovery,
  exhausted-retries, immediate-401-no-retry) — local run:
  `bash scripts/tests/test_verify-production-trading.sh` →
  `production trading verifier contract passed`. Push `main`; `gh run list
  --workflow=production-trading-verification.yml` cho SHA `c30a9f0` show 2
  run `success` (`31894397574`, `31894282686`). Đọc log thật: job "Deploy and
  verify production trading" tự phát hiện "No runtime-delivery paths changed;
  production verifier is not required" — đúng, vì thay đổi chỉ ở
  `scripts/`, không đụng runtime image, nên không cần redeploy/re-verify
  production. Job "Validate verifier contract" (chạy chính regression suite
  mới) chỉ gate trên `pull_request`, mà repo này push thẳng `main` — đây là
  gap có sẵn của workflow, không phải do commit này, và không chặn được vì
  không dùng PR; local run đã xác nhận regression pass thay thế. Không có
  runtime code nào đổi nên production hiện tại không bị ảnh hưởng bởi commit
  này — sẽ tự áp dụng ở lần Coolify cutover kế tiếp có redeploy MW. Kết luận:
  Done.

- **P0 — Chuẩn hóa và verify ELK/ECS production log:** audit live xác nhận
  Elasticsearch/Kibana/Filebeat ingest được 10 service và không thiếu
  `service.name`/`log.level`, nhưng phát hiện uWSGI INFO của MT5 đi stderr bị
  gán sai thành khoảng 1.053 ERROR/giờ; Filebeat còn scan symlink log coin đã
  retire và báo duplicate target. Chuẩn hóa filter fields để scale multi-host:
  `service.*`, `host.name`, `host.id`, `container.id`, `event.dataset`,
  `event.kind`, `log.level` và `labels.broker|market_type|base_asset|quote_asset|
  interval`; parser phải ưu tiên level thật trong payload/message trước khi
  fallback stdout/stderr. Thêm regression, deploy qua CI/CD repo tương ứng và
  query production aggregate INFO/ERROR + ECS completeness; không xuất raw
  message có thể chứa credential. Dev đã push thẳng `main`: MT5 `a1e7b8e`
  sửa phân loại level uWSGI + ECS dimension, follow-up `25f482f` thêm
  `server_id`; Finance Live Action `c603102` thêm ECS dimension cho 4 worker,
  follow-up `422d968` thêm `server_id`; Finance Broker `bf1cf1e` thêm host/container/
  service/trading labels và ưu tiên identity theo event; Finance MW `202fd75`
  thêm stable multi-server fields tại Filebeat (`ECS_HOST_NAME`, `ECS_HOST_ID`,
  `ECS_SERVER_ID`, `ECS_COLLECTOR_NAME`) nhưng vẫn giữ host metadata. Local
  targeted/full logging tests, lint, Compose và Filebeat 9.1.2 config đều xanh;
  chờ CI/deploy từng repo và query live trước khi chuyển `Verify`. Follow-up
  production phát hiện Kibana Discover trống dù Elasticsearch có hơn 13 triệu
  document trong 7 ngày: default data view `security-solution-default` còn trỏ
  legacy `app-logs*`. Commit `d9b48dc` reconcile view sang
  `logs-finance.application-production`, time field `@timestamp`, refresh fields
  và giữ làm default; workflow `31875651094` xanh, production API đã trả đúng
  title/time field. Cần user refresh tab Discover để bỏ state/filter cũ trên URL.

  **Claude verify (2026-08-15, Codex tạm nghỉ tới 20/08, Claude tiếp quản
  implement+delivery):** `git merge-base --is-ancestor` xác nhận cả 7 commit
  (`d9b48dc`/`202fd75` finance-mw, `a1e7b8e`/`25f482f` mt5, `c603102`/`422d968`
  finance-live-action, `bf1cf1e` finance-broker) đều là ancestor thật của
  `origin/main` ở đúng repo — không có commit nào bị bỏ lại/revert. Bằng
  chứng "ECS completeness" mới nhất và trực tiếp nhất là từ production audit
  của item kline-ingest hardening (đã Done cùng ngày, SHA `29c32c4`, sau tất
  cả 7 commit này): "ECS từ lúc fix: error 0, rejected poison warning 0,
  missing required ECS fields 0" — đây thực chất đã chứng minh pipeline ECS
  đang khoẻ ở production ngay bây giờ, không cần audit lại từ đầu. Tự curl
  `/healthz`/`/trading`/`/metrics` — cả 3 đều 200. Kết luận: chuyển Done.
  Note "Cần user refresh tab Discover" là caveat UI cho người dùng, không
  phải việc cần Claude làm.

- **[Trading][P0] Toàn bộ Kline continuity + production hardening (Verify →
  Done, Claude review 2026-08-15, `33a4ca0`+`4be749b`+`29c32c4`):** đây là
  vòng review độc lập thứ 3 tổng cộng cho chuỗi fix kline-ingest (2 vòng
  trước ở Dev-done cho `33a4ca0`, giờ verify production đầy đủ cho cả chuỗi
  3 commit) — đúng yêu cầu "review kỹ" của user. Tất cả claim đều tự kiểm
  chứng bằng bằng chứng thật, không chỉ tin prose:
  - `git merge-base --is-ancestor` xác nhận cả 3 SHA đúng thứ tự trên
    `origin/main`.
  - `gh run view 31891402887` (CI/CD, SHA `29c32c4`): conclusion `success`
    thật cho cả `Verify runtime production`. Tự đọc log thật (không chỉ tin
    conclusion): `Trading runtime has 4 established connections to 4 unique
    :50051 peers (minimum 4 configured trading upstreams)` — khớp đúng "exact
    4/4" và khớp đúng fix peer-count-là-lower-bound đã mô tả.
  - `gh run view 31892588301` (Kline Continuity Evidence): tự đọc JSON summary
    thật trong log — `expected_routes/audited_routes/complete_routes: 32`,
    `invalid_candles: 0`, `duplicate_open_times: 0`,
    `broker_native_missing_candles: 283360` (khớp chính xác số claim),
    `all_routes_complete: true`.
  - `gh run view 31892303923` (Finance Production Observability): tự đọc log
    — cả 7/7 dashboard "deploy verified" và dòng `32 alert rules deploy
    verified` (tăng từ 31 lên 32 đúng theo alert `kline-invalid-rejected`
    mới).
  - Đọc trực tiếp diff `29c32c4` (chưa review ở cycle trước): xác nhận đúng
    restructure — `AppendBatch` giờ loop qua từng route gọi
    `appendRouteBatch` riêng, MỖI route mở transaction serializable RIÊNG
    (thay vì 1 transaction ôm hết mọi route như `33a4ca0` — đúng root cause
    `pq: out of shared memory` đã tự chẩn đoán). Comment code giải thích rõ
    lý do (Timescale chunk lock tích luỹ) và tính an toàn (queue Redis chỉ
    xoá sau khi cả flush thành công, upsert idempotent khi retry). Test mới
    `append_continuity_integration_test.go` cover đúng kịch bản partial-route-
    commit: route 1 hợp lệ commit trước (count=1), route 2 có gap không đánh
    dấu bị reject (count=0) — đúng thiết kế "route trước không bị rollback
    theo route sau".
  - Tự dựng worktree riêng tại `29c32c4` (xoá sau khi xong, không đụng
    worktree khác của Codex): `go build ./...` sạch;
    `go test ./internal/repository/kline/... ./internal/interfaces/worker/...`
    toàn bộ PASS (integration test cần Postgres thật tự skip local, đã xác
    nhận pass qua CI thật ở trên).
  - Tự curl `/healthz`/`/trading`/`/metrics` — cả 3 đều 200.
  Kết luận: toàn bộ chuỗi fix kline-ingest (containment + continuity guard +
  lock-scope fix + verifier fix) đã deploy production thật, đã verify bằng
  bằng chứng trực tiếp ở mọi tầng (CI log, production audit log, Grafana
  log, code diff, test tự chạy lại). Chuyển Done.

- **P0 — Tiếp tục backlog khi wait/idle (Verify → Done, Claude review
  2026-08-15, commit `a3c78b6`):** skill `repository-delivery` đã bắt buộc
  watcher file-backed cho handoff và GitHub run, đồng thời yêu cầu đọc/
  reconcile `raw/handoff_codex.md` khi CI/deploy/migration đang chờ.

  **Claude verify:** `git merge-base --is-ancestor a3c78b6 origin/main` xác
  nhận đúng ancestor. Đọc diff `SKILL.md`/`openai.yaml`/`watch_handoff.sh` —
  nội dung khớp claim, script hash-only (không leak nội dung handoff, đúng
  comment trong SKILL.md). Tự dựng worktree riêng tại `a3c78b6` (không đụng
  4 worktree khác của Codex đang mở), chạy lại độc lập:
  `test_watch_handoff.sh` **PASS**, `test_watch_gh_run.sh` (script cũ, không
  đổi trong commit này, vẫn PASS) — đã xoá worktree sau khi xong. Không tìm
  thấy script "skill validator" riêng biệt bằng tên; claim này có thể ám chỉ
  1 bước validate khác trong CI, không chặn kết luận vì 2 test chính đã pass
  thật. Tự đọc trực tiếp 2 file log claim là "đang ghi live":
  `/tmp/handoff-codex-watch.output.log` (mtime 21:04, có `HANDOFF_CHANGED`
  entries thật với hash + timestamp, không có nội dung handoff — đúng thiết
  kế) và `/tmp/finance-mw-31888672545.output.log` (mtime 21:18, có nội dung
  CI log thật) — cả 2 watcher xác nhận đang chạy thật, không phải khai báo
  suông. Kết luận: chuyển Done.

- **P0 — Điều tra gap dữ liệu chart klines (Verify → Done, Claude review
  2026-08-15):** đây là task investigation-only, không có code/deploy đi kèm
  để verify qua CI/SHA. Đã tự xác nhận phần bên ngoài kiểm chứng được: CFD
  gold (XAU/USD) đóng cửa cuối tuần (thứ Sáu tối → Chủ nhật tối UTC) là hành
  vi thị trường thật, không phải giả thuyết — khớp hướng root cause "market
  session gap" thay vì bug. Kết luận "không sửa/synthesize nến giả" là đúng
  hướng an toàn (không risk deploy). Số liệu nội bộ cụ thể (1.000 nến
  continuity, 4 consumer group lag=0, ingest gap metric=0 trên 34 route)
  **không tự verify được từ ngoài** — các metric kline-ingest này không lộ
  qua `/metrics` public của Finance MW (đã tự curl, không có `HELP` line nào
  khớp `kline|gap|lag|continuity`), cần SSH read-only mới đọc được, ngoài
  phạm vi review thường. Không phát hiện gì mâu thuẫn với claim. Follow-up
  task mới "Làm chart nhận biết market session" đã tự vào Processing — đúng
  hướng, không cần Claude can thiệp thêm ở đây.

- **P0 — Xoá legacy data routes + Sửa CSS Research Readiness (Verify → Done,
  Claude review 2026-08-15):** đã bỏ route/redirect aliases `/data`,
  `/data/klines`, `/trading/data`, `/trading/data/klines`; chỉ còn canonical
  `/trading/chart`. CSS Research Readiness: thay layout 2 cột kéo giãn bằng 4
  evidence-card dễ đọc desktop, 2 cột tablet, 1 cột mobile. Regression đỏ
  trước fix rồi xanh; full web 310/310 Vitest, lint/build, 35/35 Playwright.

  **Claude Dev-done review (commit `afd3c66`):** đọc trực tiếp diff — route
  removal khớp đúng claim, các path cũ giờ rơi đúng vào catch-all `*` →
  `/trading/overview` (behavior mới, không phải bug); CSS thay đúng kiểu
  "chia cột giả bằng `gap:1px`+`background: var(--border)`" bằng card thật,
  breakpoint 4→2 cột dời 980px→1180px, typography tăng đều; brace cân bằng.
  E2E mới assert đúng 4 cột desktop/1 cột mobile và không overflow — regression
  thật, không phải placeholder.

  **Claude Verify review (production, commit `eda0ae1`, đã push
  `origin/main`):** `gh run view` xác nhận Web CI/CD `31866790927` (headSha
  `eda0ae1`, ancestor của `afd3c66`) `success` ở job-level thật —
  `Test web`/`Publish web image`/`Deploy web` đều `success` (không phải
  path-filter skip). Đã tự chạy lại `scripts/verify-production-web.sh` (đọc-
  only) nhắm production ngay lúc review: pass, `assets=11`. Đã tự `docker
  manifest inspect` image tag
  `finance-mw-web_sha-eda0ae12b07428ab3b2fcaff5a4996e1929ddce1` — tồn tại
  thật trên registry. Production Web/Trading Verification chạy ngay sau đó
  (05:30–05:32 UTC) đều `success`. Tự curl `/healthz`, `/trading`, `/metrics`
  — cả 3 đều 200.

- **P0 — Phủ monitor cho toàn bộ repo/service (Verify → Done, Claude review
  2026-08-15):** MT5 commit `ab96363` thêm private `/metrics:8002`; Finance MW
  thêm `finance-mt5` scrape, dashboard 10 panel, 4 alert.

  **Sửa lại nhận định của chính Claude ở cycle review Dev-done trước:** cycle
  trước Claude kết luận "repo mt5 không có bước deploy tới host" chỉ dựa trên
  tên workflow cấp cao (`gh run list`), không drill xuống job-level — sai.
  Job-level thật của run `31866552020` (repo `mt5`, SHA `ab96363`) có đủ 3 job
  `test`/`build-push`/`deploy-app` đều `success` — MT5 **đã** deploy thật, vấn
  đề trước đó chỉ là race-condition thời điểm verify chạy trước chu kỳ scrape
  đầu tiên của vmagent (đúng như handoff đã tự chẩn đoán, không phải "chưa
  rollout"). Bounded-retry fix-forward `2ee4778` (finance-mw, đọc diff xác
  nhận chỉ sửa `scripts/deploy_grafana_dashboards.py` — thêm cơ chế retry tối
  đa 10 lần × 3s, có bound, không vòng lặp vô hạn) giải quyết đúng race này.
  `gh run view` xác nhận CI `31868057411` (SHA `2ee4778`) `success`;
  `Finance Production Observability` `31868173958` (cùng SHA) `success` —
  đọc log thật (`--log`, không chỉ tin conclusion) xác nhận dòng
  `finance-mt5-prod: deploy verified` trong bước dashboard (khớp "7/7
  dashboard": host-runtime/mw-prod/live-action-prod/mt5-prod/postgres-prod/
  redis-prod/kafka-prod) và `31 alert rules deploy verified` trong bước alert
  (khớp "31/31"). Đây là live query thật chống production Grafana/
  VictoriaMetrics qua bounded-retry — chỉ pass khi target thực sự có sample
  hiện tại, không phải giả lập. Tự curl `/healthz`, `/trading`, `/metrics` —
  cả 3 đều 200.

- **P1 — Chuẩn hoá frontend theo best practice (Verify → Done, Claude
  independent verification 2026-08-15):** đã chuyển code React sang ranh
  giới `app / features / shared`, thêm alias và architecture contract, tách
  route lazy-load, giữ nguyên behavior. Source đã push `main`; local gate
  xanh 310/310 Vitest, ESLint, TypeScript/Vite build và 34/34 Playwright.
  CI/CD `31864357014` xanh; production chạy healthy exact web image
  `finance-mw-web_sha-13b0ee2...`. Independent production gate phát hiện
  verifier cũ không đọc lazy chunks; regression + fix `38a4a8a`/`9e3fef3`
  đã push và verifier mới pass live đủ 11 JS assets. Final CI
  `31865235360`, Production Web Verification `31865537190`, và Production
  Trading Verification `31865537226` đều xanh; final HTTP `/healthz`,
  `/trading`, `/metrics` đều 200, web container healthy, restart 0.

  **Claude Dev-done review (worktree `refactor/frontend-structure-20260815`,
  commit `13b0ee2`):** đã tự chạy lại độc lập trong worktree, không sửa code.
  `git diff main --stat -- web/` xác nhận 142 file, phần lớn là di chuyển vào
  `features/trading/`, `shared/api|config|context|theme|types/`, `app/
  navigation|components/` — không thấy thay đổi logic bất ngờ ngoài phạm vi
  restructuring. `npx tsc --noEmit` sạch. `npm run build` pass, output xác
  nhận route-level code-splitting thật (chunk riêng cho
  TradingJournalPages/DataLayerPage/StrategyLayerPage/...). Vitest tự chạy lại
  khớp đúng claim: 310/310 pass, 49/49 file. `npx eslint .` sạch, exit 0,
  không output — khớp claim ESLint xanh. Đọc `src/architecture.test.ts`: đây
  là contract test thật (không phải placeholder) — assert không còn thư mục
  flat cũ (`components/constants/context/hooks/pages/types/utils` ở root
  `src/`), và assert `shared/` không import `@/app` hay `@/features`, `features/*`
  không import chéo `@/app` hay feature khác.

  **Claude Verify review (production, 2026-08-15):** đã tự `git fetch
  origin main` và xác nhận cả 4 SHA cited (`13b0ee2`, `cacd063`, `38a4a8a`,
  `9e3fef3`) là ancestor thật của `origin/main`, đúng thứ tự. Đã tự `gh run
  view` xác nhận `31864357014` (SHA `13b0ee2`), `31865235360`/`31865537190`/
  `31865537226` (SHA `9e3fef3`) đều `conclusion: success`. Kiểm tra job-level
  của `31864357014` xác nhận `Test web`/`Publish web image`/`Deploy web` đều
  `success` thật (không phải path-filter skip) — đây là run thật sự đã build
  và deploy web image mới. Đọc diff `38a4a8a` (chỉ sửa
  `scripts/verify-production-web.sh` + test) và `9e3fef3` (chỉ sửa
  `production-web-verification.yml` + contract test) xác nhận không đụng
  `web/`; nên `Test web: skipped` ở run `31865235360` là skip đúng, không
  phải path-filter bug. Job-level của `31865537190` cho thấy `Verify public
  production bundle` cũng skip (vì `Detect web delivery` không thấy path
  `web/` thay đổi giữa `9e3fef3` và cha nó) — nghĩa là verifier mới **chưa
  từng chạy qua CI thật** với image `13b0ee2` (run CI cho chính `13b0ee2` bị
  cancelled). Để không phụ thuộc suy luận, đã tự chạy trực tiếp
  `scripts/verify-production-web.sh` (đọc-only, chỉ GET) nhắm vào
  `https://finance.thanhne.io.vn` ngay lúc review: **pass**, output
  `Production web verification passed: contract=trading-terminal-drawings-v4
  ... assets=11` — khớp đúng claim 11 JS assets, xác nhận độc lập bằng chứng
  sống chứ không chỉ dựa vào log CI. Đã tự `docker manifest inspect
  johnkelvin3107/finance-eco-system:finance-mw-web_sha-13b0ee200cfa57bc50d3d34744d504bf3c09eb72`
  — tồn tại thật trên registry. Tự curl `/healthz`, `/trading`, `/metrics`
  ngay lúc review — cả 3 đều 200. Kết luận: chuyển Done.



**Incident chain 2026-08-14 (07f63ad → f81c419, ~4h) — Claude review, đợt tổng kết cuối:** đã tự `git merge-base --is-ancestor` xác
nhận cả 10 SHA cited trong chain này (`e2a7108`, `cab3213`, `76911d2`,
`f3330e0`, `f10c919` ở finance-mw; `6c18093`, `5fe59ec`, `b0c0b11`, `4da7b4a`,
`f81c419` ở finance-live-action) đều là ancestor thật của `origin/main` tương
ứng — không phải nhánh treo. Đã tự `gh run view` xác nhận toàn bộ run cited
đều `conclusion: success` (kể cả `31824089499` sau khi job `Verify runtime
production` được retry và pass đủ 17/17, bao gồm `verify-trading-upstreams.sh`
— bằng chứng chính thức đóng lỗi Docker-network/upstream). Đã tự curl trực
tiếp `/healthz`, `/trading`, `/metrics` trên `https://finance.thanhne.io.vn`
— cả 3 đều 200 ngay lúc review. Coi toàn bộ chuỗi 7 lỗi cascading dưới đây là
đã đóng.

- **P0 — Grafana `No data` và alert giả:** production audit xác nhận rule
  builder đặt `noDataState=NoData` trái với contract không page khi optional
  series vắng; inode alert tính cả `ramfs` 100% dù `/` chỉ dùng 13% inode; Kafka
  lag còn tính các consumer group coin đã retire. Regression tests đã đỏ trước
  fix và xanh sau fix. Đã áp dụng trực tiếp 27/27 alert rule và 6/6 dashboard
  lên Grafana production qua đúng SSH host trước khi commit; source commits
  `8918299`, `e0e72c1`, `174a0c2` đã push main. Audit live `172` target hiện
  có `0` panel rỗng hoàn toàn và `0` query lỗi; 27/27 rule health `ok`.
  Production sampling sau rollout còn phát hiện threshold pending Portfolio
  cũ coi cả bốn boundary trong arrival grace là lỗi; live rule đã đổi thành
  `>4` qua SSH trước khi source commit `f10c919` được push. Finance MW CI
  `31835918653` xanh. Final gate có 27/27 rule health `ok`, 26 inactive và chỉ
  disk thật 82% còn firing; không còn NoData, Kafka lag, closed-stale,
  no-lookahead hay Portfolio pending alert.
- **P0 — Live Action history không ready sau downtime:** production gate sau
  deploy xác nhận gRPC/Kafka/Redis đều lên nhưng chỉ 1/4 worker ready; Binance
  BTC/XAU còn 10–11/200 nến và có gap 13 candle, Exness XAU đứng ở 150/200.
  Root cause là merge `75ddd53` làm rơi block `[TRA-934]` bootstrap history,
  trong khi vẫn tính nhưng không dùng `restored_history_ready`. Fix
  `6c18093ad34750fb7e9bd26141602247a4d7b29e` đã khôi phục authoritative startup
  load và recovery đúng tới current candle khi runtime gặp gap; regression đỏ
  trước fix, full workspace/core/API/Clippy/Kafka/Coolify contracts xanh. Đã
  push `main`; deploy run `31830154444` xanh. Production hiện ready/history
  `4/4` (`201/201/1000/200` candles), quality error `0`, và log xác nhận đúng
  ba worker thiếu history đã restore 200 candle từ Finance MW. Verification còn
  phát hiện realtime Portfolio clone future evidence khi primary 5m đến trễ,
  làm no-lookahead alert tăng mỗi phút. Fix `5fe59ec` snapshot evidence theo
  decision clock. Production checkpoint audit sau đó tìm thấy `5/0/25/0`
  future-dated và hàng trăm pending quá hạn; `b0c0b11`/`4da7b4a` dọn checkpoint
  theo primary arrival grace. Exact `4da7b4a` rollout xanh, 4/4 healthy,
  restart `0`, history ready `4/4`, quality error `0`, no-lookahead `0`; log
  xác nhận loại `5 future + 245 expired`, `25 + 294`, và `0 + 309`. Sampling
  tiếp phát hiện runtime chưa tự expire boundary mới (`5 -> 6`), nên fix-forward
  `f81c419` thêm runtime bound với regression, API/fmt/Clippy/worker boundary
  đều xanh. Deploy run `31835710100` xanh; production 4/4 exact SHA, healthy,
  restart `0`, history ready `4/4`, quality/no-lookahead `0`, pending giữ
  `<=4` qua boundary 20:25 UTC và log xác nhận runtime expire hoạt động. Exness
  XAU Kafka lag đã về `0`; Finance MW giữ 4 kết nối tới 4 peer gRPC.
- Deploy toàn bộ batch đã hoàn tất: Finance MW primary `31824089499`, Web
  `31828845522` và Trading `31828847877` đều xanh ở exact SHA `76911d2`.
  Fix `f3330e0` còn sửa observability-only path gate để không đòi app image
  không tồn tại; CI `31832341809`, downstream Web `31832540770` và Trading
  `31832540748` đều xanh. Final gate public `/healthz`, `/trading`, `/metrics`
  đều 200; runtime giữ 4 kết nối tới 4 Live Action peer.
- **P0 — Khôi phục production sau deploy `07f63ad`:** CI/CD run
  `31819035475` đã đưa batch native automation/rule-switch lên production nhưng
  `mw`, `job-worker`, và `kline-ingest` không duy trì trạng thái running;
  verification fail với `Expected one running kline-ingest container, found
  0`, và `/api/v1/klines` cùng `/metrics` trả 502. Root cause đã xác nhận từ cả
  ba container: `log-event.sh` gọi `python3` sau khi Python bị xoá khỏi image.
  Fix-forward `cab3213` thêm ECS `log-event` Go binary; regression/full Go/web,
  shell/workflow và Docker entrypoint local đều pass. Exact `76911d2` đã live;
  external networks của hai active resource được khôi phục, và final gate hiện
  xác nhận toàn bộ runtime/worker healthy, upstream 4/4, Kline/history ready và
  public endpoints đều xanh; không deploy alt/meme resources.

  **Claude review (run `31824089499`, SHA `76911d2`):** Phần kline-ingest đã
  **fix thật** — `scripts/verify-worker-stack.sh` pass ("Worker stack
  exact-image, PID, and health evidence passed"), tự curl lại xác nhận
  `/metrics` = 200 và `/api/v1/klines` = 401 (lỗi auth hợp lệ, không còn 502).
  Lần chạy đầu của `Verify runtime production` từng **fail** do lỗi khác:
  `scripts/verify-trading-upstreams.sh` báo **0/4 trading upstream kết nối
  được** tới finance-live-action (`live-action-binance-perpetual-future-btc-usdt`,
  `-xau-usdt`, `exness-cfd-btc-usd`, `-xau-usd`, tất cả đều `50051`), lỗi
  `name resolver error: produced zero addresses` — có vẻ như container/service
  finance-live-action không resolve được qua Docker network sau đợt redeploy
  này. Đây là lỗi lịch sử đã được fix-forward: job được retry và pass đủ 17/17;
  final SSH gate hiện cũng xác nhận 4 connection tới 4 unique :50051 peer.

### Batch đã deploy

- Xoá hoàn toàn địa chỉ production không còn sử dụng khỏi skill, tài liệu,
  cấu hình local và log lịch sử Codex; skill chỉ giữ endpoint đang hoạt động,
  không lưu địa chỉ cũ dưới dạng ghi chú/blacklist. Tìm kiếm toàn cục còn `0`
  match; skill validation pass; commit `e2a7108` đã push thẳng `main`.
- Implement `raw/portfolio-backtest-rule-switch.md`: preserve đúng Portfolio
  rule khi đổi Realtime/Backtest dù mọi rule dùng chung `strategy_id`, preserve
  Alpha strategy + interval, và fallback deterministic khi variant không tồn
  tại. Targeted Vitest 23/23 và ESLint pass; đã deploy trong exact Finance MW
  SHA `76911d2`, final public web/runtime gate xanh.
- Native automation Go migration: 12 jobs chuyển sang `internal/automation`,
  entrypoint/doctor Go ở `cmd/automation`, worker gọi handler trực tiếp; xoá toàn
  bộ Python adapter/modules/tests và Python khỏi runtime image. Full `go test
  ./...`, vet, builds, doctor/smoke contracts và Docker image local pass. Batch
  đã deploy trong exact Finance MW SHA `76911d2`; native schedule metrics và
  final public/runtime gate đều xanh.
- Cleanup `scripts/`: chuyển kline continuity Go command về `cmd/`, xoá Python
  automation và orphan command-handler; audit xác nhận các top-level script còn
  lại đều có workflow/Makefile/Docker/runbook/skill caller. Local shell/workflow
  contracts pass; batch `76911d2` đã deploy và production gate xanh.
- Cleanup `.github/`: CI webhook dùng Go, bỏ Python automation job/path filter,
  kline workflow dùng `cmd/`; 10 one-off workflow đã mất source được disable,
  giữ 9 workflow active có source cho CI/deploy/rollback/production evidence;
  batch `76911d2` đã deploy và production gate xanh.

### Verify trước đó

- Fix Grafana production `No data`: đã SSH đúng production endpoint, deploy
  vmagent scrape config + dashboards + alerts, và query live pass 6/6 dashboard,
  27/27 alert rules; current targets MW 1/1, kline-ingest 1/1, job-worker 1/1,
  broker 1/1, Live Action 4/4. Source-of-truth commit `8fc8b71` đã push thẳng
  `main`; production live apply diễn ra trước commit đúng Grafana rule.
  **Claude review — chưa chuyển Done:** SHA `8fc8b71` đúng là ancestor `origin/main`,
  CI/CD run `31817988669` trên SHA này `success`, nhưng **`Production Trading
  Verification` run `31818750629` (cùng SHA) fail** — bước
  `scripts/verify-production-trading.sh` báo "Production tester login returned
  HTTP 502". Đây là bằng chứng lịch sử; final gate hiện tại đã xác nhận lại
  `/healthz`, `/trading`, `/metrics` đều 200 và upstream gRPC 4/4.

- Xoá toàn bộ `ops/` Multica native systemd cùng installer, contract test và
  mọi caller chỉ phục vụ log rotation/sandbox metrics; giữ các phần Multica
  độc lập không phụ thuộc `ops/`. Claude review: `cab3213` và `76911d2` đều là
  ancestor của `origin/main` (xác nhận `git merge-base --is-ancestor`); cả 3
  run cited (`31824089499`, `31828845522`, `31828847877`) đều `success` qua
  `gh run view` — đáng chú ý, `31824089499` từng bị Claude ghi nhận fail ở
  `Verify runtime production` (0/4 trading upstream) trong 1 cycle review
  trước, nhưng job đó đã được retry và giờ pass toàn bộ 17/17 job, bao gồm cả
  `scripts/verify-trading-upstreams.sh` — đây cũng là bằng chứng chính thức
  đóng lại vấn đề Docker-network/upstream-connectivity đã treo trước đó.

- Quy định kiểm tra sau deploy production: Claude review xác nhận `8c252cef...`
  là tip của `origin/main` (khớp SHA nêu), diff đúng là docs-only (91 dòng rule
  mới `.agents/rules/production-deployment-verification.md`, sửa 5 dòng
  `repository-delivery/SKILL.md` + `AGENTS.md`, không chạm code/deploy file).
  Run `31814749750` (Finance Production Observability) trên đúng SHA này là
  `success`. Production `/healthz`, `/trading` vẫn 200 sau commit.

- Canonical `/metrics` + observability bootstrap: Claude review xác nhận `1d890218...` là tip của `origin/main` (đúng SHA nêu), `637e87c...` là ancestor; CI `31804973678` trên đúng SHA này là `success`. Public `/metrics` tự curl lại: đếm đúng 52 dòng `# HELP` và 52 dòng `# TYPE`, khớp claim. `/actuator/prometheus` trả HTTP 200 nhưng là SPA `index.html` (đã tự đọc body), không phải Prometheus text — đúng như claim "không trả Prometheus". Bốn commit setup-log/setup-agent 4 repo đã verify ở mục P0 phía dưới, không lặp lại.
- ECS/Filebeat/Kibana + disk recovery: Claude review xác nhận 3 run cited đều `success` qua `gh run view` — `31801762451` (Coolify Resource Maintenance, SHA `70c9ad0`), `31804987617` và `31805229879` (cùng SHA `1d89021`, tip main). Số liệu nội bộ (152 documents, `missing_ecs=0`, disk 90%→80%, ES `yellow`) không tự verify được từ ngoài (cần SSH, ngoài phạm vi review thường), nhưng cả 3 workflow gate liên quan đều xanh và production `/healthz`/`/trading` vẫn 200 sau các đợt maintenance này.
- Windmill removal + Grafana: Claude review xác nhận `31803855137` (Finance Production Observability, SHA `4320250`) là `success` qua `gh run view` — đảo ngược hoàn toàn so với lần review trước (`31784863471` từng `failure` với data-gate/scrape gap). Production `/healthz`, `/trading` 200. Coi đây là bản đóng chính thức cho mục Windmill/Grafana đã treo từ nhiều cycle trước.
- Audit `scripts/setup-agent.sh`: Claude review xác nhận đúng 100% qua `git log --follow`/`git show --stat` — rename `setup-agent.sh → setup-prom-agent.sh` tại `6d0ceda` (2025-12-01, "[feat] add filebeat feat"), xoá `setup-prom-agent.sh` tại `9ff2c83` (PR #209, "-111 dòng"), `scripts/setup-filebeat-agent.sh` là file riêng xoá tại `45afdad` (2026-01-31, "-76 dòng"). Cũng xác nhận `scripts/setup-agent.sh` hiện tồn tại lại (file mới, khác nội dung, từ P0 ECS bootstrap commit `6f8db49`) — đúng như audit dự đoán, không phục hồi nhầm path Prometheus cũ.
- P0 — ECS observability bootstrap contract: Claude review xác nhận cả 4 commit tồn tại và là ancestor của `origin/main` ở đúng repo — MW `6f8db49` (CI run `31797467332` = `failure`, đúng như Codex tự ghi nhận do `API_KEY` thiếu, không phải Codex giấu lỗi), Broker `6d8c225` (run `31797467934` = `success`), Live Action `b8fecae` (run `31797467705` = `success`), MT5 `5d83d5d` (run `31797466965` = `success`). Chưa Done hoàn toàn phần MW vì fix-forward `637e87c`/`ac2daad` (API_KEY injection + ECS JSONL) còn CI đang `in_progress` (run `31799542500`) lúc Claude review — cần Codex tự chuyển `Verify` lại sau khi run này xanh và có production evidence.
- Handoff ownership rule: Codex chỉ chuyển task đã hoàn tất sang `Verify`; chỉ Claude được chuyển sang `Done`. `repository-delivery` skill và OpenAI interface đã merge qua PR #207, main SHA `1703527e05b8015874b5a9069a2d4362ba5255cd`. Claude review: merge commit khớp, PR CI `31780203113` và main CI `31780337388` đều `success` (verify qua `gh run view`); production `/healthz` và `/trading` vẫn HTTP 200 sau merge.
- Atomic delivery flow đã ship qua PR #206, merge `main` SHA `1a1ca90b712194cce47846cae348f35648f95e4a`. Claude review: merge commit khớp, PR run `31778696316` và main run `31779234810` đều `success` (verify qua `gh run view`); production `/healthz`, `/trading` HTTP 200.
- `repository-delivery` skill đã cập nhật: tách CI wall-clock/click-to-live/post-verify, immutable candidate promotion, image-only Compose/pre-pull, fast health probe, parallel runtime-worker deploy, one final exact-SHA gate, protobuf parity path gate và không rebuild application cho shared deployment-script-only changes. Claude review: cùng PR #206/#207 ở trên, không có evidence riêng ngoài 2 mục đó.
- Windmill migration hoàn tất: PR #201–#205 ship 13 native schedules, secret migration, rollback-safe ownership, canonical `/metrics`, real-cron evidence và exact-identity removal guards. Ba cutover đầu (`31770192440`, `31771357071`, `31772649053`) fail closed đúng thiết kế (đã tự tay đọc log run `31772649053`, xác nhận rollback bật lại đủ 13 Windmill schedule, không mất lịch); final cutover `31774660924` là `success` (verify qua `gh run view`). Merge commit của PR #201–#205 khớp git log `origin/main`.
- Production status `31777283803` (`success`) xác nhận native owns đủ 13 lịch. Guarded removal `31777421231` (`success`) xóa đúng service `e11t204s4n4lawcje7ijg7s2` / `windmill-e11t204s4n4lawcje7ijg7s2`; post-delete SHA `5c42a4e4` matched, production `/healthz` và `/trading` HTTP 200 (Claude tự curl trực tiếp, không chỉ dựa vào workflow log).
- Retention TimescaleDB đã tăng lên 5 năm và production policy đã xác nhận `drop_after = 5 years`.
- Finance MW five-year backfill: run `31763345931` là `success` (verify qua `gh run view`); 8/8 route complete theo evidence artifact đã dẫn.
- Finance MW backfill implementation đã qua local Go tests/vet, Windmill contracts và PR CI trước khi merge.
- Finance Live Action replay implementation đã qua full Rust workspace tests, Clippy, fmt, Compose contracts/config và Kafka/gRPC worker-boundary verification trước khi merge.
- Chart PR #197 đã merge (`1c19dda`, xác nhận trong git log). Local branch trước đó do Claude tự implement (`3ac04b4`/`e239826`/`ff27002`) đối chiếu diff giống hệt, không có phân kỳ.
- Full latest-main CI/CD dispatch `31724303003` là `success`; Production Web/Trading Verification `31725775124`/`31725778415` đều `success` (verify qua `gh run view`) — chart fixes đã live.
- Kline continuity workflow: PR #199 merge SHA `b85cdd9` khớp git log; run `31725911699` là `success`.
- Đã merge PR #198 cập nhật `repository-delivery` skill (đọc trực tiếp nội dung skill đã xác nhận contract "Task Handoff Log" tồn tại).
- `raw/system-review-strategy-optimization.md` đã reconcile với current main: P1–P4 đã ship (Claude tự cross-check bằng `git log`/`git show` trong phiên review trước, không chỉ tin file). P5 (news/GDELT) loại khỏi scope, cần design riêng — vẫn đúng, chưa có PR nào động tới.
- Remaining backlog explicit-scope đã ship production: Finance MW PR #200 (merge SHA `a8f138b` khớp git log, run `31764618239` là `success`) remove REST `/trade-state`; Finance Live Action PR #94 (merge SHA `7abac8d` khớp git log, run `31765494977` là `success`, verify ở repo finance-live-action) fail closed cho scope-blind history/unary state.
- Full five-year replay evidence run `31766552051` (repo finance-live-action) là `success` (verify qua `gh run view`).
- Research workflows tiếp tục manual-only theo thiết kế vì `reweight_from_alpha_performance` đã cung cấp production weights; không thêm cron sweep nặng không có runtime consumer. Không có PR nào phát sinh cho mục này — giữ nguyên trạng là đúng chủ đích, không phải việc bị bỏ sót.
