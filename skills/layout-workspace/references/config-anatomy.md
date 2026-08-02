# Config anatomy

Read when writing a group config or deciding whether something deserves its own group.

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
| **model** | dtype/attention/precision, adapter or backbone selection, generation defaults for API models |
| **dataset** | per-split `init_kwargs` (train/validate/test), the metric set, per-split sample caps |
| **pipeline** | the framework's config as ONE verbatim block, plus loop-level knobs |

## Owned components

Not every swappable thing deserves a top-level group. Ask **who owns it**: a component meaningless
without a particular owner belongs *under* it — in subdir, mount path, and selection alike.

| owner | component | why owned |
|---|---|---|
| pipeline | **reward** | only an RL trainer has one |
| pipeline | **trainer / inferer engine** | the loop's execution strategy, not an independent axis |
| pipeline | **judge, teacher** | a model, but not the one being optimised |
| pipeline | **agent** | a whole sub-structure: it owns a model and a tool set of its own |
| agent | **model, tool, memory** | the nesting recurses — an agent's model is the agent's, not the run's |
| dataset | **metrics** | a metric scores *this* dataset's outputs |
| model | **adapter / PEFT, processor** | wraps a *specific* model class |

**Owned components nest arbitrarily deep**, because they mirror code that nests arbitrarily deep:
`config/pipeline/agent/model/<name>.yaml` opposite `<pkg>/pipeline/agent/model/<name>.py`, mounting at
`pipeline.agent.model`. The depth is never a judgement call — it is whatever the implementation already
does.

**A run has exactly one top-level `model`: the policy it optimises or evaluates.** Every other model in
the run belongs to whatever uses it. If you find yourself wanting a second top-level model slot, the
second one is owned, and the owner tells you where it goes.

**Where a component lives is not always where its content applies.** A component that gets instantiated
applies where it lives. A component that is a *preset over another group's fields* does not: it lives at
its own mount point but its content has to reach the target group's subtree, and the merge must land
*beneath* the target so an explicit field still wins. Declare that second path in the group registry,
never as meta-keys inside each file. `naming-config` owns this rule in full, under "Where a component
LIVES vs where it APPLIES".

**Selection follows ownership.** An owned component is named by its owner's config
(`pipeline: {reward: judge}`) and swapped through that path (`pipeline.reward=judge_hygiene`). It never
gets its own `<component>_name=` argument: that would re-assert at the CLI the independence the layout
just denied, and would let a run name a reward for a pipeline with no concept of one.

Identity resolves *before* field overrides land, so `pipeline.reward=X` and
`pipeline.reward.init_kwargs.k=v` compose rather than clobber.

The payoff matches a top-level group's: N arms are N small configs in one component directory sharing
one owner config, not N forked owners that drift on the first retune.

## The framework block

This is where configs rot, so two rules:

- **Pass it verbatim** (`Trainer(**cfg.pipeline.trainer_kwargs)`). A hand-picked subset makes every
  unnamed field unreachable, and the run trains on a default nobody chose.
- **Group by concern** (`adamw_kwargs`, `data_loader_kwargs`, `fsdp_kwargs`) when the framework takes
  several config objects; one flat block when it takes one.

Swapping the trainer class is itself config (`trainer_class_path` + `trainer_extra_kwargs`), so a novel
variant is a subclass named in YAML, never a fork of the assembly code.

## How the pieces compose

- `config/<group>/<name>.yaml` — fragments, merged into one tree by the config system.
- `launcher/<name>/task.yaml` — the neutral spec (`platform-run`). Its `run:` is an argv **list** of
  `k=v`: group names plus only this run's overrides.
- `launcher/launch.sh` — the one shared entrance: env/venv/multinode, ask the config system for the run
  dir, tee the log into it, hand every argument to the runner.
