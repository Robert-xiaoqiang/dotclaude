# Eval launchers and trained-policy models

Read when naming an eval launcher or wiring a judge.

## A checkpoint trained by a different trainer is a different MODEL

That rule decides launcher identity, and it follows from `model` being top-level: it is orthogonal to
every pipeline precisely because training produces one and eval consumes one.

| | pipeline | model | dataset | produces | consumes |
|---|---|---|---|---|---|
| **trainer** | `grpo`, `sft`, … | the INITIAL policy | train split | checkpoints | data |
| **eval** | `eval` | the TRAINED policy | val split / bench | scores | checkpoints |

So evaluating N arms is N launchers, each naming a different `config/model/<policy>.yaml` whose `path`
pins the checkpoint. Pipeline, dataset and decoding stay byte-identical; only the policy moves.

**The failure this prevents:** passing the checkpoint as a submit-time override so ONE launcher serves
every arm. N evals then appear on the cluster under one name, indistinguishable in the console, and the
policy's identity never reaches the frozen `config.yaml`. The tell is a second home for something a
group already owns — the policy path belongs to `model`, so an eval-side `checkpoint:` field is a
duplicate source of truth by construction.

**Model-config provenance.** A trained-policy config records where weights came from, so its `path`
carries the training run's own config hash. Read one and you can find the run that produced it.

## The name must correspond strictly to the trainer

```
train:   launcher/coevolve_evorubric__qwen3_4b__healthbench/     # {pipeline}__{model}__{dataset}
eval:    launcher/eval__qwen3_4b_coevolve_evorubric__healthbench/ # eval__{base}_{PIPELINE}__{dataset}
                          ^^^^^^^^^^^^^^^^^^ the trainer pipeline name, VERBATIM
```

**The trained-policy model name is `{base_model}_{trainer_pipeline_name}`, copied verbatim, never
abbreviated.** A compressed form reads perfectly well, which is exactly why it is dangerous: if the
infix matches no config in the repo, the link between an eval and the run it evaluates degrades into a
coincidence of wording that a reader must reconstruct by guesswork. Verbatim means the name resolves
mechanically, infix → pipeline config → trainer launcher, and a check can enforce it.

Two assertions worth having in CI: the infix IS a pipeline config name, and
`launcher/<infix>__<model>__<dataset>/` exists.

No reward slot gets appended. Two arms sharing a pipeline and differing only in reward are already two
PIPELINE configs, because reward is an owned component, so the infix stays exactly one pipeline name.

**What legitimately stays a CLI override** is a value the (pipeline, model, dataset) triple genuinely
cannot express: which checkpoint STEP of that one run to score. Same trainer, same lineage, same eval,
only the snapshot moves. Distinguish those submissions at the platform layer by deriving the job name
from the override, never by minting launcher segments.

## Every model in the chain must be config

An eval pipeline usually runs more than one model: a policy generates and a judge scores. Only the
policy is the top-level `model` group. The scorer is an owned component of whatever does the scoring
(`pipeline.reward.judge` for RL, `pipeline.eval.judge` for eval), because a judge is meaningless
detached from the thing it scores.

**None of them arrives from the environment.** A judge configured only through an env var does not
appear in the frozen `config.yaml`, so two eval runs scored by different graders are indistinguishable
on disk — and the grader is not a detail, it *is* the metric. An env var may carry the *endpoint*, since
a pod IP changes every relaunch and must not be frozen, but the judge's identity (model name,
class_path, decoding) belongs in the config.
