---
name: writing-paper
description: "Write or revise a research paper in LaTeX: where a citation attaches, how related work is grouped by theme rather than listed paper by paper, and how the method and experiments sections are built. A method opens with the modeling choice and each subsection with the limitation it fixes; a results paragraph takes a finding as its subject, never a table. Inherits the punctuation and word rules of writing-style."
when_to_use: "Use when drafting or editing any section of a paper, when placing citations, when a method section reads as a derivation with no choices in it, when a results paragraph opens with Table 1 shows, when related work is a list of summaries, or when a reviewer says the contribution is hard to locate."
---
# Skill: writing-paper

## Purpose
A paper is an argument, and every convention here exists to keep the argument legible. `writing-style`
governs punctuation and word choice in any authored document. This skill adds what a paper needs on
top of that: citations that attach to the concept they support, related work grouped by theme rather
than recited paper by paper, and paragraphs that open with a claim instead of a topic announcement.

The failure this guards against is prose that is fluent, grammatical, and carries no information in
the position a reader looks first. A section that begins "We treat per-token circuit design as a
differentiable architecture search" has spent its most valuable sentence restating its own title. A
section that begins "Existing memory-augmented agents collect fragments into a bank and retrieve
entries at inference time" has spent it setting up the gap the paper fills.

## When to Use
- Drafting or revising any section of a paper: abstract, introduction, method, experiments, related work.
- Placing citations, or fixing a draft where citations sit at the ends of sentences.
- A related-work section has become one paragraph per paper.
- A reviewer says the writing is vague, or that the contribution is hard to locate.

## Contents
- [What this adds to writing-style](#what-this-adds-to-writing-style)
- [Where a citation attaches](#where-a-citation-attaches)
- [The tilde, and the one case that drops it](#the-tilde-and-the-one-case-that-drops-it)
- [One line of work, one citation](#one-line-of-work-one-citation)
- [Related work is organized by theme](#related-work-is-organized-by-theme)
- [The leading sentence carries the finding](#the-leading-sentence-carries-the-finding)
- [The arc: each section expands the last](#the-arc-each-section-expands-the-last)
- [The method section](#the-method-section)
- [The experiments section](#the-experiments-section)
- [Numbers](#numbers)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## What this adds to writing-style
Everything in `writing-style` holds: no em-dashes, no semicolons, colons used sparingly, and the same
list of filler words to avoid. Three additions are specific to papers.

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

## Related work is organized by theme
Each paragraph covers one theme and ends by saying what the theme leaves open. The shape is fixed:

1. **A bolded theme header**, run in with `\noindent \textbf{Learning-based agent memory.}\`
2. **The trajectory of the field as a claim**, with grouped citations on each stage. "Agent memory has
   evolved from static pipelines~\citep{...} toward learned memory operations~\citep{...}."
3. **Each sub-direction in one sentence** with its own grouped citation, opened by "One line of work"
   and "Another line of work".
4. **Named exemplars**, only the two or three whose mechanism the argument needs.
5. **The gap**, stated as a property shared by everything above. "Despite these advances, all remain
   retrieval-centric: they improve when and how to access stored entries, but the memory content
   itself is fixed at write time."
6. **Our position**, one sentence, naming what changes. "Ours departs from this paradigm by modeling
   memory as a generative policy."

Steps 5 and 6 are what make the section an argument instead of a bibliography. A related-work paragraph
that ends on its last citation has told the reader what exists and not why the paper was written.

## The leading sentence carries the finding
The first sentence of a section, subsection, or paragraph is the most-read sentence in it. Spend it on
a claim, never on a topic announcement.

In **results**, lead with the finding in bold, then give the evidence:

```latex
\textbf{Experience distillation alone already matches or surpasses RL-based baselines.}
Stage~1 achieves 35.0\% on \textsc{WebArena}, comparable to Memory-R1 (33.2\%) and MemRL (34.0\%)
without any RL training.
```

In **ablations**, lead with the research question, describe the variants, then state the answer in
bold and attribute it:

```latex
\noindent\textbf{RQ1: Are both training stages necessary?}\
We compare against two single-stage variants. \textit{(i)} ... \textit{(ii)} ...
Results show that \textbf{both stages are essential, with unified training suffering the largest
drop.} Removing Stage~1 degrades \textsc{WebArena} by 5.2\,pp, suggesting that without a
well-initialized memory distribution, online RL struggles to converge.
```

The order is research question, then main finding, then detailed depiction. A reader who stops after
the bold sentence has the result. A reader who continues gets the numbers and the attribution. Never
invert it by walking through numbers first and concluding at the end of the paragraph.

An **interpretation** sentence earns its place when it says why, not that. "We attribute this to a
mismatch between the two rewards: the similarity reward encourages imitation of references, whereas
the task reward rewards memories that improve success." That is a mechanism. "This demonstrates the
effectiveness of our approach" is not.

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

**Method.** Each mechanism named in the introduction gets its own subsection, in the same order, with
the definition, the objective, and the reason for each choice.

**Experiments.** Each claim made in the introduction gets an experiment that could have refuted it.

The consistency requirement is strict: a mechanism named in the abstract must appear in the
introduction, be defined in the method, and be measured in the experiments. A reader who finds a
contribution in the abstract and cannot find its experiment stops trusting the paper.

## The method section
A method section fails in a specific way: it derives correctly and never says what was chosen or why.
The reader finishes it able to reimplement the equations and unable to name the contribution.

**Open with the modeling choice, not with notation.** The first sentence states what the paper decides
to treat the problem as. Notation follows in the next sentence, once the reader knows what is being
formalized.

```latex
% WEAK: formalism from the first word. Nothing here is a choice, so nothing is defended,
% and standard background is indistinguishable from the contribution.
Let $x_0 = (w^1, \ldots, w^L)$ be a clean token sequence over a vocabulary that includes a
dedicated mask symbol. The forward process draws a masking level $t \sim \mathcal{U}(0,1]$ and
independently replaces each token ...

% STRONG: the choice, then the formalism it needs.
We model adaptive memory as a generative policy \mempolicy{} parameterized by $\theta$, separate
from the downstream agent. Let $\mathcal{E}$ denote an offline bank of context-guidance pairs
$(x,m)$, where each context $x=(q,o)$ consists of a task specification $q$ and an observation $o$.
```

**Each subsection opens with the limitation that motivates it.** A method is a sequence of decisions,
and a decision is only legible against the thing it fixes. "While experience distillation provides a
strong initialization, the supervised policy cannot determine \emph{when} generation is useful or
potentially harmful" earns the subsection that follows. A subsection that opens by defining its own
title has to be read to the end before the reader learns why it exists.

**Every design choice carries its reason, usually as a "so that" clause.** "We initialize the two
decision-token embeddings symmetrically so that both decisions have comparable initial probabilities
and can be explored at the beginning of training." Without the clause a reviewer cannot tell a
considered choice from an arbitrary one, and will assume the second.

**Mark background as background.** Standard machinery the paper inherits gets compressed and cited,
not re-derived at length. A full derivation of a known objective, presented in the same voice and at
the same length as the contribution, hides which part is new. Give the inherited objective, cite it,
and spend the space on what the paper changes.

**Define every symbol immediately after its equation**, in a "where" clause. An equation whose symbols
are defined three paragraphs later, or not at all, is decoration.

## The experiments section
The test is mechanical. **Look at the grammatical subject of each paragraph's first sentence. If it is
an artifact of the paper, a table, a figure, or a section, the sentence is wasted. If it is a claim
about the world, it is doing work.**

```latex
% WEAK: the subject is the table. The reader learns what the table contains, which the caption
% already said, and must hunt the paragraph for the result.
Table~\ref{tab:main} positions our method against classical baselines of matched scale.
Table~\ref{tab:ablation} ablates the sub-layer, and Table~\ref{tab:ensemble} reports ensembling.

% STRONG: the subject is the finding. The table is cited as evidence for it.
\textbf{Our method achieves state-of-the-art performance across all benchmarks and sub-domains.}
As summarized in Table~\ref{tab:main-results}, it leads every sub-domain, with the largest gains
in Reddit ($+$23.8\,pp) and CMS ($+$28.2\,pp), where structured navigation patterns benefit most
from memorized experience.
```

The strong form also places the number **immediately after the claim it supports**, not several
sentences later behind a digression. A result that appears mid-paragraph, after an explanation of why
prior work is hard to compare against, will be missed by every reader who skims.

**Structure the section as questions, not as tables.** Ablations and analyses are numbered research
questions carried in run-in bold, answered before the numbers arrive:

```latex
\noindent\textbf{RQ1: Are both training stages necessary?}\
We compare against two single-stage variants. \textit{(i) w/o Stage~1 init} skips experience
distillation. \textit{(ii) Unified single-stage} collapses both stages into one RL phase.
Results show that \textbf{both stages are essential, with unified training suffering the largest
drop.} Removing Stage~1 degrades \textsc{WebArena} by 5.2\,pp, suggesting that without a
well-initialized memory distribution, online RL struggles to converge.
```

Number the questions across the whole section, so RQ1 and RQ2 in the ablation continue into RQ4 in the
analysis. A reader can then locate the claim a table supports without reading the table.

**The setup is a reproducibility contract.** Benchmarks and baselines go under run-in bold headers.
Each benchmark carries its citation on its name, its size, and, where a split is inherited rather than
chosen, the prior work the split follows: "Following WebAgent-R1~\citep{wei-etal-2025-webagent} and
WebRL~\citep{qi2024webrl}, we use a 647/165 train/test split." Naming the source of a split is what
makes a comparison against those papers legitimate, and choosing a split freely without saying so is
the most common way a results table stops being comparable.

**Group baselines by paradigm, not alphabetically**, using the same inline enumeration as everywhere
else: `\emph{(i)~Workflow-based memory}` then `\emph{(ii)~Learning-based memory}`. The grouping is
itself an argument, because it says which family the paper competes with.

**When a comparison is impossible, say so and say why.** If no prior system reports the suite, state
it plainly, state what each reports instead, and state what the paper adds. That is a finding about
the field. Burying it inside a paragraph about tables turns a legitimate contribution into an excuse.

## Numbers
Report a difference with an explicit sign and a unit, and bind the unit with a thin space:
`($+$23.8\,pp)`. Percentage points and percent are different quantities, so a change from 42.0\% to
50.3\% is `$+$8.3\,pp`, never `$+$8.3\%`. Give absolute values alongside relative ones when a relative
gain sits on a small base, because "50\% relative improvement" on a base of 4\% is two points.

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
7. **Every related-work paragraph ends with the gap and the position.** Not on its last citation.
8. **The leading sentence states the claim.** Never the topic, never what the section will do.
9. **Results lead with the finding in bold, ablations with the research question.** Evidence follows,
   attribution last.
10. **No sentence exists only to introduce the next one.** Delete it and promote the next.
11. **A method subsection opens with the limitation it fixes**, and every design choice carries a
    reason, usually as a "so that" clause.
12. **Background is compressed and cited, never re-derived** at the length of the contribution.
13. **The subject of a results paragraph is a finding, never a table.** "Table 1 positions ..." is
    always the wrong opener.
14. **The number follows the claim immediately.** Not after a digression.
15. **Ablations and analyses are numbered research questions**, answered in bold before the evidence.
16. **An inherited split names the work it follows.** A freely chosen split that does not say so is
    not comparable to anything.
17. **Signed differences carry a unit and a thin space**, and percentage points are not percent.
18. **Every mechanism in the abstract appears in the method and is measured in the experiments.**

## Anti-patterns
- **The trailing citation.** `... is a left-to-right generative model~\citep{x}.` The citation now
  supports the paper's own description rather than the published concept.
- **The bibliography paragraph.** One paper per sentence, each a summary, no claim connecting them and
  no gap at the end. It is a reading list wearing the shape of an argument.
- **The topic-announcing lead.** "In this section we describe our architecture search." The heading
  already said it. Say what the search does that a fixed design cannot.
- **The mechanical method opener.** "We treat X as a variant of Y in which Z is optimized by
  gradients." True, and it defines rather than claims. Lead with what the choice buys, then define.
- **Conclusion-last results.** A paragraph that walks through every number and states the finding in
  its final sentence. A reader who skims gets nothing.
- **Effectiveness claims as interpretation.** "This demonstrates the effectiveness of our approach"
  restates that the number was good. Give the mechanism that produced it.
- **The table-of-contents paragraph.** "Table 1 positions X. Table 2 ablates Y. Table 3 reports Z."
  Three sentences that restate three captions and state no result.
- **The formalism-first method.** A method section that opens `Let $x_0 = \ldots$` has defined the
  problem without saying what the paper decided to do about it.
- **Background at contribution length.** A known objective re-derived over a page, in the same voice
  as the new part, so a reviewer cannot see the boundary.
- **The undefended constant.** A design choice with no "so that". A reviewer reads an arbitrary choice
  where a considered one was intended.
- **The buried headline.** The main result arriving in the middle of a paragraph, after an
  explanation of why comparison is difficult.
- **The freely chosen split.** A train/test division with no cited source, which quietly makes every
  number in the table incomparable with the work it is placed beside.
- **Percent where percentage points belong.** It inflates every reported gain and a reviewer will
  notice.
- **A contribution in the abstract with no experiment.** The fastest way to lose a reviewer.

## Companions
`writing-style` (the punctuation, word, and sentence-structure rules this inherits) · `docs-figure`
(what a figure may contain and how to render it) · `naming-descriptive` (naming a method or an arm so
the name states what it is) · `output-analysis` (producing the tables and curves the experiments
section reports) · `conventions` (the map).
