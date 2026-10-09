# dotclaude

My portable [Claude Code](https://claude.com/claude-code) configuration, version-controlled **in place inside the Claude Code config directory**.

That directory is `~/.claude` by default, but its true location is wherever the
`CLAUDE_CONFIG_DIR` environment variable points, so this repo lives at
`"$CLAUDE_CONFIG_DIR"` (plain `~/.claude` on a laptop, or a persistent path such
as `/mnt/cpfs/<you>/.claude` on an ephemeral cloud box). It holds your
**user-level** (personal) config, the skills, subagents, slash commands, and
hooks. This is separate from a project's own `.claude/`.

Only **portable, secret-free** files are tracked. Everything else in the config
dir (credentials, session logs, caches, the machine-specific `settings.json`, and
the personal `CLAUDE.md`) is ignored by a deny-all `.gitignore`, so this repo is
safe to keep public.

## The config directory (`$CLAUDE_CONFIG_DIR`)

Claude Code stores user-level config under `~/.claude` unless `CLAUDE_CONFIG_DIR`
is set, which relocates the whole directory. That is handy for keeping it on a
persistent or mounted filesystem, or for multi-account setups. Set it in your
shell profile so every command below resolves correctly.

```bash
export CLAUDE_CONFIG_DIR="$HOME/.claude"          # default, or a persistent path
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
| `.claude-plugin/marketplace.json` | The plugins this config uses, pinned to a commit | one file |
| `.gitignore`      | Deny-all allow-list that keeps secrets out | n/a |

Skills, agents, and commands are *instructions and config for the model*. They
are identical everywhere, so they stay flat. **Only `hooks/` holds executable
scripts**, so it is split by interpreter. Bash scripts live in `hooks/bash/`
(Linux, macOS, WSL, Git Bash) and PowerShell scripts in `hooks/powershell/`
(Windows, or `pwsh` anywhere). See `hooks/README.md`.

Some things are deliberately **not** tracked. Those are `settings.json` (absolute
paths and OS-specific command and permission syntax, plus where hooks are wired
up), `CLAUDE.md` (personal), `.credentials.json`, `.claude.json` (accounts and
per-project MCP servers), `plugins/` (Claude Code's own plugin install cache), and
all runtime and session state.

## Plugins and the marketplace

A plugin uses the same layout as this directory: `skills/`, `agents/`,
`commands/`, `hooks/` and an `.mcp.json`, with a manifest in `.claude-plugin/`.
A marketplace is a catalogue of plugins, one `.claude-plugin/marketplace.json`.
This repository is a marketplace named `dotclaude`, so the plugins the config
uses are recorded in a tracked file beside the skills, not only in machine-local
install state.

Each entry names a plugin's git source and the commit it was tested at.
A third-party plugin is referenced, never copied in: its author keeps
publishing fixes, and a copy here would freeze it. Today it lists one plugin,
Icons8's, which brings the Icons8 MCP server that `skills/drawing-icons` uses.

`plugins/` is not where these live. That directory is Claude Code's install
cache: clones, versions and `installed_plugins.json`, all written by `claude
plugin install`. A plugin written here would go in `skills/<name>/` with its own
`.claude-plugin/plugin.json`, where Claude Code loads it as `<name>@skills-dir`
(`claude plugin init <name>` scaffolds one), or under its own directory listed
in the marketplace by relative path.

```bash
# change a pin or add a plugin: edit the manifest, then
claude plugin validate .claude-plugin/marketplace.json
claude plugin marketplace update dotclaude
claude plugin update icons8@dotclaude     # or: claude plugin install <name>@dotclaude
```

**Why the manifest sits at this repository's root.** A marketplace's root is the
directory that holds `.claude-plugin/`, and this repository's root is the config
directory. So the catalogue's scope is the Claude config and nothing wider:
relative plugin sources resolve inside it, and adding `Robert-xiaoqiang/dotclaude`
from GitHub would clone only Claude config. Putting it beside `.claude/` at the
root of a home or dotfiles repository would make the whole home the marketplace
root, and a clone of this repository alone would lose the record. A dotfiles
repository that includes this one as a submodule still carries it.

**No extra variable.** `CLAUDE_CONFIG_DIR` already decides where everything lives:
Claude Code stores settings, sessions and plugins under it, and this checkout is
the marketplace. No variable names a marketplace. Claude Code finds one through
`extraKnownMarketplaces` in `settings.json`, which stores it as an absolute path.
`CLAUDE_CODE_PLUGIN_CACHE_DIR` would move only the install store out from under
the config directory, so leave it unset.

```bash
claude plugin marketplace list            # dotclaude -> Folder ($CLAUDE_CONFIG_DIR)
claude plugin list                        # icons8@dotclaude, enabled
ls "$CLAUDE_CONFIG_DIR"/plugins/cache/dotclaude/icons8/   # the installed copy, by version
```

Inside a session, `/plugin` shows the same, and a plugin's own hooks and servers
see their install directory as `${CLAUDE_PLUGIN_ROOT}`.

**After moving the config directory,** the absolute path in `settings.json` points
at the old place and the plugin fails to load. Adding the marketplace again from
the new place repoints it, and installed plugins load again:

```bash
claude plugin marketplace add "$CLAUDE_CONFIG_DIR"
```

> ⚠️ The tracked dirs are allow-listed wholesale, so never put a secret inside
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
git checkout -b master origin/master
```

Then install the plugins the marketplace manifest lists. The checkout itself is the
marketplace, so this needs nothing but the clone:

```bash
claude plugin install icons8 --marketplace "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
# or, inside a session: /plugin marketplace add <that path>, then /plugin install icons8@dotclaude
```

A box that mounts an existing config directory already has them installed.

## Day-to-day

```bash
cd "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
git status            # only ever shows the allow-listed paths
git add -A            # safe: deny-all .gitignore blocks everything else
git commit -m "..."
git push
```
