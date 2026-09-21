#!/usr/bin/env python3
r"""cc2bib: resolve and audit BibTeX entries against Semantic Scholar.

Two scenarios, one resolver.

  audit  read a .bib, verify every entry against the literature, and write a
         corrected cc2semantics.bib beside a side-by-side old -> new report
  make   resolve free-text descriptions (paper, author, method) into correct
         entries, for citing something while writing

A record is confirmed only when the title matches AND the author list agrees.
An exact-title query for "Quantum machine learning" returns a 2025 arXiv
preprint, not the 2017 Nature paper an entry may claim, so title similarity
alone would certify the wrong record.

Preprints are preferred over the published version when both exist, because an
arXiv id is stable, free to resolve and always reachable by a reader.
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import s2client as C  # noqa: E402

TITLE_OK, TITLE_MAYBE, YEAR_TOL = 0.93, 0.78, 2


# --------------------------------------------------------------- bib parsing
def parse_bib(text: str):
    out = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", text, re.S):
        out.append({"type": m.group(1), "key": m.group(2).strip(),
                    "raw": m.group(0), "body": m.group(3)})
    return out


def field(body: str, name: str) -> str:
    m = (re.search(rf"\b{name}\s*=\s*\{{(.+?)\}},?\s*\n", body, re.S)
         or re.search(rf"\b{name}\s*=\s*\"(.+?)\",?\s*\n", body, re.S)
         or re.search(rf"\b{name}\s*=\s*([^,\n}}]+)", body))
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


# ------------------------------------------------------------------ resolve
def candidates(title: str):
    """S2 first, then arXiv and Crossref, so an S2 outage degrades rather than stops."""
    out = []
    hit = C.s2_match(title)
    if hit:
        out.append(hit)
    out += (C.arxiv_match(title) or [])
    if not any(difflib.SequenceMatcher(None, C.norm(title), C.norm(c["title"])).ratio() >= TITLE_OK
               for c in out):
        out += C.crossref_match(title)
    return out


def judge(title, author, year, cands):
    best, sim = None, 0.0
    for c in cands:
        s = difflib.SequenceMatcher(None, C.norm(title), C.norm(c.get("title", ""))).ratio()
        if s > sim:
            best, sim = c, s
    if best is None:
        return "NOT-FOUND", 0.0, None, "no candidate from any source"
    want, got = C.bib_surnames(author), C.surnames(best.get("authors"))
    # a corporate author such as "Meta AI" has no surname to match on
    corporate = want <= {"ai", "team", "inc", "labs", "research"} or not want
    author_ok = corporate or bool(want & got)
    notes = []
    if not author_ok:
        notes.append(f"authors {sorted(want)[:3]} vs {sorted(got)[:3]}")
    dy = 0
    try:
        if year and best.get("year"):
            dy = abs(int(year) - int(best["year"]))
    except (TypeError, ValueError):
        dy = 0
    if dy > YEAR_TOL:
        notes.append(f"year {year} vs {best['year']}")
    if sim < TITLE_MAYBE:
        v = "NOT-FOUND"
    elif sim < TITLE_OK:
        v = "REVIEW"
    elif not author_ok:
        v = "WRONG-RECORD"
    elif dy > YEAR_TOL:
        v = "REVIEW"
    else:
        v = "VERIFIED"
    if corporate and v == "VERIFIED" and want:
        notes.append("corporate author, not cross-checked")
    return v, sim, best, "; ".join(notes)


# ------------------------------------------------------------------- emit
def to_bibtex(key, rec, kind="article"):
    """One entry, preferring the arXiv id so the reference always resolves."""
    ids = rec.get("externalIds") or {}
    auth = " and ".join(a["name"] for a in (rec.get("authors") or []))
    lines = [f"@{kind}{{{key},",
             f"  title = {{{rec.get('title','')}}},",
             f"  author = {{{auth}}},"]
    if ids.get("ArXiv"):
        lines.append(f"  journal = {{arXiv preprint arXiv:{ids['ArXiv']}}},")
        lines.append(f"  eprint = {{{ids['ArXiv']}}},")
        lines.append("  archivePrefix = {arXiv},")
    elif rec.get("venue"):
        lines.append(f"  journal = {{{rec['venue']}}},")
    if rec.get("year"):
        lines.append(f"  year = {{{rec['year']}}},")
    if ids.get("DOI"):
        lines.append(f"  doi = {{{ids['DOI']}}},")
    lines.append("}")
    return "\n".join(lines)


# ------------------------------------------------------------------ audit
def cmd_audit(a):
    src = pathlib.Path(a.bib)
    entries = parse_bib(src.read_text())
    cited = set()
    for t in a.tex or []:
        for m in re.findall(r"\\cite[a-zA-Z]*\{([^}]*)\}", pathlib.Path(t).read_text()):
            cited |= {k.strip() for k in m.split(",")}
    rows, fixed = [], []
    for i, e in enumerate(entries, 1):
        t, au, yr = field(e["body"], "title"), field(e["body"], "author"), field(e["body"], "year")
        v, sim, best, notes = judge(t, au, yr, candidates(t))
        new = to_bibtex(e["key"], best, e["type"]) if best and v in ("VERIFIED", "REVIEW") else e["raw"]
        rows.append({"key": e["key"], "cited": e["key"] in cited if cited else None,
                     "verdict": v, "sim": round(sim, 3), "notes": notes,
                     "claim": {"title": t, "author": au, "year": yr},
                     "match": ({"title": best.get("title"), "year": best.get("year"),
                                "venue": best.get("venue"),
                                "ids": best.get("externalIds"),
                                "authors": [x["name"] for x in (best.get("authors") or [])][:6]}
                               if best else None),
                     "old_entry": e["raw"], "new_entry": new})
        fixed.append(new)
        print(f"[{i:>3}/{len(entries)}] {e['key']:<28}{v:<14}{sim:.2f}  "
              f"{(best.get('externalIds') or {}).get('ArXiv') or (best.get('externalIds') or {}).get('DOI') or '-' if best else '-'}",
              flush=True)
    out = pathlib.Path(a.out or (src.parent / "cc2semantics.bib"))
    out.write_text("\n\n".join(fixed) + "\n")
    rep = out.with_suffix(".report.json")
    rep.write_text(json.dumps(rows, indent=1))
    write_md_report(rows, out.with_suffix(".report.md"), src, out)
    print(f"\nwrote {out}\nwrote {rep}\nwrote {out.with_suffix('.report.md')}")


def write_md_report(rows, path, src, out):
    n = len(rows)
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    L = [f"# cc2bib audit of `{src.name}`", "",
         f"{n} entries. " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())), "",
         f"Corrected file: `{out.name}`. Entries marked NOT-FOUND or WRONG-RECORD are "
         "carried through unchanged, because inventing a replacement is the failure "
         "this audit exists to catch.", ""]
    for bad in ("NOT-FOUND", "WRONG-RECORD", "REVIEW"):
        sel = [r for r in rows if r["verdict"] == bad]
        if not sel:
            continue
        L += [f"## {bad} ({len(sel)})", ""]
        for r in sel:
            cite = "" if r["cited"] is None else (" **cited**" if r["cited"] else " (uncited)")
            L += [f"### `{r['key']}`{cite}  sim={r['sim']}", "",
                  f"- claimed: {r['claim']['title']} / {r['claim']['author'][:70]} / {r['claim']['year']}"]
            if r["match"]:
                m = r["match"]
                L += [f"- matched: {m['title']} / {'; '.join(m['authors'][:3])} / {m['year']} / {m['venue']}",
                      f"- ids: {m['ids']}"]
            if r["notes"]:
                L += [f"- why: {r['notes']}"]
            L += [""]
    ok = [r for r in rows if r["verdict"] == "VERIFIED" and r["old_entry"] != r["new_entry"]]
    if ok:
        L += [f"## VERIFIED with field corrections ({len(ok)})", "",
              "| key | field change |", "| --- | --- |"]
        for r in ok:
            ids = (r["match"] or {}).get("ids") or {}
            gained = "adds " + ", ".join(k for k in ("ArXiv", "DOI") if ids.get(k)) if ids else "metadata"
            L.append(f"| `{r['key']}` | {gained} |")
        L += [""]
    path.write_text("\n".join(L))


# -------------------------------------------------------------------- make
def cmd_make(a):
    """Resolve free-text descriptions into entries. For citing while writing."""
    out = []
    for q in a.query:
        hits = [C.s2_match(q)] if a.exact else C.s2_search(q, limit=a.limit)
        hits = [h for h in hits if h]
        if not hits:
            hits = C.arxiv_match(q) or []
        if not hits:
            print(f"NO MATCH: {q}"); continue
        h = hits[0]
        ids = h.get("externalIds") or {}
        first = (h.get("authors") or [{}])[0].get("name", "anon").split()[-1].lower()
        key = re.sub(r"[^a-z]", "", first) + str(h.get("year", "")) + \
            re.sub(r"[^a-z0-9]", "", C.norm(h.get("title", ""))[:14].split(" ")[0])
        print(f"\n%% {q}\n%% -> {h.get('title')} ({h.get('year')}, {h.get('venue')})")
        if ids.get("ArXiv"):
            print(f"%%    https://arxiv.org/abs/{ids['ArXiv']}")
        elif ids.get("DOI"):
            print(f"%%    https://doi.org/{ids['DOI']}")
        print(to_bibtex(key, h))
        out.append(to_bibtex(key, h))
    if a.out:
        pathlib.Path(a.out).write_text("\n\n".join(out) + "\n")
        print(f"\nwrote {a.out}")


def main():
    p = argparse.ArgumentParser(prog="cc2bib", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("audit", help="verify every entry in a .bib")
    pa.add_argument("bib"); pa.add_argument("--tex", nargs="*", help="mark which keys are cited")
    pa.add_argument("--out", help="default: cc2semantics.bib beside the input")
    pa.set_defaults(fn=cmd_audit)
    pm = sub.add_parser("make", help="resolve descriptions into entries")
    pm.add_argument("query", nargs="+"); pm.add_argument("--exact", action="store_true")
    pm.add_argument("--limit", type=int, default=5); pm.add_argument("--out")
    pm.set_defaults(fn=cmd_make)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
