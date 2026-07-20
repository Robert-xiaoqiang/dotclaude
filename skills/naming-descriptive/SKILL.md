# Skill: naming-descriptive

## Purpose
Name every *durable* artifact by **what it is** — the design / feature / module
and its core point — never by an opaque sequence ID (`v1/v2/vX`, `P0/P1/Px`,
`step1/phase2`, `draft_final_FINAL`). A name should let a reader predict the
content without outside context. Sequence IDs are allowed only as *ephemeral*
labels while talking (chat, console, an in-progress ticket) to organize a
dialogue — they must not be baked into anything that persists.

## When to Use
- Building a multi-step feature / design roadmap and committing checkpoints
- Naming: commits, branches, files & dirs, docs / reports / titles, modules,
  classes, functions, configs, experiments/runs, schemas/migrations
- The user lays out work as "P0..Pn" or "v1..vn" → translate each to a name that
  describes the change, keeping the Px/vX only in conversation
- Reviewing names that are version/phase numbers instead of descriptions

## The rule
- **Describe, don't number.** Name the change, not its position in a sequence.
- **Durable → descriptive. Ephemeral → an ID is fine.** Persisted name = meaning;
  throwaway chat label = ordering is OK.
- **One change, one name that states the change.** "Typed pydantic config with
  provider registry" — not "Phase 0" or "config v2".

## Examples (bad → good)
- commit `P0: config` → `Typed pydantic config with provider registry`
- branch `feature/phase1` → `self-evolving-memory`
- file `DESIGN-v2.md` → `self-evolving-memory.md` (name the subject)
- report `REPORT_v3_final.md` → name what the report covers
- function `process2()` → `consolidate_summaries()`
- doc `notes-draft-final-FINAL.md` → the document's actual subject (+ a date if needed)

## Allowed exceptions
- **Talking, not persisting:** use `P0`/`v2`/`step3` freely in chat/console/PR
  discussion to keep the conversation organized — then commit/name the artifact
  descriptively.
- **Real releases:** semantic versions on *published* releases are a contract and
  are correct (`v1.4.0`) — that's versioning a shipped product, not numbering an
  internal design iteration.

## Why
Sequence IDs carry order but no meaning, and they rot when the roadmap is
reordered or a phase is dropped. A content-revealing name stays accurate and lets
the next reader (often future-you) understand the artifact at a glance.

(Companion: see `naming-config` for naming *config files* by a
slot grammar, and `git-commit` for commit-message conventions.)
