# 2026-07-28 Strategy-Owned Protective Levels

## Scope

This is the `finance-mw` delivery note for
`finance-live-action/prompts/2026-07-28-03-implement-strategy-owned-exits.md`.

## Contract and UI

- `ExecutionContext.strategy_owned_protective_levels` uses protobuf field `18`.
- The HTTP gateway preserves the field in its JSON execution context.
- The web client normalizes a missing or non-boolean value to `false`.
- A selected Alpha scope with the field set to `true` displays a warning that
  its performance is not directly comparable with raw Alpha scopes.
- Raw Alpha, Portfolio, Live, Runtime, Backtest, and legacy scopes do not display
  the warning.

## Cardinality

The selected single-ledger design does not add contexts. With one strategy, the
worker remains at:

```text
1 signal + (4 intervals × 1 strategy × 2 workflows) + 2 Portfolio = 11 contexts
```

The middleware therefore adds `0` contexts and `0` repeated context entries per
snapshot.

## Validation status

- Gateway fail-first regression: captured.
- Client normalization fail-first regression: captured.
- Alpha comparability warning fail-first regression: captured.
- `go vet ./...`, targeted race tests, full Go tests, all `159` web tests,
  frontend build, changed-file ESLint, exact protobuf parity, and diff checks
  passed locally.
- Prompt 03 middleware commit
  `d96c71422cea0a4eb7a4f2d66b5d9d44b3ef1e04` completed CI/CD run
  `30381933500`; web, worker stack, and runtime deployments succeeded.
- Worker commit `4906dbe535f4b23120059a0da50c6ea76eddd51e`
  completed Build and Deploy run `30381357564`; all four Coolify groups
  deployed and verified successfully.
- Production `/healthz` and `/api/v1/health` both returned HTTP `200`.

## Production memory

Run `30384137825` measured exactly `18` running containers using immutable image
`finance-live-action_sha-4906dbe535f4b23120059a0da50c6ea76eddd51e` at
`2026-07-28T17:44:17Z`.

The Docker memory metric removes inactive cache:

```text
workers=18
total_mib=1556.223
avg_mib=86.457
min_mib=22.324
max_mib=141.688
limit_mib_per_worker=512.000
```

The workflow is committed in `183b4350be1687e9f4f3b1dc96523d4a27ff628f`.
Delivery is `done`, awaiting human verification.
