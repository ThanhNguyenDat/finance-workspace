# KAFKA_CONTROLLER_PASSWORD exposed via broad `docker exec ... env` dump (2026-08-21)

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
  read (this session's mistake, worth encoding as a standing caution — now
  codified as a standing rule, see `raw/system/promptp2claude.md` and
  `raw/system/prompt2codex.md`).

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
