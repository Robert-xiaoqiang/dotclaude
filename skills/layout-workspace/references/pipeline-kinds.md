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
