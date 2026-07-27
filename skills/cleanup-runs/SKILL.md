# Skill: cleanup-runs

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
- **Junk**, `*.tmp` / `*.partial` files, zero-byte files, and half-written checkpoint dirs
  (missing their weights or marker file after a crash).
- **Bulky derived data** the user confirms is done with, `logs/`, `events.out.tfevents.*`
  once `metrics.jsonl` holds the curves, and `per_instance/` of a *completed* eval whose
  `summary.json` exists.

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
`naming-config` (the tags that flag smoke / debug runs) · `analysis-runs` (read the metrics
before thinning, so a curve is not lost with its tfevents) · `conventions` (the index).
