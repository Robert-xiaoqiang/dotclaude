# Skill: platform-run

## Purpose
Specify a run **once** in a platform-neutral job spec and **render/route** it to whatever
scheduler is available (Alibaba PAI **DLC**, **Slurm**, ServiceNow **EAI**, Kubernetes, a
cloud). Keeps the *logical* run request portable and pushes all platform-specific
account/quota/image detail into a separate profile, so the same launcher runs anywhere by
changing one flag. This is the run-control layer that sits under the launcher.

## When to Use
- Adding a launcher / a remote run, or wiring remote submission.
- Adding support for a new platform (write one translator, not a new spec).
- Reviewing how a run maps onto a scheduler's native job format.
- The user says: "submit this to the cluster", "launch a job", "make it run on Slurm too".

## Core principle
**One neutral spec × a platform profile → a native submission.** The neutral spec never
contains platform IDs (workspace/quota/data-source ids, image registry, partition). Those
live in the platform profile. A translator combines the two into the scheduler's native
artifact (DLC `job_file`, Slurm `sbatch`, EAI yaml) and submits it.

## The neutral spec — `launcher/<name>/task.yaml`
Adopt the **SkyPilot task-YAML schema** (do not invent a new one — it is well-designed,
documented, and already understood by tooling):

```yaml
name: <launcher-name>              # = the launcher dir (see naming-config)
resources:
  accelerators: A100-80G:8         # <gpu_type>:<count-per-node>
  cpus: 64
  memory: 512                      # GiB
num_nodes: 2
setup: |                           # optional, run once before the job
  ...
run: |                             # the job command(s); rank/world env injected by the platform
  bash scripts/launch.sh model_name=... pipeline_name=... dataset_name=...
envs:                              # OS/user env vars
  HF_ENDPOINT: https://hf-mirror.com
  OUTPUT_DIR: ${OUTPUT_DIR_HOME}/<project>
file_mounts: { /data: cpfs }       # ADVISORY only — see the note below
mode: batch                        # batch | interactive; picks the backend verb set
runtime: serving                   # optional NAMED stack from the profile's `runtimes:`
workdir: .                         # optional
platform:                          # THE ESCAPE HATCH, namespaced by family
  pai:   { gpu_type: A100-80G, driver: "" }
  slurm: { partition: gpu-long }
```

`platform:` is namespaced by family on purpose. `platform.pai.driver` reads as "PAI-specific,
portable nowhere", which is honest, where a bare top-level `driver:` reads as a property of the
task, which is a lie. A spec may carry blocks for several families at once and each ignores the
others, so adding a platform never edits an existing spec. Prefer not to use it: anything true
of every task in a project belongs in that project's `platform/<family>.yaml`, and anything true
of a whole cluster belongs in the shared stack. It is for the one task that differs.

**`file_mounts` is advisory and read by no translator.** Mounts come from the profile's
`data_sources`, because which datasets exist is a property of the cluster, not of a task. It
survives as documentation of intent, so do not expect editing it to change what gets mounted.

Anything outside the allowed set is rejected rather than silently dropped — a typo in a spec
should stop the launch, not reach a job file nobody reads.

## The platform profile — the shared stack
Non-portable, platform-specific: account / workspace / quota (resource) id / data-source ids /
container image / driver / region / partition / qos. In skylaunch this is
`skylaunch/platforms/<family>/stacks.yaml`, one file shared by every project, with a project's
own `platform/<family>.yaml` layered over it only where it genuinely differs.

Two things belong here that a task must never carry. **Mounts**, per above. And **image
identity**, which on PAI means two fields for one image: a catalog `image_id` (what the console
calls an "Alibaba Cloud Image") and the full registry `worker_image` address. They must name the
same image, because the two modes select differently — DSW validates an id against the catalog,
while an unresolvable *address* is accepted as a "custom image" and fails only at pull time,
once the pod is already gone. A check that they agree is worth having.

## The engine — three layers, share what's shareable
Factor by *what actually varies per platform*. Only native submit/status/logs differ; the
rest is shared. Do NOT let each platform script re-implement parsing, rendering, snapshot,
or the follow loop (the classic smell — two `dlc.sh`/`eai.sh` that each duplicate everything).

1. **Render (neutral → native) — SHARED, in Python, tested.** `<pkg>/platform/`:
   `jobspec.py` (load+validate `task.yaml`, expand `${VAR}`), `profile.py` (load
   `scripts/platform/<platform>.yaml`, else a legacy env fallback), `translate/<platform>.py`
   (pure `render(spec, profile, *, snapshot, jobname) -> native text`), and `render.py`
   — one CLI that **dispatches by `--platform`** to the right translator. Golden-file
   tested; no cluster needed.
2. **Orchestration (snapshot + follow) — SHARED, in shell.** `scripts/platform/_common.sh`:
   `snapshot_repo <dest>` (rsync the repo for FS-based platforms), `render_artifact <platform> …`
   (calls `render.py`), and `follow_loop <jobid>` (poll→terminal, streaming new logs) that
   calls caller-provided `plat_status`/`plat_logs` hooks.
3. **Native submit/status/logs — PER-PLATFORM, thin.** `scripts/platform/<platform>.sh`
   (~40 lines): resolve the profile, `render_artifact`, `snapshot_repo` (or the platform's
   own code-push), then the native `submit`, and define the `plat_status`/`plat_logs` hooks.
   Same subcommand contract (`submit|auto|follow|logs|status|stop|jobs|print`) so the
   Makefile is platform-invariant. `--dryrun` prints the native artifact without submitting.

**Litmus test:** adding a platform touches exactly `translate/<p>.py` (+ a `render.py`
branch) and a thin `<p>.sh` adapter — never a second spec dialect, snapshot, or follow loop.

## Field → platform mapping (what each translator does)
| neutral | DLC job_file | Slurm sbatch | EAI yaml |
|---|---|---|---|
| `num_nodes` | `workers` | `--nodes` | (implicit) |
| `resources.accelerators` count | `worker_gpu` (+`NPROC_PER_NODE`) | `--gpus-per-node` | `resources.gpu` |
| `resources.accelerators` type | *omitted* — DLC quotas are GPU-type-locked (`resource_id` pins it); passing `worker_gpu_type` errors `GPUType should be in []`. Advisory only. | `--gres=gpu:<t>:<n>` | `resources.gpuModel` |
| `resources.cpus` | `worker_cpu` | `--cpus-per-task` | `resources.cpu` |
| `resources.memory` | `worker_memory=<n>Gi` | `--mem=<n>G` | `resources.mem` |
| `run` | `command` | script body / `srun` | `command` |
| `envs` | `envs=k=v,…` | `export` / `--export` | `environmentVars:[k=v]` |
| `file_mounts` | *ignored* — mounts come from the profile's `data_sources` | bind / shared FS | `--data ac.user:/path` |
| `runtime` | selects a named stack from the profile's `runtimes:` | (n/a) | (n/a) |
| `platform.<family>` | merged last, over everything | same | same |
| (account/quota/image/driver) | `workspace_id`,`resource_id`,`worker_image`,`--driver` | `--account`,`--partition` | `account`,`--image` |

Bottom row is **from the profile, not the spec.** Precedence, lowest to highest: shared stack,
project override, cluster entry, named `runtime`, then the task's own `platform.<family>`.
`envs` merge in that order too, so a cluster can carry fabric tunables (`NCCL_IB_*`) that a
single task may still override.

## Resources: a total, not a layout

A neutral spec's `num_nodes x accelerators` is a **total world size**, and the platform layer
re-splits it against the target pool's node shape — 16 accelerators is one node on a 16-card pool
and two on an 8-card pool, the same experiment either way. Never encode a pool's node count in a
launcher: batch algebra depends on `num_processes`, so a layout baked for one pool silently becomes
a different recipe on the next. See `platform-runtime` for the invariant and its RNG caveat.

## Rules
1. The neutral `task.yaml` contains **zero** platform IDs. If you're tempted to put a
   workspace/quota/data-source id in it, it belongs in the profile.
2. Adding a platform = **add one translator + one profile**, never a second spec dialect.
3. **Golden-file test every translator** (a `task.yaml` → expected native artifact); no
   cluster needed. Always `--dryrun` before a real submit.
4. Submitting consumes shared quota (outward-facing) — confirm before firing real jobs.
5. Prefer an existing engine for platforms it supports (SkyPilot drives Slurm/K8s/clouds);
   write a translator only for platforms it doesn't (e.g. DLC, EAI).
6. The node **GPU driver** is as load-bearing as the image and is selectable per job (DLC
   `--driver`). Pin it explicitly in the profile beside `worker_image`, and read a CUDA /
   driver / symbol error as a layer mismatch to diagnose, not an impossible request
   (`platform-runtime`).

## The implementation: skylaunch
This skill is the *contract*; `$PROJECTS_HOME/skylaunch` (github.com/Robert-xiaoqiang/skylaunch)
is the implementation, and the two are meant to stay consistent. Read the code as the ground
truth when they disagree, then fix whichever is wrong — this file has drifted from it before.

The map, for orientation: `core/spec.py` holds the allowed field set and the validation that
rejects anything else, `core/profile.py` the layer merge described above, `core/mode.py` the
batch/interactive verb vocabulary, and `platforms/<family>/` one backend per mode
(`pai/dlc.py`, `pai/dsw.py`) over a single shared `stacks.yaml`. `scripts/checks/interface.py`
renders every real project `task.yaml` against every cluster with no scheduler needed, which is
the golden-file test rule below made executable.

Both modes read one stack on purpose: a DSW box and a DLC job on the same cluster share its
workspace, quota, mounts, image and driver, so debugging interactively on the box you will later
submit to actually proves something. When they diverge, that guarantee is silently gone —
`skylaunch drift` exists to catch exactly that, since nothing re-reads the stack during a
long-lived instance's life.

## Companions
`naming-config` (the launcher's *name* + config triple) · `layout-workspace` (where
`launcher/` and `scripts/platform/` live) · `platform-runtime` (the driver/image/venv stack the
job runs on) · `platform-env` (the machine env the profile assumes) · `platform-migrate` (moving
the persistent home the profile points at) · `conventions` (the family index).
