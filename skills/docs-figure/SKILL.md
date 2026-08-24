---
name: docs-figure
description: "Decide what a figure may and may not contain when it is destined for a document, and render it in whichever pipeline fits: TikZ, Mermaid, HTML/SVG, or matplotlib."
when_to_use: "Use when drawing a workflow, architecture or formulation diagram, or producing an experiment plot such as bars, curves, violins, heatmaps or scatter."
---
# Skill: docs-figure

## Purpose
Decide **what a figure may and may not contain** when it is destined for a document, and render it in
whatever pipeline fits (TikZ, Mermaid, HTML/SVG, matplotlib). Owns figure *content and style*. It does
not own which runs to compare (`output-analysis`) or how a report references a figure (`docs-weekly`).

## When to Use
- Drawing a workflow, architecture, or formulation diagram for a paper, report, or design doc.
- Producing an experiment-section plot: bars, curves, violins, heatmaps, Venn / UpSet, scatter.
- Reviewing a figure someone produced and asking whether it belongs in the document.

---

## The one rule

> **The figure is not self-contained. The document is.**

Whatever the surrounding text already says, the figure must not repeat. A figure carries **structure and
quantity**; the text carries **claim, explanation, and caption**. Every violation below is a case of the
figure trying to be readable on its own, which is a requirement nobody imposed.

### What never appears inside the image

| ✗ | why | where it belongs |
|---|---|---|
| **A headline claim** ("no cross-step credit assignment", "our method wins") | the figure is asserting, not showing | body text |
| **An explanatory sentence** ("q is never observed, so the state summarises...") | prose in an image cannot be edited, translated, or searched | body text |
| **A trailing text node under a panel** ("schematic. two routes reach s≈0, collapsing k or rotating q off it") | a caption in disguise, parked exactly where the real caption goes | caption |
| **Title or `suptitle`** | the document numbers and titles its own floats | caption |
| **A baked caption** | duplicates the caption, and the two drift | caption |
| **Bullets copied from the text** | the reader reads the same list twice, in a worse font | keep the text, cut from the figure |
| **A legend entry that is a sentence** | legends are keys, not glossaries | shorten to the arm name |
| **Units or definitions spelled out** (`accuracy (fraction of correct answers)`) | terse axis labels are the convention | caption, once |

### What the figure must carry

Names of objects, their arrangement, the direction of flow, axes, scales, tick labels, and a legend when
more than one series shares an axis. If deleting an element does not remove structure or a number, delete
it.

**The test, applied before rendering:** cover the surrounding text. If the figure is still fully
understandable, it is carrying prose that belongs in the document.

---

## Diagrams (TikZ · Mermaid · HTML/SVG)

For workflow, architecture, and formulation figures.

- **Node labels are names, not descriptions.** `Harness Policy $\pi_\omega$`, not
  `Harness Policy (the outer agent that selects interventions)`. A second line is allowed only when it
  names a mechanism (`decoding head`), never when it explains a purpose.
- **Symbols over words** wherever the document defines the symbol. `a_t=(x,g,z)` beats
  "the action, which chooses samples, guidance and criteria".
- **Group with a container, label the container once.** Bands and boxes replace repeated per-node tags.
- **Line style encodes one distinction, and the key names it in two words.** Solid vs dashed vs colour
  should each mean one thing, and a two-entry key is the whole legend.
- **Equations are content, not explanation.** A displayed update rule beside the block it governs is the
  figure doing its job. A sentence about why that rule matters is not.
- **Never end a panel with a text node.** The last element under a panel is the single most common place
  a caption gets smuggled into an image. If a node sits below the drawing, spans most of its width, and
  reads as a sentence, it is a caption and it belongs in the document. Delete it and check the real
  caption says it.

  ```tex
  % wrong: the panel explains itself
  \node[align=center] at (2.6,-0.9) {schematic. two routes reach $s\approx0$,
                                     collapsing $\mathbf{k}$ or rotating $\mathbf{q}$ off it};
  % wrong: a definition the document already displays as an equation
  \node at (2.6,0.6) {selectivity $s=\mathbb{E}_j[\cos(q_j,k_j)]-\mathbb{E}_{i\neq j}[\cos(q_j,k_i)]$};
  % right: the panel names its parts, the caption carries the rest
  \node at (0.6,1.1) {$s\approx 1$};   \node at (2.7,1.1) {$s\approx 0$};
  ```

  Three tests, cheapest first. Does it contain a finite verb. Does it start with a hedge such as
  "schematic" or "note that". Would it survive being moved into the caption verbatim. Any yes means cut
  it. Symbols, values, units and one-word or two-word part names stay, since those are the drawing, and
  axis names such as "what must persist" stay because an axis without a name is unreadable.

### Pipeline choice

| pipeline | use when | note |
|---|---|---|
| **TikZ** | the figure goes in a paper, or needs precise placement and real math | one `.tex` per figure, isolated so a change cannot break its siblings |
| **Mermaid** | the figure lives in markdown that renders it inline | routing is automatic and coarse, so expect a graph rather than a block diagram |
| **HTML/SVG** | the artifact is a web page | inline everything, no external assets |
| **matplotlib** | anything with data behind it | see below |

Keep a TikZ figure and its Mermaid twin in sync when both exist, and expect the Mermaid one to be the
lossy version. Emit vector (`pdf`) for LaTeX and a raster preview only for review.

### Geometry, which is where diagrams actually fail

- Fixed coordinates break silently when a label grows. Anchor to node borders
  (`[xshift=4mm]M.north west`) and use `fit` for containers, so a rename cannot produce an overlap.
- **Check the render, never the source.** Box collisions, arrows entering the wrong edge, and labels
  landing on lines are invisible in `.tex` and obvious in the image.
- Route so nothing crosses. A crossing is a layout failure, not a fact about the system.

---

## Data figures (matplotlib)

For experiment sections. Chart type follows the question, not the habit.

| question | figure |
|---|---|
| how does a metric evolve | line, one per run, x = step |
| which arm is ahead at a fixed point | grouped bar |
| what is the *distribution*, not the mean | violin or box, and prefer it whenever n is small |
| where do two runs agree and disagree | Venn (≤3 sets) or UpSet (>3) |
| how do two quantities relate | scatter, with the null or identity line drawn |
| a matrix of pairs or a confusion structure | heatmap, diverging colormap only when zero is meaningful |
| a rate against a rate | paired scatter with the diagonal, not two bars |

Style, matching the embed rule above:

- Terse axis labels (`step`, `loss`, `acc`). Units in the caption, once.
- **One colour per run, fixed across every figure in the document**, so a run keeps its identity.
  Colourblind-safe palette (Okabe-Ito).
- Legend inside the axes, no frame, only when more than one series. Direct labelling beats a legend when
  it fits.
- Vector output (`pdf`, or `pgf` for the paper's own fonts), font ~8–10 pt at final width, tight bbox.
- No gridlines unless they aid reading, no chart junk, no 3D, no dual y-axis.
- **Show the null.** A shuffle baseline, a chance line, or an error band, drawn as a grey band. A
  difference without its noise floor is not a result.

### Merging parallel runs

**Arms that differ in one config slot go on one axes with a legend, never one figure per arm.** The
comparison is the point, and separate figures make the reader do the overlay by eye. Split only when the
scales genuinely differ, and then say so in the caption.

---

## Reproducibility

A figure is regenerated whenever a run updates, so the generator is an artifact, not a chat one-off.

- One script or `.tex` per figure, **isolated in a figures directory beside the document**, so editing
  one cannot break another.
- The script reads from the run tree read-only and writes only into the figures directory.
- Headed with what it draws, from which runs, and how to invoke it.
- Never leave the only copy in a scratchpad (`layout-workspace`).

---

## Anti-patterns

- **A figure that reads fine with the document covered.** It has absorbed the document's job.
- **A claim, a conclusion, or a "key insight" printed on the image.**
- **A footnote node under a panel**, which is a caption written twice in two places that will drift.
- **A caption baked into the image**, then a second caption in the document.
- **One figure per arm** where a legend would do.
- **A legend key that is a sentence.**
- **A difference plotted with no null, chance line, or error band.**
- **Fixed coordinates in a diagram**, then a silent overlap after a label change.
- **Reviewing the source instead of the render.**
- **A figure whose generator exists only in the conversation.**

---

## Companions
`output-analysis` (which runs to compare, and the latitude / longitude split) · `docs-weekly` (how a
report references a figure and what a placeholder spec contains) · `docs-pptx` (how a figure reaches
a slide: cropping a published one to the panel that carries the argument, rather than redrawing it) · `dataviz` (palette and mark detail for
richer or interactive charts, whose default is a standalone dashboard, so strip its title and caption) ·
`layout-workspace` (where generators live) · `conventions` (family index).
