---
title: English Web Chat and Telegram Sync Delivery
tags: [english, web, telegram, delivery]
status: awaiting-human-verification
---

# English Web Chat and Telegram Sync

## Delivered boundary

- The React English page streams assistant deltas with server-sent events and
  persists the completed reply through the existing English chat repository.
- A browser identity requests a short-lived verification code; only a Telegram
  webhook carrying that code can bind the chat. The browser never submits a
  `chat_id` to claim ownership.
- The webhook verifies Telegram's secret token in constant time and is rate
  limited. Chat identifiers and provider keys are not written to logs or sent
  back to the browser.
- Web and Telegram messages use the same user-scoped chat history, while an
  unlinked learner can continue on the web.

## Delivery evidence

Source commit `eb292f3218867503263d7dc33f92a806a6189f10` completed GitHub
Actions run `30429282224` successfully. Validation, database migration, worker,
web, and runtime deployments passed; production `/healthz` returned
`{"status":"ok"}` after deployment.

The implementation checks ran before release:

```text
go vet ./... && go test -race ./internal/services/... ./internal/interfaces/http/...
cd web && npm test -- --run && npm run build
make atlas-validate-all
```

## Ownership-remediation evidence

Feedback reopened the prompt because an arbitrary repository failure was being
reported as a chat-ownership conflict and the ownership query had no regression
tests. Source `a8dd26a8f189db6a4ee889898fad062cfca2ada5` now maps only PostgreSQL
unique violation `23505` to `409`; all other link-verification failures return
`500`. Its repository tests cover expiry, one-time consumption, and prevention
of a second user taking an existing chat identifier. GitHub Actions run
`30438317323` completed validation, migration, worker deployment, and runtime
deployment successfully.

## Verification handoff

Status is `done`, awaiting a human verifier with an actual learner session and
Telegram bot. Confirm the prompt's four observable cases: streaming web reply,
Telegram-to-web visibility, rejection of another person's `chat_id`, and normal
web chat while Telegram remains unlinked. This handoff deliberately does not
manufacture production learner traffic or disclose a real chat identifier.
