# Directions

Read when starting a campaign, when a stage changes direction, or when the next action is unclear.

The direction decides what evidence closes the work. Get it wrong and a campaign can run for two days,
produce correct numbers, and answer a question nobody asked.

## insight — move forward
**Question:** why is this happening, and what does it change?
**Closes on:** a claim that survived an attempt to kill it, *and* the decision it unblocks.

The point is forward motion. Understanding that leaves the plan unchanged is trivia however true it is,
so record every finding together with what it makes you do next. If nothing follows, the question was
not the bottleneck and you should keep digging.

How to run it. Instrument before retraining, since most questions are answered by looking harder at
runs you already have. Prefer many cheap probes to one expensive run. State the claim, then design the
observation that would *falsify* it, and go looking for that. A claim earns belief by surviving, not by
accumulating agreeable evidence. Check it across seeds and checkpoints, because a single curve is an
anecdote.

Failure modes: telling a story from one training curve, gathering only confirming evidence, describing
*what* happened and calling it *why*, and the big one, finishing with a fascinating explanation that
changes nothing.

Report leads with the claim, the evidence that could have killed it, the decision it drove, and what it
does not explain.

## grind — performance
**Question:** can the number go up, and does the gain survive contact with a full evaluation?
**Closes on:** a gain over the baseline larger than seed variance, on the full benchmark.

How to run it. Freeze the baseline and never retune it downward. Reproduce any gain with a second seed
before claiming it, since a single-seed improvement inside the variance is the most common false result
in the whole loop. Evaluate per `evaluation-integrity.md`, at full scope, every time. Define diminishing
returns in `plan.md` up front so there is a stopping rule that is not "the user woke up".

Keep the fair-comparison ladder: baseline, then a faithful implementation of the published method, then
yours. A hand-crafted fix stacked on a weak baseline is not a gain, it is a stronger baseline you failed
to run.

Failure modes: a cherry-picked seed, tuning the proposal while leaving the baseline untuned, selecting
repeatedly on the evaluation set until the number is optimistic, and a gain that evaporates at a
different scale.

Report leads with the number, its variance, its scope, and the baseline it beat.

## ablation — attribution
**Question:** which component is responsible for the effect?
**Closes on:** a complete table whose arms differ in exactly one slot, including the arm that removes
the component entirely.

How to run it. Arms differ in one config slot and nothing else (`naming-config` symmetry). Identical
budget, identical scale, and the same seeds across arms wherever possible, because an arm that trained
longer is not an ablation. Run the arms you expect to lose, not only the ones you expect to win.

The removal arm is the one most often skipped and the most informative. "Component X plus everything
else" versus "everything else" is the actual question, and without it the table shows correlation among
variants rather than attribution.

A component that turns out to do nothing is a genuine result. Report it.

Failure modes: two things changed per arm so no row means anything, no removal arm, arms compared at
different budgets, and stopping once a favourable row appears.

Report leads with the table, then the one-sentence attribution it supports.

## design — build it
**Question:** can this be built, and does it work at the intended scale?
**Closes on:** it runs at the planned scale, meets the spec, and its outputs pass validation.

How to run it. Build the smallest thing that tests the idea, not the general framework it might one day
need. Climb the scale ladder in order, since most design faults surface at the smoke rung for a
thousandth of the cost. Correctness before speed. Put assertions around every fragile assumption,
because nobody is watching. Fit the existing architecture (`layout-workspace`) rather than growing a
parallel one beside it.

Verify the code path you tested is the path a real run takes. A design validated through a debug branch
that production never executes is not validated.

Failure modes: infrastructure the experiment does not need, a design confirmed only at toy scale, and a
tested path that differs from the executed one.

Report leads with what was built, where it lives, and the evidence it works.

## formulation — elegant or novel, and empirically validated
**Question:** is there a cleaner, more principled, or more general statement of this?
**Closes on:** measured parity or better against the incumbent, at lower complexity or wider scope.

**Elegance is a claim, and claims need runs.** This is the direction most likely to produce a beautiful
argument and no evidence. Paired runs against the thing being replaced are what settle it, and until
those exist the work is a proposal rather than a result.

How to run it. Show parity before claiming an advantage, since a reformulation that quietly costs two
points is a different trade and must be reported as one. Where possible, derive the incumbent as a
special case of your formulation, which is the strongest available argument for generality. Then make
the simplification concrete and countable: fewer moving parts, fewer hyperparameters, one loss instead
of three, or a case the incumbent cannot express at all. Check the literature before claiming novelty
(`iteration.md`), because an independently rediscovered method is still worth having but must be named
correctly.

If it does cost performance, say by how much and argue the trade explicitly. That is a legitimate
result. Silence about it is not.

Failure modes: aesthetic claims with nothing measured, a "simpler" method that introduces more
hyperparameters than it removes, never running the incumbent under identical conditions, and asserting
novelty without a search.

Report leads with the formulation, the parity evidence, and the concrete simplification or added
generality.

## Sequencing
Real campaigns chain directions: design a mechanism, ablate to find what carries the effect, grind the
survivor, and extract the insight that motivates the next one. Give each its own stage with its own
closing evidence in `plan.md`. A stage that inherits the previous stage's success criterion has quietly
changed direction, which is the drift `SKILL.md` warns about.

When directions conflict, the plan's primary direction wins, and the conflict goes in `journal.md`.
