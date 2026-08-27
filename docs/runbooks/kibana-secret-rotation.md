# Kibana service credential and encryption-key rotation

Production Kibana belongs to the Coolify Compose service
`finance-observability` (`vc0gwk040csg4cwg88000k48`). Run only
`scripts/kibana-secret-rotation.sh` by hand over guarded SSH
(`ssh -A root@160.22.122.55`). This is infrastructure credential rotation for
shared infrastructure, not finance-mw/finance-web/live-action/broker/mt5 application
code or its deploy, so it is delivered live-first — it does not run as a
`.github/workflows/*.yml` file, even for the CI audit trail. See
`.agents/skills/repository-delivery/SKILL.md`'s "Ownership and Delivery Lane"
for the exact policy (owner-confirmed 2026-08-24, cross-references commit
`451ce7c`). Never pass a secret through a command argument, exported
environment dump, process listing, or diagnostic output.

This service stores `docker_compose_raw` in the Coolify database; a Git commit
does not synchronize that live source. The guarded `source-plan` and
`install-source` phases must reconcile the exact repository Compose before the
credential plan. Do not run a generic deploy against stale raw Compose.

## Running it over SSH

The script enforces the exact same safety invariants whether it runs in CI or
by hand: `git rev-parse HEAD` (in the checkout the script runs from) must
equal `EXPECTED_AUTOMATION_COMMIT`, `ROTATION_ID` must be
`YYYYMMDDTHHMMSSZ`, and each mutating mode requires its own exact typed
`ROTATION_CONFIRMATION` phrase plus the reviewed digest(s) from the prior
phase. Only the former `GITHUB_ACTIONS` execution-venue guard is gone;
nothing else changed.

`COOLIFY_BASE_URL`/`COOLIFY_TOKEN` are the same Coolify API credentials the
deleted workflow read from a GitHub Actions secret — they are **not**
present in `docker/env/production.env` (that file holds only Finance MW's
own application runtime values). Generate/read `COOLIFY_TOKEN` from the
Coolify UI's API-token settings for the production instance.

```sh
ssh -A root@160.22.122.55
cd /path/to/finance-mw   # a checkout on the exact commit under review
export COOLIFY_TOKEN="..."     # from the Coolify UI's API-token settings
export COOLIFY_BASE_URL="..."  # the Coolify instance's API base URL
export EXPECTED_AUTOMATION_COMMIT="$(git rev-parse HEAD)"
export ROTATION_ID="$(date -u +%Y%m%dT%H%M%SZ)"
export KIBANA_ROTATION_MODE=source-plan
export ROTATION_CONFIRMATION=
timeout --signal=TERM --kill-after=30s 55m scripts/kibana-secret-rotation.sh
```

Then step through `install-source` (needs `EXPECTED_CURRENT_SOURCE_SHA256`
from the `source-plan` output and
`ROTATION_CONFIRMATION=INSTALL-KIBANA-SECURE-SOURCE`), `plan`, `apply` (needs
`EXPECTED_PLAN_SHA256`, `ELASTIC_SNAPSHOT_REPOSITORY`, `ELASTIC_SNAPSHOT_NAME`,
and `ROTATION_CONFIRMATION=ROTATE-KIBANA-SERVICE-AND-SAVED-OBJECTS`),
`finalize` (needs `EXPECTED_PLAN_SHA256`, `EXPECTED_RESULT_SHA256`, and
`ROTATION_CONFIRMATION=REMOVE-KIBANA-DECRYPTION-ONLY-KEY`), each re-running
the same script with the same `ROTATION_ID` and `EXPECTED_AUTOMATION_COMMIT`
over the same SSH session, exactly as described in "Guarded phases" below.

The repository entrypoint transfers the four sensitive scalar settings into
a mode-`0600` ephemeral Kibana keystore over stdin, writes an optional old
saved-object key only to a mode-`0600` configuration file, unsets the source
variables, then starts Kibana. A diagnostic may inspect the exact Kibana
container only by matching known secret values against a private temporary
file and emitting a boolean result. Broad `ps ... args`, `docker top` output,
`docker inspect .Config.Env`, `env`, and `printenv` output are forbidden.

## Documented boundaries

Kibana 9.1.2 uses
`POST /api/encrypted_saved_objects/_rotate_key?batch_size=10000`. Its current
API accepts only `batch_size` and optional `type`; the legacy
`conflicts=abort` parameter is not part of this endpoint. The script obtains
equivalent fail-closed behavior by aborting on any nonzero `failed` value and
requiring a second pass with `failed=0` and `successful=0` before permitting
removal of the decryption-only key. It also refuses automatic finalization
when the encrypted object total exceeds the 10,000-object safely verifiable
window.

The API has no `unprotected_objects` field and silently skips objects that no
configured key can decrypt. Do not claim such a field was verified. The
retained Elasticsearch snapshot and the zero-success second pass are the
reviewable recovery/removal gates.

Only the encrypted-saved-objects key has a supported decryption-only list and
bulk re-encryption API. This script therefore refuses to patch
`SERVICE_PASSWORD_XPACKSECURITY` or `SERVICE_PASSWORD_XPACKREPORTING`:

- rotating `xpack.security.encryptionKey` invalidates active sessions;
- rotating `xpack.reporting.encryptionKey` can make pending report metadata
  undecryptable.

Their exposed values remain a P0 prerequisite, not a silently skipped success.
Rotate them only in a separately owner-approved maintenance window after
proving the reporting queue is empty, accepting global session invalidation,
taking a fresh snapshot, and reviewing an authentication/reporting smoke test
plus rollback. There is no lossless key-overlap API for these two settings.

## Guarded phases

Use one unique `ROTATION_ID` for every phase and run the script only from the
exact current `origin/main` SHA.

1. `source-plan` is read-only. It verifies current service health without
   printing the known-exposed argv and emits both the exact current-source and
   canonical-source SHA-256 values. It does not patch, deploy, or write a
   production-host backup.
2. `install-source` requires the reviewed current-source digest and confirmation
   `INSTALL-KIBANA-SECURE-SOURCE`. It refuses if either live raw Compose or the
   reviewed live source differs, writes that exact source to
   `coolify-compose-before.yaml` mode `0600`, reads it back and verifies the
   digest, then patches only the exact canonical repository source
   through the Coolify API, proves exact byte parity, deploys the same resource,
   then verifies health, ingestion, and clean targeted Kibana argv. Any failure
   restores the mode-`0600` source backup, redeploys, and re-verifies health.
3. `plan` is read-only to the service and first requires exact canonical/live
   source parity. It verifies the exact Coolify resource,
   Kibana 9.1.2 identity, Elasticsearch/Kibana/Filebeat health, fresh
   `app-logs`, zero restarts/OOM, and clean Kibana argv. It emits only a
   redacted plan SHA-256 and does not patch, deploy, or write a production-host
   backup.
4. `apply` requires that digest, rechecks exact canonical/live source parity,
   reconstructs the plan from current live state and refuses any digest drift,
   then writes the exact Coolify environment and reviewed redacted plan under
   `/data/backups/kibana-secret-rotation/<rotation_id>/` with directory mode
   `0700` and file mode `0600` before the snapshot or secret changes. It also
   requires an already configured Elasticsearch snapshot repository, a unique
   snapshot name, and confirmation
   `ROTATE-KIBANA-SERVICE-AND-SAVED-OBJECTS`. It snapshots every `.kibana*`
   index, rotates `kibana_system`, installs a new saved-object primary with the
   old key decryption-only, redeploys through Coolify, proves the old service
   credential returns `401`, runs two strict key-rotation passes, and retains
   the old key. Review the emitted result SHA-256.
5. `finalize` requires both reviewed digests and confirmation
   `REMOVE-KIBANA-DECRYPTION-ONLY-KEY`. It removes the old key only when the
   stored second pass proves `failed=0`, `successful=0`, and `total<=10000`,
   then redeploys and repeats the full health/ingestion/argv/auth gate.
6. `rollback` requires the plan digest and confirmation
   `ROLLBACK-KIBANA-SERVICE-AND-SAVED-OBJECTS`. It restores the previous service
   credential and saved-object primary while retaining the generated key as
   decryption-only, so objects already re-encrypted during apply remain
   readable. A later reviewed reverse rotation can remove that secondary key.

The apply/finalize exit trap performs the same configuration rollback after
any post-mutation failure. Snapshot data and credential backups are never
copied off the host, uploaded anywhere, or committed to Git.

## Independent verification

After finalization, record the automation SHA, the SSH session's output for
every phase,
Coolify deployment IDs, exact Kibana image ID, snapshot repository/name/UUID,
rotation-result digest and counts, old credential rejection, current Kibana
and Elasticsearch status, Filebeat output test plus fresh document count,
clean targeted argv result, container restart/OOM state, host safety, and the
retained rollback path in `raw/handoff_agent.md`. Never record secret values.
Keep the task in `Processing` for the security/reporting-key prerequisite or
any other gap; Codex moves a fully verified task only to `Verify`, never
`Done`.
