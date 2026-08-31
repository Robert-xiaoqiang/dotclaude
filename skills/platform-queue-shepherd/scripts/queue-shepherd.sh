#!/usr/bin/env bash
# queue-shepherd — one live claim per service, migrated only into measured capacity.
#
# WHAT THIS IS. The decision logic from the skill, as a runnable engine that knows nothing
# about any particular scheduler. Everything platform-specific lives behind a five-function
# adapter, and everything project-specific lives in a manifest file. Porting to a new
# scheduler means writing five functions; adding a service means adding one line.
#
#   queue-shepherd.sh <verb> [service]
#     submit  <service>   claim it on the preferred cluster that can seat it now
#     tick                one pass over every claim: hold, migrate, or release
#     watch   [service]   tick on a loop at $QS_INTERVAL_SECS
#     status              print every claim and what the world says about it
#     doctor              check the adapter and manifest without touching any job
#
# CONFIGURATION, all required unless marked. Nothing is defaulted to a guessed path, per
# `code-no-fallbacks`: a wrong root here silently shepherds the wrong fleet.
#   QS_ADAPTER        path to the adapter script (see adapters/ beside this file)
#   QS_MANIFEST       path to the service manifest (see services.example.conf)
#   QS_STATE_DIR      where claims are recorded; MUST be on shared storage, not /tmp
#   QS_STUCK_SECS     optional, default 7200. Queue-position is worth hours, not minutes.
#   QS_INTERVAL_SECS  optional, default 3600. `watch` sleeps this long between ticks.
#   QS_SETTLE_SECS    optional, default 45. Wait before re-querying after a submit.
#   QS_AHEAD_MAX_GPUS optional, default unset (disabled). Migrate only when the TARGET cluster's
#                     queued-ahead accelerator demand is at most this. Killing a claim forfeits
#                     the position it holds and a fresh submit joins the BACK of the target's
#                     queue — so a target with room today but a deep queue is not a seat, it is
#                     a second wait bought with the first one's position.
#   QS_AHEAD_MAX_RATIO optional, default unset (disabled). Same veto, expressed relative to the
#                     job's own accelerator ask (needs the manifest's 4th field): migrate only
#                     when ahead_demand <= ratio * own_gpus. Either knob may veto; both may be
#                     set. With neither set the decision is empty-nodes-only, as before.
#
# THE ADAPTER CONTRACT. Source-able bash defining exactly these, each printing to stdout and
# returning non-zero only on a hard error:
#   qs_job_status  <cluster> <job_id>      -> Running|Queuing|Stopped|Failed|Succeeded|Unknown
#   qs_empty_nodes <cluster>               -> integer, WHOLE EMPTY NODES (not free cards)
#   qs_queue_ahead_gpus <cluster>          -> OPTIONAL: accelerators demanded by jobs already
#                                             queued there (what a fresh submit waits behind).
#                                             Undefined -> the ahead-demand knobs are inert.
#   qs_find_job    <cluster> <name_prefix> -> "<job_id> <status>" for the newest match, or ""
#   qs_submit      <cluster> <launcher>    -> submits; adoption is the engine's job, not yours
#   qs_kill        <cluster> <job_id>      -> stops the job
#
# THE MANIFEST. One service per line, alternatives in preference order, `#` comments ignored:
#   <service>  <cluster>:<launcher>:<nodes_needed>  [<cluster>:<launcher>:<nodes_needed> ...]
# A service with ONE alternative is watch-and-report only: it can never migrate, which is the
# correct encoding of "its dependencies exist on one platform only". A service absent from the
# manifest is refused rather than guessed at.
set -euo pipefail

: "${QS_ADAPTER:?required: path to the platform adapter. See adapters/ beside this script.}"
: "${QS_MANIFEST:?required: path to the service manifest. See services.example.conf.}"
: "${QS_STATE_DIR:?required: claim directory on SHARED storage. A claim on node-local disk is invisible to the next box and the shepherd will double-submit.}"
STUCK_SECS="${QS_STUCK_SECS:-7200}"
AHEAD_MAX_GPUS="${QS_AHEAD_MAX_GPUS:-}"
AHEAD_MAX_RATIO="${QS_AHEAD_MAX_RATIO:-}"
INTERVAL_SECS="${QS_INTERVAL_SECS:-3600}"
SETTLE_SECS="${QS_SETTLE_SECS:-45}"

[ -r "$QS_ADAPTER" ]  || { echo "[shepherd] FATAL: adapter not readable: $QS_ADAPTER" >&2; exit 2; }
[ -r "$QS_MANIFEST" ] || { echo "[shepherd] FATAL: manifest not readable: $QS_MANIFEST" >&2; exit 2; }
# shellcheck source=/dev/null
. "$QS_ADAPTER"
for fn in qs_job_status qs_empty_nodes qs_find_job qs_submit qs_kill; do
    declare -F "$fn" >/dev/null || { echo "[shepherd] FATAL: adapter $QS_ADAPTER does not define $fn" >&2; exit 2; }
done
mkdir -p "$QS_STATE_DIR"

say()  { echo "[shepherd] $*"; }
warn() { echo "[shepherd] WARN: $*" >&2; }
now()  { date +%s; }

# ---------------------------------------------------------------- manifest
alts_for() {  # <service> -> "cluster:launcher:nodes ..." in preference order, or ""
    awk -v s="$1" '$1 !~ /^#/ && $1 == s { $1=""; sub(/^ +/,""); print; exit }' "$QS_MANIFEST"
}
all_services() { awk '$1 !~ /^#/ && NF >= 2 {print $1}' "$QS_MANIFEST"; }

# ---------------------------------------------------------------- claims
# A claim is one line: <job_id> <cluster> <launcher> <claimed_epoch>
claim_file() { echo "$QS_STATE_DIR/$1.claim"; }
read_claim()  { [ -f "$(claim_file "$1")" ] && cat "$(claim_file "$1")" || true; }
drop_claim()  { rm -f "$(claim_file "$1")"; }
write_claim() { printf '%s %s %s %s\n' "$2" "$3" "$4" "$(now)" > "$(claim_file "$1")"; }

# ADOPTION FOLLOWS A LISTING, NEVER AN EXIT CODE. A submit that printed nothing may have done
# nothing: a rejected flag, a quota refusal, a CLI that exits 0 on a usage error. The claim
# records what a fresh query actually saw.
adopt_after_submit() {  # <service> <cluster> <launcher>
    local svc="$1" cluster="$2" launcher="$3" id st
    say "submitting $launcher on $cluster"
    if ! qs_submit "$cluster" "$launcher"; then
        warn "submit reported failure for $launcher on $cluster"
    fi
    sleep "$SETTLE_SECS"
    read -r id st < <(qs_find_job "$cluster" "$launcher" || true)
    if [ -z "${id:-}" ]; then
        warn "$launcher did not appear on $cluster after ${SETTLE_SECS}s; NOT adopting"
        return 1
    fi
    write_claim "$svc" "$id" "$cluster" "$launcher"
    say "adopted $svc -> $id on $cluster (status ${st:-unknown})"
}

# ---------------------------------------------------------------- capacity
seats_available() {  # <cluster> <nodes_needed> -> 0 if it can seat the job right now
    local n; n="$(qs_empty_nodes "$1" 2>/dev/null || true)"
    # Trim: an adapter that pipes through awk/tail legitimately returns padded output, and
    # rejecting " 4" as unparseable would report a cluster with room as having none.
    n="${n//[$' \t\r\n']/}"
    if ! [[ "$n" =~ ^[0-9]+$ ]]; then
        warn "cannot read capacity of $1; treating as zero rather than guessing"
        n=0
    fi
    [ "$n" -ge "$2" ]
}

# ahead_demand_ok <cluster> <own_gpus> -> 0 when the target's queued-ahead accelerator demand
# does not veto a migration. THE ECONOMICS THIS ENCODES: a kill spends the position the claim
# already holds, and the resubmit starts LAST on the target — so empty nodes are necessary but
# not sufficient; a target whose queue already demands more than the configured bound would
# seat the jobs ahead first and the migration buys a second wait with the first one's position.
# Inert (returns ok) when neither knob is set or the adapter has no qs_queue_ahead_gpus.
ahead_demand_ok() {
    local cluster="$1" own="$2" ahead
    [ -n "$AHEAD_MAX_GPUS$AHEAD_MAX_RATIO" ] || return 0
    declare -F qs_queue_ahead_gpus >/dev/null || return 0
    ahead="$(qs_queue_ahead_gpus "$cluster" 2>/dev/null || true)"; ahead="${ahead//[$' \t\r\n']/}"
    if ! [[ "$ahead" =~ ^[0-9]+$ ]]; then
        warn "cannot read queued-ahead demand of $cluster; not vetoing on an unreadable number"
        return 0
    fi
    if [ -n "$AHEAD_MAX_GPUS" ] && [ "$ahead" -gt "$AHEAD_MAX_GPUS" ]; then
        say "ahead-demand veto: $cluster has ${ahead} accelerators queued ahead (> $AHEAD_MAX_GPUS)"
        return 1
    fi
    if [ -n "$AHEAD_MAX_RATIO" ] && [[ "$own" =~ ^[0-9]+$ ]] && [ "$own" -gt 0 ] \
       && [ "$ahead" -gt $(( AHEAD_MAX_RATIO * own )) ]; then
        say "ahead-demand veto: $cluster queues ${ahead} accelerators ahead (> ${AHEAD_MAX_RATIO}x our $own)"
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------- verbs
cmd_submit() {
    local svc="${1:?usage: submit <service>}" alts alt cluster launcher nodes
    alts="$(alts_for "$svc")"
    [ -n "$alts" ] || { say "FATAL: '$svc' is not in $QS_MANIFEST"; exit 2; }
    if [ -n "$(read_claim "$svc")" ]; then
        say "REFUSED: $svc already claimed ($(read_claim "$svc")). One live claim per service."
        return 1
    fi
    for alt in $alts; do
        IFS=: read -r cluster launcher nodes _gpus <<<"$alt"
        if seats_available "$cluster" "$nodes"; then
            adopt_after_submit "$svc" "$cluster" "$launcher" && return 0
        else
            say "$cluster cannot seat $svc now (needs $nodes empty nodes)"
        fi
    done
    # Nothing can seat it. Queue on the PREFERRED alternative rather than not running at all:
    # a queued claim holds position, and position is the thing migration spends.
    IFS=: read -r cluster launcher nodes _gpus <<<"${alts%% *}"
    say "no alternative has capacity; queueing on preferred cluster $cluster"
    adopt_after_submit "$svc" "$cluster" "$launcher"
}

cmd_tick() {
    local svc line id cluster launcher since age st alts alt acl alau anodes moved
    for svc in $(all_services); do
        line="$(read_claim "$svc")"; [ -n "$line" ] || continue
        read -r id cluster launcher since <<<"$line"
        st="$(qs_job_status "$cluster" "$id" 2>/dev/null || echo Unknown)"
        age=$(( $(now) - since ))
        case "$st" in
            Running|Succeeded)
                say "$svc: $st on $cluster ($id) -> leaving shepherd care"
                drop_claim "$svc" ;;
            Stopped)
                # A human stop is a decision. Resubmitting it is an argument with whoever made
                # it, run on a timer.
                say "$svc: STOPPED by someone ($id). Holding, never resubmitting."
                drop_claim "$svc" ;;
            Failed)
                say "$svc: FAILED ($id) -> needs diagnosis, not a retry. Claim released."
                drop_claim "$svc" ;;
            Queuing)
                if [ "$age" -lt "$STUCK_SECS" ]; then
                    say "$svc: queuing ${age}s on $cluster (< ${STUCK_SECS}s) -> wait"
                    continue
                fi
                moved=0
                for alt in $(alts_for "$svc"); do
                    IFS=: read -r acl alau anodes agpus <<<"$alt"
                    [ "$acl" = "$cluster" ] && continue
                    seats_available "$acl" "$anodes" || continue
                    ahead_demand_ok "$acl" "${agpus:-0}" || continue
                    say "$svc: stuck ${age}s; $acl has >= $anodes empty nodes -> migrating"
                    qs_kill "$cluster" "$id" || warn "kill of $id on $cluster reported failure"
                    # A QUIET KILL IS NOT A KILL. A stop with a wrong flag can print nothing,
                    # exit zero and do nothing (measured 2026-08-29 on a pod scheduler) — and a
                    # resubmit beside a still-live job is the two-copies collision this whole
                    # tool exists to prevent. Verify terminal state before submitting.
                    _kst="$(qs_job_status "$cluster" "$id" 2>/dev/null || echo Unknown)"
                    case "$_kst" in
                        Stopped|Failed|Succeeded|"") ;;
                        *) warn "$svc: $id still '$_kst' after kill; holding claim, no resubmit"
                           continue 2 ;;
                    esac
                    drop_claim "$svc"
                    adopt_after_submit "$svc" "$acl" "$alau" && moved=1
                    break
                done
                [ "$moved" = 1 ] || say "$svc: stuck ${age}s but no alternative can seat it -> holding position" ;;
            *)
                warn "$svc: status of $id on $cluster is '$st'; holding claim, not acting on an unknown" ;;
        esac
    done
}

cmd_watch() {
    say "watching every ${INTERVAL_SECS}s (stuck threshold ${STUCK_SECS}s)"
    while true; do cmd_tick; sleep "$INTERVAL_SECS"; done
}

cmd_status() {
    local svc line id cluster launcher since st
    printf '  %-28s %-12s %-10s %-10s %s\n' SERVICE JOB CLUSTER STATUS AGE
    for svc in $(all_services); do
        line="$(read_claim "$svc")"
        if [ -z "$line" ]; then
            printf '  %-28s %-12s %-10s %-10s %s\n' "$svc" "-" "-" "unclaimed" "-"
            continue
        fi
        read -r id cluster launcher since <<<"$line"
        st="$(qs_job_status "$cluster" "$id" 2>/dev/null || echo Unknown)"
        printf '  %-28s %-12s %-10s %-10s %sh\n' "$svc" "$id" "$cluster" "$st" \
               "$(( ( $(now) - since ) / 3600 ))"
    done
}

# Prove the wiring without touching a job: every service resolves, every cluster answers a
# capacity query, and the adapter is complete. Run this first on a new platform.
cmd_doctor() {
    local svc alt cluster launcher nodes n bad=0
    say "adapter : $QS_ADAPTER"
    say "manifest: $QS_MANIFEST"
    say "state   : $QS_STATE_DIR"
    for svc in $(all_services); do
        for alt in $(alts_for "$svc"); do
            IFS=: read -r cluster launcher nodes _gpus <<<"$alt"
            if ! [[ "$nodes" =~ ^[0-9]+$ ]]; then
                warn "$svc: '$alt' has a non-numeric node count"; bad=1; continue
            fi
            n="$(qs_empty_nodes "$cluster" 2>/dev/null || true)"; n="${n//[$' \t\r\n']/}"
            [[ "$n" =~ ^[0-9]+$ ]] || { warn "$svc: capacity query failed for $cluster"; bad=1; continue; }
            printf '  %-28s %-10s needs %-3s empty now %s\n' "$svc" "$cluster" "$nodes" "$n"
        done
    done
    [ "$bad" = 0 ] && say "doctor: OK" || { say "doctor: problems above"; return 1; }
}

case "${1:?usage: queue-shepherd.sh submit|tick|watch|status|doctor [service]}" in
    submit) shift; cmd_submit "$@" ;;
    tick)   cmd_tick ;;
    watch)  cmd_watch ;;
    status) cmd_status ;;
    doctor) cmd_doctor ;;
    *) echo "unknown verb '$1'" >&2; exit 2 ;;
esac
