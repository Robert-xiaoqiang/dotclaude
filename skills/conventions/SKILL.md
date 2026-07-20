# Skill: conventions

## Purpose
The **map** of the project-convention skill family: how we structure a research / ML /
agent project so a coding agent and humans stay coherent. This skill doesn't do work
itself — it names the concerns and routes you to the focused skill for each. Read it when
starting or organizing a project, or when unsure which convention applies.

## When to Use
- Setting up or reorganizing a project's configs / docs / layout / run-control.
- You know you want "the convention" but not which skill.
- Onboarding a new project or a new coding agent to how this org works.

## The four concerns → which skill
| concern | question it answers | skill |
|---|---|---|
| **naming** | what do I call this config / file / run? | `naming-config` (model/pipeline/dataset/launcher slot-grammar) · `naming-descriptive` (the general primitive) |
| **layout** | where does this doc / script / artifact live? | `layout-workspace` (`docs/`, `scripts/`, reports/plans, what's committed) |
| **docs** | how do I write/maintain the living docs? | `docs-plan` (`docs/plans/<date>-<topic>.md`) · `docs-arch` (`docs/ARCH.md`) |
| **run-control** | how is a run specified + submitted across platforms? | `platform-run` (neutral `task.yaml` → DLC/Slurm/EAI) |
| **env / ops** | machine setup & project relocation | `env-cluster` (env.sh / cluster env) · `env-migrate` (relocate a project dir) |

## The philosophy (one line each)
- **naming** — a config's *name* uniquely identifies what runs; two ablation arms differ in
  exactly the slots that describe the change (`naming-config`).
- **layout** — plans, reports, and re-runnable scripts persist in predictable places, out of
  the source tree (`layout-workspace`).
- **docs** — a project keeps one living architecture ref (`docs-arch`) and dated, actionable
  plans (`docs-plan`).
- **run-control** — a run is a *platform-neutral* spec rendered per platform; platform IDs
  live in a separate profile, never the spec (`platform-run`).

## How the concerns connect at a launcher
A single launcher ties three of them together: `naming-config` fixes its **name** and its
model/pipeline/dataset triple; `platform-run` fills its **`task.yaml`** (neutral spec) and
renders it; `layout-workspace` says the launcher and `platforms/` profiles live at repo
top-level. Output dirs derive mechanically under `OUTPUT_DIR_HOME` (never the project dir).

## Companions
Every skill in the family should link back here. Non-family skills (`git-commit`,
`git-push`, `writing-style`) are separate.
