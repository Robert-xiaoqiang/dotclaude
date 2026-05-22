# dotclaude

My portable [Claude Code](https://claude.com/claude-code) configuration, version-controlled in place at `~/.claude`.

Only **portable, secret-free** files are tracked. Everything else in `~/.claude`
(credentials, session logs, caches, the machine-specific `settings.json`, and the
personal `CLAUDE.md`) is ignored by a deny-all `.gitignore`, so this repo is safe
to keep public.

## What's tracked

| Path | What it is | Platform |
|------|------------|----------|
| `skills/`     | Custom skills (`SKILL.md` instructions)  | independent |
| `agents/`     | Custom subagents (markdown definitions)  | independent |
| `commands/`   | Custom slash commands (markdown)         | independent |
| `hooks/<os>/` | Executable hook scripts, split by OS     | **OS-specific** |
| `.gitignore`  | Deny-all allow-list that keeps secrets out | — |

Skills, agents, and commands are *instructions/config for the model* — identical
on every OS, so they stay flat. **Only `hooks/` holds executable scripts**, so it
is split per platform: `hooks/linux/` today; add `hooks/macos/`, `hooks/windows/`
as needed.

Deliberately **not** tracked: `settings.json` (absolute paths + OS-specific
command/permission syntax, and where hooks are wired up), `CLAUDE.md` (personal),
`.credentials.json`, and all runtime/session state.

> ⚠️ The tracked dirs are allow-listed wholesale — never put a secret inside
> `skills/`, `agents/`, `commands/`, or `hooks/` or it will be committed.

## Activating hooks (per machine)

Hook *scripts* are versioned here but only fire once referenced from
`settings.json`, which is intentionally machine-local. See `hooks/README.md`
for the exact snippet.

## Set up on a new device

```bash
cd ~/.claude
git init
git remote add origin git@github.com:<you>/dotclaude.git
git fetch origin
# Bring tracked files in without touching local untracked/ignored files:
git checkout -t origin/main -- . 2>/dev/null || git reset --hard origin/main
```

## Day-to-day

```bash
cd ~/.claude
git status            # only ever shows the allow-listed paths
git add -A            # safe: deny-all .gitignore blocks everything else
git commit -m "..."
git push
```
