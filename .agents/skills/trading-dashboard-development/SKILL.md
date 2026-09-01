---
name: trading-dashboard-development
description: Build or revise Finance trading-dashboard screens that consume Finance Live Action metrics and trade history while preserving ledger, broker, authorization, and freshness semantics. Use for dashboard layout, interaction, chart, and monitoring changes.
---

# Trading Dashboard Development

Present trading state truthfully and make the route's current condition legible
without duplicating or inventing domain meaning.

## Inputs and output

Input is the metric/API contract, target user task, affected route or scope, and
existing design tokens/components. Output is a tested dashboard change with
clear information ownership, accessible interaction, and production evidence.

## Workflow

1. Read the current API/metric contract and identify freshness and scope.
2. Choose one information hierarchy from the user's decision path.
3. Reuse existing tokens and components; keep raw trading identifiers intact.
4. Distinguish unavailable, empty, stale, loading, and error states.
5. Validate responsive layout, both themes, keyboard/accessibility behavior,
   chart interactions, and authorization boundaries.
6. Run bounded web checks and verify the deployed dashboard against live data.

## Non-negotiable invariants

- Never turn missing metrics into zero or aggregate incompatible ledgers.
- Do not relabel broker/order semantics for visual convenience.
- One fact has one visual owner; summaries link to detail rather than duplicate it.
- A healthy page shell is not proof that trading data is current.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for metric truth rules,
layout selection, route composition, chart workspace, interactions, visual
checks, testing, and deployment evidence. Read only the sections matching the
screen and interaction being changed.
