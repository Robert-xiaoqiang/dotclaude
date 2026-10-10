# docs-resume resources

Placeholder templates and two scripts for the `docs-resume` skill. Every name, institution, date,
title and URL in the templates is a placeholder (`Firstname Lastname`, `University A`, `MethodA`,
`example.org`). Replace them in a copy inside your CV project, never here, because this skill
family is published.

## Files

| file | what it is | engine |
|---|---|---|
| `templates/cv-onepage.tex` | one-page English CV: extarticle 9pt, Libertinus Serif, hanging-paragraph publication list, honors beside service and skills | lualatex |
| `templates/cv-onepage-zh_CN.tex` | the Chinese sibling: the same structure retuned for CJK, Noto Serif and Sans CJK SC with a Fandol fallback, nothing below 8pt | lualatex |
| `templates/cv-dense.tex` | dense two-page English CV: article 10pt, direction sidebar beside the research focus, title-over-authors publication entries, every lab and internship entry | lualatex |
| `templates/cv-onepage-bilingual.tex` | the Overleaf root of the bilingual bundle: imports `pdf/cv-onepage.pdf` and `pdf/cv-onepage-zh_CN.pdf` and lays their links back on | lualatex (pdflatex also compiles it, but Overleaf has one compiler per project and the halves need lualatex) |
| `scripts/build-bilingual.py` | writes `pdf/<family>-bilingual-links.tex` (the bundle's link layer) and `pdf/<family>-bilingual.pdf` (a merged PDF with explicit GoTo jumps, each read back and compared with its source destination). With `--refresh` it first recompiles both halves into `pdf/`. A half that fails to compile stops it before anything is written | python3 with PyMuPDF |
| `scripts/check-cv.py` | reads a built PDF: page count, fill per page, URI and internal links, whether every `[n]` jump it can identify lands on its entry's label and stays in its language (and how many it could not identify, a failure under `--strict`), short last lines, and Overfull, Underfull and missing-character counts from the log | python3 with PyMuPDF |

The one-page templates build to one page and the dense one to two, each with no Overfull or
Underfull box, the last page filled to 93 to 98% (an earlier page is full, as TeX broke it) and
every jump landing on its entry. The three templates are one CV: the dense file carries every
fact of the one-page file, word for word, plus the lab entries and bullets the one-page variant
leaves out, and the Chinese file carries the same facts as the English one-page file. Run the
fact diff in the skill's Checks on every pair after editing any of them.

## Setting up a CV project

```sh
SKILL=<path to this skill>        # ${CLAUDE_SKILL_DIR} inside a session
cd <cv project>
cp "$SKILL"/resources/templates/*.tex .
mkdir -p scripts pdf && cp "$SKILL"/resources/scripts/*.py scripts/
```

Rename the files to your family name (`<name>-<variant>.tex`, `...-zh_CN.tex`,
`...-bilingual.tex`, with a variant such as `onepage` or `dense`) and update the
`\input{pdf/...-links.tex}` line of the bundle to match. Add a
short `scripts/README.md` saying what the two scripts do.

## Building

Build into a scratch directory so no intermediate file lands in the project.

```sh
export PATH=<texlive>/bin/x86_64-linux:$PATH
OUT=$(mktemp -d)

lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage.tex
python3 scripts/check-cv.py "$OUT/cv-onepage.pdf" --log "$OUT/cv-onepage.log" --pages 1

lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-dense.tex
python3 scripts/check-cv.py "$OUT/cv-dense.pdf" --log "$OUT/cv-dense.log" --pages 2
```

The Chinese file needs the CJK fonts Overleaf has. A local luaotfload may not index the system's
Noto CJK and then falls back to Fandol without an error. Put `NotoSerifCJKsc-Regular.otf`,
`NotoSansCJKsc-Regular.otf` and `NotoSansCJKsc-Bold.otf` in a directory and point `OSFONTDIR` at it:

```sh
export OSFONTDIR=<font dir> TEXMFVAR="$OUT/texmf-var"
lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage-zh_CN.tex
python3 scripts/check-cv.py "$OUT/cv-onepage-zh_CN.pdf" --log "$OUT/cv-onepage-zh_CN.log" --pages 1
```

The bundle reads snapshots of the two halves from `pdf/`. Refresh them and the link layer in one
step, then build the root:

```sh
python3 scripts/build-bilingual.py --family cv-onepage --refresh
lualatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" cv-onepage-bilingual.tex
python3 scripts/check-cv.py "$OUT/cv-onepage-bilingual.pdf" --pages 2
```

Without `--refresh` the link layer is read from `pdf/`, so copy freshly built halves there
first, while the merged `pdf/<family>-bilingual.pdf` is always built from the current sources.
With `--refresh` each half is compiled once, copied into `pdf/`, and both outputs are read from
those snapshots. The links file records each half's MD5, and the bundle stops with `has changed
since its link layer was generated` when a snapshot is newer than its links.

Check each half with `check-cv.py` before bundling: a half's jumps carry their destination
names, so every one is checked. The PDF-level merge keeps no names, so `check-cv.py` confirms
only the jumps drawn over an `[n]` there and reports the rest as unchecked; the bundler's own
read-back covers those.

## On Overleaf

Upload or push the `.tex` files, `pdf/` with its snapshots and links file, and nothing else built.
Set Menu, Main document to the root you want and Menu, Compiler to LuaLaTeX. Overleaf has Libertinus
and Noto CJK, so the templates need no font files in the project.
