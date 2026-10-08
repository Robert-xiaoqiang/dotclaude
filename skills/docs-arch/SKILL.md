---
name: docs-arch
description: "Keep docs/ARCH.md consistent with the current codebase, so the architecture reference never drifts from the code it describes."
when_to_use: "Use after a structural change or a refactor."
---
# Skill: docs-arch

## Purpose
Keep docs/ARCH.md consistent with the current codebase.

## When to Use
- After structural changes
- After refactor
- After adding/removing modules
- When user mentions architecture

## Steps
1. Inspect relevant code changes
2. Update docs/ARCH.md:
   - modules and responsibilities
   - data/control flow
   - key abstractions

## Rules
- Keep it high-level (not line-by-line code)
- Reflect actual implementation (not intention)
- Be concise and structured
- `docs/ARCH.md` lives in the workspace layout (see `layout-workspace`);
  reports/walkthroughs go in `docs/reports/`, not in ARCH.md

## Output
- Confirm ARCH.md updated
- Brief summary of changes

## Companions
`docs-plan` (dated plans for work in flight; this file is the living reference they update) · `layout-workspace` (where `docs/` lives and what is committed) · `claude-auto-research` (a campaign's ledger links back to the architecture it changes) · `code-abstraction` (the roles and contracts this file
records) · `conventions` (the family index).
