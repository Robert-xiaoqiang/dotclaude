# Report: <topic>

Campaign <YYYY-MM-DD> to <YYYY-MM-DD>. Plan: `./plan.md`

> Written for a user returning after being away. Lead with the answer, and be honest about what did
> not work. Every number carries its scope and its run dir, so any claim can be checked in one command.

## Outcome
<Two or three sentences. Did the objective succeed, partially succeed, or fail, and on what evidence.>

## Results
| arm | metric | result | scope | seeds | vs baseline | vs target | run dir |
|---|---|---|---|---|---|---|---|
| baseline | <metric@bench> | <value> | full | <n> | — | <delta> | `<path>` |
| published method | <metric@bench> | <value> | full | <n> | <delta> | <delta> | `<path>` |
| ours | <metric@bench> | <value> | full | <n> | <delta> | <delta> | `<path>` |

Evaluation scope: <benchmark, split, example count, decoding settings, metric code>. Any number below
full scope is labelled and is not a benchmark result.

## What was built
<The implementation, in terms of the repo: which modules, which config groups, which launchers. Point
at paths, not descriptions.>

## Experiments
<Summary of `experiments.md`: how many ran, what the decisive ones showed. Include the negative results,
which are usually the more useful half.>

## Jobs and artifacts
| stage | job | run dir | checkpoint kept | status |
|---|---|---|---|---|

## Bugs found and fixed
| bug | class | how it surfaced | fix | what it would have invalidated |
|---|---|---|---|---|

The last column matters: a bug caught after eight hours of training is a different story from one
caught at the smoke rung, and it tells the user how much to trust the earlier stages.

## What did not work
<Approaches tried and abandoned, with the evidence that killed each. This is the section that saves the
next campaign the most time, so do not compress it away.>

## Design decisions
<Non-obvious choices and why. Anything durable about the architecture graduates to `docs/ARCH.md`
(`docs-arch`) rather than living only here.>

## Limitations
<What the results do not show. Untested conditions, single-seed numbers, scope shortfalls, known
confounds.>

## Recommended next
<The next stage or campaign, with the reasoning. If blocked, exactly what is needed.>

## Reproduction
```bash
# environment
<venv / image / driver, per platform-runtime>

# the decisive run
<exact submit command>

# the evaluation
<exact eval command>
```
Commands are copy-pasteable as written. A reproduction section that needs interpretation is not one.
