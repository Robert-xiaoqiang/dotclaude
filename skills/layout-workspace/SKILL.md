# Skill: layout-workspace

## Purpose
Lay out a research project's **workspace** end to end — the *experiment-facing* half
(`config/` + `launcher/` + a single flat platform layer) and the *agent-facing* half
(`docs/` + session `scripts/`) — so both a config's purpose and a session's artifacts are
**predictable and recoverable**, not buried in a recipe script or a chat scratchpad. Keeps
this scaffolding distinct from source code, tests, and packaging. Config **names** follow
`naming-config`; the run-control layer follows `platform-run`; run **outputs** follow
`layout-output`. This skill is the map that ties launcher → config → project together.

## When to Use
- Standing up (or auditing) a config-driven training/eval/serving project.
- Deciding *where* something lives — a hyperparameter, a launcher, a plan, a one-off script.
- The user asks for a plan, report, or design walkthrough, or you generate a session script.
- Reviewing / tidying repo layout, or porting a project onto this paradigm.

## The layout
```
# ── Experiment-facing: config → launcher → platform (names per naming-config) ──
# config/ MIRRORS the implementation tree, one level deeper. Read a config path, predict the import
# path; read a module path, predict where its configs live. The mirror is the layout's core invariant.
<pkg>/
  config/                            # config lives INSIDE the package, so resolution never
    model/<model_name>.yaml          #   depends on the CWD and ships with an install
    pipeline/<pipeline_name>.yaml    #      ⟷  <pkg>/pipeline/<name>.py
    pipeline/reward/<reward_name>.yaml #    ⟷  <pkg>/pipeline/reward/<name>.py   (nested BECAUSE
    dataset/<dataset_name>.yaml      #          the code is nested: a reward belongs to the RL pipeline)
  model/  dataset/                   # the code each group's class_path points at
  pipeline/                          #   ...and pipeline/ owns reward/, which is why config does too
    reward/
  platform/                          # PURE-PYTHON translation: jobspec, profile, translate/<p>.py
  utils/config.py                    # the config system (group merge + run-dir derivation)
launcher/
  launch.sh                          # ONE shared in-pod entrance for EVERY pipeline (env → runner)
  <launcher-name>/task.yaml          # neutral run spec; run: is an argv LIST of k=v, no shell string
platform/                            # TOP-LEVEL, because it is on the critical path of "how a run
  <platform>.sh  _common.sh          #   starts" — thin native submit/status/logs + shared follow loop
  <platform>.yaml                    #   the profile: account / quota / image / data sources
README.md  pyproject.toml            # what this is + how to install it
# ── Agent-facing: docs + durable session scripts ──
docs/
  ARCH.md                            # single architecture reference (see docs-arch)
  plans/<YYYY-MM-DD>-<topic>.md       # timestamped task/design plans (see docs-plan)
  reports/<topic>.md | .html          # walkthroughs/figures that explain the system
scripts/
  README.md                          # what's here + the convention
  checks/                            # re-runnable verification/smoke scripts (committed)
  migration/  setup/                  # purpose subdirs; machine-specific ones git-ignored
```

**`scripts/` vs top-level: relevance, not file type.** `scripts/` is for work *incidental* to the
main workflow — run once, or run occasionally, and the project still trains without it (checks,
migrations, setup, probes). Anything on the critical path of starting a run is top-level and named for
what it is: `launcher/`, `platform/`. Burying the submit adapter in `scripts/` misfiles the entrance as
a chore. The *pure-python* half of the platform layer still lives in the package (`<pkg>/platform/`) so
it is importable and unit-testable without a shell — that is a language/role split of ONE layer, not a
second layer (see the anti-patterns).

## The config → launcher paradigm (the experiment-facing half)

### Design philosophy (why it is shaped this way)
The layout is not filing preference; each principle exists to make a class of mistake impossible.

1. **Config is data ABOUT code, and the two trees mirror.** `config/<group>/` sits opposite
   `<pkg>/<group>/`, one level deeper, at every depth. So a config path predicts an import path and a
   module path predicts where its configs live — and *nesting is inherited*: a reward's config nests
   under `config/pipeline/` precisely because the reward's code lives in `<pkg>/pipeline/reward/`. When
   you cannot decide where a new config belongs, the answer is wherever its implementation already is.
2. **Selection versus specification.** The config **specifies** (every knob, complete). The launcher
   **selects** (names, plus the few overrides that define *this* run). A launcher that starts
   specifying is a config wearing a disguise, and it will not appear in the run's frozen `config.yaml`.
3. **`class_path` is the only seam.** Config names code to build; it never encodes control flow. The
   moment a pipeline reads a config value to decide *which* branch to take (`if kind == "opd"`), the
   arm has leaked into the code and the config stops being a complete description of the run.
4. **Compose, never duplicate.** N arms are N configs in ONE group, not N copies of a pipeline config.
   The test is mechanical: if two configs differ in one field, that field is an axis and belongs in its
   own group (`naming-config`). Duplicates do not stay in sync — the first retune proves it.
5. **The merged config IS the run.** It is hashed into the run dir and frozen there. Anything that
   influences a run but is not in it — an env flag, a `mode=`, a hand-edited default — is invisible
   history, and two materially different runs become indistinguishable after the fact.

### What goes IN a config (the canonical shape)
Every group config is a single namespaced fragment keyed by its group, with the same four-part body:

```yaml
<group>:                 # the namespace == the group == the mount point in the merged tree
  name: <identity>       # THE SELECTOR. Unique across the group's dir; a duplicate is a hard error.
  class_path: a.b.C      # WHAT to build (a class or a factory function)
  init_kwargs: {...}     # HOW to build it — every ctor kwarg, explicitly (naming-config rule 2)
  <group-specific>       # knobs the pipeline reads directly rather than passing to a constructor
```

`name` + `class_path` + `init_kwargs` is the invariant; the fourth part is where groups differ.

| group | typically also carries | example |
|---|---|---|
| **model** | dtype/attention/precision, adapter or backbone selection, generation defaults for API models | `init_kwargs: {path, dtype: bfloat16, attn_implementation: sdpa, trust_remote_code}` · VMS: `init_kwargs: {base_url, model_path, generate_kwargs: {max_tokens, temperature}}` |
| **dataset** | **per-split** `init_kwargs` (train / validate / test), the metric set, the split's own subset caps | `train.init_kwargs: {files, max_samples, scaffold}` · VMS adds `test.metrics: [{class_path: ...ROUGEMetric, init_kwargs: {}}]` and `metric_key: rouge_l` |
| **pipeline** | the framework's config as ONE verbatim block, plus loop-level knobs | `trainer_kwargs: {...}` splatted into `GRPOConfig(**kwargs)` · VMS splits it: `accelerator_kwargs`, `data_loader_kwargs`, `adamw_kwargs: {lr, betas, weight_decay, eps}`, `fsdp_kwargs`, plus `num_epochs`, `num_warmup_steps`, `max_val_samples`, `resume_overall_step` |

### Owned components — the second level of the hierarchy
Not every swappable thing deserves a top-level group. Ask **who owns it**: a component that is
meaningless without a particular owner belongs *under* that owner, in all three of subdir, mount path,
and how it is selected.

| owner | component | why owned, not a peer | lives at · mounts at |
|---|---|---|---|
| **pipeline** | **reward** | only an RL trainer has one; an eval or SFT pipeline has none | `config/pipeline/reward/judge.yaml` · `pipeline.reward` |
| **pipeline** | **trainer / inferer engine** | the loop's execution strategy — a trainer subclass, or eval's generation engine; both are *how this pipeline runs*, not independent axes | `pipeline.trainer_class_path` + `trainer_kwargs` / `trainer_extra_kwargs` |
| **dataset** | **metrics** | a metric scores *this* dataset's outputs; another dataset has different ones, and a metric has no meaning detached from what it measures | `dataset.<split>.metrics: [{class_path, init_kwargs}]` (Visual-Memory-SFT) |
| **model** | **adapter / PEFT mixin, processor** | wraps or modifies a *specific* model class; a LoRA config without its base model describes nothing | `config/model/adapter/…` · `model.adapter`, `model.processor` |

**Selection follows ownership.** An owned component is named **by its owner's config**
(`pipeline: {reward: judge}`) and swapped through that same dotted path
(`pipeline.reward=judge_hygiene`). It never gets its own `<component>_name=` argument, because that
would re-assert at the CLI the independence the layout just denied — and it would let a run name a
reward for a pipeline that has no concept of one. Identity is resolved *before* field overrides land, so
`pipeline.reward=X` and `pipeline.reward.init_kwargs.k=v` compose rather than clobber.

The payoff is the same as for a top-level group: N arms are N small configs in ONE component directory,
sharing a single owner config, instead of N forked owners that drift apart on the first retune.

Two rules about the *framework* block specifically, because it is where configs rot:
- Pass it **verbatim** (`Trainer(**cfg.pipeline.trainer_kwargs)`). A hand-picked subset silently makes
  every unnamed field unreachable, and the run then trains on a default nobody chose.
- **Group it by concern**, VMS-style (`adamw_kwargs`, `data_loader_kwargs`, `fsdp_kwargs`), when the
  framework takes several distinct config objects; use one flat block when it takes one.

Swapping the trainer class is itself config — `trainer_class_path` plus `trainer_extra_kwargs` — so a
novel variant is a subclass named in YAML, never a fork of the assembly code.

### How the pieces compose
- `config/<group>/<name>.yaml` — the fragments above, merged into one tree by the config system.
- `launcher/<name>/task.yaml` — the platform-neutral spec (`platform-run`). Its `run:` is an argv
  **list** of `k=v`: the group names plus only the overrides that define this run. The launcher dir
  name mirrors the selected config names so the run's purpose is readable without opening it.
- `launcher/launch.sh` — the **one** shared entrance: env/venv/multinode, ask the config system for the
  run dir, tee the log into it, then hand every argument to the runner (`-m pkg.run "$@"`).

### Two runner styles — own the loop vs wrap a framework (get this right first)
The config→launcher shell is the same; what the config *points at* and how you *launch* differ by
whether you own the training loop or wrap an existing trainer. Decide this before building `config/`.

1. **Class-path harness — you own the loop.** Each config carries a `class_path`; a generic
   `<pkg>/pipeline/run.py` does `importlib.import_module(cfg.pipeline.class_path).main(cfg)`, and that
   pipeline instantiates `model.class_path(**init_kwargs)` + `dataset.class_path(**init_kwargs)` +
   `reward.class_path(**init_kwargs)` and runs. **Every group maps to real code** under
   `<pkg>/{model,pipeline,dataset,reward}/`. Launch with the distributed backend *you* drive —
   `accelerate` or `torchrun` (DDP/FSDP). (QDiffMDM, Visual-Memory-SFT, AutoRSI-on-TRL.)
   Note this style also applies when you use a *library* trainer (TRL's `GRPOTrainer`): you still own
   the loop's assembly, so the trainer class itself is just another `class_path`
   (`pipeline.trainer_class_path`) and its args are a verbatim `trainer_kwargs` block. A novel variant
   becomes a `GRPOTrainer` subclass named in config — never a fork of the build path.
2. **Framework-extension — you wrap a trainer (e.g. verl).** The config groups **override the wrapped
   framework's config** (its `ppo_trainer` base, merged via a hydra searchpath); your code plugs in
   through the framework's **hooks** — a reward-manager registry, `custom_reward_function.path`, a
   `data.custom_cls` dataset class. **Only the parts you own are code with a class_path;** the trainer
   owns model-building (an HF path → its own FSDP workers) and data-loading (parquet), so `config/model`
   and `config/dataset` are *config fragments, not class_path targets*, and there is **no** generic
   `run.py` dispatch — the framework is the pipeline. Launch with the **framework's own** mechanism:
   verl runs on **Ray**, so a plain `python -m <driver>` bootstraps the Ray cluster + actors — **NOT**
   torchrun/accelerate/DeepSpeed (those would fight verl's own worker management). A bare `python -m`
   is *correct here*, not a smell. (This is AutoRSI-on-verl.)

Litmus: if you can't point a `config/model` at a class you wrote, you're in style 2 — don't fabricate
empty `model/` wrapper modules for symmetry; put code only where you actually own it (the reward/method
= your "pipeline", a custom dataset class, a policy wrapper when you add one), and let the rest be
override fragments. Match the launch to the engine, not to a habit.

### Trainer pipelines PRODUCE a policy; eval pipelines CONSUME one

The two halves of a research loop share the same three top-level groups, and the direction of the
arrow is what tells you where an artifact belongs:

| | pipeline | model | dataset | produces | consumes |
|---|---|---|---|---|---|
| **trainer** | `grpo`, `coevolve`, `sft` | the INITIAL policy | train split | checkpoints | data |
| **eval** | `eval` | the TRAINED policy | val split / bench | scores | checkpoints |

**A checkpoint trained by a different trainer is a different MODEL.** That is the rule that decides
launcher identity, and it follows from `model` being top-level: it is orthogonal to every pipeline
precisely because training produces one and eval consumes one. So evaluating N arms is N launchers —
`eval__<model>__<dataset>` — each naming a different `config/model/<policy>.yaml` whose `path` pins the
checkpoint. The eval pipeline, dataset and decoding are byte-identical across them; only the policy
moves, and the launcher name says which.

The failure this prevents, seen in practice: passing the checkpoint as a submit-time override
(`--set pipeline.eval.checkpoint=...`) so that ONE launcher serves every arm. Six evals then appear on
the cluster under one name, indistinguishable in the console, **and** the policy's identity never
reaches the run's frozen `config.yaml` — the same "invisible history" a `mode=` flag creates. The tell
is a second home for something a group already owns: the policy path belongs to `model`, so an
eval-side `checkpoint:` field is a duplicate source of truth by construction.

What legitimately stays an override is a value the (pipeline, model, dataset) triple genuinely cannot
express — sweeping checkpoint STEPS *within* one arm, where all three are unchanged. Distinguish those
submissions at the PLATFORM layer (a job name derived from the overrides), never by inventing launcher
segments.

**Model-config provenance.** A trained-policy config records where weights came from, so its `path`
carries the training run's own config hash. Read one and you can find the run that produced it; that
is the model group doing the job `naming-config` gives its `backbone` slot — weights loaded from a
source are a user-visible event and the name says so.

#### The eval launcher name must correspond STRICTLY to the trainer launcher

An eval launcher sits **side by side** with the trainer that produced its policy, and the name says so
without opening either file:

```
train:   launcher/coevolve_evorubric__qwen3_4b__healthbench/     # {pipeline}__{model}__{dataset}
eval:    launcher/eval__qwen3_4b_coevolve_evorubric__healthbench/ # eval__{base}_{PIPELINE}__{dataset}
                          ^^^^^^^^^^^^^^^^^^ the trainer pipeline name, VERBATIM
```

**The trained-policy model name is `{base_model}_{trainer_pipeline_name}`, copied verbatim — never
abbreviated.** `qwen3_4b_coevolve_evorubric`, not `qwen3_evorubric_4b`. The compressed form reads
perfectly well, which is exactly why it is dangerous: `evorubric` matches no config in the repo, so the
link between an eval and the run it evaluates degrades into a coincidence of wording that a reader has
to reconstruct by guesswork. Verbatim means the name resolves mechanically — infix → pipeline config →
trainer launcher — and a check can enforce it. Two assertions worth having in CI: the infix IS a
pipeline config name, and `launcher/<infix>__<model>__<dataset>/` exists.

Note what does NOT get appended: a reward slot. If two arms share a pipeline and differ only in reward,
they are already two PIPELINE configs (`grpo`, `grpo_asymmetric_opd`) because reward is an owned
component the pipeline names — so the infix stays exactly one pipeline name in every case.

**What legitimately stays a CLI override**, because the (pipeline, model, dataset) triple genuinely
cannot express it: which checkpoint STEP of that one run to score — `final`, `best`, or a number. Same
trainer, same policy lineage, same eval; only the snapshot moves. Distinguish those submissions at the
platform layer (derive the job name from the override), never by minting launcher segments.

### Eval is a CHAINED call, and every model in the chain must be config

An eval pipeline usually runs more than one model: a **policy** generates and a **judge/grader** scores
(and an agentic pipeline may chain more). Only the policy is the top-level `model` group. The scorer is
an OWNED component of whatever does the scoring — `pipeline.reward.judge` for RL, `pipeline.eval.judge`
for eval — because a judge is meaningless detached from the thing it scores, exactly like a metric
detached from its dataset.

The rule that matters: **every model in the chain is named in config, none arrives from the
environment.** A judge configured only through `$JUDGE_BASE_URL` does not appear in the frozen
`config.yaml`, so two eval runs scored by different graders are indistinguishable on disk — and the
grader is not a detail, it *is* the metric. An env var may carry the endpoint (a pod IP changes every
relaunch and must not be frozen), but the judge's identity — model name, class_path, decoding — belongs
in the config.

### The THREE axes a run varies along — and why they are not one list

"sft, peft, rl, eval, ar, nar, mtp" reads like one menu of pipeline kinds. It is three axes wearing one
coat, and collapsing them is what produces a `config/pipeline/lora.yaml` sitting beside
`config/pipeline/eval.yaml` — two things that cannot be swapped for one another.

| axis | the question it answers | where it lives | values |
|---|---|---|---|
| **the LOOP** | what procedure is executing? | `pipeline` (top-level) | `sft`, `dpo`, `grpo`, `distill`, `eval`, `serve`, `agent` |
| **the POLICY'S FACTORIZATION** | how does the model define p(y\|x)? | `model.class_path` — the `model_class` slot | `ar` (causal LM), `nar` (mask-predict, CTC), `diffusion` |
| **the ADAPTATION** | which weights actually move? | `model.adapter` (owned by model) | full, `lora`, `qlora`, `ia3` |

**PEFT is not a pipeline.** LoRA is a way of adapting a model, and you can run SFT, DPO or GRPO with or
without it — so it is an owned component of `model`, and `sft` + `model.adapter=lora` is the run. Giving
PEFT its own pipeline forces a fork of the SFT loop that then drifts from it, which is the
near-duplicate anti-pattern in config form.

**Pipelines sort by their direction relative to the policy**, which is the generalisation of
trainer-produces / eval-consumes:

| direction | pipelines | reads | writes |
|---|---|---|---|
| **producer** | `sft`, `dpo`, `grpo` | data | checkpoints |
| **consumer** | `eval`, `serve`, `agent` | a checkpoint | scores / a service / trajectories |
| **both** | `distill` | a TEACHER checkpoint + data | a STUDENT checkpoint |

`distill` is the useful stress test: it consumes a policy and produces one, so it needs *two* model
slots. The teacher is not a second top-level `model` (a run has one policy under optimisation); it is an
owned component — `pipeline.teacher` — for the same reason a judge is. Anything that is a model but is
not the thing being optimised belongs to the pipeline that uses it.

### Is MTP a kind of NAR? No — they are answers to different questions

They look alike because both emit several tokens per forward pass, but that is a *decoding* property,
and it is not the axis `model_class` encodes:

| | factorization | tokens per forward | what it changes |
|---|---|---|---|
| **AR** | left-to-right, p(y_t \| y_<t) | 1 | — |
| **MTP** | **left-to-right, unchanged** | k, via auxiliary heads | an extra training objective + a decoding accelerator |
| **NAR** | **not left-to-right** (parallel / iterative refinement) | k | what the model IS |

MTP (DeepSeek-V3, Medusa) keeps the AR factorization on its primary head and adds heads predicting
t+2, t+3…, usually verified by the main head. NAR (mask-predict, CTC, diffusion LMs) removes the
sequential conditioning altogether.

So MTP is **AR + auxiliary heads**, not a species of NAR. Filing it under `nar` would put a training
objective and a decoding trick in the slot that names a *generative model class* — and then
`model_class` no longer predicts which code runs, which is the invariant the whole mirror depends on.
Place MTP as a model VARIANT AXIS (`qwen3_mtp4_4b` — four heads) plus whatever loss term the pipeline
adds, exactly as `naming-config` treats variant axes.

Litmus for any new word someone proposes: **does it change which code the run instantiates, or only
which values that code reads?** A new class → a `model_class` or a `pipeline`. A new setting → a
variant axis or an owned component. `nar` builds a different model; `mtp` adds heads to the same one;
`lora` wraps it; `grpo` is a different loop over it.

### Template: adding a new pipeline kind

```
1. Which direction is it?      producer / consumer / both   -> decides whether `model` is an
                                                               input, an output, or both
2. Code:    <pkg>/pipeline/<kind>/__init__.py   with main(cfg)
3. Config:  config/pipeline/<kind>.yaml         name + class_path + init_kwargs + loop knobs
4. Owned components: anything meaningless without this pipeline nests under it
                     (reward -> RL, judge -> eval, teacher -> distill, tools -> agent)
5. Launcher: launcher/<kind>__<model>__<dataset>/task.yaml   — names only, plus this run's overrides
6. Does it consume a policy? Then its `model` is a TRAINED-policy config whose name carries the
   trainer pipeline name verbatim, and its launcher sits side by side with that trainer's.
```

Nothing in that list is new machinery: a new pipeline kind is one module, one config, and a launcher.
If a proposed kind needs a new top-level directory or a launcher-only flag, it is being placed on the
wrong axis — re-run the litmus above.

### Future high-level pipelines (agent, serving) slot in the same way

A new top-level pipeline kind — `agent`, `serve` — is another `config/pipeline/<kind>.yaml` mirroring
`<pkg>/pipeline/<kind>/`, not a new top-level tree. It keeps the same three groups (an agent has a
policy, and it has data), and whatever is meaningless without it (a tool registry, an environment, a
judge) nests underneath as an owned component. The test is unchanged: orthogonal to every pipeline →
top-level group; meaningless without one owner → nested under that owner.

## Rules
- **Hyperparameters live in `config/`, never in a launcher or a recipe script.** The task.yaml
  `run:` and the shared entrance carry config **names** + env, plus at most the handful of overrides
  that define *this* run. If you see a wall of `key=value` overrides, the defaults belong in
  `config/{model,pipeline,dataset,reward}` and only the delta stays in the launcher.
- **The framework's config is passed VERBATIM, never whitelisted.** A group config carries a
  `*_kwargs` block splatted straight into the trainer's config object
  (`GRPOConfig(**cfg.pipeline.trainer_kwargs)`). The moment a `build_config()` hand-picks fields, every
  field it forgot becomes unreachable from YAML *and* CLI — and the run silently uses a default nobody
  chose. Dump the fully-resolved framework config into the run dir so the library defaults are on record.
- **A group's settings live under its group key.** No second top-level home for the same concern:
  eval settings go under `pipeline.eval`, not a free-floating `eval:`. One rule, no exceptions, so an
  override path is always predictable from the group name.
- **A group is top-level only if it is orthogonal to every pipeline.** `model` and `dataset` are
  (SFT, RL and eval all need them); a `reward` is not (only the RL trainer has one). An owned group
  nests — `config/pipeline/reward/`, mounting at `cfg.pipeline.reward` — while keeping its short
  selector. See `naming-config`.
- **The launcher passes ONLY config names and config overrides.** No `mode=`, no `--debug`, no
  launcher-only flags: they expand into config changes that never appear in the run's frozen
  `config.yaml`, so two materially different runs look identical on disk. A smoke run is a named
  dataset (`dataset_name=<...>_smoke`), not a mode.
- **The entrance derives the log path from the config chain, it does not choose one.** The shared
  entrance asks the config system for the run dir (a lightweight CLI that imports the config module
  only, never torch) and tees into it, so config + checkpoints + metrics + log are one directory. A
  `log:` field in a launcher spec is a smell: it is a second, hand-maintained source of truth for
  where a run lives.
- **One shared entrance, not one per launcher.** A single `launcher/launch.sh` (and
  `launcher/serve_launch.sh` for serving) serves every launcher; the per-launcher `task.yaml`
  is the *only* per-run file. Never scatter a `launch.sh` into each launcher dir.
- **One flat platform layer.** The run-control render + thin per-platform shell live in a single
  place (`platform-run`); do not split platform logic across a top-level dir *and* an in-package dir.
- **Plans** → `docs/plans/`, filename `YYYY-MM-DD-<topic>.md` (timestamp orders history).
- **Reports** (workflow/architecture walkthroughs, figures, HTML) → `docs/reports/`
  — not `docs/design/`.
- **Architecture doc** → a single `docs/ARCH.md`, kept current.
- **Session scripts** (checks, migrations, data munging, verification, setup) →
  `scripts/<purpose>/` as durable **checkpoints** — never leave them only in `/tmp`
  or a scratchpad. Header each script with **what · when · usage**.
- **Commit reusable scripts; git-ignore machine-specific/secret ones** (e.g. a
  `scripts/migration/` helper with hardcoded local paths).
- Name everything descriptively (companion: `naming-descriptive`) — never
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

## Anti-patterns (seen in real repos — do not copy)
- **Per-launcher `launch.sh` in every launcher dir** (a `launcher/<name>/launch.sh` beside each
  `task.yaml`). Redundant and drifts; collapse to one shared entrance and let the `task.yaml`
  carry the only per-run difference.
- **Hyperparameters inline** in the `run:` block or a `scripts/train_*.sh` recipe — the config
  masquerading as a script. Dissolve into `config/{model,pipeline,dataset,reward}`.
- **A whitelisting `build_config()`** that names a subset of the trainer's fields. Whatever it omits
  cannot be set from anywhere, and the failure is silent — the run trains on defaults and looks fine.
  (Cost of learning this: four arms × 12h, all flat, because `use_vllm` and `lr_scheduler_type` were
  unreachable.)
- **DUPLICATED platform logic** — two renderers, two snapshot helpers, two follow loops, or a second
  spec dialect. Note this is about duplicated *logic*, not about language: pure-python translation in
  `<pkg>/platform/` plus a thin native adapter in top-level `platform/` is ONE layer with two roles and
  is the intended shape (`platform-run`). Adding a platform must touch only a translator + a thin shell.
- **A pipeline config that duplicates another byte-for-byte except one flag.** That flag is a different
  *axis*: give it its own group (`reward/`, `dataset/`) and let the arms differ by which config they
  name. Otherwise every new arm forks the whole trainer config and they drift apart.
- **A hand-chosen `log:` path** in a launcher spec — see the rules; the run dir already knows.
- **`_v2` / `_baseline` / `_test` launcher or config names** — say what *differs* in a slot, not
  "this is the other one" (`naming-config`).
- **Empty or stale package dirs** left behind by a refactor (a `pkg/foo/` holding only `__pycache__`,
  a `scripts/oneoff/` with nothing in it). Git does not track empty dirs, so they survive a `git mv`
  invisibly and read as real structure to the next person. Sweep after every move.

## Not this skill
Run outputs (checkpoints, logs, metrics, eval) are a **separate** tree under
`$OUTPUT_DIR_HOME`, not the agent workspace. Their layout and their resume-vs-derived
classification live in `layout-output`. Never write run outputs into the project dir.

## Companions
`naming-config` (the slot grammar for config/launcher **names** — the paired skill for the
experiment-facing half) · `platform-run` (the flat run-control layer under `launcher/`) ·
`layout-output` (the run-output tree, the sibling `layout-` concern) · `docs-plan` (writes
`docs/plans/…`) · `docs-arch` (maintains `docs/ARCH.md`) · `naming-descriptive` (how to name) ·
`git-commit` (commit conventions).
