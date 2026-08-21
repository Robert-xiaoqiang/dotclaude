---
name: docs-plan
description: "Create or update a structured task plan under docs/plans/<date>-<topic>.md so multi-step work has a written, resumable design."
when_to_use: "Use when a task is non-trivial or spans multiple files or modules."
---
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

   A plan that grows stages, a job ledger, and its own experiment record becomes a
   **directory** at the same path, keeping the same `<date>-<topic>` name:
   `docs/plans/YYYY-MM-DD-<topic>/plan.md` plus its siblings. That is the only
   sanctioned second form, and `claude-auto-research` owns what goes inside it.
   Do not promote a plan to a directory before it needs one.

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
- A long-horizon campaign is a plan, not a new location. Its state lives in the
  plan directory above, never at the repo root and never under `$OUTPUT_DIR_HOME`
  (see `claude-auto-research`)

## Output
- Confirm plan file path
- Summarize key steps briefly
