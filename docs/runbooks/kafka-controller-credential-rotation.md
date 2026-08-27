# Kafka controller credential rotation

The production Kafka resource is the Coolify Docker Compose service
`kafka-cluster` (`j8c8ogo8k8g8s0ck4kg0k0k0`). It is a single combined
KRaft broker/controller, so its controller credential cannot be rotated with
rolling overlap. A guarded apply has a short Kafka outage while Coolify
recreates the service.

Run only `scripts/kafka-controller-rotation.sh` by hand over guarded SSH
(`ssh -A root@160.22.122.55`). This is infrastructure credential rotation for
shared infrastructure, not finance-mw/web/live-action/broker/mt5 application
code or its deploy, so it is delivered live-first — it does not run as a
`.github/workflows/*.yml` file, even for the CI audit trail. See
`.agents/skills/repository-delivery/SKILL.md`'s "Ownership and Delivery Lane"
for the exact policy (owner-confirmed 2026-08-24, cross-references commit
`451ce7c`). Do not edit the Coolify database, restart a container directly,
pass a credential in a command argument, or inspect a complete production
container environment.

## Running it over SSH

The script itself checks: `EXPECTED_AUTOMATION_COMMIT` is a well-formed
40-hex-character SHA *and* equals this checkout's own `git rev-parse HEAD`;
`EXPECTED_MW_COMMIT`/`EXPECTED_LIVE_ACTION_COMMIT` are well-formed SHAs (they
name commits in *other* repositories, so the script cannot cross-check them
against its own git state — read them correctly from the deployed
containers, step 2 below); `ROTATION_ID` matches `YYYYMMDDTHHMMSSZ`; and an
exact typed `ROTATION_CONFIRMATION` phrase for `apply`/`rollback`. The
`git rev-parse origin/main` match is an *operator* precondition (step 1
below), not an in-script check — fetch and confirm it by hand before every
run. Only the former `GITHUB_ACTIONS` execution-venue guard is gone from the
script; nothing else changed.

1. SSH to the production host and check out (or pull) the exact `finance-mw`
   commit you intend to run — the script requires its own checkout's
   `git rev-parse HEAD` to equal `EXPECTED_AUTOMATION_COMMIT`, and
   `origin/main` to also equal it, so fetch first:

   ```sh
   ssh -A root@160.22.122.55
   cd /path/to/finance-mw   # a checkout on the exact commit under review
   git fetch --quiet origin main
   commit="$(git rev-parse HEAD)"
   test "$commit" = "$(git rev-parse origin/main)"
   ```

2. Export the required inputs. `EXPECTED_MW_COMMIT` and
   `EXPECTED_LIVE_ACTION_COMMIT` are the exact deployed revisions of Finance
   MW's three apps (`mw`, worker fleet) and the four BTC/XAU Live Action
   workers — read them from the running containers' image tags
   (`docker inspect --format '{{.Config.Image}}' <container>`) or from
   `deployment-version-verification`. `COOLIFY_BASE_URL`/`COOLIFY_TOKEN` are
   the same Coolify API credentials the deleted workflow read from a GitHub
   Actions secret — they are **not** present in
   `docker/env/production.env` (that file holds only Finance MW's own
   application runtime values). Generate/read `COOLIFY_TOKEN` from the
   Coolify UI's API-token settings for the production instance, and use its
   API base URL for `COOLIFY_BASE_URL`; export both only in the interactive
   SSH shell, never hardcode them in a script or shell history file.

   ```sh
   export COOLIFY_BASE_URL="..."          # Coolify API base URL
   export COOLIFY_TOKEN="..."             # Coolify API token
   export EXPECTED_AUTOMATION_COMMIT="$commit"
   export EXPECTED_MW_COMMIT="..."        # exact deployed Finance MW commit
   export EXPECTED_LIVE_ACTION_COMMIT="..." # exact deployed Live Action commit
   export ROTATION_ID="$(date -u +%Y%m%dT%H%M%SZ)"
   export KAFKA_ROTATION_MODE=plan
   export ROTATION_CONFIRMATION=          # empty for plan
   export EXPECTED_SERVICE_COMPOSE_SHA256= # empty for plan
   ```

3. Run `plan` first (read-only):

   ```sh
   timeout --signal=TERM --kill-after=30s 85m \
     scripts/kafka-controller-rotation.sh
   ```

   Review its emitted `service_compose_sha256=...` and preflight evidence
   (host safety, application fleet, Kafka runtime, application progress,
   public health) before proceeding.

4. Re-run with `KAFKA_ROTATION_MODE=apply`,
   `ROTATION_CONFIRMATION=ROTATE-KAFKA-CONTROLLER`, and
   `EXPECTED_SERVICE_COMPOSE_SHA256` set to the exact digest the plan emitted,
   keeping the same `ROTATION_ID` and commit inputs:

   ```sh
   KAFKA_ROTATION_MODE=apply \
   ROTATION_CONFIRMATION=ROTATE-KAFKA-CONTROLLER \
   EXPECTED_SERVICE_COMPOSE_SHA256=<digest from the plan> \
     timeout --signal=TERM --kill-after=30s 85m \
     scripts/kafka-controller-rotation.sh
   ```

5. For a rollback, re-run with the same `ROTATION_ID`, current commit inputs,
   `KAFKA_ROTATION_MODE=rollback`,
   `ROTATION_CONFIRMATION=ROLLBACK-KAFKA-CONTROLLER`, and the current reviewed
   Compose SHA-256 — see "Explicit rollback" below.

## Preconditions

1. Finance MW `mw`, `kline-ingest`, `trading-worker`, `english-worker`,
   `social-worker`, and `tvl-worker` must each be healthy for at least ten
   minutes on the exact expected immutable image ID with zero restarts.
   `kline-ingest` owns the persistent broker WebSocket -> Kafka ->
   Redis/PostgreSQL streaming pipeline; `trading-worker` owns the periodic
   `kline_sync`/`kline_sync_full` HTTP jobs.
2. All four BTC/XAU Live Action workers must be healthy for at least ten
   minutes on the exact expected immutable commit and expose their Kafka,
   Redis, history, gRPC, and worker readiness gauges as `1`.
3. No BuildKit container may be active. The host must have at least 4 GiB
   available memory and 25 GiB available disk.
4. Kafka must have one healthy Coolify-owned broker/controller, a converged
   KRaft leader, the expected research read-only ACL, advancing real publisher
   traffic, zero lag for the five production consumer groups, and a healthy
   Kafka exporter.

Run `KAFKA_ROTATION_MODE=plan` first with these exact inputs (step 2/3 above):

- `EXPECTED_AUTOMATION_COMMIT`: current `origin/main` containing the script;
- `EXPECTED_MW_COMMIT`: exact Finance MW revision deployed to all three apps;
- `EXPECTED_LIVE_ACTION_COMMIT`: exact revision deployed to all four workers;
- `EXPECTED_SERVICE_COMPOSE_SHA256`: empty for plan; the plan derives and
  reports the exact current Coolify Compose source digest;
- `ROTATION_ID`: a unique UTC value such as `20260822T120000Z`;
- `ROTATION_CONFIRMATION`: empty.

The plan is read-only. Review its measured identities, topic count, quorum,
consumer lag, publisher progress, public health, and host capacity before an
apply.

## Apply and automatic recovery

Re-run the same source and identity inputs with `KAFKA_ROTATION_MODE=apply`,
`ROTATION_CONFIRMATION=ROTATE-KAFKA-CONTROLLER`, and the exact
`EXPECTED_SERVICE_COMPOSE_SHA256` emitted by the reviewed plan. A source drift
between plan and apply fails closed before mutation.

The script performs the following bounded sequence:

1. Repeat the complete preflight and capture the current Coolify service and
   only the two controller credential rows in a mode-600 backup.
2. Generate the replacement on the host running the script; it is never
   accepted as an input or printed.
3. Pre-copy the named Kafka volume while the broker remains live, repeat the
   dependency gate, stop the exact service through Coolify, and run a final
   delta copy. This yields a consistent restorable volume while minimizing the
   broker outage.
4. PATCH only `KAFKA_CONTROLLER_PASSWORD` through the Coolify service API and
   start the same durable owner.
5. Require a new healthy Kafka generation on the unchanged volume, successful
   authentication to the controller listener with the replacement, rejection
   of the retired credential, a converged quorum, broker client auth, expected
   ACLs, advancing production publish/consume traffic, zero required consumer
   lag, current exporter metrics, healthy dependent workers, and public health.

If any command fails after the service is stopped or the Coolify value is
changed, the exit trap restores the old value through the same API, starts the
same Coolify resource, and waits for the old credential to become healthy.
The script exits non-zero so the incomplete verification is visible in the
SSH session.

Backups remain under
`/data/backups/kafka-controller-rotation/<rotation_id>/` with directory mode
`0700` and file mode `0600`. They contain credential material and must
never be copied off the host, uploaded anywhere, or committed to Git.

## Explicit rollback

If a later regression requires rollback, re-run the script over SSH from the
exact current `origin/main` with the same `ROTATION_ID`, current deployed
MW/Live Action commits, `KAFKA_ROTATION_MODE=rollback`,
`ROTATION_CONFIRMATION=ROLLBACK-KAFKA-CONTROLLER`, and the current reviewed
Compose SHA-256. The rollback restores the prior Coolify value and recreates
Kafka on the preserved live volume, then repeats the functional gate.

The script intentionally does not overwrite the Kafka data volume during a
normal credential rollback. If the volume itself is proven corrupt, stop and
obtain owner approval for a separate destructive recovery: stop the exact
Coolify service, verify the volume name from the backup manifest, restore the
reviewed `volume/` snapshot, restore the old Coolify value, and start/verify
through Coolify. Never run a broad or wildcard volume restore.

## Independent production evidence

After a successful apply, independently record in `raw/handoff_agent.md`:

- the SSH session's exact automation commit and rotation ID;
- Coolify resource/deployment identity and rotation ID (never the values);
- Kafka container/image/volume identity, restart count, quorum and topic count;
- retired-controller rejection, controller acceptance, expected ACLs, and the
  five production consumer-group lag results;
- two advancing producer/consumer samples and all seven dependent app images;
- current `up{job="finance-kafka"}`, broker/exporter metrics, a real trace or an
  explicitly documented telemetry boundary, fresh Filebeat ingestion plus
  scoped Kafka/client error counts;
- public health, host CPU/memory/disk pressure, and the retained backup path.

Keep the handoff item in `Processing` on any gap. Move it to `Verify` only
after the entire production gate passes; only the independent researcher may
move it to `Done`.
