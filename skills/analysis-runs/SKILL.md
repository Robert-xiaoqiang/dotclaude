# Skill: analysis-runs

## Purpose
Given a directory of runs that share the `layout-output` schema, compare them and produce
the tables and figures that go into a paper or report. Handle the two axes that matter for
research, **latitude** (compare different runs at the same step) and **longitude** (compare
dynamics across steps). Emit results in an embed-ready style, figures with no title, no
baked caption, and terse labels, because they land inside another document and do not need
to stand alone.

## When to Use
- The user points at a run dir, a pair of runs, a list, or a root logging dir and asks to
  compare, tabulate, or plot them.
- Building the results table or the loss / metric curves for a paper, report, or slide.
- The user is fuzzy ("plot last night's runs", "compare the two lora arms") and expects you
  to find the runs by name and editing time.

## Input shapes (all reduce to a run set)
- **Single run.** Longitude only, its own dynamics over steps.
- **Pair.** The common ablation, two arms differing in one slot (`naming-config`).
- **List.** Several explicit run dirs.
- **Root logging dir.** A parent under `$OUTPUT_DIR_HOME` holding many runs. Discover them
  with the `layout-output` signature, then filter by the user's scope and by mtime.

Resolve fuzzy asks by discovery. Walk for the schema signature, read each `config.yaml` to
label runs by their pipeline / model / dataset, and sort by mtime so "recent" and "last
night" map to concrete dirs. Confirm the resolved set before plotting when the ask was vague.

## The two axes
- **Latitude (cross-run, fixed step).** Hold the step, vary the run. Answers "at step 2000,
  which arm is ahead", or "final eval score per run". Cross-sectional. Renders as a bar
  chart or a table row per run.
- **Longitude (within/across runs, over steps).** Hold the run(s), vary the step. Answers
  "how does the loss or the eval metric evolve". Time-series. Renders as line curves, one
  per run.

Align on **steps, not wallclock**. Runs log at different cadences and may miss steps. For a
latitude cut, take each run's value at the requested step or the nearest earlier logged step,
and say so when a run has no matching step. Do not silently interpolate a run onto another's
grid. For longitude, plot each run on its own step grid.

## Outputs
- **Tables.** One row per run, columns are the chosen metrics at a chosen step (or `best`).
  Emit markdown for the chat or a report, and a booktabs LaTeX table for a paper. Keep any
  prose around the table within `writing-style`.
- **Line figure (longitude).** Metric vs step, one line per run, consistent color per run
  reused across every figure so a run keeps its identity.
- **Bar figure (latitude).** One bar per run at the chosen step, same per-run colors.
- **Set figure (eval).** A Venn or an UpSet over which instances each run got right, read
  from `eval/<bench>/predictions.jsonl`. Shows where runs agree and disagree, not just the
  aggregate score. Venn stays readable up to three sets, use UpSet beyond that.
- **Individual vs merged.** Default to one figure per metric. Merge into a small multi-panel
  only when the user wants a single float in the paper.

## Figure style (embed, not standalone)
These figures go inside another document, so the document supplies the title and caption,
not the image.
- No `title` and no `suptitle`. No caption text baked into the image.
- Terse axis labels (`step`, `loss`, `acc`), not sentences. Let the paper's caption carry
  the detail.
- Vector output, `pdf` for LaTeX `includegraphics` and `pgf` when you want the paper's fonts.
  Match the document font size, roughly 8 to 10 pt at final width.
- Legend inside the axes, no frame, only when there is more than one line. Prefer labeling
  lines directly when it is cleaner.
- A constrained, colorblind-safe palette (Okabe-Ito). One color per run, fixed across all
  figures. `tight_layout` or a tight bbox so there is no border slack.
- No gridlines unless they aid reading, no chart junk, no 3D, no dual y-axis.

The bundled `compare_runs.py` applies this style and emits the table plus the line and bar
figures. `templates/dynamics.pgf.tex` and `templates/table.tex` are the TikZ / pgfplots and
booktabs equivalents for when the figure or table is authored directly in LaTeX. For a
richer or interactive chart, the `dataviz` skill has the palette and mark rules, but its
default is a standalone dashboard, so strip the title and caption to match this embed style.

## Where the analysis itself lives
The analysis is a durable artifact, so it follows `layout-workspace`. The regeneration
script goes in the repo under `scripts/analysis/` (or `scripts/checks/` if it doubles as a
sanity check), headed with what / when / usage. The written report or the figures go in
`docs/reports/`. A small throwaway helper can live in `$CPFS_HOME/snippets`. Never leave the
only copy in a chat scratchpad, because the point is to rerun the figure when a run updates.

## Rules
1. Read-only on the run tree. Analysis never writes into a run dir.
2. Compare siblings that share a `<pipeline>/<model>/<dataset>` prefix. Comparing unrelated
   triples needs the user to say why.
3. Align on steps and state gaps. No silent interpolation.
4. One color per run, reused across every figure.
5. Embed style. No title, no baked caption, terse labels, vector output.
6. Emit a rerunnable script, not just an inline one-off.

## Companions
`layout-output` (the run schema this reads) · `naming-config` (how runs are labeled and
paired) · `layout-workspace` (where the script and report live) · `writing-style` (prose
around the tables) · `dataviz` (palette and marks for richer charts) · `conventions` (index).
