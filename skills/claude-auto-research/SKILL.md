# Skill: claude-auto-research

## Purpose
Execute an approved research objective **unattended for 24–48h or longer** — implement, launch,
monitor, debug, evaluate, analyse, iterate — across job runtimes and context windows that outlive any
single session. This skill owns the **campaign**: the durable plan-plus-ledger that lets a cold session
resume from the repository alone, with no conversational context.

It supplies only the control loop and the surviving state. Everything it touches belongs to a
companion skill: `layout-workspace` (where things live), `naming-config` (what they are called),
`platform-run` (how a job is submitted), `layout-output` (what a run writes), `output-analysis` (how
runs are compared). Delegate to those rather than restating them.

## When to Use
- The objective needs several train/eval cycles, or one job longer than a session.
- The user is asleep, away, or has said to keep going without checking in.
- Resuming any campaign — a `docs/plans/<date>-<topic>/state.md` exists and is `active`.

Not for a single bounded change, one job you will sit and watch, or work the user is actively steering.

## The prime directive
**An approved plan is a standing instruction, not a one-time authorization.** While the plan covers the
situation in front of you, keep working.

None of these is a reason to stop: a job that takes nine hours, the user being asleep, one failed
experiment, a fixable bug, a disappointing metric, a dropped pod, a malformed checkpoint, a design that
misses target on its first attempt, or a fix that needs an hour of documentation reading first.

Stop only at the *Autonomy boundary* below. When you hit one, first finish every independent thing that
remains possible, then record the blocker precisely enough to be actioned in one reply.

## Where the campaign state lives
A campaign is **a plan that outgrew one file**, so it stays where plans live and becomes a directory:

```
<repo>/docs/plans/<YYYY-MM-DD>-<topic>/
  plan.md          approved intent: stages, gates, budgets, stop conditions   rarely changes
  state.md         the cursor: current stage, next action, open blockers      rewritten each cycle
  journal.md       append-only: timestamp · decision · evidence               grows
  experiments.md   one row per experiment: hypothesis → result → conclusion   grows
  jobs.md          job registry: pointers INTO $OUTPUT_DIR_HOME               grows
  report.md        the final report                                           written once, at the end
```

Three other placements are wrong, and the reasons are the rule:

- **Not the repo root.** A `LONG_HORIZON_PLAN.md` beside the README is a second home for something
  `docs/plans/` already owns, and `layout-workspace` forbids the second home.
- **Not `$OUTPUT_DIR_HOME`.** That path is mechanical — one segment per config group, then the config
  hash (`naming-config` rule 6, `layout-output`). A campaign spans many runs and sits *above* them, so
  it owns no segment there. Wedging one in collides with the group grammar.
- **Not `/tmp` or the session.** The campaign must outlive the context window. That is its entire point.

Single-file plans stay single files. A plan becomes a directory the moment it acquires stages and a
ledger, keeping the same `<date>-<topic>` name (`docs-plan`).

The campaign directory is **committed** as work proceeds (`git-commit` conventions, and never
auto-push). Its git history is the audit trail of an unattended run.

### The ledger indexes the world, it never replaces it
`state.md` and `jobs.md` are an **index over the output tree, not a source of truth.** Ground truth is
the run dir: `config.yaml` says what a run *is*, a `DONE` marker says it finished, `metrics.jsonl` says
what happened, the scheduler says what is alive.

**When the ledger and the world disagree, the world wins and you correct the ledger.**

That rule is what makes a cold resume safe. Never mark a stage complete on the ledger's word alone, and
never relaunch a job because the ledger forgot it.

## Resume protocol (run this first, every session)
1. **Find** campaigns: glob `docs/plans/*/state.md`. Those marked `active` are live.
2. **Read** `plan.md` in full. The objective and the gates are your standing instruction.
3. **Verify**, do not trust. For every job in `jobs.md`, check liveness (scheduler / PID / pod) *and*
   its run dir for `DONE`, newest checkpoint, and the tail of `metrics.jsonl`.
4. **Reconcile** `state.md` to what you found, and record any correction in `journal.md`.
5. **Then** choose the next action from *Stage transitions*.

Before every submission, check `jobs.md` **and** the scheduler for a job already doing that work.
Duplicate launches are the characteristic failure of an agent resuming with stale state.

## The loop
Each cycle: **orient → act → verify → record → decide.** Never skip *record*, since it is the only part
that survives you.

| phase | do | verified by |
|---|---|---|
| **Orient** | resume protocol above | ledger reconciled to the world |
| **Implement** | change code inside the existing architecture (`layout-workspace`) | it imports, tests pass |
| **Validate** | the scale ladder below, bottom rung first | each gate passes before the next |
| **Launch** | submit through the project's own platform layer (`platform-run`) | job registered in `jobs.md` |
| **Monitor** | `references/monitoring.md` | alive *and* progressing, not merely alive |
| **Diagnose** | `references/failure-recovery.md` | root cause named, not just symptom |
| **Evaluate** | `references/evaluation-integrity.md` | full bench, correct checkpoint, complete outputs |
| **Analyse** | compare against baseline and target (`output-analysis`) | numbers traced to `summary.json` |
| **Decide** | *Stage transitions* below | decision + evidence in `journal.md` |

### The scale ladder
Climb it in order. Each rung is a gate, and a rung never substitutes for the one above.

1. **Unit** — config parses, dataset sizes and splits are as expected, samples are shaped right, model
   and tokenizer load, one forward/backward pass runs.
2. **Smoke** — a few steps end to end, proving checkpoint save *and* resume, metric logging, and the
   run dir layout. Confirm the code path under test is the same one a real run takes.
3. **Diagnostic** — a medium run, only when isolating something a smoke run cannot reproduce.
4. **Full** — the planned scale, the planned config.

**A smoke run is a named configuration, never a flag.** `naming-config` is explicit: use the dataset
`tag` slot (`dataset_name=healthbench_smoke`) so the run gets its own hashed run dir and its own frozen
`config.yaml`. A `mode=smoke` that quietly rewrites fields is invisible in `config.yaml`, and it is what
lets a toy result later be mistaken for a real one. Getting this right is what makes
`references/evaluation-integrity.md` enforceable rather than aspirational.

## Stage transitions
Decide explicitly, and write the decision with its evidence into `journal.md`.

| decide | when |
|---|---|
| **Advance** | outputs complete, validation passed, results trustworthy, milestone criteria met, no open bug that invalidates the result |
| **Retry** | failure was operational or fixable, a bug invalidated an otherwise sound run, an incomplete job can resume safely, or a small config correction is plainly enough |
| **Refine / redesign** | the run was *valid* but missed target, failure analysis shows a structural weakness, repeated tuning does not move the metric, or evidence contradicts the plan's assumption |
| **Stop and report** | see the autonomy boundary below |

A result you do not trust is not a result. Audit the pipeline before you draw any conclusion about the
method — `references/evaluation-integrity.md` lists what to check and what "suspicious" looks like.

## Autonomy boundary
**Do without asking:** read anything, edit project code, write and run tests, run smoke and diagnostic
runs, submit training and evaluation jobs the plan already covers, reconnect to remote compute, monitor,
fix ordinary bugs, restart a failed job after validating a fix, analyse results, read documentation and
papers, advance between approved stages, and run evidence-driven iterations inside the plan's budget.

**Stop and record a blocker for:** missing credentials or access; spend beyond the plan's budget; a
destructive or irreversible action on data you did not create; changing the research objective itself;
publishing or sending results anywhere outside the repo; and ambiguity that the plan, the repo, and
prior decisions cannot resolve *and* that would materially change the objective.

Blocked on one thing is not blocked on everything. Park it, do the rest, and leave the exact question in
`state.md` under *Blockers*.

## Rules
- **Verify before trusting, always.** The ledger, a "successful" job, a plausible number, and a
  finished-looking eval each need one concrete check against a file on disk.
- **Never fabricate or interpolate a result.** A number in `experiments.md` traces to a
  `summary.json`. If a run did not finish, say so.
- **Never silently narrow the benchmark.** Subsetting is a named dataset config recorded in
  `config.yaml`, never a quiet `--limit`. A subset result is labelled a smoke or diagnostic result
  wherever it appears.
- **Change one major factor at a time**, and keep a comparable baseline alongside. Arms differ in
  exactly the slots that describe the change (`naming-config` symmetry).
- **Every experiment needs a hypothesis** written before it runs. Random hyperparameter thrashing is
  not iteration.
- **Fix the cause, not the symptom.** Same command twice with nothing changed is not a retry.
- **Respect the budget.** Honour stated GPU, wall-clock, storage, and money limits. With none stated,
  infer a conservative one from the project and write it into `plan.md` as an assumption.
- **Never delete a checkpoint or result to reclaim space** during a campaign. That is `output-cleanup`,
  with its own resume-safety rules, and it is not part of this loop.
- **Keep secrets out of logs, ledger, and commits.** Record a config *path*, not its contents.
- **Session scripts are durable.** Probes and diagnostics go to `scripts/checks/` with a
  what/when/usage header (`layout-workspace`), never left in `/tmp`.
- **Write the ledger as you go, not at the end.** A campaign that dies mid-cycle must lose at most one
  cycle of knowledge.

## Going deeper
| read | when |
|---|---|
| `references/monitoring.md` | a job is running: cadence, what to inspect, and the silent failures |
| `references/failure-recovery.md` | something broke: classify, find the cause, budget the retries |
| `references/evaluation-integrity.md` | before trusting any number, and before every final eval |
| `references/iteration.md` | the run was valid but missed target: hypotheses, ablations, literature |

Templates to copy into a new campaign directory live in `templates/`.

## Companions
`docs-plan` (the campaign directory is its directory form) · `layout-workspace` (where plans, scripts
and configs live) · `naming-config` (config, launcher, and run-dir names, and the `tag` slot that makes
a smoke run distinguishable) · `platform-run` (submitting the job) · `platform-runtime` (the
driver/image/venv stack a job needs to match) · `layout-output` (what a run writes and what must
survive) · `output-analysis` (comparing runs) · `output-cleanup` (reclaiming space, deliberately *not*
part of this loop) · `docs-arch` (durable architecture decisions graduate here) · `git-commit` (how the
ledger is committed) · `conventions` (the family index).
