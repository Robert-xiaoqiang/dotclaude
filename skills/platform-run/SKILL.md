---
name: platform-run
description: "Specify a run once in launcher/<name>/task.yaml and let skylaunch render and route it to whatever scheduler is available - PAI DLC, Slurm, EAI, local. A project ships task specs and nothing else: account, quota, image, driver and mounts belong to the cluster and are resolved at submit time."
when_to_use: "Use when adding a launcher or wiring remote submission, when a submit is rejected for a field the spec should not have carried, or when deciding whether something belongs in the task spec or in the cluster stack. Not for choosing WHICH cluster to submit to, and not for diagnosing a driver or image failure once the job is already running."
---
# Skill: platform-run

## Purpose
A run is specified **once**, in `launcher/<name>/task.yaml`, in terms that mean the same thing on
every scheduler. Everything that is *not* portable — account, workspace, quota, image, driver,
region, partition, mounts — is a property of the cluster rather than of the run, and is resolved by
skylaunch at submit time.

**That is the entire interface. A project ships task specs and nothing else.** No profile file, no
renderer, no submit adapter, no follow loop. This skill is the contract for what a spec may say and
what it must leave to the cluster.

## Contents
- [When to Use](#when-to-use)
- [The interface: one spec per run](#the-interface-one-spec-per-run)
- [What the cluster owns, and why a spec must not restate it](#what-the-cluster-owns-and-why-a-spec-must-not-restate-it)
- [Field → platform mapping](#field--platform-mapping)
- [Resources: a total, not a layout](#resources-a-total-not-a-layout)
- [Where the implementation lives](#where-the-implementation-lives)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- Adding a launcher, or wiring a project up to remote submission.
- A submit is rejected, or a job lands with the wrong image, driver or quota.
- Deciding whether a field belongs in the task spec or in the cluster stack.
- The user says "submit this to the cluster", "launch a job", "make it run on Slurm too".
- NOT for choosing *which* cluster has room, or for migrating a stuck submission — that is
  `platform-queue-shepherd`. NOT for diagnosing a CUDA / driver / ABI failure in a job that is
  already running — that is `platform-runtime`. NOT for naming the launcher — `naming-config`.

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

**A project does not ship a profile.** Where the stack is genuinely wrong for a cluster, the fix is
in the stack, so every project on that cluster gets it — a per-project override is a second copy
that drifts, and it drifts silently, because nothing re-reads it to compare. If a value is true of
one *task* rather than one cluster, it goes in that task's `platform.<family>` block, which is what
the escape hatch is for.

## Field → platform mapping

What each translator does with a neutral field. Useful when reading a rendered artifact, or when a
submission lands with resources you did not expect.

| neutral | DLC job_file | Slurm sbatch | EAI yaml |
|---|---|---|---|
| `num_nodes` | `workers` | `--nodes` | (implicit) |
| `resources.accelerators` count | `worker_gpu` (+`NPROC_PER_NODE`) | `--gpus-per-node` | `resources.gpu` |
| `resources.accelerators` type | *omitted* — DLC quotas are GPU-type-locked (`resource_id` pins it); passing `worker_gpu_type` errors `GPUType should be in []`. Advisory only. | `--gres=gpu:<t>:<n>` | `resources.gpuModel` |
| `resources.cpus` | `worker_cpu` | `--cpus-per-task` | `resources.cpu` |
| `resources.memory` | `worker_memory=<n>Gi` | `--mem=<n>G` | `resources.mem` |
| `run` | `command` | script body / `srun` | `command` |
| `envs` | `envs=k=v,…` | `export` / `--export` | `environmentVars:[k=v]` |
| `file_mounts` | *ignored* — mounts come from the cluster's `data_sources` | bind / shared FS | `--data ac.user:/path` |
| `runtime` | selects a named stack from the cluster's `runtimes:` | (n/a) | (n/a) |
| `platform.<family>` | merged last, over everything | same | same |
| (account/quota/image/driver) | `workspace_id`,`resource_id`,`worker_image`,`--driver` | `--account`,`--partition` | `account`,`--image` |

Bottom row is **from the cluster, not the spec.** Precedence, lowest to highest: shared stack,
cluster entry, named `runtime`, then the task's own `platform.<family>`. `envs` merge in that order
too, so a cluster can carry fabric tunables (`NCCL_IB_*`) that a single task may still override.

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
shared `stacks.yaml`. **Adding a platform is work inside skylaunch** — one backend and one stack —
never a renderer, spec dialect or submit script inside a project.

`scripts/checks/interface.py` renders every real project `task.yaml` against every cluster with no
scheduler needed. Rendering is a pure function of (spec, stack), which is why the whole gate runs on
a laptop, and why a golden-file test of a translator never needs a cluster.

Both modes read one stack on purpose: a DSW box and a DLC job on the same cluster share its
workspace, quota, mounts, image and driver, so debugging interactively on the box you will later
submit to actually proves something. When they diverge that guarantee is silently gone, and
`skylaunch drift` exists to catch it, since nothing re-reads the stack during a long-lived
instance's life.

## Rules
1. **A task spec carries zero platform IDs.** If you are tempted to put a workspace, quota, or
   data-source id in one, it belongs to the cluster.
2. **A project's run-control surface is `launcher/<name>/task.yaml` and nothing else.** No profile,
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
7. **A launcher never encodes a pool's node count**, because `num_nodes × accelerators` is a total
   that gets re-split per pool.

## Anti-patterns
- **Rebuilding the engine in the project.** A renderer, a `_common.sh`, a per-scheduler submit
  script. It feels like ownership; it is a fork of a tested component that now has to be kept in step
  with a scheduler's API by whoever is on call at 3am.
- **A per-launcher `launch.sh`** beside each `task.yaml`. Redundant, and it drifts. One shared
  in-pod entrance serves every pipeline.
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
runs on, and why a run is or is not portable to other silicon) · `platform-queue-shepherd` (which
cluster to submit to, and when to move a stuck claim) · `platform-env` (the machine env the stack
assumes) · `platform-migrate` (moving the persistent home the stack points at) · `conventions` (the
family index).
