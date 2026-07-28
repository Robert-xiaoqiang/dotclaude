# Skill: platform-runtime

## Purpose
Reason about a cluster job's runtime as a **layered, partially-independent stack**, GPU driver,
container image, python venv, and shared storage, so you pick a *mutually consistent* set and
never lose hours to an "impossible" that is really a one-layer mismatch. The model is
scheduler-neutral and holds on any pod or batch scheduler (Alibaba PAI **DLC**, **Slurm**,
**Kubernetes**, a cloud batch service). The shell you submit from (a PAI **DSW** instance, a
Slurm **login node**, your laptop with `kubectl`, or your Claude session) is itself just one
such stack, on a **different** driver and image and an **isolated network**. Never assume it
shares a job's runtime.

## When to Use
- Submitting a training or serving job on any scheduler and choosing its driver, image, or venv.
- A job fails with `libcudart.so.N not found`, `undefined symbol: ...`, `driver too old`,
  `cuda_avail False`, or an import error. That is a layer mismatch. Diagnose the stack, do not
  conclude "impossible".
- Building a python venv for a job and deciding where and under which driver and image.
- Confused why the submitting shell cannot run a job's venv, or cannot reach a job's endpoint.

## The four layers (bottom to top), each set at a different time
They must be **mutually consistent for code to RUN**, not merely import.
1. **GPU driver.** On the node, kernel-mode. Sets the *max CUDA the node can execute*.
   Provisioned per node, though some schedulers let you pick it per job (see the table). The
   most common cause of an "impossible" that is actually a one-knob fix.
2. **Container image (or environment module).** Provides the CUDA *runtime* libs
   (`libcudart.so.N`), the base python, glibc and system libs, sometimes baked frameworks. Its
   CUDA runtime must be **≤ the node driver's CUDA**, else `libcudart.so.N: cannot open` or
   missing symbols. Where a scheduler runs bare metal with no container, `module load cuda/...`
   fills this same layer.
3. **Python venv.** Installed packages (torch, vLLM) with their *bundled* CUDA runtime **and
   compiled kernels**. Lives on shared storage, persistent, side by side per (platform, python,
   CUDA). Its kernels call driver symbols, so the *driver*, not just the image, must be new enough.
4. **Shared storage.** A cross-node filesystem mounted on every node: venvs, models, data,
   outputs, logs. Building a venv **writes** here, running it **reads** here.

## How each layer is set, per platform
The same four layers exist everywhere. Only the knob and the moment it is set change. Read across
a row to translate a runtime between schedulers.

| layer | DLC (PAI) | Slurm | Kubernetes |
|---|---|---|---|
| **GPU driver** | pick per job at submit: `dlc submit --driver <ver>` (UI dropdown mirror) | fixed on the node by the admin, select a matching node via `--partition` / `--constraint` / `--gres=gpu:<type>` | fixed on the node pool (GPU Operator), select via `nodeSelector` / taints |
| **image / runtime** | `--worker_image` | container via Pyxis/enroot (`srun --container-image=...`) or Singularity (`singularity exec --nv a.sif`), else `module load cuda/...` | pod `spec.containers[].image` |
| **python venv** | venv dir on CPFS | venv dir on Lustre / GPFS / NFS | venv dir on a PVC (RWX) |
| **shared storage** | CPFS / NAS / OSS | Lustre / GPFS / BeeGFS / NFS | PVC / CSI volume |
| **submit from** | DSW instance | login node | laptop / `kubectl` |

The one difference worth internalizing: on DLC you **pick a driver** per job, on Slurm and K8s
the driver is **fixed on the node** and you pick a *node* that already carries the driver you
need. Same consistency requirement, opposite direction of control.

## The consistency rule (the crux)
```
node-driver CUDA  ≥  image/module runtime CUDA  ≥  venv (torch/vLLM) CUDA
```
A venv **runs** only when all three hold. Storing and building a venv is *free*. Any box can
download wheels to shared storage with no GPU. Only **running** needs the full chain. So build
the venv **on a node with the target driver and image** (never on the submitting shell),
build-if-missing into shared storage, and reuse after. If a venv is broken or half-built, `rm`
it. Shared storage makes that safe for any job.

## Instance isolation, the submitting shell is NOT the job
The shell you submit from is its own instance, with its own driver, image, and network, a
different stack from the jobs it launches. So:
- **Do not run a job's venv in the submitting shell.** If the shell's driver is older than the
  venv's CUDA, the driver rejects it. Reading a venv's *metadata* (dist-info Version) is fine,
  importing or running is not. On our DSW the shell is R470 / cu128 / py3.11 and cannot run a
  cu130 or cu129 venv.
- **The submitting shell usually cannot reach a job's service port.** Pods and compute nodes sit
  on the cluster network, isolated from the login instance (an instant `HTTP 000` on DLC, and
  commonly the same from a Slurm login node). A trainer job reaches a serving job by its pod or
  node address, published to a shared-storage endpoints file. Test a served endpoint from a
  **peer job**, not the submitting shell.
- **Everything crosses instances only through shared storage:** venvs, models, the endpoints
  file, logs. Route job logs to shared storage, not node-local `/tmp` or a purged `/scratch`, or
  you debug blind (a real trap: vLLM replica logs on `/tmp` hid a one-line argparse error for
  20 minutes).

## Symptom to layer (fast triage)
| symptom | culprit layer | fix |
|---|---|---|
| `libcudart.so.N: cannot open` | image lacks that CUDA runtime | use an image/module with CUDA ≥ N |
| `undefined symbol: cuTensorMapEncodeTiled`, `driver too old`, `cuda_avail False` | driver too old for the venv's kernels | run on a newer driver: DLC `--driver`, Slurm a newer-driver partition/constraint, K8s a `nodeSelector` |
| `import` OK on node A, fails on node B | different driver/image per node | pin both, or select the node explicitly |
| venv builds fine but will not run | driver or image below the venv's CUDA | bump the driver or the image |
| endpoint unreachable *from the submitting shell* | instance / network isolation (expected) | test from a peer job |

## Worked example (DLC, and its Slurm equivalent)
Default a100/a800 driver is `470.199.02` = CUDA 11.4 (nvidia-smi may report 12.8 only through a
cu128 image's forward-compat). For CUDA 13 pick `580.95.05-open`. Selectable drivers: 470.199.02,
535.54.03, 550.54.15, 570.133.20, 570.133.20-open, 580.95.05-open. vLLM 0.26 calls
`cuTensorMapEncodeTiled`, a CUDA-12+ Hopper-TMA symbol, so it needs a CUDA-12+ *driver*, not
merely a cu13 image. On Slurm the same fix is not a flag but a node selection: submit to a
partition or `--constraint` whose nodes already run a CUDA-12+ driver. The reasoning is identical,
only the control surface differs.

## Rules
- Treat the **driver as a first-class knob beside the image**. On DLC set both explicitly per
  platform in the launcher or serve script (e.g. `GPU_SERVE_DRIVER=580.95.05-open`,
  `GPU_SERVE_IMAGE=...cu130...`). On Slurm and K8s, pin the node selection that guarantees the driver.
- Build venvs **on-target, build-if-missing, named by platform**, into shared storage. Never
  `--clear` or reinstall a present venv. If broken, `rm` it.
- Keep the pod or job-step entrance command short. Inject only `CPFS_HOME` and the few
  job-specific vars, and let the entrance `source $CPFS_HOME/env.sh` for the standard paths. Do
  not re-export what env.sh already sets.
- Route job logs to shared storage. Confirm a served endpoint from a peer job, never the
  submitting shell.

## Companions
`platform-run` (neutral spec → native submit) · `platform-env` (the machine env the profile assumes) ·
`layout-output` (output tree) · `naming-config` · `conventions` (the family index). Project memory: `dlc-driver-flag-serving`.
