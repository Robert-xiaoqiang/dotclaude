---
name: claude-skill-authoring
description: "Write or revise a skill in this family so every skill keeps one predictable shape: the required section spine, the frontmatter contract, and the voice that states why rather than only what."
when_to_use: "Use when creating a skill, turning repeated instructions into one, or restructuring one that has grown unreadable."
---
# Skill: claude-skill-authoring

## Purpose
Write and revise the skills in this family so they stay **one shape**. A reader who has read one skill
should be able to predict where anything is in the next: the same sections, in the same order, meaning
the same thing. This skill is the contract for that shape — it does no domain work itself, it says how
a skill is built, when a skill is the right container at all, and what makes one land.

It is the authoring counterpart to `conventions`, which is the *map* of the family. `conventions` says
which skill owns a concern; this says what a skill must look like once it does.

## Contents
- [When to Use](#when-to-use)
- [Is it a skill at all?](#is-it-a-skill-at-all)
- [The required spine](#the-required-spine)
- [Section contracts](#section-contracts)
- [When a TOC is required](#when-a-toc-is-required)
- [Voice: why, not just what](#voice-why-not-just-what)
- [The frontmatter contract](#the-frontmatter-contract)
- [Updating an existing skill](#updating-an-existing-skill)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Writing a new skill, or being asked to "turn this into a skill".
- Revising one that has grown past being readable — too many sections, no way in, sections that answer
  different kinds of question in different orders.
- Reviewing a skill someone else wrote, or auditing the family for drift.
- Deciding whether a piece of knowledge belongs in a skill, a project doc, or a code comment.

Not for the *content* of a domain skill. This file will not tell you what belongs in `naming-config`,
only how `naming-config` must be laid out.

## Is it a skill at all?

A skill is **reusable judgement that an agent needs before it acts**. Three tests, all of which must
pass:

1. **It generalises past one repo.** A rule about *this* project's directory names is a project doc
   (`docs/ARCH.md`) or `CLAUDE.md`. A rule about how any config-driven repo should name things is a
   skill.
2. **It changes a decision, not just a fact.** "The judge runs on port 8000" is a fact — put it in the
   config or the ledger. "Pass the judge a file path, never a URL, because a URL freezes a pod IP at
   submit time" is judgement, and it belongs here.
3. **It would otherwise be re-derived, wrongly, on a later day.** The strongest skills in this family
   are all scar tissue: each rule exists because something failed once and the failure was expensive
   and silent. If nothing goes wrong when the rule is unknown, it is documentation, not a skill.

If it fails (1), write a project doc. If it fails (2), write a comment where the value lives. If it
fails (3), write nothing — an unused rule is a cost.

## The required spine

Every skill has these sections, with these names, **in this order**. Anything specific to the domain
goes in the body, between `When to Use` and `Rules`.

```
---                            <- REQUIRED frontmatter; see the contract below
name: <name>
description: "..."
when_to_use: "..."
---
# Skill: <name>                 <- H1, exactly this form, matches the directory name

## Purpose                      <- REQUIRED, first
## When to Use                  <- REQUIRED, second
## Contents                     <- REQUIRED when long (see the TOC rule); sits after Purpose
<body sections>                 <- the domain: as many H2s as the subject needs
## Rules                        <- REQUIRED: the numbered, checkable list
## Anti-patterns                <- optional, but expected wherever failure modes have names
## Companions                   <- REQUIRED: the sibling skills and how they relate
```

Order is not cosmetic. `Purpose` and `When to Use` are the routing pair — an agent reads them to decide
whether to keep reading, so anything before them is read by someone who may not need it. `Rules` is the
part that gets re-read under time pressure, so it goes at a predictable depth from the bottom, not
buried mid-file. `Companions` last, because it is where you go when this skill was the wrong one.

Where `Contents` sits is fixed too: **after `Purpose`, before `When to Use`**. Purpose is one paragraph
and tells you if you are in the right file; the TOC is useless before it and in the way after
`When to Use`.

## Section contracts

Each section answers exactly one kind of question. Mixing them is the most common drift.

| section | answers | must NOT contain |
|---|---|---|
| `Purpose` | what this skill is for, in 2–5 lines | procedure, rules, examples |
| `When to Use` | the concrete triggers, as a bullet list, plus an explicit *not for* | explanation of the concepts |
| `Contents` | where things are | anything not a link |
| body | the actual knowledge: grammars, layouts, tables, worked examples | numbered rules (those belong in `Rules`) |
| `Rules` | numbered, checkable assertions — each one falsifiable | new concepts introduced for the first time |
| `Anti-patterns` | named failure modes, each with why it is tempting | fixes that are not stated elsewhere |
| `Companions` | sibling skills, one clause each on the boundary | domain content |

**`When to Use` always ends with what the skill is NOT for.** Every skill in this family that omits it
gets invoked for adjacent work and the reader ends up applying the wrong rules.

## When a TOC is required

Add `## Contents` when the file is **over 120 lines OR has more than 8 H2 sections**. Below that a
reader can scroll; above it they cannot, and the file starts being read by search instead of by
structure — which is how two sections end up saying different things without anyone noticing.

Link to H2s only. A TOC that lists H3s is a second outline to keep in sync, and it will drift.

## Voice: why, not just what

The rule and its reason travel together, in that order, and the reason is specific. This family's
working style is that a claim carries the evidence that produced it:

> **A launcher-only flag is a config masquerading as a flag.** A `mode=smoke` that quietly rewrites
> three trainer fields never appears in the run's frozen `config.yaml`, so two materially different
> runs look identical on disk.

not

> Avoid launcher-only flags. They are bad practice.

Where a rule came from a real failure, say what failed. "Four arms died with `judge unreachable: 16
endpoints x 3 attempts`" is worth ten lines of principle, because it tells the reader what the rule
*costs* to ignore and makes the rule memorable enough to survive.

Keep prose tight — see `writing-style`. Tables for anything with more than three parallel cases; prose
for anything with a because.

## The frontmatter contract

`description` is the ONLY way Claude decides to load a skill it was not asked for by name. Omit it
and the loader falls back to the first paragraph of markdown — which in this family is the H1, so
the skill advertises itself as `layout-workspace: Skill: layout-workspace`. That is a tautology: it
tells a reader nothing they did not already have from the name. All 22 skills sat that way until
2026-08-14, discoverable only by someone who already knew they existed, while 235 KB of bodies waited
to be found. A skill nobody can find is 100% waste no matter how good the body is.

Write the pair as **what it does**, then **when to reach for it**:

```yaml
---
name: <matches the directory>
description: "What it does, key use case first. State the mechanism, not the category."
when_to_use: "Use when <situation>, <trigger phrase>, or <the symptom that should send you here>."
---
```

- Put the **symptom** in `when_to_use` where one exists — "a run worked but wrote to the wrong place"
  finds `code-no-fallbacks` in a way "input validation" never will.
- `description` + `when_to_use` are truncated together at **1,536 characters** in the listing. Two or
  three sentences each; the listing is always in context, the body is not.
- `name` may be omitted (it defaults to the directory) but state it anyway — it makes the mismatch
  between H1, directory and `conventions` visible in one place.

**Arguments.** Without `$ARGUMENTS` in the body, whatever the caller passed is appended as
`ARGUMENTS: <value>`, which is fine for prose skills and is what this family relied on for a year.
Add `$ARGUMENTS` only when **placement** matters — the target has to appear before a checklist rather
than after it. Verified behaviour when a skill is invoked with nothing passed:

| placeholder | no args passed | args passed |
|---|---|---|
| `$ARGUMENTS` | empty string | the raw string, quoting preserved |
| `$name` (declared in `arguments:`) | empty string | that positional value |
| `$0`, `$1` | **stays literal** — `$1` reaches the model as text | shell-split value |

**Indexed `$0`/`$1` are therefore banned here.** An unfilled one leaks a literal placeholder into the
prompt and the model has to guess whether it is a variable, a literal, or noise — the same
silently-wrong-instead-of-loudly-absent shape `code-no-fallbacks` exists to kill. Use named
`arguments:` when position matters; they empty cleanly.

**Paths to bundled files use `${CLAUDE_SKILL_DIR}`**, never `~/.claude/skills/<name>/...`. `$HOME` and
`$CLAUDE_CONFIG_DIR` differ whenever Claude's state lives on shared storage, and this skill family
shipped a `~/.claude/skills/claude-migrate/migrate_session.py` that resolved to nothing on the very
box it was written on.

**Fields to leave alone.** `allowed-tools` grants tool permission for the whole turn — wrong for a
fleet that runs destructive operations. `disable-model-invocation` also removes the description from
context, so a safety-rule skill like `git-push` becomes *less* safe: the user says "push it" in prose
and the rules that say how to push safely are no longer loaded. `model`, `effort`, `context: fork`,
`user-invocable` have no use in this family yet.

## Updating an existing skill

1. **Read the whole file first.** Skills accrete, and the section you are about to add often already
   exists under another name three screens down.
2. **Put it in the section whose contract it matches**, not where the related words appear. A new rule
   goes in `Rules` even if the paragraph that motivates it lives in the body.
3. **Re-check the spine and the TOC.** Adding a section can push a file past the TOC threshold, and a
   TOC that misses a section is worse than none.
4. **Look for the contradiction.** If the new content is a correction, find and fix the old claim —
   two sections disagreeing is the failure this skill exists to prevent.
5. **Update `Companions` on BOTH sides** when a boundary moves. A one-way companion link is how two
   skills come to claim the same concern.

## Rules

1. **One concern per skill.** If `Purpose` needs "and" to describe two unrelated things, it is two
   skills. Split, and link them in `Companions`.
2. **The spine is mandatory and ordered.** `Purpose`, `When to Use`, `Rules`, `Companions` in that
   relative order, every time, even for a 14-line skill.
3. **`When to Use` states what the skill is NOT for**, explicitly.
4. **TOC over 120 lines or 8 H2s**, placed after `Purpose`, linking H2s only.
5. **Every rule is checkable.** A reader must be able to look at a repo and say whether it holds. "Be
   consistent" is not a rule; "two arms of an ablation differ in name only by the slots that describe
   the change" is.
6. **Every rule carries its reason**, and where one exists, the failure that produced it.
7. **The H1 matches the directory name**, and both match how `conventions` refers to it.
8. **YAML frontmatter is REQUIRED**, above the H1: `name`, `description`, `when_to_use`. The body
   header stays `# Skill: <name>` followed by `## Purpose`. See the frontmatter contract below for
   why, and for which other fields to leave alone.
9. **Cross-link, don't duplicate.** When another skill owns a concept, name it and move on. Two copies
   of a rule drift, and the reader cannot tell which is current.
10. **A skill that has never been used is deleted, not kept.** Dead rules make the live ones cheaper to
    ignore.

## Anti-patterns

- **The kitchen-sink skill.** Twelve H2s, no TOC, three of them overlapping. It is read by `grep`, and
  the parts stop agreeing. Fix: split by concern, or add the TOC and merge the overlaps.
- **Rules stranded in prose.** A hard constraint stated only in the middle of a body paragraph. Nobody
  re-reading under pressure will find it. Fix: state it in `Rules` and let the body motivate it.
- **The order shuffle.** `Rules` before `When to Use`, or `Purpose` after a body section. Each one on
  its own is harmless; together they mean the family has no shape and every file must be read fully.
- **Fact dressed as judgement.** A port number, a path, a model id. It goes stale silently and takes
  the skill's credibility with it. Facts live in config; skills say how to decide.
- **The one-way companion.** Skill A points at B, B has never heard of A. Both then grow into the same
  ground.
- **Rewriting instead of correcting.** Replacing a section wholesale loses the recorded reason for the
  old rule, and the next author reintroduces it.

## Companions
`conventions` (the family map — which skill owns which concern; this file says what a skill looks like
once it does) · `writing-style` (the prose these files are written in) · `naming-descriptive` (naming
the skill itself, and the things it describes) · `docs-plan` / `docs-arch` (where knowledge goes when
it is project-specific rather than reusable judgement).
