---
name: drawing-icons
description: "Find, fetch and keep the icons a figure, a deck or a page uses, one family per document: Lucide through Iconify as TikZ macros for LaTeX, Icons8 Fluency as PNGs for python-pptx figures, and every file recorded in a MANIFEST.md that can fetch the set back. Bundles cc2icon (search, get, sync, copy, check), and covers how the Icons8 MCP server reaches a session, why a script cannot use it, and what the bundled client does instead."
when_to_use: "Use when a figure, slide or page needs icons, when choosing a document's icon family, when moving icons into a project or between projects, when an icon directory holds files nobody can trace, or when setting up Icons8 on a new machine. Not for what a figure may contain (drawing-figure), how a workflow figure is laid out around its icons (drawing-workflow), or a picture generated from a prompt (drawing-gemini)."
---
# Skill: drawing-icons

## Purpose
An icon is the smallest drawing in a figure and the easiest to get wrong in bulk. Ten icons from five
families read as five documents. A PNG copied from a sibling project has no source, so nobody can
resize it, refetch it or credit it. A build script that reads icons from another directory breaks the
day that directory moves. This skill owns where icons come from, which family a document uses, and
how an icon directory stays traceable and rebuildable. It bundles `cc2icon`, which does the searching,
fetching and record keeping, so the same steps run from a session, a build script or another agent.

## Contents
- [When to Use](#when-to-use)
- [Which family, for which pipeline](#which-family-for-which-pipeline)
- [cc2icon](#cc2icon)
- [The manifest](#the-manifest)
- [Where icons live](#where-icons-live)
- [Icons8: the MCP, the plugin and the script](#icons8-the-mcp-the-plugin-and-the-script)
- [Licences](#licences)
- [Rules](#rules)
- [Anti-patterns](#anti-patterns)
- [Companions](#companions)

## When to Use
- A figure, slide or page needs icons, or an emoji or a placeholder is standing in for one.
- Choosing the icon family for a new paper, deck or site.
- Moving icons into a project, or from one project to another.
- An icon directory holds files with no record of where they came from.
- Setting up the Icons8 MCP on a new machine, or calling Icons8 from a script.

Not for what a figure may contain (`drawing-figure`), how a workflow figure is laid out around its
icons (`drawing-workflow`), or a picture generated from a prompt (`drawing-gemini`).

## Which family, for which pipeline
| pipeline | family | file | why |
|---|---|---|---|
| LaTeX deck or TikZ figure | Lucide, `lucide:` | a `.tex` macro beside its `.svg` | outline strokes that TikZ reproduces exactly, on a box with no SVG toolchain |
| python-pptx figure | Icons8 Fluency, `icons8-fluency:` | a 256 px RGBA PNG | the colour idiom the `drawing-workflow` figures were accepted in |
| HTML page or artifact | Lucide | the `.svg`, inline | free SVG under the ISC licence, and it scales with the text |

**One family per document.** A deck that mixes Lucide outlines with Fluency colour reads as two decks.
When a concept has no icon in the family, take the nearest metaphor inside the family first. If
nothing fits, fetch from outside it with a recorded reason, which `cc2icon` asks for.

## cc2icon
```sh
I=${CLAUDE_SKILL_DIR}/scripts/cc2icon.py
python3 $I search archive --family lucide                 # an Iconify prefix
python3 $I search judge --family icons8-fluency           # an Icons8 style
python3 $I get lucide:archive lucide:brain --out figures/icons
python3 $I get icons8-fluency:trophy --as benchmark --out figures/icons
python3 $I sync figures/icons                             # fetch every listed file that is missing
python3 $I copy accuracy latency --from <icon dir> --to figures/icons
python3 $I check figures/icons                            # exit status is the problem count
```

Every icon is `family:name`. A family is an Iconify prefix, written as an SVG plus a TikZ macro, or
`icons8-<style>`, written as a PNG named after the concept given with `--as`. `get` checks what it
downloaded before writing it: a PNG must carry PNG magic bytes and an alpha channel, because a failed
download can arrive as an error page with status 200 and then sits in the figure as a broken image.
It writes the file's manifest row, and refuses an icon outside the directory's family unless
`--off-family "reason"` says why.

Three things the commands do on purpose:
- **`search` on Iconify matches every word of the query**, so a list of concepts finds nothing as a
  whole. `cc2icon` then searches word by word and says so. Search one concept at a time.
- **An Icons8 name resolves through search**, because looking up an id needs an API key. The search
  output prints names in the form `get` accepts, and the manifest records the id it resolved to.
- **The TikZ converter takes stroke-drawn icons only.** A filled icon, a filled element inside a
  stroke icon, or two stroke widths in one icon are refused, because each would render wrong without
  an error. From their cached SVGs it reproduces the 16 icons of the CCPre return-offer deck byte
  for byte.

A Lucide macro in LaTeX needs `\usetikzlibrary{svg.path}` once:

```latex
\input{figures/icons/lucide-archive.tex}   % in the preamble
\iconlucidearchive{6mm}{brand}             % 6 mm square, colour `brand`, on the baseline
```

The stroke scales with the side, so an icon at 4 mm keeps the weight of one at 12 mm. Two TikZ traps
shaped the macro, and both fail without an error. TikZ's `svg` path reads absolute points and ignores
the picture's unit vectors, so the macro draws at one point per SVG unit and scales by transformation
instead. A `baseline={(x,y)}` coordinate inflates the box the same way, so the macro passes a plain
dimension. A new icon's box should come out 34.02 pt square at 12 mm in a `standalone` document.

## The manifest
Every icon directory has a `MANIFEST.md`: prose on top naming the family and the licence, then one
table with one row per file.

| concept | file | icon name (commonName) | id | style | source URL | glyph |
|---|---|---|---|---|---|---|

`get` and `copy` write the rows. The glyph column is written by hand, one line saying what the icon
looks like, because that is what a reviewer reads to tell two icons apart without opening them. A file
made by hand, such as a recolour or a raster cut from a deck, gets `-` as its URL and a glyph that
says how it was made. `cc2icon` matches columns by header name, so a manifest with an extra column,
such as a `used by`, keeps it.

**The manifest is what makes a directory rebuildable.** `sync` fetches back every row that has a URL.
The 49 fetched icons of the shared `drawing-workflow` set come back byte-identical from their rows,
and the one recolour is reported as unfetchable rather than skipped. A repository can therefore carry
the manifest and let `sync` restore the files.

## Where icons live
- **A build reads only its own project's icon directory.** Copy icons in with `copy`, never point a
  script at another project or at a skill. Five scripts that read the shared set by absolute path had
  to be repointed when its skill was renamed on 2026-10-08.
- **The shared Fluency set is `skills/drawing-workflow/resources/icons/`**, the vocabulary of every
  accepted workflow figure. Copy from it before fetching anew, so figures across papers share icons.
  Its templates look for icons in the project's own `icons/`, so a `copy` there needs no template change.
- **A directory made before its manifest** gets one by running `get` again for each of its icons.
  The files are rewritten identically, and the rows appear.

## Icons8: the MCP, the plugin and the script
- **A skill cannot carry an MCP server.** Claude Code loads servers from its settings, a project's
  `.mcp.json` or a plugin. The Icons8 server arrives with Icons8's own plugin, `icons8@icons8`, under
  Apache-2.0, which also brings the `icons8:icons8` and `icons8:ouch` skills.
- **The plugin does not travel with the dotfiles.** It is enabled in `~/.claude/settings.json`, which
  dotclaude deliberately leaves untracked, so a new machine needs it installed once:

  ```sh
  claude plugin marketplace add icons8/agent-skills
  claude plugin install icons8@icons8
  ```

  The server asks for a browser sign-in the first time a session uses it.
- **A script cannot use the MCP.** The endpoint answers 401 without that sign-in, which a script does
  not have. `cc2icon` calls the public search API the MCP wraps, and the free PNG URLs, so it needs
  no key and runs wherever curl runs. Icons8 asks anonymous callers to get an API key and has said
  anonymous access may end. When it does, `cc2icon search` stops with Icons8's message rather than
  returning nothing.
- **SVG belongs to the MCP, and this account is not entitled to it.** `get_icon_svg` needs a paid
  plan, and our account answered "does not have MCP API access". A 256 px PNG stays sharp at the half
  to one centimetre a figure uses.
- **In a session, browse with whichever is quicker, then record with `cc2icon get`.** The MCP's search
  and previews are good for choosing. A choice that is not in the manifest cannot be rebuilt. The
  plugin's own skill keeps its lock in an `icons8.json`, and ours keeps it as the manifest's family.

## Licences
- **Lucide** is ISC-licensed.
- **Icons8** icons are free with a link to icons8.com in the document, in the acknowledgements or on
  the last slide, or under a paid licence. The manifest's prose says which applies.
- **Any other Iconify set** has its own licence, listed at icon-sets.iconify.design. Read it before
  the document ships.

## Rules
1. **One family per document, held as the manifest's family.** An icon outside it carries its reason
   in the glyph column, written by `--off-family`.
2. **Every icon file has a manifest row,** with its source URL or `-` and how it was made. A file
   without a row cannot be refetched, resized or credited.
3. **A build reads only its own project's icon directory.** Icons arrive by `copy` or `get`, never by
   a path into another project or a skill.
4. **Icons are fetched through `cc2icon`, never by a bare curl.** The PNG check and the manifest row
   are the point, and a bare curl skips both.
5. **The family follows the pipeline:** Lucide for LaTeX and TikZ, Icons8 Fluency for a python-pptx
   figure.
6. **The TikZ converter is given stroke icons only.** A filled family is refused, never approximated.
7. **A document with Icons8 icons links to icons8.com,** unless a paid licence covers it.
8. **`check` passes before a figure or a deck ships.**

## Anti-patterns
- **The mixed bag.** Each icon taken from whichever family matched its search. Each pick looked best
  alone, and together they read as several documents.
- **The borrowed path.** A build script that reads icons from another project or a skill, tempting
  because the icon is already on disk. It breaks the day either directory moves.
- **The orphan PNG.** A file copied in with no row. Nobody can refetch it at another size, prove its
  licence or find it again.
- **The silent error page.** A bare curl saved an HTML or JSON error as `judge.png`, and the figure
  shows a broken image in the PDF.
- **The concept-list query.** "archive memory storage" sent to Iconify finds nothing and looks like a
  missing icon, when each word alone has several.

## Companions
`drawing-figure` (what a figure may contain, and the pipelines that draw it) · `drawing-workflow` (the
Fluency figure idiom, and the shared icon set it owns) · `docs-slides` (decks, where the Lucide macros
go) · `drawing-gemini` (a generated scene, when the need is a picture rather than a symbol) · `icons8`
and `icons8:ouch` (the plugin's skills, for choosing an Icons8 pack and for illustrations) ·
`conventions` (the family index).
