---
name: layout-workspace
description: "Place every file of a config-driven research project: the package with its config/ tree mirroring the code tree, launcher roots and their one shared entrance, the prompt template tree, docs/ plans and reports, session scripts/, and which package a harness, its subject or a shared library lives in."
when_to_use: "Use when standing up or auditing such a project, or when deciding which directory or package a config, launcher, module, prompt template, plan, report or one-off script belongs in. Not for how a config's fields and groups are owned, composed and frozen into the run (config-composition), how a run variation is represented (config-variants), or what a config is called (naming-config)."
---
# Skill: layout-workspace

## Purpose
Place every file of a research project's workspace: the experiment-facing half (the package, its
`config/` tree and `launcher/`) and the agent-facing half (`docs/` and session `scripts/`). A reader
who knows what a file is should be able to predict where it lives, and a session's plans and scripts
should be recoverable instead of buried in a recipe script or a chat scratchpad. This skill answers
where a thing physically lives and nothing else.

## Contents
- [When to Use](#when-to-use)
- [The layout](#the-layout)
- [The five principles](#the-five-principles)
- [When the repo holds BOTH a harness and the thing under test](#when-the-repo-holds-both-a-harness-and-the-thing-under-test)
- [The layout walk is checkable](#the-layout-walk-is-checkable)
- [Going deeper](#going-deeper)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Standing up (or auditing) a config-driven training/eval/serving project.
- Deciding *where* something lives — a hyperparameter, a launcher, a plan, a one-off script.
- Deciding which package a module, a shared library or a harness belongs in.
- The user asks for a plan, report, or design walkthrough, or you generate a session script.
- Reviewing / tidying repo layout, or porting a project onto this paradigm.
- Not for: what a config holds and how its groups are owned, composed, resolved and frozen into the
  run (`config-composition`), how a run variation such as a smoke or a grid cell is represented
  (`config-variants`), what a config or launcher is called (`naming-config`), or where run outputs
  land (`layout-output`).

## The layout
```
# ── Experiment-facing: config → launcher (names per naming-config) ──
# config/ MIRRORS the implementation tree, one level deeper. Read a config path, predict the import
# path; read a module path, predict where its configs live. The mirror is the layout's core invariant.
<pkg>/
  config/                              # config lives INSIDE the package, so resolution never
    model/<model_name>.yaml            #   depends on the CWD and ships with an install
    dataset/<dataset_name>.yaml        #      ⟷  <pkg>/dataset/<name>.py   (flat, as the code is)
    pipeline/<family>/<name>.yaml      #      ⟷  <pkg>/pipeline/<family>/  (rl/, eval/, distill/)
    pipeline/reward/<reward_name>.yaml #      ⟷  <pkg>/pipeline/reward/<name>.py   (nested BECAUSE
    pipeline/agent/<agent_name>.yaml   #          the code is nested: a reward belongs to the RL
    pipeline/agent/model/<name>.yaml   #          pipeline, an agent's model belongs to the agent)
    pipeline/agent/tool/<tool_name>.yaml
  model/  dataset/                     # TOP-LEVEL groups: orthogonal to every pipeline
  pipeline/                            #   ...owns reward/ and agent/, which is why config does too
    <family>/                          # one dir per family, mirrored in config/pipeline/
    reward/
    agent/
      model/  tool/                    # an agent owns ITS model and tools — the nesting RECURSES,
                                       #   and config mirrors it at every depth
  prompting/                           # the prompt registry (contract: config-prompting)
    templates/<owner>/<role>.<ext>     #   prompt text as files, one dir per owning component
  utils/config.py                      # the config system (group merge + run-dir derivation)
launcher/                            # a launcher ROOT: one shared in-pod entrance, many specs
  launch.sh                          # the ONE entrance for every spec under this root (env → runner)
  <launcher-name>/task.yaml          # the neutral run spec (platform-run), the only per-run file
serving_launcher/                    # a second root only for specs no runner shares (AutoRSI's
  launch.sh                          #   vLLM pools), again with exactly one entrance
README.md  pyproject.toml            # what this is + how to install it
# ── Agent-facing: docs + durable session scripts ──
docs/
  ARCH.md                            # single architecture reference (see docs-arch)
  plans/<YYYY-MM-DD>-<topic>.md       # timestamped task/design plans (see docs-plan)
  reports/<YYYY-MM-DD>-<topic>.md    # a FINDING as of a date: results, walkthroughs, handovers
  reports/<topic>.md | .html         # the exception: a LIVING reference maintained in place
scripts/
  README.md                          # what's here + the convention
  checks/                            # re-runnable verification/smoke scripts (committed)
  migration/  setup/                  # purpose subdirs; machine-specific ones git-ignored
```

**`scripts/` vs top-level: relevance, not file type.** `scripts/` is for work *incidental* to the
main workflow — run once or occasionally, and the project still trains without it. Anything on the
critical path of starting a run is top-level and named for what it is: `launcher/`. Burying the
entrance in `scripts/` misfiles it as a chore.

## The five principles
Each exists to make a class of mistake impossible. Principle 1 is this skill's own. Principles 2 to
5 keep their numbers and key phrases because project code cites them by number and by phrase, and each
states its rule in one sentence and names the skill that owns the full statement.

1. **Config is data ABOUT code, and the two trees mirror.** `config/<group>/` sits opposite
   `<pkg>/<group>/`, one level deeper, at every depth — and *nesting is inherited*: a reward's config
   nests under `config/pipeline/` precisely because its code lives in `<pkg>/pipeline/reward/`. The
   recursion has no floor: an agent owns a model and a tool set, so those nest under the agent, which
   nests under the pipeline. When you cannot decide where a new config belongs, the answer is wherever
   its implementation already is.
   **One directory per group, flat inside, and a subdirectory only where the code has the same
   one.** AutoRSI's `autorsi/config/` holds `model/`, `dataset/` and `pipeline/`, and MemCodex's
   `memarena/config/` adds `agent/` and `memory/`. AutoRSI's `config/model/` is 46 flat files because
   `autorsi/model/` is flat (`qwen3.py`, `qwen35.py`), while its `config/pipeline/` has `rl/`, `eval/`
   and `distill/` because `autorsi/pipeline/` has them. `<pkg>/model/<file>.py` defines a class and
   `<pkg>/config/model/<file>_<scale>.yaml` instantiates it, so renaming the class file renames its
   configs and the other way round (the name half is `naming-config`'s). A subdirectory per model
   class or family under `config/model/` is not the house style. `config/model/mdm/mdm_180m.yaml`
   opposite a flat `model/mdm.py` names a directory the code does not have, so the config path stops
   predicting the import path, and the class is already the first slot of the name. QDiffMDM's
   per-class `config/model/<class>/` directories are the older form this replaces.
   Which components a run owns, where each mounts in the merged config, and which model is the run's
   subject are `config-composition`'s. This principle says only that an owned component's config
   directory nests where its code does.
2. **Selection versus specification.** The config specifies and the launcher selects, passing names
   plus the few overrides that define this run, and how many that may be is `config-variants`' rule.
3. **`class_path` is the only seam.** Config names the code to build and never encodes control flow,
   which `config-composition` owns for the config and `code-abstraction` rule 10 (callers never branch
   on a variant) owns for the code.
4. **Compose, never duplicate.** N arms are N configs in one group, never N copies of a pipeline
   config, and how a difference between two runs is represented (an overlay, a child config, a group
   axis or a variant launcher) is `config-variants`'.
5. **The merged config IS the run.** It is hashed into the run dir and frozen there, so anything that
   shapes a run from outside it is invisible history, and `config-composition` owns the rule.

## When the repo holds BOTH a harness and the thing under test

A research repo often grows two things at once: a **harness** that measures (a benchmark, an arena, an
eval suite) and a **subject** that is measured (your system). They feel like one project because you
built both, and they get written as one package. That is a mistake with a specific, diagnosable shape.

**The tell:** a competitor, baseline or third-party implementation has to import YOUR system's package
in order to be measured by your harness. The thing being compared now depends on one of the
competitors, so the harness cannot be used, published, or trusted independently of the subject.

**The fix is two packages and a one-way dependency:**

```
<harness>/                 measures. Knows NOTHING about how any subject works.
  protocol.py              the interface under test — the contract, dependency-free
  registry.py              name -> builder
  bench/                   benchmarks are DATA, not pipelines (see pipeline-kinds.md)
  pipeline/eval/           the consumer loop
  model/                   interfaces the harness CONSUMES, plus the backends it needs to run alone
<subject>/                 implements <harness>.protocol and exposes nothing else publicly
  core/                    what every internal component shares
  <component>/             one directory per swappable internal part
  pipeline/{build,train}/  the PRODUCER loops that make this subject's artifacts
baselines/                 OTHER implementations. Each imports <harness> and bridges to it.
  <name>/                  one per third-party system being compared
```

`<subject> → <harness>` and `baseline → <harness>`, never the reverse, and never subject ↔ baseline.

**Implementations live OUTSIDE the harness, including the baselines.** It is tempting to file
competitors under the harness on the grounds that they exist only to be compared — that is how the
first draft of this section read, and it is wrong. A harness that contains implementations cannot be
used, shipped, or trusted without them, which is the standalone property the split exists to buy. The
harness defines the interface; **every system, yours and theirs alike, writes its own bridge to it.**
Systems register into the harness's registry; the harness imports none of them.

**Interfaces go with the consumer that defines them, implementations with whoever provides them, and
the two meet at `class_path`.** An interface is part of the contract its consumer publishes, so it
lives there even when every implementation lives elsewhere. Because config names an implementation by
`class_path`, the consumer never needs a static import of any of them. The memory protocol and the
model clients below use the same seam.

Three consequences worth stating, because each is a rule people break:

1. **The contract module must stay dependency-free.** If `protocol.py` imports the harness's own
   datasets or its LLM client, then implementing the interface drags in the bench, and you have the
   original coupling wearing a new import path.
2. **A library several packages share lives in the package the others already depend on, never in a
   new neutral package.** The usual case is an LLM client that the subject's writer and the harness's
   judge both call. Decide by what each package must be able to do alone. A harness has to score, and
   scoring calls a model, so a harness that cannot build a model without importing a system it
   measures is not standalone, and the clients go in the harness. The subject reaches them across the
   edge it already has, through `class_path` against an interface it declares itself. MemCodex is the
   working case. Its model clients live in `memarena/model/`, with their configs opposite in
   `memarena/config/model/`, while the `memcodex` library declares only the `LLM` interface
   (`memcodex/llm/`), imports nothing from `memarena`, and receives a client by `class_path`. A third
   package added to keep the library neutral buys nothing when a dependency edge already exists, and
   it fragments a repo a reader has to hold in their head. Filing the clients under the subject
   instead makes the harness import one of the systems it measures, the coupling this section exists
   to remove.
3. **Prove the split with a conformance suite, not a directory listing.** The harness ships a
   parameterised test that every registered implementation must pass, and CI runs it across all of
   them. Moving files proves nothing; an implementation that only compiles against the subject's
   internals is caught the moment it must satisfy the contract on its own.

**Do not split before there are two implementations.** One system and one bench in one package is fine
and is not premature to leave alone; the split earns its cost at the second implementation, which is
also when the coupling first does damage. The same second-consumer test decides when a part is lifted
into a shared component (`references/pipeline-kinds.md`) and when an unused eval protocol or reducer
gets built (`references/eval-axes.md`).

## The layout walk is checkable

The associations this skill and `naming-config` promise are mechanically verifiable, and a project
should carry a `layout_walk` check that locks them:
  A1  every config's class_path imports, and the config's subdir mirrors the class's module
  A2  every `_base_` chain is a name-prefix walk (the naming rule is `naming-config`'s)
  A3  the name carries the class walk (see naming-config "Two walks, one name") — resolve owned
      sub-objects' class_paths too, not just the module entry point
  A4  every launcher selector resolves to a real group config
  A5  no config inherits a backbone's own constructor kwargs onto a class that cannot accept them,
      after removing the kwargs the target class itself accepts
A5 exists because AutoRSI's `rl_grpo_shared_harness` inherited the dual-role trainer's kwargs through
its recipe base, and `GRPOTrainer` refused them at the pod an hour of queueing later. Its first
version flagged the raw intersection of the two kwarg sets and produced a false positive within
minutes of the true one, which is why the target's own parameters are removed first.
`scaffold/layout_walk.py` specifies the five checks and the thin adapter a project supplies
(`paths_of`, `GROUP_KEYS`, `BACKBONES`, `KNOWN_DEBTS`). It holds no check bodies, so copy the working
instantiation, AutoRSI's `scripts/checks/layout_walk.py`, and wire the adapter. The adapter's
`paths_of(group)` is the project's one resolver for a group's files, never a private glob
(`config-composition`, "One resolver owns a group's paths").
Violations that predate the rule are DECLARED debts (a named list in the check, reported every run,
failing under --strict), never silenced: a debt list is a decision queue, an exemption list is a
blindfold.

## Going deeper
These references carry the detail, and are worth opening only when the question is theirs:

| read | when |
|---|---|
| `references/runner-styles.md` | starting a project: do you own the loop, or wrap a framework? |
| `references/pipeline-kinds.md` | adding a pipeline kind and placing its code and config, or placing a term like `lora` / `nar` / `mtp` |
| `references/eval-launchers.md` | wiring an eval run's trained policy and its judge |
| `references/eval-axes.md` | designing or extending an eval family: what forks a pipeline vs a scorer |

## Rules
1. **Config lives inside the package, one directory per group, mirroring the code tree.** A config
   subdirectory exists only where the code has the same one (principle 1).
2. **Hyperparameters live in `config/`, never in a launcher's `run:` list or a recipe script.** How
   many overrides a launcher may still carry is `config-variants`'.
3. **One shared entrance per launcher root, never one per launcher.** `launcher/launch.sh` serves
   every spec under `launcher/`. A second root such as `serving_launcher/` exists only for specs no
   runner shares and has its own single entrance. The per-launcher `task.yaml` is the only per-run
   file.
4. **Prompt templates live inside the package under `prompting/templates/<owner>/`, beside the
   registry that loads them**, so they ship with an install as config does (`config-prompting` owns
   the contract).
5. **A library several packages share lives in the package the others already depend on**, never in
   a new neutral package, and an interface lives with the consumer that defines it.
6. **A run's log lands inside the run dir that `naming-config` rule 6 derives**, never at a `log:`
   path a launcher spec chooses.
7. **Plans** → `docs/plans/<YYYY-MM-DD>-<topic>.md` · **reports** → `docs/reports/`, dated the same
   way unless the document is a living reference · **architecture** → a single `docs/ARCH.md`, kept
   current.
8. **A report is dated when re-reading it later needs to know WHEN it was true.** Results, sweep
   walkthroughs, verifications, handovers and design snapshots all describe a world that has since
   moved; a bare `comparison_table.md` claims to be current forever and quietly becomes a lie. The
   test is one question: *would updating this file in place make its name wrong?* If yes it is a
   finding and takes the date. If no — a runbook, a related-work section, a conventions reference —
   it is living, it is maintained in place, and a date on it would falsely imply a snapshot.
   Date by LAST UPDATE, not first draft (`git log -1 --format=%ad --date=short -- <file>`), because
   that is the moment the content was last true.
9. **A report is prose about the system, not an artifact of it.** A job spec, a config, a `.job` or
   a raw metric dump under `docs/reports/` is misfiled: specs live in `launcher/`, outputs live under
   `$OUTPUT_DIR_HOME`. `docs/reports/` is what you would hand a colleague to read.
10. **Session scripts** → `scripts/<purpose>/` as durable checkpoints, never left in `/tmp`. Header
    each with **what · when · usage**. Commit reusable ones; git-ignore machine-specific or secret ones.
11. Name everything descriptively (`naming-descriptive`) — never `v1`/`Px`/`tmp`/`final2`.
12. Keep docs, plans, reports and session scripts **out of** the package/source/test trees.
13. **Run outputs never land in the project dir.** Checkpoints, logs, metrics and eval results are a
    separate tree under `$OUTPUT_DIR_HOME`, whose layout and resume-versus-derived classification
    belong to `layout-output`.

## Anti-patterns
- **Per-launcher `launch.sh`** beside each `task.yaml`. Redundant, and it drifts. Any second entrance
  in one root drifts the same way. AutoRSI's `trl_rollout_launcher.sh`, named directly in one serve
  spec's `run:`, drifted to different env names for the same concepts (`SERVE_MAX_LEN` against
  `SERVE_MAX_MODEL_LEN`, `SERVE_PORT` against `SERVE_PORT_BASE`) before it was folded back into
  `serving_launcher/launch.sh`.
- **Hyperparameters inline** in a `run:` block or a `train_*.sh` recipe — a config in disguise.
- **A class or family directory under `config/model/` that the code does not have.** It is tempting
  because it groups one class's scales together, but the config path stops predicting the import
  path, and the grouping is already in the name's first slot.
- **A new neutral package for a shared library.** It looks impartial, but it adds a package and a
  dependency edge where one existing edge already does the job.
- **A whitelisting `build_config()`**, which `config-composition` forbids in its framework block.
  (Cost of learning this: four arms × 12h, all flat.)
- **`_v2` / `_baseline` / `_test` names** — say what *differs* in a slot (`naming-config` Hard rule 1).
- **An undated report of a dated finding.** `comparison_table.md`, `fixes_verification.md`,
  `00-A2C-MetaRL.md`: the first two claim permanence they never had, and the third orders by an
  opaque counter (`naming-descriptive`). A reader cannot tell which of two comparison tables is the
  live one, and neither can the author six weeks later. (Cost of learning this: 16 files renamed at
  once on 2026-09-01, and every link to them across docs and analysis scripts repointed by hand.)
- **Empty or stale package dirs** left by a refactor. Git does not track empty dirs, so they survive a
  `git mv` invisibly and read as real structure. Sweep after every move.

## Companions
`naming-config` (what a config or launcher is called, the paired skill for the experiment-facing
half) · `config-composition` (how the groups this tree holds are owned, composed, resolved and frozen
into the run) · `config-variants` (how a run variation is represented without copying a launcher) ·
`config-prompting` (the prompt contract whose template tree lives here) · `platform-run` (the task
spec under `launcher/` and how it renders) · `layout-output` (the run-output tree, the sibling
`layout-` concern) · `docs-plan` (writes `docs/plans/…`) · `docs-arch` (maintains `docs/ARCH.md`) ·
`naming-descriptive` (how to name) · `git-commit` (commit conventions) · `code-abstraction` (what
goes behind a `class_path`, and why callers never branch on a variant) · `conventions` (the family
index).
