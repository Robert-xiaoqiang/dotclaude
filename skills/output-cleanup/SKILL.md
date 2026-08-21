---
name: output-cleanup
description: "Reclaim space in the layout-output tree without destroying what a run needs to resume or what stands as a result. Discovers, classifies and proposes; never deletes on its own."
when_to_use: "Use when runs are called junk and should be cleared, or when space is tight and old smoke, debug or superseded checkpoints may be reclaimable."
---
# Skill: output-cleanup

## Purpose
Reclaim space in the `layout-output` tree by removing what a run no longer needs, without
ever destroying what a run needs to **resume** or what stands as a **result**. Deleting a
good checkpoint costs a long retrain, so this skill is conservative by construction. It
discovers, classifies, and *proposes*, it never deletes on its own read of intent, and it
prefers a reversible move over an `rm`. The user reaches for it knowingly ("I made junk
runs, clear them"), and that instruction is the scope, not a blank check.

## When to Use
- The user says a run or a set of runs is junk and asks to clear it, in clear or fuzzy terms.
- Space is tight and old smoke or debug runs, superseded intermediate checkpoints, or per
  instance eval dumps have piled up.
- Thinning a finished run's intermediate checkpoints down to the ones worth keeping.

Do not run it speculatively. Absent an instruction to reclaim, leave the tree alone.

## The safety model (read before touching anything)
Classify every artifact with `layout-output` first, then act only on the reclaimable class.

**Never delete without an explicit, per-item instruction:**
- The **newest** checkpoint of any run that is not finished. It is the resume point.
- The **`best`** checkpoint and each `eval/<bench>/summary.json`. They are the result.
- Any checkpoint that a `best` / `last` / `final` symlink points at. Resolve symlinks
  before considering a target, or you delete the file the link depends on.
- `config.yaml`. It is tiny and it identifies the run.
- The resume state of an eval still in progress (a partial `predictions.jsonl`).
- Anything modified inside the recency window (default 24h). A recent run may be live.

**Reclaimable, and only with confirmation:**
- Whole **smoke / toy / debug** runs, by name tag (`naming-config`), a tiny step count, or
  no checkpoints. Confirm even so, a "debug" name is a hint, not proof.
- **Intermediate checkpoints** strictly older than the kept set. Keep the newest, keep
  `best`, and keep every K-th or the last K if the user wants a ladder for restarts. Thin
  the rest. Never the newest.
- **Partial / unresumable runs** that never wrote a checkpoint. A crashed or killed run
  with only `wandb/`, `events.out.tfevents.*`, and `logs/` has nothing to resume from, so the
  whole dir is scratch. Confirm it is not a run still working toward its first save.
- **Junk**, `*.tmp` / `*.partial` files, zero-byte weight files, and half-written checkpoint
  dirs (missing their weights or marker file after a crash).
- **Bulky derived data** the user confirms is done with, `wandb/`, `events.out.tfevents.*`,
  and `logs/` once `metrics.jsonl` holds the curves, and `per_instance/` of a *completed*
  eval whose `summary.json` exists. Never drop the last record of the curves, so keep
  tfevents when there is no `metrics.jsonl`.

## Signals for scoping
- **The user's instruction** is the strongest signal. "Clear last night's debug runs" scopes
  by kind and by time. Treat it as the boundary, then still verify each item.
- **mtime** finds recent vs stale. "Recent runs" and "last night" map to an mtime window on
  the newest checkpoint.
- **Name tags** from `naming-config` (`_smoke`, `_toy`, `debug`, the launcher triple).
- **Step numbers** on checkpoints, to thin while keeping the newest and `best`.
- **A terminal marker** (`DONE`) or a `best` at the target step tells finished from
  resumable, so a checkpoint of a finished run is safe to thin and one of an unfinished run
  is not.

## The procedure
1. **Scope.** Combine the user's instruction (a path plus fuzzy intent) with an mtime window.
   Confirm the resolved run set before classifying.
2. **Scan, read-only.** Walk the scope, classify each run and each checkpoint into protected
   or candidate, and size each candidate. The bundled `scan_runs.py` does this and writes
   nothing.
3. **Show the plan.** A table of candidate path, class, size, and the reason it is safe,
   sorted by reclaim. For each run, also list what is **preserved for resume**, so the safety
   net is visible, not implied.
4. **Confirm.** Get an explicit yes on the concrete list, not on the idea.
5. **Prefer a reversible move.** Stage candidates into a `.trash-<date>` dir on the same
   filesystem, which is an instant rename, not a copy. Verify the runs still load, then the
   user hard-deletes the trash later. Reach for `rm` only when the user declines staging.
6. **Report** what was staged or removed, the space reclaimed, and where the trash sits.

## Driving the scan (conservative by default, on purpose)
The bundled `scan_runs.py` errs quiet because a wrong delete costs a retrain, so out of the
box it reports little. That is expected, not a failure. When it stays silent it prints why,
a count of runs protected as recently active and the `--include-*` classes it did not use, so
the fix is to re-run with the flags that match a scope you vouch for. The controls map to the
exact cases you meet.
- **Point `--root` at what you mean.** It takes the exact run dir or any parent. Scoping by
  path is how you vouch for a set, so name the `_bak` you just made or the smoke parent, not
  the whole output home.
- **Recent but safe** (a `_bak` or smoke run made this session). The recency guard protects
  anything touched within `--older-than` days (default 1). Pass `--older-than 0` to consider
  them, since you already know they are safe.
- **Smoke / toy / debug runs.** `--include-smoke` proposes the whole run.
- **Partial, unresumable runs** with no checkpoint (crashed before the first save). These are
  the wandb and tensorboard scratch you want gone. `--include-partial` proposes the whole dir.
- **wandb / tensorboard / logs on a run you keep.** `--include-derived` proposes them, and
  only when `metrics.jsonl` still holds the curves so nothing irreplaceable goes.
- **A resumable run you want to abandon anyway** (it has a `last` checkpoint, but you have
  decided not to continue it). The script will not auto-propose deleting a run that has a
  resume point, by design. That is a judgment call, so name the exact run and say to clear it,
  and it gets staged whole. The filesystem cannot know you gave up on a run, only you can.

## Hard rails (do not cross)
- Two-phase always. Propose, confirm, then act. Never delete on inferred intent alone.
- Stay inside `$OUTPUT_DIR_HOME`. Refuse to operate at or above its root, and never touch
  `projects`, `datasets`, or `downloads`.
- Never build a destructive path from an unchecked variable. An empty variable in
  `rm -rf "$X/"` erases the parent. Guard for empty, resolve to a real path, confirm it sits
  under the root.
- Resolve symlinks and check for the newest and `best` targets before staging any checkpoint.
- Refuse an ambiguous glob. Expand it, show the matches, and confirm.
- Prefer move-to-trash over `rm`. When you must `rm`, `rm` the explicit staged paths, never a
  wildcard against a live run dir.
- When unsure whether an item is resume state, treat it as resume state and keep it.

## Companions
`layout-output` (the schema and the resume-vs-derived classification this enforces) ·
`naming-config` (the tags that flag smoke / debug runs) · `output-analysis` (read the metrics
before thinning, so a curve is not lost with its tfevents) · `conventions` (the index).
