# Skill: vibe-workspace-layout

## Purpose
Lay out the **agent-facing workspace** of a project — the docs and cached scripts a
coding agent (and you) produce during sessions — so the work is **reusable and
recoverable**, not lost in a chat scratchpad. This is project scaffolding, kept
distinct from source code, tests, packaging, and `.gitignore`.

## When to Use
- Working a project with a coding agent ("vibe coding") — setup or maintenance
- The user asks for a plan, report, design walkthrough, or you generate a one-off
  script during a session
- Deciding *where* a doc or script should live
- Reviewing / tidying repo layout

## The layout
```
docs/
  ARCH.md                          # single architecture reference (see arch-update)
  plans/<YYYY-MM-DD>-<topic>.md     # timestamped task/design plans (see plan-doc)
  reports/<topic>.md | .html        # walkthroughs/figures that explain the system
scripts/
  README.md                         # what's here + the convention
  checks/                           # re-runnable verification/smoke scripts (committed)
  migration/  setup/  oneoff/       # purpose subdirs; machine-specific ones git-ignored
```

## Rules
- **Plans** → `docs/plans/`, filename `YYYY-MM-DD-<topic>.md` (timestamp orders history).
- **Reports** (workflow/architecture walkthroughs, figures, HTML) → `docs/reports/`
  — not `docs/design/`.
- **Architecture doc** → a single `docs/ARCH.md`, kept current.
- **Session scripts** (checks, migrations, data munging, verification, setup) →
  `scripts/<purpose>/` as durable **checkpoints** — never leave them only in `/tmp`
  or a scratchpad. Header each script with **what · when · usage**.
- **Commit reusable scripts; git-ignore machine-specific/secret ones** (e.g. a
  `scripts/migration/` helper with hardcoded local paths).
- Name everything descriptively (companion: `descriptive-naming-pattern`) — never
  `v1`/`Px`/`tmp`/`final2`.
- Keep all of this **out of** the package/source/test trees — it is doc-level
  scaffolding, not shipped code.

## Why
A coding agent's value compounds when its plans, reports, and scripts persist in a
predictable place: you can re-run a check, recover a migration, or re-read the
design later without regenerating it. Scratchpad-only artifacts vanish between
sessions.

## Output
- Confirm the doc/script path used and which subdir, and whether it's committed or
  git-ignored.

## Companions
`plan-doc` (writes `docs/plans/…`) · `arch-update` (maintains `docs/ARCH.md`) ·
`descriptive-naming-pattern` (how to name) · `git-commit` (commit conventions).
