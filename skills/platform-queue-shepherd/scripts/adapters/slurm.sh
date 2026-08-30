# Adapter: Slurm. Included to prove the interface is not shaped around one scheduler.
#
# The engine's vocabulary maps onto Slurm without changing the decision table:
#   cluster  -> partition
#   launcher -> an sbatch script, resolved under $QS_PROJECT_HOME
#   empty nodes -> sinfo's idle count for that partition
#
# WHY IDLE NODES AND NOT IDLE CPUS. Same reason as every other platform: a whole-node job is
# seated by whole nodes. `sinfo -o %C` reports allocated/idle/other/total CPUs, and its idle
# figure counts cores scattered across partly-busy nodes that cannot seat anything exclusive.
# `-t idle -o %D` counts nodes with nothing on them, which is the number the decision needs.

: "${QS_PROJECT_HOME:?required: directory holding the sbatch scripts}"

qs_job_status() {  # <partition> <job_id>
    # squeue while pending or running, sacct once it has left the queue.
    local st
    st=$(squeue -h -j "$2" -o '%T' 2>/dev/null | head -1)
    [ -z "$st" ] && st=$(sacct -n -X -j "$2" -o State 2>/dev/null | head -1 | awk '{print $1}')
    case "${st:-}" in
        PENDING)                     echo Queuing ;;
        RUNNING|CONFIGURING)         echo Running ;;
        COMPLETED)                   echo Succeeded ;;
        CANCELLED*)                  echo Stopped ;;   # a human scancel is a decision
        FAILED|TIMEOUT|NODE_FAIL|OUT_OF_MEMORY) echo Failed ;;
        *)                           echo Unknown ;;
    esac
}

qs_empty_nodes() {  # <partition> -> nodes with nothing running on them
    sinfo -h -p "$1" -t idle -o '%D' 2>/dev/null | awk '{s+=$1} END {print s+0}'
}

qs_find_job() {  # <partition> <name_prefix> -> "<job_id> <status>" newest first
    squeue -h -u "$USER" -p "$1" -o '%i %j %T' --sort=-V 2>/dev/null \
        | awk -v p="$2" 'index($2, p) == 1 {print $1, $3; exit}'
}

qs_submit() {  # <partition> <launcher>
    ( cd "$QS_PROJECT_HOME" && sbatch --partition "$1" "$2" ) >/dev/null 2>&1
}

qs_kill() {  # <partition> <job_id>
    scancel "$2" >/dev/null 2>&1
}
