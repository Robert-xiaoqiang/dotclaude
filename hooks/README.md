# hooks

Executable hook scripts, **split by OS** because — unlike skills/agents/commands —
these actually run on the machine. Add `hooks/macos/` and `hooks/windows/` as
needed; keep each platform's scripts under its own folder with natural names.

## Linux scripts

| Script | Event | Does |
|--------|-------|------|
| `linux/protect-secrets.sh`   | `PreToolUse` on `Edit\|Write`  | Blocks edits to `.env`, `*.pem`, `*.key`, `credentials`, etc. |
| `linux/format-after-edit.sh` | `PostToolUse` on `Edit\|Write` | Runs black/prettier/gofmt/rustfmt on the edited file if installed |

## Wiring them up (per machine)

Scripts here are dormant until referenced from `settings.json` — which is
**not** tracked (it's machine-specific). Add this to `~/.claude/settings.json`
on each Linux device:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "$HOME/.claude/hooks/linux/protect-secrets.sh" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "$HOME/.claude/hooks/linux/format-after-edit.sh" } ] }
    ]
  }
}
```

Make sure the scripts are executable: `chmod +x ~/.claude/hooks/linux/*.sh`.
