---
name: claude-migrate
description: "Rename or move a Claude Code project folder without orphaning its session history, or recover sessions after a whole persistent root moved."
when_to_use: "Use when --resume or --continue stops finding past sessions after a rename, move, or storage migration."
---
# Skill: claude-migrate

## Purpose
Rename or move a Claude Code **project folder** without losing its session
history. Claude Code keys sessions by the project's absolute path, so a plain
folder rename orphans every prior session (`claude --resume` can't find them).
This skill renames the folder, renames the matching `~/.claude/projects/<slug>`
store, AND rewrites the absolute-path references baked inside the `.jsonl`
transcripts — so resume keeps working.

## When to Use
- The user wants to **rename or move a project directory** and keep `--resume`/`--continue` working
- "I renamed/moved my project and my Claude sessions are gone / won't resume"
- Reorganizing repos or folders that already have Claude Code history
- A project's path changes (rename, move, different drive)
- Renaming the project/package as part of a rebrand (folder name should follow)

## Background — why a plain rename breaks sessions
- Sessions live at `$CLAUDE_CONFIG_DIR/projects/<SLUG>/<uuid>.jsonl` — `~/.claude` only when
  that variable is unset. On a box whose Claude state lives on shared storage the two differ,
  and a `~/.claude/...` path there points at nothing; pass `--claude-dir` to be explicit.
  **SLUG** = the absolute path with every non-alphanumeric char replaced by `-`
  (no collapsing, case preserved):
  - Windows: `D:\projects\Old App` → `D--projects-Old-App`
  - Unix: `/home/u/old app` → `-home-u-old-app`
- `--resume` / `--continue` discover sessions purely by the **current dir's SLUG**.
- Each transcript also stores the absolute path internally (a `"cwd"` field on
  many lines), so even after renaming the slug folder, resume may not list the
  session unless those embedded paths are rewritten too (a known footgun).

## ⚠️ Check FIRST: is this the *currently open* project?
- **Yes (the session you're in runs from this folder):** you CANNOT rename it
  live — the OS locks the cwd and the transcript is open. Prepare the command,
  tell the user to **fully exit Claude Code**, then run it **from a shell that is
  not inside the folder**, then `claude --resume`. Do not attempt the rename from
  inside the running session.
- **No (a different, not-open project):** you can run the migration now.

## Procedure (cross-platform — preferred)
Use the bundled helper. It computes slugs, backs up the store, renames the
folder + slug store, rewrites embedded paths (BOM-safe, JSON-valid), and prints
how to resume. Needs only Python 3.

Script path: `${CLAUDE_SKILL_DIR}/migrate_session.py`

1. **Dry run first** (changes nothing — confirm the slug mapping, transcript
   count, and that embedded cwd count drops to 0):
   ```
   python "${CLAUDE_SKILL_DIR}/migrate_session.py" \
       --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>" --dry-run
   ```
2. **Migrate** (`--yes` skips the prompt; `--claude-dir` if `~/.claude` is elsewhere):
   ```
   python "${CLAUDE_SKILL_DIR}/migrate_session.py" \
       --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>"
   ```
3. **Resume** from the new path:
   ```
   cd "<NEW_ABS_PATH>" && claude --resume
   ```
On Windows, invoke with `python` (or `py`); the script is OS-agnostic.

## The other case: the whole persistent root moved

Use `--old-root/--new-root` when a persistent home moved and **every** project moved
with it — a new cluster, a new mount, a storage migration. This is not the same job
as the one above and the single-project mode cannot do it:

- **Nothing needs renaming on disk.** An rsync already put both trees in place, so
  the folder move that mode leads with is not just unnecessary — its
  `if Path(new).exists(): die(...)` preflight fires on every project, above the
  `--dry-run` branch, so there is not even a way to look without failing.
- **One `--old/--new` pair cannot cover it.** A real store had 65 distinct embedded
  cwd values behind 18 slugs.
- **Both spellings can already hold sessions.** Work done from the new root before
  the migration finished creates new-root slugs, so the old store must be **merged**
  into the new one. `mv` of a directory onto an existing directory nests it a level
  deep, where `--resume` will never look.

```
python "${CLAUDE_SKILL_DIR}/migrate_session.py" \
    --old-root /mnt/cpfs/xqwang --new-root /mnt/data/xqwang \
    --claude-dir /mnt/data/xqwang/.claude --prune-snapshots --dry-run
```

Drop `--dry-run` (add `--yes`) to run it. It is **re-runnable**: run it again after a
later catch-up sync and it is a no-op if nothing new arrived. That matters because
the final sync has to happen after the last old-root session exits, which is
necessarily after you have already migrated once.

### Things that cost time to learn
- **The slug encoding is one-way.** `encode_slug` maps every non-alphanumeric char to
  `-`, so `/` and `_` are indistinguishable afterwards and decoding a slug to re-encode
  it invents paths that never existed. Both roots encode to a fixed prefix, so
  substitute on the **slug string**, never round-trip through a path.
- **Anchor on the full old root, never the mount point.** `/mnt/cpfs` also prefixes
  other people's homes, and transcripts legitimately reference their shared
  checkpoints. Substituting on the mount point corrupts those references.
- **`.jsonl` is not enough.** Sidecar `.js` workflow scripts, `.json` task state and
  `.md` notes carry absolute paths too — 12,071 references across 156 non-jsonl files
  in one real store.
- **Files outside `projects/` matter.** `history.jsonl`, `.claude.json`,
  `plugins/known_marketplaces.json`, `jobs/*/state.json`, `settings.local.json`.
- **`.claude.json` needs JSON-aware handling.** Its project entries are *keys*, so a
  textual replace when both spellings are present yields duplicate keys and every
  parser silently keeps only the last — discarding a trust flag and tool allow-list.
- **Shell snapshots are poison, not data.** Every one pins a whole stale `PATH` and
  they are live-sourced by each Bash call. `--prune-snapshots` deletes them; they
  regenerate.
- **Never `rsync --delete` the catch-up pass.** Claude Code garbage-collects its own
  state, so the old root can be *missing* files the new one should keep.
- **Exclude the tracked repo from the catch-up sync.** If `.claude` is a git checkout
  (skills, hooks), syncing the old root over it reverts commits and edits. Sync state
  only.

## Manual fallback (no Python)
Compute `SLUG = path with every non-[A-Za-z0-9] char → '-'`. Then:

**Windows (PowerShell)** — run after exiting Claude, from outside the folder:
```powershell
$old='D:\projects\Old App'; $new='D:\projects\New App'
$oldSlug='D--projects-Old-App'; $newSlug='D--projects-New-App'
$base="$env:USERPROFILE\.claude\projects"
Rename-Item $old -NewName (Split-Path $new -Leaf)
Rename-Item "$base\$oldSlug" -NewName $newSlug
Get-ChildItem "$base\$newSlug" -Recurse -Filter *.jsonl | ForEach-Object {
  $t=[IO.File]::ReadAllText($_.FullName)
  $t=$t.Replace('D:\\projects\\Old App','D:\\projects\\New App') ` # JSON "cwd" (note doubled backslashes)
      .Replace('D:/projects/Old App','D:/projects/New App') `
      .Replace('/d/projects/Old App','/d/projects/New App')
  [IO.File]::WriteAllText($_.FullName,$t)   # UTF-8, no BOM
}
```

**macOS / Linux (bash)**:
```bash
old="/home/u/old app"; new="/home/u/new app"
oldSlug="-home-u-old-app"; newSlug="-home-u-new-app"
base="$HOME/.claude/projects"
mv "$old" "$new"
mv "$base/$oldSlug" "$base/$newSlug"
# rewrite embedded cwd (paths in .jsonl use forward slashes on unix)
grep -rl --include='*.jsonl' "$old" "$base/$newSlug" | while read f; do
  python3 - "$f" "$old" "$new" <<'PY'
import sys; p,o,n=sys.argv[1:4]
open(p,'w',encoding='utf-8').write(open(p,encoding='utf-8').read().replace(o,n))
PY
done
```

## Notes
- **Reversible**: rename both folders back to undo; the helper also writes a
  store backup to the system TEMP dir.
- **Official alternative**: `/cd <existing-dir>` (Claude Code v2.1.169+) moves a
  *live* session to another **existing** folder and preserves the prompt cache —
  but it can't rename the *current* folder in place, so for an in-place rename use
  this skill.
- The helper rewrites three path forms: JSON-escaped native (functional `cwd`),
  forward-slash, and git-bash drive (`/d/...`).
- Always do a `--dry-run` and confirm "valid JSON: True" before the real run.
