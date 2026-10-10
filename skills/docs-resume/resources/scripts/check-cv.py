#!/usr/bin/env python3
r"""Check a built CV PDF the way the docs-resume skill asks, and report what a compile log hides.

    python3 check-cv.py build/cv-onepage.pdf [--log build/cv-onepage.log] [--pages 1]
                        [--margin-top-bp 28.35] [--margin-bottom-bp 28.35] [--strict]

It prints, per file:

  pages        the page count, and a failure if --pages is given and differs
  fill         per page, how far down the text block the lowest glyph reaches (aim 93-98%)
  links        URI links and internal links read from the PDF itself
  jumps        every internal link that targets entry [n] must land on that entry's label,
               and in a bilingual bundle no jump may cross from one language half into the
               other. The entry is read from the destination name (pub:<n>, en:pub:<n>) or,
               when the link has none, from a single [n] under the link. A label is an [n]
               that starts its line and is not itself a link, so a jump that lands on a
               bullet's grey [n] tag misses. Jumps with neither a name nor an [n] under them
               (method-name jumps in a PDF-level merge) are counted as unchecked.
  short tails  the last line of a text block when it holds 1-3 Latin words or one to four
               CJK characters (punctuation not counted) and is much shorter than the block
               (a heuristic: PyMuPDF blocks are close to, not identical with, TeX paragraphs,
               so look at each one it names)
  log          Overfull, Underfull and Missing character counts when --log is given

Exit status is the number of failures (jumps that miss, a page count that differs, any
Overfull / Missing character in the log, and with --strict every unchecked jump). Short
tails and fill are reported, not counted, because the render is the final judge for those.
"""
import argparse, re, sys
import pymupdf

CJK = re.compile(r"[㐀-鿿豈-﫿]")


def visual_lines(block):
    """Lines of a PyMuPDF text block as (x0, x1, text), one per baseline.

    PyMuPDF splits a typeset line at wide gaps (a right-aligned date, the separators
    of a contact line), so pieces that share a baseline are joined back first."""
    rows = []
    for line in block.get("lines", []):
        text = "".join(span["text"] for span in line["spans"]).strip()
        if not text:
            continue
        x0, _, x1, y1 = line["bbox"]
        if rows and abs(rows[-1][3] - y1) < 2:
            r = rows[-1]
            rows[-1] = (min(r[0], x0), max(r[1], x1), r[2] + " " + text, r[3])
        else:
            rows.append((x0, x1, text, y1))
    return [(x0, x1, text) for x0, x1, text, _ in rows]


def short_tail(text):
    cjk = len(CJK.findall(text))
    if cjk:
        return cjk + len(re.findall(r"[A-Za-z0-9]+", text)) <= 4
    return len(text.split()) <= 3


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf")
    ap.add_argument("--log", help="the .log of the same build")
    ap.add_argument("--pages", type=int, help="expected page count")
    ap.add_argument("--margin-top-bp", type=float, default=None,
                    help="top margin in bp (default: the top of the highest glyph on page 1)")
    ap.add_argument("--margin-bottom-bp", type=float, default=None,
                    help="bottom margin in bp (default: equal to the top margin)")
    ap.add_argument("--strict", action="store_true",
                    help="count every internal jump whose target entry cannot be read as a failure")
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    failures = 0
    print(f"{a.pdf}: {doc.page_count} page{'s' * (doc.page_count != 1)}")
    if a.pages is not None and doc.page_count != a.pages:
        print(f"  FAIL expected {a.pages} page(s)")
        failures += 1

    first_words = doc[0].get_text("words")
    top = a.margin_top_bp if a.margin_top_bp is not None else min(w[1] for w in first_words)
    bottom = a.margin_bottom_bp if a.margin_bottom_bp is not None else top

    # Where each entry label sits: (page, y0, y1) of a word that is exactly "[n]", that
    # starts its line, and that is not itself a link. The grey [n] tags in the research
    # bullets are links and sit mid-line, so a jump that lands on one does not count.
    labels = {}
    for pno, page in enumerate(doc):
        words = page.get_text("words")
        sources = [lk["from"] for lk in page.get_links()]
        for w in words:
            m = re.fullmatch(r"\[(\d+)\]", w[4])
            if not m:
                continue
            r = pymupdf.Rect(w[:4])
            if any((s & r).get_area() > 0.5 * r.get_area() for s in sources if s.intersects(r)):
                continue
            if any(o is not w and abs(o[3] - w[3]) < 2 and o[2] <= w[0] + 0.5 for o in words):
                continue
            labels.setdefault(m.group(1), []).append((pno, w[1], w[3]))

    cjk_page = [len(CJK.findall(page.get_text())) > 50 for page in doc]
    mixed = len(set(cjk_page)) > 1
    uri = internal = missed = checked = unchecked = 0
    for pno, page in enumerate(doc):
        words = page.get_text("words")
        low = max(w[3] for w in words) if words else 0
        area = page.rect.height - top - bottom
        print(f"  page {pno + 1}: fill {100 * (low - top) / area:.1f}%")

        for lk in page.get_links():
            if lk["kind"] == pymupdf.LINK_URI:
                uri += 1
                continue
            internal += 1
            target = lk.get("page", -1)
            if target < 0:
                missed += 1
                print(f"  FAIL page {pno + 1}: internal link at {lk['from']} has no target page")
                continue
            # A bundle must never jump from one language half into the other.
            if mixed and cjk_page[pno] != cjk_page[target]:
                missed += 1
                print(f"  FAIL page {pno + 1}: jump lands on page {target + 1}, "
                      f"in the other language half")
            # Which entry should it reach? pub:<n> in a single CV, en:pub:<n> in a
            # bundle's link layer; a merged PDF keeps no names, so read the one [n]
            # under it (a CJK tag's rectangle can pick up neighbouring characters).
            name = lk.get("nameddest", "") or ""
            m = re.fullmatch(r"(?:\w+:)?pub:(\d+)", name)
            if not m:
                under = re.findall(r"\[(\d+)\]", page.get_textbox(lk["from"]))
                m = re.match(r"(\d+)", under[0]) if len(under) == 1 else None
            if not m:
                unchecked += 1
                continue
            checked += 1
            n = m.group(1)
            to = lk.get("to") or pymupdf.Point(0, 0)
            # A named destination's "to" is in PDF coordinates (y measured upwards), an
            # explicit one in MuPDF coordinates (y measured downwards).
            h = doc[target].rect.height
            y = h - to.y if lk["kind"] == pymupdf.LINK_NAMED else to.y
            hits = [l for l in labels.get(n, []) if l[0] == target and l[1] - 2 <= y + 14
                    and l[2] + 2 >= y - 14]
            if not hits:
                missed += 1
                print(f"  FAIL page {pno + 1}: jump to [{n}] lands on page {target + 1} "
                      f"at y={y:.0f}, where no [{n}] label sits")

        for block in page.get_text("dict")["blocks"]:
            lines = visual_lines(block)
            if len(lines) < 2:
                continue
            widest = max(x1 - x0 for x0, x1, _ in lines)
            right = max(x1 for _, x1, _ in lines)
            x0, x1, text = lines[-1]
            # A right-aligned date or place ends at the block's right edge; a paragraph's
            # last line ends well short of it.
            if short_tail(text) and (x1 - x0) < 0.35 * widest and right - x1 > 0.3 * widest:
                print(f"  tail page {pno + 1}: {text!r} ends a block of {len(lines)} lines")

    print(f"  links: {uri} URI, {internal} internal, {checked} jumps to [n] checked, "
          f"{missed} missed, {unchecked} unchecked (no entry name and no [n] under them)")
    failures += missed
    if a.strict and unchecked:
        print(f"  FAIL --strict: {unchecked} jump(s) could not be checked")
        failures += unchecked

    if a.log:
        log = open(a.log, encoding="utf-8", errors="replace").read()
        counts = {k: log.count(k) for k in ("Overfull", "Underfull", "Missing character")}
        print("  log: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
        failures += counts["Overfull"] + counts["Missing character"]

    sys.exit(min(failures, 125))


if __name__ == "__main__":
    main()
