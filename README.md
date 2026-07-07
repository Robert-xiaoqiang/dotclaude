# dotclaude

My portable [Claude Code](https://claude.com/claude-code) configuration, version-controlled **in place inside the Claude Code config directory**.

That directory is `~/.claude` by default, but its true location is wherever the
`CLAUDE_CONFIG_DIR` environment variable points — so this repo lives at
`"$CLAUDE_CONFIG_DIR"` (plain `~/.claude` on a laptop, or a persistent path such
as `/mnt/cpfs/<you>/.claude` on an ephemeral cloud box). It holds **user-level**
("personal") config — skills, subagents, slash commands, hooks — as opposed to a
project's own `.claude/`.

Only **portable, secret-free** files are tracked. Everything else in the config
dir (credentials, session logs, caches, the machine-specific `settings.json`, and
the personal `CLAUDE.md`) is ignored by a deny-all `.gitignore`, so this repo is
safe to keep public.

## The config directory (`$CLAUDE_CONFIG_DIR`)

Claude Code stores user-level config under `~/.claude` unless `CLAUDE_CONFIG_DIR`
is set, which relocates the whole directory — handy for keeping it on a
persistent/mounted filesystem or for multi-account setups. Set it in your shell
profile so every command below resolves correctly:

```bash
export CLAUDE_CONFIG_DIR="$HOME/.claude"          # default; or a persistent path:
# export CLAUDE_CONFIG_DIR="/mnt/cpfs/you/.claude"
```

Where you never set it, `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}"` simply falls back
to `~/.claude`.

## What's tracked

| Path | What it is | Layout |
|------|------------|--------|
| `skills/`         | Personal skills (`SKILL.md` instructions)  | flat |
| `agents/`         | Personal subagents (markdown definitions)  | flat |
| `commands/`       | Personal slash commands (markdown)         | flat |
| `hooks/<interp>/` | Executable hook scripts                    | **by interpreter** |
| `.gitignore`      | Deny-all allow-list that keeps secrets out | — |

Skills, agents, and commands are *instructions/config for the model* — identical
everywhere, so they stay flat. **Only `hooks/` holds executable scripts**, so it
is split by interpreter: `hooks/bash/` (Linux/macOS/WSL/Git Bash) and
`hooks/powershell/` (Windows, or `pwsh` anywhere). See `hooks/README.md`.

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
cd "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
git init
git remote add origin git@github.com:Robert-xiaoqiang/dotclaude.git
git fetch origin
# Bring tracked files in without touching local untracked/ignored files:
git checkout -b main origin/main
```

## Day-to-day

```bash
cd "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
git status            # only ever shows the allow-listed paths
git add -A            # safe: deny-all .gitignore blocks everything else
git commit -m "..."
git push
```
