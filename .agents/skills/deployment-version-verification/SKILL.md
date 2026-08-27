---
name: deployment-version-verification
description: Aggregate immutable finance-service build identities through Finance MW and verify exact deployment revisions without treating delivery as functional success.
---

# Deployment Version Verification

Use this skill for service version RPCs, build metadata, the public Finance MW
version endpoint, cross-repository contract pins, or GitHub Actions deployment
identity checks.

## Architecture

- `finance-mw` is the only public HTTP surface.
- `finance-live-action`, `finance-broker`, and MT5 expose private unary gRPC
  version methods. The browser and GitHub Actions never call those services
  directly.
- The public endpoint is `GET /api/v1/system/version`.
- Without query parameters it returns the full deployment inventory.
- With both `repository` and `commit_sha` it verifies every configured instance
  of that repository. Partial expectations are invalid.

## Identity fields

Every service returns:

- stable service name;
- repository owner/name;
- application or package version;
- full 40-character source commit SHA;
- UTC build timestamp when the service build pipeline supplies one.

The full source SHA is mandatory. Build time is supplementary and may be omitted
when an existing immutable image pipeline does not expose it. Do not infer
deployment identity
from mutable tags, branch names, a server checkout, Coolify labels, or the GitHub
API at request time.

## Status semantics

- `200`: inventory read succeeded, or every relevant instance matches the
  expected repository and commit.
- `400`: only one expectation query parameter was supplied or the SHA is invalid.
- `404`: no configured service belongs to the requested repository.
- `409`: all requested instances answered but at least one commit differs.
- `503`: at least one requested instance is unavailable or reports unknown or
  malformed production metadata.

A successful version response proves deployment identity only. The JSON must
state `functional_status: not_evaluated`. Strategy behavior, data freshness,
broker login, order execution, reconciliation, PnL, ROI, and the official web
workflow retain separate production checks and statuses.

## Fan-out and safety

- Probe upstreams concurrently with a strict per-RPC timeout.
- Verify every explicitly routed live-action worker; never sample a single
  symbol.
- Do not expose private hostnames, credentials, raw transport errors, or stack
  traces. Return a normalized status and gRPC code only.
- The endpoint is public but read-only, low-cardinality, globally rate-limited,
  access-logged, and covered by existing HTTP metrics.

## Required checks

```bash
make proto-gen
gofmt -w ./pkg/buildinfo ./internal/services ./internal/interfaces
go test -timeout=10m ./...
go vet ./...
go build ./cmd/server
docker compose -f docker/compose.mw.yaml config --quiet
bash scripts/tests/test_verify_service_version.sh
```

Cross-repository protobuf copies must be pinned and verified against the merged
source revisions before the middleware PR is merged.
