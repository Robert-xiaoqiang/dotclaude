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
python3 $CC2 make "FlowQ-Net generative quantum circuit design" --out new.bib
```

`--exact` uses the exact-title endpoint and is right when the title is known.
Without it, relevance search runs, which is right when only the method name,
an author and a rough topic are known. Always read back the matched title,
authors and year printed above each entry before using it.

### 2. audit, existing .bib to corrected .bib
```sh
python3 $CC2 audit claudetodo.bib --tex body.tex frontmatter.tex
```

Writes three files next to the input:

| file | contents |
|---|---|
| `cc2semantics.bib` | every entry, corrected where a record was confirmed |
| `cc2semantics.report.md` | side-by-side old versus new, grouped by verdict |
| `cc2semantics.report.json` | the same, machine-readable |

`--tex` marks which keys the manuscript actually cites, so attention goes to
the ones that matter.

## What counts as verified
A title match is a candidate, never a verdict. An exact-title query for
"Quantum machine learning" returns a 2025 arXiv preprint, not the 2017 Nature
paper an entry may claim. Confirmation needs the author list too.

| verdict | meaning |
|---|---|
| `VERIFIED` | title similarity at least 0.93 and a first-author surname in common and year within 2 |
| `REVIEW` | title between 0.78 and 0.93, or year off by more than 2 |
| `WRONG-RECORD` | title matches but no author overlaps, so the entry points at a different paper |
| `NOT-FOUND` | nothing above 0.78 from any source, the strongest hallucination signal |

The year tolerance of 2 exists because a preprint and its publication
legitimately differ, for example posted 2016 and published 2017.

A corporate author such as "Meta AI" has no surname to cross-check, so it is
accepted on title alone and the report says so.

**Preprints are preferred** when both a preprint and a published version exist.
An arXiv id is stable, free to resolve and always reachable, which is what a
reader needs. The published venue is kept in the entry.

## Output contract
`cc2semantics.bib` is written beside the source and **the source is never
modified**. Entries that came back `NOT-FOUND` or `WRONG-RECORD` are carried
through byte-identical, because inventing a replacement is the exact failure
this skill exists to catch. Those are listed in the report for a person to
decide.

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
2. **Read the matched title and authors before accepting an entry.** The tool
   reports what it matched precisely so that this check is possible.
3. **Never auto-replace a `NOT-FOUND` or `WRONG-RECORD` entry.** Surface it.
4. **The source `.bib` is read-only.** Output goes to `cc2semantics.bib`.
5. **Prefer the preprint id** when both exist.
6. **Rerun after editing the `.bib`.** The cache makes it cheap.

## Anti-patterns
- **Title-only verification.** Certifies the wrong paper whenever two works
  share a title, which is common for short generic titles.
- **Treating 429 as failure.** It means later. Backing off and retrying
  resolves almost everything.
- **Auto-fixing everything.** The entries the audit cannot confirm are exactly
  the ones a person has to look at.
- **Clearing the cache between runs.** Turns a free rerun into a rate-limited
  one.
