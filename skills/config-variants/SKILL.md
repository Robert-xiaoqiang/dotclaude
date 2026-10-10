---
name: config-variants
description: "How a config-driven run varies from its launcher. The launcher is a committed template of one standard run, and each variation of it (a smoke, a local probe, a resume, one cell of a checkpoint grid) is a CLI overlay, a committed child config, a group axis or a committed variant launcher, chosen by whether it recurs, frozen into the run's config.yaml, never an edit to the template and never a mode flag. Bundles the checkpoint-grid engine."
when_to_use: "Use when a smoke, local, probe, debug or resume variant of a run is needed, when sweeping one field across a grid (checkpoints, seeds, scales), when deciding how many overrides a launcher's run: list may carry or where a tracing toggle is switched on, or when tempted to copy a launcher and edit one line, add a mode= flag, or hand-patch a template for a one-off. Symptoms: two launchers or configs that differ by one field, a run whose behavior is not in its config.yaml, a run: list grown into a wall of a.b.c=value. Not for what a launcher or variant is called (naming-config), how configs merge and freeze (config-composition), or env values that differ by cluster (platform-run)."
---
# Skill: config-variants

## Purpose
A launcher is a committed template of one standard run. Its `run:` list selects the run by name and
carries only what is true of every submit of it. Each variation of that run (a smoke, a local probe,
a resume, one cell of a grid) takes one of four forms, chosen by whether it recurs, and lands in the
run's frozen `config.yaml` like any other value. This is how one launcher serves a 90-cell eval grid,
a 4-rank local smoke and a 16-rank production run without a copied file.

## Contents
- [When to Use](#when-to-use)
- [Nothing else is a launcher argument](#nothing-else-is-a-launcher-argument)
- [What a launcher carries](#what-a-launcher-carries)
- [How a variation is represented](#how-a-variation-is-represented)
- [Commit what recurs, inline what does not](#commit-what-recurs-inline-what-does-not)
- [Instrumentation toggles](#instrumentation-toggles)
- [The grid pattern](#the-grid-pattern)
- [The bundled grid scripts](#the-bundled-grid-scripts)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Reviewing a launcher whose `run:` list has grown overrides, or deciding how many it may carry.
- Running a smoke, local, probe, debug or resume variant of an existing launcher.
- Sweeping one field over many values: checkpoints of an arm, seeds, model scales.
- Two configs or launchers that differ in one field, or a tracing toggle someone wants switched on.
- NOT for: what a launcher, a child config or a `tag` variant is called (`naming-config`), how
  selectors and overrides merge into the frozen config (`config-composition`), where the launcher
  lives (`layout-workspace`), or how the spec renders and which env values differ by cluster
  (`platform-run`).

## Nothing else is a launcher argument

Every token a launcher passes, in its `run:` list or at the invocation, is a `<group>_name=` selector
(it picks a group config by name) or an `a.b.c=value` override (it sets one field of the merged
config). **There are no launcher-only flags.** A `mode=smoke` that quietly rewrites three trainer
fields and redirects the output root is a config masquerading as a flag. It never reaches the run's
frozen `config.yaml`, so two runs that differ by it look identical on disk, which is how a toy result
gets read as a real one. The same holds for `--debug`, and for a `prompt_mode=` that picks prompt
text (`config-prompting`). AutoRSI's smoke dataset replaced exactly such a flag. Its entrance,
`launcher/launch.sh`, hands every argument to the runner untouched and reads `pipeline_name=` back
only for its log line, so nothing it receives can diverge from what the config system sees. How
selectors and overrides merge, argv last, into the one config that is the run belongs to
`config-composition`.

## What a launcher carries

The launcher directory's `task.yaml` is the template: resources, env declarations, and a `run:` list.
What that list may carry depends on the kind of run the launcher is.

| launcher kind | its `run:` list | why |
|---|---|---|
| **full run** (the result) | the group selectors plus, when needed, the few overrides that define that experiment permanently | a reader recovers the recipe from the config names and a short list that holds for every submit |
| **committed variant** (a standing smoke gate, a resume) | as many overrides as it needs, written in the file | many hands rerun it, so no hand may retype it |
| **`_local`** | the override for the code path the box forces, and the launcher exists only then | otherwise local is a verb ([Local](#local)) |

*Worked example.* AutoRSI's `rl_grpo__qwen3_4b__rubric_mix_1k` passes three selectors and four
trainer overrides. `num_train_epochs=5` sets the 1k corpus's budget, since the family base's 1.75
epochs is the 10k production choice. `save_steps=15`, `eval_strategy=steps` and `eval_steps=15` set
the half-epoch checkpoint grid every arm shares for paired eval. All four hold for every submit of
that launcher, so they belong to it. Most other full runs pass three selectors and nothing else.

**Anything that varies per invocation stays out of the template** (Rule 1). Three tests keep the
experiment-defining list short.
- **The same override in every launcher of a group is that group's missing default.** AutoRSI's
  dynamics arms carried one four-line training protocol in 26 identical `run:` blocks until
  2026-08-31, when it moved into `rl_grpo_harness_dynamics.yaml`. Every arm's merged config, and so
  its hash and run dir, came out unchanged, which kept the live checkpoints resumable across the move.
- **An override that holds the recipe across a world size states its arithmetic.** Prompts per
  gradient is per-device batch x world size x accumulation / generations, where world size is the
  spec's total, `num_nodes` x `accelerators` (`platform-run`). A launcher whose total differs from
  its siblings' therefore changes the recipe unless an override holds it. AutoRSI's 32-rank dynamics
  arms, beside siblings that run 16, pass `gradient_accumulation_steps=4` for this, with the
  arithmetic written in the launcher beside the fields that set the total, and the override belongs
  to the launcher because that total holds for every submit. Check the product in the frozen
  `config.yaml`, never in the base file, since a later link of the config chain can override both
  factors. When the larger world buys nothing, return to the siblings' total and drop the override
  with it. A scaffold arm that needed `grad_accum: 2` at 16 ranks ended at its siblings' 8 and zero
  overrides.
- **An override that changes the method belongs in a child config.** If it makes the arm differ
  from its siblings by more than its name says, it is a recipe, and the child config is named for
  that difference.

Read when a launcher's `run:` grew a wall of `a.b.c=value`:
[references/overrides.md](references/overrides.md). It sorts each token into redundant, missing
default, per-run delta or selector before anything moves, because two of the four are correct where
they stand.

## How a variation is represented

Two configs or launchers that differ in one field are one run and one variation of it, never two
copies, because the first retune edits one copy and the pair drifts in silence. A variation takes one
of four forms.

| form | use it when | example |
|---|---|---|
| **CLI overlay** at submit (`--set a.b.c=value`, `SET_ARGS=` through `make`) | the value changes per invocation, as in a one-off probe or a machine-generated grid cell | `--set model.init_kwargs.path=<ckpt>` per cell of an eval grid |
| **committed child config** (`_base_:` plus the delta, or a named config in the `tag` slot) | the variation recurs and changes what one group holds | AutoRSI `rl_grpo_harness_dynamics_profile.yaml` (`_base_: rl_grpo_harness_dynamics` plus the profile protocol), `dataset/healthbench_smoke.yaml` |
| **group axis** (a nested group, selected by name) | several arms pick among values of one independent component | MemCodex `memory.routing.budget=b16k`, one budget per cell of a sweep run from one template |
| **committed variant launcher** | a standing gate many hands run, a resume, a code path the box forces | AutoRSI `rl_grpo__qwen3_4b__healthbench_smoke` |

The overlay dies with the invocation and the other three are files. Which one a variation takes is
[Commit what recurs, inline what does not](#commit-what-recurs-inline-what-does-not), and every form
lands in the frozen `config.yaml`. What each file is called, the `tag` slot included, is
`naming-config`'s.

**A value that differs by cluster is a fact about the cluster, not a variation of the experiment.** An
env value that differs by silicon, today the venv name, is a `by_accelerator` env map in the
template, which skylaunch resolves at submit for DLC and local runs. `platform-run` owns the map, and
the DSW gap with it. A
config field that differs by cluster is a named config for that cluster, a committed child like any
other. AutoRSI once word-split an `EXTRA_CONFIG_OVERRIDES` env into the entrance's argv so a
`by_accelerator` map could bend trainer fields per silicon. It removed that seam on 2026-08-31,
because an env that can rewrite a config field is a second, invisible launcher, and its one real user,
an a100 engine-slice tweak, belonged in a named config for the cluster that needed it.

## Commit what recurs, inline what does not

Whether a variation is typed at the command line or committed to a file depends on how often it is
repeated, not on what it is. A standing pre-flight gate that many hands run before every submit is a
committed variant launcher, a template of the smoke run whose file carries its overrides so no hand
can mistype them. A one-off probe, or a machine-generated grid cell, is an inline overlay that dies
with the invocation. Either way every delta lands in the frozen `config.yaml`, so the choice is only
about who repeats the typing. The full-run template is never edited for either. When a variant goes
green, the full submit uses the untouched template, and the diff between what was smoked and what
ships is exactly the variant's override list.

### Smoke

A smoke is a named config with its own hashed run dir. Its identity is a named dataset in the `tag`
slot (`dataset_name=healthbench_smoke`, a 64-sample subset), so a smoke result can never be mistaken
for a real one. Its speed is a short schedule passed as overrides, committed in the smoke launcher
when the smoke is a standing gate and typed at the command line when it is a one-off. AutoRSI's
`rl_grpo__qwen3_4b__healthbench_smoke` is the committed form. It carries the smoke dataset,
`max_steps=120`, verdict tracing, and `report_to=[tensorboard]` so a toy-scale run never lands on the
dashboard beside the arms it would be read against.

The subset is a config because it changes what is measured. The schedule stays an override because
it changes only how long, and because a config schedule forces a second coordinated selection. A
smoke spans two groups, small data in `dataset` and a short schedule in `pipeline`, so a fully-config
smoke selects `pipeline_name=..._smoke` and `dataset_name=..._smoke` together. They can desync, and
the dangerous direction is silent: the full pipeline on the smoke dataset is a full-length run on 64
examples that reads as real. A fully-config smoke is still legitimate with one check, that a `_smoke`
pipeline pairs only with a `_smoke` dataset. With the check config wins, and without it overrides are
safer. AutoRSI's `_profile` cell takes the fully-config form, a `_profile` pipeline child selected
with the `rubric_mix_1k_profile` dataset, and has no such check yet.

### Resume

A resume is a committed variant whose overrides name the checkpoint chain, recurring by nature.

### Local

A local run is a probe, not a launcher, because where a run happens is a verb, not a file. The same
template runs on the box through the local platform family, with the smoke dataset and fast-knob
overlays (`platform-run` owns the local mechanics). A second file for "the same run, on my box"
duplicates a launcher to change nothing a launcher owns.

A local probe does not clear the smoke gate. It answers whether the path executes, and the recipe
moves with the card count. 8 x 4 x 4 / 8 = 16 prompts per gradient on 8 GPUs, the full run's figure,
but 4 on 2 GPUs and 2 on one. In AutoRSI world size is not config either, so a local run of a
template hashes to the same run dir as its cluster run, and since `rl_grpo` resumes by default it
picks up that run's checkpoint unless an overlay, the smoke dataset for one, sets it apart.

Write `<arm>_local` only when the box forces a different code path, not a smaller number. A card with
too little free memory cannot hold the policy and a colocated vLLM engine together, so local needs
`use_vllm=false`. That is HF generate, a different generation path rather than a knob, so it is a
named variant and earns its file. Fewer GPUs does not.

## Instrumentation toggles

An instrumentation or tracing toggle lives in the owning component's config with its value written
out. A committed smoke launcher may switch it on. A full-run launcher never does,
because then whether an arm was traced depends on whether its launcher remembered. When the analysis
of every arm reads what the instrument records, the config turns it on for every arm. AutoRSI's
`trace_verdicts` is the case. It was a constructor default that five launchers switched on by hand,
and the arms that forgot produced 1080 state-matrix snapshots and zero readable cases, on the one arm
every claim is compared against. It now sits, written out and on, in the reward configs under
`config/pipeline/rl/reward/`, and only the two `healthbench_smoke` launchers still pass it. Why an
instrument never appears in a name is `naming-config`'s.

## The grid pattern
A sweep is **one template plus a queue of one-field overlays**, never N launcher copies. The working
example: an arm's eval grid generates ONE eval launcher; a queue holds `(launcher, checkpoint-path)`
rows; a runner drains it with `--set model.init_kwargs.path=<ckpt>` per cell, under an admission
budget. Each cell hashes to its own run dir; the template is byte-identical across the grid, so a
retune touches one file. The queue, the dedup ledger, and the budget live OUTSIDE the launcher — a
template that knew about the sweep would stop being a template.

**The checkpoint is always an overlay, however often it appears.** Every cell of an eval grid
passes `model.init_kwargs.path`, so the count test in
[references/overrides.md](references/overrides.md) would call it a missing default. It is not. It
names an instance rather than a choice, and a config per checkpoint step would be a file per artifact
rather than per decision. Name each cell's job from its overlay (the checkpoint step), so the
scheduler's listing tells the cells apart, and never mint a launcher per checkpoint. The bundled
runner does not derive that name yet, so the submit hook must.

## The bundled grid scripts
`${CLAUDE_SKILL_DIR}/scripts/` ships the grid machinery as a portable engine, extracted from a
working fleet and generalized so that the engine knows files and hooks, never a scheduler or a
project.

| script | job | hooks it needs |
|---|---|---|
| `grid-enqueue.sh` | checkpoint ladder -> queue rows, with the provenance guard (a checkpoint with no `config.yaml` above it cannot be scored), the one-run-root refusal (two roots is two policies on one curve), and dedup against queue AND ledger | none — pure files |
| `grid-runner.sh` | drain the queue: budget hook admits, submit hook runs `<template> + --set <cell>` and prints a job id, the row MOVES to the ledger | `GRID_SUBMIT_CMD`, `GRID_BUDGET_CMD` |
| `grid-reconcile.sh` | self-healing: ledger rows whose jobs read Failed/Stopped return to the queue front; Succeeded stays as the done-record; unreadable status holds (never requeue on ignorance) | `GRID_STATUS_CMD` |

The move-to-ledger discipline is the load-bearing part: a runner that DELETES rows plus a scheduled
enqueuer that only dedups against the queue re-adds every submitted cell each pass and
double-submits the grid — measured before the ledger existed. All three state files live on shared
storage and every input is required, no defaults (`code-no-fallbacks`). Two known defects remain in
`grid-runner.sh`. It still defaults `GRID_TICK_SECS` to 180, and it takes the last token of eight or
more characters in the submit hook's output as the job id, so the hook must print the id last.

What stays in the PROJECT is the thin wrapper that generates the template itself — the eval
launcher's `task.yaml`, the per-arm model config, the policy-class mapping — because those name
project code. The wrapper calls (or mirrors) this engine; the engine never imports the project.

## Rules
1. **The template carries no invocation-specific tokens.** A full run's `run:` list is its selectors
   plus, when needed, the few overrides that define that experiment permanently.
2. **Every variation lands in the frozen `config.yaml`** as a selector or an override, because the
   merged config is the run (`config-composition`).
3. **A smoke is a named config in the `tag` slot**, with its own hashed run dir.
4. **A grid is one template plus per-cell overlays**, with the cell list held outside the launcher
   (a queue, a manifest), never N near-copies of the launcher.
5. **A value that differs by cluster belongs to the cluster.** A config field is a named config for
   that cluster. An env value that differs by silicon is a `by_accelerator` map, which today carries
   the venv name and which `platform-run` owns. An endpoint is a plain env and never enters the map.
6. **Two launchers differing by one field are one launcher and one variation**, in one of the four
   forms of [How a variation is represented](#how-a-variation-is-represented).
7. **The smoked code path is the shipped code path.** The smoke varies data and knobs via overlays;
   it must not take a different branch, or green means nothing.
8. **No launcher-only flags.** Every token is a `<group>_name=` selector or an `a.b.c=value`
   override.
9. **Commit what recurs, inline what does not.**
10. **An instrumentation toggle lives in its owner's config.** A committed smoke launcher may switch
    it on, a full-run launcher never does.
11. **A grid cell's job is named from its overlay**, never from a launcher minted per checkpoint.

## Anti-patterns
- **The `_local` copy that only shrinks numbers.** It feels quick, and now a retune edits two files
  that have already drifted. A local run is the same template plus overlays. The exception is a code
  path the box forces, such as `use_vllm=false`, which earns a named variant.
- **The patched template.** Hand-editing `task.yaml` for a one-off and meaning to revert it — the
  next submit ships the patch. Overlays die with the invocation; edits do not.
- **The launcher that knows the sweep.** A template with a checkpoint list baked in must be edited
  every time the grid grows; the queue outside the launcher grows for free.
- **The env that silently changes the run.** An override env that the entrance word-splits into argv
  is a second, invisible launcher. Neither the template nor the submit command shows the variation,
  and a stale export in the submitting shell carries it into the next run unasked. A variation takes
  one of the four forms of [How a variation is represented](#how-a-variation-is-represented). What
  may come from the environment at all is `config-composition`'s env rule, under which only an
  endpoint may.

## Companions
`naming-config` (what a launcher, a child config and a `tag` variant are called, and why an
instrument is never a name segment) · `config-composition` (how selectors and overrides merge, argv
last, into the frozen config that is the run) · `layout-workspace` (where the launcher and its
configs live) · `platform-run` (how the template renders and submits, the local family, and
`by_accelerator` env maps) · `config-prompting` (prompt text varied the same way, `prompt_mode=`
included) · `code-abstraction` (callers never branch on a variant, which keeps the smoked path the
shipped one) · `code-no-fallbacks` (why a required invocation value fails loudly instead of
defaulting) · `conventions` (the family index).
