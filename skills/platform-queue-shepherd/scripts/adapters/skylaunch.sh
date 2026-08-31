# Adapter: skylaunch CLI over a pod scheduler (PAI DLC and friends).
#
# Source-able by queue-shepherd.sh. Defines the five contract functions and nothing else, so
# the engine stays free of any scheduler's vocabulary.
#
#   QS_SKY_PY       interpreter that can import skylaunch
#   QS_PROJECT_HOME project root the CLI resolves launchers against
#   QS_SUBMIT_ENVS  optional, space-separated K=V injected into the submit only
#
# CAPACITY IS EMPTY NODES, NOT FREE CARDS. `capacity` prints a table whose last column is the
# empty-node count; a free-card column can read 24 while nothing whole-node can be seated.
# Parsing the wrong column is the single most expensive mistake available here, because it
# migrates a job into a cluster that cannot start it and burns the queue position to do so.

: "${QS_SKY_PY:?required: interpreter that can import skylaunch}"
: "${QS_PROJECT_HOME:?required: project root for launcher resolution}"

_sky() { SKYLAUNCH_PROJECT_HOME="$QS_PROJECT_HOME" timeout 150 "$QS_SKY_PY" -m skylaunch.cli "$@"; }

qs_job_status() {  # <cluster> <job_id>
    _sky status --cluster "$1" "$2" 2>/dev/null \
        | grep -m1 '"Status"' | sed 's/.*"Status": *"\([A-Za-z]*\)".*/\1/'
}

qs_empty_nodes() {  # <cluster> -> whole empty nodes
    _sky capacity --cluster "$1" 2>/dev/null | tail -1 | awk '{print $NF}'
}

qs_find_job() {  # <cluster> <name_prefix> -> "<job_id> <status>" newest first
    _sky jobs --cluster "$1" --own 2>/dev/null \
        | awk -v p="$2" 'index($6, p) == 1 {print $2, $1; exit}'
}

qs_submit() {  # <cluster> <launcher>
    local cluster="$1" launcher="$2"
    ( cd "$QS_PROJECT_HOME" && env ${QS_SUBMIT_ENVS:-} \
        make job LAUNCHER="$launcher" PLATFORM=dlc CLUSTER="$cluster" ) >/dev/null 2>&1
}

qs_kill() {  # <cluster> <job_id>
    _sky kill --cluster "$1" "$2" >/dev/null 2>&1
}

qs_queue_ahead_gpus() {  # <cluster> -> accelerators demanded by jobs queued there (approximation)
    # The pod listing has no per-job accelerator column, and querying every queued job's detail
    # is hundreds of API calls per tick. The capacity table carries card-denominated `used` and
    # `submitted` totals, so submitted-minus-used is the demand a fresh submit waits behind.
    # APPROXIMATE on purpose: it counts every non-running ask, not strictly the ones scheduled
    # ahead of ours — a conservative over-estimate, which is the safe direction for a veto.
    _sky capacity --cluster "$1" 2>/dev/null | tail -1 \
        | awk '{u=$(NF-2); s=$(NF-1); d=s-u; if (d<0) d=0; print d}'
}
