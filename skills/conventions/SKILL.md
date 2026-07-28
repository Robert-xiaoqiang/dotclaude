# Skill: conventions

## Purpose
The **map** of the project-convention skill family: how we structure a research / ML /
agent project so a coding agent and humans stay coherent. This skill doesn't do work
itself — it names the concerns and routes you to the focused skill for each. Read it when
starting or organizing a project, or when unsure which convention applies.

## When to Use
- Setting up or reorganizing a project's configs / docs / layout / platform.
- You know you want "the convention" but not which skill.
- Onboarding a new project or a new coding agent to how this org works.

## The concerns → which skill
| concern | question it answers | skill |
|---|---|---|
| **naming** | what do I call this config / file / run? | `naming-config` (model/pipeline/dataset/launcher slot-grammar) · `naming-descriptive` (the general primitive) |
| **layout** | where does this doc / script / run output live? | `layout-workspace` (`docs/`, `scripts/`, reports/plans, what's committed) · `layout-output` (the run-output tree under `$OUTPUT_DIR_HOME`) |
| **docs** | how do I write/maintain the living docs? | `docs-plan` (`docs/plans/<date>-<topic>.md`) · `docs-arch` (`docs/ARCH.md`) |
| **platform** | how do I set up, submit to, and match the runtime of a compute platform? | `platform-env` (env.sh / cluster setup) · `platform-run` (neutral `task.yaml` → DLC/Slurm/EAI) · `platform-runtime` (driver × image × venv × storage stack) |
| **outputs** | how do I compare runs or reclaim their space? | `output-analysis` (latitude vs longitude, embed-style figures) · `output-cleanup` (resume-safe reclaim) |

## The philosophy (one line each)
- **naming** — a config's *name* uniquely identifies what runs; two ablation arms differ in
  exactly the slots that describe the change (`naming-config`).
- **layout** — plans, reports, and re-runnable scripts persist out of the source tree
  (`layout-workspace`), and run outputs live in a separate mechanical tree under
  `$OUTPUT_DIR_HOME` (`layout-output`).
- **docs** — a project keeps one living architecture ref (`docs-arch`) and dated, actionable
  plans (`docs-plan`).
- **platform** — working on a compute platform means setting up a persistent env on it
  (`platform-env`), submitting a platform-neutral run spec that is rendered per scheduler with
  IDs kept in a profile (`platform-run`), and matching the job's runtime stack of driver, image,
  and venv (`platform-runtime`).
- **outputs** — the `layout-output` tree is read by `output-analysis` to compare runs across
  steps and arms, and by `output-cleanup` to reclaim space while protecting resume state.

## How the concerns connect at a launcher
A single launcher ties three of them together: `naming-config` fixes its **name** and its
model/pipeline/dataset triple; `platform-run` fills its **`task.yaml`** (neutral spec) and
renders it; `layout-workspace` says the launcher and `platforms/` profiles live at repo
top-level. Output dirs derive mechanically under `OUTPUT_DIR_HOME` (never the project dir).

## Companions
Every skill in the family should link back here. Non-family skills (`git-commit`,
`git-push`, `writing-style`, `claude-migrate`) are separate.
