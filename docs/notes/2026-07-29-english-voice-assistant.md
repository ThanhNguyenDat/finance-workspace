---
title: English Voice Assistant Implementation Notes
tags: [implementation, english, voice, web-speech, streaming]
author: codex/executor
status: complete-awaiting-human-verification
related:
  - "[[prompts/2026-07-29-english-02-voice-assistant]]"
  - "[[docs/notes/2026-07-29-english-web-chat-and-telegram-sync]]"
---

# English Voice Assistant

## Contract

The English page keeps text chat as the only conversation path. Voice input is
a browser-only adapter that places a final transcript into the existing
`/api/v1/english/chat/stream` request; voice output consumes the same streamed
assistant deltas already rendered by the page. No server route, provider key, or
audio storage was added.

The microphone is created only after the user presses **Speak message**. Interim
recognition results update the existing Message field, and recognition end sends
the transcript through the same sender used by the form. A second press stops
listening and completes that flow.

## Browser and privacy behavior

- The page detects `SpeechRecognition` and the prefixed
  `webkitSpeechRecognition` implementation.
- If recognition is missing, or the page is outside a secure context, the
  microphone control is hidden and the reason explicitly says text chat still
  works.
- The UI states before activation that browser recognition may send audio to its
  provider, that Chrome uses Google, and that HTTPS is required.
- Permission denial, missing audio capture, no speech, and network failures map
  to actionable text-chat fallbacks.
- Audio is never persisted by this application; only the resulting transcript
  enters chat state.

## Streamed speech output

`drainCompleteSentences` retains an incomplete tail across SSE deltas. Complete
sentences are passed one at a time to `SpeechSynthesisUtterance`; a final
unpunctuated tail is spoken only after the stream closes. This prevents fragment
audio such as `"First frag"` followed by `"ment."`.

The **Read tutor replies aloud** preference is stored in local storage. Turning
it off immediately cancels queued browser speech, and the setting is restored on
the next page load. Browsers without speech synthesis keep text replies and show
an explicit explanation.

## Verification

- Full web Vitest suite: 169 tests passed across 36 files. The 6 new tests cover
  interim/final recognition, the shared text send path, sentence buffering,
  unsupported-browser fallback, permission denial, and persisted spoken-reply
  preference.
- Production TypeScript/Vite build passed.
- ESLint passed for all changed TypeScript files. Repository-wide lint still has
  pre-existing findings in `ThemeContext.tsx` and `useKlinesData.ts`.

## Delivery evidence

- Implementation commit:
  `7bc9fb9612574032c6ed302ebffce02fd50400fb`.
- GitHub Actions run
  [30446478666](https://github.com/ThanhNguyenDat/finance-mw/actions/runs/30446478666)
  completed successfully for that exact commit, including contract parity,
  validation, web image publication, and the web deployment job.
- `https://finance.thanhne.io.vn/healthz` returned `{"status":"ok"}` after the
  deployment.
- The production HTML referenced `/ui/assets/index-CZht20nM.js` and
  `/ui/assets/index-DM8DESo1.css`, matching the assets produced by the verified
  local build.

The prompt is complete and awaits human verification of the real microphone and
spoken-reply interaction.
