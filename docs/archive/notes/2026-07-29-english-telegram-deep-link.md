---
title: English Telegram Deep Link Implementation Notes
tags: [implementation, english, telegram, deep-link, security]
author: codex/executor
status: complete-awaiting-human-verification
related:
  - "[[prompts/2026-07-29-english-03-telegram-deep-link]]"
  - "[[archive/notes/2026-07-29-english-web-chat-and-telegram-sync]]"
---

# English Telegram Deep Link

## Contract

`POST /api/v1/english/telegram/link-code` still creates and stores only the
SHA-256 hash of a ten-minute, single-use code. The response now also includes
an optional `deep_link` built by the backend:

```text
https://t.me/<bot_username>?start=<one-time-code>
```

The browser never receives the Telegram bot token. The backend resolves the bot
username through Telegram `getMe`, validates the returned bot identity, caches a
successful username for the process lifetime, and applies a one-minute retry
backoff after failures. A `getMe` failure omits `deep_link` but does not fail code
creation.

The public webhook recognizes `/start <code>` and hashes only the payload. Plain
manual codes continue through the same atomic, expiring, single-use repository
operation used before this change.

## Web behavior

After code generation, the English page shows:

- the manual code and ten-minute expiry;
- an **Open English bot** action when the backend supplied a valid `t.me` URL;
- a **Copy code** fallback in both the linked and link-unavailable cases;
- explicit manual instructions when Telegram bot discovery is unavailable.

The deep link is opened with `noopener` and `noreferrer`. No analytics event,
page title, or application log receives the one-time code.

## Verification

- Full Go suite: `go test ./...` passed.
- English webhook/service regressions cover cached `getMe`, token
  non-disclosure, graceful `getMe` failure, `/start` payload extraction, and the
  existing unique-violation mapping.
- Full web Vitest suite: 171 tests passed across 36 files.
- Production TypeScript/Vite build passed.
- ESLint passed for the changed English page and tests.

## Delivery evidence

- Implementation commit:
  `2e63691454951c96b01be178b2ef2c72406f015b`.
- Finance MW CI/CD run
  [30449281097](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30449281097)
  completed successfully for that exact commit. Go and web validation passed,
  both immutable images published, all database migration streams applied, and
  the web, runtime, and worker stack production deploy gates passed.
- The production health endpoint returned `{"status":"ok"}`. An unauthenticated
  `POST /api/v1/english/telegram/link-code` returned `401` without exposing a
  token or link payload.
- The implementation web build produced `index-B8E8bcEI.js` and
  `index-D1vCwIvd.css`; production referenced those exact assets after the
  implementation deploy.
- A preserved automation commit,
  `93cba10efad5a8a770d1b58389111ea7e8f451e7`, then centralized business route
  ownership without changing the English deep-link contract. Its full 176-test
  web regression and build passed locally, and CI/CD run
  [30450005278](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30450005278)
  completed successfully with runtime, migrations, and worker deploys correctly
  skipped. The final production page references the exact verified assets
  `index-xSnJChDh.js` and `index-D1vCwIvd.css`.

The backend/provider boundary, manual fallback, `/start` payload path, and
production deployment are complete. Opening the link with a real Telegram
identity and observing the one-tap account link is intentionally reserved for
human verification.
