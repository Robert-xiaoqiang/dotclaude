#!/usr/bin/env bash
# grid-runner — drain the grid queue: one template launcher, one --set overlay per cell.
#
# Env (all required, per code-no-fallbacks):
#   GRID_QUEUE       queue file (launcher<TAB>checkpoint)
#   GRID_LEDGER      submitted ledger this runner APPENDS to (launcher, ckpt, jobid)
#   GRID_SUBMIT_CMD  hook: receives <launcher> <checkpoint>, submits ONE job with the overlay
#                    (e.g. make job LAUNCHER=$1 SET_ARGS="model.init_kwargs.path=$2"), prints the
#                    job id on success, nothing on failure
#   GRID_BUDGET_CMD  hook: exit 0 to admit one more submission (judge capacity, concurrency cap)
#
# Rows are MOVED to the ledger at submit, never deleted: the ledger is what stops a scheduled
# enqueuer re-adding submitted cells, and it carries the job id the reconciler checks.
set -uo pipefail
: "${GRID_QUEUE:?required}"; : "${GRID_LEDGER:?required}"
: "${GRID_SUBMIT_CMD:?required: hook printing a job id}"; : "${GRID_BUDGET_CMD:?required: admission hook}"
while true; do
  line=$(head -1 "$GRID_QUEUE" 2>/dev/null)
  if [ -n "$line" ] && bash -c "$GRID_BUDGET_CMD" >/dev/null 2>&1; then
    L=$(printf '%s' "$line" | cut -f1); CK=$(printf '%s' "$line" | cut -f2)
    jid=$(bash -c "$GRID_SUBMIT_CMD \"\$@\"" _ "$L" "$CK" 2>&1 | grep -oE '[A-Za-z0-9_-]{8,}' | tail -1)
    if [ -n "$jid" ]; then
      printf '%s\t%s\t%s\n' "$L" "$CK" "$jid" >> "$GRID_LEDGER"
      sed -i '1d' "$GRID_QUEUE"
      echo "$(date -u +%H:%M:%SZ) submitted $(basename "$CK") -> $jid"
    else
      echo "$(date -u +%H:%M:%SZ) submit failed for $CK; retrying next cycle"
    fi
  fi
  sleep "${GRID_TICK_SECS:-180}"
done
