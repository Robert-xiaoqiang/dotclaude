# hooks

Executable hook scripts, **split by interpreter** because — unlike
skills/agents/commands — these actually run on the machine, and what decides
whether a script can run is which interpreter is installed, not the OS. Bash
scripts run on Linux/macOS/WSL/Git Bash; PowerShell scripts run on Windows (and
on `pwsh` anywhere). Keep each interpreter's scripts under its own folder; the
`.sh` / `.ps1` extension already reinforces which is which. For a script that's
genuinely OS-specific (e.g. `pbcopy` vs `xclip`), put the OS in the *filename*
(`copy-clipboard-macos.sh`) or detect it at runtime — the folder stays
interpreter-based.

## Bash scripts (Linux / macOS / WSL / Git Bash)

| Script | Event | Does |
|--------|-------|------|
| `bash/protect-secrets.sh`   | `PreToolUse` on `Edit\|Write`  | Blocks edits to `.env`, `*.pem`, `*.key`, `credentials`, etc. |
| `bash/format-after-edit.sh` | `PostToolUse` on `Edit\|Write` | Runs black/prettier/gofmt/rustfmt on the edited file if installed |

## PowerShell scripts (Windows, or `pwsh` anywhere)

| Script | Event | Does |
|--------|-------|------|
| `powershell/protect-secrets.ps1` | `PreToolUse` on `Edit\|Write` | Blocks edits to `.env`, `*.pem`, `*.key`, `credentials`, etc. (PowerShell port of the bash script) |

## Wiring them up (per machine)

Scripts here are dormant until referenced from `settings.json`'s `"hooks"` key.
`settings.json` itself **is** tracked (since 2026-07-30 — it carries `effortLevel`,
`tui`, `theme` and prompt toggles too, which are genuinely identical across
machines), but the *bash vs PowerShell* wiring below is not something one tracked
block can express for both OS families: the `command` string is OS-specific syntax
(a direct executable path on bash, `powershell -File ...\x.ps1` on Windows), so a
single synced `"hooks"` block only works if every machine you sync to is in the
same interpreter family. For a bash-only fleet (Linux/macOS/WSL), it is safe and
correct to put the bash block directly in the tracked `settings.json`; add a
PowerShell machine later and that block would need to move to a local override or
gain an OS check. The paths below use `$CLAUDE_CONFIG_DIR` so they resolve wherever
your config dir lives (it defaults to `~/.claude`); the variable is exported in
your shell, so Claude Code expands it when it runs the hook.

On a bash machine (Linux/macOS/WSL/Git Bash), add this to your `settings.json`
(the one inside `$CLAUDE_CONFIG_DIR`):

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "$CLAUDE_CONFIG_DIR/hooks/bash/protect-secrets.sh" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "$CLAUDE_CONFIG_DIR/hooks/bash/format-after-edit.sh" } ] }
    ]
  }
}
```

Make sure the scripts are executable: `chmod +x "$CLAUDE_CONFIG_DIR/hooks/bash/"*.sh`.

For the PowerShell hook, add this to your `settings.json` under
`%USERPROFILE%\.claude` (or `%CLAUDE_CONFIG_DIR%`, if you set it). PowerShell
isn't invoked by the executable bit, so call it explicitly:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "powershell -NoProfile -ExecutionPolicy Bypass -File %USERPROFILE%\\.claude\\hooks\\powershell\\protect-secrets.ps1" } ] }
    ]
  }
}
```

## Native git hooks (`git/`) — a different mechanism, not Claude Code's

Everything above is a **Claude Code hook**: triggered by an event in Claude Code's
own tool-call loop (`PreToolUse`, `PostToolUse`, …), configured in `settings.json`,
and meaningless outside a Claude Code session.

`git/` holds **git's own hooks** instead — triggered by `git` itself, via the
standard [`githooks(5)`](https://git-scm.com/docs/githooks) mechanism, wired up
with `git config core.hooksPath` rather than anything in `settings.json`. The
filename is fixed by git (`commit-msg`, `pre-commit`, …, no extension), and it
fires for **every** commit on the machine — from any Claude Code session, from a
plain terminal, from any other tool — because git doesn't know or care who called
it. That is strictly wider coverage than a `PostToolUse` hook matching `Bash` could
ever get (which only sees commits made through Claude Code's own Bash tool), for
less complexity: no JSON to parse, no `jq`/`python3` dependency, just the message
file git already hands the hook at `$1`.

| Script | Fires on | Does |
|--------|----------|------|
| `git/commit-msg` | every `git commit` (and `--amend`) | Strips any `Co-Authored-By:` trailer, case-insensitively, before the commit object is written |

**Why this exists alongside `"includeCoAuthoredBy": false` in `settings.json`.**
That setting is real (verified against the installed CLI binary) and is the
first-class way to stop Claude from writing the trailer at all — but it is a
closed-box behavior inside Claude Code that only takes effect in a session started
*after* the setting was set, and its correctness can't be independently checked
from outside. This hook is the opposite on every axis: fully readable in this
repo, testable with two `git commit` calls, and it fires regardless of whether
that setting works, whether a session predates it, or whether the committer is
Claude at all.

### Wiring it up (per machine, one time)

```sh
git config --global core.hooksPath "$CLAUDE_CONFIG_DIR/hooks/git"
```

This applies to every repo on the machine (no per-repo setup), unless a repo
already sets its own `core.hooksPath` or relies on `.git/hooks/` directly (e.g. via
`pre-commit install` or Husky) — check for that before going global, since a
global `core.hooksPath` replaces git's default `.git/hooks/` lookup entirely
rather than adding to it.

**On the CPFS Linux boxes this is automatic**, and has to be: `~/.gitconfig` lives
under `$HOME=/root`, which is on the same volatile overlay as `~/.bashrc` and
`~/.ssh` — wiped on every DSW relaunch. `home.sh --boot` (and therefore the onStart
hook) reapplies it every time, the same way it reinstalls the bashrc hook and
copies ssh keys back. On any other machine (a Mac, a plain Linux box not using this
`home.sh`), run the `git config` line above once yourself; nothing here does it for
you.
