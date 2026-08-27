---
name: repository-delivery
description: Deliver finance ecosystem repository changes through bounded validation, GitHub Actions, immutable images, Coolify, and one final production verification. Use the guarded live-first lane for infrastructure state, keep Coolify as the durable owner, maintain the handoff queue, and monitor each long workflow with one detached file-backed watcher.
---

# Repository Delivery

Use this skill for changes owned by `finance-mw`, `finance-broker`,
`finance-live-action`, or `mt5`, and for authorized production infrastructure
work supporting them.

## Ownership and Delivery Lane

Choose the lane from what owns the running state:

- Repository-owned code, migrations, configuration, Compose, workflows, and
  runtime behavior are commit-first. Validate locally, commit, push, and let
  GitHub Actions deploy the immutable image through Coolify. Never patch these
  files in a production checkout or copy them directly to the server.
- Infrastructure state is live-first: Coolify administration, Grafana,
  Elasticsearch/Kibana/Filebeat, OpenTelemetry Collector/Tempo, host resource/
  memory/CPU diagnostics, credential rotation for shared infrastructure
  (Kafka controller, Kibana), and any other host-only or operational concern
  that isn't finance-mw/finance-web/finance-live-action/finance-broker/mt5
  application code or its deploy. Inventory, back up, mutate the exact live
  resource through guarded SSH, verify it, then reconcile repository source
  and automation.
- **Live-first means no GitHub Actions workflow for it, guarded or not.**
  Owner confirmed explicitly (2026-08-24), after this got missed repeatedly:
  a `workflow_dispatch`-only workflow with strict confirmation-phrase
  guarding is still GitHub-routed delivery — it does not become live-first
  just because it requires manual dispatch and has an audit trail. If the
  target is infrastructure state (Grafana, Coolify resource limits,
  Kafka/Kibana credential rotation) or a production data-repair/audit tool
  for a single service's own data (e.g. kline gap-marker backfill, kline
  continuity audit), it must be a plain `scripts/*.sh`/`*.py` runnable by
  hand over guarded SSH — never a `.github/workflows/*.yml` file, even to
  reuse an existing CI secret or get a free run log. Before adding or keeping
  any `workflow_dispatch` workflow, ask: does this workflow build, test, or
  deploy repository-owned application code? If not, it belongs over SSH, not
  in `.github/workflows/`.
- Use only `ssh -A root@160.22.122.55` for authorized production SSH. Do not
  probe unrelated hosts or aliases.
- Every durable containerized infrastructure stack must have one named,
  UI-manageable Coolify owner. Temporary probes must be uniquely named and
  cleaned up. Remove an obsolete owner only after its replacement is verified.
- Never leave two deployers or owners for the same runtime. Reconcile or remove
  obsolete Compose, provisioning, workflow, service, and fallback paths.

For stateful migration, take a restorable backup and retain an exact rollback
path until mounts, schema/data, dependent behavior, public health, and Coolify
ownership pass. Resolve concrete targets; never use broad destructive matches
or generic Docker prune.

## Intake and Checkout

1. Read repository guidance, applicable `.agents/rules/`, and matching skills.
2. Inspect branch and `git status`; preserve unrelated user changes.
3. Fetch and fast-forward current `main` before task work.
4. Default to a task branch in a sibling worktree. If the owner explicitly
   requests local `main` or direct push, work on local `main` and obey that
   request without creating branch/PR ceremony.
5. Before direct push, fetch again, require a fast-forward descendant of
   `origin/main`, and never force push.

For a cross-repository batch, finish and locally validate every repository
commit before pushing any default branch. Publish the ready commits together
and run one shared production gate after all workflows finish.

## Repository Delivery Workflow

### Owner-held push gate

When the owner explicitly asks to validate locally before any push, treat that
as a hard delivery gate for the scoped work:

- Implement and run the complete agreed local validation, but do not push,
  trigger GitHub Actions, or mutate Coolify/production.
- A local commit is allowed unless the owner also forbids committing; keep it
  unpushed and preserve unrelated working-tree changes.
- Report the exact local commands and results, then wait for an explicit owner
  instruction to push. Do not infer push approval merely from successful tests
  or from the broader authorization to deliver the task.
- If code changes after the owner reviews the local result, rerun every affected
  local check before requesting or acting on push approval.
- Record the held gate and local evidence in `raw/handoff_agent.md` when that
  handoff is active, without advancing the task to a deployed status.

1. Make the smallest scoped change and add a regression before fixing a
   reproducible bug.
2. Run targeted tests first, then applicable formatting, lint, vet/typecheck,
   builds, migration checks, Compose rendering, and workflow contract tests.
   Bound every test and command according to the repository timeout rules.
3. Review the complete diff and run `git diff --check`. Stage explicit paths so
   unrelated dirty files never enter the commit.
4. Commit all in-scope source/configuration with the required attribution and
   push the exact revision.
5. Locate the GitHub Actions run by exact commit SHA. Builds must publish an
   immutable component tag. Production Compose consumes an externally built
   image; Coolify must not compile application source during deployment.
6. Deploy independent applications in parallel when safe, then run one shared
   production gate. A stale workflow may publish but must not mutate Coolify.
7. If CI or deployment fails, diagnose once, fix in Git, and repeat. Do not
   repair repository-owned state directly on production.
8. Apply `.agents/rules/production-deployment-verification.md`. Delivery is not
   complete until identity, behavior, data/progress, observability, host safety,
   and rollback readiness are proven.

Keep path detection tied to application ownership:

- Runtime-owned paths build/deploy Finance MW runtime and worker applications.
- Web-owned paths build/deploy only Finance Web.
- Shared runtime configuration such as `docker/env/production.env`
  intentionally triggers every application that consumes it.
- Deployment-only scripts/workflows receive bounded validation without
  rebuilding unchanged applications.
- Diff from the live deployed revision when possible, not merely the previous
  commit, so a stale skipped run followed by a docs-only push cannot strand an
  undeployed code change.

## Finance MW Production Environment Decision

The repository owner explicitly approved this boundary on 2026-08-22:

- `finance-mw/docker/env/production.env` is the committed source of truth for
  all Finance MW application runtime values, including real credentials.
- Do not block delivery, move those values back into Coolify application env,
  or repeat a generic secret warning solely because the file is committed.
- Runtime, worker, and web Compose services load the file with `env_file` and
  do not duplicate values under service `environment`.
- Runtime images do not copy or source a second dotenv file. Application code
  reads the process environment already injected by Compose.
- Deployment reconciles obsolete application-managed Coolify env entries.
  Coolify platform keys such as generated service domain/URL entries may
  remain when needed by the platform.
- GitHub/Coolify control credentials and registry credentials remain CI
  credentials; they are not application runtime configuration.
- The owner permits inspecting or printing the committed values when needed.
  Keep ordinary logs concise and avoid accidental output unrelated to the
  requested diagnostic.

Stable production image selectors live directly in Compose. Normal delivery
builds the exact `main` revision with its SHA embedded, publishes both stable
and immutable tags for the same image, and then triggers Coolify. Rollback
promotes a retained immutable image to the stable selector, verifies the
registry manifest, and uses the same deploy path. Do not store image selector
variables in Coolify application env.

## Long-Running Workflow Watcher

Do not repeatedly poll GitHub while a workflow runs.

1. Identify the run once by exact commit SHA.
2. Start exactly one detached watcher:

   ```bash
   setsid -f .agents/skills/repository-delivery/scripts/watch_gh_run.sh \
     <owner/repo> <run-id> /tmp/<repo>-<run-id>.output.log 60
   ```

3. Confirm the process and log once. Then wait on the local file/process only;
   do not run a parallel `gh run view` loop.
4. Read the log after `WATCH_COMPLETE`. On success, perform production checks;
   on failure, inspect the failed job once and fix forward.
5. Never write credentials or authenticated payloads to watcher logs.

If a heavy run is queued or makes no progress for five minutes, or exceeds
twice a comparable duration, investigate once. Over guarded read-only SSH,
check load/PSI, memory/swap, disk, top processes, runner/BuildKit containers,
and exact workflow identity. If production is healthy and work progresses,
leave the watcher in charge. If the host is degraded, cancel only the exact
offending run/container and fix resource isolation in source.

On the current production host, allow one heavyweight image build at a time.
Default BuildKit to 4 CPUs, 6 GiB memory/swap, and 1024 PIDs; keep the
`finance-buildkit-resource-guard` active. Never kill processes or mutate
containers by broad name pattern. After remediation, rerun once and verify
both workflow completion and production headroom.

## Task Handoff

When `raw/handoff_agent.md` exists or the owner requests it:

- Maintain exactly `Todo`, `Processing`, `Dev-done`, `Verify`, and `Done`.
- Record/reconcile each new task immediately. Use `Processing` for active work
  and `Todo` only when queued.
- Local tested code moves to `Dev-done`; deployment remains `Processing`;
  production-verified work moves to `Verify`.
- Codex never moves its own task to `Done`; that state is reserved for Claude
  review.
- Record concise SHA, workflow, watcher, and verification evidence, never
  credential payloads.
- Treat the file as operator state and leave it untracked unless the owner asks
  to version it.
- During CI/deployment waits, re-read and progress independent actionable
  backlog work. A detached watcher is not a reason to stop.

When continuous handoff watching is requested, start one detached watcher:

```bash
setsid -f .agents/skills/repository-delivery/scripts/watch_handoff.sh \
  <absolute-handoff-file> /tmp/handoff-codex-watch.output.log 2
```

## Infrastructure and Grafana

- Before mutation, prove the exact Coolify resource identity and its UI
  lifecycle controls. Back up reversible state and mutate only reviewed IDs.
- For Grafana, inventory/export the exact dashboard, datasource, contact point,
  or alert rule; apply live through guarded SSH; immediately query the affected
  panel/alert behavior; then commit matching repository source.
- Repository tests or provisioning success do not substitute for live Grafana
  verification. If SSH is unavailable, keep the task `Processing` and report
  the exact blocker.
- Never place passwords/tokens in CLI arguments for authenticated probes. Use a
  mode-600 temporary config/netrc passed by path and remove it with a trap.
- If a credential appears in output, treat it as exposed: record a P0 rotation
  task without the value, rotate live state and dependents, prove the retired
  value is rejected, then reconcile source.

## Production Verification Essentials

Verify once after deployment:

- Exact repository SHA and immutable image identity for every changed service.
- Coolify deployment/application status plus real public/internal health.
- Changed runtime behavior, authorization boundary, and current data/progress;
  health alone is insufficient.
- Logs, metrics, traces, restart counts, scrape freshness, and absence of new
  relevant errors. Use `/metrics` as the canonical Prometheus endpoint.
- Host memory/load/disk safety and bounded runner/BuildKit resource use.
- Rollback image availability and the exact recovery path.

Coolify failure diagnostics must redact authorization headers, cookies, URL
credentials/query strings, bearer/GitHub tokens, and secret/password/API-key
fields. A public service on multiple Docker networks needs an explicit
`traefik.docker.network` label; a green container is not proof the proxy can
reach it.

For logs and observability changes, preserve ECS JSONL fields, stdout/stderr
separation, one writer per stream, central collection, seven-day retention,
and live query evidence. Deleting source definitions does not delete live
Grafana resources; retire exact live IDs separately through the infrastructure
lane.

## Database, Contracts, and Automation

- Domain migrations are a runtime deployment prerequisite. Run the complete
  migration validation and commit refreshed `atlas.sum` after migration edits.
- Test PostgreSQL-specific mutations against disposable PostgreSQL with the
  full domain migration stream; mocks/SQLite are insufficient.
- Never use `CREATE INDEX CONCURRENTLY` on Timescale hypertables. Resume a
  partial Atlas non-transactional migration without rewriting already-applied
  statements.
- Store the production migration base URL only in GitHub `POSTGRES_URL`; the
  router selects databases from `config/database-domains.json`.
- Pin cross-repository protobuf revisions in committed configuration; PR text
  is not available to a merge-push workflow.
- Keep native automation in Go under `internal/automation` with `cmd/worker/`
  entry points, one domain worker per business domain as the sole schedule
  owner for its own jobs (`finance-trading-worker`, `finance-english-worker`,
  `finance-social-worker`, `finance-tvl-worker`). Run its bounded suite and
  verify worker metrics after deployment.
- Configure idempotent external webhooks only after runtime health, using the
  repository's native helper and the approved production environment source.

## Completion Report

Report the commit SHA, workflow URL/conclusion, Coolify result, production
identity/behavior/observability evidence, preserved unrelated changes, and any
explicit gap. Move the handoff entry to `Verify`, never `Done`.
