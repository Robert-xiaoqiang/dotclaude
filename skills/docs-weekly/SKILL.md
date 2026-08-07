# Skill: docs-weekly

## Purpose
Write the **weekly research report** in this project's established style: Chinese main text with
English core concepts, assembled in **stages** from whatever inputs exist that week. The report is a
deliverable a human reads in a meeting, so it must carry the argument, not a list of what happened.

## When to Use
- "写周报", "build this week's report", "finish the weekly report".
- A draft weekly exists and needs to be brought to style, or a missing section written.
- Any dated `BrainStorm/<MMDD>/` or `docs/reports/` weekly deliverable.

Not for: plan docs (`docs-plan`), architecture refs (`docs-arch`), or English method specs, which stay
in English.

---

## The one rule that decides everything else

> **A weekly report is an ARGUMENT with a date on it, not a log of the week.**

Every section exists to move one claim forward. A section with no input that week is **omitted**, and
its absence is stated in the honest list. Never pad a heading with filler so the skeleton looks
complete: an empty section reads as "we did nothing here", which is worse than not having the heading.

---

## Staged assembly: input → section

The report is conditional. Check which inputs exist, emit only those sections, in this order.

| # | input available that week | section produced | what it must contain |
|---|---|---|---|
| 1 | *always* | **挑战 / 回顾** | last week's finding restated in one paragraph + the number that motivates this week |
| 2 | a formulation, notation, or math change | **形式化（Formulation）** | the objects, the equation, and **why this formulation addresses the measured phenomenon** |
| 3 | new measurements, an analysis subdir, cached verdicts | **新证据（Evidence）** | numbers with their measurement basis, and what changed the design |
| 4 | paper links, PDFs, a literature sweep | **相关工作 / 定位** | a mapping table (dimension × existing work), and **which cell is empty** |
| 5 | a codebase change | **实现与观测** | what is implemented and verified vs what is not, as two explicit lists |
| 6 | run outputs | **结果（Results）** | tables and figure placeholders (§figures) |
| 7 | *always* | **测评计划（Evaluation Plan）** | one row per premise, and the experiment that would falsify it |
| 8 | *always* | **诚实清单 + 下周计划** | what is missing, what is assumed, what is next |

**Sections 2 and 4 are where the argument lives.** A report that has 3, 5 and 6 but not 2 and 4 is a
status update, and the reader cannot tell whether the week moved the thesis.

---

## Style

### Language mix
- **Main text Chinese. Core concepts English**, unbolded, in their field-standard form: `rubric`,
  `reward`, `policy`, `rollout`, `GRPO`, `advantage`, `Blind / Spurious / Inversion`, `harness`,
  `criterion`, `curriculum`. Do not translate a term the reader will meet again in a paper.
- **Natural Chinese, never translationese.** Read each sentence aloud. If it is an English sentence
  with Chinese words substituted, rewrite it. Common tells: 「基于…的…」stacking, 「进行了…」for a verb
  that exists, 「其」as a possessive, subject-verb distance of half a line.
- Never write a heading or sentence that only exists to introduce the next one.

### Headings
```
## 1. 挑战（Challenge）：上周 diagnosis 的回顾
### 1.2 主要结果
```
Numbered from **1**, never 0. Top level carries a Chinese name, the English term in parentheses when
the concept is a term of art, then a colon and what the section actually argues.

### Body
- Bullets use `+` at top level, `-` then `*` nested. Not `*` at top level.
- **Bold** the claim in a bullet, then the evidence. `_斜体_` for a gloss on a term.
- Tables: numeric columns right-aligned `| ---: |`, `<br/>` for a two-line cell, tree glyphs
  (`├`, `└`) for a decomposition that sums to a parent row.
- Every number carries its basis: `62.1%`（按回答对统计，330 对，良构过滤后）. A number without a
  denominator is not a result.
- No em-dashes (`—`) in authored prose. Use a comma, parentheses, or two sentences (`writing-style`).

### What to cut
Passive constructions where the actor matters, 「可以看出」/「值得注意的是」openers, and any sentence
that restates the section heading. If a paragraph survives being deleted, delete it.

---

## Figures

Figures are **generated separately** and referenced by placeholder. Never inline plotting code in the
report, and never block the report on a figure existing.

Emit a placeholder plus a spec the generator can act on:

```markdown
<!-- FIG fig-drift: 见 figures/drift.png -->
> **图 N**：`fig-drift`
> x 轴 step｜y 轴 d∠（子空间漂移）｜曲线 = 4 条 arm，legend 用 arm 名｜灰带 = shuffle null
```

Rules, from `output-analysis`:
- **Not self-contained.** No title, no baked caption, terse axis labels. The surrounding text is the
  caption, so a figure repeating it wastes ink.
- **Parallel runs merge into one figure** with a legend keyed by arm name, never one figure per arm.
  Two arms one config slot apart belong on the same axes or the comparison is not visible.
- Longitude (over steps) and latitude (across arms at one step) are different figures. Do not mix.
- Generate with `output-analysis` when the runs are in the `layout-output` tree, otherwise a small
  script beside the report.

---

## The Formulation section, when the week has one

This section fails most often, so it has its own recipe. Four moves, in order:

1. **The objects.** State the space, its indices, and their bounds, paired (`t ≤ T`, `i ≤ I`). A
   reader must be able to write down the shape.
2. **The equation.** One boxed statement of what is being optimised or measured.
3. **为什么这个形式化能解释已量到的现象.** Map each measured failure mode onto a term. This is the
   part that makes it a formulation rather than notation: if a measured phenomenon has no term, the
   formulation is incomplete and the report should say so.
4. **它带来什么新的可做的事.** What action or estimator becomes available that was not before.

A formulation section that does 1 and 2 but not 3 is notation, and a reader is right to ask what it
bought.

---

## The non-parametric / parametric section

When the week's argument is "we should learn this", the report must earn it module by module:

| module | non-parametric 实现（现有工作） | 缺什么 | parametric 版本 | 参数化买到什么 |
|---|---|---|---|---|

- **Fill the non-parametric column with real citations**, not "a heuristic". If an existing work
  already does the module, say so and name it. That is what makes the empty cell credible.
- **The empty cell is the contribution.** Name which module has no existing non-parametric answer,
  and why the reason it is missing is structural rather than an oversight.
- **Parametric must beat the rule, not the absence.** State the rule-based sibling each learned
  component is measured against. "Learned beats nothing" is not a result.

---

## The Evaluation Plan section

One row per premise. The report's own assumptions are the rows, not the experiments you feel like
running.

| # | 前提 / 假设 | 如果错了会怎样 | 验证实验 | 需要什么 |
|---|---|---|---|---|

Every design decision that is stated as fact in sections 2-5 must appear here as a row. A premise
with no falsifying experiment is a belief, and the report should label it as one.

---

## Anti-patterns

- **A skeleton with empty sections.** Omit the heading instead.
- **English paragraphs in the body.** Core terms stay English, prose does not.
- **A results table with no measurement basis.** Denominator, filter, and n, or it is not a result.
- **One figure per arm.** Merge with a legend.
- **A formulation section that is only notation** (no mapping to the measured phenomenon).
- **"Learned component X helps"** with no rule-based sibling in the comparison.
- **Restating the plan as achievement.** What is implemented and what is not are two lists, and the
  second one is the useful one.
- **Numbering from 0.**

---

## Steps

1. Inventory the inputs: codebase diff, analysis subdirs, run outputs, paper links, figures.
2. Map them onto the staged table. Decide which sections exist. Say out loud which are omitted.
3. Draft the spine: section 1 and the Formulation, because they carry the argument.
4. Fill evidence and mapping sections from real numbers and real citations.
5. Emit figure placeholders with specs, do not generate inline.
6. Write the Evaluation Plan from the premises the earlier sections asserted.
7. Close with the honest list. Read it back: does someone who missed the week know what changed and
   what is still unknown?

## Companions
`writing-style` (punctuation and word choice in the authored doc) · `output-analysis` (the figures this
report embeds) · `docs-plan` (the actionable plan a report's next-week section points at) ·
`layout-workspace` (where reports live) · `conventions` (the family index).
