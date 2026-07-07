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

Scripts here are dormant until referenced from `settings.json` — which is **not**
tracked (it's machine-specific). The paths below use `$CLAUDE_CONFIG_DIR` so they
resolve wherever your config dir lives (it defaults to `~/.claude`); the variable
is exported in your shell, so Claude Code expands it when it runs the hook.

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
