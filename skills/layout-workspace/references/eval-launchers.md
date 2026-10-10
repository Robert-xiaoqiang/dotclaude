# Eval launchers and trained-policy models

Read when wiring an eval run to the trainer whose checkpoints it scores, or giving it a judge.

## A checkpoint trained by a different trainer is a different MODEL

That rule decides launcher identity, and it follows from `model` being top-level: it is orthogonal to
every pipeline precisely because training produces one and eval consumes one.

| | pipeline | model | dataset | produces | consumes |
|---|---|---|---|---|---|
| **trainer** | `grpo`, `sft`, … | the INITIAL policy | train split | checkpoints | data |
| **eval** | `eval` | the TRAINED policy | val split / bench | scores | checkpoints |

So evaluating N arms takes N trained-policy model configs and one eval launcher per arm. Pipeline,
dataset and decoding stay byte-identical, and only the policy moves. That a trained policy is a model
config, never an eval-side `checkpoint:` field, is `config-composition`'s rule, and scoring several
checkpoints of one arm is the grid pattern of `config-variants`.

**A trained-policy config names its training run.** It records where its weights came from, so its
`model.init_kwargs.path` carries the training run's own config hash. Read one and you can find the run
that produced it. AutoRSI's `qwen3_4b_rl_grpo_rubric_mix_1k.yaml` points at
`.../rl_grpo/qwen3_4b/rubric_mix_1k/judge/5a09d62c/checkpoint-150`, the run its header comment names.

## The name follows the trainer

The trained-policy model name is `{base_model}_{trainer_pipeline_name}`, with the trainer's pipeline
name copied verbatim, and the eval launcher selects it in its model slot. `naming-config` owns both
rules and the check that the infix is a real pipeline config.

## Every model in the chain is config

A policy generates and a judge scores, and only the policy is the top-level `model`. The judge is
owned by whatever scores (`pipeline.reward.judge` for RL, `pipeline.eval.judge` for eval), and its
identity comes from config while only its endpoint may come from the environment. `config-composition`
owns both rules.
