#!/usr/bin/env bash
# grid-reconcile — self-healing for the grid: dead cells go back to the queue on their own.
#
# Env: GRID_QUEUE, GRID_LEDGER as in the runner, plus
#   GRID_STATUS_CMD  hook: receives <jobid>, prints Running|Queuing|Succeeded|Failed|Stopped|...
#
# Failed/Stopped rows return to the FRONT of the queue (their jobs died — a shared-workspace
# reclamation sweep or a transient failure); Succeeded rows stay in the ledger as the done-record;
# live rows stay put. Run from the same schedule as the enqueuer. An unreadable status holds the
# row — never requeue on ignorance, a live job resubmitted is a double-write.
set -uo pipefail
: "${GRID_QUEUE:?required}"; : "${GRID_LEDGER:?required}"; : "${GRID_STATUS_CMD:?required}"
[ -s "$GRID_LEDGER" ] || exit 0
: > "$GRID_LEDGER.next"; : > "$GRID_QUEUE.requeue"
while IFS=$'\t' read -r L CK JID; do
  st=$(bash -c "$GRID_STATUS_CMD \"\$@\"" _ "$JID" 2>/dev/null | head -1)
  case "$st" in
    Failed|Stopped) printf '%s\t%s\n' "$L" "$CK" >> "$GRID_QUEUE.requeue"
                    echo "requeue $(basename "$CK"): job $JID $st";;
    *)              printf '%s\t%s\t%s\n' "$L" "$CK" "$JID" >> "$GRID_LEDGER.next";;
  esac
done < "$GRID_LEDGER"
mv "$GRID_LEDGER.next" "$GRID_LEDGER"
if [ -s "$GRID_QUEUE.requeue" ]; then cat "$GRID_QUEUE" >> "$GRID_QUEUE.requeue" 2>/dev/null; mv "$GRID_QUEUE.requeue" "$GRID_QUEUE"; else rm -f "$GRID_QUEUE.requeue"; fi
