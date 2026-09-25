---
name: docs-caption
description: "Write a paper's figure and table captions: open with a noun phrase that names the float's object and the paper's method in the paper's own terms, tell an overview figure's flow in one or two sentences, name panels by content or position and never by letters the figure does not draw, and keep protocol, legend text and findings out, learned from the author's rewrites of eight HarnessRL captions."
when_to_use: "Use when writing, revising or reviewing any figure or table caption, when a caption opens with a generic label such as 'Results at two scales', reads as colon fragments ('Memory M_t: rollouts, ...'), enumerates (a)(b)(c) that are not drawn on the figure, restates the legend or an axis label, or carries metrics, checkpoint selection or notation that the setup already states."
---
# Skill: docs-caption

## Purpose
A caption names what the float shows in the paper's own terms and says nothing the float or the setup
already says. This skill owns the caption's wording and shape for every figure and table in a paper.
`docs-figure` owns what the image contains and `docs-table` owns the grid, its number format and its
marks, and both defer here for the caption.

The failure it guards against is a caption that is long and still unhelpful: a generic subject
("Results at two scales"), then a row of `Label: value.` fragments that restate the legend, define the
metric a second time, and name panels by letters nobody drew. The author rewrote eight HarnessRL
captions in one pass, and every rewrite was shorter and named the paper's object more exactly.

## Contents
- [When to Use](#when-to-use)
- [The principle](#the-principle)
- [The shape of a caption](#the-shape-of-a-caption)
- [The HarnessRL rewrites](#the-harnessrl-rewrites)
- [By kind of float](#by-kind-of-float)
- [Checklist](#checklist)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Writing a caption for a new figure or table, in a paper, a report or an appendix.
- Revising captions before submission, or after the author says a caption is verbose, telegraphic or
  names panels that are not there.
- Reviewing a caption someone else wrote, with the [checklist](#checklist).
- Moving a figure between panel layouts, which changes how its panels are named.

Not for:
- what the image may contain, its labels, legend and panel titles (`docs-figure`),
- the table's columns, number format, and where bold, underline and margins go (`docs-table`),
- which ablation rows exist (`docs-ablation`),
- the prose paragraph that cites the float (`writing-paper`, `docs-analysis`),
- polishing the caption's sentences once the content is right (`writing-chatgpt`).

---

## The principle

> **A caption names what the float shows in the paper's own terms, and says nothing that the float
> or the setup already says.**

Everything a caption could carry has a better home except two things: the name of the object shown,
and the meaning of any mark the reader cannot decode from the float itself. The legend already names
the series, the axis already names the quantity, the in-panel label already names the panel, the setup
already defines the metric and the checkpoint rule, and the results paragraph already states the
finding. A caption that repeats any of these is read twice, and the second copy drifts the next time
one of them is edited.

## The shape of a caption

1. **The lead: a noun phrase naming the object and the method.** `Quantitative results of
   \ourmethod{} on ...`, `Training dynamics of \ourmethod{}`, `Ablations of \ourmethod{} on <the
   ablation axes>`. The words come from the paper: its section titles, its module names, its corpus
   macro. A float compares the method against baselines, and the lead still names the method, because
   the float is evidence about the method.
2. **For an overview or pipeline figure, one or two full sentences of flow** in place of the lead's
   full stop: what conditions what, and how the parts interact, in the order the drawing runs.
3. **The panels' contents, when the float has several and the lead does not already cover them**,
   joined as a list after a colon or named by position (`Top left:`, `Right:`). Letters only when the
   figure draws them.
4. **The marks that encode something invisible otherwise.** In a table, `\textbf{Bold}: best.
   \underline{Underline}: second. Parentheses: \ourmethod{}'s margin over the best baseline.` In a
   figure, a symbol drawn without definition (`judge scores $S$ and rubric-free quality order $Q$`).

Nothing else. A results or table caption runs ten to thirty words, an overview or composite
caption up to about sixty. The caption sits above a table and below a figure.

---

## The HarnessRL rewrites

Each pair is the caption as it stood in `main.tex` and the author's rewrite. The rule it teaches
follows each one.

**Figure 1, a composite of two plots and an overview, with no drawn letters.**

```latex
before: Rubric-reward failures under GRPO~\citep{...} on \corpus{} at Qwen3.5-4B and the \ourmethod{}
        control loop. (a) Failure classes on one criterion, with judge scores $S$ and rubric-free
        quality order $Q$. (b) Failure-class shares and GRPO's training reward against rubric-free
        quality on held-out tasks. (c) Control loop over $p_t$, $g_t$ and $c_t$.
after:  Rubric-reward failures under GRPO~\citep{...} on \corpus{} at Qwen3.5-4B, and
        harness-controlled RL training in \ourmethod{}. Top left: failure classes on one criterion,
        with judge scores $S$ and rubric-free quality order $Q$. Bottom left: failure-class shares and
        GRPO's training reward against rubric-free quality on held-out tasks. Right: harness
        $(p_t, g_t, c_t)$-controlled RL training.
```

The figure draws no letters, so the caption names the three parts by where they sit, and in a
two-column layout position is the only unambiguous order. The right panel is named by the title of
Section 2.1, `Harness-Controlled RL Training`, not by a paraphrase ("control loop") that the reader
must map back to it. The author rewrote the panel names and the right panel; the lead takes the same
term so the caption does not name one object twice, and keeps `\ourmethod{}` so it still names the
method. `$S$` and `$Q$` stay because the cards draw the letters without defining them.

**Figure 2, the method overview.**

```latex
before: The \ourmethod{} loop: harness $\harness{}_t=(p_t,g_t,c_t)$ around GRPO. Memory
        $\mathcal{M}_t$: rollouts, rubric states, outcomes, retrieved as $E_t$. Evolver
        $\mathcal{E}$: attribute, propose, critique, update $\harness{}_{t+1}$. JIT critic: rollout
        and rubric updates measured against the frozen policy, sampling updates sign-checked, and
        secondary rubric operations accepted with primary repairs.
after:  \ourmethod{} runs an RL loop conditioned on a training-time harness
        $\harness{}_t=(p_t,g_t,c_t)$, which controls task sampling, rollout guidance and the rubric,
        respectively. The harness co-evolves with the policy: it retrieves evidence from the
        training-time memory $\mathcal{M}_t$, attributes failures, and is iteratively refined by a
        proposer and JIT critic loop.
```

An overview caption tells the flow in sentences, because the reader holds the caption beside the
drawing and follows the arrows with it. The before is an inventory of `Module: contents` fragments,
and its last fragment is the critic's acceptance protocol, which is Section 2.3's job. The after
names each part by the name drawn on the figure and the paper's own concepts (co-evolve, training-time
memory, proposer and JIT critic loop), and says how they connect.

**Table 1, the main results.**

```latex
before: Results at two scales. In-domain: rubric mean. OOD: one benchmark per domain, scored by its
        own metric. \textbf{Bold}: best. \underline{Underline}: second. Parenthesis: \ourmethod{}
        margin over the best baseline. OOD benchmarks: MedQA, GPQA-Diamond, WritingBench, RoleBench,
        IFBench.
after:  Quantitative results of \ourmethod{} on the five-domain \corpus{} with Qwen3.5-4B and
        Qwen3.5-9B. \textbf{Bold}: best. \underline{Underline}: second. Parentheses: \ourmethod{}'s
        margin over the best baseline.
```

"Results at two scales" names nothing a reader can locate: whose results, on what. The after names
the method, the corpus and both policies. The metric definitions and the OOD benchmark list are
protocol, already stated in the setup's Dataset paragraph and in Table 2, so they go. The three marks
stay, because nothing in the grid says what bold, underline or a parenthesis means.

**Table 2, the dataset.**

```latex
before: \corpus{} tasks. OOD: benchmark (size), GPQA-D.\ whole. $\mathcal{D}_0$: memory cold start.
after:  Domain composition of \corpus{}: training and held-out sizes per domain, and the
        out-of-distribution benchmark for each.
```

The before is shorthand only its writer can read ("GPQA-D. whole"), and it spends a fragment
explaining the `$\mathcal{D}_0$` column, a calibration split that is setup detail. The author removed
the column, which is the general lesson: a column that needs a caption note to be understood is a
column to question under `docs-table`'s one rule. The after says what the table is for.

**Figure 3, three panels of one quantity, one per failure class.**

```latex
before: Share of pairs by failure class at Qwen3.5-4B: (a) \clblind{}, (b) \clsat{}, (c) \clspur{}.
after:  Fraction of pairs by failure class at Qwen3.5-4B during training.
```

The class names are one word each and sit inside the panels (`blind`, `saturated`, `spurious`, at the
upper middle), so the enumeration repeated them under letters the figure never drew. "Fraction", not
"ratio": a ratio compares part to part (blind pairs per saturated pair), while a fraction, proportion or
share is part of a whole, which is what a percentage of all pairs is. The author asked which word is
common, and a search of ML papers finds "fraction of pairs" far more often than "share" or "proportion",
so the caption, the axis (`Fraction of pairs (%)`) and the text all move to it together: one object,
one name, and the name readers expect. "During training" is the author's, and cheap: it says
what the x-axis spans without naming the axis.

**Table 3, the ablations.**

```latex
before: Ablations of \ourmethod{} at Qwen3.5-4B: out-of-distribution scores at each arm's best
        checkpoint. Subscript $g$ or $c$: single-interface harness. Indentation: removed modules.
        \textbf{Bold}: best. \underline{Underline}: second.
after:  Ablations of \ourmethod{} on evolver components and control interfaces.
        \textbf{Bold}: best. \underline{Underline}: second.
```

The lead now names the two axes the ablation varies, which is what a reader scanning for "does the
critic matter" needs. The author's rewrite gave only the lead; the two marks stay by
[rule 7](#rules), since the grid bolds and underlines and nothing in it says what that means. The
checkpoint rule is protocol. The subscript and the indentation are notation the setup's Baselines
paragraph defines ("a subscript restricts the harness to one interface"), and the column headers
repeat the main table's, so none of them need a caption line.

**Figure 4, three panels over training.**

```latex
before: Harness dynamics at Qwen3.5-4B. Dashed: guidance ceiling. (a) Tasks by guidance fields.
        (b) Accepted rubric updates per 100 steps. (c) Share of accepted rubric updates that undo an
        earlier update within two draws of the task.
after:  Training dynamics of \ourmethod{}. Left: tasks by guidance fields. Middle: accepted rubric
        updates per 100 steps. Right: reversed rubric updates.
   or:  Training dynamics of \ourmethod{}: tasks by guidance fields, accepted rubric updates per
        100 steps, and reversed rubric updates.
```

"Harness dynamics" was the writer's term. "Training dynamics of \ourmethod{}" is the reader's.
"Dashed: guidance ceiling" repeats the left panel's right axis, which is labelled `Ceiling`. The
definition of a reversed update is the text's (RQ2 defines it in full), so the caption uses the name
the axis uses (`Reversed updates (%)`). `per 100 steps` stays because the middle axis says only
`Accepted rubric updates`: the caption carries what the axis leaves out, never what it already says.
Either form is fine: position words when the text points at one panel, a joined list when it does not.

**Figure 5, two panels on cost.**

```latex
before: Training efficiency at Qwen3.5-4B. Hatched: one-off memory cold start. (a) Cluster hours per
        hundred steps by stage. (b) Best OOD score against cluster hours to reach it.
after:  Training efficiency of \ourmethod{}: hours per 100 steps decomposed by stage, and hours to
        the best checkpoint.
```

The legend already carries `memory cold start (once)` with its hatch, and the axes already say
`OOD performance` against `Cluster hours to best OOD checkpoint`. What is left is the two contents,
joined, in reading order. `100`, not `hundred`, because the axis says `100`.

**What the eight rewrites share.** Every lead names the method or its object in the paper's words.
Every letter went, because the figures draw none. Every protocol line went (metric, benchmark list,
checkpoint rule, subscript key, calibration split, acceptance rule). Every line that repeated a
legend or axis went. The model scale stayed where it is the float's defining setting (Figures 1 and
3, and Table 1 where two scales are the point) and went where the analysis paragraph that cites the
float already opens with it ("At Qwen3.5-4B, ...").

---

## By kind of float

| float | lead | then | never |
|---|---|---|---|
| **Overview or pipeline figure** | the method as subject of a sentence (`\ourmethod{} runs ...`) | one or two sentences of flow, each part named as drawn, with its symbol | `Module: contents` fragments, acceptance rules, equations |
| **Method-comparison diagram** (a prior loop, the same loop under another objective, then ours) | `Comparison of` | one sentence in the drawing's order, each system named with its citation and one clause on what distinguishes it | position labels or letters, since the systems' names are drawn and the sentence gives the order |
| **Main results table** | `Quantitative results of \ourmethod{} on <corpus> with <models>` | the marks | metric definitions, benchmark lists the setup gives, the finding |
| **Ablation table** | `Ablations of \ourmethod{} on <the axes varied>` | the marks | the notation key the setup defines, checkpoint selection |
| **Dataset table** | `<What the table decomposes> of <corpus>` | what the columns hold, in one clause | size conventions, calibration splits, shorthand |
| **Training-curve figure** | `Training dynamics of \ourmethod{}`, or the quantity by what it is split on | the panels' contents, if more than one | line styles the legend shows, definitions the text gives |
| **Efficiency figure** | `Training efficiency of \ourmethod{}` | the panels' contents, joined | hatch or colour keys the legend shows |
| **Multi-panel figure, no letters drawn** | as its kind | contents joined in reading order, or `Left:`, `Middle:`, `Right:`, `Top left:` when the layout is not one row or the text cites a panel | `(a)`, `(b)`, `(c)` |
| **Figure whose letters are drawn** (the author asked for them, `docs-figure`) | as its kind | `(a) <noun phrase>. (b) <noun phrase>.`, each letter matching the glyph on the figure | letters in the caption that are not on the figure, or the reverse |
| **Case or qualitative figure** | what is traced, and under what (`One training task under \ourmethod{}`) | the panels' contents | the story the case paragraph tells |

**Panels whose identity is one word** (a failure class, a domain, a benchmark) carry that word
inside the panel, at the upper middle where plots leave space, and the caption names only what the
panels share (Figure 3). The caption does not enumerate what the reader has already read in the
panels.

**Position words and joined lists are both fine.** The author's remark: "we can just say xxx and yy,
that is also fine, no need to always use left, right, or a, b, c." A one-row figure with distinct
contents reads naturally as a list after a colon. Use position words when the layout is two
dimensional (Figure 1) or when the text says "the right panel of Figure 4".

---

## Checklist

Run on every caption, in order, and delete what fails.

1. Does the lead name the object and the method in the paper's own words (a section title, a module
   name, the corpus macro)? Replace a generic label.
2. Is it an overview figure? Then is it one or two sentences of flow rather than fragments?
3. Does every `(a)` in the caption match a letter drawn on the figure? If none is drawn, rewrite with
   position words or a joined list.
4. Does any clause state a metric, a scoring rule, a checkpoint rule, a cadence, a notation key or an
   acceptance rule? Check the setup or method states it, then delete it here.
5. Does any clause repeat an axis label, a legend entry or an in-panel label? Delete it.
6. Does any `Label: value.` define a mark the reader can decode without it? Delete it. Keep bold,
   underline, parentheses and any symbol drawn without definition.
7. Does any clause state the finding? Move it to the results paragraph.
8. Does each noun match the word the axis, the legend and the text use for the same object (fraction
   rather than ratio, 100 rather than hundred, reversed updates rather than a paraphrase)?
9. Is the setting (model scale, corpus) already stated by the paragraph that cites the float and
   constant across that analysis? Then drop it here, unless it is the float's defining setting.
10. Is it over thirty words for a results float, or sixty for an overview or composite? Find what
    else fails 4 to 7.

---

## Rules

1. **The lead is a noun phrase naming the float's object and the method, in the paper's terms.**
   `Quantitative results of \ourmethod{} on the five-domain \corpus{}`, not `Results at two scales`.
   A generic lead makes the reader find the object in the grid, and a paraphrase ("control loop" for
   the section titled Harness-Controlled RL Training) makes them map it back.
2. **An overview figure's caption is one or two full sentences telling the flow**: what conditions
   what, and how the parts interact, in the drawing's order and with the names drawn on it. Colon
   fragments list the parts and lose the arrows, which were the reason for drawing the figure.
3. **No panel letters unless the figure draws them.** Name panels by position (`Left:`, `Top left:`)
   or join their contents in reading order. A caption letter with no glyph to match sends the reader
   searching the figure for something that is not there.
4. **No protocol in a caption.** Metrics, scoring instruments, checkpoint selection, evaluation
   cadence, notation keys, calibration splits and acceptance rules live in the setup or the method,
   once. The caption copy is the one that goes stale.
5. **Nothing the float already says, and what it leaves out.** An axis label, a legend entry, a hatch
   key or an in-panel name is not repeated: "Dashed: guidance ceiling" beside an axis labelled
   `Ceiling` is read twice. A unit or rate the axis omits (`per 100 steps` under `Accepted rubric
   updates`) is what the caption is for.
6. **One-word panel identities go inside the panel**, at the upper middle, and the caption names only
   what the panels share.
7. **Keep only the marks that encode something the reader cannot see otherwise**: bold, underline
   and the margin's parentheses in a table, and a symbol drawn without its definition. The shaded
   row of the paper's method needs no key.
8. **One object, one name, across caption, axis, legend and text, and the name the field uses.**
   Fraction (part of a whole, the common term in ML papers), never ratio (part to part). When the
   name changes, the axis and the text change with the caption. `100` when the axis says `100`.
9. **No finding in a caption.** The finding is the results paragraph's bold sentence, and a caption
   that repeats it is left behind when the numbers move.
10. **A setting constant across an analysis is stated once**, by the paragraph that cites the floats
    or by the first float, not in every caption.
11. **Ten to thirty words for a results float, up to sixty for an overview or composite.** A
    longer caption is almost always carrying protocol, legend text or a finding.
12. **A caption the agent drafts goes through the writer** (`writing-chatgpt`) with this skill as
    context. A caption the author dictates is patched in as given, with only spelling and macros
    fixed.

---

## Anti-patterns

- **The generic subject.** `Results at two scales`, `Harness dynamics`, `\corpus{} tasks`. Tempting
  because it is short and true. It names a category, not the object, and not the method.
- **Telegraphic colon fragments.** `Memory $\mathcal{M}_t$: rollouts, rubric states, outcomes,
  retrieved as $E_t$.` Tempting because it looks precise. It lists parts and drops how they connect,
  which the overview exists to show.
- **(a)(b)(c) with no letters in the figure.** Tempting because it is the habit of multi-panel
  figures. The reader looks for glyphs that are not drawn.
- **Protocol in the caption.** `In-domain: rubric mean. OOD: one benchmark per domain, scored by its
  own metric.` Tempting because a float should "stand alone". The document stands alone, and the
  setup already said it.
- **Repeating the legend.** `Hatched: one-off memory cold start.` above a legend that says `memory
  cold start (once)`.
- **Marks that encode nothing.** `Indentation: removed modules.` on rows named `w/o critic`.
- **Enumerating in-panel labels.** `(a) \clblind{}, (b) \clsat{}, (c) \clspur{}` when each panel
  already carries its class name.
- **Shorthand only the writer reads.** `GPQA-D.\ whole.`
- **The long caption.** Eighty words, of which the object's name is five. Every extra clause is one
  of the above.
- **A caption note that explains a column.** Usually the column fails `docs-table`'s one rule
  (`$\mathcal{D}_0$` in the dataset table).
- **The writer's term in the lead.** `Harness dynamics` where the reader expects `Training dynamics
  of \ourmethod{}`.

---

## Companions
`docs-figure` (what the image contains, including the in-panel labels a caption must not repeat and
when panel letters are drawn) · `docs-table` (the grid, number format, and the bold, underline and
margin marks the caption declares) · `docs-ablation` (which ablation rows exist, whose axes the
ablation caption's lead names) · `docs-workflow` (drawing the overview figure whose flow the caption
tells) · `docs-analysis` and `writing-paper` (the setup that owns the protocol, and the results
paragraph that owns the finding) · `writing-chatgpt` (polishing a drafted caption's sentences) ·
`conventions` (family index).
