# Proposal: Notion-sourced English review reminders on Telegram

Status: proposal, not applied. Written by Claude, for Codex to implement.
User request (verbatim intent): watch a personal Notion page of English
lesson notes, and repeatedly cycle through it on a fixed schedule, sending
reminders to Telegram, so nothing gets forgotten. Confirmed scope with the
user via follow-up questions before writing this:

- **Source**: a single free-form Notion page (not a structured database) —
  buổi học / lesson notes, long-form text under headings.
- **Repetition mechanism**: simple round-robin — each run sends the next
  unit(s) in the list, wrapping back to the start when it reaches the end.
  Explicitly *not* a full spaced-repetition algorithm (no per-item
  ease/interval tracking) — keep this simple for v1.
- **Cadence**: every 4 hours.
- **Delivery**: the existing `ENGLISH_TELEGRAM_BOT_TOKEN` bot, but as a
  **separate, independent send flow** — do not thread this through
  `sendEnglishSession`/`/v1/english/daily-plans/personalized`. This is its
  own message type, unrelated to the existing daily-plan pipeline.
- **Notion page**: `https://app.notion.com/p/English-1940ad67bbf880a3a1dcfcc419e26123`
  → page ID (Notion API `block_id`/`page_id` format, UUID with dashes):
  `1940ad67-bbf8-80a3-a1dc-fcc419e26123`. The user must share this page with
  whatever Notion integration is created before the token can read it.

## Grounding

Read directly from the repo, not assumed:
- `internal/automation/runner.go` — job constants, `scheduledJobs`, `Config`
  (env-driven, see `ConfigFromEnv()`), `Run()` dispatch switch, `Doctor()`
  required-env check, `r.telegram(ctx, token, payload)` helper (already used
  by `english.go`/`facebook.go`/`threads.go` — reuse this exact helper for
  sending, don't reimplement the Telegram call).
- `internal/automation/english.go` — shows the established shape for a new
  automation file: one function per concern, calls back into finance-mw's
  own HTTP API for anything stateful rather than touching Postgres directly
  from the `automation` package.
- `internal/initialize/job_worker.go` — `automationJobSchedules()` returns
  `[]jobs.CalendarSchedule{{Job, Every, Timeout}, ...}` (interval-based) or
  `{Job, Hour, Minute, Timeout}` (fixed daily time) entries; the scheduler
  (`jobs.CalendarScheduler`) runs whichever job constants appear here. This
  job wants `Every: 4 * time.Hour`.
- Confirmed via a repo-research pass: **no generic key-value/checkpoint/
  cursor mechanism exists** anywhere in the codebase reachable from
  `internal/automation` (the only "checkpoint"-ish code is
  `internal/repository/kline/cache_repository.go`'s Redis-backed
  `SetNewestOpenTime`/`GetNewestOpenTime`, hardcoded to kline
  instrument/interval, not reusable as a generic named cursor). A new tiny
  piece of state is unavoidable for the round-robin position.
- Smallest existing template for adding that state, matching the
  established "automation job calls finance-mw's own API" pattern:
  - Ent schema: `internal/persistence/english/ent/schema/entities.go` — the
    existing `DailyReview` entity (5 fields, `entsql.Annotation{Table:
    "english_daily_reviews"}`) is the pattern to copy for a new minimal
    entity, e.g. `NotionReviewCursor` with fields `key string unique`
    (so this table can serve any future page/job, not just this one),
    `position int`, `updated_at`.
  - Migration: raw SQL file under `migrations/english/`, timestamp-prefixed
    (e.g. `migrations/english/20260815HHMMSS_create_notion_review_cursor.sql`),
    generated via `make ent-generate` then
    `make make-migration MIGRATION_ENV=english MIGRATION_NAME=<name>`,
    applied via `make migrate MIGRATION_ENV=english`. Uses Atlas
    (`scripts/database.py`), the same tool the rest of the repo's schema
    changes already go through — don't hand-write ad-hoc SQL outside this
    flow.
  - Controller: thin, delegates to a service method — follow
    `internal/interfaces/http/controllers/english_controller.go` +
    `internal/services/english_service.go`'s existing shape (e.g.
    `VocabularyReview`, `CreateDailyReview` around lines 157–304 of the
    service file) rather than inventing a new controller pattern.
    Two endpoints are enough: read current cursor, advance-and-return-next.

## Proposed implementation shape

1. **New Config fields** in `runner.go`'s `Config`/`ConfigFromEnv()`:
   `NotionAPIKey` (env `NOTION_API_KEY`), `NotionEnglishReviewPageID` (env
   `NOTION_ENGLISH_REVIEW_PAGE_ID`, default to the page ID above so the env
   var only needs overriding if the page ever changes). Add both to
   `Doctor()`'s required-env check so a missing token/page fails loudly at
   startup, not silently mid-run.
2. **New job constant** `JobNotionEnglishReview` in the existing const block
   + `scheduledJobs` slice; new `case` in `Run()`'s switch.
3. **New file `internal/automation/notion_english_review.go`**:
   - `fetchNotionPageUnits(ctx, token, pageID)` — calls Notion's
     `GET https://api.notion.com/v1/blocks/{page_id}/children` (paginated
     via `next_cursor`/`has_more`, `Notion-Version: 2022-06-28` header,
     `Authorization: Bearer <token>`). Groups the flat block list into
     review units: each `heading_1`/`heading_2`/`heading_3` block starts a
     new unit; subsequent non-heading blocks belong to it until the next
     heading. For any block with `has_children: true` (e.g. a toggle
     heading), recursively fetch and append its children's text — bound the
     recursion depth (e.g. max 3) so a pathological page can't hang the job.
     Concatenate each block's `rich_text[].plain_text`. This function is a
     pure-ish transform once the raw block list is fetched — write it so
     the grouping/pagination logic is unit-testable against fixture JSON
     without a live Notion call.
   - `nextNotionReviewUnit(ctx, apiKey)` — calls the two new finance-mw
     endpoints (read cursor / advance cursor) described above, scoped by a
     fixed key string for this job (e.g. `"english-notion-review"`) so the
     same table can host a second watcher later without a migration.
   - `sendNotionEnglishReview(ctx)` — orchestrates: fetch units, if the list
     is empty log and return without erroring (an empty/unreachable Notion
     page shouldn't fail the job loudly every 4h), clamp the persisted
     cursor to the current unit count (handles the list having shrunk since
     last run — don't index out of bounds), pick the next 1–2 units, format
     a Telegram message, send via the existing `r.telegram(...)` helper
     with `EnglishTelegramToken`, advance the cursor.
4. **Schedule entry** in `automationJobSchedules()`:
   `{Job: controllers.JobNotionEnglishReview, Every: 4 * time.Hour, Timeout: 5 * time.Minute}`.

## Explicitly out of scope for v1

- Real spaced-repetition scheduling (ease factors, per-item due dates) —
  the user confirmed simple round-robin is fine to start.
- Any change to the existing `/v1/english/daily-plans/personalized` flow or
  `sendEnglishSession` — this is a parallel, independent message stream.
- Two-way sync (editing Telegram replies back into Notion) — read-only from
  Notion.

## Verification expectations before Dev-done

- Unit tests for the block-grouping/pagination transform against fixture
  Notion API JSON (headings + mixed block types + a `has_children` case +
  pagination across two pages).
- `Doctor()` test covering the two new required env vars.
- Standard local gate: `go test ./...`, `go vet ./...`, build, plus the
  Atlas migration contract test that already guards
  `migrations/english/`.
- One production sanity check after deploy: confirm the job actually fires
  on schedule and a message lands in the configured Telegram chat, per the
  existing native-automation verification pattern
  (`scripts/verify-worker-stack.sh`'s `automation_smoke` style check).
