---
name: writing-table
description: "Set a results table for a paper or technical report: keep a column only where it carries a comparison, write three effective digits on a 0-100 scale, bold the best and underline the second best with the winning cell's margin inline in the accent colour, rule it with booktabs and group it like a technical report's main table, and print every row with one emitter from the one data file the figures also read."
when_to_use: "Use when building or revising a main results or comparison table in LaTeX, or the number format of any table, when a reviewer says a table is hard to read, when a table carries an epoch, seed or delta column, four-decimal scores or a bold placed by hand, or when a table and a figure disagree on a number. Not for the ablation table's variants and change marks (writing-ablation), the caption (writing-caption), or whether a result is a table at all (writing-analysis)."
---
# Skill: writing-table

## Purpose
A table is a ranking the reader performs with their eyes, and every convention here exists to make
that ranking possible in one pass. This skill owns the grid of a results table: which columns it keeps,
how its numbers are written, how the winner and its margin are marked, how its rules and row groups are
set, and the one data file and emitter that print its rows and feed the paper's figures.

The failure this guards against is a table that is complete and unreadable: nine columns where four
carry the argument, four decimal places on a number measured to two, and a winner the reader has to
find by scanning every cell because nothing on the page marks it.

## Contents
- [When to Use](#when-to-use)
- [The one rule](#the-one-rule)
- [Number format](#number-format)
- [Marking the winner](#marking-the-winner)
- [The caption](#the-caption)
- [Structure](#structure)
- [Organizing a results table like a technical report](#organizing-a-results-table-like-a-technical-report)
- [One source for tables and figures](#one-source-for-tables-and-figures)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Building or revising a main results or comparison table in LaTeX, or setting the number format and
  rules of any table in the document.
- A reviewer says a table is hard to read, or a table carries an epoch, seed or delta column,
  four-decimal scores, or a bold placed by hand.
- Writing the script that emits a paper's table rows, or a table and a figure disagree on a number.

Not for:
- the ablation table's variants, columns, row names and change marks (`writing-ablation`),
- the caption, including how it declares the marks (`writing-caption`),
- whether a result is a table, a figure or an appendix entry, and the prose that cites it
  (`writing-analysis`, `writing-paper`),
- what a figure may contain (`drawing-figure`).

---

## The one rule

> **A column must carry a comparison. If its values do not change how the reader ranks the rows, it
> is not a column.**

Two kinds of column fail this and both are common:

**Metadata columns.** An `Ep.` column holding the epoch each arm peaked at, a `#Params` column where
every arm is the same size, a `Seed` column. None of them is a result, all of them are read as one
because they sit inside the rule, and each costs the width the real numbers needed. Metadata goes in
a setup paragraph ("each method's best checkpoint per evaluation set"), never in the grid.

**Derived columns.** A `$\Delta$` column holding each arm's mean minus the baseline's mean prints the
same comparison the `Mean` column already made, once per row, in a second place where it can drift.
The reader now ranks by two columns that cannot disagree. Fold the one difference that matters into
the cell that carries it, and delete the column.

The test, applied before the table is set: cover each column in turn. If the remaining table supports
the same claim, that column was not carrying it. A column that needs a caption note before it can be
read is the first one to cover.

**Absolute values, not differences.** A cell holds the quantity measured, and the baseline appears as
its own row. `13.5 (+1.5)` beside every share, or a table whose cells are all `pp vs base`, hides the
baseline's level and makes every reader subtract. The one difference a results table carries is the
margin of the paper's own winning cell over the underlined runner-up
([Marking the winner](#marking-the-winner)).

---

## Number format

**Three effective digits, and no more.** A rubric score of `0.5784` claims a precision no evaluation
of a few hundred prompts has. `57.8` says the same thing and is a third the width.

**Put the scale in the number, not in front of it, and never annotate it.** A column of `0.5784`,
`0.6073`, `0.6075` spends its first two characters on `0.` in every cell, and the reader's eye has
to travel past them to reach the digits that differ. Report `57.8`, `60.7`, `60.8`. A score written
as `xx.y` is the standard form in this literature and needs no explanation, so there is no
"$\times 100$" in the caption, the axis label, or the prose: the annotation makes a reader wonder
what the raw quantity was, and nobody asks. The same holds for a percentage: `48.9` in a column
headed "Agree (%)", never `0.489` with a note.

**One decimal count per column, always.** `57.8` beside `60.7` beside `60.75` breaks the alignment
that makes a column scannable. Pad with a trailing zero rather than dropping it.

**Digits line up.** Right-align every numeric column (`r`, or `S` from `siunitx` when the column mixes
widths), and set `\sisetup` or the document's font so figures are tabular. A centred numeric column
is the third most common reason a table is slow to read. The one exception: when every value in a column
has the same format (`xx.x` throughout), centring keeps the digits aligned just as well, and it keeps a
column of short numbers balanced under a header wider than they are (`MedMCQA` over `50.7`), where
right alignment leaves a hole on the left.

**Differences carry a sign, and the unit is stated once.** `{$+$}3.8` and `{$-$}2.0` in the cells, with
the unit in the column header and dropped from every cell. That a difference between two percentages
is `pp` and never `\%` is `writing-paper`'s rule, with its worked example in `writing-analysis`.

**Never print a constant column.** If every cell in a column is `0.0000` because it is the baseline's
own delta against itself, the column is an artifact of how the numbers were computed.

---

## Marking the winner

**Bold the best, underline the second best, and give the winning cell its margin.**

```latex
EvoRubric    & \snd{60.8}          & \snd{50.0} \\
\ourmethod{} & \best[$+$3.8]{64.6} & \best[$+$3.5]{53.5} \\
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

Define them as macros in the preamble so a restyle is one edit. One macro sets every winning cell,
`\best{84.2}` for a plain bold and `\best[$+$4.8]{53.5}` for a bold that carries its margin:

```latex
\NewDocumentCommand{\best}{o m}{\textbf{#2}\IfValueT{#1}{\,{\scriptsize\color{oursfg}(#1)}}}
\newcommand{\snd}[1]{\underline{#1}}
```

When the paper's own method is not the best in some column, mark that column honestly: the bold goes
on whoever won. A table where the bold never leaves one row reads as a table nobody checked.

**The header says which way is better.** A lower-is-better column carries a small `$\downarrow$` in
its header, a higher-is-better one `$\uparrow$`, and the bold and underline follow the arrow.

**Tint the row of the paper's own method, and no cell.** One `\rowcolor` on that row finds the
method at a glance and reads as one band. Per-cell tint looks like the same thing and is not:
`\cellcolor` paints only the cell's own box, so the method-name cell and every cell that is not
marked break the band into patches with white gutters between them. Bold and underline still
carry which cell won; the tint says only whose row this is.

**The margin is inline, never a second line.** `64.6 (+3.8)`: the value in bold, the margin
in parentheses right after it, in the paper's accent colour `oursfg` and one size smaller, never bold.
A margin set as a small second line under the value breaks the row's baseline, and a reader scanning
the column sees two numbers where there is one result.

```latex
\ourmethod{} & \best{84.2} & \best{53.1} & \best[$+$4.8]{53.5} & \best[$-$29]{55} \\
```

**When the row cannot carry it in every column**, as in a nine-column results table, give the
margin only in the summary columns the reader ranks by, the average and the cost columns, and
leave the per-benchmark cells as plain bold. The per-benchmark margins then belong in the results
paragraph, next to the claim each one supports. Never shrink the table to make every margin fit.

**One exception: the ablation table.** Its cells carry each variant's change from the full system in
small red or green, and it takes no bold and no underline, because the change marks carry its ranking.
`writing-ablation` owns that table's columns, rows and marks, and this skill still sets its number
format and its `booktabs` rules.

---

## The caption

`writing-caption` owns the caption, including the sentence that declares bold, underline and the margin.

---

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
groups the setup introduced them in (`writing-analysis`), then the paper's own method last. A
`\midrule` separates groups, and the groups are themselves a claim.

**A wide table goes sideways or gets split**, never shrunk to `\tiny`. Two stacked blocks under one
caption, each with its own header row, beat one block nobody can read.

**Leave the placeholder visible when a number is not in yet.** `--` in every cell of a row, with the
caption saying what is pending, is honest and survives review. A blank cell reads as a bug, and a
number invented to fill the hole is the one mistake in this skill that ends a career.

## Organizing a results table like a technical report

The flagship reports set their main table the same way, and the pattern is worth copying whole.

**Columns are benchmarks, grouped by what they test.** A spanning header over each group, joined by a
`\cmidrule(lr)`, and an `Avg.` column closing every group. Short benchmark names in the header, and
where an abbreviation is expanded is `writing-caption`'s rule.

**Rows are methods, grouped twice.** The outer grouping is the base model or scale, set as an italic
header row spanning the table (`\multicolumn{12}{l}{\textit{Qwen3.5-4B}}`), so several scales share
one set of columns instead of becoming several tables. Inside a scale, methods run in families in the
order the paper introduced them: the plain baseline first, then each family of competing methods,
then the paper's own method last and shaded. A thin `\cmidrule` or a `\midrule` between families
states the grouping without a label.

**Merge tables that share their columns.** Two tables with the same benchmarks at two model scales are
one table with two row groups. Three tables that differ only in which arms they list are one table.
Splitting them makes the reader carry numbers between floats.

**Endpoints only.** A table compares end states, and whether a result is a table, a figure or an
appendix entry is `writing-analysis`'s call.

**Every table in the document uses one font size, one `\tabcolsep`, one shading colour.**
`\footnotesize` for results, the same for a qualitative case table, which is not an exception.

## One source for tables and figures

A results table is regenerated whenever a run updates, so the LaTeX rows are emitted by a script, not
typed. This skill is the one owner of the data file and the emitter. `drawing-figure`'s scripts read
the same file read-only and own only how each figure draws it.

- One data file per paper (`arms.json` or equivalent) holding the measured values, read-only.
- One emitter that prints the `\\`-terminated rows, applying the format and the marks from this skill.
- Figures import the same file, so a curve's endpoint and a table's cell cannot disagree.
- The emitter computes the bold and the underline itself. Marks placed by hand go stale on the next
  run, and a stale bold is a wrong claim.

## Rules
1. **A column carries a comparison or it is deleted.** Epoch, seed and parameter count belong in the
   setup, and a column derivable from two others is deleted.
2. **Three effective digits.** Scale to 0-100 rather than printing a leading `0.` in every cell.
3. **One decimal count per column**, trailing zeros kept, numeric columns right-aligned.
4. **Bold the best, underline the second best**, in every column, computed per column, in every table
   but the ablation table, whose change marks `writing-ablation` sets.
5. **The winning cell carries its margin over the underlined cell**, signed, in points, inline as
   `64.6 (+3.8)` in `oursfg` through the one `\best` macro, never as a second line, and only in the
   summary columns when the row is tight.
6. **`booktabs` only.** `\toprule`, `\midrule`, `\cmidrule(lr){}`, `\bottomrule`. No vertical rules,
   no `\hline`, no full-width rule between every row.
7. **One font size and one `\tabcolsep` across every table in the document.** A table set smaller
   than its neighbours reads as an afterthought.
8. **Differences are signed, with the unit once in the column header.** That a difference between
   two percentages is `pp`, never `\%`, is the rule `writing-paper` states and `writing-analysis`
   works through.
9. **Tables and figures read the same source**, one data file whose rows one emitter prints with the
   marks it computes, so a number cannot differ between them.
10. **Cells hold absolute values.** The baseline is a row, not a subtrahend.
11. **The paper's own row is shaded**, lightly, in its accent. No other colour in the table, except an
    ablation table's change marks, which `writing-ablation` sets.
12. **Scales are row groups of one table**, families are runs of rows, and a trajectory is a figure
    (`writing-analysis`).

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
- **Vertical rules**, `\hline` between every row, or a box around the table.
- **`\tiny` to make a table fit.** Rotate it, split it, or drop the columns that fail the one rule.
- **A different font size in every table.**
- **A fabricated number in place of a pending one.**
- **A table of differences against a baseline**, or `(+x)` against the baseline in every cell, when
  the baseline row could simply be printed.
- **Two tables with the same columns**, one per model scale.
- **Coloured individual cells** instead of one shaded row for the paper's method.
- **A margin set as a second line under the value**, which breaks the baseline the column is read along.
- **A table shrunk to fit a margin in every column**, where the summary columns alone should carry it.

## Companions
`writing-ablation` (the ablation table's variants, columns, row names and red and green change marks,
the one exception to the marks here) · `writing-caption` (the caption, including the sentence that
declares bold, underline and the margin) · `writing-analysis` (whether a result is a table, a figure or
an appendix entry, the baseline groups the rows follow, and the worked `pp` example) · `writing-paper`
(the prose that leads with the finding and cites the table as evidence, and the `pp` rule itself) · `drawing-figure` (what a
picture may contain, drawn by scripts that read this skill's data file) · `output-analysis` (which
runs belong in the comparison) · `writing-chatgpt` (the caption's prose) · `conventions` (family index).
