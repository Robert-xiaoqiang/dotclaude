#!/usr/bin/env python3
r"""Semantic Scholar client that survives the free tier.

The documented limit is one request per second cumulative across all endpoints,
sent as an ``x-api-key`` header. Measured behaviour is worse and erratic: at a
2.5 s gap only one call in five returned 200, because the quota is shared and
this host sits behind a proxy. So this client is retry-driven rather than
schedule-driven.

  * every 429 backs off exponentially with jitter and is retried, because a 429
    means "later", never "no"
  * every resolved query is cached on disk, so a rerun costs nothing and an
    interrupted run resumes where it stopped
  * arXiv, Crossref and DBLP stand behind S2, so a hard S2 outage degrades the
    audit rather than stopping it

urllib is not used: through the local proxy its first call succeeds and every
later one returns 406, so each request is a fresh curl process.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import random
import re
import subprocess
import time
import urllib.parse

UA = "cc2bib/1.0 (mailto:robertxiaoqiang@gmail.com)"
CACHE = pathlib.Path(os.environ.get("CC2BIB_CACHE", pathlib.Path.home() / ".cache" / "cc2bib"))
S2 = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,venue,externalIds,authors.name,publicationTypes,abstract"
MIN_GAP = float(os.environ.get("CC2BIB_MIN_GAP", "1.6"))
_last = [0.0]


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


def fetch(url: str, tag: str = "s2", headers: dict | None = None,
          tries: int = 7, timeout: int = 30):
    """GET with on-disk cache, paced gap and exponential backoff on 429."""
    cf = _cached(tag, url)
    if cf.is_file():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            cf.unlink(missing_ok=True)

    cmd = ["curl", "-sS", "--max-time", str(timeout), "-A", UA, "-w", "\n%{http_code}"]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)

    delay = 2.0
    for attempt in range(tries):
        gap = MIN_GAP - (time.time() - _last[0])
        if gap > 0:
            time.sleep(gap)
        r = subprocess.run(cmd, capture_output=True, text=True)
        _last[0] = time.time()
        body, _, code = r.stdout.rpartition("\n")
        code = code.strip()
        if code == "200" and body.strip():
            try:
                data = json.loads(body)
            except ValueError:
                data = {"__raw__": body}
            cf.write_text(json.dumps(data))
            return data
        if code in ("429", "403", "500", "502", "503", "504") or not code:
            time.sleep(delay + random.uniform(0, delay * 0.4))
            delay = min(delay * 2, 45.0)
            continue
        return None
    return None


# --------------------------------------------------------------- S2 lookups
def s2_match(title: str):
    """Exact-title match. The right endpoint for verifying a known reference."""
    k = _key()
    if not k or not title.strip():
        return None
    url = f"{S2}/paper/search/match?query={urllib.parse.quote(title)}&fields={FIELDS}"
    d = fetch(url, tag="s2match", headers={"x-api-key": k})
    if not d or not d.get("data"):
        return None
    return d["data"][0]


def s2_search(query: str, limit: int = 5):
    """Relevance search, for when only a description of the work is known."""
    k = _key()
    if not k or not query.strip():
        return []
    url = (f"{S2}/paper/search?query={urllib.parse.quote(query)}"
           f"&limit={limit}&fields={FIELDS}")
    d = fetch(url, tag="s2search", headers={"x-api-key": k})
    return (d or {}).get("data") or []


# ------------------------------------------------------------- fallbacks
def arxiv_match(title: str):
    """arXiv exact-phrase title search. ti: must stay literal or arXiv 406s."""
    if not title.strip():
        return None
    q = "ti:%22" + urllib.parse.quote_plus(norm(title)) + "%22"
    d = fetch(f"https://export.arxiv.org/api/query?search_query={q}&max_results=3",
              tag="arxiv")
    raw = (d or {}).get("__raw__", "")
    out = []
    for m in re.finditer(r"<entry>(.*?)</entry>", raw, re.S):
        e = m.group(1)
        t = re.search(r"<title>(.*?)</title>", e, re.S)
        i = re.search(r"<id>https?://arxiv\.org/abs/([^<]+)</id>", e)
        y = re.search(r"<published>(\d{4})", e)
        if t:
            out.append({"title": re.sub(r"\s+", " ", t.group(1)).strip(),
                        "year": int(y.group(1)) if y else None,
                        "venue": "arXiv",
                        "externalIds": {"ArXiv": re.sub(r"v\d+$", "", i.group(1))} if i else {},
                        "authors": [{"name": n} for n in re.findall(r"<name>([^<]+)</name>", e)]})
    return out


def arxiv_by_id(arxiv_id: str):
    """Resolve an arXiv id directly. Authoritative, and the strongest check
    available: an entry that carries an id is claiming a specific record, so
    the claim can be compared against that record rather than guessed at from
    the title."""
    if not arxiv_id:
        return None
    d = fetch(f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1",
              tag="arxivid")
    raw = (d or {}).get("__raw__", "")
    m = re.search(r"<entry>(.*?)</entry>", raw, re.S)
    if not m:
        return None
    e = m.group(1)
    t = re.search(r"<title>(.*?)</title>", e, re.S)
    if not t or "Error" in t.group(1):
        return None
    y = re.search(r"<published>(\d{4})", e)
    return {"title": re.sub(r"\s+", " ", t.group(1)).strip(),
            "year": int(y.group(1)) if y else None, "venue": "arXiv",
            "externalIds": {"ArXiv": arxiv_id},
            "authors": [{"name": n} for n in re.findall(r"<name>([^<]+)</name>", e)]}


def crossref_match(title: str):
    if not title.strip():
        return []
    q = urllib.parse.quote_plus(norm(title))
    d = fetch(f"https://api.crossref.org/works?query.bibliographic={q}&rows=3"
              f"&mailto=robertxiaoqiang@gmail.com", tag="crossref")
    items = ((d or {}).get("message") or {}).get("items") or []
    out = []
    for it in items:
        y = None
        for k in ("published-print", "published-online", "issued"):
            v = it.get(k, {}).get("date-parts", [[None]])[0][0]
            if v:
                y = v
                break
        out.append({"title": (it.get("title") or [""])[0],
                    "year": y, "venue": (it.get("container-title") or [""])[0],
                    "externalIds": {"DOI": it.get("DOI", "")},
                    "authors": [{"name": f"{a.get('given','')} {a.get('family','')}".strip()}
                                for a in it.get("author", [])]})
    return out


# ------------------------------------------------------------------ helpers
def norm(t: str) -> str:
    """Query text for a search endpoint. Comparison lives in match.py."""
    t = re.sub(r"[{}$\\]", "", (t or "").lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()
