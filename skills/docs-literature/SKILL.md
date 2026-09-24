---
name: docs-literature
description: "Build a paper's related-work section, learned from Mem-Pi and System-1.5: two or three direction paragraphs, a family sentence with a grouped citation, lines of work with two named exemplars each, a one- or two-sentence closing that states the paper's difference, and a citation list that is recent, with a fifth to a quarter of it from the last six months."
when_to_use: "Use when drafting or revising related work, when a related-work paragraph reads as a list of summaries, when the middle of a paragraph criticises each cited method, when the closing runs longer than two sentences, or when the citations look dated for the venue."
---
# Skill: docs-literature

## Purpose
Related work places the paper among its neighbours after the reader has the method and the results.
It fails in four ways, all seen on real drafts: one paragraph per paper, a middle that says what each
cited method does not do, a closing that restates the method at length, and a citation list whose
newest entry is a year old. This skill fixes the shape, taken from the two papers the author holds up
as the model, Mem-Pi and System-1.5, and adds a recency rule. `writing-paper` owns where a citation
attaches and the tilde; this skill owns what the section contains and how it is ordered.

## Contents
- [The shape Mem-Pi and System-1.5 share](#the-shape-mem-pi-and-system-15-share)
- [The opening sentence](#the-opening-sentence)
- [Lines of work and named exemplars](#lines-of-work-and-named-exemplars)
- [The closing states the difference](#the-closing-states-the-difference)
- [Recency](#recency)
- [What to cut](#what-to-cut)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## The shape Mem-Pi and System-1.5 share
Two or three paragraphs, each one research direction under a noun-phrase run-in head:

```latex
\noindent \textbf{Retrieval-centric agent memory.}\        % Mem-Pi
\noindent \textbf{Efficient reasoning models.}\            % System-1.5
\noindent \textbf{Conditional computation.}\               % System-1.5
```

Inside each paragraph the order is fixed:

1. one sentence stating the family or its trajectory, with a grouped citation;
2. *One line of work* with a grouped bracket, then two named exemplars, one clause each;
3. *Another line of work* (Mem-Pi writes *A second line*), the same way, optionally *More recently*;
4. a `%%` line in the source, then the closing, one or two sentences on the paper's difference.

A direction the method section already contrasts in full does not also need a paragraph here. A
third theme is justified only when the reader would otherwise miss a family the paper competes with.

## The opening sentence
Two forms, both from the model papers:

- **The family and its aim.** System-1.5: "Efficient reasoning models aim to mitigate the
  inefficiencies caused by verbose outputs and the overthinking phenomenon~\citep{...}." Also
  "Conditional computation techniques aim to selectively apply heavy computation only to the
  important parts of an input".
- **The family's trajectory.** Mem-Pi: "Agent memory has moved from static pipelines~\citep{...}
  toward operations learned against downstream outcomes~\citep{...}." A survey or two belongs in this
  bracket.

The opening never introduces the paper and never names a limitation.

## Lines of work and named exemplars
A line of work is one sentence with one grouped bracket that carries the coverage. The named
exemplars carry the mechanism, and there are at most two per line, three or four per paragraph:

```latex
% System-1.5
One line of work focuses on improving language-space efficiency, using length budgeting through
prompting~\citep{lee2025well} and fine-tuning~\citep{liu2024can,yu2024distilling,luo2025o1}.
For example, Chain-of-Draft~\citep{xu2025chain} applies token budget-aware prompting to guide the
model toward more concise reasoning, while S1~\citep{muennighoff2025s1} introduces a budget-forcing
strategy to terminate the thinking process early.

% Mem-Pi
One line distills trajectories into rules, guidelines or strategies that are retrieved at
inference~\citep{...}: AutoGuide~\citep{fu2024autoguide} compresses interaction logs into
context-conditional guidelines, and ReasoningBank~\citep{ouyang2025reasoningbank} distills
strategies from both successes and failures.
```

Each exemplar clause says what the method does, in its own terms. System-1.5 orders recent work
last with *More recently*, which also shows the reader the field is current. Mem-Pi names the
closest prior work explicitly once: "SEAM~\citep{li2026beyond}, the closest to our setting".

## The closing states the difference
One or two sentences, after the `%%` line, and nowhere else does the paragraph evaluate the cited
work. Three forms appear in the model papers:

```latex
% System-1.5, build and extend
\ourmethod{} builds upon latent-space reasoning but further optimizes efficiency by adaptively
allocating computation to handle reasoning steps with varying complexity.
\ourmethod{} draws inspiration from this line of work and extends it to the latent reasoning space.

% Mem-Pi, the shared constraint we remove
What unites them is the constraint we remove: however well when and how to access entries is
optimized, the content is fixed at write time. \ourmethod{} constructs guidance for the current
context instead.
```

The closing names the paper's position in one clause and, when needed, one clause of mechanism. A
closing that re-derives the method, lists its actions, or states results is the method section
leaking into related work.

## Recency
The citation list must look current to a reviewer reading it in the submission month.

- **At least a fifth, and ideally a quarter, of the unique citations in the section come from the
  last six months** before submission, counted by arXiv first-submission date or venue date.
  Count it before submitting: unique keys in the section, and how many fall in the window.
- **At least half come from the last eighteen months.** Foundational work (the first paper of a
  family, the method the paper builds on) stays, but it is cited once, in a bracket, not described.
- **Recent work goes into the brackets first.** A recent paper does not need a clause of its own to
  count; the grouped bracket of its line of work is where most of them belong, as in Mem-Pi's
  memory brackets, which carry 2026 work beside 2023 foundations.
- **Every added citation is verified** against its arXiv or venue page (title, authors, date)
  before it enters the bib. A plausible title that cannot be found is dropped, never guessed.
- **One recent survey per direction** where one exists, in the opening sentence's bracket.

## What to cut
Learned from revising a draft that read as verbose:

- **Middle-of-paragraph criticism.** "System-1.5 routes between language and latent computation but
  does not place memory retrieval within the recurrent action set" attacks one paper to set up the
  contribution. The closing does that job once, for the whole family.
- **An exemplar clause per cited paper.** Ten "X does A, while Y does B" clauses make a list. Two per
  line, and the bracket covers the rest.
- **A theme the method section already argues.** A step-level-credit paragraph that repeats the
  method's own contrast with VinePPO-style completed branches adds length and no new placement.
- **Evaluation and cost studies as their own sentences.** They go in a bracket or not at all.
- **An inherited-components paragraph.** What the paper takes unchanged belongs in the method.

## Rules
1. Two or three direction paragraphs, each under a noun-phrase run-in head.
2. Opening sentence: the family's aim or trajectory, with a grouped citation that includes a survey.
3. Lines of work are one sentence with a grouped bracket each. At most two named exemplars per line.
4. Exemplar clauses describe what the method does, never what it lacks.
5. The closing is one or two sentences after a `%%` line and is the only place the paper's
   difference is stated.
6. At least a fifth to a quarter of unique citations are from the last six months, and at least half
   from the last eighteen months. Count them.
7. Every added citation is verified against its source page before it enters the bib.
8. Citations attach to their concept with a tilde, as in `writing-paper`.

## Anti-patterns
- **The bibliography paragraph.** One sentence per paper, no line of work, no closing.
- **The critique in the middle.** "X does not do Y" about each cited method.
- **The long closing.** Three or more sentences restating the method's actions or results.
- **The stale list.** The newest citation is a year old at submission.
- **The unverified recent citation.** A 2026 paper added from memory, wrong title or authors.
- **The duplicate theme.** A related-work paragraph that repeats a contrast the method already made.

## Companions
`writing-paper` (where a citation attaches, the tilde, grouping by claim) · `docs-analysis` (the
experiments section) · `writing-chatgpt` (the paragraphs go through the writer) · `cc2bib` (turning
verified papers into bib entries) · `conventions` (family index).
