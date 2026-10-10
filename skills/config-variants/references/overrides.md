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
| **selector** | it names an owned component (`pipeline.reward=`, `memory.writer=`) | correct, this is the sanctioned swap path (owned components are `config-composition`'s) |

The count is what separates the middle two, and it is the whole diagnostic. **Every launcher of a
pipeline passing `pipeline.backend=fsdp` means the config's default is simply wrong.** Four of twenty
passing `batch_size=8` means those four runs deliberately differ, which is what a launcher is for.

Redundant is the most common and the least noticed, because it is invisible: the run is correct, the
line is just noise, and nobody reads a submit line closely enough to spot a value that matches the
default it overrides.

## The exception to the count

A value that names an instance rather than a choice is an overlay however often it appears, so the
"all launchers pass it" test does not apply to it. The canonical case is the checkpoint of an eval
grid, `model.init_kwargs.path=<...>/checkpoint-N`, which every cell passes and which is still correct
on the command line. The full statement, and how each cell's job is named, is The grid pattern in
[../SKILL.md](../SKILL.md#the-grid-pattern).

## Smoke runs

A smoke's short schedule is a per-run delta of its smoke launcher or its invocation, never a missing
default of the pipeline. Where it lives, and when a fully-config smoke is safe, is Smoke in
[../SKILL.md](../SKILL.md#smoke).

## Do not audit a submit line by eye

Both classifications need the config default and a count across launchers, so grep for the leaf key in
the group config and count launchers selecting that group. Doing it by eye finds the long lines and
misses the redundant ones, which are the ones actually costing nothing but confusion.
