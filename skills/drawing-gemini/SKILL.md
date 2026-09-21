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

Three request shapes reach three families, and the key decides which of them exist:

| family | path | models |
|---|---|---|
| OpenAI images | `{base}/images/generations` | `mr.gpt-image-2`, `gpt-image-1.5` |
| Gemini | `{root}/protocol/vertex/v1beta/models/{model}:generateContent`, `responseModalities: ["IMAGE"]` | `mr.gemini-3-pro-image-preview`, `mr.gemini-3.1-flash-image-preview` |
| Seedream | `{base}/images/generations` | `mr.doubao-seedream-5-0-260128`, `mr.doubao-seedream-4-5-251128` |

Probed on 2026-09-21 from the public domain `routify-pub.alibaba-inc.com`, **only the OpenAI family
answered**. The Gemini ids return `AllModelsFailed` and the Seedream ids return `NoAvailableModels`,
which is the router saying this key has no such model rather than the request being wrong. The
internal domains `routify.alibaba-inc.com` and `routify-online.alibaba-inc.com` are not reachable
from this host, so the fix is a provisioning request, not a code change. Re-run the probe before
assuming today matches that snapshot:

```sh
python3 $CPFS_HOME/.claude/skills/drawing-gemini/scripts/genimage.py --probe
```

The key is rate limited at 5 requests per minute for synchronous models, so the probe sleeps between
calls and a batch of generations should too.

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
