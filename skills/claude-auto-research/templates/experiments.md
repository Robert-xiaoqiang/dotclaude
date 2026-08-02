# Experiments: <topic>

> One row per experiment, written when it launches and completed when it finishes. Negative results
> stay, since they are what stops the next session repeating them.
>
> Every number here traces to a `summary.json`. Nothing is estimated, remembered, or interpolated.

| id | hypothesis | revision | config delta vs baseline | scale | metric | result | scope | conclusion | next |
|---|---|---|---|---|---|---|---|---|---|
| E01 | baseline reference | `<sha>` | — | full | <metric@bench> | 0.412 | full | reference point | — |
| E02 | <falsifiable claim> | `<sha>` | `pipeline=<x>` | full | <metric@bench> | 0.437 ±0.014 | full | supported, +2.5pt over E01 | keep, go to E03 |
| E03 | <claim> | `<sha>` | `pipeline.reward=<y>` | smoke | <metric@bench> | 0.44 | smoke(n=50) | inconclusive at this scale | rerun full |

Columns that carry weight:

**hypothesis** — falsifiable, and written before the run. Record what result would have killed it.
**config delta** — the slots that differ from the arm being compared against, and nothing else. If this
column lists more than one major factor, the experiment cannot attribute its own result
(`naming-config` symmetry, `references/iteration.md`).
**scope** — `full` or `smoke(n=…)`. A missing scope makes the number unusable later.
**result** — with seed variance when available. A gain inside the variance is not a gain.
**conclusion** — supported, refuted, or inconclusive. "Inconclusive" is a real and common answer.

## Detail
Add a section for any experiment whose story does not fit a row.

### E0N — <name>
- **Hypothesis and its disconfirming outcome:** <what would have proved it wrong>
- **Setup:** <what changed, run dir, baseline compared against>
- **Result:** <numbers, with variance>
- **Reading:** <what it means, and what it does not mean>
- **Follow-up:** <the next experiment, or the decision it settled>
