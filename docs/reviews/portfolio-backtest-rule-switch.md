# Portfolio Rule selection resets when switching Realtime → Backtest

Investigation only — not applied. User-reported: "UI chọn Portfolio Realtime
thì rule đúng nhưng chọn Backtest thì sai" (the Rule shown for Portfolio
Realtime is correct, but switching to Backtest shows the wrong Rule).

## Root cause

`web/src/components/TradingScopeSwitcher.tsx:47-51`:

```ts
const selectWorkflow = useCallback((workflow: TradingWorkflow) => {
    if (workflow === selectedScope?.workflow) return;
    const next = pickContextForLaneWorkflow(contexts, currentLane, workflow);
    setSelectedScopeId(next?.scope_id ?? null);
  }, [contexts, currentLane, selectedScope, setSelectedScopeId]);
```

`pickContextForLaneWorkflow` (`web/src/utils/tradingScope.ts:132-141`) filters
contexts down to `{lane: portfolio, workflow: backtest}` and hands them to
`selectDefaultContext` — the same picker used for the app's *initial* default
scope on page load. That picker's sort order
(`web/src/utils/tradingScope.ts:78-98`) is: lane priority (irrelevant, all
Portfolio already) → realtime-over-backtest preference (irrelevant, both
already Backtest after the filter) → **`scope_id` alphabetical** → insertion
index.

Neither `selectWorkflow` nor `selectLane` (`tradingScope.ts:42-46`) passes the
currently-selected `strategy_id` (the "Rule" for Portfolio — see
`VARIANT_LABELS` in `TradingScopeSwitcher.tsx:15-18`) through to the picker.
So clicking the "Backtest" pill while Rule = e.g. `compounding-10pct` is
selected under Realtime does not look for a `compounding-10pct` Backtest
context — it silently lands on whichever Backtest Portfolio context sorts
first by `scope_id`, which is very unlikely to be the same rule the user was
just looking at. The Rule `<select>` then reflects that arbitrary pick, not
the one implied by what was on screen a moment ago.

This is the same gap for lane switches too (`selectLane`,
`tradingScope.ts:42-46`, already passes `selectedScope?.workflow` through to
preserve the *workflow* axis — but nothing preserves `strategy_id`), but the
user's report is specifically about the Realtime→Backtest workflow pill,
which is the more common path since both pills sit right next to each other
in the same switcher.

## What correct looks like

Switching the Backtest/Realtime pill (or the lane pill) while staying on the
same Rule should keep showing that Rule's data if a same-`strategy_id`
context exists in the new workflow/lane; only fall back to
`selectDefaultContext`'s arbitrary pick when no matching `strategy_id` exists
there.

## Fix direction (not applied — investigation only)

In `pickContextForLaneWorkflow` (`tradingScope.ts:132-141`), accept an
optional `preferredStrategyId` parameter and prefer a context whose
`strategy_id` matches it within `laneContexts`/`matching`, falling back to
`selectDefaultContext` only when no match exists. Thread
`selectedScope?.strategy_id` into both call sites in
`TradingScopeSwitcher.tsx` (`selectLane` and `selectWorkflow`, alongside the
existing `selectedScope?.workflow` argument `selectLane` already passes).

## Verification checklist for whoever implements this

- Unit test in `tradingScope.test.ts`: given Portfolio contexts with the same
  `strategy_id` present in both `realtime` and `backtest` workflows,
  `pickContextForLaneWorkflow(contexts, 'portfolio', 'backtest',
  'compounding-10pct')` returns the Backtest context with that exact
  `strategy_id`, not the alphabetically-first one.
- Unit test: when no matching `strategy_id` exists in the target
  workflow/lane, falls back to today's `selectDefaultContext` behavior
  (no regression).
- `TradingScopeSwitcher.test.tsx` (or equivalent): clicking the Backtest pill
  while a non-default Rule is selected keeps the Rule `<select>` showing the
  same rule label, not a different one.
- Manual: on `/trading/journal` or `/trading/overview`, pick a Portfolio
  Realtime rule other than the alphabetically-first one, click "Backtest",
  confirm the Rule dropdown still reads the same rule (or, if that rule has
  no backtest run, confirm it's obviously a fallback rather than silently
  swapped).
