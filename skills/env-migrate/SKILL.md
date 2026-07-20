# Skill: env-migrate

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
- Sessions live at `~/.claude/projects/<SLUG>/<uuid>.jsonl`.
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

Script path: `~/.claude/skills/env-migrate/migrate_session.py`

1. **Dry run first** (changes nothing — confirm the slug mapping, transcript
   count, and that embedded cwd count drops to 0):
   ```
   python "~/.claude/skills/env-migrate/migrate_session.py" \
       --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>" --dry-run
   ```
2. **Migrate** (`--yes` skips the prompt; `--claude-dir` if `~/.claude` is elsewhere):
   ```
   python "~/.claude/skills/env-migrate/migrate_session.py" \
       --old "<OLD_ABS_PATH>" --new "<NEW_ABS_PATH>"
   ```
3. **Resume** from the new path:
   ```
   cd "<NEW_ABS_PATH>" && claude --resume
   ```
On Windows, invoke with `python` (or `py`); the script is OS-agnostic.

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
