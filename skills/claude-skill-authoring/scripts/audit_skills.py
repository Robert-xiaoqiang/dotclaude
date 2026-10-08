#!/usr/bin/env python3
"""Audit the skill tree for the consistency a rename or a removal breaks silently.

Run after adding, renaming, merging or removing any skill:

    python3 audit_skills.py [SKILLS_DIR] [--gone old-name ...] [--also FILE_OR_DIR ...]

Checks, each one a failure that has happened here:
  name      directory name == frontmatter `name:` == `# Skill:` title
  length    description + when_to_use within the 1536-character listing cap
  refs      every backticked skill-shaped token resolves to a skill, or to a known external one
  paths     every `skills/<x>/...` and `${CLAUDE_SKILL_DIR}/...` path exists
  anchors   every Contents link `(#slug)` matches a heading under GitHub slug rules
  companions  every skill has a Companions section; every family skill links `conventions`
  map       every family skill appears in conventions/SKILL.md
  gone      no file still names a removed or renamed skill (pass --gone, scan --also)
Exit status is the number of failures, so it can gate a commit.
"""
import os, re, sys, unicodedata

argv = sys.argv[1:]
def take(flag):
    out = []
    while flag in argv:
        i = argv.index(flag); argv.pop(i)
        while i < len(argv) and not argv[i].startswith("--"):
            out.append(argv.pop(i))
    return out
GONE = take("--gone")
ALSO = take("--also")
ROOT = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
ROOT = os.path.abspath(ROOT)

SKIP_DIRS = {"synced"}                       # Claude Code's own download, not ours
EXTERNAL = re.compile(r"^(anthropic-skills:[a-z0-9-]+|icons8(:[a-z0-9-]+)?)$")
FAMILY = re.compile(r"^(docs|writing|naming|layout|platform|output|claude|git|code|drawing)-[a-z0-9-]+$")
NON_FAMILY = {"git-commit", "git-push", "claude-migrate", "claude-skill-authoring", "conventions"}

skills = sorted(d for d in os.listdir(ROOT)
                if os.path.isdir(os.path.join(ROOT, d)) and d not in SKIP_DIRS
                and os.path.isfile(os.path.join(ROOT, d, "SKILL.md")))
names = set(skills)
fails = []
def fail(kind, where, msg): fails.append((kind, where, msg))

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if _: fm[k.strip()] = v.strip().strip('"')
    return fm

def slug(h):
    h = h.strip().lower()
    h = "".join(c for c in h if unicodedata.category(c)[0] in "LN" or c in " -_")
    return h.replace(" ", "-")

def strip_code(text):
    # fenced blocks hold shell and examples, not references
    return re.sub(r"```.*?```", "", text, flags=re.S)

for s in skills:
    path = os.path.join(ROOT, s, "SKILL.md")
    text = open(path, encoding="utf-8").read()
    fm = frontmatter(text)
    if fm.get("name") != s: fail("name", s, f"frontmatter name is {fm.get('name')!r}")
    t = re.search(r"^# Skill: *(.+)$", text, re.M)
    if t and t.group(1).strip() != s: fail("name", s, f"title is {t.group(1).strip()!r}")
    n = len(fm.get("description", "")) + len(fm.get("when_to_use", ""))
    if n > 1536: fail("length", s, f"description + when_to_use = {n} > 1536")

    prose = strip_code(text)
    for tok in set(re.findall(r"`([a-z0-9][a-z0-9:-]*)`", prose)):
        if (FAMILY.match(tok) or tok in GONE) and tok not in names and not EXTERNAL.match(tok):
            fail("refs", s, f"`{tok}` is not a skill")
    for m in re.finditer(r"skills/([a-z0-9-]+)(/[^\s`'\")]*)?", text):
        tgt, rest = m.group(1), (m.group(2) or "")
        if tgt in SKIP_DIRS: continue
        p = os.path.join(ROOT, tgt, rest.lstrip("/")) if rest else os.path.join(ROOT, tgt)
        p = re.sub(r"[.,;:]+$", "", p)
        if not os.path.exists(p): fail("paths", s, f"skills/{tgt}{rest} does not exist")
    for m in re.finditer(r"\$\{CLAUDE_SKILL_DIR\}/([^\s`'\")]+)", text):
        p = re.sub(r"[.,;:]+$", "", os.path.join(ROOT, s, m.group(1)))
        if not os.path.exists(p): fail("paths", s, f"${{CLAUDE_SKILL_DIR}}/{m.group(1)} does not exist")

    heads = {slug(h) for h in re.findall(r"^#{2,4} +(.+)$", text, re.M)}
    for a in re.findall(r"\]\(#([^)]+)\)", text):
        if a not in heads: fail("anchors", s, f"#{a} matches no heading")

    comp = re.search(r"^## Companions\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not comp: fail("companions", s, "no Companions section")
    elif s not in NON_FAMILY and "`conventions`" not in comp.group(1):
        fail("companions", s, "family skill does not link `conventions`")

conv = os.path.join(ROOT, "conventions", "SKILL.md")
if os.path.isfile(conv):
    ct = open(conv, encoding="utf-8").read()
    for s in skills:
        if s not in NON_FAMILY and f"`{s}`" not in ct:
            fail("map", "conventions", f"`{s}` is not on the map")

if GONE:
    scan = [os.path.join(ROOT, s) for s in skills] + [os.path.abspath(a) for a in ALSO]
    # A family-shaped name (docs-figure) is distinctive and counts anywhere. Any other name may
    # also be a module, a file format or a tool (pptx, cc2bib), so it counts only where it is
    # plainly a skill: backticked on its own, or as a skills/<name> path.
    strict = [g for g in GONE if FAMILY.match(g)]
    loose = [g for g in GONE if not FAMILY.match(g)]
    parts = []
    if strict: parts.append(r"(?<![A-Za-z0-9_./-])(" + "|".join(map(re.escape, strict)) + r")(?![A-Za-z0-9_-])")
    if loose:
        alt = "|".join(map(re.escape, loose))
        parts.append(r"`(" + alt + r")`")
        parts.append(r"skills/(" + alt + r")\b")
    pat = re.compile("|".join(parts))
    for base in scan:
        files = [base] if os.path.isfile(base) else [
            os.path.join(dp, f) for dp, dn, fs in os.walk(base)
            for f in fs if not any(x in dp.split(os.sep) for x in ("__pycache__", ".git", "synced"))]
        for f in files:
            if f == os.path.abspath(__file__): continue
            try: lines = open(f, encoding="utf-8").read().splitlines()
            except (UnicodeDecodeError, OSError): continue
            for i, line in enumerate(lines, 1):
                for m in pat.finditer(line):
                    hit = next(g for g in m.groups() if g)
                    fail("gone", os.path.relpath(f, os.path.dirname(ROOT)), f"line {i}: `{hit}`")

for kind in ("name", "length", "refs", "paths", "anchors", "companions", "map", "gone"):
    rows = [f for f in fails if f[0] == kind]
    print(f"{kind:<11} {'ok' if not rows else str(len(rows)) + ' FAIL'}")
    for _, where, msg in rows: print(f"    {where}: {msg}")
print(f"\n{len(skills)} skills, {len(fails)} failure(s)")
sys.exit(min(len(fails), 125))
