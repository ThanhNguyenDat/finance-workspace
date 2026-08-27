---
name: production-trading-verification
description: Provision the read-only tester account and verify the production trading dashboard, authorization boundary, and finance-live-action metrics through Finance MW after a Coolify deployment.
---

# Production Trading Verification

Use this skill when a Finance MW runtime change can affect login, domain
authorization, the trading dashboard, the finance-live-action gRPC contract, or
Coolify delivery.

## Security contract

- The fixed verifier username is `tester`.
- Its role is always `viewer` and its only group is `trading`.
- That combination may read trading data, metrics, and the masked broker-key
  status already granted to trading viewers. It may not insert, rotate, or
  delete broker credentials; it never receives decrypted key material.
- It may not receive any write permission or any English, affiliate, or user
  administration permission.
- Never commit or document the verifier password. The production workflow
  generates a new random value, masks it, injects it through the Coolify secret
  environment API, and rotates the bcrypt hash on startup.
- Never print login payloads, cookies, authorization headers, or the generated
  password in workflow output.

## Delivery sequence

1. Run the repository's normal CI/CD workflow for the exact commit.
2. Require the immutable image `finance-mw_sha-<commit>` before verification.
3. Publish a pending `production/trading-verification` commit status on that
   immutable revision.
4. Redeploy that exact image through `scripts/coolify-deploy.sh` while injecting
   `PRODUCTION_TESTER_PASSWORD` as a Coolify secret.
5. Treat a deployment that has not reached a terminal healthy state within ten
   minutes as a failure requiring investigation, not as ordinary startup delay.
6. Run `scripts/verify-production-trading.sh` against
   `https://finance.thanhne.io.vn`.
7. Replace the pending commit status with success or failure and link it to the
   exact workflow run. Do not claim deployment complete without that terminal
   status.

## Required evidence

The verifier must prove all of the following in one session:

- password login succeeds and issues the normal HttpOnly session cookie and
  CSRF cookie;
- `/api/v1/auth/me` reports username `tester`, role `viewer`, and group
  `trading`;
- `/api/v1/trading-metrics` returns a typed, non-empty snapshot from the
  finance-live-action gRPC upstream for the requested symbol and interval;
- `GET /api/v1/broker/credentials` can return only the existing masked status;
- a CSRF-valid broker-credential mutation returns `403`, proving the viewer
  ceiling remains effective;
- `https://finance.thanhne.io.vn/trading` serves the production application
  shell.

The production workflow is `.github/workflows/verify-trading.yml`.
Its pull-request job runs the database authorization test and a local HTTP
contract fixture; its default-branch job performs the Coolify deployment and
real production verification.

## Commands

```bash
go test -timeout=5m ./internal/repository/auth \
  -run 'TestEnsureProductionTester' -count=1

timeout --signal=TERM --kill-after=5s 1m \
  bash scripts/tests/test_verify-production-trading.sh
```

For an authorized manual production rerun, dispatch the workflow against
`main`, optionally with an immutable 40-character `source_sha`. Do not execute
production deployment scripts directly from a laptop or an untrusted branch.

## Manual read-only SSH access (when a CI health check fails and needs a real answer)

`scripts/verify-trading-upstreams.sh` runs on a GitHub Actions self-hosted
runner that already has Docker access to production — a sandbox session does
not, by default. When that check (or any other) fails and the failure needs
eyes on an actual container, ask the user for the current host/credentials
rather than guessing from `~/.ssh/config`; entries there can be stale (wrong
`IdentityFile` path, a LAN-only IP unreachable from a sandbox) or point at the
wrong box entirely. What has worked once other than the standard config:
`ssh -A root@<host>` (agent-forwarded, `root`, no config entry needed) after
the user supplies the IP directly.

`root@160.22.122.55` is the Coolify host for finance-mw (`mw-*`,
`kline-ingest-*`, `trading-worker-*`, `english-worker-*`, `social-worker-*`,
`tvl-worker-*`, `web-*`), the four current per-instrument finance-live-action
workers, and shared Kafka, Redis, Timescale, Grafana, VictoriaMetrics,
Elasticsearch, Filebeat, finance-broker, and MT5 services. The job-worker
split into four domain workers on 2026-08-23; this container-name list was
updated then but not re-verified against a fresh live inventory the way the
2026-08-15 note below was. `kline-ingest-*` was folded into `trading-worker-*`
later the same day (2026-08-23), then split back out into its own
`kline-ingest-*` container on 2026-08-24 (nested under
`cmd/worker/trading-worker/kline-ingest/` in source, still an independent
process/container) — the persistent broker WebSocket -> Kafka ->
Redis/PostgreSQL pipeline runs there again, separate from trading-worker's
periodic `kline_sync`/`kline_sync_full` jobs.
Still resolve exact containers from current Docker labels before diagnostics;
names and Coolify resource IDs can change after a redeploy, and
`WORKER_COOLIFY_RESOURCE_ID` refers only to finance-mw's worker stack.
