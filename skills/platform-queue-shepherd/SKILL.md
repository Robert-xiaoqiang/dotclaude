---
name: platform-queue-shepherd
description: "Keep one live claim per service on a contended fleet, and move it to another cluster only when it is provably stuck and an alternative can seat it right now. Owns the submit-or-adopt and hold-or-move decision, on any scheduler: the platform-specific part is a five-function adapter, the fleet-specific part is a manifest file."
when_to_use: "Use when submitting whole-node work to a contended cluster, when a submission has queued for hours while a sibling cluster looks free, or when the temptation arises to submit the same service twice to be safe. Not for diagnosing a slow RUNNING job, and never for resubmitting one a human stopped."
---
# Skill: platform-queue-shepherd

## Purpose
Work that needs whole nodes can queue for hours on one cluster while a sibling holds exactly the
nodes it wants. The two obvious fixes are both wrong. Submitting to both races two publishers
onto one address and double-spends the fleet, and hand-migrating at 3am does not happen.

This is the judgement layer for one narrow decision: **one claim per service, checked on a slow
clock, moved only when it is stuck past a threshold AND an alternative can seat it now.** The
decision is scheduler-neutral. What changes per platform is only how you ask five questions, so
that part is an adapter and the rest is shared.

## When to Use
- Submitting a service that needs whole nodes when the preferred cluster shows none free.
- A claim has queued past the stuck threshold and you are deciding whether to move it.
- Adding a service to the shepherd's care, or porting the shepherd to a new scheduler.
- NOT for: a slow-but-running job, which is diagnosis and belongs to the watcher; a job a human
  stopped, where a retry is an argument with whoever stopped it; or a service whose
  dependencies exist on one platform only, which has nowhere to migrate to.

## Contents
- [The decision table](#the-decision-table)
- [Why capacity means empty nodes](#why-capacity-means-empty-nodes)
- [One claim per service](#one-claim-per-service)
- [Migratability is a property, not a preference](#migratability-is-a-property-not-a-preference)
- [Cases](#cases)
- [The mechanism](#the-mechanism)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## The decision table
Read the world, then act. Every row is a fact about the job plus a fact about the fleet.

| observed | action | why |
|---|---|---|
| Queuing, age < threshold | wait | queues drain, and churning claims forfeits position |
| Queuing, age ≥ threshold, an alternative has ≥ the nodes needed | kill, resubmit there | the only migration that can actually seat it |
| Queuing, age ≥ threshold, no alternative has room | hold the claim | killing without a seat elsewhere is pure loss |
| Running or Succeeded | release the claim | the watcher owns live work |
| Stopped | release, report, never resubmit | a human decision outranks the shepherd |
| Failed | release, report only | failure wants diagnosis, not a blind retry |

## Why capacity means empty nodes
**A whole-node job is seated by whole nodes, so free-unit counts are the wrong number.** A
cluster can report a large pool of free units that are scattered a few at a time across many
partly-occupied nodes, and seat nothing that needs a node to itself. Migrating on that number
spends the queue position you already hold and buys a seat that does not exist.

Every scheduler exposes both numbers and makes the misleading one easier to reach:

| scheduler | the misleading number | the number to use |
|---|---|---|
| pod schedulers (PAI DLC and similar) | free accelerator count | whole empty nodes |
| Slurm | `sinfo -o %C` idle CPUs | `sinfo -t idle -o %D` idle nodes |
| Kubernetes | allocatable minus requested | nodes with no pod of the exclusive class |

The same reasoning applies to any indivisible resource, so read the constraint the *job* has,
not the one the dashboard shows first.

## One claim per service
A service is a **role** ("the judge pool", "the indexer arm"), not a job id. The shepherd keeps
one live claim per role and refuses a second, because two live copies of one role fail quietly
rather than loudly:

- two serving pools publish one endpoint file, and the loser's writes vanish with no error
- two copies of a batch arm double-spend the fleet and produce duplicate outputs that then have
  to be de-duplicated by hand, usually after someone has already read one of them
- two writers of one state file on a shared mount can interleave, and on a mount without
  working locks the mutual exclusion you think you have is node-local only

The claim lives in a state directory on **shared storage**. A claim on node-local disk is
invisible to the next box, which is the same as having no claim at all.

## Migratability is a property, not a preference
A service can move only if everything it needs exists at the destination: the built environment,
the accelerator ABI it was compiled against, the data staged on that filesystem. That is a fact
about the service, so it is recorded as one. In the manifest, **the number of alternatives is the
policy**: two or more means migratable, exactly one means pinned and watch-only, absent means the
shepherd refuses to guess a placement.

Writing a second alternative a service cannot actually run is worse than writing none, because
the shepherd will faithfully strand it there at 3am.

## Cases
Concrete situations the table resolves. Use them as patterns, and add your own.

**The full-but-empty cluster.** The preferred cluster reports free units and zero empty nodes,
with more work submitted against it than it can allocate, while a sibling holds a genuinely
empty node. *Observed in the incident that produced this skill: a preferred pool showed 8 free
accelerators and 0 empty nodes, with 1084 jobs submitted against 1024 allocatable slots, while
an alternative held one whole free node.* Migrate, because the alternative can seat it and the
preferred one demonstrably cannot.

**The queue that was about to drain.** A claim is 20 minutes old and the cluster is busy. Wait.
Position is worth more than motion, and a threshold in minutes converts a shepherd into a
churner that never lets anything reach the front.

**The pinned sidecar.** A benchmark arm needs a helper built for one accelerator only. One
alternative in the manifest, so it is never moved however long it queues. The shepherd reports
and holds, which is the honest outcome.

**The human stop.** Someone stops a job at 2am because it was misconfigured. The shepherd sees
`Stopped`, releases the claim, and says so. Retrying would restart the exact thing a person
decided to end.

**The quiet submit.** A submit prints nothing and exits zero, having done nothing: a rejected
flag, a quota refusal, a CLI that treats a usage error as success. Adoption therefore follows a
fresh listing, never an exit code.

**The two-shepherd fleet.** Two sessions each run a shepherd over the same manifest. Both see a
stuck claim, both migrate it, and the second kills the job the first just placed. Split by
mandate, one shepherd per manifest, and let the claim directory be the referee.

**The spot reclaim.** On a preemptible pool a job can go from Running back to Queuing without
anyone acting. Treat the transition as a fresh queue age rather than the original claim time, or
a long-running job that gets reclaimed once looks instantly stuck and migrates for no reason.

## The mechanism
`${CLAUDE_SKILL_DIR}/scripts/queue-shepherd.sh` is the decision table as a runnable engine that
knows nothing about any scheduler. Verbs: `submit`, `tick`, `watch`, `status`, `doctor`.

Everything platform-specific is a **five-function adapter**:

```
qs_job_status  <cluster> <job_id>      -> Running|Queuing|Stopped|Failed|Succeeded|Unknown
qs_empty_nodes <cluster>               -> integer, WHOLE EMPTY NODES
qs_find_job    <cluster> <name_prefix> -> "<job_id> <status>" for the newest match, or ""
qs_submit      <cluster> <launcher>    -> submits, adoption is the engine's job
qs_kill        <cluster> <job_id>      -> stops the job
```

`scripts/adapters/` ships two, for a skylaunch-driven pod scheduler and for Slurm, which is
enough to show the seam is real. Porting means writing those five; the table above does not
change. Everything fleet-specific is one line per service in a manifest
(`scripts/services.example.conf`).

Run `doctor` first on any new platform: it resolves every service and queries every cluster's
capacity **without touching a job**, so a broken adapter or a typo in a node count surfaces
before the shepherd can act on it. Then run `tick` from a cron or a session loop on the hour
scale. Required configuration fails loudly rather than defaulting, per `code-no-fallbacks`:
guessing a state directory would shepherd a fleet you did not mean.

## Rules
1. **One live claim per service.** A second submit is refused, because two copies of a role
   collide silently rather than loudly.
2. **Migrate only into measured capacity**, read at decision time and never remembered from an
   earlier pass.
3. **Capacity is the indivisible unit the job needs**, usually whole nodes, never the free-unit
   count the dashboard shows first.
4. **Never resubmit a job a human stopped.** Release the claim and report it.
5. **A failure gets diagnosis, not a retry.**
6. **The stuck threshold is hours, not minutes.** Every kill forfeits queue position, so a move
   must be worth more than the position it burns.
7. **Adoption follows a fresh listing, not an exit code.**
8. **The claim directory lives on shared storage**, or the next box cannot see the claim.
9. **A service with no alternative it can actually run is pinned**, and the manifest says so.
10. **One shepherd per manifest.** Two shepherds over one fleet fight.

## Anti-patterns
- **Dual-submitting to be safe.** It feels like a hedge. It races two publishers onto one path,
  and the loser's writes are silent.
- **Migrating on free-unit counts.** Scattered free units seat nothing that needs a whole node,
  so the move burns position and gains nothing.
- **The five-minute shepherd.** Queues move on the hour scale. Checking every few minutes only
  creates opportunities to churn.
- **Auto-retrying human stops.** The stop was a decision, and the retry argues with it on a
  timer.
- **Trusting a submit's exit code.** A quiet command may have done nothing at all.
- **A manifest entry the service cannot run.** The shepherd will strand it there, at the hour
  when nobody is watching.

## Companions
`platform-run` (renders and routes the spec the shepherd resubmits) · `platform-runtime` (why an
environment is or is not portable to another accelerator, which decides migratability) ·
`code-no-fallbacks` (the required-input contract the engine enforces) · `claude-auto-research`
(the campaign whose watcher owns work once it runs) · `claude-debrief` (how a migration gets
reported).
