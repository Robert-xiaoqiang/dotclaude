# Monitoring a running job

Read while a job is in flight, and after any long gap.

## Alive is not the same as progressing
The default failure of an unattended run is not a crash, which is loud and leaves a stack trace. It is
a job that stays *alive* and stops *advancing*. Every check below exists to separate the two.

The minimum signal of health is **the step counter moved since the last inspection**. A process in `R`
state, a pod in `Running`, and a job in `RUNNING` all mean nothing on their own.

## Cadence
Poll on the timescale of the thing you are watching, not on a timer.

| job length | check every | rationale |
|---|---|---|
| minutes (smoke) | on completion | watch it directly, it is a gate |
| 1–4 h | 15–30 min | early divergence is still cheap to kill |
| 8–48 h | 1–2 h | enough to catch a stall inside one checkpoint interval |
| queued / pending | 30 min | you are watching the scheduler, not the job |

Two adjustments. Check more often for the **first 20 minutes** of any full run, since most failures
(OOM, shape errors, a bad data path) surface early and killing early saves the whole allocation. Check
less often once a run has been stable for hours with a healthy loss curve.

Never busy-poll a multi-hour job. It burns context you will need for diagnosis, and it teaches you
nothing a sparser check would not.

## What to inspect, in order
Cheapest and most decisive first, so you stop as soon as you have the answer.

1. **Liveness** — scheduler state, pod phase, or PID. Distinguish `PENDING` from `RUNNING` from gone.
2. **Step progress** — the tail of `metrics.jsonl` or the log. Compare the step against the previous
   inspection. No movement is the alarm.
3. **Loss and reward** — trending, flat, exploding, or `NaN`/`Inf`. A `NaN` that does not crash the job
   is worse than one that does, because the run keeps burning GPU on garbage.
4. **Throughput** — steps/sec or tokens/sec against the smoke run's rate. A silent 5× slowdown is
   usually a dataloader stall, a filesystem stall, or a fallback to a slower kernel.
5. **Checkpoints** — is one appearing on schedule, is it complete (marker files, non-zero size), and is
   `last` advancing (`layout-output`).
6. **Resources** — GPU utilization and memory, host RAM, and **disk**. A full `$OUTPUT_DIR_HOME` fails
   the next checkpoint write and often only shows up as a truncated file.
7. **The tail of stderr** — warnings that repeat every step are usually the cause of item 4.

## The silent failures
These do not raise, so nothing but a deliberate check will find them.

- **Collective mismatch.** In distributed training every logged metric key becomes a collective. If one
  rank logs a key the others do not (an `if` around a metric, a reward that only fires on some batches),
  the ranks wait on different gathers and the job hangs with **no error and full GPU memory**. The tell
  is zero step progress with all ranks alive. Make the logged key set identical on every rank and
  unconditional, then re-launch.
- **Early exit reported as success.** A wrapper swallows a non-zero exit, or the process ends at step 0
  after the dataloader yielded nothing. Check the step count *and* the exit code, and treat a run with
  no `DONE` marker and no checkpoint as failed regardless of what the scheduler says.
- **Silent example dropping.** Data loading skips malformed rows inside a `try`. Sample counts shrink
  and every downstream metric quietly uses a smaller denominator. Assert the count.
- **Stale reuse.** A cached dataset, a resumed run picking up an old checkpoint, or an eval reading a
  previous prediction file. Check mtimes against the launch time.
- **Wrong weights.** Training or evaluating the base model because a checkpoint path silently fell back
  to the pretrained default. Verify the loaded path in the log, not in the config.
- **Throughput decay.** Gradual slowdown from memory fragmentation, a growing log, or a leaking cache.
  Visible only by comparing against an earlier rate.
- **Deadlock at a barrier.** One rank crashed while the rest wait forever. Check *every* rank's log,
  not just rank 0, which is usually the only one that looks fine.

## Recording what you saw
Write to `jobs.md` on every inspection: the timestamp, the observed step, and the status. That column
is what tells the next session whether the job is stalled or merely slow, which is otherwise
unrecoverable after a context reset.

Put a *change* in `journal.md` (it stalled, it diverged, you killed it). Do not put routine healthy
polls there, since a journal of "still fine" is a journal nobody rereads.
