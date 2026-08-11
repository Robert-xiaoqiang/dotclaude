#!/usr/bin/env bash
# ============================================================================
# migrate-claude-state.sh
# Relocate Claude Code STATE from volatile /root onto persistent CPFS, so a
# fresh DSW instance resumes sessions / plugins / login with zero reconfig.
#
#   FROM : /root/.claude   +   /root/.claude.json      (lost when instance dies)
#   TO   : $CPFS_HOME/.claude   (== $CLAUDE_CONFIG_DIR, persistent)
#
# Design / safety
#   * NON-DESTRUCTIVE: only ever writes to the destination + env.sh. /root is
#     never modified, so you can re-run freely and retire the old copy yourself
#     once the new one is verified.
#   * IDEMPOTENT: re-running just re-syncs; the env.sh edit is grep-guarded.
#   * --dry-run prints every action and changes nothing.
#
# Verified findings this script encodes (2026-07-07, claude 2.1.201):
#   - Every project key is already a CPFS cwd  => --resume stays valid; no
#     transcript re-keying needed.
#   - ~/.claude.json contains ZERO functional /root paths.
#   - The ONLY functional pointer to rewrite is:
#         plugins/known_marketplaces.json  ->  "installLocation"
#   - /root strings inside projects/*.jsonl and memory/*.md are historical
#     LOG/DOC data (tool outputs + notes) that Claude replays as text and never
#     resolves => copied VERBATIM (rewriting them would corrupt history).
#   - shell-snapshots/* are per-session, regenerated, and carry a stale
#     /root/.local/bin/claude fallback => EXCLUDED from the copy.
#   - In marketplace.json "/root" == the vendor name "Rootly"; in
#     security-guidance/hooks/llm.py it's upstream fallback code => untouched.
# ============================================================================
set -euo pipefail

# ---- config (override via flags / env) -------------------------------------
[ -z "${CPFS_HOME:-}" ] && echo "migrate-claude-state.sh: CPFS_HOME not set, defaulting to /mnt/cpfs/xqwang" >&2
CPFS_HOME="${CPFS_HOME:-/mnt/cpfs/xqwang}"
SRC_DIR="/root/.claude"
SRC_JSON="/root/.claude.json"
DST_DIR="$CPFS_HOME/.claude"
ENV_SH="$CPFS_HOME/env.sh"

DRY_RUN=0; FORCE=0; PATCH_ENV=1; RETIRE=0

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]
  --dst DIR        destination config dir (default: $DST_DIR)
  --dry-run        show what would happen; change nothing
  --force          skip the running-claude check and the confirm prompt
  --no-patch-env   do NOT add CLAUDE_CONFIG_DIR to $ENV_SH
  --retire         AFTER verifying: move /root/.claude(.json) -> *.premigrate
  -h, --help       this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dst)          DST_DIR="$2"; shift 2;;
    --dry-run)      DRY_RUN=1; shift;;
    --force)        FORCE=1; shift;;
    --no-patch-env) PATCH_ENV=0; shift;;
    --retire)       RETIRE=1; shift;;
    -h|--help)      usage; exit 0;;
    *) echo "unknown option: $1" >&2; usage; exit 2;;
  esac
done

say() { printf '\033[1m==>\033[0m %s\n' "$*"; }
log() { printf '    %s\n' "$*"; }
die() { printf '\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[[ "$DST_DIR" != "$SRC_DIR" ]] || die "destination equals source ($SRC_DIR)"

# ---- preflight -------------------------------------------------------------
say "Preflight"
[[ -d "$SRC_DIR" ]]            || die "source dir not found: $SRC_DIR"
command -v python3 >/dev/null  || die "python3 not found"
if command -v rsync >/dev/null 2>&1; then COPY=rsync; else COPY=cp; fi
mkdir -p "$(dirname "$DST_DIR")"
[[ -w "$(dirname "$DST_DIR")" ]] || die "not writable: $(dirname "$DST_DIR")"
log "source : $SRC_DIR  ($(du -sh "$SRC_DIR" 2>/dev/null | cut -f1))"
log "json   : $SRC_JSON  ($([[ -f "$SRC_JSON" ]] && du -sh "$SRC_JSON" | cut -f1 || echo missing))"
log "dest   : $DST_DIR"
log "copy   : $COPY$([[ $COPY == cp ]] && echo '  (rsync absent — cp+prune fallback)')"
log "flags  : dry-run=$DRY_RUN  patch-env=$PATCH_ENV  force=$FORCE  retire=$RETIRE"

# ---- running-claude guard --------------------------------------------------
if (( ! FORCE )); then
  if pgrep -af 'claude-code/(lib|bin)|@anthropic-ai/claude-code' >/dev/null 2>&1; then
    echo
    echo "A Claude Code process appears to be RUNNING."
    echo "Exit every Claude session first (including any you are chatting in), so the"
    echo "final transcript is flushed to $SRC_DIR before it is copied. Then re-run."
    echo "Tip: run this from a plain SSH shell, not from inside a Claude bash tool."
    echo "(Override with --force.)"
    exit 1
  fi
fi

# ---- confirm ---------------------------------------------------------------
if (( ! FORCE && ! DRY_RUN )); then
  read -r -p "$(printf '\033[1m?\033[0m Copy state -> %s and patch env.sh? [y/N] ' "$DST_DIR")" ans
  [[ "$ans" == [yY]* ]] || die "aborted by user"
fi

RS_DRY=(); (( DRY_RUN )) && RS_DRY=(--dry-run)

# ---- 1) copy the state dir (excluding regenerated ephemera) ----------------
say "1/4  Copy $SRC_DIR -> $DST_DIR   (via $COPY)"
EXCLUDES=(shell-snapshots paste-cache .last-cleanup .last-update-result.json mcp-needs-auth-cache.json)
if [[ "$COPY" == rsync ]]; then
  (( DRY_RUN )) || mkdir -p "$DST_DIR"
  rsync -a "${RS_DRY[@]}" "${EXCLUDES[@]/#/--exclude=}" "$SRC_DIR"/ "$DST_DIR"/
elif (( DRY_RUN )); then
  log "DRY  cp -a $SRC_DIR/. $DST_DIR/   then prune: ${EXCLUDES[*]}"
else
  mkdir -p "$DST_DIR"
  cp -a "$SRC_DIR"/. "$DST_DIR"/
  for e in "${EXCLUDES[@]}"; do rm -rf "${DST_DIR:?}/$e"; done
fi
log "excluded (regenerated): ${EXCLUDES[*]}"

# ---- 2) copy the global config json INTO the config dir --------------------
say "2/4  Copy global config -> $DST_DIR/.claude.json"
if [[ -f "$SRC_JSON" ]]; then
  if (( DRY_RUN )); then log "DRY cp $SRC_JSON -> $DST_DIR/.claude.json"
  else cp -a "$SRC_JSON" "$DST_DIR/.claude.json"; log "copied"; fi
else
  log "no $SRC_JSON — skipped"
fi

# ---- 3) rewrite the ONE functional pointer (plugin installLocation) --------
say "3/4  Fix functional path pointers"
if (( DRY_RUN )); then
  log "DRY would rewrite installLocation ($SRC_DIR -> $DST_DIR) in plugins/known_marketplaces.json"
else
  python3 - "$SRC_DIR" "$DST_DIR" <<'PY'
import json, os, sys
src, dst = sys.argv[1], sys.argv[2]
f = os.path.join(dst, "plugins", "known_marketplaces.json")
if not os.path.exists(f):
    print("    no known_marketplaces.json — nothing to rewrite"); raise SystemExit
data = json.load(open(f))
changed = 0
for _name, mp in (data.items() if isinstance(data, dict) else []):
    if isinstance(mp, dict):
        for k in ("installLocation", "path", "location"):
            v = mp.get(k)
            if isinstance(v, str) and v.startswith(src):
                mp[k] = dst + v[len(src):]; changed += 1
if changed:
    json.dump(data, open(f, "w"), indent=2)
    print(f"    rewrote {changed} path(s) in known_marketplaces.json -> {dst}")
else:
    print("    no rewrite needed (already points at destination)")
PY
fi
log "transcripts + memory/*.md left VERBATIM (historical logs, never resolved on resume)"

# ---- 4) permissions --------------------------------------------------------
say "4/4  Tighten permissions"
if (( DRY_RUN )); then
  log "DRY chmod 700 $DST_DIR ; chmod 600 .claude.json / .credentials.json / backups/*"
else
  chmod 700 "$DST_DIR"
  chmod 600 "$DST_DIR/.claude.json" "$DST_DIR/.credentials.json" 2>/dev/null || true
  [[ -d "$DST_DIR/backups" ]] && chmod 600 "$DST_DIR"/backups/* 2>/dev/null || true
  log "config dir 700; token/config files 600"
fi

# ---- env.sh patch ----------------------------------------------------------
if (( PATCH_ENV )); then
  say "env.sh  ($ENV_SH)"
  if grep -q 'CLAUDE_CONFIG_DIR' "$ENV_SH" 2>/dev/null; then
    log "already sets CLAUDE_CONFIG_DIR — left unchanged"
  elif (( DRY_RUN )); then
    log 'DRY would append: export CLAUDE_CONFIG_DIR="$CPFS_HOME/.claude"'
  elif [[ -f "$ENV_SH" ]]; then
    cp -a "$ENV_SH" "$ENV_SH.bak.$(date +%Y%m%d-%H%M%S)"
    cat >> "$ENV_SH" <<'EOF'

# ---- Claude Code STATE/config dir (persistent) -----------------------------
# Sessions, projects/--resume, plugins, credentials, MCP. This is the *state*
# dir (equivalent of ~/.claude); CLAUDE_CODE_HOME above is the *install* dir.
export CLAUDE_CONFIG_DIR="$CPFS_HOME/.claude"
mkdir -p "$CLAUDE_CONFIG_DIR"
EOF
    log "appended CLAUDE_CONFIG_DIR (backup saved next to env.sh)"
  else
    log "WARN: $ENV_SH not found — add 'export CLAUDE_CONFIG_DIR=\"$DST_DIR\"' to your shell init yourself"
  fi
fi

# ---- optional retire -------------------------------------------------------
if (( RETIRE )); then
  say "Retire old /root copies (use ONLY after verifying the new location)"
  if (( DRY_RUN )); then
    log "DRY mv $SRC_DIR -> $SRC_DIR.premigrate ; mv $SRC_JSON -> $SRC_JSON.premigrate"
  else
    for p in "$SRC_DIR" "$SRC_JSON"; do
      [[ -e "$p" ]] || continue
      tgt="$p.premigrate"; [[ -e "$tgt" ]] && tgt="$tgt.$(date +%Y%m%d-%H%M%S)"
      mv "$p" "$tgt"; log "moved $p -> $tgt"
    done
  fi
fi

# ---- report ----------------------------------------------------------------
cat <<REPORT

$(printf '\033[1m✔ done%s\033[0m' "$( ((DRY_RUN)) && echo ' (dry-run — nothing changed)' )")

Next steps:
  1) Load the new location (new shell, or: source $ENV_SH):
        echo "\$CLAUDE_CONFIG_DIR"        # -> $DST_DIR
  2) Relaunch from the SAME project dir and verify:
        cd /mnt/cpfs/xqwang/projects/QDiffLM/QDiffMDM
        claude --resume                   # your sessions should be listed
        # inside: account still logged in, /mcp servers, /plugin marketplace present
  3) Only AFTER it checks out, retire the volatile copy:
        mv /root/.claude       /root/.claude.premigrate
        mv /root/.claude.json  /root/.claude.json.premigrate
     (or re-run:  $(basename "$0") --retire --force)

Note: memory notes under projects/*/memory/ are copied verbatim; dsw-env-setup.md
still documents the old /root layout — review at leisure, not required for function.
REPORT
