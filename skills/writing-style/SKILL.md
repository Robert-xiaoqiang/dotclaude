---
name: writing-style
description: "The user's rules for English documents, covering punctuation, the words and sentence shapes that read as generic AI prose, how a method and a contribution are named, and how the author's own draft is kept when revising it. Covers the written deliverable, not its argument and not the way you talk in session."
when_to_use: "Use when producing or revising an English document the user will keep or publish, such as a paper, report, README, research statement, CV or slide text. Also use when a draft carries em-dashes, slogans, trailing 'so X rather than Y' tails or a 'what was taught' where a noun belongs, when a paragraph ends on a line of one to three words, when the author hands over a paragraph of their own to fix, or when a correction flagged on one page has to reach the rest."
---
# Skill: writing-style

## Purpose
The user's style rules for English documents. They cover punctuation, the words and sentence shapes
that read as generic AI prose, how a method or a contribution is named, and how a passage the author
wrote is handled during revision. They do not cover what a document argues, which belongs to the
document's own skill, and not the way you talk in the session.

## Contents
- [When to Use](#when-to-use)
- [Punctuation and layout](#punctuation-and-layout)
- [Words to avoid](#words-to-avoid)
- [Sentence shapes to avoid](#sentence-shapes-to-avoid)
- [Naming the method and the contribution](#naming-the-method-and-the-contribution)
- [Revising the author's text](#revising-the-authors-text)
- [Polishing through the writer tool](#polishing-through-the-writer-tool)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Writing or editing a standalone English document the user will keep or publish, such as a paper,
  report, article, README or other repository documentation, design doc, proposal, research
  statement, CV, or the text and speaker notes of a deck. If the text is itself the thing being
  delivered, these rules apply.
- A research paper. Every rule here applies, and `writing-paper` adds what these rules do not reach,
  namely where a citation attaches, how related work is grouped, and how a section leads with its
  finding rather than its topic. Read both.
- Revising a passage the author wrote, or carrying a correction the author flagged on one page
  through the rest of the deliverable.
- Not for session replies or anything conversational in the chat. Not for commit messages, PR
  descriptions and other version-control text (`git-commit`). Not for code, code comments, config
  or data the user asked to see in a given shape, or for logs and terminal output. Not for Chinese
  deliverables (`writing-style-zh`). Not for what a deck or a CV contains and how it is laid out
  (`docs-slides`, `docs-resume`), or for the mechanics of the writer tool (`writing-chatgpt`). If you
  are not producing a document the user will save or share, assume these rules do not apply.

## Punctuation and layout
In finished documents the user wants writing that reads like continuous, spoken prose rather than
punctuation-heavy or list-chopped text. Em-dashes, semicolons, stacked colons and reflexive bullets
fragment a paragraph and read as a generic AI default. Chat and logs are working text, not
deliverables, and are deliberately left alone.

An em-dash or en-dash ("—", "–") used as clause punctuation becomes a comma, a pair of parentheses,
or two sentences. An en-dash inside a numeric or date range (pp. 12–18, or `YYYY.MM -- YYYY.MM` in
LaTeX source) is range typography, not a dash, and stays. A semicolon becomes two sentences, or a
comma and "and" or "but". A ", so" join is allowed only when the clause it opens names the mechanism,
as the trailing tail under Sentence shapes to avoid explains, which is why it is not the default
repair.

What you would have bulleted becomes ordinary sentences unless the user asked for a list. A format
that is a list by nature, such as a CV's entries or a slide's bullets, follows `docs-resume` or
`docs-slides`. The ban is on bulleting an argument that belongs in prose. A colon that sets up an
explanation or a list becomes a plain sentence, while a colon in front of a short quoted term, a path
or a ratio is fine.

The interpunct `·` is not a separator anywhere in a deliverable, in bylines, headers and lists of
names as much as in body text. Put one fact per line or use a comma. A byline, for example, is the
name with the date on the next line. A CV contact line, which has to stay on one line, uses the
spaced pipe that `docs-resume` sets (`\quad|\quad` in LaTeX). The ban was first recorded for slides
only (`docs-slides`), and the dot kept reaching CV headers and document bylines that no rule covered.

**A short last line is fixed by cutting words, never claims.** A paragraph whose last line holds one
to three words wastes a line, and the author flagged such lines on CV pages more than once. Tighten
the paragraph by deleting a word that carries no claim, then re-read each sentence to confirm its
claim did not change. Dropping a qualifier to save the line changes what the sentence asserts.
`docs-resume` owns the CV line-fit procedure and the check that finds these lines in a built PDF, and
`writing-style-zh` has the Chinese form as 段末孤行.

## Words to avoid
Some words read as generic AI or corporate filler in a finished document. Prefer the plain word. This
is a short curated set, not an exhaustive ban.
- `delve into` becomes look at or examine.
- `leverage` and `utilize` become use.
- `showcase` becomes show or demonstrate, and `underscore` becomes highlight.
- `testament to` becomes shows or proves.
- `seamless` becomes smooth or without friction.
- `game-changer` and `cutting-edge` become a plain statement of what changed or what is new.
- `boasts` becomes has, `in order to` becomes to, and `due to the fact that` becomes because.
- `embark`, `realm`, `tapestry`, `ever-evolving`, and `navigate the complexities` get rewritten in
  plain words.
- `substrate`, used as a metaphor, becomes base, foundation, or layer.
- `together`, `taken together`, and `collectively`, as a summarizing opener, get cut. State what the
  evidence shows.
- `moving forward` becomes next, or name the actual time.
- `landscape`, used as a metaphor, becomes field or area.
- `pivotal` becomes key or important, or a plain statement of what it changed.
- `ledger`, used as a metaphor for a record of what happened, becomes record, log, or the name of
  the actual file. Reserve the word for double-entry bookkeeping.
- `ladder` and `rung`, used as a metaphor for an ordered set of comparisons or difficulty levels,
  get rewritten as the ordering itself. Say which arms differ by what, or name the levels. This
  binds a table's row labels too. A column of `rung 0 / rung 1 / rung 2` is the metaphor wearing a
  header, and the fix is to label each row with the thing that actually varies down the column.
- `ruler`, `crutch`, `channel`, `reading`, `threshold` and the rest of that family, used for an
  object that already has a name, become that name.
- `projected`, `estimated`, `derived` and `simulated`, used as a **bare source tag on a number
  nobody measured**, become a statement of what happened: `not run, scaled from <source>`. A
  one-word tag names a technique, so the column reads as two kinds of result and the reader cannot
  see that one of them was never run. The words are fine in their ordinary sense, and the ban is
  only on using one as the label in the column that says where a number came from. This wording is
  for reports and plans. In a deck the row is removed instead, because `docs-slides` keeps run
  status off the slide and out of its notes.
- `hygiene`, used as a metaphor for keeping something tidy (code hygiene, language hygiene),
  becomes the practice itself. Say what is checked and what fails the check, because the metaphor
  is what lets a section promise a standard without naming one.
- `provenance`, used as a vague label for where a claim came from, becomes the source itself, the
  run that produced it or the paper that reported it. Keep the word where it names a recorded
  artifact that exists, a provenance manifest or the hash a run writes into its own config, and see
  the `projected` entry for the tag on an unmeasured number.
- `commit and push`, fused into one instruction in a plan, runbook or README, gets split. They are
  two decisions, and the second one publishes. A document that welds them tells whoever reads it
  next, human or agent, to push without anyone deciding to. Write the commit as the step, and give
  the push its own line and its own reason.

Technical terms keep their meaning. Words like robust, comprehensive, significant, novel, scalable,
and state-of-the-art carry a precise claim in scientific and ML writing, for example robust to
outliers, statistically significant, and a comprehensive benchmark. Use them freely when they make a
real technical point. Avoid them only when they are vague praise, and never drop a correct technical
term just to dodge a filler word.

## Sentence shapes to avoid
Each shape below sounds finished and leaves the reader with less than the sentence promised.

- **Negation pivot.** "It is not just X, it is Y" and "this is not about X, it is about Y". State
  the claim directly.
- **Reflexive rule of three.** Do not default to triples, whether an "adjective, adjective, and
  adjective" phrase or a three-item list. Vary the grouping or use a plain sentence.
- **Hollow intensifiers and hedges.** Cut `genuinely`, `truly`, `really`, `it is worth noting`,
  `it is important to note`, `to be clear`, `perhaps`, and `arguably`, then state the point.
- **Vague endorsement.** "Worth noting" or "worth exploring". Give the specific reason something
  matters.
- **Sweeping "from X to Y" openers.** Name the actual scope instead.
- **The trailing tail.** A closing clause that restates its sentence ("..., since moving any one of
  them alone trades one failure mode for another"), or that claims a consequence or contrast the
  sentence never established ("..., so cost tracks usefulness rather than trajectory length",
  "which is what keeps the loop productive rather than saturating"). These tails sound like insight,
  and the causal link between the two halves is asserted, never shown. The author called them
  useless trailing explanation, a cause statement with no explicit reason between its halves. Give
  the mechanism and its measured effect a sentence of their own, or cut the clause.
- **A wh-clause standing in for a noun.** "What was taught", "how it was judged", "what is worth
  remembering", and as labels or headings "What must be true" or "What counts as gold". The reader
  has to turn the question into the thing meant, and the phrase stays vague. Name the object, such
  as the training data, the reward, the stored content or a gold-trace taxonomy. The test is whether
  the phrase could take a question mark and stand alone as a sentence. This is the English form of
  疑问词当名词 in `writing-style-zh`, and it kept reaching CV openings and slide labels while only the
  Chinese skill banned it.
- **Slogans and aphorism pairs.** "Building X is now routine. Deciding whether it did Y is not." "One
  task is a paper cut in half." "A new paradigm for model scaling" hung on a sentence as a dangling
  apposition. Each compresses before the distinction is made, the premature-compression failure
  `writing-chatgpt` names, and the author's answer to a page of them was to ask what its logic was.
  State the claim formally, with its subject and its evidence, or delete it. A slide made of such
  lines is the slogan page that `writing-chatgpt` describes.
- **Prepositions between numbers.** Prepositional shorthand between two numbers is a visibly
  non-native construction, and the reader cannot tell which quantity the preposition attaches to.
  Write a full clause that names the quantity, the comparison object and the direction.

  | ✗ | ✓ |
  |---|---|
  | N× faster at M% fewer steps | an N× speedup with M% fewer decoding steps |
  | at K% fewer tokens | while using K% fewer tokens than BaselineY |
  | an a% spread at recall against b% at problem-solving | the gap was only a% for recall but reached b% for problem solving |

- **The document explaining itself.** A line that explains the document's own conventions or
  announces what the reader is about to see, such as "Numbered newest first", "My name appears in
  bold", "the [n] tags cross-reference this list", "Papers this talk is built on" or "This section
  covers ...". The reader can already see the numbering, the bold and the heading, and the author
  deleted every such line on sight. A deck's outline page (`docs-slides`) and a method section's
  opening overview (`writing-methodology`) state content, not conventions, and stay.
  `writing-style-zh` has the same rule as 不写文档自述.

## Naming the method and the contribution
The writer has the codebase and the drafts open, and the reader has neither. Most naming failures
come from writing in the first context for a reader who is in the second.

**Name operations, not qualities.** A method described as a stack of rare abstract nouns
("machine-checked contracts for provenance, budget honesty, determinism and split hygiene") sounds
rigorous and names no mechanism. The author's verdict on that line was rare words and concepts that
make no sense. Name operations a reader can picture, such as defining an interface, letting the loop
rewrite its implementation, or testing on a held-out split. A coined abstract-quality noun that
neither the field nor the document defines is replaced by the operation it stands for. A standard
term of the field, or a term the paper defines (a Horvitz-Thompson correction, say), passes.

**Internal vocabulary stays internal.** Codebase metaphors (a palace, a tape, "layered"), nicknames
of modules inside the method, draft dates and the section names of internal reports never reach an
external deliverable. Describe the method by what it does ("stores at several granularities, read
under an evolving policy") and by the mechanisms the paper itself names. `writing-style-zh` has the
Chinese form as 内部报告的结构和词都不进对外文档.

**Contribution statements, not an oral explanation.** In a CV entry or a research-statement
achievement, each contribution line opens with a technical verb and names what the work does or
improves. Narrative verbs and physical metaphors read as a talk transcript and as translated English.
An external critique of a CV made this point and the author adopted it as a rule. The order of the
parts within a CV bullet belongs to `docs-resume`, an abstract's opening to `writing-paper`, and a
slide bullet to `docs-slides`.

| ✗ oral explanation | ✓ contribution statement |
|---|---|
| Gave memory its own parameters | Introduced a parameterized memory module decoupled from the base agent |
| Made X reversible | Designed a reversible X |
| keeps learning productive as the policy climbs | preserves reward discrimination as the policy improves |
| what makes it cheap | reduces inference cost |

**One term for the contribution.** Use the term the paper defines, for example
`training-time harness`, with one spelling per document, in the CV entry, the deck title and the
abstract alike. The paper's English term may be kept inside the Chinese version, and is never
half-translated (`writing-style-zh`). A generic role word (`controller`, `control harness`)
undersells it, and the author rejected both as low-excitement words. A variant spelling
(`train-time`) splits one concept into two search strings. Paired terms stay symmetric, so
inference-time goes with training-time, never test-time on one side and train-time on the other.
The author's frozen text wins over this rule. It governs text the agent writes and the entry or
title that names the contribution, and a sentence the author wrote with another phrase for the same
work stays as written.

**A tagline is one sentence.** A repository or product tagline states what the tool does that the
alternatives do not, with no implementation words (`plain-text`, `lint`). It may carry one metaphor,
and the author asked for one ("one compile, all running"). Re-check it whenever the product changes.
A negation tagline ("Not X. Not Y.") became false on the day the tool gained the backends it denied.

## Revising the author's text
**Text the author wrote or approved is frozen.** When the author supplies a paragraph, paste it
verbatim. By default only grammar and agreement change. When the author asks for more, a polish, a
named phrase or a fit to the line, that request is the scope and nothing beyond it changes. Every
changed span is listed back to the author as a before/after pair. When the author proposes a phrase,
adopt it or say why not, never substitute your own in silence. Editing a neighbouring span is no
licence to touch an approved one, and an approved span gets no explanatory filler. Twice an agent
replaced the author's draft with its own version, the author judged the result worse, and the
original had to be restored.

**A correction applies to the whole deliverable.** When the author flags one instance of a pattern
(a banned word, a separator, a title shape, a symbol, a renamed concept), grep the whole deliverable
and fix every instance in the same pass, figures, outline, footers and notes included. If the fix is
a new rule, add it to the skill that owns it, reload that skill and re-run it over all the text
before reporting. Report how many instances changed. The same flags came back round after round
(你又忘了 and 说了多少遍了, "you forgot again" and "how many times have I said it") because each fix
touched only the page that had been pointed at.

## Polishing through the writer tool
`writing-chatgpt` owns the writer tool's mechanics, which are what to hand it, which task to pick and
how to diff its reply. The decisions below, about when to use it and how far to trust a reply, are
recorded here until that skill carries them.

**Rewritten deliverable text goes through the writer.** When the agent writes or rewrites text that
goes into a deliverable, the writer polishes it before the author sees it. The author's words were
that any rewrite has to pass the writer, and the question after a wordy line was whether the writer
had been asked. The author can switch this off for a task, and the switch holds until the author
lifts it.

**Two rounds, then accept.** Critique the text with the writer, revise, then critique and revise
again before accepting. The author asked for this sequence by name ("critique again, revise again"),
because a single pass leaves whatever the first revision introduced.

**Reject what the writer should not have touched.** A reply that rewrites a frozen span, expands a
dictated sentence or adds explanatory filler is rejected for that span, and the author's text goes
back in. The author's reaction to an expanded dictated line was 谁让你展开重写的 ("who told you to
expand and rewrite it").

**The author's "I" survives the writer.** The writer's English prompt is written for papers, where
the first-person singular is wrong. A CV or research statement written as "I" says so in the
request, and the reply is checked for drift to "we".

## Rules
1. **No em-dash or en-dash as clause punctuation**, neither "—" nor "–". They fragment a paragraph
   and are the most recognisable AI default. An en-dash inside a numeric or date range (pp. 12–18,
   LaTeX `--` between dates) is range typography and stays.
2. **No semicolons.** Two sentences, or a comma and "and" or "but", carry the same relation.
3. **No bulleted or numbered lists in prose unless the user asked for one.** A list strips the
   relations out of an argument. A format that is a list by nature, a CV's entries or a slide's
   bullets, follows `docs-resume` or `docs-slides`.
4. **A colon only before a short quoted term, a path or a ratio.** One that sets up an explanation
   fragments the paragraph as the dash does.
5. **No interpunct `·` as a separator**, in bylines and headers too. It reached CV headers while the
   ban covered only slides. A CV contact line uses the spaced pipe that `docs-resume` sets.
6. **Every entry in Words to avoid is replaced, and no correct technical term is dropped to dodge
   one.** Filler reads as AI default, while a technical `significant` carries a claim.
7. **No negation pivot, reflexive triple, hollow intensifier or hedge, vague endorsement, or
   sweeping "from X to Y" opener survives a final read.** Each sounds finished and says less than it
   promises.
8. **No sentence ends in a restating or unsupported tail.** Every hit of `, so `, `rather than`,
   `instead of` or `which is what` that survives has its mechanism in the text, because the tail
   otherwise asserts a link it never showed.
9. **No wh-clause stands in for a noun, a label or a heading.** A phrase that could take a question
   mark and stand alone is rewritten as the noun it points at, so the reader need not translate it.
10. **No slogan or aphorism pair replaces an argument.** A slogan compresses before the distinction
    is made, and a slide made of them is the slogan page `writing-chatgpt` names.
11. **Each number comparison is a full clause** naming the quantity, the comparison object and the
    direction. Shorthand like `at M% fewer` is ambiguous and visibly non-native.
12. **No line explains the document's conventions (numbering, bold, tags) or announces what the
    reader is about to see.** The reader already sees them. A deck's outline page and a method
    section's overview state content and are exempt.
13. **A method is described by operations a reader can picture, with no coined abstract-quality noun
    that neither the field nor the document defines.** Abstract-quality stacks sound rigorous and
    name no mechanism, while a standard field term or one the paper defines passes.
14. **Internal vocabulary never reaches an external deliverable.** Codebase metaphors, module
    nicknames, draft dates and internal report section names all stay out, because the reader lacks
    the context they need.
15. **A contribution line in a CV entry or research statement opens with a technical verb and names
    a measurable property**, never a physical metaphor. Narrative verbs read as an oral explanation
    in translated English.
16. **The contribution has one name**, the paper's own term, with one spelling per document and
    paired terms symmetric. A reader searching for it should find one string. The author's frozen
    text wins over this rule, which governs text the agent writes and the entry or title that names
    the contribution.
17. **A tagline is one sentence with the selling point and no implementation words**, re-checked
    whenever the product changes. A negation tagline went false once the product gained what it denied.
18. **The author's text is frozen.** Only grammar and agreement change unless the author names a
    wider scope (a polish, a phrase, a line fit), every changed span is listed back as a before/after
    pair, and a proposed phrase is adopted or answered. Agent rewrites of an author's draft were
    judged worse and reverted.
19. **A correction reaches every instance in one pass, and the report gives the count.** Fixing only
    the flagged page is why the same flags returned round after round.
20. **A last line of one to three words is fixed by cutting a word that carries no claim**, never by
    changing the claim, and every sentence is re-read afterwards. A dropped qualifier saves the line
    and changes what the sentence asserts.
21. **Rewritten deliverable text passes the writer and two critique-and-revise rounds before it is
    accepted, unless the author has switched the writer off**, and a reply that touches a frozen
    span or adds filler is rejected for that span. The author asked for each pass, and asked whether
    the writer had been used when it had not.

## Anti-patterns
- **The insight tail.** A ", so X rather than Y" closing a sentence. Tempting because it makes a
  plain statement sound as if it understood something.
- **The rigorous-sounding stack.** Four abstract nouns where one mechanism belongs. Tempting because
  each noun is defensible alone and the list sounds thorough.
- **The question as a noun.** "What was taught" in place of the training data. Tempting because it
  spares the writer from deciding which object is meant.
- **The house metaphor.** The codebase's name for a component, used in a paper or a CV. Tempting
  because the writer has said it for weeks and no longer hears it as private.
- **The silent substitution.** The author's paragraph replaced by an "improved" version. Tempting
  because a rewrite feels like more help than a grammar fix.
- **The one-page fix.** Only the flagged instance corrected. Tempting because the request named one
  page, and the same flag comes back next round.
- **The claim trimmed for a line.** A qualifier deleted to pull a one-word last line up. Tempting
  because the page looks clean at once, and the sentence now claims more than it did.

## Companions
- `writing-style-zh` (the Chinese sibling, the same job with Chinese punctuation and its own word
  list. This skill does not govern Chinese deliverables.)
- `writing-paper` (the paper layer, which adds citation placement, related work and section openers)
- `docs-slides` (deck register, slide titles and labels, and speaker notes that must be speakable
  aloud, on top of these rules)
- `docs-resume` (CV layout, the one- and two-page versions, the English and Chinese pair, the
  line-fit check and the order of the parts within a contribution bullet, on top of these rules)
- `docs-weekly` (the staged weekly report)
- `writing-chatgpt` (the writer tool's mechanics, which are what to hand it, which task to pick and
  how to diff its reply. Its English prompt encodes the punctuation and word rules only, so check
  the sentence-shape and naming rules on its reply yourself.)
- `conventions` (the family index)
