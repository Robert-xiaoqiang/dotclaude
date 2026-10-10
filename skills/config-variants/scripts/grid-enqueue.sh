#!/usr/bin/env bash
# grid-enqueue — turn a trained run's checkpoint ladder into grid rows for ONE template launcher.
#
# Usage:  GRID_QUEUE=... GRID_LEDGER=... grid-enqueue.sh <launcher> <run_root>
#   <launcher>  the eval/sweep TEMPLATE launcher every cell shares
#   <run_root>  directory holding checkpoint-* dirs (the trained run dir, or a parent)
#
# Extracted from a working fleet (AutoRSI, 2026-08); the guards are its scar tissue:
#   PROVENANCE  a checkpoint with no config.yaml above it cannot say which run produced it, and a
#               row for it buys a job that dies on startup. Skipped, loudly.
#   ONE LADDER  several run roots under one arm = a config change moved the hash; a curve built
#               from two roots is two policies on one line. Refuse and name them.
#   DEDUP       against BOTH the queue and the submitted ledger — a runner that MOVES rows on
#               submit plus an enqueuer that only checks the queue re-adds every submitted cell
#               each pass and double-submits the grid (measured before the ledger existed).
# Idempotent: re-run on a schedule to feed new checkpoints as training saves them.
set -uo pipefail
: "${GRID_QUEUE:?required: queue file (launcher<TAB>checkpoint per row), on shared storage}"
: "${GRID_LEDGER:?required: submitted ledger (launcher<TAB>checkpoint<TAB>jobid), on shared storage}"
L="${1:?usage: grid-enqueue.sh <launcher> <run_root>}"; ROOT="${2:?run_root required}"
touch "$GRID_QUEUE" "$GRID_LEDGER"
_prov() { local d="$1"; for _ in 1 2 3 4 5 6 7 8; do d=$(dirname "$d"); [ -f "$d/config.yaml" ] && { echo "$d"; return 0; }; done; return 1; }
all=$(find "$ROOT" -maxdepth 9 -type d -name "checkpoint-*" ! -path "*/eval/*" ! -path "*/trajectory/*" 2>/dev/null)
roots=$(printf '%s\n' $all | while read -r c; do [ -n "$c" ] && _prov "$c"; done | sort -u | grep -c . || true)
if [ "${roots:-0}" -gt 1 ]; then
  echo "REFUSING: $ROOT holds checkpoints under $roots distinct run roots; a grid over two" >&2
  echo "roots is two policies on one curve. Narrow <run_root> to one of them." >&2
  exit 2
fi
n=0
printf '%s\n' $all | awk -F/ '!seen[$NF]++' | awk -F'checkpoint-' '{print $NF"\t"$0}' | sort -n | cut -f2 | while read -r ck; do
  [ -n "$ck" ] || continue
  _prov "$ck" >/dev/null || { echo "skip $(basename "$ck"): no config.yaml above it" >&2; continue; }
  grep -qFh "$ck" "$GRID_QUEUE" "$GRID_LEDGER" 2>/dev/null && continue
  printf '%s\t%s\n' "$L" "$ck" >> "$GRID_QUEUE"; echo "queued: $(basename "$ck")"
done
echo "queue length: $(wc -l < "$GRID_QUEUE")"
