---
name: platform-queue-shepherd
description: "Keep one live claim per service on a busy fleet and migrate it between clusters only when it is provably stuck and another cluster has the empty nodes right now. Owns the submit-or-adopt, hold-or-move decision; the mechanism is scripts/checks/queue_shepherd.sh in the project."
when_to_use: "Use when submitting whole-node jobs to a slammed cluster, when a submission has sat Queuing for hours while another cluster shows empty nodes, or when the temptation arises to submit the same service to two clusters at once. Not for diagnosing why a RUNNING job is slow, and never for resubmitting a job a human stopped."
---
# Skill: platform-queue-shepherd

## Purpose
A whole-node job on a busy cluster can queue for hours while a sibling cluster holds the empty
nodes it needs. The naive fixes are both wrong: double-submitting races two pools onto one
published router path and double-spends cards, and hand-migrating at 3am does not happen. The
shepherd is the judgement layer for a single alternative: one claim per service, checked on a
slow clock, moved only when stuck past a threshold AND an allowed alternative can seat it now.

## When to Use
- Submitting any whole-node service (a serving pool, a search arm) when `capacity` shows zero
  empty nodes on the preferred cluster.
- A claim has been Queuing past the stuck threshold and you are deciding whether to move it.
- Adding a new service to the shepherd's care.
- NOT for: slow-but-Running jobs (that is the watcher's diagnosis work), jobs a human stopped
  (an external stop is a decision, not a failure — resubmitting it starts a fight), or services
  whose venv exists on one accelerator only (they have no alternative to migrate to).

## The decision table

| observed | action | why |
|---|---|---|
| Queuing, age < threshold | wait | queues drain; churning claims loses queue position |
| Queuing, age >= threshold, alternative has >= needed empty nodes | kill + resubmit there | the only migration that can actually seat the job |
| Queuing, age >= threshold, no alternative has capacity | hold the claim | killing without a seat elsewhere is pure loss of position |
| Running / Succeeded | leave shepherd care | the watcher owns live jobs |
| Stopped | hold, report, never resubmit | a human decision outranks the shepherd |
| Failed | report only | failure needs diagnosis, not a blind retry |

**Empty nodes are the binding constraint, not free GPUs.** A whole-node job cannot use 14 free
cards spread across busy nodes; a `free` column of 24 with `emptynodes 0` seats nothing. The
2026-08-30 incident that produced this skill: ppu showed 8 free GPUs and 0 empty nodes with
1084 jobs submitted against 1024 allocatable, while a100 held a genuinely empty node.

**One claim per service, enforced.** Two live pools publish one `router.url` and silently
overwrite each other; two copies of a search arm double-spend accelerator-hours producing
archives that then have to be de-duplicated. The state dir under `$OUTPUT_DIR_HOME` refuses a
second claim for a named service.

**Migratability is a property of the venv chain, not a preference.** A service can move only
if every venv it needs exists on the target accelerator. A serving pool whose cuda venv is
proven elsewhere migrates; an arm whose sidecar venv is built for one accelerator does not,
and the manifest must say so or the shepherd will strand it.

**Re-query after acting.** A submit that printed nothing may have done nothing; the shepherd
adopts a claim only after the job appears in a fresh listing, never on the submit's exit code.

## Mechanism
The bash implementation lives in the project at `scripts/checks/queue_shepherd.sh`
(verbs: `submit`, `watch`, `tick`, `status`; per-service alternatives and node counts in its
`alts_for` manifest; state under `$OUTPUT_DIR_HOME/<project>/_launch/shepherd/`). Run `tick`
hourly from a cron or a session loop. Required env comes from `env.sh` and fails loudly
(`CPFS_HOME`, `OUTPUT_DIR_HOME`, `UV_VENVS_DIR`), per `code-no-fallbacks`.

## Rules
1. **One live claim per service.** A second submit for a claimed service is refused, because
   two pools on one router path silently clobber each other.
2. **Migrate only into measured capacity**: alternative `emptynodes >= nodes_needed`, read at
   decision time, never remembered from an earlier tick.
3. **Never resubmit a Stopped job.** A human stop outranks the shepherd; report and hold.
4. **A Failed job gets diagnosis, not a retry.** The shepherd drops the claim and says so.
5. **The stuck threshold is hours, not minutes** (default 2h): killing a queued job loses its
   queue position, so a move must be worth more than the position it burns.
6. **Adoption follows a listing, not an exit code.** The claim records what a fresh `jobs`
   query showed, because a quiet submit can have done nothing.
7. **Services without a full venv chain on the target never enter the manifest as migratable.**

## Anti-patterns
- **Dual-submitting "to be safe".** Feels like a hedge; it races two publishers onto one path
  and the loser's writes are silent.
- **Migrating on free-GPU counts.** 24 free cards and zero empty nodes seats nothing
  whole-node; the migration burns queue position for nothing.
- **The 5-minute shepherd.** Checking every few minutes tempts churn; queues move on the hour
  scale and every kill forfeits position.
- **Auto-retrying human stops.** The stop was a decision; the retry is an argument with
  whoever made it, run at cron frequency.

## Companions
`platform-run` (renders and routes the job spec the shepherd resubmits) · `code-no-fallbacks`
(the env contract the script enforces) · `claude-auto-research` (the campaign loop whose
watcher owns jobs once they run) · `claude-debrief` (how a migration is reported to the user).
