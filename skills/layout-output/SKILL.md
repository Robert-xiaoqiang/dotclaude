---
name: layout-output
description: "Define the run-output tree under $OUTPUT_DIR_HOME where runs write checkpoints, logs, metrics, samples and eval results, and classify what is resume state versus deliverable versus junk."
when_to_use: "Use when deciding where a run writes its outputs, reviewing a launcher's output path, or before comparing runs or reclaiming space."
---
# Skill: layout-output

## Purpose
Define the **run-output tree** where training and eval runs write their checkpoints,
logs, metrics, samples, and eval results. This is a third organization, separate from
the project source tree and the agent-facing workspace, and it lives under
`$OUTPUT_DIR_HOME` (never inside the project dir). This skill fixes the schema and,
more importantly, the classification of every artifact into *resumable state*,
*deliverable*, or *derived / junk*. Two downstream skills read this schema, `output-analysis`
locates and compares runs, and `output-cleanup` decides what is safe to delete.

## When to Use
- Deciding where a run should write its outputs, or reviewing a launcher's output path.
- Before comparing runs (`output-analysis`) or reclaiming space (`output-cleanup`), to know
  what each file means and what must survive.
- Onboarding a new project, so runs land in a predictable, tool-agnostic shape.

## Three trees, kept distinct
A project spans three locations with different owners and lifetimes. Confusing them is
the root of both lost results and unsafe deletes.

| tree | root | holds | owner / lifetime |
|---|---|---|---|
| **source** | `$PROJECTS_HOME/<repo>` | code, configs, launchers | git, versioned |
| **agent workspace** | `<repo>/docs/`, `<repo>/scripts/` | plans, reports, re-runnable scripts (`layout-workspace`) | committed with the repo |
| **run output** | `$OUTPUT_DIR_HOME/...` | checkpoints, logs, metrics, eval | produced by runs, this skill |

`$OUTPUT_DIR_HOME` is `$CPFS_HOME/output_dir` from `env.sh`. Outputs never go inside the
project dir. `naming-config` rule 6 makes the run path mechanical, so a run's identity is
readable from its path and no user invents a per-run directory.

## The run path (from naming-config)
```
$OUTPUT_DIR_HOME/<project>/<group.name>/.../<hash>/     # one segment per config GROUP, fixed order
e.g. .../autorsi/grpo/qwen3_4b/healthbench/judge/09ab18d5/
```
One path segment per config group the project defines, in a fixed order (pipeline, model, dataset,
then any further axes such as `reward`), then the hash. Everything up to and including `<hash>` is one
**run dir**. The `<hash>` is `md5(merged config)[:8]` over the **resolved** config, so a run overridden
on the command line disambiguates itself instead of overwriting the run it came from. Sibling runs
sharing a prefix are the natural comparison set, and the arms of an ablation differ only in the slots
that name the change (`naming-config` symmetry rule).

**The run dir is derived, never chosen.** The launcher asks the config system for this path (a
lightweight CLI that imports the config module only) and writes its own log inside it. A launcher spec
that carries its own `log:`/`output:` path is a second source of truth and will drift.

## The reference run layout
A tool-agnostic schema most frameworks (HF Trainer, Lightning, DeepSpeed, a custom loop)
can be shaped to. Names vary per project, so match by role, not by exact spelling.
```
<run>/
  config.yaml                     # resolved, frozen config: the run's identity
  trainer_config.json             # the framework config as ACTUALLY resolved, incl. library defaults
  launch.rank<N>.log              # the entrance's own log, written INSIDE the run it launched
  checkpoints/
    step_0000500/ ... step_0004000/   # step-tagged checkpoints (weights + optimizer + RNG + scheduler)
    best  -> step_0003000              # symlink: best-by-metric
    last  -> step_0004000              # symlink: latest, the resume point
  metrics.jsonl                   # append-only scalar history, one record per logged step
  logs/  train.log stdout stderr  # human/text logs
  events.out.tfevents.*           # tensorboard scalars (mirror of metrics)
  wandb/  run-<id>/               # or a resume-id file
  samples/                        # generations produced during training
  eval/
    <benchmark>/
      summary.json                # benchmark-level metrics: the eval keeper
      predictions.jsonl           # per-instance outputs
      per_instance/               # bulky per-instance dumps
  DONE                            # optional terminal marker written when the run finishes
```

## Artifact classification (the crux)
Every file falls into one of four classes. The class, not the filename, decides whether
`output-cleanup` may touch it.

- **Identity** (always keep, tiny). `config.yaml` and `trainer_config.json`. They name the run and are
  needed to interpret every other file; deleting them orphans the whole dir. `config.yaml` is what you
  *asked for*, `trainer_config.json` is what the framework *resolved* — keep both, because the gap
  between them (fields left at a library default nobody chose) is exactly where silent misconfiguration
  hides, and it is not reproducible later from a different library version.
- **Resume state** (keep while a run is unfinished). The `last` checkpoint target with its
  optimizer, scheduler, and RNG state, plus the wandb resume id, plus a partially written
  `eval/<bench>/predictions.jsonl` for an eval still in progress. Losing this forces a
  restart from zero.
- **Deliverable** (keep, it is the result). The `best` checkpoint target and each
  `eval/<bench>/summary.json`, plus final `samples/` the user cares about.
- **Derived / junk** (reclaimable, with confirmation). Text `logs/`, `events.out.tfevents.*`
  once metrics are archived, intermediate checkpoints strictly between the first and the
  kept set, `per_instance/` of a *completed* eval, scratch `samples/`, `*.tmp`, and
  half-written or zero-size checkpoints missing their marker files.

The `metrics.jsonl` is the analysis anchor. Keep it. It is small and it is what
`output-analysis` reads for the longitude axis, and it lets you drop the far larger tfevents
without losing the curves.

## Run kinds (how to tell them apart)
- **Smoke / toy / debug.** A `_smoke` / `_toy` / `debug` tag in the launcher name
  (`naming-config` dataset `tag` slot), a tiny step count, few files, no `best`. Short-lived
  by intent.
- **Intermediate.** A real run superseded by a newer sibling under the same
  `<pipeline>/<model>/<dataset>` prefix. Often kept only for its `best` or discarded once
  the successor lands.
- **Keeper.** Finished (a `DONE` marker or a `best` at the target step) or the current
  best-in-class for its triple. Never deleted without an explicit, per-item instruction.

## Discovery (robust to path variation)
Both downstream skills find runs the same way, so exact paths never need to be hardcoded.
1. Walk `$OUTPUT_DIR_HOME` for the schema signature (a dir containing `config.yaml`, or
   `checkpoints/` plus `metrics.jsonl`). That set is the runs.
2. Read each `config.yaml` to recover pipeline / model / dataset and group siblings.
3. Sort and filter by mtime when the instruction is fuzzy ("the recent runs", "last night's
   debug runs"). Editing time on the newest checkpoint is a good proxy for run activity.

## Rules
1. Outputs live under `$OUTPUT_DIR_HOME`, never inside the project or `datasets` dir.
2. The run path is mechanical (`naming-config` rule 6). Do not invent per-run paths.
3. Keep a small `metrics.jsonl` (or equivalent) so curves survive even if tfevents is dropped.
4. Write a terminal marker (`DONE`) when a run finishes, so finished-vs-resumable is a file
   check, not a guess.
5. Classify before acting. Read a file's class from this skill, not from its name.

## Companions
`naming-config` (the run path + the launcher triple) · `layout-workspace` (the agent
workspace tree, the sibling `layout-` concern) · `platform-runtime` (the driver/image/venv/storage
stack a run executes on) · `output-analysis` (compares runs in this tree) · `output-cleanup`
(safely reclaims this tree) · `conventions` (the family index).
