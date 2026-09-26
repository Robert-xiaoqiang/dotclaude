---
name: cc2bib
description: Resolve and audit BibTeX against Semantic Scholar, arXiv and Crossref. Use when writing a citation, when a .bib may contain hallucinated or wrong entries, or before submitting a paper.
---

# Skill: cc2bib

## Purpose
A citation an agent writes from memory is a guess. The title is plausible, the
authors are plausible, the year is plausible, and the paper does not exist, or
exists with different authors. This skill replaces guessing with a lookup
against Semantic Scholar, arXiv and Crossref, in both directions: resolving a
description into a correct entry, and auditing a `.bib` that already exists.

## Contents
- [When to Use](#when-to-use)
- [The two scenarios](#the-two-scenarios)
- [What counts as verified](#what-counts-as-verified)
- [Output contract](#output-contract)
- [Rate limits and robustness](#rate-limits-and-robustness)
- [Usage](#usage)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)

## When to Use
- Writing a paper and needing to cite a work known only by description, such as
  "the LLaDA diffusion language model paper" or "Zoph and Le's NAS paper".
- Any `.bib` an agent has contributed to, before the paper is submitted or
  shared.
- A reviewer or co-author questions a reference.
- Not for: formatting or style of an existing correct entry, or choosing which
  papers to cite. This skill checks that a citation points at a real work, not
  that the work supports the claim.

## The two scenarios

### 1. make, description to entry
Given free text, return the entry and the resolvable URL.

```sh
CC2=$CPFS_HOME/.claude/skills/cc2bib/scripts/cc2bib.py
python3 $CC2 make "large language diffusion models LLaDA" --limit 3
python3 $CC2 make --exact "Attention is all you need"
python3 $CC2 make --exact "Attention is all you need" --diff \
    --author "Vaswani, Ashish and Shazeer, Noam and ..." --year 2017
python3 $CC2 make "FlowQ-Net generative quantum circuit design" --out new.bib
```

An entry is emitted only for a record whose normalised title equals the query.
Relevance search is for finding a work from a description; when no hit has the
query's exact title, the hits are listed as candidates and nothing is emitted,
so the next step is `--exact "<the title you mean>"`. Several works under one
exact title are reported as ambiguous until `--author` picks one. `--author`
and `--year` add the strict author-order and year check of an audit, and
`--diff` prints the claim and the record side by side. The header of each
emitted entry says which of title, authors and year were checked.

### 2. audit, existing .bib to corrected .bib
```sh
python3 $CC2 audit claudetodo.bib --tex body.tex frontmatter.tex
python3 $CC2 audit custom.bib --keys ouyang2022training --diff all   # one entry, side by side
python3 $CC2 audit custom.bib --diff mismatch                         # every failure, side by side
```

Writes three files next to the input:

| file | contents |
|---|---|
| `cc2semantics.bib` | every entry, corrected where a record was confirmed |
| `cc2semantics.report.md` | side-by-side old versus new, grouped by verdict |
| `cc2semantics.report.json` | the same, machine-readable |

`--tex` marks which keys the manuscript actually cites, so attention goes to
the ones that matter. `--keys` restricts the audit to named entries, which is
how a reviewer or a subagent works through a bibliography one entry at a time.
`--diff mismatch` or `--diff all` prints each entry beside its nearest record,
one author per row, marked `=` identical, `~` same up to diacritics or initial
format, `!` different, `+` present on one side only. The markdown report
carries the same table for every entry that is not VERIFIED.

## What counts as verified
A title match is a candidate, never a verdict. An exact-title query for
"Quantum machine learning" returns a 2025 arXiv preprint, not the 2017 Nature
paper an entry may claim. A relevance query for SOTOPIA returns SOTOPIA-π, and
a Crossref query for the InstructGPT title returns "InstructPatentGPT:
training patent language models to follow instructions with human feedback".
The earlier matcher accepted the nearest fuzzy title (similarity 0.84 in both
cases) together with any one shared surname, and wrote the wrong paper into
the corrected file. Matching is now exact on three fields, and nothing else
counts.

| field | accepted only when |
|---|---|
| title | the normalised titles are identical. Normalising folds case, LaTeX braces and commands, accents, greek letters (`$\pi$` and `π` both read `pi`) and punctuation, and nothing else, so a dropped or changed subtitle, or a suffix such as `-π`, is a mismatch |
| authors | the full lists have the same length and agree position by position on surname and given names, where only diacritics and initial format may differ (`Sandhini`, `S.` and `S` agree; `Jeff` and `Jeffrey`, or `Chong` and `Chen`, do not). A list cut short with `and others` cannot be confirmed |
| year | the claimed year is the record's year, or the posting year of the record's arXiv id |

| verdict | meaning | written back |
|---|---|---|
| `VERIFIED` | title, full author list in order and year all agree | yes, the record replaces the entry |
| `NOT-CITABLE` | a blog post, model card, repository or bare URL, checked before any lookup | no |
| `TITLE-WRONG` | the entry's own arXiv id resolves to a paper with the same authors and a different title | no |
| `MISMATCH` | the nearest record differs in title, authors or year; the report names which, shows both side by side, and marks each author row | no |
| `NOT-FOUND` | no candidate from any source, or none close even in wording, the strongest hallucination signal | no |

Fuzzy title similarity survives only to choose which non-matching record to
show beside a `MISMATCH`; it never accepts anything. A `MISMATCH` whose only
difference is the year is usually a preprint posted one year and published the
next. The person resolving it picks the year, the tool does not.

A corporate author such as `{Qwen Team}` is compared as one name like any
other, so it verifies only against a record that carries the same corporate
name, and otherwise comes back `MISMATCH` for a person to settle.

## Web sources are not citations
A blog post, a model card, a repository or a bare URL is not a citable source.
It has no authors of record, no venue, no version a reader can pin, and nothing
to verify against, and its content can change or disappear after the citing
paper is published. Entries like these are reported as `NOT-CITABLE` before any
lookup runs, because there is nothing to look up.

Almost always the thing being cited does have a paper, and that paper is what
belongs in the bibliography. A table row reading `Llama-3.2-3B` cited a Meta
blog post; the Llama 3 herd paper says the same thing and can be checked. When
no paper exists, the right move is usually to name the artefact in the text and
drop the citation, not to cite the URL.

An entry carrying an arXiv id or a DOI is never `NOT-CITABLE`, whatever its
venue string says, because it has a real identifier behind it.

**Preprints are preferred** when both a preprint and a published version exist.
An arXiv id is stable, free to resolve and always reachable, which is what a
reader needs. The published venue is kept in the entry.

## Output contract
`cc2semantics.bib` is written beside the source and **the source is never
modified**. Only `VERIFIED` entries are rewritten. Every other entry is carried
through byte-identical, because a near miss written over a real reference is
the exact failure this skill exists to catch. Those entries are listed in the
report, beside the nearest record, for a person to decide.

Applying the result is a separate, deliberate step: read the report, then
replace the old `.bib` and, where a key changed, substitute it across the
manuscript sources.

## Rate limits and robustness
The Semantic Scholar free tier documents one request per second cumulative
across all endpoints, with the key sent as an `x-api-key` header. Measured
behaviour is worse and erratic, because the quota is shared and a proxied host
competes with others: at a 2.5 s gap only one call in five returned 200.

The client is therefore retry-driven, not schedule-driven. A 429 means "later",
never "no", so it backs off exponentially with jitter up to 45 s and retries
seven times. Every resolved query is cached under `~/.cache/cc2bib`, so a rerun
costs nothing and an interrupted audit resumes. arXiv and Crossref stand behind
Semantic Scholar, so an outage degrades the audit rather than stopping it.

Two transport details that cost an hour to find. arXiv returns 406 if the colon
in `ti:` is percent-encoded, so the field prefix stays literal. And through a
local proxy `urllib` succeeds on its first call and returns 406 on every later
one, so each request is a fresh `curl` process.

Tune with `CC2BIB_MIN_GAP` (default 1.6 s) and `CC2BIB_CACHE`.

## Usage
The key lives in `$CPFS_HOME/.secret` as `SEMANTIC_SCHOLAR_API_KEY` and is read
from the environment or that file. Rotating it means editing that one line; the
cache stays valid because it is keyed by query, not by credential. Without a
key the skill still runs on arXiv and Crossref alone, with weaker venue and
author coverage.

## Rules
1. **Never hand-write a citation this skill can resolve.** A plausible entry
   written from memory is the failure mode.
2. **Accept only an exact match on all three fields.** Identical normalised
   title, the full author list in the same order, and the same year. A
   subtitle difference, a missing, extra or reordered author, or a changed
   given name is a mismatch, whatever the similarity score.
3. **Never auto-replace anything but `VERIFIED`.** `MISMATCH`, `TITLE-WRONG`,
   `NOT-FOUND` and `NOT-CITABLE` are surfaced side by side, never written over.
4. **The source `.bib` is read-only.** Output goes to `cc2semantics.bib`.
5. **Prefer the preprint id** when both exist.
6. **Rerun after editing the `.bib`.** The cache makes it cheap.
7. **Review a failure with `--diff`, one entry at a time with `--keys`.**
   The per-author rows show where a list diverges, which a one-line verdict
   cannot.

## Anti-patterns
- **Title-only verification.** Certifies the wrong paper whenever two works
  share a title, which is common for short generic titles.
- **Nearest-hit acceptance.** Taking the closest fuzzy title, or the first
  relevance hit, as the paper. It replaced SOTOPIA with SOTOPIA-π and
  InstructGPT with InstructPatentGPT, both at similarity 0.84. A near title is
  a different paper until every field says otherwise.
- **First-author or any-surname checks.** One shared surname says nothing
  about the rest of the list, and a set of surnames ignores order. Compare the
  whole list, position by position.
- **Tolerances on the accept path.** A similarity threshold, a year window or
  a partial author overlap turns "close" into "confirmed". Tolerance belongs
  only in normalisation (case, braces, accents, punctuation, initial format).
- **Completing an `and others` list silently.** The record's full list may be
  right, but the entry did not claim it; resolve it by hand from the report.
- **Treating 429 as failure.** It means later. Backing off and retrying
  resolves almost everything.
- **Auto-fixing everything.** The entries the audit cannot confirm are exactly
  the ones a person has to look at.
- **Clearing the cache between runs.** Turns a free rerun into a rate-limited
  one.
