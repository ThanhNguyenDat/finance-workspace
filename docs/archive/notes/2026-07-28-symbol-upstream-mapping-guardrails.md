# 2026-07-28 Symbol Upstream Guardrails

## Outcome

Finance MW now routes the complete 18-symbol production universe without silently
borrowing data from the default worker:

- the production map includes `LINKUSDT`, `ORDIUSDT`, and `WLDUSDT`;
- an explicit symbol map is fail-closed, while an empty map retains the
  single-worker development fallback;
- a configured-map coverage mismatch emits a startup warning;
- an unmapped HTTP request returns a visible `503 Service Unavailable` backed by
  gRPC `FailedPrecondition`;
- the web composition registry exposes all 18 symbols;
- production verification requires 18 established connections to 18 unique
  `:50051` peers and distinct candle samples for the three newly wired symbols.

`HISTORICAL_REPLAY_CONTRACT_VERSION` was not changed because this delivery changes
routing and observability, not trading semantics.

## Implementation

Primary implementation commit:

- `0f9c4e4` — `feat(trading): fail closed on missing symbol upstreams`

Production verifier hardening commits:

- `ece6a69` — select the Finance MW compose service rather than every container
  that shares the immutable runtime image;
- `814601f` — reacquire the runtime container while Coolify replaces it;
- `0233da5` — inspect sockets through Docker because the self-hosted runner is
  itself containerized;
- `89b07b0` — copy the probe through the Docker API instead of bind-mounting a
  runner-container path into the host daemon;
- `7d29379` — keep the unary data sample scoped to the three newly connected
  symbols while the socket check covers the full 18-worker universe.

The production upstream verifier is intentionally split into two checks:

1. `/proc/net/tcp*` in the deployed Finance MW container must show exactly 18
   established connections to 18 unique remote `:50051` peers.
2. The immutable probe binary copied into that container must read one latest
   five-minute candle from `LINKUSDT`, `ORDIUSDT`, and `WLDUSDT`, and the three
   candle signatures must differ.

This measures the prompt's full connection-count contract without turning the
three-symbol acceptance test into an unrelated health audit of every legacy
worker.

## Validation

Local feature validation completed successfully:

```text
go test ./...
go vet ./...
go test -race ./internal/interfaces/http/... ./internal/interfaces/grpc/...
cd web && npm test -- --run
cd web && npm run build
bash scripts/tests/test_coolify-workflows.sh
bash scripts/tests/test_coolify-deploy.sh
```

The web suite passed all 163 tests. The final verifier adjustment additionally
passed:

```text
go test ./cmd/trading-upstream-probe
go test ./internal/interfaces/grpc/... ./internal/interfaces/http/...
go vet ./cmd/trading-upstream-probe ./internal/interfaces/grpc/... ./internal/interfaces/http/...
```

GitHub Actions run
[`30397265792`](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30397265792)
completed successfully for exact source SHA
`7d29379b7626adf5b8d61f6d8faf6f78b93bb1be`. Its green path included contract
parity, formatting, Go test/vet/build, runtime-image build and publish,
migrations, Compose and deployment-script validation, web tests/build, worker
deployment, runtime deployment, upstream verification, and rollback-image
retention.

## Production evidence

Coolify deployment `x284rv92u2nisbwmjrbrgod8` finished for immutable image:

```text
johnkelvin3107/finance-eco-system:finance-mw_sha-7d29379b7626adf5b8d61f6d8faf6f78b93bb1be
```

The deployed runtime then reported:

```text
Trading runtime has 18 established connections to 18 unique :50051 peers
upstream verified symbol=LINKUSDT address=live-action-linkusdt:50051 latest_ts=1785271200 close=8.381
upstream verified symbol=ORDIUSDT address=live-action-ordiusdt:50051 latest_ts=1785271200 close=3.345
upstream verified symbol=WLDUSDT address=live-action-wldusdt:50051 latest_ts=1785271200 close=0.3197
verified 18 configured trading upstreams; sampled distinct candle data for LINKUSDT,ORDIUSDT,WLDUSDT
```

The three samples share the same candle timestamp but have different prices and
full candle signatures, proving that the dashboard data no longer falls back to
one mislabeled default worker.

## Remaining gate

Engineering delivery is complete and production evidence is green. The prompt
remains subject only to the repository's explicit human verification step before
`done` may become `verified`.
