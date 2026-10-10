---
name: config-prompting
description: "Treat prompt text as config-like data: each prompt is a file loaded byte-exact, registered under a <owner>.<role> name (duplicate = hard error), rendered by exact-match placeholder substitution, and content-hashed (sha8) into run provenance so two runs under different prompt text are never indistinguishable. Composition is ordered fragments with banded orders; ablation is an ordinary config override under the owning component."
when_to_use: "Use when adding, moving, or rewording a prompt in a config-driven repo, when building or auditing a prompt registry, when composing role prompts from fragments or defining variants, or when a prompt must be ablated or evolved. Symptoms that should send you here: prompt strings inlined in pipeline code, a run whose behavior changed with no config diff, chained str.replace rendering, a parse schema that grew fields nobody consumes, or an evolver that can rewrite its own judge. Prompt and fragment names are owned here. Not for config or launcher names (naming-config), how the owning component's config merges (config-composition, which treats a prompts: block as an owned component it does not open), or where the template tree lives (layout-workspace)."
---
# Skill: config-prompting

## Purpose
A prompt selects behavior the way a config value does, but it is prose, so repos treat it as code —
inlined literals, ad-hoc `str.format`, no record of what text a run actually saw. This skill is the
contract that makes prompts **registered, named, hashed data**: one grammar for prompt names, one
storage form (files, loaded byte-exact), one rendering mechanism, provenance that survives into the
run dir, and one seam for ablation and evolution. It owns the whole prompt-resource contract, prompt
and fragment names included, so no other skill states these rules. Distilled from two independent
implementations (AutoRSI `autorsi/prompting/`, MemCodex `memcodex/prompting/` and its program
registry `memcodex/program/prompting.py`) that converged on the same design — the convergences are
the rules, the divergences are marked choices.

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
- Naming a prompt or a fragment. Prompt-resource names are owned here, not by `naming-config`.
- Filling the `prompts:` block of a component's config. `config-composition` merges that block as an
  owned component it does not open, so what goes inside it is decided here.
- NOT for: choosing the prompt's *wording* (that is the experiment), conversation and message-history
  management at inference time, the names of configs and launchers (`naming-config`), or where the
  template tree lives (`layout-workspace`).

## The name grammar
A prompt name is `<owner>.<role>` — the component that owns the prompt, then what the prompt does
for it: `rubric.update_union` and `judge.grade` in AutoRSI, `raw.summarize` in MemCodex. Both
registries enforce the form, lowercase with exactly one dot, because the owner half is what the
manifest reports and what stops one component's override from shadowing another component's role.
Fragments (pieces a role prompt is composed from) are `<owner>.<role>:<slot>`, as in AutoRSI's
`rubric.update:rule_budget`, so the role a fragment composes into is part of its name and a
composition refuses a fragment of another role. MemCodex's fragment module spells the same idea
`<stage>:<slot>` with a fixed STAGES tuple, a stronger form worth adopting when the roles form a
pipeline. Two laws come with the grammar:

- **Ownership is load-bearing.** A prompt is looked up and rendered only by its owner. Another
  component wanting "almost the same text" registers its own name — cross-owner borrowing means a
  wording fix for one caller silently rewires another, the same drift near-duplicate configs
  cause, and here the duplication runs the other way: shared text with two masters is worse than
  two texts with one master each, because prose has no type checker to catch the divergence.
  AutoRSI pays this cost on purpose. `rubric.update_union` re-registers every `rubric.update:*` row
  under its own `rubric.update_union:*` name instead of borrowing them, so the shipped
  `rubric.update` stays byte-identical for the arms that still mount it.
- **A changed placeholder set is a new role, not a variant.** Callers bind to the placeholder set;
  changing it under one name breaks every call site invisibly (render fails only at runtime).

## Text lives in files; rationale lives at the register site
The template body is a file at `<owner>/<role>` under the repository's template root, with an
extension the repository picks once. AutoRSI uses `.txt` (`rubric.propose` is
`autorsi/prompting/templates/rubric/propose.txt`, read by `T("rubric/propose")`), and a fragment file
adds its slot (`templates/rubric/update/rule_budget.txt`). MemCodex uses `.md`
(`memcodex/program/prompts/raw/summarize.md`, registered by `register_dir` as `raw.summarize`).
Where the template root sits is placement, owned by `layout-workspace`. The file is loaded
**byte-exact**: no `strip()`, no encoding guess, no format detection. Two readers justify this —
the model reads the bytes, and a human diffing two runs reads the file — and both need the file to
BE the prompt, not a source the code massages. The *why* of the prompt (what failed without this
sentence, which model quirk a clause works around) does not go in the template, where the model
would read it; it goes as a comment or docstring at the `register()` site, where the maintainer
reads it. MemCodex allows YAML front-matter in the template file for metadata; if used, the hash
covers the body only and the loader must split deterministically.

## Registration
Registration happens at import time, into one registry:

- **Duplicate name = hard error.** Two components claiming `judge.grade` is a two-writers collision
  in miniature: both publish under one name, and the loser's text vanishes with no error.
- **Byte-identical re-registration is a no-op.** This is what lets a composition assemble the same
  role twice (e.g. under reload) without tripping the duplicate check — and it doubles as the
  byte-identity proof: if a "re-registration" errors, two sources genuinely disagree.
- The registry maps name → (template, placeholder set, parse schema, output budget). An unknown
  name fails loudly at lookup, the rule `code-abstraction` (rule 11) states for anything selected by
  name. For a prompt, the failure it prevents is an empty string handed to the model.

## Rendering: placeholders
- **The required set is derived from the template, never hand-declared.** Scan for placeholders;
  a hand-maintained list drifts the first time someone edits the file (both repos scarred here).
- **Exact-match fill:** rendering with a missing key errors; rendering with an unused key errors.
  Extra silently-dropped context is a prompt bug you cannot see in any log.
- **Single-pass substitution.** A value that itself contains `<<name>>` is data, not a directive.
  Chained `str.replace` re-scans earlier substitutions and turns payload into template.
- Delimiter is a marked choice: `<<name>>` (AutoRSI) survives payloads full of `{`/`}` (JSON, code,
  rubrics); `str.format` (MemCodex's fragment module) requires escaping every literal brace in every
  payload forever. MemCodex's program registry chose `<<name>>` for that reason.
  Prefer `<<name>>` for any prompt that ever interpolates model output or structured data.
- **A role may declare which slots it is allowed to receive.** AutoRSI attaches a `ContextPolicy` to
  a role and render refuses any slot outside the grant. The judge roles name `reference`,
  `ground_truth` and `answer` as denials, so a refactor that hands the grader a reference answer
  fails at render instead of contaminating the reward.

## Provenance: the sha8 contract
The merged config is the run (`config-composition` owns that rule). Prompts are part of that
identity, so:

- Every registered prompt carries a **sha8 derived over its bytes** at registration.
- Render returns **(text, sha8)**, and the caller logs the sha alongside whatever the render fed —
  a judge call, a controller step, a stored artifact.
- The run records a **prompt manifest**, name → sha8 for every registered prompt, rendered or
  not. MemCodex states why it must cover every registered prompt. Its writer, task-agent and judge
  prompts render only inside worker processes, so a manifest built from what the parent rendered
  would miss an edited writer prompt. Where the manifest file lives is a repository choice. MemCodex
  writes `prompts.json` in the run dir. AutoRSI's rubric store reserves a `prompt_registry` field in
  `<run_dir>/rubric_state/manifest.json`, but no live caller hands the registry to the store's
  `bind()`, so that field stays empty. That gap is known debt in AutoRSI, not a precedent.
- **Resume compares the prompt identity stored with the resume state.** AutoRSI keeps
  `{role: sha8}` for the rubric component's own roles, and the judge model, under the `rubric` key
  of `checkpoint-<step>/harness_state_rank<r>.json`, beside the weights, and refuses a resume when
  any of them differs. Its `rubric_state/manifest.json` is a derived view that no resume reads.
  MemCodex compares the registry's manifest with the run dir's `prompts.json` at seed and again in
  every worker. A store or checkpoint evolved under different prompt text is not a continuation of
  the same experiment, so refusing the resume is the honest outcome. Continuing anyway is an
  explicit config field (`allow_prompt_change: true` in AutoRSI), so the choice lands in the frozen
  config.

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
  into a prompt for another (the judge). AutoRSI declares an audience (`policy`, `judge`, `agent`)
  on every fragment and every composition and refuses a mismatch at construction. MemCodex refuses
  a fragment from another stage of its STAGES tuple. At minimum, composition refuses fragments whose
  `<owner>.<role>:` prefix disagrees with the target role.
- **Variants are declarative deltas** where possible — MemCodex's `_compositions.yaml` with
  `inherits` / `replace` / `add` / `drop` beats AutoRSI's code-side edits because the delta is
  greppable and the base is provably shared (assert byte-identity of the untouched fragments).
- **Golden files pin the assembled bytes.** A byte-level golden per composition catches an
  accidental reorder or a fragment edit that was meant to be variant-local. Regenerating the golden
  is the deliberate act that acknowledges the prompt changed.

## Output contracts
The prompt's other half is what comes back:

- **Per-role `max_tokens`, sized to the whole expected object.** A uniform cap is a scar in
  AutoRSI. Its judge capped replies at 512 tokens, each reply was cut after the explanation and
  before `criteria_met`, every verdict read False, and the reward was uniformly 0 for a full run
  with nothing in the log to say so, a silent no-op of exactly the kind `code-no-fallbacks` bans.
  MemCodex's program runtime shows the form to copy. Its config gives `max_tokens[owner][role]` per
  prompt name, and a prompt the block omits raises `KeyError`. AutoRSI's `Prompt` and `register()`
  still default `max_tokens=768`, so a role registered without a value gets a uniform cap. That
  default is known debt in AutoRSI, not a precedent.
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
this by keeping its judge prompts out of the evolvable fragment registry entirely, and its run-time
overlay may reshape only fragments that are registered, narrowed further by a per-run `allowed`
scope. AutoRSI has no loop that rewrites prompt text yet. Its judge roles (`judge.grade`,
`judge.matrix`) share one registry with the cascade roles, and each component's `prompts:` block
may override only that component's own roles, applied at construction. A run therefore cannot
rewrite its judge from another component's block, but nothing marks the judge roles as harness,
so a loop that evolves prompt text there needs the MemCodex split first. The reason is the
measurement, not the safety theater: an optimizer that can rewrite its own judge optimizes the
judge, and every number downstream stops meaning anything.

## Ablation is a config override
A prompt experiment is an ordinary arm. The owning component's config carries the prompt selection,
which may be a composition name, a template path or the variant text itself. AutoRSI's form is a
`prompts:` block keyed by registered name, with the text inline in the component's YAML:

```yaml
pipeline:
  rubric:
    init_kwargs:
      prompts:
        rubric.analyze: "...the variant wording..."
```

Inline text in config is legal and a literal in code is not. The YAML lands in the frozen
`config.yaml`, changes the run hash and re-stamps the role's sha8, and a literal in code does none
of the three. Overriding the selection is a frozen-config, hash-changing override like any other
axis, so the two arms differ in exactly one slot (`naming-config` symmetry) and the run dirs are
distinct. The override seam refuses three mistakes. An unknown role is a hard error,
because overriding a role nothing renders changes the hash and no prompt. A changed placeholder set
is refused, because the call site still fills the old inputs. A composition that renders after a
whole-template override of its role refuses too, because its fragment manifest would describe text
that was not sent, so a composed role is ablated per fragment through the composition's edits
(`{fragment_name: text}` rewrites a row, `{fragment_name: null}` drops it). What ablation is NOT:
editing the registered file in place (both arms then claim one name and the manifest lies), or a
`prompt_mode=` flag (the mode-flag ban owned by `config-variants`, applied to prompt text).

## Rules
1. **Every prompt has a registered `<owner>.<role>` name**, and no prompt string reaches a model call
   from a literal in code. Variant text inline in the owning component's `prompts:` block is config,
   and legal.
2. **Only the owner renders its prompt.** A second component wanting the text registers its own.
3. **Template bytes are the prompt.** Loaded byte-exact; rationale lives at the register site, not
   in the template.
4. **Duplicate name is a hard error; byte-identical re-registration is a no-op.**
5. **The placeholder set is derived from the template**, filled exact-match (missing OR unused key
   errors), in a single pass.
6. **Render returns text plus sha8**, the run records a name→sha8 manifest of every registered
   prompt, and resume refuses prompt text that differs from the identity stored with its resume
   state unless the config opts out.
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
- **`prompt_mode=` flags.** The mode-flag ban owned by `config-variants`, applied to prompt text.
- **The self-judging evolver.** An optimization loop with write access to its own scorer's prompt.
  Every improvement it reports is unfalsifiable.

## Companions
`naming-config` (the names of configs and launchers, while prompt and fragment names are owned
here) · `config-composition` (merges the owning component's config and treats its `prompts:` block
as an owned component it does not open) · `config-variants` (the mode-flag ban that `prompt_mode=`
falls under) · `layout-workspace` (where `prompting/` and the template tree live in the package
tree) · `code-abstraction` (selection by name with an unknown name a loud error, which the registry
lookup applies) · `code-no-fallbacks` (missing prompt, missing key, and parse failure all fail
loudly, never default) · `conventions` (the family index).
