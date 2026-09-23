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
- [Organizing a results table like a technical report](#organizing-a-results-table-like-a-technical-report)
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

**Absolute values, not differences.** A cell holds the quantity measured, and the baseline appears as
its own row. `13.5 (+1.5)` beside every share, or a table whose cells are all `pp vs base`, hides the
baseline's level and makes every reader subtract. The one difference a table may carry is the margin
of the paper's own cell over the underlined runner-up, and only when the author has asked for it.

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
is the third most common reason a table is slow to read. The one exception: when every value in a column
has the same format (`xx.x` throughout), centring keeps the digits aligned just as well, and it keeps a
column of short numbers balanced under a header wider than they are (`MedMCQA` over `50.7`), where
right alignment leaves a hole on the left.

**Differences carry a sign and a unit.** `{$+$}3.8` and `{$-$}2.0`, and percentage points are `pp`, never
`\%`. A change from 57.8 to 64.6 is `{$+$}6.8\,pp`; calling it `{$+$}6.8\%` is a different and wrong
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
- **Bold and underline are the only rank marks.** Arrows, daggers and coloured numbers added on top
  stop the reader from knowing what a mark means. Shading is not a rank mark: a light tint of the
  paper's accent on its own row (`\rowcolor{ours}` with a colour at 8 to 12 percent) marks identity,
  and is the one place colour belongs in a results table. Shade the row, never individual cells.

Define them as macros in the preamble so a restyle is one edit:

```latex
\newcommand{\best}[1]{\textbf{#1}}
\newcommand{\snd}[1]{\underline{#1}}
```

When the paper's own method is not the best in some column, mark that column honestly: the bold goes
on whoever won. A table where the bold never leaves one row reads as a table nobody checked.

**Tint the row of the paper's own method, and no cell.** One `\rowcolor` on that row finds the
method at a glance and reads as one band. Per-cell tint looks like the same thing and is not:
`\cellcolor` paints only the cell's own box, so the method-name cell and every cell that is not
marked break the band into patches with white gutters between them. Bold and underline still
carry which cell won; the tint says only whose row this is.

**Where the margin goes when the row is tight.** `64.6 (+3.8)` inline costs about twice a cell's width,
which an eleven-column table cannot pay. Set the margin as a small second line under the value instead,
in the accent colour at `\tiny` or `\scriptsize`, so the column keeps the width of its numbers:

```latex
\newcommand{\gain}[2]{\makecell{\textbf{#1}\\[-2.5pt]{\tiny\color{oursfg}$+$#2}}}
\ourmethod{} & \gain{59.3}{3.0} & \gain{64.6}{2.9} & ... \\
```

---

## The caption declares the convention

A table caption is a noun phrase with the metric and the setting, then the marks as label:
value pairs, then nothing. Ten to thirty words.

```latex
\caption{Task success rate (SR \%) across four agent benchmarks with gpt-5.4-mini as the base
agent. \textbf{Bold}: best per column. \underline{Underline}: second best.}
\caption{Ablation results (SR \%) on WebArena and ALFWorld. Subscripts: drop from the full model.}
```

Column abbreviations are defined in the caption once, in the form they appear, `WB, IFB,
MMCQA: WritingBench, IFBench, MedMCQA`. The scale is stated once, `$\times 100$`. What the
caption never carries: the experiment's design, the reason a row is there, or the finding,
which is the text's first bold sentence and not the table's. The caption goes **above** a table
and **below** a figure, which is the `booktabs` convention and every venue's template follows
it. The caption is prose and goes through the writer like every other paragraph.
---

## Rules
1. **A column carries a comparison or it is deleted.** Epoch, seed, parameter count and any column
   derivable from two others belong in the caption.
2. **Three effective digits.** Scale to 0-100 rather than printing a leading `0.` in every cell.
3. **One decimal count per column**, trailing zeros kept, numeric columns right-aligned.
4. **Bold the best, underline the second best**, in every column, computed per column.
5. **The winning cell carries its margin over the underlined cell**, signed, in points, inline when
   the row has room and as a small second line when it does not.
6. **The caption declares the setting, the scale and both marks**, never the result, and sits
   above the table.
7. **`booktabs` only.** `\toprule`, `\midrule`, `\cmidrule(lr){}`, `\bottomrule`. No vertical rules,
   no `\hline`, no full-width rule between every row.
8. **One font size and one `\tabcolsep` across every table in the document.** A table set smaller
   than its neighbours reads as an afterthought.
9. **Differences are `pp`, not `\%`**, and relative gains are given beside absolutes when the base is
   small.
10. **Tables and figures read the same source**, so a number cannot differ between them.
11. **Cells hold absolute values.** The baseline is a row, not a subtrahend.
12. **The paper's own row is shaded**, lightly, in its accent. No other colour in the table.
13. **Scales are row groups of one table**, families are runs of rows, and trajectories are figures.

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

## Organizing a results table like a technical report

The flagship reports set their main table the same way, and the pattern is worth copying whole.

**Columns are benchmarks, grouped by what they test.** A spanning header over each group, joined by a
`\cmidrule(lr)`, and an `Avg.` column closing every group. Short benchmark names in the header, with
any abbreviation expanded once in the caption.

**Rows are methods, grouped twice.** The outer grouping is the base model or scale, set as an italic
header row spanning the table (`\multicolumn{12}{l}{\textit{Qwen3.5-4B}}`), so several scales share
one set of columns instead of becoming several tables. Inside a scale, methods run in families in the
order the paper introduced them: the plain baseline first, then each family of competing methods,
then the paper's own method last and shaded. A thin `\cmidrule` or a `\midrule` between families
states the grouping without a label.

**Merge tables that share their columns.** Two tables with the same benchmarks at two model scales are
one table with two row groups. Three tables that differ only in which arms they list are one table.
Splitting them makes the reader carry numbers between floats.

**Endpoints only.** A table compares end states. A per-epoch trajectory is a figure (`docs-figure`),
and once that figure exists the per-epoch table is deleted.

**Ablations share the main table's conventions** and add one column naming what each variant keeps,
set as a compact tag (`p,g,c`, `g`, `c`) rather than a sentence. Lower-is-better columns say so in the
header with a small `$\downarrow$`, higher-is-better with `$\uparrow$`, and the bold and underline
follow the arrow.

**Every table in the document uses one font size, one `\tabcolsep`, one shading colour.**
`\footnotesize` for results, the same for a qualitative case table, which is not an exception.

**Name an ablation by what it removes, in words, indented under the row it ablates.**

```latex
\ourmethod{}          & 10.5 & 13.4 & \best{27.2} \\
\quad w/o critic      & 11.1 & 15.2 & 31.6 \\
\quad w/o critic \& memory & 11.7 & 16.1 & 33.1 \\
```

Never `$-$C $-$M`. A math minus in a name typesets as an operator, the letters mean nothing
to a reader who has not memorised the key, and the same string set by LaTeX and by
matplotlib's mathtext comes out in two different faces, so the table and its figure disagree
on what the arm is called. The parent row comes first and its ablations sit below it in the
order the modules are removed, so the group reads top-down and the name is never repeated.
A subscript is fine for a restriction that has a symbol, `\ourmethod{}$_g$` for the harness
held to one interface, because it is the paper's own notation and not an abbreviation.

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
- **The constant column.** `{$+$}0.0000` down the baseline's whole row.
- **Bold with no underline.** The reader sees who won and not who they beat, so a margin of 0.1 and a
  margin of 8 look the same.
- **Marks placed by hand** on a table a script emits, then not moved when the numbers change.
- **A caption that describes the experiment and never says what bold means.**
- **A caption that reports the result.** The winner and its margin, restated above the grid that
  already marks them, and left behind when the numbers move.
- **Vertical rules**, `\hline` between every row, or a box around the table.
- **`\tiny` to make a table fit.** Rotate it, split it, or drop the columns that fail the one rule.
- **A different font size in every table.**
- **`\%` on a difference between two percentages.**
- **A fabricated number in place of a pending one.**
- **A table of differences against a baseline**, or `(+x)` against the baseline in every cell, when
  the baseline row could simply be printed.
- **A per-epoch table** beside the curve that already shows the trajectory.
- **Two tables with the same columns**, one per model scale.
- **Coloured individual cells** instead of one shaded row for the paper's method.
- **An inline margin that pushes the table past the text width**, where a stacked margin would fit.

## Companions
`docs-figure` (the same question for pictures, and the shared generator directory) · `writing-paper`
(the prose that leads with the finding and cites the table as evidence, and the `pp` convention) ·
`output-analysis` (which runs belong in the comparison) · `writing-chatgpt` (the caption's prose) ·
`conventions` (family index).
