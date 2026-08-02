# State: <topic>

status: active | blocked | complete
updated: <YYYY-MM-DD HH:MM TZ>
plan: ./plan.md

> The cursor. Rewritten in place each cycle, so it stays short. History belongs in `journal.md`.
>
> **This file is an index, not an authority.** Verify every claim against the run dirs and the
> scheduler before acting on it. Where they disagree, the world is right.

## Now
- **Stage:** N — <name>
- **Doing:** <the single action in progress>
- **Next:** <the one action after this, so a cold session has a default>

## Verified complete
Only stages whose validation criteria were checked against artifacts on disk.

| stage | evidence | when |
|---|---|---|
| 1 — <name> | `<run dir>/eval/<bench>/summary.json`, metric=<value>, scope=full | <date> |

## In flight
See `jobs.md` for the full registry. Summarise here only what needs watching.

| job | stage | submitted | last seen | expected done |
|---|---|---|---|---|
| <name> | N | <time> | step <k>, healthy, <time> | <time> |

## Blockers
| blocker | needs | parked work | independent work continuing |
|---|---|---|---|
| <what is stuck> | <exactly what would unblock it, phrased so one reply resolves it> | <stage/job> | <what you are doing meanwhile> |

Empty is the normal state. Blocked on one thing is not blocked on everything.

## Best result so far
| metric | value | scope | run dir | vs baseline | vs target |
|---|---|---|---|---|---|
| <metric@bench> | <value> | full | `<path>` | <delta> | <delta> |

Always record scope. A `smoke(n=50)` number here that loses its label becomes a fake result later.

## Open questions
Things to resolve from evidence, not from the user. Each with the experiment that would settle it.
