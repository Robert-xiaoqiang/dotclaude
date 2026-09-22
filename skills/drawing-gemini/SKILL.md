---
name: drawing-gemini
description: Generate an image from a text prompt through ModelRouter's image models (gpt-image, and the Gemini and Seedream families when the key carries them), for concept art, cover images, and candidate figure treatments a reviewer can compare against a hand-built one. Covers the endpoint, the three request shapes, prompt discipline for a scientific figure, and the limit that decides whether a generated image may ship. - Use when asked to generate or draw a picture from a description, to produce alternative renderings of a paper figure, or when a deliverable wants an illustration no vector pipeline is going to hand-draw. Not for a figure whose labels, numbers or arrows have to be exactly right, which belongs to docs-figure.
---

# Skill: drawing-gemini

## Purpose
One place for text-to-image generation on this machine. The models sit behind the same ModelRouter
endpoint and key the writer uses, so the credentials, the rate limit and the failure messages are
already understood. The scripts live in this skill rather than in a separate project, so the skill is
the whole of it: read `SKILL.md`, run `scripts/genimage.py`, get a PNG.

It owns **how to get an image**. It does not own **what a figure may contain**, which is `docs-figure`,
and it does not own the vector pipeline that produces the figure a paper actually ships.

## Contents
- [When to Use](#when-to-use)
- [The endpoint and what answers today](#the-endpoint-and-what-answers-today)
- [The scripts](#the-scripts)
- [Writing the prompt](#writing-the-prompt)
- [What a generated image may be used for](#what-a-generated-image-may-be-used-for)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- A concept illustration, a cover image, a teaser, a slide background, a mascot.
- Candidate treatments of a paper figure, generated beside the hand-built one so a person can pick
  the composition before anybody draws it properly.
- Anything where the picture carries a feeling rather than a fact.

Not for a figure whose arrows, labels and numbers have to be right. Generators misspell, invent
labels, and route arrows into the wrong box, and they do it confidently. That figure is built in
TikZ, matplotlib or PowerPoint under `docs-figure`.

## The endpoint and what answers today
The base URL and key are `MODELROUTER_BASE_URL` and `MODELROUTER_API_KEY` in `$CPFS_HOME/.secret`,
the same pair `writing-chatgpt` uses. Source it before any call:

```sh
set -a; . $CPFS_HOME/.secret; set +a
```

Three protocols reach three families, and **the model id says which one it speaks**. The `mr.` prefix
belongs to the OpenAI-protocol ids only, and using it on a Google or Volcengine id is what produces a
routing error that looks like a missing model.

| family | path | model ids |
|---|---|---|
| OpenAI images | `{base}/images/generations` | `mr.gpt-image-2`, `gpt-image-1.5` |
| Google | `{root}/protocol/vertex/v1beta/models/{model}:{action}` | `vertex_ai.gemini-3-pro-image-preview`, `ai_studio.gemini-3-pro-image-preview`, and the `3.1-flash-image-preview` and `2.5-flash-image` pairs |
| Volcengine | `{root}/protocol/volcengine/api/v3/images/generations` | `doubao-seedream-5-0-260128`, `doubao-seedream-4-5-251128` |

Google authenticates with `x-goog-api-key: Bearer <key>`, and the action is `generateContent` with
`responseModalities: ["IMAGE"]`. The two Google channels differ in how they take an input file:
`vertex_ai.*` accepts both `contents[].parts[].fileData.fileUri`, which the router converts to a GCS
link, and `contents[].parts[].inlineData.data`, which it converts to base64. `ai_studio.*` accepts
only the second. Text-to-image needs neither, so either channel works for this skill.

Volcengine authenticates with `Authorization: Bearer <key>`. Seedream is the image family and is
synchronous. **Seedance is video, not image**, and it is asynchronous: a POST to
`{root}/protocol/volcengine/api/v3/contents/generations/tasks` creates a task whose body carries
`content[]` parts, `ratio`, `duration` and `generate_audio`, and the result is polled rather than
returned. This skill does not drive it. The Doubao seed text models split by id, where an id ending
in `-completion` speaks `/chat/completions` and everything else speaks `/responses`.

Three failures mean three different things, and only one of them is worth retrying:

- `NoAvailableModels` is the router saying this key has no such model. A provisioning request fixes
  it, a different path does not.
- `AllModelsFailed` means the route was found and the upstream refused. Usually a wrong id shape for
  that channel, sometimes a real outage, and `429 ... model is overloaded` under it is worth a retry.
- `401 API密钥状态异常：AK余额耗尽禁用` means the key itself is disabled because its balance is
  exhausted. Every endpoint returns it, text and image alike, so a probe that shows this everywhere is
  reporting one billing fact rather than a model inventory. **This is the state as of 2026-09-21.**
  Before that the OpenAI family answered, the Google and Volcengine ids were never reached under
  their correct prefixes, and the internal domains `routify.alibaba-inc.com` and
  `routify-online.alibaba-inc.com` are not reachable from this host in any case. Re-probe once the
  key is funded:

```sh
python3 $CPFS_HOME/.claude/skills/drawing-gemini/scripts/genimage.py --probe
```

The key is rate limited at 5 requests per minute for synchronous models and 1 for asynchronous ones,
so the probe sleeps between calls and a batch of generations should too.

## The scripts
`scripts/genimage.py` is the whole interface. It picks the family from the model id, sends one
request, pulls the first image out of whichever reply shape came back, and writes a PNG.

```sh
G=$CPFS_HOME/.claude/skills/drawing-gemini/scripts/genimage.py
python3 $G --prompt-file fig1.prompt.txt --out fig1.png            # mr.gpt-image-2, 1536x1024
python3 $G --model gpt-image-1.5 --prompt-file fig1.prompt.txt --out fig1_alt.png
python3 $G --model mr.gemini-3-pro-image-preview --aspect 3:2 \
           --prompt-file fig1.prompt.txt --out fig1_gemini.png     # when the key carries it
python3 $G --probe
```

Keep the prompt in a file next to the output, never only in the shell history. The prompt is the
source and the PNG is the artifact, exactly as a figure script is the source of a plot.

## Writing the prompt
A generator is good at composition and bad at content. The prompt should therefore spend its length
on layout and style, and almost none of it on text.

- **Open with the register**: publication-quality schematic, flat vector, white background, thin grey
  strokes, one or two muted accent colours, serif labels, no 3D, no drop shadows, no photographic
  texture. Without this a paper figure comes back as glossy marketing art.
- **Give the paper's own sentences** for what the picture is about, taken from the abstract and the
  method, so the composition is about the right thing.
- **Then describe the drawing element by element**, in reading order, naming the shape, its position
  relative to what came before, and what connects to it. Rows before columns, left before right.
- **Cap the text**: at most two or three words per label, spelled out in the prompt, and an explicit
  ban on a title, a caption, a legend, panel letters and a watermark. Generators add all five.
- **Say what must be absent**, because absence is content in a comparison figure: an empty dashed
  box where the other row has a store, no token squares in the row that never decodes.
- **One request, one picture.** Ask for three variants and you get three different visual languages.

## What a generated image may be used for
The output is a proposal about composition. Before it goes anywhere a reader will see:

- Read every word in the image. A misspelled or invented label is disqualifying, and it is the
  commonest defect by a wide margin.
- Follow every arrow. Generators connect boxes that have no relation.
- Check the count. Three rows asked for, three rows delivered, not four.

An image that fails any of those can still be shown as a candidate treatment, clearly labelled as
generated, so a person can choose the composition. It cannot be the figure of record. When the
composition is chosen, rebuild it in the vector pipeline, where the labels are macros and the arrows
are anchored.

## Rules
1. **Source `$CPFS_HOME/.secret` before calling.** The script raises `KeyError` with no endpoint,
   which is the right failure.
2. **Probe before you promise a model.** The available set is a property of the key on the day.
3. **The prompt lives in a file beside the image**, so the picture can be regenerated and diffed.
4. **Style register first, subject second, layout third, text last.**
5. **Read every label in the output before using it anywhere.**
6. **A generated image is never the figure of record in a paper.** It is a candidate treatment, and
   it says so wherever it appears.
7. **Space the calls.** Five requests per minute, shared with every other user of the key.
8. **Never put the key on a command line or into a prompt file.**

## Anti-patterns
- **The unread label.** The image is beautiful and one box says "memroy". It shipped.
- **The prompt in the shell only.** The image cannot be regenerated, so it cannot be revised.
- **Asking for accuracy.** Numbers, axis ticks, real equations. Generators approximate all of them.
- **Marketing register.** No style clause, so a paper figure arrives glossy, gradient-filled and 3D.
- **The variant flood.** Eight images, no criterion, and the choice now costs more than drawing it.
- **Treating a provisioning error as a bug.** `NoAvailableModels` is an access problem, and retrying
  with a different path will not fix it.

## Companions
`docs-figure` (what a figure may contain, and the vector pipelines that produce the one that ships) ·
`pptx` (the PowerPoint path, when a figure should stay editable by hand) · `writing-chatgpt` (the
same endpoint and key, for prose) · `icons8` and `icons8:ouch` (real icons and illustrations, for
when the need is a symbol rather than a scene) · `conventions` (the family index).
