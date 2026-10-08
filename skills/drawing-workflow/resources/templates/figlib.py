"""shared pptx helpers (from fig2_build v12) (v11 + adversarial critique) -- 20.3 cm canvas, columns aligned across the two rows.
Top, the task loop:  MemArena -> Task Agent (NL port into the prompt, latent port into attention) <- MemDGM
(the four-layer ladder over the append-only floor, supp(x*) fanned onto verbatim leaves, promote/demote
between layers, route, compose C with its two channels, the KV store behind the latent port).
Bottom, the Darwin Godel loop, each panel under its counterpart:  Evaluate (under MemArena, same metric
icons) <- Archive (tree, parent/child) -> Self-modify (under MemDGM, a zoom wedge from the Summary layer):
the Tier interface as highlighted code, the rewriter, and the v3 -> v4 override as a code-review diff.
Icons: Icons8 Fluency (icons2/).  Fonts: Arial, Courier New.  One type scale: titles 12.5 pt, body and
edge labels 10 pt, code 9 pt.  Orthogonal arrows only.
Build: python3 src/fig2_build.py && soffice --headless --convert-to pdf --outdir out out/fig2_arch.pptx
"""
import os, pathlib, re
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml.ns import qn
from lxml import etree

CM = 360000; W, H = 13.97, 4.0
C = RGBColor.from_string
INK, GREY, MUTE, WHITE = C('1F2933'), C('5B6472'), C('8A94A6'), C('FFFFFF')
P_ARENA, P_AGENT, P_MEM, P_EVAL, P_ARCH, P_SELF = C('EAF1FA'), C('FFF6E6'), C('EFEBF8'), C('FDEEE7'), C('E6F3EA'), C('F8F5FD')
LOOP, NLB, LAT, PROM, DEM = C('B4472F'), C('2E6E8E'), C('7B5EA7'), C('2E8B57'), C('7C8794')
HILITE, HILINE = C('F6C9B4'), C('B4472F')
WEDGE = C('FBEFEA')
# code colours (GitHub light)
K_KW, K_FN, K_TY, K_CT, K_CM, K_TX = C('CF222E'), C('8250DF'), C('953800'), C('0550AE'), C('6E7781'), C('1F2328')
ED_BG, ED_LN, ED_HD = C('F6F8FA'), C('D0D7DE'), C('EAEEF2')
DF_RED, DF_GRN, DF_RS, DF_GS = C('FFEBE9'), C('DAFBE1'), C('CF222E'), C('1A7F37')
SANS, MONO, SERIF, FREE = 'Arial', 'Courier New', 'Times New Roman', 'FreeSerif'
ICONS = [str(pathlib.Path(__file__).resolve().parent.parent / 'icons'), 'icons2', 'icons']   # the skill's icon set first
LW = 1.0; ALW = 1.25; FS = 10.5; FT = 12.5; FC = 9

from PIL import ImageFont
_FD = '/usr/share/fonts/truetype/liberation/'
_FF = {(SANS, False, False): 'LiberationSans-Regular.ttf', (SANS, True, False): 'LiberationSans-Bold.ttf',
       (SANS, False, True): 'LiberationSans-Italic.ttf', (SANS, True, True): 'LiberationSans-BoldItalic.ttf',
       (MONO, False, False): 'LiberationMono-Regular.ttf', (MONO, True, False): 'LiberationMono-Bold.ttf',
       (MONO, False, True): 'LiberationMono-Italic.ttf', (MONO, True, True): 'LiberationMono-BoldItalic.ttf',
       (SERIF, False, True): 'LiberationSerif-Italic.ttf', (SERIF, False, False): 'LiberationSerif-Regular.ttf',
       (SERIF, True, True): 'LiberationSerif-BoldItalic.ttf', (SERIF, True, False): 'LiberationSerif-Bold.ttf',
       (FREE, False, False): '../freefont/FreeSerif.ttf', (FREE, False, True): '../freefont/FreeSerif.ttf'}
_FC = {}
def width_cm(runs):
    w = 0.0
    for t, size, bold, col, italic, face, sub in runs:
        sz = size * (0.58 if sub else 1.0); key = (_FF[(face, bool(bold), bool(italic))], sz)
        if key not in _FC: _FC[key] = ImageFont.truetype(_FD + key[0], int(round(sz * 20)))
        w += _FC[key].getlength(t) / 20 / 72 * 2.54
    return w
OVER = []
prs = Presentation(); prs.slide_width = Emu(int(W * CM)); prs.slide_height = Emu(int(H * CM))
s = prs.slides.add_slide(prs.slide_layouts[6]); E = lambda v: Emu(int(round(v * CM)))

# ------------------------------------------------------------------ primitives
def _font(r, size, bold=False, col=INK, italic=False, face=SANS, sub=False):
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = col; r.font.name = face
    if sub: r._r.get_or_add_rPr().set('baseline', '-25000')
def R(t, size=FS, bold=False, col=INK, italic=False, face=SANS, sub=False): return (t, size, bold, col, italic, face, sub)
def M(t, size=12, col=INK, sub=False): return R(t, size, False, col, True, SERIF, sub)   # math letter
def S(t, size=13, col=INK): return R(t, size, False, col, False, FREE)                     # script / math glyph (FreeSerif)
def text(x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, pad=0.02, wrap=False, rot=0):
    b = s.shapes.add_textbox(E(x), E(y), E(w), E(h)); tf = b.text_frame; tf.word_wrap = wrap; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = E(pad); tf.margin_top = tf.margin_bottom = E(0.0)
    tf.auto_size = None
    if isinstance(lines, tuple): lines = [[lines]]              # a single run
    elif lines and isinstance(lines[0], tuple): lines = [lines]  # one line of runs
    for k, runs in enumerate(lines):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph(); p.alignment = align
        for rr in runs: r = p.add_run(); r.text = rr[0]; _font(r, *rr[1:])
    if rot: b.rotation = rot
    if not wrap:
        for runs in lines:
            need = width_cm(runs) + 2 * pad
            if need > w + 1e-3: OVER.append((round(need - w, 2), ''.join(r[0] for r in runs)[:40], round(x, 2), round(y, 2)))
    return b
def nostyle(sh):
    st = sh._element.find(qn('p:style'))
    if st is not None: sh._element.remove(st)
    return sh
def rect(x, y, w, h, fill=WHITE, line=INK, lw=LW, rad=0.08, dash=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, nofill=False):
    sh = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if nofill: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(lw)
    if dash: sh.line.dash_style = dash
    sh.shadow.inherit = False; nostyle(sh)
    try: sh.adjustments[0] = rad
    except Exception: pass
    return sh
def oval(cx, cy, r, fill, line=INK, lw=LW):
    sh = s.shapes.add_shape(MSO_SHAPE.OVAL, E(cx - r), E(cy - r), E(2 * r), E(2 * r)); sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line; sh.line.width = Pt(lw); sh.shadow.inherit = False; nostyle(sh); return sh
def icon(name, x, y, size):
    for d in ICONS:
        p = os.path.join(d, name + '.png')
        if os.path.exists(p): return s.shapes.add_picture(p, E(x), E(y), width=E(size), height=E(size))
    raise SystemExit('missing icon ' + name)
def seg(x1, y1, x2, y2, col=INK, w=ALW, dash=None, head=False, tailhead=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2)); nostyle(c); c.line.color.rgb = col; c.line.width = Pt(w)
    if dash: c.line.dash_style = dash
    ln = c.line._get_or_add_ln()
    if head: te = etree.SubElement(ln, qn('a:tailEnd')); te.set('type', 'arrow'); te.set('w', 'med'); te.set('len', 'med')
    if tailhead: he = etree.SubElement(ln, qn('a:headEnd')); he.set('type', 'arrow'); he.set('w', 'med'); he.set('len', 'med')
    return c
def path(pts, **kw):
    for i in range(len(pts) - 1): seg(*pts[i], *pts[i + 1], head=(i == len(pts) - 2), **kw)
def poly(pts, fill, line=None):
    ff = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    ff.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=True); sh = ff.convert_to_shape()
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    sh.shadow.inherit = False; nostyle(sh); return sh
def panel(x, y, w, h, fill, ic, name):
    rect(x, y, w, h, fill, INK, LW, 0.035)
    icon(ic, x + 0.2, y + 0.14, 0.55); text(x + 0.85, y + 0.14, w - 1.0, 0.55, R(name, FT, True))
def ichip(x, y, w, h, ic, runs, fill=WHITE, line=INK, lw=0.9, isz=None, align=PP_ALIGN.LEFT):
    rect(x, y, w, h, fill, line, lw, 0.18)
    isz = isz or min(0.48, h - 0.14); icon(ic, x + 0.12, y + (h - isz) / 2, isz)
    text(x + 0.2 + isz, y, w - isz - 0.28, h, runs, align)
def chip(x, y, w, h, runs, fill=WHITE, line=INK, lw=0.9, align=PP_ALIGN.CENTER, rad=0.18):
    rect(x, y, w, h, fill, line, lw, rad); text(x, y, w, h, runs, align)

# ------------------------------------------------------------------ code highlighting
KW = {'class', 'def', 'return', 'if', 'and', 'else'}
FN = {'admit', 'index', 'score', 'propose', 'route', 'supp', 'len'}
TY = {'Tier', 'Interface', 'SummaryTier_v3', 'SummaryTier_v4', 'bool', 'Index', 'Proposal', 'Action'}
CT = {'Stop', 'Narrow', 'Descend'}
def code_runs(line, size=FC):
    runs = []; body, cm = (line.split('#', 1) + [None])[:2] if '#' in line else (line, None)
    for tok in re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\.?\d[\d.]*|\s+|.", body):
        col, bold = K_TX, False
        if tok in KW: col, bold = K_KW, True
        elif tok in FN: col = K_FN
        elif tok in TY: col = K_TY
        elif tok in CT or re.fullmatch(r"\.?\d[\d.]*", tok): col = K_CT
        runs.append(R(tok, size, bold, col, False, MONO))
    if cm is not None: runs.append(R('#' + cm, size, False, K_CM, True, MONO))
    return runs
def editor(x, y, w, h, fname=None, tag=None, tabs=None):
    rect(x, y, w, h, ED_BG, ED_LN, 1.0, 0.03)
    rect(x, y, w, 0.46, ED_HD, ED_LN, 1.0, 0.1)
    for k, col in enumerate(['FF5F57', 'FEBC2E', '28C840']): oval(x + 0.22 + k * 0.24, y + 0.23, 0.075, C(col), C(col), 0.5)
    tx = x + 0.95
    if fname:
        icon('terminal', tx, y + 0.08, 0.3); text(tx + 0.37, y, 4.5, 0.46, R(fname, FC, True, K_TX, False, MONO))
    for name, ic, active in (tabs or []):
        tw = width_cm([R(name, FC, active, K_TX, False, MONO)]) + 0.62
        if active: rect(tx, y + 0.05, tw, 0.41, WHITE, HILINE, 1.25, 0.12, MSO_LINE_DASH_STYLE.DASH)
        icon(ic, tx + 0.1, y + 0.1, 0.3); text(tx + 0.44, y + 0.05, tw - 0.44, 0.41, R(name, FC, active, K_TX if active else GREY, False, MONO))
        tx += tw + 0.08
    if tag:
        tw = width_cm([R(tag, FC, True, K_TX, False, MONO)]) + 0.3
        chip(x + w - tw - 0.12, y + 0.05, tw, 0.36, R(tag, FC, True, K_TX, False, MONO), C('FFF3C4'), C('D4A72C'), 0.75)
LH = 0.36
def cline(x, y, line, w=8.3): text(x, y, w, LH, code_runs(line), pad=0.0)

