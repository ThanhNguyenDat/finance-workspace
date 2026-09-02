---
name: test-timeouts
description: Enforce bounded execution for unit, integration, load, contract, shell, browser, and end-to-end tests. Use when adding or changing tests, test scripts, Make targets, package scripts, or CI workflows so deadlocks cannot occupy local or self-hosted runners indefinitely.
---

# Test Timeouts

Apply layered timeouts to every non-interactive test run.

## Contract

1. Prefer a framework-native suite timeout when it terminates the full process,
   such as `go test -timeout=10m`.
2. Otherwise wrap the test command with
   `timeout --signal=TERM --kill-after=30s <duration>`.
3. Give subprocesses created inside tests an API-level timeout.
4. Set `timeout-minutes` on every GitHub Actions job as the final boundary.
5. Clean up containers and child processes with traps after timeout or failure.
6. Keep interactive watch mode out of CI; watch mode is the only unbounded
   exception.

For model-owned verification runners, keep the check plan small and
sequential so the agent can emit its final gate before the phase deadline.
Do not ask the agent to clean temporary files with `rm`/`rm -f`; shell-tool
routers may reject those commands. Prefer repository test scripts that own
their bounded cleanup, or leave transient evidence under the runtime log root.

Use a short timeout for deterministic unit and shell tests, and a larger
explicit timeout for integration, image, or end-to-end suites. A timeout must
fail the run visibly; never convert it to success.
