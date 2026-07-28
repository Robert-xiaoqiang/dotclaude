# Skill: layout-runtime

## Purpose
Reason about a cluster job's RUNTIME as a **layered, partially-independent stack** — GPU driver ×
container image × python venv × shared storage — so you pick a *mutually consistent* set and never
burn hours on an "impossible" that is really a one-layer mismatch. The submitting shell (an Alibaba
PAI **DSW** instance, or your Claude session) is itself just one such stack, on a **different** driver/
image and an **isolated network** — never assume it shares a job's runtime.

## When to Use
- Submitting a serving/training job on **DLC** (or any pod scheduler): choosing driver / image / venv.
- A job fails with `libcudart.so.N not found`, `undefined symbol: …`, `driver too old`, `cuda_avail
  False`, or an import error → it is a layer mismatch; diagnose the stack, don't conclude "impossible."
- Building a python venv (`$CPFS_HOME/uv_home/venvs/`) for a job — where to build, under which driver/image.
- Confused why the DSW can't run a venv, or can't `curl` a job's HTTP endpoint.

## The four layers (bottom → top), each set at a different time
They must be **mutually consistent for code to RUN** (not merely import):

1. **GPU driver** — on the **node** (kernel-mode). Sets the *max CUDA the node can execute*. On DLC it is
   **selectable per job at submit time: `dlc submit … --driver <ver>`** (the web-UI driver dropdown; the
   CLI flag mirrors it). Default a100/a800 = `470.199.02` = CUDA 11.4 (nvidia-smi shows 12.8 only via the
   cu128 image's forward-compat). Pick `580.95.05-open` for **CUDA 13**. Selectable: 470.199.02, 535.54.03,
   550.54.15, 570.133.20, 570.133.20-open, 580.95.05-open. **As load-bearing as the image** — the #1 cause
   of an "impossible" that is actually a one-flag fix.
2. **Container image** — `--worker_image`. Provides the CUDA **runtime** libs (`libcudart.so.N`), the base
   python, glibc/system libs, sometimes baked frameworks. Chosen at submit time. Its CUDA runtime must be
   ≤ the node driver's CUDA (else `libcudart.so.13: cannot open` / missing symbols).
3. **Python venv** — installed packages (torch/vLLM with their *bundled* CUDA runtime **and compiled
   kernels**). Lives in **shared storage** (`uv_home/venvs/`), persistent, side-by-side per (platform,
   python, CUDA). Its kernels need driver symbols — e.g. vLLM 0.26 → `cuTensorMapEncodeTiled` (a CUDA-12+
   Hopper-TMA symbol), so it needs a CUDA-12+ *driver*, not just a cu13 image.
4. **Shared storage** — CPFS/NAS/OSS mounted across nodes: venvs, models, data, outputs, logs — persistent,
   read/write from any job that mounts it. Building a venv **writes** here; running it **reads** here.

## The consistency rule (the crux)
```
node-driver CUDA  ≥  image runtime CUDA  ≥  venv (torch/vLLM) CUDA
```
A venv **runs** only when all three hold. **Storing/building** a venv is *free* — any box can download
wheels to CPFS with no GPU. Only **running** needs the full chain. So: build the venv **on a node with the
target driver+image** (never the DSW), first-run *build-if-missing* into shared CPFS, reuse after. If a
venv is broken/half-built, just `rm` it — shared CPFS makes that safe for any job.

## Instance isolation — the DSW / submitting shell is NOT the job
The submitting shell is **its own instance** with its own driver+image (here R470 / cu128 / py3.11) — a
different stack from the jobs it launches. Therefore:
- **Never run a job's venv (cu130/129) in the cu128 DSW shell** — the driver rejects it. Submit to DLC and
  monitor output. Inspecting a venv by *metadata* (dist-info Version) is fine; *importing/running* is not.
- **The DSW cannot HTTP-reach a DLC job's pod** — pods sit on the cluster pod network, isolated from the
  interactive DSW (instant `HTTP 000`). A trainer **job** reaches a serving **job** via pod IPs (published
  to a CPFS endpoints file); the DSW can't. Test a served endpoint from a **peer DLC job**, not the DSW.
- Everything crosses instances **only via shared storage** (CPFS): venvs, models, the endpoints file, logs.
  Route job logs to **CPFS, not node `/tmp`**, or you debug blind (a real trap: vLLM replica logs on `/tmp`
  hid a one-line argparse error for 20 min).

## Symptom → layer (fast triage)
| symptom | culprit layer | fix |
|---|---|---|
| `libcudart.so.13: cannot open` | image lacks cu13 runtime | use a cu130 image |
| `undefined symbol: cuTensorMapEncodeTiled`, `driver too old (11040)`, `cuda_avail False` | driver too old | `--driver 580.95.05-open` |
| `import vllm` OK on node A, fails on node B | different driver/image per node | pin both |
| venv builds fine but won't run | driver/image below venv CUDA | bump driver/image |
| endpoint unreachable *from DSW* | instance/pod-network isolation (expected) | test from a peer DLC job |

## Rules
- Treat `--driver` as a **first-class knob** beside `--worker_image`; define both explicitly per platform in
  the launcher/serve script (e.g. `GPU_SERVE_DRIVER=580.95.05-open`, `GPU_SERVE_IMAGE=…cu130…`).
- Build venvs **on-target, build-if-missing, name by platform** into shared CPFS; never `--clear`/reinstall
  a present venv — if broken, `rm` it.
- Keep the pod entrance command short: inject only `CPFS_HOME` (+ the few job-specific vars) and let the
  entrance `source $CPFS_HOME/env.sh` for the standard paths — don't re-export what env.sh already sets.
- Route job logs to CPFS; confirm serving from a peer DLC job, never the DSW.

## Companions
`platform-run` (neutral spec → native submit) · `env-cluster` (the machine env the profile assumes) ·
`layout-output` (output tree) · `naming-config` · `conventions` (the family index). Project memory: `dlc-driver-flag-serving`.
