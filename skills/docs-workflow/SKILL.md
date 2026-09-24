---
name: docs-workflow
description: "Build a paper's workflow or architecture figure, and small concept illustrations, as a python-pptx drawing in the accepted MemDGM Fig 2 idiom: aligned panel grid, Icons8 Fluency icon plus concept word, code-editor windows with syntax highlighting and a code-review diff, a zoom band into a framed loop, one type scale, measured text, orthogonal arrows."
when_to_use: "Use when drawing a system overview, a workflow with a feedback loop, a zoom-in onto one component, a code or interface panel inside a figure, or a small concept illustration that replaces a paragraph of method prose."
---
# Skill: docs-workflow

## Purpose
This is the drawing idiom the author signed off on for the MemDGM paper's Fig 2 (2026-09-23/24),
after a dozen rejected versions. It owns **how a workflow figure is laid out and drawn**: the grid,
the icons, the code panels, the zoom, the arrows, the type scale, and the checks that keep all of
it aligned. `docs-figure` still owns what a figure may contain (no annotation sentences, no
baked captions); `drawing-gemini` owns generated images; `pptx` owns decks.

The reference drawings are in `resources/examples/`, the generators that produced them in
`resources/templates/`, and every icon they use in `resources/icons/` with its Icons8 id in
`MANIFEST.md`. Start from a template, not from a blank slide.

## Contents
- [When to Use](#when-to-use)
- [The pipeline](#the-pipeline)
- [Layout: a grid, not a collage](#layout-a-grid-not-a-collage)
- [Type scale and print size](#type-scale-and-print-size)
- [Icon plus concept word](#icon-plus-concept-word)
- [Retrieving icons](#retrieving-icons) (labels: see Icon plus concept word)
- [Arrows and lines](#arrows-and-lines)
- [Colour carries one meaning](#colour-carries-one-meaning)
- [The code-editor window](#the-code-editor-window)
- [The zoom into a loop](#the-zoom-into-a-loop)
- [Showing a query-dependent path](#showing-a-query-dependent-path)
- [Concept mini-figures](#concept-mini-figures)
- [Checks that must pass](#checks-that-must-pass)
- [The caption](#the-caption)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- A system overview with a task loop on top and an improvement loop (search, training, evolution)
  beneath it, where the lower row is a closer look at one component of the upper row.
- Any figure that must show an interface or a rewrite as code rather than as boxes.
- A small illustration of one concept (two ways to spend an item, a search space as a grid) that
  lets a method section drop a paragraph.

## The pipeline
```sh
T=$CPFS_HOME/.claude/skills/docs-workflow/resources/templates
cp $T/figlib.py $T/fig2_build.py src/            # the full figure; figlib for small ones
python3 src/fig2_build.py                        # writes out/<name>.pptx, prints OVERFLOW lines
cd out && soffice --headless --convert-to pdf <name>.pptx
python3 -c "import pymupdf; p=pymupdf.open('<name>.pdf')[0]; p.get_pixmap(dpi=300).save('<name>_300.png')"
```
python-pptx places every shape in centimetres (`E(v)` converts), LibreOffice renders the PDF the
paper includes, and PyMuPDF renders PNGs to inspect. Arial renders as Liberation Sans and Courier
New as Liberation Mono, which are metric-compatible, so what you measure is what prints. Keep the
generator beside the figure in the paper's figure workshop and copy only the PDF into the repo.

## Layout: a grid, not a collage
- **Columns align across rows.** In Fig 2 the top row is MemArena | Task Agent | MemDGM and the
  bottom row Evaluate | Archive | Self-modify, with identical x-ranges (0.6-5.1, 5.8-10.1,
  10.8-20.0 on a 20.3 cm canvas). Every cross-row relation then becomes a straight vertical, and
  the eye reads the two rows as one table.
- **Gutters hold exactly one arrow.** 0.7 cm between panels: enough for an arrow and its one-glyph
  label (`q`, `a`, `C`, `KV`), not enough to invite a sentence.
- **Compact interiors.** Content starts 0.15 to 0.2 cm inside a panel border; the author rejected
  "big boxes, small arrows" on sight. Chips span the panel's inner width; rows sit 0.1 to 0.2 cm apart.
- **Titles in one place.** Every panel: icon 0.55 cm at (x+0.2, y+0.14), title 12.5 pt bold at
  x+0.85. The zoomed row gets a frame with its own title in the loop colour.
- **Row 2 as offsets.** Write lower-row coordinates as `r2(v) = Y2 + v`, so tightening row 1 moves
  everything below with one edit.
- **Receiving edges sit 0.4 cm inside their panel**, so an arrowhead never lands on a panel border.
- **Align the rows an arrow joins.** Choose the y of each horizontal flow first (the query lane,
  the answer row, each port row), then place the chips at both ends on that y. In Fig 2: query lane
  1.41, answer 2.15, latent port 2.40, text port 5.10.

## Type scale and print size
- The canvas is 20.3 cm wide and prints at 13.97 cm (0.69x). One scale everywhere: panel titles
  12.5 pt bold, body **and edge labels** 10.5 pt, code 9 pt, benchmark chips 9.5 pt at the
  smallest. That prints at 8.6 / 7.2 / 6.2 / 6.5 pt. Nothing below 6 pt in print.
- Edge labels are the same size as body text and bold in the arrow's colour. Tiny grey arrow labels
  were the author's first complaint.
- Math letters are Times/Liberation Serif italic at 12 pt (the x-height of 10.5 pt Arial). Script
  letters (𝒱, 𝒜, 𝒟, 𝒥) and ⋆ come from FreeSerif, the only installed face that has them.
- **Never use a baseline-shifted run for a subscript**: LibreOffice renders it at 58 percent, which
  prints near 3 pt. Draw the subscript as its own 9 pt text box offset 0.13 cm down (`sub_lbl`).
- A concept mini-figure is drawn at **true print size** (13.97 cm or half of it), with 7.5 to 9 pt text.

## Icon plus concept word
Every concept on the drawing is an icon followed by its word, the EvoTrainer (arXiv 2606.03108)
pattern: a gavel and "Judge", a bullseye and "Accuracy", a stopwatch and "Latency", a stethoscope
and "diagnosis", a pencil and "rewriter". The icon is 0.4 to 0.55 cm beside 10.5 pt text. The same
concept reuses the same icon everywhere it recurs (the metric icons in MemArena and again in
Evaluate), which links the two places without a line. A symbol-only label (`F`, `score(a, gold)`)
was rejected: name the concept.

### Labels live in one table, and come from the literature
Every concept word on the drawing is an entry of one `LBL` dict at the top of the generator, so a
terminology change is one edit, and the same words appear in the paper's text and captions. Take
the words from the representative papers the figure's own related work cites, not from the
implementation: MemDGM's first labels (`verbatim floor`, `kv-assoc`, `NL port`, `ledger`,
`contract`, `rewriter`, `genome`) were replaced after a literature sweep by `Raw`, `KV memory`,
`Text injection`, `rejection log`, `validity check`, `meta agent`, `architecture` (Zep, MemGPT,
RAPTOR, MemOS, DGM, HyperAgents, AutoMem). Code shown in an editor window follows the same names
(`class Layer`, `score(q, scope)`, `src(x)`).

## Retrieving icons
- One family: **Icons8 Fluency** (colourful flat, soft gradients). Search with the Icons8 MCP tool
  `search_icons(query, platform='fluency')`, then download the permanent PNG:
  `curl -sL -o name.png "https://img.icons8.com/?id=<ID>&format=png&size=256"`. Check it is an
  RGBA PNG (PIL), not an HTML page. Append a line to `MANIFEST.md` (concept, file, name, id, url,
  glyph).
- Recolour an icon to carry a semantic colour by keeping alpha and luminance and replacing hue
  (`latent_purple.png` is `latent_interface.png` moved to the latent purple #7B5EA7).
- An agent icon must not repeat the author's other papers (Mem-Pi and HarnessRL use robot heads);
  the sparkle assistant `task_agent.png` is the accepted one.
- `resources/icons/` holds all 43 icons used so far. Prefer reusing them over fetching new ones,
  so figures across a paper share one visual vocabulary.

## Arrows and lines
- Orthogonal only. Diagonals appear once, as the dashed edge of a zoom band.
- One weight for flow arrows (1.25 pt), one for structure (1.0 pt), heads `arrow`/`med` at the end.
  Draw a multi-segment path as segments with the head on the last one (`path`).
- A tail is at least three head lengths (0.4 cm) long, or the arrow reads as a dot on a border.
- A loop return is the one heavier, longer line: it leaves the last stage, runs in a lane below the
  frame, and re-enters the first stage from the side, with its label (`child g′`, icon beside it)
  under the lane.
- No crossing. If two flows must cross, move a panel, not the line. The query lane in Fig 2 runs
  above every panel's content so the returning ports never meet it.
- A tree is drawn as an org chart: parent, vertical stub, horizontal bus, vertical drops. The new
  child's stem is dashed in the loop colour.

## Colour carries one meaning
Panels take a pastel fill each (arena blue EAF1FA, agent cream FFF6E6, memory lilac EFEBF8,
evaluate peach FDEEE7, archive green E6F3EA, self-modify F8F5FD) with a 1 pt near-black border.
Lines take one colour per kind of flow and keep it everywhere: query lane and route actions blue
0550AE, text port 2E6E8E, latent port 7B5EA7, the improvement loop terracotta B4472F, promote
2E8B57, demote grey 7C8794. The selected element (the layer being evolved, the active file tab) is
marked by a **dashed terracotta border**, the same mark in both places.

## The code-editor window
The part of Fig 2 the author praised most. Reproduce it exactly (`editor()` in `fig2_build.py`):
- Window: fill F6F8FA, border D0D7DE 1 pt, radius small. Header 0.46 cm, fill EAEEF2, with three
  traffic-light dots (FF5F57, FEBC2E, 28C840, r 0.075 cm) at x+0.22 step 0.24, then a 0.3 cm
  terminal icon, then the file name in 9 pt bold Courier.
- A tag chip at the header's right (FFF3C4 fill, D4A72C border, 0.36 cm tall) says `fixed` for the
  interface file. Several files become **tabs**: layer icon plus name, the active tab white with the
  dashed terracotta border.
- Code in 9 pt Courier New, line height 0.36 cm, GitHub-light colours from a tiny tokenizer
  (`code_runs`): keywords CF222E bold, function names 8250DF, types 953800, constants and numbers
  0550AE, comments 6E7781 italic, text 1F2328.
- Write the interface as real code: an `Action = ...` alias, `class Tier(Interface):`, then
  `# in-layer` and `# cross-layer` sections with signatures in words (`score(q, focus)`, not
  `score(q, F)`), then the contract as comments.
- **A rewrite is a code-review diff**: context lines plain, removed lines on FFEBE9 with a red `-`,
  added lines on DAFBE1 with a green `+`, the sign in its own 0.25 cm column. Draw every band
  first, then every line of text, or a band clips the descenders of the line above.
- Size an editor as `0.5 + n * 0.36 + 0.14` cm for n lines.

## The zoom into a loop
- The lower row is a closer look at one upper panel. Draw a pale band (F2EFFA) as a polygon from
  that panel's bottom edge to the top edge of a frame around the whole lower row, **behind**
  everything, with one dashed edge on the slanted side. The panels drawn on top hide the band
  inside themselves, so it shows only in the gutter.
- A band that starts at an inner element (one layer bar) and fans to a wider row must cross the
  neighbours; start it at the panel edge instead, and mark the element with the dashed border.
- Do not add a magnifier icon on the band; the band already says zoom.
- Inside the zoom, name the element again (the active tab `summary`) so the link is explicit.

## Showing a query-dependent path
The core motivation of an adaptive memory is that depth depends on the query, so draw two queries:
one lane carries `q` from the benchmark through the agent into the memory, where it forks into
`q1`, which stops at a coarse layer, and `q2`, which narrows on a hit and stops at the floor.
The route actions are icons on the path (a funnel for Narrow, a stop sign for Stop, the continuing
arrow for Descend) with a three-entry key beneath. The same lane also drops into any side store the
query reaches (the latent layers), so every memory part is visibly addressed by the query. Outputs
return to the agent on their own rows, one per port, below the lane.

## Concept mini-figures
A paragraph that explains two ways of doing one thing becomes a two-panel figure at text width and
3.5 cm tall (`fig_channels.py`): the same object in both panels, the path that differs coloured,
the consequence in a chip (`μ(G) unchanged` / `μ(G) raised`), an accept or reject mark at the
reader. A search space becomes a grid (`fig_genome.py`): rows are components with their icons,
columns the editable slots grouped by header bands, one cell shown overridden and one switch
flipped, a two-line key. Place a grid as a `wrapfigure` at half width beside the paragraph it
replaces.

## Checks that must pass
1. **Measure every label.** `width_cm()` measures runs with the Liberation fonts through PIL, and
   `text()` records any box its text overflows. The build prints `OVERFLOW` lines; zero is the
   target, 0.05 cm is tolerable.
2. **Strip `p:style` from every shape** (`nostyle`), or LibreOffice draws the theme's soft drop
   shadow under everything.
3. **Render at 300 dpi and read it in four quadrants**, then place it on its paper page and read it
   at print scale.
4. **Adversarial critique.** Three critics (compliance with the author's requests, geometry,
   semantics against the method text), each finding verified against the render before it is
   applied. Most useful catches: arrowheads on borders, a label on its own arrow, a symbol that
   differs from the paper's macro, a drawn concept the text never defines.

## The caption
Narrate the workflow in running order, `Illustration of the X workflow.` then the top loop from
the first stage to the answer, then the lower loop from selection to admission, with the paper's
symbols, and nothing that is not on the drawing. See `writing-paper`, Captions.

## Rules
1. Start from `resources/templates/`, never from a blank slide.
2. One grid: columns aligned across rows, 0.7 cm gutters, content 0.15 to 0.2 cm inside borders.
3. One type scale; edge labels as large as body text; nothing under 6 pt in print; real subscripts.
4. Icon plus concept word for every concept, one Fluency family, reused across the figure.
5. Orthogonal arrows, tails of at least 0.4 cm, heads 0.4 cm inside the receiving panel, no crossings.
6. One colour per kind of flow, held across figures in the paper.
7. Interfaces and rewrites as code windows, never as boxes with verbs.
8. The zoom is a band behind the panels into a framed row, with no magnifier.
9. Measure, strip shadows, render, crop, critique, then ship.

## Anti-patterns
- Numbered circles, tinted-outline panels, a dark terminal block, UML boxes for code.
- Annotation sentences on the drawing (`select ∝ fitness`, `in-layer: admit index score`).
- A chip repeated per row (`NL | Latent` on every layer); name the port once where it is used.
- Symbols as concepts (`F`, `score(a, gold)`, `Ω₅` when the paper never defines Ω).
- Double rules or decorations with no meaning (a double line under the floor layer).
- A magnifier on a zoom band; a zoom band crossing neighbour panels.
- An arrow that starts and ends on nothing, a spine next to the layers that no query enters.
- Subscripts by baseline shift, text boxes narrower than their text, edge labels smaller than body.

## Companions
`docs-figure` (what a figure may contain; the chart idiom) · `docs-table` · `pptx` (deck
building) · `drawing-gemini` (generated emblems) · `writing-paper` (captions) · `icons8` MCP
(`search_icons`, `get_icon_png_url`).
