#!/usr/bin/env python3
r"""Semantic Scholar, arXiv and Crossref clients that survive their free tiers.

The Semantic Scholar limit is one request per second cumulative across all
endpoints, sent as an ``x-api-key`` header. Measured behaviour is worse and
erratic: at a 2.5 s gap only one call in five returned 200, because the quota
is shared and this host sits behind a proxy. So this client is retry-driven
rather than schedule-driven.

  * every 429 backs off exponentially with jitter and is retried, because a 429
    means "later", never "no"
  * every resolved query is cached on disk, so a rerun costs nothing and an
    interrupted run resumes where it stopped
  * arXiv and Crossref stand behind S2, so a hard S2 outage degrades the
    audit rather than stopping it

urllib is not used: through the local proxy its first call succeeds and every
later one returns 406, so each request is a fresh curl process.

arXiv has its own transport chain (``arxiv_get``). Each API request tries a
direct connection that bypasses every proxy first, then the environment proxy;
an id lookup falls back to the abstract page https://arxiv.org/abs/<id>, whose
``citation_*`` meta tags carry title, authors and posting date. The chain
exists because export.arxiv.org has answered 406 with an empty body on every
request that missed its CDN cache, through the proxy and directly alike, while
the abstract page kept answering. Which transport answered is logged at debug
level. arXiv asks for one request every three seconds, and gets it.

Every record carries ``source`` (S2, arXiv or Crossref), so a verdict can say
which service confirmed it.
"""
from __future__ import annotations

import hashlib
import html
import json
import logging
import os
import pathlib
import random
import re
import subprocess
import time
import urllib.parse

log = logging.getLogger("cc2bib")

UA = "cc2bib/1.0 (mailto:robertxiaoqiang@gmail.com)"
CACHE = pathlib.Path(os.environ.get("CC2BIB_CACHE", pathlib.Path.home() / ".cache" / "cc2bib"))
S2 = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,externalIds,authors.name,publicationTypes,abstract"
MIN_GAP = float(os.environ.get("CC2BIB_MIN_GAP", "1.6"))
ARXIV_GAP = float(os.environ.get("CC2BIB_ARXIV_GAP", "3.0"))
_last = [0.0]
_arxiv_last = [0.0]

# retried with backoff: rate limits and transient server errors; anything
# else (404, 406, ...) is a hard answer from this transport
RETRY = ("429", "403", "500", "502", "503", "504")


def _key() -> str | None:
    k = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if k:
        return k
    secret = pathlib.Path(os.environ.get("CPFS_HOME", "")) / ".secret"
    if secret.is_file():
        m = re.search(r"SEMANTIC_SCHOLAR_API_KEY\s*=\s*[\"']?([^\"'\s]+)", secret.read_text())
        if m:
            return m.group(1)
    return None


def _cached(tag: str, url: str):
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"{tag}-{hashlib.sha1(url.encode()).hexdigest()[:20]}.json"


def _pace(clock: list, gap: float):
    wait = gap - (time.time() - clock[0])
    if wait > 0:
        time.sleep(wait)


def _curl(url: str, extra: list, timeout: int, headers: dict | None = None):
    """One fresh curl process. Returns (http code, body)."""
    cmd = ["curl", "-sS", "-L", "--max-time", str(timeout), "-A", UA, "-w", "\n%{http_code}"]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    cmd += [*extra, url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    return code.strip(), body


def fetch(url: str, tag: str = "s2", headers: dict | None = None,
          tries: int = 7, timeout: int = 30):
    """GET with on-disk cache, paced gap and exponential backoff on 429."""
    cf = _cached(tag, url)
    if cf.is_file():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            cf.unlink(missing_ok=True)

    delay = 2.0
    for attempt in range(tries):
        _pace(_last, MIN_GAP)
        code, body = _curl(url, [], timeout, headers)
        _last[0] = time.time()
        log.debug("%s %s -> %s", tag, url, code or "no answer")
        if code == "200" and body.strip():
            try:
                data = json.loads(body)
            except ValueError:
                data = {"__raw__": body}
            cf.write_text(json.dumps(data))
            return data
        if code in RETRY or not code:
            time.sleep(delay + random.uniform(0, delay * 0.4))
            delay = min(delay * 2, 45.0)
            continue
        return None
    return None


# ------------------------------------------------------------ arXiv transport
# (name, extra curl arguments). The direct connection first: it bypasses
# every proxy variable, so a proxy that mangles or rate-limits the API is
# never the first thing tried. Then the environment proxy as curl sees it.
TRANSPORTS = (("direct", ["--noproxy", "*"]), ("proxy", []))


def arxiv_get(url: str, tag: str, tries: int = 3, timeout: int = 30):
    """arXiv over the transport chain: direct, then proxy. The cache is keyed
    by url alone, so a record fetched over any transport is reused. Returns
    {"__raw__": body, "__transport__": name} or None when every transport
    failed; the caller decides whether a further fallback applies."""
    cf = _cached(tag, url)
    if cf.is_file():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            cf.unlink(missing_ok=True)
    for name, extra in TRANSPORTS:
        delay = 3.0
        for attempt in range(tries):
            _pace(_arxiv_last, ARXIV_GAP)
            code, body = _curl(url, extra, timeout)
            _arxiv_last[0] = time.time()
            log.debug("arxiv %s %s -> %s", name, url, code or "no answer")
            if code == "200" and body.strip():
                data = {"__raw__": body, "__transport__": name}
                cf.write_text(json.dumps(data))
                log.debug("arxiv answered by %s: %s", name, url)
                return data
            if code in RETRY or not code:
                time.sleep(delay + random.uniform(0, delay * 0.4))
                delay = min(delay * 2, 30.0)
                continue
            break                        # 406 or other hard answer: next transport
    log.debug("arxiv: no transport answered %s", url)
    return None


def _atom_entry(e: str, arxiv_id: str | None = None):
    t = re.search(r"<title>(.*?)</title>", e, re.S)
    if not t or "Error" in t.group(1):
        return None
    i = re.search(r"<id>https?://arxiv\.org/abs/([^<]+)</id>", e)
    y = re.search(r"<published>(\d{4})", e)
    aid = arxiv_id or (re.sub(r"v\d+$", "", i.group(1)) if i else None)
    return {"title": html.unescape(re.sub(r"\s+", " ", t.group(1)).strip()),
            "year": int(y.group(1)) if y else None, "venue": "arXiv",
            "externalIds": {"ArXiv": aid} if aid else {},
            "authors": [{"name": html.unescape(n)} for n in re.findall(r"<name>([^<]+)</name>", e)],
            "source": "arXiv"}


def arxiv_abs(arxiv_id: str):
    """The abstract page as a record, from its citation_* meta tags: the
    third transport for an id lookup, used when the API answered nothing.
    citation_author is 'Last, First'; citation_date is the v1 posting date."""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    d = arxiv_get(url, tag="arxivabs")
    raw = (d or {}).get("__raw__", "")
    meta = {}
    for name, content in re.findall(r'<meta\s+name="(citation_[a-z_]+)"\s+content="([^"]*)"', raw):
        meta.setdefault(name, []).append(html.unescape(content))
    if not meta.get("citation_title"):
        return None
    authors = []
    for a in meta.get("citation_author", []):
        last, _, first = a.partition(",")
        authors.append({"name": f"{first.strip()} {last.strip()}".strip() if first else a.strip()})
    y = re.search(r"\d{4}", (meta.get("citation_date") or [""])[0])
    return {"title": re.sub(r"\s+", " ", meta["citation_title"][0]).strip(),
            "year": int(y.group(0)) if y else None, "venue": "arXiv",
            "externalIds": {"ArXiv": arxiv_id}, "authors": authors,
            "source": "arXiv", "transport": "abs"}


# --------------------------------------------------------------- S2 lookups
def _s2(rec):
    if rec:
        rec["source"] = "S2"
    return rec


def s2_match(title: str):
    """Exact-title match. The right endpoint for verifying a known reference."""
    k = _key()
    if not k or not title.strip():
        return None
    url = f"{S2}/paper/search/match?query={urllib.parse.quote(title)}&fields={FIELDS}"
    d = fetch(url, tag="s2match", headers={"x-api-key": k})
    if not d or not d.get("data"):
        return None
    return _s2(d["data"][0])


def s2_search(query: str, limit: int = 5):
    """Relevance search, for when only a description of the work is known."""
    k = _key()
    if not k or not query.strip():
        return []
    url = (f"{S2}/paper/search?query={urllib.parse.quote(query)}"
           f"&limit={limit}&fields={FIELDS}")
    d = fetch(url, tag="s2search", headers={"x-api-key": k})
    return [_s2(r) for r in (d or {}).get("data") or []]


# ------------------------------------------------------------- fallbacks
def arxiv_match(title: str):
    """arXiv exact-phrase title search over the transport chain. The colon in
    ti: must stay literal or arXiv 406s; the title itself is percent-encoded
    with spaces as +. No abstract-page fallback: a title has no page."""
    if not title.strip():
        return None
    q = "ti:%22" + urllib.parse.quote_plus(norm(title)) + "%22"
    d = arxiv_get(f"https://export.arxiv.org/api/query?search_query={q}&max_results=3",
                  tag="arxiv")
    raw = (d or {}).get("__raw__", "")
    out = []
    for m in re.finditer(r"<entry>(.*?)</entry>", raw, re.S):
        rec = _atom_entry(m.group(1))
        if rec:
            rec["transport"] = d.get("__transport__")
            out.append(rec)
    if not out:
        out = arxiv_search_html(title)
    return out


def arxiv_search_html(title: str, size: int = 100):
    """Title search through the arXiv listing page, the fallback when the API
    answers 406 (as it does from some hosts and proxies). Parses the results
    list for id, title, authors and submission date. Only records whose
    normalised title equals the query are returned, so the caller never sees
    a near miss from here."""
    if not title.strip():
        return []
    url = ("https://arxiv.org/search/?query=" + urllib.parse.quote_plus('"' + norm(title) + '"')
           + f"&searchtype=title&abstracts=hide&order=&size={size}")
    cf = _cached("arxivhtml", url)
    if cf.is_file():
        body = cf.read_text()
    else:
        body = ""
        for name, extra in TRANSPORTS:
            code, body = _curl(url, extra, 30)
            if code == "200" and "arxiv-result" in body:
                cf.parent.mkdir(parents=True, exist_ok=True); cf.write_text(body)
                break
            body = ""
    out = []
    want = norm(title).lower()
    for m in re.finditer(r'<li class="arxiv-result">(.*?)</li>', body, re.S):
        b = m.group(1)
        aid = re.search(r'arXiv:(\d{4}\.\d{4,5})', b)
        t = re.search(r'class="title is-5 mathjax">\s*(.*?)\s*</p>', b, re.S)
        if not (aid and t):
            continue
        ttl = html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip()
        ttl = " ".join(ttl.split())
        if norm(ttl).lower() != want:
            continue
        authors = [html.unescape(a.strip()) for a in
                   re.findall(r'<a href="/search/\?searchtype=author[^"]*">([^<]*)</a>', b)]
        year = None
        plain = re.sub(r"<[^>]+>", " ", b)
        d = (re.search(r"originally announced\s*([A-Za-z]+\s+\d{4})", plain)
             or re.search(r"v1\s*submitted\s*([^;]*)", plain)
             or re.search(r"Submitted\s*(?:on\s*)?([^;]*)", plain))
        if d:
            y = re.search(r"(\d{4})", d.group(1))
            year = int(y.group(1)) if y else None
        out.append({"title": ttl, "year": year, "venue": "arXiv",
                    "externalIds": {"ArXiv": aid.group(1)},
                    "authors": [{"name": a} for a in authors],
                    "source": "arXiv", "transport": "search-html"})
    return out


def arxiv_by_id(arxiv_id: str):
    """Resolve an arXiv id directly. Authoritative, and the strongest check
    available: an entry that carries an id is claiming a specific record, so
    the claim can be compared against that record rather than guessed at from
    the title. API over direct then proxy; then the abstract page."""
    if not arxiv_id:
        return None
    d = arxiv_get(f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1",
                  tag="arxivid")
    raw = (d or {}).get("__raw__", "")
    m = re.search(r"<entry>(.*?)</entry>", raw, re.S)
    if m:
        rec = _atom_entry(m.group(1), arxiv_id)
        if rec:
            rec["transport"] = d.get("__transport__")
            return rec
        return None                      # the API answered: the id does not exist
    rec = arxiv_abs(arxiv_id)
    if rec:
        log.debug("arxiv %s answered by the abstract page", arxiv_id)
    return rec


def crossref_match(title: str):
    if not title.strip():
        return []
    q = urllib.parse.quote_plus(norm(title))
    d = fetch(f"https://api.crossref.org/works?query.bibliographic={q}&rows=3"
              f"&mailto=robertxiaoqiang@gmail.com", tag="crossref")
    items = ((d or {}).get("message") or {}).get("items") or []
    out = []
    for it in items:
        # a journal paper carries several dates (online in December, in print
        # in January); every one of them is a year of the record
        years = []
        for k in ("published-print", "published-online", "issued"):
            v = (it.get(k) or {}).get("date-parts", [[None]])[0][0]
            if v and v not in years:
                years.append(v)
        out.append({"title": (it.get("title") or [""])[0],
                    "year": years[0] if years else None,
                    "alt_years": years[1:],
                    "venue": (it.get("container-title") or [""])[0],
                    "externalIds": {"DOI": it.get("DOI", "")},
                    "authors": [{"name": f"{a.get('given','')} {a.get('family','')}".strip()}
                                for a in it.get("author", [])],
                    "source": "Crossref"})
    return out


# ------------------------------------------------------------------ helpers
def norm(t: str) -> str:
    """Query text for a search endpoint. Comparison lives in match.py."""
    t = re.sub(r"[{}$\\]", "", (t or "").lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()
