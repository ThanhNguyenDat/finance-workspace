---
title: English Conversation Surface Implementation Notes
tags: [implementation, english, conversation, streaming, accessibility]
author: codex/executor
status: complete-awaiting-human-verification
related:
  - "[[prompts/2026-07-29-english-04-conversation-surface]]"
  - "[[docs/notes/2026-07-29-english-voice-assistant]]"
  - "[[docs/notes/2026-07-29-english-telegram-deep-link]]"
---

# English Conversation Surface

## Contract

English now has two data-owned routes:

- `/english` renders Telegram linking, tutor voice preference, and status. It
  does not load chat history.
- `/english/chat` renders the conversation workspace. It does not call the
  Telegram link-code endpoint.

The English-only application entry lands on `/english/chat`. The shared header
links to chat, settings links back to chat, and chat links unconfigured users to
settings. Unknown `/english/*` routes return to `/english`.

## Conversation behavior

Learner and tutor turns are full-width rows, not chat bubbles. Learner rows use
the base surface while tutor rows use the raised surface, so speaker identity is
visible through background and spacing before reading the supplementary label.
All colors come from the existing theme tokens.

The conversation owns its scroll container. A small bottom threshold tracks
whether the reader is pinned to the newest message. Streaming deltas scroll only
while pinned; scrolling up preserves the reader's position. The active assistant
row has a distinct streaming state, while `aria-live` remains on the conversation
region.

Quick replies provide the predictable tutor actions without changing the
existing SSE request path. Speech recognition, buffered speech synthesis, text
chat, and Telegram linking retain their existing data contracts.

## Verification

- Finance MW CI/CD run
  [30451601753](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30451601753)
  passed for implementation commit
  `dd8a5fa7fb2501c546b9e7f139acfeeb4650e25c`.
- The CI web suite passed 184 tests across 38 files.
- The TypeScript/Vite production build and changed-file ESLint checks passed.
- Tests cover dedicated route ownership, speaker-distinct rows, streaming state,
  navigation, settings fallback, and scroll position preservation during SSE.
- Runtime, migration, worker, and automation jobs were skipped because path
  detection correctly classified this as a web-only delivery.

## Production evidence

- Coolify web deployment completed successfully.
- `https://finance.thanhne.io.vn/healthz` returned `{"status":"ok"}`.
- `/english`, `/english/chat`, and `/english/unknown` returned HTTP 200.
- Production referenced `/ui/assets/index-BZUK9ZxA.js` and
  `/ui/assets/index-CKGTTVdt.css`, exactly matching the verified local build.

The conversation layout and deployment are complete. The prompt is `done` and
awaits human verification.
