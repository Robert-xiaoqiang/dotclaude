# Skill: docs-weekly

## Purpose
Write the **weekly research report**: prose in one chosen language with technical vocabulary always in
English, assembled in **stages** from whatever inputs exist that week. The report is a deliverable a
human reads in a meeting, so it must carry the argument, not a list of what happened.

## When to Use
- "写周报", "build this week's report", "finish the weekly report".
- A draft weekly exists and needs to be brought to style, or a missing section written.
- Any dated `BrainStorm/<MMDD>/` or `docs/reports/` weekly deliverable.

Not for: plan docs (`docs-plan`), architecture refs (`docs-arch`), or method specs, which follow their
own language.

---

## Language: one skill, one argument

Invoke `/docs-weekly` for the default, `/docs-weekly en` for English. **Do not create a second skill for
the second language.** Two copies of a recipe drift, the drift is silent, and it is the same failure
`naming-config` forbids for near-duplicate configs: the fix is a parameter, not a fork.

Resolution order, first match wins:
1. explicit argument — `zh` | `en`
2. the language of the draft being revised, when one exists
3. default — `zh`

### What the toggle changes: prose only

| | `zh` | `en` |
|---|---|---|
| body prose, headings, table cells | Chinese | English |
| **technical vocabulary** | **English, unchanged** | **English, unchanged** |
| numbers, symbols, equations | identical | identical |
| section order and content | identical | identical |

**The term list is invariant across modes, and that invariance is the whole anti-drift device.** A term
of art is English in both modes, so there is nothing to translate in either direction and the common
failure has no surface to occur on. `rubric` stays `rubric` in a Chinese sentence and in an English one.

### Language hygiene, checked before returning

1. **One language per document.** Not per section, not per paragraph. A single English paragraph in a
   `zh` report is the bug this section exists to prevent.
2. **Never translate a term of art**, in either direction. If the reader will meet the word in a paper,
   it stays as the paper writes it.
3. **Punctuation follows the prose language.** `zh` uses `，。、（）——`; `en` uses `,.()`. Mixed
   punctuation is the earliest visible symptom of drift, so scan for it.
4. **Self-check:** after drafting, scan the body for sentences in the other language and for the other
   language's punctuation inside prose. Fix before returning, do not hand back a mixed document.

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
| 1 | *always* | **挑战 / 回顾** · Challenge | last week's finding restated in one paragraph + the number that motivates this week |
| 2 | a formulation, notation, or math change | **形式化** · Formulation | the objects, the equation, and **why this formulation addresses the measured phenomenon** |
| 3 | new measurements, an analysis subdir, cached verdicts | **新证据** · Evidence | numbers with their measurement basis, and what changed the design |
| 4 | paper links, PDFs, a literature sweep | **相关工作 / 定位** · Positioning | a mapping table (dimension × existing work), and **which cell is empty** |
| 5 | a codebase change | **实现与观测** · Implementation | what is implemented and verified vs what is not, as two explicit lists |
| 6 | run outputs | **结果** · Results | tables and figure placeholders (§figures) |
| 7 | *always* | **研究问题** · Research questions | one row per premise, and the experiment that would falsify it |
| 8 | *always* | **Benchmark** | scale, composition, known defects, what each eval can settle |
| 9 | *always* | **本周结论与未决项** · Findings + open | what holds, what is missing, what is next |

**Sections 2 and 4 are where the argument lives.** A report that has 3, 5 and 6 but not 2 and 4 is a
status update, and the reader cannot tell whether the week moved the thesis.

Sections 7 and 8 are separate on purpose: a premise table without a benchmark description states what
would be tested but not whether the test could settle it.

---

## Style

### Vocabulary, both modes
Technical terms stay English and unbolded, in their field-standard form: `rubric`, `reward`, `policy`,
`rollout`, `GRPO`, `advantage`, `Blind / Spurious / Inversion`, `harness`, `criterion`, `curriculum`.
Do not translate a term the reader will meet again in a paper.

### `zh` mode
**Natural Chinese, never translationese.** Read each sentence aloud. If it is an English sentence with
Chinese words substituted, rewrite it. Common tells: 「基于…的…」stacking, 「进行了…」for a verb that
already exists, 「其」as a possessive, subject and verb half a line apart.

### `en` mode
Plain declarative English under `writing-style`: no em-dashes, no semicolons, no lists unless asked.
The failure here is the mirror image, English that reads as translated Chinese, usually from keeping
the Chinese clause order or a topic-comment opener.

### Both modes
Never write a heading or sentence that only exists to introduce the next one.

### Headings
```
zh   ## 1. 挑战（Challenge）：上周 diagnosis 的回顾
     ### 1.2 主要结果
en   ## 1. Challenge: what last week's diagnosis established
     ### 1.2 Main result
```
Numbered from **1**, never 0. In `zh`, put the English term of art in parentheses after the Chinese
name, top level only.

**A heading states the CLAIM or names the CONTENT. It never glosses its own title.**

| | |
|---|---|
| ✗ `挑战：这条线在追什么` | 「这条线在追什么」only re-asks what 「挑战」already said |
| ✓ `开放端训练挑战：反馈的可靠性与训练的动态性` | names the two challenges |
| ✗ `定位：我们在哪里` | same failure, Chinese explaining Chinese |
| ✓ `该形式化下的现有工作定位` | says what is being positioned against what |
| ✗ `核心挑战：outer reward 怎么定义` | the colon introduces a question, not an answer |
| ✓ `outer reward 的定义困难与一条出路` | says there is a difficulty and that there is a way out |

The test: **delete everything before the colon. Does the remainder still carry information?** If it only
restates the part you deleted, the heading is empty.

### Body
- Bullets use `+` at top level, `-` then `*` nested. Not `*` at top level.
- **Bold** the claim in a bullet, then the evidence. `_斜体_` for a gloss on a term.
- Tables: numeric columns right-aligned `| ---: |`, `<br/>` for a two-line cell, tree glyphs
  (`├`, `└`) for a decomposition that sums to a parent row.
- Every number carries its basis: `62.1%`（按回答对统计，330 对，良构过滤后）. A number without a
  denominator is not a result.
- `en`: no em-dashes (`writing-style`). `zh`: the paired 破折号「——」is correct Chinese punctuation and
  is used freely, but a lone `—` never is.

### What to cut

**Meta-commentary about the document itself.** Sentences that rate a passage instead of adding to it:
「这一点是整个形式化的支点」, 「这也是最容易写错的地方」, 「本节最重要」, "this is the key insight",
"note that this matters". If a claim is load-bearing, the reader learns that from the argument standing
on it, never from being told. Delete every one of them, do not soften them.

Also cut: passive constructions where the actor matters, 「可以看出」/「值得注意的是」openers, and any
sentence that restates its heading. If a paragraph survives being deleted, delete it.

### Words this project does not use
| ✗ | ✓ |
|---|---|
| 诚实清单 | 本周结论与未决项 / 已有与未有 |
| 我们在哪里 / 这条线在追什么 | say the actual position or the actual question |

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

**Figure content and style are owned by `docs-figure`.** Read it before generating. The rules that bite
most often in a weekly report:
- **Nothing on the image that the report already says.** No headline claim, no explanatory sentence, no
  bullets copied out of the text. The report is the caption.
- **Parallel arms merge into one figure** with a legend keyed by arm name, never one figure per arm.
- Longitude (over steps) and latitude (across arms at one step) are different figures.
- One generator per figure, isolated in a `figures/` directory beside the report.

Generate with `output-analysis` when the runs are in the `layout-output` tree, otherwise a small script
or `.tex` beside the report.

---

## Use the field's vocabulary, never coin a rival one

When a formulation is an instance of a standard framework, **write it in that framework's terms**. A
coined phrase that competes with an established one costs the reader a translation and invites the
reviewer to ask whether the author knows the standard name.

| ✗ coined | ✓ standard | why it matters |
|---|---|---|
| "state is a trajectory, not a snapshot" | belief state / sufficient statistic of the history | in a POMDP the state already summarises history, so the coined line reads as if the author is redefining `state` |
| "cross-step tracking" as a new mechanism | the filtering / belief-update step | it is a named part of the framework, not an invention |
| "our two-layer thing" | bilevel / outer-loop RL, meta-learning | each has a literature the reader can check |

If the formulation genuinely departs from the standard framework, **say which axiom it drops**. That is
a contribution. Renaming a standard object is not.

---

## The Formulation section, when the week has one

This section fails most often, so it has its own recipe. Four moves, in order:

1. **The objects.** State the space, its indices, and their bounds, paired (`t ≤ T`, `i ≤ I`). A
   reader must be able to write down the shape.
2. **The equation.** One boxed statement of what is being optimised or measured.
3. **为什么这个形式化能解释已量到的现象** / *why it explains what was measured.* Map each measured failure mode onto a term. This is the
   part that makes it a formulation rather than notation: if a measured phenomenon has no term, the
   formulation is incomplete and the report should say so.
4. **它带来什么新的可做的事** / *what it makes possible.* What action or estimator becomes available that was not before.

A formulation section that does 1 and 2 but not 3 is notation, and a reader is right to ask what it
bought.

---

## The mechanism-ladder section

Use whenever the week's argument has the form *"this component should be X"* — learned, automated,
adaptive, parameterised, whatever the project's X is. The claim is only as good as the rung below it.

| component | existing mechanism + citation | what is missing | new mechanism | what it buys |
|---|---|---|---|---|

Four rules make it an argument rather than a table:

1. **Decompose into components a reader can check independently.** If a component cannot be swapped on
   its own, it is not a rung, and the ladder cannot be climbed one step at a time.
2. **Every occupied rung names a real implementation with a citation.** "A heuristic" is not a rung. The
   credibility of the empty cell comes entirely from how solid the filled ones are.
3. **The empty rung is the contribution, and its emptiness needs a reason.** Say why nothing occupies it
   — a structural obstacle, not an oversight. "Nobody tried" is weak; "the credit-assignment unit makes
   it unlearnable at their sample size" is an argument.
4. **The new rung must beat the rung below it, not the absence of one.** Name the simple mechanism each
   new component is measured against. Beating nothing is not a result, and a ladder whose middle rung is
   a strawman the authors wrote themselves is worse than no ladder.

Read the "existing implementation" column top to bottom: it should describe a complete, runnable system
with none of the week's new machinery. That configuration is the floor, and it is what makes the claim
falsifiable.

## Evaluation: two sections, not one

Splitting these is what lets a reader judge whether the plan could settle anything.

### (a) Research questions

One row per premise the earlier sections asserted as fact. Not the experiments you feel like running.

| # | premise | if it is wrong | falsifying experiment | what it needs |
|---|---|---|---|---|

A premise with no falsifying experiment is a belief, and the report labels it as one.

### (b) Benchmark

The reader cannot weigh a result without knowing what it was measured on. Give enough for them to
judge solidity before any number arrives:

- **Scale and composition** — train/eval sizes, per-item structure, the distribution that matters.
- **Known defects, stated by the authors.** A split that is not actually held out, a judge with known
  bias, a metric that saturates. Hiding these costs more later than admitting them now.
- **What each eval can and cannot settle.** In-distribution score, OOD transfer, and the probe set
  answer different questions, and a table saying which is which prevents the usual overclaim.
- **The generalisation protocol, when the claim is that something transfers.** Name what is frozen and
  what is tuned in each arm, because "it transfers" means nothing until that is fixed:

| arm | frozen | tuned | tests |
|---|---|---|---|
| zero-shot transfer | everything | nothing | whether the learned object is domain-agnostic |
| head-only | trunk / representation | output heads | whether the representation transfers |
| full re-train | nothing | everything | the upper bound the other two are read against |

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
- **A mixed-language document**, or a term of art translated into the prose language.
- **A heading that glosses its own title** (`挑战：这条线在追什么`).
- **Meta-commentary** telling the reader which part is important.
- **A coined term where a standard one exists**, especially one that redefines a framework's word.
- **An evaluation plan with no benchmark description**, so no one can judge what a number would mean.
- **A ladder whose lower rungs are strawmen the report invented**, rather than published mechanisms.

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
`writing-style` (punctuation and word choice in the authored doc) · `docs-figure` (what the embedded
figures may contain) · `output-analysis` (comparing the runs behind them) · `docs-plan` (the actionable plan a report's next-week section points at) ·
`layout-workspace` (where reports live) · `conventions` (the family index).
