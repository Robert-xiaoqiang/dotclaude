#!/usr/bin/env python3
r"""Strict comparison of a claimed reference against a looked-up record.

A candidate record is the claimed paper only when all three agree:

  title    the normalised titles are identical. Normalising folds case, LaTeX
           braces and commands, accents and punctuation, and nothing else, so a
           different subtitle or an extra suffix ("SOTOPIA" versus "SOTOPIA-pi")
           is a mismatch, never a near miss
  authors  the full lists have the same length and agree position by position,
           each pair on surname and on given names, where only diacritics and
           initial format may differ ("Jeffrey", "J.", "J" agree; "Jeff" and
           "Jeffrey" do not)
  year     the claimed year is a year of the record

There is no similarity threshold on the accept path. The previous matcher
accepted the nearest fuzzy title and any shared surname, which let it replace
SOTOPIA with SOTOPIA-pi and InstructGPT with InstructPatentGPT. Fuzzy
similarity survives only for choosing which non-matching candidate to show
beside the claim in a report.

Pure functions, no network, so the rules can be tested offline.
"""
from __future__ import annotations

import difflib
import re
import shutil
import textwrap
import unicodedata

# ---------------------------------------------------------------- folding
# \'e, \"{o} are symbol accents; \c{c}, \v s are letter accents and must not
# swallow the start of \textit or \cite
_ACCENT = re.compile(r"\\(?:[`'^\"~=.]|[uvHtcdbkr](?![A-Za-z]))\s*"
                     r"(?:\{\s*\\?([A-Za-z])\s*\}|\\?([A-Za-z]))")
_LETTER = {"ss": "ss", "ae": "ae", "AE": "AE", "oe": "oe", "OE": "OE",
           "aa": "a", "AA": "A", "o": "o", "O": "O", "l": "l", "L": "L",
           "i": "i", "j": "j"}
_GREEK = ("alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota "
          "kappa lambda mu nu xi omicron pi varpi rho varrho sigma varsigma tau "
          "upsilon phi varphi chi psi omega").split()
_SPECIAL = {"ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "đ": "d", "Đ": "D",
            "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "ı": "i",
            "þ": "th", "Þ": "Th", "ð": "d"}


def detex(s: str) -> str:
    """LaTeX to plain text: accents to their base letter, greek commands to
    their names, formatting commands and braces dropped."""
    s = s or ""
    s = _ACCENT.sub(lambda m: m.group(1) or m.group(2), s)
    s = re.sub(r"\\(ss|ae|AE|oe|OE|aa|AA|o|O|l|L|i|j)(?![A-Za-z])",
               lambda m: _LETTER[m.group(1)], s)
    s = re.sub(r"\\(?:var)?(" + "|".join(_GREEK) + r")(?![A-Za-z])",
               lambda m: m.group(1).lower(), s, flags=re.I)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)      # \emph, \textsc, \ensuremath ...
    s = re.sub(r"\\(.)", r"\1", s)              # \& \% \_
    s = s.replace("~", " ")
    return re.sub(r"[{}$]", "", s)


def fold(s: str) -> str:
    """detex, then drop diacritics, spell greek letters, lowercase."""
    s = detex(s)
    out = []
    for ch in unicodedata.normalize("NFKD", s):
        if unicodedata.combining(ch):
            continue
        if ch in _SPECIAL:
            out.append(_SPECIAL[ch])
            continue
        name = unicodedata.name(ch, "")
        if name.startswith("GREEK") and "LETTER" in name:
            out.append(" " + name.split()[-1].lower() + " ")
            continue
        out.append(ch)
    return "".join(out).lower()


def title_key(t: str) -> str:
    """Case, braces, LaTeX, accents, punctuation and spacing folded away.
    Every letter and digit is kept, so any wording difference survives."""
    return re.sub(r"[^a-z0-9]", "", fold(t))


def year_of(y) -> str:
    m = re.search(r"\d{4}", str(y or ""))
    return m.group(0) if m else ""


# ------------------------------------------------------------------ names
_SUFFIX = {"jr", "sr", "ii", "iii", "iv"}


def _split_top(s: str, sep_re: str):
    """Split on a separator regex only at brace depth 0."""
    parts, depth, cur, i = [], 0, [], 0
    pat = re.compile(sep_re, re.I)
    while i < len(s):
        ch = s[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if depth == 0:
            m = pat.match(s, i)
            if m:
                parts.append("".join(cur))
                cur, i = [], m.end()
                continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return [p.strip() for p in parts]


def split_bib_authors(field: str):
    """BibTeX author field to (names, truncated). 'and others' truncates."""
    field = re.sub(r"\s+", " ", field or "").strip()
    if not field:
        return [], False
    names = [n for n in _split_top(field, r"\s+and\s+") if n]
    truncated = bool(names) and names[-1].lower() in ("others", "et al", "et al.")
    if truncated:
        names = names[:-1]
    return names, truncated


def _wrapped(s: str) -> bool:
    """True when the whole string is one brace group, e.g. {Qwen Team}."""
    s = s.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return False
    depth = 0
    for i, ch in enumerate(s):
        depth += ch == "{"
        depth -= ch == "}"
        if depth == 0 and i < len(s) - 1:
            return False
    return True


def _initials(given: str):
    """Given names as folded tokens; a one-letter token is an initial."""
    toks = re.split(r"[\s.\-]+", fold(given))
    return tuple(re.sub(r"[^a-z0-9]", "", t) for t in toks if re.sub(r"[^a-z0-9]", "", t))


def _skey(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold(s))


def name_forms(raw: str):
    """Every (surname key, initials) reading of one name.

    'Last, First' and 'von Last, Jr, First' are unambiguous. 'First Last', the
    form every API returns, is read at every split point, so 'Benjamin Van
    Durme' can meet 'Van Durme, Benjamin'. A name wrapped whole in braces is
    corporate and compares as one token.
    """
    raw = re.sub(r"\s+", " ", raw or "").strip()
    if _wrapped(raw):
        return [(_skey(raw), ())]
    parts = [p for p in _split_top(raw, r",") if p]
    if len(parts) >= 2:
        given = parts[2] if len(parts) >= 3 else parts[1]
        return [(_skey(parts[0]), _initials(given))]
    toks = [t for t in detex(raw).split() if t]
    while len(toks) > 1 and _skey(toks[-1]) in _SUFFIX:
        toks = toks[:-1]
    if len(toks) <= 1:
        return [(_skey(raw), ())]
    return [(_skey(" ".join(toks[k:])), _initials(" ".join(toks[:k])))
            for k in range(1, len(toks))]


def _initials_ok(a, b) -> bool:
    """Given names agree up to initial format: an initial meets any name with
    that first letter, two spelled-out names must be identical, and a missing
    trailing middle name is allowed ('John' and 'John D.'). 'Xiao-Qiang' and
    'Xiaoqiang' agree; 'Chong' and 'Chen' do not, nor 'Jeff' and 'Jeffrey'."""
    if a and b and "".join(a) == "".join(b):
        return True
    for x, y in zip(a, b):
        if len(x) == 1 or len(y) == 1:
            if x[0] != y[0]:
                return False
        elif x != y:
            return False
    return True


def _plain(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold(s))


def name_match(a: str, b: str) -> str:
    """'=' identical after folding, '~' same person up to diacritics or
    initial format, '!' different."""
    if _plain(a) == _plain(b):
        return "="
    for sa, ia in name_forms(a):
        for sb, ib in name_forms(b):
            if sa and sa == sb and _initials_ok(ia, ib):
                return "~"
    return "!"


def _flip(raw: str) -> str:
    """'Last, First' to 'First Last' for the exact-equality test."""
    parts = [p for p in _split_top(raw, r",") if p]
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    if len(parts) == 3:
        return f"{parts[2]} {parts[0]} {parts[1]}"
    return raw


def record_names(rec) -> list:
    return [(a.get("name", "") if isinstance(a, dict) else str(a))
            for a in (rec or {}).get("authors") or []]


# -------------------------------------------------------------- comparing
def compare(claim: dict, rec: dict) -> dict:
    """Strict comparison of a claim {title, author, year} against a record.

    Returns ok flags per field, the per-position author table and the
    reasons, which a report prints verbatim.
    """
    reasons = []
    t_ok = bool(title_key(claim.get("title"))) and \
        title_key(claim.get("title")) == title_key(rec.get("title"))
    if not t_ok:
        reasons.append("title differs")

    names, truncated = split_bib_authors(claim.get("author", ""))
    got = record_names(rec)
    rows, bad = [], []
    for i in range(max(len(names), len(got))):
        a = names[i] if i < len(names) else ""
        b = got[i] if i < len(got) else ""
        if a and b:
            mark = "=" if _plain(_flip(a)) == _plain(b) else name_match(a, b)
        else:
            mark = "+"
        rows.append((i + 1, a, b, mark))
        if mark in "!+":
            bad.append(i + 1)
    a_ok = bool(names) and not truncated and not bad and len(names) == len(got)
    if truncated:
        reasons.append(f"entry truncates the author list with 'and others' after "
                       f"{len(names)} names, record has {len(got)}")
    elif len(names) != len(got):
        reasons.append(f"author count {len(names)} vs {len(got)}")
    first_bad = [r for r in rows if r[3] == "!"]
    if first_bad:
        i, a, b, _ = first_bad[0]
        more = f" (+{len(first_bad) - 1} more)" if len(first_bad) > 1 else ""
        reasons.append(f"author {i}: {a!r} vs {b!r}{more}")
    if not names:
        reasons.append("entry has no author list")

    cy = year_of(claim.get("year"))
    ry = {year_of(y) for y in [rec.get("year"), *(rec.get("alt_years") or [])] if year_of(y)}
    y_ok = bool(cy) and cy in ry
    if not y_ok:
        reasons.append(f"year {cy or '?'} vs {'/'.join(sorted(ry)) or '?'}")

    return {"title_ok": t_ok, "authors_ok": a_ok, "year_ok": y_ok,
            "ok": t_ok and a_ok and y_ok, "author_rows": rows,
            "reasons": reasons,
            "fuzzy": difflib.SequenceMatcher(None, title_key(claim.get("title")),
                                             title_key(rec.get("title"))).ratio()}


def rank(c: dict):
    """Order for choosing which candidate to show beside a failed claim."""
    return (c["title_ok"], c["authors_ok"], c["year_ok"], c["fuzzy"])


def same_work(r1: dict, r2: dict) -> bool:
    """Two records describe one work when titles and full author lists agree."""
    if title_key(r1.get("title")) != title_key(r2.get("title")):
        return False
    a, b = record_names(r1), record_names(r2)
    return len(a) == len(b) and all(name_match(x, y) != "!" for x, y in zip(a, b))


# ----------------------------------------------------------- side by side
def side_by_side(claim: dict, rec: dict | None, cmp: dict | None = None,
                 width: int | None = None, left: str = "entry",
                 right: str = "record") -> str:
    """Two-column plain-text diff of claim and record, one author per row.

    Marks: '=' identical, '~' same up to diacritics or initial format,
    '!' differs, '+' present on one side only.
    """
    width = width or max(100, min(shutil.get_terminal_size((160, 20)).columns, 200))
    col = (width - 18) // 2
    rec = rec or {}
    cmp = cmp or (compare(claim, rec) if rec else None)

    def fmt(tag, mark, a, b):
        la = textwrap.wrap(a or "", col) or [""]
        lb = textwrap.wrap(b or "", col) or [""]
        out = []
        for k in range(max(len(la), len(lb))):
            out.append(f"{tag if k == 0 else '':<10} {mark if k == 0 else ' '} | "
                       f"{(la[k] if k < len(la) else ''):<{col}} | "
                       f"{lb[k] if k < len(lb) else ''}")
        return out

    L = [f"{'':<13}| {left:<{col}} | {right}", "-" * width]
    if not rec:
        L += fmt("title", "+", claim.get("title", ""), "(no candidate)")
        return "\n".join(L)
    L += fmt("title", "=" if cmp["title_ok"] else "!", claim.get("title", ""), rec.get("title", ""))
    ry = "/".join(sorted({year_of(y) for y in [rec.get("year"), *(rec.get("alt_years") or [])] if year_of(y)}))
    L += fmt("year", "=" if cmp["year_ok"] else "!", year_of(claim.get("year")), ry)
    for i, a, b, mark in cmp["author_rows"]:
        L += fmt(f"author {i}", mark, a, b)
    names, truncated = split_bib_authors(claim.get("author", ""))
    if truncated:
        L += fmt("", "!", "and others", "")
    ids = rec.get("externalIds") or {}
    L += fmt("venue", " ", claim.get("venue", ""), rec.get("venue") or "")
    L += fmt("ids", " ", claim.get("ids", ""),
             ", ".join(f"{k}:{v}" for k, v in ids.items() if k in ("ArXiv", "DOI") and v))
    return "\n".join(L)


def side_by_side_md(claim: dict, rec: dict | None, cmp: dict | None = None) -> list:
    """The same diff as a markdown table, for the report."""
    esc = lambda s: str(s or "").replace("|", "\\|")
    L = ["| | field | entry | record |", "| --- | --- | --- | --- |"]
    if not rec:
        return L + [f"| + | title | {esc(claim.get('title'))} | (no candidate) |"]
    cmp = cmp or compare(claim, rec)
    L.append(f"| {'=' if cmp['title_ok'] else '!'} | title | {esc(claim.get('title'))} | {esc(rec.get('title'))} |")
    ry = "/".join(sorted({year_of(y) for y in [rec.get("year"), *(rec.get("alt_years") or [])] if year_of(y)}))
    L.append(f"| {'=' if cmp['year_ok'] else '!'} | year | {year_of(claim.get('year'))} | {ry} |")
    for i, a, b, mark in cmp["author_rows"]:
        L.append(f"| {mark} | author {i} | {esc(a)} | {esc(b)} |")
    if split_bib_authors(claim.get("author", ""))[1]:
        L.append("| ! | | and others | |")
    ids = rec.get("externalIds") or {}
    L.append(f"| | venue | {esc(claim.get('venue'))} | {esc(rec.get('venue'))} |")
    L.append(f"| | ids | {esc(claim.get('ids'))} | "
             f"{esc(', '.join(f'{k}:{v}' for k, v in ids.items() if k in ('ArXiv', 'DOI') and v))} |")
    return L
