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
- [House style for result plots](#house-style-for-result-plots)
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

### Style, which is where a figure looks amateur before it is read

| ✗ | why | instead |
|---|---|---|
| **Drop shadows, glows, bevels, gradients** | a slide effect, and it muddies every edge at print size | flat fills, nothing behind the shape |
| **Fill plus stroke plus shadow on the same box** | three ways of saying "this is a box" | pick one: a tinted fill with no stroke, or a stroke with no fill |
| **Mixed capitalization** across labels, axis names and panel titles | the reader reads the inconsistency before the content | one convention for every string in the figure, and the same one in its siblings |
| **The whole equation, transcribed into the image** | the document already displays it, and the two will drift | the symbol alone, `$\mathcal{L}_{\mathrm{OPD}}$`, placed on the thing it scores |

**A comparison is marked, not narrated.** When the figure exists to say *this is compared against
that*, put a marker on each of the two things, a box around them or a bracket beside them, join them
with one line, and label that line with the name of the comparison. A red dashed box around each
compared quantity and a red arrow between them carrying `$\mathcal{L}_{\mathrm{KD}}$` is the whole
idiom. Writing the loss out in full inside the panel is the failure it replaces.

### What never appears inside the image, continued

The trailing-node rule below is the commonest case of a wider one. **An explanatory annotation is a
caption wherever it sits**, not only under a panel. Labels such as `dense credit`, `evidence, before
decoding`, `one decision`, `one state, three operations` and `near-duplicate` all name the reader's
takeaway rather than the object drawn, and all of them belong in the caption. The test is the same:
if deleting it removes no object, no symbol and no quantity, it was prose.

**An illustration sells a concept and a formulation.** It is not text placed in boxes. If the panel
would survive being replaced by a bulleted list of its own labels, it is a list with borders, and the
drawing has not been done yet.

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
| **PowerPoint (python-pptx + soffice)** | a workflow diagram in the numbered-panel style of Jev-Mem (arXiv:2609.23986 fig. 1): large pastel panels with a thin tinted outline and a soft outer shadow, a black numbered circle with a bold title and a grey subtitle per panel, one large Icons8 line glyph per panel and small ones per item, chips inside for the concrete objects, **thin open-headed arrows with italic math between panels**, returns routed beneath the row. An evolution loop takes MemEvolve's diagnose-and-design shape: archive with a Pareto front, diagnose traces to the failed module, propose a patch behind the fixed interface, validate, evaluate, gate | generator in the figure workshop; export to PDF; Icons8 ios7 PNGs via the `id=…&format=png` URL; the red dashed box on the body being rewritten, never on data |

Keep a TikZ figure and its Mermaid twin in sync when both exist, and expect the Mermaid one to be the
lossy version. Emit vector (`pdf`) for LaTeX and a raster preview only for review.

### Geometry, which is where diagrams actually fail

- Fixed coordinates break silently when a label grows. Anchor to node borders
  (`[xshift=4mm]M.north west`) and use `fit` for containers, so a rename cannot produce an overlap.
- **Check the render at print scale, not on the canvas.** A 36 cm canvas set to `\textwidth` prints
  at 0.39x and its 8 pt labels at 3 pt. A blanket font scale on fixed geometry fails, since the text
  grows and the boxes do not. Change the canvas shape instead: two rows print at 0.58x.
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
- **Use a swept head, not a solid triangle.** The default filled triangle reads as heavy at print
  size, and where two of them meet on a short connector the shaft disappears between them. The swept
  head is concave at the back, so it stays legible while taking less ink: `stealth` in OOXML
  (`<a:tailEnd type="stealth" w="med" len="med"/>`), `-{Stealth}` in TikZ, and `arrowstyle='-|>'`
  with a `head_width` set in matplotlib. Reserve the solid `triangle` for the rare case where one
  arrow must outweigh its neighbours, and never mix the two kinds in one figure.
- **Spend space on the connectors, not on empty box interiors.** Oversized boxes with cramped arrows
  between them is the commonest way a diagram becomes unreadable: shrink the boxes to their contents
  and give the gaps to the edges.
- **A label on an edge must clear the edge and both boxes.** Centring a label on a short connector
  hides the connector under the label's own background. Move it beside the line, or shorten the label
  to two characters, or lengthen the edge.
- **One line style per kind of relation, and only one meaning per style.** A connector that says
  "this module is applied here" must not look like a connector that says "the data flows here next".
  Give it its own colour and dash pattern and name the distinction in the panel label.
- **A positioning chart has discrete, named levels on both axes, each axis one kind of thing, and
  every placement checked against the system's own paper before it is drawn.** Use the
  literature's levels: organization `Flat · Indexed · Graph · Hierarchical` (survey
  arXiv:2512.13564 §3.1), design search `Hand-designed · Fixed space · Open-ended` (ADAS
  arXiv:2408.08435). `Flat · Vector · Wiki · Layers` mixed an index, an organization and two
  topologies; `Search one module` collapsed selecting with rewriting. **Audit twice**: the writer
  for the axis design, then `claude -p` with `WebSearch` for each placement, prompt on stdin,
  `--output-format json`, and the instruction that the final message must hold the whole report,
  because text mode returns only the last message and a mid-loop report is lost. The MemDGM
  chart's "empty cell" claim survived the first draft and the writer, and fell to the web check:
  two published systems already sat in it. A search whose result may land in several columns is a
  **span**, drawn to the column its best published result reaches. No vertical offsets inside a
  discrete row. Tint the cell the paper occupies and put the surviving claim, with citations for
  every neighbour, in the caption.
- **No panel title on the drawing.** `(a) Design space` above a panel is the caption's job. The
  panel letter alone, if two panels share a figure.
- **A workflow reads left to right in numbered panels, one concept per panel.** Panel = a stage the
  caption can name (MemArena, Agent, hierarchy; Archive, Diagnose, Propose, Evaluate); inside it, a
  large glyph and chips for the concrete objects (benchmarks, tiers, the program with its slots).
  Between panels, one thin open-headed line with a symbol. Small flat boxes in a bare grammar were
  tried for this author and rejected as weaker: the panels carry the visual weight.
- **An evolution loop is drawn in DGM's own idiom** (arXiv:2505.22954 fig. 1), as three panels
  beneath the task loop: *Archive*, a tree of grey nodes with the selected parent in red and the
  new child in yellow, one verb per edge (`select`, `add`); *Self-modify*, the interface **defined
  as code in a terminal panel** (console glyph, dark ground, keyword in green) and beneath it a UML
  class view of one implementation evolving into the next, `SummaryTier_v3` → `SummaryTier_v4`
  extending it and overriding one verb shown in red, with hollow-triangle generalization heads;
  *Evaluate*, run, gate, accept/reject. Promotion and demotion between adjacent tiers in the task
  loop follow HMO (arXiv:2604.01670 fig. 2). **No annotation sentences anywhere**: the reader
  who wants "select ∝ fitness" reads the caption. Canvas ≤ 21.5 cm so 10 pt labels print ≥ 6.5 pt.
  Pipelines of stages, a bare small-box grammar, and a three-column tree/diff without the task
  loop were each rejected for this figure.
- **On a positioning chart a search system is one point**, in the cell its published system
  occupies; spans across columns were rejected ("still with line span? wtf"). Say in the caption
  what the search may reach.
- **A title emblem has no enclosing ring and a transparent ground.** Generators put the mark in a
  circle and on an off-white square; both show against the page. Crop to the mark and knock the
  near-white out to alpha before embedding.
- **Route every return under or around, never through the gutter a vertical must cross.** Two
  loops on two rows meet at exactly the vertical that connects them; the accept-return and the
  feedback go beneath the lower row on separate lines.
- **A zoom callout is built, not implied.** Shade the source region with a translucent overlay,
  run two hairlines from its bottom corners to the top corners of the magnified box, and fill the
  trapezoid between them with a lighter translucent shade. Draw the shade and the two lines
  *before* the row they cross, so the blocks stay on top of the shade; in a generator that is
  insertion order.
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

- Terse axis labels in sentence case (`Training step`, `Loss`, `Accuracy (%)`), never lowercase.
  Units in the label's parentheses or in the caption, once.
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

**Hue encodes family, weight encodes importance.** The default colour cycle gives every series equal
weight and none of them meaning. Strong reports assign colour by what an arm *is*: the untrained or
plain baseline in neutral grey, each family of competing methods in its own hue with one tint per
member, and the paper's own method in the single accent no other series uses, drawn heaviest. With
two to four series that collapses to grey, one muted hue and the accent. A reader should be able to
find the contribution without reading the legend, and to see which baselines belong together without
reading it either. Keep the assignment fixed across every figure in the document, and match it to any
colour the paper already gives those families in its diagrams, so a run keeps its identity.

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

**Panel letters live in the sub-caption, below the panel and centred, never at the top left.**
Most figures need no sub-captions at all: the caption names panels by position, "Left:",
"Right:", "Top:", "Bottom:". When panels do carry sub-captions, each is a centred line under its
panel in the body face, the way a LaTeX `\subcaption` sits, and then it starts with its letter,
"(a) Methods", "(b) Modules of the harness", so the caption and the text can say "Fig. 3a". The
anti-pattern is the letter as a title at the top left of the axes, "(a) Blind", with the
sub-caption trailing under it or missing: a title reads as part of the plot, the letter has no
caption to belong to, and the figure looks like a notebook export. Panels in a row share a
y-axis and say so by drawing the tick labels once. Panels that do not share a scale must not be
the same size and shape, or the reader will compare them anyway.

**A curve over training looks measured.** It is drawn through the evaluation points, one marker
per evaluation, with the run-to-run noise those points actually carry. A spline through five
checkpoint values, smooth to the eye, reads as invented even when the values are real, and
smoothing that hides the noise hides the very thing that makes a gap credible. Keep the
evaluation cadence visible on the axis: a tick per hundred steps with a minor per fifty, never
three ticks on a five-hundred-step run.

**No text on the data.** The best checkpoint, the peak, the crossing are what the text and the
caption say. A label floating beside a curve competes with the curve, and a second one beside the
next curve turns the panel into a diagram. Name series in a legend, and mark a point with a
marker, not with words.

**Spend the space on the data.** Tight bounding box, no title, no `suptitle`, no padding the document
will add again. Inside the axes, the opposite: keep marks off the spines and labels off the marks.

### Hallmarks of a figure nobody styled

| tell | fix |
|---|---|
| The default blue-orange-green cycle on four series | grey plain baseline, one hue per method family, one accent for the contribution |
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

## House style for result plots

The section above says what a strong figure looks like. This is the concrete specification that
produces one, so a generator can be written against it rather than tuned by eye. It is what the
flagship technical reports converge on, and every value below was chosen for print at the width the
figure is set.

**Size first, then type.** Draw the figure at the width it will occupy: `5.5 in` for an ICLR or
NeurIPS `\textwidth`, `3.25 in` for one column of a two-column venue. Then set type for that size:
tick labels 7 to 7.5 pt, axis labels and panel titles 8 to 8.5 pt, legend 7.5 pt, value labels on bars
6.5 to 7 pt. A figure drawn at 13 in and shrunk into 5.5 in carries 11 pt labels that print at 4.5 pt,
which is the single most common reason a paper's plots look amateur next to its text.

**Face.** The document's face in the generator: `Nimbus Roman` or `Times New Roman` for a Times
template, with `stix` math, `pdf.fonttype 42` so the text stays text.

**Capitalization.** Sentence case for every string: `Training epoch`, `Score`, `Share of pairs (%)`,
panel titles as proper names (`Medical`, `WritingBench`, `Blind`). One convention for the whole
document.

**Lines.** Baselines 1.1 to 1.3 pt, the paper's own method 1.9 to 2.2 pt and drawn last so it sits on
top. The plain baseline is dashed grey. Other baselines are solid. Line style is a second channel for
family only when colour alone would fail in greyscale, never decoration.

**Markers.** When the x-axis has ten points or fewer, every point gets a marker: hollow (white face,
coloured edge) for baselines, filled for the paper's method, 3 to 4 pt. One marker shape per family,
so shape repeats the family that hue already encodes. With dense steps, no markers, and a filled dot
on the endpoint only.

**Bars.** Soft fill (the series colour at about 85 percent opacity, or a light tint of it for
baselines), a darker edge of 0.5 to 0.6 pt, width 0.7 of the slot, and the value printed at the bar's
end in the value's own precision. The paper's bar is the accent at full saturation. Any reference
value, such as the plain baseline, is a thin dashed vertical or horizontal line with its value, not a
bar the reader must compare against by eye. Horizontal bars when the category names are long.

**Legend.** One legend per figure, not one per panel: a single frameless row above the panels
(`fig.legend(..., ncol=n, loc="upper center")`), in the order the arms appear in the results table,
paper's method last. Direct end-of-line labels replace it when there are three series or fewer and
the lines separate.

**Frame and grid.** Left and bottom spines at 0.6 pt in a mid grey, outward ticks 2.5 pt long, three
to five of them at round values, a 0.5 pt light horizontal grid behind the data, nothing else.

**Plot values, not differences.** A panel plots the quantity itself, the score or the share, with
the baseline drawn as its own series or reference line. A panel of `Δ vs base` hides the baseline's
own level, turns every baseline movement into apparent movement of every arm, and makes the reader
reconstruct what the table already reports. Plot a difference only when the reader asked for one, and
then label the axis with the difference's name.

**Trajectories are figures, endpoints are tables.** A per-epoch or per-step trajectory belongs in a
line plot. A table with one column per epoch prints the same curve less legibly, and should be
deleted once the curve exists. The table keeps the endpoint comparison.

**Panels.** Panels in a row share the y-axis (`sharey="row"`) when they measure the same quantity on
comparable scales, so a small gain looks small. Panels that measure different quantities do not.


### What a results figure plots, and what it does not

**Scores are `xx.y` on the axis and in the labels, never `0.xxx` with a "$\times 100$" note.** The
number a reader compares is the one in the table, in the same form.

**Plot the metric the paper is judged on, and say so on the axis.** A results curve shows the
deployment score, the out-of-distribution average when that is what the claims rest on, with
the y-axis labelled as that score. In-domain numbers and every other training-side quantity
stay in the table. The one exception is a figure whose claim is about the training signal
itself, such as the share of response pairs in each failure class over training. That is a
training-set statistic, it is labelled as one, and it is the only kind of figure that shows one.

**A figure whose every number is already in a table is deleted.** Nine panels of per-benchmark
curves beside a table with the same nine columns is the commonest instance, followed by a
bar chart of the ablation table's cells. The figure earns its place by showing something the
table cannot: a trajectory, a distribution, a crossing.

**Track the mechanism, not only the outcome.** When the method claims to move several things,
such as three interfaces and a memory, give each its own panel showing that interface's own
quantity over training, in that interface's colour from the method figure, never an outcome
metric and never a difference. A reader then sees the method act, which no results table can
show, and the panels justify the story rather than decorate it.

**End labels live inside the axes.** Extend the x-limit past the last tick to leave room, rather
than letting a label overhang the axes. An overhanging label grows the saved bounding box, and
`\includegraphics[width=\textwidth]` then shrinks the whole figure, type included, to fit it.

**A legend never covers a value label.** Put the legend over the empty part of the panel. When
the tallest bar is the first one, that means a single column at the upper right and a raised
y-limit, not two columns across the top.

**The palest tint in a family must still read as a line.** A colour chosen as "lighter as
components are removed" fails when the last member vanishes against the grid. Check the palest
member against the grid colour before committing the family, and darken it rather than the grid.

**The training axis is the training step, never the epoch index.** An epoch is a bookkeeping
unit whose length depends on the batch, so a curve over epochs 1 to 5 is five points that cannot
show where a method peaks or how fast it gets there. Plot against steps, sample the curve densely
enough that its derivative is visible, mark each curve's best checkpoint, and let the reader see
the convergence claim: the method that repairs its signal reaches its best at half the budget of
one that does not. Every figure in the document shares this axis, so a share of pairs, a guidance
strength and a score all read against the same abscissa.

**A two-dimensional ablation is not one Cartesian table.** When arms vary along two axes, such as
which interface may move and which modules are present, a table holding every combination reads
as a grid nobody can rank. Give one axis the table, ordered so each restricted arm sits beside the
published method it mirrors, and give the other axis a figure: a slope per setting from the
weakest arm to the full one, with the published counterpart as a reference tick. The numbers then
appear once each, the table holding one dimension and the figure the other.

### Showing one case evolve

A case study is where a method's story is either seen or lost, and a table of visits with a prose
column loses it. The form that reads at once is a **timeline on the training-step axis**, one lane
per thing the method changes, stacked so a reader's eye moves down one moment in time:

- a lane per scalar the method controls, drawn as a step function with its value at each change
  (a sampling weight, a strength, a threshold);
- a lane per set of discrete fields, drawn as bars over the interval each field is mounted
  (guidance fields, active tools);
- a lane of **lifelines**, one per item the method edits (a criterion, a rule, a prompt), each a
  bar spanning the steps it is alive, coloured by the method's own verdict on it at that moment,
  with its parameter printed on the bar and each operation that created, repriced, merged, split
  or deleted it as a distinct mark at the step it happened;
- a bottom lane with the quantity being optimised against the quantity that is actually wanted
  (the group reward against a rubric-free judgement), so the reader sees them separate and
  rejoin.

Vertical hairlines at the moments the method acted tie the lanes together. Item names go on the
left as tick labels, short enough to read at 6 pt, and the legend for verdict colours and
operation marks sits above the whole figure, never inside a lane. No lane carries a sentence: the
lane titles are names ("Guidance fields", "Adaptive criteria"), and the reading is the caption's
and the text's. What the reader gets in one look, and never gets from the table, is the causal
sequence: a field retires when the criteria it targeted change colour, a weight drops when a
lifeline saturates, the reward falls when a bar is raised while quality keeps rising.

### The caption

A caption names what is shown and how to read the marks, and stops. Its shape, taken from the
papers whose figures read fastest:

1. **A noun phrase with the metric and the setting.** "Abstention rate (line, left axis) and SR
   improvement over the base agent (bars, right axis) across task-difficulty bins on WebArena."
   Not a sentence, not a story.
2. **The marks as label: value pairs.** "Dashed: GRPO's best checkpoint." "Bold: best per column.
   Underline: second best." Each one a fragment ending in a full stop.
3. **At most one sentence of reading, for a results figure only.** "Mem-π abstains on easy tasks,
   generates on hard tasks, and improves most where memory is needed." That sentence is the
   figure's claim, in bold in the text; the caption may echo it and nothing more.

Ten to thirty words for a results figure, up to fifty for a method overview, where each panel's
name is followed by what it holds and not by what it shows. What a caption never does: narrate
panel by panel, say why the design produces the result, define the quantities the text already
defined, or say "top row shows" when "Top:" will do. A reader who wants the reading is in the
text; a caption that carries it is read twice and drifts from the text the second time it is
edited. Panel positions are named by "Left:", "Right:", "Top:", "Bottom:", never by letters.

The caption is prose and goes through the writer like every other paragraph.

**Before, 88 words:** "Training dynamics at Qwen3.5-4B on one step axis. Top row: share of
response pairs in each signal class over training, a training-set statistic. Bottom row, left
to right: share of tasks the sampling interface holds at each weight level; mean number of
guidance fields per task against the scheduled ceiling, with the harness without a critic for
contrast; accepted rubric operations per hundred steps by type; and the share of accepted
rubric edits that reverse an edit on the same criterion within the previous two visits to it."

**After, 32 words:** "Training dynamics at Qwen3.5-4B. Top: share of response pairs in each
signal class. Bottom: sampling weight levels, guidance strength against the scheduled ceiling,
accepted rubric operations per hundred steps, and the rubric-edit reversal rate.\"
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
- **The decorative equation.** `E_t = R(q_t, M_t)` and `M_{t+1} = U(M_t, q_t, a_t)` floating under a
  block: symbols the paper never defines, standing in for a mechanism the drawing should show. Draw the
  mechanism (route with its outcomes, supp to the floor, the two reads) and keep only the paper's own
  symbols on the arrows.
- **An explanatory annotation anywhere in the panel**, not only under it. `dense credit`,
  `evidence, before decoding`, `one decision` are captions that wandered into the drawing.
- **Drop shadows and gradients**, which are slide effects that print as mud.
- **Two capitalization conventions in one figure**, usually an uppercase panel title over
  lowercase axis labels, or the reverse.
- **An equation transcribed into a panel** where its symbol would have pointed at the same
  thing and could not drift from the text.
- **A list with borders.** Boxes of text in a row, no structure, no quantity, no flow.
- **A footnote node under a panel**, which is a caption written twice in two places that will drift.
- **A caption baked into the image**, then a second caption in the document.
- **One figure per arm** where a legend would do.
- **A legend key that is a sentence.**
- **A difference plotted with no null, chance line, or error band.**
- **Fixed coordinates in a diagram**, then a silent overlap after a label change.
- **A diagram of diagonals.** Nothing overlaps, and it still reads as scribble.
- **The headless arrow.** The gap is shorter than the arrowhead, so the edge renders as a dot on a
  border and the reader does not see a connection at all.
- **The blunt arrow.** Solid triangles everywhere, so a short connector is all head and no shaft and
  a dense panel turns into a field of black wedges.
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
- **A `Δ vs base` panel** nobody asked for, where the baseline's own level has vanished and every
  line moves when the baseline does.
- **A figure drawn at 13 in and set at 5.5 in**, whose labels print at 4 pt.
- **Lowercase axis labels** beside capitalized panel titles.
- **One legend per panel**, repeated six times across a grid.
- **A per-epoch table** printed beside the curve that already shows it.

---

## Companions
`output-analysis` (which runs to compare, and the latitude / longitude split) · `docs-weekly` (how a
report references a figure and what a placeholder spec contains) · `docs-slides` (how a figure reaches
a slide: cropping a published one to the panel that carries the argument, rather than redrawing it) · `dataviz` (palette and mark detail for
richer or interactive charts, whose default is a standalone dashboard, so strip its title and caption) ·
`docs-table` (the same question for a grid of numbers, and the shared generator) ·
`layout-workspace` (where generators live) · `writing-style-zh` (the prose rules a Chinese figure's
labels obey, and where the one-name-one-object rule lives) · `conventions` (family index).
