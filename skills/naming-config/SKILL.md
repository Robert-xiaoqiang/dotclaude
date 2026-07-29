# Skill: naming-config

## Purpose
Apply a consistent naming convention across **model**, **pipeline**,
**dataset**, and **launcher** configs in any LLM / agent / research
codebase that uses a config-driven runner (OmegaConf, Hydra, Pydantic
configs, YAML registries, etc.). Keeps file names, class paths, and
output dirs aligned so a config name uniquely identifies what runs.

## When to Use
- Adding a new model variant, pipeline stage, dataset, or launcher
- Renaming an existing config (refactor)
- Reviewing PRs that introduce new config files
- The user says: "what should I name this config?", "is this naming
  consistent?", "build a launcher for ..."

## Core principle
Each config file's name is a **slot grammar string** of the same
slots that describe the corresponding code path. Read the file name,
predict the class / module / behavior. Read the class / module name,
predict the config file name. Two configs that differ in one knob must
differ in exactly that one slot.

## Slot grammars

### Model configs

```
{model_class}[_{variant_axes...}][_{backbone}]_{scale}[_{specialty_tag}]
```

* `model_class` matches the file name in `<package>/model/` and is
  the **subdir** under `<package>/config/model/`. e.g. `mdm`, `lora_mdm`,
  `quantum_lora_mdm`.
* `variant_axes` are class-specific knobs that go into the file name
  *only when set non-trivially* (e.g. quantum injection position /
  strategy / readout). Order them outer→inner.
* `backbone` appears only when weights are loaded from a pretrained
  source (e.g. `smdm`, `llama3`). Omit for from-scratch.
* `scale` matches the model-config registry key (`180m`, `1028m`, `8b`).
* `specialty_tag` for orthogonal axes that don't fit the above
  (e.g. qubit count `8q`/`16q`, expert count `8e`).

### Pipeline configs

```
{stage}_{flavour}
```

* `stage` ∈ `{pretrain, sft, eval, dpo, rl, ...}`.
* `flavour` matches the model-class family (`ar`, `mdm`, `quantum_mdm`,
  `lora_mdm`).
* Reuse Python pipelines via `class_path` — many configs can share one
  pipeline with one boolean flag (e.g. `optimize_trainable_only` to flip
  full-fine-tune vs LoRA-only).

### Dataset configs

```
{method}_{source}[_{tag}]
```

* `method` is the loader (`local_packed`, `hf_streaming`, `sharegpt`).
* `source` is the corpus name (`slimpajama`, `ultrachat`, `c4`).
* `tag` for `toy` / `smoke` / `mini` subsets used for fast iteration.

### Groups beyond the three — and where a new group BELONGS

A group is *an axis a run selects by name*. When experiments systematically vary something the three
canonical groups can't express, give it a group rather than a flag inside another group. The test:
**would two arms otherwise share a byte-for-byte config differing in one field?** If yes, it is an axis.

But answer a second question before making it a top-level peer:

> **Is it orthogonal to every pipeline, or owned by one?**

`model` and `dataset` are orthogonal — an SFT run, an RL run and an eval run all need a policy and data.
A `reward` is not: only an RL trainer has one, and an eval pipeline has none. Placing it side by side
with model/dataset asserts an orthogonality that does not hold, and the config tree then lies about the
domain. So a group carries **two** placements, and both mean something:

| | encodes | orthogonal axis | owned component |
|---|---|---|---|
| **subdir** | ownership | `config/<group>/` | `config/<owner>/<group>/` |
| **mount path** | scope | `cfg.<group>` | `cfg.<owner>.<group>` |

A nested group still gets its own short selector (`reward_name=judge`) and its own directory — that is
what keeps N arms one slot apart instead of N near-identical owner configs. It also still contributes
its own segment to the run path, because that path expresses run *identity* (which arm is this?), not
the shape of the config tree, and the arms of an ablation must sit side by side to be comparable.

Keep the owner's own glob **non-recursive** (`config/pipeline/*.yaml`) so a nested group's directory
cannot be swallowed by its parent.

### Nothing else is a launcher argument

Every token a launcher passes is a `<group>_name=` selector or a `a.b.c=value` override — **there are
no launcher-only flags**. A `mode=smoke` that quietly rewrites three trainer fields and redirects the
output root is a config masquerading as a flag: it is invisible in the run's `config.yaml`, so two runs
that differ by it can look identical on disk. A smoke run is a *named configuration*
(`dataset_name=healthbench_smoke`, the `tag` slot) with its own hashed run dir.

### Launcher dirs

```
{stage}_{technique}[_{variant_axes...}][_{backbone}]_{scale}[_{specialty_tag}]_{dataset}[_{tag}]
```

* `technique` is the model-class file name with the redundant trailing
  family suffix dropped (`lora_mdm` → `lora`, `quantum_lora_mdm` →
  `quantum_lora`). The pipeline's `stage` already implies the family.
* `specialty_tag` (e.g. `8q`/`16q` for quantum, `8e` for MoE) is
  **required** when the technique uses it — the launcher name must
  mirror the corresponding model-config name so they are visually
  paired. A launcher that omits a slot the model config has is a
  smell — fix the launcher.
* The launcher name = a single string from which the run's purpose is
  obvious; no need to read its `config.yaml`.

## Hard rules

1. **Symmetry between paired runs.** Two arms of an ablation differ in
   name *only* by the slots that describe the change. Never tack on
   qualifiers like `_baseline`, `_v2`, `_test` that say "I am the other
   one". Absence of the variant slot **is** the baseline.
2. **No omitted defaults in YAML.** Every kwarg the loader would
   default goes into the YAML explicitly. Audit with a script that
   instantiates each class via its `class_path` and compares the
   YAML keys against the constructor signature; exit non-zero on any
   gap. Bake into CI.
   *Exception, for a framework config object with hundreds of fields
   (an HF `TrainingArguments` subclass has ~189):* naming them all is
   noise. Name the ones this experiment reasons about, splat the block
   **verbatim** into the constructor so the rest stay reachable, and
   have the run dump the fully-resolved object to `trainer_config.json`.
   Auditability comes from the dump, never from a whitelist.
3. **Code path mirrors the slot grammar.** `<package>/model/<file>.py`
   defines `<ClassName>Model`; `<package>/config/model/<file>/<file>_<scale>.yaml`
   instantiates it. A config name suffix change implies a class file
   rename, and vice versa.
4. **One subdirectory per model class.** Don't mix unrelated classes in
   the same `model/` subdir. The subdir IS the `model_class` slot.
5. **Backbone slot only when loading pretrained weights.** From-scratch
   runs simply omit it. Loading a backbone is a *user-visible*
   event — the name says so.
6. **Output dir is mechanically derived.** Don't let users invent
   per-run output paths. Build it as
   `OUTPUT_DIR / {group.name for each group present} / hash(config)[:8]`
   (e.g. `pipeline/model/dataset/reward/hash`). The hash makes
   CLI-overridden runs disambiguate themselves. The launcher's own log
   goes *inside* this dir — see `layout-output`.
7. **A group config is selected by its `name:` field, not its filename.**
   Glob `config/<group>/*.yaml` and match `<group>.name`; a missing name
   is an error and a **duplicate name is a hard error**. Keep the filename
   equal to the name by convention, but let the loader enforce uniqueness
   so a config can never be silently shadowed by a copy.
8. **A group's settings live under that group's key.** No second
   top-level home for the same concern (`pipeline.eval.*`, never a
   free-floating `eval:`). One rule means an override path is always
   predictable from the group name.
9. **The CLI/launcher overrides the YAML, at any depth.** Merge argv
   *last* over the group configs, with no allowlist of what may be
   overridden. If a launcher cannot set a field without a code change,
   the config system is broken, not the launcher.

## Steps when adding / reviewing a config

1. Identify which slot grammar applies (model / pipeline / dataset / launcher).
2. Fill in the slots from the actual class / pipeline / data source.
3. Check the file name lives in the right subdir.
4. Cross-check a paired config (the natural ablation companion). Names
   should differ in exactly the new slot.
5. Run the audit (or the project's equivalent of
   `tools/audit_config_completeness.py`) before committing.
6. If a slot can't be expressed, the slot grammar is wrong — extend it
   in this skill *and* in the project's ARCH doc. Don't just override
   ad-hoc.

## Anti-patterns

* `_v2`, `_new`, `_test`, `_baseline` suffixes — say what's *different*,
  not "this is the other one".
* Mixing model classes in one config subdir (e.g. lumping LoRA-only and
  LoRA+quantum into `quantum_lora/`).
* Dataset YAML missing a `validate:` block (use `validate: null` to make
  "no val" explicit).
* Pipeline YAML duplicating an existing one byte-for-byte (delete; reuse
  via `class_path`).
* **Near-duplicate group configs differing by ONE flag** (`grpo.yaml` vs
  `grpo_with_fix.yaml` where only `enable_fixes` differs). That flag is a
  separate axis: promote it to its own group and let the arms name
  different configs. Otherwise retuning the trainer means editing N files
  and they silently drift.
* **A branch in the pipeline that selects the arm** (`if cfg.reward_kind
  == "opd": ...`). The arm is config; the code should not know which arm
  it is running.
* **A pipeline-owned concern promoted to a top-level peer** (a `reward/`
  group beside `model/` and `dataset/`) — it claims an orthogonality
  that does not exist, since an eval pipeline has no reward. Nest it
  under its owner and keep the selector.
* **A launcher-only flag** (`mode=smoke`, `--debug`) that expands into
  config changes. It never appears in the run's frozen `config.yaml`, so
  two materially different runs become indistinguishable on disk.
* **Ambiguous env-var names shared by two subsystems.** When a trainer
  and its judge are both vLLM, a bare `VLLM_BASE_URL` names neither;
  prefix by ROLE (`JUDGE_BASE_URL`) so a misconfiguration is a loud
  mismatch instead of a silently wrong number.
* Launcher dir name that doesn't tell you which model + dataset will run.

## Output

When invoked:
- State the slot grammar that applies.
- List the slots and their values for the proposed name.
- Compare against any sibling configs to verify symmetry.
- Confirm the audit script (or its absence + the need to add one).
- Brief summary of the chosen name + path.

## References
- Project example: `/home/toolkit/QDiffMDM/doc/ARCH.md` §"Naming
  conventions" — full instantiation of this pattern for a quantum-MDM /
  LoRA codebase.
