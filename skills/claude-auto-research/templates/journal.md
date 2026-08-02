# Journal: <topic>

> Append-only. Decisions and the evidence behind them, newest at the bottom. This is what a user
> reads first after sleeping, so keep it to things that changed the campaign.
>
> Record: stage transitions, diagnoses, design changes, blockers, kills, ledger corrections, and
> external findings that led to an action. Do **not** record routine healthy polls or individual shell
> commands. A journal of "still fine" is a journal nobody rereads.

---
**<YYYY-MM-DD HH:MM TZ> · stage 2 · decision: advance**

<What happened, in one or two sentences.>

- **Evidence:** `<run dir>/eval/<bench>/summary.json`, <metric>=<value>, full scope, N=<count> matching
  the benchmark's expected size.
- **Decision:** advance to stage 3.
- **Why:** <the criterion from plan.md that this satisfies>.

---
**<YYYY-MM-DD HH:MM TZ> · stage 3 · diagnosis**

<Symptom.>

- **Evidence:** <log path, line, or the observation>
- **Root cause:** <named cause, distinct from the symptom>
- **Fix:** <the smallest change>, validated at <rung>.
- **Outcome:** <resubmitted as <job>, or still open>

---
**<YYYY-MM-DD HH:MM TZ> · ledger correction**

`state.md` said <X>, the world showed <Y>. Corrected.

- **How found:** <the check that caught it>
- **Consequence:** <what would have gone wrong had it not been caught>

---
**<YYYY-MM-DD HH:MM TZ> · blocker**

- **Blocked:** <what, and which stage it parks>
- **Needs:** <phrased so a single user reply resolves it>
- **Continuing with:** <the independent work that remains>
