---
name: naming-config-launcher
description: "The launcher contract for config-driven runs: the launcher is a frozen TEMPLATE of the full standard run, and every variation — smoke, local probe, per-checkpoint grid cell, per-cluster fit — is a named config or a CLI overlay that lands in the run's frozen config, never an edit to the template and never a mode flag."
when_to_use: "Use when adding or invoking a launcher, when a smoke/local/probe/debug variant of a run is needed, when sweeping one field across a grid (checkpoints, seeds, scales), or when the temptation arises to copy a launcher and edit one line, add a mode= flag, or hand-patch a template for a one-off. Symptoms that should send you here: two launchers that differ by one field, a run whose behavior is not in its config.yaml, a _v2/_test launcher name."
---
# Skill: naming-config-launcher

## Purpose
A launcher is a **template**: the complete, standard, full-scale run, selected by name, with zero
inline variation. Everything that varies — a smoke, a local probe, one grid cell of a sweep, a
per-cluster resource fit — is expressed **at the invocation**, as a named config or a CLI overlay
that the config system merges last and freezes into the run's `config.yaml`. The template never
changes for a variant, and no variant exists outside a frozen config. This is the pattern that keeps
one launcher serving a 90-cell eval grid, a 4-rank local smoke, and a 16-rank production run without
a single copied file.

## Contents
- [When to Use](#when-to-use)
- [The two halves of the contract](#the-two-halves-of-the-contract)
- [The grid pattern](#the-grid-pattern)
- [Local and smoke invocations](#local-and-smoke-invocations)
- [The bundled grid scripts](#the-bundled-grid-scripts)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Creating a launcher, or reviewing one that has grown overrides in its `run:` list.
- Running a smoke, local, probe, or debug variant of an existing launcher.
- Sweeping one field over many values: checkpoints of an arm, seeds, model scales.
- Fitting one task to clusters that differ in silicon, storage, or memory.
- NOT for: naming the launcher (the slot grammar is `naming-config`'s), where the launcher lives
  (`layout-workspace`), or how the spec renders to a scheduler (`platform-run`).

## The two halves of the contract

**The template half** is the launcher directory's `task.yaml`: resources, env declarations, and a
`run:` list naming only group selectors (`pipeline_name=`, `model_name=`, `dataset_name=`) plus the
few overrides that define *this experiment* permanently. It is what a full-run submit uses verbatim,
with no CLI additions. If a token would only ever apply to some invocations, it does not belong here.

**The invocation half** carries every variation, in one of three forms, chosen by what varies:

| what varies | form | example | why this form |
|---|---|---|---|
| the corpus or scale of the run | a **named config** (the `tag` slot) | `dataset_name=rubric_mix_1k_smoke` | the variant is a first-class citizen with its own hashed run dir; a smoke result can never be mistaken for a real one |
| one field, per grid cell | a **CLI overlay** at submit | `--set model.init_kwargs.path=<ckpt>` | N auditable one-field jobs from one template; the override is frozen into each cell's own `config.yaml` |
| hardware fit, per cluster | a **conditional map** in the template's envs | `by_accelerator: {cuda: ..., ppu: ...}` resolved at submit; an env seam (`EXTRA_CONFIG_OVERRIDES`) when the fit is a config field | the value is a fact about what the cluster mounts or fits, not about the experiment — it stays declared, one template serves every cluster |

The merge order makes this safe: CLI last, over the named configs, over the defaults — so whatever
the invocation says is exactly what the frozen `config.yaml` records, and two runs that differ
materially can never look identical on disk.

## The grid pattern
A sweep is **one template plus a queue of one-field overlays**, never N launcher copies. The working
example: an arm's eval grid generates ONE eval launcher; a queue holds `(launcher, checkpoint-path)`
rows; a runner drains it with `--set model.init_kwargs.path=<ckpt>` per cell, under an admission
budget. Each cell hashes to its own run dir; the template is byte-identical across the grid, so a
retune touches one file. The queue, the dedup ledger, and the budget live OUTSIDE the launcher — a
template that knew about the sweep would stop being a template.

## Local and smoke invocations
A local run is the SAME shared entrance (`launcher/launch.sh`) invoked on the box with the smoke
dataset and fast-knob overlays on the command line — not a `_local` copy of the launcher and not a
`mode=` flag. The smoke's identity comes from its named dataset (`*_smoke`), so it gets its own run
dir; its speed comes from CLI overlays (`...max_steps=6`) that die with the invocation. When the
smoke goes green, the full submit uses the untouched template: nothing to un-patch, nothing to
forget, and the diff between what was smoked and what ships is precisely the overlay list.

**Commit what recurs, inline what doesn't.** `naming-config` teaches the committed `<arm>_smoke`
launcher; this file teaches the CLI-overlay smoke; both are right, at different repetition counts.
A standing pre-flight gate that many hands run before every submit is a committed variant launcher —
a TEMPLATE of the smoke run, whose file carries its overrides so no hand can mistype them. A one-off
probe, or a machine-generated grid cell, is an inline overlay that dies with the invocation. In both
forms every delta lands in the frozen `config.yaml`; the choice is only about who repeats the typing.
Two more committed-variant cases the taxonomy owns:
- **`resume`**: a committed variant whose overrides name the checkpoint chain — recurring by nature.
- **`_local` with a different CODE PATH** (e.g. `use_vllm=false` because the box lacks the engine):
  a genuinely different code path is a different config and earns a name. A `_local` that only
  shrinks numbers is the anti-pattern; where a run happens is a verb (`make run`), not a file.

## The bundled grid scripts
`/mnt/data/xqwang/.claude/skills/naming-config-launcher/scripts/` ships the grid machinery as a portable engine, extracted from a
working fleet and generalized the same way `platform-queue-shepherd` ships its shepherd: the engine
knows files and hooks, never a scheduler or a project.

| script | job | hooks it needs |
|---|---|---|
| `grid-enqueue.sh` | checkpoint ladder -> queue rows, with the provenance guard (a checkpoint with no `config.yaml` above it cannot be scored), the one-run-root refusal (two roots is two policies on one curve), and dedup against queue AND ledger | none — pure files |
| `grid-runner.sh` | drain the queue: budget hook admits, submit hook runs `<template> + --set <cell>` and prints a job id, the row MOVES to the ledger | `GRID_SUBMIT_CMD`, `GRID_BUDGET_CMD` |
| `grid-reconcile.sh` | self-healing: ledger rows whose jobs read Failed/Stopped return to the queue front; Succeeded stays as the done-record; unreadable status holds (never requeue on ignorance) | `GRID_STATUS_CMD` |

The move-to-ledger discipline is the load-bearing part: a runner that DELETES rows plus a scheduled
enqueuer that only dedups against the queue re-adds every submitted cell each pass and
double-submits the grid — measured before the ledger existed. All three state files live on shared
storage and every input is required, no defaults (`code-no-fallbacks`).

What stays in the PROJECT is the thin wrapper that generates the template itself — the eval
launcher's `task.yaml`, the per-arm model config, the policy-class mapping — because those name
project code. The wrapper calls (or mirrors) this engine; the engine never imports the project.

## Rules
1. **The template carries no invocation-specific tokens.** Every token in `run:` applies to every
   legitimate submit of that launcher, or it moves to the invocation.
2. **Every variation lands in the frozen `config.yaml`.** A variant expressed anywhere else — a mode
   flag, an env the config never sees, a hand-edit — makes two different runs indistinguishable on
   disk, which is how a toy result gets read as a real one.
3. **A smoke is a named config, never a flag.** The `tag` slot (`_smoke`, `_mini`, `_probe`) gives
   the variant its own hashed run dir; `mode=smoke` gives it a disguise.
4. **A grid is one template plus per-cell overlays**, with the cell list held outside the launcher
   (a queue, a manifest), never N near-copies of the launcher.
5. **Cluster-dependent values are declared maps, not submit-shell memory.** A value that depends on
   which cluster runs the job (`venv`, storage root, endpoints path, a memory fraction) lives in the
   template as a conditional map, so a resubmit by any hand renders correctly.
6. **Two launchers differing by one field are one launcher and an axis** — promote the field to a
   named config or an overlay (`naming-config` rule: near-duplicates drift on the first retune).
7. **The smoked code path is the shipped code path.** The smoke varies data and knobs via overlays;
   it must not take a different branch, or green means nothing.

## Anti-patterns
- **The `_local`/`_test` launcher copy.** Feels quick; now the retune edits two files and they have
  already drifted. The local run is the same entrance plus overlays.
- **The mode flag.** `mode=smoke` rewrites fields invisibly; the run dir cannot tell you it happened.
- **The patched template.** Hand-editing `task.yaml` for a one-off and meaning to revert it — the
  next submit ships the patch. Overlays die with the invocation; edits do not.
- **The launcher that knows the sweep.** A template with a checkpoint list baked in must be edited
  every time the grid grows; the queue outside the launcher grows for free.
- **The submit-shell env as configuration.** A value that must be exported just-so before `make job`
  is one forgotten export away from a wrong run; declare it in the template's env maps.

## Companions
`naming-config` (the slot grammar for the names of templates, tags, and groups — including that the
launcher name alone states what runs) · `layout-workspace` (selection-vs-specification, where the
launcher lives, and `references/overrides.md` for classifying a long submit line) · `platform-run`
(how the template renders and submits to a scheduler) · `naming-config-prompting` (the sibling
deep-dive: the same frozen-template-plus-overlay doctrine applied to prompt text) ·
`code-no-fallbacks` (why a required invocation value fails loudly instead of defaulting).
