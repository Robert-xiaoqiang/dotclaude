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
   `OUTPUT_DIR / {pipeline.name} / {model.name} / {dataset.name} / hash(config)[:8]`.
   Hash makes CLI-overridden runs disambiguate themselves.

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
