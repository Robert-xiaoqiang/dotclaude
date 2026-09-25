---
name: docs-methodology
description: "Write a paper's method section: an overview that goes from the design goal to the components and their training, the inherited base model formulated before anything is added, each new component told as motivation, design and explanation ('we model X as Y because Z'), modules defined by their inputs and outputs in causal order, intuition and a standard-design contrast around every hard equation, and one hierarchy of claims from abstract to introduction to method, learned from the LatentHarness method rewrites."
when_to_use: "Use when drafting or revising a Method section, its opening overview, or a paragraph that introduces a new component or a hard equation, and when an author or reviewer says the method 'rushes to state facts', opens abruptly, uses an object before defining it, or has an equation nobody can follow."
---
# Skill: docs-methodology

## Purpose
A method section fails in a way that looks like confidence: every sentence is a true statement of
what the system does, and the reader still cannot say why any of it is there. The author's verdict
on such a draft was that it "always rushes to state its position and facts". The fix is a rule about
*who owes an explanation*. Prior work may be stated directly, as background the reader can look up.
Every choice the paper makes itself owes the reader a motivation before it and an explanation after
it. This skill fixes the order of the section, the shape of each component paragraph, and what must
surround a hard equation. `writing-paper` owns the sentence, `docs-analysis` the experiments,
`docs-figure` the method figure.

## Contents
- [When to Use](#when-to-use)
- [The one rule](#the-one-rule)
- [Adapt the depth](#adapt-the-depth)
- [The section overview](#the-section-overview)
- [Order: base model first, then causal order](#order-base-model-first-then-causal-order)
- [A new component: motivation, design, explanation](#a-new-component-motivation-design-explanation)
- [Modules by inputs and outputs](#modules-by-inputs-and-outputs)
- [Architecture before credit](#architecture-before-credit)
- [Hard equations](#hard-equations)
- [One hierarchy from abstract to method](#one-hierarchy-from-abstract-to-method)
- [Checking a method section](#checking-a-method-section)
- [Worked example: LatentHarness](#worked-example-latentharness)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Drafting a Method section, or its first paragraph, before the subsections.
- A paragraph introduces a component the paper designed (a memory, a gate, a router, a loss).
- An equation or a derivative sits in the text with no sentence telling the reader what it is for.
- An author says the section reads as a list of facts, or a reviewer asks "why this design?".
- Not for the experiments (`docs-analysis`), related work (`docs-literature`), or sentence-level
  style (`writing-paper`, `writing-style`).

## The one rule

> **Prior work is stated. Our own choices are argued.**

Background the paper inherits (a looped Transformer, GRPO, the delta rule) is stated directly and
compactly, with a citation, in one or two sentences a reader who does not know it can follow. A
choice the paper makes (to add a memory, to gate its writes, to credit the gate a certain way) is
never stated bare. It comes with the problem that forces it and the reason this form fits.

| sentence | kind | verdict |
|---|---|---|
| "A looped latent reasoner applies one weight-tied block up to $R$ times." | prior work | state it |
| "The memory is a fast-weight matrix written by the delta rule." | our choice, stated as fact | argue it |
| "Because the loop can only recompute from its current state, we model the latent memory as a fast-weight matrix, which stores results for one matrix-vector read." | our choice, argued | keep |

The test, applied to each sentence that describes the method: *did the paper choose this?* If yes,
the sentence before it gives the reason, or the sentence itself does ("we model X as Y because Z").

## Adapt the depth
The full argument (motivation, design, explanation) is for the paper's central and non-obvious
choices, the ones a reviewer would question. A component that is standard in the field (a fast-weight
memory, a delta-rule write, a GRPO advantage, a KL regularizer, a looped Transformer) gets one clause
of *why* and one sentence of *what*, with its citation, and nothing more. The author rejected a
latent-memory paragraph that argued fast weights, the delta rule and prompt compilation at length:
"though docs-methodology is important, no need to follow it every time, concise when it is a very
common background". The same judgment decides structure.
- Merge a short background definition into the paragraph that uses it. "Looped latent reasoning" and
  "the latent Think action" are one paragraph, since Think is just one more application of the block.
- Merge short consecutive equations into one display separated by a comma,
  `g=\sigma(\cdots),\qquad M'=M+g(v-Mk)k^\top`, instead of a two-line `align`.
- Write the base model's composition inline when nothing later refers to it by number.
- Keep the full treatment, with intuition, named factors and edge cases, for the equation that carries
  the paper's contribution (for LatentHarness, the gate credit), not for every equation.

## The section overview
The first paragraph of the section is a roadmap one level more detailed than the introduction and
one level less technical than the subsections. It runs in this order.

1. **What it is built on and what it adds, with the goal.** "\ourmethod{} builds on looped latent
   reasoning and inserts recall into the loop, so that a latent state can reuse stored evidence and
   results instead of recomputing them."
2. **The components, named in the order the subsections define them.** "Specifically, a latent
   \actTHINKop{} action applies the shared block once more, a latent memory stores ..., and a latent
   action policy chooses ... ."
3. **How they are trained, at the level of ideas.** "We train the policy and the memory with
   counterfactual policy distillation, whose one-step branches serve two roles ..." The loss formulas,
   penalties and weights stay in the subsections.

Never open with the problem stated as the method's own premise ("A looped reasoner must decide at
each latent state whether to compute again, recall, or emit"). It asks the reader to accept a framing
the paper has not yet introduced, and it states our design as if it were a fact about the world.

## Order: base model first, then causal order
- **Formulate the inherited base model before adding anything.** Write it in the form its own papers
  use, for a looped model the composition $h^{(R)}=F_\theta\circ\cdots\circ F_\theta(h^{(0)})$ with
  decoding at any depth and the learned exit. This is prior work, stated directly.
- **Then introduce each addition in causal order**, so that nothing reads or updates an object that
  has not been defined. An action that writes memory comes after the memory is defined, or the write
  equation sits beside the action. A policy that reads the memory comes after the memory.
- **Assemble composite objects after their parts.** A state $s=(h,M,n)$ is defined once $h$, $M$ and
  $n$ each mean something, not before.
- **Parameter lists come last**, after every parameter has appeared in an equation.
- **No forward references to the next subsection** for anything the current paragraph needs to be
  understood. A reference to a later equation is a sign the equation is in the wrong place.

## A new component: motivation, design, explanation
Each component the paper adds is one paragraph with three moves.

1. **Motivation.** The problem that exists without it, stated in terms of the base model just
   formulated. "A loop can only recompute from its current state, so evidence outside it and results
   derived earlier are lost."
2. **Design, phrased as a choice.** "We model the latent memory as a fast-weight matrix because it
   stores associations with constant size and reads them with one matrix-vector product, far cheaper
   than another block application." Give the prior-work concept in one plain sentence for readers who
   do not know it, then the equation.
3. **Explanation.** What each term does and one consequence the reader can check ("a key orthogonal
   to $k$ reads the same value as before").

Say *why here* as well as *why this form*: what about this model makes the component necessary, and
what about the component makes it fit this model. When the paper cannot support a specific constant
or restriction (a cap, a scale, a linear head), state it as a design setting and put the value in the
appendix. Never invent a rationale to fill the slot.

## Modules by inputs and outputs
A module (a router, a policy, a gate, a reader) is defined by what it reads, what it outputs, and what
its output changes, in that order.

```latex
% WEAK: parameterization first, role implied.
A linear head $\pi_\phi(a\mid s)=\operatorname{softmax}(W_\pi[h;u])$ selects one latent action.

% STRONG: why it needs what it reads, then input, output, effect.
The policy must judge whether a recall would help before injecting it, so it reads the residual
vector $h$ and a probe $u$ of the memory read, and outputs a distribution over \actTHINKop{},
\actRECALL{} and \actEXIT{}; the selected action produces the next state by Eq.~\ref{eq:transition}.
```
(The semicolon above is illustration only. The paper's own style bans it.)

## Architecture before credit
Keep what the model computes separate from how its training assigns credit. The architecture
subsection defines the state, the components and the transition. The training subsection opens with
the limitation that motivates each signal (a task reward sees only whole answers, sampled credit
vanishes once rollouts stop splitting) and then introduces the signal. A training paragraph that has
to define the component it trains is a sign the component belongs one subsection earlier: define the
memory in the architecture, and let the credit paragraph start from "the write gate $g$ of
Eq.~\ref{eq:write_gate} learns only through executed recalls, which are rare early in training".

## Hard equations
An equation the reader cannot parse on first sight gets four things around it.

- **Before:** one sentence of intuition that says what the quantity should reward or measure. "A write
  is worth keeping when a later recall reads it and the read raises the emitted token's probability."
- **The equation itself**, with its factors named where the naming carries the meaning, for example
  `\underbrace{...}_{\text{content}}` and `\underbrace{...}_{\text{addressing}}`.
- **After:** what each factor measures, the exact edge cases (when it is zero, when it is negative),
  with exact conditions rather than approximations.
- **A contrast with the standard design.** "Compared with standard delta-rule training, the update is
  unchanged, and the only added training signal is $\mathcal{L}_{\mathrm{mem}}$."

Present the objective before its gradient: the loss says what is optimized, the gradient then shows
which cases it rewards. A short derivation (a covariance identity, a two-line chain rule) is not a
theorem. Put its result inline where it motivates the design, and move the derivation to the appendix
behind the method's single appendix pointer. Keep a theorem environment only for a non-obvious claim
the paper relies on.

## One hierarchy from abstract to method
The abstract states the idea, the introduction motivates it and names its parts, the method
formalizes them. The same claim appears at each level in the same terms, at increasing depth.
- The introduction names the method's run-in heads (for LatentHarness, *state-level action credit* and
  *gain-credited memory writing*), so the reader meets them again in the method.
- A term defined only in the method (an admissible set, a masked action) stays out of the abstract and
  introduction. Use the plain word ("allowed actions").
- Distinguish quantities the method keeps apart: a stop-gradient action gain trains the policy, a
  differentiated recall change trains the gate. A summary that says "the gains train the gate"
  contradicts the method.
- Name the same thing the same way everywhere (one verb for the paper's own operation, for example
  "recall" throughout, keeping "retrieval" for external search methods).

## Checking a method section
Before accepting a rewritten method paragraph that carries math or a claim:
1. Derive the key equation yourself.
2. Have two independent reviewers check it: ChatGPT through the writer tool (`critique`) and a
   separate Claude session (`claude -p ... --model claude-opus-5-5 < /dev/null`), each given the
   paragraph, the rest of the method, and a brief listing what to verify.
3. Accept the formulation only when both accept it. Apply their precision fixes (exact zero conditions,
   signed rather than positive credit, the stop-gradient boundary, the product order).
4. Reject a reviewer point that comes from seeing only part of the paper (a macro rendering, a table
   the reviewer was not given), and say so.
5. Polish the prose with the writer after the math is settled, then re-check that no qualification
   was dropped.

## Worked example: LatentHarness
The draft opened with the premise stated as fact and defined its memory inside the training
subsection.

```latex
% REJECTED: premise as fact, components named before the base model, memory defined as a fact
A looped reasoner must decide at each latent state whether to compute again, recall stored
information, or emit the next token. ...
\noindent\textbf{Gain-credited memory writing.}\ The memory is a fast-weight matrix written by the
delta rule ...
```

The author's skeleton, which this skill generalizes:
1. Overview: "\ourmethod{} builds on looped latent reasoning and inserts recall into the loop, so that
   ... Specifically, a latent \actTHINKop{} ..., a latent memory ..., and a latent action policy ... .
   CPD trains them, and its counterfactual branches serve two roles ..."
2. Architecture subsection: the loop as $F_\theta\circ\cdots\circ F_\theta$ (stated), \actTHINKop{} as
   one more application of the block (stated), the latent memory (motivated: why a loop needs it and
   why fast weights fit, then the delta-rule write and prompt compilation), then the policy by its
   inputs and outputs, the transition, masks and hard selection.
3. Training subsection: trajectory advantage (motivated by what a task reward can see), state-level
   action credit (motivated by the covariance factor that vanishes), gain-credited memory writing
   (only how the gate is credited, with intuition, factor names, edge cases, and the contrast with
   standard training), the final objective, one appendix pointer.

## Rules
1. **Prior work is stated, our choices are argued.** Every design choice has its reason next to it.
2. **The overview goes from goal to components to training**, one level below the introduction.
3. **The inherited base model is formulated first**, in its own papers' form.
4. **Causal order, no forward references**: nothing is used before it is defined.
5. **A new component is motivation, design ("we model X as Y because Z"), explanation**, with why here.
6. **A module is its inputs, outputs and effect.**
7. **Architecture and credit live in separate subsections.**
8. **A hard equation has intuition before, named factors, exact edge cases after, and a contrast.**
9. **Short derivations go inline with the appendix holding the steps. No trivial theorems.**
10. **One hierarchy of terms and claims from abstract to introduction to method.**
11. **Math is accepted only after two independent reviewers accept it.**
12. **No invented rationale.** An unsupported constant is a setting with its value in the appendix.
13. **Adapt the depth.** Full argument for central choices, one clause of why for common background,
    short background merged into the paragraph that uses it, short equations merged into one display.

## Anti-patterns
- **The premise as opening.** "A looped reasoner must decide ..." as the first sentence.
- **The fact-statement component.** "The memory is a fast-weight matrix." for a choice the paper made.
- **The over-explained background.** Three sentences on the delta rule, none on why this paper uses it.
- **The over-argued standard component.** A full motivation, design and explanation paragraph for a
  fast-weight memory, as if it were the contribution. One clause of why is enough.
- **The forward reference.** An action "writes by Eqs. 7 and 8" when Eqs. 7 and 8 are a subsection away.
- **The parameterization-first module.** A softmax head defined before the reader knows what it decides.
- **The bare equation.** A gradient displayed with no sentence of what it rewards.
- **The trivial theorem.** A covariance identity in a theorem environment with a proof environment.
- **The summary that contradicts the method.** "The gains train the gate" when the gains are held
  under stop-gradient.
- **The undefined symbol.** $\mathcal{A}(s)$ used in a loss before any sentence defines it.

## Companions
`writing-paper` (the sentence, citations, the finding-first head) · `writing-style` (punctuation and
word rules) · `writing-chatgpt` (every paragraph goes through the writer, and `critique` for review) ·
`docs-analysis` (the experiments section that follows) · `docs-ablation` (ablations along the design
decisions this section argues for) · `docs-figure` (the method figure) · `conventions` (family index).
