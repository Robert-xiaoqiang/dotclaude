# Skill: platform-migrate

## Purpose
Move a persistent home from one shared mount to another, and decide **what is actually worth
moving** before spending hours on it. `platform-env` covers *landing* on a new environment;
this covers *leaving* one. The core claim is that a naive "copy the persistent dir" is almost
always the wrong plan: it takes far longer than expected, and a meaningful fraction of what it
copies is either reconstructible or **broken on arrival**.

## When to Use
- Migrating to a new cluster, a new storage backend, or a different mount on the same platform.
- Deciding whether some large directory is worth backing up at all.
- Estimating how long a bulk transfer will take, before committing to it.
- Someone proposes "just copy `$PERSISTENT_HOME`" and you need to say what that really costs.

## File count, not size, predicts transfer time
The single most useful thing to internalise. On network storage, per-file round-trip cost
dominates raw bandwidth by orders of magnitude. Measured on one PAI platform, CPFS to NFS:

| regime | rate |
|---|---|
| large files | 412 MB/s |
| small files | **126 files/s** |

That is a ~3300x per-byte difference, and it inverts the intuitive ordering. A 54G venv tree of
711k files took ~1.6h; a 239G model cache of 2k files took ~10min. **Always measure both**
`du -sm` and `find -type f | wc -l`, and estimate as `max(files/rate_files, mb/rate_mb)`.

Benchmark the destination rather than assuming these numbers. Two `dd`/`cp` runs, one large
file and one directory of ~500 small ones, take under a minute and make every later estimate
real instead of guessed.

## The three tiers
Classify every top-level entry before copying anything.

**MUST** — irreplaceable, nothing regenerates it. Run outputs and checkpoints, agent/session
history, ssh keys, secrets, and the env/bootstrap scripts themselves.

**SHOULD** — cheap to copy, annoying to rebuild. Source checkouts (git has them, but copying
preserves uncommitted work and remote wiring), datasets, XDG config/state, shell history.

**SKIP** — reconstructible, or actively wrong to copy. Every entry needs a stated reason, not
just an exclusion. Caches (model, JIT, corpora) refill on demand. Installed toolchains are
reinstalled by the commands that created them. Scratch and trash dirs are disposable.

## The trap: a venv is not portable
The one that turns a slow copy into a *broken* copy. A python venv hardcodes its interpreter
path in `pyvenv.cfg` (`home = ...`) and in the `bin/python` symlink. Copy it to a different
prefix and every one of those still points at the **old** path, so the venv is dead on arrival
while looking perfectly intact.

Venv trees are also usually the worst file-count offender in the whole home, so this is the
rare case where the expensive thing to copy is also the wrong thing to copy. Rebuild from each
project's installer instead. The same reasoning applies to anything embedding absolute paths:
compiled extensions, `.pth` files, tool configs written with a literal prefix.

## The manifest is not the env file
A tempting shortcut is to take the persistent-dir list straight from `env.sh`'s
export-and-mkdir calls. That list exists so paths get *created and exported*, and it
deliberately includes caches and toolchains because they must exist, not because they matter.
Reading it as a backup manifest copies every cache in the environment. The tiers are a
**separate, curated judgement**, and the exclusions are the valuable part.

## Use rsync, and re-run it
Not `cp`. `rsync -a --partial` is resumable, verifiable, and idempotent, which matters because
a multi-hour copy of a **live** source is guaranteed to be internally inconsistent. Re-running
after the bulk pass catches up whatever changed, and is the normal way to finish, not a
failure. Copy the source entry *without* a trailing slash so files and directories behave the
same way.

## Pair the migration with a reinstall script
A migration is only half a move. Everything in SKIP must be reconstructible **by a command you
have written down**, or it was not really reconstructible, it was just forgotten. Emit those
commands as part of the tool, so the far side is a script to run rather than a memory exercise.
Order matters: bootstrap env, then the package manager, then interpreters, then per-project
venvs, then control-plane tooling.

## The scripts
Both live in `scripts/` beside this file, deliberately. They were loose in a `snippets/` dir,
which gave a reader the *what* with none of the *when* or *why*: a migration script without its
rationale is a command you have to reverse-engineer before trusting. Skill and implementation
travel together, so one clone gets both.

`scripts/migrate-cpfs-home.sh` — the general tool. `audit` classifies, measures and estimates,
changing nothing. `migrate` rsyncs the MUST and SHOULD tiers. `reinstall` prints the far-side
rebuild commands. The tier lists are three arrays at the top, so retargeting it to a different
home is editing data, not logic.

`scripts/with-root.sh` — run a command rooted at a given prefix, with the *other* root's
variables scrubbed. Read the header before skipping it. Setting `CPFS_HOME` is **not**
sufficient to retarget anything that sources `env.sh`, because `env.sh` deliberately writes
`UV_HOME="${UV_HOME:-$CPFS_HOME/uv_home}"` — an override that exists so a half-migrated root
stays usable, and that therefore *outranks* the prefix. A shell on a half-migrated box always
has the old `UV_HOME` exported, so `CPFS_HOME=/new bash install.sh` builds into the **old**
root's venv tree, reports success, and warns about nothing. This cost a real venv during the
cpfs→data migration. Any build or install aimed at a specific root goes through this wrapper.

`scripts/migrate-claude-state.sh` — the narrower, earlier case: relocating Claude Code's own
state (sessions, plugins, login) off a volatile home onto the persistent mount, which is what
makes `--resume` survive a node dying. Worth reading before the general tool, because it is a
concrete instance of the same tier logic with one directory's specifics worked out, including
which files inside it are safe to rewrite and which must be copied verbatim.

## Bootstrap order on the far side
Install the agent FIRST. Everything else in the SKIP tier is easier to rebuild with the agent
present than without it, since the reinstall commands, the skills describing them, and the
judgement about what broke all arrive together. Concretely: env bootstrap, then the package
manager, then the agent CLI, then interpreters, then per-project venvs, then control-plane
tooling. `reinstall` emits them in that order.

## Companions
`platform-env` (landing on a new environment, the inverse of this) · `platform-runtime` (the
driver/image/venv stack a job needs) · `layout-output` (what in a run output tree is resume
state vs deliverable vs junk, which is how to decide whether a run dir must move in full) ·
`output-cleanup` (reclaiming space, the same classification applied to deletion).
