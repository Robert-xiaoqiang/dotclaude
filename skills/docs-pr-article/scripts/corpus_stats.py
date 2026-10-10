#!/usr/bin/env python3
"""Measure the style of a corpus of Chinese PR articles, and score drafts against it.

Every judgement in docs-pr-article about length, punctuation, hype words or
paragraph size should trace to a number this script printed, not to an
impression of what 量子位 "usually" does. It reads:

  corpus/<source>/*.txt     articles saved with the header block the corpus
                            collectors write (title, subtitle, url, ..., then ---)
  corpus/titles/titles.tsv  optional title corpus: title, subtitle, url, account, date, popularity
  --draft FILE ...          build sources (build_article.py format) to score

and prints a markdown report: per-source medians, the corpus median, and each
draft's value beside it, so a draft that is twice as long per paragraph as
anything published is visible at a glance.

    corpus_stats.py <corpus_dir> [--draft src_v1.txt ...] [--out report.md]
"""
import argparse
import csv
import pathlib
import re
import statistics as st
import sys

HYPE = ["首个", "首次", "重磅", "炸裂", "狂飙", "颠覆", "刷新", "SOTA", "超越", "碾压", "吊打",
        "封神", "暴涨", "突破", "反超", "王炸", "史上", "最强", "全面超越", "一举", "杀疯"]
AIISM = ["深入探讨", "深入剖析", "赋能", "助力", "彰显", "凸显", "无缝", "颠覆性", "前沿",
         "至关重要", "旨在", "一系列", "极大地", "值得注意的是", "众所周知", "可以看出", "开启", "新时代"]
CONNECT = ["因此", "所以", "因为", "然而", "但是", "而且", "此外", "同时", "从而", "进而", "由此", "于是", "因而"]
INSTITUTIONS = ["清华", "北大", "北京大学", "浙大", "复旦", "上交", "交大", "中科院", "港中文", "港大", "港科",
                "南大", "人大", "哈工大", "中科大", "北航", "Mila", "蒙特利尔", "斯坦福", "MIT", "伯克利",
                "CMU", "谷歌", "Google", "DeepMind", "Meta", "OpenAI", "微软", "Microsoft", "英伟达",
                "NVIDIA", "阿里", "腾讯", "字节", "百度", "华为", "蚂蚁", "智源", "上海AI", "剑桥", "牛津",
                "Anthropic", "IBM", "团队"]
CJK = re.compile(r"[一-鿿]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9\-\.]*")
NUMBER = re.compile(r"\d+(?:\.\d+)?%?")


def read_article(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    head, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                head[k.strip()] = v.strip()
        body = m.group(2)
    return head, body


def read_draft(path):
    """Turn a build_article.py source into (head, body) in the corpus shape."""
    head, lines = {}, []
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@title"):
            head["title"] = line[6:].strip()
        elif line.startswith("@subtitle"):
            head["subtitle"] = line[9:].strip()
        elif line.startswith("@intro"):
            head["author_intro"] = "yes"
            lines.append(line[6:].strip())
        elif line.startswith("@image"):
            cap = line.split("|")[1].strip() if "|" in line else ""
            lines.append("[图] " + cap)
        elif line.startswith("@paper"):
            head["paper_info_block"] = "yes"
            lines.append(line[6:].strip())
        elif line == "@end":
            lines.append("— 完 —")
        else:
            lines.append(line)
    return head, "\n".join(lines)


def per_k(n, chars, k=1000):
    return 0.0 if chars == 0 else n * k / chars


def measure(head, body):
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    paras = [l for l in lines if not l.startswith("[图") and not re.match(r"^#{2,3} ", l)
             and not re.match(r"^(论文|代码|项目|arXiv|— 完)", l)]
    heads = [l.lstrip("#").strip() for l in lines if re.match(r"^#{2,3} ", l)]
    figs = [l for l in lines if l.startswith("[图")]
    text = "\n".join(paras)
    chars = len(CJK.findall(text)) + len(LATIN_WORD.findall(text))
    sents = [s for s in re.split(r"[。！？!?]", text) if s.strip()]
    first_fig = next((i for i, l in enumerate(lines) if l.startswith("[图") or l.startswith("## ")), len(lines))
    opening = "".join(l for l in lines[:first_fig] if not l.startswith("本文"))
    title = head.get("title", "")
    return {
        "title_len": len(title),
        "title_excl": "！" in title or "!" in title,
        "title_q": "？" in title or "?" in title,
        "title_num": bool(re.search(r"\d", title)),
        "title_inst": any(i in title for i in INSTITUTIONS),
        "title_hype": any(h in title for h in HYPE),
        "has_subtitle": bool(head.get("subtitle")),
        "author_intro": head.get("author_intro", "").lower().startswith("y"),
        "paper_block": head.get("paper_info_block", "").lower().startswith("y"),
        "chars": chars,
        "paragraphs": len(paras),
        "para_len_med": st.median([len(p) for p in paras]) if paras else 0,
        "para_over_150": sum(len(p) > 150 for p in paras) / len(paras) if paras else 0,
        "sent_len_med": st.median([len(s) for s in sents]) if sents else 0,
        "headings": len(heads),
        "heading_q": sum(("？" in h or "?" in h) for h in heads),
        "figures": len(figs),
        "fig_per_k": per_k(len(figs), chars),
        "bold_per_k": per_k(text.count("**") // 2, chars),
        "num_per_k": per_k(len(NUMBER.findall(text)), chars),
        "latin_per_k": per_k(len(LATIN_WORD.findall(text)), chars),
        "dash_per_k": per_k(text.count("——"), chars),
        "colon_per_k": per_k(text.count("："), chars),
        "excl_per_k": per_k(text.count("！"), chars),
        "semicolon_per_k": per_k(text.count("；"), chars),
        "hype_per_10k": per_k(sum(text.count(h) for h in HYPE), chars, 10000),
        "aiism_per_10k": per_k(sum(text.count(w) for w in AIISM), chars, 10000),
        "connect_per_k": per_k(sum(text.count(c) for c in CONNECT), chars),
        "opening_len": len(opening),
    }


ROWS = [
    ("title_len", "title length (chars)", "{:.0f}"),
    ("title_excl", "titles with ！", "{:.0%}"),
    ("title_q", "titles with ？", "{:.0%}"),
    ("title_num", "titles with a number", "{:.0%}"),
    ("title_inst", "titles naming an institution", "{:.0%}"),
    ("title_hype", "titles with a hype word", "{:.0%}"),
    ("has_subtitle", "has subtitle / 导语", "{:.0%}"),
    ("author_intro", "opens with author bio", "{:.0%}"),
    ("paper_block", "has 论文标题/链接 block", "{:.0%}"),
    ("chars", "body length (chars)", "{:.0f}"),
    ("paragraphs", "paragraphs", "{:.0f}"),
    ("para_len_med", "median paragraph (chars)", "{:.0f}"),
    ("para_over_150", "paragraphs over 150 chars", "{:.0%}"),
    ("sent_len_med", "median sentence (chars)", "{:.0f}"),
    ("headings", "section headings", "{:.0f}"),
    ("heading_q", "question-form headings", "{:.0f}"),
    ("figures", "figures", "{:.0f}"),
    ("fig_per_k", "figures per 1k chars", "{:.2f}"),
    ("bold_per_k", "bold spans per 1k chars", "{:.2f}"),
    ("num_per_k", "numbers per 1k chars", "{:.1f}"),
    ("latin_per_k", "English words per 1k chars", "{:.1f}"),
    ("dash_per_k", "—— per 1k chars", "{:.2f}"),
    ("colon_per_k", "：per 1k chars", "{:.2f}"),
    ("excl_per_k", "！per 1k chars", "{:.2f}"),
    ("semicolon_per_k", "；per 1k chars", "{:.2f}"),
    ("hype_per_10k", "hype words per 10k chars", "{:.1f}"),
    ("aiism_per_10k", "AI-isms per 10k chars", "{:.1f}"),
    ("connect_per_k", "connectives per 1k chars", "{:.2f}"),
    ("opening_len", "opening before 1st figure (chars)", "{:.0f}"),
]


RATE_KEYS = {"title_excl", "title_q", "title_num", "title_inst", "title_hype",
             "has_subtitle", "author_intro", "paper_block"}


def agg(ms, key):
    """Median for measured quantities. Mean for the yes/no rows, which are
    shares of articles: a median of booleans can only be 0% or 100%."""
    vals = [float(m[key]) for m in ms]
    if not vals:
        return float("nan")
    return st.fmean(vals) if key in RATE_KEYS else st.median(vals)


def title_rows(tsv):
    rows = []
    with tsv.open(encoding="utf-8", errors="ignore") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            t = (r.get("title") or "").strip()
            if t:
                rows.append({"title": t, "subtitle": (r.get("subtitle") or "").strip(),
                             "popularity": (r.get("popularity") or "").strip()})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpus")
    ap.add_argument("--draft", nargs="*", default=[])
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.corpus)

    by_source = {}
    for f in sorted(root.glob("*/*.txt")):
        if f.name.endswith(".INCOMPLETE") or f.parent.name == "titles":
            continue
        head, body = read_article(f)
        by_source.setdefault(f.parent.name, []).append(measure(head, body))
    allm = [m for ms in by_source.values() for m in ms]
    drafts = [(pathlib.Path(d).stem, measure(*read_draft(pathlib.Path(d)))) for d in a.draft]

    out = [f"# Style statistics: {len(allm)} articles from {len(by_source)} sources\n",
           "Medians, except the yes/no rows, which are the share of articles (mean). Drafts are scored on the same measures.\n"]
    cols = ["measure", "corpus"] + [f"{s} (n={len(v)})" for s, v in by_source.items()] + [d for d, _ in drafts]
    out.append("| " + " | ".join(cols) + " |")
    out.append("|" + "---|" * len(cols))
    for key, label, fmt in ROWS:
        cells = [label, fmt.format(agg(allm, key)) if allm else "–"]
        cells += [fmt.format(agg(v, key)) for v in by_source.values()]
        cells += [fmt.format(float(m[key])) for _, m in drafts]
        out.append("| " + " | ".join(cells) + " |")

    tsv = root / "titles" / "titles.tsv"
    if tsv.exists():
        trs = title_rows(tsv)
        L = [len(r["title"]) for r in trs]
        pop = [r for r in trs if r["popularity"] and "none" not in r["popularity"].lower()]
        share = lambda pred: sum(1 for r in trs if pred(r["title"])) / len(trs)
        out += ["", f"## Title corpus: {len(trs)} titles, {len(pop)} with a real popularity signal\n",
                f"- length: median {st.median(L):.0f}, quartiles {st.quantiles(L, n=4)[0]:.0f} to {st.quantiles(L, n=4)[2]:.0f}" if len(L) > 3 else "",
                f"- with ！ {share(lambda t: '！' in t or '!' in t):.0%}, with ？ {share(lambda t: '？' in t or '?' in t):.0%}, "
                f"with a number {share(lambda t: re.search(chr(92)+'d', t) is not None):.0%}, "
                f"naming an institution {share(lambda t: any(i in t for i in INSTITUTIONS)):.0%}, "
                f"with a hype word {share(lambda t: any(h in t for h in HYPE)):.0%}",
                f"- 当X遇上Y {share(lambda t: '当' in t and '遇上' in t):.0%}, 进入…时代 {share(lambda t: '进入' in t and '时代' in t):.0%}, "
                f"首个/首次 {share(lambda t: '首个' in t or '首次' in t):.0%}"]
        if pop:
            out += ["", "Titles with a popularity signal:", ""]
            out += [f"- {r['title']}  ({r['popularity']})" for r in pop[:25]]

    report = "\n".join(l for l in out if l is not None) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(report)
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
