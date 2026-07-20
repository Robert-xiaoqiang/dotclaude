# Skill: env-cluster

## Purpose
My playbook for configuring a usable, persistent working environment when I land in a new compute environment, before running any real work. These are usually containerized cluster nodes where the local filesystem is ephemeral and a shared filesystem is mounted for persistence. It applies to both an interactive session, where I get a shell, and a submitting-based job session, where work runs from a batch script. It records the steps to take, where things should live, and my preferences, so a new environment comes up the same way every time. It is a decision and preference guide, not a copy of any one machine's config.

## When to Use
- The first time I land on a new cluster node or container and need to configure it before working.
- Writing or fixing a job-submission script so it resolves the same tools, paths, and caches as my interactive shell.
- Deciding where a new tool's config, data, or cache should live.
- Debugging why something did not persist across a node or container restart.

## The environment model (read first)
The compute node or container is ephemeral, and its local home is wiped when it dies or is rescheduled. A shared filesystem is mounted and persists across nodes. The whole game is to put everything durable on that shared mount and treat the node as disposable. The first move on any new environment is to identify the persistent mount. Then two firm rules. Keep HOME as it is, because moving HOME breaks getpwuid, git, and ssh. Relocate config, data, state, caches, and tools onto the mount through environment variables, not by moving HOME.

## Landing checklist (the steps)
1. Find the persistent shared mount, and treat it as home base.
2. Put one env file on the mount. Source it from the shell rc for interactive shells, and from the top of every job script for batch shells.
3. Create the workspace dirs with role names, through the export-and-mkdir helper.
4. Point XDG and per-tool env vars at the mount so config, data, and state persist. Leave cache local.
5. Install toolchains under one `devtools` dir on the mount and add their bin dirs to PATH.
6. If the cluster gates egress, bring up a local proxy and route git-over-ssh through its 443 endpoint.
7. Set up interactive niceties (tmux, shell history, editor), guarded so non-interactive job shells skip them.
8. Persist dev-tooling state such as the Claude config dir and personal skills from a dotfiles repo.
9. Retire any superseded dirs in the ephemeral home with a `.premigrate` suffix.

## One env file, two session types
A single env file on the shared mount is the bootstrap that wires everything, and the same file must serve both session types.
- Interactive session, the shell rc (`~/.bashrc`) sources the env file, so every login shell is configured.
- Submitting-based job, the job script sources the same env file at its top, so the batch shell resolves the same tools, paths, and caches.
Because a job shell is non-interactive, the env file must be non-interactive-safe. Do not use `set -e`. Guard interactive-only bits such as tmux autostart, aliases, a login banner, and starting a proxy, so they are harmless when there is no tty. Make it safe to source more than once.

## The bootstrap hook
The only thing a fresh node needs by hand is the one line that sources the env file. Interactive shells get it from the shell rc, which itself lives on the ephemeral home, so re-add that line on a new node or inject it through the platform startup-script or module mechanism. Job scripts get it from their own explicit source line. Everything else follows from the env file.

## Workspace layout and naming (preference)
Under the persistent mount I keep a flat set of top-level dirs, named by role, and export each as a shortcut variable.
- Data and work dirs use plain role names, such as `projects`, `datasets`, `downloads`, and an output dir.
- Tool homes take a `_home` suffix, such as `uv_home`, `hf_home`, and similar per-tool caches and data.
- One `devtools` dir holds installed toolchains.
In the env file, use a helper that both exports a variable and creates its directory in a single line, so adding a persistent dir is one statement and can never be forgotten from a separate mkdir list. Create only data, cache, and config dirs, not install dirs that already exist. Drop intermediate variables that exist only to build PATH.

## Config, data, state, cache placement
Point `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME` at the mount so config, data, and state persist. Leave cache local, because it is regenerable and a network filesystem is slow for it. For tools that are not XDG-aware, set the tool's own env var to a dir on the mount, for HF, uv, triton, wandb, nltk, npm caches, and so on. Know the split. Config is what I set, data is what a tool made and I want to keep, state is replaceable history and logs, cache is throwaway. The limit worth remembering is that XDG only moves config for XDG-aware tools, so check each tool.

## Toolchain
Install node, uv, the language tools, TeX, and any proxy under the `devtools` dir on the mount and put their bin dirs on PATH. The caveat to remember is that binaries still depend on the node image for glibc, CUDA, and the GPU driver, so a new node must use the same image family. Only files, config, and data persist on the mount, not the runtime the image provides. For Python, prefer a uv-managed interpreter over the system one so a venv is portable, and rebuild dependencies with uv on a new node rather than copying the venv.

## Network and proxy (only if egress is gated)
On a cluster that gates outbound network, run a local proxy and keep its config on the mount under `XDG_CONFIG_HOME`, with both the config and any acl file in one dir. Keep runtime pids local and per-node, never on the shared mount, because a stale pid from a dead node can block startup or match an unrelated process. For git over ssh where the gateway blocks port 22, route the host through the proxy to its 443 endpoint with an explicit IdentityFile.

## Interactive niceties (interactive sessions only)
These matter only when I have a shell, so guard them so job shells skip them.
- tmux config lives in `XDG_CONFIG_HOME` and is instance-independent. Mouse on. TPM with resurrect and continuum so sessions restore after a restart, with resurrect saves in `XDG_DATA_HOME` and pids kept local. Clipboard is the gotcha. A mouse drag copies to tmux's buffer, and reaching the local clipboard needs OSC 52, which is `set-clipboard on` plus declaring the terminal clipboard feature, and it only works if the terminal supports it. iTerm2, WezTerm, and kitty do. macOS Terminal.app does not, so bind a key to toggle mouse off, select natively, Cmd-C, then toggle back on.
- Persist shell history to the mount.
- Keep editor config on the mount through the tool's env var or XDG.

## Dev-tooling state (Claude Code and similar)
Install the CLI under `devtools` and persist its state by pointing its config-dir env var at the mount. When migrating existing state, copy the config dir and its top-level json, rewrite only genuine path pointers such as a plugin install location, and leave session transcripts and memory verbatim, because they are logs keyed by working directory. Sync personal skills, agents, commands, and hooks from a dotfiles git repo checked out inside the config dir with a deny-all gitignore that allow-lists only portable, secret-free paths. Keep git identity in the XDG git config. Commit with no AI attribution trailer, and never auto-push, wait for an explicit request.

## Reference layout (a filled-in persistent home)
A complete example of the mount, rooted at the persistent home (call it `$CPFS_HOME`), that a new environment can be shaped to match. Grouped by role.

Bootstrap and secrets.
- `env.sh`, the single bootstrap file, sourced by the shell rc and by job scripts.
- `.secret`, a gitignored secret store, sourced last by `env.sh` so it can override anything above. Holds exported API keys and tokens, for example OpenAI, OpenRouter, the Hugging Face token, and the wandb API key.

Workspace and data, plain role names.
- `projects`, code repositories and working trees.
- `datasets`, input datasets for training and eval.
- `downloads`, fetched files and archives.
- `output_dir`, run and training outputs.
- `snippets`, small standalone scripts.

Tool homes and toolchains.
- `devtools`, installed toolchains with their bin dirs on PATH, holding node, an npm cache, uv, the claude CLI, TeX Live, and the proxy.
- `uv_home`, uv cache, managed pythons, tools, and venvs, from the `UV_*` vars.
- `hf_home`, Hugging Face cache and data, from `HF_HOME`.
- `triton_home`, Triton compiled-kernel cache and autotune, from `TRITON_HOME`.
- `wandb_local`, Weights and Biases run data, from `WANDB_DIR`.
- `nltk_data`, NLTK corpora, from `NLTK_DATA`.

XDG base dirs.
- `.config`, `XDG_CONFIG_HOME`, per-tool config, here git, pip, tmux, code-server, uv, and shadowsocks-rust with its config and acl.
- `.local`, `XDG_DATA_HOME` at `.local/share` and `XDG_STATE_HOME` at `.local/state`.

Dev-tooling state and history.
- `.claude`, `CLAUDE_CONFIG_DIR`, Claude Code state and the dotfiles repo checkout with its deny-all gitignore.
- `.bash_history`, persistent shell history, from `HISTFILE`.

Cache stays off the mount and local. The ephemeral home still holds ssh keys and image-based cloud credentials, which are recreated per node.

## Retirement pattern
When a location on the mount replaces an old dir in the ephemeral home, retire the old one by renaming it with a top-level `.premigrate` suffix. Rename, never delete, so it stays reversible, and it vanishes with the node anyway. Verify the mount already has everything first. Keep the markers top-level and consistent, with no nested premigrate inside a live dir.

## Pitfalls and reminders
- Current shells keep the old environment until re-sourced. Only new shells and new nodes pick up env-file changes, so validate a change by sourcing the env file in a throwaway subshell, not by trusting the running shell.
- The env file must survive a non-interactive job shell. No `set -e`, guard tty-only bits, safe to source twice.
- Runtime things do not belong on a network filesystem. Keep sockets and pids local.
- git config precedence bites. `~/.gitconfig` shadows the XDG git config, and git writes `--global` into `~/.gitconfig` when it exists. Move identity to the XDG path and remove `~/.gitconfig`.
- Some things stay volatile on purpose, such as ssh keys and image-based cloud credentials, and get recreated on a fresh node.
- A tool that respects `XDG_DATA_HOME` but not `XDG_CONFIG_HOME`, or the reverse, splits its files across the mount and local. Check both.

## Preferences (summary)
- Identify the persistent mount first. Keep HOME as is. Relocate through env vars.
- One env file, non-interactive-safe, sourced by both the shell rc and job scripts.
- Flat role-named workspace dirs, a `_home` suffix for tool homes, one `devtools` dir, all exported as shortcuts.
- Persist config, data, and state on the mount. Cache stays local.
- Retire replaced dirs with a reversible top-level `.premigrate`.
- tmux with mouse on, resurrect and continuum, and prefer an OSC 52 terminal.
- Write docs without em-dashes or semicolons, per my writing-style skill.
