# Iteration and research

Read when a run was valid but missed target, or when the next move is not obvious.

## One iteration
1. **Name the bottleneck.** What specifically limits the metric — capability, data, optimization,
   reward shape, inference, or evaluation? Point at evidence: a curve, a failure breakdown, a sample.
2. **State a hypothesis** that could be wrong. "Longer training helps" is not a hypothesis. "Reward
   saturates by step 800, so the policy stops receiving gradient signal" is.
3. **Design the smallest experiment that can falsify it**, and say in advance what result would kill
   the hypothesis. An experiment with no disconfirming outcome is not an experiment.
4. **Hold the baseline fixed** and change one major factor.
5. **Run, evaluate at the required scale, compare** (`references/evaluation-integrity.md`).
6. **Record the conclusion in `experiments.md`, including the negative ones.** A recorded failure stops
   the next session repeating it, which is most of what an unattended campaign's memory is for.
7. **Keep, revert, or revise.** Never leave an unevaluated change in the tree.

## Arms differ in one slot
Two arms being compared should differ in exactly the config slots that describe the change
(`naming-config` symmetry). If arm B also picked up a longer schedule and a different seed, the
comparison measures nothing, and no amount of later analysis recovers it.

**A hand-crafted fix is not a research arm.** Patching the specific failure you observed proves only
that you can patch it. When comparing against prior work, put a *faithful implementation of the
published method* on the middle rung, so the ladder reads: baseline → published method → your method.
Skipping the middle rung makes any gain unattributable.

Ablations belong in one group directory as small deltas, never as forked copies of a large config
(`layout-workspace` principle 4). Copies drift, and the drift is silent.

## What to iterate on
Order by expected effect per GPU-hour, and re-derive the order from your own failure analysis rather
than working down this list: data construction and quality, reward or objective shape, the training
recipe (schedule, LR, batch), inference and decoding strategy, prompt or agent policy, curriculum and
sampling, architecture, and distributed performance.

Two cautions. Hyperparameter sweeps are the *last* resort, not the first, since they consume the most
compute and teach the least. And a change that helps a smoke run frequently does nothing at scale, so
never conclude from the smoke rung alone.

## Knowing when to stop iterating
Escalate from tuning to redesign when two or three well-motivated iterations move the metric by less
than the seed variance, or when failure analysis points at something the current design structurally
cannot do. Record that judgement in `journal.md` with the evidence, since it is the decision a returning
user will most want to see reasoned.

## Research
Search when you are about to guess. Specifically: an unfamiliar error, a dependency behaving unlike its
documentation, an implementation pattern you are inventing from scratch, a bottleneck a known algorithm
probably solves, a method underperforming its published numbers, or an evaluation convention you are
unsure of.

Prefer, in order: official documentation, then the upstream **source code** (which settles behaviour
questions that docs leave ambiguous), then the original paper, then the project's issue tracker, then
reputable implementations. For "why does this library do X", the source and the issue tracker beat every
secondary explanation.

**Research must terminate in an action.** For each useful finding record the source, the specific claim,
why it applies here, what you will change, and the outcome after testing it. A literature summary with
no experiment attached is not progress, and it does not belong in the campaign ledger.

Time-box it. If an hour of searching yields no actionable change, fall back to reducing the problem to
a minimal reproduction, which usually answers the question faster than more reading.
