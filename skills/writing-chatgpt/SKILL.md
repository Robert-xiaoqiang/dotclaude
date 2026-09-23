---
name: writing-chatgpt
description: "Route paper and slide prose to the writer tool at $PROJECTS_HOME/ChatGPTMCP (./writer, also the `writer` MCP server), which calls a general-purpose frontier model through ModelRouter's Responses API under the author's own writing rules and keeps a named session, so the coding agent patches files and never drafts the prose itself. Covers what to hand it (passage, request, context files, session), which task to pick, and how to patch the result back."
when_to_use: "Use when asked to write, rewrite, polish, critique, shorten or translate an abstract, introduction, related work, method, results paragraph, reviewer response, slide text or speaker notes, in English or Chinese, or when a request says 'use the writer' or 'use ChatGPT'. Also use when prose has come back shorter but flatter, every line a conclusion with the reasoning removed, which is the premature-compression failure this skill names. Not for code, tables, grep, citation lookups or LaTeX plumbing, which the coding agent does itself, and not for chat replies."
---
# Skill: writing-chatgpt

## Purpose
Paper and slide prose written inside a coding agent comes out in the agent's own register: short,
utilitarian, inspect-modify-summarize. The writer tool at `$PROJECTS_HOME/ChatGPTMCP` exists so
that prose is drafted by a general-purpose frontier model under a writing prompt stack instead,
with the author's `writing-style`, `writing-style-zh`, `writing-paper` and `docs-slides` rules
already loaded, and with a session that remembers the thread. This skill says how to hand work to
it and how to take the result back. The division is fixed: the writer does the editorial work,
the coding agent does the filesystem work.

## Contents
- [When to Use](#when-to-use)
- [The tool](#the-tool)
- [Which task](#which-task)
- [What to hand it](#what-to-hand-it)
- [Premature compression](#premature-compression)
- [Taking the result back](#taking-the-result-back)
- [Usage](#usage)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- A request to write, rewrite, polish or "refine" any manuscript prose: abstract, introduction,
  related work, a method subsection, a results or ablation paragraph, a conclusion.
- A reviewer response, a rebuttal paragraph, or a research note that will be read by others.
- Slide text and speaker notes, a talk storyline, or a deck that needs stripping to the register
  of `docs-slides`.
- Shortening to a page budget, or checking that the abstract, introduction and experiments tell
  one story.
- Chinese deliverables as much as English ones. The tool picks the language layer from the passage.
- Not for: code, LaTeX tables and macros, figure scripts, citation keys and `.bib` entries, grep
  over the repo, or anything that is a fact lookup. Those stay with the coding agent. Not for the
  agent's own chat replies, which follow no document style.

## The tool
The project is `$PROJECTS_HOME/ChatGPTMCP`. Its command is `./writer` at the project root, and the
same tasks are exposed as the `writer` MCP server, registered user-scope in Claude Code
(`claude mcp get writer`) and in `$CODEX_HOME/config.toml`. Prefer the MCP tools when they are
loaded; fall back to the command when they are not:

```sh
$PROJECTS_HOME/ChatGPTMCP/writer --help
$PROJECTS_HOME/ChatGPTMCP/writer check       # endpoint, key, one round trip
$PROJECTS_HOME/ChatGPTMCP/writer models      # router ids known to work; --probe pings them
```

The endpoint and key are `MODELROUTER_BASE_URL` and `MODELROUTER_API_KEY` in `$CPFS_HOME/.secret`.
The shim sources env.sh when they are missing, so a bare MCP launch works. Sessions live under
`$OUTPUT_DIR_HOME/writer/sessions/<name>/` as `meta.json` plus `transcript.jsonl`.

## Which task
| task | give it | it returns |
|---|---|---|
| `rewrite` | the passage, the request | the full replacement text, same markup, ready to paste |
| `critique` | the passage | quoted problems with a fix each, no rewrite |
| `slide` | a section, outline or slide, plus the register (research talk or pitch) | title, bullets and the spoken script per slide |
| `compress` | the passage and a budget ("to 180 words") | the shortened passage, no claim dropped |
| `narrative` | several sections concatenated, each under a heading | where the chain breaks, and the storyline told vs the one to tell |
| `ask` | a session and a follow-up request | text or an answer, in the session's thread |

`rewrite` is the default for "polish", "refine" and "improve". Use `critique` first when the request
is "what is wrong with this section", because a rewrite hides what it fixed.

## What to hand it
Four things, every time the work is more than a sentence:

1. **The passage** as a file (`file`), not pasted, so the source label lands in the transcript and
   the markup format is preserved.
2. **The request in your own words** (`instruction`): what the passage should do that it does not,
   for example "establish the limitation before naming the method" or "make the transition into
   Section 3 explicit". Restating the task name is not a request.
3. **Context files** (`context`): the paper repo's `.writer/research_context.md` (what the project
   is, the terminology it keeps, the headline result) and the adjacent sections. The writer needs
   the argument around the passage, not the repository. Never pass source code, and do not pass
   the whole manuscript when two neighbouring sections carry the argument.
4. **A session name** (`session`), one per thread of work, such as `harnessrl-intro` or
   `mempi-rebuttal`. The session remembers the context files, so a follow-up passes only the
   request. A call without a session is one-shot and forgets everything.

Pass `out` when the result should land in a file. The tool writes it and returns a preview, so a
long section is never re-emitted through the agent's own output. Then diff the file against the
original and report what changed. Keep `effort` and `verbosity` at their defaults (high, high)
unless the request is a one-line touch-up; low effort is for pings, not for prose.

## Premature compression

The failure this tool exists to avoid does not disappear when a frontier model does the writing; it
reappears in the request. Ask for "polish" or "make it tighter" and what comes back is the same
compression the coding agent would have produced: every line squeezed into a conclusion, fewer
characters, and the reasoning that made the line worth saying eaten in the process. The author named
it after reading a rewritten slide table: *premature compression*. Good brevity is thinking the
distinction through and then deleting words. Bad brevity is compressing into a conclusion before the
distinction is clear.

It shows up as four symptoms, all visible in a before/after table:

1. **Mixed abstraction levels in one list.** Four rows about the problem, the representation and the
   memory requirement, then a fifth row that is an experimental number. The list stops being a
   comparison and becomes four concept upgrades with a result bolted on.
2. **Enumeration upgrade instead of conceptual upgrade.** "state and intermediate steps within one
   task" becomes "state, intermediate steps and reasoning traces within a single task". More
   complete, and the audience is no closer to knowing why the method is better. The upgrade that
   was wanted crossed a level: *memory does not live only inside one task, training is itself a
   temporal process that needs memory.*
3. **Every line a slogan.** "X is temporal." "Y needs history." "Z is multi-dimensional." "We reach
   51.93." Each reads like a paper claim and none of them unfolds the object, the difficulty, why
   the existing view is not enough, and how this work widens it. One such line per page lands; a
   page of them reads as assertion.
4. **An unstable left-to-right relation.** In one row the pair is vague to specific, in the next old
   view to new view, in the next problem to requirement, in the last old phrasing of a result to new
   phrasing. The reader cannot tell what the right-hand column is claiming to be.

So the request carries the relation, not just the verb. "Keep the derivation: object, difficulty,
why the current view falls short, what we widen it to" is a request. "Polish" is not. When the
passage is a two-column comparison, say what the right column *is* (the view we now take, the
capability we now have, a more precise statement of the same thing) and hold every row to it. When a
line is genuinely a claim and not a summary, say so, and let the neighbouring lines stay expository
rather than promoting all of them to match.

Length is the wrong lever, and saying "make it shorter" is what invites the failure. Ask for the
distinction first, then compress in a second call against a budget, which is what `compress` is for.

## Taking the result back
The reply is the whole passage, so replace the original span, never splice sentences from the two.
Read the diff before committing to it: numbers, citation keys, labels, macros **and every `\input`
or `\include` line** must be unchanged,
and a `[CITE]` or `[NUMBER]` placeholder in the reply is the writer refusing to invent a fact, which
the agent then resolves from the repo. A critique or narrative reply is a list of problems, not a
patch; apply the fixes it names with `rewrite` or `ask` in the same session.

A slide reply follows the `docs-slides` register: title, bullets, notes. Paste it into the deck
source, then run the deck's own lint and timing gates. The writer does not know the slot length.

## Usage
From a paper repo, a first rewrite with context and a session, then a follow-up:

```sh
W=$PROJECTS_HOME/ChatGPTMCP/writer
$W rewrite --file sections/intro.tex \
    --context .writer/research_context.md sections/abstract.tex sections/related.tex \
    --session harnessrl-intro \
    --instruction "Rewrite the motivation and the transition into our method." \
    --out sections/intro.tex
$W ask --session harnessrl-intro \
    --instruction "The second paragraph hedges. State the limitation directly."
$W critique --file sections/method.tex --context .writer/research_context.md
$W slide --file sections/results.tex --session harnessrl-talk \
    --instruction "Three slides for a research talk, noun-phrase titles, one per RQ."
$W rewrite --file abstract_zh.md --context .writer/research_context.md \
    --instruction "改写成答辩用的中文摘要，先说问题再说方法，保留所有数字。"
$W sessions
$W session harnessrl-intro --last 2
```

The MCP tools take the same arguments (`file` or `text`, `instruction`, `context`, `session`,
`lang`, `domain`, `model`, `effort`, `verbosity`, `out`, `reset`). A routing sentence from the user
maps directly: "Rewrite Sec 2.1 with the writer, session `harnessrl-method`, context `.writer/*.md`
and `sections/intro.tex`, then patch `sections/method.tex`" is one `rewrite` call with `out`, then a
diff.

## Rules
1. **Prose goes to the writer, files go to the agent.** A coding agent that drafts an abstract inline
   produces the compressed register this tool exists to avoid, so any request in `When to Use` is a
   writer call, not a local edit.
2. **Every call carries a passage file, a request in plain words, context files and a session
   name**, except a one-line touch-up. A call with no context rewrites the passage against nothing
   and drifts from the paper's terminology.
3. **Context is the argument, not the repo.** `.writer/research_context.md` plus adjacent sections.
   Source code and unrelated sections cost tokens and add nothing the writer can use.
4. **One session per thread of work**, named by paper and section. A session reused across papers
   replays the wrong history; a missing session forgets the context on the follow-up.
5. **The reply replaces the whole span.** Splicing sentences between the old and new text breaks
   the transitions the writer wrote, which is the thing it was asked to fix.
6. **Diff before accepting.** Numbers, citation keys, labels and macros must match the original,
   and a bracketed placeholder is a fact for the agent to supply from the repo, never to delete.
7. **Model ids come from `./writer models`**, not from memory. The router's list drifts; the probe
   under `scripts/checks/probe_models.py` is what refreshes it.
8. **The request names the relation the passage must keep**, not only the edit verb. "Polish",
   "tighten" and "make it slide-like" all read as licence to compress, and the reply arrives with
   the reasoning removed and each line promoted to a conclusion.
9. **Never ask for brevity and insight in the same call.** Get the distinction right first, then run
   `compress` against a stated budget. A single "shorter and sharper" request produces sentences
   that are shorter and claim more than the passage established.
10. **A list holds one abstraction level.** Before sending a table or a bullet list, check that every
   row answers the same kind of question; a results number sitting among conceptual rows is a
   different list and belongs on its own.
11. **Slides still pass the deck's gates.** The writer returns text in the right register; overflow,
   timing and citation checks belong to the deck build (`docs-slides`).

## Anti-patterns
- **The inline draft.** The agent rewrites the introduction itself "to save a call". The result is
  correct and flat, and the user notices the register before the content.
- **The task name as the request.** `instruction: "rewrite"` tells the writer nothing the task did
  not. Say what the passage fails to do.
- **The repository as context.** Twenty files passed as `context`, most of them code. The writer
  reads them for the argument and finds none, and the passage comes back generic.
- **The sentence splice.** Keeping the old first sentence and the new rest. The writer's transition
  now points at a sentence it never saw.
- **The dropped `\input`.** Asked to remove "where a file lives", the writer deleted
  `\input{runindex}` and `\input{pairedtests}` from the top of an appendix: thirteen pages of tables
  and four labels gone, and a label-set diff of the returned text showed nothing, because the
  labels lived in the included files. Diff the `\input` lines explicitly, and never phrase a
  removal request in words that also describe an include.
- **Deleting the placeholder.** `[CITE]` removed to make the paragraph clean. The claim is now
  unsupported and the reviewer finds it.
- **Premature compression.** The reply is shorter, every line is a conclusion, and the middle step
  that made the point land is gone. Caused by a request that asked for brevity before the
  distinction was settled.
- **The enumeration upgrade.** The noun gets more items, the claim does not change level. Reads as
  progress, teaches nothing.
- **The slogan page.** Every line is a paper-grade claim, so none of them carries weight and nothing
  is explained.
- **Low effort for prose.** Set to make the call faster; the reply is the compressed register again.

## Companions
`writing-style` and `writing-style-zh` (the rules the writer's prompt stack encodes; read them to
judge a reply, not to redo the writing) · `writing-paper` (the argument-level layer the writer
applies to a paper) · `docs-slides` (the register the `slide` task writes in, and the gates the deck
must still pass) · `docs-weekly` (the weekly report, which may hand its prose stage to the writer) ·
`naming-config-prompting` (how the writer's prompts are stored and hashed, for anyone editing them)
· `conventions` (the map).
