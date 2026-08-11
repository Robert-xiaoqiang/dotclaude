#!/usr/bin/env bash
# ============================================================================
# migrate-cpfs-home.sh
# Move a persistent home ($CPFS_HOME) to another mount, and tell you honestly
# what is worth moving before you spend hours on it.
#
#   audit      classify every top-level entry, with size, file count and a
#              measured time estimate. Changes nothing.
#   migrate    rsync the MUST + SHOULD tiers to the destination.
#   reinstall  print the commands that rebuild the SKIP tier on the far side.
#
# WHY A TIER LIST AND NOT "COPY $CPFS_HOME"
#   env.sh's _pdir list is a list of paths to EXPORT, not a backup manifest. It
#   names caches and installed toolchains because they must exist, not because
#   they are precious. Measured here: ~2.4T across ~1.1M files, of which the four
#   costliest entries are all reconstructible, and one of them (uv_home) arrives
#   BROKEN because a venv hardcodes its interpreter path in pyvenv.cfg.
#
# WHY FILE COUNT AND NOT SIZE DRIVES THE ESTIMATE
#   Benchmarked CPFS -> NFS on this platform: 412 MB/s for large files, but only
#   126 files/s for small ones. Per-file round-trip dominates by ~3300x, so a
#   directory's FILE COUNT predicts its transfer time far better than its size.
#   uv_home is 54G but 711k files: ~1.6h, longer than the 239G hf_home.
#
# SAFETY
#   * READ-ONLY at the source. Never deletes, never modifies $CPFS_HOME.
#   * rsync, not cp: resumable, verifiable, and re-runnable to catch up a live
#     source. Re-running is the intended way to finish a migration.
#   * --dry-run on `migrate` passes through to rsync's own dry run.
# ============================================================================
set -uo pipefail

SRC="${CPFS_HOME:-/mnt/cpfs/xqwang}"
DST="${MIGRATE_DST:-/mnt/data/xqwang}"
DRY=0

# ---- the tiers -------------------------------------------------------------
# MUST: irreplaceable. Nothing regenerates these; losing them loses work.
#   env.sh and home.sh are tracked in the dotfile repo, so strictly a clone would
#   bring them back, but they stay here because they are the bootstrap: sourcing
#   env.sh is step one of the far-side recipe, and needing them before a clone is
#   possible is exactly when "recoverable from the remote" is worth nothing.
MUST=(output_dir .claude .ssh.persistent .secret env.sh home.sh)
# SHOULD: cheap to copy and annoying to rebuild, but not irreplaceable.
#   projects/ is in git, but copying preserves uncommitted work and remotes.
#
#   The four repo-metadata entries are here for that identical reason, and NOT in
#   MUST, which is where they were first put by mistake. $CPFS_HOME is itself a git
#   checkout, and .gitignore, .gitmodules and README.md are all TRACKED, so a clone
#   reproduces them byte for byte: nothing about them is irreplaceable. They are
#   copied anyway because .git here is under half a megabyte across 57 files, which
#   is free at any transfer rate, and copying preserves uncommitted edits and the
#   remote wiring rather than resetting to whatever was last pushed.
#
#   The hazard is in the path where they are NOT copied, and it is worth knowing
#   before choosing it. `git clone` refuses a populated directory, so recovery means
#   cloning --no-checkout elsewhere and moving .git in on top of the existing tree.
#   In the window between that move and restoring .gitignore, the repository root
#   presents .secret, the ssh private key and .bash_history as ordinary untracked
#   files, because that file is a deny-all allow-list and it is the only thing
#   standing between them and a `git add -A`. So restore .gitignore FIRST, before
#   touching the index at all.
SHOULD=(projects datasets .config .local snippets .bash_history .codex .qoder
        .git .gitignore .gitmodules README.md)
# SKIP: reconstructible, or actively wrong to copy. Reason given per entry.
SKIP_uv_home="711k files (~1.6h) AND arrives broken: pyvenv.cfg hardcodes the
              interpreter path, so every venv points at the OLD prefix. Rebuild
              from each project's install.sh instead."
SKIP_devtools="194k files (~26min) of installed toolchains (node, uv, claude,
              texlive). Reinstalled by the same commands that created them."
SKIP_hf_home="239G re-downloadable model cache. Re-fetches on first use."
SKIP_wandb_local="local run cache; the runs themselves are on wandb.ai."
SKIP_triton_home="JIT kernel cache, regenerates on first compile."
SKIP_nltk_data="re-downloadable corpora (nltk.download)."
SKIP_trash="pod-lifetime scratch; self-empties on relaunch."
SKIP=(uv_home devtools hf_home wandb_local triton_home nltk_data .trash)

# measured on this platform; override if the destination differs
RATE_FILES="${RATE_FILES:-126}"      # files/s, small-file regime
RATE_MB="${RATE_MB:-412}"            # MB/s, large-file regime

say()  { printf '%s\n' "$*"; }
info() { printf '  %s\n' "$*"; }
warn() { printf 'migrate: %s\n' "$*" >&2; }

# Time is whichever regime dominates: per-file cost vs raw bandwidth.
est_seconds() {
    local files="$1" mib="$2"
    python3 -c "
f, m = $files, $mib
print(int(max(f/$RATE_FILES, m/$RATE_MB)))" 2>/dev/null || echo 0
}

human_time() {
    python3 -c "
s = $1
print(f'{s/3600:.1f}h' if s >= 3600 else (f'{s/60:.0f}m' if s >= 60 else f'{s}s'))" 2>/dev/null
}

measure() {   # dir -> "files<TAB>MiB"
    local d="$SRC/$1"
    [ -e "$d" ] || { printf '0\t0\n'; return; }
    local f m
    f="$(find "$d" -type f 2>/dev/null | wc -l)"
    m="$(du -sm "$d" 2>/dev/null | cut -f1)"
    printf '%s\t%s\n' "${f:-0}" "${m:-0}"
}

cmd_audit() {
    say "source      $SRC"
    say "destination $DST"
    say "rates       ${RATE_FILES} files/s (small), ${RATE_MB} MB/s (large)"
    say ""
    printf '%-11s %-18s %10s %12s %9s\n' TIER ENTRY SIZE FILES EST
    printf '%s\n' "------------------------------------------------------------------"
    local tf=0 tm=0 tier name fm f m s
    for tier in MUST SHOULD SKIP; do
        eval "local list=(\"\${${tier}[@]}\")"
        for name in "${list[@]}"; do
            [ -e "$SRC/$name" ] || continue
            fm="$(measure "$name")"; f="${fm%%$'\t'*}"; m="${fm##*$'\t'}"
            s="$(est_seconds "$f" "$m")"
            printf '%-11s %-18s %10s %12s %9s\n' \
                "$tier" "$name" "$(numfmt --to=iec $((m*1024*1024)) 2>/dev/null || echo "${m}M")" \
                "$(printf "%'d" "$f" 2>/dev/null || echo "$f")" "$(human_time "$s")"
            if [ "$tier" != SKIP ]; then tf=$((tf+f)); tm=$((tm+m)); fi
        done
    done
    printf '%s\n' "------------------------------------------------------------------"
    printf '%-11s %-18s %10s %12s %9s\n' "TO COPY" "(MUST+SHOULD)" \
        "$(numfmt --to=iec $((tm*1024*1024)) 2>/dev/null || echo "${tm}M")" \
        "$(printf "%'d" "$tf" 2>/dev/null || echo "$tf")" \
        "$(human_time "$(est_seconds "$tf" "$tm")")"
    say ""
    say "SKIP tier, and why:"
    local key
    for name in "${SKIP[@]}"; do
        [ -e "$SRC/$name" ] || continue
        key="SKIP_${name#.}"; key="${key//./_}"
        info "$name: $(eval "printf '%s' \"\${$key:-reconstructible}\"" | tr -s ' \n' ' ')"
    done
}

cmd_migrate() {
    command -v rsync >/dev/null || { warn "rsync not found"; return 1; }
    local args=(-a --info=progress2 --human-readable --partial)
    [ "$DRY" = 1 ] && args+=(--dry-run)
    mkdir -p "$DST"
    local name
    for name in "${MUST[@]}" "${SHOULD[@]}"; do
        [ -e "$SRC/$name" ] || continue
        say ""
        say "-> $name"
        # No trailing slash on the source: copies the entry itself INTO $DST,
        # so a file and a directory behave the same way.
        rsync "${args[@]}" "$SRC/$name" "$DST/" || warn "$name: rsync exited $?"
    done
    say ""
    say "done. Re-run to catch up anything that changed while copying."
    say "Then run: $0 reinstall"
}

cmd_reinstall() {
    cat <<EOF
# Rebuild the SKIP tier on the destination. Run these ON the new box, after
# setting CPFS_HOME to the new prefix and sourcing its env.sh.

export CPFS_HOME=$DST
. "\$CPFS_HOME/env.sh"

# --- nc, FIRST, because git over ssh is dead without it ---------------------
# The ssh ProxyCommand names \$DEVTOOLS_HOME/bin/nc by absolute path, and devtools/ is
# a SKIP tier, so on the far side that binary does not exist and every git push fails
# in a way that reads like a rejected key rather than a missing tunnel.
#
# This looks circular and is not: the clone needs ssh, ssh needs nc, nc needs the
# network, the network needs the proxy. The archive is reachable DIRECTLY, so apt
# needs neither the proxy nor git, and that is where the circle breaks. The proxy
# variables are unset explicitly because env.sh has already exported them and would
# otherwise send apt through a tunnel that is not up yet.
mkdir -p "\$DEVTOOLS_HOME/bin" && cd /tmp \\
  && env -u http_proxy -u https_proxy -u all_proxy \\
       -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY apt-get download netcat-openbsd \\
  && dpkg-deb -x netcat-openbsd*.deb x \\
  && install -m 755 x/bin/nc.openbsd "\$DEVTOOLS_HOME/bin/nc"

bash "\$CPFS_HOME/home.sh" --boot     # bashrc hook, ssh keys, git hooks

# --- node, ONLY because the agent needs npm --------------------------------
# devtools/ is skipped wholesale, and node lives inside it, so there is no npm
# on a fresh box at all. This one piece has to come back before anything else.
# Adjust the version/arch to taste; any recent LTS works.
mkdir -p "\$DEVTOOLS_HOME"
curl -fsSL https://nodejs.org/dist/v22.11.0/node-v22.11.0-linux-x64.tar.xz \\
  | tar -xJ -C "\$DEVTOOLS_HOME" && mv "\$DEVTOOLS_HOME/node-v22.11.0-linux-x64" "\$DEVTOOLS_HOME/node"
export PATH="\$DEVTOOLS_HOME/node/bin:\$PATH"

# --- then the agent, before anything else ----------------------------------
# Everything below is easier to rebuild with the agent present than without it:
# the commands, the skills describing them, and the judgement about what broke
# all arrive together. \$CLAUDE_CONFIG_DIR already points at the copied .claude,
# so sessions, skills and plugins are there the moment it starts.
npm install -g --prefix "\$DEVTOOLS_HOME/claude-code" @anthropic-ai/claude-code@latest

# --- then the package manager everything else installs through --------------
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="\$DEVTOOLS_HOME/uv" sh

# --- venvs: one per project, from each project's own installer -------------
# uv_home is NOT copied: a venv hardcodes its interpreter in pyvenv.cfg, so a
# copied one points at the old prefix and is broken on arrival.
uv python install 3.11 && uv python install 3.12   # into \$UV_PYTHON_INSTALL_DIR
bash "\$PROJECTS_HOME/QDiffLM/QDiffMDM/install.sh"
bash "\$PROJECTS_HOME/LatentHarness/LatentHarness/install.sh"
bash "\$PROJECTS_HOME/MemPalace/MemCodex/install.sh"
# AutoRSI has no install.sh; build from its pyproject:
#   uv venv --python 3.11 "\$UV_VENVS_DIR/autorsi_trl" && uv pip install -e ...
# skylaunch control plane (pure python, needed by every make job/run):
uv venv --python 3.12 "\$UV_VENVS_DIR/skylaunch"
uv pip install --python "\$UV_VENVS_DIR/skylaunch/bin/python" -e "\$PROJECTS_HOME/skylaunch"

# --- the proxy: binary, credentials, then start ----------------------------
# .config/ IS copied, so acl.conf and server.conf survive and the proxy comes back
# with no editing. On a box that did NOT inherit them, server.conf is the one file
# no repo can carry, since it holds the SS password and the VLESS UUID:
#   install -m 600 "\$DEVTOOLS_HOME/sing-box/server.conf.template" \\
#                  "\$XDG_CONFIG_HOME/sing-box/server.conf"    # then fill it in
# The sing-box binary itself is a download from the upstream release page into
# \$DEVTOOLS_HOME/sing-box/sing-box, mode 755.
sbproxy start && sbproxy status

# --- TeX Live: scheme-full, ~45 min, no prompts -----------------------------
# instopt_adjustpath 0 because env.sh owns PATH, and docfiles off to halve the size.
# TEXDIR must match \$TEXLIVE_HOME or env.sh puts the wrong bin dir on PATH.
#   curl -sL https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar xz
#   ./install-tl-*/install-tl -profile <profile>

# --- caches: no action, they refill on demand ------------------------------
# hf_home, triton_home, nltk_data, wandb_local, .trash
EOF
}

case "${1:-audit}" in
    audit)     shift; cmd_audit ;;
    migrate)   shift; for a in "$@"; do [ "$a" = --dry-run ] && DRY=1; done; cmd_migrate ;;
    reinstall) shift; cmd_reinstall ;;
    -h|--help) sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//' ;;
    *)         warn "unknown command: $1 (try audit, migrate, reinstall)"; exit 2 ;;
esac
