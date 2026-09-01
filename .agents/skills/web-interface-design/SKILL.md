---
name: web-interface-design
description: Design or revise finance-web React screens using existing tokens, components, themes, accessibility patterns, and responsive behavior. Use before adding a page, panel, interaction, or CSS rule, or when a screen is cluttered or unreadable.
---

# Web Interface Design

Build the smallest coherent interface from the existing design system, with
content hierarchy and interaction behavior driving layout choices.

## Inputs and output

Input is the user task, content hierarchy, existing component/token inventory,
and required states. Output is a responsive, themed, accessible implementation
that reuses established patterns and passes the repository's web checks.

## Workflow

1. Inspect nearby screens, tokens, and reusable components.
2. Define the primary action and information hierarchy before layout/CSS.
3. Reuse semantic components and tokens; add a style only when no existing
   pattern expresses the requirement.
4. Implement loading, empty, error, overflow, and interaction states together.
5. Verify keyboard behavior, accessible names, both themes, and responsive sizes.
6. Run bounded lint, tests, typecheck, and production build.

## Non-negotiable invariants

- Do not invent colors or bypass theme tokens.
- Component choice follows content semantics, not visual proximity.
- Empty data, loading, and broken data are distinct states.
- Preserve accessible names and avoid drawer/overflow interaction regressions.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for token usage, component
selection, conversation/voice behavior, known layout traps, CSS isolation,
drawer/overflow contracts, theme/accessibility checks, and completion criteria.
Read only the sections relevant to the surface being changed.
