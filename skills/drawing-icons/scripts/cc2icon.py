#!/usr/bin/env python3
"""cc2icon: find, fetch and keep the icons a figure, a deck or a document uses.

    cc2icon.py search QUERY [--family lucide | --family icons8-fluency] [--limit N]
    cc2icon.py get NAME... --out DIR [--as CONCEPT] [--size PX] [--off-family REASON]
    cc2icon.py sync DIR [--force]
    cc2icon.py copy CONCEPT... --from DIR --to DIR
    cc2icon.py check DIR

Every icon is `family:name`. A family is an Iconify prefix (`lucide`, `tabler`), written as an
SVG plus a TikZ macro, or `icons8-<style>` (`icons8-fluency`), written as a PNG. Every file `get`
writes gets a row in DIR/MANIFEST.md. `sync` fetches a directory back from that manifest,
`copy` moves icons between directories with their rows, and `check` reports files without a
row, rows without a file and icons outside the directory's one family.

Network access is curl, because the Iconify API refuses urllib's default user agent, and curl
honours the proxy variables the rest of this machine uses.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter

UA = "cc2icon/0.2"
ICONIFY = "https://api.iconify.design"
ICONS8_SEARCH = "https://search.icons8.com/api/iconsets/v5/search"
ICONS8_PNG = "https://img.icons8.com/?id={id}&format=png&size={size}"
HEADER = ["concept", "file", "icon name (commonName)", "id", "style", "source URL", "glyph"]
STYLE_ALIASES = {"fluent": "fluency"}       # the search API answers `fluent` for Fluency


def die(msg):
    sys.exit(f"cc2icon: {msg}")


def style_of(family):
    s = family[len("icons8-"):] if family.startswith("icons8-") else family
    return STYLE_ALIASES.get(s, s)


# ---------------------------------------------------------------- network

def fetch(url, binary=False, timeout=30):
    r = subprocess.run(["curl", "-fsSL", "--max-time", str(timeout), "-A", UA, url],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        die(f"fetch failed for {url}: {r.stderr.decode(errors='replace').strip()[:200]}")
    return r.stdout if binary else r.stdout.decode("utf-8")


def search_iconify(query, prefix, limit):
    q = urllib.parse.urlencode({"query": query, "limit": limit, "prefix": prefix})
    return [{"name": i} for i in json.loads(fetch(f"{ICONIFY}/search?{q}")).get("icons", [])]


def search_icons8(query, style, limit):
    q = urllib.parse.urlencode({"term": query, "amount": limit, "platform": style})
    d = json.loads(fetch(f"{ICONS8_SEARCH}?{q}"))
    if not d.get("success", False):
        die(f"Icons8 search refused: {d.get('message') or d}")
    return [{"name": f"icons8-{style_of(i['platform'])}:{i['commonName']}", "id": i["id"],
             "title": i["name"], "where": f"{i.get('category', '')}/{i.get('subcategory', '')}"}
            for i in d.get("icons", [])]


def resolve_icons8(family, name):
    """An Icons8 id cannot be looked up without an API key, so resolve family:name by search."""
    style = style_of(family)
    term = name.split("--")[0].replace("-", " ")
    hits = search_icons8(term, style, 100)
    for h in hits:
        if h["name"] == f"icons8-{style}:{name}":
            return h
    near = ", ".join(h["name"].split(":", 1)[1] for h in hits[:8]) or "nothing"
    die(f"no Icons8 {style} icon is called {name!r}. Search returned: {near}")


# ---------------------------------------------------------------- Lucide SVG to TikZ
# Lucide draws every icon in a 24x24 viewBox with six primitives and one set of stroke
# attributes, so this is a direct translation, not a general SVG renderer. Anything outside that
# set raises, because a silently dropped element is an icon that renders half drawn.
#
# TikZ's `svg {...}` path reads its numbers as ABSOLUTE POINTS: the picture's x= and y= unit
# vectors never reach it, so drawing shapes with x=\ccunit,y=-\ccunit puts paths and shapes in two
# grids (a 12mm icon came out 34x496pt and swallowed the slide, with no error). The coordinate
# TRANSFORMATION does reach it, so the macro draws at 1pt per SVG unit under scale=\ccscale and
# yscale=-1. `baseline={(x,y)}` resolves against the unit vectors and inflates the box the same
# way, so the macro passes a plain dimension.

NS = "{http://www.w3.org/2000/svg}"
KNOWN = {"path", "rect", "circle", "line", "polyline", "polygon", "g", "svg", "ellipse"}
RADIUS_NAMES = "ABCDEFGH"


def _num(el, key):
    v = el.get(key)
    return float(v) if v not in (None, "") else 0.0      # SVG's own initial value is 0


def _pts(el):
    vals = [float(v) for v in re.split(r"[\s,]+", (el.get("points") or "").strip()) if v]
    return list(zip(vals[0::2], vals[1::2]))


DRAWN = KNOWN - {"svg", "g"}


def _paint(root):
    """Each drawn element's effective fill, stroke and stroke-width, inherited from its ancestors
    and starting from SVG's initial values (fill black, no stroke, width 1)."""
    out = []

    def walk(el, inh):
        inh = {**inh, **{k: el.get(k) for k in ("fill", "stroke", "stroke-width")
                         if el.get(k) is not None}}
        tag = el.tag.replace(NS, "")
        if tag in DRAWN:
            out.append({**inh, "tag": tag})
        for child in el:
            walk(child, inh)

    walk(root, {"fill": "black", "stroke": "none", "stroke-width": "1"})
    return out


def element_to_tikz(el, radii):
    tag = el.tag.replace(NS, "")
    if tag in ("svg", "g"):
        return []
    if tag == "path":
        d = " ".join((el.get("d") or "").split())
        return [f"\\path[icon] svg {{{d}}};"] if d else []
    if tag == "rect":
        x, y, w, h = _num(el, "x"), _num(el, "y"), _num(el, "width"), _num(el, "height")
        opt = "[icon]"
        if el.get("rx") and float(el.get("rx")) > 0:
            r = float(el.get("rx"))
            if r not in radii:
                radii.append(r)
            opt = f"[icon,rounded corners=\\ccr{RADIUS_NAMES[radii.index(r)]}]"
        return [f"\\draw{opt} ({x},{y}) rectangle ({x + w},{y + h});"]
    if tag == "circle":
        return [f"\\draw[icon] ({_num(el,'cx')},{_num(el,'cy')}) circle ({_num(el,'r')});"]
    if tag == "ellipse":
        return [f"\\draw[icon] ({_num(el,'cx')},{_num(el,'cy')}) ellipse "
                f"({_num(el,'rx')} and {_num(el,'ry')});"]
    if tag == "line":
        return [f"\\draw[icon] ({_num(el,'x1')},{_num(el,'y1')}) -- "
                f"({_num(el,'x2')},{_num(el,'y2')});"]
    if tag in ("polyline", "polygon"):
        pts = _pts(el)
        if not pts:
            return []
        body = " -- ".join(f"({x},{y})" for x, y in pts)
        return [f"\\draw[icon] {body}{' -- cycle' if tag == 'polygon' else ''};"]
    raise ValueError(f"unhandled SVG element {tag!r}: it would render as a missing stroke")


def svg_to_tikz(svg_text, name, source):
    root = ET.fromstring(svg_text)
    # The converter draws outlines in one stroke width, so every drawn element must resolve to no
    # fill and a stroke, and all of them to the same width. Iconify puts those attributes on
    # <svg>, on a wrapping <g> or on a lone <path>, so they are resolved with SVG inheritance.
    paints = _paint(root)
    filled = sorted({p["tag"] for p in paints if p["fill"] != "none" or p["stroke"] == "none"})
    if not paints or filled:
        raise ValueError(f"{name} is not a stroke-drawn icon (filled or unstroked: {filled}); the "
                         "TikZ converter draws outlines only. Use a stroke family such as lucide "
                         "or tabler.")
    widths = {p["stroke-width"] for p in paints}
    if len(widths) != 1:
        raise ValueError(f"{name} mixes stroke widths {sorted(widths)}; the macro draws one")
    vb = root.get("viewBox")
    if not vb:
        raise ValueError(f"{name} has no viewBox, so its size is unknown")
    vb = vb.split()
    side = float(vb[2])
    stroke = float(widths.pop())
    body, radii = [], []
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        if tag not in KNOWN:
            raise ValueError(f"unhandled SVG element {tag!r} in {name}")
        body.extend(element_to_tikz(el, radii))
    macro = re.sub(r"[^a-zA-Z]", "", name)
    head = [
        f"% {name} -- fetched by cc2icon from {source}",
        f"% Drawn in the icon's own {vb[2]}x{vb[3]} grid at 1pt per unit and scaled by",
        "% \\ccscale, because TikZ's svg path parser reads absolute points and ignores",
        "% the picture's x/y unit vectors. #1 is the rendered side length, #2 the colour.",
        "% Stroke and corner radii are lengths, which no coordinate transformation",
        "% scales, so both are derived from #1 and one icon at 4mm keeps the visual",
        "% weight of another at 12mm. baseline is a plain dimension: baseline={(x,y)}",
        "% resolves against the unit vectors and blows the box up without an error.",
        f"\\newcommand{{\\icon{macro}}}[2]{{%",
        f"  {{\\pgfmathsetmacro{{\\ccscale}}{{#1/{side:.0f}pt}}%",
        f"   \\pgfmathsetlengthmacro{{\\ccstroke}}{{{stroke / side:.5f}*(#1)}}%",
        "   \\pgfmathsetlengthmacro{\\ccbase}{-0.86*(#1)}%",
    ]
    for r in radii:
        head.append(f"   \\pgfmathsetlengthmacro{{\\ccr{RADIUS_NAMES[radii.index(r)]}}}"
                    f"{{{r / side:.5f}*(#1)}}%")
    head += [
        "   \\begin{tikzpicture}[x=1pt,y=1pt,scale=\\ccscale,yscale=-1,baseline=\\ccbase,",
        "     icon/.style={draw=#2,line width=\\ccstroke,line cap=round,line join=round,fill=none}]",
        f"     \\path (0,0) rectangle ({side},{side});",
    ]
    head += ["     " + b for b in body]
    head += ["   \\end{tikzpicture}}}"]
    return "\n".join(head) + "\n"


# ---------------------------------------------------------------- PNG check

def png_info(data, what):
    """A failed download can be an HTML or JSON page with a 200, so read the PNG header itself."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        die(f"{what} is not a PNG (starts {data[:16]!r})")
    w, h = int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    ctype = data[25]
    alpha = ctype in (4, 6) or (ctype == 3 and b"tRNS" in data[:4096])
    if not alpha:
        die(f"{what} has no alpha channel (PNG colour type {ctype}), so it would sit in a white box")
    return w, h


# ---------------------------------------------------------------- the manifest

class Manifest:
    """DIR/MANIFEST.md: prose on top, then one markdown table with a `file` column.

    Columns are matched by header name, so a hand-written manifest with extra columns (a
    `used by`, a longer glyph note) keeps them. Only `file` is required."""

    def __init__(self, d):
        self.dir = pathlib.Path(d)
        self.path = self.dir / "MANIFEST.md"
        self.pre, self.post, self.head, self.rows = [], [], list(HEADER), []
        if not self.path.exists():
            return
        lines = self.path.read_text(encoding="utf-8").splitlines()
        i = next((k for k, l in enumerate(lines) if l.startswith("|")
                  and "file" in [self._clean(c).lower() for c in self._cells(l)]), None)
        if i is None:
            die(f"{self.path} has no table with a `file` column")
        self.pre, self.head = lines[:i], [self._clean(c) for c in self._cells(lines[i])]
        j = i + 2
        while j < len(lines) and lines[j].startswith("|"):
            self.rows.append(dict(zip(self.head, self._cells(lines[j]))))
            j += 1
        self.post = lines[j:]

    @staticmethod
    def _cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    @staticmethod
    def _clean(c):
        return c.strip().strip("`")

    def col(self, want):
        """The header for a field: exact name first, then any header naming a URL or a name."""
        for h in self.head:
            if h.lower() == want:
                return h
        for h in self.head:
            if want in ("url", "name") and want in h.lower():
                return h
        return None

    def raw(self, row, want):
        c = self.col(want)
        return row.get(c, "") if c else ""

    def get(self, row, want):
        return self._clean(self.raw(row, want))

    def file_of(self, row):
        return self.get(row, "file")

    def family(self):
        """The style most fetched rows share. Rows with no URL were made by hand and do not vote."""
        styles = [STYLE_ALIASES.get(self.get(r, "style"), self.get(r, "style")) for r in self.rows
                  if self.get(r, "url").startswith("http") and self.get(r, "style")]
        return Counter(styles).most_common(1)[0][0] if styles else None

    def put(self, values, extra=None):
        """Insert or replace the row for values["file"]. `values` is keyed by field (concept,
        file, name, id, style, url, glyph); `extra` by header, for columns only some manifests
        carry."""
        row = {h: "" for h in self.head}
        for h, v in (extra or {}).items():
            if h in row:
                row[h] = v
        for want, v in values.items():
            c = self.col(want)
            if c and v:
                row[c] = v
        for k, r in enumerate(self.rows):
            if self.file_of(r) == self._clean(values["file"]):
                self.rows[k] = row
                return
        self.rows.append(row)

    def save(self, intro):
        if not self.pre:
            self.pre = [f"# Icon set ({self.dir.name})", "", intro,
                        "`cc2icon.py sync` fetches every row's file back from its source URL. "
                        "Fill the glyph column by hand.", ""]
        out = list(self.pre) + ["| " + " | ".join(self.head) + " |",
                                "|" + "---|" * len(self.head)]
        out += ["| " + " | ".join(r.get(h, "") for h in self.head) + " |" for r in self.rows]
        out += self.post
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")


def licence(url):
    if "icons8.com" in url:
        return "Icons8 icons need a link to icons8.com in the document, or a paid Icons8 licence."
    if "/lucide/" in url:
        return "Lucide is ISC-licensed."
    return "Check the set's licence at icon-sets.iconify.design before publishing."


def intro(family, url):
    return f"One family: **{family}**. {licence(url)}"


# ---------------------------------------------------------------- writing one icon

def write_icon(full, out, concept, size):
    """Fetch one icon into `out`. Returns its manifest values."""
    family, _, name = full.partition(":")
    if not name:
        die(f"{full!r} is not family:name (lucide:archive, icons8-fluency:trophy)")
    if family.startswith("icons8-"):
        hit = resolve_icons8(family, name)
        url = ICONS8_PNG.format(id=hit["id"], size=size)
        data = fetch(url, binary=True)
        w, h = png_info(data, full)
        stem = concept or name
        (out / f"{stem}.png").write_bytes(data)
        print(f"{full} -> {out / (stem + '.png')} ({w}x{h}, id {hit['id']})")
        return {"concept": concept or name, "file": f"`{stem}.png`",
                "name": f"{hit['title']} (`{name}`)", "id": f"`{hit['id']}`",
                "style": style_of(family), "url": url}
    url = f"{ICONIFY}/{family}/{name}.svg"
    text = fetch(url)
    stem = f"{family}-{name}"
    try:
        tex = svg_to_tikz(text, full, url)
    except ValueError as e:
        die(str(e))
    (out / f"{stem}.svg").write_text(text, encoding="utf-8")
    (out / f"{stem}.tex").write_text(tex, encoding="utf-8")
    print(f"{full} -> {out / (stem + '.tex')}  (\\icon{re.sub(r'[^a-zA-Z]', '', full)})")
    return {"concept": concept or name, "file": f"`{stem}.tex`", "name": f"`{name}`",
            "id": f"`{full}`", "style": family, "url": url}


def check_family(m, family, off_family, full):
    lock = m.family()
    if lock and lock != style_of(family) and not off_family:
        die(f"{m.path} is locked to {lock!r}; {full} is {style_of(family)!r}. One family per "
            "document. Pass --off-family 'reason' if this icon truly has no counterpart.")


# ---------------------------------------------------------------- commands

def cmd_search(a):
    if a.family.startswith("icons8-"):
        hits = search_icons8(a.query, style_of(a.family), a.limit)
        if not hits:
            die(f"no hits for {a.query!r} in Icons8 style {style_of(a.family)!r}; an unknown "
                "style also returns nothing")
        for h in hits:
            print(f"{h['name']:<44} {h['id']:<14} {h['where']}")
    else:
        hits = search_iconify(a.query, a.family, a.limit)
        if hits:
            for h in hits:
                print(h["name"])
            return
        # Iconify matches every word of a query, so a list of concepts finds nothing as a whole
        words = a.query.split()
        if len(words) < 2:
            die(f"no hits for {a.query!r} in the Iconify set {a.family!r}")
        print(f"# no {a.family} icon matches all of {a.query!r}; by word:")
        for w in words:
            print(f"{w}: " + " ".join(h["name"] for h in search_iconify(w, a.family, a.limit)))


def cmd_get(a):
    if a.as_ and len(a.name) > 1:
        die("--as names one icon; fetch the others separately")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = Manifest(out)
    for full in a.name:
        family = full.partition(":")[0]
        check_family(m, family, a.off_family, full)
        v = write_icon(full, out, a.as_, a.size)
        if a.off_family:
            v["glyph"] = f"off-family: {a.off_family}"
        m.put(v)
        m.save(intro(family, v["url"]))


def cmd_sync(a):
    m = Manifest(a.dir)
    if not m.path.exists():
        die(f"{m.path} does not exist")
    missing = 0
    for r in m.rows:
        f, url = m.file_of(r), m.get(r, "url")
        target = m.dir / f
        if target.exists() and not a.force:
            continue
        if not url.startswith("http"):
            print(f"  {f}: no source URL ({url or 'blank'}), so it cannot be fetched", file=sys.stderr)
            missing += not target.exists()
            continue
        if f.endswith(".png"):
            data = fetch(url, binary=True)
            png_info(data, f)
            target.write_bytes(data)
        elif f.endswith(".tex"):
            text = fetch(url)
            target.with_suffix(".svg").write_text(text, encoding="utf-8")
            target.write_text(svg_to_tikz(text, m.get(r, "id") or f, url), encoding="utf-8")
        else:
            target.write_bytes(fetch(url, binary=True))
        print(f"  fetched {f}")
    print(f"{len(m.rows)} rows, {missing} could not be fetched")
    return missing


def cmd_copy(a):
    src, dst = Manifest(getattr(a, "from")), Manifest(a.to)
    if not src.path.exists():
        die(f"{src.path} does not exist, so the icons there have no record to copy")
    fields = ("concept", "file", "name", "id", "style", "url", "glyph")
    url = ""
    for want in a.concept:
        row = next((r for r in src.rows if src.get(r, "concept") == want
                    or pathlib.Path(src.file_of(r)).stem == want), None)
        if row is None:
            die(f"{want!r} is not a concept or file in {src.path}")
        f, style = src.file_of(row), STYLE_ALIASES.get(src.get(row, "style"), src.get(row, "style"))
        lock = dst.family()
        if lock and style and lock != style:
            die(f"{dst.path} is locked to {lock!r}; {f} is {style!r}")
        dst.dir.mkdir(parents=True, exist_ok=True)
        for p in [src.dir / f] + ([(src.dir / f).with_suffix(".svg")] if f.endswith(".tex") else []):
            if not p.exists():
                die(f"{p} is in the manifest but missing; run `cc2icon.py sync {src.dir}` first")
            shutil.copy2(p, dst.dir / p.name)
        dst.put({w: src.raw(row, w) for w in fields}, extra=row)
        url = url or src.get(row, "url")
        print(f"  {f} -> {dst.dir}")
    dst.save(f"One family: **{src.family()}**, copied from `{src.dir}`. {licence(url)}")


def cmd_check(a):
    m = Manifest(a.dir)
    problems = []
    if not m.path.exists():
        problems.append("no MANIFEST.md")
    listed = {m.file_of(r) for r in m.rows}
    for f in listed:
        if not (m.dir / f).exists():
            problems.append(f"{f}: listed, file missing (cc2icon.py sync)")
    for p in sorted(m.dir.iterdir()):
        if p.suffix in (".png", ".tex", ".svg") and p.name not in listed and \
           not (p.suffix == ".svg" and p.with_suffix(".tex").name in listed):
            problems.append(f"{p.name}: file has no manifest row")
    lock = m.family()
    for r in m.rows:
        s = STYLE_ALIASES.get(m.get(r, "style"), m.get(r, "style"))
        if lock and s and s != lock and m.get(r, "url").startswith("http") \
           and "off-family" not in m.get(r, "glyph"):
            problems.append(f"{m.file_of(r)}: style {s!r} in a {lock!r} set, with no off-family reason")
    for p in problems:
        print("  " + p)
    print(f"{m.dir}: {len(m.rows)} rows, family {lock!r}, {len(problems)} problem(s)")
    return len(problems)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cc2icon", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="search one family")
    s.add_argument("query")
    s.add_argument("--family", default="lucide", help="an Iconify prefix, or icons8-<style>")
    s.add_argument("--limit", type=int, default=24)
    g = sub.add_parser("get", help="fetch icons into a directory and record them")
    g.add_argument("name", nargs="+", help="family:name, e.g. lucide:archive, icons8-fluency:trophy")
    g.add_argument("--out", required=True, help="the icon directory, e.g. figures/icons")
    g.add_argument("--as", dest="as_", help="the concept this icon stands for; names an Icons8 PNG")
    g.add_argument("--size", type=int, default=256, help="Icons8 PNG side in pixels")
    g.add_argument("--off-family", help="why this icon may break the directory's one family")
    y = sub.add_parser("sync", help="fetch every manifest row whose file is missing")
    y.add_argument("dir")
    y.add_argument("--force", action="store_true", help="refetch files that exist too")
    c = sub.add_parser("copy", help="copy icons and their rows into another directory")
    c.add_argument("concept", nargs="+")
    c.add_argument("--from", required=True)
    c.add_argument("--to", required=True)
    k = sub.add_parser("check", help="report missing files, unlisted files and off-family icons")
    k.add_argument("dir")
    a = ap.parse_args(argv)
    return {"search": cmd_search, "get": cmd_get, "sync": cmd_sync,
            "copy": cmd_copy, "check": cmd_check}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(min(main(), 125))
