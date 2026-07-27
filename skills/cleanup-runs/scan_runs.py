#!/usr/bin/env python3
"""scan_runs.py - classify runs in the layout-output tree and propose safe reclaim.

What: walk a root under OUTPUT_DIR_HOME, classify each run and each checkpoint into
      PROTECTED (resume point / best / symlink target / recent / config) or CANDIDATE
      (intermediate checkpoint, smoke run, tmp junk), size each candidate, and print a
      plan sorted by reclaim. Read-only by default: it writes nothing unless --stage is
      given, and --stage MOVES candidates into a trash dir (a reversible rename), it never
      calls rm. Enforces the cleanup-runs hard rails.
When: the user has asked to reclaim space and you need a safe, reviewable plan first.
Usage:
      # dry-run plan for one project's runs, keep newest+best, thin older intermediates
      python scan_runs.py --root $OUTPUT_DIR_HOME/proj --keep-last 1
      # also propose whole smoke/toy/debug runs, only those idle for 2+ days
      python scan_runs.py --root $OUTPUT_DIR_HOME/proj --include-smoke --older-than 2
      # after reviewing the plan, stage candidates reversibly (rename, not rm)
      python scan_runs.py --root $OUTPUT_DIR_HOME/proj --keep-last 1 --stage $OUTPUT_DIR_HOME/.trash-20260726

The user hard-deletes the trash dir themselves once the kept runs are verified to load.
"""
import argparse, os, re, sys, time

CKPT_RE = re.compile(r"(?:step|checkpoint|ckpt|epoch)[_-]?(\d+)", re.I)
PROTECTED_LINKS = ("best", "last", "final")   # checkpoint symlinks that pin a target
SMOKE_TAGS = ("smoke", "toy", "mini", "debug")
SIGNATURE = ("config.yaml", "metrics.jsonl")
SMOKE_MAX_STEP = 200          # a run whose top checkpoint is below this reads as smoke/debug


def die(msg):
    sys.exit(f"scan_runs: {msg}")


def dir_size(path):
    total = 0
    for dp, _d, files in os.walk(path):
        for f in files:
            fp = os.path.join(dp, f)
            try:
                if not os.path.islink(fp):
                    total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def human(n):
    for unit in ("B", "K", "M", "G", "T"):
        if n < 1024 or unit == "T":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024


def is_run(dirpath, files):
    return any(s in files for s in SIGNATURE)


def find_checkpoints(run):
    """Return (ckpt_dirs, symlink_targets). ckpt_dirs is [(step:int, path)] for real dirs."""
    ck_root = None
    for name in ("checkpoints", "ckpt", "checkpoint"):
        p = os.path.join(run, name)
        if os.path.isdir(p):
            ck_root = p
            break
    search = ck_root or run
    ckpts, targets = [], set()
    for entry in os.listdir(search):
        full = os.path.join(search, entry)
        if os.path.islink(full):
            if entry.lower() in PROTECTED_LINKS:
                targets.add(os.path.realpath(full))
            continue
        if os.path.isdir(full):
            m = CKPT_RE.search(entry)
            if m:
                ckpts.append((int(m.group(1)), os.path.realpath(full)))
            elif entry.lower() in PROTECTED_LINKS:
                targets.add(os.path.realpath(full))
    return sorted(ckpts), targets


def looks_smoke(run, ckpts):
    name = os.path.basename(run.rstrip(os.sep)).lower()
    if any(t in name for t in SMOKE_TAGS):
        return True
    top = ckpts[-1][0] if ckpts else 0
    return top and top < SMOKE_MAX_STEP


def classify(run, keep_last, recency_s, include_smoke, now):
    """Return (candidates, protected_notes). candidates = [(path, cls, reason)]."""
    files = set(os.listdir(run))
    ckpts, link_targets = find_checkpoints(run)
    finished = "DONE" in files
    cands, notes = [], []

    # recency guard: a recently touched run may be live, protect it wholesale
    try:
        idle = now - max((os.path.getmtime(p) for _s, p in ckpts), default=os.path.getmtime(run))
    except OSError:
        idle = 0
    if idle < recency_s:
        notes.append(f"PROTECT whole run (active {human_time(idle)} ago)")
        return [], notes

    # protected checkpoints: newest, best/last targets
    protected = set(link_targets)
    if ckpts:
        protected.add(ckpts[-1][1])   # newest = resume point
        notes.append(f"PROTECT newest ckpt step {ckpts[-1][0]}")
    for t in link_targets:
        notes.append(f"PROTECT symlink target {os.path.basename(t)}")

    # smoke/toy/debug: propose the whole run only when opted in
    if include_smoke and looks_smoke(run, ckpts):
        cands.append((run, "smoke-run", "smoke/toy/debug: tag or tiny step count"))
        return cands, notes + ["(whole run proposed as smoke; overrides ckpt-level thinning)"]

    # thin intermediate checkpoints: keep the last `keep_last` plus protected, drop older
    keep_recent = {p for _s, p in ckpts[-keep_last:]} if keep_last > 0 else set()
    for step, p in ckpts:
        if p in protected or p in keep_recent:
            continue
        state = "finished run" if finished else "unfinished run, older than newest"
        cands.append((p, "intermediate-ckpt", f"superseded step {step} ({state})"))

    # tmp / junk anywhere in the run
    for dp, _d, fs in os.walk(run):
        for f in fs:
            fp = os.path.join(dp, f)
            if os.path.islink(fp):
                continue
            try:
                z = os.path.getsize(fp) == 0
            except OSError:
                z = False
            # weight-like: a zero-byte checkpoint file is a crash artifact. A zero-byte
            # marker/log (DONE, stdout) is meaningful or harmless, so do not flag it.
            weightlike = f.endswith((".bin", ".pt", ".pth", ".ckpt", ".safetensors"))
            if f.endswith((".tmp", ".partial", ".lock")):
                cands.append((fp, "tmp-junk", "*.tmp/*.partial/*.lock"))
            elif z and weightlike:
                cands.append((fp, "tmp-junk", "zero-byte weights file (crash artifact)"))
    return cands, notes


def human_time(s):
    if s < 3600:
        return f"{s/60:.0f}m"
    if s < 86400:
        return f"{s/3600:.1f}h"
    return f"{s/86400:.1f}d"


def stage_move(path, root, trash):
    real = os.path.realpath(path)
    if not real.startswith(os.path.realpath(root) + os.sep):
        die(f"refusing to stage a path outside root: {real}")
    rel = os.path.relpath(real, os.path.realpath(root))
    dest = os.path.join(trash, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.stat(real).st_dev != os.stat(os.path.dirname(dest) or ".").st_dev:
        die(f"trash is on another filesystem; a rename would become a slow copy: {dest}")
    os.rename(real, dest)
    return dest


def main():
    ap = argparse.ArgumentParser(description="classify runs and propose safe reclaim (read-only unless --stage)")
    ap.add_argument("--root", required=True, help="dir under OUTPUT_DIR_HOME to scan")
    ap.add_argument("--keep-last", type=int, default=1, help="intermediate checkpoints to keep per run (newest); best is always kept")
    ap.add_argument("--older-than", type=float, default=1.0, help="only consider runs idle for at least this many days")
    ap.add_argument("--include-smoke", action="store_true", help="also propose whole smoke/toy/debug runs")
    ap.add_argument("--stage", metavar="TRASH", help="MOVE candidates into TRASH (reversible rename). Omit for a dry run.")
    a = ap.parse_args()

    root = os.path.realpath(a.root)
    out_home = os.path.realpath(os.environ.get("OUTPUT_DIR_HOME", ""))
    # hard rails: real path, non-empty, under OUTPUT_DIR_HOME, not the root itself
    if root in ("/", "") or root.count(os.sep) < 2:
        die(f"refusing to scan a top-level path: {root}")
    if out_home and not (root == out_home or root.startswith(out_home + os.sep)):
        die(f"root is not under OUTPUT_DIR_HOME ({out_home}): {root}")
    if out_home and root == out_home and not a.stage:
        pass  # scanning the whole output home read-only is fine
    if not os.path.isdir(root):
        die(f"not a directory: {root}")
    if a.stage:
        trash = os.path.realpath(a.stage)
        if trash.startswith(root + os.sep) or root.startswith(trash + os.sep):
            die("trash dir must not sit inside (or contain) the scan root")
        os.makedirs(trash, exist_ok=True)

    now = time.time()
    recency_s = a.older_than * 86400
    all_cands, total = [], 0
    for dp, dirs, files in os.walk(root):
        if is_run(dp, files):
            cands, notes = classify(dp, a.keep_last, recency_s, a.include_smoke, now)
            dirs[:] = []  # do not descend into a run's checkpoints as if they were runs
            if cands or notes:
                print(f"\n# {os.path.relpath(dp, root)}")
                for n in notes:
                    print(f"    {n}")
                for path, cls, reason in cands:
                    sz = dir_size(path) if os.path.isdir(path) else (os.path.getsize(path) if os.path.exists(path) else 0)
                    total += sz
                    all_cands.append((path, cls, sz))
                    print(f"    CANDIDATE [{cls:16}] {human(sz):>7}  {os.path.relpath(path, root)}  <- {reason}")

    print(f"\n# total reclaimable: {human(total)} across {len(all_cands)} items")
    if not a.stage:
        print("# dry run. Review, then re-run with --stage <trash-dir> to move these reversibly.")
        return
    print(f"# staging into {trash} (reversible rename) ...")
    for path, _cls, _sz in sorted(all_cands, key=lambda c: -len(c[0])):  # deepest first
        if os.path.exists(path):
            print(f"    moved {os.path.relpath(path, root)} -> {stage_move(path, root, trash)}")
    print(f"# done. Verify the kept runs load, then remove {trash} yourself.")


if __name__ == "__main__":
    main()
