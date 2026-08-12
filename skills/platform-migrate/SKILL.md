# Skill: platform-migrate

## Purpose
Move a persistent home from one shared mount to another, decide **what is actually worth
moving**, and carry out the **cutover** — the half where migrations actually fail.
`platform-env` covers *landing* on a new environment; this covers *leaving* one.

Two claims, and the second is the expensive one. First, a naive "copy the persistent dir" is
almost always the wrong plan: it takes far longer than expected, and a meaningful fraction of
what it copies is either reconstructible or **broken on arrival**. Second, once the bytes are
in place the job is maybe half done — the remaining failures come from references that still
name the old root, and from a new root that is **mounted but not actually reachable by the
thing that matters**. A migration that passes every check on the interactive box can still
break every job.

## When to Use
- Migrating to a new cluster, a new storage backend, or a different mount on the same platform.
- Deciding whether some large directory is worth backing up at all.
- Estimating how long a bulk transfer will take, before committing to it.
- Someone proposes "just copy `$PERSISTENT_HOME`" and you need to say what that really costs.
- Jobs fail on a path that demonstrably exists on the shared storage.
- Retiring or deleting an old root, and deciding what must be true first.

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

## Copying is the easy half — the cutover is where migrations fail

Everything above is about moving bytes. Every expensive failure in practice came *after* the
bytes were in place, from something that still pointed at the old root or from a new root that
was not actually reachable. Budget for this half.

## A mount can be present and WRONG

The worst failure mode in the whole subject, because every check short of running real work
says the migration succeeded.

A shared filesystem is attached to a job through some platform object — a "data source",
"dataset", volume claim — and **that object can carry a version or a subpath that differs
from what an interactive box mounts.** One real case: the same data source id resolved to the
filer's *root* on the interactive box and to the filer's `/mnt` subdirectory inside batch
pods. The pods mounted it at the same path, so `/mnt/<user>` existed on the box and simply did
not exist in any job — the mount point held other tenants' home directories instead. Every job
died on its first `cd` with a path that was demonstrably present on the shared storage.

It hid for months because every pre-migration job rooted at the *old* mount, so nothing ever
read the new one. **A mount that nothing reads is indistinguishable from a working one.**

- Read the object's real definition, not its name: on PAI,
  `aliyun aiworkspace GetDataset --DatasetId <id> --region <r>` returns `ImportInfo` *and*
  `LatestVersion.ImportInfo`, and they can differ. The submit CLI defaults to the older
  version.
- The fix may be a version pin in the job spec (`<id>:v3`), not new infrastructure. Check
  before requesting a console change or building a replacement.
- Setting only a *mount path* does not help — it relocates the mount and keeps the wrong
  export. Verify by listing the mount source, not the mount point.

## Only a real job proves a mount

No check that runs on the interactive box can see a pod's view of storage, because the box has
its own mounts for the same filer. Path checks, `make check`, venv imports and config
resolution all pass while every job fails.

Prove a new root with a **job that reads code, executes the venv's interpreter, and writes a
file back** — cheap and conclusive. A CPU-only job (`gpu=0`) schedules in seconds and answers
mount questions without waiting for accelerators. Keep it as a committed check; it is the
cheapest insurance in the whole migration.

## An inline env prefix is not the pod's environment

`CPFS_HOME=/new bash boot.sh` sets the variable **for that one process**. It never joins the
container environment, so anything else that starts in the pod — a notebook server, an IDE
backend, a login shell racing the boot script — sees no prefix and falls back.

The symptom is oddly specific: **empty directory skeletons reappearing on the old root** after
a relaunch, holding only the layouts of tools that self-initialise (a package manager's cache
dirs, an agent's config dir) while every other path is correct. That is two tools bootstrapping
under a stale prefix, not a failed move.

Put the root in the platform's own environment field (DSW `EnvironmentVariables`) so it reaches
every process, and keep the inline prefix as belt-and-braces. Leave the empty skeleton deleted
rather than ignored: if it comes back, a stale prefix leaked again, which makes it a free
canary.

## Find what still LIVES on the old root

Job listings will not tell you. A long-lived interactive box accumulates processes rooted at
the old path that no scheduler knows about — in one cutover, a 2.5-day experiment, a 2-day
inference server, the proxy the box itself needs for outbound traffic, and a set of idle shells.

```sh
for p in /proc/[0-9]*; do readlink $p/cwd; readlink $p/exe; done | grep /old/root | sort -u
```

Check both `cwd` and `exe`, and check **the agent's own install**: if the tooling directory is
in the SKIP tier, the running agent may itself be executing from the root being retired.

Also: **paginated listings lie.** A CLI defaulting to ten rows let a six-day-old serving job go
unnoticed, and "it does not exist" was reported from a single page. Pass an explicit page size
and a status filter before concluding anything is absent.

## Retire by rename, not delete

`mv /root /root_purged_<timestamp>` on the same filesystem is instant, reversible for as long
as you leave it, and inode-preserving — running processes keep their open files and cwd. Its
real virtue is that every *stale* reference now fails loudly instead of silently reading a tree
that should be gone.

Delete only after the new root has carried real work for a few days. Record the retired path
somewhere the next session will find it.

## Order the cutover by dependency, not by convenience

Freeing capacity is not the same as reassigning it. Stopping a serving job to move it released
its accelerators to *queued trainers*, which then started against endpoints that no longer
answered. Bring the dependency up first, wait until it actually serves — poll the endpoint,
not the job status — and only then submit its consumers.

## A migration is the moment to fix data living in a source tree

Absolute paths get audited exactly once, so use it. One project's benchmark data sat inside a
sibling *source checkout* and was reached through an env var pointing at that checkout; the
repo also was not a git repo, so it could not be deleted safely either. Move such data to the
data root, repoint the configs, and the dead checkout becomes deletable.

While auditing, watch for **absolute paths inside a hashed run config**. If run-dir identity is
`md5(resolved_config)` and the config contains the root, the same experiment hashes differently
on each mount, and old and new results stop lining up by identity. Byte-identical inputs, new
identity — a design bug the move only reveals.

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
