---
name: naming-config
description: "Apply the slot grammar to model, pipeline, dataset and launcher config names so a name uniquely identifies what runs, a derived config's name spells its inheritance chain, and two ablation arms differ in exactly the slots that describe the change. Names only."
when_to_use: "Use when adding a model variant, pipeline stage, dataset or launcher, renaming an existing config, or checking that two arms sit one slot apart. Not for how groups and fields are owned, composed and frozen (config-composition), how a run variation is represented or what a launcher may pass (config-variants), prompt names (config-prompting), or where a file lives (layout-workspace)."
---
# Skill: naming-config

## Purpose
Apply a consistent naming convention across **model**, **pipeline**,
**dataset**, and **launcher** configs in any LLM / agent / research
codebase that uses a config-driven runner (OmegaConf, Hydra, Pydantic
configs, YAML registries, etc.). Keeps file names, class paths, and
output dirs aligned so a config name uniquely identifies what runs.
This skill owns names and nothing else. Prompt names belong to
`config-prompting`.

## Contents
- [When to Use](#when-to-use)
- [Core principle](#core-principle)
- [Slot grammars](#slot-grammars)
- [The name IS the inheritance chain](#the-name-is-the-inheritance-chain)
- [Assembled names: the name IS the component list](#assembled-names-the-name-is-the-component-list)
- [Two walks, one name: assembly AND implementation](#two-walks-one-name-assembly-and-implementation)
- [Polarity: the unmarked name is the complete thing](#polarity-the-unmarked-name-is-the-complete-thing)
- [Steps when adding / reviewing a config](#steps-when-adding--reviewing-a-config)
- [Output](#output)
- [Hard rules](#hard-rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Adding a new model variant, pipeline stage, dataset, or launcher
- Renaming an existing config (refactor)
- Reviewing PRs that introduce new config files
- The user says: "what should I name this config?", "is this naming
  consistent?", "what should this launcher be called?"
- NOT for: how a config's groups and fields are owned, composed, merged
  and frozen into the run (`config-composition`), how a run variation is
  represented or which tokens a launcher may pass (`config-variants`),
  prompt names and the prompt registry (`config-prompting`), where a
  config, package or launcher file lives (`layout-workspace`), or the
  task spec and how it renders to a scheduler (`platform-run`).

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

* `model_class` matches the file name in `<package>/model/` that
  defines the class. e.g. `mdm`, `qwen3`, `quantum_mdm`. Where the
  config file sits is `layout-workspace`'s.
* `variant_axes` are class-specific knobs that go into the file name
  *only when set non-trivially* (e.g. quantum injection position /
  strategy / readout). Order them outer→inner.
* An adapter (LoRA, any PEFT method) is owned by the model it adapts,
  as `model.adapter` (`config-composition`), so it is a variant axis of
  the model name and never a model class or a pipeline
  (`mdm_lora_smdm_1028m`, with no segment for full fine-tuning).
* `backbone` appears only when weights are loaded from a pretrained
  source (e.g. `smdm`, `llama3`). Omit for from-scratch.
* `scale` matches the model-config registry key (`180m`, `1028m`, `8b`).
* `specialty_tag` for orthogonal axes that don't fit the above
  (e.g. qubit count `8q`/`16q`, expert count `8e`).
* A **trained policy** is a model config named
  `{base_model}_{trainer_pipeline_name}`, the trainer's pipeline name
  copied verbatim and never abbreviated
  (`qwen3_4b_rl_grpo_dualrole_rlcer`), and an eval launcher selects it
  in its model slot. An abbreviation still reads well, which is why it
  is dangerous. An infix that matches no pipeline config turns the link
  from an eval to the run it scores into a guess, while a verbatim infix
  resolves mechanically to the pipeline config and the trainer's
  launcher. A check enforces it by asserting that the infix is a
  pipeline config name and that
  `launcher/<infix>__<base_model>__<dataset>/` exists. No reward
  segment is appended, because two arms that differ only in reward are
  already two pipeline configs.

### Pipeline configs

```
{family}_{method}[_{variant}...]
```

* `family` names the base loop that runs (`pretrain`, `sft`, `rl`,
  `distill`, `eval`, `serve`).
* `method` is the algorithm within the family (`grpo` in `rl_grpo`,
  `onpolicy` in `distill_onpolicy`). Where the loop's math depends on the model's
  factorization, the method slot is that factorization (`sft_ar` beside
  `sft_mdm`), which is the older `{stage}_{flavour}` form.
* For `eval` the method slot is the decoding family, as in `eval_ar`
  and `eval_mdm`, because a different generate loop is different code.
  Within one decoding family, decoding settings belong to the model
  (`config-composition`) and never fork an eval pipeline name.
* `variant` segments follow *The name IS the inheritance chain* below,
  one segment per delta from the base (`rl_grpo_dualrole`,
  `eval_ar_single_turn_suite`).
* An adapter never appears here. LoRA adapts a model, so the run is
  `sft` over a model config that sets `adapter`, and the adapter shows
  in that model's name.
* What decides a family and where its code sits is in
  `layout-workspace`'s pipeline-kinds reference.

### Dataset configs

```
{method}_{source}[_{tag}]
```

* `method` is the loader (`local_packed`, `hf_streaming`, `sharegpt`).
* `source` is the corpus name (`slimpajama`, `ultrachat`, `c4`).
* `tag` for `toy` / `smoke` / `mini` subsets used for fast iteration.

### Groups beyond the three

A group is an axis a run selects by name. Whether a difference earns a group at all is
`config-variants`' question. Whether that group is a top-level peer or owned by the component that uses
it, and the test that finds a run's one subject (the thing it optimises or evaluates), belong to
`config-composition`. The naming consequence is in
*Launcher dirs* below. A top-level group is a launcher segment, an owned one is at most a run-dir
segment, and the subject decides which groups a pipeline family's launcher grammar names.

### One component library, several owners

Instruments of one kind (a reader under `agent`, a writer under `memory`, a judge under `pipeline`) share
one directory and mount at their roles. The registry that maps a kind to several mounts, and the rule
that selection follows ownership, are `config-composition`'s. Where the library's code lives when its
owners span packages, and where interfaces sit, are `layout-workspace`'s. Two naming rules stay here:

- **Name the file for the component, never for the role.** `qwen2_5_7b_vllm.yaml`, never
  `reader_7b.yaml` — the same file is a reader in one run and a judge in the next. A reader of the file
  should learn what that endpoint is, not which of three roles some run will use it for.
- **Name a library for what it CONTAINS, never for the domain it serves.** A directory of LLM client
  wrappers is `model` or `llmbackend`, not `memllm` — the latter reads as a memory-augmented model or a
  training entry point, and a reader who guesses wrong looks for a trainer that does not exist.

### Where a component LIVES vs where it APPLIES

A preset over another group's fields (a parallelism `backend` that lives at `cfg.pipeline.backend` but
whose content reaches the trainer's `init_kwargs`) lives at its own mount and applies at a payload path
the group registry declares, merged beneath its target so an explicit field still wins. That mechanism,
its precedence and the tests that catch it are `config-composition`'s. The name does not change with
it. The file is named for what it is (`fsdp.yaml`), never for where its content lands.

### Nothing else is a launcher argument

Every token a launcher passes is a `<group>_name=` selector or an `a.b.c=value` override, and there are
no launcher-only flags, because a `mode=smoke` never reaches the run's frozen `config.yaml`. That ban
and the forms a variation takes instead belong to `config-variants`. The naming half stays here. A
smoke is the dataset `tag` slot (`dataset_name=healthbench_smoke`), never a flag and never a launcher
segment of its own.

### How many overrides a launcher may carry

A full-run launcher passes its group selectors plus, when needed, the few overrides that define that
experiment permanently, and anything that varies per invocation stays out of it. Smoke, `_local`,
resume and grid variants, and the rule *commit what recurs, inline what does not*, belong to
`config-variants`, which also sends an override that changes the method into a child config. That
child is named by *The name IS the inheritance chain*, one segment for the change.

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

How N arms that differ in one field avoid becoming N near-duplicate configs (an overlay, a committed
child, a group axis or a variant launcher) is a question for `config-variants`. A committed child's
name follows *The name IS the inheritance chain* below.

**The failure this grammar catches.** A launcher that runs N arms cannot be named at all, because the
grammar names one config chain and N arms are N chains. When you find yourself inventing a segment no
config group defines (`smoke__qwen3_4b__coevolve`: no `smoke` pipeline, no `coevolve` dataset), the
name is not the problem — the launcher is. Split it into N launchers. The same holds for a script that
loops over arms inside one job (`smoke_arms.sh judge scaffold`). It is a multi-run driver, not
a launcher, and its name can only lie. Keep such drivers for local sweeps and give the cluster one
launcher per chain.

A pre-flight is not an exception: it is the same arm with the `tag` slot set
(`dataset_name=healthbench_smoke`).

**Run dirs are a different question from launcher names.** The run path expresses run IDENTITY, so an
owned component DOES contribute a path segment (the arms of an ablation must sit side by side). Launcher
name and run dir are therefore related but not identical, and only the run dir carries the component.

**(b) Slot grammar — use this when launchers name a model class and its axes directly:**

```
{stage}_{technique}[_{variant_axes...}][_{backbone}]_{scale}[_{specialty_tag}]_{dataset}[_{tag}]
```

* `technique` is the model-class file name with the redundant trailing
  family suffix dropped (`quantum_mdm` → `quantum`, `quantum_head_mdm`
  → `quantum_head`). The pipeline's `stage` already implies the family.
  An adapter is a variant axis here as in the model name, never the
  technique.
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

## Assembled names: the name IS the component list

### The principle

When a thing is built from interchangeable parts, its name must let a reader recover which parts —
and, given the parts, predict the name. That is a bijection, and it is what makes an assembly
reproducible from its name alone.

```
{base}[_{component}]...        each segment names ONE component that differs from the base
```

Three rules make it a bijection rather than a habit:

1. **One segment per component that DIFFERS from the base.** A component left at its default
   contributes nothing — absence of a segment IS the default, exactly as absence of a variant slot is
   the baseline (Hard rule 1). `_default`, `_none`, `_plain` are all wrong.
2. **Fixed slot ORDER, from the outermost structural choice inward.** `rl_grpo_dualrole_rlcer_statemem`
   reads: family `rl`, method `grpo`, structure `dualrole`, reward `rlcer`, trainer component
   `statemem`. Sorting segments alphabetically, or by when they were added, destroys the bijection.
3. **A component never takes a run name of its own.** It has no entry point and cannot run, so it gets
   no launcher and no top-level config group. Only assemblies run, and only assemblies are named.

### What is NOT a segment

**Instrumentation.** Measuring does not change what an arm is, so it must never appear in a name.
An arm named `rl_grpo_trace` is the error this prevents: every arm carries the instrument, so the
segment describes no difference between arms, and the same experiment acquires two names depending on
whether anyone was watching. The toggle itself lives in the owning component's config, off by default.
A committed smoke launcher may switch it on and a full-run launcher never does, as `config-variants`
states in full. Schedule such a toggle in the unit the experiment reasons in — OPTIMIZER
steps, not micro-batches — so changing gradient accumulation does not silently change what was
recorded.

### The same grammar, elsewhere

| domain | assembled name | recovers |
|---|---|---|
| VL model | `vlm_siglip_mlp2_qwen3_8b` | encoder · projector · backbone · scale |
| data mixture | `mix_slimpajama_starcoder_2to1` | atoms and their ratio |
| agent | `agent_react_tools_fewshot` | prompt sections, in assembly order |
| RL arm | `rl_grpo_dualrole_rlcer_statemem` | structure · reward · trainer component |

If a name cannot be read back into its parts, either a component is missing a slot or a slot is
carrying two components. Both are naming bugs, and both surface later as two runs that cannot be told
apart on disk.

### Assembly-specific anti-patterns

* **A segment for a component that did not change** — inflates every name and breaks rule 1.
* **A segment naming the instrument** (`_trace`, `_logged`, `_debug`) rather than the method.
* **Reordered segments between siblings** (`a_x_y` beside `a_y_x`) — the pair no longer reads as one
  slot apart, and an ablation table built from the names is silently wrong.
* **A component with its own launcher.** If it can be launched it is an assembly; give it a base.
* **Assembly order left implicit.** With mixins the MRO *is* the assembly order and it changes
  behaviour, so state it where the assembly is defined — not in a commit message.

## Two walks, one name: assembly AND implementation

A config name encodes TWO inheritance walks, and it must not contradict either:

1. **Assembly walk** (`_base_`): a derived config's name extends an ancestor's name by suffix
   segments. `x_y.yaml` with `_base_: x` is the walk made visible; `x_y` deriving from `z` is a
   name that lies about its parentage.
2. **Implementation walk** (class MRO): if the config resolves — directly or through its `_base_`
   chain, including owned sub-objects like `trainer.class_path` — to a class that subclasses a
   *named backbone*, the backbone's segment appears in the name. A config named as if it sat on the
   plain backbone must not resolve to the specialized one: `x_harness` whose trainer subclasses
   `DualRoleTrainer` hides a schedule change (half its passes are generator passes) behind a name
   that promises the plain trainer. Either the name carries the segment (`x_dualrole_harness`) or
   the component is made genuinely backbone-independent first — never the silent middle.

   Checking this requires resolving the CLASS, not the module: a `class_path` that names a module
   entry point tells you nothing about the trainer's MRO, and a checker that stops there reports
   zero violations forever.

**When every descendant neutralizes the base, the base is wrong.** A family whose every arm pins the
same base knob to its inert value (`role_period: 1` on a two-role backbone) sits on the wrong base. The
structural fix, the crash it prevents and the `_unset_` caveat are `config-composition`'s, and the
check that fails before submit is `layout-workspace`'s layout walk (A5). The naming consequence is the
implementation walk above: once the family is re-homed on the backbone it actually runs, its arms no
longer carry the specialized backbone's segment, and that backbone becomes a marked leaf.

## Polarity: the unmarked name is the complete thing

For datasets and any headline artifact, the UNMARKED name is the full/complete version and ablations
carry the marker: `mix` (everything) vs `mix_wo_<component>`. Naming the full thing `mix_with_x`
inverts the polarity — the baseline becomes the marked name, and every future reader must remember
which way the marking runs. This is the same rule as "absence of the variant slot IS the baseline",
applied to composition: absence of a REMOVAL marker is the whole.

## Steps when adding / reviewing a config

1. Identify which slot grammar applies (model / pipeline / dataset / launcher).
2. Fill in the slots from the actual class / pipeline / data source.
3. Check the file sits where `layout-workspace` puts it.
4. Cross-check a paired config (the natural ablation companion). Names
   should differ in exactly the new slot.
5. Run the audit (or the project's equivalent of
   `tools/audit_config_completeness.py`) before committing.
6. If a slot can't be expressed, the slot grammar is wrong — extend it
   in this skill *and* in the project's ARCH doc. Don't just override
   ad-hoc.

## Output

When invoked:
- State the slot grammar that applies.
- List the slots and their values for the proposed name.
- Compare against any sibling configs to verify symmetry.
- Confirm the audit script (or its absence + the need to add one).
- Brief summary of the chosen name + path.

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
3. **Code path mirrors the slot grammar**, so the `model_class` slot
   names the file that defines the class, a rename of one is a rename of
   the other, and where each file sits is `layout-workspace`'s.
4. **Config subdirectories are `layout-workspace`'s**, and the name
   carries the `model_class` slot whether or not a directory repeats it.
5. **Backbone slot only when loading pretrained weights.** From-scratch
   runs simply omit it. Loading a backbone is a *user-visible*
   event — the name says so.
6. **Output dir is mechanically derived.** Don't let users invent
   per-run output paths. Build it as
   `OUTPUT_DIR / {group.name for each group present} / hash(config)[:8]`
   (e.g. `pipeline/model/dataset/reward/hash`). The hash makes
   CLI-overridden runs disambiguate themselves. The launcher's own log
   goes *inside* this dir — see `layout-output`.
7. **A group config is selected by its `name:` field, and a duplicate
   name is a hard error**, as `config-composition` states in full.
8. **A group's settings live under that group's key, with no second
   top-level home**, as `config-composition` states in full.
9. **The CLI/launcher overrides the YAML, at any depth.** Merge argv
   *last* over the group configs, with no allowlist of what may be
   overridden. If a launcher cannot set a field without a code change,
   the config system is broken, not the launcher.

## Anti-patterns

* `_v2`, `_new`, `_test`, `_baseline` suffixes — say what's *different*,
  not "this is the other one".
* Dataset YAML missing a `validate:` block (use `validate: null` to make
  "no val" explicit).
* Pipeline YAML duplicating an existing one byte-for-byte (delete; reuse
  via `class_path`).
* **A branch in the pipeline that selects the arm** (`if cfg.reward_kind
  == "judge": ...`). The arm is config, and the code should not know
  which arm it is running. `code-abstraction` owns the rule that callers
  never branch on a variant.
* **Ambiguous env-var names shared by two subsystems.** When a trainer
  and its judge are both vLLM, a bare `VLLM_BASE_URL` names neither;
  prefix by ROLE (`JUDGE_BASE_URL`) so a misconfiguration is a loud
  mismatch instead of a silently wrong number.
* Launcher dir name that doesn't tell you which model + dataset will run.
* **A launcher whose name contains a segment no config group defines.** It means either the name is
  invented (say what it selects) or the launcher runs more than one config chain (split it, as
  *Launcher dirs* says). Both are caught by globbing launcher dirs and resolving each `__`-segment
  against the group configs.
* **A role in a component's file name** (`reader_7b.yaml`, `judge_qwen.yaml`). The same file serves
  another role in the next run, and the name then misdescribes it.

## Companions
`naming-descriptive` (the general naming primitive this specialises) · `config-composition` (how the
named groups are owned, composed, merged and frozen into the run) · `config-variants` (how a run varies
from its launcher, and which tokens a launcher passes) · `config-prompting` (prompt names and the
prompt registry) · `layout-workspace` (where each named file, package and launcher lives) ·
`layout-output` (the run tree that rule 6's derived path feeds, the seam where a name becomes a path) ·
`platform-run` (the task spec a launcher dir holds) · `code-abstraction` (callers never branch on a
variant, and an old `class_path` stays importable when a class moves) · `conventions` (the family
index).
