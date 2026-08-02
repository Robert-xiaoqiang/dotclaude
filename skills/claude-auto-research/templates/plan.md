# Campaign: <topic>

Approved <YYYY-MM-DD>. Status: active | complete | abandoned

> The standing instruction. Changes here need user approval; everything else in this
> directory is the agent's to maintain. Keep it short enough to reread every session.

## Objective
<One paragraph. What must be true at the end, in terms someone can check.>

## Success criteria
| criterion | metric | baseline | target | how measured |
|---|---|---|---|---|
| <primary> | <metric@bench> | <value, cite the run or paper> | <value> | <full bench, N seeds, decoding> |

State the primary metric explicitly. A campaign with two primary metrics has no decision rule when they
disagree.

## Baselines and comparisons
| arm | what it is | source | status |
|---|---|---|---|
| baseline | <untrained / published number / prior run> | <run dir or citation> | measured / to run |
| published method | <faithful reimplementation of X> | <paper> | to run |
| ours | <the proposal> | this campaign | to run |

## Assumptions
Repository, entry points, config groups, platform and scheduler, dataset locations, and the runtime
stack (`platform-runtime`). Write what you verified, not what you expect. Anything unverified is a risk.

## Budget
GPU-hours, wall-clock, storage under `$OUTPUT_DIR_HOME`, and money. If the user gave none, infer a
conservative limit from the project and mark it INFERRED, since exceeding an inferred budget is a
blocker, not a judgement call.

## Stages
Repeat this block per stage. No stage is vague: "improve the model" is not a stage, "raise
reward@healthbench from 0.41 to 0.50 by adding a rubric-grounded reward" is.

### Stage N — <name>
- **Objective:** <what this stage establishes>
- **Depends on:** <stage(s), or none>
- **Actions:** <concrete steps>
- **Expected artifacts:** <run dirs, checkpoints, summary.json paths>
- **Validation:** <the checks that must pass for this stage to count>
- **Advance when:** <explicit, checkable criterion>
- **Known failure modes:** <what is likely to break, and the recovery>
- **Compute:** <scale, expected wall-clock>

## Stopping conditions
- **Success:** <criterion met>
- **Exhaustion:** <retry or budget limit>
- **Futility:** <evidence that would prove the approach cannot reach target>

## Requires the user
Things that must stop the campaign: <credentials, spend above budget, objective changes, anything
leaving the repo>. See the autonomy boundary in `SKILL.md`.
