# What forks an eval pipeline

An eval family grows one config per experiment unless something says where a new one is allowed to
come from. Without that rule the tree fills with names like `eval_unified`, `eval_sweep`,
`eval_final_v2` — each naming the author's convenience or budget rather than a property of the
measurement, and each indistinguishable from the others a month later.

## The seven axes

Every evaluation varies along exactly these, and each belongs to a different owner.

| # | axis | the question it answers | where it lives |
|---|---|---|---|
| 1 | **corpus** | which items are evaluated | `dataset` group |
| 2 | **policy + decoder** | how tokens come out of the model | `model` group |
| 3 | **sampling** | how many samples, how random | `pipeline.eval.generation` |
| 4 | **protocol** | what ONE attempt consists of | the pipeline FLAVOUR |
| 5 | **reduction** | k samples → one verdict | `pipeline.eval.reduce` |
| 6 | **scorer** | verdict → number | `pipeline.eval.score` |
| 7 | **state carry** | may item *i* depend on items `< i` | `pipeline.eval.state` |

## The fork rule

> A change forks the **pipeline** only if it changes **what one attempt consists of** — its control
> flow. A change of how an attempt becomes a number is a **scorer**. A change of how many attempts is
> **sampling**. A change of which rows is a **dataset**. A change of how tokens are produced is a
> **model**.

Applied:

| change | verdict |
|---|---|
| accuracy vs BLEU vs BERTScore vs LLM-judge | scorer |
| greedy vs temperature 0.8 | sampling |
| self-consistency-8 vs pass@8 | same protocol (n=8), different **reduction** |
| single-turn vs multi-turn with an environment | **different protocol** — new pipeline |
| pass@k with an execution sandbox | **different protocol** — new pipeline |
| AR vs MDM vs diffusion policy | model |
| full bench vs subsampled bench | dataset (the `tag` slot: `mini` / `smoke` / `toy`) |

So the pipeline name should say the **protocol** — and it must also carry the base it derives from.
If the scorer subfamilies are `eval_ar_choice` / `eval_ar_graded`, a protocol subfamily is
`eval_ar_single_turn_suite`, later `eval_ar_multi_turn_suite` when there is an environment to talk
to. Dropping the `ar` makes the one pipeline you actually run the only one whose base you cannot
read off its name. The name must not say how much of each bench was scored — that is the corpus, and
the corpus has a tag slot for exactly this.

**Make the protocol a component group, not just a name.** Code at `<pkg>/pipeline/eval/protocol/`,
configs mirroring at `config/pipeline/eval/protocol/`, mounted at `pipeline.eval.protocol`. Then a
pipeline is an assembly — `eval_ar_k_consistency_suite` is `eval_ar_single_turn_suite` with one slot
moved — and the arms of a protocol comparison sit one config slot apart instead of being separate
near-duplicate pipelines. Give the base class the invariants its subclasses must not break: that a
record reaches the sink only once scored, and that a protocol declaring `carries_state` refuses to
be sharded (two ranks would accumulate two histories and report two measurements under one name).

## Three traps

**Decoding is not an eval axis.** AR, MTP, MDM and diffusion are *model classes*. The loop should
depend on a contract — `policy.generate(records, **sampling) -> completions` — and never on how the
tokens were produced, or every new decoder forks the eval family for no measurement reason. The one
thing that would justify an eval-side fork is decoder-specific *instrumentation*, and that is a
different measurement, not a different decoder.

**State carry deserves its own name.** "The sampler accumulates experience" sounds like a loading
concern; it is not. If item *i* may depend on items before it, the score depends on item ORDER, two
shards disagree, and resume stops being idempotent. Naming it (`state: none | accumulating`) means an
arm that carries memory cannot be averaged as if it were i.i.d. without someone having written that
down.

**A bench list in the pipeline config is fine.** One dataset *config* per run is a launcher-triple
convention (so the run dir carries one dataset segment), not a prohibition on a pipeline iterating
over benches. Each bench already IS a dataset config selected by name, so a suite that walks a list
of `{dataset, score}` pairs keeps the corpora as dataset-group citizens. The pairing is the one fact
a launcher cannot derive — a banded corpus through a met/not-met scorer yields a plausible near-zero
and no error — so it belongs beside the list.

## Do not pre-build the unused rungs

Define the **contracts** fully — `generate`, the scorer's `__call__(records) -> scores`, a `reduce`
contract, and the naming grammar above — so that a new rung is a config plus one class. Then stop.

A registered-but-unbuilt component is worse than an absent one, because its name in a config is a
claim that something happened. The instance that taught this: a `query` component was registered in
one group table and missing from another, so it built nothing while preflight cheerfully printed
`query resolved to a component ok`, and four launched arms silently became their own control.

Add `reduce` when the first n>1 arm needs it. Add the multi-turn protocol when there is an
environment. The abstraction is the deliverable; the rungs are not.

**But if you do build a rung ahead of its use, it must run or REFUSE.** Those are the only two honest
states. A multi-turn protocol with no environment should raise at construction, naming what is
missing and what to use instead — never quietly become a one-turn eval that reports plausible
numbers under the multi-turn name. Then have a check instantiate every rung's config and assert that
each one either constructs or refuses with an actionable message; that check is what keeps
"not wired yet" from decaying into "silently does nothing".

## Auditing is not a mode of evaluating

"Which benches did this checkpoint actually score?" is a question *about* evaluations, answerable
from the output tree alone. Making it `pipeline.eval.mode: run | audit | repair` puts a branch in the
pipeline that selects behaviour, and forces a GPU, a policy load and a judge into answering a
filesystem question. Write a separate read-only script, and let it emit work into whatever queue the
submission guard already drains rather than submitting anything itself.

Companions: `naming-config` (the slot grammar and the `tag` slot) · `eval-launchers.md` (naming an
eval launcher and wiring a judge) · `pipeline-kinds.md` (where a pipeline term belongs).
