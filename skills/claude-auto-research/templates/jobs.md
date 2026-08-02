# Job registry: <topic>

> Every submitted job, appended at launch and updated at each inspection. This is how a cold session
> learns what is running without asking the user, and it is the duplicate-submission guard: **check
> here and the scheduler before every launch.**
>
> Liveness fields go stale by nature. Re-verify, never trust.

## Active

### <job-name>
- **launcher:** `launcher/<pipeline>__<model>__<dataset>/`
- **stage:** N
- **platform:** <dlc | slurm | local | pod> · **id:** <job id / PID> · **host:** <pod or node>
- **submitted:** <YYYY-MM-DD HH:MM TZ>
- **command:** `<exact submit command, reproducible as written>`
- **config:** `<config path>` · **revision:** `<git sha>`
- **run dir:** `$OUTPUT_DIR_HOME/<project>/<groups...>/<hash>/`
- **log:** `<path>`
- **expected:** <artifacts, and expected wall-clock>
- **status:** running | queued | done | failed | killed
- **inspections:**
  | when | step | loss / reward | throughput | note |
  |---|---|---|---|---|
  | <time> | <k> | <value> | <rate> | healthy |

The run dir is the job's identity. It is derived by the config system (`naming-config` rule 6), never
chosen by hand, so two jobs with the same run dir are the same run and one of them is a duplicate.

## Completed
| job | stage | run dir | outcome | result | when |
|---|---|---|---|---|---|
| <name> | N | `<path>` | done | <metric>=<value> (full) | <date> |

## Failed or killed
| job | stage | run dir | class | cause | action taken | when |
|---|---|---|---|---|---|---|
| <name> | N | `<path>` | OOM | <named root cause, not the symptom> | <fix, and the retry job name> | <date> |

Keep failed entries. They are what stops a later session repeating an attempt that already failed.
