#!/usr/bin/env python3
r"""cc2bib: resolve and audit BibTeX entries against Semantic Scholar.

Two scenarios, one resolver.

  audit  read a .bib, verify every entry against the literature, and write a
         corrected cc2semantics.bib beside a side-by-side old -> new report
  make   resolve free-text descriptions (paper, author, method) into correct
         entries, for citing something while writing

A record is confirmed only when the normalised title is identical, the full
author list agrees in order, and the year agrees (match.py holds the rules).
Anything else is a MISMATCH, shown beside the claim and never written over it.
The earlier matcher accepted the nearest fuzzy title and any one shared
surname, and so replaced SOTOPIA with SOTOPIA-pi and InstructGPT with
InstructPatentGPT.

One exception, by the entry's own claim rather than by a search hit: an entry
that declares an arXiv id names one record, and when that record has the
identical normalised title and the year rule holds, the id identifies the
work. A full or prefix ("and others") author match is then VERIFIED from arXiv
with the record's full author list written back; differing author names are
ARXIV-FIX, the author list replaced from the record and written back, because
a title and year confirmed by the entry's own id leave the author list as the
only thing that can be wrong, and the record is the ground truth for it.

Preprints are preferred over the published version when both exist, because an
arXiv id is stable, free to resolve and always reachable by a reader.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import s2client as C  # noqa: E402
import match as M  # noqa: E402

# Fuzzy similarity never accepts anything. Below this, the nearest candidate
# is not even the same topic and the entry is reported NOT-FOUND.
NEAREST_SHOWN = 0.78


# --------------------------------------------------------------- bib parsing
def _balanced(text: str, i: int, open_ch: str = "{", close_ch: str = "}") -> int:
    """Index just past the group opening at text[i]."""
    depth = 0
    while i < len(text):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def _fields(body: str) -> dict:
    """name = {..} | "..." | bare, joined by '#', one entry at a time.
    Handles the one-line ACL Anthology dumps as well as hand-written entries."""
    out, i, n = {}, 0, len(body)
    while i < n:
        m = re.compile(r"[\s,]*([A-Za-z][\w-]*)\s*=\s*").match(body, i)
        if not m:
            break
        name, i, parts = m.group(1).lower(), m.end(), []
        while i < n:
            if body[i] == "{":
                j = _balanced(body, i)
                parts.append(body[i + 1:j - 1])
            elif body[i] == '"':
                j, depth = i + 1, 0
                while j < n and not (body[j] == '"' and depth == 0):
                    depth += (body[j] == "{") - (body[j] == "}")
                    j += 1
                parts.append(body[i + 1:j])
                j += 1
            else:
                mm = re.compile(r"[^,#}\s]+").match(body, i)
                j = mm.end() if mm else i + 1
                parts.append(body[i:j])
            i = j
            mm = re.compile(r"\s*#\s*").match(body, i)
            if not mm:
                break
            i = mm.end()
        out[name] = re.sub(r"\s+", " ", "".join(parts)).strip()
    return out


def parse_bib(text: str):
    """Brace-balanced BibTeX parser. The previous regex needed a newline
    before every closing brace, so it merged one-line entries and read the
    last field of an entry as '{2024' (the year check then silently passed)."""
    out, pos = [], 0
    head = re.compile(r"@(\w+)\s*([{(])")
    while True:
        m = head.search(text, pos)
        if not m:
            break
        close = "}" if m.group(2) == "{" else ")"
        end = _balanced(text, m.start(2), m.group(2), close)
        pos = end
        if m.group(1).lower() in ("comment", "preamble", "string"):
            continue
        inner = text[m.end():end - 1]
        key, _, body = inner.partition(",")
        out.append({"type": m.group(1), "key": key.strip(), "raw": text[m.start():end],
                    "body": body, "fields": _fields(body)})
    return out


def field(entry: dict, name: str) -> str:
    return entry["fields"].get(name, "")


# ------------------------------------------------------------------ resolve
ARXIV_RE = re.compile(r"arxiv[:\s/]*(\d{4}\.\d{4,5})", re.I)

# A blog post, a model card, a repository or a bare URL is not a citable
# source. It has no authors of record, no venue, no version a reader can pin
# and nothing to verify against, and it can be edited or removed after
# publication. Almost always the thing being cited has a paper, and that paper
# is what belongs in the bibliography.
WEB_VENUE = re.compile(
    r"\bblog\b|model card|release notes|documentation|\bdocs\b|github|gitlab|"
    r"hugging\s*face|repository|\brepo\b|website|web page|online|"
    r"technical report,\s*open|\burl\b", re.I)


def web_source(entry: dict):
    """Reason this entry is a web source rather than a paper, or None."""
    body, f = entry["raw"], entry["fields"]
    if ARXIV_RE.search(body) or "doi" in f:
        return None                      # it has a real identifier, it is a paper
    venue = next((f[k] for k in ("journal", "booktitle", "howpublished", "publisher")
                  if f.get(k)), "")
    if venue and WEB_VENUE.search(venue):
        return f"venue is {venue!r}"
    if "url" in f and not venue:
        return "url only, no venue"
    return None


def declared_arxiv(body: str):
    """An arXiv id anywhere in the entry, not only in an eprint field. Most
    entries written by hand put it in journal = {arXiv preprint arXiv:...}."""
    m = ARXIV_RE.search(body or "")
    return m.group(1) if m else None


def candidates(title: str, body: str = ""):
    """Identifier first, then title.

    An entry that names an arXiv id is claiming one specific record, so that
    record is fetched and compared. Resolving by id is authoritative and it
    catches the case a title search cannot: a real id and a real author under a
    title that was never the paper's.
    """
    out = []
    aid = declared_arxiv(body)
    if aid:
        rec = C.arxiv_by_id(aid)
        if rec:
            rec["by_id"] = True
            out.append(rec)
    hit = C.s2_match(title)
    if hit:
        out.append(hit)
    # the record the id names, when it carries the entry's title, is judged
    # before any search hit, so a title search of arXiv could add nothing the
    # judge would look at; it is skipped, which spares the paced API
    if not (out and out[0].get("by_id") and M.title_key(title) == M.title_key(out[0].get("title"))):
        out += (C.arxiv_match(title) or [])
    if not any(M.title_key(title) == M.title_key(c.get("title")) for c in out):
        out += C.crossref_match(title)
    return out


def author_requery(title: str, author: str):
    """Relevance search with the authors attached.

    The exact-title endpoint locks onto one record, and for a generic title
    such as "Quantum machine learning" that record may be a different paper
    entirely. Before calling an entry wrong, ask again with the authors.
    """
    names, _ = M.split_bib_authors(author)
    surnames = [M.name_forms(n)[0][0] for n in names[:4]]
    surnames = [x for x in surnames if x]
    if not surnames:
        return []
    return C.s2_search(f"{title} {' '.join(surnames)}", limit=5) or []


def _add_preprint_year(rec: dict):
    """A preprint and its venue carry different years (posted 2023, ICLR
    2024). Where a record has an arXiv id, its posting year is also a year of
    the record."""
    aid = (rec.get("externalIds") or {}).get("ArXiv")
    if not aid or rec.get("alt_years") is not None:
        return
    r = C.arxiv_by_id(aid)
    rec["alt_years"] = [r["year"]] if r and r.get("year") else []


WRITTEN_BACK = ("VERIFIED", "ARXIV-FIX")


def judge(claim: dict, cands: list):
    """(verdict, record, comparison) under the strict rule in match.py.

    VERIFIED    title identical, full author list in order, year agrees; or
                the entry's own arXiv id resolves to the identical title, the
                year rule holds and the entry's list is the record's, possibly
                cut short with 'and others'
    ARXIV-FIX   the entry's own arXiv id resolves to the identical title and
                the year rule holds, but the author names differ; the record's
                author list replaces the entry's
    TITLE-WRONG the entry's own arXiv id resolves to another title
    MISMATCH    the nearest record differs in title, authors or year
    NOT-FOUND   no candidate, or none even close in title
    Only VERIFIED and ARXIV-FIX are ever written back.
    """
    if not cands:
        return "NOT-FOUND", None, None
    scored = [(c, M.compare(claim, c)) for c in cands]
    for c, k in scored:
        if k["title_ok"] and k["authors_ok"] and not k["year_ok"]:
            _add_preprint_year(c)
    scored = [(c, M.compare(claim, c)) for c, _ in scored]
    # the entry's own id first: the record it names is the candidate that is
    # judged, whatever the title search returned, so a paper posted last month
    # verifies from arXiv alone
    by_id = [(c, k) for c, k in scored if c.get("by_id")]
    if by_id and by_id[0][1]["title_ok"] and by_id[0][1]["year_ok"]:
        c, k = by_id[0]
        if k["authors_ok"]:
            return "VERIFIED", c, k
        if k["authors_prefix"]:
            k["notes"].insert(0, "author list completed from the arXiv record "
                              "after 'and others'")
            k["reasons"] = []
            return "VERIFIED", c, k
        k["notes"].insert(0, "title and year confirmed by the entry's own arXiv "
                          "id; author list replaced from the arXiv record")
        return "ARXIV-FIX", c, k
    full = [(c, k) for c, k in scored if k["ok"]]
    if full:
        return "VERIFIED", full[0][0], full[0][1]
    if by_id and by_id[0][1]["title_ok"]:
        return "MISMATCH", by_id[0][0], by_id[0][1]      # own id, year fails
    if by_id and not by_id[0][1]["title_ok"] and by_id[0][1]["authors_ok"]:
        c, k = by_id[0]
        k["reasons"].insert(0, "entry's own arXiv id resolves to a different title")
        return "TITLE-WRONG", c, k
    c, k = max(scored, key=lambda ck: M.rank(ck[1]))
    if not k["title_ok"] and k["fuzzy"] < NEAREST_SHOWN:
        return "NOT-FOUND", c, k
    return "MISMATCH", c, k


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


def rewrite(e: dict, rec: dict) -> str:
    """The entry written back after a confirmed match. The entry keeps its
    own fields (title, venue, pages, note), because the title is identical
    after normalisation and the venue is what the record cannot know; the
    author list is the record's full list, and the record's ids are added
    where the entry lacks them."""
    f = dict(e["fields"])
    ids = rec.get("externalIds") or {}
    f["author"] = " and ".join(M.record_names(rec))
    if ids.get("ArXiv") and "eprint" not in f:
        f["eprint"] = ids["ArXiv"]
        f["archiveprefix"] = "arXiv"
        if not any(f.get(k) for k in ("journal", "booktitle", "howpublished")):
            f["journal"] = f"arXiv preprint arXiv:{ids['ArXiv']}"
    if ids.get("DOI") and "doi" not in f:
        f["doi"] = ids["DOI"]
    if not f.get("year") and rec.get("year"):
        f["year"] = str(rec["year"])
    pretty = {"archiveprefix": "archivePrefix", "primaryclass": "primaryClass"}
    lines = [f"@{e['type']}{{{e['key']},"]
    lines += [f"  {pretty.get(k, k)} = {{{v}}}," for k, v in f.items()]
    return "\n".join(lines) + "\n}"


def claim_of(e: dict) -> dict:
    f = e["fields"]
    ids = ", ".join(x for x in (
        f"ArXiv:{declared_arxiv(e['raw'])}" if declared_arxiv(e["raw"]) else "",
        f"DOI:{f['doi']}" if f.get("doi") else "") if x)
    return {"title": f.get("title", ""), "author": f.get("author", ""),
            "year": f.get("year", ""), "ids": ids,
            "venue": next((f[k] for k in ("booktitle", "journal", "howpublished",
                                          "publisher") if f.get(k)), "")}


# ------------------------------------------------------------------ audit
def cmd_audit(a):
    src = pathlib.Path(a.bib)
    entries = parse_bib(src.read_text())
    if a.keys:
        want = set(a.keys)
        entries = [e for e in entries if e["key"] in want]
        missing = want - {e["key"] for e in entries}
        if missing:
            sys.exit(f"keys not in {src.name}: {', '.join(sorted(missing))}")
    cited = set()
    for t in a.tex or []:
        for m in re.findall(r"\\cite[a-zA-Z]*\{([^}]*)\}", pathlib.Path(t).read_text()):
            cited |= {k.strip() for k in m.split(",")}
    rows, fixed = [], []
    for i, e in enumerate(entries, 1):
        claim = claim_of(e)
        web = web_source(e)
        if web:
            rows.append({"key": e["key"], "cited": e["key"] in cited if cited else None,
                         "verdict": "NOT-CITABLE", "reasons": [web], "claim": claim,
                         "match": None, "author_rows": [], "side_by_side_md": [],
                         "old_entry": e["raw"], "new_entry": e["raw"]})
            fixed.append(e["raw"])
            print(f"[{i:>3}/{len(entries)}] {e['key']:<28}{'NOT-CITABLE':<13}{web[:60]}", flush=True)
            continue
        cands = candidates(claim["title"], e["raw"])
        v, best, cmp = judge(claim, cands)
        if v not in WRITTEN_BACK:
            extra = author_requery(claim["title"], claim["author"])
            if extra:
                v2, best2, cmp2 = judge(claim, cands + extra)
                if v2 in WRITTEN_BACK or (cmp2 and (not cmp or M.rank(cmp2) > M.rank(cmp))):
                    v, best, cmp = v2, best2, cmp2
        # only a record that agrees on title, every author in order and year,
        # or the record the entry's own arXiv id names, may replace the
        # entry; everything else is carried through verbatim
        new = rewrite(e, best) if v in WRITTEN_BACK else e["raw"]
        source = (best or {}).get("source", "") if best else ""
        rows.append({"key": e["key"], "cited": e["key"] in cited if cited else None,
                     "verdict": v, "source": source,
                     "reasons": (cmp or {}).get("reasons", ["no candidate"]),
                     "notes": (cmp or {}).get("notes", []),
                     "claim": claim,
                     "match": ({"title": best.get("title"), "year": best.get("year"),
                                "alt_years": best.get("alt_years"),
                                "venue": best.get("venue"), "source": source,
                                "transport": best.get("transport"),
                                "ids": best.get("externalIds"),
                                "authors": M.record_names(best)} if best else None),
                     "author_rows": (cmp or {}).get("author_rows", []),
                     "side_by_side_md": M.side_by_side_md(claim, best, cmp),
                     "old_entry": e["raw"], "new_entry": new})
        fixed.append(new)
        ids = (best or {}).get("externalIds") or {}
        why = "; ".join(((cmp or {}).get("notes") or []) +
                        ([] if v in WRITTEN_BACK else (cmp or {}).get("reasons", [])))
        print(f"[{i:>3}/{len(entries)}] {e['key']:<28}{v:<13}{source or '-':<9}"
              f"{ids.get('ArXiv') or ids.get('DOI') or '-':<34} {why[:110]}", flush=True)
        if a.diff == "all" or (a.diff == "mismatch" and v not in WRITTEN_BACK):
            print(M.side_by_side(claim, best, cmp) + "\n", flush=True)
    out = pathlib.Path(a.out or (src.parent / "cc2semantics.bib"))
    out.write_text("\n\n".join(fixed) + "\n")
    rep = out.with_suffix(".report.json")
    rep.write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    write_md_report(rows, out.with_suffix(".report.md"), src, out)
    print(f"\nwrote {out}\nwrote {rep}\nwrote {out.with_suffix('.report.md')}")


def write_md_report(rows, path, src, out):
    n = len(rows)
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    L = [f"# cc2bib audit of `{src.name}`", "",
         f"{n} entries. " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())), "",
         f"Corrected file: `{out.name}`. Only VERIFIED entries (identical normalised "
         "title, full author list in order, year rule) and ARXIV-FIX entries (the "
         "entry's own arXiv id resolves to the identical title under the year rule; "
         "the author list is replaced from that record) are rewritten, keeping the "
         "entry's own fields and taking the record's full author list. Every other "
         "entry is carried through byte-identical and shown below beside the nearest "
         "record, for a person to decide. The source column names the service whose "
         "record confirmed the entry (S2, arXiv, Crossref).", "",
         "Marks: `=` identical, `~` same up to diacritics or initial format, "
         "`!` differs, `+` on one side only.", ""]
    for bad in ("NOT-CITABLE", "TITLE-WRONG", "MISMATCH", "NOT-FOUND", "ARXIV-FIX"):
        sel = [r for r in rows if r["verdict"] == bad]
        if not sel:
            continue
        L += [f"## {bad} ({len(sel)})", ""]
        for r in sel:
            cite = "" if r["cited"] is None else (" **cited**" if r["cited"] else " (uncited)")
            L += [f"### `{r['key']}`{cite}", ""]
            if r.get("source"):
                L += [f"- source: {r['source']}", ""]
            if r.get("notes"):
                L += [f"- note: {'; '.join(r['notes'])}", ""]
            if r["reasons"]:
                L += [f"- why: {'; '.join(r['reasons'])}", ""]
            L += r["side_by_side_md"] + [""]
    ok = [r for r in rows if r["verdict"] == "VERIFIED"]
    if ok:
        L += [f"## VERIFIED ({len(ok)})", "",
              "| key | source | id | written back | note |", "| --- | --- | --- | --- | --- |"]
        for r in ok:
            ids = (r["match"] or {}).get("ids") or {}
            wb = "unchanged" if r["old_entry"] == r["new_entry"] else "author list, ids"
            L.append(f"| `{r['key']}` | {r.get('source') or '-'} | "
                     f"{ids.get('ArXiv') or ids.get('DOI') or '-'} | {wb} | "
                     f"{'; '.join(r.get('notes') or [])} |")
        L += [""]
    path.write_text("\n".join(L))


# -------------------------------------------------------------------- make
def _dedupe(hits):
    """One record per work: S2, arXiv and Crossref often return the same one."""
    out = []
    for h in hits:
        if not any(M.same_work(h, o) for o in out):
            out.append(h)
    return out


def _brief(h) -> str:
    ids = h.get("externalIds") or {}
    names = M.record_names(h)
    au = "; ".join(names[:3]) + (f" +{len(names) - 3}" if len(names) > 3 else "")
    return (f"{h.get('title')} / {au} / {h.get('year')} / "
            f"{ids.get('ArXiv') or ids.get('DOI') or '-'}")


def cmd_make(a):
    """Resolve descriptions into entries. For citing while writing.

    An entry is emitted only for a record whose normalised title equals the
    query. A relevance hit with a different title (SOTOPIA-pi for SOTOPIA) is
    listed as a candidate and never emitted, so the caller reruns with the
    exact title it means. --author and --year add the strict author-order and
    year check; without them the header says authors were not checked.
    """
    out = []
    for q in a.query:
        claim = {"title": q, "author": a.author or "", "year": a.year or ""}
        hits = [C.s2_match(q)] if a.exact else C.s2_search(q, limit=a.limit)
        hits = [h for h in hits if h]
        hits += C.arxiv_match(q) or []
        if not any(M.title_key(h.get("title")) == M.title_key(q) for h in hits):
            hits += C.crossref_match(q) or []
        hits = _dedupe(hits)
        exact = [h for h in hits if M.title_key(h.get("title")) == M.title_key(q)]
        print(f"\n%% {q}")
        if not exact:
            print("%% NO EXACT TITLE. Nothing emitted. Candidates, none of them the query:")
            for h in hits[:a.limit]:
                print(f"%%   - {_brief(h)}")
            if hits and a.diff:
                print(M.side_by_side(claim, hits[0], left="query", right="nearest"))
            print("%% rerun with --exact \"<the title you mean>\" to take one")
            continue
        if a.author or a.year:
            scored = [(h, M.compare(claim, h)) for h in exact]
            for h, k in scored:
                if k["authors_ok"] and not k["year_ok"]:
                    _add_preprint_year(h)
            scored = [(h, M.compare(claim, h)) for h, _ in scored]
            if not a.year:
                ok = [(h, k) for h, k in scored if k["authors_ok"]]
            elif not a.author:
                ok = [(h, k) for h, k in scored if k["year_ok"]]
            else:
                ok = [(h, k) for h, k in scored if k["ok"]]
            if not ok:
                h, k = max(scored, key=lambda hk: M.rank(hk[1]))
                print("%% MISMATCH. Nothing emitted. " + "; ".join(
                    r for r in k["reasons"] if not r.startswith("title")))
                print(M.side_by_side(claim, h, k, left="claim", right="record"))
                continue
            h, k = ok[0]
            checked = "title exact, " + ("authors in order" if a.author else "authors not checked") \
                + (", year" if a.year else "")
        else:
            if len(exact) > 1:
                print("%% AMBIGUOUS. Several works carry this exact title. Nothing emitted; "
                      "rerun with --author to pick one:")
                for h in exact:
                    print(f"%%   - {_brief(h)}")
                continue
            h, k = exact[0], None
            checked = "title exact, authors not checked (pass --author to check order)"
        ids = h.get("externalIds") or {}
        first = (M.record_names(h) or ["anon"])[0].split()[-1].lower()
        key = re.sub(r"[^a-z]", "", M.fold(first)) + str(h.get("year", "")) + \
            re.sub(r"[^a-z0-9]", "", C.norm(h.get("title", ""))[:14].split(" ")[0])
        print(f"%% -> {h.get('title')} ({h.get('year')}, {h.get('venue')})  "
              f"[{checked}; source {h.get('source') or '-'}]")
        if ids.get("ArXiv"):
            print(f"%%    https://arxiv.org/abs/{ids['ArXiv']}")
        elif ids.get("DOI"):
            print(f"%%    https://doi.org/{ids['DOI']}")
        if a.diff:
            print(M.side_by_side(claim, h, k, left="claim", right="record"))
        print(to_bibtex(key, h))
        out.append(to_bibtex(key, h))
    if a.out:
        pathlib.Path(a.out).write_text("\n\n".join(out) + "\n")
        print(f"\nwrote {a.out}")


def main():
    p = argparse.ArgumentParser(prog="cc2bib", description=__doc__.split("\n")[0])
    p.add_argument("--debug", action="store_true",
                   help="log every request and which arXiv transport answered (also CC2BIB_DEBUG=1)")
    sub = p.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("audit", help="verify every entry in a .bib")
    pa.add_argument("bib"); pa.add_argument("--tex", nargs="*", help="mark which keys are cited")
    pa.add_argument("--out", help="default: cc2semantics.bib beside the input")
    pa.add_argument("--keys", nargs="*", help="audit only these keys, e.g. one at a time")
    pa.add_argument("--diff", choices=("none", "mismatch", "all"), default="none",
                    help="print entry and record side by side, per author")
    pa.set_defaults(fn=cmd_audit)
    pm = sub.add_parser("make", help="resolve descriptions into entries")
    pm.add_argument("query", nargs="+"); pm.add_argument("--exact", action="store_true")
    pm.add_argument("--author", help="claimed BibTeX author list, checked in order")
    pm.add_argument("--year", help="claimed year, checked")
    pm.add_argument("--diff", action="store_true", help="print claim and record side by side")
    pm.add_argument("--limit", type=int, default=5); pm.add_argument("--out")
    pm.set_defaults(fn=cmd_make)
    a = p.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if a.debug or os.environ.get("CC2BIB_DEBUG") else logging.WARNING,
        format="%(levelname)s %(message)s", stream=sys.stderr)
    a.fn(a)


if __name__ == "__main__":
    main()
