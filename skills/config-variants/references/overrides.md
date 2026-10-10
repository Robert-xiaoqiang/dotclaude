# Reading a submit line: which overrides are wrong

Read when a launcher's `run:` has grown a wall of `a.b.c=value`, before moving anything into config.

A long submit line is a symptom, not a verdict. Four kinds hide in one, and two of them are correct
where they are. Moving those into config is not a cleanup, it is a regression.

## The four kinds

Compare each token against the config default of the group it targets, and count how many launchers
selecting that same group pass it.

| kind | test | verdict |
|---|---|---|
| **redundant** | value EQUALS the config default | delete, it does nothing |
| **missing default** | ALL launchers selecting that group pass the same value | move it into the group config |
| **per-run delta** | SOME launchers pass it, others take the default | correct, leave it |
| **selector** | it names an owned component (`pipeline.reward=`, `memory.writer=`) | correct, this is the sanctioned swap path |

The count is what separates the middle two, and it is the whole diagnostic. **Every launcher of a
pipeline passing `pipeline.backend=fsdp` means the config's default is simply wrong.** Four of twenty
passing `batch_size=8` means those four runs deliberately differ, which is what a launcher is for.

Redundant is the most common and the least noticed, because it is invisible: the run is correct, the
line is just noise, and nobody reads a submit line closely enough to spot a value that matches the
default it overrides.

## What is ALWAYS an override, however often it appears

A value the (pipeline, model, dataset) triple genuinely cannot express, and that changes per
submission rather than per configuration. The canonical case is **scoring N checkpoints of one run in
parallel**: same pipeline, same model, same dataset, same decoding, and only the checkpoint moves.

    pipeline.checkpoint_path=<...>/checkpoint_step_2000
    pipeline.checkpoint_path=<...>/checkpoint_step_4000

Making that a config would mint a config file per checkpoint step, which is a file per artifact rather
than per decision. It appears in every launcher of its kind and is still correct, so the
"all launchers pass it" test does NOT apply to it. Ask instead: *does this name a choice, or an
instance?* A choice belongs in config, an instance belongs on the command line.

Distinguish these at submit time by deriving the job name from the override, never by minting a
launcher per checkpoint (`eval-launchers.md`).

## Smoke runs

`naming-config` settles this: a pre-flight is the same arm with the dataset `tag` slot set
(`dataset_name=healthbench_smoke`) and a short schedule passed as ordinary overrides. The subset is a
named config because it changes WHAT is measured. The schedule stays an override because it changes
only how long, and because making it a config forces a second coordinated selection.

That coordination is the real argument. "Smoke" spans two groups, small data in `dataset` and short
schedule in `pipeline`, so a fully-config smoke arm needs `pipeline_name=..._smoke` AND
`dataset_name=..._smoke` selected together. They can desync, and the dangerous direction is silent:
the full pipeline on the smoke dataset is a full-length run on 50 examples that reads as real.

Going fully-config is still legitimate, on one condition: add a check that a `_smoke` pipeline may
only pair with a `_smoke` dataset. With that check the desync is impossible and config wins. Without
it, overrides are safer.

## Do not audit a submit line by eye

Both classifications need the config default and a count across launchers, so grep for the leaf key in
the group config and count launchers selecting that group. Doing it by eye finds the long lines and
misses the redundant ones, which are the ones actually costing nothing but confusion.
