---
name: docs-table
description: "Decide what a results table may contain, how its numbers are formatted, and how the winner is marked, for a paper or technical report."
when_to_use: "Use when building or revising any results, ablation or comparison table in LaTeX, or when a reviewer says a table is hard to read."
---
# Skill: docs-table

## Purpose
A table is a ranking the reader performs with their eyes, and every convention here exists to make
that ranking possible in one pass. `docs-figure` owns what a picture may contain; this owns the same
question for a grid of numbers. `writing-paper` owns the prose that cites the table.

The failure this guards against is a table that is complete and unreadable: nine columns where four
carry the argument, four decimal places on a number measured to two, and a winner the reader has to
find by scanning every cell because nothing on the page marks it.

## Contents
- [The one rule](#the-one-rule)
- [Number format](#number-format)
- [Marking the winner](#marking-the-winner)
- [The caption declares the convention](#the-caption-declares-the-convention)
- [Rules](#rules)
- [Structure](#structure)
- [One source for tables and figures](#one-source-for-tables-and-figures)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

---

## The one rule

> **A column must carry a comparison. If its values do not change how the reader ranks the rows, it
> is not a column.**

Two kinds of column fail this and both are common:

**Metadata columns.** An `Ep.` column holding the epoch each arm peaked at, a `#Params` column where
every arm is the same size, a `Seed` column. None of them is a result, all of them are read as one
because they sit inside the rule, and each costs the width the real numbers needed. Metadata goes in
the caption ("each arm at its best checkpoint") or in a setup paragraph, never in the grid.

**Derived columns.** A `$\Delta$` column holding each arm's mean minus the baseline's mean prints the
same comparison the `Mean` column already made, once per row, in a second place where it can drift.
The reader now ranks by two columns that cannot disagree. Fold the one difference that matters into
the cell that carries it, and delete the column.

The test, applied before the table is set: cover each column in turn. If the remaining table supports
the same claim, that column was not carrying it.

---

## Number format

**Three effective digits, and no more.** A rubric score of `0.5784` claims a precision no evaluation
of a few hundred prompts has. `57.8` says the same thing and is a third the width.

**Put the scale in the number, not in front of it.** A column of `0.5784`, `0.6073`, `0.6075` spends
its first two characters on `0.` in every cell, and the reader's eye has to travel past them to reach
the digits that differ. Multiply by 100 and say so once in the caption. This is what every strong
technical report does, and it is why their tables read at a glance.

**One decimal count per column, always.** `57.8` beside `60.7` beside `60.75` breaks the alignment
that makes a column scannable. Pad with a trailing zero rather than dropping it.

**Digits line up.** Right-align every numeric column (`r`, or `S` from `siunitx` when the column mixes
widths), and set `\sisetup` or the document's font so figures are tabular. A centred numeric column
is the third most common reason a table is slow to read.

**Differences carry a sign and a unit.** `$+$3.8` and `$-$2.0`, and percentage points are `pp`, never
`\%`. A change from 57.8 to 64.6 is `$+$6.8\,pp`; calling it `$+$6.8\%` is a different and wrong
quantity. State the unit in the caption once and drop it from the cells.

**Never print a constant column.** If every cell in a column is `0.0000` because it is the baseline's
own delta against itself, the column is an artifact of how the numbers were computed.

---

## Marking the winner

**Bold the best, underline the second best, and give the winning cell its margin.**

```latex
EvoRubric    & \underline{60.8} & \underline{50.0} \\
\ourmethod{} & \best{64.6 (+3.8)} & \best{53.5 (+3.5)} \\
```

The pair does three things one mark cannot. The bold says which row won. The underline says who it
beat, so a reader sees at once whether the win is over a strong arm or a weak one. The parenthetical
gives the margin at the place the eye already is, which is the number a reader would otherwise compute
in their head for every column.

Two constraints make it work:

- **The margin is measured against the underlined cell, in the same column.** Not against the
  baseline, and not against a different column's runner-up. If the runner-up differs by column, the
  underline moves with it and each margin is still locally correct.
- **Bold and underline are the only two marks.** Colour, shading, arrows and daggers added on top
  stop the reader from knowing what a mark means. One exception: `\meas{}`-style superscripts that
  flag provenance rather than rank, declared in the caption.

Define them as macros in the preamble so a restyle is one edit:

```latex
\newcommand{\best}[1]{\textbf{#1}}
\newcommand{\snd}[1]{\underline{#1}}
```

When the paper's own method is not the best in some column, mark that column honestly: the bold goes
on whoever won. A table where the bold never leaves one row reads as a table nobody checked.

---

## The caption declares the convention

Every marking and scaling decision is invisible in the grid, so the caption states it, in this order:
what the table reports, the scale, what the marks mean, and what the parenthetical is.

```latex
\caption{%
Main results against the reproduced published methods, each arm at its best checkpoint.
Scores are rubric means $\times 100$. \textbf{Bold} marks the best result in a column and
\underline{underline} the second best; the parenthetical on our row is the margin over that
second best, in points.}
```

The caption goes **above** a table and **below** a figure. That is the `booktabs` convention and
every venue's template follows it.

---

## Rules
1. **A column carries a comparison or it is deleted.** Epoch, seed, parameter count and any column
   derivable from two others belong in the caption.
2. **Three effective digits.** Scale to 0-100 rather than printing a leading `0.` in every cell.
3. **One decimal count per column**, trailing zeros kept, numeric columns right-aligned.
4. **Bold the best, underline the second best**, in every column, computed per column.
5. **The winning cell carries its margin over the underlined cell**, signed, in points.
6. **The caption declares the scale and both marks**, and sits above the table.
7. **`booktabs` only.** `\toprule`, `\midrule`, `\cmidrule(lr){}`, `\bottomrule`. No vertical rules,
   no `\hline`, no full-width rule between every row.
8. **One font size and one `\tabcolsep` across every table in the document.** A table set smaller
   than its neighbours reads as an afterthought.
9. **Differences are `pp`, not `\%`**, and relative gains are given beside absolutes when the base is
   small.
10. **Tables and figures read the same source**, so a number cannot differ between them.

## Structure

**Group columns with a spanning header and a `\cmidrule`,** never with a vertical rule:

```latex
\toprule
& \multicolumn{5}{c}{In-domain held-out} & \multicolumn{4}{c}{Out of distribution} \\
\cmidrule(lr){2-6} \cmidrule(lr){7-10}
Arm & Medical & Science & \dots & MedQA & MedMCQA \\
\midrule
```

**Order rows by the argument, not alphabetically.** Baseline first, then published methods in the
order the related-work section introduced them, then ablations grouped by what they change, then the
paper's own method last. A `\midrule` separates groups, and the groups are themselves a claim.

**A wide table goes sideways or gets split**, never shrunk to `\tiny`. Two stacked blocks under one
caption, each with its own header row, beat one block nobody can read.

**Leave the placeholder visible when a number is not in yet.** `--` in every cell of a row, with the
caption saying what is pending, is honest and survives review. A blank cell reads as a bug, and a
number invented to fill the hole is the one mistake in this skill that ends a career.

## One source for tables and figures

A results table is regenerated whenever a run updates, so the LaTeX rows are emitted by a script, not
typed. The same script feeds the figures.

- One data file per paper (`arms.json` or equivalent) holding the measured values, read-only.
- One emitter that prints the `\\`-terminated rows, applying the format and the marks from this skill.
- Figures import the same file, so a curve's endpoint and a table's cell cannot disagree.
- The emitter computes the bold and the underline itself. Marks placed by hand go stale on the next
  run, and a stale bold is a wrong claim.

## Anti-patterns
- **The epoch column.** Metadata inside the rule, read as a result, taking the width the results
  needed.
- **The delta column.** The same comparison the mean column already made, in a second place that can
  drift from the first.
- **`0.5784`.** Four decimals on a number measured to two, with the two most prominent characters
  identical in every row.
- **The constant column.** `$+$0.0000` down the baseline's whole row.
- **Bold with no underline.** The reader sees who won and not who they beat, so a margin of 0.1 and a
  margin of 8 look the same.
- **Marks placed by hand** on a table a script emits, then not moved when the numbers change.
- **A caption that describes the experiment and never says what bold means.**
- **Vertical rules**, `\hline` between every row, or a box around the table.
- **`\tiny` to make a table fit.** Rotate it, split it, or drop the columns that fail the one rule.
- **A different font size in every table.**
- **`\%` on a difference between two percentages.**
- **A fabricated number in place of a pending one.**

## Companions
`docs-figure` (the same question for pictures, and the shared generator directory) · `writing-paper`
(the prose that leads with the finding and cites the table as evidence, and the `pp` convention) ·
`output-analysis` (which runs belong in the comparison) · `writing-chatgpt` (the caption's prose) ·
`conventions` (family index).
