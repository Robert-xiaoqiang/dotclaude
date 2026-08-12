#!/usr/bin/env bash
# ============================================================================
# with-root.sh ROOT -- COMMAND [ARGS...]
#
# Run COMMAND in an environment rooted at ROOT, with every prefix-bearing
# variable of the OLD root scrubbed first.
#
# WHY THIS EXISTS, and it is not paranoia. During the cpfs -> data migration a
# build script was invoked as
#
#     CPFS_HOME=/mnt/data/xqwang bash .../create_env.sh
#
# and it built into /mnt/cpfs/xqwang/uv_home/venvs anyway, silently, because the
# script sources env.sh and env.sh line 149 is
#
#     export UV_HOME="${UV_HOME:-$CPFS_HOME/uv_home}"
#
# The calling shell already had UV_HOME set to the OLD root, so the :- default
# never fired and the explicit CPFS_HOME was ignored for that one variable. That
# override is deliberate and correct (it is what makes a half-migrated root
# usable), but it means CPFS_HOME alone is NOT sufficient to retarget a process:
# the override outranks it by design. Anything that must land on a specific root
# has to arrive with the old root's variables REMOVED, not merely overridden.
#
# The same trap applies to PATH: a stale devtools prefix earlier in PATH wins
# over the one env.sh prepends later only in the reverse case, but a bare `uv`
# or `python` resolving to the old root's copy is the same class of bug, so PATH
# is rebuilt from scratch here rather than filtered.
#
# usage:
#   with-root.sh /mnt/data/xqwang -- bash projects/Foo/install.sh
#   with-root.sh /mnt/data/xqwang -- uv pip list
#   with-root.sh /mnt/data/xqwang --source -- <cmd>   # also source ROOT/env.sh
#
# Without --source it only scrubs and exports the root; the command may source
# env.sh itself (most install scripts do). With --source it sources env.sh for
# commands that expect a fully derived environment but do not source it.
# ============================================================================
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: $0 ROOT [--source] -- COMMAND [ARGS...]" >&2; exit 2; }
ROOT="$1"; shift
SOURCE_ENV=0
[ "${1:-}" = "--source" ] && { SOURCE_ENV=1; shift; }
[ "${1:-}" = "--" ] && shift
[ $# -ge 1 ] || { echo "$0: no command given" >&2; exit 2; }
[ -d "$ROOT" ] || { echo "$0: no such root: $ROOT" >&2; exit 1; }
[ -f "$ROOT/env.sh" ] || { echo "$0: no env.sh under $ROOT" >&2; exit 1; }

# Every variable env.sh exports that carries a prefix. Scrubbed rather than
# overwritten, so env.sh re-derives each one from the ROOT we hand it. UV_HOME is
# the only one with a :- default, which is exactly why it is the dangerous one,
# but the rest are listed too: an unconditional export is only safe while it
# STAYS unconditional, and this list should not need editing when one changes.
SCRUB=(
  CPFS_HOME PERSIST_HOME DEVTOOLS_HOME
  PROJECTS_HOME DATASETS_HOME DOWNLOADS_HOME OUTPUT_DIR_HOME
  XDG_CONFIG_HOME XDG_DATA_HOME XDG_STATE_HOME
  GIT_CONFIG_GLOBAL DLC_CONFIG_DIR DLC_CONFIG
  CLAUDE_CONFIG_DIR CODEX_HOME QODER_CONFIG_DIR
  HF_HOME TEXLIVE_HOME TRITON_HOME WANDB_DIR NLTK_DATA HISTFILE
  UV_HOME UV_VENVS_DIR UV_CACHE_DIR UV_PYTHON_INSTALL_DIR UV_TOOL_DIR UV_TOOL_BIN_DIR
  NPM_CONFIG_CACHE RUSCARL_ROOT
)

# A PATH built from scratch, so no old-root devtools entry can shadow the new
# one. env.sh prepends the ROOT's own toolchains when it is sourced.
BASE_PATH="/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

args=()
for v in "${SCRUB[@]}"; do args+=(-u "$v"); done

if [ "$SOURCE_ENV" = 1 ]; then
    exec env "${args[@]}" CPFS_HOME="$ROOT" PATH="$ROOT/devtools/uv:$ROOT/devtools/node/bin:$BASE_PATH" \
        bash -c 'set -a; . "$CPFS_HOME/env.sh" >/dev/null 2>&1; set +a; exec "$@"' _ "$@"
else
    exec env "${args[@]}" CPFS_HOME="$ROOT" PATH="$ROOT/devtools/uv:$ROOT/devtools/node/bin:$BASE_PATH" "$@"
fi
