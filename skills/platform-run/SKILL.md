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
file_mounts: { /data: cpfs }       # logical mounts; the profile resolves to real ids/paths
```

## The platform profile — `platforms/<platform>.yaml`
Non-portable, platform-specific: account / workspace / quota (resource) id / data-source
ids / container image / region / partition / qos. (Generalizes an ad-hoc `*_clusters.env`.)

## The engine — `<pkg>/platform/`
- `jobspec.py` — load + validate `task.yaml`, expand `${VAR}`.
- `profile.py` — load `platforms/<platform>.yaml`.
- `translate/<platform>.py` — `render(spec, profile) -> (native_artifact, submit_argv)`.
- `submit.py` — CLI: pick translator by `--platform`; `--dryrun` prints the native artifact
  without submitting. The Makefile's remote targets and `scripts/platform/<p>.sh` are thin
  wrappers over this.

## Field → platform mapping (what each translator does)
| neutral | DLC job_file | Slurm sbatch | EAI yaml |
|---|---|---|---|
| `num_nodes` | `workers` | `--nodes` | (implicit) |
| `resources.accelerators` count | `worker_gpu` (+`NPROC_PER_NODE`) | `--gpus-per-node` | `resources.gpu` |
| `resources.accelerators` type | `worker_gpu_type` | `--gres=gpu:<t>:<n>` | `resources.gpuModel` |
| `resources.cpus` | `worker_cpu` | `--cpus-per-task` | `resources.cpu` |
| `resources.memory` | `worker_memory=<n>Gi` | `--mem=<n>G` | `resources.mem` |
| `run` | `command` | script body / `srun` | `command` |
| `envs` | `envs=k=v,…` | `export` / `--export` | `environmentVars:[k=v]` |
| `file_mounts` | `data_sources=<ids>` | bind / shared FS | `--data ac.user:/path` |
| (account/quota/image) | `workspace_id`,`resource_id`,`worker_image` | `--account`,`--partition` | `account`,`--image` |

Bottom row is **from the profile, not the spec.**

## Rules
1. The neutral `task.yaml` contains **zero** platform IDs. If you're tempted to put a
   workspace/quota/data-source id in it, it belongs in the profile.
2. Adding a platform = **add one translator + one profile**, never a second spec dialect.
3. **Golden-file test every translator** (a `task.yaml` → expected native artifact); no
   cluster needed. Always `--dryrun` before a real submit.
4. Submitting consumes shared quota (outward-facing) — confirm before firing real jobs.
5. Prefer an existing engine for platforms it supports (SkyPilot drives Slurm/K8s/clouds);
   write a translator only for platforms it doesn't (e.g. DLC, EAI).

## Companions
`naming-config` (the launcher's *name* + config triple) · `layout-workspace` (where
`launcher/` and `platforms/` live) · `env-cluster` (the machine env the profile assumes) ·
`conventions` (the family index).
