---
name: web-interface-design
description: Design and change screens in the finance-web React SPA using the tokens, components and theming that already exist. Use before adding a page, laying out a panel, choosing colours, or reaching for a new CSS rule, and when a screen reads as cluttered, unreadable, or generic.
---

# Web Interface Design

The SPA already has a design system. Almost every visual problem here comes from
**not using it**, or from using the wrong existing component for the content — not
from missing styles.

## The tokens are the palette. Do not invent colours.

`web/src/App.css`, `:root`:

| Group | Tokens | Use for |
|---|---|---|
| Surface | `--bg-base`, `--bg-surface`, `--bg-raised`, `--bg-hover` | depth, in that order |
| Line | `--border`, `--border-md` | `--border-md` only when something must read as separate |
| Text | `--text-1`, `--text-2`, `--text-3` | primary, secondary, tertiary |
| Meaning | `--positive`, `--negative`, `--warn` | numbers and states only |
| Section | `--layer-trade`, `--layer-strategy`, `--layer-data`, `--layer-alert`, `--layer-control` | the accent of a page |
| Shape | `--r`, `--font-ui`, `--font-mono` | radius 6px, two families |

A hard-coded hex in a new rule is a defect. The file carries **77** light-theme and
`prefers-color-scheme` rules — a raw colour will look correct in one theme and wrong
in the other, and nobody will notice until a user switches.

Each page owns one accent from the section row. English is `--layer-strategy`, the
trade dashboard is `--layer-trade`. Use the page's accent for emphasis; do not
introduce a sixth colour.

## Reuse the component that matches the *content*, not the one that is nearby

This is the mistake worth naming, because it has already shipped.

The English conversation rendered every message as `.callout-grid` with a `.label`
and a `.sub` — the same component used by the settings panel directly above it. The
result: learner and tutor turns had identical alignment, background, size and
spacing, and the only difference was a small word. A conversation is about **whose
turn it is**, and the layout encoded none of it. It read as a list of properties
because it was built from a list-of-properties component.

Before reaching for `.card`, `.callout-grid`, `.label`, `.sub`, ask what the content
*is*:

| Content | Needs |
|---|---|
| Key/value facts | `.callout-grid` with `.label` + `.sub` — correct as-is |
| A conversation | see the section below |
| A time series | a chart, not a table of numbers |
| A choice among peers | tabs or a select, sized to the longest real option |
| A status | `.pill` or `.meta-badge`, never a sentence in `.sub` |

If no existing component fits the content, that is the moment to add one — with
tokens, and styled for both themes.

## Conversation surfaces specifically

Checked against how ChatGPT, Claude and Chainlit render chat, because this app has
one and it was built wrong once.

**Do not use chat bubbles.** Full width is the current convention for a serious
assistant; bubbles read as a messenger and undercut the tool framing. This app is a
dashboard, so full width also matches everything around it. Bubbles are only right
when the chat is a small widget rather than the main surface.

Separate the speakers with **restraint**, not shape:

- A different background — `--bg-raised` for the assistant, transparent for the
  learner — is enough. One step of contrast, not two.
- Vertical rhythm between turns carries more than any border does. Space is the
  cheapest separator and the one that survives both themes.
- A small role label is fine as a *supplement*. It must not be the only signal, which
  is exactly the fault that shipped.

**Streaming is table stakes, and first token is what people feel.** A blank pause
before anything appears is what reads as slow — not the total duration. Show the
first token quickly and let the rest arrive; never a spinner followed by a wall of
text.

Also expected of a conversation surface:

- Its own scroll container, newest turn in view, and auto-scroll that stops when the
  user scrolls up.
- When chat is the primary workspace, give it a dedicated route instead of placing
  it below settings. Each route should fetch only the data it renders, while keeping
  an obvious link in both directions so an unconfigured user cannot reach a dead end.
- Treat "pinned to bottom" as state derived from
  `scrollHeight - scrollTop - clientHeight`, with a small threshold. Auto-scroll on
  new streaming content only while pinned, and test the behavior with explicit
  scroll geometry so a user reading history is never pulled back to the latest turn.
- Long replies broken into readable structure rather than one block.
- A visible in-progress state distinct from a finished message.
- Quick replies when the next move is predictable. For a language tutor: correct my
  sentence, explain that grammar, make it harder.
- A fallback that recovers when the model fails, in the flow rather than as an error
  banner off to one side.

### Voice input has an end-only failure path

Browser speech recognition can fire `onend` without either a result or an error.
Treating `onerror` as exhaustive makes the microphone appear to do nothing:

- An intentional recognition session that ends without a transcript must show an
  actionable no-speech message and must not submit an empty chat request.
- Keep the text-chat input usable after every recognition failure.
- Log only the browser error code under a stable prefix; never log the transcript.
- Include unknown browser error codes in the user-facing fallback so a report is
  diagnosable.
- Cover all three terminal event sequences in tests: `result → end`, `error → end`,
  and bare `end`.

Sources: <https://www.setproduct.com/blog/ai-chat-interface-ui-design>,
<https://www.aiuxdesign.guide/patterns/conversational-ui>,
<https://thefrontkit.com/blogs/ai-chat-ui-best-practices>

## Layout traps that have actually happened here

Each of these shipped and was found by a user, not by a test.

- **`overflow-x: auto` hides things silently.** Six lane tabs sat behind a horizontal
  scrollbar; `Legacy / Unscoped` looked like it did not exist. Prefer `flex-wrap:
  wrap`. A scrollbar is acceptable for a wide table inside its own container, never
  for a row of choices.
- **A label that changes width moves the page.** The refresh button swapped between
  `↻ Refresh` and `↻ Refreshing…`, so the whole top bar shifted every poll. It read
  as jank, though nothing was slow. Keep the label fixed and animate a glyph, or
  reserve the width.
- **One `min-width` for controls holding different content.** The interval select
  holds `5m`–`4h` and shared the strategy select's 150px floor, so a
  three-character menu was as wide as one listing strategy names. Size to the
  content.
- **The breakpoint is not where the bug is.** The 768px rule already stacked the
  toolbar, so narrow screens were fine and wide screens were fine. The break lived
  in between, on an ordinary laptop. Check the middle, not just the two ends.
- **Redundant label composition.** `scopeLabel` appended `bot_id`, then
  `strategy_id`, then `run_id`, plus a window word the `display_name` already
  carried, producing `Portfolio · fixed-pct · weighted-strategies · Forward`. Append
  only what distinguishes.

## Editing CSS without breaking a neighbour

A closing brace inserted mid-rule moves every property after it into the next
selector. That shipped: adding `.trade-scope-select.compact` moved `border`,
`background`, `padding` and `font` out of `.trade-scope-select`, so the strategy
select lost its styling entirely while the interval select looked fine.

- Never insert a rule by splitting an existing one. Add complete rules between
  complete rules.
- After any CSS edit, read the diff for the rule **above** the change, not only the
  new rule.
- `{` and `}` counts must balance — cheap and it catches this exact fault.
- **Tests and the build will not catch it.** A broken visual is only caught by
  reading the diff or opening the page.

A modifier class should hold only what differs. Everything shared stays on the base
rule so the two cannot drift.

## Drawer and overflow interaction contract

A compact navigation is a drawer only on mobile. Preserve desktop sidebar persistence: selecting a desktop navigation item must not close it. On mobile, the drawer must close on navigation, backdrop click, and Escape; move focus to its close control when opened and back to the hamburger when closed. Any overflow menu follows the same Escape and click-away behavior, and its trigger receives focus after Escape. Cover both mobile and desktop paths in tests by setting `window.innerWidth`; CSS visibility alone does not exercise the behavior.

Wide data tables and heatmaps are the only approved horizontal scrollers. Give their scroll container a clear accessible label and keyboard focus, keep numeric cells non-wrapping, and never put choice controls in a horizontal scroller.

## Both themes, every time

Styling only the dark theme is half the work. Check the light variables at the top of
`App.css` and add the `.theme-light` counterpart in the same change. Contrast that
works on `#070b12` frequently fails on `#ffffff`.

## Do not break the accessible name

Tests query by role and accessible name — `getByRole('tab', { name: 'Portfolio' })`,
`getByRole('button', { name: '↻ Refresh' })`. Wrapping text in a `<span>` for styling
is safe; `aria-hidden`, an added icon with a label, or changed text is not.

Keep `aria-live` on regions that update on their own, and `aria-pressed` on toggles.
Both are already in use and both are load-bearing.

## Empty is not the same as broken

An empty state should say **why** it is empty and **what** would fill it. The Live
lane explains that a broker account is required before real orders can be submitted,
and a test guards that text. That is worth more than hiding the tab.

When something is empty by design and something else is empty by fault, they must not
look alike. Dim the deliberate ones; surface the faulty ones.

## Before finishing

```bash
cd web && npm test -- --run && npm run build
```

Any change that touches CSS, a media query, or a flex/grid container must be
checked at both a phone width (~375-430px) and a laptop width (~1280-1440px)
before it counts as done, not laptop alone. A container that stops wrapping
its children (or starts) only shows up at one end. Also drag through the
gap between the component's own breakpoints, not just past each one — a
container with no wrap set can hold together at both a narrow and a wide
preset and still collapse into a squeezed, wrapped-inside-itself mess in
between, exactly where nobody happens to test. The header identity block
shipped this once: `.chart-terminal-identity` had no `flex-wrap`, so its
lane/workflow pill switchers (each already wrapping internally) got squeezed
into a sliver next to the instrument name and stacked their own pills three
deep instead of laying out horizontally below it.

Then read the page as a user who has never seen it, at each width:

1. What is this screen for? Answerable in one glance, or the hierarchy is wrong.
2. What is the most important number or message here? It should be the loudest.
3. Is anything reachable only by scrolling sideways? Then it is hidden.
4. Does anything move while data refreshes? Then it will read as broken.
5. Switch themes. Does anything disappear?
