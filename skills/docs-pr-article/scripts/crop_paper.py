#!/usr/bin/env python3
"""Cut the images a PR article needs out of a compiled paper.

A Chinese PR article carries three kinds of picture, and every one of them
already exists in the paper, so nothing is redrawn:

  header   the 论文截图: page 1 from the title down to the last author,
           affiliation or e-mail line, stopping above "Abstract". This is
           the image that sits above 论文标题 / 论文链接.
  float    one figure or table, found by its caption ("Fig. 5", "Table 1").
           The English caption is cut off, because the article writes its
           own Chinese one. Figures in most templates sit ABOVE their
           caption and tables BELOW it, which is handled.
  figure   a standalone figure PDF (the repo's figure/*.pdf), rasterised.
           Prefer this over a float crop whenever the file exists: it has
           no page furniture to trim and no neighbouring text to bleed in.

Every output is rendered at --dpi and then trimmed to its ink, so the white
margin is the same on every image whatever the source geometry was.

    crop_paper.py header <paper.pdf> <out.png>
    crop_paper.py float  <paper.pdf> <out.png> --caption "Table 1"
    crop_paper.py figure <figure.pdf> <out.png>
    crop_paper.py batch  <spec.json>

A batch spec is a list of {"kind", "src", "out", "caption"?, "dpi"?, "pad"?, "region"?}
objects, with src and out relative to the spec file's directory.
"""
import argparse
import json
import pathlib
import re
import sys

import pymupdf
from PIL import Image, ImageChops

DPI = 220
PAD_PT = 4.0          # breathing room kept around the detected region, in points
TRIM_MARGIN_PX = 18   # white border left after trimming, in pixels


def trim(img, margin=TRIM_MARGIN_PX):
    """Crop to the non-white content, then pad back a uniform margin."""
    rgb = img.convert("RGB")
    bg = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, bg).convert("L").point(lambda v: 255 if v > 12 else 0)
    box = diff.getbbox()
    if box is None:
        raise SystemExit("rendered region is blank: the crop rectangle missed the content")
    l, t, r, b = box
    l, t = max(0, l - margin), max(0, t - margin)
    r, b = min(rgb.width, r + margin), min(rgb.height, b + margin)
    return rgb.crop((l, t, r, b))


def render(page, rect, dpi):
    pix = page.get_pixmap(clip=rect, dpi=dpi, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def blocks(page):
    """Text blocks as (x0, y0, x1, y1, text), top to bottom."""
    out = [(b[0], b[1], b[2], b[3], b[4].strip()) for b in page.get_text("blocks") if b[4].strip()]
    return sorted(out, key=lambda b: (b[1], b[0]))


def is_page_number(b):
    return re.fullmatch(r"\d{1,3}", b[4]) is not None


# --------------------------------------------------------------------------- header
def crop_header(pdf, out, dpi=DPI, pad=PAD_PT):
    doc = pymupdf.open(pdf)
    page = doc[0]
    bs = [b for b in blocks(page) if not is_page_number(b)]
    stop = next((i for i, b in enumerate(bs)
                 if re.match(r"^(Abstract|ABSTRACT|摘要)\b", b[4])), None)
    if stop is None or stop == 0:
        raise SystemExit("could not find an 'Abstract' heading on page 1 to stop above")
    head = bs[:stop]
    x0 = min(b[0] for b in head) - pad
    x1 = max(b[2] for b in head) + pad
    y0 = min(b[1] for b in head) - pad
    y1 = max(b[3] for b in head) + pad
    img = trim(render(page, pymupdf.Rect(x0, y0, x1, y1), dpi))
    img.save(out)
    return out, img.size


# --------------------------------------------------------------------------- float
def find_caption(doc, label):
    """Return (page, caption_block) for the caption that starts with label."""
    pat = re.compile(r"^" + re.escape(label) + r"\s*[:.]", re.I)
    for page in doc:
        for b in blocks(page):
            if pat.match(b[4].replace("\n", " ")):
                return page, b
    raise SystemExit(f"no caption starting with {label!r} found")


def ink_boxes(page):
    """Bounding boxes of everything drawn that is not running text: vector
    paths, images and form XObjects. get_bboxlog() reports them all."""
    return [pymupdf.Rect(r) for kind, r in page.get_bboxlog()
            if not kind.endswith("text") and pymupdf.Rect(r).width > 0.5]


def crop_float(pdf, out, caption, dpi=DPI, pad=PAD_PT):
    doc = pymupdf.open(pdf)
    page, cap = find_caption(doc, caption)
    cx0, cy0, cx1, cy1 = cap[:4]
    is_table = caption.lower().startswith("tab")
    text = [b for b in blocks(page) if not is_page_number(b)]
    width_x0 = min(cx0, min(b[0] for b in text))
    width_x1 = max(cx1, max(b[2] for b in text))

    # Side-by-side floats share a band of the page. Keep the crop inside the
    # caption's own column whenever another caption sits beside it.
    neighbour = [b for b in text if b is not cap
                 and re.match(r"^(Fig\.|Figure|Table)\s*\d+", b[4])
                 and abs(b[1] - cy0) < 40]
    if neighbour:
        width_x0, width_x1 = cx0 - pad, cx1 + pad

    if is_table:
        # Table body runs from the caption's bottom to the last horizontal
        # rule below it that belongs to the same cluster of rules.
        rules = sorted((r for r in ink_boxes(page)
                        if r.height < 2.0 and r.width > 40
                        and r.y0 > cy1 - 1 and r.x1 > width_x0 and r.x0 < width_x1),
                       key=lambda r: r.y0)
        if not rules:
            raise SystemExit(f"{caption}: no table rules found below the caption")
        bottom = rules[0].y1
        for r in rules[1:]:
            if r.y0 - bottom > 140:      # a gap this big leaves the table
                break
            bottom = max(bottom, r.y1)
        x0 = min([width_x0] + [r.x0 for r in rules if r.y1 <= bottom + 0.5])
        x1 = max([width_x1] + [r.x1 for r in rules if r.y1 <= bottom + 0.5])
        rect = pymupdf.Rect(x0 - pad, cy1 + 1, x1 + pad, bottom + pad)
    else:
        # Figure body sits above its caption. Labels inside a vector figure
        # are text blocks too, so "the block above the caption" is usually a
        # node label, not prose. A body paragraph is told apart by being both
        # wide and long; the figure starts below the last one, or at the
        # topmost ink on the page when the float is at the top.
        cap_w = cx1 - cx0
        body_above = [b for b in text if b is not cap and b[3] <= cy0 + 0.5
                      and (b[2] - b[0]) > 0.65 * cap_w and len(b[4]) > 120
                      and not re.match(r"^(Fig\.|Figure|Table)\s*\d+", b[4])]
        floor = body_above[-1][3] + 1 if body_above else 0
        content = [pymupdf.Rect(b[:4]) for b in text if b is not cap and b[1] >= floor and b[3] <= cy0 + 0.5]
        content += [r for r in ink_boxes(page) if r.y0 >= floor - 0.5 and r.y1 <= cy0 + 1]
        if not content:
            raise SystemExit(f"{caption}: nothing drawn above the caption")
        top = min(r.y0 for r in content) - pad
        x0 = min([width_x0] + [r.x0 for r in content]) - pad
        x1 = max([width_x1] + [r.x1 for r in content]) + pad
        rect = pymupdf.Rect(x0, max(top, floor), x1, cy0 - 1)

    img = trim(render(page, rect, dpi))
    img.save(out)
    return out, img.size


# --------------------------------------------------------------------------- figure
def crop_figure(pdf, out, dpi=DPI, region=None):
    """region = [x0, y0, x1, y1] as fractions of the page, to cut one panel
    out of a multi-panel figure, e.g. [0, 0.6, 0.48, 1] for a bottom-left
    panel. Check the result by eye: panel boundaries are not detected."""
    page = pymupdf.open(pdf)[0]
    rect = page.rect
    if region:
        x0, y0, x1, y1 = region
        rect = pymupdf.Rect(rect.x0 + x0 * rect.width, rect.y0 + y0 * rect.height,
                            rect.x0 + x1 * rect.width, rect.y0 + y1 * rect.height)
    img = trim(render(page, rect, dpi))
    img.save(out)
    return out, img.size


# --------------------------------------------------------------------------- cli
def run_one(kind, src, out, caption=None, dpi=DPI, pad=PAD_PT, region=None):
    if kind == "header":
        return crop_header(src, out, dpi, pad)
    if kind == "float":
        if not caption:
            raise SystemExit("kind=float needs a caption")
        return crop_float(src, out, caption, dpi, pad)
    if kind == "figure":
        return crop_figure(src, out, dpi, region)
    raise SystemExit(f"unknown kind {kind!r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["header", "float", "figure", "batch"])
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--caption")
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--pad", type=float, default=PAD_PT)
    a = ap.parse_args(argv)

    if a.kind == "batch":
        spec_path = pathlib.Path(a.src).resolve()
        base = spec_path.parent
        for item in json.loads(spec_path.read_text()):
            src = str((base / item["src"]).resolve())
            out = base / item["out"]
            out.parent.mkdir(parents=True, exist_ok=True)
            path, size = run_one(item["kind"], src, str(out), item.get("caption"),
                                 item.get("dpi", a.dpi), item.get("pad", a.pad), item.get("region"))
            print(f"{item['kind']:6} {item.get('caption') or '':9} -> {item['out']}  {size[0]}x{size[1]}")
        return 0

    if not a.out:
        ap.error("out is required unless kind=batch")
    path, size = run_one(a.kind, a.src, a.out, a.caption, a.dpi, a.pad)
    print(f"{a.kind} -> {path}  {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
