# Pipeline kinds and the axes they vary along

Read when adding a pipeline kind, or when a proposed name does not obviously belong to a group.

## Direction relative to the policy

| direction | pipelines | reads | writes |
|---|---|---|---|
| **producer** | `sft`, `dpo`, `grpo` | data | checkpoints |
| **consumer** | `eval`, `serve`, `agent` | a checkpoint | scores / a service / trajectories |
| **both** | `distill` | a TEACHER checkpoint + data | a STUDENT checkpoint |

`distill` is the stress test: it needs *two* model slots. The teacher is not a second top-level `model`,
because a run has one policy under optimisation. It is an owned component, `pipeline.teacher`, for the
same reason a judge is: anything that is a model but is not the thing being optimised belongs to the
pipeline that uses it.

## Three axes, not one menu

"sft, peft, rl, eval, ar, nar, mtp" reads like one list of pipeline kinds. It is three axes wearing one
coat, and collapsing them puts `pipeline/lora.yaml` beside `pipeline/eval.yaml` — two things that cannot
be swapped for one another.

| axis | question | where it lives | values |
|---|---|---|---|
| **the LOOP** | what procedure is executing? | `pipeline` (top-level) | `sft`, `dpo`, `grpo`, `distill`, `eval`, `serve`, `agent` |
| **the POLICY'S FACTORIZATION** | how does the model define p(y\|x)? | `model_class` (names CODE) | causal, masked-diffusion, and their variants |
| **the ADAPTATION** | which weights actually move? | `model.adapter` (owned) | full, `lora`, `qlora`, `ia3` |

**Categories are not slot values.** You never instantiate "an NAR"; you instantiate a specific model
class. `model_class` must name code, because the config↔code mirror rests on a config path predicting an
import path. The category is what you REASON with; the class is what you BUILD.

**PEFT is not a pipeline.** LoRA adapts a model, and you can run SFT, DPO or GRPO with or without it, so
it is owned by `model` and the run is `sft` + `model.adapter=lora`. Giving PEFT its own pipeline forks
the SFT loop, which then drifts.

**Factorization propagates into the pipeline when the loop's math depends on it.** A diffusion model's
SFT objective is an ELBO over masked positions; an autoregressive one's is next-token cross-entropy.
Same stage, different loop, so they are separate pipeline modules and the grammar becomes
`{stage}_{flavour}`. That is not duplication but two objectives sharing a stage name.

So the axes are not fully orthogonal: model and dataset are orthogonal to every pipeline, while
factorization gates which (pipeline, model) pairs are even valid. When a pipeline's math is
factorization-specific, say so in its name; when it is not, keep one pipeline.

## What determines the FAMILY: rollout source x what the objective consumes

The train-side families are not a taste list. Two questions fix them:

| family | rollout source | what the objective consumes |
|---|---|---|
| `sft` | a FIXED dataset | the given target tokens (cross-entropy) |
| `distill` | EITHER (see below) | a TEACHER's per-token distribution (KL / JSD / CE) |
| `rl` | ON-POLICY, sampled from the policy | a SCALAR reward per sequence (policy gradient, GRPO) |

**`distill` splits again on where its samples come from**, because that is a different loop, not a
flag: `distill/offpolicy/` consumes a fixed corpus of teacher outputs (an SFT-shaped loop with a
teacher-provided target), while `distill/onpolicy/` samples from the STUDENT and asks the teacher to
score those tokens. Same family, two bases — hence `distill_offpolicy` and `distill_onpolicy`, and a
guided self-distillation arm is `distill_onpolicy_rubric`. Do not compress this to `opd`: the config
name must walk to the code, and there is no `pipeline/opd/`.

The same subdivision is expected of the other families as they grow — `rl/grpo/` vs `rl/ppo/`,
`sft/full.py` vs `sft/peft.py`. A family root is a directory precisely so its methods can be siblings.

On-policy distillation is the one people misfile. It samples on-policy like RL, so it looks
like RL — but it has no reward, no advantage and no group; the signal is dense and per-token, coming
from a second distribution rather than a scalar. Filing it under `rl` would put it on a base class
built around rollout -> reward -> advantage, none of which it uses. Filing it under `sft` would claim
its data is fixed, which is the one thing on-policy means it is not.

The discriminating question, in order: **is the data fixed or sampled from the model being trained?**
then **does the objective consume a scalar or a distribution?**

A method whose teacher is a frozen copy of the student is still `opd` — self-distillation is a
statement about where the teacher's WEIGHTS come from, not about the loop. Put that in the method slot
(`opd_self`) and what the teacher sees that the student does not in the variant slot
(`opd_self_rubric`, `opd_self_memory`). Two arms that differ only in the guidance are then one slot
apart by construction, which is exactly the asymmetric with/without diagnostic.

## The name encodes the TAXONOMY, not the method's title

```
{family}_{method}[_{variant}...]
```

| level | question | train-side | eval-side |
|---|---|---|---|
| **family** | which BASE INFRA runs? | `sft`, `rl`, `distill`, `pretrain` | `eval`, `serve`, `agent` |
| **method** | which algorithm within it? | `grpo`, `dpo`, `rgsd` | the DECODING paradigm, or the agent loop |
| **variant** | what is one slot from a sibling? | the reward, the schedule, the memory | the tool set, the decoding budget |

`rl_grpo` · `rl_grpo_scaffold` · `rl_coevolve_infogain` · `distill_rgsd` · `eval_ar` · `agent_react`.

**The family goes first because it names the base class that runs.** Every `rl_*` shares
rollout → reward → advantage → update; every `distill_*` shares two conditions and a divergence; every
`eval_*` shares load → generate → score. Reading the prefix tells you which abstraction you extend, so
a new arm inherits instead of forking.

**A method name alone is wrong even when it is a good name.** A title like `coevolve` says what is
novel — ideal for a paper, useless as a module path: it does not say the family, the algorithm it
derives from, or what it reuses. Put the novelty in the METHOD or VARIANT slot of a name whose prefix
is structural. A PROJECT name is worse: when the package, the output root and every pipeline share it,
the prefix partitions nothing — the same redundancy the model grammar strips as a family suffix.

**Eval-side's method slot is the decoding paradigm**, by the same argument that factorization forks
the training loop: different generate loops are different code, hence different pipelines. An agentic
eval is a different loop again, not a flag on a decoding one.

## The code tree mirrors the taxonomy, and the abstractions are load-bearing

```
<pkg>/pipeline/
  base.py           TrainPipeline / EvalPipeline — what EVERY pipeline provides
  rl/
    base.py         RLPipeline: rollout -> reward -> advantage -> update
    grpo.py         GRPOPipeline(RLPipeline)
    coevolve.py     CoEvolvePipeline(GRPOPipeline)  — roles + schedule; inherits the rest
  distill/
    base.py         DistillPipeline: TWO CONDITIONS + a divergence
    self.py         SelfDistillPipeline(DistillPipeline) — teacher is a frozen copy of the student
  eval/
    base.py         EvalPipeline: load_records -> generate -> score
    ar.py           autoregressive decoding
    bench/          benchmarks, which are DATA and not pipelines
```

Three rules keep the hierarchy real rather than decorative:

1. **A new arm SUBCLASSES; it never forks.** If a variant copies its parent's loop to change one step,
   the parent is missing a hook — add the hook.
2. **A family base owns what the family shares and nothing more.** `DistillPipeline` owns "two
   conditions and a divergence"; it must not know that one condition happens to be rubric-conditioned,
   or a later teacher-student / with-memory-vs-without arm cannot reuse it. The ASYMMETRY is the
   abstraction; what fills the two conditions is the subclass's business.
3. **Config NAME mirrors the code PATH, segment for segment.** Replace `/` with `_` and you have the
   config name; split the name on `_` and you have the directory walk:

   ```
   pipeline/rl/grpo/__init__.py            rl_grpo
   pipeline/rl/grpo/dualrole.py            rl_grpo_dualrole
   pipeline/distill/onpolicy/__init__.py   distill_onpolicy
   pipeline/distill/onpolicy/rubric.py     distill_onpolicy_rubric
   pipeline/distill/offpolicy/__init__.py  distill_offpolicy
   pipeline/sft/full.py                    sft_full
   ```

   This is why an abbreviation is not a free choice. If the code lives in `distill/offpolicy/`, the
   config is `distill_offpolicy` — NOT `opd`, however standard the acronym is in the literature. A name
   that does not walk to its own implementation makes the mirror a thing you have to remember instead
   of a thing you can derive, and the first person to guess wrong finds nothing.

   Config files stay FLAT in `config/pipeline/` (that glob is deliberately non-recursive so the
   owned-component dirs are not swallowed), so the mirror runs name→path, not path→path. Say so; do not
   leave a reader assuming `config/pipeline/rl/` exists.

4. **A segment with NO code names an owned component's selection.** Not every segment adds a module.
   `rl_grpo_dualrole_infogain` is three lines — `_base_`, `name`, `reward: rubric_infogain` — and has
   no implementation of its own, because its contribution lives in the REWARD it selects. That is
   correct, not a defect: the alternative is a fourth launcher segment for an axis the runner has no
   selector for. The rule is only that such a segment must name a real component selection (a reward, a
   memory backend, an adapter) and must not smuggle in a second change. Read a name as:
   *walk the segments that have code, then read the rest as component selections.*

## Every group has its own abstraction, not just `pipeline`

The inheritance story is not a pipeline privilege. Each top-level group and each owned component has a
family root, subclasses that add one thing, and a polymorphic seam the runner dispatches through.

| group | family root | subclasses add | polymorphic seam |
|---|---|---|---|
| **pipeline** | `rl_grpo`, `opd_self`, `eval_ar` | a schedule, a guidance, a decoding | `pipeline.class_path` -> `main(cfg)` |
| **model** | the base policy | trained weights, an adapter, extra heads | `model.class_path` -> a policy object |
| **dataset** | the corpus loader | a split, a subset, a scaffold transform | `dataset.<split>.class_path` |
| **reward** (owned by rl) | the judge | a rubric rule, a memory backend | `reward.class_path` -> a callable |
| **memory** (owned by reward) | the store INTERFACE | exact-match vs associative | `memory_class` |
| **agent** | the loop | a tool set, a stopping rule | `pipeline.class_path` + owned `tools` |

Two rules make these real rather than decorative:

1. **An interface that two implementations share must be DECLARED, not implied.** Two memory backends
   that both happen to provide `admit / hist / grading_set / merge / report` are a duck-typed contract
   nobody wrote down: the second one is authored by reading the first, and every shared rule (the EMA
   cold start, the eviction policy, the count-weighted merge) gets written twice and drifts. Declare
   the base, and a third backend inherits the rules instead of re-deriving them.
2. **The seam is a `class_path`, so the code never branches on which implementation is live.** A
   pipeline that reads a config value to decide which memory or which reward it has is the arm leaking
   into the code (see the anti-patterns). Dispatch, do not branch.

The corollary for names: since every group inherits, every group's names obey the same
name-is-the-chain rule (`naming-config`). `qwen3_4b_rl_grpo` is a trained-policy subclass of
`qwen3_4b`; the segment says which trainer produced it.

## The litmus for any new word

**Does it change which code the run instantiates, or only which values that code reads?**

A new class means a `model_class` or a `pipeline`. A new setting means a variant axis or an owned
component. Beware terms that describe *decoding* rather than factorization: emitting several tokens per
forward pass can mean either a genuinely different model class or an extra head on an unchanged one, and
only the factorization question separates them. Filing the second under the first breaks the invariant
that `model_class` predicts which code runs.

## Adding a kind

```
1. Direction?   producer / consumer / both  -> is `model` an input, an output, or both
2. Code:        <pkg>/pipeline/<kind>/__init__.py  with main(cfg)
3. Config:      config/pipeline/<kind>.yaml        name + class_path + init_kwargs + loop knobs
4. Owned:       anything meaningless without this pipeline nests under it
                (reward -> RL, judge -> eval, teacher -> distill, tools -> agent)
5. Launcher:    launcher/<kind>__<model>__<dataset>/task.yaml
6. Consumes a policy? Its `model` is a trained-policy config (see eval-launchers.md)
```

A new kind is one module, one config, one launcher. If it seems to need a new top-level directory or a
launcher-only flag, it is on the wrong axis — re-run the litmus. A high-level kind such as `agent` or
`serve` is no exception: same three groups, with whatever is meaningless without it nested underneath.

---

# Composition: components and assemblies

## The principle, before any example

A taxonomy answers *what kind of thing is this*. It does not answer *what is this made of*. Those are
different questions, and a tree can only encode the first — so a codebase organised by taxonomy alone
strands every shared part at whatever depth first needed it.

**A part becomes a COMPONENT the moment a second thing needs it.** Not when it looks reusable, not
when it is elegant — when a second consumer exists. Before that it is an implementation detail of one
thing and belongs inside it.

Two forces, and they pull in different directions:

| | expresses | mechanism | answers |
|---|---|---|---|
| **taxonomy** (nesting) | what kind of thing this is | directory depth | where do I look for it |
| **composition** (assembly) | what this is made of | a named part, selected | what is it made of |

Nesting alone forces *walk-in*: to vary one part you descend into the subfamily that owns it, and a
part two subfamilies share has no home above either. The symptom is unmistakable —
**a module importing sideways across the tree, or the same file existing twice at two depths.** Both
say the same thing: this is a component wearing a location.

## The rule

1. **Components live above the things that use them**, in their own directory, grouped by the axis
   they vary (`components/reward/`, `components/memory/`, not `components/for_grpo/`).
2. **A component is selected by name, never by inheritance path.** If picking a different one means
   editing a class hierarchy, it is not yet a component.
3. **An assembly is what runs, and the assembly is what gets a name.** A component alone is not
   runnable and takes no run name — no entry point, no config group of its own at top level.
4. **The assembled name records its components**, in a fixed slot order, so the name and the parts
   determine each other. See `naming-config`.
5. **Prefer selection to subclassing; use a mixin when the part changes BEHAVIOUR rather than DATA.**
   A reward is data-shaped and swaps by name. A trainer that adds a loss term is behaviour-shaped and
   composes as a mixin. Both are components; only the mechanism differs.

## Where this shows up (it is not an RL idea)

| domain | atoms | assembly |
|---|---|---|
| **RL pipeline** | reward · memory · instrument · trainer base | `rl_grpo_dualrole_rlcer_statemem` |
| **VL model** | vision encoder · aligner · projector · LM backbone | one model config naming all four |
| **agent** | prompt sections (role · tools · format · few-shot) | an assembled system prompt |
| **data** | atomic corpora, each with its own loader and licence | a named mixture with weights |

The VL case is the clearest test of rule 1: an encoder is shared by every model that uses it, so it
cannot live inside one of them. The agent case is the clearest test of rule 4: a prompt assembled from
sections must be reproducible from its section list, or the run is not reproducible at all.

## Worked example: how it went wrong, and what it cost

AutoRSI grew `pipeline/rl/grpo/dualrole/` and put THREE components inside it:

    dualrole/reward.py        a reward — while pipeline/rl/reward/ already existed
    dualrole/memory_assoc.py  a memory backend
    dualrole/memory_text.py   a second memory backend

Nothing about a reward or a memory is specific to playing two roles. They landed there because the
taxonomy offered no shelf above `dualrole/`, and the cost was visible in three ways: two reward
directories that a reader has to reconcile, memory backends invisible to any other arm, and a state
matrix instrument that was first written INSIDE one arm — where it would have measured that arm with
one implementation and its baseline with another, making the comparison meaningless.

The fix was to name the axes and lift the parts:

    pipeline/components/tracing.py   the instrument   (behaviour -> mixin, default OFF)
    pipeline/components/memory.py    the EMA memory   (behaviour -> mixin)
    pipeline/rl/reward/              rewards          (data -> selected by name)

and let pipelines assemble them:

    class StateMemoryDualRoleTrainer(DualRoleTrainer, StateMemoryTrainer)   # two roles + memory

**Read the MRO as the assembly order.** `DualRoleTrainer` first means the role schedule owns the
step and the memory composes underneath it; reversed, the memory's `compute_loss` shadows the role
alternation and the arm silently becomes single-role — training fine, reporting plausible numbers, and
not being the arm its name claims. An assembly's order is part of its meaning, so state it in the
class docstring rather than leaving it to MRO trivia.

## The test to apply

> Would a second pipeline want this part, unchanged?

Yes -> it is a component; lift it and select it by name.
No  -> it is an implementation detail; leave it where it is.

Answer this when the second consumer appears, not before. Lifting on the first speculative consumer
produces a `components/` full of parts with one user and a name chosen for a use case that never came.
