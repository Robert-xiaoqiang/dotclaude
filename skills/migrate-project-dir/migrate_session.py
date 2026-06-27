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

Usage:
    python migrate_session.py --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>" [--dry-run] [--yes]
    python migrate_session.py --old ... --new ... --claude-dir "<~/.claude>"

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Migrate a Claude Code project folder + session history.")
    ap.add_argument("--old", required=True, help="current absolute project path")
    ap.add_argument("--new", required=True, help="target absolute project path")
    ap.add_argument("--claude-dir", default=str(Path.home() / ".claude"),
                    help="Claude config dir (default: ~/.claude)")
    ap.add_argument("--dry-run", action="store_true", help="preview only; change nothing")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = ap.parse_args(argv)

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
