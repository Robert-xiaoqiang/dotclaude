# Failure recovery

Read when something broke. Failure is the normal state of a long campaign, not an exception to it.

## The sequence
1. **Capture evidence first.** The failing command, the exit code, the last 100 log lines from the
   *failing rank*, the run dir path, the config path, and the code revision. Do this before any fix
   attempt, because a retry frequently overwrites the log that explains the first failure.
2. **Classify** with the table below. The class determines who can fix it and how expensive the fix is.
3. **Name the root cause, not the symptom.** `CUDA out of memory` is a symptom. The cause is a batch
   size, a sequence length, a missing `no_grad`, an unfreed cache, or an eval running at train batch
   size. Until you can name which, any fix is a guess.
4. **Propose the smallest credible fix.** One change, addressing the named cause.
5. **Validate at the cheapest rung that can prove it** (the scale ladder in `SKILL.md`). A fix for an
   OOM at step 3 does not need a full run to test.
6. **Retry the stage**, then record the outcome in `journal.md` whether or not it worked.

A failed attempt that you record is worth more than one you silently retry, because the next session
does not repeat it.

## Classification
| class | tell | typical fix |
|---|---|---|
| **implementation** | stack trace in project code, wrong shapes, wrong dtype | fix code, add a test at the boundary that broke |
| **configuration** | wrong path, missing key, a value the framework silently defaulted | fix the config, then check what *else* was defaulted |
| **data** | shape or encoding errors, empty splits, count mismatch | inspect raw examples, assert the count |
| **environment** | import errors, ABI or driver mismatch, missing binary | `platform-runtime` — match driver × image × venv |
| **infrastructure** | pod evicted, node lost, quota exceeded, filesystem timeout | resubmit, usually no code change |
| **OOM** | allocator error, or the OOM killer | reduce batch, shorten sequence, enable checkpointing, or fix a leak |
| **numerical** | `NaN`/`Inf`, loss spike, gradient explosion | lower LR, clip, check the loss for `log(0)` or a divide by zero |
| **checkpoint** | load fails, or a size-zero or partial file | fall back to the previous checkpoint, check the disk |
| **evaluation** | eval crashes, or produces impossible numbers | `references/evaluation-integrity.md` |
| **aggregation** | metrics disagree between scripts, wrong denominator | audit the metric code before blaming the method |
| **methodological** | everything ran correctly and the result is simply worse | not a bug — `references/iteration.md` |

The last row matters most. **A valid run that misses target is not a failure to recover from**, it is
evidence. Treating it as a bug wastes hours hunting a defect that is not there.

## Retry budget
Default budgets, unless `plan.md` sets others.

| class | attempts | then |
|---|---|---|
| infrastructure | 3 | check quota and node health before a fourth |
| config / data / implementation | 2 per distinct hypothesis | if both fail, the hypothesis is wrong, not the fix |
| OOM | 2 (each a real reduction) | drop to a diagnostic scale and measure actual memory |
| numerical | 2 | reduce to a minimal reproduction |
| same command, unchanged | **0** | never |

**A retry requires a changed condition.** Re-running the identical command against the identical state
is not a retry, it is a wish. The one exception is a documented transient (a node failure, a network
timeout), and that still counts against the infrastructure budget.

When a budget is exhausted, do not escalate the scale. **Shrink the problem** into a minimal
reproduction that runs in minutes, then debug that. If it still resists, search for the error text and
the library's issue tracker (`references/iteration.md`), and if that is dry, record a blocker with the
minimal reproduction attached and move to independent work.

## Guardrails during recovery
- **Never delete a checkpoint or a result to unblock yourself.** Move it, or write elsewhere.
- **Never widen a fix beyond its cause.** "Refactor the trainer" to fix a config typo destroys the
  comparability of everything already run.
- **Never disable an assertion to make a job proceed.** The assertion is the only thing standing
  between you and eight hours of invalid results. Fix what it caught.
- **Never lower a metric's standard to make a result look valid** — do not shrink an eval set, drop
  failing examples, or switch metric definitions in response to a bad number.
- **Re-verify the environment after any infrastructure failure.** A relaunched pod can come back with a
  different driver, image, or mount state (`platform-runtime`).
