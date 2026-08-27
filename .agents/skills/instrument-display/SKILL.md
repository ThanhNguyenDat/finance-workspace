---
name: instrument-display
description: Standardize user-facing trading instrument labels without changing raw symbols used by APIs, brokers, storage, or order execution.
---

# Instrument Display

Use one explicit identity format everywhere a trading instrument is shown:

`BASE/QUOTE · broker market_type`

Examples:

- `1000BONK/USDT · binance perpetual_future`
- `XAU/USD · exness mt5`

## Rules

1. Keep the raw venue symbol unchanged for API queries, websocket identity,
   storage keys, broker orders, and external trading URLs.
2. Store `baseAsset`, `quoteAsset`, `broker`, and `marketType` as composition
   metadata. Do not rely on suffix parsing when explicit metadata is available.
3. Render labels through `web/src/utils/instrumentDisplay.ts`; do not duplicate
   string formatting in components.
4. Only create an external broker link when the formatter knows the broker's
   URL contract. Never send an MT5 or Exness symbol to a Binance URL.
5. Cover numeric contract bases such as `1000BONK`, commodity symbols, and
   explicit MT5 suffix variants with unit tests.
6. Run bounded web tests and the production build after changing instrument
   identity or display behavior.
