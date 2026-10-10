---
name: config-composition
description: "How a config-driven run's configuration is put together and frozen: the shape of a group config, which groups a run selects and which components belong to an owner, one component library mounted at several roles, presets that apply beneath another group's fields, `_base_` inheritance, one resolver and a fixed merge order with argv last, and the merged config as the complete record of the run."
when_to_use: "Use when writing a group config, deciding whether something deserves its own group or belongs under an owner, adding a judge, teacher or reader beside the policy, or tracing how a value reaches the merged config. Symptoms: a run whose behaviour is not in its config.yaml, a value that reaches the run through an env var, a second top-level model, a field set in YAML that the run ignores, or a component selection that resolves to a bare string. Not for what a config is called (naming-config), where its file lives (layout-workspace), how a run varies from its launcher (config-variants), or prompt text (config-prompting)."
---
# Skill: config-composition

## Purpose
Own how a config-driven run's configuration is assembled. A group config has one fixed shape, a run
selects a few top-level groups and every other component mounts under the owner that uses it, and one
resolver and one merge order turn that selection into a single tree. That tree, frozen into the run
dir, is the run. What each piece is called, where its file sits and how a run varies from its launcher
belong to sibling skills.

## Contents
- [When to Use](#when-to-use)
- [The canonical shape](#the-canonical-shape)
- [Which groups are top-level](#which-groups-are-top-level)
- [Owned components](#owned-components)
- [One component library, several owners](#one-component-library-several-owners)
- [Where a component lives and where it applies](#where-a-component-lives-and-where-it-applies)
- [Inheritance inside a group](#inheritance-inside-a-group)
- [The framework block](#the-framework-block)
- [Decoding and adapters](#decoding-and-adapters)
- [One resolver owns a group's paths](#one-resolver-owns-a-groups-paths)
- [Merge order](#merge-order)
- [The merged config is the run](#the-merged-config-is-the-run)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Writing a group config, or adding a component to an existing group.
- Deciding whether something deserves its own group, belongs under an owner, or is a field.
- A run needs a second model (a judge, a teacher, a reader, a writer) and a second top-level `model`
  slot looks like the answer.
- Tracing how a value reaches the merged config, or why a field set in YAML did not take effect.
- A run whose behaviour is not in its `config.yaml`, or a value that reaches the run through an env var.
- Writing or auditing the config system itself, meaning the group registry, the resolver and the merge.
- Not for what a config or launcher is called (`naming-config`), where a config file or package lives
  (`layout-workspace`), how a run varies from its launcher through an overlay, a child config, a smoke
  or a grid (`config-variants`), or prompt text and its registry (`config-prompting`).

## The canonical shape

Every group config is one namespaced fragment keyed by its group, with the same body:

```yaml
<group>:                 # namespace == group == mount point in the merged tree
  name: <identity>       # THE SELECTOR. Unique in the group's dir; a duplicate is a hard error.
  class_path: a.b.C      # WHAT to build
  init_kwargs: {...}     # HOW to build it — every ctor kwarg, explicitly
  <group-specific>       # knobs the pipeline reads directly
```

`name` + `class_path` + `init_kwargs` is the invariant. The fourth part is where groups differ:

| group | typically also carries |
|---|---|
| **model** | dtype/attention/precision, the backbone it loads, an owned `adapter`, the decoder's settings within its decoding family, generation defaults for API models |
| **dataset** | per-split `init_kwargs` (train/validate/test), the metric set, per-split sample caps |
| **pipeline** | the framework's config as ONE verbatim block, plus loop-level knobs |

`init_kwargs` names every constructor kwarg explicitly, so the YAML alone says how the object was
built. `naming-config` rule 2 states that requirement and the CI audit that enforces it.

**`class_path` is the only seam.** A config names the code to build and never encodes control flow.
The moment a pipeline reads a config value to pick a branch (`if cfg.pipeline.kind == "harness"`), the
arm has leaked into the code and the config stops being a complete description of the run. A variant
is a different `class_path` or a different owned component. The code half of the rule, callers that
never branch on a variant, is `code-abstraction` rule 10.

**One home per concern.** A group's settings live under that group's key and nowhere else, so
`pipeline.eval.*` is right and a free-floating `eval:` beside it is not. One rule makes every override
path predictable from the group name, and a second home is two places that can disagree. AutoRSI
removed an eval-side `bench_kwargs.<bench>.max_samples` for exactly that reason. It duplicated
`dataset.validate.init_kwargs.max_samples`, so two fields could disagree about how much of a benchmark
ran. The same test rejects an eval-side `checkpoint:` field, which duplicates the path the `model`
group already owns. AutoRSI's launch block also sets `mixed_precision: "no"` on purpose. Dtype has one
owner, the trainer config, and a second owner is how a run silently trains in the wrong precision.

## Which groups are top-level

A group is an axis a run selects by name. Something earns a group when its values are components the
code builds (each a `class_path` with its kwargs) or presets the loader applies, and runs choose among
them. Whether a one-field difference between two runs has reached that point, or stays an overlay or a
committed child config, is `config-variants`' question. Once something is a group, where it goes
starts with one question.

> **Is it orthogonal to every pipeline in its family, or owned by one?**

`model` and `dataset` are orthogonal. An SFT run, an RL run and an eval run all need a policy and
data. A `reward` is not, because only an RL trainer has one and an eval pipeline has none. Placing it
beside `model` and `dataset` asserts an orthogonality that does not hold, and the config tree then lies
about the domain. Orthogonality is tested against the pipelines that share a launcher grammar, so the
same noun can land on either side. MemCodex's eval family selects `agent` at top level because every
eval run there has an answering agent, while a repo where only one pipeline runs an agent mounts it
under that pipeline.

**A run has exactly one subject, the thing it optimises or evaluates.** The subject is top-level. Every
model that is not the subject is an instrument, and an instrument belongs to whatever uses it.

In a model-training repo the subject is `model`, which is why the rule is usually written as "one
top-level `model`". That phrasing over-fits. The subject is whatever the research is about, and
MemCodex, whose runs are about a memory system, has no top-level `model` at all:

| repo | subject | instruments (each owned by its user) |
|---|---|---|
| LLM training (AutoRSI) | `model` | the judge inside `pipeline.reward`, the teacher inside a distill pipeline's trainer config |
| memory research (MemCodex) | `memory` | `agent.model` (the reader), `memory.writer`, `pipeline.judge` |
| retrieval research | `retriever` | `pipeline.judge`, the corpus encoder |
| agent-scaffold research | `agent` | `agent.model`, `agent.tool`, `pipeline.judge` |

An owned judge takes one of two forms. AutoRSI writes it as an inline block in the reward's own file,
merged at `pipeline.reward.init_kwargs.judge`, while MemCodex mounts a shared model file at
`pipeline.judge` ([One component library, several owners](#one-component-library-several-owners)).

**The subject can change with the pipeline's direction, in the same repo.** An eval run over a memory
system optimises nothing, so `memory` is the subject and every model is an instrument. A run that
trains an adapter over that same memory has `model` as its subject, and the memory becomes an input.
Two directions give two subjects, and each pipeline family then has its own launcher grammar
(`naming-config`, Launcher dirs). `pipeline-kinds.md` in `layout-workspace` tabulates direction per
pipeline kind, with `distill` as the kind that needs a teacher beside the policy.

**The instrument test is mechanical.** Ask what the run would still be about if this were swapped.
Swapping the reader in a memory benchmark still measures the memory, so the reader is an instrument.
Swapping the memory changes what is measured, so the memory is the subject. Anything that survives the
swap is owned, and it is owned by whatever calls it, never by the run.

**Every model in a run is one of these two things, and there is no third.** A judge, a teacher, an
answerer and an ingest-time extractor are all models, and none of them is the subject unless the run is
about it. Wanting a second top-level model slot is the signal that one of the two is an instrument.

## Owned components

Not every swappable thing deserves a top-level group. Ask **who owns it**. A component meaningless
without a particular owner mounts under that owner and is selected through it. A group therefore
carries three placements, and each one means something:

| placement | encodes | top-level group | owned component | owned by |
|---|---|---|---|---|
| **subdir** | where the code lives | `config/<group>/` | `config/pipeline/rl/reward/` (AutoRSI) | `layout-workspace` |
| **mount path** | scope, where it lives in the merged tree | `cfg.<group>` | `cfg.pipeline.reward` | this skill |
| **payload path** | reach, where its content applies | the mount | usually the mount, sometimes another subtree | this skill |

| owner | component | why owned |
|---|---|---|
| pipeline | **reward**, **critic** | only an RL trainer has one |
| pipeline | **score**, **protocol**, **reduce** | only an eval pipeline grades, so AutoRSI mounts them at `pipeline.eval.*` |
| pipeline | **trainer / inferer engine**, parallelism **backend** | the loop's execution strategy, not an independent axis |
| pipeline | **judge, teacher** | a model, but not the one being optimised or evaluated |
| pipeline | **agent**, where only some pipelines run one | it owns a model and a tool set of its own |
| agent | **model, tool** | the nesting recurses, so an agent's model is the agent's and not the run's |
| memory | **writer, routing, storage** | MemCodex: `fullcontext` and `bm25` have no write side and no hierarchy |
| dataset | **metrics** | a metric scores *this* dataset's outputs |
| model | **adapter (LoRA, PEFT), processor** | wraps a *specific* model (see [Decoding and adapters](#decoding-and-adapters)) |
| any | a **`prompts:` block** | `config-prompting` owns what is inside it, and this skill only mounts it |

**Owned components nest as deep as the code does.** An agent owns a model and a tool set while being
owned by the pipeline that runs it, which mounts its model at `cfg.pipeline.agent.model`. There is no
depth limit and no judgement call, because the nesting is whatever the implementation already does. A
kind that several owners use is the one exception. Each role still mounts under its owner, while the
files stay in one directory for the kind (next section).

**Selection follows ownership.** An owned component is named by its owner's config
(`pipeline: {reward: judge}`) and swapped through that same dotted path (`pipeline.reward=judge_delta`).
It never gets a `<component>_name=` argument. That would re-assert at the CLI the independence the
nesting denies, and would let a run name a reward for a pipeline with no concept of one. The component
still contributes a run-dir segment when it says which experiment this is, because the arms of an
ablation must sit side by side. The registry's `in_path` column marks that, and `naming-config` rule 6
derives the path.

**Identity resolves before field overrides land**, so `pipeline.reward=X` and
`pipeline.reward.init_kwargs.k=v` compose rather than clobber. This takes care in the loader.
`OmegaConf.from_cli` applies dotted assignments in order, so the field override replaces the selection
string with a dict and the selection is silently lost. AutoRSI pulls component selections out of the
raw argv by exact key before anything parses it, which makes the two orthogonal and order-independent.

**An owned component needs a registry row, or its selection is a string.** Without a row,
`pipeline.curriculum: uniform` resolves to the bare string `'uniform'`, nothing builds it, and the arm
trains as its own control under the treated arm's name. AutoRSI met this from both ends. Eight arms
whose slots had no row sat in `launcher/` with submittable `task.yaml` files until
`scripts/checks/arm_slot_registration.py` caught them before launch. Earlier, the four arms of a
`query` slot had their row and still trained as their own control while preflight printed `ok`,
because the trainer's list of groups to build did not name it, so a row without wiring fails the same
way. MemCodex hit it too. `MemoryConfig` carried `summarizer_model` and the factory read it, but with
no registry row nothing mounted `memory.summarizer=x`. A component has to exist in the config, the
code and the registry, and a check should fail any config that names a component with no row.

## One component library, several owners

Instruments of the same kind share one directory even when they mount in different places. A reader
under `agent`, a writer under `memory` and a judge under `pipeline` are all models, drawn from one pool.
Giving each role its own directory triplicates every endpoint file, and the copies drift on the first
port change.

So the group's **subdir is its kind** and its **mount path is its role**, and one kind may resolve to
several mounts. MemCodex's registry, abridged:

```python
GROUPS = (
    # selector, subdir,  mount (LIVES),          file_key, top_level, in_path, payload
    ("model",   "model", ("agent", "model"),     "model",  False,     True,    None),  # the reader
    ("writer",  "model", ("memory", "writer"),   "model",  False,     True,    None),  # ingest-time extractor
    ("judge",   "model", ("pipeline", "judge"),  "model",  False,     False,   None),  # the grader
)
```

The file declares what it is (`model: {name: qwen2_5_7b_vllm, class_path: …}`), and the registry
decides where it lands. The `file_key` column is what lets one file serve every role. The loader strips
the file's top key, which names its kind, and mounts the content at the row's own path. A reader of
`qwen2_5_7b_vllm.yaml` learns what that endpoint is, not which role some run will give it, which is
also why `naming-config` names such a file for the component and never for the role.

**Selection still follows ownership.** `agent.model=…`, `memory.writer=…` and `pipeline.judge=…` each
go through their owner. A shared library does not earn a `model_name=` selector, because it is still
not an independent axis.

Which package holds the library when its owners span packages is a placement question, and
`layout-workspace` answers it.

## Where a component lives and where it applies

Those are two questions, and for most components the answer is the same, which is why the distinction
stays invisible until it bites.

A component that is *instantiated* applies where it lives. A `reward` sits at `cfg.pipeline.reward`, and
something calls `instantiate(cfg.pipeline.reward)` right there.

A component that is a **preset over another group's fields** does not. A parallelism `backend` (DDP,
FSDP, DeepSpeed) lives at `cfg.pipeline.backend`, which is its ownership, its scope and what
`pipeline.backend=fsdp` selects. Its content, though, is trainer-config fields that must reach
`cfg.pipeline.trainer.config.init_kwargs`, and nothing is instantiated at `cfg.pipeline.backend` at all.

**Declare it in the group definition, not in each file.** The group registry already answers where a
fragment mounts, so give it a second column for where its content applies. AutoRSI's rows:

```python
GROUPS = (
    # selector, subdir,               mount path (LIVES),      top_level, in_path, payload path (APPLIES)
    ("reward",  "pipeline/rl/reward", ("pipeline", "reward"),  False,     True,    None),
    ("backend", "pipeline/backend",   ("pipeline", "backend"), False,     False,
     ("pipeline", "trainer", "config", "init_kwargs")),
)
```

The loader merges each such component's content, everything but its identity keys (`name` and
`_base_`), at that path, and the component's own YAML says nothing about plumbing:

```yaml
backend:
  name: fsdp
  fsdp: true
  fsdp_config: {...}
```

Resist putting `mount:` or `payload:` meta-keys inside every file. They restate in data what the group
registry already owns, they must be repeated correctly in each new file of that group, and they read as
configuration when they are wiring. A reader of `fsdp.yaml` should learn what an FSDP backend is. Where
it lands is a property of the group, and belongs where the group is defined.

**Precedence is the whole point, and it is easy to get backwards.** A preset must merge **beneath** its
target, so an explicit field in the owning config, and argv later still, always wins. Merging it at
group-resolution time does the opposite, because nested groups resolve after their owners and the
preset would then beat the explicit value. If the merge order and the override order disagree, a config
that looks like it sets a field does not, and nothing says so.

The converse failure follows from the same order. A preset field that its target already sets
explicitly is inert. MemCodex's read-budget sweep is six three-line preset files applied beneath
`memory.routing.init_kwargs`, and each carries only `read_char_budget`, because a `top_k` added to one
would lose to the routing YAML's explicit value and that point of the sweep would silently not move.

**Test it, because both failure modes are silent.** Assert that the preset reaches its target at all,
since a preset that never arrives leaves the run on the default while the config claims otherwise, and
that an explicit field still beats it. AutoRSI's `scripts/checks/config_and_render.py` asserts both,
and also that identity keys never travel to the payload path.

## Inheritance inside a group

A config may name a `_base_` in its own group, and the loader merges the base underneath it. That is
what lets an arm be a few lines of delta instead of a copy of a 60-field trainer block. AutoRSI lived
the alternative first, when `rl_grpo_dualrole.yaml` duplicated `rl_grpo.yaml`'s recipe verbatim and only
a check held the two together. The mechanics:

- Merge order is the base, then the deriving file, then argv last.
- `_base_` stays in the merged config on purpose. It is part of what the config is, and the frozen
  `config.yaml` should say so.
- A cycle is an error that prints the chain.
- `_unset_: [key, ...]` is the one way a derived config removes an inherited key. It exists because some
  inherited keys are not wrong-valued but inapplicable. `memory_kwargs.promote_after` means something to
  a string-keyed pool and nothing to the associative one, whose constructor rejects it. An override
  cannot express removal, and the alternatives are worse. A constructor that swallows unknown kwargs
  hides real typos, and filtering kwargs to the target signature hides them everywhere at once.
  Unsetting a key no ancestor set is not an error, so a delta need not know which ancestor introduced a
  field.

What a derived config is called, its base's name plus one segment, is `naming-config`'s rule.

**When every descendant neutralizes the base, the base is wrong.** If each derived config pins the same
base-contributed knob to its inert value (`role_period: 1` in every arm of a family whose base is the
two-role backbone), the family is telling you its inheritance is inverted. The arms wanted the other
backbone all along and were silencing this one file by file. The fix is structural. Re-home the family
on the backbone it actually runs and let the specialized backbone become a marked leaf, never add one
more pin. The pins are also latent crashes. The moment the base class changes, inherited but
inapplicable constructor kwargs become constructor refusals at the pod, and check A5 of
`layout-workspace`'s layout walk turns that drift into a pre-submit failure.

A mid-chain `_unset_` cleans its own resolution, but a descendant that re-declares the key reintroduces
it. Check the whole family after removing a layer, not just the config that carried the marker.

## The framework block

The framework's own config object is where configs rot. An HF `TrainingArguments` subclass such as
TRL's `GRPOConfig` carries about 189 fields, so four rules govern it.

- **Pass it verbatim.** AutoRSI splats `pipeline.trainer.config.init_kwargs` into the class named by
  `pipeline.trainer.config.class_path`. A hand-picked subset makes every unnamed field unreachable from
  YAML and argv, and the run trains on a default nobody chose. AutoRSI's first version lost a week to a
  `build_config()` that picked 14 of `GRPOConfig`'s 189 fields, which left `use_vllm`,
  `lr_scheduler_type` and `mask_truncated_completions` out of reach. (Cost of learning this: four arms
  × 12h, all flat.)
- **Write what the experiment reasons about, and dump the rest.** Name the fields this experiment
  reasons about, splat the block so the rest stay reachable, and have the run dump the fully resolved
  object into its run dir (`trainer_config.json` in AutoRSI), so the fields left at their library
  default are on record. Auditability comes from the dump, never from a whitelist. This is the one
  exception to writing every kwarg explicitly (`naming-config` rule 2).
- **Group by concern** (`adamw_kwargs`, `data_loader_kwargs`, `fsdp_kwargs`) when the framework takes
  several config objects, and keep one block when it takes one.
- **The classes are config too.** `pipeline.trainer.class_path` names the trainer and
  `pipeline.trainer.config.class_path` names the config object it takes, both in the same `class_path`
  and `init_kwargs` shape as every other group. A novel variant is then a subclass named in YAML, never
  a fork of the assembly code. AutoRSI learned the second half late. Under its old `trainer_class_path`,
  `trainer_extra_kwargs` and `trainer_kwargs` fields, `GRPOConfig` was hardcoded in Python, so its 189
  fields were configurable while the class holding them was not. That bites the moment a trainer needs
  another config class, and `AsyncGRPOConfig` has 8 fields `GRPOConfig` lacks and lacks 63 that it has.

## Decoding and adapters

Two model-side properties are repeatedly filed as pipelines. Both are settled here.

**An eval pipeline's method slot is its decoding family.** A different generate loop is different code,
and different code is a different pipeline, so an autoregressive eval is `eval_ar` and a
masked-diffusion policy that needs its own denoising loop gets an `eval_mdm` beside it. Within one
decoding family, the decoder's own settings (denoising steps, block length, remasking order) belong to
the model config and never fork an eval pipeline. How many samples at what temperature is sampling,
which lives at `pipeline.eval.generation`. AutoRSI follows this. Every eval config it has is
`eval_ar_*`, and its siblings move owned fields within that one family, `eval_ar_graded` the scorer at
`pipeline.eval.score` and `eval_ar_k_consistency_suite` the protocol at `pipeline.eval.protocol`. The
slot grammar is `naming-config`'s. The fork rule for the remaining eval axes (corpus, protocol,
reduction, scorer, state carry) is `eval-axes.md` in `layout-workspace`, which agrees with this
paragraph. It makes AR versus MDM the method slot and keeps the decoder settings within a family on the model.

**A parameter-efficient adapter is owned by the model it adapts.** LoRA, QLoRA, IA3 and every other PEFT
method change which weights move, and SFT, DPO and GRPO all run with or without one. So an adapter is
configured as `model.adapter`, never as a pipeline kind, a pipeline flavour or a pipeline boolean. A
`peft` pipeline forks the SFT loop and the fork drifts, and a pipeline flag that flips LoRA-only
training records a property of the model where no model config shows it. The run is the ordinary `sft`
pipeline with an adapter set on its model. `pipeline-kinds.md` in `layout-workspace` sets this axis
beside the loop and the policy's factorization. MemCodex's `train_adapter`, a pipeline whose method
slot is the adapter and whose LoRA `rank` sits in `pipeline.init_kwargs`, is debt against this rule
and not a precedent.

## One resolver owns a group's paths

When a group's configs may live in subdirectories that mirror the code (`config/pipeline/rl/grpo/`
beside `autorsi/pipeline/rl/grpo/`), "which files are this group's" becomes a real function. It is a
recursive walk that excludes every other registered group's subdirectory. **Ownership must come from
the group registry, never from glob depth.** Depth was only ever an accident that happened to encode
ownership, and the registry already says that `pipeline/rl/reward/` belongs to `reward` and not to
`pipeline`.

Export one `group_config_paths(group)` from the config system, and make the loader and every check
import it. AutoRSI once had eight checks with private flat `pipeline/*.yaml` globs, and the day the
family subdirectories appeared every one of them went blind at once while reporting healthy empty sets.
Its `config/pipeline/` now holds no file at its top level, so a flat glob there finds nothing at all.

## Merge order

The config system turns a launcher's argv into one tree in a fixed order, and each step sits where it
does because the other order failed somewhere.

1. **Each top-level group is selected by its `name:` field, not its filename**, among the files the
   resolver returns for it. A missing name is an error that lists the known names, and a duplicate name
   is a hard error that names both files, so a config can never be silently shadowed by a copy. Keep the
   filename equal to the name by convention and let the loader enforce uniqueness. The `<group>_name=`
   selector is consumed here and never merged into the tree.
2. **Its `_base_` chain merges beneath it**, base first
   ([Inheritance inside a group](#inheritance-inside-a-group)).
3. **Owned components resolve next.** The owner's config names a default (`pipeline.reward: judge`),
   argv may replace it (`pipeline.reward=judge_delta`), and the chosen file mounts at the component's
   path.
4. **Presets merge beneath their targets**, at their payload paths.
5. **argv merges last, at any depth, with no allowlist.** Every `a.b.c=value` token goes through one
   parser, so any field is reachable from a launcher without touching Python. If a launcher cannot set a
   field without a code change, the config system is broken, not the launcher.

In one line, `_base_` < group YAML < argv, with each preset beneath its own target.

**An unknown top-level argv key is a hard error.** In AutoRSI, `reward_name=asymmetric_opd`, a stale
selector from before reward became a pipeline component, was once accepted as a no-op, and that arm
trained as the baseline while its launcher, its logs and its run dir all claimed otherwise. A typo that
changes which experiment runs must never be survivable. The error names the valid roots and says that a
component is set through its owner.

What a launcher may put into that argv, and how many overrides a full run carries, is
`config-variants`' question. The `task.yaml` whose `run:` list carries the argv is `platform-run`'s,
and the shared entrance that hands it to the runner is `layout-workspace`'s.

## The merged config is the run

The merged tree is hashed into the run dir and frozen there as `config.yaml`. Anything that influences a
run but is not in it (an env flag, a `mode=`, a hand-edited default, a value computed at submit time) is
invisible history, and two materially different runs become indistinguishable after the fact. So every
value that changes what the run computes reaches it through a group config or an argv override, and
through nothing else.

Settings that feel operational follow the same rule. AutoRSI's `pipeline.launch` block carries the
`accelerate launch` flags instead of the shared entrance's exec line, because a value hardcoded in a
shell script appears in no run's frozen config. Its eval config writes `score_workers: 32` as a literal
instead of computing it from the concurrent-job count at launch, because a value derived at submit time
never reaches `config.yaml` either.

**Every model in the chain is config.** An eval usually runs more than one model, a policy that
generates and a judge that scores. At most one of them is a top-level group, and only when it is the
subject. Each other model is owned by whatever uses it (a judge under the reward or under the eval pipeline), but every one of them is in
the config. A judge configured only through an env var does not appear in the frozen `config.yaml`, so
two eval runs scored by different graders are indistinguishable on disk. The grader is not a detail. It
is the metric.

**The environment may supply an endpoint, and nothing that changes the result.** A pod IP changes on
every relaunch and must not be frozen, so a base URL or an endpoints file may arrive from the
environment, ideally one the run refuses to start without. The model's identity (its name, `class_path`
and decoding) belongs in the config. The test for any env var a run reads is whether two values of it
would make the run compute something different. An endpoint would not, so it may come from the
environment. A model name would, so it may not. AutoRSI's reward judge still falls back to `$JUDGE_MODEL`
when its `model:` field is null, which is recorded debt and not a precedent.

**A trained policy is a model config.** Evaluating N arms takes N trained-policy model configs, each
pinning its checkpoint in `model.init_kwargs.path`, never one launcher with an eval-side checkpoint
field. `eval-launchers.md` in `layout-workspace` gives the trainer-to-eval correspondence, and
`config-variants` gives the per-checkpoint grid.

The hash covers the resolved tree minus execution state such as `pipeline.trainer.resume`, so a resumed
run stays the same run, while the frozen `config.yaml` still shows the field. How the run dir is derived
from the hash is `naming-config` rule 6, and what lands inside the run dir is `layout-output`'s.

## Rules
1. **A group config is one fragment under its group key**, carrying `name`, `class_path` and
   `init_kwargs`, and nothing about where it mounts.
2. **A group config is selected by its `name:` field, never by its filename.** A missing name lists the
   known ones, and a duplicate name is a hard error.
3. **A group's settings live under its group key**, with no second top-level home for the same concern.
4. **A group is top-level only if every pipeline in its family needs it.** Anything meaningless without
   a particular owner mounts under that owner.
5. **A run has one subject and at most one top-level model.** Every other model mounts at the role of
   whatever uses it.
6. **An owned component is selected through its owner's dotted path** (`pipeline.reward=…`), never a
   `<component>_name=` argument, and it has a row in the group registry.
7. **Instruments of one kind share one directory**, and the registry, not the file, says where each one
   mounts.
8. **A preset's payload path is declared in the registry, and the preset merges beneath its target.** A
   test asserts that it arrives and that an explicit field still beats it.
9. **One resolver function names a group's files.** The loader and every check import it, and ownership
   comes from the registry, never from glob depth.
10. **`_base_` merges beneath the deriving file and stays in the merged config, and `_unset_` is the only
    way to remove an inherited key.** A family whose every arm pins the same base knob to its inert
    value is re-homed, not pinned again.
11. **The framework's config object is passed verbatim, its class is named in config, and the resolved
    object is dumped into the run dir.**
12. **An eval pipeline forks on its decoding family, never on a setting within one.** Decoder settings
    live in the model and sampling in `pipeline.eval.generation`.
13. **A parameter-efficient adapter is configured as `model.adapter`**, never as a pipeline kind,
    flavour or boolean.
14. **argv merges last, at any depth, with no allowlist, and an unknown top-level key is a hard error.**
15. **The merged config is the run.** It is hashed and frozen into the run dir, every model in the chain
    is in it, and the environment supplies at most an endpoint.
16. **`class_path` is the only seam.** No config value selects a branch in pipeline code, and a variant
    is a different `class_path` or a different owned component.

## Anti-patterns
- **A pipeline-owned concern promoted to a top-level peer** (a `reward/` group beside `model/` and
  `dataset/`). It looks like one more axis, but an eval pipeline has no reward, so the peer claims an
  orthogonality that does not exist. Nest it under its owner and keep the selector.
- **A second top-level model slot** for a judge, a teacher or a reader. It is tempting because the
  judge is a model just like the policy, but only one of them is what the run is about.
- **A `<component>_name=` argument for an owned component.** It re-asserts at the CLI the independence
  the nesting denies.
- **A component selection with no registry row.** It resolves to a bare string, nothing builds it, and
  the arm trains as its own control under the treated name.
- **A pipeline module that reaches into another group's subtree to move fields.** That is a payload path
  the config system could not express. Declare the path in the group registry instead.
- **`mount:` or `payload:` meta-keys inside each component file.** They feel self-documenting, but they
  restate the registry and must be repeated correctly in every new file.
- **A preset that merges on top of its target.** It silently overrides the explicit field the user
  wrote, and the config reads as though that field applied.
- **A preset carrying a field its target already sets.** The field loses, so that point of the sweep
  never moves.
- **A private flat glob in a check.** It works until the first family subdirectory, then reports a
  healthy empty set.
- **A whitelisting `build_config()`.** It looks tidy, and whatever it omits is unreachable while the run
  trains on defaults and looks fine.
- **A framework config class hardcoded in Python.** The fields are configurable and the class holding
  them is not, so the first trainer that needs another config class forks the assembly code.
- **One more pin per descendant** instead of re-homing a base that every arm neutralizes.
- **A config field a pipeline branches on** (`kind: harness` read by an `if`). It saves writing a
  class, but the arm leaks into the code and the config stops being a complete description of the run.
- **A model identity read from an env var.** It is convenient because the serving pool already exports
  it, but the frozen config then cannot say which grader produced the metric.
- **A `peft` pipeline, or a LoRA-only boolean on a pipeline.** It forks the training loop for a property
  of the model.
- **An eval pipeline per decoder setting** (`eval_mdm_steps64`, `eval_mdm_block32`). A setting within
  a decoding family belongs to the model, and the fork multiplies pipelines that differ in one field.

## Companions
`naming-config` (what each config and launcher is called, including the audit of its rule 2 and the
run dir of its rule 6) · `layout-workspace` (where each config file and package lives, the shared
entrance, and the references `pipeline-kinds.md`, `eval-axes.md` and `eval-launchers.md`) ·
`config-variants` (how a run varies from its launcher, as an overlay, a committed child config, a group
axis or a variant launcher) · `config-prompting` (the `prompts:` block and everything inside it) ·
`platform-run` (the task spec whose `run:` argv this skill merges) · `code-abstraction` (the interface
behind a `class_path`, and callers that never branch on a variant) · `layout-output` (the run tree the
frozen config lands in) · `conventions` (the family index).
