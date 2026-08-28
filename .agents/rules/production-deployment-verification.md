# Production Deployment Verification

## Completion boundary

- Treat CI success, a finished Coolify deployment, container health, and HTTP
  `200` as inputs to verification, never as proof that production works.
- Run one bounded production gate after every deployment batch. Verify every
  changed application and the shared paths it depends on.
- Require the baseline checks below for every deployment. Add the
  surface-specific checks that match the change.
- Keep checks read-only unless a separately reviewed migration, smoke command,
  or rollback workflow explicitly authorizes a mutation.

## Mandatory baseline

1. **Identity and topology**
   - Match the remote default-branch SHA, GitHub Actions run SHA, published
     immutable image, Coolify deployment, and runtime-reported build identity.
   - Verify every expected instance, not one representative container. Reject
     stale, mixed-revision, missing, restarting, or duplicate instances.
   - Distinguish a repository or infrastructure revision from the runtime image
     revision when a docs-only or infrastructure-only commit does not rebuild
     the application.
2. **Availability and routing**
   - Check the deterministic public health/readiness endpoint through the same
     route users consume and validate its status, content type, and body.
   - Do not accept an SPA fallback, proxy error page, or cached response merely
     because it returns `200`.
   - Verify affected internal HTTP or gRPC upstreams through their owning
     gateway. Do not expose private services just to test them.
3. **Changed behavior**
   - Exercise at least one representative read-only production workflow for
     each changed feature and assert meaningful response fields, not only
     transport success.
   - Verify authentication and authorization boundaries when login, sessions,
     roles, groups, or protected routes are affected.
4. **Current data and progress**
   - Prove expected data is present, fresh, correctly scoped, and complete for
     the affected broker, market type, base asset, quote asset, interval,
     layer, setup, or rule.
   - Verify worker heartbeats, processed counters, queue or consumer lag,
     checkpoints, and last-success timestamps continue to advance after the
     startup grace period. A healthy container with no progress is a failure.
5. **Observability**
   - Query canonical `/metrics` and verify Prometheus content, all expected
     current scrape targets with `up == 1`, and the metric families needed by
     the changed path. Use instant queries or freshness timestamps so retained
     historical series cannot satisfy the gate.
   - Verify affected Grafana panels return current data and affected alert
     rules evaluate without new unexpected failures or firing states.
   - Verify new ECS JSONL events reach Elasticsearch/Kibana with all required
     fields and no malformed-document increase. Inspect recent error events
     without printing credentials or secret payloads.
6. **Host safety**
   - Check CPU/load and pressure stalls, available memory and swap, disk and
     inode headroom, OOM events, restart counts, and crash loops.
   - When self-hosted runners share the production host, confirm the completed
     pipeline did not leave BuildKit, runner, or temporary artifacts consuming
     production capacity.
7. **Cleanup and recovery**
   - Keep one active production container per application after a successful
     rollout. Remove only exact reviewed stale candidate or legacy instances;
     preserve data volumes.
   - Record an immutable previous image or revision that can be rolled back.
     When deployment or rollback machinery changed, exercise the guarded
     rollback contract independently.

## Surface-specific additions

| Changed surface | Additional production evidence |
| --- | --- |
| Web | Load the changed route, assert its API payload and visible state, and check browser/API errors. |
| HTTP or gRPC API | Call the changed contract through Finance MW, verify schema and error behavior, and confirm downstream identity. |
| Kline or trading path | Check fresh candles/trades across every affected interval and scope, continuity, worker progress, PnL/risk invariants, and no duplicate processing. |
| Database or migration | Verify the expected schema revision, migration completion, pool health, representative reads, and data/backfill continuity. |
| Scheduler or automation | Verify single schedule ownership, the exact job count, next/last run, last success, and no duplicate execution. |
| Observability | Verify scrape discovery, instant metrics, dashboard queries, alert evaluation, ECS ingestion, and retention/storage health. |
| Infrastructure only | Verify the exact resource identity, service health, resource headroom, and that application health and current metrics did not regress. |

## Evidence and failure handling

- Record the commit SHA, workflow run, immutable image or deployed source SHA,
  Coolify result, verification timestamp, and concise command/query results in
  the active `.ops/changes/<change>/handoff.md`; completion archives it under
  `.ops/archive/`. Keep implementation task completion in OpenSpec. Never
  record credentials, tokens, cookies, or secret payloads.
- Advance only the authoritative OpenSpec tasks and OPS phase/status supported
  by evidence. `raw/handoff_agent.md` is a legacy human index and must not own
  `Processing`, `Verify`, or `Done` lifecycle truth.
- If any check fails, keep the task in `Processing`, identify the exact failed
  instance or invariant, fix forward or run the reviewed rollback, then repeat
  the mandatory baseline and affected surface checks. Never report deployment
  success with an unreported verification gap.
