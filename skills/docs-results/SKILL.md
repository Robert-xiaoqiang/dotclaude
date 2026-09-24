---
name: docs-results
description: "Build the experiments section of a paper: what the setup must state, how each results paragraph is shaped, how ablations are designed and grouped, which evidence goes in a table, a figure or the appendix, and how every number stays traceable. The results-level layer above docs-table (the grid), docs-figure (the picture) and writing-paper (the sentence)."
when_to_use: "Use when drafting or revising Main results, Ablations or In-depth analysis, designing the ablation set, deciding whether a result is a table, a figure or an appendix entry, or when a reviewer says the results are hard to follow, the ablations are unconvincing, or the numbers cannot be traced."
---
# Skill: docs-results

## Purpose
An experiments section is where a reader decides whether to believe the paper. It fails in three
recurring ways, all seen on real drafts: paragraphs that enumerate every cell of a table and never
say why, ablations that remove parts one by one without testing the design choice that matters, and
statistics whose construction is never stated, so the reader cannot tell what a number measures.
This skill fixes the shape of the section. `writing-paper` owns the sentence, `docs-table` the grid,
`docs-figure` the picture. This skill decides what goes where and what each paragraph must carry.

The patterns are taken from papers the author has written and liked (System-1.5, Mem-Pi,
LatentHarness): finding-first run-in heads, ablations described before their result, a wrapped
figure or table beside the paragraph that reads it, and every analysis statistic defined once.

## Contents
- [Section order](#section-order)
- [The setup is a measurement contract](#the-setup-is-a-measurement-contract)
- [One finding, two or three numbers, one reason](#one-finding-two-or-three-numbers-one-reason)
- [Ablations test design choices, by family](#ablations-test-design-choices-by-family)
- [Table, figure, appendix, or nothing](#table-figure-appendix-or-nothing)
- [Every number has a displayed source](#every-number-has-a-displayed-source)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## Section order
1. **Setup**, as run-in paragraphs: backbones, datasets (with the split each follows), baselines
   grouped by family, efficiency measures, and one paragraph on how ablations and analysis
   statistics are produced.
2. **Main results**: two to four paragraphs, overall accuracy, where the gain comes from, cost.
3. **In-depth analysis**: ablations first, because they justify the design, then the mechanism
   analyses that show the method behaving as the story says, then the residual failure.

Two subsections after the setup, `Main results` and `In-depth analysis`, are enough. A separate
subsection per ablation or per efficiency table fragments the argument.

## The setup is a measurement contract
Before a number is read, the reader must know how it was produced. State once, in the setup or the
appendix, never scattered across results paragraphs:

- **How each ablation is built.** Every variant retrains from the same initialization, data and
  budget and changes one component. Name what replaces the removed part, not only what is removed.
- **How each analysis statistic is computed.** The unit of averaging (per answer token, per
  question, per step), the split, and a one-sentence operational definition of every derived label
  (a "settled" state, a "hit", a "derived" read, "chance").
- **How cost is counted.** FLOPs relative to what, latency at which batch size and hardware, and
  what is included (prompt processing, compilation). Cost must not depend on a training loss.
- **Where the full values live.** A pointer to the appendix table that holds every per-suite value
  behind a figure.

A results paragraph that spends its first three sentences defining how it measured something is a
setup paragraph in the wrong place.

## One finding, two or three numbers, one reason
Every results paragraph has the same shape.

1. **The head is the finding**, a short claim: "X beats Y on Z", "X drives Y", "A fails where B
   holds". A reader who reads only the heads has the results in order. Never a topic label
   (`Ablations.`, `Recall provenance.`), never a question, never the figure as the subject.
2. **Two or three representative numbers**, each right after the claim it supports, of one of four
   kinds: a versus b, a trend from x to y, a difference, or a ratio. Pick the comparison that makes
   the point. The table or figure carries every other cell and is cited for it.
3. **One or two sentences of reason**, tied to the paper's motivation and mechanism: why the method
   behaves this way, why the baseline cannot. "We attribute this to" is the honest form when the
   reason is an interpretation.

```latex
% WEAK: topic head, every cell restated, no reason.
\noindent\textbf{Ablations.}\ Removing A reduces the two averages by 3.5 and 5.4 points to 52.3
and 44.3, removing B by 6.1 and 6.3 to 49.7 and 43.4, removing C by 2.2 and 7.7 to 53.6 and 42.0 ...

% STRONG: the finding as the head, two numbers, the reason.
\noindent\textbf{One-step branches match completed branches at a fraction of the training cost.}\
Counterfactual distillation reaches 49.7 on long-context tasks at 1.1$\times$ training compute,
against 48.6 at 3.6$\times$ for Monte Carlo branches, while state grouping adds under a point
because continuous latent states rarely recur. Every latent state decodes, so one step suffices.
```

Numbers in heads are fine when the claim is quantitative ("... by 3.9 points at 1.4B"). Signs and
units follow `writing-paper`: `$+$3.9 points`, `pp` for differences of percentages.

## Ablations test design choices, by family
An ablation table exists to justify the design, so its rows are chosen by the question each one
answers, not by listing every component.

- **Group variants into families**, each a design axis the method takes a position on: for example
  *credit* (how each decision is credited), *action space* (which decisions exist), *memory content*
  (what is stored), *cost control* (how computation is priced). A family header row replaces a
  sentence of explanation.
- **Include the alternatives, not only removals.** A family is convincing when it replaces the
  paper's component with the strongest published alternatives for the same job, run in the same
  setup: other step-level credit schemes (state grouping as in GiGPO, completed Monte Carlo branches
  as in VinePPO) beside the paper's own, an always-on variant beside a decided one. "w/o X" shows X
  matters; "X replaced by Y" shows X is the right choice.
- **Report the cost that makes the comparison fair.** When an alternative wins on accuracy by
  spending more, show its training or inference cost next to the score, or the comparison hides the
  trade.
- **Name variants by what they are**, in two or three words a reader can carry into the text:
  `GRPO only`, `GiGPO groups`, `VinePPO branches`, `Always read`, `Prompt only`. Never `$-$C $-$M`,
  never a sentence.
- **Drop inherited parts** unless the paper claims something about them. Ablating a component the
  paper takes unchanged from prior work tests the prior work.
- **Six to ten rows.** More is an appendix table.

Describe how each variant is built in the setup, then the result paragraphs only read it.

## Table, figure, appendix, or nothing
| the evidence is | it goes in |
|---|---|
| endpoint comparisons across methods and suites | the main table (`docs-table`), one long row per method |
| a handful of variants the next paragraph discusses | a wrapped table or figure beside that paragraph |
| a trend over a controlled axis (input length, hops, depth, budget) | a line figure, one panel per quantity |
| a distribution or allocation (where steps or reads go) | a stacked bar or histogram figure |
| per-suite values behind a trend figure | an appendix table, cited from the figure caption or setup |
| a single qualitative trace that repeats what a table or distribution already shows | nothing, delete it |
| hyperparameters | an appendix table |

A table whose rows are levels of one axis (4k, 8k, 16k ...) is a figure in disguise: plot the trend
and move the table to the appendix. A case-study figure earns its place only when it shows a
mechanism no aggregate can, such as the order of operations on one input, and it is cut the moment
the text no longer needs it.

## Every number has a displayed source
- Every number in a results paragraph must appear in a table, a figure, or an appendix table the
  paragraph cites. Text-only statistics are allowed only when no display fits (a training-dynamics
  scalar), and then they are stated once.
- Derived numbers are recomputed, not retyped: an average equals the mean of its cells, a speedup
  equals the latency ratio, a margin equals the difference to the named baseline.
- A claim about a family ("faster than token-space memory") holds for every member, or the member is
  named ("5.9$\times$ faster than Memory-R2").
- After any change to a number, check the abstract, introduction, conclusion, captions and figure
  scripts in the same pass. An independent read-only check of numbers against displays catches what
  the author's own pass misses.

## Rules
1. The setup states how every ablation is built and every statistic is computed, once.
2. Every results paragraph: finding head, two or three representative numbers, one reason.
3. Ablations are grouped into design families and include the strongest alternatives, not only
   removals, with the cost that makes the comparison fair.
4. Variant names are two or three words that say what the variant is.
5. Trends are figures, endpoints are tables, per-suite detail is appendix.
6. A figure that shows nothing the text or a table does not is deleted.
7. Every number has a displayed source, and derived numbers are recomputed.
8. Two subsections after the setup: Main results and In-depth analysis.

## Anti-patterns
- **The enumerating paragraph.** Every suite, scale and variant in prose, the same comparison six
  times, no reason.
- **The topic head.** `Ablations.`, `Efficiency.`, `Case study.` where the finding should be.
- **The figure as subject.** "Figure 5 shows ..." as the head.
- **Removal-only ablations.** "w/o A, w/o B, w/o C", no alternative for the component the paper
  argues is right.
- **Ablating the inherited backbone.**
- **The undefined statistic.** "33% never settle" with no definition of settling anywhere.
- **The scaling table.** Rows 4k, 8k, 16k, 32k, 64k in a table beside prose describing the trend.
- **The decorative case trace.** One example drawn at length, repeating what the aggregate shows.
- **The orphan number.** A value quoted in text that no table or figure contains.
- **The family claim from one member.** "Faster than token-space memory" when it holds only against
  one of four.

## Companions
`writing-paper` (the sentence and the finding-first head) · `docs-table` (the grid, marks, caption)
· `docs-figure` (the picture, captions, house plot style) · `writing-chatgpt` (every paragraph goes
through the writer) · `output-analysis` (which runs to compare) · `conventions` (family index).
