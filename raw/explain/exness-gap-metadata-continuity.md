# Carry Exness gap metadata through the Kline contract into finance-research (2026-08-21)

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
