# Correction banner: Portfolio measurement integrity

This banner accompanies the `portfolio-measurement-integrity` implementation.

The daily-profit gate verdicts recorded in rounds **335, 336, and 337**, and
the other historical `--daily-profit-gate` results that used the same replay,
described an unguarded one-ledger `on_kline` configuration. They must not be
silently compared with the corrected Portfolio-faithful stream. The corrected
path applies construction, historical risk evaluation, execution-target
filtering, and target execution; the legacy stream remains only as an
explicitly labelled control.

Round 371's reported Portfolio result (approximately `-9.91` versus
`-4.82`, roughly a 2x understatement) is historical evidence of that replay
gap, not a result to be rewritten. Future hold-bearing gate runs should record
the hold setting, Portfolio-faithful result, and legacy control separately.

No historical verdict is reinterpreted by this banner.
