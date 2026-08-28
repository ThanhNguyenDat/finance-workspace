---
name: business-prompt-delivery
description: Track and deliver Finance ecosystem business prompts through the owning repository and verified deployment.
---

# Business Prompt Delivery

Use this skill when a Finance business prompt needs to be tracked, implemented,
and delivered across the repository that owns the affected runtime behavior.

## Boundaries

- Keep orchestration artifacts, handoff, and evidence in `finance-workspace`.
- Make runtime changes only in the owning Finance repository.
- Read the applicable repository rules and shared delivery/verification skills
  before implementation.
- Keep OpenSpec-native integrations local to the CLI that owns them.

## Delivery record

- Identify the affected repository and acceptance criteria before implementation.
- Use bounded local checks and the repository's delivery path.
- Record concise SHA, CI, deployment, and verification evidence in the handoff.
- Leave implementation in `Verify` until Claude completes independent review.
