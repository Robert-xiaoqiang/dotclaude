---
name: layout-workspace
description: "Lay out a config-driven research project end to end: config/ mirroring the package tree, launcher/, one flat platform layer, plus docs/ and session scripts/."
when_to_use: "Use when standing up or auditing such a project, or when deciding where a hyperparameter, launcher, plan or one-off script belongs."
---
# Skill: layout-workspace

## Purpose
Lay out a research project's **workspace** end to end — the *experiment-facing* half
(`config/` + `launcher/` + a single flat platform layer) and the *agent-facing* half
(`docs/` + session `scripts/`) — so both a config's purpose and a session's artifacts are
**predictable and recoverable**, not buried in a recipe script or a chat scratchpad. Config
**names** follow `naming-config`; the run-control layer follows `platform-run`; run **outputs**
follow `layout-output`. This skill is the map that ties launcher → config → project together.

## When to Use
- Standing up (or auditing) a config-driven training/eval/serving project.
- Deciding *where* something lives — a hyperparameter, a launcher, a plan, a one-off script.
- The user asks for a plan, report, or design walkthrough, or you generate a session script.
- Reviewing / tidying repo layout, or porting a project onto this paradigm.

## The layout
```
# ── Experiment-facing: config → launcher → platform (names per naming-config) ──
# config/ MIRRORS the implementation tree, one level deeper. Read a config path, predict the import
# path; read a module path, predict where its configs live. The mirror is the layout's core invariant.
<pkg>/
  config/                              # config lives INSIDE the package, so resolution never
    model/<model_name>.yaml            #   depends on the CWD and ships with an install
    dataset/<dataset_name>.yaml        #      ⟷  <pkg>/dataset/<name>.py
    pipeline/<pipeline_name>.yaml      #      ⟷  <pkg>/pipeline/<name>.py
    pipeline/reward/<reward_name>.yaml #      ⟷  <pkg>/pipeline/reward/<name>.py   (nested BECAUSE
    pipeline/agent/<agent_name>.yaml   #          the code is nested: a reward belongs to the RL
    pipeline/agent/model/<name>.yaml   #          pipeline, an agent's model belongs to the agent)
    pipeline/agent/tool/<tool_name>.yaml
  model/  dataset/                     # TOP-LEVEL groups: orthogonal to every pipeline
  pipeline/                            #   ...owns reward/ and agent/, which is why config does too
    reward/
    agent/
      model/  tool/                    # an agent owns ITS model and tools — the nesting RECURSES,
                                       #   and config mirrors it at every depth
  platform/                            # PURE-PYTHON translation: jobspec, profile, translate/<p>.py
  utils/config.py                      # the config system (group merge + run-dir derivation)
launcher/
  launch.sh                          # ONE shared in-pod entrance for EVERY pipeline (env → runner)
  <launcher-name>/task.yaml          # neutral run spec; run: is an argv LIST of k=v, no shell string
platform/                            # TOP-LEVEL, because it is on the critical path of "how a run
  <platform>.sh  _common.sh          #   starts" — thin native submit/status/logs + shared follow loop
  <platform>.yaml                    #   the profile: account / quota / image / data sources
README.md  pyproject.toml            # what this is + how to install it
# ── Agent-facing: docs + durable session scripts ──
docs/
  ARCH.md                            # single architecture reference (see docs-arch)
  plans/<YYYY-MM-DD>-<topic>.md       # timestamped task/design plans (see docs-plan)
  reports/<topic>.md | .html          # walkthroughs/figures that explain the system
scripts/
  README.md                          # what's here + the convention
  checks/                            # re-runnable verification/smoke scripts (committed)
  migration/  setup/                  # purpose subdirs; machine-specific ones git-ignored
```

**`scripts/` vs top-level: relevance, not file type.** `scripts/` is for work *incidental* to the
main workflow — run once or occasionally, and the project still trains without it. Anything on the
critical path of starting a run is top-level and named for what it is: `launcher/`, `platform/`.
Burying the submit adapter in `scripts/` misfiles the entrance as a chore. The *pure-python* half of
the platform layer still lives in the package so it is importable and unit-testable without a shell —
one layer with two roles, not two layers.

## The five principles
Each exists to make a class of mistake impossible.

1. **Config is data ABOUT code, and the two trees mirror.** `config/<group>/` sits opposite
   `<pkg>/<group>/`, one level deeper, at every depth — and *nesting is inherited*: a reward's config
   nests under `config/pipeline/` precisely because its code lives in `<pkg>/pipeline/reward/`. The
   recursion has no floor: an agent owns a model and a tool set, so those nest under the agent, which
   nests under the pipeline. When you cannot decide where a new config belongs, the answer is wherever
   its implementation already is.
   **An owned model is not the top-level `model` group.** Top-level `model` is the one policy the run
   optimises or evaluates. An agent's internal model, a judge, a teacher — each is a model owned by the
   thing that uses it, and lives under that owner. Two model slots in one run means one of them is
   owned; see `references/config-anatomy.md`.
2. **Selection versus specification.** The config **specifies** (every knob, complete). The launcher
   **selects** (names, plus the few overrides that define *this* run). A launcher that starts
   specifying is a config in disguise, and it will not appear in the run's frozen `config.yaml`.
3. **`class_path` is the only seam.** Config names code to build; it never encodes control flow. The
   moment a pipeline reads a config value to pick a branch (`if kind == "opd"`), the arm has leaked
   into the code and the config stops being a complete description of the run.
4. **Compose, never duplicate.** N arms are N configs in ONE group, not N copies of a pipeline config.
   The test is mechanical: if two configs differ in one field, that field is an axis and belongs in its
   own group (`naming-config`). Duplicates do not stay in sync — the first retune proves it.
5. **The merged config IS the run.** It is hashed into the run dir and frozen there. Anything that
   influences a run but is not in it — an env flag, a `mode=`, a hand-edited default — is invisible
   history, and two materially different runs become indistinguishable after the fact.

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

Three consequences worth stating, because each is a rule people break:

1. **The contract module must stay dependency-free.** If `protocol.py` imports the harness's own
   datasets or its LLM client, then implementing the interface drags in the bench, and you have the
   original coupling wearing a new import path.
2. **A shared instrument does not live in either one.** An LLM client used by the subject's writer AND
   the harness's judge belongs to neither; put it in its own small package. Filing it under the harness
   makes an offline build depend on the benchmark — the same category error as (1).
3. **Prove the split with a conformance suite, not a directory listing.** The harness ships a
   parameterised test that every registered implementation must pass, and CI runs it across all of
   them. Moving files proves nothing; an implementation that only compiles against the subject's
   internals is caught the moment it must satisfy the contract on its own.

**Do not split before there are two implementations.** One system and one bench in one package is fine
and is not premature to leave alone; the split earns its cost at the second implementation, which is
also when the coupling first does damage.

## Rules
- **Hyperparameters live in `config/`, never in a launcher or a recipe script.** A wall of `key=value`
  overrides means the defaults belong in a group config and only the delta stays in the launcher. But
  a long submit line is a *symptom*, not a verdict: classify each token before moving anything, because
  two of the four kinds are correct exactly where they are. See `references/overrides.md`.
- **The framework's config is passed VERBATIM, never whitelisted.** A `build_config()` that hand-picks
  fields makes every field it forgot unreachable from YAML *and* CLI, and the run silently uses a
  default nobody chose. Dump the fully-resolved framework config into the run dir.
- **A group's settings live under its group key.** No second top-level home for the same concern, so
  an override path is always predictable from the group name.
- **A group is top-level only if it is orthogonal to every pipeline.** `model` and `dataset` are; a
  `reward` is not. An owned group nests while keeping its short selector — see `config-anatomy.md`.
- **The launcher passes ONLY config names and config overrides.** No `mode=`, no `--debug`, no
  launcher-only flags. A smoke run is a named dataset, not a mode.
- **The entrance derives the log path from the config chain.** It asks the config system for the run
  dir and tees into it, so config, checkpoints, metrics and log are one directory. A `log:` field in a
  launcher spec is a second, hand-maintained source of truth.
- **One shared entrance, not one per launcher.** The per-launcher `task.yaml` is the only per-run file.
- **One flat platform layer.** Do not split platform logic across a top-level dir *and* a package dir.
- **Plans** → `docs/plans/<YYYY-MM-DD>-<topic>.md` · **reports** → `docs/reports/` · **architecture**
  → a single `docs/ARCH.md`, kept current.
- **Session scripts** → `scripts/<purpose>/` as durable checkpoints, never left in `/tmp`. Header each
  with **what · when · usage**. Commit reusable ones; git-ignore machine-specific or secret ones.
- Name everything descriptively (`naming-descriptive`) — never `v1`/`Px`/`tmp`/`final2`.
- Keep all of this **out of** the package/source/test trees.

## One resolver owns a group's paths

When a group's configs may live in family subdirs (the mirror rule), "which files are this group's"
becomes a real function: recursive walk, other groups' subdirs excluded — and OWNERSHIP MUST COME
FROM THE GROUP REGISTRY, never from glob depth. Depth was only ever an accident that happened to
encode ownership. Export ONE `group_config_paths(group)` from the config system and make the loader
AND every check import it: the day a family subdir appears, N private flat globs are N tools that go
blind simultaneously while reporting healthy empty sets.

## The layout walk is checkable — scaffold it

The four associations this skill promises are mechanically verifiable, and a project should carry a
`layout_walk` check that locks them:
  A1  every config's class_path imports, and the config's subdir mirrors the class's module
  A2  every `_base_` chain is a name-prefix walk (assembly inheritance visible in the name)
  A3  the name carries the class walk (see naming-config "Two walks, one name") — resolve owned
      sub-objects' class_paths too, not just the module entry point
  A4  every launcher selector resolves to a real group config
A generic scaffold lives in `scaffold/layout_walk.py` (copy + thin project adapter).
Violations that predate the rule are DECLARED debts (a named list in the check, reported every run,
failing under --strict), never silenced: a debt list is a decision queue, an exemption list is a
blindfold.

## Anti-patterns
- **Per-launcher `launch.sh`** beside each `task.yaml`. Redundant, and it drifts.
- **Hyperparameters inline** in a `run:` block or a `train_*.sh` recipe — a config in disguise.
- **A whitelisting `build_config()`.** Whatever it omits is unreachable, and the failure is silent:
  the run trains on defaults and looks fine. (Cost of learning this: four arms × 12h, all flat.)
- **Duplicated platform logic** — two renderers, two follow loops, or a second spec dialect. This is
  about duplicated *logic*, not language: python translation plus a thin native adapter is one layer.
- **A pipeline config duplicating another except one flag.** That flag is an axis; give it a group.
- **A hand-chosen `log:` path** in a launcher spec — the run dir already knows.
- **`_v2` / `_baseline` / `_test` names** — say what *differs* in a slot (`naming-config`).
- **Empty or stale package dirs** left by a refactor. Git does not track empty dirs, so they survive a
  `git mv` invisibly and read as real structure. Sweep after every move.

## Going deeper
The core above covers placement. These carry the detail, and are worth opening only when the
question is theirs:

| read | when |
|---|---|
| `references/config-anatomy.md` | writing a group config, or deciding if something deserves its own group |
| `references/runner-styles.md` | starting a project: do you own the loop, or wrap a framework? |
| `references/pipeline-kinds.md` | adding a pipeline kind, or placing a term like `lora` / `nar` / `mtp` |
| `references/eval-launchers.md` | naming an eval launcher, or wiring a judge |
| `references/overrides.md` | a launcher's `run:` grew a wall of `a.b.c=value` |

## Not this skill
Run outputs (checkpoints, logs, metrics, eval) are a **separate** tree under `$OUTPUT_DIR_HOME`, not
the agent workspace. Their layout and their resume-vs-derived classification live in `layout-output`.
Never write run outputs into the project dir.

## Companions
`naming-config` (the slot grammar for config/launcher **names** — the paired skill for the
experiment-facing half) · `platform-run` (the flat run-control layer under `launcher/`) ·
`layout-output` (the run-output tree, the sibling `layout-` concern) · `docs-plan` (writes
`docs/plans/…`) · `docs-arch` (maintains `docs/ARCH.md`) · `naming-descriptive` (how to name) ·
`git-commit` (commit conventions).
