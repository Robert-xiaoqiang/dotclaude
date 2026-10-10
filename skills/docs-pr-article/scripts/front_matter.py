#!/usr/bin/env python3
"""Record the front-matter structure of every article in one corpus source.

Writes a committable markdown record (structure plus short excerpts only, never
full text) of how each article opens: title, 导语, the order of banner / author
bio / opening / screenshot / paper-info block, the first sentence, the shape of
the paper-info block with URLs masked, and the section headings.

    front_matter.py <corpus/source_dir> <out.md> [title]
"""
import pathlib, re, sys


def parse(t):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", t, re.S)
    head = {}
    if m:
        for l in m.group(1).split("\n"):
            if ":" in l:
                k, v = l.split(":", 1)
                head[k.strip()] = v.strip()
    return head, (m.group(2) if m else t)


def record(f):
    head, body = parse(f.read_text(encoding="utf-8", errors="ignore"))
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    bio = next((l for l in lines if l.startswith("**") and ("作者" in l[:20] or "，" in l[:30])), "")
    i_bio = lines.index(bio) if bio in lines else 1
    opening = next((l for l in lines[i_bio + 1:] if not l.startswith(("[图", "-", "##", "AIxiv"))), "")
    first = re.split(r"(?<=[。！？])", opening)[0][:80]
    paper = [re.sub(r"https?://\S+", "<url>", l) for l in lines
             if re.match(r"^-?\s*(论文|代码|项目|主页|arXiv|Github|GitHub)", l)][:5]
    heads = [l[3:] for l in lines if l.startswith("## ")][:8]
    order = []
    for l in lines[:30]:
        tag = ("图" if l.startswith("[图") else "专栏说明" if l.startswith("AIxiv")
               else "作者简介(加粗)" if l == bio and bio.startswith("**")
               else "论文信息" if re.match(r"^-?\s*(论文|代码|项目)", l)
               else "小标题" if l.startswith("## ") else "正文")
        if not order or order[-1] != tag:
            order.append(tag)
        if tag == "小标题":
            break
    pop = head.get("popularity", "none found")
    pop = re.sub(r"https?://\S+", "<url>", pop)[:90]
    return [f"## {head.get('title', f.stem)}", "",
            f"- 导语：{head.get('subtitle') or '无'}",
            f"- 日期：{head.get('date', '')}；热度：{pop}",
            f"- 前置顺序：{' → '.join(order)}",
            (f"- 作者简介开头：{bio.replace('**', '')[:28]}……（{'整段加粗' if bio.startswith('**') else '未加粗'}）"
             if bio else "- 作者简介：无"),
            f"- 开头第一句：{first}",
            "- 论文信息块：" + ("；".join(paper) if paper else "无"),
            "- 小标题：" + ("、".join(heads) if heads else "无"),
            f"- 来源：{head.get('url', '')[:120]}", ""]


def main(argv):
    src, out = pathlib.Path(argv[1]), pathlib.Path(argv[2])
    title = argv[3] if len(argv) > 3 else f"{src.name} 的前置结构"
    lines = [f"# {title}", "",
             f"由 `scripts/front_matter.py {src.name}` 从本地全文生成，只记结构与短摘录，全文不进仓库。", ""]
    for f in sorted(src.glob("*.txt")):
        lines += record(f)
    out.write_text("\n".join(lines))
    print(f"{out}: {len(list(src.glob('*.txt')))} articles")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
