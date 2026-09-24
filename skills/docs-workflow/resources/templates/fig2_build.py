"""fig:arch v12 (v11 + adversarial critique) -- 20.3 cm canvas, columns aligned across the two rows.
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

CM = 360000; W, H = 20.3, 18.0
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

# ================================================================== geometry
Y1, B1 = 0.3, 7.4           # row 1
XA0, XA1 = 0.6, 5.1         # column A: MemArena / Evaluate
XB0, XB1 = 5.8, 10.1        # column B: Task Agent / Archive
XC0, XC1 = 10.8, 20.0       # column C: MemDGM / Self-modify
F0 = B1 + 1.15              # the Darwin Godel frame (the zoom of MemDGM)
P0 = F0 + 0.75              # row-2 panel tops
def ichip2(x, y, w, h, ic, l1, l2, fill=WHITE, line=INK, lw=0.9, isz=0.46):
    rect(x, y, w, h, fill, line, lw, 0.16); icon(ic, x + 0.14, y + (h - isz) / 2, isz)
    text(x + 0.3 + isz, y + 0.05, w - isz - 0.38, h / 2 - 0.05, l1); text(x + 0.3 + isz, y + h / 2, w - isz - 0.38, h / 2 - 0.05, l2)
def sub_lbl(x, y, base, sub, col=INK, size=12, subsize=9):      # a symbol with a real-size subscript
    bw = width_cm([M(base, size, col)])
    text(x, y, bw + 0.04, 0.5, M(base, size, col), pad=0.0); text(x + bw - 0.02, y + 0.13, 0.4, 0.45, R(sub, subsize, False, col, False, SERIF), pad=0.0)
def elabel(x, y, w, txt, col, align=PP_ALIGN.CENTER): return text(x, y, w, 0.45, R(txt, FS, True, col), align)

# ------------------------------------------------------------------ Self-modify geometry first (it sets the height)
ex, ew = 11.2, 8.45
yt0 = P0 + 0.8                                          # tier.py top
TIER = ['Action = Stop | Narrow | Descend', 'class Tier(Interface):', '    # in-layer',
        '    def admit(p) -> bool', '    def index(items) -> Index', '    def score(q, focus) -> [(x, c)]',
        '    # cross-layer', '    def propose(items, seg) -> [Proposal]', '    def route(q, x, c) -> Action',
        '    # contract: V append-only; supp exact;', '    #   within budget B; deterministic']
ht = 0.5 + len(TIER) * LH + 0.14
ysel = yt0 + ht + 0.25 + 0.33                           # diagnosis -> rewriter row
DIFF = [(' ', 'class SummaryTier_child(SummaryTier_seed):'), (' ', '    def route(q, x, c):'),
        ('-', '        return Stop if c > .3 else Descend'), ('+', '        if c > .55: return Stop'),
        ('+', '        if c > .3 and len(supp(x)) <= 8:'), ('+', '            return Narrow'), ('+', '        return Descend')]
ydf = ysel + 0.33 + 0.55
hd = 0.5 + len(DIFF) * LH + 0.14
PB = ydf + hd + 0.15                                    # row-2 panel bottoms
FB = PB + 0.15
lane = FB + 0.42
H = lane + 0.62
prs.slide_height = Emu(int(H * CM))
yd = P0 + 8.35                                          # accept / reject row, also the new child g'

# ------------------------------------------------------------------ labels (one place, so a terminology change is one edit)
LBL = dict(verbatim='Verbatim', kv='kv-assoc', adapter='adapter', nlport='NL port', latport='Latent port',
           compose='compose', latent='latent layers')
# ------------------------------------------------------------------ the zoom band (behind everything)
BAND = C('F2EFFA')
poly([(XC0, B1), (XC1, B1), (XC1, F0), (XA0, F0)], BAND)
seg(XC0 + 0.26, B1, XA0 + 0.2, F0, C('8C7BB8'), 1.0, MSO_LINE_DASH_STYLE.DASH)

# ------------------------------------------------------------------ one query lane: MemArena -> Task Agent -> MemDGM
yq = 1.41                                   # the query lane
yA, yKV, yC = 2.15, 2.4, 5.1                # answer row, latent-port row, text-port row

# ------------------------------------------------------------------ MemDGM
panel(XC0, Y1, XC1 - XC0, B1 - Y1, P_MEM, 'layers_stack', 'MemDGM')
LX0, LX1, BH = 13.3, 17.45, 0.75
BARS = [('skill', 'Skill', 1.95), ('graph', 'Graph', 3.2), ('summary', 'Summary', 4.45), ('verbatim', LBL['verbatim'], 5.7)]
cy = {nm: y + BH / 2 for _, nm, y in BARS}
ys, yv = 4.45, 5.7
for ic, nm, y in BARS:
    hl = nm == 'Summary'
    rect(LX0, y, LX1 - LX0, BH, C('E4F2E6') if ic == 'verbatim' else WHITE, HILINE if hl else INK, 1.75 if hl else LW, 0.16,
         MSO_LINE_DASH_STYLE.DASH if hl else None)
    icon(ic, LX0 + 0.12, y + 0.12, 0.5); text(LX0 + 0.7, y, 1.9, BH, R(nm, FS, True))
icon('lock', LX0 + 0.72 + width_cm([R(LBL['verbatim'], FS, True)]) + 0.06, yv + 0.2, 0.34)      # the append-only floor
IX = 16.2
for x in (IX + 0.3, IX + 0.75): rect(x, cy['Skill'] - 0.18, 0.36, 0.36, C('FAEAD5'), C('C08A2E'), 0.9, 0.2)
gn = [(IX + 0.12, cy['Graph'] - 0.13), (IX + 0.62, cy['Graph'] + 0.15), (IX + 1.1, cy['Graph'] - 0.13)]
for i, j in [(0, 1), (1, 2), (0, 2)]: seg(*gn[i], *gn[j], C('4A7CB5'), 1.0)
for x, y in gn: oval(x, y, 0.12, C('D6E6F5'), C('4A7CB5'), 1.0)
for k, x in enumerate([IX, IX + 0.43, IX + 0.86]):
    rect(x, cy['Summary'] - 0.17, 0.34, 0.34, HILITE if k == 0 else C('E6E1F1'), HILINE if k == 0 else GREY, 0.9, 0.12)
leaves = [IX + 0.24 * k for k in range(5)]
for k, x in enumerate(leaves): rect(x, cy[LBL['verbatim']] - 0.105, 0.21, 0.21, HILITE if k < 3 else WHITE, HILINE if k < 3 else GREY, 0.8, 0.1)
for k in range(3): seg(IX + 0.07 + 0.1 * k, ys + BH, leaves[k] + 0.105, cy[LBL['verbatim']] - 0.105, GREY, 0.9, MSO_LINE_DASH_STYLE.DASH)
text(13.4, ys + BH + 0.05, 2.55, 0.45, [R('supp', FS), R('(', FS), M('x'), S('⋆', 9), R(')', FS)], PP_ALIGN.RIGHT)
PX, DX = LX1 - 0.35, LX1 - 0.12                     # promote / demote in the gaps, labelled once
for (_, _, ya), (_, _, yb) in zip(BARS[:-1], BARS[1:]):
    seg(PX, yb, PX, ya + BH, PROM, ALW, head=True); seg(DX, ya + BH, DX, yb, DEM, ALW, head=True)
text(LX0, 2.7, PX - LX0 - 0.1, 0.5, [R('promote', FS, True, PROM), R(' / ', FS, False, GREY), R('demote', FS, True, DEM)], PP_ALIGN.RIGHT)
# two queries, two depths: q1 stops at graph, q2 narrows on the summary hit and stops at the floor
Q1X, Q2X, QS = 17.9, 18.65, 0.38
seg(10.95, yq, Q2X, yq, K_CT, ALW)                                        # the lane inside MemDGM
seg(Q1X, yq, Q1X, cy['Graph'] - QS / 2, K_CT, ALW, head=True); icon('stop', Q1X - QS / 2, cy['Graph'] - QS / 2, QS)
seg(Q2X, yq, Q2X, cy['Summary'] - QS / 2, K_CT, ALW); icon('focus_set', Q2X - QS / 2, cy['Summary'] - QS / 2, QS)
seg(Q2X, cy['Summary'] + QS / 2, Q2X, cy[LBL['verbatim']] - QS / 2, K_CT, ALW, head=True); icon('stop', Q2X - QS / 2, cy[LBL['verbatim']] - QS / 2, QS)
sub_lbl(Q1X + 0.06, yq + 0.03, 'q', '1', K_CT); sub_lbl(Q2X + 0.06, yq + 0.03, 'q', '2', K_CT)
text(19.0, 3.9, 1.4, 0.44, R('route', FS, True, K_CT), PP_ALIGN.CENTER, rot=90)
# key for the three actions
ky = 6.62; kx = LX0
seg(kx + 0.12, ky + 0.02, kx + 0.12, ky + 0.34, K_CT, 1.0, head=True); text(kx + 0.26, ky, 1.5, 0.38, R('Descend', FC, True, K_CT, False, MONO))
icon('focus_set', kx + 1.75, ky + 0.02, 0.32); text(kx + 2.1, ky, 1.4, 0.38, R('Narrow', FC, True, K_CT, False, MONO))
icon('stop', kx + 3.45, ky + 0.02, 0.32); text(kx + 3.8, ky, 1.1, 0.38, R('Stop', FC, True, K_CT, False, MONO))
# the two ports: latent layers (kv-assoc, adapter) and compose (the text context through its two channels)
rect(10.95, 1.87, 1.85, 1.05, WHITE, LAT, 1.0, 0.12)
for k, nm in enumerate([LBL['kv'], LBL['adapter']]):
    y = 1.93 + k * 0.48; rect(11.03, y, 1.69, 0.42, C('F1EEF8'), LAT, 0.75, 0.2)
    text(11.03, y, 1.69, 0.42, R(nm, 9.5, True, LAT), PP_ALIGN.CENTER)
seg(11.87, yq, 11.87, 1.87, K_CT, ALW, head=True)                             # q also reaches the latent layers
rect(10.95, 3.2, 1.85, 3.25, WHITE, NLB, 1.0, 0.08)
def chan(y, subtxt):
    rect(11.1, y - 0.26, 1.55, 0.52, C('EAF3FA'), NLB, 0.75, 0.18)
    text(11.28, y - 0.26, 0.36, 0.52, R('C', 12, False, NLB, False, SANS), pad=0.0); text(11.6, y - 0.14, 1.0, 0.45, R(subtxt, 9, False, NLB), pad=0.0)
chan(cy['Graph'], 'txt'); chan(cy[LBL['verbatim']], 'route')
icon('nl_interface', 11.66, yC - 0.62, 0.36); text(10.95, yC - 0.22, 1.85, 0.45, R(LBL['compose'], FS, True, NLB), PP_ALIGN.CENTER)
seg(LX0, cy['Graph'], 12.65, cy['Graph'], NLB, ALW, head=True)
seg(LX0, cy[LBL['verbatim']], 12.65, cy[LBL['verbatim']], NLB, ALW, head=True)

# ------------------------------------------------------------------ MemArena
panel(XA0, Y1, XA1 - XA0, B1 - Y1, P_ARENA, 'benchmark_arena', 'MemArena')
ichip(0.8, yq - 0.32, 4.1, 0.64, 'query', [R('Query ', FS, True), M('q')])
ichip(0.8, yA - 0.3, 3.85, 0.6, 'judge', R('Judge', FS, True))
for k, (ic, nm) in enumerate([('accuracy', 'Accuracy'), ('tokens', 'Tokens'), ('latency', 'Latency')]):
    ichip(0.8, 2.85 + k * 0.66, 3.85, 0.56, ic, R(nm, FS, True), C('F7FAFD'), GREY, 0.75, 0.4)
for k, (b, x, w) in enumerate([('LoCoMo', 0.8, 1.6), ('LongMemEval', 2.48, 2.42), ('InMind', 0.8, 1.6), ('PersonaMem', 2.48, 2.42)]):
    chip(x, 5.0 + (k // 2) * 0.62, w, 0.52, R(b, 9.5), WHITE, GREY, 0.75)

# ------------------------------------------------------------------ Task Agent
panel(XB0, Y1, XB1 - XB0, B1 - Y1, P_AGENT, 'task_agent', 'Task Agent')
chip(7.55, yq - 0.24, 0.9, 0.48, [M('q')], C('EDF1F6'), GREY, 0.75)            # the agent issues the read
seg(4.9, yq, 7.55, yq, K_CT, ALW, head=True); seg(8.45, yq, 10.95, yq, K_CT, ALW, head=True)
text(5.1, yq - 0.5, 0.6, 0.45, M('q', 12, K_CT), PP_ALIGN.CENTER); text(10.1, yq - 0.5, 0.7, 0.45, M('q', 12, K_CT), PP_ALIGN.CENTER)
rect(6.2, 1.85, 1.7, 2.15, WHITE, INK, LW, 0.08); text(6.2, 1.88, 1.7, 0.42, R('Reader', FS, True), PP_ALIGN.CENTER)
bars = [2.35 + k * 0.53 for k in range(3)]
for y in bars:
    rect(6.35, y, 1.4, 0.38, C('F1EEF8'), C('9A8BB8'), 0.75, 0.2); text(6.35, y, 1.4, 0.38, R('attn', 9.5, False, LAT), PP_ALIGN.CENTER)
rect(8.9, yKV - 0.5, 0.8, 1.0, WHITE, LAT, 1.0, 0.12)
for i in range(3):
    for j in range(3): rect(9.0 + j * 0.21, yKV - 0.38 + i * 0.26, 0.18, 0.22, C('D9CCF0'), LAT, 0.5, 0.1)
bx = 8.45
seg(8.9, yKV, bx, yKV, LAT, ALW); seg(bx, yKV, bx, bars[-1] + 0.19, LAT, ALW)
for y in bars: seg(bx, y + 0.19, 7.9, y + 0.19, LAT, ALW, head=True)
rect(6.2, yC - 0.38, 3.5, 0.76, WHITE, GREY, 0.75, 0.12)
rect(6.3, yC - 0.27, 0.5, 0.54, C('5B6472'), C('5B6472'), 0.75, 0.12); text(6.3, yC - 0.27, 0.5, 0.54, M('q', 12, WHITE), PP_ALIGN.CENTER)
for k in range(5): rect(7.0 + k * 0.5, yC - 0.14, 0.28, 0.28, HILITE, HILINE, 0.8, 0.12)
seg(7.05, yC - 0.38, 7.05, 4.0, INK, ALW, head=True)
ichip2(6.0, 5.72, 3.9, 0.76, 'nl_interface', R(LBL['nlport'], FS, True, NLB), R('text → prompt', FS), WHITE, NLB, 0.9, 0.4)
ichip2(6.0, 6.54, 3.9, 0.76, 'latent_purple', R(LBL['latport'], FS, True, LAT), R('KV → attention', FS), WHITE, LAT, 0.9, 0.4)
# answer and the two ports back into the agent
seg(6.2, yA, 4.65, yA, INK, ALW, head=True); text(5.15, yA - 0.5, 0.6, 0.45, M('a'), PP_ALIGN.CENTER)
seg(10.95, yC, 9.7, yC, NLB, ALW, head=True); text(10.1, yC - 0.52, 0.7, 0.45, M('C', 12, NLB), PP_ALIGN.CENTER)
seg(10.95, yKV, 9.7, yKV, LAT, ALW, head=True); text(10.0, yKV - 0.52, 0.9, 0.45, R('KV', FS, True, LAT), PP_ALIGN.CENTER)

# ================================================================== the Darwin Godel frame: Evaluate | Archive | Self-modify
rect(XA0, F0, XC1 - XA0, FB - F0, BAND, C('8C7BB8'), 1.0, 0.02)
icon('evolution', XA0 + 0.2, F0 + 0.1, 0.5); text(XA0 + 0.8, F0 + 0.08, 6.0, 0.55, [R('Darwin Gödel Loop', FT, True, C('5B4A8A'))])
EA0, EA1 = 0.75, XA1                                    # panels inset in the frame
# ------------------------------------------------------------------ Evaluate
panel(EA0, P0, EA1 - EA0, PB - P0, P_EVAL, 'evaluate', 'Evaluate')
yrun = P0 + 1.2; ex0, ex1 = 1.05, 4.9
ichip(ex0, yrun - 0.33, ex1 - ex0, 0.66, 'run', R('run task loop', FS, True))
icon('benchmark_arena', ex1 - 0.72, yrun - 0.15, 0.3); icon('task_agent', ex1 - 0.38, yrun - 0.15, 0.3)
ysc = P0 + 2.25; RH = 0.86
rect(ex0, ysc, ex1 - ex0, 3 * RH + 0.16, WHITE, GREY, 0.8, 0.06)
for k, (ic, nm, val) in enumerate([('accuracy', 'Accuracy', '.577 → .599'), ('tokens', 'Tokens', '4766 → 4683'), ('latency', 'Latency', '7.6 → 4.3 s')]):
    y = ysc + 0.08 + k * RH; icon(ic, ex0 + 0.15, y + 0.2, 0.44)
    text(ex0 + 0.72, y + 0.03, 2.9, 0.42, R(nm, FS, True)); text(ex0 + 0.72, y + 0.43, 2.9, 0.4, R(val, FC, False, INK, False, MONO))
ypt = ysc + 3 * RH + 0.16 + 0.55
ichip2(ex0, ypt, ex1 - ex0, 0.86, 'paired_test', R('paired test', FS, True), R('p = .043', FC, False, INK, False, MONO))
xm = (ex0 + ex1) / 2
seg(xm, yrun + 0.33, xm, ysc, LOOP, ALW, head=True); seg(xm, ysc + 3 * RH + 0.16, xm, ypt, LOOP, ALW, head=True)
xr, xa, fy = ex0 + 0.9, ex1 - 0.9, ypt + 0.86 + 0.5
seg(xm, ypt + 0.86, xm, fy, LOOP, ALW); seg(xr, fy, xa, fy, LOOP, ALW)
seg(xr, fy, xr, yd - 0.3, LOOP, ALW, head=True); seg(xa, fy, xa, yd - 0.3, LOOP, ALW, head=True)
def decide(x, w, ic, word, fill):
    rect(x, yd - 0.3, w, 0.6, fill, INK, 0.9, 0.18); icon(ic, x + 0.1, yd - 0.16, 0.32); text(x + 0.48, yd - 0.3, w - 0.5, 0.6, R(word, FS, True))
decide(ex0, 1.8, 'reject', 'Reject', C('FDECEA')); decide(ex1 - 1.9, 1.9, 'accept', 'Accept', C('E4F2E6'))

# ------------------------------------------------------------------ Archive
panel(XB0, P0, XB1 - XB0, PB - P0, P_ARCH, 'archive_tree', 'Archive')
text(XB0 + 0.85 + width_cm([R('Archive', FT, True)]) + 0.12, P0 + 0.12, 0.6, 0.55, S('\U0001D49C', 15))
r = 0.32; ya0 = P0 + 1.55; bus = P0 + 2.3; yl1, yl2, yl3 = P0 + 3.1, P0 + 4.6, P0 + 6.1
root = (7.7, ya0); gprime = (9.15, yd)
seg(root[0], ya0 + r, root[0], bus, INK, LW); seg(6.5, bus, 7.7, bus, INK, LW); seg(7.7, bus, 9.15, bus, LOOP, LW, MSO_LINE_DASH_STYLE.DASH)
for x in (6.5, 7.7): seg(x, bus, x, yl1 - r, INK, LW)
seg(9.15, bus, 9.15, yd - r, LOOP, LW, MSO_LINE_DASH_STYLE.DASH)
seg(6.5, yl1 + r, 6.5, yl2 - r, INK, LW); seg(7.7, yl1 + r, 7.7, yl2 - r, INK, LW); seg(6.5, yl2 + r, 6.5, yl3 - r, INK, LW)
for (x, y) in [(6.5, yl1), (7.7, yl1), (6.5, yl2), (7.7, yl2), (6.5, yl3)]: oval(x, y, r, C('D5DAE0'))
oval(*root, r, C('E06A4E')); sub_lbl(root[0] - 0.16, ya0 - 0.27, 'g', '0', WHITE)
oval(*gprime, r, C('F2C23E')); text(gprime[0] - r, yd - r, 2 * r, 2 * r, M('g′'), PP_ALIGN.CENTER)
elabel(5.95, ya0 - 0.22, 1.35, 'parent', LOOP, PP_ALIGN.RIGHT)
elabel(7.7, yd - 0.52, 1.1, 'child', LOOP, PP_ALIGN.RIGHT)
ylog = yd + 0.8
ichip(6.2, ylog - 0.3, 2.3, 0.6, 'log', [R('ledger ', FS, True), S('\U0001D4A5', 13)], WHITE, GREY, 0.8, 0.38)

# ------------------------------------------------------------------ Self-modify
panel(XC0, P0, XC1 - 0.15 - XC0, PB - P0, P_SELF, 'code_edit', 'Self-modify')
editor(ex, yt0, ew, ht, 'tier.py', 'fixed')
for k, l in enumerate(TIER): cline(ex + 0.2, yt0 + 0.52 + k * LH, l)
ichip(ex, ysel - 0.33, 3.45, 0.66, 'diagnosis', [R('diagnosis ', FS, True), S('\U0001D49F', 13), R('(', FS), M('g'), R(')', FS)])
ichip(ex + 4.15, ysel - 0.33, 2.75, 0.66, 'rewriter', [R('rewriter ', FS, True), M('ρ')])
seg(ex + 3.45, ysel, ex + 4.15, ysel, LOOP, ALW, head=True)
seg(ex + 5.5, ysel + 0.33, ex + 5.5, ydf, LOOP, ALW, head=True)
editor(ex, ydf, ew, hd, tabs=[('skill', 'skill', False), ('graph', 'graph', False), ('summary', 'summary', True), ('verbatim', 'verbatim', False)])
yy = ydf + 0.52
for sign, l in DIFF:                                     # bands first, then text
    if sign != ' ': rect(ex + 0.02, yy, ew - 0.04, LH, DF_RED if sign == '-' else DF_GRN, None, 0, 0.0, shape=MSO_SHAPE.RECTANGLE)
    yy += LH
yy = ydf + 0.52
for sign, l in DIFF:
    text(ex + 0.08, yy, 0.25, LH, R(sign, FC, True, DF_RS if sign == '-' else DF_GS, False, MONO), pad=0.0)
    text(ex + 0.35, yy, ew - 0.4, LH, code_runs(l), pad=0.0); yy += LH

# ------------------------------------------------------------------ loop arrows
xsel = 9.75
path([(root[0] + r, ya0), (xsel, ya0), (xsel, ysel), (ex, ysel)], col=LOOP, w=ALW); elabel(8.05, ya0 - 0.5, 1.6, 'select', LOOP)
seg(ex1, yd, gprime[0] - r, yd, LOOP, ALW, head=True); elabel(6.0, yd - 0.5, 1.0, 'add', LOOP, PP_ALIGN.LEFT)
path([(xr, yd + 0.3), (xr, ylog), (6.2, ylog)], col=GREY, w=ALW, dash=MSO_LINE_DASH_STYLE.DASH)
ylj = ysel + 0.33 + 0.27                                 # ledger -> rewriter, under the diagnosis row
path([(8.5, ylog), (10.45, ylog), (10.45, ylj), (ex + 4.55, ylj), (ex + 4.55, ysel + 0.33)], col=GREY, w=ALW, dash=MSO_LINE_DASH_STYLE.DASH)
xc0, xc1 = 6.3, 8.65                                     # contract gate on the lane
path([(ex + 4.2, ydf + hd), (ex + 4.2, lane), (xc1, lane)], col=LOOP, w=ALW)
ichip(xc0, lane - 0.31, xc1 - xc0, 0.62, 'contract', R('contract', FS, True), WHITE, LOOP, 1.0, 0.4)
path([(xc0, lane), (0.3, lane), (0.3, yrun), (ex0, yrun)], col=LOOP, w=ALW)
icon('python_code', 11.3, lane + 0.1, 0.4); text(11.75, lane + 0.05, 2.2, 0.5, [R('child ', FS, True, LOOP), M('g′', 12, LOOP)])

for o in sorted(OVER, reverse=True): print('OVERFLOW %.2f cm  %-40s at (%s, %s)' % o)
print('canvas', W, 'x', round(H, 2))
os.makedirs('out', exist_ok=True); prs.save('out/fig2_arch.pptx'); print('written')
