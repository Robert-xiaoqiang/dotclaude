# Skill: docs-plan

## Purpose
Create or update structured task plans in docs/plans/.

## When to Use
- Task is non-trivial
- Multiple files/modules involved
- User asks for plan / design
- Before large modifications

## Steps
1. Create or update:
   docs/plans/YYYY-MM-DD-<topic>.md

2. Structure:
   - Goal
   - Context
   - Affected components
   - Plan (step-by-step)
   - Risks / assumptions
   - Verify (if possible)

3. Verification Design
- Prefer lightweight, executable checks:
  - unit tests
  - small scripts
  - CLI runs
- If execution not possible:
  - define expected behavior or invariants

## Rules
- Be concise but structured
- Prefer updating existing plan if relevant
- Avoid duplicate plan files
- Ensure plan is actionable and verifiable
- Plans live under `docs/plans/` per `layout-workspace`; name the topic
  descriptively (`layout-workspace` companion: `naming-descriptive`)

## Output
- Confirm plan file path
- Summarize key steps briefly
