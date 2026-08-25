---
name: claude-debrief
description: "Report back to a person who left work running and has just returned: what is alive right now, what the numbers say, what broke and whether the fix is verified, what needs a decision, and what happens next if they say nothing. Orders the answer by what the reader must act on, not by the order things happened."
when_to_use: "Use on returning after hours or overnight, and on any request like what happened, catch me up, summarize, status, or how did it go. Also use before handing a campaign to another session."
---
# Skill: claude-debrief

## Purpose
Someone left a plan running and came back. Their first question is never "what did you do", it is
**"do I need to do something right now"**, followed by "did it work" and "what is it costing me".
A debrief answers in that order and grounds every claim in something the reader can open.

The failure this guards against is the diary: a chronological narration of what the agent did, in
which the one job that died at 03:00 appears in paragraph four, the fix that was never verified reads
identically to the fixes that were, and the reader has to reconstruct the current state themselves.
Effort spent is not the subject. **The current state of the world is the subject.**

## When to Use
- The user returns after being away and asks what happened, in any phrasing.
- A long-running campaign reaches a checkpoint, a stage boundary, or a stopping condition.
- Before handing a campaign to another session, so the next reader inherits state rather than history.
- Any time the honest answer to "is this still working" is longer than one line.

## Contents
- [Not the ledger, not the weekly report](#not-the-ledger-not-the-weekly-report)
- [The shape](#the-shape)
- [Evidence discipline](#evidence-discipline)
- [Verify before you report](#verify-before-you-report)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## Not the ledger, not the weekly report
Three artifacts describe the same campaign and none substitutes for the others.

The **ledger** (`claude-auto-research`) is `state.md`, `journal.md`, `experiments.md` and `jobs.md`. It
is written so a cold session can resume, so it is complete, append-only, and indifferent to what
matters most. A debrief that pastes `state.md` has answered a question nobody asked.

The **weekly report** (`docs-weekly`) is a deliverable for a meeting. It carries an argument about
research direction over a week, and it is written once the results are settled.

The **debrief** is spoken to one person at one moment, and its job is **selection**: which of the many
true facts in the ledger this reader needs in the next sixty seconds. It is not persisted unless asked.
Read the ledger to write it, never instead of writing it.

## The shape
Six blocks, in this order. The order is the skill. Skip a block only when it is genuinely empty, and
say so in one clause rather than deleting the heading silently.

**1. The verdict.** One sentence: is the campaign healthy, degraded, or stopped, and is anything
waiting on the user. A reader who stops here has the truth, just at low resolution. "Three of four
arms are training normally, the fourth died on an OOM and is not restarted, and nothing needs you."

**2. What needs you.** Decisions, blockers, and anything irreversible that was deliberately not done.
Put it second because it is the only time-sensitive part. State the question, the options, and what
happens if the user says nothing. If nothing needs them, say "nothing needs you" and move on. Never
bury a blocker below results.

**3. Running now.** The live state, with identifiers the reader can paste: job ids, cluster, what
stage each is in, and the evidence that each is progressing rather than merely scheduled. Queued and
dead jobs belong here too, because a queue that has not moved in six hours is a finding.

**4. Results.** Numbers with the comparison that makes them mean something, and the seed count in the
same sentence. A number with no baseline is not a result. If nothing has finished, say what will
produce the first number and when.

**5. What broke, and what was done.** Each failure gets the symptom, the root cause if it is known,
the fix, and **whether the fix is verified and by what**. An unverified fix is labelled unverified.
Group repeats rather than listing each occurrence.

**6. Next.** What happens if the user says nothing. This is a commitment, not a wish list, and it
should be short enough that the reader can veto one item without unpicking the rest.

## Evidence discipline
**Every factual claim carries the thing it came from.** A job id, a run dir, a log path, a metric file.
A reader who cannot check a claim in one command has to trust it, and the entire value of a debrief is
that it does not require trust.

**Separate what was observed from what was inferred.** "The loss curve is flat since step 400"
is an observation. "Training has converged" is an inference, and it may be wrong for three reasons
that the observation does not distinguish. Write both, marked, or write only the observation.

**Report what did not happen.** This is the block most often missing and the one that costs most. A
sweep that was meant to launch eight arms and launched six is not "the sweep is running". An eval that
skipped two of ten benchmarks because a dataset path was stale reports nine of ten, and nobody notices
until the table is short. Say the intended count, the actual count, and the difference.

**Report cost.** Accelerator-hours consumed since the last debrief, and how much of it was wasted on
runs that failed or were superseded. A campaign that is technically healthy while burning a pool on a
misconfigured arm is not healthy, and the cost line is what surfaces that.

**Never round a failure into a success.** "Mostly working", "largely complete" and "should be fine"
are the three phrases that end up in an incident review. Give the count.

## Verify before you report
The state you report must be the state of the world at the moment you report it, not the state you
last believed. Four checks, each of which has produced a wrong debrief:

**A status field is not progress.** A job whose status reads `Running` may have been stuck since its
first step. Confirm progress from the run's own output, a recent step count or a file written in the
last few minutes, before reporting it as training.

**A paginated listing is not the whole list.** Job listings default to a small page. Concluding that
something is absent from page one is how a serving job that had been up for six days got reported as
not existing. Pass an explicit page size and a status filter before saying anything is gone.

**A command that printed nothing did not necessarily succeed.** A stop or submit with a wrong flag can
exit quietly having done nothing at all. Re-query the state afterwards and report the queried state,
not the command's exit.

**Timestamps need arithmetic, not intuition.** Boxes disagree on clock and timezone, and some `find`
implementations silently accept a relative time expression they do not honour. Compare epoch seconds
when liveness matters, and pair it with a second independent signal before calling anything dead.

## Rules
1. **Order by what the reader must act on**, never by when things happened.
2. **Lead with a one-sentence verdict** that a reader can stop after.
3. **Blockers and decisions come second**, above results, always.
4. **Every claim carries an id or a path** the reader can open.
5. **Label an inference as an inference**, and prefer the observation.
6. **State intended versus actual counts** for every sweep, launch, and eval.
7. **A fix is reported with how it was verified**, or explicitly as unverified.
8. **Numbers carry their baseline and their seed count** in the same sentence.
9. **Report accelerator-hours since the last debrief**, including the wasted share.
10. **Re-query the world before reporting it.** A status field, a quiet command, and page one of a
    listing are all insufficient on their own.
11. **Say what you deliberately did not do**, especially anything irreversible you left for the user.
12. **End with what happens if the user says nothing.**

## Anti-patterns
- **The diary.** "First I checked the logs, then I noticed, then I tried." Nobody needs the search
  path. Give the finding.
- **The ledger dump.** Pasting `state.md` or a job table with no selection and no verdict.
- **The buried blocker.** A decision the user must make, placed after three paragraphs of results, so
  a skimming reader misses it and the campaign idles another eight hours.
- **The unqualified fix.** "Fixed the OOM" with no statement of whether anything has run since.
- **The naked number.** "47.65 on the suite" with no baseline, no target, and no seed count.
- **Silent partial success.** Reporting a sweep as running when two arms never launched.
- **Effort as achievement.** Hours spent, files read, and commands run are not results.
- **The confident stale claim.** Reporting a job as alive from a status read hours ago.

## Companions
`claude-auto-research` (owns the campaign and the durable ledger this reads from) · `output-analysis`
(produces the comparisons a results block cites) · `layout-output` (where a run's evidence lives, so a
claim can name a path) · `docs-weekly` (the meeting deliverable, written from settled results) ·
`writing-style` (the prose rules, when a debrief is written down rather than spoken).
