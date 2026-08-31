---
name: naming-config-prompting
description: "Treat prompt text as config-like data: each prompt is a file loaded byte-exact, registered under a <owner>.<role> name (duplicate = hard error), rendered by exact-match placeholder substitution, and content-hashed (sha8) into run provenance so two runs under different prompt text are never indistinguishable. Composition is ordered fragments with banded orders; ablation is an ordinary config override under the owning component."
when_to_use: "Use when adding, moving, or rewording a prompt in a config-driven repo, when building or auditing a prompt registry, when composing role prompts from fragments or defining variants, or when a prompt must be ablated or evolved. Symptoms that should send you here: prompt strings inlined in pipeline code, a run whose behavior changed with no config diff, chained str.replace rendering, a parse schema that grew fields nobody consumes, or an evolver that can rewrite its own judge."
---
# Skill: naming-config-prompting

## Purpose
A prompt selects behavior the way a config value does, but it is prose, so repos treat it as code —
inlined literals, ad-hoc `str.format`, no record of what text a run actually saw. This skill is the
contract that makes prompts **registered, named, hashed data**: one grammar for prompt names, one
storage form (files, loaded byte-exact), one rendering mechanism, provenance that survives into the
run dir, and one seam for ablation and evolution. It is a component deep-dive of `naming-config`:
the umbrella owns the naming philosophy; this file owns the prompting machinery. Distilled from two
independent implementations (AutoRSI `autorsi/prompting/`, MemCodex `memcodex/prompting/`) that
converged on the same design — the convergences are the rules, the divergences are marked choices.

## Contents
- [When to Use](#when-to-use)
- [The name grammar](#the-name-grammar)
- [Text lives in files; rationale lives at the register site](#text-lives-in-files-rationale-lives-at-the-register-site)
- [Registration](#registration)
- [Rendering: placeholders](#rendering-placeholders)
- [Provenance: the sha8 contract](#provenance-the-sha8-contract)
- [Composition: fragments and bands](#composition-fragments-and-bands)
- [Output contracts](#output-contracts)
- [The evolvable boundary](#the-evolvable-boundary)
- [Ablation is a config override](#ablation-is-a-config-override)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Adding a prompt to a pipeline, agent, judge, or controller — or finding one inlined in code.
- Building or auditing a prompt registry; porting one repo's prompting layer to another.
- Composing a role prompt from shared fragments, or defining a variant of an existing composition.
- Ablating a prompt as an experiment arm, or wiring prompts into a self-modification loop.
- NOT for: choosing the prompt's *wording* (that is the experiment); conversation/message-history
  management at inference time; or config names generally (`naming-config` owns the grammar this
  specialises).

## The name grammar
A prompt name is `<owner>.<role>` — the component that owns the prompt, then what the prompt does
for it: `rubric.update_union`, `jitgen.controller`, `guidance.record_diagnosis`. Fragments (pieces
a role prompt is composed from) are `<role>:<slot>` (MemCodex spells the same idea `<stage>:<slot>`
with a fixed STAGES tuple — a stronger form worth adopting when the roles form a pipeline). Two
laws come with the grammar:

- **Ownership is load-bearing.** A prompt is looked up and rendered only by its owner. Another
  component wanting "almost the same text" registers its own name — cross-owner borrowing means a
  wording fix for one caller silently rewires another, the exact drift `naming-config`'s
  compose-never-duplicate rule exists to kill, and here the duplication runs the other way: shared
  text with two masters is worse than two texts with one master each, because prose has no type
  checker to catch the divergence.
- **A changed placeholder set is a new role, not a variant.** Callers bind to the placeholder set;
  changing it under one name breaks every call site invisibly (render fails only at runtime).

## Text lives in files; rationale lives at the register site
The template body is a file (`templates/<owner>/<role>.md`), loaded **byte-exact**: no `strip()`,
no encoding guess, no format detection. Two readers justify this — the model reads the bytes, and
a human diffing two runs reads the file — and both need the file to BE the prompt, not a source
the code massages. The *why* of the prompt (what failed without this sentence, which model quirk a
clause works around) does not go in the template, where the model would read it; it goes as a
comment or docstring at the `register()` site, where the maintainer reads it. MemCodex allows YAML
front-matter in the template file for metadata; if used, the hash covers the body only and the
loader must split deterministically.

## Registration
Registration happens at import time, into one registry:

- **Duplicate name = hard error.** Two components claiming `judge.score` is the two-publishers
  collision of `platform-queue-shepherd`, in miniature: the loser's text vanishes with no error.
- **Byte-identical re-registration is a no-op.** This is what lets a composition assemble the same
  role twice (e.g. under reload) without tripping the duplicate check — and it doubles as the
  byte-identity proof: if a "re-registration" errors, two sources genuinely disagree.
- The registry maps name → (template, placeholder set, parse schema, output budget). A name that
  resolves to nothing fails loudly at lookup (`code-no-fallbacks`): a missing prompt must never
  degrade to an empty string handed to the model.

## Rendering: placeholders
- **The required set is derived from the template, never hand-declared.** Scan for placeholders;
  a hand-maintained list drifts the first time someone edits the file (both repos scarred here).
- **Exact-match fill:** rendering with a missing key errors; rendering with an unused key errors.
  Extra silently-dropped context is a prompt bug you cannot see in any log.
- **Single-pass substitution.** A value that itself contains `<<name>>` is data, not a directive.
  Chained `str.replace` re-scans earlier substitutions and turns payload into template.
- Delimiter is a marked choice: `<<name>>` (AutoRSI) survives payloads full of `{`/`}` (JSON, code,
  rubrics); `str.format` (MemCodex) requires escaping every literal brace in every payload forever.
  Prefer `<<name>>` for any prompt that ever interpolates model output or structured data.

## Provenance: the sha8 contract
`naming-config` rule: the merged config IS the run. Prompts are part of that identity, so:

- Every registered prompt carries a **sha8 derived over its bytes** at registration.
- Render returns **(text, sha8)**, and the caller logs the sha alongside whatever the render fed —
  a judge call, a controller step, a stored artifact.
- The run writes a **provenance manifest** (name → sha8 for every prompt it used) into the run dir
  beside `config.yaml`.
- **Resume validates the manifest.** A store or checkpoint evolved under different prompt text is
  not a continuation of the same experiment; refusing the resume is the honest outcome.

## Composition: fragments and bands
A role prompt assembled from fragments is ordered by **banded integer orders** — both repos
independently chose the same bands (≈ −100 role/persona … 0 task … 100 evidence … 400 output
contract), which is the strongest sign the bands are the natural joints. The machinery:

- **A tie within a band is an error**, not a stable-sort accident: two fragments at one order means
  nobody decided which comes first, and the model's behavior would hang on dict ordering.
- **Numbered rules are auto-numbered over the surviving fragments** after composition, never
  hard-coded in fragment text — a dropped fragment otherwise leaves a hole ("rules 1, 2, 4") the
  model reads as meaningful.
- **Stage/audience firewall:** a fragment written for one audience (the policy model) never leaks
  into a prompt for another (the judge). MemCodex enforces this with the STAGES tuple; at minimum,
  composition refuses fragments whose `<role>:` prefix disagrees with the target role.
- **Variants are declarative deltas** where possible — MemCodex's `_compositions.yaml` with
  `inherits` / `replace` / `add` / `drop` beats AutoRSI's code-side edits because the delta is
  greppable and the base is provably shared (assert byte-identity of the untouched fragments).
- **Golden files pin the assembled bytes.** A byte-level golden per composition catches an
  accidental reorder or a fragment edit that was meant to be variant-local. Regenerating the golden
  is the deliberate act that acknowledges the prompt changed.

## Output contracts
The prompt's other half is what comes back:

- **Per-role `max_tokens`, sized to the whole expected object.** A uniform cap is a scar in both
  repos: AutoRSI's 512-token cap truncated every controller JSON, parse failed, and the arm trained
  on a uniform floor reward — a silent no-op of exactly the kind `code-no-fallbacks` bans.
- **Minimal parse schema: key presence only.** Validate that the keys the consumer reads exist;
  do not type-check or range-check fields nobody consumes. Every extra required field is a new way
  for a good response to be discarded.
- **A parse failure yields None and is counted, never substituted.** Backfilling a default answer
  hides a broken prompt behind healthy-looking metrics; the parse-fail fraction is itself a metric
  key, present from step 0 (a late-appearing key is a collective-schedule hang in TRL-style
  trainers — see memory `trl-metric-keys-are-a-collective-schedule`).
- **One extractor at the transcript boundary.** A second place that regex-scrapes model output is a
  second parser to drift; route every consumer through the registered schema's parser.

## The evolvable boundary
When prompts are subject to self-modification (an evolver, a DGM-style loop, a controller that
edits guidance text), the registry splits in two: **evolvable** prompts the loop may rewrite, and
**harness** prompts — judges, scorers, safety gates — that it must never touch. MemCodex enforces
this by excluding judge prompts from the evolvable registry entirely; AutoRSI should adopt the same
(its overlay channel is contextvar-scoped, which contains but does not forbid). The reason is the
measurement, not the safety theater: an optimizer that can rewrite its own judge optimizes the
judge, and every number downstream stops meaning anything.

## Ablation is a config override
A prompt experiment is an ordinary arm. The owning component's config carries the prompt selection
(a composition name or template path); overriding it is a frozen-config, hash-changing override
like any other axis, so the two arms differ in exactly one slot (`naming-config` symmetry) and the
run dirs are distinct. What ablation is NOT: editing the registered file in place (both arms then
claim one name and the manifest lies), or a `prompt_mode=` flag (the mode-flag anti-pattern of
`naming-config-launcher`, verbatim).

## Rules
1. **Every prompt has a registered `<owner>.<role>` name**; no prompt string reaches a model call
   from an inline literal.
2. **Only the owner renders its prompt.** A second component wanting the text registers its own.
3. **Template bytes are the prompt.** Loaded byte-exact; rationale lives at the register site, not
   in the template.
4. **Duplicate name is a hard error; byte-identical re-registration is a no-op.**
5. **The placeholder set is derived from the template**, filled exact-match (missing OR unused key
   errors), in a single pass.
6. **Render returns text plus sha8**, the run writes a name→sha8 manifest beside `config.yaml`, and
   resume validates it.
7. **Composition uses banded orders; a tie is an error; rule numbers are assigned after assembly.**
8. **A composed prompt has a byte-level golden**, regenerated only as a deliberate act.
9. **`max_tokens` is per role and sized to the full expected object.**
10. **Parse schemas check key presence only; a parse failure is None and counted, never defaulted.**
11. **Judge and scorer prompts live outside any evolvable registry.**
12. **A prompt ablation is a config override under the owning component**; a changed placeholder
    set is a new role.

## Anti-patterns
- **The six-literal sprawl.** The same instruction pasted into six call sites, each drifting one
  wording fix behind the others. The registry exists to make this impossible.
- **The hand-declared placeholder list.** Correct on the day it was written; wrong after the first
  template edit; fails only at 3am when the missing key finally renders.
- **Chained `str.replace` rendering.** Model output containing `<<evidence>>` becomes a directive
  on the second pass. Single-pass or nothing.
- **Hard-coded rule numbers in fragments.** Dropping fragment 3 leaves "rule 4" pointing at
  nothing, and the model dutifully reasons about the gap.
- **The second extractor.** A helper that re-scrapes the transcript beside the registered parser;
  the two disagree the first time the format shifts.
- **`prompt_mode=` flags.** A mode that swaps prompt text outside the config is invisible in the
  frozen run — the launcher mode-flag anti-pattern wearing prose.
- **The self-judging evolver.** An optimization loop with write access to its own scorer's prompt.
  Every improvement it reports is unfalsifiable.

## Companions
`naming-config` (the umbrella: naming philosophy, slot grammar, arm symmetry — this file is its
prompting deep-dive) · `naming-config-launcher` (the sibling deep-dive: the same
frozen-template-plus-overlay doctrine applied to launchers) · `layout-workspace` (where
`prompting/` and `templates/` live in the package tree) · `code-no-fallbacks` (missing prompt,
missing key, and parse failure all fail loudly, never default) · `conventions` (the family index).
