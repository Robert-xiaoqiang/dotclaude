#!/usr/bin/env python3
r"""Build both forms of a CV family's bilingual bundle: the English CV followed by the Chinese one.

A family is three files at the root of the CV project:

    <family>.tex            the English CV, a standalone document
    <family>-zh_CN.tex      the Chinese CV, a standalone document
    <family>-bilingual.tex  the Overleaf bundle, which typesets nothing itself

Run it from anywhere:

    python3 build-bilingual.py --family cv-onepage --root path/to/cv-project
    python3 build-bilingual.py --family cv-onepage --root . --refresh

It writes two files into the snapshot directory (pdf/ by default).

pdf/<family>-bilingual-links.tex is the link layer of the Overleaf bundle
<family>-bilingual.tex. That bundle stitches the two halves in pdf/ together with
pdfpages, and pdfpages imports every page as a form XObject and discards its link
annotations: the URLs on names, schools and paper titles, the mailto, and the [n]
cross-references from the experience bullets into the publication list. This script
reads those annotations from the two halves in pdf/ with PyMuPDF and writes them out as
LaTeX. For every page the bundle lays an invisible \href box over each URI link, an
invisible \hyperlink box over each internal link, and a \hypertarget at each point an
internal link jumps to. Target names are prefixed with the half (en:, zh:), so pub:3 in
the English half never resolves into the Chinese one. The file records each half's MD5,
and the bundle stops with an error when a half in pdf/ no longer matches it.

The halves in pdf/ are snapshots. Without --refresh this script reads them and never
writes them, so after editing a source, recompile it and copy its PDF into pdf/ before
running the script. With --refresh it compiles both sources first and copies the PDFs
into pdf/ itself, only once both halves have compiled cleanly.

pdf/<family>-bilingual.pdf is the same bundle merged at the PDF level, for use outside
Overleaf. Without --refresh it is built from the current sources, compiled afresh, so it
can be newer than the snapshots the link layer was read from. With --refresh it is built
from the snapshots just written, so both outputs describe the same two PDFs. Named
destinations need extra work here. Both halves define pub:1 ... pub:n, so after
concatenation the names would collide and a jump could land in the wrong language. Each
named link is therefore resolved against its own source document and rewritten as an
explicit GoTo carrying an absolute page number in the merged file, and every rewritten
jump is read back and compared with the destination it came from before the script
reports success. The merged file keeps no destination names, so check-cv.py can confirm
only the jumps drawn over an [n]; this comparison is what covers the rest.

A half that fails to compile stops the script before anything is copied or written: an
engine error, a line starting with "!" in the log, or a missing character.

Each source names its engine on its first lines (% !TeX program = lualatex), and the
script compiles it with that engine. CJK fonts are whatever the engine finds: export
OSFONTDIR (and a scratch TEXMFVAR) first if the local fonts differ from Overleaf's.
"""
import argparse, hashlib, pathlib, re, shutil, subprocess, sys, tempfile
import pymupdf

_ap = argparse.ArgumentParser(description="Build pdf/<family>-bilingual.pdf and the link "
                              "layer pdf/<family>-bilingual-links.tex of <family>-bilingual.tex.")
_ap.add_argument("--family", required=True,
                 help="the family stem: <family>.tex and <family>-zh_CN.tex must exist")
_ap.add_argument("--root", default=".", help="the CV project directory (default: .)")
_ap.add_argument("--snapshots", default="pdf",
                 help="directory under --root holding the two half PDFs (default: pdf)")
_ap.add_argument("--refresh", action="store_true",
                 help="compile both halves and copy them into the snapshot directory first")
_ARGS = _ap.parse_args()
FAMILY = _ARGS.family
ROOT = pathlib.Path(_ARGS.root).resolve()
SNAP = ROOT / _ARGS.snapshots

def engine_of(stem):
    """The engine is whatever the source's own `% !TeX program = ...` line says.

    Families do not have to agree: a dense family may be pdflatex in English and
    lualatex in Chinese while a one-page family sets its fonts through fontspec and is
    lualatex on both sides. Hard-coding one pair built a half with the wrong engine
    once two families diverged, so the comment is the only record."""
    head = (ROOT / f"{stem}.tex").read_text(encoding="utf-8", errors="replace")[:400]
    for line in head.splitlines():
        if line.lower().startswith("% !tex program"):
            return line.split("=", 1)[1].strip()
    sys.exit(f"{stem}.tex has no '% !TeX program = ...' line")

# (key, stem): the key prefixes the half's target names in the link layer and is what
# the bundle passes to \includelinkedhalf.
HALVES = [("en", FAMILY), ("zh", FAMILY + "-zh_CN")]

# ---------------------------------------------------------------- link layer for Overleaf

# A URI or a target name is written into the links file verbatim, inside a group where
# # % ~ & _ ^ $ are ordinary characters. Backslashes, braces, spaces and non-ASCII would
# still be read as TeX, so anything outside this set stops the script instead.
TEX_SAFE = re.compile(r"[!-~]+")
TEX_UNSAFE = set("\\{}")

def tex_verbatim(text, what):
    if not TEX_SAFE.fullmatch(text) or TEX_UNSAFE & set(text):
        sys.exit(f"{what} {text!r} has a character the links file cannot carry verbatim")
    return text

def num(v):
    return f"{v:.3f}"

def read_half(key, pdf):
    r"""Every link of one half, in PDF points (bp) from the lower-left corner of its page.

    Returns (page count, per-page list of (kind, target, x, y, w, h), {target name:
    (page, x, y)}). kind is "uri" with the URI as target, or "goto" with the name of the
    \hypertarget the link jumps to."""
    doc = pymupdf.open(pdf)
    pages, dests = [], {}
    for pno, page in enumerate(doc):
        box = page.mediabox
        # PyMuPDF reports rectangles from the top-left corner of the crop box. The flip
        # below is the PDF's own frame only for an unrotated page whose crop box is its
        # media box at the origin, which is what the CV sources produce.
        if page.rotation or box.x0 or box.y0 or page.cropbox != box:
            sys.exit(f"{pdf.name} page {pno + 1}: rotated or cropped page, "
                     f"its link coordinates would not map onto the imported page")
        height, links = box.height, []
        for lk in page.get_links():
            r = lk["from"]
            rect = (r.x0, height - r.y1, r.width, r.height)
            kind = lk["kind"]
            if kind == pymupdf.LINK_URI:
                links.append(("uri", tex_verbatim(lk["uri"], "URI")) + rect)
                continue
            target = lk.get("page", -1)
            if kind not in (pymupdf.LINK_NAMED, pymupdf.LINK_GOTO) or target < 0:
                sys.exit(f"{pdf.name} page {pno + 1}: link {lk} is neither a URI nor an "
                         f"internal jump, and the links file has no way to carry it")
            to = lk.get("to") or pymupdf.Point(0, 0)
            if kind == pymupdf.LINK_NAMED:
                # PyMuPDF resolves a named destination to the raw /XYZ left and top,
                # already in PDF coordinates.
                x, y = to.x, to.y
                name = lk.get("nameddest", "")
            else:
                # An explicit destination comes back in MuPDF coordinates (y downwards).
                x, y = to.x, doc[target].mediabox.height - to.y
                name = ""
            if not name or not TEX_SAFE.fullmatch(name) or TEX_UNSAFE & set(name):
                name = f"p{target + 1}:{num(x)}:{num(y)}"
            name = tex_verbatim(f"{key}:{name}", "target name")
            if dests.setdefault(name, (target, x, y)) != (target, x, y):
                sys.exit(f"{pdf.name}: destination {name} resolves to two different places")
            links.append(("goto", name) + rect)
        pages.append(links)
    return doc.page_count, pages, dests

# The macros the generated file defines. \includelinkedhalf{<key>} imports one half page
# by page with fitpaper, so the output page is the imported page and a PDF point on it is
# a picture unit with \unitlength=1bp, measured, as in the PDF, from the lower-left
# corner (where eso-pic, which pdfpages draws its pictures with, puts the origin). Each
# box is an empty \hbox of the link's width whose height comes from a zero-width rule,
# so nothing is drawn. pdflinkmargin=0pt keeps the annotation on the box itself, and
# \HyperRaiseLinkDefault=0pt stops hyperref lifting a \hypertarget by a \baselineskip.
LINKS_MACROS = r"""\RequirePackage{pdftexcmds}
\hypersetup{pdfborder={0 0 0},pdflinkmargin=0pt}
\makeatletter
\newcommand*\includelinkedhalf[1]{%
  \@ifundefined{cvlinks/#1/import}%
    {\PackageError{bilingual-links}{No half `#1' in this links file}%
       {The halves are: @HALVES@.}}%
    {\csname cvlinks/#1/import\endcsname}}
\newcommand*\cvlinks@half[3]{% key, PDF, MD5 it was read with
  \expandafter\gdef\csname cvlinks/#1/file\endcsname{#2}%
  \expandafter\gdef\csname cvlinks/#1/import\endcsname{}%
  \edef\cvlinks@md5{\pdf@filemdfivesum{#2}}%
  \ifx\cvlinks@md5\@empty
    \PackageWarningNoLine{bilingual-links}{This engine cannot checksum #2,
      so a link layer that no longer matches it would go unnoticed}%
  \else\ifnum\pdf@strcmp{\cvlinks@md5}{#3}=\z@\else
    \PackageError{bilingual-links}{#2 has changed since its link layer was generated}%
      {Its links would land on the wrong text. Rerun
       build-bilingual.py --family @FAMILY@, which rewrites @LINKS@.}%
  \fi\fi}
\newcommand\cvlinks@page[3]{% key, page, overlay
  \expandafter\gdef\csname cvlinks/#1/#2\endcsname{#3}%
  \expandafter\g@addto@macro\csname cvlinks/#1/import\endcsname
    {\cvlinks@import{#1}{#2}}}
\newcommand*\cvlinks@import[2]{%
  \edef\cvlinks@call{\noexpand\includepdf[pages=#2,fitpaper,
    picturecommand*={\noexpand\cvlinks@overlay{#1}{#2}}]{\csname cvlinks/#1/file\endcsname}}%
  \cvlinks@call}
\newcommand*\cvlinks@overlay[2]{%
  \setlength\unitlength{1bp}%
  \def\HyperRaiseLinkDefault{\z@}%
  \csname cvlinks/#1/#2\endcsname}
\newcommand*\cvlinks@box[2]{%
  \hbox to #1\unitlength{\vrule width\z@ height #2\unitlength depth\z@\hss}}
\newcommand*\cvlinks@uri[5]{\put(#1,#2){\href{#5}{\cvlinks@box{#3}{#4}}}}
\newcommand*\cvlinks@goto[5]{\put(#2,#3){\hyperlink{#1}{\cvlinks@box{#4}{#5}}}}
\newcommand*\cvlinks@dest[3]{\put(#2,#3){\hypertarget{#1}{}}}
\makeatother
"""

def write_links_tex():
    """Write pdf/<family>-bilingual-links.tex from the two halves in pdf/."""
    pdfs = [(key, SNAP / f"{stem}.pdf") for key, stem in HALVES]
    missing = [p.relative_to(ROOT).as_posix() for _, p in pdfs if not p.is_file()]
    if missing:
        sys.exit("cannot write the link layer, missing: " + ", ".join(missing) +
                 f"\n  compile each half and copy its PDF into {SNAP.name}/ first, or pass --refresh")
    out = SNAP / f"{FAMILY}-bilingual-links.tex"
    rel_out = out.relative_to(ROOT).as_posix()

    header, body, total = [], [], {"uri": 0, "goto": 0}
    for key, pdf in pdfs:
        rel = pdf.relative_to(ROOT).as_posix()
        md5 = hashlib.md5(pdf.read_bytes()).hexdigest().upper()
        n, pages, dests = read_half(key, pdf)
        if n == 0:
            sys.exit(f"{rel} has no pages")
        count = {"uri": 0, "goto": 0}
        body.append(f"\\cvlinks@half{{{key}}}{{{rel}}}{{{md5}}}")
        for pno, links in enumerate(pages):
            body.append(f"\\cvlinks@page{{{key}}}{{{pno + 1}}}{{")
            for name, (target, x, y) in sorted(dests.items()):
                if target == pno:
                    body.append(f"\\cvlinks@dest{{{name}}}{{{num(x)}}}{{{num(y)}}}")
            for kind, target, x, y, w, h in links:
                count[kind] += 1
                if kind == "uri":
                    body.append(f"\\cvlinks@uri{{{num(x)}}}{{{num(y)}}}{{{num(w)}}}"
                                f"{{{num(h)}}}{{{target}}}")
                else:
                    body.append(f"\\cvlinks@goto{{{target}}}{{{num(x)}}}{{{num(y)}}}"
                                f"{{{num(w)}}}{{{num(h)}}}")
            body.append("}")
        header.append(f"%   {key}  {rel}  {n} page{'s' * (n > 1)}, {count['uri']} URI "
                      f"links, {count['goto']} internal links, {len(dests)} targets\n"
                      f"%       MD5 {md5}")
        for k in total:
            total[k] += count[k]

    text = "\n".join([
        f"% {rel_out}",
        f"% GENERATED by build-bilingual.py --family {FAMILY}. Do not edit by hand.",
        "%",
        f"% The link layer of {FAMILY}-bilingual.tex. pdfpages drops the link annotations",
        "% of every page it imports, so this file lays them back on. Each page gets an",
        "% invisible \\href box over every URI link, an invisible \\hyperlink box over every",
        "% internal link, and a \\hypertarget wherever an internal link jumps to. Positions",
        "% are PDF points (bp) from the lower-left corner of the page. Target names start",
        "% with the half (en:, zh:), so the two halves never share one.",
        "%",
        "% Read from the halves below. The bundle checks their MD5 when it compiles and",
        "% stops with an error if either has changed, so after refreshing a half in pdf/,",
        "% rerun the script before compiling.",
        *header,
        "%",
        "% Between \\begingroup and \\endgroup below, # % ~ & _ ^ $ are ordinary characters",
        "% so that URIs can be copied verbatim, and line ends are ignored. A comment cannot",
        "% go in there.",
        LINKS_MACROS.replace("@FAMILY@", FAMILY).replace("@LINKS@", rel_out)
                    .replace("@HALVES@", ", ".join(k for k, _ in HALVES)).rstrip("\n"),
        r"\begingroup",
        r"\catcode`\@=11 \catcode`\#=12 \catcode`\%=12 \catcode`\~=12 \catcode`\&=12",
        r"\catcode`\_=12 \catcode`\^=12 \catcode`\$=12 \endlinechar=-1",
        *body,
        r"\endgroup",
        "",
    ])
    out.write_text(text, encoding="ascii")
    print(f"wrote {rel_out}  uri={total['uri']}  cross-refs={total['goto']}")

# ---------------------------------------------------------------- merged PDF

def compile_one(stem, engine, workdir):
    """Compile one half (two runs) and stop the script on any error.

    nonstopmode alone runs past an undefined macro and still writes a PDF, which was
    then snapshotted, linked and merged with exit status 0. So the engine halts on the
    first error, and its exit status, every log line starting with "!" and every
    missing character each stop the script, as they fail check-cv.py."""
    for _ in range(2):
        r = subprocess.run(
            [engine, "-interaction=nonstopmode", "-halt-on-error",
             f"-output-directory={workdir}", str(ROOT / f"{stem}.tex")],
            capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            break
    pdf, logf = workdir / f"{stem}.pdf", workdir / f"{stem}.log"
    log = logf.read_text(errors="replace") if logf.is_file() else ""
    lines = log.splitlines()
    errors = [i for i, line in enumerate(lines) if line.startswith("!")]
    missing = log.count("Missing character")
    if r.returncode != 0 or errors or missing or not pdf.is_file():
        # Each error with the lines TeX prints after it (where it happened), or else
        # the missing characters, or else the end of the log.
        shown = [line for i in errors for line in lines[i:i + 4]] or \
                [line for line in lines if "Missing character" in line][:10] or lines[-20:]
        tail = "\n".join(shown) or r.stdout[-2000:]
        sys.exit(f"{stem}: {engine} failed (exit {r.returncode}, {len(errors)} error "
                 f"line(s), {missing} missing character(s)); nothing was copied or "
                 f"written\n{tail}")
    boxes = sum(log.count(k) for k in ("Overfull", "Underfull"))
    print(f"  {stem:32s} {engine:9s} {pymupdf.open(pdf).page_count}p  boxes={boxes}")
    return pdf

def write_merged_pdf(pdfs):
    """Merge the two half PDFs, English first, into pdf/<family>-bilingual.pdf."""
    merged = pymupdf.open()
    offsets, saved = [], []
    for path in pdfs:
        doc = pymupdf.open(path)
        offsets.append(merged.page_count)
        # capture links now: the source resolves its own named destinations
        saved.append([doc[i].get_links() for i in range(doc.page_count)])
        merged.insert_pdf(doc)
        doc.close()

    restored, expected = 0, []
    for off, per_page in zip(offsets, saved):
        for i, links in enumerate(per_page):
            page = merged[off + i]
            for lk in links:
                if lk.get("kind") != pymupdf.LINK_NAMED:
                    continue          # URI links survive insert_pdf untouched
                target = lk.get("page")
                if target is None or target < 0:
                    continue
                # A named destination's "to" is in PDF coordinates (y upwards), but
                # insert_link takes MuPDF coordinates (y downwards) and flips them, so
                # passing it through unchanged mirrored every jump about the middle.
                to = lk.get("to") or pymupdf.Point(0, 0)
                dest = merged[off + target]
                point = pymupdf.Point(to.x, dest.mediabox.height - to.y)
                page.insert_link({"kind": pymupdf.LINK_GOTO, "from": lk["from"],
                                  "page": off + target, "to": point})
                expected.append((off + i, lk["from"], off + target, to.y,
                                 lk.get("nameddest", "")))
                restored += 1

    # The bundle takes the English half's own title and author, so no name is
    # written into this script.
    meta = pymupdf.open(pdfs[0]).metadata or {}
    title = meta.get("title") or FAMILY
    merged.set_metadata({"title": f"{title} (English and Chinese)",
                         "author": meta.get("author") or ""})
    out = SNAP / f"{FAMILY}-bilingual.pdf"
    out.parent.mkdir(exist_ok=True)
    merged.save(out, garbage=3, deflate=True)

    chk = pymupdf.open(out)
    uri = sum(1 for i in range(chk.page_count) for l in chk[i].get_links()
              if l.get("kind") == pymupdf.LINK_URI)
    goto = sum(1 for i in range(chk.page_count) for l in chk[i].get_links()
               if l.get("kind") == pymupdf.LINK_GOTO)
    print(f"wrote {out.relative_to(ROOT)}  {chk.page_count}p  "
          f"url={uri}  cross-refs={goto} (restored {restored})")
    if goto != restored:
        sys.exit("cross-reference count does not match what was restored")
    # Read every rewritten jump back and compare it, in PDF coordinates, with the
    # named destination it was resolved from in its own half: the right page, the
    # same height, from the same rectangle. An explicit GoTo reads back in MuPDF
    # coordinates (y downwards), so a jump written without the flip fails here.
    wrong = []
    for pno, rect, target, src_y, name in expected:
        height = chk[target].mediabox.height
        if not any(l.get("kind") == pymupdf.LINK_GOTO and l.get("page") == target
                   and abs(l["from"].x0 - rect.x0) < 0.5
                   and abs(l["from"].y0 - rect.y0) < 0.5
                   and abs(height - (l.get("to") or pymupdf.Point(0, 0)).y - src_y) < 1.0
                   for l in chk[pno].get_links()):
            wrong.append(f"page {pno + 1} {name or '?'} -> page {target + 1}")
    if wrong:
        sys.exit(f"{len(wrong)} rewritten jump(s) do not land where their source "
                 f"destination is:\n  " + "\n  ".join(wrong))
    print(f"  all {restored} rewritten jumps land on their source destinations")

def refresh_snapshots():
    """Compile both halves, then copy both PDFs into the snapshot directory.

    Both compile before either is copied, so a failing half never leaves pdf/ holding
    one new snapshot and one old one. Returns the snapshot paths."""
    SNAP.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        print(f"refreshing {SNAP.name}/")
        built = [(stem, compile_one(stem, engine_of(stem), work)) for _, stem in HALVES]
        for stem, pdf in built:
            shutil.copyfile(pdf, SNAP / f"{stem}.pdf")
    return [SNAP / f"{stem}.pdf" for _, stem in HALVES]

def main():
    missing = [f"{stem}.tex" for _, stem in HALVES if not (ROOT / f"{stem}.tex").is_file()]
    if missing:
        sys.exit(f"{ROOT}: missing " + ", ".join(missing))
    if _ARGS.refresh:
        # Compiled once: the link layer and the merged PDF both read the new snapshots.
        snapshots = refresh_snapshots()
        write_links_tex()
        write_merged_pdf(snapshots)
        return
    write_links_tex()
    with tempfile.TemporaryDirectory() as tmp:
        print("compiling halves for the merged PDF (the link layer read pdf/)")
        write_merged_pdf([compile_one(stem, engine_of(stem), pathlib.Path(tmp))
                          for _, stem in HALVES])

if __name__ == "__main__":
    main()
