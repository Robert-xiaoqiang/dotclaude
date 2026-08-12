#!/usr/bin/env python3
"""Migrate a Claude Code project folder + its session history to a new path.

Claude Code keys sessions by the project's ABSOLUTE PATH:
  * discovery: sessions live under  ~/.claude/projects/<SLUG>/<uuid>.jsonl,
    where SLUG = the absolute path with every non-alphanumeric char -> '-'
    (no collapsing, case preserved). e.g.
        Windows : D:\\projects\\Old App   -> D--projects-Old-App
        Unix    : /home/u/old app         -> -home-u-old-app
  * each transcript ALSO embeds the absolute path (a "cwd" field on many lines),
    so resume can fail to list a session unless those are rewritten too.

This script (cross-platform, Python 3, std-lib only):
  1. computes old/new slugs
  2. backs up the session store
  3. renames the project folder            (old -> new)
  4. renames the slug store                 (projects/<old> -> projects/<new>)
  5. rewrites embedded paths in every *.jsonl (BOM-safe, JSON-valid)
  6. prints how to resume

There is a SECOND mode, --old-root/--new-root, for the case this script could not
originally express: the whole persistent home moved, every project moved with it,
and the trees ALREADY EXIST on both sides. Then there is nothing to rename on
disk, only a store to re-key, and the single-project mode aborts on its own
preflight ("target already exists") before it can help. See relocate_root().

Usage:
    # one project renamed or moved
    python migrate_session.py --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>" [--dry-run] [--yes]
    python migrate_session.py --old ... --new ... --claude-dir "<~/.claude>"

    # the whole persistent root moved; re-key every project at once
    python migrate_session.py --old-root /mnt/cpfs/xqwang --new-root /mnt/data/xqwang \
        --claude-dir /mnt/data/xqwang/.claude [--dry-run] [--yes]

It is REVERSIBLE: rename both folders back, or restore the printed backup.
NOTE: you cannot rename the folder of a CURRENTLY-OPEN session (the OS locks the
cwd and the transcript is in use) — exit Claude Code first, then run this from a
shell that is not inside the folder.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


def encode_slug(path: str) -> str:
    """Replicate Claude Code's path -> storage-slug encoding."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def norm(path: str) -> str:
    """Absolute, OS-native-separator form (matches what Claude records as cwd)."""
    return os.path.normpath(os.path.abspath(os.path.expanduser(path)))


def path_pairs(old: str, new: str):
    """(old, new) string pairs to replace inside transcripts, most-specific first.

    Covers the JSON-escaped native form (the functional "cwd"), the forward-slash
    form, and the git-bash drive form (/d/...). Returns escaped-for-file strings.
    """
    pairs = []
    # 1) JSON-escaped native form (what the "cwd" field actually contains on disk)
    pairs.append((json.dumps(old)[1:-1], json.dumps(new)[1:-1]))
    # 2) forward-slash form (e.g. D:/projects/x  or  /home/u/x)
    pairs.append((old.replace("\\", "/"), new.replace("\\", "/")))
    # 3) git-bash drive form (D:\x -> /d/x)
    mo = re.match(r"^([A-Za-z]):[\\/](.*)$", old)
    mn = re.match(r"^([A-Za-z]):[\\/](.*)$", new)
    if mo and mn:
        go = "/" + mo.group(1).lower() + "/" + mo.group(2).replace("\\", "/")
        gn = "/" + mn.group(1).lower() + "/" + mn.group(2).replace("\\", "/")
        pairs.append((go, gn))
    # de-dup while preserving order, drop no-op pairs
    seen, out = set(), []
    for a, b in pairs:
        if a and a != b and a not in seen:
            seen.add(a)
            out.append((a, b))
    return out


def rewrite_text(text: str, pairs) -> tuple[str, int]:
    n = 0
    for a, b in pairs:
        n += text.count(a)
        text = text.replace(a, b)
    return text, n


def die(msg: str, code: int = 1):
    print(f"ABORT: {msg}", file=sys.stderr)
    raise SystemExit(code)


# ===========================================================================
# ROOT RELOCATION — the whole persistent home moved
# ===========================================================================
# Everything below exists because the single-project mode above cannot express
# the case where a persistent root moves. Four differences drive it.
#
# NOTHING IS RENAMED ON DISK. Both project trees already exist (an rsync put
# them there), so the folder move that the single-project mode leads with is not
# merely unnecessary, it is what makes that mode abort: `if Path(new).exists():
# die(...)` fires on every project. Here the only thing that moves is the store.
#
# THE SLUG IS SUBSTITUTED, NOT RE-ENCODED. encode_slug maps every non-alphanumeric
# character to '-', so it is one-way: '-PreReward-case-analysis' could have come
# from a '/' or from a '_' and there is no way to tell. Decoding a slug back to a
# path to re-encode it therefore invents paths that never existed. Since both
# roots encode to a fixed prefix, a literal prefix substitution ON THE SLUG STRING
# is exact where a round-trip is not.
#
# STORES MERGE, THEY DO NOT MOVE ONTO EACH OTHER. Work done from the new root
# before the migration finished has already created new-root slugs, so both
# spellings can hold transcripts. shutil.move of a directory onto an existing
# directory NESTS it one level deep, where --resume will never look, which is why
# the single-project mode refuses the case outright.
#
# THE ANCHOR IS THE FULL OLD ROOT, never its mount point. '/mnt/cpfs' also prefixes
# other people's homes, and those paths appear in transcripts as legitimate
# references to shared checkpoints. Substituting on the mount point corrupts them.

# Files whose CONTENT is rewritten. An allow-list, because the store also holds
# binaries and caches: .jsonl transcripts are the point, but sidecar .js workflow
# scripts, .json task state and .md notes all carry absolute paths that a
# jsonl-only walk leaves behind.
REWRITE_SUFFIXES = {".jsonl", ".json", ".js", ".txt", ".md"}

# Subtrees of the config dir to walk. Deliberately NOT the whole dir:
#   .git/            submodule metadata; rewriting it corrupts object contents
#   shell-snapshots/ regenerated on demand, and every one pins a whole stale PATH,
#                    so they are deleted rather than repaired (see --prune-snapshots)
#   backups/         historical copies; rewriting them destroys their reason to exist
REWRITE_DIRS = ("projects", "jobs", "plugins", "tasks", "todos")
REWRITE_FILES = ("history.jsonl", "settings.json", "settings.local.json")


def _iter_rewritable(claude_dir: Path):
    for d in REWRITE_DIRS:
        base = claude_dir / d
        if not base.is_dir():
            continue
        for f in base.rglob("*"):
            if f.is_file() and f.suffix in REWRITE_SUFFIXES:
                yield f
    for name in REWRITE_FILES:
        f = claude_dir / name
        if f.is_file():
            yield f


def _rewrite_file(path: Path, pairs, dry: bool) -> int:
    """Rewrite one file in place. Returns the number of occurrences replaced."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0
    new_text, hits = rewrite_text(text, pairs)
    if hits and not dry:
        path.write_text(new_text, encoding="utf-8", newline="")
    return hits


def _merge_store(src: Path, dst: Path, dry: bool) -> tuple[int, int]:
    """Merge slug store src into dst. Returns (moved, kept_larger).

    A name present on both sides means the same session id was written under both
    spellings. Transcripts are append-only, so the LONGER file is the later one and
    wins; the loser is kept beside it with a .premigrate suffix rather than dropped,
    because "these two disagree" is a fact worth being able to inspect afterwards.
    """
    moved = kept = 0
    for s in sorted(src.rglob("*")):
        if not s.is_file():
            continue
        rel = s.relative_to(src)
        d = dst / rel
        if d.exists():
            if d.stat().st_size >= s.stat().st_size:
                if not dry:
                    s.replace(d.with_suffix(d.suffix + ".premigrate"))
                kept += 1
                continue
            if not dry:
                d.replace(d.with_suffix(d.suffix + ".premigrate"))
        if not dry:
            d.parent.mkdir(parents=True, exist_ok=True)
            s.replace(d)
        moved += 1
    return moved, kept


def _remap_claude_json(claude_dir: Path, old_root: str, new_root: str, dry: bool) -> str:
    """Re-key .claude.json's `projects` map, JSON-aware.

    This one file cannot take the plain text substitution the others do. Its
    project entries are JSON *keys*, so when both spellings are present a textual
    replace produces a document with two identical keys — which is not invalid
    JSON, but every parser silently keeps only the last, discarding whichever
    entry it happened to see first along with its trust flag and tool allow-list.
    """
    f = claude_dir / ".claude.json"
    if not f.is_file():
        return "no .claude.json"
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return f"could not parse .claude.json ({e}); left untouched"

    projects = doc.get("projects")
    if not isinstance(projects, dict):
        return ".claude.json has no projects map"

    remapped = merged = 0
    out = {}
    for k, v in projects.items():
        nk = new_root + k[len(old_root):] if k.startswith(old_root) else k
        if nk != k:
            remapped += 1
        if nk in out and isinstance(out[nk], dict) and isinstance(v, dict):
            # An entry already exists under the new spelling. Keep it as the base
            # and let the old root's non-empty values win: the old entry is the one
            # that accumulated the trust dialog and the allow-list, while the new
            # one is usually a freshly created stub.
            base = dict(out[nk])
            base.update({kk: vv for kk, vv in v.items() if vv not in (None, [], {}, "", False)})
            out[nk] = base
            merged += 1
        else:
            out[nk] = v
    doc["projects"] = out

    # Any remaining string values anywhere in the document (mcpContextUris and
    # friends) still name the old root and are plain values, so they take the
    # ordinary substitution.
    def walk(node):
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str) and old_root in node:
            return node.replace(old_root, new_root)
        return node

    doc = walk(doc)
    if not dry:
        f.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return f"{remapped} project key(s) re-keyed, {merged} merged"


def relocate_root(claude_dir: Path, old_root: str, new_root: str,
                  dry: bool, prune_snapshots: bool) -> int:
    old_root, new_root = old_root.rstrip("/"), new_root.rstrip("/")
    old_pre, new_pre = encode_slug(old_root), encode_slug(new_root)
    projects = claude_dir / "projects"
    pairs = [(old_root, new_root)]

    print("Claude Code ROOT relocation")
    print(f"  config dir : {claude_dir}")
    print(f"  root       : {old_root}")
    print(f"             ->{new_root}")
    print(f"  slug prefix: {old_pre} -> {new_pre}")
    if dry:
        print("  MODE       : dry run, nothing will be written")

    if not projects.is_dir():
        die(f"no projects store at {projects}")

    stale = sorted(p for p in projects.iterdir() if p.is_dir() and p.name.startswith(old_pre))
    print(f"\n  slug dirs to re-key: {len(stale)}")
    if not stale:
        print("  (already relocated, or nothing to do)")

    moved_total = kept_total = merged_stores = 0
    for src in stale:
        dst = projects / (new_pre + src.name[len(old_pre):])
        if dst.exists():
            m, k = _merge_store(src, dst, dry)
            moved_total += m
            kept_total += k
            merged_stores += 1
            print(f"    merge  {src.name}\n        -> {dst.name}  ({m} moved, {k} kept-existing)")
            if not dry:
                shutil.rmtree(src, ignore_errors=True)
        else:
            print(f"    rename {src.name}\n        -> {dst.name}")
            if not dry:
                src.replace(dst)
            moved_total += 1

    # Content rewrite happens AFTER the moves, so files that were merged in are
    # covered by the same pass rather than needing a second one.
    files = hits = 0
    for f in _iter_rewritable(claude_dir):
        n = _rewrite_file(f, pairs, dry)
        if n:
            files += 1
            hits += n
    print(f"\n  content: {hits} occurrence(s) rewritten across {files} file(s)")
    print(f"  .claude.json: {_remap_claude_json(claude_dir, old_root, new_root, dry)}")

    snaps = claude_dir / "shell-snapshots"
    if snaps.is_dir():
        n = len(list(snaps.glob("*")))
        if prune_snapshots:
            print(f"  shell-snapshots: removing {n} (each pins a whole stale PATH; they regenerate)")
            if not dry:
                for s in snaps.glob("*"):
                    s.unlink(missing_ok=True)
        elif n:
            print(f"  shell-snapshots: {n} left in place — pass --prune-snapshots to remove "
                  f"(every one exports the old root's PATH)")

    # ---- verification, the part that makes this re-runnable with confidence --
    # In a dry run these are necessarily the BEFORE counts, since nothing was
    # written. Saying so matters: "18 (want 0)" reads as a failed run otherwise,
    # and the one time you most need to trust this output is the time you are
    # deciding whether to commit to it.
    print("\n  verify:" + ("   [dry run: pre-change counts, not results]" if dry else ""))
    left = [p.name for p in projects.iterdir() if p.is_dir() and p.name.startswith(old_pre)]
    print(f"    slug dirs still on the old root : {len(left)}  (want 0)")
    residue = sum(1 for f in _iter_rewritable(claude_dir)
                  if old_root in f.read_text(encoding="utf-8", errors="ignore"))
    print(f"    files still naming the old root : {residue}  (want 0)")
    cj = claude_dir / ".claude.json"
    cj_hits = cj.read_text(encoding="utf-8", errors="ignore").count(old_root) if cj.is_file() else 0
    print(f"    .claude.json old-root mentions  : {cj_hits}  (want 0)")

    if dry:
        print("\n[dry-run] no changes made.")
    else:
        print(f"\nDone. {moved_total} store(s)/file(s) moved, {merged_stores} store(s) merged.")
        print("Re-runnable: run it again after a later catch-up sync and it is a no-op "
              "if nothing new arrived.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Migrate a Claude Code project folder + session history.")
    ap.add_argument("--old", help="current absolute project path (single-project mode)")
    ap.add_argument("--new", help="target absolute project path (single-project mode)")
    ap.add_argument("--old-root", help="old persistent root (root-relocation mode)")
    ap.add_argument("--new-root", help="new persistent root (root-relocation mode)")
    # $CLAUDE_CONFIG_DIR FIRST, because ~/.claude is the wrong answer on exactly the
    # setups this script is for: a persistent root keeps the config dir off $HOME so
    # it survives the box, which means the default would point at a directory that
    # does not exist and the run would silently find nothing to do.
    ap.add_argument("--claude-dir",
                    default=os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude"),
                    help="Claude config dir (default: $CLAUDE_CONFIG_DIR, else ~/.claude)")
    ap.add_argument("--prune-snapshots", action="store_true",
                    help="root mode: delete shell-snapshots (each pins a stale PATH; they regenerate)")
    ap.add_argument("--dry-run", action="store_true", help="preview only; change nothing")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = ap.parse_args(argv)

    # ---- root-relocation mode --------------------------------------------
    if args.old_root or args.new_root:
        if not (args.old_root and args.new_root):
            die("--old-root and --new-root must be given together")
        if args.old or args.new:
            die("--old/--new (single project) cannot be combined with --old-root/--new-root")
        cdir = Path(args.claude_dir)
        if not cdir.is_dir():
            die(f"no Claude config dir at {cdir} (set --claude-dir or $CLAUDE_CONFIG_DIR)")
        if not args.dry_run and not args.yes:
            ans = input("\nProceed with the root relocation? type MIGRATE to continue: ")
            if ans.strip() != "MIGRATE":
                die("cancelled by user.")
        return relocate_root(cdir, norm(args.old_root), norm(args.new_root),
                             args.dry_run, args.prune_snapshots)

    # ---- single-project mode ---------------------------------------------
    if not (args.old and args.new):
        die("give either --old/--new (one project) or --old-root/--new-root (whole root)")

    old, new = norm(args.old), norm(args.new)
    old_slug, new_slug = encode_slug(old), encode_slug(new)
    projects = Path(args.claude_dir) / "projects"
    old_store, new_store = projects / old_slug, projects / new_slug
    pairs = path_pairs(old, new)

    print("Claude Code project migration")
    print(f"  project : {old}")
    print(f"          ->{new}")
    print(f"  slug    : {old_slug}")
    print(f"          ->{new_slug}")
    print(f"  store   : {old_store}")
    print(f"          ->{new_store}")

    # ---- preflight --------------------------------------------------------
    if not Path(old).is_dir():
        die(f"project folder not found: {old} (already renamed?)")
    if Path(new).exists():
        die(f"target already exists: {new}")
    has_store = old_store.is_dir()
    if not has_store:
        print(f"  NOTE: no session store at {old_store} — folder will be renamed, "
              f"but there are no sessions to migrate.")
    elif new_store.exists():
        die(f"target store already exists: {new_store}")

    transcripts = sorted(old_store.rglob("*.jsonl")) if has_store else []
    print(f"  transcripts to rewrite: {len(transcripts)}")

    # ---- dry run ----------------------------------------------------------
    if args.dry_run:
        print("\n[dry-run] validating rewrite on a throwaway copy of one transcript...")
        if transcripts:
            sample = transcripts[0]
            text = sample.read_text(encoding="utf-8")
            before = text.count(pairs[0][0]) if pairs else 0
            new_text, _ = rewrite_text(text, pairs)
            after = new_text.count(pairs[0][0]) if pairs else 0
            ok = True
            lines = [l for l in new_text.splitlines() if l.strip()]
            for ln in (lines[:1] + lines[-1:]):
                try:
                    json.loads(ln)
                except Exception:
                    ok = False
            print(f"  functional cwd occurrences: {before} -> {after} (want 0)")
            print(f"  rewritten transcript still valid JSON: {ok}")
        print("[dry-run] no changes made.")
        return 0

    # ---- confirm ----------------------------------------------------------
    if not args.yes:
        ans = input("\nProceed with rename + migration? type MIGRATE to continue: ")
        if ans.strip() != "MIGRATE":
            die("cancelled by user.")

    # ---- 1) backup the store (non-destructive) ----------------------------
    backup = None
    if has_store:
        backup = Path(tempfile.gettempdir()) / f"claude-session-backup-{old_slug}"
        if backup.exists():
            shutil.rmtree(backup)
        shutil.copytree(old_store, backup)
        print(f"Backed up session store -> {backup}")

    # ---- 2) rename the project folder (lock-prone; do first) --------------
    try:
        shutil.move(old, new)
    except (OSError, PermissionError) as e:
        die(f"could not rename '{old}'. Is Claude Code still running, or is a shell/"
            f"Explorer window inside it? Close them and re-run. ({e})")
    print(f"Renamed project folder -> {new}")

    # ---- 3) rename the slug store -----------------------------------------
    if has_store:
        shutil.move(str(old_store), str(new_store))
        print(f"Renamed session store -> {new_store}")

        # ---- 4) rewrite embedded paths inside transcripts -----------------
        rewritten = 0
        for f in sorted(new_store.rglob("*.jsonl")):
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            new_text, hits = rewrite_text(text, pairs)
            if new_text != text:
                f.write_text(new_text, encoding="utf-8", newline="")
                rewritten += 1
        print(f"Rewrote embedded paths in {rewritten} transcript file(s).")

    # ---- done -------------------------------------------------------------
    print("\nDone. Resume with:")
    print(f'    cd "{new}"')
    print("    claude --resume")
    if backup:
        print(f"\nBackup kept at: {backup}  (delete once resume is confirmed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
