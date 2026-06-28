# Skill: arch-update

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
- `docs/ARCH.md` lives in the workspace layout (see `vibe-workspace-layout`);
  reports/walkthroughs go in `docs/reports/`, not in ARCH.md

## Output
- Confirm ARCH.md updated
- Brief summary of changes
