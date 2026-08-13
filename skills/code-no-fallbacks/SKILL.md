# Skill: code-no-fallbacks

## Purpose
A required input has exactly **three** legitimate sources: the environment the workflow
established, an argument the caller passed, or a field the job config declared. If none of
them supplied it, the invocation chain is broken — and the only correct response is to say so
and stop. A default in that position does not rescue the run; it **hides the break and
produces a plausible wrong answer**, usually somewhere far from the missing variable.

This is the difference between a value that is *absent* (a bug in the chain) and a value that
is *unspecified* (a knob the caller chose not to turn). Defaults are correct for the second
and catastrophic for the first.

## When to Use
- Writing or reviewing any launcher, entrypoint, install script, or job wrapper.
- Reaching for `${VAR:-...}`, `os.environ.get(VAR, default)`, or a default parameter value.
- A run "worked" but wrote to the wrong place, used the wrong venv, or trained on the wrong data.
- Auditing a chain after a migration, a rename, or a platform change.

## The rule

**Required inputs fail loudly. Optional inputs may default. Nothing in between.**

An input is **required** when the chain is supposed to supply it and no value is more correct
than any other: roots and prefixes (`CPFS_HOME`, `OUTPUT_DIR_HOME`, `PROJECTS_HOME`,
`DATASETS_HOME`, `UV_VENVS_DIR`), service addresses the job must reach, identities of the
thing being run. **Guess these and the run silently relocates.**

An input is **optional** when the code legitimately owns a value and offers an override: the
project's own venv name, a pinned toolchain version, a mirror endpoint, a log verbosity. Here
a default is documentation, not a guess.

The test is one question: **if this is missing, is that a bug?** If yes, it is required.

## The idioms

Shell — one character, and the message names the fix, not the symptom:

```sh
# WRONG: silently relocates the entire run
BASE="${CPFS_HOME:-/mnt/cpfs/xqwang}/devtools"

# RIGHT: names the variable, says where it should have come from, exits non-zero
BASE="${CPFS_HOME:?required: set by env.sh, the instance env, or the job envs}/devtools"
```

Python — the mapping form already raises; only `.get()` invents:

```python
root = os.environ.get("OUTPUT_DIR_HOME", os.path.expanduser("~"))  # WRONG
root = os.environ["OUTPUT_DIR_HOME"]                               # RIGHT
```

Default *parameters* follow the same rule. `def run(cfg, venv=None)` where `None` then means
"go find one" is a fallback wearing a signature. Make it positional and let the call fail.

## Two failures this actually caused

Both looked like working code, and both were found only by auditing, never by a test.

- `${CPFS_HOME:-/mnt/cpfs/xqwang}` — the default named a root that had been **retired**. With
  the variable set it worked; the day anything dropped it, the script pointed at a deleted
  tree and reported a missing file rather than a missing prefix.
- `${OUTPUT_DIR_HOME:-$HOME/output_dir}` and
  `os.environ.get("OUTPUT_DIR_HOME", os.path.expanduser("~"))` — `$HOME` on a
  container-backed box is the **volatile overlay**. Runs wrote checkpoints to a directory that
  vanished at the next pod restart, having reported success.

Note the shape both share: **the fallback is only reachable when something upstream is already
broken, and it converts a loud failure into a silent one.** That is the whole argument.

## When you remove them in bulk

Three traps, each of which cost a real repair:

1. **A default can be nested.** `${VENV_NAME:-${PROJECT_VENV:-name}}` — a `[^}]*` regex stops
   at the *first* `}`, eats the inner expansion and leaves a stray brace. It still parses, and
   the variable silently gains a `}`. Match balanced braces, and grep for a trailing `}` after
   your replacement before committing.
2. **An apostrophe inside `${VAR:?...}` opens a quote context** and breaks parsing far below,
   often inside an unrelated heredoc. Write "the job envs", never "the job's envs". Run
   `bash -n` over every touched file — this is caught in seconds and is invisible by eye.
3. **`VAR="${VAR:-x}"` is usually a declaration, not a fallback.** The script is naming its own
   default and offering an override. Converting those to `:?` makes the script demand a value
   nobody supplies. Self-assignment is the tell: check whether anything upstream actually sets
   it before requiring it.

After the sweep, verify the other half: **every variable you made required must actually be
exported by the chain.** List them against the env file and against what each launcher passes.
A required variable nobody supplies is the same outage, arriving sooner.

## Companions
`platform-run` (what a launcher may pass — names and overrides, never behaviour) ·
`layout-workspace` (config specifies, launcher selects) · `platform-migrate` (the audit that
surfaces stale defaults) · `conventions` (the map).
