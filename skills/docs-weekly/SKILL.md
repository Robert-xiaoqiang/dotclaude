---
name: docs-weekly
description: "Write the weekly research report in stages: prose in one chosen language with technical vocabulary kept in English, carrying the argument rather than listing what happened."
when_to_use: "Use on requests like write the weekly report or finish this week's report, or when a draft weekly needs bringing to style."
---
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

## The report is a self-contained story

**A reader who has seen nothing else must be able to read it start to finish and end up where you are.**
No prior week assumed, no pointer to another document, no term used before it is defined. If a claim
needs something from last week, restate that thing here in one sentence.

Two arcs work. Pick one before writing and hold it for the whole report:

| arc | when | shape |
|---|---|---|
| **challenge → solution** | the week produced a method | what is broken and how you know → what you built → does it move the thing that was broken |
| **premise → setting → results** | the week produced measurements | what you are assuming and why it is reasonable → exactly what was run → what came out, and what it forces |

**The arcs are not section lists, they are dependency orders.** Every section answers a question the
previous section made the reader ask. If a section could be moved earlier without confusing anyone, the
arc is not actually carrying the report and the reader is navigating a folder rather than following an
argument.

The commonest break: results arrive before the setting that makes them interpretable, and the setting
is then reconstructed afterwards out of parenthetical asides. If a number needs a condition to be read,
the condition is a section that precedes it, not a caveat that trails it.

---

## Format dealbreakers

These are not preferences. A draft that violates one gets fixed before anything else is looked at.

1. **No section numbers. Ever.** Not `## 1.`, not `### 3.8`, not `一、`, not `(1)`. Headings are bare
   names. A numbered list *inside* a section is fine and starts at 1.
2. **When sections are generated as separate files that assemble into one report, the top heading in
   every file is H2.** The H1 belongs to the assembled document alone, written once by the assembler.
   A per-section file starting at H1 produces a report with ten titles.
3. **Figures are embedded at the point of use, with the figure named and its path visible.** Never a
   placeholder that survives into the delivered document, never a figure referenced but not shown.
4. **No cross-references between sections in the report.** If two sections need to point at each other,
   they are one section (§What to cut). The `§` pointers in *this skill* are reference-doc navigation and
   are not a licence to use them in a weekly.
5. **One language in the body.** §Language hygiene.

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
| 6 | run outputs | **结果** · Results | tables, and every figure embedded at its point of use with name and path (§Figures) |
| 7 | *always*, but in `docs-plan` | **研究问题** · Research questions | one row per premise **this report asserted**, and the measurement that would falsify it. Built as a check, not shipped in the report (§Forward-looking material) |
| 8 | *always* | **Benchmark** | scale, composition, known defects, what each eval can settle |
| 9 | *always* | **计划** · What happens next | three to five bare names, each with an antecedent in the body. The 结论 half moves **up**, under the tables that produced it (§What to cut) |

The `#` column indexes this table only. **It is not a numbering scheme for the report** — the report's
headings are bare names (§Format dealbreakers).

**Formulation and Positioning are where the argument lives.** A report with Evidence, Implementation and
Results but neither of those two is a status update, and the reader cannot tell whether the week moved
the thesis.

Research questions and Benchmark are separate on purpose: a premise table without a benchmark description
states what would be tested but not whether the test could settle it.

---

## Where the length goes

**The character budget is not spread evenly, and a draft reliably inverts it.** Two zones with opposite
defaults. Getting this backwards is the single most common failure, and it reads as a writer who has
padded the easy parts and rushed the hard ones.

| zone | default | what it looks like when right |
|---|---|---|
| **Derivation, formulation, mechanism, setup** | **detailed** | every step shown, every symbol bounded, every constant sourced. A reader can re-derive the quantity and re-run the experiment without asking you a question |
| **Prose around tables, results, verdicts, case narration** | **concise** | one line of judgment per table, one bullet per arm, the number in the cell and nothing restating it |

### Be detailed here

**A formulation states its derivation, not just its result.** From the definition to the quantity you
actually measure, show the intermediate steps. If a quantity is a difference of two logged things, say
which two and why the difference is the right object. If a bound is claimed, prove it or name the
assumption it rests on. **A single line of math with no derivation under it is not a formulation, it is
a citation of a formulation you did not write down.**

Also detailed: **why a mechanism should work** before its numbers arrive, and **the setup**, to the
level where someone else can reproduce the run. These are the parts a reader cannot reconstruct from
your tables, so they are the parts that must be on the page.

### Be concise here

Everything downstream of a number. The table already carries the value, its condition and its
comparison, so the prose beside it adds a **judgment** and stops. See §Tables.

**Count sentence-enders. That one number decides whether the report is written or narrated.** Measured
across three drafted-vs-human pairs on identical content: 句号 per 1,000 characters ran **0.5 – 1.0** in
the human versions against **4.2 – 8.3** in the drafted ones, at roughly twice the total length.

But the count is a symptom. **The disease is that the two zones above get swapped.** In every pair the
drafted version spent its paragraphs *interpreting results* and its one-liners *describing mechanism* —
exactly backwards. Diagnose a long passage by asking which side of the line it is on:

| the passage is | long because | verdict |
|---|---|---|
| a derivation, a mechanism, a protocol | the reader cannot reconstruct it from any table | correct, probably still too short |
| a reading of a table | it speculates about *why* the numbers came out that way | **cut to one line** |

**Speculation about a result gets one sentence, not a paragraph**, however interesting. "X beats Y,
probably because Z" is one line, plus at most one line naming what would test Z. If the mechanism behind
Z deserves three paragraphs, those paragraphs belong in the section that introduces the mechanism, before
any numbers exist.

**The operational test, applied per paragraph: is this a judgment, or is it narration of the table above
it?** A judgment survives as one clause. Narration gets deleted, and if the fact it carried matters, it
becomes a column, a cell parenthetical, or a bolded label.

**The test, applied to any paragraph: could the reader have derived this from the display object next
to it?** If yes, cut. If the answer is no because the paragraph carries a derivation, an assumption, or
a mechanism, it belongs in the detailed zone and is probably still too short.

---

## Style

### Vocabulary, both modes
Technical terms stay English and unbolded, in their field-standard form: `rubric`, `reward`, `policy`,
`rollout`, `GRPO`, `advantage`, `Blind / Spurious / Inversion`, `harness`, `criterion`, `curriculum`.
Do not translate a term the reader will meet again in a paper.

### `zh` mode

**中文的用词、标点与句式规则全部在 `writing-style-zh`，这里不复述。** 两份复制会各自漂移，而漂移是静默的——这正是 `naming-config` 对近似重复配置禁止的那件事，修法是指过去而不是分叉。写 `zh` 报告前读那一份，它管：自造比喻的禁令、「不是 X，是 Y」的每文档一次预算、「——」每 1,000 字一个的预算、反射式强调（唯一/正是/本身/真正）、连接词密度、译不出来就用英文、指代与量词跟前文对齐，以及标题点名主语与冒号测试。

这里只留周报特有的那一条：**句号密度**，它测的是报告被写出来还是被叙述出来（见 §Where the length goes）。

### `en` mode
Plain declarative English under `writing-style`: no em-dashes, no semicolons, no lists unless asked.
The failure here is the mirror image, English that reads as translated Chinese, usually from keeping
the Chinese clause order or a topic-comment opener.

### Both modes
Never write a heading or sentence that only exists to introduce the next one.

### Headings
```
zh   ## 挑战（Challenge）：上周 diagnosis 的回顾
     ### 主要结果
en   ## Challenge: what last week's diagnosis established
     ### Main result
```
In `zh`, put the English term of art in parentheses after the Chinese name, top level only.

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

**The H1 is the exception.** It names a **durable subject** — the standing problem, or the system under
study — as a short noun phrase, with no number, no comparative verdict, and no draft marker. Both forms
are attested; what is invariant is that nothing in the title goes stale when a later run flips a result.

| | |
|---|---|
| ✗ `【目标版】四类失败模式的五个 epoch：机制 A 的振荡与机制 B 的稳定` | this week's result plus a draft tag; nothing in it survives to the next report |
| ✗ `方法 B 优于方法 A` | a verdict, stale the moment a later run flips it |
| ✓ `Training-time PO-MDP Controller for RSI Training` | names the system under study |
| ✓ `开放端训练挑战：任务探索空间的多样性，反馈的可靠性` | names two standing problems |

The check: **could this exact title head next week's report?** If not, it is a finding wearing a title's
clothes, and the finding already has a home under the table that produced it. Take the title's nouns
from the problem names bound in the Formulation recipe's move 4, so the title and the taxonomy speak one
vocabulary. A title that headed one week's report is free to become a section heading in the next.

**Headings carry no numbers.** A heading number exists so that something can point at it, and with
cross-references cut to at most one (§What to cut) the ordinals have no referent left while still costing
a renumber on every insertion. Delete the ordinal, keep the name. Any numbered list *inside* a section
still starts at 1, never 0.

**When the system has a store, name the sections by which direction data moves through it.** A pipeline
described component-by-component makes the reader hold the dataflow in their head; described by
write-then-read it is already sorted. The pattern is one heading per direction with the component name
in parentheses:

| | |
|---|---|
| ✗ `dynamics store、diff 算子与 agent 装配` | three component names, no order among them |
| ✓ `训练动态 (memory write)` then `PE (memory read/utilization)` | the store is written here, read there; everything else nests under one of the two |

This is worth reaching for whenever the week's object is a thing that accumulates. It also silently
enforces the arc, because writing precedes reading.

**Count H2s before writing them: two or three, not seven.** Depth carries the grouping. A mechanism's
setup and the numbers it produced are one section, not two, so a reader compares a row against the
mechanism that produced it without scrolling. **The sections that pointed at each other in the draft are
the ones to merge**, and merging them is what makes the cross-reference ban affordable. Per-component
detail nests under the setup it belongs to, however deep that goes.

### Body
- Bullets use `+` at top level, `-` then `*` nested. Not `*` at top level.
- **Bold an operand, not a proposition.** A number, a name, an action, or a one-clause verdict — something
  a reader could lift into a table cell. Measured: 12% of the human doc's bold spans outside tables
  contain a 。, against 40% of the drafted one's. A bolded full sentence followed by its unbolded
  unpacking is the tell; bold the operand inside it and leave the rest plain.
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

**Sentences that justify the document's own layout.** 「这就是要把 X 放在第一张表的原因」, 「所以主结果
表把 X 放在第一张」, 「第 1 项排最前，因为…」. The order is either right, in which case the reader
follows it without being told, or wrong, in which case reorder. The meta-commentary ban above does not
catch these: they rate the *arrangement* rather than the content.

**Internal cross-references.** Keep at most one, and only to name where a shared definition lives.
Measured gap: **1.7 per 10K characters in the human doc against 14.7 in the drafted one.** A pointer is
three promises — the target still exists, still says the same thing, still carries that number — and an
edit pass breaks all three silently. The fix is almost never to paste the target in; it is to **merge the
two sections** (§Headings) so they are adjacent, or to write the **mechanism** where the pointer was:
「分数买到了，能力没全买到，强干预带来的强 overfitting，早期变化过大」 carries the finding with no
arithmetic left to drift.

**A synthesis or insight section whose subsections are reworded copies of findings already made under
their evidence.** Check it mechanically: if every subsection of a late section opens by pointing at an
earlier one, it is a second copy of the report. **Delete the section, do not reword it** — the instinct
to reword the duplicate is what produced it. The copy that survives is the one next to its table. In the
contrast that produced this rule, 13 of the drafted version's 15 table-free sections were deleted whole.

Also cut: passive constructions where the actor matters, 「可以看出」/「值得注意的是」openers, and any
sentence that restates its heading. If a paragraph survives being deleted, delete it.

### After a deletion, re-read the sentence you cut into

Most rules here remove text, and a deletion pass leaves wreckage that no rule about *writing* catches.
Three checks, run over the diff rather than the draft. All three are taken from real damage in a
human-edited doc, so they are what a careful editor actually leaves behind:

1. **A two-part claim loses both halves or neither.** 「两处改动各自站得住，合起来是破坏性的」 trimmed to
   「**两处改动各自站得住**」 is not a shortened claim, it is the opposite claim, still bolded.
2. **No colon or causal connective may be left pointing at evidence that is gone.** A bolded sentence
   ending in a bare `：` with nothing under it is the signature.
3. **Pulling a pointer leaves a grammatical hole.** 「问的四件事就是〈第 1 节〉的三种失败模式」 minus the
   pointer is 「问的四件事就是的三种失败模式」. After removing pointers, grep the file for `§` and 〈第 —
   one survivor is one dangling reference.

### Words this project does not use

**这张表搬到 `writing-style-zh` 了**，连同 落差 / 尺子 / 拐杖 / 读数 / 门槛 / 通道 / 判读 / 命中位 / 界 这些新增行，以及 诚实清单、我们在哪里、真正、唯一 那几条。这里不再留副本。

---

## Match a reference draft, when the author has edited one

Once the author has hand-edited a version of the report, **that file is the spec**, not this skill.
Read it before writing, and match it on three measurable things.

### Length: 1.3x the reference, and you know what to cut first

Measured on one pair: the reference ran 21,771 characters and the generated draft 45,062, **2.07x**.
The overflow was not spread evenly. It sat in two places, and both are the same mistake — pasting an
artifact instead of reporting what it does:

| what inflated it | what the reference had instead |
|---|---|
| three prompt templates and four JSON schemas quoted in full | two tables (the diagnosis items, the action set) |
| a full worked case: rollout excerpts, regrade table, two rounds of JSON | the section heading, and nothing yet |

**Prompts, schemas and full traces are appendix material.** In the body, a prompt becomes the table of
what it asks for, and a trace becomes the one line that says what changed. If the draft is over 1.5x,
cut those before touching anything else — no amount of sentence editing closes a 2x gap.

### Section order: heading, one line, figure, table, bullets

The reference opens a section with the picture, not with prose. Prose that arrives before the figure
is prose the reader skips to get to the figure, then re-reads.

```
### 路线 A：通过 Guidance / Rollout Intervention 改善探索
核心思路是：**在给定 reward 下扩大或引导 policy 的探索空间……**      <- one line, optional
<img src="..." width="768">                                          <- the figure
| 类型 | 代表工作 | 核心机制 |                                        <- the table
+ **claim**：数值                                                    <- the reading
```

### The caption names the figure; the bullets read it

When the image itself is embedded, **the caption line carries the figure name and its path and
stops**. Everything a reader should conclude from the picture goes in the bullets under it, where it
can carry its numbers. A caption that runs to four ｜-separated clauses is a paragraph wearing a
caption's clothes, and the reference has none.

### Group the analysis under one heading, nest the rest

Parallel `###` sections named 消融分析 / 效率分析 / 样例分析 read as three unrelated appendices. The
reference collapses them into one `### 分析` and nests: `#### Failure pattern 动态`,
`#### 控制端口`, `#### 额外开销`, and under that last one `##### 摊还成本` / `##### 成本效益` /
`##### 优化策略`. Depth carries the grouping — the same rule as §Headings, applied to results.

### Two comparisons per headline result, not one

A best-result claim reports **both** the gain over base and the gain over the strongest baseline.
Against base alone the number is unfalsifiable as a contribution claim: base is what everyone beats.

```
+ HarnessRL 两列都最好：
    - 对比 base：in-domain +0.0395，OOD +0.0434
    - 对比 AMARIS：in-domain +0.0275，OOD +0.0324
```

### A cost section ends with what to do about it

Any 成本 / 效率 analysis closes with a short 优化策略 subsection: two or three executable directions.
A cost table with no exit reads as an apology.

### When a component list enumerates parts, the heading says what each part fixes

`x_t`, `g_t`, `c_t` are not self-explaining. The reference titles them with the failure each one
repairs — 样本演化（解全 1）, guidance 演化（解全 0）, 诊断维度与原子动作（解虚假 reward）— so the
list doubles as the argument for why there are three.

## Tables, and the prose around them

> **One quantity, one table. A number has one home. The prose beside a table adds a judgment, never a
> reading lesson.**

Tables survive editing at more than twice the rate of prose: **55% of table rows retained against 21% of
prose blocks.** A table is the only object in a report that holds a number, its condition, and its
comparison in one place, so a claim that can live in a cell should.

### One home per number

**A number appears once per section.** Two statements of the same figure on one screen, slicing it
differently — a ranking table and the verdict bullet under it — are fine and are how a verdict reads.
**The same figure in two sections is a drift bug**, whatever justifies it.

In the contrast that produced this rule, one measurement appeared in three sections as `19 分里有 17 分`,
`21 分里有 9 分`, and `21 分有 9 分`. The first was correct, the other two were invented at the restating
site, and the cross-references between them were what kept the contradiction invisible for three drafts.
**Restating a number across a section boundary does not duplicate it, it forks it.**

### One table per quantity

A second table that re-slices numbers the first one already gave is a copy, and copies drift. Delete any
table derivable by arithmetic from a table you are already printing:

| ✗ the re-slice | where it belongs instead |
|---|---|
| a snapshot table of the final time point | it is the last column of the over-time table |
| a share-of-subtotal table | a `%` parenthetical in the cell, or in that row's verdict bullet |
| a delta table between two points | a Δ **column** on the table that already has both points |
| the same numbers rolled up side by side "for comparison" | the ranking table, if you have one |

**Keep the delta column, kill the standalone delta table.** A derived table earns its place only when it
adds a column that is a **judgment rather than arithmetic** — a per-row verdict, a best/worst call, a
rank. That column is why the table exists, and it cannot be recomputed from the others.

**One printing per defining equation.** An equation restated at the top of the results section is a
re-sliced table in another costume.

**A column holding one value in every row is not a column.** Delete it and state the constant in one
sentence under the table. If that constant *is* a finding, the sentence is the finding and the column was
hiding it in the margin. Where the same field varies in a neighbouring table, that table keeps its column,
and the contrast between the two is the point.

### Write the sentence before you draw the table

A table earns its rows by making the reader scan two axes. **If the whole table reads out as one sentence
carrying two numbers and a ratio, that sentence is the deliverable and the table was scaffolding.** Keep
the table only when collapsing it loses a comparison the reader has to make. This catches the small table
the arithmetic test above misses: a five-row, two-column table of derived fractions is not a re-slice of
anything, and it still collapses to 「八次里四次，正好一半」.

Order the result tables the way the definitions section introduced their quantities — left to right
across the summing equation, the summary quantity last — and then delete the sentence explaining why you
ordered them that way (§What to cut).

### Where the verdict goes

**One verdict block, immediately after the last table of the results section, with nothing between it and
the tables**: a per-category ranking table, then one bullet per arm. Not eight interpretation subsections
interleaved among the tables.

**A worked example is a subsection of the result it illustrates, placed after the verdict, never a
top-level peer.** A peer-level example forces a pointer in both directions and states the finding twice,
once as a claim and once as a case. Placed after the verdict it reads as verification of a claim already
made, which is the job it can actually do.

### Never teach the reader how to read a table

The direction of good goes in the label. Everything else goes in the cell it repairs.

| | |
|---|---|
| ✗ a subsection `读这张表的三个陷阱` | three corrections, each belonging in the cell it corrects |
| ✗ a document-wide preamble `两条读表规则，全文通用：` | a rule with no number attached is a rule nobody applies |
| ✗ a paragraph `**X 要按占 M 的比例读，否则会读反**` | put the share in the cell: `.150（占 M 的 51.9%）` |
| ✗ column header `（越低越好，但要连 M 一起读）` | `（越低越好）` |
| ✓ cell `+.001（**振荡**）`, `−.045（后段走平）` | the anomaly is attached to the number it repairs |

**This is a placement rule, not a deletion licence.** A denominator, a filter, an n, or a caveat that
changes what a number *means* is load-bearing — §Body requires it — and it still appears, as a
parenthetical inside the affected cell, inside the definition row, or inside that row's verdict bullet.
The *block* gets deleted, never the caveat. A caveat with no cell small enough to hold it usually means
the table is measuring two things.

---

## Figures

Figures are **generated separately**. Never inline plotting code in the report, and never block drafting
on a figure existing.

**A placeholder is a drafting device with a deadline: it must not survive into the delivered document.**
While drafting, emit a placeholder plus a spec the generator can act on:

```markdown
<!-- FIG fig-drift: figures/drift.png -->
> x 轴 step｜y 轴 d∠（子空间漂移）｜曲线 = 4 条 arm，legend 用 arm 名｜灰带 = shuffle null
```

**In the delivered document every figure is embedded at the point of use, named, with its path visible**
— the reader sees the image, knows which figure it is, and can find the file that produced it:

```markdown
![fig-drift](figures/drift.png)

**图：`fig-drift`（`figures/drift.png`）** x 轴 step｜y 轴 d∠｜4 条 arm｜灰带 = shuffle null
```

Name and path are not decoration. They are how a reader regenerates the figure, how a reviewer checks it
against the analysis code, and how you find it again in six weeks. A figure referenced but not shown, or
shown but unnamed, fails §Format dealbreakers.

**Figure content and style are owned by `docs-figure`.** Read it before generating. The rules that bite
most often in a weekly report:
- **Nothing on the image that the report already says.** No headline claim, no explanatory sentence, no
  bullets copied out of the text. The report is the caption.
- **Parallel arms merge into one figure** with a legend keyed by arm name, never one figure per arm.
- **Quantities split.** Merge across arms, split across metrics. A multi-panel strip of four quantities
  is one figure the reader must navigate instead of four they can each read beside their own table.
- **Every result table showing a quantity over time gets a figure immediately above it.** The table
  under it carries the values, so the figure's own line carries only its name, path, axes, and marker
  convention.
- Longitude (over steps) and latitude (across arms at one step) are different figures.
- One generator per figure, isolated in a `figures/` directory beside the report.

**A figure is the substitute for deleted interpretation prose, not a casualty of the same pass.** In the
contrast that produced these rules, prose halved while the figure count went from four to seven. When you
delete a paragraph describing the shape of a curve, the shape still has to arrive somewhere: put the
figure above the table and let the reader see it.

**Provenance is a cell property, not a preamble.** A table containing any projected, estimated, or
borrowed value marks it **in the cell or in the column label**. Never define a marker convention in a
document-level note, because that note is the first thing an edit pass deletes and it takes the definition
of every marker with it — leaving solid-vs-hollow points on the images and provenance tags in the prose
with nothing defining either, and aggregate tables of projections reading as measured.

Generate with `output-analysis` when the runs are in the `layout-output` tree, otherwise a small script
or `.tex` beside the report.

---

### Where a figure sits relative to its heading and its table

Measured against a human-edited weekly on the same content, figures land in one of three positions, and
each carries a different job:

| position | what precedes it | use when |
|---|---|---|
| **directly under the heading** | nothing | the figure *is* the section's claim; the heading already named it |
| **under a bold one-line label** | `**direct PE with memory：一次 memory read, 一次 analyzer 调用, 一次 updater 调用, 一次 memory write**` | several figures compare configurations, and the label is the only thing that differs between them |
| **after the table** | the table it visualises | the numbers are the evidence, the figure is the shape |

**Sibling figures share one label pattern and skip their captions.** Three pipeline diagrams in a row,
each under a bold line naming its call sequence, need no `**图：**` line apiece — the labels already
distinguish them, and three captions would repeat the three labels. Caption a figure that stands alone,
not one standing in a series.

### Nest the mechanism, do not flatten it

Measured on the same content: the human-edited version used 8 `###` and 7 `#####`; the drafted one used
25 `###` and no `#####`. Flattening turns one mechanism with parts into twenty-five siblings, and the
reader loses which part belongs to what.

**One `###` per claim; the machinery under that claim goes to `####` and `#####`.** In an implementation
section, `#### 外层：一次 harness update` legitimately owns `##### JIT-diff`, `##### 跨步记忆`,
`##### 跨步检索与跨样本检索`, `##### 工作流程` — four aspects of one mechanism, not four sections of the
report.

### One results subsection per claim, not per slice of the same data

The same measurement re-cut along another axis is not a new finding. Measured on one pair: the
human-edited version carried **主要结果 → failure pattern → 消融** and stopped; the drafted one had ten
results subsections, six of which were the same nine arms re-sliced by scope, by bench, by epoch, by
failure class, by rate, by correlation. Each slice was individually true and collectively noise.

**Before adding a results subsection, state the claim it makes that no existing subsection makes.**

+ genuinely new claim — keep it
+ same claim at a finer grain — it is a **column** in the existing table, or a second panel in the
  existing figure
+ no claim, just more of the data on display — cut it

A results section with three subsections and one claim each gets read; one with ten gets skimmed, and the
three claims that mattered are lost among the seven that did not.

## Citing a paper costs one line

A paper enters a weekly as **one bolded mechanism phrase plus the operative detail**, on a single line
under the citation. Not a paragraph, not a summary of its contributions.

```markdown
Agentic Rubrics as Contextual Verifiers for SWE Agents, Scale AI, ACL 2026

+ **Rubric as execution-free verifier:** candidate patches are scored against this contextual
  rubric **without running tests**
```

The bolded phrase is the thing you will reuse later in your own argument; the rest of the line is the
detail that makes it checkable. Everything else about the paper belongs in the literature list, not here.

**Bold the operative clause inside quoted external text too.** A rubric criterion, an abstract sentence,
a spec line — quote it verbatim, and bold the two or three words your argument turns on, so a reader
scanning the quote lands where you need them:

```markdown
+ "The fix modifies the **correct location(s):** hydra/_internal/instantiate/_instantiate2.py, ..."（4.0）
```

**The one-line form is also a correctness device.** Compressing a paper to a single mechanism phrase
forces you to name what it actually does, and a wrong compression is visible immediately. A paragraph of
paraphrase hides the same error: in the pair that produced this rule, a drafted report described an
agentic verifier as one that *applies the patch and runs the named test*, while the cited work is
explicitly **execution-free**. The one-line form would have made the contradiction unmissable; the
paragraph did not.

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

This section fails most often, so it has its own recipe. **It is also the section that gets shortchanged
while the results prose runs long** (§Where the length goes), so give it the room. Five moves, in order:

1. **The objects.** State the space, its indices, and their bounds, paired (`t ≤ T`, `i ≤ I`). A
   reader must be able to write down the shape. **Every dimension gets a symbol and a bound, never this
   week's configured value** — a constant baked into an object's type silently re-scopes the formulation
   to one run. The value belongs in the setup section, where changing it invalidates nothing.
2. **The equation, and the derivation to it.** One boxed statement of what is being optimised or
   measured, and **the steps from the definitions in move 1 to that statement**. If the measured quantity
   is a difference or ratio of two logged things, say which two and why that combination is the right
   object. If a bound or a partition is claimed, prove it in two lines or name the assumption it rests
   on. **A line of math with nothing under it is not a formulation, it is a citation of one you did not
   write down**, and the reader cannot tell whether it holds.
3. **为什么这个形式化能解释已量到的现象** / *why it explains what was measured.* Map each measured failure mode onto a term. This is the
   part that makes it a formulation rather than notation: if a measured phenomenon has no term, the
   formulation is incomplete and the report should say so.
4. **每类绑定一个问题名和一种干预** / *bind each category to a named problem and to what moves it.* Move 3
   runs phenomenon → term. This one runs term → **the standing problem it is a proxy for**, plus the kind
   of change that moves it. Label the equation's underbraces with problem names, not with structural
   descriptions of the partition (`_{探索不够}`, not `_{没有组内信号}`). Do it once, here, and every later
   table reads as movement on a problem instead of movement in a metric.
5. **它带来什么新的可做的事** / *what it makes possible.* What action or estimator becomes available that was not before.

**Where two categories look alike on the headline metric, say in one sentence that their fixes point in
opposite directions.** This is the sentence that pays for the section, and it is the one a drafted
version reliably omits. Without it, a later result showing one category converting into another needs
vocabulary invented on the spot, and the reader meets the report's best finding as a surprise instead of
as the thing the taxonomy predicted.

**The prose under a definition table says which rows matter and what repairs each of the rest. It never
re-narrates the table's own 含义 column.** One sentence, then move on.

| | |
|---|---|
| ✗ `X 表示…，Y 表示…，Z 表示…` | the 含义 column already said this |
| ✓ `只有 Y 那部分有用。X 和 Z 都不产生信号，但含义相反：X 要靠抬高一侧来修，Z 要靠换一个更难的目标来修。` | ranks the rows, and gives each dead one its own repair |

A formulation section that does 1 and 2 but not 3 is notation, and a reader is right to ask what it
bought. One that states the equation without deriving it is a claim the reader has to take on trust. One
that does 3 but not 4 makes the reader carry a second vocabulary for the rest of the report, and leaves
the title with nothing to be about.

---

## The mechanism-ladder section

**The word `ladder`, the word `rung`, and 阶梯 never appear in the report.** `writing-style` rule 15
bans them as metaphors, and a row labelled `rung 2` is that metaphor wearing a table header. The
recipe below is how you *build* the comparison; what ships is a table whose first column names the
thing that actually varies down it — who produces the component, or what data each level sees. Refer
to a level by that value（「prompted 改写这一档」）, never by its index.

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
5. **State how your build deviates from the published one directly under the table**, before any prose
   about the mechanism's internals. Not in an appendix, not two paragraphs into that rung's own
   subsection. Citing a paper borrows its credibility, and a description written from memory of the paper
   rather than from the config will overclaim a capability the implementation does not have, after which
   the downstream arguments lean on it. The note is a **correction**, not a caveat: 「注：本实现与原方法
   的区别：没有 X 这一步；只有单实例的跨轮分析，没有跨样本影响。」

**`what it buys` and a prediction column look identical and are not.** `What it buys` argues a *design's*
contribution and stays. **A column or paragraph predicting which of this report's own metrics a rung
should move is a conclusion filed early, and it goes** — the column, the per-row prediction text, and the
paragraph arguing why a rung ought to improve a named quantity. The results table is a few pages later.
Let it answer. This holds even when the prediction turns out right, because a reader who was told the
answer first cannot read the result as evidence.

| ✗ | ✓ |
|---|---|
| a trailing column `该修哪一端`, filled with metric names from the results section | the four columns above, and nothing else |
| `同上，但每次改之前先检索历史` | the exact scope of data the rung sees: `历史分析（1, 2, …, t−1）` vs `单轮分析（t−1）` |
| a paragraph `这一级为什么该降 X` | delete it |

Two adjacent rungs differ by a **stated range of data or a named component**, never by a sentence of
narrative. Allow at most one clause of design rationale per rung, for a schedule or constant that would
otherwise look arbitrary, and cut that clause before it turns into a claim about what it achieved.

Read the "existing implementation" column top to bottom: it should describe a complete, runnable system
with none of the week's new machinery. That configuration is the floor, and it is what makes the claim
falsifiable.

## Evaluation: two sections, not one

Splitting these is what lets a reader judge whether the plan could settle anything.

### (a) Research questions

**Build this table; do not ship it.** It is the check that the report's assertions are falsifiable, and
it lives in the plan doc (§Forward-looking material). One row per premise the earlier sections asserted
as fact. Not the experiments you feel like running.

| # | premise | if it is wrong | falsifying experiment | what it needs |
|---|---|---|---|---|

A premise with no falsifying experiment is a belief, and the report labels it as one. **Every row names a
premise stated earlier in this same report**; a row about a design nobody has built is a backlog row and
belongs in `docs-plan` (§Forward-looking material). `what it needs` names a prerequisite, never a cost to
rank by.

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

## Forward-looking material: where it goes, what shape it takes

> **An open question lives under the number that raised it. Work you have not run gets one sentence,
> not a section.**

### Placement

Every open question sits inside the subsection that raised it, within a few lines of the number, row, or
figure that provoked it, one line, phrased as a question, and **carrying one visual marker reserved for
the author's own voice** — whatever the rendering platform gives you, used consistently and for nothing
else. The same marker carries the deviation notes of §The mechanism-ladder section: both are the author
stepping out of the report to say something the tables cannot.

**That marker's real job is wider than questions: it marks whatever is least settled.** It goes on the
newly added domain, the arm that has not been decided, the parameter still written as a guess. Observed
uses in one report: a whole table row (the domain added this week), a heading fragment, and a bare
`(7-8B?)` where a model size had not been chosen. All three are the same act — telling a reader which
parts of the page the author would not yet defend. A report with the marker on nothing is claiming
uniform confidence it does not have, and a reader who later finds the soft part unmarked stops trusting
the firm parts too.

```markdown
**关键读数：撤除前 +19，撤除后 +2。**

> **启发：强度取决于输入的数量，还是输入之间的结构？能不能更细粒度地控制？**
```

**No item's only appearance is in a closing list.** A closing section may collect what is still unknown,
but a reader who stops at the last table must already have met every open question beside the evidence
that raised it. An item reachable from its evidence only through a chain of pointers is an item nobody
will connect to its evidence.

### Form

**A sentence about work that has not been run must not be assertable as a finding.** Write it as a
question, or as a named missing measurement. Never as a declarative about what it would achieve.

| ✗ | ✓ |
|---|---|
| `这正好补上 (a) 和 (b)。` | `这补不补得上 (a)？没测过。` |
| `这是本轮最便宜的一条。` | name the cost, or delete the sentence |
| `后两条都不需要新机制。` | a claim about code nobody has written |

### Weight

Work you have not started gets **at most one sentence naming the knob it would change**. No per-option
subsection, no `方法 / 为什么 / 已有支持 / 风险` template, no comparison table of unbuilt options, and
**no benchmark numbers from other people's papers marshalled to argue for them.** Citations for arms you
actually ran stay; that is the ladder's `出处` column. The rule is about structural weight: a proposal
nobody has built should never be the most quotable page in the report.

### The terminal section is a list of names, and the premise table is not in the report

**Two consecutive weeks, the human deleted the premise/falsification table outright.** In its place, a
closing section of three bare bullets — a name each, no columns, no falsifying experiment, no
prerequisite:

```markdown
## 计划
+ Case-analysis
+ Trainable just-in-time diff
+ Internalization
```

Take this as settled rather than as two accidents. The premise table is a **working artifact**: it is how
you check that the report's assertions are falsifiable, and it belongs in the plan doc (`docs-plan`)
where the next week's work is scheduled. Building it is still worth doing — a report whose premises
survive that check reads differently from one whose premises were never tested — but the table itself
does not ship.

What ships is **three to five names**, each one word or phrase that a reader already met in the body.
If a name has no antecedent in the body, it is a backlog item and it goes to the plan doc with the table.

`what it needs` in the §Evaluation template stays a **prerequisite, not a price**; the moment that column
carries comparable costs, the table has become a ranked backlog. Row 9 keeps only what is still unknown,
because a terminal section restating delivered conclusions is a second copy of the report (§What to cut).

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
- **Numbered headings**, which exist only so a cross-reference can point at them. Any list *inside* a
  section still starts at 1, never 0.
- **A section file whose top heading is H1**, so the assembled report has one title per section.
- **A figure placeholder shipped in the delivered document**, or a figure shown without its name and path.
- **A formulation whose equation has no derivation under it**, while the results prose runs three
  paragraphs per table.
- **A mixed-language document**, or a term of art translated into the prose language.
- **A heading that glosses its own title** (`挑战：这条线在追什么`).
- **Meta-commentary** telling the reader which part is important.
- **A coined term where a standard one exists**, especially one that redefines a framework's word.
- **An evaluation plan with no benchmark description**, so no one can judge what a number would mean.
- **A ladder whose lower rungs are strawmen the report invented**, rather than published mechanisms.
- **A title that states this week's result** instead of naming a durable subject.
- **The same number stated in two sections.** They fork, and the cross-reference between them hides it.
- **A second table that re-slices numbers already tabulated.**
- **A subsection teaching the reader how to read the table above it.**
- **A synthesis section that is a second telling of findings already made under their evidence.**
- **A ranked, costed table of options nobody built.**
- **A premise/falsification table shipped in the report** instead of built in the plan doc.
- **A paper summarised in a paragraph** where one bolded mechanism phrase would do.
- **A report with the author's-voice marker on nothing**, claiming uniform confidence.

---

## Steps

1. Inventory the inputs: codebase diff, analysis subdirs, run outputs, paper links, figures.
2. Map them onto the staged table. Decide which sections exist. Say out loud which are omitted.
3. **Pick the arc** (§The report is a self-contained story) and order the sections by it, not by the
   order the work happened in.
4. Draft the spine: the Challenge and the Formulation, because they carry the argument. Give the
   Formulation its derivation now, while you still remember why the quantity is the right one.
5. Fill evidence and mapping sections from real numbers and real citations.
6. Emit figure placeholders with specs, do not generate inline. **Replace every placeholder with the
   embedded figure, its name and its path before delivering** (§Figures).
7. Write the Evaluation Plan from the premises the earlier sections asserted.
8. Close with the honest list. Read it back: does someone who missed the week know what changed and
   what is still unknown?
9. **Check §Format dealbreakers**: no section numbers anywhere, every section file topping out at H2,
   every figure embedded with name and path, no cross-references, one language.
10. **Count 句号 per 1,000 characters** (§Where the length goes). Above ~2, the report is being narrated
   rather than written, and the 不是/——/所以 budgets will be blown as a side effect. Delete sentences
   before editing words.
11. **De-duplicate, then read your own diff.** Grep for every number appearing in two sections and every
   claim stated twice, keep the copy next to its evidence, and delete whole sections that turn out to be
   second copies — reworking the duplicate is not a fix. Then run §After a deletion over the diff rather
   than the draft, and grep for surviving `§` and 〈第.

## Judging a draft against the reference

When a reference draft exists, the check is mechanical enough to hand to a fresh session that carries
none of the writing context and cannot be argued into agreeing. Give it the reference, the draft and a
rubric whose every row is countable — length ratio, prose paragraphs over three lines, bullets carrying
more than three numbers, caption lines over one line, parallel `###` that should nest, banned words,
negation pivots, document-self-description sentences — and require an evidence quote from BOTH files
for every finding. A rubric row that cannot be counted will be answered with an impression.

Have it end on a three-way verdict (adopt / revise / rewrite) and the three highest-priority fixes,
because a list of thirty findings does not say where to start. One worked harness lives at
`BrainStorm/0903/style-judge/` (`rubric.md` plus `judge.sh`, which runs `claude -p --model opus` or
`codex exec` on the pair).

## Companions
`writing-style` (**`en` mode only**) · `writing-style-zh` (**`zh` mode only** — the Chinese word,
punctuation and sentence rules live there in full, and this skill does not restate them) ·
`docs-figure` (what the embedded
figures may contain) · `output-analysis` (comparing the runs behind them) · `docs-plan` (the actionable plan a report's next-week section points at) ·
`layout-workspace` (where reports live) · `conventions` (the family index).
