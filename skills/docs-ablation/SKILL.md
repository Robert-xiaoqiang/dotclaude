---
name: docs-ablation
description: "Design a paper's ablation set and its table: group variants into families along the method's design dimensions, build each variant by removal, same-function substitution, extreme setting or oracle, change one component per row at a matched budget, name rows by what they are, and lay the table out compactly with the change from the full system, learned from LatentHarness and a rejected MemCodex table."
when_to_use: "Use when designing or revising an ablation study or ablation table, when every row reads 'w/o X (long explanation)', when a reviewer asks whether a component matters or merely adds capacity, or when an ablation table is too long or too flat to read."
---
# Skill: docs-ablation

## Purpose
An ablation earns its space by showing *which design choice* carries the result and *why the
alternative a reader would try instead is worse*. A list of `w/o X` rows answers only the first half:
it shows a part helps, not that this form of the part is the right one. This skill designs the
ablation set as families of alternatives along the method's design dimensions, and fixes how the table
and its prose present them. `docs-analysis` owns how an ablation is framed in the results prose,
`docs-table` owns number format and marks, and this skill owns which variants exist and how they are
grouped.

## Contents
- [When to Use](#when-to-use)
- [Families along design dimensions](#families-along-design-dimensions)
- [Four ways to build a variant](#four-ways-to-build-a-variant)
- [Naming rows](#naming-rows)
- [The table](#the-table)
- [The prose](#the-prose)
- [Worked example: LatentHarness](#worked-example-latentharness)
- [Worked example: the rejected MemCodex table](#worked-example-the-rejected-memcodex-table)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Designing the ablation set of a method paper, before any variant is run.
- Revising an ablation table whose rows are all removals, or whose names are sentences.
- A reviewer asks whether a component matters or only adds capacity, compute or context.
- Compressing a long ablation table that no longer fits.

Not for: the main results table (`docs-table`), the order and shape of the results section
(`docs-analysis`), or sweeps over one hyperparameter (a figure, `docs-figure`).

## Families along design dimensions
Start from the method's **design decisions**, not its module list. Each decision the paper claims to
get right becomes a family, and the family asks one question: *which way of making this decision
works, and why*. LatentHarness has five: action credit (how steps are credited), action space (which
actions exist), memory content (what is written), write gate (how the gate is trained) and action
price (what computation costs). Each family sits under an italic family row, so the table is read
as five small experiments instead of one long list.

A good family has two to four variants and exactly one dimension. A row that changes two decisions at
once belongs to no family and proves nothing, because its drop cannot be attributed.

## Four ways to build a variant

| kind | what changes | what it proves | example |
|---|---|---|---|
| removal | the component is dropped or switched off | the component contributes | Think and Exit (no Recall action) |
| substitution | the component is replaced by a **same-function alternative**, usually the standard one from prior work | this form beats the obvious alternative | GRPO only, GiGPO groups, VinePPO branches in place of counterfactual credit |
| extreme | the component is forced to one end of its range | the decision must adapt, not be fixed | Always read (read at every step); No price |
| oracle or upper bound | the component gets information the method cannot have | how much headroom is left | an oracle router given the gold layer |

Substitutions are the strongest rows. A removal shows a part helps, and a reviewer answers "any
reasonable version would help". A substitution by the standard alternative answers that objection
directly. Every family should contain at least one substitution or extreme. A family of pure
removals is a sign the dimension was not thought through.

Keep the budget matched and say so. LatentHarness: "Every variant retrains from the same
initialization with the same data, training steps, and compute budget, while changing one
component." Where a variant costs more (VinePPO branches at 3.6x compute), report that cost in the
caption. Otherwise a variant that loses on accuracy but wins on cost looks like a plain loss.

## Naming rows
Name a row by **what the variant is**, in two to four words, never by a parenthetical explanation.
"GRPO only", "Token-loss gate", "Derived only", "Always read" and "No price" are names. "w/o routing channel (derived text as content)"
is a definition, and it belongs in the construction paragraph. Use `w/o X` only for a genuine
removal, and prefer the positive name of what remains. "Raw layer only" says more than "w/o derived
layers". The full system is the first row, tinted, with the paper's macro.

## The table
- **Family rows.** An italic row spanning the variant columns (`\famrow{4}{Action credit}`) opens
  each family. There is no `\midrule` between families. The family rows do the grouping.
- **Two halves when the set is long.** Split the families into two side-by-side blocks that share one
  header (`Variant & m1 & m2 & m3 & Variant & m1 & m2 & m3`), separated by extra column space rather
  than a vertical rule. Fourteen rows print as seven, which is how an ablation fits beside the main
  table.
- **Few columns.** Show the family averages and one cost column (LatentHarness: Gen., Long, FLOPs).
  Per-benchmark columns go to the appendix. An ablation table compares variants, not benchmarks.
- **The change from the full system** goes in small type after each value,
  `55.4\,\drop{$-$0.4}` or `56.1\,\rise{$+$0.3}`, with red for a loss and green for a gain. This is the
  one exception to `docs-table`'s "absolute values, not differences": an ablation's point is the
  change, and the absolute value stays beside it. Do not bold-and-underline an ablation table as well.
  The change marks carry the ranking.
- **The caption** states that one component changes per row, defines the columns, says what the
  parentheses are, and reports any budget differences.

## The prose
**One construction paragraph** in the setup says how each family's variants are built, in the order
of the table, with the inherited method named ("GiGPO groups states visited across the rollouts of a
prompt by output position and preceding action sequence, then computes step advantages from
within-group returns"). The table names stay short because this paragraph carries the definitions.

**One bold finding per family**, which leads with the decision and gives the mechanism. "One-step
counterfactual branches match completed branches at much lower training cost." "Selective Recall and
both forms of memory content are necessary on long inputs." The numbers follow, then the reason
("because just 14% of visited states belong to a group containing at least two states"). A finding
that only restates a drop has not explained the family.

## Worked example: LatentHarness
`LatentHarness/overleaf-git/main.tex`, Table `tab:ablation`: five families, eleven variants, two
halves, three columns per half (Gen., Long, FLOPs), changes in parentheses, one construction
paragraph ("Ablations and analysis statistics") and one finding paragraph per family.

| family | removal | substitution | extreme |
|---|---|---|---|
| Action credit | | GRPO only, GiGPO groups, VinePPO branches | |
| Action space | Think and Exit | | Always read |
| Memory content | Prompt only, Derived only | | |
| Write gate | | Token-loss gate, Write-time gate | |
| Action price | | | No price |

Macros from its `commands.tex`:
```latex
\newcommand{\drop}[1]{{\color{lossred}\scriptsize(#1)}}
\newcommand{\rise}[1]{{\color{gaingreen}\scriptsize(#1)}}
\newcommand{\famrow}[2]{\multicolumn{#1}{l}{\footnotesize\textit{#2}}}
```

## Worked example: the rejected MemCodex table
The author rejected a nine-row table on 2026-09-25: "why the variant name so verbose, so long",
"not just +/-, can switch into some same-function component". Every row was a removal named by a
parenthetical, `w/o routing channel (derived text as content)`, and one row, `w/o latent memory`,
differed from the full system by under a point with the same recall and tokens, so it read as noise.
The fix regrouped the rows into families by the method's decisions: evidence channel, organization,
read depth, latent memory, edit unit, acceptance and search. It added same-function alternatives,
such as content plus routing against routing, a RAPTOR-style summary tree against the hierarchy, and
whole-program rewrites against one-verb edits, and it moved per-benchmark numbers to the appendix.

## Rules
1. **Families come from design decisions, one dimension each, two to four variants.**
2. **Every family has at least one substitution or extreme.** A family of removals alone is not
   finished.
3. **One component changes per row, at a matched budget**, and any budget difference is in the
   caption.
4. **Rows are named by what they are, in two to four words.** Definitions go in the construction
   paragraph.
5. **Family rows group the table**, with no rules between families, and a long set is split into two
   halves.
6. **Cells hold the value and its change from the full system**, in small red or green, and nothing
   else marks rank.
7. **Few columns**: family averages and one cost, per-benchmark results in the appendix.
8. **One construction paragraph, then one bold finding per family** that names the mechanism.
9. **Every number traces to the results ledger**, and a changed row updates every sentence that
   quotes it.

## Anti-patterns
- **The w/o list.** Every row removes a part. It shows parts help and never that this form of a part is
  the right one.
- **The definition as a name.** `w/o query-adaptive depth (always read to raw)` in the row label. The
  table becomes unreadable and the construction paragraph has nothing to do.
- **The noise row.** A variant that differs by less than the seed spread, left in without comment. Either
  it is a finding ("adds nothing here, at no cost") or it is removed.
- **Two changes in one row.** A variant that swaps the organization and the read rule together cannot
  be attributed to either.
- **The benchmark table in disguise.** Six benchmark columns per variant. The comparison is between
  variants, so averages carry it.

## Companions
`docs-analysis` (framing ablations in the results prose, RQ numbering) · `docs-table` (number
format, marks, captions, and the rule this skill makes one exception to) · `writing-paper` (the
finding-first paragraph) · `writing-chatgpt` (the construction paragraph and findings go through
the writer) · `docs-results` where present (traceable numbers).
