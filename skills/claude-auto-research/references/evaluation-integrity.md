# Evaluation integrity

Read before trusting any number, and before every final evaluation.

## The rule
**Evaluate on the full benchmark, always.** Never quietly substitute a hand-picked, shortened, easier,
or "representative" subset for the benchmark the plan named.

A subset is legitimate for exactly four purposes, and each must be labelled as such wherever the number
appears: smoke-testing the eval pipeline, debugging a known failure, verifying that a fix works, and
rapid diagnosis. A subset result is a **diagnostic**, never a benchmark result, and it never enters
`report.md` as one.

**The mechanism, not a promise.** `naming-config` makes this enforceable: a subset is a named dataset
config using the `tag` slot (`dataset_name=healthbench_smoke`), so it produces its own hashed run dir
and its own frozen `config.yaml`. A subset evaluated that way is *physically* distinguishable from the
full bench forever after. A `--limit 50` passed at the CLI is invisible in `config.yaml`, and six hours
later nothing on disk can tell you which of two numbers was the real one.

So the check is mechanical: **if the run dir does not record the eval scope, the eval does not count.**

Unless `plan.md` explicitly says otherwise, a final evaluation uses the complete benchmark, the
official split, the full example count, the normal decoding or rollout settings, the planned number of
seeds, the project's standard metric code, and every baseline the comparison needs.

## Pre-flight checklist
Verify each before believing a number. Most are one command.

1. **Right weights.** The loaded checkpoint path appears in the log and matches the run you intended.
   Not the config's default, not the base model.
2. **Right code.** The revision under evaluation is the one that produced the checkpoint.
3. **Right split.** The official test or validation split, not the training data, and not a split the
   model was tuned against.
4. **Complete coverage.** Processed count equals the benchmark's expected count. Compare the number,
   do not eyeball the file.
5. **No silent drops.** Failed or malformed generations are counted as failures, not skipped. Skipping
   inflates every score.
6. **Right denominator.** The metric divides by the intended total, not by the number that happened to
   parse.
7. **Fresh outputs.** No stale cache. Prediction file mtimes postdate the launch.
8. **Matching decoding.** Temperature, top-p, max tokens, stop sequences, and sample count are what the
   plan specified. Greedy versus sampled is often a larger effect than the method under test.
9. **Shards merged.** In a distributed eval, every rank's shard is present and the merge is complete.
   A missing shard usually looks like a plausible score on a smaller set.
10. **Parseable results.** `summary.json` exists, parses, and its fields carry the expected types.

## Suspicious results
Treat each as a pipeline bug until proven otherwise. **Audit before concluding anything about the
method**, because a methodological conclusion drawn from a broken pipeline costs days.

- A score at exactly 0.0 or 1.0, or suspiciously round.
- A jump far larger than the intervention could plausibly cause.
- Identical scores across different checkpoints — usually the same weights loaded twice.
- An eval that finished far faster than expected — usually a truncated set.
- Example counts that differ between arms, or from the benchmark's published size.
- Two scripts disagreeing on the same predictions — the metric code is wrong somewhere.
- A trained model scoring exactly like the base model.
- Variance across seeds far below what the benchmark normally shows.

The audit order: read raw predictions first (do the outputs look like the task?), then counts, then the
config actually used, then the metric code. Reading the generations first resolves most of these in a
minute, and it is the step most often skipped.

## Comparison discipline
A number without a baseline is not a result. Every reported score carries the baseline it is measured
against and the target from `plan.md`, evaluated under **identical** conditions: same bench, same
split, same decoding, same metric code, same seeds.

Report variance whenever seeds allow it. A 0.4-point gain with a 1.5-point seed spread is noise, and
calling it an improvement will send the next iteration chasing nothing.

State the eval scope next to every number you write down. `full` or `smoke(n=50)` is enough, and it
removes the single most common source of confusion after a long unattended run.
