---
name: docs-analysis
description: "Build a paper's experiments and analysis section: section order, what the setup states, how each results paragraph is shaped, how ablations are framed and grouped, which evidence is a table, a figure or an appendix entry, and how numbers are reported and kept traceable, learned from System-1.5 and Mem-Pi."
when_to_use: "Use when drafting or revising Experiments, Main Results, Ablation Study or In-depth Analysis, when choosing between finding-framed and question-framed ablations, when placing a result in a table, a figure or the appendix, or when a reviewer says the ablations have no numbers, the text disagrees with the table, or a statistic is never defined."
---
# Skill: docs-analysis

## Purpose
An experiments section is where a reader checks the claims against the numbers. This skill fixes its
order, setup, paragraph shape, ablation framing, displays and number format, all learned from two papers:
System-1.5 (a compact NeurIPS camera-ready) and Mem-Pi (a research-question-driven ICLR draft). Where they
differ, the body says which to follow and when. The errors each shipped are the anti-patterns.

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
- Not for the grid itself (`docs-table`), the plot (`docs-figure`), sentence style (`writing-paper`,
  `writing-style`), or choosing which runs to compare (`output-analysis`).

## Section order: compact or question-driven
Both papers open `Experiments` with bold run-in setup paragraphs and no setup subsection, put the main
table first under `Main Results`, and place Related Work and Conclusion after Experiments. Then:

| | System-1.5 (compact) | Mem-Pi (question-driven) |
|---|---|---|
| setup run-ins | `Datasets.`, `Baselines.` | `Benchmarks.`, `Baselines.`, `Agent and memory configuration.`, `Information-matched comparison.` |
| subsections | Main Results, In-depth Analysis | Main Results, Ablation Study (RQ1-RQ3), In-Depth Analysis (RQ4-RQ9), Evolving-Bank Self-Improvement (an extension) |
| ablations | bold findings inside In-depth Analysis | RQ blocks in their own subsection |
| appendix | Limitations, then setup prose only | Limitations, experimental details with one subsection per analysis protocol, full results with std, prompts, cases |

Follow System-1.5 when there are at most three analyses and the page limit binds: two subsections, each
analysis a bold finding, nothing to renumber. Follow Mem-Pi when there are five or more questions or the
analyses need protocols, numbering RQs continuously (RQ1-RQ9 across Ablation Study and In-Depth Analysis)
so captions and appendix sections can cite them. Mem-Pi folded its planned `Case Study` subsection into
the mechanism RQ.

## The setup states how every number was produced
**Task framing, then one sentence per benchmark.** System-1.5 opens with what is measured ("We evaluate
the effectiveness and efficiency of \ourmethod{} on two reasoning-intensive tasks"). Mem-Pi gives each
benchmark its size, domains, exact split and whose split it follows:
```latex
\textbf{\textsc{WebArena}}~\citep{zhou2023webarena} contains 812 multi-step browser tasks over five
domains (Shopping, CMS, GitLab, Reddit, Maps). Following WebAgent-R1~\citep{wei-etal-2025-webagent}
and WebRL~\citep{qi2024webrl}, we use a 647/165 train/test split.
```
An out-of-domain set carries its reason in the same sentence (System-1.5: "a dataset with increased
reasoning difficulty designed to test generalization beyond the original GSM8K"), and a method that builds
a store from training data states its leakage isolation (Mem-Pi: "no test task contributes a trajectory, a
hint, or a reward at any stage").

**Baselines grouped by mechanism, numbered, one clause each.** System-1.5 numbers three classes, each
glossed with "which ..." ("which compress natural language CoT into compact continuous latent
representations"). Mem-Pi labels "(i)~Workflow-based memory" and "(ii) Learning-based memory" and fixes a
shared knob once ("In both settings, we fix k = 1"). The grouping becomes the table's `\midrule` blocks.

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

**Metrics.** One metric is stated once in the setup (Mem-Pi: "We use task success rate (SR) as the reward
signal across all benchmarks"). Abbreviated efficiency metrics are defined in the main-table caption, with
their construction in the appendix (System-1.5: FLOPs "approximating the dot-product and matrix-vector
operations within Transformer layers, while omitting nonlinearities, normalization, and residual
connections").

**Implementation, seeds and cost go to the appendix behind a live pointer** ("Implementation details are
in Appendix", Mem-Pi). System-1.5's pointer is commented out, so no text leads to its appendix, which
then repeats Datasets and Baselines almost verbatim. The appendix adds optimizer, schedule, hardware,
wall-clock and seed count, as System-1.5's does, says where the standard deviations are, which
System-1.5's does not, and defines cost before the cost table ("GPU-hours are wall-clock training time
multiplied by eight", Mem-Pi).

## The results paragraph: claim, evidence, reason
A results paragraph opens with a bold full-sentence claim whose subject is the method or the finding, never
the table, then one to three sentences of numbers against a named reference, then why. Every System-1.5
finding and every Mem-Pi finding outside RQ1-RQ2 opens its paragraph this way.
```latex
% System-1.5: claim, then an "As shown in Table" evidence sentence.
\textbf{\ourmethod{} outperforms previous state-of-the-art methods in latent-space reasoning in both
accuracy and efficiency.} As shown in Table~\ref{tab:main-results}, compared to iCoT, Coconut, CODI,
and \emph{pause} token, \ourmethod{} achieves higher accuracy and greater overall speedup.
```
Mem-Pi puts the baselines' numbers inline after its own ("\textbf{Experience distillation alone already
matches or surpasses RL-based baselines.} ... achieves 35.0\% on \textsc{WebArena}, comparable to Memory-R1
(33.2\%) and MemRL (34.0\%)"). The reason sits beside the number it explains. System-1.5 follows "a 1.95×
reduction in average FLOPs per decoding step" with the mechanism ("due to its dynamic step shortcut
mechanism, which allows hidden states ... to be directly copied and reused in the next decoding step") and
a contrast saying the baselines "still reprocess these states starting from the first layer".
Mem-Pi uses "suggesting that" and "We attribute this to". An untested reason is an attribution, never
"validates". The table reference comes second (System-1.5: "As shown in Table~\ref{...}") or trails
(Mem-Pi: "As summarized in Table~\ref{...}"), never first with the claim buried, as in all three of
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

## Table, figure, appendix
| evidence | display | source |
|---|---|---|
| every method on every benchmark | full-width `table*`, one column group per dataset (the same four metrics under each in System-1.5, sub-domains plus `Avg` in Mem-Pi), rows in the setup's baseline groups | both |
| a few variants the adjacent paragraph reads | wrapped table (`wrapfigure` with `\captionof{table}`), signed subscript deltas | Mem-Pi |
| paired variants | bar chart, colour code explained in the caption, value labels, dataset named | System-1.5, which has neither the value labels nor the dataset |
| a two-knob sweep / performance against cost | annotated heatmap / scatter | System-1.5 / Mem-Pi |
| difficulty bins, training dynamics, std table, protocol tables, cases | appendix | Mem-Pi |

In its experiments section System-1.5 has one table and stacks two figures in one right-side wrapfigure.
Mem-Pi's has five tables and one figure, and a source comment records why a display moved to the
appendix ("the quantitative hint-level evaluation ... now carries the reliability argument in the main
paper"). A case enters only tied to counts ("19 tasks
solved only by \ourmethod{}, and 10 solved by both the base agent and \ourmethod{} but not RAG", Mem-Pi).

**Marks and captions.** Bold best and underline second per column, even when a baseline wins (System-1.5
bolds CoT on GSM8K accuracy). The reference row shows `-` in its own ratio cells, and the paper's row goes
last (System-1.5) or is shaded with `\rowcolor{bestcell}` (Mem-Pi). The main caption defines every
abbreviated column and its reference and states the rule ("Best and second-best results are highlighted
with \textbf{bold} and \underline{underline}, respectively.", System-1.5). The caption itself follows
`docs-caption`: it names the float's object and the method, declares the marks, and leaves the metric,
the columns' definitions and the finding to the setup and the results paragraph.

## Numbers and traceability
| | System-1.5 | Mem-Pi |
|---|---|---|
| precision | two decimals, `Acc. (%)` in the header | one decimal, `43.1\%` in text |
| comparison | absolute beside the reference: "achieves 48.61\% accuracy, outperforming CoT's 47.36\%" (the form only: the table's CoT cell is 47.62) | signed points over a named reference: "$+$23.8\,pp" |
| ratios and deltas | `20.27$\times$` relative to CoT, no deltas in tables | `$37.9_{\scriptscriptstyle-5.2}$` subscripts |
| dispersion | none | `$27.1_{\pm 0.4}$` in an appendix table |

Use System-1.5's form when every number is relative to one reference, as efficiency ratios to CoT are, and
Mem-Pi's when gains are compared across several baselines. Name the reference in the same clause, give
counts as fractions ("6/165") and relative savings with absolute anchors ("31% fewer than Stage 1 (200
tokens)"). Report seed dispersion once against the gaps: "Standard deviations stay below $1.2$\,pp on every
cell, well under the inter-method gaps in the same column, so the ranking is not seed-induced." (Mem-Pi).
System-1.5's means alone license no ranking. Before submission, recompute every prose number from its
display and grep the abstract, introduction, conclusion and captions for it. A derived number states its
derivation once (System-1.5's 92.31% is 1-2/26 from the Steps column), and `Avg` states its weighting.

## Rules
1. **The setup names what is not matched.** An unqualified fairness claim is read as covering compute and
   supervision, which Mem-Pi explicitly disclaims.
2. **Each benchmark sentence gives size, split and whose split it follows, and the baseline groups are the
   main table's `\midrule` blocks,** so results compare with prior work and the reader keeps one taxonomy.
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
   in the same pass.** Both papers shipped mismatches.
9. **Seed dispersion is reported once and compared to the gaps.** Means alone cannot carry a ranking.
10. **Columns, averaging and the dataset are defined once, in the setup, and the caption names the
    float's object (`docs-caption`).** Mem-Pi's WorkArena `Avg` cannot be recomputed from its cells,
    and System-1.5's ablation figure never names what its bars measure, so they read only as
    "Performance".
11. **A results subsection reports a measured result, or it is cut.** Mem-Pi's Evolving-Bank
    Self-Improvement subsection says what a result "would establish" beside a table whose source banner
    reads "PLACEHOLDER NUMBERS -- NOT MEASURED".

## Anti-patterns
- **The swapped cell and headline drift.** System-1.5 writes "46.94\% and 38.32\% ... closely matching CoT
  fine-tuning results of 46.67\% and 38.28\%", the table's numbers on the wrong rows plus one found
  nowhere, gives CoT's StrategyQA accuracy as 47.36\% where the table has 47.62, and its abstract's
  "91.0\% on average" is 92.31% in the results. Prose written against an earlier table, never
  rechecked.
- **The unnumbered ablation.** "a more pronounced drop" off bars with no values, dataset or named metric.
- **Explanation as evidence.** "These conflicts likely hinder ...", "potentially indicating that the length
  regularizer encourages concise memory", "This validates offline parametric knowledge".
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
`docs-ablation` (which ablation variants exist and how the ablation table is grouped, the one table allowed to print changes) · `writing-paper` (the sentence and the finding-first head) · `docs-table` (the grid, marks, caption) ·
`docs-figure` (the picture) · `docs-literature` (the related-work section that follows) ·
`writing-chatgpt` (prose goes through the writer) · `output-analysis` (which runs to compare) ·
`conventions` (family index).
