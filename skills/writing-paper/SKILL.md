---
name: writing-paper
description: "Write or revise a research paper in LaTeX by the rules every section shares: where a citation attaches and how citations group by claim, a leading sentence that states a claim, one argument carried from the abstract through the method to the experiments, headings that name concepts, families that are counted and named, claim boxes, and signed numbers. Each section's own shape has a section skill, writing-literature for related work, writing-methodology for the method, writing-analysis and writing-ablation for the experiments, and writing-caption and writing-table for captions and tables. Load alongside writing-style, which is the word- and token-level layer this sits on top of, or writing-style-zh for a Chinese paper."
when_to_use: "Use when drafting or editing any part of a paper alongside the section skill that owns it, when writing the abstract or the introduction, when placing or grouping citations, when a paragraph opens by announcing its topic or what the section will do, when the abstract, introduction, method and experiments disagree about the contribution, when a heading names a process or asks a question, or when a reviewer says the contribution is hard to locate. The shape of related work, the method and the experiments goes to writing-literature, writing-methodology and writing-analysis."
---
# Skill: writing-paper

## Purpose
A paper is an argument, and every convention here exists to keep the argument legible.

**Load `writing-style` alongside this skill, and `writing-style-zh` instead of it when the paper is
in Chinese.** Those skills are the word- and token-level layer: which characters are forbidden, which
words read as filler, which sentence shapes to avoid. This skill is the argument-level layer above
them. They constrain the sentence. This constrains what the sentence is for. Neither substitutes for
the other, and a draft that satisfies only one of them still fails: prose can be free of em-dashes
and still open every paragraph by announcing its own title, and prose can lead with a finding in
every paragraph and still be unreadable for punctuation.

On top of that layer, this skill holds the rules every section shares: citations that attach to the
concept they support, paragraphs that open with a claim instead of a topic announcement, and one
argument carried from the abstract to the experiments. Each section's own shape belongs to a section
skill, `writing-literature` for related work, `writing-methodology` for the method, and
`writing-analysis` with `writing-ablation` for the experiments.

The failure this guards against is prose that is fluent, grammatical, and carries no information in
the position a reader looks first. A section that begins "We treat per-token circuit design as a
differentiable architecture search" has spent its most valuable sentence restating its own title. A
section that begins "Existing memory-augmented agents collect fragments into a bank and retrieve
entries at inference time" has spent it setting up the gap the paper fills.

## When to Use
- Drafting or revising any part of a paper, alongside the section skill that owns that part. The
  abstract and the introduction have no skill of their own, and their recipe is the arc below.
- Placing or grouping citations, or fixing a draft where citations sit at the ends of sentences.
- A paragraph opens by announcing its topic, or a heading names a process or asks a question.
- The abstract, introduction, method and experiments disagree about what the paper contributes.
- A reviewer says the writing is vague, or that the contribution is hard to locate.
- Not for the shape of a section. Related work is `writing-literature`'s, the method
  `writing-methodology`'s, the experiments `writing-analysis`'s, the ablation set `writing-ablation`'s,
  captions `writing-caption`'s and table grids `writing-table`'s.

## Contents
- [What this adds to writing-style](#what-this-adds-to-writing-style)
- [Where a citation attaches](#where-a-citation-attaches)
- [The tilde, and the one case that drops it](#the-tilde-and-the-one-case-that-drops-it)
- [One line of work, one citation](#one-line-of-work-one-citation)
- [The leading sentence carries the claim](#the-leading-sentence-carries-the-claim)
- [The arc: each section expands the last](#the-arc-each-section-expands-the-last)
- [The section skills](#the-section-skills)
- [Headings name concepts, never processes or unnumbered questions](#headings-name-concepts-never-processes-or-unnumbered-questions)
- [Families are enumerated, not described by a split](#families-are-enumerated-not-described-by-a-split)
- [Numbers](#numbers)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## What this adds to writing-style
Everything in `writing-style` holds and is checked first, because it is mechanical and a draft can be
scanned for it: no em-dashes or en-dashes, no semicolons in prose, colons used sparingly, no bulleted
lists unless asked, and the curated list of filler words and sentence shapes to avoid. For a
Chinese-language paper `writing-style-zh` replaces it and governs the same layer. Three additions are
specific to papers.

**Concise.** No sentence may exist only to announce the next one. "In this section we describe our
method" and "We now turn to the experimental results" carry nothing a section heading has not already
said. Delete them and start with the claim.

**Formal.** No contractions and no first-person singular. "We" is the plural authorial voice and is
correct throughout, including for choices ("we set the learning rate to"), which is preferred over the
passive evasion "the learning rate was set to".

**Enumerate inline, not vertically.** `writing-style` defaults to flowing prose, and a paper follows
that even where a draft wants bullets. Variants and conditions go inline with italic markers, so a
comparison stays one paragraph and one argument:

```latex
We compare against two single-stage variants.
\textit{(i) w/o Stage~1 init} skips experience distillation and applies online RL directly.
\textit{(ii) Unified single-stage} collapses both stages into one RL phase.
```

Reserve `itemize` and `enumerate` for genuinely parallel items a reader will scan rather than read,
such as a contribution list some venues require.

## Where a citation attaches
**A citation attaches to the concept it supports, not to the end of the sentence it appears in.** The
concept is whatever noun, noun phrase, named system, or adjective the citation is evidence for. Put
the citation immediately after that token, wherever it falls in the sentence.

```latex
% WRONG: the citation has drifted to the sentence boundary and now supports "left-to-right
% generative model", which is a description this paper is making, not a claim the cited work owns.
An autoregressive transformer is a left-to-right generative model~\citep{vaswani2017attention}.

% RIGHT: the citation sits on the thing that was published.
An autoregressive transformer~\citep{vaswani2017attention} is a left-to-right generative model.
```

The rule holds for every kind of token, and it holds several times in one sentence:

```latex
Large language models~\citep{ouyang2022training,dubey2024llama} have shown potential as
autonomous agents~\citep{liu2025advances}, enabling computer-use agents~\citep{qin2025ui},
deep research assistants~\citep{li2025webthinker}, and scientific discovery
systems~\citep{lu2024ai,liu2026evox}.
```

Four concepts, four citations, each on its own noun. A single citation at the end would claim that one
set of papers established all four, which is false and unreviewable. When a sentence lists parallel
items, **each item carries its own citation**. A named system carries it on the name, since the name
is the noun: `AutoGuide~\citep{fu2024autoguide}`, `GRPO~\citep{shao2024deepseekmath}`. An emphasized
term of art carries it on the term: `\emph{workflow-based memory}~\citep{packer2023memgpt}`.

## The tilde, and the one case that drops it
The `~` before a citation is a LaTeX non-breaking space. It stops a line break from separating the
concept from its bracket, which would leave a citation stranded at the start of a line, apparently
attached to nothing. **Use it every time a word precedes the citation.**

There is exactly one exception. When the citation is itself the grammatical subject, no word precedes
it, so there is nothing to bind and the tilde is wrong:

```latex
% Citation follows a concept: tilde, parenthetical form.
Group Relative Policy Optimization~\citep{shao2024deepseekmath} separates decision from content.

% Citation IS the subject: no tilde, textual form.
\citet{shao2024deepseekmath} introduce Group Relative Policy Optimization.
```

`\citep` renders in parentheses and belongs beside a concept. `\citet` renders as text and stands in
for a name in the sentence's grammar. Choosing `\citep` where `\citet` belongs produces "(Shao et al.,
2024) introduce", which reads as a typo. A well-formed draft is overwhelmingly `~\citep`: in the paper
this convention was taken from, 128 of 128 citations use it, and every one carries a leading concept.

## One line of work, one citation
A citation command takes as many keys as the claim needs. **Group them.** Four papers that established
the same idea belong in one bracket after that idea, not in four sentences that each summarize one
paper.

```latex
% WRONG: four sentences, four summaries, no argument.
Zhao et al. distill trajectories into rules. Wang et al. also distill trajectories. Wu et al.
propose a similar method. Yang et al. extend it.

% RIGHT: one claim, one grouped citation, then exemplars only where they differ.
One line of work distills raw interaction trajectories into structured knowledge retrieved at
inference time~\citep{zhao2024expel,wang2025agent,wu2025evolver,yang2026autoskill}.
For example, AutoGuide~\citep{fu2024autoguide} compresses offline logs into context-conditional
guidelines, while ReasoningBank~\citep{ouyang2025reasoningbank} distills strategies from both
successes and failures.
```

Name a paper individually only when it carries a detail the argument needs: it is the closest prior
work, it is the baseline being compared against, or its specific mechanism is what the next sentence
contrasts with. Everything else belongs inside a grouped bracket.

## The leading sentence carries the claim
The first sentence of a section, subsection or paragraph is the most-read sentence in it. Spend it on
a claim, never on a topic announcement or on what the section will do. Each section has its own form
of the claim. The method overview opens with what the method builds on and what it adds
(`writing-methodology`), and each component opens with the problem that forces it. A results
paragraph opens with its finding in bold (`writing-analysis`). A related-work paragraph opens with
the family's aim or trajectory (`writing-literature`). The experiments setup opens with what is
measured and on which tasks, which describes the evaluation and does not announce the section.

The test is mechanical. Look at the grammatical subject of each paragraph's first sentence. If it is
an artifact of the paper, a table, a figure, or a section, the sentence is wasted. If it is a claim
about the world, it is doing work. The one exception is a sentence whose claim is about the display
itself, such as what its measurement leaves out, as in Mem-Pi's
`Figure~\ref{fig:efficiency} counts tokens inserted into the agent and so omits the memory model's own prefill`.

## The arc: each section expands the last
The paper says the same thing four times at increasing resolution, and each pass must be consistent
with the one before it.

**Abstract.** Present the method, state what existing work does and where it falls short, state the
contrast, name the mechanism, close with the headline number. Five or six sentences.

**Introduction.** The abstract's sentences become paragraphs, in the same order. The field and its
capability, with grouped citations. The limitation. What existing approaches do, split into their
lines of work, and the property both share that constrains them. A different view, from another field
or from concurrent work, and why the obvious version of it is not sufficient. The method. Its
advantages, each a consequence of one design choice. How it is trained. What was measured and the
headline result.

**Method.** Each mechanism named in the introduction gets its own run-in head, in the causal order
`writing-methodology` fixes, and the introduction names them in that order.

**Experiments.** Each claim made in the introduction gets an experiment that could have refuted it.

Related work comes after the experiments and before the conclusion, where Mem-Pi and System-1.5 put
it. By then the reader has the method and the numbers, so the section places the paper among its
neighbours and does not motivate it again, because the introduction's lines of work have already
stated the gap.

The consistency requirement is strict: a mechanism named in the abstract must appear in the
introduction, be defined in the method, and be measured in the experiments. A reader who finds a
contribution in the abstract and cannot find its experiment stops trusting the paper. The writer's
`narrative` task (`writing-chatgpt`) checks this chain across sections. Each kind of content also
has one home. Evidence belongs to the results, and caveats about what was not run belong to the
limitations.

## The section skills
Each section's own shape lives in one skill, and this file keeps only what crosses sections. Related
work is two or three direction paragraphs, each closing on the paper's difference, with recent
citations, and `writing-literature` owns it. The method section, from the overview and the inherited
base model to each motivated component and every hard equation, is `writing-methodology`'s.
`writing-analysis` owns the experiments section, its setup, the shape of a results paragraph,
ablation framing and where each piece of evidence goes, and `writing-ablation` owns which ablation
variants exist and how the ablation table is grouped. Every figure and table caption is
`writing-caption`'s. The grid of a results table, its number format and its marks are
`writing-table`'s.

## Headings name concepts, never processes or unnumbered questions

A heading is the one line a skimming reviewer reads, so it has to carry something they can take
away. The section decides its form. In the method a run-in head is a concept noun the paper then
owns (`writing-methodology`), in related work a direction noun phrase (`writing-literature`), and in
the setup the things the paragraph fixes (`Datasets.`, `Baselines.`). A head that names a step
leaves the reader nothing to carry into the next section.

**In the results, a heading is a complete claim with its number.** `Routing gains $+8.18$ points
over the verbatim-only floor on LoCoMo-10.` Not `LoCoMo-10.`, which is a label, and not `The
census.`, which is a topic. A reader who reads only the bold run-in heads of the results section
should come away with the paper's findings in order.

**A heading that opens with What, How, or Why is always wrong**, except a numbered RQ head in a
question-framed experiments section, which a bold finding answers before any number arrives
(`writing-analysis`). `What would refute each law.` is a question put to the reader, and the reader
came to be told. It is also a process description wearing a question mark: the thing itself is the
falsification condition, so the heading is `Falsification conditions.` The same applies to
`What this says about the field.`, which should be the thing it says.

**Counted-article headings are process headings in disguise.** `The two-channel model.`, `The two
channels.`, `The three laws.`, `The self-rewriting store.`, `The ceiling clause.` name how many
things there are or point at "the" thing instead of naming a concept a reader can carry. Write the
concept in Title Case, the way Mem-Pi, System-1.5 and HarnessRL do (`Adaptation Distillation`,
`Dynamic Shortcut Architecture`, `Harness Evolver`): `Channel Model of Derived Memory`, `Content
Channel and Routing Channel`, `Laws of Derived Memory`, `Certified Self-Rewriting`, `Conversion
Ceiling: Once Routing Saturates, the Reader Binds`. Title Case is for `\section` and `\subsection`
titles. A counted-article run-in head becomes a sentence-case concept noun (`The two channels.`
becomes `Content channel and routing channel.`).

**Strong claims get one visual register, and only strong claims do.** An observation, a results
takeaway and the design principle the model implies go in claim boxes. A claim box is a light tinted
panel with no frame and no edge rule, numbered `Observation N` or `Finding N` (the principle is
unnumbered), with one colour per kind. Each box holds the claim in one sentence and its headline
evidence in at most two more. A headline claim inside running prose may take one accent span
(`\keyclaim{}`), at most once per paragraph and a handful of times per paper. Nothing else is
coloured or boxed, so the eye learns that colour means "this is a claim the paper stands on".

**Run-in heads, not `\paragraph`.** Use `\noindent\textbf{Concept.}` followed by the text on the
same line. `\paragraph` adds vertical space that breaks the density of a conference page, and its
output drifts between classes.

**Prompts are typeset, never dumped.** Prompts, rules and LLM reflections go in the paper's
`promptbox` idiom, with `\role{system}` markers and `\phead{Section}` heads, never in verbatim
blocks, wherever they appear, whether the method, a case study or the appendix. The box's caption is
`writing-caption`'s.

## Families are enumerated, not described by a split

When a set divides, name the families and count them. The reader needs the partition, not the
procedure that produced it.

```
wrong:  Splitting those questions by where the gold session lands isolates the effect.
wrong:  We use a two-family rule.
right:  Runs fall into two families, \emph{(i)~cross-system comparisons}, including the
        seven-system arena at fixed reader and judge, and \emph{(ii)~paired within-system
        comparisons}, including the content and routing arms at fixed writer, reader and judge.
```

The form is
`these fall into N families, \emph{(i)~NAME}, including X and Y, and \emph{(ii)~NAME}, including Z.`
It applies to benchmarks, baselines, layers, ablation arms and error categories alike. A sentence that
describes the splitting operation — "by where the memory lives", "by which tier is varied" — leaves
the reader to reconstruct the families, and they will reconstruct them differently from you.

## Numbers
Report a difference with an explicit sign and a unit, and bind the unit with a thin space:
`($+$23.8\,pp)`. Percentage points and percent are different quantities, so a change from 42.0\% to
50.3\% is `$+$8.3\,pp`, never `$+$8.3\%`. Give absolute values alongside relative ones when a relative
gain sits on a small base, because "50\% relative improvement" on a base of 4\% is two points.

A number follows the claim it supports immediately, in the abstract and the introduction as much as
in the results, and never after a digression. A table cell states its unit once in the column header
(`writing-table`).

## Rules
1. **A citation attaches to its concept, not to the sentence.** Move it to sit immediately after the
   noun, named system, or emphasized term it supports.
2. **Every parallel item in a list carries its own citation.** One citation at the end of a list claims
   one source established all of it.
3. **`~\citep{}` whenever a word precedes the citation.** The tilde is a non-breaking space and is not
   optional.
4. **`\citet{}` with no tilde when the citation is the subject.** Nothing precedes it, so there is
   nothing to bind.
5. **Group citations by claim.** A line of work is one sentence with one bracket of keys, not one
   sentence per paper.
6. **Name a paper individually only when its mechanism carries the argument**, such as the closest
   prior work or the baseline being compared against.
7. **The leading sentence states the claim.** Never the topic, never what the section will do. Its
   subject is never a table, a figure or a section unless the claim is about the display itself.
8. **No sentence exists only to introduce the next one.** Delete it and promote the next.
9. **The number follows the claim immediately.** Not after a digression.
10. **Signed differences carry a unit and a thin space**, and percentage points are not percent.
11. **Every mechanism in the abstract appears in the method and is measured in the experiments.**

## Anti-patterns
- **The trailing citation.** `... is a left-to-right generative model~\citep{x}.` The citation now
  supports the paper's own description rather than the published concept.
- **The topic-announcing lead.** "In this section we describe our architecture search." The heading
  already said it. Say what the search does that a fixed design cannot.
- **The question heading.** `What would refute each law.` `How does the router decide?` The reader
  came to be told, not asked. Name the thing: `Falsification conditions.` A numbered RQ head in a
  question-framed experiments section is the one exception, because a bold finding answers it.
- **The process heading.** `The two-family rule.` `The descent policy.` `The store and the
  leaf-support relation.` Each names a step or a mechanism-in-motion where a concept noun belongs.
- **The label heading in a results section.** `LoCoMo-10.` `The census.` `Cost against accuracy.`
  A results run-in head that is not a claim with a number wastes the one line a skimmer reads.
- **The split described instead of the families named.** "by where the memory lives", "splitting
  those questions by where the gold session lands". Name and count them instead,
  `\emph{(i)~NAME}, including X, and \emph{(ii)~NAME}, including Y`.
- **`\paragraph` for a run-in head.** Use `\noindent\textbf{...}`.

## Companions
`writing-style` (the punctuation, word, and sentence-structure rules this inherits, load it alongside) ·
`writing-style-zh` (the same layer for a Chinese-language paper) · `writing-literature` (the
related-work section: shape, closing, recency) · `writing-methodology` (the method section: overview,
base model first, motivated components, hard equations) · `writing-analysis` (the experiments and
analysis section: setup, results paragraphs, ablations, evidence placement) · `writing-ablation`
(which ablation variants exist and how the ablation table is grouped) · `writing-caption` (every
figure and table caption) · `writing-table` (the grid, number format and marks of a results table) ·
`naming-descriptive` (naming a method or an arm so the name states what it is) · `writing-chatgpt`
(hand the drafting to the writer tool, which applies this layer and the style layer; the agent
patches the result) · `conventions` (the map).
