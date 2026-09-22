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

## Contents
- [When to Use](#when-to-use)
- [The one rule](#the-one-rule)
- [Diagrams (TikZ · Mermaid · HTML/SVG)](#diagrams-tikz--mermaid--htmlsvg)
- [Data figures (matplotlib)](#data-figures-matplotlib)
- [Looking like a strong technical report](#looking-like-a-strong-technical-report)
- [Reproducibility](#reproducibility)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

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
- **Prefer orthogonal routing, and let the layout earn it.** A diagram full of diagonals reads as
  scribble even when nothing overlaps. Arrange the nodes so every connector is horizontal or vertical:
  down inside a stage, sideways between stages. When a diagonal is unavoidable, it should be a
  deliberate fan-out (one source to two branches), never the default.
- **An arrow needs a visible tail.** If the gap between two node borders is only a little longer than
  the arrowhead, all that renders is a head pressed against a box and the edge reads as absent. Leave
  at least three times the head length between borders, and shorten the path a fraction of a
  millimetre at each end so the head sits beside the border rather than merging into it.
- **Size arrowheads for the room, not for the source file.** A head that looks right at 100% is
  invisible once the figure is scaled to a slide width. Set the head explicitly and check it in the
  render at final size.
- **Spend space on the connectors, not on empty box interiors.** Oversized boxes with cramped arrows
  between them is the commonest way a diagram becomes unreadable: shrink the boxes to their contents
  and give the gaps to the edges.
- **A label on an edge must clear the edge and both boxes.** Centring a label on a short connector
  hides the connector under the label's own background. Move it beside the line, or shorten the label
  to two characters, or lengthen the edge.
- **One line style per kind of relation, and only one meaning per style.** A connector that says
  "this module is applied here" must not look like a connector that says "the data flows here next".
  Give it its own colour and dash pattern and name the distinction in the panel label.
- **Draw the construction, not a paraphrase of it.** If the mechanism is a split, two additive
  couplings and a concat, then draw split, ⊕, ⊕, concat. A box labelled with the mechanism's name
  teaches nothing the caption did not already say. The test: could a reader reimplement the step from
  the picture?
- **Follow the source's own drawing idiom** when the figure explains a published mechanism. Reversible
  networks are drawn as two vertical rails; segment recurrence is drawn as shaded segment blocks with
  a carry arrow between them. Inventing a fresh layout for a well-known picture costs the reader the
  recognition they already had.
- **Do not draw the inverse as a second figure** when the same drawing read backwards is the inverse.
  One diagram plus both sets of equations beats two diagrams the reader must diff.

**CJK-specific traps, both silent:**
- Justification stretches CJK to fill a fixed-width node, so a two-character label renders as
  `注 意 力 块`. Set `align=flush center` (ragged) rather than `align=center` in the shared node style,
  and it is fixed everywhere at once.
- `\par` inside a TikZ node does nothing unless the node has `text width` or an `align` key. A
  three-line label silently collapses to one line, and the source looks correct.

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

## Looking like a strong technical report

The rule above governs what a figure *contains*. This governs what it *looks like*, and the gap
between a competent figure and one that reads as it came out of a strong lab is almost entirely here.
Every item is something the good reports do and the default settings of every plotting library do
not.

**The figure uses the document's font, at the document's size.** This is the single loudest tell. A
panel set in DejaVu Sans, dropped into a paper set in Times or Palatino, reads as pasted in no matter
how good the data is. Name the document's face in the generator, or export `pgf` and let LaTeX set
the text. Then size the figure to the width it will occupy, and never let `\includegraphics` scale
it: a figure drawn at 6 in and included at `0.7\textwidth` has 7 pt labels claiming to be 10 pt, and
two such figures at different scales have visibly different type.

**One hue, plus grey, plus one accent.** The default colour cycle gives every series equal weight and
none of them meaning. Strong reports desaturate: baselines and reference curves are grey, the
paper's own arm is the one saturated colour on the page, and a second hue appears only when a second
distinction genuinely exists. A reader should be able to find the contribution without reading the
legend. Keep that assignment fixed across every figure in the document, so a run keeps its identity.

**Remove the frame, keep two spines.** A full box around the axes is a library default, not a
choice. Left and bottom spines in a mid grey, a hairline horizontal grid behind the data on the value
axis only, and nothing else. Ticks point outward, are short, and there are three to five of them at
round values.

**Label the lines, not a legend box.** A legend makes the reader match a colour to a name and carry
it back to the curve. A name set at the end of its own line, in that line's colour, removes the trip
entirely, and it is what the reports do whenever the lines separate at the right edge. Keep a legend
only when the curves cross or bunch.

**Let the data set the limits.** An axis running 0 to 40 for data that lives in 10 to 34 spends a
third of the panel on nothing, and the differences the figure exists to show shrink accordingly.
Pad the data range slightly and stop. The exception is a bar chart, whose baseline must be zero or
the bars lie about their ratios.

**Annotate the claim.** The peak, the crossing point, the endpoint gap: mark the one place the text
points at, with a dot and its value or a short arrow. A figure where every point is equally
unmarked makes the reader find the result; a figure with one marked point hands it over.

**Panels are lettered, aligned, and share their scales.** `(a)`, `(b)` in bold at the top left,
outside the axes. Panels in a row share a y-axis and say so by drawing the tick labels once. Panels
that do not share a scale must not be the same size and shape, or the reader will compare them
anyway.

**Spend the space on the data.** Tight bounding box, no title, no `suptitle`, no padding the document
will add again. Inside the axes, the opposite: keep marks off the spines and labels off the marks.

### Hallmarks of a figure nobody styled

| tell | fix |
|---|---|
| The default blue-orange-green cycle on four series | one hue in tints, grey baselines, one accent for the contribution |
| A legend box floating over the data | direct labels at the line ends |
| A full box around the axes, ticks on all four sides | two spines, outward ticks |
| A dense grid in both directions | hairline horizontal grid, behind the data |
| Font visibly different from the body text | the document's face, or `pgf` output |
| Two figures on facing pages at different type sizes | draw each at the width it is included at, never scale |
| `0.0, 0.1, ... 1.0` on an axis whose data spans 0.42 to 0.70 | limits from the data, plus a little padding |
| A title inside the image | the caption |
| Value labels absent from a bar chart | print the value above each bar and drop the y-axis |
| A rainbow heatmap | sequential for magnitudes, diverging only when zero means something |


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
- **A diagram of diagonals.** Nothing overlaps, and it still reads as scribble.
- **The headless arrow.** The gap is shorter than the arrowhead, so the edge renders as a dot on a
  border and the reader does not see a connection at all.
- **Big boxes, starved arrows.** Half the panel is empty box interior while the connectors have no
  room to be seen.
- **A connector crossing a box it has nothing to do with**, which reads as a relation that does not
  exist.
- **Reviewing the source instead of the render.**
- **A figure whose generator exists only in the conversation.**
- **The library's default palette**, which gives four series equal weight and the reader no way
  to find the contribution.
- **A figure scaled by `\includegraphics`**, so its type size no longer matches its neighbour's.
- **An axis padded to a round number** far outside the data, shrinking the difference the figure
  exists to show.

---

## Companions
`output-analysis` (which runs to compare, and the latitude / longitude split) · `docs-weekly` (how a
report references a figure and what a placeholder spec contains) · `docs-slides` (how a figure reaches
a slide: cropping a published one to the panel that carries the argument, rather than redrawing it) · `dataviz` (palette and mark detail for
richer or interactive charts, whose default is a standalone dashboard, so strip its title and caption) ·
`docs-table` (the same question for a grid of numbers, and the shared generator) ·
`layout-workspace` (where generators live) · `writing-style-zh` (the prose rules a Chinese figure's
labels obey, and where the one-name-one-object rule lives) · `conventions` (family index).
