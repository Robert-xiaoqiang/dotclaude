# Two runner styles

Decide this before building `config/`. The config→launcher shell is identical either way; what differs
is what the config *points at* and how you launch.

## 1. Class-path harness — you own the loop

Each config carries a `class_path`. A generic `<pkg>/pipeline/run.py` does
`importlib.import_module(cfg.pipeline.class_path).main(cfg)`, and that pipeline instantiates
`model.class_path(**init_kwargs)`, `dataset.class_path(...)`, `reward.class_path(...)` and runs.
**Every group maps to real code.** Launch with the distributed backend you drive: `accelerate` or
`torchrun`.

This still applies when you use a *library* trainer such as TRL's `GRPOTrainer`. You own the loop's
assembly, so the trainer class is just another `class_path` (`pipeline.trainer_class_path`) with a
verbatim `trainer_kwargs` block, and a novel variant is a subclass named in config.

## 2. Framework-extension — you wrap a trainer

The config groups **override the wrapped framework's config**, and your code plugs in through its
**hooks**: a reward-manager registry, a custom reward function path, a custom dataset class.

Only the parts you own are code with a `class_path`. The framework owns model-building and data-loading,
so `config/model` and `config/dataset` are *config fragments, not class_path targets*, and there is no
generic `run.py` dispatch — the framework is the pipeline.

Launch with the framework's own mechanism. A Ray-based trainer wants a plain `python -m <driver>` to
bootstrap its cluster and actors, **not** torchrun/accelerate/DeepSpeed, which would fight its worker
management. A bare `python -m` is correct here, not a smell.

## Litmus

If you cannot point a `config/model` at a class you wrote, you are in style 2. Do not fabricate empty
`model/` wrapper modules for symmetry: put code only where you actually own it, and let the rest be
override fragments. Match the launch to the engine, not to a habit.
