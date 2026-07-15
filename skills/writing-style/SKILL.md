# Skill: writing-style

## Purpose
The user's style rules for authored documents. They cover punctuation and formatting in a written deliverable, not the content, and not the way you talk in the session.

## When to Use
When you write or edit a standalone document that the user will keep or publish. Examples are a paper, a report, an article or essay, a README or other repository documentation, a design doc, or a proposal. If the text is itself the thing being delivered, these rules apply.

## Out of scope
These rules do NOT govern:
1. Session replies and any conversational input or output in the chat.
2. Commit messages, PR descriptions, and other version-control text, which follow the git-commit skill instead.
3. Code, code comments, and config or data the user asked to see in a specific shape.
4. Logs, terminal or CLI output, and other machine-facing text.

If you are not producing a document the user will save or share, assume the rules do not apply.

## The rules
1. No em-dashes. Never use the "—" or "–" character. Rewrite with a comma, a pair of parentheses, or two separate sentences.
2. No semicolons. Break the clause into two sentences, or join it with a comma and a word like "and", "but", or "so".
3. No bulleted or numbered lists unless the user explicitly asks for one. Default to flowing paragraphs and write what you would have bulleted as ordinary sentences.
4. Use colons sparingly. Prefer a plain sentence over a colon that sets up an explanation or a list. A colon in front of a short quoted term, a path, or a ratio is fine.

## Words to avoid
Some words read as generic AI or corporate filler in a finished document. Prefer the plain word. This is a short curated set, not an exhaustive ban.
1. `delve into` becomes look at or examine.
2. `leverage` and `utilize` become use.
3. `showcase` becomes show or demonstrate, and `underscore` becomes highlight.
4. `testament to` becomes shows or proves.
5. `seamless` becomes smooth or without friction.
6. `game-changer` and `cutting-edge` become a plain statement of what changed or what is new.
7. `boasts` becomes has, `in order to` becomes to, and `due to the fact that` becomes because.
8. `embark`, `realm`, `tapestry`, `ever-evolving`, and `navigate the complexities` get rewritten in plain words.
9. `substrate`, used as a metaphor, becomes base, foundation, or layer.
10. `together`, `taken together`, and `collectively`, as a summarizing opener, get cut. State what the evidence shows.
11. `moving forward` becomes next, or name the actual time.
12. `landscape`, used as a metaphor, becomes field or area.
13. `pivotal` becomes key or important, or a plain statement of what it changed.

Technical terms keep their meaning. Words like robust, comprehensive, significant, novel, scalable, and state-of-the-art carry a precise claim in scientific and ML writing, for example robust to outliers, statistically significant, and a comprehensive benchmark. Use them freely when they make a real technical point. Avoid them only when they are vague praise, and never drop a correct technical term just to dodge a filler word.

## Sentence structures to avoid
1. Negation-pivot. Avoid "it is not just X, it is Y" and "this is not about X, it is about Y". State the claim directly.
2. Reflexive rule of three. Do not default to triples, whether an "adjective, adjective, and adjective" phrase or a three-item list. Vary the grouping or use a plain sentence.
3. Hollow intensifiers and hedges. Cut `genuinely`, `truly`, `really`, `it is worth noting`, `it is important to note`, `to be clear`, `perhaps`, and `arguably`, then state the point.
4. Vague endorsement. Do not write "worth noting" or "worth exploring". Give the specific reason something matters.
5. Sweeping "from X to Y" openers. Name the actual scope instead.

## Why
In finished documents this user prefers writing that reads like continuous, spoken prose rather than punctuation-heavy or list-chopped text. Em-dashes, semicolons, stacked colons, and reflexive bullets fragment a paragraph and read as a generic AI default. Chat and logs are working text, not deliverables, so they are deliberately left alone.
