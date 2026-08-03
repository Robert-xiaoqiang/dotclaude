# Skill: naming-config

## Purpose
Apply a consistent naming convention across **model**, **pipeline**,
**dataset**, and **launcher** configs in any LLM / agent / research
codebase that uses a config-driven runner (OmegaConf, Hydra, Pydantic
configs, YAML registries, etc.). Keeps file names, class paths, and
output dirs aligned so a config name uniquely identifies what runs.

## When to Use
- Adding a new model variant, pipeline stage, dataset, or launcher
- Renaming an existing config (refactor)
- Reviewing PRs that introduce new config files
- The user says: "what should I name this config?", "is this naming
  consistent?", "build a launcher for ..."

## Core principle
Each config file's name is a **slot grammar string** of the same
slots that describe the corresponding code path. Read the file name,
predict the class / module / behavior. Read the class / module name,
predict the config file name. Two configs that differ in one knob must
differ in exactly that one slot.

## Slot grammars

### Model configs

```
{model_class}[_{variant_axes...}][_{backbone}]_{scale}[_{specialty_tag}]
```

* `model_class` matches the file name in `<package>/model/` and is
  the **subdir** under `<package>/config/model/`. e.g. `mdm`, `lora_mdm`,
  `quantum_lora_mdm`.
* `variant_axes` are class-specific knobs that go into the file name
  *only when set non-trivially* (e.g. quantum injection position /
  strategy / readout). Order them outer→inner.
* `backbone` appears only when weights are loaded from a pretrained
  source (e.g. `smdm`, `llama3`). Omit for from-scratch.
* `scale` matches the model-config registry key (`180m`, `1028m`, `8b`).
* `specialty_tag` for orthogonal axes that don't fit the above
  (e.g. qubit count `8q`/`16q`, expert count `8e`).

### Pipeline configs

```
{stage}_{flavour}
```

* `stage` ∈ `{pretrain, sft, eval, dpo, rl, ...}`.
* `flavour` matches the model-class family (`ar`, `mdm`, `quantum_mdm`,
  `lora_mdm`).
* Reuse Python pipelines via `class_path` — many configs can share one
  pipeline with one boolean flag (e.g. `optimize_trainable_only` to flip
  full-fine-tune vs LoRA-only).

### Dataset configs

```
{method}_{source}[_{tag}]
```

* `method` is the loader (`local_packed`, `hf_streaming`, `sharegpt`).
* `source` is the corpus name (`slimpajama`, `ultrachat`, `c4`).
* `tag` for `toy` / `smoke` / `mini` subsets used for fast iteration.

### Groups beyond the three — and where a new group BELONGS

A group is *an axis a run selects by name*. When experiments systematically vary something the three
canonical groups can't express, give it a group rather than a flag inside another group. The test:
**would two arms otherwise share a byte-for-byte config differing in one field?** If yes, it is an axis.

But answer a second question before making it a top-level peer:

> **Is it orthogonal to every pipeline, or owned by one?**

`model` and `dataset` are orthogonal — an SFT run, an RL run and an eval run all need a policy and data.
A `reward` is not: only an RL trainer has one, and an eval pipeline has none. Placing it side by side
with model/dataset asserts an orthogonality that does not hold, and the config tree then lies about the
domain. So a group carries **two** placements, and both mean something:

| | encodes | orthogonal axis | owned component |
|---|---|---|---|
| **subdir** | ownership | `config/<group>/` | `config/<owner>/<group>/` |
| **mount path** | scope — where it LIVES | `cfg.<group>` | `cfg.<owner>.<group>` |
| **payload mount** | reach — where it APPLIES | usually the same | may be another subtree |

**Ownership chains, so `<owner>` may itself be owned.** An agent owns a model and a tool set while
being owned by the pipeline that runs it, giving `config/pipeline/agent/model/` mounting at
`cfg.pipeline.agent.model`. There is no depth limit and no judgement call: the config tree mirrors the
code tree at every level, so the nesting is whatever the implementation already does
(`layout-workspace`).

**A run has exactly one SUBJECT: the thing it optimises or evaluates.** That group is top-level; every
other candidate is an *instrument*, and an instrument belongs to whatever uses it.

In a model-training repo the subject is always `model`, which is why this rule is usually written as
"one top-level `model`". That phrasing over-fits. The subject is whatever the research is *about*:

| repo | subject | instruments (each owned by its user) |
|---|---|---|
| LLM training | `model` | `pipeline.judge`, `pipeline.teacher`, `agent.model` |
| memory / RAG research | `memory` | `agent.model` (the reader), `memory.writer`, `bench.judge` |
| retrieval research | `retriever` | `bench.judge`, the corpus encoder |
| agent-scaffold research | `agent` | `agent.model`, `agent.tool`, `bench.judge` |

**The subject can change with the pipeline's DIRECTION, in the same repo.** An eval run over a memory
system optimises nothing, so `memory` is the subject and every model is an instrument. A run that
trains an adapter over that same memory has `model` as its subject and the memory becomes an input.
Two directions, two subjects, two launcher grammars — see *Launcher dirs* below.

**The instrument test, which is mechanical:** ask *what would this run still be about if I swapped
this?* Swapping the reader in a memory benchmark still measures the memory, so the reader is an
instrument. Swapping the memory changes what is measured, so the memory is the subject. Anything that
survives the swap is owned, and it is owned by whatever calls it — never by the run.

**Every model in a run is one of these two things, and there is no third.** A judge, a teacher, an
answerer and an ingest-time extractor are all models, and none of them is the subject unless the run
is about it. Wanting a second top-level model slot is the signal that one of the two is an instrument.

### One component library, several owners

Instruments of the same KIND share one directory even when they mount in different places. Three roles
— a reader under `agent`, a writer under `memory`, a judge under `bench` — are all *models*, drawn from
one pool. Giving each role its own directory triplicates every endpoint file, and they drift on the
first port change.

So the group's **subdir is its kind** and the **mount path is its role**, and one selector may resolve
to several mounts:

```python
GROUPS = (
    # selector, subdir,  mount (LIVES),        top_level, in_path
    ("model",   "model", ("agent", "model"),   False,     True),   # the reader
    ("writer",  "model", ("memory", "writer"), False,     True),   # ingest-time extractor
    ("judge",   "model", ("bench", "judge"),   False,     False),  # the grader
)
```

The file declares what it IS (`model: {name: qwen2_5_7b_vllm, class_path: …}`); the registry decides
where it LANDS. A reader of `qwen2_5_7b_vllm.yaml` should learn what that endpoint is, not which of
three roles some run will use it for.

Two rules keep this honest:
- **Name the file for the component, never for the role.** `qwen2_5_7b_vllm.yaml`, never
  `reader_7b.yaml` — the same file is a reader in one run and a judge in the next.
- **Selection still follows ownership.** `agent.model=…`, `memory.writer=…`, `bench.judge=…`. A shared
  library does not earn a `model_name=` selector, because it is still not an independent axis.

**Where the library LIVES, when its owners span packages.** The mirror still holds — `config/model/`
sits opposite `<pkg>/model/` — but which `<pkg>`? Do not reach for a new package. Ask instead:

> **Which package is already a dependency of the other, and can the dependee still do its own job
> without the library?**

The library belongs in the package the others already import. Adding a third package to "keep it
neutral" buys nothing when a dependency edge already exists, and it fragments a repo that a reader has
to hold in their head.

The deciding question is what each package must be able to do ALONE. A benchmark harness has to score,
and scoring calls a model — so a harness that cannot instantiate a model without importing one of the
systems it measures is not standalone, and the library goes in the harness. The subject then uses it
across the edge it already depends on. Reverse those and the harness ends up importing a competitor,
which is the failure `layout-workspace` names.

**Interfaces go with the consumer that defines them; implementations go with whoever provides them; the
two meet at `class_path`.** An interface is part of the contract a harness publishes, so it lives there
even when every implementation lives elsewhere — and because config names implementations by
`class_path`, the harness never needs a static import of any of them. That is the same seam the memory
protocol uses, applied to models.

Name it for what it CONTAINS, never for the domain it serves. A directory of LLM client wrappers is
`model` or `llmbackend`, not `memllm` — the latter reads as a memory-augmented model or a training
entry point, and a reader who guesses wrong looks for a trainer that does not exist.

### Where a component LIVES vs where it APPLIES

Those are two questions, and for most components the answer is the same, which is why the distinction
stays invisible until it bites.

A component that is *instantiated* applies where it lives: a `reward` sits at `cfg.pipeline.reward` and
something calls `instantiate(cfg.pipeline.reward)`. Living and applying coincide.

A component that is a **preset over another group's fields** does not. A parallelism `backend`
(DDP/FSDP/DeepSpeed) lives at `cfg.pipeline.backend` — that is its ownership, its scope, and what
`pipeline.backend=fsdp` selects — but its content is trainer-config fields that must reach
`cfg.pipeline.trainer.config.init_kwargs`. Nothing is instantiated at `cfg.pipeline.backend` at all.

**Declare it in the GROUP DEFINITION, not in each file.** The group registry already answers "where
does this fragment mount"; give it a second column for "where does its content apply":

```python
GROUPS = (
    # selector,  subdir,             mount path (LIVES),      top_level, in_path, payload path (APPLIES)
    ("reward",   "pipeline/reward",  ("pipeline","reward"),   False,     True,    None),
    ("backend",  "pipeline/backend", ("pipeline","backend"),  False,     False,
     ("pipeline","trainer","config","init_kwargs")),
)
```

Then the loader merges each component's content (everything but its identity keys — `name`, and any
inheritance key) at that path, and the component's own YAML says nothing about plumbing:

```yaml
backend:
  name: fsdp
  fsdp: true
  fsdp_config: {...}
```

Resist putting `mount:`/`payload:` meta-keys inside every file. They restate in data what the group
registry already owns, they must be repeated correctly in each new file of that group, and they read as
configuration when they are wiring. A reader of `fsdp.yaml` should learn what an FSDP backend IS; where
it lands is a property of the GROUP, and belongs where the group is defined.

**Precedence is the whole point, and it is easy to get backwards.** A preset must merge **BENEATH** its
target: an explicit field in the owning config, and argv later still, must always win. Merging it at
group-resolution time does the opposite, because nested groups resolve *after* their owners — so the
preset would beat the explicit value. If the merge order and the override order disagree, a config that
looks like it sets a field does not, and nothing says so.

**Test it, because both failure modes are silent.** Assert (a) the preset reaches the target at all —
a preset that never arrives leaves the run behaving as the default while the config claims otherwise —
and (b) an explicit field still beats it.

**Selection follows ownership.** A nested group is named by its OWNER's config (`pipeline: {reward:
judge}`) and swapped through that same dotted path (`pipeline.reward=judge_hygiene`). It does NOT get a
`<component>_name=` argument: that would re-assert at the CLI exactly the independence the nesting
denies, and would let a run name a reward for a pipeline that has no concept of one. It keeps its own
directory, which is what keeps N arms one slot apart instead of N near-identical owner configs, and it
still contributes its own segment to the run path — that path expresses run *identity* (which arm is
this?), not the shape of the config tree, and the arms of an ablation must sit side by side.

Keep the owner's own glob **non-recursive** (`config/pipeline/*.yaml`) so a nested group's directory
cannot be swallowed by its parent.

### Nothing else is a launcher argument

Every token a launcher passes is a `<group>_name=` selector or a `a.b.c=value` override — **there are
no launcher-only flags**. A `mode=smoke` that quietly rewrites three trainer fields and redirects the
output root is a config masquerading as a flag: it is invisible in the run's `config.yaml`, so two runs
that differ by it can look identical on disk. A smoke run is a *named configuration*
(`dataset_name=healthbench_smoke`, the `tag` slot) with its own hashed run dir.

### Launcher dirs

Two grammars, and which one applies depends on how the project selects a run.

**(a) Group-sequence grammar — use this when the runner selects by `<group>_name=`.** The launcher dir
name is the sequence of the **top-level, independently-selected** group names, joined by `__`:

```
{pipeline}__{model}__{dataset}                # one segment per TOP-LEVEL group, in GROUPS order
```

**There is one grammar PER PIPELINE FAMILY, not one per repo.** Which groups are top-level follows from
the subject, and the subject follows from the pipeline's direction, so a producer and a consumer in the
same repo have different grammars. Writing one grammar for the whole repo is how a consumer's roles get
welded onto every run:

```
eval_bench__{agent}__{memory}__{bench}__{dataset}   consumer · subject = memory · scores
build_memory__{memory}__{dataset}                   producer · subject = memory · a built store
train_adapter__{model}__{memory}__{dataset}         producer · subject = model  · a checkpoint
```

`agent` and `bench` appear only in the eval grammar because only an evaluation has an answerer and a
grader. A training launcher that names a reader is describing a run that cannot exist — and if the
grammar forces it to, the name has stopped being checkable.

**The failure this catches, stated plainly because it is easy to commit:** picking ONE grammar and
applying it everywhere. Every run then carries the dominant family's roles, the config tree grows slots
that half the pipelines must leave empty, and the harness's concerns and the subject's concerns become
indistinguishable in the name. The fix is not a shorter name; it is one grammar per family, derived
from that family's subject.

Mechanically: the run-dir deriver already emits one segment per `in_path` group **present**, so per-
family grammars need no new machinery — only that a group stop being mandatory when its family does
not have one.

**An owned component NEVER gets a segment.** A `reward` is not an axis a run picks independently — it
is part of what an RL pipeline IS. So the pipeline config *embodies* its reward (`pipeline: {reward:
judge}`), and two arms that differ in reward are two PIPELINE configs, not one launcher with a fourth
slot. Adding that slot re-asserts in the name exactly the independence the nesting denies, and it
produces launcher names that claim a run selected four things when the runner only accepts three
`<group>_name=` selectors.

The test is mechanical: **a launcher segment must correspond to a `<group>_name=` argument the runner
actually accepts.** If a segment cannot be passed as a selector, it does not belong in the name.

**Avoiding N near-duplicate pipeline configs** is then the real work, and it is a solved problem: give
pipeline configs a one-line base-merge (`_base_: grpo`) so an arm is a 5-line delta naming its reward,
not a copy of a 60-field trainer block. Copies drift; the drift is silent; and the anti-pattern list
below already forbids them.

**The failure this grammar catches.** A launcher that runs N arms cannot be named at all, because the
grammar names one config chain and N arms are N chains. When you find yourself inventing a segment no
config group defines (`smoke__qwen3_4b__coevolve`: no `smoke` pipeline, no `coevolve` dataset), the
name is not the problem — the launcher is. Split it into N launchers.

A pre-flight is not an exception: it is the same arm with the `tag` slot set
(`dataset_name=healthbench_smoke`) and a short schedule passed as ordinary overrides.

**Run dirs are a different question from launcher names.** The run path expresses run IDENTITY, so an
owned component DOES contribute a path segment (the arms of an ablation must sit side by side). Launcher
name and run dir are therefore related but not identical, and only the run dir carries the component.

**(b) Slot grammar — use this when launchers name a model class and its axes directly:**

```
{stage}_{technique}[_{variant_axes...}][_{backbone}]_{scale}[_{specialty_tag}]_{dataset}[_{tag}]
```

* `technique` is the model-class file name with the redundant trailing
  family suffix dropped (`lora_mdm` → `lora`, `quantum_lora_mdm` →
  `quantum_lora`). The pipeline's `stage` already implies the family.
* `specialty_tag` (e.g. `8q`/`16q` for quantum, `8e` for MoE) is
  **required** when the technique uses it — the launcher name must
  mirror the corresponding model-config name so they are visually
  paired. A launcher that omits a slot the model config has is a
  smell — fix the launcher.
* The launcher name = a single string from which the run's purpose is
  obvious; no need to read its `config.yaml`.

## The name IS the inheritance chain

When a config declares `_base_`, its name must be **the base's name plus exactly one segment**:

```
rl_grpo                                  _base_: —            (family root)
rl_grpo_scaffold                         _base_: rl_grpo
rl_grpo_dualrole                         _base_: rl_grpo
rl_grpo_dualrole_infogain                _base_: rl_grpo_dualrole
rl_grpo_dualrole_infogain_kvmem          _base_: rl_grpo_dualrole_infogain
```

Read a name and you know its parent, what it adds, and what it reuses — without opening the file.
The rule is mechanically checkable, which is the point: `name == base_name + "_" + one_segment`.

**The failure it catches is not hypothetical.** A config named `..._infogain_kvmem` was found carrying
`_base_: ..._dualrole` — skipping `_infogain` and re-declaring the reward it should have inherited. The
name advertised a two-step chain the config did not have, so a reader (and a diff) would believe the
arm was one slot from `_infogain` when it was actually a fork of their common parent. Nothing failed
loudly; it just meant "one config slot apart", the claim the whole ablation rests on, was untrue.

Corollaries:

* **One segment per delta.** If a config adds two things at once, either it needs an intermediate
  parent, or the two belong together as one named concept. `_infogain_kvmem` is legitimate only when
  `_infogain` exists as its parent.
* **The segment names the AXIS that changed**, not the arm. `_kvmem` says the memory backend moved;
  it must not also silently move the reward.
* **A family root has no `_base_` and no inherited segment.** `rl_grpo` is a root; `rl_dualrole` is not
  a root, because its algorithm is GRPO — writing it as a root hides that it duplicates the parent's
  recipe rather than inheriting it.

## Hard rules

1. **Symmetry between paired runs.** Two arms of an ablation differ in
   name *only* by the slots that describe the change. Never tack on
   qualifiers like `_baseline`, `_v2`, `_test` that say "I am the other
   one". Absence of the variant slot **is** the baseline.
2. **No omitted defaults in YAML.** Every kwarg the loader would
   default goes into the YAML explicitly. Audit with a script that
   instantiates each class via its `class_path` and compares the
   YAML keys against the constructor signature; exit non-zero on any
   gap. Bake into CI.
   *Exception, for a framework config object with hundreds of fields
   (an HF `TrainingArguments` subclass has ~189):* naming them all is
   noise. Name the ones this experiment reasons about, splat the block
   **verbatim** into the constructor so the rest stay reachable, and
   have the run dump the fully-resolved object to `trainer_config.json`.
   Auditability comes from the dump, never from a whitelist.
3. **Code path mirrors the slot grammar.** `<package>/model/<file>.py`
   defines `<ClassName>Model`; `<package>/config/model/<file>/<file>_<scale>.yaml`
   instantiates it. A config name suffix change implies a class file
   rename, and vice versa.
4. **One subdirectory per model class.** Don't mix unrelated classes in
   the same `model/` subdir. The subdir IS the `model_class` slot.
5. **Backbone slot only when loading pretrained weights.** From-scratch
   runs simply omit it. Loading a backbone is a *user-visible*
   event — the name says so.
6. **Output dir is mechanically derived.** Don't let users invent
   per-run output paths. Build it as
   `OUTPUT_DIR / {group.name for each group present} / hash(config)[:8]`
   (e.g. `pipeline/model/dataset/reward/hash`). The hash makes
   CLI-overridden runs disambiguate themselves. The launcher's own log
   goes *inside* this dir — see `layout-output`.
7. **A group config is selected by its `name:` field, not its filename.**
   Glob `config/<group>/*.yaml` and match `<group>.name`; a missing name
   is an error and a **duplicate name is a hard error**. Keep the filename
   equal to the name by convention, but let the loader enforce uniqueness
   so a config can never be silently shadowed by a copy.
8. **A group's settings live under that group's key.** No second
   top-level home for the same concern (`pipeline.eval.*`, never a
   free-floating `eval:`). One rule means an override path is always
   predictable from the group name.
9. **The CLI/launcher overrides the YAML, at any depth.** Merge argv
   *last* over the group configs, with no allowlist of what may be
   overridden. If a launcher cannot set a field without a code change,
   the config system is broken, not the launcher.

## Steps when adding / reviewing a config

1. Identify which slot grammar applies (model / pipeline / dataset / launcher).
2. Fill in the slots from the actual class / pipeline / data source.
3. Check the file name lives in the right subdir.
4. Cross-check a paired config (the natural ablation companion). Names
   should differ in exactly the new slot.
5. Run the audit (or the project's equivalent of
   `tools/audit_config_completeness.py`) before committing.
6. If a slot can't be expressed, the slot grammar is wrong — extend it
   in this skill *and* in the project's ARCH doc. Don't just override
   ad-hoc.

## Anti-patterns

* `_v2`, `_new`, `_test`, `_baseline` suffixes — say what's *different*,
  not "this is the other one".
* Mixing model classes in one config subdir (e.g. lumping LoRA-only and
  LoRA+quantum into `quantum_lora/`).
* Dataset YAML missing a `validate:` block (use `validate: null` to make
  "no val" explicit).
* Pipeline YAML duplicating an existing one byte-for-byte (delete; reuse
  via `class_path`).
* **Near-duplicate group configs differing by ONE flag** (`grpo.yaml` vs
  `grpo_with_fix.yaml` where only `enable_fixes` differs). That flag is a
  separate axis: promote it to its own group and let the arms name
  different configs. Otherwise retuning the trainer means editing N files
  and they silently drift.
* **A branch in the pipeline that selects the arm** (`if cfg.reward_kind
  == "opd": ...`). The arm is config; the code should not know which arm
  it is running.
* **A pipeline-owned concern promoted to a top-level peer** (a `reward/`
  group beside `model/` and `dataset/`) — it claims an orthogonality
  that does not exist, since an eval pipeline has no reward. Nest it
  under its owner and keep the selector.
* **A launcher-only flag** (`mode=smoke`, `--debug`) that expands into
  config changes. It never appears in the run's frozen `config.yaml`, so
  two materially different runs become indistinguishable on disk.
* **Ambiguous env-var names shared by two subsystems.** When a trainer
  and its judge are both vLLM, a bare `VLLM_BASE_URL` names neither;
  prefix by ROLE (`JUDGE_BASE_URL`) so a misconfiguration is a loud
  mismatch instead of a silently wrong number.
* Launcher dir name that doesn't tell you which model + dataset will run.
* **A pipeline module that reaches into another group's subtree to move fields.** That is a payload
  mount the config system could not express; give the component a declared `mount` instead.
* **A preset that merges ON TOP of its target.** It silently overrides the explicit field the user
  wrote, and the config reads as though the explicit field applied.
* **A launcher whose name contains a segment no config group defines.** It means either the name is
  invented (say what it selects) or the launcher runs more than one config chain (split it). Both are
  caught by globbing launcher dirs and resolving each `__`-segment against the group configs.
* **A launcher that drives N runs.** `smoke_arms.sh judge hygiene scaffold` inside one job is a
  multi-run script, not a launcher; its name can only lie. Keep such drivers for LOCAL sweeps and give
  the cluster one launcher per chain.

## Output

When invoked:
- State the slot grammar that applies.
- List the slots and their values for the proposed name.
- Compare against any sibling configs to verify symmetry.
- Confirm the audit script (or its absence + the need to add one).
- Brief summary of the chosen name + path.

## Division of labour with `layout-workspace`

The two are one paradigm split by question, and neither should restate the other:

| question | skill |
|---|---|
| what is this config **called**, and what does a launcher dir name mean? | **this skill** |
| **where** does the file live, and what does the tree look like? | `layout-workspace` |
| what goes **inside** a config, and what may a component own? | `layout-workspace/references/config-anatomy.md` |
| where do run **outputs** land? | `layout-output` |

Rule 6 below is the seam: it is a *name* (so it lives here) that determines a *path* (so
`layout-output` consumes it).

## Companions
`layout-workspace` (where these files live — the paired skill for the experiment-facing half) ·
`naming-descriptive` (the general naming primitive this specialises) · `layout-output` (the run tree
rule 6 derives) · `platform-run` (the launcher's neutral spec) · `conventions` (the family index).
