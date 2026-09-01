# Kline continuity audit and gap-marker backfill

`cmd/ops/kline-continuity-audit` (read-only evidence) and
`cmd/ops/kline-gap-marker-backfill` (guarded metadata mutation) are
production data-audit/repair tools for Finance MW's own Kline data, not
shared infrastructure and not application code being deployed. Run both by
hand over guarded SSH (`ssh -A root@160.22.122.55`) — they do not run as
`.github/workflows/*.yml` files. See
`.agents/skills/repository-delivery/SKILL.md`'s "Ownership and Delivery
Lane" for the exact policy (owner-confirmed 2026-08-24, cross-references
commit `451ce7c`) and `.agents/skills/kline-data-quality/SKILL.md` for the
data-quality method these tools serve.

Neither tool has ever had a `GITHUB_ACTIONS` guard — both already parse
their flags and validate their own inputs standalone, so moving them off
GitHub Actions required no code change beyond relocating the package from
`cmd/ci/` to `cmd/ops/` (this repository's convention: `cmd/ci/` is for
tools a GitHub Actions workflow builds and runs; `cmd/ops/` is for
SSH/host-run tools with no CI trigger).

## What moved off CI, and what did not

The deleted `Kline Continuity Evidence` and `Kline Gap Marker Backfill`
workflows did two different kinds of work:

- **Mutation safety** — matching `EXPECTED_SOURCE_COMMIT`/
  `--source-commit`, requiring an exact reviewed `--expected-plan-sha256`
  and `--expected-updates` before `--apply`, and the rollback path. This
  logic lives entirely inside `cmd/ops/kline-gap-marker-backfill`'s own flag
  validation (`command.go`'s `parseOptions`/`run`) and is unchanged by the
  move. It is covered by that package's Go test suite
  (`main_test.go`, `database_integration_test.go`), which moved with it.
- **CI-only orchestration** — the self-hosted-runner preflight (worker
  fleet health, BuildKit load, host capacity, database growth sampling),
  building a maintenance Docker image, uploading/downloading `dry-run`
  artifacts between separate workflow runs, and posting a run summary. None
  of that is safety-critical mutation logic; it only made sense inside a
  GitHub Actions run. It is **not** reimplemented as a script. The operator
  running this runbook performs the equivalent checks by hand, using the
  already-existing standalone scripts referenced below, and keeps the
  before/plan/after evidence files on the host (or references their approved
  durable location from `.ops/changes/<change>/handoff.md`) instead of a workflow artifact.

## Building the binaries

Build directly on the production host from the exact commit under review —
the same `go build` pattern used for other host-run Go tools in this
ecosystem, without a container image if you don't need the extra isolation
below.

```sh
ssh -A root@160.22.122.55
cd /path/to/finance-mw   # a checkout on the exact commit under review
git fetch --quiet origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
source_commit="$(git rev-parse HEAD)"
CGO_ENABLED=0 /usr/local/go/bin/go build -trimpath \
  -o /usr/local/bin/kline-continuity-audit ./cmd/ops/kline-continuity-audit
CGO_ENABLED=0 /usr/local/go/bin/go build -trimpath \
  -o /usr/local/bin/kline-gap-marker-backfill ./cmd/ops/kline-gap-marker-backfill
```

If the host's Go toolchain is not at `/usr/local/go/bin/go`, use whatever
`go` the host has, matching `go.mod`'s Go version (currently 1.24.x, see
`GO_VERSION` in `.github/workflows/pipeline-ci-quality.yml`).

### Optional: run inside the isolated maintenance image

For the same read-only, resource-limited, no-bind-mount isolation the
deleted workflow used, build and run the existing
`docker/infrastructure/kline-maintenance/Dockerfile` image instead of
running the binaries directly on the host:

```sh
mkdir -p artifacts
cp /usr/local/bin/kline-continuity-audit /usr/local/bin/kline-gap-marker-backfill artifacts/
docker build --pull=false --no-cache \
  --file docker/infrastructure/kline-maintenance/Dockerfile \
  --tag "finance-mw-kline-maintenance:${source_commit}" artifacts
docker create --name kline-maintenance --read-only \
  --tmpfs /tmp:rw,nosuid,nodev,noexec,size=128m,mode=1777 \
  --network finance --cpus 2 --memory 1g --pids-limit 256 \
  --env DATABASE_URL="${POSTGRES_URL%/}/postgres?sslmode=disable" \
  "finance-mw-kline-maintenance:${source_commit}"
docker start kline-maintenance
# then: docker exec kline-maintenance /kline-continuity-audit ...
docker rm -f kline-maintenance
docker image rm "finance-mw-kline-maintenance:${source_commit}"
```

The remainder of this runbook shows the direct-binary invocation; substitute
`docker exec kline-maintenance /kline-continuity-audit ...` /
`docker exec kline-maintenance /kline-gap-marker-backfill ...` if using the
container.

## Preflight checklist (operator-performed)

Before any `--apply`, confirm by hand what the deleted CI workflow used to
gate automatically:

- Finance MW `mw`, `kline-ingest`, `trading-worker`, `english-worker`,
  `social-worker`, `tvl-worker` each healthy, non-restarting, at least ten
  minutes old, on the expected immutable image (`docker inspect --format
  '{{.Config.Image}}' <container>`).
- All Live Action workers healthy and ready — run
  `scripts/verify-live-action-maintenance-readiness.sh <route>` per route
  against each worker's `/metrics`, or `scripts/verify-worker-stack.sh` for
  the aggregate Finance MW worker fleet.
- No concurrent BuildKit load — `scripts/buildkit-resource-guard.sh verify`.
- Host capacity — `df -Pk .`, `/proc/meminfo` `MemAvailable`, and
  `/proc/pressure/cpu` `avg10` comfortably below saturation.
- Database headroom — no long-running queries, connection count comfortably
  below `max_connections`, via `psql`'s `pg_stat_activity`.
- The deployed runtime SHA matches expectations —
  `scripts/detect-deployed-runtime-sha.sh`.

`POSTGRES_URL` (the deleted workflow's `${{ secrets.POSTGRES_URL }}`) is
**not** present in `docker/env/production.env` — that file holds only
Finance MW's own application runtime values, not the Timescale/Postgres
Coolify service's own credentials. Compose it from that service's
`POSTGRES_USER`/`POSTGRES_PASSWORD` (Coolify-managed; see
`docker/infrastructure/psql/timescaledb.yaml`) and its reachable
host:port on the `finance` Docker network, e.g.
`postgres://postgres:<POSTGRES_PASSWORD>@<timescale-host>:5432`.

## Running `kline-continuity-audit` (read-only)

```sh
export DATABASE_URL="${POSTGRES_URL%/}/postgres?sslmode=disable"
/usr/local/bin/kline-continuity-audit \
  --database-url "$DATABASE_URL" \
  --mt5-address <mt5-container-or-host>:50052 \
  --expected-source-commit "$source_commit" \
  --ingestion-grace 5m \
  --lookback-years 5 \
  --verify-broker=true \
  --output kline-continuity-before.json
```

Review the emitted `summary.all_routes_complete`, `summary.expected_routes
== 48`, `summary.incomplete_routes == 0`, `summary.total_missing_candles ==
0`, `summary.broker_unverified_missing_candles == 0`, and
`summary.invalid_gap_markers == 0` before any repair. `--verify-broker=false`
skips the (slower) live broker cross-check when only the raw database
grid-gap inventory is needed.

## Running `kline-gap-marker-backfill` (guarded mutation)

Historical session-gap markers are a separate, guarded metadata repair — see
`.agents/skills/kline-data-quality/SKILL.md`. Run a dry-run first for one
exact `BROKER.MARKET_TYPE.BASE.QUOTE` route and interval:

```sh
/usr/local/bin/kline-gap-marker-backfill \
  --database-url "$DATABASE_URL" \
  --evidence kline-continuity-before.json \
  --source-commit "$source_commit" \
  --instrument binance.perpetual_future.BTC.USDT \
  --interval 5m \
  --backup-output kline-gap-marker-backup.json \
  --output kline-gap-marker-plan.json
```

This writes `kline-gap-marker-plan.json` (mode `dry-run`, with `plan_sha256`
and `expected_updates` fields) and `kline-gap-marker-backup.json` (the
empty-state backup needed to `--rollback`). Keep both files — retained on
the host or in an approved durable evidence location referenced by
`.ops/changes/<change>/handoff.md`, since there is no workflow artifact upload
to retain them automatically.

Re-run the audit (`kline-continuity-audit` above, output to
`kline-continuity-after.json` isn't needed pre-apply, but re-running the
audit against the same route confirms the dry-run evidence is still current)
and have the plan reviewed before applying. Apply with the exact reviewed
digest, count, and the dry-run's own evidence/backup as the "reviewed"
inputs:

```sh
/usr/local/bin/kline-gap-marker-backfill \
  --database-url "$DATABASE_URL" \
  --evidence kline-continuity-current.json \
  --source-commit "$source_commit" \
  --instrument binance.perpetual_future.BTC.USDT \
  --interval 5m \
  --apply \
  --expected-plan-sha256 <plan_sha256 from the dry-run> \
  --expected-updates <expected_updates from the dry-run> \
  --reviewed-evidence kline-continuity-before.json \
  --reviewed-backup kline-gap-marker-backup.json \
  --backup-output kline-gap-marker-apply-backup.json \
  --rollback-output kline-gap-marker-rollback.json \
  --output kline-gap-marker-apply-result.json
```

`--evidence` here must be a **fresh** audit run immediately before apply
(`kline-continuity-current.json`); `--reviewed-evidence`/`--reviewed-backup`
are the retained dry-run artifacts. The command itself enforces that the
fresh evidence and the reviewed evidence agree on route identity and broker
evidence before mutating, rejects a shortened/moved/new segment, and
verifies the applied result post-commit — rolling itself back automatically
and writing `--rollback-output` if post-commit verification fails.

After a successful apply, run `kline-continuity-audit` again
(`kline-continuity-after.json`) and confirm the same all-routes-complete
summary as before. Retain `kline-continuity-before.json`,
`kline-gap-marker-backup.json`, `kline-gap-marker-plan.json`,
`kline-continuity-after.json`, and (if produced)
`kline-gap-marker-rollback.json`/`kline-continuity-rollback.json` as the
rollback/audit evidence referenced from `.ops/changes/<change>/handoff.md`.

### Explicit rollback

```sh
/usr/local/bin/kline-gap-marker-backfill \
  --rollback \
  --source-commit "$source_commit" \
  --instrument binance.perpetual_future.BTC.USDT \
  --interval 5m \
  --expected-plan-sha256 <plan_sha256 from the applied plan> \
  --expected-updates <expected_updates from the applied plan> \
  --rollback-backup kline-gap-marker-apply-backup.json \
  --output kline-gap-marker-rollback-result.json
```

`--rollback-backup` must be the exact backup file the apply step wrote
(`--backup-output` from the apply invocation), and the source-commit, route,
plan digest, and count guards must match exactly or the command refuses.
