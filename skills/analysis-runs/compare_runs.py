#!/usr/bin/env python3
"""compare_runs.py - latitude / longitude comparison of runs in the layout-output tree.

What: discover runs under a root (or take explicit run dirs), read each run's
      metrics.jsonl, and emit (1) a comparison table at a chosen step (latitude) as
      markdown + booktabs LaTeX, and (2) a line figure of metric-vs-step (longitude)
      and a bar figure at the chosen step. Figures use the embed style from the
      analysis-runs skill: no title, no caption, terse labels, vector output, one
      colorblind-safe color per run reused across figures.
When: comparing training/eval runs for a paper or report. Read-only on the run tree.
Usage:
      # discover every run under a root logging dir, plot the loss curve + final bar
      python compare_runs.py --root $OUTPUT_DIR_HOME/proj/sft --metric loss --at last --out fig/
      # explicit runs, compare eval accuracy at step 2000
      python compare_runs.py --runs runA runB --metric eval/acc --at 2000 --out fig/

Assumptions (adjust the two globs below per project):
  - each run dir holds metrics.jsonl, a list of JSON records, each with an integer
    "step" and one key per logged scalar (e.g. {"step": 500, "loss": 2.1, "eval/acc": 0.3}).
  - a run is any dir containing config.yaml OR metrics.jsonl (the layout-output signature).
This script depends only on matplotlib + stdlib. tfevents parsing is intentionally omitted;
keep a small metrics.jsonl per the layout-output skill so curves survive without it.
"""
import argparse, json, os, sys

METRICS_FILE = "metrics.jsonl"       # adjust if the project logs elsewhere
SIGNATURE = ("config.yaml", METRICS_FILE)

# Okabe-Ito colorblind-safe palette. One color per run, assigned by sorted run order.
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]


def apply_style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.figsize": (3.3, 2.2),      # ~single column at final width
        "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": False,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.01,
        "pdf.fonttype": 42, "ps.fonttype": 42,   # editable text in the PDF
    })


def discover_runs(root):
    runs = []
    for dirpath, _dirs, files in os.walk(root):
        if any(s in files for s in SIGNATURE):
            runs.append(dirpath)
    return sorted(runs, key=lambda p: os.path.getmtime(p))


def load_metrics(run_dir):
    path = os.path.join(run_dir, METRICS_FILE)
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return sorted(rows, key=lambda r: r.get("step", 0))


def run_label(run_dir, root=None):
    """Short, meaningful label. Prefer the path tail relative to root; runs that share a
    prefix then differ only by the slot that changed (naming-config symmetry)."""
    if root:
        rel = os.path.relpath(run_dir, root).strip(os.sep)
        return rel if rel != "." else os.path.basename(run_dir.rstrip(os.sep))
    return os.path.basename(run_dir.rstrip(os.sep))


def series(rows, metric):
    xs, ys = [], []
    for r in rows:
        if metric in r and "step" in r:
            xs.append(r["step"]); ys.append(r[metric])
    return xs, ys


def value_at(rows, metric, at):
    """Value at the requested step. `at` is 'last', 'best', or an int (nearest not-exceeding).
    'best' picks max for accuracy-like metrics and min for loss-like ones. Returns (step, val)
    or (None, None) when the run never logged this metric."""
    xs, ys = series(rows, metric)
    if not xs:
        return None, None
    if at == "last":
        return xs[-1], ys[-1]
    if at == "best":
        lower = metric.split("/")[-1].lower()
        pick = min if any(k in lower for k in ("loss", "ppl", "perplexity", "nll", "error")) else max
        i = ys.index(pick(ys))
        return xs[i], ys[i]
    target = int(at)
    cand = [(s, v) for s, v in zip(xs, ys) if s <= target]
    return cand[-1] if cand else (None, None)


def emit_table(labels, rows_by_run, metric, at, out):
    header = f"run | step | {metric}"
    md = [f"| {header.replace(' | ', ' | ')} |", "|" + "---|" * 3]
    tex_rows = []
    for lab in labels:
        step, val = value_at(rows_by_run[lab], metric, at)
        s = "-" if step is None else str(step)
        v = "-" if val is None else f"{val:.4g}"
        md.append(f"| {lab} | {s} | {v} |")
        tex_rows.append(f"    {lab.replace('_', chr(92)+'_')} & {s} & {v} \\\\")
    md_txt = "\n".join(md)
    tex = ("\\begin{tabular}{lrr}\n  \\toprule\n"
           f"  run & step & {metric.replace('_', chr(92)+'_')} \\\\\n  \\midrule\n"
           + "\n".join(tex_rows) + "\n  \\bottomrule\n\\end{tabular}\n")
    print(md_txt + "\n")
    if out:
        with open(os.path.join(out, "table.md"), "w") as f:
            f.write(md_txt + "\n")
        with open(os.path.join(out, "table.tex"), "w") as f:
            f.write(tex)
    return md_txt


def plot_longitude(labels, rows_by_run, colors, metric, out):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for lab in labels:
        xs, ys = series(rows_by_run[lab], metric)
        if xs:
            ax.plot(xs, ys, color=colors[lab], label=lab, linewidth=1.4)
    ax.set_xlabel("step"); ax.set_ylabel(metric)
    if len(labels) > 1:
        ax.legend()
    p = os.path.join(out, "dynamics.pdf")
    fig.savefig(p); plt.close(fig)
    return p


def plot_latitude(labels, rows_by_run, colors, metric, at, out):
    import matplotlib.pyplot as plt
    vals, keep = [], []
    for lab in labels:
        _s, v = value_at(rows_by_run[lab], metric, at)
        if v is not None:
            vals.append(v); keep.append(lab)
    fig, ax = plt.subplots()
    ax.bar(range(len(keep)), vals, color=[colors[l] for l in keep], width=0.6)
    ax.set_xticks(range(len(keep))); ax.set_xticklabels(keep, rotation=30, ha="right")
    ax.set_ylabel(metric)
    p = os.path.join(out, "compare.pdf")
    fig.savefig(p); plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser(description="latitude/longitude comparison of runs")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="parent logging dir; discover runs beneath it")
    g.add_argument("--runs", nargs="+", help="explicit run dirs")
    ap.add_argument("--metric", required=True, help="metric key in metrics.jsonl, e.g. loss or eval/acc")
    ap.add_argument("--at", default="last", help="step for the latitude cut: last | best | <int>")
    ap.add_argument("--out", default=".", help="output dir for table + figures")
    a = ap.parse_args()

    root = a.root
    runs = discover_runs(a.root) if a.root else [r.rstrip(os.sep) for r in a.runs]
    if not runs:
        sys.exit("no runs found (looked for config.yaml / metrics.jsonl)")
    os.makedirs(a.out, exist_ok=True)

    labels = [run_label(r, root) for r in runs]
    rows_by_run = {lab: load_metrics(r) for lab, r in zip(labels, runs)}
    colors = {lab: PALETTE[i % len(PALETTE)] for i, lab in enumerate(labels)}

    # the table is pure stdlib and always works; figures need matplotlib.
    emit_table(labels, rows_by_run, a.metric, a.at, a.out)
    print(f"wrote {os.path.join(a.out, 'table.md')} + table.tex")
    try:
        apply_style()
    except ModuleNotFoundError:
        print("matplotlib not found; table emitted, figures skipped. "
              "Install it in the project env (e.g. `uv pip install matplotlib`) for figures.")
        return
    fl = plot_longitude(labels, rows_by_run, colors, a.metric, a.out)
    fb = plot_latitude(labels, rows_by_run, colors, a.metric, a.at, a.out)
    print(f"wrote {fl}\nwrote {fb}")


if __name__ == "__main__":
    main()
