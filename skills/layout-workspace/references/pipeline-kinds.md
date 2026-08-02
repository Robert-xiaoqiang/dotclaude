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
3. **Config NAME mirrors the code PATH**: `rl_coevolve_infogain.yaml` ↔ `pipeline/rl/coevolve.py`.
   Config files stay flat in `config/pipeline/` because that glob is deliberately non-recursive (so the
   owned-component dirs are not swallowed), so state plainly that here the mirror runs name→path, not
   path→path. A reader must not be left assuming `config/pipeline/rl/` exists.

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
