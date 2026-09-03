# phase-agent-python-spawn-layer

## LIVE_SMOKE evidence (2026-09-03)

- Ran the fully SDK-backed chain with separate temporary compatibility state
  directories so the legacy runtime state was not modified.
- Claude account `personal-02` was selected explicitly, with the configured
  `sonnet`/`high` candidate.
- The bounded command completed successfully with:
  `Quant iteration 2 completed with claude`.
- The first setup attempt used one directory for both state schemas and was
  rejected before provider startup; the retry used distinct phase-agent and
  quant-research state directories and reached the provider successfully.
