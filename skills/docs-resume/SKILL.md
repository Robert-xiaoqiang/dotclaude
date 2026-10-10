---
name: docs-resume
description: "Build and maintain an academic CV as LaTeX on Overleaf, in English and Chinese, as a one-page pitch and a dense multi-page record. Covers which variant keeps what, the type recipe that holds one page at 9pt, the header and contact line, the research-focus paragraph, entry and bullet anatomy, the publication list and its counts line, fitting a page and clearing short last lines, in-page links and why a pdfpages bilingual bundle strips them, CJK fonts and line breaking, and the Overleaf git bridge. Ships placeholder templates, a link-preserving bilingual bundler and a checker that reads the built PDF."
when_to_use: "Use when writing, revising, trimming or translating a CV or resume, making a one-page or Chinese version of one, bundling the English and Chinese CVs into one PDF, or syncing a CV repository with Overleaf. Also use when a CV spills onto an extra page by a few lines, a paragraph ends on one to three words, links or [n] jumps die in a merged PDF, a Chinese CV renders in the wrong font, the two languages disagree on a count, or a bullet reads like an abstract or a talk transcript."
---
# Skill: docs-resume

## Purpose
A CV is read top to bottom in about a minute, and every line competes for a fixed number of pages.
This skill covers the CV as a deliverable: its variants, the page and type, the shape of each block,
fitting a page without shrinking the type, links that survive an English and Chinese bundle, and the
Overleaf sync. The prose inside a CV follows `writing-style` and `writing-style-zh`; this skill adds
what is specific to a CV on top of them.

## Contents
- [When to Use](#when-to-use)
- [Variants and families](#variants-and-families)
- [Page and type](#page-and-type)
- [The header](#the-header)
- [The research focus](#the-research-focus)
- [Education, experience and people](#education-experience-and-people)
- [Research bullets](#research-bullets)
- [The publication list](#the-publication-list)
- [Honors, service and skills](#honors-service-and-skills)
- [Fitting a page](#fitting-a-page)
- [Links and in-page jumps](#links-and-in-page-jumps)
- [The bilingual bundle](#the-bilingual-bundle)
- [The Chinese version](#the-chinese-version)
- [LaTeX traps in CV macros](#latex-traps-in-cv-macros)
- [Overleaf and git](#overleaf-and-git)
- [Facts and the writer tool](#facts-and-the-writer-tool)
- [Workflow](#workflow)
- [Checks](#checks)
- [Bundled resources](#bundled-resources)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Writing a CV from blank, or refreshing one for a new search (faculty, industry research, an
  internship).
- Making a variant: a one-page pitch from a dense record, a Chinese version from an English one, or
  a bilingual PDF that carries both.
- A page that overflows by a few lines, a paragraph or title that ends on one to three words, a
  section rule touching its heading, a page with a band of white at the bottom.
- Links that work in each language but die in the merged PDF, or `[n]` jumps that land in the
  wrong language.
- Syncing a CV repository with an Overleaf project through its git bridge.
- Not for the sentence-level prose of a CV, a research statement, a cover letter or a bio, which
  `writing-style` and `writing-style-zh` govern. Not for a job-talk or defence deck (`docs-slides`),
  a paper's sections (`writing-paper`), or a Chinese PR article (`docs-pr-article`). This skill
  decides where a claim goes and what shape it takes, not what the research claims.

## Variants and families
Every rule in this skill was a correction made during dozens of review rounds on one English and
Chinese CV pair, and each carries the incident that produced it.

A CV is kept as **families**. A family is one CV in three files: a standalone English source, a
standalone Chinese source, and a bilingual bundle that stitches the two built PDFs together. Two
variants recur, and each is built for its size rather than derived by shrinking the other.

| variant | for | keeps | leaves out |
|---|---|---|---|
| one-page pitch | an industry search, a first screen | header, research focus, education at two lines per degree, only the experiences the target reader weighs most (for industry, the internships) with one or two bullets each, the complete publication list, honors beside service and skills | lab entries whose results already sit in the publication list, the direction keyword list |
| dense record, two or three pages | faculty and academic positions, the full record | everything above, plus every lab and internship entry, earlier degrees included, two or three bullets each, and each publication as a title line over a full author line | nothing that carries a claim |

The split settles a real conflict. A lab entry from an earlier degree was cut from the one-page
version to give the internships the space "they care about more", and was then wanted back, so it
lives in the dense variant. A trimmed two-page version that left a third of each page empty was
"too sparse" and became one page. A variant that leaves white space is the wrong size for its content.

**Name a family by what it is**: `<name>-<variant>.tex`, `<name>-<variant>-zh_CN.tex`,
`<name>-<variant>-bilingual.tex`, with a variant such as `onepage` or `dense`, as the templates are
named (`naming-descriptive`). A date suffix is unnecessary because the family is refreshed in place,
and a recency word such as `latest` or `final` says nothing about which CV the file is. An owner's
existing names stay as they are. When another variant is asked for, create a new family and leave
the existing files untouched.

**Every content change reaches every variant and both languages in the same pass**: a bullet, a
mentor, a count, a link, a title, a number. Then diff the facts across the files (publication ids,
first-author and accepted counts, names, numbers) and across any talk that quotes them. An external
critique found the English and Chinese CVs counting a different number of papers, and the author had
to ask again and again to "sync the dense CV with the same updates".

**Section order is the same in both languages of a variant.** Publications once sat ahead of
Experience in one language and after it in the other. The author's standing instruction is
Publications before Experience, in both languages, and it is the default for every variant.

| variant | order |
|---|---|
| dense (the default) | research focus, Education, Publications, Research Experience, Honors and Awards, Teaching, Service and Skills |
| one-page, as last built | research focus, Education, Research Experience (short), Publications (complete), then Honors beside Service and Skills in one band |

The one-page order is the choice the last one-page build made to put the internships in front of
an industry reader; the author did not reject it but never asked for it, so confirm it with the
author before reusing it, and otherwise keep Publications before Experience.

## Page and type
Build the one-page CV for one page from the start. A two-page layout shrunk until it fits ends with
7pt text and cramped bullets. The recipe that held, in both languages:

| | English | Chinese |
|---|---|---|
| class | `extarticle`, 9pt, A4 | same |
| engine | lualatex (fontspec) | lualatex (ctex, `fontset=none`) |
| body face | Libertinus Serif (holds up at small sizes) | Noto Serif CJK SC, Libertinus for Latin and digits |
| bold, heads | Libertinus Bold, small caps letterspaced 8 | Noto Sans CJK SC Bold, `\ziju{0.08}` |
| margins | sides about 1.3 cm, top and bottom 0.9 to 1.0 cm | the same sides as the English file, top and bottom 0.9 cm |
| line spread | 1.11 to 1.15 | 1.13 to 1.25, wider when the Chinese text runs shorter than the English |
| floor | grey tags at `\footnotesize` (7pt) | nothing below 8pt, so tags use `\small` |
| colour | links only, dark navy (`1F3A5F`), paper titles in near-black ink | same |

The dense variant uses `article` at 10pt with the same faces and about 1.4 to 1.5 cm margins.

**Section heads sit over a 0.4pt hair rule about 3pt below the baseline and 2 to 3pt above the first
line of content.** A titlesec rule pulled up by a negative `\vspace` of 3.5pt sat inside the
heading's descenders on every section, and the author called it a "big issue". Check both gaps on
the render after any spacing change.

**Dates and places align right on the same line** (`\hbox to \linewidth{left\hfil right}`, or a
tabularx with a ragged-right `X` column), never after em-dash separators. The author's words were
that long dashes "look so messy". Keep the gutter between columns tight.

**No institution or company logos.** Two logo attempts were discarded: six logos never read as one
set (different colour families and resolutions, and one institution with no usable file). The
author's instruction after the second attempt was to use generic icons instead (a book for
education, and so on). Any variant may carry one family of generic section icons at text height in
one colour (`drawing-icons`), or none when the page is tight.

## The header
The name in the largest type, with a right-aligned status line on the same row: the current position,
then `Available from <Month YYYY>`. Below it, **one** contact line at near-body size: email, the
Google Scholar profile (linked), phone number(s), and the city the candidate is in now. One hairline
closes the header. The separator is a grey pipe with a quad on each side (`\quad|\quad`) in both
languages. The interpunct and the slash render too large beside CJK glyphs (`writing-style-zh`).

The Chinese header puts the native-script name and its Latin form side by side on the name row,
never stacked. A Chinese header that split the contacts over two lines in small type drew "waste so much
space", and its fix took the header from 115pt to 80pt of height.

Leave out of the header: a GitHub link when there are no notable repositories (the author's
reasoning was that a profile with no high-star projects counts against him), a bare domain name shown
as text (link the Scholar profile instead), and any field the owner never stated. A generated
Chinese draft invented a messaging handle, a desired position and a desired city.

## The research focus
The opening is **one paragraph in a selling register, introduced by a bold run-in label** (`Research
focus`, `研究方向`), not by a section heading. Its shape:

1. a thesis sentence, opened with `My research ...` (an endorsed critique called `I am interested
   in` tentative),
2. one sentence per timescale or half of the agenda, each saying what changes and naming the
   methods (an agenda with no natural halves runs problem, then agenda, in the same place), and
3. one vision sentence.

Do not split it into near-term and long-term goals (the author cut that structure). Every new
concept needs a bridge from the sentence before it: a sentence that announced "X is the binding
constraint" with no lead-in had "no clear logic transition". A coined vision phrase gets checked
against the literature, and the field's established phrase replaces it.

**The opening names objectives, not machinery**: what the work changes and what that buys
(efficiency, effectiveness). Training-loop internals such as sampling details, top-k or the
optimiser belong in the bullets, and vague wh-phrases (`what was taught`, `how it was judged`) are
rejected outright. The exception is the author's own wording.

**When the author supplies a draft of the paragraph, it is the paragraph.** Save it verbatim to a
file first. By default only grammar and agreement change. When the author asks for more, a polish,
a fix for awkward or redundant wording, or a fit to the line, that request is the scope: the claims
and their order stay, and every changed span goes back to the author as a before/after pair. The
rule is owned by `writing-style` (Revising the author's text) and `writing-style-zh`
(作者给定的文字). On a CV it went wrong twice: a writer-built opening meant to be more insightful
was rejected as worse than the old one, and both times the shipped version was the author's draft
with small edits. A later draft of the author's named one training-loop internal, and that wording
stays even though the objectives rule above would cut it.

**Method names go in square brackets, and each one is an in-page link to its publication entry**:
`Capability One [\pubref{5}{MethodA}], Capability Two [\pubref{8}{MethodB}, \pubref{9}{MethodC}]`.
Parenthesised names were corrected to square brackets, and the same bracket form is used in both
languages and every variant.

**The opening has a line budget**: five lines in an English one-page CV. Its last line holds at least
about four words or five CJK characters. The fix for a short last line is wording (see
[Fitting a page](#fitting-a-page)). The Chinese opening that left 进的机制 alone on its last line was
cleared by deleting four filler phrases without touching a claim, which was in scope because the
author had asked for the line to be fixed.

**One name per object across the whole CV.** The term the opening introduces for a concept of the
owner's is the term the bullet heading and both languages use, and it is defined where it first
appears (`writing-style`, one term for the contribution). The bullets map visibly onto the
opening's halves: each half's word starts the heading of the bullets that belong to it.

## Education, experience and people
**Each degree is two lines.** Line 1: the institution, linked, with city and dates at the right.
Line 2: the degree, the expected date for a current degree (written out, `expected Sept. YYYY`), and
the advisors with titles, all on one line at body size. The current degree's line also names the
internships held during it, linked, so a reader who stops at Education sees the strongest
affiliations. A secondary fact about a degree (a named program, a thesis, an exchange) goes on the
degree line, not in an entry of its own.

**An experience entry is an org line and a role line.**

```
\entry{Team, Lab, Company (now New Name)}{City, Country}{YYYY.MM -- present}
      {Research Intern, mentored by A, B, and Dr. C}
```

The org line is one bold linked line of official names, and a renamed organisation is written
`Old Name (now New Name)`. The role line uses a serial comma and says `mentored by` or `advised by`.
The author's question about `internship host` was "is it a standard concept? why not supervisor or
mentor?". Set the role line in the same full-size upright style as the education detail lines, with
tight space around it. A small grey italic role line with loose spacing read as sparse and hard to
read.

**Titles.** `Prof.` for professors, `Dr.` for doctorate holders without a professorship, the same
title wherever the person appears, `Profs. X and Y` for two. Check every mentor's title, because a
titled person sitting untitled among titled peers was caught twice. People's names stay in their
Latin form in both language versions. The Chinese CV once transliterated the advisors, and the
author's instruction was to keep every name in English in both versions.

**Dates are never altered.** Showing year or month precision is a display choice, and once the owner
gives exact months they are used. Keep one date format per language within a file.

**Named collaborators.** Name a collaborator who is not an advisor only when that person co-authors
papers listed on the same CV, so the reader can check the connection on the page. Link them to their
Scholar profile. Add a present-employer tag (`Prof. Name (now Org)`) only where the owner asks for
one, as he did for an advisor who had moved, fitted to one line with `\mbox`.

**Link every person** (homepage if one exists, otherwise Scholar), **every organisation, and the
course title on a teaching line.** Keep links dark navy and paper titles in ink, so a page full of
links does not read as a wall of blue.

## Research bullets
A research bullet has four parts: a bold heading in the field's terms, a grey `[MethodX, venue or
status]` tag, an `[n]` jump to the publication, and one paragraph of three or four sentences.

```
\result[9]{Label-efficient speech recognition}{MethodC, Venue YYYY submission}
  {Proposed MethodC, in which <innovation>, addressing <problem>. <Mechanism 1>, and
   <mechanism 2>. Across <N benchmarks or domains>, MethodC beat the strongest baseline by about
   K points and <efficiency gain>.}
```

The author dictated this shape after rejecting a bullet copied from talk text: the framework, what
co-evolves, the problem it solves, the core mechanisms, the margin over baselines and how much faster
it converges. The verb-mechanism-result order of each line is owned by `writing-style` (contribution
statements, not an oral explanation). The CV-specific parts:

- **Lead with the design, not a background or challenge sentence.** The author first asked for
  direction, challenge, solution, results, and hours later said the opening sentence "shows up
  suddenly" and should go. The later instruction stands.
- **Mechanism over numbers.** Every bullet states the key idea and how it is designed. Dense numbers
  stay only in the one or two headline works. Bullets that drifted into number lists drew the
  complaint that a reader cannot grasp anything from so thin a statement.
- **Results in compact form**: the strongest honest margin over the strongest baseline plus one
  efficiency figure, `+X/+Y on A/B, -Z% tokens`. Drop a small margin that undersells the work when
  a larger one exists (a `+1.0` printed beside a `+2.4` drew "just 2.4 points, and faster
  convergence"). Do not narrate why the number moved.
- **Headings use the term the field searches for** (`Speech Recognition`, `Program Synthesis`), not
  a paper's private phrase, and avoid low-energy framing words such as `controller` or `control`
  for a framework.
- **No implementation procedure or internal module names.** "A candidate edit is pre-applied on
  frozen parameters, measured, then committed" was "useless" detail. Name the mechanism as a concept
  in one clause and sell what is new.
- **A paper's diagnosis is not its method.** A bullet that described how failure modes were
  classified was "wrong, the core idea is ..." the mechanism that was built.
- **No pasted abstract or slide text.** A bullet lifted from a talk's summary page drew "isn't this
  just pure copying?".
- **A project without a paper** is written from its own design docs, plans and reports, quoting only
  numbers that trace to a run that still exists. Internal ablations are fine. Cross-system
  leaderboard numbers whose runs were deleted, and claims the project notes record as retracted,
  never appear.
- **An application with no finished result** (a method carried to a new modality, say) gets
  one bullet of one or two sentences framed as an extension, saying what it studies, with no numbers.
- **Curate for one story.** Projects from an unrelated area stay out of the bullets (their papers
  stay in the list), a claim with no public result is dropped and its space goes to the stronger
  bullets, and a claim found to be wrong is removed, because a wrong claim on a CV is worse than a
  missing one.

## The publication list
**Number descending, newest highest**, so ids never shift when work is added. **Never explain the
conventions on the page**: no `Numbered newest first`, no `Bold = me`, no gloss of what `[n]` means.
The author removed each one ("it's obvious for the reader").

**One counts line sits above the list**, computed from the entries and checked to sum:

```
N publications, M first-author, K of them accepted (VenueA ×1, VenueB ×3, VenueC ×2). <Role sentence>.
```

Use no ambiguous token: `arXiv ×1` drew "refers to which?", because it could mean either of two
preprints. The author writes `×1` himself, so it is fine; dropping it (`VenueA, VenueB ×3`) is an
option when the line needs the space. No topical prose either: a `Recent work is on ...` version was
sent back to the old count-only style. The owner's role sentence (`Led the <chapter> of the <named
work>.`) stands on its own: joining a noun phrase and a verb phrase with `and` (`9 first-author
(...) and led the chapter`) read as "disgusting", and the work goes by its real name, not a
shorthand that appears nowhere else.

**Entry formats.**

| variant | entry |
|---|---|
| one-page | one hanging paragraph: `[n] Authors. Title. Venue. [link] [badge]`, author initials, the owner bold, the venue bold grey inside an `\mbox`, `\nolinebreak` before `[link]` and before the badge |
| dense | a title line with the venue right-aligned, the full author line beneath it, `[link]` and badges at the end of the author line |

**Linking.** Every title links to the accepted proceedings page (ACL Anthology, the conference
proceedings, the publisher), or to arXiv when there is none. A paper that is not public yet links to
the owner's Scholar profile for the time being. Every entry also ends with a trailing `[link]`. This
changed twice: the trailing links were removed when the title became the link, and came back on
every entry because the line ends had room. The latest instruction stands.

**Badges and venue tags.** After `[link]`, linked recognition badges such as a daily or weekly
paper-ranking place (`[Top-5 of the Week]`) point to the ranking page. The venue tag carries the
track (`ACL YYYY Findings`, `EMNLP YYYY Oral`). Preprints are `arXiv YYYY`, never `Preprint
YYYY`. A paper under review can show `<Venue> submission` in its bullet tag while its list entry
stays `arXiv YYYY`.

**A paper with dozens of authors** shows `FirstAuthor et al. (N authors)` and opens with the owner's
role in bold, `Led the X Chapter.`, in the strongest wording the owner confirms. Once the owner asked
for `led`, keeping the hedged `core contributor` drew "why don't you adopt it?".

**A paper under review whose preprint is not public yet** carries the author list the owner
supplies, or `OwnName et al.` if the owner asks for that, and links to the owner's Scholar profile
until the preprint is out. The `et al.` form was asked for once and superseded later, when the author
gave the full author list of a submission whose preprint was still being prepared.

## Honors, service and skills
**Each honor is one row**: the award name in bold, the amount with its currency written in the
document's language, the awarding institution, and the year at the right. Each language names the
award only in its own language, so a foreign official name and its gloss are both dropped ("the
English version uses English only, the Chinese version Chinese only").

**In the one-page variant, honors sit beside service and skills** in two top-aligned minipages, set
smaller than the body (about 7.6pt in English and 8pt in Chinese on a 9pt page), while education
detail stays at body size. Measure the label column from the widest label: a column measured from a
short label ran `Languages` into its value.

**Skills is one line**: the programming languages and the training and inference stack that backs up
the experience entries. Programming and stack were two lines and were merged. No jokes or trendy
labels (`vibe coding` drew "a good signal for a CV?") and nothing irrelevant to the target role.
**Service** reads `Reviewer for <Conf> (years) and <review system>`. The labels are Teaching, Service,
Skills and Languages. When unsure whether a term is standard for the genre, check real CVs in the
field before using it, because a nonstandard term marks the page as machine-written.

## Fitting a page
**Use the levers in this order**, and cut content only after all of them:

| order | lever | example |
|---|---|---|
| 1 | wording | cut filler, reorder clauses, wrap a name and its parenthesis in `\mbox` |
| 2 | list and section spacing | `itemsep`, `topsep`, `\titlespacing*` |
| 3 | margins | side margins first, never wider in the Chinese file than in its English sibling without a reason |
| 4 | line spread | `\linespread` in steps of 0.01 to 0.02 |
| 5 | font size or class | the last resort, and never below 8pt for CJK |

**Space freed at the end goes back into line spread or detail, never into white space.** Every page
runs to the foot, which the checker reports as a fill of 93 to 98%. The author asked for two full
pages with no extra space at the top or bottom, and a Chinese file with wider margins than its English
sibling for no reason was narrowed and its slack given to the bullets.

**Short last lines.** No paragraph, bullet, education line, opening, publication entry, counts line
or label row may end on a line holding one to three English words or one to four CJK characters
(punctuation not counted, the threshold `check-cv.py` uses). The author flagged these round after
round and made it a standing request. Fix one by wording first: delete a word that carries no claim,
or, when the author allows it or the page has room, add a substantive clause that completes the
line. The author asked for exactly that ("twist the last line, or more text"), and asked for spare
space to go into "more details" in the bullets. Never shrink the font for it. The sentence-level
rules (re-read every sentence, never trade a claim for the line) are owned by `writing-style` and,
for Chinese, `writing-style-zh` (段末孤行). **A short tail the checker reports blocks shipping.** Run
`check-cv.py` on every variant the repository builds (the one-page and the dense CV, each language)
and fix every tail it lists before the work is reported. A tail found in a variant you did not edit
is still yours to fix. Listing it as an open item for the author is the failure: the author called
it a basic requirement and asked why a known defect was left waiting for his answer. The layout
means, in order:

1. Tie a fragment to its neighbour: `\mbox{Org (now New Name)}`, `\mbox{\bfseries Venue}`,
   `\nolinebreak` before `[link]`.
2. Move a clause so the break falls elsewhere.
3. `\looseness=-1` on that one paragraph, with its limits below.

**What `\looseness=-1` does.** It asks TeX for a paragraph one line shorter. When that is impossible,
TeX does not stop at its first acceptable set of breaks: it runs every pass, including the emergency
pass that adds `\emergencystretch`, and keeps the break set from the last pass whose line count is
closest to the target. Those breaks can differ from the default ones, so in one Chinese opening the
same five lines came back with a dozen characters on the last line instead of two. Its limits:

- It only helps a paragraph with stretch to spare, and it cannot be told which line to change.
- Under `\raggedright` the emergency pass accepts very short lines. In a publication macro it once
  left an entry whose first line held only the author names, so it never goes into `\pub`, `\entry`
  or list macros.
- It applies to one paragraph and is reset at the paragraph's end. Put it right before that
  paragraph's text with a comment saying which tail it fixed, and re-check the render after any edit
  to the paragraph, because a different text gives different breaks.

Wording first remains the rule: the shipped fix for 进的机制 was deleting filler, and `\looseness`
stayed only in a variant where wording could not do it.

## Links and in-page jumps
`hyperref` with `colorlinks`, `pdfborder={0 0 0}`, links in dark navy, titles in ink. Each
publication label carries `\hypertarget{pub:<n>}`, and bullets and the opening jump to it with
`\hyperlink{pub:<n>}{...}` (`\result[n]`, `\pubref{n}{Name}` in the templates).

**Verify links in the PDF, not the source.** `check-cv.py` counts URI and internal links read from
the PDF, confirms that each jump whose entry it can identify (from the destination name, or from a
single `[n]` under the link) lands on that entry's label rather than on a bullet's tag, fails a jump
that crosses from one language half into the other in a bundle, and reports how many jumps it could
not identify. A single CV and the Overleaf bundle name every destination, so nothing goes unchecked
there. The PDF-level merge keeps no names, so its method-name jumps are covered instead by
`build-bilingual.py`, which reads each rewritten jump back and compares it with its source
destination. Check every URL against the title of the live page it opens (the curl loop in
[Checks](#checks)). The links on the CV this skill came from were trusted only once each had been
checked that way.

**PyMuPDF coordinates.** The `to` point of a named destination comes back in PDF coordinates (y
measured upwards), while `insert_link` expects MuPDF coordinates (y measured downwards). Convert with
page height minus y, or every jump lands mirrored about the middle of the page, which is what the
first merged bundle did.

## The bilingual bundle
**English first, then Chinese.** Each half is a standalone monolingual CV, the bundle typesets
nothing itself, and it has a compilable root `.tex` in the Overleaf project so the owner can build
it there. The first bundle led with Chinese and had no root file, and both were corrected.

**`\includepdf` strips every link.** pdfpages imports each page as a form XObject and discards its
link annotations, URLs and internal `[n]` jumps alike. The first bundle carried none of its 58
external and 12 internal links, and the author found that "the cross-reference in the merged version
does not work". Two fixes work, and `build-bilingual.py` produces both:

- **An overlay for Overleaf.** Read every link rectangle and destination from the two half PDFs with
  PyMuPDF and write a links `.tex` that, through pdfpages' `picturecommand*`, lays an invisible
  `\href` box over each URI link, an invisible `\hyperlink` box over each internal link, and a
  `\hypertarget` at each destination. Destination names carry the half (`en:pub:3`, `zh:pub:3`), so
  a jump never resolves into the other language. The file records each half's MD5, and the bundle
  stops with an error when a half no longer matches, rather than placing the boxes over the wrong
  text.
- **A merge at the PDF level** for use outside Overleaf. Both halves define `pub:1 ... pub:n`, so
  after concatenation the names collide. Resolve each named link against its own source document
  and rewrite it as an explicit GoTo to an absolute page of the merged file.

**The bundle imports snapshots.** Overleaf compiles one root, so the bundle reads committed PDFs of
the two halves from `pdf/`. Keep `pdf/` tracked and every other build output ignored. After editing
either source, recompile it, copy it into `pdf/` and regenerate the link layer, or run the bundler
with `--refresh`, which does all three. A stale snapshot is the failure the MD5 check exists for.

## The Chinese version
**Write the Chinese from the English meaning, as native Chinese, not sentence by sentence**
(`writing-style-zh`). The Chinese opening that tracked the English clause by clause was sent back
for not reading naturally.

**Retune the template, do not clone it.** A cloned English layout read "very sparse" in Chinese,
especially the publication list. Give the Chinese file CJK fonts, a CJK leading and the 8pt floor,
and keep the structure the English one has. Use the academic register: full author lists with the
owner bold, and no job-application furniture (a job-intent bar, school-tier tags, per-entry ranking
tags, tally lines). The first Chinese-native rebuild drew "not academic style", and the next one "so
ugly, change a template". Head the opening 研究方向, not 个人简述.

**The language boundary.**

| element | English CV | Chinese CV |
|---|---|---|
| people's names | Latin | Latin, never transliterated |
| publication entries (authors, title, venue, role note) | English | English, the whole entry, never mixed scripts within it |
| award and degree names | English | Chinese only, no foreign name and no gloss |
| method names and named concepts from the papers | English | English, the same string |
| section headings | English | Chinese |
| dates | `YYYY.MM`, `expected Sept. YYYY` | `YYYY.MM`, `YYYY 年 M 月起可入职` |
| punctuation | ASCII | full-width (`punct=quanjiao`) |

A publication entry carrying a Chinese role note and author count beside the English title was
corrected back to English, because mixed fonts in one line looked pasted in. A half-translated
concept name (a Chinese prefix on an English noun) drifted from the English and was replaced by the
English term.

**Line breaking.** Set `\hyphenpenalty=10000` so English words never break mid-word inside a Chinese
line, and leave `\exhyphenpenalty` at its default so an explicitly hyphenated compound can still
break. Setting both made a hyphenated name unbreakable, and one line ran 24pt into the margin.

**Fonts differ between Overleaf and a local build.** Guard each CJK family with `\IfFontExistsTF`
and a Fandol fallback. Overleaf has Noto CJK, but a local luaotfload may not index the system's Noto
fonts and then silently takes Fandol: the same metrics, a different look. Local PDFs once shipped in
Fandol while Overleaf rendered Noto, so the reviewed look was not the delivered one. To proof the
Overleaf look locally, put the Noto CJK OTFs in a directory and export `OSFONTDIR` (and a scratch
`TEXMFVAR`) before running lualatex, then read the embedded font names back from the PDF.

## LaTeX traps in CV macros
Each of these shipped, or nearly did, with a clean compile.

| trap | what it did | fix |
|---|---|---|
| `\color` inside a `\setbox` | leaked into every later paragraph, so the page turned grey below Education | `\textcolor`, or the colour set inside an explicit group within the box content, then a look at the render below the macro |
| `\color` at the very start of a `p` cell or minipage | started vertical mode and pushed the cell down a line | begin the cell with `\leavevmode` or `\strut` |
| `\settowidth` from a short label | `Languages` ran into its value | measure the widest label |
| `\needspace` before an entry | pushed the whole block to the next page and left a seventh of the page blank | remove it, fit by wording |
| `\looseness=-1` in a list macro under `\raggedright` | an entry's first line held only author names | never in `\pub` or `\entry` |
| a negative `\vspace` before the section rule | the rule sat in the heading's descenders | about `-1pt`, rule about 3pt under the baseline |
| a title in a fixed-width `\makebox` venue slot | overflowed both margins with no Overfull warning | measure on the render, not the log |
| `\hyphenpenalty` and `\exhyphenpenalty` both 10000 | a hyphenated name went 24pt overfull | block only `\hyphenpenalty` |
| academicons under xelatex | icon glyphs dropped silently (fontawesome5 embeds fine) | keep the engine the source declares, and check for missing characters in the log |

## Overleaf and git
**Engines and the main document.** Declare each source's engine on its first line (`% !TeX program
= lualatex`). Build scripts read that line instead of hard-coding one engine per family, which once
built a half with the wrong engine after two families diverged. Overleaf's documented control is the
project menu (Menu, Compiler and Menu, Main document), one compiler per project, so set the main
document to the root you want and the compiler to the engine its first line names. Keeping every
root on LuaLaTeX, the bundle included, means switching the main document never needs a compiler
switch.

**Fonts.** Overleaf's TeX Live carries Libertinus and Fandol, and its system has Noto CJK. Anything
else goes into the project as files and is loaded by file name.

**`.gitignore` from the first commit**: the LaTeX intermediates (`*.aux *.log *.out *.synctex.gz
*.fdb_latexmk *.fls *.xdv *.bbl *.blg *.bcf *.run.xml *.toc *.nav *.snm`), root-level PDFs and the
build directory, with `pdf/` tracked for the bundle. Ignore rules do not apply to files already
tracked, so artifacts committed before the rules existed are untracked with `git rm --cached`. They
were, and every local compile pushed six changed files to Overleaf.

**The git bridge.**

- The branch may be `main`, not `master`. Check `git branch -a` first. `git push origin master`
  failed with `src refspec master does not match any`.
- The bridge token goes through a credential helper that reads a secret file. Never put it in the
  remote URL, the repository or a chat transcript, where it ends up in logs and in `.git/config`.

  ```sh
  git config credential.helper \
    '!f() { test "$1" = get && echo username=git && echo "password=$(cat "$OVERLEAF_TOKEN_FILE")"; }; f'
  ```

- Edits made in the Overleaf editor arrive as commits of their own. Fetch and merge before editing
  locally.
- A push that times out may still have landed. Compare `git ls-remote origin <branch>` with `git
  rev-parse HEAD` before retrying, and never answer a timeout with a force push or a re-clone.
- Committing and pushing are separate decisions (`git-commit`, `git-push`). Push only when asked.

## Facts and the writer tool
**Every number, venue and author list traces to the latest build of the paper.** Where a paper's
prose and its tables disagree, the table wins: one paper's prose had swapped two values relative to
its own table. When the CV and a talk quote different numbers, update both to the paper (the talk is
`docs-slides`' concern, the number's source is the paper).

**Before shipping, verify** co-author spellings and order, the venue and track (Findings, Oral), the
year and status of the accepted version (a downloaded arXiv copy made an accepted paper look like a
preprint), people's titles, and every URL against the live page title. A co-author surname went out
misspelled once.

**Route CV prose through the writer tool** (`writing-chatgpt`) with the critique-and-revise rounds
`writing-style` sets (Polishing through the writer tool), then one adversarial fact check of the
result against the sources. What is specific to a CV is the brief, which names:

- the reader: a recruiter or hiring manager reading in page order,
- the register: a first-person research CV, a pitch but not a slogan or an abstract,
- the facts that are frozen: every number, venue, date, name, title, URL, `[n]` id, paper title and
  author list, plus the LaTeX macros and link targets,
- the length budget: no longer than the original, deletions preferred, because the page is full,
- the style skill for the language, and the terms the author has fixed (the English concept names
  kept in the Chinese version, say).

Patch the result back yourself. **Screen every suggestion against the author's explicit
instructions before applying it.** One critique recommended deleting the internships the author had
put on the doctoral line and the chapter-lead claim he had asked for, and another proposed a
separator he had banned. Applying them would have reverted his decisions without his knowledge.

## Workflow
1. Copy the templates from `${CLAUDE_SKILL_DIR}/resources/templates/` into the CV project's root
   under the family names, and the two scripts into the project's `scripts/` with a README.
2. Gather the facts from their sources: the paper builds, the proceedings pages, Scholar, the
   official names of organisations. Save any paragraph the author supplies, verbatim, before
   touching it.
3. Fill the English source: header, research focus to its line budget, entries, bullets in the
   four-part anatomy, the full publication list with the counts line computed from it.
4. Run the writer passes and screen them. Patch back.
5. Build into a scratch directory, run `check-cv.py`, look at every page, and fit with the levers in
   order until the page count is right, the fill is 93 to 98%, and no short tails or overfull boxes
   remain.
6. Write the Chinese source from the English meaning, build it with the Noto fonts Overleaf uses,
   and check it the same way.
7. Diff the facts across both languages and every variant.
8. Refresh the bundle (`build-bilingual.py --refresh`), build it, and check that its links survived.
9. Commit (`git-commit`). Push to Overleaf only when asked (`git-push`), through the credential
   helper.

## Checks
Build outside the repository and outside this skill, so no intermediate lands in either.

```sh
export PATH=<texlive>/bin/x86_64-linux:$PATH
OUT=$(mktemp -d)
lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage.tex
python3 scripts/check-cv.py "$OUT/cv-onepage.pdf" --log "$OUT/cv-onepage.log" --pages 1

# Chinese, proofed with the fonts Overleaf has
export OSFONTDIR=<dir with NotoSerifCJKsc-Regular.otf, NotoSansCJKsc-Regular.otf, NotoSansCJKsc-Bold.otf>
export TEXMFVAR="$OUT/texmf-var"
lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage-zh_CN.tex
python3 scripts/check-cv.py "$OUT/cv-onepage-zh_CN.pdf" --log "$OUT/cv-onepage-zh_CN.log" --pages 1
python3 -c 'import sys,pymupdf; d=pymupdf.open(sys.argv[1]); print(sorted({f[3].split("+")[-1] for p in d for f in p.get_fonts()}))' "$OUT/cv-onepage-zh_CN.pdf"

# Render every page and look at it: short tails, rule overlaps, colour leaks
python3 -c 'import sys,pymupdf; d=pymupdf.open(sys.argv[1]); [p.get_pixmap(dpi=150).save(f"{sys.argv[1][:-4]}-p{i+1}.png") for i,p in enumerate(d)]' "$OUT/cv-onepage.pdf"

# The same publication ids, titles and venues in every pair of files (both languages, every variant)
python3 - cv-onepage.tex cv-onepage-zh_CN.tex cv-dense.tex <<'EOF'
import re, sys
pat = re.compile(r'\\pub(?:\[(?:[^\[\]]|\[[^\]]*\])*\])?\{(\d+)\}\{(.*?)\}\{(.*?)\}')
ref, *rest = sys.argv[1:]
a = pat.findall(open(ref, encoding="utf-8").read())
for f in rest:
    b = pat.findall(open(f, encoding="utf-8").read())
    print(f"{ref} vs {f}: {len(a)} vs {len(b)} entries:", "same" if a == b else sorted(set(a) ^ set(b)))
EOF

# Every URL against the title of the page it opens
grep -o 'https\?://[^}]*' cv-onepage.tex | sort -u | while read -r u; do
  printf '%s\t%s\n' "$u" "$(curl -sL --max-time 20 "$u" | grep -o -i -m1 '<title>[^<]*' | head -1)"
done

# The bundle: refresh the snapshots, build the Overleaf root, confirm the links survived
python3 scripts/build-bilingual.py --family cv-onepage --refresh
lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage-bilingual.tex
python3 scripts/check-cv.py "$OUT/cv-onepage-bilingual.pdf" --pages 2
python3 scripts/check-cv.py pdf/cv-onepage-bilingual.pdf --pages 2   # method-name jumps show as unchecked

# Build outputs ignored, snapshots tracked
git check-ignore -v cv-onepage.aux cv-onepage.pdf; git ls-files pdf/
```

`check-cv.py` exits with the number of failures: a wrong page count, a jump that misses its entry or
crosses languages, an Overfull box or a missing character, and under `--strict` every jump it could
not identify. Fill and short tails are reported for a person to judge on the render, because
PyMuPDF's text blocks approximate TeX paragraphs.

## Bundled resources
`${CLAUDE_SKILL_DIR}/resources/README.md` says how to build each file.

| file | what it is |
|---|---|
| `resources/templates/cv-onepage.tex` | one-page English CV, lualatex, placeholder content |
| `resources/templates/cv-onepage-zh_CN.tex` | one-page Chinese CV, lualatex, Noto CJK with a Fandol fallback |
| `resources/templates/cv-dense.tex` | dense two-page English CV with the direction sidebar: every fact of `cv-onepage.tex`, word for word, plus the lab entries and bullets the one-page variant leaves out |
| `resources/templates/cv-onepage-bilingual.tex` | the Overleaf bundle root for the one-page family |
| `resources/scripts/build-bilingual.py` | writes the bundle's link layer and the merged PDF, `--refresh` rebuilds the snapshots |
| `resources/scripts/check-cv.py` | page count, fill, links and jumps, short tails, log counts, read from the built PDF |

Every name, institution, date, title and URL in the templates is a placeholder. Never copy a real
CV's personal details into this skill or its resources, because the skill family is published.

## Rules
1. **A family is an English source, a Chinese source and a bundle, named `<name>-<variant>`**, by
   what it is. The family is refreshed in place, so a date or a recency word such as `latest` adds
   nothing a reader of the file name can use; an owner's existing names are left alone.
2. **A new variant is a new family**, and the existing files stay untouched. The author asked for a
   new variant on the condition that the current CV stay as it was.
3. **The one-page variant keeps the complete publication list and drops lab entries whose results
   that list already carries.** The dense variant keeps every entry. This split resolved a cut that
   was later reversed.
4. **Every content change lands in every variant and both languages in the same pass, followed by a
   fact diff.** The two languages once disagreed on the paper count.
5. **Both languages of a variant use the same section order.** Publications once sat in different
   places in the two.
6. **The one-page CV is built at 9pt for one page, and CJK text never goes below 8pt.** Shrinking a
   two-page layout gives 7pt text, which is unreadable in CJK.
7. **The header has one contact line at near-body size, separated by `\quad|\quad`, and no field the
   owner never stated.** Two lines in tiny type took 115pt of header where 80pt now holds it all,
   and a generated draft invented contact fields.
8. **The research focus is one paragraph with a bold run-in label, opening `My research ...`, one
   sentence per half, then the vision**, fitted to a stated line budget. Near-term and long-term
   splits and unbridged concepts were cut.
9. **An opening the author supplied is kept from a verbatim saved copy. By default only grammar and
   agreement change; when the author asks for a polish or a fit to the line, that request is the
   scope, the claims and their order stay, and every changed span is listed back as a before/after
   pair** (`writing-style`, Revising the author's text). A rewrite was rejected as worse than the
   author's draft.
10. **Method names in the opening are in square brackets, each linking to its entry.** Parentheses
    were corrected.
11. **Each degree is two lines, and the current degree's line names the internships held during
    it.** A reader who stops at Education should see the strongest affiliations.
12. **Role lines read `Research Intern, mentored by A, B, and Dr. C`, in the full-size upright style
    of the education lines.** `Host` is not the genre's word, and small grey italics read as sparse.
13. **Titles are consistent and people's names are Latin in both languages.** A transliterated
    advisor name and an untitled doctor were both corrected.
14. **A research bullet is heading, tag, `[n]` jump and three or four sentences: contribution, then
    mechanism, then the strongest honest margin plus one efficiency figure.** Background openers,
    number lists, implementation detail and pasted abstracts were each rejected.
15. **Publications are numbered newest highest, with no legend on the page**, so ids never shift and
    nothing explains what the reader can see.
16. **The counts line is computed from the entries, sums correctly, carries no ambiguous token, and
    puts the owner's role (`Led ...`) in a sentence of its own.** `arXiv ×1` drew "refers to
    which?", and a role joined on with `and` read as "disgusting".
17. **Every title links to the accepted proceedings page (arXiv if none), and every entry ends with
    `[link]`.** The proceedings page is the record of acceptance, and the author asked for every
    entry to be clickable at both places.
18. **In the Chinese CV every publication entry is wholly English, and award and degree names are
    wholly Chinese.** Mixed-script entries looked pasted in.
19. **Pages are fitted by wording, then spacing, then margins, then line spread, then font size,
    and only then by cutting content.** Shrinking type is the visible failure, cutting is the
    invisible one.
20. **Every page runs to the foot (fill 93 to 98% on the last page) and no line holds a short tail**
    (one to three words, or one to four CJK characters with punctuation not counted), in every variant
    the repository builds, before the work is reported. Both were flagged in nearly every review
    round, and a tail reported as an open item instead of fixed drew the sharpest complaint.
21. **`\looseness=-1` is never used inside a ragged-right list or publication macro.** Under
    `\raggedright` it left an entry's first line holding only author names. In a justified paragraph
    it is the first layout lever for a short tail (it cleared three of four Chinese tails in a dense CV
    without moving any other line), and the fix is confirmed by re-running `check-cv.py`.
22. **Section rules sit about 3pt below the heading baseline**, checked on the render after any
    spacing change. A pulled-up rule overlapped every heading.
23. **Links are verified in the built PDF, and every `[n]` jump lands on its own entry in its own
    language.** Links checked only in the source shipped dead in the bundle.
24. **The bilingual bundle is English first, carries its links through a generated overlay or an
    explicit-GoTo merge, and checks its snapshots' MD5.** A plain `\includepdf` bundle had no working
    link at all.
25. **Every CJK font is guarded by `\IfFontExistsTF` with a Fandol fallback, and a local proof uses
    the Noto fonts Overleaf has.** Local PDFs shipped in a different face from the one reviewed.
26. **The Chinese file sets `\hyphenpenalty=10000` and leaves `\exhyphenpenalty` alone.** Blocking
    both made a hyphenated name overflow by 24pt.
27. **Each source names its engine on its first line, and Overleaf's compiler and main document are
    set to match.** A hard-coded engine built a half wrongly.
28. **Build outputs are ignored from the first commit and the bundle's `pdf/` snapshots are
    tracked.** Tracked artifacts pushed six files on every compile.
29. **The Overleaf token reaches git only through a credential helper**, never through a URL, a
    file in the repository or a transcript. A token in a remote URL lands in `.git/config` and in
    shell history, and from there in any log or transcript that prints them.
30. **Every number, venue and author list traces to the latest paper build, the table winning over
    the prose.** A paper's prose had swapped two values from its own table.
31. **CV prose passes the writer rounds `writing-style` sets and then an adversarial fact check, under
    a brief that freezes the facts and the length, and each suggestion is screened against the
    author's instructions.** A critique proposed undoing three of the author's explicit decisions.
32. **No institution or company logos; section icons, if any, are one generic family at text
    height.** Six logos never read as one set, and the author asked for generic icons in their
    place.

## Anti-patterns

- **The open defect.** The checker flags short tails in a variant nobody asked about, and they are
  reported as "still open" instead of fixed. It looks like deference and reads as stopping short:
  the fix takes one rebuild per tail, and the author has already said short tails are never wanted.
- **The shrunk two-pager.** A two-page layout scaled down until it fits on one. Tempting because it
  keeps every word, and it produces 7pt type, cramped bullets and a page nobody reads. Build the
  one-page variant for its size and move the excess to the dense variant.
- **The improved opening.** Replacing the author's research-focus draft with a "more insightful"
  version, from the agent or the writer tool. Tempting because the draft has rough grammar, and the
  author rejects the result and asks for his own text back.
- **The abstract bullet.** A bullet pasted from the paper's abstract or the talk's summary slide.
  Tempting because the facts are already checked, and it reads as copying and buries the mechanism.
- **The legend line.** `Numbered newest first`, `Bold = me`, an explanation of `[n]`. Tempting
  because it feels helpful, and it spends a line telling the reader what they can see.
- **The cloned Chinese file.** The English source with the strings translated. Tempting because the
  structure is already fitted, and it ships sparse CJK spacing, 7pt tags and translated prose.
- **The stapled bundle.** Two PDFs joined with `\includepdf` and nothing else. It compiles and looks
  right, and every link in it is dead.
- **The one-file fix.** A correction applied to the variant that was pointed at. The other variant
  and the other language keep the old fact, and an outside reader finds the mismatch.
- **The silent writer reversal.** Applying a writer critique wholesale. It reads as expert advice and
  quietly undoes what the author asked for.
- **The font that shrinks for a tail.** Dropping a paragraph to `\small` to pull up a one-word last
  line. It fixes the line and makes the page uneven, where deleting a filler word, or adding a
  clause the author wants, fixes both.
- **The logo strip.** Institution logos for visual weight. They never match in colour or resolution,
  and the author discarded them twice.

## Companions
`writing-style` (the English prose of the CV: punctuation, banned words, contribution statements,
the author's text kept, the writer's critique-and-revise rounds, and the sentence-level rules for a
short last line, under this skill's layout) · `writing-style-zh` (the Chinese prose of the CV:
native register, term choice, separators, 段末孤行 and 作者给定的文字) · `writing-chatgpt` (the writer
tool, its brief and how to patch its reply back) · `docs-slides` (the job talk or defence deck,
which quotes the same numbers and titles and must change with the CV) · `drawing-icons` (the one
generic icon family a variant may carry) · `naming-descriptive` (naming a CV family by what it is)
· `git-commit` and `git-push` (committing and, only on request, pushing to the Overleaf bridge) ·
`conventions` (the family map).
