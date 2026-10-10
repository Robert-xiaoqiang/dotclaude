---
name: docs-slides
description: "Build a talk deck as a compiled artifact, from a plain-text source rendered to several backends or from a self-contained Beamer project per talk, so it can be linted, timed against its slot, cited from one bibliography and rebuilt a year later. Covers the storyline of a talk about your own works, the per-work page pattern and its summary-page title formula, short and long versions, an external job talk versus an internal defense, titles and page chrome, where each slide figure comes from (crop, rebuild from the paper's source, or redraw) and its measured text floor, build gates, pptx export, and the confirmative register of a pitch deck."
when_to_use: "Use when producing slides for a talk, seminar, reading group, job talk or defense, when one deck ships as PowerPoint and PDF, when a deck must be cut to a slot or re-cut for another audience, when a talk lists papers one by one with no main line, when titles report results or carry an enumerator, when figure text is unreadable from the room, when text ran off a slide nobody looked at, or when a proposal deck hedges its own results."
---
# Skill: docs-slides

## Purpose
Produce a slide deck the way a paper is produced: **compile plain-text sources into artifacts** and look
at every rendered page before anyone else does, so the deck can be linted, timed, cited from one
bibliography and rebuilt. This skill owns the deck as a build product, a talk's storyline and page
patterns, and a slide's visual discipline; not a figure's content (`drawing-figure`), the python-pptx
idiom (`drawing-workflow`), a paper's tables (`writing-table`) or the prose (`writing-style`,
`writing-style-zh`).

## Contents
- [When to Use](#when-to-use)
- [Two kinds of backend, and what lint means in each](#two-kinds-of-backend-and-what-lint-means-in-each)
- [The build loop](#the-build-loop)
- [What belongs in the source](#what-belongs-in-the-source)
- [One directory per talk](#one-directory-per-talk)
- [The storyline of a talk about your own works](#the-storyline-of-a-talk-about-your-own-works)
- [A section needs an entry before it needs content](#a-section-needs-an-entry-before-it-needs-content)
- [The per-work page pattern](#the-per-work-page-pattern)
- [Short and long versions, and the time budget](#short-and-long-versions-and-the-time-budget)
- [Re-cutting a deck for another audience](#re-cutting-a-deck-for-another-audience)
- [Cover, self-introduction and closing](#cover-self-introduction-and-closing)
- [The arc of a reading-group or survey talk](#the-arc-of-a-reading-group-or-survey-talk)
- [Titles](#titles)
- [Style: what a slide looks like](#style-what-a-slide-looks-like)
- [Page chrome: header, logos, navigation](#page-chrome-header-logos-navigation)
- [What to remove](#what-to-remove)
- [What to preserve](#what-to-preserve)
- [Examples on a slide](#examples-on-a-slide)
- [Page layout: figure, bullets and columns](#page-layout-figure-bullets-and-columns)
- [Figures: crop, rebuild from source, or redraw](#figures-crop-rebuild-from-source-or-redraw)
- [What a slide figure shows](#what-a-slide-figure-shows)
- [Tables and charts on a slide](#tables-and-charts-on-a-slide)
- [Citations, footers and the reading-group cover](#citations-footers-and-the-reading-group-cover)
- [Speaker notes are the script](#speaker-notes-are-the-script)
- [Verifying the numbers before they reach a slide](#verifying-the-numbers-before-they-reach-a-slide)
- [The register of a pitch deck](#the-register-of-a-pitch-deck)
- [A .pptx the compiler did not build](#a-pptx-the-compiler-did-not-build)
- [Exporting a LaTeX deck and sharing its source](#exporting-a-latex-deck-and-sharing-its-source)
- [Beamer traps that render silently wrong](#beamer-traps-that-render-silently-wrong)
- [The gates a deck build must have](#the-gates-a-deck-build-must-have)
- [Reviewing before delivery](#reviewing-before-delivery)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Building slides for a talk, seminar, reading group, job talk or defense, especially one with a fixed
  slot.
- A talk about several of your own works that needs one storyline instead of a list of papers.
- Cutting a long deck to a short slot, or re-cutting an internal deck for an external audience.
- Shipping the same deck as PowerPoint for a co-author and as a PDF for a venue or a room.
- Setting up a Beamer project that holds several talks and compiles on Overleaf.
- Generating slides from code, from a results table, or from research notes.
- Stripping back a deck that has grown dense, or restructuring one whose argument changed.
- Text ran off the bottom of a slide, figure labels were unreadable from the room, or a talk written
  for thirty minutes ran forty.

**Not for**: what a figure may contain or which plotting pipeline draws it, which is `drawing-figure`,
nor the python-pptx workflow-figure idiom, which is `drawing-workflow`. Not for a paper's table
formatting (`writing-table`), the prose rules the slide text and notes obey (`writing-style`,
`writing-style-zh`), or a CV, even though a self-introduction page copies from one (`docs-resume`). Not
for the research that fills the deck, and not for posters or papers.

## Two kinds of backend, and what lint means in each

Two source forms are in use. A **cc2slides** markdown deck is the compiled form's reference
implementation; it is not on PyPI, so install it from its repository with `pip install git+<repository
URL>`. A **hand-written Beamer project** is one directory per talk. The rules hold for both, and where a
section names one form it says so. The skill was called docs-pptx while there was one backend; the format
argument that used to open it is settled and lives in the cc2slides README.

One source, several targets, and the targets are not equivalent. Record the kind, because the whole
review procedure turns on it.

| kind | consumes | examples | overflow lint |
|---|---|---|---|
| **geometric** | placed rectangles, colours resolved | pptx, html preview | describes the output exactly |
| **semantic** | the document IR, typesetting delegated | beamer | does **not** describe the output |

A geometric backend paints where the layout engine said, which is what lets one preview be a faithful
picture of another artifact and what lets the linter reason about overflow before either is written.

A semantic backend hands typesetting to something with its own opinions. LaTeX does its own line
breaking, float placement and vertical glue, and fighting those to honour a pre-computed rectangle
produces worse output than letting it work. The cost is that **overflow lint does not describe the
Beamer output**, because the layout the linter measured is not the layout that gets rendered. A
linter that reports geometry findings against a semantic backend is lying politely; downgrade them
to informational and say so.

So the review procedure differs. For a geometric target, look at the contact sheet. For a semantic
target, **rasterise the PDF and look at that**, and check separately for the failure modes LaTeX has
and the geometry engine does not: overfull boxes, and content typeset into a fixed strip that neither
shrinks nor clips. A hand-written Beamer project is a semantic target with no geometric preview at
all, so its gates read the log and the rendered PDF ([The gates a deck build must have](#the-gates-a-deck-build-must-have)).

## The build loop

Build, read the findings, **look at the slides**, fix, repeat. Do not skip the looking.

```bash
cc2slides build deck.md              # pptx + html preview; EXITS 1 on an error finding
cc2slides build deck.md -b beamer    # a LaTeX PDF, and its .tex beside it
cc2slides shots deck.md              # one PNG per slide plus a contact sheet
cc2slides outline deck.md            # slide list with a running clock, for pacing
cc2slides script deck.md             # the standalone speaker script, page by page
cc2slides backends                   # which targets this machine can produce
cc2slides figures                    # which diagram engines are usable here
cc2slides new talks/my-talk          # scaffold a deck that already builds
```

A Beamer project runs the same loop through its own `scripts/build.sh` (xelatex, then the gates), and
renders pages for review with a script beside the gates.

**The repository carries the agent's operating manual.** A `CLAUDE.md` at the root of the deck tooling
or the talk project, written for the agent rather than a human reader: the build command, what to do
about each finding, and the instruction to look at the pages. cc2slides ships one. The agent that builds
the next deck starts without this session, and the manual is the first thing it reads.

The linter catches geometry. It cannot catch a slide that is correct and dead, a figure that fits its
box but is too small to read, a caption that repeats the script, or a section with three slides where
it needed one. Only looking catches those.

**Check geometry numerically as well as visually.** Reading placed rectangles out of the build is
cheap and catches what the eye misses: content off the slide, content overlapping content, columns
whose tops disagree, and whitespace above a body that does not match the whitespace below it. For a
semantic target, read the PDF's text blocks and flag any page whose ink reaches the paper edge.

## What belongs in the source

For a cc2slides deck: one markdown file per deck, with the front matter carrying what the build needs:
title, author, date, theme, slide size, **the declared slot length**, the spoken rate, and the
bibliography path. Slides split on a rule at column zero; per-slide options go in a comment. A Beamer
project states the slot and the page count in the header comment of its main file.

Fenced containers carry what markdown cannot express: columns, callouts, case panels, timelines,
speaker notes, and diagram blocks for TikZ and Mermaid. A diagram block inherits the deck palette, so
colour names are already defined inside it and should be used rather than hardcoded hex.

Theme leaves are overridable from the front matter (`theme_overrides:` down to `type: table:`),
which is how a dense deck buys larger table type without forking the theme. And a grouped results
table sets its families as a **bold label on the group's first row** with blank continuation cells,
never as full-width category header rows: every table row costs its text height plus a fixed
0.18 in of padding, so six category rows spend a bullet's worth of height each saying nothing. Two
results tables built that way measured 124% and 116% of their boxes after shrinking to 80%, and fit
at full size the moment the categories moved into a column.

## One directory per talk

A project that holds several talks (a defense, a short and a long job talk, a reading group) is laid
out so that no talk can change another.

**Each talk is a self-contained directory, and its main file is named after it.**

```
<talk>/
  <talk>.tex          main file: the root probe, then \input preamble and sections
  preamble.tex        layout, palette, footer band, corner marks, navigation macros
  sections/           one file per section; page-level design notes as comments at the top
  figures/            TikZ, one file per figure, logos, template material
  assets/             cropped paper figures and generated PDFs/PNGs
  figure-workshop/    the builders behind assets/ (see Figures below)
  scripts/
    build.sh          xelatex, then every gate, with their exit codes
    checks/           the gates and the page renderer
    figures/          matplotlib generators writing into assets/
    pptx/             the .pptx exporter, run on its own
  pdf/<talk>.pdf      the built deck
```

No file is `\input` across talk directories; reuse is a copy. Recorded: a flat root with
`deck-short.tex` and `deck-dense.tex` sharing one preamble meant that editing the new talk silently
changed the talk already given, and `deck.tex` in five editor tabs named nothing. The same section held
in three directories is the cost of this rule, not an oversight.

**Every script resolves the talk root from its own location** (`$BASH_SOURCE` in shell, `__file__` in
Python), never from the working directory, so it gives the same result wherever it is called. Loose
utilities at the project root broke as soon as they were called from somewhere else. Helper scripts go
under `scripts/` with a README, never flat at the root.

**Each talk compiles from its own directory and from the project root.** Overleaf may or may not `cd`
into the talk before compiling. Probe for the preamble, set a prefix and `\input@path` so every
`\input` in the sections stays relative, and stop with an error that names the cause when neither path
finds it, because the silent version surfaces forty lines later as unrelated missing-file errors:

```latex
% !TeX program = xelatex
\makeatletter
\newcommand{\troot}{}
\IfFileExists{preamble.tex}{}{%
  \renewcommand{\troot}{<talk>/}%
  \IfFileExists{\troot preamble.tex}{}{%
    \GenericError{}{preamble.tex not found}{}{The talk directory was probably renamed.
      Rename it back to <talk>, or change the prefix in this file.}}}
\edef\input@path{{\troot}}
\makeatother
\input{preamble.tex}
```

**Pin the engine and select the Main document.** `% !TeX program = xelatex` heads every main file,
since CJK text goes through fontspec. On Overleaf, Menu → Main document must name this talk's file: a
deleted `main.tex` that is still selected compiles nothing and reports "0 errors" with no PDF, which
reads as a broken build.

**Freeze before a restructure, and keep parallel attempts side by side.** Copy the talk directory to a
sibling with a descriptive suffix (`<talk>__50pages`, `<talk>__final`) before a large change. Parallel
attempts by different agents live as `<talk>__codex` and `<talk>__claude`, a retired attempt is
renamed `<talk>__legacy` rather than deleted, and nobody edits another's directory. When another
version's typesetting is better, copy its source wholesale and iterate on it: re-drawing an imitation
came out worse every time.

**The Overleaf mirror carries sources only.** Sources, vector figure PDFs and small icon PNGs go in.
Gitignore the exported `.pptx` (about seven times the PDF and different on every export), `build/`,
reference decks and fonts. After pulling Overleaf's "Update on Overleaf" commits, restore the
executable bits it strips from `scripts/` (it turns `100755` into `100644`). The git-bridge token goes
through a credential helper, never into the remote URL. Pushing follows `git-push`: only when asked.

**Retire a one-way sync script the moment anyone edits its target.** A script that mirrors staging
directories into the Overleaf clone by deleting and rebuilding each talk becomes destructive once
someone edits the clone directly: one more run rebuilds every talk from stale copies. From then on the
clone is the single source, and the script is changed to exit immediately with a message saying where
to edit, not left runnable.

## The storyline of a talk about your own works

**One main line, named by the speaker, with every work as exactly one stop on it.** The line is a
capability, a scale or a loop that grows stage by stage. Check it against the outline: each entry is a
stop on that named progression, no section is titled by time period, employer or venue (`past work`,
`internship work`), and no work sits beside the line as a side branch. Decks that stacked papers one
by one, or split the body into history and internship, were rejected as having no story, and a work
presented beside the line read as a side branch: it has to be strung onto it.

**Not a taxonomy grid.** A two-axis grid (when the method acts × what capability it adds) as the
research overview is a classification, not a thread. If any paper of the era would fit some cell, the
grid says nothing about this speaker's line. The author asked for such a grid, then rejected it for
exactly that reason; replace it with a progression figure that orders the works.

**Open the research part with two pages.**
1. A *why* page for the topic, built as a contrast: without versus with. A light human analogy may
   inspire it, never stand in as an equivalence.
2. A page placing the topic in the speaker's research: one left-to-right progression of same-family
   cards, each with one small icon from a single icon family, a one-line motivation question and the
   method names. It organises the works; it is not a publication list. Venues appear as plain text at
   most, never as venue logos, and there are no paragraphs. Abstract circles, big colour blocks and
   venue logos were each tried and removed.

Each later stage page repeats one small check-mark table that shows what this stage adds over the one
before it ([progressive figure](#what-a-slide-figure-shows)), so the audience reads the progression on
every page instead of remembering it from the overview.

**Deck order:** cover, self-introduction, the research overview (the why page, then the progression
page), then the outline as the first work's transition, the works, closing, and the appendix. Add a
neutral outline page only where it does not sit next to a transition outline: two identical outline pages
rendered back to back, and the neutral one was commented out of all three shipped decks. (An earlier
instruction put the outline right after the cover; this order superseded it.) The outline is a vertical
list with no tagline under it (a `主线：…` line was called filler), and it is reused before every section
as the transition, with the current entry highlighted. Never use a full-colour section divider page; the
highlighted outline replaced it. Each outline entry reads
`<stage>：MethodX <one phrase on what it does>`, the same phrase the work's summary page uses, so the
two never drift.

**The appendix.** Pages taken out of the body go after the closing, numbered on their own (`附录 N`),
and appear in neither the outline nor the navigation bar. The appendix divider carries its name and
nothing else; a blurb listing what the appendix holds was deleted as pointless. An external job talk
drops the appendix stack entirely, with the files kept and not `\input`.

## A section needs an entry before it needs content

A deck that jumps from one project into the next leaves the room reconstructing why this slide follows
that one. Every section opens the same way and in this order: **where it sits** (the outline again,
current section highlighted), **the problem it solves** stated as a difficulty, **one concrete case**
as evidence, then the mechanism. Opening on the case is the common inversion: the audience meets an
example before they know what it is an example of. In a talk about your own works this entry takes the
fixed shape of [the per-work page pattern](#the-per-work-page-pattern).

**Enumerate a section's threads once, in bullets, not in titles.** When a section has several
difficulties, name them on one overview page as bullets (`优化挑战`, `工程挑战一`, `工程挑战二`) and in
the outline; the pages that answer them keep plain noun-phrase titles. This is a correction. An earlier
version of this skill said to carry the label in every answering page's title, which followed an
instruction the author gave and then reversed two rounds later, deleting every such label from the
titles and keeping it only as bullet and outline structure. See [Titles](#titles).

**A slide's settings belong on the settings slide.** Backbone, LoRA rank, epochs, GPU hours, the data
source per domain and the judge are experimental setup, not method. Left on a method or analysis slide
they read as clutter; gathered once on one setup slide beside the data and the baselines they are what a
committee actually wants. Step and epoch counts stay off analysis pages.

## The per-work page pattern

In a talk about several of your own works, **every work is the same sequence**, so the audience learns
the shape once:

1. the outline with this work highlighted, as its transition;
2. a one-page **summary**, written for the committee or for leadership;
3. one to three **body** pages (method, results) in the short version, the work the audience cares
   about most getting the most, with detail pages after them in the long version. The author asked for
   two or three pages per work, then added a page to one work for its training objective.

Body pages do not restate the background, challenge or motivation the summary already gave; that
repetition was cut every time it appeared.

**The summary page title is the one place a title states the contribution.** Its formula is
`MethodX：通过<核心机制>，[解决<问题>，]提高<收益>`: one 通过, at most one 解决, one 提高, and no further
clause naming a sub-symptom. It is abstract enough for a leader outside the subfield and may wrap to two
lines. Specific, jargon-heavy titles were rejected as written for the wrong reader, and the author then
dictated this shape ("通过xxx，解决xxx，提高效率/泛化"); what he deleted later was an extra clause naming a
sub-symptom, not the 解决 slot. Every other page keeps a noun-phrase title ([Titles](#titles)).

**The summary page body is a single column of three labelled blocks**, with no sub-bullets and no
second column. It is the one text-only page besides the outline, a takeaway and a settings page, and it
follows this shape rather than the bullet count of other pages:

- **问题背景**, one paragraph a non-specialist can follow: the object, then the difficulty, then why the
  existing approach falls short, then what this work changes. It describes no method.
- **核心方法**, one paragraph: the modeling choice, then the named key mechanism and the storyline
  concept it instantiates, then what that makes possible.
- **主要结果**, two or three lines: performance (one headline benchmark and the margin over the best
  prior), efficiency only when efficiency is a claim of the work, and acceptance status. The author
  deleted the efficiency line from two summary pages, and cut a second and third benchmark to keep
  only the headline one.

Every fact and number on it comes from the work's own body pages and is stated in one place. A
two-column version and a result list of four benchmarks were replaced in the third round. The skeleton
that was accepted:

```
MethodX：通过可逆的参数化记忆，提高跨任务长期记忆的泛化与召回效率
问题背景  随着 X 持续增长，主流做法 Y 面临 A 与 B 两项代价。这项工作把 X 从 Y 转向 Z，
          Z 的核心难点是 W。
核心方法  MethodX 把<写入>与<读取>建模为一对互逆过程，用<结构>保证可逆，只训练<组件>，
          并加入<损失>约束<性质>。
主要结果  性能：<benchmark> 上 <指标> 为 N，最强基线 M
          效率：<规模> 增长时 <开销> 基本不变，<基线> 增至 K 倍
          录用：<venue year>
```

Earlier drafts opened on colloquial scene-setting and listed implementation limits; what landed states
the paradigm shift and then its one core challenge.

**Build a method up from the simplest baseline, one step per page:** the standard pipeline on a concrete
instance; the alternative paradigm and exactly where it differs (how the store is built versus how it is
accessed); the challenge; the motivation; then the method. Keep the motivation to two bullets and the
challenges to two or three. When a trick needs justifying, derive its necessity from the trivial case
(identity, then a general map, then the trick) before showing it. Pages that opened on the method, or
listed five challenges and four motivations, were rejected; the page-by-page build-up was later named as
exactly the wanted style.

**Name the problem in the field's own words.** State it with the established phenomenon names (reward
hacking, overthinking) on one classic example, name and cite the current mainstream paradigm, call prior
work "the current mainstream" and never "the only way", and describe its gap accurately as what it does
not model. Self-coined symptom descriptions and "only X can" claims were rejected as inaccurate.

**One related-work page before the method.** Group prior work by which component it changes ("route A
changes X, solving P; route B changes Y, solving Q"), name each route's exemplars, and end with the gap
that motivates the method (the uncovered component, the missing unified view). Beside it, a figure shows
where each route intervenes in the pipeline. Say what a route solves, not what it is "aimed at". Without
this page the unified view had no motivation. The exemplars are names, not citations: a `代表工作`
column or phrase gives each by its method name, with venue and year where they fit, the full entries go
on the references page or in the appendix, and the footer keeps the work's own identity
([Citations](#citations-footers-and-the-reading-group-cover)).

**A method with several components gets one overview page, then one page per component in one layout.**
The overview is the whole loop in one figure (outer versus inner process, data flow). Each component
page has a goal row spanning the top, inputs on the left, outputs on the right, then one worked update on
the shared example; what a second call adds is marked inside the same frame, not on a new page. One
shape lets the audience learn it once; component pages in prose or in three different shapes were
rejected.

**A spec page for an LLM component (evolver, judge, router).** The goal sits in a full-width band on top,
written like a system instruction. Inputs go in the left column and outputs in the right. Each field is
its literal English name in angle brackets followed by a one-line definition, nested fields indented,
outputs defined once. Name action levels after the literature in a `Layer | Operation | Description |
Example` table; for rubric edits, for instance, Revise (Reword, Reweight), Restructure (Split, Merge),
Curate (Create, Filter, Delete). Chinese field names, several fields merged into one slash-separated tag,
a process narrated where field definitions belonged, and ad hoc level names (light, medium, heavy) were
each rejected.

**A transition page between two works when the second extends the first.** Title it
`MethodA 到 MethodB：<维度一>与<维度二>` and contrast the two left and right along those two named
dimensions (training objective, fidelity → utility; injection, always-on → adaptive). The second work
then does not re-introduce what the first already established, which it did before this page existed.

**Results pages.** The first results page is a table with methods grouped by family and separated by
midrules (no external control / single component / joint), so the taxonomy arrives with the numbers;
every baseline the bullets mention has a row. Efficiency against quality is a plot, not a latency table.
Beside each result go one or two findings with sub-bullets, never a summary sentence opening the page.
Ablations are split by the question each answers, one figure per question. Table and chart details are
in [Tables and charts on a slide](#tables-and-charts-on-a-slide).

## Short and long versions, and the time budget

**Build the long version first, and richly**: about ten pages per main work (pipeline, contrast,
challenge, mechanism step by step, data construction, results, a case). A conservative first version
left every work vague. Then derive the short version. **The long version is a superset of the short one,
in the same order**: it keeps every short-version page, each summary page included, and appends detail
pages after each work.

**Compress by reusing, not by re-authoring.** Carry the long version's figures, examples and wording
verbatim into the short one, and gain space by merging pages, shrinking figures, smaller body type and
tighter spacing. Never re-author an approved page from scratch, and never compress an example into a
fragment. Re-drafted short pages lost the style the author had approved, and the instruction was to
carry the original material into the new structure.

**Budget pages against the slot.** About one content page per minute; outline and transition pages cost
one or two seconds and stay even in the shortest version, so a 15-minute slot holds about 20 pages and a
20-minute slot about 25. Each work gets one to three body pages after its transition and summary (method,
then one or two results), the work the audience cares about most getting the most. If the slot is still
overrun, **drop whole works** (transition, summary, body and the outline entry) rather than thinning
every work: squeezing all of them left none of them clear. Take a page out by commenting its `\input` or
its frame with a one-line reason and the exact restore step, because the author removes and restores
whole works as the slot changes.

## Re-cutting a deck for another audience

**Re-cut, do not relabel.** Copy the talk to a sibling directory for the new audience, then grep the copy
for every audience-specific term and remove it: the internal event's name (defense, internship report,
review), team names, internal product names and nicknames, business validation, and a next-step plan
aimed at the old team. Recorded: an external copy of an internal defense kept the defense's sections and
wording, and the author had to ask why. The research is the same; the listener is not.
(`writing-style-zh` owns the general rule that an internal report's structure and words stay out of an
external document.)

| | internal defense or review | external job talk |
|---|---|---|
| cover title | the event's title | the speaker's name |
| work done for a team | may be its own section | merged into the research storyline |
| appendix | after the closing, numbered on its own | dropped, files kept |
| closing | written for the team (below) | one trend insight figure (below) |

## Cover, self-introduction and closing

**Cover.** Centred horizontally and vertically, no left-aligned block. In order: the title (the event's
title for an internal talk, the speaker's name for an external one); a rule; the speaker's name, on an
internal talk only, because on an external talk the name is the title and is not repeated as a byline
(the author asked for the name as the title and no separate talk title); the affiliation in full (in a
Chinese deck the full Chinese name with the short name); the program and expected graduation for a
student; the full date including the day. One fact per line, no interpunct or slash between fields. An
English byline is the name, then `MM/DD/YYYY`. Left-aligned covers, month-only dates, centre-dot bylines
and title-plus-name covers on a job talk were each corrected. A reading-group cover is different: see
[Citations](#citations-footers-and-the-reading-group-cover).

**Self-introduction.** A left-to-right timeline of equal-size boxes with institution logos and an
unlabelled arrow (no "time" on it), each box one degree or role with its major and one research-direction
phrase. Below it, two aligned blocks side by side: research output in one line (N papers, M
first-author, venues with ×N counts, plus one line for a major survey contribution) and honors as aligned
rows. No CV research-statement line, no interpuncts, generous spacing left and right. Unequal boxes, a
labelled arrow, a CV-style statement line and dot-separated honors were each removed, and the result was
then frozen as perfect.

**Facts restated from the CV are copied, not paraphrased.** An honors row reads award, institution, date,
amount, exactly as the CV has it, and the publication line uses the CV's counts. Update the deck and the
CV together whenever either changes; counts had drifted between them (`docs-resume` owns the CV side).

**Closing of an external job talk: one insight figure that shows a trend** across rounds (what grows,
what shrinks, what carries over from one round to the next), with three short bullets and the thank-you
on the same page. Not two axes drawn from an origin, which read as flat with no visible trend, and not a
product or business pipeline, which is an internal defense's story.

**Closing of an internal defense: written for the team, not for the speaker's ambitions.** Learnings
(a change of methodology, a shift of interest) as a small figure plus short lines; the next plan as one
line tied to the team's business (`A + B`, not a bullet list); a simplified version of the storyline
figure; strengths at the level HR reads (independence, speed backed by one piece of evidence), never
project details; acknowledgments on the same page. Each block is at most two short plain sentences:
bulleted reflections read as AI-written, and long closing text was cut in each of four rounds. Delete
template placeholder sections (`困惑与求助（待填）`) and any section with nothing to say.

## The arc of a reading-group or survey talk

Open on the field's current direction, backed by current data: what the newest frontier releases
report. Then why that direction is hard, the target task and today's scope, and a timeline. Then go deep
on **one or two anchor papers instead of many**: motivation, contributions, data collection, the
pipeline expanded stage by stage, a gold trace or task case, the evaluation protocol (what is compared
with what, process versus outcome), an excerpt of the results table, insights, and two concrete cases per
taxonomy class. Close with a two-to-three-bullet takeaway, a comparison table over the main dimensions,
and an outlook with a personal view. Cut good sections that are off the story. A breadth-first deck with
a generic agent-introduction section, stale figures and one-line takeaways was rebuilt around this arc.

**A figure of a fast-moving field's state includes the current frontier.** If its newest data point
predates the talk by more than a few months (a capability-horizon chart that stops at a model two
generations old), replace it with current data or drop it. Such a chart was rejected as legacy.

## Titles

**What a title does depends on the register, and the two registers want opposite things.** Getting this
backwards is the most visible way a deck reads wrong, because the title is the largest text on every
page.

- **A pitch, proposal or ideation deck**: titles are **short claims** under about 46 characters, stating
  the finding. The room is being persuaded once, in order, and will not look anything up.
  Equation-shaped titles are good where they fit: `Agent = Model + Scaffold + Harness` says more than
  "An agent is a model, a scaffold, and the harness that runs them" and fits on one line. See
  [The register of a pitch deck](#the-register-of-a-pitch-deck).
- **A research talk, defense or technical review**: titles are **noun phrases or concepts naming the
  object and which facet of it the page covers**: `参数化记忆的优化目标与不可靠根源`,
  `MethodX：训练目标与注入策略`, `主要结果`, `样例分析`, `核心动机`. The audience navigates, looks up
  mid-talk, and keeps the deck as a reference, so the title's job is to say where you are. A plain
  concept title beats a rigid one that tries to pack the page into the title; the author said a title can
  simply be a concept.

**The failure is writing pitch titles into a research deck**, and it is easy because claim titles feel
sharper in isolation. Recorded: a 30-page defense deck came back with every title rewritten as a finding
(`GSM8K 上与 CoT 持平，收益落在 26 步降到 2 步的效率一侧`, `MethodX：域内 F₁ 从 38 到 53，替换记忆模块后四项指标领先`)
against a 49-page deck by the same author whose titles were all nominal. The author's verdict was that
the short version's titles were "全都是瞎写". Two costs beyond register: a claim title spends the finding
before the evidence is on screen, so the body has nothing left to deliver, and every page competing to
announce a result flattens the ones that carry a real result.

In a research deck, a title is none of these:

- **A subject-verb sentence or a reported result**, even one dressed as a noun phrase. When the point is
  a mechanism, name it: `通过加性耦合实现可逆`.
- **A question.** `怎么…`, `…是什么`, `为什么…` hand the reader a question instead of a place.
- **A number.** `38 到 53`, `37.9%`, `862 token` belong in the bullet under the figure that shows them.
- **An enumerator or a back-reference.** `优化挑战`, `工程挑战一`, `问题 1`, `上一页`, `那一条` stay out of
  titles. Enumerators live in the bullets of the overview page and in the outline (see
  [A section needs an entry](#a-section-needs-an-entry-before-it-needs-content) for why this reversed).
- **A metaphor**, or a self-coined name for something the field already names.

**The colon test**: delete everything before the colon. If what remains only restates the deleted half,
the title is empty. The per-work summary page is the one exception to "no claim in a title"
([its formula](#the-per-work-page-pattern)).

**Titles in an English deck are in Title Case**, short, cover title included:
`Evaluation Methodology for Autonomous Research Agents`. This is a correction: this skill used to say
sentence case for pitch titles, and the author asked for Title Case on every page title and on the cover
of an English deck.

**Consecutive slides on one topic share a title verbatim**, and sibling pages that walk through stages
share one title frame (`单任务的…`, `跨任务的…`, `整个学习过程的…`). Three slides that all develop one
argument tell the room they are still in it; a new claim per continuation slide fragments it. A title
that wraps eats a line of body, in either register; only the summary page may take two lines.

**Table and result-block headings are plain category nouns**: `主要结果`, `样例分析`, `分类统计`,
`汇总统计`. A descriptive heading carrying the model name, the epoch count or `九格合计 100` was renamed
each time; that setup goes on the settings line, which says what is trained, on which data, scored by
which judge.

**Pane labels are noun phrases.** `Anatomy`, `Gold`, `Trajectory`, `Failure`, `Condition`. Never "What
counts as gold", "What happened", "What must be true". A label names its column; it does not ask the
audience a question the speaker is about to answer.

## Style: what a slide looks like

**One left edge per column.** Body text, table cells and callout content must line up. Cells padded on
all four sides put the first column a fraction right of everything else in the same block, which is
small enough to look accidental and large enough to see. Give the outer cell edges no padding, and do
not indent a callout that already has a rule and a coloured label.

**The body is centred in its box by one rule with no threshold in it.** Centring only below some fill
fraction, or only partway, is a discontinuity: with the title and its rule pinned at a fixed height,
the body lands at one height on one slide and a different one on the next, and clicking through reads
as the page wobbling under a fixed heading.

**A column is never narrower than its own longest word.** Proportional-to-content alone lets a narrow
column beside a wide one fall under a single word, and the renderer then breaks that word across
lines.

**Bullets: three to five first-level items per page, each a bold key phrase, a colon and one claim.**
Mechanisms, formulas, baseline names and numbers go into second-level bullets one size smaller. Two or
more parallel items under one head become sub-bullets, not a run-on line. (`writing-style-zh` owns
one-claim-per-bullet for prose; this is its slide shape.)

**A Chinese bullet ends bare.** No terminal punctuation, and no `。` inside it; clauses join with `，` or
`；`. Labels, table cells and short definition lines (`一条记录记作 m_{t,i}`) end bare too. The English
semicolon ban in `writing-style` does not carry over: the author proposes `；` for Chinese bullets.
Bullets ending in `。` and full stops mid-bullet were flagged until a gate failed on them. The summary
page's two paragraphs are prose and keep their full stops.

**No line wraps onto a second line by a few characters.** Shorten the wording, widen the box, or shrink
that one element a step so each bullet, criterion or list line fits on one line, and check it on the
render, not the source. A third criterion wrapping by two characters was flagged three times.

**Small, tight body type; even, modest gaps between blocks; spare room goes to the figure or the
example.** First-level bullets about 7 to 8.5 pt, the second level one step smaller, tight item spacing,
boxes that hug their text with about 1 mm of inner padding, and the gaps between blocks even rather than
large. Each page must still carry enough information; a short version puts more on each page, not more
pages. The author asked for a look that is "高级，正式，且美观" (polished, formal and good-looking) and
rejected "大字，大间隔，大留白" (big type, big gaps, big whitespace), then asked for the body type to go
smaller still.

**Distribute free space instead of parking it.** Two columns sit a normal gutter apart, never a third of
the page; stacked figures and formula rows sit close; the body is balanced between the title rule and
the footer. With spare room, enlarge the figure or add the example; without it, shrink the body a step
rather than keep big type, big gaps and big margins. Repeated elements (timeline boxes, logo cells,
cards, labels under icons) are the same size and share a baseline or centre line.

**Colour: grey scale by default, colour only for a category or a single highlight.**
- One muted hue per category, the same hue on every page, in figure, table, chart and text tag alike.
  Adjacent categories must be distinguishable on the render; change one hue if two look alike.
- One brand accent, taken from the speaker's institution rather than the theme's default blue.
- Coloured fills belong to diagram nodes only. Text blocks are bullets, and example panels are grey or
  transparent.
- Red means "look here": the optimisation target, a screenshot region, the one cell under discussion.
- No full-bleed coloured pages, and no narrow coloured edge bars on callouts or cards, which read as
  AI-made.

Many coloured boxes and bright category colours were called messy and lacking a formal look ("if it can
be black and white, make it black and white").

**Emphasis marks and quotations.** On a screenshot, mark the region with a red rectangle and red
numbered circles, because black frames vanish against UI chrome. Inside a table or field list, a thin
red frame points at the single entry being discussed. In text, bold the decisive span. A motivation
page may carry an epigraph: one short quoted claim from the literature in its original language, small
italic, with the source (authors, venue, year) right-aligned on its own line. It makes a motivation
intuitive without the speaker's own slogan.

## Page chrome: header, logos, navigation

**The header.** The frame title sits vertically centred in its band above a full-width rule. A brand
mark in the top-right corner sits on the title's visual centre line, on one line, smaller than the title
and still clearly readable, and clears the title and the rule by at least about 1 mm. **The gap from the
title rule to the first ink under it is about 1.2 to 4 mm on a 16:9 page, measured in the PDF**, not
judged by eye. Beamer adds about 5 mm under the frametitle template on its own, so every page gets a
blank band under the rule; take it back once in the template with a negative skip, never page by page.
A deck measured 6.9 mm under the rule on every page before that fix. Short rules, titles drifting
upward, and a brand mark too small, then too large, then too high were each corrected over many rounds.

**Logos in one row are equalised by optical weight, not by file height.** Enlarge marks with small
glyphs, shrink heavy ones, and align all of them on one centre line with the text beside them. Two minor
affiliations may stack vertically inside the footprint of one major logo, within a fixed corner budget.
A text label beside an icon aligns to the icon's vertical middle. When an organisation was renamed, crop
the legacy part of its mark or replace it with the current name as text. One logo too large, another too
small, two misaligned and a legacy name on every page were each flagged.

**An organisation's slide template is a read-only reference.** Copy its brand elements (the corner mark,
the title rule, the colours) into your own preamble and never edit the template file. Ignore its
data-policy and page-limit pages for a personal talk, replace its default font when a more formal one
reads better, and do not copy decorative lines such as coloured text above every title. A rebuild that
ignored the template's corner mark was questioned; editing the template was forbidden.

**A navigation bar on every page but the cover.** One line of hyperlinks (outline, each work, closing)
with the current section highlighted, every target frame labelled so each link resolves, and a gate that
counts the links on every page of the PDF. It exists so the presenter can jump between sections during
questions.

**The footer band is drawn only when it has content.** What it holds is in
[Citations, footers and the reading-group cover](#citations-footers-and-the-reading-group-cover); cover,
outline, self-introduction and overview pages carry none, and a band drawn on them read as chrome.

## What to remove

The governing principle, shared with `drawing-figure`: **the slide carries structure and quantity, the
script carries claim and explanation.** Anything in small type that explains rather than names is dead
weight, because the speaker is already saying it.

- **Figure captions that are sentences.** Delete outright, leaving a bare figure. A caption survives
  only if it is a bare name or a bare quantity that appears nowhere else on the slide.
- **Meta notes, where the slide comments on itself.** A notation disclaimer (`本页省略样本下标`), the
  provenance of a count (`计数取自…预跑`), what the appendix holds, a kicker above a paragraph, a
  legend sentence (`柱为…，线为…`), a colour key (`红色虚线：…`), and a takeaway the author did not write
  (`验证了 X 应联合建模`). Each was deleted by the author, usually with "the speaker says that"; they keep
  coming back because each looks locally helpful. If notation needs a disclaimer, fix the notation.
- **Editorial callout labels.** "Read a result as a triple", "What the recipe bought", "Why this one
  matters". Delete the label and often the whole block.
- **Column headings that editorialise**, and every "What x" / "How x" / "Why x" label.
- **The section that opens on a case.** The room meets an example before it knows what the example is
  an example of, and spends the next two slides catching up.
- **The inherited number.** It survived three revisions because nobody asked where it came from, and
  it is not in the paper.
- **Bar heights read off a plot and stated as the paper's numbers.**
- **The full-then-short citation.** Correct in a paper, an inconsistency in a deck, where slides are
  seen one at a time.
- **Settings stranded on a method slide.** The committee wants them next to the data and the
  baselines, and the method slide wants the space.
- **The four-name object.** hint / 短提示 / 提示 m / 经验 for one thing, across one deck.
- **Pitch titles in a research deck**, and enumerators in research titles ([Titles](#titles)).
- **The two-headed pane.** A left-right split with a small-text heading banding each side. Use
  hierarchical bullets on one side and a figure or a table on the other.
- **Chrome the author did not write.** A kicker, a heading over a list that is obviously a list, a
  corporate source named three times because `name`, `authors_display` and `affiliation` all say the
  same thing.
- **Trailing prose under a table or figure.** It is a caption in disguise, parked where the caption
  goes.
- **Restatements.** If the script reads the axes out loud, the caption must not. If the slide states
  the number, the script should not read the table back. If the summary page gave the background, the
  body page does not.
- **Provenance hedges on your own numbers.** "Mock", "forged", "projected", "illustrative", "not yet
  run", "runs queued". A pitch deck claims in the confirmative; see
  [The register of a pitch deck](#the-register-of-a-pitch-deck).
- **Interpuncts and slashes as separators**, anywhere on a slide or inside a figure, in either
  language: `·`, `\cdot`, `／` and `/` between two fields. `writing-style-zh` owns the rule and its
  reason for Chinese text (both render oversized beside CJK glyphs); on a deck it also covers figure
  labels, bylines and English slides, where in a generated markdown script a `·` reads as a bullet. Use a
  comma, a colon, parentheses, a line break or a bullet, stack a byline one fact per line, and gate it
  with a grep over the sources that skips commented lines and allows an unspaced interpunct inside a
  transliterated name.
- **An appendix blurb**, the divider that lists what the appendix contains.
- **Template placeholders** (`待填`) and any section with nothing to say.
- **A page that is only a figure.** Add two or three bullets stating the claim the figure is there to
  make.
- **A page that is only bullets**, unless it is an outline, a takeaway, an experimental setting, or a
  work's summary page, which has its own three-block shape
  ([the per-work page pattern](#the-per-work-page-pattern)).

## What to preserve

Stripping is not the goal; legibility is. These earn their place and should survive the pass.

- **Source attribution.** A label like "Its own docstring" or "From the paper" over a quotation is
  attribution, not editorialising. Without it the quote reads as the speaker's own verdict.
- **Bare quantities.** A caption of "1,642 traces" or "207-day doubling" is data, not explanation,
  when the number is nowhere else on the slide.
- **The paper's own figure**, cropped to the panel the slide argues about, when it reads at slide size
  ([the ladder](#figures-crop-rebuild-from-source-or-redraw)).
- **Numbers in tables.** Prose belongs in the script; a number belongs in a cell where it is visibly
  attached to its row.
- **The qualifier on every score.** Model, harness, subset, effort setting, pass@k. A benchmark number
  without them is not reproducible and the audience cannot check it.
- **The caveat a cited source printed against itself.** A judge-dependent headline, a confidence
  interval a factor of ten wide, a countervailing signal the authors published anyway. Keeping these
  is what makes the rest credible: attribution of a source's own doubt, not a hedge on your own
  rows, which the pitch register bans.
- **Approved pages.** A page the author has approved is frozen: a deck-wide restyle skips it
  ([Reviewing before delivery](#reviewing-before-delivery)).

## Examples on a slide

**An example is real and complete.** Data quoted from a source (a benchmark prompt, a rollout, rubric
text) appears in its original language first, then the translation (the order `writing-style-zh` sets for
any quotation); two or three actual outputs; the per-criterion scores aligned directly under them; only
then one line of analysis. A constructed teaching example in a Chinese deck is written in Chinese, with
no original to quote ("例子需要中文，或者只用中文"). A passage is five to ten sentences, not a clause, and long
examples are broken into structured lines. A hierarchy slide that shows a four-sentence passage at the
document level and one clause at the sentence level shows the hierarchy; truncating every level to a
fragment shows nothing. **Never attribute or analyse ("this pair is spurious") without the data on the
slide**: analysis without the rollouts, one-clause examples and translation-only quotes were each
rejected ("你得给 rollout，才能说打分").

**Background for a broad audience is an instance, not a list of labels.** Show input, output and data on
one concrete instance (real text, a question and its answer, a GUI trace) drawn into the figure and
annotated beside it. A page of abstract labels (`输入：… 标准输出：… 核心问题：…`), or an abstract flow
with no content, is not background; it was called useless twice. A committee is broad peers, not
specialists in the subfield.

**Lay out an example panel this way:**
- The source tag (benchmark and task type) as a plain meta line above the panel, not inside it.
- For quoted source data, original-language text first and translation after it; bold the decisive
  span.
- A grey or transparent background, never a saturated fill.
- Each criterion or list line on one line, shrinking a step or widening the box rather than leaving two
  words on a second line.
- A one-to-many structure drawn as a tree.
- The same example, verbatim, on consecutive pages that discuss one case, annotated in place.

The in-place annotated example was the most praised page of one deck.

**When shortening a deck, never compress the example.** Merge pages or shrink the frame, and keep the
example's type size.

**A constructed example must not prove itself.** An intervention that restates the criterion it is then
scored on makes the improvement trivially true; one such guidance example paraphrased its own criterion
and was rejected. Write the intervention as the method actually produces it (a critique of the current
output plus a reference for a better one), then show the output before and after and each one's score on
each criterion.

## Page layout: figure, bullets and columns

**Choose the layout by content.** A flow or structure figure goes full width on top, bullets below it.
Only data figures and tables use a side-by-side split, and then the two columns sit close together with
no wide gutter. When a figure needs part-by-part explanation, interleave bullet, figure, bullet, figure
instead of writing the explanation inside the figure. Wide gutters and explanation inside figures were
each rejected; the interleaved layout was specified by the author.

**A figure page pairs the figure with one to three bullets that state its claim.** Hierarchical bullets
on one side and the figure or table on the other, never two panes each headed by a small-type label. In
a stacked layout, keep the line under the diagram to one short line: two CJK bullets wrap to five or six
lines and shrink the diagram to half the slide. When the figure dominates, shrink it or swap the sides
rather than cut the bullets.

**Pick the layout from the aspect ratio, not the reverse.** Compute it before writing the slide. Forcing
a tall figure into full width centres it, shrinks it to the box height and wastes half the slide. If a
figure slide overflows, lower the figure's width before cutting text.

## Figures: crop, rebuild from source, or redraw

**Choose each slide figure's source by this ladder, and name the choice in the figure file's header:**

1. **Crop the paper's vector figure** to the panel the slide argues about, but only if its smallest label
   lands at or above the deck's figure-text floor at the placed size.
2. **Rebuild from the paper's editable source** when the crop lands below the floor and the paper keeps
   one (a python-pptx generator, a `.pptx`, a TikZ file): rebuild that panel at slide size, printed 1:1,
   keeping the paper's strings, numbers and icons.
3. **Redraw in deck style only a teaching figure that must show less than the paper's**: a baseline
   pipeline before the method, one half of a two-part figure, the one mechanism the slide explains. Go
   back to the paper's own figure as soon as a redraw is less clear than the original.
4. **Re-plot a results table as a chart** only from that table's own numbers.

This is a correction of the old rule, which said to prefer the paper's figure and treated any redraw as
an anti-pattern. The instruction changed three times: first simplify and redraw, because paper figures
carry too much for a slide; then put the original back, because the redraws were messier and lacked the
original's wholeness; finally rebuild from the papers' own pptx sources. Crops of column-width figures
measured 4 to 5.6 pt on a slide, and several redraws were less clear than what they replaced.

**Take the vector original** from the e-print tarball where there is one; the HTML build ships a
downsampled raster that turns to mush on a projector.

**A published multi-panel figure is cropped to the panel that carries the argument**, and the crop is
four fractions of the source. Where the same figure serves several slides, crop it differently for
each. When a figure must appear at thumbnail size, crop it first and check it still reads.

**Vendor benchmark tables ship as images.** Several labs render their comparison tables as PNGs, so
scraping the page text returns prose and no numbers. Fetch the image from the CDN and read it.

**A PDF figure never reaches a geometric slide directly.** The geometric backend places images through
PIL, which does not open PDFs, so vector sources are rasterised to PNG by a generator script kept beside
the deck (about 2,600 px wide, white margins trimmed), because a standalone built as a full page
otherwise lands as a small drawing in a sea of white that the layout then dutifully scales down.

**Keep every generated or rebuilt figure's builder in a figure workshop beside the deck.**
`figure-workshop/` holds `src/` (generator scripts that read the paper repository read-only), `icons/`
with its `MANIFEST.md` (`drawing-icons`), `out/` (the `.pptx`, the PDF and a 300-dpi PNG preview of each
figure) and `out/superseded/` for replaced drafts. The deck reads only `figures/` and `assets/`; an
explicit `--install` step copies an output into `assets/`, and only after its preview has been looked
at. The workshop README has one table with the columns `slide figure | file the deck includes | built
by | read-only source`. Without it a figure cannot be rebuilt, traced to its paper source, or compared
with the draft it replaced, and a one-off conversion done in a chat leaves nothing behind.

**Figure text has a floor, and it is measured on the render.** Author every figure at its placed size,
or compute the landed size as authored pt times the scale factor. Then gate on the rendered PDF: every
text span inside a figure must be at or above the floor. Excuse a super- or subscript only when a
full-size neighbour sits within about 10 pt of it, and exclude the citation band. Reference floors:

| page | floor |
|---|---|
| Beamer 16:9, 160 mm wide | 5.6 pt |
| PowerPoint 16:9, 13.33 in wide | about 12 pt (the same physical size) |
| python-pptx figure printed at 14.5 cm | 7 pt text, 6.6 pt code |

The last row is stricter than `drawing-workflow`'s paper type scale, which prints code at 6.2 pt and
allows anything at or above 6 pt. A figure rebuilt for a slide therefore raises that scale until code
prints at 6.6 pt or more and text at 7 pt or more; a figure built to the paper scale fails this gate.

Set nominal sizes a little above the floor, because LibreOffice rounds to 0.1 pt and stores 1/100 mm, so
6.5 pt prints as 6.49. A `\resizebox` can turn a 9 pt label into 3 pt while nothing in the source looks
wrong and nothing overflows; only the measurement catches it. Letters too small to read were the most
repeated figure complaint.

**Size figure text and boxes together.** Text one step below body size, symbols and letters about as
large as the body; boxes hug it with about 1 mm of inner padding, never zero and never mostly empty
interior; the space freed goes to arrow length and gutters. When a figure looks cramped, shrink the type
one step and widen the gutters before enlarging any box. Never abbreviate a label to make it fit; tighten
the spacing instead. Feedback ran both ways (padding to the minimum, then the text too big for its box,
then smaller text with more room to the border), and each time the fix was box size and padding, checked
numerically. `drawing-figure` owns the general version: spend space on connectors, not box interiors.

## What a slide figure shows

`drawing-figure` owns what any figure may contain and its geometry: no sentence inside the image,
orthogonal connectors with tails of three head lengths, swept heads sized for the room, one line style
per kind of relation, the source paper's own drawing idiom, and the construction drawn rather than
paraphrased. `drawing-workflow` owns the python-pptx idiom. This section is what a slide adds or
tightens.

**No narration, with one exception.** On top of `drawing-figure`'s ban, a slide figure carries no
provenance (`redrawn from the paper's numbers`), no legend written as a sentence (`red dashed =
directions prior work never trained`), no corner label repeating what the box, the adjacent table or the
bullets already say, and no label on a back-edge whose target box already names it. An explanation the
audience needs goes into a bullet beside the figure or into the script. The one annotation allowed is a
short gloss attached to a specific span of a concrete example. Across three decks the author kept
deleting in-figure explanations ("that is what you say out loud"); the one annotation praised marked up
spans of a real example.

**A flowchart is modules plus data flow.** Modules in boxes; data objects as short letter names on the
arrows (q query, c context, a answer); the input and the output at the two ends; the loop drawn if the
process has one. An arrow label is a symbol or at most three words. An operation (an inverse map, a
compression step) gets its own box, not a label on an arrow, and each loss term labels the arrow it
supervises. The optimisation target is the one red element, and the module that replaces the previous
paradigm is framed so the audience sees what is being replaced. A column of text boxes holding sentences
is not a flowchart: "a flowchart is not text turned into a picture; it is the loop, the core modules and
the data flow, with short labels on the arrows."

```
rejected  [history docs / long dialogues, reports, web pages] -> [chunking and vectorising /
          chunk -> embedding -> vector DB] -> [keeps text and index] -> [top-k retrieval /
          by similarity] -> [task model answers / query + retrieved text]
accepted  three named stages (knowledge-base creation, retrieval and QA, knowledge-base update);
          q, the retrieved c and a on the arrows; the concrete question and answer drawn on the
          chart; a lookup that visits the store and comes back; a dashed arrow with an ellipsis for
          accumulation over time feeding the update stage; one arrow style within a stage and
          another between stages
```

**Concrete instances go inside the boxes.** Every box that names a data object (query, context, rollout,
rubric, memory entry, interface, environment) shows one real instance from a single running case, drawn
where it flows rather than in a separate panel. An interface is shown as code (signatures and a call), an
environment as its API and one episode, a scoring step as the actual outputs with their per-criterion
marks. Abstract concept names and bare symbols (`r`, `o_t`) appear only as tags beside instances. "Why
not put the c and q instances into the boxes instead of abstract concepts" was the question that settled
this.

**A comparison figure runs the same input through both pipelines**, in aligned rows or columns with
identical stage positions, highlights only the module that differs, and draws every branch the method
has (both the generate path and the abstain path). The two-row, two-column comparison with one document
and one query was the one the author called clear.

**A progressive figure keeps one canvas across pages.** When a concept builds over several pages (base
pipeline, variant, method; or level 1 to level 4), use identical coordinates, reserve slots for rows not
yet shown so the outline never resizes, and highlight the current element in the accent. If the
progression is along capabilities, add a small check-mark table that gains one row per page. Clicking
through changes only the new element.

**An iterative or agentic method is drawn as a workflow of its agent stages** (memory → retrieve evidence
→ attribute → propose → critic → re-propose → update), each round in its own lane or cell so a candidate
and a committed output are visibly separate, with one concrete case threaded through every stage with its
actual values and accept or reject marked on each proposal. Keep the rounds in the paper's order. Three
cells could not separate candidate from commit; four could. A long deck had its two proposal rounds
swapped against the paper's figure.

**The shape of a structural figure is the relation it claims.** Nesting for containment, a pyramid or
inverted triangle for build-up, a sequence of stacks for a trend over rounds. Group layers with a
translucent tint over them, not with corner labels. No decorative loop the relation does not have (one
was called forced), and a closing or outlook figure shows the direction of change, not a static map of
where the work sits.

**Connectors on a slide** follow `drawing-figure`'s geometry, plus: a connector attaches to the whole
module it means, not to one internal step; a back-edge stops at the outer frame's edge; arrows into a
stack align to the stack's centre line, and an arrow beside a stacked figure stays clear of the text in
it; when diagonals pile up, re-orient the layout (horizontal 1-2-3 becomes vertical) rather than bend
lines. Keep one arrow-style mapping for the whole deck: solid for data flow within a stage, a distinct
style between stages, dashed for accumulation or update over time, a third style for "applied at" (a
shared output head, a gate), and the accent for the training signal. If two kinds look alike on the
render, the figure fails. Heads with no tail, heads pressed onto boxes and crossings were the most
repeated defect of one 50-page deck.

**Symbols agree across figure, code and bullets.** Every symbol a formula, a code panel or a bullet on a
page uses also appears in that page's figure, and the terms in the bullets match the figure's labels.
When a figure defines many symbols, set an aligned `symbol : meaning` table in small type beside or under
it instead of explanatory bullets. Define a structured object (prompt inputs and outputs, a memory
record) as a table: the English field name in angle brackets first, then a one-line explanation,
hierarchy by indentation, never a field described as a procedure. `writing-style-zh` owns
one-symbol-one-meaning, global renames and field-name order in prose; on a deck the change is cascaded
across every page and figure file in the same pass, and a grep over all of them confirms it.

**A code panel carries only the core lines** (forward and inverse, or the one function the slide
explains), taken from the paper's released code or appendix and never reconstructed from memory, set
syntax-highlighted in a monospace face at or above the code floor, side by side with the schematic and
using the same names so each line maps to a box. "Dump the original paper, extract the core code, don't
guess", then "only the core code, side by side with the schematic, with a correspondence".

**Icons on a slide.** `drawing-icons` owns the family, the fetching and the manifest. On a slide: one
family for the whole deck; one icon per concept with a one-line label, never icons alone and never an
icon over a paragraph; literal icons (a person for a human, a robot for a model or agent); and any icon
that renders as noise at slide size is dropped. Venue logos are replaced by text labels (venue and year).

## Tables and charts on a slide

`writing-table` owns a paper's tables: number format, `booktabs`, absolute values, ordering rows by the
argument. A slide differs in what it marks and how much it carries.

**A comparison table's columns carry the argument.** A related-work or baseline table compares along the
dimensions the slide argues about (which component a route changes, what it leaves unsolved), never
bookkeeping columns such as `stage | work | venue | what I did`. A cell holds the method name, its venue
and a 4 to 8 word mechanism, nothing more. A research overview is not a table: it is a progression
figure, never a grid ([The storyline of a talk about your own
works](#the-storyline-of-a-talk-about-your-own-works)). Headers use the field's ordinary word (`ratio`,
not `share`; `Component` or blank, not an invented `port`). In a deck written in another language, a
table of method names and metrics is entirely in English.

**Set it black on white.** `booktabs` rules, a midrule between method families, minimal cell padding,
small type, a narrow table centred, few columns, with prose columns moved into bullets. Mark the winner
in bold or with a light grey cell, never a saturated fill. Put only absolute values in a table or on a
chart; relative gains (+x points, ×N) go in the bullets. **On a slide this departs from `writing-table`**,
which bolds the best, underlines the second, puts the margin in the winning cell and never shades a
single cell: a slide allows the light grey winner cell, drops the underline and the in-cell margin, and
states gains in the bullets, because the author asked for the winner in grey with no coloured fill
("获胜者灰色，没有底色") and a slide table carries absolute values only. A redrawn table contains every number the
adjacent bullets cite and every baseline family the text names. Large cell whitespace, decorative
colours and a missing baseline were each corrected.

**Re-plot data charts in the deck's font and palette.** Label marks directly instead of using a legend,
and never let a legend cover data. Axis labels in plain words at a readable size, tick labels a step
smaller than body text, not larger, and no explanatory caption. Pick the chart that shows the trend the
slide claims: a cost-versus-quality Pareto scatter for an efficiency claim (it replaced a latency table),
a best-checkpoint or convergence curve for a speed claim. The chart and the text beside it share font and
colours. `drawing-figure` owns the plot house style these refine.

## Citations, footers and the reading-group cover

One bibliography, cited by key. An unknown key is a build error. Never write a citation into slide text.
A method name in a cell or a bullet is a name, not a citation: inside an own-work section the
related-work page names its exemplars that way, and their full entries go on the references page or in
the appendix, so the footer can stay the work's identity. Preprints are cited with year and month,
because in a fast field a bare year does not identify the work. An accepted paper is cited at its venue
and year, not as the arXiv copy that was downloaded, and under-review work says so.

**On a page of your own work, the footer carries that work's identity and nothing else**: the method
name, the paper's full title, its status (accepted at <venue>, under review, submitted) and the storyline
stage it maps to. For a talk about your own works this supersedes the several-sources footer below: the
author first asked for related work one per line in the footer, then for own-work identity only. Cover,
outline, self-introduction and overview pages carry no footer.

**In a reading-group or survey talk, the cover names the papers the talk is built on**, with enough of
the citation that the room can place the work before the first claim lands: short name, **full title**,
first two authors, and the affiliation. A cover that gives only the short name states the label but not
the claim.

**A field the bibliography does not carry is omitted, never described.** Printing "affiliations not
listed on the preprint" states an absence the audience did not ask about and cannot act on. Leave the
line blank.

**One citation format for the whole deck.** The academic habit of a full citation on a section's
first slide and a short form after it looks tidy in a paper and reads as an inconsistency in a deck,
where slides are seen out of order and one at a time. Pick the full form and use it on every slide
that cites. If it does not fit, the citation is too long, not the rule.

**Several sources on one slide go one per line**, and the page number is bottom-aligned with the last
of them, not with the first. Two things follow from a multi-line footer. Beamer fixes the footline
height before the frame body runs, so a `\source` set inside the body cannot grow it: the extra lines
run off the bottom of the page with no warning; draw the citation block from the shipout-time
background layer instead. And once the page number and the citation are produced by two different
templates they will not share a baseline: measure it in the rendered PDF rather than trusting that
they look aligned in the source.

**The footer is a fixed strip and must fit.** A slide citing eight sources sets three lines into a
two-line box. Shrink a step, then elide with "+ N more". Nothing is lost, because the references slide
lists every cited key and is generated from the keys the deck actually used. In practice the footer
holds about **four keys** before it wraps and clips mid-entry, so keep per-slide lists that short and
let the references slide carry the rest: `layout: references` accepts `auto: all` to list the whole
bibliography, and `columns:` with `size:` to fit a long one; three columns at 7 pt hold about sixty
entries.

## Speaker notes are the script

**Every slide gets a script, including the outline and transition pages.** A transition is a sentence
the speaker has to say out loud; it is the one slide with nothing to read off. A deck where five slides
carry no notes cannot be delivered by anyone but its author, and often not by them either ("I need to
read the material to give the presentation"). A generated deck keeps the script in a separate
page-by-page file; a Beamer source keeps it in a comment block (`% 口播：…`) directly above each frame,
where it moves with the frame.

Write them as spoken words: numbers spelled the way they are said, a stage direction where there is a
figure, one idea per paragraph, simple transition words. The test is whether a colleague could deliver
the talk from them. Bullets on the slide, details in the script.

**Use technical register.** "Cohen's kappa", not "kappa". "Exhausting the four-hour budget", not
"running out of clock". Cut conversational openers, hedges and filler; casual phrasing in a script was
rejected.

**When a slide's columns move, re-read its notes.** This is the failure mode that recurs. Restructuring
a slide orphans phrases like "the table on the right" and "the left column is the six stages", and the
result is a speaker pointing at the wrong half of their own slide. Cross-check every left/right
reference in a script against what actually sits in that column, mechanically, after any layout change.

**Timing reads the notes, not the slide text.** Count a Chinese script at one CJK character per word and
about 200 to 220 per minute. Two consequences. Writing notes is what makes the estimate exist, so a deck
without notes reports a guess. And trimming bullets buys almost no time, because the clock counts the
notes. To recover minutes, cut slides or tighten the script.

## Verifying the numbers before they reach a slide

A talk is a claim made to a room that cannot check it. Verify at source, and **scope the verification
to what is printed on the slide**, not to everything the research turned up: re-checking a hundred and
fifty crawled rows to support fifteen is an expensive way to be slow, and it was a real error.

Default to refuted when a source cannot be opened. A number that is close but attached to a different
subset, model, harness or metric is refuted, not confirmed. Check what a claim is attached to, not
just its value: the same figure has meant a paper's headline and its confidence-interval bound.

**For your own works, the paper's latest build is the single source of truth.** Pin each section to a
named build of its paper (a commit or a date, recorded in the figure and section headers) and take every
number, term, example and step order from it. When the paper rebuilds, re-derive the section: numbers,
tables, the example's round order, method names, and delete detail pages that describe a superseded
design. A results row with no run behind it in the paper is removed, never kept with a hedge. When the
paper's prose and its table disagree, the table wins. Recorded: talk and CV numbers for one work
disagreed until both were aligned to the paper build; a placeholder baseline row added while drafting
survived into a later build with invented numbers; an 18-page detail section described an older design;
an example's rounds were swapped against the paper's figure.

**Numbers inherited from an earlier deck are unverified numbers.** Building on someone else's slides,
or on your own from a previous talk, imports their claims at full confidence and none of their
provenance. Re-derive every figure against the source before it survives a rewrite. A real case: a
deck carried "综合表现提高 10.3 个百分点" and "检索延迟由 1453 ms 降至 360 ms" through several revisions;
the paper reports **no numeric result at all** for that experiment. Everything is in one radar chart
whose own caption says the axes are min-max rescaled per metric. Both numbers would have been stated
to a committee.

**When the source has only a figure, show the source's figure and quote only its prose.** Reading bar
heights off a plot, even correctly, even from the vector geometry, produces numbers that appear
nowhere in the paper, and an examiner who checks will find you asserting more precision than the
authors did. Two related habits: say so on the slide when the axis is truncated, and check the prose
against the plot, because they disagree more often than you would expect.

Verification pays. Real defects it has caught: a table that did not exist because the post used charts,
a footnote misattributed to a table, a generalisation refuted by the same leaderboard it came from, a
paper credited with coining a term another paper defined a year earlier, an affiliation the paper does
not carry, and one number meaning two different things on one slide.

## The register of a pitch deck

A proposal or ideation deck is a claim made in a room, and it speaks in the confirmative: its tables
are results, its titles are strong claims, and the numbers on its own arms are stated as what they
are, never apologised for. Provenance hedges ("mock", "forged", "projected", "illustrative", "not
yet run", "runs queued") do not belong on a slide or in its notes. They read as apology, the room
hears the doubt before it hears the idea, and one hedged row discounts every other number on the
page. This is a recorded correction: a four-project one-to-one deck shipped a provenance bullet
under three results tables, every one came back with "remove, these are real results", and each
freed slot was better spent on a mechanism or scale claim.

Three boundaries keep the register honest rather than reckless. Verification still applies with full
force to anything **quoted from a source**: misquoting someone else's table is an error of fact,
not a register choice. The **qualifier** on a score (model, subset, harness, pass@k) is
reproducibility metadata, not a hedge, and it stays. And run status is still tracked, just **outside
the deliverable**: the working notes record which rows have runs behind them, so the author always
knows exactly what they are standing behind, while the deck itself carries only the claim.

## A .pptx the compiler did not build

Some decks and figures are not compiled from a source: a figure deck drawn by a python-pptx script, a
template someone else owns, a pptxgenjs deck. The rules above still apply to what is on the slide. What
changes is the tooling.

**The package mechanics belong to `anthropic-skills:pptx`.** Unpacking, adding and cleaning slides,
schema validation, pptxgenjs gotchas: use that skill for them. It is Anthropic's, licensed for use
inside the service only, so this repository points at it and does not keep a copy. One used to live
here as a skill of its own; it was removed for that reason, and what follows is the part of it that
was written here.

**Audit the geometry, not only the render.** `${CLAUDE_SKILL_DIR}/scripts/overlap_audit.py deck.pptx`
reads the shape geometry and reports three things a rendered image makes you hunt for: shapes that
fall off the slide, text that sits on top of other text or on a box it does not belong to, and edges
that are within a hair of aligning without actually aligning. Run it before the visual pass, because
it finds the defects that are one millimetre wide and it names the shapes, which the eye does not. It
cannot see text that overflows its own box, so the visual pass still happens. It needs python-pptx:

```bash
uv run --with python-pptx python3 "${CLAUDE_SKILL_DIR}/scripts/overlap_audit.py" deck.pptx [--tol 0.02]
```

It was written while rebuilding two paper figures, where every defect it named had survived three
passes of looking at the rendered image.

**Name the arrowhead.** Connectors default to no head at all, and the first thing anyone reaches for is
the filled triangle, which reads heavy at print size and swallows the shaft of a short connector. Set
the head on the line's `<a:ln>`: `<a:tailEnd type="stealth" w="med" len="med"/>`, adding
`<a:headEnd .../>` for a double arrow. `stealth` is the swept head; `triangle` is the solid one. Keep
one kind per deck. `drawing-figure` carries the same rule spelled for TikZ and matplotlib.

**Convert with `${CLAUDE_SKILL_DIR}/scripts/soffice.sh`**, not bare `soffice`:

```bash
"${CLAUDE_SKILL_DIR}/scripts/soffice.sh" --convert-to pdf deck.pptx --outdir .
```

It runs LibreOffice headless in a throwaway profile, so a second instance or a stale lock cannot hang
it, and it **fails loudly when LibreOffice is absent**. The wrapper it replaced was always called with
its output sent to `/dev/null`, so on a box without LibreOffice the PDF step of four figure builds
failed in silence and the PDFs on disk went stale without anyone being told. A build script that calls
this must not swallow its exit status.

**Absent is not unavailable.** On a container whose root is ephemeral, LibreOffice is an apt package
that a restart wipes, while its profile in the persistent home survives and proves only that it once
ran. Before concluding a python-pptx plus LibreOffice toolchain cannot run, check `command -v soffice`
and reinstall `libreoffice-impress` with the fonts the figures need (Liberation, DejaVu, FreeFont,
Carlito); find the python-pptx venv on the current persistent root, since a storage migration retires the
old path. **Never ship a weaker fallback in its place silently.** A deck agent found no `soffice`,
decided the paper figure builders could not run, and shipped TikZ redraws; the container had merely
restarted.

**Fonts and metrics in a LibreOffice render.** `drawing-workflow` owns the type scale, the drawn
subscript and the shadow strip. Beyond those: name fonts that are actually installed, because Calibri
silently becomes Carlito and script letters fall back to DejaVu when FreeFont is missing; measure every
label's width with PIL against the exact font file LibreOffice will use and exit non-zero on overflow;
put non-breaking spaces inside tags that must not wrap. CJK fonts reach LibreOffice and xelatex only
through an explicit fontconfig file, and the CJK face need not be the system UI default when a more
formal one reads better. Labels that fit in PowerPoint overflowed, or changed metrics, in the
LibreOffice PDF.

## Exporting a LaTeX deck and sharing its source

**A .pptx of a LaTeX-laid deck is its pages as images.** Beamer stays the source of truth; a separate
exporter (outside the build) places each rendered page as one full-slide 16:9 image (13.333 × 7.5 in,
about 400 dpi, the aspect ratio asserted) and checks that the slide count equals the PDF's page count.
Ship the PDF with the same base name beside it, because a headless server or an IDE cannot preview a
`.pptx`. The instruction went from Beamer, to "back to pptx", to "pptx plus a PDF preview", and settled
on "cut the Beamer pages out and paste them in": re-laying the text in pptx boxes came out worse than the
LaTeX layout every time.

**A share bundle holds the deliverable and nothing else.** When a talk's source is requested for
sharing, make one archive named `<owner>_<event>.zip` that unpacks to one directory of the same name:

```
<owner>_<event>/
  main.pdf  appendix.pdf      the deck and its appendix as two PDFs
  main.pptx appendix.pptx     their page-image exports, when the recipient presents from PowerPoint
  main.tex  preamble.tex      the compilable source, with sections/, figures/ and assets/
```

The main file is renamed `main.*` in the bundle even though it is named after its talk directory in the
project: the recipient holds one talk, and the author asked for `main.pdf`. No build scripts, reference
material or build junk. Keep it in a local archive folder; it is not pushed. A first bundle had a poor
name, one PDF, and build scripts and reference decks inside.

## Beamer traps that render silently wrong

Each of these cost a build or a round of complaints before it was found, and none shows in the source.

1. **A conditional footer tests the macro's content, not the token.** `\ifstrempty{\currentsource}`
   never takes the empty branch, because its argument is a control sequence and is never empty, so the
   band is painted on every page; use `\ifdefempty{\currentsource}`. Check the condition on a page that
   should not get the band (the cover, the outline).
2. **A font size set outside `itemize` has no effect inside it.** Beamer resets the theme's itemize size
   on entry, so set the size inside the environment.
3. **A custom TikZ style named like a PGF key breaks the build.** A local style called `step` collided
   with the PGF key. Prefix custom style names (`ds-step`).
4. **Beamer adds about 5 mm under the frametitle template**, so every page gets a blank band under the
   title rule. Compensate once in the template with a negative skip and measure the result
   ([Page chrome](#page-chrome-header-logos-navigation)).

## The gates a deck build must have

An error-severity finding fails the build, and an override flag is fine while an override default is
not. **Every gate's exit status is wired into the build script.** A build that runs its checks as
`check || true` prints findings and still exits 0, so a deck with gate failures builds green; one talk
build did exactly that, and a later agent had to run the gates by hand.

For a cc2slides deck, the gates that earn their place: overflow against the geometric geometry, a
missing image, a cite key that is not in the bibliography, a crop whose fractions are out of order or
out of range, a title long enough to wrap, an uncited number, and the timing estimate against the
declared slot.

For a Beamer deck, measured on the log and the rendered PDF:

| gate | catches |
|---|---|
| any `Overfull \vbox` in the log | content pushed off the frame |
| body text below the measured top of each page's citation band | text running into the footer |
| a span more than one CJK glyph outside the text box (hanging punctuation allowed) | bleed past the margin |
| decorative interpuncts and separator slashes, comments skipped | the separator rule |
| a banned-word list with an allowlist of exact dictated phrases | words the author banned |
| a bullet ending in `。` | the punctuation rule |
| figure text under the floor | unreadable labels |
| title-rule-to-content gap outside its band | blank bands and crowding |
| navigation links per page | a bar that does not resolve |
| `.pptx` slide count equal to the PDF's pages | a short export |

Each gate exists because its defect reached the author at least once and is invisible on a contact
sheet. **A banned word stays banned.** When the author dictates one phrase containing it, add that exact
phrase to the allowlist; never take the word off the list or give it a conditional exception, which once
let four instances back into a deck (`writing-style-zh` records the same failure for its word list).

## Reviewing before delivery

**Look at every page, twice.** After every build, run the gates, then render every page to PNG (about
190 dpi), look at each page image and at the contact sheets, and read every changed page on its own:
once for language, once for figures and geometry. Fix, read once more, then deliver. Neither a subagent's
"done" nor a green exit code counts as having looked. Overlaps, misaligned arrows and wording slips
reached the author round after round until this was the rule ("no aesthetic sense or checking?").

**Run an independent critique before the author sees a major section.** A separate model invocation
(`claude -p`, a different model or the writer's critique task) reviews the section as the committee
would: logic gaps, inconsistencies, the questions likely to be asked. Fix what it finds without breaking
the style rules. The author asked for this pass more than once.

**Approved content is frozen.** A page or block the author has approved is excluded explicitly from a
deck-wide restyle (font step, padding, colour, spacing), and its text and spacing are not touched without
a request that names it. Text the author dictated is placed verbatim, typos only fixed
(`writing-style-zh` owns how dictated text enters any document). A requested local edit changes only
what was asked: no expansion, rewrite or filler in the neighbouring text. Approved
self-introduction pages were at risk in a global sweep, and unrequested expansions of dictated text were
rejected ("who told you to expand and rewrite it").

**Render variants for an unsettled visual choice.** When the author has not settled a choice (logo
placement, a footer band, the closing figure's shape, a nested versus a pyramid layout), render two or
three variants as page images side by side and let the author pick. Keep the unpicked ones under
`superseded/`, not called by the deck.

**The writer tool on request only.** Route slide prose through `writing-chatgpt` when the author asks for
it, and then every rewritten line on the requested pages goes through it with a prompt built for formal
slide register, and the coding agent patches the result. Do not call it unprompted. The author's standing
instruction is explicit request only, and it covers all writing, not just slides, so `writing-chatgpt`
is where the policy belongs; the author asked for a token-cost estimate of past writer calls minutes
after giving it, and has kept asking for the tool by name for specific passes.

## Rules

### Build and review
1. **Record each backend's kind, and act on it.** Geometric backends make overflow lint meaningful;
   for a semantic backend, rasterise the output and look, because the layout measured is not the
   layout rendered.
2. **Render and look at every page after every build, and read changed pages twice before
   delivering**, checking placed geometry numerically as well: off-slide, overlapping, column tops that
   disagree. A green exit code or a subagent's "done" is not inspection; overlaps reached the author
   repeatedly when it was treated as one.
3. **An error-severity finding fails the build, and every gate's exit status reaches the build's.** No
   keep-going flag, no `|| true`, because a deck with failures then builds green.
4. **A Beamer deck gates on the log and the rendered PDF**: overfull vboxes, the citation band, glyph
   bleed, separators, banned words with an exact-phrase allowlist, bullets ending in `。`, the
   figure-text floor, the title gap, navigation link counts, and the pptx slide count. Each defect reached
   the author once and none shows on a contact sheet.
5. **Run an independent critique pass before the author sees a major section**, because the author
   otherwise finds the logic gaps the committee would.
6. **Approved pages are frozen and dictated text is placed verbatim**; a local edit changes only what was
   asked, because global sweeps and unrequested expansions undid accepted work.
7. **The writer tool runs on slides only when the author asks for it**, because the author's standing
   instruction, given for all writing, is explicit request only.

### The project
8. **One self-contained directory per talk, its main file named after it, nothing `\input` across
   talks**, and every script resolving the talk root from its own location. A shared preamble let a new
   talk silently change an old one.
9. **Each main file pins `xelatex`, compiles from its directory and from the project root, and fails
   with a named cause on a renamed directory**, because the silent failure surfaces forty lines later.
10. **Freeze a version by sibling copy before a restructure, and never edit another agent's
    directory**, so a finished state and a parallel attempt both survive.
11. **A one-way sync script is retired the moment its target is edited directly**, because its next run
    rebuilds every talk from stale copies.

### Storyline and structure
12. **One named main line, every work exactly one stop on it**: no section titled by period, employer or
    venue, no side branch, no taxonomy grid as the overview. Paper lists and grids were rejected as
    having no story.
13. **Deck order is cover, self-introduction, overview (why page, progression page), the outline as the
    first work's transition, works, closing, appendix**, with a neutral outline page only where it does
    not sit next to a transition outline, because two identical outline pages rendered back to back; the
    outline is vertical, untaglined and reused as the highlighted transition; no full-colour divider; a
    navigation bar on every page but the cover, with every link resolving, so the room always knows
    where it is and the presenter can jump during questions.
14. **Every own work is outline transition, summary page, then one to three body pages in the short
    version, the work the audience cares about most getting the most**, and body pages do not restate
    what the summary said, which was cut as redundant each time.
15. **A summary page's title is `MethodX：通过<机制>，[解决<问题>，]提高<收益>`: one 通过, at most one 解决,
    one 提高, no clause naming a sub-symptom; its body is three single-column blocks with two or three
    result lines (performance, efficiency only when the work claims it, acceptance)**, because it is
    read by a leader in one minute and the author dictated that shape.
16. **An own work's footer is its identity only** (method, full title, status, storyline stage), drawn
    only on pages that have one, per the author's latest instruction; a band on empty pages read as
    chrome.
17. **A method is built up from the simplest baseline one step per page, with two motivation bullets and
    two or three challenges**, because pages opening on the method, or five challenges, lost the room.
18. **Every section opens with position, problem, case, then mechanism**, and its threads are enumerated
    once in bullets and the outline, never in page titles, because opening on the case loses the room
    and enumerator titles were deleted when the author reversed them.
19. **The long version is built first and is a superset of the short one in the same order; the short
    one reuses its material verbatim.** Re-authored short pages lost the approved style.
20. **Pages are budgeted at about one content page per minute, and an overrun drops whole works**, each
    removal a commented `\input` with its reason and restore step. Thinning every work left none clear.
21. **The appendix follows the closing with its own numbering and a name-only divider, outside the
    outline and navigation, and an external talk drops it**, because a blurbed divider was called
    pointless and the job talks were to ship without it.
22. **A deck re-cut for another audience is a sibling copy with every audience-specific term grepped
    out**, and its cover and closing rewritten for the new listener; an external copy kept the defense's
    words.
23. **Facts a self-introduction restates from the CV are copied in the CV's format and numbers**, and
    the two are updated together, because counts drifted between them.

### Titles and text
24. **Title register follows the deck's purpose**: short claims for a pitch; noun phrases or concepts
    for a research talk or defense, with no sentence, result, question, number, enumerator,
    back-reference or metaphor, the summary page being the one exception; English titles in Title Case;
    consecutive slides on one topic share a title verbatim. A claim title spends the finding before the
    evidence, and enumerator titles were deleted after the author reversed them.
25. **Pane labels and table or result-block headings are plain noun phrases**, with setup details on the
    settings line, because a label that asks or narrates makes the reader read a sentence to find a
    column.
26. **Three to five first-level bullets per page, each a bold key phrase and one claim, details in
    sub-bullets; a Chinese bullet ends bare and holds no `。`**, which the author flagged until a gate
    enforced it. A work's summary page follows its own three-block shape (rule 15) instead.
27. **No line wraps onto a second line by a few characters**, checked on the render, because a
    two-character orphan was flagged on three separate pages.
28. **One object one name, one symbol one meaning, across titles, outline, footer, figures, tables and
    script**; a rename is applied by grep across every file in the same pass, figure files included,
    because renames applied to one page left two names on neighbouring pages.
29. **No interpunct and no slash as a separator, on a slide or in a figure**, because a CJK slash renders
    oversized and a `·` reads as a bullet.
30. **No meta notes**: notation disclaimers, provenance of a count, legend or colour-key sentences,
    appendix blurbs, invented takeaways. Each was deleted by the author as what the speaker says.

### Layout and chrome
31. **A column has one left edge**, and outer cell edges carry no padding, because a padded first column
    sits visibly right of the text above it.
32. **The body is centred by a rule with no threshold in it**, so the page does not move under a pinned
    title.
33. **No slide is only a figure, and none is only bullets** unless it is an outline, a takeaway, an
    experimental setting, or a work's summary page, because a bare figure leaves its claim unstated and a
    bare list leaves it unshown.
34. **Layout follows content**: flow figures full width with bullets below, side by side only for data,
    columns a normal gutter apart, one short line under a stacked diagram, because wide gutters and
    two-line callouts halved the figures.
35. **The title-rule-to-content gap is 1.2 to 4 mm measured in the PDF, and the corner mark sits on the
    title's centre line**, because blank bands under the title recurred on every page.
36. **Logos are equalised by optical weight on one centre line**, and a renamed organisation shows its
    current name, because equal file heights made one logo too large and another unreadable.
37. **Grey scale by default; one muted hue per category held across pages; one institutional accent;
    fills only on diagram nodes; red only for look-here; no full-bleed pages and no edge bars**, because
    many bright boxes read as messy and informal.
38. **An organisation's template is copied from, never edited**, because the template belongs to others
    and its brand elements are all a personal talk needs.

### Figures
39. **Each figure's source follows the ladder (crop if legible, else rebuild from the paper's editable
    source, redraw only a teaching figure, re-plot a table only from its own numbers) and the choice is
    named in the figure file's header**, because crops landed at 4 pt and several redraws were worse than
    the original.
40. **A figure caption is a bare name or a bare quantity, or it is deleted**, and no figure carries
    narration beyond a gloss on a span of a concrete example, because the script carries the claim.
41. **Figure text is at or above the floor measured on the rendered PDF** (5.6 pt on a 160 mm Beamer
    page), because a scaled figure hides 3 pt labels behind correct-looking source.
42. **Every generated or rebuilt figure has its builder in `figure-workshop/`**, with the README's
    what-builds-what table, and reaches `assets/` only by an explicit install after its preview was seen,
    because a figure with no builder cannot be rebuilt or traced to its source.
43. **A flowchart is modules, data flow and short arrow labels, with one concrete instance inside the
    boxes**, never prose cut into boxes, which was rejected as text turned into a picture.
44. **Every symbol on a page's formula, code or bullets appears in its figure**, with a symbol table when
    there are many, because coefficients present in code and absent from the figure were flagged.
45. **A code panel holds only core lines taken from released code**, never reconstructed from memory,
    because a guessed line is a claim about someone's implementation.
46. **Before concluding a figure toolchain is missing, check `soffice` and reinstall; never ship a weaker
    fallback silently**, because a container restart once turned rebuilt figures into TikZ redraws.

### Examples and tables
47. **An example is real and complete: quoted source data in its original language first, actual
    outputs with per-criterion scores, then analysis; it is never compressed, and a constructed one is
    written in the deck's language and never restates the criterion it is scored on**, because analysis
    without the data and self-proving examples were each rejected.
48. **A slide table holds absolute values only, marks the winner in bold or light grey (departing from
    `writing-table`: no underline, no in-cell margin), separates families with midrules, and contains every
    number and baseline the bullets cite**, because a missing baseline and coloured cells were each
    corrected.

### Citations and facts
49. **Slides cite by key from one bibliography, and an unknown key is a build error.** Preprints carry
    year and month; accepted papers carry their venue. A citation retyped onto a slide drifts: one author
    list was corrected in the source and not in the three footers that quoted it.
50. **A reading-group cover names each anchor paper with its full title, first authors and
    affiliation**, and omits a field the bibliography lacks rather than describing its absence, because
    a short name alone states the label and not the claim, and a printed absence gives the room nothing
    to act on.
51. **One citation format across the whole deck**, several sources one per line, page number aligned
    to the last line, and the block drawn where it can grow, because slides are seen one at a time, so a
    short form reads as an inconsistency, and a footer set inside the frame body runs off the page.
52. **Verify every number quoted from a source before it reaches a slide**, scoped to what is printed,
    defaulting to refuted; the deck's own arms follow rule 55. A close number attached to another subset
    or metric is still wrong, and re-checking a whole crawl is slow enough to get skipped next time.
53. **Re-derive every inherited number.** A figure carried over from a previous deck has no provenance
    until you check it against the source.
54. **Never read values off a published plot and state them as the paper's.** Show the paper's figure
    and quote its prose, because the values appear nowhere in the paper and assert more precision than
    the authors did.
55. **A pitch deck claims in the confirmative.** No "mock", "projected", "forged", "illustrative" or
    "not yet run" on a slide or in its notes; run status lives in the working notes, never in the
    deliverable, because one hedged row discounts every number on the page, and every provenance bullet
    on one deck came back as "remove, these are real results".
56. **Each section about your own work is pinned to a named paper build and re-derived when it
    rebuilds**; a row with no run behind it is removed, and the table wins over the prose.

### Script, time and export
57. **Every slide carries a script, including outline and transition pages**, written as spoken words
    in technical register, in a separate file or as a comment above each Beamer frame, because a deck
    without one cannot be delivered, even by its author.
58. **Re-read a slide's notes whenever its columns move.** Stale left/right references are the most
    common defect a restructure introduces.
59. **The slot length is declared in the source.** Without it there is no timing check, only a hope.
60. **To recover time, cut slides or tighten the script**, never trim body text; time a Chinese script
    at 200 to 220 characters per minute.
61. **A .pptx of a LaTeX deck is page images with the same-named PDF beside it and an equal page
    count**, because text re-laid in pptx boxes came out worse and a server cannot preview a .pptx.
62. **The deck tooling or talk project carries the agent's operating manual** (a `CLAUDE.md` with the
    build command, the fix for each finding and the instruction to look), because the agent that builds
    the next deck starts without this session.

## Anti-patterns

- **Trusting overflow lint on a semantic backend.** The build is green, the PDF is clipped, and the
  linter measured a layout that was never rendered.
- **The paper list.** Works stacked one by one, or split into "history" and "internship", with no line
  the speaker names. Every paper is clear and the talk has no story.
- **The taxonomy grid.** A two-axis overview any paper of the era fits into. It classifies; it does not
  order.
- **The restated summary.** The body page opens by repeating the background and motivation the summary
  page gave a minute earlier.
- **Pitch titles in a research deck.** Every page announces a finding, so the body has nothing left to
  say and the pages with real results no longer stand out. The tell is a number in the title.
- **The enumerator title.** `工程挑战二：…` in the title of every answering page. It reads as navigation
  and was deleted from every title it appeared in.
- **The relabelled deck.** An internal defense copied for an external talk with the sections and words
  kept. Same research, wrong listener.
- **The thinned deck.** Every work squeezed to fit the slot, so none of them is clear. Drop whole works.
- **The re-authored short version.** Approved pages redrafted from scratch to save space, losing the
  style that had been approved.
- **The two-headed pane.** Both halves banded with a small-type heading, so the slide has two
  competing entry points and neither is the content.
- **The caption that is the script.** A figure captioned with the sentence the speaker is about to
  say, in the smallest type on the slide, where it is read by nobody and inflates nothing but the
  density.
- **The meta note.** `本页省略样本下标`, `计数取自…预跑`, a colour-key sentence. Locally helpful, deleted
  every time.
- **The whole figure.** A four-panel published figure pasted at full width so every panel is
  unreadable, when the slide argues about one of them.
- **The illegible crop.** A column-width paper figure cropped onto a slide, its labels landing at 4 pt,
  when the paper's editable source could rebuild it at slide size.
- **The redraw nobody compared.** A paper's figure redrawn by hand in deck style, messier than the
  original and stripped of its authority, kept because it was new.
- **Text as boxes.** A pipeline of boxes holding phrases, with no modules, no data flow and no instance.
- **The abstract background.** `输入：… 输出：… 核心问题：…` for a broad audience that needed one real
  example.
- **The verdict without the data.** "This pair is spurious" on a slide that shows no rollout and no
  score.
- **The self-proving example.** An intervention that restates the criterion it is scored on.
- **Notes as bullet echo.** Speaker notes that restate the slide text. They inflate the timing
  estimate, help no one rehearse, and cannot be handed to a colleague.
- **The transition with no notes.** The one slide with nothing to read off, and no script for the
  transition it exists to make.
- **The orphaned script.** Slides restructured, notes left pointing at the column that used to be
  there.
- **Trimming slide text to save time.** The clock counts the notes. It buys nothing and makes the
  slide worse.
- **The green exit code.** A build that reports findings and returns success anyway (`check || true`), so
  the Makefile, the CI job and the author all believe the deck is fine.
- **The silent fallback.** A missing `soffice` read as a missing toolchain, and TikZ redraws shipped in
  place of the paper-source rebuilds without a word.
- **The live mirror script.** A delete-and-rebuild sync left runnable after someone edited its target
  directly.
- **The cross-talk `\input`.** A new talk that reuses an old one's section by reference, so the archive
  is no longer what was given.
- **Verifying everything.** Re-checking every row a crawl returned rather than the rows that reach a
  slide, which is slow enough that the checking gets skipped next time.
- **The bibliography retyped onto a slide.** One author list corrected in the source and not in the
  three footers that quote it.
- **The hedged pitch.** A results table apologising for itself with a "projected, runs queued"
  bullet underneath. It feels honest, but the deck is a claim made to a room, and the apology is the
  part the room remembers.

## Companions
`drawing-figure` (what any figure may contain and its connector, arrowhead and spacing geometry; this
skill says where a slide figure comes from, by the crop-rebuild-redraw ladder, and what a slide adds) ·
`drawing-workflow` (the python-pptx idiom a rebuilt paper figure is drawn in, its type scale raised to
this skill's slide floors; its geometry audit and PDF conversion are the ones described here) ·
`drawing-icons` (the deck's one icon family, fetched and recorded in a manifest) · `writing-table` (a
paper's table conventions; a slide table departs from them in how the winner is marked) · `docs-resume`
(the CV whose honors rows and publication counts a self-introduction page copies exactly, and which
shares the bilingual and Overleaf habits of a talk project) · `writing-style` (the punctuation and prose
rules the English slide text and notes obey) · `writing-style-zh` (the same for a Chinese deck: one name
per object, labels as noun phrases, internal-report words kept out of external documents; its slide-title
register defers to this skill) · `writing-chatgpt` (the writer tool's `slide` and critique tasks, used
only when the author asks for them; the deck's gates still run here) · `docs-weekly` (the other
spoken-argument deliverable, which carries an argument rather than a log) · `naming-descriptive` (naming
the talk directory, its snapshots and its assets) · `code-no-fallbacks` (why an unknown cite key, an
out-of-range crop and a renamed talk directory fail loudly rather than defaulting) · `conventions` (the
family index).
