---
name: platform-run
description: "Specify a run once in launcher/<name>/task.yaml and let skylaunch render and route it to PAI DLC, PAI DSW or the local box (its Slurm and EAI backends are stubs that raise). A project ships task specs, and at most one optional platform file per scheduler family for a fact only it has. Account, quota, image, driver and mounts belong to the cluster and are resolved at submit time, and an env value that differs by silicon is a by_accelerator map the cluster resolves."
when_to_use: "Use when adding a launcher or wiring remote submission, when a submit is rejected for a field the spec should not have carried, when deciding whether something belongs in the task spec or in the cluster stack, when running a launcher on this box, or when an env value must differ by accelerator. Not for choosing WHICH cluster to submit to, not for diagnosing a driver or image failure once the job is already running, and not for how a run variant is represented (config-variants)."
---
# Skill: platform-run

## Purpose
A run is specified **once**, in `launcher/<name>/task.yaml`, in terms that mean the same thing on
every scheduler. Everything that is *not* portable — account, workspace, quota, image, driver,
region, partition, mounts — is a property of the cluster rather than of the run, and is resolved by
skylaunch at submit time.

**That is the entire interface. A project ships task specs**, and at most one optional platform
file for a fact that is genuinely its own ([below](#what-the-cluster-owns-and-why-a-spec-must-not-restate-it)).
No copied profile, no renderer, no submit adapter, no follow loop. This skill is the contract for
what a spec may say and what it must leave to the cluster.

## Contents
- [When to Use](#when-to-use)
- [The interface: one spec per run](#the-interface-one-spec-per-run)
- [What the cluster owns, and why a spec must not restate it](#what-the-cluster-owns-and-why-a-spec-must-not-restate-it)
- [Field → platform mapping](#field--platform-mapping)
- [Per-cluster env values: by_accelerator](#per-cluster-env-values-by_accelerator)
- [Local runs: the same spec on this box](#local-runs-the-same-spec-on-this-box)
- [Resources: a total, not a layout](#resources-a-total-not-a-layout)
- [Where the implementation lives](#where-the-implementation-lives)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Adding a launcher, or wiring a project up to remote submission.
- A submit is rejected, or a job lands with the wrong image, driver or quota.
- Deciding whether a field belongs in the task spec or in the cluster stack.
- The user says "submit this to the cluster", "launch a job", "make it run on Slurm too". The last
  one is a port inside skylaunch (Rule 3), because its Slurm backend is a stub today.
- An env value, such as the venv name, has to differ between CUDA and PPU pools.
- Running a launcher on this machine's GPUs from the same spec the cluster uses.
- NOT for choosing *which* cluster has room, or for moving a stuck submission elsewhere. NOT for diagnosing a CUDA / driver / ABI failure in a job that is
  already running — that is `platform-runtime`. NOT for naming the launcher — `naming-config`.
  NOT for how a run variant is represented (a smoke, a probe, a grid cell, a config field that
  differs per cluster), which is `config-variants`.

## The interface: one spec per run

`launcher/<name>/task.yaml`, in the SkyPilot task-YAML schema — adopted rather than invented,
because it is well designed, documented, and already understood by tooling.

```yaml
name: <launcher-name>              # = the launcher dir (see naming-config)
resources:
  accelerators: "gpu:8"            # <type>:<count-per-node>
  cpus: 64
  memory: 512                      # GiB
num_nodes: 2
setup: |                           # optional, run once before the job
  ...
run:                               # an argv LIST of k=v, never a shell string
  - bash
  - launcher/launch.sh
  - pipeline_name=...
envs:                              # OS/user env vars
  HF_ENDPOINT: https://hf-mirror.com
mode: batch                        # batch | interactive; picks the backend verb set
runtime: serving                   # optional NAMED stack from the cluster's `runtimes:`
workdir: .                         # optional
platform:                          # THE ESCAPE HATCH, namespaced by family
  pai:   { gpu_type: A100-80G, driver: "" }
  slurm: { partition: gpu-long }
```

The allowed set is exactly `name, resources, num_nodes, envs, run, workdir, setup, mode, runtime,
file_mounts, platform`, and within `resources`: `accelerators, cpus, memory, disk_size,
instance_type, use_spot`. **Anything else is rejected rather than silently dropped** — a typo in a
spec should stop the launch, not reach a job file nobody reads.

**`platform:` is namespaced by family on purpose.** `platform.pai.driver` reads as "PAI-specific,
portable nowhere", which is honest, where a bare top-level `driver:` reads as a property of the task,
which is a lie. A spec may carry blocks for several families at once and each ignores the others, so
adding a platform never edits an existing spec. Prefer not to use it at all: it exists for the one
task that genuinely differs, and anything true of a whole cluster belongs to the cluster.

**`file_mounts` is advisory and read by no translator.** Mounts come from the cluster's
`data_sources`, because which datasets exist is a property of the cluster, not of a task. The field
survives as documentation of intent, so do not expect editing it to change what gets mounted.

## What the cluster owns, and why a spec must not restate it

Account, workspace, quota / resource id, data-source ids, container image, GPU driver, region,
partition, qos. These live in skylaunch's shared stack, one file per family covering every project.

Two of them are worth naming, because a spec that restates them fails in ways that are expensive to
read. **Mounts**, per above. And **image identity**, which on PAI is two fields for one image: a
catalog `image_id` (what the console calls an "Alibaba Cloud Image") and the full registry
`worker_image` address. They must name the same image, because the two modes select differently —
DSW validates an id against the catalog, while an unresolvable *address* is accepted as a "custom
image" and fails only at pull time, once the pod is already gone.

**A project rarely ships a platform file, and never a copy of the stack.** skylaunch reads one
optional layer over the shared stack, `<project>/platform/<family>.yaml` (found through
`$SKYLAUNCH_PROJECT_HOME/platform`, else `./platform`, and still read under the older per-mode names
such as `dlc.yaml`). It is for a fact that is genuinely the project's own, such as its `rotation:`
policy, a pool no other project uses, or one field of a shared cluster changed through
`driver_by_cluster`, `gpu_type_by_cluster` or `worker_image_by_cluster`. Most projects never need
one. Where the stack is genuinely wrong for a cluster, the fix is
in the stack, so every project on that cluster gets it — a per-project override is a second copy
that drifts, and it drifts silently, because nothing re-reads it to compare. If a value is true of
one *task* rather than one cluster, it goes in that task's `platform.<family>` block, which is what
the escape hatch is for.

## Field → platform mapping

What each translator does with a neutral field. Useful when reading a rendered artifact, or when a
submission lands with resources you did not expect.

**Only the DLC column runs today.** skylaunch's Slurm and EAI backends are stubs whose every verb
raises `NotImplementedError`, and neither family has a `stacks.yaml` yet. Their columns record what
the projects' own translators did before those were deleted in favour of skylaunch, which is the
mapping a port has to reproduce, not what a submit does now.

| neutral | DLC job_file | Slurm sbatch (stub) | EAI yaml (stub) |
|---|---|---|---|
| `num_nodes` | `workers` | `--nodes` | (implicit) |
| `resources.accelerators` count | `worker_gpu` (+`NPROC_PER_NODE`) | `--gpus-per-node` | `resources.gpu` |
| `resources.accelerators` type | *omitted* — DLC quotas are GPU-type-locked (`resource_id` pins it); passing `worker_gpu_type` errors `GPUType should be in []`. Advisory only. | `--gres=gpu:<t>:<n>` | `resources.gpuModel` |
| `resources.cpus` | `worker_cpu` | `--cpus-per-task` | `resources.cpu` |
| `resources.memory` | `worker_memory=<n>Gi` | `--mem=<n>G` | `resources.mem` |
| `run` | `command` | script body / `srun` | `command` |
| `envs` | `envs=k=v,…` | `export` / `--export` | `environmentVars:[k=v]` |
| `envs.<K>.by_accelerator` | collapsed to the branch the cluster's `accelerator:` names, then encoded as `envs` ([below](#per-cluster-env-values-by_accelerator)) | not ported | not ported |
| `file_mounts` | *ignored* — mounts come from the cluster's `data_sources` | bind / shared FS | `--data ac.user:/path` |
| `runtime` | selects a named stack from the cluster's `runtimes:` | (n/a) | (n/a) |
| `platform.<family>` | merged last, over everything | same | same |
| (account/quota/image/driver) | `workspace_id`,`resource_id`,`worker_image`,`--driver` | `--account`,`--partition` | `account`,`--image` |

Bottom row is **from the cluster, not the spec.** Precedence, lowest to highest: the shared stack
and the project's optional `platform/<family>.yaml` merged section by section, then the selected
cluster entry, the `<key>_by_cluster` overrides, the operator's `<cluster>_<KEY>` env
vars, the named `runtime`, and last the task's own `platform.<family>`. The task's `envs` merge key
by key over the cluster's, so a cluster can carry fabric tunables (`NCCL_IB_*`) that a single task
may still override.

## Per-cluster env values: by_accelerator

An `envs` value in a task spec may be a map instead of a string, when what the job needs differs by
silicon. Today it carries one value, the project's venv name, because a venv is compiled for one
accelerator's ABI (`platform-runtime`):

```yaml
envs:
  UV_VENV_PROJECT:
    by_accelerator:
      cuda: autorsi_trl
      ppu: autorsi_trl_ppu
```

skylaunch collapses the map to the one string the target cluster's declared `accelerator:` names.
Every PAI cluster in `platforms/pai/stacks.yaml` declares one (`cuda` or `ppu`), and the local box
declares its own in `platforms/local/stacks.yaml`, written by hand rather than detected, because a
wrong guess activates a CUDA venv on PPU silicon and fails far from the cause. The spec stays
cluster-unaware and the cluster picks the branch. There is no fallback. A map with no
`by_accelerator` table, a cluster that declares no `accelerator:`, and a kind the table does not
list each stop the launch with an error naming what is missing.

Where it resolves, and where it does not:

| path | resolved? |
|---|---|
| DLC (PAI batch) | yes, over the merged envs, the cluster's under the task's |
| local, attached or detached | yes, over the task's envs, against `platforms/local/stacks.yaml` |
| DSW (PAI interactive) | **no**. The backend writes `str()` of the map, so the box gets the Python repr of the dict as the variable's value, and an entrance that reads it as a venv name finds no such venv |
| Slurm, EAI | no backend to resolve it ([stubs](#field--platform-mapping)) |

It applies to `envs` values and nothing else. `resources`, `run` and `platform.<family>` are read as
written, whatever the cluster's accelerator. A config field that differs per cluster is not an env
value. It is a named config, which `config-variants` owns.

## Local runs: the same spec on this box

The local box is a skylaunch family like PAI, so a local run reads the same `task.yaml` the cluster
does, through `skylaunch run <launcher>`, which projects wrap as `make run LAUNCHER=<name>`. Where a
run happens is a choice of command, not a second launcher file (`config-variants` owns the one
exception, a forced code-path change). The mode axis keeps its meaning. The default is attached
(interactive) and streams to the terminal, and `--detach` (`DETACH=1`) is batch, returning an id for
a run that outlives the shell.

- **What carries over.** `envs`, with `by_accelerator` resolved against `platforms/local/stacks.yaml`,
  and `run`, so the box executes the same argv through the same entrance. `--set k=v` (`SET_ARGS`)
  appends to that argv exactly as it does on `submit`, so a local reproduction of a queued job is the
  same command.
- **What is dropped.** The remote-placement fields `resources`, `num_nodes`, `file_mounts`, `workdir`,
  `setup`, `platform` and `max_minutes`. The banner names the ones a spec carried.
- **Which cards.** `--gpus` (`GPUS=`) takes a count, where 0 means every card with enough free memory,
  or an explicit set such as `8-15`. Cards are picked by free memory rather than index, and a pinned
  card that is busy is refused, because other jobs share the box and a busy card produces an OOM that
  reads like a bug in the run.
- **World size follows the cards.** `NPROC_PER_NODE` and `CUDA_VISIBLE_DEVICES` come from the cards
  taken, never from `resources`, so a 2-card run is a smaller world than the spec's total and its
  per-gradient batch shrinks with it ([Resources](#resources-a-total-not-a-layout)). That is fine for
  a smoke, which asks whether a path executes, not whether the recipe trains.
- **No snapshot.** A cluster job is frozen against edits while it queues. A local run starts now,
  against the working tree, so it tests the edit you just made.

## Resources: a total, not a layout

A spec's `num_nodes × accelerators` is a **total world size**, and the platform layer re-splits it
against the target pool's node shape — 16 accelerators is one node on a 16-card pool and two on an
8-card pool, the same experiment either way. Never encode a pool's node count in a launcher: batch
algebra depends on `num_processes`, so a layout baked for one pool silently becomes a different
recipe on the next. See `platform-runtime` for the invariant and its RNG caveat.

## Where the implementation lives

`$PROJECTS_HOME/skylaunch` (github.com/Robert-xiaoqiang/skylaunch). This file is the *contract*;
that repo is the implementation, and the two are meant to stay consistent. Read the code as ground
truth when they disagree, then fix whichever is wrong — this file has drifted from it before.

The map, for orientation: `core/spec.py` holds the allowed field set and the validation that rejects
anything else, `core/profile.py` the layer merge, `core/mode.py` the batch/interactive verb
vocabulary, and `platforms/<family>/` one backend per mode (`pai/dlc.py`, `pai/dsw.py`) over a single
shared `stacks.yaml`, with `local/` built the same way for this machine. `slurm/` and `eai/` hold
stubs that raise and have no stack.
**Adding a platform is work inside skylaunch** — one backend and one stack —
never a renderer, spec dialect or submit script inside a project.

`scripts/checks/interface.py` renders every real project `task.yaml` against each PAI GPU pool the
gate lists (`a100`, `a800`, `ppu` today), through the DLC translator, with no scheduler needed.
Rendering is a pure function of (spec, stack), which is why the whole gate runs on
a laptop, and why a golden-file test of a translator never needs a cluster.

Both modes read one stack on purpose: a DSW box and a DLC job on the same cluster share its
workspace, quota, mounts, image and driver, so debugging interactively on the box you will later
submit to actually proves something. When they diverge that guarantee is silently gone, and
`skylaunch drift` exists to catch it, since nothing re-reads the stack during a long-lived
instance's life. One difference is in the code today. DSW does not resolve `by_accelerator` env
values, so a DSW box does not get the venv a DLC job on the same cluster gets
([by_accelerator](#per-cluster-env-values-by_accelerator)).

## Rules
1. **A task spec carries zero platform IDs.** If you are tempted to put a workspace, quota, or
   data-source id in one, it belongs to the cluster.
2. **A project's run-control surface is `launcher/<name>/task.yaml`**, plus an optional
   `platform/<family>.yaml` only for a fact the shared stack cannot hold. No copied profile,
   renderer, submit adapter or follow loop — those exist once, in skylaunch, and a second copy is a
   second thing to keep correct.
3. **Adding a platform is one backend plus one stack, inside skylaunch**, never a second spec
   dialect.
4. **`--dry-run` before a real submit**, and read the rendered artifact. Rendering needs no cluster,
   so there is no excuse for finding a bad field after the queue.
5. **Submitting consumes shared quota and is outward-facing** — confirm before firing real jobs.
6. **The node GPU driver is as load-bearing as the image** and is selectable per job (DLC
   `--driver`). Read a CUDA / driver / symbol error as a layer mismatch to diagnose, not an
   impossible request (`platform-runtime`).
7. **A launcher never encodes a pool's node count** ([Resources](#resources-a-total-not-a-layout)).
8. **An env value that differs by silicon is a `by_accelerator` map**, resolved by the cluster's
   declared accelerator on DLC and local only
   ([by_accelerator](#per-cluster-env-values-by_accelerator)).

## Anti-patterns
- **Rebuilding the engine in the project.** A renderer, a `_common.sh`, a per-scheduler submit
  script. It feels like ownership; it is a fork of a tested component that now has to be kept in step
  with a scheduler's API by whoever is on call at 3am.
- **A per-launcher `launch.sh`** beside each `task.yaml`. It copies the shared entrance, and where
  that entrance lives is `layout-workspace`'s rule.
- **Trusting a DSW box to resolve `by_accelerator`.** It receives the map's repr as the value. Set
  the resolved string on the box yourself, or test on local or DLC, which do resolve it.
- **A shell string in `run:`.** It is an argv list; a string re-introduces quoting bugs the list
  exists to remove.
- **Restating a cluster fact in a task**, because one submission needed it once. It is true until
  the cluster changes and then it is a lie in a file nobody re-reads.
- **Editing `file_mounts` to change what gets mounted.** It is advisory; the mount did not move, and
  the next reader will believe it did.
- **Trusting a submit's exit code.** A quiet command may have done nothing at all — re-query the job
  listing and report the queried state.

## Companions
`naming-config` (the launcher's *name* + config triple) · `layout-workspace` (where `launcher/`
lives, and the config tree it selects from) · `platform-runtime` (the driver/image/venv stack the job
runs on, and why a run is or is not portable to other silicon) · `platform-env` (the machine env the stack
assumes) · `platform-migrate` (moving the persistent home the stack points at) · `config-variants`
(how a run variant is represented, including a config field that differs per cluster) ·
`conventions` (the family index).
