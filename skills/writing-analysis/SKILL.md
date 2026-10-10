---
name: writing-analysis
description: "Build a paper's experiments and analysis section: section order, what the setup states, how each results paragraph is shaped, how ablations are framed and grouped, which evidence is a table, a figure or an appendix entry, and how numbers are reported and kept traceable, learned from System-1.5 and Mem-Pi."
when_to_use: "Use when drafting or revising Experiments, Main Results, Ablation Study or In-depth Analysis, when choosing between finding-framed and question-framed ablations, when placing a result in a table, a figure or the appendix, or when a reviewer says the ablations have no numbers, the text disagrees with the table, or a statistic is never defined, or when a results paragraph opens with Table 1 shows or restates its table cell by cell."
---
# Skill: writing-analysis

## Purpose
An experiments section is where a reader checks the claims against the numbers. This skill fixes its
order, setup, paragraph shape, ablation framing, which display holds each result, and how numbers are
written in prose, all learned from two papers: System-1.5 (a compact NeurIPS camera-ready) and Mem-Pi
(a research-question-driven ICLR draft). Where they differ, the body says which to follow and when. The
errors each shipped are the anti-patterns. How a number is formatted inside a table cell, and how the
table marks its winner, belong to `writing-table`.

## Contents
- [When to Use](#when-to-use)
- [Section order: compact or question-driven](#section-order-compact-or-question-driven)
- [The setup states how every number was produced](#the-setup-states-how-every-number-was-produced)
- [The results paragraph: claim, evidence, reason](#the-results-paragraph-claim-evidence-reason)
- [Ablations: procedures as findings, components as questions](#ablations-procedures-as-findings-components-as-questions)
- [Analyses that earn a place](#analyses-that-earn-a-place)
- [Table, figure, appendix](#table-figure-appendix)
- [Numbers and traceability](#numbers-and-traceability)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Drafting Experiments, Main Results, Ablation Study or In-depth Analysis, or choosing an ablation framing.
- Deciding whether a result is a table, a figure, an appendix entry or nothing, or checking prose numbers
  against displays before submission.
- Not for the grid itself or a cell's number format (`writing-table`), the plot (`drawing-figure`),
  sentence style (`writing-paper`, `writing-style`), or choosing which runs to compare (`output-analysis`).

## Section order: compact or question-driven
Before choosing the order, list the claims the introduction makes. Each gets a finding paragraph or an
RQ whose result could have refuted it, and a claim with no such experiment is either given one or cut
from the introduction. Claims about design decisions are tested by the ablation families of
`writing-ablation`.

Both papers open `Experiments` with bold run-in setup paragraphs and no setup subsection, put the main
table first under `Main Results`, and place Related Work and Conclusion after Experiments. Then:

| | System-1.5 (compact) | Mem-Pi (question-driven) |
|---|---|---|
| setup run-ins | `Datasets.`, `Baselines.` | `Benchmarks.`, `Baselines.`, `Agent and memory configuration.`, `Information-matched comparison.` |
| subsections | Main Results, In-depth Analysis | Main Results, Ablation Study (RQ1-RQ3), In-Depth Analysis (RQ4-RQ9), Evolving-Bank Self-Improvement (an extension) |
| ablations | bold findings inside In-depth Analysis | RQ blocks in their own subsection |
| appendix | Limitations, then setup prose only | Limitations, experimental details with one subsection per analysis protocol, full results with std, prompts, cases |

Follow Mem-Pi when there are five or more questions or any analysis needs a protocol, numbering RQs
continuously (RQ1-RQ9 across Ablation Study and In-Depth Analysis) so captions and appendix sections can
cite them. Otherwise follow System-1.5, which also suits a binding page limit: two subsections, each
analysis a bold finding, nothing to renumber. In the compact form the question folds into the finding's
head (System-1.5: "Direct distillation from language to latent is more effective for shortcut
learning") and no RQ label appears. Whichever form is chosen holds across every analysis subsection.
RQ labels in one and bare finding heads in the next give the reader two indexes to one section. Mem-Pi
folded its planned `Case Study` subsection into the mechanism RQ.

## The setup states how every number was produced
**Each setup run-in names what its paragraph fixes, as nouns.** `Benchmarks, readers and judges.` names
the three things the paragraph holds constant. `Benchmarks and grading.` names one thing and a gerund,
so the reader cannot tell what was fixed.

**Task framing, then one sentence per benchmark.** System-1.5 opens with what is measured ("We evaluate
the effectiveness and efficiency of \ourmethod{} on two reasoning-intensive tasks"). Mem-Pi gives each
benchmark its size, domains, exact split and whose split it follows:
```latex
\textbf{\textsc{WebArena}}~\citep{zhou2023webarena} contains 812 multi-step browser tasks over five
domains (Shopping, CMS, GitLab, Reddit, Maps). Following WebAgent-R1~\citep{wei-etal-2025-webagent}
and WebRL~\citep{qi2024webrl}, we use a 647/165 train/test split.
```
System-1.5 names its source too ("We train models on the official training splits"). A split the paper
draws itself says so and how it was drawn. Left unattributed, it reads as inherited, and the table sits
beside papers that tested on other data.

An out-of-domain set carries its reason in the same sentence (System-1.5: "a dataset with increased
reasoning difficulty designed to test generalization beyond the original GSM8K"), and a method that builds
a store from training data states its leakage isolation (Mem-Pi: "no test task contributes a trajectory, a
hint, or a reward at any stage").

**Baselines grouped by mechanism, numbered, one clause each.** System-1.5 numbers three classes, each
glossed with "which ..." ("which compress natural language CoT into compact continuous latent
representations"). Mem-Pi labels "(i)~Workflow-based memory" and "(ii) Learning-based memory" and fixes a
shared knob once ("In both settings, we fix k = 1"). The grouping becomes the table's `\midrule` blocks.
It is itself an argument, since it says which family the paper competes with. It also fixes
the main table's row order, the groups in the order this paragraph lists them and the paper's own row
last, and `writing-table` sets how the groups are typeset. Benchmarks that divide are introduced the
same way, counted and named as families (*these fall into two families, \emph{(i)~NAME}, including X
and Y, and \emph{(ii)~NAME}, including Z*), never by the rule that splits them.

**A fairness statement that names what is not matched.** When baselines come from codebases on different
backbones, say why the method is built twice (System-1.5: "we implement two backbone versions ... to
ensure fair comparisons across different baselines"), then label every table with its backbone, which
System-1.5 never did. When the method spends a budget the baselines do not, write Mem-Pi's form and name
the controls that bound the extra budget (a zero-shot hinter and a cost appendix):
```latex
Every method draws on the \emph{same} offline JEF-Hinter bank under the same train/test isolation,
so the comparison is \emph{information-matched}: no method sees experience the others do not.
It is not compute- or supervision-matched.
```
A baseline adaptation is justified by attributability (Mem-Pi: "the alternative changes two variables at
once, the information and the operator set, which would make any resulting difference unattributable").

**When no prior system reports the suite, say so in the setup.** State what each prior system reports
instead and what the paper adds by measuring it. The absence is a fact about the field. Explained inside
a results paragraph, ahead of the headline, it reads as an excuse and pushes the headline out of the
place a skimming reader looks.

**Metrics.** One metric is stated once in the setup (Mem-Pi: "We use task success rate (SR) as the reward
signal across all benchmarks"). Abbreviated efficiency metrics are defined in the setup, with their
construction in the appendix (System-1.5: FLOPs "approximating the dot-product and matrix-vector
operations within Transformer layers, while omitting nonlinearities, normalization, and residual
connections"). The main caption only expands the abbreviation, in the plain sentence `writing-caption`
prescribes.

**Implementation, seeds and cost go to the appendix behind a live pointer** ("Implementation details are
in Appendix", Mem-Pi). System-1.5's pointer is commented out, so no text leads to its appendix, which
then repeats Datasets and Baselines almost verbatim. The appendix adds optimizer, schedule, hardware,
wall-clock and seed count, as System-1.5's does, says where the standard deviations are, which
System-1.5's does not, and defines cost before the cost table ("GPU-hours are wall-clock training time
multiplied by eight", Mem-Pi).

## The results paragraph: claim, evidence, reason
A results paragraph opens with a bold full-sentence claim whose subject is the method or the finding, never
the table, then two or three representative numbers against a named reference, then why. Every System-1.5
finding and every Mem-Pi finding outside RQ1-RQ2 opens its paragraph this way. The check is mechanical.
Read the grammatical subject of each paragraph's first sentence. A table, a figure or a section
("Table~\ref{tab:main-results} presents", "This subsection reports") spends the most-read sentence on
what the caption already says. The one exception is a sentence whose claim is about the display itself,
such as what its measurement leaves out.
```latex
% System-1.5 drafted a table-first opener and commented it out before submission:
% Table~\ref{tab:main-results} presents the accuracy and efficiency results across the three test sets.
% What shipped instead: claim, then an "As shown in Table" evidence sentence.
\textbf{\ourmethod{} outperforms previous state-of-the-art methods in latent-space reasoning in both
accuracy and efficiency.} As shown in Table~\ref{tab:main-results}, compared to iCoT, Coconut, CODI,
and \emph{pause} token, \ourmethod{} achieves higher accuracy and greater overall speedup.
```
The display holds every other cell and is cited for them. The reason ties the finding back to the
mechanism the method was built around. Without it the paragraph only restates the table. Read in order,
the bold heads alone state the section's results. A paragraph that restates every suite, scale and
variant makes the same comparison six times, buries the one that mattered, and never says why.

Nothing comes between the claim and its numbers. An explanation of why prior work is hard to compare
against, put first, pushes the headline into mid-paragraph, where a reader who skims misses it. That
explanation goes after the numbers, or into the setup.

Mem-Pi puts the baselines' numbers inline after its own ("\textbf{Experience distillation alone already
matches or surpasses RL-based baselines.} ... achieves 35.0\% on \textsc{WebArena}, comparable to Memory-R1
(33.2\%) and MemRL (34.0\%)"). The reason sits beside the number it explains. System-1.5 follows "a 1.95×
reduction in average FLOPs per decoding step" with the mechanism ("due to its dynamic step shortcut
mechanism, which allows hidden states ... to be directly copied and reused in the next decoding step") and
a contrast saying the baselines "still reprocess these states starting from the first layer".
Mem-Pi uses "suggesting that" and "We attribute this to". An untested reason is an attribution, never
"validates". The reason says why, not that. Mem-Pi's "We attribute this to a mismatch between the two
rewards: $R_{\text{sim}}$ encourages imitation of reference memories, whereas $R_{\text{task}}$ rewards
memories that improve task success" names a mechanism. "This demonstrates the effectiveness of our
approach" only restates that the number was good, and it is cut. The table reference comes second
(System-1.5: "As shown in Table~\ref{...}") or trails (Mem-Pi: "As summarized in Table~\ref{...}"),
never first with the claim buried, as in all three of
Mem-Pi's RQ1-RQ2 findings: "Results in Table~\ref{tab:ablation-results} show that \noindent\textbf{both
training stages are essential ...}", "Variant \textit{(i)} shows that", "Variants \textit{(ii)} and
\textit{(iii)} show that".

**Analysis paragraphs.** System-1.5 uses three steps over two paragraphs: the bold claim, then in the same
paragraph a first-person construction ("We further investigate the training strategy of \ourmethod{} by
exploring two variants: (1) Joint learning ... and (2) Full-parameter shortcut learning ..."), then a
paragraph that reads the figure and gives the reason ("As shown in Figure~\ref{fig:ablation-optimization},
both joint learning and full-parameter shortcut learning degrade ...", "We attribute this to optimization
conflicts ..."). Mem-Pi puts a bold question header over a protocol paragraph,
then bold-finding paragraphs (RQ1-RQ3, RQ5-RQ8). RQ4 and RQ9 fold protocol and result into the question
paragraph with no bold finding, so a reader skimming the heads gets only the questions. A finding may open by
naming what the last measurement misses (Mem-Pi: "Figure~\ref{fig:efficiency} counts tokens inserted into
the agent and so omits the memory model's own prefill over a long axtree observation."). Concede inside
the finding ("RAG is cheaper on both", Mem-Pi), limit it ("We claim robustness to moderate sparsity and
plausible mapping errors only."), and end on it, not on System-1.5's "highlighting the promising potential".

## Ablations: procedures as findings, components as questions
**System-1.5 frames alternative procedures as bold findings.** Its ablations ask how to train, not what to
remove: which student to distil from ("Direct distillation from language to latent is more effective for
shortcut learning") and which strategy ("Joint learning and full-parameter shortcut learning degrade the
performance"). Each variant is built in prose, an inherited schedule is stated ("We follow Coconut's
original training schedule, using six epochs in the initial stage and three in each subsequent stage"), and
a strong comparison point is chosen on purpose ("we also evaluate CODI, a distillation-based latent
reasoning model that performs competitively"). Use this for a pipeline whose steps cannot be dropped, but
still remove each mechanism once: System-1.5 never isolates either of its two, leaving only the sweep.

**Mem-Pi frames components as research questions, one per stage or objective.** "RQ1: Are both training
stages necessary?", "RQ2: Does Stage-2 decision--content policy optimization help?". Variants are italic
roman numerals, one sentence each, and a substitution names what replaces the part:
```latex
\textit{(i) w/o structured rollout} reverts to vanilla GRPO without paired abstain--generate branches;
\textit{(ii) w/o $\Delta$-gating} replaces gated fusion in Eq.~\ref{eq:per-token-advantage} with a naive
sum of decision- and content-level advantages;
\textit{(iii) w/o $R_m$} drops the length-aware memory-quality reward.
```
Use this when components are separable. Group rows under italic headers by the axis tested (*Training
Stages*, *RL Objective*), mix alternatives with removals ("Unified single-stage collapses both stages into
one RL phase"), and write findings that name the variant and rank by drop size.

A question-framed block runs question, variants, then a paragraph that opens on the bold answer and gives
numbers and attribution after it.
```latex
\noindent\textbf{RQ1: Are both training stages necessary?}\ We compare against two single-stage
variants. \textit{(i) w/o Stage~1 init} skips experience distillation. \textit{(ii) Unified
single-stage} collapses both stages into one RL phase.

\textbf{Both training stages are essential, and unified training suffers the largest drop.}
Unified single-stage training degrades \textsc{WebArena} by 6.8\,pp and removing Stage~1
initialization by 5.2\,pp, suggesting that without a well-initialized memory distribution, online RL
struggles to converge.
```
This is Mem-Pi's RQ1 with the answer moved to the front of its paragraph and the unified single-stage
definition cut to one clause (Rule 5). The shipped form quoted above opens that paragraph with the table.
When `writing-ablation`'s construction paragraph in the setup already defines the variants, the RQ
paragraph names them and does not rebuild them. An RQ head is the one head that may be a question,
because a bold finding answers it before any number arrives (LatentHarness: `RQ4: What does the write
gate learn?`, then `Gain credit opens the write gate for derived states that later recalls reuse.`).
Every other head, whether a setup run-in, a finding or a subsection title, names a concept or states a
claim (`writing-paper`).

**Source of gains is a factorial with single-change controls.** When the gain could come from an extra
model call or extra training, Mem-Pi's RQ3 crosses two factors per panel and builds each control to isolate
one confound. The zero-shot hinter "is an untrained Qwen2.5-7B-Instruct given the same hinter prompt and
decoding budget but no bank access, so it isolates the cost of the extra inference call alone", and RAG +
learned abstention keeps "the identical Stage-2 objective, reward and 200-step budget, changing only what
is injected". Check additivity both ways ("$4.1 + 7.6$ or $8.4 + 3.3$"). In either framing, each ablation
claim carries a number and its benchmark, and every benchmark is covered or the gap explained, which
System-1.5's unquantified bars and Mem-Pi's two-of-four ablation table both miss.

## Analyses that earn a place
Each analysis answers one mechanism or robustness question, shares a number with the main table, and
defines its statistic in the appendix well enough to recompute it.

| question | form | example |
|---|---|---|
| can compute be traded at test time | 2-D sweep heatmap, cells labelled, a boundary at the baseline's score, default cell equal to the main-table value | System-1.5: 6x6 grid over $\lambda_\text{depth}$ and $\lambda_\text{step}$, a red boundary around the cells above CoT's 46.94, default cell 46.66 as in Table 1 |
| does it help where it should | bin by difficulty, report both ends of two opposite trends | Mem-Pi: "from $+1.3$\,pp on the easiest bin to $+9.7$\,pp on the hardest" |
| does it transfer | an unseen agent without retraining, plus a counted error statistic | Mem-Pi: "Only 6/165 WebArena and 4/134 ALFWorld decisions are wrong" |
| does it survive shift | leave-one-domain-out against a conservative baseline, three sampled perturbations per condition, a margin range | Mem-Pi: RAG keeps the full bank, "making the comparison conservative" |
| is the intermediate output good | blinded judge on named criteria, correlated with downstream success | Mem-Pi: "$\rho{=}0.43$ against $\rho{=}0.11$" |
| what does it cost | tokens, latency with its breakdown, GPU-hours beside the baselines' | Mem-Pi: "1.8\,s (0.7\,s prefill, 1.1\,s decoding)", "154 GPU-hours of training against 312 for Memory-R1" |
| why does it win | success-set counts, one worked case per region in the appendix | Mem-Pi: "29 of the 165 tasks that \ourmethod{} solves and RAG does not, against 13 where the reverse holds" |

The claim must match its display, which System-1.5's "approximately equally sensitive to adjustments along
both dimensions" does not over a heatmap whose default row runs from 46.66 to 49.11 across the step
constant while its default column runs from 45.87 to 46.77 across the depth threshold. Mem-Pi
defines protocols to be rerun ("Corruption is defined mechanically so that it is reproducible") and states
thresholds in units a reader can picture ("differ by at least three rollouts").

A split analysis names its groups, never the operation that produced them. Categorical groups, error
categories among them, are counted and named as families in `writing-paper`'s form, and ordinal bins are
named by their range, as Mem-Pi names its easiest bin ("base-agent SR from 80\% to 100\%"). "Splitting
those questions by where the gold session lands isolates the effect" and "by which tier is varied" leave
the reader to rebuild the partition, and the reader rebuilds it differently from the author.

## Table, figure, appendix
| evidence | display | source |
|---|---|---|
| every method on every benchmark | full-width `table*`, rows in the setup's baseline groups, columns grouped by dataset as `writing-table` sets them | both |
| a few variants the adjacent paragraph reads | wrapped table (`wrapfigure` with `\captionof{table}`), in Mem-Pi an ablation table printing signed subscript deltas, whose change marks are `writing-ablation`'s | Mem-Pi |
| paired variants | bar chart, colour code explained in the caption, value labels, dataset named | System-1.5, which has neither the value labels nor the dataset |
| a two-knob sweep / performance against cost | annotated heatmap / scatter | System-1.5 / Mem-Pi |
| difficulty bins, training dynamics, std table, protocol tables, cases | appendix | Mem-Pi |

In its experiments section System-1.5 has one table and stacks two figures in one right-side wrapfigure.
Mem-Pi's has five tables and one figure, and a source comment records why a display moved to the
appendix ("the quantitative hint-level evaluation ... now carries the reliability argument in the main
paper"). A case enters only tied to counts ("19 tasks
solved only by \ourmethod{}, and 10 solved by both the base agent and \ourmethod{} but not RAG", Mem-Pi).
A trajectory over steps or epochs is a figure and its endpoint is a table cell, so a per-epoch table
beside the curve is deleted (Mem-Pi's training dynamics are an appendix figure).

**Marks and captions.** Bold best and underline second per column, the paper's row last in the main
table and tinted, and the column groups are `writing-table`'s (System-1.5 bolds the baseline CoT where
it wins GSM8K accuracy, and Mem-Pi tints its last row with `\rowcolor{bestcell}`). The reference row
shows `-` in its own ratio cells. The main caption names the reference and states the marks rule
("Best and second-best results are highlighted with \textbf{bold} and \underline{underline},
respectively.", System-1.5). The caption itself follows
`writing-caption`: it names the float's object and the method, declares the marks, and leaves the metric,
the columns' definitions and the finding to the setup and the results paragraph.

## Numbers and traceability
| | System-1.5 | Mem-Pi |
|---|---|---|
| precision | two decimals, `Acc. (%)` in the header | one decimal, `43.1\%` in text |
| comparison | absolute beside the reference: "achieves 48.61\% accuracy, outperforming CoT's 47.36\%" (the form only: the table's CoT cell is 47.62) | signed points over a named reference: "$+$23.8\,pp" |
| ratios and deltas | `20.27$\times$` relative to CoT, no deltas in tables | `$37.9_{\scriptscriptstyle-5.2}$` subscripts |
| dispersion | none | `$27.1_{\pm 0.4}$` in an appendix table |

The table records what each paper shipped, not a format to copy into cells. A cell's format, and whether
a cell may carry a difference at all, is `writing-table`'s. Mem-Pi's subscripts sit in its ablation
table, the one table `writing-ablation` lets print changes. This section governs numbers in prose.

A difference that stands alone, in parentheses or after its reference, carries an explicit sign and its
unit, bound by a thin space, `($+$23.8\,pp)`, which keeps the unit on the number's line. After a verb that
already gives the direction (`degrades \textsc{WebArena} by 5.2\,pp`) the magnitude stays unsigned.
Percentage points and percent are different quantities. A change from 42.0\% to 50.3\% is `$+$8.3\,pp`.
Written `$+$8.3\%` it claims a relative change, which is in fact $+$19.8\%, and a relative change quoted
without its points makes a gain on a low base look larger than it is. The rule is `writing-paper`'s, and
`writing-table` applies it to cells by putting the unit in the column header.

In prose, use System-1.5's form when every number is relative to one reference, as efficiency ratios to
CoT are, and Mem-Pi's signed points when gains are compared across several baselines. Name the reference
in the same clause, give counts as fractions ("6/165") and relative savings with absolute anchors ("31%
fewer than Stage 1 (200 tokens)"). A relative gain on a small base takes the same anchor. A 50% relative
improvement on a base of 4% is two points. Report seed dispersion once against the gaps: "Standard
deviations stay below $1.2$\,pp on every cell, well under the inter-method gaps in the same column, so
the ranking is not seed-induced." (Mem-Pi).
System-1.5's means alone license no ranking. Before submission, recompute every prose number from its
display and grep the abstract, introduction, conclusion and captions for it. The same pass also checks
that each mechanism the abstract names is measured by an experiment or an ablation family
(`writing-ablation`). A derived number states its derivation once (System-1.5's 92.31% is 1-2/26 from
the Steps column), and `Avg` states its weighting.

## Rules
1. **The setup names what is not matched, and when no prior system reports the suite, it says so and
   what each reports instead.** An unqualified fairness claim is read as covering compute and
   supervision, which Mem-Pi explicitly disclaims.
2. **Each benchmark sentence gives size, split and whose split it follows, or says the paper drew the
   split and how, and the baseline groups are the main table's `\midrule` blocks and its row order,**
   so results compare with prior work and the reader keeps one taxonomy.
3. **Each results paragraph opens with a bold claim about the method or finding, and each quantitative
   claim carries a number, its reference and its dataset.** "A significant accuracy drop" cannot be checked.
4. **An untested reason is written as an attribution.** "likely hinder" beside a measured drop reads as a
   second result.
5. **Each ablation variant is named, enumerated and built in one short sentence saying what replaces the
   removed part.** Mem-Pi's unified single-stage definition runs to over 60 words.
6. **A gain that could come from extra compute or an extra call gets a factorial with single-change
   controls,** because leave-one-out cannot separate the two.
7. **Each analysis statistic is defined in the appendix with its threshold, behind a live pointer.**
   Mem-Pi's "differ by at least three rollouts" lets a reader recount a routing error. System-1.5's
   commented-out pointer leaves its setup appendix reachable only by browsing.
8. **Each prose number is recomputed from a display, with abstract, introduction, conclusion and captions
   in the same pass.** Both papers shipped mismatches. The same pass also checks that each mechanism the
   abstract names is measured by an experiment or an ablation family (`writing-ablation`).
9. **Seed dispersion is reported once and compared to the gaps.** Means alone cannot carry a ranking.
10. **Columns, averaging and the dataset are defined once, in the setup, and the caption names the
    float's object (`writing-caption`).** Mem-Pi's WorkArena `Avg` cannot be recomputed from its cells,
    and System-1.5's ablation figure never names what its bars measure, so they read only as
    "Performance".
11. **A results subsection reports a measured result, or it is cut.** Mem-Pi's Evolving-Bank
    Self-Improvement subsection says what a result "would establish" beside a table whose source banner
    reads "PLACEHOLDER NUMBERS -- NOT MEASURED".
12. **Pick one ablation framing per paper and hold it across the section.** Finding-framed (System-1.5)
    opens each ablation with its bold finding. Question-framed (Mem-Pi) opens each with a numbered RQ
    head, and a bold finding answers it before the numbers. In both, the attribution comes last.
13. **A difference standing alone carries its sign, its unit and a thin space, and percentage points
    are not percent.** A relative gain on a small base carries its absolute anchor.

## Anti-patterns
- **The swapped cell and headline drift.** System-1.5 writes "46.94\% and 38.32\% ... closely matching CoT
  fine-tuning results of 46.67\% and 38.28\%", the table's numbers on the wrong rows plus one found
  nowhere, gives CoT's StrategyQA accuracy as 47.36\% where the table has 47.62, and its abstract's
  "91.0\% on average" is 92.31% in the results. Prose written against an earlier table, never
  rechecked.
- **The unnumbered ablation.** "a more pronounced drop" off bars with no values, dataset or named metric.
- **Explanation as evidence.** "These conflicts likely hinder ...", "potentially indicating that the length
  regularizer encourages concise memory", "This validates offline parametric knowledge".
- **Conclusion-last results.** A paragraph that walks through every number and states the finding in
  its final sentence. A reader who skims gets nothing.
- **The table-of-contents paragraph.** "Table 1 positions X. Table 2 ablates Y. Table 3 reports Z."
  Three sentences that restate three captions and state no result.
- **Effectiveness as interpretation.** "This demonstrates the effectiveness of our approach", or
  System-1.5's "highlighting the promising potential of \ourmethod{}", in the reason slot. It restates the
  number and names no mechanism.
- **The claim its figure contradicts.** "approximately equally sensitive" over a heatmap that is not.
- **Significance without a test.** Mem-Pi's head "The RL stage provides significant additional gains", and
  System-1.5's checklist "demonstrating not only statistical but also practical significance".
- **The wrong superlative or reference.** Mem-Pi lists Maps (+3.0) among "the largest jumps" over Shopping
  (+4.0) and GitLab (+3.4), calls gains over the base agent "over RAG", and writes "$3$--$5\times$" where
  the ALFWorld ratio on the training-time agent is 11.8 over 2.1, or 5.6.
- **The broken legend, the undefined average.** Mem-Pi underlines Stage-1 cells that four methods beat
  (CMS 17.4, WorkArena Filt 9.0) under "Underline: second best", and the full model's WorkArena category
  cells average 53.7 where `Avg` shows 50.3.
- **The stale cross-reference.** Mem-Pi's appendix still reserves a backbone "for the visual-input ablation
  in Section~\ref{sec:in-depth-analysis} (RQ3)", but RQ3 is now the source-of-gains factorial in the
  Ablation Study and no RQ covers visual input. Renaming or renumbering an RQ needs a grep for its label.
- **The unlabelled backbone.** Two backbones built for fairness, a table silent on which one, and an
  appendix naming the model two ways ("LLaMA 3.1-1B", "LLaMA 3.2 1B").
- **The unexplained anomaly.** System-1.5's GSM-HARD `# Steps` is 4 for iCoT, Coconut, CODI and
  System-1.5, which show 2 on GSM8K and StrategyQA, while the default decoding step count is 2, and the
  text never says why.

## Companions
`writing-ablation` (which ablation variants exist and how the ablation table is grouped, the one table allowed to print changes) · `writing-paper` (the sentence and the finding-first head) · `writing-table` (the grid, cell format, marks and the tinted row) · `writing-caption` (the caption) ·
`drawing-figure` (the picture) · `writing-literature` (the related-work section that follows) ·
`writing-chatgpt` (prose goes through the writer) · `output-analysis` (which runs to compare) ·
`conventions` (family index).
